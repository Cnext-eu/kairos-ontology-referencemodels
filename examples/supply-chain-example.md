# Supply Chain Ontology - Usage Examples

This document provides practical examples of using the Kairos Supply Chain Ontology based on UN/CEFACT MMT RDM and ISO Buy-Ship-Pay standards.

## Basic Import

```turtle
@prefix : <http://example.org/shipment-data#> .
@prefix sc: <http://kairos.ai/ont/supply-chain#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/shipment-data> a owl:Ontology ;
    owl:imports <http://kairos.ai/ont/supply-chain#> .
```

---

## Example 1: Simple Sea Freight Shipment

A basic container shipment from Shanghai to Rotterdam.

```turtle
# Shipment
:shipment-2026-001 a sc:Shipment ;
    sc:hasShipmentId "SHP-2026-001" ;
    sc:shipmentDate "2026-01-05"^^xsd:date ;
    sc:expectedDeliveryDate "2026-02-10"^^xsd:date ;
    sc:hasOrigin :shanghai-port ;
    sc:hasDestination :rotterdam-port ;
    sc:hasConsignment :consignment-001 .

# Consignment
:consignment-001 a sc:Consignment ;
    sc:hasConsignmentId "CNS-2026-001" ;
    sc:totalGrossWeight 18500.00 ;
    sc:totalNetWeight 17800.00 ;
    sc:packageCount 800 ;
    sc:hasShipper :acme-electronics ;
    sc:hasConsignee :euro-distributors ;
    sc:hasCarrier :global-shipping-line ;
    sc:hasTransportMovement :movement-001 ;
    sc:usesEquipment :container-001 ;
    sc:documentedBy :bol-001 .

# Transport Movement
:movement-001 a sc:TransportMovement ;
    sc:hasTransportMode "sea" ;
    sc:vesselName "Pacific Express" ;
    sc:voyageNumber "PE-2026-W02" ;
    sc:departureLocation :shanghai-port ;
    sc:arrivalLocation :rotterdam-port ;
    sc:departureDate "2026-01-10T14:00:00"^^xsd:dateTime ;
    sc:arrivalDate "2026-02-08T08:00:00"^^xsd:dateTime .

# Container
:container-001 a sc:Container ;
    sc:hasEquipmentId "MSCU1234567" ;
    sc:equipmentType "40HC" ;
    sc:sealNumber "SEAL-789456" .

# Locations
:shanghai-port a sc:Port ;
    sc:locationName "Port of Shanghai" ;
    sc:locationCode "CNSHA" ;
    sc:city "Shanghai" ;
    sc:countryCode "CN" .

:rotterdam-port a sc:Port ;
    sc:locationName "Port of Rotterdam" ;
    sc:locationCode "NLRTM" ;
    sc:city "Rotterdam" ;
    sc:countryCode "NL" .

# Parties
:acme-electronics a sc:Shipper ;
    rdfs:label "Acme Electronics Co., Ltd." .

:euro-distributors a sc:Consignee ;
    rdfs:label "Euro Distributors B.V." .

:global-shipping-line a sc:Carrier ;
    rdfs:label "Global Shipping Line" .

# Bill of Lading
:bol-001 a sc:BillOfLading ;
    sc:documentNumber "BOL-GSL-2026-001" ;
    sc:documentDate "2026-01-05"^^xsd:date ;
    sc:issuedBy :global-shipping-line .
```

---

## Example 2: Multi-Modal Transport with Multiple Legs

Shipment involving road, sea, and rail transport.

```turtle
# Consignment with multiple transport legs
:consignment-002 a sc:Consignment ;
    sc:hasConsignmentId "CNS-2026-002" ;
    sc:totalGrossWeight 22000.00 ;
    sc:hasShipper :midwest-manufacturing ;
    sc:hasConsignee :asian-imports ;
    sc:hasForwarder :international-freight ;
    sc:hasTransportMovement :leg-001, :leg-002, :leg-003 .

# Leg 1: Factory to Port by Road
:leg-001 a sc:TransportMovement ;
    sc:hasTransportMode "road" ;
    sc:departureLocation :chicago-warehouse ;
    sc:arrivalLocation :la-port ;
    sc:departureDate "2026-01-06T09:00:00"^^xsd:dateTime ;
    sc:arrivalDate "2026-01-08T15:00:00"^^xsd:dateTime ;
    sc:usesEquipment :trailer-001 ;
    sc:nextMovement :leg-002 .

# Leg 2: Sea Freight
:leg-002 a sc:TransportMovement ;
    sc:hasTransportMode "sea" ;
    sc:vesselName "Trans-Pacific Voyager" ;
    sc:voyageNumber "TPV-2026-003" ;
    sc:departureLocation :la-port ;
    sc:arrivalLocation :tokyo-port ;
    sc:departureDate "2026-01-12T18:00:00"^^xsd:dateTime ;
    sc:arrivalDate "2026-01-26T10:00:00"^^xsd:dateTime ;
    sc:usesEquipment :container-002 ;
    sc:previousMovement :leg-001 ;
    sc:nextMovement :leg-003 .

# Leg 3: Rail to Final Destination
:leg-003 a sc:TransportMovement ;
    sc:hasTransportMode "rail" ;
    sc:departureLocation :tokyo-port ;
    sc:arrivalLocation :osaka-terminal ;
    sc:departureDate "2026-01-27T08:00:00"^^xsd:dateTime ;
    sc:arrivalDate "2026-01-27T14:00:00"^^xsd:dateTime ;
    sc:usesEquipment :railcar-001 ;
    sc:previousMovement :leg-002 .

:trailer-001 a sc:Trailer ;
    sc:hasEquipmentId "TRL-9876" ;
    sc:equipmentType "53ft" .

:container-002 a sc:Container ;
    sc:hasEquipmentId "ABCU9876543" ;
    sc:equipmentType "40GP" ;
    sc:sealNumber "SEAL-456123" .

:railcar-001 a sc:RailCar ;
    sc:hasEquipmentId "JR-12345" ;
    sc:equipmentType "boxcar" .

:international-freight a sc:Forwarder ;
    rdfs:label "International Freight Solutions Inc." .
```

---

## Example 3: Consignment with Multiple Items and Documents

Detailed consignment with itemization and full documentation.

```turtle
:consignment-003 a sc:Consignment ;
    sc:hasConsignmentId "CNS-2026-003" ;
    sc:packageCount 120 ;
    sc:hasConsignmentItem :item-001, :item-002, :item-003 ;
    sc:hasShipper :tech-manufacturer ;
    sc:hasConsignee :retail-chain ;
    sc:hasNotifyParty :customs-broker ;
    sc:documentedBy :bol-003, :invoice-003, :packing-003, :customs-003 .

# Consignment Items
:item-001 a sc:ConsignmentItem ;
    sc:itemSequenceNumber 1 ;
    sc:itemDescription "Laptop Computers - Model XYZ" ;
    sc:itemQuantity 500 ;
    sc:hsCode "8471.30" .

:item-002 a sc:ConsignmentItem ;
    sc:itemSequenceNumber 2 ;
    sc:itemDescription "Computer Monitors - 27 inch" ;
    sc:itemQuantity 300 ;
    sc:hsCode "8528.52" .

:item-003 a sc:ConsignmentItem ;
    sc:itemSequenceNumber 3 ;
    sc:itemDescription "Wireless Keyboards" ;
    sc:itemQuantity 800 ;
    sc:hsCode "8471.60" .

# Documents
:bol-003 a sc:BillOfLading ;
    sc:documentNumber "BOL-2026-003" ;
    sc:documentDate "2026-01-05"^^xsd:date .

:invoice-003 a sc:CommercialInvoice ;
    sc:documentNumber "INV-2026-0045" ;
    sc:documentDate "2026-01-05"^^xsd:date ;
    sc:issuedBy :tech-manufacturer .

:packing-003 a sc:PackingList ;
    sc:documentNumber "PKL-2026-0045" ;
    sc:documentDate "2026-01-05"^^xsd:date .

:customs-003 a sc:CustomsDeclaration ;
    sc:documentNumber "CUSTOMS-EU-2026-001234" ;
    sc:documentDate "2026-02-07"^^xsd:date .

# Parties
:customs-broker a sc:NotifyParty ;
    rdfs:label "Express Customs Brokerage Ltd." .
```

---

## Example 4: Air Freight with Full Party Roles

Express air shipment with complete party role assignments.

```turtle
:shipment-004 a sc:Shipment ;
    sc:hasShipmentId "SHP-AIR-2026-001" ;
    sc:shipmentDate "2026-01-05"^^xsd:date ;
    sc:expectedDeliveryDate "2026-01-07"^^xsd:date ;
    sc:hasOrigin :frankfurt-airport ;
    sc:hasDestination :jfk-airport ;
    sc:hasConsignment :consignment-004 .

:consignment-004 a sc:Consignment ;
    sc:hasConsignmentId "AWB-125-12345678" ;
    sc:totalGrossWeight 850.50 ;
    sc:totalVolume 2.5 ;
    sc:packageCount 15 ;
    sc:hasShipper :pharma-europe ;
    sc:hasConsignee :pharma-usa ;
    sc:hasCarrier :global-air-cargo ;
    sc:hasNotifyParty :pharma-usa ;
    sc:hasTransportMovement :air-leg-001 ;
    sc:documentedBy :awb-001 .

:air-leg-001 a sc:TransportMovement ;
    sc:hasTransportMode "air" ;
    sc:vesselName "Flight GA-8745" ;
    sc:departureLocation :frankfurt-airport ;
    sc:arrivalLocation :jfk-airport ;
    sc:departureDate "2026-01-06T22:30:00"^^xsd:dateTime ;
    sc:arrivalDate "2026-01-07T02:15:00"^^xsd:dateTime .

:frankfurt-airport a sc:Airport ;
    sc:locationName "Frankfurt Airport" ;
    sc:locationCode "DEFRA" ;
    sc:city "Frankfurt" ;
    sc:countryCode "DE" .

:jfk-airport a sc:Airport ;
    sc:locationName "John F. Kennedy International Airport" ;
    sc:locationCode "USJFK" ;
    sc:city "New York" ;
    sc:countryCode "US" .

:awb-001 a sc:AirWaybill ;
    sc:documentNumber "125-12345678" ;
    sc:documentDate "2026-01-05"^^xsd:date ;
    sc:issuedBy :global-air-cargo .

:global-air-cargo a sc:Carrier ;
    rdfs:label "Global Air Cargo" .

:pharma-europe a sc:Shipper ;
    rdfs:label "European Pharmaceuticals GmbH" .

:pharma-usa a sc:Consignee ;
    rdfs:label "Pharma USA Inc." .
```

---

## Example 5: Warehouse and Distribution Center Management

Tracking goods through distribution facilities.

```turtle
:shipment-005 a sc:Shipment ;
    sc:hasShipmentId "SHP-DIST-2026-001" ;
    sc:hasOrigin :central-warehouse ;
    sc:hasDestination :regional-dc .

:central-warehouse a sc:Warehouse ;
    sc:locationName "Central Distribution Warehouse" ;
    sc:addressLine "1000 Logistics Parkway" ;
    sc:city "Memphis" ;
    sc:countryCode "US" ;
    sc:postalCode "38118" .

:regional-dc a sc:DistributionCenter ;
    sc:locationName "Northeast Regional Distribution Center" ;
    sc:addressLine "500 Commerce Drive" ;
    sc:city "Newark" ;
    sc:countryCode "US" ;
    sc:postalCode "07102" .

:consignment-005 a sc:Consignment ;
    sc:hasConsignmentId "CNS-DIST-2026-001" ;
    sc:partOfShipment :shipment-005 ;
    sc:usesEquipment :pallet-001, :pallet-002 .

:pallet-001 a sc:Pallet ;
    sc:hasEquipmentId "PLT-001234" ;
    sc:equipmentType "EUR-1200x800" .

:pallet-002 a sc:Pallet ;
    sc:hasEquipmentId "PLT-001235" ;
    sc:equipmentType "EUR-1200x800" .
```

---

## SPARQL Query Examples

### Query 1: Find all shipments scheduled for delivery in January 2026

```sparql
PREFIX sc: <http://kairos.ai/ont/supply-chain#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?shipment ?shipmentId ?deliveryDate ?origin ?destination
WHERE {
    ?shipment a sc:Shipment ;
              sc:hasShipmentId ?shipmentId ;
              sc:expectedDeliveryDate ?deliveryDate ;
              sc:hasOrigin ?origin ;
              sc:hasDestination ?destination .
    
    FILTER (?deliveryDate >= "2026-01-01"^^xsd:date && 
            ?deliveryDate < "2026-02-01"^^xsd:date)
}
ORDER BY ?deliveryDate
```

### Query 2: List all consignments by a specific shipper

```sparql
PREFIX sc: <http://kairos.ai/ont/supply-chain#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?consignment ?consignmentId ?shipperName
WHERE {
    ?consignment a sc:Consignment ;
                 sc:hasConsignmentId ?consignmentId ;
                 sc:hasShipper ?shipper .
    ?shipper rdfs:label ?shipperName .
    
    FILTER (CONTAINS(LCASE(?shipperName), "acme"))
}
```

### Query 3: Find multi-modal shipments (more than one transport mode)

```sparql
PREFIX sc: <http://kairos.ai/ont/supply-chain#>

SELECT ?consignment (COUNT(?movement) as ?legCount) 
       (GROUP_CONCAT(?mode; separator=", ") as ?modes)
WHERE {
    ?consignment a sc:Consignment ;
                 sc:hasTransportMovement ?movement .
    ?movement sc:hasTransportMode ?mode .
}
GROUP BY ?consignment
HAVING (COUNT(?movement) > 1)
```

### Query 4: Get all equipment used for a specific consignment

```sparql
PREFIX sc: <http://kairos.ai/ont/supply-chain#>

SELECT ?equipment ?equipmentType ?equipmentId
WHERE {
    :consignment-002 sc:usesEquipment ?equipment .
    ?equipment sc:equipmentType ?equipmentType ;
               sc:hasEquipmentId ?equipmentId .
}
```

### Query 5: Find all documents associated with a consignment

```sparql
PREFIX sc: <http://kairos.ai/ont/supply-chain#>

SELECT ?document ?docType ?docNumber ?docDate
WHERE {
    :consignment-003 sc:documentedBy ?document .
    ?document a ?docType ;
              sc:documentNumber ?docNumber ;
              sc:documentDate ?docDate .
    
    FILTER (?docType != owl:NamedIndividual)
}
ORDER BY ?docDate
```

---

## Best Practices

1. **Use UN/LOCODE** for location codes when available
2. **Follow ISO standards** for country codes (ISO 3166), dates (ISO 8601)
3. **Include HS codes** for consignment items to enable customs classification
4. **Link documents** to the entities they describe using appropriate properties
5. **Track equipment** throughout the supply chain using unique identifiers
6. **Sequence transport movements** using previousMovement/nextMovement for multi-leg journeys
7. **Assign all relevant party roles** to ensure complete business context

---

## Integration with Kairos Core

The Supply Chain ontology extends Kairos Core concepts:

- Party roles extend FIBO Agent concepts
- Documents extend FIBO Document arrangements
- Locations extend FIBO Location concepts
- Can link to Orders, Products, and Services from core ontology

Example integration:

```turtle
@prefix kairos-core: <http://kairos.ai/ont/core#> .

:consignment-006 a sc:Consignment ;
    sc:hasConsignmentId "CNS-2026-006" ;
    rdfs:comment "Fulfillment for customer order" ;
    # Link to a core Order
    sc:fulfillsOrder :customer-order-123 .

:customer-order-123 a kairos-core:Order ;
    kairos-core:orderId "ORD-2026-0123" ;
    kairos-core:contains :laptop-product .

:laptop-product a kairos-core:Product ;
    kairos-core:productId "PROD-LAPTOP-001" ;
    kairos-core:name "Business Laptop XYZ" .
```
