# CLdN Data Domain Recommendations

**Purpose:** Recommend a complementary, low-overlap data-domain structure for CLdN’s logistics operating model and ontology roadmap.

**Scope:** CLdN as a short-sea RoRo/LoLo carrier, multimodal transport provider, terminal operator, automotive logistics provider, and project cargo / high-and-heavy logistics provider.

**Recommended design principle:** define domains by **business capability and data ownership**, not by document type or system. A domain should own a coherent set of master data, transactional data, events, and reference data. Other domains should consume it through well-defined relationships.

---

## 1. Executive Recommendation

CLdN should use a **capability-aligned domain model** with a small number of enterprise domains and several logistics-specific domains. The model should avoid overlap by assigning each domain a primary ownership question:

| Domain group | Primary ownership question |
|---|---|
| Party & Commercial | Who are we doing business with, under what agreement, and at what price? |
| Transport & Cargo | What is being transported, by which movement, route, asset, and equipment? |
| Maritime & Terminal | What happens on vessels, at berths, gates, yards, rail/barge links, and terminals? |
| Specialist Logistics | What special handling applies to vehicles, RoRo units, high/heavy cargo, and project cargo? |
| Compliance & Sustainability | What regulatory, dangerous-goods, customs, emissions, and governance data must be reported? |
| Visibility & Events | What happened, where, when, to which cargo/equipment/asset, and why? |

This report recommends **24 data domains**. They are intentionally complementary: each domain has one clear master scope and explicit interfaces to adjacent domains.

---

## 2. CLdN Business Capabilities Reflected in the Domains

Public CLdN information indicates that the model should cover:

- RoRo shipping, vessel stevedoring, terminal handling, and vehicle storage / handling.
- Multimodal transport using ships, trucks, trains, and European network services.
- Automotive logistics, including terminal handling, storage, PDI, wash, vehicle enhancement, modification, technical services, and body repair.
- Terminal services across ports, including RoRo/LoLo cargo handling, stevedoring, high-and-heavy handling, and intermodal rail/barge handling.
- Project cargo / high-and-heavy services, including inland and short-sea shipping, terminal handling, loading/unloading, and storage.
- Energy, fuel, CO₂, rail energy, and carbon reporting / surcharge data.
- Dangerous-goods restrictions and operational customer documents.

Sources are listed at the end of the report.

---

## 3. Recommended Non-Overlapping Data Domains

### 3.1 Party, Role & Organisation Domain

**Owns:** legal entities, customers, suppliers, carriers, terminal operators, agents, authorities, internal business units, contact roles, and organizational hierarchy.

**Does not own:** contracts, bookings, invoices, operational cargo events, or terminal moves.

**Key entities:**

- Party
- Organisation
- Legal Entity
- Customer
- Supplier
- Carrier
- Terminal Operator
- Port Authority
- Customs Authority
- Contact
- Role Assignment

**Primary standards alignment:** UN/CEFACT CCL, BSP-RDM.

**Interfaces:** used by Booking, Contract, Terminal Operations, Customs, and Compliance domains.

---

### 3.2 Customer, Contract & Commercial Agreement Domain

**Owns:** commercial relationships, service agreements, trade terms, customer commitments, route/service coverage in agreements, and pricing conditions at contract level.

**Does not own:** monthly surcharge calculation, invoice posting, operational booking execution, or terminal tariff event capture.

**Key entities:**

- Customer Agreement
- Service Contract
- Commercial Term
- Rate Agreement
- Incoterm / Trade Term
- Service Commitment
- Contracted Route

**Primary standards alignment:** BSP-RDM, SCRDM, UN/CEFACT CCL.

**Interfaces:** consumes Party; provides commercial context to Booking, Tariff/Surcharge, and Invoice domains.

---

### 3.3 Booking, Quote & Order Management Domain

**Owns:** booking requests, quote requests, transport orders, customer instructions, booking confirmation, and booking lifecycle state.

**Does not own:** transport execution events, invoices, vessel schedule master data, or terminal handling moves.

**Key entities:**

- Quote Request
- Booking Request
- Booking
- Transport Order
- Shipping Instruction
- Booking Confirmation
- Amendment / Cancellation

**Primary standards alignment:** DCSA Booking, BSP-RDM, SCRDM, MMT-RDM.

**Interfaces:** consumes Customer/Contract, Route/Schedule, Cargo, Equipment, and Party data; triggers Transport Movement and Document domains.

---

### 3.4 Route, Network, Schedule & Service Domain

**Owns:** service network, routes, corridors, port pairs, sailing schedules, service loops, cut-offs, voyage schedule publication, and network connectivity.

**Does not own:** actual cargo loaded, actual terminal moves, invoice charges, or customer contracts.

**Key entities:**

- Route
- Corridor
- Service Loop
- Sailing Schedule
- Vessel Schedule
- Port Call Plan
- Cut-off Time
- Transit Time
- Network Connection

**Primary standards alignment:** DCSA Operational Vessel Schedules, MMT-RDM, IMO port-call models.

**Interfaces:** provides planned network context to Booking, Maritime Operations, Terminal Operations, Track & Trace, and Carbon domains.

---

### 3.5 Vessel, Fleet & Maritime Operations Domain

**Owns:** vessels, vessel characteristics, voyage operations, sea legs, port calls, berthing plan references, marine operational status, and fleet operational capabilities.

**Does not own:** terminal yard moves, customer booking, cargo commercial terms, or emissions accounting formulas.

**Key entities:**

- Vessel
- Fleet Asset
- Voyage
- Sea Leg
- Port Call
- Berth Stay
- Arrival / Departure
- Vessel Capacity
- Vessel Operational Status

**Primary standards alignment:** DCSA, IMO Compendium / FAL, MMT-RDM.

**Interfaces:** consumes Route/Schedule; provides vessel/voyage context to Cargo Movement, Terminal Operations, Events, and Sustainability.

---

### 3.6 Consignment, Shipment & Transport Movement Domain

**Owns:** the transport semantic backbone: consignments, shipments, legs, transport movements, multimodal chains, handovers, transport status, and movement decomposition.

**Does not own:** terminal micro-events, commercial pricing, customs declaration content, or specialized vehicle service details.

**Key entities:**

- Consignment
- Shipment
- Transport Movement
- Transport Leg
- Multimodal Chain
- Place of Loading
- Place of Discharge
- Handover
- Transport Status

**Primary standards alignment:** MMT-RDM, BSP-RDM.

**Interfaces:** central hub between Booking, Cargo, Equipment, Route/Schedule, Terminal Operations, Documents, Customs, and Events.

---

### 3.7 Cargo, Goods & Cargo Unit Domain

**Owns:** cargo description, goods classification, cargo units, packages, weights, dimensions, commodity attributes, handling requirements, and cargo-level master/transaction data.

**Does not own:** transport equipment master data, terminal move execution, automotive service lifecycle, or dangerous-goods regulatory rules.

**Key entities:**

- Cargo Item
- Goods Item
- Package
- Cargo Unit
- Weight
- Dimension
- Commodity
- Handling Requirement
- Temperature Requirement

**Primary standards alignment:** MMT-RDM, UN/CEFACT CCL, WCO where classification/regulatory cargo data is needed.

**Interfaces:** used by Booking, Shipment, Equipment, RoRo, LoLo/Container, Dangerous Goods, and Customs domains.

---

### 3.8 Cargo Equipment & Fleet Equipment Domain

**Owns:** transport equipment and equipment master data such as trailers, containers, tank containers, reefer units, chassis, and other load-carrying equipment.

**Does not own:** vessel fleet, terminal cranes/handling equipment, cargo contents, or operational moves.

**Key entities:**

- Trailer
- Container
- Tank Container
- Reefer Unit
- Chassis
- Swap Body
- Equipment Identifier
- Equipment Owner
- Equipment Status
- Equipment Capability

**Primary standards alignment:** MMT-RDM, DCSA for container equipment, ISO container identifiers where applicable.

**Interfaces:** used by Cargo, Booking, Shipment, Terminal Operations, Events, and Maintenance/Inspection.

---

### 3.9 RoRo Operations Domain

**Owns:** RoRo-specific cargo and operational concepts: trailers, self-drive units, rolling machinery, accompanied/unaccompanied units, lane-metre planning, RoRo loading/discharge context, and RoRo cargo readiness.

**Does not own:** generic cargo master data, vessel master data, terminal yard moves, or commercial charges.

**Key entities:**

- RoRo Unit
- Trailer Unit
- Self-Drive Unit
- Rolling Cargo
- Lane Metre
- RoRo Load Plan Reference
- RoRo Cargo Readiness
- Accompanied / Unaccompanied Indicator

**Primary standards alignment:** MMT-RDM, DCSA where applicable, CLdN-specific RoRo extension.

**Interfaces:** specializes Cargo and Equipment; connects to Vessel Operations and Terminal Operations.

---

### 3.10 LoLo / Container Operations Domain

**Owns:** containerized lift-on/lift-off operational concepts, container journey context, container booking references, load/discharge plans at container level, and container operational statuses.

**Does not own:** terminal crane execution detail, generic cargo description, vessel schedule, or invoice charging.

**Key entities:**

- Container Shipment
- Container Journey
- Container Load Plan Reference
- Load-on / Load-off Instruction
- Container Operational Status
- Empty / Full Indicator
- Seal Reference

**Primary standards alignment:** DCSA, MMT-RDM, TIC 4.0 for terminal handling interface.

**Interfaces:** specializes Cargo Equipment and Transport Movement; consumes Terminal Operations events.

---

### 3.11 Terminal, Yard, Berth & Gate Operations Domain

**Owns:** terminal infrastructure, yard areas, gates, berths, storage zones, quay/yard resources, gate processes, yard position, and operational terminal state.

**Does not own:** customer contracts, route network, vessel master data, cargo semantic description, or customs declaration content.

**Key entities:**

- Terminal
- Berth
- Yard Area
- Storage Zone
- Gate
- Yard Position
- Rail Head
- Barge Connection
- Terminal Resource
- Terminal Visit

**Primary standards alignment:** TIC 4.0, MMT-RDM, DCSA terminal interface concepts.

**Interfaces:** consumes Vessel, Cargo, Equipment, Booking, and Shipment data; emits operational events to Track & Trace.

---

### 3.12 Stevedoring, Load/Discharge & Handling Moves Domain

**Owns:** stevedoring execution, vessel load/discharge moves, lift events, cargo handling moves, operational move instructions, and move completion data.

**Does not own:** terminal master layout, cargo master semantics, vessel schedule, or customer commercial relationship.

**Key entities:**

- Stevedoring Operation
- Load Move
- Discharge Move
- Lift Move
- Handling Instruction
- Move Sequence
- Move Completion
- Exception During Move

**Primary standards alignment:** TIC 4.0, DCSA, MMT-RDM, GS1 EPCIS for event representation.

**Interfaces:** consumes Terminal, Vessel, Cargo, Equipment, and Shipment data; emits events to Track & Trace and Exception Management.

---

### 3.13 Automotive Logistics & Vehicle Services Domain

**Owns:** vehicle-unit lifecycle and value-added automotive services such as PDI, wash, vehicle enhancement, modification, technical service, body repair, storage, and release readiness.

**Does not own:** generic RoRo trailer handling, general cargo classification, terminal yard master data, or commercial contract terms.

**Key entities:**

- Vehicle Unit
- VIN / Vehicle Identifier
- Vehicle Storage
- PDI
- Wash
- Vehicle Enhancement
- Vehicle Modification
- Technical Service
- Body Repair
- Vehicle Release Status

**Primary standards alignment:** MMT-RDM for cargo base, TIC 4.0 for terminal activity context, automotive-specific extension.

**Interfaces:** specializes Cargo; consumes Terminal/Yard data; emits service completion events and damage/exception data.

---

### 3.14 High & Heavy / Project Cargo Domain

**Owns:** oversized, heavyweight, breakbulk, high-and-heavy cargo requirements, special handling plans, lifting/stowage constraints, engineering review status, and tailored load/unload/storage plans.

**Does not own:** generic cargo attributes, vessel schedule, terminal resource master data, or invoice settlement.

**Key entities:**

- Project Cargo
- High & Heavy Cargo
- Oversized Cargo
- Breakbulk Item
- Special Handling Plan
- Lifting Requirement
- Stowage Constraint
- Engineering Approval

**Primary standards alignment:** MMT-RDM, TIC 4.0, CLdN-specific project cargo extension.

**Interfaces:** specializes Cargo; consumes Vessel, Terminal, Equipment, and Booking data; interfaces with Risk/Exception and Documents.

---

### 3.15 Intermodal Rail, Barge & Inland Execution Domain

**Owns:** inland legs, rail/barge connections, road execution, terminal-to-terminal handovers, inland carrier handover, inland route execution, and multimodal chain status outside the sea leg.

**Does not own:** maritime voyage execution, terminal yard moves, cargo master data, or customer contracts.

**Key entities:**

- Inland Leg
- Rail Leg
- Barge Leg
- Road Leg
- Inland Carrier
- Inland Terminal
- Intermodal Connection
- Handover Event
- Inland Execution Status

**Primary standards alignment:** MMT-RDM, eFTI, Open Trip Model for road, rail standards where required.

**Interfaces:** extends Transport Movement; consumes Booking, Cargo, Equipment, Route, and Terminal data.

---

### 3.16 Track & Trace / Operational Events Domain

**Owns:** normalized event model across cargo, equipment, vessel, terminal, gate, rail/barge, road, and handover events. This is the cross-domain event ledger, not the owner of operational master data.

**Does not own:** master definitions of cargo, vessel, equipment, terminal, route, or customer.

**Key entities:**

- Operational Event
- Object Event
- Aggregation Event
- Transaction Event
- Event Time
- Event Location
- Event Source
- Business Step
- Disposition
- Exception Event

**Primary standards alignment:** GS1 EPCIS / CBV, DCSA Track & Trace, TIC 4.0 event concepts, MMT-RDM.

**Interfaces:** consumes identifiers from almost every operational domain; publishes visibility data to customers, operations, carbon, and exception management.

---

### 3.17 Dangerous Goods & Cargo Restrictions Domain

**Owns:** dangerous-goods restrictions, hazardous cargo attributes, acceptance rules, route/terminal/vessel restrictions, regulatory classes, and approval status.

**Does not own:** all cargo classification, customs declarations, booking lifecycle, or incident response events.

**Key entities:**

- Dangerous Goods Item
- Hazard Class
- UN Number
- IMDG Classification
- Restriction Rule
- Acceptance Decision
- Route Restriction
- Terminal Restriction
- Vessel Restriction

**Primary standards alignment:** IMDG/IMO, MMT-RDM, WCO where customs/regulatory treatment is involved.

**Interfaces:** consumes Cargo, Booking, Route, Vessel, and Terminal data; provides constraints to Booking and Operations.

---

### 3.18 Customs, Border & Regulatory Declarations Domain

**Owns:** customs and border data, regulatory declarations, entry/exit summary references, filings, authority messages, and regulatory status.

**Does not own:** transport execution, cargo operations, commercial contracts, or dangerous-goods acceptance rules except where referenced in declarations.

**Key entities:**

- Customs Declaration
- Border Filing
- Regulatory Declaration
- Authority Message
- Declaration Status
- Inspection Reference
- Import / Export / Transit Reference
- ICS2 Reference

**Primary standards alignment:** WCO Data Model, UN/CEFACT Cross-Border Management RDM, eFTI, IMO/FAL where maritime reporting is involved.

**Interfaces:** consumes Party, Cargo, Shipment, Document, Vessel, and Route data; emits compliance status to Booking and Operations.

---

### 3.19 Documents, Messages & Evidence Domain

**Owns:** business and transport documents, message metadata, document versions, evidence, attachments, document lifecycle, and document-to-shipment relationships.

**Does not own:** the semantic truth of cargo, bookings, customs, or invoice data; it references domain data and records documentary representation.

**Key entities:**

- Transport Document
- Bill of Lading
- Waybill
- Consignment Note
- Shipping Instruction Document
- Dangerous Goods Document
- Terminal Document
- Evidence Attachment
- Document Version

**Primary standards alignment:** BSP-RDM, MMT-RDM, DCSA eBL/documentation, UN/CEFACT document standards, UBL where used.

**Interfaces:** consumes data from Booking, Cargo, Shipment, Customs, Commercial, and Terminal domains.

---

### 3.20 Tariff, Surcharge, Invoice & Settlement Domain

**Owns:** tariff structures, surcharges, monthly energy/fuel/CO₂/rail surcharge data, charge calculation, invoices, credit notes, settlement, and billing status.

**Does not own:** customer contract master data, booking lifecycle, emissions accounting methodology, or operational events.

**Key entities:**

- Tariff
- Surcharge
- Energy Surcharge
- Fuel Component
- CO₂ Component
- Rail Energy Surcharge
- Charge Line
- Invoice
- Credit Note
- Settlement Status

**Primary standards alignment:** BSP-RDM, UN/CEFACT CII, SCRDM.

**Interfaces:** consumes Customer/Contract, Booking, Route, Cargo, Equipment, and Sustainability data.

---

### 3.21 Claims, Damage, Exception & Incident Management Domain

**Owns:** cargo/equipment/vehicle damage records, operational exceptions, claims, incident reports, root-cause classification, liability references, and resolution status.

**Does not own:** routine operational events, cargo master data, vehicle service completion, or invoice settlement.

**Key entities:**

- Damage Report
- Claim
- Exception
- Incident
- Root Cause
- Liability Party
- Resolution Action
- Claim Status
- Evidence Reference

**Primary standards alignment:** GS1 EPCIS for exception events, MMT-RDM for transport context, internal claims model.

**Interfaces:** consumes Track & Trace, Cargo, Equipment, Automotive, Terminal, and Document data.

---

### 3.22 Sustainability, Carbon, Energy & ESG Domain

**Owns:** carbon intensity, emissions factors, CO₂/tonne-km metrics, energy consumption, modal-shift metrics, Scope 1/2/3 reporting data, ESG indicators, and sustainability reporting outputs.

**Does not own:** commercial surcharge pricing logic, operational event capture, or vessel/terminal master data.

**Key entities:**

- Carbon Emission
- Emission Factor
- CO₂ Intensity
- Tonne-Kilometre
- Energy Consumption
- Scope 1 / 2 / 3 Emission
- Modal Shift Metric
- Sustainability Report Metric

**Primary standards alignment:** ISO 14083, GLEC Framework, EU MRV/ETS where applicable, IMO DCS where applicable.

**Interfaces:** consumes Route, Vessel, Transport Movement, Terminal, Fuel/Energy, and Event data; provides metrics to Tariff/Surcharge and Reporting.

---

### 3.23 Compliance, Governance, Policy & Legal Domain

**Owns:** regulatory/compliance policies, corporate governance, privacy, terms and conditions, audit evidence, whistleblowing, modern slavery / CSR-related governance references, and legal document metadata.

**Does not own:** customs filings, operational cargo restrictions, commercial contract details, or invoice settlement.

**Key entities:**

- Policy
- Legal Term
- Compliance Obligation
- Audit Evidence
- Privacy Notice
- Governance Control
- Regulatory Requirement
- Compliance Status

**Primary standards alignment:** BSP compliance concepts, legal/policy metadata standards, internal governance model.

**Interfaces:** provides governance constraints to Documents, Customer Portal, Party, and Regulatory domains.

---

### 3.24 Master Data, Code Lists & Reference Data Domain

**Owns:** shared identifiers, code lists, location codes, port codes, equipment type codes, cargo type codes, status codes, unit-of-measure codes, currency codes, and ontology reference mappings.

**Does not own:** domain-specific transaction records or operational events.

**Key entities:**

- Code List
- Reference Code
- Unit of Measure
- Currency
- Country
- Location Code
- Port Code
- Equipment Type Code
- Status Code
- Ontology Mapping

**Primary standards alignment:** UN/CEFACT CCL, UN/LOCODE, UNECE recommendations, ISO code lists, DCSA code lists, GS1 code lists where relevant.

**Interfaces:** used by all domains.

---

## 4. Domains Deliberately Kept Separate

The following separations reduce overlap and improve ownership clarity.

| Potential overlap | Recommended separation |
|---|---|
| Cargo vs Equipment | Cargo is what is transported. Equipment is what carries it. A trailer/container may be equipment; the goods or vehicle inside/on it are cargo. |
| RoRo vs Terminal Operations | RoRo owns rolling-cargo concepts and lane/boarding logic. Terminal Operations owns yard, gate, berth, and storage infrastructure. |
| Automotive vs RoRo | Automotive owns vehicle lifecycle and value-added services. RoRo owns rolling transport handling. A vehicle can be both cargo in RoRo and a vehicle unit in Automotive. |
| LoLo/Container vs Terminal Handling | LoLo owns container journey/status semantics. Terminal Handling owns physical lift/load/discharge execution. |
| Schedule vs Vessel Operations | Schedule owns planned services and published times. Vessel Operations owns actual voyage/port-call execution. |
| Track & Trace vs Operational Domains | Track & Trace normalizes events. It does not own the master data or detailed execution rules of the source domain. |
| Sustainability vs Surcharges | Sustainability owns emissions and energy metrics. Tariff/Surcharge owns commercial application of fuel/CO₂/energy charges. |
| Customs vs Dangerous Goods | Customs owns declarations and authority interactions. Dangerous Goods owns acceptance rules and hazardous cargo restrictions. |
| Documents vs Domain Data | Documents store documentary representation and evidence. Domain data remains the source of semantic truth. |

---

## 5. Recommended Ontology / Standards Alignment

| Ontology layer | Recommended standards / models | Role |
|---|---|---|
| Enterprise semantic core | UN/CEFACT CCL, BSP-RDM | Party, document, commercial, supply-chain backbone |
| Commercial supply chain | SCRDM, CII | Contracts, orders, invoices, settlement |
| Multimodal logistics | MMT-RDM | Consignment, shipment, transport movement, cargo, equipment |
| Ocean carrier | DCSA | Booking, schedules, bill of lading, track & trace, container operations |
| Terminal operations | TIC 4.0 | Terminal resources, equipment, yard, moves, operational terminal events |
| Maritime reporting | IMO Compendium / FAL, IMDG | Port-call, maritime authority reporting, dangerous goods |
| Visibility events | GS1 EPCIS / CBV | Cross-domain event model |
| Customs / freight compliance | WCO Data Model, eFTI | Customs, border, regulatory freight information |
| Sustainability | ISO 14083, GLEC, EU MRV/ETS, IMO DCS | Emissions, energy, carbon intensity, reporting |

---

## 6. Suggested Domain Package Structure

```text
/core
  party-role-organisation.md
  master-reference-data.md
  customer-contract-commercial.md

/commercial
  booking-quote-order.md
  tariff-surcharge-invoice-settlement.md
  documents-messages-evidence.md

/transport
  consignment-shipment-transport-movement.md
  cargo-goods-cargo-unit.md
  cargo-equipment.md
  route-network-schedule-service.md
  intermodal-rail-barge-inland.md

/maritime
  vessel-fleet-maritime-operations.md
  roro-operations.md
  lolo-container-operations.md

/terminal
  terminal-yard-berth-gate.md
  stevedoring-load-discharge-handling.md
  automotive-logistics-vehicle-services.md
  high-heavy-project-cargo.md

/visibility
  track-trace-operational-events.md
  claims-damage-exception-incident.md

/compliance
  dangerous-goods-cargo-restrictions.md
  customs-border-regulatory-declarations.md
  compliance-governance-policy-legal.md
  sustainability-carbon-energy-esg.md
```

---

## 7. Priority Implementation Roadmap

### Phase 1 — Foundation domains

1. Party, Role & Organisation
2. Master Data, Code Lists & Reference Data
3. Consignment, Shipment & Transport Movement
4. Cargo, Goods & Cargo Unit
5. Cargo Equipment & Fleet Equipment
6. Route, Network, Schedule & Service

### Phase 2 — CLdN operational differentiation

7. RoRo Operations
8. LoLo / Container Operations
9. Terminal, Yard, Berth & Gate Operations
10. Stevedoring, Load/Discharge & Handling Moves
11. Automotive Logistics & Vehicle Services
12. High & Heavy / Project Cargo
13. Intermodal Rail, Barge & Inland Execution

### Phase 3 — Customer, compliance, and visibility

14. Booking, Quote & Order Management
15. Documents, Messages & Evidence
16. Track & Trace / Operational Events
17. Dangerous Goods & Cargo Restrictions
18. Customs, Border & Regulatory Declarations
19. Tariff, Surcharge, Invoice & Settlement
20. Sustainability, Carbon, Energy & ESG

### Phase 4 — Governance and exception maturity

21. Claims, Damage, Exception & Incident Management
22. Compliance, Governance, Policy & Legal
23. Advanced customer portal / API product domains if required
24. Analytics and data product domains if required

---

## 8. Final Recommended Domain List

The final recommended CLdN domain set is:

1. Party, Role & Organisation
2. Customer, Contract & Commercial Agreement
3. Booking, Quote & Order Management
4. Route, Network, Schedule & Service
5. Vessel, Fleet & Maritime Operations
6. Consignment, Shipment & Transport Movement
7. Cargo, Goods & Cargo Unit
8. Cargo Equipment & Fleet Equipment
9. RoRo Operations
10. LoLo / Container Operations
11. Terminal, Yard, Berth & Gate Operations
12. Stevedoring, Load/Discharge & Handling Moves
13. Automotive Logistics & Vehicle Services
14. High & Heavy / Project Cargo
15. Intermodal Rail, Barge & Inland Execution
16. Track & Trace / Operational Events
17. Dangerous Goods & Cargo Restrictions
18. Customs, Border & Regulatory Declarations
19. Documents, Messages & Evidence
20. Tariff, Surcharge, Invoice & Settlement
21. Claims, Damage, Exception & Incident Management
22. Sustainability, Carbon, Energy & ESG
23. Compliance, Governance, Policy & Legal
24. Master Data, Code Lists & Reference Data

---

## 9. Source Notes

The recommendations are based on CLdN’s public service descriptions and operational information, including:

- CLdN home page and solution descriptions: https://www.cldn.com/en
- CLdN solutions overview: https://www.cldn.com/en/solutions
- CLdN terminal services: https://www.cldn.com/en/solutions/terminal-services
- CLdN automotive logistics: https://www.cldn.com/en/solutions/automotive-logistics
- CLdN project cargo / high & heavy: https://www.cldn.com/en/solutions/project-cargo
- CLdN terminals information: https://www.cldn.com/en/our-company/our-terminals
- CLdN customer operational documents: https://www.cldn.com/en/customers/downloads
- CLdN cargo surcharges: https://www.cldn.com/en/baf-and-fuel/cargo
- CLdN energy surcharges: https://www.cldn.com/en/baf-and-fuel/energy-surcharges-for-roro-shipping
- CLdN ship CO₂ surcharge: https://www.cldn.com/en/baf-and-fuel/ship-co2-surcharge
- CLdN 2025 carbon report news: https://www.cldn.com/en/news/cldn-published-its-2025-carbon-report
- CLdN 2024 fleet emissions news: https://www.cldn.com/en/news/cldn-continues-offer-customers-best-short-sea-co2-efficiency

---

## 10. Summary

The recommended CLdN data-domain model should not be a generic shipping model only. It should explicitly represent CLdN’s combined role as:

- short-sea RoRo and LoLo carrier;
- terminal and stevedoring operator;
- multimodal road/rail/barge/sea transport provider;
- automotive logistics and value-added vehicle services provider;
- project cargo / high-and-heavy logistics provider;
- sustainability and carbon-performance reporting actor.

The most important anti-overlap rule is to keep **semantic transport data**, **terminal execution data**, **specialist cargo/service data**, **commercial data**, **regulatory data**, and **event visibility data** in separate but connected domains.
