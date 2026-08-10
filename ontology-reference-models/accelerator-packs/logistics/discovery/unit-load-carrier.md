# Unit-Load-Carrier — SME Discovery Guide

**Archetype:** `unit-load-carrier` (see
[`blueprints/archetypes/unit-load-carrier.yaml`](../../../blueprints/archetypes/unit-load-carrier.yaml))
**Pack:** `accelerator-packs/logistics`
**Target sector:** Non-containerised unit-load carriers — trailer, swap-body
and cassette operators running ro-ro / short-sea ferry legs bookended by
own-account and subcontracted road haulage. Includes accompanied traffic
(driver travels with the trailer) and unaccompanied traffic (trailer crosses
without its driver).

## §0 How to use this guide

This guide is the prose companion to the `unit-load-carrier` archetype
catalog. It is consumed by the `kairos-design-discovery` skill in the
`kairos-ontology-toolkit` repo, but can also be used as a stand-alone
interview script by a data architect or business analyst.

### Interview flow

1. Walk the SME through §1–§19 (business areas). For each section:
   - Read **Why it matters**.
   - Ask the **Questions**.
   - For every URI in **Maps to**, record an outcome code (see below)
     plus a free-text note.
2. Walk through §20 (Structural & lifecycle relationships). These are
   the cardinality and lifecycle decisions the ontology cannot infer.
3. Walk through §21 (Naming & identifier conventions). These determine
   whether outcomes are `conforms` vs `conforms-with-rename`.

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

The DCSA / MMT / IMO / WCO ref-models declare directional typed edges
between classes (`rdfs:domain` + `rdfs:range` on every `owl:ObjectProperty`).
The skill should **derive** the relationship topology from the resolved
catalog graph and present it as a confirmation checklist — not as open
questions. This guide therefore focuses on **business semantics** and
**cardinality/lifecycle decisions** the ontology cannot pin down.

### Two declared gaps you will hit repeatedly in this interview

Unlike `shipping-carrier` and `freight-forwarder`, this archetype runs
straight into two capability gaps recorded in
[`current/blueprint/capability-coverage.yaml`](../current/blueprint/capability-coverage.yaml):

- **`empty-equipment-repositioning`** — no parent class for empty
  equipment availability / repositioning exists anywhere in this pack. See
  §11.
- **`trade-lane-and-market-segment`** — no class for trade lane / market
  segment exists in the commercial ontology. See §19.

For both, do **not** let the SME's answer drift into "so what class should
we invent" — record the business requirement in the free-text note and flag
it for the blueprint layer's gap-closure backlog instead. Inventing a class
during a live discovery session produces exactly the kind of untracked,
divergent local extension the archetype catalog exists to prevent.

---

## §1 Booking / order intake

**Why it matters.** Drives whether the model needs a booking-request →
confirmed-booking lifecycle distinct from the transport document, and
whether requested vs. utilized equipment are tracked as separate records.

**Questions**
1. Do shippers book online/EDI against a rate/contract, or is every booking
   a manual quote-and-confirm cycle?
2. Is a booking always for exactly one trailer/swap-body, or can one
   booking cover a multi-trailer consignment (e.g. a groupage operator's
   daily trunk)?
3. Do you distinguish the equipment *type* requested at booking time from
   the *specific unit* assigned at gate-in?
4. Do you support both spot bookings and standing (contract) capacity
   allocations on a given sailing?

**Maps to.**
`dcsa/booking#Booking`, `BookingRequest`, `ConfirmedBooking`, `Shipment`,
`ShippingInstruction`, `CargoItem`, `Commodity`, `RequestedEquipment`,
`UtilizedTransportEquipment`, `TransportPlanLeg`.

**Outcome guidance.** No requested/utilized split ⇒ `RequestedEquipment`
and `UtilizedTransportEquipment` collapse to `partial` (one entity doing
both jobs). No standing capacity allocation ⇒ treat as `conforms` with a
note that `ConfirmedBooking` never carries a contract reference.

---

## §2 Transport document (CMR / road waybill)

**Why it matters.** Unlike `shipping-carrier`, the primary contractual
transport document for this archetype is the road consignment note (CMR),
not an ocean bill of lading. Getting the primary-document anchor right
changes which lifecycle events (issuance, signature, surrender) the model
must support.

**Questions**
1. Do you issue your own CMR, or does the subcontracted haulier issue it
   under their own operator details?
2. Do you also issue rail consignment notes (CIM) for any intermodal legs?
3. Is a single cargo manifest produced per ferry sailing covering every
   trailer aboard, and who consumes it (port authority, ferry operator,
   customs)?
4. Do you issue a customs declaration as part of the same document set, or
   is that always a separate downstream filing (see §16)?
5. Do delivery instructions travel with the CMR, or as a separate document
   to the consignee?

**Maps to.**
`mmt/documents#TransportDocument`, `RoadConsignmentNote`,
`RailConsignmentNote`, `TransportInstructions`, `DeliveryInstructions`,
`CargoManifest`, `DangerousGoodsDeclaration`, `CustomsDeclaration` (MMT),
`CertificateOfOrigin`.

**Outcome guidance.** Subcontracted haulier issues their own CMR ⇒
`RoadConsignmentNote` is `partial` in your system (you hold a reference, not
the authoritative record). No intermodal rail leg ⇒ `RailConsignmentNote`
is `not-applicable`.

---

## §3 Consignment & movement

**Why it matters.** This is where the "physical trip" grain — distance,
toll, emissions, predecessor/successor chaining — either gets a home or
gets silently folded into the consignment record, which is a known
grain-collision risk flagged by CR-RM-07 §9.3.

**Questions**
1. Is a "consignment" in your system the commercial transaction, the goods
   collection, or the physical trip a tractor unit makes? (If your answer
   is "it depends", that is the grain collision — probe further.)
2. Do house/master consignment splits matter to you (e.g. you consolidate
   multiple shippers' trailers under one ferry booking), or is every
   trailer its own consignment end to end?
3. Do you track a transport route as a reusable network object (a standing
   lane), or only as the realized sequence of legs on one shipment?
4. Does a single trip (tractor + trailer, gate to gate) get its own record
   independent of the commercial consignment it is carrying?

**Maps to.**
`mmt/consignment#Consignment`, `ConsignmentItem`, `GoodsItem`,
`TransportLeg`, `TransportRoute`, `TransportService`,
`TransportServiceExecution`, `TransportMovement`, `MasterConsignment`,
`HouseConsignment`.

**Outcome guidance.** If "consignment" conflates commercial transaction and
physical trip, record `TransportMovement` as `deviates` and flag the
grain-collision explicitly in the discovery report — this is exactly the
collision CR-RM-04's anti-pattern register is meant to catch. No
consolidation ⇒ `MasterConsignment` / `HouseConsignment` are
`not-applicable`.

---

## §4 Cargo characteristics

**Questions**
1. Do you model cargo as commodities (HS-class level) or as goods items per
   package/pallet inside the trailer?
2. Do you carry temperature-controlled cargo requiring set-point tracking
   at trailer level (see also §10 reefer trailer equipment)?
3. Do you handle shipper-provided handling, quarantine (e.g. food or
   animal products crossing a food-safety border), or disposal
   instructions?
4. Do you carry cargo insurance on behalf of customers, or never?
5. Do you record dimensions/weight at trailer level, pallet level, or both?

**Maps to.**
`mmt/cargo#Goods`, `PackageSpecification`, `Weight`, `Dimension`,
`CargoMeasurement`, `HandlingInstructions`, `ShippingMarks`,
`CargoInsurance`, `QuarantineInstructions`, `DisposalInstructions`.

**Outcome guidance.** No quarantine-controlled cargo ⇒
`QuarantineInstructions` is `not-applicable`. Weight/dimension captured only
at trailer level ⇒ `Dimension`/`CargoMeasurement` at goods-item level are
`partial`.

---

## §5 Parties & roles (own-account vs subcontracted haulier)

**Why it matters.** This is the distinction that barely exists in
`shipping-carrier` or `freight-forwarder` but is a first-order concern
here: does the trailer move behind your own tractor and driver, or behind a
subcontracted haulier's? Both use the *same* ref-model class
(`Carrier`/`InlandCarrier`, see §9) — the split is carried as an attribute
or qualified role, not a subclass. Confirm the SME's system reflects that
same decision rather than maintaining two parallel party hierarchies.

**Questions**
1. Do you maintain a single haulier master with an own-account/subcontracted
   flag, or two separate registries?
2. When a subcontracted haulier is used, do you still record the driver and
   tractor as first-class entities, or only the haulier company?
3. Do you distinguish Notify Party as a structured party, or a free-text
   field on the CMR?
4. Do you maintain a customs broker master (their own filings vs. yours),
   given the short-sea customs exposure (§16)?
5. Do you track terminal-operator relationships separately for the ro-ro
   terminal at each end of the crossing?

**Maps to.**
`mmt/party#Carrier`, `Consignor`, `Consignee`, `TransportParty`,
`FreightForwarder`, `NotifyParty`, `CustomsBroker`, `TerminalOperator`,
`WarehouseOperator`.

**Outcome guidance.** Two separate registries for own-account vs.
subcontracted ⇒ `deviates` — negotiate a merge onto one `Carrier`/
`InlandCarrier` party with an attribute discriminator before mapping, per
the archetype's own design decision (see the YAML §5 comment). No warehouse
operations ⇒ `WarehouseOperator` is `not-applicable`.

---

## §6 Locations & geographic network

**Why it matters.** Ro-ro terminal, border crossing, and depot are the
three location types that carry the most operational weight for this
sector — more so than the deep-sea port network that dominates
`shipping-carrier`.

**Questions**
1. Do you model the ro-ro terminal as a Port, a Terminal, or both (arrival
   side vs. departure side of the same physical facility)?
2. Do you have a structured border-crossing location distinct from the
   terminal itself (e.g. a customs post some distance from the ferry
   berth)?
3. Do you operate or contract depots for empty trailer/swap-body storage
   between loads?
4. Do you distinguish road terminals used purely for tractor/trailer
   marshalling from the ro-ro terminal itself?

**Maps to.**
`dcsa/locations#Port`, `Terminal`, `BorderCrossing`, `Depot`,
`mmt/locations#Location`, `TransportLocation`, `RoadTerminal`, `Warehouse`.

**Outcome guidance.** Border crossing co-located with the terminal (common
for a dedicated ro-ro-only port) ⇒ `BorderCrossing` is
`conforms-with-rename` onto the same physical record as `Terminal`, not a
separate location. No dedicated depot network ⇒ `Depot` is `partial` (ad
hoc parking, not a managed facility).

---

## §7 Transport calls

**Questions**
1. Do you record a Truck Transport Call at the terminal gate distinct from
   the Vessel Transport Call for the ferry itself?
2. Do intermodal legs (rail, barge) ever appear on the same network, or is
   the model exclusively truck + ferry?

**Maps to.**
`dcsa/transport-call#TransportCall`, `TruckTransportCall`,
`VesselTransportCall`, `RailTransportCall`, `BargeTransportCall`.

**Outcome guidance.** No intermodal legs ⇒ `RailTransportCall` and
`BargeTransportCall` are `not-applicable`. `TruckTransportCall` should be
`required`-tier confirmed even for otherwise minimal implementations — it
is the one call type genuinely unique to this archetype among the three
logistics archetypes shipped so far.

---

## §8 Vessel / ferry operation (short-sea ro-ro leg)

**Why it matters.** Vessel capacity here is measured in lane metres, not
TEU — a structural difference from `shipping-carrier` that this archetype
exists specifically to surface.

**Questions**
1. Is ferry capacity planned and sold in lane metres, number of trailer
   slots, or both?
2. Do you own/charter the ferry tonnage, or purchase slot capacity from a
   ferry operator (analogous to slot-chartering in `shipping-carrier`)?
3. Do multiple trailers from different bookings get grouped as one
   "convoy" unit for the crossing (e.g. for driver logistics on
   accompanied crossings)?
4. Do you publish a fixed sailing schedule with cut-off times to shippers,
   given ferries typically run several fixed departures a day?
5. Do you track vessel/ferry statutory identifiers (IMO number, MMSI,
   flag state) yourself, or rely entirely on the ferry operator's data?

**Maps to.**
`mmt/transport-means#Vessel`, `RoadVehicle`, `LogisticsConvoy`,
`imo/vessel-registry#Vessel`, `VesselType`, `VesselCapacity`, `Fleet`,
`FlagState`, `VesselOperationalStatus`, `IMONumber`, `MMSI`,
`dcsa/schedule#SailingSchedule`, `CutOffTime`, `imo/port-call#PortCall`,
`BerthStay`, `SeaLeg`.

**Declared gap — lane-metre capacity.** No class in this pack models
lane-metre capacity specifically. `VesselCapacity` is the closest real
class — it is a generic capacity holder with no lane-metre-specific
structure (no length-based unit, no distinction between deck-level
capacity and total vessel capacity). Record the SME's actual capacity
model (lane metres per deck, total lane metres, trailer-slot count) as a
free-text note against `VesselCapacity`'s outcome, not as a separate
mapped concept — there is nothing to map it to yet. Flag this explicitly
in the discovery report as an open capability gap
(`capability-coverage.yaml` id `empty-equipment-repositioning`'s sibling
gap is the one to cite alongside it, since both stem from the same
"non-containerised units don't fit the container-shaped classes" root
cause).

**Outcome guidance.** Slot-purchase only, no owned/chartered tonnage ⇒ most
of `imo/vessel-registry#*` is `not-applicable`, mirroring the slot-charter
case in `shipping-carrier` §5.

---

## §9 Road / inland leg & haulage (own-account vs subcontracted)

**Why it matters.** This is the leg-level counterpart to §5's party-level
distinction: is the road leg itself flagged own-account vs. subcontracted,
independent of which haulier company is on the party record? And does the
handover event capture whether traffic was accompanied or unaccompanied?

**Questions**
1. Is "own-account vs subcontracted" recorded on the leg, the haulier
   party, the tractor unit, or all three — and if more than one, are they
   ever inconsistent in practice?
2. On an accompanied crossing, does the driver's handover event get
   recorded (e.g. driver books into the terminal, then reappears at the
   destination terminal with the same trailer)?
3. On an unaccompanied crossing, who initiates the handover at the
   departure terminal, and who collects at the destination terminal — is
   that captured as a structured handover event or only inferred from
   gate-in/gate-out timestamps?
4. Do you maintain haulage instructions as a structured document
   independent of the CMR (e.g. internal dispatch instructions to the
   tractor driver)?

**Maps to.**
`mmt/inland-transport#InlandCarrier`, `RoadLeg`, `InlandLeg`,
`InlandTerminal`, `HaulageInstructions`, `HandoverEvent`, `RailLeg`,
`BargeLeg`.

**Outcome guidance.** Own-vs-subcontracted recorded only on the party
(§5), never on the leg ⇒ `RoadLeg` is `conforms` but note that leg-level
cost/liability attribution (see §19) depends on joining back to the party
record, which is a design decision worth surfacing, not a defect. No
distinct handover-event capture for accompanied vs. unaccompanied traffic
⇒ `HandoverEvent` is `partial` — the event exists implicitly in gate
timestamps but the accompanied/unaccompanied distinction itself is not a
first-class attribute anywhere.

---

## §10 Equipment fleet (non-containerised)

**Why it matters.** The equipment anchor for this archetype is
deliberately `mmt/equipment#TransportEquipment`, not
`dcsa/equipment#Container` — per CR-RM-07 §9.2's correction to the
canonical equipment-asset anchor. Confirming this with the SME early avoids
a false start where the interview drifts toward container-shaped questions
(ISO 6346 check digit, TEU) that do not apply to a trailer fleet.

**Questions**
1. What equipment types are in your fleet: standard trailer, curtain-sider,
   reefer trailer, swap body, cassette?
2. Do you use ISO 6346-style container numbering for any unit, or does your
   fleet use a proprietary trailer-fleet numbering scheme (see §21)?
3. Do you carry any genuinely containerised equipment on chassis as a
   minority of the fleet (mixed-fleet operators)?
4. Do you seal trailers for customs/security purposes, and if so, at what
   point in the journey?

**Maps to.**
`mmt/equipment#TransportEquipment`, `TrailerUnit`, `SwapBody`, `Pallet`,
`Seal`, `TemperatureSettingInstructions`, `FreightContainer`,
`ReeferContainer`, `TankContainer`.

**Outcome guidance.** Fleet is 100% trailer/swap-body with no containers on
chassis ⇒ `FreightContainer`, `ReeferContainer`, `TankContainer` are
`not-applicable` — this is the expected, common case for this archetype,
not a gap. No reefer trailers ⇒ `TemperatureSettingInstructions` is
`not-applicable`.

---

## §11 Empty equipment availability & repositioning (declared gap)

**Why it matters.** Every unit-load carrier repositions empty trailers,
swap bodies, and cassettes across its network to balance supply against
demand by lane — and, per `capability-coverage.yaml`
(id `empty-equipment-repositioning`), **no parent class for this exists
anywhere in this pack's ontologies today**, for containers or for
non-containerised equipment alike.

**Questions**
1. Do you plan empty repositioning centrally (network optimisation) or
   locally (depot-by-depot ad hoc)?
2. Do you track real-time empty-equipment availability per depot/terminal
   in your own systems, or rely on the terminal operator's yard system?
3. Is a repositioning move recorded as its own trip type (distinguishing
   it from a revenue-carrying trip), or only inferred from the absence of
   a consignment reference on a leg?
4. Do you forecast repositioning need by lane, and if so, on what horizon?

**Maps to.** `mmt/events#TransferEvent` is the closest real class — a
repositioning move is structurally a transfer of an equipment unit between
two locations with no revenue cargo attached — but it carries none of this
sector's network-optimisation or availability-forecast semantics.

**Outcome guidance.** Regardless of the SME's answer, `TransferEvent` will
be at best `partial` for this business area — this is expected. Capture the
SME's actual repositioning model (planning horizon, trigger, ownership) in
the free-text note in full, because this is the input the blueprint layer
needs to eventually close the `empty-equipment-repositioning` gap with a
real class. Do **not** record `not-applicable` here just because
`TransferEvent` is a poor fit — every carrier reposition empties in
practice; the gap is in the model, not the business.

---

## §12 Terminal / ro-ro handling

**Why it matters.** Roll-on/roll-off is a horizontal move — the unit is
driven or towed on and off under its own power or by a terminal tractor —
structurally distinct from a container terminal's lift-on/lift-off
crane operation.

**Questions**
1. Do you use terminal tractors for trailer shunting within the terminal,
   and are those tracked as terminal-owned or carrier-owned assets?
2. Is a "carrier visit" (your operational touchpoint with the ferry
   operator at this terminal) recorded distinctly from the vessel's own
   port call?
3. Do you record individual roll-on / roll-off moves per trailer, or only
   aggregate counts per sailing?

**Maps to.**
`tic/terminal-infrastructure#TerminalTractor`,
`tic/handling-operations#CarrierVisit`, `HorizontalMove`, `Move`,
`tic/locations#Berth`, `QuaySide`.

**Outcome guidance.** No terminal-tractor tracking (driver drives the
trailer on/off directly) ⇒ `TerminalTractor` is `not-applicable`. Only
aggregate counts per sailing ⇒ `HorizontalMove` is `partial` (the class
exists conceptually in your operation but is not instantiated per unit in
your system).

---

## §13 Track & trace events

**Why it matters.** The customer-facing visibility backbone — which
milestones a shipper can see for their trailer's crossing.

**Questions**
1. Which milestones do you publish externally (booking, gate-in at origin
   terminal, loaded on ferry, sailed, discharged, gate-out at destination
   terminal, delivered)?
2. Do you publish separate customs-clearance and border-crossing events,
   given the sector's short-sea customs exposure?
3. Are gate-in/gate-out events recorded against the trailer, the tractor,
   or both?

**Maps to.**
`mmt/events#ArrivalEvent`, `DepartureEvent`, `PickupEvent`, `DeliveryEvent`,
`LoadingEvent`, `DischargeEvent`, `CustomsClearanceEvent`,
`dcsa/events#TransportEvent`, `EquipmentEvent`, `GateInEvent`,
`GateOutEvent`, `BorderCrossingEvent`, `CustomsEvent`.

**Outcome guidance.** `BorderCrossingEvent` and `CustomsEvent` are tiered
`required` in the archetype (unlike `shipping-carrier`, where they are
`optional`) because short-sea border exposure is the norm for this sector,
not an edge case — if the SME reports these as `not-applicable`, treat that
as a signal to re-confirm the sector fit before proceeding, not as a normal
outcome.

---

## §14 Detention & equivalent delay charges

**Why it matters.** This archetype's centre of gravity is equipment
(trailer) detention, not cargo demurrage — the tiers in the catalog
deliberately invert `shipping-carrier`'s, where cargo demurrage sits at
`recommended` and detention is the secondary concept.

**Questions**
1. Do you charge detention when a consignee holds a trailer beyond agreed
   free time?
2. What free-time structure applies (days by lane, customer tier, or
   equipment type)?
3. Do you ever charge demurrage-equivalent fees for cargo held at the ro-ro
   terminal itself (as opposed to trailer detention at the consignee)?
4. Is there a formal dispute/waiver process for detention charges, or are
   they handled as ad hoc credit notes?

**Maps to.**
`dcsa/demurrage-detention#DetentionCharge`, `FreeTimeAllowance`,
`PerDiemRate`, `DemurrageDetentionTariff`, `DetentionEvent`,
`DemurrageCharge`, `DisputeRecord`.

**Outcome guidance.** No terminal-side cargo demurrage (typical — most
delay cost in this sector is trailer detention at the consignee, not cargo
held at the ro-ro terminal) ⇒ `DemurrageCharge` is `not-applicable`. This
is the expected default outcome for this archetype, in contrast to
`shipping-carrier` where the reverse is expected.

---

## §15 Dangerous goods on trailers

**Questions**
1. Do you carry dangerous goods on trailers? If yes, under ADR (road) or
   IMDG (sea leg) rules, or do you have to reconcile both regimes for the
   same load across the ferry crossing?
2. Do you maintain segregation/stowage-category logic for the ferry deck
   assignment, or is that entirely the ferry operator's responsibility?
3. Do you store EmS/Tremcard, flash-point, and emergency-contact data per
   booking, or only for high-risk hazard classes?
4. Do you refuse any hazard classes outright (e.g. certain Class 1
   explosives) regardless of ferry-operator acceptance?

**Maps to.**
`mmt#DangerousGoods`, `FlammableLiquid`, `FlammableGas`, `CorrosiveSubstance`,
`imo/dangerous-goods#DangerousGoodsItem`, `HazardClass`, `UNNumber`,
`PackingGroup`, `FlashPoint`, `EmergencySchedule`, `SegregationRule`,
`DGDeclaration`.

**Outcome guidance.** Carrier refuses all DG ⇒ entire module is
`not-applicable`, same as `shipping-carrier`. Reconciling ADR and IMDG
regimes for the same physical load ⇒ record as `deviates` with a note —
the ontology does not currently model dual-regime DG classification, only
a single hazard-class assignment per goods item.

---

## §16 Customs & border formalities (short-sea exposure)

**Why it matters.** This sector has real, recurring customs exposure at
short-sea borders — the post-Brexit UK-EU customs burden is the paradigm
case, though the same structural burden applies at any short-sea border
with a customs boundary. `TransitDeclaration` and `ICS2Reference` are
tiered up relative to `shipping-carrier` because transit movements and
pre-arrival safety/security filings are routine here, not an edge case.

**Questions**
1. Do you file transit declarations (NCTS-style) for goods moving under
   transit procedure rather than full import/export clearance at each
   border?
2. Do you file ICS2-style pre-arrival safety & security declarations
   yourself, or does a customs broker / the ferry operator file on your
   behalf?
3. Do you hold HS classification, customs value, and preference-claim data
   for your shippers, or only pass through what the shipper provides?
4. How many customs declarations are filed per crossing — one per trailer,
   one per sailing, or something else?

**Maps to.**
`wco/customs#CustomsDeclaration`, `TransitDeclaration`, `ImportDeclaration`,
`ExportDeclaration`, `EntryExitSummary`, `ICS2Reference`, `Filing`,
`DeclarationStatus`, `CustomsProcedure`, `GoodsItem`, `TariffClassification`,
`CustomsValue`, `PreferenceClaim`.

**Outcome guidance.** Broker files everything on your behalf ⇒ most of
`wco/customs#*` is `partial` (you hold a reference number, not the
authoritative filing). If the SME reports zero customs exposure at all,
re-confirm the sector fit — a genuinely domestic-only unit-load operation
with no border crossing is arguably better modelled as a generic road
haulier, not this archetype.

---

## §17 Trade facilitation

**Questions**
1. Are you AEO-certified, and do you track AEO status of your subcontracted
   hauliers and customs brokers?
2. Do you originate eFTI records (EU electronic freight transport
   information) for road movements, given the EU eFTI regulation's
   applicability to road consignment notes?
3. Do you connect to any National Single Window directly, or only through
   an intermediary?

**Maps to.**
`wco/trade-facilitation#AEOCertification`, `SingleWindow`, `eFTIRecord`,
`CertificateOfOrigin`, `TradeAgreementReference`, `TrustedTrader`.

**Outcome guidance.** No eFTI participation yet (regulation phasing in) ⇒
`eFTIRecord` is `not-applicable` today but should be flagged as an upcoming
requirement in the discovery report, the same treatment `shipping-carrier`
gives CII/EU ETS in its own sustainability section.

---

## §18 Sustainability — road fleet & ferry-leg emissions

**Why it matters.** Modal-shift reporting (road-only vs. road+ferry) is a
genuine commercial argument for this sector in a way it is not for a pure
ocean carrier, and tonne-kilometre is the standard road-fleet carbon
intensity metric.

**Questions**
1. Do you report tonne-kilometre carbon intensity for your own-account
   tractor fleet, subcontracted haulage, or both?
2. Do you publish a modal-shift metric (comparing road-only vs. road+ferry
   emissions for the same lane) to customers as a sustainability argument
   for using your ro-ro service?
3. Are your own-account tractor units diesel, electric, or mixed — and if
   electric, do you track energy consumption per trip?
4. Do you separately account for emissions on the ferry leg (which you
   typically do not control) versus the road legs (which you may)?

**Maps to.**
`sustainability/carbon#CarbonEmission`, `TonneKilometre`,
`ModalShiftMetric`, `EmissionFactor`, `CarbonFootprint`,
`sustainability/energy#FuelType`, `EnergyConsumption`, `Electric`.

**Outcome guidance.** No modal-shift reporting yet ⇒ `ModalShiftMetric` is
`not-applicable` today but flag as upcoming commercial opportunity, not
just a regulatory risk (contrast with `shipping-carrier`'s CII/EU ETS
framing, which is purely regulatory-risk framed).

---

## §19 Financial settlement, revenue/yield & cost allocation

**Why it matters.** Trade-lane profitability reporting is a first-order
capability for this sector, and per `capability-coverage.yaml`
(id `trade-lane-and-market-segment`), **no class for trade lane / market
segment exists in the commercial ontology today**. This section also
carries the own-vs-subcontracted cost-allocation question flagged by
CR-RM-07 §9.2.

**Questions**
1. Do you report profitability by trade lane (e.g. Dover–Calais,
   Rosslare–Cherbourg) as a named, reusable dimension, or only by
   ad hoc date-range query?
2. When a load moves behind a subcontracted haulier, is the haulage cost
   allocated against the same cost record as an own-account move, with a
   resource-type flag distinguishing them — or are subcontracted costs
   tracked in an entirely separate ledger?
3. Are freight invoices, detention invoices, and any customs-pass-through
   charges issued from the same system as the operational TMS?
4. Do you reconcile against the BSP / ISO 20197 invoice model, or a
   bespoke billing schema?

**Maps to.**
`bsp/financial#FreightCharge`, `FreightRate`, `Invoice`, `PaymentTerms`,
`bsp/revenue-yield#FreightRevenue`, `ProfitabilityScope`, `ContractRate`,
`bsp/cost-accounting#TransportCostItem`, `CostAllocation`,
`AllocationBasis`.

**Declared gap — trade lane / market segment.** `ProfitabilityScope` is
the closest real class — it names *that* a profitability boundary exists —
but it does not carry a trade-lane or market-segment dimension. Record the
SME's actual lane-definition model (named lanes, geography-derived,
customer-segment-derived) in the free-text note, and flag it for the
blueprint layer rather than mapping it to an invented "TradeLane" class.

**Outcome guidance.** Subcontracted costs tracked in a wholly separate
ledger with no resource-type discriminator on a shared allocation record ⇒
`CostAllocation` is `deviates` — this is precisely the collision CR-RM-07
§9.2 anticipates ("one source allocation relation commonly mixes equipment,
driver, operator and subcontractor rows"). No lane-level profitability
reporting at all ⇒ `ProfitabilityScope` is `partial`, not `not-applicable`
— nearly every carrier tracks *some* profitability boundary, even if not
by lane.

---

## §20 Structural & lifecycle relationships

> **Important.** The ref-models declare *which* entities relate (via
> `rdfs:domain` + `rdfs:range`), but do **not** declare cardinality,
> aggregation, or temporal lifecycle. These questions resolve the
> table-design decisions the ontology leaves open — and this archetype adds
> several that do not arise for `shipping-carrier` or `freight-forwarder`.

### Booking ↔ Shipment ↔ Sailing

1. Can one Booking become multiple Shipments (e.g. a groupage booking
   split across two sailings for capacity reasons)?
2. Can multiple Bookings be combined onto one sailing as a single
   commercial unit, or does each booking always ride independently?
3. Is a Shipment associated with exactly one ferry crossing, or can it span
   multiple crossings (e.g. a multi-leg intermodal route)?

**Affects.** `dcsa/booking#Booking`, `Shipment`, `TransportPlanLeg`,
`imo/port-call#SeaLeg`.

### Booking ↔ Equipment ↔ Trailer

4. When is a trailer/swap-body identifier assigned: at booking, at gate-in,
   at loading, or only on the manifest?
5. Are `RequestedEquipment` (a type/quantity) and
   `UtilizedTransportEquipment` (the specific trailer instance) one entity
   or two in your system?

**Affects.** `dcsa/booking#RequestedEquipment`,
`UtilizedTransportEquipment`, `mmt/equipment#TrailerUnit`.

### Own-account vs. subcontracted — the cross-cutting cardinality question

6. Is own-vs-subcontracted a property of the Booking, the Leg, the Haulier
   party, the Tractor unit, or (commonly) more than one of these — and if
   more than one, which one is authoritative when they disagree?
7. Can a single physical trip change from own-account to subcontracted
   mid-journey (e.g. a relay handover to a subcontracted haulier for the
   final delivery leg)?

**Affects.** `mmt/party#Carrier`, `mmt/inland-transport#InlandCarrier`,
`RoadLeg`, `bsp/cost-accounting#CostAllocation`.

### Accompanied vs. unaccompanied — handover cardinality

8. On an accompanied crossing, is the driver modelled as riding with a
   specific trailer for the whole crossing, or could the driver and
   trailer be logically decoupled and rejoined at the destination terminal
   (effectively converting to unaccompanied mid-journey)?
9. Does a `HandoverEvent` always pair exactly one outgoing party with one
   incoming party, or can a handover be to/from a pool (e.g. "any available
   destination-terminal driver")?

**Affects.** `mmt/inland-transport#HandoverEvent`, `InlandCarrier`.

### TransportCall ↔ PortCall ↔ Sailing

10. Is `TruckTransportCall` the same event as the trailer's gate-in, or a
    distinct record that the gate-in event references?
11. Does a `VesselTransportCall` correspond to one physical sailing, or can
    one call cover multiple consecutive sailings (e.g. a round trip)?

**Affects.** `dcsa/transport-call#TruckTransportCall`,
`VesselTransportCall`, `imo/port-call#PortCall`, `SeaLeg`.

### Detention billing grain

12. Is detention billed per trailer, per booking, or per customer account
    aggregated across trailers?
13. Does the free-time clock pause on customs holds — a real risk given
    this sector's border exposure — and if so, is that pause a structured
    record or an ad hoc manual adjustment?

**Affects.** `dcsa/demurrage-detention#DetentionCharge`,
`FreeTimeAllowance`, `wco/customs#CustomsDeclaration`.

### Customs declaration grain

14. One customs declaration per trailer, per sailing, or per shipper's
    goods collection within a trailer?

**Affects.** `wco/customs#CustomsDeclaration`, `TransitDeclaration`,
`Filing`.

### Empty repositioning ↔ revenue trip

15. Is a repositioning move ever combined with a partial revenue load
    (e.g. reposition to a depot that happens to also deliver cargo en
    route), and if so, how is that trip typed?

**Affects.** `mmt/events#TransferEvent`, `mmt/inland-transport#RoadLeg`
— and directly informs the `empty-equipment-repositioning` gap (§11).

---

## §21 Naming & identifier conventions (cross-cutting)

These don't map to specific URIs but determine whether outcomes are
`conforms` or `conforms-with-rename` across the whole model.

1. Do your internal terms match the ref-model naming (e.g., "CMR" vs.
   "consignment note" vs. "waybill"; "sailing" vs. "crossing" vs.
   "voyage")?
2. What is your booking-id format, CMR-number format, and trailer/swap-body
   numbering standard — proprietary fleet numbers, ISO 6346-style (for any
   containerised minority of the fleet), or a national trailer-plate
   scheme?
3. Do you use UN/LOCODE for ports/terminals/border crossings, or
   proprietary location codes?
4. Do you use IMO Number + MMSI for the ferry, or rely entirely on the
   ferry operator's identifiers since you rarely own the tonnage?
5. Do you use HS codes for commodities, or proprietary commodity
   classifications?
6. What term does your organisation use internally for "own-account"
   versus "subcontracted" — this drives whether the attribute-level split
   in §5/§9 lands as `conforms-with-rename` or needs a genuinely new
   enumerated value.

---

## Appendix — relationship topology (auto-derive note)

The `kairos-design-discovery` skill should auto-derive and render the
directional typed-edge graph for the `unit-load-carrier` archetype from the
catalog, so the SME confirms / corrects rather than answers from scratch.
Example edges already in the referenced modules:

- `Shipment` `hasBooking` → `Booking`
- `Booking` `hasRequestedEquipment` → `RequestedEquipment`
- `Shipment` `hasUtilizedEquipment` → `UtilizedTransportEquipment`
- `UtilizedTransportEquipment` `hasTransportEquipment` → `TransportEquipment`
- `RoadLeg` `hasInlandCarrier` → `InlandCarrier`
- `Shipment` `hasTransportDocument` → `TransportDocument`
- `Consignment` `hasConsignmentItem` → `ConsignmentItem`

(Full list derived at runtime from the resolved catalog graph; the above is
illustrative only. Note that several edges this archetype needs most —
equipment ↔ repositioning-move, and consignment/movement ↔ trade-lane — do
not exist yet, because the classes on one end of each edge are the declared
gaps in §11 and §19.)
