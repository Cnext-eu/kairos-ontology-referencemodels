# Kairos Logistics Accelerator Pack

**Pre-composed ontology bundle for logistics companies**

## Who is this for?

This accelerator pack is designed for organisations in the logistics and supply chain sector, including:

- Freight forwarders
- Ocean carriers (vessel operators)
- Road carriers (trucking companies)
- Terminal operators
- 3PL / logistics service providers
- NVOCCs
- Customs brokerages

## What's included?

The Logistics Accelerator imports **8 ontologies** covering the full logistics value chain:

| Ontology | Standard | Focus |
|----------|----------|-------|
| DCSA | DCSA API Standards | Container shipping lifecycle |
| MMT | UN/CEFACT MMT-RDM | Consignment, movement, cargo, equipment |
| BSP | ISO 20197-1:2024 | Party, contract, invoice, settlement |
| TIC | TIC 4.0 | Terminal operations, handling, automotive |
| IMO | IMO Compendium / FAL / IMDG | Vessel registry, dangerous goods, port-call, crew, environmental, maritime security |
| WCO | WCO Data Model 3.10.0 | Customs declarations, goods items, procedures, trade facilitation |
| Sustainability | ISO 14083:2023 / GLEC | Emissions, energy, ESG reporting |
| Supply Chain | — | Integration layer |

### What's NOT included?

- **FIBO** (Financial Industry Business Ontology) — use the [Financial Services Accelerator](../financial-services/) for financial ontologies.

## How to use

Import the root Turtle file to pull in every logistics ontology at once:

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.com/my-logistics-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/accelerator/logistics#> .
```

Or, if working locally, point your tool at:

```
ontology-reference-models/accelerator-packs/logistics/logistics-accelerator.ttl
```

## Version

See [VERSION](VERSION) — currently **1.3.0**.

## Changelog

### v1.3.0 (2026-06-13)
- Updated SupplyChain bridge to v1.1.0: added Sustainability, WCO GoodsItem, and document bridges
- Updated WCO focus to reflect v1.2.0 (goods items, customs procedures)
- Updated IMO focus to reflect v1.1.0 (crew, environmental, maritime security)
- Fixed WCO Data Model version reference (3.0 → 3.10.0)

### v1.2.0 (2026-05-22)
- Added SupplyChain integration ontology
- Version alignment updates
