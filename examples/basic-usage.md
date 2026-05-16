# Basic Usage - Kairos Reference Models

This guide shows how to consume and use Kairos reference models in your ontology project.

---

## Installation Methods

### Method 1: Git Submodule (Recommended)

Best for projects under version control that need stable, versioned references.

```bash
# Navigate to your project
cd my-ontology-project

# Add reference models as submodule
git submodule add https://github.com/Cnext-eu/kairos-reference-models.git reference-models

# Initialize and update
git submodule update --init --recursive

# Pin to specific version (recommended)
cd reference-models
git checkout v1.0.0
cd ..

# Commit the pinned version
git add .gitmodules reference-models
git commit -m "Add kairos-reference-models@v1.0.0"
```

**Update to newer version:**
```bash
cd reference-models
git fetch --tags
git checkout v1.1.0  # Or latest: git checkout main && git pull
cd ..
git add reference-models
git commit -m "Update reference-models to v1.1.0"
```

### Method 2: Direct Clone

Simpler for experimentation or non-Git projects.

```bash
# Clone specific version
git clone --branch v1.0.0 --depth 1 https://github.com/Cnext-eu/kairos-reference-models.git

# Or clone latest
git clone https://github.com/Cnext-eu/kairos-reference-models.git
```

---

## Validation

Install the Kairos Ontology Toolkit:

```bash
pip install kairos-ontology-toolkit
```

### Validate Reference Models Only

```bash
# From project root
kairos-ontology validate \
  --ontologies reference-models/ontologies \
  --shapes reference-models/shapes \
  --all

# Test FIBO catalog resolution
kairos-ontology catalog-test \
  --catalog reference-models/catalog-v001.xml
```

### Validate Your Extensions

```bash
# Validate both reference models and your extensions
kairos-ontology validate \
  --ontologies reference-models/ontologies:my-ontologies \
  --shapes reference-models/shapes:my-shapes \
  --all
```

---

## Importing in Your Ontology

### Import Core Ontology

```turtle
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix kairos: <https://www.kairosflow.ai/ont/core#> .

<http://example.com/my-company/ontology> a owl:Ontology ;
    rdfs:label "My Company Ontology"@en ;
    owl:imports <https://www.kairosflow.ai/ont/core> .
```

**Note:** When using file-based imports (not dereferenced URIs), configure your system to resolve `https://www.kairosflow.ai/ont/core` to `reference-models/ontologies/core.ttl`.

### Using Kairos Classes

```turtle
@prefix kairos: <https://www.kairosflow.ai/ont/core#> .
@prefix mycomp: <http://example.com/my-company#> .

# Create a Customer instance
mycomp:customer-123 a kairos:Customer ;
    kairos:name "ACME Corporation" ;
    kairos:email "contact@acme.com" ;
    kairos:phone "+1-555-0100" .

# Create an Order instance
mycomp:order-456 a kairos:Order ;
    kairos:orderDate "2025-01-03T10:30:00Z"^^xsd:dateTime ;
    kairos:totalAmount "1500.00"^^xsd:decimal ;
    kairos:status "confirmed" ;
    kairos:hasCustomer mycomp:customer-123 .

# Create a Product instance
mycomp:product-789 a kairos:Product ;
    kairos:sku "PROD-789" ;
    kairos:name "Premium Widget" ;
    kairos:price "150.00"^^xsd:decimal ;
    kairos:category "hardware" .

# Link order to product
mycomp:order-456 kairos:hasProduct mycomp:product-789 .
```

---

## Generating Projections

Use the toolkit to generate downstream artifacts:

```bash
# Generate all projection types
kairos-ontology project \
  --target all \
  --ontologies reference-models/ontologies \
  --mappings reference-models/mappings \
  --output output

# Generate specific projection
kairos-ontology project \
  --target dbt \
  --ontologies reference-models/ontologies \
  --output output/dbt
```

**Output:**
- **DBT:** `output/dbt/models/silver/*.sql` and `*.yml`
- **Neo4j:** `output/neo4j/schema.cypher`
- **Azure Search:** `output/azure-search/indexes/*.json` and `synonym-maps/*.json`
- **A2UI:** `output/a2ui/schemas/*.schema.json`
- **Prompt:** `output/prompt/prompt-context-compact.json`

---

## SKOS Mappings

Access Schema.org alignments:

```bash
# Load SKOS mappings
from rdflib import Graph

g = Graph()
g.parse("reference-models/mappings/schema-org.ttl", format="turtle")

# Query for mappings
query = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX kairos: <https://www.kairosflow.ai/ont/core#>

SELECT ?kairos_class ?schema_class
WHERE {
    ?kairos_class skos:closeMatch|skos:exactMatch ?schema_class .
    FILTER (STRSTARTS(STR(?schema_class), "http://schema.org/"))
}
"""

for row in g.query(query):
    print(f"{row.kairos_class} → {row.schema_class}")
```

---

## Directory Structure in Your Project

```
my-ontology-project/
├── reference-models/          # Git submodule → kairos-reference-models@v1.0.0
│   ├── ontologies/
│   ├── shapes/
│   ├── mappings/
│   └── catalog-v001.xml
├── ontologies/                # Your custom extensions
│   └── my-company.ttl
├── shapes/                    # Your custom SHACL shapes
│   └── my-company.shacl.ttl
├── output/                    # Generated projections
├── requirements.txt           # kairos-ontology-toolkit==1.0.0
└── README.md
```

---

## Troubleshooting

### Submodule Not Initialized

**Error:** `reference-models/` directory is empty

**Solution:**
```bash
git submodule update --init --recursive
```

### FIBO Imports Not Resolving

**Error:** Cannot resolve `https://spec.edmcouncil.org/fibo/...`

**Solution:**
```bash
# Test catalog
kairos-ontology catalog-test --catalog reference-models/catalog-v001.xml

# Ensure catalog is used during validation
kairos-ontology validate --all --catalog reference-models/catalog-v001.xml
```

### Version Mismatch

**Error:** Reference models version doesn't match expected version

**Solution:**
```bash
cd reference-models
git describe --tags  # Check current version
git checkout v1.0.0  # Switch to expected version
cd ..
git add reference-models
git commit -m "Pin reference-models to v1.0.0"
```

---

## Next Steps

- **[Extending Models](extending-models.md)** - Learn how to extend Kairos classes with custom properties
- **[CHANGELOG](../CHANGELOG.md)** - See version history and upgrade notes
- **[GitHub Discussions](https://github.com/Cnext-eu/kairos-reference-models/discussions)** - Ask questions and share feedback

---

**Last Updated:** 2025-01-03 | **Version:** 1.0.0
