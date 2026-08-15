# Logistics Blueprint Sources

This directory contains versioned, source-neutral blueprint evidence and decisions for
the Logistics Accelerator.

- `_schema/` defines the machine-readable registry contracts.
- `evidence/class-inventory.yaml` is generated deterministically from the local ontology
  import closure.
- `evidence/source-shapes/` contains schema-validated synthetic evidence for a freight
  forwarder and a carrier/terminal operating model.
- `convergence-analysis.md` contains the evidence-backed review dossier.
- Canonical, overlap, relationship, and capability registries persist the current review
  state. Pending candidates remain `unresolved` or `deferred`, are experimental, and are
  explicitly excluded from the first slice.

Regenerate the evidence inventory with:

```powershell
uv run python scripts\generate_logistics_inventory.py
```

Check that committed evidence is current with:

```powershell
uv run python scripts\generate_logistics_inventory.py --check
```

Generated evidence is not a semantic decision. Canonical choices require recorded
authority, grain, lifecycle, evidence, confidence, and overlap disposition.

The committed registries intentionally contain no approved concepts or relationships
while stakeholder decisions remain open. Consequently, the Silver Starter profile and
generated contract are not created from these candidates.
