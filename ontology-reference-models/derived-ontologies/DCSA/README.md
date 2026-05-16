# DCSA Container Shipping Ontology — Domain Modules

This directory contains the modularized DCSA (Digital Container Shipping Association) ontology, split into seven domain-specific modules with a root ontology that imports them all.

## Structure

```
DCSA/
├── dcsa.ttl                                        # Root ontology (imports all modules)
├── booking/booking.ttl                             # Booking & shipping domain
├── container-operations/container-operations.ttl   # Container lifecycle & operations
├── equipment/equipment.ttl                         # Container equipment types
├── transport-documents/transport-documents.ttl     # Bills of Lading & transport docs
├── party/party.ttl                                 # Shipping party roles
├── locations/locations.ttl                         # Ports, terminals & locations
├── events/events.ttl                               # Track & trace events
├── VERSION                                         # Version file
└── README.md                                       # This file
```

## Domain Modules

### Root — `dcsa.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa#`

The root ontology imports all seven domain modules via `owl:imports`. Use this as the single entry point to load the complete DCSA ontology.

### Booking — `booking/booking.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa/booking#`

Core booking and shipping workflow classes:
- `Booking`, `BookingRequest`, `ConfirmedBooking`
- `ShippingInstruction`, `Shipment`
- `CargoItem`, `Commodity`
- `RequestedEquipment`, `UtilizedTransportEquipment`

Also contains object properties relating shipments to bookings, cargo, equipment, parties, locations, and events, plus datatype properties for booking references, cargo details, and commercial terms.

### Container Operations — `container-operations/container-operations.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa/container-operations#`

Container lifecycle and operational concepts (new domain, not in original monolith):
- `ContainerJourney` — full lifecycle from empty pickup to empty return
- `ContainerOperationalStatus` — current state tracking (available, in-transit, at-terminal)
- `ContainerStuffing` / `ContainerStripping` — cargo packing/unpacking
- `LiftOnLiftOff` — LoLo crane handling operations

### Equipment — `equipment/equipment.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa/equipment#`

ISO container types and physical properties:
- `Container` (base), `DryContainer`, `ReeferContainer`, `TankContainer`
- `FlatRackContainer`, `OpenTopContainer`, `PlatformContainer`
- Properties: container number, ISO codes, VGM, tare weight, temperature settings, etc.

### Transport Documents — `transport-documents/transport-documents.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa/transport-documents#`

Shipping documentation:
- `TransportDocument`, `BillOfLading`, `ElectronicBillOfLading`, `SeaWaybill`
- Properties: document reference, status, negotiability, number of originals

### Party — `party/party.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa/party#`

Shipping party roles:
- `ShippingParty` (base)
- `Shipper`, `Consignee`, `Carrier`, `BookingParty`, `NotifyParty`, `FreightForwarder`

### Locations — `locations/locations.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa/locations#`

Geographic and facility locations:
- `Location`, `Port`, `Terminal`
- `PlaceOfReceipt`, `PortOfLoading`, `PortOfDischarge`, `PlaceOfDelivery`, `TransshipmentPort`
- Properties: UN/LOCODE, facility code

### Events — `events/events.ttl`
**Namespace:** `http://kairos.ai/ont/dcsa/events#`

Track and trace events:
- `Event` (base), `TransportEvent`, `EquipmentEvent`, `DocumentEvent`
- Transport: `VesselDepartureEvent`, `VesselArrivalEvent`
- Equipment: `GateInEvent`, `GateOutEvent`, `LoadedOnVesselEvent`, `DischargedFromVesselEvent`, `EmptyContainerPickupEvent`, `EmptyContainerReturnEvent`
- Document: `DocumentIssuedEvent`, `DocumentSurrenderedEvent`
- Properties: event datetime, type/classifier codes, ETA/ETD/ATA/ATD

## Design Principles

1. **No cross-imports** — Each domain module is standalone within the DCSA ontology. The root `dcsa.ttl` is the only file with `owl:imports`.
2. **Property placement** — Properties live in the domain module of their primary domain (subject) class. Cross-domain properties omit the range type reference to avoid cross-module dependencies.
3. **Consistent metadata** — All modules use `dcterms:` for title, description, creator, and dates; `owl:versionInfo` for versioning.
4. **Version:** 1.0.0
5. **Source:** Digital Container Shipping Association (DCSA) Standards

## Usage

To load the complete ontology, import the root:
```turtle
@prefix dcsa: <http://kairos.ai/ont/dcsa#> .
```

To use a specific domain only:
```turtle
@prefix booking: <http://kairos.ai/ont/dcsa/booking#> .
@prefix equipment: <http://kairos.ai/ont/dcsa/equipment#> .
```
