"""Install or update the reqmap-managed git hook block and CI workflow."""
import os
import stat

from .git import _git

BEGIN = "# reqmap:begin"
END = "# reqmap:end"

HOOK_BLOCK = """# reqmap:begin
# Managed by `reqmap hook install`. Replaced on update. Do not edit inside.
if [ -f scripts/reqmap.py ]; then
  python -X utf8 scripts/reqmap.py gate --if-affected || exit $?
fi
# reqmap:end
"""

WORKFLOW = """# Written by `reqmap hook install`. Gate only — not your app CI.
name: reqmap
on:
  workflow_dispatch:
  pull_request:
    paths:
      - "requirements/**"
      - "scripts/reqmap.py"
      - "scripts/reqmap_engine/**"
permissions:
  contents: read
concurrency:
  group: reqmap-${{ github.ref }}
  cancel-in-progress: true
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v8
"""


def _replace_block(text, block):
    if BEGIN in text and END in text:
        pre = text.split(BEGIN, 1)[0]
        post = text.split(END, 1)[1]
        if post.startswith("\n"):
            post = post[1:]
        return pre + block + post
    if text and not text.endswith("\n"):
        text += "\n"
    return text + ("\n" if text else "") + block


def _write_executable(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)


def cmd_hook(code_root, action="install"):
    """Write or refresh the managed pre-push block and the reqmap workflow."""
    if action not in ("install", "update", None):
        print("usage: reqmap hook [install|update]")
        return 2
    hooks = os.path.join(code_root, ".githooks")
    pre = os.path.join(hooks, "pre-push")
    existing = ""
    if os.path.isfile(pre):
        with open(pre, encoding="utf-8") as f:
            existing = f.read()
    if not existing:
        existing = "#!/usr/bin/env bash\nset -e\n"
    _write_executable(pre, _replace_block(existing, HOOK_BLOCK))
    wf_dir = os.path.join(code_root, ".github", "workflows")
    wf = os.path.join(wf_dir, "reqmap.yml")
    if not os.path.isfile(wf):
        os.makedirs(wf_dir, exist_ok=True)
        with open(wf, "w", encoding="utf-8") as f:
            f.write(WORKFLOW)
        print("wrote {}".format(wf))
    else:
        print("left existing {}".format(wf))
    print("updated {}".format(pre))
    print("enable with: git config core.hooksPath .githooks")
    print("does not change a global hooksPath; run the config locally if you want it")
    return 0


def _changed_paths(code_root):
    names = set()
    for args in (
        ["diff", "--name-only", "HEAD"],
        ["diff", "--cached", "--name-only"],
        ["diff", "--name-only", "HEAD~1", "HEAD"],
    ):
        out = _git(args, cwd=code_root)
        if out:
            names.update(
                n.strip().replace("\\", "/")
                for n in out.splitlines() if n.strip()
            )
    return names


def should_run_gate(ws):
    """True when the worktree/index/last commit can change the gate verdict."""
    names = _changed_paths(ws.code_root)
    if not names:
        return True
    for n in names:
        if n.startswith("requirements/") or n.startswith("plugin/requirements/"):
            return True
        if n.endswith("reqmap.py") or "/reqmap_engine/" in "/" + n:
            return True
    members = getattr(ws, "members", {}) or {}
    items = members.values() if isinstance(members, dict) else members
    try:
        for recs in items:
            if not isinstance(recs, (list, tuple)):
                recs = [recs]
            for rec in recs:
                path = rec.get("path") if isinstance(rec, dict) else getattr(rec, "path", None)
                if not path:
                    continue
                path = str(path).replace("\\", "/")
                if path in names or any(n.endswith(path) or n.endswith("/" + path) for n in names):
                    return True
    except Exception:
        return True
    return False
