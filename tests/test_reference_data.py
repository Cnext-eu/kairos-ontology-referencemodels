"""Vendored reference data (code lists) carries consistent, machine-readable provenance.

Reference data is refreshed by script rather than released upstream with a version, so the
snapshot date is the version. It is recorded three times — ``METADATA.txt``, the vendor
extract's header and the OWL patch — and a hand edit or a partial regeneration would let
them disagree. A consumer reading the patch must also be able to tell a code-list class is
reference data (``kairos-ext:isReferenceData``) and find where it came from and how to
refresh it, without opening this repository. See VERSIONING.md, "Refreshing reference
data" (gh#120).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS

ONTOLOGY_ROOT = Path(__file__).resolve().parent.parent / "kairos_ontology_referencemodels" / "ontology-reference-models"
KAIROS_EXT = Namespace("https://kairos.cnext.eu/ext#")
UNECE = Namespace("https://vocabulary.uncefact.org/")
UNLCDV = Namespace("https://vocabulary.uncefact.org/unlocode-vocab/")

#: module dir -> (extract file, patch file, patch ontology IRI, code-list classes)
REFERENCE_DATA_MODULES = {
    "UNCEFACT": (
        "UNCEFACT-CodeLists.ttl",
        "UNCEFACT-CodeLists.owl-patch.ttl",
        URIRef("https://www.kairosflow.ai/ont/uncefact/code-lists"),
        [
            UNECE.TransportModeCodeList,
            UNECE.UnitMeasureCode,
            UNECE.PackageTypeCodeList,
            UNECE.DeliveryTermsCodeList,
            UNECE.TransportMovementStageCodeList,
            UNECE.CurrencyCodeList,
            UNECE.PartyRoleCodeList,
            UNLCDV.Country,
            UNLCDV.Subdivision,
            UNLCDV.Function,
        ],
    ),
}


def _metadata(current: Path) -> dict[str, str]:
    lines = (current / "METADATA.txt").read_text(encoding="utf-8").splitlines()
    return dict(line.split(": ", 1) for line in lines if ": " in line and not line.startswith(" "))


@pytest.fixture(scope="module", params=sorted(REFERENCE_DATA_MODULES))
def module(request):
    extract_name, patch_name, patch_iri, classes = REFERENCE_DATA_MODULES[request.param]
    current = ONTOLOGY_ROOT / "authoritative-ontologies" / request.param / "current"
    return {
        "name": request.param,
        "snapshot": _metadata(current)["download_date"],
        "extract": Graph().parse(current / extract_name),
        "patch": Graph().parse(current / patch_name),
        "patch_iri": patch_iri,
        "classes": classes,
    }


def test_snapshot_date_agrees_everywhere(module) -> None:
    snapshot = module["snapshot"]
    patch_version = module["patch"].value(module["patch_iri"], OWL.versionInfo)
    assert str(patch_version) == snapshot, f"{module['name']}: patch owl:versionInfo != METADATA download_date"
    extract_versions = {str(v) for v in module["extract"].objects(None, OWL.versionInfo)}
    assert extract_versions == {f"snapshot {snapshot}"}, f"{module['name']}: extract header != METADATA"


def test_code_list_classes_carry_reference_data_provenance(module) -> None:
    patch, snapshot = module["patch"], module["snapshot"]
    for cls in module["classes"]:
        assert (cls, RDF.type, OWL.Class) in patch, f"{cls} is not typed owl:Class"
        assert patch.value(cls, KAIROS_EXT.isReferenceData) == Literal(True), f"{cls} lacks isReferenceData"
        assert str(patch.value(cls, OWL.versionInfo)) == snapshot, f"{cls} versionInfo != snapshot"
        assert patch.value(cls, DCTERMS.source) is not None, f"{cls} lacks dcterms:source"
        see_also = str(patch.value(cls, RDFS.seeAlso) or "")
        assert see_also.endswith(f"/authoritative-ontologies/{module['name']}/README.md"), (
            f"{cls} rdfs:seeAlso does not point at the module README: {see_also!r}"
        )


def test_hub_loaded_reference_classes_say_where_their_rows_come_from() -> None:
    """unlcdv:UNLOCODE ships without members, so its source and instruction are its whole contract."""
    current = ONTOLOGY_ROOT / "authoritative-ontologies" / "UNCEFACT" / "current"
    extract = Graph().parse(current / "UNCEFACT-CodeLists.ttl")
    patch = Graph().parse(current / "UNCEFACT-CodeLists.owl-patch.ttl")
    cls = UNLCDV.UNLOCODE
    assert (None, RDF.type, cls) not in extract, "UN/LOCODE locations must not be vendored"
    assert patch.value(cls, KAIROS_EXT.isReferenceData) == Literal(True)
    assert str(patch.value(cls, DCTERMS.source)) == "https://vocabulary.uncefact.org/unlocode"
    assert "not vendored" in str(patch.value(cls, DCTERMS.description))


def test_every_code_is_an_owl_individual_with_a_code(module) -> None:
    extract, patch = module["extract"], module["patch"]
    for cls in module["classes"]:
        members = set(extract.subjects(RDF.type, cls))
        assert members, f"{cls} has no members"
        missing_value = [m for m in members if extract.value(m, RDF.value) is None]
        assert not missing_value, f"{cls}: members without rdf:value: {missing_value[:5]}"
        untyped = [m for m in members if (m, RDF.type, OWL.NamedIndividual) not in patch]
        assert not untyped, f"{cls}: members the patch does not type: {untyped[:5]}"
