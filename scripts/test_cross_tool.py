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

        # 3. map — must produce a valid _map.json
        rc = run_cmd(["scripts/reqmap.py", "map"], tmpdir)
        if rc != 0:
            return 1

        map_json_path = os.path.join(req_dir, "_map.json")
        if not os.path.exists(map_json_path):
            print(f"FAIL: _map.json was not written to {map_json_path}")
            return 1

        with open(map_json_path, encoding="utf-8") as f:
            data = json.load(f)

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
