#!/usr/bin/env python3
"""Vendor ISO 4217 currency codes from SIX, the ISO 4217 maintenance agency (gh#128).

SIX Financial Information AG maintains ISO 4217 on behalf of ISO and publishes the lists
"online and free of charge" as XML:

* ``list-one.xml``   — current currency and fund codes, one row per (country, currency),
  with numeric code and minor unit;
* ``list-three.xml`` — historic rows, each with a withdrawal date.

Every RDF copy of ISO 4217 lags this source (UN/CEFACT's ``unece:CurrencyCodeList`` by up
to 18 months; FIBO's ``ISO4217-CurrencyCodes`` too), so this is the kind-1 currency list
hubs bind to. SIX publishes no RDF, so the IRIs are Kairos-minted
(``https://www.kairosflow.ai/ont/iso4217#EUR``); the codes, names, numbers, minor units and
dates are copied from the XML unchanged, and the XML itself is vendored next to the Turtle.

One member per alphabetic code:

* a code in ``list-one`` is **current**. Its rows supply the name, numeric code, minor
  unit and fund flag (``IsFund``);
* a code only in ``list-three`` is **withdrawn**: ``owl:deprecated true`` plus
  ``iso4217:withdrawalDate``, the date of its latest historic row, as SIX writes it
  ("2025-03", "1989 to 1990"). Historic codes are kept because historic records carry them.
  A code that appears in ``list-three`` and is still in ``list-one`` (EUR, after a
  territory dropped it) is current; a withdrawal is per country row, not per code.

Also written: ``ISO4217-alignment.ttl``, generated ``skos:exactMatch`` from each member
to the same code in the secondary copies: UN/CEFACT's ``unece:CurrencyCodeList`` and FIBO's
ISO 4217 currency identifiers. (IATA ONE Record's ``code-lists:CurrencyCode`` has no members
to link.)

This is reference data: SIX amends ISO 4217 several times a year, so refresh periodically
(see VERSIONING.md, "Refreshing reference data").

Usage:
    python scripts/download_iso4217.py --check         # has SIX published a change? (exit 1 if so)
    python scripts/download_iso4217.py                 # download and refresh
    python scripts/download_iso4217.py --from-dir D    # refresh from saved list-one.xml / list-three.xml
"""
import argparse
import hashlib
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTHORITATIVE = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models" / "authoritative-ontologies"
TARGET_DIR = AUTHORITATIVE / "ISO4217" / "current"
CODES_TTL = TARGET_DIR / "ISO4217-CurrencyCodes.ttl"
ALIGNMENT_TTL = TARGET_DIR / "ISO4217-alignment.ttl"
METADATA_TXT = TARGET_DIR / "METADATA.txt"
UNCEFACT_TTL = AUTHORITATIVE / "UNCEFACT" / "current" / "UNCEFACT-CodeLists.ttl"
FIBO_4217_RDF = AUTHORITATIVE / "FIBO" / "current" / "fibo" / "FND" / "Accounting" / "ISO4217-CurrencyCodes.rdf"

SIX_BASE = "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/"
SIX_PAGE = "https://www.six-group.com/en/products-services/financial-information/market-reference-data/data-standards.html"
LISTS = ("list-one.xml", "list-three.xml")

ONTOLOGY_IRI = URIRef("https://www.kairosflow.ai/ont/iso4217")
ALIGNMENT_IRI = URIRef("https://www.kairosflow.ai/ont/iso4217/alignment")
ISO = Namespace("https://www.kairosflow.ai/ont/iso4217#")
UNECE = Namespace("https://vocabulary.uncefact.org/")
FIBO_CUR = Namespace("https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/")
FIBO_REL = Namespace("https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/")
KAIROS_EXT = Namespace("https://kairos.cnext.eu/ext#")
README_URL = (
    "https://github.com/Cnext-eu/kairos-ontology-referencemodels/blob/main/"
    "kairos_ontology_referencemodels/ontology-reference-models/authoritative-ontologies/ISO4217/README.md"
)

ALPHA_RE = re.compile(r"^[A-Z]{3}$")
YEAR_RE = re.compile(r"\d{4}(?:-\d{2})?")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "kairos-referencemodels/refresh"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def latest_key(withdrawal: str) -> str:
    """Sort key for SIX withdrawal dates: the last date mentioned ("1989 to 1990" -> "1990")."""
    found = YEAR_RE.findall(withdrawal or "")
    return found[-1] if found else ""


def parse(raw_one: bytes, raw_three: bytes):
    one = ET.fromstring(raw_one)
    three = ET.fromstring(raw_three)
    current: dict[str, dict] = {}
    for row in one.iter("CcyNtry"):
        code = (row.findtext("Ccy") or "").strip()
        if not code:
            continue  # territories with no universal currency (e.g. ANTARCTICA)
        if not ALPHA_RE.match(code):
            raise ValueError(f"list-one: unexpected currency code {code!r}")
        name_el = row.find("CcyNm")
        entry = current.setdefault(code, {
            "name": (name_el.text or "").strip(),
            "number": (row.findtext("CcyNbr") or "").strip(),
            "minor": (row.findtext("CcyMnrUnts") or "").strip(),
            "fund": name_el is not None and name_el.get("IsFund", "").lower() == "true",
            "countries": set(),
        })
        entry["countries"].add((row.findtext("CtryNm") or "").strip())
    historic: dict[str, dict] = {}
    for row in three.iter("HstrcCcyNtry"):
        code = (row.findtext("Ccy") or "").strip()
        if not ALPHA_RE.match(code):
            raise ValueError(f"list-three: unexpected currency code {code!r}")
        candidate = {
            "name": (row.findtext("CcyNm") or "").strip(),
            "number": (row.findtext("CcyNbr") or "").strip(),
            "withdrawn": (row.findtext("WthdrwlDt") or "").strip(),
        }
        if code not in historic or latest_key(candidate["withdrawn"]) >= latest_key(historic[code]["withdrawn"]):
            historic[code] = candidate
    return one.get("Pblshd"), three.get("Pblshd"), current, historic


def build_codes(current, historic, published_one, published_three, snapshot) -> Graph:
    g = Graph()
    g.bind("iso4217", ISO)
    g.bind("dcterms", DCTERMS)
    g.bind("kairos-ext", KAIROS_EXT)
    version = f"{published_one}"
    g.add((ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    g.add((ONTOLOGY_IRI, RDFS.label, Literal("ISO 4217 currency codes")))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(version)))
    g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(published_one, datatype=XSD.date)))
    g.add((ONTOLOGY_IRI, DCTERMS.source, URIRef(SIX_BASE + "list-one.xml")))
    g.add((ONTOLOGY_IRI, DCTERMS.source, URIRef(SIX_BASE + "list-three.xml")))
    g.add((ONTOLOGY_IRI, RDFS.seeAlso, URIRef(README_URL)))
    g.add((ONTOLOGY_IRI, RDFS.comment, Literal(
        "ISO 4217 currency and fund codes from SIX, the ISO 4217 maintenance agency: list one "
        f"(current, published {published_one}) and list three (historic, published "
        f"{published_three}), retrieved {snapshot}. Codes, names, numeric codes, minor units and "
        "withdrawal dates are copied from the XML unchanged; the IRIs are Kairos-minted because "
        "SIX publishes no RDF. Withdrawn codes are kept, owl:deprecated, with their withdrawal "
        "date. Generated by scripts/download_iso4217.py; do not hand-edit."
    )))

    cls = ISO.CurrencyCode
    g.add((cls, RDF.type, OWL.Class))
    g.add((cls, RDFS.label, Literal("ISO 4217 currency code")))
    g.add((cls, RDFS.comment, Literal(
        "A currency or fund in ISO 4217. The alphabetic code is in rdf:value and is the join key "
        "to source data; iso4217:numericCode and iso4217:minorUnit come from the same SIX row."
    )))
    g.add((cls, KAIROS_EXT.isReferenceData, Literal(True)))
    g.add((cls, OWL.versionInfo, Literal(version)))
    g.add((cls, DCTERMS.source, URIRef(SIX_BASE + "list-one.xml")))
    g.add((cls, DCTERMS.description, Literal("ISO 4217 currency and fund codes, as maintained by SIX for ISO")))
    g.add((cls, RDFS.seeAlso, URIRef(README_URL)))
    g.add((KAIROS_EXT.isReferenceData, RDF.type, OWL.AnnotationProperty))

    props = {
        "numericCode": (XSD.string, "ISO 4217 numeric code, three digits with leading zeros kept (e.g. '008')."),
        "minorUnit": (XSD.integer, "Number of decimal places of the minor unit (absent where ISO 4217 says 'N.A.', e.g. XAU)."),
        "isFund": (XSD.boolean, "True for fund codes (SIX IsFund), e.g. CHE, USN, XAD."),
        "withdrawalDate": (XSD.string, "When ISO 4217 withdrew the code, as SIX writes it ('2025-03', '1989 to 1990'); the latest historic row."),
    }
    for local, (rng, comment) in props.items():
        prop = ISO[local]
        g.add((prop, RDF.type, OWL.DatatypeProperty))
        g.add((prop, RDFS.label, Literal(re.sub(r"(?<!^)(?=[A-Z])", " ", local).lower())))
        g.add((prop, RDFS.comment, Literal(comment)))
        g.add((prop, RDFS.domain, cls))
        g.add((prop, RDFS.range, rng))

    for code in sorted(set(current) | set(historic)):
        member = ISO[code]
        g.add((member, RDF.type, OWL.NamedIndividual))
        g.add((member, RDF.type, cls))
        g.add((member, RDF.value, Literal(code)))
        if code in current:
            row = current[code]
            g.add((member, RDFS.label, Literal(row["name"])))
            if row["number"]:
                g.add((member, ISO.numericCode, Literal(row["number"])))
            if row["minor"].isdigit():
                g.add((member, ISO.minorUnit, Literal(int(row["minor"]))))
            if row["fund"]:
                g.add((member, ISO.isFund, Literal(True)))
        else:
            row = historic[code]
            g.add((member, RDFS.label, Literal(row["name"])))
            if row["number"]:
                g.add((member, ISO.numericCode, Literal(row["number"])))
            g.add((member, OWL.deprecated, Literal(True)))
            g.add((member, ISO.withdrawalDate, Literal(row["withdrawn"])))
    return g


def build_alignment(codes: set[str]) -> tuple[Graph, dict[str, int]]:
    g = Graph()
    g.bind("skos", SKOS)
    g.bind("iso4217", ISO)
    counts = {}
    # IATA's code-lists:CurrencyCode is an open list with no members ("based on ISO 4217"),
    # so there is nothing to link; a hub can subclass it under iso4217:CurrencyCode instead.
    targets = {
        "UN/CEFACT unece:CurrencyCodeList": (UNCEFACT_TTL, UNECE.CurrencyCodeList, lambda gr, m: str(gr.value(m, RDF.value))),
        "FIBO fibo-fnd-acc-cur:CurrencyIdentifier": (FIBO_4217_RDF, FIBO_CUR.CurrencyIdentifier, lambda gr, m: str(gr.value(m, FIBO_REL.hasTag))),
    }
    for label, (path, cls, code_of) in targets.items():
        other = Graph().parse(path, format="xml" if path.suffix == ".rdf" else "turtle")
        linked = 0
        for member in other.subjects(RDF.type, cls):
            code = code_of(other, member)
            if code in codes:
                g.add((ISO[code], SKOS.exactMatch, member))
                linked += 1
        counts[label] = linked
    g.add((ALIGNMENT_IRI, RDF.type, OWL.Ontology))
    g.add((ALIGNMENT_IRI, RDFS.label, Literal("ISO 4217 to UN/CEFACT and FIBO currency alignment")))
    g.add((ALIGNMENT_IRI, RDFS.comment, Literal(
        "skos:exactMatch from each ISO 4217 member to the same alphabetic code in the secondary copies: "
        + ", ".join(f"{k} ({v})" for k, v in counts.items())
        + ". Generated by scripts/download_iso4217.py; do not hand-edit."
    )))
    return g, counts


def recorded() -> tuple[str | None, str | None]:
    if not METADATA_TXT.is_file():
        return None, None
    fields = dict(line.split(": ", 1) for line in METADATA_TXT.read_text(encoding="utf-8").splitlines()
                  if ": " in line and not line.startswith(" "))
    return fields.get("download_date"), (fields.get("sha256") or "").split(" ", 1)[0] or None


def write_metadata(snapshot, published_one, published_three, digests, sizes, n_current, n_withdrawn, n_fund, alignment):
    METADATA_TXT.write_text(f"""ISO 4217 Currency Codes - Download Information
==============================================

source: ISO 4217 lists published by SIX Financial Information AG, maintenance agency for ISO 4217
publisher: SIX Financial Information AG, on behalf of ISO and SNV (Swiss Association for Standardization)
source_page: {SIX_PAGE}
download_date: {snapshot}
version: {published_one} (list one publication date)
list_one: {SIX_BASE}list-one.xml (published {published_one}, {sizes['list-one.xml']} bytes, sha256 {digests['list-one.xml']})
list_three: {SIX_BASE}list-three.xml (published {published_three}, {sizes['list-three.xml']} bytes, sha256 {digests['list-three.xml']})
sha256: {hashlib.sha256((digests['list-one.xml'] + digests['list-three.xml']).encode()).hexdigest()} (combined; compared by --check)
members: {n_current} current ({n_fund} of them funds) + {n_withdrawn} withdrawn (owl:deprecated)
ontology_files:
  - list-one.xml, list-three.xml   (vendored source, unchanged)
  - ISO4217-CurrencyCodes.ttl      (generated; ontology IRI {ONTOLOGY_IRI})
  - ISO4217-alignment.ttl          (generated skos:exactMatch; ontology IRI {ALIGNMENT_IRI})
alignment: {", ".join(f"{k} {v}" for k, v in alignment.items())}
license: SIX provides the lists "online and free of charge" on ISO's behalf, and ISO states use
  of the codes is free of charge. No explicit redistribution clause was found on SIX's site;
  the content is facts (codes, names, numbers, dates). See README.md, section License.
generator: scripts/download_iso4217.py -- regenerates everything in current/; do not hand-edit.
deviations:
  - IRIs are Kairos-minted (https://www.kairosflow.ai/ont/iso4217#<code>): SIX publishes XML only.
  - One member per alphabetic code. Current codes take name, numeric code, minor unit and fund
    flag from list one; withdrawn codes (in list three, not in list one) take name, numeric code
    and withdrawal date from their latest historic row and are marked owl:deprecated.
  - Minor unit 'N.A.' is omitted, not encoded.
""", encoding="utf-8")


def archive_current(old_date: str) -> None:
    archive_dir = TARGET_DIR.parent / "archive" / old_date
    if archive_dir.exists():
        raise SystemExit(f"ERROR: {archive_dir} already exists; refusing to overwrite an archived snapshot")
    archive_dir.mkdir(parents=True)
    for path in sorted(TARGET_DIR.iterdir()):
        path.rename(archive_dir / path.name)
    print(f"Archived snapshot {old_date} -> archive/{old_date}/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from-dir", type=Path, help="use saved list-one.xml / list-three.xml instead of downloading")
    parser.add_argument("--snapshot-date", help="download date to record (default: today)")
    parser.add_argument("--check", action="store_true", help="only report whether SIX published a change (exit 1 if so)")
    parser.add_argument("--force", action="store_true", help="regenerate even when SIX is unchanged (after changing this script)")
    args = parser.parse_args()

    raws = {}
    for name in LISTS:
        if args.from_dir:
            raws[name] = (args.from_dir / name).read_bytes()
        else:
            print(f"Downloading {SIX_BASE}{name} ...")
            raws[name] = fetch(SIX_BASE + name)
    snapshot = args.snapshot_date or date.today().isoformat()
    digests = {k: hashlib.sha256(v).hexdigest() for k, v in raws.items()}
    combined = hashlib.sha256((digests["list-one.xml"] + digests["list-three.xml"]).encode()).hexdigest()
    old_date, old_digest = recorded()
    if args.check:
        if combined == old_digest:
            print(f"Up to date: SIX matches the vendored snapshot of {old_date}.")
            return 0
        print(f"SIX changed since the vendored snapshot of {old_date}: re-run without --check.")
        return 1
    if combined == old_digest and not args.force:
        print(f"Up to date: SIX matches the vendored snapshot of {old_date}; nothing written.")
        return 0

    published_one, published_three, current, historic = parse(raws["list-one.xml"], raws["list-three.xml"])
    if len(current) < 150:
        print(f"ERROR: list one has only {len(current)} codes; refusing to write", file=sys.stderr)
        return 1
    if old_date and old_date != snapshot:
        archive_current(old_date)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for name, raw in raws.items():
        (TARGET_DIR / name).write_bytes(raw)
    codes = build_codes(current, historic, published_one, published_three, snapshot)
    codes.serialize(CODES_TTL, format="turtle", encoding="utf-8")
    alignment, counts = build_alignment(set(current) | set(historic))
    alignment.serialize(ALIGNMENT_TTL, format="turtle", encoding="utf-8")
    withdrawn = set(historic) - set(current)
    funds = sum(1 for row in current.values() if row["fund"])
    write_metadata(snapshot, published_one, published_three, digests, {k: len(v) for k, v in raws.items()},
                   len(current), len(withdrawn), funds, counts)
    print(f"  current: {len(current)} ({funds} funds), withdrawn: {len(withdrawn)}")
    print(f"  alignment: {counts}")
    print(f"Wrote {CODES_TTL.name}, {ALIGNMENT_TTL.name}, {METADATA_TXT.name} (list one {published_one}, snapshot {snapshot})")
    print("Next: diff the result (a newly withdrawn code is deprecated, never removed), then run the test suite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
