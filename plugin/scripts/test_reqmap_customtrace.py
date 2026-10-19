"""A repository's own trace convention (ADR-0077): `TRACE_TAGS`,
`TEST_FILE_PATTERNS` and `REQUIREMENT_SOURCES` in `_config.json`.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_customtrace`.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R
from test_reqmap_common import _write

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
FORM = r"\\trace\{([A-Z0-9_]+)\}"          # reads `\trace{AB_CD12}`
TEXT_SOURCE = {"glob": "modules/*/reqs/**/*.txt", "format": "text",
               "start": r"^([A-Z][A-Z0-9_]+):"}
HTML_SOURCE = {"glob": "specs/*.html", "format": "html",
               "start": r"^\s*([A-Z][A-Z0-9_]+)\s"}


def _run(cwd, *args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", ENGINE, *args], cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, encoding="utf-8", timeout=120)


def _tmp(test):
    d = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, d, True)
    return d


def _repo(test, config=None):
    """A repository written only in the invented `\\trace{ID}` convention:
    requirements as text in two module folders and as an HTML table, code,
    a `*Test.cpp` test, and one tag to an id nobody defines."""
    d = _tmp(test)
    os.makedirs(os.path.join(d, "requirements"))
    cfg = {"TRACE_TAGS": [{"pattern": FORM, "role": "auto"}],
           "TEST_FILE_PATTERNS": ["**/*Test.cpp"],
           "REQUIREMENT_SOURCES": [TEXT_SOURCE, HTML_SOURCE]}
    cfg.update(config or {})
    _write(os.path.join(d, "requirements", "_config.json"), json.dumps(cfg))
    _write(os.path.join(d, "modules", "brake", "reqs", "brake.txt"),
           "AB_CD12: The light turns on above 5 percent. It turns off when "
           "released.\n\nAB_CD13: A reading outside 0 to 100 turns it on.\n")
    _write(os.path.join(d, "modules", "door", "reqs", "sub", "door.txt"),
           "AB_DL01: The doors lock above 15 km/h.\n")
    _write(os.path.join(d, "specs", "spec.html"),
           "<html><body><table>\n<tr><td>AB_HT01</td><td>The horn sounds while "
           "the button is pressed.</td></tr>\n</table></body></html>\n")
    _write(os.path.join(d, "src", "brake.cpp"),
           "/// \\trace{AB_CD12}\nbool on(float p) { return p > 5.0f; }\n"
           "/// \\trace{AB_ZZ99}\nvoid stray() {}\n")
    _write(os.path.join(d, "src", "BrakeTests", "BrakeLightTest.cpp"),
           "/// \\trace{AB_CD12}\nTEST(BrakeLight, On) { EXPECT_TRUE(on(20.0f)); }\n")
    return d


def _patched(**values):
    return mock.patch.multiple(R.config, **values)


class CustomTags(unittest.TestCase):  # tested-by: REQ-CUSTOMTRACE-1110 @unit
    def test_a_configured_form_is_a_member(self):
        # verifies: REQ-CUSTOMTRACE-1110#CASE-1
        d = _tmp(self)
        fp = os.path.join(d, "src", "a.cpp")
        _write(fp, "/// \\trace{AB_CD12}\nint x;\n")
        with _patched(TRACE_TAGS=[{"pattern": FORM, "role": "implements"}]):
            self.assertEqual([["implements", "AB_CD12", 1]], R.tags._scan_file_tags(fp))

    def test_auto_follows_the_file(self):
        # verifies: REQ-CUSTOMTRACE-1110#CASE-2
        d = _tmp(self)
        code = os.path.join(d, "src", "a.cpp")
        test = os.path.join(d, "src", "ATest.cpp")
        for fp in (code, test):
            _write(fp, "/// \\trace{AB_CD12}\n")
        with _patched(TRACE_TAGS=[{"pattern": FORM, "role": "auto"}],
                      TEST_FILE_PATTERNS=["**/*Test.cpp"]):
            self.assertEqual("implements", R.tags._scan_file_tags(code)[0][0])
            self.assertEqual("tested-by", R.tags._scan_file_tags(test)[0][0])

    def test_a_configured_tag_to_no_requirement_is_dangling(self):
        # verifies: REQ-CUSTOMTRACE-1110#CASE-3
        out = _run(_repo(self), "gate").stdout
        self.assertIn("RM001", out)
        self.assertIn("AB_ZZ99", out)

    def test_a_bad_form_is_skipped(self):
        # verifies: REQ-CUSTOMTRACE-1110#CASE-4
        kept, problems = R.customtrace.validate_tags(
            [{"pattern": "trace", "role": "implements"},
             {"pattern": FORM, "role": "owns"}])
        self.assertEqual([], kept)
        self.assertEqual(2, len(problems))
        d = _tmp(self)
        fp = os.path.join(d, "a.py")
        _write(fp, "# " + "impl" + "ements: REQ-A-001\n")
        with _patched(TRACE_TAGS=kept):
            self.assertEqual("REQ-A-001", R.tags._scan_file_tags(fp)[0][1])


class TestFileGlobs(unittest.TestCase):  # tested-by: REQ-CUSTOMTRACE-1112 @unit
    def test_a_glob_makes_a_test_file(self):
        # verifies: REQ-CUSTOMTRACE-1112#CASE-1
        with _patched(TEST_FILE_PATTERNS=["**/*Test.cpp"]):
            self.assertTrue(R.tags._is_test_path("src/BrakeLightTest.cpp"))
            self.assertTrue(R.tags._is_test_path(
                os.path.join(os.sep, "repo", "src", "BrakeLightTest.cpp")))

    def test_the_convention_still_holds(self):
        # verifies: REQ-CUSTOMTRACE-1112#CASE-2
        with _patched(TEST_FILE_PATTERNS=["**/*Test.cpp"]):
            self.assertTrue(R.tags._is_test_path("tests/brake_light.cpp"))

    def test_without_the_glob_it_is_code(self):
        # verifies: REQ-CUSTOMTRACE-1112#CASE-3
        with _patched(TEST_FILE_PATTERNS=[]):
            self.assertFalse(R.tags._is_test_path("src/BrakeLightTest.cpp"))


class RequirementSources(unittest.TestCase):  # tested-by: REQ-CUSTOMTRACE-1113 @unit
    def _load(self, d, *sources):
        kept, problems = R.customtrace.validate_sources(list(sources))
        self.assertEqual([], problems)
        reqs = R.parse.RequirementIndex()
        with _patched(REQUIREMENT_SOURCES=kept):
            R.customtrace.load_sources(reqs, d)
        return reqs

    def test_text_in_two_module_folders_is_read(self):
        # verifies: REQ-CUSTOMTRACE-1113#CASE-1
        reqs = self._load(_repo(self), TEXT_SOURCE)
        self.assertEqual({"AB_CD12", "AB_CD13", "AB_DL01"}, set(reqs))
        self.assertTrue(reqs["AB_DL01"]["path"].endswith(
            os.path.join("door", "reqs", "sub", "door.txt")))
        clauses = R.sections._from_any(R.text._bullets, reqs["AB_CD12"]["body"],
                                       R.sections.CONTRACT_LABELS)
        self.assertEqual(2, len(clauses))

    def test_an_html_table_row_is_one_requirement(self):
        # verifies: REQ-CUSTOMTRACE-1113#CASE-2
        reqs = self._load(_repo(self), HTML_SOURCE)
        self.assertEqual(["AB_HT01"], list(reqs))
        self.assertIn("The horn sounds while the button is pressed.",
                      reqs["AB_HT01"]["body"])

    def test_a_text_requirement_is_not_held_to_the_markdown_format(self):
        # verifies: REQ-CUSTOMTRACE-1113#CASE-3
        out = _run(_repo(self), "gate", "--full").stdout
        for absent in ("missing-section", "RM014", "RM011"):
            self.assertNotIn(absent, out)
        self.assertIn("readability: 4 non-draft requirement(s) linted · 0 error(s) · "
                      "0 warning(s)", out)

    def test_a_source_that_matches_nothing_is_named(self):
        # verifies: REQ-CUSTOMTRACE-1113#CASE-4
        d = _repo(self, {"REQUIREMENT_SOURCES": [dict(TEXT_SOURCE, glob="nowhere/**/*.txt")]})
        out = _run(d, "gate").stdout
        self.assertIn("INPUT:requirements", out)
        self.assertIn("nowhere/**/*.txt", out)

    def test_generated_files_stay_put_and_a_source_is_not_untagged(self):
        # verifies: REQ-CUSTOMTRACE-1113#CASE-5
        d = _repo(self)
        _run(d, "sync")
        self.assertTrue(os.path.isfile(os.path.join(d, "requirements", "_reqlock.json")))
        for folder in ("modules", "specs"):
            for _root, _dirs, files in os.walk(os.path.join(d, folder)):
                self.assertFalse([f for f in files if f.startswith("_")])
        risk = _run(d, "gate", "--risk", "--all").stdout
        untagged = risk.split("Untagged files", 1)[1] if "Untagged files" in risk else ""
        self.assertNotIn("specs/spec.html", untagged)


class CustomTraceRepo(unittest.TestCase):  # tested-by: ARCH-CUSTOMTRACE-077 @integration
    def test_a_repository_in_its_own_convention_is_read(self):
        # verifies: ARCH-CUSTOMTRACE-077#CASE-1
        d = _repo(self)
        show = json.loads(_run(d, "gate", "--show", "AB_CD12", "--json").stdout)
        roles = {(m["role"], m["file"].replace("\\", "/")) for m in show["members"]}
        self.assertEqual({("implements", "src/brake.cpp"),
                          ("tested-by", "src/BrakeTests/BrakeLightTest.cpp")}, roles)
        self.assertIn("AB_ZZ99", _run(d, "gate").stdout)

    def test_no_config_no_change(self):
        # verifies: ARCH-CUSTOMTRACE-077#CASE-2
        d = _tmp(self)
        _write(os.path.join(d, "requirements", "REQ-A-001.md"),
               "---\nid: REQ-A-001\nstatus: draft\nlayer: feature\n---\n\n# T\n\n"
               "## Description\n- It holds.\n")
        probe = ("import sys, runpy; sys.argv = ['reqmap.py', 'sync']; "
                 "sys.path.insert(0, {!r});\n"
                 "try:\n    runpy.run_path({!r}, run_name='__main__')\n"
                 "except SystemExit:\n    pass\n"
                 "print('LOADED' if 'reqmap_engine.customtrace' in sys.modules "
                 "else 'NOT LOADED')").format(os.path.dirname(ENGINE), ENGINE)
        done = subprocess.run([sys.executable, "-X", "utf8", "-c", probe], cwd=d,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True, encoding="utf-8", timeout=120)
        self.assertIn("NOT LOADED", done.stdout, done.stderr)
        self.assertEqual(0, _run(d, "gate", "--full").returncode)

    def test_a_bad_entry_is_named_and_skipped(self):
        # verifies: ARCH-CUSTOMTRACE-077#CASE-3
        d = _repo(self, {"TRACE_TAGS": [{"pattern": "trace", "role": "auto"},
                                        {"pattern": FORM, "role": "auto"}]})
        out = _run(d, "gate").stdout
        self.assertIn("INPUT:config", out)
        self.assertIn("AB_ZZ99", out)              # the good entry still applies
        self.assertEqual(1, _run(d, "gate", "--strict").returncode)


if __name__ == "__main__":
    unittest.main(verbosity=2)
