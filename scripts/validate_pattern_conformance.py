# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
#!/usr/bin/env python3
"""Validate the derived ontologies against the normative pattern library.

Issue #41's root cause: the pattern library and the derived ontologies are
governed independently, and nothing checked one against the other — so
`tier: required` modules shipped names a normative pattern bans, and every
hub inherited the violation or redeclared its own. This script is the
durable fix: the machine-checkable half of each normative pattern is
enforced here, over the content this repository actually ships.

Blocking checks (exit 1 on failure):

  A. temporal-quartet naming, over every current derived-ontology and
     blueprint-ontology TTL, skipping owl:deprecated subjects:
       A1. quartet-variant rule — a property whose first camel token is a
           quartet qualifier (requested/planned/estimated/actual) and that
           contains a quartet event token (Start/End/Arrival/Departure)
           MUST be exactly one of the 16 names published in
           temporal-quartet/pattern.yaml naming_conventions.
       A2. banned-token rule — a datatype property whose declared range is
           in the pattern's applies_to_ranges MUST NOT carry any
           banned_name_tokens token (whole-token match, camel/snake
           tokenisation with acronym runs — semantics normative in
           temporal-quartet/pattern.md).
     Both rules honour the pattern's exemptions (exact local-name or full
     IRI match; every entry needs a non-empty cited reason). Exemption
     usage is reported so dead entries stay visible.

  B. multimodal-order-leg participants:
       B1. every mode_bindings[].leg_module_iris module that declares *Leg
           classes must wire at least one of them rdfs:subClassOf* under the
           carries_mode: true participant (the leg) — mode-as-reified-leg
           must actually hold, not just be asserted in prose (finding 2 of
           #41 was exactly this edge missing). Means-borne modes (air) whose
           module declares no *Leg classes are noted and skipped.
       B2. the carries_mode: false participant (the order) must have no
           mode-named property domained on it and no mode-named subclass —
           the mode-subclass-on-order anti-pattern, mechanised.

Advisory check (warns, never fails):

  C. subclass-identity-by-role detection — a party-shaped parent (local
     name ending in 'Party') with >= 3 non-deprecated subclasses, outside
     qualified-role-assignment's exemptions.

Precedence rule enforced here (CONTRACT.md, "Patterns vs derived modules"):
where a derived module mirrors a cited source element, source fidelity wins
— but only through a visible exemptions entry. An unexempted disagreement
between a pattern and shipped content fails this build.
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import yaml

try:
    from rdflib import Graph, RDF, RDFS, OWL, URIRef
    from rdflib.term import Literal
except ImportError:  # pragma: no cover - CI installs rdflib
    print("rdflib not installed — pattern conformance validation requires it.")
    sys.exit(1)

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
ONTOLOGY_ROOT = REPO_ROOT / "ontology-reference-models"
PATTERNS_DIR = ONTOLOGY_ROOT / "blueprints" / "patterns"
CATALOG = ONTOLOGY_ROOT / "catalog-v001.xml"

sys.path.insert(0, str(SCRIPT_DIR))
from catalog_utils import CatalogResolver  # noqa: E402

XSD_PREFIX = "http://www.w3.org/2001/XMLSchema#"

QUARTET_QUALIFIERS = {"requested", "planned", "estimated", "actual"}
QUARTET_EVENTS = {"start", "end", "arrival", "departure"}
MODE_WORDS = {"mode", "ocean", "air", "rail", "road", "barge", "maritime"}

# Camel/snake tokenisation with acronym runs kept whole — normative in
# temporal-quartet/pattern.md "Synonym ban — matching semantics".
TOKEN_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+")


def tokenize(name: str) -> list[str]:
    return TOKEN_RE.findall(name)


def local_name(uri: str) -> str:
    return uri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def load_pattern(pattern_id: str) -> dict:
    path = PATTERNS_DIR / pattern_id / "pattern.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def anti_pattern(pattern: dict, anti_id: str) -> dict | None:
    for entry in pattern.get("anti_patterns", []):
        if isinstance(entry, dict) and entry.get("id") == anti_id:
            return entry
    return None


def scan_ttl_files() -> list[Path]:
    files: list[Path] = []
    for base in (ONTOLOGY_ROOT / "derived-ontologies", ONTOLOGY_ROOT / "blueprints" / "ontology"):
        if not base.is_dir():
            continue
        for ttl in sorted(base.rglob("*.ttl")):
            if "archive" in ttl.parts:
                continue
            files.append(ttl)
    return files


class Exemptions:
    """Structured {name, reason} exemption entries with usage tracking."""

    def __init__(self, entries, source: str, errors: list[str]):
        self.names: dict[str, str] = {}
        self.used: set[str] = set()
        self.source = source
        for entry in entries or []:
            if not isinstance(entry, dict) or not entry.get("name") or not str(entry.get("reason", "")).strip():
                errors.append(
                    f"{source}: exemption entry {entry!r} must be a mapping with a "
                    "non-empty name and a non-empty cited reason"
                )
                continue
            self.names[str(entry["name"])] = str(entry["reason"])

    def exempts(self, uri: str) -> bool:
        name = local_name(uri)
        for candidate in (uri, name):
            if candidate in self.names:
                self.used.add(candidate)
                return True
        return False

    def unused(self) -> list[str]:
        return sorted(set(self.names) - self.used)


def parse_graph(ttl: Path, errors: list[str]) -> Graph | None:
    g = Graph()
    try:
        g.parse(ttl, format="turtle")
    except Exception as exc:  # noqa: BLE001 - report and continue
        errors.append(f"{ttl.relative_to(REPO_ROOT)}: unparseable Turtle — {exc}")
        return None
    return g


def is_deprecated(g: Graph, subject) -> bool:
    return (subject, OWL.deprecated, Literal(True)) in g


def check_temporal_quartet(errors: list[str]) -> Exemptions:
    pattern = load_pattern("temporal-quartet")
    anti = anti_pattern(pattern, "synonym-for-estimated-or-requested") or {}
    banned = {t.lower() for t in anti.get("banned_name_tokens", [])}
    ranges = {
        URIRef(XSD_PREFIX + r.split(":", 1)[1])
        for r in anti.get("applies_to_ranges", [])
        if r.startswith("xsd:")
    }
    exemptions = Exemptions(
        anti.get("exemptions"), "temporal-quartet/pattern.yaml", errors
    )
    if not banned:
        errors.append(
            "temporal-quartet/pattern.yaml: synonym-for-estimated-or-requested has no "
            "banned_name_tokens — the structured denylist is required (issue #40)"
        )

    legal_names: set[str] = set()
    for row in pattern.get("naming_conventions", []):
        for key in ("start_or_arrival", "arrival_variant", "end_or_departure", "departure_variant"):
            if row.get(key):
                legal_names.add(row[key])

    for ttl in scan_ttl_files():
        g = parse_graph(ttl, errors)
        if g is None:
            continue
        rel = ttl.relative_to(REPO_ROOT)
        props = set(g.subjects(RDF.type, OWL.DatatypeProperty)) | set(
            g.subjects(RDF.type, OWL.ObjectProperty)
        )
        for prop in props:
            if not isinstance(prop, URIRef) or is_deprecated(g, prop):
                continue
            name = local_name(str(prop))
            tokens = [t.lower() for t in tokenize(name)]
            if not tokens:
                continue

            # A1 — quartet-variant rule.
            if (
                tokens[0] in QUARTET_QUALIFIERS
                and any(t in QUARTET_EVENTS for t in tokens[1:])
                and name not in legal_names
                and not exemptions.exempts(str(prop))
            ):
                errors.append(
                    f"{rel}: {name} is a quartet variant — temporal-quartet names it "
                    f"'{tokens[0]}<Start|End|Arrival|Departure>' (16 legal names); "
                    "rename or add a cited exemption"
                )
                continue

            # A2 — banned-token rule (datatype properties in scoped ranges only).
            if (prop, RDF.type, OWL.DatatypeProperty) in g:
                declared_ranges = set(g.objects(prop, RDFS.range))
                if declared_ranges & ranges and any(t in banned for t in tokens):
                    if not exemptions.exempts(str(prop)):
                        hit = sorted(set(tokens) & banned)
                        errors.append(
                            f"{rel}: {name} carries banned token(s) {hit} on a temporal "
                            "property — use estimated*/requested* per temporal-quartet, "
                            "or add a cited exemption"
                        )
    return exemptions


def check_multimodal_order_leg(errors: list[str]) -> None:
    pattern = load_pattern("multimodal-order-leg")
    participants = {p.get("carries_mode"): p for p in pattern.get("participants", [])}
    resolver = CatalogResolver(CATALOG)

    def graph_for_module(module_iri: str) -> Graph | None:
        path = resolver.resolve(module_iri)
        if path is None or not Path(path).is_file():
            errors.append(
                f"multimodal-order-leg: module IRI {module_iri} does not resolve "
                "through catalog-v001.xml"
            )
            return None
        return parse_graph(Path(path), errors)

    # B1 — the leg participant: reified mode subclasses must actually exist.
    leg = participants.get(True)
    if leg:
        leg_class = URIRef(leg["class_uri"])
        leg_module_iri = leg["class_uri"].rsplit("#", 1)[0]
        leg_graph = graph_for_module(leg_module_iri)
        checked_modules: set[str] = set()
        for binding in pattern.get("mode_bindings", []):
            for module_iri in binding.get("leg_module_iris", []):
                if module_iri in checked_modules:
                    continue
                checked_modules.add(module_iri)
                mod_graph = graph_for_module(module_iri)
                if mod_graph is None or leg_graph is None:
                    continue
                union = mod_graph + leg_graph
                # Only modules that CLAIM leg reification (declare *Leg classes)
                # must wire them under the pattern's leg class. A means-borne
                # mode (air: transport-means#Aircraft, per the discovery guide)
                # has no leg subclasses and is out of scope here.
                leg_named = [
                    cls
                    for cls in mod_graph.subjects(RDF.type, OWL.Class)
                    if isinstance(cls, URIRef) and "Leg" in local_name(str(cls))
                ]
                if not leg_named:
                    print(
                        f"  · {binding.get('mode')}: {module_iri} declares no *Leg classes "
                        "(means-borne mode) — subclass check not applicable"
                    )
                    continue
                if not any(
                    (cls, RDFS.subClassOf * "+", leg_class) in union  # type: ignore[operator]
                    for cls in leg_named
                ):
                    errors.append(
                        f"multimodal-order-leg grain 2 ({binding.get('mode')}): {module_iri} "
                        f"declares leg classes but none is rdfs:subClassOf* {leg['class_uri']} "
                        "— the pattern says mode is reified onto the leg, and the subclass "
                        "edge is missing (issue #41 finding 2)"
                    )

    # B2 — the order participant: no mode axis at order grain.
    order = participants.get(False)
    if order:
        order_class = URIRef(order["class_uri"])
        order_graph = graph_for_module(order["class_uri"].rsplit("#", 1)[0])
        if order_graph is not None:
            for prop in set(order_graph.subjects(RDFS.domain, order_class)):
                name = local_name(str(prop))
                if {t.lower() for t in tokenize(name)} & MODE_WORDS:
                    errors.append(
                        f"multimodal-order-leg grain 1: property {name} on the order class "
                        "carries a mode token — mode never lives on the order "
                        "(mode-subclass-on-order anti-pattern)"
                    )
            for cls in set(order_graph.subjects(RDFS.subClassOf, order_class)):
                name = local_name(str(cls))
                if {t.lower() for t in tokenize(name)} & MODE_WORDS:
                    errors.append(
                        f"multimodal-order-leg grain 1: subclass {name} of the order class is "
                        "mode-named — mode never lives on the order"
                    )


def check_role_subclassing(warnings: list[str], errors: list[str]) -> Exemptions:
    pattern = load_pattern("qualified-role-assignment")
    anti = anti_pattern(pattern, "subclass-identity-by-role") or {}
    exemptions = Exemptions(
        anti.get("exemptions"), "qualified-role-assignment/pattern.yaml", errors
    )
    for ttl in scan_ttl_files():
        g = parse_graph(ttl, [])
        if g is None:
            continue
        rel = ttl.relative_to(REPO_ROOT)
        parents: dict[URIRef, int] = {}
        for cls, parent in g.subject_objects(RDFS.subClassOf):
            if not isinstance(parent, URIRef) or not isinstance(cls, URIRef):
                continue
            if is_deprecated(g, cls):
                continue
            if local_name(str(parent)).endswith("Party"):
                parents[parent] = parents.get(parent, 0) + 1
        for parent, count in sorted(parents.items()):
            if count >= 3 and not exemptions.exempts(str(parent)):
                warnings.append(
                    f"{rel}: {count} live subclasses of {local_name(str(parent))} look like "
                    "subclass-identity-by-role (qualified-role-assignment) — model roles as "
                    "assignments, or add a cited exemption"
                )
    return exemptions


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    print("── pattern conformance: temporal-quartet (check A, blocking) ──")
    tq_exemptions = check_temporal_quartet(errors)

    print("── pattern conformance: multimodal-order-leg (check B, blocking) ──")
    check_multimodal_order_leg(errors)

    print("── pattern conformance: subclass-identity-by-role (check C, advisory) ──")
    role_exemptions = check_role_subclassing(warnings, errors)

    for exemptions in (tq_exemptions, role_exemptions):
        for name in exemptions.unused():
            warnings.append(
                f"{exemptions.source}: exemption '{name}' matched nothing — stale entry?"
            )

    for msg in warnings:
        print(f"  ⚠ {msg}")
    for msg in errors:
        print(f"  ✗ {msg}")

    if errors:
        print(f"\n✗ pattern conformance: {len(errors)} failure(s), {len(warnings)} warning(s)")
        return 1
    print(f"\n✓ pattern conformance passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
