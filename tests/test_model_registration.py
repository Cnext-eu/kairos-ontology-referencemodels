# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Fan-out tests: one industry model, registered consistently across every surface.

Why this file exists
--------------------
Adding the RAIL (TAF TSI) and IATA ONE Record models in v1.14.0/v1.15.0 touched about
fifteen files, and six of them were missed. Every miss was in a surface with **no machine
reader**: the pack README still said "8 ontologies" and "currently 1.6.0" while the pack
was at 1.10.0 with eleven imports; the ``.intro`` version tables were four releases stale;
``data-domains.yaml`` never learned that RAIL exists.

None of the existing gates could see any of it. ``version_manager.py`` checks that a
module's ``VERSION`` matches its own ``owl:versionInfo`` — not that anything *else* agrees.
``validate_structure.py`` checks folder shape. So a model could be fully valid in isolation
and still be invisible to the people and tools that consume the pack.

These tests encode the fan-out instead: ``manifest.yaml`` is the single hand-edited
registry, and every other surface must agree with it. One new model, one registry edit, and
a failing test for each surface that was forgotten.

The escape hatch is deliberate: :func:`test_every_include_reaches_data_domains` accepts an
explicit ``data_domain_status`` in the manifest. A known gap that is written down is a
tracked gap; the failure mode being closed here is the *silent* one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from rdflib import Graph
from rdflib.namespace import OWL

REPO_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_ROOT = REPO_ROOT / "ontology-reference-models"
CATALOG_PATH = ONTOLOGY_ROOT / "catalog-v001.xml"
PACKS_DIR = ONTOLOGY_ROOT / "accelerator-packs"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from catalog_utils import CatalogResolver  # noqa: E402


#: Pre-existing financial-services gaps, recorded so this file can land without silently
#: widening its own scope. Each entry is a real defect these tests surfaced on first run;
#: none is caused by the change that introduced them. Fixing them needs FIBO judgement
#: about which ontology was intended, which is a financial-services decision.
#:
#:  * ``advertised_not_imported`` — ``manifest.yaml`` claims eleven FIBO module groups; the
#:    accelerator imports four leaf ontologies, all under ``BE/`` and ``FND/``. Either the
#:    manifest overstates the bundle or the accelerator under-imports it.
#:  * ``uncatalogued_domain_imports`` — three ``data-domains.yaml`` entries name FIBO
#:    ontologies absent from the vendored release (``RealEstateLoans/MortgageLoans/`` when
#:    the file is ``Mortgages.rdf``; ``TemporalCore/SecurityTemporal/`` and
#:    ``DerivativesTemporal/DerivativesPricing/``, neither of which exists). The toolkit
#:    reads this file, so these mislead a client hub today.
#:
#: A gap outside these lists — in any pack — fails. That is the point.
KNOWN_GAPS: dict[str, dict[str, set[str]]] = {
    "financial-services": {
        "advertised_not_imported": {
            "https://spec.edmcouncil.org/fibo/ontology/ACTUS/",
            "https://spec.edmcouncil.org/fibo/ontology/BP/",
            "https://spec.edmcouncil.org/fibo/ontology/CAE/",
            "https://spec.edmcouncil.org/fibo/ontology/DER/",
            "https://spec.edmcouncil.org/fibo/ontology/FBC/",
            "https://spec.edmcouncil.org/fibo/ontology/IND/",
            "https://spec.edmcouncil.org/fibo/ontology/LOAN/",
            "https://spec.edmcouncil.org/fibo/ontology/MD/",
            "https://spec.edmcouncil.org/fibo/ontology/SEC/",
        },
        "uncatalogued_domain_imports": {
            "https://spec.edmcouncil.org/fibo/ontology/LOAN/RealEstateLoans/MortgageLoans/",
            "https://spec.edmcouncil.org/fibo/ontology/MD/DerivativesTemporal/DerivativesPricing/",
            "https://spec.edmcouncil.org/fibo/ontology/MD/TemporalCore/SecurityTemporal/",
        },
    },
}


def _known(pack_name: str, key: str) -> set[str]:
    return KNOWN_GAPS.get(pack_name, {}).get(key, set())


def _packs() -> list[Path]:
    """Every accelerator pack directory that ships a manifest."""
    return sorted(p for p in PACKS_DIR.iterdir() if p.is_dir() and (p / "manifest.yaml").is_file())


PACK_IDS = [p.name for p in _packs()]


def _norm(uri: str) -> str:
    """Normalise an ontology IRI for comparison (drop the trailing ``#`` or ``/``)."""
    return uri.rstrip("#").rstrip("/")


@pytest.fixture(scope="module")
def resolver() -> CatalogResolver:
    return CatalogResolver(CATALOG_PATH)


@pytest.fixture(params=_packs(), ids=PACK_IDS)
def pack(request) -> dict:
    """Load one pack's manifest, accelerator imports, and data-domain URIs."""
    pack_dir: Path = request.param
    manifest = yaml.safe_load((pack_dir / "manifest.yaml").read_text(encoding="utf-8"))["package"]

    accelerator = next((pack_dir / "current").glob("*-accelerator.ttl"))
    graph = Graph()
    graph.parse(accelerator, format="turtle")
    imports = {_norm(str(o)) for _, _, o in graph.triples((None, OWL.imports, None))}

    dd_path = pack_dir / "client-hub-blueprint" / "data-domains.yaml"
    domain_uris: set[str] = set()
    if dd_path.is_file():
        dd = yaml.safe_load(dd_path.read_text(encoding="utf-8")) or {}
        for group in dd.get("groups", []) or []:
            for domain in group.get("domains", []) or []:
                for imp in domain.get("imports", []) or []:
                    if imp.get("uri"):
                        domain_uris.add(_norm(imp["uri"]))
        # Bridge modules appear as relationship endpoints rather than domain imports.
        for rel in dd.get("cross_domain_relationships", []) or []:
            for key in ("property_uri", "inverse_of"):
                if rel.get(key):
                    domain_uris.add(_norm(str(rel[key]).split("#", 1)[0]))

    return {
        "name": pack_dir.name,
        "dir": pack_dir,
        "manifest": manifest,
        "imports": imports,
        "domain_uris": domain_uris,
    }


def test_every_include_is_imported_by_the_accelerator(pack) -> None:
    """A module the manifest advertises must actually be in the bundle.

    Matching is by prefix, because a manifest may name a module *group* whose members are
    imported individually (financial-services lists FIBO's ``FND/``, and the accelerator
    imports ``FND/Agreements/Contracts/``).
    """
    allowed = _known(pack["name"], "advertised_not_imported")
    missing = [
        entry["uri"]
        for entry in pack["manifest"].get("includes", []) or []
        if entry["uri"] not in allowed
        and not any(
            imported == _norm(entry["uri"]) or imported.startswith(_norm(entry["uri"]) + "/")
            for imported in pack["imports"]
        )
    ]
    assert not missing, (
        f"{pack['name']}: manifest.yaml advertises modules the accelerator never imports: "
        f"{missing}"
    )


def test_references_are_not_bulk_imported(pack) -> None:
    """``references`` is the reference-only tier — catalogued, deliberately not imported.

    IATA ONE Record is mirrored so a hub can bind to it at the reservation grain, but
    bulk-importing it into the pack would drag an entire external cargo model into every
    consumer — the same reason FIBO is excluded from logistics.
    """
    leaked = [
        entry["uri"]
        for entry in pack["manifest"].get("references", []) or []
        if _norm(entry["uri"]) in pack["imports"]
    ]
    assert not leaked, (
        f"{pack['name']}: reference-only modules are owl:imported by the accelerator: {leaked}. "
        "Either drop the import or promote the entry to 'includes'."
    )


def test_every_manifest_module_is_catalogued(pack, resolver) -> None:
    """Every advertised module must resolve offline through ``catalog-v001.xml``."""
    unresolved = [
        entry["uri"]
        for kind in ("includes", "references")
        for entry in pack["manifest"].get(kind, []) or []
        if not resolver.is_mapped(entry["uri"])
    ]
    assert not unresolved, (
        f"{pack['name']}: manifest modules with no catalog mapping: {unresolved}"
    )


def test_every_accelerator_import_is_catalogued(pack, resolver) -> None:
    """The bundle must be resolvable offline: no import may escape the catalog."""
    unresolved = sorted(uri for uri in pack["imports"] if not resolver.is_mapped(uri))
    assert not unresolved, (
        f"{pack['name']}: accelerator owl:imports with no catalog mapping: {unresolved}"
    )


def test_every_data_domain_import_is_catalogued(pack, resolver) -> None:
    """``data-domains.yaml`` is read by the toolkit; a dangling URI there misleads a client hub."""
    dd_path = pack["dir"] / "client-hub-blueprint" / "data-domains.yaml"
    if not dd_path.is_file():
        pytest.skip(f"{pack['name']} ships no data-domains.yaml")
    dd = yaml.safe_load(dd_path.read_text(encoding="utf-8")) or {}
    allowed = _known(pack["name"], "uncatalogued_domain_imports")
    unresolved = sorted(
        {
            imp["uri"]
            for group in dd.get("groups", []) or []
            for domain in group.get("domains", []) or []
            for imp in domain.get("imports", []) or []
            if imp.get("uri")
            and imp["uri"] not in allowed
            and not resolver.is_mapped(imp["uri"])
        }
    )
    assert not unresolved, (
        f"{pack['name']}: data-domains.yaml imports with no catalog mapping: {unresolved}"
    )


def test_every_include_reaches_data_domains(pack) -> None:
    """A model in the bundle must be reachable from the surface clients actually design against.

    This is the RAIL regression. RAIL shipped in the accelerator, the catalog, the pattern
    library and the discovery guides — and never reached ``data-domains.yaml``, so a hub
    classifying an air- or rail-cargo source system had nowhere to put it.

    A module may opt out by declaring ``data_domain_status`` in ``manifest.yaml`` with a
    reason. That keeps a known gap tracked rather than silent.
    """
    dd_path = pack["dir"] / "client-hub-blueprint" / "data-domains.yaml"
    if not dd_path.is_file():
        pytest.skip(f"{pack['name']} ships no data-domains.yaml")

    unreached = []
    for entry in pack["manifest"].get("includes", []) or []:
        if entry.get("data_domain_status"):
            continue
        uri = _norm(entry["uri"])
        if any(d == uri or d.startswith(uri + "/") for d in pack["domain_uris"]):
            continue
        unreached.append(entry["uri"])

    assert not unreached, (
        f"{pack['name']}: modules in the bundle that data-domains.yaml never references: "
        f"{unreached}. Wire them into a domain's imports, or declare 'data_domain_status' "
        "on the manifest entry with a reason."
    )
