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
  9. Each accelerator pack's client-hub-blueprint/entity-projections.yaml, WHEN PRESENT,
     validates against accelerator-packs/_schema/entity-projections.schema.json
     and is internally coherent. The file is optional by design — a pack that
     ships none yields no candidates, and the toolkit has no fallback (DD-188).
 10. Import closure (gh#97). Every **rdfs:domain** naming a class in a foreign Kairos
     namespace must have that class's module in the asserting module's transitive
     owl:imports closure; and a leaf module must not import a vendor root. Without
     this, a property domained on a class the module never imports is left dangling:
     the class is never typed in that module's graph, so the property is invisible to
     any consumer resolving "which properties does class X carry" — which produced a
     false reference-model gap report.

     rdfs:range is checked but only WARNS (see the advisory list below). The asymmetry
     is deliberate and was measured. A dangling range costs a consumer little — the
     property is still discoverable on its own domain class, only the range class is
     untyped locally. Requiring imports for ranges as well would have added 70 imports
     rather than 15, and because the consuming toolkit derives each data domain's
     alignment pool from the *transitive* owl:imports closure, that widened the total
     classes offered across the logistics domains from 729 to 1805 (2.48x) — offering
     `compliance` 92 classes where it had 5. The pack's "cross-domain references use
     untyped ranges" convention exists to keep those closures narrow, and it is
     load-bearing rather than stale.

Advisory (warnings only, never fail the build):
 10b. Unimported rdfs:range targets — see check 10 above for why this warns rather
      than fails.
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
ONTOLOGY_ROOT = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models"

SCAN_DIRS = [
    ONTOLOGY_ROOT / "derived-ontologies",
    ONTOLOGY_ROOT / "accelerator-packs",
]

ACCELERATOR_SUPPORT_DIRS = {"blueprint", "profiles", "contracts", "examples", "docs"}
PACKS_DIR = ONTOLOGY_ROOT / "accelerator-packs"
ENTITY_PROJECTIONS_SCHEMA = PACKS_DIR / "_schema" / "entity-projections.schema.json"
#: Relative to a pack directory. Mirrors the contract-manifest.yaml glob
#: ``accelerator-packs/*/client-hub-blueprint/entity-projections.yaml``. It sits beside
#: data-domains.yaml, not under ``current/blueprint/``: that directory is the logistics
#: blueprint dossier and financial-services has no such directory at all, so a path under
#: it could not express the two-packs-two-vocabularies point of DD-188.
ENTITY_PROJECTIONS_REL = Path("client-hub-blueprint") / "entity-projections.yaml"
BLUEPRINTS_DIR = ONTOLOGY_ROOT / "blueprints"
ARCHETYPES_DIR = BLUEPRINTS_DIR / "archetypes"
ARCHETYPE_SCHEMA = ARCHETYPES_DIR / "_schema" / "archetype.schema.json"
PATTERNS_DIR = BLUEPRINTS_DIR / "patterns"
PATTERN_SCHEMA = PATTERNS_DIR / "_schema" / "pattern.schema.json"
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
REUSABLE_NO_DOMAIN_RE = re.compile(r'REUSABLE\s+—\s+no rdfs:domain by design')
#: A term being retired. Per the repo's rename/deprecation policy a deprecated term stays
#: resolvable for one major but need not carry a complete domain/range: a stub that kept
#: its foreign rdfs:domain would also keep the owl:imports edge it exists to remove.
DEPRECATED_RE = re.compile(r'\bowl:deprecated\s+true\b')

KAIROS_NS_PREFIX = "https://www.kairosflow.ai/ont/"
#: ``@prefix foo: <...> .`` — captures the prefix label (empty for the default ``:``).
#: MULTILINE: these anchor per line, not at the start of the file.
PREFIX_DECL_RE = re.compile(
    r'^\s*@prefix\s+(?P<label>[A-Za-z][\w.-]*)?:\s*<(?P<ns>[^>]+)>\s*\.', re.MULTILINE
)
#: The ontology's own IRI, e.g. ``<https://.../ont/mmt/cargo> a owl:Ontology ;``
ONTOLOGY_IRI_RE = re.compile(r'^\s*<(?P<iri>[^>]+)>\s+a\s+owl:Ontology\b', re.MULTILINE)
#: An individual ``owl:imports`` target IRI. Unlike OWL_IMPORTS_RE (presence-only,
#: used by check 3) this captures each IRI, including comma-continuation members.
OWL_IMPORTS_IRI_RE = re.compile(r'owl:imports\s+((?:<[^>]+>\s*,\s*)*<[^>]+>)')
#: A prefixed name in a domain/range span, e.g. ``mmt-evt:TransportEvent``.
PREFIXED_NAME_RE = re.compile(r'\b(?P<label>[A-Za-z][\w.-]*)?:(?P<local>[A-Za-z][\w-]*)\b')

# Matches Turtle string literals: triple-quoted ("""..."""), single-quoted ("..."),
# and their single-quote analogues ('''...''', '...'). Used to strip literals
# before regex-searching for predicate keywords like rdfs:domain, so that an
# rdfs:comment *mentioning* rdfs:domain does not count as a real declaration.
_TTL_STRING_LITERAL_RE = re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')


def _strip_turtle_literals_and_comments(text: str) -> str:
    """Remove Turtle string literals and full-line comments from *text*.

    Property blocks sometimes contain rdfs:comment strings that mention
    rdfs:domain (e.g. the REUSABLE marker ``"REUSABLE — no rdfs:domain by
    design"``). Searching the raw block for ``\\brdfs:domain\\b`` matches
    those mentions, making the REUSABLE domainless branch unreachable.
    Stripping literals first means only actual predicate declarations remain.
    """
    stripped = _TTL_STRING_LITERAL_RE.sub('""', text)
    lines = [line for line in stripped.splitlines() if not line.lstrip().startswith("#")]
    return "\n".join(lines)


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
            code_block = _strip_turtle_literals_and_comments(block)
            if DEPRECATED_RE.search(code_block):
                r.ok(
                    f"{ttl_rel}: {property_name} ({property_type}) deprecated — "
                    f"domain/range not required on a retiring stub",
                    verbose,
                    is_verbose=True,
                )
                continue
            if RDFS_DOMAIN_RE.search(code_block):
                r.ok(
                    f"{ttl_rel}: {property_name} ({property_type}) has rdfs:domain",
                    verbose,
                    is_verbose=True,
                )
            elif REUSABLE_NO_DOMAIN_RE.search(block):
                # Escape marker for deliberately domainless reusable properties:
                # asserting a domain would infer that class onto every hub class
                # using the property (e.g. bsp/party hasAddress + TradeParty
                # re-created subclass-identity-by-role by the back door). The
                # marker must be in the property's own rdfs:comment; range is
                # still required. Documented in CONTRACT.md.
                r.ok(
                    f"{ttl_rel}: {property_name} ({property_type}) domainless by design (REUSABLE marker)",
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


def _prefix_map(text: str) -> dict[str, str]:
    """Map prefix label -> namespace IRI. The default ``:`` prefix has label ``""``."""
    out = {}
    for match in PREFIX_DECL_RE.finditer(text):
        out[match.group("label") or ""] = match.group("ns")
    return out


def _ontology_iri(text: str) -> str | None:
    match = ONTOLOGY_IRI_RE.search(text)
    return match.group("iri") if match else None


def _declared_imports(code_text: str) -> set[str]:
    out = set()
    for match in OWL_IMPORTS_IRI_RE.finditer(code_text):
        out.update(re.findall(r'<([^>]+)>', match.group(1)))
    return out


def _domain_range_spans(code_text: str):
    """Yield (predicate, span_text) for each rdfs:domain / rdfs:range assertion.

    The span runs to the statement terminator at bracket depth 0, so a union
    domain/range (``rdfs:range [ owl:unionOf ( a:X b:Y ) ]``) yields all its
    members rather than being skipped the way a simple ``rdfs:range X`` regex
    would skip it.
    """
    for match in re.finditer(r'\brdfs:(domain|range)\b', code_text):
        predicate = f"rdfs:{match.group(1)}"
        depth = 0
        index = match.end()
        while index < len(code_text):
            char = code_text[index]
            if char in "[(":
                depth += 1
            elif char in "])":
                depth -= 1
            elif char in ";." and depth <= 0:
                break
            index += 1
        yield predicate, code_text[match.end():index]


def _is_vendor_root(iri: str) -> bool:
    """True for a vendor aggregator IRI such as .../ont/mmt (no module segment)."""
    if not iri.startswith(KAIROS_NS_PREFIX):
        return False
    return "/" not in iri[len(KAIROS_NS_PREFIX):].strip("/")


def _module_iri_of_namespace(namespace: str) -> str:
    return namespace.rstrip("#").rstrip("/")


def validate_import_closure(verbose: bool, scan_roots=None) -> ValidationResult:
    """Check 10 (gh#97): every foreign domain/range target is in the import closure.

    Repo-scoped rather than folder-scoped because the closure legitimately crosses
    vendor trees (Sustainability/carbon imports three IMO modules), so a per-folder
    view could not tell a missing import from a cross-vendor one.

    *scan_roots* overrides the directories scanned; the first entry is treated as the
    derived-ontologies tree for the leaf-must-not-import-a-vendor-root rule. Tests pass
    a tmp_path so the rules can be exercised without the real corpus.
    """
    r = ValidationResult()
    r.messages.append("\n── Import Closure (gh#97) ──")

    if scan_roots is None:
        scan_roots = list(SCAN_DIRS) + [BLUEPRINTS_DIR / "ontology"]
    scan_roots = list(scan_roots)
    derived_root = scan_roots[0] if scan_roots else None
    docs = {}  # ontology IRI -> record

    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for ttl_file in sorted(scan_root.rglob("*.ttl")):
            if "archive" in ttl_file.relative_to(scan_root).parts:
                continue
            text = ttl_file.read_text(encoding="utf-8")
            code_text = _strip_turtle_literals_and_comments(text)
            iri = _ontology_iri(code_text)
            if iri is None:
                continue
            prefixes = _prefix_map(text)
            own_ns = prefixes.get("", "")
            # Kept separate: a dangling rdfs:domain hides properties from the class they
            # belong to and blocks; a dangling rdfs:range only leaves the range class
            # untyped and warns. See the docstring for why range is not blocking.
            targets = {}       # blocking:  target module IRI -> ["rdfs:domain prefix:Local"]
            range_only = {}    # advisory:  same shape, for range-only references
            for predicate, span in _domain_range_spans(code_text):
                bucket = targets if predicate == "rdfs:domain" else range_only
                for match in PREFIXED_NAME_RE.finditer(span):
                    label = match.group("label") or ""
                    namespace = prefixes.get(label)
                    if namespace is None or not namespace.startswith(KAIROS_NS_PREFIX):
                        continue
                    if namespace == own_ns:
                        continue
                    target = _module_iri_of_namespace(namespace)
                    token = f"{label}:{match.group('local')}"
                    bucket.setdefault(target, []).append(f"{predicate} {token}")
            try:
                rel_path = ttl_file.relative_to(ONTOLOGY_ROOT)
            except ValueError:
                rel_path = ttl_file.relative_to(scan_root)
            docs[iri] = {
                "path": rel_path,
                "in_derived": scan_root == derived_root,
                "imports": _declared_imports(code_text),
                "targets": targets,
                "range_only": range_only,
            }

    def closure(iri: str) -> set[str]:
        seen = set()
        stack = list(docs.get(iri, {}).get("imports", ()))
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(docs.get(current, {}).get("imports", ()))
        return seen

    for iri, record in sorted(docs.items()):
        rel = record["path"]
        reachable = closure(iri)
        unresolved = {
            target: evidence
            for target, evidence in record["targets"].items()
            if target != iri and target not in reachable
        }
        if unresolved:
            for target, evidence in sorted(unresolved.items()):
                r.fail(
                    f"{rel}: {', '.join(sorted(set(evidence)))} names a class in "
                    f"<{target}>, which is not in this module's owl:imports closure — "
                    f"the property is dangling and invisible to consumers resolving "
                    f"'which properties does this class carry'"
                )
        elif record["targets"]:
            r.ok(
                f"{rel}: {len(record['targets'])} foreign rdfs:domain reference(s) in closure",
                verbose,
                is_verbose=True,
            )

        # Advisory: an unimported rdfs:range leaves the range class untyped here. That
        # costs a consumer far less than a dangling domain (the property is still found
        # on its own class), and importing every range target is what would blow up the
        # per-domain alignment pools — so this warns and never fails.
        dangling_ranges = {
            target: evidence
            for target, evidence in record.get("range_only", {}).items()
            if target != iri and target not in reachable and target not in record["targets"]
        }
        for target, evidence in sorted(dangling_ranges.items()):
            r.warn(
                f"{rel}: {', '.join(sorted(set(evidence)))} names a class in <{target}> "
                f"which this module does not import — the range class stays untyped here. "
                f"Intentional under the untyped-range convention; import it only if a "
                f"consumer needs to resolve the range class from this module"
            )

        # A leaf module must not import a vendor root: that would pull the whole
        # vendor tree into every consumer and defeat per-domain import scoping.
        # Accelerator packs and vendor roots are aggregators and may do so.
        if record["in_derived"] and not _is_vendor_root(iri):
            for imported in sorted(record["imports"]):
                if _is_vendor_root(imported):
                    r.fail(
                        f"{rel}: imports vendor root <{imported}> — a leaf module must "
                        f"import the specific sibling module(s) it references, not the "
                        f"vendor aggregator"
                    )

    return r


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


RANGE_OWL_THING_RE = re.compile(r'rdfs:range\s+owl:Thing\b')


def pattern_schema_errors(data, schema):
    """Validate one parsed pattern.yaml against pattern.schema.json.

    Returns a list of human-readable error strings (empty = valid). Split out
    from validate_blueprints so tests can exercise the schema against known-bad
    shapes (the v1.13.0 stray-`rule:` defect class) without touching the tree.
    """
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    return errors


def validate_pattern_template(template_text: str):
    """Structural guard for a pattern's copyable OWL fragment (``<id>.ttl``).

    Returns a list of error strings. Enforces the two rules the
    deferred-relationship review made explicit (issues #39/#42):
      - rdfs:range owl:Thing is never an acceptable placeholder (it passes hub
        validate, then hard-fails compile as safety.relationship-endpoint).
      - every property block declares rdfs:domain (the domain is never
        deferred — it is the class being authored). Range is deliberately NOT
        required here; the range policy is pattern-specific prose.
    """
    # Full-line comments are guidance, not declarations — the templates warn
    # ABOUT owl:Thing in comments, which must not trip the ban on declaring it.
    lines = [
        line for line in template_text.splitlines()
        if not line.lstrip().startswith("#")
    ]
    errors = []
    if RANGE_OWL_THING_RE.search("\n".join(lines)):
        errors.append(
            "declares rdfs:range owl:Thing — banned placeholder; it passes validate "
            "then hard-fails compile (safety.relationship-endpoint)"
        )
    current_property = None
    block_lines = []
    for line in lines:
        if current_property is None:
            m = PROPERTY_START_RE.match(line)
            if m:
                current_property = m.group("property")
                block_lines = [line]
        else:
            block_lines.append(line)
        if current_property is not None and BLOCK_END_RE.search(line):
            block = "\n".join(block_lines)
            if not RDFS_DOMAIN_RE.search(_strip_turtle_literals_and_comments(block)):
                errors.append(
                    f"property {current_property} has no rdfs:domain — the domain is "
                    "never deferred (it is the class being authored)"
                )
            current_property = None
            block_lines = []
    return errors


def validate_blueprints(verbose: bool) -> ValidationResult:
    """Validate the opinionated blueprints/ module structure.

    Distinct from the ontology-folder validation: blueprints carry YAML
    catalogs (no .ttl, no owl:Ontology). This check enforces:

      1. blueprints/README.md exists.
      2. blueprints/archetypes/VERSION exists and is SemVer.
      3. blueprints/archetypes/README.md exists.
      4. blueprints/archetypes/_schema/archetype.schema.json exists.
      5. Every blueprints/patterns/<id>/pattern.yaml parses, its id matches its
         directory name, and it validates against
         blueprints/patterns/_schema/pattern.schema.json (the library has a
         downstream parser in kairos-ontology-toolkit).
      6. Every OWL fragment under blueprints/patterns/<id>/ (any *.ttl that is not a
         *.shacl.ttl — by convention <id>.ttl) passes the template guard: no
         rdfs:range owl:Thing, and every property block declares rdfs:domain.
      7. Every *.yaml directly under archetypes/ (excluding _schema/ and dotfiles)
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

    # Per-pattern YAML files: parse, id/directory match, and full JSON-Schema
    # validation against _schema/pattern.schema.json. The schema closes the
    # v1.13.0 defect class for good: temporal-quartet shipped unparseable (a
    # stray `rule:` key inside a block sequence — invalid YAML that reads fine
    # to a human) and the toolkit's pattern_loader silently skipped it in bulk
    # listing, so the one normative pattern was invisible for its entire life.
    # Parse guards caught malformed YAML; the schema now also catches
    # wrong-but-parseable shapes inside list entries.
    if PATTERN_SCHEMA.is_file():
        r.ok("blueprints/patterns/_schema/pattern.schema.json exists", verbose, is_verbose=True)
    else:
        r.fail("blueprints/patterns/_schema/pattern.schema.json missing")

    pattern_schema = None
    if PATTERN_SCHEMA.is_file():
        try:
            import json
            import jsonschema  # noqa: F401 — probe only; used via pattern_schema_errors
            pattern_schema = json.loads(PATTERN_SCHEMA.read_text(encoding="utf-8"))
        except ImportError:
            r.warn("jsonschema not installed — pattern.yaml schema validation skipped (CI installs it)")

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

        if pattern_schema is not None:
            schema_errors = pattern_schema_errors(data, pattern_schema)
            if schema_errors:
                for err in schema_errors:
                    r.fail(f"{rel}: schema — {err}")
            else:
                r.ok(f"{rel}: validates against pattern.schema.json", verbose, is_verbose=True)

        # Discovered by glob, not by a fixed "template.ttl" name. The two templates that
        # had that name both inventoried to template-inventory.yaml in the consumer and
        # silently clobbered each other (gh#57); they are now named for their pattern.
        # Globbing means the guard follows the file instead of the filename.
        for template_file in sorted(pattern_dir.glob("*.ttl")):
            if template_file.name.endswith(".shacl.ttl"):
                continue
            template_rel = template_file.relative_to(ONTOLOGY_ROOT)
            template_errors = validate_pattern_template(
                template_file.read_text(encoding="utf-8")
            )
            if template_errors:
                for err in template_errors:
                    r.fail(f"{template_rel}: {err}")
            else:
                r.ok(f"{template_rel}: template guard passed", verbose, is_verbose=True)

    return r


def entity_projection_errors(data, schema):
    """Validate one parsed ``entity-projections.yaml`` against its schema, plus
    the coherence rules JSON Schema cannot express.

    Returns a list of human-readable error strings (empty = valid). Split out so
    tests can drive it against known-bad shapes without touching the tree.

    Beyond the schema, three unsatisfiable-configuration checks. All three are
    files that validate structurally and then detect nothing at runtime, which is
    the worst outcome here: the pack looks configured and silently is not.

      1. Duplicate projection ``id`` — the toolkit keys candidates on it, so the
         second entry would shadow the first.
      2. Duplicate ``kind`` inside one projection — ``kind`` is the unit
         ``min_complementary_parts`` counts over, so a repeat lets one column
         type satisfy the threshold twice. (``uniqueItems`` on the list cannot
         see this: the two entries differ in their tokens.)
      3. A kind that can never count — ``requires: context`` with no
         ``context_tokens`` declared, or fewer ``part_kinds`` than
         ``min_complementary_parts``.
    """
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")
    if errors:
        # Coherence checks below assume the shape held; reporting both sets at
        # once would bury the real error under type confusion.
        return errors

    seen_ids = set()
    for index, projection in enumerate(data["projections"]):
        where = f"projections/{index}"
        projection_id = projection["id"]
        if projection_id in seen_ids:
            errors.append(f"{where}: duplicate projection id '{projection_id}'")
        seen_ids.add(projection_id)

        part_kinds = projection["part_kinds"]
        kinds = [part["kind"] for part in part_kinds]
        for kind in sorted({k for k in kinds if kinds.count(k) > 1}):
            errors.append(
                f"{where} ('{projection_id}'): duplicate part kind '{kind}' — kind is the "
                "unit min_complementary_parts counts over"
            )

        minimum = projection["min_complementary_parts"]
        if len(set(kinds)) < minimum:
            errors.append(
                f"{where} ('{projection_id}'): declares {len(set(kinds))} distinct part "
                f"kind(s) but requires {minimum} — the projection can never fire"
            )

        if not projection.get("context_tokens"):
            for part in part_kinds:
                if part.get("requires") == "context":
                    errors.append(
                        f"{where} ('{projection_id}'): part kind '{part['kind']}' requires a "
                        "context token but the projection declares no context_tokens — that "
                        "kind can never count"
                    )
    return errors


def validate_entity_projections(verbose: bool) -> ValidationResult:
    """Validate every accelerator pack's ``entity-projections.yaml``, if it has one.

    The file carries the column-recognition vocabulary the toolkit's alignment
    stage used to hardcode (toolkit DD-188, reference-models #94). It is
    OPTIONAL by design: a pack that ships none yields no candidates, and the
    toolkit has no built-in fallback vocabulary to fall back to. So an absent
    file passes and says so out loud — absent is a decision, and it should be
    visible in the log rather than inferred from silence. A file that is present
    is fully binding.
    """
    r = ValidationResult()
    r.messages.append("\n── accelerator-packs/*/client-hub-blueprint/entity-projections.yaml ──")

    if not PACKS_DIR.is_dir():
        r.warn("accelerator-packs/ directory not present — skipping")
        return r

    packs = sorted(
        d for d in PACKS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "_schema"
    )
    present = [p for p in packs if (p / ENTITY_PROJECTIONS_REL).is_file()]

    if not present:
        r.ok("No pack ships entity-projections.yaml (valid: no config, no candidates)")
        return r

    if ENTITY_PROJECTIONS_SCHEMA.is_file():
        r.ok("accelerator-packs/_schema/entity-projections.schema.json exists", verbose, is_verbose=True)
    else:
        r.fail(
            "accelerator-packs/_schema/entity-projections.schema.json missing, but "
            f"{len(present)} pack(s) ship an entity-projections.yaml"
        )
        return r

    try:
        import json
        import yaml  # PyYAML
        import jsonschema  # noqa: F401 — probe only; used via entity_projection_errors
    except ImportError as exc:
        r.warn(f"{exc.name} not installed — entity-projections validation skipped (CI installs it)")
        return r

    schema = json.loads(ENTITY_PROJECTIONS_SCHEMA.read_text(encoding="utf-8"))

    for pack in packs:
        path = pack / ENTITY_PROJECTIONS_REL
        rel = path.relative_to(ONTOLOGY_ROOT)
        if not path.is_file():
            r.ok(f"{pack.name}: ships no entity-projections.yaml (no config, no candidates)")
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            r.fail(f"{rel}: invalid YAML — {e}")
            continue
        if not isinstance(data, dict):
            r.fail(f"{rel}: top-level YAML must be a mapping")
            continue
        schema_errors = entity_projection_errors(data, schema)
        if schema_errors:
            for err in schema_errors:
                r.fail(f"{rel}: {err}")
        else:
            ids = ", ".join(p["id"] for p in data["projections"])
            r.ok(f"{rel}: validates against entity-projections.schema.json ({ids})")

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

    closure_result = validate_import_closure(args.verbose)
    for msg in closure_result.messages:
        print(msg)
    total_pass += closure_result.passes
    total_fail += closure_result.failures

    blueprint_result = validate_blueprints(args.verbose)
    for msg in blueprint_result.messages:
        print(msg)
    total_pass += blueprint_result.passes
    total_fail += blueprint_result.failures

    projection_result = validate_entity_projections(args.verbose)
    for msg in projection_result.messages:
        print(msg)
    total_pass += projection_result.passes
    total_fail += projection_result.failures

    print(f"\n{'─' * 50}")
    if total_fail:
        print(f"✗ {total_fail} failure(s), {total_pass} passed")
        return 1
    else:
        print(f"✓ All {total_pass} checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
