# Cross-Archetype Assessment

The synthetic freight-forwarder and carrier/terminal shapes are evidence probes, not
consumer schemas. Neither shape authorizes a canonical class or physical Silver policy.

| Semantic grain | Forwarder shape | Carrier/terminal shape | Assessment |
|---|---|---|---|
| Durable Party | Present | Present | Universal need; role separation remains unresolved |
| Contextual Party role | Combined as FKs on jobs/consignments | Combined as FKs on bookings | Universal semantic need, commonly flattened physically |
| Booking | Carrier booking under a forwarding job | Primary reservation aggregate | Survives both; forwarder adds a distinct upstream job |
| Shipment | May be carrier reference only | First-class transaction | Optional for forwarder, core for carrier |
| Consignment | First-class house/master hierarchy | May be absent or combined with shipment | Distinct freight grain, not universally materialized |
| Consignment item | First-class | Often cargo lines elsewhere | Supported, but physical naming varies |
| Equipment request | May be combined with allocation | First-class before assignment | Distinct semantics survive both |
| Equipment asset | Third-party reference or tracked unit | Durable fleet/unit master | Optional master ownership, universal referenced identity |
| Equipment utilisation | Allocation table | Allocation table | Strong cross-archetype grain |
| Route/leg | Ordered consignment legs | Often schedule/call-centric | Forwarder core; carrier representation may specialize |
| Transport call | Carrier feed or absent | First-class execution grain | Carrier core, forwarder optional |
| Event | Multi-subject milestone | Container/call operational event | Universal envelope need; subject grain differs |
| Transport document | House/master split | Carrier document reference | Identity/version pattern survives; class authority differs |

## Consequences

1. Do not require every consuming hub to materialize every candidate.
2. Do not set universal SCD policy while one shape combines or omits the grain.
3. Preserve Booking, Shipment, Consignment, equipment request, equipment utilisation,
   and equipment asset as distinct semantics even when a source combines them.
4. Add extension points for forwarding job, qualified party/location roles, event
   subjects, and plan-to-execution realization.
5. Keep unresolved candidates out of the Silver Starter until reviewed.
