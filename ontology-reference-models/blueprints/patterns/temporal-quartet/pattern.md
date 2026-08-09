# Temporal Quartet

**Normativity:** naming — normative. Participants and cardinality rules — advisory.

## Problem

Almost every transport aggregate carries the same four-way timestamp distinction — what was
requested, what was planned, what was estimated, and what actually happened — crossed with
start/arrival and end/departure. Without a shared naming convention, each class that needs this
independently invents its own words for the same eight timestamps. The specific failure this
pattern closes: one client hub carried **four different naming conventions for the same
requested/planned/actual triple across four classes**, because nothing normative existed to copy.
This is exactly why naming, unlike the rest of this pattern, ships normative from day one — the
observed cost is concentrated entirely in naming drift, not in the underlying structure.

## Applicability

Use this pattern on any class that distinguishes what was asked for, planned, estimated, or
actually observed, for either a start/arrival event or an end/departure event. Most transport
aggregates in this pack need a subset of the full quartet — few need all eight properties.

## Participants (advisory)

- **Requested** — what the counterparty asked for (e.g. requested pickup date).
- **Planned** — what the carrier committed to, independent of the request.
- **Estimated** — a forward-looking prediction, updated as execution proceeds.
- **Actual** — what was observed to happen. Immutable once recorded; corrections append, they do
  not overwrite (see the event-envelope guidance in `capability-coverage.yaml`'s `event-history`
  capability).

## Naming (normative)

| Qualifier | Start/arrival property | End/departure property |
|---|---|---|
| Requested | `requestedStart` / `requestedArrival` | `requestedEnd` / `requestedDeparture` |
| Planned | `plannedStart` / `plannedArrival` | `plannedEnd` / `plannedDeparture` |
| Estimated | `estimatedStart` / `estimatedArrival` | `estimatedEnd` / `estimatedDeparture` |
| Actual | `actualStart` / `actualArrival` | `actualEnd` / `actualDeparture` |

Use `Start`/`End` for a duration-bearing activity (a transport leg, a booking window) and
`Arrival`/`Departure` for a point-of-presence event (a transport call, a port call). Never mix
the two vocabularies on the same class, and never substitute a synonym (`eta`, `expected`,
`due`) for `estimated` or `requested` — that substitution is precisely the drift this pattern
exists to stop.

## Cardinality rules (advisory)

`actual*` properties are `0..1` until observed, then fixed — do not allow a later write to
overwrite an already-recorded `actual*` value; supersession is a new event, not a mutation (see
`qualified-role-assignment` for how to model a correcting record if the pack needs one).

## When NOT to use

A class with only one timestamp and no planning/estimation lifecycle does not need this pattern —
a single `occurredAt` or `recordedAt` property is simpler and more honest about what the class
actually tracks.

## Worked example

```turtle
:TransportCall a owl:Class .

:plannedArrival a owl:DatatypeProperty ; rdfs:domain :TransportCall ; rdfs:range xsd:dateTime .
:estimatedArrival a owl:DatatypeProperty ; rdfs:domain :TransportCall ; rdfs:range xsd:dateTime .
:actualArrival a owl:DatatypeProperty ; rdfs:domain :TransportCall ; rdfs:range xsd:dateTime .
:plannedDeparture a owl:DatatypeProperty ; rdfs:domain :TransportCall ; rdfs:range xsd:dateTime .
:estimatedDeparture a owl:DatatypeProperty ; rdfs:domain :TransportCall ; rdfs:range xsd:dateTime .
:actualDeparture a owl:DatatypeProperty ; rdfs:domain :TransportCall ; rdfs:range xsd:dateTime .
```

`TransportCall` has no "requested" leg — a carrier does not request its own port call — so only
six of the eight properties apply. That is expected; the pattern names the properties a class
needs, it does not require all eight.

## Anti-patterns

- **Inventing a synonym** (`eta`, `expectedTime`, `due_date`) instead of `estimated*` /
  `requested*`. This is the exact defect that motivated shipping this pattern normative.
- **Overwriting `actual*` in place** on a correction instead of appending a new observation.

## Grain collisions

None specific to this pattern.
