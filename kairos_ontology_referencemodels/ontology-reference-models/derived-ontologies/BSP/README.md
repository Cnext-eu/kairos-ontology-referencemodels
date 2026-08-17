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

- **A module imports what it domains on** — a property asserting `rdfs:domain` against a
  class from another module requires that module in this module's `owl:imports` closure.
  Six such imports were added at 2.5.0 (gh#97); before that the classes were untyped here
  and could not be anchored in the consuming data domain.
- The **root `bsp.ttl`** imports all eight domains via `owl:imports`; a leaf must never
  import the root.
- Each module uses its own namespace: `https://www.kairosflow.ai/ont/bsp/<domain>#`
- **The module graph is acyclic, deliberately.** `:relatedToShipment` moved to
  `bsp/financial` at 2.5.0 — it is domained on `fin:Invoice`, so it belongs there — which
  removed the only `commercial → financial → commercial` cycle. The cycle was harmless to
  the graph but made all four BSP modules mutually reachable, so any data domain importing
  one was offered all four.
- Cross-domain `rdfs:range` alignment stays unimported by design — see the MMT README for
  why. Annotation-only links use `rdfs:seeAlso`.
- Properties are distributed to the domain of their primary class

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
