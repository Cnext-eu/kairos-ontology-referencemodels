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

## Version

UN/CEFACT does not version the endpoint; it serves one dump that is updated in place. A
snapshot is identified by its download date and the sha256 of the full dump, both in
`METADATA.txt`. To refresh:

```sh
python scripts/download_uncefact_codelists.py
```

Diff the result before committing: a code that disappears is a breaking change for any
hub that stores it.

## Relation to the IATA code lists

`authoritative-ontologies/IATA/` ships `code-lists:ModeCode` (an air-cargo profile of
Rec 19) and `code-lists:MeasurementUnitCode` (96 codes, based on Rec 20). These lists are
the full standards-body lists behind both. Where both exist, a hub links to these.

## Where it binds in Kairos

Routed to the logistics `reference-data` domain as `import_policy: reference-only`: the
accelerator never bulk-imports it. Per `blueprints/patterns/governed-code-list`, a hub
whose governed code-list class stands for one of these lists links to these members
instead of re-ingesting the list from the UNECE PDFs.

## License

UN/CEFACT publishes no licence file with the vocabulary (the
[source repository](https://github.com/uncefact/spec-JSONLD) has none). UNECE makes its
trade facilitation recommendations and their code lists available free of charge. The
exact redistribution terms are **unconfirmed** — see gh#120 before a release ships this
module.
