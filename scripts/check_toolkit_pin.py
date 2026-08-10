# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
#!/usr/bin/env python3
"""Keep the pinned ``kairos-ontology-toolkit`` release current with its channel.

Why this exists
---------------
The toolkit is declared in ``pyproject.toml`` as a direct wheel URL:

    kairos-ontology-toolkit @ https://github.com/.../v<version>/kairos_ontology_toolkit-<version>-py3-none-any.whl

A URL dependency is exact by construction. ``uv``/``pip`` resolve precisely that artifact
and will never advance it, and ``[tool.kairos].channel`` is not a packaging mechanism —
it is a hint read by ``kairos-ontology update --upgrade``, a command a human has to run.

So the pin only moves when somebody remembers. In practice nobody did: the repo sat on
``5.1.0rc2`` while the toolkit shipped eight further releases, and the local ``.venv`` was
older still (``4.5.0rc4``), leaving three different versions in play at once — installed,
pinned, and published. The cross-repo contract tests silently skipped the whole time,
because the loader they import only exists in later releases.

This script closes that loop: it asks GitHub what the newest release on the configured
channel is and compares it to the pin.

Channels (``[tool.kairos].channel`` in ``pyproject.toml``):
  * ``stable``  — newest final release (no ``rc``/``beta``/``alpha`` suffix)
  * ``preview`` — newest release of any kind, pre-releases included
  * ``<version>`` — an explicit pin; the check is skipped, the value must match

Network policy: this is the one script here that talks to the network, so it degrades
rather than fails. With no network, no ``gh``, and no token it reports "undetermined" and
exits 0 — a firewalled contributor is not a broken build. Run it in a CI job that has
network if you want it enforced.

Usage:
    python scripts/check_toolkit_pin.py            # report
    python scripts/check_toolkit_pin.py --check    # exit 1 when behind
    python scripts/check_toolkit_pin.py --update   # rewrite the pin, then run `uv lock`
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"

TOOLKIT_REPO = "Cnext-eu/kairos-ontology-toolkit"
RELEASES_API = f"https://api.github.com/repos/{TOOLKIT_REPO}/releases?per_page=100"

_PIN_RE = re.compile(
    r"(kairos-ontology-toolkit @ https://github\.com/[^/]+/[^/]+/releases/download/v)"
    r"(?P<version>[^/]+)"
    r"(/kairos_ontology_toolkit-)(?P=version)(-py3-none-any\.whl)"
)
_CHANNEL_RE = re.compile(r"^\s*channel\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)
_PRERELEASE_RE = re.compile(r"(rc|a|b|alpha|beta|dev)\d*$", re.IGNORECASE)


def pinned_version(text: str) -> str | None:
    match = _PIN_RE.search(text)
    return match.group("version") if match else None


def configured_channel(text: str) -> str:
    match = _CHANNEL_RE.search(text)
    return match.group(1) if match else "stable"


def _version_key(version: str) -> tuple:
    """Sort key: release number first, then pre-release ordering (rc > b > a > dev)."""
    head, _, tail = version.partition("rc")
    numeric = tuple(int(p) for p in re.findall(r"\d+", head))
    # A final release outranks any pre-release of the same number.
    stage = 1 if not _PRERELEASE_RE.search(version) else 0
    rc_number = int(tail) if tail.isdigit() else 0
    return (numeric, stage, rc_number)


def latest_release(channel: str) -> str | None:
    """Newest release tag for *channel*, or None when it cannot be determined."""
    payload = _fetch_releases()
    if payload is None:
        return None
    tags = []
    for release in payload:
        tag = str(release.get("tag_name", "")).lstrip("v")
        if not tag or release.get("draft"):
            continue
        if channel == "stable" and (release.get("prerelease") or _PRERELEASE_RE.search(tag)):
            continue
        tags.append(tag)
    return max(tags, key=_version_key) if tags else None


def _fetch_releases() -> list[dict] | None:
    """Release list via ``gh`` (uses existing auth) falling back to the anonymous API."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{TOOLKIT_REPO}/releases?per_page=100"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    try:
        with urllib.request.urlopen(RELEASES_API, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit 1 if the pin is behind.")
    parser.add_argument("--update", action="store_true", help="Rewrite the pin and re-lock.")
    args = parser.parse_args(argv)

    text = PYPROJECT.read_text(encoding="utf-8")
    pinned = pinned_version(text)
    if pinned is None:
        print("✗ Could not find a kairos-ontology-toolkit wheel pin in pyproject.toml")
        return 1
    channel = configured_channel(text)

    if channel not in {"stable", "preview"}:
        ok = channel.lstrip("v") == pinned
        print(
            f"{'✓' if ok else '✗'} channel is an explicit pin ({channel}); "
            f"pyproject has {pinned}"
        )
        return 0 if ok or not args.check else 1

    latest = latest_release(channel)
    if latest is None:
        print(f"⚠ Latest '{channel}' release undetermined (offline or unauthenticated).")
        print(f"  Pinned: {pinned}. Not failing — this check needs network access.")
        return 0

    if _version_key(pinned) >= _version_key(latest):
        print(f"✓ Toolkit pin {pinned} is current for channel '{channel}' (latest {latest}).")
        return 0

    print(f"✗ Toolkit pin is behind: pinned {pinned}, latest '{channel}' is {latest}.")
    if not args.update:
        print("  Run: python scripts/check_toolkit_pin.py --update")
        return 1 if args.check else 0

    PYPROJECT.write_text(_PIN_RE.sub(rf"\g<1>{latest}\g<3>{latest}\g<5>", text), encoding="utf-8")
    print(f"  ✎ pyproject.toml → {latest}")
    lock = subprocess.run(["uv", "lock"], cwd=REPO_ROOT, capture_output=True, text=True)
    if lock.returncode != 0:
        print(f"✗ `uv lock` failed:\n{lock.stderr.strip()}")
        return 1
    print("  ✎ uv.lock regenerated. Run `uv sync --extra dev` to install.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
