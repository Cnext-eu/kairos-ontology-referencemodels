# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Tests for the archetype concept -> data-domain reachability gate (gh#98).

A class can be perfectly modelled, correctly imported by *a* domain, and still be
unreachable from the domain that needs it, because data-domains.yaml scopes imports
per domain and nothing checked the result against what the archetypes say a hub
requires. mmt/cargo#Dimension was routed to `cargo` and `roro` only, while the
`equipment` and `consignment` domains that carry the dimension columns could not see
it at all — which produced a false reference-model gap report.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_archetypes import (  # noqa: E402
    _load_domain_routing,
    _normalise_module,
    _reachability_findings,
)

KAIROS = "https://www.kairosflow.ai/ont"
DIMENSION = f"{KAIROS}/mmt/cargo#Dimension"


def _concepts(*entries: tuple[str, str]) -> dict[str, list[tuple[str, str, str]]]:
    """Build the archetype_concepts mapping from (uri, tier) pairs."""
    return {"unit-load-carrier.yaml": [(uri, tier, "label") for uri, tier in entries]}


# ── unreachable concepts ─────────────────────────────────────────────────────

def test_required_concept_routed_nowhere_is_blocking() -> None:
    errors, warnings, _ = _reachability_findings(
        _concepts((f"{KAIROS}/mmt/locations#Location", "required")), {}, {}
    )
    assert len(errors) == 1
    assert "not reachable from any data domain" in errors[0]
    assert warnings == []


@pytest.mark.parametrize("tier", ["recommended", "optional"])
def test_non_required_concept_routed_nowhere_only_warns(tier: str) -> None:
    """Blocking on optional concepts would make the gate unadoptable.

    The tier is the pack's own statement of how load-bearing the concept is, so it
    is the right lever for blocking-versus-advisory.
    """
    errors, warnings, _ = _reachability_findings(
        _concepts((f"{KAIROS}/mmt/transport-means#Aircraft", tier)), {}, {}
    )
    assert errors == []
    assert any("not reachable" in w for w in warnings)


# ── the two reachability mechanisms ──────────────────────────────────────────

def test_direct_module_import_makes_a_concept_reachable() -> None:
    errors, warnings, singles = _reachability_findings(
        _concepts((DIMENSION, "recommended")),
        {f"{KAIROS}/mmt/cargo": {"cargo"}},
        {},
    )
    assert errors == []
    assert not any("not reachable" in w for w in warnings)
    assert singles == [("cargo", "recommended", DIMENSION)]


def test_a_bridge_alone_makes_a_concept_reachable() -> None:
    """A declared cross-domain bridge is a first-class reachability mechanism.

    The consumer widens a domain's alignment pool with each bridge's range_class_uri,
    so a bridged class is anchorable without the consuming domain importing the
    module. That is what makes "bridge, not import" a real fix for gh#98 rather than
    a paper one.
    """
    errors, warnings, singles = _reachability_findings(
        _concepts((DIMENSION, "required")),
        {},
        {DIMENSION: {"equipment"}},
    )
    assert errors == []
    assert singles == [("equipment", "required", DIMENSION)]


def test_bridge_is_keyed_by_class_not_module() -> None:
    """A bridge exposes exactly its range_class_uri, not its whole module.

    This is why gh#98 needed one bridge entry per (class, domain) pair: a bridge to
    mmt/cargo#Dimension does not also expose mmt/cargo#Weight.
    """
    errors, _, _ = _reachability_findings(
        _concepts((f"{KAIROS}/mmt/cargo#Weight", "required")),
        {},
        {DIMENSION: {"equipment"}},
    )
    assert len(errors) == 1, "a Dimension bridge must not make Weight reachable"


def test_imports_and_bridges_are_unioned() -> None:
    """The owning domain and every bridging domain both count."""
    _, _, singles = _reachability_findings(
        _concepts((DIMENSION, "recommended")),
        {f"{KAIROS}/mmt/cargo": {"cargo", "roro"}},
        {DIMENSION: {"equipment", "consignment"}},
    )
    assert singles == [], "four domains reach it, so it is not a single-domain concept"


# ── the single-domain summary ────────────────────────────────────────────────

def test_single_domain_concepts_are_summarised_not_enumerated() -> None:
    """One summary warning, not one per concept.

    The issue proposed flagging every concept reachable from exactly one domain as
    the cheap first step. Measured against the shipped archetypes that fires on 340
    of 416 concepts, because belonging to one domain is the normal case for an owned
    class. Enumerating them would bury the real findings.
    """
    entries = tuple((f"{KAIROS}/mmt/cargo#C{i}", "recommended") for i in range(5))
    errors, warnings, singles = _reachability_findings(
        _concepts(*entries), {f"{KAIROS}/mmt/cargo": {"cargo"}}, {}
    )
    assert errors == []
    assert len(singles) == 5
    assert len(warnings) == 1
    assert "5 of 5" in warnings[0]


# ── module normalisation ─────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "value",
    [
        f"{KAIROS}/mmt/cargo#",
        f"{KAIROS}/mmt/cargo#Dimension",
        f"{KAIROS}/mmt/cargo",
    ],
)
def test_normalise_module_folds_import_and_concept_forms(value: str) -> None:
    """data-domains writes ``.../cargo#``; archetypes write ``.../cargo#Dimension``.

    Both must fold to the same module key or every lookup misses.
    """
    assert _normalise_module(value) == f"{KAIROS}/mmt/cargo"


# ── against the real shipped pack ────────────────────────────────────────────

def test_shipped_packs_route_the_gh98_measurement_classes() -> None:
    """The gh#98 fix must be live in the committed data-domains.yaml.

    Guards the bridges themselves, not just the checker: equipment and consignment
    must reach the MMT measurement value objects they could not see before.
    """
    module_to_domains, bridged_to_domains, packs = _load_domain_routing()
    assert packs >= 1

    assert "equipment" in bridged_to_domains.get(DIMENSION, set())
    for local in ("Dimension", "Weight", "CargoMeasurement"):
        uri = f"{KAIROS}/mmt/cargo#{local}"
        assert "consignment" in bridged_to_domains.get(uri, set()), local


def test_shipped_packs_route_every_vendor_locations_and_party_module() -> None:
    """mmt/locations and dcsa/party were unrouted while their siblings were routed.

    Five tier-required concepts on mmt/locations and four on dcsa/party were
    unreachable from every domain until gh#98 surfaced them.
    """
    module_to_domains, _, _ = _load_domain_routing()
    assert module_to_domains.get(f"{KAIROS}/mmt/locations")
    assert module_to_domains.get(f"{KAIROS}/dcsa/party")
