# DCSA Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-15

| Item | Details |
|---|---|
| What is it? | A shipping information model from the Digital Container Shipping Association, represented here as modular OWL ontologies. |
| Main focus | Shipment journey, booking, transport documents, equipment journey, vessel journey, and track-and-trace events. |
| Why selected in this blueprint | Provides authoritative container-shipping process semantics and event models for ocean-forwarding scenarios. |
| Who is behind it | Digital Container Shipping Association (DCSA). |
| Official site / references | https://dcsa.org |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/dcsa#` |
| Adoption context | Commonly used as a shared API and information model baseline across container-shipping integrations. |
| Kairos modules used | `dcsa/booking`, `dcsa/shipment-journey`, `dcsa/transport-documents`, `dcsa/schedule`, `dcsa/events`, `dcsa/track-and-trace`, `dcsa/equipment`, `dcsa/vessel-journey`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/DCSA/README.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `Booking` | Customer request and confirmation container for transport planning. | `hasBookingParty`, `bookingStatus`, `requestedEquipmentType` |
| `Shipment` | End-to-end shipping movement unit tracked through the journey. | `origin`, `destination`, `shipmentStatus` |
| `TransportDocument` | Official transport documentation (for example bill of lading variants). | `documentNumber`, `issueDate`, `documentStatus` |
| `Container` | Reusable equipment unit used to carry shipment cargo. | `equipmentReference`, `isoEquipmentCode`, `containerOperationalStatus` |
| `ServiceLoop` | Planned vessel service pattern used for routing and scheduling. | `serviceCode`, `hasPortCallSequence`, `plannedTransitTime` |
| `Event` | Normalized milestone/event object for track-and-trace visibility. | `eventType`, `eventDateTime`, `eventLocation` |
