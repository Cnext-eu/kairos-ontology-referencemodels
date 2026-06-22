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

- [`archetypes/`](archetypes/) — Per-archetype YAML catalogs (one file per archetype) describing the ref-model modules and core concepts an archetype is expected to support.

## Consumer

The primary consumer of the archetype catalog is the **`kairos-design-discovery`** skill in [`Cnext-eu/kairos-ontology-toolkit`](https://github.com/Cnext-eu/kairos-ontology-toolkit) (CR #203). The cross-repo contract is documented in the comment thread on [issue #23](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/23).
