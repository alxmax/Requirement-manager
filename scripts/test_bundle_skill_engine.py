"""Tests for scripts/bundle_skill_engine.py: the skill's engine copy.

Stdlib unittest, run from the repo root:
    python -X utf8 scripts/test_bundle_skill_engine.py
Builds a throwaway source tree in a tempdir; the real engine is never touched
except by the last test, which pins that the committed copy is current.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bundle_skill_engine as B


def _source(d):
    src = Path(d) / "scripts"
    (src / "reqmap_engine" / "__pycache__").mkdir(parents=True)
    (src / "reqmap.py").write_text("print('cli')\n", encoding="utf-8")
    (src / "_map_viewer.html").write_text("<html></html>\n", encoding="utf-8")
    (src / "reqmap_engine" / "__init__.py").write_text("V = 1\n", encoding="utf-8")
    (src / "reqmap_engine" / "gate.py").write_text("x = 1\n", encoding="utf-8")
    (src / "reqmap_engine" / "__pycache__" / "gate.pyc").write_bytes(b"\0")
    (src / "test_reqmap.py").write_text("import reqmap\n", encoding="utf-8")
    return src


class BundleSkillEngine(unittest.TestCase):
    def test_build_then_diff_is_empty(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = _source(d), Path(d) / "skill" / "scripts"
            self.assertEqual(B.build(src, dest), 4)
            self.assertEqual(B.diff(src, dest), [])

    def test_carries_neither_tests_nor_bytecode(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = _source(d), Path(d) / "skill" / "scripts"
            B.build(src, dest)
            self.assertFalse((dest / "test_reqmap.py").exists())
            self.assertFalse((dest / "reqmap_engine" / "__pycache__").exists())

    def test_changed_source_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = _source(d), Path(d) / "skill" / "scripts"
            B.build(src, dest)
            (src / "reqmap_engine" / "gate.py").write_text("x = 2\n", encoding="utf-8")
            self.assertEqual(B.diff(src, dest), ["differs  reqmap_engine/gate.py"])

    def test_missing_and_stale_files_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = _source(d), Path(d) / "skill" / "scripts"
            B.build(src, dest)
            (dest / "reqmap_engine" / "gate.py").unlink()
            (dest / "reqmap_engine" / "old.py").write_text("", encoding="utf-8")
            self.assertEqual(B.diff(src, dest), ["missing  reqmap_engine/gate.py",
                                                 "stale    reqmap_engine/old.py"])

    def test_line_endings_alone_are_not_drift(self):
        with tempfile.TemporaryDirectory() as d:
            src, dest = _source(d), Path(d) / "skill" / "scripts"
            B.build(src, dest)
            (dest / "reqmap.py").write_bytes(b"print('cli')\r\n")
            self.assertEqual(B.diff(src, dest), [])

    def test_committed_copy_is_current(self):
        """The check CI runs, as a test: editing plugin/scripts/ without
        re-running the bundler fails here with the files named."""
        self.assertEqual(B.diff(), [])


if __name__ == "__main__":
    unittest.main()
