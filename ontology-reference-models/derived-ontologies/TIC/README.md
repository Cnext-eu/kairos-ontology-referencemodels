# TIC 4.0 Terminal Industry Ontology

**Namespace:** `https://www.kairosflow.ai/ont/tic#`  
**Version:** 1.1.0  
**Created:** 2026-05-16  
**Source:** TIC4.0 Release 2025.017 / BSI PAS 4000:2026  
**Reference:** https://tic40.org/standards/

## Description

An ontology for terminal and port operations based on the TIC 4.0 standard (BSI PAS 4000:2026). The ontology is modularised into six domain-specific sub-ontologies aligned with TIC 4.0 core subjects and concepts.

## Structure

| Module | File | Namespace | Classes |
|--------|------|-----------|---------|
| **Root** | `tic.ttl` | `https://www.kairosflow.ai/ont/tic#` | Imports all 6 domain modules |
| **Terminal Infrastructure** | `terminal-infrastructure/terminal-infrastructure.ttl` | `https://www.kairosflow.ai/ont/tic/terminal-infrastructure#` | Terminal, Berth, YardArea, Gate, StorageZone, RailHead, BargeConnection, QuayCrane, YardCrane, ReachStacker, TerminalTractor |
| **Handling Operations** | `handling-operations/handling-operations.ttl` | `https://www.kairosflow.ai/ont/tic/handling-operations#` | CarrierVisit, CargoVisit, Move, LoadMove, DischargeMove, LiftMove, HorizontalMove, Cycle, JobInstruction |
| **Automotive Services** | `automotive-services/automotive-services.ttl` | `https://www.kairosflow.ai/ont/tic/automotive-services#` | VehicleUnit, VIN, VehicleStorage, PDI, Wash, BodyRepair, VehicleReleaseStatus, DamageReport |
| **Party** | `party/party.ttl` | `https://www.kairosflow.ai/ont/tic/party#` | TerminalParty, TerminalOperator, Stevedore |
| **Locations** | `locations/locations.ttl` | `https://www.kairosflow.ai/ont/tic/locations#` | Terminal, Berth, YardPosition, GateLane, QuaySide, ReeferPlug, RailSiding, BargeQuay |
| **Events** | `events/events.ttl` | `https://www.kairosflow.ai/ont/tic/events#` | GateInEvent, GateOutEvent, YardMoveEvent, VesselLoadEvent, VesselDischargeEvent, StackEvent, ServiceCompleteEvent, DamageDetectedEvent, InspectionEvent |

## Coverage

- **Terminal Infrastructure** — physical assets, berths, yard areas, gates, intermodal connections, and cargo handling equipment (quay cranes, yard cranes, reach stackers, terminal tractors)
- **Handling Operations** — carrier visits, cargo visits, moves (load/discharge/lift/horizontal), cycles, and job instructions
- **Automotive Services** — vehicle units, VIN identification, storage, pre-delivery inspections (PDI), washing, body repair, release status, and damage reporting
- **Party Roles** — terminal operators and stevedores
- **Locations** — terminal-level through yard-position-level addressing (block-bay-row-tier), gate lanes, quay sides, reefer plugs, rail sidings, and barge quays
- **Events** — gate in/out, yard moves, vessel load/discharge, stacking, service completion, damage detection, and inspections

## Standards Alignment

- TIC4.0 Release 2025.017 / BSI PAS 4000:2026
- ISO 3779 / ISO 3780 (VIN)
- UN/LOCODE for port identification
- SMDG / BIC facility codes

## Key Features

- Modular design — each domain is a standalone `owl:Ontology` importable independently
- OWL class restrictions enforce structural constraints (e.g., Cycle must have ≥1 move)
- Object and datatype properties with domain/range declarations
- Inverse properties for bidirectional navigation
- Comprehensive `rdfs:label` and `rdfs:comment` annotations with TIC 4.0 context

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
