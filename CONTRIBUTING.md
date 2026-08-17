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

## Reach: two mechanisms at two different layers

Almost every "the model is missing X" report against this pack has turned out to be a
reach failure rather than a modelling gap. The term exists; the consumer cannot get to
it. There are two independent mechanisms, they live at different layers, and **neither
substitutes for the other** — fixing one will not fix the other, and each has its own
gate.

| | `owl:imports` (graph layer) | data-domain routing (blueprint layer) |
|---|---|---|
| **Question it answers** | "Is this class *typed* in my module's graph?" | "Is this class *offered* to a client-hub domain?" |
| **Declared in** | the module's own `.ttl` header | `data-domains.yaml` |
| **Consumed by** | any RDF reader resolving domain/range | the toolkit's alignment pool |
| **Failure mode** | `rdfs:domain`/`rdfs:range` silently dangles; the property becomes invisible to "which properties does class X carry" | the class is absent from the domain's pool; a table anchored to it is refused as `outside_pool` |
| **Gate** | `validate_structure.py` check 10 | `validate_archetypes.py` check 8 + `test_every_term_declaring_module_reaches_a_data_domain` |
| **Real incident** | gh#97 — `bsp:TradeParty` resolved 9 properties, not 13 | gh#98 — `mmt/cargo#Dimension` unreachable from `equipment` |

The rule for the graph layer is unconditional: **if your module asserts `rdfs:domain`
or `rdfs:range` against a class from another module, import that module.** Declaring
the `@prefix` is not enough. A leaf module must import the specific sibling it
references, never its vendor root — importing the root pulls the whole vendor tree into
every downstream consumer and defeats per-domain scoping.

Cyclic sibling imports are fine. BSP genuinely cycles (`commercial → financial →
commercial`); both loaders guard on already-visited paths, so a cycle costs at most one
diagnostic and cannot drop triples.

### Choosing between a domain import and a bridge

At the blueprint layer you have two options, and the choice is a modelling statement,
not a mechanical one:

- **Add the module to a domain's `imports`** when that domain *owns* the grain. This is
  the right move when a module is owned by nobody yet — and it is the *only* move then,
  because a bridge needs an owning domain to point away from.
- **Declare a `cross_domain_relationships` bridge** when a domain needs to *reference*
  a class another domain owns. A bridge says "may reference, does not own". Importing
  the other domain's module instead reads as co-ownership and trips the consumer's
  cross-domain duplicate check.

Two consequences worth knowing before you pick:

- A bridge exposes **exactly its `range_class_uri`**, not the whole module. Three
  classes needed by two domains is six bridge entries, not one import.
- A domain import exposes **every class in the module**, including ones the domain's own
  `does_not_own` statement excludes. Where that is unavoidable, say so in the import's
  `note` and keep `does_not_own` as the governing rule.

A `status: new-bridge` bridge also needs its property to exist — add it to
`derived-ontologies/SupplyChain/current/supply-chain.ttl`, in the `supply-chain#`
namespace. Keep those properties free of qualifiers you cannot cite: a bridge property
is a Kairos routing declaration, not a claim about the upstream standard.

## Runbook: adding an industry model

Adding RAIL and IATA ONE Record touched about fifteen files and six were missed, every
one in a surface with no machine reader. Work the levels in order; the right-hand column
is what fails if you skip one.

| # | Level | What to do | Caught by |
|---|---|---|---|
| 1 | Module `.ttl` | Write modules under `derived-ontologies/<VENDOR>/current/<module>/`. Give each its own namespace and `owl:versionInfo`. Add `owl:imports` for every module you assert domain/range against. | `validate_structure.py` checks 1–7, 10 |
| 2 | Vendor root | `<vendor>.ttl` imports every module. Keep it a **pure aggregator** — no terms of its own, or they end up in a namespace no domain can route. | check 10 + the routing test |
| 3 | `catalog-v001.xml` | One `<uri>` entry per module IRI → file path. Offline resolution depends on it. | `test_every_manifest_module_is_catalogued` |
| 4 | Accelerator `.ttl` | `accelerator-packs/<pack>/current/*-accelerator.ttl` imports the vendor root. | `test_every_include_is_imported_by_the_accelerator` |
| 5 | `manifest.yaml` | Add to `package.includes` (or `references` for catalogued-but-not-bundled). This is the single hand-edited registry every other surface is checked against. | the fan-out tests |
| 6 | `data-domains.yaml` | Route **every term-declaring module** into at least one domain's `imports`. Aggregators are exempt automatically. | `test_every_term_declaring_module_reaches_a_data_domain` |
| 7 | Bridges | Declare `cross_domain_relationships` for classes another domain must reference, and add the property to `supply-chain.ttl`. | `test_every_bridge_class_endpoint_is_in_the_bundle` |
| 8 | Archetypes | Add `ref_model_modules` entries and `core_concepts` with a `tier`. Every `tier: required` concept must be domain-reachable. | `validate_archetypes.py` checks 2, 8 |
| 9 | Versioning | `archive_version.py <VENDOR>` **before** editing, then `version_manager.py bump`/`sync`. See the warning below. | `version_manager.py check` |
| 10 | Generated artifacts | `generate_logistics_inventory.py`, `generate_pack_docs.py`. Never hand-edit their output. | freshness tests |
| 11 | `CHANGELOG.md` + root `VERSION` | Record the change and why. A vendor major may ride a repo minor (MMT 2.0.0 shipped in repo 1.16.0). | review |

> **Archive before you edit, not after.** `archive_version.py` copies the *current
> working tree*, so running it after your edits archives your new content under the old
> version number. If you slip, restore from git: `git archive HEAD <vendor-current-path>`
> and copy that into `archive/<old-version>/`.

## Runbook: changing a data domain or blueprint

Changing `data-domains.yaml` looks local and is not — it is a published contract surface
the toolkit reads directly.

1. **Adding an import to a domain** — assigning ownership. Check the domain's `owns` /
   `does_not_own` prose still holds, and add a `note` explaining why this module belongs
   here. Every module URI must resolve through the catalog.
2. **Adding a bridge** — one entry per (class, domain) pair, `source_domain` = the domain
   that needs reach. The schema is `additionalProperties: false`, so a typo'd key fails
   rather than being ignored. Add the property to `supply-chain.ttl` for
   `status: new-bridge`.
3. **Removing or re-pointing an import** — check no archetype `core_concepts` entry loses
   its last route. `validate_archetypes.py` blocks at `tier: required` and warns below it.
4. **Any change** — re-run `generate_logistics_inventory.py` and
   `generate_pack_docs.py`, then `check_all.py`, then tier 2. `data-domains.yaml` is in
   `contract-manifest.yaml`, so tier 2 is not optional.

Useful while auditing: `validate_archetypes.py --list-single-domain` enumerates concepts
reachable from exactly one domain. Most are fine — one owner is normal — but it is the
list to scan when you suspect the domain that *needs* a class differs from the one that
*owns* it.

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
