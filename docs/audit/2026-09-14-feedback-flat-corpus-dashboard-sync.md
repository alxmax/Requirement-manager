# Feedback din teren — de ce un corpus tagat 96% rămâne plat (0 `code`, 1 `system`)

- **Sursa:** Dashboard_Sync (consumator real), engine vendorat `2026-09-14.1` (plugin 7.8.1), 2026-09-14
- **Corpus la momentul măsurării:** 195 requirements (150 confirmed, 40 draft), 423 membri, 106 requirements cu test, 274 fișiere scanate dintre care 263 tagate (96%). Toate 195 fără `level:`.
- **Întrebarea proprietarului:** de ce engine-ul nu generează și requirement-uri `level: code` și `level: system`.
- **Metoda:** fiecare cifră de mai jos e ieșirea comenzii numite lângă ea, pe working tree-ul zilei. Referințele `fișier:linie` sunt în `scripts/reqmap_engine/` din plugin 7.8.1.

## Răspunsul scurt

Corpusul e plat din trei cauze care se adună, niciuna un bug în sine — dar împreună fac ca piramida să fie **de neatins** pentru exact tipul de repo pentru care merită: unul vechi, tagat de mână, cu teste.

1. **`init` mintează rungurile doar pentru ce EXTRAGE el** (ADR-0030, `init.py:185-197`). Un corpus tagat înainte de 2026-09-06 nu primește nimic; cele 40 de `DRAFT-*` din repo au și ele `level:` lipsă (0/40) pentru că au fost extrase înainte de axă, iar `init` nu rescrie fișiere existente.
2. **Retrofitul `clarify --levels` propune `code` doar cu `verifies:`** (`levels.py:_propose_levels`, regula a 4-a: `impls and len(labels) >= LINT_AC_MIN and covered`, unde `covered` vine din `AC_VERIFY_RE` = `verifies: ID#CASE-N`, `tags.py:47`). Repo-ul are **0** tag-uri `verifies:` și **122** fișiere de test legate prin `tested-by:` la nivel de fișier. Rezultatul pe 195 de requirements: **194 architecture, 1 system, 0 code**, fiecare cu motivul „no decomposed-behaviour evidence (N case(s), 0 verified, M member(s))" — deși 106 dintre ele AU teste.
3. **`system` vine exclusiv din `layer: need`** (regula 1 din `_propose_levels`) și ADR-0036 refuză deliberat să-l derive din `depends_on`. Repo-ul are un singur `layer: need` (BUS-RISKRAILS-001) → un singur `system`. Pentru un corpus pornit la architecture nu există nicio cale, nici măcar opt-in, spre rungul de sus.

Pe scurt: mesajul „no decomposed-behaviour evidence" e literalmente adevărat și practic înșelător. Cititorul înțelege „n-ai teste"; realitatea e „ai teste pe canalul pe care regula nu-l citește".

## Dovezile

```
$ REQMAP_EXTRA_CODE_EXTS=.mq4,.mqh python -X utf8 requirements/reqmap.py clarify --levels
  ...
  architecture   VOL-REGIME-001   no decomposed-behaviour evidence (5 case(s), 0 verified, 1 member(s))
  No requirement is proposed at `code`. ...
  system         BUS-RISKRAILS-001   layer: need already says stakeholder need
$ ... | grep -oE "\b(system|architecture|code)\b" | sort | uniq -c
    194 architecture
      1 code        <- apare doar în textul explicativ, nu ca propunere
      1 system

$ grep -rn "verifies:" --include=*.py --include=*.js --include=*.mq4 . | grep -v requirements/reqmap | wc -l
0
$ grep -rln "tested-by:" tests/*.py | wc -l
122
$ grep -l "^layer: need" requirements/*.md | wc -l
1
$ grep -l "^level:" requirements/DRAFT-*.md | wc -l      # din 40
0
```

## Observații colaterale (găsite pe drum, fiecare cu reproducere)

### A. UTF-16 e invizibil pentru scanner, fără niciun avertisment
`scan.py:187` și `:232` deschid sursele cu `encoding="utf-8", errors="ignore"`. Un `.mq4` UTF-16 LE (MetaEditor le salvează adesea așa) se citește ca octeți intercalați cu NUL: orice tag din el e invizibil, fișierul raportează „untagged" la nesfârșit, iar LOC-ul se dublează.

```
$ file mt4/indicatorarrowsMODIF.mq4
... UTF-16, little-endian text, with CRLF line terminators
$ iconv -f UTF-16LE -t UTF-8 mt4/indicatorarrowsMODIF.mq4 | wc -l
2041
$ python requirements/reqmap.py init --plan --out plan.json
  NEW: MT4-INDICATORARROWSMODIF-001 ['mt4/indicatorarrowsMODIF.mq4'] loc 4089    <- 2 × 2041
```
Repo-ul a mai fost mușcat o dată (Write tool → UTF-16 → tag „dispărut", notat în `tools/gen_madistance_rsi_pptx.py:344`). Engine-ul știe deja de BOM-ul UTF-8 (`parse.py:61,111`, `author.py:267`), dar nu și de `FF FE` / `FE FF`.

**Propunere:** în `scan.py`, înainte de decodare, dacă primii 2 octeți sunt `FF FE`/`FE FF` → decodează UTF-16; altfel, dacă textul conține `\x00`, emite `WARN RMxxx <path>: not UTF-8 (UTF-16?) — tags in it are invisible` și sări fișierul din LOC. Cost: două comparații pe fișier.

### B. `init`/`draft` scrie stub-ul, dar nu tag-ul — sursa rămâne „untagged" pentru totdeauna
`draft.py:109,143` scriu fișierul requirement; nicio linie din `draft.py`/`init.py` nu inserează tag-ul de membru în sursă (singurul cod care atinge tag-uri în sursă e `_strip_line_tag`, pentru `--wipe`). Consecință în repo: 5 stub-uri (`DRAFT-TESTS-TEST-{CONSOLE-CONFIG,TL5-POST-RESULT,TL8-MAE-STOP}`, `DRAFT-MT4-{WPR-SRZONES-BETA,INDICATORARROWSMODIF}`) cu 0 membri, iar cele 5 fișiere-sursă listate ca „untagged" de `gate --risk` — deși stub-ul lor există. Omul a curățat de mână 11 astfel de stub-uri în Task 13 (2026-08-26) și încă 4 azi.

**Propunere:** `init` inserează `# implements: <DRAFT-ID>` (respectiv `tested-by:` pentru fișierele `is_test`) pe prima linie non-shebang a sursei, cu aceeași grijă de EOL/BOM ca `_apply_level` (`levels.py:104`). Dacă asta e o decizie deliberată („engine-ul nu scrie în cod"), atunci `gate --risk` ar trebui să spună „stub exists, source untagged: run X" în loc să propună `init` din nou.

### C. `init --plan` și write path-ul nu au aceeași definiție de „tagat"
`candidates.py:246` decide `existing_req` printr-un dict `tagged[file]`; `draft.py:253` construiește `tagged` din **toate** rolurile (`members.values()`). Planul listează 123 candidați NEW pe un corpus 96% tagat, dintre care ~120 sunt teste care au deja `tested-by:`:

```
candidates total 224 | existing_req set 101 | would be NEW drafts 123
  NEW: TESTS-TEST-ACC-GROUP-FILTER-001 ['tests/test_acc_group_filter.py']   <- linia 1: # tested-by: JS-FILTERS-001
```
Nu am verificat dacă write path-ul le-ar scrie efectiv (nu am rulat `init` fără `--plan` pe repo); dar `--plan` există tocmai ca să arate ce ar face `init`, iar aici arată altceva. Cele 31 de `DRAFT-TESTS-TEST-*` rămase în repo sugerează că, la un moment dat, chiar au fost scrise.

**Propunere:** un singur helper `_tagged_files(members, roles=...)` folosit de ambele; `is_test` + `tested-by:` prezent = acoperit, nu candidat.

### D. `--plan` nu arată piramida
`plan.json` conține 0 chei `level`. Rungurile se mintează la scriere, deci nu poți previzualiza ce sistem/arhitectură ar propune `init` înainte să scrie 123 de fișiere. `--plan` ar trebui să poarte `level` per candidat, plus placeholder-ul de sistem pe care ADR-0036 spune că `init` îl draftează.

### E. Două numărători de „untagged" cu denominatoare diferite
`sync` a raportat „9 code file(s) traced to no requirement"; `gate --risk --untagged` a raportat 263/274 (= 11). După tagarea celor 9: 270/272 — cele 2 rămase sunt în rădăcină (`. 3/5`), nu au apărut niciodată în bucket-ul „Untagged files" și nu sunt numite nicăieri. Ambele rapoarte ar trebui să numească aceeași listă, sau să spună de ce diferă.

## Cerința proprietarului: `init` ar fi trebuit să genereze requirement-uri pe 3 nivele

Nu „poate primi rungurile mai târziu, opt-in" — ci **la `init`**, corpusul iese pe trei
nivele, pentru că așa e definit de propriul gate (`RM032`): fiecare `architecture` e un grup
care are un `system` deasupra (prin `satisfies:`) și cel puțin un `code` dedesubt. Un `init`
care scoate doar rungul din mijloc produce, prin construcție, un corpus pe care `sync` îl
avertizează de două ori per requirement. Concret, `init` (și retrofitul pentru un corpus
existent) ar trebui să scrie:

1. **system** — câte un `layer: need` draft per familie de capabilități (semnalul e declarat
   de autor: prefixele de ID — aici `JS` 26, `AI` 25, `DASH` 16, `BUS` 13, `TL` 6, `MFEMAE` 5,
   `CONSOLE` 5 — sau directoarele sursă), cu `satisfies:` completat invers pe fiecare
   architecture din familie. ADR-0036 refuză derivarea din `depends_on`; prefixele nu sunt
   `depends_on`.
2. **architecture** — ce face azi.
3. **code** — copiii pe care `clarify --decompose` îi știe deja construi (aici 10, din 4
   părinți), plus câte un copil per requirement marcat `lint_exempt: over-scoped` (7 aici —
   exemptarea e engine-ul spunând „ăsta e mai multe lucruri").

Toate ca `draft`, toate `level_source: auto`, toate reversibile — exact contractul ADR-0030/0031.
Diferența e că rezultatul trece propriul gate cu 0 avertismente în loc de 304.

### F. `clarify --levels --apply` produce o stare pe care gate-ul o respinge de 304 ori

Rulat pe corpus (branch `chore/reqmap-levels-apply`, 2026-09-14):

```
$ python requirements/reqmap.py clarify --levels --apply
194 requirement(s) updated.
$ python requirements/reqmap.py sync
WARN  RM032 A2-ENTRY-LOCK-001: level: architecture groups no `level: code` requirement — every architecture is a group; give it a member one rung down, or move it down a rung
WARN  RM032 A2-ENTRY-LOCK-001: level: architecture satisfies nothing — every architecture belongs to a `level: system` group; declare `satisfies:`
...
194 requirements (152 confirmed, 0 legacy-schema), 436 members, 0 errors, 304 warnings.
```

304 = 152 confirmed × 2 (cele 40 de drafturi și cele 2 baseline nu sunt verificate de RM032).
Înainte de `--apply`: **0 warnings**. Deci singura comandă care dă rungurile unui corpus
existent îl duce, prin construcție, din „gate curat" în „304 avertismente permanente" —
starea despre care skill-ul însuși spune că antrenează reflexul de a nu mai citi gate-ul.
Retrofitul (ADR-0031, 2026-09-06) și regula RM032 (engine 2026-09-14) au fost scrise de
aceeași mână la câteva zile distanță și nu au fost rulate una după alta pe un corpus real.

**Propunere:** `clarify --levels --apply` fie construiește toate cele trei runguri (punctul
de mai sus), fie refuză să scrie doar rungul din mijloc când RM032 e activ, cu mesajul
„this would raise N RM032 warnings; run with `--three-rungs` or add `satisfies:` first".
Testul de regresie e simplu: `init` pe un repo de probă → `sync` → 0 RM032.

## Ce ar debloca piramida pe un corpus ca ăsta (în ordinea cost/beneficiu)

1. **Mesaj sincer în `clarify --levels`** (cost minim): când `covered == 0` dar requirement-ul are membri `tested-by:`, motivul devine „N tested-by link(s), 0 `verifies:` — the code rung needs a case linked to a test; see `clarify --link-cases`". Azi mesajul ascunde singura acțiune care ar schimba ceva.
2. **`clarify --link-cases <ID>`** (nou, read-only, `--apply` scrie): propune `# verifies: ID#AC-n` în fișierele `tested-by:` ale requirement-ului, potrivind numele funcțiilor de test cu etichetele AC (lexical, ca `gate --search`). Pe repo-ul ăsta ar avea 122 de fișiere și ~430 de AC-uri de lucrat — de mână nu se va întâmpla niciodată, deci `code` rămâne o rungă teoretică.
3. **Opțional, sub config (`CODE_RUNG_ACCEPT_TESTED_BY: true`)**: `tested-by ... @unit` + `len(labels) >= LINT_AC_MIN` contează ca dovadă slabă pentru `code`, cu motivul marcat „weak: file-level test link". Respectă ADR-0031 (opt-in, marcat, reversibil) și dă corpusurilor vechi o rungă intermediară în loc de zero.
4. **Rungul de sistem pentru corpusuri pornite la architecture**: ADR-0036 refuză derivarea din `depends_on` — corect. Dar prefixele de ID sunt un semnal **declarat de autor**, nu inferat din graf: aici `JS` 26, `AI` 25, `DASH` 16, `BUS` 13, `MFEMAE` 5, `CONSOLE` 5. `clarify --levels --system-from-prefixes` ar putea propune câte un `layer: need` draft per familie ≥ N, cu `satisfies:` propus invers, tot opt-in și tot `level_source: auto`. Dacă și asta e refuzată, măcar `init` să ofere placeholder-ul de sistem și pe un corpus existent, nu doar la extracție.

## Ce s-a făcut în consumator azi (pentru context, nu cerere)
Cele 9 fișiere au fost rezolvate de mână: 3 teste → `tested-by:` pe requirement-uri reale (două noi, `TL-5`/`TL-8`, autorate după modelul `TL-6`), 2 hook-uri git → `REPO-GATES-001` nou, `.mq4`-ul UTF-16 → convertit UTF-8 + tagat, 2 fișiere → `.reqmapignore` cu motivul scris (unul pentru că propriul header interzice tagul). Gate: 0 erori / 0 avertismente; 4 stub-uri `DRAFT-*` orfane șterse. Corpusul a rămas plat — nimic din cele de mai sus nu-l putea mișca fără schimbări în engine. `clarify --levels --apply` a fost rulat apoi pe un branch separat (F de mai sus): 193 architecture + 1 system, 304 RM032 — nemerge-uit.

## Status — rezolvat în aceeași zi (ADR-0038, plugin 7.9.0, engine `2026-09-14.2`)

Modelul a rămas cel al requirement manager-ului — *fiecare `code` are un `architecture`,
niciun `architecture` fără `code`*, RM032 neschimbat. S-a corectat **clasificarea**, nu regula:

- `clarify --levels --apply` propune `code` pentru orice requirement legat de cod (un fișier =
  un grup de comportament; sub-specificarea rămâne treaba lint-ului) și `architecture` doar cu
  dovadă de grup (≥ 2 grupuri de contract sau `lint_exempt: over-scoped/ac-count-high`).
  Scrie apoi rungurile de sus în forma lui `init`: `ARCH-<FAMILIE>-001` draft per familie de
  prefix cu ≥ `LEVEL_FAMILY_MIN` (3) membri (restul sub `ARCH-NEEDS-A-NAME-001`),
  `SYS-NEEDS-A-NAME-001` la vârf (golul lui `init`, scris de funcția lui), `satisfies:` de la
  fiecare `code` la familie și de la fiecare placeholder / architecture nelegat la vârf.
  Stub-urile `draft` sărite. Idempotent, reversibil, `level_source: auto` peste tot.
- Pe Dashboard_Sync (PR #712): **2 system / 19 architecture / 195 code**, 11 `ARCH-*` + 1
  `SYS-*`, 176 muchii, gate **0 errors, 3 warnings** — cele 3 sunt singurele architecture
  fără code: grupuri prin propria exemptare `over-scoped`, fără grupuri de contract de
  despărțit. Înainte: 0 / 194 / 0 și, după vechiul `--apply`, 1 / 193 / 0 cu 304 avertismente.
- Două tăieturi retrase pe drum, cu motiv: (1) familiile ca `system` — 48 de placeholder-e
  fără prag (45 de prefixe, 33 cu un singur membru, plus o „familie" `DRAFT` de 36 de stub-uri)
  și o piramidă cu vârful în jos (12 / 193 / 10); (2) relaxarea RM032 pentru „architecture
  atomic" — respinsă de proprietar pe model. Ambele sunt în ADR-0038 ca istoric.
- A–E au fost rezolvate în aceeași zi (plugin `7.10.0`, engine `2026-09-14.3`) — fiecare
  era același tipar: două părți ale engine-ului răspundeau diferit la aceeași întrebare.
  A: un singur decodor (`read_source_text`/`read_source_lines`) pentru cele patru locuri
  care deschid surse, BOM UTF-16 decodat, restul raportat de noul **RM033**
  (`ARCH-UNREADABLE-070`). B: `init` scrie tagul în sursa pe care o draftează
  (`REQ-INITTAG-1008`). C: o singură definiție `tags.tagged_files` pentru „tagat”
  (`REQ-PLANTAGGED-1005`). D: `--plan` poartă `level`, `arch_id` și `pyramid`
  (`REQ-PLANLEVEL-1006`). E: `orphans.untaggable_by_design` — un singur predicat pentru
  ambele rapoarte (`REQ-UNTAGGEDSET-1007`). 25 de teste noi, gate 0 erori.
- Propunerea de la A a fost corectată pe drum: „orice NUL ⇒ refuză fișierul” șterge 4 taguri
  reale din `app/src/lib/search.js` al acestui repo (UTF-8 valid cu două sentinele NUL
  într-un literal). Testul livrat e densitatea NUL-urilor, nu prezența lor.
- Rămâne deschisă doar legarea per-caz a testelor (`--link-cases`, `verifies:` din
  `tested-by @unit`) — ca îmbunătățire a dovezii, nu ca precondiție a rungului.
