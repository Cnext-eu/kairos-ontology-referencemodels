# RAIL Ontology — TAF TSI Rail Reservation & Running Model

This directory contains the modularized Kairos RAIL ontology, a **derived** ontology
grounded in the EU **TAF TSI** (Technical Specification for Interoperability —
Telematics Applications for Freight) data catalogue.

## Scope and grain

This ontology specialises the **carrier-reservation grain** (grain 3 of the
`multimodal-order-leg` pattern) and the **movement/running grain** (grain 4) for
rail. It does **not** model a `RailOrder` — mode never lives on the order grain.
Order-level consignment is already covered by `mmt/documents#RailConsignmentNote`
(CIM consignment note). This ontology provides the rail-specific reservation,
path allocation, rolling-stock, and train-running concepts that bind at the
reservation grain, hub-local.

## Source and provenance

- **Standard:** TAF TSI — Commission Regulation (EU) No 1305/2012 as amended,
  Annex D.2 Appendix F (Data Catalogue).
- **Machine-readable source:** `taf_cat_complete.xsd` — the official TAF TSI
  data catalogue XML schema, published by the European Union Agency for
  Railways (ERA) at <https://github.com/EU-Agency-for-Railways/TSI_TAF>.
- **Implementation guideline:** ERA-TD-105 (TAF TSI Implementation Guide).
- Every `owl:Class` in this ontology is backed by a documented TAF TSI data
  element (verified by `refmodels-ontology-audit`). No invented classes.

## Structure

```
RAIL/
├── current/
│   ├── rail.ttl                         # Root (imports all modules)
│   ├── consignment/consignment.ttl      # Consignment Order Message (ORFEUS ECN)
│   ├── path-request/path-request.ttl    # Path Request / allocation (PCS)
│   ├── train-running/train-running.ttl  # Train running data, forecasts, interruptions
│   ├── rolling-stock/rolling-stock.ttl  # Wagon, locomotive, telematics
│   ├── party/party.ttl                  # Railway Undertaking (RU), Infrastructure Manager (IM)
│   └── shared-kernel/shared-kernel.ttl  # Location, timing, identifiers
├── archive/
├── VERSION
└── README.md
```

## Module map (TAF TSI message families)

| Module | TAF TSI source elements | Grain |
|---|---|---|
| `consignment` | `ConsignmentOrderMessage`, `ConsignmentLevelData`, `ConsignmentNumber`, `ShipmentType`, `ExceptionalConsignment` | Reservation (3) |
| `path-request` | `PathRequestMessage`, `PathConfirmedMessage`, `PathCanceledMessage`, `PathNotAvailableMessage`, `PathDetailsMessage`, `PathDetailsRefusedMessage`, `PreArrangedPath`, `OnDemandPath` | Reservation (3) |
| `train-running` | `TrainRunningInformationMessage`, `TrainRunningForecastMessage`, `TrainRunningInterruptionMessage`, `TrainRunningData`, `TrainRunningTechData`, `TrainLocationStatus` | Movement (4) |
| `rolling-stock` | `WagonStatusMessage`, `WagonLocationStatus`, `WagonAtDeparture`, `WagonTelematics`, `TelematicsDevice`, `TelematicsOnBoard` | Movement (4) |
| `party` | `AllocationCompany`, `CustomerCode`, Railway Undertaking / Infrastructure Manager roles | Reservation (3) |
| `shared-kernel` | `LocationIdent`, `CompositIdentifierPlannedType`, `ValidityPeriodType`, `BitmapDays`, timing primitives | Shared |

## Versioning

Current version: **1.0.0** (initial release). See `VERSION`. Archived versions
live under `archive/<version>/`.
