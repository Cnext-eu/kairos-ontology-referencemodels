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
