# Modeling Session: Financial

**Started:** 2026-05-22 17:10
**Last updated:** 2026-05-22 17:12
**Status:** COMPLETED

## Domain Scope

| Decision | Choice | Confirmed? |
|----------|--------|-----------|
| Domain name | financial | ✅ |
| Namespace | `https://cldn.com/ont/financial#` | ✅ |
| Reference model imports | None (standalone — BSP/Financial is invoicing, not operational costs) | ✅ |
| Subclass vs extend strategy | Standalone classes | ✅ |

## Classes Confirmed

| # | Class Name | Business Term | Subclass of | Status |
|---|-----------|---------------|-------------|--------|
| 1 | DemurrageCharge | Demurrage Charge | owl:Thing (standalone) | ✅ Confirmed |
| 2 | HaulierPerformance | Haulier Performance (HPI) | owl:Thing (standalone) | ✅ Confirmed |

## Properties Confirmed

| # | Property | Domain | Range | Business Term | Status |
|---|----------|--------|-------|---------------|--------|
| 1 | demurrageReference | DemurrageCharge | xsd:string | Reference ID | ✅ |
| 2 | demurrageDays | DemurrageCharge | xsd:integer | Days overdue | ✅ |
| 3 | demurrageAmount | DemurrageCharge | xsd:decimal | Charge amount | ✅ |
| 4 | freeTimeDays | DemurrageCharge | xsd:integer | Free days | ✅ |
| 5 | returnDate | DemurrageCharge | xsd:date | Return date | ✅ |
| 6 | dueDate | DemurrageCharge | xsd:date | Due date | ✅ |
| 7 | currency | DemurrageCharge | xsd:string | Currency code | ✅ |
| 8 | performancePeriod | HaulierPerformance | xsd:date | Assessment period | ✅ |
| 9 | costPerKm | HaulierPerformance | xsd:decimal | Cost/km | ✅ |
| 10 | totalCost | HaulierPerformance | xsd:decimal | Total cost | ✅ |
| 11 | totalKm | HaulierPerformance | xsd:decimal | Total km | ✅ |
| 12 | geozone | HaulierPerformance | xsd:string | Geozone | ✅ |
| 13 | forOrder | DemurrageCharge | TransportOrder | Order FK | ✅ |
| 14 | forAsset | DemurrageCharge | Asset | Asset FK | ✅ |
| 15 | forHaulier | HaulierPerformance | Haulier | Haulier FK | ✅ |

## Design Decisions Log

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Import BSP/Financial? | No | BSP/Financial = invoicing/payments; CLdN needs = operational charges + KPIs |
| 2 | Demurrage as Invoice subclass? | No | Demurrage is a penalty charge, not an AR invoice |
| 3 | HPI as standalone? | Yes | CLdN-specific KPI concept with no reference model equivalent |
