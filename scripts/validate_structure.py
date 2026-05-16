#!/usr/bin/env python3
"""Validate repository structure conventions for Kairos ontology reference models.

Checks:
  1. Each ontology folder has VERSION, README.md, and a root .ttl file
  2. Each root .ttl has an owl:Ontology declaration
  3. Each root .ttl has owl:imports statements (for multi-domain ontologies)
  4. Namespace convention: https://www.kairosflow.ai/ont/<name># or .../name/domain#
  5. Each domain subfolder has a .ttl file
  6. Each .ttl file has owl:versionInfo
  7. VERSION file matches owl:versionInfo in the root .ttl
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
ONTOLOGY_ROOT = REPO_ROOT / "ontology-reference-models"

SCAN_DIRS = [
    ONTOLOGY_ROOT / "derived-ontologies",
    ONTOLOGY_ROOT / "accelerator-packs",
]

VERSION_INFO_RE = re.compile(r'owl:versionInfo\s+"([^"]*)"')
OWL_ONTOLOGY_RE = re.compile(r'\ba\s+owl:Ontology\b')
OWL_IMPORTS_RE = re.compile(r'owl:imports\s')
NAMESPACE_ROOT_RE = re.compile(r'@prefix\s+:\s+<https://www\.kairosflow\.ai/ont/([^/>]+)#>\s*\.')
NAMESPACE_MODULE_RE = re.compile(r'@prefix\s+:\s+<https://www\.kairosflow\.ai/ont/([^/>]+)/([^/>]+)#>\s*\.')


class ValidationResult:
    def __init__(self):
        self.passes = 0
        self.failures = 0
        self.messages = []

    def ok(self, msg, verbose=False, is_verbose=False):
        self.passes += 1
        if verbose or not is_verbose:
            self.messages.append(f"  ✓ {msg}")

    def fail(self, msg):
        self.failures += 1
        self.messages.append(f"  ✗ {msg}")

    def warn(self, msg):
        self.messages.append(f"  ⚠ {msg}")

    @property
    def success(self):
        return self.failures == 0


def find_ontology_folders():
    """Find all ontology folders that contain a VERSION file."""
    results = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.is_dir():
            continue
        for child in sorted(scan_dir.iterdir()):
            if child.is_dir() and (child / "VERSION").is_file():
                results.append(child)
    return results


def find_root_ttl(folder: Path) -> Path | None:
    """Find the root .ttl file for an ontology folder.

    Looks for <foldername>.ttl or a lowercase variant in the folder root.
    """
    name = folder.name
    candidates = [
        folder / f"{name}.ttl",
        folder / f"{name.lower()}.ttl",
        folder / f"{name.replace(' ', '-').lower()}.ttl",
    ]
    for c in candidates:
        if c.is_file():
            return c

    # Fallback: any .ttl directly in the folder
    ttl_files = sorted(folder.glob("*.ttl"))
    if len(ttl_files) == 1:
        return ttl_files[0]
    return ttl_files[0] if ttl_files else None


def find_domain_subfolders(folder: Path):
    """Find immediate subfolders that look like domain modules."""
    return sorted(
        d for d in folder.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def validate_ontology(folder: Path, verbose: bool) -> ValidationResult:
    """Validate a single ontology folder."""
    r = ValidationResult()
    name = folder.name
    rel = folder.relative_to(ONTOLOGY_ROOT)

    r.messages.append(f"\n── {rel} ──")

    # 1. Required files: VERSION, README.md, root .ttl
    version_file = folder / "VERSION"
    readme_file = folder / "README.md"

    if version_file.is_file():
        r.ok(f"VERSION file exists", verbose, is_verbose=True)
    else:
        r.fail(f"Missing VERSION file")

    if readme_file.is_file():
        r.ok(f"README.md exists", verbose, is_verbose=True)
    else:
        r.fail(f"Missing README.md")

    root_ttl = find_root_ttl(folder)
    if root_ttl:
        r.ok(f"Root .ttl: {root_ttl.name}", verbose, is_verbose=True)
    else:
        r.fail(f"No root .ttl file found (expected {name.lower()}.ttl or similar)")
        return r  # Can't check further without root ttl

    # Read root .ttl content
    content = root_ttl.read_text(encoding="utf-8")

    # 2. owl:Ontology declaration
    if OWL_ONTOLOGY_RE.search(content):
        r.ok(f"owl:Ontology declaration found", verbose, is_verbose=True)
    else:
        r.fail(f"{root_ttl.name}: missing owl:Ontology declaration")

    # 3. owl:imports (for multi-domain ontologies with subfolders)
    domain_subs = find_domain_subfolders(folder)
    has_imports = bool(OWL_IMPORTS_RE.search(content))
    if domain_subs:
        if has_imports:
            r.ok(f"owl:imports present (multi-domain ontology)", verbose, is_verbose=True)
        else:
            r.fail(f"{root_ttl.name}: multi-domain ontology missing owl:imports")
    else:
        if has_imports:
            r.ok(f"owl:imports present", verbose, is_verbose=True)
        else:
            r.ok(f"No owl:imports (single-file ontology)", verbose, is_verbose=True)

    # 4. Namespace convention
    ns_match = NAMESPACE_ROOT_RE.search(content)
    if ns_match:
        ns_name = ns_match.group(1)
        expected_ns = name.lower().replace(" ", "-")
        if ns_name == expected_ns or ns_name == name:
            r.ok(f"Namespace: https://www.kairosflow.ai/ont/{ns_name}#", verbose, is_verbose=True)
        else:
            r.warn(f"Namespace name '{ns_name}' differs from folder '{name}'")
    else:
        r.warn(f"Could not detect root namespace prefix")

    # 6. owl:versionInfo in root .ttl
    ver_match = VERSION_INFO_RE.search(content)
    if ver_match:
        ttl_version = ver_match.group(1)
        r.ok(f"owl:versionInfo: {ttl_version}", verbose, is_verbose=True)

        # 7. VERSION file matches owl:versionInfo
        if version_file.is_file():
            file_version = version_file.read_text(encoding="utf-8").strip()
            if file_version == ttl_version:
                r.ok(f"VERSION ({file_version}) matches owl:versionInfo", verbose, is_verbose=True)
            else:
                r.fail(f"VERSION ({file_version}) ≠ owl:versionInfo ({ttl_version})")
    else:
        r.fail(f"{root_ttl.name}: missing owl:versionInfo")

    # 5. Domain subfolders have .ttl files
    for sub in domain_subs:
        sub_ttls = sorted(sub.glob("*.ttl"))
        sub_rel = sub.relative_to(folder)
        if sub_ttls:
            r.ok(f"Subfolder {sub_rel}/: has {len(sub_ttls)} .ttl file(s)", verbose, is_verbose=True)

            # 6 (continued). Check versionInfo in module .ttl files
            for ttl in sub_ttls:
                mod_content = ttl.read_text(encoding="utf-8")
                mod_ver = VERSION_INFO_RE.search(mod_content)
                ttl_rel = ttl.relative_to(folder)
                if mod_ver:
                    r.ok(f"{ttl_rel}: owl:versionInfo {mod_ver.group(1)}", verbose, is_verbose=True)
                else:
                    r.fail(f"{ttl_rel}: missing owl:versionInfo")

                # 4 (continued). Check module namespace convention
                mod_ns = NAMESPACE_MODULE_RE.search(mod_content)
                if mod_ns:
                    r.ok(f"{ttl_rel}: namespace https://www.kairosflow.ai/ont/{mod_ns.group(1)}/{mod_ns.group(2)}#", verbose, is_verbose=True)
                else:
                    # Also accept root namespace pattern for modules
                    mod_root_ns = NAMESPACE_ROOT_RE.search(mod_content)
                    if mod_root_ns:
                        r.ok(f"{ttl_rel}: uses root namespace pattern", verbose, is_verbose=True)
                    else:
                        r.warn(f"{ttl_rel}: could not detect namespace")
        else:
            r.fail(f"Subfolder {sub_rel}/: no .ttl files found")

    return r


def main():
    parser = argparse.ArgumentParser(
        description="Validate Kairos ontology repository structure conventions."
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show all checks including passing ones"
    )
    args = parser.parse_args()

    folders = find_ontology_folders()
    if not folders:
        print("No ontology folders found.")
        return 1

    total_pass = 0
    total_fail = 0

    for folder in folders:
        result = validate_ontology(folder, args.verbose)
        for msg in result.messages:
            print(msg)
        total_pass += result.passes
        total_fail += result.failures

    print(f"\n{'─' * 50}")
    if total_fail:
        print(f"✗ {total_fail} failure(s), {total_pass} passed")
        return 1
    else:
        print(f"✓ All {total_pass} checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
