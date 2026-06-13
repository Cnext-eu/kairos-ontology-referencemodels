# WCO Ontology Gap Analysis Report

**Date:** 2026-06-09
**Ontology:** WCO (World Customs Organization)
**Current Version:** 1.1.0
**Standard Reference:** WCO Data Model 3.10.0, WCO SAFE Framework, WTO Customs Valuation Agreement, Revised Kyoto Convention, eFTI Regulation (EU) 2020/1056

---

## 1. Current Inventory

| Module | Classes | Obj Props | Datatype Props | Restrictions |
|--------|--------:|----------:|---------------:|-----------:|
| customs | 14 | 9 | 11 | 5 |
| trade-facilitation | 11 | 8 | 12 | 5 |
| documents | 10 | 8 | 13 | 7 |
| party | 8 | 8 | 10 | 7 |
| locations | 6 | 7 | 11 | 3 |
| **Total** | **49** | **40** | **57** | **27** |

### What's Well Covered

- **Declaration lifecycle:** Full hierarchy (CustomsDeclaration → Import/Export/Transit + EntryExitSummary), Filing, DeclarationStatus, AuthorityMessage
- **Tariff & valuation:** TariffClassification (HS code), CustomsValue, DutyCalculation, PreferenceClaim
- **Trade facilitation:** Certificate hierarchy (CoO, SPS), License hierarchy (Import/Export permits), AEO, TrustedTrader, SingleWindow, eFTIRecord
- **Documents:** SAD, T1/T2 transit, ATA/TIR carnets, import/export permit docs
- **Party roles:** Declarant, Authority, Broker, Importer, Exporter, AEO holder, FreightAgent, GuaranteeProvider
- **Locations:** CustomsOffice, BorderCrossing, BondedWarehouse, FreeZone, CustomsControlledArea, DesignatedExportPlace

---

## 2. Gap Analysis

### Gap 1: Goods Item / Commodity Description — 🔴 CRITICAL

**What the WCO DM has:** The central `GoodsItem` entity is the core line-item of every customs declaration. It describes what is being declared — commodity description, quantity, weight, value, country of origin, tariff classification, and packaging details. The WCO DM 3.x treats GoodsItem as the linchpin linking declarations to tariff, valuation, and procedure data.

**What we have:** TariffClassification and CustomsValue exist but are linked directly to CustomsDeclaration. There is no concept of "what goods are being declared" — no GoodsItem, no commodity description, no quantity/weight/packaging.

**Why it matters:** Without GoodsItem, the ontology models declarations as monolithic blobs rather than multi-line-item structures. A single import declaration may cover 50 different commodity types, each with its own HS code, value, origin, and duty rate. The current model cannot represent this.

**Recommendation:** Add `GoodsItem` class with properties for commodity description, quantity, weight (gross/net), country of origin, statistical value, and sequence number. Link to TariffClassification, CustomsValue, and DutyCalculation at the goods-item level rather than declaration level.

**Estimated scope:** 1 class, ~10 datatype properties, 3-4 object properties (refactoring existing links)

---

### Gap 2: Packaging and Transport Reference — 🟠 HIGH

**What the WCO DM has:** Packaging information (number of packages, package type, marks and numbers, container stuffing) and transport references (transport mode, conveyance reference number, nationality of transport means, arrival/departure transport means).

**What we have:** Nothing. No packaging concepts, no transport reference from a customs perspective. DCSA and MMT model transport extensively, but customs needs its own view — the conveyance reference number on a customs declaration is NOT the same as the DCSA transport plan.

**Why it matters:** Packaging data is mandatory on customs declarations globally. Transport mode and conveyance reference are required fields on SAD Box 18-21 and are essential for ICS2 pre-loading ENS filings.

**Recommendation:**
- Add `Packaging` class (numberOfPackages, packageType, marksAndNumbers, grossWeight, netWeight)
- Add `TransportMeans` class (transportModeCode, conveyanceReferenceNumber, nationalityOfTransportMeans, registrationNumber)
- Link to GoodsItem and CustomsDeclaration respectively
- Add rdfs:seeAlso to DCSA/MMT transport concepts

**Estimated scope:** 2 classes, ~12 datatype properties, 2-3 object properties

---

### Gap 3: Customs Procedure Codes — 🟠 HIGH

**What the WCO DM has:** Procedure codes (Customs Procedure Code — CPC) are a fundamental element. They define how goods are treated: free circulation (4000), inward processing (5100), temporary admission (5300), re-export (3100), etc. The WCO DM distinguishes requested procedure, previous procedure, and additional procedure.

**What we have:** Declaration types (Import/Export/Transit) but no procedure concept. The declaration type tells you the direction; the procedure code tells you the customs treatment.

**Why it matters:** CPC codes drive duty calculations, guarantee requirements, and compliance obligations. Without them, the ontology cannot distinguish between goods released to free circulation vs. placed under inward processing vs. placed in a customs warehouse.

**Recommendation:** Add `CustomsProcedure` class with procedureCode, requestedProcedure, previousProcedure, additionalProcedureCode. Link to CustomsDeclaration.

**Estimated scope:** 1 class, ~5 datatype properties, 1 object property

---

### Gap 4: Customs Valuation Adjustments — 🟡 MEDIUM

**What the WCO DM has / WTO Valuation Agreement:** The transaction value (Article 1) is subject to additions and deductions. Additions include: commissions, brokerage, container/packaging costs, royalties, license fees, assists (moulds, tooling, engineering), transport costs, insurance, loading/unloading. Deductions include: post-importation charges, domestic duties, transport after importation.

**What we have:** CustomsValue with `valueDeclared` and `valuationMethod`. No breakdown of adjustments.

**Why it matters:** Valuation adjustments are the primary area of customs disputes and audits. The difference between a declared value of €100K and a customs value of €130K (after adding royalties and assists) is significant for duty calculations.

**Recommendation:** Add properties on CustomsValue for adjustment categories: `royaltiesAndLicenseFees`, `assists`, `transportCostToPort`, `insuranceCost`, `loadingAndHandling`, `adjustmentTotal`, `valuationBasis` (CIF/FOB). Keep as properties, NOT sub-classes — these are always present on every valuation.

**Estimated scope:** 0 classes, ~8 datatype properties

---

### Gap 5: Revenue and Payment — 🟡 MEDIUM

**What the WCO DM has:** Payment methods (cash, deferred, electronic), payment references, guarantee utilization, duty deferment accounts, revenue collection records.

**What we have:** DutyCalculation with `dutyAmount` and `dutyRate`. No payment mechanism.

**Why it matters:** Knowing that duty has been calculated is half the picture — knowing whether it's been paid, deferred, or guaranteed is the other half. Trade finance and compliance systems need this.

**Recommendation:** Add `DutyPayment` class with paymentMethod, paymentReference, paymentDate, paymentAmount, defermentAccountNumber. Link to DutyCalculation.

**Estimated scope:** 1 class, ~6 datatype properties, 1 object property

---

### Gap 6: Guarantee Types — 🟡 MEDIUM

**What the WCO DM has / EU UCC:** Individual guarantee, comprehensive guarantee, transit guarantee (for T1/T2), guarantee waiver, flat-rate guarantee, fixed guarantee. Each has a Guarantee Reference Number (GRN), validity period, and coverage amount.

**What we have:** GuaranteeProvider with guaranteeReference and guaranteeAmount. No guarantee type classification, no GRN structure, no validity period.

**Why it matters:** Transit operations (T1/T2/TIR) require specific guarantee types. AEO holders can use comprehensive guarantees or reduced amounts. The guarantee type drives the customs procedure options available.

**Recommendation:** Add properties on GuaranteeProvider: `guaranteeType` (code-based: individual/comprehensive/transit/waiver/flat-rate), `guaranteeValidFrom`, `guaranteeValidTo`, `guaranteeCurrency`, `guaranteeReferenceNumber` (GRN). Keep as properties — structurally identical, differentiated by code.

**Estimated scope:** 0 classes, ~5 datatype properties

---

### Gap 7: Risk Management & Selectivity — 🟡 MEDIUM

**What the WCO DM has / SAFE Framework:** Risk assessment profiles, selectivity criteria, risk indicators (green/yellow/red channel), targeting rules, examination orders. This is central to modern customs — pre-arrival risk assessment determines whether goods are inspected or fast-tracked.

**What we have:** InspectionReference exists but has no properties at all (no risk indicators, no selectivity channel).

**Why it matters:** Risk-based customs management is the WCO's core modernization pillar. Without risk concepts, the ontology misses how customs authorities actually process declarations in practice.

**Recommendation:** Enrich InspectionReference with risk-related properties: `riskChannel` (green/yellow/red/blue), `selectivityResult`, `examinationType` (documentary/physical/scanner), `riskIndicatorCode`. Add `RiskProfile` class linked to Declarant/AEOHolder for compliance scoring.

**Estimated scope:** 1 class, ~8 datatype properties, 1 object property

---

### Gap 8: Special Customs Procedures — 🟡 MEDIUM

**What the WCO DM has:** The Revised Kyoto Convention and WCO DM define specific customs procedures via CPC codes: customs warehousing (71xx), inward processing (51xx), outward processing (21xx), temporary admission (53xx), end-use relief (44xx), free zone operations (78xx). Each has distinct guarantee, time-limit, and discharge requirements.

**What we have:** Declaration subtypes (Import/Export/Transit) but no concept of special procedures. `FreeZone` exists in locations but only as a place, not as a procedure.

**Why it matters:** Special procedures account for ~15-20% of all EU customs declarations. Inward processing alone covers most manufacturing imports. Without procedure codes, the ontology cannot distinguish "goods released to free circulation" from "goods placed under inward processing suspension."

**Recommendation:** This overlaps with Gap 3 (Customs Procedures). Rather than a separate module, add `procedureCategory` (normal/special) and `specialProcedureType` (warehousing/inward-processing/outward-processing/temporary-admission/end-use) as properties on CustomsProcedure. The procedure codes already encode this information.

**Estimated scope:** 0 additional classes (covered by Gap 3), ~3 additional datatype properties

---

### Gap 9: Duty Type Granularity — 🟡 MEDIUM

**What the WCO DM has:** WCO DM element 113 (`DutyTaxFeeTypeCode`) distinguishes: A00 = customs duty, B00 = anti-dumping duty, C00 = countervailing duty, 1XX = excise, 2XX/3XX = VAT/GST. Each has different calculation methods (ad valorem, specific, compound), different legal bases, and different payment regimes.

**What we have:** `DutyCalculation` with `dutyAmount` and `dutyRate` only. No duty type differentiation.

**Why it matters:** Anti-dumping and countervailing duties are trade defense instruments with separate legal proceedings. Excise and VAT are collected at import but are fundamentally different taxes. Lumping them all into one `DutyCalculation` loses critical business meaning.

**Recommendation:** Add properties on DutyCalculation: `dutyTypeCode` (A00/B00/C00/etc.), `dutyCalculationMethod` (ad-valorem/specific/compound), `quotaOrderNumber` (tariff quota reference), `dutyRegimeCode` (MFN/preferential/suspension/anti-dumping). Keep as properties — structurally identical calculations.

**Estimated scope:** 0 classes, ~5 datatype properties

---

### Gap 10: Advance Rulings — 🟢 LOW

**What the WCO DM has:** Binding Tariff Information (BTI), advance rulings on classification, origin, and valuation. These are pre-clearance decisions that give legal certainty to traders.

**What we have:** Nothing. However, this is a niche concept — it's important for compliance but not for day-to-day declaration processing.

**Recommendation:** Add `AdvanceRuling` class (rulingNumber, rulingType: classification/origin/valuation, rulingDate, validFrom, validTo, issuingAuthority). Link to TariffClassification or CustomsValue.

**Estimated scope:** 1 class, ~6 datatype properties, 1 object property

---

### Gap 11: Consignee/Consignor Distinction — 🟢 LOW

**What the WCO DM has:** Distinct consignee (receiver of goods) and consignor (sender of goods) roles, separate from importer/exporter. In triangular trade, the consignee is NOT the importer and the consignor is NOT the exporter.

**What we have:** Importer and Exporter only. These cover the primary flow but miss triangular trade and third-party logistics scenarios.

**Recommendation:** Add `Consignee` and `Consignor` classes with identity properties (name, address, identifier). Link to CustomsDeclaration. Add rdfs:seeAlso to BSP party concepts.

**Estimated scope:** 2 classes, ~4 datatype properties, 2 object properties

---

### Gap 12: Cross-Domain Alignment — 🔴 CRITICAL

**What exists:** WCO has rdfs:seeAlso to wcoomd.org but ZERO cross-references to other Kairos ontologies. Meanwhile, BSP already points TO WCO (compliance, CoO, CustomsDeclaration). IMO has no WCO links. DCSA has no WCO links.

**What's needed:** Bidirectional alignment between WCO and the rest of the ecosystem:
- WCO CustomsDeclaration ↔ BSP compliance concepts
- WCO locations (CustomsOffice, BorderCrossing) ↔ DCSA locations, IMO Port
- WCO party (Importer, Exporter) ↔ BSP party (Buyer, Seller)
- WCO documents (CoO, SPS Certificate) ↔ BSP documents
- WCO TransitDeclaration ↔ DCSA transport concepts
- WCO AEOHolder ↔ BSP compliance certification

**Recommendation:** Add rdfs:seeAlso annotations throughout WCO modules pointing to BSP, DCSA, IMO counterparts. This is the highest-value, lowest-effort enrichment.

**Estimated scope:** 0 classes, 0 properties, ~15-20 rdfs:seeAlso annotations

---

### Gap 13: Declaration Property Enrichment — 🟡 MEDIUM

**What the WCO DM has:** Rich data elements on declarations that we're missing (confirmed by WCO DM schema elements with WCO IDs):
- `declarationType` (WCO D013: IM, EX, CO)
- `totalNumberOfItems` (WCO 228)
- `totalPackages` (WCO 146)
- `totalGrossWeight` (WCO 131)
- `currencyCode` (WCO 135, ISO 4217)
- `exchangeRate` (WCO 118)
- `placeOfLoading`, `placeOfUnloading` (UN/LOCODE)
- `acceptanceDate` (WCO 023 — when customs accepts)
- `releaseDate` (when goods released)
- `amendmentReason` (WCO 099)
- `functionCode` (WCO 017: 9=original, 13=amendment, 14=cancellation)
- `movementReferenceNumber` (MRN — especially for transit)
- `localReferenceNumber` (LRN, WCO D026)
- `specificCircumstancesCode` (WCO 504)

**What we have:** Only `declarationNumber` on CustomsDeclaration. Very thin.

**Recommendation:** Add ~12 datatype properties to CustomsDeclaration and its subclasses.

**Estimated scope:** 0 classes, ~12 datatype properties

---

## 3. Summary

| # | Gap | Severity | New Classes | New Properties | Priority |
|---|-----|----------|------------|---------------|----------|
| 1 | Goods Item | 🔴 CRITICAL | 1 | ~14 | Phase 1 |
| 12 | Cross-Domain Alignment | 🔴 CRITICAL | 0 | ~0 (+seeAlso) | Phase 1 |
| 2 | Packaging & Transport | 🟠 HIGH | 2 | ~15 | Phase 2 |
| 3 | Customs Procedures | 🟠 HIGH | 1 | ~6 | Phase 2 |
| 13 | Declaration Properties | 🟡 MEDIUM | 0 | ~15 | Phase 2 |
| 4 | Valuation Adjustments | 🟡 MEDIUM | 0 | ~8 | Phase 3 |
| 5 | Revenue & Payment | 🟡 MEDIUM | 1 | ~7 | Phase 3 |
| 6 | Guarantee Types | 🟡 MEDIUM | 0 | ~5 | Phase 3 |
| 9 | Duty Type Granularity | 🟡 MEDIUM | 0 | ~5 | Phase 3 |
| 7 | Risk Management | 🟡 MEDIUM | 1 | ~9 | Phase 4 |
| 8 | Special Procedures | 🟡 MEDIUM | 0 | ~3 | Phase 2 |
| 10 | Advance Rulings | 🟢 LOW | 1 | ~7 | Phase 5 |
| 11 | Consignee/Consignor | 🟢 LOW | 2 | ~6 | Phase 5 |
| **Total** | | | **9** | **~100** | |

### Key Observations

1. **The biggest structural gap is GoodsItem** — without it, the ontology cannot represent multi-line declarations, which is how ALL customs declarations work in practice.

2. **Cross-domain alignment is free value** — WCO is the most isolated ontology in the Kairos ecosystem with zero outbound references.

3. **The customs module is structurally thin** — 14 classes but only 11 datatype properties for the most data-intensive domain in international trade. Declaration properties need significant enrichment.

4. **Property enrichment > new classes** — Most gaps are about adding properties to existing classes (valuation adjustments, guarantee types, declaration properties) rather than creating new class hierarchies. This is a sign the class structure is fundamentally sound.

5. **Overlap risk is LOW** — Unlike BSP (trade finance overlap with banking) or TIC (container overlap with DCSA), WCO concepts are highly domain-specific. The main overlap is with BSP compliance/documents, which is handled via rdfs:seeAlso.

---

## 4. Challenge & Critique

Applied design principles: (1) no cross-ontology duplication, (2) reify only structurally distinct types, (3) reference model boundary — domain entities IN / operational data OUT, (4) cross-domain via rdfs:seeAlso, (5) code-based patterns over class hierarchies, (6) contextual roles as properties.

### Challenge 1: GoodsItem — ✅ AGREE (keep as-is)

GoodsItem is genuinely the biggest structural gap. Every customs declaration in the world has line items. The class is structurally distinct (has its own sequence number, commodity description, weight, origin — not derivable from the declaration header). No duplication risk — MMT has CargoItem but that's a transport concept; WCO GoodsItem is a customs/tariff classification concept. **Keep 1 class, ~12 properties.**

### Challenge 2: Packaging & Transport — ⚠️ PARTIAL (keep Packaging, SKIP TransportMeans)

**Packaging: AGREE.** Packaging is a 1:N relationship on GoodsItem (a goods item can have multiple package types). It's a structurally distinct entity with its own properties (packageType, numberOfPackages, marksAndNumbers). 1 class justified.

**TransportMeans: SKIP.** The SupplyChain ontology already bridges MMT Consignment → WCO CustomsDeclaration via `requiresCustomsDeclaration`. The actual transport entities live in DCSA (Vessel, Transport), MMT (TransportService), and IMO (Vessel). Creating a WCO TransportMeans class would DUPLICATE these concepts.

What customs actually needs is transport REFERENCE DATA on the declaration — the SAD Box 18-21 fields: `transportModeCode`, `conveyanceReferenceNumber`, `nationalityOfTransportMeans`. These are **datatype properties on CustomsDeclaration**, not a separate class. Add rdfs:seeAlso to DCSA/IMO transport.

**Result: 1 class (Packaging), ~6 props + ~4 transport data props on CustomsDeclaration. Down from 2 classes, ~15 props.**

### Challenge 3+8: Customs Procedures + Special Procedures — ✅ MERGE

Gap 8 (Special Procedures) correctly identified itself as overlapping with Gap 3. Merge them. CustomsProcedure is justified as a class — it has its own identity (procedure code), its own lifecycle (requested → applied), and its own properties (previousProcedure, additionalProcedure, specialProcedureType).

The procedure CODE already encodes whether it's normal (40xx = free circulation) or special (51xx = inward processing, 53xx = temporary admission, 71xx = warehousing). No need for separate special procedure classes — the code-based pattern handles this.

**Result: 1 class, ~8 properties (merged). Down from 1 class + ~9 props across two gaps.**

### Challenge 4: Valuation Adjustments — ⚠️ TRIM

Individual properties for royalties, assists, transport, insurance, loading, handling, proceeds → too many fine-grained decimal properties for a reference model. The WCO DM has ~15 adjustment types; modeling all of them is over-engineering.

Keep the STRUCTURAL ones that affect the calculation method:
- `valuationBasis` (CIF/FOB/CFR — determines which adjustments apply)
- `freightCharges` (WCO 117 — most common adjustment)
- `insuranceCost` (CIF calculation)
- `totalAdjustments` (net additions/deductions)
- `currencyCode` (ISO 4217)
- `exchangeRate` (WCO 118)

Drop: royalties, assists, proceeds, loading, handling — these are case-specific line items that belong in operational systems, not reference models.

**Result: 0 classes, ~6 properties. Down from ~8.**

### Challenge 5: Revenue & Payment — ⚠️ SKIP CLASS (properties only)

DutyPayment as a separate class crosses the **reference model boundary**. Payment is an OPERATIONAL EVENT — it happens in banking/treasury systems, has payment statuses, reconciliation records, etc. The reference model should know WHAT is owed (DutyCalculation) but not HOW it was paid.

Better: Add 3 payment-related properties directly on DutyCalculation: `paymentMethodCode` (cash/deferred/electronic), `defermentAccountNumber`, `paymentStatus` (unpaid/paid/deferred). These capture the structural relationship without creating an operational entity.

**Result: 0 classes (down from 1), ~3 properties (down from ~7).**

### Challenge 6: Guarantee Types — ✅ AGREE (keep as-is)

Properties on GuaranteeProvider. Code-based pattern. Structurally identical guarantees differentiated by type code. 0 classes, ~5 properties. **Keep as-is.**

### Challenge 7: Risk Management — ⚠️ SKIP RiskProfile CLASS

**RiskProfile: SKIP.** Risk profiles are OPERATIONAL — maintained by customs authorities, contain classified targeting criteria, change frequently. Firmly OUTSIDE the reference model boundary. No customs authority would publish their risk profiles in an ontology.

**InspectionReference enrichment: AGREE.** Adding `riskChannel` (green/yellow/red/blue), `examinationType` (documentary/physical/scanner), `examinationResult` on the existing InspectionReference class is justified — these are OUTCOME data, not operational secrets.

**Result: 0 classes (down from 1), ~4 properties (down from ~9).**

### Challenge 9: Duty Type Granularity — ✅ AGREE (minor trim)

Properties on DutyCalculation. Code-based pattern (dutyTypeCode, dutyCalculationMethod, dutyRegimeCode, quotaOrderNumber). **Keep 0 classes, ~4 properties.**

### Challenge 10: Advance Rulings — ❌ SKIP for v1.2.0

BTI is important for compliance professionals but very niche for the core declaration model. Can be added in a future version. **Skip entirely.**

### Challenge 11: Consignee/Consignor — ✅ AGREE (keep classes)

Consistent with existing party module pattern (each role is a class with identity props). Consignee/Consignor are NOT the same as Importer/Exporter in triangular trade. The WCO DM has dedicated data elements (R014/R015, R020/R021). **Keep 2 classes, ~6 properties.**

### Challenge 12: Cross-Domain Alignment — ✅ AGREE (scope correctly)

The SupplyChain ontology handles STRUCTURAL bridges (owl:ObjectProperty linking classes). WCO should add rdfs:seeAlso for SEMANTIC alignment — documenting concept relationships without creating formal OWL relationships. No duplication with SupplyChain.

**Keep ~15 rdfs:seeAlso annotations.**

### Challenge 13: Declaration Property Enrichment — ✅ AGREE (with assignment)

Most properties go on CustomsDeclaration. Some are subclass-specific:
- `movementReferenceNumber` → TransitDeclaration only
- Transport reference properties → covered by Challenge 2

**Keep ~12 properties.**

---

## 5. Challenge Summary — Before vs After

| Gap | Original | Challenged | Classes | Properties |
|-----|----------|------------|---------|------------|
| 1: GoodsItem | 1 cls, ~14 props | AGREE | 1 | ~12 |
| 2: Packaging & Transport | 2 cls, ~15 props | 1 cls + decl props | 1 | ~10 |
| 3+8: Procedures (merged) | 1 cls, ~9 props | MERGE | 1 | ~8 |
| 4: Valuation | 0 cls, ~8 props | TRIM | 0 | ~6 |
| 5: Revenue | 1 cls, ~7 props | SKIP class | 0 | ~3 |
| 6: Guarantee | 0 cls, ~5 props | AGREE | 0 | ~5 |
| 7: Risk | 1 cls, ~9 props | SKIP class | 0 | ~4 |
| 9: Duty Types | 0 cls, ~5 props | AGREE | 0 | ~4 |
| 10: Advance Rulings | 1 cls, ~7 props | SKIP | 0 | 0 |
| 11: Consignee/Consignor | 2 cls, ~6 props | AGREE | 2 | ~6 |
| 12: Cross-Domain | 0 cls, ~15 seeAlso | AGREE | 0 | ~15 seeAlso |
| 13: Declaration Props | 0 cls, ~15 props | AGREE | 0 | ~12 |
| **Original Total** | **9 cls, ~100 props** | | | |
| **Challenged Total** | | | **5 cls** | **~70 props + ~15 seeAlso** |

**Net reduction: 4 classes removed, ~30 properties trimmed.**

Key decisions:
- **TransportMeans → SKIP** (SupplyChain already bridges; use data properties)
- **DutyPayment → SKIP** (operational, outside reference model boundary)
- **RiskProfile → SKIP** (operational, classified data)
- **Advance Rulings → SKIP** (too niche for v1.2.0)
- **Special Procedures → MERGED** into Customs Procedures (code-based)

---

## 6. Implementation Plan — WCO v1.2.0

### Phase 1: Cross-Domain Alignment + Declaration Enrichment
**Modules:** customs.ttl, documents.ttl, party.ttl, locations.ttl, trade-facilitation.ttl
- Add ~15 rdfs:seeAlso annotations across all 5 modules pointing to BSP, DCSA, IMO, MMT
- Add ~12 declaration header properties on CustomsDeclaration (declarationType, totalItems, totalPackages, totalGrossWeight, acceptanceDate, releaseDate, functionCode, LRN, specificCircumstancesCode, placeOfLoading, placeOfUnloading, amendmentReason)
- Add ~4 transport reference properties on CustomsDeclaration (transportModeCode, conveyanceReferenceNumber, nationalityOfTransportMeans, borderTransportMeansId)
- Add MRN property on TransitDeclaration

### Phase 2: GoodsItem + Packaging
**Module:** customs.ttl (extend)
- Add `GoodsItem` class (commodityDescription, sequenceNumber, countryOfOrigin, statisticalValue, grossWeight, netWeight, tariffQuantity, supplementaryUnits, dangerousGoodsUNDG)
- Add `Packaging` class (packageTypeCode, numberOfPackages, marksAndNumbers, shippingMarks)
- Add object properties: hasGoodsItem (Declaration→GoodsItem), hasPackaging (GoodsItem→Packaging)
- Refactor: add hasGoodsItemTariffClassification, hasGoodsItemCustomsValue, hasGoodsItemDutyCalculation at goods-item level
- Keep existing declaration-level links for backward compatibility

### Phase 3: Customs Procedures
**Module:** customs.ttl (extend)
- Add `CustomsProcedure` class (procedureCode, requestedProcedure, previousProcedure, additionalProcedureCode, procedureCategory, specialProcedureType, procedureDescription, dischargeDueDate)
- Add object property: hasCustomsProcedure (GoodsItem→CustomsProcedure)

### Phase 4: Valuation + Revenue + Duty + Guarantee Enrichment
**Modules:** customs.ttl, party.ttl
- Add valuation properties on CustomsValue: valuationBasis, freightCharges, insuranceCost, totalAdjustments, currencyCode, exchangeRate
- Add payment properties on DutyCalculation: paymentMethodCode, defermentAccountNumber, paymentStatus
- Add duty type properties on DutyCalculation: dutyTypeCode, dutyCalculationMethod, dutyRegimeCode, quotaOrderNumber
- Add guarantee properties on GuaranteeProvider: guaranteeType, guaranteeValidFrom, guaranteeValidTo, guaranteeCurrency, guaranteeReferenceNumber

### Phase 5: Party + Risk Enrichment
**Modules:** party.ttl, customs.ttl
- Add Consignee, Consignor classes to party.ttl (with name, identifier, address properties)
- Add hasConsignee, hasConsignor object properties on CustomsDeclaration
- Enrich InspectionReference: riskChannel, examinationType, examinationResult, inspectionDate

### Phase 6: Version Bump + README
- Bump all 6 TTL files to v1.2.0
- Update VERSION file
- Rewrite README with changelog, cross-domain alignment table, module inventory
