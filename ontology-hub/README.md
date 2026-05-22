# Cldn — Ontology Hub

## Company context

| Field              | Value                                          |
|--------------------|------------------------------------------------|
| **Company name**   | Cldn                                 |
| **Company domain** | cldn.com                               |
| **Namespace base** | `https://cldn.com/ont/`                |

## Namespace convention

All ontologies in this hub use the namespace pattern:

```
https://cldn.com/ont/<domain>#
```

For example:
- Customer domain → `https://cldn.com/ont/customer#`
- Order domain → `https://cldn.com/ont/order#`

## Domain model overview

Before creating individual domain ontology files, define the high-level domain
structure here.  This helps avoid fragmented .ttl files and ensures coherent
coverage.

| Domain | Description | File | Status |
|--------|-------------|------|--------|
| party | Customers, hauliers, and employees | `model/ontologies/party/party.ttl` | ✅ Modeled |
| equipment | Trailers, containers, unit types, asset availability | `model/ontologies/equipment/equipment.ttl` | 🔲 Planned |
| route-schedule | Shipping routes, markets, intermodal legs | `model/ontologies/route-schedule/route-schedule.ttl` | 🔲 Planned |
| consignment | Transport orders, loading/unloading, volumes, OTA | `model/ontologies/consignment/consignment.ttl` | 🔲 Planned |
| financial | Demurrage, HPI cost/km, margins | `model/ontologies/financial/financial.ttl` | 🔲 Planned |
| booking | Cargo quotes, quote lifecycle, forecast loads | `model/ontologies/booking/booking.ttl` | 🔲 Planned |

## Master ontology

The file `ontology-hub/model/ontologies/_master.ttl` imports all domain ontologies
into a single unified graph.  Keep it updated when adding or removing domains.

## Conventions

- One domain per `.ttl` file (e.g., `customer.ttl`, `order.ttl`).
- Filename = domain identifier (lowercase, hyphens for multi-word).
- Every file declares an `owl:Ontology` with `rdfs:label` and `owl:versionInfo`.
- Classes: PascalCase.  Properties: camelCase.
- Target 5–15 classes per domain file.
