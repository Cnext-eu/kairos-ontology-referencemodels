# Accelerator Packs

**Pre-composed ontology bundles for specific industry verticals**

## What are Accelerator Packs?

Accelerator Packs are curated bundles of Kairos ontologies tailored to a particular industry or use-case. Instead of hand-picking individual ontologies, you import a single accelerator `.ttl` file and get every ontology relevant to your sector — with the right standards alignment baked in.

## Available Packs

| Pack | Directory | Target Sectors |
|------|-----------|---------------|
| [Logistics](logistics/) | `logistics/` | Freight forwarding, ocean/road carriers, terminals, 3PL, NVOCC, customs brokerage |
| [Financial Services](financial-services/) | `financial-services/` | Banks, accounting firms, auditors, insurance, trade finance |

## How to use

1. **Choose a pack** that matches your industry.
2. **Import the root `.ttl` file** in your ontology:

```turtle
# Logistics example
<http://example.com/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/accelerator/logistics#> .

# Financial Services example
<http://example.com/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/accelerator/financial-services#> .
```

3. **Or reference the local file** if working offline:

```
ontology-reference-models/accelerator-packs/logistics/logistics-accelerator.ttl
ontology-reference-models/accelerator-packs/financial-services/financial-services-accelerator.ttl
```

Each pack ships with a `manifest.yaml` describing what is included, what is excluded, and which standards it aligns with.

## Creating a new Accelerator Pack

1. Create a new directory under `accelerator-packs/`.
2. Add a `VERSION` file, a root `.ttl` file, a `manifest.yaml`, and a `README.md`.
3. Register the pack's URI in `catalog-v001.xml`.
