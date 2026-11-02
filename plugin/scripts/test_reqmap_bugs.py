"""Known bugs by module (ADR-0080): the file format, the map, the gate,
`sync --bug` and `ask --bugs`.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_bugs`.
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
from reqmap_engine import bugs as B
from test_reqmap_common import _spec, _write, tag, tb_tag

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
HEAD = "| ID | Bug | Priority | Date | Where | Why it matters | Source |\n" \
       "|---|---|---|---|---|---|---|\n"
FIXTURE = os.path.join(os.path.dirname(ENGINE), "..", "..", "app", "scripts",
                       "smoke", "bugfile.fixture.json")


def _run(cwd, *args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", ENGINE, *args], cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, encoding="utf-8", timeout=120)


def _repo(test):
    d = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, d, True)
    rid = "BUG-THING-001"
    _write(os.path.join(d, "requirements", rid + ".md"),
           _spec(rid, ["`f` returns 1."], status="confirmed"))
    _write(os.path.join(d, "a.py"), tag(rid) + "\nx = 1\n")
    _write(os.path.join(d, "test_a.py"),
           tb_tag(rid) + "\ndef test_ok():\n    assert True\n")
    return d


def _bug_file(d, name, text):
    path = os.path.join(d, "requirements", "bugs", name)
    _write(path, text)
    return path


def _read(d, path, problems=None):
    out = [] if problems is None else problems
    return B._read_file(path, d, out)


def _map(d):
    with open(os.path.join(d, "requirements", "_map.json"),
              encoding="utf-8") as f:
        return json.load(f)


def _bytes(path):
    with open(path, "rb") as f:
        return f.read()


class BugFile(unittest.TestCase):  # tested-by: REQ-BUGS-1116 @unit
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, True)

    def test_a_canonical_file_reads_back_whole(self):
        # verifies: REQ-BUGS-1116#CASE-1
        path = _bug_file(self.d, "Payments.md", "# Bugs — Payments\n\n" + HEAD
                         + "| B1 | Refund twice | P1 | 2026-11-02 | `p.py:3` "
                           "| Money | ticket |\n")
        got = _read(self.d, path)[0]
        self.assertEqual(
            ("Payments:B1", "B1", "Payments", "Refund twice", "P1",
             "2026-11-02", "`p.py:3`", "Money", "ticket", False),
            (got["id"], got["ref"], got["module"], got["title"], got["prio"],
             got["date"], got["where"], got["why"], got["source"],
             got["estimated"]))

    def test_a_repository_names_its_own_columns(self):
        # verifies: REQ-BUGS-1116#CASE-2
        own = _bug_file(self.d, "own.md", "# Own\n\n| # | Issue | Sev |\n"
                        "|---|---|---|\n| 1 | Broken | P3 |\n")
        std = _bug_file(self.d, "std.md", "# Std\n\n" + HEAD
                        + "| B1 | Fine | P2 | | | | |\n")
        with mock.patch.dict(R.config.BUG_COLUMNS,
                             {"title": ["Issue"], "prio": ["Sev"]}):
            self.assertEqual("Broken", _read(self.d, own)[0]["title"])
            self.assertEqual("Fine", _read(self.d, std)[0]["title"])

    def test_the_heading_gives_module_and_date(self):
        # verifies: REQ-BUGS-1116#CASE-3
        path = _bug_file(self.d, "b.md",
                         "# Known issues — Billing (15.03.2026)\n\n"
                         "| ID | Bug | Priority |\n|---|---|---|\n"
                         "| B1 | Late | P2 |\n")
        got = _read(self.d, path)[0]
        self.assertEqual(("Billing", "2026-03-15"), (got["module"], got["date"]))

    def test_another_table_is_not_a_bug_table(self):
        # verifies: REQ-BUGS-1116#CASE-4
        path = _bug_file(self.d, "c.md", "# Contents\n\n| # | Module | P0 |\n"
                         "|---|---|---|\n| 01 | Core | 2 |\n\n" + HEAD
                         + "| B1 | Real | P2 | | | | |\n")
        problems = []
        self.assertEqual(["Real"], [b["title"] for b in
                                    _read(self.d, path, problems)])
        self.assertEqual([], problems)

    def test_a_bad_row_does_not_cost_the_others(self):
        # verifies: REQ-BUGS-1116#CASE-5
        path = _bug_file(self.d, "d.md", "# Bad\n\n" + HEAD
                         + "| B1 | No priority | high | | | | |\n"
                           "| B2 | Good | P2 | 2026-11-02 | | | |\n"
                           "| B2 | Again | P2 | | | | |\n"
                           "| B3 | Wrong day | P2 | 31.13.2026 | | | |\n")
        problems = []
        titles = [b["title"] for b in _read(self.d, path, problems)]
        self.assertEqual(["Good", "Wrong day"], titles)
        self.assertEqual(3, len(problems))
        self.assertTrue(all(p.startswith("requirements/bugs/d.md:")
                            for p in problems))

    def test_an_estimated_priority_is_kept_apart(self):
        # verifies: REQ-BUGS-1116#CASE-6
        path = _bug_file(self.d, "e.md", "# E\n\n" + HEAD
                         + "| B2* | Maybe | P3 | | | | |\n"
                           "| B3 | Mixed | P2 (audit), P1 | | | | |\n")
        first, second = _read(self.d, path)
        self.assertEqual(("B2", True, "P2", False),
                         (first["ref"], first["estimated"], second["prio"],
                          second["estimated"]))


class BugsOnTheMap(unittest.TestCase):  # tested-by: REQ-BUGS-1117 @integration
    def test_the_folder_reaches_the_map(self):
        # verifies: REQ-BUGS-1117#CASE-1
        d = _repo(self)
        _bug_file(d, "Core.md", "# Bugs — Core\n\n" + HEAD
                  + "| B1 | Crash | P1 | 2026-11-02 | | | |\n")
        self.assertEqual(0, _run(d, "sync").returncode)
        self.assertEqual(["Core:B1"], [b["id"] for b in _map(d)["bugs"]])
        self.assertEqual(0, _run(d, "gate", "--full").returncode)

    def test_no_list_no_key_no_module(self):
        # verifies: REQ-BUGS-1117#CASE-2
        d = _repo(self)
        self.assertEqual(0, _run(d, "sync").returncode)
        self.assertNotIn("bugs", _map(d))
        code = ("import sys; sys.path.insert(0, {!r}); sys.argv = ['r', 'sync'];"
                " import reqmap; reqmap.main();"
                " print('LOADED' if 'reqmap_engine.bugs' in sys.modules "
                "else 'CLEAN')").format(os.path.dirname(ENGINE))
        out = subprocess.run([sys.executable, "-X", "utf8", "-c", code], cwd=d,
                             stdout=subprocess.PIPE, universal_newlines=True,
                             encoding="utf-8", timeout=120).stdout
        self.assertIn("CLEAN", out)

    def test_a_declared_source_is_read_and_not_written(self):
        # verifies: REQ-BUGS-1117#CASE-3
        # verifies: ARCH-BUGS-078#CASE-2
        d = _repo(self)
        doc = os.path.join(d, "notes", "issues.md")
        _write(doc, "# Known — Billing (2026-03-15)\n\n| # | Issue | Sev |\n"
                    "|---|---|---|\n| 1 | Late | P2 |\n")
        _write(os.path.join(d, "requirements", "_config.json"), json.dumps({
            "BUG_SOURCES": ["notes/*.md"],
            "BUG_COLUMNS": {"title": ["Issue"], "prio": ["Sev"]}}))
        before = _bytes(doc)
        self.assertEqual(0, _run(d, "sync").returncode)
        got = _map(d)["bugs"]
        self.assertEqual([("Billing", "Late")],
                         [(b["module"], b["title"]) for b in got])
        self.assertEqual(before, _bytes(doc))

    def test_a_pattern_that_matches_nothing_is_named(self):
        # verifies: REQ-BUGS-1117#CASE-4
        d = _repo(self)
        with mock.patch.object(R.config, "BUG_SOURCES", ["nope/*.md"]):
            self.assertIn("nope/*.md",
                          B.load_bugs(d, os.path.join(d, "requirements"))[1][0])

    def test_a_changed_bug_file_makes_the_map_stale(self):
        # verifies: REQ-BUGS-1117#CASE-5
        d = _repo(self)
        path = _bug_file(d, "Core.md", "# Bugs — Core\n\n" + HEAD
                         + "| B1 | Crash | P1 | | | | |\n")
        self.assertEqual(0, _run(d, "sync").returncode)
        with open(path, "a", encoding="utf-8") as f:
            f.write("| B2 | Another | P2 | | | | |\n")
        self.assertNotEqual(0, _run(d, "gate", "--full").returncode)

    def test_a_bug_from_the_command_line_reaches_the_map(self):
        # verifies: ARCH-BUGS-078#CASE-1
        d = _repo(self)
        self.assertEqual(0, _run(d, "sync", "--bug", "Crash", "--module",
                                 "Core", "--date", "2026-11-02").returncode)
        self.assertEqual(0, _run(d, "sync").returncode)
        got = _map(d)["bugs"][0]
        self.assertEqual(("Crash", "Core", "2026-11-02"),
                         (got["title"], got["module"], got["date"]))

    def test_no_list_changes_nothing(self):
        # verifies: ARCH-BUGS-078#CASE-3
        d = _repo(self)
        self.assertEqual(0, _run(d, "sync").returncode)
        self.assertNotIn("bugs", _map(d))


class BugsAtTheGate(unittest.TestCase):  # tested-by: REQ-BUGS-1118 @integration
    def _synced(self, row):
        d = _repo(self)
        self.assertEqual(0, _run(d, "sync").returncode)
        _bug_file(d, "Core.md", "# Bugs — Core\n\n" + HEAD + row)
        self.assertEqual(0, _run(d, "sync").returncode)
        return d

    def test_a_p0_does_not_fail_the_gate(self):
        # verifies: REQ-BUGS-1118#CASE-1
        d = self._synced("| B1 | Everything is down | P0 | | | | |\n")
        done = _run(d, "gate", "--strict")
        self.assertEqual(0, done.returncode, done.stdout)
        self.assertNotIn("INPUT:bugs", done.stdout)

    def test_a_malformed_row_is_a_warning(self):
        # verifies: REQ-BUGS-1118#CASE-2
        d = self._synced("| B1 | No priority | soon | | | | |\n")
        done = _run(d, "gate")
        self.assertEqual(0, done.returncode, done.stdout)
        self.assertIn("INPUT:bugs", done.stdout)
        self.assertIn("requirements/bugs/Core.md:5", done.stdout)

    def test_strict_promotes_it(self):
        # verifies: REQ-BUGS-1118#CASE-3
        d = self._synced("| B1 | No priority | soon | | | | |\n")
        self.assertEqual(1, _run(d, "gate", "--strict").returncode)

    def test_bugs_stay_out_of_the_locks(self):
        # verifies: REQ-BUGS-1118#CASE-4
        d = _repo(self)
        self.assertEqual(0, _run(d, "sync").returncode)
        lock = os.path.join(d, "requirements", "_reqlock.json")
        before = _bytes(lock)
        _run(d, "sync", "--bug", "Crash", "--module", "Core")
        self.assertEqual(0, _run(d, "sync").returncode)
        self.assertEqual(before, _bytes(lock))


class AddABug(unittest.TestCase):  # tested-by: REQ-BUGS-1119 @integration
    def test_the_first_bug_creates_the_file(self):
        # verifies: REQ-BUGS-1119#CASE-1
        d = _repo(self)
        done = _run(d, "sync", "--bug", "Refund is applied twice", "--module",
                    "Payments API", "--prio", "P1", "--date", "2026-11-02")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("B1", done.stdout)
        self.assertEqual(
            "# Bugs — Payments API\n\n" + HEAD
            + "| B1 | Refund is applied twice | P1 | 2026-11-02 |  |  |  |\n",
            _bytes(os.path.join(d, "requirements", "bugs", "Payments-API.md"))
            .decode("utf-8"))

    def test_the_next_bug_takes_the_next_id(self):
        # verifies: REQ-BUGS-1119#CASE-2
        text = "# Bugs — Core\n\nIntro.\n\n" + HEAD \
            + "| B1 | One | P1 | | | | |\n| B7 | Seven | P2 | | | | |\n" \
            + "\nA note.\n"
        out, ref = B.append_bug(text, {"module": "Core", "title": "New",
                                       "prio": "P3"})
        self.assertEqual("B8", ref)
        self.assertEqual(text.replace(
            "| B7 | Seven | P2 | | | | |\n",
            "| B7 | Seven | P2 | | | | |\n| B8 | New | P3 |  |  |  |  |\n"), out)

    def test_a_value_cannot_break_the_row(self):
        # verifies: REQ-BUGS-1119#CASE-3
        out, _ref = B.append_bug("", {"module": "Core", "title": "T",
                                      "prio": "P2", "why": "a|b\nc"})
        self.assertEqual(7, len(B._cells(out.strip().split("\n")[-1])))
        d = _repo(self)
        got = _read(d, _bug_file(d, "Core.md", out))[0]
        self.assertEqual("a|b c", got["why"])

    def test_bad_input_writes_nothing(self):
        # verifies: REQ-BUGS-1119#CASE-4
        d = _repo(self)
        for extra in (("--module", "Core", "--prio", "P9"),
                      ("--module", "Core", "--date", "2026-13-40"),
                      ("--module", "///")):
            self.assertEqual(2, _run(d, "sync", "--bug", "T", *extra).returncode)
        self.assertFalse(os.path.exists(os.path.join(d, "requirements", "bugs")))

    def test_a_module_cannot_leave_the_folder(self):
        # verifies: REQ-BUGS-1119#CASE-5
        d = _repo(self)
        self.assertEqual(0, _run(d, "sync", "--bug", "T", "--module",
                                 "../../etc").returncode)
        self.assertEqual(["etc.md"], os.listdir(
            os.path.join(d, "requirements", "bugs")))

    def test_an_estimate_stays_an_estimate(self):
        # verifies: REQ-BUGS-1119#CASE-7
        d = _repo(self)
        self.assertEqual(0, _run(d, "sync", "--bug", "T", "--module", "Core",
                                 "--prio", "p2*").returncode)
        got = json.loads(_run(d, "ask", "--bugs", "--json").stdout)["bugs"][0]
        self.assertEqual(("P2", True), (got["prio"], got["estimated"]))

    def test_the_engine_and_the_viewer_write_the_same_bytes(self):
        # verifies: REQ-BUGS-1119#CASE-6
        with open(FIXTURE, encoding="utf-8") as f:
            cases = json.load(f)
        for case in cases:
            self.assertEqual(case["file"], B.module_file(case["bug"]["module"]))
            self.assertEqual(case["expected"],
                             B.append_bug(case["text"], case["bug"])[0])


class ListBugs(unittest.TestCase):  # tested-by: REQ-BUGS-1120 @integration
    def _two_modules(self):
        d = _repo(self)
        _bug_file(d, "Payments.md", "# Bugs — Payments\n\n" + HEAD
                  + "| B1 | Slow | P2 | | | | |\n| B2 | Lost | P1 | | | | |\n")
        _bug_file(d, "Search.md", "# Bugs — Search\n\n" + HEAD
                  + "| B1 | Empty | P3 | | | | |\n")
        return d

    def test_bugs_print_by_module(self):
        # verifies: REQ-BUGS-1120#CASE-1
        done = _run(self._two_modules(), "ask", "--bugs")
        self.assertEqual(0, done.returncode)
        self.assertEqual(1, done.stdout.count("Payments (2)"))
        self.assertLess(done.stdout.index("Lost"), done.stdout.index("Slow"))

    def test_the_filters_narrow_the_list(self):
        # verifies: REQ-BUGS-1120#CASE-2
        out = _run(self._two_modules(), "ask", "--bugs", "--module", "pay",
                   "--prio", "P1").stdout
        self.assertIn("Lost", out)
        self.assertNotIn("Slow", out)
        self.assertNotIn("Empty", out)

    def test_json_carries_the_problems(self):
        # verifies: REQ-BUGS-1120#CASE-3
        d = _repo(self)
        _bug_file(d, "Core.md", "# Bugs — Core\n\n" + HEAD
                  + "| B1 | Good | P2 | | | | |\n| B2 | Bad | soon | | | | |\n")
        doc = json.loads(_run(d, "ask", "--bugs", "--json").stdout)
        self.assertEqual((1, 1), (len(doc["bugs"]), len(doc["problems"])))

    def test_no_bugs_is_an_answer(self):
        # verifies: REQ-BUGS-1120#CASE-4
        done = _run(_repo(self), "ask", "--bugs")
        self.assertEqual(0, done.returncode)
        self.assertIn("no known bugs", done.stdout)


if __name__ == "__main__":
    unittest.main()
