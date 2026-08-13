# Changelog

All notable changes to the Kairos Reference Models will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### temporal-quartet — the synonym ban becomes a closed, structured list (#40)

#### Added
- **`banned_name_tokens: [eta, etd, ata, atd, expected, due]`**, `applies_to_ranges:
  [xsd:dateTime, xsd:date, xsd:time]` and a cited `exemptions` list on the
  `synonym-for-estimated-or-requested` anti-pattern (closes #40). The normative ban previously
  lived only as prose examples ("eta, expected, due") that disagreed with the anti-pattern's own
  literals ("eta, expectedTime, due_date") — an implementation had to choose between
  under-enforcing and inventing policy. The token list is now closed; matching semantics
  (scope by range, exemptions first, whole-token camel/snake matching with acronym runs) are a
  normative subsection of `pattern.md`. Exemptions each carry a reason citing the source term of
  art (`dueDate`, `dischargeDueDate`, `reviewDueDate`), so every place the ban yields is a
  visible, audited line item.
- **`blueprints/patterns/_schema/pattern.schema.json`** — the schema owed since v0.1; both
  triggers for writing it fired long ago (a consumer exists; more than one person authors).
  Open at the top level (custom top-level keys are the library's documented design; the
  toolkit's loader preserves them in `extra`), strict `additionalProperties: false` inside every
  list-entry shape — the v1.13.0 defect was a wrong-but-parseable key inside a block sequence.
  `scripts/validate_structure.py` now validates every `pattern.yaml` against it, and guards
  every pattern `template.ttl` (no `rdfs:range owl:Thing`; every property declares
  `rdfs:domain`). The `patterns` surface in `contract-manifest.yaml` now declares the schema,
  which auto-activates `test_contract_manifest`'s schema validation over every pattern file.
  This closes the 1.14.0 "Known gaps" item.
### deferred-relationship — one derivation, one range policy (#39, #42)

`blueprints/patterns/` bumped to **0.3.0**: two normative rules in this pattern changed meaning.

#### Changed
- **Interim-scalar naming MUST now derives from the target class** (closes #39). The published
  rule said "derivable from the eventual object property name by appending 'Reference'", which
  contradicted its own example (`hasEquipmentAllocation` + `Reference` ≠
  `equipmentAllocationReference`) and named a different source than the `<target>Reference`
  convention beside it. The rule now states the full transform: target class local name,
  first character downcased, `Reference` appended. The worked example's target class is renamed
  `EquipmentAsset` → `EquipmentAllocation` so example, convention and rule finally agree.
- **The pattern now prescribes one range policy: a marked stub class** (closes #42). `pattern.md`
  declared the range while `template.ttl` said to omit both domain and range — two mutually
  exclusive instructions for the same decision. Resolution: the domain is *never* deferred (it is
  the class being authored — the template's deferred-domain instruction was simply wrong); the
  range is declared against a stub class in the hub's namespace whose `rdfs:comment` starts with
  the literal marker `STUB (deferred-relationship):`, making unmigrated stubs mechanically
  findable. New pattern.md section "Domain and range while the target is unresolved" states the
  policy, the stub's migration duty, and an explicit ban: **`rdfs:range owl:Thing` is never an
  acceptable substitute** — it passes `validate` and then hard-fails `compile`
  (`safety.relationship-endpoint`, non-suppressible) the moment a binding is authored.
  `template.ttl` now declares domain and range on both properties and carries the marked stub.
- Toolkit note: v5.2.1rc7's `validate` warning text and DD-133 §7 describe the *omitted*-range
  shape as pattern-prescribed; a toolkit issue updating that wording is filed with this change.
  Omission remains tolerated by the toolkit, so nothing breaks in the interim.

### qualified-role-assignment — heterogeneous identity types documented (#43)

#### Added
- A "Heterogeneous identity types (context, not a requirement)" section in
  `qualified-role-assignment/pattern.md` (closes #43). A reproducibility test — two blind,
  independent authoring runs from identical evidence — resolved the same two-identity-type case
  two different, reasonable ways because the pattern was silent on it. The section names both
  legitimate shapes (one assignment class per concrete identity type, or one class ranging over
  a shared supertype), warns against minting an abstract supertype nothing else needs, and makes
  explicit that the `physical_simplification` escape hatch is evaluated **per identity type**,
  not once per pattern application. Deliberately prose-only context with no enforcement surface
  and no `pattern.yaml` change — the structural choice stays a judgment call.

### data-domains — drop the unread `folder:` key (#38)

#### Removed
- The `folder: "model/ontologies/<id>/"` key from all 22 domains in each of the logistics and
  financial-services `client-hub-blueprint/data-domains.yaml` files, and its declaration from
  `accelerator-packs/_schema/data-domains.schema.json`. The key stated a directory-per-domain
  layout nothing implements: the toolkit derives the flat `model/ontologies/<id>.ttl` path from
  `id` and never reads `folder`, so the key was a second place for the path convention to drift
  (closes #38).
Two changes, both from the same QA pass and shipping together. **Part 2** names the contract and
retires the last hand-maintained restatement of it; **Part 1** below made the derived surfaces
generated or tested.

### Part 2 — name the contract, retire BLUEPRINT.md

#### Added
- **`ontology-reference-models/CONTRACT.md`** — what this repository publishes, what consumers may
  rely on, and how it changes. Kept deliberately thin: rules and policy only, no restatement of
  schemas or key lists, because a prose copy of a machine file is what rots.
- **`ontology-reference-models/contract-manifest.yaml`** — the machine-readable half: each of the
  six published surfaces with its schema, its consuming loader, and the check that guards it.
  Enforced by **`tests/test_contract_manifest.py`**, which asserts that every glob still matches
  files, every declared schema validates every match, every `enforced_by` target still exists,
  and every `schema: null` row justifies itself.
- **`accelerator-packs/_schema/data-domains.schema.json`** — the first schema for
  `data-domains.yaml`, which the toolkit has read for four minor versions with nothing checking
  its shape. `additionalProperties: false` throughout, so a typo'd key now fails here instead of
  being silently dropped by the loader.
- **Adoption order** in `accelerator-packs/logistics/discovery/README.md` — the five-phase
  sequencing rehomed from `BLUEPRINT.md`, beside the scope axes that decide *which* domains a
  client needs.

#### Removed
- **`client-hub-blueprint/BLUEPRINT.md` from both packs** (338 and 255 lines). Measured before
  deleting: ~119 lines copied the toolkit's own `scaffold/ontology-hub/` tree, ~86 restated
  `data-domains.yaml` — and had **already drifted four bridge properties** behind it
  (`hasBookingParty`, `hasEvent`, `hasTransportDocument`, `hasTransportEquipment`), a seventh
  stale surface the QA pass never counted — and ~22 were superseded by the toolkit's `mdm/`
  package and `kairos-design-mdm`. Rewriting it for v5 would have recreated both drift sources
  in fresh paint.

  Its three genuinely unique facts were rehomed to files that already have readers: the
  import-the-module-not-the-pack rule and the extend-vs-import table to `CONTRACT.md`; the
  phased adoption order to `discovery/README.md`; the working-capital-metrics boundary into the
  `financial` domain's `does_not_own`. Hub folder structure is now deferred to
  `kairos-ontology new-repo`, which generates and owns it.

  This also achieves the contract/prose separation that motivated the proposed
  `client-hub-blueprint/` rename — by moving the prose out rather than the contract file, so no
  cross-repo coordination is needed. **The rename is therefore not planned**: the folder now
  holds only `data-domains.yaml`, and the path is hardcoded in 32 places across 10 toolkit files.

#### Changed
- **`.docs/ReferenceMaterial/mdm.md`** carries a prominent pre-v5 banner mapping each retired
  surface it describes to its v5 replacement, and pointing at `kairos-design-mdm`. Content kept:
  the phased-coexistence reasoning is still sound, only the mechanics are obsolete. `.docs/` is
  not shipped in the release tarball.
- `discovery/README.md` now states that archetype checks 6 and 7 **fail the build** — they were
  promoted from advisory in the preceding entry, and that text still described them as guards.

#### Fixed
- The working-capital-metrics boundary is stated in `does_not_own`, which the source-system
  classifier actually reads. `load_data_domains` builds a fixed dict — only `name`, `owns`,
  `does_not_own`, `group`, `uris`, `modules` and `imports` reach `build_data_domain_targets`.
  Custom keys such as `grain_note`, `mode_note` and `extension_note` are co-located commentary
  for editors only, and the schema now says so.

### Part 1 — make derived surfaces generated or tested

A QA pass after [1.15.0](#1150---2026-08-10) found every automated gate green while six
documentation surfaces had silently gone stale. Each miss was in a file with **no machine
reader**. This release makes the derived surfaces generated or tested, closes the RAIL/IATA
registration gap, and removes a hub scaffold that never belonged in this repository.

#### Added
- **`tests/test_model_registration.py`** — fan-out tests treating `manifest.yaml` as the single
  hand-edited registry: every advertised module must be imported by the accelerator, resolvable
  through the catalog, absent from `owl:imports` when reference-only, and reachable from
  `data-domains.yaml`. A module may opt out only via an explicit `data_domain_status` on the
  manifest entry, so a known gap is a tracked gap. A model added to the bundle and wired nowhere
  now fails three tests at once.
- **`scripts/generate_pack_docs.py`** — renders pack README module tables, version lines, and the
  `.intro` version/sheet tables from `manifest.yaml` plus per-module `VERSION` files into
  marker-delimited blocks, leaving hand-written narrative untouched. `--check` runs in CI, the
  same contract as `generate_logistics_inventory.py --check`.
- **`scripts/check_toolkit_pin.py`** — compares the pinned toolkit wheel against the newest
  release on the configured `[tool.kairos].channel`. A wheel URL is exact by construction and
  `channel` is only read by `kairos-ontology update --upgrade`, so nothing ever advanced the pin
  on its own. Degrades to a pass when offline.
- **Cross-repo contract CI job** — installs the pinned toolkit and runs
  `tests/test_toolkit_contract.py`, asserting tests were actually collected so a silent skip
  fails the build. Structural validation stays toolkit-free in its own job.
- **Model sheets for RAIL and IATA** (`.intro/industry-models/`) — the two newest models were the
  only ones with no business-facing briefing. RAIL carries the reservation-vs-movement grain
  split; IATA carries the authoritative-mirror tier and reference-only import policy.

#### Changed
- **Mode-binding and scope-profile drift now fail the build** (`validate_archetypes.py` checks 6
  and 7, previously advisory). The v1.13-1.15 defect — `pattern.yaml` saying `extension-point`
  for air and rail for two releases — would have printed a warning into a green run.
- **`mode_bindings[].target` → `target_iris` + `target_note`.** The old field held an IRI for
  ocean but prose for air and rail, and the collector skipped anything not starting with `http`,
  so the prose was never validated. Every `target_iris` entry is now asserted to be a declared
  `owl:Class`.
- **RAIL and IATA wired into `data-domains.yaml`** by grain: `rail/path-request` and
  `rail/consignment` plus IATA ONE Record cargo at the reservation grain (`booking`);
  `rail/train-running` and `rail/rolling-stock` at movement grain (`intermodal`); `rail/party`
  beside `imo/party`. IATA is marked `reference-only` — the pack never imports it, a hub binds to
  it hub-local. The toolkit now resolves 56 module profiles for logistics, up from 50.
- **Toolkit pin `5.1.0rc2` → `5.2.0rc6`**, `uv.lock` regenerated. Three versions had been live at
  once: installed `4.5.0rc4`, pinned `5.1.0rc2`, published `5.2.0rc6`. The cross-repo contract
  tests could not run before this, because `pattern_loader` does not exist in `5.1.0rc2`.
- **`.github/copilot-instructions.md` rewritten for this repository.** It described a v5 *hub*
  — `kairos.yaml`, `compile <domain>`, EntityBinding — none of which exists here.

#### Fixed
- **`scripts/catalog_utils.py` now implements `rewriteURI`.** Only exact `<uri>` entries were
  honoured, so the single rule covering 300+ FIBO files was invisible: every FIBO import resolved
  to `None` while `test_catalog.py` still reported "all mappings valid". Includes the FIBO
  trailing-slash convention (`…/Contracts/` → `Contracts.rdf`).
- Stale generated facts: the logistics pack README claimed "8 ontologies" and version `1.6.0`
  against 11 imports at `1.10.0`; the two `.intro` version tables were up to four releases behind.
- `pattern.md` listed `TransportMovement` as an air reservation-grain target; it is movement grain.

#### Removed
- **27 toolkit-managed agent files** — 22 hub-authoring `kairos-*` skills, 3 `SC-*` skills, and a
  stray `.docs/wip/SKILL.md`. The toolkit's hub scaffold had been applied to a repository that is
  not a hub, which is why `kairos-design-silver` appeared stale: it was current, and simply did
  not belong here. The two repo-authored skills are kept and renamed off the toolkit's `kairos-`
  namespace to `refmodels-ontology-audit` and `refmodels-ontology-versioning`.

#### Known gaps (recorded, not silent)
- financial-services `data-domains.yaml` names three FIBO ontologies absent from the vendored
  release, and its `manifest.yaml` advertises nine FIBO module groups the accelerator never
  imports. Both are pre-existing, need FIBO judgement, and are listed in `KNOWN_GAPS` in
  `tests/test_model_registration.py`. Any *new* gap, in any pack, fails.

## [1.15.0] - 2026-08-10

Closes the transport-mode specialisation gap opened in [1.14.0](#1140---2026-08-10):
the `multimodal-order-leg` pattern named IATA ONE Record (air) and TAF TSI (rail) as
reservation-grain extension points — this release authors both, vendors the IATA
ontology, and re-mediates the FIBO license. Project cargo is documented as **not a
mode**; nothing is authored for it. The release also lands the logistics discovery
scope switchboard and repairs the broken archetype/fixed-evidence surface.

### Added
- **Scope switchboard in the logistics SME discovery guides** — each guide now opens with a
  `§0 Scope profile` answered before the business-area sections. Three axes (`modes-served`,
  `geographic-scope`, `service-model`) turn an SME's answers into a tuned module set, so a
  two-mode port-to-port agent and a five-mode door-to-door 4PL no longer resolve to the same
  ontology. The axes and their **resolution rules** are defined once in
  `accelerator-packs/logistics/discovery/README.md`; each guide carries only its own
  consequence tables, because the same answer implies different modules for a forwarder than
  for a carrier. Mode targets are cited from `multimodal-order-leg` `pattern.yaml`
  `mode_bindings` rather than restated.
- **Resolution rule 1** — an axis may only *promote* the tier of a module the archetype
  already declares, never invent one. `ref_model_modules` is the complete menu of what an
  operating model can require; the axis chooses from it. This is what makes the prose
  checkable, since `ref_model_modules` is exactly what the toolkit's `archetype_loader` reads.
  Scope answers land on the existing `outcome-codes.yaml` enum as a pre-seeded
  `not-applicable` + `needs_confirmation: true`, so no new outcome code and no cross-repo
  contract change was needed.
- **"Picking a starting archetype" alias table** in `discovery/README.md` — maps market
  vocabulary (3PL, 4PL, LSP, control tower, NVOCC, shipping line, ferry/ro-ro operator, road
  haulier, BCO) onto archetype ids, which name an *operating model* rather than a commercial
  position. Records why xPL is not used as an archetype id: it has no ISO/CEN/UN-CEFACT/WCO
  definition (4PL is a 1996 Accenture coinage), none of the party-role code lists the derived
  ontologies are grounded in contains an xPL code, and most real operators occupy several
  rungs at once — so `service-model` is recorded multi-valued and is a routing hint only.
- **`scripts/validate_archetypes.py` check 6** (advisory) — the guard that keeps the prose
  honest. Asserts every module IRI a Scope profile names is declared in that archetype's
  `ref_model_modules` (grain-3 mode targets excepted and matched against `mode_bindings`
  instead), that a paired guide carries a Scope profile at all, that `pattern.md`'s per-mode
  table agrees with `pattern.yaml`'s `mode_bindings` statuses, and that every mode target
  resolves through the catalog.
- **`mode_bindings[].module_iris` and `.leg_module_iris`** in
  `blueprints/patterns/multimodal-order-leg/pattern.yaml` — the module IRIs per mode, split
  by grain (3 = the reservation-grain standard, 2 = where mode is stated). Makes that block
  the single mode→module source the discovery guides cite. IATA carries
  `import_policy: reference-only`.
- **`.docs/wip/discovery-scope-selection-cr.md`** — the cross-repo CR for machine-readable
  scope resolution (`_scope/scope-axes.yaml` + the `archetype_loader` /
  `discovery-conformance load` changes to consume it), specified so registry and reader land
  together the way CR #203 did for outcome codes. Also records the deferred backlog: archetype
  composition, the five missing archetypes, and the forwarder guide's remaining business areas.

### Fixed
- **`freight-forwarder.yaml` could not express transport mode at all.** The archetype declared
  11 modules against 27/28 for the two carrier archetypes and was missing
  `mmt/inland-transport` — the module declaring `RoadLeg`/`RailLeg`/`BargeLeg`/`InlandLeg`,
  which is precisely where `multimodal-order-leg` places mode and which the forwarder guide's
  own §3 links to. A forwarder hub built from this archetype could not state that a leg was a
  road leg. Added at `required` with those four classes, plus `mmt/transport-means`
  (`Aircraft`/`RailVehicle`/`RoadVehicle`/`BargeVessel`) at `recommended` and
  `InlandCarrier`/`HaulageInstructions` for carrier-versus-merchant haulage.
- **Air and rail mode specialisations were invisible to the discovery layer.** `pattern.yaml`
  still reported `status: extension-point` for both while `pattern.md` said *modelled* — the
  78c967c work landed in the models and the prose but not the machine twin, because nothing
  reads it. Both set to `modelled` with their catalogued module IRIs. Same drift in
  `accelerator-packs/logistics/current/blueprint/capability-coverage.yaml`, which still listed
  "Air reservation alignment (IATA ONE Record)" and "Rail reservation alignment (TAF TSI)" as
  open extension points at a stale `accelerator_version: "1.8.0"`.
- **`freight-forwarder.md` violated the structure its own `discovery/README.md` mandates** —
  168 lines using `## 1.` instead of `## §1`, no `§0` interview-flow / outcome-code /
  don't-ask-twice blocks, no link to its archetype YAML, and *Outcome guidance* on only 2 of 9
  sections while `shipping-carrier.md` and `unit-load-carrier.md` both complied fully. Most
  consequentially §1 asked "which modes are supported" and "door-to-door or port-to-port" and
  then dropped the answers: no outcome guidance, and a mode-blind *Maps to*. Rebuilt on the
  `shipping-carrier.md` skeleton with guidance on every section. New business areas (dangerous
  goods, sustainability, settlement, trade facilitation, warehousing) are deliberately
  deferred — see the CR.
- **`blueprint/evidence/class-inventory.yaml` was missing the entire RAIL module set**, and
  `tests/test_logistics_blueprint.py::test_real_repository_inventory_is_deterministic_without_artifacts`
  was **already failing on `main`** as a result. Commit 78c967c added `owl:imports <ont/rail>`
  to `logistics-accelerator.ttl` but never regenerated the derived inventory evidence, so the
  committed artifact carried 67 modules against the accelerator's actual 74 and zero
  `ont/rail` records. Regenerated with `scripts/generate_logistics_inventory.py`; the
  hardcoded module count in the test is updated to 74 with a note on why it moved. The four
  blueprint registries are re-stamped to the pack version, which the version-agreement
  invariant requires transitively via the generated inventory.
- **`shipping-carrier.yaml`** gained `mmt/inland-transport` at `optional` (with `InlandLeg`,
  `RoadLeg`, `RailLeg`, `BargeLeg`) so the carrier-haulage promotion in its Scope profile has a
  declared module to promote, satisfying resolution rule 1. `blueprint/transport-order` stays
  deliberately absent: a carrier's incoming demand *is* the booking, and the guide now routes a
  carrier that genuinely sells arranged transport to the composition backlog instead of
  stretching the archetype.
- **`authoritative-ontologies/FIBO/current/LICENSE`** — upstream MIT license text
  (Copyright (c) 2020 Enterprise Data Management Council). The 300+ vendored FIBO files
  were bundled without the license text, which MIT requires to travel with any copy or
  substantial portion. IATA already shipped its `LICENSE`; FIBO did not.
- **`authoritative-ontologies/FIBO/README.md`** — mirror README matching the IATA
  template: tier, contents, version, catalog `rewriteURI` binding, license.
- **FIBO entry in `NOTICE`** third-party section, plus an explicit note that both bundled
  ontologies are MIT, that MIT is Apache-2.0 compatible, and that vendored files are
  aligned to by reference rather than edited.
- **`authoritative-ontologies/IATA/`** — IATA ONE Record air-cargo ontology vendored
  verbatim (v3.3.0 RC1, 2026-08 standard). Ships the Data Model
  (`IATA-1R-DM-Ontology.ttl`, namespace `https://onerecord.iata.org/ns/cargo#`) and
  Code Lists (`IATA-1R-CL-Ontology.ttl`, namespace
  `https://onerecord.iata.org/ns/code-lists#`), plus `LICENSE` (MIT), `METADATA.txt`
  (provenance), and `README.md`. Registered in `catalog-v001.xml` (three `uri` entries,
  including mapping the DM's `owl:imports` of the code-lists to the local CL file).
  This is the **authoritative mirror** for the air reservation grain — ONE Record is
  published natively as RDF/OWL, so no hand-authored derived ontology is needed. Not
  bulk-imported into the logistics accelerator (mirrors the FIBO exclusion); exposed
  via catalog + `manifest.yaml` `references`.
- **`derived-ontologies/RAIL/`** (v1.0.0) — hand-authored **derived** ontology for rail,
  backed by **TAF TSI** (EU Regulation 1305/2012, Annex D.2 Appendix F — Data
  Catalogue; machine-readable `taf_cat_complete.xsd` from the ERA GitHub). 38 classes
  across six modules: `shared-kernel`, `party`, `path-request`, `consignment`,
  `train-running`, `rolling-stock`. Not railML (infrastructure/timetable grain) —
  TAF TSI is the reservation/running grain that matches the pattern. Every class
  cites its exact TAF TSI element via `dcterms:source` + `rdfs:seeAlso`; the
  `kairos-ontology-audit` discipline found zero invented classes. Registered in
  `catalog-v001.xml` (seven `uri` entries).
- **`multimodal-order-leg` pattern updates** — `pattern.md` per-mode table now records
  Air as *Modelled (authoritative mirror)* and Rail as *Modelled (derived)*; the
  project-cargo-not-a-mode note is strengthened to an authoritative statement.
  `template.ttl` adds `iata-cargo:` and `rail-path:` prefixes plus hub-local
  `AirCarrierReservation` (subClassOf `bp:CarrierReservation`, `iata-cargo:Booking`)
  and `RailCarrierReservation` (subClassOf `bp:CarrierReservation`,
  `rail-path:PathRequestMessage`) example bindings at the reservation grain (grain 3).
  Mode remains never specialised at the order grain.
- **Logistics accelerator pack 1.9.0** — archived 1.8.0; bumped VERSION and
  `logistics-accelerator.ttl` to 1.9.0; added the RAIL import; `manifest.yaml`
  bumped 1.7.0 → 1.9.0, RAIL added to `includes`, IATA added to a new `references`
  section (catalog-exposed, not imported), and TAF TSI + IATA ONE Record added to
  `standards_alignment`.

## [1.14.0] - 2026-08-10

Closes the transport-order gap ([#29](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/29))
and the mode-specialisation question ([#33](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/33)).
Both turned out to be the same gap seen from opposite ends: the missing thing was a **grain**
(demand-side order), not a generic mode-agnostic supertype — MMT already supplies that.

### Changed
- **Mode specialises the leg, never the order.** An order is multimodal by construction, so a
  mode subclass axis on the order breaks on the first intermodal order. Mode-specific standards
  bind at the leg's carrier reservation, where their semantics actually hold — which is what
  makes subclassing `dcsa:Booking` legitimate for ocean scope without imposing
  `carrierBookingReference` on road-only hubs. The binding stays hub-local pending the
  cross-model-axiom decision (`convergence-analysis.md` stakeholder decision #9).
- **Logistics Accelerator** bumped to 1.8.0 — now imports `blueprint/transport-order`, its only
  non-standards-derived import, called out explicitly in the pack's `dcterms:description` so
  consumers can see which classes carry no standard provenance. `class-inventory.yaml`
  regenerated.
- **Archetype catalog** bumped to 0.5.0 — `TransportOrder` is `required` for `freight-forwarder`,
  `recommended` for `unit-load-carrier`, and **deliberately absent** for `shipping-carrier`,
  which is supply side and whose incoming demand already *is* the booking. The absence is
  commented in the file so it does not read as unreviewed. Per-archetype tiering is the
  mechanism for this variation — no archetype-flavoured blueprints were added.
- `client-hub-blueprint/data-domains.yaml` Booking domain gained a `grain_note` stating that
  "transport order" and "booking" are distinct grains with a 1..N fan-out, resolving the #29
  finding that the blueprint claimed ownership of a class that did not exist.
- **Freight-forwarder discovery guide §3 corrected.** It told interviewers to "record it as a
  potential gap until its grain is proven" — stale now that the audit is complete and the class
  exists. Rewritten to point at `TransportOrder`, to make the 1..N fan-out the thing discovery
  must still confirm from source data, and to flag mode-typed orders as a known anti-pattern to
  redirect.

### Known gaps (not addressed here)
- **No `not_applicable` tier** in `archetype.schema.json`, so `shipping-carrier` omitting
  `TransportOrder` on purpose is machine-indistinguishable from nobody having reviewed it. The
  intent is currently carried by a YAML comment only.
- **No archetype-to-pattern link.** `capability-coverage.yaml` has `pattern_ids`; archetype files
  have no equivalent, so the pattern that governs a concept's shape is reachable only through
  the discovery guide's prose. Changing this touches the cross-repo contract.
- Convergence gaps **3** (booking amendment/version history), **4** (equipment
  allocation/utilisation), and **6** (source-neutral event envelope) remain unclaimed by any
  pattern.
- **`patterns/_schema/pattern.schema.json` is still owed.** Both triggers the v0.1 README set for
  writing it have now fired. The parse guard added here catches malformed YAML, not a
  wrong-but-parseable pattern.
- **`VALID_TIERS` is duplicated across repos** — `archetype.schema.json` here and
  `archetype_loader.py` in the toolkit, which comments that it mirrors ours. Adding a
  `not_applicable` tier requires a coordinated pair of PRs; a schema-first change would break the
  consumer on the next ref-model bump.

## [1.13.0] - 2026-08-09

Harvests learnings from a client hub implementation back into the Logistics Accelerator, per
`.docs/wip/refmodelchange.md`, while keeping the pack aligned to the industry models rather than
to any single implementation — see "Added" for the mechanism that enforces that boundary.

### Removed
- Logistics client-hub-blueprint `examples/extensions/` starter templates
  (9 `*-silver-ext.ttl` + README). Silver extensions are authored per hub via the
  `kairos-design-silver` skill; the static examples were illustrative-only,
  unvalidated, and prone to drift.

## [1.6.0] - 2026-06-20

### Migration
- Migrated from kairos-core-ontology-hub repository
- Content separated for independent versioning
- Git history preserved for all ontology files

---

## Version Numbering

### MAJOR.MINOR.PATCH (e.g., 1.0.0)

**MAJOR** version when:
- Breaking changes to core ontology structure
- Remove existing classes or properties
- Change cardinality constraints (more restrictive)
- Modify domain/range restrictions (breaking)
- Rename classes or properties

**MINOR** version when:
- Add new classes or properties (backward compatible)
- Add new SHACL constraints (non-breaking)
- Add new SKOS mappings
- Deprecate features (with backward compatibility)
- Update FIBO to new version

**PATCH** version when:
- Fix typos in labels, comments, documentation
- Update SHACL error messages
- Documentation improvements
- Fix bugs in SKOS mappings
- Update README or examples

---

## Upgrade Guide

### From 1.0.0 to Future Versions

When upgrading, always:
1. Read the CHANGELOG entry for the new version
2. Check for BREAKING CHANGES in MAJOR versions
3. Update customer ontologies if affected
4. Revalidate all customer data
5. Test projection generation
6. Deploy to staging before production

### Breaking Change Migration

If a MAJOR version introduces breaking changes:
1. The CHANGELOG will include a "Breaking Changes" section
2. Migration guide will be provided in examples/
3. Deprecated features will be documented
4. Support for old version continues for one MINOR version cycle

---

## Future Roadmap

### Planned for 1.1.0 (MINOR)
- Add `Invoice` class linked to Orders
- Add `PaymentMethod` class for payment tracking
- Enhanced SKOS mappings for FIBO alignment
- Additional SHACL shapes for data quality

### Planned for 2.0.0 (MAJOR - If Needed)
- Restructure class hierarchy (if business requirements change significantly)
- Potential namespace changes for better URN structure
- Integration with additional industry standards

---

**Note:** This changelog will be updated with each release. Contributors should add entries under "Unreleased" during development.

[1.0.0]: https://github.com/Cnext-eu/kairos-reference-models/releases/tag/v1.0.0
