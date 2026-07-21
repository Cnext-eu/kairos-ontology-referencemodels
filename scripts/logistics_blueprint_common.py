# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Shared, deterministic I/O and local RDF helpers for the Logistics Blueprint."""

from __future__ import annotations

import json
import os
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from rdflib import DCTERMS, OWL, RDF, RDFS, Graph, URIRef


class BlueprintError(RuntimeError):
    """Raised when a blueprint input cannot be loaded or resolved safely."""


def require_file(path: Path, description: str = "input") -> Path:
    """Return a resolved file path or raise a user-facing error."""
    path = Path(path)
    try:
        if not path.is_file():
            raise BlueprintError(f"Missing {description}: {path}")
        return path.resolve()
    except OSError as exc:
        raise BlueprintError(f"Cannot access {description} {path}: {exc}") from exc


def load_yaml(path: Path) -> Any:
    """Safely load YAML and report parse errors with the source path."""
    source = require_file(path, "YAML document")
    try:
        with source.open(encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise BlueprintError(f"Invalid YAML in {source}: {exc}") from exc
    except OSError as exc:
        raise BlueprintError(f"Cannot read YAML document {source}: {exc}") from exc
    if data is None:
        raise BlueprintError(f"YAML document is empty: {source}")
    return data


def load_json(path: Path) -> Any:
    """Load JSON and report parse errors with the source path."""
    source = require_file(path, "JSON document")
    try:
        with source.open(encoding="utf-8") as stream:
            return json.load(stream)
    except json.JSONDecodeError as exc:
        raise BlueprintError(f"Invalid JSON in {source}: {exc}") from exc
    except OSError as exc:
        raise BlueprintError(f"Cannot read JSON document {source}: {exc}") from exc


def dump_yaml(data: Any, path: Path) -> None:
    """Atomically write stable, human-readable YAML with sorted mapping keys."""
    destination = Path(path)
    text = yaml.safe_dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=True,
        width=100,
    )
    temporary: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        temporary = None
    except OSError as exc:
        raise BlueprintError(f"Cannot write YAML document {destination}: {exc}") from exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


class LocalCatalog:
    """Resolve OASIS XML Catalog URI and rewriteURI entries to local files only."""

    _NAMESPACE = "{urn:oasis:names:tc:entity:xmlns:xml:catalog}"

    def __init__(self, catalog_path: Path):
        self.path = require_file(catalog_path, "XML catalog")
        self.root = self.path.parent.resolve()
        self._uris: dict[str, Path] = {}
        self._rewrites: list[tuple[str, Path]] = []
        try:
            catalog = ET.parse(self.path).getroot()
        except ET.ParseError as exc:
            raise BlueprintError(f"Invalid XML catalog {self.path}: {exc}") from exc
        except OSError as exc:
            raise BlueprintError(f"Cannot read XML catalog {self.path}: {exc}") from exc

        for element in catalog.findall(f".//{self._NAMESPACE}uri"):
            name, target = element.get("name"), element.get("uri")
            if name and target:
                key = self._normalise(name)
                resolved_target = self._local_target(target)
                if key in self._uris and self._uris[key] != resolved_target:
                    raise BlueprintError(f"Conflicting catalog mappings for ontology URI: {name}")
                self._uris[key] = resolved_target
        for element in catalog.findall(f".//{self._NAMESPACE}rewriteURI"):
            start, prefix = element.get("uriStartString"), element.get("rewritePrefix")
            if start and prefix:
                self._rewrites.append((start, self._local_target(prefix)))
        self._rewrites.sort(key=lambda item: (-len(item[0]), item[0]))

    @staticmethod
    def _normalise(uri: str) -> str:
        return uri.rstrip("/#")

    def _local_target(self, value: str) -> Path:
        if "://" in value and not value.startswith("file:"):
            raise BlueprintError(f"Catalog target must be local, not {value!r}")
        raw = Path(value.removeprefix("file:"))
        try:
            target = raw.resolve() if raw.is_absolute() else (self.root / raw).resolve()
        except OSError as exc:
            raise BlueprintError(f"Cannot resolve catalog target {value}: {exc}") from exc
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise BlueprintError(f"Catalog target escapes catalog directory: {value}") from exc
        return target

    def resolve(self, uri: str) -> Path:
        """Resolve an ontology URI without attempting network access."""
        normalised = self._normalise(uri)
        if normalised in self._uris:
            target = self._uris[normalised]
        else:
            target = None
            for start, prefix in self._rewrites:
                if uri.startswith(start):
                    target = prefix / uri[len(start):]
                    break
        if target is None:
            raise BlueprintError(f"No local catalog mapping for ontology import: {uri}")
        try:
            target = target.resolve()
        except OSError as exc:
            raise BlueprintError(f"Cannot resolve catalog mapping for {uri}: {exc}") from exc
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise BlueprintError(f"Catalog rewrite escapes catalog directory: {uri}") from exc

        candidates = (target, target.with_suffix(".ttl"), target.with_suffix(".rdf"))
        try:
            for candidate in candidates:
                if candidate.is_file():
                    return candidate.resolve()
        except OSError as exc:
            raise BlueprintError(f"Cannot access catalog mapping for {uri}: {exc}") from exc
        raise BlueprintError(f"Catalog mapping for {uri} points to missing file: {target}")


@dataclass(frozen=True)
class RdfDocument:
    """One locally parsed ontology document and its declared ontology URI."""

    path: Path
    ontology_uri: str
    graph: Graph


def parse_rdf_document(path: Path) -> RdfDocument:
    """Parse one local RDF document and identify its ontology declaration."""
    source = require_file(path, "ontology document")
    graph = Graph()
    try:
        graph.parse(source)
    except Exception as exc:
        raise BlueprintError(f"Cannot parse ontology {source}: {exc}") from exc
    ontology_nodes = set(graph.subjects(RDF.type, OWL.Ontology))
    if len(ontology_nodes) != 1:
        raise BlueprintError(
            f"Ontology document must declare exactly one owl:Ontology, found "
            f"{len(ontology_nodes)}: {source}"
        )
    ontology_node = next(iter(ontology_nodes))
    if not isinstance(ontology_node, URIRef):
        raise BlueprintError(f"Ontology declaration must use a URI: {source}")
    return RdfDocument(source, str(ontology_node), graph)


def load_import_closure(entry_path: Path, catalog_path: Path) -> list[RdfDocument]:
    """Parse an ontology and its complete owl:imports closure through a local catalog."""
    catalog = LocalCatalog(catalog_path)
    pending: list[tuple[Path, str | None]] = [
        (require_file(entry_path, "entry ontology"), None)
    ]
    loaded: dict[Path, RdfDocument] = {}

    while pending:
        source, expected_uri = pending.pop(0)
        try:
            source = source.resolve()
        except OSError as exc:
            raise BlueprintError(f"Cannot resolve ontology document {source}: {exc}") from exc
        if source in loaded:
            if expected_uri is not None and catalog._normalise(
                loaded[source].ontology_uri
            ) != catalog._normalise(expected_uri):
                raise BlueprintError(
                    f"Catalog import URI {expected_uri} resolves to {source}, which declares "
                    f"{loaded[source].ontology_uri}"
                )
            continue
        document = parse_rdf_document(source)
        if expected_uri is not None and catalog._normalise(
            document.ontology_uri
        ) != catalog._normalise(expected_uri):
            raise BlueprintError(
                f"Catalog import URI {expected_uri} resolves to {source}, which declares "
                f"{document.ontology_uri}"
            )
        loaded[source] = document
        imports = sorted(str(node) for node in document.graph.objects(None, OWL.imports))
        for import_uri in imports:
            imported = catalog.resolve(import_uri)
            if imported not in loaded:
                pending.append((imported, import_uri))
            elif imported in loaded and catalog._normalise(
                loaded[imported].ontology_uri
            ) != catalog._normalise(import_uri):
                raise BlueprintError(
                    f"Catalog import URI {import_uri} resolves to {imported}, which declares "
                    f"{loaded[imported].ontology_uri}"
                )

    return sorted(loaded.values(), key=lambda item: (item.ontology_uri, str(item.path)))


def _literal_values(graph: Graph, subject: URIRef, predicate: URIRef) -> list[str]:
    return sorted(
        {
            str(value).replace("\r\n", "\n").replace("\r", "\n")
            for value in graph.objects(subject, predicate)
        }
    )


def _uri_values(graph: Graph, subject: URIRef, predicate: URIRef) -> list[str]:
    return sorted(
        {
            str(value)
            for value in graph.objects(subject, predicate)
            if isinstance(value, URIRef)
        }
    )


def rdf_inventory(
    entry_path: Path,
    catalog_path: Path,
) -> dict[str, Any]:
    """Build a deterministic class/property inventory from a local import closure."""
    documents = load_import_closure(entry_path, catalog_path)
    entry = parse_rdf_document(entry_path)
    versions = _literal_values(entry.graph, URIRef(entry.ontology_uri), OWL.versionInfo)
    records: list[dict[str, Any]] = []
    catalog_root = Path(catalog_path).resolve().parent

    for document in documents:
        module = URIRef(document.ontology_uri)
        inherited_sources = _literal_values(document.graph, module, DCTERMS.source)
        inherited_citations = _literal_values(
            document.graph, module, DCTERMS.bibliographicCitation
        )
        kinds = (
            ("class", OWL.Class),
            ("datatype_property", OWL.DatatypeProperty),
            ("object_property", OWL.ObjectProperty),
        )
        for kind, rdf_type in kinds:
            subjects = sorted(
                {
                    node
                    for node in document.graph.subjects(RDF.type, rdf_type)
                    if isinstance(node, URIRef)
                },
                key=str,
            )
            for subject in subjects:
                record: dict[str, Any] = {
                    "comments": _literal_values(document.graph, subject, RDFS.comment),
                    "domains": _uri_values(document.graph, subject, RDFS.domain),
                    "kind": kind,
                    "labels": _literal_values(document.graph, subject, RDFS.label),
                    "module_uri": document.ontology_uri,
                    "ranges": _uri_values(document.graph, subject, RDFS.range),
                    "source_file": document.path.relative_to(catalog_root).as_posix(),
                    "superclasses": _uri_values(document.graph, subject, RDFS.subClassOf),
                    "uri": str(subject),
                }
                sources = _literal_values(document.graph, subject, DCTERMS.source)
                citations = _literal_values(
                    document.graph, subject, DCTERMS.bibliographicCitation
                )
                if sources or inherited_sources:
                    record["sources"] = sources or inherited_sources
                if citations or inherited_citations:
                    record["citations"] = citations or inherited_citations
                records.append(record)

    records.sort(key=lambda item: (item["uri"], item["kind"], item["module_uri"]))
    return {
        "accelerator_uri": entry.ontology_uri,
        "accelerator_version": versions[0] if versions else "unversioned",
        "format_version": "1.0",
        "modules": [
            {
                "ontology_uri": document.ontology_uri,
                "source_file": document.path.relative_to(catalog_root).as_posix(),
            }
            for document in documents
        ],
        "records": records,
    }
