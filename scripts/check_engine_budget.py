#!/usr/bin/env python3
# implements: ARCH-SELFGATE-039
"""Measure the engine's core in logical lines and fail above the budget.

ADR-0046 made the engine's size a release gate; ADR-0053 changed what is
measured. The budget no longer covers every file `wc -l` counts:

- CORE is the modules the engine's own routine actually loads. One
  subprocess builds a throwaway repository (one requirement, one tagged
  code file, a CHANGELOG), runs `sync` and `gate --full` against it
  in-process, and reads `reqmap_engine.*` back out of `sys.modules`.
  `reqmap.py`, the command line, is always counted. The list is derived
  on every run, never written down, so a module the routine stops
  loading leaves the core without an edit here.
- The unit is the logical line: one `tokenize.NEWLINE` token per
  statement. Rewrapping a statement over several physical lines, or
  adding blank and comment lines, moves it by 0, so formatting cannot
  spend or earn budget.

The physical total, exactly
`wc -l plugin/scripts/reqmap.py plugin/scripts/reqmap_engine/*.py | tail -1`,
is still printed, because every CHANGELOG entry quotes it. It is judged
only against a ceiling, TOTAL_LINE_CEILING, set by the maintainer as an
alarm: it does not say what the engine should weigh, only that crossing
it deserves a look before a release. Tests are not the engine and are not
counted.

The budget is the stage the core has reached, not the direction: it is
lowered by the change that earns the lower number, in the same commit. CI
runs this only on the path that cuts a NEW release, so an over-budget
core blocks a tag, never a commit.

  --budget N   judge the core against N instead of CORE_LOGICAL_BUDGET
               (a dry run of the gate)
  --ceiling N  judge the physical total against N instead of
               TOTAL_LINE_CEILING
"""
import argparse
import functools
import json
import subprocess
import sys
import tempfile
import tokenize
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = REPO_ROOT / "plugin" / "scripts"
PACKAGE = "reqmap_engine"
# The stage reached, lowered only by the change that earns it (ADR-0046).
# Set by ADR-0053 to the measured core, in logical lines, with no headroom.
CORE_LOGICAL_BUDGET = 7049
# An alarm, not a target (ADR-0053): the maintainer's line in the sand for
# the whole vendored engine, in physical lines. It moves only by decision.
TOTAL_LINE_CEILING = 17000

# Run in a fresh interpreter: argv[1] is the scripts dir, argv[2] the
# fixture repository. Prints the loaded engine modules as one JSON line.
_PROBE = """
import contextlib, io, json, sys
scripts, root = sys.argv[1:3]
sys.path.insert(0, scripts)
import reqmap
rcs = []
for verb in (["sync"], ["gate", "--full"]):
    sys.argv = ["reqmap.py"] + verb + ["--root", root]
    with contextlib.redirect_stdout(io.StringIO()):
        rcs.append(reqmap.main())
names = sorted(n for n in sys.modules
               if n == "{pkg}" or n.startswith("{pkg}."))
sys.stdout.write("\\nCORE " + json.dumps([rcs, names]) + "\\n")
""".format(pkg=PACKAGE)


def _write_fixture(root):
    """One confirmed requirement, one code file tagged with it, and a
    CHANGELOG: the smallest repository `sync` and `gate` both pass on.
    The tag is assembled here so this file carries no phantom member."""
    rid = "REQ-CORE-001"
    reqs = root / "requirements"
    reqs.mkdir()
    (reqs / (rid + ".md")).write_text(
        "---\nid: {}\nstatus: confirmed\nlayer: feature\nowner: probe\n"
        "---\n\n# Core probe\n\n## Description\n\n- The probe runs.\n\n"
        "## Cases\n\n- CASE-1 - runs: Given the probe, When it is "
        "called, Then it returns 1.\n".format(rid), encoding="utf-8")
    role = "implem" + "ents"
    (root / "probe.py").write_text(
        "def probe():  # {}: {}\n    return 1\n".format(role, rid),
        encoding="utf-8")
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## `v0.1.0`\n\n- first\n", encoding="utf-8")


@functools.lru_cache(maxsize=None)
def core_modules(scripts_dir=ENGINE_DIR):
    """The engine modules `sync` + `gate --full` load, sorted: derived by
    running both in one subprocess against a fixture repository."""
    with tempfile.TemporaryDirectory() as d:
        _write_fixture(Path(d))
        p = subprocess.run(
            [sys.executable, "-X", "utf8", "-c", _PROBE,
             str(scripts_dir), d],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, encoding="utf-8", cwd=d)
    line = p.stdout.rpartition("\nCORE ")[2].strip()
    if p.returncode or not line:
        raise RuntimeError("core probe failed:\n" + p.stdout + p.stderr)
    rcs, names = json.loads(line)
    if any(rcs):
        # A failed run skips work, so its module set understates the core.
        raise RuntimeError("core probe: sync/gate exit codes {} on the "
                           "fixture\n{}".format(rcs, p.stderr))
    return names


def core_files(scripts_dir=ENGINE_DIR):
    """`reqmap.py` plus the source file of every core module."""
    files = [scripts_dir / "reqmap.py"]
    for name in core_modules(scripts_dir):
        parts = name.split(".")
        if len(parts) == 1:
            files.append(scripts_dir / parts[0] / "__init__.py")
        else:
            files.append(scripts_dir.joinpath(*parts[:-1])
                         / (parts[-1] + ".py"))
    return files


def logical_lines(source):
    """The number of `tokenize.NEWLINE` tokens in `source`: one per
    statement, however it is wrapped, blank and comment lines excluded."""
    lines = iter(source.splitlines(True))
    return sum(1 for t in tokenize.generate_tokens(lambda: next(lines, ""))
               if t.type == tokenize.NEWLINE)


def core_logical_lines(scripts_dir=ENGINE_DIR):
    """Logical lines over `core_files`."""
    return sum(logical_lines(p.read_text(encoding="utf-8"))
               for p in core_files(scripts_dir))


def engine_files(scripts_dir):
    """The files `wc -l` covers: `reqmap.py` plus `reqmap_engine/*.py`,
    sorted."""
    pkg = sorted((scripts_dir / PACKAGE).glob("*.py"))
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
    ap.add_argument("--budget", type=int, default=CORE_LOGICAL_BUDGET)
    ap.add_argument("--ceiling", type=int, default=TOTAL_LINE_CEILING)
    a = ap.parse_args(argv)
    n = core_logical_lines()
    m = len(core_files())
    core_ok = n <= a.budget
    print("{}  core is {:,} logical lines in {} modules, budget {:,}"
          .format("OK" if core_ok else "FAIL", n, m, a.budget))
    total = engine_lines()
    total_ok = total <= a.ceiling
    print("{}  total is {:,} physical lines in {} files, ceiling {:,}"
          .format("OK" if total_ok else "FAIL", total,
                  len(engine_files(ENGINE_DIR)), a.ceiling))
    return 0 if core_ok and total_ok else 1


if __name__ == "__main__":
    sys.exit(main())
