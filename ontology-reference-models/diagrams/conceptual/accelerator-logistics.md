# Logistics accelerator pack

An accelerator pack is a **pre-composed bundle**. Instead of a client hub importing nine suites
one by one, it imports the pack and gets the whole vertical in a single `owl:imports`. The
Logistics pack bundles eight derived suites plus the SupplyChain bridge, references IATA ONE
Record without bulk-importing it, and deliberately excludes FIBO.

```mermaid
flowchart TB
  PACK["Logistics Accelerator Pack<br/><small>ont/accelerator/logistics#</small>"]

  subgraph INCL["owl:imports — bundled"]
    direction LR
    DCSA["DCSA"]
    MMT["MMT"]
    BSP["BSP"]
    TIC["TIC"]
    IMO["IMO"]
    WCO["WCO"]
    RAIL["RAIL"]
    SUS["Sustainability"]
    SC["SupplyChain<br/><small>cross-standard bridge</small>"]
  end

  subgraph REF["referenced, not bundled"]
    IATA["IATA ONE Record<br/><small>bind hub-local at reservation grain</small>"]
  end

  subgraph EXC["excluded"]
    FIBO["FIBO<br/><small>use the Financial Services pack</small>"]
  end

  PACK --> INCL
  PACK -. via catalog .-> REF
  PACK -. never imports .-> EXC

  classDef pack fill:#f3e8ff,stroke:#8a3bd8,color:#123;
  classDef incl fill:#e8f7e9,stroke:#3aa657,color:#123;
  classDef ref fill:#fff3d6,stroke:#d8a13b,color:#123;
  classDef exc fill:#ffe3e3,stroke:#d84b4b,color:#123;
  class PACK pack;
  class DCSA,MMT,BSP,TIC,IMO,WCO,RAIL,SUS,SC incl;
  class IATA ref;
  class FIBO exc;
```

## Import the module, not the pack

The bundle exists for tools that need the complete graph at once (validation, projection). A
client hub's **domain** ontology should still import the specific module it needs — `…/ont/bsp/party`,
not the whole pack — so its real dependencies stay readable. See
[`CONTRACT.md`](../../CONTRACT.md) → "Rules for consumers".

```mermaid
flowchart LR
  HUB["client hub<br/>party domain"] -->|imports the module| MOD["ont/bsp/party"]
  HUB -.->|NOT the whole pack| PACK["ont/accelerator/logistics"]
  linkStyle 1 stroke:#d84b4b,stroke-dasharray:4;
```

## Target sectors

Freight forwarding · ocean carrier · road carrier · terminal operations · 3PL/LSP · NVOCC ·
customs brokerage. A second pack, **Financial Services**, bundles FIBO foundations + BSP for the
financial vertical.
