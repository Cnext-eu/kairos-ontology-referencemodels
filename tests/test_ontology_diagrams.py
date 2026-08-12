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


def test_input_mode_renders_customer_ontology(tmp_path) -> None:
    """A customer can point --input at their own Turtle; imported reference classes render
    as external stubs labelled by their suite."""
    model = tmp_path / "model"
    model.mkdir()
    (model / "hub.ttl").write_text(
        """@prefix : <https://acme.example/ont/logistics#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dcsa: <https://www.kairosflow.ai/ont/dcsa/booking#> .

<https://acme.example/ont/logistics> a owl:Ontology .
:Shipment a owl:Class .
:PriorityShipment a owl:Class ; rdfs:subClassOf :Shipment .
:customerName a owl:DatatypeProperty ; rdfs:domain :Shipment ; rdfs:range xsd:string .
:coversBooking a owl:ObjectProperty ; rdfs:domain :Shipment ; rdfs:range dcsa:Booking .
""",
        encoding="utf-8",
    )
    bases = gen.suite_bases()
    out = gen.render_input(model, "ACME Hub", bases)

    assert "# ACME Hub — class diagram" in out
    # Customer's own classes are nodes; the imported DCSA class is an external stub.
    assert "class Shipment" in out
    assert "Shipment <|-- PriorityShipment" in out
    assert "<<dcsa>>" in out and "coversBooking" in out


def test_input_mode_without_ontology_iri_treats_all_classes_as_own(tmp_path) -> None:
    """A customer ontology with no owl:Ontology root still renders its classes."""
    model = tmp_path / "model"
    model.mkdir()
    (model / "hub.ttl").write_text(
        """@prefix : <https://acme.example/x#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:Foo a owl:Class .
:Bar a owl:Class .
""",
        encoding="utf-8",
    )
    out = gen.render_input(model, "No Root", gen.suite_bases())
    assert "class Foo" in out and "class Bar" in out


def _all_diagram_md() -> list[Path]:
    return sorted(gen.DIAGRAMS_DIR.rglob("*.md"))


def test_every_mermaid_block_has_a_current_mmd_export() -> None:
    """Each fenced ```mermaid block in a diagram .md has a matching raw .mmd sibling.

    Same --check contract as the generator: the .mmd files are a pure derivative of the
    committed markdown, so if a .md changed and .mmd was not refreshed, this fails.
    """
    for md_path in _all_diagram_md():
        for mmd_path, body in gen.mmd_targets_for(md_path):
            assert mmd_path.exists(), (
                f"{mmd_path} is missing — run python scripts/generate_ontology_diagrams.py"
            )
            assert mmd_path.read_text(encoding="utf-8") == body, (
                f"{mmd_path.name} is stale — run: python scripts/generate_ontology_diagrams.py"
            )


def test_no_orphan_mmd_files() -> None:
    """Every .mmd corresponds to a mermaid block that still exists."""
    expected = {
        mmd_path
        for md_path in _all_diagram_md()
        for mmd_path, _ in gen.mmd_targets_for(md_path)
    }
    orphans = [p for p in gen.DIAGRAMS_DIR.rglob("*.mmd") if p not in expected]
    assert not orphans, f"orphaned .mmd files: {orphans}"


def test_mmd_export_is_plain_mermaid_without_fences_or_banner() -> None:
    """A raw .mmd is directly loadable by mmdc / mermaid.live: no markdown, no HTML banner."""
    sample = gen.OUTPUT_DIR / "dcsa.mmd"
    text = sample.read_text(encoding="utf-8")
    assert "```" not in text
    assert "<!--" not in text
    assert text.lstrip().startswith("classDiagram")

