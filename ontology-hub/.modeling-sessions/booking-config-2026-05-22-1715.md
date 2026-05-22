# Modeling Session: Booking

**Started:** 2026-05-22 17:15
**Last updated:** 2026-05-22 17:18
**Status:** COMPLETED

## Domain Scope

| Decision | Choice | Confirmed? |
|----------|--------|-----------|
| Domain name | booking | ✅ |
| Namespace | `https://cldn.com/ont/booking#` | ✅ |
| Reference model imports | None (standalone — DCSA/Booking is carrier reservation, not sales quoting) | ✅ |
| Subclass vs extend strategy | Standalone class | ✅ |

## Classes Confirmed

| # | Class Name | Business Term | Subclass of | Status |
|---|-----------|---------------|-------------|--------|
| 1 | CargoQuote | Cargo Quote | owl:Thing (standalone) | ✅ Confirmed |

## Properties Confirmed

| # | Property | Domain | Range | Business Term | Status |
|---|----------|--------|-------|---------------|--------|
| 1 | quoteReference | CargoQuote | xsd:string | Quote ID | ✅ |
| 2 | quoteStatus | CargoQuote | xsd:string | Status | ✅ |
| 3 | quoteDate | CargoQuote | xsd:date | Quote Date | ✅ |
| 4 | expiryDate | CargoQuote | xsd:date | Expiry Date | ✅ |
| 5 | wonDate | CargoQuote | xsd:date | Won Date | ✅ |
| 6 | bookingDate | CargoQuote | xsd:date | Booking Date | ✅ |
| 7 | forecastLoads | CargoQuote | xsd:integer | Forecast Loads | ✅ |
| 8 | actualLoads | CargoQuote | xsd:integer | Actual Loads | ✅ |
| 9 | quotedPrice | CargoQuote | xsd:decimal | Quoted Price | ✅ |
| 10 | currency | CargoQuote | xsd:string | Currency | ✅ |
| 11 | margin | CargoQuote | xsd:decimal | Margin | ✅ |
| 12 | transportMode | CargoQuote | xsd:string | Transport Mode | ✅ |
| 13 | validityPeriod | CargoQuote | xsd:string | Validity Period | ✅ |
| 14 | forCustomer | CargoQuote | Customer | Customer FK | ✅ |
| 15 | bySalesperson | CargoQuote | Employee | Salesperson FK | ✅ |
| 16 | approvedByManager | CargoQuote | Employee | Manager FK | ✅ |
| 17 | fromMarket | CargoQuote | Market | Origin Market FK | ✅ |
| 18 | toMarket | CargoQuote | Market | Destination Market FK | ✅ |
| 19 | resultsInOrder | CargoQuote | TransportOrder | Resulting Order FK | ✅ |

## Design Decisions Log

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Import DCSA/Booking? | No | DCSA Booking = carrier space reservation; CLdN quote = sales proposal lifecycle |
| 2 | Subclass Booking? | No | Quote lifecycle (Draft→Won) precedes any booking concept |
| 3 | Role-playing dimensions? | Multiple object properties to same class | bySalesperson/approvedByManager both → Employee |
| 4 | Link to TransportOrder? | Yes via resultsInOrder | Won quote creates a transport order |
