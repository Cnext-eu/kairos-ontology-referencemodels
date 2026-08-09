# CR — Harvest hub-implementation learnings into the reference models

**Type:** Change request (reference models) · **Status:** proposed · **Raised from:** `cldn2-ontology-hub`
**Date:** 2026-08-09 · **Target repo:** `Cnext-eu/kairos-ontology-referencemodels`
**Affected:** `blueprints/` (new content), `accelerator-packs/logistics/` (corrections), pack manifests

Companion documents: [`docs/cr-fast-path-to-silver.md`](cr-fast-path-to-silver.md) (toolkit-side
authoring workflow — CR §5 below is the reference-model half of the same lever).

---

## 1. Problem statement

### 1.1 The blueprint layer is blocked on decisions it cannot make

The Logistics Accelerator v1.6.0 shipped a well-designed blueprint layer — canonical class
registry, overlap register, capability coverage, relationship registry, decision log,
convergence dossier, JSON schemas, deterministic evidence generation. The analysis is sound.

But the layer is entirely inert:

| Artifact | State |
|---|---|
| `canonical-class-registry.yaml` | 17 concepts, **all** `disposition: unresolved`, `maturity: experimental`, `first_slice: false` |
| `relationship-registry.yaml` | `relationships: []` |
| `capability-coverage.yaml` | 8 capabilities, **all** `status: deferred` |
| `decision-log.md` | 10 of 11 checkpoints at *Investigate* |
| `profiles/silver-starter/` | Reserved placeholder, gated |
| `contracts/generated/` | Reserved placeholder, gated |

The release gate reads: *blocked until stakeholder review records approve, defer, or reject
each remaining candidate*. That gate has no owner and no scheduled forcing function, so the
layer cannot progress on its own.

### 1.2 The evidence model only accepts synthetic probes

The only evidence the registries consume is `evidence/source-shapes/` — two synthetic shapes
(freight-forwarder, carrier-terminal) explicitly described as "evidence probes, not consumer
schemas". Nothing in the schema allows a **shipped client hub** to count as evidence, even
though a hub that has compiled a domain to Silver against real sources is a materially
stronger signal than a synthetic probe.

### 1.3 The declared gaps are mis-classified

`convergence-analysis.md` lists eight "explicit reference-model gaps" and the release gate
blocks on all of them. Classified properly:

| # | Declared gap | Actually a… |
|---|---|---|
| 1 | Neutral durable Party + qualified Party Role Assignment | pattern |
| 2 | Qualified Location Role Assignment | **same pattern as #1** |
| 3 | Booking amendment / version history | pattern (identity/version/state) |
| 4 | General equipment allocation outside the container model | **class gap** |
| 5 | Ordered stop + plan-to-execution realization | pattern |
| 6 | Event envelope with subject roles and correction/supersession | part pattern (#3), part class gap |
| 7 | Cross-domain structured Identifier Assignment | pattern (variant of #1) |
| 8 | Temporal Status Observation + governed code-list | two patterns |

**Seven of eight are pattern gaps, not class gaps**, and #1/#2/#7 are three instances of one
pattern. A pattern states a shape and its applicability; it does not require settling which
class is authoritative. Patterns can therefore ship independently of every open canonical
dispute.

### 1.4 Consequence

Each client hub re-derives the same modelling craft by hand — role flattening, deferred
cross-domain links, denormalised attribute copies, timestamp naming, code-list conformance,
provenance and survivorship — with no shared vocabulary, no shared shapes, and no route for
what it learned to return to the reference models.

---

## 2. Proposal overview

Split the work along the axis the repo already uses:

| Axis | Content | Destination |
|---|---|---|
| **Horizontal** — modelling craft, sector-neutral | Pattern library, evidence governance, anchor invariant, anti-pattern register, shape derivation profile | `blueprints/` — already defined as *"opinionated Kairos guidance layered on top of the ref models"*, versioned independently, consumed by `kairos-design-discovery` |
| **Vertical** — sector semantics | New archetype, class gaps, registry corrections | `accelerator-packs/logistics/` |

Horizontal changes benefit the Financial Services pack immediately and at zero marginal cost.

Changes are numbered CR-RM-01 … CR-RM-08 below.

---

## 3. CR-RM-01 — Pattern library (`blueprints/patterns/`)

### 3.1 Rationale

Seven of the eight declared reference-model gaps are pattern gaps (§1.3). Shipping them as
patterns unblocks the release gate without resolving a single canonical-class dispute.

Patterns must be **implementable**, not merely documented. Prose-only guidance produces
divergent client implementations — the observed failure mode is a single hub carrying four
different naming conventions for the same requested/planned/actual timestamp triple across
four classes, because nothing normative existed to copy.

### 3.2 Proposed structure

Mirrors the existing `archetypes/` convention:

```
blueprints/patterns/
  _schema/pattern.schema.json
  VERSION
  README.md
  <pattern-id>/
    pattern.yaml         # structure: id, problem, applicability, participants,
                         # naming convention, cardinality rules, known anti-patterns
    pattern.md           # prose: when to use, when NOT to, worked example
    template.ttl         # copyable OWL fragment, placeholder namespaces
    template.shacl.ttl   # the shapes that enforce it
```

**Convention deviation to record explicitly in the README:** the v0.2 archetype contract puts
structure in `blueprints/` and prose in `accelerator-packs/<pack>/`. Patterns keep both in
`blueprints/` because pattern prose is craft guidance, not sector interview material — there
is no pack it belongs to. State the reason so it does not read as an oversight.

### 3.3 Candidate patterns

| Pattern id | Problem it solves | Closes gap |
|---|---|---|
| `deferred-relationship` | Declare the ObjectProperty now; carry the scalar FK as a DatatypeProperty; resolve the object link after key conformance. Naming: `<relationship>` ↔ `<target>Reference`. Lets a domain slice land before cross-domain keys conform. | — (new) |
| `qualified-role-assignment` | Durable identity + `(identity, role, context, validity)` link entity — plus explicit guidance on when flattened boolean role flags are an acceptable physical simplification. | 1, 2, 7 |
| `attribute-snapshot` | Denormalised copy of another entity's attributes onto a transaction, with declared source, as-of semantics, and explicit "this is not the master" status. | — (new) |
| `temporal-quartet` | One naming convention for requested / planned / estimated / actual × start\|arrival / end\|departure, with subproperty hooks into the derived ontologies. | 8 (partly) |
| `governed-code-list` | Classification dimension as an entity with cross-source survivorship, distinct from the raw source-typed string carried on the instance. | 8 |
| `plan-execution-realisation` | Plan aggregate + execution aggregate + realisation link, with the rule that actuals, cost and emissions attach to execution. | 5 |
| `identity-version-state` | Separate document / contract / rate identity from its versions and its states. | 3, 6 (partly) |
| `multi-source-conformance` | Provenance property, survivorship priority, per-attribute system-of-record declaration for a conformed entity. | — (new) |
| `derived-child-entity` | An entity with no source table, derived by an ordered window over a sibling relation, with determinism rules for its key. | 5 (partly) |
| `dual-instantiation` | One source record legitimately instantiating two classes at different semantic grains, sharing a key — explicitly not a duplicate. | — (new) |

### 3.4 Related change

Extend `blueprints/archetypes/_schema` with a `patterns:` selection list alongside the
existing `ref_model_modules:` tiering, so an archetype declares which patterns its sector
requires and `kairos-design-discovery` can surface them during the interview.

### 3.5 Open decision

Are patterns **normative** (a hub is non-conformant if it invents a variant) or **advisory**?

Recommendation: ship advisory, with a stated intent to make the *naming conventions*
normative at the next major version. The naming drift is where the cost concentrates, and
normative-from-day-one on an unproven library tends to be ignored rather than followed.

### 3.6 Acceptance criteria

- `pattern.schema.json` published and validated in CI alongside the archetype schema.
- At least `deferred-relationship`, `qualified-role-assignment`, `temporal-quartet` and
  `governed-code-list` shipped with all four files each.
- Each pattern's `template.ttl` parses; each `template.shacl.ttl` validates against it.
- `convergence-analysis.md` gap list updated to reference pattern ids and to distinguish
  pattern gaps from class gaps.

---

## 4. CR-RM-02 — Implementation attestations and a promotion rule

### 4.1 Rationale

§1.1 and §1.2: the registries are blocked on a stakeholder review with no owner, and cannot
consume the strongest available evidence — hubs that have actually compiled a domain against
real sources.

### 4.2 Proposed change

Add a source-neutral **implementation attestation**, structured so it is publishable without
client-detail review:

```
blueprints/evidence/attestations/_schema/attestation.schema.json
blueprints/evidence/attestations/<opaque-id>.yaml
```

```yaml
schema_version: 1
archetype: <archetype-id>
accelerator: <pack-id>
attested_at: <date>
concepts:
  - concept_id: <registry concept id>
    chosen_parent: <class IRI actually used>
    declined_parent: <class IRI the registry recommends, if different>
    decline_reason: <short, structural>
    grain: <one sentence>
    cardinalities_observed: [ ... ]
patterns_used: [ <pattern-id>, ... ]
grain_collisions_encountered: [ <collision-id>, ... ]
```

No client names, no source-system names, no column names — the schema forbids free text
outside the enumerated fields.

Then publish a **promotion rule** in the blueprint README, for example:

- *N* independent attestations agreeing, spanning ≥ 2 archetypes, moves a concept from
  `unresolved` to `evidenced`.
- A `declined_parent` recurring across attestations **forces** re-review of that anchor.
- Attestations never by themselves authorise a new class; they authorise a disposition change
  on an existing candidate.

### 4.3 Acceptance criteria

- Schema published; `canonical-class-registry.schema.json` extended with an
  `implementations:` field referencing attestation ids.
- Promotion rule documented in `blueprints/README.md` and in each pack's
  `blueprint/README.md`.
- At least one attestation committed, so the mechanism is exercised end to end.

---

## 5. CR-RM-03 — Anchor-selection invariant, enforced by a validator

### 5.1 Rationale

A canonical anchor pinned to a class narrower than the pack's own declared target sectors is
a mechanical inconsistency, not a judgement call — and it is silently fatal, because a hub in
an unserved sub-sector must either mis-model or abandon the anchor.

Concrete instance in the current pack: `equipment-asset` is anchored on
`dcsa/equipment#Container` with identity "ISO 6346 container number", while `manifest.yaml`
declares road carriers, 3PL, terminal operations and NVOCC among `target_sectors`. Non-
containerised unit-load operations cannot use that anchor.

### 5.2 Proposed rule

> A canonical anchor must be the most general class that covers **every** archetype in the
> pack's declared `target_sectors`. Narrower classes are recorded in the overlap register as
> scope-specific overlays, never as the anchor.

### 5.3 Proposed enforcement

Extend `scripts/validate_archetypes.py` (or add a sibling `validate_anchors.py`) to
cross-check, for every concept in a pack's canonical registry and every archetype the pack
claims, that the anchor class is applicable. Fail CI on violation.

This check is pack-agnostic and should be expected to surface findings in Financial Services
too — anchoring *Account* or *Party* on a retail-banking-specific class while claiming
insurance and trade finance as targets is the same defect.

### 5.4 Acceptance criteria

- Rule stated in `blueprints/README.md` and both pack `blueprint/README.md` files.
- Validator implemented and wired into CI.
- Existing violations either corrected (see CR-RM-06) or explicitly waived with recorded
  rationale.

---

## 6. CR-RM-04 — Anti-pattern and grain-collision register

### 6.1 Rationale

The logistics `decision-log.md` "Rejected shortcuts" table is high-value content trapped as
prose inside one pack's markdown. It is not machine-readable, not pack-neutral, and not
reachable by discovery scripts or reviewers.

### 6.2 Proposed change

Promote it to `blueprints/anti-patterns/`, machine-readable and keyed by concept id, so the
toolkit, the discovery skill and human reviewers consume one source.

Add one generalisation that is currently absent and recurs across sectors:

> **Source-noun ≠ canonical grain.** A source relation's name is evidence of nothing.

Record known collisions per concept — for example, that a source relation named *shipment*
may carry the carrier transaction, the physical trip, or the goods batch, three grains that
must be disambiguated before mapping — and make grain disambiguation a required discovery
question rather than an optional one.

### 6.3 Acceptance criteria

- `anti-patterns/_schema/` published; logistics "Rejected shortcuts" migrated without loss.
- Grain-collision entries added for the concepts where collisions are known.
- Discovery scripts reference collision ids at the relevant questions.

---

## 7. CR-RM-05 — Ship SHACL by derivation rule

### 7.1 Rationale

No accelerator pack ships shapes today, so every client hub hand-authors them. Observed cost
in one hub: 9 files, ~937 lines — all of which follow a rule that is entirely mechanical.

### 7.2 Proposed derivation profile

Publish in `blueprints/` as a shape derivation profile:

| Source fact | Derived constraint |
|---|---|
| Column not-null | `sh:minCount 1 ; sh:maxCount 1` |
| Column nullable | `sh:maxCount 1` only |
| Column unique at grain | identity constraint on the grain shape |
| Enumerated source domain | `sh:in ( … )` |
| Deferred object link (`deferred-relationship`) | object property optional; the materialised reference carries the required constraint |
| Every constraint | `sh:description` citing the source column that justifies it |

### 7.3 Proposed packaging

Each pack ships generated `current/shapes/` at `sh:severity sh:Info`, for clients to activate
and tighten. Shapes are derivative artifacts and must never become a second design authority
— same rule the pack already applies to generated contracts.

### 7.4 Relationship to the toolkit CR

Shapes are artifact #2 of the 7 hand-authored artifacts counted in
[`cr-fast-path-to-silver.md`](cr-fast-path-to-silver.md) §1.1, and the most derivable of the
seven. This CR supplies the rule; the toolkit CR supplies the generator.

### 7.5 Acceptance criteria

- Derivation profile documented with the full rule table.
- Generated shapes shipped for at least the pack's `first_slice` concepts.
- Regeneration is deterministic and checked in CI (same pattern as
  `generate_logistics_inventory.py --check`).

---

## 8. CR-RM-06 — Pack profile tiers

### 8.1 Rationale

`client-hub-blueprint/BLUEPRINT.md` instructs clients **not** to import the full accelerator,
but the pack offers no middle ground between a single module and all eight ontologies. In
practice a hub commonly exercises three of the eight, while carrying the import closure of
all eight.

### 8.2 Proposed change

Reuse the tier vocabulary that archetypes already use (`required` / `recommended` /
`optional`) rather than inventing a second one. Declare named profiles in each pack's
`manifest.yaml` and emit one `.ttl` per profile:

| Profile | Logistics composition |
|---|---|
| `core` | MMT + BSP + DCSA + supply-chain |
| `+maritime` | core + IMO |
| `+terminal` | core + TIC |
| `+customs` | core + WCO |
| `+esg` | core + Sustainability |

Financial Services gets equivalent treatment (retail / capital-markets / insurance).

### 8.3 Acceptance criteria

- `manifest.yaml` schema extended with `profiles:`.
- Per-profile `.ttl` files generated and registered in `catalog-v001.xml`.
- `BLUEPRINT.md` import guidance updated to name profiles as the recommended default.

---

## 9. CR-RM-07 — Vertical corrections and additions (logistics pack)

The genuinely sector-specific items. Short list by design.

### 9.1 New archetype — unit-load / ro-ro short-sea carrier

`blueprints/archetypes/unit-load-carrier.yaml` + `accelerator-packs/logistics/discovery/unit-load-carrier.md`.

Sector definition: non-containerised unit loads (trailers, swap bodies, cassettes),
accompanied and unaccompanied traffic, own-account plus subcontracted road haulage, capacity
measured in lane metres rather than TEU.

Its value is that it stresses the model exactly where the two existing archetypes do not —
the equipment anchor, own-vs-subcontracted classification, and empty repositioning all only
surface here. It is also the archetype that makes CR-RM-03's validator produce a finding.

### 9.2 Correct the `equipment-asset` anchor

Anchor on the general multimodal transport-equipment class; record the container-specific
class in the overlap register as a scope overlay. Note in the registry that a single source
allocation relation commonly mixes equipment, driver, operator and subcontractor rows, so the
allocation grain requires a resource-type discriminator rather than a clean 1:1 to the asset.
This closes declared gap #4 without a new class.

### 9.3 Record the three-grain shipment split

`convergence-analysis.md` debates carrier-transaction vs goods-collection as a two-way split.
Field evidence shows a third grain — the **physical trip**, which owns distance, toll,
emissions and predecessor/successor chaining. Add it to the `shipment-grains` overlap entry
and to the grain-collision register (CR-RM-04).

Also revisit `canonical-erd.mmd`: the `Shipment -. books .-> Consignment` edge implies a
direct dependency that field evidence does not support — both commonly hang off the order.

### 9.4 Two class gaps to add to capability coverage

- **Empty equipment availability and repositioning.** Universal for carriers and lessors;
  currently has no parent class anywhere in the pack.
- **Trade lane / market segment.** Lane profitability is a first-order carrier capability
  with no class in the commercial ontology.

### 9.5 Movement-grain emissions attachment point

The supply-chain bridge attaches emissions at consignment and transport-service grain only.
Operational emissions data lands at movement/trip grain. Add the attachment point.

### 9.6 Populate the relationship registry

`relationships: []` is the direct blocker on the release gate's *relationship cardinality and
temporal semantics* item. Seed it from attested cardinalities (CR-RM-02) rather than waiting
for a stakeholder session.

### 9.7 Housekeeping

`discovery/README.md`'s "Available today" table lists only `shipping-carrier`, but
`freight-forwarder.md` ships. Same staleness in the pack `README.md`.

---

## 10. CR-RM-08 — Close the feedback loop

### 10.1 Rationale

Everything above is a one-time harvest because no step in the pack lifecycle sends learnings
back. Without a defined step, the next engagement repeats the same re-derivation.

### 10.2 Proposed change

Add a **harvest step** to the accelerator-pack lifecycle, executed at the end of each
engagement, producing exactly three artifacts:

1. an implementation attestation (CR-RM-02),
2. pattern candidates (CR-RM-01),
3. grain collisions encountered (CR-RM-04).

All three are source-neutral **by schema**, so the harvest is publishable without a review
pass for client detail — which is the property that makes the loop actually run.

### 10.3 Acceptance criteria

- Harvest step documented in `accelerator-packs/README.md`.
- A template or toolkit command exists to produce the three artifacts.
- The blueprint promotion rule (CR-RM-02) names the harvest as its input.

---

## 11. Sequencing

| Order | Changes | Why first |
|---|---|---|
| 1 | CR-RM-01 (patterns), CR-RM-05 (shape derivation) | Pure addition. No disputes to settle, immediate reuse in both packs, unblocks 7 of 8 declared gaps. |
| 2 | CR-RM-02 (attestations), CR-RM-03 (anchor invariant) | The governance that makes disposition promotion possible and mechanically checked. |
| 3 | CR-RM-07 (vertical corrections + archetype), CR-RM-04 (anti-patterns) | Depends on the anchor rule and the pattern ids existing. |
| 4 | CR-RM-06 (profile tiers), CR-RM-08 (harvest loop) | Packaging and process; safe to land last. |

## 12. Risks and caveats

- **Single-implementation evidence.** Attestation-driven promotion is only sound with a
  stated threshold (CR-RM-02 §4.2). A lone attestation should close a checkpoint *only where
  it agrees with the disposition the blueprint already recommends*; where it diverges, it
  triggers investigation, not promotion.
- **Pattern library bloat.** Ten patterns is a plausible starting set, not a target. A
  pattern earns its place by appearing in ≥ 2 attestations or by closing a declared gap;
  everything else waits.
- **Normativity.** See CR-RM-01 §3.5 — shipping normative patterns before they are proven
  invites silent non-conformance, which is worse than advisory guidance that is followed.
- **Validator false positives.** CR-RM-03's applicability check needs a waiver mechanism with
  recorded rationale, or it will be disabled the first time a legitimate scope restriction
  trips it.
