# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""The reader for ``contract-manifest.yaml``.

A manifest describing the published contract, with nothing checking it, would be precisely the
failure this repository keeps having: an official-looking file that no process consumes and that
therefore drifts. ``BLUEPRINT.md`` sat beside ``data-domains.yaml`` looking equally normative
and fell four bridge properties behind without anyone noticing.

So the manifest is executable. These tests assert that:

* every declared path glob actually matches files (a surface that has moved is caught);
* every declared JSON Schema exists and validates **every** matching file;
* every ``enforced_by`` entry names a real script or a real test that still exists;
* a ``schema: null`` row is a deliberate choice with an execution-based check behind it,
  not an oversight.

Deliberately *not* asserted: that the consumer list is complete. That direction is the toolkit's
to prove, and its mirror at ``tests/test_refmodels_contract.py`` is where it belongs — a
consumer can add a reader without telling us, and only its own test suite can see that.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_ROOT = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models"
MANIFEST_PATH = ONTOLOGY_ROOT / "contract-manifest.yaml"

#: ``enforced_by`` entries are "<path>" or "<path>::<test_name>".
_ENFORCER_RE = re.compile(r"^(?P<path>[^:\s]+)(?:::(?P<test>\w+))?")


def _manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


def _surfaces() -> list[dict]:
    return _manifest()["surfaces"]


SURFACE_IDS = [s["id"] for s in _surfaces()]


@pytest.fixture(params=_surfaces(), ids=SURFACE_IDS)
def surface(request) -> dict:
    return request.param


def _matching_files(surface: dict) -> list[Path]:
    """Files a surface's ``path`` matches. A plain directory contributes its whole tree."""
    patterns = surface["path"] if isinstance(surface["path"], list) else [surface["path"]]
    found: list[Path] = []
    for pattern in patterns:
        if pattern.endswith("/"):
            found.extend(p for p in (ONTOLOGY_ROOT / pattern).rglob("*") if p.is_file())
        elif any(ch in pattern for ch in "*?["):
            found.extend(ONTOLOGY_ROOT.glob(pattern))
        else:
            candidate = ONTOLOGY_ROOT / pattern
            if candidate.is_file():
                found.append(candidate)
    return sorted(found)


def test_manifest_is_wellformed() -> None:
    """Structural sanity: unique ids, and the fields every row must carry."""
    manifest = _manifest()
    assert manifest.get("contract_version_policy"), "manifest must state its versioning policy"
    ids = [s["id"] for s in manifest["surfaces"]]
    assert len(ids) == len(set(ids)), f"duplicate surface ids: {ids}"
    for entry in manifest["surfaces"]:
        for key in ("id", "path", "schema", "consumers", "enforced_by"):
            assert key in entry, f"surface {entry.get('id')!r} is missing {key!r}"
        assert entry["consumers"], f"surface {entry['id']!r} declares no consumer"
        assert entry["enforced_by"], f"surface {entry['id']!r} declares no enforcement"


def test_surface_path_matches_files(surface) -> None:
    """A declared surface that matches nothing has moved or been deleted."""
    assert _matching_files(surface), (
        f"surface {surface['id']!r} path {surface['path']!r} matches no files — the contract "
        "surface moved without the manifest following it"
    )


def test_declared_schema_validates_every_matching_file(surface) -> None:
    """Where a schema is declared, it is binding on every file the glob matches."""
    if surface["schema"] is None:
        pytest.skip(f"{surface['id']}: intentionally schema-less, enforced by execution")
    import jsonschema

    schema_path = ONTOLOGY_ROOT / surface["schema"]
    assert schema_path.is_file(), f"{surface['id']}: schema {surface['schema']} not found"
    validator = jsonschema.Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))

    failures: list[str] = []
    for path in _matching_files(surface):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
            location = "/".join(str(p) for p in error.absolute_path) or "<root>"
            failures.append(f"{path.relative_to(REPO_ROOT)}: at {location} — {error.message}")
    assert not failures, "schema violations in declared contract files:\n  " + "\n  ".join(failures)


def test_enforcement_targets_exist(surface) -> None:
    """``enforced_by`` must name a script or test that is really there.

    Enforcement that quietly stops existing is worse than none, because the manifest goes on
    claiming the surface is guarded.
    """
    missing: list[str] = []
    for entry in surface["enforced_by"]:
        match = _ENFORCER_RE.match(entry)
        assert match, f"{surface['id']}: unparseable enforced_by entry {entry!r}"
        path = REPO_ROOT / match.group("path")
        if not path.is_file():
            missing.append(f"{entry} (no such file)")
            continue
        test_name = match.group("test")
        if test_name and f"def {test_name}(" not in path.read_text(encoding="utf-8"):
            missing.append(f"{entry} (file exists, test does not)")
    assert not missing, f"{surface['id']}: enforcement no longer exists: {missing}"


def test_schemaless_surfaces_are_enforced_by_execution(surface) -> None:
    """A ``schema: null`` row must justify itself with a note and a real check.

    Without this, "no schema" becomes the easy way to add an unchecked file to the contract.
    """
    if surface["schema"] is not None:
        pytest.skip(f"{surface['id']}: has a declared schema")
    assert surface.get("notes", "").strip(), (
        f"{surface['id']}: schema-less surfaces must explain why in 'notes'"
    )
    assert len(surface["enforced_by"]) >= 1, (
        f"{surface['id']}: schema-less surfaces need at least one execution-based check"
    )
