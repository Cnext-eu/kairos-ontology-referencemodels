# Logistics Blueprint Decision Log

## Review state

Only explicitly reviewed decisions are approved. The initial analysis was completed
without an available stakeholder, so all other checkpoints remain **investigate** rather
than silently accepted.

| ID | Checkpoint | Status | Recommendation | Rationale | Confidence | Evidence |
|---|---|---|---|---|---|---|
| LOG-BP-001 | Party authority | Approved - standards audit required | Use a neutral durable Party identity and qualified contextual Party Role Assignment; keep BSP/DCSA/MMT/IMO role classes as standards overlays until mappings are proven. | BSP, DCSA, MMT, and IMO party parents all mix identity and role context; both operating archetypes require one organisation to play several roles over time. | High | Stakeholder confirmation 2026-07-21; `convergence-analysis.md` Session A; `evidence/cross-archetype-assessment.md` |
| LOG-BP-002 | Location authority | Investigate | Separate durable place/facility identity from route and shipment roles. | Loading, discharge, receipt, delivery, and transshipment are contextual uses of a location. | Medium | `convergence-analysis.md` Sessions A-B |
| LOG-BP-003 | Booking and upstream forwarding-job authority | Investigate - expert review in #29 | Use DCSA `Booking` only for carrier reservations. Treat a forwarder-owned transport order/job as a hub-local extension candidate unless primary standards evidence proves a shared reference class. | The installed DCSA, BSP, MMT, and TIC candidates have different grains. Cross-archetype evidence supports a distinct upstream forwarding job, but no verified cited standard currently authorizes adding it as a shared reference class. | Medium | `convergence-analysis.md` Booking and order; `evidence/cross-archetype-assessment.md`; `evidence/source-shapes/freight-forwarder.yaml`; issue #29 |
| LOG-BP-004 | Shipment and consignment | Investigate | Retain DCSA Shipment and MMT Consignment as related distinct grains. | Carrier transaction and identifiable goods collection are not equivalent. | High | `convergence-analysis.md` Consignment and shipment |
| LOG-BP-005 | Equipment model | Investigate | Preserve asset, request, utilisation, and journey grains. | Their identities and lifecycles are explicitly different. | High | `convergence-analysis.md` Equipment |
| LOG-BP-006 | Transport topology | Investigate | Preserve route, planned leg, actual movement, call, port call, and terminal move. | They represent path, intent, execution, facility interaction, regulation, and handling respectively. | High | `convergence-analysis.md` Movement, leg, stop and call |
| LOG-BP-007 | Event authority | Investigate | Use a neutral event envelope only after subject roles and correction semantics converge. | DCSA, MMT, BSP, and TIC event scopes are not proven equivalent. | Medium | `convergence-analysis.md` Transport event |
| LOG-BP-008 | Documents | Investigate | Keep standard-specific transport-document classes and separate identity from version/state. | Carrier, multimodal, and generic trade scopes differ. | Medium | `convergence-analysis.md` Document pattern |
| LOG-BP-009 | Identifiers | Investigate | Keep scoped identifier properties; use structured assignments only for scheme, issuer, validity, or crosswalk requirements. | No universal scalar identifier is evidenced. | High | `convergence-analysis.md` Identifier pattern |
| LOG-BP-010 | Measurements | Investigate | Prefer MMT measurements in cargo context; do not assert blanket equivalence to BSP measurements. | Quantity context and authority differ. | High | `convergence-analysis.md` Measurement pattern |
| LOG-BP-011 | Status | Investigate | Keep aggregate-specific status codes; add temporal observations only when history/provenance is required. | Current state, state observation, and lifecycle event are different concepts. | High | `convergence-analysis.md` Status pattern |

## Open challenge: transport order / forwarding job

Issue #29 challenges whether the Booking domain needs a shared `TransportOrder`
class. The review distinguishes an **installed-model gap** from a
**standards-authorized reference-model gap**:

| Candidate | Verified grain | Challenge outcome |
|---|---|---|
| DCSA `Booking` | One carrier capacity/equipment reservation, identified by a carrier booking reference | Retain for carrier reservations; not the upstream forwarder job |
| DCSA `Shipment` | One carrier-side transport transaction | Reject as an order/job substitute |
| BSP `PurchaseOrder` / `SalesOrder` | Buyer/seller commercial order documents | Reject as freight-forwarding orchestration |
| MMT `TransportInstructions` | Transport instruction content in the documents module | Useful related evidence, but not a durable job aggregate |
| TIC `Order` | Atomic terminal handling directive and subclass of `Move` | Reject; terminal execution has a different grain |
| Forwarding job / customer instruction | One forwarder-owned instruction or job that may create several carrier bookings | Preserve as an extension point; shared-class authority remains unproven |

The current evidence supports the **semantic distinctness** of the upstream
forwarding job, but not its promotion into a standards-derived reference ontology.
Repository policy permits only classes backed by the cited standard. Absence of an
exact `TransportOrder` class name is therefore insufficient: experts must identify a
primary standard concept with matching grain, identity, lifecycle, and relationships
before any shared class is added.

Until issue #29 is resolved:

1. do not force-fit an upstream forwarding job to DCSA `Booking` or `Shipment`;
2. do not add a shared `TransportOrder` class;
3. allow consuming hubs to model a narrowly scoped local forwarding-job extension
   when their source evidence proves the grain; and
4. treat the Booking-domain ownership phrase "transport orders" as a capability
   boundary, not as an implemented canonical class.

## Rejected shortcuts

| Shortcut | Rejection reason |
|---|---|
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
