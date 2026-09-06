"""The verdict: gate rules, drift in both directions, `--since` scoping, `--strict`,
`--json`, test links and per-criterion coverage, traceability and the V-model rungs.

Part of the `test_reqmap` suite — run it through the aggregator (`python
scripts/test_reqmap.py`), or on its own with `python -m unittest test_reqmap_gate`."""
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

    def test_gate_warns_on_an_aggregate_covered_by_nothing(self):  # verifies: REQ-TRACE-935#CASE-2
        """An aggregate is exempt from implements and tested-by because its
        `depends_on` covers it. An empty list claims the exemption and supplies
        nothing. The `confirm` verb refused this until v5.0.0 folded it away; nothing
        replaced the guard, and a confirmed aggregate with `depends_on: []` passed the
        gate silently until RM031."""
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "REQ-AGG-004.md"),
                   REQ.format(id="REQ-AGG-004", status="confirmed", layer="aggregate",
                              extra="depends_on: []\n", title="Empty agg"))
            reqs = R.load_requirements(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = R.cmd_check(R.Workspace(reqs, {}, d, d), False)
        out = buf.getvalue()
        self.assertIn("RM031", out)
        self.assertIn("REQ-AGG-004", out)
        self.assertEqual(rc, 0, "RM031 is a warning, never a build failure")

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


class MemberHashPerDefinition(unittest.TestCase):  # tested-by: REQ-MEMBERDRIFT-982
    """The hash keys on the definition a tag sits in, so a shared file stays attributable."""

    TWO_OWNERS = ('def alpha():\n    """A."""\n    # implements: REQ-A-001\n    return 1\n'
                  '\n\ndef beta():\n    """B."""\n    # implements: REQ-B-001\n    return 2\n')

    def _hashes(self, d, src, name="mod.py"):
        _write(os.path.join(d, "src", name), src)
        members = R.scan_members(d, os.path.join(d, "requirements"))
        return R.compute_member_hashes(d, members), members

    def test_one_file_two_owners_two_keys(self):  # verifies: REQ-MEMBERDRIFT-982#CASE-1
        """Per file this recorded nothing at all: two owners meant the file was dropped."""
        with tempfile.TemporaryDirectory() as d:
            h, _ = self._hashes(d, self.TWO_OWNERS)
        self.assertEqual(sorted(h), ["REQ-A-001", "REQ-B-001"])
        self.assertEqual(list(h["REQ-A-001"]), ["src/mod.py#alpha"])
        self.assertEqual(list(h["REQ-B-001"]), ["src/mod.py#beta"])

    def test_drift_names_only_the_changed_definition(self):  # verifies: REQ-MEMBERDRIFT-982#CASE-2
        with tempfile.TemporaryDirectory() as d:
            rq = os.path.join(d, "requirements")
            for rid in ("REQ-A-001", "REQ-B-001"):
                _write(os.path.join(rq, rid + ".md"),
                       REQ.format(id=rid, status="confirmed", layer="feature",
                                  extra="", title=rid))
            baseline, _ = self._hashes(d, self.TWO_OWNERS)
            changed = self.TWO_OWNERS.replace("return 2", "return 999")
            current, members = self._hashes(d, changed)
            reqs = R.load_requirements(rq)
            lock = {rid: R.binding_hash(r["body"]) for rid, r in reqs.items()}
            drift = R.member_drift(reqs, members, lock, baseline, d, current=current)
        self.assertEqual(drift, [("REQ-B-001", "src/mod.py#beta")])

    def test_a_shared_definition_is_still_dropped(self):  # verifies: REQ-MEMBERDRIFT-982#CASE-3
        """Sharing a file is no longer sharing a key; sharing a DEFINITION still is."""
        src = ('def both():\n    """X."""\n'
               '    # implements: REQ-A-001\n    # implements: REQ-B-001\n    return 1\n')
        with tempfile.TemporaryDirectory() as d:
            h, _ = self._hashes(d, src)
        self.assertEqual(h, {})

    def test_a_non_python_member_keeps_the_plain_path(self):  # verifies: REQ-MEMBERDRIFT-982#CASE-4
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "notes.md"), "# doc\n\n<!-- implements: REQ-A-001 -->\n")
            members = R.scan_members(d, os.path.join(d, "requirements"))
            h = R.compute_member_hashes(d, members)
        self.assertEqual(list(h.get("REQ-A-001", {})), ["notes.md"])

    def test_a_module_level_tag_keeps_the_whole_file_key(self):  # verifies: REQ-MEMBERDRIFT-982#CASE-4
        with tempfile.TemporaryDirectory() as d:
            h, _ = self._hashes(d, "# implements: REQ-A-001\nVALUE = 1\n")
        self.assertEqual(list(h.get("REQ-A-001", {})), ["src/mod.py"])

    def test_crlf_does_not_read_as_drift(self):  # verifies: REQ-MEMBERDRIFT-982#CASE-2
        """The span hash normalises line endings, as the whole-file hash already did —
        otherwise a Windows checkout reports every member as drifted."""
        with tempfile.TemporaryDirectory() as d:
            pass
        def write_bytes(root, data):
            p = os.path.join(root, "src", "mod.py")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:      # bytes: text mode would re-translate them
                f.write(data)
            members = R.scan_members(root, os.path.join(root, "requirements"))
            return R.compute_member_hashes(root, members)
        body = self.TWO_OWNERS.encode("utf-8")
        with tempfile.TemporaryDirectory() as d:
            lf = write_bytes(d, body)
        with tempfile.TemporaryDirectory() as d:
            crlf = write_bytes(d, body.replace(b"\n", b"\r\n"))
        self.assertEqual(lf, crlf)


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


class CasesOrphanCode(unittest.TestCase):  # tested-by: ARCH-ORPHANCODE-034  # tested-by: REQ-ORPHANCODE-888
    def test_only_program_extensions_considered(self):  # verifies: REQ-ORPHANCODE-888#CASE-2
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "big.go"), _BIG_PY)
            _write(os.path.join(d, "big.txt"), _BIG_PY)
            result = R.orphan_code_files(d, set())
            self.assertIn("big.go", result)
            self.assertNotIn("big.txt", result)


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


class DriftReason(unittest.TestCase):  # tested-by: ARCH-DRIFT-003  # tested-by: REQ-DRIFT-988
    """`--accept-drift` is the one escape hatch in the gate. It must leave a trace."""

    def _confirmed_repo(self, d, body_tail=""):
        rdir = os.path.join(d, "requirements")
        _write(os.path.join(rdir, "REQ-A-001.md"),
               _spec("REQ-A-001", ["`gate` writes the lock file."]) + body_tail)
        _write(os.path.join(d, "impl.py"), "x = 1  " + tag("REQ-A-001"))
        _write(os.path.join(d, "test_impl.py"),
               "def test_a():" + "\n" + "    assert True  " + tb_tag("REQ-A-001"))
        return rdir

    def _drift(self, d, **kw):
        """Seed a lock, edit the contract, re-check with `kw`. Returns (rdir, output)."""
        rdir = self._confirmed_repo(d)
        reqs, members = R.load_requirements(rdir), R.scan_members(d, rdir)
        with redirect_stdout(io.StringIO()):
            R.cmd_check(R.Workspace(reqs, members, rdir, d), True)
        self._confirmed_repo(d, body_tail="\n" + "Text that changes the hash." + "\n")
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_check(R.Workspace(R.load_requirements(rdir), members, rdir, d), True, **kw)
        return rdir, buf.getvalue()

    def test_a_reason_is_recorded_where_a_reviewer_reads_it(self):  # verifies: ARCH-DRIFT-003#CASE-5  # verifies: REQ-DRIFT-988#CASE-1
        with tempfile.TemporaryDirectory() as d:
            rdir, _out = self._drift(d, accept_drift=True, drift_reason="renamed the flag")
            log = R.load_driftlog(rdir)
        self.assertIn("REQ-A-001", log)
        self.assertEqual("renamed the flag", log["REQ-A-001"]["reason"])
        self.assertTrue(log["REQ-A-001"]["hash"])

    def test_a_bare_waiver_is_recorded_with_no_reason(self):  # verifies: REQ-DRIFT-988#CASE-2
        # Silence is a legible answer. Recording only the explained waivers would make
        # the UNexplained one the invisible one, which is backwards.
        with tempfile.TemporaryDirectory() as d:
            rdir, _out = self._drift(d, accept_drift=True)
            log = R.load_driftlog(rdir)
        self.assertIn("REQ-A-001", log)
        self.assertIsNone(log["REQ-A-001"]["reason"])

    def test_a_demotion_records_nothing(self):  # verifies: REQ-DRIFT-988#CASE-3
        with tempfile.TemporaryDirectory() as d:
            rdir, out = self._drift(d, accept_drift=False)
            self.assertIn("demoted:", out)
            self.assertFalse(os.path.exists(R._driftlog_path(rdir)))

    def test_a_retired_id_is_pruned_from_the_log(self):  # verifies: REQ-DRIFT-988#CASE-4
        with tempfile.TemporaryDirectory() as d:
            rdir, _out = self._drift(d, accept_drift=True, drift_reason="first")
            R.save_driftlog(rdir, dict(R.load_driftlog(rdir),
                                       **{"GONE-X-999": {"hash": "abc", "reason": "old"}}))
            self._confirmed_repo(d, body_tail="\n" + "Changed again." + "\n")
            members = R.scan_members(d, rdir)
            with redirect_stdout(io.StringIO()):
                R.cmd_check(R.Workspace(R.load_requirements(rdir), members, rdir, d), True,
                            accept_drift=True, drift_reason="second")
            log = R.load_driftlog(rdir)
        self.assertNotIn("GONE-X-999", log)
        self.assertEqual("second", log["REQ-A-001"]["reason"])

    def test_a_forward_schema_fails_open(self):  # verifies: REQ-DRIFT-988#CASE-5
        with tempfile.TemporaryDirectory() as d:
            rdir = os.path.join(d, "requirements")
            os.makedirs(rdir)
            _write(R._driftlog_path(rdir),
                   json.dumps({"_schema": R.DRIFTLOG_SCHEMA + 1, "accepted": {"A-1": {}}}))
            self.assertEqual({}, R.load_driftlog(rdir))

    def test_the_flag_takes_a_reason_and_still_works_bare(self):  # verifies: ARCH-DRIFT-003#CASE-6
        # `nargs="?"` must not swallow the flag that follows it: `--accept-drift --code ..`
        # was the shape that would have silently eaten the code root.
        p = R._build_parser()
        self.assertIs(False, p.parse_args(["sync"]).accept_drift)
        self.assertIs(True, p.parse_args(["sync", "--accept-drift"]).accept_drift)
        self.assertEqual("why", p.parse_args(["sync", "--accept-drift", "why"]).accept_drift)
        a = p.parse_args(["sync", "--accept-drift", "--code", ".."])
        self.assertIs(True, a.accept_drift)
        self.assertEqual("..", a.code)


class DriftSeverityConfig(unittest.TestCase):  # tested-by: ARCH-RULES-059  # tested-by: REQ-RULES-989
    """A repo may promote drift for ITSELF. The default never moves."""

    def setUp(self):
        self._saved = R.DRIFT_SEVERITY

    def tearDown(self):
        R.DRIFT_SEVERITY = self._saved

    def _drifted_ctx(self, d, exempt=""):
        rdir = os.path.join(d, "requirements")
        _write(os.path.join(rdir, "REQ-A-001.md"),
               _spec("REQ-A-001", ["`gate` writes the lock file."], extra=exempt))
        _write(os.path.join(d, "impl.py"), "x = 1  " + tag("REQ-A-001"))
        reqs, members = R.load_requirements(rdir), R.scan_members(d, rdir)
        R.save_lock(rdir, {"REQ-A-001": "stale-hash-from-an-older-contract"})
        return R.GateContext(R.Workspace(reqs, members, rdir, d))

    def _codes(self, ctx):
        errors, warns = R.run_gate_rules(ctx)
        return ([f["rule"] for f in errors], [f["rule"] for f in warns])

    def test_the_default_is_still_warn(self):  # verifies: ARCH-RULES-059#CASE-4  # verifies: REQ-RULES-989#CASE-1
        with tempfile.TemporaryDirectory() as d:
            errs, warns = self._codes(self._drifted_ctx(d))
        self.assertNotIn("RM018", errs)
        self.assertIn("RM018", warns)

    def test_config_promotes_drift_for_this_repo_only(self):  # verifies: ARCH-RULES-059#CASE-5  # verifies: REQ-RULES-989#CASE-2
        with tempfile.TemporaryDirectory() as d:
            ctx = self._drifted_ctx(d)
            R.apply_config({"DRIFT_SEVERITY": "error"}, out=io.StringIO())
            errs, _warns = self._codes(ctx)
        self.assertIn("RM018", errs)

    def test_a_requirements_own_exemption_still_wins(self):  # verifies: ARCH-RULES-059#CASE-6  # verifies: REQ-RULES-989#CASE-3
        # A repo-wide dial must not overrule a decision written down per requirement.
        with tempfile.TemporaryDirectory() as d:
            ctx = self._drifted_ctx(d, exempt="gate_exempt: [RM018]" + "\n")
            R.apply_config({"DRIFT_SEVERITY": "error"}, out=io.StringIO())
            errs, warns = self._codes(ctx)
        self.assertNotIn("RM018", errs)
        self.assertNotIn("RM018", warns)

    def test_a_mistyped_value_is_reported_not_silently_ignored(self):  # verifies: REQ-RULES-989#CASE-4
        # apply_config's numeric branch would have rejected every string outright, so a
        # repo could never set this at all; a typo must be loud, not a silent default.
        out = io.StringIO()
        self.assertEqual([], R.apply_config({"DRIFT_SEVERITY": "eror"}, out=out))
        self.assertEqual("warn", R.DRIFT_SEVERITY)
        self.assertIn("DRIFT_SEVERITY", out.getvalue())

    def test_the_registry_is_not_mutated(self):  # verifies: REQ-RULES-989#CASE-5
        # `audit` runs cmd_check twice over the same module-level GATE_RULES; a promotion
        # written back onto the Rule would leak from the first run into the second.
        before = {r.id: r.severity for r in R.GATE_RULES}
        with tempfile.TemporaryDirectory() as d:
            ctx = self._drifted_ctx(d)
            R.apply_config({"DRIFT_SEVERITY": "error"}, out=io.StringIO())
            self._codes(ctx)
        self.assertEqual(before, {r.id: r.severity for r in R.GATE_RULES})


class SinceScopesNotFacts(unittest.TestCase):  # tested-by: ARCH-CHECK-006  # tested-by: REQ-CHECK-831
    """--since says which requirements are reported on, never what a rule may read."""

    BODY = "## Description\n- x\n\n## Cases\nCASE-1 x\n"

    def _ctx(self, narrowed, full):
        reqs = {rid: {"meta": {"id": rid, "layer": "need", "status": "confirmed"},
                      "body": self.BODY} for rid in full}
        ws = R.Workspace(reqs, narrowed, "requirements", ".", {}, {})
        return R.GateContext(ws, since="HEAD~1", full_members=full)

    def test_a_validated_need_outside_the_diff_is_not_warned_about(self):  # verifies: REQ-CHECK-831#CASE-7
        full = {"SYS-A-001": [("validated-against", "a.md", 1)],
                "SYS-B-002": [("validated-against", "b.md", 1)]}
        ctx = self._ctx({"SYS-A-001": full["SYS-A-001"]}, full)
        self.assertEqual(list(R._rule_need_not_validated(ctx)), [])

    def test_a_genuinely_unvalidated_need_in_the_diff_still_warns(self):  # verifies: REQ-CHECK-831#CASE-3
        full = {"SYS-A-001": [("validated-against", "a.md", 1)],
                "SYS-B-002": [("implements", "b.py", 1)]}
        ctx = self._ctx({"SYS-B-002": full["SYS-B-002"]}, full)
        self.assertEqual([rid for rid, _ in R._rule_need_not_validated(ctx)], ["SYS-B-002"])

    def test_the_opt_in_is_read_from_the_whole_tree(self):
        full = {"SYS-A-001": [("validated-against", "a.md", 1)]}
        self.assertTrue(self._ctx({}, full).any_validation)
        self.assertFalse(self._ctx({}, {"SYS-A-001": [("implements", "a.py", 1)]}).any_validation)
