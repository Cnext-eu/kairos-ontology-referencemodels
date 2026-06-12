# DCSA Reference Model — Comprehensive Gap Analysis Report

**Date:** 2026-06-12
**Scope:** All DCSA OpenAPI specifications vs. current Kairos DCSA reference-model ontology (v1.0.0)
**Methodology:** Systematic review of DCSA OpenAPI GitHub repo (domain/dcsa v3.1.1, domain/event v3.2.0, BKG v2, EBL v3, TNT v3, OVS v3) against all current DCSA TTL modules.

---

## Executive Summary

The current DCSA reference-model ontology captures the **high-level entity structure** well
(Booking, Shipment, Events, Equipment, Locations, Parties, Schedules) but is **missing
significant operational vocabulary** from the DCSA standard — particularly around:

1. **TransportCall model** — the central linking concept between events, schedules, and transport means, entirely absent
2. **Inland/intermodal transport vocabulary** — mode-specific transport calls, plan stages, facility types
3. **Booking operational properties** — receipt/delivery types, shipment location types, incoterms detail
4. **Event enrichment** — customs/border crossing events, operations events, reefer/IoT events
5. **Dangerous goods detail** — extensive DG properties added in Domain v3.1.0

---

## Gap Matrix

### 1. TransportCall Model (CRITICAL — Entirely Missing)

**Source:** Event Domain v3.1.0, OVS v3, TNT v3
**Impact:** HIGH — TransportCall is the central linking concept in the DCSA model

| Missing Concept | DCSA Source | Type | Description |
|----------------|------------|------|-------------|
| `TransportCall` | Event Domain v3.1.0 | Class | Links a transport means (vessel, barge, rail, truck) to a facility at a specific point in a journey |
| `vesselTransportCall` | Event Domain v3.1.0 | Class | Vessel-specific transport call with vessel properties |
| `railTransportCall` | Event Domain v3.1.0 | Class | Rail-specific transport call |
| `truckTransportCall` | Event Domain v3.1.0 | Class | Truck-specific transport call |
| `bargeTransportCall` | Event Domain v3.1.0 | Class | Barge-specific transport call with barge identity |
| `transportCallReference` | Event Domain v3.0.0 | Property | Unique reference for transport call (replaced transportCallID) |
| `modeOfTransport` | DCSA Domain v3.1.0 | Property | Transport mode: VESSEL, BARGE, RAIL, TRUCK (string, max 50 chars) |
| `portVisitReference` | Event Domain v2.0.2 | Property | Reference to the port visit associated with a transport call |
| `transportCallSequenceNumber` | DCSA Domain v2.0.0 | Property | Sequence number of the transport call in a voyage |

**Recommended placement:** New sub-module `DCSA/current/shared-kernel/transport-call/transport-call.ttl`

---

### 2. Barge Identity Fields (Missing)

**Source:** DCSA Domain v3.0.0+
**Impact:** HIGH — Essential for intermodal/RoRo operators

| Missing Concept | DCSA Source | Type | Description |
|----------------|------------|------|-------------|
| `bargeCallSignNumber` | DCSA Domain v3.0.0 | DatatypeProperty | Radio call sign of the barge |
| `bargeFlag` | DCSA Domain v3.0.0 | DatatypeProperty | Flag state of the barge (2-letter country code) |
| `bargeName` | DCSA Domain v3.0.0 | DatatypeProperty | Name of the barge vessel |
| `bargeOperatorCarrierCode` | DCSA Domain v3.0.0 | DatatypeProperty | SCAC or other carrier code for barge operator |
| `bargeOperatorCarrierCodeListProvider` | DCSA Domain v3.0.0 | DatatypeProperty | Code list provider for barge operator code (SMDG, NMFTA) |

**Recommended placement:** Could go in `shared-kernel/equipment/` or in the new `transport-call/` module, as properties of `bargeTransportCall`.

---

### 3. Transport Plan Stages (Missing)

**Source:** DCSA Domain v2.0.0 (BKG v1.0+)
**Impact:** HIGH — Defines the formal stage classification for journey segments

| Missing Concept | DCSA Source | Type | Description |
|----------------|------------|------|-------------|
| `transportPlanStage` | DCSA Domain v2.0.0 | DatatypeProperty | Stage classification: PRC (Pre-Carriage), MNC (Main Carriage), ONC (On-Carriage) |
| `transportPlanStageSequenceNumber` | DCSA Domain v2.0.0 | DatatypeProperty | Sequence number within a transport plan stage |

**Recommended placement:** `shared-kernel/transport-call/transport-call.ttl` or `shipment-journey/booking/booking.ttl`

---

### 4. Receipt/Delivery Type Codes (Missing)

**Source:** DCSA Domain v2.0.1+
**Impact:** MEDIUM-HIGH — Important for door-to-door logistics

| Missing Concept | DCSA Source | Type | Description |
|----------------|------------|------|-------------|
| `receiptTypeAtOrigin` | BKG v2.0.0 | DatatypeProperty | **Formal enum:** CY (Container Yard incl. rail ramp), SD (Store Door), CFS (Container Freight Station). **Required** on booking. |
| `deliveryTypeAtDestination` | BKG v2.0.0 | DatatypeProperty | **Formal enum:** CY, SD, CFS. **Required** on booking. |
| `cargoMovementTypeAtOrigin` | DCSA Domain v2.0.0 | DatatypeProperty | FCL (Full Container Load), LCL (Less than Container Load) |
| `cargoMovementTypeAtDestination` | DCSA Domain v2.0.0 | DatatypeProperty | FCL, LCL |
| `requestedPreCarriageModeOfTransport` | BKG v2.0.2 (Jul 2025) | DatatypeProperty | Shipper-requested pre-carriage mode: VESSEL, RAIL, TRUCK, BARGE, RAIL_TRUCK, BARGE_TRUCK, BARGE_RAIL, MULTIMODAL |
| `requestedOnCarriageModeOfTransport` | BKG v2.0.2 (Jul 2025) | DatatypeProperty | Shipper-requested on-carriage mode (same values) |
| `Transport` (schema) | BKG v2.0.0 | Class | A single leg of the carrier-confirmed transport plan — with transportPlanStage, modeOfTransport, load/discharge locations, planned dates |

**Recommended placement:** `shipment-journey/booking/booking.ttl`

---

### 5. Shipment Location Type Codes (Partially Missing)

**Source:** DCSA Domain v2.0.0+
**Impact:** MEDIUM-HIGH — Our locations module has the classes but not the type code vocabulary

| Missing Code | Description | Currently In Ontology? |
|-------------|-------------|----------------------|
| PRE | Place of Receipt | ✅ As class `PlaceOfReceipt` — but no code property |
| POL | Port of Loading | ✅ As class `PortOfLoading` — but no code property |
| POD | Port of Discharge | ✅ As class `PortOfDischarge` — but no code property |
| PDE | Place of Delivery | ✅ As class `PlaceOfDelivery` — but no code property |
| PSR | Pre-carriage under shipper's responsibility | ❌ |
| PCF | Pre-carriage From | ❌ |
| OIR | Onward In-land Routing | ❌ |
| ORI | Origin of goods | ❌ |
| IEL | Container intermediate export stop-off location | ❌ |
| PTP | Prohibited transshipment port | ❌ |
| RTP | Requested transshipment port | ❌ |
| FCD | Full container drop-off location | ❌ |
| ECP | Empty container pick-up date and time | ❌ |
| DRL | Depot release location | ❌ |
| FDE | Final destination | ❌ |
| ROU | Route reference (v2.0.3) | ❌ |

**Recommended placement:** `shared-kernel/locations/locations.ttl` — add `shipmentLocationTypeCode` property and missing location type classes.

---

### 6. Facility Type Codes (Missing)

**Source:** DCSA Domain v1.0.3+ through v3.0.0
**Impact:** MEDIUM-HIGH — Essential for inland terminal classification

| Missing Code | Version Added | Description | 
|-------------|--------------|-------------|
| Code | Version | Description |
|------|---------|-------------|
| BOCR | Event Domain v3.2.0 | Border crossing |
| CLOC | Event Domain v3.2.0 | Customer location |
| COFS | Event Domain v3.2.0 | Container freight station |
| OFFD | Event Domain v3.2.0 | Off-dock storage |
| DEPO | Event Domain v3.2.0 | Depot |
| INTE | Event Domain v3.2.0 | Inland terminal |
| POTE | Event Domain v3.2.0 | Port terminal |
| RAMP | Event Domain v3.2.0 | Rail ramp |
| WAYP | Event Domain v3.2.0 | Waypoint |
| BRTH | OVS v3.0.2 | Berth (OVS timestamps) |
| PBPL | OVS v3.0.2 | Pilot boarding place (OVS timestamps) |
| ANCH | DCSA Domain v2.0.1 | Anchorage |

**Note:** The `facilityTypeCode` has a **formal `enum:`** in Event Domain v3.2.0 with 9 values.

Our `locations.ttl` has a `facilityCode` property on Terminal but NO `facilityTypeCode` property and no representation of the facility type vocabulary.

**Recommended placement:** `shared-kernel/locations/locations.ttl` — add `facilityTypeCode` property and inland facility subclasses.

---

### 7. Event Enrichment (Partially Missing)

**Source:** Event Domain v3.0.0 through v3.2.0
**Impact:** MEDIUM-HIGH

#### 7a. Missing Equipment Event Type Codes

| Missing Code | Version Added | Description |
|-------------|--------------|-------------|
| CROS | v3.0.0 | Crossed (border crossing) |
| AVPU | v3.0.0 | Available for Pick-up |
| AVDO | v3.0.0 | Available for Drop-off |
| CUSS | v3.0.0 | Customs Selected for Scan |
| CUSI | v3.0.0 | Customs Selected for Inspection |
| CUSR | v3.0.0 | Customs Released |
| PICK | v1.0.4 | Picked up |
| DROP | v1.0.4 | Dropped off |
| INSP | v1.0.4 | Inspected |
| RSEA | v1.0.4 | Resealed |
| RMVD | v1.0.4 | Removed |

Our events module only has: GateIn, GateOut, LoadedOnVessel, DischargedFromVessel, EmptyContainerPickup, EmptyContainerReturn. Many event types are missing.

#### 7b. Missing Event Infrastructure

| Missing Concept | Source | Description |
|----------------|--------|-------------|
| TransportCall linkage on events | Event Domain v2.0.0+ | Events should reference TransportCall |
| `facilityTypeCode` on events | Event Domain v2.0.0+ | Facility type at event location |
| `isTransshipmentMove` | Event Domain v3.0.0 | Boolean flag on equipment events |
| `relatedDocumentReferences` | Event Domain v3.0.0 | Array of related document references |
| `publisher` / `publisherRole` | Event Domain v3.1.0 | Who published the event |

#### 7c. Missing Event Types (Entire Categories)

| Missing Event Category | Source | Description |
|-----------------------|--------|-------------|
| `OperationsEvent` | Event Domain v1.1.0+ | Port call operations (mooring, pilotage, towage) |
| `ReeferEvent` | Event Domain v3.1.0 | Temperature monitoring events |
| `IoTEvent` | Event Domain v3.1.0 | IoT sensor events |
| Port call service types | Event Domain v1.1.1+ | FAST, GWAY, LASH, SAFE, ANCO, SLUG, SHPW, LCRO, DCRO, VRDY |

**Recommended placement:** Expand `track-and-trace/events/events.ttl` with missing event type subclasses, add TransportCall linkage.

---

### 8. Pre/On-Carriage on Transport Documents (Missing)

**Source:** DCSA Domain v3.0.0+, EBL v3
**Impact:** MEDIUM

| Missing Concept | Source | Type | Description |
|----------------|--------|------|-------------|
| `preCarriageBy` | EBL v3 | DatatypeProperty | Mode of pre-carriage transport (VESSEL, RAIL, TRUCK, BARGE, MULTIMODAL) |
| `onCarriageBy` | EBL v3 | DatatypeProperty | Mode of on-carriage transport |

**Note:** The `preCarriageUnderShippersResponsibility` property was present in earlier Domain versions but was **deleted** in v3.1.0. The `PSR` shipment location type code replaces it.

**Recommended placement:** `shipment-journey/transport-documents/transport-documents.ttl`

---

### 8b. Onward Inland Routing (Missing)

**Source:** EBL v3.0.3+
**Impact:** MEDIUM — Explicit inland routing beyond Port of Discharge

| Missing Concept | Source | Type | Description |
|----------------|--------|------|-------------|
| `onwardInlandRouting` | EBL v3.0.3+ | ObjectProperty / Class | Inland routing location beyond POD, with UNLocationCode, facilityCode, address |

**Recommended placement:** `shipment-journey/transport-documents/transport-documents.ttl`

---

### 8c. Spec Notes

- **`BOCR` vs `BORD` discrepancy:** The `transportCall.facilityTypeCode` in `event_domain_v3.2.0` uses `BOCR` in its enum but the authoritative `dcsa_domain_v3.1.1` uses `BORD`. This is a spec bug in the event domain. Our ontology should use **`BORD`** as the canonical value.
- **Three `facilityTypeCode` variants in DCSA:** `facilityTypeCode` (11 codes, general), `facilityTypeCodeTRN` (9 codes, for TransportCall/stuffing), `facilityTypeCodeOPR` (3 codes, for JIT operations: PBPL, BRTH, ANCH).
- **No inland party roles:** DCSA has no mode-specific party roles. Carrier identity for inland modes is handled at the TransportCall level (barge/vessel have operatorCarrierCode; rail/truck do not).

---

### 9. Dangerous Goods Detail (Partially Missing)

**Source:** DCSA Domain v3.1.0
**Impact:** MEDIUM — Our MMT module has basic DG classes but DCSA added extensive DG properties

| Missing Property | Description |
|-----------------|-------------|
| `imoClass` | IMO hazard class |
| `dgGrossWeight` / `dgVolume` | DG-specific weight/volume |
| `dgRemarks` | Remarks about dangerous goods |
| `EMSNumber` | Emergency Schedule number |
| `flashPoint` | Flash point temperature |
| `fumigationDateTime` | When fumigation occurred |
| `inhalationZone` | Inhalation toxicity zone |
| `isCompetentAuthorityApprovalProvided` | Boolean |
| `isEmptyUncleanedResidue` | Boolean |
| `isExceptedQuantity` | Boolean |
| `isHot` | Boolean |
| `isLimitedQuantity` | Boolean |
| `isMarinePollutant` | Boolean |
| `isReportableQuantity` | Boolean |
| `isSalvagePackings` | Boolean |
| `isWaste` | Boolean |
| `naNumber` | North American number |
| `netExplosiveContent` / `netExplosiveContentUnit` | Explosive content |
| `packingGroup` | Packing group (I, II, III) |
| `subsidiaryRisk` | Subsidiary risk class |
| `sadt` / `sapt` | Self-accelerating decomposition/polymerization temperature |
| `transportControlTemperature` / `transportEmergencyTemperature` | Control/emergency temps |

**Note:** Some of these (packingGroup, flashPoint, properShippingName, technicalName) are already in our MMT `mmt.ttl` DangerousGoods section, but NOT in the DCSA ontology.

**Recommended placement:** Consider a new `DCSA/current/shared-kernel/dangerous-goods/` module or add to existing booking module.

---

### 10. Booking Operational Properties (Missing)

**Source:** DCSA Domain v2.0.0+, BKG v2
**Impact:** MEDIUM

| Missing Property | Source | Description |
|-----------------|--------|-------------|
| `freightPaymentTermCode` | Domain v3.1.0 | PRE (Prepaid), COL (Collect) — replaces our string-typed `freightPaymentTerm` |
| `originChargesPaymentTermCode` | Domain v3.1.0 | Payment terms for origin charges |
| `destinationChargesPaymentTermCode` | Domain v3.1.0 | Payment terms for destination charges |
| `communicationChannelCode` | Domain v2.0.0 | How shipper receives documents |
| `contractQuotationReference` | Domain v2.0.0 | Reference to contract quotation |
| `isPartialLoadAllowed` | Domain v2.0.0 | Boolean |
| `isEquipmentSubstitutionAllowed` | Domain v2.0.0 | Boolean |
| `declaredValue` / `declaredValueCurrency` | Domain v2.0.0 | Declared cargo value |
| `expectedArrivalAtPlaceOfDeliveryStartDate` | Domain v2.0.0 | Expected arrival window |
| `expectedArrivalAtPlaceOfDeliveryEndDate` | Domain v2.0.0 | Expected arrival window |
| `etaAtPlaceOfDeliveryDateTime` | Domain v3.0.0 | ETA at final destination |
| `etaAtPortOfDischargeDateTime` | Domain v3.0.0 | ETA at POD |

**Recommended placement:** `shipment-journey/booking/booking.ttl`

---

### 11. Document Type Codes (Missing)

**Source:** Event Domain v3.0.0
**Impact:** LOW-MEDIUM

Our `DocumentEvent` has no document type code vocabulary. DCSA defines:
`BKG`, `SHI`, `VGM`, `CAS`, `CUS`→`CUC`, `DGD`, `OOG`, `CBR`, `TRD`, `DEI`, `DEO`, `TRO`, `CRO`, `CQU`, `INV`, `HCE`, `PCE`, `VCE`, `FCE`, `ICE`, `CEA`, `CEO`

**Recommended placement:** `track-and-trace/events/events.ttl`

---

### 12. Reference Type Codes (Missing)

**Source:** DCSA Domain v2.0.0+
**Impact:** LOW-MEDIUM

| Missing Code | Description |
|-------------|-------------|
| ECR | Empty container release reference |
| CSI | Customer shipment ID |
| BPR | Booking party reference number |
| BID | Booking Request ID |
| EQ | Equipment reference |
| RUC | Customs declaration unique reference (UCR) |
| DUE | Export declaration unique number |
| CER | AES ITN (Customs export reference) |
| AES | AES filing |

**Recommended placement:** `shipment-journey/booking/booking.ttl` or a shared reference types vocabulary.

---

### 13. Additional APIs Not Yet Covered

The DCSA OpenAPI repo contains several API domains that have **no representation** in our ontology:

| API | Directory | Description | Priority |
|-----|-----------|-------------|----------|
| **D&D (Demurrage & Detention)** | `dei/`, `deo/` | Demurrage/detention invoicing | ✅ Already partially covered in `demurrage-detention/` |
| **Arrival Notice (AN)** | `an/` | Arrival notification | MEDIUM |
| **Commercial Schedules (CS)** | `cs/` | Published commercial schedules | LOW |
| **IoT** | `iot/` | Container IoT monitoring | LOW |
| **Reefer** | `reefer/` | Reefer container monitoring | LOW |
| **PINT** | `pint/` | Platform Interoperability | LOW |
| **JIT** | `jit/` | Just-in-Time port calls | MEDIUM |
| **CBF** | `cbf/` | Cyber Booking Finalization | LOW |
| **Adopt** | `adopt/` | Adoption tooling | N/A |

---

## Priority Summary

| Priority | Gap Area | # Missing Concepts | Enrichment Effort |
|----------|---------|-------------------|-------------------|
| 🔴 CRITICAL | TransportCall model | ~9 classes/properties | New sub-module |
| 🔴 HIGH | Barge identity fields | 5 properties | Add to transport-call module |
| 🔴 HIGH | Transport plan stages | 2 properties | Add to booking or transport-call |
| 🟠 HIGH | Facility type codes | ~8 codes + property | Extend locations module |
| 🟠 HIGH | Receipt/delivery types | 4 properties | Extend booking module |
| 🟠 HIGH | Shipment location types | ~7 new codes | Extend locations module |
| 🟠 HIGH | Event type enrichment | ~11 event types + 3 categories | Extend events module |
| 🟡 MEDIUM | Pre/on-carriage on docs | 2 properties | Extend transport-documents |
| 🟡 MEDIUM | Booking operational props | ~12 properties | Extend booking |
| 🟡 MEDIUM | DG detail properties | ~25+ properties | New DG sub-module or extend booking |
| 🟢 LOW-MED | Document type codes | ~20 codes | Extend events |
| 🟢 LOW-MED | Reference type codes | ~9 codes | Extend booking or shared |

---

## Recommendations

### Immediate Actions (Next Sprint)

1. **Create TransportCall sub-module** — `DCSA/current/shared-kernel/transport-call/transport-call.ttl`
   - Define `TransportCall` base class with 4 mode-specific subclasses
   - Include barge identity fields, modeOfTransport, transportCallReference
   - Link from events module via `hasTransportCall` object property

2. **Enrich locations module** — Add `facilityTypeCode` property and inland facility vocabulary (INTE, RAMP, BORD, DEPO, WAYP, ANCH)

3. **Add transport plan stages** — `transportPlanStage` (PRC/MNC/ONC) and sequence number

4. **Add receipt/delivery types** — `receiptTypeAtOrigin`, `deliveryTypeAtDestination` to booking

### Short-Term Actions

5. **Enrich events module** — Add missing equipment event types (CROS, AVPU, AVDO, customs events), add TransportCall linkage
6. **Add shipment location type codes** — PSR, IEL, PTP, RTP, FCD, ECP, FDE
7. **Add pre/on-carriage mode to transport documents**

### Medium-Term Actions

8. **Add booking operational properties** — payment terms, declared value, ETAs
9. **Create DG properties module** — Align with DCSA Domain v3.1.0 DG properties
10. **Add Operations Event class** — For JIT port call operations
11. **Add document type code and reference type code vocabularies**

---

## Appendix: DCSA API Version Traceability

| Our Ontology Source Reference | Actual Latest DCSA Version | Gap |
|------------------------------|---------------------------|-----|
| BKG v2.0 | BKG v2.0.2+ (v2 directory in OpenAPI repo) | Minor delta — receipt/delivery types, plan stages |
| EBL v3.0 | EBL v3 (v3 directory in OpenAPI repo) | preCarriageBy, onCarriageBy |
| TNT v2.2 | TNT v3 (v3 directory in OpenAPI repo) | **Major delta** — TransportCall split, new event types |
| OVS v3.0 | OVS v3 (latest in repo) | TransportCall linkage |
| DCSA Domain (not versioned) | Domain v3.1.1 | **Major delta** — barge fields, DG props, facility types |
| Event Domain (not versioned) | Event Domain v3.2.0 | **Major delta** — mode-specific transport calls, CROS, customs events |
