# Content tier landscape

The repository publishes three tiers of content. They differ by **who authors them** and **how
much Kairos is allowed to add** — from "vendored verbatim, never touched" to "opinionated Kairos
guidance". Accelerator packs sit on top and compose the lower tiers into per-sector bundles.

```mermaid
flowchart TB
  subgraph AUTH["Authoritative — authoritative-ontologies/"]
    direction LR
    A1["Official RDF/OWL from standards bodies<br/>Vendored verbatim — never hand-edited"]
    FIBO["FIBO<br/>(300+ files, EDM Council)"]
    IATA["IATA ONE Record<br/>(air cargo)"]
  end

  subgraph DER["Derived — derived-ontologies/"]
    direction LR
    D1["Kairos RDF interpretations of non-RDF standards<br/>Every class cites an element of its standard"]
    DSUITES["DCSA · MMT · BSP · TIC<br/>IMO · WCO · RAIL · SupplyChain · Sustainability"]
  end

  subgraph BP["Blueprint — blueprints/"]
    direction LR
    B1["Opinionated Kairos guidance — not a standard<br/>Versioned independently"]
    BPARTS["archetypes/ · patterns/ · ontology/"]
  end

  subgraph ACC["Accelerator packs — accelerator-packs/"]
    P1["Pre-composed per-sector bundles: one owl:imports pulls a whole vertical"]
    PLOG["logistics"]
    PFIN["financial-services"]
  end

  AUTH --> ACC
  DER --> ACC
  BP -. guides .-> ACC

  classDef auth fill:#e3f0ff,stroke:#3b7dd8;
  classDef der fill:#e8f7e9,stroke:#3aa657;
  classDef bp fill:#fff3d6,stroke:#d8a13b;
  classDef acc fill:#f3e8ff,stroke:#8a3bd8;
  class AUTH,A1,FIBO,IATA auth;
  class DER,D1,DSUITES der;
  class BP,B1,BPARTS bp;
  class ACC,P1,PLOG,PFIN acc;
```

## What each tier means

| Tier | Folder | Rule of thumb |
|---|---|---|
| **Authoritative** | `authoritative-ontologies/` | Someone else's standard, already published as RDF. We vendor it **verbatim** and re-download to update — we never hand-edit it. |
| **Derived** | `derived-ontologies/` | A standard that is *not* published as RDF (DCSA APIs, TIC 4.0, WCO Data Model…). We author a faithful RDF interpretation where **every `owl:Class` cites the standard element it represents**. |
| **Blueprint** | `blueprints/` | Kairos's own opinion — archetype catalogs, reusable modelling patterns, and a handful of Kairos-authored classes for grains no standard covers. Not a standard; carries the highest bar for the last of those. |
| **Accelerator pack** | `accelerator-packs/` | A curated bundle that `owl:imports` the suites a sector needs, so a client hub imports one thing instead of nine. |
