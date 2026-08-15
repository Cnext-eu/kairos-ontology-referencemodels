# Kairos Reference Models

**Centralized repository for Kairos platform canonical ontologies and reference models**

_Part of the [Kairos Community Edition](https://github.com/Cnext-eu) by Cnext.eu_

[![Validation Status](https://github.com/Cnext-eu/kairos-ontology-referencemodels/actions/workflows/validate.yml/badge.svg)](https://github.com/Cnext-eu/kairos-ontology-referencemodels/actions/workflows/validate.yml)
[![Version](VERSION)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

## 🎯 Overview

The Kairos Reference Models repository provides validated, versioned ontologies that serve as the foundation for the Kairos platform and customer-specific implementations. These models define the canonical structure for core business entities and their relationships.

**Key Features:**
- ✅ **Semantic versioning** for stable evolution (per-ontology + global)
- ✅ **Automated validation** on every commit (syntax, SHACL, consistency, structure)
- ✅ **FIBO integration** with 300+ Financial Industry Business Ontology files
- ✅ **8 standard-backed derived ontologies** covering logistics, trade, and sustainability
- ✅ **SupplyChain bridge module** linking the standards into one supply-chain view
- ✅ **Accelerator Packs** — one-import bundles for Logistics and Financial Services
- ✅ **SKOS mappings** for alignment with industry standards (Schema.org)
- ✅ **Git-based distribution** via tags and submodules

---

## 📁 Repository Structure

```
kairos-ontology-referencemodels/
├── kairos_ontology_referencemodels/ontology-reference-models/
│   ├── authoritative-ontologies/      # Official RDF/OWL from standards bodies
│   │   ├── FIBO/                      # FIBO Q4 2025 (300+ files, EDM Council)
│   │   ├── IATA/                      # IATA ONE Record
│   │   ├── OMG-Commons/               # OMG Commons (vocabularies)
│   │   ├── OMG-LCC/                   # OMG Languages, Countries & Codes
│   │   └── W3C-SKOS/                  # W3C SKOS core
│   ├── derived-ontologies/            # Our RDF interpretations of non-RDF standards
│   │   ├── DCSA/                      # Container shipping (1 root + 6 domains)
│   │   ├── MMT/                       # Multi-modal transport (1 root + 10 domains)
│   │   ├── BSP/                       # Buy-Ship-Pay (1 root + 8 domains)
│   │   ├── TIC/                       # Terminal operations (1 root + 8 domains)
│   │   ├── IMO/                       # Maritime regulatory (1 root + 9 domains)
│   │   ├── WCO/                       # Customs & border (1 root + 5 domains)
│   │   ├── Sustainability/            # Carbon & energy (1 root + 2 domains)
│   │   ├── RAIL/                      # TAF TSI rail (1 root + 6 domains)
│   │   └── SupplyChain/               # Cross-standard bridge (defines no new classes)
│   ├── accelerator-packs/             # Pre-composed bundles
│   │   ├── logistics/                 # 11 ontologies for logistics companies
│   │   └── financial-services/        # FIBO FND/BE foundations for financial services
│   ├── blueprints/                    # Opinionated Kairos guidance (not standards)
│   │   ├── archetypes/                # Per-archetype YAML catalogs (e.g. shipping-carrier)
│   │   ├── patterns/                  # Sector-neutral shapes and naming conventions
│   │   └── ontology/                  # Kairos-authored classes where no standard defines the grain
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

The repository ships **8 standard-backed derived ontologies** covering the full logistics, trade, and sustainability value chain:

| # | Ontology | Standard | Focus | Domains |
|---|----------|----------|-------|---------|
| 1 | **DCSA** | DCSA API Standards | Container shipping lifecycle | 6 |
| 2 | **MMT** | UN/CEFACT MMT-RDM | Consignment, movement, cargo, equipment | 10 |
| 3 | **BSP** | ISO 20197-1:2024 | Party, contract, invoice, settlement | 8 |
| 4 | **TIC** | TIC 4.0 | Terminal operations, handling, automotive | 8 |
| 5 | **IMO** | IMO Compendium / FAL / IMDG | Vessel registry, dangerous goods, port-call | 9 |
| 6 | **WCO** | WCO Data Model 3.0 | Customs declarations, trade facilitation | 5 |
| 7 | **Sustainability** | ISO 14083:2023 / GLEC | Emissions, energy, ESG reporting | 2 |
| 8 | **RAIL** | TAF TSI | Train running, path requests, rolling stock, consignment | 6 |

Plus the **SupplyChain** module — a *cross-standard bridge* that defines no new classes of
its own, but composes and links classes across the standards above into one supply-chain
view. Plus **FIBO**, **IATA ONE Record**, **OMG Commons / LCC**, and **W3C SKOS** — 300+
authoritative ontology files vendored verbatim from the standards bodies.

Each derived ontology lives in its own directory under `kairos_ontology_referencemodels/ontology-reference-models/derived-ontologies/` with a `VERSION` file for independent versioning.

---

## 🚀 Accelerator Packs

Accelerator Packs are **pre-composed bundles** that let you import an entire vertical with a single `owl:imports` statement.

| Pack | Import URI | What's included |
|------|-----------|-----------------|
| **Logistics** | `https://www.kairosflow.ai/ont/accelerator/logistics#` | DCSA, MMT, BSP, TIC, IMO, WCO, Sustainability, SupplyChain, RAIL |
| **Financial Services** | `https://www.kairosflow.ai/ont/accelerator/financial-services#` | FIBO FND & BE foundations |

```turtle
# Example — import the entire logistics suite in one line
<http://example.com/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/accelerator/logistics#> .
```

See [`kairos_ontology_referencemodels/ontology-reference-models/accelerator-packs/`](kairos_ontology_referencemodels/ontology-reference-models/accelerator-packs/) for details.

---

## 🧭 Blueprints (opinionated guidance)

The repository ships a **third content tier** alongside the authoritative and derived ontologies:

| Tier | Folder | What it is |
|------|--------|------------|
| Authoritative | `authoritative-ontologies/` | Official RDF/OWL published by standards bodies (e.g. FIBO). Verbatim. |
| Derived | `derived-ontologies/` | Kairos RDF interpretations of non-RDF standards (DCSA, MMT, BSP, …). Faithful to the source. |
| **Blueprint** | **`blueprints/`** | **Opinionated Kairos guidance** layered on top of the ref models — not a standard. Versioned independently. |

The first blueprint shipping today is the **archetype catalog** under [`blueprints/archetypes/`](kairos_ontology_referencemodels/ontology-reference-models/blueprints/archetypes/). Each YAML file describes the ref-model modules and core concepts a given business archetype is expected to support. Three archetypes ship today: `shipping-carrier` (186 core concepts across 21 business areas), `freight-forwarder` (34 core concepts), and `unit-load-carrier` (170 core concepts across 19 business areas, covering non-containerised ro-ro / short-sea operations).

The repository also ships a **pattern library** under [`blueprints/patterns/`](kairos_ontology_referencemodels/ontology-reference-models/blueprints/patterns/) — sector-neutral modelling craft (shapes and naming conventions) harvested from client hub implementations, distinct from the archetype catalog and not yet part of its cross-repo contract.

A third blueprint module, [`blueprints/ontology/`](kairos_ontology_referencemodels/ontology-reference-models/blueprints/ontology/), holds **Kairos-authored OWL classes** for business grains that a standards audit has shown no installed standard expresses. It has the highest bar of the three — see that folder's README for the admission criteria. It ships `TransportOrder` and `CarrierReservation` today.

Each archetype may be paired with a **sector discovery script** under
`accelerator-packs/<pack>/discovery/<archetype-id>.md` holding the SME
interview questions and lifecycle / cardinality guidance the ontology
itself cannot infer. The shipping-carrier discovery script lives at
[`accelerator-packs/logistics/discovery/shipping-carrier.md`](kairos_ontology_referencemodels/ontology-reference-models/accelerator-packs/logistics/discovery/shipping-carrier.md).

Both are consumed by the `kairos-design-discovery` skill in the
[`kairos-ontology-toolkit`](https://github.com/Cnext-eu/kairos-ontology-toolkit) repository.

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
git checkout v1.18.0
cd ..
git add reference-models
git commit -m "Pin reference-models to v1.18.0"
```

**Option 2: Direct Clone**
```bash
# Clone reference models
git clone --branch v1.18.0 https://github.com/Cnext-eu/kairos-ontology-referencemodels.git
```

### Validate Reference Models

Validation is done with the
[kairos-ontology-toolkit](https://github.com/Cnext-eu/kairos-ontology-toolkit) consumer
CLI, pointed at this repo's `kairos_ontology_referencemodels/ontology-reference-models/` layout and its
[`catalog-v001.xml`](kairos_ontology_referencemodels/ontology-reference-models/catalog-v001.xml) import-resolution catalog.
See that repo's README for exact `kairos-ontology validate` flags.

> **Contributors** — to validate changes *inside this repository*, skip the toolkit and
> run the local gate instead:
>
> ```bash
> python scripts/check_all.py        # tier-1 toolkit-free gate
> ```
>
> See [CONTRIBUTING.md](CONTRIBUTING.md) and the *✅ Validation gate* section below for
> the contract (tier-2) tests.

---

## 📦 FIBO Integration

### Financial Industry Business Ontology

[authoritative-ontologies/FIBO/](kairos_ontology_referencemodels/ontology-reference-models/authoritative-ontologies/FIBO/) contains 300+ FIBO Q4 2025 ontologies:

- **fibo-fnd**: Foundations (agents, organizations, people)
- **fibo-fbc**: Business Contracts
- **fibo-be**: Business Entities (legal entities, corporations)

**XML Catalog Resolution:**

[catalog-v001.xml](kairos_ontology_referencemodels/ontology-reference-models/catalog-v001.xml) maps FIBO URIs and all derived-ontology URIs to local files.
FIBO uses a URI-prefix rewrite into the vendored tree (`authoritative-ontologies/FIBO/current/fibo/`):

```xml
<rewriteURI uriStartString="https://spec.edmcouncil.org/fibo/ontology/"
            rewritePrefix="authoritative-ontologies/FIBO/current/fibo/"/>
```

So `https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/` resolves to
`kairos_ontology_referencemodels/ontology-reference-models/authoritative-ontologies/FIBO/current/fibo/FND/AgentsAndPeople/Agents/`
(a directory listing).

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
git checkout v1.18.0

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
3. Validate locally: `python scripts/check_all.py` (see *✅ Validation gate* below)
4. Update CHANGELOG.md
5. Update VERSION if needed
6. Open Pull Request
7. Get 2 approvals from ontology team
8. Merge to main
9. Create release tag (if version changed)

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide.

**For External Contributors:**

External contributions are welcome! Please:
1. Open an issue describing the proposed change
2. Wait for ontology team feedback
3. Follow the PR process above

---

## ✅ Validation gate

This repo validates itself in two tiers. **Run the tier-1 gate before opening a PR.**

### Tier 1 — toolkit-free local gate

```bash
python scripts/check_all.py
```

Runs every repo-intrinsic check (ontology syntax, structure, catalog, archetypes,
patterns, contract manifest, version consistency, and the unit tests). Depends only on
Python — **not** on the `kairos-ontology-toolkit` it feeds. `check_all.py` derives the
step list from `validate.yml` so there is one source of truth for the gate.

### Tier 2 — cross-repo contract checks

Run only when your change could affect the toolkit contract (catalog scheme, manifest
shape, accelerator-pack layout, blueprint YAML). Needs the pinned toolkit installed:

```bash
uv sync --extra dev
python -m pytest tests/test_toolkit_contract.py tests/test_bundle_conformance.py -v -ra -p no:randomly
```

These are the same tests the `contract` job runs in CI (see
[`.github/workflows/validate.yml`](.github/workflows/validate.yml)).

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

Licensed under the [Apache License 2.0](LICENSE). Part of the **Kairos Community
Edition** by [Cnext.eu](https://cnext.eu). See [NOTICE](NOTICE) for attribution.

This repository also bundles third-party authoritative ontologies (e.g. FIBO)
under their own licenses; those terms continue to apply to the respective files.

See also [CONTRIBUTING](CONTRIBUTING.md), [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md),
and [SECURITY](SECURITY.md).

---

## 📞 Contact

- **Ontology Team:** ontology@kairos.ai
- **Issues:** [GitHub Issues](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Cnext-eu/kairos-ontology-referencemodels/discussions)

For questions about using these models in customer projects, contact the Ontology Team.

---

## 🔗 Related Repositories

- **[kairos-ontology-toolkit](https://github.com/Cnext-eu/kairos-ontology-toolkit)** - Consumer CLI and Python library (validates hubs and projects ontologies)
- **[kairos-customer-template](https://github.com/Cnext-eu/kairos-customer-template)** - Template for customer projects

---

The canonical version lives in [`VERSION`](VERSION) and [`CHANGELOG.md`](CHANGELOG.md).
