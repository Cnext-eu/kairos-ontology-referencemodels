# UN/CEFACT Code Lists Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-10-17

| Item | Details |
|---|---|
| What is it? | **Reference data**, not a data model: the members of three UNECE code lists, as published by UN/CEFACT in its JSON-LD Web Vocabulary. |
| Main focus | Transport mode (Rec 19, 10 codes), unit of measure (Rec 20, 1,828 codes), package type (Rec 21, 405 codes). |
| Why selected in this blueprint | Hubs re-ingested these lists from the UNECE PDFs, each on its own, and the copies drifted (gh#120). They are maintained by a standards body, so the reference models ship the members once for every hub. |
| Who is behind it | UN/CEFACT (United Nations Centre for Trade Facilitation and Electronic Business), UNECE. |
| Official site / references | https://vocabulary.uncefact.org/ ; source repository https://github.com/uncefact/spec-JSONLD |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/uncefact/code-lists` (hubs import this); terms keep their `https://vocabulary.uncefact.org/` IRIs, e.g. `unece:TransportModeCodeList#4` |
| Adoption context | Rec 19/20/21 are the code lists behind EDIFACT, UN/CEFACT MMT-RDM, WCO (T020 = Rec 19), PEPPOL, and IATA ONE Record's `ModeCode` / `MeasurementUnitCode`. |
| Kairos modules used | **None — an authoritative extract, not a Kairos-authored module.** Vendored under `authoritative-ontologies/UNCEFACT/` by script and resolved through `catalog-v001.xml`. |

## Reference data — refreshed, not released

UN/CEFACT revises these lists in place and serves one unversioned dump, so a snapshot's
version is its **download date**. That date is the `owl:versionInfo` on the ontology and on
each code-list class. Each class also carries `kairos-ext:isReferenceData true`, the
`dcterms:source` it was downloaded from, and an `rdfs:seeAlso` link to the module README.

**Refresh periodically with the script.** Never hand-edit:

```bash
python scripts/download_uncefact_codelists.py --check   # exit 1 if upstream changed
python scripts/download_uncefact_codelists.py           # refresh
```

The monthly `reference-data-freshness` workflow opens a PR when upstream changed. A
**removed** code is breaking for hubs that store it.

## How a hub uses it

`reference-only` in `manifest.yaml`: the accelerator never bulk-imports it. The hub's
governed code-list class takes the shared list in, and the hub joins source data on each
code's `rdf:value` (`blueprints/patterns/governed-code-list`):

```turtle
hub:TransportModeCode a owl:Class .
unece:TransportModeCodeList rdfs:subClassOf hub:TransportModeCode .
```

The derived transport-mode slots (DCSA, MMT, BSP, TIC, WCO) point here with
`rdfs:seeAlso`, and each states how its standard's values map to Rec 19.
`UNCEFACT-IATA-alignment.ttl` links IATA ONE Record's codes to these with
`skos:exactMatch`.

## Internal reference

- `ontology-reference-models/authoritative-ontologies/UNCEFACT/README.md`
- `ontology-reference-models/VERSIONING.md`, "Refreshing reference data"
