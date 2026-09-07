"""`gate --implement`: the brief for writing a requirement's code."""
import json

from . import MAP_ENGINE_VERSION
from .acceptance import _acc_blocks
from .clarify import _clarify_questions
from .model import _as_list
from .sections import ACCEPTANCE_LABELS, CONTRACT_LABELS, _from_any
from .similar import _cosine, _sim_text, _sim_tokens, _tfidf
from .text import _bullets, _distinct_intent, _req_title, _section_raw


# ---------- implement: the brief a coding agent needs, and nothing more ----------
def _neighbours(reqs, members, rid, k=2):
    # implements: ARCH-IMPLEMENT-063  # implements: REQ-IMPLEMENT-959
    """The k requirements most similar to `rid` that already have code, by the same
    TF-IDF cosine `search` and `dupes` rank on. Similar prose almost always means
    neighbouring code, so this answers "where does this kind of thing live here?"
    without the engine knowing anything about the host project."""
    docs = {q: _sim_tokens(_sim_text(rr["body"])) for q, rr in reqs.items()}
    docs = {q: toks for q, toks in docs.items() if toks}
    if rid not in docs:
        return []
    vecs = _tfidf(docs)
    scored = []
    for other in docs:
        if other == rid or not members.get(other):
            continue
        scored.append((_cosine(vecs[rid], vecs[other]), other))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{"id": q, "score": round(s, 3),
             "files": sorted({fp for _role, fp, _ln in members.get(q, [])})}
            for s, q in scored[:k] if s > 0]


def _implement_brief(cap_id, r, reqs, members):
    # implements: ARCH-IMPLEMENT-063  # implements: REQ-IMPLEMENT-958
    """The JSON-able implementation brief for one requirement: obligations, cases,
    tags, neighbours and the verify command -- everything `cmd_implement` prints."""
    body, meta = r["body"], r["meta"]
    clauses = _from_any(_bullets, body, CONTRACT_LABELS)
    cases_raw = _from_any(_section_raw, body, ACCEPTANCE_LABELS) or ""
    labels = [b["label"] for b in _acc_blocks(body) if b.get("label")]
    mem = sorted(members.get(cap_id, []))
    questions = _clarify_questions(cap_id, r, reqs)
    return {
        "engine_version": MAP_ENGINE_VERSION,
        "id": cap_id,
        "title": _req_title(body, cap_id),
        "status": meta.get("status", "draft"),
        "level": meta.get("level", ""),
        "layer": meta.get("layer", "feature"),
        "intent": _distinct_intent(body),
        "contract": clauses,
        "cases": cases_raw,
        "case_labels": labels,
        "members": [{"role": role, "file": fp, "line": ln} for role, fp, ln in mem],
        "depends_on": _as_list(meta.get("depends_on")),
        "open_questions": questions,
        "neighbours": _neighbours(reqs, members, cap_id),
        "tags": {
            "implements": "# implements: {}".format(cap_id),
            "tested_by": "# tested-by: {}".format(cap_id),
            "verifies": ["# verifies: {}#{}".format(cap_id, lb) for lb in labels],
        },
        "verify": ["reqmap.py gate", "reqmap.py sync"],
        "contract_note": ("Write the code and the tests, carry the tags verbatim, then run "
                          "verify. Do not edit the requirement to match the code -- if the "
                          "contract is wrong, change it deliberately and run sync "
                          "--accept-drift."),
    }


def _print_implement_brief(brief):
    # implements: ARCH-IMPLEMENT-063  # implements: REQ-IMPLEMENT-958
    """Human-readable rendering of one implementation brief (the non-JSON path)."""
    cap_id = brief["id"]
    clauses, cases_raw = brief["contract"], brief["cases"]
    mem, labels = brief["members"], brief["case_labels"]
    blocking = [q for q in brief["open_questions"] if q["severity"] == "blocking"]
    print("{} · {} · {}".format(cap_id, brief["status"], brief["layer"]))
    print(brief["title"])
    if brief["intent"]:
        print("  " + brief["intent"])
    if blocking:
        print("\nBLOCKING — {} question(s) unanswered; implementing now guesses the contract:"
              .format(len(blocking)))
        for q in blocking:
            print("  - [{}] {}".format(q["rule"], q["question"]))
        print("  run: reqmap.py clarify {}".format(cap_id))
    print("\nObligations ({}):".format(len(clauses)))
    for i, c in enumerate(clauses, 1):
        print("  {}. {}".format(i, c))
    if cases_raw:
        print("\nCases:")
        for line in cases_raw.splitlines():
            print("  " + line)
    print("\nAlready implemented by ({}):".format(len(mem)))
    for m in mem:
        print("  {:12} {}:{}".format(m["role"], m["file"], m["line"]))
    if not mem:
        print("  (nothing yet — this is new code)")
    if brief["neighbours"]:
        print("\nSimilar requirements, for where this kind of code lives here:")
        for n in brief["neighbours"]:
            print("  {} ({:.2f})".format(n["id"], n["score"]))
            for f in n["files"][:6]:
                print("      " + f)
    print("\nTags the new code must carry:")
    print("  " + brief["tags"]["implements"] + "        (on the implementing file/function)")
    print("  " + brief["tags"]["tested_by"] + "         (on the test file)")
    for v in brief["tags"]["verifies"]:
        print("  " + v)
    if not labels:
        print("  (no labelled case — add CASE-N labels to get per-criterion coverage)")
    print("\nThen: reqmap.py gate   (and reqmap.py sync once it passes)")


def cmd_implement(ws, cap_id, as_json=False):
    # implements: ARCH-IMPLEMENT-063  # implements: REQ-IMPLEMENT-958
    """Emit the brief for implementing one requirement in code: its obligations, its
    cases, the tags the new code must carry, where similar code already lives, and the
    command that proves the work landed. The engine writes no code -- it states the
    contract and then verifies it, which is the only half a deterministic tool can own."""
    reqs, members = ws.reqs, ws.members
    r = reqs.get(cap_id)
    if not r:
        print("no requirement with id {} (expected requirements/{}.md)".format(cap_id, cap_id))
        return 1
    brief = _implement_brief(cap_id, r, reqs, members)
    if as_json:
        print(json.dumps(brief, indent=2, ensure_ascii=False))
        return 0
    _print_implement_brief(brief)
    return 0
