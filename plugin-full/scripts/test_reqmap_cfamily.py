"""C and C++ in an audit: which file is a test, what a code draft asks of a C
file, and a value a requirement states against the value its code defines.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_cfamily`.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R
from test_reqmap_common import _ROLE, _write

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
CTAG = "// " + _ROLE + ": "


def _repo(test):
    d = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, d, True)
    return d


class CppTestFiles(unittest.TestCase):  # tested-by: REQ-CANDIDATES-1141 @unit
    """A C/C++ test is known by GoogleTest's file names or by the framework
    it includes; a CamelCase `*Test` name alone is not enough."""

    def test_the_c_and_cpp_names_mark_a_test(self):  # verifies: REQ-CANDIDATES-1141#CASE-1
        for rel in ("src/brake_test.cc", "src/brake_unittest.cpp",
                    "src/brake_tests.c", "UnitTests/brake.cpp",
                    "unit_tests/brake.c"):
            self.assertTrue(R.tags._is_test_path(rel), rel)
        self.assertFalse(R.tags._is_test_path("src/RamTest.c"))

    def test_an_included_framework_marks_a_test(self):  # verifies: REQ-CANDIDATES-1141#CASE-2
        d = _repo(self)
        for name, head in (("BrakeTest.cpp", "#include <gtest/gtest.h>"),
                           ("BrakeSpec.cpp", '#include "CppUTest/TestHarness.h"'),
                           ("brake_check.c", '#include "unity.h"'),
                           ("RamTest.c", '#include "ram.h"')):
            _write(os.path.join(d, "src", name), head + "\nvoid f(void) {}\n")
        test = lambda n: R.tags._is_test_path(           # noqa: E731
            "src/" + n, os.path.join(d, "src", n))
        self.assertTrue(test("BrakeTest.cpp"))
        self.assertTrue(test("BrakeSpec.cpp"))
        self.assertTrue(test("brake_check.c"))
        self.assertFalse(test("RamTest.c"))        # a production self-test

    def test_a_test_is_paired_with_the_code_it_tests(self):  # verifies: REQ-CANDIDATES-1141#CASE-3
        d = _repo(self)
        _write(os.path.join(d, "BrakeTest.cpp"), "#include <gtest/gtest.h>\n")
        _write(os.path.join(d, "RamTest.c"), '#include "ram.h"\n')
        files = ["brake.cpp", "BrakeTest.cpp", "pedal.c", "pedal_test.cc",
                 "Ram.c", "RamTest.c"]
        idx = R.candidates._test_by_stem_index(files, d)
        self.assertEqual(["BrakeTest.cpp"], idx.get("Brake"))
        self.assertEqual(["pedal_test.cc"], idx.get("pedal"))
        self.assertNotIn("Ram", idx)


class CDraftQuestions(unittest.TestCase):  # tested-by: REQ-EXTRACT-1142 @unit
    """A code draft of a C/C++ file asks about the line each signal is on."""

    SRC = ("#define LIMIT 100\n"
           "static int check(int v) {\n"
           "    if (v > 250) {\n"
           "        return 1;\n"
           "    }\n"
           "    if (v == 0) return 0;\n"
           "    if (v < LIMIT)\n"
           "        return 2;\n"
           "    (void)log_event(v);\n"
           "    return 3;\n"
           "    v++;\n"
           "}\n"
           "int other(int x) {\n"
           "    switch (x) {\n"
           "    case 3: return 4;\n"
           "    default: break;\n"
           "    }\n"
           "    return 0;\n"
           "}\n")

    def test_each_signal_names_its_line(self):  # verifies: REQ-EXTRACT-1142#CASE-1
        asks, more, partial = R.draftquestions.draft_questions("src/c.c", self.SRC)
        self.assertEqual("", partial)
        self.assertTrue(any("c.c:3" in a and "unnamed number" in a for a in asks))
        self.assertTrue(any("c.c:9" in a and "discards a return value" in a
                            for a in asks))
        self.assertTrue(any("c.c:11" in a and "can never run" in a for a in asks))

    def test_a_guarded_exit_and_a_plain_number_ask_nothing(self):  # verifies: REQ-EXTRACT-1142#CASE-2
        asks, _more, _partial = R.draftquestions.draft_questions("src/c.c", self.SRC)
        lines = {a.split("`")[1].split(":")[1] for a in asks}
        self.assertEqual({"3", "9", "11"}, lines)   # not 6, 8, 15, 16

    def test_unbalanced_braces_are_reported_as_not_read(self):  # verifies: REQ-EXTRACT-1142#CASE-3
        asks, _more, partial = R.draftquestions.draft_questions(
            "src/bad.c", "int f() {\n  if (x > 250) return 1;\n")
        self.assertEqual([], asks)
        self.assertIn("braces do not balance", partial[1])


class SpecValueAgainstCode(unittest.TestCase):  # tested-by: REQ-RULES-1143 @integration
    """RM038: a value a clause gives a named constant, against its code."""

    REQ = ("---\nid: CFG-001\nstatus: draft\nlayer: feature\n---\n\n"
           "# Retries\n\n## Description\n> Why.\n\nEvery bullet below is binding.\n"
           "{clauses}\n## Cases\nCASE-1 — it retries\n  Given  a\n  When   b\n"
           "  Then   c\n")

    def _gate(self, d, clauses, code, extra=None):
        _write(os.path.join(d, "reqs", "CFG-001.md"),
               self.REQ.format(clauses=clauses))
        _write(os.path.join(d, "src", "cfg.h"), CTAG + "CFG-001\n" + code)
        for name, text in (extra or {}).items():
            _write(os.path.join(d, "src", name), text)
        def run(*args):
            return subprocess.run(
                [sys.executable, "-X", "utf8", ENGINE, "--root", d, "--reqs",
                 os.path.join(d, "reqs"), "--code", d, "gate", *args], cwd=d,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, encoding="utf-8", timeout=120).stdout
        return run("--full"), run()

    def test_a_different_value_is_reported_with_both_sides(self):  # verifies: REQ-RULES-1143#CASE-1
        full, _bare = self._gate(_repo(self), "- `MAX_RETRIES` is 3 per request.\n",
                                 "#define MAX_RETRIES 5U\n")
        self.assertIn("RM038 CFG-001", full)
        self.assertIn("`MAX_RETRIES` 3", full)
        self.assertIn("src/cfg.h:2 defines 5", full)

    def test_the_same_value_written_otherwise_is_not(self):  # verifies: REQ-RULES-1143#CASE-2
        full, _bare = self._gate(
            _repo(self),
            "- `MASK` is 0x10.\n- `TIMEOUT_MS` = 1,000.\n- `SCALE` (2.5).\n",
            "#define MASK 16u\nstatic const uint32_t TIMEOUT_MS = 1000UL;\n"
            "constexpr float SCALE{2.5f};\n")
        self.assertNotIn("RM038", full)

    def test_prose_and_files_of_other_requirements_are_not_read(self):  # verifies: REQ-RULES-1143#CASE-3
        full, _bare = self._gate(
            _repo(self), "- `gate` retries 3 times, `MAX_RETRIES` is 3.\n",
            "#define MAX_RETRIES 3\n",
            extra={"other.h": "#define MAX_RETRIES 9\n#define gate 4\n"})
        self.assertNotIn("RM038", full)

    def test_the_bare_gate_does_not_run_it(self):  # verifies: REQ-RULES-1143#CASE-4
        _full, bare = self._gate(_repo(self), "- `MAX_RETRIES` is 3.\n",
                                 "#define MAX_RETRIES 5\n")
        self.assertNotIn("RM038", bare)


if __name__ == "__main__":
    unittest.main()
