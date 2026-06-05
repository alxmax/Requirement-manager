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


def gtag_html(cap):  # runtime-built so THIS .py source registers no phantom member
    return "<!-- {}-from: {} -->".format("generated", cap)


_TB_ROLE = "tested" + "-by"


def tb_tag(cap):
    return "# {}: {}".format(_TB_ROLE, cap)



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

    def test_confirmed_missing_contract_section_warns(self):  # tested-by: REQ-CHECK-006
        files = {
            "AREA-FOO-001.md": (
                "---\nid: AREA-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n"
                "# Foo\n\n"
                "## HOW — Acceptance (= tests)\n- Given X When Y Then Z\n"
            ),
            "src.py": tag("AREA-FOO-001") + "\n" + tb_tag("AREA-FOO-001") + "\n",
        }
        code, out = self._check(files)
        self.assertIn("missing '## WHAT — Contract'", out)
        self.assertEqual(code, 0)  # WARN, not error

    def test_confirmed_missing_acceptance_section_warns(self):  # tested-by: REQ-CHECK-006
        files = {
            "AREA-FOO-001.md": (
                "---\nid: AREA-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n"
                "# Foo\n\n"
                "## WHAT — Contract (normative)\n- It shall do X\n"
            ),
            "src.py": tag("AREA-FOO-001") + "\n" + tb_tag("AREA-FOO-001") + "\n",
        }
        code, out = self._check(files)
        self.assertIn("missing '## HOW — Acceptance'", out)
        self.assertEqual(code, 0)  # WARN, not error

    def test_confirmed_with_both_sections_no_section_lint_warn(self):  # tested-by: REQ-CHECK-006
        files = {
            "AREA-FOO-001.md": (
                "---\nid: AREA-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n"
                "# Foo\n\n"
                "## WHAT — Contract (normative)\n- It shall do X\n\n"
                "## HOW — Acceptance (= tests)\n- Given X When Y Then Z\n"
            ),
            "src.py": tag("AREA-FOO-001") + "\n" + tb_tag("AREA-FOO-001") + "\n",
        }
        code, out = self._check(files)
        self.assertNotIn("missing '## WHAT — Contract'", out)
        self.assertNotIn("missing '## HOW — Acceptance'", out)


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


class ProseClassification(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def test_meta_files_are_ignored(self):
        for rel in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", "CONTRIBUTING.md",
                    "SKILL.md", "TODO.md", "CHANGELOG.md", "LICENSE", "LICENSE.md",
                    "_map.md", "_findings.md", "_map.html"):
            self.assertEqual(R.classify_prose(rel), "ignore", rel)

    def test_readme_and_docs_and_html_are_sync_only(self):
        for rel in ("README", "README.md", "docs/senate.md",
                    "docs/sub/guide.md", "docs/architecture.html", "x.html"):
            self.assertEqual(R.classify_prose(rel), "sync_only", rel)

    def test_prompts_and_specs_are_capability(self):
        for rel in ("prompts/senators/aurelius.md", "specs/foo.md",
                    "modes/bar.md", "notes.md"):
            self.assertEqual(R.classify_prose(rel), "capability", rel)


class ProseFacts(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def test_markdown_frontmatter_title_and_headings(self):
        src = ("---\ntitle: Senator Aurelius\n---\n\n"
               "## Role\nrisk lens\n## Specialty\nreversibility\n### sub\n")
        title, heads = R._prose_facts(src)
        self.assertEqual(title, "Senator Aurelius")
        self.assertEqual(heads, ["Role", "Specialty"])  # H2 only, not H3

    def test_markdown_h1_title_when_no_frontmatter(self):
        title, heads = R._prose_facts("# My Cap\n\n## A\n## B\n")
        self.assertEqual(title, "My Cap")
        self.assertEqual(heads, ["A", "B"])

    def test_html_title_and_h2(self):
        src = "<title>Project Map</title><h2>Section One</h2><h2>Two</h2>"
        title, heads = R._prose_facts(src)
        self.assertEqual(title, "Project Map")
        self.assertEqual(heads, ["Section One", "Two"])

    def test_no_title_returns_none(self):
        title, heads = R._prose_facts("just text, no headings\n")
        self.assertIsNone(title)
        self.assertEqual(heads, [])


class Rendering(unittest.TestCase):  # tested-by: REQ-MAP-007
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

    def test_render_md_carries_legends(self):
        with tempfile.TemporaryDirectory() as d:
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


class ProseExtract(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def _extract(self, d):
        reqs = R.load_requirements(os.path.join(d, "requirements"))
        members = R.scan_members(d, os.path.join(d, "requirements"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_extract(reqs, members, d, os.path.join(d, "requirements"))
        return os.path.join(d, "requirements")

    def test_capability_prose_is_drafted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "prompts", "aurelius.md"),
                   "---\ntitle: Aurelius\n---\n## Role\nx\n")
            rdir = self._extract(d)
            drafts = [f for f in os.listdir(rdir) if f.endswith(".md")]
            self.assertTrue(any("PROMPTS-AURELIUS" in f for f in drafts), drafts)

    def test_sync_only_and_meta_prose_not_drafted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "README.md"), "# Project\n## Overview\n")
            _write(os.path.join(d, "docs", "guide.md"), "# Guide\n## How\n")
            _write(os.path.join(d, "report.html"), "<title>R</title><h2>S</h2>")
            _write(os.path.join(d, "CLAUDE.md"), "# Claude\n## Rules\n")
            rdir = self._extract(d)
            drafts = [f for f in os.listdir(rdir) if f.endswith(".md")]
            for bad in ("README", "GUIDE", "REPORT", "CLAUDE"):
                self.assertFalse(any(bad in f for f in drafts), (bad, drafts))

    def test_explicitly_tagged_prose_not_redrafted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "README.md"),
                   "# P\n" + gtag_html("SENATE-SYNTH-001") + "\n")
            members = R.scan_members(d, None)
            self.assertIn("SENATE-SYNTH-001", members)   # rider #1 guard
            rdir = self._extract(d)
            drafts = [f for f in os.listdir(rdir) if f.endswith(".md")]
            self.assertFalse(any("README" in f for f in drafts), drafts)

    def test_tagged_capability_prose_not_redrafted(self):
        with tempfile.TemporaryDirectory() as d:
            # a prompts/ file (bucket 3) that already carries a member tag must be
            # skipped by the `rel in tagged` guard, not re-drafted
            _write(os.path.join(d, "prompts", "foo.md"),
                   "# Foo\n" + tag("PROMPTS-FOO-001") + "\n## Role\n")
            members = R.scan_members(d, os.path.join(d, "requirements"))
            self.assertIn("PROMPTS-FOO-001", members)   # it IS a member
            rdir = self._extract(d)
            drafts = [f for f in os.listdir(rdir) if f.endswith(".md")]
            self.assertFalse(any("FOO" in f for f in drafts), drafts)


class RiderGuards(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def test_tag_inside_html_comment_is_a_member(self):  # rider #1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"),
                   gtag_html("SENATE-SYNTH-001") + "\n<h1>x</h1>\n")
            members = R.scan_members(d, None)
            self.assertIn("SENATE-SYNTH-001", members)
            roles = [r for (r, _f, _l) in members["SENATE-SYNTH-001"]]
            self.assertIn("generated-from", roles)

    def test_draft_status_is_not_enforced(self):  # rider #3
        self.assertNotIn("draft", R.ENFORCED)
        self.assertEqual(R.ENFORCED, {"in-progress", "implemented", "confirmed"})


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

    def test_extract_honors_reqmapignore(self):  # init surfaced: extract ignored .reqmapignore
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "keep.py"), "x = 1\n")
            _write(os.path.join(d, "scripts", "reqmap.py"), "y = 2\n")
            _write(os.path.join(d, ".reqmapignore"), "scripts/reqmap.py\n")
            reqs_dir = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract({}, {}, d, reqs_dir)
            made = sorted(n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-"))
            self.assertEqual(made, ["DRAFT-KEEP.md"])   # the vendored engine is not drafted


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

def _export_doc_for(node):
    """Serialize a single node dict (defaults filled) via _build_json_text, parse back."""
    base = {"id": "A-1", "layer": "feature", "status": "draft", "title": "t", "intent": "",
            "input": "", "output": "", "desc": "", "acc": [], "deps": [], "used_by": [],
            "members": [], "contract": [], "verify": [], "notes": [], "current_impl": [],
            "accept": "", "risks": []}
    base.update(node)
    return json.loads(R._build_json_text({"nodes": [base], "edges": []}))


class JsonExport(unittest.TestCase):  # tested-by: REQ-MAP-007
    def test_export_writes_nodes_edges_and_version(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_export(R.load_requirements(rd), {}, rd)
            doc = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
            self.assertEqual(doc["engine_version"], R.MAP_ENGINE_VERSION)
            self.assertEqual(len(doc["nodes"]), 1)
            self.assertIn("edges", doc)

    def test_hostile_title_roundtrips_as_data_not_injection(self):  # bug: id-js-string-breakout-xss
        doc = _export_doc_for({"id": "a</script><img src=x>", "title": "x\");alert(1)//"})
        # the value survives intact as a JSON string — there is no markup context to break out of
        self.assertEqual(doc["nodes"][0]["id"], "a</script><img src=x>")
        self.assertEqual(doc["nodes"][0]["title"], "x\");alert(1)//")

    def test_node_with_no_members_has_empty_list(self):
        self.assertEqual(_export_doc_for({"id": "A-1"})["nodes"][0]["members"], [])

    def test_json_carries_repo_field(self):  # dynamic repo name in viewer header
        doc = json.loads(R._build_json_text(
            {"repo": "owner/proj", "nodes": [], "edges": []}))
        self.assertEqual(doc["repo"], "owner/proj")

    def test_json_repo_is_null_when_absent(self):
        # _build_json_text reads data.get("repo") — a graph without it stays valid (repo: null)
        doc = json.loads(R._build_json_text({"nodes": [], "edges": []}))
        self.assertIsNone(doc["repo"])


class RepoName(unittest.TestCase):  # tested-by: REQ-MAP-007
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


class ViewerInject(unittest.TestCase):  # tested-by: REQ-MAP-007
    def test_marker_replaced_with_inline_data(self):
        out = R._inject_viewer("<head><!--REQMAP_DATA--></head>",
                               {"nodes": [{"id": "A-1"}], "edges": []})
        self.assertNotIn("<!--REQMAP_DATA-->", out)   # marker consumed
        self.assertIn("window.__REQMAP_DATA__=", out) # data assigned
        self.assertIn('"A-1"', out)                   # node present

    def test_script_close_in_field_is_escaped(self):  # bug: viewer-data-script-breakout-xss
        out = R._inject_viewer("<!--REQMAP_DATA-->",
                               {"nodes": [{"id": "a</script><img src=x>"}], "edges": []})
        self.assertNotIn("</script><img", out)        # NOT a raw breakout
        self.assertIn("<\\/script>", out)             # escaped form instead

    def test_render_html_writes_self_contained_file(self):
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


class DocsPublish(unittest.TestCase):  # tested-by: REQ-MAP-007
    def test_docs_publish_path_nojekyll_signal(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", ".nojekyll"), "")
            self.assertEqual(R._docs_publish_path(d), os.path.join(d, "docs", "map.html"))

    def test_docs_publish_path_index_html_signal(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "index.html"), "<html></html>")
            self.assertEqual(R._docs_publish_path(d), os.path.join(d, "docs", "map.html"))

    def test_docs_publish_path_no_signal(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            self.assertIsNone(R._docs_publish_path(d))

    def test_docs_publish_path_no_docs_dir(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R._docs_publish_path(d))


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


class RiskSignals(unittest.TestCase):  # tested-by: REQ-MAP-007
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
                R.cmd_map(reqs, members, rd)
            md = open(os.path.join(rd, "_map.md"), encoding="utf-8").read()
            self.assertIn("untested", md)
            self.assertIn("unverified-intent", md)


class MapFreshness(unittest.TestCase):  # tested-by: REQ-MAP-007
    def _map(self, d, check=False):
        rd = os.path.join(d, "requirements")
        reqs = R.load_requirements(rd)
        members = R.scan_members(d, rd)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_map(reqs, members, rd, d, check)
        return code, buf.getvalue()

    def _seed(self, d, title="A"):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "AREA-A-001.md"),
               REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title=title))

    def test_absent_map_is_not_stale(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            code, out = self._map(d, check=True)   # never generated
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)

    def test_fresh_map_passes_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            self._map(d)                            # generate
            code, _ = self._map(d, check=True)      # immediately check
            self.assertEqual(code, 0)

    def test_stale_map_fails_check(self):
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


class Promote(unittest.TestCase):  # tested-by: REQ-PROMOTE-011
    def _run(self, d, cap_id):
        reqs = R.load_requirements(d)
        members = R.scan_members(d, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_promote(reqs, members, cap_id)
        return code, buf.getvalue()

    def test_promotes_baseline_with_implements(self):  # AC-1
        with tempfile.TemporaryDirectory() as d:
            body = REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A") + "\nbody line\n"
            _write(os.path.join(d, "AREA-A-001.md"), body)
            _write(os.path.join(d, "a.py"), tag("AREA-A-001") + "\n")
            code, out = self._run(d, "AREA-A-001")
            self.assertEqual(code, 0)
            after = open(os.path.join(d, "AREA-A-001.md"), encoding="utf-8").read()
            self.assertIn("status: confirmed", after)
            self.assertNotIn("status: baseline", after)
            self.assertIn("body line", after)            # body preserved

    def test_refuses_without_implements(self):  # AC-2
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "AREA-B-001.md")
            _write(p, REQ.format(id="AREA-B-001", status="baseline", layer="bus", extra="", title="B"))
            before = open(p, encoding="utf-8").read()
            code, out = self._run(d, "AREA-B-001")
            self.assertNotEqual(code, 0)
            self.assertEqual(open(p, encoding="utf-8").read(), before)   # unchanged
            self.assertIn("must point to code", out)

    def test_idempotent_when_confirmed(self):  # AC-3
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "AREA-C-001.md")
            _write(p, REQ.format(id="AREA-C-001", status="confirmed", layer="bus", extra="", title="C"))
            _write(os.path.join(d, "c.py"), tag("AREA-C-001") + "\n")
            before = open(p, encoding="utf-8").read()
            code, out = self._run(d, "AREA-C-001")
            self.assertEqual(code, 0)
            self.assertEqual(open(p, encoding="utf-8").read(), before)
            self.assertIn("already confirmed", out)

    def test_unknown_id_errors(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = self._run(d, "NOPE-X-001")
            self.assertNotEqual(code, 0)

    def test_preserves_trailing_comment(self):  # AC-4
        new_text, n = R._set_frontmatter_status(
            "---\nid: X-1\nstatus: baseline   # was draft\nlayer: bus\n---\n\nbody\n", "confirmed")
        self.assertEqual(n, 1)
        self.assertIn("status: confirmed   # was draft", new_text)
        self.assertIn("\nbody\n", new_text)

    def test_no_frontmatter_is_noop(self):
        new_text, n = R._set_frontmatter_status("no frontmatter here", "confirmed")
        self.assertEqual(n, 0)
        self.assertEqual(new_text, "no frontmatter here")


class Next(unittest.TestCase):  # tested-by: REQ-NEXT-013
    def _next(self, reqs, members, show_all=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_next(reqs, members, show_all)
        return code, buf.getvalue()

    def _req(self, status, extra="", body="# T\n"):
        return {"meta": {"status": status, **dict(_kv(extra))}, "body": body}

    def test_progress_header_present(self):
        reqs = {"CORE-FOO-001": self._req("confirmed"), "REQ-BAR-002": self._req("draft")}
        members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._next(reqs, members)
        self.assertIn("2 requirement(s)", out)
        self.assertIn("1 confirmed", out)
        self.assertIn("1 tested", out)
        self.assertIn("1 draft(s)", out)

    def test_untested_confirmed_lands_in_needs_tests(self):
        reqs = {"CORE-FOO-001": self._req("confirmed")}
        members = {"CORE-FOO-001": [("implements", "src/foo.py", 1)]}  # no tested-by
        code, out = self._next(reqs, members)
        self.assertEqual(code, 0)
        self.assertIn("Needs tests", out)
        self.assertIn("requirements/CORE-FOO-001.md", out)   # names the file to open

    def test_draft_lands_in_drafts_to_review(self):
        reqs = {"REQ-BAR-002": self._req("draft")}
        _, out = self._next(reqs, {})
        self.assertIn("Drafts to review", out)
        self.assertIn("REQ-BAR-002", out)

    def test_draft_intent_deduped_not_in_intent_bucket(self):
        # a draft with an open verify bullet must NOT appear under intent review:
        # the source dedup folds it into 'unreviewed' (one bucket, honest count)
        body = "# T\n\n## WHAT — Verify intent\n- is this magic constant a bug?\n"
        reqs = {"REQ-BAR-002": self._req("draft", body=body)}
        _, out = self._next(reqs, {})
        self.assertIn("Drafts to review", out)
        self.assertNotIn("Needs intent review", out)

    def test_open_verify_intent_lands_in_needs_intent_review(self):
        body = "# T\n\n## WHAT — Verify intent\n- is this magic constant a bug?\n"
        reqs = {"CORE-FOO-001": self._req("confirmed", body=body)}
        members = {"CORE-FOO-001": [("implements", "src/foo.py", 1),
                                    ("tested-by", "t.py", 2)]}  # tested, so only intent fires
        _, out = self._next(reqs, members)
        self.assertIn("Needs intent review", out)

    def test_review_flagged_drafts_ordered_first(self):
        reqs = {"DRAFT-A-001": self._req("draft", "risk: 0"),
                "DRAFT-B-002": self._req("draft", "risk: 2")}  # REVIEW
        _, out = self._next(reqs, {})
        self.assertLess(out.index("DRAFT-B-002"), out.index("DRAFT-A-001"))  # high-risk first
        self.assertIn("[REVIEW]", out)

    def test_top_n_truncates_and_all_expands(self):
        reqs = {"DRAFT-{}-00{}".format(c, i): self._req("draft")
                for i, c in enumerate("ABCDE", 1)}            # 5 drafts > top_n=3
        _, out = self._next(reqs, {})
        self.assertIn("more — run `reqmap.py next --all`", out)
        _, out_all = self._next(reqs, {}, show_all=True)
        self.assertNotIn("more — run", out_all)
        for rid in reqs:
            self.assertIn(rid, out_all)

    def test_blast_radius_is_omitted(self):
        # FOO has 3 dependents -> blast-radius signal, but next must not surface it
        reqs = {"CORE-FOO-001": self._req("confirmed"),
                "A-1": self._req("confirmed", "depends_on: [CORE-FOO-001]"),
                "B-2": self._req("confirmed", "depends_on: [CORE-FOO-001]"),
                "C-3": self._req("confirmed", "depends_on: [CORE-FOO-001]")}
        members = {k: [("implements", "x.py", 1), ("tested-by", "t.py", 2)] for k in reqs}
        _, out = self._next(reqs, members)
        self.assertNotIn("blast-radius", out)

    def test_all_clear_when_nothing_pending(self):
        reqs = {"CORE-FOO-001": self._req("confirmed")}
        members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        code, out = self._next(reqs, members)
        self.assertEqual(code, 0)
        self.assertIn("Nothing pending", out)

    def test_empty_registry_is_distinct_from_all_clear(self):
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

    def test_granularity_at_threshold_warns(self):  # tested-by: REQ-NEXT-013
        reqs = {"AREA-FOO-001": self._req_with_acs(5)}
        _, out = self._next(reqs, {})
        self.assertIn("consider splitting", out)
        self.assertIn("AREA-FOO-001", out)

    def test_granularity_below_threshold_no_warn(self):  # tested-by: REQ-NEXT-013
        reqs = {"AREA-FOO-001": self._req_with_acs(4)}
        _, out = self._next(reqs, {})
        self.assertNotIn("consider splitting", out)

    def test_granularity_above_threshold_warns(self):  # tested-by: REQ-NEXT-013
        reqs = {"AREA-FOO-001": self._req_with_acs(8)}
        _, out = self._next(reqs, {})
        self.assertIn("consider splitting", out)
        self.assertIn("AREA-FOO-001", out)


class Init(unittest.TestCase):  # tested-by: REQ-INIT-012
    def _init(self, code_root, wipe=False):
        reqs_dir = os.path.join(code_root, "requirements")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_init(reqs_dir, code_root, wipe=wipe)
        return code, buf.getvalue(), reqs_dir

    def _req_file(self, d, rid="CORE-FOO-001"):
        path = os.path.join(d, "requirements", rid + ".md")
        _write(path, "---\nid: {}\nstatus: confirmed\n---\n\n# Cap\n".format(rid))
        return path

    def test_scaffolds_dir_ignore_lock_and_map(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "scripts", "app.py"), "def f(x):\n    return x\n")
            code, out, reqs_dir = self._init(d)
            self.assertEqual(code, 0)
            self.assertTrue(os.path.isdir(reqs_dir))
            ignore = open(os.path.join(d, ".reqmapignore"), encoding="utf-8").read()
            self.assertIn("scripts/reqmap.py", ignore)
            self.assertTrue(os.path.exists(os.path.join(reqs_dir, "_map.json")))
            self.assertTrue(os.path.exists(os.path.join(reqs_dir, "_map.md")))
            self.assertTrue(os.path.exists(R.lock_path(reqs_dir)))

    def test_drafts_from_existing_code(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"), "x = 1\n")
            _, _, reqs_dir = self._init(d)
            drafts = [n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-")]
            self.assertTrue(drafts)

    def test_selfhost_init_omits_engine_ignore(self):
        # A self-hosting repo: scripts/reqmap.py carries a tag that resolves to an
        # existing requirement => init must NOT ignore the engine (else it orphans it).
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "CORE-X-001.md"),
                   "---\nid: CORE-X-001\nstatus: confirmed\n---\n\n# Cap\n")
            _write(os.path.join(d, "scripts", "reqmap.py"),
                   tag("CORE-X-001") + "\nx = 1\n")
            self._init(d)
            ignore = open(os.path.join(d, ".reqmapignore"), encoding="utf-8").read()
            # No live (uncommented) glob ignoring the engine.
            globs = [ln.strip() for ln in ignore.splitlines()
                     if ln.strip() and not ln.strip().startswith("#")]
            self.assertNotIn("scripts/reqmap.py", globs)
            # And the engine is actually scanned as a member of the resolved requirement.
            members = R.scan_members(d, os.path.join(d, "requirements"))
            self.assertIn("CORE-X-001", members)

    def test_does_not_clobber_existing_reqmapignore(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, ".reqmapignore"), "my-custom-glob/**\n")
            self._init(d)
            kept = open(os.path.join(d, ".reqmapignore"), encoding="utf-8").read()
            self.assertEqual(kept, "my-custom-glob/**\n")  # untouched

    def test_rerun_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"), "x = 1\n")
            self._init(d)
            code, _, _ = self._init(d)   # second run
            self.assertEqual(code, 0)

    def test_summary_points_at_next(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"), "x = 1\n")
            _, out, _ = self._init(d)
            self.assertIn("reqmap.py next", out)

    def test_empty_extraction_is_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "README.txt"), "not code\n")   # nothing extractable
            code, out, reqs_dir = self._init(d)
            self.assertEqual(code, 0)
            self.assertIn("no requirements were extracted", out)
            self.assertEqual([n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-")], [])

    # --wipe tests
    def test_wipe_deletes_existing_requirements(self):
        with tempfile.TemporaryDirectory() as d:
            req_path = self._req_file(d)
            _write(os.path.join(d, "requirements", "_map.md"), "generated\n")
            _write(os.path.join(d, "app.py"), "def f(): pass\n")
            code, _, _ = self._init(d, wipe=True)
            self.assertEqual(code, 0)
            self.assertFalse(os.path.exists(req_path))       # authored requirement deleted
            self.assertTrue(os.path.exists(                  # generated file stays (or re-created)
                os.path.join(d, "requirements", "_map.md")))

    def test_wipe_strips_tags_from_source(self):
        with tempfile.TemporaryDirectory() as d:
            self._req_file(d)
            _write(os.path.join(d, "app.py"),
                   "def f():  " + tag("CORE-FOO-001") + "\n    pass\n")
            self._init(d, wipe=True)
            content = open(os.path.join(d, "app.py"), encoding="utf-8").read()
            self.assertNotIn(_ROLE + ":", content)
            self.assertIn("def f():", content)               # code line preserved

    def test_wipe_strips_tested_by_tag(self):
        with tempfile.TemporaryDirectory() as d:
            self._req_file(d)
            _write(os.path.join(d, "test_app.py"),
                   "class T:  " + tb_tag("CORE-FOO-001") + "\n    pass\n")
            self._init(d, wipe=True)
            content = open(os.path.join(d, "test_app.py"), encoding="utf-8").read()
            self.assertNotIn(_TB_ROLE + ":", content)
            self.assertIn("class T:", content)

    def test_wipe_left_boundary_guard(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"),
                   "# re" + _ROLE + ": CORE-FOO-001\ndef f(): pass\n")
            self._init(d, wipe=True)
            content = open(os.path.join(d, "app.py"), encoding="utf-8").read()
            self.assertIn("re" + _ROLE + ":", content)      # NOT stripped

    def test_wipe_preserves_non_tag_comments(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"),
                   "# regular comment\ndef f(): pass\n")
            self._init(d, wipe=True)
            content = open(os.path.join(d, "app.py"), encoding="utf-8").read()
            self.assertIn("# regular comment", content)

    def test_no_wipe_preserves_requirements(self):
        with tempfile.TemporaryDirectory() as d:
            req_path = self._req_file(d)
            self._init(d, wipe=False)
            self.assertTrue(os.path.exists(req_path))       # untouched without --wipe


def _kv(extra):
    """Parse the 'key: value' frontmatter lines a test passes as `extra` into meta,
    so Next can build requirement dicts the same way the REQ template does."""
    for line in extra.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta, _ = R.parse_frontmatter("---\n{}: {}\n---\n".format(k.strip(), v.strip()))
        yield k.strip(), meta.get(k.strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
