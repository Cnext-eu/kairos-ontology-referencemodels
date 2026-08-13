# Published Contract

What this repository publishes, what consumers may rely on, and how it changes.

The machine-readable half is [`contract-manifest.yaml`](contract-manifest.yaml), which maps each
contract file to its schema and its consuming loader. That file is enforced by
`tests/test_contract_manifest.py`; **this document deliberately does not restate it**. A prose
copy of a machine file is how `BLUEPRINT.md` came to sit four bridge properties behind
`data-domains.yaml` without anyone noticing.

Versioned with the repository `VERSION`. There is no separate contract version: a contract
change is a minor bump at least, and the `CHANGELOG.md` entry says so.

## Consumers

`kairos-ontology-toolkit` is the primary consumer. It reads this repository as a directory
(resolved via `KAIROS_REFMODELS_ROOT`, an explicit `--ref-models`, or a sibling checkout), not
as an installed package. Releases are published as a tarball containing
`ontology-reference-models/`, `scripts/`, and the root metadata files — **`.docs/` is not
shipped**.

Contract tests run from both sides and must stay in step:

| Repository | Test |
|---|---|
| here | `tests/test_toolkit_contract.py` — our published surface, through the real toolkit loaders |
| toolkit | `tests/test_refmodels_contract.py` — its loaders, against a real checkout of this repo |

## Rules for consumers

**Import the module, not the pack.** A hub's domain ontology imports the specific reference
module it needs — `…/ont/bsp/party`, not `…/ont/accelerator/logistics`. The accelerator bundle
exists for tools that need the complete graph at once; importing it into a domain file pulls in
everything and makes the domain's real dependencies unreadable. The toolkit already behaves this
way: `scaffold-binding` resolves the module that owns the target class and keeps that
`owl:imports` block in sync automatically.

**Extend rather than redefine.**

| Situation | Action |
|---|---|
| The concept exists in a reference model | `owl:imports` the module — do not redefine it locally |
| It exists but needs extra properties | Import it, then add properties with your namespace as `rdfs:domain` |
| It exists in no reference model | Define it in your own domain `.ttl` as a client-specific class |
| You need a subclass of a reference class | Import the parent, define the subclass in your domain |

**Bind mode at the reservation, never at the order.** See
`blueprints/patterns/multimodal-order-leg`. An order spanning three modes has no single mode
value; `mode_bindings[].target_iris` names the grain-3 class each mode binds to.

## Patterns vs derived modules

The pattern library (`blueprints/patterns/`) and the derived ontologies are both published by
this repository, and until v1.16.0 nothing reconciled them. The precedence rule:

1. **Pattern-normative naming governs every Kairos-chosen name** — everything in
   `blueprints/ontology/`, and any derived-module term that does not mirror a cited source
   element.
2. **Where a derived module mirrors its source standard's element name, source fidelity wins**
   — but only visibly: the term carries the citation in its `rdfs:comment` **and** an entry in
   the owning pattern's `exemptions` list (`{name, reason}`, reason cites the source). The
   exemptions list is the machine-readable record of every place a pattern yields.
3. **An unexempted disagreement between a pattern and shipped content is a defect in this
   repository.** `scripts/validate_pattern_conformance.py` fails the build on it. Hub authors
   follow the pattern and file an issue here.

Deliberately domainless reusable properties are marked with an `rdfs:comment` starting
`REUSABLE — no rdfs:domain by design` (e.g. `bsp/party#hasAddress`: a `TradeParty` domain would
infer the subsumption the qualified-role-assignment pattern bans onto every hub class using the
property). `validate_structure.py` accepts a missing domain only with that marker; the range is
always required.

## Rules for us

**Never ship a machine-readable file with no reader.** Every stale surface this repository has
had was a file nothing consumed: `pattern.yaml` `mode_bindings` said `extension-point` for air
and rail for two releases; `capability-coverage.yaml` sat at `1.8.0` while the pack reached
`1.9.0`; `BLUEPRINT.md`'s bridge table silently fell four properties behind. If the consumer
does not exist yet, write a CR under `.docs/wip/` and land the file *with* its reader — as
`discovery-scope-selection-cr.md` does.

**Derived facts are generated or tested, never hand-maintained.** `manifest.yaml` is the single
hand-edited registry per pack. Documentation counts, version tables and module lists are
rendered into marker blocks by `scripts/generate_pack_docs.py --check`;
`tests/test_model_registration.py` fans `manifest.yaml` out across the accelerator imports, the
catalog and `data-domains.yaml`.

**Enums shared with the toolkit are duplicated there.** Changing `$defs/tier` in
`blueprints/archetypes/_schema/archetype.schema.json` needs a coordinated PR;
`test_toolkit_contract.py::test_tier_enum_matches_the_consumer_copy` fails when they diverge.

## Adding or changing an industry model

1. Author the ontology under the correct tier (`authoritative-` verbatim, `derived-` with every
   class citing its standard, `blueprints/` for Kairos-authored grains).
2. Bump the module `VERSION` and `owl:versionInfo` together — skill `refmodels-ontology-versioning`.
3. Register every module document IRI in `catalog-v001.xml`.
4. Add it to `manifest.yaml`, to the accelerator's `owl:imports`, and to `data-domains.yaml`.
   A module in the bundle that no data domain references fails
   `test_every_include_reaches_data_domains`; opting out requires an explicit
   `data_domain_status` on the manifest entry, with a reason.
5. Run the full gate (see `README.md`) and regenerate docs with
   `python scripts/generate_pack_docs.py`.
6. Add a model sheet under `.intro/industry-models/` — the generated index lists a module with
   no sheet as missing rather than omitting it.

## Deprecation

A contract file may not be moved or removed in a single release. Expand, then contract: the
toolkit accepts both old and new for one release, this repository moves, the toolkit drops the
old path a release later. A hard cut breaks any hub on the previous toolkit — a moved
`data-domains.yaml` surfaces as *"No data-domains.yaml for accelerator"* and silently degrades
`scaffold-binding` to *"owl:imports was not added automatically"*.

Advisory surfaces (warnings, discovery prose) may change freely. Anything in
`contract-manifest.yaml` may not.

**Terms inside a published module** (class/property IRIs) have their own policy — hubs bind to
them even though only document IRIs are listed in the manifest:

- **Renaming or removing a term IRI is a breaking change and a MAJOR module bump**, with an
  old→new table in the `CHANGELOG.md` entry. Archetype `compatible_with.ontology_versions`
  ranges are updated in the same release, so existing hubs opt in consciously rather than
  inheriting the break through a compatible-looking pin. (First exercised by MMT 2.0.0 —
  the temporal-quartet renames.)
- **Additive machinery and annotations are a minor bump**: new classes/properties,
  `owl:deprecated true` markings, comment/citation changes. (First exercised by BSP 1.6.0 —
  the role-assignment machinery.)
- **`owl:deprecated true` is a signal, not a removal**: the term stays declared and resolvable
  for at least the remainder of the current major version; conformance checks skip deprecated
  subjects.
