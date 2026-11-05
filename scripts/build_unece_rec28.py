#!/usr/bin/env python3
"""Build UNECE Recommendation 28 (codes for types of means of transport) from the official code list.

UN/CEFACT's web vocabulary carries only part of Rec 28: ``unece:TransportMeansTypeCodeList``
has the 134 four-digit codes and none of the two- and three-digit ones, which include the
generic road codes (31 Truck, 33 Tractor, 34 Van, 342 Van, light). The complete list is the
Rev 4.2 (2018) code list UNECE publishes as an XLS on
https://unece.org/trade/uncefact/cl-recommendations. That file is vendored unchanged next to
the generated Turtle, and this script builds the code list from it.

The sheet has one row per code, with columns CI (change indicator), Mode, Code-A, Code-B,
Name and Description. The code is Mode + Code-A + Code-B concatenated (3,4,2 -> "342"), which
gives 282 unique codes. Each member gets:

* ``rdf:value``: the code, which is the join key;
* ``rdfs:label``: the Name; ``skos:definition``: the Description;
* ``rec28:transportMode``: the Rec 19 mode the first digit stands for
  (``unece:TransportModeCodeList#<mode>``);
* ``skos:broader``: a Code-B row's broader code is its Code-A row (342 -> 34);
* ``owl:deprecated true`` where the change indicator is ``X`` (marked for deletion in this
  revision), and ``rec28:changeIndicator`` for any non-blank indicator.

IRIs are Kairos-minted (``https://www.kairosflow.ai/ont/unece-rec28#342``), because UNECE
publishes the full list as XLS only. ``UNECE-Rec28-alignment.ttl`` links each four-digit code
by ``skos:exactMatch`` to the same code in ``unece:TransportMeansTypeCodeList``. The build
fails if the two disagree on which four-digit codes exist.

Rec 28 changes rarely (Rev 4.2 is from 2018). Rebuild only when UNECE publishes a new revision:
replace the XLS in the module's current/ and re-run. Reading .xls needs xlrd:

    uv run --with xlrd python scripts/build_unece_rec28.py
"""
import hashlib
import sys
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTHORITATIVE = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models" / "authoritative-ontologies"
TARGET_DIR = AUTHORITATIVE / "UNECE-Rec28" / "current"
SOURCE_XLS = TARGET_DIR / "Rec28_Rev4.2e_2018.xls"
CODES_TTL = TARGET_DIR / "UNECE-Rec28.ttl"
ALIGNMENT_TTL = TARGET_DIR / "UNECE-Rec28-alignment.ttl"
METADATA_TXT = TARGET_DIR / "METADATA.txt"
UNCEFACT_TTL = AUTHORITATIVE / "UNCEFACT" / "current" / "UNCEFACT-CodeLists.ttl"

SOURCE_PAGE = "https://unece.org/trade/uncefact/cl-recommendations"
REVISION = "4.2"
REVISION_YEAR = "2018"

ONTOLOGY_IRI = URIRef("https://www.kairosflow.ai/ont/unece-rec28")
ALIGNMENT_IRI = URIRef("https://www.kairosflow.ai/ont/unece-rec28/alignment")
REC28 = Namespace("https://www.kairosflow.ai/ont/unece-rec28#")
UNECE = Namespace("https://vocabulary.uncefact.org/")
KAIROS_EXT = Namespace("https://kairos.cnext.eu/ext#")
README_URL = (
    "https://github.com/Cnext-eu/kairos-ontology-referencemodels/blob/main/"
    "kairos_ontology_referencemodels/ontology-reference-models/authoritative-ontologies/UNECE-Rec28/README.md"
)

#: Sub-codes whose Code-A row the revision does not print (e.g. 1711 without a 171 row). They get
#: no skos:broader; build() collects them and METADATA.txt lists them.
ORPHANS: list[str] = []


def cell(value) -> str:
    if isinstance(value, float):
        return str(int(value))
    return str(value).strip()


def read_rows(path: Path) -> list[dict]:
    try:
        import xlrd
    except ImportError:
        raise SystemExit("xlrd is needed to read the .xls: uv run --with xlrd python scripts/build_unece_rec28.py")
    sheet = xlrd.open_workbook(str(path)).sheet_by_index(0)
    header = [cell(c.value) for c in sheet.row(2)]
    if header[:6] != ["CI", "Mode", "Code-A", "Code-B", "Name", "Description"]:
        raise SystemExit(f"unexpected header row: {header}")
    title = cell(sheet.cell_value(0, 0))
    if f"Revision {REVISION}" not in title:
        raise SystemExit(f"expected Revision {REVISION}, title is {title!r}; update REVISION")
    rows = []
    for r in range(3, sheet.nrows):
        ci, mode, code_a, code_b, name, description = (cell(c.value) for c in sheet.row(r)[:6])
        if not (mode or code_a or name):
            continue
        rows.append({"ci": ci, "mode": mode, "a": code_a, "b": code_b, "code": mode + code_a + code_b,
                     "name": name, "description": description})
    return rows


def build(rows: list[dict]) -> Graph:
    codes = [row["code"] for row in rows]
    if len(set(codes)) != len(codes):
        raise SystemExit("duplicate codes in the XLS")
    known = set(codes)
    g = Graph()
    for prefix, ns in (("rec28", REC28), ("unece", UNECE), ("skos", SKOS), ("dcterms", DCTERMS), ("kairos-ext", KAIROS_EXT)):
        g.bind(prefix, ns)
    g.add((ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    g.add((ONTOLOGY_IRI, RDFS.label, Literal("UNECE Recommendation 28: codes for types of means of transport")))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(f"Rev {REVISION} ({REVISION_YEAR})")))
    g.add((ONTOLOGY_IRI, DCTERMS.source, URIRef(SOURCE_PAGE)))
    g.add((ONTOLOGY_IRI, RDFS.seeAlso, URIRef(README_URL)))
    g.add((ONTOLOGY_IRI, RDFS.comment, Literal(
        f"UNECE Recommendation 28, Revision {REVISION} ({REVISION_YEAR}), built from the official XLS code "
        "list (vendored unchanged as Rec28_Rev4.2e_2018.xls). Codes, names and descriptions are copied "
        "from the file unchanged; the IRIs are Kairos-minted because "
        "UNECE publishes the full list as XLS only. Generated by scripts/build_unece_rec28.py; do not "
        "hand-edit."
    )))

    cls = REC28.TransportMeansTypeCode
    g.add((cls, RDF.type, OWL.Class))
    g.add((cls, RDFS.label, Literal("Rec 28 type of means of transport")))
    g.add((cls, RDFS.comment, Literal(
        "A type of means of transport (vessel, train, road vehicle, aircraft, ...). The code is in "
        "rdf:value; its first digit is the UNECE Rec 19 transport mode (rec28:transportMode). Codes "
        "are hierarchical: skos:broader runs from a sub-type to its type (342 Van, light -> 34 Van)."
    )))
    g.add((cls, KAIROS_EXT.isReferenceData, Literal(True)))
    g.add((cls, OWL.versionInfo, Literal(f"Rev {REVISION} ({REVISION_YEAR})")))
    g.add((cls, DCTERMS.source, URIRef(SOURCE_PAGE)))
    g.add((cls, DCTERMS.description, Literal("UNECE Recommendation No. 28, Codes for Types of Means of Transport")))
    g.add((cls, RDFS.seeAlso, URIRef(README_URL)))
    g.add((KAIROS_EXT.isReferenceData, RDF.type, OWL.AnnotationProperty))

    mode_prop = REC28.transportMode
    g.add((mode_prop, RDF.type, OWL.ObjectProperty))
    g.add((mode_prop, RDFS.label, Literal("transport mode")))
    g.add((mode_prop, RDFS.comment, Literal("The UNECE Rec 19 transport mode the code's first digit stands for.")))
    g.add((mode_prop, RDFS.domain, cls))
    g.add((mode_prop, RDFS.range, UNECE.TransportModeCodeList))
    ci_prop = REC28.changeIndicator
    g.add((ci_prop, RDF.type, OWL.DatatypeProperty))
    g.add((ci_prop, RDFS.label, Literal("change indicator")))
    g.add((ci_prop, RDFS.comment, Literal(
        f"The Revision {REVISION} change indicator as printed: '+' added, '|' changed, 'X' marked for "
        "deletion (also owl:deprecated)."
    )))
    g.add((ci_prop, RDFS.domain, cls))
    g.add((ci_prop, RDFS.range, XSD.string))

    for row in rows:
        member = REC28[row["code"]]
        g.add((member, RDF.type, OWL.NamedIndividual))
        g.add((member, RDF.type, cls))
        g.add((member, RDF.value, Literal(row["code"])))
        g.add((member, RDFS.label, Literal(row["name"])))
        if row["description"]:
            g.add((member, SKOS.definition, Literal(row["description"])))
        g.add((member, mode_prop, URIRef(f"{UNECE}TransportModeCodeList#{row['mode']}")))
        if row["b"]:
            parent = row["mode"] + row["a"]
            if parent in known:
                g.add((member, SKOS.broader, REC28[parent]))
            else:
                ORPHANS.append(f"{row['code']} (no {parent} row)")
        if row["ci"]:
            g.add((member, ci_prop, Literal(row["ci"])))
        if row["ci"] == "X":
            g.add((member, OWL.deprecated, Literal(True)))
    return g


def build_alignment(rows: list[dict]) -> tuple[Graph, int]:
    vocab = Graph().parse(UNCEFACT_TTL)
    vocab_codes = {str(vocab.value(m, RDF.value)): m for m in vocab.subjects(RDF.type, UNECE.TransportMeansTypeCodeList)}
    four = {row["code"] for row in rows if len(row["code"]) == 4}
    if vocab_codes and set(vocab_codes) != four:
        raise SystemExit(
            "UN/CEFACT's TransportMeansTypeCodeList no longer equals Rec 28's four-digit codes: "
            f"vocabulary-only {sorted(set(vocab_codes) - four)}, Rec 28-only {sorted(four - set(vocab_codes))}"
        )
    g = Graph()
    g.bind("skos", SKOS)
    g.bind("rec28", REC28)
    for code, member in vocab_codes.items():
        g.add((REC28[code], SKOS.exactMatch, member))
    g.add((ALIGNMENT_IRI, RDF.type, OWL.Ontology))
    g.add((ALIGNMENT_IRI, RDFS.label, Literal("UNECE Rec 28 to UN/CEFACT vocabulary alignment")))
    g.add((ALIGNMENT_IRI, RDFS.comment, Literal(
        f"skos:exactMatch from each of the {len(vocab_codes)} four-digit Rec 28 codes to the same code in "
        "unece:TransportMeansTypeCodeList, which carries only those. Generated by "
        "scripts/build_unece_rec28.py; do not hand-edit."
    )))
    return g, len(vocab_codes)


def main() -> int:
    raw = SOURCE_XLS.read_bytes()
    rows = read_rows(SOURCE_XLS)
    codes = build(rows)
    codes.serialize(CODES_TTL, format="turtle", encoding="utf-8")
    alignment, linked = build_alignment(rows)
    alignment.serialize(ALIGNMENT_TTL, format="turtle", encoding="utf-8")
    deprecated = [row["code"] for row in rows if row["ci"] == "X"]
    by_length = {n: sum(1 for row in rows if len(row["code"]) == n) for n in (2, 3, 4)}
    METADATA_TXT.write_text(f"""UNECE Recommendation 28 - Source Information
============================================

source: UNECE Recommendation No. 28, Codes for Types of Means of Transport
publisher: UN/CEFACT, United Nations Economic Commission for Europe
source_page: {SOURCE_PAGE}
source_file: {SOURCE_XLS.name} (vendored unchanged; {len(raw)} bytes, sha256 {hashlib.sha256(raw).hexdigest()})
version: Rev {REVISION} ({REVISION_YEAR})
codes: {len(rows)} ({by_length[2]} two-digit, {by_length[3]} three-digit, {by_length[4]} four-digit)
deprecated: {", ".join(deprecated) or "none"} (change indicator X: marked for deletion in this revision)
alignment: {linked} four-digit codes linked by skos:exactMatch to unece:TransportMeansTypeCodeList
ontology_files:
  - UNECE-Rec28.ttl            (generated; ontology IRI {ONTOLOGY_IRI})
  - UNECE-Rec28-alignment.ttl  (generated; ontology IRI {ALIGNMENT_IRI})
license: UNECE recommendation; same position as authoritative-ontologies/UNCEFACT (CC BY 4.0 per
  UN/CEFACT, confirmation pending). See README.md, section License.
generator: scripts/build_unece_rec28.py (uv run --with xlrd ...) -- do not hand-edit.
deviations:
  - IRIs are Kairos-minted (https://www.kairosflow.ai/ont/unece-rec28#<code>): the full list is XLS only.
  - The code is Mode + Code-A + Code-B as printed; skos:broader and rec28:transportMode are derived
    from those columns.
  - Sub-codes without a printed Code-A row get no skos:broader: {", ".join(ORPHANS) or "none"}
  - Labels are kept exactly as printed, including an en dash (1515) and non-breaking spaces
    (e.g. "type N"); the UN/CEFACT vocabulary writes 1515 with a hyphen.
""", encoding="utf-8")
    print(f"  {len(rows)} codes {by_length}, deprecated {deprecated}, alignment {linked}")
    print(f"Wrote {CODES_TTL.name}, {ALIGNMENT_TTL.name}, {METADATA_TXT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
