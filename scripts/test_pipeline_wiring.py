"""Structural tests for this repo's own pipeline wiring.

Stdlib unittest, run from the repo root:
    python -X utf8 scripts/test_pipeline_wiring.py
The CI workflow, the dev git hooks, the published Action and the cache-sync
script run only on GitHub, on a commit or on a maintainer's machine, so no
suite executes them. These tests read the real files and assert what their
requirements' cases state: the job exists, the step runs the named command
with the named flags, in the stated order. Text and regex only: no YAML
library, because the repo's checks stay stdlib-only.
"""
import os
import re
import unittest
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CI = ".github/workflows/ci.yml"
ACTION = "check/action.yml"
PRE_COMMIT = ".githooks/pre-commit"
PRE_PUSH = ".githooks/pre-push"
SYNC = "sync_reqmap.sh"
VIEWER = "plugin/scripts/_map_viewer.html"


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def _jobs(text):
    """{job id: its block} from a workflow's top-level `jobs:` map."""
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"^  ([\w-]+):[ \t]*$", body, flags=re.M)
    return dict(zip(parts[1::2], parts[2::2]))


def _steps(block, indent):
    """The items of a `steps:` list, in order, each as its own text."""
    body = re.split(r"^ *steps:[ \t]*$", block, maxsplit=1, flags=re.M)[1]
    return re.split(r"^" + " " * indent + "- ", body, flags=re.M)[1:]


def _find(steps, needle):
    """Index of the first step whose text contains `needle`."""
    for i, step in enumerate(steps):
        if needle in step:
            return i
    raise AssertionError("no step contains {!r}".format(needle))


def _ci_steps(job):
    return _steps(_jobs(_read(CI))[job], 6)


def _positions(text, needles):
    """Offset of each needle in `text`; fails naming the one missing."""
    out = []
    for n in needles:
        i = text.find(n)
        if i < 0:
            raise AssertionError("{!r} not found".format(n))
        out.append(i)
    return out


class SelfGate(unittest.TestCase):  # tested-by: ARCH-SELFGATE-039 @integration
    def test_one_verdict(self):  # verifies: ARCH-SELFGATE-039#CASE-1
        steps = _ci_steps("gate-and-tests")
        gate = steps[_find(steps, "reqmap.py gate")]
        self.assertRegex(gate, r"python -X utf8 scripts/reqmap\.py gate\b")
        self.assertRegex(_read(PRE_COMMIT),
                         r'plugin/scripts/reqmap\.py gate\b')
        action = _read(ACTION)
        self.assertRegex(action, r'"\$\{\{ inputs\.reqmap-path \}\}" gate\b')
        self.assertIn("default: 'scripts/reqmap.py'", action)


class CiWorkflow(unittest.TestCase):  # tested-by: REQ-SELFGATE-916 @unit
    def test_gate_on_push_and_pr(self):  # verifies: REQ-SELFGATE-916#CASE-1
        on = _read(CI).split("\non:\n", 1)[1].split("\n\n", 1)[0]
        self.assertRegex(on, r"push:\s*\n\s*branches: \[main\]")
        self.assertIn("pull_request:", on)
        steps = _ci_steps("gate-and-tests")
        gate = steps[_find(steps, "reqmap.py gate")]
        self.assertIn("working-directory: plugin\n", gate)
        self.assertIn("scripts/reqmap.py gate --full --code ..", gate)

    def test_checks_precede_gate(self):  # verifies: REQ-SELFGATE-916#CASE-2
        steps = _ci_steps("gate-and-tests")
        order = [_find(steps, "run: python scripts/check_versions.py"),
                 _find(steps, "check_engine_bump.py --base HEAD~1"),
                 _find(steps, "run: python -X utf8 scripts/check_retired_"),
                 _find(steps, "reqmap.py gate --full")]
        self.assertEqual(order, sorted(order))
        self.assertEqual(len(set(order)), 4)

    def test_release_moves_alias(self):  # verifies: REQ-SELFGATE-916#CASE-3
        release = _jobs(_read(CI))["release"]
        self.assertIn("github.event_name == 'push'", release)
        self.assertIn("github.ref == 'refs/heads/main'", release)
        steps = _steps(release, 6)
        alias = steps[_find(steps, "major-alias tag")]
        # A step of its own, so the "already released, exit 0" shortcut of
        # the release step never skips it.
        self.assertNotIn("gh release view", alias)
        self.assertIn("requirement-manager/check@v[0-9]+' check/action.yml",
                      alias)
        self.assertIn("plugin/.claude-plugin/plugin.json", alias)
        self.assertIn('git tag -f "$ALIAS" "$TARGET"', alias)
        self.assertIn('git push --force origin "refs/tags/$ALIAS"', alias)


class DevHooks(unittest.TestCase):  # tested-by: REQ-SELFGATE-1070 @unit
    CHECKS = ("check_versions.py", "check_engine_bump.py",
              "check_retired_verbs.py", "reqmap.py gate --full")

    def test_ci_order(self):  # verifies: REQ-SELFGATE-1070#CASE-1
        hook = _read(PRE_COMMIT)
        at = _positions(hook, ('"$PY" scripts/check_versions.py',
                               "check_engine_bump.py --staged",
                               "scripts/check_retired_verbs.py",
                               "reqmap.py gate --full --root plugin"))
        self.assertEqual(at, sorted(at))
        steps = _ci_steps("gate-and-tests")
        ci = [_find(steps, "run: python scripts/check_versions.py"),
              _find(steps, "run: python scripts/check_engine_bump.py"),
              _find(steps, "run: python -X utf8 scripts/check_retired_"),
              _find(steps, "reqmap.py gate --full")]
        self.assertEqual(ci, sorted(ci))

    def test_fail_stops(self):  # verifies: REQ-SELFGATE-1070#CASE-2
        hook = _read(PRE_COMMIT)
        blocks = re.findall(r"^if ! (.*?); then\n(.*?)^fi$", hook,
                            flags=re.M | re.S)
        for check in self.CHECKS:
            body = [b for cond, b in blocks if check in cond]
            self.assertEqual(len(body), 1, check)
            self.assertRegex(body[0], r"\n  exit 1\n$", check)

    def test_push_to_main(self):  # verifies: REQ-SELFGATE-1070#CASE-3
        hook = _read(PRE_PUSH)
        self.assertRegex(hook, r"while read local_ref local_sha remote_ref")
        m = re.search(r'if \[\[ (.*?) \]\]; then\n(.*?)\n\s*fi', hook,
                      flags=re.S)
        self.assertIsNotNone(m)
        self.assertIn('"$remote_ref" == "refs/heads/main"', m.group(1))
        self.assertIn('"$remote_ref" == "refs/heads/master"', m.group(1))
        self.assertRegex(m.group(2), r"\bexit 1$")
        self.assertRegex(hook.rstrip(), r"\bdone\nexit 0$")


class PublishedAction(unittest.TestCase):  # tested-by: REQ-SELFGATE-1071 @unit
    def _gate_step(self):
        text = _read(ACTION)
        runs = text.split("\nruns:\n", 1)[1]
        self.assertIn("using: 'composite'", runs)
        steps = _steps(runs, 4)
        return steps[_find(steps, "name: reqmap gate")]

    def _input(self, name):
        text = _read(ACTION).split("\ninputs:\n", 1)[1].split("\nruns:", 1)[0]
        parts = re.split(r"^  ([\w-]+):[ \t]*$", text, flags=re.M)
        return dict(zip(parts[1::2], parts[2::2]))[name]

    def test_same_gate(self):  # verifies: REQ-SELFGATE-1071#CASE-1
        step = self._gate_step()
        self.assertIn('python -X utf8 "${{ inputs.reqmap-path }}" gate',
                      step)
        self.assertIn("default: 'scripts/reqmap.py'",
                      self._input("reqmap-path"))

    def test_inputs_switch(self):  # verifies: REQ-SELFGATE-1071#CASE-2
        for name in ("lint", "freshness"):
            self.assertIn("default: 'true'", self._input(name), name)
        step = self._gate_step()
        self.assertIn('if [ "${{ inputs.lint }}" != "true" ]; then '
                      'FLAGS="$FLAGS --no-lint"; fi', step)
        self.assertIn('if [ "${{ inputs.freshness }}" != "true" ]; then '
                      'FLAGS="$FLAGS --no-map-check"; fi', step)
        self.assertRegex(step, r"\}\}\" gate \$FLAGS \"\$\{CODE_ARGS\[@\]\}\"\n")

    def test_code_input_widens_the_scan(self):  # verifies: REQ-SELFGATE-1071#CASE-4
        self.assertIn("default: ''", self._input("code"))
        self.assertIn('if [ -n "${{ inputs.code }}" ]; then '
                      'CODE_ARGS=(--code "${{ inputs.code }}"); fi',
                      self._gate_step())

    def test_names_alias(self):  # verifies: REQ-SELFGATE-1071#CASE-3
        # The same pattern the release job's alias step greps for.
        refs = set(re.findall(r"requirement-manager/check@(v[0-9]+)",
                              _read(ACTION)))
        self.assertEqual(len(refs), 1, refs)


class SyncScript(unittest.TestCase):  # tested-by: REQ-SELFGATE-1072 @unit
    def _loop(self):
        text = _read(SYNC)
        return text.split('for REPO in "$@"; do', 1)[1].split("\ndone", 1)[0]

    def test_cache_gets_engine(self):  # verifies: REQ-SELFGATE-1072#CASE-1
        text = _read(SYNC)
        self.assertRegex(text, r'PLUGIN_VERSION=\$\(grep -m1 \'"version"\' '
                               r'"\$SCRIPT_DIR/plugin/\.claude-plugin/'
                               r'plugin\.json"')
        self.assertIn('CACHE="$CACHE_BASE/$PLUGIN_VERSION"', text)
        cache = text.split('if [[ -d "$CACHE" ]]; then', 1)[1]
        cache = cache.split("\nelse", 1)[0]
        for line in ('cp "$SRC" "$CACHE/scripts/reqmap.py"',
                     'cp -r "$PKG_SRC" "$CACHE/scripts/reqmap_engine"',
                     'rm -rf "$CACHE/scripts/reqmap_engine/__pycache__"',
                     'cp "$VIEWER_SRC" "$CACHE/scripts/_map_viewer.html"'):
            self.assertIn(line, cache)
        self.assertIn('SRC="$SCRIPT_DIR/plugin/scripts/reqmap.py"', text)
        self.assertIn('PKG_SRC="$SCRIPT_DIR/plugin/scripts/reqmap_engine"',
                      text)

    def test_never_seeds(self):  # verifies: REQ-SELFGATE-1072#CASE-2
        loop = self._loop()
        skip = re.search(r'if \[\[ -z "\$REL" \]\]; then\n(.*?)\n\s*fi',
                         loop, flags=re.S)
        self.assertIsNotNone(skip)
        self.assertRegex(skip.group(1), r"WARN: .*; continue$")
        self.assertLess(skip.end(), loop.index("cp "))
        self.assertLess(loop.index('REL=$(find_engine "$REPO")'),
                        skip.start())

    def test_viewer_guard(self):  # verifies: REQ-SELFGATE-1072#CASE-3
        loop = self._loop()
        guard = re.search(r'-f "\$REPO/\$ENGINE_DIR/_map_viewer\.html" '
                          r'\]\]; then\n(.*?)\n\s*fi', loop, flags=re.S)
        self.assertIsNotNone(guard)
        copy = 'cp "$VIEWER_SRC" "$REPO/$ENGINE_DIR/_map_viewer.html"'
        self.assertIn(copy, guard.group(1))
        self.assertEqual(loop.count('cp "$VIEWER_SRC"'), 1)


class ArtifactsJob(unittest.TestCase):
    # tested-by: ARCH-REPRO-041 @integration  # tested-by: REQ-REPRO-905 @unit
    def test_stale_viewer(self):
        # verifies: ARCH-REPRO-041#CASE-1  # verifies: REQ-REPRO-905#CASE-1
        block = _jobs(_read(CI))["artifacts"]
        self.assertNotRegex(block, r"(?m)^    if:", "runs on every trigger")
        steps = _steps(block, 6)
        check = steps[_find(steps, "git diff --exit-code")]
        self.assertIn("git diff --exit-code -- " + VIEWER, check)
        self.assertIn("exit 1", check)
        error = re.search(r"::error::(.*)", check).group(1)
        self.assertIn(VIEWER, error)
        self.assertIn("npm run build:viewer", error)

    def test_smoke_first(self):
        # verifies: ARCH-REPRO-041#CASE-2  # verifies: REQ-REPRO-905#CASE-2
        steps = _ci_steps("artifacts")
        smoke = _find(steps, "name: Viewer SSR smoke")
        self.assertIn("working-directory: app", steps[smoke])
        self.assertIn("run: npm run sync -- --require && npm run smoke",
                      steps[smoke])
        self.assertLess(smoke, _find(steps, "run: npm run build:viewer"))

    def test_diff_is_the_check(self):  # verifies: REQ-REPRO-905#CASE-3
        steps = _ci_steps("artifacts")
        build = _find(steps, "run: npm run build:viewer")
        check = steps[build + 1]
        self.assertIn("git diff --exit-code -- " + VIEWER, check)
        run = check.split("run: |", 1)[1].split("\n\n", 1)[0]
        self.assertEqual(re.findall(r"\b(?:cmp|diff|sha\w*sum)\b", run),
                         ["diff"])

    def test_release_needs(self):
        # verifies: ARCH-REPRO-041#CASE-3  # verifies: REQ-REPRO-905#CASE-4
        release = _jobs(_read(CI))["release"]
        needs = re.search(r"^    needs: \[(.*?)\]", release, flags=re.M)
        self.assertIsNotNone(needs)
        names = {n.strip() for n in needs.group(1).split(",")}
        self.assertEqual({"artifacts", "gate-and-tests", "tests"}, names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
