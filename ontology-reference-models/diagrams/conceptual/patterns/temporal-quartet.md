# Pattern: Temporal quartet

**Closes gap 8 (partly).** Almost every transport aggregate carries the same timestamp
distinction — **requested**, **planned**, **estimated**, **actual** — crossed with a start/arrival
and an end/departure event. Without a shared convention, each class reinvents the words for the
same eight timestamps. This pattern names them once, normatively.

```mermaid
flowchart TB
  subgraph START["Start / Arrival"]
    RS["requestedStart / requestedArrival"]
    PS["plannedStart / plannedArrival"]
    ES["estimatedStart / estimatedArrival"]
    AS["actualStart / actualArrival<br/><small>immutable once observed</small>"]
  end
  subgraph END["End / Departure"]
    RE["requestedEnd / requestedDeparture"]
    PE["plannedEnd / plannedDeparture"]
    EE["estimatedEnd / estimatedDeparture"]
    AE["actualEnd / actualDeparture<br/><small>immutable once observed</small>"]
  end

  classDef req fill:#eef4ff,stroke:#3b6ea8;
  classDef plan fill:#e8f7e9,stroke:#3aa657;
  classDef est fill:#fff3d6,stroke:#d8a13b;
  classDef act fill:#f3e8ff,stroke:#8a3bd8;
  class RS,RE req;
  class PS,PE plan;
  class ES,EE est;
  class AS,AE act;
```

## The lifecycle each qualifier captures

```mermaid
flowchart LR
  REQ["requested<br/><small>what was asked for</small>"] --> PLAN["planned<br/><small>what the carrier committed</small>"] --> EST["estimated<br/><small>prediction, updated live</small>"] --> ACT["actual<br/><small>observed — corrections append, never overwrite</small>"]
```

Use `Start`/`End` for a duration-bearing activity, `Arrival`/`Departure` for a point-of-presence
event — **never mix the two on one class**, and never substitute a synonym (`eta`, `expected`,
`due`) for `estimated`/`requested`. Most classes need only a subset; a `TransportCall` has no
"requested" leg (a carrier does not request its own port call), so only six of the eight apply.

Source: [`blueprints/patterns/temporal-quartet`](../../../blueprints/patterns/temporal-quartet/pattern.md).
Naming is **normative**; the synonym ban is the specific drift this pattern stops.
