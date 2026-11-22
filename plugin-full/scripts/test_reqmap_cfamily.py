"""C and C++ in an audit: which file is a test, what a code draft asks of a C
file, and a value a requirement states against the value its code defines.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_cfamily`.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R
from reqmap_engine import tracecover as _tracecover
R.tracecover = _tracecover
from test_reqmap_common import _ROLE, _spec, _write

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


class SpecValueReading(unittest.TestCase):  # tested-by: REQ-RULES-1143 @unit
    """The claim grammar and the definition reader, without a gate run."""

    def test_a_connector_makes_a_claim_and_prose_does_not(self):  # verifies: REQ-RULES-1143#CASE-3
        body = ("## Description\n> Why.\n\nEvery bullet below is binding.\n"
                "- `gate` retries 3 times, `MAX_RETRIES` is 3 and `MASK` (0x10).\n")
        claims = [(n, v) for n, v, _lit in R.specvalues.spec_claims(body)]
        self.assertEqual([("MAX_RETRIES", 3.0), ("MASK", 16.0)], claims)

    def test_definitions_compare_by_value(self):  # verifies: REQ-RULES-1143#CASE-2
        d = _repo(self)
        _write(os.path.join(d, "c.h"), "#define MASK 16u\n"
               "static const uint32_t TIMEOUT_MS = 1000UL;\nenum { LIMIT = 3, };\n")
        vals = {n: [v for v, _f, _l, _lit in R.specvalues.code_values(d, {"c.h"}, n)]
                for n in ("MASK", "TIMEOUT_MS", "LIMIT")}
        self.assertEqual({"MASK": [16.0], "TIMEOUT_MS": [1000.0], "LIMIT": [3.0]}, vals)


class TraceBlock(unittest.TestCase):  # tested-by: REQ-MAP-1144 @unit
    """The map's trace block: reach, tested-by suggestions, hygiene, rules."""

    def _ws(self, d, reqs, files):
        for rel, text in files.items():
            _write(os.path.join(d, rel), text)
        os.makedirs(os.path.join(d, "requirements"), exist_ok=True)
        members = R.scan_members(d, os.path.join(d, "requirements"))
        return R.tracecover, reqs, members

    def _req(self, rid, status="confirmed", clauses=("It does a thing.",)):
        body = "## Description\n> Why.\n\nEvery bullet below is binding.\n" + "".join(
            "- {}\n".format(c) for c in clauses)
        return {"meta": {"id": rid, "status": status, "layer": "feature"},
                "body": body, "path": rid + ".md"}

    def test_coverage_counts_files_tags_and_the_lock(self):  # verifies: REQ-MAP-1144#CASE-1
        d = _repo(self)
        tc, _r, members = self._ws(d, {}, {
            "src/a.c": CTAG + "R-1\nint a(void) { return 1; }\n",
            "src/b.c": "int b(void) { return 2; }\n",
            "tests/a_test.c": "int t(void) { return 0; }\n"})
        with open(os.path.join(d, "requirements", "_memberlock.json"), "w") as f:
            f.write('{"members": {"R-1": {"src/a.c#a": "x"}}}')
        cov = tc._coverage(tc._code_files(d, os.path.join(d, "requirements")),
                           members, os.path.join(d, "requirements"))
        self.assertEqual({"code_files": 3, "tagged_files": 1,
                          "production_files": 2, "drift_files": 1}, cov)

    def test_a_test_that_names_the_requirement_is_tier_a(self):  # verifies: REQ-MAP-1144#CASE-2
        d = _repo(self)
        reqs = {rid: self._req(rid) for rid in ("R-1", "R-2", "R-3")}
        tc, reqs, members = self._ws(d, reqs, {
            "src/brake.c": CTAG + "R-1\nint brake(void) { return 1; }\n",
            "src/pedal.c": CTAG + "R-2\nint pedal(void) { return 1; }\n",
            "src/horn.c": CTAG + "R-3\nint horn(void) { return 1; }\n",
            "tests/brake_test.c": "/* R-1 */ void t(void) {}\n",
            "tests/pedal_test.c": "void t(void) {}\n"})
        rd = os.path.join(d, "requirements")
        s = tc._suggestions(reqs, members, tc._code_files(d, rd), d, rd)
        self.assertEqual({"tier": "A", "tests": ["tests/brake_test.c"]}, s["R-1"])
        self.assertEqual({"tier": "B", "tests": ["tests/pedal_test.c"]}, s["R-2"])
        self.assertEqual({"tier": "C", "tests": []}, s["R-3"])

    def test_duplicates_and_empty_confirmed_are_listed(self):  # verifies: REQ-MAP-1144#CASE-3
        reqs = {"R-1": self._req("R-1"), "R-2": self._req("R-2"),
                "R-3": self._req("R-3", clauses=())}
        h = R.tracecover._hygiene(reqs)
        self.assertEqual([["R-1", "R-2"]], h["duplicates"])
        self.assertEqual(["R-3"], h["title_only_confirmed"])

    def test_a_design_rule_counts_production_code_only(self):  # verifies: REQ-MAP-1144#CASE-4
        d = _repo(self)
        for rel, text in {"src/a.cpp": "// throw here\nvoid f() {\n  throw 1;\n}\n",
                          "tests/a_test.cpp": "void t() { throw 2; }\n"}.items():
            _write(os.path.join(d, rel), text)
        old = R.config.DESIGN_RULES
        R.config.DESIGN_RULES = [{"id": "no-exceptions", "pattern": r"\bthrow\b",
                                  "why": "no exceptions"}]
        self.addCleanup(setattr, R.config, "DESIGN_RULES", old)
        rules, problems = R.tracecover._rules(R.tracecover._code_files(d, None))
        self.assertEqual([], problems)
        self.assertEqual(1, rules[0]["count"])
        self.assertEqual({"file": "src/a.cpp", "line": 3}, rules[0]["hits"][0])

    def test_coverage_skips_prose_and_ignored_files(self):  # verifies: REQ-MAP-1144#CASE-5
        if not shutil.which("git"):
            self.skipTest("git is not installed")
        d = _repo(self)
        for rel, text in {"src/a.c": "int a(void) { return 1; }\n",
                          "src/local.c": "int l(void) { return 2; }\n",
                          "docs/notes.md": "# Notes\n",
                          "docs/page.html": "<p>page</p>\n"}.items():
            _write(os.path.join(d, rel), text)
        subprocess.run(["git", "-C", d, "init", "-q"], check=True)
        _write(os.path.join(d, ".git", "info", "exclude"), "/src/local.c\n")
        files = R.tracecover._code_files(d, None)
        self.assertEqual(["src/a.c"], [rel.replace(os.sep, "/") for _a, rel, _t in files])



class CppTestsThatCannotFail(unittest.TestCase):  # tested-by: REQ-TESTGAPS-1147
    """GoogleTest, Catch2, CppUTest and Unity tests that cannot fail."""
    TAG = "// " + "verif" + "ies: "  # spelled apart so this file's scan sees no tag

    def _read(self, src, fp="t_test.cpp"):
        from reqmap_engine.vacuouscpp import cpp_vacuous
        tags = [(i, c) for i, line in enumerate(src.split("\n"), 1)
                for c in re.findall(r"ies: (\S+#CASE-\d+)", line)]
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, fp), src)
            found = cpp_vacuous(d, fp, tags)
        return [(v["test"], v["kind"], v["line"]) for v in found]

    def test_a_test_with_no_assertion_is_named(self):  # verifies: REQ-TESTGAPS-1147#CASE-1
        src = ("#include <gtest/gtest.h>\n"
               + self.TAG + "REQ-A-001#CASE-1\n"
               "TEST(Suite, Runs) {\n  run(1);\n}\n")
        self.assertEqual([("TEST(Suite, Runs)", "no assertion", 3)], self._read(src))

    def test_a_constant_or_a_self_comparison_is_named(self):  # verifies: REQ-TESTGAPS-1147#CASE-2
        src = ("TEST(S, Const) {  " + self.TAG + "REQ-A-001#CASE-1\n  EXPECT_TRUE(true);\n}\n"
               "TEST_F(F, Same) {  " + self.TAG + "REQ-A-001#CASE-2\n"
               "  EXPECT_EQ(f(1), f(1));\n}\n"
               "TEST(S, Real) {  " + self.TAG + "REQ-A-001#CASE-3\n  EXPECT_EQ(f(1), 3);\n}\n")
        self.assertEqual([("TEST(S, Const)", "constant assertion", 1),
                          ("TEST_F(F, Same)", "compares a value with itself", 4)],
                         self._read(src))

    def test_a_helper_or_a_string_does_not_mislead_it(self):  # verifies: REQ-TESTGAPS-1147#CASE-3
        src = ("static void expect_three(int x) { EXPECT_EQ(x, 3); }\n"
               "TEST(S, Helper) { expect_three(f()); }  " + self.TAG + "REQ-A-001#CASE-1\n"
               "TEST(S, Lib) { check_frame(f()); }  " + self.TAG + "REQ-A-001#CASE-2\n"
               "TEST(S, Str) {  " + self.TAG + "REQ-A-001#CASE-3\n"
               "  EXPECT_STREQ(name(), \"a(b\");\n}\n"
               "void helper_main(void) { run(); }  " + self.TAG + "REQ-A-001#CASE-4\n")
        self.assertEqual([], self._read(src))

    def test_a_unity_test_reaches_the_worklist(self):  # verifies: REQ-TESTGAPS-1147#CASE-4
        src = ("#include \"unity.h\"\n"
               "void test_x(void) {  " + self.TAG + "REQ-A-001#CASE-1\n"
               "  TEST_ASSERT_EQUAL(f(), f());\n}\n")
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"),
                   _spec("REQ-A-001", ["A works."]))
            _write(os.path.join(d, "test_a.c"), src)
            ws = R.Workspace.load(rd, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_next(ws)
        self.assertIn("Tests that cannot fail (1)", buf.getvalue())
        self.assertIn("test_a.c:2   void test_x(void)   compares a value with itself",
                      buf.getvalue())

    def test_unbalanced_braces_are_skipped(self):  # verifies: REQ-TESTGAPS-1147#CASE-5
        src = "TEST(S, Broken) {  " + self.TAG + "REQ-A-001#CASE-1\n  run(1);\n"
        self.assertEqual([], self._read(src))


if __name__ == "__main__":
    unittest.main()
