# Changelog

All notable changes to the Kairos Reference Models will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.14.0] - 2026-08-10

Closes the transport-order gap ([#29](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/29))
and the mode-specialisation question ([#33](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/33)).
Both turned out to be the same gap seen from opposite ends: the missing thing was a **grain**
(demand-side order), not a generic mode-agnostic supertype — MMT already supplies that.

### Added
- **Blueprint ontology tier** at `blueprints/ontology/` (v0.1.0) — Kairos-authored OWL classes
  for grains no installed standard expresses. Ships `TransportOrder` (demand-side order owned by
  the arranging party) and `CarrierReservation` (the slot at which a mode-bound standard
  attaches). Separate tier because `derived-ontologies/` is bound to be faithful to its source
  standard, and the issue #29 audit found no standard behind this grain. The folder README
  states a four-point admission bar so the tier does not become a dumping ground.
- **`multimodal-order-leg` pattern** (`blueprints/patterns/`, bumped to 0.2.0) — the four-grain
  shape order → leg → reservation → movement, closing declared convergence gap 5. Records the
  per-mode alignment targets for the reservation grain: DCSA (ocean, modelled), IATA ONE Record
  (air, extension point — *not* Cargo-XML, which is document grain), TAF TSI (rail, extension
  point — *not* RailML, which is infrastructure grain). Project cargo is documented as **not a
  mode** — it cuts across all of them.
- **`transport-order` and `carrier-reservation` concepts** in
  `canonical-class-registry.yaml`, plus overlap entries `transport-order-grain`
  (`distinct_grain`) and `transport-order-mode-axis` (`specialisation`).
- Decision-log entries `LOG-BP-012` (transport order grain) and `LOG-BP-013` (transport mode
  axis), and three new rejected shortcuts.
- **Anchor-selection invariant** documented in `blueprints/README.md`. `validate_archetypes.py`
  has cited this section in its warning text since 1.13.0, but the section did not exist — the
  warning pointed readers at nothing.
- **Archetype authoring guidance** in `blueprints/archetypes/README.md`: anchor generality,
  expressing archetype variation through `tier` rather than forked catalogs, commenting
  deliberate omissions, and a companion-pattern table.
- `transport-order-orchestration` capability in `capability-coverage.yaml`, linked to the new
  pattern via `pattern_ids`, with air and rail alignment recorded as extension points.

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

### Fixed
- **`temporal-quartet/pattern.yaml` was invalid YAML** from the day it shipped (1.13.0). A stray
  `rule:` mapping key inside a block sequence parses as an error but reads fine to a human, so
  review missed it. `kairos-ontology-toolkit`'s `pattern_loader` skips a malformed pattern
  silently during bulk listing — so the library's only *normative* naming pattern was never
  visible to the `kairos-design-domain` flow, and no check in either repo failed. Found by
  running the toolkit's own loader against this branch.
- **The stale claim that caused it.** `patterns/README.md` and `blueprints/README.md` both stated
  there was no toolkit consumer for the pattern library. There is one, and its loader was written
  lenient *because* this repo said the library had no schema — each repo relying on the other's
  assumption. Both statements corrected.
- **`validate_structure.py` now parses every `blueprints/patterns/<id>/pattern.yaml`** and checks
  `id` against the directory name. Parse-only floor, not the owed JSON Schema.
- **Cross-repo contract tests** at `tests/test_toolkit_contract.py`, loading this working tree
  through the toolkit's *real* loaders rather than a local guess at what they do. Skipped when
  the toolkit is not on the machine (set `KAIROS_TOOLKIT_SRC`, or keep a sibling checkout), so CI
  here needs no cross-repo dependency. Asserts every pattern loads via the fail-fast path, bulk
  loading emits no warnings, `VALID_TIERS` still matches our schema enum, every archetype
  resolves, and the three-way `TransportOrder` tiering is visible to the consumer. A mirror ships
  in the toolkit. Neither repo's CI could previously see the other, which is the whole reason the
  `temporal-quartet` defect survived two minor versions.
- `naming_conventions` is documented as a list-only block; whole-block prose belongs in a sibling
  `naming_rule` key. Applied to `temporal-quartet` and `multimodal-order-leg`.

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

### Added
- **Evidence provenance and a bias firewall.** `canonical-class-registry.yaml` concepts now
  carry `evidence_basis` (`standard | pack-consistency | implementation | analysis`);
  `validate_logistics_blueprint.py` rejects `disposition: approved` on a concept whose
  `evidence_basis` is `implementation` — client implementation evidence may raise,
  corroborate, or force re-review of a concept, but never authorises it alone.
- **Implementation attestations** at `current/blueprint/evidence/attestations/`
  (`_schema/attestation.schema.json`), source-neutral by schema. First attestation
  (`att-001`) committed.
- **Pattern library** at `blueprints/patterns/` (v0.1.0) — `deferred-relationship`,
  `qualified-role-assignment`, `temporal-quartet`, `governed-code-list`. Naming conventions
  are normative; structural guidance is advisory. `capability-coverage.yaml` gained an
  optional `pattern_ids` field linking capabilities to patterns. Markdown-first: no JSON
  Schema yet, since there is no toolkit consumer for this folder today.
- **`unit-load-carrier` archetype** (`blueprints/archetypes/`, bumped to 0.4.0) — non-
  containerised ro-ro / short-sea carrier with own-account and subcontracted road haulage,
  170 core concepts across 19 business areas, plus its paired
  `discovery/unit-load-carrier.md`. Two declared capability gaps (empty equipment
  repositioning, trade-lane/market-segment) are called out explicitly rather than papered
  over with invented classes.
- **Anchor-generality and orphaned-discovery-doc checks** in `validate_archetypes.py`
  (advisory, never fail the build). The anchor check retroactively delivers the "structural
  regression coverage" the [1.12.1] entry below claimed but did not actually ship.
- **SupplyChain 1.2.0 — `hasMovementEmission` bridge property** (MMT `TransportMovement` →
  Sustainability `CarbonFootprint`), closing the movement/trip-grain emissions attachment gap
  (CR-RM-07 §9.5): operational emissions data commonly lands at movement grain, but the
  existing bridges (`hasCarbonFootprint`, `hasEnergyConsumption`) only attach at consignment
  and transport-service grain. Standards-grounded (ISO 14083 / GLEC, already claimed in
  `manifest.yaml`), not client-evidence-driven. `data-domains.yaml` and `BLUEPRINT.md` updated
  with the new bridge.

### Changed
- **`equipment-asset` re-anchored** from `dcsa/equipment#Container` to the general
  `mmt/equipment#TransportEquipment`, correcting an anchor narrower than the pack's own
  `manifest.yaml` `target_sectors` (road carrier, 3PL, NVOCC are not containers-only).
  Container is recorded as a scope-specific overlay in `overlap-register.yaml`, not the
  anchor. Basis: `pack-consistency`, corroborated but not authorised by `att-001`.
- Two capability gaps added: empty equipment repositioning, trade-lane/market-segment.
- **Logistics Accelerator opened at 1.7.0** (`VERSION`, `manifest.yaml`, the four blueprint
  registries' `accelerator_version`, the accelerator `.ttl`'s `owl:versionInfo`, and the
  regenerated `class-inventory.yaml`, all kept in lockstep — `validate_logistics_blueprint.py`
  fails the build on any one of them drifting from the others).
- Fixed a stale `logistics/README.md` path (missing `current/` segment) and its discovery
  table (missing `freight-forwarder`, then missing `unit-load-carrier`); its inline
  changelog now points at this file instead of duplicating it.
- Replaced `accelerator-packs/financial-services/discovery/README.md` — it was an
  uncorrected verbatim copy of the logistics pack's README, still indexing a
  `shipping-carrier.md` that was never part of this pack (see [1.12.1] below).
- Removed root `README.md` sections describing `ontologies/core.ttl`,
  `shapes/core.shacl.ttl`, and `mappings/schema-org.ttl` — none of these files exist in
  this repository.

## [1.12.1] - 2026-07-22

### Fixed
- Removed the duplicated shipping-carrier discovery guide from the financial-services
  accelerator pack (#26). *Correction (see [Unreleased] above): this entry originally also
  claimed "added structural regression coverage to prevent cross-sector discovery guides
  from being misplaced" — no such coverage was actually added at the time; the
  financial-services `discovery/README.md` remained an uncorrected copy of the logistics
  README until this was caught in review. The coverage now exists.*

## [1.12.0] - 2026-07-21

### Added
- **Logistics Accelerator 1.6.0 Blueprint foundation** with deterministic RDF inventory,
  JSON Schemas, semantic validators, generated-contract tooling, and focused tests.
- **Evidence-backed convergence dossier and unresolved registries** for Party, Location,
  Booking, Shipment/Consignment, equipment, transport topology, events, documents,
  identifiers, measurements, and status. Unreviewed candidates are excluded from the
  first Silver slice.
- **Freight-forwarder archetype and discovery guide**, complementing the existing
  shipping-carrier archetype; archetype catalog version bumped to 0.3.0.
- **Synthetic freight-forwarder and carrier/terminal source shapes** plus a
  cross-archetype assessment and capability-oriented blueprint documentation.

### Changed
- **Logistics Accelerator** opened at 1.6.0 after archiving the complete 1.5.0 baseline.
- Repository validation recognizes versioned accelerator support folders and runs the
  Logistics Blueprint test suite through `python -m pytest`.

## [1.11.0] - 2026-06-22

### Added
- **Expanded `shipping-carrier` archetype** (`blueprints/archetypes/shipping-carrier.yaml`,
  bumped to `0.2.0`) — grew from ~30 to ~140 core concepts and from 9 to 26
  ref-model modules, organised into 21 commented business areas covering the
  full liner shipment lifecycle: commercial cycle (booking → B/L), transport
  documents (B/L, eBL, sea waybill, master/house), consignment, cargo, parties,
  locations, transport calls, vessels & fleet (IMO registry), schedule /
  voyage, port-call execution, equipment & container operations, track-and-trace
  events, demurrage & detention, dangerous goods (IMDG), vessel certificates,
  maritime security (ISPS), environmental compliance, customs filing, trade
  facilitation, and sustainability (CII / EEXI / EU ETS).
- **Sector discovery materials in the logistics accelerator-pack**
  (`accelerator-packs/logistics/discovery/`) — new `README.md` documenting the
  archetype-id ↔ discovery-script pairing convention, plus
  `shipping-carrier.md`: 21 business-area interview sections + a dedicated
  *Structural & lifecycle relationships* section (~16 questions covering
  Booking↔Shipment↔Voyage cardinality, SI↔B/L grain, container-assignment
  timing, T&T event grain, TransportCall vs PortCall granularity, D&D billing
  grain, customs declaration grain) + naming & identifier conventions section.
  Implements the **v0.2 contract**: machine catalog in `blueprints/archetypes/`,
  human discovery prose in `accelerator-packs/<pack>/discovery/<id>.md`,
  toolkit skill as pure consumer.
- **Soft archetype ↔ discovery pairing check** in
  `scripts/validate_archetypes.py` — warns (not errors) when an archetype YAML
  has no matching `discovery/<id>.md` in any accelerator-pack.
- **Catalog mappings** for `imo/certificates-surveys`, `imo/environmental`,
  `imo/maritime-security`, and `imo/crew-seafarer` (previously missing from
  `catalog-v001.xml`), surfaced while resolving the expanded archetype's URIs.

### Changed
- **`accelerator-packs/logistics`** bumped 1.4.0 → **1.5.0** (additive
  `discovery/` subfolder). Pack `manifest.yaml` `package.version` aligned to
  1.5.0 (previously drifted at 1.3.0 — cleaned up in this release).
- `compatible_with.repo_tag_range` on `shipping-carrier.yaml` updated to
  `>=1.10.0,<2.0.0`; `compatible_with.ontology_versions` now also pins IMO,
  WCO, and Sustainability ranges.
- **`blueprints/README.md`** documents the revised v0.2 contract (discovery
  prose lives in accelerator-packs, not in the toolkit skill).

## [1.10.0] - 2026-06-22

### Added
- **Blueprints (opinionated) module** — new third content tier at
  `ontology-reference-models/blueprints/` distinct from authoritative and
  derived ontologies. Initial content: archetype catalog
  (`blueprints/archetypes/`, `schema_version: 1`) with a single
  `shipping-carrier.yaml` referencing DCSA + MMT modules and ~30 core
  concepts. Consumed by the `kairos-design-discovery` skill in
  `kairos-ontology-toolkit` (see issue #23 and toolkit CR #203).
- **`scripts/validate_archetypes.py`** — validates archetype YAML files
  against `_schema/archetype.schema.json` and resolves every
  `ref_model_modules.iri` and `core_concepts.uri` against the local
  `catalog-v001.xml` (rdflib, local-only — no remote dereference).
- **Archetype validation step** in `.github/workflows/validate.yml`.
- **Catalog mapping** for the `dcsa/transport-call` module (previously
  missing from `catalog-v001.xml`), surfaced while wiring up archetype URI
  resolution.

### Changed
- **`scripts/version_manager.py`** — `SCAN_DIRS` now includes
  `ontology-reference-models/blueprints/` so the new `archetypes/VERSION`
  file is reported by `list` and considered by `check`.
- **`scripts/validate_structure.py`** — new `validate_blueprints()` check
  asserts blueprints README, archetypes README + SemVer VERSION + schema
  exist, parses every `*.yaml` with `yaml.safe_load`, and enforces the
  filename-equals-`id` invariant.
- **`README.md`** — added blueprints to the repository-structure tree and
  introduced a new "Blueprints (opinionated guidance)" section explaining
  the three-tier model.
- **`NOTICE`** — added paragraph clarifying that `blueprints/` is
  opinionated Kairos content (Apache-2.0), distinct from authoritative
  third-party material.

## [1.9.0] - 2026-06-21

### Added
- **DCSA v1.3.0 — DCSA Domain v3.1.0 fit-gap alignment.** Added 14 selected
  high-value terms from the DCSA Domain v3.1.0 fit-gap:
  `bookingRequestDateTime`, `bookingUpdatedDateTime`,
  `bargeOperatorCarrierCodeListProvider`, `facilityTypeCodeTRN`,
  `facilityTypeCodeOPR`, and dangerous-goods commodity properties
  (`unNumber`, `imoClass`, `properShippingName`, `technicalName`,
  `packingGroup`, `flashPoint`, `isMarinePollutant`, `isLimitedQuantity`,
  `isReportableQuantity`). The full parsed DCSA Domain v3.1.0 model and
  fit-gap artifacts are available under `.docs/refmodels/DCSA/` for future
  domain discovery.

## [1.8.0] - 2026-06-20

### Changed
- **BSP v1.5.0 — relocate the party→address relationship.** The
  `:hasAddress` / `:hasBillingAddress` / `:hasShippingAddress` object properties
  moved from the `reference-data` module into the `party` module, where their
  `rdfs:domain` (`:TradeParty`) lives. `party` now `owl:imports` `reference-data`
  for the `Address` range. This makes the party module self-contained for address
  navigation — any consumer importing `bsp/party#` gets the relationship without
  separately importing reference-data. The `Address` class stays in
  `reference-data` as shared master data; the unused `party:` prefix was removed
  from `reference-data`.
  - Property IRIs changed from `…/bsp/reference-data#hasAddress…` to
    `…/bsp/party#hasAddress…`. These properties were introduced in BSP 1.4.0 with
    no downstream consumers, so impact is minimal.
  - BSP 1.4.0 snapshot archived under `BSP/archive/1.4.0/`.

## [1.7.0] - 2026-06-20

### Added
- **Explicit relationships across logistics reference models** — generic parent
  object properties that make implicit party/location links navigable (the same
  pattern as BSP `party` → `:hasAddress`). Typed roles are retained as
  `rdfs:subPropertyOf` the new generics:
  - **MMT v1.1.0** (`consignment`): `:hasParty` (→ `mmt-party:TransportParty`)
    over consignor/consignee/carrier/freight-forwarder/notify-party; `:hasLocation`
    (→ `mmt-loc:TransportLocation`) over departure/arrival.
  - **DCSA v1.2.0** (`booking`): `:hasParty` (→ `party:ShippingParty`) over
    shipper/consignee/carrier/booking-party/notify-party; `:hasLocation`
    (→ `loc:Location`) over place-of-receipt/port-of-loading/port-of-discharge/
    place-of-delivery/transshipment. (`transport-documents`):
    `:hasDocumentParty` and `:hasDocumentLocation` over the document-level roles.
  - **TIC v1.3.0** (`events`): `:atChargingStation` (→ `tic-infra:ChargingStation`)
    and `:chargedEquipment` (→ `tic-infra:TerminalEquipment`) make the charging
    session's `:chargingStationRef` / `:vehicleRef` identifiers navigable.
    (`party`): `:stevedoresCarrierVisit` (→ `tic-ops:CarrierVisit`) links a
    stevedore to the carrier visits it services.

### Changed
- Logistics accelerator bundle bumped to **1.4.0** to signal the refreshed
  constituent models (BSP 1.4.0, MMT 1.1.0, DCSA 1.2.0, TIC 1.3.0). Imports
  remain version-less ontology IRIs, so the bundle always composes each model's
  `current/` version.

### Removed
- Logistics client-hub-blueprint `examples/extensions/` starter templates
  (9 `*-silver-ext.ttl` + README). Silver extensions are authored per hub via the
  `kairos-design-silver` skill; the static examples were illustrative-only,
  unvalidated, and prone to drift.

## [1.6.0] - 2026-06-20

### Added
- **BSP v1.4.0 — party master-data** (#17, #13):
  - `reference-data`: generic `:hasAddress` (1:n) with `:hasBillingAddress` /
    `:hasShippingAddress` now declared as `rdfs:subPropertyOf :hasAddress`
    (typed roles 0..1, documented cardinality).
  - `party`: new `:Contact` person entity (`rdfs:seeAlso` UN/CEFACT
    `TradeContact`) with `:hasContact` (1:n) and `:contactName` / `:jobTitle` /
    `:contactRole`; `:contactEmail` / `:contactPhone` broadened to cover both
    `TradeParty` and `Contact` (single canonical coordinate).
  - `financial`: new `:BankAccount` entity (1:n via `:hasBankAccount`) with
    `:iban` / `:bic` / `:accountNumber` / `:accountHolderName`; party-level
    `:hasPartyPaymentTerms`; currency-scoped `:creditLimit` +
    `:creditLimitCurrency`. FIBO used as design inspiration only (not imported).
- Logistics accelerator blueprint: surfaced contact persons, address, and
  bank account / credit limit in the party-commercial domain `provides` lists.

### Changed
- BSP reference model bumped to **1.4.0** (all modules) for the additions above.

## [1.5.0] - 2026-06-14

### Added
- **Open-source governance** — repository is now released under the **Apache
  License 2.0** as part of the Kairos Community Edition:
  - `LICENSE` (Apache 2.0), `NOTICE`, `CONTRIBUTING.md` (DCO workflow),
    `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1), `SECURITY.md`
  - `.github/PULL_REQUEST_TEMPLATE.md` and issue templates (bug / feature)
  - `.gitignore` (Python, venv, build artifacts, OS/editor noise)
- **IMO v1.1.0** — 6 new modules: certificates-surveys, crew-seafarer,
  environmental, maritime-security, plus enriched party and locations (#11)
- **TIC v1.2.0** — new KPI and reefer-monitoring modules; enriched party,
  locations, events, automotive-services, handling-operations (#11)
- **DCSA v1.1.0** — new shared-kernel transport-call module; cross-domain
  `rdfs:seeAlso` annotations and declaration headers (#11)
- **WCO v1.2.0** — GoodsItem, Packaging, CustomsProcedure, Consignee/Consignor
  and 50+ new properties (#11)
- **SupplyChain v1.1.0** — 6 new bridge properties (sustainability, WCO goods,
  documents); added to the XML catalog
- Logistics accelerator v1.3.0 — refreshed metadata (WCO 3.0 → 3.10.0),
  blueprint imports and cross-domain bridge table

### Changed
- Relocated 9 `*-silver-ext.ttl` files from the derived ontologies to
  `accelerator-packs/logistics/client-hub-blueprint/examples/extensions/` as
  client starter templates — reference models now hold pure domain semantics
  only (#12)
- README: license badge MIT → Apache 2.0, version badge → 1.5.0, added Kairos
  Community Edition attribution and rewrote the License section
- Updated `ontology-reference-models/catalog-v001.xml` for the new modules

### Removed
- Stale `.github/info/.sparse-checkout` template (referenced directories that no
  longer exist and was never wired into git)
- Untracked an accidentally committed `scripts/__pycache__/*.pyc` artifact

## [1.4.0] - 2026-05-31

### Added
- Version bump release establishing the 1.4.x line (see git history for the
  detailed ontology changes folded into 1.5.0).

## [1.3.0] - 2026-05-19

### Added
- Silver-layer extension files for all BSP derived ontology modules (`derived-ontologies/BSP/current/extensions/`):
  - `party-silver-ext.ttl` — TradeParty hierarchy with discriminator strategy
  - `commercial-silver-ext.ttl` — CommercialTransaction, Product, Shipment, BusinessEvent hierarchies + detail tables
  - `compliance-silver-ext.ttl` — RegulatoryRequirement, TariffClassification (ref), DutyTax, TradeAgreement, CustomsEvent
  - `documents-silver-ext.ttl` — Document hierarchy with 14 subtypes + DocumentEvent
  - `financial-silver-ext.ttl` — Invoice hierarchy, PaymentTerms (ref), Payment, InvoiceLine
  - `reference-data-silver-ext.ttl` — Location hierarchy (ref) + Measurement hierarchy
- All extensions use `kairos-ext:` annotation vocabulary with explicit annotations on every class

### Changed
- Bumped BSP ontology version from 1.0.0 to 1.1.0

## [1.2.1] - 2026-03-01

### Fixed
- Corrected `scripts/test_catalog.py` catalog path to `ontology-reference-models/catalog-v001.xml` (was incorrectly pointing to repo root)
- Removed redundant `ontology-reference-models/` prefix from all relative URI paths in `ontology-reference-models/catalog-v001.xml` so paths resolve correctly from the catalog's own directory (OASIS XML Catalog spec)
- Moved canonical catalog location to `ontology-reference-models/catalog-v001.xml`; removed stale copy from repo root

## [1.2.0] - 2026-03-01

### Changed
- Updated FIBO ontologies from Q3 2025 (master_2025Q3) to Q4 2025 (master_2025Q4)
- Corrected folder structure from `ontologies/authoritative-ontologies/` to `ontology-reference-models/Authoritative Ontologies/`
- Updated all catalog paths to point to correct FIBO version (edmcouncil-fibo-90770ba)
- Fixed download_fibo.py script to use correct target directory
- Fixed test_catalog.py script to use correct catalog path

### Added
- Backward-compatibility redirect for deprecated `FND/Parties/Roles/` → `FND/Parties/Parties/` in catalog

### Removed
- Removed non-existent `FND/Organizations/Organizations.rdf` mapping (module no longer exists in Q4 2025 FIBO)

### Fixed
- Unicode encoding issues in download_fibo.py for Windows console compatibility
- All 22 catalog mappings now validated and working correctly

## [1.0.0] - 2025-01-03

### Added
- Initial release of Kairos reference models
- Core ontology classes:
  - `Customer` - Customer entity with name, email, phone
  - `Order` - Order transaction with orderDate, totalAmount, status
  - `Product` - Product catalog item with SKU, price, category
  - `Service` - Abstract service class with subclasses:
    - `ConsultingService` - Professional consulting services
    - `TechnicalService` - Technical implementation services
    - `TrainingService` - Training and education services
  - `Supplier` - Supplier entity with contact information
- Object properties: `hasCustomer`, `hasProduct`, `hasSupplier`
- SHACL validation constraints in `shapes/core.shacl.ttl`:
  - Customer validation (required name, email pattern, max lengths)
  - Order validation (required fields, totalAmount >= 0)
  - Product validation (unique SKU, required properties)
  - Service validation (duration, deliveryMode constraints)
- SKOS mappings to Schema.org in `mappings/schema-org.ttl`:
  - `kairos:Customer` ↔ `schema:Customer`
  - `kairos:Order` ↔ `schema:Order`
  - `kairos:Product` ↔ `schema:Product`
  - Additional closeMatch and relatedMatch alignments
- FIBO Q3 2025 integration (300+ ontology files):
  - Foundations (agents, organizations, people)
  - Business Contracts
  - Legal Entities
  - Products and Services
  - Financial Dates and Relations
- XML catalog (`catalog-v001.xml`) for FIBO import resolution
- GitHub Actions CI/CD:
  - Automatic validation on every commit
  - Release workflow with version verification
  - Test projection generation
- Documentation:
  - README.md with usage examples
  - examples/basic-usage.md
  - examples/extending-models.md

### Changed
- Reorganized ontologies folder structure:
  - Removed nested `external/` subdirectory
  - Created `authoritative-ontologies/` for official RDF/OWL from standards bodies
  - Created `derived-ontologies/` for our RDF interpretations of non-RDF standards
  - Updated catalog-v001.xml to reflect new paths
  - Updated README.md documentation

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
