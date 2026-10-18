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

After re-vendoring IATA, regenerate the two files derived from it:
`python scripts/generate_iata_domain_patch.py` and
`python scripts/generate_uncefact_iata_alignment.py`.

After any mirror update, run the bundle conformance suite — it is what proves the closure
still resolves offline:

```bash
export KAIROS_TOOLKIT_SRC="$(uv run python -c 'import kairos_ontology, pathlib; print(pathlib.Path(kairos_ontology.__file__).parent.parent)')"
uv run --extra dev python -m pytest tests/test_bundle_conformance.py -v
```

### Refreshing reference data

This repository ships **reference data** as well as ontologies: the members of code lists
that standards bodies publish (`authoritative-ontologies/UNCEFACT/`: UNECE Rec 19 transport
modes, Rec 20 units of measure, Rec 21 package types and more; `authoritative-ontologies/ISO4217/`:
ISO 4217 currencies from SIX, refreshed with `python scripts/download_iso4217.py [--check]`).
SIX amends ISO 4217 several times a year; a newly withdrawn currency becomes `owl:deprecated`
and is never removed. Ontology mirrors change when a
release is published, and you hear about it. Code lists are revised **in place**: the
UN/CEFACT vocabulary endpoint serves one unversioned dump with no release to watch. A
vendored snapshot therefore goes stale silently, and **must be refreshed periodically with
the scripts**:

```bash
# Has upstream changed since the vendored snapshot? (exit 1 if so)
python scripts/download_uncefact_codelists.py --check

# Refresh: moves current/ to archive/<old download date>/, rewrites the extract,
# the OWL patch and METADATA.txt, and regenerates UNCEFACT-IATA-alignment.ttl.
# Writes nothing when upstream is byte-identical.
python scripts/download_uncefact_codelists.py

# Regenerate from the same upstream after changing the script itself
python scripts/download_uncefact_codelists.py --force
```

A snapshot's version is its download date. It is recorded in `METADATA.txt` (with the
dump's sha256), in the extract header, and as `owl:versionInfo` on the OWL patch and on
each code-list class. `tests/test_reference_data.py` fails if they disagree.

After a refresh:

1. **Diff the extract.** A code that is **removed** upstream is a breaking change for every
   hub that stores it; call it out as breaking in `CHANGELOG.md`. Added codes and changed
   names are additive.
2. Run the full gate (the bundle conformance suite proves the closure still resolves).
3. Bump the root `VERSION` and add a CHANGELOG entry naming the snapshot date.

**Cadence.** The `reference-data-freshness` workflow runs the refresh on the 1st of each
month and opens a PR when upstream changed; that PR still needs steps 1–3. Run `--check` by
hand before a release.

If a refresh prints `NOTE erratum obsolete`, upstream has fixed a known error: delete that
entry from `ERRATA` in the script. If it fails with `erratum no longer matches upstream`,
upstream changed a corrected value: review the new value before deciding to keep, change or
drop the erratum. Report every new upstream error to UN/CEFACT
(`opensource.unicc.org/un/unece/uncefact`) as well as adding an erratum.

Never hand-edit the generated files (`UNCEFACT-CodeLists.ttl`,
`UNCEFACT-CodeLists.owl-patch.ttl`, `UNCEFACT-IATA-alignment.ttl`, `METADATA.txt`). To
vendor another standards-body list, add it to `CODE_LISTS` in the script and to
`REFERENCE_DATA_MODULES` in `tests/test_reference_data.py` if it lives in a new module.

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
| `scripts/download_iso4217.py` | Refresh ISO 4217 currency codes from SIX (`--check`, auto-archives old) |
| `scripts/download_uncefact_codelists.py` | Refresh UN/CEFACT reference data (`--check`, auto-archives old) |
| `scripts/generate_uncefact_iata_alignment.py` | Regenerate IATA → UNECE code links |
| `scripts/generate_iata_domain_patch.py` | Regenerate the IATA `rdfs:domain` sidecar |
