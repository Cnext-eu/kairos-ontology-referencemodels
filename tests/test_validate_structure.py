# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Focused tests for repository structure classification."""

from pathlib import Path

from scripts.validate_structure import find_domain_subfolders


def test_accelerator_support_folders_are_not_domain_modules(tmp_path: Path) -> None:
    accelerator = tmp_path / "accelerator-packs" / "logistics"
    current = accelerator / "current"
    current.mkdir(parents=True)
    for name in ("blueprint", "profiles", "contracts", "examples", "docs", "real-domain"):
        (current / name).mkdir()

    assert [path.name for path in find_domain_subfolders(accelerator)] == ["real-domain"]


def test_support_named_folders_remain_domains_outside_accelerators(tmp_path: Path) -> None:
    ontology = tmp_path / "derived-ontologies" / "example"
    current = ontology / "current"
    (current / "docs").mkdir(parents=True)

    assert [path.name for path in find_domain_subfolders(ontology)] == ["docs"]
