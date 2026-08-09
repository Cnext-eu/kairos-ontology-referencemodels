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
ontology-reference-models/accelerator-packs/logistics/current/logistics-accelerator.ttl
```

## Version

See [VERSION](VERSION) — currently **1.6.0**.

## Sector discovery materials

This pack ships SME interview scripts for each target sector under
[`discovery/`](discovery/), keyed by archetype id from
[`blueprints/archetypes/`](../../blueprints/archetypes/). See
[`discovery/README.md`](discovery/README.md) for the convention.

Available today:

| Sector | Archetype | Discovery script |
|--------|-----------|------------------|
| Ocean carrier / short-sea / ro-ro / barge (containerised) | [`shipping-carrier`](../../blueprints/archetypes/shipping-carrier.yaml) | [`discovery/shipping-carrier.md`](discovery/shipping-carrier.md) |
| Freight forwarder / NVOCC / multimodal logistics service provider | [`freight-forwarder`](../../blueprints/archetypes/freight-forwarder.yaml) | [`discovery/freight-forwarder.md`](discovery/freight-forwarder.md) |
| Unit-load / ro-ro / short-sea carrier (non-containerised, own-account + subcontracted road haulage) | [`unit-load-carrier`](../../blueprints/archetypes/unit-load-carrier.yaml) | [`discovery/unit-load-carrier.md`](discovery/unit-load-carrier.md) |

## Changelog

Pack-level changes are recorded in the root [`CHANGELOG.md`](../../../CHANGELOG.md) alongside
every other pack and ontology, not duplicated here.
