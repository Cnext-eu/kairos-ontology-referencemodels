# Contributing to Kairos Reference Models

Thank you for your interest in contributing! This project is part of the
**Kairos Community Edition** by [Cnext.eu](https://cnext.eu).

## Developer Certificate of Origin (DCO)

All contributions must be signed off under the
[Developer Certificate of Origin v1.1](https://developercertificate.org/).

By adding a `Signed-off-by` line to your commit messages, you certify that you
wrote the content (or have the right to submit it) and that you agree to release
it under the project's Apache 2.0 license.

```bash
git commit -s -m "ontology: add new domain entity"
```

This produces a commit message like:

```
ontology: add new domain entity

Signed-off-by: Your Name <your.email@example.com>
```

> **Tip:** Configure git to sign off automatically:
> `git config --global format.signOff true`

## Getting started

### Prerequisites

- Python 3.12+ (for the validation and versioning scripts)
- Git

### Setup

```bash
git clone https://github.com/Cnext-eu/kairos-ontology-referencemodels.git
cd kairos-ontology-referencemodels
```

### Validating your changes

Run the tier-1 gate before opening a PR:

```bash
python scripts/check_all.py
```

`check_all.py` parses `.github/workflows/validate.yml` and runs the `validate` job's
steps locally, in CI order — the workflow is the single source of truth, so the local
gate cannot drift from CI. It covers structure, versions, archetypes, patterns,
generated docs, and the pytest suite, all without installing the toolkit.

On a green run it prints the tier-2 contract command (`uv sync --extra dev` + the
toolkit contract/conformance tests), which verifies the pinned toolkit can actually
read this bundle. Run tier 2 as well when you change any published contract surface
(see `kairos_ontology_referencemodels/ontology-reference-models/contract-manifest.yaml`). CI remains the authoritative
gate on every push and pull request.

## Ontology conventions

- All ontology files use Turtle (`.ttl`) syntax.
- Every ontology MUST declare an `owl:Ontology` with `rdfs:label` and
  `owl:versionInfo`.
- Every `owl:Class` must have `rdfs:label` and `rdfs:comment`.
- Every property must have `rdfs:domain`, `rdfs:range`, and `rdfs:label`.
- **Make relationships explicit.** Typed party/location roles declare a generic
  navigable parent via `rdfs:subPropertyOf` (e.g.
  `:hasConsignor rdfs:subPropertyOf :hasParty`, range a party/location
  supertype). When a referenced entity exists as an `owl:Class` in the model,
  model the link as an `owl:ObjectProperty` rather than a bare `*Ref` / `*Id`
  string scalar (keep the scalar only as a denormalised passthrough if needed).
  See the BSP `party` → `:hasAddress` pattern. The structure validator emits
  advisory `⚠` hints for likely implicit relationships.
- Naming: PascalCase for classes, camelCase for properties.
- When changing ontology content, bump the version and archive the previous
  version (see `scripts/version_manager.py` and `scripts/archive_version.py`).
- Every derived `owl:Class` should be backed by its cited standard.

## Cross-module references and `owl:imports`

**If your module asserts `rdfs:domain` against a class from another module, import that
module.** Declaring the `@prefix` is not enough. Without the import the class is never
typed in your module's graph, so the property hangs off an untyped resource — and a
consumer working in the data domain that loads your module cannot offer that class as an
anchor at all. Enforced by `validate_structure.py` check 10.

A leaf module must import the specific sibling it references, **never its vendor root**.
Importing the root pulls the whole vendor tree into every downstream consumer.

### Why `rdfs:range` is treated differently

An unimported `rdfs:range` only warns. This is deliberate and was measured, so please
don't "fix" the warnings in bulk.

The consuming toolkit derives each data domain's alignment pool from the **transitive**
`owl:imports` closure. So every import you add widens what a client hub is offered.
Requiring imports for ranges as well meant 70 imports rather than 15 and pushed the
classes offered across the logistics domains from 729 to 1805 — handing the `compliance`
domain 92 classes where it had 5, most of them from modules it has no relationship with.

The distinction that matters:

- a dangling **domain** hides a property from the class it belongs to, and the widening
  it costs is real dependency (`financial` sees `CommercialTransaction` because its
  properties are domained on it);
- a dangling **range** only leaves the range class untyped locally — the property is
  still discoverable on its own domain class — and importing for it drags in modules
  that have no dependency relationship.

This is what the "cross-domain references use untyped ranges" convention in the vendor
READMEs is protecting. It is load-bearing, not stale. Import a range target only when a
consumer genuinely needs to resolve the range class from your module, and say why.

### Cycles

Sibling import cycles do not fail the gate: both this repo's loader and the consumer's
guard on already-visited paths, so a cycle cannot drop triples.

They are still worth avoiding, for a reason the gate cannot see. BSP used to cycle
(`commercial → financial → commercial`) and that one edge made all four BSP modules
mutually reachable, so any data domain importing one was offered all four — 352 extra
classes. If you find yourself adding an import that closes a cycle, check whether the
property is simply in the wrong module: `:relatedToShipment` was domained on
`fin:Invoice` while living in `commercial`, and moving it to `financial` removed the
cycle rather than papering over it.

## How to contribute

### Reporting bugs

Open a [GitHub Issue](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/new/choose)
with steps to reproduce, the affected ontology or accelerator pack, and the
reference models version.

### Suggesting features

Open a GitHub Issue with the `enhancement` label describing the use case, a
proposed solution (if any), and alternatives considered.

### Submitting a pull request

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-improvement
   ```
2. Make your changes — follow the ontology conventions above.
3. Run `python scripts/check_all.py` and fix any failures.
4. Commit with DCO sign-off: `git commit -s`
5. Push and open a Pull Request against `main`.

### Branch naming

| Prefix | Use for |
|--------|---------|
| `feature/*` (or `feat/*`) | New ontologies / domains / capabilities |
| `fix/*` | Bug fixes targeting the next release |
| `chore/*` | Maintenance, dependencies, CI |
| `docs/*` | Documentation only |

Never commit to `main` directly — always branch + PR.

### Commit message convention

| Prefix | When |
|--------|------|
| `ontology:` | Ontology file changes |
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `chore:` | Maintenance, dependencies, CI |
| `docs:` | Documentation only |

### PR checklist

- [ ] `python scripts/check_all.py` passes (tier-1 gate)
- [ ] Ontology version bumped + old version archived (if content changed)
- [ ] DCO sign-off on all commits
- [ ] No secrets, credentials, or PII in labels, comments, or fixtures
- [ ] No proprietary or client-specific content

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
Please read it before participating.

## License

By contributing, you agree that your contributions will be licensed under the
[Apache License 2.0](LICENSE).
