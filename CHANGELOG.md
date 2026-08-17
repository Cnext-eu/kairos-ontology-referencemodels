# Changelog

All notable changes to the Kairos Reference Models will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.33.0] - 2026-08-17

Blueprint-layer companion to 1.32.0. That release fixed the graph layer — a module not
importing what it asserts `rdfs:domain` against. This one fixes the routing layer: a
class can be perfectly modelled, correctly imported by *a* domain, and still be
unreachable from the domain that needs it, because `data-domains.yaml` scopes imports
per domain and nothing checked the result against what the archetypes say a hub requires.

### Fixed

- **`mmt/cargo` measurement classes unreachable from the domains that carry the columns**
  (#98). `Dimension`, `Weight` and `CargoMeasurement` were routed to `cargo` and `roro`
  only, so the `equipment` domain (trailer dimensions) and `consignment` domain (goods
  measures) could not see them at all. Four `cross_domain_relationships` bridges added.

  Bridges rather than imports: a bridge says "may reference, does not own", whereas
  importing `mmt/cargo` into `equipment` reads as co-ownership and trips the consumer's
  cross-domain duplicate check. It is also the surgical option — a bridge exposes exactly
  its `range_class_uri`, so the four entries widen each domain's pool by one class each,
  not by a module.

  The pack's own overlap register had already resolved `Dimension` to `MMT/Cargo`
  deliberately. The decision was made and recorded, then not routed to the domains that
  consume it.

- **Four modules routed to no data domain at all**, found by the new gates:
  - **`mmt/locations`** — 5 tier-required archetype concepts unreachable, while every
    other vendor's locations module was routed. Now in `reference-data`.
  - **`dcsa/party`** — 4 tier-required concepts unreachable, while BSP, MMT, IMO and RAIL
    party modules were all routed. Now in `party`.
  - **`mmt/transport-means`** — 11 concepts unreachable including `Vessel` and
    `RoadVehicle`, both tier-required. The module spans every mode, so it is routed to
    `vessel-maritime`, `equipment` and `intermodal` along mode lines rather than assigned
    one owner. Precedent: `mmt/cargo` is imported by both `cargo` and `roro`.
  - **`tic/party`** — 9 terms, and the only one found by the *module-level* check rather
    than the archetype check, because no archetype core concept names a `tic/party` class.
    Now in `party`.

### Added

- **`validate_archetypes.py` check 8 — concept/domain reachability.** Every archetype core
  concept must be reachable from at least one data domain, by module import or declared
  bridge. Blocking at `tier: required`, advisory below — `Dimension` is
  `tier: recommended`, so a required-only gate would have missed the defect that prompted
  the check.

  `--list-single-domain` enumerates concepts reachable from exactly one domain. The issue
  proposed flagging those as the cheap first step, but measured against the shipped
  archetypes it fires on 348 of 416: belonging to one domain is the normal case for an
  owned class, and per-concept warnings would bury the real findings. Reported as one
  summary line instead.

- **`test_every_term_declaring_module_reaches_a_data_domain`.** Worth being explicit that
  this was a *granularity* gap, not a missing test.
  `test_every_include_reaches_data_domains` was already written for exactly this failure
  (the RAIL regression), but it checks `manifest.yaml` includes, which are vendor-level
  (`ont/mmt#`), and passes on a prefix match against any routed module. That prefix match
  is required for FIBO, where the manifest names module *groups* — and it is what made
  per-module gaps invisible: MMT counted as reaching data-domains on the strength of
  `mmt/cargo` alone.

  The new check is scoped to each pack's own accelerator import closure and auto-exempts
  pure aggregators, so it needs no allowlist entry per vendor root.

- **Four integration-layer bridge properties** in `supply-chain`:
  `hasEquipmentDimension`, `hasGoodsDimension`, `hasGoodsWeight`, `hasGoodsMeasurement`.
  These are Kairos routing declarations and deliberately **not** a claim that UN/CEFACT
  associates a spatial dimension with logistics transport equipment or with a consignment
  goods item. That remains open pending a versioned MMT-RDM audit; until it lands, no
  equivalent property may be added to `mmt/equipment` or `mmt/consignment`, and
  `cargo:hasDimension` must not be re-domained — doing so would infer that equipment is
  cargo. The names carry no exterior/interior or ordered/actual qualifier for the same
  reason.

- `tests/test_validate_archetypes.py` (13 tests, none previously), a bridge
  class-endpoint check in `test_model_registration.py` — previously only the bridge
  *property*'s module was verified as catalogued — and two `CONTRIBUTING.md` runbooks:
  adding an industry model, and changing a data domain.

### Known gaps

- **`ont/mmt` declares 33 dangerous-goods terms in the vendor root namespace, which no
  data domain imports**, so none is reachable from any client hub. Four are archetype
  core concepts and the new gate warns on all four. Recorded in `UNROUTED_TRACKED_GAP`
  with a staleness test that fails once it is fixed. The fix — extracting them into an
  `mmt/dangerous-goods` leaf module — is a breaking MMT major and therefore its own
  release.

## [1.32.0] - 2026-08-17

### Fixed

- **50 orphaned `rdfs:domain` assertions across 13 modules in 4 vendor trees** (#97). A
  module asserted `rdfs:domain` against a class it neither declared nor `owl:imports`, so
  that class was never typed in the module's own graph. 15 `owl:imports` added; no term
  added, renamed or re-domained.

  Measured on the `bsp/financial` entry point — which the `financial` data domain loads:
  `party:TradeParty` and `commercial:CommercialTransaction` were **not `owl:Class`**
  there before the fix, so a hub working in that domain could not offer either as an
  anchor. Both are typed now, and `TradeParty` carries 13 properties in that closure
  rather than 4.

  Note for anyone reading #97: its worked example overstates the defect and the issue has
  been annotated accordingly. From the vendor root — the closure a hub actually loads,
  since the accelerator imports `ont/bsp` — `creditLimit`, `creditLimitCurrency`,
  `hasBankAccount` and `hasPartyPaymentTerms` all resolved on `TradeParty` *before* this
  change. Their absence from a `bsp/party`-only closure is correct behaviour, not a
  defect: they are financial-domain facts, exactly as the standards assessment concluded.

- **The BSP module graph is now acyclic.** `:relatedToShipment` moves from `bsp/commercial`
  to `bsp/financial`, where its `rdfs:domain fin:Invoice` says it belongs; the old IRI
  stays as an `owl:deprecated` stub for one major.

  This is not cosmetic. That single edge closed a `commercial → financial → commercial`
  cycle, and while a cycle is harmless to the graph — both this repo's loader and the
  consumer's guard on visited paths — it made all four BSP modules mutually reachable.
  Since the consuming toolkit derives each data domain's alignment pool from the
  *transitive* `owl:imports` closure, any domain importing one BSP module was offered all
  four: 352 classes of widening from one misplaced property.

### Added

- **`validate_structure.py` check 10 — import closure.** Blocking for `rdfs:domain`,
  advisory for `rdfs:range`, and blocking on a leaf module importing its vendor root.
  Union domains (`rdfs:domain [ owl:unionOf ( … ) ]`) are checked; a simple
  `rdfs:domain <prefixed-name>` regex would skip every one of them silently.

  **The domain/range asymmetry is deliberate and was measured.** Requiring imports for
  ranges too meant 70 imports rather than 15, and pushed the classes offered across the
  logistics data domains from 729 to 1805 (2.48×) — handing `compliance` 92 classes where
  it had 5, most from modules it has no relationship with. Domain-only costs 1.19×, and
  that widening is real dependency: `financial` sees `CommercialTransaction` because its
  properties are domained on it. The "cross-domain references use untyped ranges"
  convention in the vendor READMEs exists to keep those closures narrow; it is
  load-bearing, not stale, and the 54 range warnings should not be bulk-fixed.

- **`tests/test_import_closure.py`** — 17 tests, none previously covering this validator.
  Includes negative controls for both blocking rules, and pins the asymmetry: an
  unimported range warns and does not fail.

- **A cross-module reference section in `CONTRIBUTING.md`** covering the import rule, why
  range is treated differently, and why a cycle is worth avoiding even though the gate
  tolerates it.

### Changed

- `validate_structure.py` property completeness now exempts properties marked
  `owl:deprecated true`. A retiring stub that kept its foreign `rdfs:domain` would also
  keep the `owl:imports` edge it exists to remove.
- MMT, BSP and DCSA READMEs: the "no cross-imports between domain modules" principle was
  already false in the shipped files (`bsp/party` has imported `bsp/reference-data` since
  1.5.0). Restated as the rule the gate now enforces, with the untyped-range convention
  kept and its rationale written down.

## [1.31.0] - 2026-08-17

### Added

- **`accelerator-packs/<pack>/client-hub-blueprint/entity-projections.yaml`** — a new pack-scoped contract surface, beside `data-domains.yaml`, declaring how a group of source columns is recognised as a denormalised projection of another entity: part kinds, role qualifiers, context tokens, target class candidates and relationship naming.

  This exists because the consuming toolkit had compiled that vocabulary into itself (toolkit DD-188). Its role list was an e-commerce one — `billing`, `shipping`, `mailing`, `home`, `work` — with no `pickup`, `origin` or `destination`, so on a logistics hub `delivery_location_city` was recognised as an address part and `pickup_location_city` was not. Vocabulary of that kind is pack knowledge, not engine knowledge.

  `logistics` ships one projection, `postal-address`, targeting `bsp/reference-data#Address` with 20 role qualifiers including the nine freight roles the toolkit was missing.

- **`accelerator-packs/_schema/entity-projections.schema.json`** — authored once beside `data-domains.schema.json`, since the document is pack-scoped but its shape is shared. `additionalProperties: false` throughout, so a typo fails validation rather than being silently ignored by a loader. Enforced by `scripts/validate_structure.py`, which also applies three coherence checks JSON Schema cannot express — duplicate projection ids, duplicate part kinds within a projection, and configurations that validate structurally but can never detect anything.

### Notes

- **`financial-services` deliberately ships no such file.** Nothing in that pack evidences which role qualifiers its columns carry, and authoring them from intuition about banking would relocate the defect rather than fix it. A pack without the file yields no candidates at all — there is no built-in fallback — and a test pins that absence as intentional.
- `house_number` carries no bare `tokens`, only the compact forms `housenumber`/`houseno`: the bare token `house` also matches unrelated business terms such as `clearingHouse`. The schema therefore allows an empty `tokens` list, while an `anyOf` still requires every part kind to be matchable by `tokens` or `compact` — a kind matchable by neither can never fire and would silently lower the effective part count.

## [1.30.0] - 2026-08-17

Three gaps found by adopting these modules on a real client hub (CLdN, logistics
pack), each filed as an issue with its adopter evidence before being fixed. All
changes are additive; no existing term was re-domained or removed.

### Added

- **`IMO/vessel-registry` `:capacityValue`** (#90). `:VesselCapacity` carried
  `:capacityUnit` and `:capacityType` but no measured value, so the class could
  state *"a TEU capacity measured in TEU"* but not how many — while
  `:GrossTonnage` beside it has the full value/unit/convention triad. Eight
  Ro-Ro capacity columns on the adopting hub had no home. `:hasCapacity` already
  links `:Vessel` to the value object, so no new link was required.
  IMO 1.2.0 → **1.3.0**.

- **`BSP/financial` credit- and debit-note attributes** (#89). `:CreditNote` and
  `:DebitNote` were bare classes — no `rdfs:subClassOf`, zero properties — while
  `:Invoice` carried 15. Their attributes could not be expressed at all: the
  invoice properties are `rdfs:domain :Invoice`, so reusing them entails
  `CreditNote ⊑ Invoice`, contradicting the module's own decision to model the
  notes as siblings rather than subclasses. Adds six header properties on each,
  `:CreditNoteLine`, `:DebitNoteLine`, `:hasCreditNoteLine`, `:hasDebitNoteLine`
  and `:appliesToInvoice` (union domain over both note types).

- **`BSP/financial` `:BillingDocumentLine`** (#91). `:InvoiceLine` carried only
  `:lineNumber` and `:taxRate` — no amount, quantity, unit price or description
  — so a line item could not state what it charges or how much. This is the same
  defect class as #90, a line object with qualifiers but no measure, and
  mirroring `:InvoiceLine` faithfully had propagated it into the new
  `:CreditNoteLine`. Introduces a shared parent carrying `:lineAmount`,
  `:lineQuantity`, `:lineQuantityUnit`, `:lineUnitPrice`, `:lineTaxAmount` and
  `:lineDescription`, with `:InvoiceLine`, `:CreditNoteLine` and
  `:DebitNoteLine` as subclasses.

  `:lineQuantityUnit` is included deliberately: UN/CEFACT `BilledQuantity`
  carries a UN/ECE Recommendation 20 `unitCode`, and a bare quantity on a
  freight line is ambiguous between pallets, tonnes, TEU and lane metres —
  omitting it would repeat #90 in the other direction.

  BSP 2.3.0 → **2.4.0** (covers both #89 and #91).

### Notes

- `:Invoice` is deliberately untouched: still exactly its original 15 properties
  and no superclass. `financial.ttl` is **+256 / −0**, pure insertions.
- **Not hoisted:** `:lineNumber` and `:taxRate` remain on the individual line
  classes rather than moving to `:BillingDocumentLine`, because widening them is
  re-domaining an existing property. The parent therefore owns the measures but
  not the numbering — an intentional asymmetry, revisitable in a major.
- No `dueDate` equivalent on either note: `due` is a banned token in the
  temporal-quartet pattern and `:dueDate` survives only via a named exemption,
  so minting one for the notes would require a new exemption entry.
- Archived `BSP/archive/2.3.0/` and `IMO/archive/1.2.0/` from the pre-change
  content before bumping.
- Verified: `check_all.py` 7/7, tier-2 contract and bundle conformance 9 passed,
  `validate_structure.py` all checks pass, `version_manager.py check` consistent
  across 76 version strings.

## [1.29.1] - 2026-08-16

### Added
- **Three missing module imports in data-domains.yaml** (accelerator-pack
  contract change, no ontology content change):
  - `rail/shared-kernel` → `intermodal` domain. Fixes dangling references:
    `rail/train-running` (already imported) uses `sk:OperationalTrainIdentifier`
    and `sk:RailLocationIdentifier` in its property ranges, but the shared-kernel
    module that defines them was never imported. Zero overlap with existing imports.
  - `tic/reefer-monitoring` → `terminal-operations` domain. Adds terminal-side
    reefer management (ReeferMonitoring, ReeferRack, ReeferSlot + 21 properties).
    Equipment-side reefer settings remain in `mmt/equipment#ReeferContainer`
    (equipment domain) — different grain, no overlap.
  - `dcsa/container-operations` → `equipment` domain. Adds container lifecycle
    operations (ContainerJourney, ContainerOperationalStatus, ContainerStuffing,
    ContainerStripping, LiftOnLiftOff). Overlap note: LiftOnLiftOff overlaps
    conceptually with `tic/handling-operations#LiftMove`; resolution documented
    in the import note (container-operations owns lifecycle grain, handling-
    operations owns terminal-move grain).

### Audit
- Challenged all 11 catalog modules missing from data-domains.yaml. 5 skipped
  due to excessive overlap (dcsa/party, mmt/locations, mmt/transport-means,
  tic/party, IATA code-lists). 3 wrapper ontologies correctly excluded
  (dcsa/equipment-journey, dcsa/track-and-trace, dcsa/shared-kernel — zero own
  classes).

## [1.29.0] - 2026-08-14

### Added
- **New SupplyChain bridge properties for unanchored-table fix (SupplyChain 1.2.0 → 1.3.0).**
  Two new cross-domain object properties to address the 9 unanchored tables
  identified in client hub mapping analysis (306 columns across 9 tables):
  - `callsAtTransportCall` — links MMT `TransportMovement` → DCSA `TransportCall`.
    Fixes 237 of 306 unanchored columns (77%): the consignment domain's `stops`/
    `stops_table` tables need TransportCall, which lives in `dcsa/transport-call`
    (owned by route-schedule). The existing `consignment-to-schedule` bridge only
    reaches `ServiceLoop` (planned rotation grain), not `TransportCall` (per-stop
    arrival/departure grain). This bridge closes that gap without changing import
    boundaries.
  - `hasVesselEvent` — links IMO `Vessel` → DCSA `Event`, as `owl:inverseOf`
    `eventRelatesToVessel`. Fixes 10 columns: vessel-maritime domain's
    `fleet_competition` table needs `DischargedFromVesselEvent` from
    `dcsa/track-and-trace/events`, but the existing bridge was one-directional
    (events → vessel). The inverse enables vessel-maritime to reach event
    classes without importing the events module.
  - Registered both as new cross-domain relationships in
    `accelerator-packs/logistics/client-hub-blueprint/data-domains.yaml`.
  - Added `dcsa/transport-call` to SupplyChain's `owl:imports` closure.

### Deferred
- Tables 3 (`resource_calendar_events`, 25 cols), 4 (`empty-units-1b-dropoff`,
  16 cols), 7 (`3-drop-off-details`, 6 cols): check enrichment coverage after
  hub upgrade before deciding whether bridges are needed.
- Tables 6 (`haulier-driver-keys`, 8 cols), 8 (`equipmentcode_fix`, 2 cols),
  9 (`__Stappenplan`, 2 cols): NOT reference model gaps — wrong anchor class,
  missing class, or misclassified table. Client extension or new class outside
  this scope.

## [1.28.1] - 2026-08-16

### Fixed
- **Re-tagged release with squashed merge content.** The v1.28.0 tag was
  created on a pre-squash-merge commit, so the release workflow ran against
  stale pack docs and failed the `generate_pack_docs.py --check` gate —
  no wheel artifact was published. v1.28.1 is tagged on the actual merge
  commit (be7fab8) which includes all post-merge fixes: toolkit pin update
  to 5.3.0, regenerated pack docs, and temporal-quartet pattern conformance
  fixes (IMO `preArrivalETA → estimatedArrival`, MMT
  `actualArrivalDateTime → actualArrival`, `actualDepartureDateTime →
  actualDeparture`).
- **Removed duplicate CHANGELOG header** (line 169) introduced during
  prior session's PowerShell string manipulation.

## [1.28.0] - 2026-09-18

### Added
- **Enriched IMO thin-stub classes across all 9 domain modules (IMO 1.1.0 → 1.2.0).**
  Systematic enrichment of classes that had zero or very few own properties
  despite being referenced by other classes or the ontology structure. All new
  properties are backed by cited IMO conventions and regulations: SOLAS, MARPOL
  (Annexes I, II, V, VI), ISM Code, ISPS Code, MLC 2006, STCW Convention, FAL
  Convention (Forms 1-7), IMDG Code (including EmS Guide), BWM Convention, IHR
  (2005), UNCLOS, IMO Resolution A.1117(30), IMO Resolution A.739(18), IMO
  Resolution A.893(21), 1969 Tonnage Convention, ITU Radio Regulations, and the
  IMO Compendium data set. Archived previous version 1.1.0 before enrichment.

  **certificates-surveys.ttl** (16 new datatype properties):
  - DocumentOfCompliance: `docCompanyAddress`, `docVerificationDate`,
    `docShipTypeScope`, `docValidityPeriod`, `docReferenceNumber` — ISM Code
    DOC certificate metadata
  - InternationalShipSecurityCertificate: `isscShipName`, `isscFlagState`,
    `isscSecurityPlanReference`, `isscVerificationDate`,
    `isscInterimCertificate` — ISPS Code ISSC data
  - SafetyManagementCertificate: `smcImoNumber`, `smcCompanyName`,
    `smcIntermediateVerificationDate` — ISM Code SMC metadata
  - MaritimeLabourCertificate: `mlcInspectionDate`,
    `mlcInspectionAreasCovered`, `mlcIntermediateInspectionDate` — MLC 2006
    certificate data

  **crew-seafarer.ttl** (8 new datatype properties):
  - CertificateOfProficiency: `copCertificateNumber`, `copIssueDate`,
    `copExpiryDate`, `copTrainingProvider` — STCW Convention CoP metadata
  - CrewList: `crewListFlagState`, `crewListVoyageNumber` — FAL Convention
    Form 5 crew list context
  - PassengerList: `passengerListFlagState`, `passengerListVoyageNumber` — FAL
    Convention Form 6 passenger list context

  **dangerous-goods.ttl** (13 new datatype properties):
  - HazardClass: `hazardClassName`, `hazardClassDivision` — IMDG Code class
    and division
  - UNNumber: `unProperShippingName` — UN Recommendations proper shipping name
  - PackingGroup: `packingGroupDangerLevel` — IMDG Code / UN Recommendations
    packing group danger level
  - FlashPoint: `flashPointTestMethod`, `flashPointUnit` — IMDG Code flash
    point measurement data
  - EmergencySchedule: `emsScheduleTitle` — IMDG Code EmS Guide schedule title
  - SegregationRule: `segregationTerm`, `segregationDescription` — IMDG Code
    segregation table
  - StowageCategory: `stowageCategoryCode`, `stowageCategoryDescription` — IMDG
    Code stowage category
  - EmergencyContact: `contactOrganization`, `contactAvailable24h` — IMDG Code
    emergency contact context

  **environmental.ttl** (11 new datatype properties):
  - BallastWaterManagementPlan: `bwmsD2ComplianceStandard`,
    `bwmsExchangeMethod`, `bwmsApprovalAuthority` — BWM Convention treatment
    system approval
  - ShipboardOilPollutionEmergencyPlan: `sopepReportingProcedures`,
    `sopepContactAuthorities`, `sopepExercisesDate` — MARPOL Annex I SOPEP
    metadata
  - GarbageManagementPlan: `gmpWasteCategories`, `gmpDesignatedOfficer`,
    `gmpPlacardPosted` — MARPOL Annex V garbage plan metadata
  - NoxiousLiquidSubstance: `nlsIbcShipType`, `nlsPollutionCategory` — MARPOL
    Annex II substance classification

  **locations.ttl** (17 new datatype properties):
  - Anchorage: `anchorageType`, `anchorageMaxVesselSize`,
    `anchorageHoldingGround` — IMO port state anchorage data
  - VTSZone: `vtsReportingRequirements`, `vtsServiceArea` — SOLAS V/12 VTS
    zone metadata
  - PilotBoardingPlace: `pilotBoardingProcedure`, `pilotBoardingTime`,
    `pilotLadderRequired` — SOLAS V/10 pilot boarding data
  - TrafficSeparationScheme: `tssSchemeType`, `tssTrafficLaneDirection`,
    `tssSeparationZoneWidth` — COLREGS Rule 10 TSS details
  - EmissionControlArea: `ecaSulphurLimit`, `ecaApplicableAnnex` — MARPOL
    Annex VI ECA limits
  - MARPOLSpecialArea: `specialAreaDischargeRestrictions`,
    `specialAreaEffectiveDate` — MARPOL special area metadata
  - PortReceptionFacility: `prfFacilityCapacity`, `prfNotificationRequired` —
    MARPOL Annex V/VI reception facility data

  **maritime-security.ttl** (4 new datatype properties):
  - ShipSecurityPlan: `sspReviewDate`, `sspSecurityMeasures` — ISPS Code SSP
    metadata
  - PortFacilitySecurityPlan: `pfspReviewDate`, `pfspSecurityMeasures` — ISPS
    Code PFSP metadata

  **party.ttl** (30 new datatype properties):
  - FlagAuthority: `flagAuthorityName`, `flagAuthorityRegistry` — UNCLOS flag
    state registration
  - PortAuthority: `portAuthorityJurisdiction`, `portAuthorityJurisdictionType`
  - ClassificationSociety: `classSocietyIacsMember`, `classSocietyCode` — SOLAS
    II-1/3-1 recognized organization data
  - MasterOfVessel: `masterCoCGrade`, `masterIssuingCountry` — STCW Certificate
    of Competency metadata
  - ShipOwner: `shipOwnerRegistry`, `shipOwnerRegistrationDate` — commercial
    registration
  - ShipManager: `shipManagerIsmDocRef`, `shipManagerIsmDocCompany` — ISM Code
    ship management agreement
  - ShipOperator: `shipOperatorType`, `shipOperatorCharterType` — ship
    operating agreement
  - MaritimeAgent: `agentLicenseNumber`, `agentServiceType` — commercial agent
    licensing
  - PilotService: `pilotServiceArea`, `pilotServiceCompulsory` — SOLAS V
    pilotage requirements
  - TowageProvider: `towageProviderPort`, `towageProviderFleetSize` —
    commercial towage provider data
  - CompanySecurityOfficer: `csoContactDetails`, `csoDesignationDate` — ISPS
    Code CSO metadata
  - ShipSecurityOfficer: `ssoCertNumber`, `ssoDesignationDate` — ISPS Code SSO
    metadata
  - PortFacilitySecurityOfficer: `pfsoContactDetails`, `pfsoDesignationDate` —
    ISPS Code PFSO metadata
  - PortStateControlOfficer: `pscMoURegion`, `pscInspectorId` — Paris MOU
    inspector identification

  **port-call.ttl** (24 new datatype properties):
  - BerthStay: `berthStayPurpose`, `berthStaySequence` — berth stay context
  - SeaLeg: `seaLegDeparturePort`, `seaLegArrivalPort`, `seaLegDistance` — FAL
    Convention sea leg data
  - FALForm: `falFormSubmissionMethod`, `falFormStatus` — FAL Convention form
    submission metadata
  - PortCallStatus: `statusCode`, `statusDescription` — IMO Compendium Port Call
    Status code list
  - TowageRequest: `towageType`, `towageTugCount` — towage request details
  - BunkeringOperation: `bunkerFuelType`, `bunkerSupplierName` — MARPOL Annex
    VI fuel oil delivery data
  - WasteDisposal: `wasteDisposalFacility`, `wasteDisposalReceiptNumber` —
    MARPOL Annex V waste delivery receipt
  - CrewChange: `crewChangeDirection`, `crewChangeNationalities` — FAL
    Convention crew change data
  - PreArrivalNotification: `estimatedArrival`, `preArrivalNotificationPort` — FAL
    Convention pre-arrival notification
  - PortHealthDeclaration: `phdSSCReference`, `phdVaccinationRequired` — IHR
    (2005) health declaration metadata
  - WastePreNotification: `wastePreNotificationPort`,
    `wastePreNotificationStatus` — MARPOL Annex V waste pre-notification
  - VoyagePlan: `voyagePlanRouteName`, `voyagePlanDeparturePort`,
    `voyagePlanDestinationPort` — SOLAS V/34 voyage plan ports

  **vessel-registry.ttl** (22 new datatype properties):
  - CallSign: `callSignAllocatedBy` — ITU Radio Regulations allocation
  - ClassSociety: `classSocietyName`, `classSocietyCode` — SOLAS II-1/3-1 and
    IMO Resolution A.739(18) recognized organization data
  - DeadweightTonnage: `deadweightSummerLoadLine` — IMO Tonnage Convention (1969)
    load line reference
  - FlagState: `flagStateCountryCode`, `flagStateName` — UNCLOS Article 91 flag
    state identification
  - Fleet: `fleetName`, `fleetOperatorName` — fleet administration data
  - GrossTonnage: `grossTonnageConvention`, `grossTonnageUnit` — 1969 Tonnage
    Convention measurement metadata
  - IMONumber: `imoNumberCheckDigit`, `imoNumberAssignedBy` — IMO Resolution
    A.1117(30) number assignment
  - MMSI: `mmsiMidCode`, `mmsiAssignedBy` — ITU Radio Regulations Appendix 43
    MMSI allocation
  - NetTonnage: `netTonnageConvention` — 1969 Tonnage Convention measurement
  - VesselCapacity: `capacityUnit`, `capacityType` — capacity measurement type
  - VesselOperationalStatus: `operationalStatusCode`,
    `operationalStatusDescription` — IMO Compendium Ship Status code list
  - VesselType: `vesselTypeCode`, `vesselTypeDescription` — IMO Compendium Ship
    Type Code

  Previous version archived to `archive/1.1.0/`.

## [1.27.0] - 2026-09-18

### Added
- **Enriched WCO thin-stub classes across all 5 domain modules (WCO 1.2.0 → 1.3.0).**
  Systematic enrichment of classes that had zero or very few own properties
  despite being referenced by other classes or the ontology structure. All new
  properties are backed by the WCO Data Model 3.10.0, Harmonized System (HS 2022),
  Revised Kyoto Convention (RKC), SAFE Framework of Standards, ICS2 (EU Reg.
  2019/1929), NCTS/Common Transit Convention, ATA/Istanbul Conventions, WTO SPS
  Agreement, WTO trade agreement references, and EU eFTI Regulation 2020/1056.
  Archived previous version 1.2.0 before enrichment.

  **customs.ttl** (30 new datatype properties):
  - AuthorityMessage: `messageType`, `messageReference`, `messageIssueDateTime`,
    `receivingCustomsOfficeCode` — WCO Data Model 3.10.0 message metadata
  - DeclarationStatus: `statusCodeList`, `statusReasonCode` — WCO status code list
    and reason
  - EntryExitSummary: `summaryType`, `entryExitGoodsItemCount`,
    `entryExitTotalGrossMass`, `customsOfficeEntryExitCode` — WCO ICS2 summary
  - ExportDeclaration: `exportTypeCode`, `exportDestinationCountry`,
    `exportDate` — WCO export declaration type and destination
  - ImportDeclaration: `importTypeCode`, `importOriginCountry`, `importDate` —
    WCO import declaration type and origin
  - TransitDeclaration: `transitStatusCode`, `customsOfficeDepartureCode`,
    `customsOfficeDestinationCode`, `transitGuaranteeAmount` — WCO/NCTS transit
  - Filing: `filingType`, `filingStatus`, `filingCustomsOfficeCode` — WCO filing
  - ICS2Reference: `ics2ReferenceType`, `ics2MRN`, `ics2DeclarationType` — EU
    ICS2 entry summary declaration reference data
  - PreferenceClaim: `preferenceTypeCode`, `preferenceCertificateReference`,
    `preferenceCalculationMethod` — WCO preference claim data
  - TariffClassification: `hsVersionYear`, `hsSupplementaryUnit`,
    `hsCustomsProcedureCode` — WCO Harmonized System classification data

  **documents.ttl** (24 new datatype properties):
  - TransitDocument: `transitType`, `transitGuaranteeReference`,
    `transitTransportMode` — WCO Data Model transit document metadata
  - SADForm: `sadBoxDescription`, `sadFormType`, `sadFormVersion` — EU Single
    Administrative Document box and form metadata
  - T1Document: `t1OfficeOfDeparture`, `t1RegistrationDate` — EU T1 transit
    departure and registration data
  - T2Document: `t2OfficeOfDeparture`, `t2RegistrationDate` — EU T2 transit
    departure and registration data
  - ImportPermitDocument: `permitIssuingAuthority`, `permitType`, `permitValidFrom`,
    `permitValidTo` — WCO Data Model import permit metadata
  - ExportLicenseDocument: `licenseIssuingAuthority`, `licenseType`, `licenseValidFrom`,
    `licenseValidTo`, `licenseValue` — WCO Data Model export license metadata
  - PreferentialOriginDoc: `originIssuingAuthority`, `originCertificationDate` —
    WCO RKC preferential origin certification
  - ATACarnet: `carnetIssuingChamber`, `carnetType`, `voucherCount` — ATA/Istanbul
    Convention carnet metadata

  **locations.ttl** (11 new datatype properties):
  - CustomsOffice: `officeType`, `officeCountryCode` — WCO Data Model office
    type and country code
  - BorderCrossing: `borderCrossingType`, `borderCountryCode` — WCO Data Model
    crossing type and country
  - FreeZone: `freeZoneType`, `freeZoneAreaCode`, `freeZoneAuthorizingAuthority` —
    WCO RKC free zone classification
  - CustomsControlledArea: `areaType`, `areaSupervisingOfficeCode` — WCO
    controlled area classification
  - DesignatedExportPlace: `placeType`, `placeSupervisingOfficeCode` — WCO RKC
    export place classification

  **party.ttl** (17 new datatype properties):
  - Declarant: `declarantType`, `declarantStatus` — WCO Data Model declarant
    type (direct/indirect) and status
  - CustomsAuthority: `authorityJurisdiction`, `authorityType` — WCO authority
    scope and type
  - CustomsBroker: `brokerLicenseType`, `brokerJurisdiction`, `brokerAuthorizedScope` —
    WCO broker license details
  - Importer: `importerCountry`, `importerLegalStatus` — WCO/EU importer country
    and legal status
  - Exporter: `exporterCountry`, `exporterLegalStatus` — WCO/EU exporter country
    and legal status
  - AEOHolder: `aeoCertificateType`, `aeoStatus`, `aeoIssuingCountry` — WCO SAFE
    Framework AEO certificate details
  - FreightAgent: `agentType`, `agentReference`, `agentAuthorization` — WCO Data
    Model agent metadata

  **trade-facilitation.ttl** (24 new datatype properties):
  - CertificateOfOrigin: `originCriterion`, `originIssuingAuthority`,
    `originCertificationDate`, `originatingCountry` — WCO RKC origin certification
  - SPSCertificate: `spsCertificateType`, `spsIssuingAuthority`,
    `sanitaryMeasureType` — WTO SPS Agreement certificate metadata
  - ImportPermit: `importPermitType`, `importPermitIssuingAuthority` — WCO Data
    Model import permit type and authority
  - ExportPermit: `exportPermitType`, `exportPermitIssuingAuthority` — WCO Data
    Model export permit type and authority
  - eFTIRecord: `eFTIRecordCreationDate`, `eFTIRecordStatus`, `eFTIDataFormat` —
    EU eFTI Regulation 2020/1056 record metadata
  - AEOCertification: `certificationIssueDate`, `certificationExpiryDate`,
    `certifyingAuthority` — WCO SAFE Framework certification dates and authority
  - TrustedTrader: `traderType`, `authorizationDate`, `authorizedScope` — WCO
    SAFE Framework trusted trader authorization
  - SingleWindow: `windowJurisdiction`, `windowURL` — WCO RKC/SAFE Framework
    single window metadata
  - TradeAgreementReference: `agreementType`, `agreementCountryCode` — WTO
    agreement type and partner country

## [1.26.0] - 2026-09-18

### Added
- **Enriched Sustainability thin-stub classes across 2 domain modules (Sustainability 1.1.0 → 1.2.0).**
  Systematic enrichment of emission scope, fuel type, reporting, and energy
  classes that had zero or very few own properties despite being referenced by
  other classes. All new properties are backed by ISO 14083:2023, GLEC Framework,
  IMO DCS, SBTi, GRI Standards, Verra/Gold Standard, and GHG Protocol.

  **carbon.ttl** (11 new datatype properties):
  - Scope1Emission: `fuelTypeConsumed` — fuel for direct emissions (ISO 14083)
  - Scope2Emission: `energySourceType` — purchased energy type (ISO 14083)
  - Scope3Emission: `transportModeCategory` — value chain transport mode (ISO 14083)
  - EmissionFactor: `factorTransportMode`, `factorGeographicScope`,
    `factorValidityPeriod` — GLEC Framework mode, region, validity data
  - EmissionReport: `reportStatus`, `reportSubmissionDate`, `reportingEntity` —
    GRI Standards report metadata
  - CarbonOffset: `offsetProjectId`, `offsetVintage` — Verra/Gold Standard
    registry project ID and vintage year

  **energy.ttl** (10 new datatype properties):
  - FuelType (HFO/VLSFO/LNG subclasses): `fossilFuelGrade`, `carbonIntensity` —
    ISO 14083 grade-specific carbon intensity
  - FuelType (Methanol subclass): `biofuelBlendPercentage`, `feedstockType` —
    ISO 14083 biofuel blend and feedstock reporting
  - Hydrogen: `hydrogenProductionMethod`, `hydrogenPurity` — ISO 14083 green/blue/grey
    production method
  - Electric: `gridMixPercentage`, `renewablePercentage` — ISO 14083 grid mix and
    renewable share
  - EnergySource: `sourceType`, `sourceMixPercentage` — ISO 14083 source classification

## [1.25.0] - 2026-09-18

### Added
- **Enriched RAIL thin-stub classes across all 6 domain modules (RAIL 1.0.0 → 1.1.0).**
  Systematic enrichment of classes that had zero or very few own properties
  despite being referenced by other classes or the ontology structure. All new
  properties are backed by the TAF TSI data catalogue (taf_cat_complete.xsd,
  Commission Regulation (EU) No 1305/2012, Annex D.2 Appendix F).

  **rolling-stock.ttl** (12 new datatype properties):
  - WagonStatusMessage: `eventType`, `eventDateTime`, `loadingStatus`,
    `messageCreationDateTime` — TAF TSI wagon event data
  - WagonAtDeparture: `departureTimeAtLocation` — TAF TSI scheduled departure
  - WagonTelematics: `telematicsOnBoardIndicator` — TAF TSI telematics flag
  - TelematicsDevice: `deviceType`, `manufacturerName`, `atexCertified`,
    `atexLevel` — TAF TSI telematics device specifications
  - TrainCompositionMessage: `compositionMessageStatus`, `transferPoint` —
    TAF TSI composition message metadata

  **train-running.ttl** (15 new datatype properties):
  - TrainRunningInformationMessage: `runningMessageStatus`, `responsibleRU`
  - TrainRunningForecastMessage: `forecastMessageStatus`, `forecastResponsibleRU`
  - TrainRunningInterruptionMessage: `interruptionMessageStatus`, `interruptionResponsibleRU`
  - TrainRunningData: `exceptionalGaugingIndicator`, `dangerousGoodsIndicator`
  - TrainRunningTechData: `trainType`, `trainWeight`, `trainLength`,
    `trainMaxSpeed`, `numberOfAxles` — TAF TSI technical train data
  - TrainLocationStatus: `bookedLocationDateTime` — TAF TSI booked timing

  **path-request.ttl** (19 new datatype properties):
  - PathRequestMessage: `pathMessageStatus`, `processType`, `typeOfInformation`
  - PathConfirmedMessage: `pathConfirmedMessageStatus`, `pathConfirmedProcessType`,
    `pathConfirmedTypeOfInformation`
  - PathCanceledMessage: `pathCanceledMessageStatus`, `pathCanceledProcessType`,
    `pathCanceledTypeOfInformation`
  - PathNotAvailableMessage: `pathNotAvailableMessageStatus`,
    `pathNotAvailableProcessType`, `pathNotAvailableTypeOfInformation`
  - PathDetailsMessage: `pathDetailsMessageStatus`, `pathDetailsTypeOfInformation`
  - PathDetailsRefusedMessage: `pathDetailsRefusedMessageStatus`,
    `pathDetailsRefusedProcessType`, `pathDetailsRefusedTypeOfInformation`
  - PreArrangedPath: `preArrangedPathCode` — TAF TSI pre-arranged path code
  - OnDemandPath: `onDemandPathIndicator` — TAF TSI on-demand path flag
  - PathInformation: `plannedCalendar` — TAF TSI bitmap calendar

  **consignment.ttl** (5 new datatype properties):
  - ConsignmentLevelData: `agreedTimeOfDelivery`, `contractNumber`
  - ShipmentType: `shipmentTypeCode` — CIM/CUV/SMGS classification
  - ExceptionalConsignment: `permissionNumber`, `imPartner`

  **party.ttl** (2 new datatype properties):
  - InfrastructureManager: `imCompanyCode`
  - AllocationCompany: `allocationCompanyCode`

  **shared-kernel.ttl** (4 new datatype properties):
  - OperationalTrainIdentifier: `operationalTrainNumber`, `scheduledTimeAtHandover`
  - ValidityPeriod: `validityStartDateTime`, `validityEndDateTime`

  Previous version archived to `archive/1.0.0/`.

## [1.24.0] - 2026-09-18

### Added
- **Enriched TIC thin-stub classes across 4 domain modules (TIC 1.3.0 → 1.4.0).**
  Systematic enrichment of classes that had zero or very few own properties
  despite being referenced by other classes or the archetype. All new
  properties are backed by the TIC 4.0 standard (TIC4.0 Release 2025.017 /
  BSI PAS 4000:2026, see https://tic40.org/standards/).

  **events.ttl** (9 new datatype properties):
  - GateInEvent / GateOutEvent: `gateLane`, `driverId` — TIC 4.0 gate event data
  - VesselLoadEvent: `craneId`, `craneOperator`, `loadingSequence` — TIC 4.0 loading event
  - VesselDischargeEvent: `dischargeSequence` — TIC 4.0 discharge event
  - StackEvent: `stowCell`, `stowTier` — TIC 4.0 yard stack event

  **terminal-infrastructure.ttl** (7 new datatype properties):
  - Gate: `gateType`, `gateLaneCount` — TIC 4.0 gate infrastructure
  - YardArea: `yardAreaType`, `yardAreaCapacityTEU` — TIC 4.0 yard area
  - Berth: `quayCraneCount` — TIC 4.0 berth equipment count
  - QuayCrane / YardCrane: `craneStatus`, `craneOutreachMetres` — TIC 4.0 crane specifications

  **handling-operations.ttl** (4 new datatype properties):
  - Order: `orderStatus`, `orderResult` — TIC 4.0 order lifecycle
  - CarrierTrip: `transportMode`, `tripDistanceKm` — TIC 4.0 transport movement

  **reefer-monitoring.ttl** (4 new datatype properties):
  - ReeferMonitoring: `humidityLevel`, `ventilationSetting`,
    `humidityControlActive` — TIC 4.0 (Release 2024.012) reefer monitoring data

  Previous version archived to `archive/1.3.0/`.

## [1.23.0] - 2026-09-18

### Added
- **Enriched MMT thin-stub classes across all 10 domain modules (MMT 2.1.0 → 2.2.0).**
  Systematic enrichment of ~90 classes that had zero or very few own properties
  despite being referenced by other classes or the archetype. All new properties
  are backed by the UN/CEFACT Multi-Modal Transport Reference Data Model
  (MMT-RDM) RABIE/BBIE property model.

  **mmt.ttl** (15 new datatype properties):
  - 9 dangerous-goods subclass classes (ExplosiveGoods, FlammableGas,
    FlammableLiquid, FlammableSolid, OxidizingSubstance, ToxicSubstance,
    RadioactiveMaterial, CorrosiveSubstance, MiscellaneousDangerousGoods):
    class-specific properties (e.g., `explosiveClassCode`, `flashPoint`,
    `radioactiveActivity`, `packingGroup`) — UN/CEFACT MMT-RDM DG types

  **cargo.ttl** (24 new datatype properties):
  - CargoInsurance: `insuranceValue`, `policyNumber`, `insuredAmount`
  - CargoMeasurement: `measurementType`, `measurementValue`, `measurementUnit`
  - Commodity: `hsCodeVersion`, `commodityCategory`
  - DisposalInstructions: `disposalMethod`, `responsibleParty`
  - Goods: `goodsDescription`, `natureOfGoods`
  - HandlingInstructions: `handlingTemperature`, `stackingAllowed`
  - PackageSpecification: `packageQuantity`, `packageMaterial`
  - QuarantineInstructions: `quarantineType`, `treatmentMethod`
  - ShippingMarks: `marksAndNumbers`, `shippingMarkType`
  - WasteMaterial: `wasteCode`, `wasteDisposalMethod`
  - WasteMaterialComponent: `componentName`, `componentPercentage`
  - Weight: `weightType` (gross/net/chargeable)

  **consignment.ttl** (11 new datatype properties):
  - HouseConsignment: `houseBillNumber`, `forwardingAgentRef`
  - MasterConsignment: `carrierBookingRef`
  - Package: `packageQuantity`, `packageMarks`
  - TransportRoute: `routeSequence`, `routeType`
  - TransportService: `serviceType`, `serviceProvider`
  - TransportServiceExecution: `executionStatus`, `executionDate`

  **documents.ttl** (36 new datatype properties):
  - 17 document subclasses enriched with document-specific reference, issue,
    date, and type fields (AirWaybill, BillOfLading, CargoManifest,
    CertificateOfOrigin, CommercialInvoice, CustomsDeclaration,
    DangerousGoodsDeclaration, DeliveryInstructions, DocumentAuthentication,
    DocumentVersion, HouseWaybill, MasterWaybill, PackingList,
    ProductCertificate, RailConsignmentNote, RoadConsignmentNote,
    TransportInstructions)

  **equipment.ttl** (15 new datatype properties):
  - FreightContainer: `isoContainerCode`, `containerSize`, `containerType`
  - Pallet: `palletType`, `palletDimensions`
  - Seal: `sealCondition`, `sealIssuer`
  - SwapBody: `swapBodyCode`, `swapBodyDimensions`
  - TankContainer: `tankCapacity`, `tankTypeCode`
  - TemperatureSettingInstructions: `targetTemperature`, `humiditySetting`
  - TrailerUnit: `trailerPlate`, `trailerType`

  **events.ttl** (22 new datatype properties):
  - 11 event subclasses enriched with 1-2 specific properties each
    (ArrivalEvent, CustomsClearanceEvent, DeliveryEvent, DepartureEvent,
    DischargeEvent, InspectionEvent, InspectionStatus, LoadingEvent,
    PickupEvent, TransferEvent, WarehouseStorageEvent)

  **inland-transport.ttl** (12 new datatype properties):
  - BargeLeg: `bargeId`, `bargeCapacity`
  - HaulageInstructions: `haulageType`, `haulageContractor`
  - InlandCarrier: `carrierName`, `carrierType`
  - InlandTerminal: `terminalName`, `terminalType`
  - RailLeg: `railwayOperator`, `railDistance`
  - RoadLeg: `roadCarrier`, `roadDistance`

  **locations.ttl** (22 new datatype properties):
  - 11 location classes enriched with name/code/type properties
    (Location, TransportLocation, Port, Airport, RailTerminal,
    RoadTerminal, InlandPort, BorderCrossing, Warehouse, Terminal,
    DistributionCenter)

  **party.ttl** (20 new datatype properties):
  - 11 party classes enriched with name/ID/role-specific properties
    (TransportParty, Consignor, Consignee, Carrier, FreightForwarder,
    CustomsBroker, NotifyParty, TerminalOperator, WarehouseOperator,
    TransportPartyRoleCode, TransportPartyRoleAssignment)

  **transport-means.ttl** (12 new datatype properties):
  - Aircraft: `aircraftType`, `aircraftRegistration`
  - BargeVessel: `bargeId`, `bargeCapacity`
  - LogisticsConvoy: `convoySize`, `convoyLeader`
  - LogisticsMeansOfTransport: `motCategory`, `motRegistration`
  - RailVehicle: `railwayCompany`, `railVehicleType`
  - RoadVehicle: `roadVehicleType`, `motCarrierId`

  Previous version archived to `archive/2.1.0/`.

## [1.22.0] - 2026-09-18

### Added
- **Enriched DCSA thin-stub classes across 4 modules (DCSA 1.4.1 → 1.5.0).**
  Systematic enrichment of 9 classes that had zero or very few own properties
  despite being referenced by other classes. All new properties are backed by
  the DCSA OpenAPI specification (DCSA-OpenAPI GitHub repo) and DCSA standards.

  **demurrage-detention module** (11 new datatype properties):
  - FreeTimeAllowance: `freetimeTypeCode` (DET/DEM/PDM/STO enum),
    `isoEquipmentCode`, `unitOfMeasure` (CD/WD/HR/DOD enum),
    `calculationBasis` — DCSA AN API Freetime schema
  - PerDiemRate: `demurrageAmount`, `detentionAmount`, `currencyCode`,
    `rateCalculationBasis`, `paymentTermCode` — DCSA D&D charges schema
  - Waiver: `waiverReason`, `approvedBy` — Kairos extension (not in DCSA OpenAPI)

  **container-operations module** (9 new datatype properties):
  - ContainerOperationalStatus: `equipmentEventTypeCode` (17 DCSA codes),
    `emptyIndicatorCode` (EMPTY/LADEN), `facilityTypeCode` — DCSA T&T API
  - ContainerStripping: `equipmentReference`, `strippingEmptyIndicatorCode`,
    `strippingFacilityTypeCode` — DCSA T&T API (STRP event)
  - LiftOnLiftOff: `isTransshipmentMove`, `loloEquipmentEventTypeCode`
    (LOAD/DISC), `loloTransportCallReference` — DCSA T&T API

  **booking module** (13 new datatype properties):
  - ShippingInstruction: `transportDocumentTypeCode` (BOL/SWB),
    `isShippedOnBoardType`, `isElectronic`, `isToOrder`,
    `freightPaymentTermCode` (PRE/COL), `numberOfOriginalsWithCharges`,
    `numberOfCopiesWithCharges` — DCSA documentation_domain_v3.0.0
  - UtilizedTransportEquipment: `cargoGrossWeightUTE`,
    `cargoGrossWeightUnit`, `cargoGrossVolume`, `cargoGrossVolumeUnit`,
    `isShipperOwned`, `isNonOperatingReefer` — DCSA _CAR variant schema

  **schedule module** (1 new datatype property):
  - CutOffTime: `cutOffDateTimeCode` (15 DCSA CS API cut-off type codes:
    DCO, VCO, FCO, LCO, PCO, ECP, EFC, RCO, DGC, OBC, etc.)

  Previous version archived to `archive/1.4.1/`.

## [1.21.0] - 2026-09-17

### Added
- **Enriched BSP thin-stub classes across 4 modules (BSP 2.2.0 → 2.3.0).**
  Systematic enrichment of classes that had zero or very few own properties
  despite being pointed to by other classes via `rdfs:range`. All new
  properties are backed by UN/CEFACT CCL D23B, ISO 20197-1:2024, or IPPC
  standard elements.

  **reference-data module** (15 new datatype properties):
  - Measurement: `measurementValue`, `measurementUnit`
  - Weight: `weightType`
  - Volume: `volumeType`
  - Dimension: `dimensionType`, `length`, `width`, `height`
  - MonetaryAmount: `monetaryAmount`, `monetaryCurrency`
  - Port: `portName`, `portType`
  - Warehouse: `warehouseType`, `bondedIndicator`
  - Facility: `facilityId`

  **commercial module** (28 new properties, 1 new object property):
  - TransportEquipment: `equipmentId`, `equipmentType`, `equipmentSizeType`,
    `sealNumber`, `tareWeight`, `equipmentOwner` (→ `party:TradeParty`)
  - Package: `packageId`, `packageTypeCode`, `marksAndNumbers`,
    `packageGrossWeight`, `packageNetWeight`, `packageVolume`
  - ShipmentLine: `shipmentLineId`, `lineItemNumber`, `lineQuantity`,
    `lineDescription`
  - SalesContract: `contractNumber`, `contractDate`, `contractTerms`
  - SalesOrder: `salesOrderNumber`, `salesOrderDate`
  - Quotation: `quotationNumber`, `quotationDate`, `quotationValidityDays`
  - TransportService: `serviceType`, `transportMode`
  - TransportLeg: `legSequence`, `legTransportMode`, `legOrigin`, `legDestination`

  **documents module** (34 new datatype properties):
  - PackingList: `packingListTotalPackages`, `packingListTotalNetWeight`,
    `packingListTotalGrossWeight`
  - ImportLicense: `licenseNumber`, `licenseExpiryDate`, `licenseCountryOfIssue`,
    `licenseGoodsDescription`
  - ExportLicense: `exportLicenseNumber`, `exportLicenseExpiryDate`,
    `exportLicenseCountryOfIssue`, `exportLicenseGoodsDescription`
  - InspectionCertificate: `inspectionType`, `inspectionResult`,
    `inspectionAuthority`
  - PhytosanitaryCertificate: `phytosanitaryOriginCountry`,
    `phytosanitaryTreatmentMethod`, `phytosanitaryImportingCountry`
  - HealthCertificate: `healthCertificateType`, `healthCertificateProduct`,
    `healthCertificateAuthority`
  - InsuranceCertificate: `insurancePolicyNumber`, `insuredAmount`,
    `insuranceCoverageType`, `insuranceInsurer`
  - DeliveryNote: `deliveryNoteGoodsReceived`, `deliveryNoteReceivedBy`,
    `deliveryNoteDate`, `deliveryNoteSignatureDate`
  - ReceiptAdvice: `receiptAdviceQuantityReceived`,
    `receiptAdviceDiscrepancyCode`, `receiptAdviceReceivedDate`
  - DocumentEvent: `documentEventType`, `documentEventTimestamp`,
    `documentEventActor`

  **revenue-yield module** (3 new datatype properties):
  - CapacityUtilization: `slotUtilizationPercentage`,
    `weightUtilizationPercentage`, `volumeUtilizationPercentage`

  Previous version archived to `archive/2.2.0/`.

## [1.20.2] - 2026-08-16

### Added
- **Enriched BSP Address class (BSP 2.1.0 → 2.2.0).** The `Address` class in
  `reference-data` had only 4 string fields (`streetAddress`, `city`,
  `stateProvince`, `postalCode`). Added: `addressCountry` (object property →
  `:Country`), `latitude`/`longitude` (WGS84 decimal), `addressType`, `poBox`,
  `buildingNumber`, `careOf` — all backed by UN/CEFACT CCL D23B TradeAddress
  elements (ISO 20197-1:2024). The Address is now a self-contained, queryable
  address concept.

## [1.20.1] - 2026-08-15

### Fixed
- **Duplicate class IRIs across dcsa/events and dcsa/track-and-trace (gh#81).** The
  `track-and-trace` module is a thin aggregation wrapper that declares no classes —
  it only `owl:imports` the `events` sub-module. Both were listed as separate import
  surfaces in `data-domains.yaml` and `shipping-carrier.yaml`, causing the toolkit to
  see both as candidate term owners for the same 22 class IRIs. Removed the redundant
  `track-and-trace` import entry from both; merged its `provides` description into the
  `events` entry. The `track-and-trace` owl:Ontology remains in the catalog as an
  internal DCSA hierarchy node (imported by `dcsa.ttl`); it is no longer a separate
  consumer-facing import.
- **Turtle literal stripping before rdfs:domain search (#69).** `RDFS_DOMAIN_RE`
  searched the full property block including `rdfs:comment` text. The REUSABLE marker
  "no rdfs:domain by design" itself contains `rdfs:domain`, causing every REUSABLE
  property to match the first branch and making the elif `REUSABLE_NO_DOMAIN_RE`
  branch dead code. Validation passed but for the wrong reason. Added
  `_strip_turtle_literals_and_comments()` to remove string literals and full-line
  comments before searching for `rdfs:domain`.
- **Toolkit pin updated to 5.2.3rc6.** Updated `pyproject.toml` and `uv.lock`;
  regenerated stale logistics pack docs; added `pattern_templates` as a third
  classification category in `test_bundle_conformance.py`.

## [1.20.0] - 2026-08-15

### Changed
- **Restructured to a distributable Python data package.** The `ontology-reference-models/`
  directory now lives inside `kairos_ontology_referencemodels/` and is bundled automatically
  in the wheel by hatchling. Consumers install via `pip install
  kairos-ontology-referencemodels` and resolve the data directory through
  `refmodels_root()` (importlib.resources) instead of a sparse git clone. The release
  workflow now builds and uploads a `.whl` alongside the `.tar.gz`.

### Removed
- **`kairos-ontology-toolkit` removed from runtime dependencies.** This is now a data
  package, not a consumer. The toolkit remains in `dev` extras for contract testing.

## [1.19.0] - 2026-08-15

### Fixed
- **Consumer-facing docs drift.** The README claimed a stale `version-1.15.0` badge and
  "Current Version: 1.13.0" footer, gave three conflicting ontology-suite counts, and a
  Quick Start pointing at a `reference-models/` layout that does not exist. It now carries
  a real CI badge, the reconciled "8 derived suites + SupplyChain bridge" framing, a
  corrected repository tree, and a Quick Start pointing contributors at
  `python scripts/check_all.py`. `examples/basic-usage.md` clone URLs fixed to
  `kairos-ontology-referencemodels`. `.github/copilot-instructions.md` tier table now lists
  the SupplyChain bridge in the derived tier.
- **The release gate no longer runs a weaker check set than the PR gate.** `release.yml`
  restated a subset of `validate.yml`'s checks by hand, and had drifted: it was missing
  `validate_pattern_conformance.py` and the entire `cross-repo-contract` job. A tag could
  therefore publish a bundle that PR CI would have rejected — including, until v1.17.0,
  one that no hub could inventory (#57). `release.yml` now *calls* `validate.yml` via
  `workflow_call` and gates the release on it with `needs:`, so the two cannot diverge:
  there is only one gate.

  Releases pass `skip-toolkit-pin-check: true`. That check compares the pin against
  whatever the toolkit has published since, so it is time-dependent and would block a
  release for a reason unrelated to the artifact being released — it went red on `main`
  this way between #58 and #59. What a release does still need, that the pinned toolkit
  can actually read the bundle, is the contract and conformance suites, which run either
  way.

  The input is phrased as skip-rather-than-require deliberately: on push/PR the `inputs`
  context is null and GitHub coerces null and `false` alike, so a `!= false` guard would
  have silently skipped the pin check on ordinary CI.

  Also drops `release.yml`'s commented-out
  `# TODO: Enable when kairos-ontology-toolkit is published to PyPI` block, the twin of
  the one removed from `validate.yml` in v1.17.0, and its now-unused Python setup.

### Removed
- **Hub-scaffold residue.** `package.json` (its only script rendered a client-hub dbt ERD
  path that does not exist here), `.devcontainer/` (hub-named, pip+npm post-create), and
  `.env.example` (toolkit AI-provider config consumed by nothing in this repo).
  `.gitignore` now covers `.claude/`.
- **`scripts/test_catalog.py`.** Standalone, non-pytest; its disk-existence check is fully
  covered by `tests/test_model_registration.py`, and it had no reader other than a
  contract-manifest note (now updated).
- Seven landed `.docs/wip/` documents (five standard gap-analysis reports, the MMT
  equipment-refactor plan, the logistics dbt-silver design plan). Content preserved in git
  history; `.docs/wip/README.md` now states the live-CRs-only rule.

### Added
- **`scripts/check_all.py` — the tier-1 contributor gate.** Parses `validate.yml`'s
  `validate` job and runs its `run:` blocks in CI order (reuse, not restatement); fails
  loudly on an unparseable workflow; prints the tier-2 contract command as a hint.
- **`test_every_rewrite_prefix_is_a_real_directory`** in
  `tests/test_model_registration.py`: statically asserts every `<rewriteURI>` prefix in
  `catalog-v001.xml` resolves to a real directory — the gap the contract manifest flagged.
- **`.github/dependabot.yml`** (github-actions + pip, weekly). The toolkit wheel pin stays
  with `check_toolkit_pin.py` and is intentionally uncovered.
- **`pytest-randomly`** in the dev extras and explicit
  `[tool.pytest.ini_options] testpaths` — CI passes `-p no:randomly` but the plugin
  previously arrived only transitively via the toolkit wheel.

### Changed
- **GitHub Actions bumped to current majors** via dependabot (#72–#75, #77):
  `actions/checkout` v4→v7, `actions/upload-artifact` v4→v7, `actions/github-script`
  v7→v9, `actions/setup-python` v5→v7, `astral-sh/setup-uv` v5→v7.

## [1.18.0] - 2026-08-15

Four fixes from one blind authoring run (issues #61–#64, filed against v1.16.0): the reference
content and its own patterns disagreed in four places, and each fix makes the existing decision
explicit rather than inventing a new one. Module bumps riding this release: **MMT 2.1.0**,
**BSP 2.1.0**, **DCSA 1.4.0**, **patterns 0.4.0** — all minor; no archetype pin changes.

### Changed — the equipment binding rule is now recorded where authors read (#64)

Every hub authoring an `equipment` domain must import both `mmt/equipment` and
`dcsa/equipment` (Managed Import Completeness leaves no opt-out), and the two overlap by name
on `ReeferContainer`/`TankContainer` with different vocabularies. The anchor decision already
existed — `canonical-class-registry.yaml` `equipment-asset` fixes
`mmt/equipment#TransportEquipment` as the pack anchor with `dcsa/equipment#Container` as its
container-scoped overlay, and the archetypes each pick one side — but neither
`data-domains.yaml` nor the classes themselves said so.

- **logistics `data-domains.yaml` equipment domain**: a domain-level `note` plus per-import
  `note`s now state the rule — the binding follows the archetype's equipment anchor (mmt for
  mixed/non-containerised fleets, dcsa for container carriers); for mmt-anchored fleets
  `dcsa/equipment` is the ISO 6346 code reference on the container subset, not a second
  anchor; **one physical unit is never bound to both twins**. Deliberately *not* an
  `overlaps` entry: its single `resolved_to` cannot express an archetype-conditional
  resolution, and `resolved_to: MMT/Equipment` would be false for shipping-carrier hubs.
- **TTL comments on all four twin classes** (mmt+dcsa `ReeferContainer`/`TankContainer`) name
  the twin IRI and the binding rule at point of use. MMT rides the unreleased 2.1.0; **DCSA
  1.3.0 → 1.4.0** (annotations = minor; pins `>=1.3.0,<2` unaffected).
- The forced dual import itself is toolkit behavior and deliberately unchanged.

### Changed — patterns 0.4.0: qualified-role-assignment × governed-code-list composition stated (#62)

The two most commonly co-applicable patterns both declared `naming: normative` and prescribed
different names for the same slot (`hasRole` vs `has<Dimension>Code`), and following either one
literally landed in the other's anti-pattern. The composition rule is now stated in both
(`pattern.md` "Composes with" sections + `pattern.yaml` comments): **`hasRole` names the slot;
`governed-code-list` decides its shape.** Single-source, ungoverned dimension → literal is fine
and qualified-role-assignment is complete alone; when governed-code-list also applies, `hasRole`
ranges to the governed `<Dimension>Code` class and the raw string moves to
`source<Dimension>Value`. `has<Dimension>Code` remains normative for every slot no other pattern
claims. This ratifies what bsp/mmt party already ship (`hasRole` → `PartyRoleCode` /
`TransportPartyRoleCode`).

Adjacent defect fixed: qualified-role-assignment's worked example declared `hasRole` as a
DatatypeProperty over `xsd:string` — contradicting both the shipped modules and
governed-code-list's `raw-string-as-classification-of-record` anti-pattern. The example now
shows the composed form, with the literal collapse allowed only under the stated caveat.
Also added to governed-code-list: where the values live (slot = the standard's, members =
client master data in the blueprint's `reference-data` domain; the enum constraint is SHACL
`sh:in` via `kairos-ontology suggest-shapes`, DD-076).

### Changed — patterns 0.4.0: class-anchored grain collisions are now machine-readable (#63)

`grain_collisions` shipped in two shapes — `{against, reason}` mappings (multimodal-order-leg)
and bare prose (qualified-role-assignment, governed-code-list) — with the party collision, the
most consequential entry in the library, unavailable to any automated check.

- **qualified-role-assignment**: the party prose entry is now **five `{against, reason}`
  entries**, one per role parent (`bsp/party#TradeParty`, `mmt/party#TransportParty`,
  `dcsa/party#ShippingParty`, `imo/party#MaritimeParty`, `tic/party#TerminalParty` — the set
  #55 completed); the location prose entry is now two entries
  (`dcsa/locations#PortOfLoading`, `#PortOfDischarge`). `against` stays **scalar** — the
  toolkit coverage ledger keys units on it, and one-entry-per-IRI is what a
  does-not-collapse-into check consumes.
- **The two-shape design is now stated, not accidental**: the schema `$comment`,
  contract-manifest notes, and a new test pin it — class-anchored collisions MUST use the
  mapping form; the bare-string form is reserved for grain warnings that name no class
  (governed-code-list's source-noun caveat is the only shipped instance, unchanged — it has
  no class IRI to carry and banning prose would relocate it without making it checkable).
- Toolkit follow-up filed: the reshaped units re-key from `#0`/`#1` to IRIs in
  `list-patterns --coverage` (2 → 7 units), staling two registry entries until the toolkit
  registry updates. The ledger is not a gate; repo CI is unaffected.

### Changed — MMT 2.1.0 and BSP 2.1.0: role-assignment properties are now genuinely reusable (#61)

The qualified-role-assignment pattern's own grain collision ("none of the five party parents
is the durable identity on its own") forces every hub to mint a local assignment class — but
`hasRole`, `roleValidFrom` and `roleValidTo` were domain-bound to the *reference* assignment
classes, so no hub could carry them without subclassing the class the pattern tells it to
avoid. Both hit the wall in practice (#43's `owl:unionOf` workaround was a symptom).

- **mmt/party + bsp/party**: `rdfs:domain` dropped from `hasRole`, `roleValidFrom`,
  `roleValidTo` (marked `REUSABLE — no rdfs:domain by design`); `rdfs:range` unchanged.
  Minor bumps per the axiom-relaxation rule — entailments weaken, no instance data breaks,
  no IRI moves (precedent: BSP 1.6.0's de-domained address/contact properties).
- **`schema:domainIncludes`** (first use in the repo) now carries the intended anchor as
  additive, non-entailing domain evidence — the toolkit's `effective_domain_classes()` /
  `class_properties()` already honor it. Backfilled onto the four de-domained BSP 1.6.0
  properties (`hasContact`, `hasAddress`, `hasBillingAddress`, `hasShippingAddress`).
  Deliberately NOT on `bsp-party:hasParty` — a landing pad has no single anchor; its
  subjects are owned by the specialisations' own `rdfs:domain` declarations.
- **Scope notes, stated as decisions**: `hasRole` keeps its module-local code-list range —
  reuse it only when the role vocabulary IS that module's code list; otherwise mint a local
  `hasRole` per the pattern (the validity pair stays reusable either way).
  `assignedToTransportParty`/`assignedToTradeParty` are excluded — their *ranges* are the
  party classes, a separate design decision.
- CONTRACT.md now states the axiom-relaxation rule explicitly (dropping `rdfs:domain` /
  widening `rdfs:range` = minor). Archetype pins `>=2.0.0,<3` remain valid; no archetype
  changes.

## [1.17.0] - 2026-08-14

### The shipped bundle now inventories cleanly, and CI proves it (#57)

v1.16.0 released with four defects that appear the first time a hub runs
`kairos-ontology generate-inventory` against the bundle: three ontologies whose import
closure could not resolve, and two files that produced the same inventory filename and
clobbered each other. The resulting `check-inventory` failure was permanent — re-running
never cleared it — so every hub on that release hit a blocking gate failure on first use
and paid the cost of proving it was a false alarm.

Nothing caught it because `validate.yml`'s first job is deliberately toolkit-free and the
second ran only `test_toolkit_contract.py`, which probes the toolkit's *loaders and APIs*.
The contract was tested; the corpus was not.

#### Added — three authoritative mirrors
- **`authoritative-ontologies/OMG-Commons/`** — the 22-module Commons Ontology Library
  (MIT, versionIRI 20250801).
- **`authoritative-ontologies/OMG-LCC/`** — Languages, Countries and Codes, 3 modules
  (MIT, versionIRI 20211101).
- **`authoritative-ontologies/W3C-SKOS/`** — the SKOS core vocabulary (W3C Software and
  Document License — the first non-MIT bundled component, so `NOTICE`'s blanket "both
  bundled ontologies are MIT licensed" paragraph is now per-vendor).

  None of these is used directly by any Kairos-authored module. They are bundled because
  the vendored FIBO tree imports them. **Without them no FIBO closure resolved at all** —
  a wider blast radius than the three failing files suggested, since only `.ttl` files
  reach the inventory generator and FIBO ships `.rdf`.

  OMG LCC was **masked**: the missing Commons mirror failed the closure first, so LCC
  never appeared in any error output until Commons resolved. It surfaced only because the
  new gate resolves each closure to completion rather than grepping a generator's log.

- **`tests/test_bundle_conformance.py`** — runs the consumer's own inventory and loader
  APIs over every bundled TTL, and is wired into the existing `cross-repo-contract` job
  (which already has the pinned toolkit installed, so the marginal cost is one pytest
  argument). Three invariants: inventory filenames are injective; every source resolves
  its import closure non-degraded; every `.ttl` is classified inventoriable-or-archived,
  so a newly added file cannot slip through unnoticed.

  It deliberately does **not** grep the CLI. `generate-inventory` exits 0 while emitting
  those failures (toolkit #405), which would make the grep load-bearing, and matching
  emoji in CLI output is brittle across locales and toolkit releases. Calling the API
  makes a broken closure an exception, works against the currently pinned toolkit, and
  needed no cross-repo fix to land.

#### Changed
- **`catalog-v001.xml`** — `rewriteURI` rules for OMG Commons and OMG LCC (both publish
  IRIs ending in `/` against `<name>.rdf` on disk, exactly like FIBO), and an explicit
  `<uri>` for SKOS.
- **Pattern OWL fragments are named `<pattern-id>.ttl`, not `template.ttl`.** Both
  `deferred-relationship/template.ttl` and `multimodal-order-leg/template.ttl` mapped to a
  single `template-inventory.yaml` — the consumer namespaces inventories by owning model
  only under `derived-ontologies/`, so `blueprints/patterns/` fell outside DD-054. One
  silently overwrote the other and every hub saw an unclearable `template: STALE`.
- **`scripts/validate_structure.py`** discovers the pattern fragment by glob rather than
  by the hardcoded name `template.ttl`, so the structural guard follows the file instead
  of the filename. Without this the rename would have silently disabled the guard on both
  patterns.
- **`.github/workflows/validate.yml`** — deleted the commented-out
  `# TODO: Enable when kairos-ontology-toolkit is published to PyPI` block. It was
  superseded by `cross-repo-contract`, which installs the toolkit via `uv sync`, and it
  implied coverage that did not exist.
- **`contract-manifest.yaml`** — the new test is registered against the `catalog` and
  `ontology-modules` surfaces, with a note that `scripts/test_catalog.py` only checks
  `<uri>` targets and is blind to a wrong `rewritePrefix`; resolution is now proven by
  execution instead.

#### Changed — toolkit pin
- **Pinned toolkit bumped 5.2.1rc9 → 5.2.3rc1**, the `preview` channel head and the exact
  version the client hub reported gh#57 against. The pin check is time-dependent — it
  compares against whatever the channel has released since — so it went red on `main` as
  soon as 5.2.3rc1 shipped, independently of any change here. Bumping also means the fix
  is verified against the version that produced the original report, not just the version
  that happened to be pinned when it was written.

#### Result
`generate-inventory` over the bundle, on both 5.2.1rc9 and 5.2.3rc1: **82 of 82
inventories, zero failures, zero collisions** (was 78 generated, 3 closure failures,
1 collision).

## [1.16.0] - 2026-08-13

### Party bookkeeping (#51)

#### Changed
- **`tic/party#TerminalParty` registered as the fifth role parent** in the overlap register's
  `party-role-parents.class_uris`, with an explicitly audit-sourced evidence line (its 2
  subclasses sit below pattern-conformance check C's ≥3 detection threshold, which is why the
  #41 sweep never flagged it). The qualified-role-assignment grain-collision prose now names
  TIC alongside BSP/DCSA/MMT/IMO. No pattern exemption — it would never be exercised at the
  current threshold and would warn as stale on every CI run.

### BSP 2.0.0 — estimatedDeliveryDate rename + party-property re-ranging (#50, #51)

#### Changed — BSP **2.0.0** (breaking: term rename)
- **`bsp/commercial#expectedDeliveryDate` renamed** (closes #50). The UN/CEFACT web vocabulary
  is decisive: `HeaderTradeDelivery` carries estimated/actual/planned/requested DeliveryEvent —
  no `expected*` delivery element exists (full property list checked; org:uncefact code search
  0 hits) — so the rename is *more* source-faithful than the status quo, and the property now
  carries the citation it never had (`rdfs:seeAlso` `estimatedDeliveryEvent`, with the
  event→date flattening stated as a deliberate simplification). Evidence boundary: the D23B
  spreadsheet/XSD itself was not enumerable; the audit covers the web-vocabulary rendering.
  The AUDIT-TODO exemption in `temporal-quartet/pattern.yaml` is deleted — the exemptions
  ledger is now fully cited.

  | old (BSP 1.x) | new (BSP 2.0.0) |
  |---|---|
  | `bsp/commercial#expectedDeliveryDate` | `bsp/commercial#estimatedDeliveryDate` |

- **Party-property re-ranging (#51 precondition 2, BSP side).** The 9 object properties that
  ranged over deprecated role subclasses — `hasBuyer`/`hasSeller`/`hasShipper`/`hasConsignee`/
  `hasCarrier`/`hasManufacturer` (bsp/party) and `issuingBank`/`advisingBank`/`confirmingBank`
  (bsp/financial — missed by the #41 inventory) — now range over the undeprecated `:TradeParty`
  and specialise a new domainless REUSABLE `bsp-party:hasParty` landing pad (mirrors
  `mmt/consignment#hasParty`). Term IRIs, domains, and the deprecated subclasses are unchanged;
  instance data stays valid; typed-range *entailments* weaken, which is the point. Archetype
  pins move to `BSP >=2.0.0,<3` (freight-forwarder, unit-load-carrier; archetypes 0.6.1) so
  hubs opt in consciously. Rides the major the rename already forced — one migration event,
  not two.

### Required modules now conform to the normative patterns — and CI checks it (#41)

The pattern library and the derived ontologies were governed independently and nothing checked
one against the other, so `tier: required` modules shipped names a normative pattern bans.
This entry fixes today's instances **and** the mechanism.

#### Changed — MMT **2.0.0** (breaking: term renames)
- **temporal-quartet conformance in `mmt/consignment`** — the four uncited `*Time`-suffixed
  quartet properties are renamed (clean break, no bridge stubs; old→new below). Any hub bound
  to the old IRIs must migrate when it opts into MMT 2 — the archetype pins move to
  `>=2.0.0,<3` in the same release precisely so the break is a conscious opt-in (one local hub,
  cldn2-ontology-hub-1 `movement.ttl`, is known to bind them).

  | old (MMT 1.x) | new (MMT 2.0.0) |
  |---|---|
  | `estimatedDepartureTime` | `estimatedDeparture` |
  | `actualDepartureTime` | `actualDeparture` |
  | `estimatedArrivalTime` | `estimatedArrival` |
  | `actualArrivalTime` | `actualArrival` |

  `availabilityDueDateTime` is **kept**: it mirrors UN/CEFACT RABIE v101
  `SupplyChainConsignment.AvailabilityDueDateTime`, and source fidelity wins — visibly, via a
  cited exemption entry (see the precedence rule below). `carrierAcceptanceDateTime` /
  `exportExitDateTime` are single event timestamps, not quartet members — unchanged.
- **multimodal-order-leg grain 2 is now real, not asserted** — `inland-transport#InlandLeg`
  gains `rdfs:subClassOf consignment:TransportLeg` (RailLeg/BargeLeg/RoadLeg inherit), so
  mode-as-reified-leg-subclass actually holds in the graph. `transportMode`/`modeCode` stay on
  `TransportMovement` (RABIE-faithful) with comments stating they are inherited from the leg,
  never decided there. MMT 1.1.0 archived as its first frozen snapshot.

#### Changed — BSP **1.6.0** and MMT party (additive role machinery)
- **qualified-role-assignment machinery added** to `bsp/party` (`TradePartyRoleAssignment`,
  governed `PartyRoleCode`, `assignedToTradeParty`, `hasRole`, `roleValidFrom/To`) and
  `mmt/party` (`TransportPartyRoleAssignment` etc.). One durable party, 0..n role assignments,
  each scoped to a context — the multi-role organisation (debtor+creditor+forwarder,
  concurrently) is finally representable with required modules.
- **The 22 role subclasses (14 BSP + 8 MMT) are `owl:deprecated true`** — kept as standards
  overlays for source fidelity and message-level interop, never the hub's role model. Removal
  is parked on the durable-party-identity stakeholder decision (overlap-register
  `party-role-parents`); design record in `.docs/design/party-design.md`.
- **Reusable properties are now genuinely reusable** — `hasContact` / `hasAddress` /
  `hasBillingAddress` / `hasShippingAddress` drop `rdfs:domain :TradeParty` (marked
  `REUSABLE — no rdfs:domain by design`), killing the back-door subsumption that made hubs
  redeclare them locally. `validate_structure.py` accepts a missing domain only with that
  marker; range stays required.
- **Archetypes re-authored** (`freight-forwarder`, `unit-load-carrier`; archetypes 0.6.0):
  role-assignment class + role code list are `required` core concepts; the deprecated role
  subclasses demote to `recommended`/`optional`. Version pins: MMT `>=2.0.0,<3`,
  BSP `>=1.6.0,<2` (also `shipping-carrier`'s MMT pin).

#### Added — the mechanism
- **`scripts/validate_pattern_conformance.py`**, wired into CI as a blocking step: (A)
  temporal-quartet naming over every current derived/blueprint TTL — the 16-name quartet rule
  plus the structured banned-token rule, honouring cited exemptions and skipping
  `owl:deprecated` subjects; (B) multimodal-order-leg participants — every `leg_module_iris`
  module that declares `*Leg` classes must wire one under the pattern's leg class
  (means-borne modes are noted and skipped), and no mode-named property/subclass at order
  grain; (C, advisory) subclass-identity-by-role detection outside the pattern's exemptions.
  Exemption-usage stats are printed so dead entries stay visible. Negative-tested: a
  reintroduced live `estimatedDepartureTime` fails the build.
- **Precedence rule** in `CONTRACT.md` ("Patterns vs derived modules"): pattern-normative
  naming governs Kairos-chosen names; a derived module mirroring a cited source element wins on
  source fidelity, but only through a cited `exemptions` entry; an unexempted disagreement is a
  repo defect and CI fails on it. Plus a **term-level rename/deprecation policy** (rename =
  major module bump with old→new table; additive/deprecation = minor; deprecated terms stay
  resolvable for the major).
- **Cited exemption seeds** in `temporal-quartet/pattern.yaml` for every source-faithful
  variant this repo ships (DCSA T&T/BKG, IMO port-call, TAF TSI train-running, RABIE
  availability) — and one `AUDIT-TODO`: `bsp/commercial#expectedDeliveryDate`, exempted pending
  source verification with a follow-up issue to rename to `estimatedDeliveryDate` if uncited.
- **`qualified-role-assignment` exemptions** for the still-live DCSA/IMO party overlays;
  applicability prose states hubs MUST NOT copy the subclass shape and documents the
  domainless-property trap.

#### Changed — tooling
- **Toolkit pin `5.2.0rc8` → `5.2.1rc9`** (`check_toolkit_pin.py --update`), `uv.lock`
  regenerated; cross-repo contract tests and `list-patterns --coverage` verified against the
  installed RC (43 units, unit ids stable, 0 unrecognized shapes).

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
- **`kairos_ontology_referencemodels/ontology-reference-models/CONTRACT.md`** — what this repository publishes, what consumers may
  rely on, and how it changes. Kept deliberately thin: rules and policy only, no restatement of
  schemas or key lists, because a prose copy of a machine file is what rots.
- **`kairos_ontology_referencemodels/ontology-reference-models/contract-manifest.yaml`** — the machine-readable half: each of the
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
  `kairos_ontology_referencemodels/ontology-reference-models/blueprints/` distinct from authoritative and
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
  `kairos_ontology_referencemodels/ontology-reference-models/blueprints/` so the new `archetypes/VERSION`
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
- Updated `kairos_ontology_referencemodels/ontology-reference-models/catalog-v001.xml` for the new modules

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
- Corrected `scripts/test_catalog.py` catalog path to `kairos_ontology_referencemodels/ontology-reference-models/catalog-v001.xml` (was incorrectly pointing to repo root)
- Removed redundant `kairos_ontology_referencemodels/ontology-reference-models/` prefix from all relative URI paths in `kairos_ontology_referencemodels/ontology-reference-models/catalog-v001.xml` so paths resolve correctly from the catalog's own directory (OASIS XML Catalog spec)
- Moved canonical catalog location to `kairos_ontology_referencemodels/ontology-reference-models/catalog-v001.xml`; removed stale copy from repo root

## [1.2.0] - 2026-03-01

### Changed
- Updated FIBO ontologies from Q3 2025 (master_2025Q3) to Q4 2025 (master_2025Q4)
- Corrected folder structure from `ontologies/authoritative-ontologies/` to `kairos_ontology_referencemodels/ontology-reference-models/Authoritative Ontologies/`
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