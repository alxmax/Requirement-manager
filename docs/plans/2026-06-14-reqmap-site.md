# `reqmap.py site` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic `reqmap.py site` command that injects engine-owned, marker-delimited regions into a project presentation page (and scaffolds one when absent), wired into `init`, while preserving authored prose.

**Architecture:** Two layers — the stdlib engine (`reqmap.py`, flag-driven, headless-safe) does the injection/scaffold; the AI skill (separate, not in this plan) does the interactive asking. v1 engine-owns two regions: `NAV` (links: Live Map / Diagram / GitHub — refreshed but excluded from the freshness gate because it embeds the fork-specific repo URL) and `STATS` (deterministic counts — gated). Reuses `REQ-PAGES-021`'s git-root + Pages-signal machinery. `COMMANDS`/`LAYERS` are authored in the scaffold for v1 and become engine-owned in a follow-up plan.

**Tech Stack:** Python 3 stdlib only (`subprocess`, `re`, `os`), `unittest`. Source spec: `docs/specs/2026-06-14-reqmap-site-presentation-design.md`. Visual reference: `docs/reqmap_site_prototype.html`.

**Conventions to match:** every new function/code path carries `# implements: REQ-SITE-026`; tests carry `# tested-by: REQ-SITE-026`; engine functions never raise on missing git/files (mirror `_repo_name`, `_docs_publish_path`). Run all commands from `plugin/`.

---

## File Structure

- **Modify `plugin/scripts/reqmap.py`** — all engine logic lives in this one file by design. New module-level constants (`SITE_REGIONS`, `SITE_TEMPLATE`), new helpers (`_git_remote_web_url`, `_region_markers`, `_inject_region`, `_extract_region`, `_site_context_from_data`, `_render_region`, `_site_default_target`, `_site_diagram_ok`), the `cmd_site` entry point, an `init` hook, a `_map_check` extension, and argparse wiring.
- **Modify `plugin/scripts/test_reqmap.py`** — one new `Site(unittest.TestCase)` class with the §Tests cases.
- **Create `plugin/requirements/REQ-SITE-026.md`** — the new capability requirement.
- **Modify `plugin/skills/requirement-manager/SKILL.md`** — a "Project site" section (interactive flow; documents the engine contract).
- **Modify `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`** — semver bump `1.34.0 → 1.35.0` (3 locations).
- **Modify `plugin/scripts/reqmap.py`** — bump `MAP_ENGINE_VERSION`.
- **Modify `CLAUDE.md`** — one line in the commands block.

---

## Task 1: git-remote → web-URL helper

**Files:**
- Modify: `plugin/scripts/reqmap.py` (add near `_repo_name`, ~line 2799)
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing test**

Add to `test_reqmap.py` (new class):

```python
class Site(unittest.TestCase):  # tested-by: REQ-SITE-026
    def test_remote_url_normalises_scp_and_https(self):
        self.assertEqual(R._normalise_remote("git@github.com:alxmax/Requirement-manager.git"),
                         "https://github.com/alxmax/Requirement-manager")
        self.assertEqual(R._normalise_remote("https://github.com/alxmax/Requirement-manager.git"),
                         "https://github.com/alxmax/Requirement-manager")
        self.assertEqual(R._normalise_remote("ssh://git@example.com/o/r.git"),
                         "https://example.com/o/r")
        self.assertIsNone(R._normalise_remote(""))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test_reqmap.Site.test_remote_url_normalises_scp_and_https -v`
Expected: FAIL — `AttributeError: module 'reqmap' has no attribute '_normalise_remote'`

- [ ] **Step 3: Write minimal implementation**

In `reqmap.py` (confirm `import re` and `import subprocess` exist near the top — both are already used):

```python
def _normalise_remote(url):  # implements: REQ-SITE-026
    """Normalise a git remote URL to a https web URL (https://host/owner/repo),
    or None when empty/unparseable. Handles scp-style (git@host:owner/repo.git),
    ssh:// and https:// forms; strips a trailing `.git`. Pure string work."""
    url = (url or "").strip()
    if not url:
        return None
    if url.endswith(".git"):
        url = url[:-4]
    m = re.match(r"^[\w.+-]+@([\w.-]+):(.+)$", url)          # scp-style
    if m:
        return "https://{}/{}".format(m.group(1), m.group(2))
    m = re.match(r"^(?:ssh|git|https?)://(?:[^@/]+@)?([\w.-]+)/(.+)$", url)
    if m:
        return "https://{}/{}".format(m.group(1), m.group(2))
    return url or None


def _git_remote_web_url(root):  # implements: REQ-SITE-026
    """The project's web URL from git `remote.origin.url`, or None when git is
    absent / no remote / not a checkout. Honours the REQMAP_REPO override (a
    bare slug becomes https://github.com/<slug>; empty disables). Never raises."""
    override = os.environ.get("REQMAP_REPO")
    if override is not None:
        if not override:
            return None
        return override if "://" in override else "https://github.com/" + override
    url = ""
    try:
        r = subprocess.run(["git", "-C", root, "config", "--get", "remote.origin.url"],
                           capture_output=True, text=True, timeout=3)
        if r.returncode == 0:
            url = r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        url = ""
    return _normalise_remote(url)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test_reqmap.Site.test_remote_url_normalises_scp_and_https -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(site): git remote -> web URL normaliser (REQ-SITE-026)"
```

---

## Task 2: Region markers — inject & extract

**Files:**
- Modify: `plugin/scripts/reqmap.py`
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing test**

```python
    def test_inject_region_refreshes_and_preserves_prose(self):
        html = "<body>\n<h1>AUTHORED</h1>\n<!--##REQMAP:NAV##-->old<!--##/REQMAP:NAV##-->\n<p>keep</p>\n</body>"
        out = R._inject_region(html, "nav", "NEW")
        self.assertIn("<!--##REQMAP:NAV##-->\nNEW\n<!--##/REQMAP:NAV##-->", out)
        self.assertIn("<h1>AUTHORED</h1>", out)   # prose preserved
        self.assertIn("<p>keep</p>", out)
        self.assertNotIn("old", out)

    def test_inject_region_absent_inserts_after_body(self):
        html = "<body>\n<h1>hi</h1>\n</body>"
        out = R._inject_region(html, "nav", "NEW")
        self.assertIn("<!--##REQMAP:NAV##-->\nNEW\n<!--##/REQMAP:NAV##-->", out)
        self.assertLess(out.index("<body>"), out.index("REQMAP:NAV"))  # inserted after <body>

    def test_extract_region_roundtrip(self):
        html = R._inject_region("<body></body>", "stats", "DATA")
        self.assertEqual(R._extract_region(html, "stats"), "DATA")
        self.assertIsNone(R._extract_region("<body></body>", "stats"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test_reqmap.Site -v -k region`
Expected: FAIL — `_inject_region` / `_extract_region` undefined.

- [ ] **Step 3: Write minimal implementation**

```python
SITE_REGIONS = ("nav", "stats", "commands", "layers")  # implements: REQ-SITE-026


def _region_markers(name):  # implements: REQ-SITE-026
    key = name.upper()
    return "<!--##REQMAP:{}##-->".format(key), "<!--##/REQMAP:{}##-->".format(key)


def _inject_region(html, name, inner, anchor="<body>"):  # implements: REQ-SITE-026
    """Replace the content between the paired markers for `name` with `inner`
    (idempotent). Markers absent -> insert a fresh marked block right after the
    first `anchor`; anchor absent too -> append. Only the marked block is
    written; surrounding (authored) bytes are untouched."""
    open_m, close_m = _region_markers(name)
    block = open_m + "\n" + inner + "\n" + close_m
    i, j = html.find(open_m), html.find(close_m)
    if i != -1 and j != -1 and j > i:
        return html[:i] + block + html[j + len(close_m):]
    a = html.find(anchor)
    if a != -1:
        a += len(anchor)
        return html[:a] + "\n" + block + html[a:]
    return html + "\n" + block


def _extract_region(html, name):  # implements: REQ-SITE-026
    """Inner text between the paired markers for `name`, or None when absent.
    Lets the freshness gate diff only engine-owned regions (prose is exempt)."""
    open_m, close_m = _region_markers(name)
    i = html.find(open_m)
    if i == -1:
        return None
    i += len(open_m)
    j = html.find(close_m, i)
    return html[i:j] if j != -1 else None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test_reqmap.Site -v -k region`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(site): marker inject/extract for engine-owned regions (REQ-SITE-026)"
```

---

## Task 3: Region renderers (NAV + STATS) from map data

**Files:**
- Modify: `plugin/scripts/reqmap.py`
- Test: `plugin/scripts/test_reqmap.py`

NAV degrades by omission: a link is emitted only when its target resolves (repo URL present; `map.html` sibling exists; `--diagram` file exists). STATS is deterministic counts from the graph.

- [ ] **Step 1: Write the failing test**

```python
    def _mapdata(self):
        return {"nodes": [{"id": "A-1", "layer": "bus", "status": "confirmed"},
                          {"id": "B-2", "layer": "feature", "status": "confirmed"},
                          {"id": "C-3", "layer": "feature", "status": "draft"}],
                "edges": [["B-2", "A-1"]]}

    def test_render_nav_omits_absent_targets(self):
        ctx = {"repo_url": None, "map_ok": False, "diagram_rel": None}
        nav = R._render_region("nav", ctx)
        self.assertNotIn("<a", nav)            # nothing resolves -> no links, no crash
        ctx = {"repo_url": "https://github.com/o/r", "map_ok": True, "diagram_rel": "d.html"}
        nav = R._render_region("nav", ctx)
        self.assertIn('href="https://github.com/o/r"', nav)
        self.assertIn('href="map.html"', nav)
        self.assertIn('href="d.html"', nav)
        self.assertIn('target="_blank"', nav)  # plain anchors, not iframes (Senate)

    def test_render_stats_counts_from_graph(self):
        ctx = R._site_context_from_data(self._mapdata(), repo_url=None, map_ok=False, diagram_rel=None)
        stats = R._render_region("stats", ctx)
        self.assertIn(">3<", stats)            # 3 requirements
        self.assertIn(">2<", stats)            # 2 confirmed
        self.assertIn(R.MAP_ENGINE_VERSION, stats)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test_reqmap.Site -v -k render`
Expected: FAIL — `_render_region` / `_site_context_from_data` undefined.

- [ ] **Step 3: Write minimal implementation**

```python
def _site_context_from_data(data, repo_url, map_ok, diagram_rel):  # implements: REQ-SITE-026
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


def _render_region(name, ctx):  # implements: REQ-SITE-026
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
        return '<nav class="reqmap-nav">' + "".join(links) + '</nav>'
    if name == "stats":
        c = ctx["counts"]
        cells = [("requirements", c["requirements"]), ("confirmed", c["confirmed"]),
                 ("layers", c["layers"]), ("edges", c["edges"]),
                 ("engine", MAP_ENGINE_VERSION)]
        items = "".join('<div class="stat"><b>{}</b><span>{}</span></div>'.format(v, k)
                        for k, v in cells)
        return '<div class="reqmap-stats">' + items + '</div>'
    return ""
```

If a `_html_escape` helper does not already exist in `reqmap.py`, add this minimal one beside the renderers:

```python
def _html_escape(s):  # implements: REQ-SITE-026
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))
```

(First grep for an existing escaper: `grep -n "def _html_escape\|def _esc" plugin/scripts/reqmap.py` — reuse it if present and skip adding a duplicate.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test_reqmap.Site -v -k render`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(site): NAV + STATS region renderers (REQ-SITE-026)"
```

---

## Task 4: Scaffold template constant

**Files:**
- Modify: `plugin/scripts/reqmap.py`
- Reference: `docs/reqmap_site_prototype.html` (the committed visual)

- [ ] **Step 1: Add `SITE_TEMPLATE` as an inline constant** (no test step — exercised by Task 6's scaffold test)

Create `SITE_TEMPLATE` by lifting the markup of `docs/reqmap_site_prototype.html` with these exact transformations (the prototype is the source of truth for the CSS/layout; do NOT invent new markup):

1. Keep the entire `<style>` block verbatim.
2. Replace the hardcoded nav `<nav class="nav-links">…</nav>` block with the marker pair only:
   `<!--##REQMAP:NAV##--><!--##/REQMAP:NAV##-->` (engine fills it; Task 3 output).
3. Replace the stats grid inner (`<div class="stats">…</div>` contents) with:
   `<!--##REQMAP:STATS##--><!--##/REQMAP:STATS##-->`.
4. Leave the hero, pillars, commands grid, layer model, and "hybrid" sections as authored prose, but put a `<!-- author me -->` comment immediately inside the hero, and substitute the project title with the `{repo_name}` field and the GitHub button href with `{repo_url}`.
5. Make it a Python triple-quoted string named `SITE_TEMPLATE` with `{repo_name}` and `{repo_url}` as the only `str.format` fields (escape any literal `{`/`}` in the CSS as `{{`/`}}`).

Header comment above the constant:

```python
# A self-contained default presentation page written by `site` scaffold mode.
# Inline (not a vendored file) so the engine stays hermetic. The NAV and STATS
# regions are marker-delimited and engine-owned; everything else is authored
# prose the user/skill rewrites. Source markup: docs/reqmap_site_prototype.html.
SITE_TEMPLATE = """..."""   # implements: REQ-SITE-026
```

- [ ] **Step 2: Sanity-check the constant parses and formats**

Run: `python -c "import reqmap; print('OK' if '##REQMAP:NAV##' in reqmap.SITE_TEMPLATE.format(repo_name='x', repo_url='y') else 'BAD')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add plugin/scripts/reqmap.py
git commit -m "feat(site): inline SITE_TEMPLATE scaffold (REQ-SITE-026)"
```

---

## Task 5: `cmd_site` (detect / attach / scaffold) + helpers

**Files:**
- Modify: `plugin/scripts/reqmap.py`
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing tests** (idempotency, prose-preservation, no-remote degradation, scaffold)

```python
    def _seed(self, d):
        """Minimal reqs dir with one confirmed requirement + _map.json so site can build data."""
        reqs = os.path.join(d, "requirements"); os.makedirs(reqs)
        with open(os.path.join(reqs, "AREA-X-001.md"), "w", encoding="utf-8") as f:
            f.write("---\nid: AREA-X-001\nstatus: confirmed\nlayer: feature\n---\n# X\n> why\n")
        return reqs

    def test_attach_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            open(page, "w", encoding="utf-8").write("<body>\n<h1>Mine</h1>\n</body>")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(r, m, reqs, d, attach=page, regions=["nav", "stats"])
            first = open(page, encoding="utf-8").read()
            R.cmd_site(r, m, reqs, d, attach=page, regions=["nav", "stats"])
            second = open(page, encoding="utf-8").read()
            self.assertEqual(first, second)         # byte-identical re-run
            self.assertIn("<h1>Mine</h1>", second)  # prose preserved

    def test_no_remote_degrades(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            page = os.path.join(d, "page.html")
            open(page, "w", encoding="utf-8").write("<body></body>")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            rc = R.cmd_site(r, m, reqs, d, attach=page, regions=["nav"])
            self.assertEqual(rc, 0)                                  # no git -> no crash
            self.assertNotIn("GitHub", open(page, encoding="utf-8").read())  # link omitted

    def test_scaffold_writes_full_page(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d)
            target = os.path.join(d, "docs", "architecture.html")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(r, m, reqs, d, attach=target, regions=["nav", "stats"])
            html = open(target, encoding="utf-8").read()
            self.assertIn("<!--##REQMAP:NAV##-->", html)
            self.assertIn("<!--##REQMAP:STATS##-->", html)
            self.assertIn("<!-- author me -->", html)               # placeholder hero marker
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m unittest test_reqmap.Site -v -k "attach or remote or scaffold"`
Expected: FAIL — `cmd_site` undefined.

- [ ] **Step 3: Write the implementation**

```python
def _site_diagram_ok(target_path, diagram_rel):  # implements: REQ-SITE-026
    """True when `diagram_rel` (relative to the page's directory) names an existing
    file — so the Diagram link is emitted only when the artifact is actually there."""
    if not diagram_rel:
        return False
    return os.path.isfile(os.path.join(os.path.dirname(target_path) or ".", diagram_rel))


def cmd_site(reqs, members, reqs_dir, root=".", attach=None,
             regions=None, diagram=None, detect=False):  # implements: REQ-SITE-026
    """Inject engine-owned regions into a presentation page (attach mode) or write
    a default page when the target is absent (scaffold mode). Deterministic and
    headless-safe: never prompts, never raises on missing git/files. `detect`
    prints findings + the suggested command and writes nothing."""
    regions = regions or ["nav"]
    data = _build_map_data(reqs, members)
    repo_url = _git_remote_web_url(root)

    if detect:
        cands = [p for p in (_site_default_target(root),) if p and os.path.isfile(p)]
        print("repo: {}".format(repo_url or "(no remote)"))
        print("presentation candidates: {}".format(", ".join(cands) or "(none)"))
        tgt = _site_default_target(root) or os.path.join(root, "docs", "architecture.html")
        print("suggested: reqmap site --attach {} --regions nav,stats".format(tgt))
        return 0

    if not attach:
        print("usage: reqmap site --attach <page.html> [--regions nav,stats] [--diagram <rel>]")
        print("   or: reqmap site --detect")
        return 0

    map_ok = os.path.isfile(os.path.join(os.path.dirname(attach) or ".", "map.html"))
    diagram_rel = diagram if _site_diagram_ok(attach, diagram) else None
    ctx = _site_context_from_data(data, repo_url=repo_url, map_ok=map_ok, diagram_rel=diagram_rel)

    if os.path.isfile(attach):
        html = open(attach, encoding="utf-8").read()
        mode = "refreshed"
    else:                                   # scaffold mode
        os.makedirs(os.path.dirname(attach) or ".", exist_ok=True)
        html = SITE_TEMPLATE.format(repo_name=(_repo_name(root) or "this project"),
                                    repo_url=(repo_url or "#"))
        mode = "scaffolded"

    for name in regions:
        if name in SITE_REGIONS:
            html = _inject_region(html, name, _render_region(name, ctx))

    with open(attach, "w", encoding="utf-8") as f:
        f.write(html)
    print("{} {} (regions: {})".format(mode, attach, ",".join(regions)))
    return 0
```

Add the default-target resolver beside `_docs_publish_path` (reuse its git-root logic):

```python
def _site_default_target(root):  # implements: REQ-SITE-026
    """docs/architecture.html at the git root (so running from plugin/ still finds
    the project-root docs/), or None when there is no docs/. Mirrors
    _docs_publish_path's git-root resolution."""
    try:
        git_root = subprocess.check_output(
            ["git", "-C", root, "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, timeout=3).decode().strip()
    except Exception:
        git_root = root
    docs = os.path.join(git_root, "docs")
    return os.path.join(docs, "architecture.html") if os.path.isdir(docs) else None
```

- [ ] **Step 4: Run to verify they pass**

Run: `python -m unittest test_reqmap.Site -v -k "attach or remote or scaffold"`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(site): cmd_site detect/attach/scaffold (REQ-SITE-026)"
```

---

## Task 6: argparse wiring

**Files:**
- Modify: `plugin/scripts/reqmap.py` (`main()`, ~line 2996-3095)
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing test** (drive the CLI via `R.main()` with patched argv)

```python
    def test_cli_site_detect_runs(self):
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            argv = ["reqmap", "site", "--detect", "--root", d]
            buf = io.StringIO()
            old = sys.argv; sys.argv = argv
            try:
                with contextlib.redirect_stdout(buf):
                    rc = R.main()
            finally:
                sys.argv = old
            self.assertEqual(rc, 0)
            self.assertIn("suggested:", buf.getvalue())
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m unittest test_reqmap.Site.test_cli_site_detect_runs -v`
Expected: FAIL — argparse rejects `site` (`invalid choice: 'site'`).

- [ ] **Step 3: Implement the wiring**

In `main()`, add `"site"` to the `cmd` choices list (line ~2997):

```python
    ap.add_argument("cmd", choices=["init", "new", "scan", "check", "map", "export", "next", "lint", "show", "similar", "health", "extract", "candidates", "findings", "promote", "promote-todo", "review", "site"])
```

Add the new flags (after the existing `--cache` argument, ~line 3033):

```python
    ap.add_argument("--attach", default=None,
                    help="site: target HTML to inject engine-owned regions into (scaffolds it if absent)")
    ap.add_argument("--regions", default="nav",
                    help="site: comma list of regions to inject (nav,stats); default nav")
    ap.add_argument("--diagram", default=None,
                    help="site: relative path (from the page) to an excalidraw HTML; linked only if it exists")
    ap.add_argument("--detect", action="store_true",
                    help="site: print docs/ findings + the suggested command; writes nothing")
    ap.add_argument("--no-site", dest="no_site", action="store_true",
                    help="init: skip the final site step")
```

Add the dispatch branch (alongside the other post-load commands, e.g. after the `map` branch, ~line 3078):

```python
    if a.cmd == "site":
        regions = [x.strip() for x in (a.regions or "").split(",") if x.strip()]
        return cmd_site(reqs, members, reqs_dir, code_root,
                        attach=a.attach, regions=regions, diagram=a.diagram, detect=a.detect)
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m unittest test_reqmap.Site.test_cli_site_detect_runs -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(site): argparse wiring for site command (REQ-SITE-026)"
```

---

## Task 7: `init` hook (best-effort site step)

**Files:**
- Modify: `plugin/scripts/reqmap.py` (`cmd_init` ~line 2336; its caller `main()` ~3052)
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing test**

```python
    def test_init_scaffolds_site_when_absent(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))   # docs/ present -> default target resolvable
            # a trivial taggable source file so extract has something
            open(os.path.join(d, "a.py"), "w").write("# implements: AREA-X-001\nx = 1\n")
            R.cmd_init(os.path.join(d, "requirements"), d, no_site=False)
            page = os.path.join(d, "docs", "architecture.html")
            self.assertTrue(os.path.isfile(page))
            self.assertIn("<!--##REQMAP:NAV##-->", open(page, encoding="utf-8").read())

    def test_init_no_site_flag_skips(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            open(os.path.join(d, "a.py"), "w").write("x = 1\n")
            R.cmd_init(os.path.join(d, "requirements"), d, no_site=True)
            self.assertFalse(os.path.isfile(os.path.join(d, "docs", "architecture.html")))
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m unittest test_reqmap.Site -v -k init`
Expected: FAIL — `cmd_init() got an unexpected keyword argument 'no_site'`.

- [ ] **Step 3: Implement the hook**

Change the `cmd_init` signature (line 2311):

```python
def cmd_init(reqs_dir, code_root, wipe=False, no_site=False):  # implements: REQ-INIT-012
```

Insert the best-effort site step immediately after `cmd_map(reqs, members, reqs_dir, code_root)` (line 2336), before the `print("\n" + "=" * 60)` line:

```python
    # implements: REQ-SITE-026 — best-effort project site. Never aborts init.
    if not no_site:
        target = _site_default_target(code_root)
        if target:
            try:
                _site_pages_bootstrap(os.path.dirname(target))   # .nojekyll + index.html redirect
                cmd_site(reqs, members, reqs_dir, code_root, attach=target, regions=["nav", "stats"])
            except Exception as e:   # site is decorative; a failure must not break bootstrap
                print("note: site step skipped ({}).".format(e))
        else:
            print("note: no docs/ folder — run the requirement-manager skill to set up a project site.")
```

Add the Pages bootstrap helper near `_docs_publish_path`:

```python
def _site_pages_bootstrap(docs_dir):  # implements: REQ-SITE-026
    """Ensure docs/ carries a GitHub Pages signal so REQ-PAGES-021 publishes and
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
```

Update the `main()` call site (line 3053):

```python
    if a.cmd == "init":
        return cmd_init(reqs_dir, code_root, wipe=a.wipe, no_site=a.no_site)
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m unittest test_reqmap.Site -v -k init`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(site): init scaffolds/refreshes the project site (REQ-SITE-026)"
```

---

## Task 8: Region-only staleness gate (STATS) in `map --check`

**Files:**
- Modify: `plugin/scripts/reqmap.py` (`_map_check` ~line 2389-2396)
- Test: `plugin/scripts/test_reqmap.py`

Only `STATS` is gated — `NAV` embeds the fork-specific repo URL (like `_map.json`'s `repo` field) so it is excluded, exactly as `_strip_generated` excludes `repo`.

- [ ] **Step 1: Write the failing test**

```python
    def test_map_check_flags_stale_stats_region(self):
        with tempfile.TemporaryDirectory() as d:
            reqs = self._seed(d); os.makedirs(os.path.join(d, "docs"))
            page = os.path.join(d, "docs", "architecture.html")
            r = R.load_requirements(reqs); m = R.scan_members(d, reqs)
            R.cmd_site(r, m, reqs, d, attach=page, regions=["stats"])
            data = R._build_map_data(r, m); data["repo"] = R._repo_name(d)
            self.assertEqual(R._map_check(data, reqs, d), 0)        # fresh
            html = open(page, encoding="utf-8").read().replace(
                R._extract_region(open(page, encoding="utf-8").read(), "stats"), "TAMPERED")
            open(page, "w", encoding="utf-8").write(html)
            self.assertEqual(R._map_check(data, reqs, d), 1)        # stale stats -> exit 1
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m unittest test_reqmap.Site.test_map_check_flags_stale_stats_region -v`
Expected: FAIL — `_map_check` returns 0 (does not yet check the site page).

- [ ] **Step 3: Implement the extension**

In `_map_check`, after the `docs/map.html` block and before `if stale:` (line ~2396), add:

```python
    # Site presentation page (REQ-SITE-026): gate the deterministic STATS region
    # only. NAV embeds the git-derived repo URL (fork-specific) and is excluded,
    # mirroring the `repo`-field exclusion in _strip_generated.
    site_target = _site_default_target(root)
    if site_target and os.path.exists(site_target):
        on_disk = open(site_target, encoding="utf-8").read()
        disk_stats = _extract_region(on_disk, "stats")
        if disk_stats is not None:
            ctx = _site_context_from_data(data, repo_url=None, map_ok=False, diagram_rel=None)
            if disk_stats != _render_region("stats", ctx):
                stale.append(os.path.basename(site_target))
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m unittest test_reqmap.Site.test_map_check_flags_stale_stats_region -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(site): region-only staleness gate for the site page (REQ-SITE-026)"
```

---

## Task 9: Excalidraw-independence anchor test

**Files:**
- Test: `plugin/scripts/test_reqmap.py`

Senate blocking condition (Confucius/Musk): the engine must never couple to the excalidraw skill's builder.

- [ ] **Step 1: Write the test**

```python
    def test_engine_never_touches_excalidraw_builder(self):
        src = open(R.__file__, encoding="utf-8").read()
        self.assertNotIn("excalidraw_builder", src)   # link-only; no import/exec coupling
```

- [ ] **Step 2: Run to verify it passes**

Run: `python -m unittest test_reqmap.Site.test_engine_never_touches_excalidraw_builder -v`
Expected: PASS (the implementation never references the builder)

- [ ] **Step 3: Commit**

```bash
git add plugin/scripts/test_reqmap.py
git commit -m "test(site): assert engine independence from excalidraw_builder (REQ-SITE-026)"
```

---

## Task 10: New requirement `REQ-SITE-026.md`

**Files:**
- Create: `plugin/requirements/REQ-SITE-026.md`

- [ ] **Step 1: Author the requirement** (model on `REQ-PAGES-021.md`)

```markdown
---
id: REQ-SITE-026
status: confirmed
layer: feature
owner: Alex
depends_on: [REQ-MAP-007, REQ-VIEWER-007, REQ-PAGES-021]
satisfies: [NEED-SSOT-001]
milestone: v1.35
---

# Generate & maintain a project presentation page

> A project is easier to grasp from one presentation page than from a folder of
> files. This capability lets the engine keep that page's links and key numbers
> current — injecting engine-owned regions into a page the author still controls,
> and scaffolding one when none exists — so the page never drifts from the registry.

## WHAT — Contract (normative)
- `site --attach <page.html>` shall inject the requested marker-delimited regions
  (`nav`, `stats`; default `nav`) into the page, replacing only the bytes between each
  region's paired markers and preserving all other (authored) content. A re-run with no
  underlying change shall produce a byte-identical file (idempotent).
- When the `--attach` target does not exist, `site` shall scaffold a self-contained default
  page (the inline `SITE_TEMPLATE`) with the regions filled and an authored placeholder hero.
- The `nav` region shall emit a link only when its target resolves: Live Map when a sibling
  `map.html` exists, Diagram when `--diagram <rel>` names an existing file, GitHub when a git
  remote resolves. A missing git remote, missing artifact, or non-checkout shall never raise.
- The engine shall never import or execute the excalidraw skill's builder; the Diagram entry
  is a link only.
- `init` shall, unless `--no-site` is given, run a best-effort `site` step after `map`:
  refresh `nav`+`stats` in `docs/architecture.html` if it exists, else scaffold it plus a
  Pages signal (`.nojekyll` + an `index.html` redirect). A failure in this step shall not
  abort `init`.
- `map --check` shall flag the site page stale when its on-disk `stats` region differs from a
  fresh render. The `nav` region is excluded (it embeds the fork-specific repo URL). A page
  that was never generated, or that lacks a `stats` region, is not stale.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent.

## WHAT — Notes & known limitations (informative)
- v1 engine-owns `nav` + `stats`; `commands`/`layers` render as authored content in the
  scaffold and may be promoted to engine-owned regions later.
- The interactive "scan docs/ and ask which target + regions" flow lives in the
  requirement-manager skill, not the engine (the engine is headless-safe).

## HOW — Acceptance (= tests)
AC-1
  Given  a page with `nav`/`stats` markers
  When   `site --attach` runs twice
  Then   the second run leaves the file byte-identical and authored prose intact
AC-2
  Given  a repo with no git remote
  When   `site --attach` injects `nav`
  Then   it exits 0 and emits no GitHub link
AC-3
  Given  an absent `--attach` target
  When   `site` runs
  Then   it scaffolds a full page with the regions + the placeholder-hero marker
AC-4
  Given  a generated site page
  When   its `stats` region is edited to differ from a fresh render
  Then   `map --check` exits non-zero and names the page (exits 0 before the edit)
AC-5
  Given  `docs/` present and no `--no-site`
  When   `init` runs
  Then   `docs/architecture.html` exists with engine regions; `--no-site` skips it

## WHERE — Current implementation
- `cmd_site`, `_render_region`, `_inject_region`/`_extract_region`, `_git_remote_web_url`,
  `_site_default_target`, `_site_pages_bootstrap`, the `cmd_init` hook, and the `_map_check`
  site branch in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)
```

- [ ] **Step 2: Verify the gate sees it linked**

Run: `python scripts/reqmap.py check`
Expected: `0 errors` (every `# implements: REQ-SITE-026` tag resolves; the requirement has members). Test-link integrity: the `tested-by` is satisfied by the `Site` class header — add `# tested-by: REQ-SITE-026` to the `Site(unittest.TestCase)` class line if not already present.

- [ ] **Step 3: Commit**

```bash
git add plugin/requirements/REQ-SITE-026.md
git commit -m "docs(site): add REQ-SITE-026 requirement"
```

---

## Task 11: SKILL.md "Project site" section + CLAUDE.md line

**Files:**
- Modify: `plugin/skills/requirement-manager/SKILL.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add the SKILL.md section** (document the interactive flow + engine contract)

Append a section to `SKILL.md` describing: run `reqmap.py site --detect`; ask the user which target (existing `docs/architecture.html` / bring-your-own path / scaffold new) and which regions (`nav`, `nav,stats`); call `reqmap.py site --attach <path> --regions <...> [--diagram <rel>]`; offer to rewrite the placeholder hero into real prose after scaffolding. Note the engine never prompts and `init` already does a best-effort `nav,stats` pass.

- [ ] **Step 2: Add one line to the CLAUDE.md commands block**

In `CLAUDE.md`, under the commands list:

```
python scripts/reqmap.py site --attach docs/architecture.html --regions nav,stats   # inject/refresh engine-owned regions (links + counts) into a presentation page; scaffolds one if absent. init runs this best-effort.
```

- [ ] **Step 3: Commit**

```bash
git add plugin/skills/requirement-manager/SKILL.md CLAUDE.md
git commit -m "docs(site): document the project-site flow in SKILL.md + CLAUDE.md"
```

---

## Task 12: Version bump + full gate

**Files:**
- Modify: `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin/scripts/reqmap.py`

- [ ] **Step 1: Bump semver in 3 locations** `1.34.0 → 1.35.0`

- `plugin/.claude-plugin/plugin.json` → `"version": "1.35.0"`
- `.claude-plugin/marketplace.json` → top-level `"version": "1.35.0"` AND `plugins[0].version` → `"1.35.0"`

- [ ] **Step 2: Bump `MAP_ENGINE_VERSION`** (line ~85)

```python
MAP_ENGINE_VERSION = "2026-06-14"
```

- [ ] **Step 3: Run the full CI gate (from repo root for versions, from `plugin/` for the rest)**

```bash
python scripts/check_versions.py
cd plugin && python scripts/reqmap.py check && python scripts/reqmap.py map --check && python scripts/test_reqmap.py
```

Expected: `check_versions` → `0 errors`; `check` → `0 errors`; `map --check` → `OK  map is fresh.` (regenerate with `reqmap.py map` and commit if the new requirement shifted the map); `test_reqmap.py` → `OK` (all tests, including the new `Site` class).

- [ ] **Step 4: Regenerate the map if stale, then commit everything**

```bash
cd plugin && python scripts/reqmap.py map
git add plugin/.claude-plugin/plugin.json .claude-plugin/marketplace.json plugin/scripts/reqmap.py plugin/requirements/_map.* docs/map.html docs/architecture.html
git commit -m "chore(site): bump to 1.35.0 + MAP_ENGINE_VERSION; regenerate map (REQ-SITE-026)"
```

---

## Self-Review (completed by plan author)

**Spec coverage:** attach mode (T5), scaffold mode (T4,T5), markers/idempotency (T2,T5), regions NAV+STATS (T3) [COMMANDS/LAYERS explicitly deferred per the v1 scope note — spec §3.4], link-only diagram + grep anchor (T9), plain anchors (T3), graceful degradation (T3,T5), init hook + opt-out + Pages bootstrap (T7), region-only gate (T8), REQ-SITE-026 (T10), SKILL/CLAUDE docs (T11), versioning + CI (T12). Skill interactive flow is documented (T11) and intentionally out of engine scope.

**Placeholder scan:** SITE_TEMPLATE (T4) references a concrete committed file with an explicit transformation recipe — not a vague placeholder. No TBD/TODO remain.

**Type consistency:** `cmd_site(reqs, members, reqs_dir, root, attach, regions, diagram, detect)` used consistently across T5/T6/T7. `_render_region(name, ctx)` and `_site_context_from_data(data, repo_url, map_ok, diagram_rel)` consistent across T3/T5/T8. `_site_default_target(root)` consistent across T5/T7/T8. `regions` is always a list inside the engine (argparse splits the comma string in T6).

**Deferred to a follow-up plan:** `COMMANDS`/`LAYERS` as engine-owned regions + `--regions commands,layers`.
