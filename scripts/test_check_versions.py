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
           engine="2026-06-21.4", plugins=None, action_majors=(), apm_ver=None,
           dir_ver=None):
    """action_majors: the major each file in CV.ACTION_REF_FILES (in order) references;
    None for a file that carries no reference at all. Files past the end of the
    tuple default to "v2"."""
    d = Path(d)
    majors = tuple(action_majors) + ("v2",) * (len(CV.ACTION_REF_FILES) - len(action_majors))
    for rel, major in zip(CV.ACTION_REF_FILES, majors):
        body = "" if major is None else "uses: alxmax/requirement-manager/check@{}".format(major)
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(body, encoding="utf-8")
    (d / "plugin-full" / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (d / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (d / "plugin-full" / "scripts").mkdir(parents=True, exist_ok=True)
    plugin_obj = {} if plugin_ver is None else {"version": plugin_ver}
    (d / "plugin-full" / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_obj), encoding="utf-8")
    if plugins is None:
        plugins = [{"name": "requirement-manager", "version": plug_ver, "source": "./plugin-full"}]
    (d / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps({"version": market_ver, "plugins": plugins}), encoding="utf-8")
    (d / "plugin-full" / "scripts" / "reqmap_engine").mkdir()
    (d / "plugin-full" / "scripts" / "reqmap_engine" / "__init__.py").write_text(
        'MAP_ENGINE_VERSION = "{}"\n'.format(engine), encoding="utf-8")
    (d / "pyproject.toml").write_text(
        '[project]\nname = "reqmap"\nversion = "{}"\n'.format(
            plugin_ver or "0.0.0"), encoding="utf-8")
    (d / "plugin-full" / "apm.yml").write_text(
        "name: requirement-manager\nversion: {}\n".format(
            apm_ver or plugin_ver or "0.0.0"), encoding="utf-8")
    (d / "plugin" / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (d / "plugin" / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "requirement-manager",
                    "version": dir_ver or plugin_ver or "0.0.0"}, indent=2) + "\n",
        encoding="utf-8")
    return d


TWO_ENTRIES = [
    {"name": "requirement-manager", "version": "2.7.5", "source": "./plugin"},
    {"name": "requirement-manager-full", "version": "2.7.5", "source": "./plugin-full"},
]


class CheckVersions(unittest.TestCase):
    def _run(self, d, argv=()):
        saved = (CV.REPO_ROOT, CV.PLUGIN_JSON, CV.MARKETPLACE_JSON, CV.REQMAP_PY,
                 CV.APM_YML, CV.DIRECTORY_PLUGIN_JSON)
        CV.REPO_ROOT = Path(d)
        CV.DIRECTORY_PLUGIN_JSON = (Path(d) / "plugin" / ".claude-plugin"
                                    / "plugin.json")
        CV.PLUGIN_JSON = Path(d) / "plugin-full" / ".claude-plugin" / "plugin.json"
        CV.MARKETPLACE_JSON = Path(d) / ".claude-plugin" / "marketplace.json"
        CV.REQMAP_PY = Path(d) / "plugin-full" / "scripts" / "reqmap_engine" / "__init__.py"
        CV.APM_YML = Path(d) / "plugin-full" / "apm.yml"
        try:
            with redirect_stdout(io.StringIO()):
                return CV.main(list(argv))
        finally:
            (CV.REPO_ROOT, CV.PLUGIN_JSON, CV.MARKETPLACE_JSON, CV.REQMAP_PY,
             CV.APM_YML, CV.DIRECTORY_PLUGIN_JSON) = saved

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

    def test_apm_manifest_mismatch_fails(self):
        """APM requires a `version:` in plugin-full/apm.yml; a release that bumps
        plugin.json and leaves it behind must fail the build."""
        with tempfile.TemporaryDirectory() as d:
            _setup(d, apm_ver="9.9.9")
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
            (Path(d) / "plugin-full" / "scripts" / "reqmap_engine" / "__init__.py").write_text(
                '"""example: MAP_ENGINE_VERSION = "not-a-date" """\n'
                'MAP_ENGINE_VERSION = "2026-06-21.4"\n', encoding="utf-8")
            self.assertEqual(self._run(d), 0)   # unanchored regex matched the docstring -> 1

    def test_action_alias_mismatch_fails(self):  # tested-by: ARCH-SELFGATE-039  # verifies: ARCH-SELFGATE-039#CASE-2
        """The README advertising a different major than the action publishes is the
        exact failure this axis exists for: @v1 in the docs, moved-on content in the repo."""
        with tempfile.TemporaryDirectory() as d:
            _setup(d, action_majors=("v2", "v1", "v2"))
            self.assertEqual(self._run(d), 1)

    def test_action_alias_skill_file_lagging_fails(self):  # tested-by: ARCH-SELFGATE-039  # verifies: ARCH-SELFGATE-039#CASE-2
        """SKILL.md is the file a consumer copies its workflow from. It kept `@v1` for
        three releases after README/CLAUDE.md moved to `@v2` because it was not in
        ACTION_REF_FILES — this pins that it is now."""
        with tempfile.TemporaryDirectory() as d:
            _setup(d, action_majors=("v2", "v2", "v2", "v1", "v2"))
            self.assertEqual(self._run(d), 1)

    def test_action_alias_not_tracking_plugin_major_fails(self):  # verifies: ARCH-SELFGATE-039#CASE-3
        """ADR-0029: the alias IS the plugin's major. Agreement across the documented
        files is no longer enough — `v4.0.0` advertised as `@v3` reads like a mistake at
        every glance, so it is one."""
        with tempfile.TemporaryDirectory() as d:
            _setup(d, plugin_ver="3.0.0", market_ver="3.0.0", plug_ver="3.0.0")  # alias defaults to v2
            self.assertEqual(self._run(d), 1)

    def test_action_alias_tracking_plugin_major_passes(self):  # verifies: ARCH-SELFGATE-039#CASE-3
        with tempfile.TemporaryDirectory() as d:
            _setup(d, plugin_ver="3.0.0", market_ver="3.0.0", plug_ver="3.0.0",
                   action_majors=("v3",) * len(CV.ACTION_REF_FILES))
            self.assertEqual(self._run(d), 0)

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

    def test_pyproject_version_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d)
            (Path(d) / "pyproject.toml").write_text(
                '[project]\nname = "reqmap"\nversion = "9.9.9"\n',
                encoding="utf-8")
            self.assertEqual(self._run(d), 1)

    def test_directory_plugin_version_mismatch_fails(self):
        """The marketplace's first entry installs the directory edition: a bump
        that leaves its plugin.json behind ships a release that entry never sees."""
        with tempfile.TemporaryDirectory() as d:
            _setup(d, plugins=TWO_ENTRIES, dir_ver="9.9.9")
            self.assertEqual(self._run(d), 1)

    def test_directory_plugin_manifest_missing_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d)
            (Path(d) / "plugin" / ".claude-plugin" / "plugin.json").unlink()
            with self.assertRaises(SystemExit) as raised:   # _load_json's exit, as for marketplace.json
                self._run(d)
            self.assertEqual(raised.exception.code, 2)

    def test_two_entries_aligned_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _setup(d, plugins=TWO_ENTRIES)
            self.assertEqual(self._run(d), 0)

    def test_stale_second_entry_fails(self):
        """Each plugins[] entry is checked, not just the first: the full edition's
        entry left behind is the drift that would strand its installs."""
        with tempfile.TemporaryDirectory() as d:
            entries = [dict(TWO_ENTRIES[0]), dict(TWO_ENTRIES[1], version="2.7.4")]
            _setup(d, plugins=entries)
            self.assertEqual(self._run(d), 1)

    def test_fix_syncs_directory_plugin_and_every_entry(self):
        with tempfile.TemporaryDirectory() as d:
            entries = [dict(TWO_ENTRIES[0], version="2.7.4"),
                       dict(TWO_ENTRIES[1], version="2.7.4")]
            _setup(d, plugins=entries, dir_ver="2.7.4")
            self.assertEqual(self._run(d, ["--fix"]), 0)
            dir_json = json.loads((Path(d) / "plugin" / ".claude-plugin"
                                   / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(dir_json, {"name": "requirement-manager", "version": "2.7.5"})
            market = json.loads((Path(d) / ".claude-plugin" / "marketplace.json")
                                .read_text(encoding="utf-8"))
            self.assertEqual([p["version"] for p in market["plugins"]], ["2.7.5", "2.7.5"])

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
