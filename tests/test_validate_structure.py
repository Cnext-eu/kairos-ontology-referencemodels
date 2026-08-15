# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Focused tests for repository structure classification."""

import json
from pathlib import Path

import pytest
import yaml

from scripts.validate_structure import (
    PATTERN_SCHEMA,
    PATTERNS_DIR,
    find_domain_subfolders,
    pattern_schema_errors,
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
