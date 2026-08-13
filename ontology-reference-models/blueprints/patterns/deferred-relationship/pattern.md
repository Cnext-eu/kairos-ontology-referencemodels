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
  will range over once its disposition resolves. Until then it is represented by a marked stub
  class in the hub's own namespace (see "Domain and range while the target is unresolved").

## Naming (normative)

| Element | Convention |
|---|---|
| Eventual object property | `<relationship>`, e.g. `hasEquipmentAllocation` |
| Interim scalar property | `<target>Reference`, e.g. `equipmentAllocationReference` |
| Stub target class marker | `rdfs:comment` starting with the literal token `STUB (deferred-relationship):` |

The interim property's name MUST be the target class's local name, lower-camel-cased, with
`Reference` appended — `EquipmentAllocation` → `equipmentAllocationReference`. It is derived
from the **target class**, never from the eventual object property's name; the two derivations
coincide only when the property happens to be named `has<Target>`. Never substitute a different
root word: renaming the concept between its interim and resolved forms is the specific failure
mode this rule closes — it is what produces divergent naming across hubs.

## Cardinality rules (advisory)

The interim scalar property's cardinality should match the eventual object property's declared
cardinality exactly. If the eventual relationship will be `0..n`, the interim scalar property
should be multi-valued too — do not narrow cardinality "temporarily" and widen it later; that
change is a breaking one for any consumer that already materialised the interim shape.

## Domain and range while the target is unresolved

The **domain is never deferred**. It is the class you are authoring, in your own hub, and it is
concrete by construction — declare `rdfs:domain` on both the eventual object property and the
interim scalar property from the start.

The **range is declared against a stub**: mint the target class IRI in your hub's namespace now,
declare it as an `owl:Class`, and mark it with an `rdfs:comment` whose text starts with the
literal token `STUB (deferred-relationship):`. The stub makes the relationship a complete,
visible edge in catalogs, diagrams and the navigator before the target domain is modelled, and
the marker keeps unmigrated stubs mechanically findable (`grep "STUB (deferred-relationship):"`).

A stub carries a migration duty: when the target module is onboarded, replace or align the stub
with the real class, re-point the range and any bindings that targeted it, and remove the marker.

**Never declare `rdfs:range owl:Thing` as a placeholder.** It passes `validate`, then fails
`compile` with a non-suppressible `safety.relationship-endpoint` error the moment a binding is
authored for the property — a latent build failure. An omitted range is *tolerated* by the
toolkit (it validates with a warning and compiles), but this pattern prescribes the marked stub:
the relationship stays visible, and the interim-scalar naming rule above stays mechanically
checkable because the target class is always declared.

## When NOT to use

- The target class is already canonical and stable — just declare the object property.
- The foreign key itself is unstable or unobserved in the source — there is nothing to carry yet;
  wait until the key is stable before adding even the interim property.

## Worked example

A booking references an equipment allocation before the equipment domain conforms:

```turtle
:EquipmentAllocation a owl:Class ;
    rdfs:label "Equipment Allocation (stub)"@en ;
    rdfs:comment "STUB (deferred-relationship): placeholder minted before the equipment domain is modelled. Replace with or align to the real class when the target module is onboarded, and re-point any bindings."@en .

:hasEquipmentAllocation a owl:ObjectProperty ;
    rdfs:domain :Booking ;
    rdfs:range :EquipmentAllocation .       # stub target — declared, marked, migrated later

:equipmentAllocationReference a owl:DatatypeProperty ;
    rdfs:domain :Booking ;
    rdfs:range xsd:string .                 # carries the FK today
```

Once the equipment domain resolves, hubs replace the stub with the real class, populate
`hasEquipmentAllocation` directly and retire `equipmentAllocationReference` — the name pairing
and the stub marker make that migration mechanical rather than a guessing exercise.

## Anti-patterns

- **Silently dropping the relationship** because the target is unresolved. This is the single
  most common failure this pattern replaces — the relationship existed in the source and its
  absence from the model is a data-loss defect, not a simplification.
- **Naming the interim property after the source column** instead of the eventual relationship
  (e.g. `equip_id_fk` instead of `equipmentAllocationReference`). This is exactly the "source-noun
  ≠ canonical grain" anti-pattern — a column name is evidence of nothing about the target concept.

## Grain collisions

None specific to this pattern; see the target concept's own grain-collision notes.
