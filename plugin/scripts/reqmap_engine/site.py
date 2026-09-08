"""`site`: engine-owned regions injected into a presentation page."""
import os, re

from . import MAP_ENGINE_VERSION
from .git import _git_remote_web_url, _git_root, _repo_name
from .mapdata import _build_map_data


# implements: ARCH-SITE-026  (commands/layers deferred to a follow-up)
SITE_REGIONS = ("nav", "stats")


def _region_markers(name):  # implements: ARCH-SITE-026
    key = name.upper()
    return "<!--##REQMAP:{}##-->".format(key), "<!--##/REQMAP:{}##-->".format(key)


def _inject_region(html, name, inner, anchor="<body>"):
    # implements: ARCH-SITE-026  # implements: REQ-SITE-924
    """Replace the content between the paired markers for `name` with `inner`
    (idempotent). Markers absent -> insert a fresh marked block right after the
    first `anchor`; anchor absent too -> append. Only the marked block is
    written; surrounding (authored) bytes are untouched."""
    open_m, close_m = _region_markers(name)
    block = open_m + "\n" + inner + "\n" + close_m
    # find the close that belongs to THIS open (search after it) so a stray close
    # before the open isn't mistaken for the region end, which would append a
    # duplicate block on re-run instead of rewriting in place
    i = html.find(open_m)
    j = html.find(close_m, i + len(open_m)) if i != -1 else -1
    if i != -1 and j != -1:
        return html[:i] + block + html[j + len(close_m):]
    # `<body class="...">` is still the body tag: a literal find appended the
    # block after `</html>` on any authored page whose body carries attributes
    m = (re.search(r"<body\b[^>]*>", html, re.I) if anchor == "<body>" else None)
    a = m.end() if m else html.find(anchor)
    if a != -1:
        a += 0 if m else len(anchor)
        return html[:a] + "\n" + block + html[a:]
    return html + "\n" + block


def _extract_region(html, name):  # implements: ARCH-SITE-026
    """Inner text between the paired markers for `name`, or None when absent.
    Lets the freshness gate diff only engine-owned regions (prose is exempt)."""
    open_m, close_m = _region_markers(name)
    i = html.find(open_m)
    if i == -1:
        return None
    i += len(open_m)
    j = html.find(close_m, i)
    return html[i:j].strip("\n") if j != -1 else None


def _html_escape(s):  # implements: ARCH-SITE-026
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _site_context_from_data(data, repo_url, map_ok, diagram_rel):  # implements: ARCH-SITE-026
    """Deterministic region inputs derived from the map graph + already-resolved
    link facts. No wall-clock, no filesystem here — callers resolve repo_url /
    map_ok / diagram_rel, so a re-run with no change reproduces byte-identically."""
    nodes = data.get("nodes", [])
    layers = {n.get("layer", "feature") for n in nodes}
    return {
        "repo_url": repo_url,
        "map_ok": map_ok,
        "diagram_rel": diagram_rel,
        "counts": {
            "requirements": len(nodes),
            "confirmed": sum(1 for n in nodes if n.get("status") == "confirmed"),
            "layers": len(layers),
            "edges": len(data.get("edges", [])),
        },
    }


def _render_region(name, ctx):  # implements: ARCH-SITE-026  # implements: REQ-SITE-924
    """Inner HTML for an engine-owned region. NAV: plain target=_blank anchors,
    each emitted only when its target resolves (graceful degradation). STATS:
    deterministic stat cards from the graph counts + engine version."""
    if name == "nav":
        links = []
        if ctx.get("map_ok"):
            links.append('<a href="map.html" target="_blank" rel="noopener">Live Map ↗</a>')
        if ctx.get("diagram_rel"):
            links.append('<a href="{}" target="_blank" rel="noopener">Diagram ↗</a>'
                         .format(_html_escape(ctx["diagram_rel"])))
        if ctx.get("repo_url"):
            links.append('<a href="{}" target="_blank" rel="noopener">GitHub ↗</a>'
                         .format(_html_escape(ctx["repo_url"])))
        return '<nav class="nav-links">' + "".join(links) + '</nav>'
    if name == "stats":
        c = ctx["counts"]
        cells = [("requirements", c["requirements"]), ("confirmed", c["confirmed"]),
                 ("layers", c["layers"]), ("edges", c["edges"]),
                 ("engine", MAP_ENGINE_VERSION)]
        items = "".join('<div class="stat"><b>{}</b><span>{}</span></div>'.format(v, k)
                        for k, v in cells)
        return items
    return ""


# A self-contained default presentation page written by `site` scaffold mode.
# Inline (not a vendored file) so the engine stays hermetic. NAV and STATS are
# marker-delimited engine-owned regions; everything else is authored prose the
# user/skill rewrites. This template is the canonical source (the prototype that
# seeded it has been removed).
# Callers fill %%REPO_NAME%% / %%REPO_URL%% via str.replace (NOT str.format —
# the CSS contains literal braces).
SITE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>%%REPO_NAME%% — project site</title>
<!--
  ============================================================================
  PROTOTYPE of `reqmap.py sync --attach` — HYBRID model.
    • Regions marked  <!##REQMAP:...##>  are regenerated by the engine on every
      run (nav links, stats band, commands grid, layer model) — never stale.
    • Everything else is AUTHORED prose, preserved across regenerations.
  Self-contained: no CDN, no network. Plain anchor links (no file:// iframes).
  Diagram is link-only (no builder coupling). Applies the Senate
  (2026-06-14, MODIFY) blocking conditions.
  ============================================================================
-->
<style>
  :root{
    --paper:#ECE9E1; --paper-2:#F4F2EC; --card:#FBFAF6;
    --ink:#1F1D1A; --muted:#6B655C; --line:#D9D4C8;
    --accent:#9A3B2E; --accent-2:#1F6F5C; --gate:#9A3B2E;
    --eng:#1F6F5C; --auth:#9A6700;
    --radius:12px; --maxw:980px;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0; background:var(--paper); color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    line-height:1.55; -webkit-font-smoothing:antialiased;
  }
  a{color:inherit}
  .wrap{max-width:var(--maxw); margin:0 auto; padding:0 24px}
  /* ============ <!##REQMAP:NAV##>  engine-owned top bar ============ */
  .nav{position:sticky; top:0; z-index:20; background:rgba(236,233,225,.86);
       backdrop-filter:saturate(140%) blur(8px); border-bottom:1px solid var(--line)}
  .nav-inner{max-width:var(--maxw); margin:0 auto; padding:12px 24px;
             display:flex; align-items:center; justify-content:space-between; gap:16px}
  .brand{display:flex; align-items:center; gap:10px; font-weight:700; letter-spacing:-.01em}
  .mark{width:26px; height:26px; border-radius:7px; background:var(--accent);
        display:grid; place-items:center; color:#fff; font-size:14px; font-weight:800}
  .nav-links{display:flex; gap:6px; align-items:center; flex-wrap:wrap}
  .nav-links a{display:inline-flex; align-items:center; gap:4px; text-decoration:none;
               color:var(--ink); font-size:.9rem; font-weight:600; padding:7px 12px;
               border-radius:8px; border:1px solid transparent}
  .nav-links a:hover{background:var(--card); border-color:var(--line); color:var(--accent)}
  .arrow{font-size:.8em; opacity:.7}
  /* legend chip explaining the hybrid coloring */
  .legend{display:flex; gap:14px; align-items:center; justify-content:center;
          font-size:.74rem; color:var(--muted); padding:8px; background:var(--paper-2);
          border-bottom:1px solid var(--line)}
  .dot{display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:5px; \
vertical-align:middle}
  .dot.eng{background:var(--eng)} .dot.auth{background:var(--auth)}
  /* region tag shown at the corner of engine/authored blocks */
  .tag{display:inline-block; font-size:.66rem; font-weight:700; letter-spacing:.04em;
       text-transform:uppercase; padding:.12rem .5rem; border-radius:999px}
  .tag.eng{color:var(--eng); background:#1F6F5C18; border:1px solid #1F6F5C40}
  .tag.auth{color:var(--auth); background:#9A670018; border:1px solid #9A670040}
  section{padding:56px 0; border-bottom:1px solid var(--line)}
  .eyebrow{font-size:.78rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; \
color:var(--accent); margin:0 0 10px}
  h1{font-size:clamp(2rem,5vw,3.2rem); line-height:1.05; letter-spacing:-.02em; margin:.2em 0 \
.3em; font-weight:800}
  h2{font-size:clamp(1.4rem,3vw,2rem); letter-spacing:-.01em; margin:0 0 .4em; font-weight:750}
  .lead{font-size:1.12rem; color:var(--muted); max-width:60ch}
  /* hero */
  .hero{padding:72px 0 60px; background:
        radial-gradient(60% 80% at 80% -10%, #9A3B2E14, transparent 60%), var(--paper)}
  .hero .cta{margin-top:26px; display:flex; gap:12px; flex-wrap:wrap}
  .btn{display:inline-flex; align-items:center; gap:6px; text-decoration:none; font-weight:650; \
font-size:.95rem;
       padding:.62rem 1.05rem; border-radius:9px}
  .btn.primary{background:var(--accent); color:#fff}
  .btn.primary:hover{filter:brightness(1.07)}
  .btn.ghost{background:var(--card); border:1px solid var(--line); color:var(--ink)}
  .btn.ghost:hover{border-color:var(--accent); color:var(--accent)}
  /* stats band — engine */
  .band{background:var(--paper-2)}
  .stats{display:grid; grid-template-columns:repeat(6,1fr); gap:14px; margin-top:8px}
  .stat{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); \
padding:16px 14px; text-align:center}
  .stat b{display:block; font-size:1.7rem; font-weight:800; letter-spacing:-.02em; color:var(--ink)}
  .stat span{font-size:.74rem; color:var(--muted); text-transform:uppercase; letter-spacing:.04em}
  .src{margin-top:14px; font-size:.78rem; color:var(--muted)}
  .src code{font-family:ui-monospace,Menlo,Consolas,monospace}
  /* pillars — authored */
  .pillars{display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:10px}
  .pill{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); \
padding:20px}
  .pill h3{margin:.1em 0 .35em; font-size:1.05rem}
  .pill p{margin:0; color:var(--muted); font-size:.92rem}
  /* commands grid — engine */
  .cmds{display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:10px}
  .cmd{background:var(--card); border:1px solid var(--line); border-radius:10px; padding:13px 14px}
  .cmd.gate{border-color:#9A3B2E66; box-shadow:0 0 0 1px #9A3B2E22 inset}
  .cmd code{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.85rem; font-weight:700; \
color:var(--accent)}
  .cmd p{margin:.35em 0 0; font-size:.82rem; color:var(--muted)}
  /* layers — engine/data */
  .layers{display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:10px}
  .layer{border-radius:var(--radius); padding:18px; border:1px solid var(--line); \
background:var(--card)}
  .layer .l{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.78rem; font-weight:700; \
margin-bottom:6px}
  .layer.bus .l{color:var(--accent)} .layer.feat .l{color:var(--accent-2)} .layer.need \
.l{color:#6b4ea8}
  .layer h3{margin:.1em 0 .3em; font-size:1rem}
  .layer p{margin:0 0 8px; font-size:.85rem; color:var(--muted)}
  .layer .ids{font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.72rem; \
color:var(--muted)}
  /* hybrid mechanism explainer */
  .mech pre{background:#1f1d1a; color:#e9e5db; border-radius:var(--radius); padding:18px 20px; \
overflow:auto; font-size:.82rem; line-height:1.5}
  .mech .c-eng{color:#7fd6bf} .mech .c-auth{color:#f0c674} .mech .c-dim{color:#9a948a}
  footer{padding:30px 0 60px; color:var(--muted); font-size:.82rem; text-align:center}
  footer code{font-family:ui-monospace,Menlo,Consolas,monospace}
  .secthead{display:flex; align-items:center; gap:10px; margin-bottom:4px}
  @media(max-width:760px){
    .stats{grid-template-columns:repeat(3,1fr)}
    .pillars,.cmds,.layers{grid-template-columns:1fr}
    .nav-links a{padding:6px 9px; font-size:.82rem}
  }
</style>
</head>
<body>
<div class="nav">
  <div class="nav-inner">
    <div class="brand"><span class="mark">R</span> %%REPO_NAME%%</div>
    <!--##REQMAP:NAV##--><!--##/REQMAP:NAV##-->
  </div>
</div>
<div class="legend">
  <span><span class="dot eng"></span>engine-generated (refreshed every run)</span>
  <span><span class="dot auth"></span>authored prose (preserved)</span>
</div>
<!-- HERO — authored -->
<header class="hero">
  <div class="wrap">
  <!-- author me -->
    <span class="tag auth">authored</span>
    <p class="eyebrow" style="margin-top:14px">Single source of truth</p>
    <h1>Keep your specs, code,<br>and intent in sync.</h1>
    <p class="lead">requirement-manager seeds one stdlib-only engine into any repo, then holds the \
line
      between what you <em>meant</em> to build and what the code actually does — a drift gate you \
run before
      every commit, a live map of every capability, and an answer to "where is this \
implemented?".</p>
    <div class="cta">
      <a class="btn primary" href="map.html" target="_blank" rel="noopener">Open the live map ↗</a>
      <a class="btn ghost" href="%%REPO_URL%%" target="_blank" rel="noopener">View on GitHub ↗</a>
    </div>
  </div>
</header>
<section class="band">
  <div class="wrap">
    <div class="secthead"><span class="tag eng">engine-generated</span></div>
    <p class="eyebrow">At a glance</p>
    <h2>The corpus, right now</h2>
    <div class="stats">
      <!--##REQMAP:STATS##--><!--##/REQMAP:STATS##-->
    </div>
    <p class="src">Auto-injected by <code>reqmap.py sync</code> from <code>_map.json</code> — \
re-computed on every run, so it never drifts.</p>
  </div>
</section>
<!-- PILLARS — authored -->
<section>
  <div class="wrap">
    <div class="secthead"><span class="tag auth">authored</span></div>
    <p class="eyebrow">Why it exists</p>
    <h2>Three jobs, one engine</h2>
    <div class="pillars">
      <div class="pill"><h3>Catch drift early</h3><p>Every code tag resolves to a real \
requirement; every confirmed requirement has code behind it. <code>gate</code> fails the build the \
moment intent and implementation diverge.</p></div>
      <div class="pill"><h3>Map the system</h3><p>One command renders the whole capability graph — \
system map, req→code, dependencies, risk — into a self-contained viewer you open by \
double-click.</p></div>
      <div class="pill"><h3>Prevent duplicates</h3><p>Before a second team re-implements an \
existing capability, <code>dupes</code> flags the overlapping contracts. The SSOT is the place you \
look first.</p></div>
    </div>
  </div>
</section>

<!--##REQMAP:COMMANDS## — engine lists the registered subcommands -->
<section class="band">
  <div class="wrap">
    <div class="secthead"><span class="tag eng">engine-generated</span></div>
    <p class="eyebrow">Surface</p>
    <h2>All 18 commands</h2>
    <div class="cmds">
      <div class="cmd gate"><code>gate</code><p>The gate. Links resolve, drift detected, \
test-links verified. Run before every commit + in CI.</p></div>
      <div class="cmd"><code>sync</code><p>Rescan + advance the drift baseline + regen the map \
(and a committed _findings.md). --accept-drift for an edited confirmed contract.</p></div>
      <div class="cmd"><code>init</code><p>First-time bootstrap: scaffold, draft from code, lock, \
map, next-steps. Idempotent.</p></div>
      <div class="cmd"><code>map</code><p>Generate _map.md (Mermaid) + _map.json (graph) + \
_map.html (viewer).</p></div>
      <div class="cmd"><code>site</code><p>Inject engine-owned regions (nav links + counts) into a \
presentation page. --attach/--diagram.</p></div>
      <div class="cmd"><code>next</code><p>"What should I work on?" — prioritised, actionable risk \
buckets.</p></div>
      <div class="cmd"><code>show &lt;ID&gt;</code><p>Consolidated dossier: contract, deps, \
members by role, risk.</p></div>
      <div class="cmd"><code>lint</code><p>Readability/structure check on non-draft \
requirements.</p></div>
      <div class="cmd"><code>dupes</code><p>Flag requirement pairs with overlapping contracts \
(TF-IDF).</p></div>
      <div class="cmd"><code>health</code><p>Corpus coherence score + component counts. --json for \
a badge.</p></div>
      <div class="cmd"><code>confirm &lt;ID&gt;</code><p>Flip a reviewed requirement to confirmed \
(needs a member).</p></div>
      <div class="cmd"><code>review</code><p>Emit a JSON review plan (intent/contract/acceptance) \
for AI-assisted quality review.</p></div>
      <div class="cmd"><code>new</code><p>Scaffold a new requirement from the built-in \
template.</p></div>
      <div class="cmd"><code>scan</code><p>List which code members belong to which \
capability.</p></div>
      <div class="cmd"><code>draft</code><p>Draft requirements from untagged legacy code + \
prose.</p></div>
      <div class="cmd"><code>plan</code><p>Read-only JSON extraction plan (AI-assist), writes \
nothing.</p></div>
      <div class="cmd"><code>findings</code><p>Aggregate open verify-intent questions into \
_findings.md.</p></div>
      <div class="cmd"><code>export</code><p>Emit _map.json for an external front-end. --out PATH \
or -.</p></div>
    </div>
  </div>
</section>
<!--##/REQMAP:COMMANDS##-->

<!--##REQMAP:LAYERS## — engine derives layers from requirement frontmatter -->
<section>
  <div class="wrap">
    <div class="secthead"><span class="tag eng">engine-generated</span></div>
    <p class="eyebrow">Layer model</p>
    <h2>Bus, feature, need, aggregate</h2>
    <div class="layers">
      <div class="layer bus"><div class="l">layer: bus</div><h3>Foundation</h3><p>High fan-in \
capabilities — config, parse, scan, drift. Change only behind the contract.</p><div \
class="ids">ARCH-PARSE-001 · ARCH-SCAN-002 · ARCH-DRIFT-003</div></div>
      <div class="layer feat"><div class="l">layer: feature</div><h3>Composed</h3><p>Built on the \
bus via <code>depends_on</code>; each carries its own contract, acceptance, tests.</p><div \
class="ids">ARCH-CHECK-006 · ARCH-MAP-007 · ARCH-INIT-012</div></div>
      <div class="layer need"><div class="l">layer: need</div><h3>Stakeholder need</h3><p>An \
upstream need, satisfied-by features via <code>satisfies:</code>; exempt from the code \
gate.</p><div class="ids">SYS-SSOT-001</div></div>
      <div class="layer need"><div class="l">layer: aggregate</div><h3>Roof</h3><p>No code of its \
own: its implementation is its <code>depends_on</code> requirements'. Exempt from the code gate, \
like a need — downward instead of upward.</p><div class="ids">—</div></div>
    </div>
  </div>
</section>
<!--##/REQMAP:LAYERS##-->
<!-- HYBRID MECHANISM — meta, explains the split -->
<section class="mech">
  <div class="wrap">
    <div class="secthead"><span class="tag auth">authored</span></div>
    <p class="eyebrow">How this page stays current</p>
    <h2>The hybrid: markers</h2>
    <p class="lead" style="margin-bottom:18px">The engine only rewrites what lives between its \
markers. Your prose is never touched.
      Re-run <code>reqmap.py sync</code> after any change and the nav links, stats, commands, and \
layers refresh — the hero and narrative survive.</p>
<pre><span class="c-dim">&lt;!--##REQMAP:NAV##--&gt;</span>      <span class="c-eng">← engine: \
Live Map / Diagram / GitHub, from `git remote` + artifact paths</span>
   ...your logo, your wording...   <span class="c-auth">← authored, preserved</span>
<span class="c-dim">&lt;!--##/REQMAP:NAV##--&gt;</span>

<span class="c-auth">&lt;header class="hero"&gt; ... your headline + story ... \
&lt;/header&gt;</span>   <span class="c-auth">← authored, preserved</span>

<span class="c-dim">&lt;!--##REQMAP:STATS##--&gt;</span>    <span class="c-eng">← engine: counts \
from _map.json, recomputed every run</span>
<span class="c-dim">&lt;!--##REQMAP:COMMANDS##--&gt;</span> <span class="c-eng">← engine: the \
registered subcommands</span>
<span class="c-dim">&lt;!--##REQMAP:LAYERS##--&gt;</span>   <span class="c-eng">← engine: layers \
from requirement frontmatter</span></pre>
  </div>
</section>
<footer>
  Prototype of <code>reqmap.py sync --attach</code> · hybrid (engine links + data / authored prose) ·
  self-contained, no network, no <code>file://</code> iframes · Senate 2026-06-14 verdict \
<strong>MODIFY</strong> conditions applied.
</footer>
</body>
</html>
"""  # implements: ARCH-SITE-026


def _site_pages_bootstrap(docs_dir):  # implements: ARCH-SITE-026  # implements: REQ-SITE-924
    """Ensure docs/ carries a GitHub Pages signal so ARCH-PAGES-021 publishes and
    the page is servable: write .nojekyll and an index.html redirect when absent.
    Idempotent — never clobbers an existing index.html."""
    os.makedirs(docs_dir, exist_ok=True)
    nojekyll = os.path.join(docs_dir, ".nojekyll")
    if not os.path.exists(nojekyll):
        open(nojekyll, "w").close()
    index = os.path.join(docs_dir, "index.html")
    if not os.path.exists(index):
        with open(index, "w", encoding="utf-8") as f:
            f.write('<!doctype html><meta charset="utf-8">'
                    '<meta http-equiv="refresh" content="0; url=./architecture.html">'
                    '<link rel="canonical" href="./architecture.html">'
                    '<title>Project site</title>'
                    '<p>Redirecting to <a href="./architecture.html">the project site</a>…</p>\n')


def _site_diagram_ok(target_path, diagram_rel):  # implements: ARCH-SITE-026
    """True when `diagram_rel` (relative to the page's directory) names an existing
    file — so the Diagram link is emitted only when the artifact is actually there."""
    if not diagram_rel:
        return False
    return os.path.isfile(os.path.join(os.path.dirname(target_path) or ".", diagram_rel))


def _site_default_target(root):  # implements: ARCH-SITE-026
    """docs/architecture.html at the git root (so running from plugin/ still finds
    the project-root docs/), or None when there is no docs/.

    The site page is the ONE thing the engine writes into docs/. The map used to be
    copied there too; it is not any more — `requirements/_map.html` is the only
    rendered viewer, and a published copy is built where it is published."""
    git_root = _git_root(root)
    docs = os.path.join(git_root, "docs")
    return os.path.join(docs, "architecture.html") if os.path.isdir(docs) else None


def cmd_site(ws, root=".", attach=None,  # implements: REQ-SITE-924
             regions=None, diagram=None, detect=False):  # implements: ARCH-SITE-026
    """Inject engine-owned regions into a presentation page (attach mode) or write
    a default page when the target is absent (scaffold mode). Deterministic and
    headless-safe: never prompts, never raises on missing git/files. `detect`
    prints findings + the suggested command and writes nothing."""
    reqs, members = ws.reqs, ws.members
    regions = regions or ["nav"]
    data = _build_map_data(reqs, members)
    repo_url = _git_remote_web_url(root)

    if detect:
        default = _site_default_target(root)
        cands = [p for p in (default,) if p and os.path.isfile(p)]
        print("repo: {}".format(repo_url or "(no remote)"))
        print("presentation candidates: {}".format(", ".join(cands) or "(none)"))
        tgt = default or os.path.join(root, "docs", "architecture.html")
        print("suggested: reqmap sync --attach {}".format(tgt))
        return 0

    if not attach:
        print("usage: reqmap sync --attach <page.html>")
        print("  the nav and stats regions are refreshed together; `init` scaffolds "
              "the page when it does not exist yet")
        return 0

    map_ok = os.path.isfile(os.path.join(os.path.dirname(attach) or ".", "map.html"))
    diagram_rel = diagram if _site_diagram_ok(attach, diagram) else None
    ctx = _site_context_from_data(data, repo_url=repo_url, map_ok=map_ok, diagram_rel=diagram_rel)

    if os.path.isfile(attach):
        with open(attach, encoding="utf-8") as f:
            html = f.read()
        mode = "refreshed"
    else:                                   # scaffold mode
        os.makedirs(os.path.dirname(attach) or ".", exist_ok=True)
        # escape before substituting — a repo dir name or remote URL with < > " &
        # would otherwise break out of the title/href sinks in the scaffold template
        html = (SITE_TEMPLATE.replace("%%REPO_NAME%%", _html_escape(_repo_name(root) or "this \
project"))
                             .replace("%%REPO_URL%%", _html_escape(repo_url or "#")))
        mode = "scaffolded"

    for name in regions:
        if name in SITE_REGIONS:
            html = _inject_region(html, name, _render_region(name, ctx))

    with open(attach, "w", encoding="utf-8") as f:
        f.write(html)
    print("{} {} (regions: {})".format(mode, attach, ",".join(regions)))
    return 0
