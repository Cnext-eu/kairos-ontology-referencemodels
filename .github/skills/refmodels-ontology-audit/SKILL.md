---
name: refmodels-ontology-audit
description: Audit a derived ontology module to verify that every owl:Class is backed by its cited standard. Use when adding/modifying classes, onboarding a new standard, or during compliance reviews.
---

# Ontology Audit Skill

## Purpose

Audit a derived ontology module to verify that every `owl:Class` is backed by its cited standard — no invented or extrapolated content allowed.

## When to Use

- Before releasing a new version of a reference ontology
- After adding or modifying classes in any derived ontology
- When onboarding a new standard into the repository
- During periodic compliance reviews

## Audit Process

### Step 1: Identify the Standard

Read the ontology's `dcterms:source` and `rdfs:seeAlso` to identify the claimed standard(s). For example:
- "TIC4.0 Release 2025.017 / BSI PAS 4000:2026"
- "WCO Data Model 3.10.0"
- "ISO 14083:2023, GLEC Framework"

### Step 2: Research the Standard

Search for the official specification:
- Official website, wiki, or documentation portal
- Published data models, XSD schemas, or OWL/TTL files
- Academic papers or industry whitepapers describing the data model
- Version-specific release notes

Document the **core entities/concepts** defined by the standard.

### Step 3: Class-by-Class Verification

For each `owl:Class` in the ontology, determine:

| Status | Meaning |
|--------|---------|
| ✅ **Backed** | Class directly maps to a named entity/concept in the standard |
| ⚠️ **Derived** | Class is a reasonable decomposition of a standard concept (e.g., subclasses of a generic type that the standard enumerates) |
| ❌ **Invented** | Class has no basis in the standard — our own abstraction |

### Step 4: Identify Missing Concepts

Check if the standard defines core concepts that are **not** in our ontology. These are candidates for addition.

### Step 5: Produce Audit Report

Generate a summary with:

```markdown
## Audit: [Ontology Name]
**Standard:** [cited standard + version]
**Date:** [audit date]

### Backed Classes (✅)
- ClassName — Standard reference

### Derived Classes (⚠️ — acceptable)
- ClassName — Justification

### Invented Classes (❌ — must remove or move to client ontology)
- ClassName — Why it's not in the standard

### Missing from Standard (candidates to add)
- ConceptName — Standard reference

### Recommendations
1. Remove invented classes or move to client-specific ontology
2. Add missing core concepts
3. Update source citations
```

## Rules

1. **Only classes backed by the cited standard belong in the reference ontology**
2. Reasonable subclass decompositions are acceptable IF the standard enumerates them (e.g., HFO, VLSFO, LNG as FuelType subclasses when IMO DCS lists these fuels)
3. Classes that are "common industry knowledge" but NOT in the cited standard must be removed — they belong in client-specific ontologies
4. Party roles are especially suspect — many standards define data exchange formats, not organizational roles
5. When in doubt, check if the standard's data model/schema/XSD explicitly names the entity
6. Always update `dcterms:source` to cite the exact version audited
7. Always add `rdfs:seeAlso` with a URL to the standard's official documentation
8. Bump `owl:versionInfo` and VERSION file after any changes

## Post-Audit Actions

After identifying issues:

1. **Remove** invented classes and their associated properties
2. **Add** missing core concepts from the standard
3. **Rename** classes to match standard terminology (e.g., MoveSequence → Cycle)
4. **Update** `dcterms:source` to exact version string
5. **Add** `rdfs:seeAlso` with official URL
6. **Bump** version in both `.ttl` and `VERSION` file
7. **Update** `README.md` to reflect changes
8. **Run** `python scripts/validate_structure.py` and `python scripts/version_manager.py check`
9. **Commit** with descriptive message

## Example Invocation

> "Audit the TIC ontology — check all classes against TIC 4.0 standard"

> "Verify the DCSA booking module classes are in DCSA BKG v2.0"

> "Check if any classes in the MMT ontology are invented"
