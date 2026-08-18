# Logistics — Sector Discovery Materials

This folder contains **sector-specific discovery questions** that complement
the machine-readable archetype catalog at
[`ontology-reference-models/blueprints/archetypes/`](../../blueprints/archetypes/).

## Why these live in the accelerator-pack

Per the v0.2 contract (revising the original PR #24 v0 contract):

| Concern | Where it lives |
|---|---|
| **Structure** — which ref-model modules + classes a sector typically needs | `blueprints/archetypes/<id>.yaml` (machine catalog, `schema_version: 1`) |
| **Prose** — SME interview questions, why each concept matters, outcome guidance | `accelerator-packs/<pack>/discovery/<id>.md` (this folder) |
| **Runtime** — orchestrate the interview, persist answers, render the conformance report | `kairos-design-discovery` skill in the `kairos-ontology-toolkit` repo |

The accelerator-pack is the right home for sector prose because:

1. It already hosts business-architecture docs in
   [`.intro/`](../.intro/) aimed at the same audience.
2. [`manifest.yaml`](../manifest.yaml) already declares `target_sectors`
   — one discovery doc per target sector keeps it cohesive.
3. The pack is already version-managed and distributed as a unit.

## Convention

For each archetype `blueprints/archetypes/<id>.yaml` an accelerator-pack
**may** ship a matching `discovery/<id>.md` (same filename stem).

- The match is **convention-based** (filename stem). No new schema field
  is added to the archetype YAML.
- Pairing is **soft**: an archetype without a discovery doc is still
  valid — the toolkit skill will fall back to a generic
  per-`core_concepts` confirmation flow.
- An accelerator-pack may carry discovery docs for archetypes that live
  outside its own pack (e.g., a multi-sector composite); the convention
  is "search every pack's `discovery/` for the matching id".

A soft validator check
([`scripts/validate_archetypes.py`](../../../../scripts/validate_archetypes.py))
warns if no matching discovery doc is found in any pack.

## Shared outcome codes

All discovery docs use the shared enum codes from
[`blueprints/archetypes/_schema/outcome-codes.yaml`](../../blueprints/archetypes/_schema/outcome-codes.yaml):

| Code | Meaning |
|---|---|
| `conforms` | Customer's term + structure match the ref-model concept |
| `conforms-with-rename` | Same structure, different terminology — alias only |
| `partial` | Concept partially present; some attributes missing |
| `deviates` | Customer's model materially differs — needs negotiation |
| `not-applicable` | Concept is out of scope for the customer's operation |

The shared codes intentionally carry **no prose** — each discovery doc
authors its own outcome guidance per question. This avoids tight coupling
between catalog and interview script.

## Index

| Archetype id | Discovery doc | Target sector |
|---|---|---|
| `freight-forwarder` | [`freight-forwarder.md`](./freight-forwarder.md) | Freight forwarder, NVOCC, multimodal logistics service provider |
| `shipping-carrier` | [`shipping-carrier.md`](./shipping-carrier.md) | Ocean carrier (vessel operators), short-sea, ro-ro, barge |
| `unit-load-carrier` | [`unit-load-carrier.md`](./unit-load-carrier.md) | Non-containerised unit-load / ro-ro / short-sea carrier — trailer, swap-body, cassette operations with own-account and subcontracted road haulage |

## Picking a starting archetype

Clients describe themselves in market vocabulary, which does not map one-to-one onto the
archetype ids. The ids name an **operating model** — what the business does, which is what
determines the module set. Market terms name a **commercial position**. Use this table to
get from one to the other, then answer the scope axes below.

| Client describes itself as | Start from | Typical `service-model` |
|---|---|---|
| Freight forwarder | `freight-forwarder` | `3pl` |
| NVOCC / NVO | `freight-forwarder` | `3pl` + `2pl` (contracts as principal) |
| 3PL / LSP | `freight-forwarder` | `3pl` |
| 4PL / control tower / lead logistics provider | `freight-forwarder` | `4pl` |
| Shipping line, ocean carrier, container carrier | `shipping-carrier` | `2pl` |
| Short-sea / feeder operator | `shipping-carrier` | `2pl` |
| Ferry operator, ro-ro operator, unit-load operator | `unit-load-carrier` | `2pl` |
| Barge / inland-waterway operator | `shipping-carrier` | `2pl` |
| Road haulier / trucking company | *no archetype yet* — see backlog | `2pl` |
| Terminal / stevedore | *no archetype yet* — see backlog | — |
| Customs broker | *no archetype yet* — see backlog | — |
| Shipper / BCO running its own TMS | *no archetype yet* — see backlog | `1pl` |

**xPL is positioning vocabulary, not a standard.** There is no ISO, CEN, UN/CEFACT or WCO
definition of 1PL–5PL — 4PL is an Accenture coinage from 1996 — and none of the party-role
code lists the derived ontologies are grounded in (UN/EDIFACT 3035, WCO, DCSA, IMO) contains
an xPL code. Most real operators occupy several rungs at once: a forwarder that is also an
NVOCC is `3pl` **and** `2pl`. So `service-model` is recorded multi-valued, is a routing hint
only, and never substitutes for the axes that actually select modules.

**Backlog.** [`manifest.yaml`](../manifest.yaml) `target_sectors` claims road carrier,
terminal operations and customs brokerage, but no archetype covers them, and there is no
shipper/BCO archetype although
[`multimodal-order-leg`](../../../blueprints/patterns/multimodal-order-leg/pattern.md)
"Applicability" names a shipper's own TMS as in scope. Each needs its own SME review before
being added — see `.docs/wip/discovery-scope-selection-cr.md`.

## Scope axes

Every discovery guide opens with a **Scope profile** in its `§0`, answered *before* the
business-area sections. The axes are defined once here; each guide carries only its own
consequence table, because the same answer implies different modules for a forwarder than
for a carrier.

| Axis | Values | What it decides |
|---|---|---|
| `modes-served` **(multi)** | `ocean` `road` `rail` `air` `barge` | Which mode-bearing leg subclasses and which mode-bound reservation standards the hub needs |
| `geographic-scope` | `port-to-port` `door-to-door` `both` | Whether pre/on-carriage, inland legs and warehouse locations are in the model at all |
| `service-model` **(multi)** | `1pl` `2pl` `3pl` `4pl` | Whether the order grain (grain 1) is required, and whether asset modules apply |
| `financial-scope` | `charges-only` `full-billing` `margin-management` | How much of the cost / revenue apparatus comes with the charge line — whether the hub holds only what it charges, the full billing document set, or cost and sell against one job |
| `customs-role` | `lodges` `prepares` `tracks-only` | Whether the customs party, document and facilitation modules are in the model at all, or the declaration reduces to a status reference |
| `tonnage-model` | `owns-operates` `charters-in` `slot-buyer` | Whether the vessel-operator regulatory block (statutory certificates, ship security, MARPOL plans, crew) applies at all, or the carrier only buys capacity on someone else's sailing |
| `unit-mix` **(multi)** | `accompanied-trailers` `unaccompanied-trailers` `swap-bodies` `cassettes` `vehicles` `reefer-trailers` | Which unit classes roll onto the deck — selects the automotive, reefer-monitoring and passenger-manifest modules. Not a mode axis: how a unit travels stays on the leg |

Mode targets are **not** restated per guide. They are cited from
[`multimodal-order-leg` `pattern.yaml`](../../../blueprints/patterns/multimodal-order-leg/pattern.yaml)
`mode_bindings`, which carries `module_iris` (grain 3, the reservation-grain standard) and
`leg_module_iris` (grain 2, where mode is stated) per mode. That block is the single source.

### Resolution rules

1. An axis may **promote** a module's tier (`optional` → `recommended` → `required`). Every
   module an axis can select **must already be declared** in the archetype's
   `ref_model_modules`, at `optional` if it is only sometimes needed. The archetype is the
   complete menu of what that operating model can ever require; the axis only chooses from
   it. An axis that needs a module the archetype does not declare is a signal the
   *archetype* is wrong — fix it there, not in the prose.
2. An axis may **never demote** a module the archetype declares `required`. The archetype is
   the floor; axes only ever tune upward.
3. A scope answer that puts a concept out of scope produces a **pre-seeded
   `not-applicable`** — recorded with `needs_confirmation: true` for the SME to confirm, not
   a verdict the interviewer applies silently.

Rule 1 is what makes the prose checkable: because `ref_model_modules` is exactly what the
toolkit's `archetype_loader` reads, an axis that stays inside it can never promise a module
the machine cannot deliver. The one deliberate exception is a **grain-3 mode target** (the
RAIL module IRIs, the IATA ONE Record IRI) — those are cited from `pattern.yaml`
`mode_bindings`, are hub-local bindings rather than pack modules, and are validated against
that block instead.

Rule 3 is why no new outcome code was needed: scope answers land on the existing
[`outcome-codes.yaml`](../../blueprints/archetypes/_schema/outcome-codes.yaml) enum, so the
cross-repo contract is untouched.

### Limits, and what is coming

Today the axes are **prose consumed by the interviewer** (human or skill). Nothing computes
a module set from them: the toolkit's `archetype_loader` reads `ref_model_modules`,
`core_concepts` and the discovery doc's *path*, and does not parse the markdown. Machine
resolution needs a `scope-axes.yaml` registry **and** a consumer, specified together in
`.docs/wip/discovery-scope-selection-cr.md`. Shipping the registry first would leave a
fourth unread machine file in a repo that already has stale ones.

Two guards exist meanwhile, and both **fail the build** rather than warn:
`scripts/validate_archetypes.py` check 6 asserts that every module IRI a Scope profile names
is resolvable and present in that archetype's `ref_model_modules`; check 7 asserts that
`pattern.md`'s mode table agrees with `pattern.yaml` `mode_bindings` and that every
`target_iris` entry is a declared `owl:Class`.

**Composition is still unsupported** — exactly one archetype id per discovery session (see
[`blueprints/archetypes/README.md`](../../blueprints/archetypes/README.md)). A client that is
genuinely both a carrier and a forwarder needs archetype composition; the axes tune one
archetype, they do not merge two.

## Adoption order

The scope axes decide *which* domains a client needs. This decides *what order* to build them
in. It is guidance, not a contract — nothing validates it — but it reflects the dependency
reality that most domains reference a party, and almost nothing references claims.

```
Phase 1: party → mdm → commercial → booking
Phase 2: consignment → cargo → equipment → route-schedule
Phase 3: vessel-maritime → terminal-operations → events
Phase 4: customs → dangerous-goods → sustainability → documents
Phase 5: financial → claims → compliance → reference-data
```

Start with **party**: it is the most common MDM case and nearly every other domain points at
it, so getting it wrong is expensive later. Specialist domains — `roro`, `automotive`,
`intermodal` — enter wherever the client's operations put them, not at a fixed phase; the
`modes-served` and `service-model` axes above are what pull them in.

Domain ids are those in
[`client-hub-blueprint/data-domains.yaml`](../client-hub-blueprint/data-domains.yaml), which
is the authority for what each domain owns and which reference modules it imports.

## Adding a new sector

1. Add a machine catalog at `blueprints/archetypes/<new-id>.yaml`
   (use the `kairos-design-discovery` skill workflow, or hand-author
   against the JSON Schema).
2. Add `discovery/<new-id>.md` here following the structure of
   `shipping-carrier.md`:
   - §0 How to use this guide
   - §1..N business-area sections, each with: *why it matters*,
     *questions*, *maps to* (catalog URIs), *outcome guidance*
   - Final section: **Structural & lifecycle relationships** — the
     cardinality / lifecycle / aggregation questions that the ontology
     cannot infer
   - Naming & identifier conventions
3. Add the row to the Index table above.
4. Bump pack `VERSION` (additive ⇒ MINOR).

## Version

Bound to the parent pack version — see
[`../VERSION`](../VERSION).
