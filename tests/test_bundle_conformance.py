# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Bundle conformance: the shipped corpus, resolved through the real consumer's loader.

Everything here loads **this working tree** through ``kairos-ontology-toolkit``'s own
canonical loader, rather than through a fixture or a local re-implementation.

Why this file exists
--------------------
``tests/test_toolkit_contract.py`` proves the toolkit can read our *published surfaces* —
patterns, archetypes, schemas. Nothing resolved the bundle's actual ontology content, so
v1.16.0 shipped and released with defects that only appeared the first time a hub tried
to use it: three TTLs whose import closure could not resolve, because OMG Commons, OMG
LCC and W3C SKOS were imported by the vendored FIBO tree but never mirrored or
catalogued.

The contract was tested; the corpus was not. That is the hole this closes. See gh#57.

Why these assertions and not a log grep
---------------------------------------
Calling the API directly makes a broken closure an exception, works against the currently
pinned toolkit, and needs no cross-repo fix to land. It also catches strictly more: the
missing OMG LCC mirror was **invisible** to CLI output, because the Commons failure
short-circuited the closure before LCC was ever reached. Only resolving each closure to
completion surfaced it.

Who owns the enumeration (changed after toolkit DD-173)
-------------------------------------------------------
This file used to enumerate and classify the bundle through the toolkit's
``core.inventory`` module. Toolkit DD-173 ("Reference models resolve live; there is no
inventory") deleted that module outright, with no compatibility shim: a materialized
inventory could go stale against a fixed resolver, so ``read_reference_terms`` now
resolves live from the catalog on every call.

Nothing here failed loudly when that landed. The probe for ``core/inventory.py`` simply
stopped resolving and every test in this module skipped — see gh#96. So the enumeration
and classification now live *here*, which is where they always belonged: this is the repo
that owns the bundle's layout and the only one that can rename a file or add a directory.
The single remaining toolkit dependency is ``ontology_loader``, which is precisely the
direct-read path DD-173 moved everyone to.

One test was removed rather than ported. ``test_inventory_filenames_are_injective``
guarded against two sources producing the same ``*-inventory.yaml`` and silently
clobbering each other. Post-DD-173 nothing is written per source, so the defect it
guarded cannot occur; keeping a ported version would assert a property of a file format
that no longer exists.

Skipping
--------
Skipped when the toolkit is not on this machine, so the toolkit-free ``validate`` job
stays green. The ``cross-repo-contract`` job installs the pinned toolkit and fails the
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

#: Module used to confirm a directory really is the toolkit package root. Was
#: ``inventory.py`` until toolkit DD-173 deleted it, at which point this probe stopped
#: resolving and every test here skipped silently for several releases (gh#96). Prefer a
#: module the toolkit cannot plausibly drop: ``ontology_loader`` is the DD-103 canonical
#: loader and the very thing these tests exercise, so if it disappears these tests
#: *should* stop working.
_TOOLKIT_SENTINEL = "ontology_loader.py"


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
            if (src / "kairos_ontology" / "core" / _TOOLKIT_SENTINEL).is_file():
                return src
    except (ImportError, ModuleNotFoundError):
        pass
    # 2. Env var override
    override = os.environ.get("KAIROS_TOOLKIT_SRC")
    candidates = [Path(override)] if override else []
    # 3. Sibling checkout
    candidates.append(REPO_ROOT.parent / "kairos-ontology-toolkit" / "src")
    for candidate in candidates:
        if (candidate / "kairos_ontology" / "core" / _TOOLKIT_SENTINEL).is_file():
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
def loader():
    """Import the toolkit's canonical loader, skipping if its dependencies are absent."""
    src = str(TOOLKIT_SRC)
    added = src not in sys.path
    if added:
        sys.path.insert(0, src)
    try:
        from kairos_ontology.core import ontology_loader
    except ImportError as exc:  # toolkit present but its dependencies are not
        pytest.skip(f"toolkit import failed ({exc}) — install its dependencies to run this")
    yield ontology_loader
    if added and src in sys.path:
        sys.path.remove(src)


# --- bundle classification -------------------------------------------------------------
#
# Ours, not the toolkit's (see the module docstring). Every ``.ttl`` under ONTOLOGY_ROOT
# falls into exactly one of three categories, and ``test_every_bundled_ttl_is_classified``
# fails if a file ever falls outside them — which is what makes *adding* an unaccounted-for
# ontology a PR-time failure rather than a client-hub surprise.


def _is_archived(path: Path) -> bool:
    """Superseded versions, shipped for provenance and never resolved."""
    return "archive" in path.relative_to(ONTOLOGY_ROOT).parts


def _is_pattern_template(path: Path) -> bool:
    """Copyable authoring stubs under ``blueprints/patterns/<id>/``, not bundle content."""
    parts = path.relative_to(ONTOLOGY_ROOT).parts
    return len(parts) >= 2 and parts[0] == "blueprints" and parts[1] == "patterns"


def _all_ttl() -> list[Path]:
    return sorted(ONTOLOGY_ROOT.glob("**/*.ttl"))


def _sources() -> list[Path]:
    """Every bundled TTL whose import closure must resolve."""
    return [p for p in _all_ttl() if not _is_archived(p) and not _is_pattern_template(p)]


def _rel(path: Path) -> str:
    return path.relative_to(ONTOLOGY_ROOT).as_posix()


def test_the_bundle_is_not_empty() -> None:
    """A misconfigured ONTOLOGY_ROOT would make every other assertion here vacuously true."""
    assert _all_ttl(), "no TTL files found — ONTOLOGY_ROOT is wrong"
    assert _sources(), "no resolvable sources found — the classification rules are wrong"


def test_every_source_resolves_its_import_closure(loader) -> None:
    """Every bundled TTL must resolve its full import closure, offline.

    ``degraded=False`` is the whole point: degraded mode returns a partial graph and a
    warning, which is what a hub sees as an unclearable gate failure. A closure that
    only resolves in degraded mode is a missing mirror or a missing catalog entry, not
    an acceptable steady state.
    """
    failures: list[str] = []
    for source in _sources():
        rel = _rel(source)
        if rel in EXPECTED_UNRESOLVABLE:
            continue
        try:
            result = loader.load_ontology(source, catalog_path=CATALOG, degraded=False)
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


def test_expected_unresolvable_entries_still_exist() -> None:
    """A stale exclusion is worse than none — it hides the next regression at that path."""
    known = {_rel(source) for source in _sources()}
    stale = sorted(set(EXPECTED_UNRESOLVABLE) - known)
    assert not stale, f"EXPECTED_UNRESOLVABLE names paths that no longer exist: {stale}"


def test_every_bundled_ttl_is_classified() -> None:
    """Every ``.ttl`` in the bundle is resolvable, archived, or a pattern template.

    This is the assertion with the longest half-life. The others catch today's defects;
    this one makes *adding* an unaccounted-for ontology fail here, at PR time, instead of
    surfacing in a client hub weeks after release.

    ``archive/`` is excluded deliberately: superseded versions are shipped for provenance
    and are never resolved. They are not exempt from being classified — they are
    classified as archived.
    """
    all_ttl = _all_ttl()
    resolvable = {p.resolve() for p in _sources()}
    archived = {p.resolve() for p in all_ttl if _is_archived(p)}
    templates = {p.resolve() for p in all_ttl if _is_pattern_template(p)}

    unclassified = sorted(
        _rel(p) for p in all_ttl if p.resolve() not in (resolvable | archived | templates)
    )
    assert not unclassified, (
        "TTL files that are neither resolvable, archived, nor pattern templates:\n"
        + "\n".join(f"  {p}" for p in unclassified)
    )

    overlap = sorted(_rel(p) for p in all_ttl if p.resolve() in resolvable & archived)
    assert not overlap, f"classified as both resolvable and archived: {overlap}"
