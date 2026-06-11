# WCO Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-11

| Item | Details |
|---|---|
| What is it? | A customs and trade-facilitation ontology aligned with the WCO Data Model and related customs frameworks. |
| Main focus | Customs declarations, tariff and duty semantics, trade facilitation, trusted trader and border filing concepts. |
| Why selected in this blueprint | Covers customs/regulatory requirements that are essential in freight forwarding across borders. |
| Who is behind it | World Customs Organization (WCO). |
| Official site / references | https://www.wcoomd.org/datamodel |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/wco#` |
| Adoption context | Common baseline for customs digitalization and cross-border declaration interoperability. |
| Kairos modules used | `wco/customs`, `wco/trade-facilitation`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/WCO/README.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `CustomsDeclaration` | Formal declaration object submitted to customs authorities. | `declarationNumber`, `declarationStatus`, `lodgementDate` |
| `ImportDeclaration` | Declaration subtype for inbound goods clearance processing. | `countryOfOrigin`, `importProcedureCode`, `releaseDate` |
| `ExportDeclaration` | Declaration subtype for outbound goods compliance processing. | `destinationCountry`, `exportProcedureCode`, `exitOffice` |
| `TariffClassification` | Commodity classification used for duty/tax determination. | `hsCode`, `commodityDescription`, `dutyRate` |
| `DutyCalculation` | Computation entity for payable customs amounts. | `customsValue`, `dutyAmount`, `taxAmount` |
| `AEOCertification` | Trusted trader certification concept used in facilitation programs. | `aeoStatus`, `certificateNumber`, `validUntil` |
