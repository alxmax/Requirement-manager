"""Regression tests for scripts/check_versions.py — the leading CI version gate.

Stdlib unittest, run from the repo root:
    python scripts/test_check_versions.py
Synthesizes a throwaway repo tree in a tempdir and repoints check_versions'
module-level paths at it, so the real manifests are never touched.
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_versions as CV


def _setup(d, plugin_ver="2.7.5", market_ver="2.7.5", plug_ver="2.7.5",
           engine="2026-06-21.4", plugins=None, action_majors=("v2", "v2", "v2")):
    """action_majors: the major each of (action.yml, README.md, CLAUDE.md) references;
    None for a file that carries no reference at all."""
    d = Path(d)
    (d / "check").mkdir(parents=True, exist_ok=True)
    for rel, major in zip(CV.ACTION_REF_FILES, action_majors):
        body = "" if major is None else "uses: alxmax/requirement-manager/check@{}".format(major)
        (d / rel).write_text(body, encoding="utf-8")
    (d / "plugin" / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (d / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (d / "plugin" / "scripts").mkdir(parents=True, exist_ok=True)
    plugin_obj = {} if plugin_ver is None else {"version": plugin_ver}
    (d / "plugin" / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_obj), encoding="utf-8")
    if plugins is None:
        plugins = [{"name": "requirement-manager", "version": plug_ver, "source": "./plugin"}]
    (d / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({"version": market_ver, "plugins": plugins}), encoding="utf-8")
    (d / "plugin" / "scripts" / "reqmap.py").write_text(
        'MAP_ENGINE_VERSION = "{}"\n'.format(engine), encoding="utf-8")
    return d


class CheckVersions(unittest.TestCase):
    def _run(self, d):
        saved = (CV.REPO_ROOT, CV.PLUGIN_JSON, CV.MARKETPLACE_JSON, CV.REQMAP_PY)
        CV.REPO_ROOT = Path(d)
        CV.PLUGIN_JSON = Path(d) / "plugin" / ".claude-plugin" / "plugin.json"
        CV.MARKETPLACE_JSON = Path(d) / ".claude-plugin" / "marketplace.json"
        CV.REQMAP_PY = Path(d) / "plugin" / "scripts" / "reqmap.py"
        try:
            with redirect_stdout(io.StringIO()):
                return CV.main([])
        finally:
            CV.REPO_ROOT, CV.PLUGIN_JSON, CV.MARKETPLACE_JSON, CV.REQMAP_PY = saved

    def test_aligned_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d)
            self.assertEqual(self._run(d), 0)

    def test_marketplace_top_level_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d, market_ver="9.9.9")
            self.assertEqual(self._run(d), 1)

    def test_plugin_entry_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d, plug_ver="9.9.9")
            self.assertEqual(self._run(d), 1)

    def test_missing_plugin_version_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d, plugin_ver=None)
            self.assertEqual(self._run(d), 2)

    def test_non_dict_plugins_entry_does_not_crash(self):  # round-1 guard regression
        with tempfile.TemporaryDirectory() as d:
            _setup(d, plugins=["requirement-manager"])   # a bare string, not an object
            self.assertEqual(self._run(d), 1)            # readable diagnostic, not AttributeError

    def test_docstring_mention_before_assignment_is_ignored(self):  # regex anchor regression
        with tempfile.TemporaryDirectory() as d:
            _setup(d)
            (Path(d) / "plugin" / "scripts" / "reqmap.py").write_text(
                '"""example: MAP_ENGINE_VERSION = "not-a-date" """\n'
                'MAP_ENGINE_VERSION = "2026-06-21.4"\n', encoding="utf-8")
            self.assertEqual(self._run(d), 0)   # unanchored regex matched the docstring -> 1

    def test_action_alias_mismatch_fails(self):  # tested-by: REQ-SELFGATE-039
        """The README advertising a different major than the action publishes is the
        exact failure this axis exists for: @v1 in the docs, moved-on content in the repo."""
        with tempfile.TemporaryDirectory() as d:
            _setup(d, action_majors=("v2", "v1", "v2"))
            self.assertEqual(self._run(d), 1)

    def test_action_alias_missing_reference_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d, action_majors=("v2", None, "v2"))
            self.assertEqual(self._run(d), 1)

    def test_action_alias_bare_at_v1_in_prose_is_not_a_reference(self):
        """`@v1` named in prose (documenting the frozen line) must not read as a live
        reference — only the full published path counts."""
        with tempfile.TemporaryDirectory() as d:
            _setup(d)
            (Path(d) / "CLAUDE.md").write_text(
                "`@v1` is frozen and no longer moves." + chr(10) +
                "- uses: alxmax/requirement-manager/check@v2", encoding="utf-8")
            self.assertEqual(self._run(d), 0)

    def test_engine_version_revision_suffix(self):
        for engine, expected in [("2026-06-03.2", 0),   # valid same-day revision
                                 ("2026-06-03.0", 1),   # .0 invalid (>= 1 required)
                                 ("2026-06-03.x", 1),   # non-numeric suffix
                                 ("2026-13-01", 1)]:     # impossible month
            with tempfile.TemporaryDirectory() as d:
                _setup(d, engine=engine)
                self.assertEqual(self._run(d), expected, "engine={!r}".format(engine))


if __name__ == "__main__":
    unittest.main()
