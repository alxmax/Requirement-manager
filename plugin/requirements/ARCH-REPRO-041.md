---
id: ARCH-REPRO-041
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.19
depends_on: [ARCH-SELFGATE-039]
satisfies: [SYS-SHIP-108]
test_exempt: pipeline wiring (a CI job that rebuilds and compares) — the behavior IS the comparison, observed by CI running it; a unit test would only re-assert that a byte compare compares
---

# Committed build artifacts stay re-derivable

## Description
> Two files here are build output that is committed anyway, because the whole promise is
> that a consumer gets them without installing a toolchain. Nothing checked either one
> against the source it came from, so an edit to the viewer app or to a diagram generator
> could ship an artifact that no longer matched its own code, with the repo still green.

Every bullet below is binding.
- `plugin/scripts/_map_viewer.html` derives from `app/`, built by `npm run build:viewer`; the `artifacts` CI job rebuilds every covered artifact and fails the build when a rebuild differs from what is committed. [[REQ-REPRO-905]]

## Cases
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

## Context
**Terms**
- *committed build artifact*: a file tracked in git that a build step produces from source also tracked in git.

**Notes**
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

**Example**
- A contributor edits a React view, forgets `npm run build:viewer`, and CI names the stale
  vendored viewer instead of shipping a map viewer built from older code.

**Current implementation**
- `.github/workflows/ci.yml` — the `artifacts` job, and `release`'s dependency on it.


--------------------


---
id: REQ-REPRO-905
status: confirmed
test_exempt: pipeline wiring observed by the CI artifacts job, not by a unit test
level: code
layer: feature
owner: Alex
satisfies: [ARCH-REPRO-041]
---

# Rebuilding and diffing each committed artifact in CI

## Description
> A committed build artifact is a promise that a consumer never has to run the toolchain that
> produced it — but that promise silently rots the moment source changes without a rebuild.
> Rebuilding each artifact fresh on every push and diffing it against the committed copy turns
> "probably still matches" into a hard CI failure, at the cost of running a Node and a Python
> build on every push.

Every bullet below is binding.
- `plugin/scripts/_map_viewer.html` derives from `app/`, built by `npm run build:viewer`.
- `docs/full_architecture.html` derives from
  `plugin/skills/excalidraw-diagram/examples/make_full_architecture.py`.
- The `artifacts` CI job rebuilds each covered artifact from its source on every push and
  pull request.
- The job fails the build when a rebuilt artifact differs from the committed one.
- The failure message names the stale file and the command that regenerates it.
- The `release` job runs only after `artifacts` passes, so a stale artifact never reaches a
  published tag.

## Cases
CASE-1 — a stale vendored viewer fails the job and names the fix
  Given  a commit that changes `app/` without re-committing `plugin/scripts/_map_viewer.html`
  When   the "Vendored viewer matches app/" step runs
  Then   `git diff --exit-code` on that file is non-zero, the step fails, and the error
         names the file and `npm run build:viewer`

CASE-2 — the published architecture diagram matches its generator
  Given  `make_full_architecture.py` regenerated into a temporary directory
  When   its output is compared byte-for-byte against the committed
         `docs/full_architecture.html`
  Then   the two files are identical

CASE-3 — the SSR smoke runs against this repo's real registry, not a stand-in
  Given  a fresh checkout whose `app/public/data.json` is gitignored and absent
  When   the "Viewer SSR smoke" step runs
  Then   `npm run sync` first builds that fixture from the committed
         `plugin/requirements/_map.json` before `npm run smoke` runs against it

CASE-4 — the vendored-viewer check is the rebuild's own diff, not a second comparison
  Given  the "Rebuild the vendored viewer" step has just overwritten
         `plugin/scripts/_map_viewer.html` in place
  When   the next step runs
  Then   it inspects the working-tree diff on that one file — the rebuild writing over the
         committed copy IS the check, with no separate comparison logic

CASE-5 — the diagram check builds into a temp directory, never in place
  Given  `.gitignore` hard-blocks `docs/*.excalidraw`, a sibling file the generator writes
  When   the "Published architecture diagram matches its generator" step runs
  Then   `make_full_architecture.py` writes into a `mktemp -d` directory, and only that
         output is compared against the committed `docs/full_architecture.html`

CASE-6 — the release job depends on the artifacts job
  Given  `.github/workflows/ci.yml`
  When   the `release` job's `needs:` list is inspected
  Then   it names `artifacts` alongside `gate-and-tests` and `tests`

