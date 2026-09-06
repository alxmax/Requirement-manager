"""Writing requirements: `new`, `promote`, `init`, extraction and candidates, the
readability linter, `clarify`/`--decompose`, `implement`, `retire` and the level retrofit.

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


class New(unittest.TestCase):  # tested-by: ARCH-NEW-004  # tested-by: REQ-NEW-881  # tested-by: REQ-NEW-882
    def test_new_scaffolds_from_template_and_substitutes_id(self):  # verifies: REQ-NEW-881#CASE-1  # verifies: REQ-NEW-881#CASE-2  # verifies: REQ-NEW-881#CASE-4
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

    def test_new_uses_builtin_template_when_no_file(self):  # verifies: REQ-NEW-881#CASE-3
        with tempfile.TemporaryDirectory() as d:
            reqs_dir = os.path.join(d, "reqs")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_new(reqs_dir, None, "CORE-FOO-001")   # no on-disk template
            self.assertEqual(code, 0)
            content = open(os.path.join(reqs_dir, "CORE-FOO-001.md"), encoding="utf-8").read()
            self.assertIn("CORE-FOO-001", content)
            self.assertNotIn("AREA-NAME-NNN", content)
            self.assertIn("## Description", content)           # current emission schema
            self.assertIn("## Cases", content)
            self.assertIn("CASE-1", content)
            self.assertIn("Cases (= tests)", content)          # from the built-in scaffold

    def test_new_refuses_to_overwrite_existing(self):  # verifies: REQ-NEW-882#CASE-1
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

    def test_template_uses_the_plain_present_voice(self):  # verifies: REQ-NEW-882#CASE-2
        t = R.REQUIREMENT_TEMPLATE
        self.assertIn("Every bullet below is binding.", t)
        # No CLAUSE may use a modal — but the guidance comment must stay free to name
        # 'shall' as the thing not to write, which is the clearest way to say it.
        # Comments are stripped whole: _lint_prose yields each line of a multi-line
        # comment separately, so filtering on a leading '<!--' would only drop the first.
        clauses = R._lint_prose(re.sub(r"<!--.*?-->", "", t, flags=re.DOTALL), "description")
        self.assertTrue(clauses)                       # guard: the section actually parsed
        for ln in clauses:
            self.assertNotIn("shall", ln.lower())
            self.assertNotIn("must", ln.lower())

    def test_template_contract_body_passes_its_own_linter(self):  # verifies: REQ-NEW-882#CASE-3
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
        # tag picked up. Reload the module so the module-level extension merge re-runs.
        import importlib
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "src", "widget.foo"),
                   "// {}: AREA-FEATURE-001\n".format(_ROLE))
            _write(os.path.join(d, "src", "helper.bar"),
                   "// {}: AREA-FEATURE-001\n".format(_ROLE))
            with mock.patch.dict(os.environ, {"REQMAP_EXTRA_CODE_EXTS": ".foo, bar"}):
                importlib.reload(R)
                try:
                    members = R.scan_members(d, os.path.join(d, "requirements"))
                finally:
                    importlib.reload(R)  # restore default CODE_EXTS for other tests
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


class Init(unittest.TestCase):  # tested-by: ARCH-INIT-012  # tested-by: REQ-INIT-860  # tested-by: REQ-INIT-861
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

    def test_over_scoped_fires_only_on_both_ceilings(self):  # composite cohesion signal  # verifies: REQ-LINTCHECKS-866#CASE-3  # verifies: ARCH-LINTCHECKS-025#CASE-5
        big_contract = "".join("- clause {}.\n".format(i) for i in range(R.LINT_CONTRACT_MAX + 1))
        big_ac = "".join("- AC {}.\n".format(i) for i in range(R.LINT_AC_MAX + 1))
        small_ac = "".join("- AC {}.\n".format(i) for i in range(3))
        over = R.lint_requirement("REQ-BIG-001", self._req("confirmed", self._body(big_contract, big_ac)))
        self.assertIn("over-scoped", [f["check"] for f in over])             # both ceilings => fires
        one = R.lint_requirement("REQ-OK-001", self._req("confirmed", self._body(big_contract, small_ac)))
        self.assertNotIn("over-scoped", [f["check"] for f in one])           # only one ceiling => silent

    def test_over_scoped_counts_groups_not_clauses(self):  # verifies: REQ-LINTCHECKS-866#CASE-4  # verifies: ARCH-LINTCHECKS-025#CASE-6
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

    def test_file_spread_warns_across_many_files(self):  # senate-driven; validates the positive branch via a synthetic multi-file fixture  # verifies: REQ-LINTCHECKS-866#CASE-5  # verifies: REQ-LINTCHECKS-866#CASE-6  # verifies: ARCH-LINTCHECKS-025#CASE-7
        r = self._req("confirmed", self._body())
        spread = [("implements", "a.py", 1), ("implements", "b.py", 2), ("implements", "c.py", 3)]
        self.assertIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-D-001", r, spread)])
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

    def test_statement_too_long_fires_on_a_fourth_sentence(self):  # verifies: REQ-LINTCHECKS-865#CASE-1  # verifies: ARCH-LINTCHECKS-025#CASE-3
        stmt = ("- `init` creates the folder. The folder holds the lock. "
                "The lock records one hash per requirement. The hash is the contract.")
        self.assertEqual(len(R._sentences(stmt[2:])), 4)
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=stmt + "\n")))
        hits = [f for f in fs if f["check"] == "statement-too-long"]
        self.assertTrue(hits)
        self.assertEqual(hits[0]["severity"], "warn")
        self.assertIn("4 sentences", hits[0]["detail"])

    def test_stacked_conditions_warns(self):  # verifies: REQ-LINTCHECKS-865#CASE-2  # verifies: ARCH-LINTCHECKS-025#CASE-2
        line = "- It shall do A and B and C and D."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=line + "\n")))
        self.assertTrue(any(f["check"] == "stacked-conditions" for f in fs))

    def test_stacked_conditions_fires_without_a_modal_keyword(self):  # verifies: REQ-LINTCHECKS-865#CASE-3
        # plain present tense, no 'shall'/'must' anywhere: the check must still fire
        line = "- `init` creates the folder and the lock and the map and the summary."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=line + "\n")))
        self.assertTrue(any(f["check"] == "stacked-conditions" for f in fs))

    def test_anonymous_subject_warns_on_unnamed_it(self):  # verifies: REQ-LINT-863#CASE-4  # verifies: REQ-LINT-864#CASE-4  # verifies: REQ-LINTCHECKS-865#CASE-4  # verifies: ARCH-LINTCHECKS-025#CASE-9
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

    # These three probe `_lint_prose`'s fence and section handling, not any one check.
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
        self.assertEqual(R._lint_prose(body, "contract"), ["short."])

    def test_lint_prose_keeps_option_flag_hyphen(self):  # bug-hunt #13
        body = "## WHAT — Contract\n--strict makes it fail.\n"
        self.assertEqual(R._lint_prose(body, "contract"), ["--strict makes it fail."])

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

    def test_ac_count_low_warns(self):  # verifies: REQ-LINTCHECKS-866#CASE-1  # verifies: ARCH-LINTCHECKS-025#CASE-4
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

    def test_vague_term_warns(self):  # verifies: REQ-LINTCHECKS-868#CASE-1  # verifies: REQ-LINTCHECKS-868#CASE-3  # verifies: ARCH-LINTCHECKS-025#CASE-1
        body = self._body(contract="- It shall be appropriate and user-friendly.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        vague = [f for f in fs if f["check"] == "vague-term"]
        self.assertEqual(len(vague), 2)            # 'appropriate' + 'user-friendly'
        self.assertEqual(vague[0]["severity"], "warn")

    def test_vague_term_skips_code_spans(self):  # verifies: REQ-LINTCHECKS-868#CASE-2  # verifies: ARCH-LINTCHECKS-025#CASE-8
        # a backticked identifier that happens to contain a vague word is not flagged
        body = self._body(contract="- It shall return `fast_path` within the limit.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "vague-term" for f in fs))

    def test_vague_term_silent_on_precise_bullet(self):
        body = self._body(contract="- It shall return HTTP 200 within 2 seconds.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "vague-term" for f in fs))

    def test_redundant_modal_warns(self):  # verifies: REQ-LINTCHECKS-869#CASE-1  # verifies: REQ-LINTCHECKS-869#CASE-3  # verifies: ARCH-LINTCHECKS-025#CASE-10
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
        with mock.patch.object(R, "TRANSLATOR_VERSION", R.TRANSLATOR_VERSION + "-next"):
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

    def test_code_needs_cases_a_member_and_a_test_link(self):  # verifies: REQ-LEVELRETROFIT-985#CASE-2
        # Same layer, same status: only the evidence differs, and only the one
        # carrying all three signals is proposed at the decomposed rung.
        _d, ws = self._repo(
            {"REQ-A-001.md": self._req("REQ-A-001", cases=True),
             "REQ-B-002.md": self._req("REQ-B-002", cases=False)},
            members={"REQ-A-001": [("implements", "src/a.py", 1)],
                     "REQ-B-002": [("implements", "src/b.py", 1)]},
            ac_cover={"REQ-A-001": {"CASE-1": ["t"]}})
        got = R._propose_levels(ws.reqs, ws.members, ws.ac_cover)
        self.assertEqual(got["REQ-A-001"][0], "code")
        self.assertEqual(got["REQ-B-002"][0], "architecture")

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
        self.assertIn("nothing to propose", out)

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

    def test_satisfies_edges_are_never_proposed_or_written(self):  # verifies: REQ-LEVELRETROFIT-987#CASE-2
        _d, ws = self._repo({"REQ-A-001.md": self._req("REQ-A-001", layer="need")})
        rc, out = self._run(ws, apply_it=True)
        self.assertEqual(rc, 0)
        self.assertIn("`satisfies:` edges are NOT proposed", out)
        self.assertNotIn("satisfies:", open(ws.reqs["REQ-A-001"]["path"], encoding="utf-8").read())

    def test_a_two_rung_corpus_is_told_what_the_third_rung_is(self):  # verifies: REQ-LEVELRETROFIT-987#CASE-3
        _d, ws = self._repo({"REQ-A-001.md": self._req("REQ-A-001")})
        _rc, out = self._run(ws)
        self.assertIn("No requirement is proposed at `code`", out)
        self.assertIn("--decompose", out)

    def test_apply_writes_the_rung_and_the_marker(self):  # verifies: ARCH-LEVELRETROFIT-066#CASE-2
        _d, ws = self._repo({
            "SYS-A-001.md": self._req("SYS-A-001", layer="need"),
            "REQ-B-002.md": self._req("REQ-B-002"),
        })
        rc, _out = self._run(ws, apply_it=True)
        self.assertEqual(rc, 0)
        reread = R.load_requirements(ws.reqs_dir)
        self.assertEqual(reread["SYS-A-001"]["meta"]["level"], "system")
        self.assertEqual(reread["REQ-B-002"]["meta"]["level"], "architecture")
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


class PromoteTodo(unittest.TestCase):  # tested-by: ARCH-PROMOTE-TODO-001  # tested-by: REQ-PROMOTE-TODO-897  # tested-by: REQ-PROMOTE-TODO-898  # tested-by: REQ-PROMOTE-TODO-899
    TODO = "## v1.14\n- [ ] Build the thing | lane: ops\n- [x] Done already | lane: feature\n"

    def _setup(self, d):
        _write(os.path.join(d, "TODO.md"), self.TODO)
        rq = os.path.join(d, "requirements")
        os.makedirs(rq, exist_ok=True)
        return rq

    def _run(self, rq, name, cap_id, mark_done=False, root="."):
        with redirect_stdout(io.StringIO()):
            return R.cmd_promote_todo(rq, None, name, cap_id, mark_done=mark_done, root=root)

    def test_scaffolds_draft_from_todo(self):  # verifies: REQ-PROMOTE-TODO-897#CASE-1  # verifies: REQ-PROMOTE-TODO-897#CASE-3  # verifies: REQ-PROMOTE-TODO-897#CASE-4  # verifies: REQ-PROMOTE-TODO-897#CASE-5  # verifies: REQ-PROMOTE-TODO-899#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rq = self._setup(d)
            self.assertEqual(self._run(rq, "Build the thing", "REQ-T-001", root=d), 0)
            text = open(os.path.join(rq, "REQ-T-001.md"), encoding="utf-8").read()
            self.assertIn("# Build the thing", text)
            self.assertIn("milestone: v1.14", text)
            self.assertIn("layer: feature", text)            # lane ops -> feature
            self.assertIn("status: draft", text)
            self.assertIn("- [ ] Build the thing", open(os.path.join(d, "TODO.md"), encoding="utf-8").read())  # unchanged

    def test_mark_done_flips_only_matched_line(self):  # verifies: REQ-PROMOTE-TODO-899#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rq = self._setup(d)
            self._run(rq, "Build the thing", "REQ-T-001", mark_done=True, root=d)
            todo = open(os.path.join(d, "TODO.md"), encoding="utf-8").read()
            self.assertIn("- [x] Build the thing", todo)
            self.assertIn("- [x] Done already", todo)        # other lines untouched

    def test_mark_done_flips_todo_with_pipe_in_name(self):  # verifies: REQ-PROMOTE-TODO-899#CASE-2
        """A TODO whose displayed name contains a literal '|' is still flipped — the
        marker must rsplit like the parser, not split on the first '|' (#7)."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"),
                   "## v1.14\n- [ ] Support a|b pipe syntax | lane: bus\n")
            rq = os.path.join(d, "requirements")
            os.makedirs(rq, exist_ok=True)
            self._run(rq, "Support a|b pipe syntax", "REQ-P-001", mark_done=True, root=d)
            todo = open(os.path.join(d, "TODO.md"), encoding="utf-8").read()
            self.assertIn("- [x] Support a|b pipe syntax", todo)

    def test_custom_template_without_anchor_still_records_milestone(self):  # bug: promote-todo-silent-drop
        """A custom template lacking the `superseded_by:` anchor must still get the
        milestone (frontmatter-fence fallback), not silently drop it (#18)."""
        with tempfile.TemporaryDirectory() as d:
            rq = self._setup(d)
            tmpl = os.path.join(d, "tmpl.md")
            _write(tmpl, "---\nid: AREA-NAME-NNN\nstatus: draft\nlayer: feature\n---\n\n# Short name\n")
            with redirect_stdout(io.StringIO()):
                R.cmd_promote_todo(rq, tmpl, "Build the thing", "REQ-T-001", root=d)
            text = open(os.path.join(rq, "REQ-T-001.md"), encoding="utf-8").read()
            self.assertIn("milestone: v1.14", text)   # injected via the fence fallback
            self.assertIn("# Build the thing", text)   # title anchor present -> filled

    def test_errors_write_nothing(self):  # verifies: REQ-PROMOTE-TODO-898#CASE-1  # verifies: REQ-PROMOTE-TODO-898#CASE-2  # verifies: REQ-PROMOTE-TODO-898#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = self._setup(d)
            self.assertEqual(self._run(rq, "Build the thing", None, root=d), 2)            # no --id
            self.assertEqual(self._run(rq, "nope", "REQ-T-001", root=d), 1)                # not found
            self.assertFalse(os.path.exists(os.path.join(rq, "REQ-T-001.md")))
            _write(os.path.join(rq, "REQ-T-001.md"), "x")
            self.assertEqual(self._run(rq, "Build the thing", "REQ-T-001", root=d), 1)     # id taken

    def test_custom_template_layer_mismatch_warns_not_silently_wrong(self):  # bug: promote-todo-layer-silent-drop
        """A custom template whose layer line does not literally read
        `layer: feature` must warn — not silently keep the wrong layer while the
        success message claims the intended one was recorded."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"), "## v1.14\n- [ ] Build the thing | lane: bus\n")
            rq = os.path.join(d, "requirements")
            os.makedirs(rq, exist_ok=True)
            tmpl = os.path.join(d, "tmpl.md")
            _write(tmpl, "---\nid: AREA-NAME-NNN\nstatus: draft\nlayer: TODO-LAYER\n---\n\n# Short name\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_promote_todo(rq, tmpl, "Build the thing", "REQ-T-001", root=d)
            self.assertEqual(rc, 0)
            self.assertIn("warning", buf.getvalue().lower())
            self.assertIn("layer", buf.getvalue().lower())
            text = open(os.path.join(rq, "REQ-T-001.md"), encoding="utf-8").read()
            self.assertIn("layer: TODO-LAYER", text)   # unchanged, not silently mis-set


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


class NewNumberCollision(unittest.TestCase):  # tested-by: ARCH-NEW-004  # tested-by: REQ-NEW-882
    def _new(self, rd, cap_id):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_new(rd, None, cap_id)
        return code, buf.getvalue()

    def test_same_area_same_number_warns_but_creates(self):  # verifies: REQ-NEW-882#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "ARCH-MAP-007.md"), "---\nid: ARCH-MAP-007\n---\n# M\n")
            code, out = self._new(rd, "ARCH-VIEWER-007")
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(rd, "ARCH-VIEWER-007.md")))
            self.assertIn("WARN", out)
            self.assertIn("ARCH-MAP-007", out)

    def test_different_area_same_number_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "ARCH-PARSE-001.md"), "---\nid: ARCH-PARSE-001\n---\n# P\n")
            code, out = self._new(rd, "SYS-SSOT-001")
            self.assertEqual(code, 0)
            self.assertNotIn("WARN", out)


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
        # _lint_prose does not skip HTML comments; _contract_clauses must, or the template's
        # own glossary block would be measured as a clause.
        contract = "<!-- {} -->\n- short.\n".format(self._words(160))
        self.assertEqual([n for n, _ in R._contract_clauses(self._body(contract))], [1])
        self.assertNotIn("statement-size", [f["check"] for f in self._findings(contract)])

    def test_wrapped_clause_is_joined_before_counting(self):  # verifies: REQ-ATOMICITY-825#CASE-7
        # The reason this check cannot reuse _lint_prose: these files wrap near 95 columns,
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

class CasesPromoteTodo(unittest.TestCase):  # tested-by: ARCH-PROMOTE-TODO-001  # tested-by: REQ-PROMOTE-TODO-897  # tested-by: REQ-PROMOTE-TODO-898  # tested-by: REQ-PROMOTE-TODO-899
    def test_matching_is_case_insensitive_and_trims(self):  # verifies: REQ-PROMOTE-TODO-897#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"), "## v1.14\n- [ ] Add Export Command | lane: cli\n")
            rq = os.path.join(d, "requirements")
            os.makedirs(rq, exist_ok=True)
            with redirect_stdout(io.StringIO()):
                code = R.cmd_promote_todo(rq, None, "  add export command  ", "REQ-X-001", root=d)
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(rq, "REQ-X-001.md")))

    def test_ambiguous_name_refuses(self):  # verifies: REQ-PROMOTE-TODO-898#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"),
                   "## v1.14\n- [ ] Ship the widget | lane: ops\n## v1.15\n- [ ] Ship the widget | lane: bus\n")
            rq = os.path.join(d, "requirements")
            os.makedirs(rq, exist_ok=True)
            with redirect_stdout(io.StringIO()):
                code = R.cmd_promote_todo(rq, None, "Ship the widget", "REQ-X-001", root=d)
            self.assertNotEqual(code, 0)
            self.assertEqual([n for n in os.listdir(rq) if n.endswith(".md")], [])

    def test_no_match_lists_open_items(self):  # verifies: REQ-PROMOTE-TODO-898#CASE-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"),
                   "## v1.14\n- [ ] Build the thing | lane: ops\n- [ ] Ship the widget | lane: bus\n")
            rq = os.path.join(d, "requirements")
            os.makedirs(rq, exist_ok=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_promote_todo(rq, None, "nope not a match", "REQ-X-001", root=d)
            out = buf.getvalue()
            self.assertNotEqual(code, 0)
            self.assertIn("Build the thing", out)
            self.assertIn("Ship the widget", out)

    def test_mark_done_write_failure_warns_not_fails(self):  # verifies: REQ-PROMOTE-TODO-899#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "TODO.md"), "## v1.14\n- [ ] Build the thing | lane: ops\n")
            rq = os.path.join(d, "requirements")
            os.makedirs(rq, exist_ok=True)
            buf = io.StringIO()
            with mock.patch.object(R, "_mark_todo_done", return_value=0):
                with redirect_stdout(buf):
                    code = R.cmd_promote_todo(rq, None, "Build the thing", "REQ-X-001", mark_done=True, root=d)
            out = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("warning", out.lower())
            self.assertTrue(os.path.exists(os.path.join(rq, "REQ-X-001.md")))


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
        self.assertEqual(R._lint_prose(body, "contract"), [])

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


class Implement(unittest.TestCase):  # tested-by: ARCH-IMPLEMENT-063  # tested-by: REQ-IMPLEMENT-958  # tested-by: REQ-IMPLEMENT-959
    def _seed(self, d, rid="AREA-I-001", clauses=("`gate` writes the lock file.",), cases=None, code=True):
        rd = os.path.join(d, "requirements")
        cases = cases or ("CASE-1 — a\n  Given x\n  When y\n  Then z",
                          "CASE-2 — b\n  Given an invalid lock\n  When y\n  Then it refuses")
        _write(os.path.join(rd, rid + ".md"), _spec(rid, list(clauses), cases))
        if code:
            _write(os.path.join(d, "mod.py"), tag(rid) + "\ndef f():\n    return 1\n")
        return rd

    def _run(self, d, rid, as_json=False):
        rd = os.path.join(d, "requirements")
        reqs = R.load_requirements(rd)
        members = R.scan_members(d, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_implement(R.Workspace(reqs, members), rid, as_json)
        return code, buf.getvalue()

    def test_tags_are_emitted_verbatim_one_per_case(self):  # verifies: ARCH-IMPLEMENT-063#CASE-1  # verifies: REQ-IMPLEMENT-958#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            _code, out = self._run(d, "AREA-I-001")
        self.assertIn(tag("AREA-I-001"), out)
        self.assertIn("# verifies: AREA-I-001#CASE-1", out)
        self.assertIn("# verifies: AREA-I-001#CASE-2", out)
        self.assertEqual(2, out.count("# verifies: AREA-I-001#"))

    def test_blocking_question_opens_the_brief(self):  # verifies: ARCH-IMPLEMENT-063#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-N-001.md"),
                   "---\nid: AREA-N-001\nstatus: confirmed\nlayer: feature\n---\n\n"
                   "# N\n\n## Description\nEvery bullet below is binding.\n- `gate` runs.\n")
            _code, out = self._run(d, "AREA-N-001")
        self.assertIn("BLOCKING", out)
        self.assertIn("clarify AREA-N-001", out)

    def test_brief_writes_nothing(self):  # verifies: ARCH-IMPLEMENT-063#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = self._seed(d)
            before = {f: open(os.path.join(rd, f), encoding="utf-8").read() for f in os.listdir(rd)}
            self._run(d, "AREA-I-001")
            after = {f: open(os.path.join(rd, f), encoding="utf-8").read() for f in os.listdir(rd)}
        self.assertEqual(before, after)

    def test_a_requirement_with_no_code_says_so(self):  # verifies: REQ-IMPLEMENT-958#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._seed(d, code=False)
            _code, out = self._run(d, "AREA-I-001")
        self.assertIn("nothing yet", out)

    def test_json_brief_carries_the_fields(self):  # verifies: REQ-IMPLEMENT-958#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            code, out = self._run(d, "AREA-I-001", as_json=True)
        data = json.loads(out)
        self.assertEqual(0, code)
        for field in ("contract", "cases", "members", "tags", "open_questions"):
            self.assertIn(field, data)

    def test_nearest_implemented_neighbour_is_offered(self):  # verifies: REQ-IMPLEMENT-959#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-I-001.md"),
                   _spec("AREA-I-001", ["the lock file records the contract hash baseline."]))
            _write(os.path.join(rd, "AREA-J-002.md"),
                   _spec("AREA-J-002", ["the lock file records the contract hash baseline exactly."]))
            _write(os.path.join(d, "neighbour.py"), tag("AREA-J-002") + "\ndef g():\n    return 2\n")
            _code, out = self._run(d, "AREA-I-001")
        self.assertIn("AREA-J-002", out)
        self.assertIn("neighbour.py", out)

    def test_at_most_two_neighbours_are_offered(self):  # verifies: REQ-IMPLEMENT-959#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            clause = "the lock file records the contract hash baseline"
            _write(os.path.join(rd, "AREA-I-001.md"), _spec("AREA-I-001", [clause + "."]))
            for n in range(5):
                rid = "AREA-N-01{}".format(n)
                _write(os.path.join(rd, rid + ".md"), _spec(rid, ["{} exactly {}.".format(clause, n)]))
                _write(os.path.join(d, "n{}.py".format(n)), tag(rid) + "\ndef f():\n    return 1\n")
            _code, out = self._run(d, "AREA-I-001")
        self.assertEqual(2, sum(1 for line in out.splitlines() if line.startswith("  AREA-N-01")))

    def test_no_neighbour_when_nothing_is_implemented(self):  # verifies: REQ-IMPLEMENT-959#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-I-001.md"), _spec("AREA-I-001", ["the lock file records the hash."]))
            _write(os.path.join(rd, "AREA-J-002.md"), _spec("AREA-J-002", ["the lock file records the hash."]))
            _code, out = self._run(d, "AREA-I-001")
        self.assertNotIn("Similar requirements", out)


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
            with mock.patch.object(R, "_git_dirty", return_value=True):
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

    def test_a_decompose_run_that_scaffolds_nothing_says_so(self):  # verifies: ARCH-DECOMPOSE-050#CASE-8  # verifies: REQ-DECOMPOSE-839#CASE-6
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


class TranslationParity(unittest.TestCase):  # tested-by: ARCH-TRANSLATE-044  # tested-by: REQ-TRANSLATE-967
    """Two derived artifacts, each correct against the requirement, disagreeing with each
    other. RM017 checks one such pair (the viewer's baked fixture); this is the other."""

    ATOMIC = ("---\nid: AREA-T-001\nstatus: confirmed\nlayer: feature\n---\n\n# T\n\n"
              "## Description\n> the story IS the obligation.\n\n"
              "Every bullet below is binding.\n- the story IS the obligation.\n\n"
              "## Cases\nCASE-1\n  Given  x\n  When   y\n  Then   z\n")

    def _cache(self, rd, entry):
        reqs = R.load_requirements(rd)
        body = reqs["AREA-T-001"]["body"]
        os.makedirs(os.path.join(rd, "_i18n"), exist_ok=True)
        entry = dict(entry, hash=R.translation_hash(body, R._title(body)))
        with open(os.path.join(rd, "_i18n", "ro.json"), "w", encoding="utf-8") as f:
            json.dump({"AREA-T-001": entry}, f)

    def _findings(self, d):
        rd = os.path.join(d, "requirements")
        reqs = R.load_requirements(rd)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_check(R.Workspace(reqs, R.scan_members(d, d), rd, d), False)
        return buf.getvalue()

    def test_translated_field_the_map_does_not_emit_is_reported(self):  # verifies: REQ-TRANSLATE-967#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-T-001.md"), self.ATOMIC)
            _write(os.path.join(d, "mod.py"), tag("AREA-T-001") + "\ndef f():\n    return 1\n")
            self._cache(rd, {"title": "T", "intent": "un motiv pe care harta nu il emite",
                             "contract": "- povestea", "acceptance": "CASE-1"})
            out = self._findings(d)
        self.assertIn("RM029", out)
        self.assertIn("AREA-T-001", out)
        self.assertIn("intent", out)

    def test_a_field_the_translation_lacks_is_not_a_finding(self):  # verifies: REQ-TRANSLATE-967#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-T-001.md"), self.ATOMIC)
            _write(os.path.join(d, "mod.py"), tag("AREA-T-001") + "\ndef f():\n    return 1\n")
            self._cache(rd, {"title": "T", "intent": "", "contract": "- povestea", "acceptance": "CASE-1"})
            out = self._findings(d)
        self.assertNotIn("RM029", out)

    def test_no_cache_raises_nothing(self):  # verifies: REQ-TRANSLATE-967#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-T-001.md"), self.ATOMIC)
            _write(os.path.join(d, "mod.py"), tag("AREA-T-001") + "\ndef f():\n    return 1\n")
            out = self._findings(d)
        self.assertNotIn("RM029", out)


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


class NewRefusesANonId(unittest.TestCase):  # tested-by: ARCH-NEW-004  # tested-by: REQ-NEW-881
    """An id is what a tag must spell; anything else mints a requirement no code can name."""

    def test_a_non_id_is_refused_and_writes_nothing(self):  # verifies: REQ-NEW-881#CASE-5
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        for bad in ("my req", "lower-case-1", "NOPARTS", "../evil", "A/B-1", ""):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_new(d, None, bad)
            self.assertEqual(rc, 2, bad)
            self.assertIn("invalid id", buf.getvalue())
        self.assertEqual(os.listdir(d), [])

    def test_a_real_id_still_scaffolds(self):  # verifies: REQ-NEW-881#CASE-1
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(R.cmd_new(d, None, "AREA-NAME-001"), 0)
        self.assertEqual(os.listdir(d), ["AREA-NAME-001.md"])

    def test_promote_todo_refuses_the_same_ids(self):  # verifies: REQ-NEW-881#CASE-5
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = R.cmd_promote_todo(d, None, "some todo", "my req", root=d)
        self.assertEqual(rc, 2)
        self.assertIn("invalid id", buf.getvalue())


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
    child per group, cases moved only on an unambiguous name match, no tags written, the
    parent rewritten only where the split happened."""

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
        self.assertIn("mentions x.py", child)            # CASE-1 named one subject: moved
        self.assertNotIn("mentions x.py", parent)
        self.assertIn("CASE-2", parent)                   # named two subjects: stayed
        self.assertIn("CASE-3", parent)                   # named none: stayed
        self.assertIn("2 stay on their parents", out)

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

    def test_the_parent_is_rewritten_only_where_the_split_happened(self):  # verifies: REQ-DECOMPOSE-994#CASE-6
        self._run(apply_it=True)
        parent = io.open(os.path.join(self.rd, "TOOL-UTILS.md"), encoding="utf-8").read()
        for line in ("- Module — see [[TOOL-UTILS-MODULE]].",
                     "- load_json_stdin — see [[TOOL-UTILS-LOAD-JSON-STDIN]].",
                     "- is_headless — see [[TOOL-UTILS-IS-HEADLESS]]."):
            self.assertIn(line, parent)
        self.assertNotIn("**Module**", parent)
        self.assertNotIn("uses only the standard library", parent)
        # untouched outside the two sections, and surviving cases keep their labels
        head = self.PARENT.split("## Description")[0]
        self.assertTrue(parent.startswith(head))
        self.assertTrue(parent.rstrip().endswith("- prose that must survive untouched"))
        self.assertIn("CASE-2\n", parent)
        self.assertIn("CASE-3\n", parent)
        self.assertNotIn("CASE-1\n  Given  empty stdin", parent)

    def test_a_parent_stripped_of_every_case_gets_a_placeholder(self):  # verifies: REQ-DECOMPOSE-994#CASE-7
        body = self.PARENT.replace(
            "CASE-2\n  Given  `CLAUDE_HEADLESS` unset\n  When   `is_headless()` runs, then `load_json_stdin` runs\n  Then   both behave\n\n", ""
        ).replace("CASE-3\n  Given  any environment\n  When   the package is imported\n  Then   it imports cleanly\n\n", "")
        _write(os.path.join(self.rd, "TOOL-UTILS.md"), body)
        self._run(apply_it=True)
        parent = io.open(os.path.join(self.rd, "TOOL-UTILS.md"), encoding="utf-8").read()
        self.assertIn("work TOGETHER", parent)
        self.assertEqual(len(R._acc_blocks(parent.split("---", 2)[2])), 1)

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
