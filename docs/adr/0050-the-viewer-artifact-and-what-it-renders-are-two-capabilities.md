# ADR-0050 — The viewer artifact and what it renders are two capabilities

- **Status:** Accepted.
- **Decided:** 2026-09-22, carrying out the split ARCH-VIEWER-007's own notes deferred
  (`lint_exempt: over-scoped`, "a deferral, not a defence").
- **Evidence:** ARCH-VIEWER-007 before the split had 16 obligation lines, 8 cases and three
  exemptions (`ac-count-high`, `file-spread`, `over-scoped`). Two of the 16 lines described
  the file; fourteen described what the file shows.

## Context

ARCH-VIEWER-007 grew one child per viewer surface: the outline, the spec, the map, the roadmap
and its plan, the inbox, the commands. Its first two children are a different kind of
thing. REQ-VIEWER-940 says `map` writes one self-contained `_map.html` when the template is
vendored and degrades without it. REQ-VIEWER-941 says the inlined graph is escaped so that no
requirement text can break out of the `<script>` holding it.

Those two are tested by the engine's Python suite and implemented by
`reqmap_engine/viewer.py`, the single-file build config and the vendoring script. They hold
for any viewer, React or not. The other fourteen are tested by the SSR smoke and implemented
under `app/src/`. The over-scoped finding was right, and the note filed against it named
the seam.

## Decision

1. **ARCH-VIEWERFILE-074, "The viewer ships as one self-contained HTML file"**, takes
   REQ-VIEWER-940 and REQ-VIEWER-941 unchanged (only their `satisfies:` moves). It also takes
   the five artifact cases (template present, `</script>`, `<!--`, template absent, U+2028/9)
   and the members that build and inject the file: `_viewer_template_path`, `_inject_viewer`
   and `render_html` in `viewer.py`, `app/vite.viewer.config.js` and
   `app/scripts/install-viewer.mjs`. It is `draft` until the maintainer confirms it.
2. **ARCH-VIEWER-007 keeps what the file renders**: fourteen obligation lines and three cases
   (layout on a cyclic registry, UI language, the authored acceptance block), renumbered
   `CASE-1`..`CASE-3`. No `# verifies:` tag named any of its cases, so no tag broke. It
   drops the `over-scoped` and `ac-count-high` exemptions and keeps `file-spread`, since a
   UI is many files by construction.
3. **No behaviour changes.** The engine, the viewer and every test do what they did. Only
   ownership moved: which requirement a line of code and a test answer to.

## Consequences

- The corpus has 295 requirements. Two exemptions that `gate --audit` counted as debt are gone.
- A change to the escaping or the vendoring now drifts ARCH-VIEWERFILE-074 and not the
  whole viewer, so the review blast radius names the file's owners, not every surface's.

## Revisit when

- A second renderer (a static HTML export, a terminal viewer) needs the same artifact
  guarantees. ARCH-VIEWERFILE-074 is the contract it would share.
