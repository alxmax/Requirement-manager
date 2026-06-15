# Plan de implementare — Senate fix plan (2026-06-12)

Sursă: două deliberări Senate.
- Audit (4 senatori, fable/opus): `Senate/runs/senate/2026-06-12_090405-requirement-manager-repo-audit.json` — verdict formal UNREACHABLE (4/9 quorum), substanțial MODIFY (2 blocking: phantom members, hollow test links + contradicții doc-vs-cod pe drift).
- Fix-plan (9 senatori, topologie default, 2 runde): `Senate/runs/senate/2026-06-12_091906-requirement-manager-fix-plan.json` — verdict **MODIFY** (4 blocking: Wittgenstein, Socrate, Dimon, Musk; Tacitus GO). Condițiile MODIFY de mai jos sunt încorporate.

Notă Tacitus: pachetul NU revendică o aprobare Senate — procedează pe cele 2 blocking MODIFY substanțiale ale auditului. PR4 (--since) e net-new, nu mandatat de audit.

Reguli generale per PR: bump `plugin.json` semver + `MAP_ENGINE_VERSION`; `python scripts/reqmap.py check` + `map` regen; `check_versions.py` 0 errors; `test_reqmap.py` verde. Fiecare schimbare de engine primește/actualizează requirement + tag-uri.

---

## PR1 — Phantom-member fix (BLOCKING, primul)

**Bug:** un tag `implements:`/`tested-by:` în docstring, string literal sau proză markdown contează ca membru real (`_scan_file_tags`, `reqmap.py:192-208` — `TAG_RE.findall` per linie, fără context) și satisface singurul check error-level de acoperire (`:518`). Fantome dovedite: `CLAUDE.md:56`, `docs/architecture.html:184` (în fenced blocks), `CORE-SCAN-002.md:14,66`, `REQ-CHECK-006.md:116`.

**Design final (Wittgenstein R2 + Socrate R2 — NU „comment-leader guard", retras explicit):** mașină de stări pe clase de fișiere în `_scan_file_tags`, admisie = NOT(zonă-exclusă):

- **PROSE_EXTS (.md/.html, `reqmap.py:44`):** tag admis doar dacă NU e în fenced code block (stare `in_fence` purtată peste linii, toggle pe ```/~~~ cu potrivire de lungime CommonMark), NU e în backtick span pe linie, NU e în bloc indentat (≥4 spații/tab). **Fără cerință de leader** — `<!-- implements: X -->` rămâne valid pentru că e în afara zonelor excluse (păstrează membrul REQ-REVIEW-022 din `plugin/skills/requirement-quality-review/SKILL.md:6`, mandatat de REQ-PROSE-024 AC-4).
- **Cod (.py):** tag admis doar dacă NU e în triple-quote (stare `in_triple`) și NU e în string literal single-line (mască de intervale per linie). **Fără cerință de comment-opener** (ar pica tag-urile inline legitime). Alte extensii de cod: comportament neschimbat (surgical change).
- Stările se resetează per fișier. Stdlib-only, O(lungime linie), fără parser per limbaj. Poți reutiliza fence-tracking-ul existent din `_lint_prose` (`reqmap.py:1620`, `:1632`).

**Fixtures obligatorii (gate de merge), F1–F8:**
| # | Fixture | Așteptat |
|---|---|---|
| F1 | .md cu `<!-- implements: X -->` în afara fence-ului | KEPT (regression guard) |
| F2 | .md cu `# implements: X` în fence ``` | DROPPED (clasa CLAUDE.md:56) |
| F3 | .md cu tag în backtick span | DROPPED |
| F4 | .md cu tag în bloc indentat 4 spații | DROPPED |
| F5 | .py cu tag în docstring triple-quoted | DROPPED |
| F6 | reset de stare per fișier (fără scurgere cross-file) | independent |
| F7 | .py cu `code()  # implements: X` inline | KEPT |
| F8 | fence-uri imbricate/mai lungi (```` conținând ```) | închidere pe lungime potrivită |

**Acceptanță suplimentară (Socrate):** după fix, corpus-ul propriu raportează zero membri fantomă (CLAUDE.md:56 și architecture.html:184 dispar din `scan` rulat din rădăcină).

**Atenție migrare (Dimon):** schimbarea poate modifica membership în repo-uri seeded; documentează în CHANGELOG comportamentul nou + calea de migrare.

## PR2 — Reconciliere documente drift, direcția B (BLOCKING)

Warn-only drift e decizie deliberată din ziua 1 (REQ-CHECK-006:23-24 „WARN (never an error)", dovedit prin git pickaxe). Direcția A (error-level) respinsă de consens (Aurelius: sparge consumatorii Action @v1; Confucius: răstoarnă un contract confirmed fără `superseded_by`; Dimon: alarm fatigue → `--update-lock` reflex). Ediții, toate gradabile:

1. `SKILL.md` secțiunea gate (~:258-271): drift = WARN, exit-neutral; adaugă **tabel de severitate** (check × nivel error/warn × efect pe exit code).
2. `SKILL.md` :250-251: șterge/corectează promisiunea „baseline — gate only alerts on change" (drift rulează doar pe `confirmed`, cf. `reqmap.py:575`, auto-recunoscut la `:584`).
3. `CLAUDE.md` paragraful gate: „all error-level" → error-level doar link sync + depends_on; drift și test-link sunt WARN.
4. `NEED-SSOT-001` AC-1 split (Socrate): **AC-1a** structural (tag dangling / confirmed fără membru → ERROR exit 1); **AC-1b** drift (raportat DRIFT cu file:line, WARN by design — vezi REQ-CHECK-006). Contract: „shall be caught" → „shall be surfaced". Apoi `check --update-lock` + `map`.
5. Opțional: aliniază proza „risk = blast radius × uncertainty × proximity" din SKILL.md cu scorul aditiv 0-3 implementat (`reqmap.py:971-976`).

**Test de acceptanță:** editează un bullet de Contract la un req confirmed → `check` exit 0 + „WARN … DRIFT" în output; SKILL.md descrie corect comportamentul.

**Întrebare deschisă (Socrate, de confirmat de owner):** B presupune că intenția warn-only e autoritativă și need-ul se rescrie. Dacă vrei vreodată drift blocant, folosește `check --strict` (PR3), nu schimbarea default-ului.

## PR3 — `check --strict` + `check --json` (features, după PR1)

**--strict** (absoarbe și ideea P1-A ca opt-in; precedent: `lint --strict`, `reqmap.py:2826`). Set enumerat EXACT de WARN-uri promovate la error (Wittgenstein — fără „optionally"):
- test-link integrity (`_test_link_problem` + missing tested-by, `reqmap.py:521-529`) → ERROR
- drift pe confirmed (`:575-580`) → ERROR
- restul warn-urilor rămân warn.
Test: corpus cu un confirmed stale → exit 0 fără `--strict`, exit 1 cu `--strict`; req confirmed cu tested-by șters → la fel.

**--json**: serializare a listelor errors/warns existente (clasă eșec, requirement id, fișier, linie). **Contract de aliniere exit-code** (Dimon): `ok` în JSON ⇔ exit 0; un test care verifică echivalența în ambele direcții. Precedent: `health --json` (`:2830`).

## PR4 — `check --since <ref>` (net-new, opțional, ultimul)

Gate scoped pe `git diff <ref>...HEAD`, extinde scan cache (REQ-SCANCACHE-023). Condiții obligatorii (Dimon):
- **fallback la full scan + WARN explicit** când git lipsește, ref-ul nu există (shallow clone fetch-depth:1) sau diff-ul eșuează — empty-diff-din-eroare nu se tratează ca „nimic de verificat";
- fail-open try/except ca la utilizările git existente (`reqmap.py:2702-2707`);
- justificarea „highest-frequency" e ipoteză de design, nu măsurătoare (Deming) — etichetează ca atare în requirement.

## PR0/PR1-adjacent — bugfix-uri mici (fiecare cu test falsificator)

- **`#` truncation în scalari frontmatter** (`reqmap.py:132`, `v.split("#",1)[0]`): nu trunchia `#` care nu e precedat de whitespace (sau doar în afara ghilimelelor). Test: `title: count #1 thing` rămâne întreg sau e trunchiat doar la ` #`.
- **Off-status drift blind spot** (`reqmap.py:575`): un Contract editat cu status temporar non-confirmed + re-lock șterge silențios semnalul. Minim: la `--update-lock`, raportează explicit care hash-uri se schimbă (lock update deliberat, nu tăcut — și condiția lui Confucius dacă se reia vreodată direcția A).

## Respins / amânat (cu motive — nu implementa)

- **P6 satisfies-edge lint:** ȘTERS (Musk, confirmat Deming: populația e epuizată — 1 singur need, 4 edges; n nu poate crește). AC-1 se repară direct în proză (PR2). Dacă revine pe multi-need repos: criteriul ex-ante al lui Socrate — determinist doar dacă e invariant structural pe frontmatter/etichete AC; orice comparație semantică de proză = comandă AI-assist/advisory, niciodată gate.
- **Scan-root pinning în _reqlock.json:** speculativ, zero rapoarte de consumatori (Musk). Reține doar ca known-limitation în SKILL.md dacă vrei.
- **export → map fold:** NU — sparge consumatorii `export --out -` (`reqmap.py:1478, :2818`). Dacă se face vreodată: alias + deprecation WARN ≥1 ciclu MAP_ENGINE_VERSION (Dimon).
- **findings → next fold:** NU — contrazice REQ-NEXT-013:35 care documentează divergența ca intenționată (Deming). Nu contrazice silențios un requirement autorat.

## Igienă (post-merge)

- Reconciliază `Senate/runs/senate/outcomes.jsonl` (Tacitus): rulările 06-08/06-09 requirement-manager sunt implementate în git (d2cb32c, c903667, 3b95feb, 8d75b85, 8977fa6, 7ec7994, bded3cf) dar figurează PEND — înregistrează-le cu `senate_outcome.py record`. La final, înregistrează și outcome-ul celor două rulări din 2026-06-12.
- Documentația spune 14 comenzi; dispatch-ul expune 17 (`promote`, `promote-todo`, `review` — `reqmap.py:2812`). Actualizează CLAUDE.md/README.

**Ordine recomandată:** PR0 bugfix-uri mici → PR1 phantom fix → PR2 docs drift → PR3 --strict/--json → PR4 --since. Estimare Napoleon: total 12-21h (cu P6 șters), overhead ~15-20min/PR pentru version bump + map regen.
