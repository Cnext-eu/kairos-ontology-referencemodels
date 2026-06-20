# Changelog

All notable changes to the Kairos Reference Models will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
