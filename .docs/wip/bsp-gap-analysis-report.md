# BSP (Buy-Ship-Pay) Gap Analysis Report

**Date:** 2026-06-13
**Analyst:** Kairos Ontology Team (AI-assisted)
**Source Standard:** UN/CEFACT Buy-Ship-Pay Reference Data Model (BSP-RDM v1.0) / ISO 20197-1:2024
**Current Version:** 1.2.0
**Scope:** Derived ontology at `ontology-reference-models/derived-ontologies/BSP/`

---

## Executive Summary

The BSP ontology currently has **8 modules, 115 classes, 53 object properties, and 109 datatype properties** covering the three pillars of international trade (Buy, Ship, Pay) plus cost-accounting and revenue-yield analytics. Cross-references to the UN/CEFACT vocabulary are extensive (~30 rdfs:seeAlso links).

However, comparison against the BSP-RDM D23B master message assembly, the UN/CEFACT vocabulary, and the sibling RDMs reveals **significant gaps** in 8 areas. The analysis also considers how BSP interacts with the other Kairos derived ontologies (DCSA, IMO, MMT, WCO) to avoid duplication.

---

## Current Coverage Summary

| Module | Classes | ObjectProps | DatatypeProps | Restrictions |
|--------|---------|-------------|---------------|-------------|
| party | 12 | 6 | 4 | 0 |
| commercial | 18 | 11 | 24 | 4 |
| financial | 29 | 12 | 31 | 5 |
| documents | 16 | 3 | 5 | 0 |
| compliance | 5 | 2 | 3 | 0 |
| reference-data | 13 | 4 | 7 | 0 |
| cost-accounting | 9 | 8 | 15 | 4 |
| revenue-yield | 13 | 7 | 20 | 1 |
| **Total** | **115** | **53** | **109** | **14** |

---

## Gap Analysis

### Gap 1: Trade Finance Instruments — CRITICAL

**What's missing:** The financial module has `LetterOfCredit`, `DocumentaryCollection`, and `BankGuarantee` as classes, but they lack the structural depth the BSP-RDM provides.

**Specific gaps:**
- **Letter of Credit types**: No distinction between irrevocable, standby (SBLC), revolving, back-to-back, red clause, green clause, transferable. The CCL D23B `financialAccountType` QDT defines all of these.
- **Purchase Order Financing**: BSP-RDM has a full 3-message workflow (`FinancingRequestDocument`, `FinancingSummaryDocument`, `FinancingRequestCancellation`) for supply chain finance/factoring/reverse factoring. The ontology has zero classes for this.
- **L/C lifecycle properties**: No `issuingBank`, `advisingBank`, `confirmingBank`, `presentingBank` party role properties on LetterOfCredit. No `lcAmendment`, `lcDrawing`, `lcPresentation` concepts.
- **Open account finance**: Factoring, forfaiting, and reverse factoring are not modeled.
- **Remittance Advice**: BSP-RDM has `CrossIndustryRemittanceAdvice` — no equivalent class in the ontology.

**Evidence:** `spec-JSONschema:UNECE-PurchaseOrderFinancingRequest.json`, `UNECE-PAYContextCCL.json`

**Impact:** Trade finance is the "Pay" pillar's most complex domain. Without it, the ontology cannot model supply chain finance workflows that are increasingly central to global trade.

**Estimated scope:** ~10–12 new classes, ~15 properties

---

### Gap 2: Supply Chain Visibility / Track-and-Trace — CRITICAL

**What's missing:** The BSP-RDM master assembly includes four GS1 EPCIS-aligned event types (`ttObjectEvent`, `ttTransformationEvent`, `ttAggregationEvent`, `ttTransactionEvent`) plus traceability and transparency schemas. The current ontology has only generic `BusinessEvent`, `OrderEvent`, `ShipmentEvent` — none of the EPCIS structure.

**Specific gaps:**
- **EPCIS event types**: No `ObjectEvent`, `TransformationEvent`, `AggregationEvent`, `TransactionEvent` classes with their EPCIS-specific properties (bizStep, disposition, readPoint, bizLocation, EPCList)
- **Consignment/Equipment status**: BSP-RDM defines `MultimodalTransportConsignmentStatusReport` and `MultimodalTransportEquipmentStatusReport` — not present
- **Traceability events**: `TLTraceabilityEvent`, `TLProductTransparency` schemas exist in BSP-RDM — not modeled
- **Milestone taxonomy**: No standardized milestone codes; `eventType` is a free string vs. the BSP-RDM `logisticsStatusCode` QDT (booked, loaded, departed, arrived, customs-held, delivered)

**Evidence:** `spec-JSONschema:UNECE-BSPMaster.json` (ttObjectEvent, ttTransformationEvent, etc.), `UNECE-TLTraceabilityEvent.json`

**Impact:** Track-and-trace is the primary integration point for supply chain visibility platforms. Without EPCIS alignment, BSP cannot interoperate with GS1-based visibility networks.

**Estimated scope:** ~8–10 new classes, ~20 properties

---

### Gap 3: Cross-Domain Alignment to Kairos Ontologies — HIGH

**What's missing:** BSP has extensive `rdfs:seeAlso` links to the UN/CEFACT vocabulary but **zero cross-references** to the other Kairos derived ontologies (DCSA, IMO, MMT, WCO) that model the same concepts from different perspectives.

**Specific alignment gaps:**
- `BSP commercial:Shipment` ↔ `DCSA shipment-journey:Shipment` — same concept, no seeAlso
- `BSP commercial:Consignment` ↔ `MMT consignment:Consignment` — identical concept
- `BSP commercial:TransportEquipment` ↔ `DCSA equipment:Container` — container as equipment
- `BSP documents:BillOfLading` ↔ `DCSA transport-documents:TransportDocument` — B/L is a transport document
- `BSP documents:CustomsDeclaration` ↔ `WCO customs:CustomsDeclaration` — same
- `BSP reference-data:Port` ↔ `IMO locations:Port` and `DCSA locations:Location`
- `BSP party:Carrier` ↔ `DCSA party:Carrier` — same party role
- `BSP compliance:TariffClassification` ↔ `WCO customs:TariffClassification` — HS code alignment
- `BSP compliance:DutyTax` ↔ `WCO customs:DutyTax` — customs duty

**Evidence:** All BSP `rdfs:seeAlso` point only to `vocabulary.uncefact.org`, zero to Kairos `kairosflow.ai/ont/` namespaces

**Impact:** Without cross-domain alignment, hub ontologies that compose BSP with DCSA/IMO/WCO have no machine-readable indication of concept overlap.

**Estimated scope:** ~15–20 rdfs:seeAlso annotations (no new classes)

---

### Gap 4: Document Lifecycle Properties — HIGH

**What's missing:** The documents module has 16 document type classes but only 5 datatype properties (`documentNumber`, `documentDate`, `documentType`, `billOfLadingNumber`, `airWaybillNumber`). Most document classes have no specific properties — they're structurally identical empty subclasses of `Document`.

**Specific gaps:**
- **BillOfLading**: Missing `placeOfIssue`, `dateOfIssue`, `numberOfOriginals`, `onBoardDate`, `shippedOnBoardDate`, `freightPayableAt`, `negotiable` (boolean), `platformProvider` (for eBL), `authenticatedOriginalIndicator`
- **AirWaybill**: Missing `originAirport`, `destinationAirport`, `executingCarrier`, `agentIATACode`, `chargeableWeight`
- **CertificateOfOrigin**: Missing `preferentialIndicator`, `originCriterion`, `issuingAuthority`, `tradeAgreementReference`
- **CustomsDeclaration**: Missing `customsOffice`, `declarationType` (import/export/transit), `customsProcedureCode`, `declarantReference`, `entryNumber`, `releaseDate`
- **All documents**: Missing `documentStatus` (DRAFT, ISSUED, AMENDED, SURRENDERED, ACCOMPLISHED), `issuer`, `signatory`

**Evidence:** Comparison with `UNECE-MaritimeBillofLading.json`, `UNECE-AirWaybill.json`, CCL Document ABIEs

**Impact:** Documents without properties are classification-only — they can't carry the data needed for integration with document management or customs systems.

**Estimated scope:** ~40–50 new datatype properties across existing classes, ~3–5 new object properties

---

### Gap 5: Compliance & Regulatory Depth — HIGH

**What's missing:** The compliance module has only 5 classes. The BSP-RDM (especially via CBM-RDM) provides significantly richer regulatory modeling.

**Specific gaps:**
- **Customs valuation**: No `CustomsValuation` class — critical for WTO Agreement on Customs Valuation, transaction value, deductive/computed methods
- **Regulatory procedure**: No distinction between `ImportProcedure`, `ExportProcedure`, `TransitProcedure` — the BSP-RDM `RegulatoryProcedure` has `governmentActionCode` (examination, release, seizure, re-export)
- **Trade sanctions**: `TradeSanction` class exists but has zero properties — no `sanctionedEntity`, `sanctionType`, `sanctionAuthority`, `effectiveDate`
- **Rules of Origin**: No `RuleOfOrigin`, `OriginCriterion` for preferential trade agreements (EU GSP, CPTPP, RCEP, USMCA)
- **Dual-use goods**: No export control classification (ECCN, Wassenaar Arrangement)
- **Trade agreement specifics**: `TradeAgreement` has no properties — no `agreementName`, `preferentialRate`, `cumulationRules`

**Evidence:** `UNECE-CBMContextCCL.json`, WCO DM alignment in BSP-RDM

**Impact:** BSP's value proposition includes cross-border management. Thin compliance modeling limits utility for customs automation.

**Estimated scope:** ~8–10 new classes, ~20 properties

---

### Gap 6: Party Identity & Additional Roles — MEDIUM

**What's missing:** BSP has 12 party types but the CCL defines additional roles, and existing parties lack identity/verification properties.

**Specific gaps:**
- **Missing party roles** from CCL: `InsuranceUnderwriter`, `InspectionBody`, `CertifyingBody`, `TerminalOperator`, `WarehouseKeeper`, `IssuingBank`, `AdvisingBank`, `ConfirmingBank` (distinct from generic Bank)
- **Party identity**: No `legalEntityIdentifier` (LEI / ISO 17442), `taxIdentificationNumber`, `dunsNumber`, `registrationCountry`, `registrationNumber`
- **Contact depth**: Only `contactEmail` and `contactPhone` — no `contactPerson`, `department`, `postalAddress` (separate from trade address)
- **Party relationships**: Only `actsOnBehalfOf`-style via object properties on commercial classes. No `subsidiaryOf`, `branchOf`, `authorizedAgentFor` relationships

**Evidence:** CCL D23B `TradeParty` ABIE, `vocabulary.uncefact.org/TradeParty` properties

**Impact:** Party identification is critical for sanctions screening, KYC, and customs declarations.

**Estimated scope:** ~6–8 new classes, ~10–12 properties

---

### Gap 7: Procurement Lifecycle Gaps — MEDIUM

**What's missing:** The commercial module covers the core order/shipment flow but misses several procurement lifecycle stages that BSP-RDM explicitly models.

**Specific gaps:**
- **Request for Quotation (RFQ)**: BSP-RDM has `CrossIndustryRequestforQuotation` and `CrossIndustryRequestforQuotationResponse` — the ontology has `Quotation` but no RFQ
- **Order Change / Order Response**: BSP-RDM models the order amendment lifecycle (`CrossIndustryOrderChange`, `CrossIndustryOrderResponse`) — not present
- **Demand Forecast / Supply Instruction**: BSP-RDM covers supply chain planning with `CrossIndustryDemandForecast`, `CrossIndustrySupplyInstruction` — not modeled
- **Despatch Advice / Receiving Advice**: BSP-RDM has separate `CrossIndustryDespatchAdvice` and `CrossIndustryReceivingAdvice` — the ontology has `DeliveryNote` and `ReceiptAdvice` in documents but they lack the shipment-level structure (line items, quantities received, discrepancies)
- **Product Catalogue**: `CrossIndustryCatalogue` exists in BSP-RDM — not modeled

**Evidence:** `spec-JSONschema:UNECE-CrossIndustryRequestforQuotation.json` etc.

**Impact:** Without RFQ/order change lifecycle, the "Buy" pillar is incomplete for B2B procurement platforms.

**Estimated scope:** ~6–8 new classes, ~15 properties

---

### Gap 8: Sustainability / Carbon Accounting — LOW

**What's missing:** BSP-RDM includes SDCE-RDM (Sustainable Development & Circular Economy) with digital product passports and carbon accounting. The Kairos repo has a separate `Sustainability` derived ontology, but BSP has no linkage to it.

**Specific gaps:**
- No `CarbonFootprint` or `EmissionsRecord` linked to `TransportLeg` or `Shipment`
- No `DigitalProductPassport` (EU DPP regulation / `CircularProductDataProtocol` in BSP-RDM)
- No alignment to ISO 14083 (transport emissions methodology)
- No `rdfs:seeAlso` from BSP commercial/transport concepts to the Sustainability ontology

**Evidence:** `UNECE-SDCEContextCCL.json`, `UNECE-CircularProductDataProtocol.json`

**Impact:** Growing regulatory requirement (EU CBAM, CSRD, DPP). Low priority since separate Sustainability ontology exists; cross-referencing would suffice.

**Estimated scope:** ~3–5 rdfs:seeAlso annotations, or ~5–8 new classes if integrated into BSP

---

## Priority Summary

| # | Gap | Priority | New Classes | New Props | Rationale |
|---|-----|----------|-------------|-----------|-----------|
| 1 | Trade Finance Instruments | CRITICAL | ~12 | ~15 | "Pay" pillar's most complex domain; supply chain finance is core BSP |
| 2 | Track-and-Trace / EPCIS | CRITICAL | ~10 | ~20 | GS1 visibility is the standard interop layer; BSP-RDM explicitly includes it |
| 3 | Cross-Domain Alignment | HIGH | 0 | ~20 seeAlso | Essential for hub composition; zero Kairos cross-refs currently |
| 4 | Document Lifecycle Properties | HIGH | 0 | ~50 | 16 document classes with almost no properties — empty shells |
| 5 | Compliance & Regulatory Depth | HIGH | ~10 | ~20 | CBM-RDM alignment; customs automation requires it |
| 6 | Party Identity & Roles | MEDIUM | ~8 | ~12 | LEI, KYC, sanctions screening |
| 7 | Procurement Lifecycle | MEDIUM | ~8 | ~15 | RFQ, order amendments, catalogues |
| 8 | Sustainability / Carbon | LOW | ~0–8 | ~5 | Separate ontology exists; cross-refs may suffice |

**Total estimated new content:** ~48–56 new classes, ~157 new properties/annotations

---

## Recommendations

### Recommendation 1: Enrich Trade Finance (Gap 1)
Add `FinancingRequest`, `FinancingSummary`, `RemittanceAdvice`, L/C type codes, and bank role object properties. Model factoring/forfaiting as properties on existing `LetterOfCredit` and `DocumentaryCollection`, not separate class hierarchies.

### Recommendation 2: Add EPCIS-Aligned Visibility Events (Gap 2)
Create a new `track-trace/` module with the 4 EPCIS event types. Add `bizStep`, `disposition`, `readPoint`, `bizLocation` properties. Use `rdfs:seeAlso` to GS1 EPCIS 2.0 URIs. Add `ConsignmentStatusReport` and `EquipmentStatusReport`.

### Recommendation 3: Add Cross-Domain rdfs:seeAlso (Gap 3)
Annotate ~15–20 BSP classes with `rdfs:seeAlso` pointing to equivalent DCSA, IMO, MMT, and WCO classes. Zero new classes — only annotations on existing ones.

### Recommendation 4: Enrich Document Properties (Gap 4)
Add B/L-specific, AWB-specific, CoO-specific, and CustomsDeclaration-specific properties. Add a shared `documentStatus` and `issuer` across all document types.

### Recommendation 5: Deepen Compliance Module (Gap 5)
Add `CustomsValuation`, `OriginCriterion`, separate procedure types, and sanctions properties. Align with WCO ontology via `rdfs:seeAlso`.

### Recommendation 6: Expand Party Identity (Gap 6)
Add `legalEntityIdentifier`, `taxIdentificationNumber`, `registrationCountry` properties. Add specialized bank roles and `InsuranceUnderwriter`, `TerminalOperator`.

### Recommendation 7: Complete Procurement Lifecycle (Gap 7)
Add `RequestForQuotation`, `OrderChange`, `OrderResponse`, `DemandForecast`, `ProductCatalogue`. Link to existing `Quotation`, `PurchaseOrder`, and `SalesOrder`.

### Recommendation 8: Cross-Reference Sustainability (Gap 8)
Add `rdfs:seeAlso` from `Shipment`, `TransportLeg`, `Product` to the Sustainability ontology. Defer integrated carbon modeling unless explicitly needed.

---

## Interaction with Other Kairos Ontologies

| BSP Concept | Other Ontology | Relationship | Action |
|-------------|---------------|-------------|--------|
| `Shipment` | DCSA `Shipment` | Same concept, maritime-specific in DCSA | rdfs:seeAlso |
| `Consignment` | MMT `Consignment` | Identical concept | rdfs:seeAlso |
| `TransportEquipment` | DCSA `Container` | Container is transport equipment | rdfs:seeAlso |
| `BillOfLading` | DCSA `TransportDocument` | B/L is a transport doc | rdfs:seeAlso |
| `CustomsDeclaration` | WCO `CustomsDeclaration` | Same concept | rdfs:seeAlso |
| `Port` | IMO `Port`, DCSA `Location` | Port/location | rdfs:seeAlso |
| `Carrier` | DCSA `Carrier` | Same party role | rdfs:seeAlso |
| `TariffClassification` | WCO `TariffClassification` | HS codes | rdfs:seeAlso |
| `DutyTax` | WCO `DutyTax` | Customs duty | rdfs:seeAlso |
| `TransportLeg` | MMT `TransportLeg` | Same concept | rdfs:seeAlso |
| `TransportService` | MMT `TransportService` | Same concept | rdfs:seeAlso |

---

## Notes

1. **BSP vs. MMT boundary**: The MMT ontology already covers multimodal transport in detail (consignment, transport means, equipment). BSP should NOT duplicate MMT transport entities — the `Ship` pillar's transport depth belongs in MMT. BSP's role is the commercial/transactional view of shipping.

2. **BSP vs. WCO boundary**: WCO already models customs deeply. BSP compliance should reference WCO, not replicate. New compliance classes (CustomsValuation, OriginCriterion) should be in BSP only if they represent the commercial perspective — the regulatory/government perspective stays in WCO.

3. **BSP vs. DCSA boundary**: DCSA owns container shipping specifics (booking, transport calls, events, vessel schedules). BSP models the cross-industry commercial transaction. The B/L in BSP is generic; DCSA's transport document is ocean-specific.

4. **Cost-accounting and revenue-yield modules** are Kairos-specific extensions beyond the BSP-RDM standard scope. They are well-structured and don't need gap-filling against the standard.

5. **Version note**: The VERSION file shows 1.2.0 but the README shows 1.0.0 — version documentation is out of sync.
