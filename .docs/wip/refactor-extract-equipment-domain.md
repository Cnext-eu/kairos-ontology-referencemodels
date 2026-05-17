# Refactoring Plan: Extract Equipment Domain from Cargo

## Goal

Move container-related concepts from `cargo.ttl` into a new `equipment/equipment.ttl` domain, aligned with the Logistics Accelerator Blueprint.

---

## Step 1 — Create `model/ontologies/equipment/equipment.ttl`

New file with:
- Namespace: `https://<company>/ont/equipment#`
- Imports: `https://www.kairosflow.ai/ont/mmt/equipment#` and `https://www.kairosflow.ai/ont/dcsa/equipment#`
- Move these from cargo.ttl:
  - `:Container` class → make it `rdfs:subClassOf mmt-equipment:FreightContainer`
  - `:ContainerType` class + all type individuals (type20GP, type40HC, etc.)
  - `:hasContainerType` property
  - `:containerNumber`, `:sealNumber`, `:containerTareWeightKg` data properties

## Step 2 — Trim `cargo.ttl`

Remove from cargo.ttl:
- `:Container` class
- `:ContainerType` class and all individuals
- `:hasContainer` object property
- `:hasContainerType` object property
- `:containerNumber`, `:sealNumber`, `:containerTareWeightKg` data properties

Keep in cargo.ttl:
- `:CargoItem` (subclass of mmt-cargo:CargoItem)
- All cargo data properties (grossWeightKg, volumeM3, chargeableWeightKg, numberOfPackages, packageType, hsCode, goodsDescription)
- `:hasCargoItem` property

## Step 3 — Add cross-reference in `consignment.ttl`

Add a loose-coupled property to link forwarding jobs to equipment:

```turtle
:hasEquipment a owl:ObjectProperty ;
    rdfs:label "has equipment"@en ;
    rdfs:comment "Links a forwarding job to assigned transport equipment (containers, trailers)."@en ;
    rdfs:domain :ForwardingJob ;
    rdfs:range owl:Thing .
```

Use `owl:Thing` as range — this avoids consignment needing to `owl:imports` the equipment domain.

## Step 4 — Update `_master.ttl`

Add:
```turtle
owl:imports <https://<company>/ont/equipment> .
```

## Step 5 — Update README domain table

Add the Equipment row:

| Equipment | Containers, trailers, reefer units, ISO types | `equipment/equipment.ttl` | ✅ Modeled |

## Step 6 — Validate & commit

```bash
python -m kairos_ontology validate --syntax
```

---

## Design rationale

- **Blueprint alignment**: Equipment is its own domain in the Logistics Accelerator (imports MMT + DCSA equipment modules)
- **Source system alignment**: Both CW1 (`JobContainer`) and Soloplan (`Fahrzeug`) treat equipment as separate entities from cargo
- **Loose coupling**: Domains reference each other via `owl:Thing` range, avoiding circular imports
- **Future-proof**: Equipment domain can later track container lifecycle, maintenance, and fleet independently of cargo contents
