#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Version manager for Kairos ontology reference models.

Commands:
  list   — Show all VERSION files and their current values
  bump   — Bump a specific ontology's version (major|minor|patch)
  sync   — Update owl:versionInfo in .ttl files to match VERSION files
  check  — Validate consistency between VERSION files and owl:versionInfo
"""

import argparse
import io
import os
import re
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
    ONTOLOGY_ROOT / "blueprints",
]

VERSION_INFO_PATTERN = re.compile(r'(owl:versionInfo\s+)"([^"]*)"')


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


def write_version(folder: Path, version: str):
    """Write version string to a VERSION file."""
    (folder / "VERSION").write_text(version + "\n", encoding="utf-8")


def get_content_dir(folder: Path) -> Path:
    """Return the directory containing active ontology content.

    If a 'current/' subfolder exists, content lives there; otherwise
    content is directly in the folder (legacy layout).
    """
    current = folder / "current"
    return current if current.is_dir() else folder


def find_ttl_files(folder: Path):
    """Find all .ttl files in an ontology folder's active content (recursive).

    Excludes the archive/ directory.
    """
    content_dir = get_content_dir(folder)
    return sorted(content_dir.rglob("*.ttl"))


def bump_version(current: str, part: str) -> str:
    """Bump a semver version string."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current)
    if not match:
        raise ValueError(f"Invalid version format: {current}")
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Unknown bump part: {part}")


# ── Commands ──────────────────────────────────────────────────────────────────


def cmd_list(_args):
    """List all VERSION files and their values."""
    folders = find_ontology_folders()
    if not folders:
        print("No ontology folders with VERSION files found.")
        return 0

    # Calculate column width
    max_name = max(len(rel) for rel, _ in folders)
    header_name = "Ontology"
    header_ver = "Version"
    col_w = max(max_name, len(header_name)) + 2

    print(f"  {header_name:<{col_w}} {header_ver}")
    print(f"  {'─' * col_w} {'─' * 10}")
    for rel, folder in folders:
        ver = read_version(folder)
        print(f"  {rel:<{col_w}} {ver}")
    print(f"\n  {len(folders)} ontologies found.")
    return 0


def cmd_bump(args):
    """Bump the version for a specific ontology."""
    target = args.ontology
    part = args.part

    folders = find_ontology_folders()
    matched = [(rel, f) for rel, f in folders if Path(rel).name == target]

    if not matched:
        print(f"✗ Ontology folder '{target}' not found.")
        print(f"  Available: {', '.join(Path(r).name for r, _ in folders)}")
        return 1

    if len(matched) > 1:
        print(f"✗ Ambiguous name '{target}', matches:")
        for rel, _ in matched:
            print(f"    {rel}")
        return 1

    rel, folder = matched[0]
    old_ver = read_version(folder)
    try:
        new_ver = bump_version(old_ver, part)
    except ValueError as e:
        print(f"✗ {e}")
        return 1

    write_version(folder, new_ver)
    print(f"✓ {rel}: {old_ver} → {new_ver}")
    print(f"  Run 'version_manager.py sync' to update .ttl files.")
    return 0


def cmd_sync(_args):
    """Sync owl:versionInfo in .ttl files to match VERSION files."""
    folders = find_ontology_folders()
    errors = 0
    updated = 0

    for rel, folder in folders:
        version = read_version(folder)
        ttl_files = find_ttl_files(folder)

        for ttl in ttl_files:
            content = ttl.read_text(encoding="utf-8")
            matches = VERSION_INFO_PATTERN.findall(content)
            if not matches:
                continue

            new_content, count = VERSION_INFO_PATTERN.subn(
                rf'\g<1>"{version}"', content
            )
            if new_content != content:
                ttl.write_text(new_content, encoding="utf-8")
                ttl_rel = ttl.relative_to(ONTOLOGY_ROOT)
                print(f"  ✓ {ttl_rel}: updated to {version}")
                updated += count
            else:
                ttl_rel = ttl.relative_to(ONTOLOGY_ROOT)
                print(f"  ✓ {ttl_rel}: already {version}")

    if updated:
        print(f"\n✓ {updated} version string(s) updated.")
    else:
        print("\n✓ All .ttl files already in sync.")
    return errors


def cmd_check(_args):
    """Check consistency between VERSION files and owl:versionInfo."""
    folders = find_ontology_folders()
    errors = 0
    checked = 0

    for rel, folder in folders:
        version = read_version(folder)
        ttl_files = find_ttl_files(folder)

        if not ttl_files:
            print(f"  ⚠ {rel}: no .ttl files found")
            continue

        for ttl in ttl_files:
            content = ttl.read_text(encoding="utf-8")
            matches = VERSION_INFO_PATTERN.findall(content)
            if not matches:
                continue

            ttl_rel = ttl.relative_to(ONTOLOGY_ROOT)
            for _, ver_in_ttl in matches:
                checked += 1
                if ver_in_ttl == version:
                    print(f"  ✓ {ttl_rel}: {ver_in_ttl}")
                else:
                    print(f"  ✗ {ttl_rel}: {ver_in_ttl} (expected {version})")
                    errors += 1

    print()
    if errors:
        print(f"✗ {errors} mismatch(es) found out of {checked} checked.")
        return 1
    else:
        print(f"✓ All {checked} version strings consistent.")
        return 0


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Manage ontology versions across the Kairos reference models."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all VERSION files and their values")

    bump_p = sub.add_parser("bump", help="Bump a specific ontology version")
    bump_p.add_argument("ontology", help="Ontology folder name (e.g. DCSA, MMT, TIC)")
    bump_p.add_argument("part", choices=["major", "minor", "patch"], help="Version part to bump")

    sub.add_parser("sync", help="Sync owl:versionInfo in .ttl files to VERSION")

    sub.add_parser("check", help="Check VERSION / owl:versionInfo consistency")

    args = parser.parse_args()
    commands = {
        "list": cmd_list,
        "bump": cmd_bump,
        "sync": cmd_sync,
        "check": cmd_check,
    }
    sys.exit(commands[args.command](args))


if __name__ == "__main__":
    main()
