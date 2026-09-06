# Audit complet — Requirement-manager, 2026-09-06

Acoperire: `plugin/scripts/reqmap.py` (9.699 linii la început), `test_reqmap.py`,
`scripts/*.py`, `check/`, hook-urile, `sync_reqmap.sh`, `.github/workflows/ci.yml`,
builder-ul Excalidraw și viewer-ul din `app/src/lib`. Fiecare constatare de mai jos a fost
confirmată citind codul; cele marcate **[reprodus]** au fost și rulate. Liniile citate sunt
cele din `main` la momentul auditului (commit `722ad31`), înainte de modificările din PR.

Baseline înainte de orice modificare: 970 teste verzi, `gate --code ..` 0 erori, harta proaspătă.

**Ce s-a aplicat în acest PR** este marcat cu ✅. Restul e propunere, cu justificare.

---

## 1. Bug-uri (prioritizate)

### Critic

| # | Unde | Ce | Stare |
|---|---|---|---|
| C1 | `_design_py_nesting` :8842, `ast.dump` :9010, `_design_python` :8991 | Review-ul de design ("advisory, niciodată gate-ul") recursa în fiecare nod de expresie. Un fișier al unui consumator cu un lanț `1+1+…` de 1.000 de termeni sau un `if/elif` cu 1.000 de ramuri se parsează, dar aruncă `RecursionError`, pe care nimic nu îl prinde. Ajunge în verdictul de commit: `gate` → `cmd_map(check)` → `_assemble_map_data` → `_design_summary`. **[reprodus]**: `gate`, `sync`, `gate --risk`, `gate --audit` ies toate cu 1 și traceback. | ✅ walker iterativ + `RecursionError` tratat ca fișier nemăsurabil |

### Mediu

| # | Unde | Ce | Stare |
|---|---|---|---|
| M1 | `_wipe` :6273, `_strip_line_tag` :6239 | `init --wipe` tăia orice linie cu un hit `TAG_RE`, fără nicio mascare pe care scanner-ul o aplică (string-uri Python, fence-uri Markdown). Pe acest repo: `test_reqmap.py:282` devine `"t_probe.py": "` → `SyntaxError`; 40+ literale tăiate; exemplele din `CLAUDE.md`, `README.md`, `CONTRIBUTING.md` golite. **[reprodus]** | ✅ șterge doar liniile pe care `_scan_file_tags` le citește ca tag; `.reqmapignore` e semănat înainte de wipe; CRLF păstrat; markere `/* -- ;` cunoscute |
| M2 | `cmd_check` :3065, `_check_integration_fresh` :774 | `plugin_root = dirname(dirname(__file__))` este rădăcina repo-ului consumatorului când motorul e vendorizat în `scripts/`. Un consumator cu propriul `tool_definition.json` primește `ERROR RM028` și exit 1. **[reprodus]** | ✅ verificarea rulează doar când `.claude-plugin/plugin.json` stă lângă motor |
| M3 | dispatch :9657, `cmd_lint` :5177 | `clarify <ID> --decompose` ignoră ID-ul și scaffoldează pentru tot corpusul. **[reprodus]** | ✅ `cmd_lint(only=…)` |
| M4 | `_next_free_number` :5098 | Citește numele fișierelor, dar `ARCH-MODULEFILE-056` pune multe id-uri într-un fișier: întoarce 110 pe un corpus cu id maxim 982. Un `--decompose` distanță de un id duplicat. **[reprodus]** | ✅ citește id-urile încărcate + directorul |
| M5 | `_strip_member_tags` :8484 | Regex-ul cere `#` literal (deci `// implements:` din JS/Go/C rămâne → RM001 la următorul commit) și nu are margine dreaptă (retragerea lui `X-001` strică tag-ul lui `X-0011`). **[reprodus]** | ✅ aceeași gardă stânga ca `TAG_RE`, margine dreaptă |
| M6 | `_link_sync_errors` :2928 | Apelează regulile direct, ocolind filtrul `gate_exempt` din `run_gate_rules`. `health` (și blocul `health` din `_map.json`) raportează o eroare pe care `gate` o trece. **[reprodus]** | ✅ |
| M7 | `load_requirements` :1024 | Fără `try`: un singur octet Latin-1 într-un fișier de cerință omoară tot corpusul cu `UnicodeDecodeError`, contrar docstring-ului. **[reprodus]** | ✅ avertisment pe stderr + skip |
| M8 | `COMMANDS["sync"]` :527, :551 | `--apply` declarat de două ori: apare de două ori în `SKILL.universal.md`/`SKILL.md`, iar schema OpenAI păstrează doar al doilea help. **[reprodus]** | ✅ o intrare, artefactele regenerate |
| M9 | `_extract_coverage` :1292 vs `_scan_file_tags` :1185 | `verifies:`/`tested-by @level` dintr-un fence Markdown (un README care documentează sintaxa) contează ca acoperire reală și tace RM013. **[reprodus]** | propunere: un singur generator `_visible_lines(ext, lines)` consumat de ambele (rezolvă și I1) |
| M10 | `split_requirement_blocks` :993 | Un exemplu de frontmatter într-un bloc de cod dintr-o cerință produce o cerință fantomă (`AREA-NAME-NNN`). **[reprodus]** | propunere: split conștient de fence-uri |
| M11 | `_bullets` :6631, `_section*`, `_context_group` | Un comentariu `<!-- … -->` pe mai multe linii: doar prima linie e sărită, restul se pliază în clauza precedentă. Trei definiții diferite ale unui "bullet" (`-` vs `- `). Linter-ul (`_contract_clauses`) le tratează corect, harta/`show`/`dupes` nu. **[reprodus]** | ✅ în `_bullets` (comentariu ca unitate, bullet = `- `, `---` separator) |
| M12 | `_mermaid_hierarchy` :6846 | Desenează o muchie către un părinte fără `level:` → Mermaid inventează un nod gol. **[reprodus]** | ✅ |
| M13 | `_mark_todo_done` :3297 vs `_parse_todos_from_text` :4238 | Parser-ul ignoră itemii de deasupra primului `## vX.Y`; `--mark-done` bifează prima linie potrivită, adică pe cea greșită. **[reprodus]** | propunere: urmărește milestone-ul ca parser-ul |
| M14 | `_lint_prose` :4659, `_contract_clauses` :4707, `_text_matches` :5633 | Forma atomică e invizibilă pentru 5 verificări lint (`vague-term`, `stacked-conditions`, …) și pentru `search`. **[reprodus]** pe cele 8 `SYS-*`. | propunere: shim `_atomic_spans` la capul celor două helpere; `_text_matches` peste `_bullets`+`_acc_blocks` |
| M15 | `_health_record` :6058 | Un `need` confirmat fără `satisfies` intră în `orphans` (scor 0), dar nicio regulă din gate nu îl raportează. **[reprodus]** | propunere: regulă warn oglindă a RM031 sau scoate testul din `covered` |
| M16 | `cmd_coverage` :5912 vs `_scan_untagged` :1601 | Două numere "untagged" diferite: `gate --risk` spune 13, `--untagged` spune 55 (walk propriu, fără prune/noise). **[reprodus]** | propunere: `cmd_coverage` peste `_walk_code` + aceleași filtre (−10 linii) |
| M17 | `benchmark_scan.py:113` | Semnătura veche a lui `cmd_check` → `TypeError`. README încă îl documentează. **[reprodus]** | ✅ |
| M18 | `sync_reqmap.sh:55, :101` | (a) fără director de versiune în cache, `ls` sub `pipefail`+`-e` omoară scriptul fără output; (b) un `sync` eșuat într-un consumator oprește bucla DUPĂ ce motorul a fost copiat (motor nou, lock vechi). **[reprodus]** | ✅ |
| M19 | `ci.yml:60` vs `changelog_notes.py:23` | Gate-ul acceptă `` `vX.Y.Z` `` oriunde în CHANGELOG, extractorul cere heading `## plugin`. O versiune menționată în proză ("amânat la `v6.0.0`") trece CI și moare în job-ul `release`. | ✅ același reader |
| M20 | `SKILL.md:413-418`, `CONTRIBUTING.md:44,46` | Hook-ul dat consumatorilor rulează `gate` de trei ori; CONTRIBUTING numește două verbe retrase pe care `check_retired_verbs.py` nu le scana. | ✅ + `INSTRUCTION_FILES` extins |

### Minor

- `load_clarifylock` :2083 — `_schema: "1"` → `TypeError` în `sync` ✅. `load_ignore` :1101 prinde doar `OSError` ✅. RM016 tace pe un lock `[]`/`null` ✅.
- `_py_def_spans` :2166 — tag pe linia decoratorului → cheie pe tot fișierul (`@gate_rule(...)  # implements:` la :2776 e exact cazul). Fix: `lo = min([n.lineno] + [d.lineno for d in n.decorator_list])`.
- `--since`: `_rule_drift` :2799 și `_rule_need_not_validated` :2629 citesc `ctx.members` (filtrat) unde docstring-ul cere `full_members`.
- `_acc_blocks` :1752 — ramura atomică lasă prefixul `Scenario:` și comentariul HTML în text, `manual` fără garda `|`.
- Un `# verifies:` către un id/caz inexistent nu e raportat niciodată (RM013 nu validează etichete).
- `_ac_name_re` :7842 — potrivea doar `ac`, deci `sync --suggest-verifies` nu propunea nimic pentru `test_case3_…` ✅.
- `_inject_region` :7192 — `<body class="…">` nerecunoscut, blocul ajunge după `</html>` ✅.
- `cmd_site` — `--regions/--diagram/--detect` parsate și ignorate (dispatch le hard-codează); `SITE_TEMPLATE` :7453 are un marker `COMMANDS` care nu se potrivește cu `_region_markers` și listează "18 comenzi" din care 13 nu mai există. Flag-urile moarte ✅ șterse; template-ul rămâne de curățat.
- `_write_frontmatter_status` :3358 — split-ul nu e lossless (preambul doar-spații pierdut, fence `---   ` normalizat).
- `_write_sys_placeholder` :3460 — nu verifică `layer: need` existent; `_write_arch_drafts` :3520 — root draft intitulat `# .`.
- `cmd_new`/`cmd_promote_todo` — fără validare de id: `new "not a valid id"` creează un fișier pe care niciun tag nu îl poate lega vreodată.
- Template-ul lui `new` — `- Observed: <…>` e numărat ca finding deschis de `collect_findings` (nu și de `_risk_signals`/`_health_record`).
- `_roadmap_signals` :4204 întoarce `None` pe TODO.md necitibil unde celelalte două citiri cad pe părinte.
- `_audit_section` :5701 — o excepție în secțiunea Gate dă rc 0, verdict "clean"; modul `--json` lasă excepția să iasă.
- `_audit_summary` :5719 număra erorile lint fără promovarea `--strict` pe care `gate` o aplică ✅ (`LINT_STRICT_PROMOTE` comun).
- `sync --retire --apply --json` :8432 scrie proză înainte de JSON.
- `_design_standards` :8816 numără o linie în plus; `function(` anonim devine funcție numită `function` :9036; `apply_config` :9351 trunchiază `7.9` → `7` fără mesaj; "cohesion not measured for N classes" descrie o metrică ce nu se mai calculează.
- `check_versions.py:143` acceptă `20260906` pe Python ≥3.11 ✅; `check_engine_bump.py:60` acceptă un bump înapoi ✅; `engine_staleness.py:100` scrie `::warning` în modul `error` ✅; `ci.yml:356` mesajul de eroare e inaccesibil sub `pipefail` ✅.
- `excalidraw_builder.py:778` — `align`/`distribute` lasă în urmă etichetele poligoanelor ISO și barele `predefined_process`; `:1591` — JSON neescapat în `<script>` (`</script>` într-o etichetă rupe pagina); `:1825` — `_selftest` nu curăță tmp.
- `test_cross_tool.py:130` trece (SKIP, rc 0) când motorul lipsește.

---

## 2. Eficientizare

Măsurat pe acest repo (238 cerințe, 1.129 membri). `gate --code ..`: **2,48 s → 1,73 s** după PR (−30%).

### E1 ✅ Harta era asamblată de două ori per `gate`
RM027 (`_rule_map_stale` :2896) și `cmd_map(check)` din `_dispatch_gate` :9543 construiau fiecare documentul complet — inclusiv `_design_summary` (0,41 s), `_health_record`, `_parse_todos`, git.
```python
# înainte (două locuri)
_assemble_map_data(ctx.reqs, ctx.full_members, ctx.reqs_dir, ctx.code_root, ctx.ac_cover)
# după: cache pe Workspace, cheie (identitatea lui members, root)
ctx.ws.map_data(ctx.code_root, ctx.full_members)      # RM027
data = ws.map_data(root)                              # cmd_map
```

### E2 ✅ `_test_link_problem` deschidea `test_reqmap.py` de 206 ori per gate
```python
problems = {}
for fp in sorted({t[1] for t in tests}):
    if fp not in problems:
        problems[fp] = _test_link_problem(os.path.join(ctx.code_root, fp))
```

### E3 ✅ `_domain_heads(reqs)` recalculat per cerință în `_clarify_questions` :8137
46 recalculări, 0,41 s din 0,46 s ai pasului, pătratic în corpus. Se calculează o dată în `blocking_question_rules` și `cmd_clarify` și se dă mai departe (`domain=`).

### E4 Fiecare linie `.py` e mascată de două ori per scan (82% din `scan_all`)
`scan_all` :1358 apelează `_extract_coverage` și apoi `_scan_file_tags` pe aceleași linii; fiecare rulează propriul automat `in_triple` + `_strip_py_strings`. 43.444 apeluri = 2 × liniile din `reqmap.py`+`test_reqmap.py`, 0,68 s din 0,83 s.
```python
# după: o singură mascare, un generator consumat de ambele (rezolvă și M9)
vis = list(_visible_lines(ext, lines))          # [(lineno, text_mascat)]
_extract_coverage(rel, vis, ac, lv)
tags = _tags_from_visible(vis)
```
Al doilea ordin: `_strip_py_strings` e o buclă per caracter; un tokenizer regex compilat (`"""|'''|"(?:\\.|[^"\\\n])*"|…`) cu `re.sub` ar fi de câteva ori mai rapid.

### E5 Cinci walk-uri ale arborelui per `gate`, ≥6 per `gate --audit`
`_walk_code` ×3 (`scan_all`, `_scan_untagged`, `_design_files`) + `untagged_doc_bundles` :1573 (parcurge TOT arborele ca să se uite doar în `docs/`) + `orphan_code_files` :1635. `_scan_untagged` :1611 **recitește și re-parsează fiecare fișier** deși `members` există deja:
```python
# după: diferență de mulțimi, zero deschideri de fișiere
tagged = {rel for hits in members.values() for _r, rel, _l in hits}
untagged = [rel for _fp, rel in _walk_code(code_root, reqs_dir)
            if rel not in tagged and classify_prose(rel) != "ignore" and not _noise(rel)]
```
Sau: `scan_all` înregistrează `rel`-urile parcurse (`Workspace.files`) și `untagged`/`orphan`/`design` le citesc de acolo.

### E6 Șase bucle `os.walk` copiate lângă `_walk_code`
:1573, :1635, :1662, :3536, :3830, :6274 (✅ aceasta din urmă) — trei dintre ele apelează `_prune_dirs(dirpath, dirs, reqs_dir)` **fără** `code_root, ignore`, deci `.worktrees/**` sunt coborâte și stat-uite. Înlocuire cu `for fp, rel in _walk_code(...)` + filtrul propriu de extensii (toate sunt submulțimi ale `CODE_EXTS`).

### E7 `compute_member_hashes` deschide `reqmap.py` de 94 de ori per apel
`_span_sha` :2174 deschide și normalizează tot fișierul per span. Citește o dată per `fp`, hash-uiește felii din memorie; `_file_sha` (mort în producție) și `_span_sha` devin un helper.

### E8 `cmd_similar` recalculează normele per pereche
28.203 perechi, 0,24 s din 0,26 s în `_cosine` :5480. Pre-normalizează o dată (`unit = {rid: {t: w/norm}}`), ~4× mai rapid; `placeholder` :5531 e o **listă** folosită cu `not in` într-o comprehension (O(n²)) → set. Pipeline-ul `docs → _tfidf` e copiat identic în `cmd_similar` :5532, `cmd_search` :5656, `_neighbours` :8211 → un `_corpus_vectors(reqs)`.

### E9 `_design_brace` e pătratic în mărimea fișierului
16k linii 1,65 s, 32k linii 6,5 s: `depth_at` :9113 și `masked.count("\n", 0, m.start())` :9131… rescanează prefixul per potrivire. Pre-calcul: `nl = [i for i,c in enumerate(masked) if c=="\n"]` + `bisect`, `depth = accumulate(...)`. `_design_summary` rulează tot pasul de două ori per `sync` (`cmd_map` + `_audit_summary`) și `cmd_design` parsează fiecare `.py` de două ori (:9252, :9254).

### E10 Corpul cerinței e re-split de ~22–30 de ori per cerință
`_atomic_spans` ×14, `_lint_prose` ×8, `_acc_blocks` ×4 per `lint_requirement`; în `_build_map_data` `_verify_bullets` de două ori (:4150, :4177), dict-ul de risc construit identic în trei locuri (:4174, :4487, :5321). `functools.lru_cache` pe `_atomic_spans(body)` (corpurile sunt string-uri imutabile) sau un record parsat o dată în `lint_requirement`.

### E11 Git pornit de 11 ori per `gate`
`untracked_members`, `tagged_unscanned_files`, `untracked_locks` (câte un `ls-files` fiecare + `rev-parse`), `_repo_name`, `_git_remote_web_url`, `_docs_publish_path`, `_site_default_target`. Un `ls-files -z` pe context + `lru_cache` pe `_git_root(root)`/`_git_origin_url(root)`. `.reqmapignore` e parsat de 10 ori per gate.

### E12 `cmd_init` scanează arborele de 3–5 ori
:6358, :6362 (`scan_members` ×2), apoi `GateContext` cade pe `scan_ac_verifies`+`scan_test_levels` pentru că `Workspace` e construit manual fără `ac_cover`, apoi :4406 încă o dată. `Workspace.load(...)` o dată.

### E13 `_verifies_proposals` :7893 recitește fișierul de test per (cerință, criteriu)
182 citiri a 5 fișiere distincte. `funcs.setdefault(fp, _test_functions(...))` în afara buclei `for ac in missing`.

---

## 3. Cod eliminabil

### 3a. Șters în acest PR ✅ (fără schimbare de comportament)
| Ce | Linii | De ce e sigur |
|---|---|---|
| `_RO_DIACRITICS`, `_RO_STOPWORDS`, `_EN_STOPWORDS` | 13 | zero referințe; rămășițe ale verbului `translate` șters pe 2026-09-05. Cititorul de traduceri rămâne — e viu (`_i18n/ro.json`, 206 intrări fresh) |
| `lock_blocked` (4 locuri) | 4 | mereu `False` |
| ramura duplicată `save_lock`/`save_memberlock` din `cmd_check` | 5 | identică în ambele ramuri ale `if` |
| `Requirement.has` | 2 | zero apelanți |
| `_clean_item` | 7 | alias pur pentru `_scalar_value` |
| atribuiri duplicate în `lint_requirement` | 3 | |
| `dep_count` din `_mermaid_risk` | 3 | construit, necitit |
| flag-uri argparse fără cititor: `--raw`, `--update-lock`, `--check`, `--regions`, `--diagram`, `--detect` | 14 | niciun `a.<nume>` nicăieri; testele care le foloseau prin subprocess trec deja prin `invalid choice` |
| epilog scris de mână (12 verbe pe care argparse le respinge) | 20 → 12 | generat din `COMMANDS` |

### 3b. Eliminabil fără schimbare de comportament (propus, ~400 linii în motor)
| Ce | Linii | Justificare |
|---|---|---|
| `_walk_code_lines` + corpurile `scan_ac_verifies`/`scan_test_levels` :1654–1722 | ~60 | copie a buclei `_walk_code` + a mascării din `_extract_coverage`; `scan_all` produce rezultat identic (testul de la 5727 o afirmă). Devin `return scan_all(...)[1]`/`[2]`. Comentariile :9510, :9643 ("cache is scan_members-only") sunt vechi |
| `_file_sha` :2139 | 13 | doar testul de CRLF îl referă; retargetat pe helper-ul comun cu `_span_sha` (E7) |
| `Workspace.levels()` | 6 | ramura `None` e moartă (`scan_all` întoarce mereu dict) |
| cele 6 bucle `os.walk` copiate (E6) | ~40 | |
| 7 automate de stare "walk lines, toggle fence, grab `## `" (`_section`, `_section_raw`, `_bullets`, `_context_group`, `_lint_prose`, `_contract_clauses`, `_acc_blocks`) | 50–70 | un generator `_section_lines(body, names)` cu shim-ul atomic într-un singur loc; M11/M14 se închid prin construcție. Numele rămân ca wrapper-e (testele le referă) |
| `_lint_terms` dublă buclă :4961–4988; `_lint_readability` două treceri :4823 | 16 | |
| `_title` :6487 vs `_req_title` :3961 | 5 | diferă doar prin `strip()` (inconsistență latentă între titlurile din `_map.json` și `show`) |
| comparația roadmap duplicată `_audit_summary` :5753 / `cmd_health` :6166 | 8 | |
| walk-ul privat din `cmd_coverage` :5911 | 10 | și rezolvă M16 |
| ramura `detect` + `_site_diagram_ok` + params :7689–7729 | ~25 | inaccesibile din CLI (flag-urile lor sunt șterse acum); doar testele le apelează |
| secțiunile COMMANDS/LAYERS + banner din `SITE_TEMPLATE` :7275–7522 | ~60 | niciodată regenerate (`SITE_REGIONS` = nav, stats), factual greșite, marker nepotrivit |
| `_DESIGN_ADVICE` + `_DESIGN_PILLAR_OF` → un dict | 8 | două dict-uri paralele pe aceleași 15 chei |
| bucla de citire duplicată `_design_summary` :9214 / `cmd_design` :9245 | 10 | |
| docstring-ul modulului :4–28 + comentariul :259 | 22 | listează un CLI care nu mai există; registrul e SSOT |
| gărzile `spec.get("internal")` :623,659,677,699; `_TYPE["float"]`; params nefolosiți `cmd_gen_integration` | 6 | nicio intrare nu setează `internal`, niciun param nu e `float` |
| `_bus_ids`, `_node_area`, pipeline TF-IDF ×3, dict de risc ×3, locale din `cmd_health` | ~30 | |

### 3c. Eliminabil doar cu editarea unei cerințe (spec o cere explicit)
| Ce | Linii | Blocaj |
|---|---|---|
| `_design_lcom` + `_design_py_fields` + `_design_cohesion_skipped*` + plumbing-ul "cohesion not measured" | ~85 (+test) | `ARCH-DESIGN-061` (REQ-DESIGN-979/980) spune explicit că rămân "pentru o variantă viitoare". LCOM nu mai e calculat nicăieri; caveat-ul descrie o metrică inexistentă. Recomand `sync --retire REQ-DESIGN-980` și scoaterea caveat-ului din 979 |
| capmap (`_load_capmap` + gruparea din `cmd_candidates`) | ~30 | nedocumentat în SKILL/README/CHANGELOG, dar `ARCH-CANDIDATES-009` CASE-6 îl cere |
| `CheckAliasDriftGuard` (test_reqmap 6268–6306) | ~40 (test) | apelează `check --update-lock`, verb respins; aserțiunile trec pentru că nimic nu rulează. `IntentVerbDispatch` acoperă deja respingerea |
| help-urile argparse generate din registru | ~80 | ar face imposibilă structural clasa de bug M8; cere un mic tabel per-flag pentru `nargs/const/type` |

### 3d. În afara motorului
| Ce | Linii | Justificare |
|---|---|---|
| `plugin/hooks/pre-commit` | 27 | nimic nu îl copiază sau referă (`init` nu îl seamănă, `sync_reqmap.sh` nu îl propagă, ambele SKILL scriu un heredoc inline). Fie SKILL.md îl indică (și consumatorii primesc varianta cu probe `python3`), fie se șterge împreună cu cele două propoziții din CLAUDE.md/SECURITY.md |
| `app/src/lib/data.js` | ~165 din 207 | copie manuală, deja veche, a 13 cerințe reale (`check --update-lock`, `promote`); :2–16 e un array JSON lipit din greșeală în comentariul de header. 2–3 rânduri sintetice per stare ajung pentru smoke |
| `ci.yml:48–55` | 8 | comentariu "amânat" despre un job `release` care există la :312 |
| `ci.yml:120–122` `fetch-depth: 0` pe matricea `tests` | — | motivat prin `test_cross_tool` "shell out to git": nu o face (0 apariții); 6 clone complete per run degeaba |
| `check_versions.py:109–111` | 3 | `_fix` întoarce mereu 0 |
| `test_reqmap.py`: 8 copii identice ale helper-ului `_check(self, files)` | ~250 | un helper la nivel de modul |

---

## 4. Rezumat: ce ar scădea dacă aplici tot

Motorul la începutul auditului: **9.699 linii**, din care 964 goale, 943 comentarii, 1.282 docstring, 395 template-uri string → **≈6.100 linii de cod efectiv**.

| Categorie | Linii | Fișiere |
|---|---|---|
| Șters în PR (3a) | ≈70 în motor (net +41 după fix-urile și comentariile adăugate) | — |
| Eliminabil fără schimbare de comportament (3b) | **≈400** | 0 (toate în `reqmap.py`) |
| Eliminabil cu editare de cerință (3c) | ≈235 (+120 în teste) | 0 |
| În afara motorului (3d) | ≈200 (+250 în teste) | 1 (`plugin/hooks/pre-commit`) |
| **Total cod** | **≈900 linii de cod + ≈370 în teste** | **1 fișier** |

**Despre ținta de ~50%.** Nu se atinge fără a scoate funcționalitate sau proză, și e corect să spun asta direct:
- 3b+3c+3d taie ≈15% din codul efectiv al motorului, zero funcționalitate pierdută.
- Restul până la 50% nu e cod mort: sunt (a) cele ≈3.200 de linii de comentarii și docstring-uri — o decizie de stil, nu o risipă; (b) feature-uri întregi care sunt corect implementate dar opționale: review-ul de design (≈635 linii, advisory; ≈400 sunt load-bearing), mașinăria de site (≈350, folosită de `init`/`sync`), `candidates`/capmap, cititorul de traduceri. Scoaterea lor e o decizie de produs (ADR nou), nu o curățenie.
- ADR-0014 fixează mărimea fișierului ca o chestiune închisă și dă praguri numerice de redeschidere; auditul nu le contrazice.

Recomandarea mea de ordine, după acest PR: E4+M9 (un generator de linii vizibile — cel mai mare câștig de viteză și un bug real), apoi 3b rândul "7 automate de stare" (închide M11/M14 prin construcție), apoi E5/E6 (un singur walk), apoi `_design_lcom` prin retragerea cerinței.
