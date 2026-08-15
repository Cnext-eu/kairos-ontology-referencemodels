# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Bundle conformance: the shipped corpus, run through the real consumer's generators.

Everything here loads **this working tree** through ``kairos-ontology-toolkit``'s own
inventory and loader APIs, rather than through a fixture or a local re-implementation.

Why this file exists
--------------------
``tests/test_toolkit_contract.py`` proves the toolkit can read our *published surfaces* —
patterns, archetypes, schemas. Nothing ran the toolkit's *generators* over the bundle's
actual ontology content, so v1.16.0 shipped and released with four defects that only
appear the first time a hub runs ``kairos-ontology generate-inventory``:

  - three TTLs whose import closure could not resolve, because OMG Commons, OMG LCC and
    W3C SKOS were imported by the vendored FIBO tree but never mirrored or catalogued;
  - two files both named ``template.ttl`` that produced one ``template-inventory.yaml``
    and silently clobbered each other.

The contract was tested; the corpus was not. That is the hole this closes. See gh#57.

Why these assertions and not a log grep
---------------------------------------
The obvious gate is to run ``generate-inventory`` and grep its output for warnings. That
was rejected: the command **exits 0 while emitting those failures** (toolkit #405), so
the grep is load-bearing, and it matches emoji in CLI output — brittle across locales and
toolkit releases. Calling the API directly makes a broken closure an exception, works
against the currently pinned toolkit, and needs no cross-repo fix to land.

It also catches strictly more. The missing OMG LCC mirror was **invisible** to the CLI
output: the Commons failure short-circuited the closure before LCC was ever reached. Only
resolving each closure to completion surfaced it.

Skipping
--------
Skipped when the toolkit is not on this machine, so the toolkit-free ``validate`` job
stays green. The ``cross-repo-contract`` job sets ``KAIROS_TOOLKIT_SRC`` and fails the
build if these tests skip instead of running.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_ROOT = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models"
CATALOG = ONTOLOGY_ROOT / "catalog-v001.xml"

# Sources whose closure is knowingly unresolvable, as ``<path relative to ONTOLOGY_ROOT>:
# <reason>``. Empty on purpose. It exists so that excluding a file is a reviewed edit to
# this list with a written reason, rather than a silent skip — the failure mode gh#57
# describes, where an exclusion list quietly becomes the place broken things go to die.
EXPECTED_UNRESOLVABLE: dict[str, str] = {}


def _toolkit_src() -> Path | None:
    """Return the directory containing the ``kairos_ontology`` package, or None.

    Resolution order:
    1. Installed package (site-packages) — works after ``uv sync --extra dev`` which installs
       the toolkit as a wheel dependency.
    2. ``KAIROS_TOOLKIT_SRC`` env var — explicit override for local development.
    3. Sibling checkout at ``../kairos-ontology-toolkit/src`` — local development convenience.
    """
    # 1. Installed package
    try:
        import importlib

        spec = importlib.util.find_spec("kairos_ontology")
        if spec and spec.origin:
            src = Path(spec.origin).resolve().parent.parent
            if (src / "kairos_ontology" / "core" / "inventory.py").is_file():
                return src
    except (ImportError, ModuleNotFoundError):
        pass
    # 2. Env var override
    override = os.environ.get("KAIROS_TOOLKIT_SRC")
    candidates = [Path(override)] if override else []
    # 3. Sibling checkout
    candidates.append(REPO_ROOT.parent / "kairos-ontology-toolkit" / "src")
    for candidate in candidates:
        if (candidate / "kairos_ontology" / "core" / "inventory.py").is_file():
            return candidate
    return None


TOOLKIT_SRC = _toolkit_src()

pytestmark = pytest.mark.skipif(
    TOOLKIT_SRC is None,
    reason=(
        "kairos-ontology-toolkit source not found — set KAIROS_TOOLKIT_SRC or place a "
        "checkout at ../kairos-ontology-toolkit"
    ),
)


@pytest.fixture(scope="module")
def toolkit():
    """Import the toolkit's inventory + loader modules, skipping if its deps are absent."""
    src = str(TOOLKIT_SRC)
    added = src not in sys.path
    if added:
        sys.path.insert(0, src)
    try:
        from kairos_ontology.core import inventory, ontology_loader
    except ImportError as exc:  # toolkit present but its dependencies are not
        pytest.skip(f"toolkit import failed ({exc}) — install its dependencies to run this")
    yield inventory, ontology_loader
    if added and src in sys.path:
        sys.path.remove(src)


def _sources(inventory) -> list[Path]:
    """Every TTL the consumer considers inventoriable, via the consumer's own rule."""
    return inventory.iter_reference_inventory_sources(ONTOLOGY_ROOT)


def _rel(path: Path) -> str:
    return path.relative_to(ONTOLOGY_ROOT).as_posix()


def test_inventory_filenames_are_injective(toolkit) -> None:
    """No two sources may produce the same inventory file.

    ``generate-inventory`` writes one YAML per source and reports a collision by
    *skipping* the loser — so a collision is silent data loss dressed as a warning, and
    the resulting ``check-inventory`` STALE failure can never be cleared by re-running.

    Asserted here rather than in the toolkit because the filenames are ours: this is the
    repo that can actually rename the file.
    """
    inventory, _ = toolkit
    by_name: dict[str, list[str]] = {}
    for source in _sources(inventory):
        name = inventory.inventory_filename(source, ref_models_dir=ONTOLOGY_ROOT)
        by_name.setdefault(name, []).append(_rel(source))

    collisions = {name: paths for name, paths in by_name.items() if len(paths) > 1}
    assert not collisions, "inventory filename collisions (last write wins, rest are lost):\n" + "\n".join(
        f"  {name} ← {', '.join(sorted(paths))}" for name, paths in sorted(collisions.items())
    )


def test_every_source_resolves_its_import_closure(toolkit) -> None:
    """Every inventoriable TTL must resolve its full import closure, offline.

    ``degraded=False`` is the whole point: degraded mode returns a partial graph and a
    warning, which is what a hub sees as an unclearable gate failure. A closure that
    only resolves in degraded mode is a missing mirror or a missing catalog entry, not
    an acceptable steady state.
    """
    inventory, ontology_loader = toolkit
    failures: list[str] = []
    for source in _sources(inventory):
        rel = _rel(source)
        if rel in EXPECTED_UNRESOLVABLE:
            continue
        try:
            result = ontology_loader.load_ontology(source, catalog_path=CATALOG, degraded=False)
        except Exception as exc:  # noqa: BLE001 — any loader failure is a bundle defect
            failures.append(f"  {rel}: {type(exc).__name__}: {exc}")
            continue
        if not getattr(result, "complete", True):
            failures.append(f"  {rel}: closure incomplete: {result.warnings()}")

    assert not failures, (
        "bundled ontologies do not resolve against catalog-v001.xml:\n"
        + "\n".join(failures)
        + "\n\nFix the missing mirror or catalog entry. Adding to EXPECTED_UNRESOLVABLE "
        "is a reviewed decision, not a way to make this green."
    )


def test_expected_unresolvable_entries_still_exist(toolkit) -> None:
    """A stale exclusion is worse than none — it hides the next regression at that path."""
    inventory, _ = toolkit
    known = {_rel(source) for source in _sources(inventory)}
    stale = sorted(set(EXPECTED_UNRESOLVABLE) - known)
    assert not stale, f"EXPECTED_UNRESOLVABLE names paths that no longer exist: {stale}"


def test_every_bundled_ttl_is_classified(toolkit) -> None:
    """Every ``.ttl`` in the bundle is inventoriable or archived — nothing is unaccounted for.

    This is the assertion with the longest half-life. The other two catch today's defects;
    this one makes *adding* an un-inventoriable ontology fail here, at PR time, instead of
    surfacing in a client hub weeks after release.

    ``archive/`` is excluded deliberately and by the consumer's own rule
    (``is_archived_ref_model_source``): superseded versions are shipped for provenance and
    are never inventoried. They are not exempt from being classified — they are classified
    as archived.
    """
    inventory, _ = toolkit
    all_ttl = sorted(ONTOLOGY_ROOT.glob("**/*.ttl"))
    assert all_ttl, "no TTL files found — ONTOLOGY_ROOT is wrong"

    inventoriable = {p.resolve() for p in _sources(inventory)}
    archived = {
        p.resolve()
        for p in all_ttl
        if inventory.is_archived_ref_model_source(p, ref_models_dir=ONTOLOGY_ROOT)
    }

    unclassified = sorted(_rel(p) for p in all_ttl if p.resolve() not in inventoriable | archived)
    assert not unclassified, (
        "TTL files the consumer would neither inventory nor treat as archived:\n"
        + "\n".join(f"  {p}" for p in unclassified)
    )

    overlap = sorted(_rel(p) for p in all_ttl if p.resolve() in inventoriable & archived)
    assert not overlap, f"classified as both inventoriable and archived: {overlap}"
