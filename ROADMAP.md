# Roadmap

Planul produsului. Nu e jurnal. Versiunile trăiesc în CHANGELOG și în tag-ul git.

Editezi în [docs/roadmap-preview.html](docs/roadmap-preview.html) (browser, fără motor) și, dacă vrei copia în git, înlocuiești acest fișier. Scena tragibilă: [docs/planning/roadmap.excalidraw](docs/planning/roadmap.excalidraw).

Format: `- [ ] text | req: ID` pe Now/Next. Later cere `unpark:`.
Heading-uri rezervate: Now, Next, Later, Not now. Nimic altceva la `## `.

## Now

- [ ] n=2: un repo care nu e ăsta rulează `uses: alxmax/requirement-manager/check@v7` pe `main`, verde, 7 zile | req: SYS-SSOT-001
- [ ] Scoate `gate --implement` (ADR-0037 pass 2). Înainte, `clarify` nu mai tipărește `next: gate --implement` | req: ARCH-CMDREGISTRY-033
- [ ] Parserul citește `ROADMAP.md` înaintea lui `TODO.md`; heading-uri Now/Next/Later | req: ARCH-ROADMAP-038
- [ ] Viewer Roadmap: orizonturi Now / Next / Later, nu Gantt pe fiecare minor | req: ARCH-VIEWER-007
- [ ] RM025 și `roadmap_unmapped` numesc un next-step | req: ARCH-ROADMAP-038

## Next

- [ ] `gate` ≤ 12 flag-uri; `sync --help` numește pasurile pe care le rulează | req: ARCH-CMDREGISTRY-033
- [ ] README de 90 de linii: problemă, 3 comenzi, exemplul lucrat, action. Fără V-model în primul ecran | req: SYS-SSOT-001
- [ ] Health: un snapshot, untagged, semnalele noi de orizont. Design review jos de pe calea verdictului | req: ARCH-HEALTH-017
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
