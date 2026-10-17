#!/usr/bin/env python3
"""Vendor standards-body code lists from the UN/CEFACT web vocabulary (gh#120).

UN/CEFACT publishes its web vocabulary at https://vocabulary.uncefact.org/ as a handful of
unversioned JSON-LD documents (content negotiation on ``Accept: application/ld+json``;
per-term URLs answer 403). Kairos vendors only the code lists named in ``SOURCES``:

* ``bsp`` (the root document, ~8.7 MB — the whole UN/CEFACT trade data model): UNECE
  Rec 19 transport modes, Rec 20 units of measure, Rec 21 package types, Rec 5 Incoterms
  (delivery terms), transport stage, ISO 4217 currencies, and UNTDED 3035 party roles.
* ``unlocode-*``: the UN/LOCODE (UNECE Rec 16) supporting lists — ISO 3166-1 countries,
  ISO 3166-2 subdivisions and location function classifiers — plus the small UN/LOCODE
  vocabulary that declares their classes and properties. The 115,928 locations
  themselves (``/unlocode``, ~39 MB) are not vendored.

Every vendored triple is copied from its dump unchanged, with its original IRI.

Two files are written, mirroring the IATA domains-patch arrangement (gh#93):

* ``UNCEFACT-CodeLists.ttl`` — the vendor extract. Never hand-edit; re-run this script.
* ``UNCEFACT-CodeLists.owl-patch.ttl`` — generated OWL typing the extract lacks
  (``owl:Class``, ``owl:NamedIndividual``, ``rdfs:label``, OWL property types) plus
  provenance. It imports the extract and is the document hubs import, via
  ``https://www.kairosflow.ai/ont/uncefact/code-lists``.

``METADATA.txt`` is regenerated too, so the snapshot date and checksums cannot drift
from the files they describe. A refresh moves the previous snapshot to
``archive/<download date>/`` and regenerates the IATA alignment
(``scripts/generate_uncefact_iata_alignment.py``). Nothing is written when every
upstream dump is byte-identical to the vendored one.

This is reference data: UN/CEFACT revises these lists, so refresh periodically (see
VERSIONING.md, "Refreshing reference data").

Usage:
    python scripts/download_uncefact_codelists.py --check         # has upstream changed? (exit 1 if so)
    python scripts/download_uncefact_codelists.py                 # download and refresh
    python scripts/download_uncefact_codelists.py --from-dir D    # refresh from saved dumps (D/<source id>.jsonld)
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, XSD

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = (
    REPO_ROOT
    / "kairos_ontology_referencemodels"
    / "ontology-reference-models"
    / "authoritative-ontologies"
    / "UNCEFACT"
    / "current"
)
EXTRACT_TTL = TARGET_DIR / "UNCEFACT-CodeLists.ttl"
PATCH_TTL = TARGET_DIR / "UNCEFACT-CodeLists.owl-patch.ttl"
METADATA_TXT = TARGET_DIR / "METADATA.txt"

BASE_URL = "https://vocabulary.uncefact.org/"
UNECE = Namespace(BASE_URL)
UNLCDV = Namespace(BASE_URL + "unlocode-vocab/")
SCHEMA = Namespace("http://schema.org/")

#: The toolkit's extension vocabulary; isReferenceData marks a code-list class (ref_ table).
KAIROS_EXT = Namespace("https://kairos.cnext.eu/ext#")
README_URL = (
    "https://github.com/Cnext-eu/kairos-ontology-referencemodels/blob/main/"
    "kairos_ontology_referencemodels/ontology-reference-models/authoritative-ontologies/UNCEFACT/README.md"
)

PUBLIC_ONTOLOGY_IRI = URIRef("https://www.kairosflow.ai/ont/uncefact/code-lists")
EXTRACT_ONTOLOGY_IRI = URIRef("https://www.kairosflow.ai/ont/uncefact/code-lists-vendor-extract")


@dataclass(frozen=True)
class Source:
    """One upstream JSON-LD document and what Kairos takes from it."""

    id: str
    url: str
    #: Compact class IRI -> what the list is. The class node and every node typed by it are vendored.
    lists: dict[str, str] = field(default_factory=dict)
    #: Vendor every node of the document (a small vocabulary that declares classes/properties).
    whole_document: bool = False


SOURCES = [
    Source("bsp", BASE_URL, {
        "unece:TransportModeCodeList": "UNECE Recommendation No. 19 (Codes for Modes of Transport)",
        "unece:UnitMeasureCode": "UNECE Recommendation No. 20 (Codes for Units of Measure)",
        "unece:PackageTypeCodeList": "UNECE Recommendation No. 21 (Codes for Passengers, Types of Cargo, Packages and Packaging Materials)",
        "unece:DeliveryTermsCodeList": "Delivery terms (UNTDED 4053): the ICC Incoterms 2020 abbreviations of UNECE Recommendation No. 5, plus two generic codes",
        "unece:TransportMovementStageCodeList": "Transport stage code qualifier (UNTDED 8051), e.g. 10 pre-carriage, 20 main carriage, 30 on-carriage",
        "unece:CurrencyCodeList": "Currency codes (UNTDED 6345): ISO 4217 alphabetic codes, UNECE Recommendation No. 9",
        "unece:PartyRoleCodeList": "Party function code qualifier (UNTDED 3035): the UN/CEFACT party roles, e.g. CZ consignor, CN consignee, CA carrier, N1 notify party",
    }),
    Source("unlocode-vocab", BASE_URL + "unlocode-vocab", whole_document=True),
    Source("unlocode-countries", BASE_URL + "unlocode-countries", {
        "unlcdv:Country": "ISO 3166-1 alpha-2 country codes, as published with UN/LOCODE (UNECE Recommendation No. 16)",
    }),
    Source("unlocode-subdivisions", BASE_URL + "unlocode-subdivisions", {
        "unlcdv:Subdivision": "ISO 3166-2 country subdivision codes, as published with UN/LOCODE (UNECE Recommendation No. 16)",
    }),
    Source("unlocode-functions", BASE_URL + "unlocode-functions", {
        "unlcdv:Function": "UN/LOCODE function classifiers (UNECE Recommendation No. 16)",
    }),
]

#: Reference-data classes whose members are deliberately NOT vendored: compact class IRI ->
#: (where the rows come from, the instruction stamped on the class). The class and its
#: properties ship (from unlocode-vocab) so every hub targets the same shape and IRIs; the
#: rows are loaded into the hub as a reference table. Kept as prose until the toolkit reads
#: a machine-readable marker for it (kairos-ontology-toolkit#1126).
HUB_LOADED_CLASSES = {
    "unlcdv:UNLOCODE": (
        BASE_URL + "unlocode",
        "Reference data whose members are deliberately not vendored: the ~116,000 UN/LOCODE "
        "locations (~39 MB, re-released twice a year) belong in the hub as a reference table, "
        "not in an imported ontology. Load them from https://vocabulary.uncefact.org/unlocode "
        "(JSON-LD; each location's IRI is https://vocabulary.uncefact.org/unlocode#<LOCODE>) "
        "or from the official UNECE UN/LOCODE CSV release, which also carries the Status "
        "column the endpoint does not serve. Key rows on the 5-character code (country + "
        "3-character location), and link them to the shipped codes with unlcdv:countryCode "
        "(unlcdv:Country), unlcdv:countrySubdivision (unlcdv:Subdivision) and "
        "unlcdv:functions (unlcdv:Function). See the module README, 'UN/LOCODE locations'.",
    ),
}

# The BSP dump's @context declares rdfs, unece, xsd, owl and schema but not rdf, although
# every code value is keyed "rdf:value". A conforming JSON-LD processor would read
# "rdf:value" as an absolute IRI with scheme "rdf", so the dumps are read as plain JSON
# and compact IRIs are expanded here against each document's own @context, with rdf:
# given its standard namespace when a context omits it.
FALLBACK_PREFIXES = {"rdf": str(RDF), "rdfs": str(RDFS), "owl": str(OWL), "xsd": str(XSD)}


class Expander:
    def __init__(self, context: dict):
        self.prefixes = dict(FALLBACK_PREFIXES)
        self.prefixes.update({k: v for k, v in context.items() if isinstance(v, str)})

    def __call__(self, compact: str) -> URIRef:
        prefix, sep, local = compact.partition(":")
        if sep and prefix in self.prefixes:
            return URIRef(self.prefixes[prefix] + local)
        if compact.startswith(("http://", "https://")):
            return URIRef(compact)
        raise ValueError(f"unexpected compact IRI {compact!r}")


def fetch(url: str, accept: str = "application/ld+json", timeout: int = 300) -> bytes:
    request = urllib.request.Request(url, headers={"Accept": accept})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_upstream_releases() -> dict[str, str]:
    """Releases the endpoint's landing page names (BSP "D23B", UN/LOCODE "v2023-2").

    The JSON-LD dumps carry no version, but the HTML landing page labels each vocabulary.
    Best effort: page layout is not a contract, so a miss is recorded as "unknown" rather
    than failing the refresh.
    """
    releases = {"bsp": "unknown", "unlocode": "unknown"}
    try:
        html = fetch(BASE_URL, accept="text/html", timeout=60).decode("utf-8", errors="replace")
    except OSError:
        return releases
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    if match := re.search(r"Buy-Ship-Pay.{0,120}?Browse (D\d{2}[A-Z])\b", text):
        releases["bsp"] = match.group(1)
    if match := re.search(r"UN/LOCODEs.{0,120}?Browse (v\d{4}-\d+)\b", text):
        releases["unlocode"] = match.group(1)
    return releases


def as_list(value):
    return value if isinstance(value, list) else [value]


#: Characters that make an IRI invalid. Upstream has shipped node ids with a trailing space
#: (unlcds:SNDB , unlcds:SOGE , unlcds:THS ); such a node cannot be serialised, and
#: correcting it would mint an IRI in UN/CEFACT's namespace that UN/CEFACT never
#: published. It is skipped and listed in METADATA.txt instead.
INVALID_IRI_RE = re.compile(r'[\s<>"{}|\\^`]')


def extract(source: Source, document: dict, graph: Graph, counts: dict[str, int], skipped: list[str]) -> None:
    """Copy the selected nodes of one document into *graph*, unchanged."""
    expand = Expander(document.get("@context", {}))
    nodes = document["@graph"]
    if source.whole_document:
        selected = list(nodes)
    else:
        # The class node travels with its members in the BSP dump; UN/LOCODE declares its
        # classes in the separate unlocode-vocab document (checked in main()).
        by_id = {node["@id"]: node for node in nodes}
        selected = [by_id[class_id] for class_id in source.lists if class_id in by_id]
        for node in nodes:
            types = set(as_list(node.get("@type", [])))
            if types & source.lists.keys():
                if INVALID_IRI_RE.search(node["@id"]):
                    label = node.get("rdfs:label") or node.get("rdfs:comment") or ""
                    skipped.append(f"{node['@id']!r} ({label})")
                    continue
                if len(types) != 1:
                    raise ValueError(f"{node['@id']}: expected exactly one type, got {types}")
                selected.append(node)
                counts[next(iter(types))] += 1

    for node in selected:
        subject = expand(node["@id"])
        for key, value in node.items():
            if key == "@id":
                continue
            predicate = RDF.type if key == "@type" else expand(key)
            for item in as_list(value):
                if key == "@type":
                    graph.add((subject, predicate, expand(item)))
                elif isinstance(item, dict) and set(item) == {"@id"}:
                    graph.add((subject, predicate, expand(item["@id"])))
                elif isinstance(item, str):
                    graph.add((subject, predicate, Literal(item)))
                else:
                    raise ValueError(f"{node['@id']}: unexpected value {key}={item!r}")


def all_lists() -> dict[str, tuple[Source, str]]:
    return {class_id: (source, what) for source in SOURCES for class_id, what in source.lists.items()}


def write_extract(graph: Graph, snapshot: str, digests: dict[str, str]) -> None:
    graph.add((EXTRACT_ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    graph.add((EXTRACT_ONTOLOGY_IRI, RDFS.label, Literal("UN/CEFACT code lists (vendor extract)")))
    graph.add((EXTRACT_ONTOLOGY_IRI, DCTERMS.source, URIRef(BASE_URL)))
    graph.add((EXTRACT_ONTOLOGY_IRI, OWL.versionInfo, Literal(f"snapshot {snapshot}")))
    graph.add((
        EXTRACT_ONTOLOGY_IRI,
        RDFS.comment,
        Literal(
            "Verbatim extract of standards-body code lists from the UN/CEFACT web vocabulary "
            f"(UNECE Rec 5, 9, 16, 19, 20, 21 and UNTDED 3035, 8051), retrieved {snapshot} from: "
            + "; ".join(f"{s.url} (sha256 {digests[s.id]})" for s in SOURCES)
            + ". Generated by scripts/download_uncefact_codelists.py; do not hand-edit."
        ),
    ))
    graph.bind("unece", UNECE)
    graph.bind("unlcdv", UNLCDV)
    graph.bind("schema", SCHEMA)
    graph.bind("dcterms", DCTERMS)
    graph.serialize(EXTRACT_TTL, format="turtle", encoding="utf-8")


def _owl_property_types(extract_graph: Graph, patch: Graph) -> None:
    """Type the UN/LOCODE vocabulary's rdf:Property terms for OWL consumers.

    Mechanical from the vocabulary's own schema:domainIncludes / schema:rangeIncludes:
    an xsd range makes a datatype property, a class range an object property, and the
    domainIncludes set becomes rdfs:domain (an owl:unionOf when there are several).
    """
    for prop in sorted(extract_graph.subjects(RDF.type, RDF.Property)):
        ranges = sorted(extract_graph.objects(prop, SCHEMA.rangeIncludes))
        domains = sorted(extract_graph.objects(prop, SCHEMA.domainIncludes))
        is_datatype = bool(ranges) and all(str(r).startswith(str(XSD)) for r in ranges)
        patch.add((prop, RDF.type, OWL.DatatypeProperty if is_datatype else OWL.ObjectProperty))
        if len(ranges) == 1:
            patch.add((prop, RDFS.range, ranges[0]))
        if len(domains) == 1:
            patch.add((prop, RDFS.domain, domains[0]))
        elif len(domains) > 1:
            union, members = BNode(), BNode()
            Collection(patch, members, domains)
            patch.add((union, RDF.type, OWL.Class))
            patch.add((union, OWL.unionOf, members))
            patch.add((prop, RDFS.domain, union))


def write_patch(extract_graph: Graph, snapshot: str) -> None:
    patch = Graph()
    patch.bind("unece", UNECE)
    patch.bind("unlcdv", UNLCDV)
    patch.bind("dcterms", DCTERMS)
    patch.bind("kairos-ext", KAIROS_EXT)
    patch.add((PUBLIC_ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    patch.add((PUBLIC_ONTOLOGY_IRI, RDFS.label, Literal("UN/CEFACT code lists")))
    patch.add((PUBLIC_ONTOLOGY_IRI, OWL.imports, EXTRACT_ONTOLOGY_IRI))
    # Provenance a consumer can read without opening METADATA.txt: the snapshot date is the
    # version (upstream publishes none), and the README says how and when to refresh.
    patch.add((PUBLIC_ONTOLOGY_IRI, OWL.versionInfo, Literal(snapshot)))
    patch.add((PUBLIC_ONTOLOGY_IRI, DCTERMS.modified, Literal(snapshot, datatype=XSD.date)))
    patch.add((PUBLIC_ONTOLOGY_IRI, DCTERMS.source, URIRef(BASE_URL)))
    patch.add((PUBLIC_ONTOLOGY_IRI, RDFS.seeAlso, URIRef(README_URL)))
    patch.add((
        PUBLIC_ONTOLOGY_IRI,
        DCTERMS.description,
        Literal(
            f"Reference data: standards-body code lists retrieved from {BASE_URL} on {snapshot} "
            "(per-document checksums in METADATA.txt). Refresh with "
            "scripts/download_uncefact_codelists.py; see the README linked by rdfs:seeAlso."
        ),
    ))
    patch.add((KAIROS_EXT.isReferenceData, RDF.type, OWL.AnnotationProperty))
    patch.add((
        PUBLIC_ONTOLOGY_IRI,
        RDFS.comment,
        Literal(
            "OWL typing for the vendored UN/CEFACT code lists. The upstream vocabulary "
            "declares each list as rdfs:Class, its codes as plain typed nodes, and its "
            "properties as rdf:Property; OWL-based consumers need owl:Class, "
            "owl:NamedIndividual, rdfs:label and OWL property types. Those triples are "
            "derived mechanically from the extract (rdfs:label is copied from rdfs:comment "
            "only where a code has no label); the rest is provenance (reference-data "
            "marker, snapshot version, source and README links). Generated by "
            "scripts/download_uncefact_codelists.py; do not hand-edit."
        ),
    ))
    expand = Expander({"unece": BASE_URL, "unlcdv": str(UNLCDV)})
    for class_id, (source, what) in all_lists().items():
        cls = expand(class_id)
        patch.add((cls, RDF.type, OWL.Class))
        patch.add((cls, KAIROS_EXT.isReferenceData, Literal(True)))
        patch.add((cls, OWL.versionInfo, Literal(snapshot)))
        patch.add((cls, DCTERMS.source, URIRef(source.url)))
        patch.add((cls, DCTERMS.description, Literal(what)))
        patch.add((cls, RDFS.seeAlso, URIRef(README_URL)))
        for member in extract_graph.subjects(RDF.type, cls):
            patch.add((member, RDF.type, OWL.NamedIndividual))
            if (member, RDFS.label, None) not in extract_graph:
                for comment in extract_graph.objects(member, RDFS.comment):
                    patch.add((member, RDFS.label, comment))
    # Classes the vendored UN/LOCODE vocabulary declares without shipped members (UNLOCODE).
    for cls in extract_graph.subjects(RDF.type, RDFS.Class):
        patch.add((cls, RDF.type, OWL.Class))
    for class_id, (source_url, instruction) in HUB_LOADED_CLASSES.items():
        cls = expand(class_id)
        if (cls, RDF.type, RDFS.Class) not in extract_graph:
            raise ValueError(f"{class_id} is not declared by any vendored document")
        if (None, RDF.type, cls) in extract_graph:
            raise ValueError(f"{class_id} is hub-loaded but members were vendored")
        patch.add((cls, KAIROS_EXT.isReferenceData, Literal(True)))
        patch.add((cls, OWL.versionInfo, Literal(snapshot)))
        patch.add((cls, DCTERMS.source, URIRef(source_url)))
        patch.add((cls, DCTERMS.description, Literal(instruction)))
        patch.add((cls, RDFS.seeAlso, URIRef(README_URL)))
    _owl_property_types(extract_graph, patch)
    patch.serialize(PATCH_TTL, format="turtle", encoding="utf-8")


def combined_digest(digests: dict[str, str]) -> str:
    return hashlib.sha256("\n".join(f"{k}={digests[k]}" for k in sorted(digests)).encode()).hexdigest()


def write_metadata(snapshot: str, digests: dict[str, str], sizes: dict[str, int],
                   counts: dict[str, int], releases: dict[str, str], skipped: list[str]) -> None:
    skipped_note = (
        "  - Skipped upstream nodes whose id is not a valid IRI (not corrected: that would\n"
        "    mint IRIs UN/CEFACT never published; not yet reported upstream):\n"
        + "\n".join(f"      {s}" for s in skipped)
        + "\n"
    ) if skipped else ""
    lists = "\n".join(
        f"  - {class_id} ({counts[class_id]} codes) -- {what}" for class_id, (_, what) in all_lists().items()
    )
    documents = "\n".join(
        f"  - {s.id}: {s.url} ({sizes[s.id]} bytes, sha256 {digests[s.id]})" for s in SOURCES
    )
    METADATA_TXT.write_text(
        f"""UN/CEFACT Code Lists - Download Information
============================================

source: UN/CEFACT JSON-LD Web Vocabulary
publisher: United Nations Centre for Trade Facilitation and Electronic Business (UN/CEFACT), UNECE
source_url: {BASE_URL} (Accept: application/ld+json)
source_repository: https://github.com/uncefact/spec-JSONLD
download_date: {snapshot}
version: {snapshot} (snapshot date; upstream publishes no version)
upstream_release: BSP {releases['bsp']}, UN/LOCODE {releases['unlocode']} (as named on the endpoint's landing page at download time)
dump_sha256: {combined_digest(digests)} (combined; per document below)
documents:
{documents}
code_lists:
{lists}
ontology_files:
  - UNCEFACT-CodeLists.ttl            (vendor extract; ontology IRI {EXTRACT_ONTOLOGY_IRI})
  - UNCEFACT-CodeLists.owl-patch.ttl  (generated OWL typing; ontology IRI {PUBLIC_ONTOLOGY_IRI})
  - UNCEFACT-IATA-alignment.ttl       (generated IATA -> UNECE skos:exactMatch; see
                                       scripts/generate_uncefact_iata_alignment.py)
license: CC BY 4.0 per UN/CEFACT ("All UN/CEFACT standards are free to use under CC By
  4.0 license"), attribution to UNECE; confirmation that it covers this endpoint is
  pending -- the endpoint's own site terms are the generic UN website terms. ISO 3166
  and ISO 4217 codes are republished here as UNECE publishes them; ISO states the codes
  themselves are free to use. See README.md, section License.
generator: scripts/download_uncefact_codelists.py -- regenerates all three files; do not hand-edit.
deviations:
  - Extract, not mirror. Only the code-list classes above, the nodes typed by them, and
    the UN/LOCODE vocabulary (4 classes, 4 properties) are vendored; the rest of the
    vocabulary (the UN/CEFACT trade data model, the UN/LOCODE locations) is not.
  - Owl:Ontology headers are Kairos-minted. The dumps declare no ontology, and an
    extract must not claim the IRI of the whole vocabulary.
  - The BSP dump's @context omits the rdf: prefix used by every rdf:value; the generator
    expands it to the standard RDF namespace. Not yet reported upstream.
  - UNCEFACT-CodeLists.owl-patch.ttl adds owl:Class, owl:NamedIndividual, rdfs:label
    (copied from rdfs:comment where a code has none) and OWL types, domains and ranges
    for the UN/LOCODE properties (from schema:domainIncludes / schema:rangeIncludes).
    Wired in by importing the extract, so the extract stays byte-for-byte generated.
  - unlcdv:UNLOCODE ships as a class without members: the locations are loaded into
    the hub as a reference table from {BASE_URL}unlocode. The patch marks it as
    reference data and states the loading instruction in dcterms:description.
  - The patch also marks each code-list class as reference data
    (kairos-ext:isReferenceData true) and stamps the ontology and each class with
    owl:versionInfo "<download_date>", dcterms:source <its document> and
    rdfs:seeAlso <the module README>.
{skipped_note}""",
        encoding="utf-8",
    )


def recorded_snapshot() -> tuple[str | None, str | None]:
    """Return (download_date, combined dump_sha256) from the current METADATA.txt, if any."""
    if not METADATA_TXT.is_file():
        return None, None
    fields = dict(
        line.split(": ", 1) for line in METADATA_TXT.read_text(encoding="utf-8").splitlines() if ": " in line
    )
    digest = fields.get("dump_sha256", "").split(" ", 1)[0] or None
    return fields.get("download_date"), digest


def archive_current(old_date: str) -> None:
    """Move the current snapshot to archive/<old download date>/, as download_fibo.py does."""
    archive_dir = TARGET_DIR.parent / "archive" / old_date
    if archive_dir.exists():
        raise SystemExit(f"ERROR: {archive_dir} already exists; refusing to overwrite an archived snapshot")
    archive_dir.mkdir(parents=True)
    for path in sorted(TARGET_DIR.iterdir()):
        path.rename(archive_dir / path.name)
    print(f"Archived snapshot {old_date} -> archive/{old_date}/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from-dir", type=Path, help="use saved dumps (<dir>/<source id>.jsonld) instead of downloading")
    parser.add_argument("--snapshot-date", help="download date to record (default: today)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="only report whether upstream differs from the vendored snapshot (exit 1 if it does)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="regenerate even when upstream is unchanged (after changing this script)",
    )
    parser.add_argument("--upstream-release", nargs=2, metavar=("BSP", "UNLOCODE"),
                        help="releases to record (default: read from the landing page)")
    args = parser.parse_args()

    raws: dict[str, bytes] = {}
    for source in SOURCES:
        if args.from_dir:
            raws[source.id] = (args.from_dir / f"{source.id}.jsonld").read_bytes()
        else:
            print(f"Downloading {source.url} ...")
            raws[source.id] = fetch(source.url)
    snapshot = args.snapshot_date or date.today().isoformat()

    digests = {k: hashlib.sha256(v).hexdigest() for k, v in raws.items()}
    digest = combined_digest(digests)
    old_date, old_digest = recorded_snapshot()
    if args.check:
        if digest == old_digest:
            print(f"Up to date: upstream matches the vendored snapshot of {old_date}.")
            return 0
        print(f"Upstream changed since the vendored snapshot of {old_date}: re-run without --check.")
        return 1
    if digest == old_digest and not args.force:
        print(f"Up to date: upstream matches the vendored snapshot of {old_date}; nothing written.")
        return 0

    graph = Graph()
    counts = dict.fromkeys(all_lists(), 0)
    skipped: list[str] = []
    for source in SOURCES:
        extract(source, json.loads(raws[source.id]), graph, counts, skipped)
    for note in skipped:
        print(f"  skipped (invalid IRI upstream): {note}")
    if not all(counts.values()):
        print(f"ERROR: a code list came back empty: {counts}", file=sys.stderr)
        return 1
    expand = Expander({"unece": BASE_URL, "unlcdv": str(UNLCDV)})
    undeclared = [c for c in counts if (expand(c), RDF.type, RDFS.Class) not in graph]
    if undeclared:
        print(f"ERROR: code-list classes no upstream document declares: {undeclared}", file=sys.stderr)
        return 1

    if old_date and old_date != snapshot:
        archive_current(old_date)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    write_extract(graph, snapshot, digests)
    write_patch(graph, snapshot)
    if args.upstream_release:
        releases = dict(zip(("bsp", "unlocode"), args.upstream_release))
    else:
        releases = fetch_upstream_releases()
    write_metadata(snapshot, digests, {k: len(v) for k, v in raws.items()}, counts, releases, skipped)
    for class_id, count in counts.items():
        print(f"  {class_id}: {count} codes")
    print(f"Wrote {EXTRACT_TTL.name}, {PATCH_TTL.name}, {METADATA_TXT.name} (snapshot {snapshot}, sha256 {digest[:12]}...)")

    # The IATA alignment links into these codes, so it is regenerated with them.
    sys.stdout.flush()
    alignment = subprocess.run([sys.executable, str(Path(__file__).with_name("generate_uncefact_iata_alignment.py"))])
    if alignment.returncode:
        return alignment.returncode
    print("Next: diff the result (a removed code breaks hubs that store it), then run the test suite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
