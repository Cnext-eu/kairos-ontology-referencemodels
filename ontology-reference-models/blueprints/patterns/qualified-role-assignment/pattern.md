# Qualified Role Assignment

**Normativity:** naming — normative. Participants and cardinality rules — advisory.

## Problem

A durable identity (a party, a location) plays different roles in different contexts over time
— the same organisation is a Shipper on one booking and a Carrier on another; the same physical
port is a Port of Loading on one itinerary and a Port of Discharge on another. Modelling the role
directly onto the identity (subclassing `Party` into `Shipper`, `Carrier`, ...) conflates identity
with a transient, context-dependent usage and produces duplicate identity records the moment one
organisation plays two roles concurrently.

This is the pattern behind CR-RM's declared gaps #1 (Party), #2 (Location), and #7 (cross-domain
Identifier Assignment) — three instances of the same shape, not three separate problems.

## Applicability

Use this pattern whenever a durable identity's role is: contextual (depends on the transaction or
itinerary it appears in), temporally bounded (starts and ends independently of the identity's own
lifecycle), or multiply-held (one identity holds several roles concurrently). Do not use it for a
role that is a permanent, definitional attribute of the identity itself.

**Standards overlays are exempt — hubs are not.** The derived party modules (`bsp/party`,
`mmt/party`, `dcsa/party`, `imo/party`) mirror their source standards' role-typed party shapes
for fidelity and message-level interop. The BSP/MMT role subclasses are `owl:deprecated`
overlays (superseded by the modules' role-assignment machinery); the still-live DCSA/IMO role
parents are named in this pattern's `exemptions`, each with a cited reason. A hub MUST NOT
subclass its durable Party identity under any of them — it assigns
roles through the modules' role-assignment machinery (`TradePartyRoleAssignment`,
`TransportPartyRoleAssignment`) or its own `<Identity>RoleAssignment` per this pattern. Where a
pattern and a derived module disagree without an exemption entry, that is a defect in this
repository — see CONTRACT.md, "Patterns vs derived modules".

## Participants (advisory)

- **Durable identity** — the party or location record, independent of any role it plays.
- **Role** — a controlled vocabulary term (Shipper, Consignee, Carrier, Port of Loading, ...).
- **Context** — the transaction, booking, or itinerary the role assignment is scoped to.
- **Validity** — the period the assignment holds, independent of the identity's own lifecycle.
- **Role assignment link entity** — `(identity, role, context, validity)`, the thing that actually
  varies over time; never merge this into the identity record.

## Naming (normative)

| Element | Convention |
|---|---|
| Role assignment class | `<Identity>RoleAssignment`, e.g. `PartyRoleAssignment`, `LocationRoleAssignment` |
| Link to identity | `assignedTo<Identity>`, e.g. `assignedToParty` |
| Link to context | `inContextOf<Context>`, e.g. `inContextOfBooking` |
| Role value property | `hasRole`, ranging over the pack's controlled role vocabulary |

## Cardinality rules (advisory)

One durable identity may have `0..n` role assignments, each scoped to exactly one context. A
context may require `1..n` role assignments (e.g. a booking requires at least a Shipper and a
Carrier) — the minimum cardinality is a pack-level business rule, not part of this pattern.

## Heterogeneous identity types (context, not a requirement)

The `<Identity>` token in the naming convention above binds to whichever class is durable and
role-bearing in the hub's model. When two or more *distinct* concrete identity classes can hold
the same kind of role assignment — e.g. both an `Organisation` and a `Staff` record can be
`assignedTo<Identity>` on a shipment — a hub has two equally valid ways to satisfy this pattern:

- **Two role-assignment classes**, one per concrete identity type (`OrganisationRoleAssignment`,
  `StaffRoleAssignment`), each with its own `assignedTo<Identity>` link. Keep this when the two
  identity types' role vocabularies, contexts, or lifecycle genuinely diverge.
- **One role-assignment class** whose identity-facing link ranges over a shared abstract
  supertype (a named class, e.g. `Party`, or an anonymous `owl:unionOf` of the concrete types)
  when the roles, contexts, and validity rules are the same regardless of which concrete type
  holds them.

Introducing a named abstract supertype is a structural convenience for the second option, not a
requirement of this pattern — it is only worth the extra class when something else in the hub (a
shared property, a shared reference-model parent, a cross-cutting query) needs to address "any
role-bearing identity" without enumerating the concrete types. Do not add it purely because two
concrete types happen to share a role shape once; check whether the concrete types already share
a natural common ancestor in the imported reference models before inventing a new one.

**The two identity types do not have to use the same physical representation.** One concrete
type's evidence may support the full reified link entity (a source table carrying role + context
+ identity as its own grain) while another's evidence only supports the `physical_simplification`
boolean-flag escape hatch described in the next section (a source table carrying only
per-identity boolean role columns, no independent role+context grain at all). Evaluate the
escape hatch's three preconditions per identity type, not once for the whole pattern
application — a hub is not required to pick one physical shape and apply it uniformly across
every identity type that plays the role.

## When NOT to use — flattened boolean role flags as a physical simplification

A boolean flag per role directly on the identity (`isCarrier`, `isForwarder`) is an **acceptable
physical simplification** when: the pack's first slice does not need role history, one identity
never holds a role concurrently with a conflicting one, and the flags are documented as a
denormalised projection of the role-assignment link entity — never as the semantic model itself.
If any of those three conditions stops holding, materialise the full link entity.

## Worked example

```turtle
:PartyRoleAssignment a owl:Class .

:assignedToParty a owl:ObjectProperty ;
    rdfs:domain :PartyRoleAssignment ;
    rdfs:range :Party .

:inContextOfBooking a owl:ObjectProperty ;
    rdfs:domain :PartyRoleAssignment ;
    rdfs:range :Booking .

:hasRole a owl:DatatypeProperty ;
    rdfs:domain :PartyRoleAssignment ;
    rdfs:range xsd:string .   # constrained to the pack's role vocabulary
```

One `Party` record; one `PartyRoleAssignment` per (party, role, booking) triple — the same party
can be Shipper on one assignment and Consignee on another without duplicating the party.

## Anti-patterns

- **Subclassing the identity by role** (`Shipper subClassOf Party`) — breaks the moment one
  organisation plays two roles, and requires re-typing the record when its role changes. The
  exempt standards overlays (see Applicability) are the only sanctioned instances, and even
  there the subclasses are deprecated for hub use. Watch the **back-door variant** too:
  asserting a reusable property that declares `rdfs:domain <RoleParent>` on a hub identity
  class infers the subsumption silently — which is why `bsp/party`'s reusable properties
  (`hasAddress`, `hasContact`, ...) are deliberately domainless (`REUSABLE — no rdfs:domain
  by design`).
- **Treating equal role labels as equivalent classes** across standards (BSP `TradeParty`, DCSA
  `ShippingParty`, MMT `TransportParty`) without checking whether each is genuinely a role overlay
  on the same durable identity or a distinct grain.

## Grain collisions

- **Party.** BSP, DCSA, MMT, IMO, and TIC each define a role-bearing party parent with a different
  context. None of them is the durable identity on its own — each is evidence for a role overlay.
- **Location.** DCSA specialises `Location` by shipment role (Port of Loading, Port of Discharge).
  Materialising those as separate physical places duplicates one port that plays several roles.
