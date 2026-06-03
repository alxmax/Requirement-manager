#!/usr/bin/env python3
"""Repo-local version-coherence gate (dev/CI tooling — NOT part of the seeded engine).

The same version string lives in several static manifests that no single process
can derive at load time (Claude Code reads plugin.json / marketplace.json as data;
they cannot import Python). This script is the single point that asserts they agree,
so drift fails the build instead of shipping silently.

Two independent axes are checked:
  - semver  — canonical source is plugin/.claude-plugin/plugin.json `version`.
              Every occurrence in .claude-plugin/marketplace.json must equal it
              (top-level `version` + each `plugins[].version`).
  - engine  — MAP_ENGINE_VERSION in plugin/scripts/reqmap.py is an ISO date with a
              different purpose (staleness compare); it is only sanity-checked for
              valid YYYY-MM-DD shape, never compared against the semver.

This deliberately does NOT live inside reqmap.py's `check` subcommand: reqmap.py is
copied verbatim into consumer repos that have no plugin.json / marketplace.json, so
manifest coherence is this repo's concern, not the portable engine's.

Exit 0 = aligned. Exit 1 = drift (with a readable diff). Exit 2 = a file/field is
missing or unreadable. stdlib only.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = REPO_ROOT / "plugin" / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
REQMAP_PY = REPO_ROOT / "plugin" / "scripts" / "reqmap.py"

MAP_ENGINE_RE = re.compile(r'MAP_ENGINE_VERSION\s*=\s*"([^"]+)"')


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"ERROR  cannot read {path.relative_to(REPO_ROOT)}: {e}")
        raise SystemExit(2)


def main() -> int:
    errors: list[str] = []

    plugin = _load_json(PLUGIN_JSON)
    canonical = plugin.get("version")
    if not canonical:
        print(f"ERROR  no `version` in {PLUGIN_JSON.relative_to(REPO_ROOT)}")
        return 2

    # Every semver occurrence in marketplace.json must equal the canonical source.
    market = _load_json(MARKETPLACE_JSON)
    occurrences = [("marketplace.version", market.get("version"))]
    for i, plug in enumerate(market.get("plugins", [])):
        occurrences.append((f"marketplace.plugins[{i}].version", plug.get("version")))
    for label, value in occurrences:
        if value != canonical:
            errors.append(f"  {label}: {value!r} != plugin.json version {canonical!r}")

    # Engine version is a separate axis — only validate it is a real ISO date.
    try:
        text = REQMAP_PY.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR  cannot read {REQMAP_PY.relative_to(REPO_ROOT)}: {e}")
        return 2
    m = MAP_ENGINE_RE.search(text)
    if not m:
        errors.append("  reqmap.py: MAP_ENGINE_VERSION not found")
        engine = None
    else:
        engine = m.group(1)
        try:
            dt.date.fromisoformat(engine)
        except ValueError:
            errors.append(f"  reqmap.py: MAP_ENGINE_VERSION {engine!r} is not a valid ISO date (YYYY-MM-DD)")

    if errors:
        print("FAIL  version drift detected:")
        print("\n".join(errors))
        print(f"\ncanonical semver (plugin.json) = {canonical!r}")
        return 1

    print(f"OK  semver aligned at {canonical!r} across "
          f"{1 + len(occurrences)} location(s); engine MAP_ENGINE_VERSION = {engine!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
