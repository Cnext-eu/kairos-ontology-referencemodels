# Party design — role subclasses vs qualified role assignment

**Status:** decided 2026-08-13 — additive hybrid shipped (BSP 1.6.0, MMT 2.0.0).
Full subclass removal deliberately deferred; see "The reversible path" below.
**Owner decision record:** issue #41, finding 3; `overlap-register.yaml`
`party-role-parents` (`reference_model_gap`, stakeholder-confirmed 2026-07-21).

## The problem

`bsp/party` shipped 14 role subclasses of `TradeParty` (Buyer, Seller, Shipper, Consignee,
Carrier, FreightForwarder, CustomsBroker, Bank, Manufacturer, Supplier, NotifyParty,
InsuranceProvider, TerminalOperator, WarehouseKeeper); `mmt/party` shipped 8 under
`TransportParty`. That is the exact `subclass-identity-by-role` anti-pattern the
`qualified-role-assignment` pattern (normative naming) rejects — and both modules are
`tier: required` in the freight-forwarder archetype, so a pattern-conformant hub could not
reuse the modules it was required to import.

The cost is not theoretical. Real source data has one organisation holding several roles at
once — one row carrying both a debtor and a creditor flag; another carrying importer,
exporter, forwarding-agent and carrier categories concurrently. Concretely:

> ACME Logistics BV is shipper on booking B123, carrier on shipment S9, and a creditor in
> finance — simultaneously. With role subclasses, ACME must be typed
> `Shipper ∧ Carrier ∧ ...`: roles are global and context-free. There is no way to say
> "shipper *on this booking*", no role validity period, no history.

A second-order trap compounded it: the reusable object properties (`hasContact`,
`hasAddress`, `hasBillingAddress`, `hasShippingAddress`) carried `rdfs:domain :TradeParty`,
so asserting any of them on a hub's own identity class silently inferred
`⊑ TradeParty` — re-creating the anti-pattern by the back door and forcing hubs to
redeclare the properties locally.

## The two candidate approaches

### A. Additive hybrid (CHOSEN)

Keep the subclasses, add the pattern-conformant machinery beside them:

```turtle
# subclasses stay, flagged
:Shipper a owl:Class ; rdfs:subClassOf :TradeParty ;
    owl:deprecated true .   # standards overlay — never the hub's role model

# new machinery (BSP 1.6.0)
:PartyRoleCode a owl:Class .                  # governed code list (governed-code-list pattern)
:TradePartyRoleAssignment a owl:Class .       # (identity, role, context, validity) link entity
:assignedToTradeParty rdfs:domain :TradePartyRoleAssignment ; rdfs:range :TradeParty .
:hasRole              rdfs:domain :TradePartyRoleAssignment ; rdfs:range :PartyRoleCode .
:roleValidFrom / :roleValidTo                 # validity period
# inContextOf<Context> — declared by the hub per context class

# reusable props: domain REMOVED (marked "REUSABLE — no rdfs:domain by design")
:hasAddress rdfs:range ref-data:Address .
```

Data: ACME is **one** `TradeParty` with three `TradePartyRoleAssignment` nodes —
(SHIPPER, booking B123), (CARRIER, shipment S9), (CREDITOR, ledger). Multi-role,
per-context, historizable.

Consequences: BSP 1.5.0 → 1.6.0 (minor — additive + annotations), MMT machinery rides the
2.0.0 already forced by the temporal-quartet renames. Archetypes re-authored in the same
release: role-assignment class + role code list are `required` core concepts; the
deprecated subclasses demoted to `recommended`. Nothing breaks; existing message-level
mappings keep resolving.

### B. Full refactor (REJECTED for now)

Delete the subclasses and ship only the role-assignment shape. Knock-on chain measured
before rejecting:

- `hasShipper` / `hasCarrier` / `hasBuyer` / `hasConsignee` / `hasManufacturer` **range over
  the subclasses** — all must be redesigned (role assignments or re-ranged).
- `mmt/consignment` object properties range over `mmt-party:Consignor` / `Consignee` — MMT
  breaks alongside BSP.
- The freight-forwarder AND shipping-carrier/unit-load-carrier archetypes pin role
  subclasses as core concepts — all re-authored.
- Every existing client hub bound to the subclass IRIs breaks on its next
  `update-refmodels`.
- BSP 2.0.0 + (bigger) MMT 2.0.0 — a coordinated major release train.

## Why hybrid, explicitly

1. **Reversibility.** Hybrid → full delete later is a follow-up release; full delete →
   "we need the subclasses back" is a re-mint. The asymmetry favours hybrid.
2. **The subclasses have real future uses.** UN/CEFACT and DCSA message schemas expose
   role-typed party elements (`Consignor`, `NotifyParty`, ...); mapping to and from those
   messages is most direct when the class exists. Projection/SHACL targets ("all
   carriers") are cheaper from a class than from a role-assignment join. If we deleted
   them now, we would plausibly re-mint them later as views.
3. **A stakeholder decision is already parked.** The durable-party-identity question is
   recorded in `overlap-register.yaml` (`party-role-parents`, `reference_model_gap`,
   confirmed 2026-07-21). A unilateral full refactor from the reference-models repo would
   pre-empt it.
4. **The pattern's goal is met either way.** What #41 required is that the library stop
   contradicting itself and that hubs get a reusable, conformant shape. Hybrid delivers
   both.

## The reversible path to full removal (if ever chosen)

Preconditions to revisit, in order:

1. The `party-role-parents` stakeholder decision lands on a durable-identity model.
2. No shipped module property ranges over a role subclass (redesign `hasShipper` et al.
   first, as their own change with their own consumers checked).
3. A survey of client hubs (they vendor this repo — grep for the subclass IRIs) shows no
   live bindings, or a migration window is agreed.
4. Message-level interop needs are covered another way (e.g. role-code-driven mapping).

Then removal is a BSP/MMT major with the old→new table in the CHANGELOG, per the
term-rename policy in CONTRACT.md.

## Pattern/exemption bookkeeping

`qualified-role-assignment/pattern.yaml` `exemptions` names the four standards-overlay role
parents (`bsp/party#TradeParty`, `mmt/party#TransportParty`, `dcsa/party#ShippingParty`,
`imo/party#MaritimeParty`), each with a cited reason. `dcsa/party` and `imo/party` have
NOT received the hybrid machinery yet — they are smaller overlays with no archetype-required
role subclasses at stake; they inherit the same parked decision.
