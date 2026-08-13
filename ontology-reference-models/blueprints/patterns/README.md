# Pattern Library

Sector-neutral modelling craft — shapes and naming conventions that recur across archetypes and
accelerator packs, harvested from client hub implementations. Opinionated Kairos guidance, per
`../README.md`'s tier explanation — not a standard, and not a canonical-class decision.

## Why this exists

Reference-model convergence work regularly surfaces gaps that are shapes, not classes: a
deferred cross-domain link, a qualified role assignment, a timestamp triple, a governed code
list. Client hubs re-derive these by hand, independently, with no shared vocabulary — the
observed failure mode is a single hub carrying four different naming conventions for the same
requested/planned/actual timestamp triple across four classes, because nothing normative existed
to copy. This library is the shared copy.

## Status

**v0.3 — markdown-first, schema-validated.** `_schema/pattern.schema.json` now exists and
`scripts/validate_structure.py` validates every `pattern.yaml` against it: open at the top level
(custom top-level keys remain fine — the loader preserves them in `extra`), strict inside every
list-entry shape, because the v0.2 defect class was a wrong-but-parseable key *inside* an entry.
Normative denylists are structured fields on the anti-pattern that owns them
(`banned_name_tokens` / `applies_to_ranges` / `exemptions`, first used by `temporal-quartet`),
with matching semantics defined in the owning pattern's `pattern.md` — every exemption carries a
cited reason, so each place a normative rule yields is a visible, audited line item.

The v0.2 statement below is kept for history:

**v0.2 — markdown-first, parse-guarded, no JSON Schema yet.**

The v0.1 statement here — "there is no toolkit consumer for this folder yet" — was **wrong by the
time anyone checked**. `kairos-ontology-toolkit` ships
`src/kairos_ontology/core/pattern_loader.py`, which reads every `pattern.yaml` in this folder for
the `kairos-design-domain` authoring flow. Its loader is deliberately lenient *because this README
told it the library has no schema*, so the two repos were each relying on the other's assumption.

That cost a real defect: `temporal-quartet/pattern.yaml` shipped in v1.13.0 with a stray `rule:`
key inside a block sequence — **invalid YAML**, which reads perfectly fine to a human. The toolkit
skips a malformed pattern silently during bulk listing, so the one pattern in this library that
ships *normative* naming was invisible to the design flow for its entire life, and nothing in
either repo failed. `multimodal-order-leg` then copied the same shape.

`scripts/validate_structure.py` now parses every `pattern.yaml` and checks its `id` against its
directory name. That is a floor, not the schema: a full `_schema/pattern.schema.json` is still
owed, and both original triggers for writing it have now fired (a consumer exists; more than one
person is authoring). See the CHANGELOG "Known gaps".

**Structural rule that follows from the defect:** `naming_conventions` is a **list of entries and
nothing else**. Prose that applies to the whole block goes in a sibling top-level `naming_rule`
key — never as a trailing mapping key inside the list. Custom top-level keys are fine (the loader
preserves unknown keys in an `extra` dict), so there is no reason to smuggle one into a sequence.

## Normativity

Each `pattern.md` states its normativity **per section**, not as a single blanket label:

- **Naming conventions ship normative.** This is where the CR-observed cost concentrated — hubs
  inventing incompatible names for the same shape — so it ships enforceable from day one.
- **Structural guidance (participants, cardinality rules) ships advisory.** The shapes are not
  proven across enough implementations yet to freeze; making them normative before that invites
  silent non-conformance, which is worse than advisory guidance that gets followed.

A pattern is advisory or normative per its own content, not per this README — always check the
`normativity` block in the individual `pattern.yaml`.

## Layout

```
patterns/
  VERSION                       # SemVer for this module, independent of repo VERSION
  README.md                     # this file
  <pattern-id>/
    pattern.md                  # problem, applicability, when NOT to use, worked example,
                                 # anti-patterns, grain collisions
    pattern.yaml                # naming conventions — the part that is normative
    template.ttl                # OPTIONAL — placeholder-namespace OWL fragment
```

**No `owl:versionInfo` in `template.ttl`.** `scripts/version_manager.py` scans every folder under
`blueprints/` that has a `VERSION` file and requires every `owl:versionInfo` literal in every
`.ttl` beneath it to equal that file's contents. A `template.ttl` is a namespace-placeholder
fragment for hubs to copy, not a versioned ontology module — it must carry no `owl:versionInfo`,
or `version_manager.py check` fails in CI the moment this module's version diverges from the
placeholder's. Do not add one "for consistency" with the derived ontologies.

## Contents

| Pattern | Closes declared gap(s) |
|---|---|
| [`deferred-relationship`](deferred-relationship/pattern.md) | — (new) |
| [`qualified-role-assignment`](qualified-role-assignment/pattern.md) | 1, 2, 7 |
| [`temporal-quartet`](temporal-quartet/pattern.md) | 8 (partly) |
| [`governed-code-list`](governed-code-list/pattern.md) | 8 |
| [`multimodal-order-leg`](multimodal-order-leg/pattern.md) | 5 |

Gap numbers refer to `accelerator-packs/logistics/current/blueprint/convergence-analysis.md`
§"Explicit reference-model gaps".

## Pack linkage

A pack's `capability-coverage.yaml` may reference a pattern by id in an optional `pattern_ids:`
field per capability (see `_schema/capability-coverage.schema.json` in each pack). This is the
only cross-file link that exists today — there is no link from `blueprints/archetypes/` into
this folder, and no toolkit CLI path reaches it. See the root plan's "Known gap" note for why,
and the companion GitHub issue on `kairos-ontology-toolkit` for the proposed fix.
