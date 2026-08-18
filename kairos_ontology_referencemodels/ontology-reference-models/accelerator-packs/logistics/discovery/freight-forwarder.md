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
   and pre-seeds outcomes for the ones it does not, so §1–§11 stay short.
2. Walk the SME through §1–§11 (business areas). For each section:
   - Read **Why it matters**.
   - Ask the **Questions**.
   - For every URI in **Maps to**, record an outcome code (see below) plus a free-text
     note.
3. Walk through §12 (Structural & lifecycle relationships). These are the cardinality
   and lifecycle decisions the ontology cannot infer.
4. Walk through §13 (Naming & identifier conventions). These determine whether outcomes
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
serves a two-mode port-to-port agent and a five-mode door-to-door 4PL. That is why
`freight-forwarder.yaml` declares the largest module menu in the pack (36 modules): it is
a *menu*, not a floor, and these five axes decide which of it the hub actually needs. Ask
them first.

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

#### Axis 4 — `financial-scope`

> *Does the system hold what you charge, what you were charged, or both against the same
> job?*
> Allowed values: `charges-only` `full-billing` `margin-management`

This axis exists because a forwarder buys and resells transport: cost and sell against one
job is its core commercial fact, not back-office detail. `bsp/financial` is `required` in
the archetype and this axis never demotes it (resolution rule 2) — what it decides is how
much of the cost/revenue apparatus comes with it.

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| `charges-only` (charge lines only; billing lives in a separate finance system) | — | `https://www.kairosflow.ai/ont/bsp/cost-accounting`, `https://www.kairosflow.ai/ont/bsp/revenue-yield` |
| `full-billing` (the system issues invoices, credit and debit notes) | `https://www.kairosflow.ai/ont/bsp/commercial` → **recommended** | — |
| `margin-management` (cost and sell held together; profitability reported per job, lane or customer) | `https://www.kairosflow.ai/ont/bsp/cost-accounting` → **required**; `https://www.kairosflow.ai/ont/bsp/revenue-yield` → **required** | — |

**Where the answer usually is.** A charge table carrying a *paired* cost and sell amount on
one row is `margin-management`, whatever the SME says the finance team calls it — the pairing
is the margin model. Confirm against the source before recording `charges-only`; the two are
easy to mistake for each other in an interview and only the source settles it.

#### Axis 5 — `customs-role`

> *Do you lodge declarations yourself, prepare the data for a broker, or only track someone
> else's filing?*
> Allowed values: `lodges` `prepares` `tracks-only`

This is §9 Q1 promoted to an axis: the answer is the difference of an entire module set, not
an attribute. `wco/customs` is `recommended` in the archetype.

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| `lodges` | `https://www.kairosflow.ai/ont/wco/customs` → **required**; `https://www.kairosflow.ai/ont/wco/party`, `https://www.kairosflow.ai/ont/wco/documents` → **recommended**; `https://www.kairosflow.ai/ont/wco/trade-facilitation` → `recommended` where the forwarder holds AEO or files preference claims | — |
| `prepares` | `https://www.kairosflow.ai/ont/wco/party` → `recommended` (declarant vs broker must be distinguishable) | — |
| `tracks-only` | — | `wco/customs#Filing`, `DutyCalculation`, `CustomsValue`; all of `https://www.kairosflow.ai/ont/wco/party`, `https://www.kairosflow.ai/ont/wco/documents`, `https://www.kairosflow.ai/ont/wco/trade-facilitation` — the declaration reduces to a status reference (§9) |

### Declared gaps you will hit in this interview

Two capability gaps recorded in
[`current/blueprint/capability-coverage.yaml`](../current/blueprint/capability-coverage.yaml)
surface repeatedly here:

- **`party-and-role-management`** — no neutral durable Party identity with qualified
  contextual role assignment exists yet. You will hit it in §2, and again in §9 where
  declarant, broker and importer of record are three roles one organisation often fills.
- **`location-and-itinerary-roles`** — same problem for locations. You will hit it in §7;
  the `dcsa/locations` subclasses are the shipped approximation, not the closure.

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
7. Does a quotation exist as a record before the job, and can one quotation produce
   several jobs — or several quotations compete for one enquiry?
8. Is the customer priced from a standing agreement, a rate card, or a per-enquiry spot
   quote? Are all three possible on the same lane?

**Maps to.** `blueprint/transport-order#TransportOrder` (the forwarding job),
`blueprint/transport-order#CarrierReservation` (per leg), `dcsa/booking#Booking` (the ocean
reservation), `Shipment`, `ShippingInstruction`, `mmt/consignment#TransportLeg`,
`bsp/commercial#RequestForQuotation`, `Quotation`, `SalesContract`,
`bsp/revenue-yield#RateCard`, `ContractRate`, `SpotRate`.

**Outcome guidance.** The grain question is settled — an internal forwarding job is **not**
equivalent to a DCSA Booking, and `TransportOrder` exists for it (issue #29 audit,
`LOG-BP-012`). What discovery must still establish is the **1..N fan-out**: confirm from
source data that one job can carry several carrier reservations, since a source that can
only ever produce one may not need the order grain separated at all.

If the answer to Q6 is yes, do **not** let the hub type the order by mode — see the
standing warning in the Scope profile. A hub proposing `OceanOrder`/`RoadOrder` subclasses,
or a single `transportMode` field on the order, has hit a known anti-pattern and should be
redirected to the leg.

Q7 and Q8 are the pricing grain. A quotation overwritten in place when the customer
re-asks is `partial` — the enquiry history is gone and win/loss can never be reconstructed.
An agreed rate stored only as a number on the job, with no reference to the agreement it
came from, is `deviates`: `ContractRate` and `SpotRate` are different commercial objects and
the job cannot say which it was priced from.

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
5. Do you handle dangerous goods? If so, do you hold the classification yourself (UN
   number, class, packing group) or only carry the shipper's declaration as a document?
6. Is the container type booked before a physical unit exists, and is that type billed
   against?

**Maps to.** `mmt/cargo#Goods`, `Weight`, `Dimension`, `Commodity`, `PackageSpecification`,
`HandlingInstructions`, `ShippingMarks`, `CargoInsurance`, `DangerousGoods`,
`mmt/equipment#TransportEquipment`, `FreightContainer`,
`dcsa/equipment#Container`, `DryContainer`, `ReeferContainer`, `TankContainer`,
`imo/dangerous-goods#DGDeclaration`, `DangerousGoodsItem`, `UNNumber`, `HazardClass`,
`PackingGroup`, `SegregationRule`.

**Outcome guidance.** Carrier-reference-only (Q3) keeps `TransportEquipment` at
`recommended` and makes ownership attributes `not-applicable`; owning equipment promotes it
to `required` and should have shown up as `2pl` on the `service-model` axis. One weight
field serving all of original/verified/chargeable is `partial`.

On Q5, note where the hazard data actually lives: classification (`mmt/cargo#DangerousGoods`
and its UN TDG subclasses) and declaration (`imo/dangerous-goods#DGDeclaration`) are separate
grains, and a hub holding only a scanned DGD with no structured UN number is `partial`, not
`conforms`. No dangerous goods at all makes the whole `imo/dangerous-goods` set
`not-applicable` — record it, do not leave it silent.

## §7 Route planning and execution

**Why it matters.** Separates the plan from what happened, and decides whether a route is
reusable master data or per-job.

**Questions**

1. Is the route a reusable lane, a job-specific plan, or both?
2. Are planned legs replaced when execution changes, or retained beside actual movements?
3. Are pickup, cross-dock, terminal, port, and delivery stops explicitly sequenced?
4. Does a location's role (pickup, port of loading, delivery) live on the location record
   or on its use within a route?
5. Do you hold carrier cut-off times and quoted transit times against the job, the lane, or
   neither?
6. Is a call at a terminal, ramp or gate a record in its own right, or only a timestamp on
   the leg?

**Maps to.** `mmt/consignment#TransportRoute`, `TransportLeg`,
`mmt/inland-transport#InlandLeg`, `InlandCarrier`, `HaulageInstructions`,
`mmt/locations#Location`, `TransportLocation`, `Warehouse`,
`mmt/route-network#Route`,
`dcsa/locations#PlaceOfReceipt`, `PortOfLoading`, `PortOfDischarge`, `PlaceOfDelivery`,
`TransshipmentPort`, `InlandTerminal`, `Depot`, `ContainerFreightStation`, `RailRamp`,
`BorderCrossing`,
`dcsa/transport-call#TransportCall`, `TruckTransportCall`, `VesselTransportCall`,
`dcsa/schedule#CutOffTime`, `TransitTime`, `SailingSchedule`.

**Outcome guidance.** Planned legs overwritten on execution is `deviates` — plan and actual
are separate grains and neither overwrites the other (`LOG-BP-006`). Roles stored on the
location record (Q4) is the `location-and-itinerary-roles` gap: record it, do not invent a
class. Port-to-port scope makes `Warehouse` and `HaulageInstructions` `not-applicable`, per
axis 2.

The `dcsa/locations` subclasses are the *itinerary role*, not a second location master. If
the hub's location table already carries one row per physical place, those subclasses attach
to the route's use of that row — mapping them onto duplicate location records is the same
mistake Q4 is asking about. A reusable lane (Q1) maps to `mmt/route-network#Route`; a
job-specific plan maps to `mmt/consignment#TransportRoute`, and a hub with both should say so
rather than force one onto the other. A missed cut-off with no `CutOffTime` record to miss
(Q5) is `partial` — the exception in §8 has no anchor without it.

## §8 Milestones and exceptions

**Why it matters.** The event subject determines the whole visibility model; getting it
wrong makes every downstream track-and-trace query ambiguous.

**Questions**

1. Which object is the primary event subject: job, booking, shipment, consignment,
   container, leg, or transport call?
2. How are planned, estimated, and actual times distinguished?
3. Can a carrier correction supersede an earlier event without changing its source ID?
4. Are exceptions separate events, statuses, or cases?
5. Do road, rail and barge legs produce milestones in the same series as the ocean leg, or
   in a separate one?

**Maps to.** `dcsa/events#Event`, `TransportEvent`, `EquipmentEvent`,
`DocumentEvent`,
`mmt/events#PickupEvent`, `DeliveryEvent`, `LoadingEvent`, `DischargeEvent`,
`TransferEvent`, `CustomsClearanceEvent`, `WarehouseStorageEvent`, `InspectionEvent`.

**Outcome guidance.** More than one primary subject in Q1 is normal for a forwarder and is
`conforms` — record each subject. A single mutable "status" column instead of an event
series is `deviates`. Corrections that reuse the source ID (Q3) make event identity
non-durable: `partial`, and flag it, because it blocks replay.

Q5 is why both event modules are in scope: `dcsa/events` is ocean-shaped (vessel departure,
gate in/out) and `mmt/events` carries pickup, delivery and cross-dock transfer. A multimodal
forwarder legitimately maps to both, and that is `conforms`, not duplication. One inland
milestone forced into a DCSA vessel event class is `deviates` — it makes every mode filter
wrong downstream.

## §9 Customs coordination

**Why it matters.** Distinguishes a forwarder that files from one that only tracks a
broker's filing — a difference of an entire module, not an attribute.

**Questions**

1. Do you lodge declarations, prepare data for a broker, or only track filing status?
2. Is one declaration linked to a consignment, house, master, document, or goods-item set?
3. Are import and export declarations separate lifecycles? Is transit (T1 / NCTS) a third?
4. Who is recorded as declarant, and is that distinguishable from the broker who filed and
   the importer of record?
5. Do you hold AEO status, file preference claims, or lodge through a single window?
6. Are duty and tax amounts held against the declaration, and do they reach the customer
   invoice as disbursements?

**Maps to.** `wco/customs#CustomsDeclaration`, `ImportDeclaration`,
`ExportDeclaration`, `TransitDeclaration`, `GoodsItem`, `DeclarationStatus`, `Filing`,
`CustomsProcedure`, `TariffClassification`, `CustomsValue`, `DutyCalculation`,
`wco/party#Declarant`, `CustomsBroker`, `FreightAgent`, `Importer`, `Exporter`, `AEOHolder`,
`wco/documents#SADForm`, `TransitDocument`, `ATACarnet`, `TIRCarnet`,
`wco/trade-facilitation#CertificateOfOrigin`, `License`, `ImportPermit`, `ExportPermit`,
`AEOCertification`, `SingleWindow`, `eFTIRecord`,
`bsp/compliance#DutyTax`, `TariffClassification`, `TradeAgreement`.

**Outcome guidance.** Q1 restates the `customs-role` axis — if the answers differ, the axis
is wrong and must be corrected before continuing, because the module set depends on it.
Track-only reduces the declaration classes to a status reference: record `partial`. Q2's
answer is the declaration grain and must be recorded explicitly; it is the most common source
of a wrong join later.

On Q4, one party field doing duty for declarant, broker and importer is `partial` — it is
the `party-and-role-management` gap again, and the roles are legally distinct even when one
organisation fills all three. On Q6, duty recorded only as a charge line with no link back to
the declaration is `partial`: the amount survives, the basis for it does not, and a
disbursement that cannot be traced to its declaration cannot be defended in an audit.

## §10 Charges, invoicing and margin

**Why it matters.** A forwarder buys transport and resells it, so cost and sell against one
job is the core commercial fact of the business — more central here than for any carrier
archetype. This is also the section that most often has no anchor in a first-pass model: a
real forwarder charge table carries both amounts on one row and links out to both an AP and
an AR document, and until this archetype declared `bsp/financial` there was nowhere owned for
it to land (gh#104).

**Questions**

1. Is there one charge line per job carrying **both** a cost and a sell amount, or two
   separate lines? If one, that pairing *is* the margin model — confirm it against the
   source, not the SME's description.
2. Is the charge code a governed list with an owner and a lifecycle, or free text?
3. Does a charge line link to the AP document from the supplier and the AR document to the
   customer, and can you get from one to the other through it?
4. What is the billing document set — invoice only, or credit notes and debit notes too?
   Is a credit note a negative invoice or its own type?
5. Are invoice header and line separate records? Is the line a `BillingDocumentLine`
   shared across document types, or a per-type line table?
6. Are payment terms, due date and outstanding amount held on the invoice, on the customer,
   or both?
7. Are surcharges (BAF, CAF, peak season, THC) separate charge lines or components of the
   freight rate?
8. Do demurrage and detention charges received from a carrier get passed through to the
   customer, and are they recognisable as such?
9. At what grain is profitability reported — job, consignment, lane, customer, branch?
10. Is the currency of a cost the same as the currency of the sell, and where does the
    exchange rate live?

**Maps to.** `bsp/financial#Charge`, `FreightCharge`, `FreightRate`, `Surcharge`,
`BunkerAdjustmentFactor`, `CurrencyAdjustmentFactor`, `TerminalHandlingCharge`,
`HandlingCharge`, `StorageCharge`, `DocumentationFee`, `TariffSchedule`,
`Invoice`, `InvoiceLine`, `BillingDocumentLine`, `CommercialInvoice`, `ProformaInvoice`,
`CreditNote`, `CreditNoteLine`, `DebitNote`, `DebitNoteLine`, `PaymentTerms`, `Payment`,
`PaymentAllocation`, `Reconciliation`, `AgingBucket`,
`bsp/cost-accounting#TransportCostItem`, `CostAllocation`, `AllocationBasis`, `CostCenter`,
`CostToServe`, `CostPerUnit`,
`bsp/revenue-yield#FreightRevenue`, `ContributionMargin`, `RevenueItem`, `AncillaryRevenue`,
`SurchargeRevenue`, `ProfitabilityScope`,
`dcsa/demurrage-detention#DemurrageCharge`, `DetentionCharge`, `FreeTimeAllowance`,
`PerDiemRate`, `DisputeRecord`,
`bsp/reference-data#MonetaryAmount`.

**Outcome guidance.** Q1 is the section's hinge. A paired cost/sell row anchors on
`bsp/financial#Charge` with `bsp/cost-accounting#TransportCostItem` and
`bsp/revenue-yield#FreightRevenue` as the two sides, and `ContributionMargin` as their
difference — do **not** let the hub invent a `MarginLine` class; the pairing is already
expressible and a local class here fragments every profitability query later.

Free-text charge codes (Q2) are `partial` and belong in the
[`governed-code-list`](../../../blueprints/patterns/governed-code-list/pattern.md) backlog.
A line table per document type (Q5) rather than a shared `BillingDocumentLine` is `partial`,
not `deviates` — the structure is right, the reuse is not. Pass-through D&D that is
indistinguishable from the forwarder's own charges (Q8) is `partial`: the amount is there,
the pass-through fact is not, and margin is overstated by exactly that amount. A single
currency field with no rate and no rate date (Q10) is `deviates` — restating a historic
margin becomes impossible.

**Where this lands in a real source.** A charge table with paired cost and sell columns, an
AR/AP document header carrying invoice date, terms, due date and outstanding, and a line
table joining the two: those three are `Charge`, `Invoice` and `BillingDocumentLine`
respectively. If the hub has all three and this section produced no `conforms`, something
was mis-anchored — re-check before moving on.

## §11 Emissions reporting

**Why it matters.** Shippers increasingly require per-consignment CO₂ from their forwarder,
who must report emissions for transport it did not run. That makes the allocation basis —
not the measurement — the modelling problem.

**Questions**

1. Do you report emissions per consignment, per job, per customer, or only in aggregate?
2. Where do emission factors come from — carrier-reported, modal default, or measured?
3. Is the activity basis tonne-kilometres, or something else?
4. Are reports a stored artefact or computed on demand?

**Maps to.** `sustainability/carbon#CarbonFootprint`, `CarbonEmission`, `TonneKilometre`,
`EmissionFactor`, `EmissionReport`, `ModalShiftMetric`.

**Outcome guidance.** No emissions reporting at all makes the whole set `not-applicable` —
common today and not a defect; record it rather than leaving it blank. A single CO₂ number
per shipment with no factor and no activity basis is `partial`: it cannot be recomputed,
audited, or split across legs. Fuel and energy consumption (`sustainability/energy`) is
deliberately **not** in this archetype — that belongs to whoever burns the fuel; if the SME
has it, they are describing own-account transport and the `service-model` axis should show
`2pl`.

## §12 Structural and lifecycle relationships

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
11. party and location roles versus durable identities;
12. charge line to job, to cost document and to revenue document — the three-way link that
    makes margin reconstructable;
13. billing document header to line, and whether the line is shared across invoice, credit
    note and debit note;
14. declaration to consignment, house, master, document or goods-item set (§9 Q2);
15. quotation to job, and quotation to the rate agreement it was priced from.

## §13 Naming and identifier conventions

Record the business terms for forwarding job, file, shipment, house, master, booking,
load, consignment, route, leg, mode, milestone, exception, charge, charge code, invoice,
credit note, cost, sell, margin, quotation, rate, and declaration. For every identifier
record the issuer, namespace, reuse policy, and whether aliases are retained.
