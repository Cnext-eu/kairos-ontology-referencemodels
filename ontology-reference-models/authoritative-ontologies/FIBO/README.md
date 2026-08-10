# FIBO — Authoritative Ontology Mirror

Vendored copy of the **Financial Industry Business Ontology (FIBO)**, published by the
Enterprise Data Management Council. Vendored verbatim — **do not hand-edit the `.rdf` /
`.ttl` files**; re-download instead via `scripts/download_fibo.py`.

## Tier

**Authoritative.** FIBO is published natively as RDF/OWL, so it enters
`authoritative-ontologies/` rather than being re-authored as a derived ontology. See
`ontology-reference-models/blueprints/README.md` for the authoritative / derived /
blueprint tier distinction.

## Contents

| Path | Purpose |
|---|---|
| `current/fibo/` | 300+ FIBO ontology files, upstream module layout preserved |
| `current/METADATA.txt` | Provenance: source, version, download date, release URL |
| `current/LICENSE` | MIT License (Copyright (c) 2020 Enterprise Data Management Council) |
| `archive/` | Superseded releases |

Top-level FIBO modules present: `ACTUS`, `BE` (Business Entities), `BP` (Business
Process), `CAE` (Corporate Actions & Events), `DER` (Derivatives), `FBC` (Financial
Business & Commerce), `FND` (Foundations), `IND` (Indicators), `LOAN`, `MD` (Market
Data), `SEC` (Securities), `etc`.

## Version

See `current/METADATA.txt` for the pinned release. The local folder is always named
`current/fibo/` regardless of upstream release version, so catalog resolution does not
change on upgrade.

## Where it binds in Kairos

FIBO URIs resolve to these local files through a single `rewriteURI` rule in
[catalog-v001.xml](../../catalog-v001.xml):

```xml
<rewriteURI uriStartString="https://spec.edmcouncil.org/fibo/ontology/"
            rewritePrefix="authoritative-ontologies/FIBO/current/fibo/"/>
```

The financial-services accelerator pack imports FIBO directly — see
[financial-services-accelerator.ttl](../../accelerator-packs/financial-services/current/financial-services-accelerator.ttl):

```turtle
owl:imports <https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/> ,
            <https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/> ,
            <https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/> ,
            <https://spec.edmcouncil.org/fibo/ontology/BE/Partnerships/Partnerships/> .
```

Elsewhere (e.g. the party-commercial payment-terms and credit-limit modelling) FIBO is
used as design inspiration only, not imported.

## License

MIT License — see `./current/LICENSE`. Bundled under the repository `NOTICE` third-party
section. Apache-2.0 compatible.
