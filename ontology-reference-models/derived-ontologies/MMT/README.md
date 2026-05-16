# MMT — Multi-Modal Transport Ontology

Modular ontology for international logistics and freight transport, based on the **UN/CEFACT Multi-Modal Transport Reference Data Model**.

## Structure

| Module | Namespace | Description |
|--------|-----------|-------------|
| **mmt.ttl** | `http://kairos.ai/ont/mmt#` | Root ontology — imports all domains; contains Dangerous Goods classes |
| **consignment/** | `http://kairos.ai/ont/mmt/consignment#` | Consignment, ConsignmentItem, TransportService, TransportLeg, Goods, Package |
| **cargo/** | `http://kairos.ai/ont/mmt/cargo#` | CargoItem, Weight, Dimension, Commodity, HandlingRequirement |
| **equipment/** | `http://kairos.ai/ont/mmt/equipment#` | FreightContainer, ReeferContainer, TankContainer, Pallet, SwapBody, Trailer |
| **transport-means/** | `http://kairos.ai/ont/mmt/transport-means#` | Vessel, Aircraft, RailVehicle, RoadVehicle, BargeVessel, Capacity |
| **route-network/** | `http://kairos.ai/ont/mmt/route-network#` | Route, Corridor, ServiceLoop, SailingSchedule, CutOffTime, TransitTime |
| **inland-transport/** | `http://kairos.ai/ont/mmt/inland-transport#` | InlandLeg, RailLeg, BargeLeg, RoadLeg, InlandCarrier, IntermodalConnection |
| **party/** | `http://kairos.ai/ont/mmt/party#` | Consignor, Consignee, Carrier, FreightForwarder, CustomsBroker, NotifyParty |
| **locations/** | `http://kairos.ai/ont/mmt/locations#` | Port, Airport, RailTerminal, Warehouse, BorderCrossing, DistributionCenter |
| **documents/** | `http://kairos.ai/ont/mmt/documents#` | BillOfLading, AirWaybill, CMR, RailConsignmentNote, CargoManifest, PackingList |
| **events/** | `http://kairos.ai/ont/mmt/events#` | Departure, Arrival, Loading, Discharge, Transfer, CustomsClearance |

## Design Principles

1. **Domain modules are self-contained** — each is a standalone `owl:Ontology` with its own namespace
2. **No cross-imports between domains** — the root `mmt.ttl` is the only file with `owl:imports`
3. **Properties follow their primary domain** — object/datatype properties are placed in the module of their primary domain class
4. **Cross-domain references use untyped ranges** — when a property references a class from another domain, the `rdfs:range` is omitted to avoid cross-imports

## Metadata

- **Version:** 1.0.0
- **Creator:** Kairos Ontology Team
- **Source:** UN/CEFACT Multi-Modal Transport Reference Data Model
- **Created:** 2026-01-06
- **Modified:** 2026-05-16

## Usage

Load `mmt.ttl` to get the complete ontology with all domain imports. Alternatively, load individual domain modules for focused use cases.
