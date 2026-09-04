"""
Cross-tool integration test: seeds reqmap.py in a tempdir, runs sync→gate→map,
and asserts the resulting _map.json is valid and contains the test requirement.

Stdlib only — no external dependencies. Run from the repo root:
    python scripts/test_cross_tool.py

Exit 0 = pass. Exit 1 = fail (details printed to stdout).
This test is the falsification criterion for multi-AI compatibility: if
reqmap.py can drive the full gate→map workflow from a clean repo with no AI
assistant tooling present, the engine is AI-agnostic.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ENGINE_SRC = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "plugin", "scripts", "reqmap.py"
)

REQ_ID = "TEST-CROSS-001"

REQUIREMENT_MD = """\
---
id: {id}
status: confirmed
layer: feature
owner: test
---

# Cross-tool compatibility test

> WHY: verify reqmap.py drives the full workflow from any AI assistant or CLI.

## WHAT — Contract
- It shall pass the gate without link-sync errors when an implements: tag and
  its requirement file both exist.

## HOW — Acceptance
- Given a confirmed requirement with one implements: member, gate exits 0.
- Given gate has passed, sync exits 0 and _reqlock.json is written.
- Given sync has passed, map exits 0 and _map.json contains engine_version,
  nodes, and edges keys.
""".format(id=REQ_ID)

FEATURE_PY = """\
# implements: {id}

def cross_tool_feature():
    pass
""".format(id=REQ_ID)


BUS_ID = "TEST-BUS-002"

BUS_MD = """\
---
id: {id}
status: confirmed
layer: bus
owner: test
---

# A bus capability verified only end-to-end

## Description
- The bus helper returns its input unchanged.

## Cases
CASE-1
  Given  any value
  When   the helper runs
  Then   the same value comes back
""".format(id=BUS_ID)

BUS_PY = "# implements: {id}\n\ndef bus_helper(x):\n    return x\n".format(id=BUS_ID)
BUS_TEST_PY = "# tested-by: {id} @system\n\ndef test_bus_helper():\n    assert True\n".format(id=BUS_ID)


def check_level_rung(tmpdir, req_dir):  # tested-by: ARCH-VLEVEL-037 @integration
    """A confirmed `bus` requirement whose only levelled test link is `@system` must
    draw the RM009 warning from a real `gate` run — the V-model rung rule exercised
    through the CLI, not through a mocked context. Returns 0 on pass."""
    with open(os.path.join(req_dir, BUS_ID + ".md"), "w", encoding="utf-8") as f:
        f.write(BUS_MD)
    with open(os.path.join(tmpdir, "bus.py"), "w", encoding="utf-8") as f:
        f.write(BUS_PY)
    with open(os.path.join(tmpdir, "test_bus.py"), "w", encoding="utf-8") as f:
        f.write(BUS_TEST_PY)
    # --no-map-check: this check is about the rung rule, and the requirement it just
    # wrote is deliberately not in the committed map. Since v4.0.0 `gate` also verifies
    # map freshness, so without the flag it would fail for the right reason at the
    # wrong moment.
    result = subprocess.run([sys.executable, "scripts/reqmap.py", "gate", "--no-map-check"],
                            cwd=tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("FAIL [level rung] gate exited {}".format(result.returncode))
        print(result.stdout.strip())
        return 1
    if "RM009" not in result.stdout or "verified only at @system" not in result.stdout:
        print("FAIL [level rung] gate did not warn about the @system-only bus link")
        print(result.stdout.strip())
        return 1
    return 0


def run_cmd(args, cwd):
    result = subprocess.run(
        [sys.executable] + args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        label = " ".join(args)
        print(f"FAIL [{label}] exit {result.returncode}")
        if result.stdout.strip():
            print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip())
    return result.returncode


def main():
    if not os.path.exists(ENGINE_SRC):
        print(f"SKIP: reqmap.py not found at {ENGINE_SRC}", file=sys.stderr)
        return 0

    with tempfile.TemporaryDirectory() as tmpdir:
        scripts_dir = os.path.join(tmpdir, "scripts")
        req_dir = os.path.join(tmpdir, "requirements")
        os.makedirs(scripts_dir)
        os.makedirs(req_dir)

        engine = os.path.join(scripts_dir, "reqmap.py")
        shutil.copy2(ENGINE_SRC, engine)

        with open(os.path.join(tmpdir, ".reqmapignore"), "w", encoding="utf-8") as f:
            f.write("scripts/reqmap.py\n")

        with open(os.path.join(req_dir, REQ_ID + ".md"), "w", encoding="utf-8") as f:
            f.write(REQUIREMENT_MD)

        with open(os.path.join(tmpdir, "feature.py"), "w", encoding="utf-8") as f:
            f.write(FEATURE_PY)

        # 1. sync — build the initial lock and map
        rc = run_cmd(["scripts/reqmap.py", "sync"], tmpdir)
        if rc != 0:
            return 1

        # 2. gate — must exit 0 (all links resolve, baseline is current)
        rc = run_cmd(["scripts/reqmap.py", "gate"], tmpdir)
        if rc != 0:
            return 1

        # 3. sync — regenerates everything derived, including a valid _map.json
        #    (`map` folded into `sync` in v4.0.0)
        rc = run_cmd(["scripts/reqmap.py", "sync"], tmpdir)
        if rc != 0:
            return 1

        map_json_path = os.path.join(req_dir, "_map.json")
        if not os.path.exists(map_json_path):
            print(f"FAIL: _map.json was not written to {map_json_path}")
            return 1

        with open(map_json_path, encoding="utf-8") as f:
            data = json.load(f)

        # 4. the level-rung rule, end to end (ARCH-VLEVEL-037 at @integration)
        if check_level_rung(tmpdir, req_dir) != 0:
            return 1

        for key in ("engine_version", "nodes", "edges"):
            if key not in data:
                print(f"FAIL: _map.json missing required key '{key}'")
                return 1

        if not any(n.get("id") == REQ_ID for n in data["nodes"]):
            print(f"FAIL: {REQ_ID} not found in _map.json nodes")
            return 1

        print(
            f"OK  sync->gate->map passed | _map.json valid | "
            f"{REQ_ID} present | engine {data['engine_version']}"
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
