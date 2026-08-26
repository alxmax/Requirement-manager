# Changelog

## plugin `v2.28.1` — 2026-08-27

**`dupes` reported a requirement and its own test suite as probable duplicates.** On a consumer corpus that keeps one requirement per script *and* one per test module (Senate: `SCRIPTS-X` / `SCRIPTS-TEST-X`), 9 of 32 flagged pairs were exactly that — scores 0.42–0.60, near the top of the list — and the reviewer learned to scroll past the report. The two share vocabulary by construction, and the corpus already says so: the test requirement's `implements` file is the other's `tested-by` file.

- `cmd_similar` now takes the member map (`dupes` passes it from the scan) and skips a pair linked by `tested-by`, printing `skipped N pair(s) linked by tested-by` instead. Without a member map (library callers, the existing tests) behaviour is unchanged. `REQ-SIMILAR-016` +AC-7; Senate corpus 32 → 23 pairs, and every pair still involving a test requirement is a genuine cross-link (e.g. two different test suites), not a suite reported against its own subject.
- `MAP_ENGINE_VERSION` → `2026-08-27`.

## plugin `v2.28.0` — 2026-08-25

**The rest of the scan-evidence matrix, run the same day: five foreign repositories, five language families, ten engine fixes.** Run 6 (`v2.27.0`) was one consumer. These are strangers: `madler/zlib` + `curl/curl` (C/C++, 4,449 files), `excalidraw/excalidraw` (TS/React), `docker/awesome-compose` (Dockerfiles, compose YAML, 11 app languages), `gin-gonic/gin` + `encode/httpx` (Go, Python), `danielmiessler/fabric` (396 Markdown prompt files). Each run: inventory → `coverage` → `plan` → `draft` → `gate` → `next`/`health`/`dupes` → a native-comment-style tag probe per language → edge probes. Zero crashes on the protocol itself; zero false-positive tag hits across all seven repos (`TAG_RE`'s boundary guard held); the C/C++ scanner passed 16/16 probes (block comments, `#define` lines, CRLF, Latin-1 bytes). What broke was everything around the scanner.

- **`plan` produced 0 candidates for zlib, none for gin's 99 Go files, none for awesome-compose's 35 Dockerfiles — and said "wrote plan (0 candidates)", exit 0.** Its file filter was a five-extension private list while `draft` used the full scan set, so the documented "run `plan` before `draft`" preview silently omitted most of what `draft` then wrote (excalidraw: 663 planned vs 687 drafted). Every scannable code file is now a candidate; a language without a parser carries empty facts. zlib: 0 → 101 candidates. Candidates also carry `is_test` (a `tests/` segment, `test_*`, `*_test.go`, `*.spec.ts`) — httpx's plan was 37/60 test files with nothing marking them. `REQ-CANDIDATES-009` +AC-7.
- **`plan`'s Python facts stopped at module level**: `httpx/_client.py` showed 3 helpers and hid its 78 public methods. Public methods of top-level classes are now signatures (`def Client.get(url)`).
- **`draft` wrote the identical TODO stub for every code file** while `plan` had already read the file's signatures — the run-2 agent found `vector.ts` with 15 extracted exports and a draft that used none. A code proposal's WHERE section now lists the observed surface (module docstring + up to 12 signatures) as an explicit non-binding hint; the Contract stays a TODO, by contract. `REQ-EXTRACT-008` +AC-6, and its extension list — stale since the scan widened — now says "every scannable code file".
- **`dupes` right after `draft` was noise at scale**: 6,340 "probable duplicate" pairs for fabric's 638 drafts, 2,055 for curl, 1,748 for excalidraw — all template text. Requirements whose Contract bullets are all still `TODO:` are skipped with a count line; nothing authored, nothing to compare. `REQ-SIMILAR-016` +AC-6.
- **`dupes | head` died with `OSError: [Errno 22]` on Windows** (no SIGPIPE). New `REQ-PIPE-046`: the CLI entry (`_run_cli`) turns a closed reader — `BrokenPipeError`, `EPIPE`, `EINVAL` — into a quiet exit 0; every other `OSError` still propagates.
- **`classify_prose` matched `README` case-sensitively**, so fabric's one `readme.md` was auto-drafted while 37 `README.md` siblings were correctly left alone. Case-insensitive now. `REQ-PROSE-024`.
- **A prompt corpus written with `#` for every section got "(no section headings detected)"** on 204 of 255 drafts — the scaffold only read `##`. With no H2 anywhere, later H1s are the sections. `REQ-PROSE-024`.
- **Scan reach**: excalidraw's only stylesheet format (`.scss`, 82 files) and awesome-compose's `.cs`/`.vue`/`.php` apps were invisible to every command. Added `.scss .sass .less .vue .svelte .mjs .cjs .mts .cts .cs .php .rb .kt .kts .swift .scala .ex .exs .dart .toml`; `ORPHAN_CODE_EXTS` grows by the program languages. `CORE-SCAN-002` notes.
- **`v2.27.0`'s unscanned-tag check skipped every dotfile**, so a tagged `.env` stayed silent — the run-3 agent caught it on the check's first outing. Only `.git*` and `.reqmap*` are exempt now. `REQ-UNSCANNEDTAG-045`.
- Recorded, not fixed (design, documented in each run's TODO entry): `TAG_RE` is context-free by design, so a tag inside a YAML string value, a Dockerfile heredoc, or plain prose counts — three probes showed it; `.rst/.txt/.adoc/.ipynb/.mdx` and curl's 2,066 extensionless `tests/data/test###` fixtures stay outside the scan; `gate --cache` is slower than plain `gate` on its cold run (it builds the cache) and faster warm.

## plugin `v2.27.0` — 2026-08-25

**First scan-evidence run on a real consumer (Management_Dashboard: NestJS + Next.js, 288 tracked files — TS/TSX, SQL, shell, Dockerfiles, Caddyfile, Prisma, YAML, JSON, Markdown). Four engine defects, all fixed here; the corpus-side findings went back to the consumer.**

- **Tags in file types the scan never read were silently not members.** `Caddyfile` and `apps/api/prisma/schema.prisma` both carried `implements:` tags; neither type was scanned, so two requirements lost their members with the gate green. Two fixes, one local and one general: `.prisma`, `.graphql`, `.proto`, `Caddyfile`, `Jenkinsfile`, `Procfile`, `Vagrantfile` and any `Dockerfile.<variant>` (`Dockerfile.converter` was the third invisible tag) are now scanned — and new `REQ-UNSCANNEDTAG-045` makes the next case visible: `gate` warns (warn-only, fail-open outside git) when a tracked, non-scannable, non-binary file under 1 MB carries a tag. Dotfiles, `_`-prefixed files, `.reqmapignore` matches and the SSOT dir are skipped (this repo's own `.reqmapignore` quotes an illustration tag in a comment). Consumer members: 282 → 286.
- **62% of the consumer's gate time was `os.path.realpath`**: `_prune_dirs` resolved every directory on the walk to find the SSOT dir — 34,596 calls across three walks for a 216-file scan, driven by a 4,900-folder upload directory. It now resolves only a directory whose *name* matches the SSOT dir's (same exclusion, contract unchanged), and a `.reqmapignore` pattern ending in `/**` or `/*` prunes the walk instead of filtering every file under it (identical results by construction). Gate on the consumer: 11.2 s → 4.1 s; 0.6 s once `apps/api/storage/**` is ignored.
- **`map --check` failed on the consumer for `_map.json` whose only difference was `engine_version`** — nodes, edges and todos identical. Updating the vendored engine alone no longer makes a committed map stale: `engine_version` joins `repo` and `generated:` in the freshness-diff exclusions (`REQ-MAP-007`). The next `sync` still refreshes it.
- **`next` listed `CLAUDE.md` and `TODO.md` as "Untagged files"** with advice to run `draft` — which never drafts them, because `REQ-PROSE-024` puts meta prose in the *ignore* bucket. The bucket now honours that bucket (`REQ-NEXT-013`); sync-only prose (`README`, `docs/`) is still listed, because it *can* carry a `generated-from:` tag.
- Also seen on the consumer, not engine defects: its committed `_findings.md` was stale (9 vs 10 live) — caught by `v2.26.0`'s new check on first contact; 42/44 requirements are `draft` with 0 confirmed (the skill's triage path); its CI has no reqmap gate step; `package-lock.json`/`tsconfig`-class JSON was the only JSON present, so no JSON tagging convention is needed on this evidence.

## plugin `v2.26.0` — 2026-08-25

**A committed `_findings.md` that said "0 open" for eleven weeks — and two smaller lies the tooling told during the same audit.** `v2.25.1` regenerated the file by hand; this release makes that unnecessary, and closes the two follow-ups the audit left open.

- **`_findings.md` is now a derived view like `_map.*`.** `map` (and therefore `sync`) rewrites it when it already exists, and `map --check` names it stale when the committed copy differs from a fresh render. Neither ever *creates* it: a repo opts in by running `findings` once and committing the result, exactly the file-absent convention `_map.*` and `docs/map.html` already follow. For a consumer who committed one and never re-ran `findings`, `map --check` will newly fail once — the fix is `reqmap.py sync`. `REQ-FINDINGS-010` +AC-6/AC-7; `_render_findings()` is the shared renderer.
- **`next` stops calling a scan-scope problem an orphan.** The narrow default invocation in this repo (no `--code ..`) lists `REQ-SELFGATE-039`, `REQ-REPRO-041` and `REQ-STALEENGINE-043` as "confirmed, no code" — their members are `.github/workflows/ci.yml`, `.githooks/pre-commit` and friends, one directory above the scan root. The committed `_map.json` records those members, so `next` now reads it and adds a note under the Orphans bucket naming one of them and suggesting `--code <dir>`. The item stays in the bucket (it *is* an orphan for that scan); only the puzzle goes away. `REQ-NEXT-013` +AC-10.
- **`new` warns on a same-area number collision.** This corpus already has `REQ-MAP-007`/`REQ-VIEWER-007`, `REQ-SITE-026`/`REQ-DOCBUNDLE-026` and `REQ-DRIFTIMPACT-035`/`REQ-REGISTRYLAG-035`. Ids stay unique by their full text, so nothing was ever broken — but two requirements answering to "007" get confused in conversation. `new` (and `new --from-todo`) now prints a `WARN` naming the existing id when the area and `NNN` both match; different areas (`CORE-PARSE-001` beside `NEED-SSOT-001`) stay silent. Exit code unchanged. The existing pairs are deliberately **not** renumbered: an id is referenced from code tags, the lock, the map, ADRs and every CHANGELOG entry, so a rename costs more than the ambiguity does. `REQ-NEW-004` +AC-5.
- `REQ-TRANSLATE-044` promoted `baseline` → `confirmed`: both verify-intent questions from `v2.25.0` are answered (stopword lists stay small; the language set stays `ro`/`en` until a second consumer language exists) and folded into its Notes. The corpus is now 48/48 confirmed with no open findings, so the committed `_findings.md` reads "0 open" and this time that is true.
- Viewer baked fixture re-synced to the three rewritten contracts; `_map_viewer.html` rebuilt. `MAP_ENGINE_VERSION` → `2026-08-25.2` (the new `check_engine_bump.py` gate saw the engine diff and required it).

## plugin `v2.25.1` — 2026-08-25

**Two engine releases told every consumer they were up to date.** `v2.24.0` (the `redundant-modal` lint check) and `v2.25.0` (`translate`) both changed `reqmap.py` without moving `MAP_ENGINE_VERSION`, which stayed at `2026-08-20.2`. That constant is the only thing a seeded copy — and `check/engine_staleness.py` in the published action — can compare, so a consumer on the 08-20 engine was reported current while missing both features. Nothing checked the rule; it lived in `CLAUDE.md` as a sentence.

- `MAP_ENGINE_VERSION` → `2026-08-25`. New `scripts/check_engine_bump.py` makes the rule mechanical: any diff to `plugin/scripts/reqmap.py` must also change the version line. CI runs it against `HEAD~1` in `gate-and-tests`; the dev pre-commit hook runs it on the staged diff. Own suite (`scripts/test_check_engine_bump.py`) seeds a throwaway git repo for both modes.
- **`SKILL.md` and `SKILL.universal.md` still told consumers to pin `check@v1`** — the gate-only alias frozen at v2.1.0 — three releases after `README.md`/`CLAUDE.md` moved to `@v2`, and right above prose describing `@v2`-only inputs (`lint:`, `freshness:`). `check_versions.py`'s `ACTION_REF_FILES` did not include the skill files, so its alias axis never saw them. Both now say `@v2` and both are in the list (7 references asserted, was 5); a regression test pins a lagging skill file as a failure.
- `translate` now hands the prompt to `claude -p` on stdin instead of as one argv element — a whole requirement in a single argument would hit Windows' ~32 KB command-line ceiling on a large corpus (largest here is ~9.5 KB today; the limit was silent).
- `lint`: the 15 `redundant-modal` warnings left visible-but-unfixed in `v2.24.0` are now fixed (69 `shall`/`must` clauses across 13 Contract sections rewritten in plain present tense — wording only, no contract change; lock advanced with `--accept-drift`). The two `file-spread` warnings (`REQ-REVIEW-022`, `REQ-SELFGATE-039`) are exempted with the reason in each Notes section: spanning those files *is* the capability. `lint --strict` now reports 0 warnings on this corpus.
- The viewer's baked demo fixture (`app/src/lib/data.js`) mirrors `REQ-INIT-012`'s rewritten clause, so `gate`'s viewer-data-sync check is silent again; `_map_viewer.html` rebuilt from it (`npm run build:viewer`).
- `_findings.md` regenerated — the committed copy dated from v1.12.0 and said "0 open" while `REQ-TRANSLATE-044` carries two open verify-intent questions.
- Repo-root `.reqmapignore` now excludes `.pytest_cache/`, `.ruff_cache/`, `.superpowers/` and `diagrams/` (all gitignored): a local `next`/`coverage`/`health` reported 47 "untagged files" CI could never see.
- Five `open(...).read()` sites in the engine use a context manager; four stale "`npm run smoke` is not wired into CI" comments (`.reqmapignore` ×2, `app/CLAUDE.md`, `REQ-VIEWER-007`) corrected — the `artifacts` job has run it since v2.23.0.

## plugin `v2.25.0` — 2026-08-25

**A consumer's viewer speaks Romanian and refuses to translate your requirements — until every requirement is in the reader's second language.** `v2.23.0` drew a hard line: the locale toggle translates UI chrome only, never requirement content, because translating the artifact under review live would put words in the author's mouth. That line was right for a mixed-language reader who mostly understands the source — it fails completely for a reviewer who does not read the corpus's language at all.

`reqmap.py translate [--to ro|en]` adds the one exception, kept manual and opt-in on purpose: it is the ONLY subcommand that shells out to an external LLM (`claude -p`), and this engine's `gate`/`sync`/`lint`/`map`/pre-commit path stays exactly as `claude`-free as before — nothing above calls it.

- Detects the corpus's majority language (Romanian diacritics, else a stopword-frequency vote); a per-file `lang: ro|en` frontmatter value overrides detection for the rare misclassified file.
- Caches results in `requirements/_i18n/<locale>.json`, keyed by a content hash over title + WHY + Contract + Acceptance — deliberately not `binding_hash()` (Contract+Acceptance only), so a title-only edit still invalidates the cache.
- A structural-fidelity check (backticked spans, numbers, heading/bullet markers must match) gates every cache write; a missing `claude` CLI, a timeout, or a failed check skips that entry with a `WARN` instead of aborting the batch. Cache hits skip the CLI call entirely.
- `map`/`export` inline the cache onto each node **read-only** — a file read, never a `claude` call — so `map --check` in CI stays exactly as deterministic as before.
- The viewer never presents cached text as the author's own: every translated field renders behind a visible "machine-translated, unreviewed" badge (`translatedText()` in `i18n.jsx`), and falls back to the source text whenever no cache entry exists.

`REQ-TRANSLATE-044` carries the full contract (8 ACs, `lint_exempt: ac-count-high` — same reasoning as `REQ-LINTCHECKS-025`: each AC pins one module's behavior).

## plugin `v2.24.0` — 2026-08-24

**A Contract section written in Romanian had "shall" in it — nothing caught that.** The style rule already existed ("Audience & writing level" in `SKILL.md`: plain present tense, no `shall`/`must` — the section already opens with "Every line in this section is binding."), but it was documentation only. A consumer repo's requirement corpus carried the anglicism in 29 files and 261 places before anyone noticed, because `lint` had no check for it.

`lint` gains `redundant-modal`: it flags `shall`/`must` on a Contract clause, same shape as the existing `vague-term` check — closed word list, backticked spans stripped first, one finding per distinct term, `warn` severity. Running it against this repo's own corpus surfaced 17 pre-existing hits, left as advisory (not fixed in this release — the check's job is to make them visible, not to silently rewrite prose).

`REQ-LINTCHECKS-025` documents the check with AC-10; `REQ-LINT-014`'s check-list note is updated to match.

## plugin `v2.23.0` — 2026-08-21

**The viewer speaks Romanian, and refuses to translate your requirements.** The self-contained `_map.html` had exactly one language, and the interesting part of adding a second is not the dictionary — it is the line the dictionary must not cross.

A locale control sits beside the theme toggle in the top bar. It translates **UI chrome only**: nav, tab labels, section headers, buttons, empty states.

Two categories are deliberately left alone:

- **Requirement content.** Id, title, intent, contract clauses, acceptance criteria and member paths stay in the language their author wrote them in. They are the artifact under review; translating them would put words in the author's mouth and break the match with the `.md` file on disk.
- **The engine's own vocabulary.** `confirmed`, `in-progress`, `draft`, `orphan`, `deprecated`, `bus`/`feature`/`need`, and the ERROR/WARN/REVIEW severities are literal values in the requirement files and in the gate's output. A reader who sees a translated status here and `status: confirmed` in the file has been handed a puzzle, not a translation.

Implementation notes, because the shape was chosen against a known-bad alternative:

- i18n is authored **into the JSX** (`app/src/lib/i18n.jsx` plus `t()` call sites) — not applied to the built bundle as a DOM overlay. A post-hoc patch of the built file lives outside every diff the build tracks and any rebuild silently wipes it.
- The dictionary is keyed by the **English source string**, so the JSX stays readable in English and a missing entry degrades to English instead of to `nav.map.label`.
- Split-node headers like `What — Contract … normative` are translated as separate strings, which is why the leading-space trap that bites exact-match DOM dictionaries cannot occur here.
- The choice is remembered per reader via `localStorage` (guarded for SSR and for browsers that throw on the accessor) and is **never written into the generated file** — `_map.html` stays byte-identical regardless of what anyone last selected.

Six assertions were added to the SSR smoke, the app's only automated check, and they test both directions: that a section header translates, and that the requirement's title, contract and status do **not**. `REQ-VIEWER-007` gains the contract clauses and AC-6.

## plugin `v2.22.0` — 2026-08-20

**A consumer's engine could rot for a year and CI would never say so.** `warn_if_stale` — the engine's own "your vendored copy is behind" notice — only fires when `CLAUDE_PLUGIN_ROOT` is set, which happens inside a Claude Code session and nowhere else. CI, the one place that runs on every push, was silent by construction. The cost is invisible and specific: checks that shipped after the vendored copy simply do not run, and the build stays green while covering less than the caller thinks.

The fix could not go in the engine. A stale `reqmap.py` does not contain the check that would report it stale, so the detector has to run from something the consumer does not vendor: the action.

`check@v2` now runs `check/engine_staleness.py` as its first step. It reads `MAP_ENGINE_VERSION` from the vendored engine and from the engine in the action's own checkout, and when the vendored one is older emits a `::warning::` annotation naming both versions — on the run, not buried in the log:

```
::warning title=Stale reqmap engine::vendored reqmap.py is stale (2025-01-02 < action 2026-08-20.2) - re-seed it ...
```

- New input `stale-engine`: `warn` (default), `error` (fail the build on it), `off`.
- Compared against the ref the caller pinned, so an exact-SHA pin is measured against that SHA's engine — the engine they asked for.
- Fails open in every mode: an unreadable or absent version, or any unexpected internal error, prints a skipped-probe note and exits 0. The probe is never itself the reason a gate run goes red.

**Why this stayed `@v2`.** The major-bump rule is about a default-on step that can newly FAIL a green build — that is what took `freshness` and `lint` to v2. This step is warn-only and exit-neutral, so no existing pin changes verdict. And a `@v3` would have stranded exactly the consumers this exists to reach: the ones who pinned once and never came back.

The probe never runs in this repo's own CI (this repo *is* the engine), so `scripts/test_engine_staleness.py` — 10 tests, wired into both CI test surfaces — is the only thing exercising it before it ships. Filed as `REQ-STALEENGINE-043`.

## plugin `v2.21.0` — 2026-08-20

**The gate read every file three times.** `scan_members`, `scan_ac_verifies` and `scan_test_levels` each walked the whole tree and opened every file. On a 10,000-file tree that was 3.06s + 2.76s + 2.81s of the gate's 8.49s — the scan was essentially its entire runtime, performed three times. The benchmark added in v2.20.0 was written to publish a number and ended up explaining one.

`scan_all` now reads each file once and runs all three extractions on the same lines:

| | before | after |
|---|---|---|
| one walk, all extractions | — | **2.53s** |
| `scan_members` alone | 2.62s | 2.62s |
| `gate` | 8.49s | **2.46s** |
| scan + gate, end to end | ~11s | **~5s** |

It is not three loops glued together — that would have been the risky version, because the three scanners have genuinely different masking rules (fences and indent blocks for prose, string literals for `.py`, a backtick strip that only the levelled scan applies):

- The walk itself moved into one `_walk_code` generator. Three byte-for-byte copies of that loop is how they drifted apart in the first place.
- `_scan_file_tags` gained an optional `lines` argument, so a caller that already read the file hands the content over instead of re-reading it. Every existing caller is unchanged.
- The two coverage scanners' identical per-line masking became **one** pass feeding both regexes, preserving the asymmetry exactly: only the levelled scan strips backticked spans first, so a documented *example* of a levelled tag still does not register as real coverage.

**The safety argument is a test, not a reading of the diff:** `scan_all`'s three results must equal what the three scanners return separately — asserted against both a mixed fixture (prose fences, a `.py` docstring, a backticked example, a `.ts` file) and against this repo's own corpus, where every masking rule is exercised by files that actually use them.

`cmd_check` takes the coverage maps as optional arguments and computes them itself when absent, so tests and any embedding tool keep working untouched. `--cache` stays on `scan_members` alone: it is off on the CI path this speeds up, and duplicating its invalidation rules would trade a measured win for a correctness risk.

**Bookkeeping:** the `v2.20.0` tag was cut at the merge of the first of that release's three stacked PRs, so it does not contain the `artifacts` job, the standing-warning fixes, or `REQ-TRACKED-042` — all of which its changelog entry describes. They ship here instead. A released tag is not worth moving; the entry above it is the correction.

`MAP_ENGINE_VERSION` → `2026-08-20.2`.

## plugin `v2.20.0` — 2026-08-20

**Two ways hostile-looking text broke the map, and a number for "does this scale".** `</script>` in a requirement body has had a regression test since v2.3.5. The other two characters named on the roadmap had nothing:

- **U+2028 / U+2029 were emitted raw into the inlined `<script>`.** They end a line in JavaScript but are ordinary characters in JSON, so `ensure_ascii=False` passed them straight through and any engine older than ES2019 read the assignment as an unterminated string — one character in one requirement title killing the entire viewer. Now escaped to ` `/` `, which denote the same characters in JSON, so the parsed graph is unchanged (pinned by a round-trip test).
- **A lone surrogate crashed `map` outright.** A lone surrogate has no UTF-8 encoding, so the write raised `UnicodeEncodeError` and took the whole command down — and with it the gate's map-freshness check. Not a theoretical input: `os.walk` hands back a filename whose bytes are not valid UTF-8 surrogate-escaped, and member paths go straight into the map. `_utf8_safe` now degrades it to U+FFFD for both `_map.json` and `_map.md`; the fast path is a C-level encode that touches nothing, and the per-character walk runs only for a string that genuinely cannot be encoded.

Both were written as failing tests first, then fixed. `REQ-VIEWER-007` gains AC-5 and the escape clause; `REQ-MAP-007`'s AC-7 widens to cover the surrogate case rather than growing an eighth criterion it has no room for.

**A published benchmark** (`scripts/benchmark_scan.py`, numbers in the README). On 10,000 source files and 100 requirements: `scan_members` 3.06s, `gate` 8.49s, map render 0.03s. It was written to publish a number and ended up explaining one — the gate performs **three full walks of the tree**, not one (`scan_members` + `scan_ac_verifies` + `scan_test_levels`, 8.63s combined ≈ its entire runtime). Filed as its own roadmap item: the three scanners have different masking rules, so merging them is a real refactor, not three loops glued together. Deliberately not wired into CI — a shared runner's I/O makes timing assertions meaningless, and a flaky perf gate teaches people to ignore red.

**The gate's two standing warnings are gone, and neither was cosmetic.** Every run printed the same pair. Both turned out to be real, and one of them was the check itself being wrong.

**1. The viewer's demo dataset had drifted from the registry it copies.** `app/src/lib/data.js` carries a hand-authored `BAKED` fixture so the viewer has something to show with no engine present, and 13 of its entries claim to mirror real requirements. Their contract text was **written in the `shall` voice that v2.15 removed from the registry** — so the tool's own demo showcased the style its linter now rejects, and a reader with no engine saw a system that no longer existed. All 13 refreshed from the live `_map.json`, and a new test asserts *this repo's* fixture against *this repo's* registry, so the drift cannot come back silently.

**2. Two of the "drifted" ids were never real, and the check should not have flagged them.** The fixture deliberately invents an orphan (`REQ-SYNC-014`) and a deprecated capability (`REQ-CACHE-014`) so the Risk and Problems tabs have signals to display. Those ids cannot exist in any registry, so comparing them against one produced permanent drift — the check crying wolf about data doing exactly its job. Entries now opt out with `demoOnly:true`, and `check_viewer_data_sync` skips them. The marker is deliberately opt-in rather than a loosening of the rule: an **unmarked** id missing from the registry still reports, because that is the real signal (a requirement renamed out from under the fixture), and a test pins that distinction.

**3. `docs/full_architecture.html` now carries its lineage.** The 99KB architecture poster is exactly the case `REQ-DOCBUNDLE-026` exists for — a whole-system doc built from many requirements, with nothing linking the two — and it was the one large bundle in this repo that had no `generated-from:` tag. `make_full_architecture.py` now stamps `<!-- generated-from: CORE-PARSE-001, CORE-SCAN-002, CORE-DRIFT-003, REQ-CHECK-006, REQ-MAP-007, REQ-VIEWER-007 -->` into the page it generates, scoped to what the diagram actually depicts rather than everything it touches. A contract change in any of the six now lists the poster as needing a redraw.

The tag immediately earned itself: the poster's glossary still explained **`@v1`** as "git tag of the published GitHub Action", three releases after that line moved to `@v2`. `check_versions.py`'s alias axis had not caught it, because the glossary names the bare `@v1` rather than the full `requirement-manager/check@vN` path it matches on.

**`gate` now names members git does not track** (`REQ-TRACKED-042`). The rule it enforces is that a committed generated artifact may depend only on tracked files — break it and the map records members a fresh checkout cannot produce, so `map --check` fails in CI over a file the reader cannot find. That happened twice in one day here (a gitignored subagent worktree, and a Consilium report carrying a real `generated-from:` tag), and both times the local scan could see what CI never would.

Built on **untracked** rather than gitignored, deliberately: it is the property that actually matters — a merely-uncommitted file breaks reproducibility identically — one `git ls-files` call answers both, and it avoids either hand-parsing gitignore semantics or spawning a `check-ignore` per path. Fail-open outside a git work tree (nothing at all, not "every member is untracked"), warn-only, exit code untouched: a consumer repo may tag an ignored file on purpose, and this nudges the choice into the open rather than overruling it.

`MAP_ENGINE_VERSION` → `2026-08-20.1`.


`MAP_ENGINE_VERSION` → `2026-08-20.1`.

## plugin `v2.19.0` — 2026-08-20

**The portability claim gets evidence.** The engine's pitch is "one stdlib-only file, runs anywhere with Python" — and the whole proof was a single CI job on ubuntu with `python-version: "3.x"`. The supported floor was therefore accidental (3.7, because nothing in the code needed more), and `-X utf8`, a convention that exists *specifically* for Windows codepages, had never once run on Windows in CI.

- **Declared floor: Python 3.9** (`MIN_PYTHON`, new `REQ-PYFLOOR-040`). Deliberately the oldest version CI actually runs, not the oldest the code happens to tolerate: 3.7 and 3.8 cannot be installed on current GitHub runners, so promising them would be a claim nothing proves — the exact failure mode this project exists to prevent. `reqmap.py` now refuses an older interpreter before any command runs, with one ASCII line naming the required version, the running version and the fix, and exit 2 — instead of an `AttributeError` from deep inside a command. The check is a pure predicate (`_python_floor_error`) so the floor is pinned by tests on any interpreter; it cannot help below 3.6, where f-strings make the module fail at compile time, and that limit is written down in the requirement's Notes.
- **New `tests` matrix job: 3.9 / 3.12 / 3.13 x ubuntu-latest / windows-latest**, `fail-fast: false`, running every suite (engine, version gate, release notes, cross-tool falsification, Excalidraw builder + tests). Kept separate from `gate-and-tests`, which stays a single authoritative verdict on this repo's requirement corpus — running the gate six times would produce six identical answers.
- **A test asserts the two stay equal**: `MIN_PYTHON` against the oldest quoted Python in `ci.yml`, so raising the floor without moving the matrix (or the reverse) fails the build. It skips cleanly in a seeded consumer repo that has no `.github/` of ours.
- `release` now needs the matrix as well as the gate — a version that fails on Windows or on the floor must not become a tag consumers install. `deploy-map` still needs only the gate, since it republishes `docs/`, which the gate already drift-checks.
- Docs corrected where they promised more than was tested: `check/action.yml`'s `python-version` said "any 3.x works", and README / both SKILL files described the engine without naming a version.

**Committed build artifacts are now re-derived and compared** (new `artifacts` job). Two files here are build output that is nonetheless committed, because the point is that a consumer gets them without a toolchain: `plugin/scripts/_map_viewer.html` (217KB, the Vite single-file build the stdlib engine injects data into) and `docs/full_architecture.html` (99KB, the Excalidraw poster). Nothing checked either against its source, so a change to `app/` or to the generator could ship a viewer that no longer matched the code it was built from — with the repo still green. Both were measured before the check was written and are byte-reproducible: the viewer half is a literal `git diff --exit-code` (the build overwrites the committed file in place), the diagram half builds into a temp dir and compares, because the generator drops a sibling `.excalidraw` and `docs/*.excalidraw` is hard-blocked by `.gitignore`. **The check failed on its own first CI run, correctly**: the committed viewer carried CRLF on the 19 lines it inlines verbatim from `app/viewer.html`, because a Windows checkout hands Vite a CRLF template — while the Linux build emits LF, so the two disagreed byte for byte. `core.autocrlf` had hidden it locally by normalizing on the way in, which is why it could only ever surface in CI. Fixed at the source rather than papered over: `.gitattributes` pins the template and both artifacts to LF, and the Excalidraw builder now passes `newline="
"` on every write (Python's default translates `
` to `os.linesep`, so the same scene produced a different file on each platform). `release` needs this job too, and the whole thing is `REQ-REPRO-041` — split out of `REQ-SELFGATE-039` rather than bolted onto it, because the clarity lint flagged the combined requirement at 8 acceptance criteria: artifact reproducibility fails independently of gate wiring, so it is its own capability. `docs/architecture.html` stays out of scope — it is hand-authored, and its engine-owned regions are already covered by `map --check`.

**The matrix paid for itself on its first run** — three defects that a single ubuntu job structurally could not see:

- **`--since` failed OPEN on Windows.** `_since_changed_files` builds its changed-set from `git rev-parse --show-toplevel`, which always returns the long path form, while the caller's `code_root` can carry an 8.3 short component (`C:/Users/RUNNER~1/...`). `abspath` + `normcase` normalize separators and case but not short-vs-long, so the two sets never intersected: every member dropped out of the changed-set and `gate --since` reported a clean tree **with a dangling tag still in it**. Both sides now go through one `_path_key` (`realpath` then `normcase`), which also fixes the POSIX shape of the same defect — a repo reached through a symlinked path — now covered by a symlink regression test.
- **16 tests never ran in the documented invocation.** `if __name__ == "__main__": unittest.main()` sat mid-file, above `RoadmapSignals` and `ViewerDataSync`, so `python test_reqmap.py` executed it before those classes existed: 478 collected instead of 494. CI runs `-m unittest`, which imports the module fully, so CI never saw the gap. The entry point now stays last.
- **A test leaked the process cwd into its own result.** `cmd_check`'s `code_root` defaults to `"."`, and `test_strict_drift_exits_1` counts DRIFT lines without passing one — so run from `plugin/` it scanned the real corpus, saw a second DRIFT line and failed, while passing from `plugin/scripts/`. Both are invocations `CLAUDE.md` documents. Now hermetic.

`MAP_ENGINE_VERSION` → `2026-08-20`.

## plugin `v2.18.1` — 2026-08-20

**The published Action stops rotting.** `alxmax/requirement-manager/check@v1` was tagged on 2026-06-15 at plugin v2.1.0 content and never moved again — 193 commits behind `main` by the time anyone noticed, while the README kept advertising it as the way to run the gate in CI. Moving the alias was a manual step with nothing to remind a maintainer it existed.

- **The action's line is now `@v2`**, and the bump is deliberate rather than cosmetic: since v2.1.0 the action gained `freshness` (`map --check`) and `lint` (`lint --strict`) steps that both default to `'true'`. Re-pointing `@v1` onto current content would have newly FAILED a consumer build that was green — a stale committed map, or a requirement the clarity lint rejects. Adding a default-on check to an existing pin is a breaking change for the caller, so `@v1` is left frozen exactly where it is: existing pins keep working and keep running the gate-only step list they always ran.
- **The alias moves itself from now on.** `ci.yml`'s `release` job force-moves the major-alias tag onto the commit the current `plugin.json` version is tagged at, on every push to `main` — deliberately outside the "already released, exit 0" shortcut, so a half-failed run or a hand-moved tag self-heals on the next push instead of staying silently wrong.
- **The documented `uses:` line is the source of truth for which major that is** — there is no separate version file to fall out of step with the docs. `check_versions.py` gains a third axis (after semver and `MAP_ENGINE_VERSION`) asserting that `check/action.yml`, `README.md` and `CLAUDE.md` all name the same `check@vN`, so the README can no longer advertise a major the repo does not publish. The regex matches the full published path, so `@v1` named in prose as the frozen line is not mistaken for a live reference.
- `scripts/check_versions.py` now carries an `implements: REQ-SELFGATE-039` tag — it is the first step of the `gate-and-tests` job and was the last untagged file in this repo's own pipeline. `REQ-SELFGATE-039` gains AC-6 (alias placement) and AC-7 (alias coherence).
- **`.worktrees/**` added to the repo-root `.reqmapignore`.** A subagent worktree holds a full second copy of the tree, so the widened local scan double-counted every member (527 vs 261) and reported the copies' README/docs illustration ids (`AUTH-LOGIN-001`, `LOGIN-001`, `AC-1`) as dangling-tag **errors**. CI checks out a clean tree and never saw them — so the local gate and CI disagreed, which is precisely the divergence the gate exists to prevent.

No engine change: `MAP_ENGINE_VERSION` stays at `2026-08-19`.

## plugin `v2.18.0` — 2026-08-19

**The engine can finally see its own supply chain.** `docs/`, `.github/`, `.githooks/`, and root-level `scripts/` have always been outside the scan root — this repo nests `reqmap.py` at `plugin/`, so every documented command only ever reached `plugin/`. `REQ-DOCBUNDLE-026` — built to catch a generated `docs/` HTML bundle with no `generated-from:` tag — never saw its own `docs/full_architecture.html` (99KB), and none of `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/*`, or `sync_reqmap.sh` carried a single membership tag. This release closes that gap for THIS repo's own CI and dev hook only, without moving the needle for any other repo vendoring `reqmap.py` unmodified — settled by a 3-personality Trias deliberation (`.consilium/runs/2026-08-18_1640_v29-scan-root-codeexts-viewer-trias.json`) that unanimously rejected auto-widening the shared default as a silent-failure risk to consumer repos scoped to a subdirectory on purpose.

- **`CODE_EXTS` gains `.sh`/`.tf`, plus exact-basename matching** for `Dockerfile`, `Makefile`, and the standard git hook names (`pre-commit`, `pre-push`, `pre-receive`, `post-receive`, `commit-msg`, `prepare-commit-msg`, `post-checkout`, `post-merge`) — behind one new `_is_code_file()` helper replacing 7 duplicated `endswith(CODE_EXTS)` call sites.
- **`--code` reaches the repo root for this repo alone.** `.github/workflows/ci.yml` and `.githooks/pre-commit` now pass `--code ..`/`--code .`; the shared `code_root = a.code or a.root` default is untouched byte-for-byte. A NEW repo-root `.reqmapignore` (kept deliberately separate from `plugin/.reqmapignore`, not a relocation of it — moving the original would have silently broken the narrow invocation's own exclusions) covers the generated-artifact false positives the wider scan surfaces: `docs/map.html` inlines requirement prose containing literal tag-syntax examples, which reads as a phantom dangling tag once reachable.
- **New requirement `REQ-SELFGATE-039`** tags `ci.yml`, `check/action.yml`, `.githooks/pre-commit`, `.githooks/pre-push`, and `sync_reqmap.sh` — this repo's pipeline wiring had zero membership tags until now. A confirmed requirement whose members are entirely outside `plugin/` genuinely ERRORs under the narrow `gate` invocation (not just a coverage miss) — documented in `CLAUDE.md` as an accepted, loud-not-silent consequence, since CI and the hook always run widened.
- **`gate` gains a warn-only check on `app/src/lib/data.js`**, the viewer's hand-authored fallback fixture (13 requirements copied from the registry so the demo works with no `_map.json` present) — flags requirement IDs whose baked contract text has drifted from the live registry. Caught two of its own correctness bugs in review before shipping: a non-greedy bracket regex that truncated any contract bullet containing `[`/`]` (any bullet describing syntax — a 100% false-positive rate on real data), and an uncaught `UnicodeDecodeError` that would have crashed `gate` outright on a non-UTF-8 file instead of degrading to a warning. Both fixed and regression-tested.
- README: lead rewritten around agent drift (an AI session silently diverging from an agreed contract) instead of generic spec rot; a real worked example (`new` → `confirm` → `sync` → drift → `gate`, actual captured terminal output); stale `~3700 lines` claim corrected; `test_reqmap.py` added to the layout tree.

`MAP_ENGINE_VERSION` → `2026-08-19`.

## plugin `v2.17.0` — 2026-08-17

**The engine now notices when its own roadmap drifts.** `TODO.md` is this project's roadmap and decision log, and nothing checked that it still matched reality. It fell behind twice — once by seven milestones — and the earlier fix, recorded in the `v1.35` section, chose manual hygiene over automation because demand was n=1. This is the read-only middle ground after n=2.

`health --json` gains two signals, both absent (not empty) when the repo has no `TODO.md`, so a project that keeps none sees nothing new:

- **`roadmap_behind`** — the newest roadmap milestone against the newest `milestone:` on any requirement, reported only when the roadmap is the older of the two. It compares against requirement metadata rather than a package version, because the engine owns the former in every repo and the latter is project-specific.
- **`roadmap_unversioned_headings`** — every `## ` heading whose first token is not a version. This is the one that actually bit: `_parse_todos_from_text` keeps the *current* milestone when a heading does not parse, so items below it are filed under the section above rather than skipped. A cosmetic rename silently re-filed this repo's only open roadmap item under the wrong version, with no error anywhere.

Versions compare segment by segment as numbers, so `v2.10` ranks above `v2.9` where a string compare reverses them.

Neither signal is a gate: no exit code changes, and the health score is untouched.

Also in this release: `scan_test_levels` masks Python string literals and docstrings alongside its backtick guard, so prose *about* how to tag never counts as coverage. That was real behaviour with no test and no clause — now pinned by both. New requirement `REQ-ROADMAP-038`.

`MAP_ENGINE_VERSION` → `2026-08-17.2`.

## plugin `v2.16.1` — 2026-08-17

**A clause-group label is decided by where it sits, not by the markers around it.** `v2.15.0` taught the voice to group clauses under bold labels, and `_bullets` learned to skip such a line so the next group's title would stop being appended to the previous group's last clause. It skipped them by shape — `re.fullmatch(r"\*\*.+\*\*", s)` — and `.+` is greedy, so it also matched a hanging-indent continuation that merely *opened and closed* on bold spans. Such a line was dropped, silently, from the parsed contract.

A requirement stating a two-part join predicate lost half of it that way: a clause reading *"shall use it ONLY when both hold: **containment** `…`, and **sanity** `…`"* wrapped so that the containment condition began and ended on a bold span. The generated map then read "when both hold:" followed by a single condition. The `.md` source was never touched and `gate` reported `0 errors` throughout — the gate checks that the map agrees with the engine, never that the engine is faithful to the source, so nothing in the toolchain could see it.

The separation that actually holds is positional: a group label is written flush left, a wrapped clause is indented. `_is_label_line` takes the raw line and requires column 0 alongside the bold-only shape. Across a 94-file consumer corpus every one of the 10 bold-only lines sits at column 0 and none is indented, while the line being eaten was indented two spaces.

**Why not simply narrow the pattern.** Excluding an internal `**` — `r"\*\*(?:(?!\*\*).)+\*\*"` — looks like the smaller change and is the wrong one twice over. It cannot decide a continuation whose entire content is one bold span, which stays ambiguous under any shape test and is exactly the case position resolves. And `***bold-italic***` contains `**`, so that pattern stops matching a real label and folds it into the bullet above — reintroducing the defect the label branch exists to prevent.

**Both call sites share the decision now.** The `over-scoped` lint counted clause groups off `_lint_prose`, which strips every line before returning it; on stripped input each bold-bounded wrap counts as its own group and inflates `contract_n`. Since `--strict` promotes `over-scoped` to an error, that miscount could fail CI on a requirement that is not over-scoped. It counts off `_section_raw`, which preserves indentation.

The two existing bullet tests were each green for the whole life of this regression, which lived in the intersection they jointly leave uncovered — so one more example-shaped test would not have been a control. The new cases pin that intersection, add shapes the corpus does not contain at all (bold-italic labels, wholly-bold continuations, tab indentation), and assert a containment invariant: every non-blank, non-comment line inside a section either opens a clause, folds into one, or is a column-0 label. `REQ-MAP-007` stated the rule in shape terms and now states the positional one.

`MAP_ENGINE_VERSION` → `2026-08-17.2`.

## plugin `v2.16.0` — 2026-08-17

**The V-model's right side gets levels, and a reserved role is redefined.** A `tested-by:` link said only *that* something tested a requirement, never at what level — a whole-system run and a single-function check looked identical to the tool. So the engine could report "this has no test", but never "this stakeholder need has never been validated", which is the question the V-model exists to answer. `tested-by:` now takes an optional suffix — `@unit`, `@integration`, `@system` — applying to the whole tag, so a comma-separated id list shares one level.

**Breaking for anyone using `validated-against:` — read this.** The role has sat in `ROLES` since the beginning with nothing consuming it, and both skill contracts described it as *"config/data (re-validated on change)"*. It is now the **validation** link: evidence the right thing was built, as opposed to `tested-by:`, which is evidence it was built correctly. Point a `layer: need` requirement at it. If your repo carries `validated-against:` tags under the old documented meaning, they will now be read as validation evidence and will satisfy the new need rule. Nothing breaks and no build fails — but the tags mean something different than they did, so re-read them before relying on the new warning.

The gate gains two warn-only rules, chosen as the two asymmetric mistakes the V-model actually warns about rather than as a strict layer-to-level table. A pairing table was rejected on evidence: this repo's `feature` requirements are unit-tested by direct function calls, which is a sound choice, and a rule that flags 36 of 40 requirements for practising something sound gets ignored within a fortnight. Instead — a confirmed `need` with no `validated-against:` link warns, and a confirmed `bus` requirement whose levelled links are all `@system` warns, because foundation code covered only end-to-end is slow, fragile, and localises failures poorly. Every other combination stays silent, including a `feature` tested end to end.

**Silent on arrival.** Both rules are opt-in and gated separately: the first holds back until your repo carries at least one `validated-against:` tag anywhere, the second until a given requirement carries at least one levelled link. An unlevelled `tested-by:` link is never judged. Neither rule can fire until you deliberately annotate something, so updating adds no warnings to any repo.

**Compatible in both directions.** `TAG_RE` already ignored a trailing `@level`, so an older vendored engine reads a levelled tag, resolves the id, and ignores the suffix. That property is now a binding acceptance criterion rather than an accident.

`show` prints the level beside a member whose tag carries one. New requirement `REQ-VLEVEL-037`, whose own tests are tagged `@unit` — the engine is the first consumer of its own vocabulary. `REQ-TRACE-020`'s blanket `need` exemption is narrowed to match, and `REQ-CHECK-006`'s severity table gains both warnings.

`MAP_ENGINE_VERSION` → `2026-08-17.1`.

## plugin `v2.15.0` — 2026-08-17

**Requirements are now written in plain present tense, and the linter enforces the reading level.** The corpus passed every clarity check the engine had while still being hard for a newcomer to read. That was not an accident: `LINT_SENTENCE_WORDS` sat at 35 and `LINT_CONTRACT_WORDS` at 30, roughly twice the level being aimed for, so `lint` reported **zero** findings on prose averaging 18.3 words per sentence. Rewriting the prose without moving those numbers would have let it drift straight back.

Contract clauses now name their subject (`` `init` creates the folder ``) instead of opening with an anonymous "It", drop `shall` in favour of a single **"Every line in this section is binding."** at the head of the section, and group under bold labels once past five clauses. `REQ-INIT-012` rewritten this way measures **10.8 words per sentence against 18.3, longest sentence 19 against 32, and no project term left undefined against twelve** — with all ten of its normative clauses intact. All 40 requirements in this repo were converted; no contract changed meaning, and the lock was advanced once with `sync --accept-drift`.

**Consumer-visible — thresholds tighten.** `LINT_SENTENCE_WORDS` drops 35 → 25 and `LINT_CONTRACT_WORDS` 30 → 22, so a repo that updates will see new warnings on prose it has not touched. They are warnings: `--strict` promotes only `ac-count-high` and `over-scoped` to errors, so **no consumer build breaks**. `SKILL.md` rule 3 now teaches the new voice instead of the `shall` convention, and both `REQUIREMENT_TEMPLATE` (what `new` writes) and the `draft`/`init` emission were rewritten to match, so generated files start compliant.

**Three linter changes came out of the migration, and two of them are fixes the old voice was hiding.**

- `stacked-conditions` no longer requires a `shall` or `must` on the line before inspecting it. Keyed on a magic word, it would have gone **silent** under the new voice without a single test failing. Removing the guard cost one additional finding across this corpus — a genuinely stacked clause in `REQ-HEALTH-017` that the keyed check had never been able to see.
- `over-scoped` now counts **scope units** rather than sentences: clause groups when a contract groups its clauses, clauses when it does not. Writing one obligation per bullet multiplies clauses without widening scope — `REQ-NEXT-013` went from 8 dense clauses to 21 atomic ones describing exactly the same command — so counting clauses alone punished the voice it was meant to serve.
- New `anonymous-subject` warning for a Contract clause opening with a bare "It" — 71 across this corpus when it was switched on. It reads physical lines, so a wrapped bullet whose continuation begins with "It " is flagged; rewriting the sentence is the fix, and `REQ-LINTCHECKS-025` records the limitation.

One rendering bug is fixed alongside: `_bullets()` treated a bold-only line as a hanging-indent continuation, so a clause group's label was folded into the previous group's last clause. That leaked into `show`, the map's contract rendering, and the bag of words behind `dupes` and `search` scoring.

`MAP_ENGINE_VERSION` → `2026-08-17`.

## plugin `v2.14.0` — 2026-08-08

**Requirement clarity is now enforced, not just documented.** `lint` mechanised the SKILL.md "Audience & writing level" rules, but nothing ever ran it — not CI, not the pre-commit hook — so 28 readability warnings had accumulated across the corpus unseen. `reqmap.py lint --strict` now runs in this repo's CI (`check_versions.py → gate → lint --strict → map --check → test_reqmap.py`) and in the shipped `hooks/pre-commit`, between the gate and the map-freshness check. **Consumer-visible:** a repo that installs the shipped hook now has commits blocked by error-severity lint findings (a `confirmed` requirement missing its Contract or Acceptance section) plus the `--strict`-promoted structural checks; style warnings stay advisory. The published `check@v1` GitHub Action gains a `lint` input running the same check, **on by default** like `freshness` — a check that must be opted into is documentation, not a check. It runs the consumer's own vendored `reqmap.py`, so it needs plugin v2.3.4 or newer (the release that added the `lint_exempt:` escape hatch); `lint: 'false'` skips it. Re-seed the engine in any repo below that floor before moving the `@v1` tag onto this commit.

The engine is untouched — no new checks, no new flags, `MAP_ENGINE_VERSION` unchanged. What changed is that the existing rules now execute.

The corpus was cleaned to pass: 25 prose findings rewritten across `REQ-SEARCH-036`, `REQ-REGISTRYLAG-035`, `REQ-NEXT-013`, `REQ-TESTLINK-018`, `REQ-INIT-012`, `REQ-FINDINGS-010`, `REQ-SIMILAR-016`, `REQ-REVIEW-022` and `REQ-PROMOTE-011` — long sentences and stacked `and`/`or` clauses split into atomic normative bullets, with rationale moved to each requirement's Notes section where it belongs. No contract changed meaning; the lock was advanced with `sync --accept-drift`. The two structural findings were resolved as documented exemptions rather than splits: `REQ-CHECK-006` (`ac-count-high`, `over-scoped`) is the gate's severity table, and every check it classifies already owns a separate requirement; `REQ-MEMBERDRIFT-027` (`ac-count-high`) has eight criteria that are the branch table of one decision. Both record the reasoning in their Notes, so the exemption is reviewable instead of silent.

## plugin `v2.13.0` — 2026-07-05

**Ranked requirement search — a `search` command and a shared viewer model.** Finding the requirement about a topic meant grepping `requirements/` (exact word, no ranking) or opening the map. The new `reqmap.py search "<query>"` ranks requirements by lexical relevance, most-relevant-first, reusing the same TF-IDF/cosine scoring (`REQ-SIMILAR-016`) that already powers `dupes` — zero new dependencies, gate/lock semantics untouched. Each hit prints its cosine score, and below a calibrated `0.05` floor it prints "No strong match" instead of a spurious top result — the floor sits far below the `0.35` dupes pair-threshold because a short query is a sparse vector, so query-vs-doc cosine runs lower than doc-vs-doc. The map viewer's search box now ranks by the **same** model (`app/src/lib/search.js`, a faithful port), replacing its substring filter, so the CLI (headless/agent/CI) and the viewer (human browsing) agree on what matches; the two runtimes are pinned to one model by a shared golden fixture asserted in both the Python `Search` tests and the viewer's SSR smoke. New requirement `REQ-SEARCH-036`.

`MAP_ENGINE_VERSION` → `2026-07-05`.

## plugin `v2.12.0` — 2026-07-04

**`health` now reports registry lag — commits since the requirements dir was last touched (RM-6, part 2).** `health` told you whether the requirements that exist are coherent, but not whether the registry as a whole had gone stale while code moved on — a consumer's registry sat frozen for 18 days across ~40 code commits while a money value drifted, and nothing surfaced it. `health --json`/print now carry `commits_since_req_touch`, a read-only git-derived count (last commit touching `reqs_dir` → `HEAD`), printed only when non-zero. It is the temporal complement to the untagged-code coverage signal: coverage asks "is this code traced?", lag asks "has the registry moved lately at all?". Advisory only — never a gate, never lowers the score, and absent (not zero) when unmeasurable (no git / no code root / `reqs_dir` untracked). New requirement `REQ-REGISTRYLAG-035`.

## plugin `v2.11.1` — 2026-07-03

**Repos can declare extra scannable extensions (`REQMAP_EXTRA_CODE_EXTS`).** The scanner
looks at a fixed set of source extensions (`CODE_EXTS`). A repo whose source language isn't in
that set had its capability tags go invisible — the file read as un-covered, and a confirmed
requirement whose only implementation lived in such a file failed the gate with "no
`implements:` member" even when correctly tagged. The new `REQMAP_EXTRA_CODE_EXTS` env var
(comma-separated, leading dot optional, e.g. `.foo,bar`) merges extra extensions into
`CODE_EXTS` at load, so any repo can extend the scan set without forking the engine. Additive;
unset = unchanged behaviour.

## plugin `v2.11.0` — 2026-07-03

**`health` can no longer read 100/clean while `gate` has link-sync errors (RM-6).** A
downstream consumer repo's `health` reported 100/100 for 18 days while `gate` sat on 14
unwired link-sync errors — `gate` was never wired into that repo's CI, so nobody saw it, and
`health`'s own score never reflected `gate`'s state at all. `health --json`/`--badge`/print now
carry `gate_errors` (count) and `gate_link_sync_clean` (bool), computed by a new shared
`_link_sync_errors()` helper mirroring `gate`'s own two ERROR-level checks (dangling tags,
enforced-status requirements with no `implements:` member). Purely additive — the `score`
formula is untouched, same idiom as the existing `untagged` signal. The badge can no longer
show `brightgreen` while `gate` would fail; it turns `red` with a `gate:N` suffix instead.

**What this deliberately does NOT fix:** a value changed in a file carrying no membership tag
at all (the actual shape of the incident that motivated this — an unsourced monetary-constant
edit) produces neither a dangling reference nor a missing-`implements` error, so it stays
invisible to this signal; pinned by a dedicated test. Closing that gap needs a sourced /
`validated-against:`-staleness convention, deliberately out of scope here — Senate run
`reqmap-health-gate-cleanliness` (verdict `GO_WITH_CONDITIONS`) rejected folding it into this
change, citing a 2026-06-21 precedent (`reqmap-enforce-all-code-has-requirements`,
`DEEPLY_SPLIT`) against granting `gate` new blocking authority without its own deliberation.

`MAP_ENGINE_VERSION` → `2026-07-03`.

## plugin `v2.8.1` — 2026-06-26

**Fix: member-hash line-ending normalization (CRLF/Windows).** `_file_sha` hashed member
files as raw bytes, so a `_memberlock.json` generated on a CRLF working tree (Windows,
`core.autocrlf=true`) did not match one verified on LF (Linux/CI) — every member showed
spurious drift. Harmless as a warning, but `gate --strict` (added in 2.8.0) escalated it to
a wall of false errors. Now line endings are folded to LF before hashing, matching the
contract hash (already LF-normalized via the text-mode body parse). LF-only repos are
unaffected (their hashes don't change); `REQ-MEMBERDRIFT-027` +AC-8. `MAP_ENGINE_VERSION`
→ `2026-06-26.1`.

## plugin `v2.8.0` — 2026-06-26

**Gate hardening — close the stale-map / uncommitted-lock blind spot.** A consumer repo
hit a recurring member-drift that the gate never caught: CI ran only the link-sync `gate`
(stale map / drift exit 0) and the `_memberlock.json` baseline was generated but never
committed. Three fixes so this can't recur for any consumer:
- The published action (`check/action.yml`) now runs **`map --check`** after the gate by
  default (new `freshness` input, default `true`) — a stale or never-committed map/lock
  fails CI instead of merging unseen. A repo that tracks no map passes silently. New
  `reqmap-repo` input pins `REQMAP_REPO` for a repo whose committed map targets a different
  slug (e.g. a private repo publishing to a public mirror); it is exported only when
  non-empty, since an empty value means "emit no repo" to the engine. The default hook/CI
  examples in `SKILL.md` gain the `map --check` line too.
- **Untracked-lock warning** (`gate`): a `_reqlock.json` / `_memberlock.json` present on disk
  but not git-tracked is now a `WARN` naming the file — the exact gap that silently disables
  drift detection on a fresh checkout. Fail-open (silent when git is unavailable).
- **Test-link detector** now recognizes a Python suite that drives its checks from a
  `run` / `run_tests` / `main` entry point under an `if __name__ == "__main__"` guard, not
  only `def test…`. A stdlib-only harness no longer false-negatives the test-link integrity
  check — that false error was what blocked `gate --strict` on such corpora.

`MAP_ENGINE_VERSION` → `2026-06-26`.

## plugin `v2.3.1` — 2026-06-16

**License correction.** `plugin/.claude-plugin/plugin.json` declared `"MIT"` while
the `LICENSE` file and README are Business Source License 1.1 — corrected to the
SPDX id `"BUSL-1.1"`.

**excalidraw-diagram — adaptive multi-layer posters (one file).**
- The "Diagramming a repo's architecture" recipe is now **adaptive**: a table of
  six layer-types (STRUCTURE / WORKFLOW / INTEGRATION / MODES / MODEL / DATA) each
  with an "include when…" condition. The author picks which layers the repo needs
  and emits them ALL as stacked sections in ONE file, with one legend that decodes
  every layer (colour-per-distinct-role discipline documented).
- **`discover` now scaffolds that poster**: a live STRUCTURE layer (`section()` +
  sized `grid()`, all four `save()` gates at `"error"`) plus commented scaffolds
  for the five optional layers. The generated stub also carries a **portable
  import** (builder next to the stub / on PYTHONPATH, else newest plugin-cache
  build) so it runs from any repo. New regression test locks the stub shape.
- **Richer-by-default, with guardrails.** Multi-tool repos (2+ skills/services
  with distinct flows) now get one labelled `s.lane()` per tool in the WORKFLOW
  layer instead of a single pipeline that hides the others; single-tool repos
  keep one pipeline. A "depth comes from structure, never from cramming" rule
  subordinates elaboration to the existing readability gates (≤20 nodes/region,
  short labels, simplicity-first always win). The `discover` scaffold shows the
  per-tool lane pattern; a ❌→✅ worked example contrasts it with the thin one.

**excalidraw-diagram — C4 removed + docs overhaul.**
- **Removed the C4 helpers** (`Scene.c4()` and `Scene.person()`). They were
  undocumented and pulled the skill toward formal C4 notation; the canonical
  poster (`examples/make_full_architecture.py`) now uses plain role-coloured
  `box()`es. ISO 5807 flowchart shapes are unaffected.
- **SKILL.md restructured for its purpose** — a "The goal" statement up front, a
  "Diagramming a repo's architecture" recipe pointing at
  `make_full_architecture.py`, a "Worked examples — ❌ → ✅ variants" section
  (repo poster, pipeline, parallel agents, decision flow, feedback loop), and the
  box-sizing guidance softened to lean on the `overflow_check` gate.
- **Doc↔code drift closed.** The cheat-sheet and `references/excalidraw_format.md`
  now document the previously-undocumented public API the examples rely on
  (`section()`, `pipeline()`, the ISO shapes, `path()`, `glossary()`), the full
  `Scene()` signature, all four `save()` gates (`crossing_check`, `legend_check`,
  `overflow_check`, `text_overlap_check`), and `check_text_overflow()` /
  `check_text_overlaps()`.

**Audit follow-up (4-lens Consilium audit) — intent-verb propagation + diagram publish.**
- **Stale CLI names swept.** The intent-verb rename (`check→gate`, `promote→confirm`,
  `extract→draft`, `candidates→plan`, `similar→dupes`, `promote-todo→new --from-todo`)
  is now propagated everywhere it had been missed: the published site
  (`docs/architecture.html`), the engine's own module docstring and scaffold
  `SITE_TEMPLATE`, and six requirement files (`REQ-PROMOTE-011`, `REQ-EXTRACT-008`,
  `REQ-CANDIDATES-009`, `REQ-SIMILAR-016`, `REQ-PROMOTE-TODO-001`, plus stale `check`
  references in `REQ-CHECK-006` / `REQ-ACVERIFY-019` / `CORE-DRIFT-003`).
- **Site truth-up.** `docs/architecture.html` showed `v1.16` (now `v2.3.1`) and
  "All 15 commands" (now 18, with the missing `sync` / `site` / `review` cards added).
  README gains the `site` and `review` rows; the `~3200 lines` engine figure is now `~3700`.
- **Diagram published.** The complete-architecture poster is committed at
  `docs/full_architecture.html` and linked from the site nav (`Diagram ↗`), so it
  resolves on GitHub Pages instead of 404-ing (it had pointed at gitignored `diagrams/`).
- **Engine fixes.** `sync --strict` now forwards the flag to the gate (it was silently
  dropped); `REQ-MAP-007`'s contract documents the `todos` key emitted in `_map.json`;
  the narrower file-type scope of `draft` (vs the gate's full scan set) is documented.

reqmap engine touched (the `sync --strict` fix + docstring/template) → `MAP_ENGINE_VERSION`
advances to `2026-06-16`.

---

## plugin `v2.3.0` — 2026-06-15

**excalidraw-diagram — text-overflow gates.** Two silent failure classes the
shape-only overlap check missed — bound text wider than its box (label spills
out) and two free captions/headers colliding — now have `check_text_overflow()`
and `check_text_overlaps()` checks plus a `fit_text()` wrap-and-size helper.
`save()` gains `overflow_check` / `text_overlap_check` (warn by default, error
opt-in); `box()` defaults are unchanged so existing layouts don't re-flow. The
new per-example assertions caught real bugs (widened a box in
`make_full_architecture.py`, fixed caption pitch in `make_explainer.py`, retired
the superseded `make_repo_map.py`). reqmap engine unchanged; `MAP_ENGINE_VERSION`
stays `2026-06-15`.

---

## plugin `v2.2.0` — 2026-06-15

**excalidraw-diagram — ISO 5807 shapes, C4 helpers, poster helpers.** Additive
builder expansion:
- **ISO 5807 flowchart shapes** — `process`, `terminator`, `decision`, `data`
  (parallelogram), `predefined_process`, `preparation` (hexagon), `connector`
  via `box(shape=…)` + convenience methods (polygons drawn as closed lines with
  bbox geometry).
- **C4 model helpers** — `person()` + `c4()` (name / [kind: tech] / description);
  later removed in v2.3.1.
- **Poster helpers** — `section()` (auto-stacked labelled regions) and `pipeline()`
  (auto-spaced, mid-aligned, auto-chained horizontal flowchart).
- **Examples consolidated** to four maintained, test-covered generators
  (`make_full_architecture.py`, `make_explainer.py`, `make_repo_map.py`,
  `make_iso5807_flowchart.py`); retired the overlapping `make_architecture.py`
  and `gen_reqmap_workflow.py`. `diagrams/` output convention documented
  (gitignored, regenerable). reqmap engine unchanged; `MAP_ENGINE_VERSION` stays
  `2026-06-15`.

---

## plugin `v2.1.1` — 2026-06-15

**Audit follow-up (Consilium Trias).** Fixes from a multi-lens audit of the v2.1.0 excalidraw CLI branch:

- **Stale doc references removed.** `README.md` no longer points to the deleted `docs/plugin_architecture.html`; the `SITE_TEMPLATE` comment in `reqmap.py` no longer cites the removed `docs/reqmap_site_prototype.html` (the template is now the canonical source).
- **`render` hardening.** `render_html()` now rejects a scene whose `elements` is a list of non-objects (e.g. `[1, 2, 3]`) instead of writing a viewer that silently fails to render.
- **excalidraw-diagram menu.** The "how to start a diagram" menu gains the missing day-2 path (**re-run / extend your generator**) and a **self-test** entry, each with a when-to-pick-it clause.
- **Tests.** Wrapped three unclosed file handles in the CLI test helpers (no more `ResourceWarning`); added coverage for the `discover` `max_components` truncation path and the non-object-`elements` rejection.

reqmap engine behaviour unchanged (comment-only edit); `MAP_ENGINE_VERSION` stays `2026-06-15`. SRI hashing of the viewer's CDN tags was identified in the audit but deferred — it needs verified per-asset `sha384` hashes (a wrong hash breaks every generated viewer).

---

## plugin `v2.1.0` — 2026-06-15

**excalidraw-diagram CLI.** Two helper verbs on `excalidraw_builder.py` — the authoring path stays Python (no declarative `build <spec>` verb, which would fork a second, divergent format):

- **`render <scene.excalidraw> [out_dir]`** — rebuild the self-contained `.html` viewer from an existing scene file (e.g. one edited on excalidraw.com, where there is no generator script to re-run).
- **`discover <repo> [out.py]`** — scan a repo and emit a runnable Python generator stub (`make_diagram.py`): one box per top-level component on a no-overlap grid, with `TODO`s for the arrows/grouping you fill in, then run it to produce the scene + viewer.
- No-arg `python excalidraw_builder.py` still runs the builder self-test (unchanged — CI relies on it).

reqmap engine unchanged; `MAP_ENGINE_VERSION` stays `2026-06-15`.

---

## plugin `v2.0.0` — 2026-06-15

**Breaking — intent-verb CLI.** Commands renamed to match what the user wants:

| Old | New |
|---|---|
| `check` | `gate` (report-only) — **kept as a deprecation alias**, removed next major |
| `scan` + `check --update-lock` + `map` | `sync` (composite; `--accept-drift` to advance an edited confirmed baseline) |
| `extract` | `draft` |
| `promote` | `confirm` |
| `candidates` | `plan` |
| `similar` | `dupes` |
| `promote-todo "x" --id ID` | `new --from-todo "x" --id ID` |

- **No consumer breakage:** `check` still runs (prints a deprecation notice, forwards to the legacy path), so vendored pre-commit hooks, CI, and the `check@v1` Action keep working. Migrate at leisure: `check`→`gate`, the trio→`sync`.
- **`sync` drift guard:** `sync` refuses to silently re-baseline an edited `confirmed`/`implemented` contract — it prints the changed hashes and exits non-zero unless you pass `--accept-drift`.
- **`gate` is report-only:** it never touches `_reqlock.json`; use `sync` to advance the baseline.
- Requirement IDs are unchanged (`REQ-PROMOTE-011`, `REQ-SIMILAR-016` keep their slugs — only the CLI verb + prose changed).

### Migration
`extract`/`promote`/`candidates`/`similar`/`promote-todo` are removed (no alias) — they do not appear in consumer CI. Update your own scripts: `sed -i 's/reqmap.py check/reqmap.py gate/' <hook>`. `MAP_ENGINE_VERSION` is `2026-06-15`.

---

## plugin `v1.35.0` — 2026-06-14

The `site` command — keep a project presentation page in sync with the registry. Highlights:

- **`site` command** — `reqmap.py site --attach <page.html> [--regions nav,stats]` injects engine-owned, marker-delimited regions into a presentation page and **preserves the authored prose between them**. `nav` = Live Map / Diagram / GitHub links (from `git remote` + artifact paths, each emitted only when its target resolves); `stats` = requirement / confirmed / layer / edge counts + engine version (from `_map.json`). When the `--attach` target does not exist, `site` scaffolds a full self-contained default page with a placeholder hero (`<!-- author me -->`).
- **Two layers** — the engine is deterministic and headless-safe (never prompts); the `requirement-manager` skill is the interactive front door (`site --detect` → ask which target + regions → call the engine). The engine only *links* an Excalidraw diagram — it never generates one (the `excalidraw-diagram` skill stays independent of `reqmap.py`).
- **`init` integration** — `init` runs a best-effort `site` pass (`nav,stats` into `docs/architecture.html`, scaffolding it plus a GitHub Pages signal — `.nojekyll` + an `index.html` redirect — when absent). Opt out with `reqmap.py init --no-site`; a failure in the step never aborts `init`.
- **`map --check` gate** — flags the page stale when its `stats` region drifts from a fresh render; the `nav` region is exempt (it embeds the fork-specific repo URL, like the `repo` field excluded from `_map.json`). A page with no `stats` marker — or one never generated — is not stale. Reuses the `REQ-PAGES-021` Pages-publish path.
- **New requirement `REQ-SITE-026`** + 14 new `Site` tests (idempotency, prose preservation, no-remote degradation, scaffold mode, region-only staleness, HTML-escaping, CLI dispatch, excalidraw independence).

### Upgrade notes
Re-seed consumer repos with `scripts/reqmap.py` only — the scaffold page is an inline template, so no new vendored file is required. `MAP_ENGINE_VERSION` is `2026-06-14`.

---

## plugin `v1.11.0` — 2026-06-04

First feature release since `v1.0.0`. Highlights:

- **Self-contained HTML viewer** — `map` now emits `requirements/_map.html`: a single-file React app with your real requirements inlined, double-click to open, no server or npm needed. Tabs: System Map, Risk, Dependencies, Spec. Main-bus layout ranks nodes by dependency depth (`bus` nodes on the right, consumers on the left); color-coded, selectable edges; grab-to-pan. Fixed: viewer used to render only its bundled demo fixture — all graph tabs now compute layout from the live registry.
- **`init` command** — one-shot bootstrap: scaffolds `requirements/` + `.reqmapignore`, drafts requirements from existing code, builds the lock + map, prints guided next steps. Idempotent; `--wipe` for a hard reset (strips all tags + deletes non-generated files before re-extracting).
- **`next` command** — terminal "what should I do next": a progress header then the Risk tab's actionable buckets most-urgent-first (Orphans · Needs tests · Needs intent review · Drafts to review). Read-only, always exit 0.
- **`promote` command** — human validation step: flips a reviewed requirement's `status` to `confirmed`. Refuses if it has no `implements:` member; warns if no `tested-by:` is linked.
- **`findings` command** — aggregates open `## WHAT — Verify intent` items across all requirements into `requirements/_findings.md`; accepts an AI-triage sidecar (`_findings_triage.json`) for a classified view.
- **`export` command** — emits `requirements/_map.json` (or `--out PATH` / `--out -`) for feeding an external front-end.
- **Intent triage skill action** — 5th menu item in the `requirement-manager` skill for AI-assisted triage of open verify-intent findings.
- **Prose capability discovery** — `extract`/`init` scan `.md`/`.html` by default and classify each prose file into three buckets: ignore (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), or capability-source (prompts/specs auto-drafted as `draft` stubs).
- **`candidates --md-glob`** — read-only extraction plan from prose/spec markdown (advisory, writes no `.md`).
- **Risk signals** — `untested` (has `implements` but no `tested-by:`) and `unverified-intent` (open verify-intent item) surfaced on the Risk tab, `_map.md` table, and detail panel. Silence per-requirement with `test_exempt: <reason>` in frontmatter.
- **`map --check`** freshness gate — exits non-zero if committed `_map.*` is stale; wire alongside `check` in pre-commit/CI.
- **`check --update-lock` auto-runs `map`** — lock and map stay in sync in one command.

### Upgrade notes
Re-seed consumer repos with both `scripts/reqmap.py` **and** `scripts/_map_viewer.html` — the viewer template is new and required for `_map.html` emission. Use `sync_reqmap.sh` or the skill's "update engine" action.

---

## engine `1.11.0` — 2026-06-04

- **Fixed — viewer rendered only its demo fixture**: the `_map.html` graph tabs
  positioned nodes through hardcoded coordinate maps keyed to the bundled sample ids,
  so any real repo's requirements were filtered out and the canvas was blank (registry
  counts were correct, masking it). The System Map, Risk and Dependencies tabs now
  **compute their layout from the live registry** — they render any repo's data.
- **Added — layered "main-bus" layout** (`app/src/lib/layout.js`): nodes are ranked by
  dependency depth so `depends_on` flows left→right (consumers left, shared
  foundation/`bus` nodes right), a barycenter pass minimises edge crossings, and
  edge-less nodes are parked in a side grid.
- **Added — colour-coded, selectable edges**: each dependency edge (arrowhead included,
  via `context-stroke`) is drawn in its source requirement's colour, so overlapping
  lines stay traceable; cards are kept neutral. Click a line to isolate it — it goes
  bold, the rest dim, and its two endpoints are ringed, so `x → y` is unambiguous.
- **Changed — card-avoiding orthogonal routing**: edges run their verticals in the
  inter-column gutters and cross any intermediate column only through a gap between its
  cards, so a line never passes through a card it doesn't connect to (no more
  "x → y → z through a node" look). Rounded right-angle turns.
- **Added — grab-to-pan**: drag anywhere on a map canvas to pan it (no need for the
  scrollbars); a plain click (no drag) still selects a node or edge.
- **Fixed — "center & highlight" button**: it set the highlight but never scrolled; it
  now `scrollIntoView`s the highlighted node.
- **Fixed — `_build_json` area**: emits the ID-prefix fallback (`_area_of`) when a
  requirement has no explicit `area:`, matching the Mermaid path's grouping so the
  JSON graph carries a usable `area` for external front-ends.

## engine `1.10.0` — 2026-06-04

- **Added — React front-end (`app/`)**: the four product surfaces (Map · Problems ·
  Console · Spec) as a real Vite + React app, recreated from the design system. Run
  with `cd app && npm run dev` (dev server pinned to port 5173 via `--strictPort`).
- **Added — `export` command**: `reqmap.py export` emits the registry graph as
  `requirements/_map.json` (`{engine_version, nodes, edges}`) — to stdout (`--out -`),
  a path (`--out PATH`), or the default file — for an external front-end to consume.
- **Added — self-contained viewer (`_map.html`)**: `map` injects this repo's graph
  into a pre-built single-file React viewer (`scripts/_map_viewer.html`, carrying a
  `<!--REQMAP_DATA-->` marker) → a double-click-openable `requirements/_map.html`,
  no server, no npm. Emitted only when the template is vendored beside the engine;
  the injected data is escaped (`</` → `<\/`) against script-breakout. `_map.html` is
  regenerable and gitignored.
- **Behavior change — engine no longer hand-generates HTML**: `render_html` and the
  inline HTML template were removed; `map` now writes `_map.md` + `_map.json`
  (+ `_map.html` from the viewer template when present). The freshness gate
  (`map --check`) now covers `_map.md` + `_map.json`. Re-seed consumer repos with both
  `scripts/reqmap.py` and `scripts/_map_viewer.html` (see SKILL setup / `sync_reqmap.sh`).

## engine `1.8.0` — 2026-06-03

- **Added**: `extract`/`init` now discover prose capabilities (`.md`/`.html`) by
  default, classified by `classify_prose` into three buckets — ignore
  (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), and
  capability-source (prompts/specs). Capability-source prose is auto-drafted as a
  `draft` stub from its title + `##` headings (`_prose_facts`). An advisory
  doc-sync step is emitted in the skill for sync-only docs tagged `generated-from`.
- **Behavior change**: on first post-upgrade `init`/`extract`, repos with
  prompt/spec markdown will see new `draft` requirements. Drafts are NOT enforced
  by the gate (`draft` is not in `ENFORCED`), so this cannot break an existing
  `check`. Review, edit, and `promote` the real ones; delete the rest.
  README/docs/HTML and meta files (`CLAUDE.md`, `SKILL.md`, `TODO.md`,
  `CHANGELOG.md`, `LICENSE*`) are never auto-drafted.

## engine `1.5.0` — 2026-06-03

- **`reqmap.py promote <ID>`** — one-command human-validation step: flips a reviewed
  requirement's `status` to `confirmed` via a single frontmatter edit (preserves
  indentation + trailing comment, body untouched). Refuses when the requirement has
  no `implements:` member (a confirmed requirement must point to code, else the gate
  errors); warns when no `tested-by:` is linked; idempotent on an already-confirmed
  requirement. Dogfooded as `REQ-PROMOTE-011`.
- **owner standardized** to `Alex` across the repo's own requirements + the scaffold
  default (`extract` still emits `owner: auto` for machine-drafted, unreviewed files).

## engine `1.4.0` — 2026-06-03

Drift gates to prevent the version/map skew that slipped past in 1.3.x.

- **`reqmap.py map --check`** — freshness gate: regenerates the map in memory and
  compares it to the committed `_map.html`/`_map.md` (ignoring the volatile
  `generated:` timestamp), exiting non-zero if stale. A map that was never generated
  passes (consumers who don't track maps are unaffected). Wired into the shared
  pre-commit hook and CI so a code/requirement edit that shifts the map can't be
  committed without regenerating it.
- **`check_versions.py --fix`** — propagates `plugin.json`'s version into every
  `marketplace.json` occurrence, so a bump is one edit + one command instead of three
  hand-edits (the exact drift that failed CI in 1.3.0).
- **dev pre-commit hook** (`.githooks/pre-commit`, enable with
  `git config core.hooksPath .githooks`) — runs version coherence + the drift gate +
  map freshness locally, before CI.

## engine `1.3.0` — 2026-06-03

Non-code capability discovery + corpus-health visibility (`MAP_ENGINE_VERSION` 2026-06-03).

- **`candidates --md-glob`** — discover capabilities in authoritative **non-code** files
  (prompt/spec markdown), advisory-only and allowlist-bounded. Off unless a glob is
  given; writes no `.md`. A new `_md_facts()` extractor pulls the H1 title, the first
  blockquote after it (intent), and `## ` H2 headings (no parser). The plan now carries
  `coverage_summary {total_candidates, with_existing_req}` and a `lineage_note` so an
  unfilled plan can't masquerade as coverage, and so a `generated-from`/`implements`
  tag is understood as authoring lineage — not auto-tracking of later source edits.
- **`.md` added to the scan extensions** so prose capabilities can carry membership
  tags (`<!-- implements: ID -->`). The drift hash still anchors only on the authored
  Contract+Acceptance, so source prose may drift freely.
- **`check` health line** — the summary now reports `(N confirmed, M legacy-schema)`,
  and legacy-schema requirements (no `## WHAT — Verify intent` section, for which
  `findings` is silently inactive) are flagged with a non-blocking WARN. Makes an
  all-baseline corpus (gate enforces nothing yet) and an inactive `findings` visible.
- **`extract`** now annotates the emitted `risk:` field as an author triage hint that
  the engine does not read.
- **map risk signals** — two new signals surface on the Risk tab + `_map.md` table +
  detail panel: `untested` (a requirement with an `implements` member but no
  `tested-by`), suppressible per-requirement with a `test_exempt: <reason>` frontmatter
  field; and `unverified-intent` (a requirement with an open `## WHAT — Verify intent`
  item). Both reuse the existing risk machinery.
- **map zoom-fit fix** — diagrams now fit their container on first open *and* on every
  tab switch. Fit is measured after layout (double `requestAnimationFrame`, zero-size
  guard) and centered, with a capped modest upscale (`FIT_MAX`) so small diagrams fill
  the pane without over/under-zooming.

## check action `v1.0.0` — 2026-06-03

First published release of the `requirement-manager` CI action. Run the drift gate
on every push and PR without copying YAML boilerplate into each repo.

### Usage
```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read            # least privilege — the gate only reads the tree
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v1
```

### Inputs (optional)
| input | default | purpose |
|---|---|---|
| `reqmap-path` | `scripts/reqmap.py` | path to your vendored engine, relative to `working-directory` |
| `working-directory` | `.` | directory the gate runs from (where `requirements/` lives) |
| `python-version` | `3.x` | Python to set up (engine is stdlib-only — any 3.x works) |

### What it enforces
`reqmap.py check` — link sync (every code tag points to a real requirement; every
confirmed requirement has ≥1 member), content drift vs. the lock, and `depends_on`
target existence. Fails the build on any violation.

### Notes
- **Versioning:** pin to `@v1` (moves with backward-compatible fixes) or to `@v1.0.0`
  / a commit SHA for exact reproducibility. The action ref is independent of the
  plugin/PyPI semver.
- **Scope:** the vendored-copy staleness notice (`warn_if_stale`) is gated on
  `CLAUDE_PLUGIN_ROOT`, unset in CI — silent and exit-neutral there by design.
- **Security:** keep `permissions: contents: read` in the caller workflow; the gate
  needs no secrets and no write scope.
