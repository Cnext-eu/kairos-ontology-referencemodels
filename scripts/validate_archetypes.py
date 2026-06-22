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

Network policy: local-only. No remote IRI dereference. YAML loaded with
``yaml.safe_load``. The script exits non-zero on any hard failure.

Usage:
    python scripts/validate_archetypes.py
"""

from __future__ import annotations

import io
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
