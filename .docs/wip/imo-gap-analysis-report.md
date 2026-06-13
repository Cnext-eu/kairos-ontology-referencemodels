# IMO Maritime Ontology Gap Analysis Report

**Status:** DRAFT  
**Date:** 2026-06-12  
**Ontology:** IMO Maritime — v1.0.0  
**Standard:** IMO Compendium (FAL 48/49, 2024), SOLAS, MARPOL, STCW, MLC 2006, ISPS Code  
**Scope:** Systematic comparison of IMO Convention domains vs. current ontology coverage

---

## Executive Summary

The current IMO ontology (5 modules, ~53 classes) covers **vessel identity and port call
facilitation** well — vessel registration, dangerous goods, port call lifecycle, maritime
parties, and navigational locations. However, the IMO's regulatory framework rests on
**four pillars** — SOLAS, MARPOL, STCW, and MLC 2006 — and the current ontology only
represents SOLAS (partially) and MARPOL's DG annex. Three of the four pillars have
minimal or zero representation.

The most significant gaps are:

| Priority | Gap | Impact |
|----------|-----|--------|
| 🔴 CRITICAL | Certificates & Surveys (no certificate classes at all) | Central compliance artifact missing |
| 🔴 CRITICAL | Crew & Seafarer (only MasterOfVessel exists) | FAL Form 5 data set unrepresented |
| 🔴 CRITICAL | Environmental/MARPOL (only WasteDisposal exists) | 5 of 6 MARPOL annexes unrepresented |
| 🟠 HIGH | ISPS Maritime Security (no security concepts) | ISSC certificate required at every port call |
| 🟠 HIGH | Cargo Manifest / FAL Forms (FALForm too generic) | FAL Forms 3, 5, 6 need specific classes |
| 🟠 HIGH | Port State Control (no PSC concepts) | Key enforcement mechanism unmodeled |
| 🟠 HIGH | Maritime Single Window (MSW mandate since 2024) | FAL Convention's biggest recent change |
| 🟡 MEDIUM | Navigation (VoyagePlan, AIS data model) | SOLAS V/34 voyage planning |
| 🟡 MEDIUM | Insurance / Financial Security (statutory certificates) | CLC/Bunker Convention certificates |
| 🟢 LOW | IMO Compendium Data Set metadata model | Structural/meta-model concept |

**Cross-domain isolation:** The IMO ontology currently has **zero cross-references** to
DCSA, MMT, TIC, or WCO ontologies. Several concepts overlap (Port, Berth, Vessel,
DangerousGoods, CargoManifest) and should be aligned.

---

## Current Coverage Summary

### What We Have (5 modules, ~53 classes)

| Module | Classes | Cross-refs |
|--------|---------|------------|
| **Vessel Registry** | Vessel, Fleet, IMONumber, MMSI, CallSign, FlagState, ClassSociety, VesselType, VesselCapacity, GrossTonnage, NetTonnage, DeadweightTonnage, VesselOperationalStatus (13) | _(self-contained)_ |
| **Dangerous Goods** | DangerousGoodsItem, HazardClass, UNNumber, PackingGroup, FlashPoint, EmergencySchedule, SegregationRule, StowageCategory, EmergencyContact, DGDeclaration (10) | _(self-contained)_ |
| **Port Call** | Voyage, SeaLeg, PortCall, BerthStay, ArrivalNotice, DepartureNotice, FALForm, PortCallStatus, PilotageRequest, TowageRequest, BunkeringOperation, WasteDisposal, CrewChange (13) | _(self-contained)_ |
| **Party** | MaritimeParty, FlagAuthority, PortAuthority, ClassificationSociety, MasterOfVessel, ShipOwner, ShipManager, ShipOperator, MaritimeAgent, PilotService, TowageProvider (11) | → locations |
| **Locations** | MaritimeLocation, Port, Anchorage, VTSZone, PilotBoardingPlace, Berth, PortApproach, TrafficSeparationScheme (8) | _(self-contained)_ |

### What's Good
- Vessel identity is comprehensive (IMO number, MMSI, call sign, flag, class, tonnage, dimensions)
- Dangerous goods covers the full IMDG Code lifecycle (UN numbers → hazard classes → packing → stowage → segregation → emergency schedules → declaration)
- Port call has good lifecycle coverage (voyage → sea leg → port call → berth stay → arrival/departure → pilotage → towage → bunkering → waste → crew change)
- Party hierarchy is well-structured with clear maritime roles
- Locations cover the navigational infrastructure (port → anchorage → VTS → pilot boarding → berth → approach → TSS)

### What's Missing
- **No certificate classes at all** — the central compliance artifact in maritime regulation
- **No crew/seafarer classes** — only MasterOfVessel and the operational CrewChange
- **MARPOL represented only by DG** — 5 of 6 annexes (oil, NLS, sewage, garbage, air pollution) unmodeled
- **No security concepts** — ISPS Code entirely absent
- **FALForm is a single generic class** — should have specific subclasses for each of the 7 FAL forms
- **No cargo manifest or passenger list** — FAL Forms 3, 5, 6 missing
- **No energy efficiency** — EEDI/EEXI/CII mandatory since 2023, absent
- **No PSC inspection model** — the enforcement side of IMO conventions
- **Zero cross-domain references** — no alignment with DCSA, MMT, TIC, WCO ontologies

---

## Gap Analysis

### Gap 1: Certificates & Surveys — 🔴 CRITICAL

**IMO source:** SOLAS Chapter I (Reg. I/12–I/14), ISM Code §13, Load Line Convention 1966,
MARPOL Annex I/IV/VI, ISPS Code  
**Current state:** No certificate classes at all.

The certificate is the **central compliance artifact** in IMO's regulatory framework.
Virtually every PSC inspection, every port entry notification, and every FAL Compendium
data exchange involves certificates. The IMO Compendium Data Set DS2 (Vessel Certificates)
explicitly lists required certificate data elements.

| Missing Concept | Convention | Key Properties |
|----------------|-----------|----------------|
| **StatutoryCertificate** | SOLAS I | Abstract parent — certificateNumber, issueDate, expiryDate, issuingAuthority, vesselRef |
| **SafetyConstructionCertificate** | SOLAS I/12 | Cargo ship structural safety |
| **SafetyEquipmentCertificate** | SOLAS I/12 | Lifesaving appliances, fire equipment |
| **SafetyRadioCertificate** | SOLAS I/12 + GMDSS | Radio communications compliance |
| **PassengerShipSafetyCertificate** | SOLAS I/12 | Combined cert for passenger ships |
| **InternationalLoadLineCertificate** | LL Conv. 1966 | Freeboard/load line compliance |
| **InternationalOilPollutionPreventionCertificate** | MARPOL Ann. I Reg. 5 | IOPPC — checked at every PSC |
| **InternationalAirPollutionPreventionCertificate** | MARPOL Ann. VI Reg. 6 | IAPP certificate |
| **InternationalEnergyEfficiencyCertificate** | MARPOL Ann. VI Reg. 6 | IEE — contains EEDI/EEXI values |
| **InternationalSewagePollutionPreventionCertificate** | MARPOL Ann. IV Reg. 5 | ISPPC |
| **BallastWaterManagementCertificate** | BWM Conv. Art. 9 | IBWMC |
| **DocumentOfCompliance** | ISM Code §13.2 | Issued to company, 5-year validity |
| **SafetyManagementCertificate** | ISM Code §13.7 | Issued to individual ship, 5-year validity |
| **InternationalShipSecurityCertificate** | SOLAS XI-2/9 / ISPS | ISSC — proves SSP approved |
| **MinimumSafeManningDocument** | SOLAS V/14 | Required on board at all times |
| **CertificateOfClass** | IACS/Classification | Not statutory but gate to insurance/registration |
| **StatutorySurvey** | SOLAS I/7–10 | Initial, renewal, annual, intermediate surveys |

**Recommendation:** Create new module `certificates-surveys/certificates-surveys.ttl` with
`StatutoryCertificate` as abstract parent and specific subclasses per convention.

### Gap 2: Crew & Seafarer — 🔴 CRITICAL

**IMO source:** STCW Convention 1978 (Manila 2010), MLC 2006, FAL Form 5 (Crew List),
SOLAS V/14  
**Current state:** Only `MasterOfVessel` in party module and `CrewChange` in port-call.

MLC 2006 is one of the **four pillars** of international maritime law. FAL Form 5 (Crew
List) is one of the 7 mandatory FAL Convention forms and a core IMO Compendium data set
(DS4). The existing ontology has essentially zero crew/seafarer representation.

| Missing Concept | Convention | Key Properties |
|----------------|-----------|----------------|
| **Seafarer** | MLC 2006 Art. II | seafarerId, nationality, dateOfBirth, rank |
| **CrewMember** | FAL Form 5 | seafarerRef, position, embarkedAt, seamanBookNumber |
| **CrewList** | FAL Form 5 | listDate, vesselRef, portOfSubmission |
| **CertificateOfCompetency** | STCW Art. II | cocNumber, grade, issueDate, expiryDate, issuingCountry |
| **CertificateOfProficiency** | STCW Art. II | copNumber, specialFunction (SSO, GMDSS, tanker) |
| **STCWEndorsement** | STCW Reg. I/10 | Flag state endorsement of foreign CoC |
| **SeafarerMedicalCertificate** | MLC Reg. 1.2 / STCW A-I/9 | medicalFitnessClass, expiryDate |
| **MaritimeLabourCertificate** | MLC Title 5.1.3 | Certificate of Maritime Labour Compliance |
| **DeclarationOfMaritimeLabourCompliance** | MLC Title 5.1.3 | DMLC Parts I and II |
| **SafeManningDocument** | SOLAS V/14 | Minimum safe manning requirements |
| **SeafarerEmploymentAgreement** | MLC Reg. 2.1 | SEA / Articles of Agreement |
| **PassengerList** | FAL Form 6 | Passengers aboard for port call |
| **Passenger** | FAL Form 6 | passengerName, nationality, embarkedAt, disembarkedAt |

**Recommendation:** Create new module `crew-seafarer/crew-seafarer.ttl`.

### Gap 3: Environmental Compliance / MARPOL — 🔴 CRITICAL

**IMO source:** MARPOL 73/78 (all 6 annexes), BWM Convention 2004, MARPOL Annex VI
Chapter 4 (EEDI/EEXI/CII)  
**Current state:** Only `WasteDisposal` in port-call (minimal) and `DGDeclaration` for
MARPOL Annex III overlap.

MARPOL has six annexes covering oil, noxious liquids, harmful packaged substances, sewage,
garbage, and air pollution. Five of six are unrepresented. Since January 2023, the
CII (Carbon Intensity Indicator) is mandatory for all ships ≥5000 GT, and EEDI/EEXI
values must appear on the IEE certificate. EU ETS (2023) requires emissions reporting
at every EU port call.

| Missing Concept | Convention | Key Properties |
|----------------|-----------|----------------|
| **OilRecordBook** | MARPOL Ann. I Reg. 17/36 | Part I (machinery) and Part II (cargo) |
| **ShipboardOilPollutionEmergencyPlan** | MARPOL Ann. I Reg. 37 | SOPEP — mandatory emergency plan |
| **GarbageManagementPlan** | MARPOL Ann. V Reg. 10 | Ship waste management plan |
| **GarbageRecordBook** | MARPOL Ann. V Reg. 10 | Log of garbage disposals |
| **BallastWaterManagementPlan** | BWM Conv. Reg. B-1 | BWMP — ballast water procedures |
| **BallastWaterRecordBook** | BWM Conv. Reg. B-2 | Record of ballast operations |
| **ShipEnergyEfficiencyManagementPlan** | MARPOL Ann. VI Reg. 22 | SEEMP (Part I/II/III) |
| **EnergyEfficiencyDesignIndex** | MARPOL Ann. VI Reg. 20/21 | EEDI — gCO₂/tonne-mile for new ships |
| **EnergyEfficiencyExistingShipIndex** | MARPOL Ann. VI Reg. 23 | EEXI — attained vs. required for existing ships |
| **CarbonIntensityIndicator** | MARPOL Ann. VI Reg. 24/28 | CII — annual operational carbon intensity |
| **CIIRating** | MARPOL Ann. VI Reg. 28 | Annual rating A/B/C/D/E |
| **EmissionControlArea** | MARPOL Ann. VI Reg. 14 | ECA for SOx/NOx (North Sea, Baltic, etc.) |
| **MARPOLSpecialArea** | MARPOL all annexes | Special areas with stricter discharge limits |
| **PortReceptionFacility** | MARPOL all annexes | Shore facility for receiving ship-generated waste |
| **NoxiousLiquidSubstance** | MARPOL Ann. II | Categories X, Y, Z, OS |
| **WastePreNotification** | FAL.5/Circ.42-Rev.2 | MARPOL waste delivery pre-notification |

**Recommendation:** Create new module `environmental/environmental.ttl` covering
MARPOL record books, management plans, energy efficiency indices, pollution zones,
and waste notification.

### Gap 4: ISPS Maritime Security — 🟠 HIGH

**IMO source:** SOLAS Chapter XI-2, ISPS Code Part A (mandatory)  
**Current state:** No security concepts at all.

The ISPS Code defines the international framework for maritime security. The International
Ship Security Certificate (ISSC) is a mandatory document verified at every port call
and PSC inspection.

| Missing Concept | ISPS Code | Key Properties |
|----------------|----------|----------------|
| **SecurityLevel** | Part A §2 | Level 1 (normal), 2 (heightened), 3 (exceptional) |
| **ShipSecurityPlan** | Part A §9 | Confidential plan, approved by flag state/RO |
| **PortFacilitySecurityPlan** | Part A §16 | PFSP, approved by contracting government |
| **ShipSecurityAssessment** | Part A §8 | Threat/vulnerability assessment precursor to SSP |
| **PortFacilitySecurityAssessment** | Part A §15 | Precursor to PFSP |
| **DeclarationOfSecurity** | Part A §5 | Bilateral document between ship & port facility |
| **CompanySecurityOfficer** | Part A §11 | CSO — party role |
| **ShipSecurityOfficer** | Part A §12 | SSO — party role |
| **PortFacilitySecurityOfficer** | Part A §17 | PFSO — party role |

**Recommendation:** Create new module `maritime-security/maritime-security.ttl` for plans,
assessments, and DeclarationOfSecurity. Add CSO/SSO/PFSO as subclasses of `MaritimeParty`
in the party module.

### Gap 5: Cargo Manifest & FAL Form Specialization — 🟠 HIGH

**IMO source:** FAL Convention Forms 3 (Cargo Declaration), 5 (Crew List), 6 (Passenger
List); SOLAS VI/2 (VGM); IMSBC/IBC/IGC Codes  
**Current state:** `FALForm` exists as a single generic class with only `falFormNumber`.

The FAL Convention defines 7 specific forms, each with distinct data elements. The
current generic `FALForm` class loses the structural distinctions between cargo
declarations, crew lists, stores declarations, and passenger lists.

| Missing Concept | FAL Form | Key Properties |
|----------------|---------|----------------|
| **CargoManifest** | FAL Form 3 | manifestDate, totalItems, totalWeight |
| **CargoItem** | FAL Form 3 data element | description, weight, volume, marks |
| **ShipsStoresDeclaration** | FAL Form 4 | storesType, quantity |
| **PassengerList** | FAL Form 6 | listDate, totalPassengers |
| **Passenger** | FAL Form 6 data element | name, nationality, embarkedAt |
| **VerifiedGrossMass** | SOLAS VI/2 | VGM value, method (weighing/calculation), signatoryName |
| **BulkCargo** | IMSBC Code | cargoType, moisture content, stowage factor |
| **LiquidBulkCargo** | IBC Code | chemicalName, IMO Category |
| **LiquefiedGasCargo** | IGC Code | gasType, temperature, pressure |

**Recommendation:** Create subclasses of FALForm in port-call module or create separate
`cargo/cargo.ttl` module for manifest and cargo type classes. Move PassengerList to
crew-seafarer module.

### Gap 6: Port State Control — 🟠 HIGH

**IMO source:** IMO Resolution A.1138(31), Paris MOU, Tokyo MOU  
**Current state:** No PSC concepts at all.

PSC is the **primary enforcement mechanism** for every IMO convention. Every commercial
vessel visiting a foreign port is subject to PSC inspection. Detention records affect
vessel insurance, chartering, and reputation.

| Missing Concept | Source | Key Properties |
|----------------|--------|----------------|
| **PSCInspection** | Paris/Tokyo MOU | inspectionDate, portOfInspection, outcome |
| **PSCDeficiency** | Paris/Tokyo MOU | deficiencyCode, conventionReference, actionRequired |
| **PSCDetention** | Paris/Tokyo MOU | detentionDate, releaseDate, detentionReason |
| **PSCReport** | Paris/Tokyo MOU | reportNumber, inspectionRef |
| **PSCRegime** | Multiple MOUs | regimeName, memberStates |
| **PortStateControlOfficer** | Paris/Tokyo MOU | Party role for PSCO |

**Recommendation:** Create new module `port-state-control/port-state-control.ttl`.

### Gap 7: Maritime Single Window (MSW) — 🟠 HIGH

**IMO source:** FAL Convention 2022 amendments (Res. FAL.14(46)), mandatory since 1 January
2024  
**Current state:** No MSW concepts.

The MSW mandate is the **biggest recent regulatory change** in FAL Convention history.
All port states must implement a Maritime Single Window for electronic data exchange.
The IMO Compendium defines the data sets for MSW interoperability.

| Missing Concept | Source | Key Properties |
|----------------|--------|----------------|
| **PreArrivalNotification** | FAL Convention | Structured pre-arrival data set |
| **PortHealthDeclaration** | FAL/WHO IHR | Health status declaration |
| **WastePreNotification** | FAL.5/Circ.42-Rev.2 | MARPOL waste pre-notification |
| **ElectronicPortClearance** | FAL Convention | Clearance decision document |

**Recommendation:** Extend port-call module with specific notification/clearance classes.
Do NOT model MSW as a system class — it's IT architecture, not a domain entity.

### Gap 8: Navigation — 🟡 MEDIUM

**IMO source:** SOLAS Chapter V (Safety of Navigation), V/34 (voyage planning), V/19
(carriage requirements)  
**Current state:** Partially covered via VTSZone, PilotBoardingPlace, PortApproach.

| Missing Concept | Source | Key Properties |
|----------------|--------|----------------|
| **VoyagePlan** | SOLAS V/34 | Mandatory passage plan before departure |
| **RouteWaypoint** | SOLAS V/34 | Individual point in voyage plan |
| **VoyageDataRecorder** | SOLAS V/20 | VDR — black box equipment |
| **LRITTransponder** | SOLAS V/19-1 | Long Range Identification & Tracking |

**Recommendation:** Add VoyagePlan and RouteWaypoint to port-call module. VDR and LRIT
are equipment concepts that could extend vessel-registry. AIS position data is real-time
operational — skip for reference model. AIS static data already overlaps with vessel
registry fields.

### Gap 9: Insurance / Financial Security — 🟡 MEDIUM

**IMO source:** CLC 1992 Protocol, Bunker Convention 2001, MLC 2006 Reg. 2.5/4.2  
**Current state:** No insurance or financial security concepts.

| Missing Concept | Source | Key Properties |
|----------------|--------|----------------|
| **CLCCertificateOfInsurance** | CLC 1992 Protocol | Oil tanker pollution liability |
| **BunkerInsuranceCertificate** | Bunker Convention 2001 | All ships ≥1000 GT |
| **MLCFinancialSecurityCertificate** | MLC 2006 Reg. 4.2 | Seafarer claims coverage |

**Recommendation:** Add as certificate subclasses in the certificates-surveys module.
Commercial insurance (H&M, P&I) is financial/commercial domain — OUT OF SCOPE for
an IMO reference model.

### Gap 10: IMO Compendium Data Set Structure — 🟢 LOW

**IMO source:** IMO Compendium on Facilitation and Electronic Business (FAL 48/49)  
**Current state:** No meta-model for Compendium data sets.

| Missing Concept | Source | Key Properties |
|----------------|--------|----------------|
| **CompendiumDataSet** | IMO Compendium | Named data set grouping (e.g., "Crew List Data Set") |
| **CompendiumDataElement** | IMO Compendium | Individual element with name, definition, format |

**Recommendation:** OUT OF SCOPE for reference model. This is a meta-model describing
the Compendium's own structure, not domain entities. The ontology already represents
the *content* of these data sets through its classes and properties.

---

## Cross-Domain Isolation Analysis

The IMO ontology currently has **zero cross-references** to other derived ontologies.
This is a significant structural gap:

| IMO Concept | Overlapping Ontology | Nature of Overlap |
|-------------|---------------------|-------------------|
| Port | DCSA `locations#Port`, MMT `locations#Port` | Same entity — port from different perspectives |
| Berth | DCSA `locations#Berth`, TIC `locations#Berth`, TIC `terminal-infrastructure#Berth` | Same physical structure |
| Vessel | DCSA `transport-call#VesselTransportCall` (references), MMT `transport-means#Vessel` | Same entity |
| DangerousGoodsItem | MMT `cargo#DangerousGoods` | IMDG classification overlap |
| Voyage/SeaLeg | DCSA `schedule#SailingSchedule` | Same carrier journey |
| CargoManifest (missing) | DCSA `transport-documents#TransportDocument` | Shipping document overlap |
| FlagState | WCO `party#GovernmentAgency` | Overlapping government role |
| PortAuthority | TIC `party#TerminalOperator` (tangential) | Port governance |

**Recommendation:** Add `rdfs:seeAlso` annotations to align overlapping concepts.
Don't create `owl:imports` (keeps modules independently loadable).

---

## IMO Compendium Data Set Coverage Check

The IMO Compendium defines 14+ named data sets. Current coverage:

| Compendium Data Set | Current Coverage | Gap |
|---------------------|-----------------|-----|
| DS1: Vessel Particulars | ✅ Well-covered | Minor |
| DS2: Vessel Certificates | ❌ No certificate classes | 🔴 CRITICAL |
| DS3: Voyage Information | ✅ Partially covered | Minor |
| DS4: Crew List (FAL Form 5) | ❌ No Seafarer/CrewMember | 🔴 CRITICAL |
| DS5: Passengers (FAL Form 6) | ❌ No Passenger class | 🔴 CRITICAL |
| DS6: Cargo (FAL Form 3) | ⚠️ FALForm only, no cargo | 🟠 HIGH |
| DS7: Ship Stores (FAL Form 4) | ❌ No StoresItem class | 🟠 HIGH |
| DS8: Dangerous Goods (FAL Form 7) | ✅ Well-covered | Minor |
| DS9: Waste Pre-notification | ⚠️ WasteDisposal minimal | 🟠 HIGH |
| DS10: Maritime Security | ❌ No security concepts | 🟠 HIGH |
| DS11: Port Health | ❌ No health declaration | 🟡 MEDIUM |
| DS12: Border Control | ❌ No immigration concepts | 🟡 MEDIUM |
| DS13: Customs (Cargo) | ⚠️ WCO module scope | 🟡 MEDIUM |
| DS14: Hazardous Materials | ✅ Via DG module | Minor |

---

## Priority Summary

### Tier 1 — Structural Gaps (should be in any IMO reference model)
1. 🔴 **Certificates & Surveys** — the central compliance artifact, zero coverage
2. 🔴 **Crew & Seafarer** — STCW + MLC 2006 (two of four IMO pillars)
3. 🔴 **Environmental / MARPOL** — 5 of 6 annexes + EEDI/EEXI/CII

### Tier 2 — Operational Depth (enriches existing model significantly)
4. 🟠 **ISPS Maritime Security** — ISSC, SSP, security levels
5. 🟠 **Cargo Manifest & FAL Form Specialization** — FAL Forms 3, 5, 6
6. 🟠 **Port State Control** — PSC inspections, deficiencies, detentions
7. 🟠 **Maritime Single Window** — pre-arrival notifications, port health

### Tier 3 — Domain Extensions (valuable additions)
8. 🟡 **Navigation** — VoyagePlan, RouteWaypoint, VDR
9. 🟡 **Financial Security Certificates** — CLC, Bunker, MLC certificates

### Tier 4 — Skip or Defer
10. 🟢 **Compendium Meta-Model** — data set structure, not domain entities
11. 🟢 **AIS Position Data** — real-time operational, not reference model
12. 🟢 **Commercial Insurance (H&M, P&I)** — financial/commercial domain

---

## Estimated Scope (if all Tier 1-3 implemented)

| Area | New Classes | New Properties | New/Modified Files |
|------|------------|----------------|-------------------|
| Certificates & Surveys | ~17 | ~12 | 1 new module |
| Crew & Seafarer | ~13 | ~18 | 1 new module |
| Environmental / MARPOL | ~16 | ~14 | 1 new module |
| ISPS Maritime Security | ~9 | ~8 | 1 new module |
| Cargo Manifest / FAL Forms | ~9 | ~12 | 1 new or extend port-call |
| Port State Control | ~6 | ~10 | 1 new module |
| MSW / Port Notifications | ~4 | ~6 | 1 modified (port-call) |
| Navigation | ~4 | ~6 | 1 modified (port-call) |
| Financial Security Certs | ~3 | ~4 | In certificates module |
| Cross-domain alignment | 0 | ~8 annotations | Multiple |
| **Total** | **~81** | **~98** | **~10** |

---

## Recommendations

### R1: Create Certificates & Surveys module (CRITICAL)
New module `certificates-surveys/certificates-surveys.ttl` with `StatutoryCertificate`
as abstract parent. Define ~15 specific certificate subclasses per SOLAS, MARPOL,
ISM, ISPS. Add `StatutorySurvey` class (initial, renewal, annual, intermediate).
Link certificates to Vessel via object properties.

### R2: Create Crew & Seafarer module (CRITICAL)
New module `crew-seafarer/crew-seafarer.ttl` with `Seafarer`, `CrewMember`, `CrewList`,
certificates of competency/proficiency, `PassengerList`, `Passenger`. Link to Vessel
and PortCall via object properties.

### R3: Create Environmental Compliance module (CRITICAL)
New module `environmental/environmental.ttl` with MARPOL record books, management
plans, energy efficiency indices (EEDI/EEXI/CII/CIIRating), `EmissionControlArea`,
`MARPOLSpecialArea`, `PortReceptionFacility`. Add `BallastWaterManagementPlan`,
`BallastWaterRecordBook`.

### R4: Create Maritime Security module (HIGH)
New module `maritime-security/maritime-security.ttl` with `SecurityLevel`, `ShipSecurityPlan`,
`PortFacilitySecurityPlan`, `DeclarationOfSecurity`. Add CSO/SSO/PFSO party roles
to party module.

### R5: Enrich Port Call with FAL Form specialization (HIGH)
Add FAL Form subclasses: `CargoDeclaration` (Form 3), `ShipsStoresDeclaration` (Form 4),
`CrewListForm` (Form 5), `PassengerListForm` (Form 6). Add `CargoManifest`, `CargoItem`,
`VerifiedGrossMass`. Add `VoyagePlan`, `RouteWaypoint`.

### R6: Create Port State Control module (HIGH)
New module `port-state-control/port-state-control.ttl` with `PSCInspection`,
`PSCDeficiency`, `PSCDetention`, `PSCReport`, `PSCRegime`. Add `PortStateControlOfficer`
to party module.

### R7: Extend Port Call with MSW concepts (HIGH)
Add `PreArrivalNotification`, `PortHealthDeclaration`, `WastePreNotification`,
`ElectronicPortClearance` to port-call module.

### R8: Add Navigation concepts (MEDIUM)
Add `VoyagePlan`, `RouteWaypoint` to port-call module. Add VDR/LRIT as vessel-registry
extensions.

### R9: Add Financial Security certificates (MEDIUM)
Add `CLCCertificateOfInsurance`, `BunkerInsuranceCertificate`,
`MLCFinancialSecurityCertificate` as subclasses in certificates-surveys module.

### R10: Add cross-domain alignment (MEDIUM)
Add `rdfs:seeAlso` on overlapping IMO concepts pointing to DCSA, MMT, TIC, WCO IRIs.
Document alignment in README.

### R11: Extend Locations with environmental zones (MEDIUM)
Add `EmissionControlArea`, `MARPOLSpecialArea`, `PortReceptionFacility` to locations
module.

---

## Four Pillars Representation

International maritime law rests on four pillars. Current coverage:

| Pillar | Convention | Current Coverage | Gap |
|--------|-----------|-----------------|-----|
| **Safety** | SOLAS | ✅ Partially (vessel registry, port call) | Certificates, navigation |
| **Pollution** | MARPOL | ⚠️ DG annex only | 5 of 6 annexes, energy efficiency |
| **Training** | STCW | ❌ Only MasterOfVessel | Full crew/seafarer model |
| **Labour** | MLC 2006 | ❌ Nothing | Maritime labour certificates, SEA |

A comprehensive IMO reference-model ontology should represent all four pillars
proportionally.
