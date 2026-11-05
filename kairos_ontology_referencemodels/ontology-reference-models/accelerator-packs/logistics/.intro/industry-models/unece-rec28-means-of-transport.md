# UNECE Rec 28 Means-of-Transport Types Model Sheet

> **Document Control**
> **Framework:** Kairos Ontology Toolkit
> **Document date:** 2026-11-05

| Item | Details |
|---|---|
| What is it? | **Reference data**, not a data model: UNECE Recommendation 28, Codes for Types of Means of Transport, Revision 4.2 (2018). |
| Main focus | 282 codes for vessels, trains, road vehicles and aircraft, hierarchical (342 Van, light → 34 Van), each tied to its Rec 19 transport mode. |
| Why selected in this blueprint | Hubs need generic vehicle types (31 Truck, 33 Tractor, 34 Van, 342 Van, light) that the UN/CEFACT vocabulary's copy (134 four-digit codes) lacks. |
| Who is behind it | UN/CEFACT, United Nations Economic Commission for Europe. |
| Official site / references | https://unece.org/trade/uncefact/cl-recommendations (the Rev 4.2 code list, XLS) |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/unece-rec28` (hubs import this); members `rec28:<code>`, class `rec28:TransportMeansTypeCode` |
| Adoption context | Used wherever a message types the means of transport: EDIFACT, UN/CEFACT MMT-RDM, customs and inland-navigation reporting. |
| Kairos modules used | **None — authoritative reference data.** Built from the vendored XLS by `scripts/build_unece_rec28.py`; IRIs are Kairos-minted because UNECE publishes the full list as XLS only. |

## Which kind of code list is this?

**Kind 1** (shipped with its members). Rec 28 types vehicles and vessels; it has no codes for
trailers on their own. Equipment classes (trailer, semi-trailer, chassis, swap body) come from
UNTDED 8053 in the UN/CEFACT extract, and a finer trailer typology is client-owned (kind 3),
linked to 8053 by `skos:broadMatch`. See `blueprints/patterns/governed-code-list`.

## Refresh

Rebuilt only when UNECE publishes a new revision: replace the XLS and run
`uv run --with xlrd python scripts/build_unece_rec28.py`.

## Internal reference

- `ontology-reference-models/authoritative-ontologies/UNECE-Rec28/README.md`
