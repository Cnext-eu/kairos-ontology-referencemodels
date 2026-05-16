# Sustainability Ontology

**Namespace:** `https://www.kairosflow.ai/ont/sustainability#`  
**Version:** 1.0.0  
**Created:** 2026-05-16

## Description

Sustainability ontology for carbon emissions, energy consumption, and environmental compliance in transport and logistics. Fully aligned with ISO 14083:2023, GLEC Framework, EU MRV Regulation, IMO DCS, and EU ETS Maritime.

## Structure

```
Sustainability/
├── sustainability.ttl       # Root ontology (imports all modules)
├── carbon/carbon.ttl        # Carbon emissions and GHG accounting
└── energy/energy.ttl        # Energy consumption and fuel management
```

## Domain Modules

### Carbon (`https://www.kairosflow.ai/ont/sustainability/carbon#`)
Carbon emissions, greenhouse gas accounting, and environmental compliance.

**Classes:** CarbonEmission, EmissionFactor, CO2Intensity, WellToWake, TankToWake, Scope1Emission, Scope2Emission, Scope3Emission, TonneKilometre, ModalShiftMetric, CarbonFootprint, EmissionReport, CIIRating, EEXICompliance, EUETSAllowance, CarbonOffset

### Energy (`https://www.kairosflow.ai/ont/sustainability/energy#`)
Energy consumption, fuel types, and energy efficiency for transport operations.

**Classes:** EnergyConsumption, FuelType (HFO, VLSFO, LNG, Methanol, Ammonia, Electric, Hydrogen), EnergySource, RenewableEnergy, Shorepower, EnergyEfficiency, FuelOilConsumption, BunkerDeliveryNote, EnergyPerformanceIndicator

## Standards Alignment

- ISO 14083:2023 — Quantification and reporting of GHG emissions from transport chains
- GLEC Framework — Global Logistics Emissions Council methodology
- EU MRV Regulation — Monitoring, Reporting and Verification of CO2 emissions from maritime transport
- IMO DCS — Data Collection System for fuel oil consumption
- EU ETS Maritime — Emissions Trading System for maritime transport
- GHG Protocol — Corporate accounting and reporting standard (Scope 1/2/3)
- IMO EEXI — Energy Efficiency Existing Ship Index
- IMO CII — Carbon Intensity Indicator

## Usage

```turtle
@prefix sust: <https://www.kairosflow.ai/ont/sustainability#> .

<http://example.org/my-ontology> a owl:Ontology ;
    owl:imports <https://www.kairosflow.ai/ont/sustainability#> .
```

Importing the root ontology (`sustainability.ttl`) automatically imports all domain modules.
