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

- [ ] `gate` ≤ 12 flag-uri. Audit / risk / show rămân; restul coboară din calea verdictului | req: ARCH-CMDREGISTRY-033
- [ ] README de 90 de linii: problemă, `init` / `sync` / `gate`, exemplul lucrat, action. Fără V-model în primul ecran | req: SYS-SSOT-001
- [ ] Health: un snapshot, untagged, semnalele noi de orizont. Design review jos de pe calea verdictului | req: ARCH-HEALTH-017
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

## Later

- [x] MCP server, stdlib, din registrul de comenzi | unpark: consumator numit care nu poate CLI
      <!-- v7.21.12, ADR-0043. Deblocat de decizia maintainerului („MCP e un must have”), nu de
           condiția din unpark: `reqmap.py mcp`, 15 tool-uri, read-only fără --allow-writes.
           v7.21.13: JSON pentru show/search/dupes și resursele reqmap://map și
           reqmap://requirement/<id>. În _planning.json, bara „Server MCP” e la 100%. -->
- [ ] n=2: Consilium-py pe `uses: alxmax/requirement-manager/check@v7`. Job-ul `gate`: scoate `setup-python` + `python scripts/reqmap.py gate`, pune action-ul; păstrează `map --check` până re-vendorizezi motorul | unpark: Consilium-py are action-ul pe `main`, verde 7 zile
- [ ] Licență Apache-2.0 / MIT în loc de BSL 1.1 | unpark: primul evaluator intern într-o firmă care cere grant
- [ ] Search RO: rank pe flexiuni, nu match literal | unpark: un cititor din afara repo-ului care folosește viewer-ul în RO

## Not now

- Requirement history — `git log -L` pe blocul cerinței ajunge
- `verifiable by:` umplut de la 2 la 54 — ADR-0016 a respins un marker la 4% adopție
- Formă atomică (54 → ~665 noduri) — ADR-0025
- Fan-out hard pe gate — rămâne warn-only (ADR-0023)
- `clarify --levels` — până la un ADR care îl înlocuiește pe 0031 (revisit 2027-03-06)
