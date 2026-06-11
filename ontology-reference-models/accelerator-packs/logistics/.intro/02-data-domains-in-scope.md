# Data Domains in Scope (Logistics Blueprint)

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-11

The blueprint groups domain ontologies by business ownership question (L1 group) and concrete domain modules (L2).

## Group and domain overview

| L1 Group | Ownership question | L2 domains in scope |
|---|---|---|
| Party & Commercial | Who are we doing business with, under what terms, at what price? | Party, Commercial, Booking, Financial |
| Transport & Cargo | What is being moved, by which route and asset? | Consignment, Cargo, Equipment, Route-Schedule, Intermodal |
| Maritime & Terminal | What happens on vessels, at berths, gates, and yards? | Vessel-Maritime, Terminal-Operations, RoRo, Automotive |
| Compliance & Sustainability | What must be reported or restricted? | Dangerous-Goods, Customs, Compliance, Sustainability |
| Visibility & Events | What happened, where, when, to what? | Events, Claims, Documents, Reference-Data |
| Master Data Management | What is the single golden-record truth? | MDM |

## Quick domain coverage

| Domain | Quick coverage summary |
|---|---|
| Party | Legal entities, organisations, roles, contacts |
| Commercial | Contracts, trade terms, service commitments |
| Booking | Quotes, booking lifecycle, customer instructions |
| Financial | Charges, surcharges, invoicing, settlement, revenue and cost analytics |
| Consignment | Shipments, transport legs, multimodal movement |
| Cargo | Goods, packaging, dimensions, weight, handling attributes |
| Equipment | Containers, trailers, reefers, chassis, equipment status |
| Route-Schedule | Service loops, schedules, cut-offs, transit times |
| Intermodal | Inland transport execution (rail, barge, road legs) |
| Vessel-Maritime | Vessel registry, voyages, port call lifecycle |
| Terminal-Operations | Berths, gates, yards, handling moves, stevedoring |
| RoRo | RoRo-specific rolling cargo and lane-metre context |
| Automotive | Vehicle logistics services (PDI, wash, repair, release) |
| Dangerous-Goods | DG classification, restrictions, IMDG-aligned semantics |
| Customs | Customs declarations, border filings, regulatory statuses |
| Compliance | Governance, policy, legal and regulatory obligations |
| Sustainability | Emissions, energy, ESG indicators and reporting |
| Events | Cross-domain operational event normalization |
| Claims | Damage, incidents, exceptions and claim lifecycle |
| Documents | Transport/commercial documents and evidence links |
| Reference-Data | Shared codes, identifiers, locations, UoM, currencies |
| MDM | Golden records, crosswalks, match/merge, survivorship |

## Notes for implementation

- Not every client activates every domain in phase 1.
- Specialist domains (for example RoRo, Automotive, Intermodal) are activated based on operational profile.
- MDM is intentionally cross-cutting and decoupled from domain imports.
