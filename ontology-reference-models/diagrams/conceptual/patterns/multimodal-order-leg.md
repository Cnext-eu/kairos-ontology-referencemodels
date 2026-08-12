# Pattern: Multimodal order → leg

**Closes gap 5.** A transport order is multimodal by construction, but every useful standard is
mode-bound (DCSA ocean, IATA air, TAF TSI rail). The pattern attaches **mode one grain lower than
the order** — on the leg — and binds the mode-specific standard at the *reservation*, never at the
order.

```mermaid
flowchart LR
  ORDER["TransportOrder<br/><small>aggregate root — carries NO mode</small>"]
  LEG["TransportLeg<br/><small>carries the mode</small>"]
  RES["CarrierReservation<br/><small>mode bound here, by binding</small>"]
  MOV["TransportMovement<br/><small>execution — mode inherited</small>"]

  ORDER -->|hasPlannedLeg| LEG
  LEG -->|hasCarrierReservation| RES
  LEG -->|realizedByMovement| MOV

  classDef order fill:#f3e8ff,stroke:#8a3bd8;
  classDef leg fill:#e8f7e9,stroke:#3aa657;
  classDef other fill:#eef4ff,stroke:#3b6ea8;
  class ORDER order;
  class LEG leg;
  class RES,MOV other;
```

## Mode binds at the reservation grain

Each leg's mode selects which standard the reservation binds to. The order itself never names a
mode — an intermodal order has none.

```mermaid
flowchart LR
  RES["CarrierReservation<br/>(grain 3)"]
  OCEAN["ocean → DCSA Booking"]
  AIR["air → IATA ONE Record<br/><small>vendored, catalog-resolved</small>"]
  RAIL["rail → TAF TSI<br/>Path Request / Consignment Order"]
  ROAD["road → pattern-only<br/><small>no standard forces a shape</small>"]
  BARGE["barge → pattern-only"]

  RES --> OCEAN
  RES --> AIR
  RES --> RAIL
  RES --> ROAD
  RES --> BARGE
```

## Anti-patterns (rejected)

```mermaid
flowchart TB
  A["OceanOrder / RoadOrder subclasses,<br/>or an orderTransportMode scalar"]:::bad
  B["order rdfs:subClassOf a mode-specific<br/>standard class (e.g. dcsa:Booking)"]:::bad
  C["hasBooking directly on the order<br/>(order → reservation shortcut)"]:::bad
  D["cargo / customs / financial properties<br/>declared on the order class"]:::bad

  A -->|"an intermodal order needs two types at once"| WHY1["mode belongs on the leg"]
  B -->|"inherits obligations no source can populate"| WHY2["bind at the reservation grain"]
  C -->|"loses which leg a reservation covers"| WHY3["reservations attach to legs"]
  D -->|"the order is a root, not a report"| WHY4["fan out to owning domains"]

  classDef bad fill:#ffe3e3,stroke:#d84b4b;
```

Source: [`blueprints/patterns/multimodal-order-leg`](../../../blueprints/patterns/multimodal-order-leg/pattern.md).
Naming is **normative**; participants and cardinality are advisory.
