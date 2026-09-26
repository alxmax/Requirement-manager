"""Everything the engine prints or renders: the map and its diagrams, the viewer,
the published site, health, risk, findings, search, duplicates, the audit, the design
review and the command registry.

Part of the `test_reqmap` suite — run it through the aggregator (`python
scripts/test_reqmap.py`), or on its own with `python -m unittest test_reqmap_report`."""
import ast
import errno
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R


from test_reqmap_common import (  # noqa: F401  (fixtures used across the parts)
    _write, _ROLE, tag, gtag_html, _TB_ROLE, _VERIFY_ROLE,
    tb_tag, v_tag, REQ, _ac_body, _SPEC_TMPL, _spec, _req_with_verify)



class Rendering(unittest.TestCase):  # tested-by: ARCH-MAPDIAGRAMS-055  # tested-by: REQ-MAPDIAGRAMS-874, REQ-MAPDIAGRAMS-876, REQ-MAPDIAGRAMS-877, REQ-MAPDIAGRAMS-878
    def _data(self, title):
        return {"nodes": [{"id": "A-1", "layer": "bus", "status": "draft", "title": title,
                           "intent": "", "input": "", "output": "", "desc": "", "acc": [],
                           "deps": [], "used_by": [], "members": []}], "edges": []}

    def test_node_label_sanitizes_id(self):  # bug #9
        out = R._node_label({"id": "A<img>", "title": "T"})
        self.assertNotIn("<img>", out)
        self.assertIn("T", out)

    def test_map_into_missing_dir_no_crash(self):  # bug #21
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "new", "requirements")
            R.render_md(self._data("T"), missing)
            R.render_json(self._data("T"), missing)
            self.assertTrue(os.path.exists(os.path.join(missing, "_map.md")))
            self.assertTrue(os.path.exists(os.path.join(missing, "_map.json")))

    def _node(self, rid, status="baseline", layer="feature", members=None):
        return {"id": rid, "layer": layer, "status": status, "title": rid,
                "intent": "", "input": "i", "output": "o", "desc": "", "acc": [],
                "deps": [], "used_by": [], "members": members or []}

    def test_req_to_code_baseline_no_members_is_grey_not_red(self):  # verifies: REQ-MAPDIAGRAMS-877#CASE-3
        out = R._mermaid_req_to_code({"nodes": [self._node("AREA-FOO-001", status="baseline")], "edges": []})
        self.assertIn("#eee", out)        # muted grey: not-yet-linked baseline is expected
        self.assertNotIn("#fee", out)     # NOT the alarming red

    def test_req_to_code_confirmed_no_members_is_red(self):  # verifies: REQ-MAPDIAGRAMS-877#CASE-3
        out = R._mermaid_req_to_code({"nodes": [self._node("AREA-FOO-001", status="confirmed")], "edges": []})
        self.assertIn("#fee", out)        # enforced + unlinked = a real gap -> red

    def test_system_map_boxes_multinode_area_and_collapses_singletons(self):  # verifies: REQ-MAPDIAGRAMS-876#CASE-2  # verifies: ARCH-MAPDIAGRAMS-055#CASE-2
        data = {"nodes": [self._node("BUS-PATHS-001", layer="bus"),
                          self._node("BUS-RULES-002", layer="bus"),
                          self._node("AI-POSTMORTEM-001")], "edges": []}
        out = R._mermaid_system(data)
        self.assertIn('subgraph sg_BUS["BUS"]', out)     # multi-node area gets a box
        self.assertIn('subgraph sg_misc["misc"]', out)   # lone node collapses into misc
        self.assertIn("stroke-width:3px", out)           # bus stays marked

    def test_system_map_hides_edges_into_bus(self):  # verifies: REQ-MAPDIAGRAMS-876#CASE-3  # verifies: ARCH-MAPDIAGRAMS-055#CASE-2
        data = {"nodes": [self._node("BUS-PATHS-001", layer="bus"),
                          self._node("BUS-RULES-002", layer="bus"),
                          self._node("ETL-PIPELINE-001"), self._node("DASH-BUILD-001")],
                "edges": [["ETL-PIPELINE-001", "BUS-PATHS-001"],     # into bus -> hidden
                          ["ETL-PIPELINE-001", "DASH-BUILD-001"]]}   # feature->feature -> kept
        out = R._mermaid_system(data)
        self.assertNotIn("--> BUS_PATHS_001", out)
        self.assertIn("--> DASH_BUILD_001", out)

    def test_system_map_area_override_via_frontmatter(self):  # verifies: REQ-MAPDIAGRAMS-876#CASE-1
        a = self._node("RULESFLOW-REPORT-001"); a["area"] = "ANALYSIS"
        b = self._node("PLAYBOOK-ANALYSIS-001"); b["area"] = "ANALYSIS"
        out = R._mermaid_system({"nodes": [a, b], "edges": []})
        self.assertIn('subgraph sg_ANALYSIS["ANALYSIS"]', out)   # grouped by area:, not id prefix

    def test_area_subgraph_label_is_mermaid_escaped(self):  # bug: area-subgraph-unescaped-label
        # a `"` in an area: frontmatter value must not break the generated Mermaid
        # subgraph line -- route it through _mlabel like _mermaid_deps already does.
        a = self._node("A-X-001"); a['area'] = 'Foo"Bar'
        b = self._node("A-Y-002"); b['area'] = 'Foo"Bar'
        out = R._mermaid_system({"nodes": [a, b], "edges": []})
        self.assertNotIn('"Foo"Bar"', out)
        self.assertIn(R._mlabel('Foo"Bar'), out)

    def test_render_md_carries_legends(self):
        with tempfile.TemporaryDirectory() as d:
            R.render_md(self._data("T"), d)
            md = open(os.path.join(d, "_map.md"), encoding="utf-8").read()
            self.assertIn("area-level coupling", md)   # dependency-map legend line present

    def test_deps_is_area_level_overview(self):  # verifies: REQ-MAPDIAGRAMS-877#CASE-1  # verifies: REQ-MAPDIAGRAMS-877#CASE-2  # verifies: ARCH-MAPDIAGRAMS-055#CASE-3
        data = {"nodes": [self._node("BUS-PATHS-001", layer="bus"),
                          self._node("BUS-RULES-002", layer="bus"),
                          self._node("AI-X-001"), self._node("AI-Y-002")],
                "edges": [["AI-X-001", "BUS-PATHS-001"], ["AI-Y-002", "BUS-PATHS-001"]]}
        out = R._mermaid_deps(data)
        self.assertIn('a_BUS["BUS', out)                 # one node per area, with a count
        self.assertIn('a_AI["AI', out)
        self.assertEqual(out.count("a_AI --> a_BUS"), 1)  # two AI->bus edges aggregate to one
        self.assertNotIn("BUS_PATHS_001", out)           # no per-capability hub hairball

    def test_deps_area_ids_distinct_on_safeid_collision(self):  # bug: deps-safeid-collision
        # reuses the exact fixture test_area_subgraphs_distinct_ids_for_safeid_collision uses:
        # two area labels ("my-area" / "my_area") that both sanitize to the same _safe_id
        # must still get distinct node ids in _mermaid_deps, with a real edge (not a self-loop).
        data = {"nodes": [
            self._node("X-1"), self._node("X-2"),
            self._node("Y-1"), self._node("Y-2"),
        ], "edges": [["X-1", "Y-1"]]}
        for n in data["nodes"]:
            n["area"] = "my-area" if n["id"].startswith("X") else "my_area"
        out = R._mermaid_deps(data)
        import re as _re
        node_ids = _re.findall(r"^  (a_\w+)\[", out, _re.M)
        self.assertEqual(len(node_ids), len(set(node_ids)), "colliding area node ids:\n" + out)
        self.assertEqual(len(node_ids), 2)
        self.assertRegex(out, r"  a_\w+ --> a_\w+")
        # a real edge between the two DISTINCT ids, not a node looping to itself
        edge_line = next(l for l in out.splitlines() if "-->" in l)
        src, dst = edge_line.strip().split(" --> ")
        self.assertNotEqual(src, dst, "collapsed distinct areas into a self-loop:\n" + out)

    def test_risk_grouped_no_edges_flags_baseline(self):  # verifies: REQ-MAPDIAGRAMS-878#CASE-1
        data = {"nodes": [self._node("AI-X-001", status="baseline"),
                          self._node("AI-Y-002", status="baseline")],
                "edges": [["AI-X-001", "AI-Y-002"]]}
        out = R._mermaid_risk(data)
        self.assertIn("unreviewed", out)
        self.assertIn('subgraph sg_AI["AI"]', out)       # grouped by area
        self.assertNotIn("-->", out)                     # Risk shows no edges

    def test_risk_table_has_scripted_recommendation(self):  # verifies: REQ-MAPDIAGRAMS-878#CASE-2
        with tempfile.TemporaryDirectory() as d:
            R.render_md({"nodes": [self._node("AI-X-001", status="baseline")], "edges": []}, d)
            md = open(os.path.join(d, "_map.md"), encoding="utf-8").read()
            self.assertIn("recommendation", md)            # new table column
            self.assertIn("promote to `confirmed`", md)    # unreviewed advice text


class Findings(unittest.TestCase):  # tested-by: ARCH-FINDINGS-010  # tested-by: REQ-FINDINGS-853  # tested-by: REQ-FINDINGS-854  # tested-by: REQ-FINDINGS-855
    def _run(self, d, raw=False):
        reqs = R.load_requirements(os.path.join(d, "requirements"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_findings(reqs, os.path.join(d, "requirements"), raw=raw)
        md = open(os.path.join(d, "requirements", "_findings.md"), encoding="utf-8").read()
        return md, buf.getvalue()

    def test_aggregates_verify_intent_grouped(self):  # verifies: REQ-FINDINGS-853#CASE-1  # verifies: REQ-FINDINGS-854#CASE-1  # verifies: REQ-FINDINGS-854#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["swallowed except, intended?", "magic 1.05, bug?"]))
            md, out = self._run(d)
            self.assertIn("AREA-X-001", md)
            self.assertIn("magic 1.05", md)
            self.assertIn("2 open finding(s) across 1 requirement(s)", out)

    def test_skips_none_placeholder(self):  # verifies: REQ-FINDINGS-853#CASE-3  # verifies: REQ-FINDINGS-854#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-Y-001.md"),
                   _req_with_verify("AREA-Y-001", ["None — behavior is unambiguous and matches the contract."]))
            md, out = self._run(d)
            self.assertIn("0 open finding(s)", out)
            self.assertIn("_No open findings._", md)

    def test_skips_the_scaffolds_own_authoring_hint(self):  # verifies: REQ-FINDINGS-853#CASE-4
        """`draft` used to list a prose file's headings under Verify intent as an
        authoring hint. They are bullets, so each heading was collected as an open
        question -- 21 drafted files reported 103 findings, 82 of them the hint."""
        with tempfile.TemporaryDirectory() as d:
            body = (
                "---\nid: AREA-H-001\nstatus: baseline\nlayer: feature\n---\n\n# Cap\n\n"
                "## Description\n- shall do the thing.\n\n"
                "## Verify intent (open questions for the human)\n"
                "- TODO: which source sections are normative vs illustrative?\n\n"
                "Source sections detected (authoring hint, not the contract):\n"
                "  - Serverul\n  - Primul contact\n  - Swap\n\n"
                "## Cases\nCASE-1\n")
            _write(os.path.join(d, "requirements", "AREA-H-001.md"), body)
            md, out = self._run(d)
            self.assertIn("1 open finding(s) across 1 requirement(s)", out)
            self.assertIn("which source sections are normative", md)
            self.assertNotIn("Serverul", md)
            self.assertNotIn("Primul contact", md)

    def test_triage_sidecar_orders_confirmed_bugs_first(self):  # verifies: REQ-FINDINGS-855#CASE-1  # verifies: REQ-FINDINGS-855#CASE-2  # verifies: REQ-FINDINGS-855#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["magic 1.05, bug?", "swallowed except, intended?"]))
            _write(os.path.join(d, "requirements", R.FINDINGS_SIDECAR), json.dumps({
                "generated_at": "2026-06-02T00:00:00Z",
                "items": [
                    {"req_id": "AREA-X-001", "finding": "swallowed except", "classification": "USER_DECISION", "severity": "low"},
                    {"req_id": "AREA-X-001", "finding": "magic 1.05", "classification": "REAL_BUG", "severity": "high", "location": "f.py:10", "fix": "read from yaml"},
                ]}))
            md, out = self._run(d)
            self.assertLess(md.index("Confirmed bugs"), md.index("Your call"))
            self.assertIn("[HIGH]", md)
            self.assertIn("`f.py:10`", md)
            self.assertIn("1 confirmed bug(s)", out)

    def test_raw_flag_ignores_sidecar(self):  # verifies: REQ-FINDINGS-854#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["magic 1.05, bug?"]))
            _write(os.path.join(d, "requirements", R.FINDINGS_SIDECAR), json.dumps({
                "items": [{"req_id": "AREA-X-001", "finding": "magic 1.05", "classification": "REAL_BUG", "severity": "high"}]}))
            md, _ = self._run(d, raw=True)
            self.assertNotIn("Confirmed bugs", md)
            self.assertIn("Open findings", md)

    def test_staleness_note_when_counts_differ(self):  # verifies: REQ-FINDINGS-855#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["a?", "b?", "c?"]))  # 3 raw
            _write(os.path.join(d, "requirements", R.FINDINGS_SIDECAR), json.dumps({
                "items": [{"req_id": "AREA-X-001", "finding": "a", "classification": "INTENTIONAL"}]}))  # 1 triaged
            md, _ = self._run(d)
            self.assertIn("WARN", md)
            self.assertIn("re-run the AI triage", md)

    def test_check_reports_open_findings(self):  # tested-by: REQ-CHECK-832  # verifies: REQ-CHECK-832#CASE-1  # verifies: REQ-FINDINGS-856#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["magic 1.05, bug?"]))
            reqs = R.load_requirements(os.path.join(d, "requirements"))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, {}, os.path.join(d, "requirements")), False)
            self.assertIn("1 open verify-intent finding(s)", buf.getvalue())


# ---- regression tests for the 2026-06-02 audit fixes + previously-untested code ----

def _export_doc_for(node):
    """Serialize a single node dict (defaults filled) via _build_json_text, parse back."""
    base = {"id": "A-1", "layer": "feature", "status": "draft", "title": "t", "intent": "",
            "input": "", "output": "", "desc": "", "acc": [], "deps": [], "used_by": [],
            "members": [], "contract": [], "verify": [], "notes": [], "current_impl": [],
            "accept": "", "risks": []}
    base.update(node)
    return json.loads(R._build_json_text({"nodes": [base], "edges": []}))


# Every key `_build_map_data` puts on a node, frozen. The engine -> _map.json ->
# viewer seam fails SILENTLY by construction: `adaptNode` (app/src/lib/loadData.js)
# turns any key it cannot find into []/""/null, so a dropped field renders as an
# empty panel and nothing goes red. It has happened: `roadmap` and `history` were
# emitted, carried on window.__REQMAP_DATA__ and thrown away by the adapter for two
# releases (v7.6.0-v7.8.0) with every check green — see loadData.js:78-84. No test
# asserted the shape of the payload, only the values of a few fields, so nothing
# could have caught it. This is that test: change the emitted set and it goes red,
# which forces the change to be deliberate and to reach the adapter in the same
# commit.
_NODE_KEYS = frozenset((
    "id", "area", "title", "layer", "level", "status",
    "intent", "contract", "notes", "current_impl", "verify",
    "accept", "desc", "input", "output",
    "depends_on", "used_by", "satisfies", "satisfied_by",
    "members", "risks", "test_exempt", "milestone", "priority",
))
# Attached AFTER _build_map_data by cmd_map, so they are absent here and optional in
# the committed file: _attach_ac_coverage adds clauses/covered only for a requirement
# with labelled criteria, _attach_translations adds i18n only for a translated one.
_NODE_KEYS_ATTACHED_LATER = frozenset(("clauses", "covered", "i18n", "acc"))


class MapPayloadShape(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-870
    def _node(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            return R._build_map_data(R.load_requirements(rd), {})

    def test_node_carries_exactly_the_frozen_key_set(self):  # verifies: ARCH-MAP-007#CASE-1
        node = self._node()["nodes"][0]
        got = set(node)
        self.assertEqual(
            got, set(_NODE_KEYS),
            "the per-node key set changed: added {} / dropped {}. A consumer reads "
            "these by name and fails open on a missing one, so update loadData.js "
            "(and this set) in the same commit."
            .format(sorted(got - _NODE_KEYS) or "-", sorted(_NODE_KEYS - got) or "-"))

    def test_coverage_and_i18n_keys_are_attached_after_build(self):  # verifies: ARCH-MAP-007#CASE-1
        # guards the split itself: if one of these ever moves into _build_map_data the
        # frozen set above is wrong, and this names which one rather than failing twice.
        node = self._node()["nodes"][0]
        self.assertEqual(set(node) & _NODE_KEYS_ATTACHED_LATER, set())

    def test_build_map_data_top_level_keys(self):  # verifies: REQ-MAP-870#CASE-2
        # cmd_map enriches this with repo/engine_version/todos/roadmap/history/
        # commands/design/health/planning; the graph itself is these three.
        self.assertEqual(set(self._node()), {"nodes", "edges", "upstream_edges"})


class JsonExport(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-870
    def test_export_writes_nodes_edges_and_version(self):  # verifies: REQ-MAP-870#CASE-1  # verifies: REQ-MAP-870#CASE-2  # verifies: ARCH-MAP-007#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(R.load_requirements(rd), {}, rd), d)
            doc = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
            self.assertEqual(doc["engine_version"], R.MAP_ENGINE_VERSION)
            self.assertEqual(len(doc["nodes"]), 1)
            self.assertIn("edges", doc)

    def test_export_includes_parsed_todos(self):  # bug: export-drops-todos  # verifies: REQ-MAP-871#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(d, "TODO.md"), "## v1.14\n- [ ] Ship it | lane: feature\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(R.load_requirements(rd), {}, rd), d)
            doc = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
            self.assertEqual([t["name"] for t in doc["todos"]], ["Ship it"])

    def test_export_includes_targets_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(rd, "_planning.json"), json.dumps({
                "scores": {"health": 95, "design": 80},   # removed keys: ignored, not exported
                "lanes": ["Tech"],
                "bars": [{"title": "Ship planning", "lane": "Tech", "start": "2026-10-01", "end": "2026-10-15"}],
                "milestones": {"v2.0": {
                    "due": "2026-12-31",
                    "label": "Ship planning",
                    "items": ["Future panel"],
                }},
            }))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(R.load_requirements(rd), {}, rd), d)
            doc = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
            self.assertNotIn("scores", doc["planning"])
            self.assertEqual(doc["planning"]["milestones"]["v2.0"]["due"], "2026-12-31")
            self.assertNotIn("items", doc["planning"]["milestones"]["v2.0"])
            self.assertEqual(doc["planning"]["bars"][0]["start"], "2026-10-01")
            self.assertEqual(doc["planning"]["lanes"], ["Tech"])
            self.assertNotIn("targets", doc)          # the legacy alias left in v8.3.0

    def test_hostile_title_roundtrips_as_data_not_injection(self):  # bug: id-js-string-breakout-xss  # verifies: REQ-MAP-870#CASE-6  # verifies: ARCH-MAP-007#CASE-3
        doc = _export_doc_for({"id": "a</script><img src=x>", "title": "x\");alert(1)//"})
        # the value survives intact as a JSON string — there is no markup context to break out of
        self.assertEqual(doc["nodes"][0]["id"], "a</script><img src=x>")
        self.assertEqual(doc["nodes"][0]["title"], "x\");alert(1)//")

    def test_node_with_no_members_has_empty_list(self):  # verifies: REQ-MAP-870#CASE-3  # verifies: ARCH-MAP-007#CASE-3
        self.assertEqual(_export_doc_for({"id": "A-1"})["nodes"][0]["members"], [])

    def test_the_dependency_list_is_emitted_once(self):  # verifies: REQ-MAP-870#CASE-7
        # Emitted under the documented name only; `deps` was the same list twice over.
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "A-DEP-002.md"),
                   REQ.format(id="A-DEP-002", status="confirmed", layer="bus", extra="", title="D"))
            _write(os.path.join(rd, "A-USE-001.md"),
                   REQ.format(id="A-USE-001", status="confirmed", layer="feature",
                              extra="depends_on: [A-DEP-002]\n", title="U"))
            node = next(n for n in R._build_map_data(R.load_requirements(rd), {})["nodes"]
                        if n["id"] == "A-USE-001")
        self.assertEqual(node["depends_on"], ["A-DEP-002"])
        self.assertNotIn("deps", node)

    def test_json_carries_repo_field(self):  # dynamic repo name in viewer header  # verifies: REQ-MAP-870#CASE-5  # verifies: REQ-MAP-871#CASE-1
        doc = json.loads(R._build_json_text(
            {"repo": "owner/proj", "nodes": [], "edges": []}))
        self.assertEqual(doc["repo"], "owner/proj")

    def test_json_repo_is_null_when_absent(self):  # verifies: REQ-MAP-871#CASE-2
        # _build_json_text reads data.get("repo") — a graph without it stays valid (repo: null)
        doc = json.loads(R._build_json_text({"nodes": [], "edges": []}))
        self.assertIsNone(doc["repo"])


class RepoName(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-871
    def test_falls_back_to_dir_name_without_git_remote(self):
        # a bare temp dir has no remote.origin.url -> directory basename is used,
        # and the call never raises (git absent / not a checkout must be tolerated)
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(R._repo_name(d), os.path.basename(os.path.abspath(d)))

    def test_repo_excluded_from_freshness_diff(self):
        # the git-derived repo line differs across forks -> map --check must ignore it
        a = R._build_json_text({"repo": "owner/a", "nodes": [], "edges": []})
        b = R._build_json_text({"repo": "fork/b", "nodes": [], "edges": []})
        self.assertNotEqual(a, b)
        self.assertEqual(R._strip_generated(a), R._strip_generated(b))

    def test_env_override_wins_over_git(self):
        # REQMAP_REPO lets a private dev repo emit a public slug (or "" for none)
        # instead of leaking its own remote into the inlined map data
        old = os.environ.get("REQMAP_REPO")
        try:
            with tempfile.TemporaryDirectory() as d:
                os.environ["REQMAP_REPO"] = "owner/public"
                self.assertEqual(R._repo_name(d), "owner/public")
                os.environ["REQMAP_REPO"] = ""          # explicit blank -> no repo
                self.assertIsNone(R._repo_name(d))
        finally:
            if old is None:
                os.environ.pop("REQMAP_REPO", None)
            else:
                os.environ["REQMAP_REPO"] = old


class ViewerInject(unittest.TestCase):  # tested-by: ARCH-VIEWERFILE-074  # tested-by: REQ-VIEWER-940  # tested-by: REQ-VIEWER-941
    def test_marker_replaced_with_inline_data(self):  # verifies: REQ-VIEWER-940#CASE-5  # verifies: REQ-VIEWER-940#CASE-6
        out = R._inject_viewer("<head><!--REQMAP_DATA--></head>",
                               {"nodes": [{"id": "A-1"}], "edges": []})
        self.assertNotIn("<!--REQMAP_DATA-->", out)   # marker consumed
        self.assertIn("window.__REQMAP_DATA__=", out) # data assigned
        self.assertIn('"A-1"', out)                   # node present

    def test_script_close_in_field_is_escaped(self):  # bug: viewer-data-script-breakout-xss  # verifies: REQ-VIEWER-941#CASE-2
        out = R._inject_viewer("<!--REQMAP_DATA-->",
                               {"nodes": [{"id": "a</script><img src=x>"}], "edges": []})
        self.assertNotIn("</script><img", out)        # NOT a raw breakout
        self.assertIn("<\\/script>", out)             # escaped form instead

    def test_render_html_writes_self_contained_file(self):  # verifies: REQ-VIEWER-940#CASE-1  # verifies: REQ-VIEWER-940#CASE-2
        if not os.path.exists(R._viewer_template_path()):
            self.skipTest("viewer template not vendored beside the engine")
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            out = R.render_html({"nodes": [{"id": "A-1"}], "edges": []}, rd)
            self.assertIsNotNone(out)
            self.assertTrue(os.path.exists(out))
            html = open(out, encoding="utf-8").read()
            self.assertIn("window.__REQMAP_DATA__=", html)
            self.assertNotIn("<!--REQMAP_DATA-->", html)


class MapInternals(unittest.TestCase):  # tested-by: ARCH-MAP-007, ARCH-CONTEXT-048  # tested-by: REQ-CONTEXT-835  # tested-by: REQ-MAP-873
    def _node(self, members):
        return {"id": "A-FOO-001", "layer": "feature", "status": "confirmed", "title": "T",
                "members": members}

    # ARCH-MAP-007 CASE-4/CASE-5. In the atomic form the `>` quote IS the single
    # contract clause, so emitting it as `intent` too printed one sentence twice on
    # every surface — 588 of 646 nodes, 91% of the corpus, before this.
    _ATOMIC = ("---\nid: REQ-A-001\nstatus: draft\nform: atomic\nlayer: feature\n---\n\n"
               "# A lock sidecar that exists\n\n"
               "> A lock sidecar that exists on disk but is not git-tracked is a `WARN`.\n\n"
               "Scenario: an untracked lock is flagged\n"
               "  Given  a lock written but never added\n"
               "  When   the gate runs\n"
               "  Then   it names the file\n")

    def test_atomic_intent_is_empty_because_it_is_the_contract(self):  # verifies: ARCH-MAP-007#CASE-4  # verifies: REQ-MAP-873#CASE-1
        self.assertEqual(R._distinct_intent(self._ATOMIC), "")
        self.assertTrue(R._from_any(R._bullets, self._ATOMIC, R.CONTRACT_LABELS),
                        "the clause must survive under contract, only the duplicate goes")

    def test_sectioned_intent_survives_when_it_is_real_rationale(self):  # verifies: ARCH-MAP-007#CASE-5  # verifies: REQ-MAP-873#CASE-2
        body = ("# T\n\n## Description\n"
                "> Specs rot when nobody updates them, so this guards that.\n"
                "- `gate` reports a dangling tag as an error.\n")
        self.assertIn("Specs rot", R._distinct_intent(body))

    def test_intent_dedupe_ignores_only_whitespace_differences(self):  # verifies: REQ-MAP-873#CASE-3
        # a quote re-wrapped across lines is still the same sentence as the clause
        wrapped = self._ATOMIC.replace(
            "> A lock sidecar that exists on disk but is not git-tracked is a `WARN`.",
            "> A lock sidecar that exists on disk but is not\n> git-tracked is a `WARN`.")
        self.assertEqual(R._distinct_intent(wrapped), "")

    def test_req_to_code_collapses_line_range(self):  # bug: mermaid-req-to-code-line-range-untested  # verifies: REQ-MAPDIAGRAMS-877#CASE-4
        out = R._mermaid_req_to_code({"nodes": [self._node(
            [{"role": "implements", "loc": "src/a.py:10"},
             {"role": "implements", "loc": "src/a.py:25"}])], "edges": []})
        self.assertIn("src/a.py:10-25", out)            # min-max collapsed

    def test_req_to_code_single_member_no_range(self):
        out = R._mermaid_req_to_code({"nodes": [self._node(
            [{"role": "implements", "loc": "src/a.py:10"}])], "edges": []})
        self.assertIn("src/a.py:10", out)
        self.assertNotIn("src/a.py:10-10", out)

    def test_mlabel_neutralizes_mermaid_metacharacters(self):  # bug: mlabel-sanitizer-set-partially-tested
        out = R._mlabel("a|b[c]{d}`e`\\f")
        for ch in "|[]{}`\\":
            self.assertNotIn(ch, out)

    def test_first_quote_single_line(self):
        self.assertEqual(R._first_quote("# T\n\n> one line why.\n\n## WHAT — Contract\n- x."),
                         "one line why.")

    def test_first_quote_gathers_multiline_why(self):  # verifies: REQ-SHOW-917#CASE-6
        body = "# T\n\n> why line one\n> why line two\n> why line three\n\n## WHAT — Contract\n- x."
        self.assertEqual(R._first_quote(body), "why line one why line two why line three")

    def test_first_quote_stops_at_first_block(self):
        # a later blockquote (e.g. an Example story) must NOT join the intent
        body = "# T\n\n> the why.\n\n## Example\n> a different story.\n"
        self.assertEqual(R._first_quote(body), "the why.")

    def test_first_quote_skips_fenced(self):
        self.assertEqual(R._first_quote("# T\n```\n> not a quote\n```\n> real why.\n"),
                         "real why.")

    def test_dangling_depends_on_emits_no_edge(self):  # bug: build-map-data-phantom-edge
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "A-B-001.md"),
                   "---\nid: A-B-001\nstatus: confirmed\nlayer: feature\n"
                   "depends_on: [NOPE-X-999]\n---\n\n# T\n")
            data = R._build_map_data(R.load_requirements(rd), {})
            self.assertEqual(data["edges"], [],
                             "a dangling depends_on target must not emit a phantom edge")

    def test_bullets_anchored_skips_commentary_heading(self):  # bug: bullets-substring-heading
        body = ("## Notes — contract caveats\n- a mere note\n"
                "## WHAT — Contract\n- real clause one\n- real clause two\n")
        self.assertEqual(R._bullets(body, "contract"),
                         ["real clause one", "real clause two"])

    def test_bullets_matches_where_prefixed_section(self):  # regression: WHERE prefix
        # _heading_label_is must accept WHERE/WHY prefixes so _bullets still finds
        # the Current-implementation section after switching off substring matching
        body = "## WHERE — Current implementation\n- impl detail\n"
        self.assertEqual(R._bullets(body, "current implementation"), ["impl detail"])

    def test_section_keeps_real_leading_dash_content(self):  # bug: section-lstrip-char-class
        # lstrip("- ") strips a CHARACTER CLASS, not the literal two-char "- " bullet
        # marker -- it must not also eat a real leading "-1" that follows the marker.
        body = "## WHAT — Contract\n- -1 means error\n"
        self.assertEqual(R._section(body, "contract"), "-1 means error")

    def test_context_group_extracts_bold_subgroup(self):  # verifies: REQ-CONTEXT-835#CASE-2
        body = ("## Context (non-binding)\n"
                "**Notes**\n- a footgun\n- a second footgun\n"
                "**Current implementation**\n- lives in foo.py\n")
        self.assertEqual(R._context_group(body, "notes"), ["a footgun", "a second footgun"])
        self.assertEqual(R._context_group(body, "current implementation"), ["lives in foo.py"])

    def test_context_group_empty_when_no_context_section(self):  # verifies: REQ-CONTEXT-835#CASE-4
        # a legacy-schema file (no Context section at all) must not spuriously match
        body = "## WHAT — Notes & known limitations (informative)\n- old-style note\n"
        self.assertEqual(R._context_group(body, "notes"), [])

    def test_context_group_ignores_unrelated_subgroup(self):  # verifies: REQ-CONTEXT-835#CASE-3
        body = "## Context (non-binding)\n**Example**\n- a story\n"
        self.assertEqual(R._context_group(body, "notes"), [])

    def test_map_data_notes_falls_back_to_context_group(self):  # verifies: REQ-CONTEXT-835#CASE-2
        # a requirement using ONLY the new consolidated Context section must still
        # populate _map.json's notes/current_impl fields — the fallback this ADR-0017
        # migration exists to guarantee, so the fields never go silently empty.
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "A-B-001.md"),
                   "---\nid: A-B-001\nstatus: confirmed\nlayer: feature\n---\n\n"
                   "# T\n\n## Context (non-binding)\n"
                   "**Notes**\n- a footgun\n"
                   "**Current implementation**\n- lives in foo.py\n")
            data = R._build_map_data(R.load_requirements(rd), {})
            node = data["nodes"][0]
            self.assertEqual(node["notes"], ["a footgun"])
            self.assertEqual(node["current_impl"], ["lives in foo.py"])

    def test_map_data_notes_prefers_legacy_heading_over_context(self):  # verifies: REQ-CONTEXT-835#CASE-4
        # an old-schema file must keep working completely unchanged — the fallback
        # only fires when the legacy heading is absent.
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "A-B-001.md"),
                   "---\nid: A-B-001\nstatus: confirmed\nlayer: feature\n---\n\n"
                   "# T\n\n## WHAT — Notes & known limitations (informative)\n"
                   "- legacy note\n")
            data = R._build_map_data(R.load_requirements(rd), {})
            self.assertEqual(data["nodes"][0]["notes"], ["legacy note"])

    def test_section_detection_and_drift_hash_agree_on_prefixes(self):  # bug: heading-re-out-of-sync
        # _has_section (gate, via _heading_label_is) and binding_hash (drift, via
        # _NORMATIVE_HEADING_RE) must use the same prefix set, else a WHY/WHERE-
        # prefixed normative heading passes the gate but is left out of the hash
        body = "## WHY — Contract\n- shall do X\n"
        self.assertTrue(R._has_section(body, "contract"))
        self.assertNotEqual(R.binding_hash(body), R.binding_hash("# empty\n"),
                            "a gate-accepted contract heading must be covered by the drift hash")

    def test_grouped_areas_no_duplicate_misc(self):  # bug: grouped-areas-misc-collision
        nodes = [{"id": "M1", "area": "misc"}, {"id": "M2", "area": "misc"},
                 {"id": "S1", "area": "solo"}]   # solo is a singleton -> misc bucket
        groups = R._grouped_areas(nodes)
        labels = [a for a, _ in groups]
        self.assertEqual(labels.count("misc"), 1, "must not emit two 'misc' groups")
        misc_nodes = next(ns for a, ns in groups if a == "misc")
        self.assertEqual({n["id"] for n in misc_nodes}, {"M1", "M2", "S1"})


class TriageFolding(unittest.TestCase):  # tested-by: ARCH-FINDINGS-010
    def test_unknown_classification_folds_into_user_decision(self):  # bug: triage-unknown-classification-dropped
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["mystery finding, bug?"]))
            _write(os.path.join(rd, R.FINDINGS_SIDECAR), json.dumps({
                "items": [{"req_id": "AREA-X-001", "finding": "mystery finding",
                           "classification": "WONTFIX"}]}))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_findings(R.load_requirements(rd), rd, raw=False)
            md = open(os.path.join(rd, "_findings.md"), encoding="utf-8").read()
            self.assertIn("mystery finding", md)            # NOT silently dropped
            self.assertIn("1 product/config decision", md)  # counted in a real bucket

    def test_malformed_sidecar_summary_not_misleading(self):  # bug: findings-misleading-triaged-count
        """A sidecar that is valid JSON but whose `items` is not a list falls back
        to raw rendering; the summary must NOT claim a triage view was rendered."""
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["a finding"]))
            _write(os.path.join(rd, R.FINDINGS_SIDECAR), json.dumps({"items": {}}))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_findings(R.load_requirements(rd), rd, raw=False)
            self.assertNotIn("triaged", buf.getvalue(),
                             "raw fallback must not claim a triage view was rendered")


class HealthLine(unittest.TestCase):  # tested-by: ARCH-CHECK-006
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
            return code, buf.getvalue()

    def test_summary_reports_confirmed_count(self):  # verifies: REQ-CHECK-832#CASE-3
        files = {
            "AREA-A-001.md": _req_with_verify("AREA-A-001", ["q?"]).replace(
                "status: baseline", "status: confirmed"),
            "AREA-B-002.md": _req_with_verify("AREA-B-002", ["q?"]),
            "impl.py": tag("AREA-A-001") + "\n",   # member so the confirmed req does not error
        }
        code, out = self._check(files)
        self.assertIn("1 confirmed", out)
        self.assertIn("0 legacy-schema", out)   # both reqs use the new schema
        self.assertEqual(code, 0)

    def test_legacy_schema_is_flagged_nonblocking(self):
        # verifies: REQ-CHECK-830#CASE-7  # verifies: REQ-CHECK-831#CASE-1
        # verifies: REQ-CHECK-831#CASE-2
        # a legacy-schema requirement (the Input/Output triad) must warn but not error
        legacy = REQ.format(id="AREA-L-001", status="baseline", layer="feature",
                            extra="", title="Legacy") + "\n## Input\n- x\n## Output\n- y\n"
        code, out = self._check({"AREA-L-001.md": legacy})
        self.assertIn("legacy schema", out)
        self.assertIn("findings` is inactive", out)
        self.assertIn("1 legacy-schema", out)
        self.assertEqual(code, 0)   # non-blocking


class RiskSignals(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-872
    def _node(self, **kw):
        n = {"status": "baseline", "members": [], "verify": [], "test_exempt": None}
        n.update(kw)
        return n

    def test_untested_fires_when_implemented_but_no_test(self):
        n = self._node(members=[{"role": "implements", "loc": "a.py:1"}])
        self.assertIn("untested", R._risk_signals(n))

    def test_untested_silent_with_tested_by(self):
        n = self._node(members=[{"role": "implements", "loc": "a.py:1"},
                                {"role": "tested-by", "loc": "t.py:1"}])
        self.assertNotIn("untested", R._risk_signals(n))

    def test_untested_not_fired_for_unimplemented_draft(self):  # gated on implements
        n = self._node(members=[])
        self.assertNotIn("untested", R._risk_signals(n))

    def test_test_exempt_suppresses_untested(self):
        n = self._node(members=[{"role": "implements", "loc": "a.py:1"}], test_exempt="manual QA")
        self.assertNotIn("untested", R._risk_signals(n))

    def test_unverified_intent_fires_on_open_findings(self):
        n = self._node(verify=["is the empty-string fallback intended?"])
        self.assertIn("unverified-intent", R._risk_signals(n))

    def test_unverified_intent_ignores_none_placeholder(self):  # mirror collect_findings
        n = self._node(verify=["None — prompt is unambiguous."])
        self.assertNotIn("unverified-intent", R._risk_signals(n))

    def test_unimplemented_uses_implements_role_not_raw_members(self):  # bug-hunt #8
        # confirmed with ONLY a tested-by member (no implements) must flag 'unimplemented',
        # mirroring the gate which errors on a confirmed req lacking an implements: tag
        n = self._node(status="confirmed", members=[{"role": "tested-by", "loc": "t.py:1"}])
        self.assertIn("unimplemented", R._risk_signals(n))
        # with an implements member it must NOT flag unimplemented
        ok = self._node(status="confirmed", members=[{"role": "implements", "loc": "x.py:1"}])
        self.assertNotIn("unimplemented", R._risk_signals(ok))

    def test_unimplemented_exempts_need_layer(self):  # mirror the gate: a need is satisfied-by, not implemented
        need = self._node(status="confirmed", layer="need", members=[])
        self.assertNotIn("unimplemented", R._risk_signals(need))
        # exemption is layer-scoped: a confirmed feature with no implements still flags
        feat = self._node(status="confirmed", layer="feature", members=[])
        self.assertIn("unimplemented", R._risk_signals(feat))

    def test_bullets_grabs_first_matching_section_only(self):  # bug-hunt #1
        body = ("# T\n\n## WHAT — Contract\n- real.\n\n"
                "## Notes — contract caveats\n- not normative.\n")
        self.assertEqual(R._bullets(body, "contract"), ["real."])

    def test_bullets_folds_multiline_continuation(self):  # a wrapped clause must not be truncated to its first line  # verifies: REQ-MAP-872#CASE-1
        body = ("# T\n\n## WHAT — Contract\n"
                "- It shall do the first thing across\n"
                "  a wrapped second line and\n"
                "  a third line.\n"
                "- A short clause.\n")
        self.assertEqual(
            R._bullets(body, "contract"),
            ["It shall do the first thing across a wrapped second line and a third line.",
             "A short clause."])

    def test_bullets_skips_clause_group_labels(self):  # voice rule 6: **What it creates**  # verifies: REQ-MAP-872#CASE-2
        # a bold-only line groups the clauses below it; folding it into the bullet above
        # would append the next group's title to the previous group's last clause
        body = ("# T\n\n## WHAT — Contract\n"
                "**What it creates**\n"
                "- `init` creates the folder.\n\n"
                "**What it prints**\n"
                "- `init` prints one next command.\n")
        self.assertEqual(
            R._bullets(body, "contract"),
            ["`init` creates the folder.", "`init` prints one next command."])

    # --- clause-group labels are positional, not shape-matched -------------------
    # A wrapped clause may legitimately open and close on bold spans. Shape-matching
    # `**...**` swallowed such a line whole; the four tests below pin the boundary
    # from both sides. The two tests above were individually green while this exact
    # composite case was broken, so each of these targets their intersection.

    # Verbatim from a requirement whose join predicate lost its "containment" half:
    # the wrapped line both opens on **containment** and closes on **sanity**.
    _WRAPPED_BOLD_BOTH_ENDS = (
        "# T\n\n## WHAT — Contract\n"
        "- **The per-ticket stamp is a named artifact with a named join predicate.** Stage 6\n"
        "  joins it by ticket (first row per ticket wins) and shall use it ONLY when both hold:\n"
        "  **containment** `h4_bar_time + 4h <= entry_dt < h4_bar_time + 8h`, and **sanity**\n"
        "  `h4_high > 0 and h4_low > 0`. On any failure it falls back to the 5M resample.\n")

    def test_bullets_keeps_wrapped_clause_bounded_by_bold_spans(self):  # verifies: REQ-MAP-872#CASE-3
        clause = " ".join(R._bullets(self._WRAPPED_BOLD_BOTH_ENDS, "contract"))
        self.assertIn("containment", clause)     # the half that used to vanish
        self.assertIn("sanity", clause)
        self.assertIn("h4_bar_time + 4h", clause)

    def test_bullets_folds_indented_line_that_is_entirely_bold(self):  # verifies: REQ-MAP-872#CASE-3
        # the residual shape: a continuation whose whole content is one bold span.
        # Indented, so it continues the clause above rather than labelling a group.
        body = ("# T\n\n## WHAT — Contract\n"
                "- The stamp is written for the attached chart's own symbol,\n"
                "  **and for no other.**\n")
        self.assertEqual(
            R._bullets(body, "contract"),
            ["The stamp is written for the attached chart's own symbol, **and for no other.**"])

    def test_bullets_skips_bold_italic_group_label(self):
        # ***Label*** is a label too — a narrower bold-span pattern would fold it into
        # the bullet above, which is the defect the label branch exists to prevent.
        body = ("# T\n\n## WHAT — Contract\n"
                "***Example Structure***\n"
                "- `init` creates the folder.\n")
        self.assertEqual(R._bullets(body, "contract"), ["`init` creates the folder."])

    def test_is_label_line_is_positional(self):
        self.assertTrue(R._is_label_line("**What it creates**"))
        self.assertTrue(R._is_label_line("***Example Structure***"))
        self.assertFalse(R._is_label_line("  **containment** `x <= y`, and **sanity**"))
        self.assertFalse(R._is_label_line("  **and for no other.**"))
        self.assertFalse(R._is_label_line("- **A bullet.** Prose follows."))

    def test_bullets_accounts_for_every_prose_line(self):
        """Containment invariant: every non-blank, non-comment line inside the section
        either opens a clause, folds into one, or is a column-0 label. Nothing is
        silently discarded — the property a shape-specific test cannot assert."""
        bodies = [
            self._WRAPPED_BOLD_BOTH_ENDS,
            ("# T\n\n## WHAT — Contract\n"
             "**Group one**\n"
             "- First clause spanning\n"
             "  **a bold-opened** wrap that ends on **another bold span**\n"
             "***Group two, italicised***\n"
             "- Second clause.\n"
             "  **wholly bold continuation**\n"),
            ("# T\n\n## WHAT — Contract\n"
             "- Clause with *single* emphasis and **inline bold** mid-sentence.\n"
             "\t**tab-indented continuation**\n"),
        ]
        for body in bodies:
            with self.subTest(body=body[:48]):
                section = R._section_raw(body, "contract").split("\n")
                prose = [ln for ln in section if ln.strip() and not ln.strip().startswith("<!--")]
                labels = [ln for ln in prose if R._is_label_line(ln)]
                joined = " ".join(R._bullets(body, "contract"))
                for ln in prose:
                    if ln in labels:
                        continue
                    payload = ln.strip().lstrip("-").strip()
                    self.assertIn(payload, joined,
                                  "line silently dropped from the parsed contract: %r" % ln)

    def test_over_scoped_group_count_ignores_indented_bold_wraps(self):
        """The lint's group counter shares _is_label_line with _bullets. Counting off
        stripped lines made every bold-bounded wrap a group, inflating contract_n —
        and `over-scoped` is an ERROR under --strict."""
        body = ("# T\n\n## WHAT — Contract\n"
                "**Only group**\n"
                "- A clause that wraps onto\n"
                "  **a bold-opened** line ending in **a bold span**\n"
                "  and another **bold-opened** wrap ending in **more bold**\n")
        section = R._section_raw(body, "contract").split("\n")
        self.assertEqual(sum(1 for ln in section if R._is_label_line(ln)), 1)

    def test_member_roles_handles_tuple_and_dict_shapes(self):
        self.assertEqual(R._member_roles([("implements", "a.py", 1)]), ["implements"])
        self.assertEqual(R._member_roles([{"role": "tested-by", "loc": "t.py:1"}]), ["tested-by"])

    def test_new_signals_have_advice(self):  # else RISK_ADVICE[s] KeyErrors in map
        for s in ("untested", "unverified-intent"):
            self.assertIn(s, R.RISK_ADVICE)

    def test_map_renders_new_signals_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            # implemented (tagged in code) but untested + has an open verify-intent item
            _write(os.path.join(rd, "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["swallowed error — bug?"]))
            _write(os.path.join(d, "x.py"), tag("AREA-X-001") + "\n")
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(reqs, members, rd), d)   # isolated root: never the real repo docs/
            md = open(os.path.join(rd, "_map.md"), encoding="utf-8").read()
            self.assertIn("untested", md)
            self.assertIn("unverified-intent", md)


class MapFreshness(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-871
    def _map(self, d, check=False):
        rd = os.path.join(d, "requirements")
        reqs = R.load_requirements(rd)
        members = R.scan_members(d, rd)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_map(R.Workspace(reqs, members, rd), d, check)
        return code, buf.getvalue()

    def _seed(self, d, title="A"):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "AREA-A-001.md"),
               REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title=title))

    def test_absent_map_is_not_stale(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            code, out = self._map(d, check=True)   # never generated
            self.assertEqual(code, 0)              # a consumer who never maps passes
            # ...and says so, rather than reporting a freshness it never measured:
            # with nothing on disk the old wording claimed "map is fresh" after
            # comparing zero files.
            self.assertIn("no committed map to check", out)
            self.assertNotIn("is fresh", out)

    def test_fresh_map_passes_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            self._map(d)                            # generate
            code, _ = self._map(d, check=True)      # immediately check
            self.assertEqual(code, 0)

    def test_stale_map_fails_check(self):  # verifies: REQ-MAP-871#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self._seed(d, title="A")
            self._map(d)                            # generate against title A
            self._seed(d, title="A renamed")        # change the requirement
            code, out = self._map(d, check=True)    # built-fresh != on-disk
            self.assertEqual(code, 1)
            self.assertIn("stale", out)

    def test_timestamp_alone_is_not_stale(self):
        # _strip_generated must ignore the volatile timestamp line
        a = "---\ngenerated: 2026-01-01 00:00\nnodes: 1\n---\nbody"
        b = "---\ngenerated: 2026-12-31 23:59\nnodes: 1\n---\nbody"
        self.assertEqual(R._strip_generated(a), R._strip_generated(b))

class Next(unittest.TestCase):  # tested-by: ARCH-NEXT-013  # tested-by: REQ-NEXT-883  # tested-by: REQ-NEXT-884  # tested-by: REQ-NEXT-885  # tested-by: REQ-NEXT-886  # tested-by: REQ-NEXT-887
    def _next(self, reqs, members, show_all=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_next(R.Workspace(reqs, members), show_all)
        return code, buf.getvalue()

    def _req(self, status, extra="", body="# T\n"):
        return {"meta": {"status": status, **dict(_kv(extra))}, "body": body}

    def test_progress_header_present(self):  # verifies: REQ-NEXT-883#CASE-3
        reqs = {"CORE-FOO-001": self._req("confirmed"), "REQ-BAR-002": self._req("draft")}
        members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._next(reqs, members)
        self.assertIn("2 requirement(s)", out)
        self.assertIn("1 confirmed", out)
        self.assertIn("1 tested", out)
        self.assertIn("1 unreviewed", out)

    def test_untested_confirmed_lands_in_needs_tests(self):  # verifies: REQ-NEXT-883#CASE-1  # verifies: REQ-NEXT-885#CASE-4  # verifies: ARCH-NEXT-013#CASE-2
        reqs = {"CORE-FOO-001": self._req("confirmed")}
        members = {"CORE-FOO-001": [("implements", "src/foo.py", 1)]}  # no tested-by
        code, out = self._next(reqs, members)
        self.assertEqual(code, 0)
        self.assertIn("Needs tests", out)
        self.assertIn("requirements/CORE-FOO-001.md", out)   # names the file to open

    def test_draft_lands_in_drafts_to_review(self):  # verifies: REQ-NEXT-884#CASE-1
        reqs = {"REQ-BAR-002": self._req("draft")}
        _, out = self._next(reqs, {})
        self.assertIn("Drafts to review", out)
        self.assertIn("REQ-BAR-002", out)

    def test_draft_intent_deduped_not_in_intent_bucket(self):  # verifies: REQ-NEXT-884#CASE-5
        # a draft with an open verify bullet must NOT appear under intent review:
        # the source dedup folds it into 'unreviewed' (one bucket, honest count)
        body = "# T\n\n## WHAT — Verify intent\n- is this magic constant a bug?\n"
        reqs = {"REQ-BAR-002": self._req("draft", body=body)}
        _, out = self._next(reqs, {})
        self.assertIn("Drafts to review", out)
        self.assertNotIn("Needs intent review", out)

    def test_open_verify_intent_lands_in_needs_intent_review(self):  # verifies: REQ-NEXT-884#CASE-1
        body = "# T\n\n## WHAT — Verify intent\n- is this magic constant a bug?\n"
        reqs = {"CORE-FOO-001": self._req("confirmed", body=body)}
        members = {"CORE-FOO-001": [("implements", "src/foo.py", 1),
                                    ("tested-by", "t.py", 2)]}  # tested, so only intent fires
        _, out = self._next(reqs, members)
        self.assertIn("Needs intent review", out)

    def test_priority_orders_within_bucket(self):  # verifies: REQ-NEXT-885#CASE-2
        # both untested-confirmed → same 'Needs tests' bucket. The must-have id sorts
        # AFTER the should-have id alphabetically, so only priority can put it first.
        reqs = {"AAA-LOW-001": self._req("confirmed", extra="priority: should-have"),
                "ZZZ-HIGH-002": self._req("confirmed", extra="priority: must-have")}
        members = {rid: [("implements", "x.py", 1)] for rid in reqs}  # untested
        _, out = self._next(reqs, members)
        self.assertLess(out.index("ZZZ-HIGH-002"), out.index("AAA-LOW-001"))

    def test_review_flagged_drafts_ordered_first(self):  # verifies: REQ-NEXT-885#CASE-3
        reqs = {"DRAFT-A-001": self._req("draft", "risk: 0"),
                "DRAFT-B-002": self._req("draft", "risk: 2")}  # REVIEW
        _, out = self._next(reqs, {})
        self.assertLess(out.index("DRAFT-B-002"), out.index("DRAFT-A-001"))  # high-risk first
        self.assertIn("[REVIEW]", out)

    def test_top_n_truncates_and_all_expands(self):  # verifies: REQ-NEXT-886#CASE-1  # verifies: REQ-NEXT-886#CASE-2  # verifies: REQ-NEXT-886#CASE-3
        reqs = {"DRAFT-{}-00{}".format(c, i): self._req("draft")
                for i, c in enumerate("ABCDE", 1)}            # 5 drafts > top_n=3
        _, out = self._next(reqs, {})
        self.assertIn("more — run `reqmap.py gate --risk --all`", out)
        _, out_all = self._next(reqs, {}, show_all=True)
        self.assertNotIn("more — run", out_all)
        for rid in reqs:
            self.assertIn(rid, out_all)

    def test_blast_radius_is_omitted(self):  # verifies: REQ-NEXT-884#CASE-3
        # FOO has 3 dependents -> blast-radius signal, but next must not surface it
        reqs = {"CORE-FOO-001": self._req("confirmed"),
                "A-1": self._req("confirmed", "depends_on: [CORE-FOO-001]"),
                "B-2": self._req("confirmed", "depends_on: [CORE-FOO-001]"),
                "C-3": self._req("confirmed", "depends_on: [CORE-FOO-001]")}
        members = {k: [("implements", "x.py", 1), ("tested-by", "t.py", 2)] for k in reqs}
        _, out = self._next(reqs, members)
        self.assertNotIn("blast-radius", out)

    def test_all_clear_when_nothing_pending(self):  # verifies: REQ-NEXT-887#CASE-2
        reqs = {"CORE-FOO-001": self._req("confirmed")}
        members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        code, out = self._next(reqs, members)
        self.assertEqual(code, 0)
        self.assertIn("Nothing pending", out)

    def test_empty_registry_is_distinct_from_all_clear(self):  # verifies: REQ-NEXT-887#CASE-1
        code, out = self._next({}, {})
        self.assertEqual(code, 0)
        self.assertIn("No requirements yet", out)
        self.assertNotIn("Nothing pending", out)

    def _req_with_acs(self, n):
        acs = "".join(f"- AC-{i}: Given X When Y Then Z\n" for i in range(n))
        body = (
            "# Foo\n\n"
            "## WHAT — Contract (normative)\n- It shall do X\n\n"
            f"## HOW — Acceptance (= tests)\n{acs}"
        )
        return {"meta": {"status": "confirmed"}, "body": body}

    def test_granularity_at_threshold_warns(self):  # tested-by: ARCH-NEXT-013  # verifies: REQ-NEXT-884#CASE-6
        # threshold unified with lint's LINT_AC_MAX (7, unchanged) via the shared
        # _oversize predicate 2026-09-03 -- "at threshold" is now LINT_AC_MAX + 1
        # (was a hardcoded 5 against the old, next-only AC_SPLIT_THRESHOLD).
        reqs = {"AREA-FOO-001": self._req_with_acs(R.LINT_AC_MAX + 1)}
        _, out = self._next(reqs, {})
        self.assertIn("consider splitting", out)
        self.assertIn("AREA-FOO-001", out)

    def test_granularity_below_threshold_no_warn(self):  # tested-by: ARCH-NEXT-013
        # exactly LINT_AC_MAX ACs does not exceed it, so this must stay silent.
        reqs = {"AREA-FOO-001": self._req_with_acs(R.LINT_AC_MAX)}
        _, out = self._next(reqs, {})
        self.assertNotIn("consider splitting", out)

    def test_granularity_above_threshold_warns(self):  # tested-by: ARCH-NEXT-013
        reqs = {"AREA-FOO-001": self._req_with_acs(R.LINT_AC_MAX + 5)}
        _, out = self._next(reqs, {})
        self.assertIn("consider splitting", out)
        self.assertIn("AREA-FOO-001", out)

    def test_granularity_reported_even_when_nothing_else_pending(self):  # bug: next-early-return-hides-granularity
        reqs = {"AREA-FOO-001": self._req_with_acs(8)}
        members = {"AREA-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        code, out = self._next(reqs, members)
        self.assertEqual(code, 0)
        self.assertNotIn("Nothing pending", out)
        self.assertIn("consider splitting", out)

    def test_granularity_truncates_to_top_n(self):  # bug: next-granularity-no-topn-truncation
        reqs = {"AREA-FOO-00{}".format(i): self._req_with_acs(R.LINT_AC_MAX + 1) for i in range(1, 6)}
        _, out = self._next(reqs, {})
        self.assertEqual(out.count("consider splitting"), 3)
        self.assertIn("more — run `reqmap.py gate --risk --all`", out)
        _, out_all = self._next(reqs, {}, show_all=True)
        self.assertEqual(out_all.count("consider splitting"), 5)


def _kv(extra):
    """Parse the 'key: value' frontmatter lines a test passes as `extra` into meta,
    so Next can build requirement dicts the same way the REQ template does."""
    for line in extra.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta, _ = R.parse_frontmatter("---\n{}: {}\n---\n".format(k.strip(), v.strip()))
        yield k.strip(), meta.get(k.strip())


class Show(unittest.TestCase):  # tested-by: ARCH-SHOW-015  # tested-by: REQ-SHOW-917  # tested-by: REQ-SHOW-918  # tested-by: REQ-SHOW-919
    def _show(self, reqs, members, cap_id):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_show(R.Workspace(reqs, members), cap_id)
        return code, buf.getvalue()

    def _req(self, status="confirmed", extra="", body="# T\n"):
        return {"meta": {"status": status, "layer": "feature", **dict(_kv(extra))},
                "body": body, "path": "requirements/X.md"}

    def test_json_carries_the_dossier_and_the_file(self):  # verifies: REQ-SHOW-919#CASE-4
        reqs = {"REQ-X-001": self._req(extra="depends_on: [REQ-Y-002]",
                                       body="# T\n\n## Description\n- does x\n"),
                "REQ-Y-002": self._req()}
        members = {"REQ-X-001": [("implements", "a.py", 3)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_show(R.Workspace(reqs, members), "REQ-X-001", as_json=True)
        rec = json.loads(buf.getvalue())
        self.assertEqual(0, code)
        self.assertEqual((["does x"], ["REQ-Y-002"]), (rec["contract"], rec["depends_on"]))
        self.assertEqual([{"role": "implements", "file": "a.py", "line": 3, "level": None}],
                         rec["members"])
        self.assertEqual("confirmed", rec["frontmatter"]["status"])
        self.assertIn("## Description", rec["body"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_show(R.Workspace(reqs, members), "NOPE-000", as_json=True)
        self.assertEqual(1, code)
        self.assertIn("no requirement with id NOPE-000", json.loads(buf.getvalue())["error"])

    def test_known_id_header_and_zero(self):  # verifies: REQ-SHOW-917#CASE-3  # verifies: REQ-SHOW-919#CASE-3
        code, out = self._show({"REQ-X-001": self._req()}, {}, "REQ-X-001")
        self.assertEqual(code, 0)
        self.assertIn("REQ-X-001", out)
        self.assertIn("confirmed", out)
        self.assertIn("feature", out)

    def test_unknown_id_returns_one(self):  # verifies: REQ-SHOW-919#CASE-3
        code, out = self._show({}, {}, "NOPE-000")
        self.assertEqual(code, 1)
        self.assertIn("no requirement with id NOPE-000", out)

    def test_priority_shown_in_header_when_set(self):  # verifies: REQ-SHOW-917#CASE-4
        reqs = {"REQ-X-001": self._req(extra="priority: must-have")}
        _, out = self._show(reqs, {}, "REQ-X-001")
        self.assertIn("must-have", out.splitlines()[0])

    def test_priority_absent_header_has_no_blank_segment(self):  # verifies: REQ-SHOW-917#CASE-5
        _, out = self._show({"REQ-X-001": self._req()}, {}, "REQ-X-001")
        self.assertNotIn("·  ·", out.splitlines()[0])   # no empty priority slot

    def test_reverse_dependency_listed(self):  # verifies: REQ-SHOW-918#CASE-1
        reqs = {"CORE-A-001": self._req(),
                "REQ-B-002": self._req(extra="depends_on: [CORE-A-001]")}
        _, out = self._show(reqs, {}, "CORE-A-001")
        self.assertIn("Depended on by", out)
        self.assertIn("REQ-B-002", out)

    def test_member_role_and_location(self):  # verifies: REQ-SHOW-918#CASE-2
        members = {"REQ-X-001": [("implements", "src/foo.py", 42)]}
        _, out = self._show({"REQ-X-001": self._req()}, members, "REQ-X-001")
        self.assertIn("implements", out)
        self.assertIn("src/foo.py:42", out)

    def test_open_verify_shown_placeholder_skipped(self):  # verifies: REQ-SHOW-919#CASE-1
        body = ("# T\n\n## WHAT — Verify intent\n- is this magic constant a bug?\n"
                "- None — doc is unambiguous.\n")
        _, out = self._show({"REQ-X-001": self._req(body=body)}, {}, "REQ-X-001")
        self.assertIn("magic constant", out)
        self.assertNotIn("None — doc is unambiguous", out)

    def test_intent_skips_fenced_blockquote(self):  # bug-hunt #2
        body = "# T\n\n## WHAT — Contract\n```\n> not the intent\n```\n\n> The real intent.\n"
        _, out = self._show({"REQ-X-001": self._req(body=body)}, {}, "REQ-X-001")
        self.assertIn("The real intent.", out)
        self.assertNotIn("not the intent", out)

    def test_intent_skips_empty_blockquote_line(self):  # bug-hunt #11
        body = "# T\n>\n> The real intent.\n\n## WHAT — Contract\n- x.\n"
        _, out = self._show({"REQ-X-001": self._req(body=body)}, {}, "REQ-X-001")
        self.assertIn("The real intent.", out)

    def test_show_annotates_a_member_with_its_verification_level(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-SHOW-918#CASE-3  # verifies: REQ-VLEVEL-946#CASE-7
        reqs = {"REQ-X-001": self._req()}
        members = {"REQ-X-001": [("tested-by", "t.py", 2)]}
        levels = {"REQ-X-001": {"integration": [("t.py", 2)]}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(R.Workspace(reqs, members), "REQ-X-001", levels)
        self.assertIn("@integration", buf.getvalue())

    def test_show_without_level_data_is_unchanged(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-VLEVEL-946#CASE-7
        reqs = {"REQ-X-001": self._req()}
        members = {"REQ-X-001": [("tested-by", "t.py", 2)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(R.Workspace(reqs, members), "REQ-X-001")      # old 3-arg call still works
        self.assertIn("t.py:2", buf.getvalue())
        self.assertNotIn("@", buf.getvalue().split("Members in code")[-1])


class Similar(unittest.TestCase):  # tested-by: ARCH-SIMILAR-016  # tested-by: REQ-SIMILAR-920  # tested-by: REQ-SIMILAR-921  # tested-by: REQ-SIMILAR-922  # tested-by: REQ-SIMILAR-923
    def _sim(self, reqs, threshold=0.35):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_similar(reqs, threshold)
        return code, buf.getvalue()

    def _req(self, title, contract):
        return {"body": "# {t}\n\n> {t} intent.\n\n## WHAT — Contract (normative)\n- {c}\n".format(
            t=title, c=contract)}

    def test_near_identical_pair_reported(self):  # verifies: REQ-SIMILAR-920#CASE-1
        # DISTINCT titles so only the Contract text overlaps — this forces the match
        # through the contract path AC-1 names (bug-hunt #8: identical titles let a
        # contract-dropping mutation survive)
        c = "validate user input and reject malformed payloads from the client"
        reqs = {"REQ-A-001": self._req("Validator", c), "REQ-B-002": self._req("Checker", c)}
        code, out = self._sim(reqs, 0.35)
        self.assertEqual(code, 0)
        self.assertIn("REQ-A-001", out)
        self.assertIn("REQ-B-002", out)
        self.assertIn("<->", out)

    def test_cosine_clamped_to_one(self):  # bug-hunt #16  # verifies: REQ-SIMILAR-922#CASE-3
        v = R._tfidf({"a": ["foo", "bar", "foo", "baz"]})["a"]
        self.assertLessEqual(R._cosine(v, v), 1.0)

    def test_threshold_arg_rejects_bad_values(self):  # bug-hunt #3/#4
        import argparse as _ap
        for bad in ("nan", "inf", "0", "-1", "2", "abc"):
            with self.assertRaises(_ap.ArgumentTypeError):
                R._threshold_arg(bad)
        self.assertEqual(R._threshold_arg("0.35"), 0.35)

    def test_shared_terms_deterministic_on_weight_ties(self):  # bug-hunt #15  # verifies: REQ-SIMILAR-923#CASE-3
        # identical contracts -> every shared term ties on weight; the tiebreaker
        # must make the printed shared-terms list deterministic (alphabetical)
        c = "alpha bravo charlie delta echo foxtrot golf hotel"
        reqs = {"REQ-A-001": self._req("Aaa", c), "REQ-B-002": self._req("Bbb", c)}
        _, out = self._sim(reqs, 0.1)
        line = [ln for ln in out.splitlines() if "shared terms:" in ln][0]
        terms = line.split("shared terms:")[1].strip().split(", ")
        self.assertEqual(terms, sorted(terms))

    def test_test_suite_pairs_skipped_when_members_given(self):  # AC-7  # verifies: REQ-SIMILAR-923#CASE-6  # verifies: REQ-SIMILAR-921#CASE-6
        # A requirement and the requirement that IS its test suite share vocabulary by
        # construction; with the member map the pair is a known tested-by link, not a dupe.
        c = "resolve the dispatch model for each reviewer from prompt frontmatter"
        reqs = {"SCRIPTS-MODELS": self._req("Model resolution", c),
                "SCRIPTS-TEST-MODELS": self._req("Model resolution tests", c)}
        members = {"SCRIPTS-MODELS": [("implements", "scripts/models.py", 1),
                                      ("tested-by", "tests/test_models.py", 3)],
                   "SCRIPTS-TEST-MODELS": [("implements", "tests/test_models.py", 3)]}
        code, out = self._sim(reqs, 0.35)          # no members: reported as before
        self.assertIn("SCRIPTS-MODELS  <->  SCRIPTS-TEST-MODELS", out)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_similar(reqs, 0.35, members)
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertNotIn("<->", out)
        self.assertIn("skipped 1 pair(s) linked by tested-by", out)

    def test_unrelated_not_reported(self):  # verifies: REQ-SIMILAR-920#CASE-3
        reqs = {"REQ-A-001": self._req("Parser", "parse yaml frontmatter into a dictionary structure"),
                "REQ-B-002": self._req("Roadmap", "render mermaid gantt diagrams for milestones")}
        _, out = self._sim(reqs, 0.35)
        self.assertIn("No overlapping", out)

    def test_too_few_docs(self):  # verifies: REQ-SIMILAR-923#CASE-4
        code, out = self._sim({"REQ-A-001": self._req("Solo", "does one thing well")}, 0.35)
        self.assertEqual(code, 0)
        self.assertIn("at least two", out)

    def test_threshold_above_score_hides_pair(self):  # verifies: REQ-SIMILAR-923#CASE-5
        c = "validate user input and reject malformed payloads"
        reqs = {"REQ-A-001": self._req("Validator", c), "REQ-B-002": self._req("Validator", c)}
        _, out = self._sim(reqs, 1.01)   # cosine maxes at 1.0, so nothing qualifies
        self.assertIn("No overlapping", out)


class Search(unittest.TestCase):  # tested-by: ARCH-SEARCH-036  # tested-by: REQ-SEARCH-912  # tested-by: REQ-SEARCH-913  # tested-by: REQ-SEARCH-914  # tested-by: REQ-SEARCH-915
    def _search(self, reqs, query, top=5):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_search(reqs, query, top)
        return code, buf.getvalue()

    def _req(self, title, contract):
        return {"body": "# {t}\n\n> {t} intent.\n\n## WHAT — Contract (normative)\n- {c}\n".format(
            t=title, c=contract)}

    def _score_lines(self, out):
        # the ranked-hit lines look like "  0.287  REQ-...  Title"; the count header
        # ("2 match(es) ...") starts with a digit too but carries no "REQ-" token.
        return [ln for ln in out.splitlines()
                if "REQ-" in ln and ln.strip()[:1].isdigit()]

    def test_json_lists_the_same_matches(self):  # verifies: REQ-SEARCH-913#CASE-6
        reqs = {"REQ-DRIFT-001": self._req("Drift", "detect when a contract changes against the lock hash baseline"),
                "REQ-MAP-002": self._req("Map", "render mermaid diagrams of the requirement graph")}
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_search(reqs, "lock hash baseline", 5, as_json=True)
        rec = json.loads(buf.getvalue())
        self.assertEqual(0, code)
        self.assertEqual("REQ-DRIFT-001", rec["matches"][0]["id"])
        self.assertIn(rec["matches"][0]["match"], ("text", "lexical"))
        self.assertIsNone(rec["message"])

    def test_query_ranks_matching_requirement_first_with_score(self):  # AC-1  # verifies: REQ-SEARCH-913#CASE-1
        reqs = {"REQ-DRIFT-001": self._req("Drift", "detect when a contract changes against the lock hash baseline"),
                "REQ-MAP-002": self._req("Map", "render mermaid diagrams of the requirement graph")}
        code, out = self._search(reqs, "contract changed against the lock hash")
        self.assertEqual(code, 0)
        lines = self._score_lines(out)
        self.assertTrue(lines, "expected at least one ranked hit")
        # top hit is the drift requirement, printed with its cosine score
        # (a match is shown WITH its score, never as a bare id)
        self.assertRegex(lines[0].strip(), r"^\d\.\d{3}\s+REQ-DRIFT-001\b")

    def test_no_lexical_overlap_reports_no_strong_match(self):  # AC-2  # verifies: REQ-SEARCH-913#CASE-4  # verifies: REQ-SEARCH-913#CASE-5  # verifies: REQ-SEARCH-915#CASE-1
        reqs = {"REQ-DRIFT-001": self._req("Drift", "detect when a contract changes against the lock hash"),
                "REQ-MAP-002": self._req("Map", "render mermaid diagrams of the requirement graph")}
        code, out = self._search(reqs, "photosynthesis quarterly dividend wombat")
        self.assertEqual(code, 0)
        self.assertIn("No match for", out)
        # the failure mode being guarded: NO spurious ranked result below the floor
        self.assertNotIn("REQ-DRIFT-001", out)
        self.assertNotIn("REQ-MAP-002", out)

    def test_query_with_only_stopwords_says_no_terms(self):  # AC-3 — distinct from no-match  # verifies: REQ-SEARCH-914#CASE-2
        reqs = {"REQ-A-001": self._req("Thing", "does one thing well")}
        code, out = self._search(reqs, "the and for with")
        self.assertEqual(code, 0)
        self.assertIn("No searchable terms", out)
        self.assertNotIn("No match for", out)

    def test_top_caps_result_count(self):  # AC-4
        reqs = {"REQ-DUP-00{}".format(i): self._req("Doc" + str(i),
                    "validate user input and reject malformed payloads from the client")
                for i in range(1, 6)}
        def n(top):
            _, out = self._search(reqs, "validate user input malformed payloads client", top=top)
            return len(self._score_lines(out))
        self.assertEqual(n(2), 2)          # capped
        self.assertGreater(n(10), 2)       # ...and the cap is real, not a shortage of matches

    def _fx(self, title, intent, contract):
        # a fixture body with an explicit intent line — matches the golden fixture
        # in app/scripts/ssr-smoke.jsx field-for-field (title / intent / contract).
        return {"body": "# {t}\n\n> {i}\n\n## WHAT — Contract (normative)\n- {c}\n".format(
            t=title, i=intent, c=contract)}

    def test_ranking_matches_viewer_golden_fixture(self):  # parity: app/src/lib/search.js  # verifies: REQ-SEARCH-912#CASE-5
        # The viewer ports this exact TF-IDF model (ARCH-SEARCH-036). The SSR smoke
        # asserts the SAME fixture scores 0.4112 on REQ-DRIFT-001 and that a
        # no-overlap query floors out — both runtimes pinned to one model, so a
        # drift in either fails here or there.
        reqs = {
            "REQ-DRIFT-001": self._fx("Drift", "detect divergence",
                                      "detect when a contract changes against the lock hash baseline"),
            "REQ-MAP-002": self._fx("Map", "diagram",
                                    "render mermaid diagrams of the requirement graph"),
            "REQ-SCAN-003": self._fx("Scan", "find tags",
                                     "walk the code and find implements and tested-by tags in source files"),
        }
        _, out = self._search(reqs, "contract changed against the lock hash")
        self.assertRegex(self._score_lines(out)[0].strip(), r"^0\.411\s+REQ-DRIFT-001\b")
        _, none = self._search(reqs, "banana photosynthesis wombat")
        self.assertIn("No match for", none)


class Health(unittest.TestCase):  # tested-by: ARCH-HEALTH-017  # tested-by: REQ-REVIEWEDSCORE-109  # tested-by: REQ-HEALTH-857  # tested-by: REQ-HEALTH-858  # tested-by: REQ-HEALTH-859  # tested-by: REQ-HEALTH-968
    def _health(self, reqs, members, as_json=False):
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            code = R.cmd_health(R.Workspace(reqs, members, d), as_json)   # empty dir -> load_lock fails open
        return code, buf.getvalue()

    def _green(self):
        return {"meta": {"status": "confirmed"},
                "body": "# T\n\n## WHAT — Verify intent\n- None — clear.\n"}

    def test_all_green_is_100(self):  # verifies: REQ-HEALTH-857#CASE-3
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        code, out = self._health({"REQ-A-001": self._green()}, members)
        self.assertEqual(code, 0)
        self.assertIn("100/100", out)

    def test_map_carries_the_score_the_console_prints(self):  # verifies: REQ-HEALTH-968#CASE-1
        """The map's `health.score` and `next --json`'s score come from one computation."""
        reqs = {"REQ-A-001": self._green()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        with tempfile.TemporaryDirectory() as d:
            data = R._assemble_map_data(reqs, members, d, d)
            payload = json.loads(R._build_json_text(data))
        self.assertEqual(payload["health"]["score"], json.loads(out)["score"])
        self.assertEqual(payload["health"]["total"], len(reqs))

    def test_record_needs_no_code_root(self):  # verifies: REQ-HEALTH-968#CASE-2
        """Everything needing a code root stays in cmd_health, so the record is portable."""
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            rec = R._health_record({"REQ-A-001": self._green()}, members, d)
        self.assertEqual(rec["score"], 100)
        self.assertNotIn("untagged", rec)
        self.assertNotIn("design_score", rec)

    def test_map_json_is_byte_stable_across_runs(self):  # verifies: REQ-HEALTH-968#CASE-3
        """A health record that moved between runs would make every map look stale."""
        reqs = {"REQ-A-001": self._green()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            first = R._build_json_text(R._assemble_map_data(reqs, members, d, d))
            second = R._build_json_text(R._assemble_map_data(reqs, members, d, d))
        self.assertEqual(first, second)

    def test_the_score_names_its_exemptions(self):  # verifies: REQ-HEALTH-968#CASE-4
        """100/100 over waivers must not read like 100/100 over none."""
        waived = self._green()
        waived["meta"]["lint_exempt"] = ["ac-count-high"]
        retired = {"meta": {"status": "deprecated", "test_exempt": "gone"}, "body": "# T\n"}
        reqs = {"REQ-A-001": waived, "REQ-B-002": self._green(), "REQ-C-003": retired}
        members = {rid: [("implements", "x.py", 1), ("tested-by", "t.py", 2)]
                   for rid in ("REQ-A-001", "REQ-B-002")}
        with tempfile.TemporaryDirectory() as d:
            rec = R._health_record(reqs, members, d)
        self.assertEqual(1, rec["exempt"])            # the deprecated one is not counted
        _, out = self._health(reqs, members)
        self.assertIn("1 with an exemption", out.splitlines()[0])
        self.assertIn("| 1 exempt", R._health_badge_payload(rec)["message"])
        _, clean = self._health({"REQ-B-002": self._green()}, members)
        self.assertNotIn("exemption", clean.splitlines()[0])

    def test_all_draft_is_zero(self):
        reqs = {"REQ-A-001": {"meta": {"status": "draft"}, "body": "# T\n"}}
        _, out = self._health(reqs, {})
        self.assertIn("0/100", out)

    def test_json_has_all_component_fields(self):  # bug-hunt #18: assert every emitted key  # verifies: REQ-HEALTH-859#CASE-1
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        self.assertEqual(json.loads(out), {
            "score": 100, "total": 1, "scored": 1, "healthy": 1, "exempt": 0, "deprecated": 0,
            "confirmed": 1, "implemented": 1,
            "tested": 1, "drafts": 0, "orphans": 0, "untested": 0, "open_intent": 0, "drift": 0,
            "gate_errors": 0, "gate_link_sync_clean": True})

    # ARCH-HEALTH-017 CASE-8 / CASE-9: a draft can never be green (the first axis is
    # status `confirmed`), so every draft caps the headline score by construction. The
    # reviewed-only score separates "not reviewed yet" from "rotting" WITHOUT redefining
    # `score`, which CASE-2 binds to zero on an all-draft corpus and which every
    # consumer badge already reads.
    def _draft(self):
        return {"meta": {"status": "draft"}, "body": "# T\n"}

    def test_reviewed_score_excludes_drafts(self):  # verifies: REQ-REVIEWEDSCORE-109#CASE-1
        reqs = {"REQ-A-001": self._green()}
        for n in (2, 3, 4):
            reqs["REQ-A-00%d" % n] = self._draft()
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["score"], 25)            # 1 green of 4 — unchanged meaning
        self.assertEqual(obj["reviewed_score"], 100)  # 1 green of 1 reviewed
        self.assertEqual(obj["reviewed_total"], 1)

    def test_reviewed_score_absent_on_all_draft_corpus(self):  # verifies: REQ-REVIEWEDSCORE-109#CASE-2
        _, out = self._health({"REQ-A-001": self._draft()}, {}, as_json=True)
        obj = json.loads(out)
        self.assertNotIn("reviewed_score", obj)       # 0 of 0 is not 0%
        self.assertEqual(obj["score"], 0)             # CASE-2 still holds

    def test_reviewed_score_absent_when_no_drafts(self):  # verifies: REQ-REVIEWEDSCORE-109#CASE-3
        # with no draft it would restate `score` — a key that means nothing is a schema cost
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        self.assertNotIn("reviewed_score", json.loads(out))

    def test_reviewed_score_line_names_the_unconfirmed(self):  # verifies: REQ-REVIEWEDSCORE-109#CASE-4
        reqs = {"REQ-A-001": self._green(), "REQ-A-002": self._draft()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members)
        self.assertIn("reviewed only", out)
        self.assertIn("1 not confirmed yet", out)

    def test_reviewed_score_denominator_is_confirmed_not_merely_non_draft(self):  # verifies: REQ-REVIEWEDSCORE-109#CASE-5
        """`healthy`'s first axis is `status == confirmed`, so a non-draft that is not
        yet `confirmed` can enter a "non-draft" denominator but never the numerator —
        it would depress the reviewed score with nothing rotting. `deprecated` is the
        sharpest case: retired, permanently un-green, capping the score forever.
        Invisible in this repo (all non-drafts are `confirmed`), hence this test."""
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        for status in ("baseline", "in-progress", "implemented", "deprecated"):
            reqs = {"REQ-A-001": self._green(),
                    "REQ-A-002": {"meta": {"status": status}, "body": "# T\n"},
                    "REQ-A-003": self._draft()}
            _, out = self._health(reqs, members, as_json=True)
            obj = json.loads(out)
            self.assertEqual(obj["reviewed_total"], 1,
                "status %r must not enter the reviewed denominator" % status)
            self.assertEqual(obj["reviewed_score"], 100,
                "status %r depressed the reviewed score with nothing rotting" % status)

    def test_drift_drops_out_of_green(self):  # bug-hunt #18: exercise the drift axis
        reqs = {"REQ-A-001": self._green()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_reqlock.json"), '{"REQ-A-001": "staleHASH0000"}')
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace(reqs, members, d), True)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["drift"], 1)
        self.assertEqual(obj["healthy"], 0)
        self.assertLess(obj["score"], 100)

    # tested-by: ARCH-COVERAGE-029
    def test_untagged_count_with_code_root(self):  # tested-by: REQ-COVERAGE-836  # verifies: REQ-COVERAGE-836#CASE-1  # verifies: REQ-COVERAGE-836#CASE-4
        # ARCH-COVERAGE-029 AC-1 — the read-only coverage signal: count scannable
        # code files with no membership tag. Informational: it must NOT lower
        # the score.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "src"))
            _write(os.path.join(d, "src", "tagged.py"), "# implements: REQ-A-001\nx = 1\n")
            _write(os.path.join(d, "src", "untagged.py"), "x = 2\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), True)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["untagged"], 1)   # only untagged.py; tagged.py is covered
        self.assertEqual(obj["score"], 100)    # informational — never lowers the score

    def test_untagged_absent_without_code_root(self):  # tested-by: REQ-COVERAGE-836  # verifies: REQ-COVERAGE-836#CASE-6
        # no code root (e.g. a unit-test caller) -> the key is absent, not zero,
        # so existing --json consumers keep their exact schema.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        self.assertNotIn("untagged", json.loads(out))

    # tested-by: ARCH-REGISTRYLAG-035
    def _mkgit(self, d):
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.email", "t@t.com"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.name", "T"],
                       check=True, capture_output=True)

    def _gcommit(self, d, msg):
        subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-m", msg], check=True, capture_output=True)

    def test_commits_since_req_touch_counted(self):  # tested-by: REQ-REGISTRYLAG-903  # tested-by: REQ-REGISTRYLAG-904  # verifies: REQ-REGISTRYLAG-903#CASE-1  # verifies: REQ-REGISTRYLAG-904#CASE-1  # verifies: REQ-REGISTRYLAG-904#CASE-3
        # ARCH-REGISTRYLAG-035 AC-1 — advisory "registry lag" signal: how many
        # commits landed since the requirements dir was last touched. It flags a
        # registry frozen while code races ahead. Informational: never lowers score.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            self._mkgit(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"), "# T\n")
            self._gcommit(d, "reqs")
            for i in range(2):   # two commits that do NOT touch requirements/
                _write(os.path.join(d, "code{}.py".format(i)), "x = 1\n")
                self._gcommit(d, "c{}".format(i))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, rdir, d), True)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["commits_since_req_touch"], 2)
        self.assertEqual(obj["score"], 100)   # informational — never lowers the score

    def test_commits_since_req_touch_zero_when_fresh(self):
        # ARCH-REGISTRYLAG-035 AC-2 — the most recent commit touched requirements/:
        # lag is 0 and the key is present (0, not absent) for --json consumers.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            self._mkgit(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"), "# T\n")
            self._gcommit(d, "reqs")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, rdir, d), True)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["commits_since_req_touch"], 0)

    def test_registry_lag_absent_without_git(self):  # verifies: REQ-REGISTRYLAG-904#CASE-4
        # ARCH-REGISTRYLAG-035 AC-3 — a code root that is not a git worktree ->
        # the key is absent (not zero), mirroring the untagged idiom.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), True)
            obj = json.loads(buf.getvalue())
        self.assertNotIn("commits_since_req_touch", obj)

    def test_commits_since_reqs_touch_rooted_to_code_root(self):  # bug: registrylag-path-not-rooted
        """`code_root` may be relative (e.g. `--code ..`), spelled against the ORIGINAL
        cwd — the reqs_dir pathspec passed to `git -C code_root log` must be resolved
        the same way, or git looks inside the wrong directory and the signal silently
        goes missing."""
        with tempfile.TemporaryDirectory() as d:
            self._mkgit(d)
            sub = os.path.join(d, "plugin")
            os.makedirs(sub)
            _write(os.path.join(sub, "requirements", "REQ-A-001.md"), "# T\n")
            self._gcommit(d, "reqs")
            for i in range(2):
                _write(os.path.join(d, "code{}.py".format(i)), "x = 1\n")
                self._gcommit(d, "c{}".format(i))
            old_cwd = os.getcwd()
            os.chdir(sub)
            try:
                lag = R._commits_since_reqs_touch("..", "requirements")
            finally:
                os.chdir(old_cwd)
            self.assertEqual(lag, 2)

    def test_orphan_not_green(self):  # verifies: REQ-HEALTH-858#CASE-1
        # confirmed but no implements member -> orphan, drops out of green
        _, out = self._health({"REQ-A-001": self._green()}, {})
        self.assertIn("orphans", out)
        self.assertIn("0/100", out)

    def test_empty_corpus(self):  # verifies: REQ-HEALTH-859#CASE-3  # verifies: REQ-HEALTH-859#CASE-4
        code, out = self._health({}, {})
        self.assertEqual(code, 0)
        self.assertIn("0/100", out)

    def _need(self):
        return {"meta": {"status": "confirmed", "layer": "need"},
                "body": "# N\n\n## WHAT — Verify intent\n- None — clear.\n"}

    def test_satisfied_need_is_green(self):  # verifies: REQ-HEALTH-858#CASE-3
        # a need is covered by being satisfied, not implemented; test axis waived
        reqs = {"NEED-X-001": self._need(),
                "REQ-A-001": {"meta": {"status": "confirmed", "satisfies": ["NEED-X-001"]},
                              "body": "# T\n\n## WHAT — Verify intent\n- None — clear.\n"}}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["score"], 100)
        self.assertEqual(obj["orphans"], 0)
        self.assertEqual(obj["untested"], 0)

    def test_unsatisfied_need_is_orphan_not_green(self):  # verifies: REQ-HEALTH-858#CASE-4
        _, out = self._health({"NEED-X-001": self._need()}, {}, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["orphans"], 1)
        self.assertEqual(obj["healthy"], 0)

    def test_a_retired_requirement_does_not_lower_the_score(self):  # verifies: REQ-HEALTH-858#CASE-5
        reqs = {"REQ-A-001": {"meta": {"status": "confirmed"},
                              "body": "# T\n\n## WHAT — Verify intent\n- None — clear.\n"},
                "REQ-B-002": {"meta": {"status": "deprecated"}, "body": "# Old\n"}}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual((obj["score"], obj["deprecated"], obj["scored"]), (100, 1, 1))

    def test_aggregate_waived_from_test_axis_like_need(self):  # bug: health-aggregate-not-waived
        reqs = {
            "AGG-X-001": {"meta": {"status": "confirmed", "layer": "aggregate",
                                    "depends_on": ["REQ-A-001"]},
                          "body": "# Agg\n\n## WHAT — Verify intent\n- None — clear.\n"},
            "REQ-A-001": {"meta": {"status": "confirmed"},
                          "body": "# T\n\n## WHAT — Verify intent\n- None — clear.\n"},
        }
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["healthy"], 2)
        self.assertEqual(obj["score"], 100)

    # tested-by: ARCH-HEALTH-017 (RM-6)
    def test_gate_errors_reflect_dangling_tag(self):
        # a code tag pointing at a nonexistent requirement is one of gate's two
        # ERROR-level link-sync predicates — health must surface it, informational
        # only (score stays 100, mirroring the `untagged` idiom).
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)],
                   "REQ-GHOST-999": [("implements", "y.py", 3)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["gate_errors"], 1)
        self.assertFalse(obj["gate_link_sync_clean"])
        self.assertEqual(obj["score"], 100)   # informational — never lowers the score

    def test_gate_errors_reflect_missing_implements(self):
        # a confirmed requirement with no implements: member is gate's other
        # ERROR-level predicate.
        _, out = self._health({"REQ-A-001": self._green()}, {}, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["gate_errors"], 1)
        self.assertFalse(obj["gate_link_sync_clean"])

    def test_gate_clean_is_default(self):
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["gate_errors"], 0)
        self.assertTrue(obj["gate_link_sync_clean"])

    def test_gate_errors_dirty_badge_is_red_with_count(self):
        members = {"REQ-GHOST-999": [("implements", "y.py", 3)]}
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            R.cmd_health(R.Workspace({}, members, d), as_badge=True)
        badge = json.loads(buf.getvalue())
        self.assertEqual(badge["color"], "red")
        self.assertIn("gate:1", badge["message"])

    def test_clean_badge_unaffected(self):
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d), as_badge=True)
        badge = json.loads(buf.getvalue())
        self.assertEqual(badge["color"], "brightgreen")
        self.assertNotIn("gate:", badge["message"])

    def test_does_NOT_catch_untagged_value_edit(self):
        # RM-6's documented limitation: a value changed in a file that carries no
        # membership tag at all produces no dangling reference and no missing-
        # implements error, so it is invisible to this signal. This test pins
        # that gap so it is never silently "closed" by a future refactor without
        # a deliberate, separate decision (see .consilium/TODO.md history).
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "config"))
            _write(os.path.join(d, "config", "risk_limits.yaml"), "daily_loss_limit: 500\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), True)
            obj = json.loads(buf.getvalue())
            # simulate the incident: the untagged file's value changes with no
            # supporting tag anywhere — re-running health sees no difference.
            _write(os.path.join(d, "config", "risk_limits.yaml"), "daily_loss_limit: 150\n")
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), True)
            obj2 = json.loads(buf2.getvalue())
        self.assertTrue(obj["gate_link_sync_clean"])
        self.assertTrue(obj2["gate_link_sync_clean"])   # unchanged — the gap is real


class Round2Polish(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: ARCH-PROMOTE-011
    """Round-2 LOW fixes: anchored heading detection in the last substring holdouts
    + a frontmatter status-line guard."""

    def test_labeled_acs_anchored_skips_commentary(self):  # _labeled_acs anchored (ARCH-ACVERIFY-019)
        body = ("## Notes — acceptance caveats\nAC-9 not a real criterion\n"
                "## HOW — Acceptance\nAC-1 real\nAC-2 real\n")
        self.assertEqual(R._labeled_acs(body), ["AC-1", "AC-2"])

    def test_section_raw_anchored_skips_commentary(self):  # _section_raw anchored (ARCH-MAP-007)
        body = ("## Notes — output format\n- not the real output\n"
                "## WHAT — Output\n- the real output line\n")
        raw = R._section_raw(body, "output")
        self.assertIn("the real output line", raw)
        self.assertNotIn("not the real output", raw)

    def test_set_status_blank_line_does_not_corrupt(self):  # _set_frontmatter_status (ARCH-PROMOTE-011)
        text = "---\nid: X-1\nstatus:\nlayer: feature\n---\n\n# T\n"
        out, n = R._set_frontmatter_status(text, "confirmed")
        self.assertEqual(n, 1)
        self.assertIn("status: confirmed", out)
        self.assertIn("layer: feature", out)   # the next frontmatter key must survive intact

    def test_set_status_normal_line_unchanged_shape(self):
        out, n = R._set_frontmatter_status("---\nstatus: draft\n---\n", "confirmed")
        self.assertEqual(out, "---\nstatus: confirmed\n---\n")
        self.assertEqual(n, 1)

    def test_lint_exempt_scalar_string_is_honored(self):  # bug: lint-exempt-char-split (ARCH-LINTCHECKS-025)
        # a bracketless `lint_exempt: ac-count-high` must exempt that check, not be
        # walked character-by-character (which silently exempts nothing)
        body = ("## WHAT — Contract\n- shall do x\n## HOW — Acceptance\n"
                + "".join("- AC {}\n".format(i) for i in range(1, 9)))   # 8 ACs > LINT_AC_MAX
        r = {"meta": {"status": "confirmed", "layer": "feature", "lint_exempt": "ac-count-high"},
             "body": body}
        checks = [f["check"] for f in R.lint_requirement("A-B-001", r)]
        self.assertNotIn("ac-count-high", checks)


class AdversarialInjection(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-870  # tested-by: REQ-VIEWER-941
    """Hostile requirement text reaching the generated HTML and JSON.

    `</script>` already had a regression test. These are the two that did not:
    the JS line terminators, and a lone surrogate - which is reachable in the
    real world through a FILENAME whose bytes are not valid UTF-8, since os.walk
    hands those back surrogate-escaped and member paths go straight into the map.
    """

    LS, PS = chr(0x2028), chr(0x2029)
    LONE = chr(0xD800)

    def _data(self, title, contract=None):
        return {"repo": "r", "edges": [], "todos": [],
                "nodes": [{"id": "A-B-001", "title": title, "contract": contract or [],
                           "status": "confirmed", "layer": "bus", "members": [],
                           "risk": 0, "acc": [], "deps": []}]}

    def test_js_line_terminators_never_reach_the_script_blob_raw(self):  # tested-by: ARCH-VIEWERFILE-074  # verifies: REQ-VIEWER-941#CASE-5
        """U+2028/U+2029 terminate a line in JavaScript. Raw in the inlined blob they
        are a syntax error on any engine older than ES2019 - the whole viewer dies on
        one character in one requirement title."""
        out = R._inject_viewer("<html><!--REQMAP_DATA--></html>",
                               self._data("a" + self.LS + "b", ["c" + self.PS + "d"]))
        self.assertNotIn(self.LS, out)
        self.assertNotIn(self.PS, out)
        self.assertIn(chr(92) + "u2028", out)      # escaped, not dropped
        self.assertIn(chr(92) + "u2029", out)

    def test_escaped_line_terminators_still_parse_back_to_the_original(self):  # verifies: REQ-VIEWER-941#CASE-5
        """The escape must be lossless: the viewer shows the character, not a mangle."""
        out = R._inject_viewer("<!--REQMAP_DATA-->", self._data("a" + self.LS + "b"))
        blob = out[len("<script>window.__REQMAP_DATA__="):-len(";</script>")]
        self.assertEqual(json.loads(blob)["nodes"][0]["title"], "a" + self.LS + "b")

    def test_lone_surrogate_does_not_crash_the_json_write(self):  # verifies: ARCH-MAP-007#CASE-3
        """A lone surrogate cannot be encoded as UTF-8: the write raised
        UnicodeEncodeError and `map` died outright, taking the gate's map-freshness
        check with it. Degrade to U+FFFD instead."""
        with tempfile.TemporaryDirectory() as d:
            R.render_json(self._data("x" + self.LONE), d)
            body = open(os.path.join(d, "_map.json"), encoding="utf-8").read()
            self.assertIn(chr(0xFFFD), body)
            self.assertNotIn(self.LONE, body)
            json.loads(body)                       # still valid JSON

    def test_lone_surrogate_does_not_crash_the_markdown_write(self):
        with tempfile.TemporaryDirectory() as d:
            R.render_md(self._data("x" + self.LONE), d)
            body = open(os.path.join(d, "_map.md"), encoding="utf-8").read()
            self.assertNotIn(self.LONE, body)

    def test_clean_data_is_untouched_by_the_guard(self):
        """The sanitizer must be inert on normal text, including non-ASCII."""
        text = R._build_json_text(self._data("café — ünïcode ✓"))
        self.assertIn("café — ünïcode ✓", text)
        self.assertNotIn(chr(0xFFFD), text)


class CommandRegistry(unittest.TestCase):  # tested-by: ARCH-CMDREGISTRY-033  # tested-by: REQ-CMDREGISTRY-834
    def test_registry_matches_argparse_choices(self):  # verifies: REQ-CMDREGISTRY-834#CASE-1
        # the registry is the single source: argparse choices must equal its keys in insertion order.
        self.assertEqual(R._cli_choices(), list(R.COMMANDS))

    def test_every_dispatch_branch_has_a_registry_entry(self):
        # guard: every command the dispatch ladder handles is described in the registry.
        import re
        _scripts = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(_scripts, "reqmap.py"), encoding="utf-8") as _f:
            src = _f.read()
        handled = set(re.findall(r'a\.cmd == "([a-z-]+)"', src))
        self.assertTrue(handled.issubset(set(R.COMMANDS)),
                        f"dispatch handles commands absent from COMMANDS: {handled - set(R.COMMANDS)}")

    def test_generated_schema_matches_committed(self):  # verifies: REQ-CMDREGISTRY-834#CASE-2
        generated = R._generate_schema()                 # JSON string, trailing newline
        HERE = os.path.dirname(os.path.abspath(__file__))
        committed = open(os.path.join(HERE, "..", "tool_definition.json"), encoding="utf-8").read()
        self.assertEqual(generated, committed)

    def test_schema_has_one_entry_per_user_command(self):  # verifies: REQ-CMDREGISTRY-834#CASE-2  # verifies: REQ-CMDREGISTRY-834#CASE-4
        import json as _j
        tools = _j.loads(R._generate_schema())
        names = {t["function"]["name"] for t in tools}
        expected = {"reqmap_" + c.replace("-", "_") for c, s in R.COMMANDS.items()
                    if not s.get("internal") and s.get("tool") is not False}
        self.assertEqual(names, expected)
        self.assertNotIn("reqmap_mcp", names)                # a server is not a function
        self.assertIn("`mcp`", R._generate_command_table())  # and is still documented

    def test_command_table_region_is_generated(self):  # verifies: REQ-CMDREGISTRY-834#CASE-3
        table = R._generate_command_table()              # markdown table string
        _here = os.path.dirname(os.path.abspath(__file__))
        skill_path = os.path.join(_here, "..", "skills", "requirement-manager", "SKILL.universal.md")
        text = open(skill_path, encoding="utf-8").read()
        start = text.index("<!--##REQMAP:COMMANDS##-->") + len("<!--##REQMAP:COMMANDS##-->")
        end = text.index("<!--##/REQMAP:COMMANDS##-->")
        self.assertEqual(text[start:end].strip(), table.strip())

    def test_skill_md_list_is_the_registry(self):  # verifies: REQ-CMDREGISTRY-834#CASE-7
        """The list an assistant reads on a fresh repo: one entry per registered verb, in
        the registry's own groups, nothing documented that does not exist."""
        body = R._generate_command_list()
        documented = re.findall(r"^- `python scripts/reqmap\.py ([a-z-]+)", body, re.M)
        expected = [n for n, s in R.COMMANDS.items() if not s.get("internal")]
        self.assertEqual(sorted(documented), sorted(expected))
        self.assertEqual(len(documented), len(set(documented)))
        for group in ("**Author**", "**Build**", "**Read**"):
            self.assertIn(group, body)
        plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(R.__file__)))
        with open(os.path.join(plugin_root, "skills", "requirement-manager", "SKILL.md"),
                  encoding="utf-8") as f:
            m = R._REGION_RE.search(f.read())
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2).strip(), body.strip())

    def test_integration_fresh_when_committed(self):  # verifies: REQ-CMDREGISTRY-834#CASE-5
        HERE = os.path.dirname(os.path.abspath(__file__))
        plugin_root = os.path.join(HERE, "..")          # plugin/
        self.assertEqual(R._check_integration_fresh(plugin_root), [])

    def test_check_integration_fresh_detects_stale_schema(self):  # verifies: REQ-CMDREGISTRY-834#CASE-5
        import tempfile, shutil
        HERE = os.path.dirname(os.path.abspath(__file__))
        with tempfile.TemporaryDirectory() as d:
            dst = os.path.join(d, "plugin")
            shutil.copytree(os.path.join(HERE, ".."), dst)
            with open(os.path.join(dst, "tool_definition.json"), "w", encoding="utf-8") as f:
                f.write("[]\n")                          # deliberately stale
            stale = R._check_integration_fresh(dst)
            self.assertIn("tool_definition.json", stale)

    def test_gate_json_also_fails_on_stale_artifact(self):  # verifies: REQ-CMDREGISTRY-834#CASE-5
        # the --json CI path must not bypass the drift-guard
        import tempfile, shutil, subprocess, sys
        HERE = os.path.dirname(os.path.abspath(__file__))
        with tempfile.TemporaryDirectory() as d:
            dst = os.path.join(d, "plugin")
            shutil.copytree(os.path.join(HERE, ".."), dst)
            with open(os.path.join(dst, "tool_definition.json"), "w", encoding="utf-8") as f:
                f.write("[]\n")                                   # stale
            r = subprocess.run([sys.executable, "-X", "utf8", os.path.join(dst, "scripts", "reqmap.py"),
                                "gate", "--json"], cwd=dst, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0, "gate --json must fail on a stale artifact")

    def test_write_region_preserves_untouched_line_endings(self):  # verifies: REQ-CMDREGISTRY-834#CASE-3
        """Regenerating the delimited region must not silently normalize the WHOLE
        file's line endings to the host platform's os.linesep -- contradicts the
        function's own docstring promise that \"prose outside is untouched\"."""
        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "SKILL.universal.md")
            content = (b"prose before\n"
                       b"<!--##REQMAP:COMMANDS##-->\n"
                       b"old table\n"
                       b"<!--##/REQMAP:COMMANDS##-->\n"
                       b"prose after\n")
            with open(fp, "wb") as f:
                f.write(content)
            R._write_region(fp, "new table")
            with open(fp, "rb") as f:
                data = f.read()
            self.assertIn(b"new table", data)
            self.assertNotIn(b"\r\n", data, "prose outside the region was flipped to CRLF")

    def test_write_region_body_takes_the_files_line_endings(self):  # verifies: REQ-CMDREGISTRY-834#CASE-3
        """A CRLF file must not end up with an LF island inside the region: it is
        byte-equal to git after normalisation, so nothing ever failed, while every
        sync on Windows left a no-op line-ending diff on SKILL.md."""
        crlf, lf = chr(13) + chr(10), chr(10)
        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "SKILL.md")
            with open(fp, "w", encoding="utf-8", newline="") as f:
                f.write(crlf.join(["prose", "<!--##REQMAP:COMMANDS##-->", "old",
                                   "<!--##/REQMAP:COMMANDS##-->", "after", ""]))
            R._write_region(fp, lf.join(["line one", "line two"]))
            with open(fp, "rb") as f:
                data = f.read().decode("utf-8")
            self.assertIn(crlf.join(["line one", "line two"]), data)
            self.assertEqual(data.count(lf), data.count(crlf), "a bare LF survived")

    def test_gen_integration_preserves_existing_eol_convention(self):
        """Regenerating tool_definition.json from scratch must not silently normalize
        the file's existing line-ending convention to the host platform's os.linesep,
        even though the regenerated JSON content itself always uses bare \"\\n\"."""
        import tempfile, shutil, subprocess, sys
        HERE = os.path.dirname(os.path.abspath(__file__))
        with tempfile.TemporaryDirectory() as d:
            dst = os.path.join(d, "plugin")
            shutil.copytree(os.path.join(HERE, ".."), dst)
            tj = os.path.join(dst, "tool_definition.json")
            with open(tj, "wb") as f:
                f.write(b"[]\n")             # pre-existing LF-only committed convention
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_gen_integration(os.path.join(dst, "requirements"), dst)
            self.assertEqual(rc, 0)
            with open(tj, "rb") as f:
                data = f.read()
            self.assertNotIn(b"\r\n", data,
                              "regenerating flipped the file's existing LF convention to CRLF")


class BugHuntMutateAnalyze(unittest.TestCase):  # tested-by: ARCH-PROMOTE-011  # tested-by: ARCH-NEXT-013
    def test_set_status_empty_value_with_comment_not_corrupted(self):
        out, n = R._set_frontmatter_status(
            "---\nid: X\nstatus:  # deprecated hint\nlayer: bus\n---\nbody\n", "confirmed")
        self.assertEqual(n, 1)
        self.assertIn("status: confirmed", out)
        self.assertNotIn("confirmed deprecated", out)   # value+leaked text must not glue
        self.assertNotIn("confirmed#", out)
        self.assertIn("\nbody\n", out)

    def test_next_granularity_counts_labeled_acs(self):
        # 9 labelled AC-N criteria (no bullet dashes): _bullets saw 0 and suppressed
        # the advisory; _count_ac sees 9. Members are implements-only so the req has a
        # pending ('untested') signal and execution reaches the granularity block.
        # Bumped from 5 to 9 ACs: the Granularity threshold was unified with lint's
        # LINT_AC_MAX (7, unchanged) via the shared `_oversize` predicate, so 5 no
        # longer qualifies (2026-09-03, reqmap-oversize-unify) -- deliberate, see
        # OversizeUnify below for the next/lint parity coverage this change needed.
        body = "# T\n\n## HOW — Acceptance\n" + "".join(
            "AC-%d: criterion %d\n" % (i, i) for i in range(1, 10))
        reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed", "layer": "feature"}, "body": body}}
        members = {"CORE-FOO-001": [("implements", "x.py", 1)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_next(R.Workspace(reqs, members))
        self.assertIn("Granularity", buf.getvalue())

    def test_map_data_verify_intent_heading_consistency(self):
        body = "# T\n\n## WHAT — Contract\n- c\n\n## WHAT — Verify roadmap\n- someday item\n"
        reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed", "layer": "feature"},
                                 "body": body, "path": "x"}}
        members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        data = R._build_map_data(reqs, members)
        node = next(n for n in data["nodes"] if n["id"] == "CORE-FOO-001")
        self.assertNotIn("unverified-intent", [r["signal"] for r in node["risks"]])


class BugHuntRender(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: ARCH-INIT-012
    def test_req_to_code_distinct_ids_for_safeid_collision(self):
        data = {"nodes": [
            {"id": "REQ-A-001", "title": "A", "status": "draft",
             "members": [{"role": "implements", "loc": "src/a-b.py:1"}]},
            {"id": "REQ-B-001", "title": "B", "status": "draft",
             "members": [{"role": "implements", "loc": "src/a_b.py:1"}]},
        ]}
        out = R._mermaid_req_to_code(data)
        import re
        ids = re.findall(r"(f_\w+)\[", out)
        self.assertEqual(len(ids), len(set(ids)), "colliding file node ids:\n" + out)

    def test_area_subgraphs_distinct_ids_for_safeid_collision(self):
        nodes = [
            {"id": "X-1", "title": "x1", "area": "my-area"},
            {"id": "X-2", "title": "x2", "area": "my-area"},
            {"id": "Y-1", "title": "y1", "area": "my_area"},
            {"id": "Y-2", "title": "y2", "area": "my_area"},
        ]
        lines = []
        R._emit_area_subgraphs(lines, nodes)
        import re
        sgids = re.findall(r"subgraph (sg_\w+)\[", "\n".join(lines))
        self.assertEqual(len(sgids), len(set(sgids)), "\n".join(lines))

    def test_wipe_preserves_non_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements"); os.makedirs(rdir)
            fp = os.path.join(d, "mod.py")
            with open(fp, "wb") as f:
                f.write(b"# caf\xe9 note\n# " + b"impl" + b"ements: WIPE-001\n")
            with redirect_stdout(io.StringIO()):
                R._wipe(rdir, d)
            with open(fp, "rb") as f:
                data = f.read()
            self.assertIn(b"\xe9", data, "non-UTF-8 byte dropped by wipe")
            self.assertNotIn(b"WIPE-001", data, "tag not stripped")

    def test_wipe_preserves_untouched_line_endings(self):
        """Stripping ONE tag comment must not silently normalize the WHOLE file's
        line endings to the host platform's os.linesep -- concretely, an LF-committed
        shell hook stripped on Windows must stay LF, or /bin/sh chokes on the CR."""
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements"); os.makedirs(rdir)
            fp = os.path.join(d, "hook.sh")
            with open(fp, "wb") as f:
                f.write(b"#!/bin/sh\n# " + b"impl" + b"ements: WIPE-EOL-001\necho done\n")
            with redirect_stdout(io.StringIO()):
                R._wipe(rdir, d)
            with open(fp, "rb") as f:
                data = f.read()
            self.assertNotIn(b"WIPE-EOL-001", data, "tag not stripped")
            self.assertNotIn(b"\r\n", data, "untouched lines were flipped to CRLF")

    def test_section_includes_content_after_fenced_heading(self):
        body = "## WHAT — Contract\nfirst clause\n```yaml\n## not a heading\nk: v\n```\nlast clause\n"
        self.assertIn("last clause", R._section(body, "contract"))

    def test_bullets_include_after_fenced_heading(self):
        body = "## WHAT — Contract\n- one\n```\n## nope\n```\n- two\n"
        self.assertIn("two", R._bullets(body, "contract"))


class RoadmapSignals(unittest.TestCase):  # tested-by: ARCH-ROADMAP-038  # tested-by: REQ-ROADMAP-907  # tested-by: REQ-ROADMAP-983
    REQ_MS = "---\nid: {id}\nstatus: confirmed\nlayer: feature\nmilestone: {ms}\n---\n\n# T\n"

    def _health(self, todo_text, req_ms="v2.13"):
        """Build a repo with one milestoned requirement plus an optional TODO.md,
        run `health --json`, and return the parsed payload."""
        with tempfile.TemporaryDirectory() as d:
            reqs_dir = os.path.join(d, "requirements")
            _write(os.path.join(reqs_dir, "REQ-A-001.md"),
                   self.REQ_MS.format(id="REQ-A-001", ms=req_ms))
            _write(os.path.join(d, "impl.py"), "# implements: REQ-A-001\ndef f():\n    pass\n")
            if todo_text is not None:
                _write(os.path.join(d, "TODO.md"), todo_text)
            reqs = R.load_requirements(reqs_dir)
            members = R.scan_members(d, reqs_dir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace(reqs, members, reqs_dir, d), True)
            return json.loads(buf.getvalue())

    def test_behind_signal_when_the_roadmap_lags(self):  # verifies: ARCH-ROADMAP-038#CASE-1  # verifies: REQ-ROADMAP-907#CASE-3
        data = self._health("# TODO\n\n## v2.8\n- [ ] later | lane: feature\n", req_ms="v2.13")
        self.assertEqual(data["roadmap_behind"], {"todo": "v2.8", "requirements": "v2.13"})

    def test_no_behind_signal_when_the_roadmap_is_current(self):  # verifies: ARCH-ROADMAP-038#CASE-2  # verifies: REQ-ROADMAP-907#CASE-4
        data = self._health("# TODO\n\n## v2.16\n- [x] shipped | lane: feature\n", req_ms="v2.13")
        self.assertNotIn("roadmap_behind", data)

    def test_unversioned_heading_is_listed(self):  # verifies: ARCH-ROADMAP-038#CASE-3  # verifies: REQ-ROADMAP-907#CASE-6
        todo = "# TODO\n\n## v2.16\n- [x] a | lane: feature\n\n## Deferred work\n- [ ] b | lane: feature\n"
        data = self._health(todo, req_ms="v2.13")
        self.assertEqual(data["roadmap_unversioned_headings"], ["Deferred work"])

    def test_no_todo_file_means_no_roadmap_signals(self):  # verifies: ARCH-ROADMAP-038#CASE-4  # verifies: REQ-ROADMAP-907#CASE-2
        data = self._health(None)
        self.assertNotIn("roadmap_behind", data)
        self.assertNotIn("roadmap_unversioned_headings", data)

    def test_versions_compare_numerically_not_as_strings(self):  # verifies: ARCH-ROADMAP-038#CASE-5  # verifies: REQ-ROADMAP-907#CASE-5
        self.assertGreater(R._version_key("v2.10"), R._version_key("v2.9"))
        self.assertLess("v2.10", "v2.9")   # the string compare this guards against

    def test_unmapped_signal_when_the_requirements_lag_shipped_work(self):  # verifies: ARCH-ROADMAP-038#CASE-6  # verifies: REQ-ROADMAP-983#CASE-1
        # The direction the behind-signal alone could not see: the roadmap says v2.16
        # shipped, the corpus stops at v2.13, and `roadmap_behind` is correctly silent.
        data = self._health("# TODO\n\n## v2.16\n- [x] shipped | lane: feature\n", req_ms="v2.13")
        self.assertEqual(data["roadmap_unmapped"], {"shipped": "v2.16", "requirements": "v2.13"})
        self.assertNotIn("roadmap_behind", data)

    def test_an_open_item_under_a_later_heading_is_a_plan_not_a_gap(self):  # verifies: REQ-ROADMAP-983#CASE-2
        # Warning here would fire on every roadmap that plans ahead, which is every one.
        data = self._health("# TODO\n\n## v2.16\n- [ ] planned | lane: feature\n", req_ms="v2.13")
        self.assertNotIn("roadmap_unmapped", data)

    def test_no_unmapped_signal_when_the_corpus_is_level_with_shipped_work(self):  # verifies: REQ-ROADMAP-983#CASE-3
        data = self._health("# TODO\n\n## v2.13\n- [x] shipped | lane: feature\n", req_ms="v2.13")
        self.assertNotIn("roadmap_unmapped", data)

    def test_each_roadmap_line_names_its_next_step(self):  # verifies: REQ-ROADMAP-983#CASE-4
        reqs = {"REQ-A-001": {"meta": {"milestone": "v2.13"}, "body": ""}}
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"),
                   "# TODO\n\n## v2.16\n- [x] a | lane: feature\n\n## Deferred\n- [ ] b\n")
            lines = R.audittail._roadmap_lag_lines(reqs, d)
        self.assertTrue(any("add `milestone:` to the requirements that shipped after v2.13" in x
                            for x in lines), lines)
        self.assertTrue(any("start each with its version" in x and "Deferred" in x
                            for x in lines), lines)

    def test_init_names_an_inert_roadmap(self):  # verifies: REQ-ROADMAP-983#CASE-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"), "# TODO\n\n## Backlog\n- [ ] b\n")
            _write(os.path.join(d, "app.py"), "def run():\n    return 1\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_init(os.path.join(d, "requirements"), d)
        self.assertEqual(1, buf.getvalue().count("the roadmap chart stays empty"))


class ViewerDataSync(unittest.TestCase):  # tested-by: ARCH-VIEWER-007
    def _fixture(self, path, entries):
        _write(path, json.dumps(entries))

    def test_demo_only_entry_is_not_compared(self):
        """The fixture INVENTS two states the registry cannot contain - a fake orphan and
        a fake deprecated capability - so the viewer's Risk and Problems tabs have
        something to show with no engine present. Comparing those against the registry
        reported permanent drift: the check crying wolf about data doing its job."""
        with tempfile.TemporaryDirectory() as d:
            baked = os.path.join(d, "baked.json")
            self._fixture(baked, [{"id": "REAL-ONE-001", "contract": ["Alpha does X."]},
                                  {"id": "FAKE-DEMO-999", "demoOnly": True,
                                   "contract": ["Invented."]}])
            drift = R.check_viewer_data_sync(baked, [{"id": "REAL-ONE-001",
                                                     "contract": ["Alpha does X."]}])
            self.assertEqual(drift, [])

    def test_unmarked_missing_id_is_still_reported(self):
        """The marker must not blunt the real signal: an entry that CLAIMS to mirror a
        requirement, whose id no longer exists (renamed out from under the fixture),
        still counts as drift."""
        with tempfile.TemporaryDirectory() as d:
            baked = os.path.join(d, "baked.json")
            self._fixture(baked, [{"id": "GONE-AWAY-001", "contract": ["X."]}])
            self.assertEqual(R.check_viewer_data_sync(baked, []), ["GONE-AWAY-001"])

    def test_repo_fixture_is_in_sync_with_its_own_registry(self):
        """The end-to-end assertion the two tests above only approximate: THIS repo's
        baked.json against THIS repo's committed _map.json. Skipped where either is
        absent (a seeded consumer copy has neither)."""
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(R.__file__))))
        baked = os.path.join(root, "app", "src", "lib", "baked.json")
        map_json = os.path.join(root, "plugin", "requirements", "_map.json")
        if not (os.path.exists(baked) and os.path.exists(map_json)):
            self.skipTest("not running inside the requirement-manager repo")
        with open(map_json, encoding="utf-8") as f:
            nodes = json.load(f)["nodes"]
        self.assertEqual(R.check_viewer_data_sync(baked, nodes), [])

    def test_matching_fixture_reports_no_drift(self):
        with tempfile.TemporaryDirectory() as d:
            baked = os.path.join(d, "baked.json")
            self._fixture(baked, [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}])
            map_nodes = [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}]
            self.assertEqual(R.check_viewer_data_sync(baked, map_nodes), [])

    def test_diverged_contract_text_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            baked = os.path.join(d, "baked.json")
            self._fixture(baked, [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}])
            map_nodes = [{"id": "FOO-BAR-001", "contract": ["It shall do Y instead."]}]
            self.assertEqual(R.check_viewer_data_sync(baked, map_nodes), ["FOO-BAR-001"])

    def test_missing_baked_id_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            baked = os.path.join(d, "baked.json")
            self._fixture(baked, [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}])
            # the requirement was deleted/renamed in the registry
            self.assertEqual(R.check_viewer_data_sync(baked, []), ["FOO-BAR-001"])

    def test_missing_fixture_file_returns_none(self):
        # fail-open: no viewer checked out (e.g. a shallow consumer clone) is not an error
        self.assertIsNone(R.check_viewer_data_sync("/no/such/baked.json", []))

    def test_bracket_in_contract_text_reports_no_drift(self):
        # The JavaScript fixture needed a bracket-aware scanner, because a naive regex
        # stopped at the first ']' inside a bullet describing `[a, b]` syntax. Read as
        # JSON the text is data; this pins that such a bullet still compares equal.
        with tempfile.TemporaryDirectory() as d:
            baked = os.path.join(d, "baked.json")
            bullet = 'Accepts an inline `[a, b]` list and a `{k: v}` block.'
            self._fixture(baked, [{"id": "FOO-BAR-001", "contract": [bullet]}])
            map_nodes = [{"id": "FOO-BAR-001", "contract": [bullet]}]
            self.assertEqual(R.check_viewer_data_sync(baked, map_nodes), [])

    def test_unreadable_fixture_returns_none(self):
        # Neither a non-UTF-8 file nor one that is not JSON may crash `gate`: both degrade
        # to "no comparison".
        with tempfile.TemporaryDirectory() as d:
            baked = os.path.join(d, "baked.json")
            with open(baked, "wb") as f:
                f.write(b"\xff\xfe garbage, not valid utf-8")
            self.assertIsNone(R.check_viewer_data_sync(baked, []))
            _write(baked, "const BAKED = [];")
            self.assertIsNone(R.check_viewer_data_sync(baked, []))

# Entry point stays LAST on purpose. It used to sit mid-file, above
# RoadmapSignals and ViewerDataSync, so `python test_reqmap.py` ran
# unittest.main() before those classes were even defined: 478 tests

class FindingsFreshness(unittest.TestCase):  # tested-by: ARCH-FINDINGS-010  # tested-by: REQ-FINDINGS-856
    """A committed _findings.md is a derived view: `map` refreshes it when present,
    `map --check` flags it stale, and neither ever creates it."""
    def _seed(self, d, items):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "AREA-X-001.md"), _req_with_verify("AREA-X-001", items))
        return rd

    def _map(self, d, rd, check=False):
        reqs = R.load_requirements(rd)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_map(R.Workspace(reqs, {}, rd), d, check)
        return code, buf.getvalue()

    def _findings(self, rd):
        with redirect_stdout(io.StringIO()):
            R.cmd_findings(R.load_requirements(rd), rd)

    def test_map_never_creates_findings(self):  # verifies: REQ-FINDINGS-856#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d, ["a?"])
            self._map(d, rd)
            self.assertFalse(os.path.exists(os.path.join(rd, "_findings.md")))

    def test_map_refreshes_existing_findings(self):  # verifies: REQ-FINDINGS-856#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d, ["a?"])
            self._findings(rd)
            self._seed(d, ["a?", "b?"])            # the requirement gains a question
            self._map(d, rd)
            with open(os.path.join(rd, "_findings.md"), encoding="utf-8") as f:
                self.assertIn("b?", f.read())

    def test_absent_findings_is_not_stale(self):  # verifies: REQ-FINDINGS-856#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d, ["a?"])
            self._map(d, rd)
            code, out = self._map(d, rd, check=True)
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)

    def test_fresh_findings_passes_check(self):
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d, ["a?"])
            self._findings(rd)
            self._map(d, rd)
            code, _ = self._map(d, rd, check=True)
            self.assertEqual(code, 0)

    def test_stale_findings_fails_check(self):  # verifies: REQ-FINDINGS-856#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d, ["a?"])
            self._findings(rd)
            self._map(d, rd)
            _write(os.path.join(rd, "_findings.md"), "# Open findings\n\n_stale copy_\n")
            code, out = self._map(d, rd, check=True)
            self.assertEqual(code, 1)
            self.assertIn("_findings.md", out)
            self.assertIn("stale", out)


class NextOrphanHint(unittest.TestCase):  # tested-by: ARCH-NEXT-013
    """An Orphans item whose node in the committed _map.json records a member is a
    scan-scope problem, not a missing tag — say so."""
    def _run(self, reqs, rd):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_next(R.Workspace(reqs, {}, rd))
        return code, buf.getvalue()

    def _reqs(self):
        return {"REQ-A-001": {"meta": {"status": "confirmed"}, "body": "# T\n"}}

    def test_note_names_recorded_member_and_code_flag(self):  # verifies: REQ-NEXT-884#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements"); os.makedirs(rd)
            _write(os.path.join(rd, "_map.json"), json.dumps({"nodes": [
                {"id": "REQ-A-001", "members": [{"role": "implements", "loc": ".githooks/pre-commit:2"}]}],
                "edges": []}))
            code, out = self._run(self._reqs(), rd)
            self.assertEqual(code, 0)
            self.assertIn("Orphans", out)                  # still an orphan for THIS scan
            self.assertIn(".githooks/pre-commit:2", out)
            self.assertIn("--code", out)

    def test_no_note_without_committed_map(self):  # verifies: REQ-NEXT-884#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements"); os.makedirs(rd)
            _, out = self._run(self._reqs(), rd)
            self.assertIn("Orphans", out)
            self.assertNotIn("--code", out)

    def test_no_note_when_map_records_no_member(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements"); os.makedirs(rd)
            _write(os.path.join(rd, "_map.json"), json.dumps({"nodes": [
                {"id": "REQ-A-001", "members": []}], "edges": []}))
            _, out = self._run(self._reqs(), rd)
            self.assertNotIn("--code", out)


class UntaggedIgnoreBucket(unittest.TestCase):  # tested-by: ARCH-NEXT-013
    # tested-by: REQ-NEXTUNTAGGED-1050
    def test_meta_prose_is_not_untagged(self):
        # verifies: REQ-NEXTUNTAGGED-1050#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "CLAUDE.md"), "# guide" + chr(10))
            _write(os.path.join(d, "TODO.md"), "- [ ] x" + chr(10))
            _write(os.path.join(d, "README.md"), "# readme" + chr(10))
            _write(os.path.join(d, "a.py"), "x = 1" + chr(10))
            out = R._scan_untagged(d)
            self.assertIn("a.py", out)
            self.assertIn("README.md", out)             # sync-only prose is still listed
            self.assertNotIn("CLAUDE.md", out)
            self.assertNotIn("TODO.md", out)


class DupesSkipPlaceholders(unittest.TestCase):  # tested-by: ARCH-SIMILAR-016  # tested-by: REQ-SIMILAR-921
    def _req(self, title, contract):
        return {"body": "# {t}" + chr(10) + chr(10) + "> {t} intent." + chr(10) + chr(10)
                + "## WHAT — Contract (normative)" + chr(10) + "- {c}" + chr(10)}

    def test_placeholder_drafts_are_skipped_with_count(self):  # verifies: REQ-SIMILAR-921#CASE-5
        reqs = {
            "DRAFT-A": {"body": "# A" + chr(10) + chr(10) + "> DRAFT extracted from a.py." + chr(10) + chr(10)
                        + "## WHAT — Contract (normative)" + chr(10) + "- TODO: the observed behavior (characterization)." + chr(10)},
            "DRAFT-B": {"body": "# B" + chr(10) + chr(10) + "> DRAFT extracted from b.py." + chr(10) + chr(10)
                        + "## WHAT — Contract (normative)" + chr(10) + "- TODO: the observed behavior (characterization)." + chr(10)},
            "REQ-X-001": {"body": "# Upload" + chr(10) + chr(10) + "> Upload intent." + chr(10) + chr(10)
                          + "## WHAT — Contract (normative)" + chr(10) + "- `upload` stores the file under the tenant bucket." + chr(10)},
            "REQ-Y-002": {"body": "# Upload copy" + chr(10) + chr(10) + "> Upload copy intent." + chr(10) + chr(10)
                          + "## WHAT — Contract (normative)" + chr(10) + "- `upload` stores the file under the tenant bucket." + chr(10)},
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35)
        out = buf.getvalue()
        self.assertIn("skipped 2 requirement(s)", out)
        self.assertNotIn("DRAFT-A", out.split("skipped", 1)[1].split(chr(10), 1)[1])
        self.assertIn("REQ-X-001  <->  REQ-Y-002", out)


class MapDocument(unittest.TestCase):  # tested-by: ARCH-MAPDIAGRAMS-055  # tested-by: REQ-MAPDIAGRAMS-874, REQ-MAPDIAGRAMS-876, REQ-MAPDIAGRAMS-877, REQ-MAPDIAGRAMS-878
    """The document `map` writes: its diagram blocks, their legends, and the graph behind them."""

    DATA = {
        "nodes": [
            {"id": "SYS-A-101", "level": "system", "layer": "need", "status": "confirmed",
             "area": "SYS", "members": [], "deps": [], "risks": []},
            {"id": "REQ-B-001", "level": "architecture", "layer": "feature",
             "status": "confirmed", "area": "REQ", "members": [], "deps": [], "risks": []},
            {"id": "REQ-B-200", "level": "code", "layer": "feature", "status": "draft",
             "area": "REQ", "members": [], "deps": [], "risks": []},
            {"id": "REQ-B-201", "level": "code", "layer": "feature", "status": "draft",
             "area": "REQ", "members": [], "deps": [], "risks": []},
        ],
        "edges": [],
        "upstream_edges": [["REQ-B-001", "SYS-A-101"],
                           ["REQ-B-200", "REQ-B-001"], ["REQ-B-201", "REQ-B-001"]],
    }

    def test_the_document_carries_four_blocks(self):  # verifies: ARCH-MAPDIAGRAMS-055#CASE-1  # verifies: REQ-MAPDIAGRAMS-874#CASE-2
        md = R._build_md_text(dict(self.DATA, todos=[]))
        self.assertEqual(md.count("```mermaid"), 4)
        self.assertNotIn("Specification Hierarchy", md)

    def test_the_legend_matches_the_diagram_order(self):  # bug: legend-md-missing-hierarchy-entry  # verifies: REQ-MAPDIAGRAMS-874#CASE-3
        # _LEGEND_MD must carry one entry per diagram _build_md_text emits, in the same
        # order -- a missing entry shifts every caption by one and leaves the LAST
        # diagram (Risk & Unknowns) with an empty legend. It caught that when the
        # Specification Hierarchy was ADDED without its entry; removing that diagram
        # has the same failure mode in the other direction.
        self.assertEqual(len(R._LEGEND_MD), 4)
        md = R._build_md_text(dict(self.DATA, todos=[]))
        idx = md.index("## System Map")
        self.assertIn("thick border = bus", md[idx:idx + 400])
        idx = md.index("## Risk & Unknowns")
        self.assertIn("unimplemented", md[idx:idx + 400])

    def test_the_graph_carries_the_satisfies_edges(self):
        # They were computed since ARCH-TRACE-020 and dropped by _build_json_text until now.
        payload = json.loads(R._build_json_text(dict(self.DATA, repo=None, todos=[])))
        self.assertEqual(len(payload["upstream_edges"]), 3)


class PlanCadence(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-PLANCADENCE-1000  # tested-by: REQ-PLANBRANCH-1011 @unit
    """The release cadence: stated as a rhythm, computed once, emitted as dates."""

    BARS = [{"title": "a", "lane": "Engine", "start": "2026-09-13", "end": "2026-09-30"}]

    def _load(self, **extra):
        with tempfile.TemporaryDirectory() as d:
            payload = dict({"bars": self.BARS}, **extra)
            _write(os.path.join(d, "_planning.json"), json.dumps(payload))
            return R.load_targets(d)

    def test_a_weekly_cadence_lands_on_its_weekday(self):  # verifies: REQ-PLANCADENCE-1000#CASE-1
        got = self._load(cadence={"every": "week"})
        self.assertEqual("friday", got["cadence"]["on"])
        self.assertEqual(["2026-09-18", "2026-09-25"], got["releases"])

    def test_no_cadence_block_means_no_releases(self):  # verifies: REQ-PLANCADENCE-1000#CASE-2
        got = self._load()
        self.assertNotIn("cadence", got)
        self.assertNotIn("releases", got)

    def test_an_unimplemented_period_yields_nothing(self):  # verifies: REQ-PLANCADENCE-1000#CASE-3
        # Not "fall back to weekly": a plan that asked for a fortnight and got a week
        # would be wrong on every other marker, which is worse than no marker at all.
        got = self._load(cadence={"every": "fortnight"})
        self.assertNotIn("cadence", got)
        self.assertNotIn("releases", got)

    def test_a_cadence_naming_no_period_is_weekly_on_friday(self):  # verifies: REQ-PLANCADENCE-1000#CASE-7
        got = self._load(cadence={})
        self.assertEqual(("week", "friday"), (got["cadence"]["every"], got["cadence"]["on"]))
        self.assertEqual(["2026-09-18", "2026-09-25"], got["releases"])

    def test_the_weekday_is_chosen_and_from_narrows_the_span(self):  # verifies: REQ-PLANCADENCE-1000#CASE-4
        got = self._load(
            bars=[{"title": "a", "lane": "Engine", "start": "2026-09-13", "end": "2026-10-05"}],
            cadence={"every": "week", "on": "monday", "from": "2026-09-21"})
        self.assertEqual(["2026-09-21", "2026-09-28", "2026-10-05"], got["releases"])

    def test_the_branch_reaches_the_export_and_is_not_gated(self):  # verifies: REQ-PLANBRANCH-1011#CASE-1  # verifies: REQ-PLANBRANCH-1011#CASE-2
        # Git-derived like `repo`: two checkouts of one corpus disagree about it, so
        # comparing it would fail `map --check` on every branch and every fork.
        self.assertIn('"branch":', R._strip_generated('{"branch": "main"}') or "")
        stripped = R._strip_generated('  "branch": "main",' + '\n' + '  "nodes": []' + '\n')
        self.assertNotIn("branch", stripped)
        self.assertIn("nodes", stripped)

    def test_a_detached_head_reports_no_branch(self):  # verifies: REQ-PLANBRANCH-1011#CASE-3
        # `rev-parse --abbrev-ref HEAD` answers the literal "HEAD" when detached, which
        # is not a branch: absent beats a name that names nothing.
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R.git._git_branch(d))

    def test_a_plan_covering_no_dates_still_gets_a_calendar(self):  # verifies: REQ-PLANHORIZON-1010#CASE-2  # verifies: REQ-PLANCADENCE-1000#CASE-5
        # Reverses REQ-PLANCADENCE-1000 CASE-5, which read "a cadence needs something to
        # run alongside". The case it was written for is the one that turned out to
        # matter: a repo that has planned nothing is exactly the one that needs a
        # calendar to plan on, and `init` now seeds a `_planning.json` to give it one.
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_planning.json"),
                   json.dumps({"cadence": {"every": "month"}}))
            got = R.load_targets(d)
        self.assertIn("cadence", got)
        self.assertTrue(got["releases"], "an empty plan must still carry its calendar")
        # ...and it reaches the shared horizon rather than stopping at today.
        self.assertGreaterEqual(got["releases"][-1], R.default_horizon()[:7])

    def test_the_horizon_is_the_year_end_or_three_months_whichever_is_later(self):  # verifies: REQ-PLANHORIZON-1010#CASE-1
        import datetime
        # Mid-year the year end wins; from October the quarter does, which is the point:
        # a plan that only ever ran to 31 Dec would show one month in December.
        self.assertEqual("2026-12-31", R.default_horizon(datetime.date(2026, 9, 15)))
        self.assertEqual("2027-03-31", R.default_horizon(datetime.date(2026, 12, 31)))
        self.assertEqual("2027-12-31", R.default_horizon(datetime.date(2027, 1, 15)))

    def test_a_monthly_cadence_lands_on_each_month_end(self):  # verifies: REQ-PLANCADENCE-1000#CASE-6
        got = self._load(bars=[{"title": "a", "lane": "E", "start": "2026-09-13",
                                "end": "2026-12-05"}],
                         cadence={"every": "month"})
        self.assertEqual("last", got["cadence"]["on"])
        self.assertEqual(["2026-09-30", "2026-10-31", "2026-11-30"], got["releases"])

    def test_a_monthly_cadence_can_name_a_day(self):
        # Capped at 28 on purpose: a plan pinned to the 30th silently skips February.
        got = self._load(bars=[{"title": "a", "lane": "E", "start": "2026-09-01",
                                "end": "2026-11-10"}],
                         cadence={"every": "month", "on": 15})
        self.assertEqual(["2026-09-15", "2026-10-15"], got["releases"])

    def test_a_long_span_truncates_rather_than_thinning(self):
        got = self._load(bars=[{"title": "a", "lane": "E", "start": "2026-01-01", "end": "2040-01-01"}],
                         cadence={"every": "week"})
        self.assertEqual(R.targets.CADENCE_MAX, len(got["releases"]))

    def test_the_dates_reach_the_map_export(self):  # verifies: REQ-PLANCADENCE-1000#CASE-1
        # The chart reads `planning.releases` off _map.json; a value computed and not
        # emitted is the same as no cadence at all.
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-P-001.md"), _spec("AREA-P-001", ["`gate` writes the lock."]))
            _write(os.path.join(d, "mod.py"), tag("AREA-P-001") + "\ndef f():\n    return 1\n")
            _write(os.path.join(rd, "_planning.json"),
                   json.dumps({"bars": self.BARS, "cadence": {"every": "week"}}))
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(reqs, members, rd), d)
            payload = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
        self.assertEqual(["2026-09-18", "2026-09-25"], payload["planning"]["releases"])


class PlanStale(unittest.TestCase):  # tested-by: ARCH-ROADMAP-038  # tested-by: REQ-PLANSTALE-1013 @unit
    """A plan that schedules a version already declared is reported, read-only."""

    def _stale(self, milestones=(), bars=(), plugin=None, changelog=None):
        with tempfile.TemporaryDirectory() as d:
            reqs = os.path.join(d, "requirements")
            os.makedirs(reqs)
            plan = {"milestones": {m: {"due": "2026-09-30"} for m in milestones},
                    "bars": [{"title": "b", "start": "2026-09-21", "milestone": m}
                             for m in bars]}
            _write(os.path.join(reqs, "_planning.json"), json.dumps(plan))
            if plugin:
                _write(os.path.join(d, ".claude-plugin", "plugin.json"),
                       json.dumps({"version": plugin}))
            if changelog:
                _write(os.path.join(d, "CHANGELOG.md"),
                       "# Changelog\n\n## plugin `{}` — 2026-09-16\n\n**x.**\n"
                       .format(changelog))
            return (R.stale_plan_milestones(reqs, d),
                    [ln for ln in [R._plan_stale_line(d, reqs)] if ln])

    def test_a_milestone_equal_to_the_declared_version_is_stale(self):  # verifies: REQ-PLANSTALE-1013#CASE-1
        got, lines = self._stale(milestones=["v7.19.0", "v7.20.0"], plugin="7.19.0")
        self.assertEqual({"baseline": "v7.19.0", "source": "plugin.json",
                          "milestones": ["v7.19.0"]}, got)
        self.assertEqual(1, sum("_planning.json schedules v7.19.0 " in ln for ln in lines))

    def test_a_milestone_past_the_baseline_is_silent(self):  # verifies: REQ-PLANSTALE-1013#CASE-2
        got, lines = self._stale(milestones=["v7.20.0"], plugin="7.19.0")
        self.assertIsNone(got)
        self.assertFalse([ln for ln in lines if "_planning.json schedules" in ln])

    def test_a_patch_past_the_baseline_is_silent_and_a_short_key_is_padded(self):  # verifies: REQ-PLANSTALE-1013#CASE-3
        got, _ = self._stale(milestones=["v7.19.1"], changelog="v7.19.0")
        self.assertIsNone(got)
        got, _ = self._stale(milestones=["v7.19"], changelog="v7.19.0")
        self.assertEqual(["v7.19"], got["milestones"])

    def test_no_baseline_source_means_no_signal(self):  # verifies: REQ-PLANSTALE-1013#CASE-4
        got, _ = self._stale(milestones=["v0.1.0"])
        self.assertIsNone(got)

    def test_the_highest_source_wins_and_bars_count(self):  # verifies: REQ-PLANSTALE-1013#CASE-5
        # The manifest trails the CHANGELOG here; a baseline read from one source only
        # would pass a bar planned on the line the CHANGELOG already shipped.
        got, _ = self._stale(bars=["v7.19.0", "later"], plugin="7.18.0", changelog="v7.19.0")
        self.assertEqual({"baseline": "v7.19.0", "source": "CHANGELOG.md",
                          "milestones": ["v7.19.0"]}, got)

    def test_the_signal_is_not_a_gate_rule(self):  # verifies: REQ-PLANSTALE-1013#CASE-6
        # Precedent (decided 2026-09-14): roadmap coherence is reported, never
        # gated, so the planning module registers no rule and the gate stays green.
        self.assertFalse([r.id for r in R.GATE_RULES if r.fn.__module__.endswith("versions")])
        with open(R.versions.__file__, encoding="utf-8") as f:
            self.assertNotIn("@gate_rule", f.read())


class ShippedHistory(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-HISTORY-1003
    """What already shipped, read from CHANGELOG.md and grouped by calendar month."""

    LOG = "\n".join([
        "# Changelog",
        "",
        "## plugin `v2.1.1` — 2026-06-20",
        "",
        "**A patch.** It fixed the thing.",
        "",
        "## plugin `v2.1.0` — 2026-06-12",
        "",
        "**A minor.** It added the thing.",
        "",
        "## plugin `v2.0.0` — 2026-06-02",
        "",
        "**First feature release. Highlights:**",
        "",
        "The breaking rename of every verb.",
        "",
        "- a bullet that is not the headline",
        "",
        "## plugin `v1.9.0` — superseded, never released",
        "",
        "**Never shipped.** Its body must not be read as v2.0.0's.",
        "",
    ])

    def test_dated_headings_are_read_newest_first(self):  # verifies: REQ-HISTORY-1003#CASE-1
        got = R.history.parse_changelog(self.LOG)
        self.assertEqual(["v2.1.1", "v2.1.0", "v2.0.0"], [e["version"] for e in got])
        self.assertEqual("2026-06-20", got[0]["date"])
        self.assertEqual("A patch", got[0]["headline"])

    def test_an_undated_heading_is_skipped(self):  # verifies: REQ-HISTORY-1003#CASE-2
        # This repo carries `## plugin `v3.5.0` — superseded, never released`. A version
        # that never shipped has no place on a timeline of what shipped — and its body
        # must not be absorbed into the dated entry above it either.
        got = R.history.parse_changelog(self.LOG)
        self.assertNotIn("v1.9.0", [e["version"] for e in got])
        self.assertNotIn("Never shipped", got[-1]["headline"])

    def test_a_colon_terminated_bold_run_is_a_lead_in(self):  # verifies: REQ-HISTORY-1003#CASE-3
        got = R.history.parse_changelog(self.LOG)
        self.assertEqual("The breaking rename of every verb", got[2]["headline"])

    def test_months_group_and_the_landmark_is_the_biggest_step(self):  # verifies: REQ-HISTORY-1003#CASE-4
        rows = R.history.by_month(R.history.parse_changelog(self.LOG))
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual("2026-06", row["month"])
        self.assertEqual(3, row["count"])
        self.assertEqual(["v2.0.0", "v2.1.0", "v2.1.1"], row["versions"])
        # not the first by date and not the last — the biggest step
        self.assertEqual("v2.0.0", row["landmark"])
        self.assertEqual("2026-06-02", row["first"])
        self.assertEqual("2026-06-20", row["last"])
        # every release in the month, newest first, so selecting it shows what was done
        self.assertEqual(["v2.1.1", "v2.1.0", "v2.0.0"], [e["version"] for e in row["entries"]])
        self.assertEqual("The breaking rename of every verb",
                         next(e for e in row["entries"] if e["version"] == "v2.0.0")["headline"])

    def test_a_repo_with_no_changelog_yields_nothing(self):  # verifies: REQ-HISTORY-1003#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([], R.history.read_history(d))

    def test_a_bullet_is_not_mistaken_for_a_headline_and_bold_is_not_a_bullet(self):
        # `* ` with the space is a bullet; `**` opens the headline every entry carries.
        # Skipping on a bare `*` threw away the headline of every single entry.
        self.assertEqual("Bold", R.history._headline("**Bold.** rest\n"))
        self.assertEqual("plain", R.history._headline("* a bullet\nplain\n"))

    def test_the_rows_reach_the_map_export(self):  # verifies: REQ-HISTORY-1003#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-H-001.md"), _spec("AREA-H-001", ["`gate` writes the lock."]))
            _write(os.path.join(d, "mod.py"), tag("AREA-H-001") + "\ndef f():\n    return 1\n")
            _write(os.path.join(d, "CHANGELOG.md"), self.LOG)
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(reqs, members, rd), d)
            payload = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
        self.assertEqual(1, len(payload["history"]))
        self.assertEqual("v2.0.0", payload["history"][0]["landmark"])


class PlanDrift(unittest.TestCase):  # tested-by: ARCH-PLANDRIFT-069  # tested-by: REQ-PLANDRIFT-1002
    """Plan drift, and the six false-positive classes it was built around.

    Each test below names the one it guards; deleting the guard is meant to fail here
    rather than quietly re-admit the report the consumer measured."""

    def _repo(self, d, files):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "AREA-D-001.md"), _spec("AREA-D-001", ["`gate` writes the lock."]))
        for rel, body in files.items():
            _write(os.path.join(d, rel.replace("/", os.sep)), body)
        return rd

    def test_the_longest_extension_wins(self):  # verifies: REQ-PLANDRIFT-1002#CASE-1
        # `ts` before `tsx` in the alternation cost the consumer nine false positives in
        # one run: the `x` is left orphaned and the file "does not exist".
        got = R.plandrift.cited_refs("see src/EmployeeDocumentList.tsx for the list")
        self.assertEqual(["src/EmployeeDocumentList.tsx"], got["paths"])

    def test_a_shortened_path_resolves_and_a_wrong_one_does_not(self):  # verifies: REQ-PLANDRIFT-1002#CASE-2
        known = {"apps/api/app/common/errors.py", "apps/api/app/signing/x.py"}
        self.assertEqual("apps/api/app/common/errors.py",
                         R.plandrift._resolves("app/common/errors.py", known))
        self.assertIsNone(R.plandrift._resolves("app/documents/errors.py", known))

    def test_a_partial_filename_is_not_a_suffix_match(self):  # verifies: REQ-PLANDRIFT-1002#CASE-3
        # A plain `endswith` would call `clarify.py` a match for `my_clarify.py` and
        # quietly rehabilitate a real typo. Segments, not characters.
        self.assertIsNone(R.plandrift._resolves("my_clarify.py", {"pkg/clarify.py"}))
        self.assertEqual("pkg/clarify.py", R.plandrift._resolves("clarify.py", {"pkg/clarify.py"}))

    def test_a_symbol_is_looked_for_across_the_whole_tree(self):
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, {"mod.py": tag("AREA-D-001") + "\ndef to_response():\n    return 1\n",
                                "other.py": "# nothing here\n"})
            items = [{"name": "fix `to_response` in `other.py`", "context": "", "done": False}]
            got = R.plandrift.plan_drift(items, d, rd)
        # The symbol lives in a file the item does not name. That is an imprecision, not
        # a drift — reporting it is what made the consumer's first run unreadable.
        self.assertEqual([], got["sure"])

    def test_a_symbol_absent_from_the_code_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, {"mod.py": tag("AREA-D-001") + "\ndef f():\n    return 1\n",
                                "notes.md": "we used to have `decrypt_cnp` here\n"})
            items = [{"name": "fix `decrypt_cnp`", "context": "", "done": False}]
            got = R.plandrift.plan_drift(items, d, rd)
        # Prose is indexed for paths, not for symbols: a changelog records what a name
        # USED to be, and counting that as existing makes the check permanently silent.
        self.assertEqual(["decrypt_cnp"], got["sure"][0]["symbols"])

    def test_a_path_nothing_resembles_is_a_target_not_a_stale_reference(self):  # verifies: REQ-PLANDRIFT-1002#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, {"mod.py": tag("AREA-D-001") + "\ndef f():\n    return 1\n"})
            items = [{"name": "move it to docs/history/ARCHIVE.md", "context": "", "done": False}]
            got = R.plandrift.plan_drift(items, d, rd)
        self.assertEqual([], got["sure"])

    def test_a_deleted_file_under_a_live_directory_is_reported(self):  # verifies: ARCH-PLANDRIFT-069#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, {"pkg/mod.py": tag("AREA-D-001") + "\ndef f():\n    return 1\n"})
            items = [{"name": "fix pkg/gone.py", "context": "", "done": False}]
            got = R.plandrift.plan_drift(items, d, rd)
        self.assertEqual(["pkg/gone.py"], got["sure"][0]["paths"])

    def test_a_version_is_not_a_date(self):  # verifies: REQ-PLANDRIFT-1002#CASE-5
        # `\b\d{4}-\d{2}-\d{2}\b` matches the date half of `2026-06-19.1`, because `.` is
        # a word boundary. The item was then dated off a version string it merely quoted.
        items = [{"name": "re-vendor the engine (2026-06-19.1)", "context": "", "done": False,
                  "section_date": "2026-09-05"}]
        self.assertEqual(["2026-09-05"], R.plandrift.item_dates(items))

    def test_an_item_with_no_date_inherits_its_sections(self):  # verifies: REQ-PLANDRIFT-1002#CASE-6
        # The trap that mattered most: an audit batch carries its date ONCE, in the
        # section's opening paragraph. Without inheritance the freshness check skipped
        # exactly the items it was written for.
        items = [{"name": "first", "context": "", "done": False, "section_date": "2026-09-05"},
                 {"name": "second", "context": "", "done": False}]
        self.assertEqual(["2026-09-05", "2026-09-05"], R.plandrift.item_dates(items))

    def test_a_done_item_is_not_examined(self):
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, {"pkg/mod.py": tag("AREA-D-001") + "\ndef f():\n    return 1\n"})
            items = [{"name": "fix pkg/gone.py", "context": "", "done": True}]
            got = R.plandrift.plan_drift(items, d, rd)
        self.assertEqual([], got["sure"])

    def test_a_clean_plan_prints_nothing(self):  # verifies: ARCH-PLANDRIFT-069#CASE-3
        self.assertEqual([], R.plandrift.plan_drift_lines({"sure": [], "rederive": []}))

    def test_a_file_committed_after_the_item_is_worth_re_reading(self):  # verifies: ARCH-PLANDRIFT-069#CASE-2
        # The case the module exists for: the path, the symbol and the line are all still
        # correct and the code was fixed underneath them. The only signal is the date, so
        # this bucket says "read it", never "close it" — and stays separate from `sure`.
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, {"pkg/mod.py": tag("AREA-D-001") + "\ndef f():\n    return 1\n"})
            for args in (["init", "-q"], ["add", "-A"],
                         ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"]):
                if R.git._git(args, cwd=d) is None:
                    self.skipTest("git unavailable")
            items = [{"name": "still true of pkg/mod.py", "context": "as of 2000-01-01",
                      "done": False}]
            got = R.plandrift.plan_drift(items, d, rd)
        self.assertEqual([], got["sure"])
        self.assertEqual(1, len(got["rederive"]))
        self.assertEqual("pkg/mod.py", got["rederive"][0]["files"][0]["path"])
        self.assertEqual("2000-01-01", got["rederive"][0]["since"])

    def test_the_roadmap_parser_carries_context_and_the_section_date(self):  # verifies: REQ-PLANDRIFT-1002#CASE-6
        plan = "\n".join([
            "## Now",
            "",
            "Audited 2026-09-05 across eight areas.",
            "",
            "- [ ] fix the thing | req: AREA-D-001",
            "      <!-- cites `pkg/mod.py` -->",
            "- [ ] the second one",
            "",
        ])
        items = R.mapdata._parse_roadmap_from_text(plan)
        self.assertEqual("2026-09-05", items[0]["section_date"])
        self.assertIn("pkg/mod.py", items[0]["context"])
        self.assertEqual("", items[1]["context"])


class RoadmapPlan(unittest.TestCase):  # tested-by: ARCH-ROADMAP-038  # tested-by: REQ-ROADMAP-998
    """ROADMAP.md: the horizon plan, and the two claims in it a machine can check."""

    PLAN = "\n".join([
        "# Roadmap",
        "",
        "## Now",
        "- [ ] ship the thing | req: AREA-A-001",
        "- [x] shipped already | req: AREA-A-001",
        "",
        "## Later",
        "- [ ] parked with a reason | unpark: someone asks for it",
        "- [ ] parked with no reason",
        "",
        "## Someday",
        "- [ ] under an invented heading | req: AREA-A-001",
        "",
    ])

    def _audit(self, d, plan):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "AREA-A-001.md"), _spec("AREA-A-001", ["`gate` writes the lock."]))
        _write(os.path.join(d, "mod.py"), tag("AREA-A-001") + "\ndef f():\n    return 1\n")
        if plan is not None:
            _write(os.path.join(d, "ROADMAP.md"), plan)
        reqs = R.load_requirements(rd)
        members = R.scan_members(d, rd)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_audit(R.Workspace(reqs, members, rd, d))
        return buf.getvalue()

    def test_it_reads_items_under_the_reserved_horizons(self):  # verifies: REQ-ROADMAP-998#CASE-1
        items = R.mapdata._parse_roadmap_from_text(self.PLAN)
        self.assertEqual(["now", "now", "later", "later"], [i["horizon"] for i in items])
        self.assertEqual("AREA-A-001", items[0]["req"])
        self.assertTrue(items[1]["done"])
        self.assertEqual("someone asks for it", items[2]["unpark"])
        self.assertIsNone(items[3]["unpark"])

    def test_a_category_heading_groups_the_items_under_it(self):  # verifies: REQ-ROADMAP-998#CASE-6
        plan = ("## Now\n\n- [ ] first | req: AREA-A-001\n\n### Viewer\n\n"
                "- [ ] second | req: AREA-A-001\n\n## Later\n\n- [ ] third | unpark: x\n")
        items = R.mapdata._parse_roadmap_from_text(plan)
        self.assertEqual([None, "Viewer", None], [i["category"] for i in items])
        self.assertEqual("", items[0]["context"])   # the heading is not the first item's prose

    def test_an_item_under_an_invented_heading_is_skipped(self):  # verifies: REQ-ROADMAP-998#CASE-2
        # `## Someday` carries one item; it must not leak in under the horizon above it.
        names = [i["name"] for i in R.mapdata._parse_roadmap_from_text(self.PLAN)]
        self.assertNotIn("under an invented heading", names)

    def test_a_req_that_names_nothing_is_reported(self):  # verifies: REQ-ROADMAP-998#CASE-3
        plan = "## Now\n- [ ] ship the thing | req: NOPE-X-999\n"
        with tempfile.TemporaryDirectory() as d:
            out = self._audit(d, plan)
        self.assertIn("NOPE-X-999", out)
        self.assertIn("points at nothing", out)

    def test_a_parked_item_with_no_condition_is_reported(self):  # verifies: REQ-ROADMAP-998#CASE-4
        with tempfile.TemporaryDirectory() as d:
            out = self._audit(d, self.PLAN)
        self.assertIn("Later` item(s) carry no `unpark:`", out)

    def test_a_repo_with_no_roadmap_sees_nothing(self):  # verifies: REQ-ROADMAP-998#CASE-5
        with tempfile.TemporaryDirectory() as d:
            out = self._audit(d, None)
        self.assertNotIn("ROADMAP.md", out)


class Redundancy(unittest.TestCase):  # tested-by: REQ-REDUNDANCY-058
    """`_redundant_groups` is the exact-match floor under `dupes`: no threshold, so a
    group is a duplicate by construction rather than a judgement call."""

    def _req(self, clause, status="confirmed"):
        return {"meta": {"status": status},
                "body": "# T\n\n## Description\n- " + clause + "\n\n"
                        "## Cases (= tests)\nCASE-1\n  Then it holds\n"}

    def test_identical_contracts_group_together(self):  # verifies: REQ-REDUNDANCY-058#CASE-1
        reqs = {"A-X-001": self._req("`x` does the thing."),
                "A-Y-002": self._req("`x` does the thing."),
                "A-Z-003": self._req("`y` does something else.")}
        self.assertEqual(R._redundant_groups(reqs), [["A-X-001", "A-Y-002"]])

    def test_case_and_whitespace_do_not_hide_a_duplicate(self):  # verifies: REQ-REDUNDANCY-058#CASE-2
        reqs = {"A-X-001": self._req("`x` does   the thing."),
                "A-Y-002": self._req("`X` DOES the thing.")}
        self.assertEqual(R._redundant_groups(reqs), [["A-X-001", "A-Y-002"]])

    def test_a_different_clause_is_not_a_duplicate(self):  # verifies: REQ-REDUNDANCY-058#CASE-3
        reqs = {"A-X-001": self._req("`x` does the thing."),
                "A-Y-002": self._req("`x` does the thing, twice.")}
        self.assertEqual(R._redundant_groups(reqs), [])

    def test_draft_placeholders_are_not_duplicates_of_each_other(self):  # verifies: REQ-REDUNDANCY-058#CASE-4
        # every scaffolded draft carries the same TODO line; counting those would report
        # the scaffold as a duplicate of itself once per draft and bury the real finding.
        reqs = {"A-X-001": self._req("TODO: the observed behavior.", status="draft"),
                "A-Y-002": self._req("TODO: the observed behavior.", status="draft")}
        self.assertEqual(R._redundant_groups(reqs), [])

    def test_a_requirement_with_no_clauses_is_skipped(self):
        reqs = {"A-X-001": {"meta": {"status": "confirmed"}, "body": "# T\n\nno sections\n"},
                "A-Y-002": {"meta": {"status": "confirmed"}, "body": "# T\n\nnothing here\n"}}
        self.assertEqual(R._redundant_groups(reqs), [])

    def test_three_way_group_is_one_finding(self):
        reqs = {i: self._req("`x` does the thing.") for i in ("A-A-001", "A-B-002", "A-C-003")}
        groups = R._redundant_groups(reqs)
        self.assertEqual(groups, [["A-A-001", "A-B-002", "A-C-003"]])
        self.assertEqual(sum(len(g) - 1 for g in groups), 2)   # two could be folded away

    def test_next_reports_the_group_and_writes_nothing(self):  # verifies: REQ-NEXT-884#CASE-7  # verifies: REQ-REDUNDANCY-058#CASE-5
        with tempfile.TemporaryDirectory() as d:
            for rid in ("AREA-A-001", "AREA-B-002"):
                _write(os.path.join(d, rid + ".md"),
                       REQ.format(id=rid, status="confirmed", layer="bus", extra="", title=rid)
                       + "\n## Description\n- `x` does the thing.\n\n"
                         "## Cases (= tests)\nCASE-1\n  Then it holds\n")
            before = sorted(os.listdir(d))
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_next(R.Workspace(reqs, R.scan_members(d, d)))
            out = buf.getvalue()
            self.assertIn("Redundancy (1)", out)
            self.assertIn("AREA-A-001, AREA-B-002", out)
            self.assertIn("identical contract", out)
            self.assertEqual(sorted(os.listdir(d)), before)     # read-only

    def test_gate_stays_silent_about_redundancy(self):  # verifies: REQ-REDUNDANCY-058#CASE-5
        # the hook runs `gate` on every commit; a corpus-shape advisory there is noise
        with tempfile.TemporaryDirectory() as d:
            for rid in ("AREA-A-001", "AREA-B-002"):
                _write(os.path.join(d, rid + ".md"),
                       REQ.format(id=rid, status="draft", layer="bus", extra="", title=rid)
                       + "\n## Description\n- `x` does the thing.\n\n"
                         "## Cases (= tests)\nCASE-1\n  Then it holds\n")
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, R.scan_members(d, d), d, d), False)
            self.assertNotIn("identical contract", buf.getvalue())
            self.assertNotIn("Redundancy", buf.getvalue())


class Stage2Engine(unittest.TestCase):  # tested-by: ARCH-CONFIG-060  # tested-by: REQ-CONFIG-949  # tested-by: REQ-SCANCACHE-911  # tested-by: REQ-NEXT-886  # tested-by: REQ-SIMILAR-921  # tested-by: REQ-MAPDIAGRAMS-877
    """One walk with cache, the config file, and the verified-bug fixes of v3.3.0."""

    def _restore(self, *names):
        # restore on `config`, the module every engine reader looks the
        # value up in (`cfg.NAME`); setting it on the facade left an
        # override live for every test that ran after this one
        saved = {n: getattr(R.config, n) for n in names}
        self.addCleanup(
            lambda: [setattr(R.config, n, v) for n, v in saved.items()])

    def test_config_applies_a_numeric_threshold(self):  # verifies: REQ-CONFIG-949#CASE-1
        self._restore("LINT_AC_MAX")
        err = io.StringIO()
        with redirect_stderr(err):
            applied = R.apply_config({"LINT_AC_MAX": 12}, out=err)
        self.assertEqual(applied, ["LINT_AC_MAX"])
        self.assertEqual(R.LINT_AC_MAX, 12)
        self.assertEqual(err.getvalue(), "")

    def test_config_ignores_unknown_and_wrong_type(self):  # verifies: REQ-CONFIG-949#CASE-2
        self._restore("LINT_AC_MAX")
        err = io.StringIO()
        applied = R.apply_config({"NOPE": 1, "LINT_AC_MAX": "seven", "MAP_ENGINE_VERSION": "x"}, out=err)
        self.assertEqual(applied, [])
        self.assertEqual(R.LINT_AC_MAX, 7)
        self.assertIn("unknown key 'NOPE'", err.getvalue())
        self.assertIn("ignoring LINT_AC_MAX", err.getvalue())
        self.assertIn("unknown key 'MAP_ENGINE_VERSION'", err.getvalue())

    def test_config_merges_fanout_bands_and_extends_code_exts(self):  # verifies: REQ-CONFIG-949#CASE-3
        self._restore("LINT_FANOUT_BANDS", "CODE_EXTS")
        R.apply_config({"LINT_FANOUT_BANDS": {"system": [None, 12]}, "extra_code_exts": ["foo", ".bar"]},
                       out=io.StringIO())
        self.assertEqual(R.LINT_FANOUT_BANDS["system"], (None, 12))
        self.assertEqual(R.LINT_FANOUT_BANDS["architecture"], (None, 30))
        self.assertEqual(R.CODE_EXTS[-2:], (".foo", ".bar"))
        self.assertTrue(R._is_code_file("x.foo"))

    def test_config_file_is_read_fail_open(self):  # verifies: REQ-CONFIG-949#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(R.load_config(d), {})
            _write(os.path.join(d, "_config.json"), "{ not json")
            self.assertEqual(R.load_config(d), {})
            _write(os.path.join(d, "_config.json"), "[1, 2]")
            self.assertEqual(R.load_config(d), {})
            _write(os.path.join(d, "_config.json"), '{"LINT_AC_MAX": 9}')
            self.assertEqual(R.load_config(d), {"LINT_AC_MAX": 9})

    def test_scan_all_cache_covers_all_three_maps(self):  # verifies: REQ-SCANCACHE-911#CASE-6
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            os.makedirs(rq)
            _write(os.path.join(d, "a.py"), tag("A-X-001") + "\n")
            _write(os.path.join(d, "t.py"),
                   "# tested-by: A-X-001 @unit\ndef test_a():  # verifies: A-X-001#CASE-1\n    pass\n")
            plain = R.scan_all(d, rq)
            c1 = R.scan_all(d, rq, cache=True)
            c2 = R.scan_all(d, rq, cache=True)
            self.assertEqual(plain, c1)
            self.assertEqual(plain, c2)
            self.assertEqual(set(plain[1]["A-X-001"]), {"CASE-1"})
            self.assertEqual(set(plain[2]["A-X-001"]), {"unit"})
            cache = json.load(open(os.path.join(rq, "_scancache.json"), encoding="utf-8"))
            self.assertIn("ac", cache["t.py"])
            self.assertIn("lv", cache["t.py"])
            # an entry written by the older members-only cache is a miss, not a wrong hit
            cache["t.py"].pop("ac"); cache["t.py"].pop("lv")
            _write(os.path.join(rq, "_scancache.json"), json.dumps(cache))
            self.assertEqual(plain, R.scan_all(d, rq, cache=True))

    def test_untagged_skips_repo_boilerplate(self):  # verifies: REQ-NEXT-886#CASE-5
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            os.makedirs(rq)
            _write(os.path.join(d, "a.py"), "print(1)\n")
            _write(os.path.join(d, "docs", "adr", "0001-x.md"), "# ADR\n")
            _write(os.path.join(d, ".github", "ISSUE_TEMPLATE", "bug.yml"), "name: bug\n")
            _write(os.path.join(d, ".github", "PULL_REQUEST_TEMPLATE.md"), "# PR\n")
            _write(os.path.join(d, "SECURITY.md"), "# policy\n")
            _write(os.path.join(d, ".github", "dependabot.yml"), "version: 2\n")
            self.assertEqual(R._scan_untagged(d, rq), ["a.py"])

    def test_dupes_skips_a_parent_and_its_child(self):  # verifies: REQ-SIMILAR-921#CASE-7
        body = "## Description\n- the scanner walks the tree and collects membership tags per file\n"
        reqs = {"ARCH-A-001": {"meta": {"id": "ARCH-A-001"}, "body": body},
                "REQ-A-002": {"meta": {"id": "REQ-A-002", "satisfies": ["ARCH-A-001"]}, "body": body}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {})
        out = buf.getvalue()
        self.assertIn("skipped 1 pair(s) linked by tested-by or satisfies", out)
        self.assertNotIn("<->", out)

    def test_dupes_skips_two_children_of_one_parent(self):  # verifies: REQ-SIMILAR-921#CASE-7
        body = "## Description\n- the scanner walks the tree and collects membership tags per file\n"
        reqs = {"ARCH-A-001": {"meta": {"id": "ARCH-A-001"}, "body": "## Description\n- unrelated\n"},
                "REQ-A-002": {"meta": {"id": "REQ-A-002", "satisfies": ["ARCH-A-001"]}, "body": body},
                "REQ-A-003": {"meta": {"id": "REQ-A-003", "satisfies": ["ARCH-A-001"]}, "body": body},
                "REQ-B-004": {"meta": {"id": "REQ-B-004", "satisfies": ["ARCH-B-009"]}, "body": body}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {})
        out = buf.getvalue()
        # the two siblings are skipped; the cousin under another parent is still reported
        self.assertIn("skipped 1 pair(s) linked by tested-by or satisfies, or siblings", out)
        self.assertNotIn("REQ-A-002  <->  REQ-A-003", out)
        self.assertIn("REQ-A-002  <->  REQ-B-004", out)

    # tested-by: REQ-SIMILARIDS-1025 @unit
    def test_two_requirements_sharing_only_ids_are_not_a_pair(self):  # verifies: REQ-SIMILARIDS-1025#CASE-1
        reqs = {"REQ-A-001": {"meta": {}, "body": "## Description\n- alpha bravo [[REQ-X-001]] req: REQ-X-001\n"},
                "REQ-B-002": {"meta": {}, "body": "## Description\n- charlie delta [[REQ-X-001]] req: REQ-X-001\n"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {})
        self.assertNotIn("<->", buf.getvalue())

    def test_the_prose_around_an_id_is_still_compared(self):  # verifies: REQ-SIMILARIDS-1025#CASE-2
        clause = "- the scanner walks the tree and collects membership tags per file "
        reqs = {"REQ-A-001": {"meta": {}, "body": "## Description\n" + clause + "[[REQ-ALPHA-007]]\n"},
                "REQ-B-002": {"meta": {}, "body": "## Description\n" + clause + "[[REQ-BRAVO-008]]\n"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {})
        out = buf.getvalue()
        self.assertIn("REQ-A-001  <->  REQ-B-002", out)
        shared = out.split("shared terms:")[1].splitlines()[0]
        self.assertNotIn("alpha", shared)
        self.assertNotIn("req", shared.split(", "))

    def test_search_keeps_the_ids(self):  # verifies: REQ-SIMILARIDS-1025#CASE-3
        body = "## Description\n- the scanner walks the tree [[REQ-X-001]]\n"
        self.assertIn("REQ-X-001", R._sim_text(body))
        self.assertNotIn("REQ-X-001", R.similar._dupes_text(body))

    # tested-by: REQ-SIMILARDISTINCT-1026 @unit
    def test_a_recorded_distinct_pair_is_skipped_and_counted(self):  # verifies: REQ-SIMILARDISTINCT-1026#CASE-1
        body = "## Description\n- the scanner walks the tree and collects membership tags per file\n"
        reqs = {"REQ-A-001": {"meta": {"distinct_from": ["REQ-B-002"]}, "body": body},
                "REQ-B-002": {"meta": {}, "body": body},
                "REQ-C-003": {"meta": {}, "body": body}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {})
        out = buf.getvalue()
        self.assertIn("skipped 1 pair(s) a reviewer recorded as distinct", out)
        self.assertNotIn("REQ-A-001  <->  REQ-B-002", out)
        self.assertIn("REQ-A-001  <->  REQ-C-003", out)
        self.assertIn("REQ-B-002  <->  REQ-C-003", out)

    def test_a_deprecated_requirement_is_not_compared(self):  # verifies: REQ-SIMILARDISTINCT-1026#CASE-3
        body = "## Description\n- the scanner walks the tree and collects membership tags per file\n"
        reqs = {"REQ-A-001": {"meta": {"status": "deprecated"}, "body": body},
                "REQ-B-002": {"meta": {}, "body": body},
                "REQ-C-003": {"meta": {}, "body": "## Description\n- unrelated words entirely here\n"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {})
        out = buf.getvalue()
        self.assertIn("skipped 1 deprecated requirement(s)", out)
        self.assertNotIn("<->", out)

    def test_dupes_json_carries_every_pair_and_what_was_skipped(self):  # verifies: REQ-SIMILAR-923#CASE-7
        body = "## Description\n- the scanner walks the tree and collects membership tags per file\n"
        reqs = {"A-A-001": {"meta": {}, "body": body}, "A-B-002": {"meta": {}, "body": body},
                "A-C-003": {"meta": {"status": "deprecated"}, "body": body}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {}, top=0, as_json=True)
        rec = json.loads(buf.getvalue())
        self.assertEqual([("A-A-001", "A-B-002")], [(p["a"], p["b"]) for p in rec["pairs"]])
        self.assertIn("scanner", rec["pairs"][0]["shared"])
        self.assertEqual((1, 2), (rec["skipped"]["deprecated"], rec["compared"]))

    def test_dupes_top_truncates_with_a_count(self):  # verifies: REQ-SIMILAR-923#CASE-6
        body = "## Description\n- the scanner walks the tree and collects membership tags per file\n"
        reqs = {"A-A-001": {"meta": {}, "body": body}, "A-B-002": {"meta": {}, "body": body},
                "A-C-003": {"meta": {}, "body": body}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_similar(reqs, 0.35, {}, top=1)
        out = buf.getvalue()
        self.assertEqual(out.count("<->"), 1)
        self.assertIn("... 2 more pair(s)", out)

    def test_req_to_code_omits_code_level_nodes(self):  # verifies: REQ-MAPDIAGRAMS-877#CASE-5
        data = {"nodes": [
            {"id": "ARCH-A-001", "level": "architecture", "status": "confirmed", "layer": "feature",
             "area": "ARCH", "members": [{"role": "implements", "loc": "x.py:1"}]},
            {"id": "REQ-A-002", "level": "code", "status": "confirmed", "layer": "feature",
             "area": "REQ", "members": [{"role": "implements", "loc": "x.py:9"}]}],
            "edges": []}
        out = R._mermaid_req_to_code(data)
        self.assertIn("ARCH_A_001", out)
        self.assertNotIn("REQ_A_002", out)


class Audit(unittest.TestCase):  # tested-by: ARCH-AUDIT-065  # tested-by: REQ-AUDIT-970  # tested-by: REQ-AUDIT-971  # tested-by: REQ-AUDIT-972  # tested-by: REQ-AUDIT-973
    """`audit` runs every discovery pass and reports; only the gate reaches the exit code."""

    def _req(self, status="confirmed", level=None, exempt=None, body_extra="", satisfies=None):
        meta = {"status": status, "layer": "feature", "owner": "Alex"}
        if level:
            meta["level"] = level
        if exempt:
            meta["lint_exempt"] = exempt
        if satisfies:
            meta["satisfies"] = satisfies
        return {"meta": meta,
                "body": "# T\n\n## Description\n- It holds.\n\n"
                        "## Cases\nCASE-1\n  Then it holds\n" + body_extra}

    def _run(self, reqs, members, **kw):
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            rc = R.cmd_audit(R.Workspace(reqs, members, d, d), **kw)
        return rc, buf.getvalue()

    def _gate_rc(self, reqs, members):
        """The gate's own verdict on the same corpus, which is what the audit must echo."""
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            return R.cmd_check(R.Workspace(reqs, members, d, d), False)

    def _green(self):
        reqs = {"REQ-A-001": self._req()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        return reqs, members

    # ---- the report ------------------------------------------------------
    def test_every_section_runs(self):  # verifies: REQ-AUDIT-970#CASE-1
        _, out = self._run(*self._green())
        for section in ("Gate", "Risk", "Duplicates", "Tag coverage",
                        "Exemptions in force", "Corpus shape"):
            self.assertIn(section, out)

    def test_advisory_findings_never_fail_the_run(self):  # verifies: REQ-AUDIT-970#CASE-2
        """Two requirements with byte-identical contracts and a flat corpus: plenty to
        advise about. The audit's verdict must be the GATE's verdict on the same corpus,
        which is the contract — asserting a bare 0 would instead assert that this
        developer's tree happens to be clean."""
        reqs, members = self._green()
        reqs["REQ-B-002"] = self._req()
        members["REQ-B-002"] = [("implements", "y.py", 1), ("tested-by", "t.py", 2)]
        self.assertTrue(R._redundant_groups(reqs))       # there IS advice to give
        rc, _ = self._run(reqs, members)
        self.assertEqual(rc, self._gate_rc(reqs, members))

    def test_a_gate_error_fails_the_audit(self):  # verifies: REQ-AUDIT-970#CASE-3
        # a confirmed requirement with no `implements:` member is the gate's own error
        rc, out = self._run({"REQ-A-001": self._req()}, {})
        self.assertEqual(rc, 1)
        self.assertIn("Corpus shape", out)          # the advisory half still printed

    def test_a_raising_section_is_reported_not_fatal(self):  # verifies: REQ-AUDIT-970#CASE-4
        def boom():
            raise RuntimeError("pass exploded")
        title, remedy, text, rc = R._audit_section("Boom", "reqmap.py boom", boom)
        self.assertIn("pass exploded", text)
        self.assertEqual(rc, 0)

    def test_json_carries_every_signal(self):  # verifies: REQ-AUDIT-970#CASE-5
        _, out = self._run(*self._green(), as_json=True)
        data = json.loads(out)
        for key in ("gate", "health", "exemptions", "shape"):
            self.assertIn(key, data)

    # ---- exemptions ------------------------------------------------------
    def test_exemption_with_a_recorded_reason_is_clean(self):  # verifies: REQ-AUDIT-971#CASE-1
        r = self._req(exempt=["file-spread"],
                      body_extra="\n## Context\n- `file-spread` is the capability here.\n")
        self.assertTrue(R._exemption_reason_recorded(r["body"], "file-spread"))
        self.assertEqual([e for e in R._exemptions_in_force({"REQ-A-001": r})
                          if not e["reason"]], [])

    def test_bare_exemption_is_a_warning(self):  # verifies: REQ-AUDIT-971#CASE-2
        reqs = {"REQ-A-001": self._req(exempt=["ac-count-high"])}
        members = {"REQ-A-001": [("implements", "x.py", 1)]}
        with tempfile.TemporaryDirectory() as d:
            ctx = R.GateContext(R.Workspace(reqs, members, d, d), full_members=members,
                                update_lock=False)
            found = list(R._exemption_without_reason_rule(ctx))
        self.assertEqual(len(found), 1)
        rid, msg = found[0]
        self.assertEqual(rid, "REQ-A-001")
        self.assertIn("lint_exempt", msg)
        self.assertIn("ac-count-high", msg)

    def test_a_distinct_from_with_no_written_reason_is_a_warning(self):  # verifies: REQ-SIMILARDISTINCT-1026#CASE-2
        r = self._req()
        r["meta"]["distinct_from"] = ["REQ-B-002"]
        reqs = {"REQ-A-001": r}
        members = {"REQ-A-001": [("implements", "x.py", 1)]}
        with tempfile.TemporaryDirectory() as d:
            ctx = R.GateContext(R.Workspace(reqs, members, d, d), full_members=members,
                                update_lock=False)
            found = list(R._exemption_without_reason_rule(ctx))
        self.assertEqual(1, len(found))
        self.assertIn("distinct_from", found[0][1])
        self.assertIn("REQ-B-002", found[0][1])
        self.assertIn("distinct_from", [e["field"] for e in R._exemptions_in_force(reqs)])

    def test_a_test_exemption_is_counted_with_its_reason(self):  # verifies: REQ-AUDIT-971#CASE-5
        r = self._req()
        r["meta"]["test_exempt"] = "integration-only"
        found = [e for e in R._exemptions_in_force({"REQ-A-001": r})
                 if e["field"] == "test_exempt"]
        self.assertEqual(found, [{"id": "REQ-A-001", "field": "test_exempt",
                                  "check": "tested-by", "reason": True}])

    def test_exemption_rule_is_never_promoted_by_strict(self):  # verifies: REQ-AUDIT-971#CASE-3
        rule = R.gate_rule_by_id("RM030")
        self.assertEqual(rule.severity, "warn")
        self.assertFalse(rule.strict)

    def test_oversize_findings_name_a_remedy_that_can_act(self):  # verifies: REQ-AUDIT-971#CASE-4
        """It used to name `clarify <ID> --decompose`, which acts on `statement-size`
        findings only. Following it printed `All clean` and wrote nothing, from a command
        the same gate run had just called an error — leaving `lint_exempt:` as the only
        visible way out, which is the one action the skill says must never be the reflex."""
        body = "# T\n\n## Description\n" + "".join(
            "- Clause {}.\n".format(i) for i in range(3)) + "\n## Cases\n" + "".join(
            "CASE-{}\n  Then it holds\n".format(i) for i in range(1, R.LINT_AC_MAX + 3))
        found = R.lint_requirement("REQ-A-001", {"meta": {"status": "confirmed"}, "body": body})
        detail = " ".join(f["detail"] for f in found if f["check"] == "ac-count-high")
        self.assertNotIn("clarify REQ-A-001 --decompose", detail)
        self.assertIn("move", detail)
        self.assertIn("does not cover this check", detail)

    # ---- corpus shape ----------------------------------------------------
    def test_a_levelled_corpus_is_not_called_flat(self):  # verifies: REQ-AUDIT-972#CASE-1
        reqs = {"REQ-A-001": self._req(level="code", satisfies=["ARCH-B-002"]),
                "ARCH-B-002": self._req(level="architecture")}
        shape = R._corpus_shape(reqs)
        self.assertFalse(shape["flat"])
        self.assertEqual(shape["levels"], {"code": 1, "architecture": 1})
        self.assertEqual(shape["satisfies_edges"], 1)

    def test_a_corpus_with_no_levels_is_flat(self):  # verifies: REQ-AUDIT-972#CASE-2
        reqs = {"REQ-{}-00{}".format(c, i): self._req() for i, c in enumerate("ABCDEFGHIJK")}
        shape = R._corpus_shape(reqs)
        self.assertTrue(shape["flat"])
        self.assertEqual(shape["levelled"], 0)
        _, out = self._run(reqs, {rid: [("implements", "x.py", 1)] for rid in reqs})
        self.assertIn("the corpus is flat", out)

    def test_a_flat_corpus_does_not_change_the_verdict(self):  # verifies: REQ-AUDIT-972#CASE-3
        reqs, members = self._green()
        self.assertTrue(R._corpus_shape(reqs)["flat"])
        rc, _ = self._run(reqs, members)
        self.assertEqual(rc, self._gate_rc(reqs, members))

    # ---- the sync tail ---------------------------------------------------
    def test_sync_tail_names_an_unclean_signal(self):  # verifies: REQ-AUDIT-973#CASE-1
        reqs = {"REQ-A-001": self._req(exempt=["ac-count-high"], level="code")}
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            R._audit_summary(reqs, {}, d, d)
        out = buf.getvalue()
        self.assertIn("no reason recorded", out)
        self.assertIn("reqmap.py gate --audit", out)

    def test_sync_tail_is_silent_on_a_clean_corpus(self):  # verifies: REQ-AUDIT-973#CASE-2
        reqs = {"REQ-A-001": self._req(level="code")}
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            R._audit_summary(reqs, {}, d, d)   # empty tree: no design, no untagged, no TODO
        self.assertEqual(buf.getvalue(), "")

    def test_sync_tail_writes_nothing(self):  # verifies: REQ-AUDIT-973#CASE-3
        reqs = {"REQ-A-001": self._req(exempt=["ac-count-high"])}
        with tempfile.TemporaryDirectory() as d:
            before = sorted(os.listdir(d))
            with redirect_stdout(io.StringIO()):
                R._audit_summary(reqs, {}, d, d)
            self.assertEqual(sorted(os.listdir(d)), before)


class Relevel(unittest.TestCase):  # tested-by: ARCH-AUDIT-065  # tested-by: REQ-RELEVEL-997
    """`relevel_residue_lines`: the read-only half-done re-level residue signals `sync`
    tails onto `_audit_summary`'s output. Report-only forever (ADR-0031/ADR-0036) - no
    signal here is a gate rule, writes anything, or changes an exit code."""

    def _req(self, level=None, satisfies=None, depends_on=None, path="req.md", body=None):
        meta = {"status": "confirmed", "layer": "feature", "owner": "Alex"}
        if level:
            meta["level"] = level
        if satisfies:
            meta["satisfies"] = satisfies
        if depends_on:
            meta["depends_on"] = depends_on
        return {"meta": meta, "path": path,
                "body": body if body is not None else
                        "# T\n\n## Description\n- It holds.\n\n## Cases\nCASE-1\n  Then it holds\n"}

    def test_flags_a_child_split_off_its_group_shared_file(self):
        # verifies: REQ-RELEVEL-997#CASE-1
        reqs = {
            "ARCH-P-001": self._req(
                level="architecture", path="p.md",
                body="# T\n\n## Description\n- A — see [[REQ-A-001]].\n"
                     "- B — see [[REQ-B-002]].\n\n## Cases\nCASE-1\n  Then it holds\n"),
            "REQ-A-001": self._req(level="code", satisfies=["ARCH-P-001"], path="p.md"),
            "REQ-B-002": self._req(level="code", satisfies=["ARCH-P-001"], path="b.md"),
        }
        lines = R.relevel_residue_lines(reqs)
        self.assertEqual(len(lines), 1)
        self.assertIn("ARCH-P-001", lines[0])
        self.assertIn("REQ-B-002", lines[0])

    def test_flags_a_code_child_missing_from_the_parent_wikilinks(self):
        # verifies: REQ-RELEVEL-997#CASE-2
        reqs = {
            "ARCH-Q-002": self._req(
                level="architecture", path="p2.md",
                body="# T\n\n## Description\n- A — see [[REQ-C-003]].\n\n"
                     "## Cases\nCASE-1\n  Then it holds\n"),
            "REQ-C-003": self._req(level="code", satisfies=["ARCH-Q-002"], path="p2.md"),
            "REQ-D-004": self._req(level="code", satisfies=["ARCH-Q-002"], path="p2.md"),
        }
        lines = R.relevel_residue_lines(reqs)
        self.assertEqual(len(lines), 1)
        self.assertIn("ARCH-Q-002", lines[0])
        self.assertIn("REQ-D-004", lines[0])

    def test_flags_a_stale_system_level_mention(self):
        # verifies: REQ-RELEVEL-997#CASE-3
        reqs = {
            "SYS-R-003": self._req(
                level="system", path="s.md",
                body="# T\n\n## Description\n- Needs [[ARCH-S-004]].\n\n"
                     "## Cases\nCASE-1\n  Then it holds\n"),
            "ARCH-S-004": self._req(level="architecture", path="s.md"),
        }
        lines = R.relevel_residue_lines(reqs)
        self.assertEqual(len(lines), 1)
        self.assertIn("SYS-R-003", lines[0])
        self.assertIn("ARCH-S-004", lines[0])

    def test_flags_a_redundant_satisfies_depends_on_edge(self):
        # verifies: REQ-RELEVEL-997#CASE-4
        reqs = {
            "ARCH-T-005": self._req(
                level="architecture", path="t.md",
                body="# T\n\n## Description\n- A — see [[REQ-E-005]].\n\n"
                     "## Cases\nCASE-1\n  Then it holds\n"),
            "REQ-E-005": self._req(level="code", path="t.md",
                                   satisfies=["ARCH-T-005"], depends_on=["ARCH-T-005"]),
        }
        lines = R.relevel_residue_lines(reqs)
        self.assertEqual(len(lines), 1)
        self.assertIn("REQ-E-005", lines[0])
        self.assertIn("ARCH-T-005", lines[0])

    def test_flags_a_requirement_satisfying_the_wrong_rung(self):
        # verifies: REQ-RELEVEL-997#CASE-5
        reqs = {
            "SYS-U-006": self._req(level="system", path="u.md"),
            "REQ-F-006": self._req(level="code", satisfies=["SYS-U-006"], path="f.md"),
        }
        lines = R.relevel_residue_lines(reqs)
        self.assertEqual(len(lines), 1)
        self.assertIn("REQ-F-006", lines[0])
        self.assertIn("SYS-U-006", lines[0])

    def test_silent_when_no_requirement_declares_a_level(self):
        # verifies: REQ-RELEVEL-997#CASE-6
        reqs = {
            "REQ-G-007": self._req(satisfies=["REQ-H-008"], depends_on=["REQ-H-008"], path="g.md"),
            "REQ-H-008": self._req(path="g.md"),
        }
        self.assertEqual(R.relevel_residue_lines(reqs), [])


class CasesNext(unittest.TestCase):  # tested-by: ARCH-NEXT-013  # tested-by: REQ-NEXT-883  # tested-by: REQ-NEXT-884  # tested-by: REQ-NEXT-885  # tested-by: REQ-NEXT-886  # tested-by: REQ-NEXT-887
    def _run(self, reqs, members, code_root=None, reqs_dir=None, **kw):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_next(R.Workspace(reqs, members, reqs_dir, code_root), **kw)
        return code, buf.getvalue()

    def test_output_starts_with_progress_header(self):  # verifies: ARCH-NEXT-013#CASE-1
        reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed"}, "body": "# T\n"}}
        members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._run(reqs, members)
        self.assertTrue(out.startswith("1 requirement(s)"), out[:60])

    def test_three_way_priority_order(self):  # verifies: REQ-NEXT-885#CASE-5
        reqs = {
            "AAA-NOPRI-001": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "BBB-SHOULD-002": {"meta": {"status": "confirmed", "priority": "should-have"}, "body": "# T\n"},
            "CCC-MUST-003": {"meta": {"status": "confirmed", "priority": "must-have"}, "body": "# T\n"},
        }
        members = {rid: [("implements", "x.py", 1)] for rid in reqs}  # all untested -> one bucket
        _, out = self._run(reqs, members)
        self.assertLess(out.index("CCC-MUST-003"), out.index("BBB-SHOULD-002"))
        self.assertLess(out.index("BBB-SHOULD-002"), out.index("AAA-NOPRI-001"))

    def test_empty_and_clean_write_no_files(self):  # verifies: ARCH-NEXT-013#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            os.makedirs(rd)
            before = set(os.listdir(rd))
            code, out = self._run({}, {}, reqs_dir=rd)
            self.assertEqual(code, 0)
            self.assertIn("No requirements yet", out)
            self.assertEqual(set(os.listdir(rd)), before)
            reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed"}, "body": "# T\n"}}
            members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
            code2, out2 = self._run(reqs, members, reqs_dir=rd)
            self.assertEqual(code2, 0)
            self.assertIn("Nothing pending", out2)
            self.assertEqual(set(os.listdir(rd)), before)

    def test_needs_tests_advice_matches_risk_advice_verbatim(self):  # verifies: REQ-NEXT-883#CASE-2
        reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed"}, "body": "# T\n"}}
        members = {"CORE-FOO-001": [("implements", "x.py", 1)]}
        _, out = self._run(reqs, members)
        self.assertIn("  -> " + R.RISK_ADVICE["untested"], out)

    def test_implements_only_member_not_counted_tested(self):  # verifies: REQ-NEXT-883#CASE-4
        reqs = {
            "CORE-FOO-001": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "CORE-BAR-002": {"meta": {"status": "confirmed"}, "body": "# T\n"},
        }
        members = {
            "CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)],
            "CORE-BAR-002": [("implements", "y.py", 1)],
        }
        _, out = self._run(reqs, members)
        self.assertIn("1 tested", out)
        self.assertNotIn("2 tested", out)

    def test_bucket_print_order(self):  # verifies: REQ-NEXT-884#CASE-2
        body_intent = "# T\n\n## WHAT — Verify intent\n- is this a bug?\n"
        reqs = {
            "AAA-ORPHAN-001": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "BBB-UNTEST-002": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "CCC-INTENT-003": {"meta": {"status": "confirmed"}, "body": body_intent},
            "DDD-DRAFT-004": {"meta": {"status": "draft"}, "body": "# T\n"},
        }
        members = {
            "BBB-UNTEST-002": [("implements", "x.py", 1)],
            "CCC-INTENT-003": [("implements", "x.py", 1), ("tested-by", "t.py", 2)],
        }
        _, out = self._run(reqs, members)
        self.assertLess(out.index("Orphans"), out.index("Needs tests"))
        self.assertLess(out.index("Needs tests"), out.index("Needs intent review"))
        self.assertLess(out.index("Needs intent review"), out.index("Drafts to review"))

    def test_untagged_files_after_drafts(self):
        # verifies: REQ-NEXTUNTAGGED-1050#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "orphan.py"), "x = 1\n")
            reqs = {"DDD-DRAFT-004": {"meta": {"status": "draft"}, "body": "# T\n"}}
            _, out = self._run(reqs, {}, code_root=d)
            self.assertIn("Untagged files", out)
            self.assertLess(out.index("Drafts to review"), out.index("Untagged files"))

    def test_no_code_root_no_untagged_section(self):
        # verifies: REQ-NEXTUNTAGGED-1050#CASE-4
        reqs = {"DDD-DRAFT-004": {"meta": {"status": "draft"}, "body": "# T\n"}}
        _, out = self._run(reqs, {})
        self.assertNotIn("Untagged files", out)

    def test_untagged_files_bucket_suggests_draft(self):
        # verifies: REQ-NEXTUNTAGGED-1050#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "orphan.py"), "x = 1\n")
            reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed"}, "body": "# T\n"}}
            members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
            _, out = self._run(reqs, members, code_root=d)
            self.assertIn("Untagged files", out)
            self.assertIn("orphan.py", out)
            self.assertIn("reqmap.py init", out)

    def test_equal_priority_and_risk_falls_back_to_id_order(self):  # verifies: REQ-NEXT-885#CASE-1
        reqs = {
            "ZZZ-B-002": {"meta": {"status": "draft", "priority": "must-have"}, "body": "# T\n"},
            "AAA-A-001": {"meta": {"status": "draft", "priority": "must-have"}, "body": "# T\n"},
        }
        _, out = self._run(reqs, {})
        self.assertLess(out.index("AAA-A-001"), out.index("ZZZ-B-002"))

    def test_untagged_files_truncate_to_top_n(self):  # verifies: REQ-NEXT-886#CASE-4
        with tempfile.TemporaryDirectory() as d:
            for i in range(5):
                _write(os.path.join(d, "f{}.py".format(i)), "x = 1\n")
            reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed"}, "body": "# T\n"}}
            members = {"CORE-FOO-001": [("implements", "src/x.py", 1), ("tested-by", "src/t.py", 2)]}
            _, out = self._run(reqs, members, code_root=d)
            shown = sum(1 for i in range(5) if "f{}.py".format(i) in out)
            self.assertEqual(shown, 3)
            self.assertIn("... 2 more", out)

    def test_two_runs_are_byte_identical_and_write_no_file(self):  # verifies: REQ-NEXT-887#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            os.makedirs(rd)
            before = set(os.listdir(rd))
            reqs = {
                "CORE-FOO-001": {"meta": {"status": "confirmed"}, "body": "# T\n"},
                "CORE-BAR-002": {"meta": {"status": "confirmed"}, "body": "# T\n"},
                "DDD-DRAFT-003": {"meta": {"status": "draft"}, "body": "# T\n"},
            }
            members = {"CORE-BAR-002": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
            _, out1 = self._run(reqs, members, reqs_dir=rd)
            _, out2 = self._run(reqs, members, reqs_dir=rd)
            self.assertEqual(out1, out2)
            self.assertEqual(set(os.listdir(rd)), before)

    def test_orphans_and_drafts_still_exit_zero(self):  # verifies: REQ-NEXT-887#CASE-4
        reqs = {
            "A-1": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "B-2": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "C-3": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "D-4": {"meta": {"status": "draft"}, "body": "# T\n\n## WHAT — Verify intent\n- x?\n"},
            "E-5": {"meta": {"status": "draft"}, "body": "# T\n\n## WHAT — Verify intent\n- y?\n"},
        }
        code, _ = self._run(reqs, {})
        self.assertEqual(code, 0)


class CasesShow(unittest.TestCase):  # tested-by: ARCH-SHOW-015  # tested-by: REQ-SHOW-917  # tested-by: REQ-SHOW-919
    def test_single_call_surfaces_everything(self):  # verifies: REQ-SHOW-917#CASE-1
        reqs = {
            "CORE-A-001": {"meta": {"status": "confirmed", "layer": "feature",
                                    "depends_on": ["CORE-B-002"]},
                          "body": "# A\n\n## Description\n- shall do X.\n",
                          "path": "requirements/CORE-A-001.md"},
            "CORE-B-002": {"meta": {"status": "confirmed", "layer": "feature"},
                          "body": "# B\n", "path": "requirements/CORE-B-002.md"},
        }
        members = {"CORE-A-001": [("implements", "src/foo.py", 3)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_show(R.Workspace(reqs, members), "CORE-A-001")
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("CORE-A-001", out)
        self.assertIn("Contract:", out)
        self.assertIn("Depends on:", out)
        self.assertIn("CORE-B-002", out)
        self.assertIn("Members in code", out)
        self.assertIn("src/foo.py:3", out)

    def test_show_leaves_file_byte_identical(self):  # verifies: REQ-SHOW-917#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            content = (REQ.format(id="REQ-X-001", status="confirmed", layer="feature",
                                  extra="", title="X") + "\n## Description\n- shall do X.\n")
            _write(os.path.join(rd, "REQ-X-001.md"), content)
            with open(os.path.join(rd, "REQ-X-001.md"), "rb") as f:
                before = f.read()
            reqs = R.load_requirements(rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_show(R.Workspace(reqs, {}), "REQ-X-001")
            with open(os.path.join(rd, "REQ-X-001.md"), "rb") as f:
                after = f.read()
            self.assertEqual(before, after)

    def test_no_description_section_says_so(self):  # verifies: REQ-SHOW-917#CASE-7
        reqs = {"REQ-X-001": {"meta": {"status": "confirmed", "layer": "feature"},
                              "body": "# X\n\nno sections here.\n",
                              "path": "requirements/REQ-X-001.md"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(R.Workspace(reqs, {}), "REQ-X-001")
        self.assertIn("(none — no '## Description' section)", buf.getvalue())

    def test_risk_signal_shown_with_advice(self):  # verifies: REQ-SHOW-919#CASE-2
        reqs = {"REQ-X-001": {"meta": {"status": "confirmed", "layer": "feature"},
                              "body": "# X\n", "path": "requirements/REQ-X-001.md"}}
        members = {"REQ-X-001": [("implements", "x.py", 1)]}  # untested -> 'untested' signal
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(R.Workspace(reqs, members), "REQ-X-001")
        out = buf.getvalue()
        self.assertIn("Risk signals:", out)
        self.assertIn("untested", out)
        self.assertIn(R.RISK_ADVICE["untested"], out)


class CasesMap(unittest.TestCase):  # tested-by: ARCH-MAP-007
    def test_map_json_top_level_keys_and_node_fields(self):  # verifies: ARCH-MAP-007#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="confirmed", layer="bus", extra="", title="A"))
            reqs = R.load_requirements(rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(reqs, {}, rd), d)
            doc = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
            for key in ("engine_version", "repo", "nodes", "edges", "todos"):
                self.assertIn(key, doc)
            node = doc["nodes"][0]
            self.assertIn("members", node)
            self.assertEqual(node["members"], [])
            self.assertIn("risks", node)
            self.assertIn("unimplemented", [r["signal"] for r in node["risks"]])


class CasesContext(unittest.TestCase):  # tested-by: ARCH-CONTEXT-048  # tested-by: REQ-CONTEXT-835
    def test_the_template_carries_the_context_section(self):  # verifies: REQ-CONTEXT-835#CASE-1
        # written through `cmd_new` until ADR-0045 removed it; the template it stamped is
        # the thing under test, and it is still the shape an author follows.
        self.assertIn("## Context (non-binding)", R.REQUIREMENT_TEMPLATE)

    def test_context_edit_does_not_change_binding_hash(self):  # verifies: REQ-CONTEXT-835#CASE-5
        body_a = ("# T\n\n## Description\n- shall do X.\n\n"
                 "## Context (non-binding)\n**Notes**\n- old note\n")
        body_b = ("# T\n\n## Description\n- shall do X.\n\n"
                 "## Context (non-binding)\n**Notes**\n- an entirely different note\n")
        self.assertEqual(R.binding_hash(body_a), R.binding_hash(body_b))


class CasesCmdRegistry(unittest.TestCase):  # tested-by: ARCH-CMDREGISTRY-033  # tested-by: REQ-CMDREGISTRY-834
    def test_generator_functions_import_stdlib_only(self):  # verifies: REQ-CMDREGISTRY-834#CASE-6
        import ast
        import importlib.util
        here = os.path.dirname(os.path.abspath(R.__file__))
        src = open(os.path.join(here, "reqmap_engine", "registry.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        target_fns = {"_generate_schema", "_generate_command_table", "_check_integration_fresh"}
        fn_nodes = [n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name in target_fns]
        self.assertEqual({n.name for n in fn_nodes}, target_fns)
        for fn in fn_nodes:
            for n in ast.walk(fn):
                self.assertNotIsInstance(n, (ast.Import, ast.ImportFrom),
                                          "{} has a local import".format(fn.name))
        # these functions have no local imports, so they inherit only the module's
        # top-level imports -- verify every one of those resolves to the stdlib.
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mods.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                mods.add(node.module.split(".")[0])
        self.assertTrue(mods)
        for name in mods:
            spec = importlib.util.find_spec(name)
            self.assertIsNotNone(spec, "{} not resolvable".format(name))
            origin = (spec.origin or "").replace(os.sep, "/")
            self.assertNotIn("site-packages", origin, "{} looks third-party: {}".format(name, origin))


class CasesFindings(unittest.TestCase):  # tested-by: ARCH-FINDINGS-010  # tested-by: REQ-FINDINGS-853
    def test_findings_writes_single_file(self):  # verifies: REQ-FINDINGS-853#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["swallowed except, intended?"]))
            before = set(os.listdir(rd))
            reqs = R.load_requirements(rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_findings(reqs, rd)
            after = set(os.listdir(rd))
            self.assertEqual(after - before, {"_findings.md"})


class CasesSearch036(unittest.TestCase):  # tested-by: ARCH-SEARCH-036  # tested-by: REQ-SEARCH-912  # tested-by: REQ-SEARCH-913  # tested-by: REQ-SEARCH-914  # tested-by: REQ-SEARCH-915
    def _req(self, title, contract):
        return {"body": "# {t}\n\n> {t} intent.\n\n## WHAT — Contract (normative)\n- {c}\n".format(
            t=title, c=contract)}

    def _score_lines(self, out):
        return [ln for ln in out.splitlines()
                if "REQ-" in ln and ln.strip()[:1].isdigit()]

    def test_search_writes_no_file(self):  # verifies: REQ-SEARCH-912#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\n---\n\n" + _ac_body())
            before = sorted(os.listdir(d))
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_search(reqs, "thing")
            after = sorted(os.listdir(d))
        self.assertEqual(before, after)

    def test_search_scores_a_pair_the_same_way_dupes_does(self):  # verifies: REQ-SEARCH-912#CASE-2
        a = self._req("Alpha", "detect when a contract changes against the lock hash baseline")
        b = self._req("Beta", "render mermaid diagrams of the requirement graph nicely")
        docs = {"REQ-A-001": R._sim_tokens(R._sim_text(a["body"])),
                "REQ-B-002": R._sim_tokens(R._sim_text(b["body"]))}
        dupes_vecs = R._tfidf(docs)
        dupes_score = R._cosine(dupes_vecs["REQ-A-001"], dupes_vecs["REQ-B-002"])
        # search-style: corpus EXCLUDES the "A" requirement, query text equals it verbatim —
        # so the folded-in query pseudo-doc mirrors the exact 2-document corpus dupes used.
        query_text = R._sim_text(a["body"])
        qtok = R._sim_tokens(query_text)
        corpus = {"REQ-B-002": docs["REQ-B-002"], "\x00query": qtok}
        search_vecs = R._tfidf(corpus)
        search_score = R._cosine(search_vecs["\x00query"], search_vecs["REQ-B-002"])
        self.assertAlmostEqual(dupes_score, search_score)

    def test_notes_only_word_does_not_score(self):  # verifies: REQ-SEARCH-912#CASE-3
        body = ("# Thing\n\n> does something else entirely.\n\n"
                "## WHAT — Contract (normative)\n- does one thing well\n\n"
                "## Notes\n- mentions xylophone here only\n")
        reqs = {"REQ-A-001": {"body": body}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_search(reqs, "xylophone")
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("No match for", out)
        self.assertNotIn("REQ-A-001", out)

    def test_rarer_shared_term_outweighs_common_one(self):  # verifies: REQ-SEARCH-912#CASE-4
        reqs = {
            "REQ-COMMON-001": self._req("Common", "shared token appears in many places"),
            "REQ-RARE-002": self._req("Rare", "zephyrine token appears nowhere else at all"),
            "REQ-DECOY-003": self._req("Decoy1", "shared token noise filler content"),
            "REQ-DECOY-004": self._req("Decoy2", "shared token noise filler content"),
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_search(reqs, "shared zephyrine", top=10)
        lines = self._score_lines(buf.getvalue())
        ids_in_order = [ln.split()[1] for ln in lines]
        self.assertIn("REQ-RARE-002", ids_in_order)
        self.assertIn("REQ-COMMON-001", ids_in_order)
        self.assertLess(ids_in_order.index("REQ-RARE-002"), ids_in_order.index("REQ-COMMON-001"))

    def test_default_top_is_five(self):  # verifies: REQ-SEARCH-913#CASE-2
        reqs = {"REQ-D-{:03d}".format(i): self._req(
            "Doc{}".format(i), "validate user input and reject malformed payloads from clients")
            for i in range(1, 8)}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_search(reqs, "validate user input malformed payloads clients")
        lines = self._score_lines(buf.getvalue())
        self.assertEqual(len(lines), 5)

    def test_non_positive_top_prints_one_match(self):  # verifies: REQ-SEARCH-913#CASE-3
        reqs = {"REQ-D-{:03d}".format(i): self._req(
            "Doc{}".format(i), "validate user input and reject malformed payloads from clients")
            for i in range(1, 4)}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_search(reqs, "validate user input malformed payloads clients", top=0)
        lines = self._score_lines(buf.getvalue())
        self.assertEqual(len(lines), 1)

    def test_default_floor_is_005(self):  # verifies: REQ-SEARCH-914#CASE-1
        import inspect
        self.assertEqual(R.SEARCH_FLOOR, 0.05)
        self.assertEqual(inspect.signature(R.cmd_search).parameters["floor"].default, R.SEARCH_FLOOR)

    def test_short_words_and_digits_are_dropped(self):  # verifies: REQ-SEARCH-914#CASE-3
        query = "ab cd 12 345"
        self.assertEqual(R._sim_tokens(query), [])
        reqs = {"REQ-A-001": self._req("Thing", "does one specific thing well")}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_search(reqs, query)
        self.assertIn("No searchable terms", buf.getvalue())

    def test_no_strong_match_line_states_lexical(self):  # verifies: REQ-SEARCH-914#CASE-4
        reqs = {"REQ-A-001": self._req("Thing", "does one specific narrow thing")}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_search(reqs, "completely unrelated wombat quokka")
        out = buf.getvalue()
        self.assertIn("No match for", out)
        self.assertIn("lexical", out.lower())

    def test_missing_query_argument_exits_nonzero(self):  # verifies: REQ-SEARCH-915#CASE-2
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "requirements"))
            old_argv = sys.argv
            sys.argv = ["reqmap", "ask", "--search", "--root", d]
            try:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    rc = R.main()
            finally:
                sys.argv = old_argv
        self.assertNotEqual(rc, 0)

    def test_empty_corpus_message_and_exit_zero(self):  # verifies: REQ-SEARCH-915#CASE-3
        reqs = {"REQ-A-001": {"body": "# T\n"}}   # title too short to tokenize -> no contract text
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_search(reqs, "meaningful search terms")
        self.assertEqual(code, 0)
        self.assertIn("No requirements with contract text to search.", buf.getvalue())


class CasesHealth017(unittest.TestCase):  # tested-by: ARCH-HEALTH-017  # tested-by: REQ-HEALTH-857  # tested-by: REQ-HEALTH-858  # tested-by: REQ-HEALTH-859
    def _green(self):
        return {"meta": {"status": "confirmed"},
                "body": "# T\n\n## WHAT — Verify intent\n- None — clear.\n"}

    def _health(self, reqs, members, as_json=False):
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            code = R.cmd_health(R.Workspace(reqs, members, d), as_json)
        return code, buf.getvalue()

    def test_snapshot_covers_the_whole_corpus_not_a_subset(self):  # verifies: REQ-HEALTH-857#CASE-1
        reqs = {
            "REQ-A-001": self._green(),
            "REQ-A-002": {"meta": {"status": "draft"}, "body": "# T\n"},
            "REQ-A-003": {"meta": {"status": "confirmed"}, "body": "# T\n"},
        }
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["total"], 3)

    def test_health_writes_no_file(self):  # verifies: REQ-HEALTH-857#CASE-2
        reqs = {"REQ-A-001": self._green()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            before = sorted(os.listdir(d))
            with redirect_stdout(io.StringIO()):
                R.cmd_health(R.Workspace(reqs, members, d), False)
            after = sorted(os.listdir(d))
        self.assertEqual(before, after)
        self.assertEqual(before, [])

    def test_open_verify_intent_excludes_from_green(self):  # verifies: REQ-HEALTH-857#CASE-4
        body = "# T\n\n## WHAT — Verify intent\n- Does X still hold under Y? Unclear.\n"
        reqs = {"REQ-A-001": {"meta": {"status": "confirmed"}, "body": body}}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["healthy"], 0)
        self.assertEqual(obj["open_intent"], 1)

    def test_exempt_satisfies_test_axis_without_tested_by(self):  # verifies: REQ-HEALTH-858#CASE-2
        body = "# T\n\n## WHAT — Verify intent\n- None — clear.\n"
        reqs = {"REQ-A-001": {"meta": {"status": "confirmed", "layer": "feature",
                                       "test_exempt": "manual QA"}, "body": body}}
        members = {"REQ-A-001": [("implements", "x.py", 1)]}   # no tested-by member
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["healthy"], 1)

    def test_json_and_console_report_same_numbers(self):  # verifies: REQ-HEALTH-859#CASE-2
        reqs = {"REQ-A-001": self._green(),
                "REQ-A-002": {"meta": {"status": "draft"}, "body": "# T\n"}}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, plain = self._health(reqs, members, as_json=False)
        _, js = self._health(reqs, members, as_json=True)
        obj = json.loads(js)
        m = re.search(r"Requirement health: (\d+)/100  \((\d+)/(\d+) green", plain)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), obj["score"])
        self.assertEqual(int(m.group(2)), obj["healthy"])
        self.assertEqual(int(m.group(3)), obj["total"])
        m2 = re.search(r"confirmed:\s+(\d+)/(\d+)", plain)
        self.assertEqual(int(m2.group(1)), obj["confirmed"])
        self.assertEqual(int(m2.group(2)), obj["total"])


class CasesViewer007(unittest.TestCase):  # tested-by: ARCH-VIEWERFILE-074  # tested-by: REQ-VIEWER-940  # tested-by: REQ-VIEWER-941
    def _node(self, **fields):
        node = {"id": "A-1", "title": "T", "contract": [], "status": "confirmed",
                "layer": "bus", "members": [], "risk": 0, "acc": [], "deps": []}
        node.update(fields)
        return {"nodes": [node], "edges": []}

    def _blob(self, out):
        return out[len("<script>window.__REQMAP_DATA__="):-len(";</script>")]

    def test_render_html_returns_none_without_template(self):  # verifies: REQ-VIEWER-940#CASE-3
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(R.viewer, "_viewer_template_path",
                                   return_value=os.path.join(d, "nope.html")):
                out = R.render_html({"nodes": [], "edges": []}, d)
            self.assertIsNone(out)

    def test_map_writes_md_and_json_when_viewer_template_absent(self):  # verifies: REQ-VIEWER-940#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n" + _ac_body())
            _write(os.path.join(d, "a.py"), tag("A-FOO-001") + "\n")
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            with mock.patch.object(R.viewer, "_viewer_template_path",
                                   return_value=os.path.join(d, "nope.html")):
                with redirect_stdout(io.StringIO()):
                    code = R.cmd_map(R.Workspace(reqs, members, d), d)
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(d, "_map.md")))
            self.assertTrue(os.path.exists(os.path.join(d, "_map.json")))
            self.assertFalse(os.path.exists(os.path.join(d, "_map.html")))

    def test_all_three_dangerous_sequences_together_round_trip(self):  # verifies: REQ-VIEWER-941#CASE-1
        title = "</script><!--x-->"
        out = R._inject_viewer("<!--REQMAP_DATA-->", self._node(title=title))
        blob = self._blob(out)
        self.assertNotIn("</", blob)
        self.assertNotIn("<!--", blob)
        self.assertNotIn("-->", blob)
        # each of the three escapes is a documented V8 no-op (backslash silently
        # dropped before /, !, -); undo them the same way a JS engine would, then
        # the blob is valid JSON again with the original title intact.
        unescaped = blob.replace("-\\->", "-->").replace("<\\!--", "<!--").replace("<\\/", "</")
        self.assertEqual(json.loads(unescaped)["nodes"][0]["title"], title)

    def test_html_comment_open_is_escaped(self):  # verifies: REQ-VIEWER-941#CASE-3
        out = R._inject_viewer("<!--REQMAP_DATA-->",
                               self._node(contract=["discusses HTML injection via <!-- markers"]))
        blob = self._blob(out)
        self.assertNotIn("<!--", blob)
        self.assertIn("<\\!--", blob)

    def test_html_comment_close_is_escaped(self):  # verifies: REQ-VIEWER-941#CASE-4
        out = R._inject_viewer("<!--REQMAP_DATA-->", self._node(title="ends with -->"))
        blob = self._blob(out)
        self.assertNotIn("-->", blob)
        self.assertIn("-\\->", blob)


class CasesSimilar(unittest.TestCase):  # tested-by: ARCH-SIMILAR-016  # tested-by: REQ-SIMILAR-920  # tested-by: REQ-SIMILAR-921  # tested-by: REQ-SIMILAR-922  # tested-by: REQ-SIMILAR-923
    def _sim(self, reqs, threshold=None, members=None, top=None):
        buf = io.StringIO()
        with redirect_stdout(buf):
            if threshold is None:
                code = R.cmd_similar(reqs, members=members, top=top)
            else:
                code = R.cmd_similar(reqs, threshold, members, top=top)
        return code, buf.getvalue()

    def _req(self, title, contract):
        return {"body": "# {t}\n\n> {t} intent.\n\n## WHAT — Contract (normative)\n- {c}\n".format(
            t=title, c=contract)}

    def _req_full(self, title, intent, contract, notes=None):
        body = "# {t}\n\n> {i}\n\n## WHAT — Contract (normative)\n- {c}\n".format(t=title, i=intent, c=contract)
        if notes:
            body += "\n## WHAT — Notes & known limitations\n- {n}\n".format(n=notes)
        return {"body": body}

    def test_dupes_writes_no_file_output_only_stdout(self):  # verifies: REQ-SIMILAR-920#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs_dir = os.path.join(d, "requirements")
            c = "validate user input and reject malformed payloads from the client"
            _write(os.path.join(reqs_dir, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="baseline", layer="feature", extra="", title="Validator")
                   + "\n> Validator intent.\n\n## WHAT — Contract (normative)\n- " + c + "\n")
            _write(os.path.join(reqs_dir, "REQ-B-002.md"),
                   REQ.format(id="REQ-B-002", status="baseline", layer="feature", extra="", title="Checker")
                   + "\n> Checker intent.\n\n## WHAT — Contract (normative)\n- " + c + "\n")
            before = {n: open(os.path.join(reqs_dir, n), "rb").read() for n in os.listdir(reqs_dir)}
            old_argv = sys.argv
            sys.argv = ["reqmap", "ask", "--dupes", "--root", d]
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    R.main()
            finally:
                sys.argv = old_argv
            after = {n: open(os.path.join(reqs_dir, n), "rb").read() for n in os.listdir(reqs_dir)}
            self.assertEqual(before, after)          # no requirement file changed
            out = buf.getvalue()
            self.assertIn("REQ-A-001", out)
            self.assertIn("<->", out)                 # the pair report went to stdout

    def test_title_and_contract_drive_the_bag_of_words(self):  # verifies: REQ-SIMILAR-921#CASE-1
        c = "issues short lived authentication tokens bound to a browser session"
        reqs = {"REQ-A-001": self._req_full("Session Token Issuer", "one intent sentence here", c),
                "REQ-B-002": self._req_full("Session Token Issuer", "a different intent wording entirely", c)}
        code, out = self._sim(reqs, 0.35)
        self.assertIn("REQ-A-001  <->  REQ-B-002", out)

    def test_notes_text_excluded_from_bag(self):  # verifies: REQ-SIMILAR-921#CASE-2
        shared_notes = "legacy migration caveat regarding timezone offsets and daylight saving edge cases"
        reqs = {
            "REQ-A-001": self._req_full("Alpha Widget", "renders alpha widgets on the dashboard.",
                                         "renders a configurable alpha widget on the dashboard", shared_notes),
            "REQ-B-002": self._req_full("Beta Report", "compiles beta usage reports.",
                                         "compiles a scheduled beta usage report", shared_notes),
        }
        code, out = self._sim(reqs, 0.35)
        # unrelated title/contract; only the (excluded) Notes section overlaps
        self.assertIn("No overlapping", out)

    def test_two_letter_tokens_dropped(self):  # verifies: REQ-SIMILAR-921#CASE-3
        toks = R._sim_tokens("ab cd widget pipeline")
        self.assertNotIn("ab", toks)
        self.assertNotIn("cd", toks)
        self.assertIn("widget", toks)
        self.assertIn("pipeline", toks)

    def test_stopwords_and_numbers_dropped_from_tokens(self):  # verifies: REQ-SIMILAR-921#CASE-4
        toks = R._sim_tokens("the requirement for 2026 widget pipeline")
        self.assertNotIn("the", toks)
        self.assertNotIn("for", toks)
        self.assertNotIn("2026", toks)
        self.assertIn("widget", toks)
        self.assertIn("pipeline", toks)

    def test_rarer_term_weighted_higher(self):  # verifies: REQ-SIMILAR-922#CASE-1
        docs = {"A": ["common", "rare"], "B": ["common", "rare"], "C": ["common"],
                "D": ["common"], "E": ["common"]}
        vecs = R._tfidf(docs)
        self.assertGreater(vecs["A"]["rare"], vecs["A"]["common"])

    def test_two_doc_corpus_scores_above_zero(self):  # verifies: REQ-SIMILAR-922#CASE-2
        docs = {"A": ["shared"], "B": ["shared"]}
        vecs = R._tfidf(docs)
        self.assertGreater(R._cosine(vecs["A"], vecs["B"]), 0.0)

    def test_default_threshold_reports_only_above_035(self):  # verifies: REQ-SIMILAR-923#CASE-1
        c_high = "issues short lived authentication tokens bound to a browser session for login"
        reqs = {
            "REQ-A-001": self._req("Session Token Issuer", c_high),
            "REQ-B-002": self._req("Session Token Issuer", c_high),
            "REQ-C-003": self._req("Alpha Widget", "renders a configurable alpha widget on the dashboard"),
            "REQ-D-004": self._req("Beta Report", "compiles a scheduled beta usage report"),
        }
        code, out = self._sim(reqs)     # no threshold arg -> module default (0.35)
        self.assertIn("REQ-A-001  <->  REQ-B-002", out)
        self.assertNotIn("REQ-C-003", out)
        self.assertNotIn("REQ-D-004", out)

    def test_lower_threshold_includes_previously_hidden_pair(self):  # verifies: REQ-SIMILAR-923#CASE-2
        reqs = {
            "REQ-A-001": self._req("Widget Alpha", "renders a configurable alpha widget on the dashboard for admins today"),
            "REQ-B-002": self._req("Widget Beta", "renders a configurable beta widget on a different page for guests only"),
        }
        docs = {rid: R._sim_tokens(R._sim_text(r["body"])) for rid, r in reqs.items()}
        vecs = R._tfidf(docs)
        score = R._cosine(vecs["REQ-A-001"], vecs["REQ-B-002"])
        self.assertTrue(0.1 <= score < 0.35, score)   # guard: engineered to land in the gap
        _, out_default = self._sim(reqs)              # default 0.35 -> hidden
        self.assertNotIn("<->", out_default)
        _, out_low = self._sim(reqs, 0.1)              # --threshold 0.1 -> now shown
        self.assertIn("REQ-A-001  <->  REQ-B-002", out_low)


class CasesRoadmap(unittest.TestCase):  # tested-by: ARCH-ROADMAP-038  # tested-by: REQ-ROADMAP-907
    def test_roadmap_signals_falls_back_to_parent_dir(self):  # verifies: REQ-ROADMAP-907#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"), "## v2.8\n- [ ] later | lane: feature\n")
            child = os.path.join(d, "plugin")
            os.makedirs(child, exist_ok=True)
            data = R._roadmap_signals(child)
            self.assertIsNotNone(data)
            self.assertEqual(data["newest_milestone"], "v2.8")

    def test_item_under_nonversion_heading_filed_under_prior_milestone(self):  # verifies: REQ-ROADMAP-907#CASE-7
        text = "## v2.16\n- [x] shipped thing | lane: feature\n\n## Deferred work\n- [ ] later thing | lane: feature\n"
        todos = R._parse_todos_from_text(text)
        later = next(t for t in todos if t["name"] == "later thing")
        self.assertEqual(later["milestone"], "v2.16")


class CasesDriftImpact(unittest.TestCase):  # tested-by: ARCH-DRIFTIMPACT-035  # tested-by: REQ-DRIFTIMPACT-843
    def test_dependent_of_dependent_not_named(self):  # verifies: REQ-DRIFTIMPACT-843#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-FOO-001.md"),
                   REQ.format(id="AREA-FOO-001", status="confirmed", layer="bus", extra="", title="Foo")
                   + "\n## Contract\n- x\n## Acceptance\n- y\n")
            _write(os.path.join(d, "AREA-A-002.md"),
                   REQ.format(id="AREA-A-002", status="baseline", layer="feature",
                              extra="depends_on: [AREA-FOO-001]\n", title="A"))
            _write(os.path.join(d, "AREA-C-003.md"),
                   REQ.format(id="AREA-C-003", status="baseline", layer="feature",
                              extra="depends_on: [AREA-A-002]\n", title="C"))
            _write(os.path.join(d, "mod.py"), tag("AREA-FOO-001") + "\n")
            _write(os.path.join(d, "_reqlock.json"), '{"AREA-FOO-001": "stalehash0000"}')
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, members, d, d), False)
            out = buf.getvalue()
            self.assertIn("review dependent(s): AREA-A-002", out)
            self.assertNotIn("AREA-C-003", out)


class CasesMapdiagrams055(unittest.TestCase):  # tested-by: ARCH-MAPDIAGRAMS-055  # tested-by: REQ-MAPDIAGRAMS-874  # tested-by: REQ-MAPDIAGRAMS-878
    def _node(self, rid, status="baseline", layer="feature", members=None, verify=None):
        return {"id": rid, "layer": layer, "status": status, "title": rid,
                "intent": "", "input": "i", "output": "o", "desc": "", "acc": [],
                "deps": [], "used_by": [], "members": members or [], "verify": verify or []}

    def test_map_regenerates_map_md_discarding_a_manual_edit(self):  # verifies: REQ-MAPDIAGRAMS-874#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_map(R.Workspace(reqs, members, rd), d)
            _write(os.path.join(rd, "_map.md"), "hand-edited content, not from the graph\n")
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_map(R.Workspace(reqs, members, rd), d)
            md = open(os.path.join(rd, "_map.md"), encoding="utf-8").read()
        self.assertNotIn("hand-edited content", md)
        self.assertIn("System Map", md)

    def test_risk_diagram_shows_only_flagged_with_recommendation(self):  # verifies: ARCH-MAPDIAGRAMS-055#CASE-4
        data = {"nodes": [self._node("AI-X-001", status="baseline"),
                          self._node("AI-Y-002", status="confirmed",
                                     members=[{"role": "implements", "loc": "a.py:1"},
                                              {"role": "tested-by", "loc": "t.py:1"}])],
                "edges": []}
        out = R._mermaid_risk(data)
        self.assertIn("AI_X_001", out)
        self.assertNotIn("AI_Y_002", out)   # no risk signal -> excluded entirely
        with tempfile.TemporaryDirectory() as d:
            R.render_md(data, d)
            md = open(os.path.join(d, "_map.md"), encoding="utf-8").read()
        self.assertIn("recommendation", md)
        self.assertIn("AI-X-001", md)
        self.assertNotIn("AI-Y-002 |", md)

    def test_draft_verify_intent_is_not_double_flagged(self):  # verifies: REQ-MAPDIAGRAMS-878#CASE-3
        n = self._node("AI-X-001", status="draft", verify=["is this intended?"])
        signals = R._risk_signals(n)
        self.assertIn("unreviewed", signals)
        self.assertNotIn("unverified-intent", signals)
        out = R._mermaid_risk({"nodes": [n], "edges": []})
        self.assertIn("unreviewed", out)
        self.assertNotIn("unverified-intent", out)


class CasesCoverage029(unittest.TestCase):  # tested-by: REQ-COVERAGE-836
    def _green(self):
        return {"meta": {"status": "confirmed"},
                "body": "# T\n\n## WHAT — Verify intent\n- None — clear.\n"}

    def test_untagged_count_matches_scan_untagged_length(self):  # verifies: REQ-COVERAGE-836#CASE-2
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "src", "tagged.py"), "# implements: REQ-A-001\nx = 1\n")
            _write(os.path.join(d, "src", "untagged.py"), "x = 2\n")
            _write(os.path.join(d, "src", "untagged2.py"), "x = 3\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), True)
            obj = json.loads(buf.getvalue())
            direct = R._scan_untagged(d, d)
        self.assertEqual(obj["untagged"], len(direct))
        self.assertEqual(len(direct), 2)

    def test_tested_by_tag_alone_covers_a_file(self):  # verifies: REQ-COVERAGE-836#CASE-3
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "probe.py"), "x = 1\n")
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), True)
            before = json.loads(buf1.getvalue())["untagged"]
            _write(os.path.join(d, "probe.py"), "# tested-by: REQ-A-001\nx = 1\n")
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), True)
            after = json.loads(buf2.getvalue())["untagged"]
        self.assertEqual(before - after, 1)

    def test_health_text_output_labels_untagged_count(self):  # verifies: REQ-COVERAGE-836#CASE-5
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "untagged.py"), "x = 1\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d, d), False)
            out = buf.getvalue()
        self.assertIn("untagged code (no requirement):", out)
        self.assertIn("1", out.split("untagged code (no requirement):")[1].splitlines()[0])

    def test_tagging_or_ignoring_drops_untagged_count(self):  # verifies: REQ-COVERAGE-836#CASE-7
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d1:
            _write(os.path.join(d1, "probe.py"), "x = 1\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d1, d1), True)
            before1 = json.loads(buf.getvalue())["untagged"]
            _write(os.path.join(d1, "probe.py"), "# implements: REQ-A-001\nx = 1\n")
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d1, d1), True)
            after1 = json.loads(buf2.getvalue())["untagged"]
        self.assertEqual(before1 - after1, 1)

        with tempfile.TemporaryDirectory() as d2:
            _write(os.path.join(d2, "probe.py"), "x = 1\n")
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d2, d2), True)
            before2 = json.loads(buf3.getvalue())["untagged"]
            _write(os.path.join(d2, ".reqmapignore"), "probe.py\n")
            buf4 = io.StringIO()
            with redirect_stdout(buf4):
                R.cmd_health(R.Workspace({"REQ-A-001": self._green()}, members, d2, d2), True)
            after2 = json.loads(buf4.getvalue())["untagged"]
        self.assertEqual(before2 - after2, 1)


class CasesRegistrylag035(unittest.TestCase):  # tested-by: REQ-REGISTRYLAG-903  # tested-by: REQ-REGISTRYLAG-904
    def _mkgit(self, d):
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.email", "t@t.com"], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.name", "T"], check=True, capture_output=True)

    def _gcommit(self, d, msg):
        subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-m", msg], check=True, capture_output=True)

    def test_lag_counts_from_most_recent_touch_not_first(self):  # verifies: REQ-REGISTRYLAG-903#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._mkgit(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"), "# T\n")
            self._gcommit(d, "reqs A")             # commit A
            for i in range(2):
                _write(os.path.join(d, "code{}.py".format(i)), "x = 1\n")
                self._gcommit(d, "c{}".format(i))
            _write(os.path.join(rdir, "REQ-A-001.md"), "# T2\n")
            self._gcommit(d, "reqs B")             # commit B
            _write(os.path.join(d, "code_last.py"), "x = 1\n")
            self._gcommit(d, "c_last")
            lag = R._commits_since_reqs_touch(d, rdir)
        self.assertEqual(lag, 1)   # since B, not since A

    def test_malformed_requirement_file_does_not_break_the_count(self):  # verifies: REQ-REGISTRYLAG-903#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._mkgit(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "BAD.md"), "---\nid: [unterminated\nnot: valid: yaml: at: all\n")
            self._gcommit(d, "bad reqs")
            for i in range(2):
                _write(os.path.join(d, "code{}.py".format(i)), "x = 1\n")
                self._gcommit(d, "c{}".format(i))
            lag = R._commits_since_reqs_touch(d, rdir)
        self.assertEqual(lag, 2)

    def test_lag_line_appears_only_for_nonzero_count(self):  # verifies: REQ-REGISTRYLAG-904#CASE-2
        with tempfile.TemporaryDirectory() as fresh:
            self._mkgit(fresh)
            rdir = os.path.join(fresh, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"), "# T\n")
            self._gcommit(fresh, "reqs")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace({}, {}, rdir, fresh), False)
            out_fresh = buf.getvalue()
        with tempfile.TemporaryDirectory() as lagged:
            self._mkgit(lagged)
            rdir2 = os.path.join(lagged, "requirements")
            _write(os.path.join(rdir2, "REQ-A-001.md"), "# T\n")
            self._gcommit(lagged, "reqs")
            for i in range(2):
                _write(os.path.join(lagged, "code{}.py".format(i)), "x = 1\n")
                self._gcommit(lagged, "c{}".format(i))
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_health(R.Workspace({}, {}, rdir2, lagged), False)
            out_lagged = buf2.getvalue()
        self.assertNotIn("commits since requirements touched", out_fresh)
        self.assertIn("commits since requirements touched", out_lagged)

    def test_reqs_dir_never_committed_reads_as_unmeasurable(self):  # verifies: REQ-REGISTRYLAG-904#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self._mkgit(d)
            _write(os.path.join(d, "code.py"), "x = 1\n")
            self._gcommit(d, "code only, requirements/ never committed")
            rdir = os.path.join(d, "requirements")   # never created/committed
            lag = R._commits_since_reqs_touch(d, rdir)
        self.assertIsNone(lag)


def _repo_root():
    """The source repo's root, or None when this suite runs from a seeded copy."""
    here = os.path.dirname(os.path.abspath(R.__file__))
    for _ in range(4):
        here = os.path.dirname(here)
        if os.path.isdir(os.path.join(here, "docs", "adr")) and \
                os.path.isfile(os.path.join(here, "README.md")):
            return here
    return None


class McpServer(unittest.TestCase):  # tested-by: REQ-MCPPROTOCOL-1027 @unit  # tested-by: REQ-MCPTOOLS-1028 @unit
    """`reqmap.py mcp`: the protocol over stdio, and the tools it runs as the CLI."""

    def _args(self, allow_writes=False, **kw):
        base = {"root": ".", "reqs": None, "code": None, "cache": False,
                "allow_writes": allow_writes}
        base.update(kw)
        return type("A", (), base)()

    def _serve(self, messages, allow_writes=False, run=None):
        lines = [m if isinstance(m, str) else json.dumps(m) for m in messages]
        stdin = io.BytesIO(("\n".join(lines) + "\n").encode("utf-8"))
        stdout = io.BytesIO()
        calls = []

        def fake(argv, workspace):
            calls.append(argv)
            return run(argv) if run else (0, "ok")
        R.mcp.serve(self._args(allow_writes), stdin, stdout, fake)
        out = [json.loads(l) for l in stdout.getvalue().decode("utf-8").splitlines()]
        return out, calls

    @staticmethod
    def _req(i, method, params=None):
        msg = {"jsonrpc": "2.0", "id": i, "method": method}
        if params is not None:
            msg["params"] = params
        return msg

    def _call(self, i, name, arguments):
        return self._req(i, "tools/call", {"name": name, "arguments": arguments})

    def test_initialize_names_the_pinned_revision(self):  # verifies: REQ-MCPPROTOCOL-1027#CASE-1
        out, _ = self._serve([self._req(1, "initialize", {"protocolVersion": "2025-06-18"})])
        result = out[0]["result"]
        self.assertEqual("2025-06-18", result["protocolVersion"])
        self.assertIn("tools", result["capabilities"])
        self.assertEqual("reqmap", result["serverInfo"]["name"])

    def test_a_notification_is_not_answered_a_ping_is(self):  # verifies: REQ-MCPPROTOCOL-1027#CASE-2
        out, _ = self._serve([{"jsonrpc": "2.0", "method": "notifications/initialized"},
                              self._req(7, "ping")])
        self.assertEqual([{"jsonrpc": "2.0", "id": 7, "result": {}}], out)

    def test_malformed_input_is_a_protocol_error(self):  # verifies: REQ-MCPPROTOCOL-1027#CASE-3
        out, _ = self._serve([self._req(1, "prompts/list"), "not json",
                              {"jsonrpc": "2.0", "id": 3}])
        self.assertEqual([-32601, -32700, -32600], [m["error"]["code"] for m in out])

    def test_relative_paths_resolve_against_the_project_directory(self):  # verifies: REQ-MCPPROTOCOL-1027#CASE-4
        project = os.path.abspath(os.path.join(os.sep, "work", "proj"))
        flags = R.mcp._workspace_flags(self._args(reqs="plugin/requirements"),
                                       env={"CLAUDE_PROJECT_DIR": project})
        at = flags.index("--reqs") + 1
        self.assertEqual(os.path.join(project, "plugin", "requirements"), flags[at])
        self.assertEqual(project, flags[flags.index("--root") + 1])

    def test_the_tools_name_only_what_the_cli_has(self):  # verifies: REQ-MCPTOOLS-1028#CASE-1
        for tool in R.mcp.MCP_TOOLS:
            verb = tool["argv"][0]
            self.assertIn(verb, R.COMMANDS, tool["name"])
            known = {p["flag"] for p in R.COMMANDS[verb]["params"]}
            flags = [a for a in tool["argv"][1:] if a.startswith("--")]
            flags += [p["flag"] for p in tool["params"] if p["flag"]]
            for flag in flags:
                self.assertIn(flag, known, "{} uses {}".format(tool["name"], flag))

    FROZEN_TOOLS = {"reqmap_gate", "reqmap_next", "reqmap_health", "reqmap_show", "reqmap_search",
                    "reqmap_audit", "reqmap_dupes", "reqmap_untagged",
                    "reqmap_review", "reqmap_clarify", "reqmap_release_plan", "reqmap_sync",
                    "reqmap_release"}

    def test_the_tool_set_is_frozen(self):  # verifies: REQ-MCPTOOLS-1028#CASE-6
        self.assertEqual(self.FROZEN_TOOLS, {t["name"] for t in R.mcp.MCP_TOOLS},
                         "the MCP tool set is frozen until a consumer other than the maintainer "
                         "uses the server (ROADMAP V2); change REQ-MCPTOOLS-1028 first")

    def test_writing_tools_need_allow_writes(self):  # verifies: REQ-MCPTOOLS-1028#CASE-2
        # verifies: ARCH-MCP-073#CASE-2
        writes = {"reqmap_sync", "reqmap_release"}   # reqmap_new went with the verb (ADR-0045)
        out, calls = self._serve([self._req(1, "tools/list"),
                                  self._call(2, "reqmap_sync", {})])
        self.assertFalse(writes & {t["name"] for t in out[0]["result"]["tools"]})
        self.assertEqual(-32602, out[1]["error"]["code"])
        self.assertEqual([], calls)
        out, _ = self._serve([self._req(1, "tools/list")], allow_writes=True)
        self.assertLessEqual(writes, {t["name"] for t in out[0]["result"]["tools"]})

    def test_arguments_are_checked_and_passed_one_by_one(self):  # verifies: REQ-MCPTOOLS-1028#CASE-3
        out, calls = self._serve([self._call(1, "reqmap_search", {}),
                                  self._call(2, "reqmap_search", {"query": "x", "top": "3"}),
                                  self._call(3, "reqmap_search", {"query": "a b", "top": 3})])
        self.assertEqual([-32602, -32602], [m["error"]["code"] for m in out[:2]])
        self.assertEqual([["ask", "--json", "--search", "a b", "--top", "3"]], calls)

    def test_a_fail_verdict_is_an_answer_a_failed_command_is_an_error(self):  # verifies: REQ-MCPTOOLS-1028#CASE-4
        out, _ = self._serve([self._call(1, "reqmap_gate", {}),
                              self._call(2, "reqmap_show", {"id": "NOPE-X-001"})],
                             run=lambda argv: (1, "result"))
        gate, show = out[0]["result"], out[1]["result"]
        self.assertFalse(gate["isError"])
        self.assertTrue(show["isError"])
        for res in (gate, show):
            self.assertEqual("exit code 1", res["content"][-1]["text"])

    def test_a_release_plan_passes_release_with_or_without_a_version(self):  # verifies: REQ-MCPTOOLS-1028#CASE-5
        tool = next(t for t in R.mcp.MCP_TOOLS if t["name"] == "reqmap_release_plan")
        self.assertEqual(["sync", "--json", "--release"], R.mcp.tool_argv(tool, {}))
        self.assertEqual(["sync", "--json", "--release", "v1.2.0"],
                         R.mcp.tool_argv(tool, {"version": "v1.2.0"}))


class McpResources(unittest.TestCase):  # tested-by: REQ-MCPRESOURCES-1030 @unit
    """The committed map and each requirement, as MCP resources."""

    def _server(self, d, run=None):
        return {"allow_writes": False, "run": run or (lambda argv, ws: (0, "{}")),
                "workspace": ["--root", d, "--reqs", os.path.join(d, "requirements")]}

    def _map(self, d):
        _write(os.path.join(d, "requirements", "_map.json"), json.dumps({"nodes": [
            {"id": "REQ-A-001", "title": "Alpha"}, {"id": "REQ-B-002", "title": "Beta"}]}))

    def test_the_list_comes_from_the_committed_map(self):  # verifies: REQ-MCPRESOURCES-1030#CASE-1
        # verifies: ARCH-MCP-073#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual([], R.mcp.resource_list(self._server(d)))
            self._map(d)
            uris = [r["uri"] for r in R.mcp.resource_list(self._server(d))]
        self.assertEqual(["reqmap://map", "reqmap://requirement/REQ-A-001",
                          "reqmap://requirement/REQ-B-002"], uris)

    def test_a_requirement_reads_as_its_dossier(self):  # verifies: REQ-MCPRESOURCES-1030#CASE-2
        calls = []

        def run(argv, ws):
            calls.append(argv)
            return (0, '{"id": "REQ-A-001"}') if argv[-1] == "REQ-A-001" else (1, "no")
        with tempfile.TemporaryDirectory() as d:
            server = self._server(d, run)
            ok = R.mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "resources/read",
                               "params": {"uri": "reqmap://requirement/REQ-A-001"}}, server)
            bad = R.mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "resources/read",
                                "params": {"uri": "reqmap://requirement/NOPE-1"}}, server)
        content = ok["result"]["contents"][0]
        self.assertEqual(("reqmap://requirement/REQ-A-001", '{"id": "REQ-A-001"}'),
                         (content["uri"], content["text"]))
        self.assertEqual(["gate", "--json", "--show", "REQ-A-001"], calls[0])
        self.assertEqual(-32002, bad["error"]["code"])

    def test_the_map_reads_as_the_file_and_other_uris_are_refused(self):  # verifies: REQ-MCPRESOURCES-1030#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._map(d)
            server = self._server(d)
            text = R.mcp.read_resource("reqmap://map", server)["contents"][0]["text"]
            self.assertEqual(self._file(d), text)
            refused = R.mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "resources/read",
                                    "params": {"uri": "file:///x"}}, server)
        self.assertEqual(-32602, refused["error"]["code"])
        self.assertEqual("reqmap://requirement/{id}",
                         R.mcp.resource_templates()[0]["uriTemplate"])

    @staticmethod
    def _file(d):
        with open(os.path.join(d, "requirements", "_map.json"), encoding="utf-8") as f:
            return f.read()


class McpConfigSeed(unittest.TestCase):  # tested-by: REQ-MCPSEED-1029 @unit
    """`init` writes the client configs that start `reqmap.py mcp`."""

    @staticmethod
    def _read(*parts):
        with open(os.path.join(*parts), encoding="utf-8") as f:
            return f.read()

    def _repo(self, d):
        scripts = os.path.join(d, "scripts")
        os.makedirs(scripts)
        return mock.patch.object(R.mcpconfig, "ENGINE_DIR", scripts)

    def test_both_configs_start_the_vendored_engine(self):  # verifies: REQ-MCPSEED-1029#CASE-1
        # verifies: ARCH-MCP-073#CASE-3
        with tempfile.TemporaryDirectory() as d, self._repo(d):
            created, notes = R.seed_mcp_files(d, os.path.join(d, "requirements"))
            claude = json.loads(self._read(d, ".mcp.json"))
            code = json.loads(self._read(d, ".vscode", "mcp.json"))
        self.assertEqual([".mcp.json", ".vscode/mcp.json"], created)
        self.assertEqual([], notes)
        for entry, base in ((claude["mcpServers"]["reqmap"], "${CLAUDE_PROJECT_DIR:-.}"),
                            (code["servers"]["reqmap"], "${workspaceFolder}")):
            self.assertEqual(base + "/scripts/reqmap.py", entry["args"][0])
            self.assertEqual("mcp", entry["args"][1])
            self.assertEqual(base + "/requirements",
                             entry["args"][entry["args"].index("--reqs") + 1])

    def test_an_existing_config_is_left_alone(self):  # verifies: REQ-MCPSEED-1029#CASE-2
        with tempfile.TemporaryDirectory() as d, self._repo(d):
            mine = '{"servers": {"other": {"type": "stdio", "command": "x"}}}\n'
            _write(os.path.join(d, ".vscode", "mcp.json"), mine)
            created, notes = R.seed_mcp_files(d, os.path.join(d, "requirements"))
            self.assertEqual(mine, self._read(d, ".vscode", "mcp.json"))
        self.assertEqual([".mcp.json"], created)
        self.assertTrue(any(".vscode/mcp.json" in n for n in notes), notes)

    def test_an_engine_outside_the_repository_writes_nothing(self):  # verifies: REQ-MCPSEED-1029#CASE-3
        with tempfile.TemporaryDirectory() as d:
            created, notes = R.seed_mcp_files(d, os.path.join(d, "requirements"))
            self.assertEqual([], os.listdir(d))
        self.assertEqual([], created)
        self.assertTrue(any("not inside this repository" in n for n in notes), notes)


class McpEndToEnd(unittest.TestCase):  # tested-by: ARCH-MCP-073 @integration
    """The server as a process, spoken to over real stdio."""

    def test_initialize_list_and_call_over_stdio(self):  # verifies: ARCH-MCP-073#CASE-1
        engine = os.path.join(os.path.dirname(os.path.abspath(R.__file__)), "reqmap.py")
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "REQ-A-001.md"),
                   _spec("REQ-A-001", ["`gate` writes the lock file."]))
            _write(os.path.join(d, "a.py"), "# implements: REQ-A-001\nx = 1\n")
            msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "test", "version": "0"}}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                     "params": {"name": "reqmap_gate", "arguments": {}}}]
            done = subprocess.run(
                [sys.executable, "-X", "utf8", engine, "mcp", "--root", d],
                input="".join(json.dumps(m) + "\n" for m in msgs), capture_output=True,
                text=True, encoding="utf-8", timeout=300, env=dict(os.environ, CLAUDE_PROJECT_DIR=""))
        replies = [json.loads(l) for l in done.stdout.splitlines()]
        self.assertEqual([1, 2, 3], [r["id"] for r in replies], done.stderr)
        names = {t["name"] for t in replies[1]["result"]["tools"]}
        self.assertIn("reqmap_gate", names)
        self.assertNotIn("reqmap_sync", names)
        self.assertIn("gate:", replies[2]["result"]["content"][0]["text"])


class DocsAreTrue(unittest.TestCase):  # implements: REQ-SELFGATE-990  # tested-by: ARCH-SELFGATE-039  # tested-by: REQ-SELFGATE-990
    """The tool's thesis is that a claim about code should be checked, not trusted.
    Its own front page asserted 9,223 lines against a 10,066-line file for two days
    and nothing noticed, because no check read it."""

    def setUp(self):
        self.root = _repo_root()

    def test_the_hello_drift_demo_shows_drift(self):
        """ROADMAP's first-contact demo: a gate run in examples/hello-drift prints DRIFT and
        exits 0. A demo that silently stopped demonstrating is worse than none."""
        demo = os.path.join(self.root, "examples", "hello-drift")
        engine = os.path.join(self.root, "plugin", "scripts", "reqmap.py")
        r = subprocess.run([sys.executable, "-X", "utf8", engine, "gate"], cwd=demo,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True, encoding="utf-8")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("RM018 HELLO-GREET-001: DRIFT", r.stdout)
        self.assertIn("hello.py:1", r.stdout)

    def test_every_engine_module_is_tracked_by_git(self):  # verifies: REQ-SELFGATE-990#CASE-2
        """A module the package imports but git does not track ships a DEAD engine, and the
        author's machine structurally cannot see it: the working tree imports fine, and even
        `sync_reqmap.sh` propagates it, while a fresh checkout raises ModuleNotFoundError at
        CLI startup. `pyramid.py` sat untracked through a whole 36-file changeset exactly so,
        with `levels.py` — tracked and modified — importing it at module scope."""
        pkg = os.path.join(self.root, "plugin", "scripts", "reqmap_engine")
        out = subprocess.run(["git", "ls-files", "--", "plugin/scripts/reqmap_engine"],
                             cwd=self.root, capture_output=True, text=True)
        if out.returncode != 0:
            self.skipTest("not a git work tree")
        tracked = {os.path.basename(p) for p in out.stdout.split("\n") if p.strip()}
        on_disk = {fn for fn in os.listdir(pkg) if fn.endswith(".py")}
        self.assertEqual(sorted(on_disk - tracked), [],
                         "engine module(s) not tracked by git — a fresh checkout cannot "
                         "import the package")
        if not self.root:
            self.skipTest("not the source repo")

    def test_the_readme_engine_line_count_is_current(self):  # verifies: REQ-SELFGATE-990#CASE-1
        readme = open(os.path.join(self.root, "README.md"), encoding="utf-8").read()
        m = re.search(r"stdlib only,\s*([\d,]+)\s+lines", readme)
        self.assertIsNotNone(m, "README no longer states the engine's line count")
        claimed = int(m.group(1).replace(",", ""))
        scripts = os.path.join(self.root, "plugin", "scripts")
        pkg = os.path.join(scripts, "reqmap_engine")
        files = [os.path.join(scripts, "reqmap.py")] + [
            os.path.join(pkg, fn) for fn in sorted(os.listdir(pkg)) if fn.endswith(".py")]
        actual = 0
        for path in files:
            with open(path, encoding="utf-8") as f:
                actual += sum(1 for _ in f)
        self.assertEqual(actual, claimed,
                         "README claims {} lines, reqmap.py + reqmap_engine/ have {}".format(claimed, actual))

    def test_every_adr_on_disk_has_an_index_row(self):  # verifies: REQ-SELFGATE-990#CASE-2
        # ADR-0027 existed on disk and in no index for nine days.
        adr = os.path.join(self.root, "docs", "adr")
        index = open(os.path.join(adr, "README.md"), encoding="utf-8").read()
        missing = [f for f in sorted(os.listdir(adr))
                   if f.endswith(".md") and f != "README.md" and "(" + f + ")" not in index]
        self.assertEqual([], missing, "ADR files with no index row")

    def test_the_engine_module_count_is_current(self):  # verifies: REQ-SELFGATE-990#CASE-4
        """The same sentence states a module count; it read 49 against 51 files."""
        claude_md = open(os.path.join(self.root, "CLAUDE.md"), encoding="utf-8").read()
        m = re.search(r"holds the logic, (\d+) modules beside", claude_md)
        self.assertIsNotNone(m, "CLAUDE.md no longer states the engine's module count")
        pkg = os.path.join(self.root, "plugin", "scripts", "reqmap_engine")
        actual = len([f for f in os.listdir(pkg)
                      if f.endswith(".py") and f != "__init__.py"])
        self.assertEqual(actual, int(m.group(1)),
                         "CLAUDE.md claims {} engine modules, the package has {}".format(
                             m.group(1), actual))

    def test_the_corpus_counts_in_claude_md_are_current(self):  # verifies: REQ-SELFGATE-990#CASE-4
        """CLAUDE.md's corpus paragraph claimed 68 architecture requirements against 63,
        159 code against 191, 236 total against 263, and 197-in-71-files against 263-in-72.
        Every check in the repo passed while it said so, and an outside reader found it
        rather than a check. RM035 re-measures the same markers in any repo, but it is
        warn-only inside a run that already prints thirty-odd warnings — this is the half
        that fails a build. Asserting the marker SET first is what makes deleting a marker
        loud instead of silently reducing what is checked."""
        claude_md = open(os.path.join(self.root, "CLAUDE.md"), encoding="utf-8").read()
        claims = R.doc_claims(claude_md)
        self.assertEqual(
            {"total", "files", "level:system", "level:architecture", "level:code"},
            {kind for kind, _claimed, _line in claims},
            "CLAUDE.md no longer marks the corpus counts it states")
        counts = R.corpus_counts(
            R.load_requirements(os.path.join(self.root, "plugin", "requirements")))
        wrong = [(kind, claimed, counts.get(kind)) for kind, claimed, _line in claims
                 if counts.get(kind) != claimed]
        self.assertEqual([], wrong,
                         "CLAUDE.md states (kind, claimed, actual): {}".format(wrong))

    def test_the_index_states_no_count_it_would_have_to_maintain(self):  # verifies: REQ-SELFGATE-990#CASE-3
        # "Twenty-three decisions" was written when there were 23 and never moved again.
        index = open(os.path.join(self.root, "docs", "adr", "README.md"), encoding="utf-8").read()
        head = index.split("| # |")[0]
        self.assertNotRegex(head, r"(?i)\b(twenty|thirty|forty|fourteen|\d+)\s+decisions\b")


class CommandsManifest(unittest.TestCase):  # tested-by: ARCH-CMDREGISTRY-033  # tested-by: REQ-CMDREGISTRY-963
    """The CLI, emitted as data for any surface that documents it without running it."""

    def test_one_entry_per_user_facing_command(self):  # verifies: REQ-CMDREGISTRY-963#CASE-1
        names = [c["name"] for c in R.commands_manifest()]
        public = [n for n, spec in R.COMMANDS.items() if not spec.get("internal")]
        self.assertEqual(sorted(names), sorted(public))
        self.assertEqual(len(names), len(set(names)))

    def test_entry_carries_argument_summary_and_flags(self):  # verifies: REQ-CMDREGISTRY-963#CASE-2
        entry = next(c for c in R.commands_manifest() if c["name"] == "sync")
        self.assertTrue(entry["summary"])
        self.assertEqual(entry["arg"], R.COMMANDS["sync"]["arg"])
        flags = {f["flag"] for f in entry["flags"]}
        self.assertIn("--delete", flags)
        self.assertIn("--apply", flags)
        self.assertTrue(all(f["help"] for f in entry["flags"]))

    def test_every_command_is_placed_in_a_group(self):  # verifies: REQ-CMDREGISTRY-963#CASE-3
        groups = {g for g, _names in R.COMMAND_GROUPS}
        for c in R.commands_manifest():
            self.assertIn(c["group"], groups, c["name"])

    def test_manifest_rides_on_the_map_payload(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-M-001.md"),
                   REQ.format(id="AREA-M-001", status="confirmed", layer="feature", extra="", title="T"))
            reqs = R.load_requirements(rd)
            data = R._build_map_data(reqs, {})
            payload = json.loads(R._build_json_text(data))
        self.assertTrue(payload["commands"])
        self.assertIn("gate", [c["name"] for c in payload["commands"]])


class SearchByIdAndText(unittest.TestCase):  # tested-by: ARCH-SEARCH-036  # tested-by: REQ-SEARCH-965
    """The id is this corpus's primary key and was not in the index at all: searching
    for `ARCH-CHECK-006` returned REQ-ORPHANCODE-888 and never the requirement named."""

    def _corpus(self, d):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "AREA-X-001.md"), _spec("AREA-X-001", ["`gate` writes the lock."]))
        _write(os.path.join(rd, "AREA-X-002.md"), _spec("AREA-X-002", ["`sync` advances the baseline."]))
        _write(os.path.join(rd, "AREA-Y-003.md"),
               _spec("AREA-Y-003", ["the scanner walks the tree."],
                     cases=("CASE-1 \u2014 c\n  Given  a tag `GHOST-CAP-001` nothing defines\n"
                            "  When   it runs\n  Then   it reports a dangling tag",)))
        return rd

    def _run(self, d, query, top=5):
        rd = os.path.join(d, "requirements")
        reqs = R.load_requirements(rd)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_search(reqs, query, top=top, reqs_dir=rd)
        return code, buf.getvalue()

    def test_exact_id_is_the_first_result(self):  # verifies: REQ-SEARCH-965#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._corpus(d)
            _code, out = self._run(d, "AREA-X-001")
        first = [l for l in out.splitlines() if l.startswith("  ")][0]
        self.assertIn("AREA-X-001", first)
        self.assertIn("id", first)

    def test_partial_id_returns_the_ids_it_names(self):  # verifies: REQ-SEARCH-965#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._corpus(d)
            _code, out = self._run(d, "AREA-X")
        self.assertIn("AREA-X-001", out)
        self.assertIn("AREA-X-002", out)

    def test_a_phrase_inside_a_case_is_found(self):  # verifies: REQ-SEARCH-965#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._corpus(d)
            _code, out = self._run(d, "GHOST-CAP-001")
        self.assertIn("AREA-Y-003", out)

    def test_a_phrase_from_the_cached_translation_is_found(self):  # verifies: REQ-SEARCH-965#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = self._corpus(d)
            reqs = R.load_requirements(rd)
            body = reqs["AREA-X-001"]["body"]
            os.makedirs(os.path.join(rd, "_i18n"), exist_ok=True)
            with open(os.path.join(rd, "_i18n", "ro.json"), "w", encoding="utf-8") as f:
                json.dump({"AREA-X-001": {
                    "title": "t", "intent": "i",
                    "contract": "- `gate` scrie fisierul de blocare unic",
                    "acceptance": "a",
                    "hash": R.translation_hash(body, R._title(body))}}, f)
            _code, out = self._run(d, "fisierul de blocare unic")
        self.assertIn("AREA-X-001", out)

    def test_a_phrase_only_in_context_is_not_a_match(self):  # verifies: REQ-SEARCH-965#CASE-6
        """Commentary is not what a requirement is about — the same reason the ranking
        bag excludes it. Two existing tests caught this the moment the literal layer
        searched the whole document."""
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            body = _spec("AREA-Z-009", ["`gate` writes the lock."])
            body += "\n## Context\n**Notes**\n- the word xylophone appears only here.\n"
            _write(os.path.join(rd, "AREA-Z-009.md"), body)
            _code, out = self._run(d, "xylophone")
        self.assertNotIn("AREA-Z-009", out)

    def test_a_plain_query_still_comes_from_the_model(self):  # verifies: REQ-SEARCH-965#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self._corpus(d)
            _code, out = self._run(d, "baseline advances")
        rows = [l for l in out.splitlines() if l.startswith("  ") and l.strip()]
        self.assertTrue(rows)
        self.assertTrue(all("id " not in r[:8] and "text" not in r[:8] for r in rows), out)


class Audit20260906(unittest.TestCase):  # tested-by: ARCH-INIT-012  # tested-by: ARCH-RETIRE-064  # tested-by: ARCH-DECOMPOSE-050  # tested-by: ARCH-HEALTH-017  # tested-by: ARCH-PARSE-001  # tested-by: ARCH-MAP-007
    """Regressions for the 2026-09-06 full audit (docs/audit/2026-09-06-full-audit.md,
    removed later; `git show 9863fb9:docs/audit/2026-09-06-full-audit.md`)."""

    LONG = " ".join(["alpha"] * 155)
    REQ_BODY = ("# T\n\n## Description\n\nEvery bullet below is binding.\n- {}.\n\n"
                "## Cases\nCASE-1\n  Given  a\n  When   b\n  Then   c\n")

    def test_wipe_strips_only_what_the_scanner_reads_as_a_tag(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            os.makedirs(rdir)
            literal = 's = "{}\\ndef f(): pass"\n'.format(tag("A-B-001"))
            _write(os.path.join(d, "t.py"), "x = 1  {}\n".format(tag("A-B-001")) + literal)
            _write(os.path.join(d, "README.md"), "```\n{}\n```\n".format(tag("A-B-001")))
            with redirect_stdout(io.StringIO()):
                R._wipe(rdir, d)
            py = open(os.path.join(d, "t.py"), encoding="utf-8").read()
            self.assertEqual(py, "x = 1\n" + literal)            # literal intact, tag gone
            md = open(os.path.join(d, "README.md"), encoding="utf-8").read()
            self.assertIn(tag("A-B-001"), md)                     # fenced example intact

    def test_retire_strips_slash_comment_tags_and_respects_the_id_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.js"),
                   "// {}: X-A-001\n// {}: X-A-0011\nlet y = 1;\n".format(_ROLE, _ROLE))
            mem = [{"file": "a.js", "line": 1}]
            with redirect_stdout(io.StringIO()):
                n = R._strip_member_tags(d, mem, "X-A-001")
            self.assertEqual(n, 1)
            text = open(os.path.join(d, "a.js"), encoding="utf-8").read()
            self.assertEqual(text, "// {}: X-A-0011\nlet y = 1;\n".format(_ROLE))

    def test_health_link_sync_honours_gate_exempt(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "X-A-001.md"),
                   "---\nid: X-A-001\nstatus: confirmed\nlayer: feature\ngate_exempt: [RM006]\n---\n# T\n")
            reqs = R.load_requirements(d)
            self.assertEqual(R._link_sync_errors(reqs, {}), [])
            reqs["X-A-001"]["meta"].pop("gate_exempt")
            self.assertEqual(len(R._link_sync_errors(reqs, {})), 1)

    def test_next_free_number_reads_ids_inside_module_files(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "ARCH-X-001.md"),
                   "---\nid: ARCH-X-001\n---\n# A\n---\nid: REQ-X-900\n---\n# B\n")
            reqs = R.load_requirements(d)
            self.assertEqual(R._next_free_number(d, reqs), 901)
            self.assertEqual(R._next_free_number(d), 2)          # the old, name-only reading

    def test_decompose_is_scoped_to_the_named_requirement(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            os.makedirs(rdir)
            reqs = {}
            for rid in ("REQ-A-001", "REQ-B-001"):
                body = self.REQ_BODY.format(self.LONG)
                _write(os.path.join(rdir, rid + ".md"), "---\nid: {}\nstatus: confirmed\n---\n".format(rid) + body)
                reqs[rid] = {"meta": {"status": "confirmed", "layer": "feature"}, "body": body}
            with redirect_stdout(io.StringIO()):
                R.cmd_lint(R.Workspace(reqs, None, rdir), decompose=True, only="REQ-A-001")
            made = sorted(f for f in os.listdir(rdir) if f not in ("REQ-A-001.md", "REQ-B-001.md"))
            self.assertEqual(made, ["REQ-A-002.md"])

    def test_an_undecodable_requirement_file_is_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "X-A-001.md"), "---\nid: X-A-001\nstatus: draft\n---\n# T\n")
            with open(os.path.join(d, "X-B-001.md"), "wb") as f:
                f.write(b"---\nid: X-B-001\n---\n# caf\xe9\n")
            err = io.StringIO()
            with redirect_stderr(err):
                reqs = R.load_requirements(d)
            self.assertEqual(sorted(reqs), ["X-A-001"])
            self.assertIn("X-B-001.md", err.getvalue())

    def test_map_data_is_assembled_once_per_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "X-A-001.md"), "---\nid: X-A-001\nstatus: draft\n---\n# T\n")
            ws = R.Workspace.load(rdir, d)
            self.assertIs(ws.map_data(d), ws.map_data(d))
            self.assertIsNot(ws.map_data(d), ws.map_data(d, {}))   # a narrowed view is its own document

    def test_bullets_read_a_multiline_comment_as_one_unit(self):
        body = ("## Description\n- clause one\n<!-- glossary:\n  - not a clause\n-->\n"
                "- clause two\n  --flag continuation\n---\n")
        self.assertEqual(R._bullets(body, "description"),
                         ["clause one", "clause two --flag continuation"])



class AuditCrashIsNotClean(unittest.TestCase):  # tested-by: ARCH-AUDIT-065  # tested-by: REQ-AUDIT-970
    """Advice that crashes is missing advice; a gate that crashes reached no verdict."""

    @staticmethod
    def _boom():
        raise RuntimeError("gate exploded")

    def test_an_advice_section_that_raises_still_reports_zero(self):  # verifies: REQ-AUDIT-970#CASE-4
        _t, _r, text, rc = R._audit_section("Risk", "reqmap.py gate --risk", self._boom)
        self.assertEqual(rc, 0)
        self.assertIn("gate exploded", text)

    def test_a_gate_section_that_raises_fails_the_audit(self):  # verifies: REQ-AUDIT-970#CASE-6
        _t, _r, text, rc = R._audit_section("Gate", "reqmap.py gate", self._boom, fail_rc=1)
        self.assertEqual(rc, 1)
        self.assertIn("gate exploded", text)

    def test_the_report_says_FAIL_and_exits_1_when_the_gate_crashes(self):  # verifies: REQ-AUDIT-970#CASE-6
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        rdir = os.path.join(d, "requirements")
        _write(os.path.join(rdir, "AREA-A-001.md"),
               REQ.format(id="AREA-A-001", status="draft", layer="feature", extra="",
                          title="A") + "\n## Description\n- x\n\n## Cases\nCASE-1 x\n")
        ws = R.Workspace.load(rdir, d)
        buf = io.StringIO()
        with mock.patch.object(R.audit, "cmd_check", side_effect=RuntimeError("gate exploded")):
            with redirect_stdout(buf):
                rc = R.cmd_audit(ws)
        self.assertEqual(rc, 1)
        out = buf.getvalue()
        self.assertIn("FAIL", out)
        self.assertIn("gate exploded", out)


class OneUntaggedList(unittest.TestCase):  # tested-by: REQ-UNTAGGEDSET-1007 @unit
    """Two reports counted untagged files against different denominators: the risk bucket
    skipped files that carry no tag by contract, the coverage ratio counted them. The gap
    was files that appeared in no bucket, were named nowhere, and held the ratio's ceiling
    below 100% no matter what the author tagged."""

    def _repo(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reqs = os.path.join(d, "requirements")
        os.makedirs(reqs)
        os.makedirs(os.path.join(d, "docs", "adr"))
        _write(os.path.join(reqs, "ARCH-FOO-001.md"), _spec("ARCH-FOO-001", ["does a thing"]))
        _write(os.path.join(d, "app.py"), tag("ARCH-FOO-001") + "\ndef f(): pass\n")
        _write(os.path.join(d, "loose.py"), "def g(): pass\n")          # a real gap
        # by contract these never carry a tag
        _write(os.path.join(d, "CHANGELOG.md"), "# Changelog\n")
        _write(os.path.join(d, "SECURITY.md"), "# Security\n")
        _write(os.path.join(d, "docs", "adr", "0001-x.md"), "# ADR\n")
        return d, reqs

    def _ratio_untagged(self, d, reqs):
        """What the per-directory coverage ratio counts as untagged."""
        members = R.scan_members(d, reqs)
        tagged = {os.path.normcase(os.path.abspath(os.path.join(d, fp)))
                  for hits in members.values() for _r, fp, _l in hits}
        reqs_abs = os.path.normcase(os.path.abspath(reqs))
        out = []
        for fp, rel in R.scan._walk_code(d, reqs):
            n = os.path.normcase(os.path.abspath(fp))
            if (n.startswith(reqs_abs + os.sep) or R.orphans.untaggable_by_design(rel)
                    or rel.startswith(R.orphans.git_ignored(d))):
                continue
            if n not in tagged:
                out.append(rel)
        return sorted(out)

    def test_both_reports_name_the_same_list(self):  # verifies: REQ-UNTAGGEDSET-1007#CASE-1
        d, reqs = self._repo()
        self.assertEqual(self._ratio_untagged(d, reqs), R.orphans._scan_untagged(d, reqs))

    def test_the_list_is_the_real_gap_only(self):  # verifies: REQ-UNTAGGEDSET-1007#CASE-2
        d, reqs = self._repo()
        self.assertEqual(R.orphans._scan_untagged(d, reqs), ["loose.py"])

    def test_by_design_untaggable_files_are_named_as_excluded(self):  # verifies: REQ-UNTAGGEDSET-1007#CASE-3
        d, reqs = self._repo()
        for rel in ("CHANGELOG.md", "SECURITY.md", "docs/adr/0001-x.md"):
            self.assertTrue(R.orphans.untaggable_by_design(rel), rel)
        self.assertFalse(R.orphans.untaggable_by_design("loose.py"))
        ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_coverage(ws)
        out = buf.getvalue()
        self.assertIn("excluded", out)          # the difference is stated, not hidden
        self.assertIn("gate --risk", out)

    @unittest.skipUnless(shutil.which("git"), "needs git")
    def test_a_file_git_ignores_is_not_a_gap(self):  # verifies: REQ-UNTAGGEDSET-1007#CASE-5
        d, reqs = self._repo()
        _write(os.path.join(d, "notes.py"), "def h(): pass\n")
        self.assertIn("notes.py", R.orphans._scan_untagged(d, reqs))  # no git yet
        subprocess.run(["git", "init", "-q", d], check=True)
        _write(os.path.join(d, ".git", "info", "exclude"), "notes.py\n")
        self.assertEqual(R.orphans._scan_untagged(d, reqs), ["loose.py"])
        self.assertEqual(self._ratio_untagged(d, reqs), ["loose.py"])
        ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_coverage(ws, as_json=True)
        self.assertEqual(sum(r["total"] for r in json.loads(buf.getvalue())["rows"]),
                         2)  # app.py and loose.py: notes.py is not counted

    def test_the_ratio_can_reach_a_hundred_percent(self):  # verifies: REQ-UNTAGGEDSET-1007#CASE-4
        d, reqs = self._repo()
        _write(os.path.join(d, "loose.py"), tag("ARCH-FOO-001") + "\ndef g(): pass\n")
        ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_coverage(ws)
        self.assertIn("(100%)", buf.getvalue())
        self.assertEqual(R.orphans._scan_untagged(d, reqs), [])

    def test_json_carries_the_excluded_count(self):  # verifies: REQ-UNTAGGEDSET-1007#CASE-3
        d, reqs = self._repo()
        ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_coverage(ws, as_json=True)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["excluded_by_design"], 3)
        self.assertTrue(all("dir" in row for row in data["rows"]))


class PlanBucket(unittest.TestCase):  # tested-by: ARCH-NEXT-013  # tested-by: REQ-PLANGAPS-1033
    """`next`'s Plan bucket: the horizon work the plan files leave open. The three
    signals existed only in `sync` and `gate --audit`; they answer the question this
    report asks, so they are shown here too, from the same predicate."""
    ROADMAP = ("# Roadmap\n\n## Now\n\n- [ ] Write the README | req: REQ-A-001\n"
               "\n## Later\n\n- [ ] Someday idea\n")

    def _repo(self, d, roadmap=None, planning=None):
        """A tempdir holding a code root, a requirements dir and the two plan files.
        `.reqmapignore` carries ROADMAP.md exactly as `init` seeds it, so the plan
        file itself is not reported as untagged code."""
        rd = os.path.join(d, "requirements")
        os.makedirs(rd)
        if roadmap is not None:
            _write(os.path.join(d, "ROADMAP.md"), roadmap)
        if planning is not None:
            _write(os.path.join(rd, "_planning.json"), json.dumps(planning))
        _write(os.path.join(d, ".reqmapignore"), "ROADMAP.md\n")
        return rd

    def _reqs(self):
        return {"REQ-A-001": {"meta": {"status": "confirmed"}, "body": "# T\n"}}

    def _members(self):
        return {"REQ-A-001": [("implements", "a.py", 1), ("tested-by", "t.py", 2)]}

    def _next(self, d, rd, show_all=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_next(R.Workspace(self._reqs(), self._members(), rd, d), show_all)
        return code, buf.getvalue()

    def _health(self, d, rd):
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_health(R.Workspace(self._reqs(), self._members(), rd, d), as_json=True)
        return json.loads(buf.getvalue())

    def test_unscheduled_now_item_is_named(self):  # verifies: REQ-PLANGAPS-1033#CASE-1  # verifies: ARCH-NEXT-013#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=self.ROADMAP, planning={"bars": []})
            code, out = self._next(d, rd)
            self.assertEqual(code, 0)
            self.assertIn("Plan (", out)
            self.assertIn("Write the README", out)
            self.assertIn("no bar", out)

    def test_bar_scheduled_item_is_not_a_gap(self):  # verifies: REQ-PLANGAPS-1033#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=self.ROADMAP,
                            planning={"bars": [{"title": "Write the README",
                                                "lane": "Feature", "start": "2026-10-01",
                                                "end": "2026-10-02"}]})
            _, out = self._next(d, rd, show_all=True)
            self.assertNotIn("Write the README", out)

    def test_parked_item_without_unpark_is_named(self):  # verifies: REQ-PLANGAPS-1033#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=self.ROADMAP, planning={"bars": []})
            _, out = self._next(d, rd, show_all=True)
            self.assertIn("Someday idea", out)
            self.assertIn("unpark", out)

    def test_unparked_item_with_a_condition_is_not_a_gap(self):  # verifies: REQ-PLANGAPS-1033#CASE-2
        plan = self.ROADMAP.replace("- [ ] Someday idea",
                                    "- [ ] Someday idea | unpark: a second consumer asks")
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=plan, planning={"bars": []})
            _, out = self._next(d, rd, show_all=True)
            self.assertNotIn("Someday idea", out)

    def test_item_naming_absent_requirement_is_named(self):  # verifies: REQ-PLANGAPS-1033#CASE-3
        plan = self.ROADMAP.replace("req: REQ-A-001", "req: ARCH-GONE-999")
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=plan, planning={"bars": []})
            _, out = self._next(d, rd, show_all=True)
            self.assertIn("ARCH-GONE-999 missing", out)

    def test_no_roadmap_means_no_bucket_and_no_key(self):  # verifies: REQ-PLANGAPS-1033#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=None, planning={"bars": []})
            _, out = self._next(d, rd)
            self.assertNotIn("Plan (", out)
            self.assertNotIn("plan_gaps", self._health(d, rd))

    def test_count_matches_what_the_bucket_names(self):  # verifies: REQ-PLANGAPS-1033#CASE-5
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=self.ROADMAP, planning={"bars": []})
            _, out = self._next(d, rd, show_all=True)
            heading = re.search(r"Plan \((\d+)\)", out)
            self.assertIsNotNone(heading)
            self.assertEqual(self._health(d, rd)["plan_gaps"], int(heading.group(1)))

    def test_a_plan_gap_alone_is_not_nothing_pending(self):  # verifies: REQ-PLANGAPS-1033#CASE-6
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap=self.ROADMAP, planning={"bars": []})
            _, out = self._next(d, rd)
            self.assertNotIn("Nothing pending", out)
            self.assertIn("Plan (", out)

    def test_bucket_truncates_and_all_expands(self):  # verifies: REQ-PLANGAPS-1033#CASE-1
        items = "".join("- [ ] Item {}\n".format(i) for i in range(5))
        with tempfile.TemporaryDirectory() as d:
            rd = self._repo(d, roadmap="# Roadmap\n\n## Now\n\n" + items,
                            planning={"bars": []})
            _, out = self._next(d, rd)
            self.assertIn("more — run `reqmap.py gate --risk --all`", out)
            _, out_all = self._next(d, rd, show_all=True)
            for i in range(5):
                self.assertIn("Item {}".format(i), out_all)

class RemovedInV820(unittest.TestCase):  # tested-by: ARCH-CMDREGISTRY-033  # tested-by: ARCH-CONFIG-060
    """ADR-0047: the i18n detector left the engine; its flag stays one release, doing
    nothing but saying so."""

    def _main(self, *argv):
        err = io.StringIO()
        old = sys.argv
        sys.argv = ["reqmap"] + list(argv)
        try:
            with redirect_stdout(io.StringIO()) as out, redirect_stderr(err):
                rc = R.main()
        finally:
            sys.argv = old
        return rc, out.getvalue(), err.getvalue()

    def test_a_removed_ask_flag_says_so_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "requirements"))
            rc, _, err = self._main("ask", "--i18n", "--root", d)
            self.assertEqual(0, rc)
            self.assertIn("removed in v8.2.0", err)
            self.assertIn("ADR-0047", err)

    def test_a_retired_config_key_is_ignored_in_silence(self):
        err = io.StringIO()
        applied = R.config.apply_config({"DESIGN_RFC_MAX": 10, "LANGUAGE": "ro",
                                         "DESIGN_DOCSTRING_PUBLIC": 0,
                                         "DESIGN_FILE_MAX_FUNCS": 9,
                                         "NOT_A_KEY": 1}, out=err)
        self.assertEqual([], applied)
        for key in ("DESIGN_RFC_MAX", "DESIGN_DOCSTRING_PUBLIC", "DESIGN_FILE_MAX_FUNCS"):
            self.assertNotIn(key, err.getvalue())
        self.assertNotIn("LANGUAGE", err.getvalue())
        self.assertIn("NOT_A_KEY", err.getvalue())


class Design(unittest.TestCase):  # tested-by: ARCH-DESIGN-061  # tested-by: REQ-DESIGN-950  # tested-by: REQ-DESIGN-951  # tested-by: REQ-DESIGN-952  # tested-by: REQ-DESIGN-953  # tested-by: REQ-DESIGN-955
    """`ask --design`: advisory candidates against the four pillars plus two
    writing rules, never the gate (ADR-0051)."""

    def _kinds(self, src):
        return [f["kind"] for f in R._design_file("m.py", src) if f["pillar"] != "standards"]

    def _set(self, **kw):
        for k, v in kw.items():
            self.addCleanup(setattr, R.config, k, getattr(R.config, k))
            setattr(R.config, k, v)

    def test_global_state_and_long_parameter_list(self):  # verifies: REQ-DESIGN-950#CASE-1
        src = ("COUNT = 0\n"
               "def bump():\n    global COUNT\n    COUNT += 1\n"
               "def wide(a, b, c, d, e, f, g):\n    return a\n")
        kinds = self._kinds(src)
        self.assertIn("global-state", kinds)
        self.assertIn("long-parameter-list", kinds)

    def test_data_clump_needs_three_carriers(self):  # verifies: REQ-DESIGN-950#CASE-2
        two = "def f(host, port, user): pass\ndef g(host, port, user): pass\n"
        self.assertNotIn("data-clump", self._kinds(two))
        three = two + "def h(host, port, user, x): pass\n"
        f = [x for x in R._design_file("m.py", three) if x["kind"] == "data-clump"]
        self.assertEqual(len(f), 1)
        self.assertIn("host, port, user", f[0]["detail"])
        self.assertEqual(f[0]["pillar"], "encapsulation")

    def test_long_function_and_deep_nesting(self):  # verifies: REQ-DESIGN-950#CASE-3
        long_src = "def big():\n" + "".join("    x = {}\n".format(i) for i in range(90))
        self.assertIn("long-function", self._kinds(long_src))
        deep = ("def deep(a):\n    if a:\n        for i in a:\n            while i:\n"
                "                with a:\n                    if i:\n"
                "                        pass\n")
        self.assertIn("deep-nesting", self._kinds(deep))
        self.assertNotIn("deep-nesting", self._kinds("def ok(a):\n    if a:\n        return 1\n"))

    def test_prefix_family(self):  # verifies: REQ-DESIGN-950#CASE-4
        src = "".join("def _scan_{}(): pass\n".format(i) for i in range(6))
        f = [x for x in R._design_file("m.py", src) if x["kind"] == "prefix-family"]
        self.assertEqual([(x["name"], x["pillar"]) for x in f], [("scan", "abstraction")])

    def test_shared_methods_and_duplicate_method(self):  # verifies: REQ-DESIGN-951#CASE-1
        src = ("class A:\n    def load(self): return 1\n    def save(self): return 2\n"
               "    def close(self): pass\n"
               "class B:\n    def load(self): return 3\n    def save(self): return 2\n"
               "    def close(self): pass\n")
        f = R._design_file("m.py", src)
        self.assertIn("shared-methods", [x["kind"] for x in f])
        dup = [x for x in f if x["kind"] == "duplicate-method"]
        self.assertEqual(sorted(x["name"] for x in dup), ["B.close", "B.save"])
        self.assertEqual({x["pillar"] for x in dup}, {"inheritance"})

    def test_related_classes_are_not_reported(self):  # verifies: REQ-DESIGN-951#CASE-2
        methods = ("    def load(self): pass\n    def save(self): pass\n"
                   "    def close(self): pass\n")
        src = "class Base:\n    pass\nclass A(Base):\n" + methods + "class B(Base):\n" + methods
        self.assertNotIn("shared-methods", self._kinds(src))

    def test_isinstance_chain_and_type_switch(self):  # verifies: REQ-DESIGN-951#CASE-3
        src = ("def f(x, kind):\n"
               "    if isinstance(x, int):\n        pass\n"
               "    elif isinstance(x, str):\n        pass\n"
               "    elif isinstance(x, list):\n        pass\n"
               "    if kind == 'a':\n        pass\n    elif kind == 'b':\n        pass\n"
               "    elif kind == 'c':\n        pass\n    elif kind == 'd':\n        pass\n")
        f = [x for x in R._design_file("m.py", src) if x["pillar"] != "standards"]
        self.assertEqual([x["kind"] for x in f], ["isinstance-chain", "type-switch"])
        self.assertEqual([x["name"] for x in f], ["x", "kind"])
        self.assertTrue(all(x["pillar"] == "polymorphism" for x in f))

    def test_short_chains_are_silent(self):  # verifies: REQ-DESIGN-951#CASE-4
        src = ("def f(x, kind):\n    if isinstance(x, int):\n        pass\n"
               "    elif isinstance(x, str):\n        pass\n"
               "    if kind == 'a':\n        pass\n    elif kind == 'b':\n        pass\n"
               "    elif kind == 'c':\n        pass\n")
        self.assertEqual(self._kinds(src), [])

    def test_report_groups_by_pillar_and_exits_zero(self):  # verifies: REQ-DESIGN-952#CASE-1  # verifies: ARCH-DESIGN-061#CASE-1
        src = "COUNT = 0\ndef bump():\n    global COUNT\n    COUNT += 1\n"
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), src)
            _write(os.path.join(d, "tests", "test_m.py"), src)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_design(d)
            out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Encapsulation (1)", out)
        self.assertIn("m.py:2  global-state", out)
        self.assertNotIn("test_m.py", out)
        self.assertIn("Advisory only", out)

    def test_json_output_and_clean_tree(self):  # verifies: REQ-DESIGN-952#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), "def ok():\n    return 1\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_design(d, as_json=True)
            data = json.loads(buf.getvalue())
            self.assertEqual((code, data["files"], data["findings"]), (0, 1, []))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_design(d)
            self.assertIn("No design candidates", buf.getvalue())

    def test_syntax_error_yields_nothing(self):  # verifies: REQ-DESIGN-952#CASE-3
        self.assertEqual(R._design_file("m.py", "def (:\n" + "x" * 200 + "\n"), [])

    def test_thresholds_are_configurable(self):  # verifies: REQ-DESIGN-952#CASE-4  # verifies: ARCH-DESIGN-061#CASE-2
        self._set(DESIGN_PARAMS_MAX=R.config.DESIGN_PARAMS_MAX)
        src = "def f(a, b, c): pass\n"
        self.assertEqual(self._kinds(src), [])
        R.apply_config({"DESIGN_PARAMS_MAX": 2}, out=io.StringIO())
        self.assertIn("long-parameter-list", self._kinds(src))

    def test_file_length_and_line_width(self):  # verifies: REQ-DESIGN-953#CASE-1
        src = ("".join("x{} = 1\n".format(i) for i in range(500))
               + "y = '" + "z" * 80 + "'\n")
        f = {x["kind"]: x for x in R._design_file("m.py", src)}
        self.assertIn("file-too-long", f)
        self.assertEqual(f["line-too-long"]["line"], 501)
        self.assertIn("1 line(s) wider than 80", f["line-too-long"]["detail"])
        self.assertEqual({x["pillar"] for x in f.values()}, {"standards"})

    def test_the_defaults_are_500_lines_and_80_columns(self):  # verifies: REQ-DESIGN-953#CASE-2
        self.assertEqual((R.config.DESIGN_FILE_MAX_LINES, R.config.DESIGN_LINE_MAX),
                         (500, 80))
        ok = "".join("x = '{}'\n".format("y" * 72) for _ in range(499))
        self.assertEqual(R._design_file("m.py", ok), [])

    def test_the_writing_rules_are_configurable(self):  # verifies: REQ-DESIGN-953#CASE-3
        self._set(DESIGN_FILE_MAX_LINES=500, DESIGN_LINE_MAX=80)
        src = "x = '" + "y" * 90 + "'\n"
        self.assertEqual([f["kind"] for f in R._design_file("m.py", src)],
                         ["line-too-long"])
        R.apply_config({"DESIGN_LINE_MAX": 120}, out=io.StringIO())
        self.assertEqual(R._design_file("m.py", src), [])

    def test_standards_print_last(self):  # verifies: REQ-DESIGN-953#CASE-4
        src = ("COUNT = 0\ndef bump():\n    global COUNT\n"
               "    COUNT += 1  # " + "c" * 80 + "\n")
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), src)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_design(d)
            out = buf.getvalue()
        self.assertLess(out.index("Encapsulation (1)"), out.index("Standards (1)"))

    def test_javascript_functions_classes_and_switch(self):  # verifies: REQ-DESIGN-955#CASE-1  # verifies: ARCH-DESIGN-061#CASE-4
        src = (
            "// comment with { brace and 'quote\n"
            "function wide(a, b, c, d, e, f, g) { return a; }\n"
            "const arrow = (x, y) => { return x + y; };\n"
            "class Store { load() { return 1; } save() { return 2; } close() { } }\n"
            "class Cache { load() { return 3; } save() { return 2; } close() { } }\n"
            "function pick(kind, v) {\n"
            "  switch (kind) { case 'a': return 1; case 'b': return 2;\n"
            "    case 'c': return 3; case 'd': return 4; }\n"
            "  if (v instanceof Foo) { } else if (v instanceof Bar) { }\n"
            "  else if (v instanceof Baz) { }\n"
            "}\n")
        f = R._design_file("m.js", src)
        kinds = {x["kind"] for x in f}
        for k in ("long-parameter-list", "shared-methods", "duplicate-method",
                  "type-switch", "isinstance-chain"):
            self.assertIn(k, kinds)
        self.assertEqual([x["name"] for x in f if x["kind"] == "type-switch"], ["kind"])
        self.assertEqual([x["name"] for x in f if x["kind"] == "isinstance-chain"], ["v"])
        self.assertIn("Cache.save",
                      [x["name"] for x in f if x["kind"] == "duplicate-method"])

    def test_cpp_long_function_and_dynamic_cast_chain(self):  # verifies: REQ-DESIGN-955#CASE-2
        body = "".join("    x += {};\n".format(i) for i in range(90))
        src = ("#include <x>\n"
               "int compute(const std::string& name, int n) {\n" + body
               + "    return x;\n}\n"
               "void handle(Shape* s) {\n"
               "    if (dynamic_cast<Circle*>(s)) { }\n"
               "    else if (dynamic_cast<Square*>(s)) { }\n"
               "    else if (dynamic_cast<Tri*>(s)) { }\n}\n")
        f = R._design_file("shapes.cpp", src)
        self.assertEqual([x["name"] for x in f if x["kind"] == "long-function"], ["compute"])
        self.assertIn("isinstance-chain", [x["kind"] for x in f])

    def test_masking_hides_braces_in_strings_and_comments(self):  # verifies: REQ-DESIGN-955#CASE-3
        src = ('function f() { const s = "{{{"; /* } */ return s; } // {\n'
               "function g() { return 1; }\n")
        f = R._design_file("m.js", src)
        self.assertEqual([x for x in f if x["kind"] in ("long-function", "deep-nesting")], [])
        masked = R._design_mask(src)
        self.assertNotIn('"{{{"', masked)
        self.assertEqual(masked.count("\n"), src.count("\n"))

    def test_other_languages_get_standards_only(self):  # verifies: REQ-DESIGN-955#CASE-4
        src = "def a\n  1\nend\n" + "x = '" + "y" * 120 + "'\n"
        self.assertEqual([x["kind"] for x in R._design_file("m.rb", src)], ["line-too-long"])
        self.assertEqual(R._design_file("m.rb", "def a\n  1\nend\n"), [])

    def test_ask_design_runs_and_is_not_a_gate_rule(self):  # verifies: ARCH-DESIGN-061#CASE-3
        self.assertFalse(any("design" in (r.fn.__name__ or "") for r in R.GATE_RULES))
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "requirements"))
            _write(os.path.join(d, "m.py"), "def bump():\n    global C\n    C = 1\n")
            old, sys.argv = sys.argv, ["reqmap", "ask", "--design", "--root", d]
            try:
                with redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
                    rc = R.main()
            finally:
                sys.argv = old
        self.assertEqual(rc, 0)
        self.assertIn("global-state", out.getvalue())

    def test_the_requirement_names_every_pillar(self):
        """REQ-DESIGN-952's print-order clause enumerates the pillars; a pillar
        added without editing it would go stale with no DRIFT."""
        here = os.path.dirname(os.path.abspath(__file__))
        doc = os.path.join(here, "..", "requirements", "ARCH-DESIGN-061.md")
        with open(doc, encoding="utf-8") as f:
            clause = [ln for ln in f.read().splitlines()
                      if "prints one block per group in the order" in ln]
        self.assertEqual(len(clause), 1)
        named = [p for p in R.DESIGN_PILLARS if p in clause[0]]
        self.assertEqual(named, list(R.DESIGN_PILLARS))



def _one_req(rq):
    _write(os.path.join(rq, "AREA-A-001.md"),
           REQ.format(id="AREA-A-001", status="baseline", layer="feature",
                      extra="", title="T"))


def _health_json(reqs, rq, d):
    buf = io.StringIO()
    with redirect_stdout(buf):
        R.cmd_health(R.Workspace(reqs, {}, rq, d), as_json=True)
    return buf.getvalue()


class DesignSummary(unittest.TestCase):
    # tested-by: ARCH-DESIGN-061  # tested-by: REQ-DESIGN-954
    # tested-by: REQ-DESIGN-976
    """The design record in `_map.json`, `_map.md`, `health` and `audit`."""

    def _dirty_repo(self, d):
        """One clean file and one carrying a candidate, so the record has a
        score below 100."""
        _write(os.path.join(d, "clean.py"), "def a():\n    return 1\n")
        _write(os.path.join(d, "dirty.py"),
               "COUNT = 0\ndef bump():\n    global COUNT\n    COUNT += 1\n")

    def test_design_summary_scores_clean_files(self):
        # verifies: REQ-DESIGN-954#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R._design_summary(d))
            self._dirty_repo(d)
            _write(os.path.join(d, "tests", "test_x.py"),
                   "def bump():\n    global COUNT\n")
            s = R._design_summary(d)
        self.assertEqual((s["files"], s["clean_files"], s["score"]),
                         (2, 1, 50))
        self.assertEqual(s["candidates"]["encapsulation"], 1)
        self.assertEqual(s["candidates"]["standards"], 0)
        self.assertEqual(list(s["candidates"]), list(R.DESIGN_PILLARS))
        self.assertNotIn("metrics", s["candidates"])

    def test_map_and_health_carry_the_design_score(self):
        # verifies: REQ-DESIGN-954#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _one_req(rq)
            _write(os.path.join(d, "m.py"), "def a():\n    return 1\n")
            reqs = R.load_requirements(rq)
            data = R._assemble_map_data(reqs, {}, rq, d)
            self.assertEqual(data["design"]["score"], 100)
            md = R._build_md_text(dict(data, todos=[]))
            self.assertIn("design pass-rate: 100% (1/1 source files", md)
            self.assertIn('"design": {', R._build_json_text(data))
            out = json.loads(_health_json(reqs, rq, d))
        self.assertEqual((out["design_score"], out["design_files"]), (100, 1))

    def test_no_program_logic_means_no_design_key(self):
        # verifies: REQ-DESIGN-954#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _one_req(rq)
            _write(os.path.join(d, "site.css"), "body { margin: 0 }\n")
            reqs = R.load_requirements(rq)
            data = R._assemble_map_data(reqs, {}, rq, d)
            out = json.loads(_health_json(reqs, rq, d))
        self.assertNotIn("design", data)
        self.assertNotIn("design pass-rate", R._build_md_text(data))
        self.assertNotIn("design_score", out)

    def test_health_text_and_audit_carry_the_line(self):
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _one_req(rq)
            self._dirty_repo(d)
            ws = R.Workspace(R.load_requirements(rq), {}, rq, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(ws)
            line = R.audittail._design_candidate_line(d, rq)
        self.assertIn("design pass-rate (files w/o candidate): 50%",
                      buf.getvalue())
        self.assertEqual(line, "design pass-rate 50% - 1 of 2 source "
                               "files carry a candidate")

    def test_design_summary_omits_findings_by_default(self):
        # verifies: REQ-DESIGN-976#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._dirty_repo(d)
            s = R._design_summary(d)
        self.assertEqual(sorted(s),
                         ["candidates", "clean_files", "files", "score"])

    def test_design_summary_with_findings_lists_every_candidate(self):
        # verifies: REQ-DESIGN-976#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._dirty_repo(d)
            s = R._design_summary(d, with_findings=True)
        self.assertEqual(len(s["findings"]), sum(s["candidates"].values()))
        one = s["findings"][0]
        self.assertEqual(sorted(one), ["detail", "file", "kind", "line",
                                       "name", "pillar"])
        # advice belongs to the rule: once per kind, never per row
        self.assertEqual(sorted(s["advice"]),
                         sorted({f["kind"] for f in s["findings"]}))

    def test_map_carries_the_candidates_and_health_does_not(self):
        # verifies: REQ-DESIGN-976#CASE-2  # verifies: REQ-DESIGN-976#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _one_req(rq)
            self._dirty_repo(d)
            reqs = R.load_requirements(rq)
            data = R._assemble_map_data(reqs, {}, rq, d)
            out = _health_json(reqs, rq, d)
        design = data["design"]
        self.assertEqual(len(design["findings"]),
                         sum(design["candidates"].values()))
        self.assertGreater(len(design["findings"]), 0)
        self.assertNotIn("findings", out)

    def test_design_block_is_byte_stable_across_runs(self):
        # verifies: REQ-DESIGN-976#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _one_req(rq)
            self._dirty_repo(d)
            reqs = R.load_requirements(rq)
            first = R._assemble_map_data(reqs, {}, rq, d)["design"]
            second = R._assemble_map_data(reqs, {}, rq, d)["design"]
        self.assertEqual(json.dumps(first, sort_keys=True),
                         json.dumps(second, sort_keys=True))


class AdvisoryDataCarriesNoVerdict(unittest.TestCase):
    # tested-by: ARCH-DESIGN-061  # tested-by: REQ-DESIGN-991
    """Issue #243: one blank line in a file no requirement claims moved a
    `line:` in `design.findings`, made the committed map stale, and failed
    `gate` with zero requirement errors."""

    def _repo(self, d):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "A-M-001.md"),
               _spec("A-M-001", ["`gate` writes the lock."]))
        _write(os.path.join(d, "impl.py"), "x = 1  " + tag("A-M-001"))
        reqs = R.load_requirements(rd)
        data = R._build_map_data(reqs, R.scan_members(d, rd))
        data["design"] = {
            "files": 2, "clean_files": 1, "score": 50,
            "candidates": {"abstraction": 1},
            "findings": [{"pillar": "abstraction", "kind": "long-function",
                          "file": "untagged.py", "line": 12, "name": "f",
                          "detail": "42 lines"}],
            "advice": {"long-function": "shorten it"}}
        data["health"] = {"score": 90, "total": 1}
        R.render_json(data, rd)
        R.render_md(data, rd)
        return rd, data

    def _stale(self, rd, data, root):
        return R._stale_artifacts(data, R.Workspace(None, None, rd), root)

    def test_baseline_is_fresh(self):
        with tempfile.TemporaryDirectory() as d:
            rd, data = self._repo(d)
            self.assertEqual([], self._stale(rd, data, d))

    def test_a_moved_advisory_line_number_is_not_staleness(self):
        # verifies: REQ-DESIGN-991#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd, data = self._repo(d)
            data["design"]["findings"][0]["line"] = 999
            self.assertEqual([], self._stale(rd, data, d))

    def test_a_changed_design_score_is_not_staleness(self):
        # verifies: REQ-DESIGN-991#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd, data = self._repo(d)
            data["design"]["score"] = 3
            data["design"]["clean_files"] = 0
            self.assertEqual([], self._stale(rd, data, d))

    def test_a_changed_requirement_still_is(self):
        # verifies: REQ-DESIGN-991#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd, data = self._repo(d)
            data["nodes"][0]["title"] = "something else entirely"
            self.assertIn("_map.json", self._stale(rd, data, d))

    def test_a_changed_health_number_still_is(self):
        # verifies: REQ-DESIGN-991#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd, data = self._repo(d)
            data["health"]["score"] = 12
            self.assertIn("_map.json", self._stale(rd, data, d))

    def test_the_design_rows_stay_in_the_artifact(self):
        # Excluded from the comparison, not from the file: the viewer's
        # Design tab renders them.
        with tempfile.TemporaryDirectory() as d:
            rd, _data = self._repo(d)
            with open(os.path.join(rd, "_map.json"), encoding="utf-8") as f:
                doc = json.load(f)
        self.assertEqual(1, len(doc["design"]["findings"]))
        self.assertEqual(12, doc["design"]["findings"][0]["line"])

    def test_the_stripper_drops_the_block_and_keeps_what_follows(self):
        text = "\n".join([
            '{', '  "nodes": [],', '  "design": {', '    "score": 50,',
            '    "findings": [', '      {', '        "line": 12', '      }',
            '    ]', '  },', '  "health": {', '    "score": 90', '  }', '}'])
        out = R._strip_generated(text)
        self.assertNotIn("findings", out)
        self.assertNotIn('"score": 50', out)
        self.assertIn('"health"', out)
        self.assertIn('"score": 90', out)
        self.assertIn('"nodes": []', out)

    def test_a_blank_line_in_an_untagged_file_does_not_fail_the_gate(self):
        # verifies: REQ-DESIGN-991#CASE-5
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "A-M-001.md"),
                   _spec("A-M-001", ["`gate` writes the lock."]))
            _write(os.path.join(d, "impl.py"), "x = 1  " + tag("A-M-001"))
            n = R.config.DESIGN_FUNC_MAX_LINES + 10
            long_fn = ("def sprawling():\n"
                       + "".join("    v{} = {}\n".format(i, i)
                                 for i in range(n))
                       + "    return v0\n")
            untagged = os.path.join(d, "untagged.py")
            _write(untagged, long_fn)
            ws = R.Workspace.load(rd, d)
            data = ws.map_data(d)
            R.render_json(data, rd)
            R.render_md(data, rd)
            self.assertTrue(data.get("design", {}).get("findings"),
                            "fixture produced no design finding to move")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(0, R.cmd_map(R.Workspace.load(rd, d), d,
                                              True))
            _write(untagged, "\n" + long_fn)      # one blank line at the top
            ws2 = R.Workspace.load(rd, d)
            moved = ws2.map_data(d)["design"]["findings"][0]["line"]
            self.assertEqual(data["design"]["findings"][0]["line"] + 1, moved,
                             "the advisory line did not move")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_map(ws2, d, True)
        self.assertEqual(0, rc, buf.getvalue())
        self.assertNotIn("stale", buf.getvalue())

    def test_the_md_design_summary_line_is_dropped(self):
        text = "\n".join(["---", "generated: 2026-01-01", "nodes: 3",
                          "design pass-rate: 29% (9/31 files)", "---",
                          "# Map"])
        out = R._strip_generated(text)
        self.assertNotIn("design pass-rate", out)
        self.assertIn("nodes: 3", out)


class HealthRows(unittest.TestCase):  # tested-by: REQ-HEALTHROWS-1083
    """The rows behind the health score, emitted beside it for the map."""

    BODY = ("# T\n\n## Description\n\nEvery bullet below is binding.\n"
            "- It works.\n\n## Cases\nCASE-1\n  Given  a\n  When   b\n"
            "  Then   c\n")

    def _req(self, status, **meta):
        m = {"status": status, "layer": "feature"}
        m.update(meta)
        return {"meta": m, "body": self.BODY}

    def _rec(self, reqs, members, with_rows=True):
        with tempfile.TemporaryDirectory() as d:
            return R._health_record(reqs, members, d, with_rows=with_rows)

    def test_a_draft_is_listed_as_not_confirmed(self):
        # verifies: REQ-HEALTHROWS-1083#CASE-1
        reqs = {"REQ-A-001": self._req("confirmed"),
                "REQ-A-002": self._req("draft")}
        members = {rid: [("implements", "x.py", 1), ("tested-by", "t.py", 2)]
                   for rid in reqs}
        rec = self._rec(reqs, members)
        self.assertEqual(rec["unhealthy"], [
            {"id": "REQ-A-002", "status": "draft",
             "why": ["not confirmed"]}])

    def test_a_waiver_is_listed_with_its_keys(self):
        # verifies: REQ-HEALTHROWS-1083#CASE-2
        reqs = {"REQ-A-001": self._req("confirmed", test_exempt="wiring")}
        members = {"REQ-A-001": [("implements", "x.py", 1)]}
        rec = self._rec(reqs, members)
        self.assertEqual(rec["exempt_ids"],
                         [{"id": "REQ-A-001", "keys": ["test_exempt"]}])
        self.assertEqual(rec["unhealthy"], [])

    def test_no_rows_unless_asked(self):
        # verifies: REQ-HEALTHROWS-1083#CASE-3
        reqs = {"REQ-A-001": self._req("draft")}
        rec = self._rec(reqs, {}, with_rows=False)
        self.assertNotIn("unhealthy", rec)
        self.assertNotIn("exempt_ids", rec)


class CommandConsumers(unittest.TestCase):  # tested-by: ARCH-CMDREGISTRY-033
    """Every OPTIONAL verb or flag names where a real use is written down."""

    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))

    @staticmethod
    def _entries():
        """(verb, flag or None, entry dict) for every verb and flag."""
        for verb, spec in R.COMMANDS.items():
            yield verb, None, spec
            for p in spec["params"]:
                yield verb, p["flag"], p

    @staticmethod
    def _is_core(verb, flag):
        from reqmap_engine.commands import CORE_PATH
        return verb in CORE_PATH and (flag is None or flag in CORE_PATH[verb])

    def test_every_optional_entry_names_a_consumer(self):
        missing = []
        for verb, flag, entry in self._entries():
            if self._is_core(verb, flag):
                continue
            c = entry.get("consumer")
            values = [c] if isinstance(c, str) else list(c or [])
            if not values or not all(isinstance(v, str) and v.strip()
                                     for v in values):
                missing.append("{} {}".format(verb, flag or "").strip())
        self.assertEqual(missing, [])

    def test_core_path_is_what_the_hook_and_ci_run(self):
        from reqmap_engine.commands import CORE_PATH
        self.assertTrue(self._is_core("gate", None))
        self.assertTrue(self._is_core("gate", "--full"))
        self.assertTrue(self._is_core("sync", None))
        self.assertTrue(self._is_core("init", None))
        # a core entry is not required to carry one: the check skips it
        self.assertFalse(self._is_core("gate", "--audit"))
        self.assertFalse(self._is_core("ask", None))
        for verb, flags in CORE_PATH.items():
            owned = {p["flag"] for p in R.COMMANDS[verb]["params"]}
            self.assertLessEqual(set(flags), owned, verb)
        for rel in (".githooks/pre-commit", ".github/workflows/ci.yml"):
            with open(os.path.join(self.ROOT, rel), encoding="utf-8") as fh:
                self.assertIn("reqmap.py gate --full", fh.read(), rel)

    def test_generated_artifacts_ignore_consumer(self):
        import copy
        import reqmap_engine.registry as G
        stripped = copy.deepcopy(R.COMMANDS)
        for spec in stripped.values():
            spec.pop("consumer", None)
            for p in spec["params"]:
                p.pop("consumer", None)
        gens = (G._generate_schema, G._generate_command_table,
                G._generate_command_list)
        before = [g() for g in gens]
        with mock.patch.object(G, "COMMANDS", stripped):
            after = [g() for g in gens]
        self.assertEqual(before, after)


class CompactExports(unittest.TestCase):
    # tested-by: REQ-MAP-870, REQ-MAP-871, REQ-MAPDIAGRAMS-874
    def test_compact_preserves_graph_and_freshness(self):
        # verifies: REQ-MAP-870#CASE-6
        # verifies: REQ-MAP-871#CASE-5
        data = Rendering()._data('Unicode ș </script>')
        data['nodes'][0]['contract'] = ['Keep the entire contract.']
        pretty = R._build_json_text(data, compact=False)
        compact = R._build_json_text(data, compact=True)
        self.assertEqual(json.loads(pretty), json.loads(compact))
        self.assertLess(len(compact), len(pretty))
        self.assertEqual(R._strip_generated(pretty), R._strip_generated(compact))
        changed = json.loads(compact)
        changed['nodes'][0]['contract'] = ['Changed contract.']
        self.assertNotEqual(R._strip_generated(compact),
                            R._strip_generated(json.dumps(changed)))
        changed = json.loads(compact)
        changed['design'] = {'score': 5}
        self.assertEqual(R._strip_generated(compact),
                         R._strip_generated(json.dumps(changed)))

    def test_compact_markdown_links_to_full_content(self):
        # verifies: REQ-MAPDIAGRAMS-874#CASE-4
        with mock.patch.object(R.config, 'MAP_PROFILE', 'compact'):
            md = R._build_md_text(Rendering()._data('Title'))
        self.assertIn('_map.json', md)
        self.assertIn('_map.html', md)
        self.assertNotIn('```mermaid', md)

    def test_locale_selection_preserves_source(self):
        # tested-by: REQ-TRANSLATE-938
        # verifies: REQ-TRANSLATE-938#CASE-4
        with tempfile.TemporaryDirectory() as d:
            reqs = {'R-1': {'body': '# Title\n', 'meta': {}}}
            entry = {'hash': R.translation_hash('# Title\n', 'Title'),
                     'title': 'Titlu'}
            _write(os.path.join(d, '_i18n', 'ro.json'),
                   json.dumps({'R-1': entry}))
            with mock.patch.object(R.config, 'MAP_LOCALES', ['ro']):
                self.assertIn('ro', R._load_translations(reqs, d)['R-1'])
            with mock.patch.object(R.config, 'MAP_LOCALES', []):
                self.assertEqual(R._load_translations(reqs, d), {})
            self.assertEqual(reqs['R-1']['body'], '# Title\n')


class SharedSkillWorkflow(unittest.TestCase):
    # tested-by: REQ-CMDREGISTRY-834
    def test_both_adapters_ship_the_same_workflow_reference(self):
        # verifies: REQ-CMDREGISTRY-834#CASE-7
        from pathlib import Path
        root = Path(__file__).resolve().parents[1] / "skills" / "requirement-manager"
        target = root / "references" / "workflow.md"
        self.assertTrue(target.is_file())
        for name in ("SKILL.md", "SKILL.universal.md"):
            entry = (root / name).read_text(encoding="utf-8")
            self.assertIn("(references/workflow.md)", entry)
            self.assertIn("<!--##REQMAP:COMMANDS##-->", entry)
        for source in root.rglob("*.md"):
            text = source.read_text(encoding="utf-8")
            for link in re.findall(r"\]\(([^)]+)\)", text):
                path = link.split("#", 1)[0]
                if path and "://" not in path:
                    self.assertTrue((source.parent / path).exists(),
                                    "{} -> {}".format(source.name, path))
