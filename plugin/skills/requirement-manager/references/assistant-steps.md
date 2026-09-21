# Assistant steps the engine does not do

Part of the `requirement-manager` skill; [SKILL.md](../SKILL.md) links here.

**Advisory doc-sync (assistant step, not the engine).** After `map`, for each
sync-only doc (bucket 2) tagged `generated-from: <ID>`, the assistant reads the doc,
its requirement(s), and the implementing code, then reports concrete mismatches
(e.g. "the HTML says quorum 6/9; the code says 7/9"). This is judgment, not a gate —
it surfaces findings and never blocks a commit. The engine's deterministic drift
flag (stale-on-change) is the hard half of doc-sync; this is the semantic half.

**Advisory clarify answers (assistant step, not the engine).** `clarify` counts; it
does not read. Its own output says so — *"there are 6 clauses and 5 cases. This check
counts, it does not read, so it cannot say WHICH — that is the part only you can do."*
That last sentence is this step's whole job. Whenever an open question reaches the user
— from `clarify <ID>`, or from the buckets in `gate --risk` — the assistant does not
relay the engine's wording. It reads the requirement, then answers in two parts:

1. **One synthesized question.** Name the specific thing that is undecided, in the
   requirement's own vocabulary. `clarify` can only say "1 clause has no case"; you
   have read the clauses, so say which one and what about it is unproven. Several
   engine findings that turn out to be the same ambiguity become one question, not
   three — and a finding you checked and found already answered is reported as
   answered, not repeated.
2. **2–4 concrete answer options**, presented with `AskUserQuestion`. Each option is
   a candidate resolution the user can pick and you can then write — "add CASE-6
   asserting X", "fold clause 4 into CASE-2", "move clause 4 to [[OTHER-ID]], which
   already proves it" — never a restatement of the question and never "clarify this".
   Say what each option costs and what it gives up, and put your recommendation
   first. If you genuinely cannot see two defensible resolutions, ask the plain
   question instead of padding the list to two.

Then write the picked option into the requirement and re-run the command, so the
question disappears because it was answered rather than silenced. This never writes a
`lint_exempt` — an exemption is the thing this step exists to avoid reaching for.
It is judgment, not a gate: it reports and asks, and blocks nothing.
