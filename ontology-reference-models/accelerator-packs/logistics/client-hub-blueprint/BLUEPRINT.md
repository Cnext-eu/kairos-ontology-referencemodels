# Client Ontology Hub — Blueprint (Logistics)

## Overview

This blueprint provides the recommended folder structure and import guidance for
organising a Kairos client ontology hub in the logistics sector. It uses the
**Kairos Logistics Accelerator** reference models as foundations, with
client-specific extensions layered on top.

## Design Principles

1. **Domain-driven** — Organise by business capability and data ownership, not
   by system or document type.
2. **Selective imports** — Each domain imports only the reference modules it
   needs, not the full accelerator.
3. **Reference + Extension** — Each domain folder combines reference model
   imports with client-specific classes.
4. **Medallion-aware** — Bronze (source vocab), Silver (canonical), Gold (BI)
   are layers that cross-cut domains.
5. **MDM as a domain** — Master data management (golden records, crosswalks) is
   its own domain module that links to any mastered domain.

---

## Recommended Folder Structure

```
<client-project>/
│
├── model/
│   ├── ontologies/                        ← One subfolder per data domain
│   │   ├── party/
│   │   │   └── party.ttl                  ← imports bsp:party, mmt:party, imo:party + client classes
│   │   ├── commercial/
│   │   │   └── commercial.ttl             ← imports bsp:commercial + client classes
│   │   ├── booking/
│   │   │   └── booking.ttl                ← imports dcsa:booking + client classes
│   │   ├── consignment/
│   │   │   └── consignment.ttl            ← imports mmt:consignment, dcsa:shipment-journey
│   │   ├── cargo/
│   │   │   └── cargo.ttl                  ← imports mmt:cargo
│   │   ├── equipment/
│   │   │   └── equipment.ttl              ← imports mmt:equipment, dcsa:equipment
│   │   ├── route-schedule/
│   │   │   └── route-schedule.ttl         ← imports dcsa:schedule, mmt:route-network, dcsa:transport-call
│   │   ├── vessel-maritime/
│   │   │   └── vessel-maritime.ttl        ← imports imo:vessel-registry, dcsa:vessel-journey,
│   │   │                                     imo:port-call, imo:certificates-surveys,
│   │   │                                     imo:crew-seafarer, imo:environmental,
│   │   │                                     imo:maritime-security, imo:locations
│   │   ├── terminal-operations/
│   │   │   └── terminal-operations.ttl    ← imports tic:terminal-infrastructure, tic:handling,
│   │   │                                     tic:locations, tic:kpi
│   │   ├── intermodal/
│   │   │   └── intermodal.ttl             ← imports mmt:inland-transport
│   │   ├── roro/
│   │   │   └── roro.ttl                   ← client extension (backed by mmt:cargo + tic)
│   │   ├── automotive/
│   │   │   └── automotive.ttl             ← imports tic:automotive-services
│   │   ├── dangerous-goods/
│   │   │   └── dangerous-goods.ttl        ← imports imo:dangerous-goods
│   │   ├── customs/
│   │   │   └── customs.ttl                ← imports wco:customs, wco:trade-facilitation,
│   │   │                                     wco:party, wco:documents, wco:locations
│   │   ├── sustainability/
│   │   │   └── sustainability.ttl         ← imports sustainability:carbon, :energy
│   │   ├── events/
│   │   │   └── events.ttl                 ← imports dcsa:track-and-trace, tic:events, mmt:events
│   │   ├── documents/
│   │   │   └── documents.ttl              ← imports bsp:documents, dcsa:transport-documents,
│   │   │                                     mmt:documents
│   │   ├── financial/
│   │   │   └── financial.ttl              ← imports bsp:financial, dcsa:demurrage-detention,
│   │   │                                     bsp:cost-accounting, bsp:revenue-yield
│   │   ├── claims/
│   │   │   └── claims.ttl                 ← client extension (no reference model)
│   │   ├── compliance/
│   │   │   └── compliance.ttl             ← imports bsp:compliance
│   │   ├── reference-data/
│   │   │   └── reference-data.ttl         ← imports bsp:reference-data, dcsa:locations
│   │   └── mdm/
│   │       └── mdm.ttl                    ← golden records, crosswalks, match/merge
│   │
│   ├── extensions/                         ← Medallion layer extensions per domain
│   │   ├── party-silver-ext.ttl            ← SCD-2, GDPR satellites, DDL hints
│   │   ├── party-gold-ext.ttl              ← dim_customer, fact tables
│   │   ├── mdm-silver-ext.ttl              ← golden_record, crosswalk tables
│   │   └── ...
│   │
│   └── mappings/                           ← Source → domain mappings
│       ├── <source-system>/
│       │   ├── <source>-to-<domain>.ttl
│       │   └── <source>-to-mdm.ttl
│       └── ...
│
├── integration/
│   └── sources/                            ← Bronze vocabularies (source system schemas)
│       ├── <source-system>/
│       │   └── <source>.vocabulary.ttl
│       └── ...
│
└── output/                                 ← Generated artifacts (not committed)
    ├── ddl/                                ← SQL DDL from silver extensions
    ├── dbt/                                ← dbt models
    └── report/                             ← Mapping coverage reports
```

---

## Domain Import Guidance

Each domain ontology file should import **only** the specific reference modules
it needs:

```turtle
# Example: model/ontologies/party/party.ttl
@prefix : <https://client.example.com/ont/party#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix bsp-party: <https://www.kairosflow.ai/ont/bsp/party#> .
@prefix mmt-party: <https://www.kairosflow.ai/ont/mmt/party#> .

: a owl:Ontology ;
    dcterms:title "Client Party Domain" ;
    owl:imports <https://www.kairosflow.ai/ont/bsp/party#> ,
                <https://www.kairosflow.ai/ont/mmt/party#> .

# --- Client-specific extensions below ---

:FreightCustomer a owl:Class ;
    rdfs:subClassOf bsp-party:Customer ;
    rdfs:label "Freight Customer" ;
    rdfs:comment "Client-specific refinement of BSP Customer for freight operations." .
```

> **Do NOT** import the full accelerator (`logistics#`) in individual domain
> files — that pulls in everything. The accelerator is for tools that need the
> complete graph at once.

---

## Data Domain Groups

| L1 Group | L2 Domains | Primary Ownership Question |
|----------|-----------|--------------------------|
| **Party & Commercial** | party, commercial, booking, financial | Who are we doing business with, under what terms, at what price, and what does it cost us? |
| **Transport & Cargo** | consignment, cargo, equipment, route-schedule, intermodal | What is being moved, by which path and asset? |
| **Maritime & Terminal** | vessel-maritime, terminal-operations, roro, automotive | What happens on vessels, berths, gates, and yards? |
| **Compliance & Sustainability** | dangerous-goods, customs, compliance, sustainability | What must be reported or restricted? |
| **Visibility & Events** | events, claims, documents, reference-data | What happened, where, when, to what? |
| **Master Data Management** | mdm | What is the single golden-record truth? |

---

## Medallion Architecture Relationship

```
 Reference Models          Client Domains           Medallion Layers
 ================          ==============           ================

 ┌──────────┐
 │ BSP/party│──imports──►┌──────────────┐
 ├──────────┤            │ party.ttl    │──extends──►┌──────────────────┐
 │ MMT/party│──imports──►│ (domain ont) │            │ party-silver.ttl │
 └──────────┘            └──────────────┘            │ (SCD-2, DDL)     │
                                │                    └────────┬─────────┘
                                │                             │
                         owl:imports                    gold projection
                                │                             │
                                ▼                             ▼
                         ┌──────────────┐            ┌──────────────────┐
                         │ mdm.ttl      │            │ party-gold.ttl   │
                         │ (crosswalks) │            │ (dim_customer)   │
                         └──────────────┘            └──────────────────┘
```

### Layer responsibilities

| Layer | Artifact | Purpose |
|-------|----------|---------|
| **Domain ontology** | `model/ontologies/<domain>/<domain>.ttl` | Semantic truth: classes, properties, relationships |
| **Silver extension** | `model/extensions/<domain>-silver-ext.ttl` | Physical projection: SCD-2 tables, GDPR satellites, DDL annotations |
| **Gold extension** | `model/extensions/<domain>-gold-ext.ttl` | BI projection: dimension/fact tables, Power BI semantic model |
| **Mapping** | `model/mappings/<source>/<source>-to-<domain>.ttl` | Source-to-canonical field mapping |
| **Bronze vocabulary** | `integration/sources/<source>/<source>.vocabulary.ttl` | Raw source schema description |

---

## When to Extend vs. When to Import

| Situation | Action |
|-----------|--------|
| Concept exists in reference model | `owl:imports` the module — do NOT redefine |
| Concept exists but needs extra properties | Import + add properties with your namespace as `rdfs:domain` |
| Concept doesn't exist in any reference model | Define in your domain `.ttl` as a client-specific class |
| Need a subclass of a reference class | Import parent + define subclass in your domain |
| Need MDM mastering for a domain entity | `mdm.ttl` links to any domain via `mastersEntity` property |

---

## MDM Integration Pattern

The MDM domain is special — it **cross-cuts** other domains. Any domain entity
that needs master data management gets linked via:

```turtle
# model/ontologies/mdm/mdm.ttl
:GoldenRecord a owl:Class .
:Crosswalk a owl:Class .
:SourceSystem a owl:Class .

:mastersEntity a owl:ObjectProperty ;
    rdfs:domain :GoldenRecord ;
    rdfs:range owl:Thing .   # Can master any domain entity
```

This means you can master Party, Equipment, Vessel, Location — any entity from
any domain — without the MDM module importing all domains. The link is made at
instance level.

---

## Getting Started — Recommended Sequence

1. **Copy this blueprint** structure into your client project repository.
2. **Start with Party domain** — it's the most common MDM use case and touches
   almost every other domain.
3. **For each domain you activate:**
   - Create the `.ttl` with `owl:imports` of the relevant reference modules
     (see `data-domains.yaml` for the exact imports).
   - Add client-specific classes and properties.
   - Create a silver extension if medallion projection is needed.
   - Create source mappings as you onboard systems.
4. **Validate:** `python -m kairos_ontology validate`
5. **Project outputs:** `python -m kairos_ontology project --target silver`

### Priority order for logistics clients

```
Phase 1: party → mdm → commercial → booking
Phase 2: consignment → cargo → equipment → route-schedule
Phase 3: vessel-maritime → terminal-operations → events
Phase 4: customs → dangerous-goods → sustainability → documents
Phase 5: financial → claims → compliance → reference-data
```

> **Financial domain note:** The `financial` domain now covers the full operational
> finance lifecycle: charges & surcharges (BSP), demurrage & detention (DCSA),
> cost allocation & budgeting (Cost Accounting), and revenue/yield analytics
> (Revenue & Yield). Working capital metrics (DSO, DPO, cash conversion cycle)
> are recommended as **client extensions** since calculation methods are
> implementation-specific.

Specialist domains (roro, automotive, intermodal) are added based on the
client's specific operations.

---

## Overlap Resolutions

Where a class appears in multiple reference modules, `data-domains.yaml` records
which module is **canonical** via the `overlaps` field on each domain. Review
these resolutions before modeling starts to avoid duplicate imports.

**Resolution principles:**

| Principle | Application |
|---|---|
| Authority first | Use the most authoritative standard (IMO for vessels, WCO for customs, DCSA for shipping events) |
| Transport-centric | Prefer MMT over BSP for operational concepts |
| Domain ownership | Each class is owned by one domain; others reference via imports |
| No duplication | Never subclass the same concept from two parents — pick one canonical source |
| Equivalence later | Add `owl:equivalentClass` only if cross-model querying is needed |

See `data-domains.yaml` → `overlaps` entries for the full list of resolved
classes.

---

## Cross-Domain Relationships

The **Supply Chain Integration** module provides cross-standard object properties
that bridge classes from different ontology standards (e.g., linking a DCSA
Booking to an MMT Consignment, or an IMO PortCall to a TIC Terminal).

### When to use

- Within a single standard, cross-module properties already exist
  (e.g., MMT consignment → MMT equipment via `hasTransportEquipment`)
- The Supply Chain module covers relationships that **span different standards**
- Import it when your client domain needs to link entities across
  booking, transport, finance, terminal, and customs boundaries

### Import pattern

```turtle
# In your domain ontology
owl:imports <https://www.kairosflow.ai/ont/supply-chain> .

# Or import the full logistics accelerator (which includes it)
owl:imports <https://www.kairosflow.ai/ont/accelerator/logistics#> .
```

### Key bridge properties

| Property | From | To | Purpose |
|----------|------|----|---------|
| `sc:bookedConsignment` | DCSA Booking | MMT Consignment | Booking creates consignment |
| `sc:underAgreement` | DCSA Booking | BSP SalesContract | Commercial terms governing booking |
| `sc:invoicedVia` / `sc:chargesForConsignment` | MMT Consignment ↔ BSP Invoice | Bidirectional finance link |
| `sc:scheduledVia` | MMT TransportService | DCSA ServiceLoop | Transport schedule assignment |
| `sc:handledAtTerminal` | DCSA Container | TIC CargoVisit | Terminal handling of equipment |
| `sc:callsAtTerminal` | IMO PortCall | TIC Terminal | Vessel-terminal relationship |
| `sc:berthsAt` | IMO BerthStay | TIC Berth | Mooring location |
| `sc:classifiedAsDangerousGoods` | MMT CargoItem | IMO DangerousGoodsItem | DG classification |
| `sc:requiresCustomsDeclaration` | MMT Consignment | WCO CustomsDeclaration | Customs requirement |
| `sc:eventRelatesToConsignment` | DCSA Event | MMT Consignment | Event subject (consignment) |
| `sc:eventRelatesToVessel` | DCSA Event | IMO Vessel | Event subject (vessel) |
| `sc:eventRelatesToEquipment` | TIC TerminalEvent | DCSA Container | Event subject (equipment) |
| `sc:hasCIIRating` | IMO Vessel | Sustainability CIIRating | Vessel carbon intensity |
| `sc:hasEmissionReport` | IMO Vessel | Sustainability EmissionReport | Vessel emission reporting |
| `sc:hasEnergyConsumption` | MMT TransportService | Sustainability EnergyConsumption | Transport energy tracking |
| `sc:hasCarbonFootprint` | MMT Consignment | Sustainability CarbonFootprint | Consignment carbon footprint |
| `sc:hasMovementEmission` | MMT TransportMovement | Sustainability CarbonFootprint | Movement/trip-grain operational emissions |
| `sc:declaredAsGoodsItem` | MMT CargoItem | WCO GoodsItem | Customs goods declaration |
| `sc:correspondsToBillOfLading` | DCSA TransportDocument | BSP BillOfLading | Document correspondence |

The full registry is in `data-domains.yaml` → `cross_domain_relationships`.

---

## Reference

- Domain registry with full import mappings: [`data-domains.yaml`](data-domains.yaml)
- Logistics accelerator (full bundle): `accelerator-packs/logistics/current/logistics-accelerator.ttl`
- MDM implementation pattern: see `.docs/ReferenceMaterial/mdm.md`
- Data domain recommendations: see `.docs/ReferenceMaterial/cldn-data-domain-recommendations.md`
