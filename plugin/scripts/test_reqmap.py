"""Regression tests for the bugs found by the 2026-06-02 bug-hunt. Stdlib only.

Run: python -m unittest test_reqmap   (from plugin/scripts/)
"""
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

    def test_scalar_and_list_fields_in_meta(self):  # verifies: CORE-PARSE-001#AC-1
        meta, _ = R.parse_frontmatter(
            "---\nid: REQ-A-001\nstatus: draft\ndepends_on: [X-Y-001, Z-W-002]\n---\nbody\n")
        self.assertEqual(meta["id"], "REQ-A-001")
        self.assertEqual(meta["status"], "draft")
        self.assertEqual(meta["depends_on"], ["X-Y-001", "Z-W-002"])

    def test_trailing_comment_stripped_from_value(self):  # verifies: CORE-PARSE-001#AC-2
        meta, _ = R.parse_frontmatter("---\nstatus: draft  # not enforced\n---\n")
        self.assertEqual(meta["status"], "draft")

    def test_no_frontmatter_block_yields_empty_meta(self):  # verifies: CORE-PARSE-001#AC-3
        meta, body = R.parse_frontmatter("# Title\njust text\n")
        self.assertEqual(meta, {})
        self.assertEqual(body, "# Title\njust text\n")

    def test_underscore_files_excluded(self):  # verifies: CORE-PARSE-001#AC-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_draft.md"), "---\nid: X-A-001\n---\n# T\n")
            _write(os.path.join(d, "REQ-A-001.md"), "---\nid: REQ-A-001\n---\n# T\n")
            reqs = R.load_requirements(d)
        self.assertEqual(list(reqs), ["REQ-A-001"])

    def test_block_list_and_unclosed_inline_list(self):  # verifies: CORE-PARSE-001#AC-5
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


class Gate(unittest.TestCase):
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, False, code_root=d)
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

    def test_corrupt_lock_does_not_crash(self):  # bug #6  tested-by: CORE-DRIFT-003  # verifies: CORE-DRIFT-003#AC-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_reqlock.json"), "")        # empty
            self.assertEqual(R.load_lock(d), {})
            _write(os.path.join(d, "_reqlock.json"), "{not json")  # garbage
            self.assertEqual(R.load_lock(d), {})
            with open(os.path.join(d, "_reqlock.json"), "wb") as f:
                f.write(b'{"A": "\xff\xfe\x80"}')               # non-UTF-8 / binary
            self.assertEqual(R.load_lock(d), {})                # must fail open, not crash
            _write(os.path.join(d, "_reqlock.json"), "[]")      # valid JSON, wrong type
            self.assertEqual(R.load_lock(d), {})                # non-dict must fail open too
            _write(os.path.join(d, "_reqlock.json"), "null")
            self.assertEqual(R.load_lock(d), {})

    def test_update_lock_missing_dir_no_crash(self):  # bug #13
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "does", "not", "exist")
            R.save_lock(missing, {"A": "b"})  # must not raise
            self.assertTrue(os.path.exists(os.path.join(missing, "_reqlock.json")))

    def test_save_then_load_roundtrip(self):  # verifies: CORE-DRIFT-003#AC-4
        with tempfile.TemporaryDirectory() as d:
            R.save_lock(d, {"A-B-001": "abc123def456", "C-D-002": "0123456789ab"})
            self.assertEqual(R.load_lock(d), {"A-B-001": "abc123def456", "C-D-002": "0123456789ab"})

    def test_binding_hash_tracks_contract_not_commentary(self):  # tested-by: CORE-DRIFT-003  # verifies: CORE-DRIFT-003#AC-1  # verifies: CORE-DRIFT-003#AC-2
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
        # a commentary heading that merely CONTAINS a normative keyword must NOT leak in
        trap = base + "\n## Notes — contract caveats\n- not normative.\n"
        self.assertEqual(R.binding_hash(base), R.binding_hash(trap))
        # ...and editing that non-normative section must not trip drift
        self.assertEqual(R.binding_hash(trap), R.binding_hash(trap.replace("not normative", "EDITED")))

    def test_dashless_normative_heading_is_hashed_and_detected(self):  # tested-by: CORE-DRIFT-003
        # `## WHAT Contract` (no em-dash) must be (a) detected as a Contract section by the
        # gate AND (b) folded into the drift hash — else a confirmed req passes the gate but
        # silently never drifts (empty hash). Regression guard for the heading-match gap.
        nodash = ("# T\n\n## WHAT Contract\n- shall do X\n\n"
                  "## HOW Acceptance\nAC-1\n  Then X holds\n")
        self.assertTrue(R._has_section(nodash, "contract"))
        self.assertTrue(R._has_section(nodash, "acceptan"))
        self.assertNotEqual(R.binding_hash(nodash), R.binding_hash(""))               # not the empty hash
        self.assertNotEqual(R.binding_hash(nodash),
                            R.binding_hash(nodash.replace("shall do X", "shall do Y")))  # tracks edits

    def test_has_section_anchored_to_label(self):  # tested-by: REQ-CHECK-006
        # a commentary heading that merely mentions the keyword is NOT the section
        self.assertFalse(R._has_section("# T\n\n## Notes — contract caveats\n- x\n", "contract"))
        # canonical, bare, and dash-less label forms all count
        for h in ("## WHAT — Contract (normative)", "## Contract", "## WHAT Contract"):
            self.assertTrue(R._has_section("# T\n\n" + h + "\n- x\n", "contract"), h)

    def test_drift_warn_names_member_locations(self):  # tested-by: REQ-CHECK-006  # verifies: REQ-CHECK-006#AC-4
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

    def test_confirmed_missing_contract_section_warns(self):  # tested-by: REQ-CHECK-006  # verifies: REQ-CHECK-006#AC-7
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

    def test_confirmed_missing_acceptance_section_warns(self):  # tested-by: REQ-CHECK-006  # verifies: REQ-CHECK-006#AC-8
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

    def test_confirmed_with_both_sections_no_section_lint_warn(self):  # tested-by: REQ-CHECK-006  # verifies: REQ-CHECK-006#AC-9
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

    def test_need_without_validation_warns_once_the_repo_opts_in(self):  # tested-by: REQ-VLEVEL-037 @unit
        # Two needs: one validated, one not. The repo has opted in (a validated-against
        # tag exists), so the unvalidated need warns and the validated one does not.
        files = {
            "NEED-A-001.md": REQ.format(id="NEED-A-001", status="confirmed", layer="need",
                                        extra="", title="Validated need"),
            "NEED-B-002.md": REQ.format(id="NEED-B-002", status="confirmed", layer="need",
                                        extra="", title="Unvalidated need"),
            "t_probe.py": "# validated-against: NEED-A-001\ndef test_x():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertIn("NEED-B-002", out)
        self.assertIn("validated-against", out)

    def test_need_without_validation_is_silent_until_the_repo_opts_in(self):  # tested-by: REQ-VLEVEL-037 @unit
        # No validated-against tag anywhere: the rule must not fire at all, so a repo
        # that never adopts the role sees no new warnings.
        files = {
            "NEED-B-002.md": REQ.format(id="NEED-B-002", status="confirmed", layer="need",
                                        extra="", title="Unvalidated need"),
        }
        _, out = self._check(files)
        self.assertNotIn("validated-against", out)

    def test_bus_verified_only_at_system_level_warns(self):  # tested-by: REQ-VLEVEL-037 @unit
        files = {
            "CORE-X-001.md": REQ.format(id="CORE-X-001", status="confirmed", layer="bus",
                                        extra="", title="Foundation"),
            "impl.py": "# implements: CORE-X-001\ndef go():\n    return 1\n",
            "t_sys.py": "# tested-by: CORE-X-001 @system\ndef test_e2e():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertIn("@system", out)

    def test_bus_with_a_lower_level_link_is_silent(self):  # tested-by: REQ-VLEVEL-037 @unit
        files = {
            "CORE-X-001.md": REQ.format(id="CORE-X-001", status="confirmed", layer="bus",
                                        extra="", title="Foundation"),
            "impl.py": "# implements: CORE-X-001\ndef go():\n    return 1\n",
            "t_sys.py": "# tested-by: CORE-X-001 @system\ndef test_e2e():\n    pass\n",
            "t_unit.py": "# tested-by: CORE-X-001 @unit\ndef test_unit():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertNotIn("verified only at @system", out)

    def test_bus_with_no_levelled_link_is_never_judged(self):  # tested-by: REQ-VLEVEL-037 @unit
        # opt-in per requirement: an unlevelled tested-by link is not evidence either way
        files = {
            "CORE-X-001.md": REQ.format(id="CORE-X-001", status="confirmed", layer="bus",
                                        extra="", title="Foundation"),
            "impl.py": "# implements: CORE-X-001\ndef go():\n    return 1\n",
            "t_plain.py": "# tested-by: CORE-X-001\ndef test_x():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertNotIn("verified only at @system", out)

    def test_feature_verified_only_at_system_level_is_silent(self):  # tested-by: REQ-VLEVEL-037 @unit
        # rule 2 is about foundation code only — a feature may legitimately be end-to-end
        files = {
            "REQ-X-001.md": REQ.format(id="REQ-X-001", status="confirmed", layer="feature",
                                       extra="", title="Feature"),
            "impl.py": "# implements: REQ-X-001\ndef go():\n    return 1\n",
            "t_sys.py": "# tested-by: REQ-X-001 @system\ndef test_e2e():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertNotIn("verified only at @system", out)


class Scanning(unittest.TestCase):  # tested-by: CORE-SCAN-002
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

    def test_tag_re_left_boundary(self):  # bug #3
        self.assertEqual(R.TAG_RE.findall(tag("FOO-BAR-001")), [("implements", "FOO-BAR-001")])
        self.assertEqual(R.TAG_RE.findall("# re" + _ROLE + ": FOO-BAR-001"), [])
        self.assertEqual(R.TAG_RE.findall("auto-" + _ROLE + ": AB-CD-001"), [])

    def test_only_ssot_requirements_dir_excluded(self):  # bug #4  # verifies: CORE-SCAN-002#AC-3
        with tempfile.TemporaryDirectory() as d:
            ssot = os.path.join(d, "requirements")
            _write(os.path.join(d, "src", "requirements", "mod.py"), tag("SRC-REQ-001") + "\n")
            _write(os.path.join(ssot, "ignored.py"), tag("SSOT-IGN-001") + "\n")
            members = R.scan_members(d, ssot)
            self.assertIn("SRC-REQ-001", members)       # non-SSOT requirements/ still scanned
            self.assertNotIn("SSOT-IGN-001", members)    # the real SSOT dir is skipped

    def test_duplicate_tag_on_one_line_deduped(self):  # bug #18  # verifies: CORE-SCAN-002#AC-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), tag("FOO-BAR-001") + " " + _ROLE + ": FOO-BAR-001\n")
            members = R.scan_members(d, None)
            self.assertEqual(len(members["FOO-BAR-001"]), 1)

    def test_member_paths_are_posix(self):  # bug #17  # verifies: CORE-SCAN-002#AC-4
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

    def test_implements_tag_yields_member(self):  # verifies: CORE-SCAN-002#AC-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), tag("REQ-T-001") + "\n")
            members = R.scan_members(d, None)
        self.assertEqual(members["REQ-T-001"], [("implements", "a.py", 1)])

    def test_all_roles_recognized_unknown_ignored(self):  # verifies: CORE-SCAN-002#AC-2
        # roles built at runtime so THIS .py source registers no phantom member
        roles = [_ROLE, _TB_ROLE, "generated" + "-from", "validated" + "-against", "refines"]
        src = "".join("# {}: REQ-T-001\n".format(r) for r in roles)
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), src)
            members = R.scan_members(d, None)
        found = sorted(r for (r, _f, _l) in members["REQ-T-001"])
        self.assertEqual(found, ["generated-from", "implements", "tested-by", "validated-against"])

    def test_generated_from_accepts_multiple_ids(self):  # verifies: CORE-SCAN-002#AC-6
        # one whole-system doc generated from several requirements → a member of
        # each, so a contract drift on ANY of them lists the doc as needing re-sync.
        # List built at runtime so THIS .py source registers no phantom member.
        line = "<!-- {}-from: {}, {} -->\n".format("generated", "REQ-MA-001", "REQ-MB-002")
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), line)
            members = R.scan_members(d, None)
        self.assertEqual(members.get("REQ-MA-001"), [("generated-from", "docs/arch.html", 1)])
        self.assertEqual(members.get("REQ-MB-002"), [("generated-from", "docs/arch.html", 1)])

    def test_multi_id_dedup_and_single_id_unchanged(self):  # verifies: CORE-SCAN-002#AC-6
        # a repeated id in one list is recorded once; a plain single-id tag is unaffected.
        multi = "# {}: {}, {}\n".format(_ROLE, "REQ-MC-001", "REQ-MC-001")
        single = tag("REQ-MD-001") + "\n"
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), multi + single)
            members = R.scan_members(d, None)
        self.assertEqual(members.get("REQ-MC-001"), [("implements", "a.py", 1)])
        self.assertEqual(members.get("REQ-MD-001"), [("implements", "a.py", 2)])

    def test_unreadable_file_skipped(self):  # verifies: CORE-SCAN-002#AC-5
        # _scan_file_tags fails open (None) on a read error; scan_members skips the file
        self.assertIsNone(R._scan_file_tags(os.path.join("no", "such", "dir", "x.py")))

    def test_scan_test_levels_collects_levels_per_requirement(self):  # tested-by: REQ-VLEVEL-037 @unit
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "t_one.py"), "w", encoding="utf-8") as f:
                f.write("# tested-by: REQ-A-001 @unit\n"
                        "# tested-by: REQ-A-001 @system\n"
                        "# tested-by: REQ-B-002 @integration\n")
            got = R.scan_test_levels(d)
            self.assertEqual(set(got["REQ-A-001"]), {"unit", "system"})
            self.assertEqual(set(got["REQ-B-002"]), {"integration"})
            self.assertEqual(got["REQ-B-002"]["integration"], [("t_one.py", 3)])

    def test_scan_test_levels_expands_an_id_list_and_ignores_unlevelled(self):  # tested-by: REQ-VLEVEL-037 @unit
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

    def test_scan_test_levels_ignores_a_tag_inside_a_python_string(self):  # tested-by: REQ-VLEVEL-037 @unit
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

    def test_scan_test_levels_ignores_a_backticked_example(self):  # tested-by: REQ-VLEVEL-037 @unit
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

    def test_levelled_tag_still_resolves_as_a_plain_member(self):  # tested-by: REQ-VLEVEL-037 @unit
        # backwards compatibility: the suffix must not disturb ordinary tag parsing
        self.assertEqual(R._findall_tags("# tested-by: REQ-A-001 @unit"),
                         [("tested-by", "REQ-A-001")])


class RepoRootScan(unittest.TestCase):  # tested-by: CORE-SCAN-002
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


class DocBundle(unittest.TestCase):  # tested-by: REQ-DOCBUNDLE-026
    """A large docs/ HTML doc with no generated-from lineage is the doc-sync blind
    spot — it drifts from the requirements it derives from with nothing linking them."""
    def _big(self, n=None):
        return "<html>" + "x" * (R.DOC_BUNDLE_MIN_BYTES + 10 if n is None else n) + "</html>"

    # generated-from comment built at runtime so THIS .py source registers no phantom member
    def _gtag(self, cap):
        return "<!-- {}-from: {} -->\n".format("generated", cap)

    def test_large_untagged_docs_html_is_flagged(self):  # verifies: REQ-DOCBUNDLE-026#AC-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), self._big())
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), ["docs/arch.html"])

    def test_small_docs_html_not_flagged(self):  # verifies: REQ-DOCBUNDLE-026#AC-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "small.html"), "<html>tiny</html>")
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_tagged_large_docs_html_not_flagged(self):  # verifies: REQ-DOCBUNDLE-026#AC-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), self._gtag("REQ-DOC-001") + self._big())
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_engine_outputs_and_nondocs_excluded(self):  # verifies: REQ-DOCBUNDLE-026#AC-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "map.html"), self._big())   # engine's published viewer
            _write(os.path.join(d, "docs", "_x.html"), self._big())    # _-prefixed generated output
            _write(os.path.join(d, "top.html"), self._big())           # not under docs/
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_reqmapignore_suppresses(self):  # verifies: REQ-DOCBUNDLE-026#AC-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "poster.html"), self._big())
            _write(os.path.join(d, ".reqmapignore"), "docs/poster.html\n")
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_gate_surfaces_the_warn(self):  # verifies: REQ-DOCBUNDLE-026#AC-6
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), self._big())
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, d, False, code_root=d)
            self.assertIn("docs/arch.html", buf.getvalue())
            self.assertIn("generated-from", buf.getvalue())


class MemberDrift(unittest.TestCase):  # tested-by: REQ-MEMBERDRIFT-027
    """Reverse-direction drift: a dedicated member (code/doc) changed while the
    confirmed requirement's own contract stayed put — behaviour shipped, spec stale.
    Scoped to mono-requirement files so a shared engine file is not blamed for all."""
    def _req(self, d, rid="REQ-MD-001", status="confirmed"):
        _write(os.path.join(d, rid + ".md"),
               "---\nid: {}\nstatus: {}\nlayer: feature\nowner: Alex\n---\n\n"
               "# T\n## WHAT — Contract (normative)\n- it shall foo\n".format(rid, status))

    def _member(self, d, body, rid="REQ-MD-001", rel="src/foo.py"):
        _write(os.path.join(d, *rel.split("/")), tag(rid) + "\n" + body + "\n")

    def _state(self, d):
        reqs = R.load_requirements(d)
        members = R.scan_members(d, d)
        lock = {rid: R.binding_hash(r["body"]) for rid, r in reqs.items()}
        return reqs, members, lock

    def test_only_mono_requirement_files_recorded(self):  # verifies: REQ-MEMBERDRIFT-027#AC-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "solo.py"), tag("REQ-AA-001") + "\n")
            _write(os.path.join(d, "shared.py"), tag("REQ-BB-001") + "\n" + tag("REQ-CC-001") + "\n")
            mh = R.compute_member_hashes(d, R.scan_members(d, d))
            self.assertIn("solo.py", mh.get("REQ-AA-001", {}))
            self.assertNotIn("REQ-BB-001", mh)   # shared.py belongs to two requirements
            self.assertNotIn("REQ-CC-001", mh)

    def test_file_sha_normalizes_line_endings(self):  # CRLF (Windows) == LF (CI)  # verifies: REQ-MEMBERDRIFT-027#AC-8
        with tempfile.TemporaryDirectory() as d:
            lf = os.path.join(d, "lf.py")
            crlf = os.path.join(d, "crlf.py")
            with open(lf, "wb") as f:
                f.write(b"def run():\n    return 0\n")
            with open(crlf, "wb") as f:
                f.write(b"def run():\r\n    return 0\r\n")
            self.assertEqual(R._file_sha(lf), R._file_sha(crlf))

    def test_memberlock_roundtrip_and_failopen(self):  # verifies: REQ-MEMBERDRIFT-027#AC-2
        with tempfile.TemporaryDirectory() as d:
            R.save_memberlock(d, {"REQ-AA-001": {"solo.py": "abc"}})
            self.assertEqual(R.load_memberlock(d), {"REQ-AA-001": {"solo.py": "abc"}})
            _write(os.path.join(d, "_memberlock.json"),
                   json.dumps({"_schema": 999, "members": {"X": {}}}))   # newer schema → degrade
            self.assertEqual(R.load_memberlock(d), {})
            _write(os.path.join(d, "_memberlock.json"), "{ broken")
            self.assertEqual(R.load_memberlock(d), {})

    def test_changed_member_unchanged_contract_is_flagged(self):  # verifies: REQ-MEMBERDRIFT-027#AC-3
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            memberlock = R.compute_member_hashes(d, members)
            self._member(d, "CHANGED = 2")     # edit the member, leave the requirement alone
            self.assertEqual(R.member_drift(reqs, members, lock, memberlock, d),
                             [("REQ-MD-001", "src/foo.py")])

    def test_contract_also_changed_not_flagged(self):  # verifies: REQ-MEMBERDRIFT-027#AC-4
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            memberlock = R.compute_member_hashes(d, members)
            self._member(d, "CHANGED = 2")
            lock = {"REQ-MD-001": "stale-hash"}   # contract drifted too → forward drift owns it
            self.assertEqual(R.member_drift(reqs, members, lock, memberlock, d), [])

    def test_non_confirmed_not_flagged(self):  # verifies: REQ-MEMBERDRIFT-027#AC-5
        with tempfile.TemporaryDirectory() as d:
            self._req(d, status="baseline"); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            memberlock = R.compute_member_hashes(d, members)
            self._member(d, "CHANGED = 2")
            self.assertEqual(R.member_drift(reqs, members, lock, memberlock, d), [])

    def test_new_member_without_baseline_not_flagged(self):  # verifies: REQ-MEMBERDRIFT-027#AC-6
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            self._member(d, "CHANGED = 2")
            self.assertEqual(R.member_drift(reqs, members, lock, {}, d), [])   # no baseline yet

    def test_gate_warns_and_strict_promotes(self):  # verifies: REQ-MEMBERDRIFT-027#AC-7
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs = R.load_requirements(d); members = R.scan_members(d, d)
            R.cmd_check(reqs, members, d, True, code_root=d)   # baseline both locks
            self._member(d, "CHANGED = 2")
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, False, code_root=d)
            self.assertIn("MEMBER DRIFT", buf.getvalue())
            self.assertEqual(code, 0)                          # warn-only by default
            with redirect_stdout(io.StringIO()):
                strict_code = R.cmd_check(reqs, members, d, False, code_root=d, strict=True)
            self.assertEqual(strict_code, 1)                   # --strict-promotable


_BIG_PY = "".join("x{0} = {0}\n".format(i) for i in range(200))   # >= ORPHAN_CODE_MIN_LOC lines


class OrphanCode(unittest.TestCase):  # tested-by: REQ-ORPHANCODE-034
    def test_large_untagged_program_file_reported(self):  # verifies: REQ-ORPHANCODE-034#AC-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "mod.py"), _BIG_PY)
            self.assertEqual(R.orphan_code_files(d, set()), ["mod.py"])

    def test_small_untagged_not_reported(self):  # verifies: REQ-ORPHANCODE-034#AC-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "mod.py"), "x = 1\ny = 2\n")
            self.assertEqual(R.orphan_code_files(d, set()), [])

    def test_covered_file_not_reported(self):  # verifies: REQ-ORPHANCODE-034#AC-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "mod.py"), _BIG_PY)
            self.assertEqual(R.orphan_code_files(d, {"mod.py"}), [])

    def test_non_program_ext_not_reported(self):  # verifies: REQ-ORPHANCODE-034#AC-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "big.txt.md"), _BIG_PY)
            _write(os.path.join(d, "big.html"), _BIG_PY)
            self.assertEqual(R.orphan_code_files(d, set()), [])

    def test_reqmapignore_suppresses(self):  # verifies: REQ-ORPHANCODE-034#AC-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "vendor", "big.py"), _BIG_PY)
            _write(os.path.join(d, ".reqmapignore"), "vendor/*\n")
            self.assertEqual(R.orphan_code_files(d, set()), [])

    def test_gate_warns_and_exit_unchanged_even_strict(self):  # verifies: REQ-ORPHANCODE-034#AC-6
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"), REQ.format(
                id="A-FOO-001", status="baseline", layer="feature", extra="", title="T"))
            _write(os.path.join(d, "orphan.py"), _BIG_PY)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, False, code_root=d)
            self.assertIn("orphan.py", buf.getvalue())
            self.assertIn("no membership tag", buf.getvalue())
            self.assertEqual(code, 0)
            with redirect_stdout(io.StringIO()):   # never strict-promoted (advisory ceiling)
                strict_code = R.cmd_check(reqs, members, d, False, code_root=d, strict=True)
            self.assertEqual(strict_code, 0)

    def test_verifies_tag_counts_as_covered_at_gate(self):  # verifies: REQ-ORPHANCODE-034#AC-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"), REQ.format(
                id="A-FOO-001", status="baseline", layer="feature", extra="", title="T"))
            # runtime-built so THIS test file registers no phantom AC coverage
            vtag = "# {}: A-FOO-001#AC-1\n".format("veri" + "fies")
            _write(os.path.join(d, "test_mod.py"), vtag + _BIG_PY)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, d, False, code_root=d)
            self.assertNotIn("test_mod.py", buf.getvalue())


class DriftDependents(unittest.TestCase):  # tested-by: REQ-DRIFTIMPACT-035
    _CONTRACT = "\n## Contract\n- x\n## Acceptance\n- y\n"

    def _gate(self, d, dep_ids):
        _write(os.path.join(d, "AREA-FOO-001.md"),
               REQ.format(id="AREA-FOO-001", status="confirmed", layer="bus",
                          extra="", title="Foo") + self._CONTRACT)
        for dep in dep_ids:
            _write(os.path.join(d, dep + ".md"),
                   REQ.format(id=dep, status="baseline", layer="feature",
                              extra="depends_on: [AREA-FOO-001]\n", title=dep))
        _write(os.path.join(d, "mod.py"), tag("AREA-FOO-001") + "\n")
        _write(os.path.join(d, "_reqlock.json"), '{"AREA-FOO-001": "stalehash0000"}')
        reqs = R.load_requirements(d)
        members = R.scan_members(d, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_check(reqs, members, d, False, code_root=d)
        return buf.getvalue()

    def test_dependent_named_on_drift(self):  # verifies: REQ-DRIFTIMPACT-035#AC-1
        with tempfile.TemporaryDirectory() as d:
            out = self._gate(d, ["AREA-BAR-002"])
            self.assertIn("DRIFT", out)
            self.assertIn("review dependent(s): AREA-BAR-002", out)

    def test_no_dependents_no_clause(self):  # verifies: REQ-DRIFTIMPACT-035#AC-2
        with tempfile.TemporaryDirectory() as d:
            out = self._gate(d, [])
            self.assertIn("DRIFT", out)
            self.assertNotIn("review dependent", out)

    def test_two_dependents_sorted(self):  # verifies: REQ-DRIFTIMPACT-035#AC-3
        with tempfile.TemporaryDirectory() as d:
            out = self._gate(d, ["AREA-BAZ-003", "AREA-BAR-002"])   # written unsorted
            self.assertIn("review dependent(s): AREA-BAR-002, AREA-BAZ-003", out)


class ProseClassification(unittest.TestCase):  # tested-by: REQ-PROSE-024
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


class ProseFacts(unittest.TestCase):  # tested-by: REQ-PROSE-024
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


class ProseExtract(unittest.TestCase):  # tested-by: REQ-PROSE-024
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


class RiderGuards(unittest.TestCase):  # tested-by: REQ-EXTRACT-008  # tested-by: REQ-PROSE-024
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

    def test_extract_drafts_go_and_rust(self):  # bug: draft-narrow-extension-set
        # draft/init must cover the same code extensions the scanner does, not just 5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "server.go"), "package main\n")
            _write(os.path.join(d, "lib.rs"), "fn main() {}\n")
            reqs_dir = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract({}, {}, d, reqs_dir)
            made = sorted(n for n in os.listdir(reqs_dir) if n.startswith("DRAFT-"))
            self.assertIn("DRAFT-SERVER.md", made)
            self.assertIn("DRAFT-LIB.md", made)

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

    def test_drafted_contract_carries_the_binding_line_and_no_shall(self):
        with tempfile.TemporaryDirectory() as d:
            code_root = os.path.join(d, "src")
            os.makedirs(code_root)
            with open(os.path.join(code_root, "widget.py"), "w", encoding="utf-8") as f:
                f.write("def go():\n    return 1\n")
            reqs_dir = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_extract({}, {}, code_root, reqs_dir)
            written = [p for p in os.listdir(reqs_dir) if p.endswith(".md")]
            self.assertEqual(len(written), 1)
            with open(os.path.join(reqs_dir, written[0]), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("Every line in this section is binding.", text)
            self.assertNotIn("shall", text.lower())


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

    def test_template_uses_the_plain_present_voice(self):
        t = R.REQUIREMENT_TEMPLATE
        self.assertIn("Every line in this section is binding.", t)
        # No CLAUSE may use a modal — but the guidance comment must stay free to name
        # 'shall' as the thing not to write, which is the clearest way to say it.
        # Comments are stripped whole: _lint_prose yields each line of a multi-line
        # comment separately, so filtering on a leading '<!--' would only drop the first.
        clauses = R._lint_prose(re.sub(r"<!--.*?-->", "", t, flags=re.DOTALL), "contract")
        self.assertTrue(clauses)                       # guard: the section actually parsed
        for ln in clauses:
            self.assertNotIn("shall", ln.lower())
            self.assertNotIn("must", ln.lower())

    def test_template_contract_body_passes_its_own_linter(self):
        # the shipped template must not be flagged by the checks it teaches
        req = {"meta": {"status": "confirmed"}, "body": R.REQUIREMENT_TEMPLATE.split("---\n", 2)[-1]}
        checks = {f["check"] for f in R.lint_requirement("AREA-NAME-001", req)}
        self.assertNotIn("anonymous-subject", checks)
        self.assertNotIn("long-sentence", checks)


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

    def test_export_includes_parsed_todos(self):  # bug: export-drops-todos
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            _write(os.path.join(d, "TODO.md"), "## v1.14\n- [ ] Ship it | lane: feature\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_export(R.load_requirements(rd), {}, rd, root=d)
            doc = json.loads(open(os.path.join(rd, "_map.json"), encoding="utf-8").read())
            self.assertEqual([t["name"] for t in doc["todos"]], ["Ship it"])

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


class ViewerInject(unittest.TestCase):  # tested-by: REQ-VIEWER-007
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


class DocsPublish(unittest.TestCase):  # tested-by: REQ-PAGES-021
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

    def test_engine_version_at_finds_real_engine(self):  # bug: staleness-probe-4k-truncation
        # The probe must parse the REAL engine file, not just synthetic fixtures:
        # a bounded read() went stale the day the file header outgrew the bound.
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
        self.assertEqual(R._engine_version_at(p), R.MAP_ENGINE_VERSION)

    def test_engine_version_at_ignores_docstring_mention(self):  # bug: staleness-probe-4k-truncation
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "reqmap.py")
            _write(p, '"""doc says MAP_ENGINE_VERSION = "1999-01-01" as an example"""\n'
                      'MAP_ENGINE_VERSION = "2099-12-31"\n')
            self.assertEqual(R._engine_version_at(p), "2099-12-31")

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
                code = R.cmd_check(reqs, members, d, False, code_root=d)
            return code, buf.getvalue()

    def test_invalid_status_errors_and_exits_nonzero(self):  # bug: gate-never-asserted-to-fail  # verifies: REQ-CHECK-006#AC-3
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="bogus", layer="feature", extra="", title="T")})
        self.assertIn("invalid status", out)
        self.assertEqual(code, 1)

    def test_invalid_layer_errors(self):  # verifies: REQ-CHECK-006#AC-3
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="bogus", extra="", title="T")})
        self.assertIn("invalid layer", out)
        self.assertEqual(code, 1)

    def test_depends_on_missing_errors(self):  # verifies: REQ-CHECK-006#AC-3
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="feature",
            extra="depends_on: [GHOST-X-999]\n", title="T")})
        self.assertIn("depends_on missing GHOST-X-999", out)
        self.assertEqual(code, 1)

    def test_dangling_tag_errors(self):  # verifies: REQ-CHECK-006#AC-1
        code, out = self._check({"mod.py": tag("GHOST-CAP-001") + "\n"})
        self.assertIn("dangling tag", out)
        self.assertEqual(code, 1)

    def test_confirmed_without_implements_errors(self):  # verifies: REQ-CHECK-006#AC-2
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="confirmed", layer="bus", extra="", title="T")})
        self.assertIn("no implements", out)
        self.assertEqual(code, 1)

    def test_test_exempt_suppresses_test_warn(self):  # verifies: REQ-CHECK-006#AC-10
        code, out = self._check({
            "A-FOO-001.md": REQ.format(id="A-FOO-001", status="confirmed", layer="bus",
                                       extra="test_exempt: covered by manual QA\n", title="T"),
            "mod.py": tag("A-FOO-001") + "\n"})
        self.assertNotIn("tested-by", out)
        self.assertEqual(code, 0)

    def test_untracked_lock_flagged_then_cleared(self):  # uncommitted-lock gap  # verifies: REQ-CHECK-006#AC-13
        import subprocess as _sp
        with tempfile.TemporaryDirectory() as d:
            reqs_dir = os.path.join(d, "requirements")
            os.makedirs(reqs_dir)
            R.save_lock(reqs_dir, {"REQ-A-001": "abc"})
            # not a git work tree yet -> fail open, no false positive
            self.assertEqual([], R.untracked_locks(reqs_dir))
            for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
                _sp.run(["git", "-C", d, *args], check=True, capture_output=True)
            # lock on disk but untracked -> flagged
            self.assertTrue(any("_reqlock.json" in p for p in R.untracked_locks(reqs_dir)))
            # once tracked -> cleared
            _sp.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
            self.assertEqual([], R.untracked_locks(reqs_dir))

    def test_update_lock_writes_hashes(self):  # verifies: REQ-CHECK-006#AC-12
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   REQ.format(id="A-FOO-001", status="baseline", layer="bus", extra="", title="T"))
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, R.scan_members(d, d), d, True)
            self.assertIn("A-FOO-001", R.load_lock(d))

    def test_corrupt_lock_warns_in_check(self):  # bug: corrupt-lock-disables-drift-silently  # verifies: REQ-CHECK-006#AC-5
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

    def test_inline_list_preserves_embedded_hash(self):  # bug: clean-item-eats-embedded-hash
        meta, _ = R.parse_frontmatter("---\ntags: [issue#1, fix]\n---\nbody")
        self.assertEqual(meta["tags"], ["issue#1", "fix"])

    def test_inline_list_still_strips_trailing_comment(self):
        meta, _ = R.parse_frontmatter("---\ntags: [a, b]  # trailing\n---\nbody")
        self.assertEqual(meta["tags"], ["a", "b"])

    def test_block_list_preserves_embedded_hash(self):
        meta, _ = R.parse_frontmatter("---\ntags:\n  - issue#123\n  - clean\n---\nbody")
        self.assertEqual(meta["tags"], ["issue#123", "clean"])


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

    def test_first_quote_single_line(self):
        self.assertEqual(R._first_quote("# T\n\n> one line why.\n\n## WHAT — Contract\n- x."),
                         "one line why.")

    def test_first_quote_gathers_multiline_why(self):
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

    def test_same_stem_files_mint_distinct_ids(self):  # bug: mint-cap-id-collision
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


class HealthLine(unittest.TestCase):  # tested-by: REQ-CHECK-006
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, False, code_root=d)
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

    def test_legacy_schema_is_flagged_nonblocking(self):  # verifies: REQ-CHECK-006#AC-11
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

    def test_bullets_folds_multiline_continuation(self):  # a wrapped clause must not be truncated to its first line
        body = ("# T\n\n## WHAT — Contract\n"
                "- It shall do the first thing across\n"
                "  a wrapped second line and\n"
                "  a third line.\n"
                "- A short clause.\n")
        self.assertEqual(
            R._bullets(body, "contract"),
            ["It shall do the first thing across a wrapped second line and a third line.",
             "A short clause."])

    def test_bullets_skips_clause_group_labels(self):  # voice rule 6: **What it creates**
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

    def test_bullets_keeps_wrapped_clause_bounded_by_bold_spans(self):
        clause = " ".join(R._bullets(self._WRAPPED_BOLD_BOTH_ENDS, "contract"))
        self.assertIn("containment", clause)     # the half that used to vanish
        self.assertIn("sanity", clause)
        self.assertIn("h4_bar_time + 4h", clause)

    def test_bullets_folds_indented_line_that_is_entirely_bold(self):
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
                R.cmd_map(reqs, members, rd, d)   # isolated root: never the real repo docs/
            md = open(os.path.join(rd, "_map.md"), encoding="utf-8").read()
            self.assertIn("untested", md)
            self.assertIn("unverified-intent", md)


class MapFreshness(unittest.TestCase):  # tested-by: REQ-MAP-007
    # tested-by: REQ-PAGES-021  (the docs/map.html freshness cases below)
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

    # ---- docs/map.html (GitHub Pages copy) freshness --------------------------
    def test_fresh_docs_map_passes_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            _write(os.path.join(d, "docs", ".nojekyll"), "")  # Pages signal
            self._map(d)                              # writes docs/map.html too
            self.assertTrue(os.path.exists(os.path.join(d, "docs", "map.html")))
            code, out = self._map(d, check=True)
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)

    def test_stale_docs_map_fails_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            _write(os.path.join(d, "docs", ".nojekyll"), "")
            self._map(d)                              # generate everything fresh
            _write(os.path.join(d, "docs", "map.html"), "<html>stale</html>")
            code, out = self._map(d, check=True)      # only the docs copy drifted
            self.assertEqual(code, 1)
            self.assertIn("map.html", out)

    def test_absent_docs_map_is_not_stale(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            _write(os.path.join(d, "docs", ".nojekyll"), "")  # signal present
            self._map(d)
            os.remove(os.path.join(d, "docs", "map.html"))    # but copy never kept
            code, out = self._map(d, check=True)
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)

    def test_no_pages_signal_skips_docs_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            self._map(d)                              # no docs/ dir at all
            code, out = self._map(d, check=True)
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)

    def test_docs_map_repo_field_change_is_not_stale(self):
        # the git-derived repo field differs across forks/clones; like _map.json,
        # it must be excluded from the docs/map.html freshness diff
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            _write(os.path.join(d, "docs", ".nojekyll"), "")
            self._map(d)
            docs = os.path.join(d, "docs", "map.html")
            html = open(docs, encoding="utf-8").read()
            # replace whatever repo value the build produced with a different slug
            i = html.index('"repo": "')
            j = html.index('"', i + len('"repo": "'))
            swapped = html[:i] + '"repo": "somefork/clone"' + html[j + 1:]
            self.assertNotEqual(swapped, html)        # the substitution actually fired
            _write(docs, swapped)
            code, out = self._map(d, check=True)      # only repo changed -> still fresh
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)


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

    def test_priority_orders_within_bucket(self):
        # both untested-confirmed → same 'Needs tests' bucket. The must-have id sorts
        # AFTER the should-have id alphabetically, so only priority can put it first.
        reqs = {"AAA-LOW-001": self._req("confirmed", extra="priority: should-have"),
                "ZZZ-HIGH-002": self._req("confirmed", extra="priority: must-have")}
        members = {rid: [("implements", "x.py", 1)] for rid in reqs}  # untested
        _, out = self._next(reqs, members)
        self.assertLess(out.index("ZZZ-HIGH-002"), out.index("AAA-LOW-001"))

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


class StripLineTag(unittest.TestCase):  # tested-by: REQ-INIT-012
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


def _kv(extra):
    """Parse the 'key: value' frontmatter lines a test passes as `extra` into meta,
    so Next can build requirement dicts the same way the REQ template does."""
    for line in extra.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta, _ = R.parse_frontmatter("---\n{}: {}\n---\n".format(k.strip(), v.strip()))
        yield k.strip(), meta.get(k.strip())


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


class PyFacts(unittest.TestCase):  # tested-by: REQ-CANDIDATES-009
    def test_nul_byte_source_yields_empty_facts(self):
        """A source with an embedded NUL byte makes ast.parse raise ValueError (not
        SyntaxError); _py_facts must swallow it and yield empty facts (#8)."""
        facts = R._py_facts("x = 1\x00\ny = 2\n")
        self.assertEqual(facts, {"signatures": [], "docstrings": {}, "imports": []})

    def test_syntax_error_yields_empty_facts(self):
        self.assertEqual(R._py_facts("def ("),
                         {"signatures": [], "docstrings": {}, "imports": []})


class CountAc(unittest.TestCase):  # tested-by: REQ-LINTCHECKS-025
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


class Lint(unittest.TestCase):  # tested-by: REQ-LINT-014  # tested-by: REQ-LINTCHECKS-025
    CONTRACT = "## WHAT — Contract (normative)"
    ACCEPT = "## HOW — Acceptance (= tests)"

    def _lint(self, reqs, strict=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_lint(reqs, strict)
        return code, buf.getvalue()

    def _req(self, status, body):
        return {"meta": {"status": status}, "body": body}

    def _body(self, contract="- ok.\n", acceptance="- ok.\n"):
        return "# T\n\n{}\n{}\n{}\n{}\n".format(self.CONTRACT, contract, self.ACCEPT, acceptance)

    def test_missing_acceptance_section_is_error(self):
        body = "# T\n\n{}\n- the contract.\n".format(self.CONTRACT)  # no acceptance heading
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertIn(("error", "missing-section"),
                      [(f["severity"], f["check"]) for f in fs])

    def test_over_scoped_fires_only_on_both_ceilings(self):  # composite cohesion signal
        big_contract = "".join("- clause {}.\n".format(i) for i in range(R.LINT_CONTRACT_MAX + 1))
        big_ac = "".join("- AC {}.\n".format(i) for i in range(R.LINT_AC_MAX + 1))
        small_ac = "".join("- AC {}.\n".format(i) for i in range(3))
        over = R.lint_requirement("REQ-BIG-001", self._req("confirmed", self._body(big_contract, big_ac)))
        self.assertIn("over-scoped", [f["check"] for f in over])             # both ceilings => fires
        one = R.lint_requirement("REQ-OK-001", self._req("confirmed", self._body(big_contract, small_ac)))
        self.assertNotIn("over-scoped", [f["check"] for f in one])           # only one ceiling => silent

    def test_over_scoped_counts_groups_not_clauses(self):
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

    def test_empty_section_flags_contentless_heading(self):
        empty = "# T\n\n{}\n{}\n".format(self.CONTRACT, self.ACCEPT)         # both headings, no content
        fs = R.lint_requirement("REQ-E-001", self._req("confirmed", empty))
        self.assertIn("empty-section", [f["check"] for f in fs])
        self.assertNotIn("empty-section",                                    # content present => silent
                         [f["check"] for f in R.lint_requirement("REQ-F-001", self._req("confirmed", self._body()))])

    def test_file_spread_warns_across_many_files(self):  # senate-driven; validates the positive branch via a synthetic multi-file fixture
        r = self._req("confirmed", self._body())
        spread = [("implements", "a.py", 1), ("implements", "b.py", 2), ("implements", "c.py", 3)]
        self.assertIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-D-001", r, spread)])
        # implements within a single file (tested-by files don't count) => silent in single-file repos
        one = [("implements", "a.py", 1), ("implements", "a.py", 9), ("tested-by", "t.py", 1)]
        self.assertNotIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-E-001", r, one)])
        # no member data supplied => check is skipped
        self.assertNotIn("file-spread", [f["check"] for f in R.lint_requirement("REQ-G-001", r)])

    def test_draft_is_out_of_scope(self):
        long_sent = " ".join(["word"] * 50) + "."
        reqs = {"DRAFT-X-001": self._req("draft", self._body(contract="- " + long_sent + "\n"))}
        code, out = self._lint(reqs)
        self.assertEqual(code, 0)
        self.assertNotIn("DRAFT-X-001", out)   # drafts are not linted

    def test_long_sentence_warns_with_count(self):
        long_sent = " ".join(["word"] * 40) + "."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract="- " + long_sent + "\n")))
        longs = [f for f in fs if f["check"] == "long-sentence"]
        self.assertTrue(longs)
        self.assertEqual(longs[0]["severity"], "warn")
        self.assertIn("40-word", longs[0]["detail"])

    def test_sentence_threshold_is_twentyfive(self):
        # 26 words: over the tightened ceiling, well under the old 35
        sent = " ".join(["word"] * 26) + "."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract="- " + sent + "\n")))
        self.assertTrue(any(f["check"] == "long-sentence" for f in fs))
        # 24 words stays silent, so the ceiling is a ceiling and not an off-by-one
        ok = " ".join(["word"] * 24) + "."
        clean = R.lint_requirement("REQ-Y-001", self._req("confirmed", self._body(contract="- " + ok + "\n")))
        self.assertFalse(any(f["check"] == "long-sentence" for f in clean))

    def test_contract_bullet_threshold_is_twentytwo(self):
        # two sentences, 24 words total: over the tightened bullet ceiling, under the old 30
        stmt = "- It creates the folder. " + " ".join(["word"] * 20) + " now."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=stmt + "\n")))
        self.assertTrue(any(f["check"] == "statement-too-long" for f in fs))

    def test_stacked_conditions_warns(self):
        line = "- It shall do A and B and C and D."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=line + "\n")))
        self.assertTrue(any(f["check"] == "stacked-conditions" for f in fs))

    def test_stacked_conditions_fires_without_a_modal_keyword(self):
        # plain present tense, no 'shall'/'must' anywhere: the check must still fire
        line = "- `init` creates the folder and the lock and the map and the summary."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=line + "\n")))
        self.assertTrue(any(f["check"] == "stacked-conditions" for f in fs))

    def test_anonymous_subject_warns_on_unnamed_it(self):
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(contract="- It creates the folder.\n")))
        hits = [f for f in fs if f["check"] == "anonymous-subject"]
        self.assertTrue(hits)
        self.assertEqual(hits[0]["severity"], "warn")

    def test_anonymous_subject_silent_when_the_subject_is_named(self):
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(contract="- `init` creates the folder.\n")))
        self.assertFalse(any(f["check"] == "anonymous-subject" for f in fs))

    def test_anonymous_subject_is_contract_only(self):
        # Acceptance prose legitimately says "it" in a Then clause; only the Contract is policed
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(acceptance="- It returns an empty dict.\n")))
        self.assertFalse(any(f["check"] == "anonymous-subject" for f in fs))

    def test_anonymous_subject_ignores_a_word_starting_with_it(self):
        # 'Items' / 'Iterating' must not be read as the pronoun
        fs = R.lint_requirement(
            "REQ-X-001", self._req("confirmed", self._body(contract="- Items are sorted.\n")))
        self.assertFalse(any(f["check"] == "anonymous-subject" for f in fs))

    def test_code_fence_line_not_flagged(self):
        long_sent = " ".join(["word"] * 50) + "."
        accept = "```\n" + long_sent + "\n```\n"
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(acceptance=accept)))
        self.assertFalse(any(f["check"] == "long-sentence" for f in fs))

    def test_in_fence_heading_does_not_disable_linter(self):  # bug-hunt #10/#14
        # a '## ' comment INSIDE a fence must not be read as a heading and silently
        # disable the linter for the rest of the section
        long_sent = " ".join(["word"] * 50) + "."
        accept = "```\n## not a heading\n```\n" + long_sent + "\n"
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(acceptance=accept)))
        self.assertTrue(any(f["check"] == "long-sentence" for f in fs))

    def test_lint_prose_first_section_only(self):  # bug-hunt #1
        long_sent = " ".join(["word"] * 50) + "."
        body = ("# T\n\n## WHAT — Contract\n- short.\n\n"
                "## Notes — contract addendum\n- " + long_sent + "\n")
        self.assertEqual(R._lint_prose(body, "contract"), ["short."])

    def test_lint_prose_keeps_option_flag_hyphen(self):  # bug-hunt #13
        body = "## WHAT — Contract\n--strict makes it fail.\n"
        self.assertEqual(R._lint_prose(body, "contract"), ["--strict makes it fail."])

    def test_strict_zero_on_warnings_only(self):
        long_sent = " ".join(["word"] * 40) + "."
        reqs = {"REQ-X-001": self._req("confirmed", self._body(contract="- " + long_sent + "\n"))}
        code, _ = self._lint(reqs, strict=True)
        self.assertEqual(code, 0)   # warnings never fail --strict

    def test_strict_nonzero_on_missing_section(self):
        body = "# T\n\n{}\n- the contract.\n".format(self.CONTRACT)  # no acceptance
        reqs = {"REQ-X-001": self._req("confirmed", body)}
        code, _ = self._lint(reqs, strict=True)
        self.assertEqual(code, 1)

    def test_statement_too_long_warns_on_multi_sentence_bullet(self):
        # two sentences, >30 words total → a stacked statement (atomicity smell)
        stmt = "- It shall do the first thing. " + " ".join(["then"] * 30) + " it acts."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=stmt + "\n")))
        hits = [f for f in fs if f["check"] == "statement-too-long"]
        self.assertTrue(hits)
        self.assertEqual(hits[0]["severity"], "warn")
        self.assertIn("sentences", hits[0]["detail"])

    def test_statement_too_long_silent_on_single_long_sentence(self):
        # a single long sentence is `long-sentence`'s job — must NOT double-flag here
        one = "- " + " ".join(["word"] * 40) + "."
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", self._body(contract=one + "\n")))
        self.assertTrue(any(f["check"] == "long-sentence" for f in fs))
        self.assertFalse(any(f["check"] == "statement-too-long" for f in fs))

    def test_ac_count_low_warns(self):
        body = self._body(contract="- ok.\n", acceptance="- only one AC.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertTrue(any(f["check"] == "ac-count-low" for f in fs))

    def test_ac_count_high_warns(self):
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

    def test_vague_term_warns(self):
        body = self._body(contract="- It shall be appropriate and user-friendly.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        vague = [f for f in fs if f["check"] == "vague-term"]
        self.assertEqual(len(vague), 2)            # 'appropriate' + 'user-friendly'
        self.assertEqual(vague[0]["severity"], "warn")

    def test_vague_term_skips_code_spans(self):
        # a backticked identifier that happens to contain a vague word is not flagged
        body = self._body(contract="- It shall return `fast_path` within the limit.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "vague-term" for f in fs))

    def test_vague_term_silent_on_precise_bullet(self):
        body = self._body(contract="- It shall return HTTP 200 within 2 seconds.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "vague-term" for f in fs))

    def test_redundant_modal_warns(self):
        body = self._body(contract="- The system shall log the event and must retry once.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        modal = [f for f in fs if f["check"] == "redundant-modal"]
        self.assertEqual(len(modal), 2)          # 'shall' + 'must'
        self.assertEqual(modal[0]["severity"], "warn")

    def test_redundant_modal_skips_code_spans(self):
        # a backticked identifier that happens to contain the word is not flagged
        body = self._body(contract="- `shall_retry` controls whether the job repeats.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "redundant-modal" for f in fs))

    def test_redundant_modal_silent_on_present_tense(self):
        body = self._body(contract="- The system logs the event and retries once.\n")
        fs = R.lint_requirement("REQ-X-001", self._req("confirmed", body))
        self.assertFalse(any(f["check"] == "redundant-modal" for f in fs))


class Translate(unittest.TestCase):  # tested-by: REQ-TRANSLATE-044
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

    def test_detect_lang_diacritics(self):
        self.assertEqual(R.detect_lang(self.RO_BODY), "ro")

    def test_detect_lang_english(self):
        self.assertEqual(R.detect_lang(self.EN_BODY), "en")

    def test_detect_lang_undetermined_on_code_only(self):
        self.assertIsNone(R.detect_lang("`foo_bar()` `baz.qux` `1234`"))

    def test_corpus_lang_is_majority_vote(self):
        reqs = {"REQ-A-001": self._req(self.RO_BODY), "REQ-B-002": self._req(self.RO_BODY),
                "REQ-C-003": self._req(self.EN_BODY)}
        self.assertEqual(R.corpus_lang(reqs), "ro")

    def test_lang_frontmatter_override_wins_over_detection(self):
        # Romanian prose, but explicitly tagged as English — override must win.
        reqs = {"REQ-A-001": self._req(self.RO_BODY, lang="en")}
        self.assertEqual(R.corpus_lang(reqs), "en")

    def test_translation_hash_changes_on_title_edit(self):
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

    def test_structural_signature_catches_dropped_backtick(self):
        source = "The `TOTAL` sum uses 2 decimals."
        good = "Suma `TOTAL` folosește 2 zecimale."
        bad = "Suma TOTAL folosește 2 zecimale."   # backtick dropped
        self.assertTrue(R._translation_preserves_structure(source, good))
        self.assertFalse(R._translation_preserves_structure(source, bad))

    def test_structural_signature_catches_dropped_number(self):
        source = "Rounds to 2 decimals."
        bad = "Rounds to decimals."   # number dropped
        self.assertFalse(R._translation_preserves_structure(source, bad))

    def test_parse_translated_sections_well_formed(self):
        text = ("===TITLE===\nT\n===INTENT===\nI\n===CONTRACT===\nC\n===ACCEPTANCE===\nA\n")
        parsed = R._parse_translated_sections(text)
        self.assertEqual(parsed, {"title": "T", "intent": "I", "contract": "C", "acceptance": "A"})

    def test_parse_translated_sections_missing_marker_is_none(self):
        text = "===TITLE===\nT\n===INTENT===\nI\n===CONTRACT===\nC\n"   # no ACCEPTANCE
        self.assertIsNone(R._parse_translated_sections(text))

    def test_cmd_translate_fails_open_when_cli_missing(self):
        reqs_dir = self._tmp_reqs_dir()
        reqs = {"REQ-A-001": self._req(self.RO_BODY)}
        with mock.patch.object(R.subprocess, "run", side_effect=FileNotFoundError):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_translate(reqs, reqs_dir)
        self.assertEqual(rc, 0)                              # never a gate, always exits 0
        self.assertIn("skipped", buf.getvalue())
        self.assertFalse(os.path.exists(os.path.join(reqs_dir, "_i18n", "en.json")))  # nothing cached

    def test_cmd_translate_happy_path_writes_cache_and_hits_on_rerun(self):
        reqs_dir = self._tmp_reqs_dir()
        reqs = {"REQ-A-001": self._req(self.RO_BODY)}
        fake_response = ("===TITLE===\nEnglish title\n"
                          "===INTENT===\nHere we explain why this requirement exists and "
                          "what problem it solves.\n"
                          "===CONTRACT===\n- The system calculates the `TOTAL` sum and shows "
                          "2 decimals.\n"
                          "===ACCEPTANCE===\n- Given a total of 10\n  When it is shown\n  "
                          "Then it reads 10.00\n")
        fake_proc = mock.Mock(returncode=0, stdout=fake_response)
        with mock.patch.object(R.subprocess, "run", return_value=fake_proc) as m:
            rc = R.cmd_translate(reqs, reqs_dir, target="en")
        self.assertEqual(rc, 0)
        self.assertEqual(m.call_count, 1)
        cache_path = os.path.join(reqs_dir, "_i18n", "en.json")
        self.assertTrue(os.path.exists(cache_path))
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        self.assertEqual(cache["REQ-A-001"]["title"], "English title")

        # re-run with unchanged content: cache hit, claude is NOT called again
        with mock.patch.object(R.subprocess, "run", return_value=fake_proc) as m2:
            R.cmd_translate(reqs, reqs_dir, target="en")
        self.assertEqual(m2.call_count, 0)

    def test_map_never_invokes_claude(self):
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
        with mock.patch.object(R.subprocess, "run", side_effect=AssertionError(
                "map must never shell out to claude")):
            data = R._build_map_data(reqs, {})
            R._attach_translations(data, reqs, reqs_dir)
        node = next(n for n in data["nodes"] if n["id"] == "REQ-A-001")
        self.assertEqual(node["i18n"]["en"]["title"], "English title")

    def test_stale_cache_entry_is_dropped_not_served(self):
        reqs_dir = self._tmp_reqs_dir()
        i18n_dir = os.path.join(reqs_dir, "_i18n")
        os.makedirs(i18n_dir)
        with open(os.path.join(i18n_dir, "en.json"), "w", encoding="utf-8") as f:
            json.dump({"REQ-A-001": {"hash": "stale-hash-does-not-match", "title": "Old"}}, f)
        reqs = {"REQ-A-001": self._req(self.RO_BODY)}
        out = R._load_translations(reqs, reqs_dir)
        self.assertNotIn("REQ-A-001", out)


class Show(unittest.TestCase):  # tested-by: REQ-SHOW-015
    def _show(self, reqs, members, cap_id):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_show(reqs, members, cap_id)
        return code, buf.getvalue()

    def _req(self, status="confirmed", extra="", body="# T\n"):
        return {"meta": {"status": status, "layer": "feature", **dict(_kv(extra))},
                "body": body, "path": "requirements/X.md"}

    def test_known_id_header_and_zero(self):
        code, out = self._show({"REQ-X-001": self._req()}, {}, "REQ-X-001")
        self.assertEqual(code, 0)
        self.assertIn("REQ-X-001", out)
        self.assertIn("confirmed", out)
        self.assertIn("feature", out)

    def test_unknown_id_returns_one(self):
        code, out = self._show({}, {}, "NOPE-000")
        self.assertEqual(code, 1)
        self.assertIn("no requirement with id NOPE-000", out)

    def test_priority_shown_in_header_when_set(self):
        reqs = {"REQ-X-001": self._req(extra="priority: must-have")}
        _, out = self._show(reqs, {}, "REQ-X-001")
        self.assertIn("must-have", out.splitlines()[0])

    def test_priority_absent_header_has_no_blank_segment(self):
        _, out = self._show({"REQ-X-001": self._req()}, {}, "REQ-X-001")
        self.assertNotIn("·  ·", out.splitlines()[0])   # no empty priority slot

    def test_reverse_dependency_listed(self):
        reqs = {"CORE-A-001": self._req(),
                "REQ-B-002": self._req(extra="depends_on: [CORE-A-001]")}
        _, out = self._show(reqs, {}, "CORE-A-001")
        self.assertIn("Depended on by", out)
        self.assertIn("REQ-B-002", out)

    def test_member_role_and_location(self):
        members = {"REQ-X-001": [("implements", "src/foo.py", 42)]}
        _, out = self._show({"REQ-X-001": self._req()}, members, "REQ-X-001")
        self.assertIn("implements", out)
        self.assertIn("src/foo.py:42", out)

    def test_open_verify_shown_placeholder_skipped(self):
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

    def test_show_annotates_a_member_with_its_verification_level(self):  # tested-by: REQ-VLEVEL-037 @unit
        reqs = {"REQ-X-001": self._req()}
        members = {"REQ-X-001": [("tested-by", "t.py", 2)]}
        levels = {"REQ-X-001": {"integration": [("t.py", 2)]}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(reqs, members, "REQ-X-001", levels)
        self.assertIn("@integration", buf.getvalue())

    def test_show_without_level_data_is_unchanged(self):  # tested-by: REQ-VLEVEL-037 @unit
        reqs = {"REQ-X-001": self._req()}
        members = {"REQ-X-001": [("tested-by", "t.py", 2)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(reqs, members, "REQ-X-001")      # old 3-arg call still works
        self.assertIn("t.py:2", buf.getvalue())
        self.assertNotIn("@", buf.getvalue().split("Members in code")[-1])


class Similar(unittest.TestCase):  # tested-by: REQ-SIMILAR-016
    def _sim(self, reqs, threshold=0.35):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_similar(reqs, threshold)
        return code, buf.getvalue()

    def _req(self, title, contract):
        return {"body": "# {t}\n\n> {t} intent.\n\n## WHAT — Contract (normative)\n- {c}\n".format(
            t=title, c=contract)}

    def test_near_identical_pair_reported(self):
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

    def test_cosine_clamped_to_one(self):  # bug-hunt #16
        v = R._tfidf({"a": ["foo", "bar", "foo", "baz"]})["a"]
        self.assertLessEqual(R._cosine(v, v), 1.0)

    def test_threshold_arg_rejects_bad_values(self):  # bug-hunt #3/#4
        import argparse as _ap
        for bad in ("nan", "inf", "0", "-1", "2", "abc"):
            with self.assertRaises(_ap.ArgumentTypeError):
                R._threshold_arg(bad)
        self.assertEqual(R._threshold_arg("0.35"), 0.35)

    def test_shared_terms_deterministic_on_weight_ties(self):  # bug-hunt #15
        # identical contracts -> every shared term ties on weight; the tiebreaker
        # must make the printed shared-terms list deterministic (alphabetical)
        c = "alpha bravo charlie delta echo foxtrot golf hotel"
        reqs = {"REQ-A-001": self._req("Aaa", c), "REQ-B-002": self._req("Bbb", c)}
        _, out = self._sim(reqs, 0.1)
        line = [ln for ln in out.splitlines() if "shared terms:" in ln][0]
        terms = line.split("shared terms:")[1].strip().split(", ")
        self.assertEqual(terms, sorted(terms))

    def test_unrelated_not_reported(self):
        reqs = {"REQ-A-001": self._req("Parser", "parse yaml frontmatter into a dictionary structure"),
                "REQ-B-002": self._req("Roadmap", "render mermaid gantt diagrams for milestones")}
        _, out = self._sim(reqs, 0.35)
        self.assertIn("No overlapping", out)

    def test_too_few_docs(self):
        code, out = self._sim({"REQ-A-001": self._req("Solo", "does one thing well")}, 0.35)
        self.assertEqual(code, 0)
        self.assertIn("at least two", out)

    def test_threshold_above_score_hides_pair(self):
        c = "validate user input and reject malformed payloads"
        reqs = {"REQ-A-001": self._req("Validator", c), "REQ-B-002": self._req("Validator", c)}
        _, out = self._sim(reqs, 1.01)   # cosine maxes at 1.0, so nothing qualifies
        self.assertIn("No overlapping", out)


class Search(unittest.TestCase):  # tested-by: REQ-SEARCH-036
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

    def test_query_ranks_matching_requirement_first_with_score(self):  # AC-1
        reqs = {"REQ-DRIFT-001": self._req("Drift", "detect when a contract changes against the lock hash baseline"),
                "REQ-MAP-002": self._req("Map", "render mermaid diagrams of the requirement graph")}
        code, out = self._search(reqs, "contract changed against the lock hash")
        self.assertEqual(code, 0)
        lines = self._score_lines(out)
        self.assertTrue(lines, "expected at least one ranked hit")
        # top hit is the drift requirement, printed with its cosine score (Dimon:
        # a match is shown WITH its score, never as a bare id)
        self.assertRegex(lines[0].strip(), r"^\d\.\d{3}\s+REQ-DRIFT-001\b")

    def test_no_lexical_overlap_reports_no_strong_match(self):  # AC-2 — Dimon blocking condition
        reqs = {"REQ-DRIFT-001": self._req("Drift", "detect when a contract changes against the lock hash"),
                "REQ-MAP-002": self._req("Map", "render mermaid diagrams of the requirement graph")}
        code, out = self._search(reqs, "photosynthesis quarterly dividend wombat")
        self.assertEqual(code, 0)
        self.assertIn("No strong match", out)
        # the failure mode being guarded: NO spurious ranked result below the floor
        self.assertNotIn("REQ-DRIFT-001", out)
        self.assertNotIn("REQ-MAP-002", out)

    def test_query_with_only_stopwords_says_no_terms(self):  # AC-3 — distinct from no-match
        reqs = {"REQ-A-001": self._req("Thing", "does one thing well")}
        code, out = self._search(reqs, "the and for with")
        self.assertEqual(code, 0)
        self.assertIn("No searchable terms", out)
        self.assertNotIn("No strong match", out)

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

    def test_ranking_matches_viewer_golden_fixture(self):  # parity: app/src/lib/search.js
        # The viewer ports this exact TF-IDF model (REQ-SEARCH-036). The SSR smoke
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
        self.assertIn("No strong match", none)


class Health(unittest.TestCase):  # tested-by: REQ-HEALTH-017
    def _health(self, reqs, members, as_json=False):
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            code = R.cmd_health(reqs, members, d, as_json)   # empty dir -> load_lock fails open
        return code, buf.getvalue()

    def _green(self):
        return {"meta": {"status": "confirmed"},
                "body": "# T\n\n## WHAT — Verify intent\n- None — clear.\n"}

    def test_all_green_is_100(self):
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        code, out = self._health({"REQ-A-001": self._green()}, members)
        self.assertEqual(code, 0)
        self.assertIn("100/100", out)

    def test_all_draft_is_zero(self):
        reqs = {"REQ-A-001": {"meta": {"status": "draft"}, "body": "# T\n"}}
        _, out = self._health(reqs, {})
        self.assertIn("0/100", out)

    def test_json_has_all_component_fields(self):  # bug-hunt #18: assert every emitted key
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        self.assertEqual(json.loads(out), {
            "score": 100, "total": 1, "healthy": 1, "confirmed": 1, "implemented": 1,
            "tested": 1, "drafts": 0, "orphans": 0, "untested": 0, "open_intent": 0, "drift": 0,
            "gate_errors": 0, "gate_link_sync_clean": True})

    def test_drift_drops_out_of_green(self):  # bug-hunt #18: exercise the drift axis
        reqs = {"REQ-A-001": self._green()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "_reqlock.json"), '{"REQ-A-001": "staleHASH0000"}')
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(reqs, members, d, as_json=True)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["drift"], 1)
        self.assertEqual(obj["healthy"], 0)
        self.assertLess(obj["score"], 100)

    # tested-by: REQ-COVERAGE-029
    def test_untagged_count_with_code_root(self):
        # REQ-COVERAGE-029 AC-1 — the read-only coverage signal: count scannable
        # code files with no membership tag. Informational: it must NOT lower
        # the score.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "src"))
            _write(os.path.join(d, "src", "tagged.py"), "# implements: REQ-A-001\nx = 1\n")
            _write(os.path.join(d, "src", "untagged.py"), "x = 2\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health({"REQ-A-001": self._green()}, members, d,
                             as_json=True, code_root=d)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["untagged"], 1)   # only untagged.py; tagged.py is covered
        self.assertEqual(obj["score"], 100)    # informational — never lowers the score

    def test_untagged_absent_without_code_root(self):
        # no code root (e.g. a unit-test caller) -> the key is absent, not zero,
        # so existing --json consumers keep their exact schema.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        self.assertNotIn("untagged", json.loads(out))

    # tested-by: REQ-REGISTRYLAG-035
    def _mkgit(self, d):
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.email", "t@t.com"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.name", "T"],
                       check=True, capture_output=True)

    def _gcommit(self, d, msg):
        subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-m", msg], check=True, capture_output=True)

    def test_commits_since_req_touch_counted(self):
        # REQ-REGISTRYLAG-035 AC-1 — advisory "registry lag" signal: how many
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
                R.cmd_health({"REQ-A-001": self._green()}, members, rdir,
                             as_json=True, code_root=d)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["commits_since_req_touch"], 2)
        self.assertEqual(obj["score"], 100)   # informational — never lowers the score

    def test_commits_since_req_touch_zero_when_fresh(self):
        # REQ-REGISTRYLAG-035 AC-2 — the most recent commit touched requirements/:
        # lag is 0 and the key is present (0, not absent) for --json consumers.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            self._mkgit(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"), "# T\n")
            self._gcommit(d, "reqs")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health({"REQ-A-001": self._green()}, members, rdir,
                             as_json=True, code_root=d)
            obj = json.loads(buf.getvalue())
        self.assertEqual(obj["commits_since_req_touch"], 0)

    def test_registry_lag_absent_without_git(self):
        # REQ-REGISTRYLAG-035 AC-3 — a code root that is not a git worktree ->
        # the key is absent (not zero), mirroring the untagged idiom.
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health({"REQ-A-001": self._green()}, members, d,
                             as_json=True, code_root=d)
            obj = json.loads(buf.getvalue())
        self.assertNotIn("commits_since_req_touch", obj)

    def test_orphan_not_green(self):
        # confirmed but no implements member -> orphan, drops out of green
        _, out = self._health({"REQ-A-001": self._green()}, {})
        self.assertIn("orphans", out)
        self.assertIn("0/100", out)

    def test_empty_corpus(self):
        code, out = self._health({}, {})
        self.assertEqual(code, 0)
        self.assertIn("0/100", out)

    def _need(self):
        return {"meta": {"status": "confirmed", "layer": "need"},
                "body": "# N\n\n## WHAT — Verify intent\n- None — clear.\n"}

    def test_satisfied_need_is_green(self):
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

    def test_unsatisfied_need_is_orphan_not_green(self):
        _, out = self._health({"NEED-X-001": self._need()}, {}, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["orphans"], 1)
        self.assertEqual(obj["healthy"], 0)

    # tested-by: REQ-HEALTH-017 (RM-6 / Senate reqmap-health-gate-cleanliness)
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
            R.cmd_health({}, members, d, as_badge=True)
        badge = json.loads(buf.getvalue())
        self.assertEqual(badge["color"], "red")
        self.assertIn("gate:1", badge["message"])

    def test_clean_badge_unaffected(self):
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, redirect_stdout(buf):
            R.cmd_health({"REQ-A-001": self._green()}, members, d, as_badge=True)
        badge = json.loads(buf.getvalue())
        self.assertEqual(badge["color"], "brightgreen")
        self.assertNotIn("gate:", badge["message"])

    def test_does_NOT_catch_untagged_value_edit(self):
        # RM-6's documented limitation (Senate reqmap-health-gate-cleanliness,
        # Round 2 — Socrate/Dimon): a value changed in a file that carries no
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
                R.cmd_health({"REQ-A-001": self._green()}, members, d,
                             as_json=True, code_root=d)
            obj = json.loads(buf.getvalue())
            # simulate the incident: the untagged file's value changes with no
            # supporting tag anywhere — re-running health sees no difference.
            _write(os.path.join(d, "config", "risk_limits.yaml"), "daily_loss_limit: 150\n")
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_health({"REQ-A-001": self._green()}, members, d,
                             as_json=True, code_root=d)
            obj2 = json.loads(buf2.getvalue())
        self.assertTrue(obj["gate_link_sync_clean"])
        self.assertTrue(obj2["gate_link_sync_clean"])   # unchanged — the gap is real


class TestLink(unittest.TestCase):  # tested-by: REQ-TESTLINK-018
    def test_link_problem_missing_file(self):
        self.assertIn("does not exist", R._test_link_problem("/no/such/file_xyz.py"))

    def test_link_problem_real_test_file(self):
        self.assertEqual("", R._test_link_problem(__file__))   # this file has def test_

    def test_link_problem_testless_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "notests.py")
            _write(p, "def helper():\n    return 1\n")
            self.assertIn("no test function", R._test_link_problem(p))

    def test_prose_it_call_is_not_a_test(self):  # bug-hunt #6
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "spec.md")
            _write(p, "The engine scans files; it (the parser) returns None.\n")
            self.assertIn("no test function", R._test_link_problem(p))

    def test_js_it_call_is_a_test(self):  # bug-hunt #6
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "spec.test.js")
            _write(p, "it('works', () => { expect(1).toBe(1); });\n")
            self.assertEqual("", R._test_link_problem(p))

    def test_go_test_func_recognized(self):  # bug-hunt #21
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "scan_test.go")
            _write(p, 'package main\nimport "testing"\nfunc TestScan(t *testing.T) {}\n')
            self.assertEqual("", R._test_link_problem(p))

    def test_rust_test_attr_recognized(self):  # bug-hunt #21
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "lib.rs")
            _write(p, "#[cfg(test)]\nmod t {\n  #[test]\n  fn checks() {}\n}\n")
            self.assertEqual("", R._test_link_problem(p))

    def test_py_runner_entry_recognized(self):  # stdlib suites drive checks from run()/main()
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "test_thing.py")
            _write(p, 'def run():\n    return 0\nif __name__ == "__main__":\n    raise SystemExit(run())\n')
            self.assertEqual("", R._test_link_problem(p))

    def test_py_runner_entry_needs_main_guard(self):  # a bare main()/run() without __main__ is not a test
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "helper.py")
            _write(p, "def main():\n    return 0\n")
            self.assertIn("no test function", R._test_link_problem(p))

    def test_check_warns_warn_only_on_broken_link(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = {"REQ-A-001": {"meta": {"status": "confirmed", "layer": "feature"},
                                  "body": "# T\n", "path": os.path.join(d, "REQ-A-001.md")}}
            members = {"REQ-A-001": [("implements", "src/foo.py", 1),
                                     ("tested-by", "tests/missing_test.py", 2)]}
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, update_lock=False, code_root=d)
            out = buf.getvalue()
            self.assertEqual(code, 0)                              # warn-only -> still passes
            self.assertIn("tested-by tests/missing_test.py", out)
            self.assertIn("does not exist", out)


_VERIFY_ROLE = "verifies"  # runtime-built so synthetic tags don't pollute the repo scan


def v_tag(cap, ac):
    return "# {}: {}#{}".format(_VERIFY_ROLE, cap, ac)


def _ac_body(contract="- It shall do the thing.", acceptance="AC-1\n  Given x\n  When y\n  Then z"):
    return ("# T\n\n## WHAT — Contract (normative)\n{}\n\n"
            "## HOW — Acceptance (= tests)\n{}\n".format(contract, acceptance))


class AcVerify(unittest.TestCase):  # tested-by: REQ-ACVERIFY-019
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, update_lock=False, code_root=d)
            return code, buf.getvalue()

    def _req(self, acceptance, impl=True, tested=True):
        body = "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n" + \
               _ac_body(acceptance=acceptance)
        files = {"A-FOO-001.md": body}
        code = "x=1\n"
        if impl:
            code += "# {}: A-FOO-001\n".format("implements")
        if tested:
            code += "# {}: A-FOO-001\ndef test_x():\n    pass\n".format("tested" + "-by")
        files["mod.py"] = code
        return files

    def test_scan_ac_verifies_parses_tag(self):  # verifies: REQ-ACVERIFY-019#AC-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "t.py"), v_tag("REQ-X-001", "AC-1") + "\n")
            cover = R.scan_ac_verifies(d, d)
            self.assertIn("REQ-X-001", cover)
            self.assertIn("AC-1", cover["REQ-X-001"])

    def test_scan_ac_verifies_requires_ac_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "t.py"), "# {}: REQ-X-001\n".format(_VERIFY_ROLE))  # no #AC
            self.assertEqual(R.scan_ac_verifies(d, d), {})

    def test_labeled_acs_extracts_labels(self):
        body = _ac_body(acceptance="AC-1\n  Given a\nAC-2\n  Given b")
        self.assertEqual(R._labeled_acs(body), ["AC-1", "AC-2"])

    def test_labeled_acs_empty_on_bullet_acs(self):
        body = _ac_body(acceptance="- a bullet criterion.\n- another one.")
        self.assertEqual(R._labeled_acs(body), [])

    def test_partial_coverage_warns_the_uncovered(self):  # verifies: REQ-ACVERIFY-019#AC-1
        files = self._req("AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n  Then d")
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n"   # only AC-1 covered
        code, out = self._check(files)
        self.assertIn("AC-2 has no", out)
        self.assertNotIn("AC-1 has no", out)
        self.assertEqual(code, 0)                              # warn-only

    def test_full_coverage_silent(self):  # verifies: REQ-ACVERIFY-019#AC-2
        files = self._req("AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n  Then d")
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n" + v_tag("A-FOO-001", "AC-2") + "\n"
        _, out = self._check(files)
        self.assertNotIn("criterion unverified", out)

    def test_no_verify_tags_is_optin_silent(self):  # verifies: REQ-ACVERIFY-019#AC-3
        files = self._req("AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n  Then d")  # zero verifies tags
        _, out = self._check(files)
        self.assertNotIn("criterion unverified", out)

    def test_bullet_acs_exempt(self):  # verifies: REQ-ACVERIFY-019#AC-4
        files = self._req("- a bullet criterion.\n- another one.")
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n"   # tag present but ACs unlabelled
        _, out = self._check(files)
        self.assertNotIn("criterion unverified", out)


class Traceability(unittest.TestCase):  # tested-by: REQ-TRACE-020
    def _check(self, files):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(reqs, members, d, update_lock=False, code_root=d)
            return code, buf.getvalue()

    def _feature(self, rid, extra=""):
        body = REQ.format(id=rid, status="confirmed", layer="feature", extra=extra, title="T")
        body += ("\n## WHAT — Contract (normative)\n- It shall x.\n\n"
                 "## HOW — Acceptance (= tests)\n- a.\n")
        return body

    def test_need_layer_is_valid(self):
        self.assertIn("need", R.VALID_LAYER)

    def test_dangling_satisfies_warns_not_errors(self):  # verifies: REQ-TRACE-020#AC-1
        files = {"A-FOO-001.md": self._feature("A-FOO-001", "satisfies: [GHOST-X-999]\n"),
                 "mod.py": "# {}: A-FOO-001\ndef test_a():\n    pass\n".format("tested" + "-by") +
                           "# {}: A-FOO-001\n".format("implements")}
        code, out = self._check(files)
        self.assertIn("satisfies GHOST-X-999", out)
        self.assertEqual(code, 0)                              # warn, not error

    def test_orphan_need_warns(self):  # verifies: REQ-TRACE-020#AC-2
        need = REQ.format(id="NEED-X-001", status="confirmed", layer="need", extra="", title="N")
        need += "\n## WHAT — Contract (normative)\n- want.\n\n## HOW — Acceptance (= tests)\n- a.\n"
        _, out = self._check({"NEED-X-001.md": need})
        self.assertIn("need has no requirement that satisfies it", out)

    def test_satisfied_need_not_orphan(self):  # verifies: REQ-TRACE-020#AC-2
        need = REQ.format(id="NEED-X-001", status="confirmed", layer="need", extra="", title="N")
        need += "\n## WHAT — Contract (normative)\n- want.\n\n## HOW — Acceptance (= tests)\n- a.\n"
        files = {"NEED-X-001.md": need,
                 "A-FOO-001.md": self._feature("A-FOO-001", "satisfies: [NEED-X-001]\n"),
                 "mod.py": "# {}: A-FOO-001\ndef test_a():\n    pass\n".format("tested" + "-by") +
                           "# {}: A-FOO-001\n".format("implements")}
        _, out = self._check(files)
        self.assertNotIn("unaddressed", out)
        self.assertNotIn("NEED-X-001: need has no", out)

    def test_need_exempt_from_implements_and_tested(self):  # verifies: REQ-TRACE-020#AC-3
        need = REQ.format(id="NEED-X-001", status="confirmed", layer="need", extra="", title="N")
        need += "\n## WHAT — Contract (normative)\n- want.\n\n## HOW — Acceptance (= tests)\n- a.\n"
        # satisfied so the orphan warn is silent; assert NO implements/tested-by finding for the need
        files = {"NEED-X-001.md": need,
                 "A-FOO-001.md": self._feature("A-FOO-001", "satisfies: [NEED-X-001]\n"),
                 "mod.py": "# {}: A-FOO-001\ndef test_a():\n    pass\n".format("tested" + "-by") +
                           "# {}: A-FOO-001\n".format("implements")}
        code, out = self._check(files)
        self.assertNotIn("NEED-X-001: status", out)            # no "no implements" error
        self.assertNotIn("NEED-X-001: confirmed but no tested-by", out)
        self.assertEqual(code, 0)

    def test_show_prints_upstream_both_directions(self):  # verifies: REQ-TRACE-020#AC-4
        need = REQ.format(id="NEED-X-001", status="confirmed", layer="need", extra="", title="N")
        feat = self._feature("A-FOO-001", "satisfies: [NEED-X-001]\n")
        reqs = {"NEED-X-001": {"meta": {"status": "confirmed", "layer": "need"}, "body": need,
                               "path": "requirements/NEED-X-001.md"},
                "A-FOO-001": {"meta": {"status": "confirmed", "layer": "feature",
                                       "satisfies": ["NEED-X-001"]}, "body": feat,
                              "path": "requirements/A-FOO-001.md"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(reqs, {}, "A-FOO-001")
        self.assertIn("Satisfies (upstream): NEED-X-001", buf.getvalue())
        buf2 = io.StringIO()
        with redirect_stdout(buf2):
            R.cmd_show(reqs, {}, "NEED-X-001")
        self.assertIn("Satisfied by: A-FOO-001", buf2.getvalue())

    def test_map_data_carries_upstream(self):
        reqs = {"NEED-X-001": {"meta": {"status": "confirmed", "layer": "need"}, "body": "# N\n"},
                "A-FOO-001": {"meta": {"status": "confirmed", "layer": "feature",
                                       "satisfies": ["NEED-X-001"]}, "body": "# T\n"}}
        data = R._build_map_data(reqs, {})
        node = next(n for n in data["nodes"] if n["id"] == "A-FOO-001")
        need = next(n for n in data["nodes"] if n["id"] == "NEED-X-001")
        self.assertEqual(node["satisfies"], ["NEED-X-001"])
        self.assertEqual(need["satisfied_by"], ["A-FOO-001"])
        self.assertIn(["A-FOO-001", "NEED-X-001"], data["upstream_edges"])

    def test_map_data_need_has_no_unimplemented_risk(self):  # wiring guard: layer reaches _risk_signals at build
        reqs = {"NEED-X-001": {"meta": {"status": "confirmed", "layer": "need"}, "body": "# N\n"},
                "A-FOO-001": {"meta": {"status": "confirmed", "layer": "feature"}, "body": "# T\n"}}
        data = R._build_map_data(reqs, {})   # neither has members
        need = next(n for n in data["nodes"] if n["id"] == "NEED-X-001")
        feat = next(n for n in data["nodes"] if n["id"] == "A-FOO-001")
        self.assertNotIn("unimplemented", [r["signal"] for r in need["risks"]])   # gate-exempt
        self.assertIn("unimplemented", [r["signal"] for r in feat["risks"]])      # feature still flags


class MilestoneGate(unittest.TestCase):  # tested-by: REQ-CHECK-006
    def _warns(self, milestone, status="confirmed"):
        with tempfile.TemporaryDirectory() as d:
            body = ("---\nid: A-X-001\nstatus: {}\nlayer: feature\nmilestone: {}\n---\n\n"
                    "# T\n\n## WHAT — Contract\n- x.\n\n## HOW — Acceptance\n- a.\n").format(status, milestone)
            _write(os.path.join(d, "A-X-001.md"), body)
            _write(os.path.join(d, "x.py"), tag("A-X-001") + "\n")   # implements so no orphan error
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, d, update_lock=False, code_root=d)
            return buf.getvalue()

    def test_malformed_milestone_warns(self):  # verifies: REQ-CHECK-006#AC-6
        for bad in ("next", "1.14", "V1.0", "v1.14-beta"):
            self.assertIn("malformed", self._warns(bad), bad)

    def test_valid_milestone_silent(self):  # verifies: REQ-CHECK-006#AC-6
        for ok in ("v1.14", "v1.04", "v2"):
            self.assertNotIn("malformed", self._warns(ok), ok)

    def test_deprecated_milestone_exempt(self):  # verifies: REQ-CHECK-006#AC-6
        self.assertNotIn("malformed", self._warns("next", status="deprecated"))


class PromoteTodo(unittest.TestCase):  # tested-by: REQ-PROMOTE-TODO-001
    TODO = "## v1.14\n- [ ] Build the thing | lane: ops\n- [x] Done already | lane: feature\n"

    def _setup(self, d):
        _write(os.path.join(d, "TODO.md"), self.TODO)
        rq = os.path.join(d, "requirements")
        os.makedirs(rq, exist_ok=True)
        return rq

    def _run(self, rq, name, cap_id, mark_done=False, root="."):
        with redirect_stdout(io.StringIO()):
            return R.cmd_promote_todo(rq, None, name, cap_id, mark_done=mark_done, root=root)

    def test_scaffolds_draft_from_todo(self):
        with tempfile.TemporaryDirectory() as d:
            rq = self._setup(d)
            self.assertEqual(self._run(rq, "Build the thing", "REQ-T-001", root=d), 0)
            text = open(os.path.join(rq, "REQ-T-001.md"), encoding="utf-8").read()
            self.assertIn("# Build the thing", text)
            self.assertIn("milestone: v1.14", text)
            self.assertIn("layer: feature", text)            # lane ops -> feature
            self.assertIn("status: draft", text)
            self.assertIn("- [ ] Build the thing", open(os.path.join(d, "TODO.md"), encoding="utf-8").read())  # unchanged

    def test_mark_done_flips_only_matched_line(self):
        with tempfile.TemporaryDirectory() as d:
            rq = self._setup(d)
            self._run(rq, "Build the thing", "REQ-T-001", mark_done=True, root=d)
            todo = open(os.path.join(d, "TODO.md"), encoding="utf-8").read()
            self.assertIn("- [x] Build the thing", todo)
            self.assertIn("- [x] Done already", todo)        # other lines untouched

    def test_mark_done_flips_todo_with_pipe_in_name(self):
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

    def test_errors_write_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            rq = self._setup(d)
            self.assertEqual(self._run(rq, "Build the thing", None, root=d), 2)            # no --id
            self.assertEqual(self._run(rq, "nope", "REQ-T-001", root=d), 1)                # not found
            self.assertFalse(os.path.exists(os.path.join(rq, "REQ-T-001.md")))
            _write(os.path.join(rq, "REQ-T-001.md"), "x")
            self.assertEqual(self._run(rq, "Build the thing", "REQ-T-001", root=d), 1)     # id taken


class Review(unittest.TestCase):  # tested-by: REQ-REVIEW-022
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

    def test_unknown_id_fails_closed(self):  # bug: review-unknown-id-silent-empty-plan
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_review(R.load_requirements(d), "TYPO-X-999")
            self.assertEqual(rc, 1, "an unknown single id must exit 1, not emit an empty plan")
            self.assertIn("no requirement with id", buf.getvalue())

    def test_plan_structure_and_coverage(self):
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

    def test_review_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            reqs = R.load_requirements(d)
            self.assertEqual(self._review(reqs), self._review(reqs))

    def test_gate_ignores_ai_sidecar(self):  # DETERMINISM WALL — verifies: REQ-REVIEW-022
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)

            def gate():
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = R.cmd_check(reqs, members, d, update_lock=False, code_root=d)
                return code, buf.getvalue()

            before = gate()
            _write(os.path.join(d, "_ai_review.md"),
                   "# AI — advisory (non-deterministic). NOT a gate.\n- something\n")
            self.assertEqual(before, gate())   # check never reads the AI sidecar


class ScanCache(unittest.TestCase):  # tested-by: REQ-SCANCACHE-023
    def _tree(self, d):
        rq = os.path.join(d, "requirements")
        os.makedirs(rq, exist_ok=True)
        _write(os.path.join(d, "a.py"), tag("A-X-001") + "\n# {}: A-X-001\n".format("tested" + "-by"))
        _write(os.path.join(d, "b.py"), tag("B-Y-002") + "\n")
        return rq

    def test_cache_results_byte_identical(self):  # verifies: REQ-SCANCACHE-023
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            no = R.scan_members(d, rq, cache=False)
            c1 = R.scan_members(d, rq, cache=True)    # builds cache
            c2 = R.scan_members(d, rq, cache=True)    # reuses cache
            self.assertEqual(no, c1)
            self.assertEqual(no, c2)
            self.assertTrue(os.path.exists(os.path.join(rq, "_scancache.json")))

    def test_cache_invalidates_on_change(self):
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            p = os.path.join(d, "a.py")
            R.scan_members(d, rq, cache=True)                       # cache A-X-001
            _write(p, tag("C-Z-003") + "\n# changed, different size\n")   # size differs -> invalidate
            m = R.scan_members(d, rq, cache=True)
            self.assertIn("C-Z-003", m)
            self.assertNotIn("A-X-001", m)

    def test_cache_prunes_deleted_file(self):
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            R.scan_members(d, rq, cache=True)
            os.remove(os.path.join(d, "b.py"))
            m = R.scan_members(d, rq, cache=True)
            self.assertNotIn("B-Y-002", m)
            cache = json.load(open(os.path.join(rq, "_scancache.json"), encoding="utf-8"))
            self.assertNotIn("b.py", cache)

    def test_cache_off_by_default_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            R.scan_members(d, rq)                                   # no cache arg
            self.assertFalse(os.path.exists(os.path.join(rq, "_scancache.json")))

    def test_corrupt_cache_fails_open(self):
        with tempfile.TemporaryDirectory() as d:
            rq = self._tree(d)
            _write(os.path.join(rq, "_scancache.json"), "{ not json")
            self.assertEqual(R.scan_members(d, rq, cache=False),
                             R.scan_members(d, rq, cache=True))     # corrupt cache -> full re-scan, same result


class LockUpdate(unittest.TestCase):
    def test_update_lock_prints_changed_hashes(self):
        """--update-lock must report which requirement hashes actually changed."""
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            # Write a requirement
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="in-progress",
                              layer="bus", extra="", title="T") +
                   "\n## WHAT — Contract\n- original contract\n")
            # Build initial lock
            reqs = R.load_requirements(rdir)
            members = {}
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, rdir, update_lock=True)
            # Now change the body so the hash differs
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="in-progress",
                              layer="bus", extra="", title="T") +
                   "\n## WHAT — Contract\n- changed contract\n")
            reqs2 = R.load_requirements(rdir)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_check(reqs2, members, rdir, update_lock=True)
            out = buf2.getvalue()
            self.assertIn("lock update:", out,
                          "update-lock must report hash changes — got: " + out)
            self.assertIn("REQ-A-001", out)

    def test_update_lock_reports_removed_entry(self):
        """--update-lock must report requirements removed from the lock."""
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            # Write a requirement and build initial lock
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="in-progress",
                              layer="bus", extra="", title="T"))
            reqs = R.load_requirements(rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, {}, rdir, update_lock=True)
            # Now delete the requirement file (simulate removal)
            os.remove(os.path.join(rdir, "REQ-A-001.md"))
            reqs2 = R.load_requirements(rdir)  # empty
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_check(reqs2, {}, rdir, update_lock=True)
            out = buf2.getvalue()
            self.assertIn("removed from lock", out,
                          "update-lock must report removed entries — got: " + out)
            self.assertIn("REQ-A-001", out)


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


class CheckStrict(unittest.TestCase):
    """--strict promotes drift and test-link integrity to errors."""

    def _setup_confirmed(self, d, contract="- shall do X"):
        """Write a confirmed req with a member tag; build and save the lock."""
        rdir = os.path.join(d, "requirements")
        body = (
            "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
            "## WHAT — Contract\n{}\n\n"
            "## HOW — Acceptance\n- AC-1\n".format(contract)
        )
        _write(os.path.join(rdir, "REQ-A-001.md"), body)
        src = os.path.join(d, "src.py")
        _write(src, "# {}: REQ-A-001\n".format("impl" + "ements"))
        reqs = R.load_requirements(rdir)
        members = R.scan_members(d, rdir)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_check(reqs, members, rdir, update_lock=True)
        return rdir

    def test_strict_clean_exits_0(self):
        """--strict: clean corpus exits 0."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._setup_confirmed(d)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, rdir, update_lock=False, strict=True)
            self.assertEqual(rc, 0)

    def test_strict_drift_exits_1(self):
        """--strict: a stale confirmed req (drift) exits 1; without --strict exits 0."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._setup_confirmed(d, contract="- shall do X")
            # Mutate the body to create drift
            body2 = (
                "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                "## WHAT — Contract\n- shall do Y (changed)\n\n"
                "## HOW — Acceptance\n- AC-1\n"
            )
            _write(os.path.join(rdir, "REQ-A-001.md"), body2)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            # code_root=d is not optional here: cmd_check defaults it to "." and this
            # assertion counts DRIFT lines, so without it the run scans whatever the
            # process cwd happens to be. From plugin/ that is the REAL corpus, whose
            # own drift added a second DRIFT line and failed the test - passing from
            # plugin/scripts/ and failing from plugin/, both documented invocations.
            with redirect_stdout(buf):
                rc_normal = R.cmd_check(reqs, members, rdir, update_lock=False, code_root=d)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc_strict = R.cmd_check(reqs, members, rdir, update_lock=False,
                                        code_root=d, strict=True)
            self.assertEqual(rc_normal, 0, "without --strict, drift must exit 0")
            self.assertEqual(rc_strict, 1, "with --strict, drift must exit 1")
            # promoted warn must appear exactly once, not twice
            drift_lines = [l for l in buf2.getvalue().splitlines() if "DRIFT" in l]
            self.assertEqual(len(drift_lines), 1, "DRIFT line must appear exactly once under --strict")

    def test_strict_bad_testlink_exits_1(self):
        """--strict: confirmed req with missing tested-by file exits 1."""
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            body = (
                "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                "## WHAT — Contract\n- shall do X\n\n"
                "## HOW — Acceptance\n- AC-1\n"
            )
            _write(os.path.join(rdir, "REQ-A-001.md"), body)
            _write(os.path.join(d, "src.py"),
                   "# {}: REQ-A-001\n".format("impl" + "ements"))
            # Inject a tested-by member pointing to a missing file
            members = {
                "REQ-A-001": [
                    ("implements", "src.py", 1),
                    ("tested-by", "missing_test.py", 1),
                ]
            }
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc_normal = R.cmd_check(R.load_requirements(rdir), members, rdir,
                                        update_lock=False)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc_strict = R.cmd_check(R.load_requirements(rdir), members, rdir,
                                        update_lock=False, strict=True)
            self.assertEqual(rc_normal, 0, "without --strict, bad test-link is warn")
            self.assertEqual(rc_strict, 1, "with --strict, bad test-link is error")
            tl_lines = [l for l in buf2.getvalue().splitlines() if "tested-by" in l]
            self.assertEqual(len(tl_lines), 1, "test-link line must appear exactly once under --strict")


class CheckJson(unittest.TestCase):
    """--json emits structured output, exit-code aligned with ok field."""

    def _make_clean_corpus(self, d):
        rdir = os.path.join(d, "requirements")
        body = (
            "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
            "## WHAT — Contract\n- shall do X\n\n"
            "## HOW — Acceptance\n- AC-1\n"
        )
        _write(os.path.join(rdir, "REQ-A-001.md"), body)
        _write(os.path.join(d, "src.py"),
               "# {}: REQ-A-001\n".format("impl" + "ements"))
        reqs = R.load_requirements(rdir)
        members = R.scan_members(d, rdir)
        # build initial lock
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_check(reqs, members, rdir, update_lock=True)
        return rdir

    def test_json_clean_ok_true(self):
        """--json: clean corpus → ok=true, errors=[], exit 0."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._make_clean_corpus(d)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, rdir, update_lock=False, as_json=True)
            data = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(data["ok"])
            self.assertEqual(data["errors"], [])

    def test_json_error_ok_false_exit_1(self):
        """--json: a dangling tag → ok=false, errors non-empty, exit 1."""
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            os.makedirs(rdir, exist_ok=True)
            # No requirements, but a member tag pointing to a nonexistent req
            _write(os.path.join(d, "src.py"),
                   "# {}: REQ-Z-999\n".format("impl" + "ements"))
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, rdir, update_lock=False, as_json=True)
            data = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(len(data["errors"]) > 0)

    def test_json_exit_code_aligned(self):
        """ok field in JSON must be equivalent to exit 0 (both directions)."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._make_clean_corpus(d)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            # clean: ok=true ⟺ exit 0
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, rdir, update_lock=False, as_json=True)
            data = json.loads(buf.getvalue())
            self.assertEqual(data["ok"], (rc == 0),
                             "ok must be True exactly when exit code is 0")
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            os.makedirs(rdir, exist_ok=True)
            _write(os.path.join(d, "src.py"),
                   "# {}: REQ-Z-999\n".format("impl" + "ements"))
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            # error: ok=false ⟺ exit 1
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, rdir, update_lock=False, as_json=True)
            data = json.loads(buf.getvalue())
            self.assertEqual(data["ok"], (rc == 0),
                             "ok must be False exactly when exit code is 1")

    def test_json_has_warnings_key(self):
        """--json output must include a warnings key."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._make_clean_corpus(d)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, rdir, update_lock=False, as_json=True)
            data = json.loads(buf.getvalue())
            self.assertIn("warnings", data)


class CheckSince(unittest.TestCase):
    """--since <ref> scopes the gate to files changed since ref."""

    def _init_git_repo(self, d):
        """Initialize a minimal git repo in d so --since can call git diff."""
        subprocess.run(["git", "init", d], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.email", "test@test.com"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "config", "user.name", "Test"],
                       check=True, capture_output=True)
        return d

    def _commit_all(self, d, msg="init"):
        subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", d, "commit", "-m", msg],
                       check=True, capture_output=True)

    def test_since_fallback_on_bad_ref(self):
        """--since with a non-existent ref falls back to full scan and emits WARN."""
        with tempfile.TemporaryDirectory() as d:
            self._init_git_repo(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                   "## WHAT — Contract\n- shall do X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(d, "src.py"),
                   "# {}: REQ-A-001\n".format("impl" + "ements"))
            self._commit_all(d)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, rdir, update_lock=True,
                                 since="nonexistent-sha-9999")
            out = buf.getvalue()
            self.assertIn("WARN", out,
                          "bad --since ref must fall back with a WARN")
            # Gate still ran (full scan fallback) — a clean corpus exits 0
            self.assertEqual(rc, 0)

    def test_since_only_checks_changed_files(self):
        """--since only validates reqs whose member files changed since the ref."""
        with tempfile.TemporaryDirectory() as d:
            self._init_git_repo(d)
            rdir = os.path.join(d, "requirements")
            # Two confirmed reqs
            for rid in ("REQ-A-001", "REQ-B-002"):
                _write(os.path.join(rdir, f"{rid}.md"),
                       f"---\nid: {rid}\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                       "## WHAT — Contract\n- shall do X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(d, "src_a.py"),
                   "# {}: REQ-A-001\n".format("impl" + "ements"))
            _write(os.path.join(d, "src_b.py"),
                   "# {}: REQ-B-002\n".format("impl" + "ements"))
            self._commit_all(d, "baseline")
            base_ref = subprocess.run(
                ["git", "-C", d, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            # Modify only src_a.py
            _write(os.path.join(d, "src_a.py"),
                   "# {}: REQ-A-001\n# changed\n".format("impl" + "ements"))
            self._commit_all(d, "touch-a-only")

            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, rdir, update_lock=True,
                            code_root=d, since=base_ref)
            # The check ran: REQ-A-001 member (src_a.py) was changed, so it was
            # included; REQ-B-002 was untouched.  Just verify it completes without
            # error (both are clean, no dangling tags).
            # Re-run and capture rc:
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc = R.cmd_check(reqs, members, rdir, update_lock=False,
                                 code_root=d, since=base_ref)
            self.assertEqual(rc, 0)

    def test_since_fallback_no_git(self):
        """--since falls back gracefully when git is not available (monkeypatched)."""
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                   "## WHAT — Contract\n- shall do X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(d, "src.py"),
                   "# {}: REQ-A-001\n".format("impl" + "ements"))
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            # Simulate git failure
            with mock.patch("subprocess.run", side_effect=FileNotFoundError("git not found")):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = R.cmd_check(reqs, members, rdir, update_lock=True,
                                     since="HEAD~1")
            out = buf.getvalue()
            self.assertIn("WARN", out, "must WARN when git is unavailable")
            self.assertEqual(rc, 0, "clean corpus exits 0 even on git failure")

    def test_since_matches_when_the_root_is_spelled_differently(self):
        """A code_root spelled differently from git's own toplevel still matches.

        Regression for the Windows-only fail-open the CI portability matrix found on
        its first run: the caller's code_root carried an 8.3 short component
        (C:/Users/RUNNER~1/...) while `git rev-parse --show-toplevel` returns the
        long form, so abspath+normcase never made the two sets intersect, every member
        dropped out of the changed-set, and the gate passed a tree with a dangling tag
        in it. Reproduced here through a symlinked path, the POSIX shape of the same
        defect: both spellings must resolve to one key.
        """
        with tempfile.TemporaryDirectory() as d:
            real = os.path.join(d, "real-checkout")
            os.makedirs(real)
            link = os.path.join(d, "lnk")
            try:
                os.symlink(real, link, target_is_directory=True)
            except (OSError, NotImplementedError, AttributeError):
                self.skipTest("symlinks unavailable (Windows without developer mode)")
            self._init_git_repo(real)
            rdir = os.path.join(real, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                   "## WHAT — Contract\n- does X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(real, "src_a.py"),
                   "# {}: REQ-A-001\n".format("impl" + "ements"))
            self._commit_all(real, "baseline")
            base_ref = subprocess.run(
                ["git", "-C", real, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True).stdout.strip()
            _write(os.path.join(real, "ghost.py"),
                   "# {}: REQ-GHOST-999\n".format("impl" + "ements"))
            self._commit_all(real, "add-ghost")

            # Everything below addresses the repo through the LINK spelling.
            lrdir = os.path.join(link, "requirements")
            reqs = R.load_requirements(lrdir)
            members = R.scan_members(link, lrdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, lrdir, update_lock=False,
                                 code_root=link, since=base_ref)
            self.assertEqual(rc, 1,
                             "a dangling tag must still be caught when code_root is "
                             "spelled differently than git's toplevel")

    def test_path_key_folds_an_alternate_spelling_of_one_directory(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "x.py")
            _write(f, "x=1\n")
            indirect = os.path.join(d, "sub", "..", "x.py")
            self.assertEqual(R._path_key(f), R._path_key(indirect))
            self.assertEqual(R._path_key(f), R._path_key(os.path.realpath(f)))

    def test_since_from_subdir_of_git_root(self):
        """--since must work when code_root is a subdirectory of the git root.

        `git diff` emits root-relative paths; the engine resolves the toplevel so
        the since-set lines up with member abspaths. Regression for the bug where
        running `gate --since` from a subdir silently checked zero requirements
        and passed even with a dangling tag in a changed file.
        """
        with tempfile.TemporaryDirectory() as d:
            self._init_git_repo(d)
            sub = os.path.join(d, "proj")          # code_root is a subdir of git root
            rdir = os.path.join(sub, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                   "## WHAT — Contract\n- shall do X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(sub, "src_a.py"),
                   "# {}: REQ-A-001\n".format("impl" + "ements"))
            self._commit_all(d, "baseline")
            base_ref = subprocess.run(
                ["git", "-C", d, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True).stdout.strip()
            # A dangling tag (no such requirement) in a NEW file under the subdir.
            _write(os.path.join(sub, "ghost.py"),
                   "# {}: REQ-GHOST-999\n".format("impl" + "ements"))
            self._commit_all(d, "add-ghost")

            reqs = R.load_requirements(rdir)
            members = R.scan_members(sub, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs, members, rdir, update_lock=False,
                                 code_root=sub, since=base_ref)
            self.assertEqual(
                rc, 1,
                "a dangling tag in a changed file under a subdir code_root must be caught")

    def test_since_update_lock_preserves_full_memberlock(self):
        """`--since --update-lock` must NOT wipe reverse-drift baselines for members
        whose files were unchanged since the ref. Regression: the memberlock was
        rebuilt from the --since-filtered member set, dropping the rest (#6)."""
        with tempfile.TemporaryDirectory() as d:
            self._init_git_repo(d)
            rdir = os.path.join(d, "requirements")
            for rid in ("REQ-A-001", "REQ-B-002"):
                _write(os.path.join(rdir, f"{rid}.md"),
                       f"---\nid: {rid}\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                       "## WHAT — Contract\n- shall do X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(d, "src_a.py"), "# {}: REQ-A-001\n".format("impl" + "ements"))
            _write(os.path.join(d, "src_b.py"), "# {}: REQ-B-002\n".format("impl" + "ements"))
            self._commit_all(d, "baseline")
            # Full baseline of the memberlock (both members recorded).
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(reqs, members, rdir, update_lock=True, code_root=d)
            full_keys = set(R.load_memberlock(rdir))
            self.assertEqual(full_keys, {"REQ-A-001", "REQ-B-002"})
            base_ref = subprocess.run(
                ["git", "-C", d, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True).stdout.strip()
            # Change only src_a.py, then re-baseline scoped with --since.
            _write(os.path.join(d, "src_a.py"),
                   "# {}: REQ-A-001\n# changed\n".format("impl" + "ements"))
            self._commit_all(d, "touch-a")
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(reqs, members, rdir, update_lock=True, code_root=d, since=base_ref)
            after_keys = set(R.load_memberlock(rdir))
            self.assertTrue(
                full_keys <= after_keys,
                "since+update-lock dropped unchanged members' baselines: {}".format(
                    full_keys - after_keys))

    def test_since_keeps_tagged_doc_bundle_unwarned(self):  # bug: since-docbundle-false-flag
        """A tagged, unchanged docs/ bundle must not be flagged 'untagged' under
        --since just because its file fell out of the --since-filtered member set."""
        with tempfile.TemporaryDirectory() as d:
            self._init_git_repo(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                   "## WHAT — Contract\n- shall do X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(d, "src.py"), "# {}: REQ-A-001\n".format("impl" + "ements"))
            # a >=50KB docs bundle, correctly tagged with generated-from
            _write(os.path.join(d, "docs", "big.html"),
                   "<!-- {}-from: REQ-A-001 -->\n".format("generated") + ("x" * 50001))
            self._commit_all(d, "baseline")
            base_ref = subprocess.run(
                ["git", "-C", d, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True).stdout.strip()
            # change only src.py; the docs bundle is untouched since base_ref
            _write(os.path.join(d, "src.py"), "# {}: REQ-A-001\n# changed\n".format("impl" + "ements"))
            self._commit_all(d, "touch-src")
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(reqs, members, rdir, update_lock=False, code_root=d, since=base_ref)
            self.assertNotIn("large docs/ HTML bundle", buf.getvalue(),
                             "an unchanged, tagged docs bundle must not be warned under --since")


class Round2Polish(unittest.TestCase):  # tested-by: REQ-MAP-007  # tested-by: REQ-PROMOTE-011
    """Round-2 LOW fixes: anchored heading detection in the last substring holdouts
    + a frontmatter status-line guard."""

    def test_labeled_acs_anchored_skips_commentary(self):  # _labeled_acs anchored (REQ-ACVERIFY-019)
        body = ("## Notes — acceptance caveats\nAC-9 not a real criterion\n"
                "## HOW — Acceptance\nAC-1 real\nAC-2 real\n")
        self.assertEqual(R._labeled_acs(body), ["AC-1", "AC-2"])

    def test_section_raw_anchored_skips_commentary(self):  # _section_raw anchored (REQ-MAP-007)
        body = ("## Notes — output format\n- not the real output\n"
                "## WHAT — Output\n- the real output line\n")
        raw = R._section_raw(body, "output")
        self.assertIn("the real output line", raw)
        self.assertNotIn("not the real output", raw)

    def test_set_status_blank_line_does_not_corrupt(self):  # _set_frontmatter_status (REQ-PROMOTE-011)
        text = "---\nid: X-1\nstatus:\nlayer: feature\n---\n\n# T\n"
        out, n = R._set_frontmatter_status(text, "confirmed")
        self.assertEqual(n, 1)
        self.assertIn("status: confirmed", out)
        self.assertIn("layer: feature", out)   # the next frontmatter key must survive intact

    def test_set_status_normal_line_unchanged_shape(self):
        out, n = R._set_frontmatter_status("---\nstatus: draft\n---\n", "confirmed")
        self.assertEqual(out, "---\nstatus: confirmed\n---\n")
        self.assertEqual(n, 1)

    def test_lint_exempt_scalar_string_is_honored(self):  # bug: lint-exempt-char-split (REQ-LINTCHECKS-025)
        # a bracketless `lint_exempt: ac-count-high` must exempt that check, not be
        # walked character-by-character (which silently exempts nothing)
        body = ("## WHAT — Contract\n- shall do x\n## HOW — Acceptance\n"
                + "".join("- AC {}\n".format(i) for i in range(1, 9)))   # 8 ACs > LINT_AC_MAX
        r = {"meta": {"status": "confirmed", "layer": "feature", "lint_exempt": "ac-count-high"},
             "body": body}
        checks = [f["check"] for f in R.lint_requirement("A-B-001", r)]
        self.assertNotIn("ac-count-high", checks)


class Site(unittest.TestCase):  # tested-by: REQ-SITE-026
    def test_remote_url_normalises_scp_and_https(self):
        self.assertEqual(R._normalise_remote("git@github.com:alxmax/Requirement-manager.git"),
                         "https://github.com/alxmax/Requirement-manager")
        self.assertEqual(R._normalise_remote("https://github.com/alxmax/Requirement-manager.git"),
                         "https://github.com/alxmax/Requirement-manager")
        self.assertEqual(R._normalise_remote("ssh://git@example.com/o/r.git"),
                         "https://example.com/o/r")
        self.assertIsNone(R._normalise_remote(""))

    def test_remote_url_with_port(self):
        """An ssh remote carrying an explicit port still yields a clickable https
        web URL with the port dropped (#14)."""
        self.assertEqual(
            R._normalise_remote("ssh://git@github.com:2222/owner/repo.git"),
            "https://github.com/owner/repo")

    def test_inject_region_refreshes_and_preserves_prose(self):
        html = "<body>\n<h1>AUTHORED</h1>\n<!--##REQMAP:NAV##-->old<!--##/REQMAP:NAV##-->\n<p>keep</p>\n</body>"
        out = R._inject_region(html, "nav", "NEW")
        self.assertIn("<!--##REQMAP:NAV##-->\nNEW\n<!--##/REQMAP:NAV##-->", out)
        self.assertIn("<h1>AUTHORED</h1>", out)
        self.assertIn("<p>keep</p>", out)
        self.assertNotIn("old", out)

    def test_inject_region_absent_inserts_after_body(self):
        html = "<body>\n<h1>hi</h1>\n</body>"
        out = R._inject_region(html, "nav", "NEW")
        self.assertIn("<!--##REQMAP:NAV##-->\nNEW\n<!--##/REQMAP:NAV##-->", out)
        self.assertLess(out.index("<body>"), out.index("REQMAP:NAV"))

    def test_extract_region_roundtrip(self):
        html = R._inject_region("<body></body>", "stats", "DATA")
        self.assertEqual(R._extract_region(html, "stats"), "DATA")
        self.assertIsNone(R._extract_region("<body></body>", "stats"))

    def test_inject_region_close_before_open_no_duplicate(self):  # bug: inject-region-malformed-marker
        """A stray close marker before the open must not trigger a duplicate block
        on injection (the close is now searched after the open)."""
        html = ("<body>\n<!--##/REQMAP:NAV##-->stray\n"
                "<!--##REQMAP:NAV##-->old<!--##/REQMAP:NAV##-->\n</body>")
        out = R._inject_region(html, "nav", "NEW")
        self.assertEqual(out.count("<!--##REQMAP:NAV##-->"), 1,
                         "must rewrite in place, not append a second region block")
        self.assertIn("NEW", out)
        self.assertNotIn("old", out)

    def test_scaffold_escapes_repo_name(self):  # bug: cmd-site-scaffold-unescaped
        """Scaffold mode must HTML-escape the repo name / URL it injects into the
        template's title and href sinks."""
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as d:
            target = os.path.join(d, "docs", "architecture.html")
            with mock.patch.object(R, "_repo_name", return_value='x"><script>bad</script>'), \
                 mock.patch.object(R, "_git_remote_web_url", return_value=None):
                with redirect_stdout(io.StringIO()):
                    R.cmd_site(R.load_requirements(os.path.join(d, "requirements")),
                               {}, root=d, attach=target, regions=["nav"])
            html = open(target, encoding="utf-8").read()
            self.assertNotIn("<script>bad</script>", html)
            self.assertIn("&lt;script&gt;", html)

    def test_render_nav_omits_absent_targets(self):
        ctx = {"repo_url": None, "map_ok": False, "diagram_rel": None}
        nav = R._render_region("nav", ctx)
        self.assertNotIn("<a", nav)
        ctx = {"repo_url": "https://github.com/o/r", "map_ok": True, "diagram_rel": "d.html"}
        nav = R._render_region("nav", ctx)
        self.assertIn('href="https://github.com/o/r"', nav)
        self.assertIn('href="map.html"', nav)
        self.assertIn('href="d.html"', nav)
        self.assertIn('target="_blank"', nav)

    def test_render_stats_counts_from_graph(self):
        data = {"nodes": [{"id": "A-1", "layer": "bus", "status": "confirmed"},
                          {"id": "B-2", "layer": "feature", "status": "confirmed"},
                          {"id": "C-3", "layer": "feature", "status": "draft"}],
                "edges": [["B-2", "A-1"]]}
        ctx = R._site_context_from_data(data, repo_url=None, map_ok=False, diagram_rel=None)
        stats = R._render_region("stats", ctx)
        self.assertIn(">3<", stats)   # 3 requirements
        self.assertIn(">2<", stats)   # 2 confirmed
        self.assertIn(R.MAP_ENGINE_VERSION, stats)

    def _seed(self, d):
        """Minimal reqs dir with one confirmed requirement so site can build map data."""
        reqs = os.path.join(d, "requirements"); os.makedirs(reqs)
        with open(os.path.join(reqs, "AREA-X-001.md"), "w", encoding="utf-8") as f:
            f.write("---\nid: AREA-X-001\nstatus: confirmed\nlayer: feature\n---\n# X\n> why\n")
        return reqs

    def test_attach_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            open(page, "w", encoding="utf-8").write("<body>\n<h1>Mine</h1>\n</body>")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(r, m, d, attach=page, regions=["nav", "stats"])
            first = open(page, encoding="utf-8").read()
            R.cmd_site(r, m, d, attach=page, regions=["nav", "stats"])
            second = open(page, encoding="utf-8").read()
            self.assertEqual(first, second)
            self.assertIn("<h1>Mine</h1>", second)

    def test_no_remote_degrades(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            open(page, "w", encoding="utf-8").write("<body></body>")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            rc = R.cmd_site(r, m, d, attach=page, regions=["nav"])
            self.assertEqual(rc, 0)
            self.assertNotIn("GitHub", open(page, encoding="utf-8").read())

    def test_scaffold_writes_full_page(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            target = os.path.join(d, "docs", "architecture.html")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(r, m, d, attach=target, regions=["nav", "stats"])
            html = open(target, encoding="utf-8").read()
            self.assertIn("<!--##REQMAP:NAV##-->", html)
            self.assertIn("<!--##REQMAP:STATS##-->", html)
            self.assertIn("<!-- author me -->", html)

    def test_init_scaffolds_site_when_absent(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            open(os.path.join(d, "a.py"), "w").write("# implements: AREA-X-001\nx = 1\n")
            R.cmd_init(os.path.join(d, "requirements"), d, no_site=False)
            page = os.path.join(d, "docs", "architecture.html")
            self.assertTrue(os.path.isfile(page))
            self.assertIn("<!--##REQMAP:NAV##-->", open(page, encoding="utf-8").read())

    def test_init_no_site_flag_skips(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            open(os.path.join(d, "a.py"), "w").write("x = 1\n")
            R.cmd_init(os.path.join(d, "requirements"), d, no_site=True)
            self.assertFalse(os.path.isfile(os.path.join(d, "docs", "architecture.html")))

    def test_map_check_flags_stale_stats_region(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d); os.makedirs(os.path.join(d, "docs"))
            page = os.path.join(d, "docs", "architecture.html")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(r, m, d, attach=page, regions=["stats"])
            data = R._build_map_data(r, m); data["repo"] = R._repo_name(d)
            self.assertEqual(R._map_check(data, reqs, d), 0)        # fresh
            cur = open(page, encoding="utf-8").read()
            tampered = cur.replace(R._extract_region(cur, "stats"), "TAMPERED")
            open(page, "w", encoding="utf-8").write(tampered)
            self.assertEqual(R._map_check(data, reqs, d), 1)        # stale stats -> exit 1

    def test_cli_site_detect_runs(self):
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            argv = ["reqmap", "site", "--detect", "--root", d]
            buf = io.StringIO()
            old = sys.argv; sys.argv = argv
            try:
                with contextlib.redirect_stdout(buf):
                    rc = R.main()
            finally:
                sys.argv = old
            self.assertEqual(rc, 0)
            self.assertIn("suggested:", buf.getvalue())

    def test_render_nav_escapes_repo_url(self):
        nav = R._render_region("nav", {"repo_url": "https://x/<script>", "map_ok": False, "diagram_rel": None})
        self.assertNotIn("<script>", nav)
        self.assertIn("&lt;script&gt;", nav)

    def test_site_diagram_ok_checks_existence(self):
        with tempfile.TemporaryDirectory() as d:
            page = os.path.join(d, "p.html")
            self.assertFalse(R._site_diagram_ok(page, "d.html"))
            open(os.path.join(d, "d.html"), "w").close()
            self.assertTrue(R._site_diagram_ok(page, "d.html"))
            self.assertFalse(R._site_diagram_ok(page, None))

    def test_engine_never_touches_excalidraw_builder(self):
        src = open(R.__file__, encoding="utf-8").read()
        self.assertNotIn("excalidraw_builder", src)   # link-only; no import/exec coupling


NL = chr(10)


class SingleWalkEquivalence(unittest.TestCase):  # tested-by: CORE-SCAN-002
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

    def test_matches_the_three_scanners_on_a_mixed_tree(self):  # verifies: CORE-SCAN-002#AC-7
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


class UntrackedMembers(unittest.TestCase):  # tested-by: REQ-TRACKED-042
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

    def test_untracked_member_is_reported(self):
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

    def test_outside_a_work_tree_fails_open(self):
        """None, not [] — the same fail-open signal _since_changed_files uses. A repo
        distributed as a tarball must not be told its every member is untracked."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "a.py"), "x=1" + chr(10))
            self.assertIsNone(R.untracked_members(d, self._members("a.py")))


class AdversarialInjection(unittest.TestCase):  # tested-by: REQ-MAP-007
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

    def test_js_line_terminators_never_reach_the_script_blob_raw(self):  # tested-by: REQ-VIEWER-007
        """U+2028/U+2029 terminate a line in JavaScript. Raw in the inlined blob they
        are a syntax error on any engine older than ES2019 - the whole viewer dies on
        one character in one requirement title."""
        out = R._inject_viewer("<html><!--REQMAP_DATA--></html>",
                               self._data("a" + self.LS + "b", ["c" + self.PS + "d"]))
        self.assertNotIn(self.LS, out)
        self.assertNotIn(self.PS, out)
        self.assertIn(chr(92) + "u2028", out)      # escaped, not dropped
        self.assertIn(chr(92) + "u2029", out)

    def test_escaped_line_terminators_still_parse_back_to_the_original(self):
        """The escape must be lossless: the viewer shows the character, not a mangle."""
        out = R._inject_viewer("<!--REQMAP_DATA-->", self._data("a" + self.LS + "b"))
        blob = out[len("<script>window.__REQMAP_DATA__="):-len(";</script>")]
        self.assertEqual(json.loads(blob)["nodes"][0]["title"], "a" + self.LS + "b")

    def test_lone_surrogate_does_not_crash_the_json_write(self):
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


class PythonFloor(unittest.TestCase):  # tested-by: REQ-PYFLOOR-040
    """The declared support floor. The predicate is tested rather than a real old
    interpreter: CI cannot install a 3.8 to watch reqmap refuse it, and a floor that is
    only asserted in prose is the failure mode this project exists to prevent."""

    def test_below_floor_names_both_versions_and_the_fix(self):
        msg = R._python_floor_error((3, 8, 10))
        self.assertIsNotNone(msg)
        self.assertIn("3.9", msg)          # required
        self.assertIn("3.8", msg)          # running
        self.assertIn("stdlib-only", msg)  # the fix: any newer interpreter, no install
        self.assertTrue(msg.isascii(), "message must survive a legacy Windows codepage")

    def test_at_and_above_floor_report_nothing(self):
        for v in [R.MIN_PYTHON, (3, 12, 0), (3, 14, 1), (4, 0, 0)]:
            self.assertIsNone(R._python_floor_error(v), v)

    def test_running_interpreter_is_at_or_above_the_declared_floor(self):
        self.assertIsNone(R._python_floor_error())

    def test_main_refuses_an_old_interpreter_with_exit_2(self):
        import contextlib
        buf = io.StringIO()
        old_argv, old_ver = sys.argv, R.sys.version_info
        sys.argv = ["reqmap", "health"]
        try:
            R.sys.version_info = (3, 8, 10, "final", 0)
            with contextlib.redirect_stdout(buf):
                rc = R.main()
        finally:
            R.sys.version_info = old_ver
            sys.argv = old_argv
        self.assertEqual(rc, 2)                        # refusal, not a command result
        self.assertIn("needs Python 3.9", buf.getvalue())

    def test_floor_matches_the_oldest_python_in_the_ci_matrix(self):
        """AC-3: the declared floor and the proven floor are one number. Skipped when
        the workflow is absent -- a seeded consumer copy has no .github/ of ours."""
        ci = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(R.__file__)))), ".github", "workflows", "ci.yml")
        if not os.path.exists(ci):
            self.skipTest("ci.yml not present (engine seeded outside this repo)")
        text = open(ci, encoding="utf-8").read()
        found = re.findall(r'"(3\.\d+)"', text)
        self.assertTrue(found, "no quoted python versions found in ci.yml")
        oldest = min(tuple(int(x) for x in v.split(".")) for v in found)
        self.assertEqual(oldest, R.MIN_PYTHON,
                         "MIN_PYTHON %r != oldest CI python %r" % (R.MIN_PYTHON, oldest))


class IntentVerbDispatch(unittest.TestCase):  # tested-by: REQ-CHECK-006
    """The renamed CLI surface: gate (report-only) + check (deprecation alias)."""

    def _run(self, *args, cwd):
        reqmap = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
        return subprocess.run([sys.executable, "-X", "utf8", reqmap, *args],
                              cwd=cwd, capture_output=True, text=True)

    def _seed(self, d):
        rdir = os.path.join(d, "requirements")
        _write(os.path.join(rdir, "REQ-A-001.md"),
               REQ.format(id="REQ-A-001", status="draft", layer="feature", extra="", title="T"))

    def test_gate_runs_report_only(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            r = self._run("gate", "--root", d, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("lock updated", r.stdout)  # gate never touches the lock

    def test_check_alias_warns_and_forwards(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            r = self._run("check", "--root", d, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("deprecated", r.stderr.lower())
            self.assertIn("gate", r.stderr.lower())


    def test_new_verbs_dispatch(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            for verb in ("draft", "dupes"):
                r = self._run(verb, "--root", d, cwd=d)
                self.assertEqual(r.returncode, 0, f"{verb}: {r.stderr}")
            # plan (cmd_candidates) always prints its extraction plan to stdout — a
            # non-empty stdout proves the branch is wired, not falling through the
            # dispatch chain to a no-op return (which would print nothing).
            r = self._run("plan", "--root", d, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(r.stdout.strip(), "plan produced no output — branch not wired")

    def test_old_verbs_are_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            for verb in ("extract", "candidates", "similar", "promote"):
                r = self._run(verb, "--root", d, cwd=d)
                self.assertEqual(r.returncode, 2, f"{verb} should be unknown")
                self.assertIn("invalid choice", r.stderr)

    def test_help_groups_everyday_and_advanced(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run("--help", cwd=d)
            self.assertEqual(r.returncode, 0)
            self.assertIn("Everyday", r.stdout)
            self.assertIn("Advanced", r.stdout)
            self.assertIn("gate", r.stdout)
            self.assertIn("sync", r.stdout)

    def test_new_from_todo_scaffolds_and_old_verb_gone(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "requirements"), exist_ok=True)
            _write(os.path.join(d, "TODO.md"), "# TODO\n\n## v1.0\n- [ ] Make widget\n")
            r = self._run("new", "--from-todo", "Make widget", "--id", "REQ-W-001",
                          "--root", d, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(d, "requirements", "REQ-W-001.md")))
            r2 = self._run("promote-todo", "Make widget", "--id", "REQ-W-002", "--root", d, cwd=d)
            self.assertEqual(r2.returncode, 2)  # old verb removed


class SyncDriftGuard(unittest.TestCase):  # tested-by: REQ-CHECK-006
    """sync must not silently re-baseline an edited confirmed contract."""

    def _confirmed_repo(self, d, body_tail=""):
        rdir = os.path.join(d, "requirements")
        _write(os.path.join(rdir, "REQ-A-001.md"),
               REQ.format(id="REQ-A-001", status="confirmed", layer="feature",
                          extra="", title="T") +
               "\n## WHAT — Contract\n- shall do the thing.\n## HOW — Acceptance\n- Given X When Y Then Z\n"
               + body_tail)
        _write(os.path.join(d, "impl.py"), "x = 1  " + tag("REQ-A-001"))
        _write(os.path.join(d, "test_impl.py"), "def test_a():\n    assert True  " + tb_tag("REQ-A-001"))
        return rdir

    def test_sync_blocks_confirmed_drift_without_flag(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = self._confirmed_repo(d)
            reqs = R.load_requirements(rdir); members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(reqs, members, rdir, update_lock=True, code_root=d)  # seed lock
            lock_before = open(R.lock_path(rdir), encoding="utf-8").read()
            # edit the contract -> drift
            self._confirmed_repo(d, body_tail="\nMore contract text that changes the hash.\n")
            reqs2 = R.load_requirements(rdir)
            with redirect_stdout(io.StringIO()):
                rc = R.cmd_check(reqs2, members, rdir, update_lock=True, code_root=d, accept_drift=False)
            self.assertEqual(rc, 1)  # blocked
            self.assertEqual(open(R.lock_path(rdir), encoding="utf-8").read(), lock_before)  # lock untouched

    def test_sync_accept_drift_advances_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = self._confirmed_repo(d)
            reqs = R.load_requirements(rdir); members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(reqs, members, rdir, update_lock=True, code_root=d)
            lock_before = open(R.lock_path(rdir), encoding="utf-8").read()
            self._confirmed_repo(d, body_tail="\nMore contract text that changes the hash.\n")
            reqs2 = R.load_requirements(rdir)
            with redirect_stdout(io.StringIO()):
                rc = R.cmd_check(reqs2, members, rdir, update_lock=True, code_root=d, accept_drift=True)
            self.assertEqual(rc, 0)
            self.assertNotEqual(open(R.lock_path(rdir), encoding="utf-8").read(), lock_before)  # advanced

    def test_json_path_reflects_blocked_lock(self):  # guard the as_json early-return
        with tempfile.TemporaryDirectory() as d:
            rdir = self._confirmed_repo(d)
            reqs = R.load_requirements(rdir); members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(reqs, members, rdir, update_lock=True, code_root=d)
            self._confirmed_repo(d, body_tail="\nMore contract text that changes the hash.\n")
            reqs2 = R.load_requirements(rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(reqs2, members, rdir, update_lock=True, code_root=d,
                                 as_json=True, accept_drift=False)
            self.assertEqual(rc, 1)  # blocked lock surfaces as non-zero even on the json path
            # the json line is printed last (after the 'lock update:' diff lines)
            self.assertEqual(json.loads(buf.getvalue().strip().splitlines()[-1])["ok"], False)


class CommandRegistry(unittest.TestCase):  # tested-by: REQ-CMDREGISTRY-033
    def test_registry_matches_argparse_choices(self):
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

    def test_generated_schema_matches_committed(self):
        generated = R._generate_schema()                 # JSON string, trailing newline
        HERE = os.path.dirname(os.path.abspath(__file__))
        committed = open(os.path.join(HERE, "..", "tool_definition.json"), encoding="utf-8").read()
        self.assertEqual(generated, committed)

    def test_schema_has_one_entry_per_user_command(self):
        import json as _j
        tools = _j.loads(R._generate_schema())
        names = {t["function"]["name"] for t in tools}
        expected = {"reqmap_" + c.replace("-", "_")
                    for c, s in R.COMMANDS.items() if not s.get("internal")}
        self.assertEqual(names, expected)

    def test_command_table_region_is_generated(self):
        table = R._generate_command_table()              # markdown table string
        _here = os.path.dirname(os.path.abspath(__file__))
        skill_path = os.path.join(_here, "..", "skills", "requirement-manager", "SKILL.universal.md")
        text = open(skill_path, encoding="utf-8").read()
        start = text.index("<!--##REQMAP:COMMANDS##-->") + len("<!--##REQMAP:COMMANDS##-->")
        end = text.index("<!--##/REQMAP:COMMANDS##-->")
        self.assertEqual(text[start:end].strip(), table.strip())

    def test_integration_fresh_when_committed(self):
        HERE = os.path.dirname(os.path.abspath(__file__))
        plugin_root = os.path.join(HERE, "..")          # plugin/
        self.assertEqual(R._check_integration_fresh(plugin_root), [])

    def test_check_integration_fresh_detects_stale_schema(self):
        import tempfile, shutil
        HERE = os.path.dirname(os.path.abspath(__file__))
        with tempfile.TemporaryDirectory() as d:
            dst = os.path.join(d, "plugin")
            shutil.copytree(os.path.join(HERE, ".."), dst)
            with open(os.path.join(dst, "tool_definition.json"), "w", encoding="utf-8") as f:
                f.write("[]\n")                          # deliberately stale
            stale = R._check_integration_fresh(dst)
            self.assertIn("tool_definition.json", stale)

    def test_gate_json_also_fails_on_stale_artifact(self):
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


# ---------------------------------------------------------------------------
# Regression tests for the 2026-06-28 multi-agent (consilium) bug hunt — 15 fixes.
# ---------------------------------------------------------------------------
class BugHuntParsing(unittest.TestCase):  # tested-by: CORE-PARSE-001
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


class BugHuntScanning(unittest.TestCase):  # tested-by: REQ-ACVERIFY-019
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


class BugHuntGateDrift(unittest.TestCase):  # tested-by: REQ-CHECK-006  # tested-by: CORE-DRIFT-003
    def test_version_key_orders_double_digit_suffix(self):
        self.assertGreater(R._ver_key("2026-06-03.10"), R._ver_key("2026-06-03.9"))
        self.assertGreater(R._ver_key("2026-06-04"), R._ver_key("2026-06-03.9"))
        self.assertGreater(R._ver_key("2026-06-03.2"), R._ver_key("2026-06-03"))

    def test_go_lowercase_func_is_not_a_test(self):
        self.assertIsNone(R._DEF_TEST_RE.search("func testHelper() {"))
        self.assertIsNotNone(R._DEF_TEST_RE.search("func TestThing(t *testing.T) {"))
        self.assertIsNotNone(R._DEF_TEST_RE.search("def test_x():"))
        self.assertIsNotNone(R._DEF_TEST_RE.search("    function testFoo() {"))

    def test_binding_hash_detects_cross_section_move(self):
        a = "## WHAT — Contract\n- A\n## HOW — Acceptance\n- B\n- C\n"
        b = "## WHAT — Contract\n- A\n- B\n## HOW — Acceptance\n- C\n"
        self.assertNotEqual(R.binding_hash(a), R.binding_hash(b))

    def test_binding_hash_detects_indent_change(self):
        a = "## WHAT — Contract\n- A\n  nested\n"
        b = "## WHAT — Contract\n- A\nnested\n"
        self.assertNotEqual(R.binding_hash(a), R.binding_hash(b))


class CheckAliasDriftGuard(unittest.TestCase):  # tested-by: REQ-CHECK-006
    """The deprecated `check --update-lock` must enforce the same confirmed-drift
    guard as `sync`, and must not regenerate the map when the gate fails."""

    def _run(self, *args, cwd):
        reqmap = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
        return subprocess.run([sys.executable, "-X", "utf8", reqmap, *args],
                              cwd=cwd, capture_output=True, text=True)

    def _confirmed_repo(self, d, clause):
        rdir = os.path.join(d, "requirements")
        _write(os.path.join(rdir, "REQ-A-001.md"),
               REQ.format(id="REQ-A-001", status="confirmed", layer="feature", extra="", title="T")
               + "\n## WHAT — Contract\n- %s\n## HOW — Acceptance\n- Given X When Y Then Z\n" % clause)
        _write(os.path.join(d, "impl.py"), "x = 1  " + tag("REQ-A-001"))
        _write(os.path.join(d, "test_impl.py"),
               "def test_a():\n    assert True  " + tb_tag("REQ-A-001"))
        return rdir

    def test_check_update_lock_blocks_confirmed_drift(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = self._confirmed_repo(d, "shall do the thing")
            self._run("sync", "--root", d, cwd=d)                      # seed the baseline
            lock_before = open(R.lock_path(rdir), encoding="utf-8").read()
            self._confirmed_repo(d, "shall do the thing DIFFERENTLY")  # drift the contract
            r = self._run("check", "--update-lock", "--root", d, cwd=d)
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(open(R.lock_path(rdir), encoding="utf-8").read(), lock_before)

    def test_check_update_lock_skips_map_on_gate_error(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="draft", layer="feature", extra="", title="T"))
            _write(os.path.join(d, "impl.py"), "x = 1  " + tag("NOPE-X-001"))  # dangling -> gate error
            r = self._run("check", "--update-lock", "--root", d, cwd=d)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(os.path.exists(os.path.join(rdir, "_map.json")),
                             "map must not be regenerated when the gate errors")


class BugHuntMutateAnalyze(unittest.TestCase):  # tested-by: REQ-PROMOTE-011  # tested-by: REQ-PROMOTE-TODO-001  # tested-by: REQ-NEXT-013
    def test_set_status_empty_value_with_comment_not_corrupted(self):
        out, n = R._set_frontmatter_status(
            "---\nid: X\nstatus:  # deprecated hint\nlayer: bus\n---\nbody\n", "confirmed")
        self.assertEqual(n, 1)
        self.assertIn("status: confirmed", out)
        self.assertNotIn("confirmed deprecated", out)   # value+leaked text must not glue
        self.assertNotIn("confirmed#", out)
        self.assertIn("\nbody\n", out)

    def test_mark_todo_done_unreadable_root_falls_through_to_parent(self):
        with tempfile.TemporaryDirectory() as d:
            root = os.path.join(d, "plugin"); os.makedirs(root)
            root_todo = os.path.join(root, "TODO.md")
            _write(root_todo, "# TODO\n- [ ] Widget\n")
            parent_todo = os.path.join(d, "TODO.md")
            _write(parent_todo, "# TODO\n- [ ] Widget\n")
            real_open = open
            def fake_open(file, *a, **k):
                if os.path.abspath(file) == os.path.abspath(root_todo):
                    raise OSError("simulated unreadable")
                return real_open(file, *a, **k)
            with mock.patch("builtins.open", side_effect=fake_open):
                changed = R._mark_todo_done(root, "Widget")
            self.assertEqual(changed, 1)
            self.assertIn("[x] Widget", open(parent_todo, encoding="utf-8").read())

    def test_next_granularity_counts_labeled_acs(self):
        # 5 labelled AC-N criteria (no bullet dashes): _bullets saw 0 and suppressed
        # the advisory; _count_ac sees 5. Members are implements-only so the req has a
        # pending ('untested') signal and execution reaches the granularity block.
        body = "# T\n\n## HOW — Acceptance\n" + "".join(
            "AC-%d: criterion %d\n" % (i, i) for i in range(1, 6))
        reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed", "layer": "feature"}, "body": body}}
        members = {"CORE-FOO-001": [("implements", "x.py", 1)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_next(reqs, members)
        self.assertIn("Granularity", buf.getvalue())

    def test_map_data_verify_intent_heading_consistency(self):
        body = "# T\n\n## WHAT — Contract\n- c\n\n## WHAT — Verify roadmap\n- someday item\n"
        reqs = {"CORE-FOO-001": {"meta": {"status": "confirmed", "layer": "feature"},
                                 "body": body, "path": "x"}}
        members = {"CORE-FOO-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        data = R._build_map_data(reqs, members)
        node = next(n for n in data["nodes"] if n["id"] == "CORE-FOO-001")
        self.assertNotIn("unverified-intent", [r["signal"] for r in node["risks"]])


class BugHuntRender(unittest.TestCase):  # tested-by: REQ-MAP-007  # tested-by: REQ-INIT-012
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

    def test_section_includes_content_after_fenced_heading(self):
        body = "## WHAT — Contract\nfirst clause\n```yaml\n## not a heading\nk: v\n```\nlast clause\n"
        self.assertIn("last clause", R._section(body, "contract"))

    def test_bullets_include_after_fenced_heading(self):
        body = "## WHAT — Contract\n- one\n```\n## nope\n```\n- two\n"
        self.assertIn("two", R._bullets(body, "contract"))


class BugHuntSince(unittest.TestCase):  # tested-by: REQ-CHECK-006
    def test_since_decodes_non_ascii_paths(self):
        with tempfile.TemporaryDirectory() as d:
            for cfg in (["init", d],
                        ["-C", d, "config", "user.email", "t@t.com"],
                        ["-C", d, "config", "user.name", "T"],
                        ["-C", d, "config", "core.quotepath", "true"]):
                subprocess.run(["git", *cfg], check=True, capture_output=True)
            fp = os.path.join(d, "café.py")
            _write(fp, "x=1\n")
            subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
            subprocess.run(["git", "-C", d, "commit", "-m", "init"], check=True, capture_output=True)
            base = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
            _write(fp, "x=2\n")
            subprocess.run(["git", "-C", d, "add", "-A"], check=True, capture_output=True)
            subprocess.run(["git", "-C", d, "commit", "-m", "change"], check=True, capture_output=True)
            files = R._since_changed_files(base, d)
            self.assertIsNotNone(files)
            self.assertIn(R._path_key(fp), files)   # not abspath: 8.3 short names



class RoadmapSignals(unittest.TestCase):  # tested-by: REQ-ROADMAP-038
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
                R.cmd_health(reqs, members, reqs_dir, code_root=d, as_json=True)
            return json.loads(buf.getvalue())

    def test_behind_signal_when_the_roadmap_lags(self):  # verifies: REQ-ROADMAP-038#AC-1
        data = self._health("# TODO\n\n## v2.8\n- [ ] later | lane: feature\n", req_ms="v2.13")
        self.assertEqual(data["roadmap_behind"], {"todo": "v2.8", "requirements": "v2.13"})

    def test_no_behind_signal_when_the_roadmap_is_current(self):  # verifies: REQ-ROADMAP-038#AC-2
        data = self._health("# TODO\n\n## v2.16\n- [x] shipped | lane: feature\n", req_ms="v2.13")
        self.assertNotIn("roadmap_behind", data)

    def test_unversioned_heading_is_listed(self):  # verifies: REQ-ROADMAP-038#AC-3
        todo = "# TODO\n\n## v2.16\n- [x] a | lane: feature\n\n## Deferred work\n- [ ] b | lane: feature\n"
        data = self._health(todo, req_ms="v2.13")
        self.assertEqual(data["roadmap_unversioned_headings"], ["Deferred work"])

    def test_no_todo_file_means_no_roadmap_signals(self):  # verifies: REQ-ROADMAP-038#AC-4
        data = self._health(None)
        self.assertNotIn("roadmap_behind", data)
        self.assertNotIn("roadmap_unversioned_headings", data)

    def test_versions_compare_numerically_not_as_strings(self):  # verifies: REQ-ROADMAP-038#AC-5
        self.assertGreater(R._version_key("v2.10"), R._version_key("v2.9"))
        self.assertLess("v2.10", "v2.9")   # the string compare this guards against


class ViewerDataSync(unittest.TestCase):  # tested-by: REQ-VIEWER-007
    def _fixture_data_js(self, path, entries):
        body = "const BAKED = [\n" + "".join(
            '  {{ id:"{id}", contract:[{contract}] }},\n'.format(
                id=e["id"], contract=",".join('"{}"'.format(c) for c in e["contract"]))
            for e in entries
        ) + "];\n"
        _write(path, body)

    def test_demo_only_entry_is_not_compared(self):
        """The fixture INVENTS two states the registry cannot contain - a fake orphan and
        a fake deprecated capability - so the viewer's Risk and Problems tabs have
        something to show with no engine present. Comparing those against the registry
        reported permanent drift: the check crying wolf about data doing its job."""
        with tempfile.TemporaryDirectory() as d:
            data_js = os.path.join(d, "data.js")
            _write(data_js, 'const BAKED = ['
                   + chr(10) + '  { id:"REAL-ONE-001", contract:["Alpha does X."] },'
                   + chr(10) + '  { id:"FAKE-DEMO-999", demoOnly:true, contract:["Invented."] },'
                   + chr(10) + '];' + chr(10))
            drift = R.check_viewer_data_sync(data_js, [{"id": "REAL-ONE-001",
                                                       "contract": ["Alpha does X."]}])
            self.assertEqual(drift, [])

    def test_unmarked_missing_id_is_still_reported(self):
        """The marker must not blunt the real signal: an entry that CLAIMS to mirror a
        requirement, whose id no longer exists (renamed out from under the fixture),
        still counts as drift."""
        with tempfile.TemporaryDirectory() as d:
            data_js = os.path.join(d, "data.js")
            self._fixture_data_js(data_js, [{"id": "GONE-AWAY-001", "contract": ["X."]}])
            self.assertEqual(R.check_viewer_data_sync(data_js, []), ["GONE-AWAY-001"])

    def test_repo_fixture_is_in_sync_with_its_own_registry(self):
        """The end-to-end assertion the two tests above only approximate: THIS repo's
        data.js against THIS repo's committed _map.json. Skipped where either is absent
        (a seeded consumer copy has neither)."""
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(R.__file__))))
        data_js = os.path.join(root, "app", "src", "lib", "data.js")
        map_json = os.path.join(root, "plugin", "requirements", "_map.json")
        if not (os.path.exists(data_js) and os.path.exists(map_json)):
            self.skipTest("not running inside the requirement-manager repo")
        with open(map_json, encoding="utf-8") as f:
            nodes = json.load(f)["nodes"]
        self.assertEqual(R.check_viewer_data_sync(data_js, nodes), [])

    def test_matching_data_js_reports_no_drift(self):
        with tempfile.TemporaryDirectory() as d:
            data_js = os.path.join(d, "data.js")
            self._fixture_data_js(data_js, [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}])
            map_nodes = [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}]
            drift = R.check_viewer_data_sync(data_js, map_nodes)
            self.assertEqual(drift, [])

    def test_diverged_contract_text_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            data_js = os.path.join(d, "data.js")
            self._fixture_data_js(data_js, [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}])
            map_nodes = [{"id": "FOO-BAR-001", "contract": ["It shall do Y instead."]}]
            drift = R.check_viewer_data_sync(data_js, map_nodes)
            self.assertEqual(drift, ["FOO-BAR-001"])

    def test_missing_baked_id_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            data_js = os.path.join(d, "data.js")
            self._fixture_data_js(data_js, [{"id": "FOO-BAR-001", "contract": ["It shall do X."]}])
            map_nodes = []  # the requirement was deleted/renamed in the registry
            drift = R.check_viewer_data_sync(data_js, map_nodes)
            self.assertEqual(drift, ["FOO-BAR-001"])

    def test_missing_data_js_file_returns_none(self):
        # fail-open: no viewer checked out (e.g. a shallow consumer clone) is not an error
        self.assertIsNone(R.check_viewer_data_sync("/no/such/data.js", []))

    def test_matching_data_js_with_bracket_in_contract_text_reports_no_drift(self):
        # regression: a naive non-greedy `contract:\[(.*?)\]` regex stops at the FIRST
        # ']', truncating any bullet whose own text contains a bracket -- and this
        # repo's real contracts do (e.g. describing `[a, b]` syntax). A bracket-aware
        # scanner must find the array's TRUE close, not the first stray ']'.
        with tempfile.TemporaryDirectory() as d:
            data_js = os.path.join(d, "data.js")
            bullet = 'Accepts an inline `[a, b]` list and a `{k: v}` block.'
            self._fixture_data_js(data_js, [{"id": "FOO-BAR-001", "contract": [bullet]}])
            map_nodes = [{"id": "FOO-BAR-001", "contract": [bullet]}]
            drift = R.check_viewer_data_sync(data_js, map_nodes)
            self.assertEqual(drift, [])

    def test_non_utf8_data_js_returns_none(self):
        # regression: only OSError was caught; a non-UTF-8 file raises UnicodeDecodeError
        # (a ValueError subclass), which was uncaught and crashed `gate` outright instead
        # of degrading to a warning.
        with tempfile.TemporaryDirectory() as d:
            data_js = os.path.join(d, "data.js")
            with open(data_js, "wb") as f:
                f.write(b"\xff\xfe garbage, not valid utf-8")
            self.assertIsNone(R.check_viewer_data_sync(data_js, []))

# Entry point stays LAST on purpose. It used to sit mid-file, above
# RoadmapSignals and ViewerDataSync, so `python test_reqmap.py` ran
# unittest.main() before those classes were even defined: 478 tests
# collected instead of 494, 16 silently skipped in the invocation
# CLAUDE.md documents. CI runs `-m unittest`, which imports the whole
# module first, so CI never saw the gap.
if __name__ == "__main__":
    unittest.main(verbosity=2)
