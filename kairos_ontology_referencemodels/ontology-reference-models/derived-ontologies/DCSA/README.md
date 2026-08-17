# DCSA Container Shipping Ontology — Journey Model

This directory contains the modularized DCSA (Digital Container Shipping Association) ontology, organized according to DCSA's official Information Model 2024.Q4 **journey-based structure**.

## Structure

```
DCSA/
├── dcsa.ttl                                                    # Root (imports all journeys)
├── shipment-journey/
│   ├── shipment-journey.ttl                                    # 1. Shipment Journey
│   ├── booking/booking.ttl                                     # Booking & shipping workflow
│   └── transport-documents/transport-documents.ttl             # B/L & transport docs
├── equipment-journey/
│   ├── equipment-journey.ttl                                   # 2. Equipment Journey
│   └── container-operations/container-operations.ttl           # Container lifecycle
├── vessel-journey/
│   ├── vessel-journey.ttl                                      # 3. Vessel Journey
│   └── schedule/schedule.ttl                                   # OVS schedules & service loops
├── track-and-trace/
│   ├── track-and-trace.ttl                                     # Track & Trace
│   └── events/events.ttl                                       # Shipping events
├── demurrage-detention/
│   └── demurrage-detention.ttl                                 # D&D charges & tariffs
├── shared-kernel/
│   ├── shared-kernel.ttl                                       # SK (Shared Kernel)
│   ├── equipment/equipment.ttl                                 # Container equipment types
│   ├── party/party.ttl                                         # Shipping party roles
│   ├── locations/locations.ttl                                 # Ports, terminals & inland facilities
│   └── transport-call/transport-call.ttl                       # Transport call (vessel/barge/rail/truck)
├── VERSION
└── README.md
```

## Journey Model (DCSA Information Model 2024.Q4)

### 1. Shipment Journey — `shipment-journey/`
**Namespace:** `https://www.kairosflow.ai/ont/dcsa/shipment-journey#`
**Source:** DCSA BKG v2.0, EBL v3.0

The cargo lifecycle from booking request through transport document issuance:
- **booking/** — `Booking`, `BookingRequest`, `ConfirmedBooking`, `ShippingInstruction`, `Shipment`, `CargoItem`, `Commodity`, `RequestedEquipment`, `UtilizedTransportEquipment`
- **transport-documents/** — `TransportDocument`, `BillOfLading`, `ElectronicBillOfLading`, `SeaWaybill`

### 2. Equipment Journey — `equipment-journey/`
**Namespace:** `https://www.kairosflow.ai/ont/dcsa/equipment-journey#`
**Source:** DCSA TNT v2.2 (equipment events)

The container lifecycle from empty pickup to empty return:
- **container-operations/** — `ContainerJourney`, `ContainerOperationalStatus`, `ContainerStuffing`, `ContainerStripping`, `LiftOnLiftOff`

### 3. Vessel Journey — `vessel-journey/`
**Namespace:** `https://www.kairosflow.ai/ont/dcsa/vessel-journey#`
**Source:** DCSA OVS v3.0

Vessel operations, schedules, and port rotations:
- **schedule/** — `ServiceLoop`, `SailingSchedule`, `CutOffTime`, `TransitTime`

### Track and Trace — `track-and-trace/`
**Namespace:** `https://www.kairosflow.ai/ont/dcsa/track-and-trace#`
**Source:** DCSA TNT v2.2

Shipping event tracking across all journeys:
- **events/** — `Event`, `TransportEvent`, `EquipmentEvent`, `DocumentEvent`, `VesselDepartureEvent`, `VesselArrivalEvent`, `GateInEvent`, `GateOutEvent`, `LoadedOnVesselEvent`, `DischargedFromVesselEvent`, `EmptyContainerPickupEvent`, `EmptyContainerReturnEvent`, `DocumentIssuedEvent`, `DocumentSurrenderedEvent`, `BorderCrossingEvent`, `AvailableForPickupEvent`, `AvailableForDropoffEvent`, `PickedUpEvent`, `DroppedOffEvent`, `CustomsEvent`, `InspectionEvent`, `SealEvent`

### Shared Kernel (SK) — `shared-kernel/`
**Namespace:** `https://www.kairosflow.ai/ont/dcsa/shared-kernel#`
**Source:** DCSA Information Model SK

Common entities referenced across all journeys:
- **equipment/** — `Container`, `DryContainer`, `ReeferContainer`, `TankContainer`, `FlatRackContainer`, `OpenTopContainer`, `PlatformContainer`
- **party/** — `ShippingParty`, `Shipper`, `Consignee`, `Carrier`, `BookingParty`, `NotifyParty`, `FreightForwarder`
- **locations/** — `Location`, `Port`, `Terminal`, `PlaceOfReceipt`, `PortOfLoading`, `PortOfDischarge`, `PlaceOfDelivery`, `TransshipmentPort`, `InlandTerminal`, `RailRamp`, `BorderCrossing`, `Depot`, `ContainerFreightStation`, `PreCarriageFromLocation`, `OnwardInlandRoutingLocation`, `DepotReleaseLocation`
- **transport-call/** — `TransportCall`, `VesselTransportCall`, `BargeTransportCall`, `RailTransportCall`, `TruckTransportCall`

## Design Principles

1. **Journey-based grouping** — Follows DCSA Information Model 2024.Q4 decomposition by journey type
2. **Stable namespaces** — Module IRIs remain entity-based (`dcsa/booking#`, `dcsa/events#`) for backwards compatibility
3. **Cross-domain references** — A leaf module that asserts `rdfs:domain` or `rdfs:range`
   against a shared-kernel entity (equipment, party, locations, transport-call) declares
   its own `owl:imports` for that module. Enforced by `validate_structure.py` check 10.
4. **Import hierarchy** — `dcsa.ttl` → journey .ttl → leaf module .ttl. The hierarchy
   composes the bundle; it does not substitute for a leaf's own imports. A leaf must
   never import the `dcsa.ttl` root.
5. **Consistent metadata** — All modules use `dcterms:` for metadata; `owl:versionInfo` for versioning

> **Changed in 1.6.0.** Principle 3 previously said journey-level files "handle composition
> via `owl:imports`", implying leaves need none of their own. They did:
> `equipment-journey.ttl` imported `container-operations` but not `equipment`, so
> `container-operations`' `rdfs:domain equip:Container` was dangling even one level up, and
> twenty such assertions across seven leaves were invisible to consumers (gh#97).

## Version
- **Ontology version:** 1.3.0
- **Based on:** DCSA Information Model 2024.Q4, DCSA Booking API v2.0.4, and DCSA Domain v3.1.0

### v1.3.0 DCSA Domain v3.1 fit-gap alignment

This release adds 14 selected high-value DCSA Domain v3.1.0 terms across
booking lifecycle timestamps, transport-call/facility qualifiers, and
dangerous-goods commodity details. The full DCSA Domain v3.1.0 fit-gap is
documented under `.docs/refmodels/DCSA/`; additional DCSA Domain fields may be
mapped through a future full domain discovery pass.

## Usage

Load the complete ontology:
```turtle
@prefix dcsa: <https://www.kairosflow.ai/ont/dcsa#> .
```

Load a specific journey:
```turtle
@prefix sj: <https://www.kairosflow.ai/ont/dcsa/shipment-journey#> .
```

Load a specific module:
```turtle
@prefix booking: <https://www.kairosflow.ai/ont/dcsa/booking#> .
@prefix equipment: <https://www.kairosflow.ai/ont/dcsa/equipment#> .
```
