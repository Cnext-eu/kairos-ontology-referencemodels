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

Every governed code list is one of **three kinds**. The kind answers two questions: where
the list's rows come from, and what the reference models give a hub.

| Kind | Examples | Rows come from | What the reference models ship |
|---|---|---|---|
| **1. Shipped standard list** | UNECE Rec 19 / 20 / 21, Incoterms (UNTDED 4053), currencies (ISO 4217), party roles (UNTDED 3035), ISO 3166-1 countries and 3166-2 subdivisions, UN/LOCODE function classifiers, IATA ONE Record code lists | vendored individuals under `authoritative-ontologies/`, refreshed by script | the class **and its members**, each code in `rdf:value`, with `owl:versionInfo` (snapshot) and `dcterms:source` |
| **2. Hub-loaded standard list** | UN/LOCODE locations (~116,000 rows, re-released twice a year) | the hub loads them from the standard's own release | the **target shape** only: class and properties, no members (`unlcdv:UNLOCODE`, with the loading instruction in `dcterms:description`) |
| **3. Client- or system-owned list** | a TMS container-type master, internal status codes, readable party roles such as `SHIPPER` | the client's own source systems | **no members.** At most an empty governed-class shell (`bsp/party#PartyRoleCode`, `mmt/party#TransportPartyRoleCode`) and, where a standard exists, the link to it |

Members are shipped only for kind 1. Shapes are shipped for all three kinds. Kinds 2 and
3 get no members and no refresh workflow from this repository.

**Telling the kinds apart in the graph.** Decide by where the class is defined and whether
it has members. Do not decide by an annotation:

- **kind 1:** the class has members (`owl:NamedIndividual`s typed by it) in the closure;
- **kind 2:** the class is defined under `authoritative-ontologies/` and has no members;
- **kind 3:** everything else: a derived-module shell, or a class the hub defines.

`kairos-ext:isReferenceData` does not decide the kind. It is the toolkit's hub-side
projection annotation, and a hub may set it on its own kind-3 class. Some kind-1 lists
(IATA, OMG-LCC) are not marked with it at all.

### Kind 1: take the shipped list in

A hub does not re-ingest a shipped list from the standard's PDF into its own bronze table:
every hub's copy would drift on its own, and nothing would identify two hubs' lists as the
same list. Instead the hub's governed class takes in the shared list:

```turtle
hub:TransportModeCode a owl:Class .
unece:TransportModeCodeList rdfs:subClassOf hub:TransportModeCode .
# every Rec 19 code (unece:TransportModeCodeList#0 … #9) is now a hub:TransportModeCode
```

The subclass runs from the shared list to the hub's class, not the other way round: the
hub's dimension is the standard's codes plus any extensions, and an extension must not
become a member of the standard's list. Join source data on (list, code), where the code
is each member's `rdf:value`, not on the member IRI: UN/CEFACT has announced a switch to
path IRIs, keeping today's fragment IRIs only as `owl:sameAs` aliases.

A **profile** (the hub accepts only part of the list) is a hub-side SHACL `sh:in` over the
shared members. Do not copy the subset into new individuals.

When the same standard ships twice, use the list the logistics pack routes:

| Dimension | Use | Also present (do not bind to) |
|---|---|---|
| Country | `unlcdv:Country` (UNCEFACT, linked to subdivisions and UN/LOCODE) | OMG-LCC ISO 3166-1 (FIBO closure) |
| Currency | `unece:CurrencyCodeList` (UNCEFACT) | IATA `code-lists:CurrencyCode` (air profile) |
| Transport mode | `unece:TransportModeCodeList` (all 10 Rec 19 codes) | IATA `code-lists:ModeCode` (air profile, linked by `skos:exactMatch`) |

### Kind 2: load the rows in the hub, to the shipped shape

The rows are too many, or change too often, to ship in an imported ontology. The hub binds
the standard's own release as an ordinary source and loads it to the shipped class and
properties, keyed on the code. For UN/LOCODE: the 5-character code, linked to the shipped
`unlcdv:Country`, `unlcdv:Subdivision` and `unlcdv:Function` members (see the UNCEFACT
module README, "UN/LOCODE locations: load in the hub").

### Kind 3: the client's list, linked to a standard where one exists

When the client or a source system defines the values, the **slot** is the standard's and
the **members** are the client's. Reference modules ship these governed classes as empty
shells: the value set is client master data and belongs to the blueprint's `reference-data`
domain, whose contract owns code lists and status codes. The enumeration constraint belongs
in SHACL, not OWL: `kairos-ontology suggest-shapes` (DD-076) derives `sh:in` enums from
bronze distinct-value evidence.

Where a standard exists, link to it:

- **The standard is shipped (kind 1):** each client member carries `skos:exactMatch` or
  `skos:closeMatch` to its standard code, so two hubs' lists are comparable through the
  shared code.
- **The standard exists but cannot be shipped** (ISO 6346 container size/type codes: ISO
  and BIC publish no free-reuse statement): the client list carries the standard's code as
  an **attribute** of each row. The derived ISO 6346 properties are where that code goes
  (BSP `commercial:equipmentSizeType`, DCSA `equipment:isoEquipmentCode` and
  `demurrage-detention:isoEquipmentCode`, MMT `equipment:equipmentSizeType`). A
  production example: the governed container-type list is the TMS's own master table,
  keyed on the TMS type code, with the ISO 6346 code as one column.

**Party roles are the worked example of the choice between kind 1 and kind 3.** A standard
list ships: UN/CEFACT's party roles (UNTDED 3035, 625 codes such as `CZ` consignor, `CN`
consignee, `CA` carrier), as `unece:PartyRoleCodeList`. But most hubs govern a short list
of readable roles (`SHIPPER`, `CONTROLLING_CUSTOMER`) that is partly client-specific. The
role classes therefore stay empty shells, and the hub chooses:

- **treat it as kind 1:** `unece:PartyRoleCodeList rdfs:subClassOf hub:PartyRoleCode`; or
- **treat it as kind 3 with links:** keep its own roles, each with `skos:exactMatch` (or
  `skos:closeMatch`) to its 3035 code, e.g.
  `hub:SHIPPER skos:closeMatch <https://vocabulary.uncefact.org/PartyRoleCodeList#CZ>`.

### Local extensions follow the list's kind

An extension (a code the standard lacks) lives where the rest of the list lives:

- **kinds 1 and 2:** a row in the hub's reference table, from a hub extension seed unioned
  in with an `origin` column. Not an individual in the hub ontology. Extensions only add
  rows; they never override a shipped row, and a local row is deprecated, not deleted,
  because facts point at it;
- **kind 3:** the client list itself.

The binding's `unique` check on the code is what catches a later release that assigns an
extension's code to something else. Where the standard reserves a user-assigned range, take
extension codes from it so this can never happen: ISO 3166-1 reserves `AA`, `QM`–`QZ`,
`XA`–`XZ` and `ZZ`. Most lists reserve nothing: Rec 19 uses all of `0`–`9`, ISO 4217's
`X` codes are mostly assigned (`XAU`, `XDR`, `XTS`, `XXX`), and Rec 20, Rec 21 and
UN/LOCODE have no reserved range. There, the `origin` column and the unique check are the
only protection.

### Crosswalks

A mapping from one *source system's* codes to the standard's (CargoWise `SEA` → Rec 19
`1`) is source-specific and stays in the hub. A mapping between two *standards* is shared
and ships here: `authoritative-ontologies/UNCEFACT/current/UNCEFACT-IATA-alignment.ttl`
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
