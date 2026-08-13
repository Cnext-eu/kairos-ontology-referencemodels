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
deprecated subclasses demoted to `recommended`. Nothing breaks; the subclass IRIs stay
resolvable for any future message-level mapping (none exists as an artifact today — see
precondition 4 below).

### B. Full refactor (REJECTED for now)

Delete the subclasses and ship only the role-assignment shape. Knock-on chain measured
before rejecting:

- `hasBuyer` / `hasSeller` / `hasShipper` / `hasConsignee` / `hasCarrier` / `hasManufacturer`
  (bsp/party) **and** `issuingBank` / `advisingBank` / `confirmingBank` (bsp/financial, ranged
  over the deprecated `party:Bank` — missed by the original #41 inventory) **range over the
  subclasses** — all must be redesigned (role assignments or re-ranged).
  *Historical as of BSP 2.0.0 (issue #50/#51): all 9 were re-ranged to `:TradeParty` under the
  new `bsp-party:hasParty` landing pad, riding the major the `estimatedDeliveryDate` rename
  already forced.*
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

Preconditions to revisit, in order — **measured status as of the 2026-08 audit (issue #51)**:

1. The `party-role-parents` stakeholder decision lands on a durable-identity model.
   *Status: OPEN and cold — the register entry is byte-identical since pack 1.8.0 (evidence
   string "Stakeholder confirmation 2026-07-21"), `maturity: experimental`, and its disposition
   is test-pinned (`tests/test_logistics_blueprint.py`). Everything below stays parked on it.*
2. No shipped module property ranges over a role subclass.
   *Status: MET for BSP as of 2.0.0 (all 9 props re-ranged to `:TradeParty` under
   `bsp-party:hasParty`). MMT's 5 typed props (`hasConsignor`/`hasConsignee`/`hasCarrier`/
   `hasFreightForwarder`/`hasNotifyParty`) still range subclasses, but all already sit under
   `mmt:hasParty` (range `TransportParty`) — widening them is deferred to the removal release
   itself, since it buys nothing while precondition 1 is parked and one live external binding
   exists.*
3. A survey of client hubs shows no live bindings, or a migration window is agreed.
   *Status: surveyed (16 local hubs, 2026-08). Exactly ONE live binding to a deprecated
   BSP/MMT subclass: tsplit-ontology-hub `model/ontologies/party/party.ttl:51`
   (`:Carrier rdfs:subClassOf mmt-party:Carrier`; the same file has a pre-existing dangling
   `bsp-party:Party` reference and its own PartyRole individuals — it needs a touch anyway).
   DCSA role subclasses ARE bound in cldn6 and cldn2-1 conformance artifacts — DCSA removal
   would not be low-impact.*
4. Message-level interop needs are covered another way (e.g. role-code-driven mapping).
   *Status: vacuous today — no message-mapping artifact (XSD/EDI/projection) exists anywhere in
   the repo; the keep-rationale above is untested in both directions. Cannot be positively
   closed until precondition 1 moves.*

Then removal is a BSP/MMT major with the old→new table in the CHANGELOG, per the
term-rename policy in CONTRACT.md.

## Pattern/exemption bookkeeping

`qualified-role-assignment/pattern.yaml` `exemptions` names the **two still-live**
standards-overlay role parents (`dcsa/party#ShippingParty`, `imo/party#MaritimeParty`), each
with a cited reason. `bsp/party#TradeParty` and `mmt/party#TransportParty` need no entry:
their role subclasses are `owl:deprecated`, deprecated subjects are outside the
subclass-identity-by-role detection, and an exemption for them would be flagged as stale by
the conformance check's usage stats — un-deprecating a subclass revives the warning, which is
the guard working.

`dcsa/party` and `imo/party` have NOT received the hybrid machinery. The original deferral
rationale here ("smaller overlays with no archetype-required role subclasses at stake") was
**wrong**, corrected by the 2026-08 audit: `shipping-carrier.yaml` pins `dcsa/party#Carrier`,
`#Shipper`, `#Consignee`, `#BookingParty` (and `#ShippingParty`) at `tier: required`; nine
DCSA properties range over the subclasses (booking 5, transport-documents 3 — all with
`hasParty`/`hasDocumentParty` landing pads already in place — plus one parent-ranged); and the
two most recently active hubs (cldn6, cldn2-1) bind them in conformance artifacts. The DCSA
deferral is deliberate (source fidelity to DCSA's own normative role-typed shape) but it is
not cost-free, and expanding #51 to DCSA would cost MORE than the BSP/MMT hybrid did, not
less. IMO is the cheap one (zero external property coupling, zero hub bindings) — but roughly
half its "subclasses" are not contextual roles at all (FlagAuthority/ClassificationSociety/
PortAuthority are durable organisation kinds; MasterOfVessel and the security officers are
persons), so a uniform hybrid would be semantically wrong there.

A **fifth role parent** surfaced in the 2026-08 audit: `tic/party#TerminalParty`
(`TerminalOperator`/`Stevedore` subclasses, with live `rdfs:domain :TerminalOperator` usage).
It sits below the conformance check C's ≥3-subclass detection threshold, which is why the #41
sweep never flagged it. It is covered by its entry in the overlap register's
`party-role-parents.class_uris` (audit-sourced evidence line), NOT by a pattern exemption —
an exemption would never be exercised at the current threshold and would be flagged as stale
on every CI run.
