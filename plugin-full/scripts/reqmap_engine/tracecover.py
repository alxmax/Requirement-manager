"""The map's `trace` block: how much of the code the trace reaches, which test
probably proves a requirement that has none, what is wrong with the corpus
itself, and the repository's own design rules (ADR-0091).

Loaded by `sync` when it writes the map, never by the gate. Everything here is
read from what the scan already knows and is advisory: no lock, no verdict.
"""
# implements: ARCH-MAP-007
# implements: REQ-MAP-1144
import json
import os
import re

from . import config as cfg
from .candidates import _tested_stem
from .orphans import git_ignored
from .scan import _walk_code
from .sections import binding_hash, CONTRACT_LABELS, _from_any
from .tags import PROSE_EXTS, _is_test_path
from .text import _bullets

_MAX_LIST = 200
_MAX_HITS = 50
_NO_CODE = ("need", "aggregate")


def _code_files(code_root, reqs_dir):  # implements: REQ-MAP-1144
    """[(abs, rel, is_test)] for every program file the scanner reads, less
    what git ignores. Prose (`.md`, `.html`) is read for tags but is not code,
    and an ignored file exists on one checkout and not the next, so counting
    either would make the committed map depend on the machine that wrote it.
    The same set the coverage ratio skips; without git nothing is skipped."""
    ignored = git_ignored(code_root)
    return [(fp, rel, _is_test_path(rel, fp))
            for fp, rel in _walk_code(code_root, reqs_dir)
            if not rel.lower().endswith(PROSE_EXTS) and not rel.startswith(ignored)]


def _memberlock(reqs_dir):
    """The member lock's `members`, `{}` when it is absent or unreadable."""
    try:
        with open(os.path.join(reqs_dir, "_memberlock.json"), encoding="utf-8") as f:
            return json.load(f).get("members") or {}
    except (OSError, ValueError):
        return {}


def _memberlock_files(reqs_dir):
    """Files the member lock holds a hash for (a definition counts its file)."""
    return {key.split("#", 1)[0]
            for keys in _memberlock(reqs_dir).values() for key in keys or {}}


def _coverage(files, members, reqs_dir):  # implements: REQ-MAP-1144
    tagged = {fp for hits in members.values() for _r, fp, _l in hits}
    prod = [rel for _a, rel, test in files if not test]
    drift = _memberlock_files(reqs_dir)
    return {"code_files": len(files),
            "tagged_files": sum(1 for _a, rel, _t in files if rel in tagged),
            "production_files": len(prod),
            "drift_files": sum(1 for rel in prod if rel in drift)}


def _definition_names(memberlock_keys):
    return {k.split("#", 1)[1].split("(", 1)[0].split("::")[-1]
            for k in memberlock_keys if "#" in k}


def _read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read(256 * 1024)
    except OSError:
        return ""


def _suggestions(reqs, members, files, code_root, reqs_dir):
    # implements: REQ-MAP-1144
    """{rid: {tier, tests}} for each requirement held to code that has an
    `implements:` member and no `tested-by:` one. Tier A: a test file paired
    with its code by name names the requirement or one of its definitions.
    B: a test is paired by name only. C: no test is paired, a real gap."""
    lock = _memberlock(reqs_dir)
    tests_by_stem = {}
    for fp, rel, test in files:
        stem = _tested_stem(rel, code_root) if test else None
        if stem:
            tests_by_stem.setdefault(stem.lower(), []).append((fp, rel))
    out = {}
    for rid in sorted(reqs):
        meta = reqs[rid]["meta"]
        if (meta.get("status") == "deprecated" or meta.get("layer") in _NO_CODE
                or meta.get("test_exempt")):
            continue
        roles = {r for r, _f, _l in members.get(rid, ())}
        if "implements" not in roles or "tested-by" in roles:
            continue
        stems = {os.path.splitext(os.path.basename(f))[0].lower()
                 for r, f, _l in members[rid] if r == "implements"}
        cands = sorted({c for s in stems for c in tests_by_stem.get(s, ())},
                       key=lambda c: c[1])
        if not cands:
            out[rid] = {"tier": "C", "tests": []}
            continue
        names = _definition_names(lock.get(rid, {})) | {rid}
        named = [rel for fp, rel in cands
                 if any(re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])",
                                  _read(fp)) for n in names)]
        out[rid] = ({"tier": "A", "tests": named[:3]} if named else
                    {"tier": "B", "tests": [rel for _fp, rel in cands][:3]})
    return out


def _hygiene(reqs):  # implements: REQ-MAP-1144
    """Duplicates (the same binding text under two ids), confirmed entries
    with no clause, and structural entries (layer `aggregate` read from a
    source), for the corpus a person keeps."""
    by_hash, empty, structural = {}, [], []
    for rid in sorted(reqs):
        r = reqs[rid]
        meta = r["meta"]
        if meta.get("status") == "deprecated":
            continue
        clauses = _from_any(_bullets, r["body"], CONTRACT_LABELS)
        if meta.get("source") and meta.get("layer") == "aggregate":
            structural.append(rid)
        elif not clauses and meta.get("status") in ("confirmed", "implemented"):
            empty.append(rid)
        if clauses:
            by_hash.setdefault(binding_hash(r["body"]), []).append(rid)
    dups = [ids for ids in by_hash.values() if len(ids) > 1]
    return {"duplicates": dups[:_MAX_LIST], "title_only_confirmed": empty[:_MAX_LIST],
            "structural": len(structural)}


def _rules(files):  # implements: REQ-MAP-1144
    """Each `DESIGN_RULES` entry with its hits on production code, read with
    comments and literals blanked for C/C++; a bad entry is a problem."""
    out, problems = [], []
    for i, rule in enumerate(cfg.DESIGN_RULES or []):
        try:
            rid, rx = str(rule["id"]), re.compile(rule["pattern"])
        except (KeyError, TypeError, re.error) as e:
            problems.append("DESIGN_RULES[{}]: {}".format(i, e))
            continue
        exts = tuple(rule.get("exts") or ())
        hits = []
        for fp, rel, test in files:
            if test or (exts and not rel.lower().endswith(exts)):
                continue
            text = _read(fp)
            if rel.lower().endswith((".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh")):
                from .bracedefs import mask_c
                text = mask_c(text)
            for m in rx.finditer(text):
                hits.append({"file": rel, "line": text.count("\n", 0, m.start()) + 1})
        out.append({"id": rid, "why": str(rule.get("why", "")), "count": len(hits),
                    "hits": hits[:_MAX_HITS]})
    return out, problems


def trace_block(code_root, reqs_dir, reqs, members):  # implements: REQ-MAP-1144
    """What `sync` writes under `trace` in `_map.json`."""
    files = _code_files(code_root, reqs_dir)
    rules, problems = _rules(files)
    block = {"coverage": _coverage(files, members, reqs_dir),
             "suggestions": _suggestions(reqs, members, files, code_root, reqs_dir),
             "hygiene": _hygiene(reqs)}
    if rules or problems:
        block["rules"], block["problems"] = rules, problems
    return block
