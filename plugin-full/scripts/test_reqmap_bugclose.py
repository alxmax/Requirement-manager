"""The life of a known bug after it is listed (ADR-0082): written in the file's
own shape, closed by hand or by a commit, kept in the register."""
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reqmap_engine import bugclose as C
from reqmap_engine import bugs as B
from test_reqmap_bugs import ENGINE, _bug_file, _bytes, _map, _repo, _run
from test_reqmap_common import _write

SHAPES = os.path.join(os.path.dirname(ENGINE), "..", "..", "app", "scripts",
                      "smoke", "bugshape.fixture.json")
HEAD = ("| ID | Bug | Priority | Date | Where | Why it matters | Source |\n"
        "|---|---|---|---|---|---|---|\n")
OPEN = "# Bugs — Billing\n\n" + HEAD + (
    "| B1 | Refund is applied twice | P1 | 2026-10-01 |  |  |  |\n"
    "| B2 | Wrong total | P3 |  |  |  |  |\n")


def _git(d, *args):
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath="] + list(args),
        cwd=d, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, encoding="utf-8", timeout=60)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()


def _commit(d, message):
    _git(d, "add", "-A")
    _git(d, "commit", "--allow-empty", "-m", message)
    return _git(d, "rev-parse", "--short", "HEAD")


def _gitrepo(test):
    d = _repo(test)
    _bug_file(d, "Billing.md", OPEN)
    _write(os.path.join(d, "VERSION"), "1.2.3\n")
    _git(d, "init", "-q")
    _commit(d, "start")
    return d


def _register(d):
    return C.parse_fixed(_bytes(os.path.join(
        d, "requirements", "bugs", "_fixed.md")).decode("utf-8"))


def _listed(d):
    out = _run(d, "ask", "--bugs", "--json")
    return [b["id"] for b in json.loads(out.stdout)["bugs"]]


class OwnShape(unittest.TestCase):  # tested-by: REQ-BUGS-1126 @integration
    def test_a_numbered_file_with_its_own_columns(self):
        # verifies: REQ-BUGS-1126#CASE-1
        d = _repo(self)
        _write(os.path.join(d, "requirements", "_config.json"), json.dumps(
            {"BUG_COLUMNS": {"title": ["Titlu"], "prio": ["Prioritate"]}}))
        _bug_file(d, "04_Billing.md", "# Known — Billing\n\n## P2\n\n"
                  "| ID | Titlu | Prioritate |\n|---|---|---|\n| B36 | a | P2 |\n")
        self.assertEqual(0, _run(d, "sync", "--bug", "x", "--module", "Billing",
                                 "--prio", "P2").returncode)
        folder = os.path.join(d, "requirements", "bugs")
        self.assertEqual(["04_Billing.md"], os.listdir(folder))
        self.assertIn(b"| B37 | x | P2 |", _bytes(
            os.path.join(folder, "04_Billing.md")))

    def test_a_new_module_takes_the_next_number(self):
        # verifies: REQ-BUGS-1126#CASE-2
        d = _repo(self)
        _bug_file(d, "04_Billing.md", OPEN)
        self.assertEqual(0, _run(d, "sync", "--bug", "x", "--module",
                                 "Ledger").returncode)
        self.assertTrue(os.path.isfile(os.path.join(
            d, "requirements", "bugs", "05_Ledger.md")))

    def test_no_section_for_the_priority_joins_the_first_table(self):
        # verifies: REQ-BUGS-1126#CASE-3
        table = "| ID | Bug | Priority |\n|---|---|---|\n"
        text = ("# Bugs — M\n\n## P0-P1\n\n" + table + "| B1 | a | P1 |\n\n"
                "## P2\n\n" + table + "| B2 | b | P2 |\n")
        out = B.append_bug(text, {"module": "M", "title": "c", "prio": "P4"})[0]
        self.assertLess(out.index("| B3 | c | P4 |"), out.index("## P2"))

    def test_a_likely_duplicate_needs_force(self):
        # verifies: REQ-BUGS-1126#CASE-4
        d = _repo(self)
        _bug_file(d, "Billing.md", OPEN)
        path = os.path.join(d, "requirements", "bugs", "Billing.md")
        before = _bytes(path)
        args = ("sync", "--bug", "Refund applied twice", "--module", "Billing")
        got = _run(d, *args)
        self.assertEqual(2, got.returncode)
        self.assertIn("B1", got.stdout)
        self.assertEqual(before, _bytes(path))
        self.assertEqual(0, _run(d, *(args + ("--force",))).returncode)
        self.assertIn(b"| B3 | Refund applied twice", _bytes(path))

    def test_the_engine_and_the_viewer_agree(self):
        # verifies: REQ-BUGS-1126#CASE-5
        with open(SHAPES, encoding="utf-8") as f:
            cases = json.load(f)
        for case in cases:
            files = [tuple(pair) for pair in case["files"]]
            self.assertEqual(case["chosen"], B.bug_file(files, case["module"]))
            text = dict(files).get(case["chosen"], "")
            self.assertEqual(
                (case["expected"], case["ref"]),
                B.append_bug(text, case["bug"], case["floor"], case["format"]))


class AuditedEdges(unittest.TestCase):  # tested-by: REQ-BUGS-1118 @integration
    def test_a_unicode_line_break_loses_no_row(self):
        # verifies: REQ-BUGS-1118#CASE-5
        d = _repo(self)
        _bug_file(d, "Billing.md", OPEN.replace("Wrong total", "Wrong\u2028total"))
        self.assertEqual(["Billing:B1", "Billing:B2"], _listed(d))

    def test_a_byte_order_mark_hides_no_heading(self):
        # verifies: REQ-BUGS-1118#CASE-6
        d = _repo(self)
        _bug_file(d, "04_Billing.md", "\ufeff" + OPEN)
        out = json.loads(_run(d, "ask", "--bugs", "--json").stdout)
        self.assertEqual("Billing", out["bugs"][0]["module"])

    def test_one_id_in_two_files_is_named(self):
        # verifies: REQ-BUGS-1118#CASE-7
        d = _repo(self)
        for folder in ("a", "b"):
            _write(os.path.join(d, folder, "Own.md"), OPEN)
        _write(os.path.join(d, "requirements", "_config.json"),
               json.dumps({"BUG_SOURCES": ["*/Own.md"]}))
        out = json.loads(_run(d, "ask", "--bugs", "--json").stdout)
        self.assertTrue(any("is also in" in p for p in out["problems"]))

    def test_an_unreadable_file_is_exit_2(self):
        # verifies: REQ-BUGS-1119#CASE-8
        d = _repo(self)
        path = os.path.join(d, "requirements", "bugs", "Billing.md")
        _write(path, "x")
        with open(path, "wb") as f:
            f.write(b"\xff\xfe")
        self.assertEqual(2, _run(d, "sync", "--bug", "x", "--module",
                                 "Billing").returncode)


class FixByHand(unittest.TestCase):  # tested-by: REQ-BUGS-1127 @integration
    def test_a_fix_moves_the_row(self):
        # verifies: REQ-BUGS-1127#CASE-1
        d = _gitrepo(self)
        head = _git(d, "rev-parse", "--short", "HEAD")
        self.assertEqual(0, _run(d, "sync", "--fix", "Billing B1").returncode)
        self.assertEqual(["Billing:B2"], _listed(d))
        row = _register(d)[0]
        self.assertEqual(("Billing:B1", "Refund is applied twice", "Billing",
                          "P1", "2026-10-01", "1.2.3", head),
                         (row["id"], row["title"], row["module"], row["prio"],
                          row["date"], row["version"], row["commit"]))
        self.assertRegex(row["fixed"], r"^\d{4}-\d{2}-\d{2}$")

    def test_a_number_is_never_given_twice(self):
        # verifies: REQ-BUGS-1127#CASE-2
        d = _gitrepo(self)
        _run(d, "sync", "--fix", "Billing:B2")
        out = _run(d, "sync", "--bug", "Other", "--module", "Billing")
        self.assertIn("bug B3 added", out.stdout)

    def test_a_dismissal(self):
        # verifies: REQ-BUGS-1127#CASE-3
        d = _gitrepo(self)
        self.assertEqual(0, _run(d, "sync", "--fix", "Billing:B1", "--note",
                                 "works as designed").returncode)
        row = _register(d)[0]
        self.assertEqual(("not a bug", "—", "works as designed"),
                         (row["version"], row["commit"], row["note"]))

    def test_refused_closes_write_nothing(self):
        # verifies: REQ-BUGS-1127#CASE-4
        d = _gitrepo(self)
        _write(os.path.join(d, "known.md"), "# Bugs — Own\n\n" + HEAD
               + "| B1 | Theirs | P2 |  |  |  |  |\n")
        _write(os.path.join(d, "requirements", "_config.json"),
               json.dumps({"BUG_SOURCES": ["known.md"]}))
        _run(d, "sync", "--fix", "Billing:B2")
        folder = os.path.join(d, "requirements", "bugs")
        paths = [os.path.join(folder, n) for n in os.listdir(folder)]
        paths.append(os.path.join(d, "known.md"))
        before = [_bytes(p) for p in paths]
        for target in ("Billing:B9", "Billing:B2", "known:B1"):
            self.assertEqual(2, _run(d, "sync", "--fix", target).returncode)
        self.assertEqual(before, [_bytes(p) for p in paths])

    def test_a_stray_carriage_return_closes_the_right_row(self):
        # verifies: REQ-BUGS-1127#CASE-6
        d = _gitrepo(self)
        path = os.path.join(d, "requirements", "bugs", "Billing.md")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(OPEN.replace("# Bugs — Billing\n",
                                 "# Bugs — Billing\nnote\rmore\n"))
        self.assertEqual(0, _run(d, "sync", "--fix", "Billing:B2").returncode)
        self.assertEqual(["Billing:B1"], _listed(d))
        self.assertEqual("Billing:B2", _register(d)[0]["id"])

    def test_a_row_that_moved_is_refused(self):
        # verifies: REQ-BUGS-1127#CASE-6
        with self.assertRaises(ValueError):
            C.close_bug(OPEN, "", {"ref": "B9", "line": 5, "file": "f"}, {})

    def test_a_broken_register_is_not_overwritten(self):
        # verifies: REQ-BUGS-1127#CASE-7
        d = _gitrepo(self)
        path = os.path.join(d, "requirements", "bugs", "_fixed.md")
        with open(path, "wb") as f:
            f.write(b"caf\xe9\n")
        self.assertEqual(2, _run(d, "sync", "--fix", "Billing:B1").returncode)
        self.assertEqual(b"caf\xe9\n", _bytes(path))
        self.assertEqual(["Billing:B1", "Billing:B2"], _listed(d))

    def test_a_declared_folder_does_not_read_the_register(self):
        # verifies: REQ-BUGS-1127#CASE-8
        d = _gitrepo(self)
        _run(d, "sync", "--fix", "Billing:B1")
        _write(os.path.join(d, "requirements", "_config.json"),
               json.dumps({"BUG_SOURCES": ["requirements/bugs/*.md"]}))
        self.assertEqual(["Billing:B2"], _listed(d))

    def test_an_id_spelled_with_a_space_after_the_colon(self):
        # verifies: REQ-BUGS-1127#CASE-1
        self.assertEqual("Billing:B1", C.bug_id("Billing: B1"))

    def test_a_dotted_date_reaches_the_map_as_iso(self):
        # verifies: REQ-BUGS-1129#CASE-1
        d = _repo(self)
        _bug_file(d, "_fixed.md", "| ID | Bug | Found | Fixed |\n|---|---|---|---|\n"
                  "| M:B1 | a | 01.10.2026 | 15.10.2026 |\n")
        row = C.fixed_block(os.path.join(d, "requirements"))[0]
        self.assertEqual(("2026-10-01", "2026-10-15"), (row["date"], row["fixed"]))

    def test_a_repositorys_own_register(self):
        # verifies: REQ-BUGS-1127#CASE-5
        d = _gitrepo(self)
        _write(os.path.join(d, "requirements", "_config.json"), json.dumps(
            {"BUG_REGISTER": "istoric.md", "BUG_REGISTER_COLUMNS": {
                "title": ["Titlu"], "fixed": ["Rezolvat"]}}))
        _bug_file(d, "istoric.md", "# Istoric\n\n| ID | Titlu | Rezolvat |\n"
                  "|---|---|---|\n")
        self.assertEqual(0, _run(d, "sync", "--fix", "Billing:B1").returncode)
        text = _bytes(os.path.join(d, "requirements", "bugs",
                                   "istoric.md")).decode("utf-8")
        self.assertIn("| Billing:B1 | Refund is applied twice | 20", text)
        self.assertEqual(["Billing:B2"], _listed(d))


class FixByCommit(unittest.TestCase):  # tested-by: REQ-BUGS-1128 @integration
    def test_a_commit_closes_a_bug(self):
        # verifies: REQ-BUGS-1128#CASE-1
        d = _gitrepo(self)
        sha = _commit(d, "Stop the double refund\n\nFixes-bug: Billing B1\n")
        date = _git(d, "log", "-1", "--format=%cs")
        self.assertEqual(0, _run(d, "sync").returncode)
        row = _register(d)[0]
        self.assertEqual(("Billing:B1", sha, date),
                         (row["id"], row["commit"], row["fixed"]))
        self.assertEqual(["Billing:B2"], _listed(d))

    def test_a_second_sync_changes_nothing(self):
        # verifies: REQ-BUGS-1128#CASE-2
        d = _gitrepo(self)
        _commit(d, "Fix\n\nFixes-bug: Billing:B1\n")
        _run(d, "sync")
        folder = os.path.join(d, "requirements", "bugs")
        names = sorted(os.listdir(folder))
        before = [_bytes(os.path.join(folder, n)) for n in names]
        self.assertEqual(0, _run(d, "sync").returncode)
        self.assertEqual(before, [_bytes(os.path.join(folder, n)) for n in names])
        self.assertEqual(1, len(_register(d)))

    def test_the_version_at_that_commit(self):
        # verifies: REQ-BUGS-1128#CASE-3
        d = _gitrepo(self)
        _commit(d, "Fix\n\nFixes-bug: Billing:B1\n")
        _write(os.path.join(d, "VERSION"), "2.0.0\n")
        _commit(d, "Release")
        _run(d, "sync")
        self.assertEqual("1.2.3", _register(d)[0]["version"])

    def test_a_trailer_that_names_nothing(self):
        # verifies: REQ-BUGS-1128#CASE-4
        d = _gitrepo(self)
        sha = _commit(d, "Fix\n\nFixes-bug: Billing:B99\n")
        got = _run(d, "sync")
        self.assertEqual(0, got.returncode)
        self.assertIn("commit {} names Billing:B99".format(sha), got.stdout)
        self.assertNotIn("B99", _run(d, "gate", "--strict").stdout)

    def test_no_git(self):
        # verifies: REQ-BUGS-1128#CASE-5
        d = _repo(self)
        _bug_file(d, "Billing.md", OPEN)
        with mock.patch.object(C, "_git", return_value=None):
            self.assertEqual([], C.fix_trailers(d))
        path = os.path.join(d, "requirements", "bugs", "Billing.md")
        before = _bytes(path)
        self.assertEqual(0, _run(d, "sync").returncode)
        self.assertEqual(before, _bytes(path))

    def test_a_repositorys_own_trailer(self):
        # verifies: REQ-BUGS-1128#CASE-6
        d = _gitrepo(self)
        _write(os.path.join(d, "requirements", "_config.json"),
               json.dumps({"BUG_FIX_TRAILERS": ["Rezolva"]}))
        _commit(d, "Fix\n\nrezolva: Billing:B2\n")
        _run(d, "sync")
        self.assertEqual("Billing:B2", _register(d)[0]["id"])


class FixedOnTheMap(unittest.TestCase):  # tested-by: REQ-BUGS-1129 @integration
    def test_the_register_reaches_the_map(self):
        # verifies: REQ-BUGS-1129#CASE-1
        d = _gitrepo(self)
        _commit(d, "Fix\n\nFixes-bug: Billing:B1\n")
        _run(d, "sync")
        data = _map(d)
        self.assertEqual(["Billing:B1"], [r["id"] for r in data["bugs_fixed"]])
        self.assertEqual(["Billing:B2"], [b["id"] for b in data["bugs"]])

    def test_an_empty_register_adds_no_key(self):
        # verifies: REQ-BUGS-1129#CASE-1
        d = _gitrepo(self)
        _run(d, "sync")
        self.assertNotIn("bugs_fixed", _map(d))

    def test_a_github_remote_links_the_commit(self):
        # verifies: REQ-BUGS-1129#CASE-2
        d = _gitrepo(self)
        _run(d, "sync", "--fix", "Billing:B1", "--commit", "abc1234")
        _git(d, "remote", "add", "origin", "https://github.com/o/r.git")
        _run(d, "sync")
        self.assertNotIn("forge", _map(d))
        page = _bytes(os.path.join(d, "requirements", "_map.html"))
        if os.path.isfile(os.path.join(os.path.dirname(ENGINE),
                                       "_map_viewer.html")):
            self.assertIn(b"https://github.com/o/r", page)
        self.assertEqual("https://github.com/o/r", C.forge_of(d))
        with mock.patch.object(C, "_git_remote_web_url",
                               return_value="https://gitlab.example/o/r"):
            self.assertEqual("", C.forge_of(d))


if __name__ == "__main__":
    unittest.main()
