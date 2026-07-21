# Logistics Blueprint Convergence Analysis

> **Status:** Partial stakeholder review. Only outcomes listed below are approved.

## Reviewed outcomes

| Decision | Outcome | Release effect |
|---|---|---|
| LOG-BP-001 Party authority | Approved 2026-07-21: neutral durable Party identity plus qualified contextual Party Role Assignment; standard-specific party/role classes remain overlays until mappings are proven. | Recorded as a reference-model gap. Party remains outside the first slice until standards audit and ontology review succeed. |

This dossier separates evidence-backed grain distinctions from decisions that require
stakeholder confirmation. Machine-readable registries use `unresolved` or `deferred`
until those decisions are reviewed; no unresolved concept is eligible for the first
Silver slice.

## Decision principles

1. Similar labels do not establish `owl:equivalentClass`.
2. A canonical choice must preserve authority, grain, identity, and lifecycle.
3. Durable identities must not be conflated with contextual roles or usages.
4. Existing cross-standard links remain informative until equivalence is proven.
5. Client-specific source shapes may select optional capabilities, but cannot redefine
   accelerator semantics.

## Session A: authority and vocabulary

| Cluster | Evidence-backed finding | Pending recommendation |
|---|---|---|
| Party | BSP `TradeParty`, DCSA `ShippingParty`, MMT `TransportParty`, and IMO `MaritimeParty` are role-bearing parents with different contexts. | **Approved architecture:** audit a neutral durable Party identity and qualified role-assignment pattern. BSP/DCSA/MMT/IMO classes remain standards overlays, not canonical identity. |
| Location | DCSA and MMT both define physical locations; DCSA also specializes locations by shipment role. | Separate durable place/facility identity from contextual loading, discharge, receipt, delivery, and transshipment roles. |
| Booking | DCSA `Booking` reserves carrier capacity/equipment; BSP orders govern commercial buy/sell transactions; TIC orders direct terminal moves. | Use DCSA `Booking` as the carrier-reservation candidate. Never treat the three order concepts as equivalents. |
| Shipment and consignment | DCSA Shipment is a carrier transport transaction. MMT Consignment is a goods collection from one consignor to one consignee. | Keep both grains and link them; do not collapse them into one table. |
| Equipment | DCSA Container and MMT TransportEquipment describe durable assets; requested equipment, utilized equipment, and container journey describe different usages. | Preserve four grains: asset, request, allocation, and journey. |
| Route execution | Route, planned leg, actual movement, call/stop, port call, and terminal move have different identities and lifecycles. | Use complementary grains rather than a universal Movement class. |
| Event | DCSA, MMT, BSP, and TIC event classes have different scopes and subject models. | Use a source-neutral event envelope only after subject, correction, and planned/estimated/actual semantics are agreed. |

## Session B: grain, identity, and lifecycle

| Candidate concept | Grain | Identity | Lifecycle boundary |
|---|---|---|---|
| Party identity | One durable person or organisation | Issuer-scoped party identifier; role-independent | Creation, merge, activation, retirement |
| Party role assignment | One party playing one role in one context | Party + role + context + validity | Starts and ends independently of party |
| Location identity | One durable physical place or facility | UN/LOCODE plus facility code where applicable | Independent of route participation |
| Location role assignment | One location playing one role in one transport context | Location + role + booking/shipment/leg | Valid for the scoped transport context |
| Booking | One carrier capacity/equipment reservation | Carrier booking reference scoped to carrier | Requested through confirmation, rejection, cancellation |
| Shipment | One carrier-side transport transaction | Issuer-scoped shipment reference | Booking handoff through delivery/closure |
| Consignment | One identifiable goods collection from consignor to consignee | Issuer-scoped consignment reference | Acceptance through completion across legs |
| Consignment item | One separately identifiable line within a consignment | Consignment + item identifier | Bound to consignment composition |
| Equipment asset | One durable physical transport asset | ISO 6346 container number or scoped equipment identifier | Acquisition/registration through retirement |
| Equipment request | One requested type/quantity line | Booking + request line | Requested through fulfilment/cancellation |
| Equipment utilisation | One allocation of an asset to a shipment | Shipment + allocation identifier | Allocation through release |
| Container journey | One operational cycle for a container in a shipment | Container + journey identifier | Pickup through return/completion |
| Transport route | One reusable ordered path | Route identifier/version | Authored, revised, retired |
| Transport leg | One planned segment using one mode | Route/plan + sequence | Planned and revised before execution |
| Transport movement | One actual traversal between locations | Execution identifier | Dispatched through completion |
| Transport call | One means-of-transport interaction at a facility | Call reference | Arrival through departure |
| Event | One observed, estimated, or planned occurrence | Source system + event identifier | Append, correct, or supersede; do not overwrite |
| Transport document | One document identity, separate from versions and states | Issuer + document number | Draft, issue, amend, surrender, cancel |

## Session C: overlap disposition

The current machine register deliberately records every cluster as `unresolved`.
Stakeholders should choose one of the supported dispositions only after reviewing the
following constraints.

| Cluster | Must remain distinct | Candidate alignment |
|---|---|---|
| Party | Identity versus Carrier, Shipper, Consignee, Booking Party, Freight Forwarder, Importer, and Exporter roles | Cross-standard role mappings, never duplicate party masters |
| Location | Physical Port versus Port of Loading/Discharge and other itinerary roles | Role assignment to one durable location |
| Booking/order | Carrier Booking versus Purchase/Sales Order versus terminal Order | Explicit business-process links only |
| Shipment/consignment | Shipment, Consignment, Master/House Consignment, Consignment Item | Existing `bookedConsignment` bridge supports related distinct grains |
| Equipment | Asset, request, utilisation, journey, operational status | Explicit allocation and journey relationships |
| Movement | Reusable route, plan leg, execution movement, transport call, regulatory port call, terminal move | Sequence and realization relationships |
| Event | Transport, equipment, document, terminal, and shipment event scopes | Common envelope only if subject roles and event semantics converge |
| Document | Generic document, DCSA transport document, MMT transport document, versions and states | Shared parent or mappings; no forced equivalence |
| Identifier | Booking, consignment, container, document, IMO, MMSI, and call-sign identifiers | Scoped properties by default; structured assignment when issuer/validity matter |
| Measurement | BSP generic measurements versus MMT cargo measurements | MMT authority for cargo context; no blanket equivalence |
| Status | Current scalar status versus temporal status observation versus lifecycle event | Aggregate-specific vocabularies |

## Session D: feature-rich relationships

These relationships are candidates for later approval. Existing properties should be
reused where their declared domain and range match the selected canonical classes.

| Relationship pattern | Existing evidence | Open semantic question |
|---|---|---|
| Booking to party roles | DCSA `hasBookingParty`, `hasShipper`, `hasConsignee`, `hasCarrier` | Are roles snapshot values or temporally qualified assignments? |
| Booking to shipping instruction | DCSA `hasShippingInstruction` | Can instructions version independently? |
| Booking to equipment request | DCSA `hasRequestedEquipment` | Are request lines mutable or versioned? |
| Shipment to equipment utilisation | DCSA `hasUtilizedEquipment` | When is the physical unit assigned? |
| Shipment to consignment | Supply Chain `bookedConsignment` | Split/consolidation cardinality |
| Consignment to item | MMT `hasConsignmentItem` | Stable item identity across regrouping |
| Route to leg | MMT `hasTransportLeg` | Ordered sequence and revision semantics |
| Event to transport call | DCSA `hasTransportCall` | Can one event concern multiple calls or subjects? |
| Consignment to event | MMT `hasEvent` | Event ownership versus many-subject observation |

## Explicit reference-model gaps

These are audit candidates, not authorization to add classes:

1. Neutral durable Party/Organisation plus qualified Party Role Assignment.
2. Qualified Location Role Assignment for itinerary and shipment context.
3. Booking amendment/version history.
4. General equipment allocation/utilisation outside the container-specific model.
5. Ordered stop and plan-to-execution realization pattern.
6. Source-neutral event envelope with subject roles and correction/supersession.
7. Cross-domain structured Identifier Assignment.
8. Temporal Status Observation and governed code-list pattern.

## Required stakeholder decisions

1. Durable Party and Location identity architecture.
2. Booking-Shipment-Consignment split and consolidation cardinalities.
3. Shipment, shipping-instruction, and transport-document aggregation/versioning.
4. Equipment assignment point and allocation lifecycle.
5. Operational Transport Call versus regulatory Port Call boundary.
6. Event subject grain and correction semantics.
7. Identifier issuer/scheme governance.
8. Status history versus current-state projection.
9. Whether cross-model links remain informational mappings or justify OWL axioms.
