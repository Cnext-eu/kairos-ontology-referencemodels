# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Cross-repo contract tests: this repo's published surface, read by the real consumer.

Everything here loads **this working tree** through the actual loaders in
``kairos-ontology-toolkit``, rather than through a fixture or a local re-implementation
of what we believe the consumer does.

Why this file exists
--------------------
``blueprints/patterns/temporal-quartet/pattern.yaml`` shipped in v1.13.0 as invalid YAML
— a stray ``rule:`` mapping key inside a block sequence, which reads perfectly fine to a
human reviewer. It went undetected for two minor versions. Not because either repo
behaved badly: the toolkit's ``load_patterns`` returns a warning for a malformed pattern
and ``kairos-ontology list-patterns`` prints it to stderr. It went undetected because the
toolkit's own tests use synthetic fixtures, and nobody ever pointed it at a real
reference-models checkout. Neither repo's CI could see the other.

These tests close that specific hole from this side. The mirror lives in the toolkit at
``tests/test_refmodels_contract.py``.

Skipping
--------
Skipped when the toolkit source is not on this machine, so CI here stays green without a
cross-repo dependency. Set ``KAIROS_TOOLKIT_SRC`` to the toolkit's ``src/`` directory to
point at a checkout elsewhere; otherwise the sibling ``../kairos-ontology-toolkit/src``
is probed. Local-only: nothing here fetches over the network.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_ROOT = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models"
ARCHETYPE_SCHEMA = ONTOLOGY_ROOT / "blueprints" / "archetypes" / "_schema" / "archetype.schema.json"


def _toolkit_src() -> Path | None:
    """Return the toolkit ``src/`` directory, or None when it is not available."""
    override = os.environ.get("KAIROS_TOOLKIT_SRC")
    candidates = [Path(override)] if override else []
    candidates.append(REPO_ROOT.parent / "kairos-ontology-toolkit" / "src")
    for candidate in candidates:
        if (candidate / "kairos_ontology" / "core" / "pattern_loader.py").is_file():
            return candidate
    return None


TOOLKIT_SRC = _toolkit_src()

pytestmark = pytest.mark.skipif(
    TOOLKIT_SRC is None,
    reason=(
        "kairos-ontology-toolkit source not found — set KAIROS_TOOLKIT_SRC or place a "
        "checkout at ../kairos-ontology-toolkit"
    ),
)


@pytest.fixture(scope="module")
def toolkit():
    """Import the toolkit's loaders, skipping if its own dependencies are absent."""
    src = str(TOOLKIT_SRC)
    added = src not in sys.path
    if added:
        sys.path.insert(0, src)
    try:
        from kairos_ontology.core import archetype_loader, pattern_loader
    except ImportError as exc:  # toolkit present but its deps are not installed here
        pytest.skip(f"toolkit import failed ({exc}) — install its dependencies to run this")
    yield archetype_loader, pattern_loader
    if added and src in sys.path:
        sys.path.remove(src)


def test_every_pattern_loads_through_the_real_loader(toolkit) -> None:
    """The regression test for the v1.13.0 defect.

    ``load_pattern`` is the fail-fast path — it raises on malformed YAML rather than
    warning — so this is what turns an unparseable ``pattern.yaml`` into a red build
    instead of a pattern that quietly never reaches the design flow.
    """
    _, pattern_loader = toolkit
    ids = pattern_loader.list_patterns(ONTOLOGY_ROOT)
    assert ids, "pattern library is empty or unreachable from the repo root"
    for pattern_id in ids:
        pattern = pattern_loader.load_pattern(ONTOLOGY_ROOT, pattern_id)
        assert pattern.id == pattern_id, f"{pattern_id}: declared id does not match directory"


def test_bulk_pattern_load_emits_no_warnings(toolkit) -> None:
    """A warning here means a pattern is being skipped, and skipped is invisible.

    ``load_patterns`` degrades gracefully by design so advisory surfacing never breaks
    the design loop. That is correct for the consumer and useless as a signal for us —
    a published library should give it nothing to warn about.
    """
    _, pattern_loader = toolkit
    patterns, warnings = pattern_loader.load_patterns(ONTOLOGY_ROOT)
    assert warnings == [], f"toolkit skipped published patterns: {warnings}"
    assert len(patterns) == len(pattern_loader.list_patterns(ONTOLOGY_ROOT))


def test_tier_enum_matches_the_consumer_copy(toolkit) -> None:
    """``VALID_TIERS`` is duplicated in the toolkit and comments that it mirrors ours.

    Nothing enforces that mirror, so adding a tier (e.g. the proposed ``not_applicable``)
    to our schema alone would break the consumer at its next ref-model bump. This test
    makes the two repos disagree loudly and at the right moment.
    """
    archetype_loader, _ = toolkit
    schema = json.loads(ARCHETYPE_SCHEMA.read_text(encoding="utf-8"))
    schema_tiers = schema["$defs"]["tier"]["enum"]
    assert sorted(archetype_loader.VALID_TIERS) == sorted(schema_tiers), (
        "archetype.schema.json $defs/tier and the toolkit's VALID_TIERS have diverged — "
        "a tier change needs a coordinated PR in both repos"
    )


def test_every_archetype_loads_through_the_real_loader(toolkit) -> None:
    """Catalog files must survive the consumer's own schema validation and URI resolution."""
    archetype_loader, _ = toolkit
    archetype_ids = sorted(
        path.stem
        for path in (ONTOLOGY_ROOT / "blueprints" / "archetypes").glob("*.yaml")
        if not path.name.startswith(".")
    )
    assert archetype_ids, "no archetype catalogs found"
    for archetype_id in archetype_ids:
        catalog = archetype_loader.load_archetype(ONTOLOGY_ROOT, archetype_id)
        assert catalog.core_concepts, f"{archetype_id}: no core concepts resolved"
        for concept in catalog.core_concepts:
            assert concept.tier in archetype_loader.VALID_TIERS


def test_transport_order_tiering_is_visible_to_the_consumer(toolkit) -> None:
    """The archetype tiering only works if the consumer actually sees all three positions.

    ``TransportOrder`` is required for the forwarder, recommended for the unit-load
    carrier, and absent for the shipping carrier — which is supply side, so its incoming
    demand already *is* the booking. The absence is deliberate and, with no
    ``not_applicable`` tier, is recorded only as a YAML comment the loader cannot read;
    this test is the machine-readable half of that statement.
    """
    archetype_loader, _ = toolkit
    order_uri = "https://www.kairosflow.ai/ont/blueprint/transport-order#TransportOrder"

    def tier_of(archetype_id: str) -> str | None:
        catalog = archetype_loader.load_archetype(ONTOLOGY_ROOT, archetype_id)
        return next((c.tier for c in catalog.core_concepts if c.uri == order_uri), None)

    assert tier_of("freight-forwarder") == "required"
    assert tier_of("unit-load-carrier") == "recommended"
    assert tier_of("shipping-carrier") is None
