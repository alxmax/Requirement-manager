"""Reading the tree: the frontmatter parser, membership scanning, the masking rules
that decide which lines a tag may live on, the walk, prose classification, the git runner
and the section reader.

Part of the `test_reqmap` suite — run it through the aggregator (`python
scripts/test_reqmap.py`), or on its own with `python -m unittest test_reqmap_scan`."""
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



class Parsing(unittest.TestCase):  # tested-by: ARCH-PARSE-001  # tested-by: REQ-PARSE-890  # tested-by: REQ-PARSE-891  # tested-by: REQ-PARSE-892
    def test_bom_does_not_break_frontmatter(self):  # bug #1
        text = "﻿---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n"
        meta, _ = R.parse_frontmatter(text)
        self.assertEqual(meta.get("id"), "REQ-A-001")
        self.assertEqual(meta.get("status"), "confirmed")

    def test_bom_file_loads_with_real_id(self):  # bug #1 end-to-end  # verifies: REQ-PARSE-892#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "REQ-A-001.md"),
                   "﻿" + REQ.format(id="REQ-A-001", status="confirmed", layer="bus", extra="", title="T"))
            reqs = R.load_requirements(d)
            self.assertIn("REQ-A-001", reqs)
            self.assertEqual(reqs["REQ-A-001"]["meta"]["status"], "confirmed")

    def test_hash_inside_inline_list(self):  # bug #2
        meta, _ = R.parse_frontmatter("---\ndepends_on: [A-1, B-2 # note]\n---\n")
        self.assertEqual(meta["depends_on"], ["A-1", "B-2"])

    def test_quoted_scalar_is_unquoted(self):  # bug #14  # verifies: REQ-PARSE-891#CASE-3
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

    def test_scalar_and_list_fields_in_meta(self):  # verifies: ARCH-PARSE-001#CASE-1  # verifies: REQ-PARSE-890#CASE-2
        meta, _ = R.parse_frontmatter(
            "---\nid: REQ-A-001\nstatus: draft\ndepends_on: [X-Y-001, Z-W-002]\n---\nbody\n")
        self.assertEqual(meta["id"], "REQ-A-001")
        self.assertEqual(meta["status"], "draft")
        self.assertEqual(meta["depends_on"], ["X-Y-001", "Z-W-002"])

    def test_trailing_comment_stripped_from_value(self):  # verifies: ARCH-PARSE-001#CASE-2  # verifies: REQ-PARSE-891#CASE-2
        meta, _ = R.parse_frontmatter("---\nstatus: draft  # not enforced\n---\n")
        self.assertEqual(meta["status"], "draft")

    def test_no_frontmatter_block_yields_empty_meta(self):  # verifies: ARCH-PARSE-001#CASE-3  # verifies: REQ-PARSE-892#CASE-1
        meta, body = R.parse_frontmatter("# Title\njust text\n")
        self.assertEqual(meta, {})
        self.assertEqual(body, "# Title\njust text\n")

    def test_underscore_files_excluded(self):  # verifies: ARCH-PARSE-001#CASE-4  # verifies: REQ-PARSE-892#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_draft.md"), "---\nid: X-A-001\n---\n# T\n")
            _write(os.path.join(d, "REQ-A-001.md"), "---\nid: REQ-A-001\n---\n# T\n")
            reqs = R.load_requirements(d)
        self.assertEqual(list(reqs), ["REQ-A-001"])

    def test_block_list_and_unclosed_inline_list(self):  # verifies: ARCH-PARSE-001#CASE-5  # verifies: REQ-PARSE-891#CASE-1  # verifies: REQ-PARSE-891#CASE-4
        meta, _ = R.parse_frontmatter(
            "---\ndepends_on:\n  - A-B-001\n  - C-D-002\ntags: [x, y\n---\n")
        self.assertEqual(meta["depends_on"], ["A-B-001", "C-D-002"])
        self.assertEqual(meta["tags"], ["x", "y"])

    def test_frontmatter_hash_in_word_not_truncated(self):
        """'#' not preceded by whitespace must not be treated as a comment."""
        text = "---\nid: REQ-A-001\ntitle: count#1 thing\nstatus: draft\nlayer: bus\n---\n\n# T\n"
        meta, _ = R.parse_frontmatter(text)
        self.assertEqual(meta.get("title"), "count#1 thing")

    def test_frontmatter_hash_preceded_by_space_is_comment(self):
        """'#' preceded by space IS an inline comment — value stops there."""
        text = "---\nid: REQ-A-001\ntitle: v1.0 # release note\nstatus: draft\nlayer: bus\n---\n\n# T\n"
        meta, _ = R.parse_frontmatter(text)
        self.assertEqual(meta.get("title"), "v1.0")

    def test_frontmatter_hash_at_start_is_comment(self):
        """'#' at the very start of a value is a comment — value becomes empty."""
        text = "---\nid: REQ-A-001\ntitle: #comment\nstatus: draft\nlayer: bus\n---\n\n# T\n"
        meta, _ = R.parse_frontmatter(text)
        self.assertEqual(meta.get("title"), "")


class Scanning(unittest.TestCase):  # tested-by: ARCH-SCAN-002  # tested-by: REQ-SCAN-908  # tested-by: REQ-SCAN-909
    def test_scan_members_deterministic_across_walk_order(self):  # cross-platform parity (Windows-generated map vs Linux CI)
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "z_pkg"))
            _write(os.path.join(d, "a.py"), tag("X-CAP-001") + "\n")
            _write(os.path.join(d, "m.py"), tag("X-CAP-001") + "\n")
            _write(os.path.join(d, "z_pkg", "q.py"), tag("X-CAP-001") + "\n")
            normal = R.scan_members(d, None)
            real = os.walk

            def rev(top, *a, **k):                 # simulate a different filesystem order (e.g. Linux vs NTFS)
                for dp, dirs, files in real(top, *a, **k):
                    dirs.sort(reverse=True)
                    files.sort(reverse=True)
                    yield dp, dirs, files
            try:
                os.walk = rev
                flipped = R.scan_members(d, None)
            finally:
                os.walk = real
            # member order must NOT depend on walk order, else a Windows-generated map fails CI on Linux
            self.assertEqual(normal["X-CAP-001"], flipped["X-CAP-001"])

    def test_tag_re_left_boundary(self):  # bug #3  # verifies: REQ-SCAN-908#CASE-1  # verifies: REQ-SCAN-908#CASE-4  # verifies: REQ-SCAN-908#CASE-5
        self.assertEqual(R.TAG_RE.findall(tag("FOO-BAR-001")), [("implements", "FOO-BAR-001")])
        self.assertEqual(R.TAG_RE.findall("# re" + _ROLE + ": FOO-BAR-001"), [])
        self.assertEqual(R.TAG_RE.findall("auto-" + _ROLE + ": AB-CD-001"), [])

    def test_only_ssot_requirements_dir_excluded(self):  # bug #4  # verifies: ARCH-SCAN-002#CASE-3  # verifies: REQ-SCAN-909#CASE-3  # verifies: REQ-SCAN-909#CASE-4
        with tempfile.TemporaryDirectory() as d:
            ssot = os.path.join(d, "requirements")
            _write(os.path.join(d, "src", "requirements", "mod.py"), tag("SRC-REQ-001") + "\n")
            _write(os.path.join(ssot, "ignored.py"), tag("SSOT-IGN-001") + "\n")
            members = R.scan_members(d, ssot)
            self.assertIn("SRC-REQ-001", members)       # non-SSOT requirements/ still scanned
            self.assertNotIn("SSOT-IGN-001", members)    # the real SSOT dir is skipped

    def test_duplicate_tag_on_one_line_deduped(self):  # bug #18  # verifies: ARCH-SCAN-002#CASE-4  # verifies: REQ-SCAN-908#CASE-6
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), tag("FOO-BAR-001") + " " + _ROLE + ": FOO-BAR-001\n")
            members = R.scan_members(d, None)
            self.assertEqual(len(members["FOO-BAR-001"]), 1)

    def test_member_paths_are_posix(self):  # bug #17  # verifies: ARCH-SCAN-002#CASE-4  # verifies: REQ-SCAN-908#CASE-7
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "sub", "dir", "m.py"), tag("FOO-BAR-001") + "\n")
            members = R.scan_members(d, None)
            self.assertEqual(members["FOO-BAR-001"][0][1], "sub/dir/m.py")

    def test_reqmapignore_excludes_listed_file(self):  # verifies: REQ-SCAN-909#CASE-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "scripts", "reqmap.py"), tag("TOOL-X-001") + "\n")
            _write(os.path.join(d, "scripts", "app.py"), tag("APP-Y-001") + "\n")
            _write(os.path.join(d, ".reqmapignore"), "# vendored tool\nscripts/reqmap.py\n")
            members = R.scan_members(d, None)
            self.assertNotIn("TOOL-X-001", members)  # ignored
            self.assertIn("APP-Y-001", members)       # still scanned

    def test_is_code_file_extensions_and_basenames(self):
        self.assertTrue(R._is_code_file("foo.sh"))
        self.assertTrue(R._is_code_file("infra.tf"))
        self.assertTrue(R._is_code_file("Dockerfile"))
        self.assertTrue(R._is_code_file("Makefile"))
        self.assertFalse(R._is_code_file("readme.txt"))
        self.assertFalse(R._is_code_file("dockerfile"))  # exact basename match only, no case-fold

    def test_is_code_file_git_hook_basenames(self):
        # git hook filenames are extensionless and as conventional as Dockerfile/Makefile —
        # needed so a repo's own .githooks/ scripts are taggable (v2.9 "tag your own pipeline").
        self.assertTrue(R._is_code_file("pre-commit"))
        self.assertTrue(R._is_code_file("pre-push"))
        self.assertTrue(R._is_code_file("commit-msg"))
        self.assertFalse(R._is_code_file("pre-commit.sample"))  # git's own shipped sample hooks

    def test_shell_and_terraform_and_basename_files_are_scanned(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "deploy.sh"), tag("SH-CAP-001") + "\n")
            _write(os.path.join(d, "infra.tf"), tag("TF-CAP-001") + "\n")
            _write(os.path.join(d, "Dockerfile"), tag("DOCKER-CAP-001") + "\n")
            _write(os.path.join(d, "Makefile"), tag("MAKE-CAP-001") + "\n")
            members = R.scan_members(d, None)
        self.assertIn("SH-CAP-001", members)
        self.assertIn("TF-CAP-001", members)
        self.assertIn("DOCKER-CAP-001", members)
        self.assertIn("MAKE-CAP-001", members)

    def test_reqmapignore_glob_pattern(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "gen", "a.py"), tag("GEN-A-001") + "\n")
            _write(os.path.join(d, ".reqmapignore"), "gen/*.py\n")
            self.assertNotIn("GEN-A-001", R.scan_members(d, None))

    def test_no_reqmapignore_scans_everything(self):  # backward compat
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), tag("FOO-BAR-001") + "\n")
            self.assertIn("FOO-BAR-001", R.scan_members(d, None))

    def test_implements_tag_yields_member(self):  # verifies: ARCH-SCAN-002#CASE-1  # verifies: REQ-SCAN-908#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), tag("REQ-T-001") + "\n")
            members = R.scan_members(d, None)
        self.assertEqual(members["REQ-T-001"], [("implements", "a.py", 1)])

    def test_all_roles_recognized_unknown_ignored(self):  # verifies: ARCH-SCAN-002#CASE-2  # verifies: REQ-SCAN-908#CASE-3
        # roles built at runtime so THIS .py source registers no phantom member
        roles = [_ROLE, _TB_ROLE, "generated" + "-from", "validated" + "-against", "refines"]
        src = "".join("# {}: REQ-T-001\n".format(r) for r in roles)
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), src)
            members = R.scan_members(d, None)
        found = sorted(r for (r, _f, _l) in members["REQ-T-001"])
        self.assertEqual(found, ["generated-from", "implements", "tested-by", "validated-against"])

    def test_generated_from_accepts_multiple_ids(self):  # verifies: ARCH-SCAN-002#CASE-6  # verifies: REQ-SCAN-909#CASE-1  # verifies: REQ-SCAN-909#CASE-2
        # one whole-system doc generated from several requirements → a member of
        # each, so a contract drift on ANY of them lists the doc as needing re-sync.
        # List built at runtime so THIS .py source registers no phantom member.
        line = "<!-- {}-from: {}, {} -->\n".format("generated", "REQ-MA-001", "REQ-MB-002")
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), line)
            members = R.scan_members(d, None)
        self.assertEqual(members.get("REQ-MA-001"), [("generated-from", "docs/arch.html", 1)])
        self.assertEqual(members.get("REQ-MB-002"), [("generated-from", "docs/arch.html", 1)])

    def test_multi_id_dedup_and_single_id_unchanged(self):  # verifies: ARCH-SCAN-002#CASE-6
        # a repeated id in one list is recorded once; a plain single-id tag is unaffected.
        multi = "# {}: {}, {}\n".format(_ROLE, "REQ-MC-001", "REQ-MC-001")
        single = tag("REQ-MD-001") + "\n"
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), multi + single)
            members = R.scan_members(d, None)
        self.assertEqual(members.get("REQ-MC-001"), [("implements", "a.py", 1)])
        self.assertEqual(members.get("REQ-MD-001"), [("implements", "a.py", 2)])

    def test_unreadable_file_skipped(self):  # verifies: ARCH-SCAN-002#CASE-5  # verifies: REQ-SCAN-909#CASE-6
        # _scan_file_tags fails open (None) on a read error; scan_members skips the file
        self.assertIsNone(R._scan_file_tags(os.path.join("no", "such", "dir", "x.py")))

    def test_scan_test_levels_collects_levels_per_requirement(self):  # tested-by: ARCH-VLEVEL-037 @unit  # tested-by: REQ-VLEVEL-944  # verifies: REQ-VLEVEL-944#CASE-1  # verifies: REQ-VLEVEL-945#CASE-1
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "t_one.py"), "w", encoding="utf-8") as f:
                f.write("# tested-by: REQ-A-001 @unit\n"
                        "# tested-by: REQ-A-001 @system\n"
                        "# tested-by: REQ-B-002 @integration\n")
            got = R.scan_test_levels(d)
            self.assertEqual(set(got["REQ-A-001"]), {"unit", "system"})
            self.assertEqual(set(got["REQ-B-002"]), {"integration"})
            self.assertEqual(got["REQ-B-002"]["integration"], [("t_one.py", 3)])

    def test_scan_test_levels_expands_an_id_list_and_ignores_unlevelled(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-VLEVEL-944#CASE-2
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "t_two.py"), "w", encoding="utf-8") as f:
                f.write("# tested-by: REQ-A-001, REQ-B-002 @integration\n"
                        "# tested-by: REQ-C-003\n"              # no level: not collected
                        "# tested-by: REQ-D-004 @wrong\n")      # not a known level
            got = R.scan_test_levels(d)
            self.assertEqual(set(got["REQ-A-001"]), {"integration"})
            self.assertEqual(set(got["REQ-B-002"]), {"integration"})
            self.assertNotIn("REQ-C-003", got)
            self.assertNotIn("REQ-D-004", got)

    def test_scan_test_levels_ignores_a_tag_inside_a_python_string(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-VLEVEL-945#CASE-4
        # a levelled tag quoted in a docstring or string literal is prose about tagging,
        # not a claim of coverage — the same masking _scan_file_tags applies
        body = "\n".join([
            "def f():",
            '    """Tag it like tested-by: REQ-DOC-001 @unit in your test."""',
            '    s = "tested-by: REQ-STR-001 @unit"',
            "    return s",
            "# tested-by: REQ-REAL-001 @unit",
        ]) + "\n"
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.py"), "w", encoding="utf-8") as f:
                f.write(body)
            got = R.scan_test_levels(d)
            self.assertNotIn("REQ-DOC-001", got)                   # docstring
            self.assertNotIn("REQ-STR-001", got)                   # string literal
            self.assertEqual(set(got["REQ-REAL-001"]), {"unit"})   # real comment tag

    def test_scan_test_levels_ignores_a_backticked_example(self):  # tested-by: ARCH-VLEVEL-037 @unit  # tested-by: REQ-VLEVEL-945  # verifies: REQ-VLEVEL-945#CASE-3
        # same phantom-member guard _scan_file_tags applies: a documented EXAMPLE of a
        # levelled tag must not register as real coverage
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "doc.py"), "w", encoding="utf-8") as f:
                f.write("# write it as `# tested-by: REQ-A-001 @unit` in your test\n"
                        "# tested-by: REQ-B-002 @unit\n")     # this one is real
            got = R.scan_test_levels(d)
            self.assertNotIn("REQ-A-001", got)
            self.assertEqual(set(got["REQ-B-002"]), {"unit"})

    def test_tag_patterns_are_built_from_roles(self):
        # ROLES is the vocabulary; both patterns are derived from it. Hand-maintaining
        # the alternation made ROLES look authoritative while driving nothing.
        for role in R.ROLES:
            self.assertEqual(R.TAG_RE.findall("# {}: REQ-A-001".format(role)),
                             [(role, "REQ-A-001")])
            self.assertEqual(R.TAG_LIST_RE.findall("# {}: REQ-A-001".format(role)),
                             [(role, "REQ-A-001")])
        self.assertEqual(R.TAG_RE.findall("# not-a-role: REQ-A-001"), [])

    def test_levelled_tag_still_resolves_as_a_plain_member(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-VLEVEL-944#CASE-3  # verifies: REQ-VLEVEL-945#CASE-2
        # backwards compatibility: the suffix must not disturb ordinary tag parsing
        self.assertEqual(R._findall_tags("# tested-by: REQ-A-001 @unit"),
                         [("tested-by", "REQ-A-001")])


class RepoRootScan(unittest.TestCase):  # tested-by: ARCH-SCAN-002
    def test_default_scan_set_unchanged_without_code_flag(self):
        # Protects external consumer repos: scan_members(code_root) must be
        # byte-identical whether or not a sibling .reqmapignore exists one
        # level up — passing no --code (code_root == a.root) must never see it.
        with tempfile.TemporaryDirectory() as d:
            plugin_dir = os.path.join(d, "plugin")
            _write(os.path.join(plugin_dir, "scripts", "reqmap.py"), tag("TOOL-X-001") + "\n")
            before = R.scan_members(plugin_dir, None)
            _write(os.path.join(d, ".reqmapignore"), "plugin/scripts/reqmap.py\n")  # repo-root file appears
            after = R.scan_members(plugin_dir, None)  # code_root still == plugin_dir
            self.assertEqual(before, after)

    def test_widened_root_excludes_generated_viewer_and_skill_pairs(self):
        # Regression test for the bug found reading load_ignore(): a NEW
        # repo-root .reqmapignore (not a relocated one) must exclude the same
        # generated files once code_root widens to the repo root via --code.
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "plugin", "scripts", "_map_viewer.html"), "<!-- generated -->\n")
            _write(os.path.join(d, "plugin", "skills", "requirement-manager", "SKILL.md"), "# skill\n")
            _write(os.path.join(d, "plugin", "scripts", "reqmap.py"), tag("TOOL-X-001") + "\n")
            _write(os.path.join(d, ".reqmapignore"),
                   "plugin/scripts/_map_viewer.html\n"
                   "plugin/skills/requirement-manager/SKILL.md\n")
            members = R.scan_members(d, None)  # code_root == repo root (simulates --code ..)
            self.assertIn("TOOL-X-001", members)
            all_files = {fp for hits in members.values() for (_r, fp, _l) in hits}
            self.assertNotIn("plugin/scripts/_map_viewer.html", all_files)
            self.assertNotIn("plugin/skills/requirement-manager/SKILL.md", all_files)

    def test_widened_root_reaches_docs_and_github(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "notes.md"), tag("DOCS-CAP-001") + "\n")
            _write(os.path.join(d, ".github", "workflows", "ci.yml"), tag("CI-CAP-001") + "\n")
            members = R.scan_members(d, None)
        self.assertIn("DOCS-CAP-001", members)
        self.assertIn("CI-CAP-001", members)


class ProseClassification(unittest.TestCase):  # tested-by: ARCH-PROSE-024  # tested-by: REQ-PROSE-900
    def test_meta_files_are_ignored(self):  # verifies: REQ-PROSE-900#CASE-2
        for rel in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", "CONTRIBUTING.md",
                    "SKILL.md", "TODO.md", "CHANGELOG.md", "LICENSE", "LICENSE.md",
                    "_map.md", "_findings.md", "_map.html"):
            self.assertEqual(R.classify_prose(rel), "ignore", rel)

    def test_readme_and_docs_and_html_are_sync_only(self):  # verifies: REQ-PROSE-900#CASE-3
        for rel in ("README", "README.md", "docs/senate.md",
                    "docs/sub/guide.md", "docs/architecture.html", "x.html"):
            self.assertEqual(R.classify_prose(rel), "sync_only", rel)

    def test_prompts_and_specs_are_capability(self):  # verifies: REQ-PROSE-900#CASE-4
        for rel in ("prompts/senators/aurelius.md", "specs/foo.md",
                    "modes/bar.md", "notes.md"):
            self.assertEqual(R.classify_prose(rel), "capability", rel)


class ProseFacts(unittest.TestCase):  # tested-by: ARCH-PROSE-024  # tested-by: REQ-PROSE-901
    def test_markdown_frontmatter_title_and_headings(self):  # verifies: REQ-PROSE-901#CASE-2
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


class ProseExtract(unittest.TestCase):  # tested-by: ARCH-PROSE-024  # tested-by: REQ-PROSE-900  # tested-by: REQ-PROSE-901
    def _extract(self, d):
        reqs = R.load_requirements(os.path.join(d, "requirements"))
        members = R.scan_members(d, os.path.join(d, "requirements"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_extract(R.Workspace(reqs, members, os.path.join(d, "requirements"), d))
        return os.path.join(d, "requirements")

    def test_capability_prose_is_drafted(self):  # verifies: REQ-PROSE-900#CASE-1
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

    def test_explicitly_tagged_prose_not_redrafted(self):  # verifies: REQ-PROSE-901#CASE-1
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


class RiderGuards(unittest.TestCase):  # tested-by: ARCH-EXTRACT-008  # tested-by: ARCH-PROSE-024
    def test_tag_inside_html_comment_is_a_member(self):  # rider #1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"),
                   gtag_html("SENATE-SYNTH-001") + "\n<h1>x</h1>\n")
            members = R.scan_members(d, None)
            self.assertIn("SENATE-SYNTH-001", members)
            roles = [r for (r, _f, _l) in members["SENATE-SYNTH-001"]]
            self.assertIn("generated-from", roles)

    def test_draft_status_is_not_enforced(self):  # rider #3  # verifies: REQ-CHECK-828#CASE-5
        self.assertNotIn("draft", R.ENFORCED)
        self.assertEqual(R.ENFORCED, {"in-progress", "implemented", "confirmed"})


class JsFacts(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009
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


class ParserBlockLists(unittest.TestCase):  # tested-by: ARCH-PARSE-001
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

    def test_inline_list_preserves_embedded_hash(self):  # bug: clean-item-eats-embedded-hash
        meta, _ = R.parse_frontmatter("---\ntags: [issue#1, fix]\n---\nbody")
        self.assertEqual(meta["tags"], ["issue#1", "fix"])

    def test_inline_list_still_strips_trailing_comment(self):
        meta, _ = R.parse_frontmatter("---\ntags: [a, b]  # trailing\n---\nbody")
        self.assertEqual(meta["tags"], ["a", "b"])

    def test_block_list_preserves_embedded_hash(self):
        meta, _ = R.parse_frontmatter("---\ntags:\n  - issue#123\n  - clean\n---\nbody")
        self.assertEqual(meta["tags"], ["issue#123", "clean"])


class PyFacts(unittest.TestCase):  # tested-by: ARCH-CANDIDATES-009  # tested-by: REQ-CANDIDATES-826
    def test_nul_byte_source_yields_empty_facts(self):
        """A source with an embedded NUL byte makes ast.parse raise ValueError (not
        SyntaxError); _py_facts must swallow it and yield empty facts (#8)."""
        facts = R._py_facts("x = 1\x00\ny = 2\n")
        self.assertEqual(facts, {"signatures": [], "docstrings": {}, "imports": []})

    def test_syntax_error_yields_empty_facts(self):
        self.assertEqual(R._py_facts("def ("),
                         {"signatures": [], "docstrings": {}, "imports": []})

    def test_whitespace_only_module_docstring_degrades_to_empty(self):  # bug: py-facts-whitespace-docstring-indexerror
        facts = R._py_facts('"""\n   \n"""\ndef f():\n    pass\n')
        self.assertEqual(facts["docstrings"], {})
        self.assertEqual(facts["signatures"], ["def f()"])

    def test_whitespace_only_function_docstring_degrades_to_empty(self):  # bug: py-facts-whitespace-docstring-indexerror
        facts = R._py_facts('def f():\n    """\n       \n    """\n    pass\n')
        self.assertEqual(facts["docstrings"], {})


class CountAc(unittest.TestCase):  # tested-by: ARCH-LINTCHECKS-025
    def test_ignores_fenced_bullets(self):
        """Bullet lines inside a ``` fence in the Acceptance section don't inflate
        the AC count (#11)."""
        body = ("## HOW — Acceptance\n- AC one\n- AC two\n"
                "```\n- not an AC\n- also not an AC\n```\n")
        self.assertEqual(R._count_ac(body), 2)

    def test_anchored_heading_not_commentary(self):
        """A `## Notes — acceptance …` commentary heading before the real section
        must not capture the count (#12)."""
        body = ("## Notes — acceptance caveats\n- note one\n- note two\n"
                "## HOW — Acceptance\n- AC one\n- AC two\n- AC three\n")
        self.assertEqual(R._count_ac(body), 3)


class AcParsing(unittest.TestCase):  # tested-by: ARCH-ACVERIFY-019  # tested-by: ARCH-MAP-007
    """The Gherkin AC BLOCK the template prescribes must reach `acc` — it never did:
    `_bullets` collects only `- ` lines, so 50/50 nodes of this repo's own map
    carried `acc: []` while the raw text sat in `accept`."""

    GHERKIN = ("AC-1  <!-- verifiable by: automated test -->\n"
               "  Given  a labelled criterion\n  When   the map is built\n"
               "  Then   the criterion appears in `acc`\n"
               "AC-2\n  Given  a second one\n  Then   it appears too\n")

    def test_labelled_blocks_reach_acc(self):
        items = R._acc_items(_ac_body(acceptance=self.GHERKIN))
        self.assertEqual(len(items), 2)
        self.assertTrue(items[0].startswith("AC-1 — Given"))
        self.assertIn("the criterion appears in `acc`", items[0])
        self.assertNotIn("verifiable by", items[0])       # marker comment stripped

    def test_bullet_acs_still_parse(self):
        items = R._acc_items(_ac_body(acceptance="- first criterion.\n- second criterion."))
        self.assertEqual(items, ["first criterion.", "second criterion."])

    def test_count_ac_agrees_with_the_parser(self):
        for acceptance in (self.GHERKIN, "- one.\n- two.\n- three.", "AC-1\n  Given x"):
            body = _ac_body(acceptance=acceptance)
            self.assertEqual(R._count_ac(body), len(R._acc_blocks(body)))

    def test_fenced_example_not_counted(self):
        body = _ac_body(acceptance="AC-1\n  Given x\n```\n- not a criterion\nAC-9\n```\n")
        self.assertEqual(R._labeled_acs(body), ["AC-1"])

    def test_map_node_emits_acc(self):  # verifies: REQ-MAP-870#CASE-4  # verifies: REQ-VIEWER-942#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n"
                   + _ac_body(acceptance=self.GHERKIN))
            reqs = R.load_requirements(d)
            node = R._build_map_data(reqs, {})["nodes"][0]
            self.assertEqual(len(node["acc"]), 2)
            self.assertTrue(node["accept"])                # raw section still emitted


class ScanCache(unittest.TestCase):  # tested-by: ARCH-SCANCACHE-023  # tested-by: REQ-SCANCACHE-911
    def _tree(self, d):
        rq = os.path.join(d, "requirements")
        os.makedirs(rq, exist_ok=True)
        _write(os.path.join(d, "a.py"), tag("A-X-001") + "\n# {}: A-X-001\n".format("tested" + "-by"))
        _write(os.path.join(d, "b.py"), tag("B-Y-002") + "\n")
        return rq

    def test_cache_results_byte_identical(self):  # verifies: ARCH-SCANCACHE-023  # verifies: REQ-SCANCACHE-911#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            no = R.scan_members(d, rq, cache=False)
            c1 = R.scan_members(d, rq, cache=True)    # builds cache
            c2 = R.scan_members(d, rq, cache=True)    # reuses cache
            self.assertEqual(no, c1)
            self.assertEqual(no, c2)
            self.assertTrue(os.path.exists(os.path.join(rq, "_scancache.json")))

    def test_cache_invalidates_on_change(self):  # verifies: REQ-SCANCACHE-911#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            p = os.path.join(d, "a.py")
            R.scan_members(d, rq, cache=True)                       # cache A-X-001
            _write(p, tag("C-Z-003") + "\n# changed, different size\n")   # size differs -> invalidate
            m = R.scan_members(d, rq, cache=True)
            self.assertIn("C-Z-003", m)
            self.assertNotIn("A-X-001", m)

    def test_cache_prunes_deleted_file(self):  # verifies: REQ-SCANCACHE-911#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            R.scan_members(d, rq, cache=True)
            os.remove(os.path.join(d, "b.py"))
            m = R.scan_members(d, rq, cache=True)
            self.assertNotIn("B-Y-002", m)
            cache = json.load(open(os.path.join(rq, "_scancache.json"), encoding="utf-8"))
            self.assertNotIn("b.py", cache)

    def test_cache_off_by_default_writes_nothing(self):  # verifies: REQ-SCANCACHE-911#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            R.scan_members(d, rq)                                   # no cache arg
            self.assertFalse(os.path.exists(os.path.join(rq, "_scancache.json")))

    def test_corrupt_cache_fails_open(self):  # verifies: REQ-SCANCACHE-911#CASE-5
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            _write(os.path.join(rq, "_scancache.json"), "{ not json")
            self.assertEqual(R.scan_members(d, rq, cache=False),
                             R.scan_members(d, rq, cache=True))     # corrupt cache -> full re-scan, same result


class PhantomMember(unittest.TestCase):
    """Fixtures F1-F8 from the phantom-member Senate spec."""

    # Split so this .py source does not register itself as a phantom member
    _CAP = "CORE" + "-SCAN-002"
    _ROLE = "impl" + "ements"
    _TAG = "# {}: {}".format(_ROLE, _CAP)
    _HTML_TAG = "<!-- {}: {} -->".format(_ROLE, _CAP)

    def _scan(self, filename, content):
        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, filename)
            _write(fp, content)
            return R._scan_file_tags(fp)

    def test_F1_md_html_comment_outside_fence_kept(self):
        """F1: <!-- implements: X --> in .md outside any fence is a real member."""
        content = "Prose.\n{}\nMore prose.\n".format(self._HTML_TAG)
        tags = self._scan("req.md", content)
        self.assertTrue(any(t[1] == self._CAP for t in tags),
                        "HTML comment tag outside fence must be kept")

    def test_F2_md_tag_inside_fence_dropped(self):
        """F2: tag inside a ``` fence block in .md is dropped."""
        content = "```\n{}\n```\n".format(self._TAG)
        tags = self._scan("doc.md", content)
        self.assertFalse(any(t[1] == self._CAP for t in tags),
                         "tag inside fenced block must be dropped")

    def test_F3_md_tag_in_backtick_span_dropped(self):
        """F3: tag inside a backtick span is dropped."""
        content = "See `{}` for details.\n".format(self._TAG)
        tags = self._scan("doc.md", content)
        self.assertFalse(any(t[1] == self._CAP for t in tags),
                         "tag inside backtick span must be dropped")

    def test_F4_md_tag_in_4space_indent_dropped(self):
        """F4: tag in a 4-space-indented block is dropped."""
        content = "    {}\n".format(self._TAG)
        tags = self._scan("doc.md", content)
        self.assertFalse(any(t[1] == self._CAP for t in tags),
                         "tag in 4-space indent must be dropped")

    def test_F5_py_tag_in_triple_quote_dropped(self):
        """F5: tag inside a triple-quoted docstring in .py is dropped."""
        content = 'def foo():\n    """\n    {}\n    """\n    pass\n'.format(self._TAG)
        tags = self._scan("module.py", content)
        self.assertFalse(any(t[1] == self._CAP for t in tags),
                         "tag in triple-quoted docstring must be dropped")

    def test_indented_fence_marker_does_not_swallow_later_tags(self):
        """An indented ```-prefixed line in .md is an indented code block, not a
        fence opener; it must not swallow tags that follow it (#3)."""
        content = "Example:\n\n    ```python\n\n{}\n".format(self._HTML_TAG)
        tags = self._scan("doc.md", content)
        self.assertTrue(any(t[1] == self._CAP for t in tags),
                        "indented ``` must not open a phantom fence")

    def test_html_indented_tag_comment_kept(self):
        """HTML has no indented-code-block concept; an indented tag comment in
        .html must still be scanned (#4)."""
        content = "<div>\n        {}\n</div>\n".format(self._HTML_TAG)
        tags = self._scan("page.html", content)
        self.assertTrue(any(t[1] == self._CAP for t in tags),
                        "indented HTML tag comment must be kept")

    def test_html_tag_inside_fence_dropped(self):
        """The ``` fence exclusion applies to .html too — a tag inside a fenced
        block in .html is dropped (complements the .md fence case)."""
        content = "```\n{}\n```\n".format(self._HTML_TAG)
        tags = self._scan("page.html", content)
        self.assertFalse(any(t[1] == self._CAP for t in tags),
                         "tag inside a fenced block in .html must be dropped")

    def test_F6_state_resets_per_file(self):
        """F6: fence/triple-quote state does not leak across files."""
        contentA = "```\n{}\n".format(self._TAG)   # opens fence, never closes
        contentB = "{}\n".format(self._TAG)          # plain prose tag
        with tempfile.TemporaryDirectory() as d:
            fpA = os.path.join(d, "a.md")
            fpB = os.path.join(d, "b.md")
            _write(fpA, contentA)
            _write(fpB, contentB)
            tagsA = R._scan_file_tags(fpA)
            tagsB = R._scan_file_tags(fpB)
        self.assertFalse(any(t[1] == self._CAP for t in tagsA),
                         "tag inside unclosed fence in file A must be dropped")
        self.assertTrue(any(t[1] == self._CAP for t in tagsB),
                        "state must reset — file B tag must be kept")

    def test_F7_py_inline_comment_tag_kept(self):
        """F7: tag in an inline comment is kept."""
        content = "code()  {}\n".format(self._TAG)
        tags = self._scan("module.py", content)
        self.assertTrue(any(t[1] == self._CAP for t in tags),
                        "inline comment tag in .py must be kept")

    def test_F8_longer_fence_contains_shorter(self):
        """F8: a 4-backtick fence containing 3-backtick content closes on length match."""
        content = "````\n```\n{}\n```\n````\n".format(self._TAG)
        tags = self._scan("doc.md", content)
        self.assertFalse(any(t[1] == self._CAP for t in tags),
                         "tag inside outer 4-backtick fence must be dropped")


NL = chr(10)


class SingleWalkEquivalence(unittest.TestCase):  # tested-by: ARCH-SCAN-002  # tested-by: REQ-SCAN-909
    """scan_all must return exactly what the three separate scanners return.

    This is the whole safety argument for the refactor: the three scanners have
    DIFFERENT masking rules (fences and indents for prose, string literals for .py,
    a backtick strip for levelled tags only), so "they look the same" is not evidence.
    Equality is asserted on real trees instead, including this repo's own.
    """

    def _tree(self, d):
        _write(os.path.join(d, "requirements", "REQ-A-001.md"),
               "---" + NL + "id: REQ-A-001" + NL + "status: confirmed" + NL + "layer: bus" + NL
               + "---" + NL + NL + "# T" + NL)
        impl = "impl" + "ements"
        _write(os.path.join(d, "src", "a.py"),
               "# {}: REQ-A-001".format(impl) + NL
               + "def test_x():  # verifies: REQ-A-001#AC-1" + NL
               + "    return 1" + NL)
        _write(os.path.join(d, "src", "b.py"),
               '"""A docstring mentioning verifies: REQ-A-001#AC-9 must NOT count."""' + NL
               + "# tested-by: REQ-A-001 @unit" + NL)
        _write(os.path.join(d, "notes.md"),
               "Prose showing `# tested-by: REQ-A-001 @system` in backticks must not count." + NL
               + "```" + NL + "# {}: REQ-FENCED-999".format(impl) + NL + "```" + NL)
        _write(os.path.join(d, "src", "c.ts"),
               "// {}: REQ-A-001".format(impl) + NL + "// verifies: REQ-A-001#AC-2" + NL)
        return os.path.join(d, "requirements")

    def test_matches_the_three_scanners_on_a_mixed_tree(self):  # verifies: ARCH-SCAN-002#CASE-7  # verifies: REQ-SCAN-909#CASE-7
        with tempfile.TemporaryDirectory() as d:
            rdir = self._tree(d)
            one = R.scan_all(d, rdir)
            three = (R.scan_members(d, rdir), R.scan_ac_verifies(d, rdir),
                     R.scan_test_levels(d, rdir))
            self.assertEqual(one, three)
            self.assertIn("REQ-A-001", one[0])          # the fixture is not vacuous
            self.assertNotIn("REQ-FENCED-999", one[0])  # fenced example still excluded
            self.assertEqual(one[1]["REQ-A-001"].get("AC-9"), None)   # docstring excluded

    def test_matches_the_three_scanners_on_this_repo(self):
        """The fixture above is a model; this is the real corpus, every masking rule
        exercised by files that actually use them. Skipped outside the repo."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(R.__file__)))
        rdir = os.path.join(root, "requirements")
        if not os.path.isdir(rdir):
            self.skipTest("not running inside the requirement-manager repo")
        self.assertEqual(R.scan_all(root, rdir),
                         (R.scan_members(root, rdir), R.scan_ac_verifies(root, rdir),
                          R.scan_test_levels(root, rdir)))

    def test_unreadable_file_is_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = self._tree(d)
            os.makedirs(os.path.join(d, "src", "weird.py"), exist_ok=True)  # a DIR named .py
            members, _ac, _lv = R.scan_all(d, rdir)
            self.assertIn("REQ-A-001", members)


class UntrackedMembers(unittest.TestCase):  # tested-by: ARCH-TRACKED-042  # tested-by: REQ-TRACKED-936
    """A member git does not track breaks reproducibility of the committed map.

    Both real instances came from a gitignored directory the local scan could see and
    CI never could: a subagent worktree, and a Consilium report carrying a real
    `generated-from:` tag. Each produced a committed map naming files absent from a
    fresh checkout, and surfaced only as a confusing CI-only staleness failure.
    """

    def _repo(self, d):
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        for cfg in (["config", "user.email", "t@t.com"], ["config", "user.name", "T"]):
            subprocess.run(["git", "-C", d] + cfg, check=True, capture_output=True)

    def _members(self, *paths):
        return {"REQ-A-001": [("implements", p, 1) for p in paths]}

    def test_untracked_member_is_reported(self):  # verifies: REQ-TRACKED-936#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(os.path.join(d, "tracked.py"), "x=1" + chr(10))
            _write(os.path.join(d, "ignored.py"), "x=1" + chr(10))
            subprocess.run(["git", "-C", d, "add", "tracked.py"], check=True, capture_output=True)
            subprocess.run(["git", "-C", d, "commit", "-m", "t"], check=True, capture_output=True)
            out = R.untracked_members(d, self._members("tracked.py", "ignored.py"))
            self.assertEqual(out, ["ignored.py"])

    def test_all_tracked_reports_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(os.path.join(d, "a.py"), "x=1" + chr(10))
            subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
            subprocess.run(["git", "-C", d, "commit", "-m", "t"], check=True, capture_output=True)
            self.assertEqual(R.untracked_members(d, self._members("a.py")), [])

    def test_nested_member_path_is_matched(self):
        """git ls-files emits POSIX separators; members carry them too, but the
        comparison must survive a Windows checkout either way."""
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(os.path.join(d, "src", "pkg", "a.py"), "x=1" + chr(10))
            subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
            subprocess.run(["git", "-C", d, "commit", "-m", "t"], check=True, capture_output=True)
            self.assertEqual(R.untracked_members(d, self._members("src/pkg/a.py")), [])

    def test_outside_a_work_tree_fails_open(self):  # verifies: REQ-TRACKED-936#CASE-4
        """None, not [] — the same fail-open signal _since_changed_files uses. A repo
        distributed as a tarball must not be told its every member is untracked."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), "x=1" + chr(10))
            self.assertIsNone(R.untracked_members(d, self._members("a.py")))


# ---------------------------------------------------------------------------
# Regression tests for the 2026-06-28 multi-agent (consilium) bug hunt — 15 fixes.
# ---------------------------------------------------------------------------
class BugHuntParsing(unittest.TestCase):  # tested-by: ARCH-PARSE-001
    def test_quoted_scalar_keeps_inner_hash(self):
        """A '#' inside a quoted scalar is DATA, not a comment (was truncated)."""
        meta, _ = R.parse_frontmatter('---\nsummary: "Parses a # fragment"\n---\n')
        self.assertEqual(meta["summary"], "Parses a # fragment")

    def test_quoted_scalar_with_trailing_comment_still_unquoted(self):
        meta, _ = R.parse_frontmatter('---\nsummary: "foo" # a comment\n---\n')
        self.assertEqual(meta["summary"], "foo")

    def test_quoted_inline_list_item_keeps_inner_hash(self):
        meta, _ = R.parse_frontmatter('---\ndepends_on: ["A-1 # note"]\n---\n')
        self.assertEqual(meta["depends_on"], ["A-1 # note"])

    def test_body_strips_leading_cr_after_crlf_close(self):
        _, body = R.parse_frontmatter("---\nid: REQ-A-001\n---\r\nBODY\r\n")
        self.assertFalse(body.startswith("\r"))
        self.assertTrue(body.startswith("BODY"))

    def test_duplicate_id_keeps_first_and_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "aaa.md"), "---\nid: REQ-DUP-001\nstatus: draft\n---\n# A\n")
            _write(os.path.join(d, "bbb.md"), "---\nid: REQ-DUP-001\nstatus: draft\n---\n# B\n")
            err = io.StringIO()
            with redirect_stderr(err):
                reqs = R.load_requirements(d)
            self.assertEqual(len(reqs), 1)
            self.assertTrue(reqs["REQ-DUP-001"]["path"].endswith("aaa.md"))
            self.assertIn("REQ-DUP-001", err.getvalue())


class BugHuntScanning(unittest.TestCase):  # tested-by: ARCH-ACVERIFY-019
    def test_verifies_inside_python_string_ignored(self):
        V = "verif" + "ies"
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "t.py"),
                   "# %s: REQ-AC-001#AC-1\n" % V
                   + 'def f():\n    """note %s: REQ-AC-001#AC-2 end"""\n    return 1\n' % V)
            cover = R.scan_ac_verifies(d, os.path.join(d, "requirements"))
            self.assertIn("AC-1", cover.get("REQ-AC-001", {}))
            self.assertNotIn("AC-2", cover.get("REQ-AC-001", {}))

    def test_labeled_acs_skips_fenced_block(self):
        body = "## HOW — Acceptance\nAC-1 real\n\n```\nAC-2 example\n```\nAC-3 real\n"
        self.assertEqual(R._labeled_acs(body), ["AC-1", "AC-3"])


class PruneDirs(unittest.TestCase):  # tested-by: ARCH-SCAN-002
    """The walk's prune step: SSOT dir by realpath (name-gated), ignored dirs not descended."""

    def test_source_package_named_requirements_is_still_scanned(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"), REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(d, "pkg", "requirements", "impl.py"), "x = 1  " + tag("REQ-A-001"))
            members = R.scan_members(d, rd)
            self.assertIn("pkg/requirements/impl.py", [fp for _, fp, _ in members["REQ-A-001"]])

    def test_ssot_dir_is_pruned_and_realpath_is_name_gated(self):
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            os.makedirs(os.path.join(d, "src"))
            dirs = ["requirements", "src", "node_modules"]
            calls = []
            real = os.path.realpath
            with mock.patch.object(R.os.path, "realpath", side_effect=lambda p: calls.append(p) or real(p)):
                R._prune_dirs(d, dirs, rd)
            self.assertEqual(dirs, ["src"])
            self.assertTrue(all("requirements" in os.path.basename(c) for c in calls))   # never for src/

    def test_ignore_dir_pattern_prunes_the_walk(self):
        dirs = ["build", "src", "docs"]
        R._prune_dirs("/root", dirs, None, code_root="/root", ignore=["build/**", "docs/*.md"])
        self.assertEqual(dirs, ["src", "docs"])        # docs/*.md is a file pattern: docs stays

    def test_dockerfile_variants_and_schema_files_are_code(self):
        for fn in ("Dockerfile.converter", "Dockerfile.dev", "Caddyfile", "schema.prisma", "api.graphql", "x.proto"):
            self.assertTrue(R._is_code_file(fn), fn)
        self.assertFalse(R._is_code_file("Dockerfile-notes.txt"))

    def test_prune_without_ignore_keeps_everything_but_noise(self):
        dirs = [".git", "build", "__pycache__", "src"]
        R._prune_dirs("/root", dirs, None)
        self.assertEqual(dirs, ["build", "src"])


class UnscannedTags(unittest.TestCase):  # tested-by: ARCH-UNSCANNEDTAG-045  # tested-by: REQ-UNSCANNEDTAG-939
    """A tag in a file type the scan never reads is not a member — say so."""

    def _repo(self, d):
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        for cfg in (["config", "user.email", "t@t.com"], ["config", "user.name", "T"]):
            subprocess.run(["git", "-C", d] + cfg, check=True, capture_output=True)

    def _commit_all(self, d):
        subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-q", "-m", "t"], check=True, capture_output=True)

    def test_tag_in_unscanned_type_is_reported_and_gate_warns(self):  # verifies: ARCH-UNSCANNEDTAG-045#CASE-1  # verifies: ARCH-UNSCANNEDTAG-045#CASE-2  # verifies: REQ-UNSCANNEDTAG-939#CASE-1  # verifies: REQ-UNSCANNEDTAG-939#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"), REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(d, "a.py"), "x = 1  " + tag("REQ-A-001"))
            _write(os.path.join(d, "config.custom"), "# implements: REQ-A-001" + chr(10))
            _write(os.path.join(d, "notes.txt"), "no tag here" + chr(10))
            _write(os.path.join(d, "_derived.custom"), "implements: REQ-A-001" + chr(10))   # _-prefixed: skipped
            _write(os.path.join(d, ".gitattributes"), "# example: implements: REQ-A-001" + chr(10))  # git dotfile: skipped
            _write(os.path.join(d, ".env"), "# implements: REQ-A-001" + chr(10))                    # .env: reported
            with open(os.path.join(d, "pic.png"), "wb") as f:
                f.write(b"\x89PNG implements: REQ-A-001")
            self._commit_all(d)
            self.assertEqual(R.tagged_unscanned_files(d, rd), [".env", "config.custom"])
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(R.Workspace(reqs, members, rd, d), False)
            self.assertEqual(rc, 0)
            self.assertIn("never reads", buf.getvalue())
            self.assertIn("config.custom", buf.getvalue())

    def test_reqmapignore_and_ssot_dir_are_skipped(self):  # verifies: REQ-UNSCANNEDTAG-939#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"), REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(rd, "map.custom"), "implements: REQ-A-001" + chr(10))        # under the SSOT dir
            _write(os.path.join(d, "vendor", "x.custom"), "implements: REQ-A-001" + chr(10))  # ignored path
            _write(os.path.join(d, ".reqmapignore"), "vendor/**" + chr(10))
            self._commit_all(d)
            self.assertEqual(R.tagged_unscanned_files(d, rd), [])

    def test_outside_git_returns_none(self):  # verifies: ARCH-UNSCANNEDTAG-045#CASE-3  # verifies: REQ-UNSCANNEDTAG-939#CASE-6
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "config.custom"), "implements: REQ-A-001" + chr(10))
            self.assertIsNone(R.tagged_unscanned_files(d))


class MatrixScanReach(unittest.TestCase):  # tested-by: ARCH-SCAN-002
    def test_matrix_languages_are_code(self):
        for fn in ("a.scss", "App.vue", "x.svelte", "m.mjs", "c.cjs", "Program.cs", "index.php",
                   "app.rb", "Main.kt", "build.gradle.kts", "App.swift", "Main.scala", "mix.exs", "main.dart", "pyproject.toml"):
            self.assertTrue(R._is_code_file(fn), fn)


class ProseBuckets(unittest.TestCase):  # tested-by: ARCH-PROSE-024
    def test_lowercase_readme_is_sync_only(self):
        self.assertEqual(R.classify_prose("data/patterns/x/readme.md"), "sync_only")
        self.assertEqual(R.classify_prose("Readme.rst.md"), "sync_only")

    def test_h1_only_prose_keeps_its_sections(self):  # verifies: REQ-PROSE-901#CASE-3
        title, heads = R._prose_facts("# IDENTITY and PURPOSE\n\ntext\n\n# STEPS\n\n# OUTPUT INSTRUCTIONS\n")
        self.assertEqual(title, "IDENTITY and PURPOSE")
        self.assertEqual(heads, ["STEPS", "OUTPUT INSTRUCTIONS"])

    def test_h2_present_wins_over_later_h1(self):
        title, heads = R._prose_facts("# Title\n\n## Real section\n\n# Stray H1\n")
        self.assertEqual(heads, ["Real section"])


class AtomicForm(unittest.TestCase):  # tested-by: ARCH-ATOMICFORM-053
    """A body with no normative headings: a story plus one Scenario."""
    ATOMIC = ("# T\n\n"
              "> As a developer, I want `scan` to list every member under its capability id,\n"
              "> so that I can see which files back that capability.\n\n"
              "Scenario: a capability with two members\n"
              "  Given  a capability carrying two tags\n"
              "  When   `scan` runs\n"
              "  Then   both members print under its id\n\n"
              "## Members in code (auto)\n")

    def test_the_atomic_body_is_read_as_both_normative_sections(self):  # verifies: ARCH-ATOMICFORM-053#CASE-1
        self.assertTrue(R._atomic_spans(self.ATOMIC))
        self.assertTrue(R._has_section(self.ATOMIC, "contract"))
        self.assertTrue(R._has_section(self.ATOMIC, "acceptan"))
        self.assertEqual(R._count_ac(self.ATOMIC), 1)
        self.assertEqual(len(R._bullets(self.ATOMIC, "contract")), 1)

    def test_the_hash_covers_the_statement_and_the_scenario(self):  # verifies: ARCH-ATOMICFORM-053#CASE-2
        # The whole point: without this, a heading-less body hashes the EMPTY STRING, every
        # such requirement collides, and no content change could ever drift.
        empty = R.hashlib.sha256(b"").hexdigest()[:12]
        self.assertNotEqual(R.binding_hash(self.ATOMIC), empty)
        self.assertNotEqual(R.binding_hash(self.ATOMIC),
                            R.binding_hash(self.ATOMIC.replace("two tags", "three tags")))
        self.assertNotEqual(R.binding_hash(self.ATOMIC),
                            R.binding_hash(self.ATOMIC.replace("every member", "each member")))

    def test_an_atomic_requirement_lints_clean(self):  # verifies: ARCH-ATOMICFORM-053#CASE-3
        fs = R.lint_requirement("REQ-A-001", {"meta": {"status": "confirmed", "form": "atomic"},
                                              "body": self.ATOMIC})
        self.assertEqual(fs, [], "atomic form should raise no finding, got %r" % fs)

    def test_a_classic_body_is_untouched(self):  # verifies: ARCH-ATOMICFORM-053#CASE-4
        classic = ("# T\n\n> why.\n\n## WHAT — Contract (normative)\n- `x` does one thing.\n"
                   "\n## HOW — Acceptance (= tests)\n- a.\n- b.\n- c.\n")
        self.assertIsNone(R._atomic_spans(classic))
        self.assertEqual(R._bullets(classic, "contract"), ["`x` does one thing."])

    def test_atomic_bullets_keeps_real_leading_quote_char(self):  # bug: bullets-lstrip-char-class
        # lstrip("> ") strips a CHARACTER CLASS ({">", " "}), not the single literal ">"
        # quote marker -- it must not also eat a real leading ">" that follows the marker
        # (e.g. ">100 requests/sec" must keep its ">100", not become "100 requests/sec").
        body = ("# T\n\n"
                "> >100 requests/sec triggers throttling.\n\n"
                "Scenario: over the limit\n"
                "  Given  heavy load\n"
                "  When   the limiter runs\n"
                "  Then   requests are throttled\n\n"
                "## Members in code (auto)\n")
        self.assertEqual(R._bullets(body, "contract"), [">100 requests/sec triggers throttling."])

    def _story(self, bullets, thens):
        """An atomic body whose story quote lists `bullets` facts and whose Scenario
        carries `thens` `Then` lines -- for the atomic-bullet-then-mismatch /
        atomic-story-overlong fixtures below."""
        quote = ["> The refresh does {} things:".format(bullets)]
        quote += ["> - fact {}".format(i + 1) for i in range(bullets)]
        scen = ["Scenario: a refresh", "  Given  a stale cache", "  When   refresh runs"]
        scen += ["  Then   fact {} holds".format(i + 1) for i in range(thens)]
        return "# T\n\n" + "\n".join(quote) + "\n\n" + "\n".join(scen) + "\n\n## Members in code (auto)\n"

    def test_atomic_story_bullets_must_each_get_their_own_then(self):  # verifies: ARCH-LINTCHECKS-025#CASE-11  # verifies: ARCH-ATOMICFORM-053#CASE-5  # verifies: REQ-LINTCHECKS-867#CASE-1
        fs = R.lint_requirement("REQ-A-002", {"meta": {"status": "confirmed", "form": "atomic"},
                                              "body": self._story(3, 1)})
        self.assertIn(("warn", "atomic-bullet-then-mismatch"),
                      [(f["severity"], f["check"]) for f in fs])

    def test_atomic_story_bullets_matching_then_count_lints_clean(self):
        fs = R.lint_requirement("REQ-A-003", {"meta": {"status": "confirmed", "form": "atomic"},
                                              "body": self._story(2, 2)})
        self.assertEqual(fs, [])

    def test_atomic_story_bullets_at_the_ceiling_lints_clean(self):
        # The ceiling is a CAN, not a MUST: 3 bullets (LINT_ATOMIC_STORY_BULLETS_MAX) with
        # 3 matching Then lines is fully permitted, not just 1 or 2.
        fs = R.lint_requirement("REQ-A-004", {"meta": {"status": "confirmed", "form": "atomic"},
                                              "body": self._story(R.LINT_ATOMIC_STORY_BULLETS_MAX,
                                                                   R.LINT_ATOMIC_STORY_BULLETS_MAX)})
        self.assertEqual(fs, [])

    def test_atomic_story_overlong_fires_past_the_ceiling(self):  # verifies: ARCH-LINTCHECKS-025#CASE-12  # verifies: ARCH-ATOMICFORM-053#CASE-5  # verifies: REQ-LINTCHECKS-867#CASE-2
        fs = R.lint_requirement("REQ-A-005", {"meta": {"status": "confirmed", "form": "atomic"},
                                              "body": self._story(R.LINT_ATOMIC_STORY_BULLETS_MAX + 1,
                                                                   R.LINT_ATOMIC_STORY_BULLETS_MAX + 1)})
        checks = [(f["severity"], f["check"]) for f in fs]
        self.assertIn(("warn", "atomic-story-overlong"), checks)
        self.assertNotIn(("warn", "atomic-bullet-then-mismatch"), checks)


class ModuleFile(unittest.TestCase):  # tested-by: ARCH-MODULEFILE-056
    """One .md may hold many requirements: a block starts at `---` followed by `id:`."""

    def _mod(self, *ids):
        return "\n".join(
            REQ.format(id=i, status="draft", layer="feature", extra="", title=i)
            + "\nbody of " + i + "\n"
            for i in ids)

    def test_single_block_file_is_byte_identical(self):  # verifies: ARCH-MODULEFILE-056#CASE-2
        # a one-block file must come back as the whole text, or every existing corpus shifts
        text = REQ.format(id="AREA-A-001", status="draft", layer="bus", extra="", title="A") + "\nprose\n"
        self.assertEqual(R.split_requirement_blocks(text), [text])

    def test_each_block_becomes_its_own_requirement(self):  # verifies: ARCH-MODULEFILE-056#CASE-1  # verifies: REQ-PARSE-890#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-A-001.md"), self._mod("AREA-A-001", "AREA-A-002", "AREA-A-003"))
            reqs = R.load_requirements(d)
            self.assertEqual(sorted(reqs), ["AREA-A-001", "AREA-A-002", "AREA-A-003"])
            for i, rid in enumerate(sorted(reqs)):
                self.assertIn("body of " + rid, reqs[rid]["body"])
                self.assertEqual(reqs[rid]["block"], i)
                self.assertTrue(reqs[rid]["path"].endswith("AREA-A-001.md"))

    def test_horizontal_rule_starts_no_block(self):  # verifies: ARCH-MODULEFILE-056#CASE-3
        # a bare `---` not followed by `id:` is a markdown rule, not a new requirement
        text = (REQ.format(id="AREA-B-001", status="draft", layer="bus", extra="", title="B")
                + "\nbefore\n\n---\n\nafter\n")
        self.assertEqual(R.split_requirement_blocks(text), [text])
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "AREA-B-001.md"), text)
            reqs = R.load_requirements(d)
            self.assertEqual(list(reqs), ["AREA-B-001"])
            self.assertIn("after", reqs["AREA-B-001"]["body"])

    def test_only_the_first_block_falls_back_to_the_filename(self):  # verifies: ARCH-MODULEFILE-056#CASE-5
        # block 0 may take its id from the file name; a later block with no id: must not,
        # or every module would mint a second copy of its own file name.
        with tempfile.TemporaryDirectory() as d:
            text = ("---\nstatus: draft\nlayer: bus\n---\n\n# no id\n\n"
                    + REQ.format(id="AREA-C-002", status="draft", layer="bus", extra="", title="C2"))
            _write(os.path.join(d, "AREA-C-001.md"), text)
            reqs = R.load_requirements(d)
            self.assertEqual(sorted(reqs), ["AREA-C-001", "AREA-C-002"])

    def test_confirm_flips_only_the_named_block(self):  # verifies: ARCH-MODULEFILE-056#CASE-4
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "AREA-D-001.md")
            _write(p, self._mod("AREA-D-001", "AREA-D-002"))
            _write(os.path.join(d, "d.py"), tag("AREA-D-002") + "\n")
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = 0 if R._write_frontmatter_status(reqs["AREA-D-002"], "confirmed") else 1
            self.assertEqual(code, 0, buf.getvalue())
            after = R.load_requirements(d)
            self.assertEqual(after["AREA-D-002"]["meta"]["status"], "confirmed")
            self.assertEqual(after["AREA-D-001"]["meta"]["status"], "draft")
            self.assertIn("body of AREA-D-001", after["AREA-D-001"]["body"])

    def test_preamble_before_the_first_block_is_kept(self):
        text = "# Module heading\n\n" + REQ.format(
            id="AREA-E-001", status="draft", layer="bus", extra="", title="E")
        blocks = R.split_requirement_blocks(text)
        self.assertEqual(len(blocks), 2)
        self.assertIn("Module heading", blocks[0])
        self.assertTrue(blocks[1].startswith("---\nid: AREA-E-001"))

    def test_preamble_does_not_shadow_a_same_named_first_block(self):
        # bug: a file preamble landing at split index 0 used to be eligible for the
        # filename fallback exactly like a genuine block 0. When the file is named
        # after its own real first requirement's id, the empty-meta preamble claimed
        # that id first and the real block was silently dropped as a "duplicate".
        with tempfile.TemporaryDirectory() as d:
            text = ("# Module heading\n\nsome prose\n\n" + REQ.format(
                id="AREA-E-001", status="draft", layer="bus", extra="", title="E")
                + "\nreal body content\n")
            _write(os.path.join(d, "AREA-E-001.md"), text)
            buf = io.StringIO()
            with redirect_stderr(buf):
                reqs = R.load_requirements(d)
            self.assertEqual(list(reqs), ["AREA-E-001"])
            self.assertEqual(reqs["AREA-E-001"]["meta"].get("status"), "draft")
            self.assertEqual(reqs["AREA-E-001"]["meta"].get("layer"), "bus")
            self.assertIn("real body content", reqs["AREA-E-001"]["body"])
            self.assertEqual(buf.getvalue(), "")  # no spurious duplicate-id warning


class DescriptionSection(unittest.TestCase):  # tested-by: ARCH-DESCRIPTION-057
    """`## Description` + `## Cases`/`CASE-N` are the current names; the older
    `## WHAT — Contract` + `## HOW — Acceptance`/`AC-N` keep working unchanged."""

    CUR = ("# T\n\n## Description\n> the intent, in one quoted line.\n\n"
           "Every bullet below is binding.\n- `x` does the thing.\n\n"
           "## Cases (= tests)\nCASE-1\n  Given a\n  When b\n  Then c\n")
    OLD = ("# T\n\n> the intent, in one quoted line.\n\n"
           "## WHAT — Contract (normative)\nEvery line in this section is binding.\n"
           "- `x` does the thing.\n\n"
           "## HOW — Acceptance (= tests)\nAC-1\n  Given a\n  When b\n  Then c\n")

    def test_both_spellings_are_seen_as_the_same_sections(self):  # verifies: ARCH-DESCRIPTION-057#CASE-1
        for body in (self.CUR, self.OLD):
            self.assertTrue(R._has_any(body, R.CONTRACT_LABELS))
            self.assertTrue(R._has_any(body, R.ACCEPTANCE_LABELS))
            self.assertEqual([c for _n, c in R._contract_clauses(body)], ["`x` does the thing."])
            self.assertEqual(R._count_ac(body), 1)

    def test_the_label_is_read_under_either_spelling(self):  # verifies: ARCH-DESCRIPTION-057#CASE-1
        self.assertEqual(R._labeled_acs(self.CUR), ["CASE-1"])
        self.assertEqual(R._labeled_acs(self.OLD), ["AC-1"])

    def test_a_verifies_tag_may_name_either_label(self):  # verifies: ARCH-DESCRIPTION-057#CASE-2
        for txt, want in (("# verifies: AREA-X-001#CASE-2", "CASE-2"),
                          ("# verifies: AREA-X-001#AC-2", "AC-2")):
            m = R.AC_VERIFY_RE.search(txt)
            self.assertIsNotNone(m, txt)
            self.assertEqual(m.group(2), want)

    def test_the_intent_quote_is_not_part_of_the_drift_hash(self):  # verifies: ARCH-DESCRIPTION-057#CASE-3
        # the quote moved INSIDE the normative section; editing rationale must not drift a
        # confirmed contract, which is the whole reason blockquotes are skipped there.
        edited = self.CUR.replace("the intent, in one quoted line.", "a better explanation.")
        self.assertNotEqual(edited, self.CUR)
        self.assertEqual(R.binding_hash(edited), R.binding_hash(self.CUR))

    def test_editing_a_clause_still_drifts(self):  # verifies: ARCH-DESCRIPTION-057#CASE-4
        edited = self.CUR.replace("`x` does the thing.", "`x` does another thing.")
        self.assertNotEqual(R.binding_hash(edited), R.binding_hash(self.CUR))

    def test_editing_a_case_criterion_still_drifts(self):  # bug: cases-heading-excluded-from-drift-hash  # verifies: ARCH-DESCRIPTION-057#CASE-4
        # _NORMATIVE_HEADING_RE used to hand-list keywords instead of reading
        # CONTRACT_LABELS/ACCEPTANCE_LABELS, and omitted "cases" — so `## Cases`
        # (the current spelling) was silently excluded from the drift hash: editing a
        # CASE-1 Then-line never tripped DRIFT under a confirmed requirement.
        edited = self.CUR.replace("Then c", "Then z")
        self.assertNotEqual(edited, self.CUR)
        self.assertNotEqual(R.binding_hash(edited), R.binding_hash(self.CUR))

    def test_the_intent_is_still_read_from_inside_the_section(self):  # verifies: ARCH-DESCRIPTION-057#CASE-5
        self.assertEqual(R._first_quote(self.CUR), "the intent, in one quoted line.")
        self.assertEqual(R._first_quote(self.OLD), "the intent, in one quoted line.")

    def test_legacy_desc_field_does_not_swallow_the_description_section(self):
        # `desc` belongs to the old Input/Description/Output triad. Without the guard it
        # would re-emit the whole contract into a second viewer field.
        reqs = {"AREA-X-001": {"meta": {"id": "AREA-X-001", "status": "draft"}, "body": self.CUR}}
        data = R._build_map_data(reqs, {})
        node = [n for n in data["nodes"] if n["id"] == "AREA-X-001"][0]
        self.assertEqual(node["desc"], "")
        self.assertEqual(node["contract"], ["`x` does the thing."])


class CasesProse(unittest.TestCase):  # tested-by: ARCH-PROSE-024  # tested-by: REQ-PROSE-901
    def test_editing_source_prose_does_not_change_binding_hash(self):  # verifies: REQ-PROSE-901#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "prompts", "foo.md"), "---\ntitle: Foo\n---\n## Role\nx\n")
            rd = os.path.join(d, "requirements")
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract(R.Workspace(reqs, members, rd, d))
            reqs_after = R.load_requirements(rd)
            drafted_ids = [rid for rid in reqs_after if "PROMPTS-FOO" in rid]
            self.assertTrue(drafted_ids, list(reqs_after))
            rid = drafted_ids[0]
            hash_before = R.binding_hash(reqs_after[rid]["body"])
            # edit the SOURCE prose file, not the drafted requirement
            _write(os.path.join(d, "prompts", "foo.md"),
                   "---\ntitle: Foo\n---\n## Role\ncompletely different text now\n## New\nmore\n")
            reqs_reloaded = R.load_requirements(rd)
            hash_after = R.binding_hash(reqs_reloaded[rid]["body"])
            self.assertEqual(hash_before, hash_after)


class CasesUnscannedtag045(unittest.TestCase):  # tested-by: REQ-UNSCANNEDTAG-939
    def _repo(self, d):
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        for cfg in (["config", "user.email", "t@t.com"], ["config", "user.name", "T"]):
            subprocess.run(["git", "-C", d] + cfg, check=True, capture_output=True)

    def _commit_all(self, d):
        subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-q", "-m", "t"], check=True, capture_output=True)

    def test_gate_warning_caps_named_files_and_states_total(self):  # verifies: REQ-UNSCANNEDTAG-939#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            for i in range(7):
                _write(os.path.join(d, "f{}.custom".format(i)), "# implements: REQ-A-001\n")
            self._commit_all(d)
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, members, rd, d), False)
            out = buf.getvalue()
        self.assertIn("7 tag(s) in file type(s) the scan never reads", out)
        for i in range(5):
            self.assertIn("f{}.custom".format(i), out)
        self.assertNotIn("f5.custom", out)
        self.assertNotIn("f6.custom", out)

    def test_gate_warning_names_both_remedies(self):  # verifies: REQ-UNSCANNEDTAG-939#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(d, "f0.custom"), "# implements: REQ-A-001\n")
            self._commit_all(d)
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, members, rd, d), False)
            out = buf.getvalue()
        self.assertIn("not members", out)
        self.assertIn("Move the tag into a scannable file", out)
        self.assertIn("ask for the type to be added to the scan", out)

    def test_non_utf8_file_is_skipped(self):  # verifies: REQ-UNSCANNEDTAG-939#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            bad = os.path.join(d, "weird.custom")
            with open(bad, "wb") as f:
                f.write(b"# implements: REQ-A-001\n\xff\xfe\x80 bad bytes\n")
            self._commit_all(d)
            self.assertEqual(R.tagged_unscanned_files(d, rd), [])


class CasesTracked042(unittest.TestCase):  # tested-by: REQ-TRACKED-936
    def _repo(self, d):
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        for cfg in (["config", "user.email", "t@t.com"], ["config", "user.name", "T"]):
            subprocess.run(["git", "-C", d] + cfg, check=True, capture_output=True)

    def test_gate_warning_caps_named_untracked_files_and_states_total(self):  # verifies: REQ-TRACKED-936#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            for i in range(7):
                _write(os.path.join(d, "f{}.py".format(i)), tag("REQ-A-001") + "\n")
            # nothing committed -> git ls-files reports nothing tracked -> all untracked
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, members, rd, d), False)
            out = buf.getvalue()
        self.assertIn("7 member(s) are not tracked by git", out)
        for i in range(5):
            self.assertIn("f{}.py".format(i), out)
        self.assertNotIn("f5.py", out)
        self.assertNotIn("f6.py", out)

    def test_gate_warning_names_both_remedies(self):  # verifies: REQ-TRACKED-936#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(d, "f0.py"), tag("REQ-A-001") + "\n")
            reqs = R.load_requirements(rd)
            members = R.scan_members(d, rd)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, members, rd, d), False)
            out = buf.getvalue()
        self.assertIn("Commit them", out)
        self.assertIn(".reqmapignore", out)


class CasesParse001(unittest.TestCase):  # tested-by: REQ-PARSE-890
    def test_file_with_no_id_field_keyed_by_filename_stem(self):  # verifies: REQ-PARSE-890#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "REQ-A-001.md"), "---\nstatus: draft\n---\n\n# T\n")
            reqs = R.load_requirements(d)
        self.assertIn("REQ-A-001", reqs)
        self.assertEqual(reqs["REQ-A-001"]["meta"].get("status"), "draft")


class SeparatorIsNotContract(unittest.TestCase):  # tested-by: ARCH-DRIFT-003  # tested-by: REQ-DRIFT-841
    """Adding a requirement to a module file must not change its neighbour's hash."""

    ONE = ("---\nid: AREA-S-001\nstatus: confirmed\nlevel: code\nlayer: feature\n"
           "owner: A\n---\n\n# One\n\n## Description\n> Why.\n\n"
           "Every bullet below is binding.\n- It does one thing.\n\n"
           "## Cases\nCASE-1\n  Given  a\n  When   b\n  Then   c\n")
    TWO = ("\n\n--------------------\n\n\n"
           "---\nid: AREA-S-002\nstatus: draft\nlevel: code\nlayer: feature\n"
           "owner: A\n---\n\n# Two\n\n## Description\n> Why.\n\n"
           "Every bullet below is binding.\n- It does another thing.\n\n"
           "## Cases\nCASE-1\n  Given  a\n  When   b\n  Then   c\n")

    def test_appending_a_block_leaves_the_first_hash_alone(self):
        alone = R.split_requirement_blocks(self.ONE)[0]
        with_neighbour = R.split_requirement_blocks(self.ONE + self.TWO)[0]
        self.assertEqual(R.binding_hash(alone), R.binding_hash(with_neighbour))


class FencedTagsAreExamples(unittest.TestCase):  # tested-by: ARCH-SCAN-002  # tested-by: REQ-SCAN-992
    """One masking pass, so a tag shown as an example is an example to every scanner."""

    def _md(self):
        return ("# doc\n"
                "How to tag a case:\n"
                "\n"
                "```python\n"
                + v_tag("REQ-FAKE-999", "CASE-1") + "\n"
                + tag("REQ-FAKE-999") + "\n"
                "```\n"
                "\n"
                "<!-- " + _VERIFY_ROLE + ": REQ-REAL-001#CASE-2 -->\n"
                "<!-- " + _ROLE + ": REQ-REAL-001 -->\n")

    def test_fenced_verifies_is_not_coverage(self):  # verifies: REQ-SCAN-992#CASE-1
        ac, lv = {}, {}
        R._extract_coverage("x.md", "x.md", self._md().splitlines(True), ac, lv)
        self.assertNotIn("REQ-FAKE-999", ac)

    def test_a_tag_outside_the_fence_is_still_real(self):  # verifies: REQ-SCAN-992#CASE-2
        ac, lv = {}, {}
        R._extract_coverage("x.md", "x.md", self._md().splitlines(True), ac, lv)
        self.assertEqual(ac, {"REQ-REAL-001": {"CASE-2": [("x.md", 9)]}})

    def test_fenced_implements_is_not_a_member_either(self):  # verifies: REQ-SCAN-992#CASE-2
        found = R._scan_file_tags("x.md", self._md().splitlines(True))
        self.assertEqual(found, [[_ROLE, "REQ-REAL-001", 10]])

    def test_docstring_is_masked_and_a_comment_is_not(self):  # verifies: REQ-SCAN-992#CASE-3
        src = ('def f():\n'
               '    """\n'
               '    ' + v_tag("REQ-DOC-1", "CASE-1") + '\n'
               '    """\n'
               + v_tag("REQ-CODE-1", "CASE-1") + '\n')
        ac = {}
        R._extract_coverage("t.py", "t.py", src.splitlines(True), ac, {})
        self.assertEqual(ac, {"REQ-CODE-1": {"CASE-1": [("t.py", 5)]}})

    def test_an_indented_fence_marker_opens_no_fence(self):  # verifies: REQ-SCAN-992#CASE-4
        md = ("# doc\n"
              "    ```\n"
              "\n"
              "<!-- " + _ROLE + ": REQ-AFTER-001 -->\n")
        self.assertEqual(R._scan_file_tags("x.md", md.splitlines(True)),
                         [[_ROLE, "REQ-AFTER-001", 4]])

    def test_every_scanner_agrees_on_every_position(self):  # verifies: REQ-SCAN-992#CASE-5
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        _write(os.path.join(d, "doc.md"), self._md())
        _write(os.path.join(d, "t.py"),
               '"""\n' + v_tag("REQ-DOC-1", "CASE-1") + '\n"""\n'
               + v_tag("REQ-CODE-1", "CASE-1") + '\n' + tag("REQ-CODE-1") + '\n')
        members, ac, lv = R.scan_all(d, os.path.join(d, "requirements"))
        self.assertEqual(members, R.scan_members(d, os.path.join(d, "requirements")))
        self.assertEqual(ac, R.scan_ac_verifies(d, os.path.join(d, "requirements")))
        self.assertEqual(lv, R.scan_test_levels(d, os.path.join(d, "requirements")))
        self.assertNotIn("REQ-FAKE-999", ac)
        self.assertNotIn("REQ-FAKE-999", members)
        self.assertNotIn("REQ-DOC-1", ac)


class OneGitRunner(unittest.TestCase):  # tested-by: ARCH-GITRUN-067  # tested-by: REQ-GITRUN-993
    """Every git question goes through one runner, with one decoding rule and one
    fail-open contract. Eleven hand-written copies disagreed about both."""

    def test_a_failing_command_reads_as_no_answer(self):  # verifies: REQ-GITRUN-993#CASE-1  # verifies: ARCH-GITRUN-067#CASE-1
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        self.assertIsNone(R._git(["rev-parse", "--show-toplevel"], cwd=d, timeout=5))

    def test_a_missing_git_is_not_an_exception(self):  # verifies: REQ-GITRUN-993#CASE-2
        with mock.patch.object(R.subprocess, "run", side_effect=OSError("no git")):
            self.assertIsNone(R._git(["status"]))
        with mock.patch.object(R.subprocess, "run",
                               side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "bad")):
            self.assertIsNone(R._git(["status"]))

    def test_the_runner_pins_utf8_decoding(self):  # verifies: REQ-GITRUN-993#CASE-2
        seen = {}

        def fake(cmd, **kw):
            seen.update(kw)
            return mock.Mock(returncode=0, stdout="ok")

        with mock.patch.object(R.subprocess, "run", side_effect=fake):
            self.assertEqual(R._git(["status"]), "ok")
        self.assertEqual(seen.get("encoding"), "utf-8")
        self.assertTrue(seen.get("text"))
        self.assertNotIn("errors", seen)   # strict: a path git cannot encode reads as None

    def test_the_root_falls_back_to_the_directory_given(self):  # verifies: REQ-GITRUN-993#CASE-3  # verifies: ARCH-GITRUN-067#CASE-2
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        self.assertEqual(R._git_root(d), d)
        with mock.patch.object(R, "_git", return_value="  /repo/root \n"):
            self.assertEqual(R._git_root(d), "/repo/root")

    def test_the_remote_url_is_empty_when_git_cannot_say(self):
        with mock.patch.object(R, "_git", return_value=None):
            self.assertEqual(R._git_remote_url("."), "")
        with mock.patch.object(R, "_git", return_value="git@example.com:a/b.git\n"):
            self.assertEqual(R._git_remote_url("."), "git@example.com:a/b.git")

    def test_no_other_code_starts_a_git_process(self):  # verifies: REQ-GITRUN-993#CASE-4  # verifies: ARCH-GITRUN-067#CASE-3
        with io.open(R.__file__, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
        starts = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if (isinstance(f, ast.Attribute) and f.attr in ("run", "check_output", "Popen",
                                                            "call", "check_call")
                    and isinstance(f.value, ast.Name) and f.value.id == "subprocess"):
                starts.append(node.lineno)
        self.assertEqual(len(starts), 1, "subprocess started at lines {}".format(starts))
        runner = next(n for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef) and n.name == "_git")
        self.assertTrue(runner.lineno < starts[0] <= (runner.end_lineno or starts[0]))


class OneSectionReader(unittest.TestCase):  # tested-by: ARCH-SECTIONS-068  # tested-by: REQ-SECTIONS-994
    """Nine readers of a requirement body, one answer to where a section starts."""

    FENCED = ("# X\n\n"
              "## Notes\n"
              "Here is what a requirement looks like:\n\n"
              "```markdown\n"
              "## Description\n"
              "- a fenced example clause\n"
              "## Cases\n"
              "CASE-9 fake\n"
              "```\n\n"
              "## Cases\n"
              "CASE-1 real\n")

    def test_the_fence_is_checked_before_the_heading(self):  # verifies: REQ-SECTIONS-994#CASE-1  # verifies: ARCH-SECTIONS-068#CASE-1
        seen = [line.strip() for is_h, line in R._body_lines(self.FENCED) if is_h]
        self.assertEqual(seen, ["## Notes", "## Cases"])

    def test_every_reader_agrees_a_fenced_section_is_absent(self):  # verifies: REQ-SECTIONS-994#CASE-1  # verifies: ARCH-SECTIONS-068#CASE-1
        self.assertFalse(R._has_section(self.FENCED, "description"))
        self.assertEqual(R._bullets(self.FENCED, "description"), [])
        self.assertEqual(R._section(self.FENCED, "description"), "")
        self.assertEqual(R._contract_clauses(self.FENCED), [])
        self.assertEqual([f["check"] for f in R._lint_sections(self.FENCED)
                          if "Description" in f["detail"]], ["missing-section"])

    def test_a_fenced_example_is_not_part_of_the_contract(self):  # verifies: REQ-SECTIONS-994#CASE-5  # verifies: ARCH-SECTIONS-068#CASE-2
        with_fence = ("## Description\n- real clause\n\n"
                      "```markdown\n## Cases\nCASE-9 fake\n```\n\n"
                      "## Cases\nCASE-1 real\n")
        without = "## Description\n- real clause\n\n## Cases\nCASE-1 real\n"
        self.assertEqual(R.binding_hash(with_fence), R.binding_hash(without))

    def test_a_section_stops_at_the_next_heading(self):  # verifies: REQ-SECTIONS-994#CASE-2
        body = "## Description\n- one\n\n## Notes\n- two\n"
        self.assertEqual(list(R._section_lines(body, "description")), ["- one", ""])
        self.assertEqual(R._bullets(body, "description"), ["one"])

    def test_a_legacy_spelling_still_reads(self):  # verifies: REQ-SECTIONS-994#CASE-3
        body = "## WHAT — Contract (normative)\n- one\n\n## HOW — Acceptance\nAC-1 x\n"
        self.assertEqual([c for _n, c in R._contract_clauses(body)], ["one"])
        self.assertEqual([b["label"] for b in R._acc_blocks(body)], ["AC-1"])

    def test_raw_keeps_indentation_and_stripped_does_not(self):  # verifies: REQ-SECTIONS-994#CASE-4
        body = "## Cases\nCASE-1 — t\n  Given  a thing\n"
        self.assertEqual(list(R._section_lines(body, "cases", raw=True)),
                         ["CASE-1 — t", "  Given  a thing"])
        self.assertEqual(list(R._section_lines(body, "cases")),
                         ["CASE-1 — t", "Given  a thing"])

    def test_presence_and_readability_answer_to_the_same_fence(self):  # verifies: ARCH-SECTIONS-068#CASE-3
        """Over this repo's real corpus, not a fixture: the presence check and the
        section reader must agree on every block, in both directions."""
        rdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(R.__file__))),
                            "requirements")
        if not os.path.isdir(rdir):
            self.skipTest("not running inside the source repo")
        names = R.CONTRACT_LABELS + R.ACCEPTANCE_LABELS + ("context", "notes")
        blocks = 0
        for fn in sorted(os.listdir(rdir)):
            if not fn.endswith(".md") or fn.startswith("_"):
                continue
            with io.open(os.path.join(rdir, fn), encoding="utf-8") as f:
                text = f.read()
            for body in R.split_requirement_blocks(text):
                blocks += 1
                atomic = bool(R._atomic_spans(body))
                headings = list(R._section_headings(body))
                for name in names:
                    opened = any(R._heading_label_is(h, name) for h in headings)
                    present = R._has_section(body, name)
                    if atomic and name in R.CONTRACT_LABELS + R.ACCEPTANCE_LABELS:
                        continue          # the atomic form stands in for both by design
                    self.assertEqual(present, opened,
                                     "{}: {!r} present={} opened={}".format(fn, name, present, opened))
        self.assertGreater(blocks, 100, "the corpus should have been read")

    def test_only_the_first_matching_section_is_read(self):  # verifies: REQ-SECTIONS-994#CASE-2
        body = "## Description\n- first\n\n## Notes\nx\n\n## Description\n- second\n"
        self.assertEqual(R._bullets(body, "description"), ["first"])
