# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Focused tests for repository structure classification."""

import json
from pathlib import Path

import pytest
import yaml

from scripts.validate_structure import (
    ENTITY_PROJECTIONS_REL,
    ENTITY_PROJECTIONS_SCHEMA,
    PACKS_DIR,
    PATTERN_SCHEMA,
    PATTERNS_DIR,
    entity_projection_errors,
    find_domain_subfolders,
    pattern_schema_errors,
    validate_entity_projections,
    validate_pattern_template,
)


def test_accelerator_support_folders_are_not_domain_modules(tmp_path: Path) -> None:
    accelerator = tmp_path / "accelerator-packs" / "logistics"
    current = accelerator / "current"
    current.mkdir(parents=True)
    for name in ("blueprint", "profiles", "contracts", "examples", "docs", "real-domain"):
        (current / name).mkdir()

    assert [path.name for path in find_domain_subfolders(accelerator)] == ["real-domain"]


def test_support_named_folders_remain_domains_outside_accelerators(tmp_path: Path) -> None:
    ontology = tmp_path / "derived-ontologies" / "example"
    current = ontology / "current"
    (current / "docs").mkdir(parents=True)

    assert [path.name for path in find_domain_subfolders(ontology)] == ["docs"]


# ── pattern.yaml schema ──────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def pattern_schema() -> dict:
    return json.loads(PATTERN_SCHEMA.read_text(encoding="utf-8"))


def test_every_shipped_pattern_validates(pattern_schema: dict) -> None:
    pattern_files = sorted(PATTERNS_DIR.glob("*/pattern.yaml"))
    assert pattern_files, "no pattern.yaml files found"
    for pattern_file in pattern_files:
        data = yaml.safe_load(pattern_file.read_text(encoding="utf-8"))
        errors = pattern_schema_errors(data, pattern_schema)
        assert not errors, f"{pattern_file.parent.name}: {errors}"


def test_typoed_key_inside_anti_pattern_entry_fails(pattern_schema: dict) -> None:
    # The v1.13.0 defect class: a wrong-but-parseable key inside a list entry.
    data = {
        "id": "example-pattern",
        "problem": "p",
        "applicability": "a",
        "normativity": {"naming": "normative", "participants": "advisory",
                        "cardinality_rules": "advisory"},
        "anti_patterns": [{
            "id": "some-anti-pattern",
            "description": "d",
            "rejection_reason": "r",
            "banned_tokens": ["eta"],  # typo: banned_name_tokens
        }],
    }
    assert pattern_schema_errors(data, pattern_schema)


def test_stray_rule_key_shape_fails(pattern_schema: dict) -> None:
    # A rule: key on a QUARTET entry is the shape that shipped invalid in
    # v1.13.0 (there it was invalid YAML; parseable variants must fail here).
    data = {
        "id": "example-pattern",
        "problem": "p",
        "applicability": "a",
        "normativity": {"naming": "normative", "participants": "advisory",
                        "cardinality_rules": "advisory"},
        "naming_conventions": [{
            "qualifier": "estimated",
            "start_or_arrival": "estimatedStart",
            "arrival_variant": "estimatedArrival",
            "end_or_departure": "estimatedEnd",
            "departure_variant": "estimatedDeparture",
            "rule": "prose that belongs in naming_rule",
        }],
    }
    assert pattern_schema_errors(data, pattern_schema)


def test_exemption_without_reason_fails(pattern_schema: dict) -> None:
    data = {
        "id": "example-pattern",
        "problem": "p",
        "applicability": "a",
        "normativity": {"naming": "normative", "participants": "advisory",
                        "cardinality_rules": "advisory"},
        "anti_patterns": [{
            "id": "some-anti-pattern",
            "description": "d",
            "rejection_reason": "r",
            "banned_name_tokens": ["due"],
            "exemptions": [{"name": "dueDate"}],  # no reason — must be cited
        }],
    }
    assert pattern_schema_errors(data, pattern_schema)


def test_grain_collision_mapping_without_reason_fails(pattern_schema: dict) -> None:
    # Class-anchored collisions are {against, reason}; an against without its
    # reason (or with a stray key) must fail, not silently half-validate.
    data = {
        "id": "example-pattern",
        "problem": "p",
        "applicability": "a",
        "normativity": {"naming": "normative", "participants": "advisory",
                        "cardinality_rules": "advisory"},
        "grain_collisions": [
            {"against": "https://www.kairosflow.ai/ont/bsp/party#TradeParty"},
        ],
    }
    assert pattern_schema_errors(data, pattern_schema)


def test_grain_collision_prose_and_mapping_shapes_both_validate(pattern_schema: dict) -> None:
    # Two shapes by design: prose is reserved for grain warnings that name no
    # class; class-anchored collisions carry a scalar against + reason.
    data = {
        "id": "example-pattern",
        "problem": "p",
        "applicability": "a",
        "normativity": {"naming": "normative", "participants": "advisory",
                        "cardinality_rules": "advisory"},
        "grain_collisions": [
            "Source-noun ≠ canonical grain: prose warning naming no class.",
            {"against": "https://www.kairosflow.ai/ont/bsp/party#TradeParty",
             "reason": "Role-bearing parent; not the durable identity."},
        ],
    }
    assert not pattern_schema_errors(data, pattern_schema)


def test_custom_top_level_key_is_allowed(pattern_schema: dict) -> None:
    # Open top level is the library's documented design; the toolkit loader
    # preserves unknown keys in `extra` and its ledger reports them loudly.
    data = {
        "id": "example-pattern",
        "problem": "p",
        "applicability": "a",
        "normativity": {"naming": "normative", "participants": "advisory",
                        "cardinality_rules": "advisory"},
        "my_custom_block": {"anything": "goes"},
    }
    assert not pattern_schema_errors(data, pattern_schema)


# ── entity-projections.yaml schema ───────────────────────────────────────────

@pytest.fixture(scope="module")
def projection_schema() -> dict:
    return json.loads(ENTITY_PROJECTIONS_SCHEMA.read_text(encoding="utf-8"))


def _valid_projection_document() -> dict:
    """The minimum shape a projection file must have; each bad-case test breaks one thing."""
    return {
        "schema_version": 1,
        "projections": [{
            "id": "postal-address",
            "target_concept": "Address",
            "target_candidates": ["https://www.kairosflow.ai/ont/bsp/reference-data#Address"],
            "min_complementary_parts": 2,
            "relationship_naming": "has{Role}Address",
            "default_relationship": "hasAddress",
            "cardinality": "1:n",
            "part_kinds": [
                {"kind": "street", "tokens": ["street"]},
                {"kind": "postal", "tokens": ["zip"], "compact": ["postalcode"]},
            ],
            "role_qualifiers": ["pickup", "destination"],
            "context_tokens": ["location"],
        }],
    }


def test_reference_document_validates(projection_schema: dict) -> None:
    assert not entity_projection_errors(_valid_projection_document(), projection_schema)


def test_every_shipped_entity_projection_validates(projection_schema: dict) -> None:
    """Whatever packs do ship must be valid. Zero shipped files is legal (DD-188)."""
    shipped = sorted(
        pack / ENTITY_PROJECTIONS_REL
        for pack in PACKS_DIR.iterdir()
        if pack.is_dir() and (pack / ENTITY_PROJECTIONS_REL).is_file()
    )
    for path in shipped:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert not entity_projection_errors(data, projection_schema), path


def test_logistics_ships_a_postal_address_projection() -> None:
    """The pack that motivated DD-188 must actually carry the projection."""
    path = PACKS_DIR / "logistics" / ENTITY_PROJECTIONS_REL
    assert path.is_file(), "logistics must ship entity-projections.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    projection = next(p for p in data["projections"] if p["id"] == "postal-address")
    # The roles whose absence from the toolkit's compiled-in vocabulary broke
    # detection on a live logistics hub.
    assert {"pickup", "origin", "destination"} <= set(projection["role_qualifiers"])


def test_typoed_key_inside_part_kind_fails(projection_schema: dict) -> None:
    data = _valid_projection_document()
    data["projections"][0]["part_kinds"][0]["token"] = ["street"]  # typo: tokens
    assert entity_projection_errors(data, projection_schema)


def test_token_with_a_separator_fails(projection_schema: dict) -> None:
    # Tokens are matched against a lower-cased, separator-stripped name, so
    # 'address_line' would silently never match anything.
    data = _valid_projection_document()
    data["projections"][0]["part_kinds"][0]["tokens"] = ["address_line"]
    assert entity_projection_errors(data, projection_schema)


def test_relationship_naming_without_role_placeholder_fails(projection_schema: dict) -> None:
    data = _valid_projection_document()
    data["projections"][0]["relationship_naming"] = "hasAddress"
    assert entity_projection_errors(data, projection_schema)


def test_min_complementary_parts_of_one_fails(projection_schema: dict) -> None:
    # At 1 a lone country column becomes an address — the false positive the
    # threshold exists to prevent.
    data = _valid_projection_document()
    data["projections"][0]["min_complementary_parts"] = 1
    assert entity_projection_errors(data, projection_schema)


def test_weak_and_requires_together_fail(projection_schema: dict) -> None:
    data = _valid_projection_document()
    data["projections"][0]["part_kinds"][0].update({"weak": True, "requires": "context"})
    assert entity_projection_errors(data, projection_schema)


def test_empty_target_candidates_fail(projection_schema: dict) -> None:
    data = _valid_projection_document()
    data["projections"][0]["target_candidates"] = []
    assert entity_projection_errors(data, projection_schema)


def test_duplicate_part_kind_fails(projection_schema: dict) -> None:
    # uniqueItems cannot see this: the two entries differ in their tokens.
    data = _valid_projection_document()
    data["projections"][0]["part_kinds"].append({"kind": "street", "tokens": ["strasse"]})
    errors = entity_projection_errors(data, projection_schema)
    assert any("duplicate part kind" in e for e in errors)


def test_duplicate_projection_id_fails(projection_schema: dict) -> None:
    data = _valid_projection_document()
    data["projections"].append(dict(data["projections"][0]))
    errors = entity_projection_errors(data, projection_schema)
    assert any("duplicate projection id" in e for e in errors)


def test_requires_context_without_context_tokens_fails(projection_schema: dict) -> None:
    data = _valid_projection_document()
    data["projections"][0]["part_kinds"][0]["requires"] = "context"
    data["projections"][0].pop("context_tokens")
    errors = entity_projection_errors(data, projection_schema)
    assert any("can never count" in e for e in errors)


def test_fewer_kinds_than_required_fails(projection_schema: dict) -> None:
    data = _valid_projection_document()
    data["projections"][0]["min_complementary_parts"] = 3
    errors = entity_projection_errors(data, projection_schema)
    assert any("can never fire" in e for e in errors)


def test_absent_file_is_a_pass_not_a_failure() -> None:
    """A pack shipping no projection file must pass: no config, no candidates.

    financial-services deliberately ships none. If this ever failed, the honest
    'absent' state would be unavailable and someone would invent a vocabulary to
    satisfy the validator — the exact failure DD-188 forbids.
    """
    fs = PACKS_DIR / "financial-services"
    assert fs.is_dir()
    assert not (fs / ENTITY_PROJECTIONS_REL).is_file(), (
        "this test assumes financial-services ships no entity-projections.yaml"
    )
    result = validate_entity_projections(verbose=False)
    assert result.success, result.messages
    assert any("financial-services" in m and "no entity-projections.yaml" in m
               for m in result.messages)


# ── template.ttl guard ───────────────────────────────────────────────────────

def test_template_guard_rejects_owl_thing_declaration() -> None:
    ttl = (
        ":hasThing a owl:ObjectProperty ;\n"
        "    rdfs:domain :Booking ;\n"
        "    rdfs:range owl:Thing .\n"
    )
    errors = validate_pattern_template(ttl)
    assert any("owl:Thing" in e for e in errors)


def test_template_guard_ignores_owl_thing_in_comments() -> None:
    ttl = (
        "# NEVER use rdfs:range owl:Thing here.\n"
        ":hasThing a owl:ObjectProperty ;\n"
        "    rdfs:domain :Booking ;\n"
        "    rdfs:range :Target .\n"
    )
    assert not validate_pattern_template(ttl)


def test_template_guard_requires_domain_on_every_property() -> None:
    ttl = (
        ":hasThing a owl:ObjectProperty ;\n"
        "    rdfs:range :Target .\n"
    )
    errors = validate_pattern_template(ttl)
    assert any("rdfs:domain" in e for e in errors)


def test_template_guard_treats_rdfs_domain_in_comment_as_absent() -> None:
    """rdfs:domain mentioned inside an rdfs:comment must not count as a declaration.

    Regression test for gh#69: the REUSABLE marker phrase "no rdfs:domain by
    design" contains the token ``rdfs:domain``, which caused RDFS_DOMAIN_RE to
    match on the comment text — making the domainless branch unreachable and
    silently passing properties that have no real rdfs:domain triple.
    """
    ttl = (
        ":hasRole a owl:ObjectProperty ;\n"
        '    rdfs:comment """REUSABLE — no rdfs:domain by design.""" ;\n'
        "    rdfs:range :RoleCode .\n"
    )
    errors = validate_pattern_template(ttl)
    assert any("rdfs:domain" in e for e in errors), (
        "rdfs:domain in a comment was counted as a real declaration (gh#69)"
    )
