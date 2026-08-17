---
id: REQ-DOCBUNDLE-026
status: confirmed
layer: feature
owner: Alex
priority: should-have
depends_on: [REQ-CHECK-006, CORE-SCAN-002]
superseded_by:
milestone: v1.17
---

# Untagged doc-bundle warning

> A whole-system doc — an architecture or explainer page generated from many
> requirements — can drift from those requirements for days with nothing linking
> the two, because a `generated-from:` tag was never added. Drift detection only
> fires through the tags it can see, so an untagged bundle is a silent blind spot.
> This surfaces the gap: the gate names a large `docs/` HTML doc that carries no
> lineage tag, so the author either links it (one tag, possibly a multi-id list)
> or marks it intentionally out of scope. Without it, "the docs are in sync" is an
> assumption the gate can neither confirm nor deny.

## WHAT — Contract (normative)
Every line in this section is binding.
<!-- Words used below, in plain terms:
     a doc bundle       a whole-system page written out of many requirements at once,
                        such as an architecture or explainer page.
     a lineage tag      a `generated-from:` comment naming the requirements a doc
                        was built from.
     the scan walk      the shared file walk every command uses. -->

**What it warns about**
- The gate warns for each file under `docs/` ending in `.html` that carries no
  `generated-from:` member tag, once that file is at least `DOC_BUNDLE_MIN_BYTES`
  in size.
- The gate considers only files under `docs/`.

**What it skips**
- The check skips engine-generated outputs: a file whose basename starts with `_`,
  and the published `map.html` viewer.
- The engine owns those two and freshness-checks them separately.
- The check honors `.reqmapignore` and the standard scan walk, so a repo can mark a
  regenerable artifact out of scope rather than tag it.
- The scan walk prunes `.git`, `node_modules`, `__pycache__` and the SSOT
  `requirements/` directory.
- The check skips a file it cannot read.

**Severity**
- The check is warn-only and never changes the gate's exit code.

## WHAT — Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## WHAT — Notes & known limitations (informative)
- A byte-size threshold is a deterministic proxy for "generated bundle", not a
  semantic one: a large hand-authored doc that legitimately has no requirement
  lineage is silenced via `.reqmapignore`, not by the check guessing intent.
- It asserts a lineage tag is *present*, not that the doc's content actually matches
  the requirements it names — the same lexical-trust limitation as `tested-by`.

## HOW — Acceptance (= tests)
AC-1
  Given  a `docs/` HTML file at or above the size threshold with no `generated-from:` tag
  When   the scan runs
  Then   the file is reported as an untagged doc bundle
AC-2
  Given  a `docs/` HTML file below the size threshold
  When   the scan runs
  Then   it is not reported
AC-3
  Given  a large `docs/` HTML file that carries a `generated-from:` tag
  When   the scan runs
  Then   it is not reported
AC-4
  Given  a large engine output (`_`-prefixed or `map.html`) or a large `.html` outside `docs/`
  When   the scan runs
  Then   none of them are reported
AC-5
  Given  a large untagged `docs/` HTML file matched by a `.reqmapignore` pattern
  When   the scan runs
  Then   it is not reported
AC-6
  Given  a large untagged `docs/` HTML file
  When   the gate runs
  Then   its output names the file and the missing `generated-from:` tag

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana generates `docs/architecture.html` from a dozen requirements but forgets a
  lineage tag. `reqmap.py gate` warns that the bundle has no `generated-from:` tag.
  She adds `<!-- generated-from: CORE-PARSE-001, CORE-SCAN-002, REQ-MAP-007 -->`, and
  from then on a contract drift in any of those three lists the doc to re-sync.

## WHERE — Current implementation
- `untagged_doc_bundles`, `DOC_BUNDLE_MIN_BYTES` in `reqmap.py`, consumed by `cmd_check`
  — `untagged_doc_bundles` walks the code root (honoring `.reqmapignore`) for large
  `docs/*.html` files absent from the `generated-from:` member set and skipping engine
  outputs, and `cmd_check` emits one warn-only line per result.

## Links
- Used by: (auto)
## Members in code (auto)
