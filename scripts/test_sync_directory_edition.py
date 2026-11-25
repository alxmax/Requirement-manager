"""Tests for scripts/sync_directory_edition.py: the directory edition's copies.

Stdlib unittest, run from the repo root:
    python -X utf8 scripts/test_sync_directory_edition.py
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_directory_edition as S


def _tree(d):
    src, dst = Path(d) / "full", Path(d) / "dir"
    for root in (src, dst):
        (root / S.REFS).mkdir(parents=True)
        for name in S.COPIED:
            (root / S.REFS / name).write_text(f"# {name}\n", encoding="utf-8")
    return src, dst


class SyncDirectoryEdition(unittest.TestCase):  # tested-by: ARCH-SELFGATE-039 @integration
    def test_equal_trees_report_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = _tree(d)
            self.assertEqual([], S.diff(src, dst))

    def test_a_changed_or_missing_copy_is_named(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = _tree(d)
            (src / S.REFS / "bugs.md").write_text("new\n", encoding="utf-8")
            (dst / S.REFS / "ci.md").unlink()
            self.assertEqual(["differs    bugs.md", "missing    ci.md"], sorted(
                S.diff(src, dst), key=lambda x: x.split()[1]))

    def test_build_repairs_and_leaves_other_files_alone(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = _tree(d)
            (src / S.REFS / "bugs.md").write_text("new\n", encoding="utf-8")
            (dst / S.REFS / "workflow.md").write_text("mine\n", encoding="utf-8")
            (dst / S.REFS / "manual-mode.md").write_text("only here\n", encoding="utf-8")
            self.assertEqual(1, S.build(src, dst))
            self.assertEqual([], S.diff(src, dst))
            self.assertEqual("mine\n", (dst / S.REFS / "workflow.md").read_text("utf-8"))
            self.assertEqual("only here\n",
                             (dst / S.REFS / "manual-mode.md").read_text("utf-8"))

    def test_crlf_is_not_drift(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = _tree(d)
            (dst / S.REFS / "ci.md").write_bytes(b"# ci.md\r\n")
            self.assertEqual([], S.diff(src, dst))

    def test_the_committed_edition_is_current(self):
        self.assertEqual([], S.diff())


if __name__ == "__main__":
    unittest.main()
