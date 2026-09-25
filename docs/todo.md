# TODO Requirement-manager — 26 sept 2026

Decis: Consilium sequential (`unconventional_default_path`) + Trias 2–1 (`default_path_plus_dogfood`).

## A. Promisiunea adevărată
- [ ] A1. README = hello-drift = action.yml pe drift advisory / PASS.
- [ ] A2. PR1 GateResult.
- [ ] A3. PR2 input invalid.
- [ ] A4. Șterge proza `@v2` (parțial #348).
- [ ] A5. Dogfood `check@v8` = E3.
- [ ] A6. Snippet fără `push`+`pull_request` (parțial #348).

## B. Calea implicită
- [ ] B1. `init` implicit `--minimal`.
- [ ] B2. Skill fără workflow obligatoriu înainte de write.
- [ ] B3. Flag-uri moarte afara din `--help`.
- [ ] B4–B6. `hook install` + `--if-affected` + `reqmap.yml` (helper pe #348).

## C. Ușa din față
- [ ] C1–C3. hello-drift, template, un tag `v8.7.0`.

## E. CI-ul acestui repo
- [ ] E1. Teste 3.9+3.12, un OS. Îngustează matrix-ul după ce `release` nu mai `needs` toate celulele.
- [x] E2. `gate --full` o dată, în `gate-and-tests`.
- [ ] E3. `.github/workflows/dogfood.yml` — `check@v8`.
- [x] E4. versions + CORE budget în job-ul scurt.
- [ ] E5. Release / `@v8` doar pe push `main` sau tag, nu și pe PR.

## P. Plan rigid (după A–C, nu în locul lor)
- [ ] P0. Un plan: `ROADMAP.md`. Nu ține un al doilea TODO pe `main`. După merge, mută Now/Next aici și retrage `docs/todo.md`.
- [ ] P1. `sync --release --apply` bifează în `ROADMAP.md` itemele `| req: ID` ale barelor din milestone-ul tăiat. Nu le mai lista doar în stdout.
- [ ] P2. `gate --strict` (opt-in) pică pe plan stale: milestone ≤ versiunea declarată. Implicit rămâne warn (`REQ-PLANSTALE-1013`).
- [ ] P3. `sync --release` exit 2 dacă un item Now/Next din milestone nu are bară în `_planning.json`.
- [ ] P4. Un drum de release în *acest* repo: ori CI citește `sync --release --json` (ADR-0040), ori docs nu mai zic că planul taie tag-ul. Acum tagează din `plugin.json`.

Nu: Roadmap generat din git, gate roșu implicit pe plan sub `@v8`, al treilea fișier de sync, cadence săptămânală cât ești singur.

## D. Mai târziu
- [ ] D1. Licență (amânat).
- [ ] D2–D4. Outreach, lazy imports, prag AC pe draft.
