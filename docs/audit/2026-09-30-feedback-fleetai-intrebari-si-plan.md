# Feedback din teren: FleetAI — întrebările deschise și planul pe jaloane

- **Sursa:** repo-ul FleetAI (`comilga-it/fleetai-prod`), consumator real, motor vendorat
  `2026-09-29.1` (v8.9.3), 306 cerințe, 1367 de membri. Folosit zilnic pe 30.09.2026, pentru PR-urile
  #125, #126 și #127 și pentru reorganizarea planului pe jaloane.
- **Metoda:** fiecare punct are dovada lui: fișier:linie din `plugin/scripts/reqmap_engine/` (aceeași
  versiune ca în FleetAI), comanda rulată sau PR-ul în care s-a văzut. Căile sunt relative la
  `plugin/scripts/reqmap_engine/`.
- **Cererea proprietarului:** întrebările deschise ale unei cerințe să arate ca o decizie de luat,
  cu variante și cu ce se întâmplă dacă nu se decide. Punctul 1 e cererea; restul sunt probleme
  întâlnite pe drum.

## Ce a mers bine

- Nota proprie a barei din plan (v8.9.3) a fost folosită imediat. În FleetAI, fiecare jalon are acum
  o bară, iar la clic chenarul arată lista bugurilor lui, pe module. Verificat în `_map.html`, local.
- `gate` a rămas verde și stabil pe toate cele trei PR-uri. Secțiunea „Verify intent” nu intră în
  `binding_hash` (`sections.py:201`), deci s-au putut rescrie întrebări pe cerințe `confirmed` fără
  retrogradare la draft. Exact comportamentul dorit.

## 1. Întrebările din „Verify intent” nu au formă de decizie (cererea proprietarului)

**Ce vrea proprietarul.** O întrebare deschisă trebuie să se poată citi fără cod și să se poată
răspunde cu o literă. Exemplul lui, pe care l-a și răspuns imediat (1a 2b 3c 4a 5a):

```
- **Doi mecanici lucrează pe același WO. Telefonul unuia se oprește. Ce vrei să se întâmple?**
  a) Cronometrul lui se oprește după 5 minute, chiar dacă telefonul colegului merge.
  b) Rămâne cum e: cât timp un telefon trimite semnal pe WO, ambele cronometre merg.
  *Dacă nu hotărăști:* rămâne b), la fel ca înainte.
  *Context:* `WorkOrder.gps_ultima_verificare_ts` … (fișier:linie, textul tehnic)
```

Cinci întrebări puse așa au primit răspuns în câteva minute. Aceleași întrebări, în forma tehnică
(„heartbeat-ul GPS e pe WO, nu pe mecanic”), stăteau deschise.

**Ce face motorul azi**, măsurat cu `_verify_bullets` (`text.py:189`) pe un corp de test:

| Cum sunt scrise variantele | Ce numără motorul | Ce afișează |
|---|---|---|
| rânduri indentate, fără liniuță (`  a) …`) | 1 întrebare (corect) | un singur șir lipit: `**…?** a) … b) … *Dacă nu hotărăști:* …` |
| sub-bullet-uri (`  - a) …`) | 3 întrebări (greșit) | fiecare variantă apare ca întrebare separată |

- `_render_findings_raw` (`findings.py:30`) scrie fiecare element ca `- {it}`, pe un singur rând.
  Variantele se pierd vizual în `_findings.md` și în vizualizator.
- Șabloanele care creează secțiunea nu sugerează forma: `draft.py:172`, `draft.py:218`, `author.py:80`
  și `decompose.py:29` scriu doar titlul „Verify intent (open questions for the human)”.

**Propunere.** O formă recunoscută de „întrebare-decizie”:
- rândul întrebării, bold;
- rânduri indentate `a)`, `b)`, `c)` pentru variante;
- `*Dacă nu hotărăști:*` (implicitul, adică ce face codul azi);
- `*Context:*` (opțional), pentru textul tehnic.

Motorul ar trebui să:
1. numere întrebarea o singură dată, chiar dacă variantele sunt scrise ca sub-bullet-uri `- a)`;
2. păstreze structura în `_map.json` (`question`, `options[]`, `default`, `context`), iar
   `_findings.md` și vizualizatorul să arate variantele ca listă;
3. aibă șabloanele din `draft` / `author` / `decompose` care scriu un exemplu comentat în această formă;
4. aibă în `gate` o regulă de lizibilitate, doar avertisment: o întrebare deschisă fără variante sau
   fără `Dacă nu hotărăști`.

**Gata =**
- un test în care corpul de mai sus (cu variante ca sub-bullet-uri) dă o singură întrebare, cu 2
  variante și un implicit;
- `_findings.md` le randează pe rânduri separate;
- o cerință nouă făcută cu `draft` are exemplul în secțiune.

## 2. O întrebare cu răspuns nu are unde să se ducă

- **Dovada:**
  - `_findings.md` din FleetAI spune „84 triaged (generated 2026-09-11)” față de 99 de întrebări
    brute; triajul e manual și îmbătrânește.
  - Mai multe elemente triate au deja „REZOLVAT … confirmat prin citire directă” în câmpul `fix`,
    dar rămân în „Confirmed bugs” ca deschise, pentru că întrebarea stă tot în „Verify intent”.
  - Unde s-a răspuns, FleetAI a inventat subsecțiuni ad-hoc: `### Întrebări închise (răspunsuri
    primite)` în `REQ-DOC-EXPORT-061.md:63`, `REQ-DOC-REQUIRED-FIELDS-123.md:50`,
    `REQ-DOC-SIGNSTATE-LIVE-266.md:65`, `REQ-DOC-TEMPLATE-AI-122.md:429`, plus o variantă a patra în
    `REQ-DOC-RBAC-OPERATOR-136.md:49`.
- **Propunere:**
  - un rând `*Răspuns (AAAA-LL-ZZ):* b) …` sub întrebare o scoate din numărătoarea deschisă;
  - `sync` o mută într-o subsecțiune standard „Întrebări închise”, cu data și litera aleasă;
  - triajul se invalidează per element (hash-ul textului întrebării), nu global.
- **Gata =** o întrebare cu `*Răspuns …*` nu mai apare în `_findings.md` și nici în contorul
  `unverified-intent` (`model.py:55`), iar după `sync` stă sub „Întrebări închise”.

## 3. Legătura bară ↔ poziție din ROADMAP e doar egalitatea titlului

- **Dovada:** `bar_items` (`plandrift.py:290`) și `items_for_bars` (`plandrift.py:415`) potrivesc
  bara cu poziția din ROADMAP după `name.strip().lower() == title`. În FleetAI, titlul barei și
  numele poziției trebuie ținute identice de mână. Un număr în titlu („v1.14 · Buguri P0 (70)”) ar
  rupe legătura la fiecare regenerare, deci numerele au fost scoase din titluri.
- **Propunere:** o cheie explicită, `"roadmap": "<id>"` pe bară, sau un `id:` pe poziție. Titlul
  rămâne liber pentru desen.
- **Gata =** redenumirea barei nu schimbă ce poziție bifează `sync --release`.

## 4. Lista de sub bară se scrie de mână, deși motorul are deja datele

- **Dovada:**
  - Chenarul barei arată comentariul de sub poziția din ROADMAP. În FleetAI, lista bugurilor unui
    jalon (din `TODO.md`, `## vX.YY` → `### modul` → `- [ ]`) a fost generată cu un script separat,
    scris pe 30.09.2026, și trebuie regenerată la fiecare mutare între jaloane. S-a întâmplat de două
    ori în aceeași zi (#126, apoi #127).
  - Motorul citește deja jaloanele din `TODO.md` (`_parse_todos_from_text`).
- **Propunere:** `sync` completează singur comentariul poziției cu lista deschisă a jalonului, pe
  subsecțiuni, cu cele mai grave primele după prefixul `Pn`, și cu un antet „instantaneu la data X”.
  Opțiunea se activează printr-un marcaj în poziție (de ex. `| list: todo`).
- **Gata =** o poziție mutată între jaloane în `TODO.md` apare în chenarul celuilalt jalon după un
  simplu `sync`.

## 5. `sync --release` scrie titlurile barelor în CHANGELOG

- **Dovada:** `_changelog_entry` (`release.py:78`) listează `bar.title` pentru barele jalonului.
  Titlurile sunt scurte pentru că lățimea barei e durata ei (regulă scrisă chiar în
  `_planning.json` din FleetAI). În CHANGELOG ar ajunge „v1.13 · Release”.
- **Propunere:** CHANGELOG-ul ia `label` / `note` al jalonului, sau un câmp `changelog` pe bară, cu
  titlul ca rezervă.
- **Gata =** o bară cu titlu scurt și `changelog` lung dă rândul lung în CHANGELOG.

## 6. Harta comisă intră în conflict la fiecare PR paralel

- **Dovada:** #125 și #126 din FleetAI nu atingeau aceleași fișiere sursă. După merge-ul lui #126,
  #125 a devenit `CONFLICTING` doar pe `requirements/_map.html`, `_map.json` și `_map.md`. Rezolvarea
  a fost un rebase cu „ia varianta commit-ului” la fiecare pas, apoi `sync`, adică 10 commit-uri
  trecute prin buclă.
- **Propunere** (oricare):
  - un driver de merge documentat în `.gitattributes`, care regenerează harta;
  - `sync --resolve-map`, care rezolvă conflictele doar pe `_map.*`;
  - `_map.html` scos din git, cu verificarea prospețimii rămasă pe `_map.json`.
- **Gata =** două PR-uri care ating cerințe diferite se pot pune în main în orice ordine, fără
  conflict manual.

## 7. Fișierele neurmărite intră în scanare

- **Dovada:** `scan.py:145` parcurge arborele cu `os.walk`. În FleetAI, documentele locale neurmărite
  din `docs/` fac hook-ul de commit să spună „map is stale”. Soluția folosită de fiecare dată e
  `git stash push -u -- docs/`, apoi `sync`, commit și `stash pop`, scrisă ca regulă în memoria de
  lucru a proiectului.
- **Propunere:** într-un repo git, scanarea se face pe `git ls-files` plus fișierele indexate.
  `os.walk` rămâne doar în afara git.
- **Gata =** un fișier neurmărit care conține `implements:` nu schimbă `_map.json`.

## 8. Zgomot care se repetă la fiecare `sync`

- „4 TODO.md heading(s) are not milestones …” (`audittail.py:213`) apare la fiecare rulare, pentru
  secțiuni care intenționat nu sunt jaloane: „Cum se împarte munca”, „Acoperire cu teste”, „Triaj de
  intenție”, un plan de aplicație.
- **Propunere:** un marcaj care scoate un titlu din regulă (de ex. `## Acoperire cu teste <!-- reqmap: not-milestone -->`),
  sau regula aplicată doar titlurilor care încep cu `v`.

## 9. Risc, nu incident: o bară cu `req:` spre o cerință-umbrelă

- `bar_done` (`plandrift.py:330`) consideră bara terminată când cerința ei e `confirmed`, dacă nu era
  deja confirmată înainte de începutul barei (`done_before`).
- O bară de tip „lista bugurilor jalonului”, legată de o cerință-umbrelă confirmată după începutul
  barei, s-ar arăta terminată cu lista încă deschisă.
- În FleetAI barele de jalon au rămas deliberat fără `req:`.
- **Propunere:** când bara are o listă (punctul 4), „terminat” se decide după listă, nu după cerință.
