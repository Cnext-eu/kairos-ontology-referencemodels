# Pattern: Qualified role assignment

**Closes gaps 1, 2, 7.** A durable identity (a party, a location) plays different roles in
different contexts over time — the same organisation is Shipper on one booking and Carrier on
another. Modelling the role *onto* the identity (`Shipper subClassOf Party`) duplicates the
identity the moment it plays two roles. Instead, reify the assignment as its own link entity.

```mermaid
flowchart LR
  PARTY["Party<br/><small>durable identity — one record</small>"]
  RA["PartyRoleAssignment<br/><small>(identity, role, context, validity)</small>"]
  BOOKING["Booking<br/><small>context</small>"]
  ROLE["hasRole<br/><small>Shipper | Consignee | Carrier …</small>"]

  RA -->|assignedToParty| PARTY
  RA -->|inContextOfBooking| BOOKING
  RA -->|hasRole| ROLE

  classDef id fill:#e8f7e9,stroke:#3aa657;
  classDef link fill:#f3e8ff,stroke:#8a3bd8;
  class PARTY id;
  class RA link;
```

One `Party`, many `PartyRoleAssignment`s — the same party is Shipper on one and Consignee on
another without a duplicate identity record.

## The rejected shape

```mermaid
flowchart TB
  PARTY["Party"]
  SHIPPER["Shipper"]:::bad
  CARRIER["Carrier"]:::bad
  PARTY --> SHIPPER
  PARTY --> CARRIER
  SHIPPER -.->|"breaks when one org is both,<br/>needs re-typing when the role changes"| WHY["subclassing identity by role ✗"]
  classDef bad fill:#ffe3e3,stroke:#d84b4b;
```

Naming is **normative** (`<Identity>RoleAssignment`, `assignedTo<Identity>`, `inContextOf<Context>`,
`hasRole`). Boolean role flags (`isCarrier`) are an acceptable *physical* simplification only when
role history is not needed and they are documented as a projection of this link entity.

Source: [`blueprints/patterns/qualified-role-assignment`](../../../blueprints/patterns/qualified-role-assignment/pattern.md).
