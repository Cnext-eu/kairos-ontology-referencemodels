# Client Ontology Hub — Blueprint (Financial Services)

## Overview

This blueprint provides the recommended folder structure and import guidance for
organising a Kairos client ontology hub in the financial services sector. It uses
the **FIBO** (Financial Industry Business Ontology) reference models as
foundations, with client-specific extensions layered on top.

## Design Principles

1. **Domain-driven** — Organise by business capability and data ownership, not
   by system or document type.
2. **Selective imports** — Each domain imports only the specific FIBO modules it
   needs, not the full FIBO suite.
3. **Reference + Extension** — Each domain folder combines FIBO reference model
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
│   ├── ontologies/                              ← One subfolder per data domain
│   │   ├── party/
│   │   │   └── party.ttl                        ← imports fibo:Agents, fibo:People, fibo:Parties, fibo:LegalPersons
│   │   ├── organisation/
│   │   │   └── organisation.ttl                 ← imports fibo:FormalOrganizations, fibo:Ownership, fibo:Partnerships
│   │   ├── regulatory/
│   │   │   └── regulatory.ttl                   ← imports fibo:GovernmentEntities, fibo:LegalCore, fibo:LegalCapacity
│   │   ├── financial-market-participants/
│   │   │   └── financial-market-participants.ttl ← imports fibo:FinancialServicesEntities, fibo:Markets
│   │   ├── contracts/
│   │   │   └── contracts.ttl                    ← imports fibo:Agreements, fibo:Contracts
│   │   ├── products-services/
│   │   │   └── products-services.ttl            ← imports fibo:ProductsAndServices, fibo:FinancialProducts
│   │   ├── actus/
│   │   │   └── actus.ttl                        ← imports fibo:ACTUSContractTerms, fibo:ACTUSTaxonomy
│   │   ├── instruments/
│   │   │   └── instruments.ttl                  ← imports fibo:FinancialInstruments, fibo:Debt
│   │   ├── securities/
│   │   │   └── securities.ttl                   ← imports fibo:Bonds, fibo:EquityInstruments, fibo:Funds
│   │   ├── derivatives/
│   │   │   └── derivatives.ttl                  ← imports fibo:Options, fibo:Swaps, fibo:Futures
│   │   ├── loans/
│   │   │   └── loans.ttl                        ← imports fibo:Loans, fibo:MortgageLoans
│   │   ├── market-data/
│   │   │   └── market-data.ttl                  ← imports fibo:SecurityTemporal, fibo:DebtAnalytics
│   │   ├── indicators/
│   │   │   └── indicators.ttl                   ← imports fibo:EconomicIndicators, fibo:ForeignExchange, fibo:InterestRates
│   │   ├── transactions/
│   │   │   └── transactions.ttl                 ← imports fibo:REATransactions, fibo:MarketTransactions
│   │   ├── accounting/
│   │   │   └── accounting.ttl                   ← imports fibo:CurrencyAmount, fibo:AccountingEquity, fibo:CashFlows
│   │   ├── corporate-actions/
│   │   │   └── corporate-actions.ttl            ← imports fibo:CorporateActions
│   │   ├── securities-issuance/
│   │   │   └── securities-issuance.ttl          ← imports fibo:DebtIssuance, fibo:EquitiesIPOIssuance
│   │   ├── reference-data/
│   │   │   └── reference-data.ttl               ← imports fibo:Identifiers, fibo:ClassificationSchemes, fibo:Addresses
│   │   ├── compliance/
│   │   │   └── compliance.ttl                   ← client extension (compose from regulatory + reference-data)
│   │   ├── insurance/
│   │   │   └── insurance.ttl                    ← client extension (no FIBO module — use ACORD reference)
│   │   ├── trade-finance/
│   │   │   └── trade-finance.ttl                ← client extension (use ICC UCP 600 / URDG 758 reference)
│   │   └── mdm/
│   │       └── mdm.ttl                          ← golden records, crosswalks, match/merge
│   │
│   ├── extensions/                               ← Medallion layer extensions per domain
│   │   ├── party-silver-ext.ttl                  ← SCD-2, KYC satellites, DDL hints
│   │   ├── party-gold-ext.ttl                    ← dim_customer, dim_counterparty
│   │   ├── mdm-silver-ext.ttl                    ← golden_record, crosswalk tables
│   │   └── ...
│   │
│   └── mappings/                                 ← Source → domain mappings
│       ├── <source-system>/
│       │   ├── <source>-to-<domain>.ttl
│       │   └── <source>-to-mdm.ttl
│       └── ...
│
├── integration/
│   └── sources/                                  ← Bronze vocabularies (source system schemas)
│       ├── <source-system>/
│       │   └── <source>.vocabulary.ttl
│       └── ...
│
└── output/                                       ← Generated artifacts (not committed)
    ├── ddl/                                      ← SQL DDL from silver extensions
    ├── dbt/                                      ← dbt models
    └── report/                                   ← Mapping coverage reports
```

---

## Domain Import Guidance

Each domain ontology file should import **only** the specific FIBO modules
it needs:

```turtle
# Example: model/ontologies/party/party.ttl
@prefix : <https://client.example.com/ont/party#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix fibo-agents: <https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/> .
@prefix fibo-people: <https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/> .
@prefix fibo-parties: <https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/> .

: a owl:Ontology ;
    dcterms:title "Client Party Domain" ;
    owl:imports <https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/> ,
                <https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/> ,
                <https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/> .

# --- Client-specific extensions below ---

:RetailCustomer a owl:Class ;
    rdfs:subClassOf fibo-parties:PartyInRole ;
    rdfs:label "Retail Customer" ;
    rdfs:comment "Client-specific refinement of FIBO PartyInRole for retail banking." .
```

> **Do NOT** import the full accelerator (`financial-services#`) in individual
> domain files — that pulls in everything. The accelerator is for tools that
> need the complete graph at once.

---

## Data Domain Groups

| L1 Group | L2 Domains | Primary Ownership Question |
|----------|-----------|--------------------------|
| **Party & Organisation** | party, organisation, regulatory, financial-market-participants | Who are we doing business with, and what is their structure? |
| **Agreements & Products** | contracts, products-services, actus-contract-analytics | Under what terms and for which products? |
| **Financial Instruments** | instruments, securities, derivatives, loans | What instruments are traded, held, or managed? |
| **Markets & Indicators** | market-data, indicators | What are the current prices, rates, and indicators? |
| **Transactions & Events** | transactions, accounting, corporate-actions, securities-issuance | What transactions and events have occurred? |
| **Reference & Master Data** | reference-data, compliance, mdm | What shared identifiers and golden records underpin all domains? |
| **Client Extensions** | insurance, trade-finance | What sector-specific extensions are needed? |

---

## Medallion Architecture Relationship

```
 FIBO Reference          Client Domains           Medallion Layers
 ================        ==============           ================

 ┌──────────────┐
 │ FIBO FND     │
 │  Agents      │─imports──►┌──────────────┐
 │  Parties     │           │ party.ttl    │──extends──►┌──────────────────┐
 ├──────────────┤           │ (domain ont) │            │ party-silver.ttl │
 │ FIBO BE      │─imports──►│              │            │ (SCD-2, KYC)     │
 │  LegalPersons│           └──────────────┘            └────────┬─────────┘
 └──────────────┘                  │                             │
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
| **Silver extension** | `model/extensions/<domain>-silver-ext.ttl` | Physical projection: SCD-2 tables, KYC/AML satellites, DDL annotations |
| **Gold extension** | `model/extensions/<domain>-gold-ext.ttl` | BI projection: dimension/fact tables, Power BI semantic model |
| **Mapping** | `model/mappings/<source>/<source>-to-<domain>.ttl` | Source-to-canonical field mapping |
| **Bronze vocabulary** | `integration/sources/<source>/<source>.vocabulary.ttl` | Raw source schema description |

---

## When to Extend vs. When to Import

| Situation | Action |
|-----------|--------|
| Concept exists in FIBO | `owl:imports` the module — do NOT redefine |
| Concept exists but needs extra properties | Import + add properties with your namespace as `rdfs:domain` |
| Concept doesn't exist in FIBO | Define in your domain `.ttl` as a client-specific class |
| Need a subclass of a FIBO class | Import parent + define subclass in your domain |
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

This means you can master Party, Organisation, Instrument, Counterparty —
any entity from any domain — without the MDM module importing all domains.
The link is made at instance level.

---

## Getting Started — Recommended Sequence

1. **Copy this blueprint** structure into your client project repository.
2. **Start with Party domain** — it's the most common MDM use case and touches
   almost every other domain.
3. **For each domain you activate:**
   - Create the `.ttl` with `owl:imports` of the relevant FIBO modules
     (see `data-domains.yaml` for the exact imports).
   - Add client-specific classes and properties.
   - Create a silver extension if medallion projection is needed.
   - Create source mappings as you onboard systems.
4. **Validate:** `python -m kairos_ontology validate`
5. **Project outputs:** `python -m kairos_ontology project --target silver`

### Priority order for financial services clients

```
Phase 1: party → mdm → organisation → contracts
Phase 2: instruments → securities → products-services → reference-data
Phase 3: transactions → accounting → loans → derivatives
Phase 4: market-data → indicators → corporate-actions
Phase 5: compliance → securities-issuance → actus
```

Specialist domains (insurance, trade-finance) are added based on the
client's specific operations.

---

## Reference

- Domain registry with full import mappings: [`data-domains.yaml`](data-domains.yaml)
- Financial services accelerator (full bundle): `accelerator-packs/financial-services/current/financial-services-accelerator.ttl`
- MDM implementation pattern: see `.docs/ReferenceMaterial/mdm.md`
- FIBO official documentation: <https://spec.edmcouncil.org/fibo/>
