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
├── shared-kernel/
│   ├── shared-kernel.ttl                                       # SK (Shared Kernel)
│   ├── equipment/equipment.ttl                                 # Container equipment types
│   ├── party/party.ttl                                         # Shipping party roles
│   └── locations/locations.ttl                                 # Ports & terminals
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
- **events/** — `Event`, `TransportEvent`, `EquipmentEvent`, `DocumentEvent`, `VesselDepartureEvent`, `VesselArrivalEvent`, `GateInEvent`, `GateOutEvent`, `LoadedOnVesselEvent`, `DischargedFromVesselEvent`, `EmptyContainerPickupEvent`, `EmptyContainerReturnEvent`, `DocumentIssuedEvent`, `DocumentSurrenderedEvent`

### Shared Kernel (SK) — `shared-kernel/`
**Namespace:** `https://www.kairosflow.ai/ont/dcsa/shared-kernel#`
**Source:** DCSA Information Model SK

Common entities referenced across all journeys:
- **equipment/** — `Container`, `DryContainer`, `ReeferContainer`, `TankContainer`, `FlatRackContainer`, `OpenTopContainer`, `PlatformContainer`
- **party/** — `ShippingParty`, `Shipper`, `Consignee`, `Carrier`, `BookingParty`, `NotifyParty`, `FreightForwarder`
- **locations/** — `Location`, `Port`, `Terminal`, `PlaceOfReceipt`, `PortOfLoading`, `PortOfDischarge`, `PlaceOfDelivery`, `TransshipmentPort`

## Design Principles

1. **Journey-based grouping** — Follows DCSA Information Model 2024.Q4 decomposition by journey type
2. **Stable namespaces** — Module IRIs remain entity-based (`dcsa/booking#`, `dcsa/events#`) for backwards compatibility
3. **No cross-imports** — Each leaf module is standalone. Journey-level .ttl files handle composition via `owl:imports`
4. **Import hierarchy** — `dcsa.ttl` → journey .ttl → leaf module .ttl
5. **Consistent metadata** — All modules use `dcterms:` for metadata; `owl:versionInfo` for versioning

## Version
- **Ontology version:** 1.0.0
- **Based on:** DCSA Information Model 2024.Q4

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
