# Supply Chain Integration Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-15

| Item | Details |
|---|---|
| What is it? | A Kairos integration ontology that defines bridge properties between classes from different standards. |
| Main focus | Cross-standard semantic links (for example booking-to-consignment, event-to-vessel, consignment-to-customs). |
| Why selected in this blueprint | Prevents siloed standards by making interoperability explicit where no single standard defines the bridge. |
| Who is behind it | Kairos Ontology Team. |
| Official site / references | Internal ontology module (`https://www.kairosflow.ai/ont/supply-chain#`) and blueprint registry documentation. |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/supply-chain#` |
| Adoption context | Used as an integration layer when combining DCSA, MMT, BSP, IMO, TIC, and WCO in one client ontology hub. |
| Kairos modules used | `supply-chain` cross-domain properties referenced in `data-domains.yaml` under `cross_domain_relationships`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/SupplyChain/README.md`
- `ontology-reference-models/accelerator-packs/logistics/client-hub-blueprint/data-domains.yaml`

## Annex A — Main relationship anchors (high-level overview)

> This is a high-level overview of representative cross-standard anchors (not a full bridge registry).

| Anchor (cross-standard) | High-level explanation | Example bridge properties |
|---|---|---|
| `DCSA Booking` → `MMT Consignment` | Connects commercial booking intent to multimodal execution object. | `sc:bookedConsignment` |
| `MMT Consignment` ↔ `BSP Invoice` | Links execution flow to financial settlement artifacts. | `sc:invoicedVia`, `sc:chargesForConsignment` |
| `IMO PortCall` → `TIC Terminal` | Bridges maritime call lifecycle to terminal operational location. | `sc:callsAtTerminal`, `sc:berthsAt` |
| `MMT CargoItem` → `IMO DangerousGoodsItem` | Connects cargo semantics to dangerous-goods classification. | `sc:classifiedAsDangerousGoods` |
| `MMT Consignment` → `WCO CustomsDeclaration` | Represents customs obligation on cross-border consignments. | `sc:requiresCustomsDeclaration` |
| `DCSA Event` → `MMT/IMO entities` | Ties shipping events to transport execution and vessel context. | `sc:eventRelatesToConsignment`, `sc:eventRelatesToVessel` |
