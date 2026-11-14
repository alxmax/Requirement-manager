"""Fail when `plugin/`, the directory edition, holds a file the plugin directory refuses
from an organization that is not Verified.

Run from the repo root:
    python -X utf8 scripts/check_directory_edition.py [ROOT]

ROOT defaults to this repository's `plugin/`. Exit 0 when clean, 1 with one line per
offending file otherwise.
"""
# implements: ARCH-SELFGATE-039  # implements: REQ-SELFGATE-1130
import os
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "plugin"
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
ALLOWED = {".md", ".txt", ".json", ".yaml", ".yml"} | IMAGES
KEEP_ANY_TYPE = {"LICENSE", ".gitignore"}
RUNNABLE_CONFIG = {".mcp.json", "hooks.json", ".lsp.json", "monitors.json"}
RUNNABLE_DIRS = {"hooks"}


def file_problems(rel, data):  # implements: REQ-SELFGATE-1130
    """The rules one file at `rel` (posix, relative to the edition) breaks."""
    parts = rel.split("/")
    name = parts[-1]
    ext = os.path.splitext(name)[1].lower()
    out = []
    if name in RUNNABLE_CONFIG:
        out.append("runnable configuration")
    if any(p in RUNNABLE_DIRS for p in parts[:-1]):
        out.append("inside a hooks/ folder")
    if ext not in ALLOWED and name not in KEEP_ANY_TYPE:
        out.append("disallowed file type")
    if parts[0] == ".claude-plugin" and name != "plugin.json" and ext not in IMAGES:
        out.append("not plugin.json or an image in .claude-plugin/")
    if data.startswith(b"#!"):
        out.append("starts with #!")
    if ext not in IMAGES:
        if b"\x00" in data:
            out.append("holds a NUL byte")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            out.append("not UTF-8")
    return out


def check(root):  # implements: REQ-SELFGATE-1130
    """[(rel, rule)] for every file under `root` that breaks a rule, sorted."""
    found = []
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            for rule in file_problems(rel, path.read_bytes()):
                found.append((rel, rule))
    return sorted(found)


def main(argv=None):  # implements: REQ-SELFGATE-1130
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]) if args else DEFAULT_ROOT
    if not root.is_dir():
        print("FAIL  {} is not a directory".format(root))
        return 2
    found = check(root)
    for rel, rule in found:
        print("FAIL  {}: {}".format(rel, rule))
    if found:
        print("The plugin directory refuses these from an organization that is not "
              "Verified; move them to plugin-full/.")
        return 1
    print("OK  {} holds only files the plugin directory accepts".format(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
