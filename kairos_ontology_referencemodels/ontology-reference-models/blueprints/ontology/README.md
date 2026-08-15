# Blueprint Ontology

**Kairos-authored OWL classes. Not a standard, not derived from one.**

This is the third module under `blueprints/`, alongside `archetypes/` (composition catalogs) and
`patterns/` (shapes and naming). Those two describe how to compose and name things that already
exist. This one **declares classes** — and is therefore the one with the highest bar to entry.

## Why this tier exists

`derived-ontologies/` is bound to be faithful to its source standard. A business grain that no
standard defines cannot live there without corrupting that contract, and force-fitting it into
the nearest standard class silently changes what that class means for every other consumer.

So a grain with real evidence behind it and no standard behind it had, until now, nowhere to go.
That is this module.

## Admission bar

A class enters this module only when **all** of the following hold:

1. A **standards audit** is on record showing that every candidate in the installed models
   expresses a *different grain* — not merely a different name. The audit names the candidates
   it rejected and why.
2. The grain is **portable** across more than one archetype or client, not an artefact of one
   hub's source system.
3. The class is **narrow**: identity, lifecycle, and outward object relationships only. It does
   not absorb properties owned by another domain in order to be convenient to query.
4. It is recorded in the owning pack's `canonical-class-registry.yaml` with an honest
   `evidence_basis`.

If a candidate fails (1), it belongs in `derived-ontologies/`. If it fails (2), it belongs in
the hub. If it fails (3), it is a report, not a class.

## Contents

| Domain | Module IRI | Holds |
|---|---|---|
| `transport-order/` | `https://www.kairosflow.ai/ont/blueprint/transport-order` | `TransportOrder`, `CarrierReservation` |

### `transport-order`

Closes the gap recorded in
[issue #29](https://github.com/Cnext-eu/kairos-ontology-referencemodels/issues/29): the
Logistics Accelerator's Booking domain claimed to own "transport orders" while no class
expressed that grain. The audit in that issue rejected DCSA `Booking` (carrier capacity
reservation), DCSA `Shipment` (carrier-side transaction), BSP `PurchaseOrder`/`SalesOrder`
(commercial buy/sell), TIC `Order` (terminal handling directive), and MMT
`TransportInstructions` (instruction content, no durable job identity).

Paired with the [`multimodal-order-leg`](../patterns/multimodal-order-leg/pattern.md) pattern,
which holds the four-grain shape and the per-mode standard-alignment targets.

## Versioning

`VERSION` is SemVer for this module, independent of the repo `VERSION`. `scripts/version_manager.py`
requires every `owl:versionInfo` in every `.ttl` here to equal it.

- **PATCH** — comment or label copy-edit.
- **MINOR** — new class, new property, new domain module.
- **MAJOR** — removed or renamed class/property/IRI, changed grain of an existing class.

## Not in scope

Hub-local specialisations. A hub binding its own ocean reservation class to both
`blueprint:CarrierReservation` and `dcsa:Booking` does that in its own namespace — this module
declares the slot, never the mode-specific subclass.
