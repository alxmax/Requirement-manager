#!/usr/bin/env python3
# implements: ARCH-SELFGATE-039
"""Keep the directory edition's copied references equal to plugin-full's.

`plugin/` carries hand-maintained copies of five reference pages that
`plugin-full/` owns. `check_versions.py` compares only the version field, so
nothing noticed when a page changed on one side (ADR-0083's bugs bullet reached
`plugin/` only, and the assistant-steps paragraph reached `plugin-full/` only).

    python scripts/sync_directory_edition.py            # overwrite the copies
    python scripts/sync_directory_edition.py --check    # exit 1 when one differs

Not copied, on purpose: `workflow.md` (opening note, `update-engine` row, ADR
links) and `requirement-quality-review/SKILL.md` (no `implements:` comment, the
'no engine in the repository' branch) differ by design, and `manual-mode.md`
exists only in `plugin/`. Dev/CI tooling, kept out of `plugin/`, which may hold
only Markdown, JSON and images. stdlib only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFS = Path("skills") / "requirement-manager" / "references"
SOURCE = REPO_ROOT / "plugin-full"
DEST = REPO_ROOT / "plugin"
COPIED = ("ci.md", "triage.md", "prose-buckets.md", "assistant-steps.md", "bugs.md")


def _text(path: Path) -> bytes:
    # a Windows checkout may hand both sides CRLF; only content is drift
    return path.read_bytes().replace(b"\r\n", b"\n")


def diff(source: Path = SOURCE, dest: Path = DEST) -> list:
    """One line per copied page that is missing or differs; [] when equal."""
    out = []
    for name in COPIED:
        src, dst = source / REFS / name, dest / REFS / name
        if not src.is_file():
            out.append(f"no source  {name}")
        elif not dst.is_file():
            out.append(f"missing    {name}")
        elif _text(src) != _text(dst):
            out.append(f"differs    {name}")
    return out


def build(source: Path = SOURCE, dest: Path = DEST) -> int:
    """Copy each page over; returns how many were written."""
    n = 0
    for name in COPIED:
        dst = dest / REFS / name
        data = _text(source / REFS / name)
        if not dst.is_file() or _text(dst) != data:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            n += 1
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when a copy differs")
    args = ap.parse_args(argv)
    problems = diff()
    if args.check:
        for line in problems:
            print(line)
        if problems:
            print("directory edition is stale: run python scripts/sync_directory_edition.py")
            return 1
        print(f"directory edition: {len(COPIED)} copied pages match plugin-full")
        return 0
    print(f"directory edition: {build()} page(s) rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
