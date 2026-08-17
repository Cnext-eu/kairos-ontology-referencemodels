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
| DCSA | Digital Container Shipping Association | `1.6.0` | Container shipping lifecycle |
| MMT | Multi-Modal Transport | `2.3.0` | Consignment, movement, cargo, equipment |
| BSP | Buy-Ship-Pay | `2.5.0` | Party, contract, invoice, settlement |
| TIC | Terminal Industry Committee 4.0 | `1.4.0` | Terminal operations, handling, automotive |
| IMO | International Maritime Organization | `1.3.0` | Vessel registry, dangerous goods, port-call, crew, environmental, maritime security |
| WCO | World Customs Organization | `1.4.0` | Customs declarations, goods items, procedures, trade facilitation |
| Sustainability | Sustainability & Carbon | `1.2.0` | Emissions, energy, ESG reporting |
| supply-chain | Supply Chain | `1.4.0` | Cross-standard bridge properties linking DCSA, MMT, BSP, TIC, IMO, and WCO |
| RAIL | TAF TSI Rail | `1.1.0` | EU rail freight reservation & running (path request, consignment order, train running, rolling stock) |

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

## Client hub blueprint

Pack-scoped inputs a client hub is scaffolded from. Both are read by the toolkit, so they are
contract rather than documentation — see [CONTRACT.md](../../CONTRACT.md) and
[`contract-manifest.yaml`](../../contract-manifest.yaml).

- **[data-domains.yaml](client-hub-blueprint/data-domains.yaml)** — the domain registry: what each
  domain owns and does not own, and which reference modules it imports.
- **[entity-projections.yaml](client-hub-blueprint/entity-projections.yaml)** — the pack's
  column-recognition vocabulary: which groups of source columns are a flattened projection of
  another entity, and what relationship connects them. Role vocabulary is exactly where the packs
  diverge — logistics needs `pickup`/`origin`/`destination`, financial services would need its own
  — which is why it is pack-scoped rather than compiled into the toolkit. Candidates derived from
  it are advisory. A pack that ships no such file yields no candidates; there is deliberately no
  built-in fallback.

Both validate against schemas in the shared
[`accelerator-packs/_schema/`](../_schema/) rather than against a pack-local `_schema/`: the
documents are pack-scoped but their shapes are not, so each schema is authored once and is binding
on every pack's copy.

## Version

<!-- BEGIN GENERATED: version -->
See [VERSION](VERSION) — currently **1.10.1**.
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
