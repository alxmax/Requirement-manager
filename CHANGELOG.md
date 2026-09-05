# Changelog

## plugin `v5.7.0` — 2026-09-06

**The skill contract now says the specification-level axis exists — and that a flat
corpus is a supported end state, not a waypoint.** A nine-senator audit asked why the
engine does not produce a three-rung corpus on a consumer repo. The verdict was MODIFY
(GO 1 / MODIFY 6 / STOP 2) and every code candidate was refused. What survived was
documentation, and the audit corrected the proposal that raised it.

**What the audit found, verified by running it:** the read-only advisory the proposal
wanted to build **already ships**. On a throwaway three-file repo with no prior
requirement-manager, `gate --audit` prints `0/3 carry a level: - the corpus is flat`,
names all three rungs, names `satisfies:` as the edge that builds the pyramid, and
states that adopting the axis is a decision and not a defect. The claim that no CLI
surface mentions levels was true only of `--help` text.

**And the charge of overselling did not land where it was aimed.**
`plugin/skills/requirement-manager/SKILL.md` — the contract that actually reaches a
consumer — mentioned the axis zero times, and `CLAUDE.md` is not inside the shipped
`plugin/` package at all. The gap was not between the tool and its consumers; it was
that a consumer was never told the field exists.

So: both SKILL files gain one paragraph naming `level: system` / `architecture` / `code`,
saying it is off by default, that nothing infers it, that a corpus declaring none gates
exactly as it did before the field existed, and that it earns itself only once a flat
list stops explaining itself — the rungs were added here at roughly 52 requirements.
`CLAUDE.md`'s three-level section now reads as a description of this corpus rather than a
target, cites ADR-0019's dated review (**2027-03-03**, whose pre-committed remedy is
*removal*, not more documentation), and carries current counts (68/159/236, not
62/126/197).

**One correction to the record:** ADR-0019's Evidence line cited
`runs/senate/2026-09-02_*-v-model*.json`, a glob matching no file. It now names the two
real bundles. The decision is untouched — only the citation was wrong.

Nothing in the engine changed. No new verb, no new flag, no new gate rule.

## plugin `v5.6.2` — 2026-09-06

**Three deep-nesting findings gone, and one silent inconsistency with them.**
`scan_ac_verifies` and `scan_test_levels` were the same twenty lines twice — same prune,
same sort, same read, same Python string-masking — differing only in what they did with a
masked line. Both nested six deep because the per-line work sat at the bottom of four
enclosing loops. They now share `_walk_code_lines`, which yields `(rel, lineno, line)`
already masked.

They also disagreed on one thing, silently: `scan_ac_verifies` passed the ignore patterns
to `_prune_dirs` and `scan_test_levels` did not, so the level scanner descended into
directories the coverage scanner skipped — including, in a repo with agent worktrees, a
full second copy of itself. It filtered them out per file afterwards, so the answers
matched, but it walked the copy to do it. The shared walk prunes.

**`parse_frontmatter` separated finding the block from reading it.** It nested six deep
because the key/value reader sat inside the block detection: two `if`s to locate the `---`
fences, then the reader's own loop and its per-shape branches on top. Now
`_parse_meta_lines` takes the lines between the fences and never has to know where the
block began. 40 lines → 13, with a 32-line helper.

**Both proved neutral, not assumed neutral**, as `TODO.md` requires: the two scanners were
run old-versus-new over two code roots — identical output, 193 and 1 capability keys — and
the parser over all 283 frontmatter blocks in the corpus plus seven hand-made edge cases
(unclosed inline list, empty block list, BOM, no frontmatter, unterminated fence, a `#`
inside a quoted value): **0 differing**.

reqmap.py deep-nesting findings 15 → 13; repo-wide 119 → 117.

## plugin `v5.6.1` — 2026-09-05

**The published Action was broken, and the guard that exists to catch this said OK.**
`check/action.yml` contained two copies of its own steps: a corrected one, and the older
one nobody deleted. The old copy ran `reqmap.py map --check` and `reqmap.py lint --strict`
as separate steps, both on by default — verbs removed in `v5.0.0`. Any consumer on
`check@v5` with a v5 engine got `exit 2, unknown command` on step 2 of 3. This repo's CI
calls the engine directly and never runs its own action, which is why nothing caught it.
The stale copy is deleted; `gate` already performs all three checks and the `freshness`
and `lint` inputs now switch its halves off. The surviving block also read
`inputs.map-check`, an input that does not exist — so map freshness was silently disabled
for every consumer. It reads `inputs.freshness` now.

**`check_retired_verbs.py` had two blind spots and ten dead invocations went out through
them.** It scanned the `requirement-manager` skill's two files *by name*, so the plugin's
other two shipped skills were never read — six stale invocations sat in
`requirement-quality-review`, telling readers to run `reqmap.py lint` and `reqmap.py
review`. And `lint`, `map`, `site`, `scan`, `health`, `coverage`, `export`, `findings`,
`plan`, `check` and `gen-integration` were missing from its retired list, which is how
`reqmap.py site` survived in a file it *does* read. It now walks every `SKILL*.md` under
`plugin/skills/` and knows every folded verb. It also learned that a line saying a verb is
gone is not an instruction to run it, so the migration notes this repo writes on purpose
no longer trip it.

**Six of the ten were in the engine's own output**, including one that reached the
published Pages site: `architecture.html` carried "Auto-injected by `reqmap.py site`", and
`sync --attach`'s usage message told a reader to type `reqmap site`. The five user-story
narratives in requirement Context sections named `health`, `lint`, `map` and `findings`.

The guard's own docstring says folding a verb "has happened four times, and three of those
left behind an instruction that told a reader to type a command that no longer resolves".
It has now happened a fifth time — and the guard's fix is that it would catch it.

## plugin `v5.6.0` — 2026-09-05

**RM031 — the guard that left with the `confirm` verb.** `gate --audit` was run against
this repo's own corpus and reported a coverage gap on `REQ-TRACE-935`. Chasing it found
that the criterion described a command that no longer exists: until `v5.0.0`, the `confirm`
verb refused to promote a `layer: aggregate` requirement whose `depends_on` was empty. The
verb was folded away and **nothing replaced the guard.**

That matters because `aggregate` is exempt from the implements and tested-by rules on one
stated promise — it is covered *downward* by its dependencies. An empty list claims the
exemption and supplies nothing to be covered by. Reproduced before fixing: a confirmed
aggregate with `depends_on: []` passed the gate at **0 errors, 0 warnings**, exempt from
every coverage rule and covered by nothing. RM031 now warns on it (advisory, never a build
failure), `REQ-TRACE-935`'s CASE-2 describes the rule instead of the removed verb, and
`_impl_exempt`'s docstring no longer names `confirm` as a caller.

**Three smaller findings from the same self-audit, all introduced in this session:**
`REQ-VIEWER-977` was confirmed with no `tested-by:` member — the SSR smoke carried its
`verifies:` tags but never declared membership; a `verifies:` tag still pointed at
`REQ-DESIGN-978#CASE-7` after that requirement was renumbered to four cases; and the same
renumbering left CASE-4 printed above CASE-3.

The audit is the point: every one of these was made by the same hand that wrote the checks,
and the checks found them.

## plugin `v5.5.0` — 2026-09-05

**`lint_requirement` was 241 lines and is now 26.** It was a flat run of twelve check
blocks appending to one list, so reading any single check meant scrolling past the eleven
around it. The blocks already clustered — the comments said so — and each cluster reads a
different part of the requirement: `_lint_sections` (are the load-bearing sections there
and non-empty), `_lint_readability` (joins per line, anonymous subjects, sentence and
clause length), `_lint_acceptance` (criteria count, atomic-form parity), `_lint_shape`
(over-scoped, fan-out), `_lint_terms` (vague words, redundant modals) and `_lint_graph`
(file spread, layer mismatch). Every block moved verbatim.

**`cmd_next` was 128 lines and is now 78**, with the analysis in `_next_pending`. It mixed
working out what is pending with printing it, so the ranking rules were read through the
formatting and vice versa.

**Both splits are proved neutral, not assumed neutral.** `lint_requirement` was run
old-versus-new over all 236 requirements: **0 differing findings**. `cmd_next`'s output was
captured from both engines and compared: **byte-identical**. That check earned its keep
twice in this session — it is how a floor check that had started returning an exit code
from a function contracted to return a parser was caught, and how a local left on the wrong
side of a cut was caught. A batch of six splits would have hidden one.

Engine long-function findings 13 → 11; repo-wide design findings 121 → 119. The nine
functions still over 80 lines are listed in `TODO.md`, to be done one at a time with the
same equivalence check — `cmd_check` is the gate's core and is deliberately last.

## plugin `v5.4.0` — 2026-09-05

**The metrics pillar was calibrated, independently reviewed, and is now one metric
instead of three.** v5.2.0 shipped WMC, RFC and LCOM1 on the strength of one repo and no
review; the Senate refused that (`OVR`, two blocking requests undelivered). All three have
now been measured over seven Python corpora and every flag judged by a reviewer who did
not write them. Two metrics failed and are gone.

**The measurement**, reproducible from the engine over any set of Python trees: 65 unique
classes across 7 corpora, after collapsing 8 byte-identical copies and excluding
`archive/`, `old/` and `backup/` directories — which hold successive saved versions of the
same file, not independent classes. 14 classes flagged, a fire rate of **21.5%**. The
first pass counted 26 and had to be thrown away: it was the same application class counted
fifteen times across repos that hold copies of it.

**The independent review: 10 of 14 confirmed, 4 refused — 71%**, below the 8-in-10 an
independent confirmation is expected to clear. Per metric:

| | confirmed | refused |
|---|---:|---:|
| `wide-class` (WMC) | 0 | 2 |
| `high-response` (RFC) | 10 | 4 |
| `low-field-sharing` (LCOM1) | 2 | 3 |

**`wide-class` is dropped.** Zero confirmed flags, and across 65 classes it never once
fired without `high-response` — RFC's formula is `methods + distinct calls`, so WMC is
literally a term inside it, and RFC's own message already prints the method count.

**LCOM1 was repaired and then dropped anyway.** The reviewer isolated two mechanical
faults: a method touching no field intersected nothing, so every pair containing it counted
as "apart" — six pure helpers on a one-field class scored 26 against a threshold of 20 with
no split anywhere in the class — and LCOM over a single field is not a measurement at all.
Both are fixed (`_design_lcom` now counts only methods that touch state; cohesion needs two
fields). The repair made it *worse* as a signal: it stopped firing on both classes it was
right about and kept firing on the two it was wrong about. Precision 0 of 2, so it is gone
too. `_design_lcom` and `_design_py_fields` stay, tested — the coverage count reads the
fields, and a future cohesion variant starts from this reading rather than from nothing.

**RFC is kept at 71% precision, with its weakness printed rather than hidden.** All four
refusals are the same failure: a class whose call count is *library* calls, not
collaborators — a request router delegating to free functions, a GUI callback class, and a
builder DSL over one shared accumulator. The pillar now names those three shapes in its own
output, so a reader who meets one can dismiss the flag in seconds. That is the most an
advisory signal at 71% can honestly ask for.

**The coverage signal Dimon's blocking request asked for** (`v5.3.0` delivered half of it):
`design --json` now carries `metrics_scope` and `cohesion_skipped` beside `findings`, so a
machine reading the output gets the same caveats as a human reading the text, and the count
of classes whose cohesion could not be measured is stated rather than inferred.

Recorded in `REQ-DESIGN-980`, including the two facts that deflate the headline: six of the
ten confirmed flags are copies of three distinct classes, and all ten sit in throwaway
analysis scripts.

## plugin `v5.3.0` — 2026-09-05

**The C&K metrics pillar went through a nine-senator audit and came back MODIFY**
(GO 4 · MODIFY 4 · STOP 1, two rounds —
`runs/senate/2026-09-05_220602-senate-reqmap-ck-metrics-pillar.json`). Four of the
requests are discharged here; two are left open on the record rather than quietly
dropped.

**A declarative class was skipped in silence — a real defect, and the audit found it.**
`_design_py_fields` harvested only names assigned through `self.<name>` and `__slots__`.
A `@dataclass`, an attrs class or a Pydantic model declares its fields as class-body
annotations and assigns them in an `__init__` synthesised at runtime, which the AST never
contains — so the pillar saw no fields, skipped cohesion, and produced output
indistinguishable from a class it had measured and found cohesive. That is the commonest
class shape in modern Python and the shape this engine meets most often in the consumer
repos it is seeded into. Class-body annotations now count as state.

**The kinds were verdicts; they are measurements now.** `god-class` became `wide-class`
and `low-cohesion` became `low-field-sharing`. The old names asserted a defect in a review
whose own footer says a candidate "is a shape worth a look, never a defect", and
`low-cohesion`'s advice claimed methods "share no field" when LCOM1 fires on a *difference*
of pair counts — a firing class necessarily has many pairs that do share.

**The pillar now says what it did not measure.** Whenever the metrics block renders — and
when the whole review comes back empty — the output names DIT, NOC and CBO as not
measured. The reasoning for omitting them lived in a requirement no consumer reads, so on
a subclass-heavy repo an empty metrics block read as "your classes are fine" when it meant
"the two metrics that would have spoken were never computed". That is the
reassuring-wrong-count failure ADR-0016 rejected, and it was reintroduced at the code
layer.

**The thresholds say they are untuned.** C&K (1994) proposed the metrics and no
thresholds; 20/50/20 are textbook conventions with no primary source to cite and no
calibration against any corpus. The code says so where the numbers are defined.

**The fire rate is published rather than asserted**, in REQ-DESIGN-978's Context: 1 of 9
non-test classes (11.1%), which is also 3 of 121 design findings (2.5%) and 1 of 31 files
(3.2%). The audit established that ADR-0016's 5–40% band has **no defined denominator for
a code-level check** — every prior application measured the requirement corpus `lint`
visits — so the band is cited as context, not as a bar this cleared.

**Left open, on the record and not silently dropped:** the confirmation sample is 1 of 1
and was made by the pillar's own author, which ADR-0022 does not accept as independent;
and Musk's request to delete WMC and LCOM1 as redundant with RFC (all three fire on the
same single class, so two of the three have never carried independent signal here) is
recorded, not actioned. Both are tracked in `TODO.md`.

Also in this release: `main` was 290 lines of argparse-then-dispatch and is now 43, split
into `_build_parser` plus one function per verb; and a `confirmed` clause that enumerated
five pillars while six shipped is fixed, with a test asserting the requirement's
enumeration equals `DESIGN_PILLARS` so the next pillar cannot go stale in silence.

## plugin `v5.2.0` — 2026-09-05

**A `metrics` pillar: the half of Chidamber & Kemerer that says something about this
codebase.** Every other check in the design review measures a function or a file, so the
one shape it could never name is the class that quietly became several — `Scene` carries
62 methods over 14 fields and each individual method looks reasonable. The pillar reports
three C&K metrics per Python class: `god-class` (WMC, methods), `high-response` (RFC, own
methods plus the distinct ones they call) and `low-cohesion` (LCOM1, method pairs sharing
no field). Run on this repo it finds exactly one class, `Scene`, on all three counts.

**Three of the six are deliberately absent, and that is recorded rather than left to be
noticed.** DIT and NOC measure an inheritance tree, and a codebase that composes instead
of subclassing has none — they would report zero forever and teach a reader to ignore the
pillar. CBO needs type inference to resolve which class a Python name refers to, and a
coupling number that is wrong is worse than no coupling number. A TODO item asks the
`senate` skill to argue that decision, including whether silence on DIT/NOC reads as
"clean" on a consumer repo where it means "not measured".

**Cohesion is measured over real fields.** A class's state is what `self.<name> = ...`
assigns plus what `__slots__` declares; a class with no such field — a `dict` subclass
keys its data elsewhere — is skipped rather than scored as maximally incohesive, which is
what a naive LCOM does to `Requirement` and `Finding`. LCOM1's own blind spot is recorded
in the requirement's Context: a constructor touching every field pairs with every method,
so a low score is weaker evidence than a high one.

**Every public definition in the engine now carries a docstring.** The standards check
asked for one sentence saying what a caller gets back, and twelve definitions in
`reqmap.py` plus eight across the repo's tooling scripts had none. `missing-docstring` is
now zero across the whole repo.

## plugin `v5.1.0` — 2026-09-05

**The design candidates are in the map, in a tab of their own.** `_map.json` carried the
design *score* and nothing else, so a reader who saw 23/100 and wanted to know which
shapes cost the other 77 had to leave the viewer and run `gate --design` in a terminal —
which is where most readers stop looking. `_design_summary` now takes `with_findings`,
and `map` is the one caller that asks for them: the record gains a `findings` list (one
entry per candidate, with its pillar, kind, file, line, name and detail) and a sibling
`advice` object holding each kind's advice once, because the advice belongs to the rule
and not to the occurrence.

`health --json` is deliberately left alone. It is a CI badge payload, so a caller reading
a score keeps getting the same small object rather than a few hundred rows it never asked
for — which is why the flag is opt-in rather than always on.

**Problems grew a third origin.** The tab lists the candidates grouped by pillar, the
same shape the CLI prints, and is offered only when the map actually carries some — an
older map leaves it unoffered rather than rendering an empty shell. They are kept out of
`All` and out of every severity count on purpose: these rows are about a *file* rather
than a requirement, they gate nothing, and 125 advisory candidates dropped into the inbox
would bury the six signals that are actually open about the corpus. ADR-0028 already made
origin a first-class tab here rather than a severity; this is the third one.

## plugin `v5.0.0` — 2026-09-05

**Breaking: the CLI is six verbs.** `init`, `new`, `gate`, `sync`, `confirm`, `clarify`.
Eleven verbs became flags on those six, and one was deleted outright. Nothing lost a
capability: not one `cmd_*` function was removed in the fold, so every behaviour still
exists and every test that covered it still runs. What moved is the entry point.

    next, dupes, design, audit        gate --risk / --dupes / --design / --audit
    show, search, review, implement   gate --show / --search / --review / --implement
    draft, draft --plan               init, init --plan
    suggest-verifies                  sync --suggest-verifies
    retire                            confirm --retire

The shape follows what the engine already did. `gate` was a three-in-one merge before this
(check + lint + map) done by adding flags rather than renaming the verb; `audit` already
called next, dupes, design and coverage internally; `init` already made the same
`cmd_extract()` call as plain `draft`. Four of the eleven were therefore a registry change
only.

**Breaking: there is no `confirm` command, and an edit takes a confirmation back.** Confirming
was the wrong shape as a command: it let anything that could type — a script, an agent, a habit —
record a human's judgement. Worse, the judgement outlived the thing it was about, because nothing
connected editing a contract to re-validating it. A status is now set by editing the frontmatter,
and `sync` writes `draft` back into any `confirmed` contract whose binding content changed,
naming each one. `--accept-drift` keeps the status: it is the human saying the edit is still
valid, which now has to be said rather than assumed.

The cost is stated rather than hidden: a demoted requirement stops being enforced — no
`implements:` requirement, no drift check — until someone confirms it again. That is why the
demotion prints loudly, by name, with the sentence "These no longer gate". The invariant the
command used to guard survives in the gate, where `RM006` makes a confirmed requirement with no
code an error on every run.

`retire` moves with it, to `sync --retire ID`. Five verbs remain: `init`, `new`, `gate`,
`sync`, `clarify`.

**`translate` is gone, and the map still reads Romanian.** The command that WROTE
`requirements/_i18n/<locale>.json` was deleted, together with everything that spawned a
`claude` subprocess: the language detection, the corpus-majority vote, the
structural-fidelity check. The reading half is untouched, so the viewer's EN/RO toggle works
exactly as before — verified, not assumed: 227 of 231 nodes still carry `i18n.ro` after the
change. No subcommand shells out to anything any more.

The consequence is stated rather than hidden: **the translation cache now decays.** An entry
is served only while its hash matches the requirement, so every requirement edited from here
on silently loses its translation and the engine cannot produce a new one. Refreshing one is
now a manual step.

**New guard: `scripts/check_retired_verbs.py`.** It fails when a live instruction names a
verb the engine no longer has. This project has folded verbs four times, and three of those
left a dead instruction behind — `map` in a consumer's CLAUDE.md, `findings` in a consumer's
script, and the `v4.0.0` cut which shipped a `SKILL.md` documenting `scan` after it was gone.
None failed at merge, none failed in CI; each failed later, when someone typed what the docs
told them to. The check found thirteen more of exactly that in this repo's own skill files.
Wired into the pre-commit hook and CI.

**The published action alias moves to `check@v5`**, per ADR-0029: the alias tracks the
plugin's major. A consumer pinned to `check@v4` keeps the four-verb engine and is unaffected
until it re-pins.

**The command layer takes one `Workspace` instead of six loose arguments.** `gate
--design` named the same clump fifteen times: `reqs`, `members`, `reqs_dir`,
`code_root` and the two coverage views were computed together in `main` and then
threaded, in varying orders, through every `cmd_*` function — `cmd_check` alone took
eleven parameters. They are now one object, built once by `Workspace.load`, and
`GateContext` derives from it rather than re-listing its fields. Each command body is
unchanged: the object is unpacked back into the same locals on the first line, so the
refactor moved the boundary and nothing else. Every command-level long-parameter-list
finding is gone (`cmd_check` 11 → 6, `cmd_retire` 9 → 6, `cmd_audit` 8 → 3,
`cmd_health` 7 → 4, `cmd_site` 7 → 6) and the engine's encapsulation findings fell
from 25 to 8. Internal shape only — no CLI, schema or artifact change.

**The diagram builder grew the value objects its parameter lists were asking for.**
`Rect` (x, y, w, h), `Style` (stroke/fill plus the four Excalidraw modifiers and the
group) and `TextStyle` (size, colour, both alignments) replace the long positional
runs through `_base` (13 parameters), `_text_el` (11), `_iso_polygon` (12) and
`_place` (8). `align`'s six-branch `axis` chain became a dispatch table, `_move_node`
lost four levels of nesting behind two named lookups, `save`'s 125-line body split
into hard checks, a table of advisory checks and the write, and the viewer page and
the `discover` stub moved into module-level templates. 51 findings → 40; all 60
builder tests unchanged and passing. **The public builder API is untouched** — `box`,
`row`, `grid`, `arrow` and `save` keep their signatures, so every existing generator
still runs. The 38 remaining findings all sit on those public signatures; collapsing
them into `Rect`/`Style` is a breaking change and is deliberately not in this release.

**README's command table matched a CLI that no longer exists.** It documented
twenty-four verbs — `map`, `next`, `scan`, `lint`, `show`, `health`, `export`,
`draft`, `plan`, `findings`, `confirm`, `translate` and the rest — every one of which
this release folded into a flag or removed. Rewritten to the five real verbs, with a
table each for `gate`'s read-only questions and `sync`'s write modes, and a note
saying where each removed verb went. The engine's line count in the repo tour was
also three thousand lines stale.

## plugin `v4.2.2` — 2026-09-05

**No more line-ending diff on `SKILL.md` after every `sync` on Windows.** The generated
command region was written with bare LF inside a CRLF file. The freshness check reads that
file with universal newlines, so CRLF collapsed to LF before the comparison and the gate saw
nothing wrong — git did, and the working tree carried a line-ending-only diff after every
regeneration. The region body now takes the file's own convention, the way
`tool_definition.json` already did. `SKILL.universal.md` carried the same LF island and is
corrected once here.

## plugin `v4.2.1` — 2026-09-05

**`SKILL.md`'s command list is generated from the registry.** It is the contract an assistant
reads when it meets the engine on a fresh repo, and a blanket rename in the `v4.0.0` verb cut had
left it documenting `scan` after it was gone, five different verbs under the name `sync`, `gate`
twice (the second describing the lint), and `clarify`, `implement`, `retire`, `review` and
`search` nowhere at all — a wrong name there is a wrong action on the user's repo. The list now
lives in the same `<!--##REQMAP:COMMANDS##-->` region `SKILL.universal.md` already used, rendered
from `COMMANDS` by `gen-integration` as a grouped bullet list, and RM028 fails the gate when it is
stale. The hand-written prose around it is untouched. Both generated surfaces now walk one
region table, so adding a third is one line.

The paragraph claiming `check` "still works" is corrected: it was removed in `v4.0.0`.

## plugin `v4.2.0` — 2026-09-04

**`audit`: every pass that discovers a problem, in one report.** The engine grew one verb per
question — is it linked, is it drifted, is it duplicated, is it tagged, is the design rotting —
and answering "how is this repo doing" came to mean remembering all of them, so a reader who
does not already know the command list never meets most of the answers. `audit` runs the gate,
`next`, `dupes`, `design` and tag coverage together, prints a summary naming what each found and
the verb that produces it, then each section's own output. Read-only, and the exit code is the
**gate's alone**: advice that can fail a build stops being read and starts being suppressed.

**An exemption nobody justified is now a finding (RM030).** `lint_exempt:` was the cheapest thing
in the tool to reach for — one frontmatter token silences a check permanently, nobody has to say
why, and nothing mentions it again. So "split this requirement" and "add one word here" cost a
reader the same, and the wrong one kept winning. Three changes, together:

- `audit` lists **every** exemption in force with its requirement and the check it silences.
- `gate` warns when the requirement's own prose never mentions the check it exempts itself from.
  Warn-only and never promoted by `--strict`: the point is to make silencing cost a sentence a
  reviewer can argue with, not to make it impossible.
- the `ac-count-high` and `over-scoped` findings now name `clarify <ID> --decompose`, which
  scaffolds the extra clause out. They used to say only "consider splitting", while the skill
  contract advertised the exemption as a one-line fix.

The six exemptions in this repo's own corpus that carried no reason now carry one.

**`audit` says whether the corpus has a shape at all.** `level:` ships commented out in the
template, so a corpus never gains the V-model axis by itself and every surface that reads a level
quietly defaults it — a repo can run the engine for months with every requirement on one rung and
nothing ever mentioning the other two. The report states the spread across the rungs, and when
almost nothing is levelled it says the corpus is flat and names the three rungs and the
`satisfies:` edge that builds the pyramid. Nothing about this warns or fails: adopting a level
axis is a decision, not a defect.

**`sync` ends by saying what it found.** One line per signal that is not clean — unjustified
exemptions, a flat corpus, design candidates, untagged code, and a `TODO.md` whose newest
milestone is behind the requirements' — and nothing at all when they are all clean, so a line
that appears is news. It changes neither what `sync` writes nor its exit code.

## plugin `v4.1.0` — 2026-09-04

**The two numbers `next` opens with now travel with the map.** `_map.json` gained a `health`
record beside the existing `design` one, and the viewer's rail renders both as rings under
the navigation — the corpus score and the advisory design score, each with the fraction
behind it. The record is computed once, by `_health_record` in the engine: the viewer
displays what it is handed and computes nothing, because a score defined twice is a score
the terminal and the browser will eventually disagree about.

The health ring is coloured by band and opens the Problems inbox. The design ring stays in
one neutral ink and is not a control — that score is advice the gate never enforces, and a
red ring would read as a failure the repo does not have. A map with neither record renders
no ring at all, so an older `_map.json` degrades to what it always showed.

**Scrollbars are 15px wide instead of 9px**, with a thumb you can hit without aiming.

**`translate` never worked on Windows.** The CLI installs as `claude.CMD`, and CreateProcess
only ever appends `.exe` to a bare program name — so every entry was reported as an
unavailable CLI against a CLI that was installed and on PATH. The name is now resolved
through the platform's own lookup before it is run, still as `argv[0]` and still with no
shell. The suite missed this because its tests mocked `subprocess.run` and nothing else, so
they passed on a machine with no `claude` at all; the CLI's presence is now mocked
explicitly, and the Romanian cache went from 211 to 224 of 226 requirements.

## plugin `v4.0.4` — 2026-09-04

**`cmd_export` is gone.** The `export` verb folded into `sync` in `v4.0.0` and the function has
been unreachable ever since — dead code kept alive by three tests calling it directly. Those tests
assert the JSON payload, which is live behaviour, so they moved to the surviving writer rather
than being deleted with it. `ARCH-MAP-007` stops describing a command that no longer exists.

## plugin `v4.0.3` — 2026-09-04

**RM029: a cached translation may not carry a field the requirement does not emit.** The gate
names the requirement, the locale and the field. A field the *translation* lacks is never
reported — a partial translation is a normal state.

This closes the class of defect that produced the previous release's fix rather than the instance:
two artifacts derived from one requirement, each correct against it, disagreeing with each other.
`translate` read the raw quote while the map emits none when that quote IS the obligation, and
nothing compared the two. The repository already checks one such pair — RM017, the viewer's baked
fixture against the live registry — and the translation cache simply never got the equivalent.
Tests of either side alone cannot see this shape; a comparison can.

**The intent reads like the rest of the document.** It sits below the obligation since `v4.0.2`,
where a lead-paragraph face read as a headline for the section under it, so it now uses the body
type — and its `code` spans render, which they never did: a backticked identifier in the intent
printed its own backticks.

**`scan` is gone from the corpus too, and `retire --delete` was wrong about where code lives.**
`ARCH-SCAN-005` and `REQ-SCAN-910` are deleted, with `cmd_scan` and its two test classes — the
verb went in `v4.0.0` and its code had been unreachable since. Dogfooding the deletion found the
bug: `_strip_member_tags` derived the code root from the requirements directory's parent, which is
only the same directory when `--code` is not used, so it built `plugin/plugin/scripts/...`,
stripped nothing, and said "0 tag(s) stripped" while the gate reported the dangling tags a moment
later. It takes the scan root now, and a file it cannot open is said out loud instead of skipped.

**TODO:** ranking a Romanian query rather than matching it literally. The model indexes the
English text, and the literal layer added in `v4.0.0` finds a query only when it appears verbatim
— "acoperire per criteriu" misses what "Acoperire de test per criteriu" hits.

## plugin `v4.0.2` — 2026-09-04

**A requirement document leads with what it obliges.** `Description` sits above `Why — Intent`
now: a requirement is read to find out what it binds, and the rationale supports that answer
rather than preceding it. The authored `.md` still keeps its quote at the top of the Description
section — this is the reading order, not the file's.

**The cached translation stopped showing a section English hides.** `translate` read
`_first_quote` while the map emits `_distinct_intent`, which is empty when the quote IS the
obligation — the atomic form of the eight `SYS-*` needs, where the story and the single clause are
the same sentence character for character. The Romanian document printed it twice. `translate` now
reads the same field the map does, the viewer will not render a section the engine hid whatever a
cache carries, and the eight stale entries are cleared. The other 217 requirements, whose quote
does say something the clauses do not, are unaffected in either language.

## plugin `v4.0.1` — 2026-09-04

**The Action's major alias tracks the plugin's major** ([ADR-0029](docs/adr/0029-action-alias-tracks-the-plugin-major.md)).
`check@v5` ships with plugin `4.x`. It was a third, independent version axis until now — which is
why `@v2` lived across 2.x through 3.4, and why `v4.0.0` shipped advertised as `@v3`. The
reasoning held (an alias that moves for reasons unrelated to its own interface forces a re-pin for
nothing) and the cost was a third number to hold, visible to the one person least equipped to
know the rule: the consumer copying a `uses:` line out of a README.

`check_versions.py` now asserts the two agree, so a mismatch is a failed build rather than
something a reader has to notice — with the falsifying case pinned by two tests
(`ARCH-SELFGATE-039` CASE-8). `@v1`, `@v2` and `@v3` stay where they point: a consumer pinned to
one keeps the engine that was current then.

## plugin `v4.0.0` — 2026-09-04

**Breaking: 25 commands become 17, and three of them are new.** The CLI had grown one verb per
artifact; it now has one verb per moment of work — author, build, read. Nothing this release
removes is unreachable: five verbs were aliases, debug prints or dry runs of another verb, and
six more were folded into the command that already ran beside them every single time.
`MAP_ENGINE_VERSION` `2026-09-04.8`. The published Action moves to **`@v3`** — its steps changed
shape, so a caller pinned to `@v2` will not silently pick this up.

**Three new commands, the author → code → retirement half of the loop** (`ARCH-CLARIFY-062`,
`ARCH-IMPLEMENT-063`, `ARCH-RETIRE-064`, 8 code-level children, 32 cases, 30 tests):

- **`clarify <ID>`** asks what a requirement has not answered: a hedge word with no threshold, a
  bare number with no unit, an "all/every" with no bound, a clause whose subject is "It", a clause
  with no case, an acceptance that never mentions a failure path. Blocking questions (no
  obligation at all, no labelled case) are separated from advice. Read-only, always exit 0, never
  a gate rule — the point is to resolve the ambiguity in the requirement instead of guessing it in
  code three weeks later.
- **`implement <ID>`** emits the brief a coding agent otherwise reconstructs by reading the repo:
  obligations, cases as authored, existing members, the still-open questions, the literal tag lines
  the new code must carry (one `implements:`, one `tested-by:`, one `verifies:` per labelled case),
  and — by the same TF-IDF the search uses — the two most similar requirements that already have
  code, with their files, which is the honest answer to "where does this kind of thing live here?".
  It writes no code: a deterministic tool can own the contract and the verdict, never the authorship.
- **`retire <ID>`** takes a requirement out of service, blast radius first: dependents, children,
  members, prose cross-references, the files where it was the only tagged requirement — and the
  dependencies it was the last consumer of, which is the dead-code question nothing else answered.
  It refuses while anything still depends on it unless `--force`, deprecates by default
  (reversible), and only `--delete` removes the block, the lock entries and the membership tags.
  Never a function body: deciding what code is now dead needs to understand the code.
  [ADR-0027](docs/adr/0027-retiring-a-requirement-supersedes-grow-only.md) supersedes ADR-0021's
  "the corpus grows only" and records the four rules that make the deletion safe.

**Three merges — one verb per moment, not per artifact:**

- **`gate` is the whole verdict.** It runs link sync + drift + test links, then requirement
  readability, then committed-map freshness. Those were `gate`, `lint --strict` and `map --check`:
  three commands that CI, the dev hook and the shipped consumer hook have run in that exact order,
  together, every time — and the published Action already defaulted both extras to on. `--no-lint`
  and `--no-map-check` opt out; the Action's `lint:` and `map-check:` inputs now switch them.
- **`sync` rebuilds everything derived**: the lock, `_map.*`, `docs/map.html`, an existing
  `_findings.md` (`--findings` creates it the first time), the presentation page's engine-owned
  regions, and — in this repository — the generated integration artifacts. `map`, `findings`,
  `site` and `gen-integration` are gone as verbs; there was no state of the world in which
  regenerating one of them and not the others was what the caller wanted.
- **`next` opens with the health score.** `health` is gone as a verb: `next --json` and
  `next --badge` emit exactly what `health --json`/`--badge` did, and `next --untagged` is the old
  `coverage` listing.

**Five verbs removed:** `check` (the deprecated `gate` alias, scheduled for removal here since
v3.0.0), `export` (`sync` writes `_map.json` anyway), `plan` (now `draft --plan`), `coverage` (now
`next --untagged`), `scan` (a debug print of the member table; `show` gives one requirement's
members, `gate --json` gives them all). `ARCH-SCAN-005` and its child are `deprecated`, not
deleted — they stay visible in the map with their history intact.

**`_map.md` no longer conflicts on every branch.** Its header carried a wall-clock timestamp, so
every regeneration rewrote one line that no content had changed: two branches that produced an
identical graph still collided there, and the resolution was always "regenerate", never "merge".
The header is content-derived now (`generated:` carries the date, `engine:` the engine version),
so two runs over the same corpus produce byte-identical files. `.gitattributes` additionally marks
every generated artifact `merge=ours`, so a merge never stops on one; the gate's freshness check
then tells you to run `sync`, which is the loud, self-correcting signal.

**The viewer, redesigned** (`ARCH-VIEWER-007`, new children `REQ-VIEWER-944`, `REQ-VIEWER-945`):

- **One paper surface, one accent.** The slab-serif display face and the four-brand palette
  (indigo + amber + magenta + coral) are gone. What is left reads like a printed manual: warm paper
  for the chrome, a lighter page for the document sheet, warm near-black ink — and in dark mode the
  same book at night, a browned ground under off-white ink rather than neutral greys. One deep
  ink-blue accent. Saturated colour now means something: requirement status, coverage and severity,
  nothing else. Token *names* are unchanged, so every `var(--...)` reference still resolves.
- **No webfont.** Type is the platform UI stack with a mono for ids. The Google Fonts `@import` is
  gone — the self-contained `_map.html` is opened by double-click from `file://`, where that
  request silently fell back mid-paint.
- **The document reads as a document.** ALL-CAPS tracked eyebrows are sentence-case headings, the
  intent quote is the lead paragraph, clauses wrap at 72ch, and the raw YAML frontmatter block is
  one quiet metadata line.
- **`[[REQ-CHECK-828]]` is a link.** A cross-reference in requirement prose renders as the bare id
  and opens that requirement (click or keyboard) when the map holds it; a dangling one is struck
  through rather than hidden. Escaping still runs first.
- **The registry tally is the filter it describes.** Clicking `draft` in the rail scopes the
  outline to drafts; `orphan` scopes to the gate's own error condition. The applied scope is a chip
  you can clear, and it is part of the first render.
- **Bugs fixed.** The spec header printed `owner: Alex` on every requirement in every repo — a
  field the engine has never exported. Problems' empty state read "Nothing here — no all signals
  open."; Findings' legend named a section renamed in v3.2.0, and its rows collapsed into the
  76px severity column, one word per line. A collapsed parent said "1 clauses". Search results
  stayed open over the document after blur. The nav error badge was white-on-red at ~2.8:1 in
  dark. `Spec`'s rail drew an empty "CORE · bus" heading. The map legend's bus swatch had lost
  its colour.

**The CLI documents itself, in the reader's language** (`REQ-CMDREGISTRY-963`,
`REQ-VIEWER-964`). `_map.json` now carries a `commands` list generated from the command registry,
and the viewer renders it as a reference grouped by the moment of work — authoring, building,
reading — with each verb's invocation, summary and flags. A verb that is removed disappears from
the reference on the next `sync`, which is the only way a command list stays true. Summaries are
translated; flag names never are, because `--accept-drift` is a literal you type.

**The Romanian corpus.** Every requirement's title, intent, Description and Cases are cached in
`requirements/_i18n/ro.json` and served by the viewer's EN/RO toggle behind the
"machine-translated, unreviewed" badge, with the `.md` file remaining the artifact of record. A
translated Description is now rendered as the section it is — a quote and a bullet list — instead
of in the monospace block the acceptance criteria use.

**The structural-fidelity check no longer rejects correct Romanian.** It counted the English
words "given", "when" and "then" wherever they appeared, so a faithful rendering of "When no
requirement scores above the floor…" looked like a dropped identifier. A Gherkin keyword is an
identifier where it opens an *indented* line — the shape of a step inside a Cases block. Measured
over this corpus: all 3091 real step keywords are indented and inside the acceptance block, all 7
line-opening prose occurrences are flush left and outside it, no exception either way, plus 79
mid-sentence occurrences. The narrower rule took the corpus's rejection count from 19 to 0.

**`findings` no longer reports the tool's own authoring hint** (`REQ-FINDINGS-853` CASE-4).
`draft` scaffolds a prose capability with the source file's headings listed under "authoring hint,
not the contract" — inside `## Verify intent`, as bullets, so every heading was collected as an
open question: a 21-draft repository reported 103 findings, 82 of them the hint. The scaffold now
writes that list into `## Context`, and a new `_verify_bullets` cut keeps files drafted before the
fix honest. All seven verify-intent readers go through it, so the viewer, the CLI and the gate
summary cannot report different counts.

Corpus: 221 requirements (9 SYS, 65 ARCH, 147 REQ), 2 deprecated.

## plugin `v3.5.0` — superseded, never released

**The map viewer is redesigned, and a `[[ID]]` cross-reference is now navigation** (`ARCH-VIEWER-007`, new child `REQ-VIEWER-944`). Engine untouched — `MAP_ENGINE_VERSION` stays `2026-09-04.5`; the change ships as a rebuilt `_map_viewer.html`.

- **One paper surface, one accent.** The slab-serif display face and the four-brand palette (indigo + amber + magenta + coral) are gone. What is left reads like a printed manual: warm paper for the chrome, a lighter page for the document sheet, warm near-black ink — and in dark mode the same book at night, a browned ground under off-white ink rather than neutral greys. One deep ink-blue accent. Saturated colour now means something: requirement status, coverage and severity, nothing else. Token *names* are unchanged, so every `var(--...)` reference still resolves.
- **No webfont.** Type is the platform UI stack (SF Pro / Segoe UI Variable) with a mono for ids. The Google Fonts `@import` is gone — the self-contained `_map.html` is opened by double-click from `file://`, where that request silently fell back mid-paint.
- **The document reads as a document.** ALL-CAPS tracked eyebrows are sentence-case headings, the intent quote is the lead paragraph, clauses wrap at 72ch, and the raw YAML frontmatter block is one quiet metadata line.
- **`[[REQ-CHECK-828]]` is a link.** A cross-reference in requirement prose renders as the bare id and opens that requirement (click or keyboard) when the map holds it; a dangling one is struck through rather than hidden. Escaping still runs first — the XSS regression checks are unchanged and a fourth case set now covers the transform.
- **Bugs fixed.** The spec header printed `owner: Alex` on every requirement in every repo — a field the engine has never exported. Problems' empty state read "Nothing here — no all signals open."; it now states what is true. Findings' legend named `## WHAT — Verify intent`, a section renamed in v3.2.0. A collapsed parent said "1 clauses". The search results stayed open over the document after blur (Escape clears them). The nav error badge was white-on-red at ~2.8:1 in dark. `Spec`'s rail drew an empty "CORE · bus" heading. The map legend's bus swatch had lost its colour.
- **The registry tally is now the filter it describes** (`REQ-VIEWER-945`). Clicking `draft` in the rail scopes the outline to drafts and opens it; `orphan` scopes to the gate's own error condition (enforced, no `implements:` member), which is a computed state rather than a status. The applied scope is drawn as an active chip you can clear, and it is part of the first render, not applied by an effect afterwards.
- **`findings` no longer reports the tool's own authoring hint** (`REQ-FINDINGS-853` CASE-4, `MAP_ENGINE_VERSION` `2026-09-04.6`). `draft` scaffolds a prose capability with the source file's headings listed under "authoring hint, not the contract" — inside `## Verify intent`, as bullets, so every heading was collected as an open question: a 21-draft repository reported 103 findings, 82 of them the hint. The scaffold now writes that list into `## Context`, and the new `_verify_bullets` cut keeps files drafted before the fix honest. All seven verify-intent readers go through it, so the viewer, the CLI and the gate summary cannot report different counts.
- **A findings row is readable again.** `.finding-row` carries no severity cell, and under `.prob-row`'s `76px 1fr auto` template its whole body landed in the 76px column, one word per line. Both selectors are a single class and `.prob-row` is declared later, so it won; the override is now `.prob-row.finding-row`.
- Quality floor: visible `:focus-visible` rings, `prefers-reduced-motion` honoured, thin scrollbars, and the narrow layout keeps the problem rows readable. Corpus: 210 requirements.

## plugin `v3.4.0` — 2026-09-04

**New command `design`: an advisory review of the repo's code, in any program-logic language, against the four OOP pillars and a set of house standards** (`ARCH-DESIGN-061`, satisfies `SYS-READ-103`). Python is read through `ast`; JS/TS, C/C++, Java, C#, Go, Rust, Kotlin, Swift, Scala, Dart and PHP through brace-matching heuristics over the source with comments and strings masked out, feeding the same shape checks. It names shapes worth a look — module state written from functions, long parameter lists and data clumps (encapsulation); long or deeply nested functions and prefix families of top-level functions (abstraction); unrelated classes sharing method names or byte-identical method bodies (inheritance); `isinstance` chains and equality switches on one value (polymorphism). A fifth block, standards, reports per file: over `DESIGN_FILE_MAX_LINES` (500), lines wider than `DESIGN_LINE_MAX` (100), public definitions without a docstring, more than `DESIGN_FILE_MAX_FUNCS` (30) top-level definitions — one finding per file per rule. Grouped by block with one advice sentence each, `--json` for tools, exit 0 always, never a gate rule. Every threshold (`DESIGN_*`) is a `CONFIG_KEYS` entry. The same analysis folds into a **design score** — the percentage of non-test Python files with no candidate — that rides in `_map.json` as `design`, in `_map.md`'s header and in `health` (`design_score`), absent when a repo has no Python. Run on this repo it reports the engine's own long functions honestly — the list is advice, not a defect count. `MAP_ENGINE_VERSION` `2026-09-04.5`.

## plugin `v3.3.0` — 2026-09-04

**The gate is a rule registry, the engine has a config file, and one walk serves every scan** ([ADR-0026](docs/adr/0026-gate-rule-registry-and-config-file.md)). `cmd_check` was four hundred lines of inline checks; every other command re-derived the same facts its own way, which is how `gate`, `health`, `next` and `confirm` came to disagree twice before (ADR-0015, v3.1.0).

- **`GATE_RULES`** (`ARCH-RULES-059`): each check is a function registered with `@gate_rule("RMnnn", severity, strict=...)`, run over one `GateContext`. Every printed line now carries its code — `WARN  RM018 ARCH-X: DRIFT — ...` — the message text is unchanged, `gate --json` gains a `findings` list of `{rule, severity, rid, msg}` records, and a requirement can write `gate_exempt: [RM013]` to switch one rule off for itself, the way `lint_exempt:` works. `health`'s link-sync count reads RM001/RM006 from the registry. Codes are permanent: a retired rule's number is never reused.
- **`Requirement` and `Finding`** are dict subclasses (`r["meta"]` keeps working) carrying the derived facts every rule used to recompute (`status`, `level`, `impl_exempt`, `exempt_from(code)`) — the encapsulation half of the OOP request; no class hierarchy, the engine is a pipeline.
- **`requirements/_config.json`** (`ARCH-CONFIG-060`): overrides the constants named in `CONFIG_KEYS` (`LINT_AC_MAX`, `SIMILAR_THRESHOLD`, `ORPHAN_CODE_MIN_LOC`, `LINT_FANOUT_BANDS`, ...) and `extra_code_exts`; read fail-open, an unknown or mistyped key is reported on stderr and skipped.
- **One walk, cached.** `scan_all` is the only scanner and `--cache` now caches all three extractions (members, `verifies:` coverage, test levels); `scan_members` is a view of it. Measured before: `gate --cache` took 1.9 s against 1.5 s without, because the cached members walk was followed by two uncached coverage walks.
- **`_is_source_repo`**: the viewer-fixture rule (RM017) runs only inside this repository; a consumer whose parent directory happened to hold an `app/src/lib/data.js` used to get a false warning.
- **Verified bugs fixed.** `dupes | head` on Windows exited 120 with an "Exception ignored" line after the v2.9 fix — `_pipe_closed` now ends with `os._exit(0)`. `_map.md`'s Req→Code block passed 83,000 characters on the 197-requirement corpus (GitHub renders 50,000) — it draws the system/architecture tiers only. `next`'s header said `11 draft(s)` above a `Drafts to review (572)` bucket — it says `unreviewed` (draft + baseline) and its category count includes the advisory buckets. The untagged bucket no longer lists decision records, issue/PR templates, `SECURITY.md` or dependabot config. `dupes` skips parent-child pairs (a child restates its parent by construction) and honours `--top N`. `lint` names the module file a block lives in instead of `requirements/<id>.md`.
- Corpus: 202 requirements (9 SYS, 64 ARCH, 129 REQ). `MAP_ENGINE_VERSION` `2026-09-03.20`.

## plugin `v3.2.0` — 2026-09-03

**The corpus is folded from 644 to 197 requirements on three levels, in a lean form** ([ADR-0025](docs/adr/0025-three-levels-restored-corpus-folded-to-two-hundred.md), superseding ADR-0024). The 573 one-sentence atomic leaves of the morning's decomposition were regrouped, one code-level requirement per behaviour group of the parent's Description: 9 `SYS-*` needs (`level: system`), 62 `ARCH-*` capabilities (`level: architecture` again), 126 `REQ-*` behaviour groups (`level: code`, 3-7 labelled cases each). Every requirement is `confirmed` with an `implements:` member; 844 members, 0 gate errors.

- An `ARCH-*` Description is now its intent quote plus one obligation sentence per child ending in `[[REQ-…]]`; the detail lives only in the child. The parent's own `## Cases` are unchanged, so every existing `# verifies: ARCH-…#CASE-N` tag still resolves.
- The lean form: frontmatter without comments or empty keys, `## Description` + `## Cases` + optional `## Context`; no `## Verify intent`, `## Links` or `## Members in code (auto)` on a confirmed requirement. `reqmap new`'s scaffold and `lint --decompose`'s scaffold drop the two auto sections nothing ever filled; the audience rule in `SKILL.md` and the scaffold is now "a developer new to the project", not "a first-year student".
- `gate`'s legacy-schema warning keys on the old `## Input`/`## Output` triad only. It used to fire on any sectioned requirement without a `## Verify intent` section, which would have named every requirement in a lean corpus in one warning.
- `LINT_FANOUT_BANDS["system"]` returns to `(None, 10)` (the test is `test_system_ceiling_is_ten` again); `architecture` stays `(None, 30)`.
- Per-case coverage is now real: 624 `# verifies:` tags in `test_reqmap.py` alone, placed by reading each test; 132 cases across 76 requirements have no test yet and the gate names them, one aggregated warning per requirement. `ARCH-VLEVEL-037` warns that it is verified at `@unit` but not `@integration` — the first consequence of the level rungs applying to a populated `architecture` level.
- The viewer's baked demo fixture (`app/src/lib/data.js`) carries the 13 lifted parents' new contracts.
- `MAP_ENGINE_VERSION` `2026-09-03.18`.

## plugin `v3.1.1` — 2026-09-03

**The `architecture` level is promoted into `system`** ([ADR-0024](docs/adr/0024-architecture-level-promoted-into-system.md), superseding [ADR-0023](docs/adr/0023-fan-out-per-level-ceilings-no-floor.md)'s `system` ceiling). A `/senate` audit rejected an earlier, literal 2-level proposal that froze the `system` tier at 9 requirements: flattening 573 `level: code` requirements onto 9 parents averages ~64 children each (one node hits 107), 2–3.5x over any proposed ceiling. The revised design that survived promotes the 62 `level: architecture` requirements into `level: system` instead of deleting them — the middle rung's grouping is unchanged, only its label moves, so no `satisfies:` edge is repointed and no confirmed contract's fan-out changes.

- `fan-out`'s `system` ceiling moves from 10 to 50 (`LINT_FANOUT_BANDS` in `plugin/scripts/reqmap.py`); the `architecture` ceiling (30) is unchanged for a consumer repo that still uses a real 3-tier split.
- This corpus now has 71 `level: system` requirements (9 original `layer: need` stakeholder requirements, fan-out 5–10, plus the 62 promoted `layer: bus`/`feature` requirements, fan-out up to 32), 0 at `level: architecture`, 573 at `level: code`. `level: system` now spans two populations distinguished by `layer:`, not `level:` — see CLAUDE.md's "Ids carry their level" section.
- **`ARCH-FANOUT-052`'s own Contract stated the old ceiling relationship as a binding clause** ("a `system` parent's ceiling is ten … lower than an architecture requirement's"), and a coupled test (`test_system_ceiling_is_lower_than_architecture`) asserted it. Both are corrected to the new ceiling; the test is renamed `test_system_ceiling_is_fifty`. Caught by a Consilium Dialectic deliberation before any file changed, not discovered by a broken CI run.
- `_mermaid_hierarchy`'s diagram label logic decided "show this node's `<N> code` fan-out annotation" by testing `level: architecture` literally — after the promotion every drawn node reads `level: system`, so the 62 promoted nodes would have silently lost their annotation. It now keys on "has counted code-level children" instead, which produces identical output on a corpus that still uses a real 3-tier split and correct output on this one. New test: `test_a_promoted_system_node_still_shows_its_code_count`.
- `VALID_LEVEL` and `LINT_FANOUT_BANDS["architecture"]` are unchanged — `architecture` stays a valid, generic level for any repo (including this one, later) that wants a real 3-tier split; this corpus having zero members there today is a fact of its current shape, not something the engine forgot how to support.

## plugin `v3.1.0` — 2026-09-03

**`next` and `lint` could report a different set of oversize requirements for the same corpus, and `lint --decompose` only ever acted on `statement-size`.** `next`'s Granularity bucket iterated every status with no `lint_exempt` check and its own hardcoded 5-AC threshold; `lint`'s `ac-count-high` check used `LINT_AC_MAX` (7), scoped to non-draft statuses, and honored `lint_exempt: [ac-count-high]`. Two commands, two answers to the same question.

**Corrections from the nine-senator branch audit** (`runs/senate/2026-09-03_155528-senate-reqmap-pr208-branch-audit.json`, MODIFY, two rounds). The audit found no defect in the engineering — gate 0 errors, `lint --strict` 0 errors, `map --check` fresh, suite green — and four defects in the *record*, three of them in text this release would have shipped as normative:

- **`health`'s reviewed-only denominator counted the wrong population.** `reviewed_total` was `total - drafts`, but `healthy`'s first axis is `status == confirmed`, so a `baseline`/`in-progress`/`implemented`/`deprecated` requirement entered the denominator and could never enter the numerator — it depressed the score with nothing rotting, and a `deprecated` requirement capped it permanently. The denominator is now `confirmed`. Invisible in this repo (all 72 non-drafts are `confirmed`), so `ARCH-REVIEWEDSCORE-109` gains CASE-5 and a test covering all four statuses.
- **A withdrawn measurement is out of a binding contract.** `ARCH-FANOUT-052`'s Description carried "a blind review of all nine findings the old floor produced confirmed none of them as real" — an unfalsifiable historical assertion inside a hash-locked normative span. The number does not reproduce (the floor produced 4, then 6, then 7; nine was a floor-plus-ceiling total) and the one flag it called plausibly real, `ARCH-CHECK-006`, is a *ceiling* finding. The clause now states the behaviour only; the history moved to ADR-0023, and the claim is retracted in ADR-0022 and here.
- **Two leaves contradicted their parent.** `REQ-FANOUT-391` and `-392` still asserted the floor this release removed — one required a 4-child parent to be flagged — so a reader implementing from the leaves would have built a floor the parent forbids. Both restated against the shipped behaviour, and `REQ-FANOUT-393` is restored to cover the still-binding warn-only clause it was deleted from under.
- **Four published figures corrected**: `six of 70 non-draft` → 72 (ADR-0022 said 72 correctly two paragraphs earlier); `551 leaves with an observable` → 546 of 570 at `b0ce92b`; `every one of the 575 leaves is a draft` → 574, since `REQ-PROMOTE-567` was confirmed five commits before that sentence was written; the health snapshots now name the commit they were measured at. `CLAUDE.md` no longer documents Granularity at the removed 5-criterion threshold.

- **New [ADR-0023](docs/adr/0023-fan-out-per-level-ceilings-no-floor.md)**, superseding ADR-0019's fan-out band Decision and its "those 7 are real" Consequence — the reversal previously lived only in a code comment. It also disposes explicitly of the two conditions run `2026-09-02_201621` left open, and notes that ADR-0019's Evidence glob matches no file.
- **New shared `_oversize(rid, r)` predicate**, beside `_impl_exempt` (the `ARCH-TRACE-020` precedent this mirrors): fires on `_count_ac(body) > LINT_AC_MAX`, scoped to `LINT_STATUSES` (drafts excluded — they are TODO stubs, not yet-scoped contracts), honoring `lint_exempt: [ac-count-high]` via the same `_as_list` handling `lint_requirement` already used. Both `cmd_next`'s Granularity bucket and `lint_requirement`'s `ac-count-high` check now call it — the two commands cannot disagree any more. `AC_SPLIT_THRESHOLD` (5) is gone; `LINT_AC_MAX` (7, unchanged) is the one number. No consumer's `lint --strict` gate moves, on purpose — the threshold consumers are already gated on never changed.
- **`lint --decompose` still covers `statement-size` only.** An `ac-count-high` triage-stub path was written for this release and removed before it shipped: `_oversize` fires on 0 of this corpus's 72 lintable requirements (all six over `LINT_AC_MAX` carry `lint_exempt: [ac-count-high]`), so the path reached nobody, and ADR-0022 — adopted in the same release — forbids shipping on a signal with no published fire rate and no human-confirmation sample. `ac-count-high`'s post-exempt rate is 0.0%, which is the profile ADR-0022 used to *reject* its sibling proposal. A test asserts `_decompose_ac_count_high` and `AC_COUNT_TRIAGE_TEMPLATE` do not come back.
- **`ARCH-DECOMPOSE-050` and `ARCH-NEXT-013` narrowed to match reality.** `ARCH-DECOMPOSE-050` now states the measured reachability: `statement-size` has never fired in this corpus (`LINT_STATEMENT_WORDS` 150 vs. a 61-word longest clause), and `ac-count-high` is reachable in principle but 0.0% post-exempt today (6 of the 72 non-draft requirements exceed `LINT_AC_MAX`, all 6 deliberately exempt). `ARCH-NEXT-013` gained the Granularity/Redundancy buckets its own contract had omitted since `ADR-0020` shipped them.
- **Expected, not a bug: Granularity goes from 38 items to 0 in this corpus.** All 6 over-threshold requirements are exempt, and the 32 requirements in the old 5–7-AC band no longer qualify under the unified threshold.
- Five new tests, plus three pre-existing threshold-coupled `next` tests (`test_next_granularity_counts_labeled_acs`, `test_granularity_at_threshold_warns`, `test_granularity_truncates_to_top_n`) updated for the new boundary. The baked `app/src/lib/data.js` viewer fixture re-synced for `ARCH-NEXT-013`'s new clauses.
**`health`'s score could not tell "not reviewed yet" from "rotting".** The first axis of green is status `confirmed`, so a `draft` can never be green, and `total` counts every requirement — each draft therefore caps the headline score by construction. A repo that runs `init` over legacy code reads near-zero health forever while nothing in it is actually decaying. This repo read `10/100` at `1eea8f1` while all 71 of its confirmed requirements were green on every axis.

- **New reviewed-only score**, additive: the percentage of green requirements among those whose status is not `draft`. `health` prints it as a `reviewed only:` line and `--json` gains `reviewed_score` + `reviewed_total`. This repo read `10/100` overall and `100/100` across the 71 confirmed at `1eea8f1`; the corpus only grows, so run `health` for today's figure.
- **`score` itself is unchanged**, deliberately: `ARCH-HEALTH-017` CASE-2 binds an all-draft corpus to zero, and every consumer badge already reads that key. Redefining the denominator would have moved every badge silently.
- **Absent, not zero**, following the `untagged` precedent (`ARCH-COVERAGE-029`): the key is omitted when nothing has been reviewed (zero of zero is not zero per cent) *and* when there are no drafts (it would restate `score` under a second name). An existing `--json` consumer's schema is unchanged.
- `ARCH-HEALTH-017` gained CASE-8 and CASE-9; four new tests.
- **Grow-only asymmetry recorded as [ADR-0021](docs/adr/0021-corpus-grows-only-by-design.md).** Five paths create a requirement file; none removes one. The single `os.remove` lives in `_wipe` (`init --wipe`), which resets to zero rather than pruning. The decision is to keep that asymmetry — growth writes a reversible draft, shrink deletes a file and rewrites `satisfies:`/`depends_on:` edges across a possible drift boundary — pinned by a `NoShrinkVerb` test that fails when a second delete path appears. The record also corrects two figures the deliberation got wrong: dropping the `ac-count-low` atomic exemption fires on 14/70 lintable (20.0%), not 621/691 (90%), because `lint` never examines drafts; and the 621 detailed-design leaves do *not* cost nothing — they are why the headline score reads 10.
- **`intent` no longer duplicates the Contract.** In the atomic form the `>` quote IS the single obligation, so `_build_map_data` emitted it as both `intent` and `contract` and every surface printed one sentence twice — the viewer drew a `Why — Intent` blockquote directly above an identical `Description` bullet, and `show` printed the line under the title and again under `Contract:`. Measured: **588 of 646 nodes, 91% of the corpus**. New shared `_distinct_intent` returns `""` when the quote and the joined Contract are the same text (whitespace-normalised), read by both `_build_map_data` and `cmd_show`; the viewer now omits the block rather than drawing an empty one. Sectioned requirements, whose quote is real rationale, are untouched — 58 keep theirs. `ARCH-MAP-007` gained CASE-4 and CASE-5.
- **Authoring rule: split by failure mode, never by sentence.** `SKILL.md` and `SKILL.universal.md` now state that a clause earns its own requirement only when it names a behavior that can fail on its own, and name the three shapes that never do — an element of an enumeration ("a Rust `#[test]` counts" is one arm of *the engine recognises a test function*), an attribute of a behavior ("warn-only and never changes the exit code"), and a rationale that restates a sibling's obligation. The test is mechanical: try to write the `Then`; if the observable only repeats the clause, the clause is not a capability.
- **[ADR-0022](docs/adr/0022-no-minimum-requirement-size-check.md) — no minimum-size lint check, and a standing launch discipline for every future one.** A nine-senator audit (2 rounds, GO 3 · MODIFY 3 · STOP 3, three senators reversing to STOP on the evidence) rejected a word-count floor: measured over the 72 requirements `lint` actually visits, it fires on **1 — 1.4% — identically at N = 8, 10, 12, 15 and 20**, below ADR-0016's floor at every threshold, and its single flag is a correct 8-word contract (day-one precision 0/1). "Contract" also has two live senses on the atomic form — 140 findings under one reading, **zero** under the one `binding_hash` uses. The standing rule adopted instead: **no lint check ships without publishing both a fire rate and a human-confirmation sample of its own findings.** Verified across the whole lint surface — every check carrying an exemption launched without a sample (`ac-count-high` 6, `file-spread` 4, `over-scoped` 1, `ac-count-low` 1); `fan-out`, the one that published both halves, carries none.
- **`fan-out` gets per-level ceilings and loses its floor.** One band for the whole hierarchy was wrong in both directions: an `architecture` requirement groups detailed design, where a dozen children is ordinary, while a `system` need groups architecture, where ten is already a lot. Ceilings are now **30** for `architecture` and **10** for `system`; a parent declaring no `level:` keeps the old uniform 5–20 band, so a repo that never adopts the level axis sees exactly what it saw before (ADR-0019's doubly-opt-in rule). The **floor is dropped, not retuned** — measured at `b0ce92b` the old uniform band produced **10** findings, **7** of them below the floor, and several of those had appeared *because* commits `e254a34` and `72213fc` correctly folded away leaves that should not have existed. A check that gets louder as the corpus gets better is measuring the wrong thing; the distribution (3:1, 4:6, 5:5, 6:8, 7:5, 8:9) has no natural floor to find, while the ceiling has a real break at 19 → 22 → 23 → 32. Findings go **10 → 1**, the survivor being `ARCH-CHECK-006` at 32. ADR-0019 pre-committed this response: "the band is wrong for this shape of corpus and should be widened or dropped — not lived with." Recorded as **ADR-0023**, which supersedes ADR-0019's fan-out band and withdraws its claim that the band's seven findings were confirmed real.
- **[ADR-0022](docs/adr/0022-no-minimum-requirement-size-check.md) gains the procedure for discharging its own confirmation half**, applied for the first time on the change above: an independent reviewer decides (AI is allowed — independence and executed evidence are what mattered, not species), every verdict cites executed output, "false positive" is a costless answer, a person ratifies the batch, and the refusal rate is recorded so a rubber stamp is detectable. The reviewer's most useful output was two corrections to the proposal — a comment carrying a false measurement, and an unreachable floor — both fixed before shipping.
- **Two new atomic-form checks close a blind spot every existing signal shared: `_count_ac` counts the one `Scenario` regardless of how many facts an atomic story's `>` quote bundles into it, and `ac-count-low` explicitly exempts the atomic form, so a story listing 3 facts with a Scenario proving 1 passed every check that existed before this — the same shape as `REQ-FANOUT-391`/`-392` (a leaf asserting behaviour its parent forbade, unnoticed). `atomic-bullet-then-mismatch` warns when a story's `- ` bullet count does not equal its Scenario's `Then`-line count; `atomic-story-overlong` warns past `LINT_ATOMIC_STORY_BULLETS_MAX` (3) bullets — a story may enumerate up to 3 facts, not just 1. Both are `warn`, promoted to error under `--strict` via `STRICT_PROMOTE`, the same mechanism `ac-count-high`/`over-scoped` already use — not unconditional error, since `missing-section` is the only unconditional-error check across all 17 severity assignments in `lint_requirement` and every other structural/count check in the file, including these two's closest relatives, is `warn`-based.** Fires on **0** of the corpus's atomic-form requirements today — no existing story lists more than one fact — so [ADR-0022](docs/adr/0022-no-minimum-requirement-size-check.md)'s launch discipline is satisfied only on the fire-rate half; there is no live finding to sample against. Recorded as an explicit exception, not a silent one: the check is deterministic and structural (a bullet count either equals the `Then` count or it does not), the same class as `missing-section` rather than a heuristic threshold like the rejected minimum-size proposal, and it ships `warn`-first so a plain `lint` run stays exactly as quiet as before. `ARCH-LINTCHECKS-025` gains a new "Atomic-form parity checks" bullet group, CASE-11/CASE-12, and two new leaf `REQ-LINTCHECKS-476`/`-477`.
- `MAP_ENGINE_VERSION` → `2026-09-03.15`. 733 tests.

## plugin `v3.0.1` — 2026-09-03

**The architecture poster describes the `v3.0.0` corpus again.** `docs/full_architecture.html` still said "36 specs", `check@v1`, a `layer:` enum without `aggregate`, `satisfies: [ NEED-... ]` and `WHY / WHAT / WHERE / HOW`. Every one of those changed in a requirement the poster was not tagged with, so the deterministic drift check stayed silent and only the advisory doc-sync pass caught them. Regenerated from the maintained `make_full_architecture.py`; its `generated-from:` lineage now also names `ARCH-DESCRIPTION-057`, `ARCH-LEVEL-051` and `ARCH-TRACE-020`, so the next rename of a section, level or layer flags the poster without anyone reading it. Engine unchanged.

## plugin `v3.0.0` — 2026-09-03

**How a requirement is written changed shape.** Three specification levels, one `## Description` section in place of a `> WHY:` quote plus `## WHAT — Contract`, `## Cases`/`CASE-N` in place of `## HOW — Acceptance`/`AC-N`, many requirements per file, and the first advisory that points at covering the code with *fewer* requirements rather than more.

**Nothing in an existing corpus has to change.** Every old section name and both criterion-label spellings parse unchanged, `level:`/`satisfies:` are optional, and a repo that adopts none of this behaves exactly as it did on `v2.30.0`. The major is about the shape this tool now asks for in new work, not about anything it stopped accepting.

**`check` survives the major it was scheduled to die in.** The deprecated alias for `gate` arrived in `v2.0.0` (2026-06-15) saying "removed in the next major version", in five places. `v3.0.0` is that major and the alias is still here: nothing else in this release breaks a caller, and removing a command consumer hooks may still invoke would have been the only thing that did. All five references now name **`v4.0.0`** instead — "the next major" was a moving target by construction, and a promise that slips once slips silently.

This release folds what was developed as `v2.32.0`–`v2.34.0`; none of those three were tagged. `v2.31.0` was released and keeps its own entry below.

### Covering the code with fewer requirements

**The tool gets an opinion about covering the code with FEWER requirements.** `next` has advised in one direction for a year — *Granularity*, "this requirement does too much". Nothing ever said the opposite.

- **New `Redundancy` bucket in `next`, and a one-line count from `sync`.** Requirements whose `## Description` clauses are identical once case and whitespace are normalised, grouped, with how many could be folded away. Exact match, no threshold — a group is a duplicate by construction, never a judgement call. It reports; it never merges, because which id survives and what the merged contract says are decisions with judgement in them. `ARCH-REDUNDANCY-058`.
- **It fires 6 times on this repo, and those 6 are left standing.** All real. One example, whole: "`show` prints the verification level beside a member whose `tested-by:` tag carries one" — authored in both `ARCH-SHOW-015` and `ARCH-VLEVEL-037`, so decomposition minted `REQ-SHOW-683` and `REQ-VLEVEL-819` for one obligation. Shipping a check and silencing its output in the same commit would make it decorative.
- **It ships below ADR-0016's 5% fire-rate floor on purpose.** 6 groups, 12 requirements, 1.7% of the corpus. [ADR-0020](docs/adr/0020-redundancy-signal-below-the-fire-rate-bar.md) records why rather than quietly widening the check until it cleared a number — which is exactly how [ADR-0012](docs/adr/0012-internal-consistency-lint-rejected.md)'s 78.6% false-positive rate happened. The floor rejects checks that are noisy or dead; this one has zero false positives by construction. **Four other candidate signals were measured and NOT shipped**: identical member sets (0 findings), subset member sets (1), and cosine ≥ 0.50/0.70 — the last two are `dupes`, which already exists and is unchanged.
- **In `sync` and `next`, deliberately not in `gate`.** The pre-commit hook runs `gate` on every commit, and corpus shape is not a commit-time concern. `sync` is the moment the corpus was just rewritten — which is when a new duplicate appears.
- **Draft placeholders are excluded**, or every scaffolded `TODO:` line would match every other and bury the six real findings under hundreds.
- **Bug: `next` told you to open a file that does not exist.** It rebuilt `requirements/<id>.md` from the id, which stopped being true in `v2.32.0` when one file began holding many requirements — `REQ-COVERAGE-327` lives inside `ARCH-COVERAGE-029.md`. All three buckets now name the real path from the requirement record. `ARCH-MODULEFILE-056`.
- **Viewer:** the Spec panel's Description eyebrow no longer claims `normative`. The section holds the intent quote *and* the binding clauses since `v2.33.0`, so the label was true of only part of what sits under it.
- `MAP_ENGINE_VERSION` → `2026-09-03.2`. 683 tests.

### One `## Description` section, and `## Cases`

**`## Description` and `## Cases` replace `WHY` + `## WHAT — Contract` and `## HOW — Acceptance`.** Every old spelling still parses, forever.

- **`## Description` merges the intent quote and the Contract section.** A reader met the same capability twice — once as rationale under a `> WHY:` quote, once as obligation under `## WHAT — Contract (normative)` — beneath two headings that both said WHAT. The quote now opens `## Description` and the binding clauses follow it. `## Verify intent` and `## Notes` simply dropped a `WHAT —` prefix that no longer named a section. `ARCH-DESCRIPTION-057`.
- **The intent quote sits inside the normative section but outside the drift hash.** `binding_hash` now skips `>` lines within a normative span, so improving an explanation never reports DRIFT on a confirmed contract, and `_contract_clauses` never treated a blockquote as a clause, so the linter never sees rationale either. The atomic form draws the same line by keeping `rationale:` in the frontmatter. **No requirement carried a blockquote inside a normative section when this was added, so no existing hash changed** — the loosening is free.
- **`## Cases` and `CASE-N` replace `## HOW — Acceptance (= tests)` and `AC-N`.** A criterion is a test case; the old name described a sign-off step rather than the cases a reader can run. 117 `# verifies:` tags in this repo were re-pointed.
- **Both spellings are honoured, and that is not optional.** `AC-N` is an **identifier a `# verifies: <ID>#AC-N` tag points at**, so dropping it would break every consumer tag already written. `CONTRACT_LABELS`/`ACCEPTANCE_LABELS` are the SSOT (current name first) and `_has_any`/`_from_any` are the only way a call site asks for either section — 34 lookups now route through them, instead of each hard-coding a heading. Most `test_reqmap.py` fixtures are deliberately left in the legacy form: that is the back-compat suite, and rewriting it would have deleted the only coverage of the older shape.
- **The legacy `desc` field no longer swallows the new section.** `_build_map_data` emitted `desc: _section(body, "description")` for the old Input/Description/Output triad; with `## Description` now the contract, it would have re-emitted every clause into a second viewer field. It is gated on the triad actually being present.
- **Two stale things the migration surfaced.** `draft`'s scaffold still told authors to keep sentences "under 25 words" — a limit retired with `long-sentence` in `v2.32.0`, so it taught a rule the linter no longer has; it now names the live per-clause limits (3 sentences, 150 words). And `ARCH-MODULEFILE-056` shipped `confirmed` in `v2.32.0` with no test behind it, caught by this repo's own test-link gate.
- **Viewer:** the Spec and Map panels label the sections `Description` and `Cases` (Romanian `Descriere` / `Cazuri`); Problems' per-criterion fix names `#CASE-N`. Vendored viewer rebuilt; the baked `data.js` fixture re-synced.
- `MAP_ENGINE_VERSION` → `2026-09-03.1`. 675 tests.

### The V-model's left arm

**The V-model's left arm, adopted.** 52 requirement files become 689 requirements on three specification levels, held in 68 files. Every engine change is opt-in: a corpus that sets no `level:` behaves exactly as it did in `v2.31.0`.

- **New `level:` frontmatter — `system` | `architecture` | `code`.** It is a **second axis, orthogonal to `layer:`**, and the two must not be merged: `layer` is graph position (fan-in), `level` is abstraction. Aliasing `architecture` onto `aggregate` would have keyed the change into `IMPL_EXEMPT_LAYERS` and silently exempted all 59 architecture requirements from the confirmed-must-have-code gate. The hierarchy edge is `satisfies:`; `depends_on:` stays composition. `ARCH-LEVEL-051`.
- **New V-model rungs joining the two arms.** `LEVEL_TEST_PAIR` maps each level to the verification depth that closes it — `code`→`@unit`, `architecture`→`@integration`, `system`→`@system` — and the gate warns when a level's `tested-by:` links all sit at the wrong depth. Warn-only and opt-in twice over: it cannot fire until the repo both sets `level:` and annotates a test level. `ARCH-VRUNGS-054`.
- **New `fan-out` lint check, band 5–20.** A level whose `satisfies:` children fall outside the band is reported at *both* edges: too few is not a level, too many is a level that has not been split. Warn-only. It fires 7 times on this corpus and those 7 are left standing — the check is only worth having if its findings are real. `ARCH-FANOUT-052`.
- **New atomic requirement form (`form: atomic`).** A story blockquote plus a `Scenario:` block, with no normative headings at all; 632 of 689 requirements now use it. The engine detects the form **from the body, never from the frontmatter**, because every consumer of `binding_hash` gets a body and not always a meta — and a form it cannot recognise hashes the empty string, which would make every requirement's contract identical. The legacy WHY/WHAT/WHERE/HOW form stays fully valid. `ARCH-ATOMICFORM-053`.
- **One `.md` may now hold many requirements.** A block starts at a `---` line *immediately followed by* `id:`, so a bare `---` horizontal rule starts nothing and a single-block file is returned byte-identical. Each architecture requirement keeps its detailed design in its own document instead of scattering it: 689 requirements in 68 files rather than 689. `confirm` flips the status of the named block alone. Only block 0 may fall back to the filename for its id, or every module would mint a duplicate named after itself. `ARCH-MODULEFILE-056`.
- **`statement-size` raised from 75 to 150 words, and `long-sentence` removed.** The 25-word per-sentence ceiling had shipped with `lint` on 2026-06-07 and reported **0** corpus-wide for its whole life — `_lint_prose` yields physical LINES and these files hard-wrap near 95 columns, so no sentence was ever seen whole. Nothing replaces it: a clause may now run three sentences of fifty words each. What remains is the sentence *count* (`statement-too-long`, 3) and the 150-word *clause* ceiling — both per clause, neither per sentence. This is a deliberate loosening, recorded so it reads as a decision and not an oversight. `ARCH-LINTCHECKS-025`, `ARCH-ATOMICITY-049`.
- **`_map.md` gains a fifth Mermaid diagram: the level hierarchy**, drawn from the `satisfies:` edges (`upstream_edges`, which `_build_json_text` previously computed and discarded). The code level is counted, not drawn — 621 nodes is not a diagram. `ARCH-MAPDIAGRAMS-055`.
- **Viewer redesigned as a module explorer** — a requirements-module tree (`app/src/lib/tree.js`), an `ExplorerView`, and a `FindingsView`, so a corpus with 689 requirements on three levels is navigable rather than a flat list. Vendored viewer rebuilt. `ARCH-VIEWER-007`.
- **Ids now carry their level: `SYS-` (9) → `ARCH-` (59) → `REQ-` (621).** One mechanical prefix swap over 681 ids and 415 code tags, every tail (`STEM-NNN`) kept intact. The prefix is a reading convenience for this corpus — `level:` in the frontmatter is the authority, and a consumer repo may name ids anything. **`docs/adr/**` and `CHANGELOG.md` were deliberately not rewritten**: they record what was true on a date, and an ADR citing `REQ-VLEVEL-037` is a correct statement about 2026-08-17. Match the tail to translate one; CLAUDE.md carries the rule.
- **`ARCH-MODULEFILE-056` shipped `confirmed` with no test behind it** — caught by this repo's own test-link gate, not by review. Six tests added.
- `reqmap.py new`'s scaffold now offers `level:` and `satisfies:` as commented optional fields, so a consumer can discover the levels without reading the source.
- `MAP_ENGINE_VERSION` → `2026-09-03`. 668 tests.

## plugin `v2.31.0` — 2026-09-02

**A word-count heuristic for over-long Contract clauses, plus an opt-in scaffold that splits one out — with the atomicity rule they serve kept explicitly separate from the number that approximates it.**

- **New `statement-size` lint check (warn-only).** A Contract clause over `LINT_STATEMENT_WORDS` (75) words is reported for re-reading. `REQ-ATOMICITY-049` states the normative rule — a clause describes a single independently verifiable obligation — and marks the 75 words an explicit *heuristic*: exceeding it never makes a clause invalid, never changes the exit code, and is never a determination of atomicity, which the engine cannot observe. AC-6 asserts that blindness as behaviour rather than leaving it as prose: a 20-word clause holding two obligations passes the check, and that is the correct result.
- **Measured per clause, not per line.** `_lint_prose` yields physical LINES, and these files are hard-wrapped near 95 columns — the longest line it produces for `REQ-CHECK-006` is 15 words. `long-sentence` (25) and `statement-too-long` (22) therefore report **0** across the corpus, not because the prose is short but because no clause is ever seen whole. New `_contract_clauses` joins continuation lines, treats a nested sub-bullet as its own clause, and skips glossary comments; `_clause_words` counts a backticked span as one token. The two per-line checks are deliberately left unchanged — widening their unit would flip the corpus from 0 warnings to many, on confirmed requirements, which is a separate decision. Pre-ship dry run: **0 of 599 clauses** over 75 words (max 62), so the check ships as a line already held rather than as a defect hunt.
- **New opt-in `lint --decompose`.** Scaffolds one draft requirement per `statement-size` finding, seeded with the clause verbatim and depending on its parent. `REQ-DECOMPOSE-050`. The default `lint` run still writes nothing, for a mechanical reason: `.githooks/pre-commit` runs `gate` -> `lint --strict` -> `map --check`, so a file written during the lint step would fail the `map --check` step of the same hook run, and in CI the checkout is ephemeral. The parent is never modified, so no confirmed contract drifts and deleting the created file undoes the whole operation. Re-running is a no-op, keyed off a `<!-- decomposed-from: <parent>#<n> -->` marker rather than the target filename — the id comes from the next free corpus number, so a second run would otherwise pick a fresh name and create a duplicate.
- `MAP_ENGINE_VERSION` -> `2026-09-02.2`.

## plugin `v2.30.0` — 2026-09-02

**A nine-senator Senate audit on "make requirements simpler, more objective, clearer" split into two decisions — one shipped, one rejected.** `runs/senate/2026-09-02_191837-reqmap-schema-simplify-context-merge-and-traceability.json`, two rounds, verdict MODIFY (8 blocking / 1).

- **New consolidated `## Context (non-binding)` section**, replacing `## WHAT — Notes & known limitations`, `## Example — in practice`, and `## WHERE — Current implementation` as three near-synonymous informative buckets with one, grouped by bold `**Notes**`/`**Example**`/`**Current implementation**` sub-labels (the same clause-group convention the Contract section already uses). `reqmap.py new`'s template scaffolds it for every new requirement. **Purely additive, not a migration**: the Senate found the originally-audited proposal's "no enforcement change" premise false — `_build_map_data` reads the legacy headings by label to populate `_map.json`'s `notes`/`current_impl` fields, so renaming them without a fallback would have silently emptied those fields corpus-wide. The legacy three-heading form stays fully valid forever; new `_context_group` is tried only when the legacy heading is absent, and no existing requirement file (in this repo or any consumer) needs to change. `git diff --stat` on this repo's 51 pre-existing requirement files for this release: zero lines. [ADR-0017](docs/adr/0017-consolidated-context-section.md), `REQ-CONTEXT-048`.
- **Rejected: a Contract-clause-to-Acceptance-criterion traceability marker** (`{#C<n>}` anchors + `covers: C<n>` tags, a new opt-in `uncovered-clause` lint check). This is the third attempt at a mechanism this repo has already rejected twice — [ADR-0012](docs/adr/0012-internal-consistency-lint-rejected.md) (78.6% false-positive rate measured) and [ADR-0016](docs/adr/0016-no-edge-case-marker.md) (decided one day earlier; comparable opt-in in-file markers measured at 2/51 adoption vs. 12/51 for test-file-based `# verifies:` tags) — and the proposed `{#C<n>}` syntax was independently found to leak into `acc`/the viewer, reproducing the `REQ-VIEWER-007` AC-8 regression class already fixed once. [ADR-0018](docs/adr/0018-no-contract-acceptance-traceability-marker-yet.md) records the numeric revisit bar for a future attempt.
- `MAP_ENGINE_VERSION` → `2026-09-02.1`.

## plugin `v2.29.3` — 2026-09-02

**A full-repo code review turned up ten latent bugs and inefficiencies, none yet reported by a consumer.** All ten are fixed here — three correctness bugs in the gate/viewer, two on-disk drift/staleness false positives, two redundant tree walks, and two small maintainability cleanups.

- **`gate`/`sync` exempted `layer: need` from the implements-tag check by hand instead of via the shared `_impl_exempt` predicate**, so a confirmed `layer: aggregate` requirement (exempt everywhere else — `confirm`, `health`, the risk map) still ERRORed on the very next `gate`. All four sites now agree. `REQ-TRACE-020`.
- **`confirm` and `new --from-todo --mark-done` silently converted CRLF requirement/TODO files to LF** on any POSIX host (Linux/macOS/CI): both read with universal-newline translation and wrote back with `os.linesep`, so a one-line frontmatter or checkbox edit turned into a whole-file line-ending diff. Both now read and write with `newline=""`, preserving whatever line ending was already on disk. `REQ-PROMOTE-011`, `REQ-PROMOTE-TODO-001`.
- **The viewer's Problems tab silently dropped every `unverified-intent` signal.** Its local severity map was written against an earlier, since-renamed set of risk signals — it still had a `drift` entry the engine never emits, and was missing `unverified-intent`, a real signal the CLI (`next`, `show`) surfaces. `REQ-VIEWER-007`.
- **The sidebar's orphan count disagreed with the Problems tab** for a `layer: aggregate` requirement: the shared `coverageOf()` helper exempts both `need` and `aggregate`, but the Rail's own inline orphan calculation only excluded `need`. `REQ-VIEWER-007`.
- **A routine `MAP_ENGINE_VERSION` bump could flag a previously-committed site page as stale.** `site`'s STATS region embeds the live engine version, and `map --check`'s freshness diff compared it byte-for-byte with no exclusion — unlike the `repo`/`engine_version` fields already stripped from `_map.md`/`_map.json` for exactly this reason. `map --check` now ignores the STATS region's `engine` cell too. `REQ-SITE-026`.
- **`show <ID>` walked the whole tree twice** — once via `scan_members`, once more via `scan_test_levels` for the same invocation — even though `gate`/`sync` were already consolidated onto one walk (`scan_all`) for this exact cost. `show` now takes the same one-walk path.
- **A full `sync`/`init` run hashed every dedicated member file twice** to compute `_memberlock.json`'s baseline: once inside `member_drift`, once again to save it. `member_drift` now accepts a precomputed hash map so the full-scan case (the common one) pays for the hash pass once. `REQ-MEMBERDRIFT-027`.
- **`AC_VERIFY_RE` hand-wrote the requirement-id grammar** instead of reusing the already-named `_ID_PAT` constant every other tag pattern in the file shares.
- **`MapView`'s `Canvas` and `RoadmapView` each carried their own copy of the same grab-to-pan mouse-handler logic** (drag threshold, document listeners, click-suppression). Extracted to a shared `useDragPan` hook so a future fix to one doesn't silently miss the other. `REQ-VIEWER-007`.
- `MAP_ENGINE_VERSION` → `2026-09-02`; vendored viewer rebuilt.

## plugin `v2.29.2` — 2026-08-31

**A consumer ran two subagents and the gate reported 1,829 members and 43 errors in a repo that has 493 members and none.** Every error came from a worktree copy of their own code.

- **The seeded `.reqmapignore` never excluded agent worktrees.** Claude Code runs an isolated subagent in `.claude/worktrees/<id>/` — a FULL second copy of the repo — and older tooling used `.worktrees/`. Neither was in `_reqmapignore_seed`, so a local scan counted every member a second and third time and read the copies' tags as dangling refs. The errors are invisible to CI, which checks out a clean tree, so the local gate and CI disagree on a repo where nothing is wrong — and the natural reaction is to hunt for the defect in your own code, not in the scanner. This repo's own root `.reqmapignore` had carried `.worktrees/**` by hand since the day it was hit; consumers got nothing. `init` now seeds both globs with the reason, and both `SKILL.md`/`SKILL.universal.md` document them beside the `scripts/reqmap.py` line. `REQ-INIT-012` +AC-7.
- **Every acceptance criterion had collapsed into one run-on line.** The viewer renders the authored Given/When/Then block (`accept`) as a monospace block, one line per line — but `adaptNode` only set it when the folded `acc` list was EMPTY. That was true for every requirement until `v2.29.0` taught the engine to parse the block form, and false for every one after: 51 of 51 nodes here, and the reader now got `AC-1 — Given a repo… When init runs Then it creates…` on a single line, in the Spec view and the map's detail panel. A fix that gave a downstream consumer its criteria back took them away in the same release. `accept` is now preferred whenever it exists; `acc` stays what it was built for — search and counting. `REQ-VIEWER-007` +AC-8, asserted in the SSR smoke; vendored viewer rebuilt.
- **`translate` could rename a criterion and still cache the result.** The structural-fidelity gate compared backticks, numbers and markdown markers — all blind to the two things that are identifiers rather than prose: `AC-1` → `CA-1` keeps the same digit and is neither heading nor bullet, and `Given` → `Dat fiind` touches nothing at all. But `AC-N` is what a test points at (`# verifies: <ID>#AC-N`), and a reader shown "Dat fiind" cannot match the criterion back to the .md file of record — the same argument that already keeps `confirmed` and `draft` untranslated. Both are now part of the signature, and the prompt says so, so a model that translates them is answering a question nobody asked. Deleting a criterion was already caught. `REQ-TRANSLATE-044` +AC-9, and its other eight criteria picked up the `verifies:` tags they had earned.
- `MAP_ENGINE_VERSION` → `2026-08-31.2`.
## plugin `v2.29.1` — 2026-08-31

**A consumer's System Map drew its edges as endless horizontal lines. The cause was a dependency cycle meeting a ranking loop that cannot converge on one.**

- **`depends_on` cycles were invisible.** The gate checked that every `depends_on` target exists and never that the graph is acyclic, so three cycles sat in a 59-requirement corpus (`ACCESSLOG-077 -> CI-UPLOAD-037 -> EMPLOYEES-036 -> TENANT-034 -> ACCESSLOG-077`, and two around `SIGN-APPLY-049`) with nothing reporting them. New `_dependency_cycles` walks the registry in sorted order and the gate names each distinct cycle. **WARN, not ERROR, deliberately**: a dangling `depends_on` is a typo with one fix, a cycle is a modelling call across several requirements, and promoting it would fail a build that was green yesterday with none of the consumer's own lines changed (ADR-0002). It stays a warning under `--strict` too. `REQ-CHECK-006` +AC-14.
- **The viewer's layout could not survive one.** `rankNodes` ranks by longest path through repeated relaxation, which never converges on a cycle: every pass adds one to every node around it, so the loop ran its full budget and returned **maxRank 236 for 59 nodes** — a DAG of 59 cannot exceed 58. That is a **71,362px-wide canvas** with ~230 empty columns, and `buildEdgePath` dutifully stepped each edge through every one of them. Cycle-closing edges (found by an iterative DFS) are now excluded from the ranking and still drawn. Same corpus: **maxRank 236 → 12, width 71,362px → 4,412px**. An acyclic registry is unaffected by construction — no back edges, nothing removed. `REQ-VIEWER-007` +AC-7, asserted in the SSR smoke.
- `MAP_ENGINE_VERSION` → `2026-08-31.1`; vendored viewer rebuilt.

## plugin `v2.29.0` — 2026-08-31

**Ten findings from a consumer session on a 55-requirement corpus, fixed.** The report is one repo's real use of `v2.28.1` (`Management_Dashboard`, ~390 members); every item below was reproduced against this repo's own corpus or its code before being changed.

- **The emitted `acc` list was empty for every requirement written the way the tool prescribes.** `_bullets` collects only `- ` lines; the template's Acceptance section is labelled Gherkin blocks (`AC-1` + indented Given/When/Then). Reproduced here: `acc: []` on **50 of 50** nodes, with the text sitting unread in `accept`. New `_acc_blocks` is now the single parser of that section — `_acc_items` (map emission), `_labeled_acs`, `_automatable_acs` and `_count_ac` all read it, so a criterion cannot be counted by one and missed by another. `REQ-MAP-007`, `REQ-ACVERIFY-019`.
- **The viewer displayed a coverage fraction nobody computed.** `covered`/`clauses`/`gap` were never emitted by the engine, so the viewer fell back to `clauses` = number of CONTRACT lines and `covered` = all-or-nothing: a requirement with three tests named after its criteria read **"untested — 0 / 8 clauses covered"**, and its owner opened an investigation. The engine now emits those three fields from the per-criterion coverage the gate already computes — and only for a requirement that has adopted `# verifies:` tagging. Absent means *not measured*, and the viewer renders the badge with no fraction. `REQ-ACVERIFY-019` +AC-6.
- **The viewer showed fabricated `created` / `updated` dates**, derived from the LENGTH OF THE ID (`2026-${id.length%5+1}-…`) and printed beside the `git log --diff-filter=A` command that would have produced them — two requirements with 16-character ids showed the same date. Removed outright rather than faked more convincingly. A real git date in a *committed* map would be self-invalidating: the commit that regenerates the map is not yet in the history the date is read from.
- **`status: draft` masked test coverage in the viewer.** The draft check preceded the `tested-by` check, so a draft with twenty tests read "untested". All 55 requirements in the consumer corpus were draft; after promoting 54, `health` went **0 → 96** without a single test being written. Review state and test coverage are two axes; the status pill already shows the first.
- **A `layer: need` was labelled "test-exempt — skipped by the gate"** though it has no `test_exempt` and may have real tests. Three exemption reasons (deprecated, `test_exempt:`, covered-by-edge) now render as three labels.
- **New `layer: aggregate`** for a requirement whose implementation IS its dependencies' — the MVP-acceptance shape: 0 fan-in, 12 fan-out, no code of its own, and no way to model it. `layer: bus` was wrong by the tool's own definition (bus = high fan-in), `need` points the wrong way, and `test_exempt` silences the wrong signal. Covered downward by `depends_on`, as a need is covered upward by `satisfies:`. Rejected the cheap version — "any requirement with dependencies and no code is covered" — because an inference disarms the gate's most valuable error for a population nobody enumerated. [ADR-0015](docs/adr/0015-aggregate-layer-instead-of-implicit-dependency-coverage.md), `REQ-TRACE-020` +AC-5.
- **`confirm` refused a `layer: need`** that the gate, `health` and the risk map all exempt. This repo's own `NEED-SSOT-001` is `confirmed` only because the file was hand-edited around the command. All four sites now read one predicate, `_impl_exempt`. `REQ-PROMOTE-011` +AC-5/AC-6.
- **Four real bash suites warned forever**: `_test_link_problem` knew Python, JS, Go and Rust, and no shell idiom. A `test_x()` function, a `function test_x`, a bats `@test`, and the `*.test.sh` naming convention now count. The check also runs at **every status** rather than only `confirmed` — a `tested-by` pointing at a React component instead of its spec is wrong the day it is written, and hiding it until promotion audits the corpus exactly when it is largest. Warn-only below `confirmed`, so a draft-heavy `--strict` CI cannot start failing. `REQ-TESTLINK-018` +AC-6/AC-7.
- **The per-AC warning ignored `<!-- verifiable by: … -->`** and warned about criteria a machine can never verify (13 `inspection` + 1 `manual` in that corpus). It also **punished partial adoption**: one tag turned on a warning for every remaining criterion, so 110 correct new tags moved the count only 171 → 98. Now: manual criteria excluded, and one aggregated line per requirement — `4/5 automatable criteria carry a verifies: tag — missing AC-6`. `REQ-ACVERIFY-019` +AC-5.
- **`gate` said nothing about a stale committed map**, so a consumer following the documented "run `gate` before every commit" learned it from a red CI run — twice. `_map_check` is split: `_stale_artifacts` returns the verdict, `map --check` fails on it, and `gate` warns. `REQ-MAP-007`.
- **New `suggest-verifies`**: proposes `# verifies: <id>#AC-N` for tests already NAMED after the criterion they check (110 of 205 untagged criteria were, in that corpus), with the three guards the reporter paid for one wrong link at a time — a shared `tested-by` file needs a distinctive id token in the test's own name; a class name qualifies nothing; a fixture parameter is not a token. Read-only; `--apply` writes the tags. New `REQ-SUGGESTVERIFIES-047`.
- **New `layer-mismatch` lint**: a `layer: bus` nothing depends on, that itself depends on 3+ requirements, is a roof labelled a foundation. Silent on this corpus (max fan-out 3, no bus with zero fan-in); it fires on the 0-in/12-out shape that prompted it. `REQ-LINTCHECKS-025`.
- `MAP_ENGINE_VERSION` → `2026-08-31`; vendored viewer rebuilt.

## plugin `v2.28.1` — 2026-08-27

**`dupes` reported a requirement and its own test suite as probable duplicates.** On a consumer corpus that keeps one requirement per script *and* one per test module (Senate: `SCRIPTS-X` / `SCRIPTS-TEST-X`), 9 of 32 flagged pairs were exactly that — scores 0.42–0.60, near the top of the list — and the reviewer learned to scroll past the report. The two share vocabulary by construction, and the corpus already says so: the test requirement's `implements` file is the other's `tested-by` file.

- `cmd_similar` now takes the member map (`dupes` passes it from the scan) and skips a pair linked by `tested-by`, printing `skipped N pair(s) linked by tested-by` instead. Without a member map (library callers, the existing tests) behaviour is unchanged. `REQ-SIMILAR-016` +AC-7; Senate corpus 32 → 23 pairs, and every pair still involving a test requirement is a genuine cross-link (e.g. two different test suites), not a suite reported against its own subject.
- `MAP_ENGINE_VERSION` → `2026-08-27`.

## plugin `v2.28.0` — 2026-08-25

**The rest of the scan-evidence matrix, run the same day: five foreign repositories, five language families, ten engine fixes.** Run 6 (`v2.27.0`) was one consumer. These are strangers: `madler/zlib` + `curl/curl` (C/C++, 4,449 files), `excalidraw/excalidraw` (TS/React), `docker/awesome-compose` (Dockerfiles, compose YAML, 11 app languages), `gin-gonic/gin` + `encode/httpx` (Go, Python), `danielmiessler/fabric` (396 Markdown prompt files). Each run: inventory → `coverage` → `plan` → `draft` → `gate` → `next`/`health`/`dupes` → a native-comment-style tag probe per language → edge probes. Zero crashes on the protocol itself; zero false-positive tag hits across all seven repos (`TAG_RE`'s boundary guard held); the C/C++ scanner passed 16/16 probes (block comments, `#define` lines, CRLF, Latin-1 bytes). What broke was everything around the scanner.

- **`plan` produced 0 candidates for zlib, none for gin's 99 Go files, none for awesome-compose's 35 Dockerfiles — and said "wrote plan (0 candidates)", exit 0.** Its file filter was a five-extension private list while `draft` used the full scan set, so the documented "run `plan` before `draft`" preview silently omitted most of what `draft` then wrote (excalidraw: 663 planned vs 687 drafted). Every scannable code file is now a candidate; a language without a parser carries empty facts. zlib: 0 → 101 candidates. Candidates also carry `is_test` (a `tests/` segment, `test_*`, `*_test.go`, `*.spec.ts`) — httpx's plan was 37/60 test files with nothing marking them. `REQ-CANDIDATES-009` +AC-7.
- **`plan`'s Python facts stopped at module level**: `httpx/_client.py` showed 3 helpers and hid its 78 public methods. Public methods of top-level classes are now signatures (`def Client.get(url)`).
- **`draft` wrote the identical TODO stub for every code file** while `plan` had already read the file's signatures — the run-2 agent found `vector.ts` with 15 extracted exports and a draft that used none. A code proposal's WHERE section now lists the observed surface (module docstring + up to 12 signatures) as an explicit non-binding hint; the Contract stays a TODO, by contract. `REQ-EXTRACT-008` +AC-6, and its extension list — stale since the scan widened — now says "every scannable code file".
- **`dupes` right after `draft` was noise at scale**: 6,340 "probable duplicate" pairs for fabric's 638 drafts, 2,055 for curl, 1,748 for excalidraw — all template text. Requirements whose Contract bullets are all still `TODO:` are skipped with a count line; nothing authored, nothing to compare. `REQ-SIMILAR-016` +AC-6.
- **`dupes | head` died with `OSError: [Errno 22]` on Windows** (no SIGPIPE). New `REQ-PIPE-046`: the CLI entry (`_run_cli`) turns a closed reader — `BrokenPipeError`, `EPIPE`, `EINVAL` — into a quiet exit 0; every other `OSError` still propagates.
- **`classify_prose` matched `README` case-sensitively**, so fabric's one `readme.md` was auto-drafted while 37 `README.md` siblings were correctly left alone. Case-insensitive now. `REQ-PROSE-024`.
- **A prompt corpus written with `#` for every section got "(no section headings detected)"** on 204 of 255 drafts — the scaffold only read `##`. With no H2 anywhere, later H1s are the sections. `REQ-PROSE-024`.
- **Scan reach**: excalidraw's only stylesheet format (`.scss`, 82 files) and awesome-compose's `.cs`/`.vue`/`.php` apps were invisible to every command. Added `.scss .sass .less .vue .svelte .mjs .cjs .mts .cts .cs .php .rb .kt .kts .swift .scala .ex .exs .dart .toml`; `ORPHAN_CODE_EXTS` grows by the program languages. `CORE-SCAN-002` notes.
- **`v2.27.0`'s unscanned-tag check skipped every dotfile**, so a tagged `.env` stayed silent — the run-3 agent caught it on the check's first outing. Only `.git*` and `.reqmap*` are exempt now. `REQ-UNSCANNEDTAG-045`.
- Recorded, not fixed (design, documented in each run's TODO entry): `TAG_RE` is context-free by design, so a tag inside a YAML string value, a Dockerfile heredoc, or plain prose counts — three probes showed it; `.rst/.txt/.adoc/.ipynb/.mdx` and curl's 2,066 extensionless `tests/data/test###` fixtures stay outside the scan; `gate --cache` is slower than plain `gate` on its cold run (it builds the cache) and faster warm.

## plugin `v2.27.0` — 2026-08-25

**First scan-evidence run on a real consumer (Management_Dashboard: NestJS + Next.js, 288 tracked files — TS/TSX, SQL, shell, Dockerfiles, Caddyfile, Prisma, YAML, JSON, Markdown). Four engine defects, all fixed here; the corpus-side findings went back to the consumer.**

- **Tags in file types the scan never read were silently not members.** `Caddyfile` and `apps/api/prisma/schema.prisma` both carried `implements:` tags; neither type was scanned, so two requirements lost their members with the gate green. Two fixes, one local and one general: `.prisma`, `.graphql`, `.proto`, `Caddyfile`, `Jenkinsfile`, `Procfile`, `Vagrantfile` and any `Dockerfile.<variant>` (`Dockerfile.converter` was the third invisible tag) are now scanned — and new `REQ-UNSCANNEDTAG-045` makes the next case visible: `gate` warns (warn-only, fail-open outside git) when a tracked, non-scannable, non-binary file under 1 MB carries a tag. Dotfiles, `_`-prefixed files, `.reqmapignore` matches and the SSOT dir are skipped (this repo's own `.reqmapignore` quotes an illustration tag in a comment). Consumer members: 282 → 286.
- **62% of the consumer's gate time was `os.path.realpath`**: `_prune_dirs` resolved every directory on the walk to find the SSOT dir — 34,596 calls across three walks for a 216-file scan, driven by a 4,900-folder upload directory. It now resolves only a directory whose *name* matches the SSOT dir's (same exclusion, contract unchanged), and a `.reqmapignore` pattern ending in `/**` or `/*` prunes the walk instead of filtering every file under it (identical results by construction). Gate on the consumer: 11.2 s → 4.1 s; 0.6 s once `apps/api/storage/**` is ignored.
- **`map --check` failed on the consumer for `_map.json` whose only difference was `engine_version`** — nodes, edges and todos identical. Updating the vendored engine alone no longer makes a committed map stale: `engine_version` joins `repo` and `generated:` in the freshness-diff exclusions (`REQ-MAP-007`). The next `sync` still refreshes it.
- **`next` listed `CLAUDE.md` and `TODO.md` as "Untagged files"** with advice to run `draft` — which never drafts them, because `REQ-PROSE-024` puts meta prose in the *ignore* bucket. The bucket now honours that bucket (`REQ-NEXT-013`); sync-only prose (`README`, `docs/`) is still listed, because it *can* carry a `generated-from:` tag.
- Also seen on the consumer, not engine defects: its committed `_findings.md` was stale (9 vs 10 live) — caught by `v2.26.0`'s new check on first contact; 42/44 requirements are `draft` with 0 confirmed (the skill's triage path); its CI has no reqmap gate step; `package-lock.json`/`tsconfig`-class JSON was the only JSON present, so no JSON tagging convention is needed on this evidence.

## plugin `v2.26.0` — 2026-08-25

**A committed `_findings.md` that said "0 open" for eleven weeks — and two smaller lies the tooling told during the same audit.** `v2.25.1` regenerated the file by hand; this release makes that unnecessary, and closes the two follow-ups the audit left open.

- **`_findings.md` is now a derived view like `_map.*`.** `map` (and therefore `sync`) rewrites it when it already exists, and `map --check` names it stale when the committed copy differs from a fresh render. Neither ever *creates* it: a repo opts in by running `findings` once and committing the result, exactly the file-absent convention `_map.*` and `docs/map.html` already follow. For a consumer who committed one and never re-ran `findings`, `map --check` will newly fail once — the fix is `reqmap.py sync`. `REQ-FINDINGS-010` +AC-6/AC-7; `_render_findings()` is the shared renderer.
- **`next` stops calling a scan-scope problem an orphan.** The narrow default invocation in this repo (no `--code ..`) lists `REQ-SELFGATE-039`, `REQ-REPRO-041` and `REQ-STALEENGINE-043` as "confirmed, no code" — their members are `.github/workflows/ci.yml`, `.githooks/pre-commit` and friends, one directory above the scan root. The committed `_map.json` records those members, so `next` now reads it and adds a note under the Orphans bucket naming one of them and suggesting `--code <dir>`. The item stays in the bucket (it *is* an orphan for that scan); only the puzzle goes away. `REQ-NEXT-013` +AC-10.
- **`new` warns on a same-area number collision.** This corpus already has `REQ-MAP-007`/`REQ-VIEWER-007`, `REQ-SITE-026`/`REQ-DOCBUNDLE-026` and `REQ-DRIFTIMPACT-035`/`REQ-REGISTRYLAG-035`. Ids stay unique by their full text, so nothing was ever broken — but two requirements answering to "007" get confused in conversation. `new` (and `new --from-todo`) now prints a `WARN` naming the existing id when the area and `NNN` both match; different areas (`CORE-PARSE-001` beside `NEED-SSOT-001`) stay silent. Exit code unchanged. The existing pairs are deliberately **not** renumbered: an id is referenced from code tags, the lock, the map, ADRs and every CHANGELOG entry, so a rename costs more than the ambiguity does. `REQ-NEW-004` +AC-5.
- `REQ-TRANSLATE-044` promoted `baseline` → `confirmed`: both verify-intent questions from `v2.25.0` are answered (stopword lists stay small; the language set stays `ro`/`en` until a second consumer language exists) and folded into its Notes. The corpus is now 48/48 confirmed with no open findings, so the committed `_findings.md` reads "0 open" and this time that is true.
- Viewer baked fixture re-synced to the three rewritten contracts; `_map_viewer.html` rebuilt. `MAP_ENGINE_VERSION` → `2026-08-25.2` (the new `check_engine_bump.py` gate saw the engine diff and required it).

## plugin `v2.25.1` — 2026-08-25

**Two engine releases told every consumer they were up to date.** `v2.24.0` (the `redundant-modal` lint check) and `v2.25.0` (`translate`) both changed `reqmap.py` without moving `MAP_ENGINE_VERSION`, which stayed at `2026-08-20.2`. That constant is the only thing a seeded copy — and `check/engine_staleness.py` in the published action — can compare, so a consumer on the 08-20 engine was reported current while missing both features. Nothing checked the rule; it lived in `CLAUDE.md` as a sentence.

- `MAP_ENGINE_VERSION` → `2026-08-25`. New `scripts/check_engine_bump.py` makes the rule mechanical: any diff to `plugin/scripts/reqmap.py` must also change the version line. CI runs it against `HEAD~1` in `gate-and-tests`; the dev pre-commit hook runs it on the staged diff. Own suite (`scripts/test_check_engine_bump.py`) seeds a throwaway git repo for both modes.
- **`SKILL.md` and `SKILL.universal.md` still told consumers to pin `check@v1`** — the gate-only alias frozen at v2.1.0 — three releases after `README.md`/`CLAUDE.md` moved to `@v2`, and right above prose describing `@v2`-only inputs (`lint:`, `freshness:`). `check_versions.py`'s `ACTION_REF_FILES` did not include the skill files, so its alias axis never saw them. Both now say `@v2` and both are in the list (7 references asserted, was 5); a regression test pins a lagging skill file as a failure.
- `translate` now hands the prompt to `claude -p` on stdin instead of as one argv element — a whole requirement in a single argument would hit Windows' ~32 KB command-line ceiling on a large corpus (largest here is ~9.5 KB today; the limit was silent).
- `lint`: the 15 `redundant-modal` warnings left visible-but-unfixed in `v2.24.0` are now fixed (69 `shall`/`must` clauses across 13 Contract sections rewritten in plain present tense — wording only, no contract change; lock advanced with `--accept-drift`). The two `file-spread` warnings (`REQ-REVIEW-022`, `REQ-SELFGATE-039`) are exempted with the reason in each Notes section: spanning those files *is* the capability. `lint --strict` now reports 0 warnings on this corpus.
- The viewer's baked demo fixture (`app/src/lib/data.js`) mirrors `REQ-INIT-012`'s rewritten clause, so `gate`'s viewer-data-sync check is silent again; `_map_viewer.html` rebuilt from it (`npm run build:viewer`).
- `_findings.md` regenerated — the committed copy dated from v1.12.0 and said "0 open" while `REQ-TRANSLATE-044` carries two open verify-intent questions.
- Repo-root `.reqmapignore` now excludes `.pytest_cache/`, `.ruff_cache/`, `.superpowers/` and `diagrams/` (all gitignored): a local `next`/`coverage`/`health` reported 47 "untagged files" CI could never see.
- Five `open(...).read()` sites in the engine use a context manager; four stale "`npm run smoke` is not wired into CI" comments (`.reqmapignore` ×2, `app/CLAUDE.md`, `REQ-VIEWER-007`) corrected — the `artifacts` job has run it since v2.23.0.

## plugin `v2.25.0` — 2026-08-25

**A consumer's viewer speaks Romanian and refuses to translate your requirements — until every requirement is in the reader's second language.** `v2.23.0` drew a hard line: the locale toggle translates UI chrome only, never requirement content, because translating the artifact under review live would put words in the author's mouth. That line was right for a mixed-language reader who mostly understands the source — it fails completely for a reviewer who does not read the corpus's language at all.

`reqmap.py translate [--to ro|en]` adds the one exception, kept manual and opt-in on purpose: it is the ONLY subcommand that shells out to an external LLM (`claude -p`), and this engine's `gate`/`sync`/`lint`/`map`/pre-commit path stays exactly as `claude`-free as before — nothing above calls it.

- Detects the corpus's majority language (Romanian diacritics, else a stopword-frequency vote); a per-file `lang: ro|en` frontmatter value overrides detection for the rare misclassified file.
- Caches results in `requirements/_i18n/<locale>.json`, keyed by a content hash over title + WHY + Contract + Acceptance — deliberately not `binding_hash()` (Contract+Acceptance only), so a title-only edit still invalidates the cache.
- A structural-fidelity check (backticked spans, numbers, heading/bullet markers must match) gates every cache write; a missing `claude` CLI, a timeout, or a failed check skips that entry with a `WARN` instead of aborting the batch. Cache hits skip the CLI call entirely.
- `map`/`export` inline the cache onto each node **read-only** — a file read, never a `claude` call — so `map --check` in CI stays exactly as deterministic as before.
- The viewer never presents cached text as the author's own: every translated field renders behind a visible "machine-translated, unreviewed" badge (`translatedText()` in `i18n.jsx`), and falls back to the source text whenever no cache entry exists.

`REQ-TRANSLATE-044` carries the full contract (8 ACs, `lint_exempt: ac-count-high` — same reasoning as `REQ-LINTCHECKS-025`: each AC pins one module's behavior).

## plugin `v2.24.0` — 2026-08-24

**A Contract section written in Romanian had "shall" in it — nothing caught that.** The style rule already existed ("Audience & writing level" in `SKILL.md`: plain present tense, no `shall`/`must` — the section already opens with "Every line in this section is binding."), but it was documentation only. A consumer repo's requirement corpus carried the anglicism in 29 files and 261 places before anyone noticed, because `lint` had no check for it.

`lint` gains `redundant-modal`: it flags `shall`/`must` on a Contract clause, same shape as the existing `vague-term` check — closed word list, backticked spans stripped first, one finding per distinct term, `warn` severity. Running it against this repo's own corpus surfaced 17 pre-existing hits, left as advisory (not fixed in this release — the check's job is to make them visible, not to silently rewrite prose).

`REQ-LINTCHECKS-025` documents the check with AC-10; `REQ-LINT-014`'s check-list note is updated to match.

## plugin `v2.23.0` — 2026-08-21

**The viewer speaks Romanian, and refuses to translate your requirements.** The self-contained `_map.html` had exactly one language, and the interesting part of adding a second is not the dictionary — it is the line the dictionary must not cross.

A locale control sits beside the theme toggle in the top bar. It translates **UI chrome only**: nav, tab labels, section headers, buttons, empty states.

Two categories are deliberately left alone:

- **Requirement content.** Id, title, intent, contract clauses, acceptance criteria and member paths stay in the language their author wrote them in. They are the artifact under review; translating them would put words in the author's mouth and break the match with the `.md` file on disk.
- **The engine's own vocabulary.** `confirmed`, `in-progress`, `draft`, `orphan`, `deprecated`, `bus`/`feature`/`need`, and the ERROR/WARN/REVIEW severities are literal values in the requirement files and in the gate's output. A reader who sees a translated status here and `status: confirmed` in the file has been handed a puzzle, not a translation.

Implementation notes, because the shape was chosen against a known-bad alternative:

- i18n is authored **into the JSX** (`app/src/lib/i18n.jsx` plus `t()` call sites) — not applied to the built bundle as a DOM overlay. A post-hoc patch of the built file lives outside every diff the build tracks and any rebuild silently wipes it.
- The dictionary is keyed by the **English source string**, so the JSX stays readable in English and a missing entry degrades to English instead of to `nav.map.label`.
- Split-node headers like `What — Contract … normative` are translated as separate strings, which is why the leading-space trap that bites exact-match DOM dictionaries cannot occur here.
- The choice is remembered per reader via `localStorage` (guarded for SSR and for browsers that throw on the accessor) and is **never written into the generated file** — `_map.html` stays byte-identical regardless of what anyone last selected.

Six assertions were added to the SSR smoke, the app's only automated check, and they test both directions: that a section header translates, and that the requirement's title, contract and status do **not**. `REQ-VIEWER-007` gains the contract clauses and AC-6.

## plugin `v2.22.0` — 2026-08-20

**A consumer's engine could rot for a year and CI would never say so.** `warn_if_stale` — the engine's own "your vendored copy is behind" notice — only fires when `CLAUDE_PLUGIN_ROOT` is set, which happens inside a Claude Code session and nowhere else. CI, the one place that runs on every push, was silent by construction. The cost is invisible and specific: checks that shipped after the vendored copy simply do not run, and the build stays green while covering less than the caller thinks.

The fix could not go in the engine. A stale `reqmap.py` does not contain the check that would report it stale, so the detector has to run from something the consumer does not vendor: the action.

`check@v2` now runs `check/engine_staleness.py` as its first step. It reads `MAP_ENGINE_VERSION` from the vendored engine and from the engine in the action's own checkout, and when the vendored one is older emits a `::warning::` annotation naming both versions — on the run, not buried in the log:

```
::warning title=Stale reqmap engine::vendored reqmap.py is stale (2025-01-02 < action 2026-08-20.2) - re-seed it ...
```

- New input `stale-engine`: `warn` (default), `error` (fail the build on it), `off`.
- Compared against the ref the caller pinned, so an exact-SHA pin is measured against that SHA's engine — the engine they asked for.
- Fails open in every mode: an unreadable or absent version, or any unexpected internal error, prints a skipped-probe note and exits 0. The probe is never itself the reason a gate run goes red.

**Why this stayed `@v2`.** The major-bump rule is about a default-on step that can newly FAIL a green build — that is what took `freshness` and `lint` to v2. This step is warn-only and exit-neutral, so no existing pin changes verdict. And a `@v3` would have stranded exactly the consumers this exists to reach: the ones who pinned once and never came back.

The probe never runs in this repo's own CI (this repo *is* the engine), so `scripts/test_engine_staleness.py` — 10 tests, wired into both CI test surfaces — is the only thing exercising it before it ships. Filed as `REQ-STALEENGINE-043`.

## plugin `v2.21.0` — 2026-08-20

**The gate read every file three times.** `scan_members`, `scan_ac_verifies` and `scan_test_levels` each walked the whole tree and opened every file. On a 10,000-file tree that was 3.06s + 2.76s + 2.81s of the gate's 8.49s — the scan was essentially its entire runtime, performed three times. The benchmark added in v2.20.0 was written to publish a number and ended up explaining one.

`scan_all` now reads each file once and runs all three extractions on the same lines:

| | before | after |
|---|---|---|
| one walk, all extractions | — | **2.53s** |
| `scan_members` alone | 2.62s | 2.62s |
| `gate` | 8.49s | **2.46s** |
| scan + gate, end to end | ~11s | **~5s** |

It is not three loops glued together — that would have been the risky version, because the three scanners have genuinely different masking rules (fences and indent blocks for prose, string literals for `.py`, a backtick strip that only the levelled scan applies):

- The walk itself moved into one `_walk_code` generator. Three byte-for-byte copies of that loop is how they drifted apart in the first place.
- `_scan_file_tags` gained an optional `lines` argument, so a caller that already read the file hands the content over instead of re-reading it. Every existing caller is unchanged.
- The two coverage scanners' identical per-line masking became **one** pass feeding both regexes, preserving the asymmetry exactly: only the levelled scan strips backticked spans first, so a documented *example* of a levelled tag still does not register as real coverage.

**The safety argument is a test, not a reading of the diff:** `scan_all`'s three results must equal what the three scanners return separately — asserted against both a mixed fixture (prose fences, a `.py` docstring, a backticked example, a `.ts` file) and against this repo's own corpus, where every masking rule is exercised by files that actually use them.

`cmd_check` takes the coverage maps as optional arguments and computes them itself when absent, so tests and any embedding tool keep working untouched. `--cache` stays on `scan_members` alone: it is off on the CI path this speeds up, and duplicating its invalidation rules would trade a measured win for a correctness risk.

**Bookkeeping:** the `v2.20.0` tag was cut at the merge of the first of that release's three stacked PRs, so it does not contain the `artifacts` job, the standing-warning fixes, or `REQ-TRACKED-042` — all of which its changelog entry describes. They ship here instead. A released tag is not worth moving; the entry above it is the correction.

`MAP_ENGINE_VERSION` → `2026-08-20.2`.

## plugin `v2.20.0` — 2026-08-20

**Two ways hostile-looking text broke the map, and a number for "does this scale".** `</script>` in a requirement body has had a regression test since v2.3.5. The other two characters named on the roadmap had nothing:

- **U+2028 / U+2029 were emitted raw into the inlined `<script>`.** They end a line in JavaScript but are ordinary characters in JSON, so `ensure_ascii=False` passed them straight through and any engine older than ES2019 read the assignment as an unterminated string — one character in one requirement title killing the entire viewer. Now escaped to ` `/` `, which denote the same characters in JSON, so the parsed graph is unchanged (pinned by a round-trip test).
- **A lone surrogate crashed `map` outright.** A lone surrogate has no UTF-8 encoding, so the write raised `UnicodeEncodeError` and took the whole command down — and with it the gate's map-freshness check. Not a theoretical input: `os.walk` hands back a filename whose bytes are not valid UTF-8 surrogate-escaped, and member paths go straight into the map. `_utf8_safe` now degrades it to U+FFFD for both `_map.json` and `_map.md`; the fast path is a C-level encode that touches nothing, and the per-character walk runs only for a string that genuinely cannot be encoded.

Both were written as failing tests first, then fixed. `REQ-VIEWER-007` gains AC-5 and the escape clause; `REQ-MAP-007`'s AC-7 widens to cover the surrogate case rather than growing an eighth criterion it has no room for.

**A published benchmark** (`scripts/benchmark_scan.py`, numbers in the README). On 10,000 source files and 100 requirements: `scan_members` 3.06s, `gate` 8.49s, map render 0.03s. It was written to publish a number and ended up explaining one — the gate performs **three full walks of the tree**, not one (`scan_members` + `scan_ac_verifies` + `scan_test_levels`, 8.63s combined ≈ its entire runtime). Filed as its own roadmap item: the three scanners have different masking rules, so merging them is a real refactor, not three loops glued together. Deliberately not wired into CI — a shared runner's I/O makes timing assertions meaningless, and a flaky perf gate teaches people to ignore red.

**The gate's two standing warnings are gone, and neither was cosmetic.** Every run printed the same pair. Both turned out to be real, and one of them was the check itself being wrong.

**1. The viewer's demo dataset had drifted from the registry it copies.** `app/src/lib/data.js` carries a hand-authored `BAKED` fixture so the viewer has something to show with no engine present, and 13 of its entries claim to mirror real requirements. Their contract text was **written in the `shall` voice that v2.15 removed from the registry** — so the tool's own demo showcased the style its linter now rejects, and a reader with no engine saw a system that no longer existed. All 13 refreshed from the live `_map.json`, and a new test asserts *this repo's* fixture against *this repo's* registry, so the drift cannot come back silently.

**2. Two of the "drifted" ids were never real, and the check should not have flagged them.** The fixture deliberately invents an orphan (`REQ-SYNC-014`) and a deprecated capability (`REQ-CACHE-014`) so the Risk and Problems tabs have signals to display. Those ids cannot exist in any registry, so comparing them against one produced permanent drift — the check crying wolf about data doing exactly its job. Entries now opt out with `demoOnly:true`, and `check_viewer_data_sync` skips them. The marker is deliberately opt-in rather than a loosening of the rule: an **unmarked** id missing from the registry still reports, because that is the real signal (a requirement renamed out from under the fixture), and a test pins that distinction.

**3. `docs/full_architecture.html` now carries its lineage.** The 99KB architecture poster is exactly the case `REQ-DOCBUNDLE-026` exists for — a whole-system doc built from many requirements, with nothing linking the two — and it was the one large bundle in this repo that had no `generated-from:` tag. `make_full_architecture.py` now stamps `<!-- generated-from: CORE-PARSE-001, CORE-SCAN-002, CORE-DRIFT-003, REQ-CHECK-006, REQ-MAP-007, REQ-VIEWER-007 -->` into the page it generates, scoped to what the diagram actually depicts rather than everything it touches. A contract change in any of the six now lists the poster as needing a redraw.

The tag immediately earned itself: the poster's glossary still explained **`@v1`** as "git tag of the published GitHub Action", three releases after that line moved to `@v2`. `check_versions.py`'s alias axis had not caught it, because the glossary names the bare `@v1` rather than the full `requirement-manager/check@vN` path it matches on.

**`gate` now names members git does not track** (`REQ-TRACKED-042`). The rule it enforces is that a committed generated artifact may depend only on tracked files — break it and the map records members a fresh checkout cannot produce, so `map --check` fails in CI over a file the reader cannot find. That happened twice in one day here (a gitignored subagent worktree, and a Consilium report carrying a real `generated-from:` tag), and both times the local scan could see what CI never would.

Built on **untracked** rather than gitignored, deliberately: it is the property that actually matters — a merely-uncommitted file breaks reproducibility identically — one `git ls-files` call answers both, and it avoids either hand-parsing gitignore semantics or spawning a `check-ignore` per path. Fail-open outside a git work tree (nothing at all, not "every member is untracked"), warn-only, exit code untouched: a consumer repo may tag an ignored file on purpose, and this nudges the choice into the open rather than overruling it.

`MAP_ENGINE_VERSION` → `2026-08-20.1`.


`MAP_ENGINE_VERSION` → `2026-08-20.1`.

## plugin `v2.19.0` — 2026-08-20

**The portability claim gets evidence.** The engine's pitch is "one stdlib-only file, runs anywhere with Python" — and the whole proof was a single CI job on ubuntu with `python-version: "3.x"`. The supported floor was therefore accidental (3.7, because nothing in the code needed more), and `-X utf8`, a convention that exists *specifically* for Windows codepages, had never once run on Windows in CI.

- **Declared floor: Python 3.9** (`MIN_PYTHON`, new `REQ-PYFLOOR-040`). Deliberately the oldest version CI actually runs, not the oldest the code happens to tolerate: 3.7 and 3.8 cannot be installed on current GitHub runners, so promising them would be a claim nothing proves — the exact failure mode this project exists to prevent. `reqmap.py` now refuses an older interpreter before any command runs, with one ASCII line naming the required version, the running version and the fix, and exit 2 — instead of an `AttributeError` from deep inside a command. The check is a pure predicate (`_python_floor_error`) so the floor is pinned by tests on any interpreter; it cannot help below 3.6, where f-strings make the module fail at compile time, and that limit is written down in the requirement's Notes.
- **New `tests` matrix job: 3.9 / 3.12 / 3.13 x ubuntu-latest / windows-latest**, `fail-fast: false`, running every suite (engine, version gate, release notes, cross-tool falsification, Excalidraw builder + tests). Kept separate from `gate-and-tests`, which stays a single authoritative verdict on this repo's requirement corpus — running the gate six times would produce six identical answers.
- **A test asserts the two stay equal**: `MIN_PYTHON` against the oldest quoted Python in `ci.yml`, so raising the floor without moving the matrix (or the reverse) fails the build. It skips cleanly in a seeded consumer repo that has no `.github/` of ours.
- `release` now needs the matrix as well as the gate — a version that fails on Windows or on the floor must not become a tag consumers install. `deploy-map` still needs only the gate, since it republishes `docs/`, which the gate already drift-checks.
- Docs corrected where they promised more than was tested: `check/action.yml`'s `python-version` said "any 3.x works", and README / both SKILL files described the engine without naming a version.

**Committed build artifacts are now re-derived and compared** (new `artifacts` job). Two files here are build output that is nonetheless committed, because the point is that a consumer gets them without a toolchain: `plugin/scripts/_map_viewer.html` (217KB, the Vite single-file build the stdlib engine injects data into) and `docs/full_architecture.html` (99KB, the Excalidraw poster). Nothing checked either against its source, so a change to `app/` or to the generator could ship a viewer that no longer matched the code it was built from — with the repo still green. Both were measured before the check was written and are byte-reproducible: the viewer half is a literal `git diff --exit-code` (the build overwrites the committed file in place), the diagram half builds into a temp dir and compares, because the generator drops a sibling `.excalidraw` and `docs/*.excalidraw` is hard-blocked by `.gitignore`. **The check failed on its own first CI run, correctly**: the committed viewer carried CRLF on the 19 lines it inlines verbatim from `app/viewer.html`, because a Windows checkout hands Vite a CRLF template — while the Linux build emits LF, so the two disagreed byte for byte. `core.autocrlf` had hidden it locally by normalizing on the way in, which is why it could only ever surface in CI. Fixed at the source rather than papered over: `.gitattributes` pins the template and both artifacts to LF, and the Excalidraw builder now passes `newline="
"` on every write (Python's default translates `
` to `os.linesep`, so the same scene produced a different file on each platform). `release` needs this job too, and the whole thing is `REQ-REPRO-041` — split out of `REQ-SELFGATE-039` rather than bolted onto it, because the clarity lint flagged the combined requirement at 8 acceptance criteria: artifact reproducibility fails independently of gate wiring, so it is its own capability. `docs/architecture.html` stays out of scope — it is hand-authored, and its engine-owned regions are already covered by `map --check`.

**The matrix paid for itself on its first run** — three defects that a single ubuntu job structurally could not see:

- **`--since` failed OPEN on Windows.** `_since_changed_files` builds its changed-set from `git rev-parse --show-toplevel`, which always returns the long path form, while the caller's `code_root` can carry an 8.3 short component (`C:/Users/RUNNER~1/...`). `abspath` + `normcase` normalize separators and case but not short-vs-long, so the two sets never intersected: every member dropped out of the changed-set and `gate --since` reported a clean tree **with a dangling tag still in it**. Both sides now go through one `_path_key` (`realpath` then `normcase`), which also fixes the POSIX shape of the same defect — a repo reached through a symlinked path — now covered by a symlink regression test.
- **16 tests never ran in the documented invocation.** `if __name__ == "__main__": unittest.main()` sat mid-file, above `RoadmapSignals` and `ViewerDataSync`, so `python test_reqmap.py` executed it before those classes existed: 478 collected instead of 494. CI runs `-m unittest`, which imports the module fully, so CI never saw the gap. The entry point now stays last.
- **A test leaked the process cwd into its own result.** `cmd_check`'s `code_root` defaults to `"."`, and `test_strict_drift_exits_1` counts DRIFT lines without passing one — so run from `plugin/` it scanned the real corpus, saw a second DRIFT line and failed, while passing from `plugin/scripts/`. Both are invocations `CLAUDE.md` documents. Now hermetic.

`MAP_ENGINE_VERSION` → `2026-08-20`.

## plugin `v2.18.1` — 2026-08-20

**The published Action stops rotting.** `alxmax/requirement-manager/check@v1` was tagged on 2026-06-15 at plugin v2.1.0 content and never moved again — 193 commits behind `main` by the time anyone noticed, while the README kept advertising it as the way to run the gate in CI. Moving the alias was a manual step with nothing to remind a maintainer it existed.

- **The action's line is now `@v2`**, and the bump is deliberate rather than cosmetic: since v2.1.0 the action gained `freshness` (`map --check`) and `lint` (`lint --strict`) steps that both default to `'true'`. Re-pointing `@v1` onto current content would have newly FAILED a consumer build that was green — a stale committed map, or a requirement the clarity lint rejects. Adding a default-on check to an existing pin is a breaking change for the caller, so `@v1` is left frozen exactly where it is: existing pins keep working and keep running the gate-only step list they always ran.
- **The alias moves itself from now on.** `ci.yml`'s `release` job force-moves the major-alias tag onto the commit the current `plugin.json` version is tagged at, on every push to `main` — deliberately outside the "already released, exit 0" shortcut, so a half-failed run or a hand-moved tag self-heals on the next push instead of staying silently wrong.
- **The documented `uses:` line is the source of truth for which major that is** — there is no separate version file to fall out of step with the docs. `check_versions.py` gains a third axis (after semver and `MAP_ENGINE_VERSION`) asserting that `check/action.yml`, `README.md` and `CLAUDE.md` all name the same `check@vN`, so the README can no longer advertise a major the repo does not publish. The regex matches the full published path, so `@v1` named in prose as the frozen line is not mistaken for a live reference.
- `scripts/check_versions.py` now carries an `implements: REQ-SELFGATE-039` tag — it is the first step of the `gate-and-tests` job and was the last untagged file in this repo's own pipeline. `REQ-SELFGATE-039` gains AC-6 (alias placement) and AC-7 (alias coherence).
- **`.worktrees/**` added to the repo-root `.reqmapignore`.** A subagent worktree holds a full second copy of the tree, so the widened local scan double-counted every member (527 vs 261) and reported the copies' README/docs illustration ids (`AUTH-LOGIN-001`, `LOGIN-001`, `AC-1`) as dangling-tag **errors**. CI checks out a clean tree and never saw them — so the local gate and CI disagreed, which is precisely the divergence the gate exists to prevent.

No engine change: `MAP_ENGINE_VERSION` stays at `2026-08-19`.

## plugin `v2.18.0` — 2026-08-19

**The engine can finally see its own supply chain.** `docs/`, `.github/`, `.githooks/`, and root-level `scripts/` have always been outside the scan root — this repo nests `reqmap.py` at `plugin/`, so every documented command only ever reached `plugin/`. `REQ-DOCBUNDLE-026` — built to catch a generated `docs/` HTML bundle with no `generated-from:` tag — never saw its own `docs/full_architecture.html` (99KB), and none of `.github/workflows/ci.yml`, `check/action.yml`, `.githooks/*`, or `sync_reqmap.sh` carried a single membership tag. This release closes that gap for THIS repo's own CI and dev hook only, without moving the needle for any other repo vendoring `reqmap.py` unmodified — settled by a 3-personality Trias deliberation (`.consilium/runs/2026-08-18_1640_v29-scan-root-codeexts-viewer-trias.json`) that unanimously rejected auto-widening the shared default as a silent-failure risk to consumer repos scoped to a subdirectory on purpose.

- **`CODE_EXTS` gains `.sh`/`.tf`, plus exact-basename matching** for `Dockerfile`, `Makefile`, and the standard git hook names (`pre-commit`, `pre-push`, `pre-receive`, `post-receive`, `commit-msg`, `prepare-commit-msg`, `post-checkout`, `post-merge`) — behind one new `_is_code_file()` helper replacing 7 duplicated `endswith(CODE_EXTS)` call sites.
- **`--code` reaches the repo root for this repo alone.** `.github/workflows/ci.yml` and `.githooks/pre-commit` now pass `--code ..`/`--code .`; the shared `code_root = a.code or a.root` default is untouched byte-for-byte. A NEW repo-root `.reqmapignore` (kept deliberately separate from `plugin/.reqmapignore`, not a relocation of it — moving the original would have silently broken the narrow invocation's own exclusions) covers the generated-artifact false positives the wider scan surfaces: `docs/map.html` inlines requirement prose containing literal tag-syntax examples, which reads as a phantom dangling tag once reachable.
- **New requirement `REQ-SELFGATE-039`** tags `ci.yml`, `check/action.yml`, `.githooks/pre-commit`, `.githooks/pre-push`, and `sync_reqmap.sh` — this repo's pipeline wiring had zero membership tags until now. A confirmed requirement whose members are entirely outside `plugin/` genuinely ERRORs under the narrow `gate` invocation (not just a coverage miss) — documented in `CLAUDE.md` as an accepted, loud-not-silent consequence, since CI and the hook always run widened.
- **`gate` gains a warn-only check on `app/src/lib/data.js`**, the viewer's hand-authored fallback fixture (13 requirements copied from the registry so the demo works with no `_map.json` present) — flags requirement IDs whose baked contract text has drifted from the live registry. Caught two of its own correctness bugs in review before shipping: a non-greedy bracket regex that truncated any contract bullet containing `[`/`]` (any bullet describing syntax — a 100% false-positive rate on real data), and an uncaught `UnicodeDecodeError` that would have crashed `gate` outright on a non-UTF-8 file instead of degrading to a warning. Both fixed and regression-tested.
- README: lead rewritten around agent drift (an AI session silently diverging from an agreed contract) instead of generic spec rot; a real worked example (`new` → `confirm` → `sync` → drift → `gate`, actual captured terminal output); stale `~3700 lines` claim corrected; `test_reqmap.py` added to the layout tree.

`MAP_ENGINE_VERSION` → `2026-08-19`.

## plugin `v2.17.0` — 2026-08-17

**The engine now notices when its own roadmap drifts.** `TODO.md` is this project's roadmap and decision log, and nothing checked that it still matched reality. It fell behind twice — once by seven milestones — and the earlier fix, recorded in the `v1.35` section, chose manual hygiene over automation because demand was n=1. This is the read-only middle ground after n=2.

`health --json` gains two signals, both absent (not empty) when the repo has no `TODO.md`, so a project that keeps none sees nothing new:

- **`roadmap_behind`** — the newest roadmap milestone against the newest `milestone:` on any requirement, reported only when the roadmap is the older of the two. It compares against requirement metadata rather than a package version, because the engine owns the former in every repo and the latter is project-specific.
- **`roadmap_unversioned_headings`** — every `## ` heading whose first token is not a version. This is the one that actually bit: `_parse_todos_from_text` keeps the *current* milestone when a heading does not parse, so items below it are filed under the section above rather than skipped. A cosmetic rename silently re-filed this repo's only open roadmap item under the wrong version, with no error anywhere.

Versions compare segment by segment as numbers, so `v2.10` ranks above `v2.9` where a string compare reverses them.

Neither signal is a gate: no exit code changes, and the health score is untouched.

Also in this release: `scan_test_levels` masks Python string literals and docstrings alongside its backtick guard, so prose *about* how to tag never counts as coverage. That was real behaviour with no test and no clause — now pinned by both. New requirement `REQ-ROADMAP-038`.

`MAP_ENGINE_VERSION` → `2026-08-17.2`.

## plugin `v2.16.1` — 2026-08-17

**A clause-group label is decided by where it sits, not by the markers around it.** `v2.15.0` taught the voice to group clauses under bold labels, and `_bullets` learned to skip such a line so the next group's title would stop being appended to the previous group's last clause. It skipped them by shape — `re.fullmatch(r"\*\*.+\*\*", s)` — and `.+` is greedy, so it also matched a hanging-indent continuation that merely *opened and closed* on bold spans. Such a line was dropped, silently, from the parsed contract.

A requirement stating a two-part join predicate lost half of it that way: a clause reading *"shall use it ONLY when both hold: **containment** `…`, and **sanity** `…`"* wrapped so that the containment condition began and ended on a bold span. The generated map then read "when both hold:" followed by a single condition. The `.md` source was never touched and `gate` reported `0 errors` throughout — the gate checks that the map agrees with the engine, never that the engine is faithful to the source, so nothing in the toolchain could see it.

The separation that actually holds is positional: a group label is written flush left, a wrapped clause is indented. `_is_label_line` takes the raw line and requires column 0 alongside the bold-only shape. Across a 94-file consumer corpus every one of the 10 bold-only lines sits at column 0 and none is indented, while the line being eaten was indented two spaces.

**Why not simply narrow the pattern.** Excluding an internal `**` — `r"\*\*(?:(?!\*\*).)+\*\*"` — looks like the smaller change and is the wrong one twice over. It cannot decide a continuation whose entire content is one bold span, which stays ambiguous under any shape test and is exactly the case position resolves. And `***bold-italic***` contains `**`, so that pattern stops matching a real label and folds it into the bullet above — reintroducing the defect the label branch exists to prevent.

**Both call sites share the decision now.** The `over-scoped` lint counted clause groups off `_lint_prose`, which strips every line before returning it; on stripped input each bold-bounded wrap counts as its own group and inflates `contract_n`. Since `--strict` promotes `over-scoped` to an error, that miscount could fail CI on a requirement that is not over-scoped. It counts off `_section_raw`, which preserves indentation.

The two existing bullet tests were each green for the whole life of this regression, which lived in the intersection they jointly leave uncovered — so one more example-shaped test would not have been a control. The new cases pin that intersection, add shapes the corpus does not contain at all (bold-italic labels, wholly-bold continuations, tab indentation), and assert a containment invariant: every non-blank, non-comment line inside a section either opens a clause, folds into one, or is a column-0 label. `REQ-MAP-007` stated the rule in shape terms and now states the positional one.

`MAP_ENGINE_VERSION` → `2026-08-17.2`.

## plugin `v2.16.0` — 2026-08-17

**The V-model's right side gets levels, and a reserved role is redefined.** A `tested-by:` link said only *that* something tested a requirement, never at what level — a whole-system run and a single-function check looked identical to the tool. So the engine could report "this has no test", but never "this stakeholder need has never been validated", which is the question the V-model exists to answer. `tested-by:` now takes an optional suffix — `@unit`, `@integration`, `@system` — applying to the whole tag, so a comma-separated id list shares one level.

**Breaking for anyone using `validated-against:` — read this.** The role has sat in `ROLES` since the beginning with nothing consuming it, and both skill contracts described it as *"config/data (re-validated on change)"*. It is now the **validation** link: evidence the right thing was built, as opposed to `tested-by:`, which is evidence it was built correctly. Point a `layer: need` requirement at it. If your repo carries `validated-against:` tags under the old documented meaning, they will now be read as validation evidence and will satisfy the new need rule. Nothing breaks and no build fails — but the tags mean something different than they did, so re-read them before relying on the new warning.

The gate gains two warn-only rules, chosen as the two asymmetric mistakes the V-model actually warns about rather than as a strict layer-to-level table. A pairing table was rejected on evidence: this repo's `feature` requirements are unit-tested by direct function calls, which is a sound choice, and a rule that flags 36 of 40 requirements for practising something sound gets ignored within a fortnight. Instead — a confirmed `need` with no `validated-against:` link warns, and a confirmed `bus` requirement whose levelled links are all `@system` warns, because foundation code covered only end-to-end is slow, fragile, and localises failures poorly. Every other combination stays silent, including a `feature` tested end to end.

**Silent on arrival.** Both rules are opt-in and gated separately: the first holds back until your repo carries at least one `validated-against:` tag anywhere, the second until a given requirement carries at least one levelled link. An unlevelled `tested-by:` link is never judged. Neither rule can fire until you deliberately annotate something, so updating adds no warnings to any repo.

**Compatible in both directions.** `TAG_RE` already ignored a trailing `@level`, so an older vendored engine reads a levelled tag, resolves the id, and ignores the suffix. That property is now a binding acceptance criterion rather than an accident.

`show` prints the level beside a member whose tag carries one. New requirement `REQ-VLEVEL-037`, whose own tests are tagged `@unit` — the engine is the first consumer of its own vocabulary. `REQ-TRACE-020`'s blanket `need` exemption is narrowed to match, and `REQ-CHECK-006`'s severity table gains both warnings.

`MAP_ENGINE_VERSION` → `2026-08-17.1`.

## plugin `v2.15.0` — 2026-08-17

**Requirements are now written in plain present tense, and the linter enforces the reading level.** The corpus passed every clarity check the engine had while still being hard for a newcomer to read. That was not an accident: `LINT_SENTENCE_WORDS` sat at 35 and `LINT_CONTRACT_WORDS` at 30, roughly twice the level being aimed for, so `lint` reported **zero** findings on prose averaging 18.3 words per sentence. Rewriting the prose without moving those numbers would have let it drift straight back.

Contract clauses now name their subject (`` `init` creates the folder ``) instead of opening with an anonymous "It", drop `shall` in favour of a single **"Every line in this section is binding."** at the head of the section, and group under bold labels once past five clauses. `REQ-INIT-012` rewritten this way measures **10.8 words per sentence against 18.3, longest sentence 19 against 32, and no project term left undefined against twelve** — with all ten of its normative clauses intact. All 40 requirements in this repo were converted; no contract changed meaning, and the lock was advanced once with `sync --accept-drift`.

**Consumer-visible — thresholds tighten.** `LINT_SENTENCE_WORDS` drops 35 → 25 and `LINT_CONTRACT_WORDS` 30 → 22, so a repo that updates will see new warnings on prose it has not touched. They are warnings: `--strict` promotes only `ac-count-high` and `over-scoped` to errors, so **no consumer build breaks**. `SKILL.md` rule 3 now teaches the new voice instead of the `shall` convention, and both `REQUIREMENT_TEMPLATE` (what `new` writes) and the `draft`/`init` emission were rewritten to match, so generated files start compliant.

**Three linter changes came out of the migration, and two of them are fixes the old voice was hiding.**

- `stacked-conditions` no longer requires a `shall` or `must` on the line before inspecting it. Keyed on a magic word, it would have gone **silent** under the new voice without a single test failing. Removing the guard cost one additional finding across this corpus — a genuinely stacked clause in `REQ-HEALTH-017` that the keyed check had never been able to see.
- `over-scoped` now counts **scope units** rather than sentences: clause groups when a contract groups its clauses, clauses when it does not. Writing one obligation per bullet multiplies clauses without widening scope — `REQ-NEXT-013` went from 8 dense clauses to 21 atomic ones describing exactly the same command — so counting clauses alone punished the voice it was meant to serve.
- New `anonymous-subject` warning for a Contract clause opening with a bare "It" — 71 across this corpus when it was switched on. It reads physical lines, so a wrapped bullet whose continuation begins with "It " is flagged; rewriting the sentence is the fix, and `REQ-LINTCHECKS-025` records the limitation.

One rendering bug is fixed alongside: `_bullets()` treated a bold-only line as a hanging-indent continuation, so a clause group's label was folded into the previous group's last clause. That leaked into `show`, the map's contract rendering, and the bag of words behind `dupes` and `search` scoring.

`MAP_ENGINE_VERSION` → `2026-08-17`.

## plugin `v2.14.0` — 2026-08-08

**Requirement clarity is now enforced, not just documented.** `lint` mechanised the SKILL.md "Audience & writing level" rules, but nothing ever ran it — not CI, not the pre-commit hook — so 28 readability warnings had accumulated across the corpus unseen. `reqmap.py lint --strict` now runs in this repo's CI (`check_versions.py → gate → lint --strict → map --check → test_reqmap.py`) and in the shipped `hooks/pre-commit`, between the gate and the map-freshness check. **Consumer-visible:** a repo that installs the shipped hook now has commits blocked by error-severity lint findings (a `confirmed` requirement missing its Contract or Acceptance section) plus the `--strict`-promoted structural checks; style warnings stay advisory. The published `check@v1` GitHub Action gains a `lint` input running the same check, **on by default** like `freshness` — a check that must be opted into is documentation, not a check. It runs the consumer's own vendored `reqmap.py`, so it needs plugin v2.3.4 or newer (the release that added the `lint_exempt:` escape hatch); `lint: 'false'` skips it. Re-seed the engine in any repo below that floor before moving the `@v1` tag onto this commit.

The engine is untouched — no new checks, no new flags, `MAP_ENGINE_VERSION` unchanged. What changed is that the existing rules now execute.

The corpus was cleaned to pass: 25 prose findings rewritten across `REQ-SEARCH-036`, `REQ-REGISTRYLAG-035`, `REQ-NEXT-013`, `REQ-TESTLINK-018`, `REQ-INIT-012`, `REQ-FINDINGS-010`, `REQ-SIMILAR-016`, `REQ-REVIEW-022` and `REQ-PROMOTE-011` — long sentences and stacked `and`/`or` clauses split into atomic normative bullets, with rationale moved to each requirement's Notes section where it belongs. No contract changed meaning; the lock was advanced with `sync --accept-drift`. The two structural findings were resolved as documented exemptions rather than splits: `REQ-CHECK-006` (`ac-count-high`, `over-scoped`) is the gate's severity table, and every check it classifies already owns a separate requirement; `REQ-MEMBERDRIFT-027` (`ac-count-high`) has eight criteria that are the branch table of one decision. Both record the reasoning in their Notes, so the exemption is reviewable instead of silent.

## plugin `v2.13.0` — 2026-07-05

**Ranked requirement search — a `search` command and a shared viewer model.** Finding the requirement about a topic meant grepping `requirements/` (exact word, no ranking) or opening the map. The new `reqmap.py search "<query>"` ranks requirements by lexical relevance, most-relevant-first, reusing the same TF-IDF/cosine scoring (`REQ-SIMILAR-016`) that already powers `dupes` — zero new dependencies, gate/lock semantics untouched. Each hit prints its cosine score, and below a calibrated `0.05` floor it prints "No strong match" instead of a spurious top result — the floor sits far below the `0.35` dupes pair-threshold because a short query is a sparse vector, so query-vs-doc cosine runs lower than doc-vs-doc. The map viewer's search box now ranks by the **same** model (`app/src/lib/search.js`, a faithful port), replacing its substring filter, so the CLI (headless/agent/CI) and the viewer (human browsing) agree on what matches; the two runtimes are pinned to one model by a shared golden fixture asserted in both the Python `Search` tests and the viewer's SSR smoke. New requirement `REQ-SEARCH-036`.

`MAP_ENGINE_VERSION` → `2026-07-05`.

## plugin `v2.12.0` — 2026-07-04

**`health` now reports registry lag — commits since the requirements dir was last touched (RM-6, part 2).** `health` told you whether the requirements that exist are coherent, but not whether the registry as a whole had gone stale while code moved on — a consumer's registry sat frozen for 18 days across ~40 code commits while a money value drifted, and nothing surfaced it. `health --json`/print now carry `commits_since_req_touch`, a read-only git-derived count (last commit touching `reqs_dir` → `HEAD`), printed only when non-zero. It is the temporal complement to the untagged-code coverage signal: coverage asks "is this code traced?", lag asks "has the registry moved lately at all?". Advisory only — never a gate, never lowers the score, and absent (not zero) when unmeasurable (no git / no code root / `reqs_dir` untracked). New requirement `REQ-REGISTRYLAG-035`.

## plugin `v2.11.1` — 2026-07-03

**Repos can declare extra scannable extensions (`REQMAP_EXTRA_CODE_EXTS`).** The scanner
looks at a fixed set of source extensions (`CODE_EXTS`). A repo whose source language isn't in
that set had its capability tags go invisible — the file read as un-covered, and a confirmed
requirement whose only implementation lived in such a file failed the gate with "no
`implements:` member" even when correctly tagged. The new `REQMAP_EXTRA_CODE_EXTS` env var
(comma-separated, leading dot optional, e.g. `.foo,bar`) merges extra extensions into
`CODE_EXTS` at load, so any repo can extend the scan set without forking the engine. Additive;
unset = unchanged behaviour.

## plugin `v2.11.0` — 2026-07-03

**`health` can no longer read 100/clean while `gate` has link-sync errors (RM-6).** A
downstream consumer repo's `health` reported 100/100 for 18 days while `gate` sat on 14
unwired link-sync errors — `gate` was never wired into that repo's CI, so nobody saw it, and
`health`'s own score never reflected `gate`'s state at all. `health --json`/`--badge`/print now
carry `gate_errors` (count) and `gate_link_sync_clean` (bool), computed by a new shared
`_link_sync_errors()` helper mirroring `gate`'s own two ERROR-level checks (dangling tags,
enforced-status requirements with no `implements:` member). Purely additive — the `score`
formula is untouched, same idiom as the existing `untagged` signal. The badge can no longer
show `brightgreen` while `gate` would fail; it turns `red` with a `gate:N` suffix instead.

**What this deliberately does NOT fix:** a value changed in a file carrying no membership tag
at all (the actual shape of the incident that motivated this — an unsourced monetary-constant
edit) produces neither a dangling reference nor a missing-`implements` error, so it stays
invisible to this signal; pinned by a dedicated test. Closing that gap needs a sourced /
`validated-against:`-staleness convention, deliberately out of scope here — Senate run
`reqmap-health-gate-cleanliness` (verdict `GO_WITH_CONDITIONS`) rejected folding it into this
change, citing a 2026-06-21 precedent (`reqmap-enforce-all-code-has-requirements`,
`DEEPLY_SPLIT`) against granting `gate` new blocking authority without its own deliberation.

`MAP_ENGINE_VERSION` → `2026-07-03`.

## plugin `v2.8.1` — 2026-06-26

**Fix: member-hash line-ending normalization (CRLF/Windows).** `_file_sha` hashed member
files as raw bytes, so a `_memberlock.json` generated on a CRLF working tree (Windows,
`core.autocrlf=true`) did not match one verified on LF (Linux/CI) — every member showed
spurious drift. Harmless as a warning, but `gate --strict` (added in 2.8.0) escalated it to
a wall of false errors. Now line endings are folded to LF before hashing, matching the
contract hash (already LF-normalized via the text-mode body parse). LF-only repos are
unaffected (their hashes don't change); `REQ-MEMBERDRIFT-027` +AC-8. `MAP_ENGINE_VERSION`
→ `2026-06-26.1`.

## plugin `v2.8.0` — 2026-06-26

**Gate hardening — close the stale-map / uncommitted-lock blind spot.** A consumer repo
hit a recurring member-drift that the gate never caught: CI ran only the link-sync `gate`
(stale map / drift exit 0) and the `_memberlock.json` baseline was generated but never
committed. Three fixes so this can't recur for any consumer:
- The published action (`check/action.yml`) now runs **`map --check`** after the gate by
  default (new `freshness` input, default `true`) — a stale or never-committed map/lock
  fails CI instead of merging unseen. A repo that tracks no map passes silently. New
  `reqmap-repo` input pins `REQMAP_REPO` for a repo whose committed map targets a different
  slug (e.g. a private repo publishing to a public mirror); it is exported only when
  non-empty, since an empty value means "emit no repo" to the engine. The default hook/CI
  examples in `SKILL.md` gain the `map --check` line too.
- **Untracked-lock warning** (`gate`): a `_reqlock.json` / `_memberlock.json` present on disk
  but not git-tracked is now a `WARN` naming the file — the exact gap that silently disables
  drift detection on a fresh checkout. Fail-open (silent when git is unavailable).
- **Test-link detector** now recognizes a Python suite that drives its checks from a
  `run` / `run_tests` / `main` entry point under an `if __name__ == "__main__"` guard, not
  only `def test…`. A stdlib-only harness no longer false-negatives the test-link integrity
  check — that false error was what blocked `gate --strict` on such corpora.

`MAP_ENGINE_VERSION` → `2026-06-26`.

## plugin `v2.3.1` — 2026-06-16

**License correction.** `plugin/.claude-plugin/plugin.json` declared `"MIT"` while
the `LICENSE` file and README are Business Source License 1.1 — corrected to the
SPDX id `"BUSL-1.1"`.

**excalidraw-diagram — adaptive multi-layer posters (one file).**
- The "Diagramming a repo's architecture" recipe is now **adaptive**: a table of
  six layer-types (STRUCTURE / WORKFLOW / INTEGRATION / MODES / MODEL / DATA) each
  with an "include when…" condition. The author picks which layers the repo needs
  and emits them ALL as stacked sections in ONE file, with one legend that decodes
  every layer (colour-per-distinct-role discipline documented).
- **`discover` now scaffolds that poster**: a live STRUCTURE layer (`section()` +
  sized `grid()`, all four `save()` gates at `"error"`) plus commented scaffolds
  for the five optional layers. The generated stub also carries a **portable
  import** (builder next to the stub / on PYTHONPATH, else newest plugin-cache
  build) so it runs from any repo. New regression test locks the stub shape.
- **Richer-by-default, with guardrails.** Multi-tool repos (2+ skills/services
  with distinct flows) now get one labelled `s.lane()` per tool in the WORKFLOW
  layer instead of a single pipeline that hides the others; single-tool repos
  keep one pipeline. A "depth comes from structure, never from cramming" rule
  subordinates elaboration to the existing readability gates (≤20 nodes/region,
  short labels, simplicity-first always win). The `discover` scaffold shows the
  per-tool lane pattern; a ❌→✅ worked example contrasts it with the thin one.

**excalidraw-diagram — C4 removed + docs overhaul.**
- **Removed the C4 helpers** (`Scene.c4()` and `Scene.person()`). They were
  undocumented and pulled the skill toward formal C4 notation; the canonical
  poster (`examples/make_full_architecture.py`) now uses plain role-coloured
  `box()`es. ISO 5807 flowchart shapes are unaffected.
- **SKILL.md restructured for its purpose** — a "The goal" statement up front, a
  "Diagramming a repo's architecture" recipe pointing at
  `make_full_architecture.py`, a "Worked examples — ❌ → ✅ variants" section
  (repo poster, pipeline, parallel agents, decision flow, feedback loop), and the
  box-sizing guidance softened to lean on the `overflow_check` gate.
- **Doc↔code drift closed.** The cheat-sheet and `references/excalidraw_format.md`
  now document the previously-undocumented public API the examples rely on
  (`section()`, `pipeline()`, the ISO shapes, `path()`, `glossary()`), the full
  `Scene()` signature, all four `save()` gates (`crossing_check`, `legend_check`,
  `overflow_check`, `text_overlap_check`), and `check_text_overflow()` /
  `check_text_overlaps()`.

**Audit follow-up (4-lens Consilium audit) — intent-verb propagation + diagram publish.**
- **Stale CLI names swept.** The intent-verb rename (`check→gate`, `promote→confirm`,
  `extract→draft`, `candidates→plan`, `similar→dupes`, `promote-todo→new --from-todo`)
  is now propagated everywhere it had been missed: the published site
  (`docs/architecture.html`), the engine's own module docstring and scaffold
  `SITE_TEMPLATE`, and six requirement files (`REQ-PROMOTE-011`, `REQ-EXTRACT-008`,
  `REQ-CANDIDATES-009`, `REQ-SIMILAR-016`, `REQ-PROMOTE-TODO-001`, plus stale `check`
  references in `REQ-CHECK-006` / `REQ-ACVERIFY-019` / `CORE-DRIFT-003`).
- **Site truth-up.** `docs/architecture.html` showed `v1.16` (now `v2.3.1`) and
  "All 15 commands" (now 18, with the missing `sync` / `site` / `review` cards added).
  README gains the `site` and `review` rows; the `~3200 lines` engine figure is now `~3700`.
- **Diagram published.** The complete-architecture poster is committed at
  `docs/full_architecture.html` and linked from the site nav (`Diagram ↗`), so it
  resolves on GitHub Pages instead of 404-ing (it had pointed at gitignored `diagrams/`).
- **Engine fixes.** `sync --strict` now forwards the flag to the gate (it was silently
  dropped); `REQ-MAP-007`'s contract documents the `todos` key emitted in `_map.json`;
  the narrower file-type scope of `draft` (vs the gate's full scan set) is documented.

reqmap engine touched (the `sync --strict` fix + docstring/template) → `MAP_ENGINE_VERSION`
advances to `2026-06-16`.

---

## plugin `v2.3.0` — 2026-06-15

**excalidraw-diagram — text-overflow gates.** Two silent failure classes the
shape-only overlap check missed — bound text wider than its box (label spills
out) and two free captions/headers colliding — now have `check_text_overflow()`
and `check_text_overlaps()` checks plus a `fit_text()` wrap-and-size helper.
`save()` gains `overflow_check` / `text_overlap_check` (warn by default, error
opt-in); `box()` defaults are unchanged so existing layouts don't re-flow. The
new per-example assertions caught real bugs (widened a box in
`make_full_architecture.py`, fixed caption pitch in `make_explainer.py`, retired
the superseded `make_repo_map.py`). reqmap engine unchanged; `MAP_ENGINE_VERSION`
stays `2026-06-15`.

---

## plugin `v2.2.0` — 2026-06-15

**excalidraw-diagram — ISO 5807 shapes, C4 helpers, poster helpers.** Additive
builder expansion:
- **ISO 5807 flowchart shapes** — `process`, `terminator`, `decision`, `data`
  (parallelogram), `predefined_process`, `preparation` (hexagon), `connector`
  via `box(shape=…)` + convenience methods (polygons drawn as closed lines with
  bbox geometry).
- **C4 model helpers** — `person()` + `c4()` (name / [kind: tech] / description);
  later removed in v2.3.1.
- **Poster helpers** — `section()` (auto-stacked labelled regions) and `pipeline()`
  (auto-spaced, mid-aligned, auto-chained horizontal flowchart).
- **Examples consolidated** to four maintained, test-covered generators
  (`make_full_architecture.py`, `make_explainer.py`, `make_repo_map.py`,
  `make_iso5807_flowchart.py`); retired the overlapping `make_architecture.py`
  and `gen_reqmap_workflow.py`. `diagrams/` output convention documented
  (gitignored, regenerable). reqmap engine unchanged; `MAP_ENGINE_VERSION` stays
  `2026-06-15`.

---

## plugin `v2.1.1` — 2026-06-15

**Audit follow-up (Consilium Trias).** Fixes from a multi-lens audit of the v2.1.0 excalidraw CLI branch:

- **Stale doc references removed.** `README.md` no longer points to the deleted `docs/plugin_architecture.html`; the `SITE_TEMPLATE` comment in `reqmap.py` no longer cites the removed `docs/reqmap_site_prototype.html` (the template is now the canonical source).
- **`render` hardening.** `render_html()` now rejects a scene whose `elements` is a list of non-objects (e.g. `[1, 2, 3]`) instead of writing a viewer that silently fails to render.
- **excalidraw-diagram menu.** The "how to start a diagram" menu gains the missing day-2 path (**re-run / extend your generator**) and a **self-test** entry, each with a when-to-pick-it clause.
- **Tests.** Wrapped three unclosed file handles in the CLI test helpers (no more `ResourceWarning`); added coverage for the `discover` `max_components` truncation path and the non-object-`elements` rejection.

reqmap engine behaviour unchanged (comment-only edit); `MAP_ENGINE_VERSION` stays `2026-06-15`. SRI hashing of the viewer's CDN tags was identified in the audit but deferred — it needs verified per-asset `sha384` hashes (a wrong hash breaks every generated viewer).

---

## plugin `v2.1.0` — 2026-06-15

**excalidraw-diagram CLI.** Two helper verbs on `excalidraw_builder.py` — the authoring path stays Python (no declarative `build <spec>` verb, which would fork a second, divergent format):

- **`render <scene.excalidraw> [out_dir]`** — rebuild the self-contained `.html` viewer from an existing scene file (e.g. one edited on excalidraw.com, where there is no generator script to re-run).
- **`discover <repo> [out.py]`** — scan a repo and emit a runnable Python generator stub (`make_diagram.py`): one box per top-level component on a no-overlap grid, with `TODO`s for the arrows/grouping you fill in, then run it to produce the scene + viewer.
- No-arg `python excalidraw_builder.py` still runs the builder self-test (unchanged — CI relies on it).

reqmap engine unchanged; `MAP_ENGINE_VERSION` stays `2026-06-15`.

---

## plugin `v2.0.0` — 2026-06-15

**Breaking — intent-verb CLI.** Commands renamed to match what the user wants:

| Old | New |
|---|---|
| `check` | `gate` (report-only) — **kept as a deprecation alias**, removed next major |
| `scan` + `check --update-lock` + `map` | `sync` (composite; `--accept-drift` to advance an edited confirmed baseline) |
| `extract` | `draft` |
| `promote` | `confirm` |
| `candidates` | `plan` |
| `similar` | `dupes` |
| `promote-todo "x" --id ID` | `new --from-todo "x" --id ID` |

- **No consumer breakage:** `check` still runs (prints a deprecation notice, forwards to the legacy path), so vendored pre-commit hooks, CI, and the `check@v1` Action keep working. Migrate at leisure: `check`→`gate`, the trio→`sync`.
- **`sync` drift guard:** `sync` refuses to silently re-baseline an edited `confirmed`/`implemented` contract — it prints the changed hashes and exits non-zero unless you pass `--accept-drift`.
- **`gate` is report-only:** it never touches `_reqlock.json`; use `sync` to advance the baseline.
- Requirement IDs are unchanged (`REQ-PROMOTE-011`, `REQ-SIMILAR-016` keep their slugs — only the CLI verb + prose changed).

### Migration
`extract`/`promote`/`candidates`/`similar`/`promote-todo` are removed (no alias) — they do not appear in consumer CI. Update your own scripts: `sed -i 's/reqmap.py check/reqmap.py gate/' <hook>`. `MAP_ENGINE_VERSION` is `2026-06-15`.

---

## plugin `v1.35.0` — 2026-06-14

The `site` command — keep a project presentation page in sync with the registry. Highlights:

- **`site` command** — `reqmap.py site --attach <page.html> [--regions nav,stats]` injects engine-owned, marker-delimited regions into a presentation page and **preserves the authored prose between them**. `nav` = Live Map / Diagram / GitHub links (from `git remote` + artifact paths, each emitted only when its target resolves); `stats` = requirement / confirmed / layer / edge counts + engine version (from `_map.json`). When the `--attach` target does not exist, `site` scaffolds a full self-contained default page with a placeholder hero (`<!-- author me -->`).
- **Two layers** — the engine is deterministic and headless-safe (never prompts); the `requirement-manager` skill is the interactive front door (`site --detect` → ask which target + regions → call the engine). The engine only *links* an Excalidraw diagram — it never generates one (the `excalidraw-diagram` skill stays independent of `reqmap.py`).
- **`init` integration** — `init` runs a best-effort `site` pass (`nav,stats` into `docs/architecture.html`, scaffolding it plus a GitHub Pages signal — `.nojekyll` + an `index.html` redirect — when absent). Opt out with `reqmap.py init --no-site`; a failure in the step never aborts `init`.
- **`map --check` gate** — flags the page stale when its `stats` region drifts from a fresh render; the `nav` region is exempt (it embeds the fork-specific repo URL, like the `repo` field excluded from `_map.json`). A page with no `stats` marker — or one never generated — is not stale. Reuses the `REQ-PAGES-021` Pages-publish path.
- **New requirement `REQ-SITE-026`** + 14 new `Site` tests (idempotency, prose preservation, no-remote degradation, scaffold mode, region-only staleness, HTML-escaping, CLI dispatch, excalidraw independence).

### Upgrade notes
Re-seed consumer repos with `scripts/reqmap.py` only — the scaffold page is an inline template, so no new vendored file is required. `MAP_ENGINE_VERSION` is `2026-06-14`.

---

## plugin `v1.11.0` — 2026-06-04

First feature release since `v1.0.0`. Highlights:

- **Self-contained HTML viewer** — `map` now emits `requirements/_map.html`: a single-file React app with your real requirements inlined, double-click to open, no server or npm needed. Tabs: System Map, Risk, Dependencies, Spec. Main-bus layout ranks nodes by dependency depth (`bus` nodes on the right, consumers on the left); color-coded, selectable edges; grab-to-pan. Fixed: viewer used to render only its bundled demo fixture — all graph tabs now compute layout from the live registry.
- **`init` command** — one-shot bootstrap: scaffolds `requirements/` + `.reqmapignore`, drafts requirements from existing code, builds the lock + map, prints guided next steps. Idempotent; `--wipe` for a hard reset (strips all tags + deletes non-generated files before re-extracting).
- **`next` command** — terminal "what should I do next": a progress header then the Risk tab's actionable buckets most-urgent-first (Orphans · Needs tests · Needs intent review · Drafts to review). Read-only, always exit 0.
- **`promote` command** — human validation step: flips a reviewed requirement's `status` to `confirmed`. Refuses if it has no `implements:` member; warns if no `tested-by:` is linked.
- **`findings` command** — aggregates open `## WHAT — Verify intent` items across all requirements into `requirements/_findings.md`; accepts an AI-triage sidecar (`_findings_triage.json`) for a classified view.
- **`export` command** — emits `requirements/_map.json` (or `--out PATH` / `--out -`) for feeding an external front-end.
- **Intent triage skill action** — 5th menu item in the `requirement-manager` skill for AI-assisted triage of open verify-intent findings.
- **Prose capability discovery** — `extract`/`init` scan `.md`/`.html` by default and classify each prose file into three buckets: ignore (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), or capability-source (prompts/specs auto-drafted as `draft` stubs).
- **`candidates --md-glob`** — read-only extraction plan from prose/spec markdown (advisory, writes no `.md`).
- **Risk signals** — `untested` (has `implements` but no `tested-by:`) and `unverified-intent` (open verify-intent item) surfaced on the Risk tab, `_map.md` table, and detail panel. Silence per-requirement with `test_exempt: <reason>` in frontmatter.
- **`map --check`** freshness gate — exits non-zero if committed `_map.*` is stale; wire alongside `check` in pre-commit/CI.
- **`check --update-lock` auto-runs `map`** — lock and map stay in sync in one command.

### Upgrade notes
Re-seed consumer repos with both `scripts/reqmap.py` **and** `scripts/_map_viewer.html` — the viewer template is new and required for `_map.html` emission. Use `sync_reqmap.sh` or the skill's "update engine" action.

---

## engine `1.11.0` — 2026-06-04

- **Fixed — viewer rendered only its demo fixture**: the `_map.html` graph tabs
  positioned nodes through hardcoded coordinate maps keyed to the bundled sample ids,
  so any real repo's requirements were filtered out and the canvas was blank (registry
  counts were correct, masking it). The System Map, Risk and Dependencies tabs now
  **compute their layout from the live registry** — they render any repo's data.
- **Added — layered "main-bus" layout** (`app/src/lib/layout.js`): nodes are ranked by
  dependency depth so `depends_on` flows left→right (consumers left, shared
  foundation/`bus` nodes right), a barycenter pass minimises edge crossings, and
  edge-less nodes are parked in a side grid.
- **Added — colour-coded, selectable edges**: each dependency edge (arrowhead included,
  via `context-stroke`) is drawn in its source requirement's colour, so overlapping
  lines stay traceable; cards are kept neutral. Click a line to isolate it — it goes
  bold, the rest dim, and its two endpoints are ringed, so `x → y` is unambiguous.
- **Changed — card-avoiding orthogonal routing**: edges run their verticals in the
  inter-column gutters and cross any intermediate column only through a gap between its
  cards, so a line never passes through a card it doesn't connect to (no more
  "x → y → z through a node" look). Rounded right-angle turns.
- **Added — grab-to-pan**: drag anywhere on a map canvas to pan it (no need for the
  scrollbars); a plain click (no drag) still selects a node or edge.
- **Fixed — "center & highlight" button**: it set the highlight but never scrolled; it
  now `scrollIntoView`s the highlighted node.
- **Fixed — `_build_json` area**: emits the ID-prefix fallback (`_area_of`) when a
  requirement has no explicit `area:`, matching the Mermaid path's grouping so the
  JSON graph carries a usable `area` for external front-ends.

## engine `1.10.0` — 2026-06-04

- **Added — React front-end (`app/`)**: the four product surfaces (Map · Problems ·
  Console · Spec) as a real Vite + React app, recreated from the design system. Run
  with `cd app && npm run dev` (dev server pinned to port 5173 via `--strictPort`).
- **Added — `export` command**: `reqmap.py export` emits the registry graph as
  `requirements/_map.json` (`{engine_version, nodes, edges}`) — to stdout (`--out -`),
  a path (`--out PATH`), or the default file — for an external front-end to consume.
- **Added — self-contained viewer (`_map.html`)**: `map` injects this repo's graph
  into a pre-built single-file React viewer (`scripts/_map_viewer.html`, carrying a
  `<!--REQMAP_DATA-->` marker) → a double-click-openable `requirements/_map.html`,
  no server, no npm. Emitted only when the template is vendored beside the engine;
  the injected data is escaped (`</` → `<\/`) against script-breakout. `_map.html` is
  regenerable and gitignored.
- **Behavior change — engine no longer hand-generates HTML**: `render_html` and the
  inline HTML template were removed; `map` now writes `_map.md` + `_map.json`
  (+ `_map.html` from the viewer template when present). The freshness gate
  (`map --check`) now covers `_map.md` + `_map.json`. Re-seed consumer repos with both
  `scripts/reqmap.py` and `scripts/_map_viewer.html` (see SKILL setup / `sync_reqmap.sh`).

## engine `1.8.0` — 2026-06-03

- **Added**: `extract`/`init` now discover prose capabilities (`.md`/`.html`) by
  default, classified by `classify_prose` into three buckets — ignore
  (meta/boilerplate), sync-only (`README*`, `docs/`, `*.html`), and
  capability-source (prompts/specs). Capability-source prose is auto-drafted as a
  `draft` stub from its title + `##` headings (`_prose_facts`). An advisory
  doc-sync step is emitted in the skill for sync-only docs tagged `generated-from`.
- **Behavior change**: on first post-upgrade `init`/`extract`, repos with
  prompt/spec markdown will see new `draft` requirements. Drafts are NOT enforced
  by the gate (`draft` is not in `ENFORCED`), so this cannot break an existing
  `check`. Review, edit, and `promote` the real ones; delete the rest.
  README/docs/HTML and meta files (`CLAUDE.md`, `SKILL.md`, `TODO.md`,
  `CHANGELOG.md`, `LICENSE*`) are never auto-drafted.

## engine `1.5.0` — 2026-06-03

- **`reqmap.py promote <ID>`** — one-command human-validation step: flips a reviewed
  requirement's `status` to `confirmed` via a single frontmatter edit (preserves
  indentation + trailing comment, body untouched). Refuses when the requirement has
  no `implements:` member (a confirmed requirement must point to code, else the gate
  errors); warns when no `tested-by:` is linked; idempotent on an already-confirmed
  requirement. Dogfooded as `REQ-PROMOTE-011`.
- **owner standardized** to `Alex` across the repo's own requirements + the scaffold
  default (`extract` still emits `owner: auto` for machine-drafted, unreviewed files).

## engine `1.4.0` — 2026-06-03

Drift gates to prevent the version/map skew that slipped past in 1.3.x.

- **`reqmap.py map --check`** — freshness gate: regenerates the map in memory and
  compares it to the committed `_map.html`/`_map.md` (ignoring the volatile
  `generated:` timestamp), exiting non-zero if stale. A map that was never generated
  passes (consumers who don't track maps are unaffected). Wired into the shared
  pre-commit hook and CI so a code/requirement edit that shifts the map can't be
  committed without regenerating it.
- **`check_versions.py --fix`** — propagates `plugin.json`'s version into every
  `marketplace.json` occurrence, so a bump is one edit + one command instead of three
  hand-edits (the exact drift that failed CI in 1.3.0).
- **dev pre-commit hook** (`.githooks/pre-commit`, enable with
  `git config core.hooksPath .githooks`) — runs version coherence + the drift gate +
  map freshness locally, before CI.

## engine `1.3.0` — 2026-06-03

Non-code capability discovery + corpus-health visibility (`MAP_ENGINE_VERSION` 2026-06-03).

- **`candidates --md-glob`** — discover capabilities in authoritative **non-code** files
  (prompt/spec markdown), advisory-only and allowlist-bounded. Off unless a glob is
  given; writes no `.md`. A new `_md_facts()` extractor pulls the H1 title, the first
  blockquote after it (intent), and `## ` H2 headings (no parser). The plan now carries
  `coverage_summary {total_candidates, with_existing_req}` and a `lineage_note` so an
  unfilled plan can't masquerade as coverage, and so a `generated-from`/`implements`
  tag is understood as authoring lineage — not auto-tracking of later source edits.
- **`.md` added to the scan extensions** so prose capabilities can carry membership
  tags (`<!-- implements: ID -->`). The drift hash still anchors only on the authored
  Contract+Acceptance, so source prose may drift freely.
- **`check` health line** — the summary now reports `(N confirmed, M legacy-schema)`,
  and legacy-schema requirements (no `## WHAT — Verify intent` section, for which
  `findings` is silently inactive) are flagged with a non-blocking WARN. Makes an
  all-baseline corpus (gate enforces nothing yet) and an inactive `findings` visible.
- **`extract`** now annotates the emitted `risk:` field as an author triage hint that
  the engine does not read.
- **map risk signals** — two new signals surface on the Risk tab + `_map.md` table +
  detail panel: `untested` (a requirement with an `implements` member but no
  `tested-by`), suppressible per-requirement with a `test_exempt: <reason>` frontmatter
  field; and `unverified-intent` (a requirement with an open `## WHAT — Verify intent`
  item). Both reuse the existing risk machinery.
- **map zoom-fit fix** — diagrams now fit their container on first open *and* on every
  tab switch. Fit is measured after layout (double `requestAnimationFrame`, zero-size
  guard) and centered, with a capped modest upscale (`FIT_MAX`) so small diagrams fill
  the pane without over/under-zooming.

## check action `v1.0.0` — 2026-06-03

First published release of the `requirement-manager` CI action. Run the drift gate
on every push and PR without copying YAML boilerplate into each repo.

### Usage
```yaml
# .github/workflows/reqmap.yml
name: reqmap gate
on: [push, pull_request]
permissions:
  contents: read            # least privilege — the gate only reads the tree
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: alxmax/requirement-manager/check@v1
```

### Inputs (optional)
| input | default | purpose |
|---|---|---|
| `reqmap-path` | `scripts/reqmap.py` | path to your vendored engine, relative to `working-directory` |
| `working-directory` | `.` | directory the gate runs from (where `requirements/` lives) |
| `python-version` | `3.x` | Python to set up (engine is stdlib-only — any 3.x works) |

### What it enforces
`reqmap.py check` — link sync (every code tag points to a real requirement; every
confirmed requirement has ≥1 member), content drift vs. the lock, and `depends_on`
target existence. Fails the build on any violation.

### Notes
- **Versioning:** pin to `@v1` (moves with backward-compatible fixes) or to `@v1.0.0`
  / a commit SHA for exact reproducibility. The action ref is independent of the
  plugin/PyPI semver.
- **Scope:** the vendored-copy staleness notice (`warn_if_stale`) is gated on
  `CLAUDE_PLUGIN_ROOT`, unset in CI — silent and exit-neutral there by design.
- **Security:** keep `permissions: contents: read` in the caller workflow; the gate
  needs no secrets and no write scope.
