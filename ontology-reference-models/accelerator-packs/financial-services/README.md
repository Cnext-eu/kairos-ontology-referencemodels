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

The Financial Services Accelerator imports the **FIBO** (Financial Industry Business Ontology) suite:

| Ontology | Standard | Focus |
|----------|----------|-------|
| FIBO FND | EDM Council FIBO | Agents, parties, organisations, agreements, contracts, dates, places, accounting, transactions |
| FIBO BE | EDM Council FIBO | Legal entities, corporate structure, ownership, partnerships, trusts, government entities |
| FIBO FBC | EDM Council FIBO | Financial instruments, intermediaries, registries, products and services |
| FIBO SEC | EDM Council FIBO | Debt, equities, funds, issuance, classification, listings |
| FIBO DER | EDM Council FIBO | Options, futures, forwards, swaps, credit/rate/security-based derivatives |
| FIBO LOAN | EDM Council FIBO | Commercial, consumer, student, mortgage, green loans |
| FIBO IND | EDM Council FIBO | Economic indicators, FX, interest rates, market indices |
| FIBO MD | EDM Council FIBO | Prices, yields, analytics, temporal market data |
| FIBO CAE | EDM Council FIBO | Corporate actions: splits, dividends, offerings, events |
| FIBO BP | EDM Council FIBO | Securities issuance, transaction workflows |
| FIBO ACTUS | ACTUS / EDM Council | Algorithmic contract terms, cashflow taxonomy |

### What's NOT included?

- **DCSA, MMT, TIC, IMO, WCO, BSP, Sustainability** — use the [Logistics Accelerator](../logistics/) for logistics-specific ontologies.

## How to use

Import the root Turtle file to pull in every financial-services ontology at once:

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.com/my-financial-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/accelerator/financial-services#> .
```

Or, if working locally, point your tool at:

```
ontology-reference-models/accelerator-packs/financial-services/current/financial-services-accelerator.ttl
```

## Data domains

- **[data-domains.yaml](client-hub-blueprint/data-domains.yaml)** — the domain registry: what each
  domain owns and does not own, and which reference modules it imports. Read by the toolkit, so
  it is contract rather than documentation — see [CONTRACT.md](../../CONTRACT.md).

For the hub folder structure itself, run `kairos-ontology new-repo` / `init`: the toolkit
scaffolds and owns that layout. Consumption rules — import the module rather than the pack,
extend rather than redefine — are in [CONTRACT.md](../../CONTRACT.md).

## Version

<!-- BEGIN GENERATED: version -->
See [VERSION](VERSION) — currently **2.1.0**.
<!-- END GENERATED: version -->
