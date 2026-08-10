# IATA ONE Record Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-08-10

| Item | Details |
|---|---|
| What is it? | The IATA air cargo data model, published natively as RDF/OWL — a single shared record of a shipment exchanged over a standardised, secured web API. |
| Main focus | Air cargo booking, shipment and pieces, transport movements, waybills, and logistics events. |
| Why selected in this blueprint | Air was one of two modes with no reservation-grain target. ONE Record is the industry standard for air cargo and, unusually, ships as OWL — so it is mirrored rather than re-authored. |
| Who is behind it | International Air Transport Association (IATA), ONE Record programme. |
| Official site / references | https://www.iata.org/en/programs/cargo/e/freight/one-record/ ; release `2026-08-standard` at https://github.com/IATA-Cargo/ONE-Record |
| Ontology / OWL reference | `https://onerecord.iata.org/ns/cargo#` (data model) and `https://onerecord.iata.org/ns/code-lists/` (code lists) |
| Adoption context | The IATA-endorsed successor to Cargo-XML messaging for airlines, forwarders, ground handlers, and customs. |
| Kairos modules used | **None — this is an authoritative mirror, not a Kairos-authored module.** Vendored verbatim under `authoritative-ontologies/IATA/` and resolved through `catalog-v001.xml`. |

## Tier and import policy — this sheet is different from the other seven

Every other model in this pack is a **derived** ontology that Kairos authored and the
accelerator imports. ONE Record is **authoritative**: published as OWL by IATA, vendored
byte-for-byte, never hand-edited, and re-downloaded rather than maintained.

Consequently the accelerator pack **deliberately never imports it** — bulk-importing an
entire external cargo model into every consumer is the same objection that keeps FIBO out
of logistics. It is `reference-only` in `manifest.yaml`. A client hub serving air cargo
binds to it *hub-local*, at the reservation grain:

```turtle
hub:AirCarrierReservation
    rdfs:subClassOf bp:CarrierReservation ,
                    <https://onerecord.iata.org/ns/cargo#Booking> .
```

Air Waybill is document grain and is already covered by `mmt/documents#AirWaybill`. This is
**not** IATA Cargo-XML: `XFWB`/`XFZB` are messages at document grain, not a reservation shape.

## Internal reference

- `ontology-reference-models/authoritative-ontologies/IATA/README.md`
- `ontology-reference-models/blueprints/patterns/multimodal-order-leg/pattern.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog — the
> vendored data model declares 173). Properties are declared via `owl:Restriction`, not
> `rdfs:domain`.

| Class | High-level explanation | Example properties |
|---|---|---|
| `Booking` | A confirmed air cargo booking — the grain-3 alignment target for the air mode. | `bookingRequest`, `bookingSegments`, `bookingShipmentDetails`, `bookingStatus` |
| `BookingRequest` | Created by a party, usually the forwarder, to confirm a booking with the carrier. | `booking`, `forBookingOption`, `waybillPrefix`, `waybillNumber` |
| `BookingOption` | An offered option against a request: carrier, product, and timings before confirmation. | `carrier`, `carrierProduct`, `bookingTimes`, `alternatives` |
| `Shipment` | The commercial consignment: goods description, parties, terms, and its constituent pieces. | `pieces`, `goodsDescription`, `involvedParties`, `incoterms` |
| `Piece` | An individual piece, or a virtual grouping of pieces, of the physical cargo. | `containedPieces`, `containedItems`, `customsInformation` |
| `TransportMovement` | Movement-grain activity describing an actual transport leg; replaces `TransportSegment`. | `departureLocation`, `arrivalLocation`, `co2Emissions`, `distanceMeasured` |
