"""Writing requirements: `new`, `promote`, `init`, extraction and candidates, the
readability linter, `clarify`/`--decompose`, `retire` and the level retrofit.

Part of the `test_reqmap` suite — run it through the aggregator (`python
scripts/test_reqmap.py`), or on its own with `python -m unittest test_reqmap_author`."""
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



class Extract(unittest.TestCase):  # tested-by: ARCH-EXTRACT-008  # tested-by: REQ-EXTRACT-849  # tested-by: REQ-EXTRACT-850
    def test_same_basename_different_dirs_no_collision(self):  # bug #10  # verifies: REQ-EXTRACT-850#CASE-5
        self.assertNotEqual(R._draft_id("src/utils.py"), R._draft_id("lib/utils.js"))
        self.assertEqual(R._draft_id("src/utils.py"), "DRAFT-SRC-UTILS")

    def test_empty_stem_fallback(self):  # bug #19
        self.assertEqual(R._draft_id("_.py"), "DRAFT-FILE")
        self.assertEqual(R._draft_id("世界.py"), "DRAFT-FILE")

    def test_extract_creates_distinct_drafts_and_makedirs(self):  # bugs #10/#11/#12  # verifies: REQ-EXTRACT-850#CASE-1  # verifies: REQ-EXTRACT-850#CASE-4
        with tempfile.TemporaryDirectory() as d:
            code = os.path.join(d, "code")
            _write(os.path.join(code, "src", "utils.py"), "x = 1\n")
            _write(os.path.join(code, "lib", "utils.js"), "var x = 1;\n")
            out = os.path.join(d, "new", "reqs")  # does not exist yet
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract(R.Workspace({}, {}, out, code))
            made = sorted(n for n in os.listdir(out) if n.startswith("DRAFT-"))
            self.assertEqual(made, ["DRAFT-LIB-UTILS.md", "DRAFT-SRC-UTILS.md"])

    def test_extract_drafts_go_and_rust(self):  # bug: draft-narrow-extension-set  # verifies: REQ-EXTRACT-849#CASE-1
        # draft/init must cover the same code extensions the scanner does, not just 5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "server.go"), "package main\n")
            _write(os.path.join(d, "lib.rs"), "fn main() {}\n")
            reqs_dir = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, d))
            made = sorted(n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-"))
            self.assertIn("DRAFT-SERVER.md", made)
            self.assertIn("DRAFT-LIB.md", made)

    def test_extract_honors_reqmapignore(self):  # init surfaced: extract ignored .reqmapignore  # verifies: REQ-EXTRACT-849#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "keep.py"), "x = 1\n")
            _write(os.path.join(d, "scripts", "reqmap.py"), "y = 2\n")
            _write(os.path.join(d, ".reqmapignore"), "scripts/reqmap.py\n")
            reqs_dir = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, d))
            made = sorted(n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-"))
            self.assertEqual(made, ["DRAFT-KEEP.md"])   # the vendored engine is not drafted

    def test_drafted_contract_carries_the_binding_line_and_no_shall(self):  # verifies: REQ-EXTRACT-850#CASE-3
        with tempfile.TemporaryDirectory() as d:
            code_root = os.path.join(d, "src")
            os.makedirs(code_root)
            with open(os.path.join(code_root, "widget.py"), "w", encoding="utf-8") as f:
                f.write("def go():\n    return 1\n")
            reqs_dir = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, code_root))
            written = [p for p in os.listdir(reqs_dir) if p.endswith(".md")]
            # one code draft plus the two rungs above it since ADR-0030; the subject of
            # this test is the drafted CONTRACT, so read the code draft specifically
            drafts = [p for p in written if p.startswith("DRAFT-")]
            self.assertEqual(len(drafts), 1, written)
            with open(os.path.join(reqs_dir, drafts[0]), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("Every bullet below is binding.", text)
            for p in written:
                with open(os.path.join(reqs_dir, p), encoding="utf-8") as f:
                    self.assertNotIn("shall", f.read().lower(), p)


class Template(unittest.TestCase):  # tested-by: REQ-NEWGONE-1034 @unit
    """ADR-0045 decision 2: `new` is gone and the template it stamped stays — it is
    the shape a person or an assistant follows when writing the file directly."""

    def test_template_uses_the_plain_present_voice(self):  # verifies: REQ-NEWGONE-1034#CASE-4
        t = R.REQUIREMENT_TEMPLATE
        self.assertIn("Every bullet below is binding.", t)
        # No CLAUSE may use a modal — but the guidance comment must stay free to name
        # 'shall' as the thing not to write, which is the clearest way to say it.
        # Comments are stripped whole: _prose_lint yields each line of a multi-line
        # comment separately, so filtering on a leading '<!--' would only drop the first.
        clauses = R._prose_lint(re.sub(r"<!--.*?-->", "", t, flags=re.DOTALL), "description")
        self.assertTrue(clauses)                       # guard: the section actually parsed
        for ln in clauses:
            self.assertNotIn("shall", ln.lower())
            self.assertNotIn("must", ln.lower())

    def test_template_contract_body_passes_its_own_linter(self):  # verifies: REQ-NEWGONE-1034#CASE-4
        # the shipped template must not be flagged by the checks it teaches
        req = {"meta": {"status": "confirmed"}, "body": R.REQUIREMENT_TEMPLATE.split("---\n", 2)[-1]}
        checks = {f["check"] for f in R.lint_requirement("AREA-NAME-001", req)}
        self.assertNotIn("anonymous-subject", checks)
        self.assertNotIn("statement-too-long", checks)
        self.assertNotIn("statement-size", checks)


class Candidates(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009  # tested-by: REQ-CANDIDATES-826  # tested-by: REQ-CANDIDATES-827
    def _plan(self, d):
        reqs_dir = os.path.join(d, "requirements")
        reqs = R.load_requirements(reqs_dir)
        members = R.scan_members(d, reqs_dir)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(R.Workspace(reqs, members, reqs_dir, d), None)
        return json.loads(buf.getvalue())

    def test_writes_no_md_and_valid_json(self):  # verifies: REQ-CANDIDATES-826#CASE-1  # verifies: REQ-CANDIDATES-826#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), '"""mod a."""\ndef f(x):\n    return x\n')
            plan = self._plan(d)
            self.assertIn("candidates", plan)
            self.assertEqual([n for n in os.listdir(d) if n.endswith(".md")], [])

    def test_respects_reqmapignore(self):  # verifies: REQ-CANDIDATES-826#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "keep.py"), "x = 1\n")
            _write(os.path.join(d, "skip.py"), "y = 2\n")
            _write(os.path.join(d, ".reqmapignore"), "skip.py\n")
            allfiles = [f for c in self._plan(d)["candidates"] for f in c["files"]]
            self.assertIn("keep.py", allfiles)
            self.assertNotIn("skip.py", allfiles)

    def test_derives_depends_on_from_imports(self):  # verifies: REQ-CANDIDATES-827#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "paths.py"), "ROOT = '.'\n")
            _write(os.path.join(d, "app.py"), "import paths\n")
            cands = self._plan(d)["candidates"]
            app = next(c for c in cands if "app.py" in c["files"])
            paths = next(c for c in cands if "paths.py" in c["files"])
            self.assertIn(paths["suggested_id"], app["depends_on"])

    def test_capmap_groups_files(self):  # verifies: REQ-CANDIDATES-827#CASE-6
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

    def test_existing_req_for_tagged_file(self):  # verifies: REQ-CANDIDATES-827#CASE-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), tag("CORE-FOO-001") + "\n")
            m = next(c for c in self._plan(d)["candidates"] if "m.py" in c["files"])
            self.assertEqual(m["existing_req"], "CORE-FOO-001")

    def test_unparseable_python_does_not_abort(self):  # one bad file != crash  # verifies: REQ-CANDIDATES-826#CASE-7
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "bad.py"), "def (:\n")     # SyntaxError
            _write(os.path.join(d, "good.py"), "z = 1\n")
            files = [f for c in self._plan(d)["candidates"] for f in c["files"]]
            self.assertIn("good.py", files)
            self.assertIn("bad.py", files)


class CapmapMalformed(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009
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


class CandidatesGrouping(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009  # tested-by: REQ-CANDIDATES-827
    def _plan(self, d):
        reqs_dir = os.path.join(d, "requirements")
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(R.Workspace(R.load_requirements(reqs_dir),
                                         R.scan_members(d, reqs_dir), reqs_dir, d), None)
        return json.loads(buf.getvalue())

    def test_high_fanin_module_inferred_bus(self):  # bug: candidates-bus-threshold-untested  # verifies: REQ-CANDIDATES-827#CASE-4
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

    def test_same_stem_files_mint_distinct_ids(self):  # bug: mint-cap-id-collision  # verifies: REQ-CANDIDATES-827#CASE-7
        """Two files sharing a slug (foo.py + foo.js) must mint distinct suggested
        ids, not collapse into one conflated candidate (#9)."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "parser.py"), "x = 1\n")
            _write(os.path.join(d, "parser.js"), "var y = 2;\n")
            cands = [c for c in self._plan(d)["candidates"]
                     if c["files"] in (["parser.py"], ["parser.js"])]
            self.assertEqual(len(cands), 2, "both same-stem files must be candidates")
            ids = [c["suggested_id"] for c in cands]
            self.assertEqual(len(set(ids)), 2,
                             "same-stem files must mint distinct ids; got " + str(ids))

    def test_minted_id_avoids_existing_requirement_id(self):  # bug: mint-cap-id-vs-reqs-collision
        """A minted candidate id must not duplicate an EXISTING requirement id
        (seed used_ids from reqs, not just the capmap groups)."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "PARSER-001.md"),
                   "---\nid: PARSER-001\nstatus: confirmed\n---\n\n# Cap\n")
            _write(os.path.join(d, "parser.py"), "x = 1\n")  # untagged -> slug PARSER-001
            parser = next(c for c in self._plan(d)["candidates"]
                          if c["files"] == ["parser.py"])
            self.assertNotEqual(parser["suggested_id"], "PARSER-001",
                                "minted id must not collide with an existing requirement id")


class MdDiscovery(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009
    def _plan(self, d, md_globs=None):
        reqs_dir = os.path.join(d, "requirements")
        reqs = R.load_requirements(reqs_dir)
        members = R.scan_members(d, reqs_dir)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(R.Workspace(reqs, members, reqs_dir, d), None, md_globs)
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

    def test_extra_code_exts_env_scans_custom_extension(self):  # REQMAP_EXTRA_CODE_EXTS
        # A repo can declare extra scannable extensions via the env var; a file with a
        # custom extension (leading dot in the env value optional) then has its capability
        # tag picked up. Reload the config module so its extension merge re-runs.
        import importlib
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "src", "widget.foo"),
                   "// {}: AREA-FEATURE-001\n".format(_ROLE))
            _write(os.path.join(d, "src", "helper.bar"),
                   "// {}: AREA-FEATURE-001\n".format(_ROLE))
            with mock.patch.dict(os.environ, {"REQMAP_EXTRA_CODE_EXTS": ".foo, bar"}):
                importlib.reload(R.config)
                try:
                    members = R.scan_members(d, os.path.join(d, "requirements"))
                finally:
                    importlib.reload(R.config)  # restore default CODE_EXTS for other tests
            self.assertIn("AREA-FEATURE-001", members)
            files = {os.path.basename(m[1]) for m in members["AREA-FEATURE-001"]}
            self.assertIn("widget.foo", files)   # leading-dot form
            self.assertIn("helper.bar", files)   # dot auto-prepended


class Promote(unittest.TestCase):  # tested-by: ARCH-PROMOTE-011  # tested-by: REQ-PROMOTE-894
    def _run(self, d, cap_id):
        # `confirm` is gone; what survives is the surgical status edit the demotion
        # now uses. The tests below are about THAT, and always were.
        reqs = R.load_requirements(d)
        r = reqs.get(cap_id)
        if not r:
            return 1, ""
        ok = R._write_frontmatter_status(r, "confirmed")
        return (0 if ok else 1), ""

    def test_promotes_baseline_with_implements(self):  # AC-1  # verifies: REQ-PROMOTE-894#CASE-1  # verifies: REQ-PROMOTE-894#CASE-4
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

    def test_preserves_trailing_comment(self):  # AC-4  # verifies: REQ-PROMOTE-894#CASE-3
        new_text, n = R._set_frontmatter_status(
            "---\nid: X-1\nstatus: baseline   # was draft\nlayer: bus\n---\n\nbody\n", "confirmed")
        self.assertEqual(n, 1)
        self.assertIn("status: confirmed   # was draft", new_text)
        self.assertIn("\nbody\n", new_text)

    def test_no_frontmatter_is_noop(self):
        new_text, n = R._set_frontmatter_status("no frontmatter here", "confirmed")
        self.assertEqual(n, 0)
        self.assertEqual(new_text, "no frontmatter here")

    def test_promote_preserves_mixed_line_endings(self):  # bug: promote-mixed-eol-blanket-convert
        with tempfile.TemporaryDirectory() as d:
            raw = (b"---\r\nid: AREA-M-001\r\nstatus: baseline\nlayer: bus\r\n---\r\n\r\nbody line\n")
            p = os.path.join(d, "AREA-M-001.md")
            with open(p, "wb") as f:
                f.write(raw)
            _write(os.path.join(d, "m.py"), tag("AREA-M-001") + "\n")
            reqs = R.load_requirements(d)
            code = 0 if R._write_frontmatter_status(reqs["AREA-M-001"], "confirmed") else 1
            self.assertEqual(code, 0)
            with open(p, "rb") as f:
                after = f.read()
            # the originally bare-LF "status:" line must STAY bare-LF, not become CRLF
            self.assertIn(b"status: confirmed\n", after)
            self.assertNotIn(b"status: confirmed\r\n", after)
            # untouched CRLF lines must remain CRLF
            self.assertIn(b"id: AREA-M-001\r\n", after)
            self.assertIn(b"body line\n", after)


class Init(unittest.TestCase):  # tested-by: ARCH-INIT-012  # tested-by: REQ-INIT-860  # tested-by: REQ-INIT-861  # tested-by: REQ-PLANHORIZON-1010 @unit
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

    def test_seeds_the_plan_files_once(self):  # verifies: REQ-PLANHORIZON-1010#CASE-4
        # A plan file a repo does not have is a plan nobody writes — and a second `init`
        # that overwrote an edited one would be worse than never seeding it.
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "scripts", "app.py"), "def f(x):\n    return x\n")
            _code, _out, reqs_dir = self._init(d)
            roadmap = os.path.join(d, "ROADMAP.md")
            planning = os.path.join(reqs_dir, "_planning.json")
            self.assertTrue(os.path.exists(roadmap))
            self.assertTrue(os.path.exists(planning))
            seeded = json.loads(io.open(planning, encoding="utf-8").read())
            self.assertEqual(["Feature", "Fix", "Release"], seeded["lanes"])
            # no frozen end: the horizon is recomputed, so the calendar cannot go stale
            self.assertNotIn("until", seeded["cadence"])
            _write(roadmap, "# mine\n")
            _write(planning, '{"lanes": ["Only"]}')
            self._init(d)
            self.assertEqual("# mine\n", io.open(roadmap, encoding="utf-8").read())
            self.assertEqual(["Only"],
                             json.loads(io.open(planning, encoding="utf-8").read())["lanes"])

    def test_the_seeded_plan_is_not_drafted_as_a_capability(self):  # verifies: REQ-PLANHORIZON-1010#CASE-5
        # `init` seeds ROADMAP.md before the extraction pass, so without the ignore line
        # the extractor reads it as untagged prose and mints a requirement whose subject
        # is the plan file itself — then stamps a membership tag into the plan.
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "scripts", "app.py"), "def f(x):\n    return x\n")
            _code, _out, reqs_dir = self._init(d)
            body = io.open(os.path.join(d, "ROADMAP.md"), encoding="utf-8").read()
            self.assertNotIn("implements:", body)
            drafted = [f for f in os.listdir(reqs_dir) if f.endswith(".md")]
            self.assertFalse([f for f in drafted if "ROADMAP" in f.upper()],
                             "the plan file is not a capability")

    def test_scaffolds_dir_ignore_lock_and_map(self):  # verifies: REQ-INIT-860#CASE-1  # verifies: REQ-INIT-860#CASE-3
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

    def test_selfhost_init_omits_engine_ignore(self):  # verifies: REQ-INIT-860#CASE-5
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

    def test_seed_ignores_agent_worktree_copies(self):
        # An isolated-subagent worktree holds a FULL second copy of the repo. Both the
        # older `.worktrees/` and Claude Code's `.claude/worktrees/` must be seeded.
        with tempfile.TemporaryDirectory() as d:
            self._init(d)
            ignore = open(os.path.join(d, ".reqmapignore"), encoding="utf-8").read()
            globs = [ln.strip() for ln in ignore.splitlines()
                     if ln.strip() and not ln.strip().startswith("#")]
            self.assertIn(".worktrees/**", globs)
            self.assertIn(".claude/worktrees/**", globs)

    def test_seeded_ignore_prunes_a_worktree_copy(self):  # verifies: REQ-INIT-860#CASE-4
        # The copy's tags would otherwise be counted a second time as members.
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "CORE-X-001.md"),
                   "---\nid: CORE-X-001\nstatus: confirmed\n---\n\n# Cap\n")
            _write(os.path.join(d, "app.py"), tag("CORE-X-001") + "\n")
            self._init(d)
            for wt in (".worktrees", os.path.join(".claude", "worktrees")):
                _write(os.path.join(d, wt, "wt1", "app.py"), tag("CORE-X-001") + "\n")
            hits = R.scan_members(d, os.path.join(d, "requirements"))["CORE-X-001"]
            self.assertEqual([fp for _role, fp, _ln in hits], ["app.py"])


    def test_does_not_clobber_existing_reqmapignore(self):  # verifies: REQ-INIT-860#CASE-2  # verifies: REQ-INIT-861#CASE-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, ".reqmapignore"), "my-custom-glob/**\n")
            self._init(d)
            kept = open(os.path.join(d, ".reqmapignore"), encoding="utf-8").read()
            self.assertEqual(kept, "my-custom-glob/**\n")  # untouched

    def test_rerun_is_safe(self):  # verifies: REQ-INIT-861#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"), "x = 1\n")
            self._init(d)
            code, _, _ = self._init(d)   # second run
            self.assertEqual(code, 0)

    def test_summary_points_at_next(self):  # verifies: REQ-INIT-861#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"), "x = 1\n")
            _, out, _ = self._init(d)
            self.assertIn("reqmap.py gate --risk", out)

    def test_empty_extraction_is_distinct(self):  # verifies: REQ-INIT-861#CASE-3
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
            with open(os.path.join(d, "app.py"), encoding="utf-8") as f:
                content = f.read()
            # `init --wipe` wipes and then re-initialises, and extraction now links each
            # source to the draft it writes (REQ-INITTAG-1008). So the OLD tag is gone and
            # the only tag left is the fresh DRAFT id — never the requirement just deleted.
            self.assertNotIn("CORE-FOO-001", content)
            self.assertEqual(content.count(_ROLE + ":"), 1)
            self.assertIn("DRAFT-APP", content)
            self.assertIn("def f():", content)               # code line preserved

    def test_wipe_strips_tested_by_tag(self):
        with tempfile.TemporaryDirectory() as d:
            self._req_file(d)
            _write(os.path.join(d, "test_app.py"),
                   "class T:  " + tb_tag("CORE-FOO-001") + "\n    pass\n")
            self._init(d, wipe=True)
            with open(os.path.join(d, "test_app.py"), encoding="utf-8") as f:
                content = f.read()
            # same as above: the old link is gone, and a test path is re-linked as tested-by
            self.assertNotIn("CORE-FOO-001", content)
            self.assertEqual(content.count(_TB_ROLE + ":"), 1)
            self.assertIn("DRAFT-TEST-APP", content)
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

    def test_no_wipe_preserves_requirements(self):  # verifies: REQ-INIT-861#CASE-5
        with tempfile.TemporaryDirectory() as d:
            req_path = self._req_file(d)
            self._init(d, wipe=False)
            self.assertTrue(os.path.exists(req_path))       # untouched without --wipe


class StripLineTag(unittest.TestCase):  # tested-by: ARCH-INIT-012
    """_strip_line_tag strips only a genuine tag comment, never prose/headings
    that merely mention the tagging convention (regression for the init --wipe
    data-loss bugs: prose/heading truncation and dangling bare markers)."""

    _CID = "AREA-NAME-001"

    def _line(self, prefix):
        return "{}{}: {}".format(prefix, _ROLE, self._CID)

    def test_strips_trailing_code_comment(self):
        self.assertEqual(R._strip_line_tag(self._line("def f():  # ") + "\n"),
                         "def f():\n")

    def test_strips_pure_comment_line(self):
        self.assertEqual(R._strip_line_tag(self._line("# ") + "\n"), "\n")

    def test_strips_html_comment_line(self):
        self.assertEqual(R._strip_line_tag("<!-- {}: {} -->\n".format(_ROLE, self._CID)),
                         "\n")

    def test_preserves_prose_heading_mention(self):
        # a heading that documents the convention must survive --wipe intact
        line = "# How {}: {} tags work\n".format(_ROLE, self._CID)
        self.assertEqual(R._strip_line_tag(line), line)

    def test_preserves_prose_html_mention(self):
        line = "<!-- note --> tag {}: {} is required <!-- end -->\n".format(_ROLE, self._CID)
        self.assertEqual(R._strip_line_tag(line), line)

    def test_markdown_heading_tag_leaves_no_dangling_marker(self):
        # `## implements: X` is a pure tag heading — removed whole, never left as '#'
        out = R._strip_line_tag("## {}: {}\n".format(_ROLE, self._CID))
        self.assertEqual(out, "\n")
        self.assertNotIn("#", out)

    def test_banner_comment_removed_whole(self):
        self.assertEqual(R._strip_line_tag("//// {}: {}\n".format(_ROLE, self._CID)),
                         "\n")

    def test_no_tag_unchanged(self):
        self.assertEqual(R._strip_line_tag("def f(): pass\n"), "def f(): pass\n")


class ParseTodos(unittest.TestCase):
    def test_basic_items(self):
        text = (
            "# TODO\n\n"
            "## v1.14\n"
            "- [ ] Feature A | lane: feature\n"
            "- [x] Done item | lane: ops\n\n"
            "## v1.15\n"
            "- [ ] Feature B\n"
        )
        todos = R._parse_todos_from_text(text)
        self.assertEqual(len(todos), 3)
        self.assertEqual(todos[0], {"name": "Feature A",  "lane": "feature", "milestone": "v1.14", "done": False})
        self.assertEqual(todos[1], {"name": "Done item",  "lane": "ops",     "milestone": "v1.14", "done": True})
        self.assertEqual(todos[2], {"name": "Feature B",  "lane": "feature", "milestone": "v1.15", "done": False})

    def test_bug_lane_parses_and_legacy_lanes_still_do(self):
        todos = R._parse_todos_from_text("## v2.0\n- [ ] Crash on empty stdin | lane: bug\n"
                                         "- [ ] Old style | lane: ops\n- [ ] Bare item\n")
        self.assertEqual([t["lane"] for t in todos], ["bug", "ops", "feature"])

    def test_missing_file_returns_empty(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(R._parse_todos(d), [])

    def test_milestone_in_node(self):
        """_build_map_data emits milestone field on each node."""
        with tempfile.TemporaryDirectory() as tmp:
            req_dir = os.path.join(tmp, "requirements")
            os.makedirs(req_dir)
            _write(os.path.join(req_dir, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\nlayer: feature\nmilestone: v1.14\n---\n\n# Title\n")
            reqs = R.load_requirements(req_dir)
            members = R.scan_members(tmp)
            data = R._build_map_data(reqs, members)
            node = next(n for n in data["nodes"] if n["id"] == "REQ-A-001")
            self.assertEqual(node["milestone"], "v1.14")

    def test_todos_in_json_text(self):
        """_build_json_text includes todos key."""
        data = {"nodes": [], "edges": [], "repo": None,
                "todos": [{"name": "X", "lane": "feature", "milestone": "v1.14", "done": False}]}
        payload = json.loads(R._build_json_text(data))
        self.assertEqual(payload["todos"][0]["name"], "X")

    def test_milestone_heading_with_annotation(self):
        """A milestone heading carrying a trailing annotation still registers and
        keeps its items (#10) — e.g. `## v2.8 (deferred — demand-gated)`."""
        text = ("## v2.8 (deferred — demand-gated)\n"
                "- [ ] MCP server | lane: feature\n")
        todos = R._parse_todos_from_text(text)
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["milestone"], "v2.8")
        self.assertEqual(todos[0]["name"], "MCP server")


class Lint(unittest.TestCase):  # tested-by: ARCH-LINT-014  # tested-by: ARCH-LINTCHECKS-025  # tested-by: REQ-LINT-863  # tested-by: REQ-LINT-864  # tested-by: REQ-LINTCHECKS-865  # tested-by: REQ-LINTCHECKS-866  # tested-by: REQ-LINTCHECKS-868  # tested-by: REQ-LINTCHECKS-869
    CONTRACT = "## WHAT — Contract (normative)"
    ACCEPT = "## HOW — Acceptance (= tests)"

    def _lint(self, reqs, strict=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_lint(R.Workspace(reqs), strict)
        return code, buf.getvalue()

    def _req(self, status, body):
        return {"meta": {"status": status}, "body": body}

    def _body(self, contract="- ok.\n", acceptance="- ok.\n"):
        return "# T\n\n{}\n{}\n{}\n{}\n".format(self.CONTRACT, contract, self.ACCEPT, acceptance)

    def test_missing_acceptance_section_is_error(self):  # verifies: ARCH-LINT-014#CASE-1  # verifies: REQ-LINT-863#CASE-4  # verifies: REQ-LINT-863#CASE-5
        body = "# T\n\n{}\n- the contract.\n".format(self.CONTRACT)  # no acceptance heading
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertIn(("error", "missing-section"),
                      [(f["severity"], f["check"]) for f in fs])

    def test_over_scoped_fires_only_on_both_ceilings(self):  # composite cohesion signal  # verifies: REQ-LINTCHECKS-866#CASE-3
        big_contract = "".join("- clause {}.\n".format(i) for i in range(R.LINT_CONTRACT_MAX + 1))
        big_ac = "".join("- AC {}.\n".format(i) for i in range(R.LINT_AC_MAX + 1))
        small_ac = "".join("- AC {}.\n".format(i) for i in range(3))
        over = R.lint_requirement("REQ-BIG-001", self._req("confirmed", self._body(big_contract, big_ac)))
        self.assertIn("over-scoped", [f["check"] for f in over])             # both ceilings => fires
        one = R.lint_requirement("REQ-OK-001", self._req("confirmed", self._body(big_contract, small_ac)))
        self.assertNotIn("over-scoped", [f["check"] for f in one])           # only one ceiling => silent

    def test_over_scoped_counts_groups_not_clauses(self):  # verifies: REQ-LINTCHECKS-866#CASE-4
        # the atomic voice multiplies bullets without widening scope: a grouped contract
        # is measured by its groups, so splitting one clause into three stays silent
        big_ac = "".join("- AC {}.\n".format(i) for i in range(R.LINT_AC_MAX + 1))
        grouped = ""
        for g in range(3):                                   # 3 groups, well under the ceiling
            grouped += "**Group {}**\n".format(g)
            for c in range(R.LINT_CONTRACT_MAX):             # but 30 clauses in total
                grouped += "- `cmd` does thing {}-{}.\n".format(g, c)
        fs = R.lint_requirement("REQ-G-001", self._req("confirmed", self._body(grouped, big_ac)))
        self.assertNotIn("over-scoped", [f["check"] for f in fs])
        # an UNGROUPED contract still falls back to counting clauses, as it always did
        flat = "".join("- `cmd` does thing {}.\n".format(i) for i in range(R.LINT_CONTRACT_MAX + 1))
        flat_fs = R.lint_requirement("REQ-F-001", self._req("confirmed", self._body(flat, big_ac)))
        self.assertIn("over-scoped", [f["check"] for f in flat_fs])

    def test_empty_section_flags_contentless_heading(self):  # verifies: ARCH-LINT-014#CASE-3  # verifies: REQ-LINT-863#CASE-6
        empty = "# T\n\n{}\n{}\n".format(self.CONTRACT, self.ACCEPT)         # both headings, no content
        fs = R.lint_requirement("REQ-E-001", self._req("confirmed", empty))
        self.assertIn("empty-section", [f["check"] for f in fs])
        self.assertNotIn("empty-section",                                    # content present => silent
                         [f["check"] for f in R.lint_requirement("REQ-F-001", self._req("confirmed", self._body()))])

    def test_file_spread_warns_across_many_files(self):  # validates the positive branch via a synthetic multi-file fixture  # verifies: REQ-LINTCHECKS-866#CASE-5  # verifies: REQ-LINTCHECKS-866#CASE-6
        r = self._req("confirmed", self._body())
        spread = [("implements", "x/a.py", 1), ("implements", "y/b.py", 2), ("implements", "z/c.py", 3)]
        self.assertIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-D-001", r, spread)])
        # three files in one directory are one place to read (ADR-0042)
        pkg = [("implements", "pkg/a.py", 1), ("implements", "pkg/b.py", 2), ("implements", "pkg/c.py", 3)]
        self.assertNotIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-H-001", r, pkg)])
        # implements within a single file (tested-by files don't count) => silent in single-file repos
        one = [("implements", "a.py", 1), ("implements", "a.py", 9), ("tested-by", "t.py", 1)]
        self.assertNotIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-E-001", r, one)])
        # no member data supplied => check is skipped
        self.assertNotIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-G-001", r)])

    def test_draft_is_out_of_scope(self):  # verifies: ARCH-LINT-014#CASE-2  # verifies: REQ-LINT-863#CASE-3
        long_sent = " ".join(["word"] * 50) + "."
        reqs = {"DRAFT-X-001": self._req("draft", self._body(contract="- " + long_sent + "\n"))}
        code, out = self._lint(reqs)
        self.assertEqual(code, 0)
        self.assertNotIn("DRAFT-X-001", out)   # drafts are not linted

    def test_a_long_two_sentence_bullet_is_not_statement_too_long(self):
        # the dimension split: 24 words across two sentences used to fire. Word count is
        # `statement-size`'s job now, so this bullet is silent.
        stmt = "- It creates the folder. " + " ".join(["word"] * 20) + " now."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=stmt + "\n")))
        self.assertFalse(any(f["check"] == "statement-too-long" for f in fs))

    def test_statement_too_long_allows_three_sentences(self):
        # the authoring rule: a clause may hold two or three sentences.
        stmt = ("- `init` creates the folder. The folder holds the lock. "
                "The lock records one hash per requirement.")
        self.assertEqual(len(R._sentences(stmt[2:])), 3)
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=stmt + "\n")))
        self.assertFalse(any(f["check"] == "statement-too-long" for f in fs))

    def test_statement_too_long_fires_on_a_fourth_sentence(self):  # verifies: REQ-LINTCHECKS-865#CASE-1  # verifies: ARCH-LINTCHECKS-025#CASE-1
        stmt = ("- `init` creates the folder. The folder holds the lock. "
                "The lock records one hash per requirement. The hash is the contract.")
        self.assertEqual(len(R._sentences(stmt[2:])), 4)
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=stmt + "\n")))
        hits = [f for f in fs if f["check"] == "statement-too-long"]
        self.assertTrue(hits)
        self.assertEqual(hits[0]["severity"], "warn")
        self.assertIn("4 sentences", hits[0]["detail"])

    def test_stacked_conditions_warns(self):  # verifies: REQ-LINTCHECKS-865#CASE-2
        line = "- It shall do A and B and C and D."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=line + "\n")))
        self.assertTrue(any(f["check"] == "stacked-conditions" for f in fs))

    def test_stacked_conditions_fires_without_a_modal_keyword(self):  # verifies: REQ-LINTCHECKS-865#CASE-3
        # plain present tense, no 'shall'/'must' anywhere: the check must still fire
        line = "- `init` creates the folder and the lock and the map and the summary."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=line + "\n")))
        self.assertTrue(any(f["check"] == "stacked-conditions" for f in fs))

    def test_anonymous_subject_warns_on_unnamed_it(self):  # verifies: REQ-LINT-863#CASE-4  # verifies: REQ-LINT-864#CASE-4  # verifies: REQ-LINTCHECKS-865#CASE-4
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(contract="- It creates the folder.\n")))
        hits = [f for f in fs if f["check"] == "anonymous-subject"]
        self.assertTrue(hits)
        self.assertEqual(hits[0]["severity"], "warn")

    def test_anonymous_subject_silent_when_the_subject_is_named(self):
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(contract="- `init` creates the folder.\n")))
        self.assertFalse(any(f["check"] == "anonymous-subject" for f in fs))

    def test_anonymous_subject_is_contract_only(self):  # verifies: REQ-LINTCHECKS-865#CASE-5
        # Acceptance prose legitimately says "it" in a Then clause; only the Contract is policed
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(acceptance="- It returns an empty dict.\n")))
        self.assertFalse(any(f["check"] == "anonymous-subject" for f in fs))

    def test_anonymous_subject_ignores_a_word_starting_with_it(self):
        # 'Items' / 'Iterating' must not be read as the pronoun
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(contract="- Items are sorted.\n")))
        self.assertFalse(any(f["check"] == "anonymous-subject" for f in fs))

    # These three probe `_prose_lint`'s fence and section handling, not any one check.
    # They used `long-sentence` as the probe until it was retired; `stacked-conditions`
    # reads the same source and fires deterministically on three and/or joins.
    PROBE = "a and b and c and d."

    def test_code_fence_line_not_flagged(self):  # verifies: ARCH-LINT-014#CASE-4
        accept = "```\n" + self.PROBE + "\n```\n"
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(acceptance=accept)))
        self.assertFalse(any(f["check"] == "stacked-conditions" for f in fs))

    def test_in_fence_heading_does_not_disable_linter(self):  # bug-hunt #10/#14
        # a '## ' comment INSIDE a fence must not be read as a heading and silently
        # disable the linter for the rest of the section
        accept = "```\n## not a heading\n```\n" + self.PROBE + "\n"
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(acceptance=accept)))
        self.assertTrue(any(f["check"] == "stacked-conditions" for f in fs))

    def test_lint_prose_first_section_only(self):  # bug-hunt #1  # verifies: REQ-LINT-864#CASE-1
        long_sent = " ".join(["word"] * 50) + "."
        body = ("# T\n\n## WHAT — Contract\n- short.\n\n"
                "## Notes — contract addendum\n- " + long_sent + "\n")
        self.assertEqual(R._prose_lint(body, "contract"), ["short."])

    def test_lint_prose_keeps_option_flag_hyphen(self):  # bug-hunt #13
        body = "## WHAT — Contract\n--strict makes it fail.\n"
        self.assertEqual(R._prose_lint(body, "contract"), ["--strict makes it fail."])

    def test_strict_zero_on_warnings_only(self):  # verifies: ARCH-LINT-014#CASE-5
        long_sent = " ".join(["word"] * 40) + "."
        reqs = {"REQ-X-001": self._req("confirmed", self._body(contract="- " + long_sent + "\n"))}
        code, _ = self._lint(reqs, strict=True)
        self.assertEqual(code, 0)   # warnings never fail --strict

    def test_strict_nonzero_on_missing_section(self):  # verifies: ARCH-LINT-014#CASE-6  # verifies: REQ-LINT-864#CASE-6
        body = "# T\n\n{}\n- the contract.\n".format(self.CONTRACT)  # no acceptance
        reqs = {"REQ-X-001": self._req("confirmed", body)}
        code, _ = self._lint(reqs, strict=True)
        self.assertEqual(code, 1)

    def test_atomic_bullet_then_mismatch_is_strict_promoted(self):
        # 3-bullet story, 1 Then: warn on plain lint, promoted to error under --strict —
        # STRICT_PROMOTE is the mechanism, not an unconditional error severity.
        body = ("# T\n\n> The refresh does three things:\n> - clears the cache\n"
                "> - reloads the index\n> - re-renders the view\n\n"
                "Scenario: a refresh clears the cache\n  Given  a stale cache\n"
                "  When   refresh runs\n  Then   the cache is cleared\n\n"
                "## Members in code (auto)\n")
        reqs = {"REQ-X-001": self._req("confirmed", body)}
        code, _ = self._lint(reqs, strict=False)
        self.assertEqual(code, 0)
        code, _ = self._lint(reqs, strict=True)
        self.assertEqual(code, 1)

    def test_statement_too_long_warns_on_multi_sentence_bullet(self):
        # four sentences in one bullet → a stacked statement (atomicity smell)
        stmt = "- It shall do the first thing. Then it waits. Then it retries. Then it acts."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=stmt + "\n")))
        hits = [f for f in fs if f["check"] == "statement-too-long"]
        self.assertTrue(hits)
        self.assertEqual(hits[0]["severity"], "warn")
        self.assertIn("sentences", hits[0]["detail"])

    def test_statement_too_long_silent_on_single_long_sentence(self):
        # sentence COUNT is the only dimension: one sentence is one sentence, however long.
        # Its length is `statement-size`'s business, at 150 words per clause.
        one = "- " + " ".join(["word"] * 40) + "."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=one + "\n")))
        self.assertFalse(any(f["check"] == "statement-too-long" for f in fs))

    def test_ac_count_low_warns(self):  # verifies: REQ-LINTCHECKS-866#CASE-1  # verifies: ARCH-LINTCHECKS-025#CASE-2
        body = self._body(contract="- ok.\n", acceptance="- only one AC.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertTrue(any(f["check"] == "ac-count-low" for f in fs))

    def test_ac_count_high_warns(self):  # verifies: REQ-LINTCHECKS-866#CASE-2
        accept = "".join("- AC number {}.\n".format(i) for i in range(8))  # 8 > 7
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(acceptance=accept)))
        self.assertTrue(any(f["check"] == "ac-count-high" for f in fs))

    def test_ac_count_clean_in_band(self):
        accept = "".join("- AC number {}.\n".format(i) for i in range(4))  # 4 in [3,7]
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(acceptance=accept)))
        self.assertFalse(any(f["check"].startswith("ac-count") for f in fs))

    def test_count_ac_handles_labeled_blocks(self):
        body = ("# T\n\n## HOW — Acceptance (= tests)\n"
                "AC-1\n  Given x\n  When y\n  Then z\n"
                "AC-2\n  Given a\n  When b\n  Then c\n")
        self.assertEqual(R._count_ac(body), 2)

    def test_vague_term_warns(self):  # verifies: REQ-LINTCHECKS-868#CASE-1  # verifies: REQ-LINTCHECKS-868#CASE-3  # verifies: ARCH-LINTCHECKS-025#CASE-4
        body = self._body(contract="- It shall be appropriate and user-friendly.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        vague = [f for f in fs if f["check"] == "vague-term"]
        self.assertEqual(len(vague), 2)            # 'appropriate' + 'user-friendly'
        self.assertEqual(vague[0]["severity"], "warn")

    def test_vague_term_skips_code_spans(self):  # verifies: REQ-LINTCHECKS-868#CASE-2  # verifies: ARCH-LINTCHECKS-025#CASE-4
        # a backticked identifier that happens to contain a vague word is not flagged
        body = self._body(contract="- It shall return `fast_path` within the limit.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "vague-term" for f in fs))

    def test_vague_term_silent_on_precise_bullet(self):
        body = self._body(contract="- It shall return HTTP 200 within 2 seconds.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "vague-term" for f in fs))

    def test_redundant_modal_warns(self):  # verifies: REQ-LINTCHECKS-869#CASE-1  # verifies: REQ-LINTCHECKS-869#CASE-3  # verifies: ARCH-LINTCHECKS-025#CASE-5
        body = self._body(contract="- The system shall log the event and must retry once.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        modal = [f for f in fs if f["check"] == "redundant-modal"]
        self.assertEqual(len(modal), 2)          # 'shall' + 'must'
        self.assertEqual(modal[0]["severity"], "warn")

    def test_redundant_modal_skips_code_spans(self):  # verifies: REQ-LINTCHECKS-869#CASE-2
        # a backticked identifier that happens to contain the word is not flagged
        body = self._body(contract="- `shall_retry` controls whether the job repeats.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "redundant-modal" for f in fs))

    def test_redundant_modal_silent_on_present_tense(self):
        body = self._body(contract="- The system logs the event and retries once.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "redundant-modal" for f in fs))

    # bug: vague-term/redundant-modal hardcoded the literal "contract" label instead of
    # iterating CONTRACT_LABELS, so both checks were dead code on any requirement using
    # the CURRENT `## Description` heading (self.CONTRACT/self.ACCEPT above are the
    # legacy spelling, which is why the tests above never caught this).
    def test_vague_term_fires_under_current_description_heading(self):
        body = ("# T\n\n## Description\n- It shall be appropriate and user-friendly.\n\n"
                "## Cases (= tests)\n- ok.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        vague = [f for f in fs if f["check"] == "vague-term"]
        self.assertEqual(len(vague), 2)            # 'appropriate' + 'user-friendly'

    def test_redundant_modal_fires_under_current_description_heading(self):
        body = ("# T\n\n## Description\n- The system shall log the event and must retry once.\n\n"
                "## Cases (= tests)\n- ok.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        modal = [f for f in fs if f["check"] == "redundant-modal"]
        self.assertEqual(len(modal), 2)            # 'shall' + 'must'


FAKE_CLAUDE = "/usr/bin/claude"   # a `claude` on PATH, so the subprocess mocks are reached


class Translate(unittest.TestCase):  # tested-by: ARCH-TRANSLATE-044  # tested-by: REQ-TRANSLATE-937  # tested-by: REQ-TRANSLATE-938
    RO_BODY = ("# Titlu în română\n\n"
               "> Aici explicăm de ce această cerință există și ce problemă rezolvă.\n\n"
               "## WHAT — Contract (normative)\n"
               "- Sistemul calculează suma `TOTAL` și afișează 2 zecimale.\n\n"
               "## HOW — Acceptance (= tests)\n"
               "- Given un total de 10\n  When se afișează\n  Then arată 10.00\n")
    EN_BODY = ("# English title\n\n"
               "> Here we explain why this requirement exists and what problem it solves.\n\n"
               "## WHAT — Contract (normative)\n"
               "- The system calculates the `TOTAL` sum and shows 2 decimals.\n\n"
               "## HOW — Acceptance (= tests)\n"
               "- Given a total of 10\n  When it is shown\n  Then it reads 10.00\n")

    def _req(self, body, lang=None, status="confirmed"):
        meta = {"status": status}
        if lang:
            meta["lang"] = lang
        return {"meta": meta, "body": body}

    def _tmp_reqs_dir(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_translation_hash_changes_on_title_edit(self):  # verifies: ARCH-TRANSLATE-044#CASE-1  # verifies: REQ-TRANSLATE-937#CASE-2
        # binding_hash() (Contract+Acceptance only) would NOT change here — that is
        # exactly the gap this hash exists to close.
        body_a = self.RO_BODY
        body_b = self.RO_BODY.replace("Titlu în română", "Titlu modificat")
        h_a = R.translation_hash(body_a, R._title(body_a))
        h_b = R.translation_hash(body_b, R._title(body_b))
        self.assertNotEqual(h_a, h_b)
        # sanity: only the title changed, so binding_hash (Contract+Acceptance only)
        # stays THE SAME — proof that reusing it would have missed this edit.
        self.assertEqual(R.binding_hash(body_a), R.binding_hash(body_b))

    def test_map_never_invokes_claude(self):  # verifies: ARCH-TRANSLATE-044#CASE-2  # verifies: REQ-TRANSLATE-937#CASE-1  # verifies: REQ-TRANSLATE-938#CASE-1
        # `map`/`export` must stay fully deterministic and claude-free — they only
        # ever read an already-committed cache file.
        reqs_dir = self._tmp_reqs_dir()
        i18n_dir = os.path.join(reqs_dir, "_i18n")
        os.makedirs(i18n_dir)
        body = self.RO_BODY
        h = R.translation_hash(body, R._title(body))
        with open(os.path.join(i18n_dir, "en.json"), "w", encoding="utf-8") as f:
            json.dump({"REQ-A-001": {"hash": h, "title": "English title", "intent": "I",
                                      "contract": "C", "acceptance": "A"}}, f)
        reqs = {"REQ-A-001": self._req(body)}
        # `shutil` left the engine with the translate writer that used it to find the
        # CLI. Patching subprocess alone is now the whole assertion, and a stronger one:
        # nothing in the engine can start a process at all.
        with mock.patch.object(R.subprocess, "run", side_effect=AssertionError(
                "map must never shell out to claude")):
            data = R._build_map_data(reqs, {})
            R._attach_translations(data, reqs, reqs_dir)
        node = next(n for n in data["nodes"] if n["id"] == "REQ-A-001")
        self.assertEqual(node["i18n"]["en"]["title"], "English title")

    def test_stale_cache_entry_is_dropped_not_served(self):  # verifies: ARCH-TRANSLATE-044#CASE-3  # verifies: REQ-TRANSLATE-938#CASE-2
        reqs_dir = self._tmp_reqs_dir()
        i18n_dir = os.path.join(reqs_dir, "_i18n")
        os.makedirs(i18n_dir)
        with open(os.path.join(i18n_dir, "en.json"), "w", encoding="utf-8") as f:
            json.dump({"REQ-A-001": {"hash": "stale-hash-does-not-match", "title": "Old"}}, f)
        reqs = {"REQ-A-001": self._req(self.RO_BODY)}
        out = R._load_translations(reqs, reqs_dir)
        self.assertNotIn("REQ-A-001", out)

    def test_load_translations_malformed_cache_fails_open(self):  # verifies: REQ-TRANSLATE-938#CASE-3  # bug: load-translations-not-dict-guarded
        reqs_dir = self._tmp_reqs_dir()
        i18n_dir = os.path.join(reqs_dir, "_i18n")
        os.makedirs(i18n_dir)
        with open(os.path.join(i18n_dir, "en.json"), "w", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)   # malformed: not a dict
        reqs = {"REQ-A-001": self._req(self.RO_BODY)}
        out = R._load_translations(reqs, reqs_dir)
        self.assertEqual(out, {})

    def test_translator_version_bump_invalidates_every_entry(self):  # verifies: REQ-TRANSLATE-937#CASE-3
        # The version is folded into the key, so ONE bump retires the whole cache;
        # without it each stale entry would have to be invalidated file by file.
        body = self.RO_BODY
        before = R.translation_hash(body, R._title(body))
        with mock.patch.object(R.i18n, "TRANSLATOR_VERSION", R.TRANSLATOR_VERSION + "-next"):
            after = R.translation_hash(body, R._title(body))
        self.assertNotEqual(before, after)


class LevelRetrofit(unittest.TestCase):  # tested-by: ARCH-LEVELRETROFIT-066  # tested-by: REQ-LEVELRETROFIT-985  # tested-by: REQ-LEVELRETROFIT-986  # tested-by: REQ-LEVELRETROFIT-987
    """`clarify --levels`: propose a V-model rung for a corpus that declares none."""

    HEAD = "---\nid: {id}\nstatus: confirmed\n{extra}layer: {layer}\nowner: Alex\n---\n\n# {id}\n\n"
    CASES = ("## Cases\nCASE-1 - a\n  Given x\n  When y\n  Then z\n\n"
             "CASE-2 - b\n  Given x\n  When y\n  Then z\n\n"
             "CASE-3 - c\n  Given x\n  When y\n  Then z\n")

    def _req(self, rid, layer="feature", extra="", cases=False, eol="\n"):
        body = self.HEAD.format(id=rid, layer=layer, extra=extra)
        body += "## Description\nEvery bullet below is binding.\n- {} does one thing.\n\n".format(rid)
        if cases:
            body += self.CASES
        return body.replace("\n", eol)

    def _repo(self, files, members=None, ac_cover=None):
        # newline='' on purpose: the CRLF case needs a genuinely CRLF file, and the
        # others a genuinely LF one. Python's default translation would erase both.
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        reqs_dir = os.path.join(d, "requirements")
        os.makedirs(reqs_dir, exist_ok=True)
        for name, text in files.items():
            with open(os.path.join(reqs_dir, name), "w", encoding="utf-8", newline="") as f:
                f.write(text)
        reqs = R.load_requirements(reqs_dir)
        return d, R.Workspace(reqs, members or {}, reqs_dir, d, ac_cover=ac_cover or {})

    def _run(self, ws, **kw):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.cmd_levels(ws, **kw)
        return rc, buf.getvalue()

    # ---- REQ-LEVELRETROFIT-985: which rung, and on what evidence ----------
    def test_layer_answers_the_rung_where_the_layer_already_said_so(self):  # verifies: ARCH-LEVELRETROFIT-066#CASE-1  # verifies: REQ-LEVELRETROFIT-985#CASE-1
        _d, ws = self._repo({
            "SYS-A-001.md": self._req("SYS-A-001", layer="need"),
            "AGG-B-002.md": self._req("AGG-B-002", layer="aggregate"),
        })
        got = R._propose_levels(ws.reqs, ws.members, ws.ac_cover)
        self.assertEqual(got["SYS-A-001"][0], "system")
        self.assertIn("need", got["SYS-A-001"][1])
        self.assertEqual(got["AGG-B-002"][0], "architecture")
        self.assertIn("aggregate", got["AGG-B-002"][1])

    def _grouped_req(self, rid):
        """A requirement whose Description carries two bold contract groups — the one
        shape the engine reads as a GROUP, hence `architecture` (ADR-0038)."""
        body = self.HEAD.format(id=rid, layer="feature", extra="")
        body += ("## Description\nEvery bullet below is binding.\n"
                 "**Polling**\n- It polls.\n**Sending**\n- It sends.\n\n") + self.CASES
        return body

    def test_a_group_is_architecture_everything_bound_to_code_is_code(self):  # verifies: REQ-LEVELRETROFIT-985#CASE-2
        # Same layer, same status: the shape decides. Under-specification (no cases) is
        # lint's finding and never moves a behaviour group up a rung.
        _d, ws = self._repo(
            {"REQ-G-000.md": self._grouped_req("REQ-G-000"),
             "REQ-A-001.md": self._req("REQ-A-001", cases=True),
             "REQ-B-002.md": self._req("REQ-B-002", cases=False)},
            members={"REQ-G-000": [("implements", "src/g.py", 1)],
                     "REQ-A-001": [("implements", "src/a.py", 1)],
                     "REQ-B-002": [("implements", "src/b.py", 1)]},
            ac_cover={"REQ-A-001": {"CASE-1": ["t"]}})
        got = R._propose_levels(ws.reqs, ws.members, ws.ac_cover)
        self.assertEqual(got["REQ-G-000"][0], "architecture")
        self.assertIn("--decompose", got["REQ-G-000"][1])
        self.assertEqual(got["REQ-A-001"][0], "code")
        self.assertIn("3 case(s), 1 linked to a test, 1 implementing member(s)", got["REQ-A-001"][1])
        self.assertEqual(got["REQ-B-002"][0], "code")
        self.assertIn("0 case(s)", got["REQ-B-002"][1])

    def test_a_declared_rung_is_never_overruled(self):  # verifies: ARCH-LEVELRETROFIT-066#CASE-3  # verifies: REQ-LEVELRETROFIT-985#CASE-3
        # Shape says `code`; the author said `architecture`. The author wins, and
        # the run reports that there is nothing to propose.
        _d, ws = self._repo(
            {"REQ-A-001.md": self._req("REQ-A-001", extra="level: architecture\n", cases=True)},
            members={"REQ-A-001": [("implements", "src/a.py", 1)]},
            ac_cover={"REQ-A-001": {"CASE-1": ["t"]}})
        self.assertEqual(R._propose_levels(ws.reqs, ws.members, ws.ac_cover), {})
        rc, out = self._run(ws)
        self.assertEqual(rc, 0)
        self.assertIn("already declare a `level:`", out)   # the rung itself is untouched

    # ---- REQ-LEVELRETROFIT-986: writing into somebody else's file ---------
    def test_a_crlf_file_comes_back_crlf(self):  # verifies: REQ-LEVELRETROFIT-986#CASE-1
        _d, ws = self._repo({"REQ-A-001.md": self._req("REQ-A-001", eol="\r\n")})
        rc, _out = self._run(ws, apply_it=True)
        self.assertEqual(rc, 0)
        raw = open(ws.reqs["REQ-A-001"]["path"], "rb").read()
        self.assertEqual(raw.count(b"\r\n"), raw.count(b"\n"))   # no bare LF survived
        self.assertIn(b"level_source: auto\r\n", raw)

    def test_one_block_of_a_module_file_and_only_one(self):  # verifies: REQ-LEVELRETROFIT-986#CASE-2
        mod = (self._req("REQ-A-001", layer="need")
               + "\n\n--------------------\n\n\n"
               + self._req("REQ-B-002", layer="aggregate"))
        _d, ws = self._repo({"REQ-A-001.md": mod})
        rc, _out = self._run(ws, apply_it=True)
        self.assertEqual(rc, 0)
        text = open(os.path.join(ws.reqs_dir, "REQ-A-001.md"), encoding="utf-8").read()
        self.assertIn("id: REQ-A-001\nstatus: confirmed\nlevel: system", text)
        self.assertIn("id: REQ-B-002\nstatus: confirmed\nlevel: architecture", text)
        self.assertEqual(text.count("level_source: auto"), 2)

    def test_a_block_that_already_carries_a_level_is_skipped_not_forced(self):  # verifies: REQ-LEVELRETROFIT-986#CASE-3
        _d, ws = self._repo({"REQ-A-001.md": self._req("REQ-A-001")})
        before = open(ws.reqs["REQ-A-001"]["path"], "rb").read()
        ok, msg = R._apply_level(ws.reqs["REQ-A-001"], "code")
        self.assertTrue(ok)
        ok2, msg2 = R._apply_level(ws.reqs["REQ-A-001"], "architecture")
        self.assertFalse(ok2)
        self.assertIn("no editable frontmatter", msg2)
        after = open(ws.reqs["REQ-A-001"]["path"], "rb").read()
        # written once, not twice: the second call found a `level:` and refused
        self.assertEqual(after.count(b"level: code"), 1)
        self.assertEqual(after.count(b"level_source: auto"), 1)
        self.assertNotIn(b"architecture", after)
        self.assertNotEqual(before, after)

    # ---- REQ-LEVELRETROFIT-987: read-only, and honest about its limits ----
    def test_the_default_run_changes_nothing_on_disk(self):  # verifies: REQ-LEVELRETROFIT-987#CASE-1
        _d, ws = self._repo({"REQ-A-001.md": self._req("REQ-A-001")})
        path = ws.reqs["REQ-A-001"]["path"]
        before = open(path, "rb").read()
        rc, out = self._run(ws)
        self.assertEqual(rc, 0)
        self.assertEqual(open(path, "rb").read(), before)
        self.assertIn("Nothing written", out)
        self.assertIn("REQ-A-001", out)

    def test_apply_writes_family_placeholders_and_satisfies_edges(self):  # verifies: REQ-LEVELRETROFIT-987#CASE-2
        _d, ws = self._repo({
            "JS-A-001.md": self._req("JS-A-001"),
            "JS-B-002.md": self._req("JS-B-002"),
            "JS-C-003.md": self._req("JS-C-003"),
            "AI-C-003.md": self._req("AI-C-003", extra="satisfies: [SYS-OWN-001]\n"),
            "SYS-OWN-001.md": self._req("SYS-OWN-001", layer="need"),
            "MT4-D-004.md": self._req("MT4-D-004"),                      # a prefix of one: no family
            "DRAFT-E-005.md": self._req("DRAFT-E-005").replace("status: confirmed", "status: draft"),
        })
        rc, out = self._run(ws)            # read-only: the plan is printed, nothing written
        self.assertEqual(rc, 0)
        self.assertIn("ARCH-JS-001", out)
        self.assertIn("Nothing written", out)
        self.assertFalse(os.path.exists(os.path.join(ws.reqs_dir, "ARCH-JS-001.md")))
        rc, out = self._run(ws, apply_it=True)
        self.assertEqual(rc, 0)
        reread = R.load_requirements(ws.reqs_dir)
        cap = reread["ARCH-JS-001"]["meta"]
        self.assertEqual((cap["status"], cap["level"], cap["layer"], cap["level_source"]),
                         ("draft", "architecture", "feature", "auto"))
        self.assertEqual(cap["satisfies"], [R.SYS_PLACEHOLDER_ID])      # the apex, init's own hole
        self.assertEqual(reread[R.SYS_PLACEHOLDER_ID]["meta"]["layer"], "need")
        for rid in ("JS-A-001", "JS-B-002", "JS-C-003"):
            self.assertEqual(reread[rid]["meta"]["level"], "code")
            self.assertEqual(reread[rid]["meta"]["satisfies"], ["ARCH-JS-001"])
        self.assertEqual(reread["AI-C-003"]["meta"]["satisfies"], ["SYS-OWN-001"])   # kept as is
        self.assertNotIn("ARCH-AI-001", reread)                      # no edge needed: no hole minted
        self.assertNotIn("satisfies", reread["SYS-OWN-001"]["meta"])  # a need satisfies nothing
        # a prefix below LEVEL_FAMILY_MIN shares one placeholder instead of minting ARCH-MT4-001
        self.assertNotIn("ARCH-MT4-001", reread)
        self.assertEqual(reread["MT4-D-004"]["meta"]["satisfies"], [R.ARCH_SHARED_ID])
        # an auto-extracted draft stub is never given an edge, and DRAFT is not a family
        self.assertNotIn("satisfies", reread["DRAFT-E-005"]["meta"])
        self.assertNotIn("ARCH-DRAFT-001", reread)
        self.assertIn("`depends_on` is never read", out)

    def test_a_second_apply_writes_nothing_new(self):  # verifies: REQ-LEVELRETROFIT-987#CASE-2
        _d, ws = self._repo({"JS-A-001.md": self._req("JS-A-001")})
        self._run(ws, apply_it=True)
        def snap():
            return {n: open(os.path.join(ws.reqs_dir, n), "rb").read()
                    for n in sorted(os.listdir(ws.reqs_dir))}
        before = snap()
        self.assertIn(R.ARCH_SHARED_ID + ".md", before)      # one JS member: below the floor
        self.assertIn(R.SYS_PLACEHOLDER_ID + ".md", before)
        ws2 = R.Workspace(R.load_requirements(ws.reqs_dir), {}, ws.reqs_dir, _d, ac_cover={})
        _rc, out = self._run(ws2, apply_it=True)
        self.assertIn("nothing to propose", out)
        self.assertEqual(snap(), before)

    def test_a_grouped_requirement_is_told_which_command_builds_its_code_rung(self):  # verifies: REQ-LEVELRETROFIT-987#CASE-3
        _d, ws = self._repo({"REQ-G-000.md": self._grouped_req("REQ-G-000"),
                             "REQ-A-001.md": self._req("REQ-A-001")})
        _rc, out = self._run(ws)
        self.assertIn("architecture   REQ-G-000", out)
        self.assertIn("1 requirement(s) carry contract groups", out)
        self.assertIn("--decompose --apply", out)

    def test_apply_writes_the_rung_and_the_marker(self):  # verifies: ARCH-LEVELRETROFIT-066#CASE-2
        _d, ws = self._repo({
            "SYS-A-001.md": self._req("SYS-A-001", layer="need"),
            "REQ-B-002.md": self._req("REQ-B-002"),
        })
        rc, _out = self._run(ws, apply_it=True)
        self.assertEqual(rc, 0)
        reread = R.load_requirements(ws.reqs_dir)
        self.assertEqual(reread["SYS-A-001"]["meta"]["level"], "system")
        self.assertEqual(reread["REQ-B-002"]["meta"]["level"], "code")
        for r in reread.values():
            self.assertEqual(r["meta"].get("level_source"), "auto")


class LayerMismatchLint(unittest.TestCase):  # tested-by: ARCH-LINTCHECKS-025  # tested-by: REQ-LINTCHECKS-867
    """`bus` is defined by fan-in and nothing checked it: a requirement with 0
    dependents and 12 dependencies was labelled bus and read as a foundation."""

    def _req(self, layer, deps):
        return {"meta": {"layer": layer, "depends_on": deps},
                "body": _ac_body(acceptance="AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n"
                                            "  Then d\nAC-3\n  Given e\n  Then f")}

    def _checks(self, findings):
        return [f["check"] for f in findings]

    def test_bus_with_no_dependents_and_many_deps_warns(self):  # verifies: REQ-LINTCHECKS-867#CASE-3
        fs = R.lint_requirement("A-ROOF-001", self._req("bus", ["A-1", "B-2", "C-3"]), None, 0)
        self.assertIn("layer-mismatch", self._checks(fs))

    def test_bus_with_dependents_is_clean(self):
        fs = R.lint_requirement("A-BUS-001", self._req("bus", ["A-1", "B-2", "C-3"]), None, 4)
        self.assertNotIn("layer-mismatch", self._checks(fs))

    def test_aggregate_layer_is_not_flagged(self):
        fs = R.lint_requirement("A-AGG-001", self._req("aggregate", ["A-1", "B-2", "C-3"]), None, 0)
        self.assertNotIn("layer-mismatch", self._checks(fs))

    def test_skipped_when_fanin_unknown(self):  # verifies: REQ-LINTCHECKS-867#CASE-4
        fs = R.lint_requirement("A-ROOF-002", self._req("bus", ["A-1", "B-2", "C-3"]))
        self.assertNotIn("layer-mismatch", self._checks(fs))

    def test_aggregate_is_a_valid_layer(self):
        self.assertIn("aggregate", R.VALID_LAYER)


class Review(unittest.TestCase):  # tested-by: ARCH-REVIEW-022  # tested-by: REQ-REVIEW-906
    BODY = ("---\nid: A-R-001\nstatus: confirmed\nlayer: feature\n---\n\n"
            "# Thing\n\n> WHY: it does the thing for a reason that matters to readers here.\n\n"
            "## WHAT — Contract\n- It shall do x.\n- It shall do y.\n\n"
            "## HOW — Acceptance\n- x happens.\n")

    def _seed(self, d):
        _write(os.path.join(d, "A-R-001.md"), self.BODY)
        _write(os.path.join(d, "a.py"), tag("A-R-001") + "\n")

    def _review(self, reqs, one=None):
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_review(reqs, one)
        return buf.getvalue()

    def test_unknown_id_fails_closed(self):  # bug: review-unknown-id-silent-empty-plan  # verifies: REQ-REVIEW-906#CASE-6
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_review(R.load_requirements(d), "TYPO-X-999")
            self.assertEqual(rc, 1, "an unknown single id must exit 1, not emit an empty plan")
            self.assertIn("no requirement with id", buf.getvalue())

    def test_plan_structure_and_coverage(self):  # verifies: REQ-REVIEW-906#CASE-2  # verifies: REQ-REVIEW-906#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            plan = json.loads(self._review(R.load_requirements(d)))
            self.assertEqual(plan["coverage_summary"], {"total_requirements": 1, "requirements_in_plan": 1})
            self.assertEqual([c["key"] for c in plan["categories"]],
                             ["untestable-contract", "why-restates-title", "acceptance-doesnt-cover-contract"])
            self.assertIn("suggested_rewrite", plan["finding_contract"])
            anchors = plan["requirements"][0]["anchors"]
            self.assertEqual(anchors["contract_clauses"], 2)
            self.assertTrue(anchors["more_contract_than_acceptance"])     # 2 contract > 1 AC

    def test_review_is_byte_deterministic(self):  # verifies: REQ-REVIEW-906#CASE-1  # verifies: REQ-REVIEW-906#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            reqs = R.load_requirements(d)
            self.assertEqual(self._review(reqs), self._review(reqs))

    def test_gate_ignores_ai_sidecar(self):  # DETERMINISM WALL — verifies: ARCH-REVIEW-022  # verifies: REQ-REVIEW-906#CASE-4  # verifies: REQ-REVIEW-906#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)

            def gate():
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
                return code, buf.getvalue()

            before = gate()
            _write(os.path.join(d, "_ai_review.md"),
                   "# AI — advisory (non-deterministic). NOT a gate.\n- something\n")
            self.assertEqual(before, gate())   # check never reads the AI sidecar


class PlanReach(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009  # tested-by: REQ-CANDIDATES-826  # tested-by: REQ-CANDIDATES-827
    def _plan(self, d):
        rd = os.path.join(d, "requirements")
        reqs = R.load_requirements(rd)
        members = R.scan_members(d, rd)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(R.Workspace(reqs, members, rd, d), None)
        return json.loads(buf.getvalue())

    def test_unparsed_languages_are_candidates_and_tests_are_flagged(self):  # verifies: REQ-CANDIDATES-826#CASE-4  # verifies: REQ-CANDIDATES-826#CASE-5  # verifies: REQ-CANDIDATES-827#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "main.go"), "package main" + chr(10) + "func main() {}" + chr(10))
            _write(os.path.join(d, "zlib.h"), "int deflate(int x);" + chr(10))
            _write(os.path.join(d, "Dockerfile"), "FROM scratch" + chr(10))
            _write(os.path.join(d, "tests", "test_x.py"), "def test_a():" + chr(10) + "    pass" + chr(10))
            _write(os.path.join(d, "lib.py"), '"""mod."""' + chr(10) + "def f(a):" + chr(10) + "    return a" + chr(10))
            plan = self._plan(d)
            by_file = {c["files"][0]: c for c in plan["candidates"]}
            for f in ("main.go", "zlib.h", "Dockerfile", "tests/test_x.py", "lib.py"):
                self.assertIn(f, by_file, f)
            self.assertEqual(by_file["main.go"]["signatures"], [])
            self.assertTrue(by_file["tests/test_x.py"]["is_test"])
            self.assertFalse(by_file["lib.py"]["is_test"])
            self.assertTrue(any(x.endswith("def f(a)") for x in by_file["lib.py"]["signatures"]))

    def test_class_methods_are_signatures(self):  # verifies: REQ-CANDIDATES-826#CASE-6
        facts = R._py_facts("class Client:" + chr(10) + "    def get(self, url):" + chr(10) + "        pass" + chr(10)
                            + "    def _hidden(self):" + chr(10) + "        pass" + chr(10))
        self.assertIn("class Client", facts["signatures"])
        self.assertIn("def Client.get(url)", facts["signatures"])
        self.assertNotIn("def Client._hidden()", facts["signatures"])

    def test_is_test_path_conventions(self):
        for p in ("tests/x.py", "src/__tests__/a.ts", "pkg/foo_test.go", "web/app.spec.ts", "test_core.py"):
            self.assertTrue(R._is_test_path(p), p)
        for p in ("src/core.py", "lib/testing_utils_guide.md", "attest.py"):
            self.assertFalse(R._is_test_path(p), p)


class DraftObservedSurface(unittest.TestCase):  # tested-by: ARCH-EXTRACT-008  # tested-by: REQ-EXTRACT-851
    def test_where_lists_signatures_contract_stays_todo(self):  # verifies: REQ-EXTRACT-851#CASE-4  # verifies: REQ-EXTRACT-851#CASE-5
        with tempfile.TemporaryDirectory() as d:
            code = os.path.join(d, "code")
            _write(os.path.join(code, "svc.py"),
                   '"""Talks to the API."""' + chr(10) + "def fetch(url):" + chr(10) + "    pass" + chr(10)
                   + "def parse(text, strict):" + chr(10) + "    pass" + chr(10))
            _write(os.path.join(code, "raw.go"), "package raw" + chr(10))
            rd = os.path.join(d, "requirements")
            with redirect_stdout(io.StringIO()):
                R.cmd_extract(R.Workspace({}, {}, rd, code))
            with open(os.path.join(rd, "DRAFT-SVC.md"), encoding="utf-8") as f:
                svc = f.read()
            where = svc.split("## Context")[1]
            self.assertIn("`def fetch(url)`", where)
            self.assertIn("`def parse(text, strict)`", where)
            self.assertIn("module: Talks to the API.", where)
            self.assertIn("- TODO: the observed behavior", svc.split("## Description")[1].split("##")[0])
            with open(os.path.join(rd, "DRAFT-RAW.md"), encoding="utf-8") as f:
                self.assertNotIn("Observed surface", f.read())     # no parser for Go: no hint, no noise


class StatementSize(unittest.TestCase):  # tested-by: ARCH-ATOMICITY-049  # tested-by: REQ-ATOMICITY-824  # tested-by: REQ-ATOMICITY-825
    """The `statement-size` heuristic: measured per CLAUSE, advisory, and deliberately
    blind to atomicity. The blindness is asserted, not just documented — see AC-6."""
    CONTRACT = "## WHAT — Contract (normative)"
    ACCEPT = "## HOW — Acceptance (= tests)"

    def _body(self, contract):
        return "# T\n\n{}\n{}\n{}\n- ok.\n- ok.\n- ok.\n".format(
            self.CONTRACT, contract, self.ACCEPT)

    def _findings(self, contract, exempt=None):
        meta = {"status": "confirmed"}
        if exempt:
            meta["lint_exempt"] = exempt
        r = {"meta": meta, "body": self._body(contract)}
        return R.lint_requirement("REQ-X-001", r)

    @staticmethod
    def _words(n, word="alpha"):
        return " ".join([word] * n)

    def test_clause_over_the_threshold_is_reported_once(self):  # verifies: ARCH-ATOMICITY-049#CASE-1  # verifies: REQ-ATOMICITY-824#CASE-4  # verifies: REQ-ATOMICITY-824#CASE-5  # verifies: REQ-ATOMICITY-825#CASE-2
        fs = self._findings("- {}.\n".format(self._words(155)))
        hits = [f for f in fs if f["check"] == "statement-size"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["severity"], "warn")          # advisory: never an error
        self.assertEqual(hits[0]["clause_n"], 1)
        self.assertIn("155 words", hits[0]["detail"])

    def test_clause_under_the_threshold_is_silent(self):  # verifies: ARCH-ATOMICITY-049#CASE-2
        fs = self._findings("- {}.\n".format(self._words(140)))
        self.assertNotIn("statement-size", [f["check"] for f in fs])

    def test_a_backticked_span_counts_as_one_word(self):  # verifies: ARCH-ATOMICITY-049#CASE-3  # verifies: REQ-ATOMICITY-825#CASE-3
        # 20 plain words + one 60-word code span = 21 counted words, well under the ceiling.
        clause = "- {} `{}`.\n".format(self._words(20), self._words(140, "code"))
        self.assertEqual(len(clause.split()), 161)              # raw split would trip the ceiling
        self.assertEqual(R._clause_words(clause[2:]), 21)      # collapsed count does not
        self.assertNotIn("statement-size", [f["check"] for f in self._findings(clause)])

    def test_a_nested_sub_bullet_is_its_own_clause(self):  # verifies: ARCH-ATOMICITY-049#CASE-4  # verifies: REQ-ATOMICITY-825#CASE-4
        contract = "- {}.\n  - {}.\n".format(self._words(40), self._words(155))
        hits = [f for f in self._findings(contract) if f["check"] == "statement-size"]
        self.assertEqual(len(hits), 1)                         # the parent is not flagged
        self.assertEqual(hits[0]["clause_n"], 2)               # the sub-bullet is

    def test_lint_exempt_silences_the_check(self):  # verifies: ARCH-ATOMICITY-049#CASE-5  # verifies: REQ-ATOMICITY-824#CASE-6
        contract = "- {}.\n".format(self._words(155))
        self.assertIn("statement-size", [f["check"] for f in self._findings(contract)])
        fs = self._findings(contract, exempt=["statement-size"])   # frontmatter yields a real list
        self.assertNotIn("statement-size", [f["check"] for f in fs])

    def test_a_short_clause_with_two_obligations_passes(self):  # verifies: ARCH-ATOMICITY-049#CASE-6  # verifies: REQ-ATOMICITY-824#CASE-2  # verifies: REQ-ATOMICITY-825#CASE-1
        # The epistemic limit, asserted as behaviour: this clause is NOT atomic, and the
        # check passes it anyway. Passing proves nothing about atomicity — a future change
        # that made this fail would be claiming a determination the engine cannot make.
        contract = ("- The service issues a token on valid credentials, and the service "
                    "revokes it on logout.\n")
        self.assertLess(R._clause_words(contract[2:]), R.LINT_STATEMENT_WORDS)
        self.assertNotIn("statement-size", [f["check"] for f in self._findings(contract)])

    def test_a_glossary_comment_is_not_a_clause(self):  # verifies: REQ-ATOMICITY-825#CASE-6
        # _prose_lint does not skip HTML comments; _contract_clauses must, or the template's
        # own glossary block would be measured as a clause.
        contract = "<!-- {} -->\n- short.\n".format(self._words(160))
        self.assertEqual([n for n, _ in R._contract_clauses(self._body(contract))], [1])
        self.assertNotIn("statement-size", [f["check"] for f in self._findings(contract)])

    def test_wrapped_clause_is_joined_before_counting(self):  # verifies: REQ-ATOMICITY-825#CASE-7
        # The reason this check cannot reuse _prose_lint: these files wrap near 95 columns,
        # so an 80-word clause reaches the per-line checks as six ~13-word lines.
        words = self._words(155).split()
        wrapped = "- " + "\n  ".join(" ".join(words[i:i + 13]) for i in range(0, 155, 13)) + ".\n"
        self.assertTrue(max(len(l.split()) for l in wrapped.splitlines()) < 25)
        hits = [f for f in self._findings(wrapped) if f["check"] == "statement-size"]
        self.assertEqual(len(hits), 1)


class Decompose(unittest.TestCase):  # tested-by: ARCH-DECOMPOSE-050  # tested-by: REQ-DECOMPOSE-837  # tested-by: REQ-DECOMPOSE-838  # tested-by: REQ-DECOMPOSE-839
    """`lint --decompose`: opt-in, writes one draft per statement-size finding, never
    touches the parent, and is a no-op on re-run."""
    CONTRACT = "## WHAT — Contract (normative)"
    ACCEPT = "## HOW — Acceptance (= tests)"

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.reqs_dir = os.path.join(self.tmp, "requirements")
        os.makedirs(self.reqs_dir)
        self.long = " ".join(["alpha"] * 155)
        self.body = "# T\n\n{}\n- {}.\n{}\n- ok.\n- ok.\n- ok.\n".format(
            self.CONTRACT, self.long, self.ACCEPT)
        self.parent = os.path.join(self.reqs_dir, "REQ-AUTH-012.md")
        _write(self.parent, "---\nid: REQ-AUTH-012\nstatus: confirmed\n---\n" + self.body)
        self.reqs = {"REQ-AUTH-012": {
            "meta": {"status": "confirmed", "layer": "feature", "owner": "Ana"},
            "body": self.body}}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _lint(self, reqs_dir=None, **kw):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_lint(R.Workspace(self.reqs, None, reqs_dir), **kw)
        return code, buf.getvalue()

    def _created(self):
        return sorted(f for f in os.listdir(self.reqs_dir) if f != "REQ-AUTH-012.md")

    def test_default_run_reports_but_writes_nothing(self):  # verifies: ARCH-DECOMPOSE-050#CASE-1  # verifies: REQ-DECOMPOSE-837#CASE-1  # verifies: REQ-LINT-863#CASE-2
        code, out = self._lint()
        self.assertIn("statement-size", out)
        self.assertEqual(self._created(), [])          # the hook and CI run this path
        self.assertEqual(code, 0)

    def test_decompose_creates_one_draft_depending_on_the_parent(self):  # verifies: ARCH-DECOMPOSE-050#CASE-2  # verifies: REQ-DECOMPOSE-837#CASE-2  # verifies: REQ-DECOMPOSE-838#CASE-1  # verifies: REQ-DECOMPOSE-838#CASE-2
        self._lint(decompose=True, reqs_dir=self.reqs_dir)
        made = self._created()
        self.assertEqual(len(made), 1)
        text = open(os.path.join(self.reqs_dir, made[0]), encoding="utf-8").read()
        self.assertIn("status: draft", text)
        self.assertIn("depends_on: [REQ-AUTH-012]", text)
        self.assertIn(self.long, text)                 # the clause is carried over verbatim

    def test_the_parent_is_never_modified(self):  # verifies: ARCH-DECOMPOSE-050#CASE-3  # verifies: REQ-DECOMPOSE-839#CASE-1
        before = open(self.parent, "rb").read()
        self._lint(decompose=True, reqs_dir=self.reqs_dir)
        self.assertEqual(open(self.parent, "rb").read(), before)

    def test_the_draft_records_that_the_split_was_by_word_count(self):  # verifies: ARCH-DECOMPOSE-050#CASE-4  # verifies: REQ-DECOMPOSE-839#CASE-2  # verifies: REQ-DECOMPOSE-839#CASE-3
        _, out = self._lint(decompose=True, reqs_dir=self.reqs_dir)
        text = open(os.path.join(self.reqs_dir, self._created()[0]), encoding="utf-8").read()
        self.assertIn("WORD COUNT, never by obligation", text)
        self.assertIn("word count, not by obligation", out)   # and on stdout

    def test_the_id_takes_the_next_free_corpus_number(self):  # verifies: ARCH-DECOMPOSE-050#CASE-5  # verifies: REQ-DECOMPOSE-838#CASE-3
        _write(os.path.join(self.reqs_dir, "REQ-ZZ-049.md"), "---\nid: REQ-ZZ-049\n---\n")
        self._lint(decompose=True, reqs_dir=self.reqs_dir)
        self.assertIn("REQ-AUTH-050.md", self._created())

    def test_rerunning_skips_the_same_clause(self):  # verifies: ARCH-DECOMPOSE-050#CASE-6  # verifies: REQ-DECOMPOSE-839#CASE-4
        self._lint(decompose=True, reqs_dir=self.reqs_dir)
        made = self._created()
        stamp = open(os.path.join(self.reqs_dir, made[0]), "rb").read()
        _, out = self._lint(decompose=True, reqs_dir=self.reqs_dir)
        self.assertIn("skipped", out)
        self.assertEqual(self._created(), made)        # no second file under a fresh number
        self.assertEqual(open(os.path.join(self.reqs_dir, made[0]), "rb").read(), stamp)

    def test_decompose_without_reqs_dir_writes_nothing(self):
        code, out = self._lint(decompose=True)         # defensive: no directory, no write
        self.assertIn("statement-size", out)
        self.assertEqual(self._created(), [])
        self.assertEqual(code, 0)

    def test_already_decomposed_skips_undecodable_sibling(self):  # bug: decompose-except-oserror-only
        _write(os.path.join(self.reqs_dir, "REQ-AUTH-013.md"), "status: draft\n")
        bad = os.path.join(self.reqs_dir, "REQ-BAD-014.md")
        with open(bad, "wb") as f:
            f.write(b"\xff\xfe\x00bad utf-8 \x80\x81")
        # must not raise UnicodeDecodeError; simply skip the undecodable sibling
        self.assertFalse(R._already_decomposed(self.reqs_dir, "REQ-AUTH-012", 1))


class OversizeUnify(unittest.TestCase):  # tested-by: ARCH-DECOMPOSE-050  # tested-by: ARCH-NEXT-013  # tested-by: REQ-DECOMPOSE-839
    """The shared `_oversize` predicate: `next`'s Granularity bucket and
    `lint_requirement`'s `ac-count-high` check must report the identical id set for the
    same corpus -- same threshold (LINT_AC_MAX, unchanged), same LINT_STATUSES scope
    (drafts excluded), same `lint_exempt: [ac-count-high]` honoring. Also covers
    `--decompose`'s ac-count-high triage-stub path, extended alongside the predicate."""
    ACCEPT = "## HOW — Acceptance (= tests)"

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.reqs_dir = os.path.join(self.tmp, "requirements")
        os.makedirs(self.reqs_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _body(self, n):
        return "# T\n\n{}\n{}".format(
            self.ACCEPT, "".join("- AC {}.\n".format(i) for i in range(n)))

    def _granularity_ids(self, out):
        m = re.search(r"Granularity \(\d+\)\n((?:  .+\n)+)", out)
        ids = set()
        if m:
            for line in m.group(1).splitlines():
                mm = re.match(r"  (\S+)   \(", line)
                if mm:
                    ids.add(mm.group(1))
        return ids

    def test_next_and_lint_agree_on_ac_count_high_set(self):
        reqs = {}
        for n in range(5, 10):
            reqs["REQ-N{}-001".format(n)] = {
                "meta": {"status": "confirmed", "layer": "feature"},
                "body": self._body(n)}
            reqs["REQ-N{}X-002".format(n)] = {
                "meta": {"status": "confirmed", "layer": "feature",
                         "lint_exempt": ["ac-count-high"]},
                "body": self._body(n)}
        members = {rid: [("implements", "x.py", 1), ("tested-by", "t.py", 1)] for rid in reqs}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_next(R.Workspace(reqs, members), True)
        next_ids = self._granularity_ids(buf.getvalue())
        lint_ids = {rid for rid, r in reqs.items()
                    if "ac-count-high" in [f["check"] for f in R.lint_requirement(rid, r)]}
        self.assertEqual(next_ids, lint_ids)
        # a bug that leaves both sets empty (or both wrong in the same way) would still
        # pass the equality check above -- pin the actual expected members too.
        self.assertEqual(lint_ids, {"REQ-N8-001", "REQ-N9-001"})

    def test_oversize_predicate_excludes_draft_status(self):
        r = {"meta": {"status": "draft", "layer": "feature"}, "body": self._body(9)}
        self.assertFalse(R._oversize("REQ-DRAFT-001", r))
        reqs = {"REQ-DRAFT-001": r}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_next(R.Workspace(reqs, {}), True)
        self.assertNotIn("Granularity", buf.getvalue())

    def test_decompose_covers_statement_size_only(self):  # verifies: ARCH-DECOMPOSE-050#CASE-7  # verifies: REQ-DECOMPOSE-839#CASE-5
        """`--decompose` must NOT scaffold anything for an over-LINT_AC_MAX parent.
        An `ac-count-high` triage-stub path existed briefly and was removed before it
        shipped: it was unreachable in the live corpus (0 non-exempt oversize
        requirements) and ADR-0022, adopted in the same change, forbids shipping on a
        signal with no fire rate and no confirmation sample. This test is the tripwire
        against re-adding it without meeting that bar."""
        body = self._body(8)
        _write(os.path.join(self.reqs_dir, "REQ-BIG-012.md"),
               "---\nid: REQ-BIG-012\nstatus: confirmed\n---\n" + body)
        reqs = {"REQ-BIG-012": {
            "meta": {"status": "confirmed", "layer": "feature", "owner": "Ana"},
            "body": body}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_lint(R.Workspace(reqs, None, self.reqs_dir), decompose=True)
        out = buf.getvalue()
        # the finding is still REPORTED (warn-only check untouched) ...
        self.assertIn("ac-count-high", out)
        # ... but nothing is written for it.
        self.assertEqual(
            sorted(f for f in os.listdir(self.reqs_dir) if f != "REQ-BIG-012.md"), [],
            "--decompose scaffolded a file for an ac-count-high finding; that path was "
            "removed on purpose (ADR-0022) and must not come back without its bar met")
        self.assertNotIn("triage stub", out)

    def test_no_ac_count_high_decompose_symbols_remain(self):
        """Grep-level guard: the removed path leaves no orphan behind."""
        src = open(R.__file__, encoding="utf-8").read()
        for sym in ("_decompose_ac_count_high", "AC_COUNT_TRIAGE_TEMPLATE"):
            self.assertNotIn(sym, src, "{} was reintroduced".format(sym))


class LiveCorpusReachability(unittest.TestCase):  # tested-by: ARCH-DECOMPOSE-050
    """Skeptic-stage closure: the OversizeUnify tests above run against SYNTHETIC
    corpora that manufacture a non-exempt over-threshold parent this repo does not
    actually have, so they stay green even if ARCH-DECOMPOSE-050's prose overclaims
    what `--decompose` reaches in THIS corpus. This test reads the real corpus and
    pins the honest-narrowing sentence in place: `--decompose` covers `statement-size`
    only, and `ac-count-high` fires on nobody here."""

    def test_arch_decompose_050_prose_matches_live_corpus_reachability(self):
        real_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "requirements")
        reqs = R.load_requirements(real_dir)
        non_exempt_over = [rid for rid, r in reqs.items() if R._oversize(rid, r)]
        text = open(os.path.join(real_dir, "ARCH-DECOMPOSE-050.md"), encoding="utf-8").read()
        self.assertEqual(
            non_exempt_over, [],
            "the live corpus now has a non-exempt oversize requirement ({}) -- "
            "ARCH-DECOMPOSE-050's reachability prose is stale".format(non_exempt_over))
        self.assertIn("not currently reachable", text)


class FanOut(unittest.TestCase):  # tested-by: ARCH-FANOUT-052  # tested-by: REQ-FANOUT-852
    """Hierarchy breadth on the satisfies graph, leaves exempt."""
    CONTRACT = "## WHAT — Contract (normative)"
    ACCEPT = "## HOW — Acceptance (= tests)"

    def _body(self):
        return "# T\n\n{}\n- `x` does one thing.\n{}\n- a.\n- b.\n- c.\n".format(
            self.CONTRACT, self.ACCEPT)

    def _checks(self, children):
        r = {"meta": {"status": "confirmed"}, "body": self._body()}
        return [f["check"] for f in R.lint_requirement("REQ-P-001", r, children=children)]

    def _level_checks(self, level, children):
        r = {"meta": {"status": "confirmed", "level": level}, "body": self._body()}
        return [f for f in R.lint_requirement("REQ-P-001", r, children=children)
                if f["check"] == "fan-out"]

    def test_too_few_children_is_reported_without_a_declared_level(self):
        # The fallback band (5-20) still carries a floor: a repo that never adopts the
        # `level:` axis must see exactly what it saw before (ADR-0019's doubly-opt-in rule).
        fs = [f for f in R.lint_requirement(
            "REQ-P-001", {"meta": {"status": "confirmed"}, "body": self._body()},
            children=3) if f["check"] == "fan-out"]
        self.assertEqual(len(fs), 1)
        self.assertEqual(fs[0]["severity"], "warn")
        self.assertIn("too few", fs[0]["detail"])

    # Per-level ceilings, with no floor at either declared level. A blind review of all
    # nine findings the old uniform floor produced confirmed 0 of 9 as real, and three of
    # them had appeared *because* the corpus was correctly cleaned up — so the floor was
    # dropped rather than retuned. See ARCH-FANOUT-052 and CHANGELOG v3.1.0.
    def test_architecture_has_no_floor(self):  # verifies: ARCH-FANOUT-052#CASE-1  # verifies: REQ-FANOUT-852#CASE-5
        self.assertEqual(self._level_checks("architecture", 3), [])

    def test_architecture_ceiling_is_thirty(self):  # verifies: ARCH-FANOUT-052#CASE-3  # verifies: REQ-FANOUT-852#CASE-4
        self.assertEqual(self._level_checks("architecture", 30), [])
        fs = self._level_checks("architecture", 32)
        self.assertEqual(len(fs), 1)
        self.assertIn("too many", fs[0]["detail"])
        self.assertIn("over 30", fs[0]["detail"])

    def test_system_ceiling_is_ten(self):  # verifies: ARCH-FANOUT-052#CASE-6  # verifies: REQ-FANOUT-852#CASE-4
        self.assertEqual(self._level_checks("system", 10), [])
        fs = self._level_checks("system", 11)
        self.assertEqual(len(fs), 1)
        self.assertIn("over 10", fs[0]["detail"])
        # the same count is silent one level down — that is the point of per-level bands
        self.assertEqual(self._level_checks("architecture", 11), [])

    def test_a_count_inside_the_band_is_silent(self):  # verifies: ARCH-FANOUT-052#CASE-2
        self.assertNotIn("fan-out", self._checks(8))

    def test_too_many_children_is_reported(self):  # verifies: ARCH-FANOUT-052#CASE-3  # verifies: REQ-FANOUT-852#CASE-1
        fs = [f for f in R.lint_requirement(
            "REQ-P-001", {"meta": {"status": "confirmed"}, "body": self._body()},
            children=25) if f["check"] == "fan-out"]
        self.assertEqual(len(fs), 1)
        self.assertIn("too many", fs[0]["detail"])

    def test_a_leaf_is_never_reported(self):  # verifies: ARCH-FANOUT-052#CASE-4  # verifies: REQ-FANOUT-852#CASE-3
        self.assertNotIn("fan-out", self._checks(0))

    def test_a_corpus_with_no_satisfies_edges_reports_nothing(self):  # verifies: ARCH-FANOUT-052#CASE-5
        # `children` omitted entirely is the shape cmd_lint passes for a corpus that has
        # never adopted `satisfies:` — the check must stay silent there.
        self.assertNotIn("fan-out", self._checks(None))

    def test_the_band_is_read_against_satisfies_not_depends_on(self):  # verifies: REQ-FANOUT-852#CASE-2
        # depends_on out-degree in this corpus maxes out at 3; a 5-20 band read against it
        # would flag every requirement. Guard the axis, not just the numbers.
        self.assertEqual((R.LINT_FANOUT_MIN, R.LINT_FANOUT_MAX), (5, 20))


class NoShrinkVerb(unittest.TestCase):  # tested-by: ARCH-DECOMPOSE-050  # tested-by: ARCH-RETIRE-064
    """ADR-0027 (superseding ADR-0021): the corpus may shrink, through exactly two
    sanctioned paths — `_wipe`, which resets everything, and `_remove_requirement_block`,
    which `retire --delete` calls after printing the blast radius and refusing while
    anything still depends on the requirement.

    This test is trivially green the day it is written — that is the point. It
    fails the moment a second delete path appears, which routes the author back
    to docs/adr/0021-corpus-grows-only-by-design.md to revisit the decision
    deliberately instead of drifting past it."""

    _DELETE_CALLS = ("os.remove", "os.unlink", "shutil.rmtree", "os.rename", "shutil.move")

    def _enclosing_def(self, lines, idx):
        """Name of the innermost top-level `def` above line *idx*, or None."""
        for j in range(idx, -1, -1):
            if lines[j].startswith("def "):
                return lines[j][4:].split("(")[0]
        return None

    def test_delete_calls_live_only_in_wipe(self):
        src = open(R.__file__, encoding="utf-8").read().split("\n")
        offenders = []
        for i, line in enumerate(src):
            code = line.split("#", 1)[0]           # ignore mentions in comments
            if not any(call + "(" in code for call in self._DELETE_CALLS):
                continue
            owner = self._enclosing_def(src, i)
            if owner not in ("_wipe", "_remove_requirement_block"):   # ADR-0027
                offenders.append("{}:{} in {}() -> {}".format(
                    os.path.basename(R.__file__), i + 1, owner, line.strip()))
        self.assertEqual(offenders, [], "\n".join(
            ["a third requirement-removing path appeared; ADR-0027 sanctions exactly two",
             "(_wipe and _remove_requirement_block). Adding one is allowed, but it",
             "supersedes that record — write the new ADR first, then update this test:"]
            + offenders))


class ExtractRungs(unittest.TestCase):  # tested-by: REQ-EXTRACT-981
    """ADR-0030: extraction drafts a pyramid, and marks every rung it invented."""

    def _extract(self, d):
        rq = os.path.join(d, "requirements")
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_extract(R.Workspace(R.load_requirements(rq), {}, rq, d))
        return rq, buf.getvalue()

    @staticmethod
    def _meta(path):
        with open(path, encoding="utf-8") as f:
            return R.parse_frontmatter(f.read())[0]

    def test_a_code_draft_asserts_its_rung(self):  # verifies: REQ-EXTRACT-981#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "src", "thing.py"), "def a():\n    return 1\n")
            rq, _ = self._extract(d)
            drafts = [f for f in os.listdir(rq) if f.startswith("DRAFT-")]
            self.assertEqual(len(drafts), 1)
            meta = self._meta(os.path.join(rq, drafts[0]))
        self.assertEqual(meta.get("level"), "code")
        self.assertEqual(meta.get("level_source"), "auto")

    def test_one_architecture_draft_per_source_directory(self):  # verifies: REQ-EXTRACT-981#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "src", "store", "a.py"), "def a():\n    return 1\n")
            _write(os.path.join(d, "src", "store", "b.py"), "def b():\n    return 2\n")
            _write(os.path.join(d, "src", "cli", "c.py"), "def c():\n    return 3\n")
            rq, _ = self._extract(d)
            arch = sorted(f for f in os.listdir(rq) if f.startswith("ARCH-"))
            kids = {}
            for f in os.listdir(rq):
                if not f.startswith("DRAFT-"):
                    continue
                m = self._meta(os.path.join(rq, f))
                kids.setdefault(R._as_list(m.get("satisfies"))[0], []).append(f)
        self.assertEqual(len(arch), 2, arch)
        # each architecture draft is satisfied by exactly the drafts of its own directory
        self.assertEqual(sorted(len(v) for v in kids.values()), [1, 2])

    def test_the_system_rung_is_a_named_hole(self):  # verifies: REQ-EXTRACT-981#CASE-3
        """A stakeholder need is not in the source. The engine refuses to guess one and
        says so in the node's own title, rather than minting a plausible-looking need."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "src", "a.py"), "def a():\n    return 1\n")
            rq, _ = self._extract(d)
            needs = [f for f in os.listdir(rq) if f.startswith("SYS-")]
            self.assertEqual(len(needs), 1, needs)
            path = os.path.join(rq, needs[0])
            meta = self._meta(path)
            with open(path, encoding="utf-8") as f:
                body = f.read()
            arch = [f for f in os.listdir(rq) if f.startswith("ARCH-")]
            up = {R._as_list(self._meta(os.path.join(rq, a)).get("satisfies"))[0] for a in arch}
        self.assertEqual(meta.get("layer"), "need")
        self.assertEqual(meta.get("level"), "system")
        self.assertEqual(meta.get("level_source"), "auto")
        self.assertIn("NAME THIS NEED", body)
        self.assertEqual(up, {meta["id"]})

    def test_a_second_run_overwrites_nothing(self):  # verifies: REQ-EXTRACT-981#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "src", "a.py"), "def a():\n    return 1\n")
            rq, _ = self._extract(d)
            before = {f: open(os.path.join(rq, f), encoding="utf-8").read()
                      for f in os.listdir(rq)}
            self._extract(d)
            after = {f: open(os.path.join(rq, f), encoding="utf-8").read()
                     for f in os.listdir(rq)}
        self.assertEqual(before, after)


class CasesAtomicity049(unittest.TestCase):  # tested-by: ARCH-ATOMICITY-049  # tested-by: REQ-ATOMICITY-824  # tested-by: REQ-ATOMICITY-825
    def test_default_statement_size_threshold_is_150(self):  # verifies: REQ-ATOMICITY-824#CASE-3
        self.assertEqual(R.LINT_STATEMENT_WORDS, 150)

    def test_long_acceptance_step_produces_no_statement_size_finding(self):  # verifies: REQ-ATOMICITY-825#CASE-5
        words = " ".join(["beta"] * 200)
        body = ("# T\n\n## WHAT — Contract (normative)\n- short clause.\n\n"
                "## HOW — Acceptance (= tests)\nAC-1\n  Given {}\n  Then ok\n".format(words))
        r = {"meta": {"status": "confirmed"}, "body": body}
        fs = R.lint_requirement("REQ-X-001", r)
        self.assertNotIn("statement-size", [f["check"] for f in fs])


class CasesFanout052(unittest.TestCase):  # tested-by: ARCH-FANOUT-052  # tested-by: REQ-FANOUT-852
    CONTRACT = "## WHAT — Contract (normative)"
    ACCEPT = "## HOW — Acceptance (= tests)"

    def _body(self):
        return "# T\n\n{}\n- `x` does one thing.\n{}\n- a.\n- b.\n- c.\n".format(
            self.CONTRACT, self.ACCEPT)

    def test_fan_out_finding_does_not_fail_the_run(self):  # verifies: REQ-FANOUT-852#CASE-6
        reqs = {"REQ-P-001": {"meta": {"status": "confirmed", "level": "architecture"},
                              "body": self._body()}}
        for i in range(32):
            rid = "REQ-C-{:03d}".format(i)
            reqs[rid] = {"meta": {"status": "confirmed", "satisfies": ["REQ-P-001"]},
                        "body": self._body()}
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_lint(R.Workspace(reqs))
        self.assertIn("fan-out", buf.getvalue())
        self.assertEqual(code, 0)

    def test_lint_exempt_fan_out_suppresses_finding(self):  # verifies: REQ-FANOUT-852#CASE-7
        r = {"meta": {"status": "confirmed", "lint_exempt": ["fan-out"]}, "body": self._body()}
        fs = [f for f in R.lint_requirement("REQ-P-001", r, children=3) if f["check"] == "fan-out"]
        self.assertEqual(fs, [])


class CasesDecompose050(unittest.TestCase):  # tested-by: ARCH-DECOMPOSE-050  # tested-by: REQ-DECOMPOSE-837
    def test_no_invocation_site_passes_decompose(self):  # verifies: REQ-DECOMPOSE-837#CASE-3
        repo_root = os.path.join(os.path.dirname(os.path.abspath(R.__file__)), "..", "..")
        hook = os.path.join(repo_root, ".githooks", "pre-commit")
        ci = os.path.join(repo_root, ".github", "workflows", "ci.yml")
        if not (os.path.exists(hook) and os.path.exists(ci)):
            self.skipTest("hook/ci files not present (engine seeded outside this repo)")
        for p in (hook, ci):
            text = open(p, encoding="utf-8").read()
            self.assertNotIn("--decompose", text, p)


class CasesExtract(unittest.TestCase):  # tested-by: ARCH-EXTRACT-008  # tested-by: REQ-EXTRACT-849  # tested-by: REQ-EXTRACT-850  # tested-by: REQ-EXTRACT-851
    def test_draft_skips_already_tagged_file(self):  # verifies: REQ-EXTRACT-849#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "auth.py"), tag("AUTH-LOGIN-001") + "\ndef login():\n    pass\n")
            reqs_dir = os.path.join(d, "requirements")
            members = {"AUTH-LOGIN-001": [("implements", "auth.py", 1)]}
            with redirect_stdout(io.StringIO()):
                R.cmd_extract(R.Workspace({}, members, reqs_dir, d))
            made = [n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-")] if os.path.isdir(reqs_dir) else []
            self.assertEqual(made, [])

    def test_fresh_proposal_is_draft_with_todo_contract(self):  # verifies: REQ-EXTRACT-850#CASE-2
        with tempfile.TemporaryDirectory() as d:
            code_root = os.path.join(d, "src")
            _write(os.path.join(code_root, "widget.py"), "def go():\n    return 1\n")
            reqs_dir = os.path.join(d, "requirements")
            with redirect_stdout(io.StringIO()):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, code_root))
            made = [n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-")]
            text = open(os.path.join(reqs_dir, made[0]), encoding="utf-8").read()
            self.assertIn("status: draft", text)
            self.assertIn("- TODO: the observed behavior", text)

    def test_marker_heavy_file_scores_higher_risk(self):  # verifies: REQ-EXTRACT-851#CASE-1
        with tempfile.TemporaryDirectory() as d:
            code_root = os.path.join(d, "src")
            clean_src = "\n".join("x{0} = {0}".format(i) for i in range(10)) + "\n"
            messy_src = ("x0 = 0  # TODO fix\n" + "y0 = 0  # noqa\n"
                         + "\n".join("x{0} = {0}".format(i) for i in range(2, 10)) + "\n")
            _write(os.path.join(code_root, "clean.py"), clean_src)
            _write(os.path.join(code_root, "messy.py"), messy_src)
            reqs_dir = os.path.join(d, "requirements")
            with redirect_stdout(io.StringIO()):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, code_root))
            clean_text = open(os.path.join(reqs_dir, "DRAFT-CLEAN.md"), encoding="utf-8").read()
            messy_text = open(os.path.join(reqs_dir, "DRAFT-MESSY.md"), encoding="utf-8").read()
            clean_risk = int(re.search(r"risk: (\d+)", clean_text).group(1))
            messy_risk = int(re.search(r"risk: (\d+)", messy_text).group(1))
            self.assertGreater(messy_risk, clean_risk)

    def test_risk_score_routes_review_flag(self):  # verifies: REQ-EXTRACT-851#CASE-2
        with tempfile.TemporaryDirectory() as d:
            code_root = os.path.join(d, "src")
            _write(os.path.join(code_root, "messy.py"), "x = 1  # TODO fix\ny = 2  # noqa\n")
            _write(os.path.join(code_root, "clean.py"), "x = 1\ny = 2\n")
            reqs_dir = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, code_root))
            out = buf.getvalue()
            messy_line = [ln for ln in out.splitlines() if "DRAFT-MESSY" in ln][0]
            clean_line = [ln for ln in out.splitlines() if "DRAFT-CLEAN" in ln][0]
            self.assertTrue(messy_line.strip().startswith("REVIEW"), messy_line)
            self.assertTrue(clean_line.strip().startswith("auto-baseline"), clean_line)

    def test_rerun_does_not_overwrite_existing_draft(self):  # verifies: REQ-EXTRACT-851#CASE-3
        with tempfile.TemporaryDirectory() as d:
            code_root = os.path.join(d, "src")
            _write(os.path.join(code_root, "widget.py"), "def go():\n    return 1\n")
            reqs_dir = os.path.join(d, "requirements")
            with redirect_stdout(io.StringIO()):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, code_root))
            dest = os.path.join(reqs_dir, "DRAFT-WIDGET.md")
            custom = "hand-edited content\n"
            _write(dest, custom)
            with redirect_stdout(io.StringIO()):
                R.cmd_extract(R.Workspace({}, {}, reqs_dir, code_root))
            self.assertEqual(open(dest, encoding="utf-8").read(), custom)


class CasesPromote(unittest.TestCase):  # tested-by: ARCH-PROMOTE-011  # tested-by: REQ-PROMOTE-894
    def test_only_first_status_line_rewritten(self):  # verifies: REQ-PROMOTE-894#CASE-2
        text = ("---\nid: X-1\nstatus: draft\nlayer: bus\n---\n\n"
                "# T\n\nThe deployment status: pending is tracked elsewhere.\n")
        new_text, n = R._set_frontmatter_status(text, "confirmed")
        self.assertEqual(n, 1)
        self.assertIn("status: confirmed", new_text)
        self.assertNotIn("status: draft", new_text)
        self.assertIn("The deployment status: pending is tracked elsewhere.\n", new_text)

    def test_hand_written_confirmed_with_no_code_is_an_error(self):  # verifies: ARCH-PROMOTE-011#CASE-3
        """Nothing stops a human typing `status: confirmed` into the frontmatter of a
        requirement no code implements — that is the cost of making confirmation an
        edit rather than a command. The gate is what catches it, as an error."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="confirmed", layer="feature",
                              extra="", title="Hand-confirmed"))
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(R.Workspace(reqs, {}, d, d), False)
        out = buf.getvalue()
        self.assertIn("RM006", out)
        self.assertIn("AREA-A-001", out)
        self.assertNotEqual(rc, 0, "RM006 is an error — the gate must fail")

class CasesCandidates(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009  # tested-by: REQ-CANDIDATES-827
    def test_candidate_carries_full_field_set(self):  # verifies: REQ-CANDIDATES-827#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), '"""mod a."""\ndef f(x):\n    return x\n')
            reqs_dir = os.path.join(d, "requirements")
            reqs = R.load_requirements(reqs_dir)
            members = R.scan_members(d, reqs_dir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_candidates(R.Workspace(reqs, members, reqs_dir, d), None)
            plan = json.loads(buf.getvalue())
            cand = plan["candidates"][0]
            expected = {"suggested_id", "suggested_layer", "files", "docstrings", "signatures",
                        "imports", "depends_on", "tested_by", "importer_count", "existing_req",
                        "loc", "split_candidate", "is_test"}
            self.assertTrue(expected.issubset(cand.keys()), cand.keys())


class CasesLint014(unittest.TestCase):  # tested-by: REQ-LINT-863  # tested-by: REQ-LINT-864
    CONTRACT = "## WHAT — Contract (normative)"
    ACCEPT = "## HOW — Acceptance (= tests)"

    def _req(self, status, body):
        return {"meta": {"status": status}, "body": body}

    def _lint(self, reqs, strict=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_lint(R.Workspace(reqs), strict)
        return code, buf.getvalue()

    def test_one_run_surfaces_structural_and_readability_findings(self):  # verifies: REQ-LINT-863#CASE-1
        body = "# T\n\n{}\n- It shall do A and B and C and D.\n".format(self.CONTRACT)  # no Cases heading
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        pairs = [(f["severity"], f["check"]) for f in fs]
        self.assertIn(("error", "missing-section"), pairs)
        self.assertIn(("warn", "stacked-conditions"), pairs)

    def test_stacked_conditions_under_notes_never_fires(self):  # verifies: REQ-LINT-864#CASE-2
        body = ("# T\n\n{}\n- ok.\n\n{}\n- ok.\n\n"
                "## Notes & known limitations\n"
                "- It shall do A and B and C and D.\n").format(self.CONTRACT, self.ACCEPT)
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "stacked-conditions" for f in fs))

    def test_blockquote_stacked_line_not_linted_as_prose(self):  # verifies: REQ-LINT-864#CASE-3
        body = "# T\n\n{}\n> It shall do A and B and C and D.\n".format(self.CONTRACT)
        self.assertEqual(R._prose_lint(body, "contract"), [])

    def test_missing_section_error_does_not_fail_non_strict_run(self):  # verifies: REQ-LINT-864#CASE-5
        body = "# T\n\n{}\n- the contract.\n".format(self.CONTRACT)  # no Cases heading
        reqs = {"REQ-X-001": self._req("confirmed", body)}
        code, _ = self._lint(reqs, strict=False)
        self.assertEqual(code, 0)


class CasesInit012(unittest.TestCase):  # tested-by: REQ-INIT-860  # tested-by: REQ-INIT-861
    def _init(self, code_root, wipe=False):
        reqs_dir = os.path.join(code_root, "requirements")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_init(reqs_dir, code_root, wipe=wipe)
        return code, buf.getvalue(), reqs_dir

    def test_dangling_tag_is_not_self_hosting(self):  # verifies: REQ-INIT-860#CASE-6
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "CORE-Y-002.md"),
                   "---\nid: CORE-Y-002\nstatus: confirmed\n---\n\n# Cap\n")
            _write(os.path.join(d, "scripts", "reqmap.py"),
                   tag("CORE-GHOST-999") + "\nx = 1\n")
            self._init(d)
            ignore = open(os.path.join(d, ".reqmapignore"), encoding="utf-8").read()
            globs = [ln.strip() for ln in ignore.splitlines()
                     if ln.strip() and not ln.strip().startswith("#")]
        self.assertIn("scripts/reqmap.py", globs)

    def test_lock_carries_hash_for_the_newly_drafted_requirement(self):  # verifies: REQ-INIT-861#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "app.py"), "x = 1\n")
            _, _, reqs_dir = self._init(d)
            drafts = [n[:-3] for n in os.listdir(reqs_dir) if n.startswith("DRAFT-") and n.endswith(".md")]
            self.assertTrue(drafts)
            lock = R.load_lock(reqs_dir)
        self.assertIn(drafts[0], lock)


def _rules(qs):
    return [q["rule"] for q in qs]


class Clarify(unittest.TestCase):  # tested-by: ARCH-CLARIFY-062  # tested-by: REQ-CLARIFY-956  # tested-by: REQ-CLARIFY-957
    def _qs(self, clauses, cases=("CASE-1 — c\n  Given x\n  When y\n  Then z",)):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-Q-001.md"), _spec("AREA-Q-001", clauses, cases))
            reqs = R.load_requirements(d)
            return R._clarify_questions("AREA-Q-001", reqs["AREA-Q-001"], reqs)

    def _run(self, d, rid=None, as_json=False):
        reqs = R.load_requirements(os.path.join(d, "requirements"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_clarify(reqs, rid, as_json=as_json)
        return code, buf.getvalue()

    def test_hedge_word_is_named(self):  # verifies: REQ-CLARIFY-956#CASE-1
        qs = self._qs(["`gate` reports errors quickly and refuses an invalid tag."])
        vague = [q for q in qs if q["rule"] == "vague-term"]
        self.assertTrue(vague)
        self.assertIn("quickly", vague[0]["question"])

    def test_bare_number_asked_identifier_not(self):  # verifies: REQ-CLARIFY-956#CASE-2
        numbered = self._qs(["`gate` retries 3 times before it fails."])
        ident = self._qs(["`gate` emits CASE-2 for v4.0.0 when the input is invalid."])
        self.assertIn("number-without-unit", _rules(numbered))
        self.assertNotIn("number-without-unit", _rules(ident))

    def test_happy_path_only_asks_about_failure(self):  # verifies: REQ-CLARIFY-956#CASE-3
        happy = self._qs(["`gate` writes the lock."],
                         cases=("CASE-1 — ok\n  Given a repo\n  When it runs\n  Then it writes",))
        sad = self._qs(["`gate` writes the lock."],
                       cases=("CASE-1 — bad\n  Given an invalid lock\n  When it runs\n  Then it refuses",))
        self.assertIn("no-failure-case", _rules(happy))
        self.assertNotIn("no-failure-case", _rules(sad))

    def test_no_clause_or_no_case_is_blocking(self):  # verifies: REQ-CLARIFY-956#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-E-001.md"),
                   "---\nid: AREA-E-001\nstatus: confirmed\nlayer: feature\n---\n\n# T\n")
            reqs = R.load_requirements(d)
            qs = R._clarify_questions("AREA-E-001", reqs["AREA-E-001"], reqs)
        blocking = [q for q in qs if q["severity"] == "blocking"]
        self.assertEqual({"no-contract", "no-cases"}, {q["rule"] for q in blocking})

    def test_unbounded_and_ambiguous_actor(self):  # verifies: REQ-CLARIFY-956#CASE-1
        qs = self._qs(["It scans all files when the input is missing."])
        self.assertIn("unbounded-quantity", _rules(qs))
        self.assertIn("ambiguous-actor", _rules(qs))

    def test_cases_all_from_one_input_kind_are_questioned(self):  # verifies: REQ-CLARIFY-956#CASE-5
        """The shape that let `search` ship: four cases, four qualities of one input kind."""
        cases = tuple(
            "CASE-{n} \u2014 c{n}\n  Given  a query that is {w}\n  When   it runs\n  Then   it answers"
            .format(n=n, w=w) for n, w in enumerate(("matching", "unmatched", "empty"), 1))
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-Q-001.md"),
                   _spec("AREA-Q-001", ["`search` ranks by wording."], cases=cases))
            _write(os.path.join(d, "AREA-P-002.md"),
                   _spec("AREA-P-002", ["`map` draws the graph."],
                         cases=("CASE-1 \u2014 c\n  Given  a diagram\n  When   it runs\n  Then   ok",)))
            reqs = R.load_requirements(d)
            qs = R._clarify_questions("AREA-Q-001", reqs["AREA-Q-001"], reqs)
        mono = [q for q in qs if q["rule"] == "case-monoculture"]
        self.assertTrue(mono, _rules(qs))
        self.assertIn("query", mono[0]["question"])

    def test_the_corpus_own_subject_is_not_that_signal(self):  # verifies: REQ-CLARIFY-956#CASE-6
        """A corpus of requirements about requirements starts every case the same way; that
        is the domain, not a narrow focus, and flagging it would fire on 17% and say nothing."""
        cases = tuple(
            "CASE-{n} \u2014 c{n}\n  Given  a requirement that is {w}\n  When   it runs\n  Then   it answers"
            .format(n=n, w=w) for n, w in enumerate(("confirmed", "drafted", "retired"), 1))
        with tempfile.TemporaryDirectory() as d:
            # a real sample: the exclusion is a statement about the corpus, so it needs one
            for n in range(12):
                rid = "AREA-{}-{:03d}".format(chr(ord("A") + n), n + 1)
                _write(os.path.join(d, rid + ".md"),
                       _spec(rid, ["`gate` reads it."], cases=cases))
            reqs = R.load_requirements(d)
            qs = R._clarify_questions("AREA-A-001", reqs["AREA-A-001"], reqs)
        self.assertNotIn("case-monoculture", _rules(qs))

    def test_output_carries_rule_quote_and_suggestion(self):  # verifies: REQ-CLARIFY-957#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-Q-001.md"),
                   _spec("AREA-Q-001", ["`gate` reports errors quickly."]))
            code, out = self._run(d, "AREA-Q-001")
        self.assertEqual(0, code)
        self.assertIn("vague-term", out)
        self.assertIn("quickly", out)
        self.assertIn("->", out)

    def test_corpus_view_reports_blocking_only(self):  # verifies: REQ-CLARIFY-957#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-B-001.md"),
                   "---\nid: AREA-B-001\nstatus: confirmed\nlayer: feature\n---\n\n# B\n")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   _spec("AREA-A-001", ["`gate` reports errors quickly."]))
            code, out = self._run(d)
        self.assertEqual(0, code)
        self.assertIn("AREA-B-001", out)
        self.assertNotIn("AREA-A-001", out)

    def test_json_carries_the_records(self):  # verifies: REQ-CLARIFY-957#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-Q-001.md"),
                   _spec("AREA-Q-001", ["`gate` reports errors quickly."]))
            code, out = self._run(d, "AREA-Q-001", as_json=True)
        data = json.loads(out)
        self.assertEqual(0, code)
        self.assertEqual("AREA-Q-001", data["requirements"][0]["id"])
        self.assertTrue(data["requirements"][0]["questions"])

    def test_unknown_id_errors_clean_requirement_passes(self):  # verifies: REQ-CLARIFY-957#CASE-4  # verifies: ARCH-CLARIFY-062#CASE-1  # verifies: ARCH-CLARIFY-062#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-C-001.md"),
                   _spec("AREA-C-001",
                         ["`gate` writes the lock file."],
                         cases=("CASE-1 — ok\n  Given an invalid lock\n  When `gate` runs\n  Then it refuses",)))
            missing, _ = self._run(d, "NOPE-X-001")
            clean, out = self._run(d, "AREA-C-001")
        self.assertEqual(1, missing)
        self.assertEqual(0, clean)
        self.assertIn("nothing unclear", out)

    def test_questions_are_deterministic(self):  # verifies: ARCH-CLARIFY-062#CASE-2
        clauses = ["It scans all files quickly, retrying 3 times."]
        self.assertEqual(self._qs(clauses), self._qs(clauses))


class Retire(unittest.TestCase):  # tested-by: ARCH-RETIRE-064  # tested-by: REQ-RETIRE-960  # tested-by: REQ-RETIRE-961  # tested-by: REQ-RETIRE-962  # tested-by: REQ-RETIRE-963
    def _seed(self, d, extra_files=True):
        rd = os.path.join(d, "requirements")
        _write(os.path.join(rd, "AREA-R-001.md"), _spec("AREA-R-001", ["`gate` writes the lock file."]))
        if extra_files:
            _write(os.path.join(d, "only.py"), tag("AREA-R-001") + "\ndef dead():\n    return 1\n")
            _write(os.path.join(d, "shared.py"),
                   tag("AREA-R-001") + "  " + tag("AREA-S-002") + "\ndef kept():\n    return 2\n")
            _write(os.path.join(rd, "AREA-S-002.md"), _spec("AREA-S-002", ["`sync` advances the baseline."]))
        return rd

    def _run(self, d, rid="AREA-R-001", **kw):
        rd = os.path.join(d, "requirements")
        reqs = R.load_requirements(rd)
        members = R.scan_members(d, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_retire(R.Workspace(reqs, members, rd, d), rid, **kw)
        return code, buf.getvalue()

    def _plan(self, d, rid="AREA-R-001"):
        rd = os.path.join(d, "requirements")
        return R._retire_plan(R.load_requirements(rd), R.scan_members(d, d), rid)

    def test_plan_comes_before_any_change(self):  # verifies: ARCH-RETIRE-064#CASE-1  # verifies: REQ-RETIRE-961#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            before = open(os.path.join(rd, "AREA-R-001.md"), encoding="utf-8").read()
            code, out = self._run(d)
            after = open(os.path.join(rd, "AREA-R-001.md"), encoding="utf-8").read()
        self.assertEqual(0, code)
        self.assertEqual(before, after)
        self.assertIn("only.py", out)

    def test_a_dependent_stops_the_operation(self):  # verifies: ARCH-RETIRE-064#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            _write(os.path.join(rd, "AREA-D-003.md"),
                   _spec("AREA-D-003", ["`map` draws the graph."], extra="depends_on: [AREA-R-001]\n"))
            code, out = self._run(d, do_apply=True)
        self.assertEqual(1, code)
        self.assertIn("AREA-D-003", out)
        self.assertIn("refusing", out)

    def test_deprecating_leaves_the_code_alone(self):  # verifies: ARCH-RETIRE-064#CASE-3  # verifies: REQ-RETIRE-961#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            code, _out = self._run(d, do_apply=True)
            spec = open(os.path.join(rd, "AREA-R-001.md"), encoding="utf-8").read()
            only = open(os.path.join(d, "only.py"), encoding="utf-8").read()
        self.assertEqual(0, code)
        self.assertIn("status: deprecated", spec)
        self.assertIn(tag("AREA-R-001"), only)

    def test_plan_names_dependents_and_children(self):  # verifies: REQ-RETIRE-960#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            _write(os.path.join(rd, "AREA-D-003.md"),
                   _spec("AREA-D-003", ["`map` draws."], extra="depends_on: [AREA-R-001]\n"))
            _write(os.path.join(rd, "AREA-C-004.md"),
                   _spec("AREA-C-004", ["`map` draws too."], extra="satisfies: [AREA-R-001]\n"))
            plan = self._plan(d)
        self.assertEqual(["AREA-D-003"], plan["dependents"])
        self.assertEqual(["AREA-C-004"], plan["children"])

    def test_plan_separates_exclusive_from_shared_files(self):  # verifies: REQ-RETIRE-960#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            plan = self._plan(d)
        self.assertEqual(["only.py"], plan["exclusive_files"])
        self.assertEqual(["shared.py"], plan["shared_files"])

    def test_plan_finds_a_prose_cross_reference(self):  # verifies: REQ-RETIRE-960#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            _write(os.path.join(rd, "AREA-P-005.md"),
                   _spec("AREA-P-005", ["`map` draws, see [[AREA-R-001]] for the rule."]))
            plan = self._plan(d)
        self.assertEqual(["AREA-P-005"], plan["referenced_by"])

    def test_plan_names_a_dependency_left_with_no_consumer(self):  # verifies: REQ-RETIRE-960#CASE-4
        """depends_on runs consumer -> foundation: retiring the consumer cannot break the
        capability, but it can leave it with no caller at all."""
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-E-007.md"), _spec("AREA-E-007", ["`scan` walks the tree."]))
            _write(os.path.join(rd, "AREA-R-001.md"),
                   _spec("AREA-R-001", ["`gate` writes."], extra="depends_on: [AREA-E-007]\n"))
            plan = self._plan(d)
        self.assertEqual(["AREA-E-007"], plan["leaves_unused"])

    def test_force_overrides_the_dependent_refusal(self):  # verifies: REQ-RETIRE-961#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            _write(os.path.join(rd, "AREA-D-003.md"),
                   _spec("AREA-D-003", ["`map` draws."], extra="depends_on: [AREA-R-001]\n"))
            code, _out = self._run(d, do_apply=True, force=True)
            spec = open(os.path.join(rd, "AREA-R-001.md"), encoding="utf-8").read()
        self.assertEqual(0, code)
        self.assertIn("status: deprecated", spec)

    def test_delete_keeps_the_sibling_block(self):  # verifies: REQ-RETIRE-962#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            two = _spec("AREA-R-001", ["`gate` writes."]) + "\n" + _spec("AREA-T-006", ["`sync` writes."])
            _write(os.path.join(rd, "MODULE.md"), two)
            code, _out = self._run(d, delete=True, do_apply=True)
            left = open(os.path.join(rd, "MODULE.md"), encoding="utf-8").read()
        self.assertEqual(0, code)
        self.assertIn("AREA-T-006", left)
        self.assertNotIn("id: AREA-R-001", left)

    def test_delete_strips_the_tag_and_keeps_a_shared_line(self):  # verifies: REQ-RETIRE-962#CASE-2  # verifies: REQ-RETIRE-962#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            code, _out = self._run(d, delete=True, do_apply=True)
            only = open(os.path.join(d, "only.py"), encoding="utf-8").read()
            shared = open(os.path.join(d, "shared.py"), encoding="utf-8").read()
        self.assertEqual(0, code)
        self.assertNotIn("AREA-R-001", only)
        self.assertIn("def dead():", only)              # the body is never removed on a tag
        self.assertNotIn("AREA-R-001", shared)
        self.assertIn("AREA-S-002", shared)

    def test_delete_drops_the_lock_entry(self):  # verifies: REQ-RETIRE-962#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            R.save_lock(rd, {"AREA-R-001": "abc123", "AREA-S-002": "def456"})
            self._run(d, delete=True, do_apply=True)
            lock = R.load_lock(rd)
        self.assertNotIn("AREA-R-001", lock)
        self.assertIn("AREA-S-002", lock)

    def test_unknown_id_exits_one(self):  # verifies: REQ-RETIRE-961#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            code, _out = self._run(d, rid="NOPE-X-001")
        self.assertEqual(1, code)

    def _pair(self, d, dependent=True):
        """AREA-R-001, plus AREA-D-003 which optionally depends on it."""
        rd = self._seed(d, extra_files=False)
        _write(os.path.join(rd, "AREA-D-003.md"),
               _spec("AREA-D-003", ["`map` draws the graph."],
                     extra=("depends_on: [AREA-R-001]\n" if dependent else "")))
        return rd

    def test_a_deprecated_dependent_does_not_block(self):  # verifies: REQ-RETIRE-961#CASE-4
        # A deprecated requirement is out of service and exempt from every gate, so its
        # pointer cannot make a retirement unsafe. Counting it made retiring a class of
        # N cost N-1 forced writes: each step was blocked by the step already gone.
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            _write(os.path.join(rd, "AREA-D-003.md"),
                   _spec("AREA-D-003", ["`map` draws the graph."], status="deprecated",
                         extra="depends_on: [AREA-R-001]\n"))
            code, out = self._run(d, do_apply=True)
            spec = open(os.path.join(rd, "AREA-R-001.md"), encoding="utf-8").read()
        self.assertEqual(0, code)
        self.assertNotIn("refusing", out)
        self.assertIn("status: deprecated", spec)

    def test_a_batch_orders_the_consumer_first(self):  # verifies: ARCH-RETIRE-064#CASE-4  # verifies: REQ-RETIRE-963#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._pair(d)
            _code, out = self._run(d, rid=["AREA-R-001", "AREA-D-003"])
        self.assertIn("AREA-D-003 -> AREA-R-001", out)

    def test_batch_members_do_not_block_each_other(self):  # verifies: REQ-RETIRE-963#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = self._pair(d)
            code, out = self._run(d, rid=["AREA-R-001", "AREA-D-003"], do_apply=True)
            texts = [open(os.path.join(rd, f), encoding="utf-8").read()
                     for f in ("AREA-R-001.md", "AREA-D-003.md")]
        self.assertEqual(0, code)
        self.assertNotIn("refusing", out)
        self.assertTrue(all("status: deprecated" in x for x in texts), texts)

    def test_one_working_tree_check_for_the_whole_batch(self):  # verifies: REQ-RETIRE-963#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = self._pair(d, dependent=False)
            names = ("AREA-R-001.md", "AREA-D-003.md")
            before = [open(os.path.join(rd, f), encoding="utf-8").read() for f in names]
            with mock.patch.object(R.retire, "_git_dirty", return_value=True):
                code, out = self._run(d, rid=["AREA-R-001", "AREA-D-003"], do_apply=True)
            after = [open(os.path.join(rd, f), encoding="utf-8").read() for f in names]
        self.assertEqual(1, code)
        self.assertEqual(1, out.count("uncommitted changes"))
        self.assertEqual(before, after)

    def test_a_single_id_carries_no_batch_ordering_line(self):  # verifies: REQ-RETIRE-963#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._seed(d, extra_files=False)
            _code, out = self._run(d, rid=["AREA-R-001"])
        self.assertNotIn("in this order", out)

    def test_a_cycle_inside_the_batch_keeps_every_member(self):
        # `gate` reports the cycle on its own; retire must not silently drop its members.
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d, extra_files=False)
            _write(os.path.join(rd, "AREA-D-003.md"),
                   _spec("AREA-D-003", ["`map` draws."], extra="depends_on: [AREA-R-001]\n"))
            reqs = R.load_requirements(rd)
            reqs["AREA-R-001"]["meta"]["depends_on"] = ["AREA-D-003"]
            order = R._retire_order(reqs, ["AREA-R-001", "AREA-D-003"])
        self.assertEqual(sorted(order), ["AREA-D-003", "AREA-R-001"])


class RemedyCanAct(unittest.TestCase):  # tested-by: ARCH-DECOMPOSE-050  # tested-by: REQ-DECOMPOSE-839
    """Both checks are ERRORS under `--strict`, and `gate` always runs the lint strict.
    They named `clarify <ID> --decompose` as the fix; that flag acts on `statement-size`
    findings only, so following the advice printed `All clean` and wrote nothing — and
    left the author with `lint_exempt:`, the one action the skill says must never be the
    reflex. Reported from a consumer repo where nine auditors hit it independently."""

    def _fs(self, rid, r):
        return R.lint_requirement(rid, r, {}, {}, {})

    def _oversized(self, n_ac=9):
        cases = tuple("CASE-{} \u2014 c{}\n  Given x{}  When y{}  Then z".format(i, i, "", "", "")
                      for i in range(1, n_ac + 1))
        return _spec("A-BIG-001", ["`gate` writes the lock file."], cases=cases)

    def test_over_scoped_says_clearing_either_number_clears_it(self):
        # The trigger is `contract_n > MAX and ac_count > MAX`, so an author who brings
        # the criteria under the ceiling clears it without touching contract structure.
        # Nothing said so, and the exemption was the only visible way out.
        clauses = ["clause {} does a distinct thing.".format(i)
                   for i in range(1, R.LINT_CONTRACT_MAX + 3)]
        cases = tuple("CASE-{} \u2014 c{}\n  Given x{}  When y{}  Then z".format(i, i, "", "", "")
                      for i in range(1, R.LINT_AC_MAX + 3))
        body = _spec("A-BIG-002", clauses, cases=cases)
        fs = self._fs("A-BIG-002", {"meta": {"status": "confirmed", "layer": "feature",
                                             "owner": "Ana"}, "body": body})
        f = next((x for x in fs if x["check"] == "over-scoped"), None)
        self.assertIsNotNone(f, [x["check"] for x in fs])
        self.assertIn("either", f["detail"])
        self.assertIn("does not cover this check", f["detail"])

    def test_a_decompose_run_that_scaffolds_nothing_says_so(self):  # verifies: REQ-DECOMPOSE-839#CASE-6
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "A-OK-001.md"),
                   _spec("A-OK-001", ["`gate` writes the lock file."]))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_lint(R.Workspace(R.load_requirements(rd), {}, rd, d),
                           decompose=True, only="A-OK-001")
            out = buf.getvalue()
        self.assertIn("nothing scaffolded", out)
        self.assertIn("statement-size", out)

    def test_a_decompose_run_that_scaffolds_says_nothing_of_the_kind(self):
        # The disclosure must not fire on a run that DID scaffold, or it becomes noise.
        long_clause = " ".join("word{}".format(i) for i in range(R.LINT_STATEMENT_WORDS + 20))
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "A-LONG-001.md"),
                   _spec("A-LONG-001", [long_clause + "."]))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_lint(R.Workspace(R.load_requirements(rd), {}, rd, d),
                           decompose=True, only="A-LONG-001")
            out = buf.getvalue()
        self.assertIn("scaffolded", out)
        self.assertNotIn("nothing scaffolded", out)


class DemoteOnEdit(unittest.TestCase):  # tested-by: ARCH-PROMOTE-011  # tested-by: REQ-PROMOTE-974
    """An edited confirmed contract loses its confirmation, in sync."""

    BODY = (
        "---\n"
        "id: AREA-E-001\n"
        "status: confirmed\n"
        "level: code\n"
        "layer: feature\n"
        "owner: A\n"
        "---\n"
        "\n"
        "# Titled\n"
        "\n"
        "## Description\n"
        "> Why.\n"
        "\n"
        "Every bullet below is binding.\n"
        "- It does one thing.\n"
        "\n"
        "## Cases\n"
        "CASE-1\n"
        "  Given  a\n"
        "  When   b\n"
        "  Then   c\n"
    )

    def _seed(self, d):
        rq = os.path.join(d, "requirements")
        _write(os.path.join(rq, "AREA-E-001.md"), self.BODY)
        _write(os.path.join(d, "m.py"), tag("AREA-E-001") + "\ndef f():\n    return 1\n")
        return rq

    def _sync(self, d, accept=False):
        rq = os.path.join(d, "requirements")
        reqs = R.load_requirements(rq)
        members = R.scan_members(d, rq)
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            R.cmd_check(R.Workspace(reqs, members, rq, d), True, accept_drift=accept)
        return buf.getvalue()

    def _status(self, rq):
        for line in open(os.path.join(rq, "AREA-E-001.md"), encoding="utf-8"):
            if line.startswith("status:"):
                return line.strip()
        return ""

    def _edit(self, rq):
        with open(os.path.join(rq, "AREA-E-001.md"), "a", encoding="utf-8") as f:
            f.write("- It also does a second thing.\n")

    def test_edited_confirmed_contract_is_demoted(self):  # verifies: ARCH-PROMOTE-011#CASE-1  # verifies: REQ-PROMOTE-974#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d)
            self._sync(d)                       # baseline
            self._edit(rq)
            out = self._sync(d)
            self.assertIn("demoted: AREA-E-001", out)
            self.assertIn("no longer gate", out)
            self.assertEqual(self._status(rq), "status: draft")
            # the baseline advanced in the same run, so a second sync is quiet
            self.assertNotIn("demoted:", self._sync(d))

    def test_a_new_requirement_is_not_drift(self):  # verifies: REQ-PROMOTE-974#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d)
            out = self._sync(d)                 # never been in the lock
            self.assertNotIn("demoted:", out)
            self.assertEqual(self._status(rq), "status: confirmed")

    def test_accept_drift_keeps_the_status(self):  # verifies: ARCH-PROMOTE-011#CASE-2  # verifies: REQ-PROMOTE-974#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d)
            self._sync(d)
            self._edit(rq)
            out = self._sync(d, accept=True)
            self.assertNotIn("demoted:", out)
            self.assertEqual(self._status(rq), "status: confirmed")


    def _commit_with_older_hash(self, d, rq):
        """A git repo whose committed lock holds a hash an older engine wrote for the
        same, unchanged text — the state a consumer is in right after re-vendoring."""
        def git(*args):
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
                           cwd=d, check=True, capture_output=True)
        git("init", "-q")
        self._sync(d)
        lock = os.path.join(rq, "_reqlock.json")
        with open(lock, encoding="utf-8") as f:
            data = json.load(f)
        data["AREA-E-001"] = "0123456789ab"
        with open(lock, "w", encoding="utf-8") as f:
            json.dump(data, f)
        git("add", "-A")
        git("commit", "-q", "-m", "baseline")

    def test_unchanged_text_under_a_new_hash_keeps_its_confirmation(self):  # verifies: REQ-PROMOTE-974#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d)
            self._commit_with_older_hash(d, rq)
            out = self._sync(d)
            self.assertNotIn("demoted:", out)
            self.assertIn("re-baselined 1 confirmed contract", out)
            self.assertEqual(self._status(rq), "status: confirmed")
            with open(os.path.join(rq, "_driftlog.json"), encoding="utf-8") as f:
                log = json.load(f)
            self.assertIn("engine upgrade", log["accepted"]["AREA-E-001"]["reason"])
            self.assertNotIn("re-baselined", self._sync(d))

    def test_an_edit_after_the_lock_commit_is_still_demoted(self):  # verifies: REQ-PROMOTE-974#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d)
            self._commit_with_older_hash(d, rq)
            self._edit(rq)
            out = self._sync(d)
            self.assertIn("demoted: AREA-E-001", out)
            self.assertNotIn("re-baselined", out)
            self.assertEqual(self._status(rq), "status: draft")


class NewQuestionsAfterAnEdit(unittest.TestCase):  # tested-by: ARCH-CLARIFY-062  # tested-by: REQ-CLARIFY-975
    """Clarifying one requirement can raise a question its old text never had."""

    HEAD = ("---\n"
            "id: AREA-Q-001\n"
            "status: confirmed\n"
            "level: code\n"
            "layer: feature\n"
            "owner: A\n"
            "---\n"
            "\n"
            "# Titled\n"
            "\n"
            "## Description\n"
            "> Why.\n"
            "\n"
            "Every bullet below is binding.\n")
    CASES = ("\n## Cases\nCASE-1\n  Given  a\n  When   b\n  Then   c\n")

    def _write_req(self, rq, clauses):
        _write(os.path.join(rq, "AREA-Q-001.md"), self.HEAD + clauses + self.CASES)

    def _sync(self, d):
        rq = os.path.join(d, "requirements")
        reqs = R.load_requirements(rq)
        members = R.scan_members(d, rq)
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            R.cmd_check(R.Workspace(reqs, members, rq, d), True, accept_drift=True)
        return buf.getvalue()

    def _seed(self, d, clauses):
        rq = os.path.join(d, "requirements")
        os.makedirs(rq, exist_ok=True)
        self._write_req(rq, clauses)
        _write(os.path.join(d, "m.py"), tag("AREA-Q-001") + "\ndef f():\n    return 1\n")
        return rq

    def test_a_new_blocking_question_is_reported(self):  # verifies: REQ-CLARIFY-975#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d, "- It does one thing.\n")
            self._sync(d)                                  # snapshot
            self._write_req(rq, "- It does one thing.\n")  # unchanged body, then break it
            # remove the Cases section entirely -> the `no-cases` blocking rule fires
            _write(os.path.join(rq, "AREA-Q-001.md"), self.HEAD + "- It does one thing.\n")
            out = self._sync(d)
            self.assertIn("New open question(s)", out)
            self.assertIn("AREA-Q-001", out)

    def test_an_unchanged_question_is_not_re_reported(self):  # verifies: REQ-CLARIFY-975#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d, "- It does one thing.\n")
            _write(os.path.join(rq, "AREA-Q-001.md"), self.HEAD + "- It does one thing.\n")
            self._sync(d)                                  # first sight of the question
            out = self._sync(d)                            # same question, second run
            self.assertNotIn("New open question(s)", out)

    def test_a_brand_new_requirement_is_not_reported(self):  # verifies: REQ-CLARIFY-975#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = self._seed(d, "- It does one thing.\n")
            _write(os.path.join(rq, "AREA-Q-001.md"), self.HEAD + "- It does one thing.\n")
            out = self._sync(d)                            # never been in the snapshot
            self.assertNotIn("New open question(s)", out)


class ClauseCaseGapIsOneQuestion(unittest.TestCase):  # tested-by: ARCH-CLARIFY-062  # tested-by: REQ-CLARIFY-956
    """The counter compares two numbers and never reads a case, so it may not
    accuse a clause by position — it says how many are uncovered, not which."""

    def _req(self, n_clauses, n_cases):
        body = ["---", "id: AREA-G-001", "status: draft", "level: code",
                "layer: feature", "owner: A", "---", "", "# Titled", "",
                "## Description", "> Why.", "", "Every bullet below is binding."]
        for i in range(1, n_clauses + 1):
            body.append("- Clause number %d does a thing." % i)
        body += ["", "## Cases"]
        for i in range(1, n_cases + 1):
            body += ["CASE-%d" % i, "  Given  a", "  When   b", "  Then   c", ""]
        return "\n".join(body) + "\n"

    def _questions(self, n_clauses, n_cases):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-G-001.md"), self._req(n_clauses, n_cases))
            reqs = R.load_requirements(d)
            return [q for q in R._clarify_questions("AREA-G-001", reqs["AREA-G-001"], reqs)
                    if q["rule"] == "clause-without-case"]

    def test_five_clauses_two_cases_raise_one_question_not_three(self):
        qs = self._questions(5, 2)
        self.assertEqual(len(qs), 1)
        self.assertIn("3 clause(s) have no case", qs[0]["question"])
        self.assertIn("5 clauses and 2 cases", qs[0]["question"])

    def test_the_question_does_not_accuse_a_clause(self):
        qs = self._questions(4, 3)
        self.assertEqual(qs[0]["where"], "Cases")
        self.assertEqual(qs[0]["quote"], "")          # no clause is quoted as the culprit
        self.assertIn("cannot say WHICH", qs[0]["question"])

    def test_a_case_per_clause_raises_nothing(self):
        self.assertEqual(self._questions(3, 3), [])


class RetireKeepsTheLineBreak(unittest.TestCase):  # tested-by: ARCH-RETIRE-064  # tested-by: REQ-RETIRE-962
    """`retire --delete` strips a tag out of source. It must take the tag and nothing else.

    Every Retire fixture put its tag on a line of ITS OWN, so the shape SKILL.md actually
    documents — `code()  # implements: X`, a tag trailing a line of code — was never
    exercised. The strip regex ended in `\\s*`, `\\s` matches a newline, and these lines
    carry their own terminator: the tag took the newline with it and the NEXT line was
    glued into the comment. Loud here (IndentationError); silent whenever the swallowed
    line left the file parseable."""

    def _strip(self, src, name="m.py", cap="AREA-X-001"):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        with io.open(os.path.join(d, name), "w", encoding="utf-8", newline="") as f:
            f.write(src)
        R._strip_member_tags(d, [{"file": name, "line": 1}], cap)
        with io.open(os.path.join(d, name), encoding="utf-8", newline="") as f:
            return f.read()

    def test_a_tag_trailing_code_does_not_swallow_the_next_line(self):
        got = self._strip("def f():\n"
                          "    x = compute()  " + tag("AREA-X-001") + "\n"
                          "    if x:\n"
                          "        return x\n")
        self.assertEqual(got, "def f():\n    x = compute()\n    if x:\n        return x\n")
        compile(got, "m.py", "exec")     # the whole point: it still parses

    def test_the_emptied_comment_marker_goes_with_the_tag(self):
        self.assertEqual(self._strip("x = 1  " + tag("AREA-X-001") + "\n"), "x = 1\n")

    def test_a_real_trailing_comment_survives(self):
        got = self._strip("x = 1  " + tag("AREA-X-001") + "  # keep me\n")
        self.assertIn("keep me", got)
        self.assertTrue(got.endswith("\n"))

    def test_a_second_tag_on_the_same_line_survives(self):
        got = self._strip("def g():  " + tag("AREA-X-001") + "  " + tag("AREA-Y-002") + "\n"
                          "    return 2\n")
        self.assertIn("AREA-Y-002", got)
        self.assertNotIn("AREA-X-001", got)
        self.assertIn("    return 2\n", got)     # the body line is still its own line

    def test_a_tag_alone_on_its_line_still_removes_the_line(self):
        self.assertEqual(self._strip(tag("AREA-X-001") + "\ndef dead():\n    return 1\n"),
                         "def dead():\n    return 1\n")

    def test_a_js_line_comment_tag_leaves_the_code_intact(self):
        got = self._strip("function f() {  // " + "implements" + ": AREA-X-001\n"
                          "  return 1;\n}\n", name="m.js")
        self.assertEqual(got, "function f() {\n  return 1;\n}\n")

    def test_crlf_source_keeps_its_line_endings(self):
        got = self._strip("def f():\r\n    x = 1  " + tag("AREA-X-001") + "\r\n    return x\r\n")
        self.assertEqual(got, "def f():\r\n    x = 1\r\n    return x\r\n")


class DecomposeOnGroups(unittest.TestCase):  # tested-by: ARCH-DECOMPOSE-050  # tested-by: REQ-DECOMPOSE-994
    """`clarify <ID> --decompose` on a Description with bold group labels: one code-rung
    child per group, cases copied only on an unambiguous name match, no tags written, the
    parent never edited."""

    PARENT = """---
id: TOOL-UTILS
status: confirmed
level: architecture
layer: bus
owner: Ana
---

# Shared utilities

> WHY: one helper module, so nothing is reimplemented.

## Description
Every line in this section is binding.

**Module**
- The module uses only the standard library.

**`load_json_stdin(name)`**
- The function reads stdin and returns the parsed value.
- On empty stdin it exits 2 naming `name`.

**`is_headless()`**
- The function returns True only when `CLAUDE_HEADLESS` is exactly "1".

## Cases
CASE-1
  Given  empty stdin and the name "x.py"
  When   `load_json_stdin("x.py")` runs
  Then   it exits 2 and mentions x.py

CASE-2
  Given  `CLAUDE_HEADLESS` unset
  When   `is_headless()` runs, then `load_json_stdin` runs
  Then   both behave

CASE-3
  Given  any environment
  When   the package is imported
  Then   it imports cleanly

## Context
**Notes**
- prose that must survive untouched
"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.tmp, True)
        self.rd = os.path.join(self.tmp, "requirements"); os.makedirs(self.rd)
        _write(os.path.join(self.rd, "TOOL-UTILS.md"), self.PARENT)
        _write(os.path.join(self.tmp, "lib", "utils.py"),
               tag("TOOL-UTILS") + "\n\ndef load_json_stdin(name):\n    return 1\n\n"
               "def is_headless():\n    return False\n")

    def _run(self, only="TOOL-UTILS", apply_it=False):
        ws = R.Workspace.load(self.rd, self.tmp)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.cmd_decompose_groups(ws, only=only, apply_it=apply_it, code_root=self.tmp)
        return rc, buf.getvalue()

    def _files(self):
        return sorted(f for f in os.listdir(self.rd) if f.endswith(".md"))

    def test_the_authors_group_labels_are_the_seams(self):  # verifies: REQ-DECOMPOSE-994#CASE-1
        rc, _ = self._run(apply_it=True)
        self.assertEqual(rc, 0)
        self.assertEqual(self._files(), ["TOOL-UTILS-IS-HEADLESS.md", "TOOL-UTILS-LOAD-JSON-STDIN.md",
                                         "TOOL-UTILS-MODULE.md", "TOOL-UTILS.md"])
        child = io.open(os.path.join(self.rd, "TOOL-UTILS-LOAD-JSON-STDIN.md"), encoding="utf-8").read()
        for needle in ("level: code", "level_source: auto", "status: draft", "satisfies: [TOOL-UTILS]",
                       "- The function reads stdin and returns the parsed value.",
                       "- On empty stdin it exits 2 naming `name`."):
            self.assertIn(needle, child)

    def test_a_case_moves_only_when_it_names_exactly_one_subject(self):  # verifies: REQ-DECOMPOSE-994#CASE-2
        rc, out = self._run(apply_it=True)
        child = io.open(os.path.join(self.rd, "TOOL-UTILS-LOAD-JSON-STDIN.md"), encoding="utf-8").read()
        parent = io.open(os.path.join(self.rd, "TOOL-UTILS.md"), encoding="utf-8").read()
        self.assertIn("mentions x.py", child)            # CASE-1 named one subject: copied
        self.assertIn("mentions x.py", parent)            # ...and still on the parent
        for other in ("TOOL-UTILS-IS-HEADLESS.md", "TOOL-UTILS-MODULE.md"):
            text = io.open(os.path.join(self.rd, other), encoding="utf-8").read()
            self.assertNotIn("both behave", text)         # named two subjects: no child
        self.assertIn("2 to none", out)

    def test_no_tag_is_written_and_expected_members_are_listed(self):  # verifies: REQ-DECOMPOSE-994#CASE-3
        src_before = io.open(os.path.join(self.tmp, "lib", "utils.py"), encoding="utf-8").read()
        self._run(apply_it=True)
        src_after = io.open(os.path.join(self.tmp, "lib", "utils.py"), encoding="utf-8").read()
        self.assertEqual(src_before, src_after)
        child = io.open(os.path.join(self.rd, "TOOL-UTILS-IS-HEADLESS.md"), encoding="utf-8").read()
        self.assertIn("`lib/utils.py:", child)
        self.assertEqual(child.count("TOOL-UTILS-IS-HEADLESS"), 1)   # its own id only, no self-tag

    def test_too_many_groups_is_refused_not_split(self):  # verifies: REQ-DECOMPOSE-994#CASE-4
        groups = "".join("**g{}**\n- clause {}.\n\n".format(i, i) for i in range(R.LINT_AC_MAX + 1))
        body = self.PARENT.split("## Description")[0] + "## Description\n" + groups + "## Cases\nCASE-1 x\n"
        _write(os.path.join(self.rd, "TOOL-UTILS.md"), body)
        rc, out = self._run(apply_it=True)
        self.assertEqual(self._files(), ["TOOL-UTILS.md"])
        self.assertIn("refused", out)
        self.assertIn("**g0**", out)
        self.assertIn("Merge the labels", out)

    def test_the_dry_run_is_a_dry_run(self):  # verifies: REQ-DECOMPOSE-994#CASE-5
        before = {f: io.open(os.path.join(self.rd, f), encoding="utf-8").read() for f in self._files()}
        rc, out = self._run(apply_it=False)
        self.assertEqual(rc, 0)
        self.assertIn("Nothing written", out)
        self.assertIn("TOOL-UTILS-LOAD-JSON-STDIN", out)
        after = {f: io.open(os.path.join(self.rd, f), encoding="utf-8").read() for f in self._files()}
        self.assertEqual(before, after)

    def test_the_parent_is_never_edited(self):  # verifies: REQ-DECOMPOSE-994#CASE-6
        # Moving the text left 33 parents holding only `see [[child]]` pointers; deleting
        # the children then destroyed their contracts with a green gate. A copy cannot.
        before = io.open(os.path.join(self.rd, "TOOL-UTILS.md"), encoding="utf-8").read()
        self._run(apply_it=True)
        after = io.open(os.path.join(self.rd, "TOOL-UTILS.md"), encoding="utf-8").read()
        self.assertEqual(before, after)
        for f in self._files():
            if f != "TOOL-UTILS.md":
                os.remove(os.path.join(self.rd, f))      # reject the split
        groups = R._contract_groups(R.load_requirements(self.rd)["TOOL-UTILS"]["body"])
        self.assertEqual(["Module", "`load_json_stdin(name)`", "`is_headless()`"],
                         [label for label, _ in groups])
        self.assertIn("On empty stdin it exits 2 naming `name`.", groups[1][1])

    def test_a_label_with_a_note_after_it_is_still_a_group(self):  # verifies: REQ-DECOMPOSE-994#CASE-7
        # `**Label** (note)` was read as prose and glued onto the previous group's last
        # clause, label and all: five groups became three children.
        _write(os.path.join(self.rd, "TOOL-UTILS.md"), self.PARENT.replace(
            "**`is_headless()`**\n", "**`is_headless()`** (the environment probe)\n"))
        self._run(apply_it=True)
        self.assertIn("TOOL-UTILS-IS-HEADLESS.md", self._files())
        loader = io.open(os.path.join(self.rd, "TOOL-UTILS-LOAD-JSON-STDIN.md"),
                         encoding="utf-8").read()
        self.assertNotIn("is_headless", loader)
        self.assertNotIn("**", loader.split("## Description")[1].split("## Cases")[0]
                         .split("binding.")[1])

    def test_a_code_requirement_is_not_split(self):  # verifies: REQ-DECOMPOSE-994#CASE-4
        _write(os.path.join(self.rd, "TOOL-UTILS.md"),
               self.PARENT.replace("level: architecture", "level: code"))
        rc, out = self._run(apply_it=True)
        self.assertEqual(rc, 0)
        self.assertIn("level: code", out)
        self.assertEqual(self._files(), ["TOOL-UTILS.md"])
        reqs = R.load_requirements(self.rd)
        self.assertFalse(R.decomposable(reqs["TOOL-UTILS"]))
        self.assertIsNone(R.audittail._decompose_candidates_line(reqs))

    def test_a_requirement_with_no_groups_falls_through(self):
        _write(os.path.join(self.rd, "TOOL-UTILS.md"),
               self.PARENT.replace("**Module**\n", "").replace("**`load_json_stdin(name)`**\n", "")
               .replace("**`is_headless()`**\n", ""))
        rc, out = self._run(apply_it=True)
        self.assertIsNone(rc)                      # the caller then runs the clause-level path
        self.assertEqual(self._files(), ["TOOL-UTILS.md"])

    def test_sync_tail_names_the_fix_until_a_child_exists(self):  # verifies: REQ-AUDIT-973#CASE-1
        def tail():
            ws = R.Workspace.load(self.rd, self.tmp)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R._audit_summary(ws.reqs, ws.members, self.rd, self.tmp)
            return buf.getvalue()
        out = tail()
        self.assertIn("1 requirement(s) carry contract groups and no code children", out)
        self.assertIn("clarify --decompose", out)
        self._run(apply_it=True)                    # children now satisfy the parent
        self.assertNotIn("carry contract groups and no code children", tail())

    def test_corpus_wide_plans_every_grouped_requirement(self):
        _write(os.path.join(self.rd, "TOOL-OTHER.md"),
               self.PARENT.replace("id: TOOL-UTILS", "id: TOOL-OTHER"))
        _write(os.path.join(self.rd, "TOOL-FLAT.md"),
               "---\nid: TOOL-FLAT\nstatus: confirmed\n---\n\n# F\n\n## Description\n- one.\n\n## Cases\nCASE-1 x\n")
        rc, out = self._run(only=None, apply_it=False)
        self.assertIn("TOOL-UTILS  (3 contract groups", out)
        self.assertIn("TOOL-OTHER  (3 contract groups", out)
        self.assertNotIn("TOOL-FLAT  (", out)
        self.assertIn("6 child requirement(s) from 2 parent(s)", out)


class PlanMatchesWritePath(unittest.TestCase):  # tested-by: REQ-PLANTAGGED-1005 @unit  # tested-by: REQ-PLANLEVEL-1006 @unit  # tested-by: REQ-PLANDRAFTID-1010 @unit
    """`--plan` exists to say what `init` will write. Two things it got wrong: it counted
    only `implements:` as coverage (so tested-by-linked tests read as NEW drafts the write
    path would skip), and it carried no rung at all."""

    def _repo(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reqs = os.path.join(d, "requirements")
        os.makedirs(reqs)
        os.makedirs(os.path.join(d, "core"))
        os.makedirs(os.path.join(d, "tests"))
        _write(os.path.join(reqs, "ARCH-FOO-001.md"), _spec("ARCH-FOO-001", ["does a thing"]))
        _write(os.path.join(d, "core", "app.py"), tag("ARCH-FOO-001") + "\ndef f(): pass\n")
        _write(os.path.join(d, "tests", "test_app.py"),
               tb_tag("ARCH-FOO-001") + "\ndef test_f(): pass\n")
        return d, reqs

    def _plan(self, d, reqs):
        ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_candidates(ws, None)
        return json.loads(buf.getvalue()), ws

    def test_a_tested_by_file_is_not_reported_as_new(self):  # verifies: REQ-PLANTAGGED-1005#CASE-1
        d, reqs = self._repo()
        plan, _ws = self._plan(d, reqs)
        new = [c["suggested_id"] for c in plan["candidates"] if not c["existing_req"]]
        self.assertEqual(new, [], "a file linked by tested-by: is already accounted for")

    def test_plan_and_write_path_agree_on_what_is_new(self):  # verifies: REQ-PLANTAGGED-1005#CASE-2
        d, reqs = self._repo()
        plan, ws = self._plan(d, reqs)
        predicted = {c["suggested_id"] for c in plan["candidates"] if not c["existing_req"]}
        before = set(os.listdir(reqs))
        with redirect_stdout(io.StringIO()):
            R.cmd_extract(ws)
        wrote = {f for f in set(os.listdir(reqs)) - before if f.startswith("DRAFT-")}
        self.assertEqual(bool(predicted), bool(wrote))

    def test_an_untagged_file_is_still_reported(self):  # verifies: REQ-PLANTAGGED-1005#CASE-3
        d, reqs = self._repo()
        _write(os.path.join(d, "core", "loose.py"), "def g(): pass\n")
        plan, ws = self._plan(d, reqs)
        new = [c for c in plan["candidates"] if not c["existing_req"]]
        self.assertEqual([c["files"] for c in new], [["core/loose.py"]])
        before = set(os.listdir(reqs))
        with redirect_stdout(io.StringIO()):
            R.cmd_extract(ws)
        self.assertEqual(sorted(set(os.listdir(reqs)) - before),
                         ["ARCH-CORE-001.md", "DRAFT-CORE-LOOSE.md", R.SYS_PLACEHOLDER_ID + ".md"])

    def test_plan_carries_the_rung_and_the_pyramid(self):  # verifies: REQ-PLANLEVEL-1006#CASE-1
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reqs = os.path.join(d, "requirements")
        os.makedirs(reqs)
        os.makedirs(os.path.join(d, "core"))
        os.makedirs(os.path.join(d, "web"))
        _write(os.path.join(d, "core", "engine.py"), "def run(): pass\n")
        _write(os.path.join(d, "web", "views.py"), "def index(): pass\n")
        plan, _ws = self._plan(d, reqs)
        self.assertEqual(plan["pyramid"]["architecture"], ["ARCH-CORE-001", "ARCH-WEB-001"])
        self.assertEqual(plan["pyramid"]["system"], R.SYS_PLACEHOLDER_ID)
        got = {c["suggested_id"]: (c["level"], c["arch_id"]) for c in plan["candidates"]}
        self.assertEqual(got["CORE-ENGINE-001"], ("code", "ARCH-CORE-001"))
        self.assertEqual(got["WEB-VIEWS-001"], ("code", "ARCH-WEB-001"))

    def test_the_planned_pyramid_is_the_one_written(self):  # verifies: REQ-PLANLEVEL-1006#CASE-2
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reqs = os.path.join(d, "requirements")
        os.makedirs(reqs)
        os.makedirs(os.path.join(d, "core"))
        _write(os.path.join(d, "core", "engine.py"), "def run(): pass\n")
        plan, ws = self._plan(d, reqs)
        with redirect_stdout(io.StringIO()):
            R.cmd_extract(ws)
        written = R.load_requirements(reqs)
        for aid in plan["pyramid"]["architecture"]:
            self.assertIn(aid, written)
            self.assertEqual(written[aid]["meta"]["level"], "architecture")
        self.assertEqual(written[plan["pyramid"]["system"]]["meta"]["level"], "system")
        for c in plan["candidates"]:
            if c["level"] != "code":
                continue
            kid = next(r for r in written.values()
                       if r["meta"].get("level") == "code" and c["files"][0] in r["body"])
            self.assertEqual(R._as_list(kid["meta"]["satisfies"]), [c["arch_id"]])

    def test_draft_id_is_the_id_the_write_path_mints(self):  # verifies: REQ-PLANDRAFTID-1010#CASE-1
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reqs = os.path.join(d, "requirements")
        os.makedirs(reqs)
        os.makedirs(os.path.join(d, "core"))
        _write(os.path.join(d, "core", "engine.py"), "def run(): pass\n")
        plan, ws = self._plan(d, reqs)
        c = plan["candidates"][0]
        # the two ids differ ON PURPOSE and the plan states both, rather than renaming either
        self.assertEqual(c["suggested_id"], "CORE-ENGINE-001")
        self.assertEqual(c["draft_id"], "DRAFT-CORE-ENGINE")
        with redirect_stdout(io.StringIO()):
            R.cmd_extract(ws)
        written = R.load_requirements(reqs)
        self.assertIn(c["draft_id"], written)          # the plan predicted the written id
        self.assertNotIn(c["suggested_id"], written)   # and did not claim to be it

    def test_an_already_linked_candidate_carries_no_draft_id(self):  # verifies: REQ-PLANDRAFTID-1010#CASE-2
        d, reqs = self._repo()
        plan, _ws = self._plan(d, reqs)
        for c in plan["candidates"]:
            self.assertIsNone(c["draft_id"])   # not drafted: no id is claimed for it

    def test_the_draft_marker_is_untouched(self):  # verifies: REQ-PLANDRAFTID-1010#CASE-3
        # the whole point of disclosure over unification: `DRAFT-` stays the marker that a
        # requirement is an unreviewed auto-draft, which several call sites key on.
        self.assertTrue(R.draft._draft_id("core/engine.py").startswith("DRAFT-"))
        self.assertEqual(R.draft._draft_id("a/b.py"), R._draft_id("a/b.py"))

    def test_an_already_linked_candidate_gets_no_rung(self):  # verifies: REQ-PLANLEVEL-1006#CASE-3
        d, reqs = self._repo()
        plan, _ws = self._plan(d, reqs)
        for c in plan["candidates"]:
            self.assertIsNone(c["level"])        # not drafted -> no rung is claimed
            self.assertIsNone(c["arch_id"])
        self.assertEqual(plan["pyramid"], {"architecture": [], "system": None})


class InitTagsTheSource(unittest.TestCase):  # tested-by: REQ-INITTAG-1008 @unit
    """`init` wrote a stub and left the source untagged, so the file stayed in the untagged
    bucket forever while `gate --risk` kept proposing the `init` that had already run."""

    def _repo(self, files):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reqs = os.path.join(d, "requirements")
        os.makedirs(reqs)
        for rel, body in files.items():
            p = os.path.join(d, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(body)
        ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
        with redirect_stdout(io.StringIO()):
            R.cmd_extract(ws)
        return d, reqs

    def _read(self, d, rel):
        with open(os.path.join(d, rel.replace("/", os.sep)), encoding="utf-8", newline="") as f:
            return f.read()

    def test_the_drafted_source_becomes_a_member(self):  # verifies: REQ-INITTAG-1008#CASE-1
        d, reqs = self._repo({"core/engine.py": "def run(): pass\n"})
        members = R.scan_members(d, reqs)
        self.assertEqual({fp for hits in members.values() for _r, fp, _l in hits},
                         {"core/engine.py"})
        self.assertEqual(R.orphans._scan_untagged(d, reqs), [])      # the advice loop closes

    def test_the_comment_marker_matches_the_language(self):  # verifies: REQ-INITTAG-1008#CASE-2
        d, _reqs = self._repo({"core/a.py": "x = 1\n", "core/b.jsx": "export const B = 1;\n",
                               "core/c.css": "a { color: red }\n", "core/d.sql": "select 1;\n"})
        self.assertTrue(self._read(d, "core/a.py").startswith("# implements: "))
        self.assertTrue(self._read(d, "core/b.jsx").startswith("// implements: "))
        self.assertTrue(self._read(d, "core/c.css").startswith("/* implements: "))
        self.assertTrue(self._read(d, "core/d.sql").startswith("-- implements: "))

    def test_a_line_that_must_stay_first_stays_first(self):  # verifies: REQ-INITTAG-1008#CASE-3
        charset = "@charset " + chr(34) + "utf-8" + chr(34) + ";\n"
        d, _reqs = self._repo({"core/hook.py": "#!/usr/bin/env python\nx = 1\n",
                               "core/s.css": charset + "a { color: red }\n"})
        self.assertTrue(self._read(d, "core/hook.py").startswith("#!/usr/bin/env python\n"))
        self.assertTrue(self._read(d, "core/s.css").startswith(charset))

    def test_a_test_file_is_linked_as_tested_by(self):  # verifies: REQ-INITTAG-1008#CASE-4
        d, _reqs = self._repo({"tests/test_a.py": "def test_a(): pass\n"})
        self.assertTrue(self._read(d, "tests/test_a.py").startswith("# tested-by: "))

    def test_crlf_survives_the_insertion(self):  # verifies: REQ-INITTAG-1008#CASE-5
        d, _reqs = self._repo({"core/w.jsx": "export const A = 1;\r\nexport const B = 2;\r\n"})
        body = self._read(d, "core/w.jsx")
        self.assertIn("implements: ", body)
        self.assertEqual(body.count("\r\n"), 3)          # tag + both originals
        self.assertNotIn("\n", body.replace("\r\n", ""))  # not one line flattened to LF

    def test_an_already_tagged_source_is_left_alone(self):  # verifies: REQ-INITTAG-1008#CASE-7
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        reqs = os.path.join(d, "requirements")
        os.makedirs(reqs)
        _write(os.path.join(reqs, "ARCH-FOO-001.md"), _spec("ARCH-FOO-001", ["does a thing"]))
        body = tag("ARCH-FOO-001") + "\ndef f(): pass\n"
        _write(os.path.join(d, "app.py"), body)
        ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
        with redirect_stdout(io.StringIO()):
            R.cmd_extract(ws)
        self.assertEqual(self._read(d, "app.py").count("implements:"), 1)

    def test_wipe_then_init_is_a_fixed_point(self):  # verifies: REQ-INITTAG-1008#CASE-6
        d, reqs = self._repo({"core/engine.py": "#!/usr/bin/env python\ndef run(): pass\n"})
        seen = []
        for _ in range(3):
            with redirect_stdout(io.StringIO()):
                R.cmd_init(reqs, d, wipe=True)
            seen.append(self._read(d, "core/engine.py"))
        self.assertEqual(seen[0], seen[1])
        self.assertEqual(seen[1], seen[2])
        self.assertEqual(len(seen[0].splitlines()), 3)   # shebang + tag + code, never growing


def _release_repo(d, version="1.4.0", milestones=None, bars=None, changelog=None):
    """A minimal consumer repo: a version file, a plan, optionally a CHANGELOG."""
    reqs = os.path.join(d, "requirements")
    os.makedirs(reqs, exist_ok=True)
    if version:
        _write(os.path.join(d, "package.json"),
               '{\n  "name": "x",\n  "version": "%s",\n  "private": true\n}\n' % version)
    _write(os.path.join(reqs, "_planning.json"), json.dumps({
        "lanes": ["Feature"], "milestones": milestones or {}, "bars": bars or []}))
    if changelog is not None:
        _write(os.path.join(d, "CHANGELOG.md"), changelog)
    return reqs


def _release(d, reqs, version=True, apply_it=False, as_json=False):
    ws = R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs), reqs, d)
    out = io.StringIO()
    with redirect_stdout(out):
        rc = R.cmd_release(ws, d, reqs, version=version, apply_it=apply_it, as_json=as_json)
    return rc, out.getvalue()


def _text(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as f:
        return f.read()


class VersionFiles(unittest.TestCase):  # tested-by: REQ-VERSIONFILES-1014 @unit
    """Where a repository declares its version."""

    def test_the_usual_files_are_found_and_a_dependency_pin_is_not(self):  # verifies: REQ-VERSIONFILES-1014#CASE-1
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0")
            _write(os.path.join(d, "pyproject.toml"),
                   '[tool.black]\nversion = "9.9.9"\n\n[project]\nname = "x"\nversion = "1.4.0"\n')
            self.assertEqual([("package.json", "1.4.0"), ("pyproject.toml", "1.4.0")],
                             R.version_files(reqs, d))

    def test_a_configured_file_replaces_the_probe(self):  # verifies: REQ-VERSIONFILES-1014#CASE-2
        saved = R.config.VERSION_FILES
        try:
            with tempfile.TemporaryDirectory() as d:
                reqs = _release_repo(d, "1.4.0")
                _write(os.path.join(d, "meta", "VERSION"), "2.0.1\n")
                R.config.apply_config({"VERSION_FILES": ["meta/VERSION"]}, out=io.StringIO())
                self.assertEqual([("meta/VERSION", "2.0.1")], R.version_files(reqs, d))
        finally:
            R.config.VERSION_FILES = saved

    def test_a_bump_rewrites_the_version_and_nothing_else(self):  # verifies: REQ-VERSIONFILES-1014#CASE-3
        cargo = ('[package]\nname = "x"\nversion = "1.4.0"  # keep\n\n'
                 '[dependencies]\nserde = { version = "1.0" }\n')
        with tempfile.TemporaryDirectory() as d:
            _release_repo(d, "1.4.0")
            _write(os.path.join(d, "Cargo.toml"), cargo)
            self.assertTrue(R.write_version_file(os.path.join(d, "package.json"), "1.5.0"))
            self.assertTrue(R.write_version_file(os.path.join(d, "Cargo.toml"), "1.5.0"))
            self.assertEqual('{\n  "name": "x",\n  "version": "1.5.0",\n  "private": true\n}\n',
                             _text(d, "package.json"))
            self.assertEqual(cargo.replace('"1.4.0"', '"1.5.0"'), _text(d, "Cargo.toml"))

    def test_no_version_file_is_an_empty_answer(self):  # verifies: REQ-VERSIONFILES-1014#CASE-4
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, version=None)
            self.assertEqual([], R.version_files(reqs, d))

    def test_a_marketplace_moves_both_of_its_versions(self):  # verifies: REQ-VERSIONFILES-1014#CASE-5
        market = ('{\n  "version": "1.4.0",\n  "plugins": [\n'
                  '    {"name": "x", "version": "1.4.0"},\n'
                  '    {"name": "other", "version": "0.3.0"}\n  ]\n}\n')
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0")
            _write(os.path.join(d, ".claude-plugin", "marketplace.json"), market)
            self.assertIn((".claude-plugin/marketplace.json", "1.4.0"), R.version_files(reqs, d))
            self.assertTrue(R.write_version_file(
                os.path.join(d, ".claude-plugin", "marketplace.json"), "1.5.0"))
            self.assertEqual(market.replace('"1.4.0"', '"1.5.0"'),
                             _text(d, ".claude-plugin", "marketplace.json"))


class ChangelogForms(unittest.TestCase):  # tested-by: REQ-CHANGELOGFORMS-1015 @unit
    """A CHANGELOG is read in the convention its ecosystem writes it in."""

    LOG = ("# Changelog\n\n## [Unreleased]\n- pending\n\n## [1.2.0] - 2026-09-01\n**Big.**\n\n"
           "## v1.1.0 - 2026-08-01\nsmall\n\n## 1.0.0 (2026-07-01)\nfirst\n")

    def test_every_form_is_read_and_unreleased_is_not(self):  # verifies: REQ-CHANGELOGFORMS-1015#CASE-1
        got = R.history.parse_changelog(self.LOG)
        self.assertEqual([("v1.2.0", "2026-09-01", "Big"), ("v1.1.0", "2026-08-01", "small"),
                          ("v1.0.0", "2026-07-01", "first")],
                         [(e["version"], e["date"], e["headline"]) for e in got])

    def test_a_new_entry_follows_the_form_the_file_uses(self):  # verifies: REQ-CHANGELOGFORMS-1015#CASE-2
        h = R.history
        self.assertEqual("## [1.3.0] - 2026-09-20",
                         h.release_heading(h.changelog_style(self.LOG), "v1.3.0", "2026-09-20"))
        plugin = "## plugin `v7.1.0` — 2026-09-01\n**x.**\n"
        self.assertEqual("## plugin `v7.2.0` — 2026-09-20",
                         h.release_heading(h.changelog_style(plugin), "v7.2.0", "2026-09-20"))
        self.assertEqual("keep", h.changelog_style(""))

    def test_init_seeds_a_changelog_once_and_does_not_scan_it(self):  # verifies: REQ-CHANGELOGFORMS-1015#CASE-3
        with tempfile.TemporaryDirectory() as d:
            reqs = os.path.join(d, "requirements")
            with redirect_stdout(io.StringIO()):
                R.cmd_init(reqs, d)
            self.assertIn("## [Unreleased]", _text(d, "CHANGELOG.md"))
            _write(os.path.join(d, "CHANGELOG.md"), "# mine\n")
            with redirect_stdout(io.StringIO()):
                R.cmd_init(reqs, d)
            self.assertEqual("# mine\n", _text(d, "CHANGELOG.md"))
            self.assertIn("CHANGELOG.md", _text(d, ".reqmapignore").splitlines())


class VersionAlignment(unittest.TestCase):  # tested-by: REQ-VERSIONALIGN-1016 @unit
    """Where the version files, the CHANGELOG and the tags disagree."""

    def test_files_that_disagree_are_named(self):  # verifies: REQ-VERSIONALIGN-1016#CASE-1
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0")
            _write(os.path.join(d, "VERSION"), "1.3.0\n")
            lines = R.version_alignment_lines(reqs, d)
            self.assertEqual(1, sum("version files disagree" in ln for ln in lines))

    def test_a_changelog_behind_the_files_asks_for_the_entry(self):  # verifies: REQ-VERSIONALIGN-1016#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", changelog="## [1.3.0] - 2026-09-01\n**x.**\n")
            lines = R.version_alignment_lines(reqs, d)
            self.assertTrue(any("v1.3.0" in ln and "write its entry" in ln for ln in lines))

    def test_a_tag_below_the_files_is_the_normal_state(self):  # verifies: REQ-VERSIONALIGN-1016#CASE-3
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", changelog="## [1.4.0] - 2026-09-01\n**x.**\n")
            with mock.patch.object(R.versions, "newest_tag", return_value=((1, 3, 0), "v1.3.0")):
                self.assertEqual([], R.version_alignment_lines(reqs, d))

    def test_a_tag_above_the_files_is_reported(self):  # verifies: REQ-VERSIONALIGN-1016#CASE-4
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", changelog="## [1.4.0] - 2026-09-01\n**x.**\n")
            with mock.patch.object(R.versions, "newest_tag", return_value=((1, 5, 0), "v1.5.0")):
                lines = R.version_alignment_lines(reqs, d)
            self.assertEqual(1, sum("git tag v1.5.0 is above" in ln for ln in lines))


class NextVersion(unittest.TestCase):  # tested-by: REQ-NEXTVERSION-1017 @unit
    """The next release's number is read from the plan."""

    def test_the_lowest_planned_version_above_the_baseline(self):  # verifies: REQ-NEXTVERSION-1017#CASE-1
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", milestones={
                "v1.4.0": {"due": "2026-09-01"}, "v1.6.0": {"due": "2026-10-09"},
                "v1.5.0": {"due": "2026-10-02"}})
            self.assertEqual("v1.5.0", R.next_planned_version(reqs, d))

    def test_nothing_planned_above_the_baseline_is_none(self):  # verifies: REQ-NEXTVERSION-1017#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", milestones={"v1.4.0": {"due": "2026-09-01"}})
            self.assertIsNone(R.next_planned_version(reqs, d))

    def test_a_bar_milestone_counts_as_planned(self):  # verifies: REQ-NEXTVERSION-1017#CASE-3
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", bars=[{"title": "b", "start": "2026-09-21",
                                                    "milestone": "v1.4.1"}])
            self.assertEqual("v1.4.1", R.next_planned_version(reqs, d))


class ReleaseCommand(unittest.TestCase):  # tested-by: REQ-RELEASECMD-1018 @unit  # tested-by: REQ-PLANADVANCE-1020 @unit
    """`sync --release`: plan first, write only with --apply."""

    PLAN = {"v1.5.0": {"due": "2026-10-02", "label": "Export to CSV"},
            "v1.6.0": {"due": "2026-10-09"}}
    BARS = [{"title": "CSV writer", "start": "2026-09-28", "end": "2026-10-02",
             "milestone": "v1.5.0", "req": "REQ-CSV-001"},
            {"title": "Later thing", "start": "2026-10-05", "milestone": "v1.6.0"}]

    def test_a_dry_run_writes_nothing(self):  # verifies: REQ-RELEASECMD-1018#CASE-1
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", self.PLAN, self.BARS, changelog="# Changelog\n")
            before = (_text(d, "package.json"), _text(d, "CHANGELOG.md"),
                      _text(reqs, "_planning.json"))
            rc, out = _release(d, reqs)
            self.assertEqual(0, rc)
            self.assertIn("release v1.5.0", out)
            self.assertEqual(before, (_text(d, "package.json"), _text(d, "CHANGELOG.md"),
                                      _text(reqs, "_planning.json")))

    def test_apply_bumps_the_files_and_writes_the_entry_under_unreleased(self):  # verifies: REQ-RELEASECMD-1018#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", self.PLAN, self.BARS,
                                 changelog="# Changelog\n\n## [Unreleased]\n- collected fix\n")
            rc, _ = _release(d, reqs, apply_it=True)
            self.assertEqual(0, rc)
            self.assertIn('"version": "1.5.0"', _text(d, "package.json"))
            log = _text(d, "CHANGELOG.md")
            self.assertLess(log.index("## [Unreleased]"), log.index("## [1.5.0] - "))
            self.assertEqual("**Export to CSV.**\n\n- CSV writer (REQ-CSV-001)\n- collected fix",
                             R.history.entry_body(log, "v1.5.0"))

    def test_apply_with_nothing_planned_is_refused(self):  # verifies: REQ-RELEASECMD-1018#CASE-3
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0")
            rc, out = _release(d, reqs, apply_it=True)
            self.assertEqual(2, rc)
            self.assertIn("no planned milestone above v1.4.0", out)
            self.assertIn('"version": "1.4.0"', _text(d, "package.json"))

    def test_a_named_version_not_above_the_baseline_is_refused(self):  # verifies: REQ-RELEASECMD-1018#CASE-4
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", self.PLAN, self.BARS)
            rc, out = _release(d, reqs, version="v1.4.0", apply_it=True)
            self.assertEqual(2, rc)
            self.assertIn("v1.4.0 is not above v1.4.0", out)

    def test_a_second_apply_does_not_write_the_entry_twice(self):  # verifies: REQ-RELEASECMD-1018#CASE-5
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", self.PLAN, self.BARS, changelog="# Changelog\n")
            _release(d, reqs, version="v1.5.0", apply_it=True)
            with mock.patch.object(R.release, "shipped_baseline", return_value=None):
                _release(d, reqs, version="v1.5.0", apply_it=True)
            self.assertEqual(1, _text(d, "CHANGELOG.md").count("## [1.5.0]"))

    def test_the_plan_drops_the_released_version_and_keeps_the_rest(self):  # verifies: REQ-PLANADVANCE-1020#CASE-1
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", self.PLAN, self.BARS, changelog="# Changelog\n")
            _release(d, reqs, apply_it=True)
            plan = json.loads(_text(reqs, "_planning.json"))
            self.assertEqual(["v1.6.0"], list(plan["milestones"]))
            self.assertEqual(["Later thing"], [b["title"] for b in plan["bars"]])
            self.assertEqual(["Feature"], plan["lanes"])

    def test_after_a_release_the_plan_is_current_and_names_the_next(self):  # verifies: REQ-PLANADVANCE-1020#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", self.PLAN, self.BARS, changelog="# Changelog\n")
            _release(d, reqs, apply_it=True)
            self.assertIsNone(R.stale_plan_milestones(reqs, d))
            self.assertEqual([], R.version_alignment_lines(reqs, d))
            self.assertEqual("v1.6.0", R.next_planned_version(reqs, d))

    def test_a_dry_run_leaves_the_plan_as_it_was(self):  # verifies: REQ-PLANADVANCE-1020#CASE-3
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", self.PLAN, self.BARS, changelog="# Changelog\n")
            before = _text(reqs, "_planning.json")
            self.assertEqual(0, _release(d, reqs)[0])
            self.assertEqual(before, _text(reqs, "_planning.json"))


class ReleaseWorkflow(unittest.TestCase):  # tested-by: REQ-RELEASEWORKFLOW-1019 @unit
    """`init` gives a GitHub repo the workflow that tags the declared version once."""

    WORKFLOW = os.path.join(".github", "workflows", "reqmap-release.yml")

    def test_init_seeds_the_workflow_on_a_github_repo(self):  # verifies: REQ-RELEASEWORKFLOW-1019#CASE-1
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".github"))
            with mock.patch.object(R.release, "release_workflow",
                                   return_value="name: release\nsync --release --json\n"):
                with redirect_stdout(io.StringIO()):
                    R.cmd_init(os.path.join(d, "requirements"), d)
            self.assertEqual("name: release\nsync --release --json\n", _text(d, self.WORKFLOW))

    def test_an_existing_workflow_is_never_overwritten(self):  # verifies: REQ-RELEASEWORKFLOW-1019#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, self.WORKFLOW), "mine\n")
            created, _ = R.seed_release_files(d, os.path.join(d, "requirements"))
            self.assertNotIn(".github/workflows/reqmap-release.yml", created)
            self.assertEqual("mine\n", _text(d, self.WORKFLOW))

    def test_a_repo_off_github_gets_no_workflow(self):  # verifies: REQ-RELEASEWORKFLOW-1019#CASE-3
        with tempfile.TemporaryDirectory() as d:
            with redirect_stdout(io.StringIO()):
                R.cmd_init(os.path.join(d, "requirements"), d)
            self.assertFalse(os.path.exists(os.path.join(d, ".github")))

    def test_the_workflow_runs_the_vendored_engine_and_releases_once(self):  # verifies: REQ-RELEASEWORKFLOW-1019#CASE-4
        scripts = os.path.dirname(os.path.dirname(os.path.abspath(R.release.__file__)))
        root = os.path.dirname(scripts)
        text = R.release_workflow(root, os.path.join(root, "requirements"))
        self.assertIn("python {}/reqmap.py sync --release --json --reqs requirements --code ."
                      .format(os.path.basename(scripts)), text)
        self.assertIn('[ "$exists" = "true" ]', text)
        self.assertIn("gh release create", text)
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R.release_workflow(d, os.path.join(d, "requirements")))
            # an engine on another Windows drive: relpath raises instead of answering ".."
            with mock.patch.object(R.release.os.path, "relpath",
                                   side_effect=ValueError("path is on mount 'D:'")):
                self.assertIsNone(R.release_workflow(d, os.path.join(d, "requirements")))

    def test_json_reports_the_declared_version_its_tag_and_notes(self):  # verifies: REQ-RELEASEWORKFLOW-1019#CASE-5
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.5.0",
                                 changelog="## [1.5.0] - 2026-10-02\n**Export to CSV.**\n")
            _, out = _release(d, reqs, as_json=True)
            got = json.loads(out)
            self.assertEqual(("v1.5.0", False, "**Export to CSV.**"),
                             (got["declared"], got["tag_exists"], got["notes"]))


class ReleaseEndToEnd(unittest.TestCase):  # tested-by: ARCH-RELEASE-072 @integration
    """init, plan, release, through the command line."""

    def _run(self, d, *args):
        engine = os.path.join(os.path.dirname(os.path.abspath(R.__file__)), "reqmap.py")
        return subprocess.run([sys.executable, "-X", "utf8", engine] + list(args)
                              + ["--reqs", "requirements", "--code", "."],
                              cwd=d, capture_output=True, text=True, encoding="utf-8")

    def test_init_then_release_through_the_cli(self):  # verifies: ARCH-RELEASE-072#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "package.json"), '{"name": "x", "version": "0.1.0"}\n')
            self.assertEqual(0, self._run(d, "init", "--no-site").returncode)
            plan = os.path.join(d, "requirements", "_planning.json")
            data = json.loads(_text(plan))
            data["milestones"] = {"v0.2.0": {"due": "2026-10-02", "label": "First feature"}}
            _write(plan, json.dumps(data))
            done = self._run(d, "sync", "--release", "--apply")
            self.assertEqual(0, done.returncode, done.stdout + done.stderr)
            self.assertIn('"version": "0.2.0"', _text(d, "package.json"))
            self.assertIn("## [0.2.0] - ", _text(d, "CHANGELOG.md"))

    def test_nothing_planned_is_refused_through_the_cli(self):  # verifies: ARCH-RELEASE-072#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "package.json"), '{"name": "x", "version": "0.1.0"}\n')
            self.assertEqual(0, self._run(d, "init", "--no-site").returncode)
            done = self._run(d, "sync", "--release", "--apply")
            self.assertEqual(2, done.returncode, done.stdout + done.stderr)
            self.assertIn('"version": "0.1.0"', _text(d, "package.json"))

    def test_a_hand_bump_is_reported_by_the_audit_and_fails_nothing(self):  # verifies: ARCH-RELEASE-072#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "package.json"), '{"name": "x", "version": "0.1.0"}\n')
            self.assertEqual(0, self._run(d, "init", "--no-site").returncode)
            _write(os.path.join(d, "package.json"), '{"name": "x", "version": "0.3.0"}\n')
            _write(os.path.join(d, "CHANGELOG.md"), "# Changelog\n\n## [0.1.0] - 2026-09-01\n**First.**\n")
            audit = self._run(d, "gate", "--audit")
            self.assertEqual(0, audit.returncode, audit.stdout + audit.stderr)
            self.assertIn("while the version files declare v0.3.0", audit.stdout)


class PlanDates(unittest.TestCase):  # tested-by: REQ-PLANDATES-1022 @unit
    """`sync` suggests a bar's date when the work it names finished, or ran over."""

    REQS = {"REQ-DONE-001": {"meta": {"status": "confirmed"}},
            "REQ-OPEN-002": {"meta": {"status": "draft"}}}
    MEMBERS = {"REQ-DONE-001": [("implements", "src/done.py", 1),
                                ("tested-by", "tests/test_done.py", 1)],
               "REQ-OPEN-002": [("implements", "src/open.py", 1)]}

    def _suggest(self, bars, touched="2026-09-12", today="2026-09-16"):
        with mock.patch.object(R.plandrift, "_last_touched", return_value=touched):
            return R.bar_date_suggestions(bars, self.REQS, self.MEMBERS, ".", today)

    def test_work_done_early_suggests_the_real_end(self):  # verifies: REQ-PLANDATES-1022#CASE-1
        got = self._suggest([{"title": "A", "req": "REQ-DONE-001",
                              "start": "2026-09-07", "end": "2026-10-02"}])
        self.assertEqual([("done", "2026-10-02", "2026-09-12")],
                         [(s["kind"], s["planned"], s["actual"]) for s in got])
        self.assertIn("set its `end` to 2026-09-12", R.bar_date_lines(got)[0])

    def test_work_that_matches_its_plan_is_silent(self):  # verifies: REQ-PLANDATES-1022#CASE-2
        self.assertEqual([], self._suggest([{"title": "A", "req": "REQ-DONE-001",
                                             "start": "2026-09-07", "end": "2026-09-12"}]))

    def test_code_older_than_the_bar_is_not_its_finish(self):  # verifies: REQ-PLANDATES-1022#CASE-3
        self.assertEqual([], self._suggest([{"title": "A", "req": "REQ-DONE-001",
                                             "start": "2026-09-14", "end": "2026-10-02"}]))

    def test_an_open_requirement_past_its_end_is_overdue(self):  # verifies: REQ-PLANDATES-1022#CASE-4
        got = self._suggest([{"title": "B", "req": "REQ-OPEN-002",
                              "start": "2026-09-01", "end": "2026-09-10"},
                             {"title": "C", "req": "REQ-OPEN-002",
                              "start": "2026-09-14", "end": "2026-09-30"},
                             {"title": "D", "start": "2026-09-01", "end": "2026-09-02"}])
        self.assertEqual([("B", "overdue")], [(s["title"], s["kind"]) for s in got])
        self.assertIn("move its `end`", R.bar_date_lines(got)[0])


class RoadmapAndBars(unittest.TestCase):  # tested-by: REQ-RELEASEROADMAP-1023 @unit  # tested-by: REQ-UNPLANNED-1024 @unit
    """ROADMAP items against the bars that schedule them."""

    ITEMS = [
        {"name": "CSV writer", "horizon": "now", "req": "REQ-CSV-001", "done": False},
        {"name": "Parser speed", "horizon": "next", "req": "REQ-PARSE-002", "done": False},
        {"name": "Viewer A", "horizon": "next", "req": "REQ-VIEW-003", "done": False},
        {"name": "Viewer B", "horizon": "next", "req": "REQ-VIEW-003", "done": False},
        {"name": "Shipped", "horizon": "now", "req": "REQ-OLD-004", "done": True},
        {"name": "Someday", "horizon": "later", "req": None, "done": False},
    ]

    def test_a_release_suggests_ticking_the_items_its_bars_carry_out(self):  # verifies: REQ-RELEASEROADMAP-1023#CASE-1
        bars = [{"title": "csv writer", "req": "REQ-OTHER"},
                {"title": "Speed-up", "req": "REQ-PARSE-002"},
                {"title": "Viewer work", "req": "REQ-VIEW-003"}]
        self.assertEqual(["CSV writer", "Parser speed"],
                         [it["name"] for it in R.items_for_bars(self.ITEMS, bars)])

    def test_a_done_item_is_never_suggested(self):  # verifies: REQ-RELEASEROADMAP-1023#CASE-3
        self.assertEqual([], R.items_for_bars(self.ITEMS, [{"title": "Shipped", "req": "REQ-OLD-004"}]))

    def test_the_release_plan_names_the_items_and_writes_none(self):  # verifies: REQ-RELEASEROADMAP-1023#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = _release_repo(d, "1.4.0", {"v1.5.0": {"due": "2026-10-02"}},
                                 [{"title": "CSV writer", "start": "2026-09-28",
                                   "milestone": "v1.5.0"}], changelog="# Changelog\n")
            roadmap = "# Roadmap\n\n## Now\n\n- [ ] CSV writer | req: REQ-CSV-001\n"
            _write(os.path.join(d, "ROADMAP.md"), roadmap)
            rc, out = _release(d, reqs, apply_it=True)
            self.assertEqual(0, rc)
            self.assertIn("tick     ROADMAP.md (by hand, if it is done): CSV writer", out)
            self.assertEqual(roadmap, _text(d, "ROADMAP.md"))

    def test_now_and_next_items_without_a_bar_are_counted(self):  # verifies: REQ-UNPLANNED-1024#CASE-1
        bars = [{"title": "CSV writer"}, {"title": "x", "req": "REQ-VIEW-003"}]
        self.assertEqual(["Parser speed"],
                         [it["name"] for it in R.unplanned_items(self.ITEMS, bars)])
        self.assertIn("1 Now/Next ROADMAP item(s) have no bar", R.unplanned_line(self.ITEMS, bars))

    def test_everything_scheduled_is_silent(self):  # verifies: REQ-UNPLANNED-1024#CASE-2
        bars = [{"title": "CSV writer"}, {"title": "y", "req": "REQ-PARSE-002"},
                {"title": "x", "req": "REQ-VIEW-003"}]
        self.assertIsNone(R.unplanned_line(self.ITEMS, bars))
        self.assertIsNone(R.unplanned_line(None, bars))

    def test_done_and_later_items_are_never_counted(self):  # verifies: REQ-UNPLANNED-1024#CASE-3
        self.assertEqual(["CSV writer", "Parser speed", "Viewer A", "Viewer B"],
                         [it["name"] for it in R.unplanned_items(self.ITEMS, [])])


class Site(unittest.TestCase):  # tested-by: ARCH-SITE-026
    """The project site: `sync` refreshes the engine-owned regions of
    docs/architecture.html and `init` scaffolds it."""
    # tested-by: REQ-SITE-924

    def _seed(self, d):
        reqs = os.path.join(d, "requirements")
        _write(os.path.join(reqs, "AREA-X-001.md"),
               "---\nid: AREA-X-001\nstatus: confirmed\nlayer: feature\n"
               "---\n# X\n> why\n")
        return reqs

    def _ws(self, d, reqs):
        return R.Workspace(R.load_requirements(reqs), R.scan_members(d, reqs))

    def _site(self, d, reqs, page, regions):
        with redirect_stdout(io.StringIO()):
            return R.cmd_site(self._ws(d, reqs), d, page, regions)

    def test_remote_url_normalises_scp_ssh_and_https(self):
        want = "https://github.com/o/r"
        self.assertEqual(want, R._normalise_remote("git@github.com:o/r.git"))
        self.assertEqual(want,
                         R._normalise_remote("https://github.com/o/r.git"))
        self.assertEqual(want,
                         R._normalise_remote("ssh://git@github.com:2222/o/r"))
        self.assertIsNone(R._normalise_remote(""))

    def test_remote_override(self):
        with mock.patch.dict(os.environ, {"REQMAP_REPO": "o/r"}):
            self.assertEqual("https://github.com/o/r",
                             R._git_remote_web_url("."))
        with mock.patch.dict(os.environ, {"REQMAP_REPO": ""}):
            self.assertIsNone(R._git_remote_web_url("."))

    def test_inject_region_refreshes_and_preserves_prose(self):
        html = ("<body>\n<h1>AUTHORED</h1>\n"
                "<!--##REQMAP:NAV##-->old<!--##/REQMAP:NAV##-->\n</body>")
        out = R._inject_region(html, "nav", "NEW")
        self.assertIn("<!--##REQMAP:NAV##-->\nNEW\n<!--##/REQMAP:NAV##-->",
                      out)
        self.assertIn("<h1>AUTHORED</h1>", out)
        self.assertNotIn("old", out)

    def test_inject_region_absent_goes_after_body_with_attributes(self):
        out = R._inject_region('<body class="x">\n<h1>hi</h1>\n</body>',
                               "nav", "NEW")
        self.assertLess(out.index("<body"), out.index("REQMAP:NAV"))
        self.assertLess(out.index("REQMAP:NAV"), out.index("</body>"))

    def test_inject_region_close_before_open_no_duplicate(self):
        html = ("<body>\n<!--##/REQMAP:NAV##-->stray\n"
                "<!--##REQMAP:NAV##-->old<!--##/REQMAP:NAV##-->\n</body>")
        out = R._inject_region(html, "nav", "NEW")
        self.assertEqual(1, out.count("<!--##REQMAP:NAV##-->"))
        self.assertNotIn("old", out)

    def test_extract_region_roundtrip(self):
        html = R._inject_region("<body></body>", "stats", "DATA")
        self.assertEqual("DATA", R._extract_region(html, "stats"))
        self.assertIsNone(R._extract_region("<body></body>", "stats"))

    def test_render_nav_omits_absent_targets(self):
        # verifies: REQ-SITE-924#CASE-3
        nav = R._render_region("nav", {"repo_url": None, "map_ok": False})
        self.assertNotIn("<a", nav)
        self.assertIn('class="nav-links"', nav)
        nav = R._render_region("nav", {"repo_url": "https://github.com/o/r",
                                       "map_ok": True})
        self.assertIn('href="https://github.com/o/r"', nav)
        self.assertIn('href="map.html"', nav)

    def test_render_nav_escapes_repo_url(self):
        nav = R._render_region("nav", {"repo_url": "https://x/<script>",
                                       "map_ok": False})
        self.assertNotIn("<script>", nav)
        self.assertIn("&lt;script&gt;", nav)

    def test_render_stats_counts_from_graph(self):
        data = {"nodes": [{"id": "A-1", "layer": "bus",
                           "status": "confirmed"},
                          {"id": "B-2", "layer": "feature",
                           "status": "confirmed"},
                          {"id": "C-3", "layer": "feature",
                           "status": "draft"}],
                "edges": [["B-2", "A-1"]]}
        ctx = R._site_context_from_data(data, repo_url=None, map_ok=False)
        stats = R._render_region("stats", ctx)
        self.assertTrue(stats.startswith('<div class="stat">'))
        self.assertIn("<b>3</b><span>requirements", stats)
        self.assertIn("<b>2</b><span>confirmed", stats)
        self.assertIn(R.MAP_ENGINE_VERSION, stats)

    def test_attach_is_idempotent(self):  # verifies: REQ-SITE-924#CASE-1
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            _write(page, "<body>\n<h1>Mine</h1>\n</body>")
            self._site(d, reqs, page, ["nav", "stats"])
            first = _text(page)
            self._site(d, reqs, page, ["nav", "stats"])
            second = _text(page)
            self.assertEqual(first, second)
            self.assertIn("<h1>Mine</h1>", second)

    def test_no_remote_degrades(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            _write(page, "<body></body>")
            with mock.patch.object(R.site, "_git_remote_web_url",
                                   return_value=None):
                rc = self._site(d, reqs, page, ["nav"])
            self.assertEqual(0, rc)
            self.assertNotIn("GitHub", _text(page))

    def test_scaffold_writes_full_page(self):  # verifies: REQ-SITE-924#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            target = os.path.join(d, "docs", "architecture.html")
            self._site(d, reqs, target, ["nav", "stats"])
            html = _text(target)
            self.assertIn("<!--##REQMAP:NAV##-->", html)
            self.assertIn("<!--##REQMAP:STATS##-->", html)
            self.assertIn("<!-- author me -->", html)
            self.assertNotIn("%%REPO", html)

    def test_scaffold_escapes_repo_name(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            target = os.path.join(d, "docs", "architecture.html")
            with mock.patch.object(R.site, "_repo_name",
                                   return_value='x"><script>bad</script>'), \
                 mock.patch.object(R.site, "_git_remote_web_url",
                                   return_value=None):
                self._site(d, reqs, target, ["nav"])
            html = _text(target)
            self.assertNotIn("<script>bad</script>", html)
            self.assertIn("&lt;script&gt;", html)

    def test_pages_bootstrap_never_clobbers_index(self):
        # verifies: REQ-SITE-924#CASE-4
        with tempfile.TemporaryDirectory() as d:
            docs = os.path.join(d, "docs")
            index = os.path.join(docs, "index.html")
            _write(index, "<h1>landing</h1>")
            R._site_pages_bootstrap(docs)
            self.assertEqual("<h1>landing</h1>",
                             _text(index))
            self.assertTrue(os.path.isfile(os.path.join(docs, ".nojekyll")))
            fresh = os.path.join(d, "fresh")
            R._site_pages_bootstrap(fresh)
            self.assertIn("./architecture.html",
                          _text(os.path.join(fresh, "index.html")))
            self.assertTrue(os.path.isfile(os.path.join(fresh, ".nojekyll")))

    def test_init_scaffolds_site_when_absent(self):
        # verifies: REQ-SITE-924#CASE-5
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            _write(os.path.join(d, "a.py"), "x = 1\n")
            with redirect_stdout(io.StringIO()):
                R.cmd_init(os.path.join(d, "requirements"), d, no_site=False)
            page = os.path.join(d, "docs", "architecture.html")
            self.assertIn("<!--##REQMAP:NAV##-->",
                          _text(page))
            self.assertTrue(os.path.isfile(
                os.path.join(d, "docs", "index.html")))

    def test_init_no_site_flag_skips(self):  # verifies: REQ-SITE-924#CASE-5
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            _write(os.path.join(d, "a.py"), "x = 1\n")
            with redirect_stdout(io.StringIO()):
                R.cmd_init(os.path.join(d, "requirements"), d, no_site=True)
            self.assertFalse(os.path.exists(
                os.path.join(d, "docs", "architecture.html")))

    def test_site_stale_fires_only_after_tampering(self):
        # verifies: REQ-SITE-924#CASE-6
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "docs", "architecture.html")
            self._site(d, reqs, page, ["stats"])
            ws = self._ws(d, reqs)
            data = R._build_map_data(ws.reqs, ws.members)
            self.assertIsNone(R.site_stale(data, d))
            cur = _text(page)
            _write(page, cur.replace(R._extract_region(cur, "stats"),
                                     "TAMPERED"))
            self.assertEqual("architecture.html", R.site_stale(data, d))

    def test_sync_refreshes_the_default_page(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            page = os.path.join(d, "docs", "architecture.html")
            _write(page, "<body><!--##REQMAP:STATS##-->0"
                         "<!--##/REQMAP:STATS##--></body>")
            old = sys.argv
            sys.argv = ["reqmap", "sync", "--root", d]
            try:
                # the verdict is not under test: only what a passing sync does
                with mock.patch.object(R, "cmd_check", return_value=0), \
                     redirect_stdout(io.StringIO()), \
                     redirect_stderr(io.StringIO()):
                    R.main()
            finally:
                sys.argv = old
            html = _text(page)
            self.assertIn("<b>1</b><span>requirements", html)
            self.assertIn("<!--##REQMAP:NAV##-->", html)
