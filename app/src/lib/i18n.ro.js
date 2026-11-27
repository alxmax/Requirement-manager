// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-943
// implements: REQ-VIEWER-964
/* English -> Romanian, UI chrome and the command summaries. Kept in its own
 * file, as the German table is, so each language is one place to read and
 * review. A key missing here falls back to English; a smoke check fails when
 * this table and the German one name different strings. */
export const RO = {  // implements: REQ-VIEWER-943
  // shell / top bar
  "local repo": "depozit local",
  "Search id, title, contract…": "Caută id, titlu, contract…",
  "no strong match": "nicio potrivire clară",
  "toggle theme": "schimbă tema",
  "switch language": "schimbă limba",
  // no map loaded
  "No requirement map to show": "Nu există o hartă de cerințe de afișat",
  "This viewer opened without a map. Run this in your repository, then open requirements/_map.html:":
    "Viewer-ul s-a deschis fără hartă. Rulează comanda în depozitul tău, apoi deschide requirements/_map.html:",
  // rail
  "Workspace": "Spațiu de lucru",
  "Registry": "Registru",
  "Signals": "Indicatori",
  "Health": "Sănătate",
  "Bugs": "Buguri",
  "critical": "foarte grav",
  "high": "grav",
  "medium": "mediu",
  "low": "mic",
  "minor": "minor",
  "Priorities": "Priorități",
  "estimated, not yet confirmed by a user": "estimată, neconfirmată încă de un utilizator",
  "What is broken": "Ce nu merge",
  "Module": "Modul",
  "Priority": "Prioritate",
  "Date": "Data",
  "Where (file:line)": "Unde (fișier:linie)",
  "Why it matters": "De ce contează",
  "Save bug": "Salvează bugul",
  "Cancel": "Renunță",
  "added, run sync": "adăugat, rulează sync",
  "Where": "Unde",
  "Source": "Sursa",
  "File": "Fișier",
  "Search bugs": "Caută în buguri",
  "Add bug": "Adaugă bug",
  "Export PDF": "Exportă PDF",
  "Expand all": "Deschide tot",
  "Collapse all": "Închide tot",
  "Open": "Deschise",
  "Fixed": "Rezolvate",
  "Found": "Găsit",
  "Version": "Versiune",
  "Commit": "Commit",
  "Week": "Săptămâna",
  "Still open": "Încă deschise",
  "Median days to fix": "Mediana zilelor până la rezolvare",
  "By priority": "Pe priorități",
  "Pick a week to see its bugs.": "Alege o săptămână ca să-i vezi bugurile.",
  // the fixed / still-open chart
  "Fixed and still open": "Rezolvate și încă deschise",
  "{fixed} fixed, {open} still open. Open peaked at {peak} on {date}.":
    "{fixed} rezolvate, {open} încă deschise. Maximul a fost {peak}, pe {date}.",
  "{fixed} fixed, {open} still open. Open peaked at {peak} on {date} and has come down since.":
    "{fixed} rezolvate, {open} încă deschise. Maximul a fost {peak}, pe {date}, și de atunci a scăzut.",
  "Show total": "Arată totalul",
  "Total found": "Total găsite",
  "{n} fixed": "{n} rezolvate",
  "{n} still open": "{n} încă deschise",
  "{n} total": "{n} în total",
  "Up to {date}": "Până la {date}",
  "Up to {date}: {fixed} fixed, {open} still open": "Până la {date}: {fixed} rezolvate, {open} încă deschise",
  "Bugs fixed and still open, week by week": "Buguri rezolvate și încă deschise, pe săptămâni",
  // the Report's charts and their filters
  "Open questions by priority": "Întrebări deschise, pe prioritate",
  "On confirmed requirements": "Pe cerințe confirmate",
  "On drafts": "Pe schițe",
  "Open questions by priority, on confirmed requirements and on drafts":
    "Întrebări deschise pe prioritate, pe cerințe confirmate și pe schițe",
  "{n} ({c} on confirmed)": "{n} ({c} pe confirmate)",
  "Bug priorities": "Priorități buguri",
  "Question priorities": "Priorități întrebări",
  "Previous page": "Pagina anterioară",
  "Next page": "Pagina următoare",
  "Page {n} of {m}": "Pagina {n} din {m}",
  "Fixed in the last 30 days": "Rezolvate în ultimele 30 de zile",
  "No bug has been closed yet.": "Niciun bug nu a fost închis încă.",
  "Known bugs": "Buguri cunoscute",
  "{n} bugs": "{n} buguri",
  "No bugs found.": "Niciun bug găsit.",
  "No known bugs yet.": "Niciun bug cunoscut încă.",
  "This browser cannot write to the repository. Run this command, then `sync`:":
    "Browserul acesta nu poate scrie în repo. Rulează comanda, apoi `sync`:",
  "Choose the requirements folder, the one holding _map.json.":
    "Alege folderul requirements, cel care conține _map.json.",
  "Design OOP": "Design OOP",
  "due {date}": "până la {date}",
  "Roadmap": "Planificare",
  "milestones": "repertori",
  "rows": "rânduri",
  "next {ms} · due {date}": "următor {ms} · până la {date}",
  "{n} planned": "{n} planificate",
  "View": "Vizualizare",
  "Plan": "Plan",
  "Versions": "Versiuni",
  "Horizons": "Orizonturi",
  "Shipped": "Livrat",
  "releases": "release-uri",
  "release": "release",
  "first commit": "primul commit",
  "last commit": "ultimul commit",
  "Nothing planned on this version yet.":
    "Nimic planificat încă pe versiunea asta.",
  "Open in TODO.md": "Deschise în TODO.md",
  "Now": "Acum",
  "Next": "Urmează",
  "Later": "Mai târziu",
  "being worked on": "în lucru",
  "queued, not started": "în coadă, neînceput",
  "parked behind a condition": "parcat în spatele unei condiții",
  "open": "deschise",
  "nothing here": "nimic aici",
  "unpark:": "repornit de:",
  "Add milestones with due dates or bars in _planning.json.":
    "Adaugă milestone-uri cu date sau bars în _planning.json.",
  "bars": "bare",
  "lanes": "benzi",
  "today": "azi",
  "Add `bars` with start/end dates to _planning.json for the timeline view.":
    "Adaugă `bars` cu date start/end în _planning.json pentru "
      + "vizualizarea timeline.",
  "{a}/{b} green": "{a}/{b} verzi",
  "{n} exempt": "{n} cu scutire",
  "Exempt": "Cu scutire",
  "not confirmed": "neconfirmată",
  "not implemented": "neimplementată",
  "not tested": "netestată",
  "open question": "întrebare deschisă",
  "drift": "drift",
  ["Requirements not green on every axis — confirmed, implemented, "
    + "tested, no open question, no drift."]:
    "Cerințe care nu sunt verzi pe toate axele — confirmată, "
    + "implementată, testată, fără întrebări deschise, fără drift.",
  "{a}/{b} files clean": "{a}/{b} fișiere curate",
  ["Requirements green on every axis — confirmed, implemented, tested, no "
    + "open question, no drift"]:
    "Cerințe verzi pe fiecare axă — confirmate, implementate, testate, "
      + "fără întrebări deschise, fără drift",
  ["Source files with no OOP or house-standard candidate — advisory, "
    + "never part of the gate"]:
    "Fișiere sursă fără semnalări OOP sau de standarde — consultativ, "
      + "niciodată parte din gate",
  "Map": "Hartă",
  "Problems": "Probleme",
  "Spec": "Specificații",
  "Commands": "Comenzi",
  "Author": "Autorare",
  "Build": "Construire",
  "Read": "Citire",
  "writing and evolving a requirement": "scrierea și evoluția unei cerințe",
  "turning it into code, and proving it": "transformarea ei în cod, și dovada",
  "asking the corpus questions": "Întrebări puse corpusului",
  "Every verb the engine exposes, generated from its own command registry.":
    "Fiecare verb pe care motorul îl expune, generat din propriul lui "
      + "registru de comenzi.",
  "No command list in this map.": "Harta nu conține lista de comenzi.",
  ["Regenerate it with a current engine — `reqmap.py sync` writes the "
    + "command reference into _map.json."]:
    "Regenereaz-o cu un motor actual — `reqmap.py sync` scrie referința "
      + "de comenzi în _map.json.",
  "Explorer": "Explorator",
  "Findings": "Constatări",
  "{n} members bound": "{n} membri legați",
  // module explorer
  "Level": "Nivel",
  "Status": "Stare",
  "has open question": "are întrebare deschisă",
  "expand all": "extinde tot",
  "collapse all": "restrânge tot",
  "{shown} of {total} shown": "{shown} din {total} afișate",
  "· no hierarchy in this map — flat list":
    "· fără ierarhie în această hartă — listă plată",
  "No requirement matches these filters.":
    "Nicio cerință nu corespunde acestor filtre.",
  "No requirement selected.": "Nicio cerință selectată.",
  "Links — traceability": "Legături — trasabilitate",
  "Needed by": "Folosit de",
  "Needs": "Are nevoie de",
  "satisfies (up)": "satisface (în sus)",
  "satisfied by (down)": "satisfăcut de (în jos)",
  "depends on (out)": "depinde de (ieșire)",
  "used by (in)": "folosit de (intrare)",
  "— top of the trace": "— vârful trasabilității",
  "— nothing decomposes this": "— nimic nu descompune asta",
  "— no outgoing dependency": "— nicio dependență ieșită",
  "— nothing depends on this": "— nimic nu depinde de asta",
  "Open questions — verify intent": "Întrebări deschise — verifică intenția",
  "system + architecture · {n} code-level hidden":
    "sistem + arhitectură · {n} de nivel cod ascunse",
  // findings
  "open verify-intent questions": "întrebări de verificare deschise",
  "No open questions.": "Nicio întrebare deschisă.",
  ["Every requirement's Verify-intent section is either empty or still "
    + "carries the authored placeholder, which the engine does not count "
    + "as a finding either."]:
    "Secțiunea Verify-intent a fiecărei cerințe este fie goală, fie "
      + "conține încă textul-șablon autorat, pe care nici motorul nu îl "
      + "numără drept constatare.",
  "{n} open question(s) across {m} requirement(s)":
    "{n} întrebare/întrebări deschise în {m} cerință/cerințe",
  ["Answer it: fold the answer into the Description and delete the bullet, "
    + "or keep it under the question as `*Answer (YYYY-MM-DD):* …`."]:
    "Răspunde: integrează răspunsul în Descriere și șterge punctul, "
    + "sau păstrează-l sub întrebare ca `*Answer (YYYY-MM-DD):* …`.",
  // map tabs
  "System Map": "Harta sistemului",
  "Req→Code": "Cerință→Cod",
  "Dependencies": "Dependențe",
  "Risk": "Risc",
  // detail panel + spec sections
  "Why — Intent": "De ce — Intenție",
  "Description": "Descriere",
  "Cases": "Cazuri",
  "Where — Members in code": "Unde — Membri în cod",
  "Depends on": "Depinde de",
  "depends on": "depinde de",
  "level": "nivel",
  "milestone": "reper",
  "Used by": "Folosit de",
  "Risk — recommended action": "Risc — acțiune recomandată",
  "Open bugs": "Buguri deschise",
  "Open full spec": "Deschide specificația completă",
  "center & highlight in the map": "centrează și evidențiază în hartă",
  "close": "închide",
  "created": "creat",
  "updated": "actualizat",
  "normative": "normativ",
  "= tests": "= teste",
  "(satisfied-by other requirements — no direct code)":
    "(satisfăcut de alte cerințe — fără cod direct)",
  "(no members found — orphan)": "(niciun membru găsit — orfan)",
  "(not linked to code yet — not enforced at this status)":
    "(încă nelegat de cod — neimpus la această stare)",
  // problems
  "All": "Toate",
  "Errors": "Erori",
  "Warnings": "Avertismente",
  "Questions": "Întrebări",
  "ASKED": "NOTAT",
  "No open questions here.": "Nicio întrebare deschisă aici.",
  "Open requirement": "Deschide cerința",
  "Close": "Închide",
  "High": "Ridicată",
  "Medium": "Medie",
  "Low": "Scăzută",
  "no high priority question": "nicio întrebare cu prioritate ridicată",
  "{n} high priority open": "{n} cu prioritate ridicată deschise",
  // report  (REQ-VIEWER-1139)
  "Report": "Raport",
  "Summary": "Rezumat",
  "How it was checked": "Cum s-a verificat",
  "Results in numbers": "Rezultate în cifre",
  "Problem types": "Tipuri de probleme",
  "Top 10 questions": "Top 10 întrebări",
  "Recommendations": "Recomandări",
  "not measured": "nemăsurat",
  "open bugs": "buguri deschise",
  "fixed bugs": "buguri rezolvate",
  "High questions": "întrebări cu prioritate ridicată",
  "Medium questions": "întrebări cu prioritate medie",
  "Low questions": "întrebări cu prioritate scăzută",
  "requirements with no code": "cerințe fără cod",
  "requirements with no test": "cerințe fără test",
  "unproven cases": "cazuri nedovedite",
  "confirmed, no implements": "confirmate, fără implements",
  "draft, no implements": "draft, fără implements",
  "code, no tested-by": "cu cod, fără tested-by",
  "cases with no verifies": "cazuri fără verifies",
  "dangling tags": "taguri orfane",
  "Dangling tags (RM001)": "Taguri orfane (RM001)",
  "Confirmed, no implements": "Confirmate, fără implements",
  "Draft, no implements": "Draft, fără implements",
  "Drift": "Drift",
  "Requirements with a High question": "Cerințe cu o întrebare ridicată",
  "Code, no tested-by": "Cu cod, fără tested-by",
  "Cases with no verifies": "Cazuri fără verifies",
  "Tests that cannot fail": "Teste care nu pot pica",
  "Health {s}/100: {a} of {b} requirements green.":
    "Sănătate {s}/100: {a} din {b} cerințe sunt verzi.",
  "{a} of {b} live requirements are confirmed.":
    "{a} din {b} cerințe active sunt confirmate.",
  "Open: bugs {bugs}, High questions {high}, missing trace tags {tags}.":
    "Deschise: buguri {bugs}, întrebări cu prioritate ridicată {high}, taguri de trasabilitate lipsă {tags}.",
  "The largest open item: {x}.": "Cel mai mare punct deschis: {x}.",
  "Nothing is open.": "Nu e nimic deschis.",
  "Map written {at} on branch {b}, engine {e}.":
    "Harta scrisă {at} pe branch-ul {b}, engine {e}.",
  "{r} requirements and {f} tagged files read.":
    "{r} cerințe și {f} fișiere taggate citite.",
  "Gate link sync: every tag names a requirement (RM001).":
    "Gate link sync: fiecare tag numește o cerință (RM001).",
  "Drift lock: a confirmed contract changed since the lock.":
    "Drift lock: un contract confirmat s-a schimbat de la lock.",
  "Test links: `implements:`, `tested-by:` and `# verifies:` tags.":
    "Legături de test: tagurile `implements:`, `tested-by:` și `# verifies:`.",
  "`clarify`: questions read from each requirement's own text.":
    "`clarify`: întrebări citite din textul fiecărei cerințe.",
  "Bug files: the open and fixed bugs the repository keeps.":
    "Fișierele de buguri: bugurile deschise și rezolvate din repository.",
  "Nothing is open: no recommendation.": "Nu e nimic deschis: nicio recomandare.",
  // report, audit depth  (REQ-VIEWER-1145)
  "{n} requirements": "{n} cerințe",
  "Export Markdown": "Exportă Markdown",
  "Deliverables": "Livrabile",
  "Engine": "Engine",
  "Branch": "Branch",
  "Audit": "Audit",
  "Main conclusions:": "Concluzii principale:",
  "of planned requirements read by the audit ({a} of {b})":
    "din cerințele planificate citite de audit ({a} din {b})",
  "questions for requirement owners": "întrebări pentru proprietarii cerințelor",
  "requirements with code, no tested-by": "cerințe cu cod, fără tested-by",
  "{a} of {b} planned requirements read ({p}%)":
    "{a} din {b} cerințe planificate citite ({p}%)",
  "band {band}.": "banda {band}.",
  "{n} open bugs.": "{n} buguri deschise.",
  "{n} questions for requirement owners": "{n} întrebări pentru proprietarii cerințelor",
  "on {m} requirements: {h} High, {md} Medium, {l} Low.":
    "pe {m} cerințe: {h} ridicată, {md} medie, {l} scăzută.",
  "{n} audit findings: {k}": "{n} constatări de audit: {k}",
  "on {m} requirements.": "pe {m} cerințe.",
  "{n} requirements have code but no tested-by":
    "{n} cerințe au cod, dar fără tag tested-by",
  "mostly tagging gaps when tier A dominates.":
    "în mare parte lacune de etichetare când domină tier A.",
  "{n} confirmed requirements have no code": "{n} cerințe confirmate nu au cod",
  "all requirements": "toate cerințele",
  "all": "toate",
  "requirements": "cerințe",
  "Read by the audit": "Citite de audit",
  "Agreement between runs": "Acord între rulări",
  "Audit precision": "Precizia auditului",
  "Audit findings": "Constatări de audit",
  "Fixed bugs": "Buguri rezolvate",
  "{n} on {m} requirements ({h} High, {md} Medium, {l} Low)":
    "{n} pe {m} cerințe ({h} ridicată, {md} medie, {l} scăzută)",
  "Dangling tags": "Taguri orfane",
  "Code files with a tag": "Fișiere de cod cu tag",
  "Production files watched for drift": "Fișiere de producție urmărite pentru drift",
  "Health score": "Scor Health",
  "{s} ({a} of {b} requirements green)": "{s} ({a} din {b} cerințe verzi)",
  "Contents": "Cuprins",
  "Paths are relative to the requirements folder; keep them in the repository, not in a temporary folder.":
    "Căile sunt relative la folderul de cerințe; păstrează-le în repository, nu într-un folder temporar.",
  "this page as Markdown (Export Markdown)": "această pagină ca Markdown (Exportă Markdown)",
  "this page as PDF (Export PDF)": "această pagină ca PDF (Export PDF)",
  "the graph the map and this page read": "graful citit de hartă și de această pagină",
  "the map as text": "harta ca text",
  "the open findings, per requirement": "constatările deschise, pe cerință",
  "the audit session: plan, reads, rates": "sesiunea de audit: plan, citiri, rate",
  "the bug files, one per module": "fișierele de buguri, câte unul pe modul",
  "Map written {at}.": "Harta scrisă {at}.",
  "Engine {e}.": "Engine {e}.",
  "Branch {b}.": "Branch {b}.",
  "An audit read {a} of the {b} planned requirements.":
    "Un audit a citit {a} din cele {b} cerințe planificate.",
  "Audit session: {a} of {b} planned requirements read (ranked by risk, plus a random sample), band {band}.":
    "Sesiune de audit: {a} din {b} cerințe planificate citite (ordonate după risc, plus un "
    + "eșantion aleatoriu), banda {band}.",
  "audit findings": "constatări de audit",
  "code files with a tag": "fișiere de cod cu tag",
  "Audit finding": "Constatare de audit",
  "tested-by suggestion, tier A (a test already names it)":
    "sugestie tested-by, tier A (un test o numește deja)",
  "tested-by suggestion, tier B (a test is paired by name)":
    "sugestie tested-by, tier B (un test e asociat după nume)",
  "tested-by suggestion, tier C (no test found)":
    "sugestie tested-by, tier C (niciun test găsit)",
  "Same text under two ids": "Același text sub două id-uri",
  "Confirmed with a title and no clause": "Confirmate cu titlu și fără clauză",
  "Design rule": "Regulă de design",
  ["audit findings say the code does not do what a clause says: confirm "
    + "each with a reproduction, then fix it or file a bug"]:
    "constatări de audit spun că codul nu face ce spune o clauză: confirmă fiecare cu o "
    + "reproducere, apoi repar-o sau deschide un bug",
  ["requirements have a test that already names them: add the "
    + "`# tested-by: ID` tag the suggestion gives"]:
    "cerințe au deja un test care le numește: adaugă tagul `# tested-by: ID` din sugestie",
  ["requirements have code but no test: tag the test with "
    + "`# tested-by: ID`, or write one"]:
    "cerințe au cod dar nu au test: taggează testul cu `# tested-by: ID`, sau scrie unul",
  ["audit findings say a test cannot fail when the code is wrong: "
    + "strengthen those tests first"]:
    "constatări de audit spun că un test nu poate pica atunci când codul e greșit: întărește întâi aceste teste",
  ["tagged tests cannot fail: they assert nothing, a constant, or a value "
    + "against itself; assert the behaviour, or drop the `# verifies:` tag"]:
    "teste taggate nu pot pica: nu verifică nimic, verifică o constantă sau o valoare cu ea "
    + "însăși; verifică comportamentul, sau scoate tagul `# verifies:`",
  ["requirements repeat another's text word for word: merge or "
    + "retire one of each pair"]:
    "cerințe repetă cuvânt cu cuvânt textul alteia: unește-le sau retrage una din fiecare pereche",
  ["confirmed requirements have a title and no clause: write the "
    + "clause or set them back to draft"]:
    "cerințe confirmate au titlu dar nicio clauză: scrie clauza sau trece-le înapoi în draft",
  ["places break the repository's own design rules: see each rule's "
    + "list under Problem types"]:
    "locuri încalcă regulile de design ale repository-ului: vezi lista fiecărei reguli la Tipuri de probleme",
  ["tags name no requirement (RM001): fix the id or remove the tag; "
    + "`gate` lists each line"]:
    "taguri nu numesc nicio cerință (RM001): corectează id-ul sau șterge tagul; `gate` listează fiecare linie",
  ["confirmed requirements have no code: tag it with `# implements: ID`, "
    + "or set them back to draft"]:
    "cerințe confirmate nu au cod: taggează-l cu `# implements: ID` sau trece-le înapoi în draft",
  ["requirements changed since the lock: re-check their code, then "
    + "`sync --accept-drift \"reason\"`"]:
    "cerințe s-au schimbat de la lock: reverifică-le codul, apoi `sync --accept-drift \"motiv\"`",
  ["High questions are open: answer each in its requirement's Description "
    + "or Cases"]:
    "întrebări cu prioritate ridicată sunt deschise: răspunde la fiecare în Description sau Cases",
  ["requirements have code but no test: tag the test with "
    + "`# tested-by: ID`"]:
    "cerințe au cod dar nu au test: taggează testul cu `# tested-by: ID`",
  ["cases are not proven by a test: add `# verifies: ID#CASE-N` on the "
    + "test that proves each"]:
    "cazuri nu sunt dovedite de un test: pune `# verifies: ID#CASE-N` pe testul care îl dovedește",
  "P0/P1 bugs are open: fix them, then `sync --fix ID`":
    "buguri P0/P1 sunt deschise: rezolvă-le, apoi `sync --fix ID`",
  "Medium questions are open: read them once the High ones are answered":
    "întrebări cu prioritate medie sunt deschise: citește-le după cele ridicate",
  ["A word on a list matched. Often not a real gap; read it when you "
    + "have time."]:
    "S-a potrivit un cuvânt dintr-o listă. Adesea nu e o lipsă reală; "
      + "citește-le când ai timp.",
  "Review": "De revizuit",
  "{n} only await confirmation — see Review.":
    "{n} așteaptă doar confirmarea — vezi De revizuit.",
  "gate passes": "poarta trece",
  "gate blocks the build — {n} error": "poarta blochează build-ul — {n} erori",
  "Nothing to fix.": "Nimic de reparat.",
  "Nothing in this tab.": "Nimic în această filtrare.",
  "The gate reports no errors, warnings or review items for this registry.":
    "Poarta nu raportează erori, avertismente sau elemente de revizuit "
      + "pentru acest registru.",
  "Other tabs may still have open items.":
    "Celelalte file pot avea încă elemente deschise.",
  // roadmap
  "done": "gata",
  "progress": "în lucru",
  "draft": "schiță",
  "planned": "planificat",
  // exports (REQ-VIEWER-1151, REQ-VIEWER-1152)
  "Export XLSX": "Exportă XLSX",
  "Requirement": "Cerință",
  "Question": "Întrebare",
  "Answer options": "Variante de răspuns",
  "Open questions": "Întrebări deschise",
  "{n} questions": "{n} întrebări",
  "Design": "Design",
  "{n} findings": "{n} constatări",
};

/* The CLI's own description of itself is chrome, not an artifact under
 * review, so it translates. Flags stay literal: `--accept-drift` is
 * something you type. A command with no entry here falls back to the
 * registry's English summary. */
export const COMMAND_RO = {  // implements: REQ-VIEWER-964
  "init":
    "Prima rulare: creează requirements/ și .reqmapignore dacă lipsesc, "
      + "scoate cerințe-schiță din codul existent, construiește lock-ul "
      + "și harta, apoi tipărește pașii următori. Idempotentă.",
  "new":
    "Învechită, scoasă în v8.0.0: scrie fișierul cerinței direct sau "
      + "cere-i asistentului. Până atunci face schelet de cerință nouă "
      + "din șablon; cu --from-todo și --id o pre-umple dintr-un item "
      + "din TODO.md.",
  "clarify":
    "Întreabă ce nu a răspuns cerința: termeni fără prag măsurabil, "
      + "numere fără unitate, cantități nemărginite, clauze fără caz, "
      + "lipsa căii de eșec. Doar citește, iese mereu cu 0.",
  "gate":
    "Verdictul complet: legăturile tag-urilor, driftul, legătura cu "
      + "testele, apoi lizibilitatea cerințelor și prospețimea hărții "
      + "comise. Doar raportează.",
  "sync":
    "Reconstruiește tot ce e derivat: lock-ul, harta, digestul de "
      + "constatări, regiunile paginii de prezentare. --accept-drift "
      + "când un contract confirmat chiar s-a schimbat.",
};
