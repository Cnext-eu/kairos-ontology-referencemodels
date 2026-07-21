# Archetype Catalog

Per-archetype YAML files describing the ref-model modules and core concepts a given business archetype is expected to support. The catalog is **opinionated Kairos guidance** — see `../README.md` for the tier explanation.

## Status

**v0 — `schema_version: 1`.** Two archetypes ship in v0:
`shipping-carrier.yaml` and `freight-forwarder.yaml`. Additional seed archetypes
(terminal operator, b2b-credit-seller, multi-entity-group) require SME / ontology-team
review per `CONTRIBUTING.md` before being added.

## Layout

```
archetypes/
  VERSION                      # SemVer for this module, independent of repo VERSION
  README.md                    # this file
  freight-forwarder.yaml       # multimodal forwarder / logistics service provider
  shipping-carrier.yaml        # one archetype = one YAML
  _schema/
    archetype.schema.json      # JSON Schema (draft 2020-12) for archetype files
    outcome-codes.yaml         # shared conformance-outcome enum codes
```

**Filename = `id` convention.** Every `*.yaml` directly under `archetypes/` (excluding `_schema/` and dotfiles) is an archetype catalog file, and its top-level `id` field MUST equal the filename stem. This is enforced by `scripts/validate_structure.py`.

## Authoring a new archetype

1. Create `archetypes/<archetype-id>.yaml` (kebab-case id).
2. Populate the fields per `_schema/archetype.schema.json`. Minimum content:
   - `schema_version: 1`
   - `id` (== filename stem)
   - `label`, `description`
   - `compatible_with.repo_tag_range` (SemVer range against this repo's tags)
   - `compatible_with.ontology_versions` (per-ontology SemVer ranges, e.g. `DCSA: ">=1.3,<2"`)
   - `ref_model_modules[]` — list of `{ iri, tier }`; `iri` MUST be a published `owl:Ontology` IRI in this repo (canonical identifier, not a filesystem path).
   - `core_concepts[]` — list of `{ uri, tier, label }`; `uri` MUST resolve to an `owl:Class` declared in one of the referenced ontologies.
   - `tier` ∈ `required | recommended | optional` everywhere.
3. Validate locally:
   ```powershell
   python scripts/validate_structure.py
   python scripts/validate_archetypes.py
   ```
4. Bump `archetypes/VERSION` per SemVer rules:
   - **PATCH** — typo, label/description copy-edit, comment.
   - **MINOR** — new archetype YAML, new `core_concepts` entry, widened `compatible_with` range.
   - **MAJOR** — schema-version bump, removed/renamed archetype id, narrowed `compatible_with` range.
5. Add a CHANGELOG entry, open a PR. Two ontology-team approvals required per `CONTRIBUTING.md`; SME sign-off required for any archetype that may be perceived as client-specific.

## What does NOT live here

By design, the catalog contains **structure only** — no discovery-skill UX. The following all live in the toolkit repo (`kairos-design-discovery` skill):

- Interview questions for `core_concepts`.
- Prose descriptions of conformance outcomes (the shared **enum codes** are in `_schema/outcome-codes.yaml`; only the codes — never the prose — are shared between repos).
- Free-text "applies_when" signals or any signal-matching logic.
- Archetype selection / composition logic.

This separation keeps the catalog stable and decoupled from UX wording, i18n, and consumer-side workflow changes.

## Cross-repo contract

The contract between this folder and the toolkit consumer (`kairos-ontology-toolkit#203`) is documented in the comment thread on [issue #23](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/23). Key invariants:

| Concern | v0 value |
|---|---|
| Catalog root | `ontology-reference-models/blueprints/archetypes/` (no submodule fallback) |
| Serialization | YAML |
| Schema version | `1` (hard fail on mismatch) |
| Module references | `owl:Ontology` IRI, not filesystem paths |
| URI validation scope | `current/` only |
| Composition | unsupported in v0 — exactly one archetype id per discovery session |
| Archetype selection | manual in v0 |
| YAML parser | `yaml.safe_load` only |
| URI resolution network policy | local-only against checked-out graphs; no remote dereference |
