#!/usr/bin/env python3
"""Tests for check_engine_budget.py — the release-time core budget, in
logical lines over the derived core (ADR-0046, ADR-0053)."""
import ast
import io
import os
import re
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
        # A file that does not end in a newline: wc -l counts newlines, not
        # lines, and so must this, or the CHANGELOG number and it disagree.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "reqmap_engine").mkdir()
            (root / "reqmap.py").write_bytes(b"a\nb\n")
            (root / "reqmap_engine" / "x.py").write_bytes(b"c\n\n# d")
            (root / "reqmap_engine" / "notes.txt").write_bytes(b"not\n")
            self.assertEqual(4, CEB.engine_lines(root))

    def test_one_line_under_the_count_fails(self):
        # tested-by: ARCH-SELFGATE-039 @integration
        n = CEB.core_logical_lines()
        rc, out = self._run("--budget", str(n - 1))
        self.assertEqual(1, rc)
        self.assertTrue(out.startswith("FAIL  core is "), out)
        rc, out = self._run("--budget", str(n))
        self.assertEqual(0, rc)
        self.assertTrue(out.startswith("OK  core is "), out)

    def test_the_real_core_is_within_its_budget(self):
        rc, out = self._run()
        self.assertEqual(0, rc, out)
        self.assertIn("budget {:,}".format(CEB.CORE_LOGICAL_BUDGET), out)

    def test_the_physical_total_is_judged_against_its_ceiling(self):
        total = CEB.engine_lines()
        files = len(CEB.engine_files(CEB.ENGINE_DIR))
        rc, out = self._run("--ceiling", str(total - 1))
        self.assertEqual(1, rc)
        self.assertEqual(
            "FAIL  total is {:,} physical lines in {} files, ceiling {:,}"
            .format(total, files, total - 1),
            out.strip().splitlines()[-1])
        rc, out = self._run("--ceiling", str(total))
        self.assertEqual(0, rc, out)

    def test_the_real_total_is_under_its_ceiling(self):
        self.assertLessEqual(CEB.engine_lines(), CEB.TOTAL_LINE_CEILING)

    @unittest.skipIf(sys.platform == "win32",
                     "wc is not on a bare Windows runner")
    def test_matches_wc(self):
        files = [str(p) for p in CEB.engine_files(CEB.ENGINE_DIR)]
        out = subprocess.run(["wc", "-l"] + files, stdout=subprocess.PIPE,
                             universal_newlines=True, check=True).stdout
        self.assertEqual(int(out.strip().splitlines()[-1].split()[0]),
                         CEB.engine_lines())

    def test_the_core_is_derived_not_listed(self):
        # No module the gate is known to need may be named in the script:
        # the list comes out of sys.modules at run time, or it rots.
        src = Path(CEB.__file__).read_text(encoding="utf-8")
        strings = [n.value for n in ast.walk(ast.parse(src))
                   if isinstance(n, ast.Constant)
                   and isinstance(n.value, str)]
        named = re.compile(r"\b(?:reqmap_engine\.)(?:gate|scan|rules)\b"
                           r"|\b(?:gate|scan|rules)\.py\b")
        for s in strings:
            self.assertNotIn(s, ("gate", "scan", "rules"))
            self.assertIsNone(named.search(s), s)
        core = CEB.core_modules()
        self.assertEqual(sorted(core), core)
        for name in ("gate", "scan", "rules"):
            self.assertIn("reqmap_engine." + name, core)
        self.assertTrue(all(p.is_file() for p in CEB.core_files()))

    def test_formatting_does_not_move_the_logical_count(self):
        flat = "total = combine(first_value, second_value, third_value)\n"
        wrapped = ("total = combine(\n"
                   "    first_value, second_value,\n"
                   "    third_value)\n"
                   "\n"
                   "# a comment explains nothing the count can see\n")
        self.assertEqual(1, CEB.logical_lines(flat))
        self.assertEqual(CEB.logical_lines(flat),
                         CEB.logical_lines(wrapped))


if __name__ == "__main__":
    unittest.main()
