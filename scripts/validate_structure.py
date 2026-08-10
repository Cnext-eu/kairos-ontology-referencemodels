# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
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

Advisory (warnings only, never fail the build):
  8. Relationship explicitness — flags likely *implicit* relationships:
       a. a *Ref/*Id string scalar whose stem matches an existing owl:Class
          (and is not a self-identifier / already navigable)
       b. >= 3 sibling object properties sharing a range with no generic
          rdfs:subPropertyOf parent
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

ACCELERATOR_SUPPORT_DIRS = {"blueprint", "profiles", "contracts", "examples", "docs"}
BLUEPRINTS_DIR = ONTOLOGY_ROOT / "blueprints"
ARCHETYPES_DIR = BLUEPRINTS_DIR / "archetypes"
ARCHETYPE_SCHEMA = ARCHETYPES_DIR / "_schema" / "archetype.schema.json"
PATTERNS_DIR = BLUEPRINTS_DIR / "patterns"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
ARCHETYPE_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

VERSION_INFO_RE = re.compile(r'owl:versionInfo\s+"([^"]*)"')
OWL_ONTOLOGY_RE = re.compile(r'\ba\s+owl:Ontology\b')
OWL_IMPORTS_RE = re.compile(r'owl:imports\s')
NAMESPACE_ROOT_RE = re.compile(r'@prefix\s+:\s+<https://www\.kairosflow\.ai/ont/([^/>]+)#>\s*\.')
NAMESPACE_MODULE_RE = re.compile(r'@prefix\s+:\s+<https://www\.kairosflow\.ai/ont/([^/>]+)/([^/>]+)#>\s*\.')
PROPERTY_START_RE = re.compile(
    r'^\s*(?P<property>\S+)\s+a\s+owl:(?P<property_type>ObjectProperty|DatatypeProperty)\s*;\s*$'
)
BLOCK_END_RE = re.compile(r'\s\.\s*$')
RDFS_DOMAIN_RE = re.compile(r'\brdfs:domain\b')
RDFS_RANGE_RE = re.compile(r'\brdfs:range\b')
CLASS_DECL_RE = re.compile(r'^\s*(?P<cls>:[A-Za-z][\w-]*)\s+a\s+owl:Class\b')
RANGE_SIMPLE_RE = re.compile(
    r'rdfs:range\s+(?P<range>[A-Za-z][\w-]*:[A-Za-z][\w-]*|:[A-Za-z][\w-]*)\s*[;.]'
)
SUBPROPERTY_RE = re.compile(r'\brdfs:subPropertyOf\b')
REF_SUFFIX_RE = re.compile(r'^(?P<stem>.+?)(Ref|Reference|Id|Identifier)$')
DOMAIN_SIMPLE_RE = re.compile(
    r'rdfs:domain\s+(?P<domain>[A-Za-z][\w-]*:[A-Za-z][\w-]*|:[A-Za-z][\w-]*)\s*[;.]'
)


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


def get_content_dir(folder: Path) -> Path:
    """Return the directory containing the active ontology content.

    If a 'current/' subfolder exists, content lives there; otherwise
    content is directly in the folder (legacy layout).
    """
    current = folder / "current"
    return current if current.is_dir() else folder


def find_root_ttl(folder: Path) -> Path | None:
    """Find the root .ttl file for an ontology folder.

    Looks for <foldername>.ttl or a lowercase variant in the content dir.
    """
    content_dir = get_content_dir(folder)
    name = folder.name
    candidates = [
        content_dir / f"{name}.ttl",
        content_dir / f"{name.lower()}.ttl",
        content_dir / f"{name.replace(' ', '-').lower()}.ttl",
    ]
    for c in candidates:
        if c.is_file():
            return c

    # Fallback: any .ttl directly in the content dir
    ttl_files = sorted(content_dir.glob("*.ttl"))
    if len(ttl_files) == 1:
        return ttl_files[0]
    return ttl_files[0] if ttl_files else None


def find_domain_subfolders(folder: Path):
    """Find immediate subfolders that look like domain modules."""
    content_dir = get_content_dir(folder)
    excluded = {"archive", "extensions"}
    if folder.parent.name == "accelerator-packs":
        excluded.update(ACCELERATOR_SUPPORT_DIRS)
    return sorted(
        d for d in content_dir.iterdir()
        if (
            d.is_dir()
            and not d.name.startswith(".")
            and d.name not in excluded
        )
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

        # 5b. Check nested subfolders (2-level nesting for journey-model structure)
        nested_subs = sorted(
            d for d in sub.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
        for nested in nested_subs:
            nested_ttls = sorted(nested.glob("*.ttl"))
            nested_rel = nested.relative_to(folder)
            if nested_ttls:
                r.ok(f"Subfolder {nested_rel}/: has {len(nested_ttls)} .ttl file(s)", verbose, is_verbose=True)

                for ttl in nested_ttls:
                    mod_content = ttl.read_text(encoding="utf-8")
                    mod_ver = VERSION_INFO_RE.search(mod_content)
                    ttl_rel = ttl.relative_to(folder)
                    if mod_ver:
                        r.ok(f"{ttl_rel}: owl:versionInfo {mod_ver.group(1)}", verbose, is_verbose=True)
                    else:
                        r.fail(f"{ttl_rel}: missing owl:versionInfo")

                    # Check module namespace convention
                    mod_ns = NAMESPACE_MODULE_RE.search(mod_content)
                    if mod_ns:
                        r.ok(f"{ttl_rel}: namespace https://www.kairosflow.ai/ont/{mod_ns.group(1)}/{mod_ns.group(2)}#", verbose, is_verbose=True)
                    else:
                        mod_root_ns = NAMESPACE_ROOT_RE.search(mod_content)
                        if mod_root_ns:
                            r.ok(f"{ttl_rel}: uses root namespace pattern", verbose, is_verbose=True)
                        else:
                            r.warn(f"{ttl_rel}: could not detect namespace")
            else:
                r.fail(f"Subfolder {nested_rel}/: no .ttl files found")

    return r


def validate_property_completeness(folder: Path, verbose: bool) -> ValidationResult:
    """Validate that property definitions include rdfs:domain and rdfs:range."""
    r = ValidationResult()
    content_dir = get_content_dir(folder)
    ttl_files = sorted(content_dir.rglob("*.ttl"))

    r.messages.append("\n── Property Completeness ──")

    for ttl_file in ttl_files:
        if "archive" in ttl_file.relative_to(folder).parts:
            continue

        content = ttl_file.read_text(encoding="utf-8")
        property_blocks = _extract_property_blocks(content.splitlines())

        if not property_blocks:
            continue

        ttl_rel = ttl_file.relative_to(ONTOLOGY_ROOT)
        r.ok(
            f"{ttl_rel}: checked {len(property_blocks)} property definition(s)",
            verbose,
            is_verbose=True,
        )

        for property_name, property_type, block in property_blocks:
            if RDFS_DOMAIN_RE.search(block):
                r.ok(
                    f"{ttl_rel}: {property_name} ({property_type}) has rdfs:domain",
                    verbose,
                    is_verbose=True,
                )
            else:
                r.fail(f"{ttl_rel}: {property_name} ({property_type}) missing rdfs:domain")

            if RDFS_RANGE_RE.search(block):
                r.ok(
                    f"{ttl_rel}: {property_name} ({property_type}) has rdfs:range",
                    verbose,
                    is_verbose=True,
                )
            else:
                r.fail(f"{ttl_rel}: {property_name} ({property_type}) missing rdfs:range")

    return r


def _extract_property_blocks(lines):
    """Extract (name, type, block_text) tuples for each property definition."""
    blocks = []
    index = 0
    while index < len(lines):
        match = PROPERTY_START_RE.match(lines[index])
        if not match:
            index += 1
            continue
        block_lines = [lines[index]]
        index += 1
        while index < len(lines):
            block_lines.append(lines[index])
            if BLOCK_END_RE.search(lines[index]):
                break
            index += 1
        blocks.append(
            (match.group("property"), match.group("property_type"), "\n".join(block_lines))
        )
        index += 1
    return blocks


def validate_relationship_explicitness(folder: Path, verbose: bool) -> ValidationResult:
    """Advisory checks (warnings only) that surface likely *implicit* relationships.

    Encourages the "make relationships explicit" convention (CONTRIBUTING.md):
      A. A ``*Ref`` / ``*Id`` string scalar whose stem matches an existing
         ``owl:Class`` in the same ontology probably hides a navigable
         ``owl:ObjectProperty``.
      B. A group of >= 3 sibling object properties that share the same range and
         none of which declares ``rdfs:subPropertyOf`` probably warrants a generic
         parent property (e.g. ``:hasParty`` / ``:hasLocation``).

    These never fail the build; they emit ``⚠`` hints for reviewer attention.
    """
    r = ValidationResult()
    content_dir = get_content_dir(folder)
    ttl_files = [
        f for f in sorted(content_dir.rglob("*.ttl"))
        if "archive" not in f.relative_to(folder).parts
    ]

    r.messages.append("\n── Relationship Explicitness (advisory) ──")

    # Collect all class local names declared anywhere in the ontology.
    class_names = set()
    for ttl_file in ttl_files:
        for line in ttl_file.read_text(encoding="utf-8").splitlines():
            m = CLASS_DECL_RE.match(line)
            if m:
                class_names.add(m.group("cls").lstrip(":").lower())

    for ttl_file in ttl_files:
        content = ttl_file.read_text(encoding="utf-8")
        blocks = _extract_property_blocks(content.splitlines())
        if not blocks:
            continue
        ttl_rel = ttl_file.relative_to(ONTOLOGY_ROOT)

        # Classes already reachable via an object property in this file are
        # considered navigable; a parallel scalar reference is acceptable passthrough.
        linked_classes = set()
        for name, ptype, block in blocks:
            if ptype != "ObjectProperty":
                continue
            rng_m = RANGE_SIMPLE_RE.search(block)
            if rng_m:
                linked_classes.add(rng_m.group("range").split(":")[-1].lower())

        # Heuristic A: scalar reference shadowing an existing class.
        for name, ptype, block in blocks:
            if ptype != "DatatypeProperty":
                continue
            local = name.lstrip(":")
            ref_m = REF_SUFFIX_RE.match(local)
            if not (ref_m and ref_m.group("stem").lower() in class_names):
                continue
            stem = ref_m.group("stem")
            # Skip self-identifiers: a *Reference/*Id on the same class it names.
            dom_m = DOMAIN_SIMPLE_RE.search(block)
            if dom_m and dom_m.group("domain").split(":")[-1].lower() == stem.lower():
                continue
            # Skip when an object property already links to that class.
            if stem.lower() in linked_classes:
                continue
            r.warn(
                f"{ttl_rel}: {name} is a string reference to existing class "
                f"':{stem[:1].upper()}{stem[1:]}' "
                f"— consider an owl:ObjectProperty to make the link navigable"
            )

        # Heuristic B: sibling object properties sharing a range, no generic parent.
        range_groups = {}
        for name, ptype, block in blocks:
            if ptype != "ObjectProperty":
                continue
            rng_m = RANGE_SIMPLE_RE.search(block)
            if not rng_m:
                continue
            has_parent = bool(SUBPROPERTY_RE.search(block))
            range_groups.setdefault(rng_m.group("range"), []).append((name, has_parent))

        for rng, members in range_groups.items():
            if len(members) >= 3 and not any(has_parent for _, has_parent in members):
                names = ", ".join(n for n, _ in members)
                r.warn(
                    f"{ttl_rel}: {len(members)} object properties share range {rng} "
                    f"with no rdfs:subPropertyOf parent ({names}) "
                    f"— consider a generic parent property"
                )

    if not any("⚠" in m for m in r.messages):
        r.ok("No likely implicit relationships detected", verbose, is_verbose=True)

    return r


def validate_blueprints(verbose: bool) -> ValidationResult:
    """Validate the opinionated blueprints/ module structure.

    Distinct from the ontology-folder validation: blueprints carry YAML
    catalogs (no .ttl, no owl:Ontology). This check enforces:

      1. blueprints/README.md exists.
      2. blueprints/archetypes/VERSION exists and is SemVer.
      3. blueprints/archetypes/README.md exists.
      4. blueprints/archetypes/_schema/archetype.schema.json exists.
      5. Every blueprints/patterns/<id>/pattern.yaml parses and its id matches
         its directory name (parse-only — the library is markdown-first, but it
         has a downstream parser in kairos-ontology-toolkit).
      5. Every *.yaml directly under archetypes/ (excluding _schema/ and dotfiles)
         loads with yaml.safe_load and its top-level ``id`` equals the filename stem.
    """
    r = ValidationResult()
    r.messages.append("\n── blueprints/ (opinionated module) ──")

    if not BLUEPRINTS_DIR.is_dir():
        r.warn("blueprints/ directory not present — skipping")
        return r

    readme = BLUEPRINTS_DIR / "README.md"
    if readme.is_file():
        r.ok("blueprints/README.md exists", verbose, is_verbose=True)
    else:
        r.fail("blueprints/README.md missing")

    if not ARCHETYPES_DIR.is_dir():
        r.fail("blueprints/archetypes/ directory missing")
        return r

    arch_readme = ARCHETYPES_DIR / "README.md"
    if arch_readme.is_file():
        r.ok("blueprints/archetypes/README.md exists", verbose, is_verbose=True)
    else:
        r.fail("blueprints/archetypes/README.md missing")

    version_file = ARCHETYPES_DIR / "VERSION"
    if version_file.is_file():
        ver = version_file.read_text(encoding="utf-8").strip()
        if SEMVER_RE.match(ver):
            r.ok(f"blueprints/archetypes/VERSION = {ver}", verbose, is_verbose=True)
        else:
            r.fail(f"blueprints/archetypes/VERSION '{ver}' is not SemVer (MAJOR.MINOR.PATCH)")
    else:
        r.fail("blueprints/archetypes/VERSION missing")

    if ARCHETYPE_SCHEMA.is_file():
        r.ok("blueprints/archetypes/_schema/archetype.schema.json exists", verbose, is_verbose=True)
    else:
        r.fail("blueprints/archetypes/_schema/archetype.schema.json missing")

    # Per-archetype YAML files
    try:
        import yaml  # PyYAML; required for blueprints validation
    except ImportError:
        r.warn("PyYAML not installed — skipping archetype YAML parse checks")
        return r

    archetype_files = sorted(
        f for f in ARCHETYPES_DIR.glob("*.yaml")
        if not f.name.startswith(".")
    )
    if not archetype_files:
        r.warn("No archetype YAML files found under blueprints/archetypes/")
        return r

    for yaml_file in archetype_files:
        rel = yaml_file.relative_to(ONTOLOGY_ROOT)
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            r.fail(f"{rel}: invalid YAML — {e}")
            continue
        if not isinstance(data, dict):
            r.fail(f"{rel}: top-level YAML must be a mapping")
            continue
        archetype_id = data.get("id")
        stem = yaml_file.stem
        if archetype_id is None:
            r.fail(f"{rel}: missing top-level 'id'")
        elif archetype_id != stem:
            r.fail(f"{rel}: id '{archetype_id}' does not match filename stem '{stem}'")
        elif not ARCHETYPE_ID_RE.match(archetype_id):
            r.fail(f"{rel}: id '{archetype_id}' is not kebab-case")
        else:
            r.ok(f"{rel}: id '{archetype_id}' matches filename", verbose, is_verbose=True)

    # Per-pattern YAML files. Parse-only, not schema validation: the pattern library is
    # markdown-first by design, but it IS parsed by a downstream consumer
    # (kairos-ontology-toolkit core/pattern_loader.py, which raises on a malformed
    # pattern.yaml when one is requested by id and silently skips it in bulk listing).
    # temporal-quartet shipped unparseable in v1.13.0 and nothing caught it, because a
    # stray `rule:` key inside a block sequence is invalid YAML but reads fine to a human.
    for pattern_dir in sorted(p for p in PATTERNS_DIR.glob("*") if p.is_dir()):
        if pattern_dir.name.startswith(".") or pattern_dir.name == "_schema":
            continue
        pattern_file = pattern_dir / "pattern.yaml"
        rel = pattern_file.relative_to(ONTOLOGY_ROOT)
        if not pattern_file.is_file():
            r.fail(f"{rel}: missing (every pattern directory needs a pattern.yaml)")
            continue
        try:
            data = yaml.safe_load(pattern_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            r.fail(f"{rel}: invalid YAML — {e}")
            continue
        if not isinstance(data, dict):
            r.fail(f"{rel}: top-level YAML must be a mapping")
            continue
        pattern_id = data.get("id")
        if pattern_id != pattern_dir.name:
            r.fail(f"{rel}: id '{pattern_id}' does not match directory '{pattern_dir.name}'")
        else:
            r.ok(f"{rel}: parses, id matches directory", verbose, is_verbose=True)

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

        if folder.parent.name == "derived-ontologies":
            property_result = validate_property_completeness(folder, args.verbose)
            for msg in property_result.messages:
                print(msg)
            total_pass += property_result.passes
            total_fail += property_result.failures

            relationship_result = validate_relationship_explicitness(folder, args.verbose)
            for msg in relationship_result.messages:
                print(msg)
            total_pass += relationship_result.passes
            total_fail += relationship_result.failures

    blueprint_result = validate_blueprints(args.verbose)
    for msg in blueprint_result.messages:
        print(msg)
    total_pass += blueprint_result.passes
    total_fail += blueprint_result.failures

    print(f"\n{'─' * 50}")
    if total_fail:
        print(f"✗ {total_fail} failure(s), {total_pass} passed")
        return 1
    else:
        print(f"✓ All {total_pass} checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
