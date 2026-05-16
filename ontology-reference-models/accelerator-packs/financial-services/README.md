# Kairos Financial Services Accelerator Pack

**Pre-composed ontology bundle for financial services companies**

## Who is this for?

This accelerator pack is designed for organisations in the financial services sector, including:

- Accounting firms
- Banks and credit institutions
- Auditors
- Financial services providers
- Insurance companies
- Trade finance institutions

## What's included?

The Financial Services Accelerator imports **FIBO foundations** and the **BSP** commercial/financial ontology:

| Ontology | Standard | Focus |
|----------|----------|-------|
| FIBO FND – Agents | EDM Council FIBO | Autonomous agents, people |
| FIBO FND – Organizations | EDM Council FIBO | Legal entities, organisations |
| FIBO FND – Contracts | EDM Council FIBO | Agreements, contractual obligations |
| FIBO BE – Partnerships | EDM Council FIBO | Partnerships, joint ventures |
| BSP | ISO 20197-1:2024 | Party, contract, invoice, settlement |

### What's NOT included?

- **DCSA, MMT, TIC, IMO, WCO, Sustainability** — use the [Logistics Accelerator](../logistics/) for logistics-specific ontologies.

## How to use

Import the root Turtle file to pull in every financial-services ontology at once:

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.com/my-financial-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/accelerator/financial-services#> .
```

Or, if working locally, point your tool at:

```
ontology-reference-models/accelerator-packs/financial-services/financial-services-accelerator.ttl
```

## Version

See [VERSION](VERSION) — currently **1.0.0**.
