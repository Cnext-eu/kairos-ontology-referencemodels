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

Who maintains the list decides where its members live. There are two cases.

**Standards-body lists — the reference models ship the members.** When a standards body
publishes and maintains the list (UNECE Rec 19 transport modes, Rec 20 units of measure,
Rec 21 package types), its members are vendored as reference data under
`authoritative-ontologies/` (`authoritative-ontologies/UNCEFACT/`, refreshed by
`scripts/download_uncefact_codelists.py`). A hub does not re-ingest the list from the
standard's PDF into its own bronze table: every hub's copy would drift on its own, and
nothing would identify two hubs' lists as the same list. Instead the hub's governed class
takes in the shared list:

```turtle
hub:TransportModeCode a owl:Class .
unece:TransportModeCodeList rdfs:subClassOf hub:TransportModeCode .
# every Rec 19 code (unece:TransportModeCodeList#0 … #9) is now a hub:TransportModeCode
```

The subclass runs from the shared list to the hub's class, not the other way round: the
hub's dimension is the standard's codes plus any extensions, and an extension must not
become a member of the standard's list. Each shared member carries its code in
`rdf:value`, which is the join key to source data. Two variations stay in the hub:

- **A profile** (the hub accepts only part of the list) is a hub-side SHACL `sh:in` over
  the shared members. Do not copy the subset into new individuals.
- **An extension** (codes the standard lacks) is a hub-local individual of the hub's
  governed class. Extensions are client members, exactly as in the next case.

**Client lists — empty shells.** When the client defines the values (party roles,
internal status codes), the **slot** is the standard's and the **members** are the
client's. Reference modules ship these governed classes as empty shells
(`bsp/party#PartyRoleCode`, `mmt/party#TransportPartyRoleCode`): the value set is client
master data and belongs to the blueprint's `reference-data` domain, whose contract owns code
lists and status codes. The enumeration constraint belongs in SHACL, not OWL:
`kairos-ontology suggest-shapes` (DD-076) derives `sh:in` enums from bronze distinct-value
evidence.

**Crosswalks.** A mapping from one *source system's* codes to the standard's (CargoWise
`SEA` → Rec 19 `1`) is source-specific and stays in the hub. A mapping between two
*standards* is shared and ships here: `authoritative-ontologies/UNCEFACT/current/UNCEFACT-IATA-alignment.ttl`
links IATA ONE Record codes to UNECE codes, and the derived transport-mode slots state how
their standard's values map to Rec 19 (see `rdfs:seeAlso` on each slot).

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
