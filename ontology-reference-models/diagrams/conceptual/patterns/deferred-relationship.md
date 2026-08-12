# Pattern: Deferred relationship

**Closes: naming drift when a link lands before its target conforms.** A slice needs to reference
a cross-domain key before the target class exists. Rather than block the slice or silently drop
the link, declare the eventual object property **now** and carry the foreign key on an interim
scalar whose name is mechanically derived from it.

```mermaid
flowchart LR
  BOOKING["Booking"]
  ASSET["EquipmentAsset<br/><small>target — not yet conformant</small>"]:::pending

  BOOKING -->|"hasEquipmentAllocation<br/>(declared now, nothing populates it yet)"| ASSET
  BOOKING -->|"equipmentAllocationReference : xsd:string<br/>(carries the FK today)"| FK["interim scalar value"]

  classDef pending fill:#fff3d6,stroke:#d8a13b,stroke-dasharray:4;
```

## The naming rule (normative)

The interim scalar's name **must** be the eventual object property's target with `Reference`
appended — never a different root word. That pairing makes the eventual migration mechanical.

```mermaid
flowchart LR
  OBJ["hasEquipmentAllocation<br/><small>eventual object property</small>"]
  SCALAR["equipmentAllocationReference<br/><small>= target + 'Reference'</small>"]
  OBJ -.->|"same root word"| SCALAR

  BAD["equip_id_fk<br/><small>named after the source column</small>"]:::bad
  BAD -.->|"rejected: a column name is<br/>evidence of nothing"| OBJ
  classDef bad fill:#ffe3e3,stroke:#d84b4b;
```

Once the target conforms, hubs populate `hasEquipmentAllocation` directly and retire the interim
scalar. **Silently dropping the relationship** because the target is unresolved is the data-loss
defect this pattern replaces.

Source: [`blueprints/patterns/deferred-relationship`](../../../blueprints/patterns/deferred-relationship/pattern.md).
