# Industry Model Selection for Freight Forwarders

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-15

The logistics blueprint combines multiple industry models because no single model fully covers the freight forwarder operating model end-to-end.

## Important positioning

This blueprint is an **opinionated combination** of industry models we bring together for a pragmatic freight-forwarder fit.

Nothing is constrained:
- If more detailed domain coverage is needed, additional domains from open industry models can be added.
- If a capability is not (well) covered by industry models, customer-specific domains can be added.

## Selected model stack

| Model | Current version | Main contribution in the blueprint |
|---|---|---|
| DCSA | 1.1.0 | Container shipping lifecycle, booking, transport documents, events, schedule |
| MMT (UN/CEFACT) | 1.0.0 | Multimodal transport semantics for consignment, cargo, equipment, inland legs |
| BSP (ISO 20197-1) | 1.3.0 | Commercial and financial backbone (party, contract, invoice, settlement) |
| TIC 4.0 | 1.2.0 | Terminal and automotive operational model |
| IMO | 1.1.0 | Maritime authority model (vessel registry, port call, dangerous goods) |
| WCO | 1.2.0 | Customs and trade facilitation model |
| Sustainability | 1.1.0 | Emissions, energy, ESG metrics |
| Supply Chain Integration | 1.1.0 | Cross-standard bridge properties across domains |

## Why this is a best fit for freight forwarders

1. It covers the full process chain from quote/booking to execution, events, compliance, and settlement.
2. It respects authority by using the strongest source per domain (for example IMO for maritime and WCO for customs).
3. It supports multimodal reality (ocean, inland, terminal, intermodal, automotive).
4. It preserves integration flexibility through explicit cross-domain bridge properties.

## Design strategy used to bring models together

- **Domain ownership first:** each concept is owned by one domain and one canonical source.
- **Overlap resolution:** ambiguous concepts are explicitly resolved in `data-domains.yaml`.
- **Selective imports:** domain files import only required modules, not entire bundles.
- **Cross-standard linking:** bridge relationships are centralized in the Supply Chain integration layer.

## Per-model detail sheets

See `industry-models/` for one-page model charts with:
- what it is
- main focus
- governance/ownership
- official references
- ontology links (OWL URI and/or model documentation)
- adoption context
