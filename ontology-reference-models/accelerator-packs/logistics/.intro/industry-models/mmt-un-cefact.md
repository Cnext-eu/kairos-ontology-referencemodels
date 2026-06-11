# MMT (UN/CEFACT) Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-11

| Item | Details |
|---|---|
| What is it? | The UN/CEFACT Multi-Modal Transport reference model, modularized into OWL domains. |
| Main focus | Consignment, cargo, equipment, route-network, inland transport, party, locations, documents, and transport events. |
| Why selected in this blueprint | Provides multimodal transport semantics beyond deep-sea container flow, including inland and intermodal coverage needed by freight forwarders. |
| Who is behind it | UN/CEFACT (United Nations Centre for Trade Facilitation and Electronic Business). |
| Official site / references | https://unece.org/trade/uncefact |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/mmt#` |
| Adoption context | Widely referenced in trade-facilitation and logistics data harmonization programs across borders and transport modes. |
| Kairos modules used | `mmt/consignment`, `mmt/cargo`, `mmt/equipment`, `mmt/route-network`, `mmt/inland-transport`, `mmt/party`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/MMT/README.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `Consignment` | Core multimodal shipment object across transport legs and parties. | `consignmentIdentifier`, `hasConsignmentItem`, `consignmentStatus` |
| `CargoItem` | Physical cargo unit with commodity and handling semantics. | `grossWeight`, `hasCommodity`, `hasHandlingRequirement` |
| `TransportEquipment` | Equipment used in movement, such as container/trailer types. | `equipmentIdentifier`, `equipmentTypeCode`, `equipmentStatus` |
| `TransportLeg` | Segment of a route executed by a specific mode/carrier context. | `modeCode`, `departureLocation`, `arrivalLocation` |
| `Route` | Network path abstraction used for planning and execution references. | `routeCode`, `hasLeg`, `plannedTransitTime` |
| `InlandLeg` | Inland rail/barge/road movement segment in intermodal chains. | `inlandMode`, `inlandCarrier`, `handoverPoint` |
