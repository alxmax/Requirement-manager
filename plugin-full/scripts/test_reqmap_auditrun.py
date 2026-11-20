"""The audit session (ADR-0076): `sync --audit-plan`, `_audit.json`, the report
in `gate --audit`, the map's audit block and the review dossier.

Part of the `test_reqmap` suite — run it through the aggregator
(`python scripts/test_reqmap.py`), or on its own with
`python -m unittest test_reqmap_auditrun`.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R
from test_reqmap_common import _spec, _write, tag, tb_tag

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")


def _run(cwd, *args):
    return subprocess.run(
        [sys.executable, "-X", "utf8", ENGINE, *args], cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, encoding="utf-8", timeout=120)


def _repo(test, n=8, drafts=0):
    """A temp repository with `n` confirmed and `drafts` draft requirements,
    one code file tagging them all and one test file."""
    d = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, d, True)
    ids = ["AUD-R{:02d}-{:03d}".format(i, i) for i in range(1, n + drafts + 1)]
    for i, rid in enumerate(ids):
        _write(os.path.join(d, "requirements", rid + ".md"),
               _spec(rid, ["`f{}` returns {}.".format(i, i)],
                     status="confirmed" if i < n else "draft"))
    _write(os.path.join(d, "a.py"),
           "".join(tag(rid) + "\n" for rid in ids) + "x = 1\n")
    _write(os.path.join(d, "test_a.py"),
           "".join(tb_tag(rid) + "\n" for rid in ids)
           + "def test_ok():\n    assert True\n")
    return d, ids


def _audit(d):
    with open(os.path.join(d, "requirements", "_audit.json"),
              encoding="utf-8") as f:
        return json.load(f)


def _record(d, findings=(), decisions=()):
    doc = _audit(d)
    doc["findings"] += list(findings)
    doc["decisions"] += list(decisions)
    _write(os.path.join(d, "requirements", "_audit.json"), json.dumps(doc))


def _f(rid, run, label, clause=1, note=""):
    return {"id": rid, "run": run, "label": label, "clause": clause, "note": note}


def _d(rid, counter, clause=1):
    return {"id": rid, "clause": clause, "counter": counter, "by": "reviewer"}


def _doc(ranked=(), rnd=(), findings=(), decisions=()):
    return {"schema": 1,
            "plan": {"date": "2026-10-19", "seed": 1, "key": "k",
                     "ranked": list(ranked), "random": list(rnd),
                     "bands": dict(R.config.AUDIT_BANDS), "min_positives": 5},
            "findings": list(findings), "decisions": list(decisions)}


class AuditPlan(unittest.TestCase):  # tested-by: REQ-AUDITRUN-1105 @unit
    def test_the_plan_is_written_with_its_seed(self):
        # verifies: REQ-AUDITRUN-1105#CASE-1
        d, _ids = _repo(self, n=60)
        done = _run(d, "sync", "--audit-plan", "--ranked", "5", "--random", "5",
                    "--seed", "7")
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)
        plan = _audit(d)["plan"]
        self.assertEqual((5, 5, 7), (len(plan["ranked"]), len(plan["random"]),
                                     plan["seed"]))
        self.assertRegex(plan["date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(R.config.AUDIT_BANDS, plan["bands"])
        self.assertFalse(set(plan["ranked"]) & set(plan["random"]))

    def test_one_seed_gives_one_set(self):
        # verifies: REQ-AUDITRUN-1105#CASE-2
        plans = []
        for _ in range(2):
            d, _ids = _repo(self, n=60)
            _run(d, "sync", "--audit-plan", "--ranked", "5", "--random", "5",
                 "--seed", "7")
            plan = _audit(d)["plan"]
            plans.append((plan["ranked"], plan["random"]))
        self.assertEqual(plans[0], plans[1])

    def test_the_ranked_set_follows_the_ordering_key(self):
        # verifies: REQ-AUDITRUN-1105#CASE-3
        meta = {"status": "confirmed", "layer": "feature"}
        reqs = {rid: {"meta": dict(meta), "body": ""} for rid in "CBA"}
        ws = SimpleNamespace(reqs=reqs, members={}, ac_cover={},
                             code_root=None, reqs_dir=None)
        gaps = [("A", 3, 3), ("B", 1, 1), ("C", 1, 1)]
        asks = lambda rid, *_a: [{}] * (4 if rid == "B" else 0)
        with mock.patch.object(R.auditrun, "case_gaps", return_value=gaps), \
                mock.patch.object(R.auditrun, "_clarify_questions", asks), \
                mock.patch.object(R.auditrun, "_domain_heads", return_value={}):
            plan = R.auditrun.build_plan(ws, 3, 0, 1, "2026-10-19")["plan"]
        self.assertEqual(["A", "B", "C"], plan["ranked"])

    def test_an_existing_plan_is_not_replaced(self):
        # verifies: REQ-AUDITRUN-1105#CASE-4
        d, _ids = _repo(self)
        _run(d, "sync", "--audit-plan", "--seed", "3")
        path = os.path.join(d, "requirements", "_audit.json")
        with open(path, "rb") as f:
            before = f.read()
        done = _run(d, "sync", "--audit-plan", "--seed", "4")
        self.assertEqual(1, done.returncode)
        self.assertIn("_audit.json", done.stdout)
        with open(path, "rb") as f:
            self.assertEqual(before, f.read())

    def test_a_draft_is_never_sampled(self):
        # verifies: REQ-AUDITRUN-1105#CASE-5
        d, ids = _repo(self, n=4, drafts=4)
        _run(d, "sync", "--audit-plan", "--ranked", "4", "--random", "4")
        plan = _audit(d)["plan"]
        self.assertFalse(set(ids[4:]) & set(plan["ranked"] + plan["random"]))


class AuditRecord(unittest.TestCase):  # tested-by: REQ-AUDITRUN-1106 @unit
    def _planned(self):
        d, _ids = _repo(self, n=4)
        _run(d, "sync", "--audit-plan", "--ranked", "2", "--random", "2",
             "--seed", "1")
        return d, _audit(d)["plan"]["ranked"]

    def test_a_valid_record_is_read(self):
        # verifies: REQ-AUDITRUN-1106#CASE-1
        d, ranked = self._planned()
        _record(d, [_f(ranked[0], 1, "bug"), _f(ranked[0], 2, "bug")],
                [_d(ranked[0], "B")])
        done = _run(d, "gate", "--audit", "--json")
        self.assertEqual(1, json.loads(done.stdout)["audit_session"]
                         ["counters"]["B"])
        self.assertNotIn("INPUT:audit", _run(d, "gate").stdout)

    def test_a_malformed_entry_is_named_not_fixed(self):
        # verifies: REQ-AUDITRUN-1106#CASE-2
        d, ranked = self._planned()
        _record(d, [_f(ranked[0], 1, "maybe")], [_d(ranked[0], "X")])
        path = os.path.join(d, "requirements", "_audit.json")
        with open(path, "rb") as f:
            before = f.read()
        out = _run(d, "gate").stdout
        self.assertIn("INPUT:audit findings[0] label 'maybe'", out)
        self.assertIn("INPUT:audit decisions[0]", out)
        self.assertEqual(1, _run(d, "gate", "--strict").returncode)
        with open(path, "rb") as f:
            self.assertEqual(before, f.read())

    def test_an_id_outside_the_plan_is_refused(self):
        # verifies: REQ-AUDITRUN-1106#CASE-3
        doc = _doc(ranked=["AUD-A-001"], findings=[_f("AUD-Z-009", 1, "bug")])
        findings, _dec, problems = R.auditrun.validate(doc)
        self.assertEqual([], findings)
        self.assertIn("in neither set", problems[0])

    def test_one_finding_one_counter(self):
        # verifies: REQ-AUDITRUN-1106#CASE-4
        doc = _doc(ranked=["AUD-A-001"], findings=[_f("AUD-A-001", 1, "bug")],
                   decisions=[_d("AUD-A-001", "B"), _d("AUD-A-001", "F_copilot")])
        rep = R.auditrun.report(doc)
        self.assertEqual((1, 0), (rep["counters"]["B"],
                                  rep["counters"]["F_copilot"]))
        self.assertIn("a second time", rep["problems"][0])


class AuditReport(unittest.TestCase):  # tested-by: REQ-AUDITRUN-1107 @unit
    def test_a_rate_carries_its_interval(self):
        # verifies: REQ-AUDITRUN-1107#CASE-1
        ids = ["AUD-P{:02d}-001".format(i) for i in range(20)]
        doc = _doc(ranked=ids, findings=[_f(i, 1, "bug") for i in ids],
                   decisions=[_d(i, "B" if n < 7 else "F_copilot")
                              for n, i in enumerate(ids)])
        p = R.auditrun.report(doc)["rates"]["precision"]
        self.assertEqual((7, 20), (p["k"], p["n"]))
        self.assertAlmostEqual(0.18, p["lo"], places=2)
        self.assertAlmostEqual(0.57, p["hi"], places=2)

    def test_zero_is_an_upper_bound(self):
        # verifies: REQ-AUDITRUN-1107#CASE-2
        ids = ["AUD-Q{:02d}-001".format(i) for i in range(25)]
        doc = _doc(rnd=ids, findings=[_f(i, 1, "ok", clause=None) for i in ids])
        m = R.auditrun.report(doc)["rates"]["miss_rate"]
        self.assertEqual((0, 25), (m["k"], m["n"]))
        self.assertAlmostEqual(0.13, m["hi"], places=2)

    def test_too_few_positives_are_not_judged(self):
        # verifies: REQ-AUDITRUN-1107#CASE-3
        ids = ["AUD-S{:02d}-001".format(i) for i in range(4)]
        doc = _doc(ranked=ids, findings=[_f(i, 1, "bug") for i in ids],
                   decisions=[_d(i, "B" if n < 2 else "F_copilot")
                              for n, i in enumerate(ids)])
        rep = R.auditrun.report(doc)
        self.assertFalse(rep["rates"]["precision"]["judged"])
        self.assertEqual("not judged yet", rep["band"])
        self.assertIn("not judged", "\n".join(R.auditrun.report_lines(rep)))

    def test_runs_that_disagree_are_unresolved(self):
        # verifies: REQ-AUDITRUN-1107#CASE-4
        doc = _doc(ranked=["AUD-U-001"],
                   findings=[_f("AUD-U-001", 1, "bug"), _f("AUD-U-001", 2, "ok")],
                   decisions=[_d("AUD-U-001", "B")])
        c = R.auditrun.report(doc)["counters"]
        self.assertEqual((1, 0), (c["U"], c["B"]))

    def test_the_exit_code_is_the_gates(self):
        # verifies: REQ-AUDITRUN-1107#CASE-5
        d, _ids = _repo(self, n=20)
        _run(d, "sync")
        _run(d, "sync", "--audit-plan", "--ranked", "20", "--random", "0")
        _record(d, [_f(rid, 1, "ok", clause=None)
                    for rid in _audit(d)["plan"]["ranked"]])
        _run(d, "sync")
        done = _run(d, "gate", "--audit")
        self.assertIn("band         stop", done.stdout)
        self.assertEqual(0, done.returncode, done.stdout)


class AuditMap(unittest.TestCase):  # tested-by: REQ-AUDITRUN-1108 @unit
    def test_the_map_carries_the_audit(self):
        # verifies: REQ-AUDITRUN-1108#CASE-1
        d, _ids = _repo(self, n=4)
        _run(d, "sync", "--audit-plan", "--ranked", "2", "--random", "0",
             "--seed", "11")
        ranked = _audit(d)["plan"]["ranked"]
        _record(d, [_f(ranked[0], 1, "bug"), _f(ranked[1], 1, "bug")],
                [_d(ranked[0], "B"), _d(ranked[1], "F_copilot")])
        _run(d, "sync")
        with open(os.path.join(d, "requirements", "_map.json"),
                  encoding="utf-8") as f:
            audit = json.load(f)["audit"]
        self.assertEqual(11, audit["plan"]["seed"])
        self.assertEqual(["B", "F_copilot"],
                         [r["findings"][0]["counter"] for r in audit["requirements"]])

    def test_no_audit_no_key(self):
        # verifies: REQ-AUDITRUN-1108#CASE-2
        d, _ids = _repo(self, n=2)
        _run(d, "sync")
        with open(os.path.join(d, "requirements", "_map.json"),
                  encoding="utf-8") as f:
            self.assertNotIn("audit", json.load(f))

    def test_the_server_does_not_write_during_an_audit(self):
        # verifies: REQ-AUDITRUN-1108#CASE-4
        d, ids = _repo(self, n=3)
        _run(d, "sync")
        _run(d, "sync", "--audit-plan", "--ranked", "1", "--random", "1")
        def snapshot():
            seen = {}
            for p, _dirs, files in os.walk(d):
                for f in files:
                    with open(os.path.join(p, f), "rb") as handle:
                        seen[os.path.relpath(os.path.join(p, f), d)] = handle.read()
            return seen
        before = snapshot()
        args = {"reqmap_show": {"id": ids[0]}, "reqmap_search": {"query": "f"},
                "reqmap_review": {"id": ids[0]}, "reqmap_clarify": {"id": ids[0]}}
        msgs = [{"jsonrpc": "2.0", "id": i, "method": "tools/call",
                 "params": {"name": t["name"], "arguments": args.get(t["name"], {})}}
                for i, t in enumerate(R.mcp.tool_list(False), 1)]
        subprocess.run([sys.executable, "-X", "utf8", ENGINE, "mcp", "--root", d],
                       input="".join(json.dumps(m) + "\n" for m in msgs),
                       capture_output=True, text=True, encoding="utf-8",
                       timeout=300, env=dict(os.environ, CLAUDE_PROJECT_DIR=""))
        self.assertEqual(before, snapshot())


class AuditReview(unittest.TestCase):  # tested-by: REQ-AUDITRUN-1109 @unit
    def _review(self, d, rid):
        return json.loads(_run(d, "ask", "--review", rid, "--json").stdout)

    def test_the_dossier_carries_the_prompt(self):
        # verifies: REQ-AUDITRUN-1109#CASE-1
        d, _ids = _repo(self, n=4)
        _run(d, "sync", "--audit-plan", "--ranked", "1", "--random", "0")
        ranked = _audit(d)["plan"]["ranked"][0]
        out = self._review(d, ranked)
        self.assertEqual("ranked", out["requirements"][0]["in_plan"])
        self.assertTrue(all(label in out["audit"]["prompt"]
                            for label in R.auditrun.LABELS))

    def test_a_requirement_outside_the_plan_says_so(self):
        # verifies: REQ-AUDITRUN-1109#CASE-2
        d, ids = _repo(self, n=4)
        _run(d, "sync", "--audit-plan", "--ranked", "1", "--random", "0")
        plan = _audit(d)["plan"]
        outside = next(i for i in ids if i not in plan["ranked"])
        self.assertEqual("no", self._review(d, outside)["requirements"][0]["in_plan"])

    def test_no_audit_no_change(self):
        # verifies: REQ-AUDITRUN-1109#CASE-3
        d, ids = _repo(self, n=2)
        out = self._review(d, ids[0])
        self.assertNotIn("audit", out)
        self.assertNotIn("in_plan", out["requirements"][0])


class AuditSession(unittest.TestCase):  # tested-by: ARCH-AUDITRUN-076 @integration
    def test_a_whole_session_runs_on_the_existing_verbs(self):
        # verifies: ARCH-AUDITRUN-076#CASE-1
        d, _ids = _repo(self, n=4)
        self.assertEqual(0, _run(d, "sync", "--audit-plan", "--ranked", "2",
                                 "--random", "0").returncode)
        ranked = _audit(d)["plan"]["ranked"]
        _record(d, [_f(ranked[0], 1, "bug"), _f(ranked[1], 1, "false-coverage")],
                [_d(ranked[0], "B"), _d(ranked[1], "G")])
        c = json.loads(_run(d, "gate", "--audit", "--json").stdout)[
            "audit_session"]["counters"]
        self.assertEqual((1, 1), (c["B"], c["G"]))
        self.assertEqual({"init", "gate", "sync", "clarify", "ask", "mcp"},
                         set(R.COMMANDS))

    def test_the_map_shows_the_session(self):
        # verifies: ARCH-AUDITRUN-076#CASE-3
        d, _ids = _repo(self, n=3)
        _run(d, "sync", "--audit-plan", "--ranked", "1", "--random", "0")
        rid = _audit(d)["plan"]["ranked"][0]
        _record(d, [_f(rid, 1, "bug")], [_d(rid, "B")])
        _run(d, "sync")
        with open(os.path.join(d, "requirements", "_map.json"),
                  encoding="utf-8") as f:
            self.assertEqual(1, json.load(f)["audit"]["counters"]["B"])

    def test_the_mcp_tool_set_does_not_change(self):
        # verifies: ARCH-AUDITRUN-076#CASE-2
        d, _ids = _repo(self, n=2)
        _run(d, "sync", "--audit-plan", "--ranked", "1", "--random", "0")
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}]
        done = subprocess.run([sys.executable, "-X", "utf8", ENGINE, "mcp", "--root", d],
                              input=json.dumps(msgs[0]) + "\n", capture_output=True,
                              text=True, encoding="utf-8", timeout=120,
                              env=dict(os.environ, CLAUDE_PROJECT_DIR=""))
        names = [t["name"] for t in json.loads(done.stdout)["result"]["tools"]]
        self.assertEqual(sorted(t["name"] for t in R.mcp.tool_list(False)),
                         sorted(names))
        self.assertEqual(11, len(names))


if __name__ == "__main__":
    unittest.main(verbosity=2)
