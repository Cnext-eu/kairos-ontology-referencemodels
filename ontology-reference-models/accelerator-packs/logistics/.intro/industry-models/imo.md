# IMO Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-11

| Item | Details |
|---|---|
| What is it? | A maritime ontology aligned with IMO Compendium, FAL Convention, and IMDG references. |
| Main focus | Vessel registry, dangerous goods, port call lifecycle, maritime parties, and maritime locations. |
| Why selected in this blueprint | Provides authoritative maritime and dangerous-goods semantics for vessel and port-call domains. |
| Who is behind it | International Maritime Organization (IMO). |
| Official site / references | https://www.imo.org |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/imo#` |
| Adoption context | Core reference body for global maritime safety, facilitation, and dangerous-goods standards. |
| Kairos modules used | `imo/vessel-registry`, `imo/dangerous-goods`, `imo/port-call`, `imo/party`, `imo/locations`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/IMO/README.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `Vessel` | Maritime transport asset identified by IMO-aligned registry semantics. | `imoNumber`, `flagState`, `vesselType` |
| `PortCall` | Arrival/departure lifecycle event of a vessel at a port. | `arrivalDateTime`, `departureDateTime`, `portCallStatus` |
| `BerthStay` | Time-bounded vessel stay at a specific berth location. | `berthStartTime`, `berthEndTime`, `berthsAt` |
| `DangerousGoodsItem` | Hazardous cargo unit classified under IMDG concepts. | `unNumber`, `hazardClass`, `packingGroup` |
| `ClassificationSociety` | Maritime authority/organization responsible for vessel class oversight. | `societyCode`, `classificationStatus`, `issuesCertificate` |
| `Port` | Maritime location entity used in voyages, calls, and navigation context. | `unlocode`, `portName`, `countryCode` |
