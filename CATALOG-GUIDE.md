# XML Catalog System

## Overview

The Kairos Ontology Hub uses **XML Catalog** to resolve FIBO ontology imports from local files instead of fetching from the internet. This ensures:

- ✅ **Offline development** - No network required
- ✅ **Deterministic builds** - Same FIBO version every time
- ✅ **Fast validation** - Local file access (no HTTP latency)
- ✅ **Version control** - Explicit tracking of FIBO version

---

## Architecture

```
kairos-reference-models/
├── catalog-v001.xml              ← URI → local file mappings
├── ontologies/
│   ├── core.ttl                  ← Uses canonical FIBO URIs
│   ├── authoritative-ontologies/ ← Official RDF/OWL from standards
│   │   └── FIBO/                 ← Downloaded FIBO ontologies
│   │       └── edmcouncil-fibo-.../
│   └── derived-ontologies/       ← Our RDF interpretations
│
scripts/
├── catalog_utils.py              ← Catalog resolver library
├── test_catalog.py               ← Catalog validation tool
└── download_fibo.py              ← Update FIBO ontologies
```

---

## How It Works

### URI Convention (Important!)

The `#` character has a specific role in ontology URIs:

| Context | Example | Has `#`? |
|---------|---------|----------|
| Namespace prefix (`@prefix`) | `<https://www.kairosflow.ai/ont/dcsa#>` | YES — used for class/property names |
| Ontology IRI (`a owl:Ontology`) | `<https://www.kairosflow.ai/ont/dcsa>` | NO — identifies the ontology itself |
| Import URI (`owl:imports`) | `<https://www.kairosflow.ai/ont/dcsa/booking>` | NO — must match catalog |
| Catalog entry (`name=`) | `"https://www.kairosflow.ai/ont/dcsa"` | NO — must match imports |

**Rule**: Catalog `name` attributes must exactly match the `owl:imports` URIs used
in ontology files. Neither should end with `#`.

### 1. Your Ontology Uses Canonical URIs

[core.ttl](../ontology-hub/ontologies/core.ttl):
```turtle
: a owl:Ontology ;
    owl:imports <https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/> .
```

### 2. Catalog Maps URIs to Local Files

[catalog-v001.xml](catalog-v001.xml):
```xml
<uri name="https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/"
     uri="ontologies/authoritative-ontologies/FIBO/edmcouncil-fibo-da9e773/FND/Organizations/FormalOrganizations.rdf"/>
```

### 3. Validation Uses Local Files

```bash
python scripts/validate.py --ontology ontology-hub/ontologies/core.ttl
```

Output:
```
✓ Loaded import: https://spec.edmcouncil.org/fibo/.../FormalOrganizations/
  → G:\...\kairos-reference-models\ontologies\authoritative-ontologies\FIBO\...\FormalOrganizations.rdf

📦 Loaded 9/9 imports via catalog
```

---

## Usage

### Test Catalog Configuration

```bash
python scripts/test_catalog.py
```

Validates all catalog mappings point to existing files.

### Update FIBO Ontologies

```bash
python scripts/download_fibo.py
```

Downloads latest FIBO release and updates reference models.

### Validate Ontologies

```bash
python scripts/validate.py --ontology ontology-hub/ontologies/core.ttl
```

Automatically resolves imports via catalog.

---

## Adding New FIBO Modules

If you need additional FIBO modules:

1. **Check if they exist** in `ontologies/authoritative-ontologies/FIBO/`
2. **Add catalog entry** in `catalog-v001.xml`:

```xml
<uri name="https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/"
     uri="ontologies/authoritative-ontologies/FIBO/edmcouncil-fibo-da9e773/BE/LegalEntities/LegalPersons.rdf"/>
```

3. **Add import** in your ontology:

```turtle
owl:imports <https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/> .
```

4. **Test**:

```bash
python scripts/test_catalog.py
python scripts/validate.py --ontology ontology-hub/ontologies/core.ttl
```

---

## Migration from `/external` Folder

**Old approach (deprecated):**
```
ontology-hub/ontologies/external/
├── fibo-agents.rdf          ← Copied files
├── fibo-organizations.rdf   ← Stale versions
└── ...

core.ttl: owl:imports <file:///G:/Git/.../external/fibo-agents.rdf>
```

**New approach (current):**
```
ontologies/authoritative-ontologies/FIBO/
└── edmcouncil-fibo-.../     ← Single source of truth

core.ttl: owl:imports <https://spec.edmcouncil.org/fibo/.../Agents/>
catalog-v001.xml: Maps URI → local file
```

**Benefits:**
- No duplication
- Clear provenance
- Easy updates
- Standards-compliant URIs

---

## Technical Details

### CatalogResolver Class

See [catalog_utils.py](../scripts/catalog_utils.py) for implementation.

**Key methods:**
- `resolve(uri)` - Maps FIBO URI to local Path
- `is_mapped(uri)` - Check if URI has catalog entry
- `load_graph_with_catalog()` - Load ontology + imports

### OASIS XML Catalog Standard

Follows [OASIS XML Catalogs v1.1](https://www.oasis-open.org/committees/entity/spec-2001-08-06.html).

---

## Troubleshooting

### Catalog mappings fail validation

```bash
python scripts/test_catalog.py
```

If files are missing, re-download FIBO:
```bash
python scripts/download_fibo.py
```

### Imports not resolving

Check catalog path in validation script:
```python
catalog_path = base_dir / "catalog-v001.xml"
```

Ensure catalog is at root: `catalog-v001.xml`.

### New FIBO version breaks catalog

Update catalog paths in `catalog-v001.xml` to match new folder name:
```xml
uri="ontologies/authoritative-ontologies/FIBO/edmcouncil-fibo-NEWVERSION/..."
```

Or regenerate catalog automatically (future enhancement).
