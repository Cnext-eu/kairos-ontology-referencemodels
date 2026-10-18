# ISO 4217 Currency Codes Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-10-18

| Item | Details |
|---|---|
| What is it? | **Reference data**, not a data model: the ISO 4217 currency and fund codes, as published by the standard's maintenance agency. |
| Main focus | 178 current codes with numeric code, minor unit and fund flag; 129 withdrawn codes kept as `owl:deprecated` with their withdrawal date. |
| Why selected in this blueprint | Every RDF copy of ISO 4217 lags the standard (UN/CEFACT's lacked `XAD`, `XCG`, `ZWG` and still listed `ANG`, `BGN`, `CUC`, `ZWL` in October 2026). The maintenance agency is the only current source (gh#128). |
| Who is behind it | ISO, through SIX Financial Information AG as the ISO 4217 maintenance agency (with SNV, the Swiss Association for Standardization). |
| Official site / references | https://www.six-group.com/en/products-services/financial-information/market-reference-data/data-standards.html (list one: current; list three: historic) |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/iso4217` (hubs import this); members `iso4217:<code>`, e.g. `iso4217:EUR`, class `iso4217:CurrencyCode` |
| Adoption context | ISO 4217 is the currency code of every freight invoice, charge and rate; UN/CEFACT Rec 9, IATA ONE Record and FIBO all reference it. |
| Kairos modules used | **None — authoritative reference data, not a Kairos-authored module.** Generated from the vendored SIX XML by `scripts/download_iso4217.py`; IRIs are Kairos-minted because SIX publishes no RDF. |

## Which kind of code list is this?

**Kind 1** (shipped with its members). Bind the hub's governed currency class to it:
`iso4217:CurrencyCode rdfs:subClassOf hub:CurrencyCode`, joining on `rdf:value` (the alphabetic
code; numeric codes are reused by ISO, e.g. `XCG` took `532` from `ANG`). See
`blueprints/patterns/governed-code-list`, "Where the values live".

## Reference data — refreshed, not released

SIX amends ISO 4217 several times a year. The version (`owl:versionInfo`) is the list-one
publication date. Refresh with the script; never hand-edit:

```bash
python scripts/download_iso4217.py --check   # exit 1 if SIX published a change
python scripts/download_iso4217.py           # refresh
```

A newly withdrawn code is marked `owl:deprecated`, never removed, so a refresh does not break
hubs that stored it. The monthly `reference-data-freshness` workflow opens a PR when SIX
changed.

## Internal reference

- `ontology-reference-models/authoritative-ontologies/ISO4217/README.md`
- `ontology-reference-models/VERSIONING.md`, "Refreshing reference data"
