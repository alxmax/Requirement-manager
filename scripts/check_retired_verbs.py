#!/usr/bin/env python
# implements: ARCH-SELFGATE-039
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

A fifth fold was proposed on 2026-09-08 and audited by nine senators
(`senate-reqmap-cli-surface-18-to-5`, MODIFY). They found this guard blind to the
change it would have to catch, in three ways, all fixed here:

  - it matched VERBS only, so `gate --show` read as the live verb `gate` and a
    cull of mode FLAGS passed it green;
  - it required an invocation to sit inside backticks or quotes or follow
    `python `, so `.githooks/pre-commit`'s own `(fix: reqmap.py map ...)` — a
    live instruction naming a verb folded at v7.0.0 — slipped through the file
    it already scanned;
  - it read one root, so the consumer repo the last two folds actually broke was
    never looked at.

The flag half is DERIVED, not enumerated. A hand-kept `RETIRED_FLAGS` set is one
more list to forget: the parser in `reqmap.py` is what actually accepts or
rejects a flag, so a flag missing from it is retired by definition, exactly as a
verb missing from `COMMANDS` already was. The guard therefore starts firing the
moment a flag is cut, with nobody updating anything.

Scope, deliberately narrow: files that INSTRUCT. History is left alone, because
in a changelog or a dated plan the old name is the correct word for what
happened then.

Run:  python scripts/check_retired_verbs.py [EXTRA_ROOT ...]
      An EXTRA_ROOT is a consumer checkout: its instructions are read against
      THIS engine's live surface, which is what it gets when it re-vendors.
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
    """The verbs the engine currently registers, read from its COMMANDS registry —
    `reqmap_engine/commands.py` since the engine became a package (ADR-0035), with the
    single-file `reqmap.py` still accepted for an older checkout."""
    block = None
    for rel in (("plugin", "scripts", "reqmap_engine", "commands.py"),
                ("plugin", "scripts", "reqmap.py")):
        path = os.path.join(ROOT, *rel)
        if os.path.exists(path):
            src = io.open(path, encoding="utf-8").read()
            block = re.search(r"^COMMANDS = \{(.*?)^\}", src, re.M | re.S)
            if block:
                break
    if not block:
        print("cannot find the COMMANDS registry in reqmap_engine/commands.py or reqmap.py",
              file=sys.stderr)
        sys.exit(2)
    return set(re.findall(r'^    "([a-z-]+)": \{', block.group(1), re.M))


def live_flags(root=None):
    """Every long flag the CLI's parser accepts, read from `reqmap.py`'s own
    `add_argument` calls.

    The parser, not `COMMANDS`, is the authority here: the registry deliberately
    omits the shared workspace flags (`--root`, `--reqs`, `--code`, `--cache`),
    so checking against it alone would report four flags that work. Returns an
    empty set when the file cannot be read, and the caller then skips the flag
    half rather than reporting every flag as retired — a guard that cannot read
    the engine must fail open, not accuse.
    """
    path = os.path.join(root or ROOT, "plugin", "scripts", "reqmap.py")
    try:
        with io.open(path, encoding="utf-8") as fh:
            src = fh.read()
    except OSError:
        return set()
    return set(re.findall(r'add_argument\(\s*"(--[a-z][a-z0-9-]*)"', src))


# Prose that tells someone what to type. Everything else is history or generated.
INSTRUCTION_FILES = [
    # The engine prints instructions too: the audit report names the command that
    # runs each section on its own. Those strings go stale like any other doc.
    "plugin/scripts/reqmap.py",
    "CLAUDE.md",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    # The hook shipped to consumers: a retired verb there fails every consumer commit.
    "plugin/hooks/pre-commit",
    # NOT one skill by name: the plugin ships three, and naming one is how six dead
    # invocations reached consumers through `requirement-quality-review`. The glob
    # below reads every SKILL*.md under plugin/skills/, whatever is added next.
    ".githooks/pre-commit",
    ".github/workflows/ci.yml",
    "sync_reqmap.sh",
]
# The engine package prints instructions too (audit sections, decompose, next steps).
INSTRUCTION_GLOBS = [("plugin/requirements", ".md"), ("check", ".yml"),
                     ("plugin/scripts/reqmap_engine", ".py")]
# Every skill the plugin ships, at any depth: each one instructs a reader to run the
# engine, and each goes stale the same way.
INSTRUCTION_TREES = [("plugin/skills", "SKILL", ".md")]

# Verbs this project has had and no longer has. Only these are flagged: matching
# "any word after reqmap" turns every sentence that mentions the file into a
# finding ("reqmap.py changed", "reqmap links code to requirements").
# A line that says a verb is GONE is the opposite of an instruction to run it, and
# this repo writes those deliberately — the migration note for `check` is the reason
# a reader stops calling it. Matched on the line itself, so a real instruction that
# happens to sit near one is still reported.
REMOVAL_NOTE = re.compile(
    r"no longer exists|was removed|were removed|is gone|are gone|removed in|"
    r"deprecated alias|folded into|replaced by|renamed to|"
    # The consumer repos are not all written in English, and a removal note that
    # the guard cannot read is reported as the very instruction it retracts.
    r"nu mai exist|a fost eliminat|au fost eliminate|a fost redenumit|"
    r"comasat|înlocuit de|inlocuit de", re.I)

RETIRED = {
    # folded into `gate`'s mode flags in v4.0.0/v5.0.0
    "next", "show", "audit", "dupes", "search", "review", "implement",
    "design", "health", "coverage", "lint",
    # folded into `sync`
    "map", "site", "export", "findings", "retire", "suggest-verifies",
    "gen-integration",
    # folded into `init`
    "draft", "plan",
    # removed outright
    "check", "scan", "translate", "confirm",
}

# An invocation, not a mention: inside backticks or a quoted string, or after
# `python` / $PY. The quoted form matters because the engine PRINTS instructions
# — the audit report tells you how to run each section on its own, and those
# strings went stale in exactly the same way the docs did.
INVOCATION = re.compile(
    r"(?:`|\"|python\s+|\$PY\s+)[^`\"\n]*?reqmap(?:\.py)?\s+([a-z][a-z-]*)"
)

# The same call with no delimiter in front of it. `.githooks/pre-commit` wrote its
# own repair hint as `(fix: reqmap.py map --root plugin --code .)` — a live
# instruction, in a file this guard already scanned, that the delimited pattern
# above could not see. Kept as a SECOND pattern rather than a relaxation of the
# first, because only the retired-VERB check may use it: an undelimited match is
# safe there (the verb must be in `RETIRED` to be reported at all) and would not
# be safe for the flag check, where any `--word` in ordinary prose downstream of
# the word "reqmap" would start accusing.
BARE_INVOCATION = re.compile(r"reqmap(?:\.py)?\s+([a-z][a-z-]*)")

# A long flag as it appears in a call. Digits allowed: `--i18n` is one.
FLAG = re.compile(r"(--[a-z][a-z0-9-]*)")

# Where one call stops: the closing backtick or quote, or a shell separator that
# starts another command.
END_OF_CALL = re.compile(r"`|\"|&&|\|\||;")


# A consumer checkout has no `plugin/` prefix and no skills tree — it vendored the
# engine and wrote its own instructions around it. Scanned as globs rather than a
# fixed list because no two consumers lay their docs out the same way.
CONSUMER_FILES = ["CLAUDE.md", "README.md", "AGENTS.md", "CONTRIBUTING.md", "TODO.md"]
CONSUMER_TREES = [("scripts", "", ".py"), ("scripts", "", ".sh"), (".githooks", "", ""),
                  (".github/workflows", "", ".yml"), ("docs", "", ".md"),
                  ("specs", "", ".md"), ("requirements", "", ".md")]
# The consumer's OWN vendored `reqmap.py` is deliberately not scanned. Its printed
# strings belong to whatever engine snapshot it holds, so reporting them says only
# "your copy is old" — which `check/engine_staleness.py` already says, at the
# version level, where it can be acted on.
CONSUMER_SKIP = ("scripts/reqmap.py", "requirements/_")


def candidate_files(root=ROOT, consumer=False):
    """The instruction files to scan — the ones a human or an assistant follows."""
    if consumer:
        for rel in CONSUMER_FILES:
            p = os.path.join(root, rel)
            if os.path.exists(p):
                yield rel, p
        for sub, prefix, ext in CONSUMER_TREES:
            base = os.path.join(root, sub.replace("/", os.sep))
            if not os.path.isdir(base):
                continue
            for dirpath, dirs, names in os.walk(base):
                dirs[:] = [d for d in dirs if d != ".git"]
                for name in sorted(names):
                    if not name.startswith(prefix) or not name.endswith(ext):
                        continue
                    full = os.path.join(dirpath, name)
                    rel = os.path.relpath(full, root).replace(os.sep, "/")
                    if any(rel.startswith(skip) for skip in CONSUMER_SKIP):
                        continue
                    yield rel, full
        return
    for rel in INSTRUCTION_FILES:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            yield rel, p
    for sub, ext in INSTRUCTION_GLOBS:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if name.endswith(ext) and not name.startswith("_"):
                yield os.path.join(sub, name), os.path.join(base, name)
    for sub, prefix, ext in INSTRUCTION_TREES:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, names in os.walk(base):
            for name in sorted(names):
                if name.startswith(prefix) and name.endswith(ext):
                    p = os.path.join(dirpath, name)
                    yield os.path.relpath(p, root).replace(os.sep, "/"), p


def scan_line(line, live, flags):
    """Every retired name this one line instructs a reader to type.

    Yields `(kind, name)`, kind being "verb" or "flag". A line that says a name is
    GONE is the opposite of an instruction to run it, and is skipped whole — this
    repo writes those deliberately, and the migration note is the reason a reader
    stops calling the old name.
    """
    if REMOVAL_NOTE.search(line):
        return
    for verb in BARE_INVOCATION.findall(line):
        if verb not in live and verb in RETIRED:
            yield "verb", verb
    if not flags:
        return                      # engine unreadable: fail open, do not accuse
    for m in INVOCATION.finditer(line):
        if m.group(1) not in live:
            continue                # not a call to a verb that exists
        # Only the flags of THIS call. One line often carries a second command
        # after it — `reqmap.py gate` ... `npm test --workspace=apps/web` — and
        # reading to end-of-line hands the neighbour's flags to reqmap.
        for flag in FLAG.findall(END_OF_CALL.split(line[m.end():], 1)[0]):
            if flag not in flags:
                yield "flag", flag


def check_root(root, live, flags, consumer=False):
    """Scan one checkout. Returns a list of (rel, lineno, kind, name, line)."""
    bad = []
    for rel, path in candidate_files(root, consumer):
        try:
            text = io.open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        for n, line in enumerate(text.split("\n"), 1):
            for kind, name in scan_line(line, live, flags):
                bad.append((rel, n, kind, name, line.strip()[:90]))
    return bad


def main(argv=None):
    """Scan the instruction files for a verb or flag the engine no longer has, and
    return an exit code — non-zero when one is named.

    Positional arguments are EXTRA consumer roots. They are read against THIS
    repo's live surface on purpose: a consumer's instructions are wrong the moment
    the engine they will re-vendor stops accepting what they say to type, not the
    moment the consumer notices.
    """
    extra = list(argv if argv is not None else sys.argv[1:])
    live, flags = live_verbs(), live_flags()
    bad = [(ROOT, r) for r in check_root(ROOT, live, flags)]
    for root in extra:
        if not os.path.isdir(root):
            print("no such root: %s" % root, file=sys.stderr)
            return 2
        bad += [(root, r) for r in check_root(root, live, flags, consumer=True)]
    scanned = "this repo" if not extra else "this repo + %d consumer root(s)" % len(extra)
    if not bad:
        print("OK  no instruction names a retired verb or flag — %s (%d live verb(s): %s)"
              % (scanned, len(live), ", ".join(sorted(live))))
        return 0
    print("FAIL  %d instruction(s) name something the engine no longer has:" % len(bad))
    for root, (rel, n, kind, name, line) in bad:
        where = rel if root == ROOT else "%s/%s" % (os.path.basename(root.rstrip("/")), rel)
        print("  %s:%d  %s `%s`  %s" % (where, n, kind, name, line))
    print("")
    print("Either the name came back, or the instruction is stale. A reader who")
    print("follows one of these lines gets an unknown-command error.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
