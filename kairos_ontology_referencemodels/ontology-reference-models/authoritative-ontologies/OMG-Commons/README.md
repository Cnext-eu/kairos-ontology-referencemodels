# OMG Commons — Authoritative Ontology Mirror

Vendored copy of the **Commons Ontology Library (COL)**, published by the Object
Management Group. Vendored verbatim — **do not hand-edit the `.rdf` files**; re-download
instead.

## Tier

**Authoritative.** Commons is published natively as RDF/OWL, so it enters
`authoritative-ontologies/` rather than being re-authored as a derived ontology. See
`ontology-reference-models/blueprints/README.md` for the authoritative / derived /
blueprint tier distinction.

## Why it is here

Commons is not used directly by any Kairos-authored module. It is here because **FIBO
imports it** — every FIBO module pulls in some subset of Commons. Without this mirror no
FIBO import closure resolves at all, which is what shipped broken in v1.16.0: three
`.ttl` files in the bundle failed `generate-inventory` with "Ontology closure is
incomplete", and the financial-services accelerator was unusable in any hub. See gh#57.

## Contents

| Path | Purpose |
|---|---|
| `current/commons/` | 22 Commons ontology modules, one `.rdf` each, flat layout |
| `current/METADATA.txt` | Provenance: source, version, download date, module list |
| `current/LICENSE` | MIT License (OMG and co-copyright holders) |
| `archive/` | Superseded releases |

## Version

See `current/METADATA.txt` for the pinned release. The local folder is always named
`current/commons/` regardless of upstream release version, so catalog resolution does
not change on upgrade.

## Where it binds in Kairos

Commons URIs resolve to these local files through a single `rewriteURI` rule in
[catalog-v001.xml](../../catalog-v001.xml):

```xml
<rewriteURI uriStartString="https://www.omg.org/spec/Commons/"
            rewritePrefix="authoritative-ontologies/OMG-Commons/current/commons/"/>
```

Commons publishes ontology IRIs ending in `/` (e.g.
`https://www.omg.org/spec/Commons/Locations/`) while the file on disk is `Locations.rdf`
one level up — the same convention FIBO uses. The catalog resolver retries a
directory-shaped rewrite target as `<name>.rdf` / `.ttl` / `.owl`, so the single rule
covers all 22 modules.

Nothing in this repository `owl:imports` Commons directly. It is reached transitively
from FIBO, and from the financial-services accelerator through FIBO.

## License

MIT License — see `./current/LICENSE`. Bundled under the repository `NOTICE` third-party
section. Apache-2.0 compatible.
