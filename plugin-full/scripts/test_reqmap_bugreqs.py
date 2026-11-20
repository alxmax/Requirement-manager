"""Which open bugs name a requirement (ADR-0083): `gate --show`, the map, and a
verdict that does not move.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_bugreqs`.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reqmap_engine import bugreqs as BR
from test_reqmap_bugs import HEAD, _bug_file, _map, _repo, _run

RID = "BUG-THING-001"


def _bugs(d, *rows):
    _bug_file(d, "Core.md", "# Bugs — Core\n\n" + HEAD + "".join(
        "| {} | {} | {} | 2026-11-02 | {} | | {} |\n".format(*r) for r in rows))


class BugsNameARequirement(unittest.TestCase):  # tested-by: ARCH-BUGS-078 @integration  # tested-by: REQ-BUGS-1131 @integration

    def test_the_dossier_lists_the_bugs_that_name_it(self):
        # verifies: REQ-BUGS-1131#CASE-1
        d = _repo(self)
        _bugs(d, ("B1", "Crash on save", "P1", "", "breaks " + RID),
              ("B2", "Slow list", "P3", "", "unrelated"))
        out = _run(d, "gate", "--show", RID).stdout
        self.assertIn("Open bugs (1):", out)
        self.assertIn("P1   Core:B1  Crash on save", out)
        self.assertNotIn("Core:B2", out)

    def test_json_carries_the_list_and_no_list_carries_no_key(self):
        # verifies: REQ-BUGS-1131#CASE-2
        d = _repo(self)
        rec = json.loads(_run(d, "gate", "--show", RID, "--json").stdout)
        self.assertNotIn("bugs", rec)
        _bugs(d, ("B1", "Crash", "P0", "a.py", "[[{}]]".format(RID)))
        rec = json.loads(_run(d, "gate", "--show", RID, "--json").stdout)
        self.assertEqual(["Core:B1"], [b["id"] for b in rec["bugs"]])
        _bugs(d, ("B1", "Crash", "P0", "a.py", "nothing named"))
        rec = json.loads(_run(d, "gate", "--show", RID, "--json").stdout)
        self.assertEqual([], rec["bugs"])

    def test_an_id_is_named_whole(self):
        # verifies: REQ-BUGS-1131#CASE-3
        bugs = [{"title": "X-10 fails"}, {"source": "X-1#CASE-2"},
                {"why": "see [[X-1]]."}, {"where": "x-1"}]
        BR.link(bugs, ["X-1", "X-10"])
        self.assertEqual([["X-10"], ["X-1"], ["X-1"], []],
                         [b["reqs"] for b in bugs])

    def test_the_map_carries_the_ids_and_a_fixed_bug_leaves_the_dossier(self):
        # verifies: REQ-BUGS-1131#CASE-4
        d = _repo(self)
        _bugs(d, ("B1", "Crash", "P1", "", RID))
        self.assertEqual(0, _run(d, "sync").returncode)
        self.assertEqual([[RID]], [b["reqs"] for b in _map(d)["bugs"]])
        self.assertEqual(0, _run(d, "sync", "--fix", "Core:B1",
                                 "--commit", "abc1234").returncode)
        rec = json.loads(_run(d, "gate", "--show", RID, "--json").stdout)
        self.assertEqual([], rec["bugs"])

    def test_an_open_p0_does_not_move_the_verdict(self):
        # verifies: REQ-BUGS-1131#CASE-5
        d = _repo(self)
        _bugs(d, ("B1", "Data loss", "P0", "", RID))
        self.assertEqual(0, _run(d, "sync").returncode)
        gate = _run(d, "gate", "--full", "--strict")
        self.assertEqual(0, gate.returncode, gate.stdout)
        self.assertNotIn("B1", gate.stdout)


if __name__ == "__main__":
    unittest.main()
