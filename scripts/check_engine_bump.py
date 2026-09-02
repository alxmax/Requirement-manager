#!/usr/bin/env python3
"""Fail when plugin/scripts/reqmap.py changed but MAP_ENGINE_VERSION did not.

Why this exists: `MAP_ENGINE_VERSION` is the only thing a seeded copy of the engine
(and `check/engine_staleness.py`, ARCH-STALEENGINE-043) can compare to learn it is
behind. Two engine releases in a row (v2.24.0, v2.25.0) shipped without touching
it, so every consumer on the previous copy was told it was current. The rule is
deliberately blunt — ANY diff to the engine file requires a new version, comments
included — because the staleness probe compares whole files, not behaviours.

Two modes, one per entry point:
  --staged     the dev pre-commit hook: judge the staged diff (what will be committed)
  --base REF   CI: judge `git diff REF`, with REF = HEAD~1 (the merge base on a
               pull_request checkout, the previous tip on a push)
An unresolvable REF or a non-git directory prints SKIP and exits 0, matching the
`git rev-parse HEAD~1` guard on the CHANGELOG-entry check.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE = "plugin/scripts/reqmap.py"
# diff lines only: `+MAP_ENGINE_VERSION = "..."` / `-MAP_ENGINE_VERSION = "..."`
ADDED_RE = re.compile(r'^\+MAP_ENGINE_VERSION\s*=\s*"([^"]+)"', re.M)
REMOVED_RE = re.compile(r'^-MAP_ENGINE_VERSION\s*=\s*"([^"]+)"', re.M)


def _engine_diff(diff_args, cwd):
    """The engine file's diff text, or None when git cannot produce one."""
    try:
        r = subprocess.run(["git", "diff", "--no-color", *diff_args, "--", ENGINE],
                           cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def main(argv=None, cwd=None) -> int:
    ap = argparse.ArgumentParser(
        description="Fail when plugin/scripts/reqmap.py changed but MAP_ENGINE_VERSION did not.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true", help="judge the staged diff (pre-commit hook)")
    mode.add_argument("--base", metavar="REF", help="judge `git diff REF` (CI; typically HEAD~1)")
    a = ap.parse_args(argv)
    cwd = cwd or str(REPO_ROOT)

    diff = _engine_diff(["--cached"] if a.staged else [a.base], cwd)
    if diff is None:
        print("SKIP  cannot diff {} (not a git checkout, or the base ref does not resolve)".format(ENGINE))
        return 0
    if not diff.strip():
        print("OK  {} unchanged - no MAP_ENGINE_VERSION bump needed".format(ENGINE))
        return 0
    added, removed = ADDED_RE.search(diff), REMOVED_RE.search(diff)
    if added and removed and added.group(1) != removed.group(1):
        print("OK  {} changed and MAP_ENGINE_VERSION bumped {!r} -> {!r}".format(
            ENGINE, removed.group(1), added.group(1)))
        return 0
    print("FAIL  {} changed but MAP_ENGINE_VERSION did not.\n"
          "      A seeded copy compares this version to learn it is behind (ARCH-STALEENGINE-043);\n"
          "      without a bump every consumer is told it is current. Set it to today's date\n"
          "      (YYYY-MM-DD, or YYYY-MM-DD.N for a second bump the same day) in this same change."
          .format(ENGINE))
    return 1


if __name__ == "__main__":
    sys.exit(main())
