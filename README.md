# Kairos Reference Models

**Centralized repository for Kairos platform canonical ontologies and reference models**

[![Validation Status](https://img.shields.io/badge/validation-passing-brightgreen.svg)](https://github.com/Cnext-eu/kairos-ontology-referencemodels/actions)
[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Overview

The Kairos Reference Models repository provides validated, versioned ontologies that serve as the foundation for the Kairos platform and customer-specific implementations. These models define the canonical structure for core business entities and their relationships.

**Key Features:**
- ✅ **Semantic versioning** for stable evolution (per-ontology + global)
- ✅ **Automated validation** on every commit (syntax, SHACL, consistency, structure)
- ✅ **FIBO integration** with 300+ Financial Industry Business Ontology files
- ✅ **8 derived ontology suites** covering logistics, trade, and sustainability
- ✅ **Accelerator Packs** — one-import bundles for Logistics and Financial Services
- ✅ **SKOS mappings** for alignment with industry standards (Schema.org)
- ✅ **Git-based distribution** via tags and submodules

---

## 📁 Repository Structure

```
kairos-ontology-referencemodels/
├── ontology-reference-models/
│   ├── authoritative-ontologies/      # Official RDF/OWL from standards bodies
│   │   └── FIBO/                      # FIBO Q4 2025 (300+ files)
│   ├── derived-ontologies/            # Our RDF interpretations of non-RDF standards
│   │   ├── DCSA/                      # Container shipping (1 root + 7 domains)
│   │   │   ├── dcsa.ttl
│   │   │   ├── booking/
│   │   │   ├── container-operations/
│   │   │   ├── equipment/
│   │   │   ├── events/
│   │   │   ├── locations/
│   │   │   ├── party/
│   │   │   └── transport-documents/
│   │   ├── MMT/                       # Multi-modal transport (1 root + 10 domains)
│   │   ├── BSP/                       # Buy-Ship-Pay (1 root + 6 domains)
│   │   ├── TIC/                       # Terminal operations (1 root + 6 domains)
│   │   ├── IMO/                       # Maritime regulatory (1 root + 5 domains)
│   │   ├── WCO/                       # Customs & border (1 root + 5 domains)
│   │   ├── Sustainability/            # Carbon & energy (1 root + 2 domains)
│   ├── accelerator-packs/             # Pre-composed bundles
│   │   ├── logistics/                 # 8 ontologies for logistics companies
│   │   └── financial-services/        # FIBO + BSP for financial services
│   └── catalog-v001.xml               # XML catalog for import resolution
├── scripts/                           # Tooling (validation, version management)
├── examples/                          # Usage examples
├── .github/workflows/                 # CI/CD (validate + release)
├── VERSION                            # Global semantic version
├── CHANGELOG.md                       # Version history
└── README.md
```

---

## 🏭 Ontology Suite

The repository ships **7 derived ontologies** covering the full logistics, trade, and sustainability value chain:

| # | Ontology | Standard | Focus | Domains |
|---|----------|----------|-------|---------|
| 1 | **DCSA** | DCSA API Standards | Container shipping lifecycle | 13 |
| 2 | **MMT** | UN/CEFACT MMT-RDM | Consignment, movement, cargo, equipment | 11 |
| 3 | **BSP** | ISO 20197-1:2024 | Party, contract, invoice, settlement | 7 |
| 4 | **TIC** | TIC 4.0 | Terminal operations, handling, automotive | 7 |
| 5 | **IMO** | IMO Compendium / FAL / IMDG | Vessel registry, dangerous goods, port-call | 6 |
| 6 | **WCO** | WCO Data Model 3.0 | Customs declarations, trade facilitation | 6 |
| 7 | **Sustainability** | ISO 14083:2023 / GLEC | Emissions, energy, ESG reporting | 3 |

Plus **FIBO** (300+ authoritative ontology files from the EDM Council) for financial industry concepts.

Each derived ontology lives in its own directory under `ontology-reference-models/derived-ontologies/` with a `VERSION` file for independent versioning.

---

## 🚀 Accelerator Packs

Accelerator Packs are **pre-composed bundles** that let you import an entire vertical with a single `owl:imports` statement.

| Pack | Import URI | What's included |
|------|-----------|-----------------|
| **Logistics** | `https://www.kairosflow.ai/ont/accelerator/logistics#` | DCSA, MMT, BSP, TIC, IMO, WCO, Sustainability |
| **Financial Services** | `https://www.kairosflow.ai/ont/accelerator/financial-services#` | FIBO foundations + BSP |

```turtle
# Example — import the entire logistics suite in one line
<http://example.com/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/accelerator/logistics#> .
```

See [`ontology-reference-models/accelerator-packs/`](ontology-reference-models/accelerator-packs/) for details.

---

## 🚀 Quick Start

### For Customer Projects

**Option 1: Git Submodule (Recommended)**
```bash
# Add reference models to your project
cd my-customer-ontology-project
git submodule add https://github.com/Cnext-eu/kairos-ontology-referencemodels.git reference-models
git submodule update --init --recursive

# Pin to specific version
cd reference-models
git checkout v1.0.0
cd ..
git add reference-models
git commit -m "Pin reference-models to v1.0.0"
```

**Option 2: Direct Clone**
```bash
# Clone reference models
git clone --branch v1.0.0 https://github.com/Cnext-eu/kairos-ontology-referencemodels.git
```

### Validate Reference Models

Install the [kairos-ontology-toolkit](https://github.com/Cnext-eu/kairos-core-ontology-hub):

```bash
pip install kairos-ontology-toolkit
```

Validate all ontologies:

```bash
# If using submodule
kairos-ontology validate \
  --ontologies reference-models/ontologies \
  --shapes reference-models/shapes

# Test catalog resolution
kairos-ontology catalog-test --catalog reference-models/catalog-v001.xml
```

---

## 📚 Core Ontologies

### core.ttl - Kairos Core Model

Defines fundamental business entities for the Kairos platform:

**Classes:**
- `Customer` - Customer entity with properties (name, email, phone)
- `Order` - Order transaction with orderDate, totalAmount, status
- `Product` - Product catalog item with SKU, price, category
- `Service` - Service offering (abstract class)
  - `ConsultingService` - Professional consulting services
  - `TechnicalService` - Technical implementation services
  - `TrainingService` - Training and education services
- `Supplier` - Supplier entity with contact information

**Object Properties:**
- `hasCustomer` - Links Order to Customer
- `hasProduct` - Links Order to Product
- `hasSupplier` - Links Product to Supplier

**Data Properties:**
- Customer: `name`, `email`, `phone`
- Order: `orderDate`, `totalAmount`, `status`
- Product: `sku`, `price`, `category`
- Service: `duration`, `deliveryMode`

See [ontologies/core.ttl](ontologies/core.ttl) for full specification.

---

## 🔒 Validation

### SHACL Shapes

SHACL constraints enforce data quality:

**shapes/core.shacl.ttl**
- Customer must have exactly one `name` (string, max 200 chars)
- Customer email must match email pattern
- Order `totalAmount` must be >= 0
- Product SKU must be unique and non-empty

### 3-Level Validation

CI/CD enforces:
1. **Syntax**: Valid Turtle/RDF syntax
2. **SHACL**: All SHACL constraints pass
3. **Consistency**: No logical contradictions

---

## 🌐 SKOS Mappings

### Schema.org Alignment

[mappings/schema-org.ttl](mappings/schema-org.ttl) provides concept alignments:

```turtle
kairos:Customer owl:sameAs schema:Customer ;
    skos:closeMatch schema:Person, schema:Organization .

kairos:Order owl:sameAs schema:Order ;
    skos:relatedMatch schema:Invoice .

kairos:Product owl:sameAs schema:Product ;
    skos:relatedMatch schema:Offer .
```

**Benefits:**
- Enables integration with Schema.org-based systems
- Supports semantic search and reasoning
- Facilitates data exchange with external platforms

---

## 📦 FIBO Integration

### Financial Industry Business Ontology

[ontologies/authoritative-ontologies/FIBO/](ontology-reference-models/authoritative-ontologies/FIBO/) contains 300+ FIBO Q4 2025 ontologies:

- **fibo-fnd**: Foundations (agents, organizations, people)
- **fibo-fbc**: Business Contracts
- **fibo-be**: Business Entities (legal entities, corporations)

**XML Catalog Resolution:**

[catalog-v001.xml](ontology-reference-models/catalog-v001.xml) maps FIBO URIs and all derived-ontology URIs to local files:

```xml
<uri name="https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/"
     uri="ontologies/authoritative-ontologies/FIBO/edmcouncil-fibo-da9e773/FND/AgentsAndPeople/Agents.rdf"/>
```

This enables offline development and consistent import resolution.

---

## 📊 Versioning

### Semantic Versioning

Reference models follow [SemVer 2.0.0](https://semver.org/):

**Global version** — tracked in the root `VERSION` file and used for release tags.

**Per-ontology versioning** — each derived ontology and accelerator pack has its own `VERSION` file (e.g. `derived-ontologies/DCSA/VERSION`) so individual suites can evolve independently.

**MAJOR.MINOR.PATCH** (e.g., `1.0.0`)

- **MAJOR**: Breaking changes to core ontology structure
  - Remove classes or properties
  - Change cardinality constraints
  - Modify domain/range restrictions

- **MINOR**: Backward-compatible additions
  - New classes or properties
  - New SHACL constraints (non-breaking)
  - New SKOS mappings

- **PATCH**: Bug fixes and documentation
  - Fix typos in labels/comments
  - Update SHACL error messages
  - Documentation improvements

### Version Tags

```bash
# List all versions
git tag

# Checkout specific version
git checkout v1.0.0

# Upgrade to latest
git checkout main
git pull
```

---

## 🔄 Update Strategy

### For Customer Projects Using Submodules

```bash
# Update to latest version
cd my-project/reference-models
git fetch --tags
git checkout v1.1.0  # Or specific tag
cd ..
git add reference-models
git commit -m "Update reference-models to v1.1.0"

# Validate before deployment
kairos-ontology validate --all
```

### Breaking Changes

When a new MAJOR version is released:
1. Review CHANGELOG.md for breaking changes
2. Update customer extensions if affected
3. Revalidate all customer ontologies
4. Test projection generation
5. Deploy to staging environment first

---

## 🤝 Contributing

Reference models are maintained by the Kairos Ontology Team. 

**For Kairos Team Members:**

1. Create feature branch: `git checkout -b feature/add-invoice-class`
2. Edit ontologies and shapes
3. Validate locally: `kairos-ontology validate --all`
4. Update CHANGELOG.md
5. Update VERSION if needed
6. Open Pull Request
7. Get 2 approvals from ontology team
8. Merge to main
9. Create release tag (if version changed)

**For External Contributors:**

External contributions are welcome! Please:
1. Open an issue describing the proposed change
2. Wait for ontology team feedback
3. Follow the PR process above

---

## 📖 Examples

### Example 1: Basic Import

```turtle
@prefix kairos: <https://www.kairosflow.ai/ont/core#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Import Kairos core ontology
<http://example.com/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/core> .

# Use Kairos classes
:acme-customer-1 a kairos:Customer ;
    kairos:name "ACME Corp" ;
    kairos:email "contact@acme.com" .
```

### Example 2: Extend with Subclass

```turtle
# Extend Kairos Product with specific product type
:SoftwareProduct a owl:Class ;
    rdfs:subClassOf kairos:Product ;
    rdfs:label "Software Product" ;
    rdfs:comment "Software license or subscription product" .

:SoftwareProduct rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty :licenseType ;
    owl:someValuesFrom xsd:string
] .
```

See [examples/](examples/) for more detailed usage patterns.

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Format | OWL 2 / Turtle | - |
| Validation | SHACL | 1.0 |
| Catalog | OASIS XML Catalogs | 1.1 |
| CI/CD | GitHub Actions | - |
| Toolkit | kairos-ontology-toolkit | 1.0.0+ |
| External | FIBO Q4 2025 | 300+ files |

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 📞 Contact

- **Ontology Team:** ontology@kairos.ai
- **Issues:** [GitHub Issues](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Cnext-eu/kairos-ontology-referencemodels/discussions)

For questions about using these models in customer projects, contact the Ontology Team.

---

## 🔗 Related Repositories

- **[kairos-core-ontology-hub](https://github.com/Cnext-eu/kairos-core-ontology-hub)** - Toolkit development and testing
- **[kairos-ontology-toolkit](https://pypi.org/project/kairos-ontology-toolkit/)** - CLI for validation and projection
- **[kairos-customer-template](https://github.com/Cnext-eu/kairos-customer-template)** - Template for customer projects

---

**Current Version:** 1.2.0 | **Last Updated:** 2026-05-16
