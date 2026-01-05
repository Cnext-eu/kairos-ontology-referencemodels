# Derived Ontologies

This directory contains domain-specific ontologies derived from and extending the Kairos core ontology and authoritative reference ontologies like FIBO.

---

## Available Ontologies

### Supply Chain Ontology
**File:** `supply-chain.ttl`  
**Namespace:** `http://kairos.ai/ont/supply-chain#`  
**Version:** 1.0.0  
**Created:** 2026-01-05

#### Description
A comprehensive supply chain and logistics ontology based on UN/CEFACT MMT RDM and ISO Buy-Ship-Pay reference data models.

#### Coverage
- **Shipment Structure:** Shipment, Consignment, ConsignmentItem
- **Transport:** TransportMovement (legs), TransportEquipment (containers, trailers, rail cars, pallets)
- **Party Roles:** Shipper, Consignee, Freight Forwarder, Carrier, Notify Party
- **Locations:** Port, Airport, Warehouse, Distribution Center, Terminal
- **Documents:** Bill of Lading, Air Waybill, Sea Waybill, Commercial Invoice, Packing List, Customs Declaration
- **Identifiers:** Shipment ID, Consignment ID, Equipment ID, Booking Reference

#### Standards Alignment
- UN/CEFACT Multi-Modal Transport (MMT) Reference Data Model
- ISO Buy-Ship-Pay Reference Data Model
- Harmonized System (HS) codes for commodity classification
- UN/LOCODE for location identification
- ISO 3166 country codes

#### Key Features
- Full support for multi-modal transport chains
- Party role management for complex supply networks
- Document lifecycle tracking
- Equipment and container management
- Location and facility modeling

---

## Usage Guidelines

### Importing Derived Ontologies

To use a derived ontology in your project, import it along with required dependencies:

```turtle
@prefix sc: <http://kairos.ai/ont/supply-chain#> .
@prefix kairos-core: <http://kairos.ai/ont/core#> .

<http://example.org/my-ontology> a owl:Ontology ;
    owl:imports <http://kairos.ai/ont/supply-chain#> .
```

### Catalog Resolution

All ontologies use the XML catalog (`catalog-v001.xml`) for URI resolution. The catalog automatically maps:
- Canonical URIs to local file paths
- FIBO URIs to local authoritative copies
- Derived ontology URIs to local files

---

## Development

### Creating New Derived Ontologies

When creating a new derived ontology:

1. **Extend, Don't Duplicate:** Build upon existing classes from core and FIBO
2. **Use Standard Namespaces:** Follow the pattern `http://kairos.ai/ont/{domain}#`
3. **Document Standards:** Reference authoritative standards (UN/CEFACT, ISO, etc.)
4. **Include Metadata:** Provide comprehensive dc:terms metadata
5. **Update Catalog:** Add mappings to `catalog-v001.xml` if needed
6. **Update This README:** Document the new ontology here

### Best Practices

- Reuse FIBO concepts where applicable (Agents, Organizations, Documents, Locations)
- Provide both labels and comprehensive comments
- Include UN/CEFACT or industry standard references in comments
- Use OWL restrictions to define class constraints
- Define inverse properties for bidirectional relationships

---

## Governance

- **Type:** Derived Ontologies
- **Status:** Active development
- **Governance:** Kairos Ontology Team
- **Review:** Changes should align with referenced standards
- Contract and agreement semantics
- Product and service definitions

Map Kairos concepts to FIBO using SKOS mappings in `ontology-hub/mappings/`.
