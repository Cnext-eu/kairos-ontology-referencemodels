# Supply Chain Integration Ontology

**Cross-domain bridge properties for logistics supply chain integration**

## Purpose

This module provides **cross-standard object properties** that link classes
from different ontology standards (DCSA, MMT, BSP, TIC, IMO, WCO, Sustainability).
It does not define new classes — it only bridges existing classes across standards.

Within a single standard, cross-module properties already exist (e.g., MMT
consignment → MMT equipment). This module covers relationships that span
**different** standards.

## What's included?

| From Standard | To Standard | Relationship |
|---------------|-------------|-------------|
| DCSA Booking | MMT Consignment | `bookedConsignment` |
| DCSA Booking | BSP Commercial | `underAgreement` |
| MMT Consignment | BSP Financial | `invoicedVia` / `chargesForConsignment` |
| MMT TransportService | DCSA Schedule | `scheduledVia` |
| DCSA Container | TIC Handling | `handledAtTerminal` |
| IMO PortCall | TIC Terminal | `callsAtTerminal` |
| IMO BerthStay | TIC Berth | `berthsAt` |
| MMT CargoItem | IMO DangerousGoods | `classifiedAsDangerousGoods` |
| MMT Consignment | WCO Customs | `requiresCustomsDeclaration` |
| DCSA Event | MMT Consignment | `eventRelatesToConsignment` |
| DCSA Event | IMO Vessel | `eventRelatesToVessel` |
| TIC TerminalEvent | DCSA Container | `eventRelatesToEquipment` |
| IMO Vessel | Sustainability Carbon | `hasCIIRating` |
| IMO Vessel | Sustainability Carbon | `hasEmissionReport` |
| MMT TransportService | Sustainability Energy | `hasEnergyConsumption` |
| MMT Consignment | Sustainability Carbon | `hasCarbonFootprint` |
| MMT CargoItem | WCO Customs | `declaredAsGoodsItem` |
| DCSA TransportDocument | BSP Documents | `correspondsToBillOfLading` |

## Design principles

1. **Bridge, don't duplicate** — only define properties that don't exist within
   any single standard's modules.
2. **Selective imports** — import only the specific modules whose classes appear
   in `rdfs:domain` or `rdfs:range`.
3. **Explicit inverses** — bidirectional relationships declare `owl:inverseOf`.
4. **Neutral namespace** — `https://www.kairosflow.ai/ont/supply-chain#` is
   standard-agnostic.

## Changelog

### v1.1.0 (2026-06-13)
- Added Sustainability bridges: CIIRating, EmissionReport, EnergyConsumption, CarbonFootprint
- Added WCO GoodsItem bridge: declaredAsGoodsItem (CargoItem → GoodsItem)
- Added document bridge: correspondsToBillOfLading (TransportDocument → BillOfLading)
- Added missing imports: transport-documents, bsp/documents, sustainability/carbon, sustainability/energy
- Fixed syntax error (stray backtick on classifiedAsDangerousGoods)

### v1.0.0 (2026-05-31)
- Initial release with 12 cross-standard bridge properties

## Version

See [VERSION](VERSION) — currently **1.1.0**.
