# Requirement Map v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `python reqmap.py map` generates both `requirements/_map.html` (5-tab interactive viewer, mermaid.js) and `requirements/_map.md` (5 Mermaid diagrams, GitHub-renderable).

**Architecture:** Add five Mermaid generator functions + `_safe_id` helper + `_add_clicks` helper. Add `render_md()` and `render_html()` to replace the old `MAP_HTML` constant. `cmd_map()` calls both renderers. The five generators produce pure Mermaid strings used by both outputs; `render_html` wraps them with click callbacks via `_add_clicks`.

**Tech Stack:** Python 3 stdlib only; mermaid.js 10.x via CDN (`cdn.jsdelivr.net`) in HTML output only.

---

## File Structure

| File | Change |
|------|--------|
| `scripts/reqmap.py` | Add 8 functions, replace `MAP_HTML` constant with `MAP_HTML_TEMPLATE` + `render_html()` |
| `requirements/REQ-MAP-007.md` | Update title, output section, acceptance criteria |
| `requirements/_map.html` | Regenerated (not hand-edited) |
| `requirements/_map.md` | New generated file |

---

## Task 1: Update REQ-MAP-007.md

**Files:**
- Modify: `requirements/REQ-MAP-007.md`

- [ ] **Step 1: Overwrite the file**

```markdown
---
id: REQ-MAP-007
status: confirmed
layer: feature
owner: alex
depends_on: [CORE-PARSE-001, CORE-SCAN-002]
superseded_by:
---

# Requirement map (HTML + MD)

> Render the whole registry as navigable diagrams a human can read at a glance.

## Input
- The loaded requirements and the discovered members.

## Description
Text listings do not show shape — which capabilities sit on the bus, what depends
on what, where the code lives. The map is a derived view (never a source of truth):
two output files are generated together:
- `_map.html`: multi-tab interactive viewer with mermaid.js and a clickable detail panel.
- `_map.md`: five Mermaid diagrams for GitHub/GitLab static rendering.

Both are regenerated, never edited, and live under `requirements/` so they travel
with the registry.

## Output
- `requirements/_map.html`: multi-tab HTML viewer with mermaid.js; clicking a node opens
  its WHY / WHAT / WHERE / HOW detail panel.
- `requirements/_map.md`: 5 Mermaid diagrams + YAML frontmatter with node/edge counts.

## Acceptance (= tests)
- The generated files contain one node per requirement and one edge per `depends_on`.
- `_map.md` contains exactly 5 Mermaid code blocks, one per view.
- `_map.html` has a tab bar with 5 tabs: System Map, Req→Code, Behavioral Flow, Dependencies, Risk.
- Behavioral Flow shows `Input([...]) --> REQ-ID[REQ-ID] --> Output([...])` for every requirement.
- Risk diagram shows only requirements with at least one risk signal (confirmed+0 members, draft/baseline, or 3+ dependents).
- A node with no members renders "(no members found)" in the HTML detail panel.

## Links
- Used by: (auto)
## Members in code (auto)
```

- [ ] **Step 2: Commit**

```bash
git add requirements/REQ-MAP-007.md
git commit -m "update REQ-MAP-007: dual output (HTML+MD), 5 diagram types, WHY/WHAT/WHERE/HOW panel"
```

---

## Task 2: Add `_safe_id()`, `_mermaid_system()`, `_mermaid_deps()`

**Files:**
- Modify: `scripts/reqmap.py` — insert after the `_bullets` function (line 286), before `MAP_HTML`

- [ ] **Step 1: Add `_safe_id()` after `_bullets`**

```python
# ---------- mermaid generators ----------
def _safe_id(rid):
    """Mermaid-safe node ID: replace non-alphanumeric chars with underscores."""
    return re.sub(r"[^A-Za-z0-9]", "_", rid)
```

- [ ] **Step 2: Add `_mermaid_system()` after `_safe_id`**

```python
def _mermaid_system(data):  # implements: REQ-MAP-007
    lines = ["graph TD"]
    feats = [n for n in data["nodes"] if n["layer"] != "bus"]
    bus   = [n for n in data["nodes"] if n["layer"] == "bus"]
    if feats:
        lines.append("  subgraph Features")
        for n in feats:
            lines.append('    {}["{}"]'.format(_safe_id(n["id"]), n["id"]))
        lines.append("  end")
    if bus:
        lines.append("  subgraph Bus")
        for n in bus:
            lines.append('    {}["{}"]'.format(_safe_id(n["id"]), n["id"]))
        lines.append("  end")
    for a, b in data["edges"]:
        lines.append("  {} --> {}".format(_safe_id(a), _safe_id(b)))
    return "\n".join(lines)
```

- [ ] **Step 3: Add `_mermaid_deps()` after `_mermaid_system`**

```python
def _mermaid_deps(data):  # implements: REQ-MAP-007
    lines = ["graph TD"]
    seen = set()
    for a, b in data["edges"]:
        for rid in (a, b):
            if rid not in seen:
                lines.append('  {}["{}"]'.format(_safe_id(rid), rid))
                seen.add(rid)
        lines.append("  {} --> {}".format(_safe_id(a), _safe_id(b)))
    if not data["edges"]:
        lines.append('  none["(no dependencies defined)"]')
    return "\n".join(lines)
```

- [ ] **Step 4: Verify no syntax errors**

```bash
python scripts/reqmap.py map
```
Expected: `wrote requirements/_map.html` and `wrote requirements/_map.md` — no crash.
(If `cmd_map` hasn't been updated yet, it still calls the old code — just confirm no import error.)

- [ ] **Step 5: Commit**

```bash
git add scripts/reqmap.py
git commit -m "add _safe_id, _mermaid_system, _mermaid_deps"
```

---

## Task 3: Add `_mermaid_req_to_code()`

**Files:**
- Modify: `scripts/reqmap.py` — insert after `_mermaid_deps`

- [ ] **Step 1: Add the function**

```python
def _mermaid_req_to_code(data):  # implements: REQ-MAP-007
    lines = ["graph LR"]
    for n in data["nodes"]:
        rid = n["id"]
        sid = _safe_id(rid)
        lines.append('  {}["{}"]'.format(sid, rid))
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
            lines.append('  {}["{}"]'.format(file_sid, loc))
            lines.append("  {} -->|{}| {}".format(sid, g["role"], file_sid))
    return "\n".join(lines)
```

- [ ] **Step 2: Verify no crash**

```bash
python -c "
import sys; sys.path.insert(0, '.')
from scripts.reqmap import _mermaid_req_to_code
print(_mermaid_req_to_code({'nodes': [{'id':'X-1','layer':'feature','members':[]}], 'edges': []})[:80])
"
```
Expected: prints `graph LR` followed by the node definition.

- [ ] **Step 3: Commit**

```bash
git add scripts/reqmap.py
git commit -m "add _mermaid_req_to_code"
```

---

## Task 4: Add `_mermaid_behavioral()`

**Files:**
- Modify: `scripts/reqmap.py` — insert after `_mermaid_req_to_code`

- [ ] **Step 1: Add the function**

```python
def _mermaid_behavioral(data):  # implements: REQ-MAP-007
    lines = ["flowchart LR"]
    for n in data["nodes"]:
        sid  = _safe_id(n["id"])
        inp  = (n["input"]  or "—")[:50].replace('"', "'")
        out  = (n["output"] or "—")[:50].replace('"', "'")
        in_id  = "in_"  + sid
        out_id = "out_" + sid
        lines.append('  {}(["{}"])'.format(in_id,  inp))
        lines.append('  {}["{}"]'.format(sid, n["id"]))
        lines.append('  {}(["{}"])'.format(out_id, out))
        lines.append("  {} --> {} --> {}".format(in_id, sid, out_id))
    return "\n".join(lines)
```

- [ ] **Step 2: Verify output shape**

```bash
python -c "
import sys; sys.path.insert(0, '.')
from scripts.reqmap import _mermaid_behavioral
d = {'nodes': [{'id':'CORE-PARSE-001','layer':'bus','input':'a file','output':'a dict','members':[]}], 'edges':[]}
print(_mermaid_behavioral(d))
"
```
Expected:
```
flowchart LR
  in_CORE_PARSE_001(["a file"])
  CORE_PARSE_001["CORE-PARSE-001"]
  out_CORE_PARSE_001(["a dict"])
  in_CORE_PARSE_001 --> CORE_PARSE_001 --> out_CORE_PARSE_001
```

- [ ] **Step 3: Commit**

```bash
git add scripts/reqmap.py
git commit -m "add _mermaid_behavioral"
```

---

## Task 5: Add `_risk_signals()` and `_mermaid_risk()`

**Files:**
- Modify: `scripts/reqmap.py` — insert after `_mermaid_behavioral`

- [ ] **Step 1: Add `_risk_signals()`**

```python
def _risk_signals(node, dependents_count):
    signals = []
    if node["status"] == "confirmed" and not node["members"]:
        signals.append("unimplemented")
    if node["status"] in ("draft", "baseline"):
        signals.append("unreviewed")
    if dependents_count >= 3:
        signals.append("blast-radius")
    return signals
```

- [ ] **Step 2: Add `_mermaid_risk()` after `_risk_signals`**

```python
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
        label = n["id"] + "\\n" + ", ".join(sigs)
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
```

- [ ] **Step 3: Verify risk signals work**

```bash
python -c "
import sys; sys.path.insert(0, '.')
from scripts.reqmap import _risk_signals
n_conf_no_members = {'id':'X','status':'confirmed','members':[]}
print(_risk_signals(n_conf_no_members, 0))   # ['unimplemented']
print(_risk_signals(n_conf_no_members, 3))   # ['unimplemented', 'blast-radius']
n_draft = {'id':'Y','status':'draft','members':[]}
print(_risk_signals(n_draft, 1))             # ['unreviewed']
"
```
Expected: three lines matching the comments.

- [ ] **Step 4: Commit**

```bash
git add scripts/reqmap.py
git commit -m "add _risk_signals, _mermaid_risk"
```

---

## Task 6: Add `_add_clicks()` and `render_md()`

**Files:**
- Modify: `scripts/reqmap.py` — insert after `_mermaid_risk`

- [ ] **Step 1: Add `_add_clicks()` helper**

```python
def _add_clicks(diagram, data):
    """Append Mermaid click statements for every requirement node."""
    clicks = "\n".join(
        "  click {} \"sel_{}\"".format(_safe_id(n["id"]), _safe_id(n["id"]))
        for n in data["nodes"]
    )
    return diagram + "\n" + clicks
```

- [ ] **Step 2: Add `render_md()`**

```python
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
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out
```

- [ ] **Step 3: Commit**

```bash
git add scripts/reqmap.py
git commit -m "add _add_clicks, render_md"
```

---

## Task 7: Replace `MAP_HTML` with `MAP_HTML_TEMPLATE` + `render_html()`

**Files:**
- Modify: `scripts/reqmap.py` — replace the `MAP_HTML = r"""..."""` block (lines 289–333) entirely

- [ ] **Step 1: Delete the `MAP_HTML` constant and add `MAP_HTML_TEMPLATE` in its place**

Replace the entire `MAP_HTML = r"""..."""` block with:

```python
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
.mermaid{background:var(--sur);border-radius:8px;padding:16px;overflow-x:auto}
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
  if(!rendered.has(i)){mermaid.run({nodes:pane.querySelectorAll('.mermaid')});rendered.add(i);}
}
switchTab(0);
const D=REQMAP_DATA;
const byId=Object.fromEntries(D.nodes.map(n=>[n.id,n]));
function sel(id){
  const n=byId[id];if(!n)return;
  const li=a=>a.map(x=>'<li>'+x+'</li>').join('');
  const mem=n.members.length?(()=>{const g={};n.members.forEach(m=>{const c=m.loc.lastIndexOf(':');const f=m.loc.slice(0,c),l=+m.loc.slice(c+1);const k=m.role+'|'+f;if(!g[k])g[k]={role:m.role,f,min:l,max:l};else{g[k].min=Math.min(g[k].min,l);g[k].max=Math.max(g[k].max,l)}});return Object.values(g).map(e=>`<div class=mono>${e.role}: ${e.f}:${e.min===e.max?e.min:e.min+'-'+e.max}</div>`).join('')})():'<div class=k>(no members found)</div>';
  const sc=n.status==='confirmed'?'var(--ok)':n.status==='in-progress'?'var(--wip)':'var(--mut)';
  document.getElementById('p').innerHTML=`
    <h2>${n.id} <span class=pill style="color:${sc}">${n.status}</span><span class=pill>${n.layer}</span></h2>
    <div class=lbl>WHY</div><p style="margin:2px 0 8px;font-style:italic">${n.intent||'—'}</p>
    <div class=lbl>WHAT</div>
    <div class=io><div><div class=k>Input</div>${n.input||'—'}</div><div><div class=k>Output</div>${n.output||'—'}</div></div>
    <div class=k>Description</div><p style="margin:2px 0 10px">${n.desc||'—'}</p>
    <div class=lbl>HOW</div><div class=k>Acceptance (= tests)</div><ul>${li(n.acc)}</ul>
    <div class=lbl>WHERE</div><div class=k>Members in code</div>${mem}
    <div class=k style="margin-top:8px">Depends on</div><div class=mono>${n.deps.join(' · ')||'— (bus)'}</div>
    <div class=k>Used by</div><div class=mono>${n.used_by.join(' · ')||'—'}</div>`;
}
REQMAP_CALLBACKS
</script>"""
```

- [ ] **Step 2: Add `render_html()` after `MAP_HTML_TEMPLATE`**

```python
def render_html(data, reqs_dir):  # implements: REQ-MAP-007
    diagrams = [
        ("System Map",      _add_clicks(_mermaid_system(data),        data)),
        ("Req→Code",   _add_clicks(_mermaid_req_to_code(data),   data)),
        ("Behavioral Flow", _add_clicks(_mermaid_behavioral(data),    data)),
        ("Dependencies",    _add_clicks(_mermaid_deps(data),          data)),
        ("Risk",            _add_clicks(_mermaid_risk(data),          data)),
    ]

    tab_btns = "".join(
        '<button class="tab{}" data-tab="{}" onclick="switchTab({}">{}</button>'.format(
            " active" if i == 0 else "", i, i, title)
        for i, (title, _) in enumerate(diagrams)
    )

    panes = "".join(
        '<div id="pane{}" class="pane{}"><div class="mermaid">{}</div></div>'.format(
            i, " active" if i == 0 else "", diagram)
        for i, (_, diagram) in enumerate(diagrams)
    )

    callbacks = "\n".join(
        "window['sel_{}'] = function(){{sel('{}');}};".format(
            _safe_id(n["id"]), n["id"])
        for n in data["nodes"]
    )

    html = MAP_HTML_TEMPLATE
    html = html.replace("REQMAP_DATA",      json.dumps(data))
    html = html.replace("REQMAP_TABS",      tab_btns)
    html = html.replace("REQMAP_PANES",     panes)
    html = html.replace("REQMAP_CALLBACKS", callbacks)

    out = os.path.join(reqs_dir, "_map.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out
```

- [ ] **Step 3: Verify import is clean**

```bash
python -c "import scripts.reqmap; print('ok')"
```
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add scripts/reqmap.py
git commit -m "replace MAP_HTML with MAP_HTML_TEMPLATE + render_html: 5-tab mermaid.js viewer"
```

---

## Task 8: Update `cmd_map()` + end-to-end verification

**Files:**
- Modify: `scripts/reqmap.py` — update `cmd_map` (around line 251)

- [ ] **Step 1: Replace the output block in `cmd_map`**

Find this block in `cmd_map`:
```python
    out = os.path.join(reqs_dir, "_map.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(MAP_HTML.replace("__DATA__", json.dumps(data)))
    print(f"wrote {out}  ({len(data['nodes'])} nodes, {len(data['edges'])} edges)")
    return 0
```

Replace with:
```python
    html_out = render_html(data, reqs_dir)
    md_out   = render_md(data, reqs_dir)
    print("wrote {}".format(html_out))
    print("wrote {}".format(md_out))
    print("({} nodes, {} edges)".format(len(data["nodes"]), len(data["edges"])))
    return 0
```

- [ ] **Step 2: Run the map command**

```bash
python scripts/reqmap.py map
```
Expected output:
```
wrote requirements/_map.html
wrote requirements/_map.md
(8 nodes, 9 edges)
```

- [ ] **Step 3: Verify `_map.md` structure**

```bash
python -c "
content = open('requirements/_map.md', encoding='utf-8').read()
blocks = content.count('` + '``' + `mermaid')
print('mermaid blocks:', blocks)          # must be 5
print('has frontmatter:', content.startswith('---'))
print('has risk table:', '### Risk Table' in content or 'No risk' in content)
"
```
Expected: `mermaid blocks: 5`, `has frontmatter: True`.

- [ ] **Step 4: Open `requirements/_map.html` in browser**

Open the file. Confirm:
- Tab bar shows: System Map | Req→Code | Behavioral Flow | Dependencies | Risk
- Clicking each tab renders a diagram (Mermaid loads from CDN)
- Clicking a node opens the detail panel with WHY / WHAT / HOW / WHERE sections

- [ ] **Step 5: Run the gate — confirm 0 errors**

```bash
python scripts/reqmap.py check
```
Expected: `0 errors, 0 warnings.`

- [ ] **Step 6: Stage and commit all outputs**

```bash
git add scripts/reqmap.py requirements/_map.html requirements/_map.md requirements/REQ-MAP-007.md
git commit -m "feat: requirement map v2 — 5 Mermaid diagrams, HTML tabs, _map.md output"
```

---

## Self-Review Checklist

| Spec requirement | Task |
|-----------------|------|
| `_map.md` with 5 Mermaid blocks | Task 6 (`render_md`) |
| `_map.html` with 5 tabs | Task 7 (`render_html`, `MAP_HTML_TEMPLATE`) |
| System Map: features/bus subgraphs | Task 2 (`_mermaid_system`) |
| Req→Code: req→file edges with role labels | Task 3 (`_mermaid_req_to_code`) |
| Behavioral Flow: Input→REQ-ID→Output | Task 4 (`_mermaid_behavioral`) |
| Dependency Map: only depends_on edges | Task 2 (`_mermaid_deps`) |
| Risk: 3 signals, table, filtered | Task 5+6 (`_risk_signals`, `_mermaid_risk`, `render_md`) |
| Node click → detail panel | Task 7 (sel() + REQMAP_CALLBACKS) |
| WHY/WHAT/WHERE/HOW labels in panel | Task 7 (sel() template) |
| mermaid.js CDN, securityLevel loose | Task 7 (MAP_HTML_TEMPLATE) |
| REQ-MAP-007 updated | Task 1 |
| `reqmap.py check` still passes | Task 8 Step 5 |
