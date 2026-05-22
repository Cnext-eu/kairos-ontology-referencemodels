# Modeling Session: Route-Schedule Domain (CLdN Logistics)

**Started:** 2026-05-22T16:25:00+02:00
**Last updated:** 2026-05-22T16:25:00+02:00
**Status:** IN_PROGRESS

## Domain Scope

| Decision | Choice | Confirmed? |
|----------|--------|-----------|
| Domain name | route-schedule | ✅ |
| Namespace | `https://cldn.com/ont/route-schedule#` | ❓ |
| Reference model imports | MMT/Route Network + MMT/Inland Transport | ❓ |

## Source Evidence (from Power BI reports)

### d_ShippingRoutes (CR01)
- Shipping.Route, UniformeRoutes, ShipperType, SearchName, PK_SHIPPINGROUTE

### d_Market (CR01 — lane/market classification)
- Market, LoadingCountry, UnloadingCountry, FromTo, ReferenceMargin
- PlanningChartLoad, PlanningChartUnload, MarketExceptions
- RefMarginTrailers, RefMarginContainers, UnitType
- PostalCodes (loading/unloading), Countries (loading/unloading)

### d_market_sender / d_market_receiver (Quotes)
- PK_MARKET, Market Source, Market Code, Country Code, Postal Code, City

### d_intermodalleg_sea / d_intermodalleg_train (Quotes)
- PK_INTERMODALLEG, Intermodalleg ID, Intermodalleg Source
- Leg Type (sea/train), Leg Code, RouteName

## Classes Confirmed

| # | Class Name | Business Term | Subclass of | Status |
|---|-----------|---------------|-------------|--------|
| | | | | |

## Design Decisions Log

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
