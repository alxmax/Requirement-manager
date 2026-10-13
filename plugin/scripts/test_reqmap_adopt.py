"""Adoption: `init --watch`, `init --propose`, the verb freeze, an outside repo.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_adopt`.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R


def _root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def _engine():
    return os.path.join(_root(), "plugin", "scripts", "reqmap.py")


def _run(cwd, *args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", _engine(), *args],
        cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, encoding="utf-8", timeout=60)


def _git(cwd, *args):
    subprocess.run(["git", "-C", cwd, *args], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _init_repo(path):
    _git(path, "init")
    _git(path, "config", "user.email", "test@test.com")
    _git(path, "config", "user.name", "Test")


def _commit(path, message):
    _git(path, "add", "-A")
    _git(path, "commit", "-m", message)


class Watch(unittest.TestCase):  # tested-by: REQ-WATCH-1092 @unit
    def _repo(self):
        path = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, path, True)
        _init_repo(path)
        with open(os.path.join(path, "README.md"), "w", encoding="utf-8") as f:
            f.write("root\n")
        _commit(path, "initial snapshot of the tree")
        return path

    def test_an_untagged_file_is_a_draft_suggestion(self):
        # verifies: REQ-WATCH-1092#CASE-1
        # verifies: REQ-WATCH-1092#CASE-6
        path = self._repo()
        os.makedirs(os.path.join(path, "src"))
        with open(os.path.join(path, "src", "login.py"), "w",
                  encoding="utf-8") as handle:
            handle.write("def login():\n    return True\n")
        with open(os.path.join(path, "notes.txt"), "w", encoding="utf-8") as handle:
            handle.write("not code\n")
        _commit(path, "login accepts an email and a password")
        done = _run(path, "init", "--watch", "HEAD~1")
        self.assertEqual(0, done.returncode, done.stderr)
        report = json.loads(done.stdout)
        paths = [item["path"] for item in report["files"]]
        self.assertEqual(["src/login.py"], paths)
        self.assertNotIn("notes.txt", paths)
        suggestion = report["files"][0]
        self.assertEqual("draft", suggestion["status"])
        self.assertTrue(suggestion["needs_confirmation"])
        self.assertTrue(suggestion["suggested_id"].startswith("DRAFT-"))
        self.assertIn("status: draft", suggestion["draft"])
        self.assertFalse(report["truncated"])
        self.assertFalse(report["writes"])
        self.assertFalse(os.path.isdir(os.path.join(path, "requirements")))

    def test_a_tagged_file_is_not_suggested(self):
        # verifies: REQ-WATCH-1092#CASE-2
        path = self._repo()
        tagged = "impl" + "ements"
        with open(os.path.join(path, "kept.py"), "w", encoding="utf-8") as handle:
            handle.write("# {}: REQ-KEEP-001\n".format(tagged))
        _commit(path, "keep the file a requirement already claims")
        done = _run(path, "init", "--watch", "HEAD~1")
        report = json.loads(done.stdout)
        self.assertEqual([], [item["path"] for item in report["files"]])

    def test_a_merge_subject_is_omitted(self):
        # verifies: REQ-WATCH-1092#CASE-3
        path = self._repo()
        with open(os.path.join(path, "login.py"), "w", encoding="utf-8") as handle:
            handle.write("def login():\n    return True\n")
        _commit(path, "Merge branch leftover")
        with open(os.path.join(path, "login.py"), "a", encoding="utf-8") as handle:
            handle.write("\n")
        _commit(path, "login accepts an email and a password")
        done = _run(path, "init", "--watch", "HEAD~2")
        report = json.loads(done.stdout)
        subjects = [item["subject"] for item in report["commits"]]
        self.assertEqual(["login accepts an email and a password"], subjects)
        self.assertEqual("draft", report["commits"][0]["status"])
        self.assertTrue(report["commits"][0]["needs_confirmation"])
        self.assertEqual("not read", report["issues"])

    def test_a_missing_ref_exits_0(self):
        # verifies: REQ-WATCH-1092#CASE-4
        path = self._repo()
        done = _run(path, "init", "--watch", "no-such-ref-xyz")
        self.assertEqual(0, done.returncode, done.stderr)
        report = json.loads(done.stdout)
        self.assertFalse(report["ok"])
        self.assertIn("git could not read that ref", report["error"])
        self.assertEqual([], report["files"])
        self.assertIn("could not read the ref", done.stderr)

    def test_gate_refuses_watch(self):
        # verifies: REQ-WATCH-1092#CASE-5
        path = self._repo()
        done = _run(path, "gate", "--watch", "HEAD")
        self.assertEqual(2, done.returncode)
        self.assertIn("init", done.stderr)

    def test_a_dash_ref_is_not_a_git_option(self):
        # verifies: REQ-WATCH-1092#CASE-7
        path = self._repo()
        before = set(os.listdir(path))
        done = _run(path, "init", "--watch", "--output=pwned x")
        self.assertEqual(0, done.returncode, done.stderr)
        report = json.loads(done.stdout)
        self.assertFalse(report["ok"])
        self.assertIn("git could not read that ref", report["error"])
        self.assertFalse(os.path.exists(os.path.join(path, "pwned x")))
        self.assertEqual(before, set(os.listdir(path)))

    def test_a_dot_directory_is_not_suggested(self):
        # verifies: REQ-WATCH-1092#CASE-1
        path = self._repo()
        for rel in (".github/x.py", ".venv/v.py", "src/ok.py", ".hidden.py"):
            full = os.path.join(path, *rel.split("/"))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as handle:
                handle.write("x = 1\n")
        _commit(path, "code lands under dot directories and a dotfile")
        done = _run(path, "init", "--watch", "HEAD~1")
        self.assertEqual(0, done.returncode, done.stderr)
        report = json.loads(done.stdout)
        self.assertEqual(["src/ok.py"], [item["path"] for item in report["files"]])

    def test_an_ignored_path_is_not_suggested(self):
        # verifies: REQ-WATCH-1092#CASE-8
        path = self._repo()
        vendor = os.path.join(path, "vendor")
        os.makedirs(vendor)
        with open(os.path.join(vendor, "lib.py"), "w", encoding="utf-8") as handle:
            handle.write("x = 1\n")
        with open(os.path.join(path, ".reqmapignore"), "w",
                  encoding="utf-8") as handle:
            handle.write("vendor/**\n")
        _commit(path, "vendor code lands in the tree")
        done = _run(path, "init", "--watch", "HEAD~1")
        self.assertEqual(0, done.returncode, done.stderr)
        report = json.loads(done.stdout)
        self.assertTrue(report["ok"], report)
        self.assertFalse(any(item["path"].startswith("vendor/")
                             for item in report["files"]))


class Propose(unittest.TestCase):  # tested-by: REQ-PROPOSE-1093 @unit
    def test_propose_prints_a_draft_and_writes_nothing(self):
        # verifies: REQ-PROPOSE-1093#CASE-1
        path = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, path, True)
        done = _run(path, "init", "--propose", "Login rejects a blank email.",
                    "--propose-files", "src/login.py")
        self.assertEqual(0, done.returncode, done.stderr)
        front = done.stdout.split("## Description")[0]
        self.assertIn("\nstatus: draft\n", front)
        self.assertNotIn("confirmed", front)
        self.assertIn("status: confirmed", done.stdout)
        self.assertIn("src/login.py", done.stdout)
        self.assertIn("not written", done.stderr)
        self.assertFalse(os.path.isdir(os.path.join(path, "requirements")))

    def test_the_mcp_server_does_not_offer_watch_or_propose(self):
        # verifies: REQ-PROPOSE-1093#CASE-2
        names = {t["name"] for t in R.mcp.MCP_TOOLS}
        self.assertNotIn("reqmap_watch", names)
        self.assertNotIn("reqmap_propose", names)

    def test_watch_and_propose_together_are_refused(self):
        # verifies: REQ-PROPOSE-1093#CASE-3
        path = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, path, True)
        done = _run(path, "init", "--watch", "HEAD", "--propose",
                    "Login rejects a blank email.")
        self.assertEqual(2, done.returncode)
        self.assertFalse(os.path.isdir(os.path.join(path, "requirements")))
        self.assertNotIn("status: draft", done.stdout)


class OutsideRepo(unittest.TestCase):  # tested-by: REQ-EXTREPO-1094 @unit
    def test_a_copied_hello_drift_still_shows_drift(self):
        # verifies: REQ-EXTREPO-1094#CASE-1
        src = os.path.join(_root(), "examples", "hello-drift")
        path = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, path, True)
        dest = os.path.join(path, "hello-drift")
        shutil.copytree(src, dest)
        done = _run(dest, "gate")
        self.assertEqual(0, done.returncode, done.stderr)
        self.assertIn("RM018", done.stdout)
        self.assertIn("HELLO-GREET-001", done.stdout)


class Surface(unittest.TestCase):  # tested-by: REQ-SURFACE-1095 @unit
    def test_the_verbs_are_the_six(self):
        # verifies: REQ-SURFACE-1095#CASE-1
        self.assertEqual(
            {"init", "gate", "sync", "clarify", "ask", "mcp"},
            set(R.COMMANDS))

    def test_the_package_metadata_names_reqmap(self):
        # verifies: REQ-SURFACE-1095#CASE-2
        with open(os.path.join(_root(), "pyproject.toml"),
                  encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn('name = "reqmap"', text)
        self.assertIn('requires-python = ">=3.9"', text)
        self.assertIn("Apache-2.0", text)
        self.assertIn("reqmap:_run_cli", text)
        self.assertTrue(callable(R._run_cli))
