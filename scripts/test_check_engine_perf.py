#!/usr/bin/env python3
"""Tests for check_engine_perf.py - the report-only engine timing.

No test runs the engine: every subprocess goes through an injected fake
runner and every timing through an injected fake clock.
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_engine_perf as CEP  # noqa: E402


def _clock(step=0.5):
    """A clock that advances `step` seconds per reading."""
    t = [0.0]

    def tick():
        t[0] += step
        return t[0]
    return tick


class FakeRunner:
    """Answers git with a fixed commit and every other command with exit
    0; `fail` names an argv fragment whose command exits 1, and `raises`
    one that raises OSError."""

    def __init__(self, fail=None, raises=None):
        self.fail, self.raises, self.calls = fail, raises, []

    def __call__(self, argv, cwd):
        self.calls.append((argv, cwd))
        if argv[0] == "git":
            return subprocess.CompletedProcess(argv, 0, "abc1234\n", "")
        line = " ".join(argv)
        if self.raises and self.raises in line:
            raise OSError("no such interpreter")
        if self.fail and self.fail in line:
            return subprocess.CompletedProcess(argv, 1, "",
                                               "ERROR  RM001 boom\n")
        return subprocess.CompletedProcess(argv, 0, "ok\n", "")


# tested-by: ARCH-SELFGATE-039 @integration
class EnginePerf(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "plugin" / "requirements").mkdir(parents=True)
        self.env = {"RUNNER_OS": "Linux", "ImageOS": "ubuntu24"}

    def tearDown(self):
        self.tmp.cleanup()

    def _main(self, *argv, runner=None, env=None):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = CEP.main(list(argv), run=runner or FakeRunner(),
                          clock=_clock(), root=self.root,
                          env=self.env if env is None else env)
        return rc, buf.getvalue()

    # --- statistics -------------------------------------------------------

    def test_median(self):
        self.assertEqual(2, CEP.median([3, 1, 2]))
        self.assertEqual(2.5, CEP.median([4, 1, 2, 3]))

    def test_sample_sd_uses_n_minus_one(self):
        # Mean 5, squared deviations sum to 32; 32 / 7 under n - 1.
        xs = [2, 4, 4, 4, 5, 5, 7, 9]
        self.assertAlmostEqual((32 / 7) ** 0.5, CEP.sample_sd(xs))

    def test_sample_sd_below_two_samples_is_zero(self):
        self.assertEqual(0.0, CEP.sample_sd([1.5]))
        self.assertEqual(0.0, CEP.sample_sd([]))

    def test_summarize(self):
        s = CEP.summarize([1.0, 1.0, 1.0])
        self.assertEqual({"n": 3, "median_s": 1.0, "sd_s": 0.0}, s)

    def test_measure_times_each_run(self):
        rec = CEP.measure(["x"], ".", 4, run=FakeRunner(), clock=_clock())
        self.assertEqual("ok", rec["status"])
        self.assertEqual([0.5] * 4, rec["samples_s"])
        self.assertEqual(0.5, rec["median_s"])
        self.assertEqual(0.0, rec["sd_s"])

    # --- output -------------------------------------------------------------

    def test_text_names_everything(self):
        rc, out = self._main("--runs", "3")
        self.assertEqual(0, rc)
        for needle in ("runner:", "python ", "RUNNER_OS=Linux",
                       "ImageOS=ubuntu24", "corpus: ",
                       str(self.root / "plugin"), "commit: abc1234",
                       "n: 3 runs", "median 0.500 s", "sd 0.000 s",
                       "gate --full --code ..", "gate --code ..",
                       "import reqmap"):
            self.assertIn(needle, out)

    def test_runs_cold_from_plugin(self):
        cache = self.root / "plugin" / "requirements" / "_scancache.json"
        cache.write_text("{}", encoding="utf-8")
        runner = FakeRunner()
        self._main("--runs", "2", runner=runner)
        self.assertFalse(cache.exists())
        engine = [(a, c) for a, c in runner.calls if a[0] != "git"]
        self.assertEqual(6, len(engine))
        for argv, cwd in engine:
            self.assertEqual(self.root / "plugin", Path(cwd))
            self.assertNotIn("--cache", argv)
            self.assertEqual(["-X", "utf8"], argv[1:3])

    def test_json_parses(self):
        rc, out = self._main("--runs", "2", "--json")
        self.assertEqual(0, rc)
        doc = json.loads(out)
        self.assertEqual("abc1234", doc["commit"])
        self.assertEqual(2, doc["n"])
        self.assertEqual(str(self.root / "plugin"), doc["corpus"])
        self.assertEqual("Linux", doc["runner"]["runner_os"])
        self.assertEqual(3, len(doc["commands"]))
        for c in doc["commands"]:
            self.assertEqual("ok", c["status"])
            self.assertIn("median_s", c)
            self.assertIn("sd_s", c)

    def test_failing_command_is_reported(self):
        rc, out = self._main("--runs", "2",
                             runner=FakeRunner(fail="--full"))
        self.assertEqual(0, rc)
        full = [ln for ln in out.splitlines() if "gate --full" in ln][0]
        self.assertIn("FAILED exit 1: ERROR  RM001 boom", full)
        # A run that reached its verdict is still a timing.
        self.assertIn("median 0.500 s  sd 0.000 s", full)
        self.assertIn("import reqmap", out)

    def test_failing_command_in_markdown(self):
        target = self.root / "summary.md"
        env = dict(self.env, GITHUB_STEP_SUMMARY=str(target))
        self._main("--runs", "2", "--summary", env=env,
                   runner=FakeRunner(fail="--full"))
        text = target.read_text(encoding="utf-8")
        self.assertIn("| `gate --full --code ..` | 0.500 | 0.000 | "
                      "failed: exit 1: ERROR  RM001 boom |", text)

    def test_raising_command_is_reported(self):
        rc, out = self._main("--runs", "2", "--json",
                             runner=FakeRunner(raises="import reqmap"))
        self.assertEqual(0, rc)
        doc = json.loads(out)
        bad = [c for c in doc["commands"] if c["status"] == "failed"]
        self.assertEqual(["import reqmap"], [c["name"] for c in bad])
        self.assertIn("OSError", bad[0]["error"])
        self.assertEqual([], bad[0]["samples_s"])
        self.assertNotIn("median_s", bad[0])

    def test_unknown_commit(self):
        def no_git(argv, cwd):
            if argv[0] == "git":
                raise OSError("git not found")
            return subprocess.CompletedProcess(argv, 0, "", "")
        _, out = self._main("--runs", "1", runner=no_git)
        self.assertIn("commit: unknown", out)

    def test_summary_appends_markdown(self):
        target = self.root / "summary.md"
        target.write_text("before\n", encoding="utf-8")
        env = dict(self.env, GITHUB_STEP_SUMMARY=str(target))
        rc, _ = self._main("--runs", "2", "--summary", env=env)
        self.assertEqual(0, rc)
        text = target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("before\n"))
        self.assertIn("| command | median (s) | sd (s) | status |", text)
        self.assertIn("| `gate --code ..` | 0.500 | 0.000 | ok |", text)
        self.assertIn("commit `abc1234`", text)

    def test_summary_without_the_variable_writes_nothing(self):
        rc, _ = self._main("--runs", "1", "--summary", env={})
        self.assertEqual(0, rc)

    def test_exits_zero_even_when_everything_fails(self):
        rc, _ = self._main("--runs", "1", runner=FakeRunner(fail="utf8"))
        self.assertEqual(0, rc)

    def test_usage_error_exits_two(self):
        with redirect_stdout(io.StringIO()), \
                redirect_stderr(io.StringIO()), \
                self.assertRaises(SystemExit) as cm:
            CEP.main(["--runs", "0"], run=FakeRunner(), root=self.root,
                     env=self.env)
        self.assertEqual(2, cm.exception.code)

    def test_lines_fit_80_columns(self):
        for name in ("check_engine_perf.py", "test_check_engine_perf.py"):
            path = Path(__file__).resolve().parent / name
            for i, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), 1):
                self.assertLessEqual(len(line), 80, "{}:{}".format(name, i))


if __name__ == "__main__":
    unittest.main()
