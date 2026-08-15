# Financial Services — Sector Discovery Materials

This folder is reserved for the Financial Services pack's own SME interview scripts, following
the same convention as the logistics pack's [`discovery/README.md`](../../logistics/discovery/README.md):
one `discovery/<archetype-id>.md` per archetype in
[`blueprints/archetypes/`](../../../blueprints/archetypes/), matched by filename-stem convention.

## Status: no archetypes yet

Unlike logistics, this pack has no archetypes under `blueprints/archetypes/`, no `blueprint/`
layer (canonical class registry, capability coverage, evidence), and no `.intro/` business-
architecture docs. `manifest.yaml` declares six `target_sectors`, but none has a machine catalog
yet, so there is nothing for a discovery doc to pair with. This folder is intentionally empty of
sector content until that changes — do not add a discovery doc here without first adding the
matching archetype under `blueprints/archetypes/`.

A previous version of this file was a stale, uncorrected copy of the logistics pack's
`discovery/README.md`, complete with a `shipping-carrier` index entry pointing at a file that
was never part of this pack. See the logistics pack's own `discovery/README.md` for the real
convention, schema, and authoring steps once this pack is ready to adopt them.

## Adding the first archetype

1. Author `blueprints/archetypes/<archetype-id>.yaml` against
   `blueprints/archetypes/_schema/archetype.schema.json`, scoped to one of this pack's declared
   `target_sectors`.
2. Add `discovery/<archetype-id>.md` here, following the structure documented in the logistics
   pack's `discovery/README.md`.
3. Validate with `python scripts/validate_archetypes.py` and `python scripts/validate_structure.py`.
4. Bump this pack's `VERSION` (additive ⇒ MINOR).
