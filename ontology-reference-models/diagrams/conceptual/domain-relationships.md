# How the domains relate

The nine derived suites are not islands. Eight of them model a slice of the logistics value
chain; the ninth — **SupplyChain** — owns no classes of its own. It is a pure *bridge module*: a
set of cross-standard object properties that link a class in one suite to a class in another. The
edges below are exactly those bridge properties (see the generated
[`supplychain.md`](../generated/supplychain.md) for the machine-rendered version).

Read this as the answer to "if I'm looking at a booking, how do I get to its customs declaration,
its emissions, or its terminal handling?"

```mermaid
flowchart LR
  DCSA["DCSA<br/><small>container shipping</small>"]
  MMT["MMT<br/><small>multimodal transport</small>"]
  BSP["BSP<br/><small>buy-ship-pay</small>"]
  TIC["TIC<br/><small>terminal operations</small>"]
  IMO["IMO<br/><small>maritime regulatory</small>"]
  WCO["WCO<br/><small>customs & border</small>"]
  RAIL["RAIL<br/><small>TAF TSI rail</small>"]
  SUS["Sustainability<br/><small>carbon & energy</small>"]

  DCSA -->|bookedConsignment| MMT
  DCSA -->|underAgreement| BSP
  DCSA -->|correspondsToBillOfLading| BSP
  DCSA -->|handledAtTerminal| TIC
  DCSA -->|eventRelatesToVessel| IMO
  DCSA -->|eventRelatesToConsignment| MMT
  MMT -->|scheduledVia| DCSA
  MMT -->|requiresCustomsDeclaration| WCO
  MMT -->|classifiedAsDangerousGoods| IMO
  MMT -->|declaredAsGoodsItem| WCO
  MMT -->|invoicedVia| BSP
  BSP -->|chargesForConsignment| MMT
  MMT -->|hasCarbonFootprint| SUS
  MMT -->|hasEnergyConsumption| SUS
  IMO -->|hasCIIRating / hasEmissionReport| SUS
  IMO -->|berthsAt| TIC
  IMO -->|callsAtTerminal| TIC
  TIC -->|eventRelatesToEquipment| DCSA

  classDef s fill:#eef4ff,stroke:#3b6ea8,color:#123;
  class DCSA,MMT,BSP,TIC,IMO,WCO,RAIL,SUS s;
```

> **RAIL** is bundled in the logistics pack for EU rail-freight reservation and running (TAF TSI),
> and binds at the reservation grain via the
> [multimodal-order-leg](patterns/multimodal-order-leg.md) pattern rather than through a
> SupplyChain bridge property today — so it stands apart in this view.

## The suites at a glance

| Suite | Standard | Focus |
|---|---|---|
| **DCSA** | DCSA API Standards | Container shipping lifecycle — booking, B/L, vessel, equipment, track & trace |
| **MMT** | UN/CEFACT MMT-RDM | Consignment, movement, cargo, equipment across modes |
| **BSP** | ISO 20197-1:2024 Buy-Ship-Pay | Party, contract, invoice, settlement |
| **TIC** | TIC 4.0 | Terminal operations, handling, automotive |
| **IMO** | IMO Compendium / FAL / IMDG | Vessel registry, dangerous goods, port-call, crew, security |
| **WCO** | WCO Data Model 3.x | Customs declarations, goods items, trade facilitation |
| **RAIL** | TAF TSI | EU rail path request, consignment order, train running, rolling stock |
| **Sustainability** | ISO 14083:2023 / GLEC | Emissions, energy, ESG reporting |
| **SupplyChain** | — (Kairos bridge) | Cross-standard properties that link all of the above |
