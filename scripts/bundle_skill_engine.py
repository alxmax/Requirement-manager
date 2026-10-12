#!/usr/bin/env python3
"""Keep the engine the requirement-manager skill carries equal to plugin/scripts/.

An APM install copies one directory, `skills/<name>/`, and nothing beside it, so
the engine in `plugin/scripts/` would not arrive with the skill. The skill
therefore carries a copy of what a consumer seeds: `reqmap.py`, the
`reqmap_engine/` package and `_map_viewer.html`. The layout under the skill is
the layout under the plugin, so `REQMAP_PLUGIN_ROOT` names either directory and
the seeding commands do not change.

The copy is generated, committed, and re-derived in CI (ADR-0068, the same
trade as ADR-0005). Never edit it by hand; edit plugin/scripts/ and run this.

    python scripts/bundle_skill_engine.py            # rewrite the copy
    python scripts/bundle_skill_engine.py --check    # exit 1 when it is stale

Dev/CI tooling, not part of the seeded engine. stdlib only.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "plugin" / "scripts"
DEST = REPO_ROOT / "plugin" / "skills" / "requirement-manager" / "scripts"
FILES = ("reqmap.py", "_map_viewer.html")
PACKAGE = "reqmap_engine"


def wanted(source: Path) -> dict:
    """{posix path relative to the scripts dir: file} that the skill carries."""
    out = {name: source / name for name in FILES}
    for path in sorted((source / PACKAGE).rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            out[path.relative_to(source).as_posix()] = path
    return out


def _held(dest: Path) -> dict:
    if not dest.is_dir():
        return {}
    return {p.relative_to(dest).as_posix(): p for p in sorted(dest.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def _text(path: Path) -> bytes:
    # a Windows checkout may hand both sides CRLF; only content is drift
    return path.read_bytes().replace(b"\r\n", b"\n")


def diff(source: Path = SOURCE, dest: Path = DEST) -> list:
    """One line per way the copy differs from the source; [] when equal."""
    want, held = wanted(source), _held(dest)
    problems = [f"missing  {rel}" for rel in want if rel not in held]
    problems += [f"differs  {rel}" for rel in want
                 if rel in held and _text(want[rel]) != _text(held[rel])]
    problems += [f"stale    {rel}" for rel in held if rel not in want]
    return problems


def build(source: Path = SOURCE, dest: Path = DEST) -> int:
    """Replace `dest` with the wanted files; returns how many were written."""
    if dest.exists():
        shutil.rmtree(dest)
    want = wanted(source)
    for rel, path in want.items():
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    return len(want)


def main(argv=None) -> int:
    """Rewrite the skill's engine copy, or with --check report whether stale."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="write nothing; exit 1 when the copy is not current")
    a = ap.parse_args(argv)
    rel = DEST.relative_to(REPO_ROOT).as_posix()
    if a.check:
        problems = diff()
        if problems:
            print(f"FAIL  {rel} is not the engine in plugin/scripts/:")
            print("\n".join(f"  {p}" for p in problems))
            print("run `python scripts/bundle_skill_engine.py` and commit it")
            return 1
        print(f"OK  {rel} matches plugin/scripts/ ({len(wanted(SOURCE))} files)")
        return 0
    print(f"wrote  {build()} file(s) to {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
