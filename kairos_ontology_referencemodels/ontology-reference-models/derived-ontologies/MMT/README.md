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

1. **Each domain module is a standalone `owl:Ontology`** with its own namespace
2. **A module imports every module it references** — if a property asserts `rdfs:domain`
   or `rdfs:range` against a class from another module, that module must be in this
   module's transitive `owl:imports` closure. Enforced by `validate_structure.py`
   check 10.
3. **Properties follow their primary domain** — object/datatype properties are placed in the module of their primary domain class
4. **The root `mmt.ttl` is a pure aggregator** — it declares no terms and imports all
   eleven domain modules. A leaf module must never import the root: that would pull the
   whole MMT tree into every consumer and defeat the per-domain import scoping in
   `data-domains.yaml`. Also enforced by check 10.

> **Changed in 3.0.0.** Principles 2 and 4 previously read "no cross-imports between
> domains — the root `mmt.ttl` is the only file with `owl:imports`" and "cross-domain
> references use untyped ranges … to avoid cross-imports". Neither held: `consignment.ttl`
> shipped sixteen typed foreign ranges, and across the pack 50 `rdfs:domain` and ~100
> `rdfs:range` assertions named classes their module never imported. Such an assertion is
> silently dropped — the class is never typed in the module's graph, so the property is
> invisible to any consumer resolving "which properties does class X carry". That produced
> a false reference-model gap report against a client hub (gh#97).

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
