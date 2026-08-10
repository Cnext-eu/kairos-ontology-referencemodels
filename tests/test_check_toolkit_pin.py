# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Unit tests for the toolkit pin gate.

``--check`` was verified by hand when it was written; ``--update`` was not, and it shipped with
``\\g<5>`` in its replacement against a pattern that has four groups. It raised ``PatternError``
the first time CI asked it to do anything — which is the whole point of a mode that only runs
when something is already wrong. These tests exercise the rewrite without touching the network.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_toolkit_pin as pin  # noqa: E402

_PYPROJECT = """\
[project]
dependencies = [
    "kairos-ontology-toolkit @ https://github.com/Cnext-eu/kairos-ontology-toolkit/releases/download/v5.2.0rc6/kairos_ontology_toolkit-5.2.0rc6-py3-none-any.whl",
]

[tool.kairos]
channel = "preview"
"""


def test_pin_and_channel_are_parsed() -> None:
    assert pin.pinned_version(_PYPROJECT) == "5.2.0rc6"
    assert pin.configured_channel(_PYPROJECT) == "preview"


def test_rewrite_replaces_both_occurrences() -> None:
    """The version appears twice — URL path and wheel filename. Both must move together.

    A rewrite that updated only one would produce a URL that 404s at install time rather than
    failing here, so this asserts the old string is gone entirely.
    """
    updated = pin._PIN_RE.sub(r"\g<1>5.2.0rc8\g<3>5.2.0rc8\g<4>", _PYPROJECT)
    assert updated.count("5.2.0rc8") == 2
    assert "5.2.0rc6" not in updated
    assert pin.pinned_version(updated) == "5.2.0rc8"
    assert "/download/v5.2.0rc8/kairos_ontology_toolkit-5.2.0rc8-py3-none-any.whl" in updated


@pytest.mark.parametrize(
    ("older", "newer"),
    [
        ("5.2.0rc6", "5.2.0rc8"),
        ("5.1.0rc2", "5.2.0rc1"),
        ("5.1.0rc9", "5.1.0rc10"),  # numeric, not lexicographic
        ("5.2.0rc8", "5.2.0"),      # a final release outranks its own pre-releases
        ("4.9.0", "5.0.0"),
    ],
)
def test_version_ordering(older: str, newer: str) -> None:
    assert pin._version_key(older) < pin._version_key(newer)


def test_explicit_channel_pin_is_not_compared_to_releases() -> None:
    """An explicit `channel = "v5.2.0rc6"` means the pin is deliberate — never 'behind'."""
    text = _PYPROJECT.replace('channel = "preview"', 'channel = "v5.2.0rc6"')
    assert pin.configured_channel(text) == "v5.2.0rc6"
    assert pin.configured_channel(text).lstrip("v") == pin.pinned_version(text)


def test_missing_pin_is_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A pyproject with no toolkit wheel URL must fail loudly, not pass vacuously."""
    broken = tmp_path / "pyproject.toml"
    broken.write_text("[project]\ndependencies = []\n", encoding="utf-8")
    monkeypatch.setattr(pin, "PYPROJECT", broken)
    assert pin.main(["--check"]) == 1
