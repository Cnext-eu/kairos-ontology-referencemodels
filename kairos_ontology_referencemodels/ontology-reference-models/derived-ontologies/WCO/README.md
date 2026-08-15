# WCO Customs Ontology

**Namespace:** `https://www.kairosflow.ai/ont/wco#`  
**Version:** 1.2.0  
**Created:** 2026-05-16  
**Modified:** 2026-06-13  
**Source:** WCO Data Model 3.10.0, WTO Customs Valuation Agreement, eFTI Regulation (EU) 2020/1056  
**Reference:** https://www.wcoomd.org/datamodel

## Description

World Customs Organization (WCO) ontology for international customs procedures and trade facilitation. Provides a comprehensive semantic framework covering customs declarations with goods-item-level detail, customs procedures (CPC codes), tariff classification, customs valuation with adjustment breakdown, duty calculation with type granularity, risk-based inspection, and cross-domain alignment with DCSA, MMT, BSP, and IMO ontologies.

## Structure

```
WCO/
├── wco.ttl                                  # Root ontology (imports all modules)
├── customs/customs.ttl                      # Declarations, goods items, procedures, duties
├── trade-facilitation/trade-facilitation.ttl # Certificates, permits, AEO, single window
├── party/party.ttl                          # Party roles incl. consignee/consignor
├── locations/locations.ttl                  # Customs locations and controlled areas
└── documents/documents.ttl                  # Customs and trade documents
```

## Domain Modules

### Customs (`https://www.kairosflow.ai/ont/wco/customs#`)
Customs declarations with goods-item-level detail, customs procedure codes, tariff classifications, customs valuation with adjustments, duty calculations with type granularity, filing, inspection with risk channels, and transport references.

**Classes:** CustomsDeclaration, EntryExitSummary, ImportDeclaration, ExportDeclaration, TransitDeclaration, Filing, AuthorityMessage, InspectionReference, ICS2Reference, DeclarationStatus, DutyCalculation, TariffClassification, CustomsValue, PreferenceClaim, **GoodsItem**, **Packaging**, **CustomsProcedure**

### Trade Facilitation (`https://www.kairosflow.ai/ont/wco/trade-facilitation#`)
Trade facilitation certificates, permits, and trusted trader programmes.

**Classes:** Certificate, CertificateOfOrigin, SPSCertificate, License, ImportPermit, ExportPermit, eFTIRecord, AEOCertification, TrustedTrader, SingleWindow, TradeAgreementReference

### Party (`https://www.kairosflow.ai/ont/wco/party#`)
Party roles in customs processes including declarants, authorities, brokers, and consignment parties.

**Classes:** Declarant, CustomsAuthority, CustomsBroker, Importer, Exporter, AEOHolder, FreightAgent, GuaranteeProvider, **Consignee**, **Consignor**

### Locations (`https://www.kairosflow.ai/ont/wco/locations#`)
Customs locations, border crossings, bonded facilities, and controlled areas.

**Classes:** CustomsOffice, BorderCrossing, BondedWarehouse, FreeZone, CustomsControlledArea, DesignatedExportPlace

### Documents (`https://www.kairosflow.ai/ont/wco/documents#`)
Customs and trade documents including declarations, permits, transit documents, and carnets.

**Classes:** CustomsDeclarationDocument, TransitDocument, ImportPermitDocument, ExportLicenseDocument, PreferentialOriginDoc, SADForm, T1Document, T2Document, ATACarnet, TIRCarnet

## Cross-Domain Alignment

| WCO Concept | Related Ontology | Related Concept |
|-------------|-----------------|-----------------|
| CustomsDeclaration | BSP | compliance:CustomsDeclaration |
| CustomsDeclaration | MMT | consignment:Consignment |
| EntryExitSummary | DCSA | transport-call:TransportCall |
| TariffClassification | BSP | compliance:hsCode |
| CertificateOfOrigin | BSP | compliance:CertificateOfOrigin, documents:CertificateOfOrigin |
| AEOCertification | BSP | compliance:ComplianceCertification |
| AEOHolder | BSP | compliance:ComplianceCertification |
| Importer | BSP | party:Buyer |
| Exporter | BSP | party:Seller |
| Consignee | BSP | party:Buyer |
| Consignor | BSP | party:Seller |
| FreightAgent | MMT | party:FreightForwarder |
| eFTIRecord | MMT | documents:TransportDocument |
| CustomsOffice | DCSA | locations:Facility |
| CustomsOffice | MMT | locations:Location |
| BorderCrossing | IMO | port-call:Port |
| BorderCrossing | DCSA | locations:UNLocationCode |
| CustomsDeclarationDocument | BSP | documents:BillOfLading |
| CustomsDeclarationDocument | DCSA | transport-documents:TransportDocument |
| GoodsItem | MMT | cargo:CargoItem |

## Standards Alignment

- WCO Data Model 3.10.0
- WTO Customs Valuation Agreement (Articles 1-7)
- Revised Kyoto Convention (customs procedures)
- eFTI Regulation (EU) 2020/1056
- EU Union Customs Code (UCC)
- ICS2 (Import Control System 2)
- TIR Convention
- ATA Carnet Convention
- WCO SAFE Framework of Standards
- Harmonized System (HS) nomenclature

## Usage

```turtle
@prefix wco: <https://www.kairosflow.ai/ont/wco#> .

<http://example.org/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/wco#> .
```

Importing the root ontology (`wco.ttl`) automatically imports all domain modules.

## Changelog

### v1.2.0 (2026-06-13)
- **NEW:** GoodsItem class — line-item-level goods declarations with commodity description, weight, origin, and links to tariff/valuation/duty
- **NEW:** Packaging class — package type, count, marks and numbers per goods item
- **NEW:** CustomsProcedure class — CPC codes covering normal and special procedures (warehousing, inward/outward processing, temporary admission, end-use)
- **NEW:** Consignee and Consignor classes in party module — distinct from Importer/Exporter for triangular trade
- **ENRICHED:** Declaration header properties — declarationType, functionCode, totalItems, totalPackages, totalGrossWeight, acceptanceDate, releaseDate, LRN, MRN, transport references (SAD Box 18-21)
- **ENRICHED:** CustomsValue — valuationBasis (CIF/FOB), freightCharges, insuranceCost, totalAdjustments, currencyCode, exchangeRate
- **ENRICHED:** DutyCalculation — dutyTypeCode (A00/B00/C00), dutyCalculationMethod, dutyRegimeCode, quotaOrderNumber, paymentMethodCode, defermentAccountNumber, paymentStatus
- **ENRICHED:** GuaranteeProvider — guaranteeType, validity period, currency, GRN
- **ENRICHED:** InspectionReference — riskChannel (green/yellow/red/blue), examinationType, examinationResult, inspectionDate
- **CROSS-DOMAIN:** Added ~15 rdfs:seeAlso annotations linking to BSP, DCSA, MMT, and IMO ontologies

### v1.1.0 (2026-05-21)
- Added trade-facilitation module (AEO, certificates, eFTI, single window)
- Initial release with 5 domain modules
