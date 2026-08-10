# CR — machine-readable scope selection for discovery

**Status:** proposed
**Repos:** `kairos-ontology-referencemodels` (this one) + `kairos-ontology-toolkit`
**Precedent:** CR #203, which established `_schema/outcome-codes.yaml` as a cross-repo
contract — codes here, prose in the skill.

## Problem

The discovery guides now carry a **scope switchboard** (`§0 Scope profile` in each guide,
axes defined in `accelerator-packs/logistics/discovery/README.md`). It works: an SME's
answers to `modes-served`, `geographic-scope` and `service-model` decide which modules a
client hub needs. But it works **only because a human or an LLM reads the prose**. Nothing
computes a module set.

That was a deliberate choice, and this CR is the other half of it.

## Why the registry was not shipped first

The toolkit's `archetype_loader` consumes exactly three things from this repo's published
surface:

- `ref_model_modules[iri, tier]`
- `core_concepts[uri, tier, label]`
- `locate_discovery_doc()` — which returns **the markdown path only** and never parses it

A grep of the installed toolkit (4.5.0rc4) for `mode_bindings|scope|axes|profile` returns
zero matches. This repo already demonstrates what happens to machine files with no reader:

| File | Reader | Outcome |
|---|---|---|
| `patterns/multimodal-order-leg/pattern.yaml` `mode_bindings` | none | said `extension-point` for air and rail for two releases after the models landed |
| `accelerator-packs/logistics/current/blueprint/capability-coverage.yaml` | none | stayed at `accelerator_version: 1.8.0` while the pack reached 1.9.0 |

Shipping a `scope-axes.yaml` before its consumer would have made a third. So the switchboard
went into prose — which *is* read — and the machine surface waits for this CR, so registry
and reader land together.

## Proposed contract

### 1. New file in this repo

`accelerator-packs/<pack>/discovery/_scope/scope-axes.yaml`, plus
`_scope/_schema/scope-axes.schema.json` (draft 2020-12, `additionalProperties: false`,
reusing the `tier` enum values from `blueprints/archetypes/_schema/archetype.schema.json`).

```yaml
schema_version: 1
axes:
  - id: modes-served
    multi_valued: true
    applies_to: [freight-forwarder, shipping-carrier, unit-load-carrier]
    default: []
    values:
      - value: rail
        promotes:                       # tier promotions only — see resolution rule 1
          - { iri: "https://www.kairosflow.ai/ont/mmt/inland-transport", tier: required }
        mode_binding_ref: rail          # grain-3 target resolved from pattern.yaml
      - value: ocean
        promotes:
          - { iri: "https://www.kairosflow.ai/ont/dcsa/booking", tier: required }
    unselected_value_drops:             # -> pre-seeded not-applicable
      rail: ["https://www.kairosflow.ai/ont/mmt/inland-transport#RailLeg"]
```

Note `mode_binding_ref`: the registry **must not restate** mode targets. It points at
`blueprints/patterns/multimodal-order-leg/pattern.yaml` `mode_bindings`, which already
carries `module_iris` (grain 3) and `leg_module_iris` (grain 2) per mode. One source.

### 2. Resolution algorithm

Input: archetype id + `{axis_id: [selected values]}`. Output: effective module set with
tiers, plus a list of pre-seeded `not-applicable` concept URIs.

1. Start from the archetype's `ref_model_modules` — this is the floor **and the ceiling of
   what may be selected**. An axis may only promote a module the archetype declares; if an
   axis needs one it does not, the *archetype* is wrong and must be fixed there.
2. For each selected value, apply `promotes` as `max(current_tier, promoted_tier)` on the
   ordering `optional < recommended < required`. Never demote.
3. For each unselected value, add `unselected_value_drops` URIs to the pre-seed list.
4. Resolve `mode_binding_ref` against `pattern.yaml` and surface the grain-3 target with its
   `import_policy` (`reference-only` for IATA — catalogue it, never add it to a pack's
   `includes`).
5. Emit pre-seeds as `outcome: not-applicable` + `needs_confirmation: true`. **No new
   outcome code** — this is why the switchboard needed no change to
   `_schema/outcome-codes.yaml`, and the CR must preserve that.

### 3. Toolkit changes

- `archetype_loader`: load the paired `_scope/scope-axes.yaml` (search every pack, same
  filename-stem convention as discovery docs); expose `axes` on the catalog object; soft-warn
  when an archetype has no axes, as it already does for a missing discovery doc.
- `discovery-conformance load --archetype <id> [--scope axis=v1,v2 ...]`: return the resolved
  module set and pre-seed list alongside today's `core_concepts` + `topology`. Absent
  `--scope`, behave exactly as today — this must stay backward-compatible.
- `conformance_artifact.build_artifact()`: persist the answered scope profile in the artifact
  so a later lifecycle stage can tell "not modelled" from "out of scope for this client".
  This is the real payoff — today that distinction is lost.
- Mirror `tests/test_refmodels_contract.py` with a scope-axes case.

### 4. This repo's side

- Author `_scope/scope-axes.yaml` from the prose tables already in the three guides — they
  were written to be mechanically transcribable, one table row per axis value.
- Extend `scripts/validate_archetypes.py` check 6: today it asserts the *prose* names only
  declared modules and that `pattern.md` agrees with `pattern.yaml`. Add: the registry and
  the prose tables agree. At that point the prose becomes generated-or-checked, not authored
  twice.

## Sequencing

Land the toolkit reader first (or in the same coordinated pair, as CR #203 did). Do not merge
the registry into this repo until `archetype_loader` reads it — that is the whole point of
this document.

---

## Deferred backlog (recorded here so it is not lost)

**Archetype composition.** `blueprints/archetypes/README.md`: *"Composition: unsupported in
v0 — exactly one archetype id per discovery session."* This is the real blocker for mixed
operators, and scope axes do not solve it. Kuehne+Nagel is a forwarder, an NVOCC, a warehouse
operator and a customs broker in one legal entity; Maersk is an ocean carrier that acquired
forwarders. The axes tune one archetype; they cannot merge two. Both carrier guides now
instruct the interviewer to stop and escalate rather than stretch the archetype — that is a
holding position, not a fix. Needs: multiple ids per session, module-set union, `max` tier
resolution, and a story for conflicting `core_concepts` anchors. Requires
`archetype.schema.json` `schema_version: 2`.

**Missing archetypes.** `accelerator-packs/logistics/manifest.yaml` `target_sectors` claims
sectors no archetype covers:

| Gap | Why it matters | Notes |
|---|---|---|
| `road-haulier` | claimed as "Road carrier (trucking)" | no reservation-grain standard exists (`pattern.yaml` road = `pattern-only`), so it is `mmt/inland-transport` + `mmt/documents#RoadConsignmentNote` centred |
| `terminal-operator` | claimed as "Terminal operations" | TIC 4.0 modules already exist and are unused outside `unit-load-carrier`'s optional tier |
| `customs-broker` | claimed as "Customs brokerage" | WCO modules exist; `wco/party#Declarant` is the anchor |
| `shipper` / BCO | `multimodal-order-leg` "Applicability" names a shipper's own TMS as in scope | would be the first `1pl` archetype |
| `3pl-contract-logistics` | warehousing / contract logistics is not covered by `freight-forwarder` | needs warehouse modelling this pack does not have beyond `mmt/locations#Warehouse` |

Each needs its own SME review before being added — per `blueprints/archetypes/README.md`,
adding an archetype is a modelling decision, not a naming one.

**Freight-forwarder guide coverage.** The guide was canonicalised structurally (§0 blocks,
§-numbering, outcome guidance on every section) but still has 9 business areas against
`shipping-carrier`'s 21 and `unit-load-carrier`'s 19. Missing and worth adding: dangerous
goods, sustainability / CO₂ reporting (a top-3 forwarder RFP topic today), financial
settlement and cost recharge, trade facilitation (AEO / Single Window), warehouse and
cross-dock interface. Deliberately split out to keep the switchboard change reviewable.

**Naming.** Archetype ids stay operating-model names (`freight-forwarder`,
`shipping-carrier`, `unit-load-carrier`); industry vocabulary (3PL, 4PL, NVOCC, control
tower, ferry operator) enters through the alias table in `discovery/README.md` and the
multi-valued `service-model` axis. Reconsider only if a rename is forced for another reason —
it costs ~98 references across 32 files plus the `--archetype <id>` CLI surface and
`tests/test_toolkit_contract.py`.

**Version skew, for whoever picks this up.** The `.venv` here has toolkit 4.5.0rc4, while
`.github/skills/kairos-design-discovery/SKILL.md` is marked `managed v5.1.0rc2`. Confirm
which version is authoritative before implementing against `archetype_loader`; 4.5.0rc4 has
no `pattern_loader.py` at all, though `tests/test_toolkit_contract.py` expects one in the
source checkout.
