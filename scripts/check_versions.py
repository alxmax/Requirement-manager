#!/usr/bin/env python3
# implements: ARCH-SELFGATE-039
"""Repo-local version-coherence gate (dev/CI tooling — NOT part of the seeded engine).

The same version string lives in several static manifests that no single process
can derive at load time (Claude Code reads plugin.json / marketplace.json as data;
they cannot import Python). This script is the single point that asserts they agree,
so drift fails the build instead of shipping silently.

Three independent axes are checked:
  - semver  — canonical source is plugin/.claude-plugin/plugin.json `version`.
              Every occurrence in .claude-plugin/marketplace.json must equal it
              (top-level `version` + each `plugins[].version`).
  - engine  — MAP_ENGINE_VERSION in plugin/scripts/reqmap.py is an ISO date with a
              different purpose (staleness compare); it is only sanity-checked for
              valid YYYY-MM-DD shape, with an optional `.N` (N>=1) same-day revision
              suffix, never compared against the semver.
  - action  — the published GitHub Action's major-alias tag (`.../check@vN`). It tracks
              the PLUGIN's major since ADR-0029 (`check@v4` ships with plugin 4.x), and the
              release job force-moves it onto each released commit. It was a third,
              independent axis until then: sound in itself, and a third number to hold. The
              documented `uses:` reference IS the source of truth (there is no separate
              version file to fall out of step with the docs), so every occurrence
              across check/action.yml, README.md, CLAUDE.md and the two requirement-manager
              SKILL files must name the same major.
              This axis exists because `@v1` sat frozen 193 commits behind main for two
              months while the README kept advertising it.

This deliberately does NOT live inside reqmap.py's `check` subcommand: reqmap.py is
copied verbatim into consumer repos that have no plugin.json / marketplace.json, so
manifest coherence is this repo's concern, not the portable engine's.

Exit 0 = aligned. Exit 1 = drift (with a readable diff). Exit 2 = a file/field is
missing or unreadable. stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = REPO_ROOT / "plugin" / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
REQMAP_PY = REPO_ROOT / "plugin" / "scripts" / "reqmap.py"
# Files that quote the action's major-alias tag. action.yml is listed first: it is the
# file the tag actually publishes, so it is reported as the canonical one on a mismatch.
ACTION_REF_FILES = (
    "check/action.yml", "README.md", "CLAUDE.md",
    # The skill files are what a consumer actually reads when wiring CI — they
    # advertised `@v1` for three releases after the docs above moved to `@v2`.
    "plugin/skills/requirement-manager/SKILL.md",
    "plugin/skills/requirement-manager/SKILL.universal.md",
)

# line-anchored so a docstring/comment mention before the real assignment can't win
MAP_ENGINE_RE = re.compile(r'^MAP_ENGINE_VERSION\s*=\s*"([^"]+)"', re.M)
# `alxmax/requirement-manager/check@v2` — the full published path, so a bare `@v1`
# mentioned in prose (e.g. "`@v1` is frozen") is not mistaken for a live reference.
ACTION_REF_RE = re.compile(r'requirement-manager/check@(v\d+)')


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"ERROR  cannot read {path.relative_to(REPO_ROOT)}: {e}")
        raise SystemExit(2)


def _fix(canonical: str) -> int:
    """Propagate the canonical plugin.json version into every marketplace.json
    occurrence, so a bump is one edit + one command instead of three hand-edits.
    Rewrites only when something changed; preserves 2-space indent + trailing NL."""
    market = _load_json(MARKETPLACE_JSON)
    before = json.dumps(market, sort_keys=True)
    market["version"] = canonical
    for plug in market.get("plugins", []):
        if isinstance(plug, dict):
            plug["version"] = canonical
    if json.dumps(market, sort_keys=True) == before:
        print(f"OK  marketplace.json already at {canonical!r} — nothing to fix.")
        return 0
    MARKETPLACE_JSON.write_text(json.dumps(market, indent=2) + "\n", encoding="utf-8")
    print(f"fixed  marketplace.json synced to {canonical!r}.")
    return 0


def main(argv=None) -> int:
    """Assert that every manifest agrees on the version (or rewrite them under
    `--fix`), and return an exit code."""
    ap = argparse.ArgumentParser(description="Assert (or --fix) version coherence across the manifests.")
    ap.add_argument("--fix", action="store_true",
                    help="rewrite marketplace.json to match plugin.json's version, then verify")
    a = ap.parse_args(argv)

    errors: list[str] = []

    plugin = _load_json(PLUGIN_JSON)
    canonical = plugin.get("version")
    if not canonical:
        print(f"ERROR  no `version` in {PLUGIN_JSON.relative_to(REPO_ROOT)}")
        return 2

    if a.fix:
        rc = _fix(canonical)
        if rc:
            return rc

    # Every semver occurrence in marketplace.json must equal the canonical source.
    market = _load_json(MARKETPLACE_JSON)
    occurrences = [("marketplace.version", market.get("version"))]
    for i, plug in enumerate(market.get("plugins", [])):
        if isinstance(plug, dict):
            occurrences.append((f"marketplace.plugins[{i}].version", plug.get("version")))
        else:
            errors.append(f"  marketplace.plugins[{i}] is not an object: {plug!r}")
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
        # YYYY-MM-DD with an optional `.N` same-day revision suffix (N a positive
        # integer) — lets a second engine bump on the same calendar day get a
        # distinct, still lexicographically-ordered version.
        base, sep, rev = engine.partition(".")
        valid = True
        try:
            dt.date.fromisoformat(base)
        except ValueError:
            valid = False
        if sep and not (rev.isdigit() and int(rev) >= 1):
            valid = False
        if not valid:
            errors.append(f"  reqmap.py: MAP_ENGINE_VERSION {engine!r} is not a valid YYYY-MM-DD date "
                          f"with an optional .N (N>=1) same-day revision")

    # Action alias — tracks the plugin's major (ADR-0029). Every documented `uses:`
    # reference must name one major, and that major must be the plugin's.
    action_major, action_refs = None, []
    for rel in ACTION_REF_FILES:
        path = REPO_ROOT / rel
        try:
            found = ACTION_REF_RE.findall(path.read_text(encoding="utf-8"))
        except OSError as e:
            errors.append(f"  {rel}: cannot read ({e})")
            continue
        if not found:
            errors.append(f"  {rel}: no `requirement-manager/check@vN` reference found")
            continue
        action_refs.extend((rel, major) for major in found)
    if action_refs:
        action_major = action_refs[0][1]
        for rel, major in action_refs:
            if major != action_major:
                errors.append(f"  {rel}: action alias {major!r} != {action_major!r} in "
                              f"{action_refs[0][0]}")
        # ADR-0029: the alias is the plugin's major. A rule only documented is a rule that
        # drifts — this is what makes `v4.0.0` shipping as `@v3` a failed build rather than
        # something a reader has to notice.
        plugin_major = "v" + canonical.split(".")[0]
        if action_major != plugin_major:
            errors.append(f"  action alias {action_major!r} != plugin major {plugin_major!r} "
                          f"(ADR-0029: the alias tracks the plugin's major)")

    if errors:
        print("FAIL  version drift detected:")
        print("\n".join(errors))
        print(f"\ncanonical semver (plugin.json) = {canonical!r}")
        return 1

    print(f"OK  semver aligned at {canonical!r} across "
          f"{1 + len(occurrences)} location(s); engine MAP_ENGINE_VERSION = {engine!r}; "
          f"action alias {action_major!r} across {len(action_refs)} reference(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
