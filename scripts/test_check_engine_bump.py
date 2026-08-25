#!/usr/bin/env python3
"""Tests for check_engine_bump.py — the "engine changed => MAP_ENGINE_VERSION changed"
rule. Seeds a throwaway git repo so both modes (--staged, --base REF) run against
real git diffs, the same way the hook and CI invoke the script.
"""
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_engine_bump as CEB

ENGINE_REL = Path("plugin") / "scripts" / "reqmap.py"


def _git(d, *args):
    subprocess.run(["git", "-C", str(d), *args], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _engine_text(version, body="def gate():\n    return 0\n"):
    return 'MAP_ENGINE_VERSION = "{}"\n\n{}'.format(version, body)


def _seed(d, version="2026-08-20.2"):
    """A repo with one commit holding the engine at `version`."""
    d = Path(d)
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "t@example.com")
    _git(d, "config", "user.name", "t")
    _git(d, "config", "commit.gpgsign", "false")
    (d / ENGINE_REL).parent.mkdir(parents=True)
    (d / ENGINE_REL).write_text(_engine_text(version), encoding="utf-8")
    _git(d, "add", "-A")
    _git(d, "commit", "-q", "-m", "seed")
    return d


def _run(d, *argv):
    with redirect_stdout(io.StringIO()):
        return CEB.main(list(argv), cwd=str(d))


class CheckEngineBump(unittest.TestCase):

    def test_no_engine_change_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _seed(d)
            self.assertEqual(_run(d, "--staged"), 0)

    def test_staged_change_without_bump_fails(self):  # tested-by: REQ-SELFGATE-039
        with tempfile.TemporaryDirectory() as d:
            d = _seed(d)
            (d / ENGINE_REL).write_text(
                _engine_text("2026-08-20.2", "def gate():\n    return 1\n"), encoding="utf-8")
            _git(d, "add", "-A")
            self.assertEqual(_run(d, "--staged"), 1)

    def test_staged_change_with_bump_passes(self):
        with tempfile.TemporaryDirectory() as d:
            d = _seed(d)
            (d / ENGINE_REL).write_text(
                _engine_text("2026-08-25", "def gate():\n    return 1\n"), encoding="utf-8")
            _git(d, "add", "-A")
            self.assertEqual(_run(d, "--staged"), 0)

    def test_unstaged_change_is_not_judged(self):
        """The hook judges what will be committed; an unstaged edit is not that."""
        with tempfile.TemporaryDirectory() as d:
            d = _seed(d)
            (d / ENGINE_REL).write_text(
                _engine_text("2026-08-20.2", "def gate():\n    return 1\n"), encoding="utf-8")
            self.assertEqual(_run(d, "--staged"), 0)

    def test_base_ref_change_without_bump_fails(self):  # the CI mode; the 2.24.0 / 2.25.0 regression
        with tempfile.TemporaryDirectory() as d:
            d = _seed(d)
            (d / ENGINE_REL).write_text(
                _engine_text("2026-08-20.2", "def gate():\n    return 1\n"), encoding="utf-8")
            _git(d, "commit", "-q", "-am", "engine change, no bump")
            self.assertEqual(_run(d, "--base", "HEAD~1"), 1)

    def test_base_ref_change_with_bump_passes(self):
        with tempfile.TemporaryDirectory() as d:
            d = _seed(d)
            (d / ENGINE_REL).write_text(
                _engine_text("2026-08-25", "def gate():\n    return 1\n"), encoding="utf-8")
            _git(d, "commit", "-q", "-am", "engine change + bump")
            self.assertEqual(_run(d, "--base", "HEAD~1"), 0)

    def test_version_only_edit_passes(self):
        with tempfile.TemporaryDirectory() as d:
            d = _seed(d)
            (d / ENGINE_REL).write_text(_engine_text("2026-08-25"), encoding="utf-8")
            _git(d, "add", "-A")
            self.assertEqual(_run(d, "--staged"), 0)

    def test_unresolvable_base_skips(self):
        """A shallow checkout with no HEAD~1 must not fail the build on its own —
        mirrors the CHANGELOG-entry check's `git rev-parse HEAD~1` guard."""
        with tempfile.TemporaryDirectory() as d:
            _seed(d)
            self.assertEqual(_run(d, "--base", "HEAD~1"), 0)


if __name__ == "__main__":
    unittest.main()
