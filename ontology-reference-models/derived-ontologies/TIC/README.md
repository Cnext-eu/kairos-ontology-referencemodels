# TIC 4.0 Terminal Industry Ontology

**Namespace:** `https://www.kairosflow.ai/ont/tic#`  
**Version:** 1.0.0  
**Created:** 2026-05-16  
**Source:** Terminal Industry Committee (TIC) 4.0 Standard

## Description

A comprehensive ontology for terminal and port operations based on the Terminal Industry Committee (TIC) 4.0 Standard. The ontology is modularised into six domain-specific sub-ontologies, each independently reusable and collectively imported by the root ontology.

## Structure

| Module | File | Namespace | Classes |
|--------|------|-----------|---------|
| **Root** | `tic.ttl` | `https://www.kairosflow.ai/ont/tic#` | Imports all 6 domain modules |
| **Terminal Infrastructure** | `terminal-infrastructure/terminal-infrastructure.ttl` | `https://www.kairosflow.ai/ont/tic/terminal-infrastructure#` | Terminal, Berth, YardArea, Gate, StorageZone, RailHead, BargeConnection, QuayCrane, YardCrane, ReachStacker, TerminalTractor |
| **Handling Operations** | `handling-operations/handling-operations.ttl` | `https://www.kairosflow.ai/ont/tic/handling-operations#` | StevedoringOperation, LoadMove, DischargeMove, LiftMove, HorizontalMove, MoveSequence, MoveInstruction, MoveCompletion, ExceptionDuringMove, HandlingEquipmentAssignment |
| **Automotive Services** | `automotive-services/automotive-services.ttl` | `https://www.kairosflow.ai/ont/tic/automotive-services#` | VehicleUnit, VIN, VehicleStorage, PDI, Wash, VehicleEnhancement, VehicleModification, TechnicalService, BodyRepair, VehicleReleaseStatus, DamageReport |
| **Party** | `party/party.ttl` | `https://www.kairosflow.ai/ont/tic/party#` | TerminalOperator, Stevedore, GateAgent, YardPlanner, ShiftSupervisor, VehicleServiceProvider |
| **Locations** | `locations/locations.ttl` | `https://www.kairosflow.ai/ont/tic/locations#` | Terminal, Berth, YardPosition, GateLane, QuaySide, StackPosition, ReeferPlug, RailSiding, BargeQuay |
| **Events** | `events/events.ttl` | `https://www.kairosflow.ai/ont/tic/events#` | GateInEvent, GateOutEvent, YardMoveEvent, VesselLoadEvent, VesselDischargeEvent, StackEvent, ServiceCompleteEvent, DamageDetectedEvent, InspectionEvent |

## Coverage

- **Terminal Infrastructure** — physical assets, berths, yard areas, gates, intermodal connections, and cargo handling equipment (quay cranes, yard cranes, reach stackers, terminal tractors)
- **Handling Operations** — stevedoring operations, load/discharge/lift/horizontal moves, move sequencing, instructions, completion tracking, exceptions, and equipment assignments
- **Automotive Services** — vehicle units, VIN identification, storage, pre-delivery inspections (PDI), washing, enhancements, modifications, technical services, body repair, release status, and damage reporting
- **Party Roles** — terminal operators, stevedores, gate agents, yard planners, shift supervisors, and vehicle service providers
- **Locations** — terminal-level through stack-position-level addressing (block-bay-row-tier), gate lanes, quay sides, reefer plugs, rail sidings, and barge quays
- **Events** — gate in/out, yard moves, vessel load/discharge, stacking, service completion, damage detection, and inspections

## Standards Alignment

- Terminal Industry Committee (TIC) 4.0 Standard
- ISO 3779 / ISO 3780 (VIN)
- UN/LOCODE for port identification
- SMDG / BIC facility codes

## Key Features

- Modular design — each domain is a standalone `owl:Ontology` importable independently
- OWL class restrictions enforce structural constraints (e.g., MoveSequence must have ≥1 move)
- Object and datatype properties with domain/range declarations
- Inverse properties for bidirectional navigation
- Comprehensive `rdfs:label` and `rdfs:comment` annotations with TIC context

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
