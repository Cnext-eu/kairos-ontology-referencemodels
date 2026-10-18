# UN/CEFACT Code Lists — Authoritative Extract

Vendored extract of the UNECE code lists that UN/CEFACT publishes in its
[JSON-LD Web Vocabulary](https://vocabulary.uncefact.org/). Generated — **do not hand-edit
the `.ttl` files**; re-run `scripts/download_uncefact_codelists.py` instead.

## Tier

**Authoritative.** UN/CEFACT publishes these lists natively as RDF, so they enter
`authoritative-ontologies/` rather than being re-authored as a derived ontology (gh#120).
It is an *extract*, not a full mirror. The root document is ~8.7 MB holding the whole
UN/CEFACT trade data model, and the UN/LOCODE locations are another ~39 MB; only the code
lists below are vendored, from five upstream documents. Every vendored triple is copied
unchanged and keeps its `https://vocabulary.uncefact.org/` IRI.

## Contents

| File | Ontology IRI | Purpose |
|---|---|---|
| `UNCEFACT-CodeLists.ttl` | `https://www.kairosflow.ai/ont/uncefact/code-lists-vendor-extract` | Vendor extract |
| `UNCEFACT-CodeLists.owl-patch.ttl` | `https://www.kairosflow.ai/ont/uncefact/code-lists` | Generated OWL typing; imports the extract. **Hubs import this IRI.** |
| `UNCEFACT-IATA-alignment.ttl` | `https://www.kairosflow.ai/ont/uncefact/iata-alignment` | Generated `skos:exactMatch` from IATA ONE Record codes to these codes |
| `METADATA.txt` | — | Provenance: source documents, snapshot date, checksums, deviations |

| UN/CEFACT class | What it is | Codes | Upstream document |
|---|---|---|---|
| `unece:TransportModeCodeList` | Rec 19 — Codes for Modes of Transport | 10 | `/` (BSP) |
| `unece:UnitMeasureCode` | Rec 20 — Codes for Units of Measure | 1,828 | `/` (BSP) |
| `unece:PackageTypeCodeList` | Rec 21 — Codes for Types of Cargo, Packages and Packaging Materials | 405 | `/` (BSP) |
| `unece:DeliveryTermsCodeList` | Delivery terms (UNTDED 4053): the 11 ICC Incoterms 2020 abbreviations (Rec 5) + 2 generic codes | 13 | `/` (BSP) |
| `unece:TransportMovementStageCodeList` | Transport stage (UNTDED 8051): 10 pre-carriage, 20 main carriage, 30 on-carriage, … | 30 | `/` (BSP) |
| `unece:CurrencyCodeList` | Currency codes (UNTDED 6345): ISO 4217, Rec 9. **Secondary:** lags ISO; bind `iso4217:CurrencyCode` (`authoritative-ontologies/ISO4217/`) instead | 179 | `/` (BSP) |
| `unece:PartyRoleCodeList` | Party roles (UNTDED 3035): CZ consignor, CN consignee, CA carrier, N1 notify party, … | 625 | `/` (BSP) |
| `unlcdv:Country` | ISO 3166-1 alpha-2 countries, as published with UN/LOCODE (Rec 16) | 249 | `/unlocode-countries` |
| `unlcdv:Subdivision` | ISO 3166-2 subdivisions, as published with UN/LOCODE (Rec 16) | 4,669 | `/unlocode-subdivisions` |
| `unlcdv:Function` | UN/LOCODE function classifiers (Rec 16) | 11 | `/unlocode-functions` |

The UN/LOCODE classes and their properties (`unlcdv:countryCode`, `unlcdv:subdivisionType`,
…) come from the small `/unlocode-vocab` document, vendored whole. A subdivision links to its
country with `unlcdv:countryCode`. The 115,928 UN/LOCODE locations themselves (`/unlocode`)
are **not** vendored: at ~39 MB they would dwarf the rest. The UN/LOCODE status indicators
are not published by the endpoint at all.

Three upstream subdivisions (`SNDB `, `SOGE `, `THS `) have a trailing space in their
IRI, which makes them invalid IRIs. They are skipped rather than corrected, because
correcting them would mint IRIs UN/CEFACT never published. `METADATA.txt` lists them.

**Errata.** A wrong *literal* upstream is corrected in the extract, from the `ERRATA` table in
the generator, and listed under `errata` in `METADATA.txt`. Today there is one:
`unlocode-countries#FR` is labelled "Saint-Pierre = PM FSP" upstream (a UN/LOCODE "="
cross-reference row taken as France's name) and ships as "FRANCE". A correction applies only
while upstream still carries exactly the wrong value. When upstream fixes it, the refresh
reports the erratum as obsolete; if upstream changes it to anything else, the refresh fails
for review. IRIs are never corrected this way.

Each code is an instance of its list's class, with the code in `rdf:value` and its name
in `rdfs:label` or `rdfs:comment` (the patch copies a comment to `rdfs:label` where the
code has no label):

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

This is **reference data**: UN/CEFACT revises these lists (UN/LOCODE twice a
year, Rec 20 several times a decade, the others rarely), so the snapshot goes stale unless
it is refreshed. UN/CEFACT does not version the endpoint; it serves documents updated in
place, so a snapshot is identified by its download date and the sha256 of each document, all in
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

## UN/LOCODE locations: load in the hub

The ~116,000 UN/LOCODE locations are **reference data that this module deliberately does
not vendor**. At ~39 MB, and re-released twice a year, they would dwarf everything else and
ride along in every hub that imports the module. They are also rows a hub queries and joins,
not a small enumeration it binds classes to. They belong in the hub as a **reference table**.

What ships here is the **target shape**, so every hub loads to the same class and IRIs:

- the class `unlcdv:UNLOCODE`. In the OWL patch it carries
  `kairos-ext:isReferenceData true`, `dcterms:source <https://vocabulary.uncefact.org/unlocode>`,
  and the loading instruction in `dcterms:description`. It has no members;
- its properties `unlcdv:countryCode` (→ `unlcdv:Country`),
  `unlcdv:countrySubdivision` (→ `unlcdv:Subdivision`) and `unlcdv:functions`
  (→ `unlcdv:Function`), whose targets **do** ship here.

| Column (suggested) | From the JSON-LD dump | Notes |
|---|---|---|
| `locode` (key) | `rdf:value`, e.g. `BEANR` | 5 characters: ISO 3166-1 country + 3-character location |
| `iri` | `@id`, e.g. `https://vocabulary.uncefact.org/unlocode#BEANR` | Stable upstream IRI |
| `name` | `rdfs:label` | |
| `country_code` | `unlcdv:countryCode` → `unlcdv:Country` | Join to the shipped countries |
| `subdivision_code` | `unlcdv:countrySubdivision` → `unlcdv:Subdivision` | Absent for ~12% of locations |
| `function_codes` | `unlcdv:functions` → `unlcdv:Function` | Several per location (1 = port, 4 = airport, …) |
| `latitude`, `longitude` | `geo:lat`, `geo:long` | Absent for ~20% of locations |
| `status` | — | Only in the official UNECE CSV release; the endpoint does not serve it |

**Sources.** `https://vocabulary.uncefact.org/unlocode` (JSON-LD, `Accept:
application/ld+json`), or the official UNECE UN/LOCODE CSV release, which also carries the
Status column and the change indicators. Reload on each UN/LOCODE release (twice a year:
`YYYY-1`, `YYYY-2`); the release vendored alongside is in `METADATA.txt`
(`upstream_release`).

The derived modules' location-code text fields (`unLocationCode`, `unlocode`) hold the
same 5-character code. Loading the locations is ordinary source binding in the hub: this
is a **kind 2** list (`blueprints/patterns/governed-code-list`, "Where the values live"),
and no tool generates its loader.

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
confirmation**. Attribution: *UNECE code lists (Recommendations 5, 9, 16, 19, 20 and 21, and UNTDED
code lists), © United Nations Economic Commission for Europe, from the UN/CEFACT Web Vocabulary
(https://vocabulary.uncefact.org/), extract of the snapshot recorded in METADATA.txt.*

**ISO 3166 and ISO 4217.** The country, subdivision and currency codes are ISO codes,
republished here as UNECE publishes them (Rec 3, Rec 9, Rec 16). ISO has stated that use
of the codes themselves is free of charge; the full standards, and ISO's own databases,
are sold separately and are not vendored. **ISO 6346** (container size/type codes) is
deliberately absent: neither ISO nor BIC publishes a free-reuse statement for that list.
It is therefore a **kind 3** list: the hub's governed equipment-type list is its own (often a
TMS master table) and carries the ISO 6346 code as an attribute, in the derived properties
BSP `commercial:equipmentSizeType`, DCSA `equipment:isoEquipmentCode` and
`demurrage-detention:isoEquipmentCode`, and MMT `equipment:equipmentSizeType`.

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
