"""The registry graph: nodes + edges from the corpus and the scan, roadmap signals, TODO parsing,
cmd_map.
"""
import os, re

from .acceptance import _acc_blocks, _acc_items
from .author import _parse_todos_from_text
from .model import RISK_ADVICE, _area_of, _as_list
from .risk import _risk_signals
from .sections import ACCEPTANCE_LABELS, CONTRACT_LABELS, _from_any, _has_any
from .text import (
    _bullets, _context_group, _distinct_intent, _section, _section_raw, _title, _verify_bullets
)


# ---------- map (HTML) ----------
def _attach_ac_coverage(node, body, covered):
    # implements: ARCH-ACVERIFY-019  # implements: REQ-ACVERIFY-823
    """Add `clauses` / `covered` / `gap` to a node, but ONLY when the requirement has
    adopted per-AC tagging: it labels criteria AND at least one carries a `verifies:`
    tag. Absent means "not measured", and every reader must render it as such.

    The viewer used to invent the pair when it was absent — `clauses` from the number
    of CONTRACT lines, `covered` all-or-nothing from the tested-by badge — so a
    requirement with three real tests read "0 / 8 clauses covered" and sent its owner
    on an investigation. A number nobody computed is worse than no number."""
    labels = [b["label"] for b in _acc_blocks(body) if b["label"] and not b["manual"]]
    if not labels or not covered:
        return
    missing = [ac for ac in labels if ac not in covered]
    node["clauses"] = len(labels)
    node["covered"] = len(labels) - len(missing)
    if missing:
        node["gap"] = "no `verifies:` tag for " + ", ".join(missing)


def _build_map_data(reqs, members, ac_cover=None):
    # implements: ARCH-MAP-007  # implements: REQ-MAP-870  # implements: REQ-TRACE-935
    """Assemble the {nodes, edges} registry graph that drives every rendered
    surface (HTML map, Mermaid blocks, and the JSON export). Pure: no IO.

    `ac_cover` ({id: {AC-N: [...]}}, from `scan_ac_verifies`) is what turns the
    per-criterion coverage the gate already computes into something the viewer can
    render honestly; omitted, the coverage fields are simply absent."""
    used_by = {rid: [] for rid in reqs}
    for rid, r in reqs.items():
        for dep in _as_list(r["meta"].get("depends_on")):
            if dep in used_by:
                used_by[dep].append(rid)
    satisfied_by = {rid: [] for rid in reqs}  # reverse upstream edges  # implements: ARCH-TRACE-020
    for rid, r in reqs.items():
        for up in _as_list(r["meta"].get("satisfies")):
            if up in satisfied_by:
                satisfied_by[up].append(rid)
    data = {"nodes": [], "edges": [], "upstream_edges": []}
    for rid, r in reqs.items():
        m = r["meta"]
        _verify = _verify_bullets(r["body"])
        data["nodes"].append({
            "id": rid, "layer": m.get("layer", "feature"),
            "level": m.get("level"),                       # implements: ARCH-LEVEL-051
            "status": m.get("status", "draft"),
            "area": (m.get("area") or "").strip() or _area_of(rid),
            "title": _title(r["body"]),
            "intent": _distinct_intent(r["body"]),
            # new emission schema (Contract / Verify-intent / Notes / Current-impl)
            "contract": _from_any(_bullets, r["body"], CONTRACT_LABELS),
            "verify": _verify,
            # legacy per-topic heading first; ADR-0017's consolidated Context section
            # (bold **Notes**/**Current implementation** sub-groups) is the fallback,
            # never both at once in one file, so this never masks real content.
            "notes": _bullets(r["body"], "notes") or _context_group(r["body"], "notes"),
            "current_impl": (_bullets(r["body"], "current implementation")
                              or _context_group(r["body"], "current implementation")),
            "acc": _acc_items(r["body"]),                    # AC blocks AND bullets
            # raw, line breaks kept
            "accept": _from_any(_section_raw, r["body"], ACCEPTANCE_LABELS),
            # legacy schema (Input / Description / Output) — kept so old docs still render
            "input": _section(r["body"], "input"),
            "output": _section(r["body"], "output"),
            # Only the legacy Input/Description/Output triad, never the current
            # `## Description` — which is the Contract and is emitted above.
            "desc": (_section(r["body"], "description")
                     if _has_any(r["body"], ("input", "output")) else ""),
            # `deps` is the historical name and the one the vendored viewer reads
            # (`n.deps` in app/src/lib/loadData.js), so it stays. `depends_on` is the
            # same list under the name the frontmatter and every document use: a
            # consumer that asked for the documented name got a silent None and built
            # the wrong graph from it.
            "deps": _as_list(m.get("depends_on")),
            "depends_on": _as_list(m.get("depends_on")),
            "used_by": used_by.get(rid, []),
            "satisfies": _as_list(m.get("satisfies")),       # upstream needs this fulfils
            "satisfied_by": satisfied_by.get(rid, []),       # requirements fulfilling this need
            "members": [{"role": x[0], "loc": f"{x[1]}:{x[2]}"} for x in members.get(rid, [])],
            "test_exempt": m.get("test_exempt"),
            "milestone": m.get("milestone"),
            "priority": m.get("priority", ""),
            "risks": [{"signal": s, "advice": RISK_ADVICE[s]} for s in _risk_signals(
                {"status": m.get("status", "draft"), "layer": m.get("layer", "feature"),
                 "members": members.get(rid, []),
                 "verify": _verify, "test_exempt": m.get("test_exempt")})],
        })
        _attach_ac_coverage(data["nodes"][-1], r["body"], (ac_cover or {}).get(rid, {}))
    for rid, r in reqs.items():
        for dep in _as_list(r["meta"].get("depends_on")):
            if dep in reqs:                    # skip dangling targets — no phantom node
                data["edges"].append([rid, dep])
        for up in _as_list(r["meta"].get("satisfies")):  # implements: ARCH-TRACE-020
            if up in reqs:
                data["upstream_edges"].append([rid, up])
    return data


def _roadmap_signals(root):
    # implements: ARCH-ROADMAP-038  # implements: REQ-ROADMAP-907  # implements: REQ-ROADMAP-983
    """Read TODO.md and report two read-only roadmap signals, or None when the file
    is absent (most repos have no TODO.md, and they must see nothing).

    Returns {"newest_milestone": "vX.Y" or None, "unversioned_headings": [str]}.

    `unversioned_headings` is the one that bites. `_parse_todos_from_text` keeps the
    CURRENT milestone when a `## ` heading does not start with a version, so items
    under such a heading are silently attributed to the section above instead of being
    skipped. A cosmetic rename therefore mis-files entries with no visible error."""
    for base in dict.fromkeys([root, os.path.dirname(os.path.abspath(root))]):
        path = os.path.join(base, "TODO.md")
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            return None
        versions, bad = [], []
        for line in text.splitlines():
            s = line.strip()
            if not s.startswith("## "):
                continue
            m = re.match(r"^##\s+(v\d[\d.]*)\b", s)
            if m:
                versions.append(m.group(1))
            else:
                bad.append(s[3:].strip())
        newest = max(versions, key=_version_key) if versions else None
        # The newest milestone the roadmap marks SHIPPED (at least one `[x]` item).
        # The reverse-direction check reads this, never `newest`: an open item under a
        # future heading is a plan, and warning on a plan would fire on every roadmap
        # that looks ahead — which is every useful one.
        shipped = [t["milestone"] for t in _parse_todos_from_text(text)
                   if t["done"] and t["milestone"]]
        return {"newest_milestone": newest, "unversioned_headings": bad,
                "newest_shipped": max(shipped, key=_version_key) if shipped else None}
    return None


def _version_key(v):  # implements: ARCH-ROADMAP-038  # implements: REQ-ROADMAP-907
    """Sort key for a `vX.Y.Z` string: compare numerically per segment, so v2.10
    sorts above v2.9 where a string compare would not."""
    return tuple(int(p) for p in v.lstrip("v").split(".") if p.isdigit())


def _roadmap_behind(reqs, roadmap):
    # implements: ARCH-ROADMAP-038  # implements: REQ-ROADMAP-907  # implements: REQ-ROADMAP-983
    """(behind, newest_req, unmapped) — the highest `milestone:` any requirement
    declares, plus whether the roadmap and the corpus drifted apart, in EITHER direction.
    `behind`: TODO.md's newest heading trails the requirements. `unmapped`: the
    requirements trail the newest milestone TODO.md marks SHIPPED, so work that shipped
    carries no requirement and the roadmap chart ends before the product does — the
    direction that went unseen for six minors because only the first was checked. One
    comparison, read by `_audit_summary` and `cmd_health` so the two cannot disagree, and
    one line per direction — never one finding per milestone."""
    newest_req = max((m["milestone"] for m in (r["meta"] for r in reqs.values())
                      if m.get("milestone")), key=_version_key, default=None)
    behind = bool(roadmap["newest_milestone"] and newest_req and
                  _version_key(roadmap["newest_milestone"]) < _version_key(newest_req))
    shipped = roadmap.get("newest_shipped")
    unmapped = bool(shipped and newest_req and
                    _version_key(newest_req) < _version_key(shipped))
    return behind, newest_req, unmapped
