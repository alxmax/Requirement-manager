# Roadmap

Planul produsului. Nu e jurnal: ce s-a livrat trăiește în CHANGELOG și în tag-urile git, iar un
item bifat pleacă de aici.

Editezi aici, direct. Barele din Gantt-ul viewer-ului se scriu în `plugin/requirements/_planning.json`.

Format: `- [ ] text | req: ID` pe Now/Next. Later cere `unpark:`.
Heading-uri rezervate: Now, Next, Later, Not now. Categoriile sunt `###` în interiorul lor.
Cadență: un release pe săptămână, nu unul pe fiecare merge.

## Now

### Adopție

- [ ] Consilium-py rămâne verde pe `check@v8`. Gata când: cel puțin 5 rulări verzi pe `main` de la re-vendorizare (2026-09-21, Consilium-py #63) | req: ARCH-SELFGATE-039
- [ ] Un evaluator din afară, pe repo-ul lui, fără ajutor la gate. Gata când: are `uses: alxmax/requirement-manager/check@v8` pe un tree în care nu faci commit | req: SYS-SSOT-001

## Next

### Documentație

- [ ] SKILL.md: primul ecran de 40 de linii; i18n, site, decompose și release trec în `references/`. Gata când: un agent nou citește 40 de linii și rulează corect `init` și `gate` | req: SYS-AUTHOR-101

### Viewer

- [ ] Split ARCH-VIEWER-007: artefactul HTML vs. ce randează | req: ARCH-VIEWER-007

## Later

### Suprafața motorului

- [ ] Următoarea tăietură din motor: o capabilitate din lista celor care pot pleca (`gate --risk`/`--audit`, `clarify`/decompose, `ask`, lint, `sync --retire`), cu ADR, retire și bugetul coborât în același commit. Podeaua cu ROADMAP, MCP și `init` păstrate: 9.303 linii (ADR-0048) | req: ARCH-SELFGATE-039 | unpark: maintainerul numește capabilitatea
- [ ] Lista de tool-uri MCP și schema OpenAI generate din același registru `COMMANDS` (ADR-0008) | req: ARCH-MCP-073 | unpark: freeze-ul MCP e ridicat

### Adopție

- [ ] Repo-template `hello-reqmap`: „Use this template” produce un gate care trece | req: ARCH-INIT-012 | unpark: un evaluator raportează că `init` l-a lăsat baltă
- [ ] Licență Apache-2.0 / MIT în loc de BSL 1.1 | unpark: primul evaluator intern într-o firmă care cere grant

### Viewer

- [ ] Search RO: rank pe flexiuni, nu match literal | unpark: un cititor din afara repo-ului care folosește viewer-ul în RO

## Not now

- Requirement history — `git log -L` pe blocul cerinței ajunge
- `verifiable by:` umplut de la 2 la 54 — ADR-0016 a respins un marker la 4% adopție
- Formă atomică (54 → ~665 noduri) — ADR-0025
- Fan-out hard pe gate — rămâne warn-only (ADR-0023)
- `clarify --levels` — până la un ADR care îl înlocuiește pe 0031 (revisit 2027-03-06)
