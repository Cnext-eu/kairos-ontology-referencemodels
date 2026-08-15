# Kairos Reference Models — Agent Instructions

## What this repository is

This repo **publishes versioned ontology reference models**. It is consumed by
`kairos-ontology-toolkit`, which reads a small contract surface from here.

**This repo is not an ontology hub.** There is no `model/`, no `integration/`, no
`kairos.yaml`, and no `compile` step. Hub-authoring concepts — EntityBinding,
`integration/bindings/*.binding.yaml`, dbt transforms, `ontology-hub-publish/` — belong in a
client hub, not here. If a task seems to call for them, it is aimed at the wrong repository.

> **Do not run `kairos-ontology setup-config`, `init`, or `update` in this repo.** They
> install the toolkit's hub scaffold (25 hub-authoring skills plus a hub
> `copilot-instructions.md`). That scaffold was previously applied here by mistake and has
> been removed; re-running those commands reinstates it.

## Content tiers

| Tier | Path | Rule |
|---|---|---|
| **Authoritative** | `authoritative-ontologies/` | Official RDF/OWL from standards bodies (FIBO, IATA ONE Record). Vendored **verbatim** — never hand-edit; re-download instead. |
| **Derived** | `derived-ontologies/` | Kairos RDF interpretations of non-RDF standards (DCSA, MMT, BSP, TIC, IMO, WCO, RAIL, Sustainability), plus **SupplyChain** — the cross-standard bridge module (defines no new classes; only bridges classes across standards). Every standard-backed class must be backed by a cited element of its standard. |
| **Blueprint** | `blueprints/` | Opinionated Kairos guidance (archetypes, patterns, `blueprints/ontology/`). Not a standard; versioned independently. |

Accelerator packs (`accelerator-packs/<pack>/`) pre-compose these into a bundle per sector.

## The published contract

The toolkit reads exactly these. Treat any change to them as a cross-repo contract change:

| Path | Consumer |
|---|---|
| `catalog-v001.xml` | root marker + URI resolution |
| `blueprints/archetypes/*.yaml` | `archetype_loader` (`ref_model_modules`, `core_concepts`) |
| `blueprints/patterns/*/pattern.yaml` | `pattern_loader` |
| `accelerator-packs/*/client-hub-blueprint/data-domains.yaml` | `analyse_sources`, `reference_modules` |
| `accelerator-packs/*/discovery/<id>.md` | path only — **never parsed** |

Two rules learned the hard way:

1. **Never ship a machine-readable file with no reader.** Files nothing consumes rot silently
   — `pattern.yaml` `mode_bindings` said `extension-point` for two releases after the models
   landed. If the consumer does not exist yet, write a CR (`.docs/wip/*-cr.md`) and land the
   file *with* its reader.
2. **A tier/enum shared with the toolkit is duplicated there.** Changing
   `blueprints/archetypes/_schema/archetype.schema.json` `$defs/tier` needs a coordinated PR;
   `tests/test_toolkit_contract.py` will fail loudly when they diverge.

## Adding or changing an industry model

`manifest.yaml` is the **single hand-edited registry**. Everything else is generated or tested
against it. After editing it:

1. Author the ontology under the correct tier; every class cites its standard.
2. Bump the module `VERSION` and `owl:versionInfo` together (**refmodels-ontology-versioning**).
3. Register in `catalog-v001.xml` (one entry per module document IRI).
4. Add the module to the accelerator `owl:imports` and to `data-domains.yaml`.
5. Run the full gate below — generators and the fan-out test catch the surfaces prose forgets.
6. Update `CHANGELOG.md`; releases are tagged `v*.*.*` and `VERSION` must match the tag.

## Validation gate

```bash
python -m pytest -q
python scripts/generate_logistics_inventory.py --check
python scripts/validate_logistics_blueprint.py
python scripts/validate_structure.py
python scripts/version_manager.py check
python scripts/validate_archetypes.py
```

These run in `.github/workflows/validate.yml` on every PR and again on release.

## Repo skills

- **refmodels-ontology-audit** — verify every `owl:Class` is backed by its cited standard.
- **refmodels-ontology-versioning** — version bumps and archiving.

Both are repo-owned. They deliberately do **not** use the `kairos-` prefix, which belongs to
the toolkit's managed scaffold.
