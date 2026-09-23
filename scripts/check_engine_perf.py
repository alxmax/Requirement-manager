#!/usr/bin/env python3
# implements: ARCH-SELFGATE-039
"""Time the engine's gate and import against this repository's own corpus.

Report only: it records numbers and always exits 0, except on a usage
error (exit 2). A command that fails is reported as failed, never raised;
a non-zero exit keeps its timings, since the gate still did its work.
The pinned snapshot is "this repository at this commit", named in the
output together with the runner, so a later change can turn the median
plus three sample standard deviations into a threshold.

Every command runs from `plugin/`, cold: no `--cache` flag, and
`requirements/_scancache.json` is deleted before each run.

  --runs N    runs per command (default 10; lower only for tests)
  --json      print a JSON document instead of text
  --summary   append a markdown table to $GITHUB_STEP_SUMMARY when set
"""
import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNS = 10
RUN_TIMEOUT_S = 600
IMPORT_SNIPPET = ("import sys; sys.path.insert(0,'scripts'); "
                  "import reqmap")
# (label, arguments after `python -X utf8`), each run from plugin/.
COMMANDS = (
    ("gate --full --code ..",
     ["scripts/reqmap.py", "gate", "--full", "--code", ".."]),
    ("gate --code ..", ["scripts/reqmap.py", "gate", "--code", ".."]),
    ("import reqmap", ["-c", IMPORT_SNIPPET]),
)


# --- statistics: pure, no engine involved ---------------------------------

def median(xs):
    """Median of a non-empty sequence of numbers."""
    return statistics.median(xs)


def sample_sd(xs):
    """Sample standard deviation (n - 1); 0.0 below two samples."""
    if len(xs) < 2:
        return 0.0
    return statistics.stdev(xs)


def summarize(xs):
    """{n, median_s, sd_s} of a list of seconds."""
    return {"n": len(xs), "median_s": median(xs), "sd_s": sample_sd(xs)}


# --- environment ------------------------------------------------------------

def runner_info(env=None):
    """The machine the numbers came from."""
    env = os.environ if env is None else env
    return {"system": platform.system(),
            "release": platform.release(),
            "python": platform.python_version(),
            "runner_os": env.get("RUNNER_OS"),
            "image_os": env.get("ImageOS")}


def runner_text(info):
    parts = ["{} {}".format(info["system"], info["release"]),
             "python " + info["python"]]
    if info.get("runner_os"):
        parts.append("RUNNER_OS=" + info["runner_os"])
    if info.get("image_os"):
        parts.append("ImageOS=" + info["image_os"])
    return ", ".join(parts)


def _run(argv, cwd):
    """One subprocess, output captured; the default `run` of `main`."""
    return subprocess.run(argv, cwd=str(cwd), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=RUN_TIMEOUT_S,
                          encoding="utf-8", errors="replace")


def git_commit(root, run=_run):
    """`git rev-parse --short HEAD`, or `unknown`."""
    try:
        cp = run(["git", "rev-parse", "--short", "HEAD"], root)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    out = (cp.stdout or "").strip()
    return out if cp.returncode == 0 and out else "unknown"


# --- measurement ------------------------------------------------------------

def _last_line(text):
    lines = [ln for ln in (text or "").splitlines() if ln.strip()]
    return lines[-1].strip() if lines else ""


def measure(argv, cwd, runs, run=_run, clock=time.perf_counter,
            before=None):
    """Time `argv` `runs` times -> {status, samples_s, n, median_s, sd_s}.

    A non-zero exit marks the command failed, with the first such exit as
    `error`, but its runs stay timed: a gate that reached a FAIL verdict
    still did all its work. An exception (no interpreter, timeout) stops
    the command and keeps no numbers."""
    samples, error = [], None
    for _ in range(runs):
        if before is not None:
            before()
        t0 = clock()
        try:
            cp = run(argv, cwd)
        except (OSError, subprocess.SubprocessError) as e:
            return {"status": "failed", "samples_s": [],
                    "error": "{}: {}".format(type(e).__name__, e)}
        samples.append(clock() - t0)
        if cp.returncode != 0 and error is None:
            err = _last_line(cp.stderr) or _last_line(cp.stdout)
            error = "exit {}: {}".format(cp.returncode, err)
    rec = {"status": "failed" if error else "ok", "samples_s": samples}
    if error:
        rec["error"] = error
    rec.update(summarize(samples))
    return rec


def _clear_cache(plugin_dir):
    def clear():
        p = Path(plugin_dir) / "requirements" / "_scancache.json"
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    return clear


def collect(root, runs, run=_run, clock=time.perf_counter, env=None):
    """The whole report as one dict (what --json prints)."""
    plugin_dir = Path(root) / "plugin"
    report = {"runner": runner_info(env), "corpus": str(plugin_dir),
              "commit": git_commit(root, run), "n": runs,
              "cold": True, "commands": []}
    for label, args in COMMANDS:
        argv = [sys.executable, "-X", "utf8"] + args
        rec = {"name": label, "argv": ["python"] + argv[1:]}
        rec.update(measure(argv, plugin_dir, runs, run, clock,
                           _clear_cache(plugin_dir)))
        report["commands"].append(rec)
    return report


# --- output -----------------------------------------------------------------

def render_text(rep):
    out = ["engine perf (report only, never fails)",
           "runner: " + runner_text(rep["runner"]),
           "corpus: {} (this repository at {})".format(
               rep["corpus"], rep["commit"]),
           "commit: " + rep["commit"],
           "n: {} runs per command, cold (no --cache)".format(rep["n"])]
    width = max(len(c["name"]) for c in rep["commands"])
    for c in rep["commands"]:
        line = "  " + c["name"].ljust(width)
        if c["samples_s"]:
            line += "  median {:.3f} s  sd {:.3f} s".format(
                c["median_s"], c["sd_s"])
        if c["status"] != "ok":
            line += "  FAILED " + c["error"]
        out.append(line)
    return "\n".join(out) + "\n"


def _cells(c):
    """(median, sd, status) cells of one command's markdown row."""
    nums = ("{:.3f}".format(c["median_s"]), "{:.3f}".format(c["sd_s"]))
    if not c["samples_s"]:
        nums = ("-", "-")
    if c["status"] == "ok":
        return nums + ("ok",)
    return nums + ("failed: " + c["error"].replace("|", "\\|"),)


def render_markdown(rep):
    out = ["## Engine performance (report only)", "",
           "Runner: {} - corpus `{}` - commit `{}` - n = {} per command, "
           "cold (no `--cache`)".format(runner_text(rep["runner"]),
                                         rep["corpus"], rep["commit"],
                                         rep["n"]),
           "", "| command | median (s) | sd (s) | status |",
           "|---|---:|---:|---|"]
    for c in rep["commands"]:
        out.append("| `{}` | {} | {} | {} |".format(c["name"], *_cells(c)))
    return "\n".join(out) + "\n\n"


def main(argv=None, run=_run, clock=time.perf_counter, root=REPO_ROOT,
         env=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args(argv)
    if a.runs < 1:
        ap.error("--runs must be at least 1")
    env = os.environ if env is None else env
    rep = collect(root, a.runs, run, clock, env)
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print(render_text(rep), end="")
    target = env.get("GITHUB_STEP_SUMMARY")
    if a.summary and target:
        try:
            with open(target, "a", encoding="utf-8") as f:
                f.write(render_markdown(rep))
        except OSError as e:
            print("summary not written: {}".format(e), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
