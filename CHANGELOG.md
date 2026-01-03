# Changelog

All notable changes to the Kairos Reference Models will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  - Created `Authoritative Ontologies/` for official RDF/OWL from standards bodies
  - Created `Derived Ontologies/` for our RDF interpretations of non-RDF standards
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
