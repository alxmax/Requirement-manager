---
id: ARCH-DESIGN-061
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: could-have
milestone: v3.4
depends_on: [ARCH-SCAN-002, ARCH-CONFIG-060, ARCH-CMDREGISTRY-033]
satisfies: [SYS-READ-103]
---

# Advisory design review

## Description
> Code written in a long AI session drifts toward procedural sprawl: state in module
> globals, six-parameter functions, `isinstance` chains that dispatch by hand, files that
> never stop growing, lines too wide to read in a diff. `ask --design` reads the repo's
> code (Python through `ast`, the brace languages through masked-text heuristics) and
> names the shapes the four OOP pillars would fix, plus two writing rules — a file of at
> most 500 lines, a line of at most 80 columns — so the reader who came to understand a
> file also sees where its design pulls against it. It advises; it never gates.

Every bullet below is binding.
- `design` reports encapsulation and abstraction candidates: module state written from functions, long parameter lists, data clumps, long or deeply nested functions, prefix families. [[REQ-DESIGN-950]]
- `design` reports inheritance and polymorphism candidates: unrelated classes sharing method names or bodies, `isinstance` chains, equality switches on one value. [[REQ-DESIGN-951]]
- `design` prints the candidates grouped by pillar with one advice line each, emits JSON on request, skips test files, always exits 0, never enters the gate. [[REQ-DESIGN-952]]
- `design` reports two writing standards per file: more than 500 lines, and lines wider than 80 columns. [[REQ-DESIGN-953]]
- The same analysis folds into one design score that rides in `_map.json`, the `_map.md` header (as `design pass-rate:`), `health` and `gate --audit`. [[REQ-DESIGN-954]]
- JS/TS, C/C++, Java, C#, Go, Rust, Kotlin, Swift, Scala, Dart and PHP are read through brace-matching heuristics that feed the same shape checks. [[REQ-DESIGN-955]]
- The candidates themselves ride in `_map.json` beside their score, so the viewer lists them instead of only counting them. [[REQ-DESIGN-976]]
- The design payload is excluded from every freshness comparison, so advisory data can never fail the gate. [[REQ-DESIGN-991]]

## Cases
CASE-1
  Given  a repo with one Python module writing a global from a function, and a test file doing the same
  When   `design` runs
  Then   the module's candidate is printed under Encapsulation, the test file is not mentioned, and the exit code is 0

CASE-2
  Given  a `requirements/_config.json` setting `DESIGN_PARAMS_MAX` to 2
  When   `design` runs over a three-parameter function
  Then   it reports a long parameter list

CASE-3
  Given  the gate rule registry and a repo with one module writing a global
  When   `reqmap.py ask --design` runs and the registry is inspected
  Then   it exits 0 naming `global-state`, and no gate rule invokes the review

CASE-4
  Given  a JavaScript file with a seven-parameter function and a four-case switch
  When   `design` runs
  Then   it reports a long parameter list and a type switch, the same kinds a Python file would

## Context
**Notes**
- Python is the only language read through a real parser (`ast`); the brace languages go through heuristics, so a candidate there is a stronger invitation to look than a fact.
- A candidate is a shape worth a look, never a defect.
- "Advisory" is a property of the whole path, not of the printer. The review is printed by `ask --design` and its summary is written into `_map.json`, `_map.md`, `health` and `audit`, where the viewer draws its design ring and Design tab. The committed map is freshness-checked, and before v8.2.0 the design rows in it could fail the gate (issue #243). [[REQ-DESIGN-991]] keeps the design payload out of every freshness comparison, so the data is written but never gated.
- Retired with ADR-0047 and not restored by ADR-0051: the `metrics` pillar (RFC), the docstring and definitions-per-file standards, and the `reqmap_design` MCP tool. Their requirements stay `deprecated`.

--------------------


---
id: REQ-DESIGN-950
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
satisfies: [ARCH-DESIGN-061]
---

# Encapsulation and abstraction candidates

## Description
> Encapsulation asks who owns a piece of state; abstraction asks whether a name says
> what a block does. `_design_file` answers both from the syntax tree alone, with
> thresholds a repo can tune, so the signals stay cheap and deterministic.

Every bullet below is binding.
- A function containing a `global` statement is a `global-state` candidate naming the globals it writes.
- A function with more than `DESIGN_PARAMS_MAX` parameters (`self`/`cls` excluded) is a `long-parameter-list` candidate.
- A set of at least `DESIGN_CLUMP_MIN` parameter names shared by at least `DESIGN_CLUMP_FUNCS` functions is one `data-clump` candidate, reported once at the first carrier.
- A function spanning more than `DESIGN_FUNC_MAX_LINES` lines is a `long-function` candidate; one nesting `if`/`for`/`while`/`with`/`try` deeper than `DESIGN_NESTING_MAX` is a `deep-nesting` candidate.
- At least `DESIGN_PREFIX_GROUP` top-level functions whose names share the token before the first underscore form one `prefix-family` candidate named by that token.
- Every candidate carries `pillar`, `kind`, `file`, `line`, `name`, `detail` and an `advice` sentence from `_DESIGN_ADVICE`.

## Cases
CASE-1 — global state and a long parameter list
  Given  a module with a function writing a global and a seven-parameter function
  When   `_design_file` reads it
  Then   it reports `global-state` and `long-parameter-list`

CASE-2 — a data clump needs three carriers
  Given  two functions sharing `host, port, user`, then a third
  When   `_design_file` reads each version
  Then   nothing is reported for two, one `data-clump` under encapsulation for three

CASE-3 — long and deeply nested functions
  Given  a 90-line function, a five-level nested function and a flat one
  When   `_design_file` reads them
  Then   `long-function` and `deep-nesting` are reported and the flat one is silent

CASE-4 — a prefix family
  Given  six top-level functions named `_scan_0` to `_scan_5`
  When   `_design_file` reads them
  Then   one `prefix-family` candidate named `scan` is reported under abstraction

--------------------


---
id: REQ-DESIGN-951
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
satisfies: [ARCH-DESIGN-061]
---

# Inheritance and polymorphism candidates

## Description
> Two classes with the same three method names describe one interface nobody wrote
> down; a chain of `isinstance` tests is dispatch done by hand. Both are visible in the
> tree without running anything, and both are exactly the shapes a reader new to the
> file has to reconstruct in their head.

Every bullet below is binding.
- Two classes in one file with no common base, neither deriving from the other, sharing at least `DESIGN_SHARED_METHODS` non-dunder method names are one `shared-methods` candidate.
- A method whose body is identical (by `ast.dump`) in two such classes is a `duplicate-method` candidate reported at the second class.
- Classes related through a base, in either direction, are never reported.
- An `if`/`elif` chain holding at least `DESIGN_ISINSTANCE_CHAIN` `isinstance` tests on one name is an `isinstance-chain` candidate.
- An `if`/`elif` chain holding at least `DESIGN_BRANCH_CHAIN` equality tests of one name against constants is a `type-switch` candidate.
- A chain below either threshold is silent, and an `elif` is never reported as its own chain.

## Cases
CASE-1 — shared and duplicated methods
  Given  classes `A` and `B` with no base sharing `load`, `save`, `close`, two bodies identical
  When   `_design_file` reads them
  Then   one `shared-methods` and two `duplicate-method` candidates (`B.close`, `B.save`) are reported

CASE-2 — related classes are silent
  Given  `A(Base)` and `B(Base)` sharing three methods
  When   `_design_file` reads them
  Then   no `shared-methods` candidate is reported

CASE-3 — isinstance chain and type switch
  Given  a three-branch `isinstance` chain on `x` and a four-branch equality chain on `kind`
  When   `_design_file` reads them
  Then   exactly one `isinstance-chain` (`x`) and one `type-switch` (`kind`) are reported, both under polymorphism

CASE-4 — short chains are silent
  Given  a two-branch `isinstance` chain and a three-branch equality chain
  When   `_design_file` reads them
  Then   nothing is reported

--------------------


---
id: REQ-DESIGN-952
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
satisfies: [ARCH-DESIGN-061]
---

# The `design` report

## Description
> The report is read by a person deciding what to refactor next, and by a tool that
> wants the same list as data. It walks the same tree the scanner walks, leaves test
> files out (a long test is not a design smell), and never changes an exit code.

Every bullet below is binding.
- `design` walks `code_root` with the scanner's walk (`.reqmapignore` honoured), reads the program-logic files (`DESIGN_EXTS`) and skips test paths (`_is_test_path`).
- `design` prints one block per group in the order `DESIGN_PILLARS` declares — encapsulation, abstraction, inheritance, polymorphism, standards — each line as `file:line  kind  detail`, followed by the distinct advice sentences of that block.
- `design --json` emits `{"files": N, "findings": [...]}` with every candidate record and nothing on stdout besides the JSON.
- With no candidate, `design` prints one line saying so and the file count.
- A Python file that does not parse yields no candidate, standards included, and no error.
- `design` exits 0 in every case and no gate rule reads it; the thresholds are `CONFIG_KEYS` entries.

## Cases
CASE-1 — grouped report, tests skipped, exit 0
  Given  a module and a test file both writing a global
  When   `cmd_design` runs
  Then   it returns 0, prints `Encapsulation (1)` with the module's line, omits the test file and ends with the advisory note

CASE-2 — JSON and the clean case
  Given  a repo with one clean module
  When   `cmd_design` runs with and without `--json`
  Then   the JSON reads `files 1, findings []` and the text run says no candidates were found

CASE-3 — a syntax error is not a finding
  Given  a file that does not parse
  When   `_design_file` reads it
  Then   it returns an empty list

CASE-4 — thresholds come from the config
  Given  `DESIGN_PARAMS_MAX` set to 2 through `apply_config`
  When   `_design_file` reads a three-parameter function
  Then   it reports `long-parameter-list`

--------------------


---
id: REQ-DESIGN-953
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
satisfies: [ARCH-DESIGN-061]
---

# Code-writing standards

## Description
> Two rules a reviewer checks by eye on every file, made mechanical and tunable: a
> file stays at most 500 lines, a line at most 80 columns. One finding per file per
> rule, so a 2,000-line file is one line in the report, not two thousand.

Every bullet below is binding.
- A file with more than `DESIGN_FILE_MAX_LINES` lines (default 500) is one `file-too-long` candidate at line 1.
- A file with lines wider than `DESIGN_LINE_MAX` columns (default 80) is one `line-too-long` candidate reporting the count and the first such line.
- Both rules apply to every program-logic file the review reads, whatever its language.
- Standards candidates carry the pillar `standards` and print as the last block of the report.

## Cases
CASE-1 — each standard fires once per file
  Given  a 501-line Python file whose last line is 86 columns wide
  When   `_design_file` reads it
  Then   one `file-too-long` and one `line-too-long` at line 501 naming 80 columns are reported, both under standards

CASE-2 — the defaults are 500 lines and 80 columns
  Given  the shipped configuration and a 499-line file of 78-column lines
  When   `_design_file` reads it
  Then   the thresholds read 500 and 80, and nothing is reported

CASE-3 — the writing rules are configurable
  Given  a file with one 96-column line, then `DESIGN_LINE_MAX` set to 120 through `apply_config`
  When   `_design_file` reads it before and after
  Then   `line-too-long` is reported before and nothing after

CASE-4 — standards print last
  Given  a module with a global write on a line wider than 80 columns
  When   `cmd_design` prints its report
  Then   the Encapsulation block precedes the Standards block

--------------------


---
id: REQ-DESIGN-954
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
satisfies: [ARCH-DESIGN-061]
distinct_from: [REQ-HEALTH-968]
---

# Design health in the map

## Description
> A list of candidates is something you read once; a number is something you watch.
> The same walk `design` runs is folded into one record — how many source files carry
> no candidate at all — and that record rides in the committed map next to the
> requirement graph, in the map's header, and in `health`, so design drift shows up
> where requirement drift already does.

Every bullet below is binding.
- `_design_summary(code_root)` returns `{files, clean_files, score, candidates}` over the non-test program-logic files, `score` being the percentage of files with no candidate, `candidates` the count per pillar (encapsulation, abstraction, inheritance, polymorphism, standards); it returns `None` when there is no such file.
- `_assemble_map_data` attaches that record as `design` in `_map.json`, and omits the key when the record is `None`, so a repo without program logic gains no empty key.
- `_map.md`'s header carries a `design pass-rate: S% (C/F source files without a design candidate)` line when the record exists.
- `health` prints a design line and `health --json` carries `design_score` and `design_files` when the record exists; both are absent otherwise.
- `gate --audit` prints a design pass-rate line and row, and its JSON carries the record as `design`, when the record exists.
- The record is deterministic, but it is advisory: a changed design score never makes `map --check` report the map stale (REQ-DESIGN-991).

## Cases
CASE-1 — the score counts clean files
  Given  a clean module, a module writing a global, and a test file writing a global
  When   `_design_summary` runs
  Then   it reports 2 files, 1 clean, score 50, one encapsulation candidate and no standards candidate

CASE-2 — the map header and health carry the score
  Given  a corpus and one clean module
  When   the map data is assembled and `health --json` runs
  Then   `_map.json` carries `design.score` 100, the `_map.md` header (as `design pass-rate:`) names it, and the JSON carries `design_score` 100

CASE-3 — no program logic, no key
  Given  a repo whose only code is a stylesheet
  When   the map data is assembled and `health --json` runs
  Then   neither `design` nor `design_score` is present

## Context
**Notes**
- `distinct_from: REQ-HEALTH-968` - `REQ-HEALTH-968` carries the requirement health record in the map; this carries the code design record.

--------------------


---
id: REQ-DESIGN-955
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v4.2
satisfies: [ARCH-DESIGN-061]
---

# Brace-language heuristics

## Description
> The engine ships no parser for JavaScript, C++ or Java and never will (stdlib only),
> but a reviewer's eye does not need one: a function head, a matched pair of braces, a
> `switch` with many cases, two classes listing the same methods. `_design_brace` reads
> those shapes from the source with comments and strings masked out, and feeds the same
> shape checks the Python analyzer feeds, so every language reports the same kinds at the
> same thresholds.

Every bullet below is binding.
- `_design_mask` replaces comments (`//`, `/* */`) plus string, char and template literals with spaces of the same length. Every newline is kept, so brace matching never sees text.
- A function is a head matching `_BRACE_FUNC_RE` (`name(params) {`, with optional modifiers, return type or arrow form) whose name is not a control keyword; its length, nesting depth (brace depth inside the body) and parameter names feed `_design_shape_findings` exactly as Python's do.
- A class, struct or interface body is matched by braces. Its methods are the functions inside it, its bases the identifiers after `extends`/`implements`/`:`. Shared and duplicated methods come from the shared checks.
- An `if`/`else if` chain collects `instanceof`, `typeof`, `dynamic_cast` and `x is T` tests as type tests, and `x == literal` tests as equality tests; a `switch (x)` counts one equality test per `case`; both feed `_design_chain_findings`.
- A program-logic file in a language with neither analyzer (Ruby, Elixir) gets the standards checks only.

## Cases
CASE-1 — JavaScript shapes
  Given  a JS file with a seven-parameter function, two unrelated classes sharing three methods, a four-case switch and a three-branch instanceof chain
  When   `_design_file` reads it
  Then   it reports long-parameter-list, shared-methods, duplicate-method, a type-switch on `kind` and an isinstance-chain on `v`

CASE-2 — C++ shapes
  Given  a C++ file with a 90-line function and a three-branch dynamic_cast chain
  When   `_design_file` reads it
  Then   it reports long-function for `compute` and an isinstance-chain

CASE-3 — masking
  Given  a JS function whose string literal and comment contain braces
  When   `_design_mask` runs and the file is analysed
  Then   the literal is gone from the masked text, the newline count is unchanged, and no length or nesting candidate is reported

CASE-4 — standards only elsewhere
  Given  a Ruby file with one 120-column line
  When   `_design_file` reads it
  Then   only line-too-long is reported, and a clean Ruby file reports nothing

---
id: REQ-DESIGN-976
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v5.6
satisfies: [ARCH-DESIGN-061]
distinct_from: [REQ-VIEWER-977]
---

# Design candidates in the map

## Description
> The score told a reader that design was at 23/100 and stopped there. To learn *which*
> shapes cost the other 77 they had to leave the map and run `ask --design` in a
> terminal, which is the moment most readers stop looking. The candidates now travel in
> the committed map beside the score they explain, so the viewer can list them in a tab
> of their own.

Every bullet below is binding.
- `_design_summary` takes `with_findings`, off by default; when it is on the returned record also carries `findings`, one entry per candidate with its `pillar`, `kind`, `file`, `line`, `name` and `detail`.
- The advice text is emitted once per `kind` in a sibling `advice` object, never repeated on each entry, because the advice belongs to the rule rather than to the occurrence.
- `_assemble_map_data` is the only caller that asks for the candidates, so `_map.json` carries them and `health --json` keeps the small score-only record a CI badge reads.
- The candidates are ordered by the walk that produced them, so a repo that did not change produces a byte-identical `design` block.

## Cases
CASE-1 — off by default
  Given  a repo with one Python file carrying a design candidate
  When   `_design_summary` runs without `with_findings`
  Then   the record carries `files`, `clean_files`, `score` and `candidates`, and neither `findings` nor `advice`

CASE-2 — the map carries them
  Given  the same repo
  When   `map` runs
  Then   `_map.json`'s `design` object carries a `findings` list whose length equals the summed `candidates` counts, and an `advice` entry for every `kind` present

CASE-3 — the badge payload is unchanged
  Given  the same repo
  When   `health --json` runs
  Then   its output carries no `findings` key

CASE-4 — deterministic
  Given  a repo whose code did not change
  When   `map` runs twice
  Then   both runs write the same `design` block

## Context
**Notes**
- `distinct_from: REQ-VIEWER-977` - `REQ-VIEWER-977` is the viewer tab that renders the design candidates; this emits them into `_map.json`.

---
id: REQ-DESIGN-978
status: deprecated
level: code
layer: feature
owner: Alex
milestone: v5.6
satisfies: [ARCH-DESIGN-061]
---

# Class metrics, the C&K half that applies

## Description
> Every other check in this review measures a function or a file, so the one shape it
> could never name is the class that quietly became several: `Scene` carries 62 methods
> over 14 fields and each individual method looks reasonable. Chidamber & Kemerer measure
> the class itself, and three of their six say something about code shaped like this one.
> The pillar reports those three and deliberately omits the rest.

Every bullet below is binding.
- `_design_metrics` reports `high-response` when a class's own methods plus the distinct method names they call exceed `DESIGN_RFC_MAX` (C&K RFC).
- A class's instance fields are the names assigned through `self.<name>`, those `__slots__` declares, and those a class-body annotation declares — the form `@dataclass`, attrs and Pydantic use, whose assignment happens in a synthesised `__init__` the tree never contains.
- A class with no field at all is skipped for cohesion. A `dict` subclass keys its state elsewhere, so it has no field two methods could share.
- The output names what the pillar did not measure whenever it renders, and when the review renders empty. An absent finding therefore never reads as a measured pass on DIT, NOC or CBO.
- The pillar reads Python only, through `ast`, since counting methods and field access needs a parser rather than the brace-language heuristics.
- DIT, NOC and CBO are not reported. Their absence is a decision, not a gap: the first two measure an inheritance tree a composing codebase does not have. The third needs type inference this engine does not do.
- `DESIGN_RFC_MAX` is a `CONFIG_KEYS` entry, so a repo can retune it like every other number in the review; the pillar stays advisory and never enters the gate — including through the committed artifacts the review is written into, which is where it leaked. [[REQ-DESIGN-991]]
- The pillar names its own known weakness where it prints: RFC counts every distinct method name a class calls, including library calls, so it over-reports routers, GUI callback classes and builder DSLs.

## Cases

CASE-1 — a class that reaches too far is named
  Given  a Python class whose own methods plus the distinct method names they call exceed `DESIGN_RFC_MAX`
  When   `design` runs
  Then   a `high-response` candidate is reported under Metrics, naming both counts

CASE-2 — the threshold is per repo
  Given  a `requirements/_config.json` setting `DESIGN_RFC_MAX` to 2
  When   `design` runs over a small class
  Then   that class is reported as `high-response`




CASE-3 — a small class is silent
  Given  a class with two methods calling almost nothing
  When   `design` runs
  Then   it reports no metrics candidate for that class

CASE-4 — the pillar says what it did not measure
  Given  any repo
  When   `design` renders the metrics pillar, or reports no candidate at all
  Then   the output names the metrics it does not compute, and its own over-reporting shapes

## Context
**Notes**
- LCOM1 has a known blind spot this engine does not correct: a constructor that assigns every field pairs with every other method, so a class with two otherwise disjoint halves scores zero as soon as its `__init__` touches both. The metric still finds the shape it was added for — `Scene`, whose 62 methods spread over 14 fields score 1409 — but a low LCOM is weaker evidence than a high one.
- WMC is unweighted here. C&K define it as the sum of a per-method complexity weight; counting each method as 1 is the conventional simplification, and it is the reading `god-class` reports.
- These numbers are advisory like every other candidate. `Scene` is reported and nothing gates on it; splitting it would change the public builder API, which is a semver decision rather than a lint fix.
- The thresholds 20/50/20 are the conventional textbook numbers and are UNTUNED: C&K (1994) proposed the metrics and no thresholds, so there is no primary source to cite. They have not been calibrated against any corpus and are `CONFIG_KEYS` entries a consumer is expected to retune.
- Fire rate on this repo, published rather than asserted: 1 of 9 non-test classes carries a candidate (11.1%); the same run is 3 of 121 design findings (2.5%) and 1 of 31 files (3.2%). ADR-0016's 5-40% band has no defined denominator for a code-level check — every prior application measured the requirement corpus `lint` visits — so the band is cited here as context, not as a passed bar. The confirmation sample is 1 of 1 and was made by this pillar's own author, which ADR-0022 does not accept as independent; that obligation is open and tracked in TODO.md.
- Audited by the Senate on 2026-09-05 (`runs/senate/2026-09-05_220602-senate-reqmap-ck-metrics-pillar.json`, verdict MODIFY, GO 4 / MODIFY 4 / STOP 1). Discharged in the same change: declarative fields now counted, the kinds renamed from verdicts to measurements, the thresholds marked untuned, and the unmeasured metrics named in the output. Left open on the record: an independent confirmation sample, and Musk's request to delete WMC and LCOM1 as redundant with RFC.

---
id: REQ-DESIGN-979
status: deprecated
level: code
layer: feature
owner: Alex
milestone: v5.6
satisfies: [ARCH-DESIGN-061]
---

# What the review could not measure

## Description
> A zero in a report means one of two very different things: measured and clean, or
> never measured. The metrics pillar reads Python classes only, reports three of C&K's
> six, and cannot see the state of a class that keeps it somewhere `ast` cannot follow.
> Every one of those produces the same silence, and silence in a report is read as
> good news. The review therefore counts what it could not measure and says so.

Every bullet below is binding.
- `_design_cohesion_skipped` counts the classes in a parsed tree that declare two or more methods and no field the engine can see, which are exactly the classes whose cohesion was not measured.
- `design` prints that count under the metrics pillar and again when it reports no candidate at all, in both cases naming it as unmeasured rather than clean.
- `design --json` carries `metrics_scope` and `cohesion_skipped` beside `findings`, so a machine reading the output receives the same caveats as a human reading the text.
- A file that does not parse contributes zero to the count rather than raising, because a design review is advisory and never fails on a file the rest of the engine tolerates.

## Cases
CASE-1 — the count finds the unmeasurable
  Given  a module with a `dict` subclass carrying three methods and no `self.<name>` assignment
  When   `_design_cohesion_skipped` runs over it
  Then   it returns 1

CASE-2 — a measurable class is not counted
  Given  a module whose only class assigns a field in `__init__` and has two methods
  When   `_design_cohesion_skipped` runs over it
  Then   it returns 0

CASE-3 — the machine surface carries the caveats
  Given  any repo with at least one Python file
  When   `design --json` runs
  Then   its object carries `metrics_scope` naming DIT, NOC and CBO, and a `cohesion_skipped` count

CASE-4 — an unparseable file is tolerated
  Given  a file that is not valid Python
  When   the count runs over its source
  Then   it returns 0 and nothing is raised

## Context
**Notes**
- The count is deliberately not a finding. It is a property of the run, like the file count, and promoting it to a candidate would report a class for the crime of being unreadable to this engine.

---
id: REQ-DESIGN-980
status: deprecated
level: code
layer: feature
owner: Alex
milestone: v5.6
satisfies: [ARCH-DESIGN-061]
---

# The metrics that did not survive calibration

## Description
> The pillar shipped with three C&K metrics on the strength of one repo and no review.
> A Senate audit refused that, so all three were measured over seven Python corpora and
> every flag was judged by a reviewer who had not written them. Two metrics failed:
> across 65 unique classes neither WMC nor LCOM1 ever fired without RFC, and the
> independent reviewer confirmed none of their flags. They are gone. This requirement
> records the measurement, because a number nobody can find is a number nobody can
> challenge.

Every bullet below is binding.
- `_design_lcom` counts only the methods that touch at least one instance field. A method touching none has no state to share, and counting it as disjoint from every sibling adds one pair per sibling while measuring nothing.
- Cohesion is not computed for a class with fewer than two fields, because a single field admits no grouping for methods to be split across.
- `wide-class` and `low-field-sharing` are not reported, and their thresholds are gone from `CONFIG_KEYS`. RFC's own detail line still names the class's method count, so nothing a reader saw is lost.
- `_design_lcom` and `_design_py_fields` remain, tested, because the cohesion-coverage count reads the fields and a future cohesion variant starts from this reading rather than from nothing.

## Cases
CASE-1 — a field-less helper does not create incohesion
  Given  a class with one field, one method using it and six helpers touching no field
  When   `_design_lcom` runs over it
  Then   it returns 0, where counting the helpers as disjoint returned 26

CASE-2 — one field is not a grouping
  Given  a class with a single field and several methods
  When   `design` runs
  Then   no cohesion candidate is reported for it

CASE-3 — the dropped kinds are gone
  Given  any repo
  When   `design --json` runs
  Then   no finding carries kind `wide-class` or `low-field-sharing`

## Context
**Notes**
- The measurement, reproducible from `plugin/scripts/reqmap.py` over any set of Python trees: 65 unique classes across 7 corpora after collapsing 8 byte-identical copies and excluding `archive/`, `old/` and `backup/` directories, which hold successive saved versions of the same file rather than independent classes. 14 classes flagged, a fire rate of 21.5%.
- The independent review: 10 of 14 flags confirmed, 4 refused — 71%, below the 8-in-10 an independent confirmation is expected to clear. Per metric before the repair: `wide-class` 0 confirmed of 2, `high-response` 10 of 14, `low-field-sharing` 2 of 5. After excluding field-less methods `low-field-sharing` stopped firing on both classes it was right about and kept firing on the two it was wrong about.
- RFC's own precision is 10 of 14 and it is kept anyway, with its weakness printed rather than hidden: all four refusals are classes whose call count is library calls — a request router delegating to free functions, a GUI callback class, and a builder DSL over one shared accumulator. A reader who meets one of those three shapes can dismiss the flag in seconds, which is the most an advisory signal at 71% can honestly ask for.
- Six of the ten confirmed flags are copies of three distinct classes across corpora, so the distinct-finding count is nearer three. The reviewer also noted that all ten sit in throwaway analysis scripts. Both facts are recorded here rather than netted out of the headline.


---
id: REQ-DESIGN-991
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v6.3
satisfies: [ARCH-DESIGN-061]
---

# Advisory data cannot inherit a verdict

## Description
> `_map.json` is one freshness-gated artifact carrying three classes of data with three
> different severities: the requirement graph is normative, `health` is derived, and `design`
> is advisory by its own contract. The freshness comparison was all-or-nothing, so anything
> that landed in that document acquired ERROR severity by construction, whatever its own
> contract said about itself. One blank line inserted into a file no requirement claims moved
> a `line:` in `design.findings`, which made the committed map stale, which failed `gate` with
> zero requirement errors and zero lint errors.

Every bullet below is binding.
- The design payload is excluded from every freshness comparison: the `design` block of
  `_map.json` and `_map.md`'s one-line design summary.
- The data itself stays in the artifacts. The viewer renders those rows in its Design tab, so
  removing them would delete a feature to fix a severity mistake.
- Determinism is not the test for what may be gated. A freshness-checked payload stays
  stable under edits that change nothing it describes, and per-line findings do not.
- Excluding it is the same exclusion `"repo":` already carries, for the same reason: a value
  that legitimately differs without the corpus having changed is not a verdict.
- The accepted cost is that committed design rows may lag the code until the next `sync`. That
  is the correct trade for advice nobody should be blocked by.

## Cases
CASE-1 — a moved advisory line number is not staleness
  Given  a committed map and a design finding whose `line` has changed
  When   the freshness check runs
  Then   no artifact is reported stale

CASE-2 — a changed design score is not staleness
  Given  a committed map and a different design score
  When   the freshness check runs
  Then   no artifact is reported stale

CASE-3 — a changed requirement still is
  Given  a committed map and a requirement whose title has changed
  When   the freshness check runs
  Then   `_map.json` is reported stale

CASE-4 — a changed health number still is
  Given  a committed map and a different health score
  When   the freshness check runs
  Then   `_map.json` is reported stale, because health is derived from the corpus and not
         from line numbers in files no requirement claims

CASE-5 — a blank line in an untagged file does not fail the gate
  Given  a source file carrying no membership tag
  When   a blank line is inserted at its top and `gate` runs
  Then   it exits 0 and reports no stale artifact
