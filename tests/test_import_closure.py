# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Tests for the owl:imports closure gate (validate_structure check 10, gh#97).

A module that asserts rdfs:domain or rdfs:range against a class it neither declares
nor imports leaves the assertion dangling: the class is never typed in that module's
graph, so the property is invisible to any consumer resolving "which properties does
class X carry". 50 such domain assertions and ~100 range assertions shipped across 7
vendor trees, and they produced a false reference-model gap report against a client
hub — TradeParty looked like it was missing credit limit, payment terms and bank
details when all four were present but unreachable.
"""

from pathlib import Path

from scripts.validate_structure import (
    _declared_imports,
    _domain_range_spans,
    _is_vendor_root,
    _ontology_iri,
    _prefix_map,
    validate_import_closure,
)

KAIROS = "https://www.kairosflow.ai/ont"


def _write_module(
    root: Path,
    vendor: str,
    module: str | None,
    *,
    prefixes: dict[str, str] | None = None,
    imports: tuple[str, ...] = (),
    body: str = "",
) -> Path:
    """Write a minimal module TTL. ``module=None`` writes the vendor root."""
    iri = f"{KAIROS}/{vendor}"
    if module:
        iri = f"{iri}/{module}"
        path = root / vendor / "current" / module / f"{module}.ttl"
    else:
        path = root / vendor / "current" / f"{vendor}.ttl"
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"@prefix : <{iri}#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
    ]
    for label, namespace in (prefixes or {}).items():
        lines.append(f"@prefix {label}: <{namespace}> .")
    lines += ["", f"<{iri}> a owl:Ontology ;", '    owl:versionInfo "1.0.0" ;']
    lines += [f"    owl:imports <{target}> ;" for target in imports]
    lines += ["    rdfs:seeAlso <https://example.invalid/> .", "", body]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _failures(derived: Path) -> list[str]:
    result = validate_import_closure(verbose=False, scan_roots=[derived])
    return [m.strip() for m in result.messages if m.lstrip().startswith("✗")]


# ── the core rule ────────────────────────────────────────────────────────────

def test_foreign_domain_without_covering_import_fails(tmp_path: Path) -> None:
    """The exact shape of the gh#97 defect.

    bsp/financial declared the ``party:`` prefix and asserted
    ``rdfs:domain party:TradeParty`` while importing nothing, so TradeParty was never
    an owl:Class in financial's graph and the four properties hanging off it could
    not be found from the party side.
    """
    derived = tmp_path / "derived-ontologies"
    _write_module(derived, "acme", "party", body=":TradeParty a owl:Class .\n")
    _write_module(
        derived,
        "acme",
        "financial",
        prefixes={"party": f"{KAIROS}/acme/party#"},
        body=(
            ":creditLimit a owl:DatatypeProperty ;\n"
            "    rdfs:domain party:TradeParty ;\n"
            "    rdfs:range rdfs:Literal .\n"
        ),
    )

    failures = _failures(derived)
    assert any("acme/party" in f and "dangling" in f for f in failures), failures


def test_foreign_domain_with_covering_import_passes(tmp_path: Path) -> None:
    derived = tmp_path / "derived-ontologies"
    _write_module(derived, "acme", "party", body=":TradeParty a owl:Class .\n")
    _write_module(
        derived,
        "acme",
        "financial",
        prefixes={"party": f"{KAIROS}/acme/party#"},
        imports=(f"{KAIROS}/acme/party",),
        body=(
            ":creditLimit a owl:DatatypeProperty ;\n"
            "    rdfs:domain party:TradeParty ;\n"
            "    rdfs:range rdfs:Literal .\n"
        ),
    )

    assert _failures(derived) == []


def test_transitive_import_satisfies_the_closure(tmp_path: Path) -> None:
    """Reachability is transitive: A -> B -> C means A may reference C.

    Guards against a direct-imports-only check. In the real pack bsp/financial
    reaches bsp/party through bsp/commercial, so a stricter rule would demand an
    import that OWL does not require.
    """
    derived = tmp_path / "derived-ontologies"
    _write_module(derived, "acme", "party", body=":TradeParty a owl:Class .\n")
    _write_module(derived, "acme", "commercial", imports=(f"{KAIROS}/acme/party",))
    _write_module(
        derived,
        "acme",
        "financial",
        prefixes={"party": f"{KAIROS}/acme/party#"},
        imports=(f"{KAIROS}/acme/commercial",),
        body=(
            ":creditLimit a owl:DatatypeProperty ;\n"
            "    rdfs:domain party:TradeParty ;\n"
            "    rdfs:range rdfs:Literal .\n"
        ),
    )

    assert _failures(derived) == []


def test_cyclic_imports_are_accepted(tmp_path: Path) -> None:
    """An owl:imports cycle must neither fail nor hang.

    BSP genuinely cycles: commercial -> financial -> commercial, caused by
    ``:relatedToShipment rdfs:domain fin:Invoice`` living in the commercial module.
    Both this repo's load_import_closure and the toolkit's ontology_loader guard on
    already-visited paths, so a cycle costs at most one diagnostic and cannot drop
    triples. Failing on it would force a restructure that buys nothing.
    """
    derived = tmp_path / "derived-ontologies"
    _write_module(
        derived,
        "acme",
        "commercial",
        prefixes={"fin": f"{KAIROS}/acme/financial#"},
        imports=(f"{KAIROS}/acme/financial",),
        body=(
            ":Shipment a owl:Class .\n\n"
            ":relatedToShipment a owl:ObjectProperty ;\n"
            "    rdfs:domain fin:Invoice ;\n"
            "    rdfs:range :Shipment .\n"
        ),
    )
    _write_module(
        derived,
        "acme",
        "financial",
        prefixes={"comm": f"{KAIROS}/acme/commercial#"},
        imports=(f"{KAIROS}/acme/commercial",),
        body=(
            ":Invoice a owl:Class .\n\n"
            ":hasInvoice a owl:ObjectProperty ;\n"
            "    rdfs:domain comm:Shipment ;\n"
            "    rdfs:range :Invoice .\n"
        ),
    )

    assert _failures(derived) == []


def test_union_range_members_are_checked(tmp_path: Path) -> None:
    """A foreign class inside owl:unionOf must be checked, not skipped.

    ``rdfs:range [ owl:unionOf ( a:X b:Y ) ]`` does not match a simple
    ``rdfs:range <prefixed-name>`` regex, so an extractor built on one would pass
    every union-typed cross-module reference in silence. IMO and TIC both ship them.
    """
    derived = tmp_path / "derived-ontologies"
    _write_module(derived, "acme", "vessel", body=":Vessel a owl:Class .\n")
    _write_module(
        derived,
        "acme",
        "events",
        prefixes={"vr": f"{KAIROS}/acme/vessel#"},
        body=(
            ":Event a owl:Class .\n\n"
            ":subject a owl:ObjectProperty ;\n"
            "    rdfs:domain :Event ;\n"
            "    rdfs:range [ owl:unionOf ( vr:Vessel :Event ) ] .\n"
        ),
    )

    failures = _failures(derived)
    assert any("acme/vessel" in f for f in failures), failures


# ── the leaf-must-not-import-a-vendor-root rule ──────────────────────────────

def test_leaf_module_importing_vendor_root_fails(tmp_path: Path) -> None:
    """A leaf must import the sibling module, never the vendor aggregator.

    mmt/consignment ranged on ``mmt:DangerousGoods``, a class in the MMT *root*
    namespace. Closing that by importing <.../ont/mmt> would have pulled all ten MMT
    modules into every consumer of mmt/consignment, defeating the per-domain import
    scoping in data-domains.yaml and masking the very defect gh#98 is about. The
    terms were moved to a mmt/dangerous-goods leaf module instead.
    """
    derived = tmp_path / "derived-ontologies"
    _write_module(derived, "acme", None, imports=(f"{KAIROS}/acme/party",))
    _write_module(derived, "acme", "party", body=":TradeParty a owl:Class .\n")
    _write_module(derived, "acme", "financial", imports=(f"{KAIROS}/acme",))

    failures = _failures(derived)
    assert any("vendor root" in f for f in failures), failures


def test_vendor_root_may_import_modules(tmp_path: Path) -> None:
    """One-directional rule: an aggregator importing its leaves is the correct shape."""
    derived = tmp_path / "derived-ontologies"
    _write_module(derived, "acme", None, imports=(f"{KAIROS}/acme/party",))
    _write_module(derived, "acme", "party", body=":TradeParty a owl:Class .\n")

    assert _failures(derived) == []


# ── things that must NOT be flagged ──────────────────────────────────────────

def test_own_namespace_references_need_no_import(tmp_path: Path) -> None:
    derived = tmp_path / "derived-ontologies"
    _write_module(
        derived,
        "acme",
        "party",
        body=(
            ":TradeParty a owl:Class .\n\n"
            ":hasName a owl:DatatypeProperty ;\n"
            "    rdfs:domain :TradeParty ;\n"
            "    rdfs:range rdfs:Literal .\n"
        ),
    )

    assert _failures(derived) == []


def test_non_kairos_namespaces_are_ignored(tmp_path: Path) -> None:
    """schema.org and xsd targets are not pack modules, so they need no owl:imports."""
    derived = tmp_path / "derived-ontologies"
    _write_module(
        derived,
        "acme",
        "party",
        prefixes={"schema": "https://schema.org/"},
        body=(
            ":TradeParty a owl:Class ;\n"
            "    rdfs:subClassOf schema:Organization .\n\n"
            ":altName a owl:DatatypeProperty ;\n"
            "    rdfs:domain :TradeParty ;\n"
            "    rdfs:range schema:Text .\n"
        ),
    )

    assert _failures(derived) == []


def test_archive_trees_are_not_scanned(tmp_path: Path) -> None:
    """Archived versions are frozen history and must never fail the gate."""
    derived = tmp_path / "derived-ontologies"
    _write_module(derived, "acme", "party", body=":TradeParty a owl:Class .\n")
    archived = derived / "acme" / "archive" / "1.0.0" / "financial"
    archived.mkdir(parents=True)
    (archived / "financial.ttl").write_text(
        f"@prefix : <{KAIROS}/acme/financial#> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        f"@prefix party: <{KAIROS}/acme/party#> .\n"
        "\n"
        f"<{KAIROS}/acme/financial> a owl:Ontology ;\n"
        '    owl:versionInfo "1.0.0" .\n'
        "\n"
        ":creditLimit a owl:DatatypeProperty ;\n"
        "    rdfs:domain party:TradeParty ;\n"
        "    rdfs:range rdfs:Literal .\n",
        encoding="utf-8",
    )

    assert _failures(derived) == []


def test_domain_mentioned_only_in_a_comment_is_not_a_declaration(tmp_path: Path) -> None:
    """Prose naming a foreign class must not be treated as an rdfs:domain triple."""
    derived = tmp_path / "derived-ontologies"
    _write_module(
        derived,
        "acme",
        "financial",
        prefixes={"party": f"{KAIROS}/acme/party#"},
        body=(
            ":creditLimit a owl:DatatypeProperty ;\n"
            '    rdfs:comment """Was rdfs:domain party:TradeParty before gh#97.""" ;\n'
            "    rdfs:domain :Account ;\n"
            "    rdfs:range rdfs:Literal .\n"
        ),
    )

    assert _failures(derived) == []


# ── helper units ─────────────────────────────────────────────────────────────

def test_prefix_map_captures_default_and_labelled_prefixes() -> None:
    text = (
        f"@prefix : <{KAIROS}/mmt/cargo#> .\n"
        f"@prefix mmt-evt: <{KAIROS}/mmt/events#> .\n"
    )
    prefixes = _prefix_map(text)
    assert prefixes[""] == f"{KAIROS}/mmt/cargo#"
    assert prefixes["mmt-evt"] == f"{KAIROS}/mmt/events#"


def test_ontology_iri_is_found_on_a_later_line() -> None:
    """Regression: without re.MULTILINE the ^ anchor only matches at line 1.

    The first cut of this check silently found zero ontologies and reported a clean
    pass over an empty document set.
    """
    text = (
        f"@prefix : <{KAIROS}/mmt/cargo#> .\n"
        "\n"
        "# Ontology Metadata\n"
        f"<{KAIROS}/mmt/cargo> a owl:Ontology ;\n"
    )
    assert _ontology_iri(text) == f"{KAIROS}/mmt/cargo"


def test_declared_imports_reads_comma_continuation_lists() -> None:
    """Both shipped styles: comma-continuation (WCO/DCSA) and per-statement (MMT/BSP)."""
    text = (
        f"    owl:imports <{KAIROS}/a> ,\n"
        f"                <{KAIROS}/b> ;\n"
        f"    owl:imports <{KAIROS}/c> ;\n"
    )
    assert _declared_imports(text) == {f"{KAIROS}/a", f"{KAIROS}/b", f"{KAIROS}/c"}


def test_domain_range_span_stops_at_the_statement_terminator() -> None:
    text = (
        ":p a owl:ObjectProperty ;\n"
        "    rdfs:domain a:X ;\n"
        "    rdfs:range b:Y .\n"
        ":q a owl:ObjectProperty ;\n"
        "    rdfs:domain c:Z ;\n"
    )
    spans = list(_domain_range_spans(text))
    assert [predicate for predicate, _ in spans] == [
        "rdfs:domain",
        "rdfs:range",
        "rdfs:domain",
    ]
    assert "b:Y" not in spans[0][1], "the domain span leaked into the range statement"


def test_vendor_root_detection() -> None:
    assert _is_vendor_root(f"{KAIROS}/mmt")
    assert not _is_vendor_root(f"{KAIROS}/mmt/cargo")
    assert not _is_vendor_root("https://schema.org/Organization")
