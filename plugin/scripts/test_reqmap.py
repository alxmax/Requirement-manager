"""Regression tests for the bugs found by the 2026-06-02 bug-hunt. Stdlib only.

Run: python -m unittest test_reqmap   (from plugin/scripts/)
"""
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


class Gate(unittest.TestCase):  # tested-by: REQ-DRIFT-841  # tested-by: REQ-DRIFT-842
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

    def test_bare_scalar_depends_on_no_percharacter_errors(self):  # bug #5  tested-by: ARCH-CHECK-006
        files = {
            "AREA-FOO-001.md": REQ.format(id="AREA-FOO-001", status="baseline", layer="feature",
                                          extra="depends_on: AREA-BAR-002\n", title="Foo"),
            "AREA-BAR-002.md": REQ.format(id="AREA-BAR-002", status="baseline", layer="bus", extra="", title="Bar"),
        }
        code, out = self._check(files)
        self.assertNotIn("depends_on missing", out)
        self.assertEqual(code, 0)

    def test_corrupt_lock_does_not_crash(self):  # bug #6  tested-by: ARCH-DRIFT-003  # verifies: ARCH-DRIFT-003#CASE-3  # verifies: REQ-DRIFT-842#CASE-2
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

    def test_update_lock_missing_dir_no_crash(self):  # bug #13  # verifies: REQ-DRIFT-842#CASE-3
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "does", "not", "exist")
            R.save_lock(missing, {"A": "b"})  # must not raise
            self.assertTrue(os.path.exists(os.path.join(missing, "_reqlock.json")))

    def test_save_then_load_roundtrip(self):  # verifies: ARCH-DRIFT-003#CASE-4  # verifies: REQ-DRIFT-842#CASE-1
        with tempfile.TemporaryDirectory() as d:
            R.save_lock(d, {"A-B-001": "abc123def456", "C-D-002": "0123456789ab"})
            self.assertEqual(R.load_lock(d), {"A-B-001": "abc123def456", "C-D-002": "0123456789ab"})

    def test_binding_hash_tracks_contract_not_commentary(self):  # tested-by: ARCH-DRIFT-003  # verifies: ARCH-DRIFT-003#CASE-1  # verifies: ARCH-DRIFT-003#CASE-2  # verifies: REQ-DRIFT-841#CASE-3
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

    def test_dashless_normative_heading_is_hashed_and_detected(self):  # tested-by: ARCH-DRIFT-003
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

    def test_has_section_anchored_to_label(self):  # tested-by: ARCH-CHECK-006
        # a commentary heading that merely mentions the keyword is NOT the section
        self.assertFalse(R._has_section("# T\n\n## Notes — contract caveats\n- x\n", "contract"))
        # canonical, bare, and dash-less label forms all count
        for h in ("## WHAT — Contract (normative)", "## Contract", "## WHAT Contract"):
            self.assertTrue(R._has_section("# T\n\n" + h + "\n- x\n", "contract"), h)

    def test_drift_warn_names_member_locations(self):  # tested-by: ARCH-CHECK-006  # verifies: ARCH-CHECK-006#CASE-4  # verifies: REQ-CHECK-829#CASE-1  # verifies: REQ-CHECK-829#CASE-2
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
                R.cmd_check(R.Workspace(reqs, members, d), False)
            out = buf.getvalue()
            self.assertIn("DRIFT", out)
            self.assertIn("re-check 1 member", out)   # actionable count
            self.assertIn("mod.py:1", out)            # names the member location

    def test_confirmed_missing_contract_section_warns(self):  # tested-by: ARCH-CHECK-006  # verifies: ARCH-CHECK-006#CASE-7  # verifies: REQ-CHECK-829#CASE-6
        files = {
            "AREA-FOO-001.md": (
                "---\nid: AREA-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n"
                "# Foo\n\n"
                "## HOW — Acceptance (= tests)\n- Given X When Y Then Z\n"
            ),
            "src.py": tag("AREA-FOO-001") + "\n" + tb_tag("AREA-FOO-001") + "\n",
        }
        code, out = self._check(files)
        self.assertIn("missing '## Description'", out)
        self.assertEqual(code, 0)  # WARN, not error

    def test_confirmed_missing_acceptance_section_warns(self):  # tested-by: ARCH-CHECK-006  # verifies: ARCH-CHECK-006#CASE-8  # verifies: REQ-CHECK-829#CASE-7
        files = {
            "AREA-FOO-001.md": (
                "---\nid: AREA-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n"
                "# Foo\n\n"
                "## WHAT — Contract (normative)\n- It shall do X\n"
            ),
            "src.py": tag("AREA-FOO-001") + "\n" + tb_tag("AREA-FOO-001") + "\n",
        }
        code, out = self._check(files)
        self.assertIn("missing '## Cases'", out)
        self.assertEqual(code, 0)  # WARN, not error

    def test_confirmed_with_both_sections_no_section_lint_warn(self):  # tested-by: ARCH-CHECK-006  # verifies: ARCH-CHECK-006#CASE-9
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
        # the fixture is written in the LEGACY form, and must still satisfy both checks
        self.assertNotIn("missing '## Description'", out)
        self.assertNotIn("missing '## Cases'", out)

    def test_need_without_validation_warns_once_the_repo_opts_in(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-CHECK-831#CASE-3  # verifies: REQ-TRACE-935#CASE-4  # tested-by: REQ-VLEVEL-946  # verifies: REQ-VLEVEL-946#CASE-1
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

    def test_need_without_validation_is_silent_until_the_repo_opts_in(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-VLEVEL-946#CASE-2
        # No validated-against tag anywhere: the rule must not fire at all, so a repo
        # that never adopts the role sees no new warnings.
        files = {
            "NEED-B-002.md": REQ.format(id="NEED-B-002", status="confirmed", layer="need",
                                        extra="", title="Unvalidated need"),
        }
        _, out = self._check(files)
        self.assertNotIn("validated-against", out)

    def test_bus_verified_only_at_system_level_warns(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-CHECK-831#CASE-4  # verifies: REQ-VLEVEL-946#CASE-3
        files = {
            "CORE-X-001.md": REQ.format(id="CORE-X-001", status="confirmed", layer="bus",
                                        extra="", title="Foundation"),
            "impl.py": "# implements: CORE-X-001\ndef go():\n    return 1\n",
            "t_sys.py": "# tested-by: CORE-X-001 @system\ndef test_e2e():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertIn("@system", out)

    def test_bus_with_a_lower_level_link_is_silent(self):  # tested-by: ARCH-VLEVEL-037 @unit
        files = {
            "CORE-X-001.md": REQ.format(id="CORE-X-001", status="confirmed", layer="bus",
                                        extra="", title="Foundation"),
            "impl.py": "# implements: CORE-X-001\ndef go():\n    return 1\n",
            "t_sys.py": "# tested-by: CORE-X-001 @system\ndef test_e2e():\n    pass\n",
            "t_unit.py": "# tested-by: CORE-X-001 @unit\ndef test_unit():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertNotIn("verified only at @system", out)

    def test_bus_with_no_levelled_link_is_never_judged(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-VLEVEL-946#CASE-4
        # opt-in per requirement: an unlevelled tested-by link is not evidence either way
        files = {
            "CORE-X-001.md": REQ.format(id="CORE-X-001", status="confirmed", layer="bus",
                                        extra="", title="Foundation"),
            "impl.py": "# implements: CORE-X-001\ndef go():\n    return 1\n",
            "t_plain.py": "# tested-by: CORE-X-001\ndef test_x():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertNotIn("verified only at @system", out)

    def test_feature_verified_only_at_system_level_is_silent(self):  # tested-by: ARCH-VLEVEL-037 @unit  # verifies: REQ-VLEVEL-946#CASE-5
        # rule 2 is about foundation code only — a feature may legitimately be end-to-end
        files = {
            "REQ-X-001.md": REQ.format(id="REQ-X-001", status="confirmed", layer="feature",
                                       extra="", title="Feature"),
            "impl.py": "# implements: REQ-X-001\ndef go():\n    return 1\n",
            "t_sys.py": "# tested-by: REQ-X-001 @system\ndef test_e2e():\n    pass\n",
        }
        _, out = self._check(files)
        self.assertNotIn("verified only at @system", out)


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


class DocBundle(unittest.TestCase):  # tested-by: ARCH-DOCBUNDLE-026  # tested-by: REQ-DOCBUNDLE-840
    """A large docs/ HTML doc with no generated-from lineage is the doc-sync blind
    spot — it drifts from the requirements it derives from with nothing linking them."""
    def _big(self, n=None):
        return "<html>" + "x" * (R.DOC_BUNDLE_MIN_BYTES + 10 if n is None else n) + "</html>"

    # generated-from comment built at runtime so THIS .py source registers no phantom member
    def _gtag(self, cap):
        return "<!-- {}-from: {} -->\n".format("generated", cap)

    def test_large_untagged_docs_html_is_flagged(self):  # verifies: ARCH-DOCBUNDLE-026#CASE-1  # verifies: REQ-DOCBUNDLE-840#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), self._big())
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), ["docs/arch.html"])

    def test_small_docs_html_not_flagged(self):  # verifies: ARCH-DOCBUNDLE-026#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "small.html"), "<html>tiny</html>")
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_tagged_large_docs_html_not_flagged(self):  # verifies: ARCH-DOCBUNDLE-026#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), self._gtag("REQ-DOC-001") + self._big())
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_engine_outputs_and_nondocs_excluded(self):  # verifies: ARCH-DOCBUNDLE-026#CASE-4  # verifies: REQ-DOCBUNDLE-840#CASE-2  # verifies: REQ-DOCBUNDLE-840#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "map.html"), self._big())   # engine's published viewer
            _write(os.path.join(d, "docs", "_x.html"), self._big())    # _-prefixed generated output
            _write(os.path.join(d, "top.html"), self._big())           # not under docs/
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_reqmapignore_suppresses(self):  # verifies: ARCH-DOCBUNDLE-026#CASE-5  # verifies: REQ-DOCBUNDLE-840#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "poster.html"), self._big())
            _write(os.path.join(d, ".reqmapignore"), "docs/poster.html\n")
            members = R.scan_members(d, None)
            self.assertEqual(R.untagged_doc_bundles(d, members), [])

    def test_gate_surfaces_the_warn(self):  # verifies: ARCH-DOCBUNDLE-026#CASE-6
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"), self._big())
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertIn("docs/arch.html", buf.getvalue())
            self.assertIn("generated-from", buf.getvalue())


class MemberDrift(unittest.TestCase):  # tested-by: ARCH-MEMBERDRIFT-027  # tested-by: REQ-MEMBERDRIFT-879  # tested-by: REQ-MEMBERDRIFT-880
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

    def test_only_mono_requirement_files_recorded(self):  # verifies: ARCH-MEMBERDRIFT-027#CASE-1  # verifies: REQ-MEMBERDRIFT-879#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "solo.py"), tag("REQ-AA-001") + "\n")
            _write(os.path.join(d, "shared.py"), tag("REQ-BB-001") + "\n" + tag("REQ-CC-001") + "\n")
            mh = R.compute_member_hashes(d, R.scan_members(d, d))
            self.assertIn("solo.py", mh.get("REQ-AA-001", {}))
            self.assertNotIn("REQ-BB-001", mh)   # shared.py belongs to two requirements
            self.assertNotIn("REQ-CC-001", mh)

    def test_file_sha_normalizes_line_endings(self):  # CRLF (Windows) == LF (CI)  # verifies: ARCH-MEMBERDRIFT-027#CASE-8  # verifies: REQ-MEMBERDRIFT-879#CASE-4
        with tempfile.TemporaryDirectory() as d:
            lf = os.path.join(d, "lf.py")
            crlf = os.path.join(d, "crlf.py")
            with open(lf, "wb") as f:
                f.write(b"def run():\n    return 0\n")
            with open(crlf, "wb") as f:
                f.write(b"def run():\r\n    return 0\r\n")
            self.assertEqual(R._file_sha(lf), R._file_sha(crlf))

    def test_memberlock_roundtrip_and_failopen(self):  # verifies: ARCH-MEMBERDRIFT-027#CASE-2  # verifies: REQ-MEMBERDRIFT-879#CASE-1  # verifies: REQ-MEMBERDRIFT-879#CASE-2
        with tempfile.TemporaryDirectory() as d:
            R.save_memberlock(d, {"REQ-AA-001": {"solo.py": "abc"}})
            self.assertEqual(R.load_memberlock(d), {"REQ-AA-001": {"solo.py": "abc"}})
            _write(os.path.join(d, "_memberlock.json"),
                   json.dumps({"_schema": 999, "members": {"X": {}}}))   # newer schema → degrade
            self.assertEqual(R.load_memberlock(d), {})
            _write(os.path.join(d, "_memberlock.json"), "{ broken")
            self.assertEqual(R.load_memberlock(d), {})

    def test_changed_member_unchanged_contract_is_flagged(self):  # verifies: ARCH-MEMBERDRIFT-027#CASE-3  # verifies: REQ-MEMBERDRIFT-880#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            memberlock = R.compute_member_hashes(d, members)
            self._member(d, "CHANGED = 2")     # edit the member, leave the requirement alone
            self.assertEqual(R.member_drift(reqs, members, lock, memberlock, d),
                             [("REQ-MD-001", "src/foo.py")])

    def test_contract_also_changed_not_flagged(self):  # verifies: ARCH-MEMBERDRIFT-027#CASE-4  # verifies: REQ-MEMBERDRIFT-880#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            memberlock = R.compute_member_hashes(d, members)
            self._member(d, "CHANGED = 2")
            lock = {"REQ-MD-001": "stale-hash"}   # contract drifted too → forward drift owns it
            self.assertEqual(R.member_drift(reqs, members, lock, memberlock, d), [])

    def test_non_confirmed_not_flagged(self):  # verifies: ARCH-MEMBERDRIFT-027#CASE-5  # verifies: REQ-MEMBERDRIFT-880#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._req(d, status="baseline"); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            memberlock = R.compute_member_hashes(d, members)
            self._member(d, "CHANGED = 2")
            self.assertEqual(R.member_drift(reqs, members, lock, memberlock, d), [])

    def test_new_member_without_baseline_not_flagged(self):  # verifies: ARCH-MEMBERDRIFT-027#CASE-6  # verifies: REQ-MEMBERDRIFT-880#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs, members, lock = self._state(d)
            self._member(d, "CHANGED = 2")
            self.assertEqual(R.member_drift(reqs, members, lock, {}, d), [])   # no baseline yet

    def test_gate_warns_and_strict_promotes(self):  # verifies: ARCH-MEMBERDRIFT-027#CASE-7  # verifies: REQ-MEMBERDRIFT-880#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._req(d); self._member(d, "ORIGINAL = 1")
            reqs = R.load_requirements(d); members = R.scan_members(d, d)
            R.cmd_check(R.Workspace(reqs, members, d, d), True)   # baseline both locks
            self._member(d, "CHANGED = 2")
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertIn("MEMBER DRIFT", buf.getvalue())
            self.assertEqual(code, 0)                          # warn-only by default
            with redirect_stdout(io.StringIO()):
                strict_code = R.cmd_check(R.Workspace(reqs, members, d, d), False, True)
            self.assertEqual(strict_code, 1)                   # --strict-promotable


_BIG_PY = "".join("x{0} = {0}\n".format(i) for i in range(200))   # >= ORPHAN_CODE_MIN_LOC lines


class OrphanCode(unittest.TestCase):  # tested-by: ARCH-ORPHANCODE-034  # tested-by: REQ-ORPHANCODE-888
    def test_large_untagged_program_file_reported(self):  # verifies: ARCH-ORPHANCODE-034#CASE-1  # verifies: REQ-ORPHANCODE-888#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "mod.py"), _BIG_PY)
            self.assertEqual(R.orphan_code_files(d, set()), ["mod.py"])

    def test_small_untagged_not_reported(self):  # verifies: ARCH-ORPHANCODE-034#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "mod.py"), "x = 1\ny = 2\n")
            self.assertEqual(R.orphan_code_files(d, set()), [])

    def test_covered_file_not_reported(self):  # verifies: ARCH-ORPHANCODE-034#CASE-3  # verifies: REQ-ORPHANCODE-888#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "mod.py"), _BIG_PY)
            self.assertEqual(R.orphan_code_files(d, {"mod.py"}), [])

    def test_non_program_ext_not_reported(self):  # verifies: ARCH-ORPHANCODE-034#CASE-4  # verifies: REQ-ORPHANCODE-888#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "big.txt.md"), _BIG_PY)
            _write(os.path.join(d, "big.html"), _BIG_PY)
            self.assertEqual(R.orphan_code_files(d, set()), [])

    def test_reqmapignore_suppresses(self):  # verifies: ARCH-ORPHANCODE-034#CASE-5  # verifies: REQ-ORPHANCODE-888#CASE-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "vendor", "big.py"), _BIG_PY)
            _write(os.path.join(d, ".reqmapignore"), "vendor/*\n")
            self.assertEqual(R.orphan_code_files(d, set()), [])

    def test_gate_warns_and_exit_unchanged_even_strict(self):  # verifies: ARCH-ORPHANCODE-034#CASE-6  # verifies: REQ-ORPHANCODE-888#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"), REQ.format(
                id="A-FOO-001", status="baseline", layer="feature", extra="", title="T"))
            _write(os.path.join(d, "orphan.py"), _BIG_PY)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertIn("orphan.py", buf.getvalue())
            self.assertIn("no membership tag", buf.getvalue())
            self.assertEqual(code, 0)
            with redirect_stdout(io.StringIO()):   # never strict-promoted (advisory ceiling)
                strict_code = R.cmd_check(R.Workspace(reqs, members, d, d), False, True)
            self.assertEqual(strict_code, 0)

    def test_verifies_tag_counts_as_covered_at_gate(self):  # verifies: ARCH-ORPHANCODE-034#CASE-3
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
                R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertNotIn("test_mod.py", buf.getvalue())


class DriftDependents(unittest.TestCase):  # tested-by: ARCH-DRIFTIMPACT-035  # tested-by: REQ-DRIFTIMPACT-843
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
            R.cmd_check(R.Workspace(reqs, members, d, d), False)
        return buf.getvalue()

    def test_dependent_named_on_drift(self):  # verifies: ARCH-DRIFTIMPACT-035#CASE-1  # verifies: REQ-DRIFTIMPACT-843#CASE-1
        with tempfile.TemporaryDirectory() as d:
            out = self._gate(d, ["AREA-BAR-002"])
            self.assertIn("DRIFT", out)
            self.assertIn("review dependent(s): AREA-BAR-002", out)

    def test_no_dependents_no_clause(self):  # verifies: ARCH-DRIFTIMPACT-035#CASE-2  # verifies: REQ-DRIFTIMPACT-843#CASE-4
        with tempfile.TemporaryDirectory() as d:
            out = self._gate(d, [])
            self.assertIn("DRIFT", out)
            self.assertNotIn("review dependent", out)

    def test_two_dependents_sorted(self):  # verifies: ARCH-DRIFTIMPACT-035#CASE-3  # verifies: REQ-DRIFTIMPACT-843#CASE-2
        with tempfile.TemporaryDirectory() as d:
            out = self._gate(d, ["AREA-BAZ-003", "AREA-BAR-002"])   # written unsorted
            self.assertIn("review dependent(s): AREA-BAR-002, AREA-BAZ-003", out)


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


class Rendering(unittest.TestCase):  # tested-by: ARCH-MAPDIAGRAMS-055  # tested-by: REQ-MAPDIAGRAMS-874, REQ-MAPDIAGRAMS-875, REQ-MAPDIAGRAMS-876, REQ-MAPDIAGRAMS-877, REQ-MAPDIAGRAMS-878
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

    def test_system_map_boxes_multinode_area_and_collapses_singletons(self):  # verifies: REQ-MAPDIAGRAMS-876#CASE-2  # verifies: ARCH-MAPDIAGRAMS-055#CASE-3
        data = {"nodes": [self._node("BUS-PATHS-001", layer="bus"),
                          self._node("BUS-RULES-002", layer="bus"),
                          self._node("AI-POSTMORTEM-001")], "edges": []}
        out = R._mermaid_system(data)
        self.assertIn('subgraph sg_BUS["BUS"]', out)     # multi-node area gets a box
        self.assertIn('subgraph sg_misc["misc"]', out)   # lone node collapses into misc
        self.assertIn("stroke-width:3px", out)           # bus stays marked

    def test_system_map_hides_edges_into_bus(self):  # verifies: REQ-MAPDIAGRAMS-876#CASE-3  # verifies: ARCH-MAPDIAGRAMS-055#CASE-3
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

    def test_deps_is_area_level_overview(self):  # verifies: REQ-MAPDIAGRAMS-877#CASE-1  # verifies: REQ-MAPDIAGRAMS-877#CASE-2  # verifies: ARCH-MAPDIAGRAMS-055#CASE-4
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
            self.assertEqual(len(written), 1)
            with open(os.path.join(reqs_dir, written[0]), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("Every bullet below is binding.", text)
            self.assertNotIn("shall", text.lower())


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


def _req_with_verify(rid, items, title="Cap"):
    """A new-schema requirement whose Verify-intent section holds `items`."""
    vi = "\n".join("- " + it for it in items)
    return (
        "---\nid: {id}\nstatus: baseline\nlayer: feature\n---\n\n# {t}\n\n"
        "## WHAT — Contract (normative)\n- shall do the thing.\n\n"
        "## WHAT — Verify intent (open questions for the human)\n{vi}\n\n"
        "## HOW — Acceptance (= tests)\nAC-1\n"
    ).format(id=rid, t=title, vi=vi)


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

    def test_hostile_title_roundtrips_as_data_not_injection(self):  # bug: id-js-string-breakout-xss  # verifies: REQ-MAP-870#CASE-6  # verifies: ARCH-MAP-007#CASE-3
        doc = _export_doc_for({"id": "a</script><img src=x>", "title": "x\");alert(1)//"})
        # the value survives intact as a JSON string — there is no markup context to break out of
        self.assertEqual(doc["nodes"][0]["id"], "a</script><img src=x>")
        self.assertEqual(doc["nodes"][0]["title"], "x\");alert(1)//")

    def test_node_with_no_members_has_empty_list(self):  # verifies: REQ-MAP-870#CASE-3  # verifies: ARCH-MAP-007#CASE-3
        self.assertEqual(_export_doc_for({"id": "A-1"})["nodes"][0]["members"], [])

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


class ViewerInject(unittest.TestCase):  # tested-by: ARCH-VIEWER-007  # tested-by: REQ-VIEWER-940  # tested-by: REQ-VIEWER-941
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


class DocsPublish(unittest.TestCase):  # tested-by: ARCH-PAGES-021  # tested-by: REQ-PAGES-889
    def test_docs_publish_path_nojekyll_signal(self):  # verifies: REQ-PAGES-889#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", ".nojekyll"), "")
            self.assertEqual(R._docs_publish_path(d), os.path.join(d, "docs", "map.html"))

    def test_docs_publish_path_index_html_signal(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "index.html"), "<html></html>")
            self.assertEqual(R._docs_publish_path(d), os.path.join(d, "docs", "map.html"))

    def test_docs_publish_path_no_signal(self):  # verifies: REQ-PAGES-889#CASE-1
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            self.assertIsNone(R._docs_publish_path(d))

    def test_docs_publish_path_no_docs_dir(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R._docs_publish_path(d))


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


class Staleness(unittest.TestCase):  # tested-by: ARCH-CHECK-006
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


class GateErrors(unittest.TestCase):  # tested-by: ARCH-CHECK-006  # tested-by: REQ-CHECK-828  # tested-by: REQ-CHECK-829  # tested-by: REQ-CHECK-830  # tested-by: REQ-CHECK-833
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

    def test_invalid_status_errors_and_exits_nonzero(self):  # bug: gate-never-asserted-to-fail  # verifies: ARCH-CHECK-006#CASE-3  # verifies: REQ-CHECK-828#CASE-2
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="bogus", layer="feature", extra="", title="T")})
        self.assertIn("invalid status", out)
        self.assertEqual(code, 1)

    def test_invalid_layer_errors(self):  # verifies: ARCH-CHECK-006#CASE-3  # verifies: REQ-CHECK-828#CASE-2
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="bogus", extra="", title="T")})
        self.assertIn("invalid layer", out)
        self.assertEqual(code, 1)

    def test_depends_on_missing_errors(self):  # verifies: ARCH-CHECK-006#CASE-3  # verifies: REQ-CHECK-828#CASE-3
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="feature",
            extra="depends_on: [GHOST-X-999]\n", title="T")})
        self.assertIn("depends_on missing GHOST-X-999", out)
        self.assertEqual(code, 1)

    def test_dangling_tag_errors(self):  # verifies: ARCH-CHECK-006#CASE-1  # verifies: REQ-CHECK-828#CASE-1
        code, out = self._check({"mod.py": tag("GHOST-CAP-001") + "\n"})
        self.assertIn("dangling tag", out)
        self.assertEqual(code, 1)

    def test_confirmed_without_implements_errors(self):  # verifies: ARCH-CHECK-006#CASE-2  # verifies: REQ-CHECK-828#CASE-4
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="confirmed", layer="bus", extra="", title="T")})
        self.assertIn("no implements", out)
        self.assertEqual(code, 1)

    def test_test_exempt_suppresses_test_warn(self):  # verifies: ARCH-CHECK-006#CASE-10  # verifies: REQ-CHECK-829#CASE-4
        code, out = self._check({
            "A-FOO-001.md": REQ.format(id="A-FOO-001", status="confirmed", layer="bus",
                                       extra="test_exempt: covered by manual QA\n", title="T"),
            "mod.py": tag("A-FOO-001") + "\n"})
        self.assertNotIn("tested-by", out)
        self.assertEqual(code, 0)

    def test_untracked_lock_flagged_then_cleared(self):  # uncommitted-lock gap  # verifies: ARCH-CHECK-006#CASE-13  # verifies: REQ-CHECK-830#CASE-5  # verifies: REQ-CHECK-830#CASE-6
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

    def test_update_lock_writes_hashes(self):  # verifies: ARCH-CHECK-006#CASE-12  # verifies: REQ-CHECK-833#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   REQ.format(id="A-FOO-001", status="baseline", layer="bus", extra="", title="T"))
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, R.scan_members(d, d), d), True)
            self.assertIn("A-FOO-001", R.load_lock(d))

    def test_corrupt_lock_warns_in_check(self):  # bug: corrupt-lock-disables-drift-silently  # verifies: ARCH-CHECK-006#CASE-5  # verifies: REQ-CHECK-830#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   REQ.format(id="A-FOO-001", status="baseline", layer="bus", extra="", title="T"))
            _write(os.path.join(d, "_reqlock.json"), "{ not json")
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, R.scan_members(d, d), d), False)
            self.assertIn("unreadable", buf.getvalue())
            self.assertEqual(code, 0)   # corrupt lock is a WARN, never a hard error


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

    def test_legacy_schema_is_flagged_nonblocking(self):  # verifies: ARCH-CHECK-006#CASE-11  # verifies: REQ-CHECK-830#CASE-7  # verifies: REQ-CHECK-831#CASE-1  # verifies: REQ-CHECK-831#CASE-2
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
    # tested-by: ARCH-PAGES-021  (the docs/map.html freshness cases below)
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
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)

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

    # ---- docs/map.html (GitHub Pages copy) freshness --------------------------
    def test_fresh_docs_map_passes_check(self):  # verifies: REQ-PAGES-889#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            _write(os.path.join(d, "docs", ".nojekyll"), "")  # Pages signal
            self._map(d)                              # writes docs/map.html too
            self.assertTrue(os.path.exists(os.path.join(d, "docs", "map.html")))
            code, out = self._map(d, check=True)
            self.assertEqual(code, 0)
            self.assertIn("fresh", out)

    def test_stale_docs_map_fails_check(self):  # verifies: REQ-PAGES-889#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            _write(os.path.join(d, "docs", ".nojekyll"), "")
            self._map(d)                              # generate everything fresh
            _write(os.path.join(d, "docs", "map.html"), "<html>stale</html>")
            code, out = self._map(d, check=True)      # only the docs copy drifted
            self.assertEqual(code, 1)
            self.assertIn("map.html", out)

    def test_absent_docs_map_is_not_stale(self):  # verifies: REQ-PAGES-889#CASE-2
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

    def test_docs_map_repo_field_change_is_not_stale(self):  # verifies: REQ-PAGES-889#CASE-3
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

    def test_draft_intent_deduped_not_in_intent_bucket(self):  # verifies: ARCH-NEXT-013#CASE-3
        # a draft with an open verify bullet must NOT appear under intent review:
        # the source dedup folds it into 'unreviewed' (one bucket, honest count)
        body = "# T\n\n## WHAT — Verify intent\n- is this magic constant a bug?\n"
        reqs = {"REQ-BAR-002": self._req("draft", body=body)}
        _, out = self._next(reqs, {})
        self.assertIn("Drafts to review", out)
        self.assertNotIn("Needs intent review", out)

    def test_open_verify_intent_lands_in_needs_intent_review(self):  # verifies: REQ-NEXT-884#CASE-1  # verifies: ARCH-NEXT-013#CASE-4
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

    def test_review_flagged_drafts_ordered_first(self):  # verifies: REQ-NEXT-885#CASE-3  # verifies: ARCH-NEXT-013#CASE-6
        reqs = {"DRAFT-A-001": self._req("draft", "risk: 0"),
                "DRAFT-B-002": self._req("draft", "risk: 2")}  # REVIEW
        _, out = self._next(reqs, {})
        self.assertLess(out.index("DRAFT-B-002"), out.index("DRAFT-A-001"))  # high-risk first
        self.assertIn("[REVIEW]", out)

    def test_top_n_truncates_and_all_expands(self):  # verifies: REQ-NEXT-886#CASE-1  # verifies: REQ-NEXT-886#CASE-2  # verifies: REQ-NEXT-886#CASE-3  # verifies: ARCH-NEXT-013#CASE-5
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

    def test_granularity_at_threshold_warns(self):  # tested-by: ARCH-NEXT-013  # verifies: ARCH-NEXT-013#CASE-11
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

    def test_load_translations_malformed_cache_fails_open(self):  # bug: load-translations-not-dict-guarded
        reqs_dir = self._tmp_reqs_dir()
        i18n_dir = os.path.join(reqs_dir, "_i18n")
        os.makedirs(i18n_dir)
        with open(os.path.join(i18n_dir, "en.json"), "w", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)   # malformed: not a dict
        reqs = {"REQ-A-001": self._req(self.RO_BODY)}
        out = R._load_translations(reqs, reqs_dir)
        self.assertEqual(out, {})


class Show(unittest.TestCase):  # tested-by: ARCH-SHOW-015  # tested-by: REQ-SHOW-917  # tested-by: REQ-SHOW-918  # tested-by: REQ-SHOW-919
    def _show(self, reqs, members, cap_id):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = R.cmd_show(R.Workspace(reqs, members), cap_id)
        return code, buf.getvalue()

    def _req(self, status="confirmed", extra="", body="# T\n"):
        return {"meta": {"status": status, "layer": "feature", **dict(_kv(extra))},
                "body": body, "path": "requirements/X.md"}

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
        c = "resolve the dispatch model for each senator from prompt frontmatter"
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

    def test_query_ranks_matching_requirement_first_with_score(self):  # AC-1  # verifies: REQ-SEARCH-913#CASE-1
        reqs = {"REQ-DRIFT-001": self._req("Drift", "detect when a contract changes against the lock hash baseline"),
                "REQ-MAP-002": self._req("Map", "render mermaid diagrams of the requirement graph")}
        code, out = self._search(reqs, "contract changed against the lock hash")
        self.assertEqual(code, 0)
        lines = self._score_lines(out)
        self.assertTrue(lines, "expected at least one ranked hit")
        # top hit is the drift requirement, printed with its cosine score (Dimon:
        # a match is shown WITH its score, never as a bare id)
        self.assertRegex(lines[0].strip(), r"^\d\.\d{3}\s+REQ-DRIFT-001\b")

    def test_no_lexical_overlap_reports_no_strong_match(self):  # AC-2 — Dimon blocking condition  # verifies: REQ-SEARCH-913#CASE-4  # verifies: REQ-SEARCH-913#CASE-5  # verifies: REQ-SEARCH-915#CASE-1
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


class Health(unittest.TestCase):  # tested-by: ARCH-HEALTH-017  # tested-by: ARCH-REVIEWEDSCORE-109  # tested-by: REQ-HEALTH-857  # tested-by: REQ-HEALTH-858  # tested-by: REQ-HEALTH-859  # tested-by: REQ-HEALTH-968
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

    def test_all_draft_is_zero(self):
        reqs = {"REQ-A-001": {"meta": {"status": "draft"}, "body": "# T\n"}}
        _, out = self._health(reqs, {})
        self.assertIn("0/100", out)

    def test_json_has_all_component_fields(self):  # bug-hunt #18: assert every emitted key  # verifies: REQ-HEALTH-859#CASE-1
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        self.assertEqual(json.loads(out), {
            "score": 100, "total": 1, "healthy": 1, "confirmed": 1, "implemented": 1,
            "tested": 1, "drafts": 0, "orphans": 0, "untested": 0, "open_intent": 0, "drift": 0,
            "gate_errors": 0, "gate_link_sync_clean": True})

    # ARCH-HEALTH-017 CASE-8 / CASE-9: a draft can never be green (the first axis is
    # status `confirmed`), so every draft caps the headline score by construction. The
    # reviewed-only score separates "not reviewed yet" from "rotting" WITHOUT redefining
    # `score`, which CASE-2 binds to zero on an all-draft corpus and which every
    # consumer badge already reads.
    def _draft(self):
        return {"meta": {"status": "draft"}, "body": "# T\n"}

    def test_reviewed_score_excludes_drafts(self):  # verifies: ARCH-REVIEWEDSCORE-109#CASE-1
        reqs = {"REQ-A-001": self._green()}
        for n in (2, 3, 4):
            reqs["REQ-A-00%d" % n] = self._draft()
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members, as_json=True)
        obj = json.loads(out)
        self.assertEqual(obj["score"], 25)            # 1 green of 4 — unchanged meaning
        self.assertEqual(obj["reviewed_score"], 100)  # 1 green of 1 reviewed
        self.assertEqual(obj["reviewed_total"], 1)

    def test_reviewed_score_absent_on_all_draft_corpus(self):  # verifies: ARCH-REVIEWEDSCORE-109#CASE-2
        _, out = self._health({"REQ-A-001": self._draft()}, {}, as_json=True)
        obj = json.loads(out)
        self.assertNotIn("reviewed_score", obj)       # 0 of 0 is not 0%
        self.assertEqual(obj["score"], 0)             # CASE-2 still holds

    def test_reviewed_score_absent_when_no_drafts(self):  # verifies: ARCH-REVIEWEDSCORE-109#CASE-3
        # with no draft it would restate `score` — a key that means nothing is a schema cost
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health({"REQ-A-001": self._green()}, members, as_json=True)
        self.assertNotIn("reviewed_score", json.loads(out))

    def test_reviewed_score_line_names_the_unconfirmed(self):  # verifies: ARCH-REVIEWEDSCORE-109#CASE-4
        reqs = {"REQ-A-001": self._green(), "REQ-A-002": self._draft()}
        members = {"REQ-A-001": [("implements", "x.py", 1), ("tested-by", "t.py", 2)]}
        _, out = self._health(reqs, members)
        self.assertIn("reviewed only", out)
        self.assertIn("1 not confirmed yet", out)

    def test_reviewed_score_denominator_is_confirmed_not_merely_non_draft(self):  # verifies: ARCH-REVIEWEDSCORE-109#CASE-5
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

    # tested-by: ARCH-HEALTH-017 (RM-6 / Senate reqmap-health-gate-cleanliness)
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


class TestLink(unittest.TestCase):  # tested-by: ARCH-TESTLINK-018  # tested-by: REQ-TESTLINK-930  # tested-by: REQ-TESTLINK-931  # tested-by: REQ-TESTLINK-932
    def test_link_problem_missing_file(self):  # verifies: REQ-TESTLINK-930#CASE-2
        self.assertIn("does not exist", R._test_link_problem("/no/such/file_xyz.py"))

    def test_link_problem_real_test_file(self):  # verifies: REQ-TESTLINK-931#CASE-2
        self.assertEqual("", R._test_link_problem(__file__))   # this file has def test_

    def test_link_problem_testless_file(self):  # verifies: REQ-TESTLINK-930#CASE-3
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "notests.py")
            _write(p, "def helper():\n    return 1\n")
            self.assertIn("no test function", R._test_link_problem(p))

    def test_prose_it_call_is_not_a_test(self):  # bug-hunt #6
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "spec.md")
            _write(p, "The engine scans files; it (the parser) returns None.\n")
            self.assertIn("no test function", R._test_link_problem(p))

    def test_js_it_call_is_a_test(self):  # bug-hunt #6  # verifies: REQ-TESTLINK-931#CASE-4
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "spec.test.js")
            _write(p, "it('works', () => { expect(1).toBe(1); });\n")
            self.assertEqual("", R._test_link_problem(p))

    def test_go_test_func_recognized(self):  # bug-hunt #21  # verifies: REQ-TESTLINK-931#CASE-5
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "scan_test.go")
            _write(p, 'package main\nimport "testing"\nfunc TestScan(t *testing.T) {}\n')
            self.assertEqual("", R._test_link_problem(p))

    def test_rust_test_attr_recognized(self):  # bug-hunt #21  # verifies: REQ-TESTLINK-932#CASE-1
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "lib.rs")
            _write(p, "#[cfg(test)]\nmod t {\n  #[test]\n  fn checks() {}\n}\n")
            self.assertEqual("", R._test_link_problem(p))

    def test_py_runner_entry_recognized(self):  # stdlib suites drive checks from run()/main()  # verifies: REQ-TESTLINK-932#CASE-2
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "test_thing.py")
            _write(p, 'def run():\n    return 0\nif __name__ == "__main__":\n    raise SystemExit(run())\n')
            self.assertEqual("", R._test_link_problem(p))

    def test_py_runner_entry_needs_main_guard(self):  # a bare main()/run() without __main__ is not a test
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "helper.py")
            _write(p, "def main():\n    return 0\n")
            self.assertIn("no test function", R._test_link_problem(p))

    def test_check_warns_warn_only_on_broken_link(self):  # verifies: REQ-TESTLINK-933#CASE-1  # verifies: REQ-TESTLINK-933#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = {"REQ-A-001": {"meta": {"status": "confirmed", "layer": "feature"},
                                  "body": "# T\n", "path": os.path.join(d, "REQ-A-001.md")}}
            members = {"REQ-A-001": [("implements", "src/foo.py", 1),
                                     ("tested-by", "tests/missing_test.py", 2)]}
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
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


class AcVerify(unittest.TestCase):  # tested-by: ARCH-ACVERIFY-019  # tested-by: REQ-ACVERIFY-821  # tested-by: REQ-ACVERIFY-822
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

    def test_scan_ac_verifies_parses_tag(self):  # verifies: ARCH-ACVERIFY-019#CASE-1  # verifies: REQ-ACVERIFY-821#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "t.py"), v_tag("REQ-X-001", "AC-1") + "\n")
            cover = R.scan_ac_verifies(d, d)
            self.assertIn("REQ-X-001", cover)
            self.assertIn("AC-1", cover["REQ-X-001"])

    def test_scan_ac_verifies_requires_ac_suffix(self):  # verifies: REQ-ACVERIFY-821#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "t.py"), "# {}: REQ-X-001\n".format(_VERIFY_ROLE))  # no #AC
            self.assertEqual(R.scan_ac_verifies(d, d), {})

    def test_labeled_acs_extracts_labels(self):
        body = _ac_body(acceptance="AC-1\n  Given a\nAC-2\n  Given b")
        self.assertEqual(R._labeled_acs(body), ["AC-1", "AC-2"])

    def test_labeled_acs_empty_on_bullet_acs(self):
        body = _ac_body(acceptance="- a bullet criterion.\n- another one.")
        self.assertEqual(R._labeled_acs(body), [])

    def test_partial_coverage_warns_the_uncovered(self):  # verifies: ARCH-ACVERIFY-019#CASE-1  # verifies: REQ-ACVERIFY-821#CASE-1  # verifies: REQ-ACVERIFY-821#CASE-4  # verifies: REQ-ACVERIFY-823#CASE-3
        files = self._req("AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n  Then d")
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n"   # only AC-1 covered
        code, out = self._check(files)
        self.assertIn("1/2 automatable criteria", out)         # ONE aggregated line
        self.assertIn("missing AC-2", out)
        self.assertNotIn("missing AC-1", out)
        self.assertEqual(code, 0)                              # warn-only

    def test_partial_coverage_is_one_warning_not_one_per_criterion(self):  # verifies: REQ-ACVERIFY-821#CASE-3
        # partial adoption must not cost more than adopting nothing (feedback 10b):
        # four uncovered criteria produce ONE line, not four.
        files = self._req("\n".join("AC-{0}\n  Given a{0}\n  Then b{0}".format(i)
                                    for i in range(1, 6)))
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n"
        _, out = self._check(files)
        self.assertEqual(out.count("automatable criteria"), 1)
        self.assertIn("missing AC-2, AC-3, AC-4, AC-5", out)

    def test_manual_criteria_excluded_from_per_ac_warning(self):  # verifies: ARCH-ACVERIFY-019#CASE-5  # verifies: REQ-ACVERIFY-822#CASE-3
        # `verifiable by: inspection` can never carry a `verifies:` tag — counting it
        # produces a warning nobody can ever clear (feedback 10a).
        files = self._req("AC-1  <!-- verifiable by: automated test -->\n  Given a\n  Then b\n"
                          "AC-2  <!-- verifiable by: inspection -->\n  Given c\n  Then d")
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n"
        _, out = self._check(files)
        self.assertNotIn("automatable criteria", out)

    def test_unedited_template_marker_is_not_manual(self):
        # the template ships `automated test | manual | inspection | load test`; an
        # author who never chose has not declared the criterion unautomatable.
        body = _ac_body(acceptance="AC-1  <!-- verifiable by: automated test | manual | "
                                   "inspection | load test -->\n  Given a\n  Then b")
        self.assertEqual(R._automatable_acs(body), ["AC-1"])


    def test_full_coverage_silent(self):  # verifies: ARCH-ACVERIFY-019#CASE-2
        files = self._req("AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n  Then d")
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n" + v_tag("A-FOO-001", "AC-2") + "\n"
        _, out = self._check(files)
        self.assertNotIn("criterion unverified", out)

    def test_no_verify_tags_is_optin_silent(self):  # verifies: ARCH-ACVERIFY-019#CASE-3  # verifies: REQ-ACVERIFY-822#CASE-1
        files = self._req("AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n  Then d")  # zero verifies tags
        _, out = self._check(files)
        self.assertNotIn("criterion unverified", out)

    def test_bullet_acs_exempt(self):  # verifies: ARCH-ACVERIFY-019#CASE-4  # verifies: REQ-ACVERIFY-822#CASE-2
        files = self._req("- a bullet criterion.\n- another one.")
        files["mod.py"] += v_tag("A-FOO-001", "AC-1") + "\n"   # tag present but ACs unlabelled
        _, out = self._check(files)
        self.assertNotIn("criterion unverified", out)


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


class AcCoverageEmission(unittest.TestCase):  # tested-by: ARCH-ACVERIFY-019  # tested-by: REQ-ACVERIFY-823
    """`clauses`/`covered`/`gap` are emitted by the ENGINE or not at all. The viewer
    used to invent them (clauses = contract-line count, covered = all-or-nothing),
    so a requirement with three real tests rendered "0 / 8 clauses covered"."""

    def _node(self, acceptance, cover):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n"
                   + _ac_body(acceptance=acceptance))
            reqs = R.load_requirements(d)
            return R._build_map_data(reqs, {}, {"A-FOO-001": cover})["nodes"][0]

    def test_absent_when_no_verifies_tag_adopted(self):  # verifies: REQ-ACVERIFY-823#CASE-1
        node = self._node("AC-1\n  Given a\nAC-2\n  Given b", {})
        self.assertNotIn("clauses", node)
        self.assertNotIn("covered", node)

    def test_absent_for_unlabelled_bullet_acs(self):
        node = self._node("- one.\n- two.", {"AC-1": [("t.py", 1)]})
        self.assertNotIn("clauses", node)

    def test_partial_coverage_emitted_with_gap(self):  # verifies: ARCH-ACVERIFY-019#CASE-6  # verifies: REQ-ACVERIFY-823#CASE-1  # verifies: REQ-ACVERIFY-823#CASE-2
        node = self._node("AC-1\n  Given a\nAC-2\n  Given b", {"AC-1": [("t.py", 1)]})
        self.assertEqual((node["clauses"], node["covered"]), (2, 1))
        self.assertIn("AC-2", node["gap"])

    def test_full_coverage_has_no_gap(self):  # verifies: REQ-ACVERIFY-823#CASE-2
        node = self._node("AC-1\n  Given a", {"AC-1": [("t.py", 1)]})
        self.assertEqual((node["clauses"], node["covered"]), (1, 1))
        self.assertNotIn("gap", node)

    def test_manual_criteria_not_counted_as_clauses(self):  # verifies: ARCH-ACVERIFY-019#CASE-5
        node = self._node("AC-1\n  Given a\nAC-2  <!-- verifiable by: inspection -->\n  Given b",
                          {"AC-1": [("t.py", 1)]})
        self.assertEqual((node["clauses"], node["covered"]), (1, 1))


class ImplExemptLayers(unittest.TestCase):  # tested-by: ARCH-TRACE-020  # tested-by: ARCH-PROMOTE-011  # tested-by: REQ-TRACE-935
    """`confirm` refused a `layer: need` the gate, `health` and the risk map all
    exempt — so this repo's own SYS-SSOT-001 could only become confirmed by editing
    the file around the command. One predicate now answers for all four."""

    def test_gate_does_not_error_on_confirmed_aggregate(self):  # verifies: ARCH-TRACE-020#CASE-5  # verifies: REQ-TRACE-935#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "REQ-AGG-003.md"),
                   REQ.format(id="REQ-AGG-003", status="confirmed", layer="aggregate",
                              extra="depends_on: [REQ-A-001]\n", title="Agg"))
            _write(os.path.join(d, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="confirmed", layer="feature", extra="", title="A"))
            _write(os.path.join(d, "a.py"), tag("REQ-A-001") + "\n")
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            self.assertEqual(R._link_sync_errors(reqs, members), [])

    def test_aggregate_is_not_flagged_unimplemented_by_risk(self):
        node = {"status": "confirmed", "layer": "aggregate", "members": [],
                "verify": [], "test_exempt": None}
        self.assertNotIn("unimplemented", R._risk_signals(node))


class ShellTestedBy(unittest.TestCase):  # tested-by: ARCH-TESTLINK-018  # tested-by: REQ-TESTLINK-932
    """Four real bash suites warned forever because no pattern matched shell."""

    def test_bash_function_recognized(self):  # verifies: REQ-TESTLINK-932#CASE-3
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "checks.sh")
            _write(p, "#!/usr/bin/env bash\ntest_backup_runs() {\n  [ -f x ]\n}\n")
            self.assertEqual(R._test_link_problem(p), "")

    def test_bats_case_recognized(self):  # verifies: REQ-TESTLINK-932#CASE-3
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "suite.bats")
            _write(p, '@test "restore drill" {\n  run ./restore\n}\n')
            self.assertEqual(R._test_link_problem(p), "")

    def test_test_sh_naming_convention_accepted(self):  # verifies: REQ-TESTLINK-932#CASE-4
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "backup-check.test.sh")
            _write(p, "#!/bin/sh\n./backup-check --dry-run || exit 1\n")
            self.assertEqual(R._test_link_problem(p), "")


    def test_bare_test_sh_name_recognized(self):  # bug: sh-test-name-re-bare-test
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "test.sh")
            _write(p, "#!/bin/sh\n./run-checks --dry-run\n")
            self.assertEqual(R._test_link_problem(p), "")

    def test_bare_tests_sh_name_recognized(self):  # bug: sh-test-name-re-bare-test
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "tests.sh")
            _write(p, "#!/bin/sh\n./run-checks --dry-run\n")
            self.assertEqual(R._test_link_problem(p), "")


class TestLinkOnDraft(unittest.TestCase):  # tested-by: ARCH-TESTLINK-018  # tested-by: REQ-TESTLINK-930  # tested-by: REQ-TESTLINK-933
    """A tested-by pointing at a non-test file is wrong the day it is written; the
    check ran only on `confirmed`, so a draft-only corpus audited nothing."""

    def _check(self, status, strict=False):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   "---\nid: A-FOO-001\nstatus: {}\nlayer: bus\n---\n\n".format(status)
                   + _ac_body())
            _write(os.path.join(d, "widget.py"), tag("A-FOO-001") + "\n" + tb_tag("A-FOO-001")
                   + "\ndef render():\n    return 1\n")
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False, strict)
            return code, buf.getvalue()

    def test_draft_link_to_non_test_file_warns(self):  # verifies: REQ-TESTLINK-930#CASE-1
        code, out = self._check("draft")
        self.assertIn("contains no test function", out)
        self.assertEqual(code, 0)                       # warn-only

    def test_draft_link_problem_is_not_strict_promoted(self):  # verifies: REQ-TESTLINK-933#CASE-3
        # a draft-heavy consumer running `gate --strict` must not start failing
        code, out = self._check("draft", strict=True)
        self.assertEqual(code, 0)
        self.assertIn("WARN", out)

    def test_confirmed_link_problem_still_fails_under_strict(self):  # verifies: REQ-TESTLINK-933#CASE-3
        code, _ = self._check("confirmed", strict=True)
        self.assertEqual(code, 1)


class GateMapFreshness(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-871
    """`gate` said nothing about a stale committed map, so a consumer running only
    `gate` before committing found out from a red CI run (twice, in one repo)."""

    def _gate(self, d):
        reqs = R.load_requirements(d)
        members = R.scan_members(d, d)
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            R.cmd_check(R.Workspace(reqs, members, d, d), False)
        return buf.getvalue()

    def _seed(self, d):
        _write(os.path.join(d, "A-FOO-001.md"),
               "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n" + _ac_body())
        _write(os.path.join(d, "a.py"), tag("A-FOO-001") + "\n")

    def test_fresh_map_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            with redirect_stdout(io.StringIO()):
                R.cmd_map(R.Workspace(reqs, members, d), d)
            self.assertNotIn("committed map is stale", self._gate(d))

    def test_stale_map_warns(self):  # verifies: REQ-MAP-871#CASE-6
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            with redirect_stdout(io.StringIO()):
                R.cmd_map(R.Workspace(reqs, members, d), d)
            _write(os.path.join(d, "A-FOO-002.md"),      # registry changed, map not regenerated
                   "---\nid: A-FOO-002\nstatus: draft\nlayer: bus\n---\n\n" + _ac_body())
            out = self._gate(d)
            self.assertIn("committed map is stale", out)
            self.assertIn("_map.json", out)

    def test_absent_map_is_not_stale(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            self.assertNotIn("committed map is stale", self._gate(d))


class SuggestVerifies(unittest.TestCase):  # tested-by: ARCH-SUGGESTVERIFIES-047  # tested-by: REQ-SUGGESTVERIFIES-927  # tested-by: REQ-SUGGESTVERIFIES-928  # tested-by: REQ-SUGGESTVERIFIES-929
    """110 of a consumer's 205 untagged criteria already had a test NAMED after them.
    Each guard below exists because its absence produced a WRONG link."""

    def _repo(self, d, reqs, tests):
        for rid, acceptance in reqs.items():
            _write(os.path.join(d, rid + ".md"),
                   "---\nid: {}\nstatus: confirmed\nlayer: feature\n---\n\n".format(rid)
                   + _ac_body(acceptance=acceptance))
        for name, body in tests.items():
            _write(os.path.join(d, name), body)

    def _suggest(self, d, apply_tags=False):
        reqs = R.load_requirements(d)
        members = R.scan_members(d, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_suggest_verifies(R.Workspace(reqs, members, d, d), apply_tags)
        return buf.getvalue()

    TWO_AC = "AC-1\n  Given a\n  Then b\nAC-2\n  Given c\n  Then d"

    def test_proposes_test_named_after_the_criterion(self):  # verifies: REQ-SUGGESTVERIFIES-927#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": self.TWO_AC},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac1_upload_jpeg_valid():\n    pass\n"
                        "def test_ac2_tip_neacceptat():\n    pass\n"})
            out = self._suggest(d)
            self.assertIn("AREA-UPLOAD-037 AC-1", out)
            self.assertIn("AREA-UPLOAD-037 AC-2", out)
            self.assertIn("2 proposal(s)", out)

    def test_already_tagged_criterion_is_not_proposed(self):  # verifies: REQ-SUGGESTVERIFIES-927#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": self.TWO_AC},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac1_x():  " + v_tag("AREA-UPLOAD-037", "AC-1") + "\n    pass\n"
                        "def test_ac2_y():\n    pass\n"})
            out = self._suggest(d)
            self.assertIn("1 proposal(s)", out)
            self.assertIn("AC-2", out)

    def test_trap1_shared_file_needs_a_distinctive_token(self):  # verifies: REQ-SUGGESTVERIFIES-928#CASE-2
        # one tested-by file serving two requirements holds two different `ac1` tests
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": self.TWO_AC, "AREA-SIGNING-046": self.TWO_AC},
                       {"test_e2e.py": tb_tag("AREA-UPLOAD-037") + "\n" + tb_tag("AREA-SIGNING-046")
                        + "\ndef test_ac1_generic():\n    pass\n"
                        "def test_ac2_upload_dosar():\n    pass\n"})
            out = self._suggest(d)
            self.assertNotIn("AC-1", out)               # ambiguous owner -> no proposal
            self.assertIn("AREA-UPLOAD-037 AC-2", out)  # name carries `upload`
            self.assertNotIn("AREA-SIGNING-046 AC-2", out)

    def test_trap2_class_name_does_not_qualify_a_test(self):
        # `class TestUploadSiSigning:` carries the tokens of BOTH requirements
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": self.TWO_AC, "AREA-SIGNING-046": self.TWO_AC},
                       {"test_e2e.py": tb_tag("AREA-UPLOAD-037") + "\n" + tb_tag("AREA-SIGNING-046")
                        + "\nclass TestUploadSiSigning:\n"
                        "    def test_ac1_runs(self):\n        pass\n"})
            self.assertNotIn("AC-1", self._suggest(d))

    def test_trap3_fixture_parameter_does_not_qualify_a_test(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-EXPORT-061": self.TWO_AC, "AREA-CAMPAIGN-056": self.TWO_AC},
                       {"test_shared.py": tb_tag("AREA-EXPORT-061") + "\n" + tb_tag("AREA-CAMPAIGN-056")
                        + "\ndef test_export_ac2_rows(self, ctx, campaign):\n    pass\n"})
            out = self._suggest(d)
            self.assertIn("AREA-EXPORT-061 AC-2", out)
            self.assertNotIn("AREA-CAMPAIGN-056 AC-2", out)   # `campaign` is a parameter

    def test_guard_foreign_requirement_number_wins(self):  # verifies: REQ-SUGGESTVERIFIES-928#CASE-3
        # `test_ac1_083_...` sits in 040's file but verifies 083
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-VARENGINE-040": self.TWO_AC, "AREA-DOCFIELDS-083": self.TWO_AC},
                       {"test_var.py": tb_tag("AREA-VARENGINE-040") + "\n"
                        + "def test_ac1_083_placeholder():\n    pass\n"})
            self.assertNotIn("AREA-VARENGINE-040 AC-1", self._suggest(d))

    def test_two_candidates_are_ambiguous_not_applied(self):  # verifies: REQ-SUGGESTVERIFIES-928#CASE-4
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": self.TWO_AC},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac1_first():\n    pass\n"
                        "def test_ac1_second():\n    pass\n"})
            out = self._suggest(d, apply_tags=True)
            self.assertIn("AMBIGUOUS", out)
            src = open(os.path.join(d, "test_upload.py"), encoding="utf-8").read()
            self.assertNotIn("#AC-1", src)

    def test_ac_number_is_not_a_prefix_match(self):  # verifies: REQ-SUGGESTVERIFIES-928#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": "AC-1\n  Given a\n  Then b"},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac12_other():\n    pass\n"})
            self.assertIn("no suggestions", self._suggest(d))

    def test_apply_writes_the_tag_and_is_idempotent(self):  # verifies: REQ-SUGGESTVERIFIES-929#CASE-2  # verifies: REQ-SUGGESTVERIFIES-929#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": "AC-1\n  Given a\n  Then b"},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac1_upload_ok():\n    pass\n"})
            self._suggest(d, apply_tags=True)
            src = open(os.path.join(d, "test_upload.py"), encoding="utf-8").read()
            self.assertIn("def test_ac1_upload_ok():  # {}: AREA-UPLOAD-037#AC-1".format("verifies"), src)
            self.assertIn("no suggestions", self._suggest(d))     # now covered
            self.assertEqual(open(os.path.join(d, "test_upload.py"), encoding="utf-8").read(), src)

    def test_apply_makes_the_gate_stop_warning(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": self.TWO_AC},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac1_a():  " + v_tag("AREA-UPLOAD-037", "AC-1") + "\n    pass\n"
                        "def test_ac2_b():\n    pass\n"})
            _write(os.path.join(d, "impl.py"), tag("AREA-UPLOAD-037") + "\n")
            self._suggest(d, apply_tags=True)
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertNotIn("automatable criteria", buf.getvalue())

    def test_js_it_label_is_matched(self):  # verifies: REQ-SUGGESTVERIFIES-927#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": "AC-1\n  Given a\n  Then b"},
                       {"upload.spec.ts": "// {}: AREA-UPLOAD-037\n".format("tested" + "-by")
                        + 'it("ac1 uploads a jpeg", () => {});\n'})
            out = self._suggest(d)
            self.assertIn("AREA-UPLOAD-037 AC-1", out)
            self.assertIn("// {}:".format("verifies"), out)        # JS comment syntax

    def test_apply_verifies_existing_case11_does_not_block_case1(self):  # bug: apply-verifies-substring-collision
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "test_x.py")
            _write(p, "def test_thing():  # {}: RID#AC-11\n    pass\n".format("verifies"))
            proposals = [("RID", "AC-1", "test_x.py", 1, "test_thing")]
            n = R._apply_verifies(proposals, d)
            self.assertEqual(n, 1)
            src = open(p, encoding="utf-8").read()
            self.assertTrue(
                src.splitlines()[0].rstrip().endswith("# {}: RID#AC-1".format("verifies")))


class DependsOnCycles(unittest.TestCase):  # tested-by: ARCH-CHECK-006  # tested-by: REQ-CHECK-831
    """A cycle makes the layering claim false, and nothing looked for one — it showed
    up as a 71,000px-wide viewer canvas on a real 59-requirement corpus."""

    def _req(self, rid, deps):
        return REQ.format(id=rid, status="confirmed", layer="feature",
                          extra="depends_on: [{}]\n".format(", ".join(deps)), title=rid)

    def _load(self, d, graph):
        for rid, deps in graph.items():
            _write(os.path.join(d, rid + ".md"), self._req(rid, deps) + "\n" + _ac_body())
            _write(os.path.join(d, rid.lower().replace("-", "_") + ".py"), tag(rid) + "\n")
        return R.load_requirements(d)

    def test_no_cycle_reports_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._load(d, {"A-X-001": ["A-X-002"], "A-X-002": [], "A-X-003": ["A-X-002"]})
            self.assertEqual(R._dependency_cycles(reqs), [])

    def test_two_node_cycle_found(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._load(d, {"A-X-001": ["A-X-002"], "A-X-002": ["A-X-001"]})
            cycles = R._dependency_cycles(reqs)
            self.assertEqual(len(cycles), 1)
            self.assertEqual(cycles[0][0], cycles[0][-1])          # closes where it opened
            self.assertEqual(set(cycles[0]), {"A-X-001", "A-X-002"})

    def test_longer_cycle_reported_once(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._load(d, {"A-X-001": ["A-X-002"], "A-X-002": ["A-X-003"],
                                  "A-X-003": ["A-X-001"], "A-X-004": ["A-X-001"]})
            cycles = R._dependency_cycles(reqs)
            self.assertEqual(len(cycles), 1)
            self.assertEqual(len(cycles[0]), 4)                    # 3 nodes + the repeat

    def test_dangling_dependency_is_not_a_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._load(d, {"A-X-001": ["GHOST-X-999"]})
            self.assertEqual(R._dependency_cycles(reqs), [])

    def test_self_dependency_is_a_cycle(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._load(d, {"A-X-001": ["A-X-001"]})
            self.assertEqual(len(R._dependency_cycles(reqs)), 1)

    def test_gate_warns_and_does_not_error(self):  # verifies: ARCH-CHECK-006#CASE-14  # verifies: REQ-CHECK-831#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self._load(d, {"A-X-001": ["A-X-002"], "A-X-002": ["A-X-001"]})
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
            out = buf.getvalue()
            self.assertIn("depends_on cycle", out)
            self.assertIn("A-X-001 -> A-X-002 -> A-X-001", out)
            self.assertEqual(code, 0)                              # warn-only

    def test_strict_does_not_promote_the_cycle_warning(self):  # verifies: REQ-CHECK-831#CASE-6
        # a consumer whose corpus has a cycle must not see a green CI turn red on upgrade
        with tempfile.TemporaryDirectory() as d:
            self._load(d, {"A-X-001": ["A-X-002"], "A-X-002": ["A-X-001"]})
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False, True)
            self.assertEqual(code, 0)


class SyncMapNotRegenerated(unittest.TestCase):  # tested-by: ARCH-CHECK-006
    """`sync` writes the lock even when the gate errors, but skips the map — the two
    then disagree, `gate` passes locally, and CI fails on `map --check`."""

    def _sync(self, d):
        old_argv, err = sys.argv, io.StringIO()
        sys.argv = ["reqmap", "sync", "--root", d, "--code", d]
        try:
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                rc = R.main()
        finally:
            sys.argv = old_argv
        return rc, err.getvalue()

    def _seed(self, d, reqs_dir):
        _write(os.path.join(reqs_dir, "A-FOO-001.md"),
               "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n" + _ac_body())
        _write(os.path.join(d, "a.py"), tag("A-FOO-001") + "\n")

    def test_failing_sync_says_the_map_was_not_regenerated(self):
        with tempfile.TemporaryDirectory() as d:
            reqs_dir = os.path.join(d, "requirements")
            self._seed(d, reqs_dir)
            _write(os.path.join(d, "b.py"), tag("GHOST-X-999") + "\n")   # dangling tag -> gate error
            rc, err = self._sync(d)
            self.assertEqual(rc, 1)
            self.assertIn("map was NOT regenerated", err)
            self.assertFalse(os.path.exists(os.path.join(reqs_dir, "_map.json")))

    def test_clean_sync_writes_the_map(self):  # verifies: REQ-CHECK-833#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs_dir = os.path.join(d, "requirements")
            self._seed(d, reqs_dir)
            rc, err = self._sync(d)
            self.assertEqual(rc, 0, err)
            self.assertTrue(os.path.exists(os.path.join(reqs_dir, "_map.json")))


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


class Traceability(unittest.TestCase):  # tested-by: ARCH-TRACE-020  # tested-by: REQ-TRACE-934  # tested-by: REQ-TRACE-935

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

    def _feature(self, rid, extra=""):
        body = REQ.format(id=rid, status="confirmed", layer="feature", extra=extra, title="T")
        body += ("\n## WHAT — Contract (normative)\n- It shall x.\n\n"
                 "## HOW — Acceptance (= tests)\n- a.\n")
        return body

    def test_need_layer_is_valid(self):  # verifies: REQ-TRACE-934#CASE-1
        self.assertIn("need", R.VALID_LAYER)

    def test_dangling_satisfies_warns_not_errors(self):  # verifies: ARCH-TRACE-020#CASE-1  # verifies: REQ-TRACE-934#CASE-2
        files = {"A-FOO-001.md": self._feature("A-FOO-001", "satisfies: [GHOST-X-999]\n"),
                 "mod.py": "# {}: A-FOO-001\ndef test_a():\n    pass\n".format("tested" + "-by") +
                           "# {}: A-FOO-001\n".format("implements")}
        code, out = self._check(files)
        self.assertIn("satisfies GHOST-X-999", out)
        self.assertEqual(code, 0)                              # warn, not error

    def test_orphan_need_warns(self):  # verifies: ARCH-TRACE-020#CASE-2  # verifies: REQ-TRACE-934#CASE-3
        need = REQ.format(id="NEED-X-001", status="confirmed", layer="need", extra="", title="N")
        need += "\n## WHAT — Contract (normative)\n- want.\n\n## HOW — Acceptance (= tests)\n- a.\n"
        _, out = self._check({"NEED-X-001.md": need})
        self.assertIn("need has no requirement that satisfies it", out)

    def test_satisfied_need_not_orphan(self):  # verifies: ARCH-TRACE-020#CASE-2  # verifies: REQ-TRACE-934#CASE-3
        need = REQ.format(id="NEED-X-001", status="confirmed", layer="need", extra="", title="N")
        need += "\n## WHAT — Contract (normative)\n- want.\n\n## HOW — Acceptance (= tests)\n- a.\n"
        files = {"NEED-X-001.md": need,
                 "A-FOO-001.md": self._feature("A-FOO-001", "satisfies: [NEED-X-001]\n"),
                 "mod.py": "# {}: A-FOO-001\ndef test_a():\n    pass\n".format("tested" + "-by") +
                           "# {}: A-FOO-001\n".format("implements")}
        _, out = self._check(files)
        self.assertNotIn("unaddressed", out)
        self.assertNotIn("NEED-X-001: need has no", out)

    def test_need_exempt_from_implements_and_tested(self):  # verifies: ARCH-TRACE-020#CASE-3  # verifies: REQ-CHECK-828#CASE-6  # verifies: REQ-CHECK-829#CASE-5  # verifies: REQ-TRACE-935#CASE-3
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

    def test_show_prints_upstream_both_directions(self):  # verifies: ARCH-TRACE-020#CASE-4  # verifies: REQ-TRACE-935#CASE-5
        need = REQ.format(id="NEED-X-001", status="confirmed", layer="need", extra="", title="N")
        feat = self._feature("A-FOO-001", "satisfies: [NEED-X-001]\n")
        reqs = {"NEED-X-001": {"meta": {"status": "confirmed", "layer": "need"}, "body": need,
                               "path": "requirements/NEED-X-001.md"},
                "A-FOO-001": {"meta": {"status": "confirmed", "layer": "feature",
                                       "satisfies": ["NEED-X-001"]}, "body": feat,
                              "path": "requirements/A-FOO-001.md"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_show(R.Workspace(reqs, {}), "A-FOO-001")
        self.assertIn("Satisfies (upstream): NEED-X-001", buf.getvalue())
        buf2 = io.StringIO()
        with redirect_stdout(buf2):
            R.cmd_show(R.Workspace(reqs, {}), "NEED-X-001")
        self.assertIn("Satisfied by: A-FOO-001", buf2.getvalue())

    def test_map_data_carries_upstream(self):  # verifies: REQ-TRACE-935#CASE-6
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


class MilestoneGate(unittest.TestCase):  # tested-by: ARCH-CHECK-006
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
                R.cmd_check(R.Workspace(reqs, members, d, d), False)
            return buf.getvalue()

    def test_malformed_milestone_warns(self):  # verifies: ARCH-CHECK-006#CASE-6  # verifies: REQ-CHECK-830#CASE-2
        for bad in ("next", "1.14", "V1.0", "v1.14-beta"):
            self.assertIn("malformed", self._warns(bad), bad)

    def test_valid_milestone_silent(self):  # verifies: ARCH-CHECK-006#CASE-6  # verifies: REQ-CHECK-830#CASE-1
        for ok in ("v1.14", "v1.04", "v2"):
            self.assertNotIn("malformed", self._warns(ok), ok)

    def test_deprecated_milestone_exempt(self):  # verifies: ARCH-CHECK-006#CASE-6  # verifies: REQ-CHECK-830#CASE-3
        self.assertNotIn("malformed", self._warns("next", status="deprecated"))


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
                R.cmd_check(R.Workspace(reqs, members, rdir), True)
            # Now change the body so the hash differs
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   REQ.format(id="REQ-A-001", status="in-progress",
                              layer="bus", extra="", title="T") +
                   "\n## WHAT — Contract\n- changed contract\n")
            reqs2 = R.load_requirements(rdir)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_check(R.Workspace(reqs2, members, rdir), True)
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
                R.cmd_check(R.Workspace(reqs, {}, rdir), True)
            # Now delete the requirement file (simulate removal)
            os.remove(os.path.join(rdir, "REQ-A-001.md"))
            reqs2 = R.load_requirements(rdir)  # empty
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                R.cmd_check(R.Workspace(reqs2, {}, rdir), True)
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
            R.cmd_check(R.Workspace(reqs, members, rdir), True)
        return rdir

    def test_strict_clean_exits_0(self):
        """--strict: clean corpus exits 0."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._setup_confirmed(d)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(R.Workspace(reqs, members, rdir), False, True)
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
                rc_normal = R.cmd_check(R.Workspace(reqs, members, rdir, d), False)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc_strict = R.cmd_check(R.Workspace(reqs, members, rdir, d), False, True)
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
                rc_normal = R.cmd_check(R.Workspace(R.load_requirements(rdir), members, rdir), False)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc_strict = R.cmd_check(R.Workspace(R.load_requirements(rdir), members, rdir), False, True)
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
            R.cmd_check(R.Workspace(reqs, members, rdir), True)
        return rdir

    def test_json_clean_ok_true(self):
        """--json: clean corpus → ok=true, errors=[], exit 0."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._make_clean_corpus(d)
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(R.Workspace(reqs, members, rdir), False, as_json=True)
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
                rc = R.cmd_check(R.Workspace(reqs, members, rdir), False, as_json=True)
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
                rc = R.cmd_check(R.Workspace(reqs, members, rdir), False, as_json=True)
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
                rc = R.cmd_check(R.Workspace(reqs, members, rdir), False, as_json=True)
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
                R.cmd_check(R.Workspace(reqs, members, rdir), False, as_json=True)
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
                rc = R.cmd_check(R.Workspace(reqs, members, rdir), True, since="nonexistent-sha-9999")
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
                R.cmd_check(R.Workspace(reqs, members, rdir, d), True, since=base_ref)
            # The check ran: REQ-A-001 member (src_a.py) was changed, so it was
            # included; REQ-B-002 was untouched.  Just verify it completes without
            # error (both are clean, no dangling tags).
            # Re-run and capture rc:
            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc = R.cmd_check(R.Workspace(reqs, members, rdir, d), False, since=base_ref)
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
                    rc = R.cmd_check(R.Workspace(reqs, members, rdir), True, since="HEAD~1")
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
                rc = R.cmd_check(R.Workspace(reqs, members, lrdir, link), False, since=base_ref)
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
                rc = R.cmd_check(R.Workspace(reqs, members, rdir, sub), False, since=base_ref)
            self.assertEqual(
                rc, 1,
                "a dangling tag in a changed file under a subdir code_root must be caught")

    def test_since_update_lock_preserves_full_memberlock(self):  # verifies: REQ-MEMBERDRIFT-880#CASE-5
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
                R.cmd_check(R.Workspace(reqs, members, rdir, d), True)
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
                R.cmd_check(R.Workspace(reqs, members, rdir, d), True, since=base_ref)
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
                R.cmd_check(R.Workspace(reqs, members, rdir, d), False, since=base_ref)


    def test_since_unrelated_member_change_does_not_false_flag_implements(self):  # bug: check-since-filtered-existence
        """A confirmed requirement whose `implements:` tag file is UNCHANGED but whose
        `tested-by:` file changed under --since must not get a false 'no implements:
        tag found' error — the existence check must read the FULL scan, not the
        --since-filtered one."""
        with tempfile.TemporaryDirectory() as d:
            self._init_git_repo(d)
            rdir = os.path.join(d, "requirements")
            _write(os.path.join(rdir, "REQ-A-001.md"),
                   "---\nid: REQ-A-001\nstatus: confirmed\nlayer: bus\n---\n\n# T\n\n"
                   "## WHAT — Contract\n- shall do X\n\n## HOW — Acceptance\n- AC-1\n")
            _write(os.path.join(d, "src_a.py"), "# {}: REQ-A-001\n".format("impl" + "ements"))
            _write(os.path.join(d, "test_a.py"), "# {}: REQ-A-001\ndef test_a():\n    pass\n"
                   .format("tested" + "-by"))
            self._commit_all(d, "baseline")
            base_ref = subprocess.run(
                ["git", "-C", d, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True).stdout.strip()
            # Change ONLY test_a.py (the tested-by file); src_a.py (implements) is untouched.
            _write(os.path.join(d, "test_a.py"), "# {}: REQ-A-001\ndef test_a():\n    pass  # changed\n"
                   .format("tested" + "-by"))
            self._commit_all(d, "touch-test-only")

            reqs = R.load_requirements(rdir)
            members = R.scan_members(d, rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(R.Workspace(reqs, members, rdir, d), False, since=base_ref)
            self.assertNotIn("no implements: tag found in code", buf.getvalue())
            self.assertEqual(rc, 0)


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


class Site(unittest.TestCase):  # tested-by: ARCH-SITE-026  # tested-by: REQ-SITE-924
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
                    R.cmd_site(R.Workspace(
                        R.load_requirements(os.path.join(d, "requirements")), {}),
                        d, target, ["nav"])
            html = open(target, encoding="utf-8").read()
            self.assertNotIn("<script>bad</script>", html)
            self.assertIn("&lt;script&gt;", html)

    def test_render_nav_omits_absent_targets(self):  # verifies: REQ-SITE-924#CASE-3
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

    def test_render_nav_wraps_in_nav_links_class(self):  # bug: site-region-wrapper-css-mismatch
        """The injected nav markup must use the `nav-links` class SITE_TEMPLATE's CSS
        actually targets (`.nav-links` / `.nav-links a`) — a made-up wrapper class
        matches no selector and leaves the nav unstyled."""
        ctx = {"repo_url": "https://github.com/o/r", "map_ok": True, "diagram_rel": "d.html"}
        nav = R._render_region("nav", ctx)
        self.assertIn('class="nav-links"', nav)
        self.assertNotIn("reqmap-nav", nav)

    def test_render_stats_has_no_extra_wrapper(self):  # bug: site-region-wrapper-css-mismatch
        """`.stat` cards must be emitted with NO extra wrapper div: SITE_TEMPLATE
        already provides the `.stats` grid container around the injected region, and
        `.stat` must be its DIRECT CHILD for the 6-column grid CSS to apply."""
        data = {"nodes": [{"id": "A-1", "layer": "bus", "status": "confirmed"}], "edges": []}
        ctx = R._site_context_from_data(data, repo_url=None, map_ok=False, diagram_rel=None)
        stats = R._render_region("stats", ctx)
        self.assertNotIn("reqmap-stats", stats)
        self.assertTrue(stats.startswith('<div class="stat">'))

    def _seed(self, d):
        """Minimal reqs dir with one confirmed requirement so site can build map data."""
        reqs = os.path.join(d, "requirements"); os.makedirs(reqs)
        with open(os.path.join(reqs, "AREA-X-001.md"), "w", encoding="utf-8") as f:
            f.write("---\nid: AREA-X-001\nstatus: confirmed\nlayer: feature\n---\n# X\n> why\n")
        return reqs

    def test_attach_is_idempotent(self):  # verifies: REQ-SITE-924#CASE-1
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            open(page, "w", encoding="utf-8").write("<body>\n<h1>Mine</h1>\n</body>")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(R.Workspace(r, m), d, page, ["nav", "stats"])
            first = open(page, encoding="utf-8").read()
            R.cmd_site(R.Workspace(r, m), d, page, ["nav", "stats"])
            second = open(page, encoding="utf-8").read()
            self.assertEqual(first, second)
            self.assertIn("<h1>Mine</h1>", second)

    def test_no_remote_degrades(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            open(page, "w", encoding="utf-8").write("<body></body>")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            rc = R.cmd_site(R.Workspace(r, m), d, page, ["nav"])
            self.assertEqual(rc, 0)
            self.assertNotIn("GitHub", open(page, encoding="utf-8").read())

    def test_scaffold_writes_full_page(self):  # verifies: REQ-SITE-924#CASE-2
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            target = os.path.join(d, "docs", "architecture.html")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(R.Workspace(r, m), d, target, ["nav", "stats"])
            html = open(target, encoding="utf-8").read()
            self.assertIn("<!--##REQMAP:NAV##-->", html)
            self.assertIn("<!--##REQMAP:STATS##-->", html)
            self.assertIn("<!-- author me -->", html)

    def test_init_scaffolds_site_when_absent(self):  # verifies: REQ-SITE-924#CASE-5
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            open(os.path.join(d, "a.py"), "w").write("# implements: AREA-X-001\nx = 1\n")
            R.cmd_init(os.path.join(d, "requirements"), d, no_site=False)
            page = os.path.join(d, "docs", "architecture.html")
            self.assertTrue(os.path.isfile(page))
            self.assertIn("<!--##REQMAP:NAV##-->", open(page, encoding="utf-8").read())

    def test_init_no_site_flag_skips(self):  # verifies: REQ-SITE-924#CASE-5
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            open(os.path.join(d, "a.py"), "w").write("x = 1\n")
            R.cmd_init(os.path.join(d, "requirements"), d, no_site=True)
            self.assertFalse(os.path.isfile(os.path.join(d, "docs", "architecture.html")))

    def test_map_check_flags_stale_stats_region(self):  # verifies: REQ-SITE-924#CASE-6
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d); os.makedirs(os.path.join(d, "docs"))
            page = os.path.join(d, "docs", "architecture.html")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(R.Workspace(r, m), d, page, ["stats"])
            data = R._build_map_data(r, m); data["repo"] = R._repo_name(d)
            self.assertEqual(R._map_check(data, reqs, d), 0)        # fresh
            cur = open(page, encoding="utf-8").read()
            tampered = cur.replace(R._extract_region(cur, "stats"), "TAMPERED")
            open(page, "w", encoding="utf-8").write(tampered)
            self.assertEqual(R._map_check(data, reqs, d), 1)        # stale stats -> exit 1

    def test_site_detect_runs(self):
        """`site` folded into `sync` in v4.0.0; detect mode stays as a function, and
        `sync` refreshes an existing page through the same call."""
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            reqs = R.load_requirements(os.path.join(d, "requirements"))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = R.cmd_site(R.Workspace(reqs, {}), d, detect=True)
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

    def test_engine_never_touches_excalidraw_builder(self):  # verifies: REQ-SITE-924#CASE-4
        src = open(R.__file__, encoding="utf-8").read()
        self.assertNotIn("excalidraw_builder", src)   # link-only; no import/exec coupling


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

    def test_js_line_terminators_never_reach_the_script_blob_raw(self):  # tested-by: ARCH-VIEWER-007  # verifies: REQ-VIEWER-941#CASE-5
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


class PythonFloor(unittest.TestCase):  # tested-by: ARCH-PYFLOOR-040  # tested-by: REQ-PYFLOOR-902
    """The declared support floor. The predicate is tested rather than a real old
    interpreter: CI cannot install a 3.8 to watch reqmap refuse it, and a floor that is
    only asserted in prose is the failure mode this project exists to prevent."""

    def test_below_floor_names_both_versions_and_the_fix(self):  # verifies: REQ-PYFLOOR-902#CASE-4  # verifies: REQ-PYFLOOR-902#CASE-5
        msg = R._python_floor_error((3, 8, 10))
        self.assertIsNotNone(msg)
        self.assertIn("3.9", msg)          # required
        self.assertIn("3.8", msg)          # running
        self.assertIn("stdlib-only", msg)  # the fix: any newer interpreter, no install
        self.assertTrue(msg.isascii(), "message must survive a legacy Windows codepage")

    def test_at_and_above_floor_report_nothing(self):  # verifies: REQ-PYFLOOR-902#CASE-5
        for v in [R.MIN_PYTHON, (3, 12, 0), (3, 14, 1), (4, 0, 0)]:
            self.assertIsNone(R._python_floor_error(v), v)

    def test_running_interpreter_is_at_or_above_the_declared_floor(self):
        self.assertIsNone(R._python_floor_error())

    def test_main_refuses_an_old_interpreter_with_exit_2(self):  # verifies: REQ-PYFLOOR-902#CASE-3  # verifies: REQ-PYFLOOR-902#CASE-4
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

    def test_floor_matches_the_oldest_python_in_the_ci_matrix(self):  # verifies: REQ-PYFLOOR-902#CASE-2
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


class IntentVerbDispatch(unittest.TestCase):  # tested-by: ARCH-CHECK-006
    """The renamed CLI surface: gate (report-only) + check (deprecation alias)."""

    def _run(self, *args, cwd):
        reqmap = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reqmap.py")
        return subprocess.run([sys.executable, "-X", "utf8", reqmap, *args],
                              cwd=cwd, capture_output=True, text=True)

    def _seed(self, d):
        rdir = os.path.join(d, "requirements")
        _write(os.path.join(rdir, "REQ-A-001.md"),
               REQ.format(id="REQ-A-001", status="draft", layer="feature", extra="", title="T"))

    def test_gate_runs_report_only(self):  # verifies: REQ-CHECK-833#CASE-3
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            r = self._run("gate", "--root", d, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("lock updated", r.stdout)  # gate never touches the lock

    def test_removed_verbs_are_unknown(self):
        """v4.0.0 cut five verbs and folded six more into gate/sync/next. A removed
        verb must fail loudly at the parser, never fall through to a silent no-op."""
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            for verb in ("check", "map", "lint", "health", "scan", "export",
                         "plan", "coverage", "site", "findings", "gen-integration"):
                r = self._run(verb, "--root", d, cwd=d)
                self.assertNotEqual(r.returncode, 0, "{} still dispatches".format(verb))
                self.assertIn("invalid choice", r.stderr.lower())


    def test_new_verbs_dispatch(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            for args in (("gate", "--dupes"), ("gate", "--design")):
                r = self._run(*args, "--root", d, cwd=d)
                self.assertEqual(r.returncode, 0, f"{args}: {r.stderr}")
            # `draft --plan` (cmd_candidates) always prints its extraction plan to
            # stdout — a non-empty stdout proves the branch is wired, not falling through
            # the dispatch chain to a no-op return (which would print nothing).
            r = self._run("init", "--plan", "--root", d, cwd=d)
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
            self.assertIn("Author:", r.stdout)
            self.assertIn("Build:", r.stdout)
            self.assertIn("Read:", r.stdout)
            self.assertIn("gate", r.stdout)
            self.assertIn("sync", r.stdout)

    def test_new_from_todo_scaffolds_and_old_verb_gone(self):  # verifies: REQ-PROMOTE-TODO-897#CASE-1
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "requirements"), exist_ok=True)
            _write(os.path.join(d, "TODO.md"), "# TODO\n\n## v1.0\n- [ ] Make widget\n")
            r = self._run("new", "--from-todo", "Make widget", "--id", "REQ-W-001",
                          "--root", d, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(d, "requirements", "REQ-W-001.md")))
            r2 = self._run("promote-todo", "Make widget", "--id", "REQ-W-002", "--root", d, cwd=d)
            self.assertEqual(r2.returncode, 2)  # old verb removed


class SyncDriftGuard(unittest.TestCase):  # tested-by: ARCH-CHECK-006
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

    def test_sync_demotes_confirmed_drift_without_flag(self):  # verifies: REQ-PROMOTE-974#CASE-1
        """An edited confirmed contract used to BLOCK the lock; it now loses its
        confirmation and the baseline advances. The safe outcome became the default."""
        with tempfile.TemporaryDirectory() as d:
            rdir = self._confirmed_repo(d)
            reqs = R.load_requirements(rdir); members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(R.Workspace(reqs, members, rdir, d), True)  # seed lock
            lock_before = open(R.lock_path(rdir), encoding="utf-8").read()
            # edit the contract -> drift
            self._confirmed_repo(d, body_tail="\nMore contract text that changes the hash.\n")
            reqs2 = R.load_requirements(rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs2, members, rdir, d), True, accept_drift=False)
            self.assertIn("demoted:", buf.getvalue())
            self.assertNotEqual(open(R.lock_path(rdir), encoding="utf-8").read(), lock_before)

    def test_sync_accept_drift_advances_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            rdir = self._confirmed_repo(d)
            reqs = R.load_requirements(rdir); members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(R.Workspace(reqs, members, rdir, d), True)
            lock_before = open(R.lock_path(rdir), encoding="utf-8").read()
            self._confirmed_repo(d, body_tail="\nMore contract text that changes the hash.\n")
            reqs2 = R.load_requirements(rdir)
            with redirect_stdout(io.StringIO()):
                rc = R.cmd_check(R.Workspace(reqs2, members, rdir, d), True, accept_drift=True)
            self.assertEqual(rc, 0)
            self.assertNotEqual(open(R.lock_path(rdir), encoding="utf-8").read(), lock_before)  # advanced

    def test_json_path_survives_a_demotion(self):  # guard the as_json early-return
        with tempfile.TemporaryDirectory() as d:
            rdir = self._confirmed_repo(d)
            reqs = R.load_requirements(rdir); members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(R.Workspace(reqs, members, rdir, d), True)
            self._confirmed_repo(d, body_tail="\nMore contract text that changes the hash.\n")
            reqs2 = R.load_requirements(rdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(R.Workspace(reqs2, members, rdir, d), True, as_json=True, accept_drift=False)
            # drift no longer blocks the lock, so the json path reports a clean run;
            # the demotion is what carries the signal, and it is printed by name.
            self.assertEqual(rc, 0)
            self.assertIn("demoted:", buf.getvalue())
            self.assertEqual(json.loads(buf.getvalue().strip().splitlines()[-1])["ok"], True)


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
        expected = {"reqmap_" + c.replace("-", "_")
                    for c, s in R.COMMANDS.items() if not s.get("internal")}
        self.assertEqual(names, expected)

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


class BugHuntGateDrift(unittest.TestCase):  # tested-by: ARCH-CHECK-006  # tested-by: ARCH-DRIFT-003  # tested-by: REQ-DRIFT-841
    def test_version_key_orders_double_digit_suffix(self):
        self.assertGreater(R._ver_key("2026-06-03.10"), R._ver_key("2026-06-03.9"))
        self.assertGreater(R._ver_key("2026-06-04"), R._ver_key("2026-06-03.9"))
        self.assertGreater(R._ver_key("2026-06-03.2"), R._ver_key("2026-06-03"))

    def test_go_lowercase_func_is_not_a_test(self):  # verifies: REQ-TESTLINK-931#CASE-3
        self.assertIsNone(R._DEF_TEST_RE.search("func testHelper() {"))
        self.assertIsNotNone(R._DEF_TEST_RE.search("func TestThing(t *testing.T) {"))
        self.assertIsNotNone(R._DEF_TEST_RE.search("def test_x():"))
        self.assertIsNotNone(R._DEF_TEST_RE.search("    function testFoo() {"))

    def test_binding_hash_detects_cross_section_move(self):  # verifies: REQ-DRIFT-841#CASE-3
        a = "## WHAT — Contract\n- A\n## HOW — Acceptance\n- B\n- C\n"
        b = "## WHAT — Contract\n- A\n- B\n## HOW — Acceptance\n- C\n"
        self.assertNotEqual(R.binding_hash(a), R.binding_hash(b))

    def test_binding_hash_detects_indent_change(self):  # verifies: REQ-DRIFT-841#CASE-3
        a = "## WHAT — Contract\n- A\n  nested\n"
        b = "## WHAT — Contract\n- A\nnested\n"
        self.assertNotEqual(R.binding_hash(a), R.binding_hash(b))


class CheckAliasDriftGuard(unittest.TestCase):  # tested-by: ARCH-CHECK-006
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


class BugHuntMutateAnalyze(unittest.TestCase):  # tested-by: ARCH-PROMOTE-011  # tested-by: ARCH-PROMOTE-TODO-001  # tested-by: ARCH-NEXT-013
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


class BugHuntSince(unittest.TestCase):  # tested-by: ARCH-CHECK-006
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


class RoadmapSignals(unittest.TestCase):  # tested-by: ARCH-ROADMAP-038  # tested-by: REQ-ROADMAP-907
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


class ViewerDataSync(unittest.TestCase):  # tested-by: ARCH-VIEWER-007
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

    def test_note_names_recorded_member_and_code_flag(self):  # verifies: REQ-NEXT-884#CASE-7  # verifies: ARCH-NEXT-013#CASE-10
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

    def test_no_note_without_committed_map(self):  # verifies: REQ-NEXT-884#CASE-7
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


class UntaggedIgnoreBucket(unittest.TestCase):  # tested-by: ARCH-NEXT-013
    def test_meta_prose_is_not_untagged(self):  # verifies: REQ-NEXT-884#CASE-5
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


class EngineVersionFreshness(unittest.TestCase):  # tested-by: ARCH-MAP-007  # tested-by: REQ-MAP-871
    def test_engine_version_alone_is_not_stale(self):  # verifies: REQ-MAP-871#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            _write(os.path.join(rd, "AREA-A-001.md"), REQ.format(id="AREA-A-001", status="baseline", layer="bus", extra="", title="A"))
            reqs = R.load_requirements(rd)
            with redirect_stdout(io.StringIO()):
                R.cmd_map(R.Workspace(reqs, {}, rd), d)
            p = os.path.join(rd, "_map.json")
            with open(p, encoding="utf-8") as f:
                text = f.read()
            self.assertIn('"engine_version": "' + R.MAP_ENGINE_VERSION + '"', text)
            _write(p, text.replace('"engine_version": "' + R.MAP_ENGINE_VERSION + '"', '"engine_version": "2000-01-01"'))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_map(R.Workspace(reqs, {}, rd), d, True)
            self.assertEqual(code, 0, buf.getvalue())


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


class ClosedPipe(unittest.TestCase):  # tested-by: ARCH-PIPE-046  # tested-by: REQ-PIPE-893
    def test_broken_pipe_and_windows_einval_exit_zero(self):  # verifies: REQ-PIPE-893#CASE-1
        def boom_pipe():
            raise BrokenPipeError()
        def boom_einval():
            raise OSError(errno.EINVAL, "Invalid argument")
        with mock.patch.object(R, "_pipe_closed", return_value=0):
            self.assertEqual(R._run_cli(boom_pipe), 0)
            self.assertEqual(R._run_cli(boom_einval), 0)

    def test_other_oserror_propagates(self):  # verifies: REQ-PIPE-893#CASE-2
        def boom():
            raise OSError(errno.ENOENT, "missing")
        with self.assertRaises(OSError):
            R._run_cli(boom)

    def test_normal_exit_code_passes_through(self):  # verifies: REQ-PIPE-893#CASE-3
        self.assertEqual(R._run_cli(lambda: 3), 3)
        self.assertEqual(R._run_cli(lambda: None), 0)


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


class SpecLevel(unittest.TestCase):  # tested-by: ARCH-LEVEL-051  # tested-by: REQ-LEVEL-862
    """The `level:` axis: validated, optional, and granting no exemption."""

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

    def test_a_known_level_is_accepted(self):  # verifies: ARCH-LEVEL-051#CASE-1  # verifies: REQ-LEVEL-862#CASE-1
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="feature",
            extra="level: architecture\n", title="T")})
        self.assertNotIn("invalid level", out)

    def test_an_unknown_level_is_an_error(self):  # verifies: ARCH-LEVEL-051#CASE-2  # verifies: REQ-LEVEL-862#CASE-2  # verifies: REQ-LEVEL-862#CASE-6
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="feature",
            extra="level: detailed\n", title="T")})
        self.assertIn("invalid level", out)
        self.assertEqual(code, 1)

    def test_absent_level_says_nothing(self):  # verifies: ARCH-LEVEL-051#CASE-3  # verifies: REQ-LEVEL-862#CASE-3
        _, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="baseline", layer="feature", extra="", title="T")})
        self.assertNotIn("level", out.replace("levels", ""))

    def test_a_level_grants_no_implementation_exemption(self):  # verifies: ARCH-LEVEL-051#CASE-4  # verifies: REQ-LEVEL-862#CASE-4
        # architecture owns code, unlike `aggregate` — the whole reason the two axes stay
        # separate. A level must never remove a requirement from the confirmed-code rule.
        code, out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="confirmed", layer="feature",
            extra="level: architecture\n", title="T")})
        self.assertIn("no implements", out)
        self.assertEqual(code, 1)
        self.assertNotIn("architecture", str(R.IMPL_EXEMPT_LAYERS))


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


class VRungs(unittest.TestCase):  # tested-by: ARCH-VRUNGS-054
    """Each specification level answered by the verification level that discharges it."""

    def _check(self, files, levels):
        with tempfile.TemporaryDirectory() as d:
            for name, body in files.items():
                _write(os.path.join(d, name), body)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_check(R.Workspace(reqs, members, d, d, None, levels), False)
            return buf.getvalue()

    def _req(self, rid, level):
        return REQ.format(id=rid, status="confirmed", layer="feature",
                          extra="level: %s\n" % level, title="T")

    def test_a_level_verified_at_the_wrong_depth_warns(self):  # verifies: ARCH-VRUNGS-054#CASE-1
        out = self._check({"A-SYS-001.md": self._req("A-SYS-001", "system")},
                          {"A-SYS-001": {"unit": [("t.py", 1)]}})
        self.assertIn("not @system", out)

    def test_the_paired_level_is_silent(self):  # verifies: ARCH-VRUNGS-054#CASE-2
        out = self._check({"A-ARCH-001.md": self._req("A-ARCH-001", "architecture")},
                          {"A-ARCH-001": {"integration": [("t.py", 1)]}})
        self.assertNotIn("not @integration", out)

    def test_no_levelled_link_is_never_judged(self):  # verifies: ARCH-VRUNGS-054#CASE-3
        out = self._check({"A-SYS-001.md": self._req("A-SYS-001", "system")}, {})
        self.assertNotIn("not @system", out)

    def test_no_declared_level_is_never_judged(self):  # verifies: ARCH-VRUNGS-054#CASE-3
        out = self._check({"A-FOO-001.md": REQ.format(
            id="A-FOO-001", status="confirmed", layer="feature", extra="", title="T")},
            {"A-FOO-001": {"unit": [("t.py", 1)]}})
        self.assertNotIn("not @", out)

    def test_the_pairing_is_the_v(self):
        self.assertEqual(R.LEVEL_TEST_PAIR,
                         {"system": "system", "architecture": "integration", "code": "unit"})


class MapHierarchy(unittest.TestCase):  # tested-by: ARCH-MAPDIAGRAMS-055  # tested-by: REQ-MAPDIAGRAMS-874, REQ-MAPDIAGRAMS-875, REQ-MAPDIAGRAMS-876, REQ-MAPDIAGRAMS-877, REQ-MAPDIAGRAMS-878
    """The Specification Hierarchy: the satisfies axis, with the code level counted."""

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

    def test_it_draws_the_two_upper_levels_and_counts_the_third(self):  # verifies: ARCH-MAPDIAGRAMS-055#CASE-2  # verifies: REQ-MAPDIAGRAMS-875#CASE-2  # verifies: REQ-MAPDIAGRAMS-875#CASE-3
        out = R._mermaid_hierarchy(self.DATA)
        self.assertIn("SYS_A_101", out)
        self.assertIn("REQ_B_001", out)
        self.assertNotIn("REQ_B_200", out)          # the code level is counted, never drawn
        self.assertIn("2 code", out)                # ...and its count lands on the parent
        self.assertIn("SYS_A_101 --> REQ_B_001", out)

    def test_it_reads_satisfies_not_depends_on(self):  # verifies: ARCH-MAPDIAGRAMS-055#CASE-2  # verifies: REQ-MAPDIAGRAMS-875#CASE-1
        # depends_on and satisfies are different axes; only the latter forms a hierarchy.
        d = dict(self.DATA, upstream_edges=[], edges=[["REQ-B-001", "SYS-A-101"]])
        self.assertNotIn("-->", R._mermaid_hierarchy(d))

    def test_an_empty_corpus_draws_nothing(self):
        self.assertEqual(R._mermaid_hierarchy({"nodes": [], "edges": [], "upstream_edges": []}), "")

    def test_a_promoted_system_node_still_shows_its_code_count(self):
        # ADR-0024: a corpus that collapsed `architecture` into `system` carries two
        # populations under `level: system` — a root need with no code children of its
        # own, and a promoted grouping node whose code children are counted same as an
        # `architecture` parent's always were. Both must render correctly from `level:`
        # alone no longer being able to tell them apart.
        d = {
            "nodes": [
                {"id": "SYS-A-101", "level": "system", "layer": "need", "status": "confirmed",
                 "area": "SYS", "members": [], "deps": [], "risks": []},
                {"id": "SYS-B-001", "level": "system", "layer": "feature", "status": "confirmed",
                 "area": "SYS", "members": [], "deps": [], "risks": []},
                {"id": "REQ-B-200", "level": "code", "layer": "feature", "status": "draft",
                 "area": "REQ", "members": [], "deps": [], "risks": []},
            ],
            "edges": [],
            "upstream_edges": [["SYS-B-001", "SYS-A-101"], ["REQ-B-200", "SYS-B-001"]],
        }
        out = R._mermaid_hierarchy(d)
        self.assertIn("1 code", out)                 # SYS-B-001's promoted fan-out is counted
        self.assertIn("SYS_A_101[[SYS-A-101]]", out)  # the true root stays bare + double-boxed
        self.assertIn("SYS_A_101 --> SYS_B_001", out)

    def test_the_document_carries_five_blocks(self):  # verifies: ARCH-MAPDIAGRAMS-055#CASE-1  # verifies: REQ-MAPDIAGRAMS-874#CASE-2
        md = R._build_md_text(dict(self.DATA, todos=[]))
        self.assertEqual(md.count("```mermaid"), 5)
        self.assertIn("Specification Hierarchy", md)

    def test_the_legend_matches_the_diagram_order(self):  # bug: legend-md-missing-hierarchy-entry  # verifies: REQ-MAPDIAGRAMS-874#CASE-3
        # _LEGEND_MD must carry one entry per diagram _build_md_text emits, in the same
        # order -- a missing entry shifts every caption by one and leaves the LAST
        # diagram (Risk & Unknowns) with an empty legend.
        self.assertEqual(len(R._LEGEND_MD), 5)
        md = R._build_md_text(dict(self.DATA, todos=[]))
        idx = md.index("## Specification Hierarchy")
        self.assertIn("satisfies", md[idx:idx + 400])
        idx = md.index("## Risk & Unknowns")
        self.assertIn("unimplemented", md[idx:idx + 400])

    def test_the_graph_carries_the_satisfies_edges(self):
        # They were computed since ARCH-TRACE-020 and dropped by _build_json_text until now.
        payload = json.loads(R._build_json_text(dict(self.DATA, repo=None, todos=[])))
        self.assertEqual(len(payload["upstream_edges"]), 3)


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


class Redundancy(unittest.TestCase):  # tested-by: ARCH-REDUNDANCY-058
    """`_redundant_groups` is the exact-match floor under `dupes`: no threshold, so a
    group is a duplicate by construction rather than a judgement call."""

    def _req(self, clause, status="confirmed"):
        return {"meta": {"status": status},
                "body": "# T\n\n## Description\n- " + clause + "\n\n"
                        "## Cases (= tests)\nCASE-1\n  Then it holds\n"}

    def test_identical_contracts_group_together(self):  # verifies: ARCH-REDUNDANCY-058#CASE-1
        reqs = {"A-X-001": self._req("`x` does the thing."),
                "A-Y-002": self._req("`x` does the thing."),
                "A-Z-003": self._req("`y` does something else.")}
        self.assertEqual(R._redundant_groups(reqs), [["A-X-001", "A-Y-002"]])

    def test_case_and_whitespace_do_not_hide_a_duplicate(self):  # verifies: ARCH-REDUNDANCY-058#CASE-2
        reqs = {"A-X-001": self._req("`x` does   the thing."),
                "A-Y-002": self._req("`X` DOES the thing.")}
        self.assertEqual(R._redundant_groups(reqs), [["A-X-001", "A-Y-002"]])

    def test_a_different_clause_is_not_a_duplicate(self):  # verifies: ARCH-REDUNDANCY-058#CASE-3
        reqs = {"A-X-001": self._req("`x` does the thing."),
                "A-Y-002": self._req("`x` does the thing, twice.")}
        self.assertEqual(R._redundant_groups(reqs), [])

    def test_draft_placeholders_are_not_duplicates_of_each_other(self):  # verifies: ARCH-REDUNDANCY-058#CASE-4
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

    def test_next_reports_the_group_and_writes_nothing(self):  # verifies: ARCH-NEXT-013#CASE-12  # verifies: ARCH-REDUNDANCY-058#CASE-5
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

    def test_gate_stays_silent_about_redundancy(self):  # verifies: ARCH-REDUNDANCY-058#CASE-5
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


# collected instead of 494, 16 silently skipped in the invocation
# CLAUDE.md documents. CI runs `-m unittest`, which imports the whole
# module first, so CI never saw the gap.


class GateRules(unittest.TestCase):  # tested-by: ARCH-RULES-059  # tested-by: REQ-RULES-947  # tested-by: REQ-RULES-948
    """The gate rule registry: one bus every consumer of 'what is wrong' reads."""

    def _run(self, files, **kw):
        with tempfile.TemporaryDirectory() as d:
            for name, text in files.items():
                _write(os.path.join(d, name), text)
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False, **kw)
            return code, buf.getvalue()

    def test_codes_are_unique_and_severities_valid(self):  # verifies: REQ-RULES-947#CASE-1  # verifies: ARCH-RULES-059#CASE-1
        ids = [r.id for r in R.GATE_RULES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(r.severity in ("error", "warn") for r in R.GATE_RULES))
        self.assertTrue(all(re.fullmatch(r"RM\d{3}", i) for i in ids))

    def test_duplicate_code_is_refused(self):  # verifies: REQ-RULES-947#CASE-2
        with self.assertRaises(ValueError):
            R.gate_rule("RM001", "warn")(lambda ctx: iter(()))
        self.assertEqual(sum(1 for r in R.GATE_RULES if r.id == "RM001"), 1)

    def test_strict_promotes_only_strict_rules(self):  # verifies: REQ-RULES-947#CASE-3
        with tempfile.TemporaryDirectory() as d:
            body = REQ.format(id="AREA-A-001", status="confirmed", layer="feature",
                              extra="milestone: nope\n", title="T") + "## Description\n- x\n## Cases\n- y\n"
            _write(os.path.join(d, "AREA-A-001.md"), body)
            _write(os.path.join(d, "impl.py"), tag("AREA-A-001") + "\n")
            R.save_lock(d, {"AREA-A-001": "0000deadbeef"})
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            ctx = R.GateContext(R.Workspace(reqs, members, d, d))
            ctx.full_member_hashes = None
            errors, warns = R.run_gate_rules(ctx, strict=True)
        self.assertIn("RM018", [e["rule"] for e in errors])          # DRIFT promoted
        self.assertIn("RM004", [w["rule"] for w in warns])           # milestone stays a warn
        self.assertNotIn("RM004", [e["rule"] for e in errors])

    def test_health_and_gate_agree_on_link_sync(self):  # verifies: REQ-RULES-947#CASE-4  # verifies: ARCH-RULES-059#CASE-2
        reqs = {"AREA-A-001": R.Requirement(meta={"id": "AREA-A-001", "status": "confirmed", "layer": "feature"},
                                            body="", path="x", block=0)}
        members = {"AREA-Z-999": [("implements", "z.py", 1)]}
        errs = R._link_sync_errors(reqs, members)
        self.assertEqual(len(errs), 2)
        self.assertTrue(any("dangling tag" in e for e in errs))
        self.assertTrue(any("no implements: tag" in e for e in errs))

    def test_source_repo_only_rule_is_skipped_in_a_consumer(self):  # verifies: REQ-RULES-947#CASE-5
        files = {
            "AREA-A-001.md": REQ.format(id="AREA-A-001", status="confirmed", layer="feature",
                                        extra="", title="T") + "## Description\n- the real clause\n## Cases\n- y\n",
            "impl.py": tag("AREA-A-001") + "\n",
            os.path.join("app", "src", "lib", "data.js"):
                'const BAKED = [\n  { id:"AREA-A-001", contract:[ "a different clause" ] }\n];\n',
        }
        _code, out = self._run(files)
        self.assertNotIn("RM017", out)
        self.assertNotIn("data.js out of sync", out)

    def test_code_is_printed_with_severity(self):  # verifies: REQ-RULES-948#CASE-1
        files = {"AREA-A-001.md": REQ.format(id="AREA-A-001", status="baseline", layer="feature",
                                             extra="milestone: nope\n", title="T")}
        _code, out = self._run(files)
        self.assertIn("WARN  RM004 AREA-A-001: milestone 'nope' is malformed", out)

    def test_json_carries_findings_records(self):  # verifies: REQ-RULES-948#CASE-2
        files = {"AREA-A-001.md": REQ.format(id="AREA-A-001", status="baseline", layer="feature",
                                             extra="milestone: nope\n", title="T")}
        _code, out = self._run(files, as_json=True)
        data = json.loads(out)
        f = [x for x in data["findings"] if x["rule"] == "RM004"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["severity"], "warn")
        self.assertEqual(f[0]["rid"], "AREA-A-001")
        self.assertTrue(any("malformed" in w for w in data["warnings"]))

    def test_gate_exempt_silences_one_rule_for_one_requirement(self):  # verifies: REQ-RULES-948#CASE-3  # verifies: ARCH-RULES-059#CASE-3
        files = {
            "AREA-A-001.md": REQ.format(id="AREA-A-001", status="baseline", layer="feature",
                                        extra="milestone: nope\ngate_exempt: [RM004]\n", title="A"),
            "AREA-B-002.md": REQ.format(id="AREA-B-002", status="baseline", layer="feature",
                                        extra="milestone: nope\n", title="B"),
        }
        _code, out = self._run(files)
        self.assertNotIn("AREA-A-001: milestone", out)
        self.assertIn("RM004 AREA-B-002: milestone", out)

    def test_exemption_does_not_reach_another_rule(self):  # verifies: REQ-RULES-948#CASE-4
        files = {
            "AREA-A-001.md": REQ.format(id="AREA-A-001", status="confirmed", layer="feature",
                                        extra="milestone: nope\ngate_exempt: [RM004]\n", title="A")
                             + "## Description\n- x\n## Cases\n- y\n",
            "impl.py": tag("AREA-A-001") + "\n",
        }
        _code, out = self._run(files)
        # the RULE must not fire; a bare substring search would also match RM030 quoting
        # the exempted code back in its own message ("`gate_exempt: [RM004]` silences...")
        self.assertNotIn("RM004 AREA-A-001", out)
        self.assertIn("RM007 AREA-A-001: confirmed but no tested-by", out)


class Stage2Engine(unittest.TestCase):  # tested-by: ARCH-CONFIG-060  # tested-by: REQ-CONFIG-949  # tested-by: REQ-SCANCACHE-911  # tested-by: REQ-NEXT-886  # tested-by: REQ-SIMILAR-921  # tested-by: REQ-MAPDIAGRAMS-877
    """One walk with cache, the config file, and the verified-bug fixes of v3.3.0."""

    def _restore(self, *names):
        saved = {n: getattr(R, n) for n in names}
        self.addCleanup(lambda: [setattr(R, n, v) for n, v in saved.items()])

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
        for section in ("Gate", "Risk", "Duplicates", "Design", "Tag coverage",
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
            found = list(R._rule_exemption_without_reason(ctx))
        self.assertEqual(len(found), 1)
        rid, msg = found[0]
        self.assertEqual(rid, "REQ-A-001")
        self.assertIn("lint_exempt", msg)
        self.assertIn("ac-count-high", msg)

    def test_exemption_rule_is_never_promoted_by_strict(self):  # verifies: REQ-AUDIT-971#CASE-3
        rule = R.gate_rule_by_id("RM030")
        self.assertEqual(rule.severity, "warn")
        self.assertFalse(rule.strict)

    def test_oversize_findings_name_the_tool_that_splits(self):  # verifies: REQ-AUDIT-971#CASE-4
        body = "# T\n\n## Description\n" + "".join(
            "- Clause {}.\n".format(i) for i in range(3)) + "\n## Cases\n" + "".join(
            "CASE-{}\n  Then it holds\n".format(i) for i in range(1, R.LINT_AC_MAX + 3))
        found = R.lint_requirement("REQ-A-001", {"meta": {"status": "confirmed"}, "body": body})
        detail = " ".join(f["detail"] for f in found if f["check"] == "ac-count-high")
        self.assertIn("clarify REQ-A-001 --decompose", detail)

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


class Design(unittest.TestCase):  # tested-by: REQ-DESIGN-978  # tested-by: REQ-DESIGN-976  # tested-by: ARCH-DESIGN-061  # tested-by: REQ-DESIGN-950  # tested-by: REQ-DESIGN-951  # tested-by: REQ-DESIGN-952  # tested-by: REQ-DESIGN-953  # tested-by: REQ-DESIGN-954  # tested-by: REQ-DESIGN-955
    """`design`: advisory design candidates against the four pillars, never the gate."""

    def _kinds(self, src):
        # the pillar kinds only; the standards block has its own tests below
        return [f["kind"] for f in R._design_file("m.py", src) if f["pillar"] != "standards"]

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
                "                with a:\n                    if i:\n                        pass\n")
        self.assertIn("deep-nesting", self._kinds(deep))
        self.assertNotIn("deep-nesting", self._kinds("def ok(a):\n    if a:\n        return 1\n"))

    def test_prefix_family(self):  # verifies: REQ-DESIGN-950#CASE-4
        src = "".join("def _scan_{}(): pass\n".format(i) for i in range(6))
        f = [x for x in R._design_file("m.py", src) if x["kind"] == "prefix-family"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["name"], "scan")
        self.assertEqual(f[0]["pillar"], "abstraction")

    def test_shared_methods_and_duplicate_method(self):  # verifies: REQ-DESIGN-951#CASE-1
        src = ("class A:\n    def load(self): return 1\n    def save(self): return 2\n    def close(self): pass\n"
               "class B:\n    def load(self): return 3\n    def save(self): return 2\n    def close(self): pass\n")
        f = R._design_file("m.py", src)
        kinds = [x["kind"] for x in f]
        self.assertIn("shared-methods", kinds)
        dup = [x for x in f if x["kind"] == "duplicate-method"]
        self.assertEqual(sorted(x["name"] for x in dup), ["B.close", "B.save"])

    def test_related_classes_are_not_reported(self):  # verifies: REQ-DESIGN-951#CASE-2
        src = ("class Base:\n    pass\n"
               "class A(Base):\n    def load(self): pass\n    def save(self): pass\n    def close(self): pass\n"
               "class B(Base):\n    def load(self): pass\n    def save(self): pass\n    def close(self): pass\n")
        self.assertNotIn("shared-methods", self._kinds(src))

    def test_isinstance_chain_and_type_switch(self):  # verifies: REQ-DESIGN-951#CASE-3
        src = ("def f(x, kind):\n"
               "    if isinstance(x, int):\n        pass\n    elif isinstance(x, str):\n        pass\n"
               "    elif isinstance(x, list):\n        pass\n"
               "    if kind == 'a':\n        pass\n    elif kind == 'b':\n        pass\n"
               "    elif kind == 'c':\n        pass\n    elif kind == 'd':\n        pass\n")
        f = [x for x in R._design_file("m.py", src) if x["pillar"] != "standards"]
        self.assertEqual([x["kind"] for x in f], ["isinstance-chain", "type-switch"])
        self.assertEqual([x["name"] for x in f], ["x", "kind"])
        self.assertTrue(all(x["pillar"] == "polymorphism" for x in f))

    def test_short_chains_are_silent(self):  # verifies: REQ-DESIGN-951#CASE-4
        src = ("def f(x, kind):\n    if isinstance(x, int):\n        pass\n    elif isinstance(x, str):\n        pass\n"
               "    if kind == 'a':\n        pass\n    elif kind == 'b':\n        pass\n    elif kind == 'c':\n        pass\n")
        self.assertEqual(self._kinds(src), [])

    def test_report_groups_by_pillar_and_exits_zero(self):  # verifies: REQ-DESIGN-952#CASE-1  # verifies: ARCH-DESIGN-061#CASE-1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), "COUNT = 0\ndef bump():\n    global COUNT\n    COUNT += 1\n")
            _write(os.path.join(d, "tests", "test_m.py"), "COUNT = 0\ndef bump():\n    global COUNT\n    COUNT += 1\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_design(d)
            out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Encapsulation (1)", out)
        self.assertIn("m.py:2  global-state", out)
        self.assertNotIn("test_m.py", out)
        self.assertIn("Advisory only", out)
        self.assertIn("Standards (1)", out)   # `bump` is public and undocumented

    def test_json_output_and_clean_tree(self):  # verifies: REQ-DESIGN-952#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), 'def ok():\n    """Returns one."""\n    return 1\n')
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
        self.assertEqual(R._design_file("m.py", "def (:\n"), [])

    def test_standards_file_line_docstring_definitions(self):  # verifies: REQ-DESIGN-953#CASE-1
        saved = (R.DESIGN_FILE_MAX_LINES, R.DESIGN_FILE_MAX_FUNCS)
        self.addCleanup(lambda: (setattr(R, "DESIGN_FILE_MAX_LINES", saved[0]),
                                 setattr(R, "DESIGN_FILE_MAX_FUNCS", saved[1])))
        R.DESIGN_FILE_MAX_LINES, R.DESIGN_FILE_MAX_FUNCS = 5, 2
        src = ("def a():\n    return 1\n" "def b():\n    return 2\n" "def c():\n    return 3\n"
               "x = '" + "y" * 120 + "'\n")
        f = R._design_file("m.py", src)
        kinds = {x["kind"]: x for x in f}
        self.assertIn("file-too-long", kinds)
        self.assertIn("too-many-definitions", kinds)
        self.assertEqual(kinds["line-too-long"]["line"], 7)
        self.assertIn("1 line(s) wider than 100", kinds["line-too-long"]["detail"])
        self.assertIn("3 public definition(s)", kinds["missing-docstring"]["detail"])
        self.assertTrue(all(x["pillar"] == "standards" for x in f))

    def test_standards_are_silent_on_a_documented_small_file(self):  # verifies: REQ-DESIGN-953#CASE-2
        src = 'def a():\n    """Says a."""\n    return 1\n\ndef _helper():\n    return 2\n'
        self.assertEqual(self._kinds(src), [])

    def test_docstring_check_can_be_switched_off(self):  # verifies: REQ-DESIGN-953#CASE-3
        saved = R.DESIGN_DOCSTRING_PUBLIC
        self.addCleanup(setattr, R, "DESIGN_DOCSTRING_PUBLIC", saved)
        src = "def a():\n    return 1\n"
        kinds = lambda: [f["kind"] for f in R._design_file("m.py", src)]
        self.assertEqual(kinds(), ["missing-docstring"])
        R.apply_config({"DESIGN_DOCSTRING_PUBLIC": 0}, out=io.StringIO())
        self.assertEqual(kinds(), [])

    def test_standards_block_comes_last_in_the_report(self):  # verifies: REQ-DESIGN-953#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "m.py"), "COUNT = 0\ndef bump():\n    global COUNT\n    COUNT += 1\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_design(d)
            out = buf.getvalue()
        self.assertLess(out.index("Encapsulation (1)"), out.index("Standards (1)"))
        self.assertIn("missing-docstring", out)

    def test_design_summary_scores_clean_files(self):  # verifies: REQ-DESIGN-954#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(R._design_summary(d))
            _write(os.path.join(d, "clean.py"), 'def a():\n    """A."""\n    return 1\n')
            _write(os.path.join(d, "dirty.py"), "COUNT = 0\ndef bump():\n    global COUNT\n    COUNT += 1\n")
            _write(os.path.join(d, "tests", "test_x.py"), "def bump():\n    global COUNT\n")
            s = R._design_summary(d)
        self.assertEqual((s["files"], s["clean_files"], s["score"]), (2, 1, 50))
        self.assertEqual(s["candidates"]["encapsulation"], 1)
        self.assertEqual(s["candidates"]["standards"], 1)

    @staticmethod
    def _metric_kinds(src, name="m.py"):
        """The `metrics` candidates only — the class's own `_kinds` covers the rest."""
        found = R._design_file(name, src)
        return sorted(f["kind"] for f in found if f["pillar"] == "metrics")

    def test_wide_class_is_a_god_class(self):  # verifies: REQ-DESIGN-978#CASE-1
        body = "".join("    def m%d(self):\n        return self.x\n" % i
                       for i in range(R.DESIGN_WMC_MAX + 1))
        src = "class Wide:\n    def __init__(self):\n        self.x = 1\n" + body
        self.assertIn("god-class", self._metric_kinds(src))

    def test_dict_subclass_is_not_accused_of_incohesion(self):  # verifies: REQ-DESIGN-978#CASE-2
        # Its state is keys, not attributes: no field exists for two methods to share,
        # so cohesion is not a question this class can be asked.
        body = "".join("    def m%d(self):\n        return self['k%d']\n" % (i, i)
                       for i in range(8))
        src = "class Bag(dict):\n" + body
        self.assertNotIn("low-cohesion", self._metric_kinds(src))

    def test_split_state_is_reported_as_low_cohesion(self):  # verifies: REQ-DESIGN-978#CASE-3
        # Two groups of methods over two disjoint fields, and deliberately no __init__:
        # a constructor touching every field pairs with all of them, which alone drags
        # LCOM1 to zero on a class this size. That is a property of the metric, not of
        # this fixture — the requirement's Context records it.
        halves = "    def a0(self):\n        self.left = 1\n"
        halves += "".join("    def a%d(self):\n        return self.left\n" % i for i in range(1, 6))
        halves += "    def b0(self):\n        self.right = 2\n"
        halves += "".join("    def b%d(self):\n        return self.right\n" % i for i in range(1, 6))
        src = "class Split:\n" + halves
        keep = R.DESIGN_LCOM_MAX
        try:
            R.apply_config({"DESIGN_LCOM_MAX": 2})     # 12 methods over 2 fields score 6
            self.assertIn("low-cohesion", self._metric_kinds(src))
        finally:
            R.apply_config({"DESIGN_LCOM_MAX": keep})

    def test_metric_thresholds_come_from_config(self):  # verifies: REQ-DESIGN-978#CASE-4
        src = ("class Two:\n"
               "    def __init__(self):\n        self.x = 1\n"
               "    def a(self):\n        return self.x\n")
        self.assertNotIn("god-class", self._metric_kinds(src))
        keep = R.DESIGN_WMC_MAX
        try:
            R.apply_config({"DESIGN_WMC_MAX": 1})
            self.assertIn("god-class", self._metric_kinds(src))
        finally:
            R.apply_config({"DESIGN_WMC_MAX": keep})

    def test_a_cohesive_class_reports_no_metric(self):  # verifies: REQ-DESIGN-978#CASE-5
        src = ("class Small:\n"
               "    def __init__(self):\n        self.x = 1\n"
               "    def get(self):\n        return self.x\n"
               "    def bump(self):\n        self.x += 1\n")
        self.assertEqual(self._metric_kinds(src), [])

    def test_slots_declare_fields_too(self):  # verifies: REQ-DESIGN-978#CASE-3
        # __slots__ names the state even when nothing assigns it in this class body.
        halves = "".join("    def a%d(self):\n        return self.left\n" % i for i in range(6))
        halves += "".join("    def b%d(self):\n        return self.right\n" % i for i in range(6))
        src = 'class Slotted:\n    __slots__ = ("left", "right")\n' + halves
        keep = R.DESIGN_LCOM_MAX
        try:
            R.apply_config({"DESIGN_LCOM_MAX": 2})     # 12 methods over 2 fields score 6
            self.assertIn("low-cohesion", self._metric_kinds(src))
        finally:
            R.apply_config({"DESIGN_LCOM_MAX": keep})

    def test_metrics_are_python_only(self):  # verifies: REQ-DESIGN-978#CASE-1
        body = "".join("  m%d() { return this.x; }\n" % i for i in range(R.DESIGN_WMC_MAX + 5))
        found = R._design_file("m.js", "class Wide {\n" + body + "}\n")
        self.assertEqual([f for f in found if f["pillar"] == "metrics"], [])

    def _dirty_repo(self, d):
        """One clean file and one carrying two candidates, so a record has both a
        score below 100 and more than one kind to group."""
        _write(os.path.join(d, "clean.py"), 'def a():\n    """A."""\n    return 1\n')
        _write(os.path.join(d, "dirty.py"),
               "COUNT = 0\n"
               "def bump():\n"
               "    global COUNT\n"
               "    COUNT += 1\n")

    def test_design_summary_omits_findings_by_default(self):  # verifies: REQ-DESIGN-976#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._dirty_repo(d)
            s = R._design_summary(d)
        self.assertEqual(sorted(s), ["candidates", "clean_files", "files", "score"])

    def test_design_summary_with_findings_lists_every_candidate(self):  # verifies: REQ-DESIGN-976#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._dirty_repo(d)
            s = R._design_summary(d, with_findings=True)
        self.assertEqual(len(s["findings"]), sum(s["candidates"].values()))
        one = s["findings"][0]
        self.assertEqual(sorted(one), ["detail", "file", "kind", "line", "name", "pillar"])
        # advice is a property of the rule, so it is emitted once per kind, not per row
        self.assertEqual(sorted(s["advice"]), sorted({f["kind"] for f in s["findings"]}))
        self.assertNotIn("advice", one)

    def test_map_carries_the_candidates_and_health_does_not(self):  # verifies: REQ-DESIGN-976#CASE-2  # verifies: REQ-DESIGN-976#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _write(os.path.join(rq, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="feature", extra="", title="T"))
            self._dirty_repo(d)
            data = R._assemble_map_data(R.load_requirements(rq), {}, rq, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace(R.load_requirements(rq), {}, rq, d), as_json=True)
        design = data["design"]
        self.assertEqual(len(design["findings"]), sum(design["candidates"].values()))
        self.assertGreater(len(design["findings"]), 0)
        self.assertNotIn("findings", json.loads(buf.getvalue()).get("design", {}))
        self.assertNotIn("findings", buf.getvalue())

    def test_design_block_is_byte_stable_across_runs(self):  # verifies: REQ-DESIGN-976#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _write(os.path.join(rq, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="feature", extra="", title="T"))
            self._dirty_repo(d)
            reqs = R.load_requirements(rq)
            first = R._assemble_map_data(reqs, {}, rq, d)["design"]
            second = R._assemble_map_data(reqs, {}, rq, d)["design"]
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_map_and_health_carry_the_design_score(self):  # verifies: REQ-DESIGN-954#CASE-2  # verifies: ARCH-DESIGN-061#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _write(os.path.join(rq, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="feature", extra="", title="T"))
            _write(os.path.join(d, "m.py"), 'def a():\n    """A."""\n    return 1\n')
            reqs = R.load_requirements(rq)
            data = R._assemble_map_data(reqs, {}, rq, d)
            self.assertEqual(data["design"]["score"], 100)
            self.assertIn("design OOP: 100/100 (1/1 source files", R._build_md_text(dict(data, todos=[])))
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace(reqs, {}, rq, d), True)
            self.assertEqual(json.loads(buf.getvalue())["design_score"], 100)

    def test_no_program_logic_means_no_design_key(self):  # verifies: REQ-DESIGN-954#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            _write(os.path.join(rq, "AREA-A-001.md"),
                   REQ.format(id="AREA-A-001", status="baseline", layer="feature", extra="", title="T"))
            _write(os.path.join(d, "site.css"), "body { margin: 0 }\n")
            data = R._assemble_map_data(R.load_requirements(rq), {}, rq, d)
            self.assertNotIn("design", data)
            buf = io.StringIO()
            with redirect_stdout(buf):
                R.cmd_health(R.Workspace(R.load_requirements(rq), {}, rq, d), True)
            self.assertNotIn("design_score", json.loads(buf.getvalue()))

    def test_javascript_functions_classes_and_switch(self):  # verifies: REQ-DESIGN-955#CASE-1  # verifies: ARCH-DESIGN-061#CASE-5
        src = (
            "// comment with { brace and 'quote\n"
            "function wide(a, b, c, d, e, f, g) { return a; }\n"
            "const arrow = (x, y) => { return x + y; };\n"
            "class Store { load() { return 1; } save() { return 2; } close() { } }\n"
            "class Cache { load() { return 3; } save() { return 2; } close() { } }\n"
            "function pick(kind, v) {\n"
            "  switch (kind) { case 'a': return 1; case 'b': return 2; case 'c': return 3; case 'd': return 4; }\n"
            "  if (v instanceof Foo) { } else if (v instanceof Bar) { } else if (v instanceof Baz) { }\n"
            "}\n")
        f = R._design_file("m.js", src)
        kinds = {x["kind"] for x in f}
        self.assertIn("long-parameter-list", kinds)
        self.assertIn("shared-methods", kinds)
        self.assertIn("duplicate-method", kinds)
        self.assertIn("type-switch", kinds)
        self.assertIn("isinstance-chain", kinds)
        self.assertEqual([x["name"] for x in f if x["kind"] == "type-switch"], ["kind"])
        self.assertEqual([x["name"] for x in f if x["kind"] == "isinstance-chain"], ["v"])
        self.assertIn("Cache.save", [x["name"] for x in f if x["kind"] == "duplicate-method"])

    def test_cpp_long_function_and_dynamic_cast_chain(self):  # verifies: REQ-DESIGN-955#CASE-2
        body = "".join("    x += {};\n".format(i) for i in range(90))
        src = ("#include <x>\n"
               "int compute(const std::string& name, int n) {\n" + body + "    return x;\n}\n"
               "void handle(Shape* s) {\n"
               "    if (dynamic_cast<Circle*>(s)) { } else if (dynamic_cast<Square*>(s)) { }"
               " else if (dynamic_cast<Tri*>(s)) { }\n}\n")
        f = R._design_file("shapes.cpp", src)
        kinds = [x["kind"] for x in f]
        self.assertIn("long-function", kinds)
        self.assertEqual([x["name"] for x in f if x["kind"] == "long-function"], ["compute"])
        self.assertIn("isinstance-chain", kinds)
        self.assertNotIn("missing-docstring", kinds)   # Python-only rule

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
        f = R._design_file("m.rb", src)
        self.assertEqual([x["kind"] for x in f], ["line-too-long"])
        self.assertEqual(R._design_file("m.rb", "def a\n  1\nend\n"), [])


    def test_thresholds_are_configurable(self):  # verifies: REQ-DESIGN-952#CASE-4  # verifies: ARCH-DESIGN-061#CASE-2
        saved = R.DESIGN_PARAMS_MAX
        self.addCleanup(setattr, R, "DESIGN_PARAMS_MAX", saved)
        src = "def f(a, b, c): pass\n"
        self.assertEqual(self._kinds(src), [])
        R.apply_config({"DESIGN_PARAMS_MAX": 2}, out=io.StringIO())
        self.assertIn("long-parameter-list", self._kinds(src))

    def test_design_is_in_the_registry_and_not_in_the_gate(self):  # verifies: ARCH-DESIGN-061#CASE-3
        # `design` is a mode of `gate`, not a gate RULE: it never decides an exit
        # code. That is the property this case has always been about.
        self.assertFalse(any("design" in (r.fn.__name__ or "") for r in R.GATE_RULES))


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

    def test_three_way_priority_order(self):  # verifies: ARCH-NEXT-013#CASE-7
        reqs = {
            "AAA-NOPRI-001": {"meta": {"status": "confirmed"}, "body": "# T\n"},
            "BBB-SHOULD-002": {"meta": {"status": "confirmed", "priority": "should-have"}, "body": "# T\n"},
            "CCC-MUST-003": {"meta": {"status": "confirmed", "priority": "must-have"}, "body": "# T\n"},
        }
        members = {rid: [("implements", "x.py", 1)] for rid in reqs}  # all untested -> one bucket
        _, out = self._run(reqs, members)
        self.assertLess(out.index("CCC-MUST-003"), out.index("BBB-SHOULD-002"))
        self.assertLess(out.index("BBB-SHOULD-002"), out.index("AAA-NOPRI-001"))

    def test_empty_and_clean_write_no_files(self):  # verifies: ARCH-NEXT-013#CASE-8
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

    def test_untagged_files_after_drafts(self):  # verifies: REQ-NEXT-884#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "orphan.py"), "x = 1\n")
            reqs = {"DDD-DRAFT-004": {"meta": {"status": "draft"}, "body": "# T\n"}}
            _, out = self._run(reqs, {}, code_root=d)
            self.assertIn("Untagged files", out)
            self.assertLess(out.index("Drafts to review"), out.index("Untagged files"))

    def test_no_code_root_no_untagged_section(self):  # verifies: REQ-NEXT-884#CASE-6
        reqs = {"DDD-DRAFT-004": {"meta": {"status": "draft"}, "body": "# T\n"}}
        _, out = self._run(reqs, {})
        self.assertNotIn("Untagged files", out)

    def test_untagged_files_bucket_suggests_draft(self):  # verifies: ARCH-NEXT-013#CASE-9
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


class CasesDrift(unittest.TestCase):  # tested-by: ARCH-DRIFT-003  # tested-by: REQ-DRIFT-841  # tested-by: REQ-DRIFT-842
    def test_binding_hash_returns_fixed_length_hex(self):  # verifies: REQ-DRIFT-841#CASE-1
        body = "# T\n\n## Description\n- shall do X.\n\n## Cases\nCASE-1\n  Then X holds\n"
        h = R.binding_hash(body)
        self.assertEqual(len(h), 12)
        int(h, 16)  # must parse as hex
        self.assertEqual(h, h.lower())

    def test_legacy_output_heading_is_normative(self):  # verifies: REQ-DRIFT-841#CASE-2
        a = "# T\n\n## Output\n- shall do X.\n"
        b = "# T\n\n## Output\n- shall do Y.\n"
        self.assertNotEqual(R.binding_hash(a), R.binding_hash(b))

    def test_binding_hash_deterministic_across_calls(self):  # verifies: REQ-DRIFT-841#CASE-4
        body = "# T\n\n## Description\n- shall do X.\n"
        self.assertEqual(R.binding_hash(body), R.binding_hash(body))

    def test_save_lock_writes_sorted_indented_json(self):  # verifies: REQ-DRIFT-842#CASE-4
        with tempfile.TemporaryDirectory() as d:
            R.save_lock(d, {"Z-9": "aaaaaaaaaaaa", "A-1": "bbbbbbbbbbbb"})
            with open(os.path.join(d, "_reqlock.json"), encoding="utf-8") as f:
                text = f.read()
            self.assertGreater(text.count("\n"), 1)  # multi-line, indented
            data = json.loads(text)
            self.assertEqual(list(data.keys()), sorted(data.keys()))
            self.assertLess(text.index('"A-1"'), text.index('"Z-9"'))


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
    def test_new_scaffolds_context_section(self):  # verifies: REQ-CONTEXT-835#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rd = os.path.join(d, "requirements")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_new(rd, None, "AREA-X-001")
            self.assertEqual(code, 0)
            content = open(os.path.join(rd, "AREA-X-001.md"), encoding="utf-8").read()
            self.assertIn("## Context (non-binding)", content)

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
        src = open(os.path.join(here, "reqmap.py"), encoding="utf-8").read()
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
            sys.argv = ["reqmap", "gate", "--search", "--root", d]
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


class CasesViewer007(unittest.TestCase):  # tested-by: ARCH-VIEWER-007  # tested-by: REQ-VIEWER-940  # tested-by: REQ-VIEWER-941
    def _node(self, **fields):
        node = {"id": "A-1", "title": "T", "contract": [], "status": "confirmed",
                "layer": "bus", "members": [], "risk": 0, "acc": [], "deps": []}
        node.update(fields)
        return {"nodes": [node], "edges": []}

    def _blob(self, out):
        return out[len("<script>window.__REQMAP_DATA__="):-len(";</script>")]

    def test_render_html_returns_none_without_template(self):  # verifies: REQ-VIEWER-940#CASE-3
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(R, "_viewer_template_path",
                                   return_value=os.path.join(d, "nope.html")):
                out = R.render_html({"nodes": [], "edges": []}, d)
            self.assertIsNone(out)

    def test_map_writes_md_and_json_when_viewer_template_absent(self):  # verifies: REQ-VIEWER-940#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n" + _ac_body())
            _write(os.path.join(d, "a.py"), tag("A-FOO-001") + "\n")
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            with mock.patch.object(R, "_viewer_template_path",
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


class CasesSuggestVerifies047(unittest.TestCase):  # tested-by: ARCH-SUGGESTVERIFIES-047  # tested-by: REQ-SUGGESTVERIFIES-927  # tested-by: REQ-SUGGESTVERIFIES-929
    def _repo(self, d, reqs, tests):
        for rid, acceptance in reqs.items():
            _write(os.path.join(d, rid + ".md"),
                   "---\nid: {}\nstatus: confirmed\nlayer: feature\n---\n\n".format(rid)
                   + _ac_body(acceptance=acceptance))
        for name, body in tests.items():
            _write(os.path.join(d, name), body)

    def _suggest(self, d, apply_tags=False):
        reqs = R.load_requirements(d)
        members = R.scan_members(d, d)
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_suggest_verifies(R.Workspace(reqs, members, d, d), apply_tags)
        return buf.getvalue()

    def test_matching_restricted_to_owning_tested_by_files(self):  # verifies: REQ-SUGGESTVERIFIES-927#CASE-2
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": "AC-1\n  Given a\n  Then b"},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_something_else():\n    pass\n",
                        # a DIFFERENT file, never tagged tested-by for this requirement
                        "unrelated_test.py": "def test_ac1_x():\n    pass\n"})
            out = self._suggest(d)
            self.assertIn("no suggestions", out)

    def test_manual_criterion_is_skipped(self):  # verifies: REQ-SUGGESTVERIFIES-927#CASE-5
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": "AC-1  <!-- verifiable by: inspection -->\n"
                                              "  Given a\n  Then b"},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac1_x():\n    pass\n"})
            out = self._suggest(d)
            self.assertIn("no suggestions", out)

    def test_dry_run_prints_without_writing(self):  # verifies: REQ-SUGGESTVERIFIES-929#CASE-1
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, {"AREA-UPLOAD-037": "AC-1\n  Given a\n  Then b"},
                       {"test_upload.py": tb_tag("AREA-UPLOAD-037") + "\n"
                        "def test_ac1_x():\n    pass\n"})
            p = os.path.join(d, "test_upload.py")
            before = open(p, encoding="utf-8").read()
            out = self._suggest(d, apply_tags=False)
            self.assertIn("AREA-UPLOAD-037 AC-1", out)
            self.assertEqual(open(p, encoding="utf-8").read(), before)


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


class CasesTestlink018(unittest.TestCase):  # tested-by: ARCH-TESTLINK-018  # tested-by: REQ-TESTLINK-931  # tested-by: REQ-TESTLINK-933
    def test_test_shaped_string_in_docstring_still_passes(self):  # verifies: REQ-TESTLINK-931#CASE-1
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "notest.py")
            _write(p, '"""This module explains: def test_foo():  pass -- for illustration '
                      'only."""\n')
            self.assertEqual(R._test_link_problem(p), "")

    def test_valid_tested_by_produces_no_warning(self):  # verifies: REQ-TESTLINK-933#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"),
                   "---\nid: A-FOO-001\nstatus: confirmed\nlayer: bus\n---\n\n" + _ac_body())
            _write(os.path.join(d, "a.py"), tag("A-FOO-001") + "\n" + tb_tag("A-FOO-001")
                   + "\ndef test_it():\n    pass\n")
            reqs, members = R.load_requirements(d), R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertNotIn("tested-by", buf.getvalue())


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


class CasesLevel051(unittest.TestCase):  # tested-by: ARCH-LEVEL-051  # tested-by: REQ-LEVEL-862
    def test_aggregate_layer_stays_exempt_regardless_of_level(self):  # verifies: REQ-LEVEL-862#CASE-5
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"), REQ.format(
                id="A-FOO-001", status="confirmed", layer="aggregate",
                extra="level: architecture\ndepends_on: []\n", title="T"))
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                _code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertNotIn("no implements", buf.getvalue())


class CasesPyfloor040(unittest.TestCase):  # tested-by: ARCH-PYFLOOR-040  # tested-by: REQ-PYFLOOR-902
    def test_min_python_is_a_concrete_version_tuple(self):  # verifies: REQ-PYFLOOR-902#CASE-1
        self.assertIsInstance(R.MIN_PYTHON, tuple)
        self.assertGreaterEqual(len(R.MIN_PYTHON), 2)
        self.assertTrue(all(isinstance(p, int) for p in R.MIN_PYTHON))
        self.assertNotEqual(R.MIN_PYTHON, (0, 0))


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
            sys.argv = ["reqmap", "gate", "--dupes", "--root", d]
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


class CasesCheck(unittest.TestCase):  # tested-by: ARCH-CHECK-006  # tested-by: REQ-CHECK-829  # tested-by: REQ-CHECK-832
    def test_confirmed_no_tested_by_warns_not_errors(self):  # verifies: REQ-CHECK-829#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "A-FOO-001.md"), REQ.format(
                id="A-FOO-001", status="confirmed", layer="bus", extra="", title="T"))
            _write(os.path.join(d, "mod.py"), tag("A-FOO-001") + "\n")
            reqs = R.load_requirements(d)
            members = R.scan_members(d, d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, members, d, d), False)
            self.assertIn("confirmed but no tested-by", buf.getvalue())
            self.assertEqual(code, 0)

    def test_open_verify_intent_finding_keeps_exit_zero(self):  # verifies: REQ-CHECK-832#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "requirements", "AREA-X-001.md"),
                   _req_with_verify("AREA-X-001", ["magic 1.05, bug?"]))
            reqs = R.load_requirements(os.path.join(d, "requirements"))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = R.cmd_check(R.Workspace(reqs, {}, os.path.join(d, "requirements")), False)
            self.assertIn("1 open verify-intent finding(s)", buf.getvalue())
            self.assertEqual(code, 0)


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


class CasesOrphanCode(unittest.TestCase):  # tested-by: ARCH-ORPHANCODE-034  # tested-by: REQ-ORPHANCODE-888
    def test_only_program_extensions_considered(self):  # verifies: REQ-ORPHANCODE-888#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "big.go"), _BIG_PY)
            _write(os.path.join(d, "big.txt"), _BIG_PY)
            result = R.orphan_code_files(d, set())
            self.assertIn("big.go", result)
            self.assertNotIn("big.txt", result)


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
        self.assertIn("Specification Hierarchy", md)

    def test_risk_diagram_shows_only_flagged_with_recommendation(self):  # verifies: ARCH-MAPDIAGRAMS-055#CASE-5
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


class CasesParse001(unittest.TestCase):  # tested-by: REQ-PARSE-890
    def test_file_with_no_id_field_keyed_by_filename_stem(self):  # verifies: REQ-PARSE-890#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "REQ-A-001.md"), "---\nstatus: draft\n---\n\n# T\n")
            reqs = R.load_requirements(d)
        self.assertIn("REQ-A-001", reqs)
        self.assertEqual(reqs["REQ-A-001"]["meta"].get("status"), "draft")


class CasesVlevel037(unittest.TestCase):  # tested-by: REQ-VLEVEL-946
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

    def test_unvalidated_need_never_bumps_exit_code(self):  # verifies: REQ-VLEVEL-946#CASE-6
        files = {
            "NEED-A-001.md": REQ.format(id="NEED-A-001", status="confirmed", layer="need",
                                        extra="", title="Validated need"),
            "NEED-B-002.md": REQ.format(id="NEED-B-002", status="confirmed", layer="need",
                                        extra="", title="Unvalidated need"),
            "t_probe.py": "# validated-against: NEED-A-001\ndef test_x():\n    pass\n",
        }
        code, out = self._check(files)
        self.assertEqual(code, 0)
        self.assertIn("validated-against", out)

    def test_system_only_bus_never_bumps_exit_code(self):  # verifies: REQ-VLEVEL-946#CASE-6
        files = {
            "CORE-X-001.md": REQ.format(id="CORE-X-001", status="confirmed", layer="bus",
                                        extra="", title="Foundation"),
            "impl.py": "# implements: CORE-X-001\ndef go():\n    return 1\n",
            "t_sys.py": "# tested-by: CORE-X-001 @system\ndef test_e2e():\n    pass\n",
        }
        code, out = self._check(files)
        self.assertEqual(code, 0)
        self.assertIn("@system", out)


# ---------------------------------------------------------------------------
# clarify / implement / retire — the author -> code -> retirement half of the CLI
# ---------------------------------------------------------------------------
_SPEC_TMPL = ("---\nid: {id}\nstatus: {status}\nlevel: code\nlayer: feature\n"
              "{extra}---\n\n# {title}\n\n"
              "## Description\nEvery bullet below is binding.\n{clauses}\n\n"
              "## Cases\n{cases}\n")


def _spec(rid, clauses, cases=("CASE-1 — c\n  Given x\n  When y\n  Then z",),
          status="confirmed", extra="", title="T"):
    """A minimal well-formed requirement: Description clauses + labelled cases."""
    return _SPEC_TMPL.format(
        id=rid, status=status, extra=extra, title=title,
        clauses="\n".join("- " + c for c in clauses),
        cases="\n\n".join(cases))


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


class Retire(unittest.TestCase):  # tested-by: ARCH-RETIRE-064  # tested-by: REQ-RETIRE-960  # tested-by: REQ-RETIRE-961  # tested-by: REQ-RETIRE-962
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
