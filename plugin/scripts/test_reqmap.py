"""Regression tests for the bugs found by the 2026-06-02 bug-hunt. Stdlib only.

Run: python -m unittest test_reqmap   (from plugin/scripts/)
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reqmap as R


def _write(path, text, encoding="utf-8"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=encoding) as f:
        f.write(text)


# Build tag strings at runtime so THIS test file does not register phantom
# members in the repo's own `reqmap check` (the scanner reads .py line by line).
_ROLE = "impl" + "ements"


def tag(cap):
    return "# {}: {}".format(_ROLE, cap)


REQ = "---\nid: {id}\nstatus: {status}\nlayer: {layer}\n{extra}---\n\n# {title}\n"


class Parsing(unittest.TestCase):  # tested-by: CORE-PARSE-001
    def test_bom_does_not_break_frontmatter(self):  # bug #1
        text = "﻿---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n"
        meta, _ = R.parse_frontmatter(text)
        self.assertEqual(meta.get("id"), "REQ-A-001")
        self.assertEqual(meta.get("status"), "confirmed")

    def test_bom_file_loads_with_real_id(self):  # bug #1 end-to-end
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "REQ-A-001.md"),
                   "﻿" + REQ.format(id="REQ-A-001", status="confirmed", layer="bus", extra="", title="T"))
            reqs = R.load_requirements(d)
            self.assertIn("REQ-A-001", reqs)
            self.assertEqual(reqs["REQ-A-001"]["meta"]["status"], "confirmed")

    def test_hash_inside_inline_list(self):  # bug #2
        meta, _ = R.parse_frontmatter("---\ndepends_on: [A-1, B-2 # note]\n---\n")
        self.assertEqual(meta["depends_on"], ["A-1", "B-2"])

    def test_quoted_scalar_is_unquoted(self):  # bug #14
        meta, _ = R.parse_frontmatter('---\nid: "REQ-X-001"\nstatus: \'draft\'\n---\n')
        self.assertEqual(meta["id"], "REQ-X-001")
        self.assertEqual(meta["status"], "draft")

    def test_full_line_comment_ignored(self):  # regression guard for #2 fix
        meta, _ = R.parse_frontmatter("---\n# id: COMMENTED\nid: REAL-1\n---\n")
        self.assertEqual(meta["id"], "REAL-1")

    def test_as_list_coerces_bare_scalar(self):  # bug #5
        self.assertEqual(R._as_list("X-1"), ["X-1"])
        self.assertEqual(R._as_list(["X-1"]), ["X-1"])
        self.assertEqual(R._as_list(""), [])


class Gate(unittest.TestCase):
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, False)
            return code, buf.getvalue()

    def test_bare_scalar_depends_on_no_percharacter_errors(self):  # bug #5  tested-by: REQ-CHECK-006
        files = {
            "AREA-FOO-001.md": REQ.format(id="AREA-FOO-001", status="baseline", layer="feature",
                                          extra="depends_on: AREA-BAR-002\n", title="Foo"),
            "AREA-BAR-002.md": REQ.format(id="AREA-BAR-002", status="baseline", layer="bus", extra="", title="Bar"),
        }
        code, out = self._check(files)
        self.assertNotIn("depends_on missing", out)
        self.assertEqual(code, 0)

    def test_corrupt_lock_does_not_crash(self):  # bug #6  tested-by: CORE-DRIFT-003
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_reqlock.json"), "")        # empty
            self.assertEqual(R.load_lock(d), {})
            _write(os.path.join(d, "_reqlock.json"), "{not json")  # garbage
            self.assertEqual(R.load_lock(d), {})

    def test_update_lock_missing_dir_no_crash(self):  # bug #13
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "does", "not", "exist")
            R.save_lock(missing, {"A": "b"})  # must not raise
            self.assertTrue(os.path.exists(os.path.join(missing, "_reqlock.json")))

    def test_binding_hash_tracks_contract_not_commentary(self):  # tested-by: CORE-DRIFT-003
        base = ("# T\n\n## WHAT — Contract (normative)\n- shall do X\n\n"
                "## HOW — Acceptance (= tests)\nAC-1\n  Then X holds\n")
        notes_a = base + "\n## WHAT — Notes & known limitations\n- footgun A\n"
        notes_b = base + "\n## WHAT — Verify intent\n- Observed: weird thing. Bug?\n"
        # commentary (Notes / Verify-intent) must NOT change the binding hash
        self.assertEqual(R.binding_hash(notes_a), R.binding_hash(notes_b))
        # changing the Contract MUST change it
        self.assertNotEqual(R.binding_hash(base), R.binding_hash(base.replace("shall do X", "shall do Y")))
        # changing an acceptance criterion MUST change it
        self.assertNotEqual(R.binding_hash(base), R.binding_hash(base.replace("X holds", "Y holds")))

    def test_drift_warn_names_member_locations(self):  # tested-by: REQ-CHECK-006
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-FOO-001.md"),
                   REQ.format(id="AREA-FOO-001", status="confirmed", layer="bus", extra="", title="Foo")
                   + "\n## Input\n- x\n## Output\n- y\n## Acceptance\n- z\n")
            _write(os.path.join(d, "mod.py"), tag("AREA-FOO-001") + "\n")
            _write(os.path.join(d, "_reqlock.json"), '{"AREA-FOO-001": "stalehash0000"}')  # != current
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, d, False)
            out = buf.getvalue()
            self.assertIn("DRIFT", out)
            self.assertIn("re-check 1 member", out)   # actionable count
            self.assertIn("mod.py:1", out)            # names the member location


class Scanning(unittest.TestCase):  # tested-by: CORE-SCAN-002
    def test_tag_re_left_boundary(self):  # bug #3
        self.assertEqual(R.TAG_RE.findall(tag("FOO-BAR-001")), [("implements", "FOO-BAR-001")])
        self.assertEqual(R.TAG_RE.findall("# re" + _ROLE + ": FOO-BAR-001"), [])
        self.assertEqual(R.TAG_RE.findall("auto-" + _ROLE + ": AB-CD-001"), [])

    def test_only_ssot_requirements_dir_excluded(self):  # bug #4
        with tempfile.TemporaryDirectory() as d:
            ssot = os.path.join(d, "requirements")
            _write(os.path.join(d, "src", "requirements", "mod.py"), tag("SRC-REQ-001") + "\n")
            _write(os.path.join(ssot, "ignored.py"), tag("SSOT-IGN-001") + "\n")
            members = R.scan_members(d, ssot)
            self.assertIn("SRC-REQ-001", members)       # non-SSOT requirements/ still scanned
            self.assertNotIn("SSOT-IGN-001", members)    # the real SSOT dir is skipped

    def test_duplicate_tag_on_one_line_deduped(self):  # bug #18
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), tag("FOO-BAR-001") + " " + _ROLE + ": FOO-BAR-001\n")
            members = R.scan_members(d, None)
            self.assertEqual(len(members["FOO-BAR-001"]), 1)

    def test_member_paths_are_posix(self):  # bug #17
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "sub", "dir", "m.py"), tag("FOO-BAR-001") + "\n")
            members = R.scan_members(d, None)
            self.assertEqual(members["FOO-BAR-001"][0][1], "sub/dir/m.py")

    def test_reqmapignore_excludes_listed_file(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "scripts", "reqmap.py"), tag("TOOL-X-001") + "\n")
            _write(os.path.join(d, "scripts", "app.py"), tag("APP-Y-001") + "\n")
            _write(os.path.join(d, ".reqmapignore"), "# vendored tool\nscripts/reqmap.py\n")
            members = R.scan_members(d, None)
            self.assertNotIn("TOOL-X-001", members)  # ignored
            self.assertIn("APP-Y-001", members)       # still scanned

    def test_reqmapignore_glob_pattern(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "gen", "a.py"), tag("GEN-A-001") + "\n")
            _write(os.path.join(d, ".reqmapignore"), "gen/*.py\n")
            self.assertNotIn("GEN-A-001", R.scan_members(d, None))

    def test_no_reqmapignore_scans_everything(self):  # backward compat
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), tag("FOO-BAR-001") + "\n")
            self.assertIn("FOO-BAR-001", R.scan_members(d, None))


class Rendering(unittest.TestCase):  # tested-by: REQ-MAP-007
    def _data(self, title):
        return {"nodes": [{"id": "A-1", "layer": "bus", "status": "draft", "title": title,
                           "intent": "", "input": "", "output": "", "desc": "", "acc": [],
                           "deps": [], "used_by": [], "members": []}], "edges": []}

    def _html(self, d, title):
        R.render_html(self._data(title), d)
        with open(os.path.join(d, "_map.html"), encoding="utf-8") as f:
            return f.read()

    def test_script_breakout_neutralized(self):  # bug #7
        with tempfile.TemporaryDirectory() as d:
            html = self._html(d, "Login </script><img src=x>")
            # the only </script> are the template's own (CDN tag + inline block)
            self.assertEqual(html.count("</script>"), 2)
            self.assertNotIn("</script><img", html)  # the injected breakout is gone
            self.assertIn("\\u003c", html)            # the data block escaped <

    def test_sel_has_html_escaper(self):  # bug #8
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("const esc=", self._html(d, "T"))

    def test_node_label_sanitizes_id(self):  # bug #9
        out = R._node_label({"id": "A<img>", "title": "T"})
        self.assertNotIn("<img>", out)
        self.assertIn("T", out)

    def test_map_into_missing_dir_no_crash(self):  # bug #21
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "new", "requirements")
            R.render_html(self._data("T"), missing)
            R.render_md(self._data("T"), missing)
            self.assertTrue(os.path.exists(os.path.join(missing, "_map.html")))

    def _node(self, rid, status="baseline", layer="feature", members=None):
        return {"id": rid, "layer": layer, "status": status, "title": rid,
                "intent": "", "input": "i", "output": "o", "desc": "", "acc": [],
                "deps": [], "used_by": [], "members": members or []}

    def test_req_to_code_baseline_no_members_is_grey_not_red(self):
        out = R._mermaid_req_to_code({"nodes": [self._node("AREA-FOO-001", status="baseline")], "edges": []})
        self.assertIn("#eee", out)        # muted grey: not-yet-linked baseline is expected
        self.assertNotIn("#fee", out)     # NOT the alarming red

    def test_req_to_code_confirmed_no_members_is_red(self):
        out = R._mermaid_req_to_code({"nodes": [self._node("AREA-FOO-001", status="confirmed")], "edges": []})
        self.assertIn("#fee", out)        # enforced + unlinked = a real gap -> red

    def test_system_map_boxes_multinode_area_and_collapses_singletons(self):
        data = {"nodes": [self._node("BUS-PATHS-001", layer="bus"),
                          self._node("BUS-RULES-002", layer="bus"),
                          self._node("AI-POSTMORTEM-001")], "edges": []}
        out = R._mermaid_system(data)
        self.assertIn('subgraph sg_BUS["BUS"]', out)     # multi-node area gets a box
        self.assertIn('subgraph sg_misc["misc"]', out)   # lone node collapses into misc
        self.assertIn("stroke-width:3px", out)           # bus stays marked

    def test_system_map_hides_edges_into_bus(self):
        data = {"nodes": [self._node("BUS-PATHS-001", layer="bus"),
                          self._node("BUS-RULES-002", layer="bus"),
                          self._node("ETL-PIPELINE-001"), self._node("DASH-BUILD-001")],
                "edges": [["ETL-PIPELINE-001", "BUS-PATHS-001"],     # into bus -> hidden
                          ["ETL-PIPELINE-001", "DASH-BUILD-001"]]}   # feature->feature -> kept
        out = R._mermaid_system(data)
        self.assertNotIn("--> BUS_PATHS_001", out)
        self.assertIn("--> DASH_BUILD_001", out)

    def test_system_map_area_override_via_frontmatter(self):
        a = self._node("RULESFLOW-REPORT-001"); a["area"] = "ANALYSIS"
        b = self._node("PLAYBOOK-ANALYSIS-001"); b["area"] = "ANALYSIS"
        out = R._mermaid_system({"nodes": [a, b], "edges": []})
        self.assertIn('subgraph sg_ANALYSIS["ANALYSIS"]', out)   # grouped by area:, not id prefix

    def test_render_html_and_md_carry_legends(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("bus (shared foundation)", self._html(d, "T"))
            R.render_md(self._data("T"), d)
            md = open(os.path.join(d, "_map.md"), encoding="utf-8").read()
            self.assertIn("area-level coupling", md)   # dependency-map legend line present

    def test_deps_is_area_level_overview(self):
        data = {"nodes": [self._node("BUS-PATHS-001", layer="bus"),
                          self._node("BUS-RULES-002", layer="bus"),
                          self._node("AI-X-001"), self._node("AI-Y-002")],
                "edges": [["AI-X-001", "BUS-PATHS-001"], ["AI-Y-002", "BUS-PATHS-001"]]}
        out = R._mermaid_deps(data)
        self.assertIn('a_BUS["BUS', out)                 # one node per area, with a count
        self.assertIn('a_AI["AI', out)
        self.assertEqual(out.count("a_AI --> a_BUS"), 1)  # two AI->bus edges aggregate to one
        self.assertNotIn("BUS_PATHS_001", out)           # no per-capability hub hairball

    def test_detail_panel_center_button_in_active_pane(self):
        with tempfile.TemporaryDirectory() as d:
            html = self._html(d, "T")
            self.assertIn('id="q"', html)                 # search box
            self.assertIn("class=ctr", html)              # ◎ center button in the detail panel header
            self.assertIn("function centerNode(", html)   # NOT 'focus' (shadowed by element.focus in inline onclick)
            self.assertIn("centerNode(n.id)", html)       # button wired in JS (id stays a var, not interpolated markup)
            self.assertNotIn("centerNode('${n.id}')", html)  # the unsafe inline-onclick interpolation is gone
            self.assertIn(".pane.active", html)           # centers in the CURRENT tab
            self.assertNotIn("switchTab(0)", html.split("function centerNode(")[1].split("}")[0])  # must not switch tabs

    def test_risk_grouped_no_edges_flags_baseline(self):
        data = {"nodes": [self._node("AI-X-001", status="baseline"),
                          self._node("AI-Y-002", status="baseline")],
                "edges": [["AI-X-001", "AI-Y-002"]]}
        out = R._mermaid_risk(data)
        self.assertIn("unreviewed", out)
        self.assertIn('subgraph sg_AI["AI"]', out)       # grouped by area
        self.assertNotIn("-->", out)                     # Risk shows no edges

    def test_risk_table_has_scripted_recommendation(self):
        with tempfile.TemporaryDirectory() as d:
            R.render_md({"nodes": [self._node("AI-X-001", status="baseline")], "edges": []}, d)
            md = open(os.path.join(d, "_map.md"), encoding="utf-8").read()
            self.assertIn("recommendation", md)            # new table column
            self.assertIn("promote to `confirmed`", md)    # unreviewed advice text

    def test_search_bar_in_html(self):
        with tempfile.TemporaryDirectory() as d:
            html = self._html(d, "T")
            self.assertIn('id="q"', html)
            self.assertIn("function search(", html)


class Extract(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def test_same_basename_different_dirs_no_collision(self):  # bug #10
        self.assertNotEqual(R._draft_id("src/utils.py"), R._draft_id("lib/utils.js"))
        self.assertEqual(R._draft_id("src/utils.py"), "DRAFT-SRC-UTILS")

    def test_empty_stem_fallback(self):  # bug #19
        self.assertEqual(R._draft_id("_.py"), "DRAFT-FILE")
        self.assertEqual(R._draft_id("世界.py"), "DRAFT-FILE")

    def test_extract_creates_distinct_drafts_and_makedirs(self):  # bugs #10/#11/#12
        with tempfile.TemporaryDirectory() as d:
            code = os.path.join(d, "code")
            _write(os.path.join(code, "src", "utils.py"), "x = 1\n")
            _write(os.path.join(code, "lib", "utils.js"), "var x = 1;\n")
            out = os.path.join(d, "new", "reqs")  # does not exist yet
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract({}, {}, code, out)
            made = sorted(n for n in os.listdir(out) if n.startswith("DRAFT-"))
            self.assertEqual(made, ["DRAFT-LIB-UTILS.md", "DRAFT-SRC-UTILS.md"])


class New(unittest.TestCase):  # tested-by: REQ-NEW-004
    def test_new_scaffolds_from_template_and_substitutes_id(self):
        with tempfile.TemporaryDirectory() as d:
            tmpl = os.path.join(d, "tmpl.md")
            _write(tmpl, "---\nid: AREA-NAME-NNN\n---\n\n# AREA-NAME-NNN\n")
            reqs_dir = os.path.join(d, "reqs")  # does not exist yet
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_new(reqs_dir, tmpl, "CORE-FOO-001")
            self.assertEqual(code, 0)
            dest = os.path.join(reqs_dir, "CORE-FOO-001.md")
            self.assertTrue(os.path.exists(dest))
            with open(dest, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("CORE-FOO-001", content)
            self.assertNotIn("AREA-NAME-NNN", content)

    def test_new_uses_builtin_template_when_no_file(self):
        with tempfile.TemporaryDirectory() as d:
            reqs_dir = os.path.join(d, "reqs")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_new(reqs_dir, None, "CORE-FOO-001")   # no on-disk template
            self.assertEqual(code, 0)
            content = open(os.path.join(reqs_dir, "CORE-FOO-001.md"), encoding="utf-8").read()
            self.assertIn("CORE-FOO-001", content)
            self.assertNotIn("AREA-NAME-NNN", content)
            self.assertIn("## WHAT — Contract", content)        # new emission schema
            self.assertIn("Acceptance (= tests)", content)      # from the built-in scaffold

    def test_new_refuses_to_overwrite_existing(self):
        with tempfile.TemporaryDirectory() as d:
            tmpl = os.path.join(d, "tmpl.md")
            _write(tmpl, "# AREA-NAME-NNN\n")
            reqs_dir = os.path.join(d, "reqs")
            _write(os.path.join(reqs_dir, "CORE-FOO-001.md"), "existing\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_new(reqs_dir, tmpl, "CORE-FOO-001")
            self.assertEqual(code, 1)
            with open(os.path.join(reqs_dir, "CORE-FOO-001.md"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "existing\n")  # untouched


class Scan(unittest.TestCase):  # tested-by: REQ-SCAN-005
    def test_scan_lists_members_and_flags_empty(self):
        reqs = {"CORE-FOO-001": {}, "CORE-BAR-002": {}}
        members = {"CORE-FOO-001": [("implements", "src/foo.py", 12)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_scan(reqs, members)
        out = buf.getvalue()
        self.assertIn("CORE-FOO-001", out)
        self.assertIn("implements", out)
        self.assertIn("src/foo.py:12", out)
        self.assertIn("(no members found)", out)  # CORE-BAR-002 has none


class Candidates(unittest.TestCase):  # tested-by: REQ-CANDIDATES-009
    def _plan(self, d):
        reqs_dir = os.path.join(d, "requirements")
        reqs = R.load_requirements(reqs_dir)
        members = R.scan_members(d, reqs_dir)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(reqs, members, d, reqs_dir, None)
        return json.loads(buf.getvalue())

    def test_writes_no_md_and_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), '"""mod a."""\ndef f(x):\n    return x\n')
            plan = self._plan(d)
            self.assertIn("candidates", plan)
            self.assertEqual([n for n in os.listdir(d) if n.endswith(".md")], [])

    def test_respects_reqmapignore(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "keep.py"), "x = 1\n")
            _write(os.path.join(d, "skip.py"), "y = 2\n")
            _write(os.path.join(d, ".reqmapignore"), "skip.py\n")
            allfiles = [f for c in self._plan(d)["candidates"] for f in c["files"]]
            self.assertIn("keep.py", allfiles)
            self.assertNotIn("skip.py", allfiles)

    def test_derives_depends_on_from_imports(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "paths.py"), "ROOT = '.'\n")
            _write(os.path.join(d, "app.py"), "import paths\n")
            cands = self._plan(d)["candidates"]
            app = next(c for c in cands if "app.py" in c["files"])
            paths = next(c for c in cands if "paths.py" in c["files"])
            self.assertIn(paths["suggested_id"], app["depends_on"])

    def test_capmap_groups_files(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), "x=1\n")
            _write(os.path.join(d, "b.py"), "y=2\n")
            _write(os.path.join(d, "requirements", "_capmap.json"),
                   json.dumps({"capabilities": [
                       {"id": "CORE-AB-001", "layer": "bus", "files": ["a.py", "b.py"]}]}))
            ab = [c for c in self._plan(d)["candidates"] if c["suggested_id"] == "CORE-AB-001"]
            self.assertEqual(len(ab), 1)
            self.assertEqual(sorted(ab[0]["files"]), ["a.py", "b.py"])
            self.assertEqual(ab[0]["suggested_layer"], "bus")

    def test_existing_req_for_tagged_file(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), tag("CORE-FOO-001") + "\n")
            m = next(c for c in self._plan(d)["candidates"] if "m.py" in c["files"])
            self.assertEqual(m["existing_req"], "CORE-FOO-001")

    def test_unparseable_python_does_not_abort(self):  # one bad file != crash
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "bad.py"), "def (:\n")     # SyntaxError
            _write(os.path.join(d, "good.py"), "z = 1\n")
            files = [f for c in self._plan(d)["candidates"] for f in c["files"]]
            self.assertIn("good.py", files)
            self.assertIn("bad.py", files)


def _req_with_verify(rid, items, title="Cap"):
    """A new-schema requirement whose Verify-intent section holds `items`."""
    vi = "\n".join("- " + it for it in items)
    return (
        "---\nid: {id}\nstatus: baseline\nlayer: feature\n---\n\n# {t}\n\n"
        "## WHAT — Contract (normative)\n- shall do the thing.\n\n"
        "## WHAT — Verify intent (open questions for the human)\n{vi}\n\n"
        "## HOW — Acceptance (= tests)\nAC-1\n"
    ).format(id=rid, t=title, vi=vi)


class Findings(unittest.TestCase):  # tested-by: REQ-FINDINGS-010
    def _run(self, d, raw=False):
        reqs = R.load_requirements(os.path.join(d, "requirements"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_findings(reqs, os.path.join(d, "requirements"), raw=raw)
        md = open(os.path.join(d, "requirements", "_findings.md"), encoding="utf-8").read()
        return md, buf.getvalue()

    def test_aggregates_verify_intent_grouped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["swallowed except, intended?", "magic 1.05, bug?"]))
            md, out = self._run(d)
            self.assertIn("AREA-X-001", md)
            self.assertIn("magic 1.05", md)
            self.assertIn("2 open finding(s) across 1 requirement(s)", out)

    def test_skips_none_placeholder(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-Y-001.md"),
                   _req_with_verify("AREA-Y-001", ["None — behavior is unambiguous and matches the contract."]))
            md, out = self._run(d)
            self.assertIn("0 open finding(s)", out)
            self.assertIn("_No open findings._", md)

    def test_triage_sidecar_orders_confirmed_bugs_first(self):
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

    def test_raw_flag_ignores_sidecar(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["magic 1.05, bug?"]))
            _write(os.path.join(d, "requirements", R.FINDINGS_SIDECAR), json.dumps({
                "items": [{"req_id": "AREA-X-001", "finding": "magic 1.05", "classification": "REAL_BUG", "severity": "high"}]}))
            md, _ = self._run(d, raw=True)
            self.assertNotIn("Confirmed bugs", md)
            self.assertIn("Open findings", md)

    def test_staleness_note_when_counts_differ(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["a?", "b?", "c?"]))  # 3 raw
            _write(os.path.join(d, "requirements", R.FINDINGS_SIDECAR), json.dumps({
                "items": [{"req_id": "AREA-X-001", "finding": "a", "classification": "INTENTIONAL"}]}))  # 1 triaged
            md, _ = self._run(d)
            self.assertIn("WARN", md)
            self.assertIn("re-run the AI triage", md)

    def test_check_reports_open_findings(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["magic 1.05, bug?"]))
            reqs = R.load_requirements(os.path.join(d, "requirements"))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, {}, os.path.join(d, "requirements"), False)
            self.assertIn("1 open verify-intent finding(s)", buf.getvalue())


# ---- regression tests for the 2026-06-02 audit fixes + previously-untested code ----

def _map_html_for(node):
    """render_html for a single node dict (defaults filled), return the HTML."""
    base = {"id": "A-1", "layer": "feature", "status": "draft", "title": "t", "intent": "",
            "input": "", "output": "", "desc": "", "acc": [], "deps": [], "used_by": [],
            "members": []}
    base.update(node)
    with tempfile.TemporaryDirectory() as d:
        R.render_html({"nodes": [base], "edges": []}, d)
        return open(os.path.join(d, "_map.html"), encoding="utf-8").read()


class Security(unittest.TestCase):  # tested-by: REQ-MAP-007
    def test_js_str_escapes_angle_brackets_and_amp(self):
        self.assertEqual(R._js_str("a<b>&"), '"a\\u003cb\\u003e\\u0026"')

    def test_id_with_quote_does_not_break_out_of_callback(self):  # bug: id-js-string-breakout-xss
        html = _map_html_for({"id": "x');};alert(1);y=function(){sel('"})
        self.assertNotIn("sel('x');};alert(1)", html)   # NOT executable: no raw breakout
        self.assertIn('sel("x', html)                    # id passed as a JSON string arg

    def test_id_with_script_close_is_escaped(self):  # bug: id-js-string-breakout-xss
        html = _map_html_for({"id": "a</script><img src=x>"})
        self.assertEqual(html.count("</script>"), 2)     # only the template's own two
        self.assertIn("\\u003c", html)                   # the id's < was escaped

    def test_search_results_use_data_id_not_inline_onclick(self):
        html = _map_html_for({"id": "A-1"})
        self.assertNotIn("onclick=\"pick(", html)        # no raw-id inline onclick
        self.assertIn("data-id=", html)                  # delegated off a data attribute


class JsFacts(unittest.TestCase):  # tested-by: REQ-CANDIDATES-009
    def test_extracts_module_doc_and_top_level_names(self):  # bug: js-facts-untested
        f = R._js_facts("/* Module doc.\n * more */\nexport function foo(){}\nconst bar = 1;\n")
        self.assertEqual(f["docstrings"].get("module"), "Module doc.")
        self.assertIn("foo", f["signatures"])
        self.assertIn("bar", f["signatures"])

    def test_leading_comment_scan_is_linear_on_star_run(self):  # bug: js-doc-comment-redos
        import time
        src = "/*" + "*" * 400000          # unterminated star run that DoS'd the old regex
        t = time.time(); R._js_facts(src)
        self.assertLess(time.time() - t, 2.0)   # str.find is linear; was minutes before


class Staleness(unittest.TestCase):  # tested-by: REQ-CHECK-006
    def test_engine_version_at_reads_and_missing(self):  # bug: warn-if-stale-untested
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "reqmap.py")
            _write(p, 'X = 1\nMAP_ENGINE_VERSION = "2099-12-31"\n')
            self.assertEqual(R._engine_version_at(p), "2099-12-31")
            self.assertIsNone(R._engine_version_at(os.path.join(d, "nope.py")))

    def test_warn_if_stale_fires_only_when_plugin_newer(self):  # bug: warn-if-stale-untested
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "scripts", "reqmap.py"),
                   'MAP_ENGINE_VERSION = "2099-12-31"\n')
            old = os.environ.get("CLAUDE_PLUGIN_ROOT")
            try:
                os.environ["CLAUDE_PLUGIN_ROOT"] = d
                buf = io.StringIO()
                with redirect_stdout(buf):
                    R.warn_if_stale()
                self.assertIn("stale", buf.getvalue())
                os.environ.pop("CLAUDE_PLUGIN_ROOT")          # no env -> silent
                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    R.warn_if_stale()
                self.assertEqual(buf2.getvalue(), "")
            finally:
                if old is not None:
                    os.environ["CLAUDE_PLUGIN_ROOT"] = old
                else:
                    os.environ.pop("CLAUDE_PLUGIN_ROOT", None)


class GateErrors(unittest.TestCase):  # tested-by: REQ-CHECK-006
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, False)
            return code, buf.getvalue()

    def test_invalid_status_errors_and_exits_nonzero(self):  # bug: gate-never-asserted-to-fail
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="bogus", layer="feature", extra="", title="T")})
        self.assertIn("invalid status", out)
        self.assertEqual(code, 1)

    def test_invalid_layer_errors(self):
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="bogus", extra="", title="T")})
        self.assertIn("invalid layer", out)
        self.assertEqual(code, 1)

    def test_depends_on_missing_errors(self):
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="feature",
            extra="depends_on: [GHOST-X-999]\n", title="T")})
        self.assertIn("depends_on missing GHOST-X-999", out)
        self.assertEqual(code, 1)

    def test_dangling_tag_errors(self):
        code, out = self._check({"mod.py": tag("GHOST-CAP-001") + "\n"})
        self.assertIn("dangling tag", out)
        self.assertEqual(code, 1)

    def test_confirmed_without_implements_errors(self):
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="confirmed", layer="bus", extra="", title="T")})
        self.assertIn("no implements", out)
        self.assertEqual(code, 1)

    def test_corrupt_lock_warns_in_check(self):  # bug: corrupt-lock-disables-drift-silently
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   REQ.format(id="A-FOO-001", status="baseline", layer="bus", extra="", title="T"))
            _write(os.path.join(d, "_reqlock.json"), "{ not json")
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, R.scan_members(d, d), d, False)
            self.assertIn("unreadable", buf.getvalue())
            self.assertEqual(code, 0)   # corrupt lock is a WARN, never a hard error


class ParserBlockLists(unittest.TestCase):  # tested-by: CORE-PARSE-001
    def test_block_style_list_is_parsed(self):  # bug: block-style-yaml-list-silently-empty
        meta, _ = R.parse_frontmatter("---\nowner: a\ndepends_on:\n  - A-1\n  - B-2\n---\nbody")
        self.assertEqual(meta["depends_on"], ["A-1", "B-2"])

    def test_unclosed_inline_list_is_lenient(self):  # bug: unclosed-inline-list-literal-string
        meta, _ = R.parse_frontmatter("---\ndepends_on: [A-1, B-2\n---\nbody")
        self.assertEqual(meta["depends_on"], ["A-1", "B-2"])

    def test_empty_scalar_after_key_stays_empty(self):  # no regression on unset superseded_by
        meta, _ = R.parse_frontmatter("---\nsuperseded_by:\nid: X-1\n---\nbody")
        self.assertEqual(meta["superseded_by"], "")
        self.assertEqual(meta["id"], "X-1")


class MapInternals(unittest.TestCase):  # tested-by: REQ-MAP-007
    def _node(self, members):
        return {"id": "A-FOO-001", "layer": "feature", "status": "confirmed", "title": "T",
                "members": members}

    def test_req_to_code_collapses_line_range(self):  # bug: mermaid-req-to-code-line-range-untested
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


class CapmapMalformed(unittest.TestCase):  # tested-by: REQ-CANDIDATES-009
    def test_corrupt_json_returns_empty(self):  # bug: load-capmap-malformed-untested
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_capmap.json"), "{ not json")
            self.assertEqual(R._load_capmap(d), [])

    def test_bare_list_shape_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_capmap.json"),
                   json.dumps([{"id": "CORE-AB-001", "files": ["a.py", "b.py"]}]))
            out = R._load_capmap(d)
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0]["id"], "CORE-AB-001")

    def test_entry_missing_files_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_capmap.json"),
                   json.dumps({"capabilities": [{"id": "X-1"}, {"id": "Y-2", "files": ["a.py"]}]}))
            out = R._load_capmap(d)
            self.assertEqual([c["id"] for c in out], ["Y-2"])  # X-1 (no files) dropped


class CandidatesGrouping(unittest.TestCase):  # tested-by: REQ-CANDIDATES-009
    def _plan(self, d):
        reqs_dir = os.path.join(d, "requirements")
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(R.load_requirements(reqs_dir), R.scan_members(d, reqs_dir),
                             d, reqs_dir, None)
        return json.loads(buf.getvalue())

    def test_high_fanin_module_inferred_bus(self):  # bug: candidates-bus-threshold-untested
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "paths.py"), "ROOT = '.'\n")
            for i in range(R.BUS_FANIN_THRESHOLD):
                _write(os.path.join(d, "imp%d.py" % i), "import paths\n")
            plan = self._plan(d)
            paths = next(c for c in plan["candidates"] if "paths.py" in c["files"])
            self.assertGreaterEqual(paths["importer_count"], R.BUS_FANIN_THRESHOLD)
            self.assertEqual(paths["suggested_layer"], "bus")
            self.assertIn(paths["suggested_id"], plan["bus"])

    def test_candidates_honors_reqmapignore_in_requirements_dir(self):  # bug: collect-files-ignores-reqsdir-reqmapignore
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "keep.py"), "x = 1\n")
            _write(os.path.join(d, "skip.py"), "y = 2\n")
            # .reqmapignore lives in requirements/ (the documented home), not the scan root
            _write(os.path.join(d, "requirements", ".reqmapignore"), "skip.py\n")
            files = [f for c in self._plan(d)["candidates"] for f in c["files"]]
            self.assertIn("keep.py", files)
            self.assertNotIn("skip.py", files)   # candidates now matches scan/check


class TriageFolding(unittest.TestCase):  # tested-by: REQ-FINDINGS-010
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


class MdDiscovery(unittest.TestCase):  # tested-by: REQ-CANDIDATES-009
    def _plan(self, d, md_globs=None):
        reqs_dir = os.path.join(d, "requirements")
        reqs = R.load_requirements(reqs_dir)
        members = R.scan_members(d, reqs_dir)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(reqs, members, d, reqs_dir, None, md_globs)
        return json.loads(buf.getvalue())

    def test_md_facts_extracts_title_intent_h2(self):
        src = "# Generator\n\n> the proposing voice.\n\n## Role\ntext\n## Output\nmore\n"
        f = R._md_facts(src)
        self.assertEqual(f["docstrings"]["title"], "Generator")
        self.assertEqual(f["docstrings"]["module"], "the proposing voice.")
        self.assertEqual(f["signatures"], ["## Role", "## Output"])

    def test_md_excluded_without_glob(self):  # default: no .md ever collected
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), "x = 1\n")
            _write(os.path.join(d, "prompts", "voice.md"), "# Voice\n\n> a voice.\n")
            files = [f for c in self._plan(d)["candidates"] for f in c["files"]]
            self.assertNotIn("prompts/voice.md", files)

    def test_md_included_only_when_glob_matches(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "prompts", "voice.md"), "# Voice\n\n> a voice.\n")
            _write(os.path.join(d, "docs", "readme.md"), "# Docs\n")  # not in allowlist
            files = [f for c in self._plan(d, ["prompts/**"])["candidates"] for f in c["files"]]
            self.assertIn("prompts/voice.md", files)
            self.assertNotIn("docs/readme.md", files)   # allowlist bounds scope

    def test_plan_has_coverage_summary_and_lineage_note(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), "x = 1\n")
            plan = self._plan(d)
            self.assertEqual(plan["coverage_summary"]["total_candidates"], len(plan["candidates"]))
            self.assertIn("with_existing_req", plan["coverage_summary"])
            self.assertIn("lineage", plan["lineage_note"].lower())

    def test_tag_in_md_is_scanned_as_member(self):  # .md now in CODE_EXTS
        with tempfile.TemporaryDirectory() as d:
            md_tag = "<!-- {}: CONSILIUM-VOICE-001 -->".format(_ROLE)
            _write(os.path.join(d, "prompts", "generator.md"), "# Generator\n" + md_tag + "\n")
            members = R.scan_members(d, os.path.join(d, "requirements"))
            self.assertIn("CONSILIUM-VOICE-001", members)
            roles = [m[0] for m in members["CONSILIUM-VOICE-001"]]
            self.assertIn("implements", roles)


class HealthLine(unittest.TestCase):  # tested-by: REQ-CHECK-006
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, False)
            return code, buf.getvalue()

    def test_summary_reports_confirmed_count(self):
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
        # a legacy-schema requirement (no Verify-intent section) must warn but not error
        legacy = REQ.format(id="AREA-L-001", status="baseline", layer="feature",
                            extra="", title="Legacy") + "\n## Input\n- x\n## Output\n- y\n"
        code, out = self._check({"AREA-L-001.md": legacy})
        self.assertIn("legacy schema", out)
        self.assertIn("findings` is inactive", out)
        self.assertIn("1 legacy-schema", out)
        self.assertEqual(code, 0)   # non-blocking


if __name__ == "__main__":
    unittest.main(verbosity=2)
