# Freight Forwarder - SME Discovery Guide

**Archetype:** `freight-forwarder`
**Pack:** `accelerator-packs/logistics`
**Target sector:** Freight forwarders, NVOCCs, multimodal logistics service providers,
and customs-capable forwarding businesses.

## 0. How to use this guide

For each section, confirm whether the business `conforms`, `conforms-with-rename`,
`partial`, `deviates`, or considers the concept `not-applicable`. Record terminology,
identifier scope, lifecycle, and cardinality differences. The guide deliberately asks
about business semantics that cannot be inferred from ontology class names.

## 1. Service and principal model

**Why it matters.** Determines whether the forwarder acts only as agent or also contracts
as principal/NVOCC.

**Questions**

1. Do you arrange transport as agent, contract as principal, or both?
2. Which modes are supported and can one consignment span several modes?
3. Do you offer door-to-door, port-to-port, or both?

**Maps to.** `mmt/party#FreightForwarder`, `Carrier`,
`mmt/consignment#TransportRoute`, `TransportLeg`.

## 2. Party identity and contextual roles

**Why it matters.** One organisation may be customer, shipper, consignor, consignee,
carrier, broker, and notify party in different contexts.

**Questions**

1. Is there one party master independent of transaction roles?
2. Are shipper and consignor synonyms in your operation, or contextually distinct?
3. Are carrier contracts held against the carrier organisation or a service-specific role?
4. Do roles have validity dates, branch scope, or compliance state?

**Maps to.** `bsp/party#TradeParty`, `FreightForwarder`,
`mmt/party#TransportParty`, `Consignor`, `Consignee`, `Carrier`.

**Outcome guidance.** Separate masters per role indicate `deviates`; do not assume the
duplicate records represent different real-world parties.

## 3. Quote, booking, and shipment handoff

**Why it matters.** Forwarders may hold an internal job/order before carrier booking and
may create several carrier bookings for one customer instruction.

**Questions**

1. What is the durable customer instruction or forwarding-job identifier?
2. Can one forwarding job create multiple carrier bookings?
3. Are carrier booking changes versioned or overwritten?
4. Is a DCSA Shipment represented directly, or only through carrier references?
5. Which legs does the forwarder subcontract, and which does it execute itself? A leg with no
   carrier reservation is normal — it means the forwarder ran it.
6. Does any order span more than one mode? If yes, confirm the customer is quoted one
   door-to-door price against one order, not one order per mode.

**Maps to.** `blueprint/transport-order#TransportOrder` (the forwarding job),
`blueprint/transport-order#CarrierReservation` (per leg), `dcsa/booking#Booking` (the ocean
reservation), `Shipment`, `ShippingInstruction`, `mmt/consignment#TransportLeg`.

**Outcome guidance.** The grain question is now settled — an internal forwarding job is **not**
equivalent to a DCSA Booking, and `TransportOrder` exists for it (issue #29 audit, `LOG-BP-012`).
What discovery must still establish is the **1..N fan-out**: confirm from source data that one
job can carry several carrier reservations, since a source that can only ever produce one may
not need the order grain separated at all.

If the answer to Q6 is yes, do **not** let the hub type the order by mode. Mode belongs on the
leg — see [`multimodal-order-leg`](../../../blueprints/patterns/multimodal-order-leg/pattern.md).
A hub proposing `OceanOrder`/`RoadOrder` subclasses, or a single `transportMode` field on the
order, has hit a known anti-pattern and should be redirected to the leg.

## 4. Master and house consolidation

**Why it matters.** Consolidation is the principal cross-archetype difference from a
single carrier transaction.

**Questions**

1. Can one house consignment participate in more than one master consignment over time?
2. Can a master contain houses with different consignors or consignees?
3. How are deconsolidation, rollover, split, and merge history retained?
4. Are direct shipments represented without a master/house split?

**Maps to.** `mmt/consignment#Consignment`, `MasterConsignment`,
`HouseConsignment`, `ConsignmentItem`.

## 5. Transport documents

**Questions**

1. Do you issue house waybills while receiving carrier master waybills?
2. Can document identity persist across amendments and re-issuance?
3. Are surrender, release, and cancellation modelled as events or current flags?

**Maps to.** `mmt/documents#TransportDocument`, `MasterWaybill`, `HouseWaybill`.

## 6. Cargo, equipment, and allocation

**Questions**

1. Is equipment requested by type/quantity before a physical unit is known?
2. At what point is a container or other unit assigned?
3. Do you own equipment, track third-party equipment, or only retain carrier references?
4. Are cargo weight and dimensions original, verified, chargeable, or all three?

**Maps to.** `mmt/cargo#Goods`, `Weight`, `Dimension`,
`mmt/equipment#TransportEquipment`, `FreightContainer`.

## 7. Route planning and execution

**Questions**

1. Is the route a reusable lane, a job-specific plan, or both?
2. Are planned legs replaced when execution changes, or retained beside actual movements?
3. Are pickup, cross-dock, terminal, port, and delivery stops explicitly sequenced?

**Maps to.** `mmt/consignment#TransportRoute`, `TransportLeg`.

## 8. Milestones and exceptions

**Questions**

1. Which object is the primary event subject: job, booking, shipment, consignment,
   container, leg, or transport call?
2. How are planned, estimated, and actual times distinguished?
3. Can a carrier correction supersede an earlier event without changing its source ID?
4. Are exceptions separate events, statuses, or cases?

**Maps to.** `dcsa/events#Event`, `TransportEvent`, `EquipmentEvent`,
`DocumentEvent`.

## 9. Customs coordination

**Questions**

1. Do you lodge declarations, prepare data for a broker, or only track filing status?
2. Is one declaration linked to a consignment, house, master, document, or goods-item set?
3. Are import and export declarations separate lifecycles?

**Maps to.** `wco/customs#CustomsDeclaration`, `ImportDeclaration`,
`ExportDeclaration`.

## 10. Structural and lifecycle relationships

Confirm explicitly:

1. forwarding job to carrier booking cardinality;
2. booking to shipment cardinality;
3. shipment to consignment cardinality;
4. master to house consolidation and history;
5. consignment to item composition;
6. route to ordered leg composition;
7. equipment request to physical allocation timing;
8. event-to-subject cardinality and correction behavior;
9. document identity to version/state lifecycle;
10. party and location roles versus durable identities.

## 11. Naming and identifier conventions

Record the business terms for forwarding job, file, shipment, house, master, booking,
load, consignment, route, leg, milestone, and exception. For every identifier record
the issuer, namespace, reuse policy, and whether aliases are retained.
