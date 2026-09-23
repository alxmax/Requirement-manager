# Project site (`reqmap.py sync --attach`)

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

`sync` keeps a project presentation page (by default `docs/architecture.html` at the git
root) current by injecting **engine-owned, marker-delimited regions** and preserving the
authored prose between them. It is deterministic and never prompts — the *interactive*
part is your job as the skill.

**When the user wants a project/landing/architecture page, or to refresh one:**
1. Ask the user **which target** — the existing `docs/architecture.html`, or a
   bring-your-own HTML path.
2. Run `python scripts/reqmap.py sync` (from the dir where `requirements/` lives). It
   refreshes `docs/architecture.html` when that file exists, and only the marked regions
   (`<!--##REQMAP:NAV##-->…<!--##/REQMAP:NAV##-->`, `…:STATS…`); your prose is untouched.
   For any other page, `sync --attach <path>`. `nav` and `stats` are refreshed together.
3. To CREATE a page that does not exist yet, run `sync --attach <path>` or `init`: both
   scaffold a small default page (regions + a placeholder hero marked `<!-- author me -->`).
   `init` also writes `docs/.nojekyll` and a `docs/index.html` redirect when they are
   absent; an existing `index.html` is never overwritten.
4. If you scaffolded, offer to rewrite the placeholder hero into real prose for the repo.

Regions and their sources: `nav` = Live Map / GitHub links (a sibling `map.html`, the git
remote or `REQMAP_REPO`; each emitted only if its target resolves); `stats` =
requirement/confirmed/layer/edge counts + engine version (from the requirement graph).

`init --no-site` skips the site step. The rendered map is never copied into `docs/`
(ADR-0034): a published `docs/map.html` is built where it is published, and a `sync`
run after that copy makes the page's `nav` link to it.
