# IATA ONE Record — Authoritative Ontology Mirror

Vendored copy of the official **IATA ONE Record** ontology, the Linked Data data model
for air cargo. Vendored verbatim (FIBO-style authoritative mirror) — **do not hand-edit
the `.ttl` files**; re-download instead.

## Tier

**Authoritative.** ONE Record is published natively as RDF/OWL, so it enters
`authoritative-ontologies/` rather than being re-authored as a derived ontology. See
`ontology-reference-models/blueprints/README.md` for the authoritative / derived /
blueprint tier distinction.

## Contents

| File | Namespace | Purpose |
|---|---|---|
| `IATA-1R-DM-Ontology.ttl` | `https://onerecord.iata.org/ns/cargo#` | Core data model (Shipment, Piece, Booking, Waybill, TransportMovement, LogisticsEvent, …) |
| `IATA-1R-CL-Ontology.ttl` | `https://onerecord.iata.org/ns/code-lists/` | Code lists / enumerations |
| `METADATA.txt` | — | Provenance: source, version, download date, release URL |
| `LICENSE` | — | MIT License (Copyright (c) 2025 IATA-Cargo) |

## Version

ONE Record **2026-08 standard**, Data Model **v3.3.0 RC1**. See `METADATA.txt`.

## Where it binds in Kairos

Per `blueprints/patterns/multimodal-order-leg/pattern.md`, ONE Record is the
reservation-grain (grain 3) alignment target for **air**. Mode binds at the carrier
reservation, never at the order grain. Hubs declare the binding hub-local, e.g.:

```turtle
hub:AirCarrierReservation
    rdfs:subClassOf bp:CarrierReservation ,
                    <https://onerecord.iata.org/ns/cargo#Booking> .
```

Document-grain air concepts (Air Waybill) are already modelled in
`derived-ontologies/MMT/current/documents/documents.ttl` as `mmt/documents#AirWaybill`.

## License

MIT License — see `./LICENSE`. Bundled under the repository `NOTICE` third-party section.
Apache-2.0 compatible.
