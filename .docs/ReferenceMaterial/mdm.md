# MDM Implementation Pattern — Phased Coexistence

> ## ⚠️ Pre-v5 historical design — not current guidance
>
> This document was written against **Kairos toolkit v4** and describes authoring surfaces that
> **no longer exist**. Do not follow its implementation steps.
>
> | It says | v5 reality |
> |---|---|
> | `model/extensions/<domain>-silver-ext.ttl` | Retired. Physical materialization policy lives in `integration/bindings/<source>-to-<domain>.binding.yaml`. |
> | `model/mappings/<source>/<source>-to-<domain>.ttl` | Retired. Same closed `EntityBinding` document. |
> | `kairos project --target silver` | Retired — `RETIRED_COMPILER_TARGETS = ("dbt", "silver")`. Use `kairos-ontology compile <domain> --check`. |
> | `kairos-ontology-medallion-silver` skill | Retired redirect: *"Silver Design Is Folded into EntityBinding."* |
>
> For current MDM guidance use the **`kairos-design-mdm`** skill and the toolkit's own `mdm/`
> package (`model`, `validation`, `vocabulary`, `profile_projector`). MDM policy in v5 is an
> optional, runtime-neutral consumer of the immutable `CompilePlan`; `EntityBinding` remains
> the sole source-to-canonical execution authority.
>
> **Why it is kept:** the *reasoning* — phased coexistence, golden-record survivorship, the
> crosswalk model, GDPR satellites — is still sound and was expensive to work out. Only the
> mechanics are obsolete. `.docs/` is not shipped in the release tarball, so this reaches no
> consumer; it is an internal design record.

## Party Domain Example (Customers / Clients)

---

## 1. Chosen MDM Pattern: Phased Coexistence

This pattern describes a **phased coexistence** MDM strategy aligned with
Gartner's MDM implementation styles. The approach balances immediate data
warehouse trust requirements with the realities of a federated operating model
where multiple operational platforms serve regional operations.

| Phase | Gartner Pattern | Goal |
|-------|----------------|------|
| **Phase 1** | Consolidation | Golden records for data warehouse Gold layer, reporting, and analytics |
| **Phase 2** | Coexistence | Bi-directional sync of governed master attributes back to sources |
| **Future** | Selective Centralization | Centrally authored reference data (location codes, KPI definitions) |

> **Key principle:** Phase 1 does _not_ require source systems to change how
> they create or maintain master data. MDM operates as the authoritative
> source for the data warehouse — not yet for the operational systems themselves.

---

## 2. How the Ontology Supports Each Phase

The `mdm.ttl` ontology provides the semantic backbone for all three phases.
Its classes and properties are designed so that Phase 1 deliverables remain
valid as the hub evolves toward coexistence.

### 2.1 Core Ontology Classes — Phase Mapping

```
┌─────────────────────────────────────────────────────────────────────┐
│                        mdm.ttl classes                              │
├──────────────────┬──────────┬──────────┬────────────────────────────┤
│ Class            │ Phase 1  │ Phase 2  │ Future                     │
├──────────────────┼──────────┼──────────┼────────────────────────────┤
│ GoldenRecord     │ ✅ Core  │ ✅ Core  │ ✅ Core                    │
│ Crosswalk        │ ✅ Core  │ ✅ Core  │ ✅ Core                    │
│ SourceSystem     │ ✅ Core  │ ✅ Core  │ ✅ Core                    │
│ MatchGroup       │ ✅ Core  │ ✅       │ ✅                         │
│ MergeEvent       │ ✅ Audit │ ✅ Audit │ ✅ Audit                   │
│ CrosswalkStatus  │ ✅ Enum  │ ✅ Enum  │ ✅ Enum                    │
│ MatchDecision    │ ✅ Enum  │ ✅ Enum  │ ✅ Enum                    │
└──────────────────┴──────────┴──────────┴────────────────────────────┘
```

### 2.2 GoldenRecord → Party Relationship

The `mastersParty` object property links a `GoldenRecord` to the canonical
`party:Party` it represents. Because `party:Customer` is a subclass of
`party:Organization → party:Party`, the golden record naturally masters any
party subtype.

```
 ┌───────────────┐   mastersParty   ┌──────────────┐
 │ GoldenRecord  │ ───────────────► │ party:Party  │
 └──────┬────────┘                  └──────┬───────┘
        │                                  │
        │ hasCrosswalk                     │ rdfs:subClassOf
        ▼                                  ▼
 ┌───────────────┐              ┌──────────────────┐
 │   Crosswalk   │              │ party:Organization│
 └──────┬────────┘              └──────┬───────────┘
        │                              │ rdfs:subClassOf
        │ fromSourceSystem             ▼
        ▼                       ┌──────────────────┐
 ┌───────────────┐              │ party:Customer   │
 │ SourceSystem  │              └──────────────────┘
 └───────────────┘
```

### 2.3 Crosswalk Pattern — Identity Resolution

The crosswalk is the central MDM construct. It answers:
_"Which record in which source system corresponds to which golden record?"_

For the **party/client** domain, a single customer like _"Acme Corp"_ may
appear in:

| Source System | Source Entity | Source Record ID | Role |
|---------------|---------------|-----------------|------|
| TMS Instance A (Europe) | `Customer` | `CUST-00123` | Customer, Shipper |
| TMS Instance B (Asia) | `Customer` | `CUST-00456` | Customer |
| ERP System | `BusinessPartner` | `BP_ID = "C-00847"` | Client |
| Legacy System | `Address` | `ADR_42091` | Customer |

The MDM hub creates **one golden record** and **four crosswalks**:

```
GoldenRecord (goldenRecordId = "GR-PARTY-00001")
  │  masteringDomain = "Client"
  │  mastersParty → party:Customer (the canonical Party instance)
  │
  ├── Crosswalk (sourceRecordId = "CUST-00123")
  │     fromSourceSystem → SourceSystem (sourceSystemCode = "TMS-A-EU")
  │     sourceEntityType = "Customer"
  │     hasCrosswalkStatus → statusActive
  │
  ├── Crosswalk (sourceRecordId = "CUST-00456")
  │     fromSourceSystem → SourceSystem (sourceSystemCode = "TMS-B-ASIA")
  │     sourceEntityType = "Customer"
  │     hasCrosswalkStatus → statusActive
  │
  ├── Crosswalk (sourceRecordId = "C-00847")
  │     fromSourceSystem → SourceSystem (sourceSystemCode = "ERP")
  │     sourceEntityType = "BusinessPartner"
  │     hasCrosswalkStatus → statusActive
  │
  └── Crosswalk (sourceRecordId = "ADR_42091")
        fromSourceSystem → SourceSystem (sourceSystemCode = "LEGACY")
        sourceEntityType = "Address"
        hasCrosswalkStatus → statusActive
```

### 2.4 Survivorship — Which Source Wins?

The `SourceSystem` class carries `survivorshipPriority` (lower = higher
priority) and `isTrustedSource`. During golden-record creation, when multiple
sources provide the same attribute (e.g., `partyName`), the value from the
highest-priority trusted source wins.

Example configuration:

| Source System | `survivorshipPriority` | `isTrustedSource` | Rationale |
|---------------|----------------------|-------------------|-----------|
| TMS Primary | 1 | `true` | Most complete party data, global standard |
| ERP | 2 | `true` | Reliable but less frequently updated |
| Legacy System | 3 | `true` | Regional coverage, less global |
| Manual MDM entry | 0 | `true` | Data steward override — always wins |

### 2.5 Match/Merge Lifecycle

The `MatchGroup` and `MergeEvent` classes support the full duplicate
detection and resolution workflow:

```
 Source records ingested
        │
        ▼
 ┌──────────────┐   matchScore > 0.9   ┌──────────────┐
 │ Match Engine  │ ──────────────────►  │ MatchGroup   │
 └──────────────┘                       │ (Auto-Merge) │
        │                               └──────┬───────┘
        │ matchScore 0.7–0.9                   │
        ▼                                      │
 ┌──────────────┐                              │
 │ MatchGroup   │ ──► Steward UI ──►           │
 │ (Manual      │     Confirm/Reject           │
 │  Review)     │                              │
 └──────┬───────┘                              │
        │                                      │
        ▼                                      ▼
 ┌──────────────┐                     ┌──────────────┐
 │ MergeEvent   │ ◄───────────────────│ MergeEvent   │
 │ (mergedFrom, │                     │ (auto)       │
 │  mergedInto) │                     └──────────────┘
 └──────────────┘
        │
        ▼
  Crosswalks reassigned
  (statusMerged → statusActive on survivor)
```

---

## 3. Phase 1 Implementation — Consolidation for Data Warehouse

### 3.1 What Phase 1 Delivers

| Deliverable | Description |
|-------------|-------------|
| **Golden records for Clients** | One mastered `party:Customer` per real-world client, consolidated from multiple source systems |
| **Crosswalk registry** | Every source-system-native customer ID linked to its golden record ID |
| **Data warehouse Gold integration** | Gold-layer `dim_customer` built from golden records instead of per-source silver tables |
| **Data quality rules** | Standardization (name normalization, address cleansing, country code validation) |
| **Match/merge engine** | Automated duplicate detection with steward review for uncertain matches |
| **Steward UI** | Review match candidates, approve/reject golden records, manage merge/split, audit trail |

### 3.2 Ontology Artifacts Required

The table below lists every artifact needed to make Phase 1 operational for
the party/client domain, mapped to the Kairos toolkit workflow.

#### 3.2.1 Already Done ✅

| Artifact | Location | Status |
|----------|----------|--------|
| Party domain ontology | `model/ontologies/party/party.ttl` | ✅ Complete — classes, roles, contacts, addresses |
| MDM domain ontology | `model/ontologies/mdm/mdm.ttl` | ✅ Complete — golden record, crosswalk, source system, match/merge |
| Party silver extension | `model/extensions/party-silver-ext.ttl` | ✅ Complete — SCD Type 2, GDPR satellites, discriminator column |

#### 3.2.2 To Be Created 🔲

| # | Artifact | Location | Purpose | Kairos Skill |
|---|----------|----------|---------|-------------|
| 1 | **MDM silver extension** | `model/extensions/mdm-silver-ext.ttl` | DDL + dbt for `silver_mdm.golden_record`, `silver_mdm.crosswalk`, `silver_mdm.source_system`, `silver_mdm.match_group`, `silver_mdm.merge_event` tables | `kairos-ontology-medallion-silver` |
| 2 | **Source system bronze vocabularies** | `integration/sources/<source>/<source>.vocabulary.ttl` | Describe source system table structures | `kairos-ontology-medallion-source` |
| 3 | **Source → Party mappings** | `model/mappings/<source>/<source>-to-party.ttl` | Map source party fields to `party:` ontology | `kairos-ontology-medallion-silver` |
| 4 | **Source → MDM mappings** | `model/mappings/<source>/<source>-to-mdm.ttl` | Map source record IDs → `mdm:Crosswalk.sourceRecordId` | `kairos-ontology-medallion-silver` |
| 5 | **MDM gold extension** | `model/extensions/mdm-gold-ext.ttl` | Gold-layer `dim_customer_master` and `fact_crosswalk` for BI | `kairos-ontology-medallion-gold` |
| 6 | **Mapping report** | `output/report/` | HTML coverage reports for MDM mappings per source | `kairos-ontology-mapping-report` |

### 3.3 Data Flow — Phase 1 (Consolidation)

```
 ┌────────────┐    ┌────────────┐    ┌────────────┐
 │  TMS A     │    │  TMS B     │    │    ERP     │
 │ (Europe)   │    │  (Asia)    │    │            │
 └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
       │                 │                 │
       ▼                 ▼                 ▼
 ┌─────────────────────────────────────────────────┐
 │              Bronze Layer                        │
 │  bronze_tms_a.customer                          │
 │  bronze_tms_b.customer                          │
 │  bronze_erp.business_partner                    │
 └─────────────────────┬───────────────────────────┘
                       │  dbt bronze-to-silver models
                       ▼
 ┌─────────────────────────────────────────────────┐
 │             Silver Layer                         │
 │  silver_party.party        (SCD-2, canonical)   │
 │  silver_party.address      (GDPR satellite)     │
 │  silver_party.contact_details (GDPR satellite)  │
 │  silver_mdm.golden_record  (mastered entity)    │
 │  silver_mdm.crosswalk      (source ↔ golden)    │
 │  silver_mdm.source_system  (system registry)    │
 │  silver_mdm.match_group    (duplicate clusters) │
 │  silver_mdm.merge_event    (audit trail)        │
 └─────────────────────┬───────────────────────────┘
                       │  gold projection
                       ▼
 ┌─────────────────────────────────────────────────┐
 │             Gold Layer                           │
 │  gold_party.dim_customer_master                 │
 │     ← built from golden_record + party          │
 │  gold_mdm.fact_crosswalk                        │
 │     ← links dim_customer_master to source IDs   │
 │  gold_mdm.dim_source_system                     │
 └─────────────────────┬───────────────────────────┘
                       │
                       ▼
 ┌─────────────────────────────────────────────────┐
 │         BI / Semantic Model                      │
 │  DirectLake on dim_customer_master               │
 │  Crosswalk slicer for source-system drill-down   │
 │  Data quality dashboard (match coverage, etc.)   │
 └──────────────────────────────────────────────────┘
```

### 3.4 Match Rules — Party/Client Example

The matching engine uses configurable rules. Typical client match rules:

| Rule Name | Match Fields | Weight | Auto-Merge Threshold |
|-----------|-------------|--------|---------------------|
| `exact-name-country` | `partyName` (exact) + `country` (exact) | 1.0 | ≥ 0.95 |
| `fuzzy-name-address` | `partyName` (Jaro-Winkler ≥ 0.85) + `city` + `country` | 0.85 | ≥ 0.90 |
| `tax-id-match` | `taxIdentifier` (exact, non-null) | 1.0 | ≥ 0.95 |
| `eori-match` | `eoriNumber` (exact, non-null) | 1.0 | ≥ 0.95 |
| `name-tax-fuzzy` | `partyName` (Jaro-Winkler ≥ 0.80) + `taxIdentifier` (exact) | 0.95 | ≥ 0.92 |

These rules map to `MatchGroup.matchRuleName` and `MatchGroup.matchScore`
in the ontology.

### 3.5 Survivorship Rules — Client Field-Level Example

| Party Attribute | Survivorship Rule | Rationale |
|----------------|-------------------|-----------|
| `partyName` | Most complete (longest non-null) | Operational systems often have abbreviated names |
| `taxIdentifier` | Highest-priority trusted source | Tax ID must be authoritative |
| `eoriNumber` | Highest-priority trusted source | EORI is a regulated identifier |
| `streetAddress` | Most recently updated | Address changes should reflect latest |
| `country` | Highest-priority trusted source | Country codes must be standardized |
| `email` | Most recently updated | Contact info changes frequently |
| `scacCode` | Designated source of truth | Carrier codes require a single authority |

---

## 4. Phase 2 — Coexistence (Bi-Directional Sync)

### 4.1 What Phase 2 Adds

Phase 2 extends the consolidation hub into a coexistence model where governed
golden-record updates flow _back_ to source systems.

| Capability | Ontology Support | Implementation |
|------------|-----------------|----------------|
| **Field-level system-of-record** | `SourceSystem.isTrustedSource` per attribute | Extend ontology with `FieldOwnership` class mapping attributes to owning systems |
| **Origin tagging** | `Crosswalk.lastVerifiedAt` + new `originSystem` property on sync events | Add `SyncEvent` class to `mdm.ttl` |
| **Loop prevention** | `originSystem` stamp on every change event | Integration middleware checks origin tag; suppresses re-publish if origin = MDM |
| **Approval workflows** | `MatchDecision.decisionConfirmed` + `MergeEvent.mergePerformedBy` | Steward UI workflow; `MergeEvent` audit trail |
| **Publish-back** | `Crosswalk` provides the target system + record ID for write-back | Integration middleware routes golden-record deltas to the correct source using crosswalk metadata |

### 4.2 Ontology Extensions Needed for Phase 2

```turtle
# Additions to mdm.ttl for Phase 2

:FieldOwnership a owl:Class ;
    rdfs:label "Field Ownership"@en ;
    rdfs:comment "Defines which source system owns (is system-of-record for)
                  a specific attribute of a mastered entity."@en .

:SyncEvent a owl:Class ;
    rdfs:label "Sync Event"@en ;
    rdfs:comment "Records a bi-directional synchronization event between
                  the MDM hub and a source system."@en .

:ownsField a owl:ObjectProperty ;
    rdfs:domain :FieldOwnership ;
    rdfs:range owl:DatatypeProperty .

:ownedBySystem a owl:ObjectProperty ;
    rdfs:domain :FieldOwnership ;
    rdfs:range :SourceSystem .

:syncDirection a owl:DatatypeProperty ;
    rdfs:domain :SyncEvent ;
    rdfs:range xsd:string .
    # Values: "source-to-hub", "hub-to-source"

:originSystem a owl:ObjectProperty ;
    rdfs:domain :SyncEvent ;
    rdfs:range :SourceSystem .
```

> **Note:** These extensions are _designed_ in Phase 1 but _not implemented_
> until Phase 2 activation. The ontology is forward-compatible.

---

## 5. Future — Selective Centralization

### 5.1 Candidates for Centralized Authoring

| Reference Data | Current Source | Centralization Rationale |
|---------------|----------------|------------------------|
| Global location codes (UN/LOCODE) | Per-system maintenance | Single authoritative source; changes infrequently |
| Shipment milestone definitions | Per-system event catalogs | Enterprise KPI consistency |
| Global KPI definitions | Spreadsheets / ad hoc | Data warehouse reporting standardization |
| Carrier hierarchy structures | TMS + manual | Global carrier management |
| Customer hierarchy / grouping | Regional spreadsheets | Enterprise client segmentation |

### 5.2 Ontology Support

The existing `mdm:SourceSystem` with `sourceSystemCode = "MDM-CENTRAL"` and
`survivorshipPriority = 0` naturally supports centralized authoring. When a
reference entity's golden record has its only crosswalk pointing to the MDM
system itself, it is effectively centrally authored.

No additional ontology classes are needed — the pattern is a configuration
of the existing model.

---

## 6. Implementation Checklist — Party/Client Phase 1

### Step-by-step using the Kairos toolkit:

```
 1. Party ontology (party.ttl)
 2. MDM ontology (mdm.ttl)
 3. Party silver extension
 4. Source system bronze vocabularies
 5. Source → Party mappings
 6. MDM silver extension
 7. Source → MDM crosswalk mappings
 8. MDM gold extension
 9. Mapping coverage reports
10. Silver DDL projection                    — kairos project --target silver
11. dbt model projection                     — kairos project --target dbt
12. Gold / BI projection                     — kairos project --target powerbi
```

### Validation at each step:

```bash
# After any ontology or extension change:
python -m kairos_ontology validate

# After creating mappings:
python -m kairos_ontology project --target report

# After silver extension:
python -m kairos_ontology project --target silver
python -m kairos_ontology project --target dbt

# After gold extension:
python -m kairos_ontology project --target powerbi
```

---

## 7. Key Assumptions & Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | MDM is modeled as a **separate domain** (`mdm.ttl`), not embedded in `party.ttl` | MDM is a cross-cutting concern; separation allows extending to Location, Carrier, and Reference Data domains without modifying `party.ttl` |
| 2 | `GoldenRecord` links to `party:Party` via `mastersParty` (not subclass) | A golden record is _about_ a party, not _a kind of_ party — composition over inheritance |
| 3 | `masteringDomain` is a string, not an enum | Allows extending to new domains (Location, Cargo) without modifying the MDM ontology |
| 4 | Crosswalks are per-source-system-instance, not per-product | Regional instances of the same product are separate source systems with separate crosswalks — reflecting federated operating models |
| 5 | Phase 2 classes (`FieldOwnership`, `SyncEvent`) are **designed but not yet modeled** | Avoids over-engineering; will be added to `mdm.ttl` when Phase 2 activates |
| 6 | Match rules and survivorship rules are **configuration, not ontology** | The ontology captures _what happened_ (match scores, decisions); the _how_ is implementation-level configuration |
| 7 | SCD Type 2 for all MDM tables | Golden records and crosswalks need full history for audit, compliance, and merge/unmerge traceability |
