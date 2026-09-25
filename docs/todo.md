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

## D. Mai târziu
- [ ] D1. Licență (amânat).
- [ ] D2–D4. Outreach, lazy imports, prag AC pe draft.
