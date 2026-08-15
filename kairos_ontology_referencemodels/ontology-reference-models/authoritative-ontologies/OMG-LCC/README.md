# OMG LCC — Authoritative Ontology Mirror

Vendored copy of **Languages, Countries and Codes (LCC)**, published by the Object
Management Group. Vendored verbatim — **do not hand-edit the `.rdf` files**; re-download
instead.

## Tier

**Authoritative.** LCC is published natively as RDF/OWL, so it enters
`authoritative-ontologies/` rather than being re-authored as a derived ontology. See
`ontology-reference-models/blueprints/README.md` for the authoritative / derived /
blueprint tier distinction.

## Why it is here

Like [OMG-Commons](../OMG-Commons/README.md), LCC is not used directly by any
Kairos-authored module — it is a FIBO dependency. FIBO's ACTUS module imports the
country-code ontologies:

```turtle
owl:imports <https://www.omg.org/spec/LCC/Countries/CountryRepresentation/> ,
            <https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/> .
```

This dependency was **masked** in v1.16.0: the missing Commons mirror failed the closure
first, so LCC never surfaced in the error output. It only became visible once Commons
resolved. See gh#57 — and note that this is exactly why the bundle-conformance test
asserts closure resolution rather than grepping a generator's log.

## Contents

| Path | Purpose |
|---|---|
| `current/lcc/Countries/` | `CountryRepresentation.rdf`, `ISO3166-1-CountryCodes.rdf` |
| `current/lcc/Languages/` | `LanguageRepresentation.rdf` |
| `current/METADATA.txt` | Provenance: source, version, download date, module list |
| `current/LICENSE` | MIT License (OMG and co-copyright holders) |
| `archive/` | Superseded releases |

## Version

See `current/METADATA.txt` for the pinned release. The local folder is always named
`current/lcc/` regardless of upstream release version, so catalog resolution does not
change on upgrade. The upstream IRI path layout (`Countries/`, `Languages/`) is
preserved on disk so a single rewrite rule maps cleanly.

## Where it binds in Kairos

LCC URIs resolve to these local files through a single `rewriteURI` rule in
[catalog-v001.xml](../../catalog-v001.xml):

```xml
<rewriteURI uriStartString="https://www.omg.org/spec/LCC/"
            rewritePrefix="authoritative-ontologies/OMG-LCC/current/lcc/"/>
```

Nothing in this repository `owl:imports` LCC directly. It is reached transitively from
FIBO.

## License

MIT License — see `./current/LICENSE`. Bundled under the repository `NOTICE` third-party
section. Apache-2.0 compatible.
