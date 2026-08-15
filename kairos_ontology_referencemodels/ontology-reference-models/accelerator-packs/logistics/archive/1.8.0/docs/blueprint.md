# Logistics Capability Blueprint

## Status

This is a client-hub-agnostic, pre-release blueprint. It organizes reusable logistics
semantics by capability and lifecycle rather than by source table or adapter. Canonical
authority remains unresolved where the convergence review requires stakeholder input.

## Capability backbone

| Capability | Stable semantic distinctions | Optional/specialized surfaces |
|---|---|---|
| Party coordination | Durable identity versus contextual role | Carrier, shipper, consignee, booking party, forwarder, customs and maritime roles |
| Location network | Durable place/facility versus itinerary role | Port, terminal, depot, warehouse, loading/discharge/receipt/delivery/transshipment |
| Commercial reservation | Booking lifecycle separate from commercial and terminal orders | Booking request, confirmation, amendments, shipping instruction |
| Freight organization | Shipment, consignment, master/house, and item are separate grains | Consolidation, split, rollover, regrouping |
| Equipment | Asset, request, allocation/utilisation, journey, and status are separate | Container-specific and multimodal specializations |
| Transport topology | Route, planned leg, movement, call, port call, and terminal move | Modal legs, ordered stops, plan-to-execution links |
| Visibility | Immutable event separate from current status | Transport, equipment, document, customs, terminal, estimated and planned events |
| Documents | Document identity separate from version, issuance, surrender, and status | Bill of lading, waybill, house/master, customs and regulatory documents |
| Quantities | Measurement context retained with quantity kind and unit | Cargo weight/dimension and generic trade measurements |
| Identifiers | Scheme and issuer scope retained | Scalar properties or structured assignments |

## Operating-archetype evidence

- `shipping-carrier` tests carrier booking, shipment, container fleet, transport calls,
  terminal events, documents, and regulatory operations.
- `freight-forwarder` tests customer instructions, multiple carrier bookings,
  master/house consolidation, multimodal legs, third-party equipment, and customs
  coordination.
- Synthetic source shapes under `blueprint/evidence/source-shapes/` verify that the
  semantic distinctions survive both operating models without prescribing source tables.

## Extension points

The following remain deliberate extension points pending standards audit and review:

- neutral Party and qualified Party Role Assignment;
- qualified Location Role Assignment;
- forwarding job/customer instruction;
- booking amendment/version history;
- general multimodal equipment allocation;
- ordered Stop and plan-to-execution realization;
- source-neutral Event subject/correction pattern;
- structured Identifier Assignment;
- temporal Status Observation.

## Explicit non-equivalences

Booking is not a purchase order or terminal order. Shipment is not Consignment.
Equipment request is not equipment asset or utilisation. Transport Call is not a
regulatory Port Call. Event is not status. Port of Loading is not a second physical Port.
Equal role labels across standards do not establish equivalent classes.

## Physical-policy boundary

This blueprint does not activate projection policy. Silver inclusion, table names,
natural keys, nullability, SCD behavior, and adapter output belong to the explicitly
activated Silver Starter profile. That profile can select only reviewed, approved
concepts and is derived into a generated contract rather than duplicated by hand.
