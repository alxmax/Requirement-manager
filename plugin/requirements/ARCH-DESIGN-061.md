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
> never stop growing. `design` reads the repo's code (Python through `ast`, the brace
> languages through masked-text heuristics) and names the shapes
> the four OOP pillars would fix, plus the house standards a reviewer checks by eye, so the
> reader who came to understand a file also sees where its design pulls against it. It
> advises; it never gates.

Every bullet below is binding.
- `design` reports encapsulation and abstraction candidates: module state written from functions, long parameter lists, data clumps, long or deeply nested functions, prefix families. [[REQ-DESIGN-950]]
- `design` reports inheritance and polymorphism candidates: unrelated classes sharing method names or bodies, `isinstance` chains, equality switches on one value. [[REQ-DESIGN-951]]
- `design` prints the candidates grouped by pillar with one advice line each, emits JSON on request, skips test files, always exits 0, never enters the gate. [[REQ-DESIGN-952]]
- `design` reports house standards per file: length, wide lines, public definitions without a docstring, definitions per file. [[REQ-DESIGN-953]]
- The same analysis folds into one design score that rides in `_map.json`, the `_map.md` header and `health`. [[REQ-DESIGN-954]]
- JS/TS, C/C++, Java, C#, Go, Rust, Kotlin, Swift, Scala, Dart and PHP are read through brace-matching heuristics that feed the same shape checks. [[REQ-DESIGN-955]]

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
  Given  the engine's command registry and gate rule registry
  When   both are inspected
  Then   `design` is a registered command and no gate rule invokes it

CASE-4
  Given  a repo with one clean Python module
  When   `map` and `health --json` run
  Then   `_map.json` carries `design.score` 100 and the health JSON carries `design_score` 100

CASE-5
  Given  a JavaScript file with a seven-parameter function and a four-case switch
  When   `design` runs
  Then   it reports a long parameter list and a type switch, the same kinds a Python file would

## Context
**Notes**
- Python is the only language read through a real parser (`ast`); the brace languages go through heuristics, so a candidate there is a stronger invitation to look than a fact.
- A candidate is a shape worth a look, never a defect. Run on this repo it reports the engine's own long functions and its 7,800-line file honestly; ADR-0014 keeps that file whole on purpose, and an advisory line does not reopen a decision.

--------------------


---
id: REQ-DESIGN-950
status: confirmed
level: code
layer: feature
owner: Alex
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
satisfies: [ARCH-DESIGN-061]
---

# The `design` report

## Description
> The report is read by a person deciding what to refactor next, and by a tool that
> wants the same list as data. It walks the same tree the scanner walks, leaves test
> files out (a long test is not a design smell), and never changes an exit code.

Every bullet below is binding.
- `design` walks `code_root` with the scanner's walk (`.reqmapignore` honoured), reads the program-logic files (`DESIGN_EXTS`) and skips test paths (`_is_test_path`).
- `design` prints one block per group in the order encapsulation, abstraction, inheritance, polymorphism, standards, each line as `file:line  kind  detail`, followed by the distinct advice sentences of that block.
- `design --json` emits `{"files": N, "findings": [...]}` with every candidate record and nothing on stdout besides the JSON.
- With no candidate, `design` prints one line saying so and the file count.
- A file that does not parse yields no candidate and no error.
- `design` exits 0 in every case and no gate rule reads it; the thresholds are `CONFIG_KEYS` entries.

## Cases
CASE-1 — grouped report, tests skipped, exit 0
  Given  a module and a test file both writing a global
  When   `cmd_design` runs
  Then   it returns 0, prints `Encapsulation (1)` with the module's line, omits the test file and ends with the advisory note

CASE-2 — JSON and the clean case
  Given  a repo with one clean, documented module
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
satisfies: [ARCH-DESIGN-061]
---

# Code-writing standards

## Description
> The rules a reviewer checks by eye on every file, made mechanical and tunable: how
> long a file may grow, how wide a line, whether a public name explains itself, how
> many definitions one module holds. One finding per file per rule, so a 2,000-line
> file is one line in the report, not two thousand.

Every bullet below is binding.
- A file with more than `DESIGN_FILE_MAX_LINES` lines is one `file-too-long` candidate at line 1.
- A file with lines wider than `DESIGN_LINE_MAX` columns is one `line-too-long` candidate reporting the count and the first such line.
- A file with more than `DESIGN_FILE_MAX_FUNCS` top-level functions and classes is one `too-many-definitions` candidate.
- With `DESIGN_DOCSTRING_PUBLIC` set, a Python file whose public top-level functions or classes (no leading underscore) lack a docstring is one `missing-docstring` candidate naming them; set to 0, the check is off.
- Standards candidates carry the pillar `standards` and print as the last block of the report.

## Cases
CASE-1 — every standard fires once per file
  Given  thresholds of 5 lines and 2 definitions, a file with three undocumented functions and one 120-column line
  When   `_design_file` reads it
  Then   `file-too-long`, `too-many-definitions`, one `line-too-long` at that line and one `missing-docstring` naming three definitions are reported, all under standards

CASE-2 — a small documented file is silent
  Given  a short file whose public function has a docstring and whose helper is private
  When   `_design_file` reads it
  Then   nothing is reported

CASE-3 — the docstring rule can be switched off
  Given  `DESIGN_DOCSTRING_PUBLIC` set to 0 through `apply_config`
  When   `_design_file` reads an undocumented public function
  Then   no `missing-docstring` candidate is reported

CASE-4 — standards print last
  Given  a module with a global write and no docstring
  When   `cmd_design` prints its report
  Then   the Encapsulation block precedes the Standards block

--------------------


---
id: REQ-DESIGN-954
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DESIGN-061]
---

# Design health in the map

## Description
> A list of candidates is something you read once; a number is something you watch.
> The same walk `design` runs is folded into one record — how many Python files carry
> no candidate at all — and that record rides in the committed map next to the
> requirement graph, in the map's header, and in `health`, so design drift shows up
> where requirement drift already does.

Every bullet below is binding.
- `_design_summary(code_root)` returns `{files, clean_files, score, candidates}` over the non-test program-logic files, `score` being the percentage of files with no candidate, `candidates` the count per group; it returns `None` when there is no such file.
- `_assemble_map_data` attaches that record as `design` in `_map.json`, and omits the key when the record is `None`, so a repo without Python gains no empty key.
- `_map.md`'s header carries a `design: S/100 (C/F source files without a design candidate)` line when the record exists.
- `health` prints a design line and `health --json` carries `design_score` and `design_files` when the record exists; both are absent otherwise.
- The record is deterministic, so `map --check` treats a changed design score like any other change to the committed map.

## Cases
CASE-1 — the score counts clean files
  Given  a clean documented module, a module writing a global, and a test file writing a global
  When   `_design_summary` runs
  Then   it reports 2 files, 1 clean, score 50, one encapsulation and one standards candidate

CASE-2 — the map header and health carry the score
  Given  a corpus and one clean module
  When   the map data is assembled and `health --json` runs
  Then   `_map.json` carries `design.score` 100, the `_map.md` header names it, and the JSON carries `design_score` 100

CASE-3 — no program logic, no key
  Given  a repo whose only code is a stylesheet
  When   the map data is assembled and `health --json` runs
  Then   neither `design` nor `design_score` is present

--------------------


---
id: REQ-DESIGN-955
status: confirmed
level: code
layer: feature
owner: Alex
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
- The docstring rule does not apply outside Python; a program-logic file in a language with neither analyzer (Ruby, Elixir) gets the standards checks only.

## Cases
CASE-1 — JavaScript shapes
  Given  a JS file with a seven-parameter function, two unrelated classes sharing three methods, a four-case switch and a three-branch instanceof chain
  When   `_design_file` reads it
  Then   it reports long-parameter-list, shared-methods, duplicate-method, a type-switch on `kind` and an isinstance-chain on `v`

CASE-2 — C++ shapes
  Given  a C++ file with a 90-line function and a three-branch dynamic_cast chain
  When   `_design_file` reads it
  Then   it reports long-function for `compute` and an isinstance-chain, and no missing-docstring

CASE-3 — masking
  Given  a JS function whose string literal and comment contain braces
  When   `_design_mask` runs and the file is analysed
  Then   the literal is gone from the masked text, the newline count is unchanged, and no length or nesting candidate is reported

CASE-4 — standards only elsewhere
  Given  a Ruby file with one 120-column line
  When   `_design_file` reads it
  Then   only line-too-long is reported, and a clean Ruby file reports nothing
