"""Regression tests for check/engine_staleness.py — the CI-side staleness probe.

Stdlib unittest, run from the repo root:
    python -X utf8 scripts/test_engine_staleness.py
Writes throwaway `reqmap.py` files into a tempdir; the real engine is never read.
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "check"))
import engine_staleness as ES


def _engine(path, version):
    """Write a stand-in reqmap.py carrying `version` (None: no version line at all)."""
    body = "" if version is None else 'MAP_ENGINE_VERSION = "{}"\n'.format(version)
    Path(path).write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    return str(path)


class StalenessProbe(unittest.TestCase):  # tested-by: REQ-STALEENGINE-925  # tested-by: REQ-STALEENGINE-926
    def _run(self, vendored, reference, mode="warn", in_actions=False):
        """Run the probe, returning (exit_code, stdout)."""
        saved = os.environ.get("GITHUB_ACTIONS")
        if in_actions:
            os.environ["GITHUB_ACTIONS"] = "true"
        else:
            os.environ.pop("GITHUB_ACTIONS", None)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = ES.main(["--vendored", vendored, "--reference", reference, "--mode", mode])
        finally:
            if saved is None:
                os.environ.pop("GITHUB_ACTIONS", None)
            else:
                os.environ["GITHUB_ACTIONS"] = saved
        return code, buf.getvalue()

    def _pair(self, d, vendored_ver, reference_ver):
        return (_engine(Path(d) / "vendored.py", vendored_ver),
                _engine(Path(d) / "reference.py", reference_ver))

    def test_stale_warns_and_exits_zero(self):  # tested-by: ARCH-STALEENGINE-043  # verifies: REQ-STALEENGINE-925#CASE-1
        """AC-1: the motivating case — an old vendored engine, named, without failing."""
        with tempfile.TemporaryDirectory() as d:
            v, r = self._pair(d, "2025-08-02", "2026-08-20.2")
            code, out = self._run(v, r, mode="warn")
            self.assertEqual(code, 0)
            self.assertIn("2025-08-02", out)
            self.assertIn("2026-08-20.2", out)
            self.assertIn("stale", out.lower())

    def test_stale_error_mode_exits_one(self):  # verifies: REQ-STALEENGINE-925#CASE-6
        """AC-2."""
        with tempfile.TemporaryDirectory() as d:
            v, r = self._pair(d, "2025-08-02", "2026-08-20.2")
            code, out = self._run(v, r, mode="error")
            self.assertEqual(code, 1)
            self.assertIn("stale", out.lower())

    def test_off_mode_is_silent(self):  # verifies: REQ-STALEENGINE-926#CASE-1
        """AC-3."""
        with tempfile.TemporaryDirectory() as d:
            v, r = self._pair(d, "2025-08-02", "2026-08-20.2")
            code, out = self._run(v, r, mode="off")
            self.assertEqual(code, 0)
            self.assertEqual(out, "")

    def test_current_or_ahead_never_warns(self):  # verifies: REQ-STALEENGINE-926#CASE-2
        """AC-4: equal, and a vendored engine ahead of the pinned action's."""
        for vendored, reference in [("2026-08-20.2", "2026-08-20.2"),
                                    ("2026-08-20.2", "2026-08-20"),
                                    ("2026-09-01", "2026-08-20.2")]:
            for mode in ("warn", "error"):
                with tempfile.TemporaryDirectory() as d:
                    v, r = self._pair(d, vendored, reference)
                    code, out = self._run(v, r, mode=mode)
                    self.assertEqual(code, 0, (vendored, reference, mode))
                    self.assertNotIn("stale", out.lower(), (vendored, reference, mode))

    def test_same_day_suffix_orders_numerically(self):
        """`.10` is newer than `.9` — a string compare gets that backwards."""
        with tempfile.TemporaryDirectory() as d:
            v, r = self._pair(d, "2026-08-20.9", "2026-08-20.10")
            code, out = self._run(v, r, mode="warn")
            self.assertEqual(code, 0)
            self.assertIn("stale", out.lower())

    def test_unreadable_version_is_a_skip_not_a_failure(self):  # verifies: REQ-STALEENGINE-926#CASE-3
        """AC-5: fail open. An unreadable version is not evidence of staleness, so even
        `error` mode must not turn it into a red build."""
        with tempfile.TemporaryDirectory() as d:
            missing = str(Path(d) / "absent.py")
            for vendored, reference in [(_engine(Path(d) / "v.py", None),
                                         _engine(Path(d) / "r.py", "2026-08-20.2")),
                                        (_engine(Path(d) / "v2.py", "2025-08-02"), missing),
                                        (missing, missing)]:
                code, out = self._run(vendored, reference, mode="error")
                self.assertEqual(code, 0, (vendored, reference))
                self.assertIn("skipped", out.lower(), (vendored, reference))

    def test_internal_failure_is_a_skip_not_a_failure(self):  # verifies: REQ-STALEENGINE-926#CASE-4
        """AC-5, second half: whatever goes wrong inside the probe, the gate run it is
        attached to must not go red because of it."""
        with tempfile.TemporaryDirectory() as d:
            v, r = self._pair(d, "2025-08-02", "2026-08-20.2")
            saved = ES.version_at
            ES.version_at = lambda path: 1 / 0
            try:
                code, out = self._run(v, r, mode="error")
            finally:
                ES.version_at = saved
            self.assertEqual(code, 0)
            self.assertIn("skipped", out.lower())

    def test_annotation_only_under_github_actions(self):  # verifies: REQ-STALEENGINE-925#CASE-7
        """AC-6: the workflow-annotation syntax is noise in a local terminal."""
        with tempfile.TemporaryDirectory() as d:
            v, r = self._pair(d, "2025-08-02", "2026-08-20.2")
            _, in_ci = self._run(v, r, mode="warn", in_actions=True)
            _, local = self._run(v, r, mode="warn", in_actions=False)
            self.assertTrue(in_ci.startswith("::warning"), in_ci)
            self.assertNotIn("::warning", local)
            self.assertIn("WARN", local)

    def test_reference_defaults_to_the_shipped_engine(self):
        """With no --reference, the probe reads the engine sitting beside the action —
        the whole reason it can answer at all."""
        with tempfile.TemporaryDirectory() as d:
            v = _engine(Path(d) / "vendored.py", "2000-01-01")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = ES.main(["--vendored", v, "--mode", "warn"])
            self.assertEqual(code, 0)
            self.assertIn("stale", buf.getvalue().lower())
            self.assertIn(ES.reference_version() or "", buf.getvalue())

    def test_invalid_mode_is_a_usage_error(self):
        """A typo in the action input must be loud, not silently treated as 'warn'."""
        with tempfile.TemporaryDirectory() as d:
            v, r = self._pair(d, "2025-08-02", "2026-08-20.2")
            with self.assertRaises(SystemExit) as cm:
                with redirect_stdout(io.StringIO()):
                    ES.main(["--vendored", v, "--reference", r, "--mode", "warning"])
            self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
