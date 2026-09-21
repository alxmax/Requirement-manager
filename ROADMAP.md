# Roadmap

Planul produsului. Nu e jurnal. Versiunile trăiesc în CHANGELOG și în tag-ul git.

Editezi aici, direct. Barele din Gantt-ul viewer-ului se scriu în `plugin/requirements/_planning.json`.

Format: `- [ ] text | req: ID` pe Now/Next. Later cere `unpark:`.
Heading-uri rezervate: Now, Next, Later, Not now. Nimic altceva la `## `.

## Now

- [x] Scoate diagrama Specification Hierarchy din `_map.md` | req: ARCH-MAPDIAGRAMS-055
      <!-- Bifa anterioară („desenează CODE când sunt ≤24 noduri code") era falsă:
           `_mermaid_hierarchy` n-a desenat niciodată un nod code și n-a avut niciun prag
           de 24. Diagrama a fost scoasă cu totul; `_map.md` are iar 4 blocuri, ca
           CLAUDE.md. REQ-MAPDIAGRAMS-875 e `deprecated`. -->
- [x] `init` pe un tree deja taguit tot scrie ARCH + SYS (nu rescrie CODE) | req: ARCH-EXTRACT-008
- [x] Parserul citește `ROADMAP.md` (Now/Next/Later) pe lângă `TODO.md` | req: ARCH-ROADMAP-038
      <!-- Bifat înainte de a fi adevărat: până azi motorul n-avea NICIO referință la
           `ROADMAP.md`. Acum `_parse_roadmap_from_text` îl citește (REQ-ROADMAP-998) și
           `gate --audit` raportează cele două lucruri verificabile mecanic: un `req:` care
           nu există, și un `Later` fără `unpark:`. NU e precedență — ambele fișiere se
           citesc, pentru semnale diferite. -->
- [x] Viewer Roadmap: trei coloane Now / Next / Later când orizonturile există | req: ARCH-VIEWER-007
      <!-- Făcut în v7.6.0 (REQ-VIEWER-999). Modul Horizons apare DOAR când exportul
           duce itemi de orizont. `Not now` se parsează și nu se desenează. -->
- [x] `roadmap_unmapped` / heading-uri fără milestone numesc un next-step | req: ARCH-ROADMAP-038
      <!-- v7.21.7, REQ-ROADMAP-983 CASE-4. Fiecare linie de roadmap din `sync` şi
           `gate --audit` se termină cu editarea care o stinge. -->
      <!-- Debifat 2026-09-13: `audit.py:183-188` se opreşte la constatare în ambele cazuri.
           `roadmap_unmapped` are deja răspunsul — adaugă `milestone:` la cerinţele care au
           ieşit în versiunile alea. Vezi şi TODO.md v5.13, care cere acelaşi lucru. -->
- [x] `clarify` nu mai tipărește `next: gate --implement` | req: ARCH-CMDREGISTRY-033
- [x] `sync --help` numește pașii (scan → drift → lock → map → findings → site) | req: ARCH-CMDREGISTRY-033
- [x] Scoate `gate --implement` (ADR-0037 pass 2) | req: ARCH-CMDREGISTRY-033

<!-- Valul 0 — aplică ce e deja scris (1–2 zile) -->
- [ ] V0: Aplică patch-ul first-contact. Gata când: `gate --help` nu listează `--wipe`, demo-ul din `examples/hello-drift` arată DRIFT | req: ARCH-INIT-012
      <!-- `reqmap-first-contact.patch` nu e în repo; singura urmă e branch-ul
           `origin/fix/first-contact-horizons` (098eb07). -->
- [x] V0: Release v8.0.0 (nu v7.23.1: `main` avea deja scoaterea lui `new`), cu `sync --release`. Gata când: tag-ul există, `check@v8` pointează pe el | req: ARCH-RELEASE-072
- [ ] V0: Pages = landing-ul de 3 comenzi, nu posterul; `architecture.html` rămâne link. Gata când: un străin nu cade în 291 de noduri | req: ARCH-SITE-026
- [x] Upgrade-ul de motor nu mai retrogradează în tăcere tot corpusul: `sync` pe Consilium-py (2026-06-19.1 → v8) a trecut 17/17 cerințe `confirmed` în `draft`, fiindcă schema `binding_hash` s-a schimbat, nu textul. Gata când: un lock scris de alt `MAP_ENGINE_VERSION` e re-baseline-uit, nu tratat ca drift | req: ARCH-DRIFT-003
- [x] Un consumer vechi re-vendorizat nu mai vede tag-urile motorului: `.reqmapignore` din Consilium-py n-avea `scripts/reqmap_engine/**` și gate-ul a dat 100+ RM001. Gata când: scanarea exclude pachetul motorului vendorizat fără o linie în `.reqmapignore` | req: ARCH-SCAN-002
- [x] `sync --release` bumpează și `marketplace.json`, nu doar `plugin.json` (la v8.0.0 a trebuit `check_versions.py --fix`) | req: ARCH-RELEASE-072
<!-- Valul 1 — primul străin poate evalua (săptămâna asta) -->
- [ ] V1: Topics GitHub: requirements, drift, ssot, spec, claude-code, mcp, traceability. Gata când: `topic:drift` găsește repo-ul | req: SYS-SSOT-001
- [ ] V1: PR-uri de la public (`pull_request_creation_policy` ≠ collaborators_only). Gata când: un fork poate deschide PR | req: SYS-SSOT-001
- [ ] V1: n=2 real: Consilium-py pe `uses: alxmax/requirement-manager/check@v8`. Scoate `setup-python` + `python scripts/reqmap.py gate`, pune action-ul. Gata când: job verde 7 zile pe `main` și motorul Consilium re-vendorizat (azi e din 19 iunie) | req: ARCH-SELFGATE-039
      <!-- Mutat din Later pe 2026-09-21. -->
      <!-- 2026-09-21: motor re-vendorizat pe v8, `map --check` scos, CI verde pe `check@v8`
           (Consilium-py #63, merge 18:14). Rămâne fereastra verde. -->
- [ ] V1: Un evaluator numit, nu un repo al tău — om/echipă ≠ Schipor, repo-ul lor, fără ajutor la gate. Gata când: au `uses: …/check@v8` pe un tree pe care nu-l comiți tu | req: SYS-SSOT-001
- [x] V1: Issue template „I tried this on my repo” — limbă, mărime tree, ce-a picat, ce-a mers, BSL a blocat? Gata când: primul issue din afară se deschide fără să ghicească formatul | req: SYS-SSOT-001

## Next

- [x] Planul si Versiunile citesc acelasi lucru | req: ARCH-VIEWER-007
      <!-- v7.20.0. O singură listă, două randări: `items[]` a fost şters, iar Versiunile
           citesc `bars` filtrate pe `milestone`. Nota de mai jos e starea de dinainte. -->
      Ce apare in Plan nu apare in Versiuni. Puntea EXISTA deja - RoadmapView.jsx:236-246
      amesteca itemi planificati in coloana fiecarei versiuni - dar ii citeste din
      `milestones[].items[]`, nu din `bars`. Iar `items[]` e chiar cheia goala pe care
      auditul din 2026-09-14 a scos-o din planBars.js: fiecare milestone o avea `[]`, deci
      ramura rula peste nimic.

      Asa ca azi: coloana v7.19 se creeaza (msSet ia si cheile din `_planning.json`,
      linia 209), dar bara "Server MCP" nu intra in ea, fiindca continutul unei coloane
      vine din cerinte cu `milestone:`, din TODO-uri, si din `items[]` - niciodata din
      `bars`.

      Reparatia mica: citeste `bars` acolo unde se citeste `items[]`, filtrate pe
      `bar.milestone`. Atentie la dedublare - se face deja pe titlu, iar o bara cu `req:`
      numeste o cerinta care e probabil deja in coloana.

      Intrebarea inainte de a scrie codul: e o singura lista cu doua randari, sau doua
      liste care se intampla sa semene? Daca e prima, `items[]` ar trebui sters, nu
      alimentat.

- [x] CD: deploy automat pe git | req: ARCH-RELEASE-072
      <!-- v7.21.0, ADR-0040. Numărul vine din plan: `sync --release --apply` ia cel mai mic
           milestone planificat peste versiunea declarată, face bump-ul, scrie intrarea de
           CHANGELOG și scoate milestone-ul din plan. Tag-ul rămâne în CI. Nota de mai jos
           e starea de dinainte. -->
      Jumatate exista deja: la push pe `main`, jobul `release` taie tag-ul din
      `plugin.json`, creeaza release-ul cu notele extrase din CHANGELOG si muta
      aliasul `check@vN` pe commit-ul tagged. E idempotent, deci un push care nu
      bumpeaza nu creeaza nimic.

      Ce e MANUAL si de asta deploy-ul nu e automat: bump-ul insusi. Cineva editeaza
      versiunea in trei locuri si scrie intrarea de CHANGELOG inainte de push, iar
      `check_versions.py` doar verifica dupa aceea ca cele trei sunt aliniate.

      Deci intrebarea nu e "cum publicam automat" - se publica deja - ci "de unde
      stie masina CE numar sa puna". Raspunsul trebuie sa fie derivabil din commit,
      nu ghicit: fie un trailer pe commit, fie o eticheta pe PR. Pana nu e ales
      unul, automatizarea ar bumpa dupa o regula pe care nimeni n-a scris-o.

- [x] `gate` ≤ 12 flag-uri. Audit / risk / show rămân; restul coboară din calea verdictului | req: ARCH-CMDREGISTRY-033
      <!-- v7.22.0, ADR-0044 (Senate 2026-09-17, MODIFY, condițiile în ADR). `gate` are 9
           flag-uri, întrebările au plecat pe verbul `ask`. Vechile forme `gate --search` & co.
           merg până la v8.0.0 cu o linie pe stderr; bara de mai jos le scoate. -->
- [x] Scoate verbul `new` și `new --from-todo` (ADR-0045) | req: ARCH-NEW-004
      <!-- REQ-NEWGONE-1034. Motorul are șase verbe: `init`, `gate`, `ask`, `sync`,
           `clarify`, `mcp`. Au plecat `cmd_new`, `cmd_promote_todo`, `_mark_todo_done`,
           `--id` / `--from-todo` / `--mark-done`, intrarea din registru, tool-ul MCP
           `reqmap_new` și ~20 de teste; `new` a intrat în paznicul de verbe retrase.
           ARCH-NEW-004 și ARCH-PROMOTE-TODO-001 (cu cei 6 copii) sunt `deprecated`, nu
           șterse — un tag vechi sau un ADR care le numește tot găsește ce descriau. -->
      <!-- Ce a RĂMAS, deliberat (ADR-0045 decizia 3): `REQUIREMENT_TEMPLATE` — forma
           documentată după care scrii fișierul — plus `_parse_todos`,
           `_set_frontmatter_status`, `_write_frontmatter_status`, pe care le citesc
           `gate`, `retire`, `mapcmd` și `mapdata`. Bara rămâne în v8.0.0: versiunea se
           taie când intră și celelalte două (alias-urile `gate --…`, split-ul viewer-ului). -->
- [x] Scoate alias-urile `gate --search` / `--dupes` / `--design` / `--review` / `--i18n` / `--top` / `--threshold` (ADR-0044) | req: ARCH-CMDREGISTRY-033
- [x] README de 90 de linii: problemă, `init` / `sync` / `gate`, exemplul lucrat, action. Fără V-model în primul ecran | req: SYS-SSOT-001
      <!-- 527 -> 92 de linii. Nimic nu s-a pierdut: secțiunile tăiate au plecat verbatim în
           cinci pagini de referință, `docs/commands.md`, `docs/requirements.md`,
           `docs/integrations.md`, `docs/planning.md`, `docs/internals.md`, linkate dintr-un
           tabel la final. V-modelul (nivelurile de specificație) trăiește acum în
           `docs/requirements.md`, deci nu mai e în primul ecran — era la linia 139.
           Cele cinci pagini intră în `.reqmapignore` din aceleași motive ca README.md. -->
- [x] Health: un snapshot, untagged, semnalele noi de orizont | req: ARCH-HEALTH-017
      <!-- REQ-PLANGAPS-1033. Snapshot-ul și untagged existau; noutatea e bucket-ul `Plan`
           din `gate --risk`: itemi `Now`/`Next` fără bară, `Later` fără `unpark:`, `req:`
           care nu există. Semnalele nu sunt noi — trăiau doar în coada lui `sync` și în
           `gate --audit`, adică nu pe ecranul care pune exact întrebarea asta.
           `_roadmap_plan_gaps` e singurul predicat, deci linia din audit și bucket-ul nu
           pot ajunge să însemne lucruri diferite; `plan_gaps` intră și în `--json`. -->
      <!-- `risk.py` importă `mapdata` la apel, nu la import: `mapdata` citește
           `_risk_signals` din `risk`. Al doilea import de felul ăsta din motor. -->
- [x] `TODO.md` → `docs/history/TODO-archive.md`. Viewer-ul citește doar ROADMAP.md | req: ARCH-ROADMAP-038
      <!-- 2026-09-14. Motorul citeşte în continuare `TODO.md` oriunde un consumator
           ţine unul — capacitatea rămâne; repo-ul ăsta pur şi simplu nu mai are unul.
           Arhiva NU e citită: dacă ar fi, ar fi tot un plan viu, iar mutarea n-ar
           însemna nimic. Consecinţa intenţionată: cele trei semnale de roadmap din
           `gate --audit` tac aici, iar graficul se alimentează doar din `milestone:`. -->
- [x] `init` spune o dată că roadmap-ul e inert, când planul n-are niciun titlu de versiune | req: ARCH-INIT-012
      <!-- v7.21.7, REQ-ROADMAP-983 CASE-5. -->
      <!-- Ultimul rest din TODO-feedback-management-dashboard.md §14, propunerea 2,
           înainte ca fişierul să fie şters pe 2026-09-14. Propunerea 1 a intrat în
           v7.5.0 (`gate --audit` tipăreşte semnalele de roadmap); 3 e alternativa ei
           şi a fost acoperită parţial de orizonturile din ROADMAP.md. Asta a rămas:
           `init.py` nu numeşte azi nici TODO nici roadmap, deci un repo al cărui plan
           n-are titluri `## vX.Y` nu află niciodată că jumătate dintr-o funcţie nu i
           se aplică — tăcerea e indistinctă de „totul e în regulă". -->
- [x] Scoate tab-ul Spec: Explorer randa deja acelaşi `SpecDoc` | req: ARCH-VIEWER-007
      <!-- v7.6.0. `SpecView.jsx` -> `SpecDoc.jsx`; a plecat doar tab-ul şi navigaţia lui. -->
- [x] Planificatorul pune un release la fiecare sfârşit de lună | req: ARCH-MAP-007
      <!-- v7.6.0, REQ-PLANCADENCE-1000. `cadence: {every, on, from, until}` în
           _planning.json; azi doar `every: week`. Un configurator peste asta e o
           extindere a cheii, nu o rescriere. -->
- [x] Istoricul livrat, pe aceeaşi axă cu planul | req: ARCH-MAP-007
      <!-- v7.8.0, REQ-HISTORY-1003. Banda `Shipped` din Gantt, o linie per lună,
           citită din CHANGELOG.md. 100 de release-uri, 2026-06-04 -> azi. -->
- [ ] Split ARCH-VIEWER-007: artefactul HTML vs. ce randează | req: ARCH-VIEWER-007

<!-- Valul 2 — produsul pe care-l țin minte (2 săptămâni) -->
- [ ] V2: Parser din registry după v8, nu în v8 — subparser per verb. Gata când: `reqmap gate --wipe` e `unrecognized arguments`, nu no-op tăcut | req: ARCH-CMDREGISTRY-033
- [ ] V2: `--attach`, `--no-lint`, `--no-map-check` intră în `COMMANDS` sau mor. Gata când: SKILL / viewer / schema OpenAI / `--help` spun același lucru | req: ARCH-CMDREGISTRY-033
- [ ] V2: SKILL.md ecranul 1 = 40 de linii; i18n, site, decompose, release → `references/`. Gata când: un agent nou citește 40 de linii și rulează `init` + `gate` corect | req: SYS-AUTHOR-101
- [ ] V2: `init --no-site` implicit; piramida V-model iese din primul contact, `clarify --levels` rămâne. Gata când: `init` pe un repo de 12 fișiere nu scrie ARCH+SYS | req: ARCH-INIT-012
- [ ] V2: Un model de tool, nu două — schema OpenAI generată din `MCP_TOOLS`. Gata când: Copilot și Claude văd aceleași tool-uri, nu `reqmap_gate` cu 9 proprietăți | req: ARCH-MCP-073
- [ ] V2: Freeze MCP — nicio unealtă nouă până n=2 folosește serverul. Gata când: CHANGELOG-ul următor nu conține mcp | req: ARCH-MCP-073
<!-- Valul 4 — adopție care nu e marketing (continuu) -->
- [ ] V4: Repo-template `hello-reqmap`, nu dogfood-ul. Gata când: „Use this template” produce un gate care trece | req: ARCH-INIT-012
- [ ] V4: Cadență: 1 release / săptămână. Gata când: septembrie viitor are ≤5 tag-uri, nu 97 | req: ARCH-RELEASE-072
- [x] V4: Health 100/100 cu 13 `lint_exempt` nu se mai publică ca scor — scoate badge-ul sau pune numărul de scutiri lângă el. Gata când: un auditor nu citește 100/100 ca „corpus perfect” | req: ARCH-HEALTH-017
- [ ] V4: Un canal public (Discussions / show-and-tell). Gata când: primul screenshot dintr-un repo străin e acolo, nu în DM | req: SYS-SSOT-001

## Later

- [x] MCP server, stdlib, din registrul de comenzi | unpark: consumator numit care nu poate CLI
      <!-- v7.21.12, ADR-0043. Deblocat de decizia maintainerului („MCP e un must have”), nu de
           condiția din unpark: `reqmap.py mcp`, 15 tool-uri, read-only fără --allow-writes.
           v7.21.13: JSON pentru show/search/dupes și resursele reqmap://map și
           reqmap://requirement/<id>. În _planning.json, bara „Server MCP” e la 100%. -->
- [ ] Licență Apache-2.0 / MIT în loc de BSL 1.1 | unpark: primul evaluator intern într-o firmă care cere grant
- [ ] Search RO: rank pe flexiuni, nu match literal | unpark: un cititor din afara repo-ului care folosește viewer-ul în RO

<!-- Valul 3 — taie ce nu e produsul (după n=2, 1–2 săptămâni) -->
- [ ] V3: Deconectează `_design_summary` din health / mapcmd / audit. Gata când: `ask --design` e singurul import | req: ARCH-DESIGN-061 | unpark: n=2 verde (Consilium-py pe check@v8, 7 zile)
- [ ] V3: Șterge `design*.py` (722 linii). Gata când: `ask --design` e unknown, motorul < 14.500 linii | req: ARCH-DESIGN-061 | unpark: n=2 verde și `_design_summary` deconectat
- [ ] V3: `init` nu mai scrie `architecture.html`; `site.py` + `site_template.py` pleacă sau devin opt-in pe `sync --attach`. Gata când: un consumer nu găsește `docs/architecture.html` după `init` | req: ARCH-SITE-026 | unpark: n=2 verde
- [ ] V3: Nu mai comite `_i18n/ro.json` (701 KB); `i18n.py` rămâne detector de gap. Gata când: clone-ul e ~9% mai mic, `ask --i18n` tot merge | req: ARCH-TRANSLATE-044 | unpark: n=2 verde
- [ ] V3: Piramida iese din `init`; `pyramid.py` + `levels.py` rămân pe `clarify --levels`, `axis.py` stă. Gata când: primul contact e plat | req: ARCH-LEVELRETROFIT-066 | unpark: n=2 verde
- [x] V3: Nu tăia `new` înainte de v8 — v8 conform ADR-0045, nu hotfix | req: ARCH-NEW-004 | unpark: v8.0.0
      <!-- Deja depășit: `new` a fost scos în #319 (ebe4061) și bara e în v8.0.0. -->

## Not now

- Comparație cu OpenFastTrace / Doorstop / rmtoo în README — respinsă de maintainer pe 2026-09-21 (PR #325 închis)
- Requirement history — `git log -L` pe blocul cerinței ajunge
- `verifiable by:` umplut de la 2 la 54 — ADR-0016 a respins un marker la 4% adopție
- Formă atomică (54 → ~665 noduri) — ADR-0025
- Fan-out hard pe gate — rămâne warn-only (ADR-0023)
- `clarify --levels` — până la un ADR care îl înlocuiește pe 0031 (revisit 2027-03-06)
