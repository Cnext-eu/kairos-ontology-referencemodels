# WCO Customs Ontology

**Namespace:** `http://kairos.ai/ont/wco#`  
**Version:** 1.0.0  
**Created:** 2026-05-16

## Description

World Customs Organization (WCO) ontology for international customs procedures and trade facilitation. Fully aligned with the WCO Data Model 3.0 and eFTI Regulation (EU) 2020/1056.

## Structure

```
WCO/
├── wco.ttl                                  # Root ontology (imports all modules)
├── customs/customs.ttl                      # Customs declarations and duty calculations
├── trade-facilitation/trade-facilitation.ttl # Certificates, permits, and trusted trader programmes
├── party/party.ttl                          # Party roles in customs processes
├── locations/locations.ttl                  # Customs locations and controlled areas
└── documents/documents.ttl                  # Customs and trade documents
```

## Domain Modules

### Customs (`http://kairos.ai/ont/wco/customs#`)
Customs declarations, duty calculations, tariff classifications, and filing procedures.

**Classes:** CustomsDeclaration, EntryExitSummary, ImportDeclaration, ExportDeclaration, TransitDeclaration, Filing, AuthorityMessage, InspectionReference, ICS2Reference, DeclarationStatus, DutyCalculation, TariffClassification, CustomsValue, PreferenceClaim

### Trade Facilitation (`http://kairos.ai/ont/wco/trade-facilitation#`)
Trade facilitation certificates, permits, and trusted trader programmes.

**Classes:** Certificate, CertificateOfOrigin, SPSCertificate, License, ImportPermit, ExportPermit, eFTIRecord, AEOCertification, TrustedTrader, SingleWindow, TradeAgreementReference

### Party (`http://kairos.ai/ont/wco/party#`)
Party roles in customs processes including declarants, authorities, and brokers.

**Classes:** Declarant, CustomsAuthority, CustomsBroker, Importer, Exporter, AEOHolder, FreightAgent, GuaranteeProvider

### Locations (`http://kairos.ai/ont/wco/locations#`)
Customs locations, border crossings, bonded facilities, and controlled areas.

**Classes:** CustomsOffice, BorderCrossing, BondedWarehouse, FreeZone, CustomsControlledArea, DesignatedExportPlace

### Documents (`http://kairos.ai/ont/wco/documents#`)
Customs and trade documents including declarations, permits, transit documents, and carnets.

**Classes:** CustomsDeclarationDocument, TransitDocument, ImportPermitDocument, ExportLicenseDocument, PreferentialOriginDoc, SADForm, T1Document, T2Document, ATACarnet, TIRCarnet

## Standards Alignment

- WCO Data Model 3.0
- eFTI Regulation (EU) 2020/1056
- EU Union Customs Code (UCC)
- ICS2 (Import Control System 2)
- TIR Convention
- ATA Carnet Convention
- WCO SAFE Framework of Standards

## Usage

```turtle
@prefix wco: <http://kairos.ai/ont/wco#> .

<http://example.org/my-ontology> a owl:Ontology ;
    owl:imports <http://kairos.ai/ont/wco#> .
```

Importing the root ontology (`wco.ttl`) automatically imports all domain modules.
