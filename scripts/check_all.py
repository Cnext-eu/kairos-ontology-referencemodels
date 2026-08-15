# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
"""Tier-1 contributor gate: run the toolkit-free CI steps locally, in CI order.

``.github/workflows/validate.yml`` is the single definition of what must pass before a
PR merges. This script parses that file and executes the ``validate`` job's ``run:``
blocks in order, so the local gate and the CI gate cannot drift apart — reuse, not
restatement (the same lesson that unified release.yml onto validate.yml in v1.17.0).

It deliberately does NOT run the tier-2 gate. The cross-repo contract job needs the
pinned toolkit installed (``uv sync --extra dev``), which this script leaves to the
contributor — no implicit installs, no network fetches. When tier 1 is green it prints
the exact tier-2 command as a hint.

Steps using actions (``uses:``) — checkout, setup-python, artifact upload, PR comment —
have no local meaning and are skipped. The dependency-install step is also skipped
(listed in SKIP_STEPS): this script assumes the current interpreter already carries
pytest/jsonschema/pyyaml/rdflib, which the dev extras provide.

Windows caveat: CI runs these steps in POSIX sh on ubuntu-latest. Locally each ``run:``
block goes through ``subprocess`` with ``shell=True`` — cmd.exe on Windows, sh on
POSIX. All steps are plain single-command invocations, so both shells cope, but if a
future step uses POSIX-only syntax, Windows contributors should run the commands
directly or via Git-bash/WSL. CI remains the authoritative gate.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate.yml"

#: Steps that provision the environment or report results; meaningless locally.
SKIP_STEPS = {
    "Checkout repository",
    "Set up Python",
    "Install validation dependencies",
    "Upload validation results",
    "Comment on PR",
}

TIER2_HINT = """\
Tier 1 is green. Now run the tier-2 contract gate against the pinned toolkit:

    uv sync --extra dev
    python -m pytest tests/test_toolkit_contract.py tests/test_bundle_conformance.py -v -ra -p no:randomly

(Tier 2 verifies the toolkit can actually read this bundle; it is not run here
because it requires installing the pinned toolkit via uv.)
"""


def _load_validate_steps() -> list[dict]:
    """Extract the ``validate`` job's steps from validate.yml. Fail loudly on drift."""
    if not WORKFLOW.is_file():
        sys.exit(f"ERROR: workflow not found: {WORKFLOW}")
    try:
        workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        steps = workflow["jobs"]["validate"]["steps"]
    except (yaml.YAMLError, KeyError, TypeError) as exc:
        sys.exit(
            f"ERROR: cannot parse the 'validate' job's steps from {WORKFLOW}: {exc}. "
            "check_all.py intentionally has no hardcoded fallback — the workflow is the "
            "single source of truth, so fix the script when the workflow shape changes."
        )
    if not isinstance(steps, list):
        sys.exit(f"ERROR: jobs.validate.steps is not a list in {WORKFLOW}")
    return steps


def _inline_run(command: str) -> str:
    """Flatten a possibly multiline ``run:`` block to a single shell invocation."""
    lines = [ln for ln in command.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return " && ".join(ln.strip() for ln in lines)


def main() -> int:
    steps = _load_validate_steps()
    print(f"check_all: tier-1 gate parsed from {WORKFLOW.relative_to(REPO_ROOT)}\n")

    ran = 0
    for step in steps:
        name = step.get("name") or "<unnamed step>"
        if name in SKIP_STEPS or "uses" in step:
            print(f"SKIP  {name}")
            continue
        command = step.get("run")
        if command is None:
            # A step with neither uses: nor run: has drifted in a way this script
            # does not understand — treat it as a visible skip, not a silent pass.
            print(f"SKIP  {name} (no run: block)")
            continue
        ran += 1
        print(f"\n>>>   {name}")
        result = subprocess.run(_inline_run(command), shell=True, cwd=REPO_ROOT)
        if result.returncode != 0:
            print(f"\nFAIL  {name} (exit {result.returncode})")
            return result.returncode
        print(f"OK    {name}")

    print(f"\ntier-1 gate passed ({ran} steps).\n")
    print(TIER2_HINT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
