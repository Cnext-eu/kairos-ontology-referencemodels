# Sustainability Model Sheet

> **Document Control**  
> **Framework:** Kairos Ontology Toolkit  
> **Document date:** 2026-06-15

| Item | Details |
|---|---|
| What is it? | A sustainability ontology for transport and logistics, aligned with ISO 14083, GLEC, EU MRV/ETS, and IMO efficiency schemes. |
| Main focus | Carbon emissions, emission factors, energy consumption, fuel and ESG-related indicators. |
| Why selected in this blueprint | Enables consistent emissions and energy semantics directly tied to logistics operations and reporting. |
| Who is behind it | Standards-led alignment (ISO/GLEC/EU/IMO) with Kairos implementation. |
| Official site / references | https://www.iso.org/standard/78864.html |
| Ontology / OWL reference | `https://www.kairosflow.ai/ont/sustainability#` |
| Adoption context | Increasingly required for compliance reporting and sustainability KPI governance in logistics networks. |
| Kairos modules used | `sustainability/carbon`, `sustainability/energy`. |

## Internal reference

- `ontology-reference-models/derived-ontologies/Sustainability/README.md`

## Annex A — Main classes (high-level overview)

> This is a high-level overview of representative classes (not a full class catalog).

| Class | High-level explanation | Example properties |
|---|---|---|
| `CarbonEmission` | Measured or calculated emission result for logistics activity. | `co2eAmount`, `calculationMethod`, `reportingPeriod` |
| `EmissionFactor` | Conversion factor used to compute emissions from activity data. | `factorValue`, `factorUnit`, `factorSource` |
| `CO2Intensity` | Emission intensity indicator normalized by transport work. | `intensityValue`, `intensityUnit`, `transportWorkBasis` |
| `EnergyConsumption` | Measured energy/fuel use in operations and transport legs. | `energyAmount`, `energyUnit`, `consumptionPeriod` |
| `FuelType` | Fuel categorization supporting energy and emission accounting. | `fuelCode`, `fuelCategory`, `defaultEmissionFactor` |
| `EmissionReport` | Reporting object for compliance and ESG disclosure outputs. | `reportIdentifier`, `reportingScope`, `submissionDate` |
