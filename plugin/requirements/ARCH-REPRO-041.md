---
id: ARCH-REPRO-041
status: confirmed        # draft | baseline | in-progress | implemented | confirmed | deprecated
level: architecture
layer: feature       # bus | feature | need
owner: Alex
priority:            # must-have | should-have | could-have | wont-have (optional)
depends_on: [ARCH-SELFGATE-039]     # ids of bus/other capabilities this builds on
satisfies: [SYS-SHIP-108]
superseded_by:       # <ID>, if replaced
test_exempt: pipeline wiring (a CI job that rebuilds and compares) — the behavior IS the comparison, observed by CI running it; a unit test would only re-assert that a byte compare compares
# area:              # optional: System Map grouping label (else the id prefix is used)
---

# Committed build artifacts stay re-derivable

## Description
> Two files here are build output that is committed anyway, because the whole promise is
> that a consumer gets them without installing a toolchain. Nothing checked either one
> against the source it came from, so an edit to the viewer app or to a diagram generator
> could ship an artifact that no longer matched its own code, with the repo still green.
Every bullet below is binding.

**Glossary** — *committed build artifact*: a file tracked in git that a build step produces
from source also tracked in git.

**What it covers**
- `plugin/scripts/_map_viewer.html` derives from `app/`, built by `npm run build:viewer`.
- `docs/full_architecture.html` derives from
  `plugin/skills/excalidraw-diagram/examples/make_full_architecture.py`.

**What it does**
- The `artifacts` CI job rebuilds each covered artifact from its source on every push and
  pull request.
- The job fails the build when a rebuilt artifact differs from the committed one.
- The failure message names the stale file and the command that regenerates it.
- The `release` job runs only after `artifacts` passes, so a stale artifact never reaches a
  published tag.

## Verify intent (open questions for the human)
- None — both builds were measured as byte-reproducible before this check was written.

## Notes & known limitations (informative)
- `docs/architecture.html` stays out of scope: a human authored it, and `map --check`
  already covers the regions the engine owns inside it.
- Byte-for-byte comparison requires the artifacts' line endings to be a property of the
  repository, not of the machine that built them: `.gitattributes` pins `app/viewer.html`,
  the vendored viewer and the published diagram to LF. Without that the Windows and Linux
  builds of the same source disagree, and `core.autocrlf` hides the disagreement locally.
- The check assumes both builds stay byte-reproducible. A Node major bump or a Vite upgrade
  can break that, and the job reports it as a stale artifact — re-vendor the viewer in the
  same commit that moves the toolchain.
- The diagram half compares against a temp directory rather than regenerating in place,
  because the generator writes a sibling `.excalidraw` and `.gitignore` blocks
  `docs/*.excalidraw`.

## Cases (= tests)
CASE-1
  Given  a commit that changes `app/` without re-committing the built viewer
  When   the `artifacts` job runs
  Then   it fails and names `plugin/scripts/_map_viewer.html` and the rebuild command

CASE-2
  Given  a commit that changes the architecture generator without re-committing its output
  When   the `artifacts` job runs
  Then   it fails and names `docs/full_architecture.html` and the rebuild command

CASE-3
  Given  a tree whose committed artifacts match their sources
  When   the `artifacts` job runs
  Then   it passes and `release` becomes eligible to run

## Example — in practice (optional, non-binding)
- A contributor edits a React view, forgets `npm run build:viewer`, and CI names the stale
  vendored viewer instead of shipping a map viewer built from older code.

## WHERE — Current implementation
- `.github/workflows/ci.yml` — the `artifacts` job, and `release`'s dependency on it.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-REPRO-618
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REPRO-041]
superseded_by:
---

# Plugin/scripts/_map_viewer.html derives from app/, built by npm run

> `plugin/scripts/_map_viewer.html` derives from `app/`, built by `npm run build:viewer`.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REPRO-619
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REPRO-041]
superseded_by:
---

# Docs/full_architecture.html derives from plugin/skills/excalidraw-diagram/examples/make_full_architecture.py

> `docs/full_architecture.html` derives from
> `plugin/skills/excalidraw-diagram/examples/make_full_architecture.py`.

Scenario: the published architecture diagram matches its generator
  Given  `make_full_architecture.py` regenerated into a temporary directory
  When   its output is compared byte-for-byte against the committed
         `docs/full_architecture.html`
  Then   the two files are identical

## Members in code (auto)




--------------------


---
id: REQ-REPRO-620
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REPRO-041]
superseded_by:
---

# The artifacts CI job rebuilds each covered artifact

> The `artifacts` CI job rebuilds each covered artifact from its source on every push and
> pull request.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REPRO-621
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REPRO-041]
superseded_by:
---

# The job fails the build when a rebuilt

> The job fails the build when a rebuilt artifact differs from the committed one.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REPRO-622
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REPRO-041]
superseded_by:
---

# The failure message names the stale file and

> The failure message names the stale file and the command that regenerates it.

Scenario: TODO — state the observable that proves this
  Given  <precondition>
  When   <action>
  Then   <observable, pass/fail result>

## Members in code (auto)




--------------------


---
id: REQ-REPRO-623
status: draft
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REPRO-041]
superseded_by:
---

# The release job runs only after artifacts passes

> The `release` job runs only after `artifacts` passes, so a stale artifact never reaches
> a published tag.

Scenario: the release job depends on the artifacts job
  Given  `.github/workflows/ci.yml`
  When   the `release` job's `needs:` list is inspected
  Then   it names `artifacts` alongside `gate-and-tests` and `tests`

## Members in code (auto)
