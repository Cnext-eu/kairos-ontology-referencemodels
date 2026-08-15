# Modeling Session: DCSA Domain v3.1 Gap Alignment

**Started:** 2026-06-21T20:52:56+02:00
**Last updated:** 2026-06-21T20:52:56+02:00
**Status:** COMPLETED

## Domain Scope

| Decision | Choice | Confirmed? |
|----------|--------|-----------|
| Domain name | DCSA reference ontology | Yes |
| Namespace | Existing DCSA module namespaces | Yes |
| Reference model imports | Existing modular DCSA structure | Yes |
| Subclass vs extend strategy | Add source-backed properties to existing classes only; no new classes | Yes |
| TMDL consulted | not-available | Yes |

## Classes Confirmed

No new classes were introduced. Existing classes receive selected DCSA Domain v3.1.0 datatype properties.

## Properties Confirmed

| # | Property | Domain | Range | Business Term | Status |
|---|----------|--------|-------|---------------|--------|
| 1 | `bookingRequestDateTime` | `booking:Booking` | `xsd:dateTime` | Booking request created timestamp | Confirmed |
| 2 | `bookingUpdatedDateTime` | `booking:Booking` | `xsd:dateTime` | Booking updated timestamp | Confirmed |
| 3 | `bargeOperatorCarrierCodeListProvider` | `transport-call:BargeTransportCall` | `xsd:string` | Barge operator carrier code list provider | Confirmed |
| 4 | `facilityTypeCodeTRN` | `transport-call:TransportCall` | `xsd:string` | Transport-call facility type code | Confirmed |
| 5 | `facilityTypeCodeOPR` | `events:Event` | `xsd:string` | Operations-event facility type code | Confirmed |
| 6 | `unNumber` | `booking:Commodity` | `xsd:string` | UN dangerous goods number | Confirmed |
| 7 | `imoClass` | `booking:Commodity` | `xsd:string` | IMO dangerous goods class | Confirmed |
| 8 | `properShippingName` | `booking:Commodity` | `xsd:string` | Proper shipping name | Confirmed |
| 9 | `technicalName` | `booking:Commodity` | `xsd:string` | Technical dangerous-goods name | Confirmed |
| 10 | `packingGroup` | `booking:Commodity` | `xsd:integer` | Dangerous goods packing group | Confirmed |
| 11 | `flashPoint` | `booking:Commodity` | `xsd:decimal` | Dangerous goods flash point | Confirmed |
| 12 | `isMarinePollutant` | `booking:Commodity` | `xsd:boolean` | Marine pollutant flag | Confirmed |
| 13 | `isLimitedQuantity` | `booking:Commodity` | `xsd:boolean` | Limited quantity flag | Confirmed |
| 14 | `isReportableQuantity` | `booking:Commodity` | `xsd:boolean` | Reportable quantity flag | Confirmed |

## Source Evidence Table

| # | Source Column | Source Table | System | Data Type | Candidate Property | Candidate Class | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | `bookingRequestDateTime` | `components.schemas.bookingRequestDateTime` | DCSA Domain v3.1.0 | string/date-time | `bookingRequestDateTime` | `Booking` | Direct |
| 2 | `bookingUpdatedDateTime` | `components.schemas.bookingUpdatedDateTime` | DCSA Domain v3.1.0 | string/date-time | `bookingUpdatedDateTime` | `Booking` | Direct |
| 3 | `bargeOperatorCarrierCodeListProvider` | `components.schemas.bargeOperatorCarrierCodeListProvider` | DCSA Domain v3.1.0 | string | `bargeOperatorCarrierCodeListProvider` | `BargeTransportCall` | Direct |
| 4 | `facilityTypeCodeTRN` | `components.schemas.facilityTypeCodeTRN` | DCSA Domain v3.1.0 | string | `facilityTypeCodeTRN` | `TransportCall` | Direct |
| 5 | `facilityTypeCodeOPR` | `components.schemas.facilityTypeCodeOPR` | DCSA Domain v3.1.0 | string | `facilityTypeCodeOPR` | `Event` | Direct |
| 6 | `unNumber` | `components.schemas.unNumber` | DCSA Domain v3.1.0 | string | `unNumber` | `Commodity` | Direct |
| 7 | `imoClass` | `components.schemas.imoClass` | DCSA Domain v3.1.0 | string | `imoClass` | `Commodity` | Direct |
| 8 | `properShippingName` | `components.schemas.properShippingName` | DCSA Domain v3.1.0 | string | `properShippingName` | `Commodity` | Direct |
| 9 | `technicalName` | `components.schemas.technicalName` | DCSA Domain v3.1.0 | string | `technicalName` | `Commodity` | Direct |
| 10 | `packingGroup` | `components.schemas.packingGroup` | DCSA Domain v3.1.0 | integer/int32 | `packingGroup` | `Commodity` | Direct |
| 11 | `flashPoint` | `components.schemas.flashPoint` | DCSA Domain v3.1.0 | number/float | `flashPoint` | `Commodity` | Direct |
| 12 | `isMarinePollutant` | `components.schemas.isMarinePollutant` | DCSA Domain v3.1.0 | boolean | `isMarinePollutant` | `Commodity` | Direct |
| 13 | `isLimitedQuantity` | `components.schemas.isLimitedQuantity` | DCSA Domain v3.1.0 | boolean | `isLimitedQuantity` | `Commodity` | Direct |
| 14 | `isReportableQuantity` | `components.schemas.isReportableQuantity` | DCSA Domain v3.1.0 | boolean | `isReportableQuantity` | `Commodity` | Direct |

## Design Decisions Log

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Scope of DCSA Domain v3.1.0 fit-gap additions | Add 14 high-value missing terms only | Avoid mirroring all 232 simple types while closing operationally important gaps |
| 2 | How to handle remaining missing DCSA Domain fields | Document that more fields may be mapped through full DCSA Domain v3.1 fit-gap discovery | Keeps current release focused and preserves traceability for future modeling |

## Source Alignment Warnings

| # | Issue | TMDL/Source says | Ref model says | Decision | Status |
|---|-------|-----------------|----------------|----------|--------|
| 1 | `bookingRequestDateTime` is in DCSA Domain v3.1.0 but absent from BKG v2.0.4 API | DCSA Domain defines the field | Latest released BKG API does not expose it | Include as DCSA Domain-backed reference-model property and note API drift | Resolved |
