"""Checking a repository that already has its requirements and tags: a change of
code is seen per definition even when the tag sits above it, and a changed
requirement the engine cannot demote keeps its drift until it is accepted.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_verify`.
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
from test_reqmap_common import _ROLE, _write

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
TAG = "# " + _ROLE + ": "


def _repo(test):
    d = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, d, True)
    return d


class TagAboveADefinition(unittest.TestCase):  # tested-by: REQ-MEMBERDRIFT-1134 @unit
    """A tag in the comments right above a Python definition owns that
    definition, so a file several requirements share keeps its drift."""

    SRC = ("{t}A-X-001\ndef f():\n    return 1\n\n"
           "# the second one\n{t}A-X-002\n@staticmethod\ndef g():\n    return 2\n\n"
           "{t}A-X-003\n\ndef h():\n    return 3\n").format(t=TAG)

    def _hashes(self, d, src):
        _write(os.path.join(d, "m.py"), src)
        members = R.scan_members(d, d)
        return R.locks.compute_member_hashes(d, members)

    def test_each_definition_is_keyed_to_the_tag_above_it(self):  # verifies: REQ-MEMBERDRIFT-1134#CASE-1
        d = _repo(self)
        h = self._hashes(d, self.SRC)
        self.assertEqual(["m.py#f"], list(h["A-X-001"]))
        self.assertEqual(["m.py#g"], list(h["A-X-002"]))     # above a decorator, under a comment

    def test_a_blank_line_ends_the_block(self):  # verifies: REQ-MEMBERDRIFT-1134#CASE-2
        d = _repo(self)
        h = self._hashes(d, self.SRC)
        self.assertEqual(["m.py"], list(h["A-X-003"]))   # the file, not h()

    def test_a_changed_body_is_drift_and_a_changed_tag_is_not(self):  # verifies: REQ-MEMBERDRIFT-1134#CASE-3
        d = _repo(self)
        before = self._hashes(d, self.SRC)
        body = self._hashes(d, self.SRC.replace("return 2", "return 20"))
        self.assertEqual(before["A-X-001"], body["A-X-001"])
        self.assertNotEqual(before["A-X-002"], body["A-X-002"])
        comment = self._hashes(d, self.SRC.replace("# the second one", "# renamed"))
        self.assertEqual(before["A-X-002"], comment["A-X-002"])


class DriftOnARequirementReadFromASource(unittest.TestCase):  # tested-by: REQ-CHECK-1135 @integration
    """A requirement read from a text source cannot be set back to draft, so
    `sync` keeps its baseline and its drift stays reported until accepted."""

    def _run(self, d, *args):
        return subprocess.run(
            [sys.executable, "-X", "utf8", ENGINE, "--root", d, "--reqs",
             os.path.join(d, "audit"), "--code", d, *args], cwd=d,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, encoding="utf-8", timeout=120).stdout

    def _seed(self, d):
        _write(os.path.join(d, "specs", "r.txt"),
               "PAY-001: A refund larger than the charge is refused.\n")
        _write(os.path.join(d, "pay.py"),
               TAG + "PAY-001\ndef refund(c, a):\n    return min(a, c)\n")
        _write(os.path.join(d, "audit", "_config.json"), json.dumps({
            "REQUIREMENT_SOURCES": [{"glob": "specs/*.txt", "format": "text",
                                     "start": "^([A-Z]+-[0-9]+):"}]}))
        self._run(d, "sync")
        _write(os.path.join(d, "specs", "r.txt"),
               "PAY-001: A refund larger than the charge is capped.\n")

    def test_the_drift_survives_a_plain_sync(self):  # verifies: REQ-CHECK-1135#CASE-1
        d = _repo(self)
        self._seed(d)
        out = self._run(d, "sync")
        self.assertIn("its baseline is kept", out)
        self.assertIn("RM018 PAY-001", self._run(d, "gate"))

    def test_accepting_clears_it_and_records_why(self):  # verifies: REQ-CHECK-1135#CASE-2
        d = _repo(self)
        self._seed(d)
        self._run(d, "sync")
        self._run(d, "sync", "--accept-drift", "capped is the rule")
        self.assertNotIn("RM018", self._run(d, "gate"))
        with open(os.path.join(d, "audit", "_driftlog.json"), encoding="utf-8") as f:
            self.assertIn("capped is the rule", f.read())


if __name__ == "__main__":
    unittest.main()
