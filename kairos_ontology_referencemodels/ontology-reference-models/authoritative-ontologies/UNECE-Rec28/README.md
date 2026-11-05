# UNECE Recommendation 28 — Codes for Types of Means of Transport

The complete Rec 28 code list (Revision 4.2, 2018), built from the official XLS that UNECE
publishes on https://unece.org/trade/uncefact/cl-recommendations. Generated — **do not hand-edit**;
re-run `scripts/build_unece_rec28.py`.

This is the **means-of-transport type list hubs bind to** (kind 1, see
`blueprints/patterns/governed-code-list`, "Where the values live"). UN/CEFACT's web vocabulary
carries only part of it: `unece:TransportMeansTypeCodeList` has the 134 four-digit codes and none
of the two- and three-digit ones, which include the generic road codes (31 Truck, 33 Tractor,
34 Van, 342 Van, light).

## Contents

| File | Ontology IRI | Purpose |
|---|---|---|
| `Rec28_Rev4.2e_2018.xls` | — | The UNECE code list, vendored unchanged |
| `UNECE-Rec28.ttl` | `https://www.kairosflow.ai/ont/unece-rec28` | Generated code list. **Hubs import this IRI.** |
| `UNECE-Rec28-alignment.ttl` | `https://www.kairosflow.ai/ont/unece-rec28/alignment` | Generated `skos:exactMatch` from the 134 four-digit codes to `unece:TransportMeansTypeCodeList` |
| `METADATA.txt` | — | Provenance: source file checksum, counts, deprecations, deviations |

## Shape

The sheet's code is Mode + Code-A + Code-B concatenated (3, 4, 2 → `342`): 282 unique codes
(20 two-digit, 128 three-digit, 134 four-digit). One member of `rec28:TransportMeansTypeCode` each:

```turtle
rec28:342 a owl:NamedIndividual, rec28:TransportMeansTypeCode ;
    rdf:value "342" ;                                        # the join key
    rdfs:label "Van, light" ;
    skos:definition "Automotive vehicle designed for light carriage." ;
    skos:broader rec28:34 ;                                  # 34 Van
    rec28:transportMode <https://vocabulary.uncefact.org/TransportModeCodeList#3> .   # Rec 19: road
```

- **Hierarchy.** A Code-B row's `skos:broader` is its Code-A row (342 → 34, 2201 → 220). Four
  sub-codes have no printed Code-A row and no broader code: 1711, 1712, 4000, 5000.
- **Mode.** The first digit is the UNECE Rec 19 transport mode, linked with `rec28:transportMode`,
  so any type rolls up to the shipped transport-mode list.
- **Change indicator.** `rec28:changeIndicator` carries the revision's `+` (added: 186, 187),
  `|` (changed: 185) and `X` (marked for deletion: 852–855). The `X` codes are also
  `owl:deprecated true`; they stay in the list for historic records.
- Labels are kept exactly as printed, including an en dash in 1515 (the vocabulary writes a
  hyphen) and non-breaking spaces in two tank-barge names.

The class carries `kairos-ext:isReferenceData true`, `owl:versionInfo "Rev 4.2 (2018)"`,
`dcterms:source` (the UNECE page) and `rdfs:seeAlso` (this README).

## What Rec 28 does and does not cover

Rec 28 types **vehicles and vessels**, including truck-plus-trailer combinations (e.g. 395
"Truck, with trailer"). It has **no codes for trailers or semi-trailers on their own**, and its
rail codes type **trains** (block train, container train), not locomotives or wagons. For
equipment classes — trailer, semi-trailer, chassis, swap body, rail car, container — use UNTDED
8053, `unece:TransportEquipmentCategoryCodeList` in `authoritative-ontologies/UNCEFACT`. A finer
trailer typology is client-owned (kind 3): link its members to 8053 `TE` / `SM` with
`skos:broadMatch`.

## Refresh

Rec 28 changes rarely. When UNECE publishes a new revision, replace the XLS here, update
`REVISION` in the script, and rebuild:

```sh
uv run --with xlrd python scripts/build_unece_rec28.py
```

The build fails if the header row changes, if the title names another revision, or if the
vocabulary's four-digit codes and this list's no longer agree. No monthly workflow runs it.

## License

A UNECE recommendation: the same position as `authoritative-ontologies/UNCEFACT` (UN/CEFACT
states its standards are free to use under CC BY 4.0; written confirmation for the download
sites is pending). Attribution: *UNECE Recommendation No. 28, Codes for Types of Means of
Transport, Revision 4.2, © United Nations Economic Commission for Europe.*
