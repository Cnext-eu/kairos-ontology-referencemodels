# Modeling Session: Equipment Domain (CLdN Logistics)

**Started:** 2026-05-22T16:20:00+02:00
**Last updated:** 2026-05-22T16:20:00+02:00
**Status:** IN_PROGRESS

## Domain Scope

| Decision | Choice | Confirmed? |
|----------|--------|-----------|
| Domain name | equipment | ✅ |
| Namespace | `https://cldn.com/ont/equipment#` | ❓ |
| Reference model imports | MMT/Equipment | ❓ |
| Subclass vs extend strategy | TBD | ❓ |

## Source Evidence (from Power BI reports)

### d_Asset (Quotes — Databricks)
- PK_ASSET, Asset ID (int), Asset Source, Asset Code, Asset Name

### d_Asset (CR01 — SharePoint lookup)
- TransportMediumTypeDescr (lowercased text), UnitType (classification code)

### d_UnitTypes (BIS — static lookup)
- TransportMediumTypeDescr, Unit_Type

### f_EmptyLocation (BIS — asset availability tracking)
- TransportMedium, TransportMediumTypeDescr, TransportmediumActive, AvailabilityStatus
- EquipmentOwner, OrderNo, CountryCode, PostalCodeCountry, VisitingAddressCity
- DropOff/PickUp/Ship, ActualDate, PlannedDate, ActualTime, OrderType

### f_Hpi / f_LoadDelivery (BIS — haulier ops)
- PhysicalNo (physical asset number), TransportMedium, UnitType

## Classes Confirmed

| # | Class Name | Business Term | Subclass of | Status |
|---|-----------|---------------|-------------|--------|
| | | | | |

## Properties Confirmed

| # | Property | Domain | Range | Business Term | Status |
|---|----------|--------|-------|---------------|--------|
| | | | | | |

## Open Questions

- [ ] Confirm class structure
- [ ] UnitType as enumeration or separate class?

## Design Decisions Log

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
