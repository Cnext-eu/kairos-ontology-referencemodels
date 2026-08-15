# Logistics Blueprint Decision Log

## Review state

Only explicitly reviewed decisions are approved. The initial analysis was completed
without an available stakeholder, so all other checkpoints remain **investigate** rather
than silently accepted.

| ID | Checkpoint | Status | Recommendation | Rationale | Confidence | Evidence |
|---|---|---|---|---|---|---|
| LOG-BP-001 | Party authority | Approved - standards audit required | Use a neutral durable Party identity and qualified contextual Party Role Assignment; keep BSP/DCSA/MMT/IMO role classes as standards overlays until mappings are proven. | BSP, DCSA, MMT, and IMO party parents all mix identity and role context; both operating archetypes require one organisation to play several roles over time. | High | Stakeholder confirmation 2026-07-21; `convergence-analysis.md` Session A; `evidence/cross-archetype-assessment.md` |
| LOG-BP-002 | Location authority | Investigate | Separate durable place/facility identity from route and shipment roles. | Loading, discharge, receipt, delivery, and transshipment are contextual uses of a location. | Medium | `convergence-analysis.md` Sessions A-B |
| LOG-BP-003 | Booking authority | Investigate | Prefer DCSA `Booking` for carrier reservations. Scope narrowed by LOG-BP-012: the demand-side order grain is no longer in this checkpoint. | BSP orders and TIC terminal orders have different grains and lifecycles. | High | `convergence-analysis.md` Booking and order |
| LOG-BP-004 | Shipment and consignment | Investigate | Retain DCSA Shipment and MMT Consignment as related distinct grains. | Carrier transaction and identifiable goods collection are not equivalent. | High | `convergence-analysis.md` Consignment and shipment |
| LOG-BP-005 | Equipment model | Investigate | Preserve asset, request, utilisation, and journey grains. | Their identities and lifecycles are explicitly different. | High | `convergence-analysis.md` Equipment |
| LOG-BP-006 | Transport topology | Investigate | Preserve route, planned leg, actual movement, call, port call, and terminal move. | They represent path, intent, execution, facility interaction, regulation, and handling respectively. | High | `convergence-analysis.md` Movement, leg, stop and call |
| LOG-BP-007 | Event authority | Investigate | Use a neutral event envelope only after subject roles and correction semantics converge. | DCSA, MMT, BSP, and TIC event scopes are not proven equivalent. | Medium | `convergence-analysis.md` Transport event |
| LOG-BP-008 | Documents | Investigate | Keep standard-specific transport-document classes and separate identity from version/state. | Carrier, multimodal, and generic trade scopes differ. | Medium | `convergence-analysis.md` Document pattern |
| LOG-BP-009 | Identifiers | Investigate | Keep scoped identifier properties; use structured assignments only for scheme, issuer, validity, or crosswalk requirements. | No universal scalar identifier is evidenced. | High | `convergence-analysis.md` Identifier pattern |
| LOG-BP-010 | Measurements | Investigate | Prefer MMT measurements in cargo context; do not assert blanket equivalence to BSP measurements. | Quantity context and authority differ. | High | `convergence-analysis.md` Measurement pattern |
| LOG-BP-011 | Status | Investigate | Keep aggregate-specific status codes; add temporal observations only when history/provenance is required. | Current state, state observation, and lifecycle event are different concepts. | High | `convergence-analysis.md` Status pattern |
| LOG-BP-012 | Transport order grain | Investigate | Author the demand-side order as a blueprint-tier class (`blueprint/transport-order#TransportOrder`) rather than force-fitting DCSA `Booking`; procure carrier capacity through `CarrierReservation` attached to the leg. | The issue #29 standards audit found every installed candidate expresses a different grain, and one order may procure several carrier reservations. Blueprint tier because no standard defines the grain, so `derived-ontologies/` would misstate provenance. | High | Issue #29 standards audit; `blueprints/patterns/multimodal-order-leg/pattern.md`; overlap `transport-order-grain` |
| LOG-BP-013 | Transport mode axis | Investigate | Specialise the leg by mode, never the order. Bind mode-specific standards at the leg's carrier reservation. | An order is multimodal by construction; MMT already reifies mode onto the leg. Binding at the reservation is what makes subclassing DCSA feasible for ocean scope without imposing it on road-only hubs. | High | Issue #33; `MMT/README.md` reification note; overlap `transport-order-mode-axis` |

## Resolved challenge: transport order / forwarding job

> **Outcome (LOG-BP-012, LOG-BP-013).** The standards audit below stands in full — every
> installed candidate expresses a different grain. What changed is the *conclusion drawn
> from it*. The audit's guidance was "do not add a shared class", on the reasoning that
> repository policy permits only classes backed by a cited standard. That reasoning was
> sound for `derived-ontologies/`, which is bound to be faithful to its source, and it is
> why the class was **not** added there. It does not apply to a tier that makes no
> standards claim: `blueprints/ontology/` was created for exactly this case and now holds
> `blueprint/transport-order#TransportOrder`, with the admission bar documented in that
> folder's README.
>
> The audit table is retained below because it is the evidence for the new class, not an
> argument against it — it is what proves the grain is distinct from every alternative.

Issue #29 challenged whether the Booking domain needs a shared `TransportOrder`
class. The review distinguished an **installed-model gap** from a
**standards-authorized reference-model gap**:

| Candidate | Verified grain | Challenge outcome |
|---|---|---|
| DCSA `Booking` | One carrier capacity/equipment reservation, identified by a carrier booking reference | Retain for carrier reservations; not the upstream forwarder job |
| DCSA `Shipment` | One carrier-side transport transaction | Reject as an order/job substitute |
| BSP `PurchaseOrder` / `SalesOrder` | Buyer/seller commercial order documents | Reject as freight-forwarding orchestration |
| MMT `TransportInstructions` | Transport instruction content in the documents module | Useful related evidence, but not a durable job aggregate |
| TIC `Order` | Atomic terminal handling directive and subclass of `Move` | Reject; terminal execution has a different grain |
| Forwarding job / customer instruction | One forwarder-owned instruction or job that may create several carrier bookings | Preserve as an extension point; shared-class authority remains unproven |

The evidence supports the **semantic distinctness** of the upstream forwarding job, and
does not support its promotion into a standards-derived reference ontology. Both remain
true. The resolution was to place the class in a tier that claims no standards
provenance, rather than to choose between them.

Standing guidance:

1. do not force-fit an upstream forwarding job to DCSA `Booking` or `Shipment` — they are
   a carrier capacity reservation and a carrier-side transaction respectively;
2. do not add a `TransportOrder` to `derived-ontologies/` — no standard defines this
   grain, so that tier would misstate its provenance. It lives in `blueprints/ontology/`;
3. hubs specialise `blueprint/transport-order#CarrierReservation` per mode where they have
   source feasibility — that is the legitimate place to subclass `dcsa:Booking`, and is
   scoped to an ocean leg rather than to the order (LOG-BP-013); and
4. the Booking-domain ownership phrase "transport orders" now has a class behind it; see
   the `grain_note` in `client-hub-blueprint/data-domains.yaml` for the order-versus-booking
   distinction it must not collapse.

## Rejected shortcuts

| Shortcut | Rejection reason |
|---|---|
| Subclass a mode-specific standard at the order grain | Inherits obligations no source can populate (DCSA `Booking` requires `carrierBookingReference`) and misstates the grain. Bind at the carrier reservation instead. |
| Specialise the transport order by mode (`OceanOrder`, `RoadOrder`) | An intermodal order would need two incompatible types at once. Mode belongs on the leg. |
| Treat "transport order" and "booking" as the same thing in blueprint prose | One order may procure several bookings across several carriers; the shorthand hides a 1..N fan-out. |
| Treat equal labels as equivalent classes | Labels do not prove identity, grain, lifecycle, or authority. |
| Use `TradeParty` as both durable identity and every transaction role | One organisation can play different roles concurrently and over time. |
| Materialize Port of Loading and Port of Discharge as separate physical locations | This duplicates one port when it plays several itinerary roles. |
| Collapse Booking, Shipment, and Consignment | Reservation, carrier transaction, and goods responsibility have distinct lifecycles. |
| Put requested and utilized equipment on the container master | Demand and allocation are contextual, not asset identity. |
| Use one Movement table for plans, legs, calls, and terminal moves | It destroys sequence, execution, and facility-interaction semantics. |
| Treat status changes as events without provenance | A current status code does not establish an immutable occurrence. |
| Hand-author the generated Silver contract | The physical profile is the single future source; the contract is derived. |

## Release gate

The following remain blocked until stakeholder review records approve, defer, or reject
each remaining candidate and the approved Party gap passes standards audit:

- first-slice flags;
- canonical authority dispositions;
- relationship cardinality and temporal semantics;
- reference-model gap implementation;
- Silver profile entities and physical policies;
- generated contract and adapter examples.
