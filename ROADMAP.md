# Roadmap

Planul produsului. Nu e jurnal. Versiunile trăiesc în CHANGELOG și în tag-ul git.

Editezi în [docs/roadmap-preview.html](docs/roadmap-preview.html) (browser, fără motor) și, dacă vrei copia în git, înlocuiești acest fișier. Scena tragibilă: [docs/planning/roadmap.excalidraw](docs/planning/roadmap.excalidraw).

Format: `- [ ] text | req: ID` pe Now/Next. Later cere `unpark:`.
Heading-uri rezervate: Now, Next, Later, Not now. Nimic altceva la `## `.

## Now

- [ ] n=2: Consilium-py, `uses: alxmax/requirement-manager/check@v7` pe `main`, verde 7 zile. Job-ul `gate`: scoate `setup-python` + `python scripts/reqmap.py gate`, pune action-ul; păstrează `map --check` până re-vendorizezi motorul (2026-06-19.1). | req: SYS-SSOT-001
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
- [ ] Viewer Roadmap: trei coloane Now / Next / Later când orizonturile există | req: ARCH-VIEWER-007
      <!-- Debifat 2026-09-13: `RoadmapView.jsx` n-are niciun „Now"/„Next"/„Later". Are două
           moduri, Plan (Gantt) și Versions (grila de chip-uri), ambele pe milestone-uri.
           Motorul citește acum orizonturile, deci datele există; viewer-ul nu le arată. -->
- [ ] `roadmap_unmapped` / heading-uri fără milestone numesc un next-step | req: ARCH-ROADMAP-038
      <!-- Debifat 2026-09-13: `audit.py:183-188` se opreşte la constatare în ambele cazuri.
           `roadmap_unmapped` are deja răspunsul — adaugă `milestone:` la cerinţele care au
           ieşit în versiunile alea. Vezi şi TODO.md v5.13, care cere acelaşi lucru. -->
- [x] `clarify` nu mai tipărește `next: gate --implement` | req: ARCH-CMDREGISTRY-033
- [x] `sync --help` numește pașii (scan → drift → lock → map → findings → site) | req: ARCH-CMDREGISTRY-033
- [x] Scoate `gate --implement` (ADR-0037 pass 2) | req: ARCH-CMDREGISTRY-033

## Next

- [ ] `gate` ≤ 12 flag-uri. Audit / risk / show rămân; restul coboară din calea verdictului | req: ARCH-CMDREGISTRY-033
- [ ] README de 90 de linii: problemă, `init` / `sync` / `gate`, exemplul lucrat, action. Fără V-model în primul ecran | req: SYS-SSOT-001
- [ ] Health: un snapshot, untagged, semnalele noi de orizont. Design review jos de pe calea verdictului | req: ARCH-HEALTH-017
- [ ] `TODO.md` → `docs/history/TODO-archive.md`. Viewer-ul citește doar ROADMAP.md | req: ARCH-ROADMAP-038
- [ ] Split ARCH-VIEWER-007: artefactul HTML vs. ce randează | req: ARCH-VIEWER-007

## Later

- [ ] MCP server, stdlib, din registrul de comenzi | unpark: consumator numit care nu poate CLI
- [ ] Licență Apache-2.0 / MIT în loc de BSL 1.1 | unpark: primul evaluator intern într-o firmă care cere grant
- [ ] Search RO: rank pe flexiuni, nu match literal | unpark: un cititor din afara repo-ului care folosește viewer-ul în RO

## Not now

- Requirement history — `git log -L` pe blocul cerinței ajunge
- `verifiable by:` umplut de la 2 la 54 — ADR-0016 a respins un marker la 4% adopție
- Formă atomică (54 → ~665 noduri) — ADR-0025
- Fan-out hard pe gate — rămâne warn-only (ADR-0023)
- `clarify --levels` — până la un ADR care îl înlocuiește pe 0031 (revisit 2027-03-06)
