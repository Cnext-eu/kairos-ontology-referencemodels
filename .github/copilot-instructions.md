# Copilot Instructions — Kairos Ontology Reference Models

## Repository Purpose

This repository contains **reference ontologies** derived from international standards for use in Kairos client deployments. Each ontology must be strictly aligned with its cited standard — no invented content.

## Key Principle

> **Only include classes that are explicitly defined or enumerated in the cited standard.**
> Classes that are "common knowledge" but not in the standard belong in client-specific ontologies, not here.

## Repository Structure

```
ontology-reference-models/
├── derived-ontologies/       # Standards-based ontologies
│   ├── BSP/                  # Baltic Shipping Procedures
│   ├── DCSA/                 # DCSA Information Model (journey-based)
│   ├── IMO/                  # IMO FAL/GISIS
│   ├── MMT/                  # UN/CEFACT Multimodal Transport
│   ├── Sustainability/       # ISO 14083 / GLEC / EU MRV
│   ├── TIC/                  # TIC 4.0 / BSI PAS 4000
│   └── WCO/                  # WCO Data Model 3.10.0
├── accelerator-packs/        # Sector-specific bundles
│   ├── logistics/
│   └── financial-services/
└── catalog-v001.xml          # OWL catalog for URI resolution
```

## Conventions

### Ontology Files
- Format: Turtle (.ttl)
- Each module is a standalone `owl:Ontology`
- Root ontology imports sub-modules via `owl:imports`
- Required metadata: `dcterms:title`, `dcterms:description`, `dcterms:source`, `owl:versionInfo`, `dcterms:created`, `dcterms:modified`
- Include `rdfs:seeAlso` with URL to official standard documentation

### Versioning
- Semantic versioning (MAJOR.MINOR.PATCH)
- Version in both `owl:versionInfo` (in .ttl) and `VERSION` file
- Must be consistent — validated by `scripts/version_manager.py check`

### Namespace Pattern
- Base: `https://www.kairosflow.ai/ont/`
- Example: `https://www.kairosflow.ai/ont/tic/handling-operations#`

### Validation
- Structure: `python scripts/validate_structure.py` (211 checks)
- Versions: `python scripts/version_manager.py check` (56 versions)
- Both must pass before committing

## Skills Available

### Ontology Audit (`.github/skills/ontology-audit.md`)
Use when adding/modifying classes to verify alignment with the cited standard. Ensures no invented content enters the reference models.

## Common Tasks

### Adding a new class
1. Verify it exists in the cited standard (exact name or clear enumeration)
2. Add with proper `rdfs:label`, `rdfs:comment` citing the standard
3. Run validation
4. Commit

### Auditing an ontology
1. Follow `.github/skills/ontology-audit.md` process
2. Research the standard's official data model
3. Flag invented classes for removal
4. Flag missing standard concepts for addition

### Adding a new standard
1. Create folder under `derived-ontologies/`
2. Create root .ttl, VERSION, README.md
3. Decompose into domain modules (one .ttl per domain)
4. Add to `catalog-v001.xml`
5. Run validation
