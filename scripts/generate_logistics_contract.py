# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Generate a deterministic Silver contract from validated registries and a YAML profile."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

if __package__:
    from .logistics_blueprint_common import BlueprintError, dump_yaml
    from .validate_logistics_blueprint import (
        DEFAULT_SCHEMA_DIR,
        LOGISTICS_CURRENT,
        BlueprintPaths,
        validate_documents,
    )
else:
    from logistics_blueprint_common import BlueprintError, dump_yaml
    from validate_logistics_blueprint import (
        DEFAULT_SCHEMA_DIR,
        LOGISTICS_CURRENT,
        BlueprintPaths,
        validate_documents,
    )


def derive_contract(documents: dict[str, Any]) -> dict[str, Any]:
    """Derive a contract without introducing semantic choices not present in inputs."""
    canonical = {
        concept["id"]: concept for concept in documents["canonical"]["concepts"]
    }
    profile = documents["profile"]
    selected = {entity["concept_id"] for entity in profile["entities"]}
    entities = []
    for entity in profile["entities"]:
        concept = canonical[entity["concept_id"]]
        entities.append(
            {
                "applicable_standards": sorted(concept.get("standards", [])),
                "business_grain": concept["grain"],
                "class_uri": concept["class_uri"],
                "concept_id": concept["id"],
                "maturity": concept["maturity"],
                "natural_key_properties": sorted(entity["natural_key_properties"]),
                "optional_properties": sorted(entity["optional_properties"]),
                "physical_name": entity["physical_name"],
                "reference_data": entity["reference_data"],
                "required_properties": sorted(entity["required_properties"]),
                "scd_policy": entity["scd_policy"],
            }
        )
    entities.sort(key=lambda item: item["concept_id"])

    relationships = []
    for relationship in documents["relationships"]["relationships"]:
        if (
            relationship["disposition"] == "approved"
            and relationship["first_slice"]
            and relationship["domain_concept"] in selected
            and relationship["range_concept"] in selected
        ):
            relationships.append(
                {
                    key: relationship[key]
                    for key in (
                        "cardinality",
                        "direction",
                        "domain_concept",
                        "id",
                        "maturity",
                        "property_uri",
                        "range_concept",
                        "temporal_semantics",
                    )
                }
            )
    relationships.sort(key=lambda item: item["id"])
    return {
        "accelerator_version": profile["accelerator_version"],
        "contract_version": profile["contract_version"],
        "entities": entities,
        "format_version": "1.0",
        "maturity": profile["maturity"],
        "profile_version": profile["profile_version"],
        "relationships": relationships,
        "supported_adapters": sorted(profile["supported_adapters"]),
    }


def generate_contract(paths: BlueprintPaths, output: Path) -> dict[str, Any]:
    """Validate source inputs and write their derived contract."""
    if paths.profile is None:
        raise BlueprintError("A source profile is required to generate a contract")
    source_paths = BlueprintPaths(
        inventory=paths.inventory,
        canonical=paths.canonical,
        overlap=paths.overlap,
        relationships=paths.relationships,
        capabilities=paths.capabilities,
        profile=paths.profile,
        schema_dir=paths.schema_dir,
    )
    contract = derive_contract(validate_documents(source_paths))
    dump_yaml(contract, output)
    return contract


def build_parser() -> argparse.ArgumentParser:
    blueprint = LOGISTICS_CURRENT / "blueprint"
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "The YAML profile (profile-input.schema.json) is the single physical-profile "
            "source intended to derive both future TTL and this contract. Canonical grains "
            "and relationships stay in registries; generated outputs never become authority."
        ),
    )
    parser.add_argument(
        "--inventory", type=Path, default=blueprint / "evidence" / "class-inventory.yaml"
    )
    parser.add_argument(
        "--canonical", type=Path, default=blueprint / "canonical-class-registry.yaml"
    )
    parser.add_argument("--overlap", type=Path, default=blueprint / "overlap-register.yaml")
    parser.add_argument(
        "--relationships", type=Path, default=blueprint / "relationship-registry.yaml"
    )
    parser.add_argument(
        "--capabilities", type=Path, default=blueprint / "capability-coverage.yaml"
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=LOGISTICS_CURRENT / "profiles" / "silver-starter" / "profile.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=LOGISTICS_CURRENT / "contracts" / "generated" / "logistics-silver-contract.yaml",
    )
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = BlueprintPaths(
        inventory=args.inventory,
        canonical=args.canonical,
        overlap=args.overlap,
        relationships=args.relationships,
        capabilities=args.capabilities,
        profile=args.profile,
        schema_dir=args.schema_dir,
    )
    try:
        contract = generate_contract(paths, args.output)
    except BlueprintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(contract['entities'])} contract entities to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
