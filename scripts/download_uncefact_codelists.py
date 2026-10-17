#!/usr/bin/env python3
"""Vendor UNECE code lists from the UN/CEFACT web vocabulary (gh#120).

UN/CEFACT publishes its whole web vocabulary as one unversioned JSON-LD document at
https://vocabulary.uncefact.org/ (content negotiation on ``Accept: application/ld+json``;
per-term URLs answer 403). The dump carries ~16,900 nodes — the complete UN/CEFACT trade
data model — of which Kairos vendors only the standards-body code lists listed in
``CODE_LISTS``. Every vendored triple is copied from the dump unchanged, with its
original ``https://vocabulary.uncefact.org/`` IRI.

Two files are written, mirroring the IATA domains-patch arrangement (gh#93):

* ``UNCEFACT-CodeLists.ttl`` — the vendor extract. Never hand-edit; re-run this script.
* ``UNCEFACT-CodeLists.owl-patch.ttl`` — generated OWL typing the extract lacks
  (``owl:Class``, ``owl:NamedIndividual``, ``rdfs:label``). It imports the extract and
  is the document hubs import, via ``https://www.kairosflow.ai/ont/uncefact/code-lists``.

``METADATA.txt`` is regenerated too, so the snapshot date and checksum cannot drift
from the files they describe.

Usage:
    python scripts/download_uncefact_codelists.py                 # download the live dump
    python scripts/download_uncefact_codelists.py --from-file X   # use a saved dump
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS

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

SOURCE_URL = "https://vocabulary.uncefact.org/"
UNECE = Namespace(SOURCE_URL)

PUBLIC_ONTOLOGY_IRI = URIRef("https://www.kairosflow.ai/ont/uncefact/code-lists")
EXTRACT_ONTOLOGY_IRI = URIRef("https://www.kairosflow.ai/ont/uncefact/code-lists-vendor-extract")

#: Class local name in the UN/CEFACT vocabulary -> the UNECE recommendation it publishes.
CODE_LISTS = {
    "TransportModeCodeList": "UNECE Recommendation No. 19 (Codes for Modes of Transport)",
    "UnitMeasureCode": "UNECE Recommendation No. 20 (Codes for Units of Measure)",
    "PackageTypeCodeList": "UNECE Recommendation No. 21 (Codes for Passengers, Types of Cargo, Packages and Packaging Materials)",
}

# The dump's @context declares rdfs, unece, xsd, owl and schema but not rdf, although
# every code value is keyed "rdf:value". A conforming JSON-LD processor would read
# "rdf:value" as an absolute IRI with scheme "rdf", so the dump is read as plain JSON and
# compact IRIs are expanded here, with rdf: given its standard namespace.
PREFIXES = {
    "rdf": str(RDF),
    "rdfs": str(RDFS),
    "owl": str(OWL),
    "unece": SOURCE_URL,
}


def expand(compact: str) -> URIRef:
    prefix, _, local = compact.partition(":")
    if prefix not in PREFIXES:
        raise ValueError(f"unexpected compact IRI {compact!r}")
    return URIRef(PREFIXES[prefix] + local)


def fetch_dump() -> bytes:
    request = urllib.request.Request(SOURCE_URL, headers={"Accept": "application/ld+json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def as_list(value):
    return value if isinstance(value, list) else [value]


def extract(nodes: list[dict]) -> tuple[Graph, dict[str, int]]:
    """Copy each code-list class node and every node typed by it, unchanged."""
    by_id = {node["@id"]: node for node in nodes}
    wanted = {f"unece:{name}" for name in CODE_LISTS}
    graph = Graph()
    counts = dict.fromkeys(CODE_LISTS, 0)

    selected = [by_id[class_id] for class_id in sorted(wanted)]
    for node in nodes:
        types = set(as_list(node.get("@type", [])))
        if types & wanted:
            if len(types) != 1:
                raise ValueError(f"{node['@id']}: expected exactly one type, got {types}")
            selected.append(node)
            counts[next(iter(types)).removeprefix("unece:")] += 1

    for node in selected:
        subject = expand(node["@id"])
        for key, value in node.items():
            if key == "@id":
                continue
            if key == "@type":
                for type_ in as_list(value):
                    graph.add((subject, RDF.type, expand(type_)))
                continue
            for item in as_list(value):
                if not isinstance(item, str):
                    raise ValueError(f"{node['@id']}: unexpected non-literal {key}={item!r}")
                graph.add((subject, expand(key), Literal(item)))
    return graph, counts


def write_extract(graph: Graph, snapshot: str, digest: str) -> None:
    graph.add((EXTRACT_ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    graph.add((EXTRACT_ONTOLOGY_IRI, RDFS.label, Literal("UN/CEFACT code lists (vendor extract)")))
    graph.add((EXTRACT_ONTOLOGY_IRI, DCTERMS.source, URIRef(SOURCE_URL)))
    graph.add((EXTRACT_ONTOLOGY_IRI, OWL.versionInfo, Literal(f"snapshot {snapshot}")))
    graph.add((
        EXTRACT_ONTOLOGY_IRI,
        RDFS.comment,
        Literal(
            "Verbatim extract of the UNECE Rec 19, 20 and 21 code lists from the UN/CEFACT "
            f"web vocabulary, retrieved {snapshot} (sha256 of the full dump: {digest}). "
            "Generated by scripts/download_uncefact_codelists.py; do not hand-edit."
        ),
    ))
    graph.bind("unece", UNECE)
    graph.bind("dcterms", DCTERMS)
    graph.serialize(EXTRACT_TTL, format="turtle", encoding="utf-8")


def write_patch(extract_graph: Graph) -> None:
    patch = Graph()
    patch.bind("unece", UNECE)
    patch.add((PUBLIC_ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    patch.add((PUBLIC_ONTOLOGY_IRI, RDFS.label, Literal("UN/CEFACT code lists")))
    patch.add((PUBLIC_ONTOLOGY_IRI, OWL.imports, EXTRACT_ONTOLOGY_IRI))
    patch.add((
        PUBLIC_ONTOLOGY_IRI,
        RDFS.comment,
        Literal(
            "OWL typing for the vendored UN/CEFACT code lists. The upstream vocabulary "
            "declares each list as rdfs:Class and its codes as plain typed nodes whose "
            "name is in rdfs:comment; OWL-based consumers need owl:Class, "
            "owl:NamedIndividual and rdfs:label. Every triple here is derived "
            "mechanically from the extract. Generated by "
            "scripts/download_uncefact_codelists.py; do not hand-edit."
        ),
    ))
    for name in CODE_LISTS:
        cls = UNECE[name]
        patch.add((cls, RDF.type, OWL.Class))
        for member in extract_graph.subjects(RDF.type, cls):
            patch.add((member, RDF.type, OWL.NamedIndividual))
            for comment in extract_graph.objects(member, RDFS.comment):
                patch.add((member, RDFS.label, comment))
    patch.serialize(PATCH_TTL, format="turtle", encoding="utf-8")


def write_metadata(snapshot: str, digest: str, size: int, counts: dict[str, int]) -> None:
    lists = "\n".join(
        f"  - unece:{name} ({counts[name]} codes) -- {rec}" for name, rec in CODE_LISTS.items()
    )
    METADATA_TXT.write_text(
        f"""UN/CEFACT Code Lists - Download Information
============================================

source: UN/CEFACT JSON-LD Web Vocabulary
publisher: United Nations Centre for Trade Facilitation and Electronic Business (UN/CEFACT), UNECE
source_url: {SOURCE_URL} (Accept: application/ld+json)
source_repository: https://github.com/uncefact/spec-JSONLD
download_date: {snapshot}
version: none published -- the endpoint serves one unversioned dump; this snapshot is
  identified by its download date and checksum.
dump_sha256: {digest}
dump_bytes: {size}
code_lists:
{lists}
ontology_files:
  - UNCEFACT-CodeLists.ttl            (vendor extract; ontology IRI {EXTRACT_ONTOLOGY_IRI})
  - UNCEFACT-CodeLists.owl-patch.ttl  (generated OWL typing; ontology IRI {PUBLIC_ONTOLOGY_IRI})
license: see README.md, section License
generator: scripts/download_uncefact_codelists.py -- regenerates all three files; do not hand-edit.
deviations:
  - Extract, not mirror. Only the code-list classes above and the nodes typed by them
    are vendored; the rest of the vocabulary (the UN/CEFACT trade data model) is not.
  - Owl:Ontology headers are Kairos-minted. The dump declares no ontology, and an
    extract must not claim the IRI of the whole vocabulary.
  - The dump's @context omits the rdf: prefix used by every rdf:value; the generator
    expands it to the standard RDF namespace. Not yet reported upstream.
  - UNCEFACT-CodeLists.owl-patch.ttl adds owl:Class, owl:NamedIndividual and
    rdfs:label (copied from each code's rdfs:comment). Wired in by importing the
    extract, so the extract stays byte-for-byte generated.
""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from-file", type=Path, help="use a saved JSON-LD dump instead of downloading")
    parser.add_argument("--snapshot-date", help="download date to record (default: today, or the file's date)")
    args = parser.parse_args()

    if args.from_file:
        raw = args.from_file.read_bytes()
        snapshot = args.snapshot_date or date.fromtimestamp(args.from_file.stat().st_mtime).isoformat()
    else:
        print(f"Downloading {SOURCE_URL} ...")
        raw = fetch_dump()
        snapshot = args.snapshot_date or date.today().isoformat()

    digest = hashlib.sha256(raw).hexdigest()
    nodes = json.loads(raw)["@graph"]
    graph, counts = extract(nodes)
    if not all(counts.values()):
        print(f"ERROR: a code list came back empty: {counts}", file=sys.stderr)
        return 1

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    write_extract(graph, snapshot, digest)
    write_patch(graph)
    write_metadata(snapshot, digest, len(raw), counts)
    for name, count in counts.items():
        print(f"  unece:{name}: {count} codes")
    print(f"Wrote {EXTRACT_TTL.name}, {PATCH_TTL.name}, {METADATA_TXT.name} (snapshot {snapshot}, sha256 {digest[:12]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
