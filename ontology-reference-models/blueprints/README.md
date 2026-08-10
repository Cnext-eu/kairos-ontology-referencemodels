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
- [`patterns/`](patterns/) — Sector-neutral modelling craft (shapes and naming conventions) harvested from client hub implementations. Naming conventions are normative; structural guidance is advisory. See `patterns/README.md`. Not part of the `archetypes/` cross-repo contract, but **it does have a toolkit consumer** — `kairos-ontology-toolkit`'s `core/pattern_loader.py` reads every `pattern.yaml` for the `kairos-design-domain` authoring flow. An earlier version of this line claimed there was none; that error let an unparseable `pattern.yaml` ship undetected.
- [`ontology/`](ontology/) — **Kairos-authored OWL classes** for business grains that a standards audit has shown no installed standard expresses. The only blueprint module that declares classes rather than describing how to compose existing ones, so it carries the highest admission bar — see `ontology/README.md`. Referenced from `archetypes/` like any other module IRI.

## Anchor-selection invariant

When a pack or archetype names the class for a concept, **the anchor must be the most general
class that covers every sector the pack declares**. A narrower anchor silently restricts the
pack: anchoring `equipment-asset` on DCSA `Container` excludes the non-containerised operators
that the logistics pack's own `manifest.yaml` `target_sectors` lists, so the anchor moved to MMT
`TransportEquipment`.

Two corollaries, both learned the hard way:

- **Generality is judged against the pack's declared sectors, not against the richest available
  model.** A more detailed standard class is not a better anchor if its detail is mode- or
  sector-specific.
- **Where a distinction really is mode- or sector-specific, push it down a grain rather than
  narrowing the anchor.** Transport mode does not narrow the transport order; it specialises the
  leg, and the mode-bound standard binds at the leg's carrier reservation. See
  [`patterns/multimodal-order-leg`](patterns/multimodal-order-leg/pattern.md).

`scripts/validate_archetypes.py` enforces a lexical proxy for this (advisory only): it warns when
a concept's `authority` text admits a scope qualifier — "for _X_ scope" — that has no counterpart
in the pack's `target_sectors`. It cannot reason about cross-standard generality, so the warning
is a prompt to re-check the anchor, not a proof that one is wrong.

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
