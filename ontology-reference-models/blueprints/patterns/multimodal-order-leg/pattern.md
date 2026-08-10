# Multimodal Order / Leg

**Normativity:** naming — normative. Participants and cardinality rules — advisory.

## Problem

A transport order is multimodal by construction: one order can move by road, then ocean, then
rail, and the arranging party sells it as one door-to-door service. But the useful external
standards are all mode-bound — DCSA is ocean, IATA is air, CIM/TAF TSI is rail — and each one
carries obligations that only hold inside its own mode.

That mismatch pushes hubs toward one of two bad moves:

1. **Subclass a mode-specific standard at the order grain** — e.g. a road transport order
   declared `rdfs:subClassOf dcsa:Booking`. It inherits `carrierBookingReference minCardinality 1`
   with no source able to populate it, and it tells every downstream consumer that a road order
   is an ocean carrier's capacity reservation. It also breaks outright on the first intermodal
   order, which would have to be both an ocean order and a road order at once.
2. **Import the standard for terminology and refuse to subclass it** — safe, but it leaves the
   hub with no place at all to attach the standard, so the alignment is decorative.

Neither is necessary. Both come from attaching mode one grain too high.

## Applicability

Use this pattern when a party accepts transport demand and arranges its execution across one or
more carriers — freight forwarder, NVOCC, 3PL, or a shipper's own TMS. Also use the leg and
movement grains alone (participants 2 and 4) when modelling execution for a carrier that has no
upstream order of its own.

## Participants (advisory)

| # | Grain | Class | Carries mode? |
|---|---|---|---|
| 1 | **Order** — one commercial request for transport, owned by the arranging party | `blueprint/transport-order#TransportOrder` | **Never** |
| 2 | **Leg** — one planned segment of the journey | `mmt/consignment#TransportLeg` | **Yes — mode lives here** |
| 3 | **Reservation** — one carrier's commitment of capacity for one leg | `blueprint/transport-order#CarrierReservation` | Yes, by binding |
| 4 | **Movement** — the trip that actually happened | `mmt/consignment#TransportMovement` | Inherited from the leg |

Mode is already reified onto the leg by MMT — `inland-transport#RoadLeg`, `#RailLeg`,
`#BargeLeg` — which is a deliberate MMT design decision, not an accident (see `MMT/README.md`
on reifying `TransportMovement` + `modeCode`). This pattern does not add a mode axis; it stops
one being added in the wrong place.

## The mode-specific standard binds at grain 3

This is the whole point of the pattern. A carrier reservation for an ocean leg genuinely **is**
a carrier capacity reservation, so `dcsa:Booking` holds there with full feasibility — including
`carrierBookingReference`, which the source actually has. A road-only hub declares no ocean leg,
so it declares no ocean reservation, so it inherits nothing. An intermodal order gets both,
attached to different legs, with no conflict.

Hubs declare the binding in their own namespace:

```turtle
hub:OceanCarrierReservation
    rdfs:subClassOf blueprint:CarrierReservation , dcsa-bkg:Booking .
```

The binding is hub-local by design. Whether cross-model links stay informational or justify OWL
axioms in the shared models is still an open stakeholder decision (`convergence-analysis.md`,
"Required stakeholder decisions" #9), so this tier declares the slot and leaves the axiom to
the hub.

### Per-mode alignment targets

**Ocean**, **Air**, and **Rail** are all modelled in this repo. Road and barge carry no
dominant reservation-grain standard, so they remain pattern-only. Each mode binds at grain 3
in the hub, never at the order grain.

The machine-readable form of this table is [`pattern.yaml`](./pattern.yaml) `mode_bindings`,
which additionally carries the module IRIs per mode (`module_iris` at grain 3,
`leg_module_iris` at grain 2). That block is the single source consumed by the `modes-served`
scope axis in the accelerator-pack discovery guides; `scripts/validate_archetypes.py` check 6
asserts the two stay in agreement.

| Mode | Reservation-grain target (grain 3) | Status | Note |
|---|---|---|---|
| **Ocean** | DCSA Booking (BKG API) — `dcsa/booking#Booking` | **Modelled** (derived, `DCSA/`) | Bind hub-local, per above. |
| **Air** | **IATA ONE Record** cargo data model (`Booking`, `BookingRequest`, `BookingOption`, `TransportMovement`) | **Modelled** (authoritative mirror, `authoritative-ontologies/IATA/`) | ONE Record is published natively as RDF/OWL, so it is vendored FIBO-style under `authoritative-ontologies/IATA/` (namespace `https://onerecord.iata.org/ns/cargo#`), not hand-authored as a derived ontology. Reference it via the catalog; do not bulk-import into accelerator packs (mirrors the FIBO exclusion). **Not** IATA Cargo-XML: `XFWB`/`XFZB` are waybill messages, i.e. document grain, already covered by `mmt/documents#AirWaybill`. |
| **Rail** | **TAF TSI** — Path Request / Consignment Order messages | **Modelled** (derived, `RAIL/`) | Hand-authored derived ontology grounded in the TAF TSI data catalogue (`taf_cat_complete.xsd`, EU Regulation 1305/2012 Annex D.2 Appendix F). Modules: `consignment` (Consignment Order Message / ORFEUS ECN), `path-request` (PCS path allocation), `train-running`, `rolling-stock`, `party` (RU/IM), `shared-kernel`. Every class is backed by a cited TAF TSI element. **Not** railML: that is infrastructure and timetable, a different grain entirely. The CIM consignment note is document grain and is already modelled as `mmt/documents#RailConsignmentNote`. |
| **Road** | None — no standard forces a reservation shape | Pattern-only | Model the subcontract as a plain `CarrierReservation` on a `RoadLeg`. `mmt/documents#RoadConsignmentNote` (CMR) covers the document grain. |
| **Barge / inland waterway** | None dominant | Pattern-only | `mmt/inland-transport#BargeLeg` carries the mode. |

**Project cargo is not a mode.** It is a combination of cargo characteristics (out-of-gauge,
heavy-lift) and service scope (engineering, permits, route survey). Modelling it as a fifth
branch of a mode axis is a category error — it cuts across every mode. Express it on the cargo
and on the service scope, not on the leg and not on the order. No project-cargo ontology is
authored in this repo; this note is the authoritative statement of that position.

## Naming (normative)

| Link | Property |
|---|---|
| Order identity | `transportOrderReference` |
| Order → ordering party | `hasOrderingParty` |
| Order → leg (1..N, ordered) | `hasPlannedLeg` |
| Order → consignment | `coversConsignment` |
| Leg → reservation | `hasCarrierReservation` |
| Leg → movement (plan → actual) | `realizedByMovement` |

Aggregate identity follows the repo-wide `<aggregate>Reference` convention (`carrierBookingReference`,
`shippingInstructionReference`, `transportOrderReference`). Requested service windows follow
[`temporal-quartet`](../temporal-quartet/pattern.md) — `requestedStart` / `requestedEnd`, using
Start/End because an order window is duration-bearing.

## Cardinality rules (advisory)

- Order → leg: `1..N`, ordered. An order with no leg is a quote, not an order.
- Leg → reservation: `0..1`. Zero while the leg is unprocured, or where the arranging party
  executes the leg itself with its own equipment.
- Order → reservation: **there is no direct link.** Always traverse the leg.
- Leg → movement: `0..N`. Zero before execution; more than one when a leg is re-executed after
  a failure. Plan and actual are separate grains and neither overwrites the other.

## When NOT to use

**A carrier with no upstream order does not need grain 1.** Its incoming demand *is* the
reservation. Adding a `TransportOrder` above `dcsa:Booking` for a pure ocean carrier duplicates
the booking with a synonym and buys nothing. This is why the archetype catalog tiers grain 1
per archetype rather than shipping it everywhere:

| Archetype | Grain 1 (order) | Grain 2 (leg) | Grain 3 (reservation) |
|---|---|---|---|
| `freight-forwarder` | `required` | `required` | `recommended` |
| `unit-load-carrier` | `recommended` — direct door-to-door sales | `required` | `required` |
| `shipping-carrier` | **omitted** — supply side | `recommended` | `required` |

A single-mode, single-carrier operation with no subcontracting can also stop at grain 3 and skip
the leg — but only while that remains true. Adding the leg later is a migration.

## Anti-patterns

| Anti-pattern | Why it is rejected |
|---|---|
| `OceanOrder` / `RoadOrder` / `AirOrder` subclasses | Mode on the order breaks on the first intermodal order, which would need two incompatible types at once. Mode belongs on the leg. |
| `orderTransportMode` scalar on the order | Same error in property form. An order spanning three modes has no single value; the field ends up holding the first leg's mode and quietly lying. |
| Order `rdfs:subClassOf` a mode-specific standard class | Inherits obligations no source can populate — e.g. `dcsa:Booking`'s `carrierBookingReference minCardinality 1` — and misstates the grain. Bind at grain 3 instead. |
| `hasBooking` directly on the order | Shortcut around the leg. It works for the single-leg case and silently loses which leg a reservation covers the moment there are two. |
| Cargo, customs, document, or financial properties on the order | The order is an aggregate root, not a report. Wide source order records fan out to the owning domains by traversal. |
| Treating a waybill (AWB, B/L, CMR) as the reservation | Transport documents are their own grain, already modelled in `mmt/documents`. A document evidences a leg; it does not reserve it. |

## Grain collisions

- **Order vs. `dcsa:Booking`** — the registry pins Booking to *"one carrier capacity and equipment
  reservation"*. One order may produce several bookings across several carriers. Non-equivalent.
- **Order vs. BSP `SalesOrder`/`PurchaseOrder`** — those are commercial buy/sell of goods. A
  transport order buys a *service*. They co-occur and reference each other; they do not merge.
- **Order vs. TIC `Order`** — TIC's is an atomic terminal handling directive subclassing `Move`.
  Different scope, different lifecycle, different owner.
- **Order vs. `mmt:TransportInstructions`** — instruction *content*, without durable job identity
  or lifecycle. Related, not equivalent.
- **Leg vs. movement** — plan versus execution. Held open by decision-log `LOG-BP-006`; do not
  collapse them even when a hub's source system carries one row for both.
