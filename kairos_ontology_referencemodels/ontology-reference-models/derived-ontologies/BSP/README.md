# BSP – Buy-Ship-Pay Domain Modules

Modular decomposition of the **ISO 20197-1:2024 Buy-Ship-Pay Reference Data Model** ontology into eight domain-specific OWL modules.

## Structure

```
BSP/
├── bsp.ttl                              # Root ontology – imports all 8 domains
├── party/party.ttl                      # Trade party roles, identity, and contact information
├── commercial/commercial.ttl            # Commercial transactions, procurement lifecycle, shipments
├── financial/financial.ttl              # Invoicing, charges, surcharges, tariffs, trade finance
├── documents/documents.ttl              # Trade, transport, and regulatory documents
├── compliance/compliance.ttl            # Regulatory requirements, tariffs, trade agreements
├── reference-data/reference-data.ttl    # Locations, measurements, code lists
├── cost-accounting/cost-accounting.ttl  # Transport cost allocation, budgets, cost-to-serve
├── revenue-yield/revenue-yield.ttl      # Revenue attribution, yield metrics, profitability
```

## Domain Modules

| Module | Namespace | Description |
|--------|-----------|-------------|
| **Party** | `https://www.kairosflow.ai/ont/bsp/party#` | TradeParty, Buyer, Seller, Carrier, Bank, FreightForwarder, CustomsBroker, InsuranceProvider, TerminalOperator, WarehouseKeeper + LEI/tax identity |
| **Commercial** | `https://www.kairosflow.ai/ont/bsp/commercial#` | PurchaseOrder, SalesOrder, Quotation, RequestForQuotation, OrderChange, OrderResponse, SalesContract, Shipment, Consignment, TransportService, BusinessEvent |
| **Financial** | `https://www.kairosflow.ai/ont/bsp/financial#` | Invoice, Charge, Surcharge (BAF/CAF/THC), FreightRate, TariffSchedule, Payment, LetterOfCredit (with L/C types), BankGuarantee, DocumentaryCollection, FinancingArrangement, RemittanceAdvice |
| **Documents** | `https://www.kairosflow.ai/ont/bsp/documents#` | Document, BillOfLading (with B/L properties), AirWaybill, CertificateOfOrigin, CustomsDeclaration, ImportLicense, ExportLicense, InspectionCertificate + document lifecycle |
| **Compliance** | `https://www.kairosflow.ai/ont/bsp/compliance#` | RegulatoryRequirement (with procedure types), TariffClassification, DutyTax (with duty types), TradeAgreement (with preferential rates) |
| **Reference Data** | `https://www.kairosflow.ai/ont/bsp/reference-data#` | Location, Address, Port, Airport, Warehouse, ManufacturingPlant, Country, Measurement, Weight, Volume |
| **Cost Accounting** | `https://www.kairosflow.ai/ont/bsp/cost-accounting#` | CostAllocation, CostCenter, TransportCostItem, CostPerUnit, BudgetItem, CostVariance, CostToServe |
| **Revenue & Yield** | `https://www.kairosflow.ai/ont/bsp/revenue-yield#` | RevenueItem, FreightRevenue, SurchargeRevenue, AncillaryRevenue, RevenuePerUnit, LoadFactor, RateCard, ContributionMargin, ProfitabilityScope, YieldAnalysis |

## Cross-Domain Alignment

The BSP ontology uses `rdfs:seeAlso` annotations to reference equivalent concepts in other Kairos reference models:

| BSP Concept | Related Concept | Relationship |
|-------------|----------------|-------------|
| `commercial:Shipment` | `dcsa/booking#Shipment` | Same concept (commercial vs. maritime view) |
| `commercial:Consignment` | `mmt/consignment#Consignment` | Identical concept |
| `commercial:TransportEquipment` | `dcsa/equipment#Container` | Container as transport equipment |
| `commercial:TransportService` | `mmt/consignment#TransportService` | Same concept |
| `commercial:TransportLeg` | `mmt/consignment#TransportLeg` | Same concept |
| `commercial:Product` | `sustainability/carbon#CarbonEmission` | Product carbon footprint |
| `commercial:Shipment` | `sustainability/carbon#CarbonFootprint` | Shipment carbon footprint |
| `documents:BillOfLading` | `dcsa/transport-documents#TransportDocument` | B/L is transport document |
| `documents:CustomsDeclaration` | `wco/customs#CustomsDeclaration` | Same concept |
| `reference-data:Port` | `imo/locations#Port`, `dcsa/locations#Location` | Port/location alignment |
| `party:Carrier` | `dcsa/party#Carrier` | Same party role |
| `party:CustomsBroker` | `wco/party#CustomsBroker` | Same party role |
| `compliance:TariffClassification` | `wco/customs#TariffClassification` | HS code alignment |
| `compliance:DutyTax` | `wco/customs#DutyCalculation` | Customs duty |
| `compliance:TradeAgreement` | `wco/trade-facilitation#TradeAgreementReference` | Trade agreement alignment |

## Design Principles

- **A module imports every module it references** — a property asserting `rdfs:domain`
  or `rdfs:range` against a class from another module requires that module in this
  module's transitive `owl:imports` closure. Enforced by `validate_structure.py` check 10.
- The **root `bsp.ttl`** is a pure aggregator: it declares no terms and imports all eight
  domains. A leaf module must never import the root.
- Each module uses its own namespace: `https://www.kairosflow.ai/ont/bsp/<domain>#`
- **Sibling imports may be cyclic, and that is accepted.** BSP genuinely cycles:
  `commercial → financial → commercial`, caused by `:relatedToShipment rdfs:domain
  fin:Invoice` living in the commercial module rather than the financial one. Both this
  repo's loader and the consumer's guard on already-visited paths, so a cycle costs at
  most one diagnostic and cannot drop triples. Relocating that property is tracked
  separately; it is a modelling change, not an import fix.
- Properties are distributed to the domain of their primary class

> **Changed in 2.5.0.** The first bullet previously read "no cross-imports between domain
> modules — each module is self-contained", with cross-domain alignment via `rdfs:seeAlso`.
> That was already untrue — `party.ttl` has imported `bsp/reference-data` since 1.5.0 — and
> the nineteen `rdfs:domain`/`rdfs:range` assertions against unimported sibling classes were
> silently dropped, making `financial#creditLimit`, `creditLimitCurrency`, `hasBankAccount`
> and `hasPartyPaymentTerms` unreachable from `party#TradeParty` (gh#97).

## Source

Derived from the monolithic `buy-ship-pay.ttl` ontology based on:

- **ISO 20197-1:2024** Buy-Ship-Pay Reference Data Model
- **UN/CEFACT** Multi-Modal Transport Reference Data Model
- **UN/CEFACT** Core Component Library D23B

## Versioning

- **Version:** 1.3.0
- **Created:** 2026-01-06
- **Last Modified:** 2026-06-13
- **Creator:** Kairos Ontology Team

## Changelog

### v1.3.0 (2026-06-13)
- **Cross-domain alignment**: Added ~16 `rdfs:seeAlso` annotations linking BSP to DCSA, MMT, IMO, WCO, and Sustainability ontologies
- **Documents enriched**: Added ~20 properties — shared lifecycle (documentStatus, issuingParty, signatoryName), B/L (placeOfIssue, numberOfOriginals, onBoardDate, negotiable), AWB (originAirport, destinationAirport, chargeableWeight), CoO (preferentialIndicator, originCriterion), CustomsDeclaration (declarationType, procedureCode, releaseDate)
- **Trade finance**: Added FinancingArrangement and RemittanceAdvice classes. Enriched LetterOfCredit with lcType, lcStatus, bank role properties (issuingBank, advisingBank, confirmingBank). Added collectionType to DocumentaryCollection, guaranteeType to BankGuarantee.
- **Procurement lifecycle**: Added RequestForQuotation, OrderChange, OrderResponse classes with linking properties
- **Compliance enriched**: Added procedureType, governmentAction to RegulatoryRequirement. Added agreementName, preferentialRate to TradeAgreement. Added hsDescription, hsChapter to TariffClassification. Added dutyType to DutyTax.
- **Party enriched**: Added InsuranceProvider, TerminalOperator, WarehouseKeeper subclasses. Added identity properties: legalEntityIdentifier (LEI), taxIdentificationNumber, registrationCountry, registrationNumber, dunsNumber.

### v1.2.0 (2026-05-16)
- Added cost-accounting and revenue-yield modules
- Silver extension templates moved to logistics accelerator blueprint (`client-hub-blueprint/examples/extensions/`)

### v1.0.0 (2026-01-06)
- Initial release with 6 core modules: Party, Commercial, Financial, Documents, Compliance, Reference Data
