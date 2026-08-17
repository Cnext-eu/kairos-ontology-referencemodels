# MMT — Multi-Modal Transport Ontology

Modular ontology for international logistics and freight transport, based on the **UN/CEFACT Multi-Modal Transport Reference Data Model**.

## Structure

| Module | Namespace | Description |
|--------|-----------|-------------|
| **mmt.ttl** | `https://www.kairosflow.ai/ont/mmt#` | Root ontology — imports all domains; contains Dangerous Goods classes |
| **consignment/** | `https://www.kairosflow.ai/ont/mmt/consignment#` | Consignment, ConsignmentItem, TransportService, TransportLeg, Goods, Package |
| **cargo/** | `https://www.kairosflow.ai/ont/mmt/cargo#` | CargoItem, Weight, Dimension, Commodity, HandlingRequirement |
| **equipment/** | `https://www.kairosflow.ai/ont/mmt/equipment#` | FreightContainer, ReeferContainer, TankContainer, Pallet, SwapBody, Trailer |
| **transport-means/** | `https://www.kairosflow.ai/ont/mmt/transport-means#` | Vessel, Aircraft, RailVehicle, RoadVehicle, BargeVessel, Capacity |
| **route-network/** | `https://www.kairosflow.ai/ont/mmt/route-network#` | Route, Corridor, ServiceLoop, SailingSchedule, CutOffTime, TransitTime |
| **inland-transport/** | `https://www.kairosflow.ai/ont/mmt/inland-transport#` | InlandLeg, RailLeg, BargeLeg, RoadLeg, InlandCarrier, IntermodalConnection |
| **party/** | `https://www.kairosflow.ai/ont/mmt/party#` | Consignor, Consignee, Carrier, FreightForwarder, CustomsBroker, NotifyParty |
| **locations/** | `https://www.kairosflow.ai/ont/mmt/locations#` | Port, Airport, RailTerminal, Warehouse, BorderCrossing, DistributionCenter |
| **documents/** | `https://www.kairosflow.ai/ont/mmt/documents#` | BillOfLading, AirWaybill, CMR, RailConsignmentNote, CargoManifest, PackingList |
| **events/** | `https://www.kairosflow.ai/ont/mmt/events#` | Departure, Arrival, Loading, Discharge, Transfer, CustomsClearance |

## Design Principles

1. **Domain modules are self-contained** — each is a standalone `owl:Ontology` with its own namespace
2. **A module imports what it domains on** — a property asserting `rdfs:domain` against a
   class from another module requires that module in this module's `owl:imports` closure,
   or the class is never typed here and cannot be anchored in the consuming data domain.
   The root `mmt.ttl` remains the aggregator and a leaf must never import it.
3. **Properties follow their primary domain** — object/datatype properties are placed in the module of their primary domain class
4. **Cross-domain references use untyped ranges** — when a property references a class
   from another domain, the `rdfs:range` may be left unimported. This is deliberate, not
   an oversight: the consumer derives each data domain's alignment pool from the
   transitive `owl:imports` closure, so importing every range target widens what a client
   hub is offered far beyond the real dependency. Principle 2 is the exception, because a
   dangling domain hides the property from its own class.

## Modeling Approach: Reification of BSP Code-Based Distinctions

The UN/CEFACT BSP D23B vocabulary uses a **flat, code-based architecture** — a single generic class
(e.g., `LogisticsTransportEquipment`, `TradeParty`, `TransportEvent`, `LogisticsLocation`) with
type/mode/function codes to distinguish subtypes. This ontology deliberately **reifies** those
code-based distinctions into OWL subclass hierarchies for improved semantic expressiveness and
reasoning support.

| BSP D23B Pattern | This Ontology's Approach |
|------------------|--------------------------|
| `LogisticsTransportEquipment` + `categoryCode` | `FreightContainer`, `ReeferContainer`, `TankContainer`, etc. |
| `TradeParty` + role properties | `Consignor`, `Consignee`, `Carrier`, `FreightForwarder`, etc. |
| `TransportEvent` + `typeCode` | `DepartureEvent`, `ArrivalEvent`, `LoadingEvent`, etc. |
| `LogisticsLocation` + `locationFunctionTypeCode` | `Port`, `Airport`, `RailTerminal`, etc. |
| `LogisticsTransportMeans` + `modeCode` | `Vessel`, `Aircraft`, `RailVehicle`, etc. |
| `TransportMovement` + `modeCode` | `InlandLeg`, `RailLeg`, `BargeLeg`, `RoadLeg` |
| `DangerousGoods` + `hazardClassificationId` | `ExplosiveGoods`, `FlammableGas`, etc. (from UN TDG) |

This design choice enables OWL-DL reasoning, SHACL validation, and SPARQL queries that would
otherwise require complex FILTER expressions on code values. Classes that are directly confirmed
BSP D23B entities are noted in their `rdfs:comment`; reified subclasses cite their source code
list or standard.

## Metadata

- **Version:** 1.0.0
- **Creator:** Kairos Ontology Team
- **Source:** UN/CEFACT Multi-Modal Transport Reference Data Model
- **Created:** 2026-01-06
- **Modified:** 2026-05-16

## Usage

Load `mmt.ttl` to get the complete ontology with all domain imports. Alternatively, load individual domain modules for focused use cases.
