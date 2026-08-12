# Diagrams

Visual documentation of the Kairos reference models — built for business and onboarding
conversations, where the point is to *show* the concepts and how they relate rather than read
Turtle. Every diagram is [Mermaid](https://mermaid.js.org/) and renders natively on GitHub.

There are two layers, kept in separate folders on purpose.

## [`conceptual/`](conceptual/) — hand-authored

The big picture. Curated, narrative diagrams a generator cannot infer:

| Diagram | Shows |
|---|---|
| [`tier-landscape.md`](conceptual/tier-landscape.md) | The three content tiers — authoritative, derived, blueprint — and what each is for |
| [`domain-relationships.md`](conceptual/domain-relationships.md) | The nine derived suites and how they connect, via the SupplyChain bridge module |
| [`accelerator-logistics.md`](conceptual/accelerator-logistics.md) | How the Logistics accelerator pack composes the suites into one importable bundle |
| [`patterns/`](conceptual/patterns/) | Each blueprint pattern drawn as the shape it prescribes |

## [`generated/`](generated/) — machine-generated, do not edit

One Mermaid class diagram per derived ontology suite, rendered straight from the Turtle by
[`scripts/generate_ontology_diagrams.py`](../../scripts/generate_ontology_diagrams.py). These
are **derived facts** — never hand-edited, per
[`CONTRACT.md`](../CONTRACT.md)'s "generated or tested, never hand-maintained" rule. CI runs the
generator's `--check` mode, so a suite that changes without its diagram being refreshed fails the
build.

```bash
# Refresh all suite diagrams after changing any ontology
python scripts/generate_ontology_diagrams.py

# Verify they are current (what CI runs)
python scripts/generate_ontology_diagrams.py --check

# Drill into a single module on demand (prints to stdout)
python scripts/generate_ontology_diagrams.py --suite DCSA --module booking
```

## Rendering to images

The diagrams are source-only; GitHub renders them inline. To export SVG/PNG for slides, the
[`@mermaid-js/mermaid-cli`](https://github.com/mermaid-js/mermaid-cli) dev dependency is declared
in the repo `package.json`:

```bash
npm install
npx mmdc -i ontology-reference-models/diagrams/generated/dcsa.md -o dcsa.svg
```
