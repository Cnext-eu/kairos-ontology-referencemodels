# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Validate Logistics Blueprint registries, inventory, profile, and generated contract."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

if __package__:
    from .logistics_blueprint_common import BlueprintError, load_json, load_yaml, require_file
else:
    from logistics_blueprint_common import BlueprintError, load_json, load_yaml, require_file

REPO_ROOT = Path(__file__).resolve().parents[1]
LOGISTICS_CURRENT = (
    REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models" / "accelerator-packs" / "logistics" / "current"
)
DEFAULT_SCHEMA_DIR = LOGISTICS_CURRENT / "blueprint" / "_schema"


class BlueprintValidationError(BlueprintError):
    """Raised when one or more blueprint semantic checks fail."""


@dataclass(frozen=True)
class BlueprintPaths:
    inventory: Path
    canonical: Path
    overlap: Path
    relationships: Path
    capabilities: Path
    profile: Path | None
    contract: Path | None = None
    schema_dir: Path = DEFAULT_SCHEMA_DIR


SCHEMAS = {
    "inventory": "inventory.schema.json",
    "canonical": "canonical-registry.schema.json",
    "overlap": "overlap-register.schema.json",
    "relationships": "relationship-registry.schema.json",
    "capabilities": "capability-coverage.schema.json",
    "profile": "profile-input.schema.json",
    "contract": "generated-contract.schema.json",
}
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
MATURITY_ORDER = {"experimental": 0, "preview": 1, "stable": 2}


def _schema_errors(document: Any, schema: Any, name: str) -> list[str]:
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
    except SchemaError as exc:
        raise BlueprintValidationError(f"Invalid {name} JSON Schema: {exc.message}") from exc
    errors = []
    for error in sorted(
        validator.iter_errors(document), key=lambda item: tuple(str(part) for part in item.path)
    ):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{name}:{location}: {error.message}")
    return errors


def _load_documents(paths: BlueprintPaths) -> tuple[dict[str, Any], list[str]]:
    documents: dict[str, Any] = {
        "inventory": load_yaml(paths.inventory),
        "canonical": load_yaml(paths.canonical),
        "overlap": load_yaml(paths.overlap),
        "relationships": load_yaml(paths.relationships),
        "capabilities": load_yaml(paths.capabilities),
    }
    if paths.profile is not None:
        documents["profile"] = load_yaml(paths.profile)
    if paths.contract is not None:
        if paths.profile is None:
            raise BlueprintValidationError(
                "Cannot validate a generated contract without its source profile"
            )
        documents["contract"] = load_yaml(paths.contract)

    errors: list[str] = []
    for name, document in documents.items():
        schema_path = require_file(paths.schema_dir / SCHEMAS[name], f"{name} JSON Schema")
        errors.extend(_schema_errors(document, load_json(schema_path), name))
    return documents, errors


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        key = value.strip().casefold()
        if key in seen:
            duplicates.add(value)
        seen.add(key)
    return sorted(duplicates)


def _records_by_key(
    records: list[dict[str, Any]],
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Index inventory records without collapsing URI/kind or module provenance."""
    indexed: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        indexed.setdefault((record["uri"], record["kind"]), []).append(record)
    return indexed


def _record_values(
    records_by_key: dict[tuple[str, str], list[dict[str, Any]]],
    uri: str,
    kind: str,
    field: str,
) -> set[str]:
    return {
        value
        for record in records_by_key.get((uri, kind), [])
        for value in record.get(field, [])
    }


def _is_class_compatible(
    actual_class: str,
    declared_class: str,
    records_by_key: dict[tuple[str, str], list[dict[str, Any]]],
) -> bool:
    """Return whether an actual endpoint is the declared class or one of its subclasses."""
    pending = [actual_class]
    visited: set[str] = set()
    while pending:
        candidate = pending.pop()
        if candidate == declared_class:
            return True
        if candidate in visited:
            continue
        visited.add(candidate)
        pending.extend(
            _record_values(records_by_key, candidate, "class", "superclasses") - visited
        )
    return False


def _validate_property_domain(
    errors: list[str],
    records_by_key: dict[tuple[str, str], list[dict[str, Any]]],
    context: str,
    property_uri: str,
    kind: str,
    actual_class: str,
) -> None:
    for declared_domain in sorted(
        _record_values(records_by_key, property_uri, kind, "domains")
    ):
        if not _is_class_compatible(actual_class, declared_domain, records_by_key):
            errors.append(
                f"{context}: property domain {declared_domain} is incompatible with "
                f"canonical class {actual_class}"
            )


def validate_documents(paths: BlueprintPaths) -> dict[str, Any]:
    """Validate schemas and cross-document semantics, returning loaded documents."""
    try:
        documents, errors = _load_documents(paths)
    except BlueprintValidationError:
        raise
    except BlueprintError as exc:
        raise BlueprintValidationError(f"Cannot validate Logistics Blueprint: {exc}") from exc
    if errors:
        raise BlueprintValidationError(
            "Logistics Blueprint schema validation failed:\n- " + "\n- ".join(errors)
        )

    inventory = documents["inventory"]
    canonical = documents["canonical"]
    overlap = documents["overlap"]
    relationships = documents["relationships"]
    capabilities = documents["capabilities"]
    profile = documents.get("profile")

    records = inventory.get("records", [])
    records_by_key = _records_by_key(records)
    class_uris = {uri for uri, kind in records_by_key if kind == "class"}
    concepts = canonical.get("concepts", [])
    concept_by_id = {item["id"]: item for item in concepts}
    overlap_by_concept: dict[str, list[dict[str, Any]]] = {}
    for entry in overlap.get("entries", []):
        overlap_by_concept.setdefault(entry["concept_id"], []).append(entry)

    duplicate_ids = _duplicates([item["id"] for item in concepts])
    duplicate_grains = _duplicates([item["grain"] for item in concepts])
    if duplicate_ids:
        errors.append(f"canonical: duplicate concept IDs: {', '.join(duplicate_ids)}")
    if duplicate_grains:
        errors.append(f"canonical: duplicate canonical grains: {', '.join(duplicate_grains)}")

    for concept in concepts:
        if concept["class_uri"] not in class_uris:
            errors.append(
                f"canonical:{concept['id']}: unknown class URI {concept['class_uri']}"
            )
        if concept.get("first_slice") and concept["disposition"] == "unresolved":
            errors.append(f"canonical:{concept['id']}: first-slice concept is unresolved")
        if (
            concept["disposition"] == "approved"
            and concept.get("evidence_basis") == "implementation"
        ):
            errors.append(
                f"canonical:{concept['id']}: disposition is approved but evidence_basis is "
                "implementation — implementation evidence may raise, corroborate, or force "
                "re-review of a concept, but cannot by itself authorise disposition: approved"
            )

    for entry in overlap.get("entries", []):
        if entry["concept_id"] not in concept_by_id:
            errors.append(
                f"overlap:{entry['id']}: unknown canonical concept {entry['concept_id']}"
            )
        for uri in entry["class_uris"]:
            if uri not in class_uris:
                errors.append(f"overlap:{entry['id']}: unknown class URI {uri}")
        if entry.get("first_slice") and entry["disposition"] == "unresolved":
            errors.append(f"overlap:{entry['id']}: first-slice overlap is unresolved")
    duplicate_overlap_ids = _duplicates(
        [entry["id"] for entry in overlap.get("entries", [])]
    )
    if duplicate_overlap_ids:
        errors.append(f"overlap: duplicate IDs: {', '.join(duplicate_overlap_ids)}")

    relationship_items = relationships.get("relationships", [])
    duplicate_relationship_ids = _duplicates(
        [relationship["id"] for relationship in relationship_items]
    )
    if duplicate_relationship_ids:
        errors.append(
            f"relationships: duplicate IDs: {', '.join(duplicate_relationship_ids)}"
        )
    for relationship in relationship_items:
        property_uri = relationship["property_uri"]
        if (property_uri, "object_property") not in records_by_key:
            errors.append(
                f"relationships:{relationship['id']}: property must be an owl:ObjectProperty: "
                f"{property_uri}"
            )
        for endpoint, rdf_field in (
            ("domain_concept", "domains"),
            ("range_concept", "ranges"),
        ):
            concept = concept_by_id.get(relationship[endpoint])
            if concept is None:
                errors.append(
                    f"relationships:{relationship['id']}: invalid {endpoint} "
                    f"{relationship[endpoint]}"
                )
            elif (property_uri, "object_property") in records_by_key:
                for declared_class in sorted(
                    _record_values(
                        records_by_key, property_uri, "object_property", rdf_field
                    )
                ):
                    if not _is_class_compatible(
                        concept["class_uri"], declared_class, records_by_key
                    ):
                        errors.append(
                            f"relationships:{relationship['id']}: property {rdf_field[:-1]} "
                            f"{declared_class} is incompatible with canonical {endpoint} class "
                            f"{concept['class_uri']}"
                        )
        if relationship.get("first_slice") and relationship["disposition"] == "unresolved":
            errors.append(
                f"relationships:{relationship['id']}: first-slice relationship is unresolved"
            )

    capability_items = capabilities.get("capabilities", [])
    duplicate_capability_ids = _duplicates(
        [capability["id"] for capability in capability_items]
    )
    if duplicate_capability_ids:
        errors.append(
            f"capabilities: duplicate IDs: {', '.join(duplicate_capability_ids)}"
        )
    for capability in capability_items:
        for concept_id in capability.get("concept_ids", []):
            if concept_id not in concept_by_id:
                errors.append(
                    f"capabilities:{capability['id']}: unknown concept {concept_id}"
                )

    profile_entities = profile.get("entities", []) if profile is not None else []
    duplicate_profile_concepts = _duplicates(
        [entity["concept_id"] for entity in profile_entities]
    )
    duplicate_physical_names = _duplicates(
        [entity["physical_name"] for entity in profile_entities]
    )
    if duplicate_profile_concepts:
        errors.append(
            "profile: duplicate concept references: "
            + ", ".join(duplicate_profile_concepts)
        )
    if duplicate_physical_names:
        errors.append(
            "profile: duplicate physical names: " + ", ".join(duplicate_physical_names)
        )
    for entity in profile_entities:
        concept = concept_by_id.get(entity["concept_id"])
        if concept is None:
            errors.append(f"profile: unknown concept {entity['concept_id']}")
            continue
        if concept["disposition"] != "approved":
            errors.append(
                f"profile:{entity['concept_id']}: class is {concept['disposition']}, not approved"
            )
        elif not concept["first_slice"]:
            errors.append(
                f"profile:{entity['concept_id']}: canonical concept is not approved "
                "for the first slice"
            )
        for entry in overlap_by_concept.get(entity["concept_id"], []):
            if not entry["first_slice"] or entry["disposition"] in {
                "deferred",
                "reference_model_gap",
                "unresolved",
            }:
                errors.append(
                    f"profile:{entity['concept_id']}: overlap {entry['id']} is not "
                    "resolved for the first slice"
                )
        natural_keys = set(entity["natural_key_properties"])
        required_properties = set(entity["required_properties"])
        optional_properties = set(entity["optional_properties"])
        missing_required_keys = natural_keys - required_properties
        if missing_required_keys:
            errors.append(
                f"profile:{entity['concept_id']}: natural_key_properties must be a subset "
                f"of required_properties: {', '.join(sorted(missing_required_keys))}"
            )
        optional_keys = natural_keys & optional_properties
        if optional_keys:
            errors.append(
                f"profile:{entity['concept_id']}: natural_key_properties cannot be optional: "
                f"{', '.join(sorted(optional_keys))}"
            )
        for field in ("natural_key_properties", "required_properties", "optional_properties"):
            for uri in entity.get(field, []):
                if (uri, "datatype_property") not in records_by_key:
                    errors.append(
                        f"profile:{entity['concept_id']}:{field}: property must be an "
                        f"owl:DatatypeProperty: {uri}"
                    )
        for uri in sorted(natural_keys | required_properties | optional_properties):
            if (uri, "datatype_property") in records_by_key:
                _validate_property_domain(
                    errors,
                    records_by_key,
                    f"profile:{entity['concept_id']}:{uri}",
                    uri,
                    "datatype_property",
                    concept["class_uri"],
                )
        overlap_properties = required_properties & optional_properties
        if overlap_properties:
            errors.append(
                f"profile:{entity['concept_id']}: properties cannot be both required and "
                f"optional: {', '.join(sorted(overlap_properties))}"
            )

    for name, document in documents.items():
        for field in ("accelerator_version", "profile_version", "contract_version"):
            version = document.get(field)
            if version is not None and SEMVER_PATTERN.fullmatch(version) is None:
                errors.append(f"{name}:{field}: version must be valid SemVer: {version}")

    versions = {
        name: document.get("accelerator_version")
        for name, document in documents.items()
        if "accelerator_version" in document
    }
    distinct_versions = {version for version in versions.values() if version is not None}
    if len(distinct_versions) > 1:
        detail = ", ".join(f"{name}={version}" for name, version in sorted(versions.items()))
        errors.append(f"accelerator version mismatch: {detail}")

    profile_maturity = profile["maturity"] if profile is not None else None
    selected_concepts = {
        entity["concept_id"] for entity in profile_entities if entity["concept_id"] in concept_by_id
    }
    for concept_id in sorted(selected_concepts):
        concept_maturity = concept_by_id[concept_id]["maturity"]
        if (
            profile_maturity is not None
            and MATURITY_ORDER[profile_maturity] > MATURITY_ORDER[concept_maturity]
        ):
            errors.append(
                f"profile: maturity {profile_maturity} overstates concept {concept_id} "
                f"maturity {concept_maturity}"
            )
    for relationship in relationship_items:
        if (
            relationship["disposition"] == "approved"
            and relationship["domain_concept"] in selected_concepts
            and relationship["range_concept"] in selected_concepts
            and not relationship["first_slice"]
        ):
            errors.append(
                f"profile: relationship {relationship['id']} is not approved "
                "for the first slice"
            )
        if (
            relationship["disposition"] == "approved"
            and relationship["domain_concept"] in selected_concepts
            and relationship["range_concept"] in selected_concepts
            and profile_maturity is not None
            and MATURITY_ORDER[profile_maturity] > MATURITY_ORDER[relationship["maturity"]]
        ):
            errors.append(
                f"profile: maturity {profile_maturity} overstates relationship "
                f"{relationship['id']} maturity {relationship['maturity']}"
            )

    if "contract" in documents and not errors:
        if __package__:
            from .generate_logistics_contract import derive_contract
        else:
            from generate_logistics_contract import derive_contract

        expected_contract = derive_contract(documents)
        if documents["contract"] != expected_contract:
            errors.append(
                "contract: content differs from the deterministic profile/registry derivation"
            )

    if errors:
        raise BlueprintValidationError(
            "Logistics Blueprint validation failed:\n- " + "\n- ".join(errors)
        )
    return documents


def build_parser() -> argparse.ArgumentParser:
    blueprint = LOGISTICS_CURRENT / "blueprint"
    parser = argparse.ArgumentParser(description=__doc__)
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
        default=None,
        help=(
            "Single YAML physical-profile source intended to derive future TTL and contract; "
            "generated outputs are not duplicate authority. If omitted, the default profile "
            "is validated when present; otherwise registry-only validation runs."
        ),
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=None,
        help=(
            "Generated contract to validate. If omitted, the default contract is validated "
            "when present."
        ),
    )
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    default_profile = LOGISTICS_CURRENT / "profiles" / "silver-starter" / "profile.yaml"
    default_contract = (
        LOGISTICS_CURRENT / "contracts" / "generated" / "logistics-silver-contract.yaml"
    )
    profile = args.profile
    if profile is None and default_profile.exists():
        profile = default_profile
    contract = args.contract
    if contract is None and default_contract.exists():
        contract = default_contract
    paths = BlueprintPaths(
        inventory=args.inventory,
        canonical=args.canonical,
        overlap=args.overlap,
        relationships=args.relationships,
        capabilities=args.capabilities,
        profile=profile,
        contract=contract,
        schema_dir=args.schema_dir,
    )
    try:
        validate_documents(paths)
    except BlueprintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print("Logistics Blueprint validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
