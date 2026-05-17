# MDM Implementation Pattern — Phased Coexistence

## Party Domain Example (Customers / Clients)

---

## 1. Chosen MDM Pattern: Phased Coexistence

Frachtgroup adopts a **phased coexistence** MDM strategy aligned with
Gartner's MDM implementation styles. The approach balances immediate GDWH
trust requirements with the realities of a federated operating model where
multiple TMS platforms (CargoWise, Soloplan, Atlantis) serve regional
operations.

| Phase | Gartner Pattern | Goal |
|-------|----------------|------|
| **Phase 1** | Consolidation | Golden records for GDWH Gold, reporting, ODQ, MyFracht analytics |
| **Phase 2** | Coexistence | Bi-directional sync of governed master attributes back to sources |
| **Future** | Selective Centralization | Centrally authored reference data (location codes, KPI definitions) |

> **Key principle:** Phase 1 does _not_ require source systems to change how
> they create or maintain master data. MDM operates as the authoritative
> source for the GDWH — not yet for the TMS systems themselves.

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

For the **party/client** domain, a single customer like _"Nestlé SA"_ may
appear in:

| Source System | Source Entity | Source Record ID | Role |
|---------------|---------------|-----------------|------|
| CargoWise (CW1 Zurich) | `OrgHeader` | `OH_Code = "NESTZUR"` | Customer, Shipper |
| CargoWise (CW1 Singapore) | `OrgHeader` | `OH_Code = "NESTLSG"` | Customer |
| Soloplan (DE) | `Adresse` | `ADR_Nummer = 40291` | Customer (`KUN`) |
| Atlantis | `BusinessPartner` | `BP_ID = "C-00847"` | Client |

The MDM hub creates **one golden record** and **four crosswalks**:

```
GoldenRecord (goldenRecordId = "GR-PARTY-00001")
  │  masteringDomain = "Client"
  │  mastersParty → party:Customer (the canonical Party instance)
  │
  ├── Crosswalk (sourceRecordId = "NESTZUR")
  │     fromSourceSystem → SourceSystem (sourceSystemCode = "CW1-ZUR")
  │     sourceEntityType = "OrgHeader"
  │     hasCrosswalkStatus → statusActive
  │
  ├── Crosswalk (sourceRecordId = "NESTLSG")
  │     fromSourceSystem → SourceSystem (sourceSystemCode = "CW1-SIN")
  │     sourceEntityType = "OrgHeader"
  │     hasCrosswalkStatus → statusActive
  │
  ├── Crosswalk (sourceRecordId = "40291")
  │     fromSourceSystem → SourceSystem (sourceSystemCode = "SOLOPLAN-DE")
  │     sourceEntityType = "Adresse"
  │     hasCrosswalkStatus → statusActive
  │
  └── Crosswalk (sourceRecordId = "C-00847")
        fromSourceSystem → SourceSystem (sourceSystemCode = "ATLANTIS")
        sourceEntityType = "BusinessPartner"
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
| CW1 (any instance) | 1 | `true` | Most complete party data, global standard |
| Atlantis | 2 | `true` | Legacy but high-quality master data |
| Soloplan | 3 | `true` | Good for DACH region, less global coverage |
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

## 3. Phase 1 Implementation — Consolidation for GDWH

### 3.1 What Phase 1 Delivers

| Deliverable | Description |
|-------------|-------------|
| **Golden records for Clients** | One mastered `party:Customer` per real-world client, consolidated from CW1, Soloplan, and Atlantis |
| **Crosswalk registry** | Every TMS-native customer ID linked to its golden record ID |
| **GDWH Gold integration** | Gold-layer `dim_customer` built from golden records instead of per-source silver tables |
| **Data quality rules** | Standardization (name normalization, address cleansing, country code validation) |
| **Match/merge engine** | Automated duplicate detection with steward review for uncertain matches |
| **Steward UI** | Review match candidates, approve/reject golden records, manage merge/split, audit trail |

### 3.2 Ontology Artifacts Required

The table below lists every artifact needed to make Phase 1 operational for
the party/client domain, mapped to the Kairos toolkit workflow.

#### 3.2.1 Already Done ✅

| Artifact | Location | Status |
|----------|----------|--------|
| Party domain ontology | `model/ontologies/party.ttl` | ✅ Complete — 15 classes, roles, contacts, addresses |
| MDM domain ontology | `model/ontologies/mdm.ttl` | ✅ Complete — golden record, crosswalk, source system, match/merge |
| Party silver extension | `model/extensions/party-silver-ext.ttl` | ✅ Complete — SCD Type 2, GDPR satellites, discriminator column |
| CW1 → Party mapping | `model/mappings/cargowise/cargowise-to-party.ttl` | ✅ Complete — OrgHeader, OrgAddress, role flags |
| Soloplan → Party mapping | `model/mappings/soloplan/soloplan-to-party.ttl` | ✅ Complete — Adresse, AdresseRolle, FK resolution |
| CW1 bronze vocabulary | `integration/sources/cargowise/cargowise.vocabulary.ttl` | ✅ Complete |
| Soloplan bronze vocabulary | `integration/sources/soloplan/soloplan.vocabulary.ttl` | ✅ Complete |

#### 3.2.2 To Be Created 🔲

| # | Artifact | Location | Purpose | Kairos Skill |
|---|----------|----------|---------|-------------|
| 1 | **MDM silver extension** | `model/extensions/mdm-silver-ext.ttl` | DDL + dbt for `silver_mdm.golden_record`, `silver_mdm.crosswalk`, `silver_mdm.source_system`, `silver_mdm.match_group`, `silver_mdm.merge_event` tables | `kairos-ontology-medallion-silver` |
| 2 | **Atlantis bronze vocabulary** | `integration/sources/atlantis/atlantis.vocabulary.ttl` | Describe Atlantis `BusinessPartner` table structure | `kairos-ontology-medallion-source` |
| 3 | **Atlantis → Party mapping** | `model/mappings/atlantis/atlantis-to-party.ttl` | Map Atlantis party fields to `party:` ontology | `kairos-ontology-medallion-silver` |
| 4 | **CW1 → MDM mapping** | `model/mappings/cargowise/cargowise-to-mdm.ttl` | Map CW1 `OrgHeader.OH_Code` → `mdm:Crosswalk.sourceRecordId` | `kairos-ontology-medallion-silver` |
| 5 | **Soloplan → MDM mapping** | `model/mappings/soloplan/soloplan-to-mdm.ttl` | Map Soloplan `Adresse.ADR_Nummer` → `mdm:Crosswalk.sourceRecordId` | `kairos-ontology-medallion-silver` |
| 6 | **Atlantis → MDM mapping** | `model/mappings/atlantis/atlantis-to-mdm.ttl` | Map Atlantis `BusinessPartner.BP_ID` → `mdm:Crosswalk.sourceRecordId` | `kairos-ontology-medallion-silver` |
| 7 | **MDM gold extension** | `model/extensions/mdm-gold-ext.ttl` | Gold-layer `dim_customer_master` and `fact_crosswalk` for Power BI | `kairos-ontology-medallion-gold` |
| 8 | **Mapping report** | `output/report/` | HTML coverage reports for MDM mappings per source | `kairos-ontology-mapping-report` |

### 3.3 Data Flow — Phase 1 (Consolidation)

```
 ┌────────────┐    ┌────────────┐    ┌────────────┐
 │ CargoWise  │    │  Soloplan   │    │  Atlantis  │
 │ OrgHeader  │    │  Adresse    │    │ BusParter  │
 └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
       │                 │                 │
       ▼                 ▼                 ▼
 ┌─────────────────────────────────────────────────┐
 │              Bronze Layer (Fabric)               │
 │  bronze_cargowise.org_header                     │
 │  bronze_soloplan.adresse                         │
 │  bronze_atlantis.business_partner                │
 └─────────────────────┬───────────────────────────┘
                       │  dbt bronze-to-silver models
                       ▼
 ┌─────────────────────────────────────────────────┐
 │             Silver Layer (Fabric)                │
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
 │             Gold Layer (Fabric)                  │
 │  gold_party.dim_customer_master                 │
 │     ← built from golden_record + party          │
 │  gold_mdm.fact_crosswalk                        │
 │     ← links dim_customer_master to source IDs   │
 │  gold_mdm.dim_source_system                     │
 └─────────────────────┬───────────────────────────┘
                       │
                       ▼
 ┌─────────────────────────────────────────────────┐
 │         Power BI / Semantic Model                │
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
| `partyName` | Most complete (longest non-null) | CW1 often has abbreviated names |
| `taxIdentifier` | Highest-priority trusted source | Tax ID must be authoritative |
| `eoriNumber` | Highest-priority trusted source | EORI is a regulated identifier |
| `streetAddress` | Most recently updated | Address changes should reflect latest |
| `country` | Highest-priority trusted source | Country codes must be standardized |
| `email` | Most recently updated | Contact info changes frequently |
| `scacCode` | CW1 always (source of truth for carrier codes) | CW1 is the carrier data authority |

---

## 4. Phase 2 — Coexistence (Bi-Directional Sync)

### 4.1 What Phase 2 Adds

Phase 2 extends the consolidation hub into a coexistence model where governed
golden-record updates flow _back_ to source systems.

| Capability | Ontology Support | Implementation |
|------------|-----------------|----------------|
| **Field-level system-of-record** | `SourceSystem.isTrustedSource` per attribute | Extend ontology with `FieldOwnership` class mapping attributes to owning systems |
| **Origin tagging** | `Crosswalk.lastVerifiedAt` + new `originSystem` property on sync events | Add `SyncEvent` class to `mdm.ttl` |
| **Loop prevention** | `originSystem` stamp on every change event | Fracht Connect checks origin tag; suppresses re-publish if origin = MDM |
| **Approval workflows** | `MatchDecision.decisionConfirmed` + `MergeEvent.mergePerformedBy` | Steward UI workflow; `MergeEvent` audit trail |
| **Publish-back** | `Crosswalk` provides the target system + record ID for write-back | Fracht Connect routes golden-record deltas to the correct source using crosswalk metadata |

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
| Global location codes (UN/LOCODE) | Per-TMS maintenance | Single authoritative source; changes infrequently |
| Shipment milestone definitions | Per-TMS event catalogs | Enterprise KPI consistency |
| Global KPI definitions | Spreadsheets / ad hoc | GDWH reporting standardization |
| Carrier hierarchy structures | CW1 + manual | Global carrier management |
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
 1. ✅ Party ontology (party.ttl)               — done
 2. ✅ MDM ontology (mdm.ttl)                   — done
 3. ✅ Party silver extension                    — done
 4. ✅ CW1 + Soloplan bronze vocabularies        — done
 5. ✅ CW1 + Soloplan → Party mappings           — done
 6. 🔲 MDM silver extension                     — kairos-ontology-medallion-silver
 7. 🔲 Atlantis bronze vocabulary               — kairos-ontology-medallion-source
 8. 🔲 Atlantis → Party + MDM mappings          — kairos-ontology-medallion-silver
 9. 🔲 CW1 → MDM crosswalk mapping             — kairos-ontology-medallion-silver
10. 🔲 Soloplan → MDM crosswalk mapping         — kairos-ontology-medallion-silver
11. 🔲 MDM gold extension                       — kairos-ontology-medallion-gold
12. 🔲 Mapping coverage reports                 — kairos-ontology-mapping-report
13. 🔲 Silver DDL projection                    — kairos project --target silver
14. 🔲 dbt model projection                     — kairos project --target dbt
15. 🔲 Gold / Power BI projection               — kairos project --target powerbi
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
| 4 | Crosswalks are per-source-system-instance, not per-product | CW1 Zurich and CW1 Singapore are separate source systems with separate crosswalks — reflecting Fracht's federated operating model |
| 5 | Phase 2 classes (`FieldOwnership`, `SyncEvent`) are **designed but not yet modeled** | Avoids over-engineering; will be added to `mdm.ttl` when Phase 2 activates |
| 6 | Match rules and survivorship rules are **configuration, not ontology** | The ontology captures _what happened_ (match scores, decisions); the _how_ is implementation-level configuration |
| 7 | SCD Type 2 for all MDM tables | Golden records and crosswalks need full history for audit, compliance, and merge/unmerge traceability |
