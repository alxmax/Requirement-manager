#!/usr/bin/env python3
# implements: ARCH-SELFGATE-039
"""Print the shipped engine's line count and fail when it is above the
budget (ADR-0046).

The count is the one number every CHANGELOG entry and this check quote,
and it is exactly
`wc -l plugin/scripts/reqmap.py plugin/scripts/reqmap_engine/*.py | tail -1`:
newline characters over the CLI module and the package's top-level
modules, blank lines and comments included. Tests are not the engine and
are not counted.

The budget is the stage the engine has reached, not the direction: it is
lowered by the change that earns the lower number, in the same commit. CI
runs this only on the path that cuts a NEW release, so an over-budget
engine blocks a tag, never a commit.

  --budget N   judge against N instead of ENGINE_LINE_BUDGET (a dry run of
               the gate)
"""
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = REPO_ROOT / "plugin" / "scripts"
# The stage reached, lowered only by the change that earns it (ADR-0046):
# 14,962 before design review, site generation and the i18n detector left.
# Raised once, to the measured size, by ADR-0052: the design review and the
# site came back, all code was rewrapped to 80 columns and four modules were
# split. A stop-gap until the metric itself is replaced; see that record.
ENGINE_LINE_BUDGET = 16753


def engine_files(scripts_dir):
    """The files the budget covers: `reqmap.py` plus `reqmap_engine/*.py`,
    sorted."""
    pkg = sorted((scripts_dir / "reqmap_engine").glob("*.py"))
    return [scripts_dir / "reqmap.py"] + pkg


def engine_lines(scripts_dir=ENGINE_DIR):
    """Newline count over `engine_files` — what `wc -l ... | tail -1`
    prints."""
    total = 0
    for p in engine_files(scripts_dir):
        total += p.read_bytes().count(b"\n")
    return total


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget", type=int, default=ENGINE_LINE_BUDGET)
    a = ap.parse_args(argv)
    n = engine_lines()
    if n > a.budget:
        print("FAIL  engine is {:,} lines, over the budget of {:,} by "
              "{:,} - cut before releasing, or record why the budget "
              "moves (ADR-0046)"
              .format(n, a.budget, n - a.budget))
        return 1
    print("OK  engine is {:,} lines, budget {:,}".format(n, a.budget))
    return 0


if __name__ == "__main__":
    sys.exit(main())
