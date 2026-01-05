# Supply Chain Ontology - Technical Summary

## Overview

The Kairos Supply Chain Ontology is a derived ontology based on **UN/CEFACT Multi-Modal Transport (MMT) Reference Data Model** and **ISO Buy-Ship-Pay** standards. It provides a comprehensive semantic model for international trade, logistics, and supply chain operations.

## File Location
- **Ontology:** [ontologies/derived-ontologies/supply-chain.ttl](../ontologies/derived-ontologies/supply-chain.ttl)
- **Examples:** [examples/supply-chain-example.md](supply-chain-example.md)
- **Documentation:** [ontologies/derived-ontologies/README.md](../ontologies/derived-ontologies/README.md)

## Namespace
```
http://kairos.ai/ont/supply-chain#
```

## Key Concepts

### 1. Shipment Hierarchy (UN/CEFACT aligned)
```
Shipment
  └─ Consignment (1..*)
       └─ ConsignmentItem (1..*)
```

- **Shipment:** Overall physical movement of goods
- **Consignment:** Logical grouping under a single transport contract
- **ConsignmentItem:** Individual items/products within a consignment

### 2. Transport Chain
- **TransportMovement:** Individual legs in the transport journey
  - Supports multi-modal transport (sea, air, road, rail)
  - Sequential linking via `previousMovement`/`nextMovement`
  - Location tracking (departure/arrival)
  - Vessel/voyage identification

### 3. Transport Equipment
- **Container** (ISO containers: 20ft, 40ft, reefer, etc.)
- **Trailer** (road transport)
- **RailCar** (rail transport)
- **Pallet** (handling equipment)

All equipment tracked with unique identifiers and seal numbers for security.

### 4. Party Roles (UN/CEFACT aligned)
- **Shipper/Consignor:** Sends goods
- **Consignee:** Receives goods
- **Carrier:** Transports goods
- **Freight Forwarder:** Arranges transport
- **Notify Party:** Informed upon arrival

All roles extend FIBO `AgentInRole` for consistency.

### 5. Locations & Facilities
- **Port:** Sea/river ports
- **Airport:** Air cargo facilities
- **Warehouse:** Storage facilities
- **DistributionCenter:** Distribution hubs
- **Terminal:** Intermodal transfer points

Supports UN/LOCODE and ISO 3166 country codes.

### 6. Documents (Trade & Transport)
- **BillOfLading:** Sea freight contract & receipt
- **AirWaybill:** Air freight document
- **SeaWaybill:** Non-negotiable sea document
- **CommercialInvoice:** Sales invoice
- **PackingList:** Package contents
- **CustomsDeclaration:** Import/export declaration

All documents extend FIBO `Document` with standard properties.

### 7. Identifiers & References
- **ShipmentIdentifier**
- **ConsignmentIdentifier**
- **EquipmentIdentifier**
- **BookingReference**

Supports multiple identifier schemes (GTIN, SSCC, etc.).

## Standards Compliance

### UN/CEFACT
- Multi-Modal Transport Reference Data Model (MMT RDM)
- Core Component Library (CCL) alignment
- Business document standards

### ISO Standards
- ISO Buy-Ship-Pay Reference Data Model
- ISO 3166 (Country codes)
- ISO 6346 (Container identification)
- ISO 8601 (Date/time formats)

### International Codes
- **HS Codes:** Harmonized System for commodity classification
- **UN/LOCODE:** Location codes for trade and transport
- **IATA Codes:** Airport identification
- **IMO Numbers:** Vessel identification

## FIBO Integration

Extends key FIBO concepts:
- `fibo-fnd-aap-agt:AgentInRole` → Party roles
- `fibo-fnd-arr-doc:Document` → Transport documents
- `fibo-fnd-plc-loc:Location` → Locations and facilities
- `fibo-fnd-arr-id:Identifier` → Reference numbers

## Class Statistics

- **Core Classes:** 8 (Shipment, Consignment, ConsignmentItem, etc.)
- **Transport Classes:** 6 (TransportMovement, Container, Trailer, etc.)
- **Party Roles:** 6 (Shipper, Consignee, Carrier, etc.)
- **Location Classes:** 6 (Port, Airport, Warehouse, etc.)
- **Document Classes:** 7 (BillOfLading, AirWaybill, etc.)
- **Identifier Classes:** 5 (ShipmentIdentifier, etc.)

**Total Classes:** 38

## Property Statistics

- **Datatype Properties:** 31
- **Object Properties:** 24

**Total Properties:** 55

## Usage Scenarios

1. **International Trade:** Import/export documentation and tracking
2. **Multi-Modal Transport:** Complex transport chains with multiple legs
3. **Container Management:** Equipment tracking and utilization
4. **Customs Clearance:** Documentation and commodity classification
5. **Supply Chain Visibility:** End-to-end shipment tracking
6. **Warehouse Operations:** Facility and inventory location management

## Example Use Cases

### Sea Freight
- Container shipments from Shanghai to Rotterdam
- Bill of Lading documentation
- Port-to-port tracking

### Air Freight
- Express air cargo with Air Waybill
- Airport-to-airport movements
- Time-critical shipments

### Multi-Modal
- Factory → Road → Port → Sea → Port → Rail → Destination
- Equipment changes at intermodal terminals
- Multiple carrier coordination

### Warehouse Distribution
- Pallet-level tracking
- Distribution center operations
- Last-mile delivery preparation

## SPARQL Query Capabilities

The ontology supports rich queries for:
- Shipment status and location tracking
- Multi-leg transport chain analysis
- Equipment utilization reports
- Document completeness checks
- Party role identification
- Customs compliance verification

See [examples/supply-chain-example.md](supply-chain-example.md) for detailed SPARQL examples.

## Extensibility

The ontology can be extended for:
- **Industry-specific logistics:** Automotive, pharmaceuticals, perishables
- **Compliance regimes:** EU ICS2, US ACI, ISF requirements
- **Track & trace systems:** Real-time location updates, event tracking
- **Carbon accounting:** Transport emissions calculation
- **Dangerous goods:** IMDG/IATA DGR compliance

## Dependencies

### Required Imports
- Kairos Core Ontology
- FIBO FND (Foundations)
  - Agents and People
  - Organizations
  - Agreements/Contracts
  - Documents
  - Identifiers
  - Locations
  - Relations
  - Dates and Times

### Catalog Resolution
All imports resolved via `catalog-v001.xml` for offline operation.

## Version History

- **v1.0.0** (2026-01-05): Initial release
  - Full UN/CEFACT MMT RDM coverage
  - ISO Buy-Ship-Pay alignment
  - Multi-modal transport support
  - Complete party role modeling
  - Document lifecycle management

## Future Enhancements

Potential additions:
1. Event tracking (shipment milestones, status updates)
2. Incoterms (trade terms modeling)
3. Payment terms and conditions
4. Insurance and liability
5. Temperature/condition monitoring for cold chain
6. Blockchain integration for document verification
7. IoT sensor data integration

## References

1. **UN/CEFACT MMT RDM:** https://unece.org/trade/uncefact/mainstandards
2. **ISO 28005:** Electronic port clearance (EPC)
3. **WCO Data Model:** World Customs Organization
4. **DCSA Standards:** Digital Container Shipping Association
5. **IATA Cargo-XML:** Air cargo messaging standards

## License & Governance

- **License:** Same as Kairos project
- **Governance:** Kairos Ontology Team
- **Status:** Active development
- **Contributions:** Follow standard alignment principles

## Contact

For questions or contributions related to the Supply Chain Ontology:
- Review [ontologies/derived-ontologies/README.md](../ontologies/derived-ontologies/README.md)
- Ensure changes align with UN/CEFACT and ISO standards
- Update examples when adding new concepts
