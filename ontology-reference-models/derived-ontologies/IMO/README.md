# IMO Maritime Ontology

An OWL ontology modelling the International Maritime Organization (IMO) reference data model, aligned with the **IMO Compendium**, the **FAL Convention**, and the **IMDG Code**.

## Version

`1.0.0`

## Namespace

| Scope | Namespace |
|---|---|
| Root ontology | `http://kairos.ai/ont/imo#` |
| Vessel Registry | `http://kairos.ai/ont/imo/vessel-registry#` |
| Dangerous Goods | `http://kairos.ai/ont/imo/dangerous-goods#` |
| Port Call | `http://kairos.ai/ont/imo/port-call#` |
| Party | `http://kairos.ai/ont/imo/party#` |
| Locations | `http://kairos.ai/ont/imo/locations#` |

## Structure

```
IMO/
├── VERSION                              # Semantic version (1.0.0)
├── README.md                            # This file
├── imo.ttl                              # Root ontology (imports all domains)
├── vessel-registry/vessel-registry.ttl  # Vessel identity, classification, dimensions
├── dangerous-goods/dangerous-goods.ttl  # IMDG Code, DG declarations, segregation
├── port-call/port-call.ttl              # Voyage, port call lifecycle, services
├── party/party.ttl                      # Maritime stakeholders and authorities
└── locations/locations.ttl              # Ports, berths, VTS zones, navigational areas
```

## Domain Modules

### Vessel Registry
Vessel identification and registration: IMO number, MMSI, call sign, flag state, classification society, vessel type, tonnage (GT, NT, DWT), and physical dimensions (LOA, beam, draft).

### Dangerous Goods
IMDG Code dangerous goods management: UN numbers, hazard classes, packing groups, flash points, emergency schedules (EmS), stowage categories, segregation rules, acceptance rules, and the Dangerous Goods Declaration (FAL Form 7).

### Port Call
Complete port call lifecycle: voyages, sea legs, arrival/departure notices, berth stays, FAL forms, pilotage and towage requests, bunkering operations, waste disposal, and crew changes.

### Party
Maritime parties and stakeholders: flag authorities, port authorities, classification societies, vessel masters, ship owners, managers, operators, maritime agents, pilot services, and towage providers.

### Locations
Maritime locations and navigational areas: ports (UN/LOCODE), anchorages, fairway buoys, VTS zones, pilot boarding places, berths, port approaches, and traffic separation schemes.

## Sources

- IMO Compendium on Facilitation of International Maritime Traffic
- Convention on Facilitation of International Maritime Traffic (FAL Convention)
- International Maritime Dangerous Goods Code (IMDG Code)
- SOLAS (International Convention for the Safety of Life at Sea)
- MARPOL (International Convention for the Prevention of Pollution from Ships)

## Creator

Kairos Ontology Team
