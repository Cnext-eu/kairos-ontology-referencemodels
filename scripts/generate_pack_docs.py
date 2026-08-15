# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Cnext.eu
#!/usr/bin/env python3
"""Regenerate the derived blocks of accelerator-pack documentation.

Why this exists
---------------
Every documentation surface that restates a fact from ``manifest.yaml`` or a module
``VERSION`` file has, at some point, gone stale. At v1.15.0 the logistics pack README still
said it imported "8 ontologies" and was "currently 1.6.0" — the bundle had eleven imports
and the pack was at 1.10.0 — while the two ``.intro`` version tables were four releases
behind. Nothing could see any of it, because prose has no reader.

So these facts are no longer written by hand. ``manifest.yaml`` plus the per-module
``VERSION`` files are the source; this script renders them into marker-delimited blocks:

    <!-- BEGIN GENERATED: <block> -->
    ... rendered content, do not edit ...
    <!-- END GENERATED: <block> -->

Only the region between the markers is replaced, so the hand-written narrative around it
("Who is this for?", "How to use") is untouched. ``--check`` re-renders and diffs without
writing, which is what CI runs — the same contract as
``generate_logistics_inventory.py --check``.

Scope: the ``version`` block is rendered for every pack. The module table and the
``.intro`` tables are logistics-only, because financial-services advertises FIBO *module
groups* rather than versioned Kairos modules and has no ``.intro`` set; rendering a version
column for it would invent data.

Usage:
    python scripts/generate_pack_docs.py            # rewrite in place
    python scripts/generate_pack_docs.py --check    # fail if anything is stale
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

import yaml

# Ensure UTF-8 output on Windows (mirrors validate_archetypes.py).
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
ONTOLOGY_ROOT = REPO_ROOT / "kairos_ontology_referencemodels" / "ontology-reference-models"
PACKS_DIR = ONTOLOGY_ROOT / "accelerator-packs"
DERIVED_DIR = ONTOLOGY_ROOT / "derived-ontologies"
AUTHORITATIVE_DIR = ONTOLOGY_ROOT / "authoritative-ontologies"

#: Packs whose module/intro tables are generated. See the module docstring for why this is
#: not simply "every pack".
VERSIONED_PACKS = {"logistics"}

_BLOCK_RE_CACHE: dict[str, re.Pattern[str]] = {}


def _block_re(name: str) -> re.Pattern[str]:
    if name not in _BLOCK_RE_CACHE:
        _BLOCK_RE_CACHE[name] = re.compile(
            rf"(<!-- BEGIN GENERATED: {re.escape(name)} -->\n).*?(<!-- END GENERATED: {re.escape(name)} -->)",
            re.DOTALL,
        )
    return _BLOCK_RE_CACHE[name]


def _slug(value: str) -> str:
    """Fold an id for matching across naming styles (``supply-chain`` vs ``SupplyChain``)."""
    return value.replace("-", "").replace("_", "").lower()


def _module_dir(module_id: str) -> Path | None:
    """Locate a module's folder under derived- or authoritative-ontologies."""
    target = _slug(module_id)
    for parent in (DERIVED_DIR, AUTHORITATIVE_DIR):
        if not parent.is_dir():
            continue
        for child in parent.iterdir():
            if child.is_dir() and _slug(child.name) == target:
                return child
    return None


def module_version(module_id: str) -> str:
    """Return a module's published version, or ``—`` when it does not carry one.

    Derived modules ship a ``VERSION`` file. Vendored authoritative mirrors do not — they
    record the upstream release in ``current/METADATA.txt`` instead, which is the honest
    thing to display for them.
    """
    folder = _module_dir(module_id)
    if folder is None:
        return "—"
    version_file = folder / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    metadata = folder / "current" / "METADATA.txt"
    if metadata.is_file():
        for line in metadata.read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("version:"):
                return line.split(":", 1)[1].strip()
    return "—"


def _manifest(pack_dir: Path) -> dict:
    return yaml.safe_load((pack_dir / "manifest.yaml").read_text(encoding="utf-8"))["package"]


def _import_count(pack_dir: Path) -> int:
    """Number of ``owl:imports`` in the pack's accelerator bundle."""
    from rdflib import Graph
    from rdflib.namespace import OWL

    accelerator = next((pack_dir / "current").glob("*-accelerator.ttl"))
    graph = Graph()
    graph.parse(accelerator, format="turtle")
    return len(set(graph.objects(predicate=OWL.imports)))


def render_version(pack_dir: Path) -> str:
    version = (pack_dir / "VERSION").read_text(encoding="utf-8").strip()
    return f"See [VERSION](VERSION) — currently **{version}**.\n"


def render_modules(pack_dir: Path) -> str:
    """The 'What's included' table: one row per manifest module, plus reference-only rows."""
    manifest = _manifest(pack_dir)
    includes = manifest.get("includes", []) or []
    references = manifest.get("references", []) or []
    count = _import_count(pack_dir)

    lines = [
        f"The {manifest['name'].replace('Kairos ', '').replace(' Pack', '')} bundles "
        f"**{len(includes)} ontologies** via **{count} `owl:imports`** "
        f"(some modules are imported at sub-module granularity):",
        "",
        "| Ontology | Standard | Version | Focus |",
        "|---|---|---|---|",
    ]
    for entry in includes:
        pending = " ⚠️ *not yet in `data-domains.yaml`*" if entry.get("data_domain_status") else ""
        lines.append(
            f"| {entry['id']} | {entry.get('name', '—')} | `{module_version(entry['id'])}` "
            f"| {entry.get('focus', '—')}{pending} |"
        )
    if references:
        lines += ["", "Reference-only — catalogued and bindable, deliberately **not** imported:", ""]
        lines += ["| Ontology | Standard | Version | Focus |", "|---|---|---|---|"]
        for entry in references:
            lines.append(
                f"| {entry['id']} | {entry.get('name', '—')} | `{module_version(entry['id'])}` "
                f"| {entry.get('focus', '—')} |"
            )
    return "\n".join(lines) + "\n"


def render_intro_versions(pack_dir: Path) -> str:
    """Version snapshot for ``.intro/README.md``: the pack plus every module it ships."""
    manifest = _manifest(pack_dir)
    pack_version = (pack_dir / "VERSION").read_text(encoding="utf-8").strip()
    lines = ["| Component | Version |", "|---|---|", f"| {manifest['name']} | {pack_version} |"]
    for entry in (manifest.get("includes", []) or []) + (manifest.get("references", []) or []):
        lines.append(f"| {entry['id']} | {module_version(entry['id'])} |")
    return "\n".join(lines) + "\n"


def render_sheets(pack_dir: Path) -> str:
    """Model-sheet index. A module with no sheet is listed as missing rather than omitted.

    Omitting it is how the gap hides: the index looked complete at eight entries while air
    and rail had shipped.
    """
    manifest = _manifest(pack_dir)
    sheets_dir = pack_dir / ".intro" / "industry-models"
    available = sorted(p.name for p in sheets_dir.glob("*.md") if p.name != "README.md")
    lines = ["| Model | Sheet | Version |", "|---|---|---|"]
    for entry in (manifest.get("includes", []) or []) + (manifest.get("references", []) or []):
        prefix = entry["id"].lower()
        match = next((s for s in available if s.lower().startswith(prefix)), None)
        cell = f"[{match}]({match})" if match else "— _no sheet yet_"
        lines.append(f"| {entry['id']} | {cell} | {module_version(entry['id'])} |")
    return "\n".join(lines) + "\n"


def build_blocks(pack_dir: Path) -> dict[Path, dict[str, str]]:
    """Map each documentation file to the generated blocks it should contain."""
    blocks: dict[Path, dict[str, str]] = {pack_dir / "README.md": {"version": render_version(pack_dir)}}
    if pack_dir.name not in VERSIONED_PACKS:
        return blocks

    blocks[pack_dir / "README.md"]["modules"] = render_modules(pack_dir)
    intro = pack_dir / ".intro"
    if (intro / "README.md").is_file():
        blocks[intro / "README.md"] = {"versions": render_intro_versions(pack_dir)}
    sheets_readme = intro / "industry-models" / "README.md"
    if sheets_readme.is_file():
        blocks[sheets_readme] = {"sheets": render_sheets(pack_dir), "versions": render_intro_versions(pack_dir)}
    return blocks


def apply_blocks(path: Path, blocks: dict[str, str]) -> tuple[str, str]:
    """Return ``(current_text, rendered_text)`` for *path*."""
    current = path.read_text(encoding="utf-8")
    updated = current
    for name, content in blocks.items():
        pattern = _block_re(name)
        if not pattern.search(updated):
            raise SystemExit(
                f"✗ {path.relative_to(REPO_ROOT)}: missing marker block '{name}'.\n"
                f"  Add:\n    <!-- BEGIN GENERATED: {name} -->\n    <!-- END GENERATED: {name} -->"
            )
        updated = pattern.sub(lambda m: m.group(1) + content + m.group(2), updated, count=1)
    return current, updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if any generated block is stale; write nothing.",
    )
    args = parser.parse_args(argv)

    stale: list[Path] = []
    written: list[Path] = []
    for pack_dir in sorted(p for p in PACKS_DIR.iterdir() if p.is_dir() and (p / "manifest.yaml").is_file()):
        for path, blocks in build_blocks(pack_dir).items():
            current, updated = apply_blocks(path, blocks)
            if current == updated:
                continue
            if args.check:
                stale.append(path)
            else:
                path.write_text(updated, encoding="utf-8")
                written.append(path)

    if args.check:
        if stale:
            print("✗ Generated documentation is stale. Run: python scripts/generate_pack_docs.py")
            for path in stale:
                print(f"    {path.relative_to(REPO_ROOT)}")
            return 1
        print("✓ Generated pack documentation is up to date.")
        return 0

    for path in written:
        print(f"  ✎ {path.relative_to(REPO_ROOT)}")
    print(f"✓ Regenerated {len(written)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
