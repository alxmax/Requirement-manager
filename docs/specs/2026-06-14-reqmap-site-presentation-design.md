# Design — `reqmap.py site`: engine-maintained project presentation page

- **Date:** 2026-06-14
- **Status:** Approved (brainstorm), pending spec review
- **Requirement:** `REQ-SITE-026` (new; `depends_on: REQ-PAGES-021, REQ-MAP-007, REQ-VIEWER-007`)
- **Audit:** Senate `2026-06-14_152646-reqmap-site-landing-page` — verdict **MODIFY**; all blocking conditions folded into this design.
- **Demo:** the page prototype (removed after implementation; markup now in `SITE_TEMPLATE`, `plugin/scripts/reqmap.py`).

## 1. Problem

The user wants a project presentation page in the style of `docs/architecture.html` — with top-bar links (Live Map ↗ / Diagram ↗ / GitHub ↗) — that is **generated and kept current by the requirement-manager plugin**, including via `init`. The page must look authored (architecture.html quality) yet never drift from the code.

The tension: `reqmap.py` is a deterministic, stdlib-only, headless engine (runs in `init`, pre-commit, CI). It cannot author bespoke prose and cannot prompt interactively. A polished, repo-specific narrative is authoring work the **AI skill** does.

## 2. Resolution — two layers

| Layer | Role | Interactive? |
|---|---|---|
| **Engine — `reqmap.py site`** | Deterministic. Injects marker-bounded regions into a target HTML; scaffolds a default page when none exists. Reuses `REQ-PAGES-021` machinery. | No (flag-driven, headless-safe) |
| **Skill — requirement-manager** | Scans `docs/`, asks the user which target + regions, then calls the engine with flags. Optionally rewrites the placeholder hero into real prose. | Yes (AI) |

**Principle:** the engine never owns your page — only the content between its markers. Authored prose is preserved across every regeneration.

## 3. Engine: `reqmap.py site`

### 3.1 Interface

```
reqmap.py site --attach <path.html> [--regions nav,stats,commands,layers] [--detect]
reqmap.py init [--no-site]    # --no-site opts out of the init site step (§5)
```

- `--attach <path>` — target HTML (bring-your-own; only its marked regions are edited).
- `--regions` — comma list of regions to inject. **Default: `nav`.**
- `--detect` — scan `docs/` and PRINT findings + the suggested command; writes nothing. (The skill calls this to inform its questions.)
- No `--attach` and not `--detect` → no-op + one-line hint (no magic target).
- `--no-site` is an **`init`** flag (not a `site` flag) — it skips the `init`→`site` step (§5).

### 3.2 Two modes

1. **Attach mode** — target exists → inject/refresh only the marked regions.
2. **Scaffold mode** — target absent → write a full default presentation page (theme + all regions + a placeholder hero), then it behaves as a normal hybrid page.

### 3.3 Marker mechanism (idempotent, prose-safe)

Paired markers, in the existing `<!--REQMAP_DATA-->` family:

```html
<!--##REQMAP:NAV##-->   …engine-owned…   <!--##/REQMAP:NAV##-->
```

- Markers present → replace **only** the text between open/close. Content outside is byte-preserved.
- Markers absent on first `--attach` → insert the region once at a sensible anchor (`NAV` immediately after `<body>`); thereafter refresh in place.
- Re-running with no underlying change produces a **byte-identical** file (timestamps, if any, live on a single stripped line).

### 3.4 Regions and their data sources

| Region | Content | Source |
|---|---|---|
| `NAV` | Live Map ↗, Diagram ↗, GitHub ↗ | `git remote get-url origin` (normalized to web URL) + known artifact paths |
| `STATS` | requirement / confirmed / command / layer / edge counts, versions | `_map.json` + `requirements/` |
| `COMMANDS` | registered subcommands + one-liners | argparse registry |
| `LAYERS` | bus / feature / need + member IDs | requirement frontmatter |

`NAV` is the minimal, maximally portable region — it imposes no layout and attaches to arbitrary HTML. `STATS/COMMANDS/LAYERS` assume the target has slots and are intended for the scaffolded/owned page.

### 3.5 Scaffold template

The default full page is an **inline template string constant** in `reqmap.py` (NOT a second vendored file) — the region fragments and the full-page shell are the same strings assembled in code. This keeps the engine hermetic/stdlib and answers the Senate's "no second maintained template" condition (Musk).

**Placeholder hero** (the one authored region the scaffold fills): repo name (from dir/remote) + a generic line (*"Single source of truth for requirements — keep specs, code, and intent in sync"*) + an "Open the live map ↗" CTA + a visible `<!-- author me -->` marker. The skill offers to rewrite it into real prose after scaffolding.

### 3.6 Graceful degradation (Senate: Dimon/Socrate, blocking)

| Condition | Behavior |
|---|---|
| No git remote / git absent | omit the GitHub link; no crash |
| `_map.html` / diagram artifact missing | omit that link/tab |
| Target HTML missing, scaffold not requested | no-op + hint |
| Non-git / headless / CI / non-TTY | fully deterministic, no prompt |

- **Link-only diagram** — the engine only references an excalidraw HTML if present; it NEVER imports or execs `excalidraw_builder.py` (Senate: Confucius/Musk, blocking — preserves the CLAUDE.md "excalidraw fully independent of reqmap.py" invariant). Anchor: `grep reqmap.py` for the builder → 0 matches.
- **Plain anchors, not `file://` iframes** (Senate: Dimon/Socrate/Musk, blocking — Chromium blocks cross-`file://` iframes, which would silently blank a tab). Links use `<a target="_blank">`.

## 4. Skill: interactive flow (requirement-manager SKILL.md gains a "project site" section)

1. Run `reqmap.py site --detect` (or scan `docs/` directly): what presentation/diagram/map files exist?
2. Ask the user: **which target** (existing `architecture.html` / `index.html` / bring-your-own path / scaffold new) and **which regions**.
3. Run `reqmap.py site --attach <path> --regions <...>`.
4. If scaffolded, offer to rewrite the placeholder hero into real prose.

## 5. `init` integration (best-effort; deliberate override of Senate Aurelius advisory)

After `cmd_map`, a best-effort site step:

- `docs/architecture.html` **exists** → attach/refresh the `nav` region in place.
- `docs/architecture.html` **absent** → **scaffold it**: write `docs/architecture.html` (full hybrid shell) + `docs/index.html` (redirect) + `.nojekyll` so GitHub Pages and the existing `docs/map.html` publish (`REQ-PAGES-021`) light up.
- **Idempotent** (never clobbers existing files), **best-effort** (a missing remote/artifact never aborts `init`), **opt-out** `--no-site`.

Rationale for the override: the user explicitly wants `init` to produce the page. Safety is preserved by best-effort + idempotency + opt-out, satisfying the spirit of the Senate's "don't let site break the bootstrap" concern.

## 6. Publish & staleness gate

- The page lives in `docs/` (committed, like `docs/map.html`).
- `map --check` extends to assert the **marked regions** match a fresh render — a **region-only diff**, so authored prose is exempt; the volatile timestamp line is stripped; **file-absent = not stale** (consumers who don't keep a site pass). Mirrors the existing `docs/map.html` gate exactly.

## 7. Testing (`test_reqmap.py`)

1. **Idempotency** — two consecutive `site` runs on an unchanged repo → byte-identical output.
2. **Prose preservation** — content outside markers is untouched after a refresh.
3. **No-remote degradation** — `site` in a repo with no `origin` exits 0, page omits the GitHub link, `init` completes.
4. **Region-only staleness** — `map --check` exits 1 when a marked region is stale, exits 0 when only out-of-marker prose changed.
5. **Scaffold mode** — absent target → full page written with all default regions + placeholder hero.
6. **Independence anchor** — `grep` proves `reqmap.py` never imports/execs `excalidraw_builder.py`.

## 8. Versioning & CI

- Bump plugin semver in 3 places (`plugin.json`, `marketplace.json` ×2) — engine + SKILL.md both change.
- Bump `MAP_ENGINE_VERSION`.
- CI gate unchanged: `check_versions.py` → `reqmap check` → `map --check` → `test_reqmap.py`. The new requirement `REQ-SITE-026` must pass the link-sync + test-link gates (needs `implements:` + `tested-by:` tags).

## 9. File touch list

- `plugin/scripts/reqmap.py` — `cmd_site`, region renderers, scaffold template constant, argparse wiring, `cmd_init` hook, `_map_check` extension, git-remote normalizer.
- `plugin/scripts/test_reqmap.py` — tests from §7.
- `plugin/requirements/REQ-SITE-026.md` — new requirement.
- `plugin/skills/requirement-manager/SKILL.md` — "project site" section (interactive flow).
- `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — semver bump.
- `CLAUDE.md` — document the `site` command + the engine/skill split (one line in the commands block).

## 10. Out of scope (YAGNI)

- AI prose authoring inside the engine (skill-only).
- Deterministic excalidraw rendering from `_map.json` (dropped per Senate — preserves skill independence).
- Bespoke per-repo theming beyond the one inline template (the skill / a later frontend-design pass can restyle the authored regions).
