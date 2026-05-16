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
├── authoritative-ontologies/ # Upstream standards (read-only reference)
│   └── FIBO/                 # EDM Council FIBO (current/ + archive/)
├── accelerator-packs/        # Sector-specific bundles
│   ├── logistics/
│   └── financial-services/
├── catalog-v001.xml          # OWL catalog for URI resolution
└── VERSIONING.md             # Versioning strategy documentation
```

Each ontology folder uses the **current/archive** layout:
```
<ontology>/
  VERSION          ← semver string
  README.md
  current/         ← active .ttl files (this is what gets validated)
  archive/         ← frozen snapshots of previous versions (never edited)
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
- **Every content change requires a version bump** — archive first, then bump
- Workflow: `archive_version.py` → `version_manager.py bump` → `version_manager.py sync` → validate

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

### Ontology Versioning (`.github/skills/ontology-versioning.md`)
Use when making any content change to an ontology. Guides the archive → bump → sync → validate workflow. Ensures old versions are preserved and `owl:versionInfo` stays consistent.

## Common Tasks

### Adding a new class
1. Verify it exists in the cited standard (exact name or clear enumeration)
2. Add with proper `rdfs:label`, `rdfs:comment` citing the standard
3. Run validation
4. Follow versioning workflow (archive → bump → sync → validate → commit)

### Modifying an existing ontology
1. Archive the current version: `python scripts/archive_version.py <ONTOLOGY>`
2. Make changes in `<ontology>/current/`
3. Bump version: `python scripts/version_manager.py bump <ONTOLOGY> <patch|minor|major>`
4. Sync: `python scripts/version_manager.py sync`
5. Validate: `python scripts/validate_structure.py && python scripts/version_manager.py check`
6. Commit

### Auditing an ontology
1. Follow `.github/skills/ontology-audit.md` process
2. Research the standard's official data model
3. Flag invented classes for removal
4. Flag missing standard concepts for addition

### Adding a new standard
1. Create folder under `derived-ontologies/` with `current/` and `archive/` subfolders
2. Create root .ttl inside `current/`, VERSION and README.md at ontology root
3. Decompose into domain modules (one .ttl per domain) inside `current/`
4. Add to `catalog-v001.xml` (paths include `current/`)
5. Run validation
