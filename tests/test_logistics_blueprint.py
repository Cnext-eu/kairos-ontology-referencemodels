# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Tests for the Logistics Blueprint validation foundation."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from rdflib import Graph, Literal, RDFS, URIRef

from scripts.generate_logistics_contract import generate_contract
from scripts.generate_logistics_inventory import (
    DEFAULT_ACCELERATOR,
    DEFAULT_CATALOG,
    build_inventory,
    check_inventory,
    generate_inventory,
)
from scripts.logistics_blueprint_common import (
    BlueprintError,
    _literal_values,
    dump_yaml,
    load_import_closure,
    load_yaml,
    parse_rdf_document,
)
from scripts.validate_logistics_blueprint import (
    DEFAULT_SCHEMA_DIR,
    LOGISTICS_CURRENT,
    BlueprintPaths,
    BlueprintValidationError,
    validate_documents,
)

EX = "https://example.test/logistics#"
VERSION = "1.5.0"


def test_literal_values_normalise_platform_line_endings() -> None:
    graph = Graph()
    subject = URIRef(f"{EX}Party")
    graph.add((subject, RDFS.comment, Literal("first\r\nsecond\rthird")))

    assert _literal_values(graph, subject, RDFS.comment) == ["first\nsecond\nthird"]


def _write_rdf_fixture(root: Path) -> tuple[Path, Path]:
    accelerator = root / "accelerator.ttl"
    module_a = root / "module-a.ttl"
    module_b = root / "module-b.ttl"
    catalog = root / "catalog.xml"
    accelerator.write_text(
        f"""@prefix owl: <http://www.w3.org/2002/07/owl#> .
<https://example.test/accelerator> a owl:Ontology ;
  owl:versionInfo "{VERSION}" ;
  owl:imports <https://example.test/module-a> .
""",
        encoding="utf-8",
    )
    module_a.write_text(
        f"""@prefix ex: <{EX}> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<https://example.test/module-a> a owl:Ontology ;
  dcterms:source "Example standard A" ;
  owl:imports <https://example.test/module-b> .
ex:Party a owl:Class ;
  rdfs:label "Party" ;
  rdfs:comment "A party identity." ;
  rdfs:subClassOf ex:Entity ;
  dcterms:bibliographicCitation "A section 1" .
ex:Entity a owl:Class ;
  rdfs:label "Entity" ;
  rdfs:comment "A superclass for identified things." .
ex:relatedTo a owl:ObjectProperty ;
  rdfs:label "related to" ;
  rdfs:domain ex:Entity ;
  rdfs:range ex:Location .
ex:partyCode a owl:DatatypeProperty ;
  rdfs:label "party code" ;
  rdfs:domain ex:Entity ;
  rdfs:range <http://www.w3.org/2001/XMLSchema#string> .
ex:locationCode a owl:DatatypeProperty ;
  rdfs:label "location code" ;
  rdfs:domain ex:Location ;
  rdfs:range <http://www.w3.org/2001/XMLSchema#string> .
ex:objectCode a owl:ObjectProperty ;
  rdfs:label "object code" ;
  rdfs:domain ex:Party ;
  rdfs:range ex:Location .
ex:wrongWay a owl:ObjectProperty ;
  rdfs:label "wrong way" ;
  rdfs:domain ex:Location ;
  rdfs:range ex:Party .
ex:notARelationship a owl:DatatypeProperty ;
  rdfs:label "not a relationship" ;
  rdfs:domain ex:Party ;
  rdfs:range <http://www.w3.org/2001/XMLSchema#string> .
ex:dualKind a owl:ObjectProperty, owl:DatatypeProperty ;
  rdfs:label "dual kind" .
""",
        encoding="utf-8",
    )
    module_b.write_text(
        f"""@prefix ex: <{EX}> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<https://example.test/module-b> a owl:Ontology ;
  dcterms:source "Example standard B" .
ex:Location a owl:Class ;
  rdfs:label "Location" ;
  rdfs:comment "A physical place." .
""",
        encoding="utf-8",
    )
    catalog.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
  <uri name="https://example.test/module-a" uri="module-a.ttl"/>
  <uri name="https://example.test/module-b" uri="module-b.ttl"/>
</catalog>
""",
        encoding="utf-8",
    )
    return accelerator, catalog


def _documents() -> dict:
    evidence = ["Example standards review"]
    return {
        "canonical": {
            "format_version": "1.0",
            "accelerator_version": VERSION,
            "concepts": [
                {
                    "id": "party",
                    "class_uri": f"{EX}Party",
                    "authority": "Example A",
                    "grain": "One party identity",
                    "identity": "Authority-assigned party identity",
                    "lifecycle": "Creation through retirement",
                    "disposition": "approved",
                    "evidence": evidence,
                    "evidence_basis": "standard",
                    "confidence": "high",
                    "maturity": "preview",
                    "first_slice": True,
                    "standards": ["Example A"],
                },
                {
                    "id": "location",
                    "class_uri": f"{EX}Location",
                    "authority": "Example B",
                    "grain": "One physical place",
                    "identity": "Stable place identity",
                    "lifecycle": "Creation through retirement",
                    "disposition": "approved",
                    "evidence": evidence,
                    "evidence_basis": "standard",
                    "confidence": "high",
                    "maturity": "preview",
                    "first_slice": True,
                    "standards": ["Example B"],
                },
            ],
        },
        "overlap": {
            "format_version": "1.0",
            "accelerator_version": VERSION,
            "entries": [
                {
                    "id": "party-authority",
                    "concept_id": "party",
                    "class_uris": [f"{EX}Party"],
                    "disposition": "canonical_authority",
                    "rationale": "Example A owns the grain.",
                    "evidence": evidence,
                    "confidence": "high",
                    "maturity": "preview",
                    "first_slice": True,
                }
            ],
        },
        "relationships": {
            "format_version": "1.0",
            "accelerator_version": VERSION,
            "relationships": [
                {
                    "id": "party-location",
                    "property_uri": f"{EX}relatedTo",
                    "domain_concept": "party",
                    "range_concept": "location",
                    "direction": "forward",
                    "cardinality": "0..n",
                    "temporal_semantics": "Current relationship",
                    "disposition": "approved",
                    "evidence": evidence,
                    "confidence": "high",
                    "maturity": "preview",
                    "first_slice": True,
                }
            ],
        },
        "capabilities": {
            "format_version": "1.0",
            "accelerator_version": VERSION,
            "capabilities": [
                {
                    "id": "party-management",
                    "status": "supported",
                    "concept_ids": ["party", "location"],
                    "extension_points": [],
                    "evidence": evidence,
                    "confidence": "high",
                    "maturity": "preview",
                }
            ],
        },
        "profile": {
            "format_version": "1.0",
            "accelerator_version": VERSION,
            "profile_version": "0.1.0",
            "contract_version": "0.1.0",
            "maturity": "preview",
            "supported_adapters": ["fabric", "databricks"],
            "entities": [
                {
                    "concept_id": "party",
                    "physical_name": "party",
                    "natural_key_properties": [f"{EX}partyCode"],
                    "required_properties": [f"{EX}partyCode"],
                    "optional_properties": [],
                    "scd_policy": "type1",
                    "reference_data": False,
                },
                {
                    "concept_id": "location",
                    "physical_name": "location",
                    "natural_key_properties": [],
                    "required_properties": [],
                    "optional_properties": [],
                    "scd_policy": "type1",
                    "reference_data": False,
                },
            ],
        },
    }


def _fixture_paths(tmp_path: Path) -> tuple[BlueprintPaths, dict]:
    accelerator, catalog = _write_rdf_fixture(tmp_path)
    inventory = tmp_path / "inventory.yaml"
    generate_inventory(accelerator, catalog, inventory)
    documents = _documents()
    files = {}
    for name, document in documents.items():
        files[name] = tmp_path / f"{name}.yaml"
        dump_yaml(document, files[name])
    return (
        BlueprintPaths(
            inventory=inventory,
            canonical=files["canonical"],
            overlap=files["overlap"],
            relationships=files["relationships"],
            capabilities=files["capabilities"],
            profile=files["profile"],
            schema_dir=DEFAULT_SCHEMA_DIR,
        ),
        documents,
    )


def _replace(paths: BlueprintPaths, name: str, document: dict) -> BlueprintPaths:
    path = getattr(paths, name)
    dump_yaml(document, path)
    return paths


def test_inventory_follows_local_imports_and_is_deterministic(tmp_path: Path) -> None:
    accelerator, catalog = _write_rdf_fixture(tmp_path)
    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"

    inventory = generate_inventory(accelerator, catalog, first)
    generate_inventory(accelerator, catalog, second)

    assert first.read_bytes() == second.read_bytes()
    assert [item["ontology_uri"] for item in inventory["modules"]] == [
        "https://example.test/accelerator",
        "https://example.test/module-a",
        "https://example.test/module-b",
    ]
    party = next(item for item in inventory["records"] if item["uri"] == f"{EX}Party")
    assert party["sources"] == ["Example standard A"]
    assert party["citations"] == ["A section 1"]
    assert {
        item["kind"] for item in inventory["records"] if item["uri"] == f"{EX}dualKind"
    } == {"datatype_property", "object_property"}


def test_inventory_check_detects_fresh_and_stale_content(tmp_path: Path) -> None:
    accelerator, catalog = _write_rdf_fixture(tmp_path)
    output = tmp_path / "inventory.yaml"
    generate_inventory(accelerator, catalog, output)

    assert check_inventory(accelerator, catalog, output)

    inventory = load_yaml(output)
    inventory["records"].pop()
    dump_yaml(inventory, output)
    assert not check_inventory(accelerator, catalog, output)


def test_real_repository_inventory_is_deterministic_without_artifacts() -> None:
    first = build_inventory(DEFAULT_ACCELERATOR, DEFAULT_CATALOG)
    second = build_inventory(DEFAULT_ACCELERATOR, DEFAULT_CATALOG)
    committed = load_yaml(
        LOGISTICS_CURRENT / "blueprint" / "evidence" / "class-inventory.yaml"
    )

    assert first == second
    assert committed == first
    expected_version = (DEFAULT_ACCELERATOR.parents[1] / "VERSION").read_text(
        encoding="utf-8"
    ).strip()
    assert first["accelerator_version"] == expected_version
    # 74 standards-derived modules + blueprint/transport-order, the pack's only
    # non-standards-derived import. Was 67 until the RAIL (TAF TSI) mode specialisation
    # added `ont/rail` and its six submodules to the accelerator's imports; the committed
    # inventory was not regenerated at the time, so this assertion caught the drift.
    # Was 74 until gh#97 extracted the dangerous-goods terms out of the MMT root
    # namespace into a routable `mmt/dangerous-goods` leaf module (MMT 3.0.0).
    assert len(first["modules"]) == 75
    assert len(first["records"]) > 1_000


def test_committed_convergence_registries_are_valid_but_not_approved(tmp_path: Path) -> None:
    blueprint = LOGISTICS_CURRENT / "blueprint"
    documents = validate_documents(
        BlueprintPaths(
            inventory=blueprint / "evidence" / "class-inventory.yaml",
            canonical=blueprint / "canonical-class-registry.yaml",
            overlap=blueprint / "overlap-register.yaml",
            relationships=blueprint / "relationship-registry.yaml",
            capabilities=blueprint / "capability-coverage.yaml",
            profile=None,
            contract=None,
        )
    )

    assert documents["canonical"]["concepts"]
    assert all(
        concept["disposition"] == "unresolved" and not concept["first_slice"]
        for concept in documents["canonical"]["concepts"]
    )
    overlap_dispositions = {
        entry["id"]: entry["disposition"] for entry in documents["overlap"]["entries"]
    }
    assert overlap_dispositions["party-role-parents"] == "reference_model_gap"
    assert all(
        entry["disposition"] == "unresolved"
        for entry in documents["overlap"]["entries"]
        if entry["id"] != "party-role-parents"
    )
    assert all(not entry["first_slice"] for entry in documents["overlap"]["entries"])
    assert documents["relationships"]["relationships"] == []
    assert all(
        capability["status"] == "deferred"
        for capability in documents["capabilities"]["capabilities"]
    )
    assert "profile" not in documents


def test_synthetic_source_shapes_are_schema_valid_and_have_complete_keys() -> None:
    blueprint = LOGISTICS_CURRENT / "blueprint"
    schema = json.loads(
        (blueprint / "_schema" / "source-shape.schema.json").read_text(encoding="utf-8")
    )
    shape_paths = sorted((blueprint / "evidence" / "source-shapes").glob("*.yaml"))

    assert [path.stem for path in shape_paths] == ["carrier-terminal", "freight-forwarder"]
    for path in shape_paths:
        shape = load_yaml(path)
        Draft202012Validator(schema).validate(shape)
        table_names: set[str] = set()
        for system in shape["systems"]:
            for table in system["tables"]:
                assert table["name"] not in table_names
                table_names.add(table["name"])
                assert set(table["primary_key"]) <= set(table["columns"])


def test_committed_attestations_are_schema_valid_and_source_neutral() -> None:
    blueprint = LOGISTICS_CURRENT / "blueprint"
    schema = json.loads(
        (blueprint / "_schema" / "attestation.schema.json").read_text(encoding="utf-8")
    )
    attestation_paths = sorted((blueprint / "evidence" / "attestations").glob("*.yaml"))

    assert [path.stem for path in attestation_paths] == ["att-001"]
    forbidden_terms = ("cldn", "client", "customer")
    for path in attestation_paths:
        attestation = load_yaml(path)
        Draft202012Validator(schema).validate(attestation)
        assert attestation["id"] == path.stem

        raw = path.read_text(encoding="utf-8").lower()
        for term in forbidden_terms:
            assert term not in raw, f"{path.name} is not source-neutral: found {term!r}"


def test_valid_registry_and_contract_flow_is_deterministic(tmp_path: Path) -> None:
    paths, _ = _fixture_paths(tmp_path)
    first = tmp_path / "contract-one.yaml"
    second = tmp_path / "contract-two.yaml"

    contract = generate_contract(paths, first)
    generate_contract(paths, second)
    validate_documents(
        BlueprintPaths(**{**paths.__dict__, "contract": first})
    )

    assert first.read_bytes() == second.read_bytes()
    assert [entity["concept_id"] for entity in contract["entities"]] == [
        "location",
        "party",
    ]
    assert contract["relationships"][0]["id"] == "party-location"
    assert contract["relationships"][0]["maturity"] == "preview"


def test_unknown_class_uri_is_rejected(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    canonical = copy.deepcopy(documents["canonical"])
    canonical["concepts"][0]["class_uri"] = f"{EX}Unknown"
    _replace(paths, "canonical", canonical)

    with pytest.raises(BlueprintValidationError, match="unknown class URI"):
        validate_documents(paths)


def test_approved_concept_with_implementation_evidence_basis_is_rejected(
    tmp_path: Path,
) -> None:
    paths, documents = _fixture_paths(tmp_path)
    canonical = copy.deepcopy(documents["canonical"])
    canonical["concepts"][0]["evidence_basis"] = "implementation"
    _replace(paths, "canonical", canonical)

    with pytest.raises(
        BlueprintValidationError,
        match="disposition is approved but evidence_basis is implementation",
    ):
        validate_documents(paths)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("id", "duplicate concept IDs"),
        ("grain", "duplicate canonical grains"),
    ],
)
def test_duplicate_canonical_identity_is_rejected(
    tmp_path: Path, field: str, expected: str
) -> None:
    paths, documents = _fixture_paths(tmp_path)
    canonical = copy.deepcopy(documents["canonical"])
    canonical["concepts"][1][field] = canonical["concepts"][0][field]
    _replace(paths, "canonical", canonical)

    with pytest.raises(BlueprintValidationError, match=expected):
        validate_documents(paths)


def test_unresolved_first_slice_overlap_is_rejected(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    overlap = copy.deepcopy(documents["overlap"])
    overlap["entries"][0]["disposition"] = "unresolved"
    _replace(paths, "overlap", overlap)

    with pytest.raises(BlueprintValidationError, match="first-slice overlap is unresolved"):
        validate_documents(paths)


@pytest.mark.parametrize("registry", ["canonical", "overlap"])
def test_profile_requires_first_slice_approval(tmp_path: Path, registry: str) -> None:
    paths, documents = _fixture_paths(tmp_path)
    changed = copy.deepcopy(documents[registry])
    rows = changed["concepts"] if registry == "canonical" else changed["entries"]
    rows[0]["first_slice"] = False
    _replace(paths, registry, changed)

    with pytest.raises(BlueprintValidationError, match="not .*first slice"):
        validate_documents(paths)


def test_profile_rejects_selected_relationship_outside_first_slice(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    relationships = copy.deepcopy(documents["relationships"])
    relationships["relationships"][0]["first_slice"] = False
    _replace(paths, "relationships", relationships)

    with pytest.raises(BlueprintValidationError, match="relationship .* not approved"):
        validate_documents(paths)


def test_invalid_relationship_endpoint_is_rejected(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    relationships = copy.deepcopy(documents["relationships"])
    relationships["relationships"][0]["range_concept"] = "missing"
    _replace(paths, "relationships", relationships)

    with pytest.raises(BlueprintValidationError, match="invalid range_concept missing"):
        validate_documents(paths)


def test_relationship_requires_object_property(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    relationships = copy.deepcopy(documents["relationships"])
    relationships["relationships"][0]["property_uri"] = f"{EX}notARelationship"
    _replace(paths, "relationships", relationships)

    with pytest.raises(BlueprintValidationError, match="must be an owl:ObjectProperty"):
        validate_documents(paths)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("domain_concept", "property domain"),
        ("range_concept", "property range"),
    ],
)
def test_relationship_rdf_endpoints_must_match_canonical_classes(
    tmp_path: Path, field: str, expected: str
) -> None:
    paths, documents = _fixture_paths(tmp_path)
    relationships = copy.deepcopy(documents["relationships"])
    relationships["relationships"][0]["property_uri"] = f"{EX}wrongWay"
    if field == "domain_concept":
        relationships["relationships"][0]["range_concept"] = "party"
    else:
        relationships["relationships"][0]["domain_concept"] = "location"
    _replace(paths, "relationships", relationships)

    with pytest.raises(BlueprintValidationError, match=expected):
        validate_documents(paths)


@pytest.mark.parametrize(
    "field", ["natural_key_properties", "required_properties", "optional_properties"]
)
def test_profile_properties_require_datatype_properties(tmp_path: Path, field: str) -> None:
    paths, documents = _fixture_paths(tmp_path)
    profile = copy.deepcopy(documents["profile"])
    party = profile["entities"][0]
    party[field] = [f"{EX}objectCode"]
    if field == "natural_key_properties":
        party["required_properties"] = [f"{EX}objectCode"]
    _replace(paths, "profile", profile)

    with pytest.raises(BlueprintValidationError, match="must be an owl:DatatypeProperty"):
        validate_documents(paths)


def test_profile_property_domain_must_match_canonical_class(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    profile = copy.deepcopy(documents["profile"])
    profile["entities"][0]["optional_properties"] = [f"{EX}locationCode"]
    _replace(paths, "profile", profile)

    with pytest.raises(BlueprintValidationError, match="property domain"):
        validate_documents(paths)


def test_natural_keys_must_be_required(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    profile = copy.deepcopy(documents["profile"])
    profile["entities"][0]["required_properties"] = []
    _replace(paths, "profile", profile)

    with pytest.raises(BlueprintValidationError, match="must be a subset"):
        validate_documents(paths)


def test_natural_keys_cannot_be_optional(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    profile = copy.deepcopy(documents["profile"])
    profile["entities"][0]["optional_properties"] = [f"{EX}partyCode"]
    _replace(paths, "profile", profile)

    with pytest.raises(BlueprintValidationError, match="cannot be optional"):
        validate_documents(paths)


@pytest.mark.parametrize(
    ("document_name", "collection", "expected"),
    [
        ("overlap", "entries", "overlap: duplicate IDs"),
        ("relationships", "relationships", "relationships: duplicate IDs"),
        ("capabilities", "capabilities", "capabilities: duplicate IDs"),
    ],
)
def test_registry_ids_are_case_normalized_unique(
    tmp_path: Path, document_name: str, collection: str, expected: str
) -> None:
    paths, documents = _fixture_paths(tmp_path)
    document = copy.deepcopy(documents[document_name])
    document[collection].append(copy.deepcopy(document[collection][0]))
    _replace(paths, document_name, document)

    with pytest.raises(BlueprintValidationError, match=expected):
        validate_documents(paths)


def test_profile_reference_to_deferred_class_is_rejected(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    canonical = copy.deepcopy(documents["canonical"])
    canonical["concepts"][1]["disposition"] = "deferred"
    _replace(paths, "canonical", canonical)

    with pytest.raises(BlueprintValidationError, match="class is deferred, not approved"):
        validate_documents(paths)


def test_accelerator_version_mismatch_is_rejected(tmp_path: Path) -> None:
    paths, documents = _fixture_paths(tmp_path)
    profile = copy.deepcopy(documents["profile"])
    profile["accelerator_version"] = "9.9.9"
    _replace(paths, "profile", profile)

    with pytest.raises(BlueprintValidationError, match="accelerator version mismatch"):
        validate_documents(paths)


@pytest.mark.parametrize("field", ["accelerator_version", "profile_version", "contract_version"])
def test_profile_versions_must_be_semver(tmp_path: Path, field: str) -> None:
    paths, documents = _fixture_paths(tmp_path)
    profile = copy.deepcopy(documents["profile"])
    profile[field] = "version-one"
    _replace(paths, "profile", profile)

    with pytest.raises(BlueprintValidationError, match=field):
        validate_documents(paths)


@pytest.mark.parametrize("registry", ["concept", "relationship"])
def test_profile_cannot_overstate_selected_maturity(tmp_path: Path, registry: str) -> None:
    paths, documents = _fixture_paths(tmp_path)
    profile = copy.deepcopy(documents["profile"])
    profile["maturity"] = "stable"
    if registry == "concept":
        relationships = copy.deepcopy(documents["relationships"])
        relationships["relationships"][0]["maturity"] = "stable"
        _replace(paths, "relationships", relationships)
    else:
        canonical = copy.deepcopy(documents["canonical"])
        for concept in canonical["concepts"]:
            concept["maturity"] = "stable"
        _replace(paths, "canonical", canonical)
    _replace(paths, "profile", profile)

    with pytest.raises(BlueprintValidationError, match=f"overstates {registry}"):
        validate_documents(paths)


def test_rdf_document_requires_exactly_one_ontology(tmp_path: Path) -> None:
    source = tmp_path / "multiple.ttl"
    source.write_text(
        """@prefix owl: <http://www.w3.org/2002/07/owl#> .
<https://example.test/one> a owl:Ontology .
<https://example.test/two> a owl:Ontology .
""",
        encoding="utf-8",
    )

    with pytest.raises(BlueprintError, match="exactly one"):
        parse_rdf_document(source)


def test_import_uri_must_match_declared_ontology_uri(tmp_path: Path) -> None:
    accelerator, catalog = _write_rdf_fixture(tmp_path)
    module_a = tmp_path / "module-a.ttl"
    module_a.write_text(
        module_a.read_text(encoding="utf-8").replace(
            "<https://example.test/module-a> a owl:Ontology",
            "<https://example.test/not-module-a> a owl:Ontology",
        ),
        encoding="utf-8",
    )

    with pytest.raises(BlueprintError, match="which declares"):
        load_import_closure(accelerator, catalog)


def test_dump_yaml_cleans_up_temporary_file_after_replace_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "output.yaml"

    def fail_replace(source: os.PathLike[str], target: os.PathLike[str]) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(BlueprintError, match="Cannot write YAML"):
        dump_yaml({"value": 1}, destination)

    assert list(tmp_path.iterdir()) == []


def test_invalid_json_schema_is_a_blueprint_validation_error(tmp_path: Path) -> None:
    paths, _ = _fixture_paths(tmp_path)
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    for source in DEFAULT_SCHEMA_DIR.glob("*.json"):
        (schema_dir / source.name).write_bytes(source.read_bytes())
    invalid_schema = schema_dir / "inventory.schema.json"
    schema = json.loads(invalid_schema.read_text(encoding="utf-8"))
    schema["type"] = 7
    invalid_schema.write_text(json.dumps(schema), encoding="utf-8")
    paths = BlueprintPaths(**{**paths.__dict__, "schema_dir": schema_dir})

    with pytest.raises(BlueprintValidationError, match="Invalid inventory JSON Schema"):
        validate_documents(paths)


def test_yaml_loader_rejects_python_objects(tmp_path: Path) -> None:
    unsafe = tmp_path / "unsafe.yaml"
    unsafe.write_text("!!python/object:builtins.object {}\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Invalid YAML"):
        load_yaml(unsafe)
