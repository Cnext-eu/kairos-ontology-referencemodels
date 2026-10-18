# ISO 4217 Currency Codes — from the Maintenance Agency (SIX)

ISO 4217 currency and fund codes, vendored from **SIX Financial Information AG**, which maintains
ISO 4217 on behalf of ISO. Generated — **do not hand-edit**; re-run
`scripts/download_iso4217.py` instead.

This is the **currency list hubs bind to** (a kind-1 list, see
`blueprints/patterns/governed-code-list`, "Where the values live"). UN/CEFACT's
`unece:CurrencyCodeList` and FIBO's ISO 4217 identifiers are secondary copies that lag ISO
(gh#128): in October 2026 UN/CEFACT still listed `ANG`, `BGN`, `CUC` and `ZWL` as current and
lacked `XAD`, `XCG` and `ZWG`.

## Contents

| File | Ontology IRI | Purpose |
|---|---|---|
| `list-one.xml`, `list-three.xml` | — | The SIX source files, vendored unchanged |
| `ISO4217-CurrencyCodes.ttl` | `https://www.kairosflow.ai/ont/iso4217` | Generated code list. **Hubs import this IRI.** |
| `ISO4217-alignment.ttl` | `https://www.kairosflow.ai/ont/iso4217/alignment` | Generated `skos:exactMatch` to `unece:CurrencyCodeList` and FIBO's ISO 4217 identifiers |
| `METADATA.txt` | — | Provenance: publication dates, checksums, counts, deviations |

## Shape

One member of `iso4217:CurrencyCode` per alphabetic code:

```turtle
iso4217:EUR a owl:NamedIndividual, iso4217:CurrencyCode ;
    rdf:value "EUR" ;                 # the join key
    rdfs:label "Euro" ;
    iso4217:numericCode "978" ;       # leading zeros kept ("008")
    iso4217:minorUnit 2 .             # absent where ISO says N.A. (XAU, XDR, ...)

iso4217:ANG a owl:NamedIndividual, iso4217:CurrencyCode ;
    rdf:value "ANG" ;
    rdfs:label "Netherlands Antillean Guilder" ;
    iso4217:numericCode "532" ;
    owl:deprecated true ;
    iso4217:withdrawalDate "2025-03" .
```

- **Current codes** (in list one, 178 in the 2026-09-17 edition) carry name, numeric code, minor
  unit and, for fund codes (`BOV`, `CHE`, `CHW`, `CLF`, `COU`, `MXV`, `USN`, `UYI`, `UYW`,
  `XAD`), `iso4217:isFund true`.
- **Withdrawn codes** (only in list three, 129) are **kept**, because historic records carry
  them, and marked `owl:deprecated true` with `iso4217:withdrawalDate` as SIX writes it
  (`"2025-03"`, `"1989 to 1990"`): the latest of the code's historic rows. Filter them out for
  new data; keep them for history.
- A withdrawal is per **country row**, not per code. A code in list three that is still in
  list one (`EUR`, after a territory dropped it) is current.
- **Join on the alphabetic code, not the numeric one.** ISO reuses numeric codes: `XCG` took
  `532` from `ANG`.

The class carries `kairos-ext:isReferenceData true`, `owl:versionInfo` (the list-one publication
date, e.g. `"2026-09-17"`), `dcterms:source` (SIX list one) and `rdfs:seeAlso` (this README).

## Refresh

SIX amends ISO 4217 several times a year (amendment numbers on its page). Refresh with:

```sh
python scripts/download_iso4217.py --check   # exit 1 if SIX published a change
python scripts/download_iso4217.py           # refresh; archives the old snapshot
```

The monthly `reference-data-freshness` workflow runs this too. A newly withdrawn code becomes
`owl:deprecated`; it is never removed, so a refresh is not breaking for hubs that stored it.
See `VERSIONING.md`, "Refreshing reference data".

## Relation to the other currency copies

| Copy | Status |
|---|---|
| `iso4217:CurrencyCode` (this module) | **Bind to this.** Current, from the maintenance agency. |
| `unece:CurrencyCodeList` (UNCEFACT) | Secondary; lags ISO. Linked by `skos:exactMatch`. |
| FIBO `fibo-fnd-acc-cur:CurrencyIdentifier` (FIBO closure) | Secondary; lags ISO. Linked by `skos:exactMatch`. |
| IATA `code-lists:CurrencyCode` | An open list with **no members** ("based on ISO 4217"), so there is nothing to link code by code. A hub that binds IATA's currency slots takes this list in with `iso4217:CurrencyCode rdfs:subClassOf iata-cl:CurrencyCode`. |

## License

SIX provides the lists "online and free of charge" on behalf of ISO and SNV (the Swiss
Association for Standardization), and ISO has stated that use of the ISO 4217 codes is free of
charge. No explicit redistribution clause was found on SIX's site; SIX's terms of use are
linked from its legal pages and should be read before relying on redistribution beyond
attribution. The vendored content is facts: codes, names, numbers, minor units and dates.
Attribution: *ISO 4217 currency codes, maintained by SIX Financial Information AG on behalf of
ISO (https://www.six-group.com/).*
