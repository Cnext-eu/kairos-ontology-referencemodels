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

<!-- BEGIN GENERATED: modules -->
The Logistics Accelerator bundles **9 ontologies** via **11 `owl:imports`** (some modules are imported at sub-module granularity):

| Ontology | Standard | Version | Focus |
|---|---|---|---|
| DCSA | Digital Container Shipping Association | `1.4.0` | Container shipping lifecycle |
| MMT | Multi-Modal Transport | `2.1.0` | Consignment, movement, cargo, equipment |
| BSP | Buy-Ship-Pay | `2.1.0` | Party, contract, invoice, settlement |
| TIC | Terminal Industry Committee 4.0 | `1.3.0` | Terminal operations, handling, automotive |
| IMO | International Maritime Organization | `1.1.0` | Vessel registry, dangerous goods, port-call, crew, environmental, maritime security |
| WCO | World Customs Organization | `1.2.0` | Customs declarations, goods items, procedures, trade facilitation |
| Sustainability | Sustainability & Carbon | `1.1.0` | Emissions, energy, ESG reporting |
| supply-chain | Supply Chain | `1.2.0` | Cross-standard bridge properties linking DCSA, MMT, BSP, TIC, IMO, and WCO |
| RAIL | TAF TSI Rail | `1.0.0` | EU rail freight reservation & running (path request, consignment order, train running, rolling stock) |

Reference-only — catalogued and bindable, deliberately **not** imported:

| Ontology | Standard | Version | Focus |
|---|---|---|---|
| IATA | IATA ONE Record (air cargo) | `3.3.0 RC1 (2026-08 standard)` | Air cargo booking, shipment, transport movement |
<!-- END GENERATED: modules -->

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

<!-- BEGIN GENERATED: version -->
See [VERSION](VERSION) — currently **1.10.0**.
<!-- END GENERATED: version -->

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
