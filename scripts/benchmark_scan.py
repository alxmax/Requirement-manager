#!/usr/bin/env python3
"""Measure the engine on a synthetic tree (dev tooling — NOT part of the seeded engine).

The README says the engine "runs in any repo". Any repo includes a large one, and the
scan is a full walk with a regex per line: the honest answer to "does this scale" is a
number, not an adjective. This builds a throwaway tree, times the four operations a
user actually waits on, and prints a table.

    python -X utf8 scripts/benchmark_scan.py            # 10,000 files
    python -X utf8 scripts/benchmark_scan.py --files 50000 --reqs 200

Deliberately NOT wired into CI: a shared runner's I/O varies far too much for a timing
assertion to mean anything, and a flaky perf gate teaches people to ignore red. Run it
by hand when touching the scan, and update the published numbers if they move.
"""
import argparse
import contextlib
import io
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "plugin", "scripts"))
import reqmap as R  # noqa: E402

REQ = """---
id: {rid}
status: confirmed
layer: bus
---

# Capability {n}

## WHAT — Contract (normative)
- `thing {n}` does one measurable thing.

## WHAT — Verify intent (open questions for the human)
- None — generated corpus.

## HOW — Acceptance (= tests)
AC-1
  Given  a tree
  When   it is scanned
  Then   the member is found
"""


def _build(root, n_files, n_reqs, tagged_every):
    """A tree shaped like a real repo: nested dirs, most files untagged."""
    reqs_dir = os.path.join(root, "requirements")
    os.makedirs(reqs_dir, exist_ok=True)
    ids = []
    for i in range(n_reqs):
        rid = "BENCH-CAP-{:03d}".format(i)
        ids.append(rid)
        with open(os.path.join(reqs_dir, rid + ".md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(REQ.format(rid=rid, n=i))
    tagged = 0
    for i in range(n_files):
        d = os.path.join(root, "src", "pkg{:02d}".format(i % 50), "mod{:02d}".format(i % 20))
        os.makedirs(d, exist_ok=True)
        body = ["def f{}():".format(i), "    return {}".format(i), ""]
        if i % tagged_every == 0:
            body.insert(0, "# {}: {}".format("impl" + "ements",
                                             ids[(i // tagged_every) % n_reqs]))
            tagged += 1
        with open(os.path.join(d, "f{}.py".format(i)), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(body))
    return reqs_dir, tagged


def _time(label, fn):
    """Time `fn` with its stdout swallowed — a few thousand WARN lines through a
    terminal would be measuring the console, not the engine."""
    buf = io.StringIO()
    t0 = time.perf_counter()
    with contextlib.redirect_stdout(buf):
        out = fn()
    return label, time.perf_counter() - t0, out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Time the engine on a synthetic tree.")
    ap.add_argument("--files", type=int, default=10000, help="source files to generate (default 10000)")
    ap.add_argument("--reqs", type=int, default=100, help="requirements to generate (default 100)")
    ap.add_argument("--tagged-every", type=int, default=10, help="tag 1 file in N (default 10)")
    a = ap.parse_args(argv)

    with tempfile.TemporaryDirectory() as root:
        t0 = time.perf_counter()
        reqs_dir, tagged = _build(root, a.files, a.reqs, a.tagged_every)
        build_s = time.perf_counter() - t0
        print("tree: {} files ({} tagged), {} requirements — generated in {:.1f}s"
              .format(a.files, tagged, a.reqs, build_s))
        print("python {}.{}.{} on {}".format(*sys.version_info[:3], sys.platform))
        print()

        rows = []
        rows.append(_time("load_requirements", lambda: R.load_requirements(reqs_dir)))
        reqs = rows[-1][2]
        rows.append(_time("scan_members", lambda: R.scan_members(root, reqs_dir)))
        members = rows[-1][2]
        # The two extra full walks the gate performs on top of scan_members, timed
        # separately so the gate's number explains itself instead of being a mystery.
        rows.append(_time("scan_ac_verifies", lambda: R.scan_ac_verifies(root, reqs_dir)))
        rows.append(_time("scan_test_levels", lambda: R.scan_test_levels(root, reqs_dir)))
        rows.append(_time("scan_all (one walk)", lambda: R.scan_all(root, reqs_dir)))
        one = rows[-1][2]
        rows.append(_time("gate (all of it)", lambda: R.cmd_check(
            reqs, members, reqs_dir, update_lock=False, code_root=root,
            ac_cover=one[1], level_cover=one[2])))
        data = R._build_map_data(reqs, members)
        rows.append(_time("build+render map", lambda: (R.render_md(data, reqs_dir),
                                                       R.render_json(data, reqs_dir))))
        print("{:<20} {:>9}".format("operation", "seconds"))
        print("-" * 30)
        for label, secs, _ in rows:
            print("{:<20} {:>9.2f}".format(label, secs))
        total = sum(r[1] for r in rows)
        print("-" * 30)
        print("{:<20} {:>9.2f}".format("total", total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
