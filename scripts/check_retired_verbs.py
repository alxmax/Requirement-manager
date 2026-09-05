#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fail if a live instruction still names a CLI verb the engine no longer has.

Why this exists, with the receipts: folding a verb into another one has happened
four times in this project, and three of those left behind an instruction that
told a reader to type a command that no longer resolves.

  - `map` folded into `sync`; a consumer repo's CLAUDE.md kept saying
    `reqmap.py map --check` in three places.
  - `findings` folded into `sync --findings`; a consumer's script kept raising
    "run `reqmap.py findings` first".
  - the v4.0.0 verb cut renamed the SKILL.md command list by blanket
    substitution, shipping a contract that documented `scan` (gone) and omitted
    five verbs that existed.

None of those failed at merge. None failed in CI. Each failed later, at the
moment a human followed a written instruction. That is the failure this guard
moves to merge time.

Scope, deliberately narrow: files that INSTRUCT. History is left alone, because
in a changelog or a dated plan the old name is the correct word for what
happened then.

Run:  python scripts/check_retired_verbs.py
Exit: 0 clean, 1 with one line per offending file:line.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The engine is the source of truth for what exists; anything else that looks
# like a verb in an invocation is retired by definition.
def live_verbs():
    """The verbs the engine currently registers, read from its COMMANDS registry."""
    src = io.open(os.path.join(ROOT, "plugin", "scripts", "reqmap.py"),
                  encoding="utf-8").read()
    block = re.search(r"^COMMANDS = \{(.*?)^\}", src, re.M | re.S)
    if not block:
        print("cannot find the COMMANDS registry in reqmap.py", file=sys.stderr)
        sys.exit(2)
    return set(re.findall(r'^    "([a-z-]+)": \{', block.group(1), re.M))


# Prose that tells someone what to type. Everything else is history or generated.
INSTRUCTION_FILES = [
    # The engine prints instructions too: the audit report names the command that
    # runs each section on its own. Those strings go stale like any other doc.
    "plugin/scripts/reqmap.py",
    "CLAUDE.md",
    "README.md",
    "plugin/skills/requirement-manager/SKILL.md",
    "plugin/skills/requirement-manager/SKILL.universal.md",
    ".githooks/pre-commit",
    ".github/workflows/ci.yml",
    "sync_reqmap.sh",
]
INSTRUCTION_GLOBS = [("plugin/requirements", ".md"), ("check", ".yml")]

# Verbs this project has had and no longer has. Only these are flagged: matching
# "any word after reqmap" turns every sentence that mentions the file into a
# finding ("reqmap.py changed", "reqmap links code to requirements").
RETIRED = {
    "next", "show", "audit", "dupes", "search", "draft", "implement",
    "retire", "review", "design", "suggest-verifies", "translate",
    "confirm",
}

# An invocation, not a mention: inside backticks or a quoted string, or after
# `python` / $PY. The quoted form matters because the engine PRINTS instructions
# — the audit report tells you how to run each section on its own, and those
# strings went stale in exactly the same way the docs did.
INVOCATION = re.compile(
    r"(?:`|\"|python\s+|\$PY\s+)[^`\"\n]*?reqmap(?:\.py)?\s+([a-z][a-z-]*)"
)


def candidate_files():
    """The instruction files to scan — the ones a human or an assistant follows."""
    for rel in INSTRUCTION_FILES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            yield rel, p
    for sub, ext in INSTRUCTION_GLOBS:
        base = os.path.join(ROOT, sub)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if name.endswith(ext) and not name.startswith("_"):
                yield os.path.join(sub, name), os.path.join(base, name)


def main():
    """Scan the instruction files for a verb the engine no longer has, and return
    an exit code — non-zero when one is named."""
    live = live_verbs()
    bad = []
    for rel, path in candidate_files():
        try:
            text = io.open(path, encoding="utf-8").read()
        except OSError:
            continue
        for n, line in enumerate(text.split("\n"), 1):
            for verb in INVOCATION.findall(line):
                # a flag, a path or an id is not a verb
                if verb in live or verb not in RETIRED:
                    continue
                bad.append((rel, n, verb, line.strip()[:90]))
    if not bad:
        print("OK  no instruction names a retired verb (%d live: %s)"
              % (len(live), ", ".join(sorted(live))))
        return 0
    print("FAIL  %d instruction(s) name a verb the engine no longer has:" % len(bad))
    for rel, n, verb, line in bad:
        print("  %s:%d  `%s`  %s" % (rel, n, verb, line))
    print("")
    print("Either the verb came back, or the instruction is stale. A reader who")
    print("follows one of these lines gets an unknown-command error.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
