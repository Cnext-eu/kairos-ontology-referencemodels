# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Kairos ontology reference models — distributable data package.

This package ships the ontology reference models (FIBO, IATA ONE Record,
blueprints, archetypes, patterns, etc.) as wheel data so downstream hubs
can resolve them via ``importlib.resources`` instead of a vendored copy.

The package itself is data-only; it has no runtime dependencies on the
kairos-ontology-toolkit. The toolkit is in ``[dev]`` extras for contract
testing only.
"""

from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files
from pathlib import Path

try:
    __version__ = version("kairos-ontology-referencemodels")
except PackageNotFoundError:  # pragma: no cover — editable/source checkout
    __version__ = "0.0.0+unknown"


def refmodels_root() -> Path:
    """Return the reference-models data directory from this installed package.

    For a wheel install this is a real filesystem path under ``site-packages``.
    For an editable install it resolves to the source checkout.
    """
    return Path(files(__package__) / "ontology-reference-models")
