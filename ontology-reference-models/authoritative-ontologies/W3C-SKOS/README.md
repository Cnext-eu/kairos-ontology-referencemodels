# W3C SKOS — Authoritative Ontology Mirror

Vendored copy of the **SKOS Simple Knowledge Organization System** core vocabulary,
published by the W3C. Vendored verbatim — **do not hand-edit `core.rdf`**; re-download
instead.

## Tier

**Authoritative.** SKOS is published natively as RDF/OWL, so it enters
`authoritative-ontologies/` rather than being re-authored as a derived ontology. See
`ontology-reference-models/blueprints/README.md` for the authoritative / derived /
blueprint tier distinction.

## Why it is here

`skos:` is used as an annotation prefix across the derived ontologies, but a prefix
declaration needs no mirror. The mirror exists because one vendored FIBO document
actually imports the vocabulary — see
[scaffolding.ttl](../FIBO/current/fibo/etc/vocabulary/scaffolding.ttl):

```turtle
owl:imports <http://www.w3.org/2004/02/skos/core> .
```

Without a resolvable target that import failed, and `scaffolding.ttl` shipped in v1.16.0
as one of three files that could not be inventoried. See gh#57.

## Contents

| Path | Purpose |
|---|---|
| `current/skos/core.rdf` | SKOS core vocabulary (namespace `http://www.w3.org/2004/02/skos/core#`) |
| `current/METADATA.txt` | Provenance: source, version, download date |
| `current/LICENSE` | W3C Software and Document License (2023) |
| `archive/` | Superseded releases |

## Version

SKOS Recommendation **18 August 2009** — the vocabulary has been stable since. See
`current/METADATA.txt`.

## Where it binds in Kairos

SKOS resolves through a single explicit `<uri>` entry in
[catalog-v001.xml](../../catalog-v001.xml):

```xml
<uri name="http://www.w3.org/2004/02/skos/core"
     uri="authoritative-ontologies/W3C-SKOS/current/skos/core.rdf"/>
```

The catalog resolver registers the base IRI plus its `/` and `#` variants, so both the
import form (`.../core`) and the prefix form (`.../core#`) match the same file.

## License

W3C Software and Document License (2023) — see `./current/LICENSE`. **This differs from
the other bundled mirrors, which are MIT.** Bundled under the repository `NOTICE`
third-party section. Apache-2.0 compatible: it is a permissive copy/modify/distribute
grant whose only condition is notice retention.
