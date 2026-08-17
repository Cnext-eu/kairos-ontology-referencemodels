# TIC 4.0 Terminal Industry Ontology

**Namespace:** `https://www.kairosflow.ai/ont/tic#`  
**Version:** 1.2.0  
**Created:** 2026-05-16  
**Source:** TIC4.0 Release 2025.017 / BSI PAS 4000:2026  
**Reference:** https://tic40.org/standards/

## Description

An ontology for terminal and port operations based on the TIC 4.0 standard (BSI PAS 4000:2026). The ontology is modularised into eight domain-specific sub-ontologies aligned with TIC 4.0 core subjects and concepts.

## Structure

| Module | File | Namespace | Classes |
|--------|------|-----------|---------|
| **Root** | `tic.ttl` | `https://www.kairosflow.ai/ont/tic#` | Imports all 8 domain modules |
| **Terminal Infrastructure** | `terminal-infrastructure/terminal-infrastructure.ttl` | `https://www.kairosflow.ai/ont/tic/terminal-infrastructure#` | Terminal, Berth, YardArea, Gate, StorageZone, RailHead, BargeConnection, QuayCrane, YardCrane, ReachStacker, TerminalTractor, StraddleCarrier, AutomatedGuidedVehicle, EmptyContainerHandler, Spreader, PowerSource, EquipmentHealth, Quay, ElectricTerminalTractor, Battery, ChargingStation |
| **Handling Operations** | `handling-operations/handling-operations.ttl` | `https://www.kairosflow.ai/ont/tic/handling-operations#` | CarrierVisit, CargoVisit, Move, LoadMove, DischargeMove, LiftMove, HorizontalMove, Cycle, JobInstruction, Seal, CarrierTrip, Order, StowagePlan, RailVisit, RailWagon |
| **Reefer Monitoring** | `reefer-monitoring/reefer-monitoring.ttl` | `https://www.kairosflow.ai/ont/tic/reefer-monitoring#` | ReeferMonitoring, ReeferRack, ReeferSlot |
| **KPI Definitions** | `kpi/kpi.ttl` | `https://www.kairosflow.ai/ont/tic/kpi#` | KPI |
| **Automotive Services** | `automotive-services/automotive-services.ttl` | `https://www.kairosflow.ai/ont/tic/automotive-services#` | VehicleUnit, VIN, VehicleStorage, PDI, Wash, BodyRepair, VehicleReleaseStatus, DamageReport |
| **Party** | `party/party.ttl` | `https://www.kairosflow.ai/ont/tic/party#` | TerminalParty, TerminalOperator, Stevedore |
| **Locations** | `locations/locations.ttl` | `https://www.kairosflow.ai/ont/tic/locations#` | Terminal, Berth, YardPosition, GateLane, QuaySide, ReeferPlug, RailSiding, BargeQuay |
| **Events** | `events/events.ttl` | `https://www.kairosflow.ai/ont/tic/events#` | GateInEvent, GateOutEvent, YardMoveEvent, VesselLoadEvent, VesselDischargeEvent, StackEvent, ServiceCompleteEvent, DamageDetectedEvent, InspectionEvent, ReeferPlugInEvent, ReeferPlugOutEvent, ReeferAlarmEvent, ChargingSessionEvent |

## Coverage

- **Terminal Infrastructure** — physical assets, berths, yard areas, gates, intermodal connections, quay walls, and cargo handling equipment (quay cranes, yard cranes, reach stackers, terminal tractors, straddle carriers, AGVs, empty container handlers) with equipment components (spreaders, power sources, health monitoring) and electric CHE infrastructure (batteries, charging stations)
- **Handling Operations** — carrier visits (with vessel identity), cargo visits (with container identity, seals, condition), moves (load/discharge/lift/horizontal), cycles, job instructions, orders, carrier trips, stowage plans, and rail intermodal (rail visits, wagons)
- **Reefer Monitoring** — reefer container temperature and atmosphere monitoring, alarm management, and reefer yard infrastructure (racks and slots)
- **KPI Definitions** — standardized terminal performance metric definitions (berth productivity, crane productivity, dwell time, truck turnaround, yard utilization, vessel turnaround)
- **Automotive Services** — vehicle units, VIN identification, storage, pre-delivery inspections (PDI), washing, body repair, release status, and damage reporting
- **Party Roles** — terminal operators and stevedores
- **Locations** — terminal-level through yard-position-level addressing (block-bay-row-tier), gate lanes, quay sides, reefer plugs, rail sidings, and barge quays
- **Events** — gate in/out, yard moves, vessel load/discharge, stacking, service completion, damage detection, inspections, reefer plug-in/plug-out, reefer alarms, and charging sessions

## Cross-Domain Alignment

The TIC ontology uses `rdfs:seeAlso` annotations to document semantic alignment with other Kairos reference-model ontologies without creating hard imports:

| TIC Concept | Aligned Ontology | Relationship |
|-------------|-----------------|-------------|
| CarrierVisit | IMO vessel-registry, IMO port-call | Vessel identity and port call context |
| CargoVisit | DCSA equipment | Container identity (ISO 6346) |
| Terminal (locations) | DCSA locations#Terminal | Same physical facility |
| GateInEvent / GateOutEvent | DCSA events | Same event from terminal vs. carrier perspective |
| VesselLoadEvent / VesselDischargeEvent | DCSA events | Same event from terminal vs. carrier perspective |

Hub ontologies should compose via `owl:imports` at integration time to connect these domains.

Within the TIC tree, a module that asserts `rdfs:domain` or `rdfs:range` against a sibling
TIC class declares its own `owl:imports` for that module — twelve such assertions across six
modules were dangling and invisible to consumers until 1.5.0 (gh#97). Enforced by
`validate_structure.py` check 10. Cross-*vendor* alignment stays annotation-only, via the
`rdfs:seeAlso` table above.

## Standards Alignment

- TIC4.0 Release 2025.017 / BSI PAS 4000:2026
- ISO 6346 (Container identification)
- ISO 3779 / ISO 3780 (VIN)
- ISO 17712 (Mechanical seals)
- SOLAS VI/2 (Verified Gross Mass)
- UN/LOCODE for port identification
- SMDG / BIC facility codes

## Key Features

- Modular design — each domain is a standalone `owl:Ontology` importable independently
- OWL class restrictions enforce structural constraints (e.g., Cycle must have ≥1 move)
- Object and datatype properties with domain/range declarations
- Inverse properties for bidirectional navigation
- Cross-domain alignment via `rdfs:seeAlso` (no hard imports to other derived ontologies)
- Comprehensive `rdfs:label` and `rdfs:comment` annotations with TIC 4.0 context

## Changelog

### v1.2.0 (2026-07-15)
- **New modules:** reefer-monitoring, kpi
- **Handling operations:** Added Seal, CarrierTrip, Order, StowagePlan, RailVisit, RailWagon; cargo visit properties (containerNumber, isoTypeCode, conditionCode, weightClass, holdStatus); vessel identity on CarrierVisit (IMO, MMSI, name, voyage, draft, LOA)
- **Terminal infrastructure:** Added StraddleCarrier, AGV, EmptyContainerHandler, Spreader, PowerSource, EquipmentHealth, Quay, ElectricTerminalTractor, Battery, ChargingStation
- **Events:** Added ReeferPlugInEvent, ReeferPlugOutEvent, ReeferAlarmEvent, ChargingSessionEvent; cross-domain rdfs:seeAlso to DCSA events
- **Cross-domain:** Added rdfs:seeAlso annotations aligning TIC concepts to IMO, DCSA

### v1.1.0 (2026-05-21)
- Initial modular structure with 6 domain modules
- Core operational model: visits, moves, cycles, job instructions

## Usage

Import the root ontology to pull in all domains:

```turtle
@prefix tic: <https://www.kairosflow.ai/ont/tic#> .

<http://example.org/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/tic#> .
```

Or import individual domains:

```turtle
@prefix tic-evt: <https://www.kairosflow.ai/ont/tic/events#> .

<http://example.org/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/tic/events#> .
```
