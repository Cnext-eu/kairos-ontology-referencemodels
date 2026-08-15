# Shipping-Carrier — SME Discovery Guide

**Archetype:** `shipping-carrier` (see
[`blueprints/archetypes/shipping-carrier.yaml`](../../../blueprints/archetypes/shipping-carrier.yaml))
**Pack:** `accelerator-packs/logistics`
**Target sector:** Ocean carrier (vessel operators), short-sea / feeder,
ro-ro, breakbulk, inland-waterway / barge.

## §0 How to use this guide

This guide is the prose companion to the `shipping-carrier` archetype
catalog. It is consumed by the `kairos-design-discovery` skill in the
`kairos-ontology-toolkit` repo, but can also be used as a stand-alone
interview script by a data architect or business analyst.

### Interview flow

1. Walk the SME through §1–§21 (business areas). For each section:
   - Read **Why it matters**.
   - Ask the **Questions**.
   - For every URI in **Maps to**, record an outcome code (see below)
     plus a free-text note.
2. Walk through §22 (Structural & lifecycle relationships). These are
   the cardinality and lifecycle decisions the ontology cannot infer.
3. Walk through §23 (Naming & identifier conventions). These determine
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

The DCSA / MMT / IMO ref-models declare directional typed edges between
classes (`rdfs:domain` + `rdfs:range` on every `owl:ObjectProperty`).
The skill should **derive** the relationship topology from the resolved
catalog graph and present it as a confirmation checklist — not as open
questions. This guide therefore focuses on **business semantics** and
**cardinality/lifecycle decisions** the ontology cannot pin down.

### Scope profile (ask before §1)

The axes, their allowed values and the **resolution rules** (promote never
demote; out-of-scope ⇒ pre-seeded `not-applicable` with
`needs_confirmation: true`) are defined once in
[`README.md`](./README.md#scope-axes). Only the carrier-specific
consequences are below. §1 asks these same questions in business terms —
if the answers differ, the Scope profile is wrong and must be corrected
first, because the module set depends on it.

#### `modes-served` (multi-valued)

Ocean-side values only for this archetype; a carrier selling road or rail
feeder legs on its own bill is answering for a leg it subcontracts, which
belongs on the `service-model` axis, not here. Mode targets are cited from
[`pattern.yaml` `mode_bindings`](../../../blueprints/patterns/multimodal-order-leg/pattern.yaml).

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| `ocean` (deep-sea, short-sea, feeder) | archetype defaults apply unchanged | — |
| `barge` / inland waterway | `https://www.kairosflow.ai/ont/mmt/transport-means` (`BargeVessel`) → **required** | — |
| `ocean` only, no barge | — | `mmt/transport-means#BargeVessel` |
| carrier haulage sold on road or rail legs | `https://www.kairosflow.ai/ont/mmt/inland-transport` → **recommended** (`RoadLeg`, `RailLeg`) | — |

#### `geographic-scope`

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| `door-to-door` (carrier haulage) or `both` | `https://www.kairosflow.ai/ont/mmt/inland-transport` → **recommended**; `dcsa/locations#PlaceOfReceipt`, `PlaceOfDelivery`, `PreCarriageFromLocation`, `OnwardInlandRoutingLocation` → **required** | — |
| `port-to-port` only | — | `dcsa/locations#PreCarriageFromLocation`, `OnwardInlandRoutingLocation`, `mmt/consignment#MasterConsignment`, `HouseConsignment` (confirm against §2 Q3 first) |

This is the rule §1's **Outcome guidance** states in prose; both cite this
axis so the two cannot drift.

#### `service-model` (multi-valued)

| Answer | Modules promoted / added | Pre-seed `not-applicable` |
|---|---|---|
| `2pl` (asset carrier — the default) | archetype defaults apply unchanged | — |
| also `3pl` / `4pl` (carrier also selling arranged multi-carrier services) | **none — stop and escalate**, see below | — |

A pure `2pl` keeps grain 1 absent, deliberately: its incoming demand **is**
the booking, and adding a `TransportOrder` above `dcsa:Booking` duplicates
it with a synonym ([`pattern.md`](../../../blueprints/patterns/multimodal-order-leg/pattern.md),
"When NOT to use"). `blueprint/transport-order` is therefore **not declared
in this archetype at all**, and no axis may add it — an axis can only
promote a module the archetype already declares
([resolution rule 1](./README.md#resolution-rules)).

So a carrier that genuinely also sells arranged multi-carrier transport is
not one archetype being tuned; it is two operating models in one company —
the `freight-forwarder` archetype for that part of the business. Composition
is unsupported in v0 (one archetype id per session). Record the finding, run
the forwarding side as a separate session, and flag it for the composition
backlog. Do **not** stretch this archetype to cover it.

---

## §1 Service scope & shipment type

**Why it matters.** Drives whether the model needs door-to-door legs,
pre- and on-carriage locations, multi-modal consignments, and the
master/house document split.

**Questions**
1. Do you offer port-to-port only, or also door-to-door (carrier
   haulage) and merchant haulage?
2. Is your scope deep-sea, short-sea / feeder, ro-ro, breakbulk, or
   inland-waterway / barge?
3. Do you contract directly with shippers, or primarily with
   freight forwarders / NVOCCs?
4. Spot bookings, contract / service-agreement bookings, or both?

**Maps to.**
`dcsa/booking#*`, `dcsa/locations#PlaceOfReceipt`, `PlaceOfDelivery`,
`PreCarriageFromLocation`, `OnwardInlandRoutingLocation`,
`mmt/consignment#MasterConsignment`, `HouseConsignment`,
`mmt/transport-means#BargeVessel`.

**Outcome guidance.** Port-to-port only ⇒ onward / pre-carriage locations
become `not-applicable`. Pure deep-sea ⇒ `BargeVessel` is
`not-applicable`.

---

## §2 Transport documents & surrender model

**Why it matters.** Defines the primary contractual artefact and the
issuance / surrender lifecycle the data model must support.

**Questions**
1. Do you issue Bills of Lading, Sea Waybills, or both?
2. Are you live on any eBL platform (essDOCS, Bolero, WaveBL, IQAX)? If
   yes — for what % of shipments?
3. Do you ever issue under a forwarder's house B/L, or always under
   your master B/L?
4. What surrender models do you support (original paper, telex release,
   electronic surrender, straight)?
5. Do you issue Cargo Manifests and DG Declarations for every voyage,
   or only when authority-mandated?

**Maps to.**
`dcsa/transport-documents#BillOfLading`, `ElectronicBillOfLading`,
`SeaWaybill`, `mmt/documents#MasterWaybill`, `HouseWaybill`,
`CargoManifest`, `DangerousGoodsDeclaration`,
`dcsa/events#DocumentSurrenderedEvent`.

**Outcome guidance.** No eBL ⇒ `ElectronicBillOfLading` is
`not-applicable`. No house-bill awareness ⇒ `HouseWaybill`,
`HouseConsignment` are `not-applicable`.

---

## §3 Parties & role model

**Why it matters.** Determines which parties need first-class entity
modelling versus being attributes on a document.

**Questions**
1. Do you model Notify Party as a structured party, or just a free-text
   field on the B/L?
2. Do you distinguish Booking Party from Shipper (e.g., when a forwarder
   books on behalf of a shipper)?
3. Do you maintain a freight-forwarder master (KYC, AEO status), or are
   they ad-hoc on each booking?

**Maps to.**
`dcsa/party#NotifyParty`, `BookingParty`, `FreightForwarder`.

---

## §4 Geographic network & transshipment

**Why it matters.** Determines whether transshipment legs, CFS, and
inland ramps need to be modelled.

**Questions**
1. Do you operate direct services only, or do shipments transship
   between your services / partner services?
2. Do you use CFS / depots for LCL or empty-management, or only carrier
   container yards at terminals?
3. Do you have rail-ramp / inland-terminal handoffs (intermodal)?

**Maps to.**
`dcsa/locations#TransshipmentPort`, `ContainerFreightStation`, `Depot`,
`InlandTerminal`, `RailRamp`, `BorderCrossing`.

---

## §5 Vessel operation model

**Why it matters.** Drives ownership / charter-party data, fleet master,
voyage-vs-call modelling.

**Questions**
1. Are your vessels owned, time-chartered, slot-chartered, or a mix?
2. Do you operate fixed liner services (service loops) or tramp /
   contract-of-affreightment?
3. Do you maintain your own fleet master with IMO registry data, or
   rely on a third-party feed (Lloyd's List, IHS Markit, partner-line
   data)?

**Maps to.**
`dcsa/schedule#ServiceLoop`, `mmt/transport-means#Vessel`,
`imo/vessel-registry#Vessel`, `Fleet`, `IMONumber`, `MMSI`, `FlagState`,
`ClassSociety`, `VesselType`, `GrossTonnage`, `DeadweightTonnage`.

**Outcome guidance.** No service loops ⇒ `ServiceLoop` is `partial` or
`deviates`. Pure slot-charter without own fleet ⇒ most IMO
vessel-registry entries are `not-applicable`.

---

## §6 Schedule, voyage & port-call execution

**Why it matters.** Determines event granularity (voyage / leg / call /
berth) and which authority forms must be filed.

**Questions**
1. Do you publish sailing schedules and cut-off times to customers, or
   only internally?
2. Do you file FAL forms / pre-arrival / port-health declarations, or
   does your agent file them on your behalf?
3. Do you track pilotage, towage, bunkering, crew change, and waste
   disposal per call?

**Maps to.**
`dcsa/schedule#SailingSchedule`, `CutOffTime`, `TransitTime`,
`imo/port-call#Voyage`, `PortCall`, `BerthStay`, `FALForm`,
`ArrivalNotice`, `DepartureNotice`, `PilotageRequest`, `TowageRequest`,
`BunkeringOperation`, `WasteDisposal`, `CrewChange`,
`PreArrivalNotification`, `PortHealthDeclaration`.

---

## §7 Equipment & container fleet

**Why it matters.** Drives equipment-master scope and SOC vs. COC
handling.

**Questions**
1. What container types are in your fleet: dry, reefer, tank, flat-rack,
   open-top, platform?
2. Do you accept Shipper-Owned Containers (SOC), or COC only?
3. Do you track empty-container repositioning at the unit level, or
   aggregate volumes?

**Maps to.**
`dcsa/equipment#DryContainer`, `ReeferContainer`, `TankContainer`,
`FlatRackContainer`, `OpenTopContainer`, `PlatformContainer`,
`dcsa/container-operations#ContainerJourney`,
`ContainerOperationalStatus`.

**Outcome guidance.** No reefer fleet ⇒ `ReeferContainer` is
`not-applicable` (and TIC reefer monitoring follow-on is moot). Only
dry + reefer ⇒ tank / flat-rack / open-top / platform `not-applicable`.

---

## §8 Container operations (stuffing / stripping, LOLO)

**Questions**
1. Do you offer carrier-stuffing (CFS) services, or only door-pickup of
   shipper-stuffed containers?
2. Do you record stuffing / stripping events at unit level for liability
   or weight-verification (VGM) reasons?

**Maps to.**
`dcsa/container-operations#ContainerStuffing`, `ContainerStripping`,
`LiftOnLiftOff`.

---

## §9 Cargo characteristics

**Questions**
1. Do you model cargo as commodities (HS-class level) or as goods items
   per package?
2. Do you carry temperature-controlled cargo (set-point, ambient range,
   ventilation, humidity)?
3. Do you handle shipper-provided handling / quarantine / disposal
   instructions?
4. Do you record shipping marks (per-container or per-package)?
5. Do you carry cargo insurance on behalf of customers, or never?

**Maps to.**
`mmt/cargo#Goods`, `PackageSpecification`, `Weight`, `Dimension`,
`CargoMeasurement`, `HandlingInstructions`, `ShippingMarks`,
`CargoInsurance`, `dcsa/booking#Commodity`.

---

## §10 Track-and-trace event publication

**Why it matters.** Defines the operational backbone of customer-facing
visibility products and DCSA T&T alignment.

**Questions**
1. Which milestones do you publish externally (booking, gate-in, loaded,
   sailed, transshipped, discharged, gate-out, empty-return)?
2. Do you publish document events (B/L issued, surrendered)?
3. Do you record customs / inspection / seal events, or are those only
   internal operational data?

**Maps to.**
`dcsa/events#TransportEvent`, `EquipmentEvent`, `DocumentEvent`,
`VesselDepartureEvent`, `VesselArrivalEvent`, `LoadedOnVesselEvent`,
`DischargedFromVesselEvent`, `GateInEvent`, `GateOutEvent`,
`EmptyContainerPickupEvent`, `EmptyContainerReturnEvent`,
`DocumentIssuedEvent`, `DocumentSurrenderedEvent`,
`BorderCrossingEvent`, `CustomsEvent`, `InspectionEvent`, `SealEvent`.

---

## §11 Demurrage & detention

**Why it matters.** Often a top-three revenue line and the most disputed.

**Questions**
1. Do you bill demurrage and detention separately, or as combined D&D?
2. What free-time structure (days by origin / destination / equipment /
   customer tier)?
3. Per-diem flat or tiered (e.g., days 1–5 × rate1, days 6–10 × rate2)?
4. Storage charges (terminal-pass-through, or own tariff)?
5. Dispute / waiver workflow — formal record or ad-hoc credit notes?

**Maps to.**
`dcsa/demurrage-detention#DemurrageCharge`, `DetentionCharge`,
`CombinedDemurrageDetention`, `StorageCharge`, `FreeTimeAllowance`,
`PerDiemRate`, `RateTier`, `DemurrageDetentionTariff`, `DisputeRecord`,
`Waiver`.

**Outcome guidance.** Combined D&D billing ⇒ `DemurrageCharge` and
`DetentionCharge` are `partial` (the standard distinction is not
preserved). Flat per-diem ⇒ `RateTier` is `not-applicable`.

---

## §12 Dangerous goods (IMDG)

**Questions**
1. Do you carry dangerous goods? If yes — which IMDG classes do you
   accept / refuse?
2. Do you maintain segregation / stowage-category logic in your booking
   acceptance flow, or only operationally at the terminal?
3. Do you store EmS, flash-point, emergency-contact per booking, or
   only for high-risk classes?

**Maps to.**
`imo/dangerous-goods#DangerousGoodsItem`, `HazardClass`, `UNNumber`,
`PackingGroup`, `FlashPoint`, `EmergencySchedule`, `SegregationRule`,
`StowageCategory`, `EmergencyContact`, `DGDeclaration`,
`mmt/documents#DangerousGoodsDeclaration`.

**Outcome guidance.** Carrier refuses all DG ⇒ entire module is
`not-applicable`.

---

## §13 Vessel certificates & ISM / ISPS / MLC compliance

**Why it matters.** Owned-fleet operators must hold these; slot-charter-
only operators rarely model them.

**Questions**
1. Do you maintain statutory-certificate validity tracking (DoC, SMC,
   ISSC, MLC, IEEC) in your systems?
2. Are surveys scheduled / tracked centrally, or by ship managers?

**Maps to.**
`imo/certificates-surveys#StatutoryCertificate`, `DocumentOfCompliance`,
`SafetyManagementCertificate`, `InternationalShipSecurityCertificate`,
`MaritimeLabourCertificate`, `InternationalEnergyEfficiencyCertificate`,
`StatutorySurvey`.

---

## §14 Maritime security (ISPS) & environmental plans

**Questions**
1. Do you maintain Ship Security Plans / Declaration of Security records
   in your systems, or only on the vessel?
2. Do you track BWMP / GMP / SOPEP / SEEMP plan versions and audits
   centrally?

**Maps to.**
`imo/maritime-security#ShipSecurityPlan`, `DeclarationOfSecurity`,
`imo/environmental#BallastWaterManagementPlan`, `GarbageManagementPlan`,
`ShipboardOilPollutionEmergencyPlan`,
`ShipEnergyEfficiencyManagementPlan`.

---

## §15 Customs filing responsibility

**Why it matters.** Defines whether the carrier system holds customs
references (ENS, AMS, ACI) or only flows them through.

**Questions**
1. Do you file ENS / AMS / ACI directly with authorities, or does your
   agent / forwarder?
2. Do you process transit declarations (e.g., NCTS in EU)?
3. Do you maintain HS classification, customs value, and preference
   claims for your shippers?

**Maps to.**
`wco/customs#CustomsDeclaration`, `EntryExitSummary`, `ImportDeclaration`,
`ExportDeclaration`, `TransitDeclaration`, `Filing`, `DeclarationStatus`,
`TariffClassification`, `CustomsValue`, `PreferenceClaim`.

---

## §16 Trade facilitation (AEO, Single Window)

**Questions**
1. Are you AEO-certified (and do you track AEO status of trading
   partners)?
2. Do you connect to any National Single Window (NSW) directly?
3. Do you originate or accept Certificates of Origin under your own
   name?

**Maps to.**
`wco/trade-facilitation#AEOCertification`, `SingleWindow`,
`CertificateOfOrigin`, `TradeAgreementReference`.

---

## §17 Sustainability — CII / EEXI / EU ETS / carbon reporting

**Why it matters.** Regulatory deadlines (IMO CII, EU ETS phase-in) make
this rapidly moving from optional to required for many EU-touching
trades.

**Questions**
1. Do you report CII rating per vessel-year (MRV / IMO DCS)?
2. Are you in scope for EU ETS, and do you currently track allowance
   surrender per voyage?
3. Do you publish customer-level carbon footprints (per shipment or per
   container) — Well-to-Wake or Tank-to-Wake?
4. Are emission factors loaded from a third-party source (GLEC, Smart
   Freight Centre) or computed in-house?

**Maps to.**
`sustainability/carbon#CarbonEmission`, `WellToWake`, `TankToWake`,
`EmissionFactor`, `CarbonFootprint`, `EmissionReport`, `CIIRating`,
`EEXICompliance`, `EUETSAllowance`, `CarbonOffset`.

**Outcome guidance.** Not yet in scope (e.g., non-EU short-sea) ⇒ most
are `not-applicable` but should be flagged as upcoming risk in the
discovery report.

---

## §18 Booking lifecycle & state model

**Questions**
1. What states does a Booking go through (requested → pending →
   confirmed → amended → cancelled)?
2. Do you keep amendment history versioned, or overwrite the booking
   in place?
3. Who can initiate / confirm / cancel — only the booking party, only
   the carrier, or both with different rules?

**Maps to.**
`dcsa/booking#BookingRequest`, `ConfirmedBooking`, `ShippingInstruction`.

---

## §19 Reefer-specific operations

**Questions** *(skip if no reefer fleet — see §7)*
1. Do you record set-point and actual temperature events per voyage?
2. Do you handle CA (controlled-atmosphere) or modified-atmosphere
   bookings?
3. Do you offer pre-trip-inspection (PTI) as a customer service?

**Maps to.** `dcsa/equipment#ReeferContainer`,
`dcsa/container-operations#ContainerOperationalStatus`.
Reefer-monitoring detail lives in the `TIC` ontology — flag as a
follow-on archetype if relevant.

---

## §20 Empty-container management

**Questions**
1. Do you optimise empty repositioning centrally, or per region?
2. Do you track empty-container availability per depot in your systems,
   or only on the terminal side?

**Maps to.** `dcsa/events#EmptyContainerPickupEvent`,
`EmptyContainerReturnEvent`, `dcsa/locations#Depot`,
`dcsa/container-operations#ContainerOperationalStatus`.

---

## §21 Financial settlement & invoicing (boundary)

**Why it matters.** Carrier-side invoicing typically lives outside the
DCSA scope. Flag whether the customer expects it to be in the same data
hub.

**Questions**
1. Are freight invoices, D&D invoices, and storage invoices issued from
   the same system as the operational TMS?
2. Do you reconcile against the BSP / ISO 20197 invoice model, or use a
   bespoke billing schema?

**Maps to.** None in the `shipping-carrier` core archetype. Flag the
`BSP` ontology + `accelerator-packs/financial-services` as a follow-on
if the customer wants billing in scope.

---

## §22 Structural & lifecycle relationships

> **Important.** The ref-models declare *which* entities relate (via
> `rdfs:domain` + `rdfs:range`), but do **not** declare cardinality,
> aggregation, or temporal lifecycle. These ~16 questions resolve the
> table-design decisions the ontology leaves open.

### Booking ↔ Shipment ↔ Voyage

1. Can one Booking become multiple Shipments (carrier-side split for
   capacity reasons)?
2. Can multiple Bookings be combined into one Shipment (consolidation)?
3. Is a Shipment associated with exactly one vessel-voyage, or can it
   span multiple (transshipment legs as separate shipment records)?
4. Is "Voyage" your unit of vessel-rotation (whole loop) or one leg
   (PoL → PoD)?

**Affects.** `dcsa/booking#Booking`, `Shipment`, `TransportPlanLeg`,
`imo/port-call#Voyage`, `SeaLeg`.

### Booking ↔ ShippingInstruction ↔ Bill of Lading

5. One Booking → one Shipping Instruction → one B/L, or can the SI
   aggregate / split?
6. Can one B/L cover multiple Shipments (consolidated B/L)?
7. When is the B/L issued versus the Shipment created — same record,
   or B/L issued downstream?

**Affects.** `dcsa/booking#ShippingInstruction`,
`dcsa/transport-documents#BillOfLading`, `SeaWaybill`,
`mmt/consignment#MasterConsignment`, `HouseConsignment`.

### Booking ↔ Equipment ↔ Container

8. When is a Container number assigned: at booking, at gate-in, at
   loading, or only on the manifest?
9. Are `RequestedEquipment` (a quantity / type) and
   `UtilizedTransportEquipment` (a specific container instance) modelled
   as one entity or two in your system?

**Affects.** `dcsa/booking#RequestedEquipment`,
`UtilizedTransportEquipment`, `dcsa/equipment#Container`.

### Container ↔ T&T events

10. Are events recorded against a Container (unit) or against a Shipment?
11. Are multiple Containers under one Shipment tracked individually for
    gate-in / load / discharge, or aggregated?

**Affects.** `dcsa/events#EquipmentEvent`, `TransportEvent`,
`dcsa/container-operations#ContainerJourney`.

### TransportCall ↔ PortCall ↔ Voyage

12. Is `TransportCall` the same as `PortCall`, or do you distinguish
    *operational* (TransportCall = your touchpoint with the vessel) from
    *regulatory* (PortCall = the vessel's call recorded by the port
    authority)?
13. Does a Voyage have a fixed start / end PortCall, or is it open-ended
    until the vessel re-positions?

**Affects.** `dcsa/transport-call#TransportCall`, `VesselTransportCall`,
`imo/port-call#PortCall`, `Voyage`, `BerthStay`.

### Demurrage & detention billing grain

14. Is D&D billed per Container, per Shipment, or per B/L?
15. Free-time clock — Container-level or Shipment-level? (And does the
    clock pause on customs holds / disputes?)

**Affects.** `dcsa/demurrage-detention#DemurrageCharge`,
`DetentionCharge`, `FreeTimeAllowance`.

### Customs declaration grain

16. One customs declaration per Shipment, per B/L, or per Master B/L?

**Affects.** `wco/customs#CustomsDeclaration`, `Filing`.

---

## §23 Naming & identifier conventions (cross-cutting)

These don't map to specific URIs but determine whether outcomes are
`conforms` or `conforms-with-rename` across the whole model.

1. Do your internal terms match DCSA naming (e.g., "transport-document"
   vs "BL", "vessel-voyage" vs "voyage-number")?
2. What is your booking-id format, B/L-number format, and container-
   number standard (ISO 6346)?
3. Do you use UN/LOCODE for ports / places, or proprietary location
   codes?
4. Do you use IMO Number + MMSI for vessels, or a proprietary fleet id?
5. Do you use HS codes for commodities, or proprietary commodity
   classifications?

---

## Appendix — relationship topology (auto-derive note)

The `kairos-design-discovery` skill should auto-derive and render the
directional typed-edge graph for the `shipping-carrier` archetype from
the catalog, so the SME confirms / corrects rather than answers from
scratch. Example edges already in DCSA:

- `Shipment` `hasBooking` → `Booking`
- `Booking` `hasShippingInstruction` → `ShippingInstruction`
- `Booking` `hasCargoItem` → `CargoItem`
- `Booking` `hasRequestedEquipment` → `RequestedEquipment`
- `Shipment` `hasUtilizedEquipment` → `UtilizedTransportEquipment`
- `UtilizedTransportEquipment` `hasContainer` → `Container`
- `Shipment` `hasTransportDocument` → `TransportDocument`
- `Shipment` `hasCarrier` → `Carrier`

(Full list derived at runtime from the resolved catalog graph; the
above is illustrative only.)
