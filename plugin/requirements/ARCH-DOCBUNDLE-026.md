---
id: ARCH-DOCBUNDLE-026
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v1.17
depends_on: [ARCH-CHECK-006, ARCH-SCAN-002]
satisfies: [SYS-GATE-102]
---

# Untagged doc-bundle warning

## Description
> A whole-system doc — an architecture or explainer page generated from many
> requirements — can drift from those requirements for days with nothing linking
> the two, because a `generated-from:` tag was never added. Drift detection only
> fires through the tags it can see, so an untagged bundle is a silent blind spot.
> This surfaces the gap: the gate names a large `docs/` HTML doc that carries no
> lineage tag, so the author either links it (one tag, possibly a multi-id list)
> or marks it intentionally out of scope. Without it, "the docs are in sync" is an
> assumption the gate can neither confirm nor deny.

Every bullet below is binding.
- The gate warns, without affecting its exit code, for each `docs/*.html` file at least `DOC_BUNDLE_MIN_BYTES` in size carrying no `generated-from:` tag — skipping engine outputs, `.reqmapignore`-matched files, and anything outside `docs/`. [[REQ-DOCBUNDLE-840]] details the behaviour.

## Cases
CASE-1
  Given  a `docs/` HTML file at or above the size threshold with no `generated-from:` tag
  When   the scan runs
  Then   the file is reported as an untagged doc bundle
CASE-2
  Given  a `docs/` HTML file below the size threshold
  When   the scan runs
  Then   it is not reported
CASE-3
  Given  a large `docs/` HTML file that carries a `generated-from:` tag
  When   the scan runs
  Then   it is not reported
CASE-4
  Given  a large engine output (`_`-prefixed or `map.html`) or a large `.html` outside `docs/`
  When   the scan runs
  Then   none of them are reported
CASE-5
  Given  a large untagged `docs/` HTML file matched by a `.reqmapignore` pattern
  When   the scan runs
  Then   it is not reported
CASE-6
  Given  a large untagged `docs/` HTML file
  When   the gate runs
  Then   its output names the file and the missing `generated-from:` tag

## Context
**Terms**
- a doc bundle       a whole-system page written out of many requirements at once,
- such as an architecture or explainer page.
- a lineage tag      a `generated-from:` comment naming the requirements a doc
- was built from.
- the scan walk      the shared file walk every command uses.

**Notes**
- A byte-size threshold is a deterministic proxy for "generated bundle", not a
  semantic one: a large hand-authored doc that legitimately has no requirement
  lineage is silenced via `.reqmapignore`, not by the check guessing intent.
- It asserts a lineage tag is *present*, not that the doc's content actually matches
  the requirements it names — the same lexical-trust limitation as `tested-by`.

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana generates `docs/architecture.html` from a dozen requirements but forgets a
  lineage tag. `reqmap.py gate` warns that the bundle has no `generated-from:` tag.
  She adds `<!-- generated-from: ARCH-PARSE-001, ARCH-SCAN-002, ARCH-MAP-007 -->`, and
  from then on a contract drift in any of those three lists the doc to re-sync.

**Current implementation**
- `untagged_doc_bundles`, `DOC_BUNDLE_MIN_BYTES` in `reqmap.py`, consumed by `cmd_check`
  — `untagged_doc_bundles` walks the code root (honoring `.reqmapignore`) for large
  `docs/*.html` files absent from the `generated-from:` member set and skipping engine
  outputs, and `cmd_check` emits one warn-only line per result.


--------------------


---
id: REQ-DOCBUNDLE-840
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-DOCBUNDLE-026]
---

# Flagging a large, unlinked docs/ HTML bundle

## Description
> A generated architecture page can drift from the requirements it was built from for
> days with nobody noticing, because drift detection only fires through tags it can see.
> The gate warns on any large `docs/*.html` file with no `generated-from:` lineage tag —
> skipping the engine's own generated outputs, anything `.reqmapignore` excludes, and
> anything outside `docs/`, since a byte-size threshold is only a proxy for "generated
> bundle", not proof of one.

Every bullet below is binding.
- The gate warns for each file under `docs/` ending in `.html` that carries no
  `generated-from:` member tag, once that file is at least `DOC_BUNDLE_MIN_BYTES`
  in size.
- The gate considers only files under `docs/`.
- The check skips engine-generated outputs: a file whose basename starts with `_`,
  and the published `map.html` viewer.
- The engine owns those two and freshness-checks them separately.
- The check honors `.reqmapignore` and the standard scan walk, so a repo can mark a
  regenerable artifact out of scope rather than tag it.
- The walk itself — what it prunes, what it ignores, and how it treats a file it cannot
  read — is [[ARCH-SCAN-002]]'s contract, not restated here.
- The check is warn-only and never changes the gate's exit code.

## Cases
CASE-1 — a large untagged docs/ HTML file is flagged
  Given  `docs/arch.html` at or above `DOC_BUNDLE_MIN_BYTES` with no `generated-from:` tag
  When   `untagged_doc_bundles` scans the repo
  Then   it returns `["docs/arch.html"]`, which `gate` folds into its warnings only —
         never an error, leaving the exit code unaffected

CASE-2 — a large untagged HTML file outside docs/ is never flagged
  Given  a large, untagged `top.html` at the repo root, outside `docs/`
  When   `untagged_doc_bundles` scans the repo
  Then   `top.html` is absent from the result

CASE-3 — engine outputs are excluded even when large and untagged
  Given  large, untagged `docs/map.html` and `docs/_x.html`
  When   `untagged_doc_bundles` scans the repo
  Then   neither file appears in the result, because the engine freshness-checks those
         two separately, on its own path

CASE-4 — a .reqmapignore pattern suppresses the finding
  Given  a large, untagged `docs/poster.html` matched by a `.reqmapignore` line `docs/poster.html`
  When   `untagged_doc_bundles` scans the repo
  Then   `docs/poster.html` is absent from the result

