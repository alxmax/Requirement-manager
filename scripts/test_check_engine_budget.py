#!/usr/bin/env python3
"""Tests for check_engine_budget.py — the release-time engine line budget (ADR-0046)."""
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_engine_budget as CEB


class EngineBudget(unittest.TestCase):
    def _run(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = CEB.main(list(argv))
        return rc, buf.getvalue()

    def test_the_count_is_what_wc_prints(self):
        # A tree with a file that does not end in a newline: wc -l counts newlines, not
        # lines, and so must this, or the CHANGELOG number and the gate's disagree.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "reqmap_engine").mkdir()
            (root / "reqmap.py").write_bytes(b"a\nb\n")
            (root / "reqmap_engine" / "x.py").write_bytes(b"c\n\n# d")
            (root / "reqmap_engine" / "notes.txt").write_bytes(b"not counted\n")
            self.assertEqual(4, CEB.engine_lines(root))

    def test_the_real_engine_is_within_its_budget(self):
        rc, out = self._run()
        self.assertEqual(0, rc, out)
        self.assertIn("budget", out)

    def test_one_line_under_the_count_fails(self):
        n = CEB.engine_lines()
        rc, out = self._run("--budget", str(n - 1))
        self.assertEqual(1, rc)
        self.assertIn("over the budget", out)
        rc, _ = self._run("--budget", str(n))
        self.assertEqual(0, rc)

    @unittest.skipIf(sys.platform == "win32", "wc is not on a bare Windows runner")
    def test_matches_wc(self):
        files = [str(p) for p in CEB.engine_files(CEB.ENGINE_DIR)]
        out = subprocess.run(["wc", "-l"] + files, stdout=subprocess.PIPE,
                             universal_newlines=True, check=True).stdout
        self.assertEqual(int(out.strip().splitlines()[-1].split()[0]), CEB.engine_lines())


if __name__ == "__main__":
    unittest.main()
