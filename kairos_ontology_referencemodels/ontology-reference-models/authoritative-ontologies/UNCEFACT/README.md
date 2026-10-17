# UN/CEFACT Code Lists — Authoritative Extract

Vendored extract of the UNECE code lists that UN/CEFACT publishes in its
[JSON-LD Web Vocabulary](https://vocabulary.uncefact.org/). Generated — **do not hand-edit
the `.ttl` files**; re-run `scripts/download_uncefact_codelists.py` instead.

## Tier

**Authoritative.** UN/CEFACT publishes these lists natively as RDF, so they enter
`authoritative-ontologies/` rather than being re-authored as a derived ontology (gh#120).
It is an *extract*, not a full mirror: the vocabulary is one ~8.7 MB document holding the
whole UN/CEFACT trade data model, and only the code lists below are vendored. Every
vendored triple is copied unchanged and keeps its `https://vocabulary.uncefact.org/` IRI.

## Contents

| File | Ontology IRI | Purpose |
|---|---|---|
| `UNCEFACT-CodeLists.ttl` | `https://www.kairosflow.ai/ont/uncefact/code-lists-vendor-extract` | Vendor extract |
| `UNCEFACT-CodeLists.owl-patch.ttl` | `https://www.kairosflow.ai/ont/uncefact/code-lists` | Generated OWL typing; imports the extract. **Hubs import this IRI.** |
| `UNCEFACT-IATA-alignment.ttl` | `https://www.kairosflow.ai/ont/uncefact/iata-alignment` | Generated `skos:exactMatch` from IATA ONE Record codes to these codes |
| `METADATA.txt` | — | Provenance: source, snapshot date, checksum, deviations |

| UN/CEFACT class | Recommendation | Codes |
|---|---|---|
| `unece:TransportModeCodeList` | Rec 19 — Codes for Modes of Transport | 10 |
| `unece:UnitMeasureCode` | Rec 20 — Codes for Units of Measure | 1,828 |
| `unece:PackageTypeCodeList` | Rec 21 — Codes for Types of Cargo, Packages and Packaging Materials | 405 |

Each code is an instance of its list's class, with the code in `rdf:value` and its name
in `rdfs:comment` (the patch copies the name to `rdfs:label`):

```turtle
<https://vocabulary.uncefact.org/TransportModeCodeList#4> a unece:TransportModeCodeList ;
    rdf:value "4" ;
    rdfs:comment "Air transport" .
```

`rdf:value` is the join key to source data.

### Provenance in the graph

A consumer does not need this README to know what it imported. The patch stamps the
ontology and each code-list class with:

| Annotation | Value |
|---|---|
| `kairos-ext:isReferenceData` | `true` on each code-list class: the toolkit's existing code-list marker (`ref_` table, SCD type 1) |
| `owl:versionInfo` | the snapshot date, e.g. `"2026-10-17"`. Upstream publishes no version, so the date is the version, and it sorts. |
| `dcterms:source` | `https://vocabulary.uncefact.org/` |
| `rdfs:seeAlso` | this README |
| `dcterms:description` | on each class, the UNECE recommendation it publishes; on the ontology, the snapshot date and dump checksum |

`tests/test_reference_data.py` fails if `METADATA.txt`, the extract header and the patch
disagree on the snapshot date, or if a class loses one of these annotations.

## Version and refresh

This is **reference data**: UN/CEFACT revises these lists (Rec 20 several times a
decade, Rec 21 and Rec 19 rarely), so the snapshot goes stale unless it is refreshed.
UN/CEFACT does not version the endpoint; it serves one dump that is updated in place, so
a snapshot is identified by its download date and the sha256 of the full dump, both in
`METADATA.txt`.

```sh
python scripts/download_uncefact_codelists.py --check   # exit 1 if upstream changed
python scripts/download_uncefact_codelists.py           # refresh
```

A refresh moves the previous snapshot to `archive/<download date>/`, rewrites the
extract, the OWL patch and `METADATA.txt`, and regenerates the IATA alignment. It writes
nothing when upstream is unchanged. Diff the result before committing: a code that
disappears is a breaking change for any hub that stores it. The CI workflow
`reference-data-freshness` runs `--check` monthly. See `VERSIONING.md`, "Refreshing
reference data".

## Relation to the IATA code lists

`authoritative-ontologies/IATA/` ships `code-lists:ModeCode` (an air-cargo profile of
Rec 19) and `code-lists:MeasurementUnitCode` (40 codes, based on Rec 20). These lists are
the full standards-body lists behind both. Where both exist, a hub links to these.

`UNCEFACT-IATA-alignment.ttl` links them: all 10 `ModeCode` individuals (matched on the
`(N)` code in their comment, so it includes `ModeCode#MAIL`, which IATA's own `owl:oneOf`
leaves out), and 36 of the 40 `MeasurementUnitCode` individuals (matched on local name).
`KBQ`, `MBQ`, `TBQ` and `NDA` are IATA codes with no Rec 20 counterpart and stay
unlinked. The links are `skos:exactMatch`, not `owl:sameAs`: IATA's `ModeCode` is a
closed `owl:oneOf` that omits Mail, and `owl:sameAs` would let a reasoner merge Mail into
one of the other modes.

## Where it binds in Kairos

Routed to the logistics `reference-data` domain as `import_policy: reference-only`: the
accelerator never bulk-imports it. Per `blueprints/patterns/governed-code-list`, a hub
whose governed code-list class stands for one of these lists links to these members
instead of re-ingesting the list from the UNECE PDFs.

## License

**Intended licence: CC BY 4.0, attribution to UNECE / UN/CEFACT. Written confirmation from
UNECE is still outstanding.** Checked 2026-10-17:

| Source | What it says |
|---|---|
| UN/CEFACT's successor vocabulary site, hosted by the UN (`opensource.unicc.org/un/unece/uncefact/vocab-bsp`, "© 2026 United Nations Economic Commission for Europe") | "All UN/CEFACT standards are free to use under CC By 4.0 license." |
| UN/CEFACT licence on its published standards (ScanCode `LicenseRef-scancode-un-cefact-2016`) | Copying and distribution permitted, including supporting derivative works, provided the copyright notice is retained; permissions perpetual. |
| `vocabulary.uncefact.org/home/terms` (the endpoint this module downloads from) | Only the generic UN website terms: personal, non-commercial use, "without any right to resell or redistribute", "subject to … more specific restrictions that may apply to specific Material". |
| `github.com/uncefact/spec-JSONLD` (the endpoint's source repository) | No licence file. |

The two UN/CEFACT-specific statements both permit redistribution, and CC BY 4.0 is the
current one. The generic website terms predate it and are not specific to the standards.
Until UNECE confirms that CC BY 4.0 covers the code lists served at
`vocabulary.uncefact.org`, treat this module as **CC BY 4.0 with attribution, pending
confirmation**. Attribution: *UNECE Recommendations 19, 20 and 21, © United Nations
Economic Commission for Europe, from the UN/CEFACT Web Vocabulary
(https://vocabulary.uncefact.org/), extract of the snapshot recorded in METADATA.txt.*

To close this, ask UNECE in the vocab-bsp repository, which invites issues:
https://opensource.unicc.org/un/unece/uncefact/vocab-bsp/-/issues.

## Upstream is changing shape

UN/CEFACT is rebuilding the vocabulary in `vocab-bsp`: code lists become SKOS concept
schemes with path IRIs (`…/party-role/consignee`), Rec 20's facet lists fold into one
master list, and `skos:notation` carries the code. Its code-list strategy commits to
keeping today's fragment IRIs (`…/TransportModeCodeList#4`) resolvable as `owl:sameAs`
aliases, so IRIs a hub stores stay valid. But once the live endpoint switches over, the
extractor's selection by `@type unece:<List>` will find nothing. The script then stops
with "a code list came back empty" instead of writing an empty snapshot. Adapting the
extractor is a deliberate change at that point, not a routine refresh.
