#!/usr/bin/env python3
"""reqmap — requirement manager engine (stdlib only).

Subcommands:
  new AREA-NAME-NNN   scaffold a requirement from templates/requirement.md
  scan              list code members (implements/generated-from/... tags) per capability
  check             the gate: link sync + drift; exit non-zero on error (use in pre-commit/CI)
  map               generate requirements/_map.html (navigable graph)
  extract           draft requirements from legacy code (status: draft, risk-scored)

Layout on disk (relative to repo root, override with --root / --reqs / --code):
  requirements/*.md     the source of truth (markdown + YAML-ish frontmatter)
  <code>/**            scanned for tags like:  # implements: <ID>
"""
import argparse, fnmatch, hashlib, json, os, re, sys

ROLES = ("implements", "generated-from", "validated-against", "tested-by")
# the (?<![\w-]) left boundary stops substring matches like `reimplements:` or
# `x-implements:` from being picked up as a real `implements:` tag
TAG_RE = re.compile(r"(?<![\w-])(implements|generated-from|validated-against|tested-by)\s*:\s*([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)")
CODE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx", ".c", ".cpp", ".h", ".hpp",
             ".cc", ".java", ".go", ".rs", ".html", ".css", ".sql", ".yaml", ".yml")
VALID_STATUS = {"draft", "baseline", "in-progress", "implemented", "confirmed", "deprecated"}
VALID_LAYER = {"bus", "feature"}
ENFORCED = {"in-progress", "implemented", "confirmed"}

# Bumped on any change to this engine. `check` warns a seeded repo when its
# vendored copy is older than the installed plugin's. ISO date: lexicographic
# order == chronological order, so a plain string compare is enough.
MAP_ENGINE_VERSION = "2026-06-02"


# ---------- parsing ----------
def _as_list(v):  # implements: CORE-PARSE-001
    """Coerce a frontmatter value to a list: lists pass through, a bare scalar
    becomes a one-element list, empty/None becomes []. Guards callers that
    iterate list-valued keys (e.g. depends_on) against a string written without
    brackets being walked character-by-character."""
    if isinstance(v, list):
        return v
    return [v] if v else []


def parse_frontmatter(text):  # implements: CORE-PARSE-001
    """Return (meta_dict, body). Minimal YAML: scalars and inline [a, b] lists."""
    meta, body = {}, text.lstrip("﻿")  # tolerate a stray UTF-8 BOM
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            block = body[3:end]
            body = body[end + 4:].lstrip("\n")
            for line in block.splitlines():
                s = line.strip()
                if not s or s.startswith("#") or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                k, v = k.strip(), v.strip()
                if v.startswith("[") and "]" in v:
                    # keep only through the closing bracket; a '#' inside the
                    # list is data, a '#' after it is a trailing comment
                    inner = v[1:v.index("]")]
                    items = [x.split("#", 1)[0].strip().strip("\"'") for x in inner.split(",")]
                    meta[k] = [x for x in items if x]
                else:
                    v = v.split("#", 1)[0].rstrip()      # inline comment
                    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                        v = v[1:-1]                       # strip matching quotes
                    meta[k] = v
    return meta, body


def load_requirements(reqs_dir):  # implements: CORE-PARSE-001
    reqs = {}
    if not os.path.isdir(reqs_dir):
        return reqs
    for name in sorted(os.listdir(reqs_dir)):
        if not name.endswith(".md") or name.startswith("_"):
            continue
        path = os.path.join(reqs_dir, name)
        with open(path, encoding="utf-8-sig") as f:  # tolerate a UTF-8 BOM
            text = f.read()
        meta, body = parse_frontmatter(text)
        rid = meta.get("id") or os.path.splitext(name)[0]
        reqs[rid] = {"meta": meta, "body": body, "path": path}
    return reqs


def _prune_dirs(dirpath, dirs, reqs_dir):  # implements: CORE-SCAN-002
    """Drop noise dirs and the SSOT output dir from an os.walk in place.

    Excludes ONLY the actual requirements dir (by realpath), not every folder
    that happens to be named 'requirements' — a source package named
    requirements/ must still be scanned."""
    reqs_real = os.path.realpath(reqs_dir) if reqs_dir else None
    keep = []
    for d in dirs:
        if d in (".git", "node_modules", "__pycache__"):
            continue
        if reqs_real and os.path.realpath(os.path.join(dirpath, d)) == reqs_real:
            continue
        keep.append(d)
    dirs[:] = keep


def load_ignore(code_root):  # implements: CORE-SCAN-002
    """Read optional `.reqmapignore` at the scan root: fnmatch globs over POSIX
    rel paths, one per line, blanks and # comments skipped. Lets a repo exclude
    vendored tooling (e.g. its own copy of reqmap.py) from membership scanning so
    the engine's self-tags don't pollute the consumer's map. Fail-open: a missing
    or unreadable file yields no patterns (behavior identical to before)."""
    pats = []
    try:
        with open(os.path.join(code_root, ".reqmapignore"), encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    pats.append(s)
    except OSError:
        pass
    return pats


def scan_members(code_root, reqs_dir=None):  # implements: CORE-SCAN-002
    members = {}  # cap_id -> list[(role, file, line)]
    ignore = load_ignore(code_root)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir)
        for fn in files:
            if not fn.endswith(CODE_EXTS):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, code_root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                continue
            try:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        seen = set()
                        for role, cap in TAG_RE.findall(line):
                            key = (role, cap)
                            if key in seen:        # same tag twice on one line
                                continue
                            seen.add(key)
                            members.setdefault(cap, []).append((role, rel, i))
            except OSError:
                continue
    return members


# ---------- hashing / drift ----------
def binding_hash(body):  # implements: CORE-DRIFT-003
    """Hash only the semantically binding sections, not rationale/links."""
    keep, grab = [], False
    for line in body.splitlines():
        h = line.strip().lower()
        if h.startswith("## "):
            grab = any(s in h for s in ("input", "output", "acceptan"))
            continue
        if grab and line.strip():
            keep.append(line.strip())
    return hashlib.sha256("\n".join(keep).encode()).hexdigest()[:12]


def lock_path(reqs_dir):  # implements: CORE-DRIFT-003
    return os.path.join(reqs_dir, "_reqlock.json")


def load_lock(reqs_dir):  # implements: CORE-DRIFT-003
    p = lock_path(reqs_dir)
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}  # empty / corrupt / merge-conflicted lock: treat as no lock
    return {}


def save_lock(reqs_dir, lock):  # implements: CORE-DRIFT-003
    os.makedirs(reqs_dir, exist_ok=True)
    with open(lock_path(reqs_dir), "w", encoding="utf-8") as f:
        json.dump(lock, f, indent=2, sort_keys=True)


# ---------- commands ----------
def cmd_scan(reqs, members):  # implements: REQ-SCAN-005
    for cap in sorted(set(list(reqs) + list(members))):
        print(cap)
        for role, fp, ln in members.get(cap, []):
            print(f"    {role:18} {fp}:{ln}")
        if cap not in members:
            print("    (no members found)")


def _engine_version_at(path):
    """Best-effort MAP_ENGINE_VERSION parsed from a reqmap.py at `path`; None on any failure."""
    try:
        with open(path, encoding="utf-8") as f:
            m = re.search(r'MAP_ENGINE_VERSION\s*=\s*"([^"]+)"', f.read(4000))
        return m.group(1) if m else None
    except Exception:  # fail open — never let the staleness probe break the gate
        return None


def warn_if_stale():  # implements: REQ-CHECK-006
    """Print a non-fatal notice when this vendored copy is older than the installed
    plugin's. Silent in CI: only runs when CLAUDE_PLUGIN_ROOT is set. Never raises,
    never affects the exit code."""
    try:
        root = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not root:
            return
        plugin_ver = _engine_version_at(os.path.join(root, "scripts", "reqmap.py"))
        if plugin_ver and plugin_ver > MAP_ENGINE_VERSION:
            print(f"WARN  vendored reqmap.py is stale ({MAP_ENGINE_VERSION} < plugin "
                  f"{plugin_ver}) - re-seed: cp \"$CLAUDE_PLUGIN_ROOT/scripts/reqmap.py\" "
                  f"scripts/reqmap.py")
    except Exception:
        return


def cmd_check(reqs, members, reqs_dir, update_lock):  # implements: REQ-CHECK-006
    errors, warns = [], []
    warn_if_stale()
    cap_ids = set(reqs)

    for cap, hits in members.items():
        if cap not in cap_ids:
            errors.append(f"dangling tag: code references {cap} but no requirement exists")

    for rid, r in reqs.items():
        m = r["meta"]
        if m.get("status") not in VALID_STATUS:
            errors.append(f"{rid}: invalid status {m.get('status')!r}")
        if m.get("layer") not in VALID_LAYER:
            errors.append(f"{rid}: invalid layer {m.get('layer')!r}")
        for dep in _as_list(m.get("depends_on")):
            if dep not in cap_ids:
                errors.append(f"{rid}: depends_on missing {dep}")
        impls = [x for x in members.get(rid, []) if x[0] == "implements"]
        if m.get("status") in ENFORCED and not impls:
            errors.append(f"{rid}: status {m['status']} but no implements: tag found in code")
        tests = [x for x in members.get(rid, []) if x[0] == "tested-by"]
        if m.get("status") == "confirmed" and not tests:
            warns.append(f"{rid}: confirmed but no tested-by: tag — acceptance tests not linked")

    lock = load_lock(reqs_dir)
    new_lock = {}
    for rid, r in reqs.items():
        h = binding_hash(r["body"])
        new_lock[rid] = h
        old = lock.get(rid)
        if old and old != h and r["meta"].get("status") == "confirmed":
            warns.append(f"{rid}: DRIFT — contract changed since lock; re-check its members")

    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)

    if update_lock:
        save_lock(reqs_dir, new_lock)
        print("lock updated.")

    print(f"\n{len(reqs)} requirements, {sum(len(v) for v in members.values())} members, "
          f"{len(errors)} errors, {len(warns)} warnings.")
    return 1 if errors else 0


def cmd_new(reqs_dir, tmpl_path, cap_id):  # implements: REQ-NEW-004
    dest = os.path.join(reqs_dir, cap_id + ".md")
    if os.path.exists(dest):
        print(f"exists: {dest}"); return 1
    with open(tmpl_path, encoding="utf-8") as f:
        t = f.read().replace("AREA-NAME-NNN", cap_id)
    os.makedirs(reqs_dir, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(t)
    print(f"created {dest}")
    return 0


def _draft_id(rel):  # implements: REQ-EXTRACT-008
    """Mint a draft capability id from a file's relative path. Path-aware so
    same-basename files in different dirs don't collide; falls back to FILE when
    the name has no usable A-Z0-9 token (e.g. `_.py`, non-ASCII stems)."""
    slug = re.sub(r"[^A-Z0-9]+", "-", os.path.splitext(rel)[0].upper()).strip("-")
    return "DRAFT-" + (slug or "FILE")


def cmd_extract(reqs, members, code_root, reqs_dir):  # implements: REQ-EXTRACT-008
    """Propose DRAFT requirements for code files that have no member tag yet."""
    tagged = {fp for hits in members.values() for (_, fp, _) in hits}
    proposed, used = 0, set()
    os.makedirs(reqs_dir, exist_ok=True)
    for dirpath, dirs, files in os.walk(code_root):
        _prune_dirs(dirpath, dirs, reqs_dir)   # skip noise + the SSOT output dir
        dirs.sort()                            # deterministic id/suffix assignment
        for fn in sorted(files):
            if not fn.endswith((".py", ".js", ".ts", ".cpp", ".c")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), code_root).replace(os.sep, "/")
            if rel in tagged:
                continue
            cap = base = _draft_id(rel)
            k = 2
            while cap in used:                 # residual collision (case/ext only)
                cap = "{}-{}".format(base, k); k += 1
            used.add(cap)
            dest = os.path.join(reqs_dir, cap + ".md")
            if os.path.exists(dest):
                continue
            with open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore") as f:
                src = f.read()
            risk = _risk(src)
            review = "REVIEW" if risk >= 2 else "auto-baseline"
            with open(dest, "w", encoding="utf-8") as f:
                f.write(f"---\nid: {cap}\nstatus: draft\nlayer: feature\n"
                        f"owner: auto\ndepends_on: []\nrisk: {risk}  # {review}\n---\n\n"
                        f"# {os.path.splitext(fn)[0]}\n\n"
                        f"> DRAFT extracted from {rel}. Describes observed behavior, "
                        f"not validated intent.\n\n"
                        f"## Input\n- TODO\n\n## Description\n- TODO (why?)\n\n"
                        f"## Output\n- TODO\n\n## Acceptance (= tests)\n"
                        f"- characterization: current behavior captured, correctness UNVERIFIED\n")
            proposed += 1
            print(f"{review:14} {cap}  <- {rel}")
    print(f"\n{proposed} draft requirements proposed. Review the REVIEW ones before promoting.")
    return 0


def _risk(src):  # implements: REQ-EXTRACT-008
    score = 0
    if re.search(r"\b(TODO|FIXME|HACK|XXX)\b", src): score += 1
    if "# noqa" in src or "eslint-disable" in src: score += 1
    if len(src.splitlines()) > 300: score += 1
    return score


# ---------- map (HTML) ----------
def cmd_map(reqs, members, reqs_dir):  # implements: REQ-MAP-007
    used_by = {rid: [] for rid in reqs}
    for rid, r in reqs.items():
        for dep in _as_list(r["meta"].get("depends_on")):
            if dep in used_by:
                used_by[dep].append(rid)
    data = {"nodes": [], "edges": []}
    for rid, r in reqs.items():
        m = r["meta"]
        data["nodes"].append({
            "id": rid, "layer": m.get("layer", "feature"),
            "status": m.get("status", "draft"),
            "title": _title(r["body"]),
            "intent": _first_quote(r["body"]),
            "input": _section(r["body"], "input"),
            "output": _section(r["body"], "output"),
            "desc": _section(r["body"], "description"),
            "acc": _bullets(r["body"], "acceptan"),
            "deps": _as_list(m.get("depends_on")),
            "used_by": used_by.get(rid, []),
            "members": [{"role": x[0], "loc": f"{x[1]}:{x[2]}"} for x in members.get(rid, [])],
        })
    for rid, r in reqs.items():
        for dep in _as_list(r["meta"].get("depends_on")):
            data["edges"].append([rid, dep])
    html_out = render_html(data, reqs_dir)
    md_out   = render_md(data, reqs_dir)
    print("wrote {}".format(html_out))
    print("wrote {}".format(md_out))
    print("({} nodes, {} edges)".format(len(data["nodes"]), len(data["edges"])))
    return 0


def _title(body):  # implements: REQ-MAP-007
    """The human title from the requirement's first `# ` heading."""
    for line in body.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:].strip()
    return ""


def _first_quote(body):  # implements: REQ-MAP-007
    for line in body.splitlines():
        if line.strip().startswith(">"):
            return line.strip()[1:].strip()
    return ""


def _section(body, name):  # implements: REQ-MAP-007
    out, grab = [], False
    for line in body.splitlines():
        h = line.strip().lower()
        if h.startswith("## "):
            grab = name in h
            continue
        if grab and line.strip() and not line.strip().startswith("<!--"):
            out.append(line.strip().lstrip("- "))
    return " ".join(out)


def _bullets(body, name):  # implements: REQ-MAP-007
    out, grab = [], False
    for line in body.splitlines():
        h = line.strip().lower()
        if h.startswith("## "):
            grab = name in h
            continue
        if grab and line.strip().startswith("-"):
            out.append(line.strip()[1:].strip())
    return out


# ---------- mermaid generators ----------
def _safe_id(rid):
    """Mermaid-safe node ID: replace non-alphanumeric chars with underscores."""
    return re.sub(r"[^A-Za-z0-9]", "_", rid)


def _mlabel(text):
    """Make free text safe inside a quoted Mermaid node label.

    Even inside quotes, Mermaid's parser chokes on backticks, brackets,
    braces, pipes and backslashes; under securityLevel:loose, angle
    brackets would also be rendered as HTML. Neutralize all of them.
    """
    text = text or "—"
    for a, b in (('"', "'"), ("`", "'"), ("[", "("), ("]", ")"),
                 ("{", "("), ("}", ")"), ("|", "/"), ("\\", "/"),
                 ("<", "‹"), (">", "›")):
        text = text.replace(a, b)
    return text


def _node_label(n):
    """Two-line node label: human title big, capability id small below.

    The `<br>`/`<small>` tags are added outside `_mlabel` (which would
    otherwise neutralize the angle brackets); only the title text is
    passed through the sanitizer.
    """
    title = _mlabel(n.get("title") or n["id"])
    return "{}<br><small>{}</small>".format(title, _mlabel(n["id"]))


def _mermaid_system(data):  # implements: REQ-MAP-007
    lines = ["graph TD"]
    feats = [n for n in data["nodes"] if n["layer"] != "bus"]
    bus   = [n for n in data["nodes"] if n["layer"] == "bus"]
    if feats:
        lines.append("  subgraph Features")
        for n in feats:
            lines.append('    {}["{}"]'.format(_safe_id(n["id"]), _node_label(n)))
        lines.append("  end")
    if bus:
        lines.append("  subgraph Bus")
        for n in bus:
            lines.append('    {}["{}"]'.format(_safe_id(n["id"]), _node_label(n)))
        lines.append("  end")
    for a, b in data["edges"]:
        lines.append("  {} --> {}".format(_safe_id(a), _safe_id(b)))
    return "\n".join(lines)


def _mermaid_deps(data):  # implements: REQ-MAP-007
    lines = ["graph TD"]
    byid = {n["id"]: n for n in data["nodes"]}
    seen = set()
    for a, b in data["edges"]:
        for rid in (a, b):
            if rid not in seen:
                label = _node_label(byid[rid]) if rid in byid else rid
                lines.append('  {}["{}"]'.format(_safe_id(rid), label))
                seen.add(rid)
        lines.append("  {} --> {}".format(_safe_id(a), _safe_id(b)))
    if not data["edges"]:
        lines.append('  none["(no dependencies defined)"]')
    return "\n".join(lines)


def _mermaid_req_to_code(data):  # implements: REQ-MAP-007
    lines = ["graph LR"]
    for n in data["nodes"]:
        rid = n["id"]
        sid = _safe_id(rid)
        lines.append('  {}["{}"]'.format(sid, _node_label(n)))
        if not n["members"]:
            lines.append("  style {} fill:#fee,stroke:#c66".format(sid))
            continue
        # group by role+file, compute min/max line numbers
        groups = {}
        for m in n["members"]:
            c = m["loc"].rfind(":")
            f, ln = m["loc"][:c], int(m["loc"][c + 1:])
            k = m["role"] + "|" + f
            if k not in groups:
                groups[k] = {"role": m["role"], "f": f, "min": ln, "max": ln}
            else:
                groups[k]["min"] = min(groups[k]["min"], ln)
                groups[k]["max"] = max(groups[k]["max"], ln)
        for g in groups.values():
            loc = "{}:{}".format(g["f"], g["min"]) if g["min"] == g["max"] \
                  else "{}:{}-{}".format(g["f"], g["min"], g["max"])
            file_sid = "f_" + re.sub(r"[^A-Za-z0-9]", "_", loc)
            lines.append('  {}["{}"]'.format(file_sid, _mlabel(loc)))
            lines.append("  {} -->|{}| {}".format(sid, g["role"], file_sid))
    return "\n".join(lines)


def _mermaid_behavioral(data):  # implements: REQ-MAP-007
    lines = ["flowchart LR"]
    for n in data["nodes"]:
        sid  = _safe_id(n["id"])
        inp  = _mlabel(n["input"])[:50]
        out  = _mlabel(n["output"])[:50]
        in_id  = "in_"  + sid
        out_id = "out_" + sid
        lines.append('  {}(["{}"])'.format(in_id,  inp))
        lines.append('  {}["{}"]'.format(sid, _node_label(n)))
        lines.append('  {}(["{}"])'.format(out_id, out))
        lines.append("  {} --> {} --> {}".format(in_id, sid, out_id))
    return "\n".join(lines)


def _risk_signals(node, dependents_count):
    signals = []
    if node["status"] == "confirmed" and not node["members"]:
        signals.append("unimplemented")
    if node["status"] in ("draft", "baseline"):
        signals.append("unreviewed")
    if dependents_count >= 3:
        signals.append("blast-radius")
    return signals


def _mermaid_risk(data):  # implements: REQ-MAP-007
    dep_count = {n["id"]: 0 for n in data["nodes"]}
    for _, b in data["edges"]:
        dep_count[b] = dep_count.get(b, 0) + 1

    risky = []
    for n in data["nodes"]:
        sigs = _risk_signals(n, dep_count.get(n["id"], 0))
        if sigs:
            risky.append((n, sigs))

    lines = ["graph TD"]
    if not risky:
        lines.append('  ok["No risk signals detected"]')
        return "\n".join(lines)

    risky_ids = {n["id"] for n, _ in risky}
    for n, sigs in risky:
        sid   = _safe_id(n["id"])
        label = _node_label(n) + "<br>" + ", ".join(sigs)
        lines.append('  {}["{}"]'.format(sid, label))
        if "unimplemented" in sigs:
            lines.append("  style {} fill:#fee,stroke:#c00,color:#900".format(sid))
        elif "unreviewed" in sigs:
            lines.append("  style {} fill:#fff3cd,stroke:#a66,color:#630".format(sid))
        else:
            lines.append("  style {} fill:#fff9c4,stroke:#aa0,color:#550".format(sid))

    for a, b in data["edges"]:
        if a in risky_ids or b in risky_ids:
            lines.append("  {} --> {}".format(_safe_id(a), _safe_id(b)))

    return "\n".join(lines)


def _add_clicks(diagram, data):
    """Append Mermaid click statements for every requirement node."""
    clicks = "\n".join(
        "  click {} sel_{}".format(_safe_id(n["id"]), _safe_id(n["id"]))
        for n in data["nodes"]
    )
    return diagram + "\n" + clicks


def render_md(data, reqs_dir):  # implements: REQ-MAP-007
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    dep_count = {n["id"]: 0 for n in data["nodes"]}
    for _, b in data["edges"]:
        dep_count[b] = dep_count.get(b, 0) + 1

    diagrams = [
        ("System Map",          _mermaid_system(data)),
        ("Requirement-to-Code", _mermaid_req_to_code(data)),
        ("Behavioral Flow",     _mermaid_behavioral(data)),
        ("Dependency Map",      _mermaid_deps(data)),
        ("Risk & Unknowns",     _mermaid_risk(data)),
    ]

    lines = [
        "---",
        "generated: {}".format(ts),
        "nodes: {}".format(len(data["nodes"])),
        "edges: {}".format(len(data["edges"])),
        "---",
        "",
        "# Requirement Map",
        "",
    ]
    for title, diagram in diagrams:
        lines += ["## {}".format(title), "", "```mermaid", diagram, "```", ""]

    # risk table
    risk_rows = []
    for n in data["nodes"]:
        sigs = _risk_signals(n, dep_count.get(n["id"], 0))
        if sigs:
            risk_rows.append((n["id"], n["status"],
                              len(n["members"]), dep_count.get(n["id"], 0),
                              ", ".join(sigs)))
    if risk_rows:
        lines += [
            "### Risk Table", "",
            "| ID | status | members | dependents | risks |",
            "| --- | --- | --- | --- | --- |",
        ]
        for row in risk_rows:
            lines.append("| {} | {} | {} | {} | {} |".format(*row))
        lines.append("")

    out = os.path.join(reqs_dir, "_map.md")
    os.makedirs(reqs_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out


MAP_HTML_TEMPLATE = r"""<!doctype html><meta charset=utf-8><title>Requirement map</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
:root{--bg:#fff;--fg:#1a1a18;--mut:#73726c;--sur:#f4f2ec;--bor:#d8d6cc;--acc:#534ab7;--ok:#3b6d11;--wip:#854f0b}
@media(prefers-color-scheme:dark){:root{--bg:#1f1e1c;--fg:#e9e7df;--mut:#9c9a92;--sur:#2a2926;--bor:#3a3935;--acc:#afa9ec;--ok:#97c459;--wip:#fac775}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif;padding:24px}
h1{font-size:18px;font-weight:500;margin:0 0 12px}
.tabs{display:flex;gap:6px;margin-bottom:16px;flex-wrap:wrap}
.tab{padding:6px 14px;cursor:pointer;border-radius:6px;border:1px solid var(--bor);background:var(--sur);color:var(--fg);font:14px system-ui,sans-serif}
.tab.active{background:var(--acc);color:#fff;border-color:var(--acc)}
.pane{display:none}.pane.active{display:block}
.mwrap{position:relative}
.mermaid{background:var(--sur);border-radius:8px;height:72vh;overflow:hidden;cursor:grab;touch-action:none}
.mermaid:active{cursor:grabbing}
.mermaid svg{transform-origin:0 0}
.mctrl{position:absolute;top:10px;right:10px;display:flex;gap:4px;z-index:5}
.mctrl button{width:30px;height:30px;border:1px solid var(--bor);background:var(--bg);color:var(--fg);border-radius:6px;cursor:pointer;font:16px/1 system-ui;opacity:.85}
.mctrl button:hover{opacity:1;border-color:var(--acc)}
.mhint{position:absolute;bottom:8px;left:12px;font-size:11px;color:var(--mut);pointer-events:none}
#p{margin-top:16px;border:1px solid var(--bor);border-radius:12px;padding:16px 20px;background:var(--bg)}
#p h2{font-size:16px;margin:0 0 4px}.mono{font-family:ui-monospace,monospace;font-size:12px;color:var(--mut)}
.pill{font-size:12px;padding:2px 10px;border-radius:8px;background:var(--sur);color:var(--mut);margin-left:6px}
.io{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0}
.io div{background:var(--sur);border-radius:8px;padding:10px}.io .k{font-size:12px;color:var(--mut)}
ul{margin:4px 0;padding-left:18px}.k{font-size:12px;color:var(--mut)}
.lbl{font-size:11px;font-weight:600;color:var(--acc);text-transform:uppercase;letter-spacing:.05em;margin-top:10px}
</style>
<h1>Requirement map</h1>
<div class="tabs">REQMAP_TABS</div>
REQMAP_PANES
<div id="p"><p style="color:var(--mut);font-style:italic">Click a node in any diagram to see details.</p></div>
<script>
mermaid.initialize({startOnLoad:false,securityLevel:'loose',theme:'neutral'});
const rendered=new Set();
function switchTab(i){
  document.querySelectorAll('.tab,.pane').forEach(e=>e.classList.remove('active'));
  document.querySelector('[data-tab="'+i+'"]').classList.add('active');
  const pane=document.getElementById('pane'+i);
  pane.classList.add('active');
  if(!rendered.has(i)){
    rendered.add(i);
    mermaid.run({nodes:pane.querySelectorAll('.mermaid')})
      .then(()=>pane.querySelectorAll('.mermaid').forEach(initPanZoom))
      .catch(()=>{rendered.delete(i);pane.querySelectorAll('.mermaid').forEach(mapFallback);});
  }
}
function paneBox(i){return document.getElementById('pane'+i).querySelector('.mermaid');}
// render failed (CDN blocked / parse error / no svg): restore a scrollable pane so content isn't silently clipped
function mapFallback(box){box.style.overflow='auto';box.style.cursor='default';}
function initPanZoom(box){
  const svg=box.querySelector('svg');if(!svg){mapFallback(box);return;}if(box._pz)return;
  svg.style.maxWidth='none';
  const st={s:1,x:0,y:0};box._pz=st;
  const apply=()=>{svg.style.transform='translate('+st.x+'px,'+st.y+'px) scale('+st.s+')';};
  box.addEventListener('wheel',e=>{
    e.preventDefault();
    const r=box.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
    const ns=Math.min(8,Math.max(.15,st.s*(e.deltaY<0?1.1:1/1.1)));
    st.x=mx-(mx-st.x)*(ns/st.s);st.y=my-(my-st.y)*(ns/st.s);st.s=ns;apply();
  },{passive:false});
  let drag=false,lx=0,ly=0,moved=0;
  box.addEventListener('pointerdown',e=>{drag=true;moved=0;lx=e.clientX;ly=e.clientY;});
  window.addEventListener('pointermove',e=>{if(!drag)return;const dx=e.clientX-lx,dy=e.clientY-ly;moved+=Math.abs(dx)+Math.abs(dy);st.x+=dx;st.y+=dy;lx=e.clientX;ly=e.clientY;apply();});
  window.addEventListener('pointerup',()=>{drag=false;});
  // suppress node-click only when an actual drag happened
  box.addEventListener('click',e=>{if(moved>4){e.stopPropagation();e.preventDefault();}},true);
  box._apply=apply;
}
function pz(i,f){const b=paneBox(i),st=b._pz;if(!st)return;const r=b.getBoundingClientRect(),cx=r.width/2,cy=r.height/2;const ns=Math.min(8,Math.max(.15,st.s*f));st.x=cx-(cx-st.x)*(ns/st.s);st.y=cy-(cy-st.y)*(ns/st.s);st.s=ns;b._apply();}
function pzReset(i){const b=paneBox(i),st=b._pz;if(!st)return;st.s=1;st.x=0;st.y=0;b._apply();}
const D=REQMAP_DATA;
const byId=Object.fromEntries(D.nodes.map(n=>[n.id,n]));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function sel(id){
  const n=byId[id];if(!n)return;
  const li=a=>a.map(x=>'<li>'+esc(x)+'</li>').join('');
  const mem=n.members.length?(()=>{const g={};n.members.forEach(m=>{const c=m.loc.lastIndexOf(':');const f=m.loc.slice(0,c),l=+m.loc.slice(c+1);const k=m.role+'|'+f;if(!g[k])g[k]={role:m.role,f,min:l,max:l};else{g[k].min=Math.min(g[k].min,l);g[k].max=Math.max(g[k].max,l)}});return Object.values(g).map(e=>`<div class=mono>${esc(e.role)}: ${esc(e.f)}:${e.min===e.max?e.min:e.min+'-'+e.max}</div>`).join('')})():'<div class=k>(no members found)</div>';
  const sc=n.status==='confirmed'?'var(--ok)':n.status==='in-progress'?'var(--wip)':'var(--mut)';
  document.getElementById('p').innerHTML=`
    <h2>${esc(n.id)} <span class=pill style="color:${sc}">${esc(n.status)}</span><span class=pill>${esc(n.layer)}</span></h2>
    <div class=lbl>WHY</div><p style="margin:2px 0 8px;font-style:italic">${esc(n.intent)||'—'}</p>
    <div class=lbl>WHAT</div>
    <div class=io><div><div class=k>Input</div>${esc(n.input)||'—'}</div><div><div class=k>Output</div>${esc(n.output)||'—'}</div></div>
    <div class=k>Description</div><p style="margin:2px 0 10px">${esc(n.desc)||'—'}</p>
    <div class=lbl>HOW</div><div class=k>Acceptance (= tests)</div><ul>${li(n.acc)}</ul>
    <div class=lbl>WHERE</div><div class=k>Members in code</div>${mem}
    <div class=k style="margin-top:8px">Depends on</div><div class=mono>${esc(n.deps.join(' · '))||'— (bus)'}</div>
    <div class=k>Used by</div><div class=mono>${esc(n.used_by.join(' · '))||'—'}</div>`;
}
REQMAP_CALLBACKS
switchTab(0);
</script>"""


def render_html(data, reqs_dir):  # implements: REQ-MAP-007
    diagrams = [
        ("System Map",      _add_clicks(_mermaid_system(data),        data)),
        ("Req→Code",   _add_clicks(_mermaid_req_to_code(data),   data)),
        ("Behavioral Flow", _add_clicks(_mermaid_behavioral(data),    data)),
        ("Dependencies",    _add_clicks(_mermaid_deps(data),          data)),
        ("Risk",            _add_clicks(_mermaid_risk(data),          data)),
    ]

    tab_btns = "".join(
        '<button class="tab{}" data-tab="{}" onclick="switchTab({})">{}</button>'.format(
            " active" if i == 0 else "", i, i, title)
        for i, (title, _) in enumerate(diagrams)
    )

    panes = "".join(
        ('<div id="pane{0}" class="pane{1}"><div class="mwrap">'
         '<div class="mctrl"><button onclick="pz({0},1.25)">+</button>'
         '<button onclick="pz({0},0.8)">−</button>'
         '<button onclick="pzReset({0})" title="reset">↺</button></div>'
         '<div class="mermaid">{2}</div>'
         '<div class="mhint">scroll = zoom · drag = pan · ↺ = reset</div>'
         '</div></div>').format(i, " active" if i == 0 else "", diagram)
        for i, (_, diagram) in enumerate(diagrams)
    )

    callbacks = "\n".join(
        "window['sel_{}'] = function(){{sel('{}');}};".format(
            _safe_id(n["id"]), n["id"])
        for n in data["nodes"]
    )

    # Embed as JSON inside a <script>: escape < > & so a requirement title
    # containing "</script>" (or "<!--") cannot break out of the data block.
    # \uXXXX decodes back to the original char when the JSON is parsed.
    payload = (json.dumps(data)
               .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))

    html = MAP_HTML_TEMPLATE
    html = html.replace("REQMAP_DATA",      payload)
    html = html.replace("REQMAP_TABS",      tab_btns)
    html = html.replace("REQMAP_PANES",     panes)
    html = html.replace("REQMAP_CALLBACKS", callbacks)

    out = os.path.join(reqs_dir, "_map.html")
    os.makedirs(reqs_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


def main():
    ap = argparse.ArgumentParser(prog="reqmap")
    ap.add_argument("cmd", choices=["new", "scan", "check", "map", "extract"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--root", default=".")
    ap.add_argument("--reqs", default=None)
    ap.add_argument("--code", default=None)
    ap.add_argument("--update-lock", action="store_true")
    a = ap.parse_args()
    reqs_dir = a.reqs or os.path.join(a.root, "requirements")
    code_root = a.code or a.root
    here = os.path.dirname(os.path.abspath(__file__))
    tmpl = os.path.join(here, "..", "templates", "requirement.md")

    if a.cmd == "new":
        if not a.arg:
            print("usage: reqmap new AREA-NAME-NNN"); return 2
        return cmd_new(reqs_dir, tmpl, a.arg)

    reqs = load_requirements(reqs_dir)
    members = scan_members(code_root, reqs_dir)
    if a.cmd == "scan":
        cmd_scan(reqs, members); return 0
    if a.cmd == "check":
        return cmd_check(reqs, members, reqs_dir, a.update_lock)
    if a.cmd == "map":
        return cmd_map(reqs, members, reqs_dir)
    if a.cmd == "extract":
        return cmd_extract(reqs, members, code_root, reqs_dir)


if __name__ == "__main__":
    sys.exit(main() or 0)
