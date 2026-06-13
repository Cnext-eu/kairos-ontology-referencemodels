# TIC 4.0 Gap Analysis Report

**Status:** DRAFT  
**Date:** 2026-06-12  
**Ontology:** TIC 4.0 Terminal Industry — v1.1.0  
**Standard:** TIC4.0 Release 2025.017 / BSI PAS 4000:2026  
**Scope:** Systematic comparison of TIC 4.0 published subjects vs. current ontology coverage

---

## Executive Summary

The current TIC ontology (6 modules, ~44 classes) covers the **core operational layer** of
TIC 4.0 well — carrier visits, cargo visits, moves, cycles, job instructions, terminal
infrastructure, equipment, locations, events, and automotive services. However, the TIC 4.0
standard has grown significantly through releases 2024.010–2026.018, introducing at least
**12 additional subject domains** that are NOT represented in the ontology.

The most significant gaps are:

| Priority | Gap | Impact |
|----------|-----|--------|
| 🔴 CRITICAL | Container/Cargo Unit identity (no Container class) | Core entity missing from handling ops |
| 🔴 CRITICAL | Reefer Monitoring (temperature, atmosphere, alarms) | Key terminal domain, released 2024.012+ |
| 🟠 HIGH | KPI Definitions (berth/crane productivity, dwell time) | Analytics foundation, released 2024.013+ |
| 🟠 HIGH | CHE Equipment sub-subjects (Spreader, Hoist, PowerSource, Health) | IoT/Digital Twin foundation |
| 🟠 HIGH | Vessel/Carrier Identity (IMO, MMSI, draft, voyage) | Missing entity behind CarrierVisit |
| 🟠 HIGH | Process hierarchy (Order, JobInstructionList, CarrierTrip) | Deeper operational model |
| 🟡 MEDIUM | Rail intermodal (RailVisit, RailWagon, RailInventoryPosition) | Released 2025.017 |
| 🟡 MEDIUM | Electric CHE / eCHE (Battery, ChargingStation, sessions) | Sustainability initiative |
| 🟡 MEDIUM | EDI Message Mapping (BAPLIE, COARRI, CODECO, COPARN) | Message standard alignment |
| 🟢 LOW | Place ontology & Quay (2026.018) | Recent addition, spatial model |
| 🟢 LOW | Automation framework (IEC 62264 levels) | Reference architecture |
| 🟢 LOW | Digital Twin classification framework | Meta-model |

**Cross-domain isolation:** The TIC ontology currently has **zero cross-references** to
DCSA, MMT, IMO, or WCO ontologies. Several concepts overlap (Container, Vessel, DG,
locations) and should be aligned.

---

## Current Coverage Summary

### What We Have (6 modules, ~44 classes)

| Module | Classes | Cross-refs |
|--------|---------|------------|
| **Terminal Infrastructure** | Terminal, Berth, YardArea, Gate, StorageZone, RailHead, BargeConnection, TerminalEquipment, QuayCrane, YardCrane, ReachStacker, TerminalTractor | → locations |
| **Handling Operations** | CarrierVisit, CargoVisit, Move, LoadMove, DischargeMove, LiftMove, HorizontalMove, Cycle, JobInstruction | → infra, locations |
| **Automotive Services** | VehicleUnit, VIN, VehicleStorage, PDI, Wash, BodyRepair, VehicleReleaseStatus, DamageReport, VehicleService | → party |
| **Party** | TerminalParty, TerminalOperator, Stevedore | → locations |
| **Locations** | TerminalLocation, Terminal, Berth, YardPosition, GateLane, QuaySide, ReeferPlug, RailSiding, BargeQuay | _(self-contained)_ |
| **Events** | TerminalEvent, GateInEvent, GateOutEvent, YardMoveEvent, VesselLoadEvent, VesselDischargeEvent, StackEvent, ServiceCompleteEvent, DamageDetectedEvent, InspectionEvent | → all other modules |

### What's Good
- Core operational model (Visit → Move → Cycle → JobInstruction) is complete
- Yard positioning (block-bay-row-tier) is well-modeled
- Equipment hierarchy with lift capacity, outreach, stacking capacity
- Event model with cross-domain references to locations, equipment, parties
- Automotive services are comprehensive (PDI, wash, body repair, VIN, damage)

---

## Gap Matrix

### Gap 1: Container / Cargo Unit Identity — 🔴 CRITICAL

**TIC 4.0 source:** CHE Data Model 2022.005, PAS 4000 examples  
**Current state:** The ontology has `CargoVisit` (the lifecycle) but NO Container entity.
Events reference `unitReference` as a string property — no typed cargo unit class.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **Container** | Physical ISO shipping container | containerNumber (BIC), isoTypeCode (20GP/40GP/40HC/OT/FR/RF), tareWeight, vgm, maxGrossWeight, conditionCode |
| **Seal** | Tamper-evident closure on a container | sealNumber, sealType (SHIPPER/CUSTOMS/TERMINAL), sealStatus (INTACT/BROKEN/MISSING) |
| **ContainerCondition** | Condition survey result | conditionCode, surveyDate, surveyLocation, conditionNotes |
| **CargoUnit** | Abstract parent for Container and VehicleUnit | unitId, unitType, weight, dimensions |

**Challenge:** DCSA already has a full Container hierarchy (Container, DryContainer,
ReeferContainer, etc.). Should TIC define its own Container class or reference DCSA's?

**Recommendation:** Create a lightweight TIC `CargoUnit` class (the terminal's view of
a cargo unit — identity, weight, condition) that maps to DCSA Container and
VehicleUnit (already exists in automotive-services). Don't duplicate DCSA's container
type hierarchy.

---

### Gap 2: Reefer Monitoring — 🔴 CRITICAL

**TIC 4.0 source:** Releases 2024.012, 2024.013, 2025.014  
**Current state:** Only `ReeferPlug` exists as a location type (electrical connection point).
No monitoring, no reefer container concept, no alarms.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **ReeferMonitoring** | Active monitoring of a refrigerated container | setTemperature, actualTemperature, supplyTemperature, returnTemperature, powerState |
| **ReeferRack** | Frame holding multiple reefer containers | rackId, capacity, powerSupplyCapacity, location |
| **ReeferSlot** | Individual position in a reefer rack | slotNumber, plugCapacityKW, occupiedBy, powerStatus |
| **VentilationSystem** | Reefer ventilation control | ventilationRate, ventilationMode (FRESH/CLOSED), actualCO2, setO2 |
| **HumiditySystem** | Reefer humidity control | setHumidity, actualHumidity |
| **ReeferAlarmEvent** | Monitoring alarm event | alarmCode, alarmDescription, severity |
| **ReeferPlugInEvent** | Reefer connected to power | plugTimestamp, plugNumber, containerRef |
| **ReeferPlugOutEvent** | Reefer disconnected from power | unplugTimestamp, plugNumber, containerRef |

**Recommendation:** New `reefer-monitoring` sub-module under terminal-infrastructure or
as a standalone module. ReeferRack/ReeferSlot extend the locations module.

---

### Gap 3: KPI Definitions — 🟠 HIGH

**TIC 4.0 source:** Releases 2024.013, 2025.016, 2025.017, 2026.018  
**Current state:** No KPI or performance metric concepts at all.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **KPI** | Base class for terminal performance metrics | kpiCode, kpiName, value, unit, measurementPeriod, scope |
| **BerthProductivity** | Gross crane moves per ship working hour | value (moves/hour), vesselCallRef, measurementWindow |
| **CraneProductivity** | Net moves per crane working hour | value (moves/hr/crane), craneId, vesselCallRef |
| **DwellTime** | Time a container spends in the yard | value (hours), containerRef, gateInTime, gateOutTime |
| **TruckTurnaroundTime** | Gate-in to gate-out duration for trucks | value (minutes), truckRef |
| **YardOccupancy** | Percentage of yard capacity used | value (%), yardAreaRef, measurementTimestamp |
| **ShipWorkingTime** | Total time cranes work on a vessel | value (hours), vesselCallRef |

**Recommendation:** New `kpi` module. KPIs reference existing classes (CarrierVisit,
YardArea, QuayCrane) via object properties.

---

### Gap 4: CHE Equipment Sub-Subjects — 🟠 HIGH

**TIC 4.0 source:** CHE Data Model 2022.005, "CHE talks TIC" guideline  
**Current state:** Equipment types exist (QuayCrane, YardCrane, etc.) but NO component-level
or sensor-level modeling. No Spreader, Hoist, Trolley, PowerSource, Health monitoring.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **Spreader** | Container lifting attachment on CHE | spreaderId, type, size (20/30/40ft), lockStatus, position |
| **Hoist** | Vertical lifting mechanism | position, speed, load, status (WORKING/IDLE) |
| **Trolley** | Horizontal traversing mechanism on gantry | position, speed, status |
| **Boom** | Crane boom extension | angle, position, lockStatus |
| **PowerSource** | Energy source of CHE | type (DIESEL/ELECTRIC/BATTERY/HYDROGEN/HYBRID), fuelLevel, energyConsumption |
| **EquipmentHealth** | Maintenance condition indicators | faultCode, alarmCode, hoursToNextService, condition, failureMode |
| **StraddleCarrier** | Mobile stacking crane straddling containers | liftCapacity, stackingHeight, speed |
| **AGV** | Automated guided vehicle for horizontal transport | routeId, batteryLevel, navigationMode, dockingStatus |
| **EmptyContainerHandler** | Forklift for empty container operations | liftCapacity, stackingHeight |

**Challenge:** This is IoT/sensor-level detail. Does it belong in a reference-model
ontology, or is it operational/implementation detail?

**Recommendation:** Add missing CHE types (StraddleCarrier, AGV, EmptyContainerHandler)
as subclasses of TerminalEquipment. Model Spreader and PowerSource as component classes
linked to equipment. Health as a status class. Skip Hoist/Trolley/Boom — too granular
for a reference model (sensor-level data, not domain entities).

---

### Gap 5: Vessel / Carrier Identity — 🟠 HIGH

**TIC 4.0 source:** PAS 4000 examples, CarrierVisit context  
**Current state:** `CarrierVisit` has `carrierType` (string) but NO vessel identity.
No IMO, MMSI, vessel name, voyage number, draft, or vessel type.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **Vessel** | Identity and static attributes of a visiting ship | imoNumber, mmsiNumber, vesselName, callSign, flag, loa, beam, maxDraft, vesselType, teuCapacity |
| **VesselCall** | A vessel's scheduled port call (planning view) | vesselCallId, voyageNumber, vesselRef, portOfCall, eta, ata, etd, atd, berthRef |

**Challenge:** The DCSA ontology already has vessel identity properties on
VesselTransportCall and the booking module. The MMT ontology has Vessel, BargeVessel,
etc. Should TIC define its own Vessel class?

**Recommendation:** Add `Vessel` class in handling-operations or a new sub-module.
This is TIC's view of a vessel (operational attributes relevant to the terminal), not
a duplicate of DCSA/MMT vessel registries. Link `CarrierVisit` → `Vessel` via object
property. Add voyage number and key identity properties.

---

### Gap 6: Process Hierarchy (Order, Lists, CarrierTrip) — 🟠 HIGH

**TIC 4.0 source:** Digital Twin papers, Release 2026.018 Planning function  
**Current state:** Only `JobInstruction` exists. The full TIC 4.0 process hierarchy is deeper.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **Order** | Atomic executable step (Collect → Move → Deliver) | orderType, startTime, endTime, cheRef, cargoRef |
| **JobInstructionList** | Dispatch queue of job instructions | queueId, priority, assignedCHE, status |
| **JobInstructionLogicalList** | Logical batch of JIs (by hatch, train, block) | groupId, groupType (HATCH/TRAIN/BLOCK), workInstructions |
| **CarrierTrip** | Carrier's movement from previous port to terminal | tripId, carrierId, departurePort, eta, legs |
| **Service** | A scheduled service/maintenance window | serviceType, serviceWindow, slotAllocation, readinessStatus |

**Recommendation:** Add `Order` as a subclass of / related to `Move`. Add
`JobInstructionList` and `CarrierTrip` to handling-operations. Skip
`JobInstructionLogicalList` and `OrderSequenceList` — too fine-grained for reference model.

---

### Gap 7: Rail Intermodal — 🟡 MEDIUM

**TIC 4.0 source:** Release 2025.017 (Yard Inventory Rail definitions)  
**Current state:** `RailHead` (infrastructure) and `RailSiding` (location) exist, but NO
rail visit, wagon, or rail inventory position concepts.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **RailVisit** | A train's visit to the terminal (analogous to CarrierVisit) | trainId, arrivalTime, departureTime, trackId, wagonCount |
| **RailWagon** | Individual wagon in a train | wagonNumber, wagonType, slotCount |
| **RailInventoryPosition** | Position/slot on a rail wagon for a container | wagonRef, slotNumber, containerRef |

**Recommendation:** Add to handling-operations. `RailVisit` could be a subclass of
`CarrierVisit` (with carrierType=TRAIN) or a separate class.

---

### Gap 8: Electric CHE / eCHE — 🟡 MEDIUM

**TIC 4.0 source:** Smart eCHE White Paper, Releases 2025.017 and 2026.018  
**Current state:** No electric/battery/charging concepts at all.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **Battery** | Battery pack on electric CHE | batteryId, capacityKWh, stateOfCharge (%), stateOfHealth (%), temperature |
| **ChargingStation** | Charging point for electric CHE | stationId, chargerType, powerKW, status |
| **ChargingSession** | A single charging event | sessionId, startTime, endTime, vehicleRef, energyDeliveredKWh |
| **ElectricTerminalTractor** | Battery-electric yard truck | batteryCapacityKWh, consumptionPerMoveKWh, chargingStrategy |

**Recommendation:** Add Battery and ChargingStation to terminal-infrastructure.
ChargingSession to events. ElectricTerminalTractor as subclass of TerminalTractor.

---

### Gap 9: EDI Message Mapping — 🟡 MEDIUM

**TIC 4.0 source:** Releases 2024.013 (BAPLIE), 2025.014 (COARRI), 2026.018 (CODECO)  
**Current state:** No EDI message concepts. Events cover the operational outcome but NOT
the message exchange model.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **BaplieMessage** | Bay Plan / Container List message | vesselVoyage, portOfLoading, messageDate, containerList |
| **BayPlan** | Derived stowage plan | bayNumber, tier, row, containerRef, weight, portOfDischarge |
| **CoarriMessage** | Container discharge/load confirmation | operationType, containerRef, craneRef, stowagePosition |
| **CodecoMessage** | Container gate in/out interchange | moveType, containerRef, truckRef, sealNumbers |

**Challenge:** Are EDI messages ontology concepts or integration patterns? Reference
models typically capture domain entities, not message formats.

**Recommendation:** Model `BayPlan` / stowage as a domain concept (it's a real physical
plan). Skip individual message classes (BaplieMessage, CoarriMessage, CodecoMessage) —
those are integration artifacts, not domain entities.

---

### Gap 10: Place Ontology & Quay — 🟢 LOW

**TIC 4.0 source:** Release 2026.018  
**Current state:** Location model is comprehensive but lacks the `Place` abstraction and
the `Quay` distinction (physical quay wall vs. Berth allocation).

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **Place** | Generic spatial entity (new TIC 4.0 core subject) | placeId, placeType, coordinates |
| **Quay** | Physical quay wall structure | quayId, quayLength, quayDepth, numberOfBerths, craneRails |

**Recommendation:** Add `Quay` to terminal-infrastructure (it's a physical asset).
`Place` is a meta-concept that maps to the existing `TerminalLocation` — don't add a
duplicate spatial abstraction.

---

### Gap 11: Automation Framework (IEC 62264) — 🟢 LOW

**TIC 4.0 source:** Release 2025.017, Terminal Automation Topology white paper  
**Current state:** No automation or control system concepts.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **AutomationLevel** | IEC 62264 levels 0-5 adapted for ports | level, levelName, functions |
| **TerminalControlSystem** | Real-time dispatch system (Level 2) | tcsId, connectedEquipment |
| **EquipmentControlSystem** | Machine-level control on CHE | ecsId, cheRef, controlMode |
| **MaintenanceManagementSystem** | Maintenance orders and schedules | mmsId, maintenanceOrders |

**Recommendation:** OUT OF SCOPE for reference model. These are IT system archetypes,
not domain entities. Document as informational references in README.

---

### Gap 12: Digital Twin Framework — 🟢 LOW

**TIC 4.0 source:** Multiple white papers  
**Current state:** No Digital Twin concepts.

| Missing Concept | Description | Key Properties |
|----------------|-------------|----------------|
| **PointOfMeasurement** | Measurement context qualifier | pomFunction, pomTemporal, pomProcess |
| **ContentLevel** | L1-L4 CHE data provision spec | level, subjectCoverage |

**Recommendation:** OUT OF SCOPE for reference model. This is a meta-model for TIC 4.0's
semantic grammar, not domain entities for terminal operations.

---

## Cross-Domain Isolation Analysis

The TIC ontology currently has **zero cross-references** to other derived ontologies.
This is a significant structural gap:

| TIC Concept | Overlapping Ontology | Nature of Overlap |
|-------------|---------------------|-------------------|
| Container (missing) | DCSA `equipment#Container` | Same entity — container passing through terminal |
| Vessel (missing) | DCSA `transport-call#VesselTransportCall`, MMT `transport-means#Vessel` | Same entity — vessel at berth |
| GateInEvent / GateOutEvent | DCSA `events#GateInEvent` / `GateOutEvent` | Same event from different perspectives |
| VesselLoadEvent / VesselDischargeEvent | DCSA `events#LoadedOnVesselEvent` / `DischargedFromVesselEvent` | Same event |
| Terminal as location | DCSA `locations#Terminal`, MMT `locations#Port` | Physical location overlap |
| DangerousGoods (missing) | IMO `dangerous-goods#DangerousGoods` | IMDG classification |
| Seal | DCSA `equipment#sealNumber` (property) | Seal on container |
| Party roles | DCSA `party#Carrier`, `party#Shipper` | Terminal interacts with shipping parties |

**Recommendation:** Add `rdfs:seeAlso` or `owl:equivalentClass` annotations to align
overlapping concepts across ontologies. Don't create owl:imports (keeps modules
independently loadable) but document the semantic alignment.

---

## Priority Summary

### Tier 1 — Structural Gaps (should be in any TIC reference model)
1. 🔴 **Container / Cargo Unit** — the central operational entity is missing
2. 🔴 **Reefer Monitoring** — major TIC 4.0 domain area (3 releases)
3. 🟠 **Vessel / Carrier Identity** — the entity behind CarrierVisit

### Tier 2 — Operational Depth (enriches the existing model)
4. 🟠 **KPI Definitions** — analytics foundation
5. 🟠 **CHE Sub-Subjects** — IoT/sensor foundation (Spreader, PowerSource, Health)
6. 🟠 **Process Hierarchy** — Order, JobInstructionList, CarrierTrip

### Tier 3 — Domain Extensions (TIC 4.0 growth areas)
7. 🟡 **Rail Intermodal** — RailVisit, RailWagon, positions
8. 🟡 **Electric CHE** — Battery, ChargingStation
9. 🟡 **Stowage / BayPlan** — from EDI mapping (domain entity)

### Tier 4 — Skip or Defer
10. 🟢 Place / Quay — add Quay only, skip Place (maps to TerminalLocation)
11. 🟢 Automation Framework — IT architecture, not domain entities
12. 🟢 Digital Twin Framework — meta-model, not domain entities
13. 🟢 EDI Messages — integration artifacts (model BayPlan only)

---

## Estimated Scope (if all Tier 1-3 implemented)

| Area | New Classes | New Properties | New/Modified Files |
|------|------------|----------------|-------------------|
| Container / Cargo Unit | ~4 | ~8 | 1 new module |
| Reefer Monitoring | ~8 | ~12 | 1 new module |
| Vessel Identity | ~2 | ~10 | 1 modified |
| KPIs | ~7 | ~10 | 1 new module |
| CHE Sub-Subjects | ~6 | ~10 | 1 modified |
| Process Hierarchy | ~4 | ~6 | 1 modified |
| Rail Intermodal | ~3 | ~5 | 1 modified |
| Electric CHE | ~4 | ~8 | 2 modified |
| BayPlan/Stowage | ~2 | ~5 | 1 new or modified |
| Quay | ~1 | ~3 | 1 modified |
| Cross-domain alignment | 0 | ~5 annotations | Multiple |
| **Total** | **~41** | **~82** | **~12** |

---

## Recommendations

### R1: Create Container/CargoUnit module (CRITICAL)
Add a `cargo-unit` sub-module to handling-operations or as a standalone module.
Define `CargoUnit` (abstract parent), `Container` (with ISO identity, weight,
condition), `Seal`, `ContainerCondition`. Link `CargoVisit` → `CargoUnit` and
events → `CargoUnit` via object properties.

### R2: Create Reefer Monitoring module (CRITICAL)
New module `reefer-monitoring/reefer-monitoring.ttl` with ReeferMonitoring,
VentilationSystem, HumiditySystem classes. Add ReeferRack and ReeferSlot to
locations. Add ReeferAlarmEvent, ReeferPlugInEvent, ReeferPlugOutEvent to events.

### R3: Add Vessel identity (HIGH)
Add `Vessel` and `VesselCall` classes to handling-operations or a new `vessel`
sub-module. Link `CarrierVisit` → `Vessel` and `VesselCall` → `Vessel` via
object properties. Include IMO, MMSI, vessel name, voyage number, draft.

### R4: Create KPI module (HIGH)
New module `kpi/kpi.ttl` with KPI base class and 6+ specific KPI subclasses.
KPIs link to CarrierVisit, YardArea, QuayCrane via object properties.

### R5: Enrich CHE equipment types (HIGH)
Add StraddleCarrier, AGV, EmptyContainerHandler as subclasses of TerminalEquipment.
Add Spreader, PowerSource, EquipmentHealth as component/status classes linked to
equipment via object properties.

### R6: Deepen process hierarchy (HIGH)
Add Order (child of JobInstruction), JobInstructionList, CarrierTrip to
handling-operations. Link CarrierTrip → CarrierVisit.

### R7: Add rail intermodal concepts (MEDIUM)
Add RailVisit, RailWagon, RailInventoryPosition to handling-operations.

### R8: Add electric CHE concepts (MEDIUM)
Add Battery, ChargingStation to terminal-infrastructure. ChargingSession to events.
ElectricTerminalTractor as subclass of TerminalTractor.

### R9: Add BayPlan / Stowage (MEDIUM)
Add BayPlan class (domain entity, not message) to handling-operations or a new
stowage sub-module. Link to VesselCall and Container.

### R10: Add Quay to infrastructure (LOW)
Add Quay class to terminal-infrastructure as physical asset distinct from Berth.

### R11: Document cross-domain alignment (ALL PHASES)
Add `rdfs:seeAlso` annotations on overlapping concepts referencing DCSA, MMT,
and IMO ontology IRIs. Update README with cross-reference table.
