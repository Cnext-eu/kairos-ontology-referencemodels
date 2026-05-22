# Modeling Session: Consignment

**Started:** 2026-05-22 17:00
**Last updated:** 2026-05-22 17:05
**Status:** COMPLETED

## Domain Scope

| Decision | Choice | Confirmed? |
|----------|--------|-----------|
| Domain name | consignment | ✅ |
| Namespace | `https://cldn.com/ont/consignment#` | ✅ |
| Reference model imports | MMT/Consignment | ✅ |
| Subclass vs extend strategy | Subclass (TransportOrder extends Consignment) | ✅ |

## Classes Confirmed

| # | Class Name | Business Term | Subclass of | Status |
|---|-----------|---------------|-------------|--------|
| 1 | TransportOrder | Transport Order | mmt-consignment:Consignment | ✅ Confirmed |

## Properties Confirmed

| # | Property | Domain | Range | Business Term | Status |
|---|----------|--------|-------|---------------|--------|
| 1 | consignmentReference (inherited) | Consignment | xsd:string | Order No | ✅ REUSE |
| 2 | orderType | TransportOrder | xsd:string | Order Type | ✅ |
| 3 | requestedDate | TransportOrder | xsd:date | Requested Date | ✅ |
| 4 | loadingDate | TransportOrder | xsd:date | Loading Date | ✅ |
| 5 | unloadingDate | TransportOrder | xsd:date | Unloading Date | ✅ |
| 6 | loadingCountry | TransportOrder | xsd:string | Loading Country | ✅ |
| 7 | loadingCity | TransportOrder | xsd:string | Loading City | ✅ |
| 8 | unloadingCountry | TransportOrder | xsd:string | Unloading Country | ✅ |
| 9 | unloadingCity | TransportOrder | xsd:string | Unloading City | ✅ |
| 10 | onTimeCollection | TransportOrder | xsd:string | On Time Collection | ✅ |
| 11 | onTimeDelivery | TransportOrder | xsd:string | On Time Delivery | ✅ |
| 12 | timeOnSite | TransportOrder | xsd:decimal | Time on Site (hours) | ✅ |
| 13 | transitTime | TransportOrder | xsd:decimal | Transit Time (days) | ✅ |
| 14 | fullOrEmpty | TransportOrder | xsd:string | Full/Empty | ✅ |
| 15 | ediOrderEntry | TransportOrder | xsd:string | EDI Order Entry | ✅ |
| 16 | customerServiceTeam | TransportOrder | xsd:string | Customer Service Team | ✅ |
| 17 | companyDescription | TransportOrder | xsd:string | Company Description | ✅ |
| 18 | hasCustomer | TransportOrder | party:Customer | Customer (FK) | ✅ |
| 19 | hasHaulier | TransportOrder | party:Haulier | Haulier (FK) | ✅ |
| 20 | hasAsset | TransportOrder | equipment:Asset | Asset (FK) | ✅ |
| 21 | onShippingRoute | TransportOrder | route-schedule:ShippingRoute | Shipping Route (FK) | ✅ |
| 22 | inMarket | TransportOrder | route-schedule:Market | Market (FK) | ✅ |

## Design Decisions Log

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Single class vs multiple? | Single TransportOrder | All PBI fact tables share OrderNo as PK — different report views, same entity |
| 2 | Subclass Consignment? | Yes | 4/4 criteria met: discriminator, variants, distinct key, distinct name |
| 3 | Reuse consignmentReference? | Yes | Maps directly to OrderNo — avoid redundant property |
| 4 | OTA flags as string? | Yes — "On Time"/"Late"/etc. | Enum values will be defined in silver extension |
