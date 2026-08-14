---
name: refmodels-ontology-versioning
description: Manage version increments and archiving when ontology content changes. Use when making any content change to an ontology to ensure old versions are preserved and owl:versionInfo stays consistent.
---

# Ontology Versioning Skill

## Purpose

Manage version increments and archiving when ontology content changes. Ensures old versions are preserved side-by-side and all version metadata stays consistent.

## When to Use

- After making any change to `.ttl` files in a derived ontology or accelerator pack
- When updating an authoritative ontology (e.g., downloading a new FIBO release)
- Before releasing a new version of the repository

## Key Rule

> **Every content change to an ontology requires a version bump.**
> Archive the old version first, then bump, then sync all `owl:versionInfo` strings.

## Versioning Workflow (Derived Ontologies)

### Step 1: Archive the Current Version

Before making changes, snapshot the current state:

```bash
python scripts/archive_version.py <ONTOLOGY>
```

This copies `<ontology>/current/` → `<ontology>/archive/<version>/` as a frozen snapshot.

Example:
```bash
python scripts/archive_version.py DCSA
# ✓ DCSA: archived v1.0.0 (6 items → archive/1.0.0/)
```

### Step 2: Make Your Changes

Edit `.ttl` files in `<ontology>/current/`. Follow the standard conventions:
- Add/remove/modify `owl:Class`, properties, or metadata
- Update `dcterms:modified` date
- Ensure all classes cite their source standard

### Step 3: Bump the Version

Choose the appropriate semver increment:

| Change Type | Bump | Example |
|-------------|------|---------|
| New classes added (backward compatible) | `minor` | 1.0.0 → 1.1.0 |
| Bug fix, typo, metadata correction | `patch` | 1.0.0 → 1.0.1 |
| Breaking change (removed classes, renamed IRIs) | `major` | 1.0.0 → 2.0.0 |

```bash
python scripts/version_manager.py bump <ONTOLOGY> <major|minor|patch>
```

### Step 4: Sync `owl:versionInfo`

Update all `.ttl` files to match the new VERSION:

```bash
python scripts/version_manager.py sync
```

### Step 5: Validate

```bash
python scripts/validate_structure.py
python scripts/version_manager.py check
```

Both must pass (211 structure checks + 56 version consistency checks).

### Step 6: Commit

Commit with a message describing the change and new version:

```
feat(DCSA): add VesselSharing class from DCSA IM 2025.Q1

Bumped DCSA from 1.0.0 → 1.1.0. Previous version archived.
```

## Versioning Workflow (Authoritative Ontologies — FIBO)

```bash
python scripts/download_fibo.py
```

The script automatically:
1. Archives `current/` → `archive/{old_version}/`
2. Downloads the latest release into `current/`
3. Updates `METADATA.txt`

After downloading, update `catalog-v001.xml` if the extracted folder name changed.

**The other mirrors (IATA, OMG-Commons, OMG-LCC, W3C-SKOS) have no script** — archive, re-fetch
and hand-write `METADATA.txt` in the same key order. See
`ontology-reference-models/VERSIONING.md`. Always finish with
`pytest tests/test_bundle_conformance.py`, which proves every closure still resolves offline;
a mirror that silently stops resolving is exactly the v1.16.0 failure (gh#57).

## Folder Structure

```
<ontology>/
  VERSION              ← semver (e.g., "1.2.0")
  README.md            ← documentation
  current/             ← active ontology content
    root-ontology.ttl
    module-a/
    module-b/
  archive/             ← frozen snapshots (never edited)
    1.0.0/
    1.1.0/
```

## Archive Rules

- Archive is **read-only** — never edit files in `archive/`
- Archive is **excluded from validation** — `validate_structure.py` only checks `current/`
- Archive preserves the **exact state** at the time of the version bump
- One archive entry per version — if `archive/1.0.0/` exists, it won't be overwritten

## Checking Versions

```bash
# List all current versions
python scripts/version_manager.py list

# Verify VERSION files match owl:versionInfo in .ttl files
python scripts/version_manager.py check
```

## Common Mistakes to Avoid

- ❌ Editing `.ttl` files without bumping the version
- ❌ Bumping the version without archiving first (old version is lost)
- ❌ Forgetting to run `sync` after `bump` (VERSION file won't match .ttl)
- ❌ Editing files inside `archive/` (these are frozen snapshots)
- ❌ Committing without running `validate_structure.py` and `version_manager.py check`
