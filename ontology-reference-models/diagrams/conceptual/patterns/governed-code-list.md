# Pattern: Governed code list

**Closes gap 8.** A classification dimension (equipment type, status, cargo category) arrives as a
raw source string. When two systems disagree on the code — or the same code means different things
— nothing resolves it and the conflict leaks downstream. This pattern splits the **governed,
cross-source code** from the **raw source value**, with an explicit survivorship rule.

```mermaid
flowchart LR
  ASSET["EquipmentAsset"]
  CODE["EquipmentTypeCode<br/><small>governed — the value of record</small>"]:::gov
  RAW1["sourceEquipmentTypeValue<br/><small>system A — as received</small>"]:::raw
  RAW2["sourceEquipmentTypeValue<br/><small>system B — as received</small>"]:::raw

  ASSET -->|"hasEquipmentTypeCode (1..1)"| CODE
  ASSET -->|"0..n"| RAW1
  ASSET -->|"0..n"| RAW2
  RAW1 -. survivorship rule .-> CODE
  RAW2 -. survivorship rule .-> CODE

  classDef gov fill:#e8f7e9,stroke:#3aa657;
  classDef raw fill:#fff3d6,stroke:#d8a13b;
```

The governed code is the **resolved** value (`1..1`); the source values are the `0..n` inputs that
were resolved. Which source wins is stated **per code-list**, never inferred from load order.

## The rejected shape

```mermaid
flowchart LR
  SRC["raw source string"]:::bad -->|"propagated as the classification of record,<br/>no governed dimension to resolve against"| DOWN["disagreement surfaces downstream ✗"]
  classDef bad fill:#ffe3e3,stroke:#d84b4b;
```

Naming is **normative**: `<Dimension>Code`, `source<Dimension>Value`, `has<Dimension>Code`. A
single-source, internally-consistent classification with no cross-source counterpart does not need
the split — a plain `sh:in (...)` string is simpler.

Source: [`blueprints/patterns/governed-code-list`](../../../blueprints/patterns/governed-code-list/pattern.md).
