# Project site (`reqmap.py sync --attach`)

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

`sync --attach` keeps a project presentation page (e.g. `docs/architecture.html`) current by
injecting **engine-owned, marker-delimited regions** and preserving the authored prose
between them. It is deterministic and never prompts — the *interactive* part is your job
as the skill.

**When the user wants a project/landing/architecture page, or to refresh one:**
1. Ask the user **which target** — an existing `docs/architecture.html`, an `index.html`,
   or a bring-your-own HTML path.
2. Run `python scripts/reqmap.py sync --attach <path>` (from the dir where `requirements/`
   lives). It refreshes only the marked regions
   (`<!--##REQMAP:NAV##-->…<!--##/REQMAP:NAV##-->`, `…:STATS…`); your prose is untouched.
   `nav` and `stats` are refreshed together — there is no per-region flag.
3. To CREATE a page that does not exist yet, run `python scripts/reqmap.py init`: its
   best-effort site pass scaffolds a full default page (theme + regions + a placeholder
   hero marked `<!-- author me -->`) at `docs/architecture.html`. `sync --attach` only
   refreshes a file that is already there.
4. If you scaffolded, offer to rewrite the placeholder hero into real prose for the repo.

Regions and their sources: `nav` = Live Map / Diagram / GitHub links (from `git remote` +
artifact paths, each emitted only if its target resolves); `stats` = requirement/confirmed/
layer/edge counts + engine version (from `_map.json`). The engine **only links** an
excalidraw diagram — it never generates one (the excalidraw-diagram skill stays independent).

`init` already runs a best-effort site pass (`nav,stats` into `docs/architecture.html`,
scaffolding it if absent); `reqmap.py init --no-site` opts out. The gate's built-in
freshness check flags the page stale if its `stats` region drifts (the `nav` region is exempt — it embeds the
fork-specific repo URL).
