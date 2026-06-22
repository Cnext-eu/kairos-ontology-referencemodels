# Kairos Blueprints

**Opinionated Kairos blueprints — not standards content.**

This folder is distinct from its siblings in `ontology-reference-models/`:

| Tier | Folder | What it is |
|------|--------|------------|
| Authoritative | `authoritative-ontologies/` | Official RDF/OWL published by standards bodies (e.g. FIBO). Verbatim. |
| Derived | `derived-ontologies/` | Kairos RDF interpretations of non-RDF standards (DCSA, MMT, BSP, …). Faithful to the source. |
| **Blueprint** | **`blueprints/`** | **Opinionated Kairos guidance layered _on top of_ the ref models.** Not a standard. Reflects how Kairos recommends a given business archetype should compose ref-model modules. |

Blueprints are versioned independently of the ref models they reference (see `archetypes/VERSION`). They are licensed under Apache-2.0 as part of the Kairos Community Edition by [Cnext.eu](https://cnext.eu) — see the root `NOTICE`.

## Contents

- [`archetypes/`](archetypes/) — Per-archetype YAML catalogs (one file per archetype) describing the ref-model modules and core concepts an archetype is expected to support. **Structure only** — no interview prose.

## Companion: sector discovery materials (in accelerator-packs)

Each archetype `archetypes/<id>.yaml` may be paired with a human-readable
**discovery script** at `accelerator-packs/<pack>/discovery/<id>.md`
(same filename stem). The discovery script holds the SME interview
questions, per-question outcome guidance, and the structural / lifecycle
relationship questions that the ontology itself cannot answer
(cardinality, aggregation, lifecycle timing).

Pairing is **convention-based** (filename stem match) and **soft** — an
archetype without a discovery doc is still valid; the toolkit skill
falls back to a generic concept-confirmation flow. `scripts/validate_archetypes.py`
emits a warning for unpaired archetypes.

Today's discovery materials:
- [`accelerator-packs/logistics/discovery/shipping-carrier.md`](../accelerator-packs/logistics/discovery/shipping-carrier.md)

## Consumer

The primary consumer of the archetype catalog + discovery scripts is the
**`kairos-design-discovery`** skill in
[`Cnext-eu/kairos-ontology-toolkit`](https://github.com/Cnext-eu/kairos-ontology-toolkit)
(CR #203). The cross-repo contract is documented in the comment thread
on [issue #23](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/23).

> **Contract note (v0.2, supersedes v0).** The earlier v0 contract
> placed discovery prose inside the toolkit skill. v0.2 moves it into
> the accelerator-pack so each pack ships its own sector interview
> materials. The toolkit skill becomes a pure consumer / orchestrator.
