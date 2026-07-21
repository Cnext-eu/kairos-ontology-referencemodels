# Logistics Accelerator dbt Silver Design Plan

**Status:** Draft
**Date:** 2026-07-21
**Scope:** Kairos Logistics Accelerator Pack
**Target platforms:** Microsoft Fabric and Azure Databricks

## 1. Decision

The Logistics Accelerator should evolve in two deliberately separated stages:

1. a source-neutral, feature-rich logistics blueprint that resolves competing classes,
   grains, roles, lifecycle concepts, and standards authority; and
2. an explicitly activated Silver Starter profile with runnable, synthetic dbt examples
   for Microsoft Fabric and Azure Databricks.

The blueprint is the first deliverable and a hard gate for the Silver Starter. The
repository must not publish a canonical table contract merely because similarly named
classes exist in one or more imported standards.

The accelerator must not ship a supposedly universal production transformation tied to
one TMS, ERP, carrier, warehouse, or downstream ontology hub. A consuming hub binds the
approved profile to its sources through Bronze vocabularies, SKOS mappings, and, where
necessary, contracted custom dbt transformations.

The eventual package should contain:

1. a canonical class and relationship registry with authority and grain decisions;
2. a feature-rich logistics blueprint organised by capability and lifecycle;
3. an opt-in Silver Starter profile for selected canonical classes;
4. synthetic source vocabularies and mappings for runnable examples;
5. generated Fabric and Databricks reference output; and
6. conformance tests proving the examples implement the same semantic contract.

## 2. Goals

- Give adopters an immediately understandable logistics Silver target.
- Demonstrate how the industry models become practical dbt entities.
- Reuse evidence-backed relationships, physical policy, data types, and tests across
  consuming hubs.
- Resolve competing classes without flattening distinct grains or lifecycle concepts.
- Make accelerator-specific materialisation an explicit opt-in profile.
- Keep ontology and Silver annotations authoritative over generated artifacts.
- Allow consuming hubs to override profile defaults without modifying reference
  ontologies.
- Support an incremental adoption path instead of requiring the entire logistics graph.
- Provide equivalent semantic contracts for Fabric and Databricks.

## 3. Non-goals

- A universal mapping from every logistics source system.
- Production-ready business rules for a specific carrier, forwarder, or terminal.
- Customer-specific identifiers, PII, credentials, endpoints, or proprietary samples.
- Hand-maintained dbt SQL that duplicates ontology projection logic.
- Projection of every imported DCSA, MMT, BSP, TIC, IMO, WCO, and sustainability class.
- Gold facts, dimensions, measures, or Power BI models in the first delivery.
- Runtime MDM matching, survivorship, or stewardship workflows.
- Automatic materialisation of every class imported by the accelerator.
- Treating matching labels as evidence that classes are equivalent.
- Adding convenience classes before completing a documented reference-model gap audit.

## 4. Design principles

### 4.1 Blueprint first, contract second, binding third

The accelerator first defines canonical semantic choices and extension points. A Silver
contract may be generated only after the relevant class, grain, identity, and
relationship decisions pass the blueprint convergence gate.

Aspirational stubs may expose approved target contracts before a source is bound. They
must not be used to bypass unresolved semantic decisions. A source mapping clears the
aspirational state and causes projection to generate the bound model.

### 4.2 Selective materialisation

The full accelerator imports eight broad industry models. Only an opinionated,
high-value subset should be eligible for the opt-in Silver Starter profile. Consuming
domains should continue to import only the modules they need.

### 4.3 Generated artifacts are derivative

OWL ontologies, Silver profile annotations, source vocabularies, and SKOS mappings are
the source artifacts. Committed dbt output is a reference snapshot and must be
reproducible. It must not become a second design authority.

### 4.4 Portable semantics, adapter-specific SQL

Fabric and Databricks outputs share entity grain, keys, relationships, tests, and
documentation. Adapter-specific types, materialisations, and SQL remain separate
generated concerns.

### 4.5 Safe extension

Accelerator profile defaults provide fallback values only after explicit activation. A
consuming `{domain}-silver-ext.ttl` remains the highest-priority authority and may
override SCD policy, natural keys, inclusion, physical names, or other supported
annotations.

The current toolkit discovers reference defaults only as sibling files beside resolved
ontology modules. That mechanism is unsuitable for accelerator-specific policy because
it would apply the same defaults whenever a module is imported outside the Logistics
Accelerator. The implementation must therefore either add explicit profile discovery
or defer automatic defaults. A central `silver-defaults/` folder must not be introduced
unless toolkit discovery and precedence rules support it.

### 4.6 Promote evidence, not legacy shapes

Existing warehouses, report models, public schemas, mapping workbooks, and hand-authored
dbt are important discovery evidence, but they are not automatically canonical
contracts.
Classify each finding before promoting it:

| Evidence class | Governed destination |
|---|---|
| Industry-stable entity, grain, identifier, or relationship | Reference ontology and accelerator Silver profile |
| Straight source-to-property equivalence | Bronze vocabulary and SKOS mapping |
| Source-specific joins, unions, windows, deduplication, parsing, or grain changes | Contracted intermediate dbt transformation |
| Organisation policy, alias, exclusion, survivorship, or local code | Consumer mapping, seed, hub extension, or governed MDM policy |
| Report role, current-state reduction, KPI, aggregation, or display classification | Gold |
| Diagnostic helper, duplicated logic, or mixed-grain compatibility shape | Staging/diagnostic output or reject |

The promotion test is portability: a default belongs in the accelerator only when its
meaning and grain remain valid for a structurally different logistics source and
organisation. Strong evidence from one source can justify an example implementation,
but not an industry-wide default.

### 4.7 Grain and identity precede columns

Every Silver entity must distinguish four identities:

1. **Business grain** -- the real-world occurrence represented by one row.
2. **Source identity** -- `source_system` plus an immutable `source_record_id`.
3. **Natural key** -- business properties that identify the occurrence within a stated
   scope; source-local keys must be labelled as such.
4. **Warehouse identity** -- generated surrogate key and projection-scoped IRI.

Do not merge records from different systems merely because display numbers overlap.
Cross-source survivorship is allowed only after an explicit equivalence or MDM decision.
Source priority may choose attributes for already matched identities; it must not be the
matching rule itself.

## 5. Candidate first vertical slice

The following is an analysis backlog, not an approved canonical contract:

| Candidate concept | Grain hypothesis | Required convergence question |
|---|---|---|
| Party | One legal or operational party identity | Is BSP `TradeParty`, MMT `TransportParty`, or a role pattern authoritative? |
| Location | One role-neutral physical or addressable place | Which location classes are identities, specialisations, or role-specific views? |
| Booking or transport order | One commercial request for transport | Does an existing Booking, SalesOrder, or PurchaseOrder express the required grain, or is there a proven gap? |
| Consignment | One responsibility and goods-movement grouping | How does MMT Consignment differ from BSP Consignment and Shipment? |
| Shipment | One operational shipment occurrence | Is Shipment a distinct universal grain or specific to an operating archetype? |
| Transport equipment | One equipment identity or usage occurrence | Separate durable equipment identity from shipment-specific equipment utilisation. |
| Transport movement | One planned or actual movement occurrence | Determine whether movement, leg, and stop are separate grains. |
| Transport event | One immutable event occurrence | Determine shared event envelope versus standard-specific event families. |

No `TransportOrder` class currently exists in the reference models under that name.
The blueprint must not assume that such a class is canonical. It must first test the
existing Booking and order concepts and record any semantic gap.

Exact class URIs must be selected from the imported DCSA, MMT, BSP, TIC, IMO, WCO, and
Supply Chain ontologies before implementation. New accelerator classes may be
introduced only after a reference-model audit documents that composition, role
modeling, or alignment cannot express the requirement.

Customs, dangerous goods, terminal operations, demurrage and detention,
sustainability, invoicing, and MDM should follow as later vertical slices.

## 6. Silver policy to design

Every materialised class must have explicit, reviewed defaults rather than relying on
projector conventions.

| Concern | Initial policy |
|---|---|
| Silver inclusion | Explicit allow-list of first-slice classes |
| Schema ownership | Owning consumer domain, never one forced global logistics schema |
| Table naming | Plain entity names; reserve fact/dimension prefixes for Gold |
| Natural keys | Industry identifier only where universally scoped; otherwise require consumer configuration |
| Surrogate keys | Generated by the Kairos dbt projection |
| IRI lineage | Retained on every normal entity |
| SCD type | No universal default until physical-policy evidence is reviewed |
| Events | Append-only occurrence grain by default; derive current state downstream |
| Reference data | Explicitly identified and reviewed for safe inlining |
| Foreign keys | Explicit for imported object properties lacking cardinality |
| Temporal FK resolution | Join to the intended current or as-of parent version explicitly |
| Inheritance | Preserve semantic annotation; Silver projection may flatten subtypes |
| Nullability | Derived from SHACL and explicit overrides |
| PII | Document sensitivity guidance; physical isolation remains consumer policy |
| Row lineage | Toolkit-owned audit capability, enabled consistently by generated output |
| Change detection | State explicitly whether relationship/FK changes create entity history |
| Audit envelope | Use the standard generated load, hash, and soft-delete columns |
| Multi-source conformance | Conform each source first; match and survive only under governed identity rules |

Natural keys, relationship direction, SCD behavior, and physical privacy controls are
design checkpoints, not assumptions. Semantic evidence from a standard can justify a
class or relationship; it does not by itself justify warehouse history policy or a
cross-organisation natural key. A profile default must be omitted when the evidence is
insufficient.

### 6.1 Blueprint convergence analysis session

Before selecting the first slice, run a dedicated, evidence-led analysis series. Its
purpose is to create a richer blueprint without solving overlap by arbitrarily choosing
one similarly named class.

Run the analysis as four facilitated sessions of approximately 90-120 minutes. Each
session reviews prepared evidence, records decisions and confidence, and ends with an
explicit approve, defer, or investigate outcome. Do not carry unresolved assumptions
silently into the next session.

#### Preparation

Build an evidence pack containing:

1. every candidate class and object property from DCSA, MMT, BSP, TIC, IMO, WCO,
   Sustainability, and the Supply Chain bridge;
2. labels, definitions, cited standards, superclass chains, domain/range, cardinality,
   identifiers, and lifecycle properties;
3. existing accelerator overlap decisions from
   `client-hub-blueprint/data-domains.yaml`;
4. at least two structurally different synthetic or public logistics source shapes; and
5. representative capability questions from the accelerator discovery materials.

#### Session A: authority and vocabulary

- Compare candidate concepts by normative definition rather than label.
- Identify the strongest authority for each capability and operating context.
- Mark classes whose standard provenance is weak, indirect, or implementation-derived.
- Record terminology aliases separately from semantic equivalence.

#### Session B: grain, identity, and lifecycle

- Write a one-sentence grain and lifecycle boundary for each candidate.
- Separate durable identity from transaction, assignment, usage, state, and event.
- Test whether Consignment, Shipment, Booking, order, movement, leg, stop, and call are
  distinct grains.
- Separate equipment identity from equipment utilisation and allocation.
- Separate Party and Location identity from their contextual roles.

#### Session C: overlap disposition

Assign every apparent overlap exactly one disposition:

| Disposition | Meaning |
|---|---|
| Canonical authority | Same concept and grain; one class is selected as authoritative |
| Specialisation | One concept is a genuine subtype of another |
| Contextual role | The apparent class is better represented as a role or assignment |
| Distinct grain | Similar label, but a different business occurrence or lifecycle |
| Cross-standard alignment | Concepts remain separate but receive a documented mapping |
| Deferred | Evidence is insufficient; exclude it from the first profile |
| Reference-model gap | No existing composition expresses the required concept |

`owl:equivalentClass` is allowed only where identity conditions, grain, and lifecycle
semantics are demonstrably equivalent. Shared labels alone are insufficient.

#### Session D: relationships and feature richness

- Define role-neutral core relationships and contextual role assignments.
- Review relationship direction, cardinality, temporal meaning, and ownership.
- Design a shared event envelope without erasing standard-specific event semantics.
- Identify reusable patterns for documents, references, status, measurements, locations,
  parties, equipment assignments, and transport topology.
- Map each capability to canonical classes, optional specialisations, relationships, and
  extension points.

#### Required outputs

1. `canonical-class-registry.yaml` with URI, authority, grain, identity, lifecycle,
   disposition, evidence, confidence, and maturity;
2. `overlap-register.yaml` covering every competing or similarly named class;
3. `relationship-registry.yaml` with domain, range, direction, cardinality, and temporal
   semantics;
4. a capability coverage matrix showing supported, deferred, and extension concepts;
5. canonical and standards-overlay ERDs;
6. a decision log for every canonical selection and rejected alternative; and
7. a prioritised reference-model gap backlog.

**Convergence gate:** every first-slice concept has one reviewed disposition, one
unambiguous grain, and no unresolved competing class. Deferred concepts are excluded
from the Silver profile rather than resolved by assumption.

### 6.2 Silver implementation rules

1. Write a one-sentence grain contract and key scope before selecting properties.
2. Require an immutable source identity even when a business number is present.
3. Namespace source-local identifiers; never solve collisions with an undocumented
   prefix embedded in a supposedly universal natural key.
4. Keep source admission, normalization, deduplication, and fan-out prevention in a
   contracted transform when they exceed ordinary mapping expressions.
5. Resolve Silver FKs against an explicit temporal view. For current-state loading,
   join only to current SCD2 parent rows; for as-of analysis, use effective-date logic.
6. Decide per relationship whether an FK change is part of the child's history and
   include it in change detection when it is.
7. Use timestamp precision or an explicit sequence when more than one valid change per
   entity per day is possible.
8. Store business aliases, port-code normalization, exclusion lists, and classifications
   as governed data or consumer rules, not accelerator-wide SQL `CASE` expressions.
9. Preserve intentional non-equivalence as metadata: an unmapped field stays null with
   a reason rather than being populated from a semantically similar field.
10. Test natural-key grain, source identity, current-row uniqueness, FK integrity,
    accepted status/code values, intentional-null assumptions, and cross-adapter contract
    equivalence.

The accelerator conformance suite must catch unresolved target-first models emitting
null keys into incremental SCD models, SCD2 parent joins fanning out over historical
rows, adapter-unsafe schema names, and lost row-level source lineage.

## 7. Package contents

The logistics accelerator should evolve toward a versioned release structure such as:

```text
ontology-reference-models/
  accelerator-packs/
    logistics/
      current/
        logistics-accelerator.ttl
        blueprint/
          canonical-class-registry.yaml
          overlap-register.yaml
          relationship-registry.yaml
          capability-coverage.yaml
          canonical-erd.mmd
          standards-overlay-erd.mmd
        profiles/
          silver-starter/
            logistics-silver-profile.ttl
        contracts/
          generated/
            logistics-silver-contract.yaml
        examples/
          synthetic-forwarder/
          synthetic-carrier-terminal/
        docs/
          blueprint.md
          silver-starter.md
```

All release-bearing artifacts belong in the versioned archive. Because current
repository validation assumes ontology-oriented subfolders under `current/`, Phase 0
must update structure validation, version archiving, and release packaging before this
layout is adopted.

The recommended profile is explicitly activated. Do not place accelerator policy in
sibling module-level `*-silver-defaults.ttl` files: those files would also affect hubs
that import DCSA, MMT, or BSP modules independently of this accelerator. If explicit
profile discovery is not available, publish the blueprint and examples first and defer
automatic profile inheritance.

## 8. Reference implementation

Use two complementary, fictitious examples with no personal or proprietary data:

1. a freight-forwarder-shaped source with orders, consignments, multimodal movements,
   equipment assignments, parties, locations, and events; and
2. a carrier-or-terminal-shaped source with bookings, transport calls, equipment
   operations, locations, and events.

Together they should include:

- small CSV or seed data for orders, consignments, shipments, equipment, legs, events,
  parties, and locations;
- Bronze vocabularies generated from those source structures;
- explicit table-to-entity and column-to-property mappings;
- direct mappings, transformed values, deduplication, FK lookup, and a multi-source
  identity case;
- a contracted intermediate dbt model only where the example genuinely needs joins,
  windows, aggregation, JSON expansion, fallback logic, or a grain change;
- projected Silver models for Fabric and Databricks; and
- dbt tests derived from SHACL plus explicit grain and referential-integrity tests.

The example SQL must remain source-conformance logic. The generated Silver boundary
continues to own ontology alignment, surrogate keys, IRIs, SCD behavior, supported FK
resolution, tests, and documentation.

## 9. Contract and compatibility

Generate a machine-readable contract from the approved blueprint registry and Silver
profile. It must not be a separately hand-authored design authority. The generated
contract describes each accelerator Silver entity:

- canonical class URI;
- business grain;
- natural-key properties, when universally safe;
- required and optional properties;
- FK targets and direction;
- SCD and reference-data policy;
- applicable industry standards;
- supported adapters; and
- maturity level: experimental, preview, or stable.

Compatibility rules:

1. Track semantic compatibility and generated-Silver compatibility separately.
2. Adding an ontology class can be semantically additive while changing an activated
   profile remains potentially breaking.
3. Adding a materialised entity, table, key, relationship, or required property requires
   a generated-contract impact assessment; it is not automatically backward-compatible.
4. Changing grain, identity scope, a natural key, FK direction, relationship
   cardinality, SCD behavior, or physical naming is breaking.
5. Removing or renaming a stable model is breaking.
6. Generated output records accelerator, profile, contract, and toolkit versions.
7. Consumer overrides are permitted but must be visible in generated documentation.

The first profile release remains **preview** until it has been validated against at
least two structurally different synthetic or public source shapes and both adapters.
A JSON Schema and deterministic validation command must cover all blueprint registries
and the generated contract.

## 10. Implementation phases

### Scope boundary

| Scope | Owns | Must not contain |
|---|---|---|
| Generic toolkit capability | Profile discovery, precedence, projection behavior, temporal SCD/FK handling, lineage, generated tests, and adapter conformance | Logistics-specific classes, grains, identifiers, or policy |
| This reference-model repository | Standards-backed semantics, convergence registries, blueprint, opt-in profile, synthetic examples, generated contract, and compatibility evidence | Proprietary schemas, production bindings, organisation policy, or source-specific aliases |
| Consuming ontology hubs | Source vocabularies, mappings, local extensions, admission rules, transformations, matching, and survivorship | Claims that local behavior is an accelerator default |

### Phase 0: Architecture and repository pre-flight

1. Decide and document explicit accelerator-profile discovery and precedence.
2. Reject module-sibling defaults for accelerator-specific inclusion policy.
3. Define schemas for blueprint registries and generated contracts.
4. Decide how release-bearing non-ontology artifacts are archived.
5. Update structure validation and release packaging for the selected layout.
6. Define semantic and generated-contract compatibility diff rules.

**Exit criterion:** profile discovery, layout, archiving, validation, and compatibility
mechanisms are approved before content files are created.

### Phase 1: Blueprint convergence analysis

1. Prepare the cross-standard evidence pack.
2. Run Sessions A-D from section 6.1.
3. Populate the class, overlap, relationship, and capability registries.
4. Resolve or defer every competing first-slice concept.
5. Produce canonical and standards-overlay ERDs.

**Exit criterion:** the convergence gate in section 6.1 passes.

### Phase 2: Feature-rich blueprint design

1. Organise capabilities independently of any source-system shape.
2. Document identity, role, assignment, lifecycle, event, document, reference-data, and
   transport-topology patterns.
3. Define explicit extension points for operating-archetype specialisation.
4. Record supported, optional, deferred, and out-of-scope capabilities.
5. Convert confirmed semantic gaps into auditable ontology change proposals.

**Exit criterion:** the blueprint is useful without requiring a Silver implementation
and contains no unresolved first-slice semantic collision.

### Phase 3: Cross-archetype evidence validation

1. Define freight-forwarder-shaped and carrier-or-terminal-shaped synthetic or public
   source models.
2. Test each canonical grain and relationship against both shapes.
3. Record where concepts are absent, specialised, split, or combined.
4. Revisit any choice that requires source-specific assumptions.

**Exit criterion:** semantic choices remain valid across both source shapes; unsupported
physical choices remain unset.

### Phase 4: Reference-model refinement

1. Audit each confirmed gap against its cited standard.
2. Prefer alignment, composition, roles, and relationships over duplicate classes.
3. Add or change ontology content only where the audit proves a reusable gap.
4. Archive and version every affected ontology according to repository policy.
5. Re-run the convergence registries after ontology changes.

**Exit criterion:** all promoted ontology changes are standards-backed, versioned, and
reflected in the blueprint.

### Phase 5: Opt-in Silver Starter profile

1. Select only mature blueprint concepts for materialisation.
2. Add explicit inclusion, physical naming, reference-data, and inheritance policy.
3. Add natural keys only with universal scope evidence; otherwise require configuration.
4. Add SCD policy only with physical-design evidence from both source shapes.
5. Declare FK placement and temporal resolution explicitly.
6. Generate the machine-readable contract from the profile and registries.

**Exit criterion:** the profile is explicitly activated, annotation-complete, and free
of unsupported semantic or physical assumptions.

### Phase 6: Synthetic bindings and adapter validation

1. Create Bronze vocabularies and mappings for both source shapes.
2. Add contracted transformations only for genuine joins, windows, aggregation, parsing,
   fallback rules, or grain changes.
3. Generate Fabric and Databricks dbt projects.
4. Compile and execute fixtures where infrastructure is available.
5. Run SHACL-derived, grain, FK, temporal, lineage, and contract-equivalence tests.

**Exit criterion:** both adapters implement the same generated contract for both source
shapes.

### Phase 7: Packaging and preview release

1. Archive the complete previous accelerator release.
2. Bump accelerator and profile versions according to compatibility impact.
3. Update `manifest.yaml`, `README.md`, `CHANGELOG.md`, and catalog entries where needed.
4. Commit reproducible expected output for reference examples only.
5. Publish blueprint, profile, generated contract, ERDs, and regeneration instructions.

**Exit criterion:** the preview release is reproducible, fully archived, schema-valid,
and consumable without modifying reference ontology files.

## 11. Acceptance criteria

- The first-slice classes and properties trace to named industry/reference models.
- Every competing first-slice class has a recorded overlap disposition.
- No canonical choice is based only on a matching label.
- The blueprint documents roles, assignments, lifecycle, events, and extension points.
- The Silver profile is explicitly activated and does not leak through module imports.
- Every projected class has explicit applicable Silver annotations.
- Every natural key has documented universal scope or is explicitly consumer-required.
- Every entity documents business grain, source identity, natural-key scope, surrogate
  key, and IRI convention separately.
- Every FK has reviewed cardinality and placement.
- Every SCD2 FK resolution declares current-state or as-of semantics and has a
  relationship test.
- Every SCD2 model defines sub-day change behavior and whether FK changes affect history.
- Toolkit-generated lineage retains source-system and immutable source-record identity.
- Both synthetic examples contain no PII or proprietary content.
- Claims and mapping coverage pass for both declared example scopes.
- Fabric and Databricks dbt projects compile.
- Runtime fixture tests prove grain uniqueness and expected relationships.
- Contract tests reject unresolved null-key incremental models and historical FK fan-out.
- Generated output is reproducible from committed source artifacts.
- Consumer extensions override profile defaults without modifying the accelerator.
- The generated contract is derived from the profile and registries, not hand-maintained.
- Release archives contain all blueprint, profile, contract, example, and documentation
  artifacts needed to reproduce that version.
- Documentation clearly distinguishes canonical contracts, examples, and production
  source bindings.

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| The full industry graph produces an unusably large Silver layer | Materialise an explicit first-slice allow-list |
| Similar labels hide different grains | Run the convergence analysis and classify every overlap |
| DCSA, MMT, BSP, and other concepts overlap | Select authority per grain; retain valid specialisations and alignments |
| Natural keys differ by organisation | Default only universally scoped keys; otherwise require configuration |
| Accelerator defaults leak into independent module imports | Use an explicitly activated profile, not sibling module defaults |
| Example SQL becomes mistaken for production logic | Label it synthetic and keep mappings/contracts authoritative |
| A hand-maintained YAML contract becomes a second authority | Generate it from the approved profile and registries |
| Release archives omit examples or contracts | Archive all release-bearing artifacts and test reproducibility |
| Generated snapshots drift from source artifacts | Add deterministic regeneration checks |
| Fabric and Databricks behavior diverges | Validate the same semantic contract independently per adapter |
| Accelerator policy constrains consumer design | Preserve hub-level override priority and document every override |
| Privacy policy is incorrectly universalised | Keep semantic sensitivity guidance separate from consumer physical controls |
| Legacy report shapes become canonical entities | Apply the evidence-classification and promotion test before modeling |
| Source-priority survivorship merges different real-world entities | Require explicit matching/equivalence before survivorship |
| SCD2 parent history multiplies child rows during FK resolution | Require current/as-of join semantics and relationship tests |
| Source lineage is lost after semantic projection | Make source system and immutable source record ID part of the Silver contract |
| Source-local aliases leak into industry defaults | Keep aliases, filters, and code normalization in consumer mappings, seeds, or transforms |

## 13. Open design decisions

1. What explicit activation mechanism should load the Logistics Silver profile?
2. Which classes pass the convergence gate for Party, Location, Booking/order,
   Consignment, Shipment, equipment, movement, and event?
3. Is a transport-order concept a reference-model gap or a contextual use of an existing
   Booking or order class?
4. Is Consignment distinct from Shipment across both evidence archetypes?
5. Should TransportEvent use a shared envelope, separate event families, or both?
6. Which identifiers are universally scoped natural keys versus example-only keys?
7. Which small code lists can be safely inlined without harming interoperability?
8. Which generated outputs belong in release archives versus CI artifacts?
9. What maturity and compatibility metadata belongs in the accelerator manifest schema?
10. Which relationship changes create a new SCD2 child version?
11. Should source lineage be physical columns, a generated audit envelope, or a standard
    lineage satellite?
12. Which deferred capabilities should form the second profile slice?

## 14. Recommended delivery

Deliver the **Logistics Blueprint** first, followed by a **preview Logistics Silver
Starter**. The blueprint convergence sessions determine the actual first slice; the
eight candidate concepts are not pre-approved entities.

Validate the selected slice with freight-forwarder-shaped and carrier-or-terminal-shaped
synthetic or public sources and both adapters. Add customs, finance, terminal,
sustainability, and MDM slices only after the same convergence process.

This sequence produces a more feature-rich blueprint without collapsing valid
standard-specific grains into competing tables. Industry semantics define reusable
targets, explicit profiles define optional physical defaults, and each consuming
organisation's source evidence determines its transformations.
