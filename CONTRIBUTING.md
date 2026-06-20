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

Run the structure validation before opening a PR:

```bash
py scripts/validate_structure.py
```

The same check runs automatically in CI on every push and pull request via
`.github/workflows/validate.yml`.

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
3. Run `py scripts/validate_structure.py` and fix any failures.
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

- [ ] `py scripts/validate_structure.py` passes
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
