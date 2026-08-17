# Standards-backed reference-model gap assessment

**Status:** SUPERSEDED - input population invalid; reasoning retained  
**Date:** 2026-08-17  
**Reference-model baseline:** repository 1.31.0; MMT 2.2.0; DCSA 1.5.0; BSP 2.4.0

> ## Superseded by the gh#97 / gh#98 fixes (repository 1.32.0)
>
> **Do not plan work from the row counts in this report.** The adopter inventory it
> assesses - 1,069 CSV rows, 615 non-excluded - was generated against a defective
> import closure, so the population itself is contaminated:
>
> - **gh#97**: 50 `rdfs:domain` and ~100 `rdfs:range` assertions across 36 modules
>   named classes their module never imported. Such an assertion is silently dropped,
>   so a discovery pass asking "which properties does class X carry" saw fewer
>   properties than the model actually defines. Measured on `bsp:TradeParty`: 9
>   reachable properties before the fix, 13 after.
> - **gh#98**: archetype core concepts were reachable from no data domain at all -
>   `mmt/cargo` measurement classes from `equipment` and `consignment`, plus
>   `mmt/locations` (5 tier-required concepts), `dcsa/party` (4 tier-required) and the
>   MMT dangerous-goods terms.
>
> Every count in sections 4, 5.3, 5.4 and 6 is therefore a lower bound on reuse and an
> upper bound on genuine gaps. Section 5.3's 24 rows whose proposed property name
> already exists elsewhere were the visible tip of gh#97.
>
> **What still stands.** The *reasoning* is unaffected - sections 3.1, 3.3 and 4.5
> already argued from the corrected position, which is why the original report was
> retracted rather than acted on. The decision rule in section 1, the do-not-change
> list in section 8, and the official references in section 9 all carry forward
> unchanged.
>
> **Two findings survive both fixes and are the real remaining work.** Sections 4.2
> (`GoodsItem`) and 4.3 (`TransportEquipment`): `hasDimension`, `hasWeight` and
> `hasMeasurement` are domained on `cargo:CargoItem` and nothing else, so the new
> bridges make `Dimension` *visible* to `equipment` and `consignment` without giving
> either anchor class a path to it. The fix removes "the consumer could not see it" as
> an explanation and leaves "no relationship exists" as a real finding - still gated on
> the versioned MMT-RDM audit in section 7.1, which is now the critical path.
>
> **To re-assess:** regenerate the adopter inventory against repository 1.32.0 or
> later, then redo sections 2, 4 and 6. That is adopter-side work; it cannot be done
> in this repository.

## 1. Scope and decision rule

This report assesses an adopter-generated gap inventory against the current
reference models and official standards. It deliberately contains no client,
source-system, table, column, sample-value, or personal data.

A source field is evidence that an adopter needs to represent a fact. It is not
evidence that:

1. the proposed anchor class owns that fact;
2. the source field name is a standard term;
3. one source row has only one semantic grain; or
4. a new reference-model property is required.

The decision order used here is:

1. reuse an existing term at its existing grain;
2. connect existing standard-backed classes;
3. correct discovery or import closure;
4. add a term only when an exact official standard element supports it;
5. otherwise leave the concept in a client extension or the evidence backlog.

No proposed class or property in this report is approved for implementation.

## 2. Input reconciliation

The Markdown summary and CSV do not describe the same population.

| Population | CSV rows |
|---|---:|
| Proposed strong | 63 |
| Review - same class, other cluster | 112 |
| Review - weak or wrong home | 173 |
| Review - unclassified | 267 |
| **Non-excluded** | **615** |
| Excluded - cross-domain projection | 294 |
| Excluded - audit/pipeline | 120 |
| Excluded - PII | 31 |
| Excluded - vendor slot | 9 |
| **Total** | **1,069** |

The Markdown says 994 rows were reduced to 589. The CSV has 1,069 rows and 454
exclusions, leaving 615. Even the Markdown category table sums to 615
non-excluded rows. This report therefore treats the CSV as the full-list
authority and assesses 615, not 589, rows.

There is a second material mismatch: the Markdown presents equipment capacity
dimensions as part of the strong example, while all six capacity value/base
rows are classified as cross-domain projections in the CSV. They must not be
silently restored to the proposal set. Only exterior equipment dimensions are
in the CSV's strong set.

Before any implementation, the producer should regenerate the Markdown from the
CSV or add a shared run identifier and row-count assertion.

## 3. Current model already available

### 3.1 MMT measurements

`derived-ontologies/MMT/current/cargo/cargo.ttl` already defines:

- `CargoMeasurement` with `measurementType`, `measurementValue`, and
  `measurementUnit`;
- `Weight` with `weightValue`, `weightUnit`, and `weightType`;
- `Dimension` with `lengthValue`, `widthValue`, `heightValue`, and
  `dimensionUnit`;
- `hasMeasurement`, `hasWeight`, and `hasDimension`, currently domained on
  `cargo#CargoItem`.

The logistics convergence analysis already selects MMT, rather than BSP, as the
authority for cargo-context measurements. Adding parallel scalar properties to
`consignment#GoodsItem` would bypass that decision.

The unresolved issue is grain: MMT also defines
`consignment#GoodsItem`, but does not relate it to `cargo#CargoItem`.
Both classes occur in the unit-load-carrier archetype. Their comments are too
general to prove equivalence, containment, or identity. That duplication must
be audited against the actual MMT-RDM association model before adding links.

### 3.2 DCSA call timing

`derived-ontologies/DCSA/current/track-and-trace/events/events.ttl` already
defines:

- `Event.eventDateTime`;
- `Event.eventClassifierCode`;
- `Event.hasTransportCall -> TransportCall`.

The official DCSA Event Domain 3.2.0 confirms this shape:

- `transportPayload` requires `transportEventTypeCode` and `transportCall`;
- `baseEvent` requires one `eventDateTime` and one `eventClassifierCode`;
- transport-event classifiers are ACT, PLN, or EST;
- start/completion/arrival/departure are event type codes, not separate
  properties on `TransportCall`.

The schema also defines `milesToDestinationPort` on an operations event as
remaining nautical miles. It is not a generic estimated route-distance property.

### 3.3 BSP party finance

`derived-ontologies/BSP/current/financial/financial.ttl` already defines:

- `BankAccount`, `hasBankAccount`, `iban`, `bic`, and `accountNumber`;
- `PaymentTerms`, `hasPartyPaymentTerms`, and `netDays`;
- `creditLimit` and `creditLimitCurrency`.

These are financial concepts whose domains or ranges reference `party#TradeParty`.
Their absence from a party-only discovery closure is not evidence for duplicate
properties in `BSP/party`.

One existing detail needs audit before further reuse: UN/CEFACT places an IBAN
on creditor/debtor/payment financial accounts, but defines BIC as the identity
of a financial institution. The current BSP `bic` property is domained directly
on `BankAccount`. That flattening must not be propagated to `TradeParty`.

## 4. Strong-set assessment

### 4.1 Row-level disposition

The 63 strong rows resolve as follows.

| Disposition | Rows | Meaning |
|---|---:|---|
| Reuse or discovery correction | 5 | Existing BSP finance concepts cover the semantic fact |
| Wrong grain | 18 | Call timestamps/distance and observed temperatures belong on events, movements, or observations |
| Source storage representation | 18 | Base-value duplicates are physical storage mechanics, not ontology terms |
| Qualified-measurement candidate | 21 | A standard measurement shape may cover the fact, subject to exact association/qualifier evidence |
| Client operational status | 1 | No cited BSP/UN/CEFACT element backs a party-wide blocked flag |
| **Total** | **63** | |

This classification is conservative. A qualified-measurement candidate is not an
approved new property.

### 4.2 `mmt-consignment:GoodsItem`

**Finding:** do not add the proposed scalar fields.

The 34 rows contain 15 base-storage duplicates and 19 semantic candidates.
UN/CEFACT supports measured weights, volumes, loading length, and spatial
dimensions. The current MMT cargo module already represents the value/unit
shape. The missing decision is how a consignment goods item reaches that shape.

Recommended future investigation:

1. Obtain the versioned MMT-RDM schema/model used to justify MMT 2.2.0.
2. Identify the exact standard entities represented by Kairos
   `consignment#GoodsItem`, `consignment#ConsignmentItem`, and
   `cargo#CargoItem`.
3. If `GoodsItem` is standard-backed as a measurable item, add narrowly scoped
   object properties from it to the existing MMT `Weight`, `Dimension`, and
   `CargoMeasurement` classes.
4. If `GoodsItem` and `CargoItem` duplicate one standard entity, plan a major
   rationalization rather than adding a bridge that canonizes the duplication.

Do not use `owl:equivalentClass` without exact identity evidence. Do not broaden
`cargo:hasDimension` or `cargo:hasMeasurement` by changing their domains:
re-domaining an existing property changes inference for every adopter.

#### Ordered versus actual

Ordered and actual values are different lifecycle observations, not two sets of
physical attributes on durable goods. No exact MMT term was found in the current
module citations for this qualifier. A future implementation must either cite
an MMT status/observation association or leave the distinction in the client
model. A free-form `measurementType` value is not sufficient governance.

#### Temperature

Required temperature can plausibly reuse `cargo#HandlingInstructions`; observed
pickup and delivery temperatures are event observations and should not become
attributes of `GoodsItem`. A minimum/maximum required range needs a standard
temperature-range or measurement association before it can be added.

### 4.3 `mmt-equipment:TransportEquipment`

**Finding:** exterior dimensions are a credible relationship gap, not six
datatype-property gaps.

The seven rows reduce to three exterior axes plus one unit; three rows are base
storage duplicates. UN/CEFACT exposes measured length, width, and height terms,
an equipment size/type characteristic code, gross goods weight/volume on
transport equipment, and loading length. The current MMT `Dimension` value
object already has the required three-axis-plus-unit shape.

The least duplicative future option is an equipment-scoped object property
ranging to `mmt-cargo:Dimension`, with an explicit import and an exact
UN/CEFACT/MMT citation. It must be a new equipment property; making it a
subproperty of `cargo:hasDimension` would inherit that property's `CargoItem`
domain and incorrectly infer that equipment is cargo.

Before implementation, verify that the selected MMT version associates a
spatial dimension with logistics transport equipment and identify how it
qualifies exterior versus interior/capacity dimensions. Do not invent
`EXTERIOR`/`CAPACITY` codes from adopter column names.

The capacity rows remain excluded under the authoritative CSV. Reconsidering
them requires a separate projection-grain review, not expansion of this strong
case.

### 4.4 `dcsa-transport-call:TransportCall`

**Finding:** add no direct temporal or distance properties.

The DCSA standard models a transport event containing a transport call. One
event time is qualified by classifier and event type. Consequently:

- planned/actual start and end become multiple event instances;
- local timestamp variants are serialization/display choices;
- an unqualified start/end timestamp loses classifier semantics;
- a requested date is not a DCSA TransportEvent classifier in Event Domain
  3.2.0 and needs a separately cited schedule/booking concept;
- generic estimated distance is not DCSA `milesToDestinationPort`.

The current DCSA ontology already has the correct direction. A later change
should focus on discovery guidance for dual-grain source records or on missing
event types, only if the official schema backs them. Importing the events module
into the route/schedule domain merely to expose its properties would blur domain
ownership and is not recommended by default.

### 4.5 `bsp-party:TradeParty`

**Finding:** reuse financial entities; add no party scalars.

| Fact | Future mapping decision |
|---|---|
| Credit limit | Existing `financial#creditLimit`, paired with `creditLimitCurrency`; reassess whether relationship scope is needed |
| Currency | Use only as the qualifier of a specific monetary amount; never map a generic currency field without context |
| Payment term in days | `financial#hasPartyPaymentTerms -> PaymentTerms.netDays` |
| IBAN | `financial#hasBankAccount -> BankAccount.iban` |
| BIC | Audit account-to-financial-institution modelling; do not copy BIC onto party |
| Blocked status | Client/customer-management status unless an exact standard element is produced |

The appropriate adopter mapping can instantiate party, payment-terms, account,
and institution grains from one source row. The reference model should not
flatten those entities because a source table did.

## 5. Similar cases

### 5.1 Measurements with fixed units in comments

Several current MMT properties carry a decimal while fixing the unit only in
prose:

- equipment tare and maximum gross weight;
- consignment gross/net weight and volume;
- reefer target/minimum/maximum temperature;
- cargo handling temperature;
- dangerous-goods temperature values.

These are analogous to the reported gaps, but not automatically defects. A
property whose semantics normatively fixes one unit differs from a general
measurement. The later audit should check the official schema datatype:

- if the standard uses `Measure` plus `unitCode`, the ontology currently loses
  information and should migrate toward a qualified value;
- if the standard normatively fixes the unit, the scalar is complete and should
  remain.

This distinction is why a validator based only on names such as `*Unit` or
`*Value` would produce false results.

### 5.2 Dimension homonyms

The inventory includes four different meanings:

1. physical spatial dimensions;
2. loading length/capacity measures;
3. accounting classification dimensions;
4. report-analysis dimensions.

Only the first two are measurements. Accounting and report dimensions must not
range to MMT/BSP `Dimension`, and numbered ERP classification slots must not be
standardized as physical axes.

### 5.3 Exact terms hidden elsewhere

An exact local-name scan found 24 non-excluded rows whose proposed property name
already exists in another current module. This is a candidate signal, not proof
of equivalence: domains and ranges still need checking. It nevertheless proves
that “no property on the anchor class” must not be treated as “no term in the
reference-model closure.”

### 5.4 Empty anchors

Thirty-five non-excluded rows have no anchor class. They cannot support an
ontology addition. Anchor discovery must be corrected before semantic gap
assessment.

## 6. Full-list triage

All 615 non-excluded rows are assigned to a conservative next-action bucket.

| Bucket | Rows | Next action |
|---|---:|---|
| Existing/reuse candidate | 28 | Check domain/range and expose or map the existing term |
| Wrong grain/home | 184 | Re-anchor to event, account, report, movement, or another entity |
| Source storage representation | 18 | Exclude from semantic vocabulary |
| Standards-backed shape candidate | 21 | Perform exact MMT association/qualifier audit |
| Same-anchor but unproven/client-specific | 109 | Require independent adopter and standard evidence |
| Insufficient evidence/unclassified | 255 | Keep in backlog; no model change |
| **Total** | **615** | |

Derivation:

- the 63 strong rows use the detailed disposition in section 4;
- the 173 rows already labelled weak/wrong-home remain wrong-home except seven
  exact existing-term candidates;
- the 112 same-class remainder contributes four exact existing-term candidates
  and 108 unproven/client-specific rows;
- the 267 unclassified rows contribute 12 exact existing-term candidates and
  255 insufficient-evidence rows.

The 454 excluded rows remain excluded. This report does not reopen projection,
pipeline, PII, or vendor-slot findings.

## 7. Proposed future change set

No files in this section should change without a second approval.

### 7.1 Evidence first

Add a version-specific MMT audit under `.docs/refmodels/MMT/` that records the
official schema paths for every affected class, association, qualifier, and
measure. Replace generic module-level MMT citations with exact `rdfs:seeAlso`
links on changed terms.

### 7.2 Conditional MMT ontology work

If the audit confirms the associations:

- update `derived-ontologies/MMT/current/consignment/consignment.ttl` with
  narrowly scoped relationships from the correct goods grain to existing MMT
  measurement objects;
- update `derived-ontologies/MMT/current/equipment/equipment.ttl` with an
  equipment-scoped relationship to the existing MMT `Dimension` object;
- update `derived-ontologies/MMT/current/cargo/cargo.ttl` only for an exact
  missing standard qualifier, not for adopter-specific ordered/actual codes;
- update `derived-ontologies/MMT/current/mmt.ttl` imports only where direct
  module closure requires them.

Do not re-domain existing properties. Do not add base-value, local-time, or
source-column-shaped datatype properties.

### 7.3 Discovery guidance

Document that one source record may instantiate multiple grains:

- `TradeParty`, `PaymentTerms`, `BankAccount`, and financial institution;
- `TransportCall` plus one or more classified events;
- goods/cargo plus qualified measurements.

Use an existing consumed contract surface if machine-readable guidance is
needed. Do not add a new YAML vocabulary without a toolkit reader.

### 7.4 Future consistency validator

Prefer an RDF-aware, explicitly scoped measurement-shape registry over suffix
matching. The validator should check registered shapes such as:

- numeric value plus unit;
- dimension axes plus unit;
- monetary amount plus currency;
- qualifier/type not being the only payload.

It should distinguish normatively fixed-unit scalars and non-physical uses of
“dimension.” Likely implementation surfaces are
`scripts/validate_pattern_conformance.py` or a dedicated validator plus focused
tests and `.github/workflows/validate.yml`.

### 7.5 Versioning impact

Any later MMT ontology addition requires:

1. `python scripts/archive_version.py MMT`;
2. an MMT minor bump for additive relationships/terms, or a major bump if
   duplicate goods/cargo classes are rationalized;
3. synchronized `owl:versionInfo`;
4. README and `CHANGELOG.md` updates;
5. regenerated logistics inventory if pack evidence changes;
6. the full repository validation gate.

DCSA and BSP need no content bump for the findings assessed here unless a
separate audit changes their existing models.

## 8. Explicit do-not-change decisions

- Do not add direct planned/actual/requested/start/end properties to
  `TransportCall`.
- Do not add IBAN, BIC, payment-term, or generic currency scalars to
  `TradeParty`.
- Do not add source base-value or local-time representation fields.
- Do not represent accounting/report dimensions with physical `Dimension`.
- Do not restore equipment capacity rows from the stale Markdown example while
  the authoritative CSV excludes them.
- Do not equate MMT `GoodsItem` and `CargoItem` without versioned standard
  evidence.
- Do not create a machine-readable mapping file without a consumer.

## 9. Official references

- UN/CEFACT Reference Data Models:
  <https://unece.org/trade/uncefact/rdm>
- UN/CEFACT `ConsignmentItem`:
  <https://vocabulary.uncefact.org/ConsignmentItem>
- UN/CEFACT `LogisticsTransportEquipment`:
  <https://vocabulary.uncefact.org/LogisticsTransportEquipment>
- UN/CEFACT measured length, width, height, and loading length:
  <https://vocabulary.uncefact.org/linearUnitLengthMeasure>,
  <https://vocabulary.uncefact.org/linearUnitWidthMeasure>,
  <https://vocabulary.uncefact.org/linearUnitHeightMeasure>,
  <https://vocabulary.uncefact.org/linearUnitLoadingLengthMeasure>
- UN/CEFACT equipment goods weight and volume:
  <https://vocabulary.uncefact.org/grossGoodsWeightMeasure>,
  <https://vocabulary.uncefact.org/grossGoodsVolumeMeasure>
- UN/CEFACT `PaymentTerms`, payment financial account, IBAN, and BIC:
  <https://vocabulary.uncefact.org/PaymentTerms>,
  <https://vocabulary.uncefact.org/PaymentFinancialAccount>,
  <https://vocabulary.uncefact.org/iBANId>,
  <https://vocabulary.uncefact.org/bICId>
- DCSA Event Domain 3.2.0, pinned source:
  <https://github.com/dcsaorg/DCSA-OpenAPI/blob/e4ec33374628537a7b70c3e1a8a22c12dd517a74/domain/event/event_domain_v3.2.0.yaml>
- DCSA OVS Domain 1.2.0 timestamp shape, pinned source:
  <https://github.com/dcsaorg/DCSA-OpenAPI/blob/591d4f23d0044faf50db5ebecb8422abc9f2b31d/domain/ovs/ovs_domain_v1.2.0.yaml>

