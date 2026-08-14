# Versioning Strategy

This repository uses a **side-by-side versioning** approach. Each ontology
maintains a `current/` folder with the active version and an `archive/` folder
for frozen snapshots of previous versions.

## Folder Layout

```
<ontology>/
  VERSION          ← semver string (e.g., "1.0.0")
  README.md        ← documentation
  current/         ← active ontology content (.ttl files, subfolders)
  archive/         ← frozen snapshots of previous versions
    1.0.0/         ← snapshot taken before bumping to 1.1.0
    1.1.0/         ← snapshot taken before bumping to 1.2.0
```

For authoritative ontologies (FIBO):

```
FIBO/
  current/         ← latest downloaded release
    METADATA.txt   ← version + download date
    edmcouncil-fibo-<hash>/
  archive/         ← previous releases
    master_2025Q4/
    master_2026Q1/
```

## Workflows

### Bumping a derived ontology version

```bash
# 1. Archive the current version
python scripts/archive_version.py DCSA

# 2. Bump the version number
python scripts/version_manager.py bump DCSA minor

# 3. Sync owl:versionInfo in .ttl files
python scripts/version_manager.py sync

# 4. Validate
python scripts/validate_structure.py
python scripts/version_manager.py check
```

### Updating FIBO (authoritative)

```bash
# The download script auto-archives the old version
python scripts/download_fibo.py
```

This will:
1. Move `current/` contents → `archive/{old_version}/`
2. Download new FIBO release into `current/`
3. Update `METADATA.txt`

### Updating the other authoritative mirrors

`scripts/download_fibo.py` is FIBO-specific. IATA, OMG-Commons, OMG-LCC and W3C-SKOS are
vendored **manually**: move `current/` to `archive/{old_version}/`, re-fetch, and hand-write
`METADATA.txt` in the same key order (`source`, `publisher`, `download_date`, `version`,
`release_name`, `release_url`, `license`, `homepage`).

The OMG mirrors are fetched by dereferencing each module IRI with
`Accept: application/rdf+xml` and following `owl:imports` until the closure is closed; the
module lists are recorded in their `METADATA.txt`. Preserve the upstream IRI path layout on
disk so the single `rewriteURI` rule in `catalog-v001.xml` keeps resolving.

After any mirror update, run the bundle conformance suite — it is what proves the closure
still resolves offline:

```bash
export KAIROS_TOOLKIT_SRC="$(uv run python -c 'import kairos_ontology, pathlib; print(pathlib.Path(kairos_ontology.__file__).parent.parent)')"
uv run --extra dev python -m pytest tests/test_bundle_conformance.py -v
```

### Archiving all ontologies at once

```bash
python scripts/archive_version.py --all
```

## Rules

- **VERSION + README stay at ontology root** — they describe the whole lineage
- **Archive is frozen** — never edited, never validated
- **validate_structure.py skips archive/** — only validates `current/`
- **Git tags** continue to mark repo-level milestones (e.g., `v1.3.0`)

## Available Scripts

| Script | Purpose |
|--------|---------|
| `scripts/archive_version.py` | Snapshot `current/` → `archive/{version}/` |
| `scripts/version_manager.py` | List, bump, sync, check versions |
| `scripts/validate_structure.py` | Validate structure (211 checks) |
| `scripts/download_fibo.py` | Download latest FIBO (auto-archives old) |
