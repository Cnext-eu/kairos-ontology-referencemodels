#!/usr/bin/env python3
"""Archive the current version of an ontology before bumping.

Usage:
  python scripts/archive_version.py <ontology_name>
  python scripts/archive_version.py DCSA
  python scripts/archive_version.py --all

This copies the contents of <ontology>/current/ into <ontology>/archive/<version>/
where <version> is read from the VERSION file.
"""

import argparse
import io
import shutil
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
ONTOLOGY_ROOT = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models"

SCAN_DIRS = [
    ONTOLOGY_ROOT / "derived-ontologies",
    ONTOLOGY_ROOT / "accelerator-packs",
]


def find_ontology_folders():
    """Find all ontology folders that contain a VERSION file."""
    results = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.is_dir():
            continue
        for child in sorted(scan_dir.iterdir()):
            if child.is_dir() and (child / "VERSION").is_file():
                rel = child.relative_to(ONTOLOGY_ROOT)
                results.append((str(rel), child))
    return results


def read_version(folder: Path) -> str:
    """Read version string from a VERSION file."""
    return (folder / "VERSION").read_text(encoding="utf-8").strip()


def archive_ontology(folder: Path) -> int:
    """Archive the current version of an ontology.

    Returns 0 on success, 1 on failure.
    """
    name = folder.name
    version = read_version(folder)
    current_dir = folder / "current"
    archive_dir = folder / "archive" / version

    if not current_dir.is_dir():
        print(f"✗ {name}: no current/ directory found")
        return 1

    if archive_dir.is_dir():
        print(f"⚠ {name}: archive/{version}/ already exists — skipping")
        return 0

    # Create archive directory and copy current/ contents
    archive_dir.mkdir(parents=True, exist_ok=True)

    items_copied = 0
    for item in current_dir.iterdir():
        dest = archive_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
        items_copied += 1

    print(f"✓ {name}: archived v{version} ({items_copied} items → archive/{version}/)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Archive the current version of an ontology before bumping."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "ontology", nargs="?", default=None,
        help="Name of the ontology folder to archive (e.g., DCSA, IMO, logistics)"
    )
    group.add_argument(
        "--all", action="store_true",
        help="Archive all ontologies"
    )
    args = parser.parse_args()

    folders = find_ontology_folders()

    if args.all:
        targets = folders
    else:
        targets = [(rel, f) for rel, f in folders if Path(rel).name == args.ontology]
        if not targets:
            print(f"✗ Ontology '{args.ontology}' not found.")
            print(f"  Available: {', '.join(Path(r).name for r, _ in folders)}")
            return 1

    errors = 0
    for rel, folder in targets:
        errors += archive_ontology(folder)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
