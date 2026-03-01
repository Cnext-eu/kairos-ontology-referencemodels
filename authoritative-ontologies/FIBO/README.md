# FIBO - Financial Industry Business Ontology

## About

The Financial Industry Business Ontology (FIBO) is an authoritative ontology published by the **EDM Council** for the financial services industry.

**Publisher:** EDM Council  
**License:** MIT License  
**Homepage:** https://spec.edmcouncil.org/fibo/  
**Repository:** https://github.com/edmcouncil/fibo

---

## Current Version

See [METADATA.txt](METADATA.txt) for download details and version information.

---

## Contents

This folder contains the complete FIBO ontology suite downloaded from the official EDM Council repository, including:

- **FND** - Foundations
- **BE** - Business Entities
- **FBC** - Financial Business and Commerce
- **IND** - Indices and Indicators
- **SEC** - Securities
- **DER** - Derivatives
- **LOAN** - Loans
- **MD** - Market Data

All files are preserved in their original structure as published by the EDM Council.

---

## Provenance

- **Type:** Authoritative Ontology
- **Status:** Read-only reference
- **Governance:** Semantics owned by EDM Council
- **Updates:** Use `python scripts/download_fibo.py` to refresh

---

## Usage in Kairos

These ontologies serve as authoritative references for:
- Financial entity modeling
- Organizational structures
- Contract and agreement semantics
- Product and service definitions

Map Kairos concepts to FIBO using SKOS mappings in `ontology-hub/mappings/`.
