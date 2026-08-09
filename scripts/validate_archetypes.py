# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
#!/usr/bin/env python3
"""Validate archetype catalog files under blueprints/archetypes/.

Two checks:

  1. JSON Schema validation of every ``*.yaml`` under ``blueprints/archetypes/``
     (excluding ``_schema/`` and dotfiles) against
     ``_schema/archetype.schema.json``.

  2. Best-effort URI resolution against the local ``catalog-v001.xml`` using
     ``scripts/catalog_utils.CatalogResolver`` and rdflib:

       a. Every ``ref_model_modules[].iri`` MUST resolve to an ontology file via
          the catalog and that file MUST declare the IRI as an ``owl:Ontology``.
       b. Every ``core_concepts[].uri`` MUST be declared as an ``owl:Class`` in
          the graph reachable from its module (the prefix of the URI must match
          one of the catalogued module IRIs).

Also runs three advisory-only checks that never fail the build:

  3. Discovery-doc pairing: warn if an archetype has no matching
     ``accelerator-packs/*/discovery/<id>.md`` (filename-stem convention).

  4. Anchor-generality: for every accelerator pack that ships a canonical class
     registry, warn when a concept's ``authority`` text admits a scope qualifier
     (e.g. "for container scope") that has no counterpart in the pack's own
     ``manifest.yaml`` ``target_sectors``. This is a lexical proxy for the
     anchor-selection invariant in ``blueprints/README.md`` — it cannot reason
     about cross-standard class generality (the derived ontologies do not
     declare ``rdfs:subClassOf`` edges across standards), so it only catches a
     concept admitting, in its own words, a narrower scope than the pack claims.

  5. Orphaned discovery docs: warn about any ``accelerator-packs/*/discovery/<id>.md``
     whose ``<id>`` does not match a known archetype id — the symmetric complement
     of check 3.

Network policy: local-only. No remote IRI dereference. YAML loaded with
``yaml.safe_load``. The script exits non-zero on any hard failure; checks 3-5
only ever emit warnings.

Usage:
    python scripts/validate_archetypes.py
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path
from typing import Iterable

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
ONTOLOGY_ROOT = REPO_ROOT / "ontology-reference-models"
ARCHETYPES_DIR = ONTOLOGY_ROOT / "blueprints" / "archetypes"
SCHEMA_PATH = ARCHETYPES_DIR / "_schema" / "archetype.schema.json"
CATALOG_PATH = ONTOLOGY_ROOT / "catalog-v001.xml"
ACCELERATOR_PACKS_DIR = ONTOLOGY_ROOT / "accelerator-packs"

# Allow importing sibling modules.
sys.path.insert(0, str(SCRIPT_DIR))


def _die(msg: str) -> None:
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def _find_archetype_files() -> list[Path]:
    if not ARCHETYPES_DIR.is_dir():
        _die(f"Archetypes directory not found: {ARCHETYPES_DIR}")
    return sorted(
        f for f in ARCHETYPES_DIR.glob("*.yaml")
        if not f.name.startswith(".")
    )


def _load_yaml(path: Path):
    import yaml

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        _die(f"{path.relative_to(REPO_ROOT)}: invalid YAML — {e}")


def _validate_schema(data: dict, schema: dict, rel: Path, errors: list[str]) -> None:
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{rel}: schema violation at {loc} — {err.message}")


def _module_of(uri: str) -> str:
    """Return the module IRI part of a class URI (everything before '#')."""
    return uri.split("#", 1)[0] if "#" in uri else uri.rstrip("/")


def _collect_class_iris(graph) -> set[str]:
    from rdflib import OWL, RDF

    return {str(s) for s in graph.subjects(RDF.type, OWL.Class)}


def _collect_ontology_iris(graph) -> set[str]:
    from rdflib import OWL, RDF

    return {str(s) for s in graph.subjects(RDF.type, OWL.Ontology)}


def _validate_uris(
    data: dict, rel: Path, errors: list[str], warnings: list[str]
) -> None:
    """Resolve module IRIs via catalog, parse graphs, check class declarations."""
    from catalog_utils import CatalogResolver  # type: ignore[import-not-found]
    from rdflib import Graph

    if not CATALOG_PATH.exists():
        warnings.append(
            f"{rel}: catalog-v001.xml not found at {CATALOG_PATH} — skipping URI resolution"
        )
        return

    resolver = CatalogResolver(CATALOG_PATH)

    module_graphs: dict[str, "Graph"] = {}
    for entry in data.get("ref_model_modules", []):
        iri = entry["iri"]
        local_path = resolver.resolve(iri)
        if local_path is None or not Path(local_path).exists():
            errors.append(
                f"{rel}: ref_model_modules iri '{iri}' has no catalog mapping (or file missing)"
            )
            continue
        try:
            g = Graph()
            g.parse(local_path, format="turtle")
        except Exception as exc:  # broad: propagate any parser error as a clear message
            errors.append(f"{rel}: failed to parse {local_path} for '{iri}' — {exc}")
            continue
        declared = _collect_ontology_iris(g)
        if iri not in declared:
            errors.append(
                f"{rel}: ref_model_modules iri '{iri}' is not declared as owl:Ontology "
                f"in {Path(local_path).relative_to(REPO_ROOT)}"
            )
            continue
        module_graphs[iri] = g

    if not module_graphs:
        return

    for entry in data.get("core_concepts", []):
        uri = entry["uri"]
        mod_iri = _module_of(uri)
        graph = module_graphs.get(mod_iri)
        if graph is None:
            errors.append(
                f"{rel}: core_concepts uri '{uri}' references module '{mod_iri}' "
                f"which is not listed in ref_model_modules (or that module failed to load)"
            )
            continue
        classes = _collect_class_iris(graph)
        if uri not in classes:
            errors.append(
                f"{rel}: core_concepts uri '{uri}' is not declared as owl:Class in module '{mod_iri}'"
            )


def _check_discovery_doc(archetype_id: str, rel: Path, warnings: list[str]) -> None:
    """Soft check: warn if no accelerator-pack ships a discovery/<id>.md for this archetype.

    The pairing is convention-based (filename stem) and intentionally non-fatal:
    archetypes without a discovery doc are still valid — consumers fall back to
    a generic concept-confirmation flow.
    """
    if not ACCELERATOR_PACKS_DIR.is_dir():
        return
    matches = sorted(ACCELERATOR_PACKS_DIR.glob(f"*/discovery/{archetype_id}.md"))
    if not matches:
        warnings.append(
            f"{rel}: no matching discovery script found at "
            f"accelerator-packs/*/discovery/{archetype_id}.md "
            f"(consumers will fall back to a generic concept-confirmation flow)"
        )


_SCOPE_QUALIFIER_RE = re.compile(r"for ([\w\s]+?) scope", re.IGNORECASE)


def _check_anchor_generality(warnings: list[str]) -> None:
    """Advisory-only: warn when a concept's authority admits a scope qualifier
    unsupported by the pack's own declared target_sectors.

    See the module docstring, check 3. Loops every accelerator pack; packs with
    no canonical class registry (e.g. financial-services today) are skipped.
    """
    if not ACCELERATOR_PACKS_DIR.is_dir():
        return
    for pack_dir in sorted(ACCELERATOR_PACKS_DIR.iterdir()):
        if not pack_dir.is_dir():
            continue
        manifest_path = pack_dir / "manifest.yaml"
        registry_path = pack_dir / "current" / "blueprint" / "canonical-class-registry.yaml"
        if not manifest_path.exists() or not registry_path.exists():
            continue
        manifest = _load_yaml(manifest_path) or {}
        registry = _load_yaml(registry_path) or {}
        target_sectors = " ".join(
            manifest.get("package", {}).get("target_sectors", []) or []
        ).lower()
        registry_rel = registry_path.relative_to(REPO_ROOT)
        for concept in registry.get("concepts", []) or []:
            match = _SCOPE_QUALIFIER_RE.search(concept.get("authority", "") or "")
            if not match:
                continue
            scope = match.group(1).strip().lower()
            if scope not in target_sectors:
                warnings.append(
                    f"{registry_rel}:{concept.get('id', '?')}: authority declares a "
                    f"'{scope} scope' restriction with no counterpart in "
                    f"{pack_dir.name}/manifest.yaml target_sectors — confirm the anchor "
                    "is the most general class covering every declared target sector "
                    "(blueprints/README.md anchor-selection invariant)"
                )


def _check_orphaned_discovery_docs(known_archetype_ids: set[str], warnings: list[str]) -> None:
    """Advisory-only: warn about a discovery/<id>.md with no matching archetype id.

    Symmetric complement to _check_discovery_doc (check 3 in the module docstring).
    This is the check CHANGELOG.md [1.12.1] described as "structural regression
    coverage to prevent cross-sector discovery guides from being misplaced" — that
    coverage did not exist until this function; see CHANGELOG.md [Unreleased].
    """
    if not ACCELERATOR_PACKS_DIR.is_dir():
        return
    for doc_path in sorted(ACCELERATOR_PACKS_DIR.glob("*/discovery/*.md")):
        if doc_path.stem == "README":
            continue
        if doc_path.stem not in known_archetype_ids:
            rel = doc_path.relative_to(REPO_ROOT)
            warnings.append(
                f"{rel}: no archetype '{doc_path.stem}' found under blueprints/archetypes/ "
                "— this discovery doc is orphaned (misplaced, or its archetype was renamed "
                "or removed)"
            )


def main() -> int:
    try:
        import jsonschema  # noqa: F401
        import yaml  # noqa: F401
        from rdflib import Graph  # noqa: F401
    except ImportError as e:
        _die(
            f"Missing dependency: {e.name}. Install with: "
            "pip install jsonschema pyyaml rdflib"
        )

    if not SCHEMA_PATH.exists():
        _die(f"Schema not found: {SCHEMA_PATH}")

    import json

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    files = _find_archetype_files()
    if not files:
        print("⚠ No archetype YAML files found under blueprints/archetypes/")
        return 0

    errors: list[str] = []
    warnings: list[str] = []

    for yaml_file in files:
        rel = yaml_file.relative_to(REPO_ROOT)
        data = _load_yaml(yaml_file)
        if not isinstance(data, dict):
            errors.append(f"{rel}: top-level YAML must be a mapping")
            continue
        _validate_schema(data, schema, rel, errors)
        # Only attempt URI resolution if schema didn't reject the structure.
        if not any(str(rel) in e for e in errors):
            _validate_uris(data, rel, errors, warnings)
        # Soft pairing check: archetype id ↔ accelerator-pack discovery doc.
        archetype_id = data.get("id") if isinstance(data, dict) else None
        if archetype_id:
            _check_discovery_doc(archetype_id, rel, warnings)
        print(f"  • {rel}")

    # Pack-level advisory checks: not tied to any single archetype file.
    _check_anchor_generality(warnings)
    _check_orphaned_discovery_docs({f.stem for f in files}, warnings)

    print()
    for w in warnings:
        print(f"  ⚠ {w}")
    for e in errors:
        print(f"  ✗ {e}")

    print()
    if errors:
        print(f"✗ {len(errors)} archetype validation failure(s) across {len(files)} file(s).")
        return 1

    suffix = f" ({len(warnings)} warning(s))" if warnings else ""
    print(f"✓ All {len(files)} archetype file(s) valid.{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
