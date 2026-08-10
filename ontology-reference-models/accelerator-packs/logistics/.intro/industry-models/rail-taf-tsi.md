# RAIL (TAF TSI) Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-08-10

| Item | Details |
|---|---|
| What is it? | A rail freight ontology derived from the EU TAF TSI data catalogue — the regulated message set exchanged between railway undertakings and infrastructure managers. |
| Main focus | Train path request and allocation, rail consignment order, train running and forecasts, wagon and train composition, and rail party roles. |
| Why selected in this blueprint | Rail was one of two modes with no reservation-grain target, so a multimodal order could not state how a rail leg was actually procured. TAF TSI is the only rail freight model that is both regulated and machine-readable. |
| Who is behind it | European Union Agency for Railways (ERA); TAF TSI is EU law. The Kairos derived ontology is authored by the Kairos Ontology Team. |
| Official site / references | Commission Regulation (EU) No 1305/2012, Annex D.2 Appendix F; data catalogue at https://github.com/EU-Agency-for-Railways/TSI_TAF |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/rail#` |
| Adoption context | Mandatory for rail freight interoperability across the EU network; realised operationally through PCS (path coordination) and ORFEUS (electronic consignment note). |
| Kairos modules used | `rail/path-request`, `rail/consignment`, `rail/party` (reservation grain); `rail/train-running`, `rail/rolling-stock` (movement grain); `rail/shared-kernel`. |

## Grain — read this before modelling

Rail spans **two** grains, and the split is the part most often got wrong. The path request
and consignment order are the *reservation* (grain 3) — what was booked. Train running and
rolling stock are the *movement* (grain 4) — what actually ran, with which wagons. They
land in different client domains (`booking` and `intermodal` respectively) precisely so a
hub can hold a path reserved months before the train that runs against it.

There is deliberately **no `RailOrder`**: mode never lives on the order grain — see
`blueprints/patterns/multimodal-order-leg`. The CIM consignment note is document grain and
is already modelled as `mmt/documents#RailConsignmentNote`.

## Internal reference

- `ontology-reference-models/derived-ontologies/RAIL/README.md`
- `ontology-reference-models/blueprints/patterns/multimodal-order-leg/pattern.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `PathRequestMessage` | A railway undertaking asks each infrastructure manager involved for a train path. Opens the reservation. | `typeOfRequest`, `hasPathInformation`, `requestedBy` |
| `ConsignmentOrderMessage` | The rail consignment order passed from lead RU to RU — the ORFEUS electronic consignment note backbone. | `dossierNumber`, `hasConsignmentLevelData`, `sendingRU`, `receivingRU` |
| `RailwayUndertaking` | The operator of rail freight services, contracting with the infrastructure manager for capacity. | `companyCode` |
| `InfrastructureManager` | The party responsible for the network and for allocating train paths; receives the path request. | *(role class; identified via shared-kernel identifiers)* |
| `TrainRunningInformationMessage` | Movement-grain report at agreed reporting points: arrival, departure, run-through, or divergence. | `reportsTrain`, `hasRunningData` |
| `TrainCompositionMessage` | The composition of the proposed train, sent RU to IM — which wagons, in what order. | `hasWagonAtDeparture`, `compositionFor` |
