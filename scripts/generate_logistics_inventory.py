# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Generate deterministic Logistics Blueprint RDF evidence inventory YAML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from .logistics_blueprint_common import (
        BlueprintError,
        dump_yaml,
        load_yaml,
        rdf_inventory,
    )
else:
    from logistics_blueprint_common import BlueprintError, dump_yaml, load_yaml, rdf_inventory

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACCELERATOR = (
    REPO_ROOT
    / "kairos_ontology_referencemodels"
    / "ontology-reference-models"
    / "accelerator-packs"
    / "logistics"
    / "current"
    / "logistics-accelerator.ttl"
)
DEFAULT_CATALOG = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models" / "catalog-v001.xml"
DEFAULT_OUTPUT = (
    DEFAULT_ACCELERATOR.parent / "blueprint" / "evidence" / "class-inventory.yaml"
)


def build_inventory(accelerator: Path, catalog: Path) -> dict:
    """Generate the inventory entirely in memory."""
    return rdf_inventory(accelerator, catalog)


def generate_inventory(accelerator: Path, catalog: Path, output: Path) -> dict:
    """Generate and write the inventory, returning its document representation."""
    inventory = build_inventory(accelerator, catalog)
    dump_yaml(inventory, output)
    return inventory


def check_inventory(accelerator: Path, catalog: Path, output: Path) -> bool:
    """Return whether the committed inventory matches the current RDF import closure."""
    return load_yaml(output) == build_inventory(accelerator, catalog)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accelerator", type=Path, default=DEFAULT_ACCELERATOR)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that the committed inventory is fresh without writing it.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.check:
            if not check_inventory(args.accelerator, args.catalog, args.output):
                print(
                    f"error: Inventory is stale; regenerate {args.output}",
                    file=sys.stderr,
                )
                return 1
            print(f"Inventory is fresh: {args.output}")
            return 0
        inventory = generate_inventory(args.accelerator, args.catalog, args.output)
    except BlueprintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(inventory['records'])} inventory records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
