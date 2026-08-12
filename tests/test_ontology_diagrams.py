# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""The generated ontology class diagrams must be current and self-consistent.

Mirrors the ``--check`` contract of the other generators: if a suite's Turtle changed and its
diagram was not regenerated, this fails — the same guarantee CI enforces by running the script
with ``--check``.
"""

from pathlib import Path

import pytest

from scripts import generate_ontology_diagrams as gen

EXPECTED_SUITES = {
    "BSP", "DCSA", "IMO", "MMT", "RAIL", "SupplyChain", "Sustainability", "TIC", "WCO",
}


def test_all_expected_suites_are_discovered() -> None:
    names = {d.name for d in gen.suite_dirs()}
    assert EXPECTED_SUITES <= names, f"missing suites: {EXPECTED_SUITES - names}"


def test_every_suite_has_a_base_namespace() -> None:
    bases = gen.suite_bases()
    for name in EXPECTED_SUITES:
        assert bases.get(name), f"{name} has no derivable base namespace"


@pytest.mark.parametrize("suite", sorted(EXPECTED_SUITES))
def test_generated_diagram_is_current(suite: str) -> None:
    bases = gen.suite_bases()
    expected = gen.render_suite(suite, None, bases)
    path = gen.OUTPUT_DIR / f"{suite.lower()}.md"
    assert path.exists(), f"{path} is missing — run scripts/generate_ontology_diagrams.py"
    on_disk = path.read_text(encoding="utf-8")
    assert on_disk == expected, (
        f"{path.name} is stale — run: python scripts/generate_ontology_diagrams.py"
    )


def test_generated_index_is_current() -> None:
    bases = gen.suite_bases()
    expected = gen.render_index(bases)
    path = gen.OUTPUT_DIR / "README.md"
    assert path.read_text(encoding="utf-8") == expected, (
        "generated/README.md is stale — run: python scripts/generate_ontology_diagrams.py"
    )


def test_supplychain_is_a_cross_suite_bridge() -> None:
    """SupplyChain owns no classes but links classes across other suites."""
    bases = gen.suite_bases()
    content = gen.render_suite("SupplyChain", None, bases)
    assert "Classes: 0" in content
    # Bridge endpoints are external stubs from at least two other suites.
    assert "<<dcsa>>" in content and "<<mmt>>" in content


def test_generated_files_carry_the_do_not_edit_banner() -> None:
    for md in gen.OUTPUT_DIR.glob("*.md"):
        assert "DO NOT EDIT" in md.read_text(encoding="utf-8").splitlines()[0]
