# Governed Code List

**Normativity:** naming — normative. Participants and cardinality rules — advisory.

## Problem

A classification dimension (equipment type, status code, cargo category) is typically carried on
a source record as a raw, source-typed string with no cross-source survivorship. When two source
systems disagree on the code for the same real-world classification, or when the same code means
different things in two systems, nothing in the model resolves the conflict — the raw string is
propagated as-is and the disagreement surfaces downstream instead of at the boundary.

## Applicability

Use this pattern whenever a classification dimension is sourced from more than one system, or
where a governed, cross-source authority for the value already exists (a standards body's code
list, an internal reference-data table). Do not use it for a value that is genuinely
system-local and has no cross-source counterpart to reconcile against.

## Participants (advisory)

- **Governed code-list entity** — the classification dimension itself, with a stable canonical
  code, independent of any source system's representation of it.
- **Source-typed raw value** — the as-received string or code from one particular source system,
  carried on the instance as evidence, never as the classification of record.
- **Survivorship rule** — which source's mapping wins when sources disagree, stated explicitly
  per code-list, not inferred implicitly from load order.

## Naming (normative)

| Element | Convention |
|---|---|
| Governed code-list class | `<Dimension>Code`, e.g. `EquipmentTypeCode`, `StatusCode` |
| Raw source value on the instance | `source<Dimension>Value`, e.g. `sourceEquipmentTypeValue` |
| Link from instance to governed code | `has<Dimension>Code`, e.g. `hasEquipmentTypeCode` |

## Composes with qualified-role-assignment

When the governed dimension is a **role** held through `qualified-role-assignment`'s link
entity, both patterns' applicability tests pass at once and they compose rather than compete:
the link property keeps that pattern's fixed, normative name `hasRole` — not
`has<Dimension>Code` — but takes this pattern's shape, ranging to the governed
`<Dimension>Code` class with the raw value on `source<Dimension>Value`. `has<Dimension>Code`
remains the normative name for every slot no other pattern claims. The reference party modules
ship this composition (`bsp/party#hasRole` → `PartyRoleCode`, `mmt/party#hasRole` →
`TransportPartyRoleCode`).

## Where the values live

The **slot** is the standard's; the **members** are the client's. Reference modules ship
governed code-list classes as empty shells (`bsp/party#PartyRoleCode`,
`mmt/party#TransportPartyRoleCode`): the value set is client master data and belongs to the
blueprint's `reference-data` domain, whose contract owns code lists and status codes. The
enumeration constraint itself belongs in SHACL, not OWL — `kairos-ontology suggest-shapes`
(DD-076) derives `sh:in` enums from bronze distinct-value evidence.

## Cardinality rules (advisory)

An instance has exactly one governed code per dimension (`1..1` via `has<Dimension>Code`), but
may carry `0..n` `source<Dimension>Value` properties if it originates from multiple systems that
each classify it — the governed code is the resolved value, the source values are the inputs
that were resolved.

## When NOT to use

A single-source, internally-consistent classification with no standards-body counterpart and no
cross-source disagreement to resolve does not need the governed-code-list split — a plain
`sh:in (...)`-constrained string property is simpler and equally correct.

## Worked example

```turtle
:EquipmentTypeCode a owl:Class .          # governed dimension

:hasEquipmentTypeCode a owl:ObjectProperty ;
    rdfs:domain :EquipmentAsset ;
    rdfs:range :EquipmentTypeCode .        # resolved, cross-source value

:sourceEquipmentTypeValue a owl:DatatypeProperty ;
    rdfs:domain :EquipmentAsset ;
    rdfs:range xsd:string .                # as-received per source system; evidence, not authority
```

## Anti-patterns

- **Propagating the raw source string as the classification of record**, with no governed
  dimension to resolve disagreements against. This reproduces the exact defect this pattern
  exists to close.
- **Implicit survivorship** — letting whichever source loads last silently overwrite the governed
  code, instead of stating a per-dimension survivorship rule.

## Grain collisions

- **Source-noun ≠ canonical grain** (general anti-pattern, applies broadly): a source column
  named e.g. `status` may carry the aggregate's current-state projection, a temporal status
  observation, or a lifecycle event — three different grains — and must be disambiguated before
  it is treated as a governed code at all.
