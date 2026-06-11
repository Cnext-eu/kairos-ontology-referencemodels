# TIC 4.0 Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-11

| Item | Details |
|---|---|
| What is it? | A terminal-industry ontology aligned with TIC 4.0 and BSI PAS 4000, modularized for infrastructure, handling, automotive, party, locations, and events. |
| Main focus | Terminal operations and physical assets: berths, yards, gates, handling moves, and automotive services. |
| Why selected in this blueprint | Adds terminal-depth semantics that are not fully covered by shipping and multimodal transport models. |
| Who is behind it | TIC4.0 ecosystem and BSI standardization (PAS 4000 context). |
| Official site / references | https://tic40.org/standards/ |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/tic#` |
| Adoption context | Positioned for ports and terminal operators standardizing operational and event semantics. |
| Kairos modules used | `tic/terminal-infrastructure`, `tic/handling-operations`, `tic/locations`, `tic/events`, `tic/automotive-services`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/TIC/README.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `Terminal` | Port/terminal operational facility as core site entity. | `terminalCode`, `hasBerth`, `terminalOperator` |
| `Berth` | Vessel mooring position where loading/discharge activities occur. | `berthIdentifier`, `berthLength`, `maxDraft` |
| `YardArea` | Storage and staging area for equipment/cargo handling flows. | `yardBlockCode`, `capacityTEU`, `temperatureControlled` |
| `CargoVisit` | Terminal visit lifecycle context for cargo/equipment movements. | `visitReference`, `arrivalTime`, `departureTime` |
| `Move` | Operational handling action (load/discharge/lift/horizontal). | `moveType`, `plannedTime`, `executedTime` |
| `TerminalEvent` | Event object for gate, yard, vessel, and service milestones. | `eventType`, `eventTimestamp`, `eventLocation` |
