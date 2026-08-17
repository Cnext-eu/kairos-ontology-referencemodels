# IMO Maritime Ontology

An OWL ontology modelling the International Maritime Organization (IMO) reference data model, aligned with the **IMO Compendium**, the **FAL Convention**, **SOLAS**, **MARPOL**, **STCW**, **MLC 2006**, the **BWM Convention**, and the **ISPS Code**.

## Version

`1.1.0`

## Namespace

| Scope | Namespace |
|---|---|
| Root ontology | `https://www.kairosflow.ai/ont/imo#` |
| Vessel Registry | `https://www.kairosflow.ai/ont/imo/vessel-registry#` |
| Dangerous Goods | `https://www.kairosflow.ai/ont/imo/dangerous-goods#` |
| Port Call | `https://www.kairosflow.ai/ont/imo/port-call#` |
| Party | `https://www.kairosflow.ai/ont/imo/party#` |
| Locations | `https://www.kairosflow.ai/ont/imo/locations#` |
| Certificates & Surveys | `https://www.kairosflow.ai/ont/imo/certificates-surveys#` |
| Crew & Seafarer | `https://www.kairosflow.ai/ont/imo/crew-seafarer#` |
| Environmental | `https://www.kairosflow.ai/ont/imo/environmental#` |
| Maritime Security | `https://www.kairosflow.ai/ont/imo/maritime-security#` |

## Structure

```
IMO/
├── VERSION                                          # Semantic version (1.1.0)
├── README.md                                        # This file
├── current/
│   ├── imo.ttl                                      # Root ontology (imports all 9 modules)
│   ├── vessel-registry/vessel-registry.ttl          # Vessel identity, classification, dimensions
│   ├── dangerous-goods/dangerous-goods.ttl          # IMDG Code, DG declarations, segregation
│   ├── port-call/port-call.ttl                      # Voyage, port call lifecycle, FAL forms
│   ├── party/party.ttl                              # Maritime stakeholders, security officers
│   ├── locations/locations.ttl                      # Ports, berths, ECAs, MARPOL special areas
│   ├── certificates-surveys/certificates-surveys.ttl # Statutory certificates & surveys
│   ├── crew-seafarer/crew-seafarer.ttl              # Seafarer identity, STCW certs, crew/pax lists
│   ├── environmental/environmental.ttl              # SEEMP, BWMP, SOPEP, NLS classification
│   └── maritime-security/maritime-security.ttl      # ISPS ship/port security plans, DoS
```

## Domain Modules

### Vessel Registry
Vessel identification and registration: IMO number, MMSI, call sign, flag state, classification society, vessel type, tonnage (GT, NT, DWT), and physical dimensions (LOA, beam, draft).

### Dangerous Goods
IMDG Code dangerous goods management: UN numbers, hazard classes, packing groups, flash points, emergency schedules (EmS), stowage categories, segregation rules, acceptance rules, and the Dangerous Goods Declaration (FAL Form 7).

### Port Call
Complete port call lifecycle: voyages, sea legs, arrival/departure notices, berth stays, FAL forms, pilotage and towage requests, bunkering operations, waste disposal, crew changes, pre-arrival notifications, port health declarations, waste pre-notifications, voyage plans, and route waypoints.

### Party
Maritime parties and stakeholders: flag authorities, port authorities, classification societies, vessel masters, ship owners, managers, operators, maritime agents, pilot services, towage providers. ISPS Code security officer roles: CSO (Company Security Officer), SSO (Ship Security Officer), PFSO (Port Facility Security Officer), and PSCO (Port State Control Officer).

### Locations
Maritime locations and navigational areas: ports (UN/LOCODE), anchorages, fairway buoys, VTS zones, pilot boarding places, berths, port approaches, traffic separation schemes, Emission Control Areas (MARPOL Annex VI), MARPOL Special Areas, and port reception facilities.

### Certificates & Surveys *(new in v1.1.0)*
Statutory certificates required under SOLAS, MARPOL, STCW, MLC 2006, and the ISPS Code. Uses a single `StatutoryCertificate` abstract base with structurally distinct subclasses: International Energy Efficiency Certificate (IEE — carries EEDI/EEXI/CII values), Document of Compliance (DOC — issued to companies), Safety Management Certificate (SMC), International Ship Security Certificate (ISSC), and Maritime Labour Certificate (MLC — carries DMLC Part I/II status). Also covers `StatutorySurvey` for initial, renewal, annual, and intermediate surveys.

### Crew & Seafarer *(new in v1.1.0)*
Seafarer identity and certification aligned with the STCW Convention: Certificate of Competency (CoC) with grade, Certificate of Proficiency (CoP) with specialized function. Crew lists (FAL Form 5) and passenger lists (FAL Form 6) linked to vessels and port calls.

### Environmental *(new in v1.1.0)*
Environmental compliance aligned with MARPOL and the BWM Convention: Ship Energy Efficiency Management Plan (SEEMP — Parts I/II/III), Ballast Water Management Plan (BWMP), Shipboard Oil Pollution Emergency Plan (SOPEP), Garbage Management Plan, and Noxious Liquid Substance (NLS) classification under MARPOL Annex II.

### Maritime Security *(new in v1.1.0)*
ISPS Code security framework: Ship Security Plan, Port Facility Security Plan, and Declaration of Security (DoS). Tracks MARSEC security levels, RSO approval, ISPS compliance status, and ship-port interface activities.

## Cross-Domain Alignment

The IMO ontology uses `rdfs:seeAlso` annotations to reference related concepts in other Kairos reference models without creating `owl:imports` dependencies. This applies to *annotation* alignment only — where an IMO module asserts `rdfs:domain` or `rdfs:range` against a class in another module, it declares an `owl:imports` for it, as `party.ttl` has for `imo/locations` since 1.1.0 and as the four modules corrected in 1.4.0 now do (gh#97). Enforced by `validate_structure.py` check 10.

| IMO Concept | Related Concept | Relationship |
|---|---|---|
| `imo-vr:Vessel` | `dcsa/transport-call#VesselTransportCall` | Same vessel identity |
| `imo-vr:Vessel` | `mmt/transport-means#Vessel` | Same vessel identity |
| `imo-pc:PortCall` | `dcsa/transport-call#TransportCall` | Port call ≈ transport call |
| `imo-loc:Port` | `dcsa/locations#Location` | Port location alignment |

Hub ontologies compose these via `owl:imports` at integration time.

## Sources

- IMO Compendium on Facilitation of International Maritime Traffic
- Convention on Facilitation of International Maritime Traffic (FAL Convention)
- International Maritime Dangerous Goods Code (IMDG Code)
- SOLAS (International Convention for the Safety of Life at Sea)
- MARPOL 73/78 (International Convention for the Prevention of Pollution from Ships)
- STCW Convention 1978 (Standards of Training, Certification and Watchkeeping, Manila 2010)
- MLC 2006 (Maritime Labour Convention)
- BWM Convention 2004 (Ballast Water Management)
- ISPS Code 2002 (International Ship and Port Facility Security)

## Changelog

### v1.1.0 (2026-06-12)
- **New module**: Certificates & Surveys — 7 classes covering statutory certificates (IEE, DOC, SMC, ISSC, MLC) and surveys
- **New module**: Crew & Seafarer — 7 classes covering seafarer identity, STCW certificates (CoC, CoP), crew lists (FAL 5), passenger lists (FAL 6)
- **New module**: Environmental — 5 classes covering SEEMP, BWMP, SOPEP, garbage management, NLS classification
- **New module**: Maritime Security — 3 classes covering ISPS ship/port security plans and declaration of security
- **Enriched**: Port Call — added 5 classes (PreArrivalNotification, PortHealthDeclaration, WastePreNotification, VoyagePlan, RouteWaypoint) + falFormType property
- **Enriched**: Party — added 4 ISPS security officer roles (CSO, SSO, PFSO, PSCO)
- **Enriched**: Locations — added 3 environmental zone classes (EmissionControlArea, MARPOLSpecialArea, PortReceptionFacility)
- **Cross-domain**: Added rdfs:seeAlso alignment to DCSA and MMT ontologies

### v1.0.0 (2026-05-16)
- Initial release with 5 modules: Vessel Registry, Dangerous Goods, Port Call, Party, Locations

## Creator

Kairos Ontology Team
