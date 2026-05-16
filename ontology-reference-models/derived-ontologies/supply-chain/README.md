# Supply Chain Ontology

A lightweight supply chain integration layer based on UN/CEFACT MMT RDM and ISO Buy-Ship-Pay reference data model.

## Structure

```
supply-chain/
├── supply-chain.ttl   # Root ontology
├── VERSION            # Version file
└── README.md          # This file
```

## Namespace

**Root:** `http://kairos.ai/ont/supply-chain#`

## Version

1.0.0

## Key Classes

### Core Shipment
- `Shipment` — A separately identifiable collection of goods items to be transported
- `Consignment` — A logical grouping of goods for transport under a single contract
- `ConsignmentItem` — An individual line item within a consignment

### Transport
- `TransportMovement` — A stage or leg of physical transportation (multi-modal)
- `TransportEquipment` — Equipment used for transporting goods (containers, trailers, etc.)
- `Container` — Standardized ISO freight container
- `Trailer` — Vehicle without a motor designed to be hauled
- `RailCar` — Vehicle for railway transport of goods

### Party Roles
- `Party` — Any entity involved in the supply chain
- `Shipper` — The party that sends/ships goods
- `Consignee` — The party that receives goods
- `Carrier` — The party that performs physical transport
- `FreightForwarder` — Intermediary arranging transport on behalf of shipper
- `NotifyParty` — Party to be notified on shipment arrival

### Location & Facility
- `Location` — A geographic or logical location in the supply chain
- `Facility` — A physical facility (warehouse, depot, terminal)

### Documents & Identifiers
- `TransportDocument` — Document covering the transport of goods
- `ReferenceIdentifier` — Unique identifier for supply chain entities

## Design Principles

1. **Standards-aligned** — Based on UN/CEFACT MMT RDM and ISO Buy-Ship-Pay
2. **FIBO-integrated** — Reuses FIBO foundational classes for agents, documents, identifiers, and locations
3. **Kairos Core** — Extends the Kairos Core ontology (`kairos-core:`)
4. **Consistent metadata** — Uses `dcterms:` for metadata and `owl:versionInfo` for versioning

## Sources

- UN/CEFACT Multi-Modal Transport Reference Data Model (MMT RDM)
- ISO Buy-Ship-Pay Reference Data Model

## Usage

```turtle
@prefix sc: <http://kairos.ai/ont/supply-chain#> .
```
