# Freight Forwarder — SME Discovery Guide

**Archetype:** `freight-forwarder` (see
[`blueprints/archetypes/freight-forwarder.yaml`](../../../blueprints/archetypes/freight-forwarder.yaml))
**Pack:** `accelerator-packs/logistics`
**Target sector:** Freight forwarders, NVOCCs, multimodal logistics service providers
(3PL / 4PL / control tower), and customs-capable forwarding businesses.

## §0 How to use this guide

This guide is the prose companion to the `freight-forwarder` archetype catalog. It is
consumed by the `kairos-design-discovery` skill in the `kairos-ontology-toolkit` repo,
but can also be used as a stand-alone interview script by a data architect or business
analyst.

### Interview flow

1. Answer the **Scope profile** below *first*. It selects which modules the hub needs
   and pre-seeds outcomes for the ones it does not, so §1–§9 stay short.
2. Walk the SME through §1–§9 (business areas). For each section:
   - Read **Why it matters**.
   - Ask the **Questions**.
   - For every URI in **Maps to**, record an outcome code (see below) plus a free-text
     note.
3. Walk through §10 (Structural & lifecycle relationships). These are the cardinality
   and lifecycle decisions the ontology cannot infer.
4. Walk through §11 (Naming & identifier conventions). These determine whether outcomes
   are `conforms` vs `conforms-with-rename`.

### Outcome codes (shared)

Codes are defined in
[`_schema/outcome-codes.yaml`](../../../blueprints/archetypes/_schema/outcome-codes.yaml):

| Code | When to use it |
|---|---|
| `conforms` | The customer's term + structure align with the ref-model concept. |
| `conforms-with-rename` | Structure aligns, only terminology differs (record the rename). |
| `partial` | Concept is partly present; attributes or sub-types are missing. |
| `deviates` | Customer's model materially differs — negotiate before mapping. |
| `not-applicable` | The concept is out of scope for the customer's operation. |

### What the ontology already tells us (don't ask twice)

The BSP / DCSA / MMT / WCO ref-models declare directional typed edges between classes
(`rdfs:domain` + `rdfs:range` on every `owl:ObjectProperty`). The skill should **derive**
the relationship topology from the resolved catalog graph and present it as a
confirmation checklist — not as open questions. This guide therefore focuses on
**business semantics** and **cardinality/lifecycle decisions** the ontology cannot pin
down.

### Scope profile (ask before §1)

Forwarders vary more in scope than any other archetype in this pack — the same archetype
serves a two-mode port-to-port agent and a five-mode door-to-door 4PL. These three axes
decide which modules the hub actually needs. Ask them first.

The axes, their allowed values and the **resolution rules** (promote never demote;
out-of-scope ⇒ pre-seeded `not-applicable` with `needs_confirmation: true`) are defined once
in [`README.md`](./README.md#scope-axes). Only the forwarder-specific consequences are below.

#### Axis 1 — `modes-served` (multi-valued)

> *Which transport modes do you sell? Can one consignment span several of them?*
> Allowed values: `ocean` `road` `rail` `air` `barge`

Mode targets are cited from
[`multimodal-order-leg` `pattern.yaml` `mode_bindings`](../../../blueprints/patterns/multimodal-order-leg/pattern.yaml)
— that block is the single source, this table must not diverge from it.

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| **two or more values** | `https://www.kairosflow.ai/ont/mmt/inland-transport` → **required**; `https://www.kairosflow.ai/ont/blueprint/transport-order` → **required** | — |
| `ocean` | `https://www.kairosflow.ai/ont/dcsa/booking` → **required** | — |
| `road` | `https://www.kairosflow.ai/ont/mmt/inland-transport` (`RoadLeg`) | — |
| `rail` | `https://www.kairosflow.ai/ont/mmt/inland-transport` (`RailLeg`); grain 3 target is **TAF TSI**, catalogued as `https://www.kairosflow.ai/ont/rail/path-request`, `https://www.kairosflow.ai/ont/rail/consignment`, `https://www.kairosflow.ai/ont/rail/party` | — |
| `air` | `https://www.kairosflow.ai/ont/mmt/transport-means` (`Aircraft`); grain 3 target is **IATA ONE Record**, `https://onerecord.iata.org/ns/cargo` — **reference-only**, resolve via the catalog, never add to a pack's includes | — |
| `barge` | `https://www.kairosflow.ai/ont/mmt/inland-transport` (`BargeLeg`), `mmt/transport-means#BargeVessel` | — |
| *mode not selected* | — | that mode's leg subclass (`RoadLeg` / `RailLeg` / `BargeLeg`) and means-of-transport class |
| **exactly one value** | — | `blueprint/transport-order#TransportOrder` may drop to `recommended` *only* if the forwarder also never subcontracts more than one carrier per job — see §3 |

**Standing warning.** A multi-mode answer must **never** produce `AirOrder` / `RailOrder` /
`OceanOrder` subclasses or an `orderTransportMode` scalar. Mode lives on the leg (grain 2)
and the mode-bound standard binds at the carrier reservation (grain 3). This is the
rejected anti-pattern in
[`pattern.md`](../../../blueprints/patterns/multimodal-order-leg/pattern.md) — if the hub
proposes it, redirect to the leg.

#### Axis 2 — `geographic-scope`

> *Do you sell port-to-port, door-to-door, or both?*
> Allowed values: `port-to-port` `door-to-door` `both`

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| `door-to-door` or `both` | `https://www.kairosflow.ai/ont/mmt/inland-transport` → **required**; `mmt/consignment#TransportRoute`, `TransportLeg` → **required**; `mmt/locations#Warehouse` → `recommended` | — |
| `port-to-port` | — | pre-carriage / on-carriage locations, `mmt/inland-transport#HaulageInstructions`, `mmt/locations#Warehouse` |

This is the same rule `shipping-carrier.md` §1 states in prose; both cite this axis so the
two cannot drift.

#### Axis 3 — `service-model` (multi-valued)

> *Where do you sit on the outsourcing ladder — and do you sit in more than one place?*
> Allowed values: `1pl` `2pl` `3pl` `4pl`

Record every value that applies — a forwarder that is also an NVOCC is `3pl` **and** `2pl`.
See [`README.md`](./README.md#picking-a-starting-archetype) for why this is a routing hint
and never a substitute for axes 1 and 2.

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| `4pl` | `blueprint/transport-order#TransportOrder` → **required**; every leg expected to carry a `CarrierReservation` → `CarrierReservation` **required** | — |
| `3pl` | archetype defaults apply unchanged | — |
| `2pl` (asset carrier work alongside forwarding) | `mmt/transport-means`, `mmt/equipment` → `recommended` | — |
| `1pl` only | — | this is a shipper running own transport; `freight-forwarder` is the wrong archetype — stop and reselect |

### Declared gaps you will hit in this interview

Two capability gaps recorded in
[`current/blueprint/capability-coverage.yaml`](../current/blueprint/capability-coverage.yaml)
surface repeatedly here:

- **`party-and-role-management`** — no neutral durable Party identity with qualified
  contextual role assignment exists yet. You will hit it in §2.
- **`location-and-itinerary-roles`** — same problem for locations. You will hit it in §7.

For both, do **not** let the SME's answer drift into "so what class should we invent".
Record the business requirement in the free-text note and flag it for the blueprint
layer's gap-closure backlog. Inventing a class during a live discovery session produces
exactly the kind of untracked, divergent local extension the archetype catalog exists to
prevent. The intended shape is
[`qualified-role-assignment`](../../../blueprints/patterns/qualified-role-assignment/pattern.md).

---

## §1 Service and principal model

**Why it matters.** Determines whether the forwarder acts only as agent or also contracts
as principal/NVOCC, and confirms the Scope profile answers against how the business
actually sells.

**Questions**

1. Do you arrange transport as agent, contract as principal, or both?
2. Which modes are supported, and can one consignment span several modes?
3. Do you offer door-to-door, port-to-port, or both?
4. Is any mode sold only as a subcontracted add-on rather than a standalone service?

**Maps to.**
`mmt/party#FreightForwarder`, `Carrier`,
`mmt/consignment#TransportRoute`, `TransportLeg`,
`mmt/inland-transport#InlandLeg`, `RoadLeg`, `RailLeg`, `BargeLeg`,
`mmt/transport-means#LogisticsMeansOfTransport`, `Aircraft`, `RailVehicle`, `BargeVessel`.

**Outcome guidance.** Q2 and Q3 restate axes 1 and 2 of the Scope profile — if the answers
differ from what was captured there, the Scope profile is wrong and must be corrected
before continuing, because the module set depends on it. Agent-only ⇒ note it for §4;
it does not by itself make any class `not-applicable`, since an agent still books carriers.
A leg subclass for a mode the forwarder does not sell is `not-applicable`, per axis 1.

## §2 Party identity and contextual roles

**Why it matters.** One organisation may be customer, shipper, consignor, consignee,
carrier, broker, and notify party in different contexts.

**Questions**

1. Is there one party master independent of transaction roles?
2. Are shipper and consignor synonyms in your operation, or contextually distinct?
3. Are carrier contracts held against the carrier organisation or a service-specific role?
4. Do roles have validity dates, branch scope, or compliance state?

**Maps to.** `bsp/party#TradeParty`, `FreightForwarder`,
`mmt/party#TransportParty`, `Consignor`, `Consignee`, `Carrier`.

**Outcome guidance.** Separate masters per role indicate `deviates`; do not assume the
duplicate records represent different real-world parties. A single master with role flags
is `partial`, not `deviates` — it is an allowed physical shortcut under
[`qualified-role-assignment`](../../../blueprints/patterns/qualified-role-assignment/pattern.md).
This is the `party-and-role-management` gap: record the requirement, do not invent a class.

## §3 Quote, booking, and shipment handoff

**Why it matters.** Forwarders may hold an internal job/order before carrier booking and
may create several carrier bookings for one customer instruction.

**Questions**

1. What is the durable customer instruction or forwarding-job identifier?
2. Can one forwarding job create multiple carrier bookings?
3. Are carrier booking changes versioned or overwritten?
4. Is a DCSA Shipment represented directly, or only through carrier references?
5. Which legs does the forwarder subcontract, and which does it execute itself? A leg with
   no carrier reservation is normal — it means the forwarder ran it.
6. Does any order span more than one mode? If yes, confirm the customer is quoted one
   door-to-door price against one order, not one order per mode.

**Maps to.** `blueprint/transport-order#TransportOrder` (the forwarding job),
`blueprint/transport-order#CarrierReservation` (per leg), `dcsa/booking#Booking` (the ocean
reservation), `Shipment`, `ShippingInstruction`, `mmt/consignment#TransportLeg`.

**Outcome guidance.** The grain question is settled — an internal forwarding job is **not**
equivalent to a DCSA Booking, and `TransportOrder` exists for it (issue #29 audit,
`LOG-BP-012`). What discovery must still establish is the **1..N fan-out**: confirm from
source data that one job can carry several carrier reservations, since a source that can
only ever produce one may not need the order grain separated at all.

If the answer to Q6 is yes, do **not** let the hub type the order by mode — see the
standing warning in the Scope profile. A hub proposing `OceanOrder`/`RoadOrder` subclasses,
or a single `transportMode` field on the order, has hit a known anti-pattern and should be
redirected to the leg.

## §4 Master and house consolidation

**Why it matters.** Consolidation is the principal cross-archetype difference from a
single carrier transaction, and it is what makes a forwarder a principal rather than an
agent on the document.

**Questions**

1. Can one house consignment participate in more than one master consignment over time?
2. Can a master contain houses with different consignors or consignees?
3. How are deconsolidation, rollover, split, and merge history retained?
4. Are direct shipments represented without a master/house split?

**Maps to.** `mmt/consignment#Consignment`, `MasterConsignment`,
`HouseConsignment`, `ConsignmentItem`.

**Outcome guidance.** A pure agent that never consolidates and never issues its own
document makes `MasterConsignment` and `HouseConsignment` `not-applicable` — but confirm
against §5 first, since many agents still receive master documents they must record.
History discarded on rollover or split is `partial`, not `conforms`.

## §5 Transport documents

**Why it matters.** Whether the forwarder issues its own document decides if it is a
contractual principal, and drives the document identity and lifecycle the model must carry.

**Questions**

1. Do you issue house waybills while receiving carrier master waybills?
2. Can document identity persist across amendments and re-issuance?
3. Are surrender, release, and cancellation modelled as events or current flags?
4. Which document types do you issue or handle per mode (B/L, sea waybill, AWB, CMR, CIM)?

**Maps to.** `mmt/documents#TransportDocument`, `MasterWaybill`, `HouseWaybill`.

**Outcome guidance.** No house-document issuance ⇒ `HouseWaybill` is `not-applicable` and
§4's house concepts likely follow. Current-state flags instead of surrender/release events
are `partial` — the lifecycle is present but not reconstructable. Per-mode document types
in Q4 must agree with the `modes-served` axis; a document type for an unsold mode is a
signal the axis was answered too narrowly.

## §6 Cargo, equipment, and allocation

**Why it matters.** Decides whether equipment is a first-class tracked asset or only a
carrier reference, and whether requested and allocated equipment are separate records.

**Questions**

1. Is equipment requested by type/quantity before a physical unit is known?
2. At what point is a container or other unit assigned?
3. Do you own equipment, track third-party equipment, or only retain carrier references?
4. Are cargo weight and dimensions original, verified, chargeable, or all three?

**Maps to.** `mmt/cargo#Goods`, `Weight`, `Dimension`,
`mmt/equipment#TransportEquipment`, `FreightContainer`.

**Outcome guidance.** Carrier-reference-only (Q3) keeps `TransportEquipment` at
`recommended` and makes ownership attributes `not-applicable`; owning equipment promotes it
to `required` and should have shown up as `2pl` on the `service-model` axis. One weight
field serving all of original/verified/chargeable is `partial`.

## §7 Route planning and execution

**Why it matters.** Separates the plan from what happened, and decides whether a route is
reusable master data or per-job.

**Questions**

1. Is the route a reusable lane, a job-specific plan, or both?
2. Are planned legs replaced when execution changes, or retained beside actual movements?
3. Are pickup, cross-dock, terminal, port, and delivery stops explicitly sequenced?
4. Does a location's role (pickup, port of loading, delivery) live on the location record
   or on its use within a route?

**Maps to.** `mmt/consignment#TransportRoute`, `TransportLeg`,
`mmt/inland-transport#InlandLeg`, `InlandCarrier`, `HaulageInstructions`,
`mmt/locations#Location`, `TransportLocation`, `Warehouse`.

**Outcome guidance.** Planned legs overwritten on execution is `deviates` — plan and actual
are separate grains and neither overwrites the other (`LOG-BP-006`). Roles stored on the
location record (Q4) is the `location-and-itinerary-roles` gap: record it, do not invent a
class. Port-to-port scope makes `Warehouse` and `HaulageInstructions` `not-applicable`, per
axis 2.

## §8 Milestones and exceptions

**Why it matters.** The event subject determines the whole visibility model; getting it
wrong makes every downstream track-and-trace query ambiguous.

**Questions**

1. Which object is the primary event subject: job, booking, shipment, consignment,
   container, leg, or transport call?
2. How are planned, estimated, and actual times distinguished?
3. Can a carrier correction supersede an earlier event without changing its source ID?
4. Are exceptions separate events, statuses, or cases?

**Maps to.** `dcsa/events#Event`, `TransportEvent`, `EquipmentEvent`,
`DocumentEvent`.

**Outcome guidance.** More than one primary subject in Q1 is normal for a forwarder and is
`conforms` — record each subject. A single mutable "status" column instead of an event
series is `deviates`. Corrections that reuse the source ID (Q3) make event identity
non-durable: `partial`, and flag it, because it blocks replay.

## §9 Customs coordination

**Why it matters.** Distinguishes a forwarder that files from one that only tracks a
broker's filing — a difference of an entire module, not an attribute.

**Questions**

1. Do you lodge declarations, prepare data for a broker, or only track filing status?
2. Is one declaration linked to a consignment, house, master, document, or goods-item set?
3. Are import and export declarations separate lifecycles?

**Maps to.** `wco/customs#CustomsDeclaration`, `ImportDeclaration`,
`ExportDeclaration`.

**Outcome guidance.** Track-only (Q1) keeps `wco/customs` at `optional` and reduces the
declaration classes to a status reference — record `partial`. Lodging declarations promotes
`wco/customs` to `required`. Q2's answer is the declaration grain and must be recorded
explicitly; it is the most common source of a wrong join later.

## §10 Structural and lifecycle relationships

Confirm explicitly:

1. forwarding job to carrier booking cardinality;
2. booking to shipment cardinality;
3. shipment to consignment cardinality;
4. master to house consolidation and history;
5. consignment to item composition;
6. route to ordered leg composition;
7. leg to mode-bearing subclass, and leg to carrier reservation (`0..1`);
8. equipment request to physical allocation timing;
9. event-to-subject cardinality and correction behavior;
10. document identity to version/state lifecycle;
11. party and location roles versus durable identities.

## §11 Naming and identifier conventions

Record the business terms for forwarding job, file, shipment, house, master, booking,
load, consignment, route, leg, mode, milestone, and exception. For every identifier record
the issuer, namespace, reuse policy, and whether aliases are retained.
