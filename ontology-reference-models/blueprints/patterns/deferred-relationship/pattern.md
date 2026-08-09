# Deferred Relationship

**Normativity:** naming — normative. Participants and cardinality rules — advisory.

## Problem

A domain slice needs to land before the cross-domain key it should link to has conformed —
either because the target class is still `unresolved` in a canonical registry, or because the
target concept lives in a module that has not yet been onboarded. Modelling teams facing this
either (a) block the whole slice on the cross-domain decision, or (b) quietly drop the link and
lose the relationship entirely. Both are worse than declaring the relationship's eventual shape
now and carrying its scalar identifier as an interim property.

## Applicability

Use this pattern whenever a relationship's **target class** is not yet conformant, but the
**foreign-key value** is already available and stable in the source. Do not use it where the
target class already exists and is stable — declare the `owl:ObjectProperty` directly.

## Participants (advisory)

- The **eventual object property** — declared now, even though nothing populates it yet.
- The **interim scalar property** — a `owl:DatatypeProperty` carrying the same foreign-key value
  the object property will eventually connect.
- The **target concept** — the not-yet-conformant canonical registry entry the object property
  will range over once its disposition resolves.

## Naming (normative)

| Element | Convention |
|---|---|
| Eventual object property | `<relationship>`, e.g. `hasEquipmentAllocation` |
| Interim scalar property | `<target>Reference`, e.g. `equipmentAllocationReference` |

The interim property's name MUST be derivable from the eventual object property's name by
appending `Reference` — never a different root word. This is the specific rule that closes the
observed failure mode: renaming the concept between its interim and resolved forms is what
produces divergent naming across hubs.

## Cardinality rules (advisory)

The interim scalar property's cardinality should match the eventual object property's declared
cardinality exactly. If the eventual relationship will be `0..n`, the interim scalar property
should be multi-valued too — do not narrow cardinality "temporarily" and widen it later; that
change is a breaking one for any consumer that already materialised the interim shape.

## When NOT to use

- The target class is already canonical and stable — just declare the object property.
- The foreign key itself is unstable or unobserved in the source — there is nothing to carry yet;
  wait until the key is stable before adding even the interim property.

## Worked example

A booking references requested equipment before the equipment-asset anchor conforms:

```turtle
:hasEquipmentAllocation a owl:ObjectProperty ;
    rdfs:domain :Booking ;
    rdfs:range :EquipmentAsset .            # target not yet conformant — declared anyway

:equipmentAllocationReference a owl:DatatypeProperty ;
    rdfs:domain :Booking ;
    rdfs:range xsd:string .                 # carries the FK today
```

Once `equipment-asset` resolves, hubs populate `hasEquipmentAllocation` directly and retire
`equipmentAllocationReference` — the name pairing makes that migration mechanical rather than a
guessing exercise.

## Anti-patterns

- **Silently dropping the relationship** because the target is unresolved. This is the single
  most common failure this pattern replaces — the relationship existed in the source and its
  absence from the model is a data-loss defect, not a simplification.
- **Naming the interim property after the source column** instead of the eventual relationship
  (e.g. `equip_id_fk` instead of `equipmentAllocationReference`). This is exactly the "source-noun
  ≠ canonical grain" anti-pattern — a column name is evidence of nothing about the target concept.

## Grain collisions

None specific to this pattern; see the target concept's own grain-collision notes.
