---
id: ARCH-SCAN-002
status: confirmed
level: system
layer: bus
owner: Alex
depends_on: []
satisfies: [SYS-READ-103]
superseded_by:
milestone: v1.00
---

# Member discovery

## Description
> Developers mark a piece of code as belonging to a capability by writing a short note in a
> comment, like "implements: LOGIN-001." This reads through all the project's source files
> and collects every one of those notes, so the tool always knows which code answers to
> which requirement. Without it, the link between a written requirement and the real code
> behind it would have to be tracked by hand, and would quickly fall out of date.
Every bullet below is binding.
<!-- Words used below, in plain terms:
     a tag             an inline comment of the form `role: <ID>` marking a piece of
                       code as belonging to a capability.
     a role            what that code does for the capability.
     a member          one recorded `(role, file, line)` place in the code.
     the SSOT dir      the `requirements/` directory itself.
     a left-boundary   a check that the word before `implements:` really ends there,
     guard             so `reimplements:` is not read as a tag. -->

**What it finds**
- `scan_members` walks a code root and, in every source file with a known extension,
  finds the inline tags.
- `scan_members` returns `cap_id -> [(role, relative_file, line), ...]`.
- A role is one of `implements`, `generated-from`, `validated-against` and `tested-by`.
- A tag ID matches `[A-Z][A-Z0-9]*(-[A-Z0-9]+)+`.
- A left-boundary guard prevents a substring match such as `reimplements:` or
  `x-implements:` being read as a real tag.
- The same `(role, ID)` appearing twice on one line is recorded once.
- File paths are reported repo-root-relative, with POSIX separators.

**Tags naming several requirements**
- A single tag may bind several requirements through a comma-separated id list,
  written `role: <ID>, <ID>, ...`.
- Each id in that list is recorded as a member of the same `(role, file, line)`.
- A whole-system doc generated from many requirements (`generated-from: A, B, C`) is
  therefore a member of each, and drifts when ANY of them changes.

**What it skips**
- `.git`, `node_modules`, `__pycache__` and the SSOT `requirements/` directory are
  skipped.
- The SSOT directory is matched by realpath, so a source package merely named
  `requirements/` is still scanned.
- Paths matching `.reqmapignore` are excluded.
- An unreadable file is skipped without aborting the scan.

- `scan_all` returns the members, the per-criterion coverage and the verification levels
  from a single walk, and each result equals what the three separate scanners return.

## Verify intent (open questions for the human)
- None — authored from known intent, not reconstructed from code.

## Notes & known limitations (informative)
- The member list is discovered, never hand-maintained — that is the first thing to rot.
- The realpath comparison for the SSOT directory runs only for a directory whose name
  matches it; resolving every directory was 62% of one consumer's gate time (4,900 upload
  folders). A directory that a `.reqmapignore` pattern ending in `/**` or `/*` covers is not
  descended at all — every file under it matched the pattern anyway, so results are identical.
- Scanned schema files and basenames grew from the first consumer evidence run (2026-08-25):
  `.prisma`, `.graphql`, `.proto`, `Caddyfile`, `Jenkinsfile`, `Procfile`, `Vagrantfile`, and any
  `Dockerfile.<variant>`; the five-repo matrix run the same day added `.scss/.sass/.less`,
  `.vue/.svelte`, `.mjs/.cjs/.mts/.cts`, `.cs/.php/.rb/.kt/.kts/.swift/.scala/.ex/.exs/.dart`
  and `.toml`. A
  tag in any other type is reported by [[ARCH-UNSCANNEDTAG-045]] rather than lost.

## Cases (= tests)
CASE-1
  Given  a file containing `# implements: <ID>`
  When   the scan runs
  Then   a member `(implements, file, line)` is recorded under `<ID>`

CASE-2
  Given  tags using each of the four roles and one unknown role string
  When   the scan runs
  Then   all four roles are recognized and the unknown role produces no member

CASE-3
  Given  files under `.git`, `node_modules`, `__pycache__` or the SSOT `requirements/`
  When   the scan runs
  Then   those directories are not scanned

CASE-4
  Given  a duplicate tag on a single line
  When   the scan runs
  Then   it is deduplicated and member paths are POSIX-relative

CASE-5
  Given  an unreadable file in the tree
  When   the scan runs
  Then   the file is skipped without aborting the scan

CASE-6
  Given  a tag `generated-from: <ID-A>, <ID-B>` listing several ids
  When   the scan runs
  Then   the file is recorded as a member of both <ID-A> and <ID-B>

CASE-7
  Given  any code tree
  When   `scan_all` runs
  Then   its three results equal those of `scan_members`, `scan_ac_verifies` and
         `scan_test_levels` run separately, and every file is opened once

## Example — in practice (optional, non-binding)
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana adds a comment `# implements: ARCH-SCAN-002` at the top of a new file and saves it.
  The scan walks the project, skipping folders like `node_modules`, and reports that file —
  with its exact path and line number — as a member of ARCH-SCAN-002. A stray comment
  reading `reimplements:` nearby is correctly ignored and never mistaken for a real tag.

## WHERE — Current implementation
- `scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE`, `TAG_LIST_RE`, `_findall_tags` in `reqmap.py`.

## Links
- Used by: (auto)
## Members in code (auto)




--------------------


---
id: REQ-SCAN-218
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# Scan_members walks a code root and, in every

> `scan_members` walks a code root and, in every source file with a known extension, finds
> the inline tags.

Scenario: an implements: tag in a scanned file is picked up by the walk
  Given  `a.py` at the code root carrying `# implements: REQ-T-001`
  When   `scan_members(root, None)` runs
  Then   `"REQ-T-001"` is a key in the returned dict

## Members in code (auto)




--------------------


---
id: REQ-SCAN-219
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# Scan_members returns cap_id -> (role, relative_file, line), 

> `scan_members` returns `cap_id -> [(role, relative_file, line), ...]`.

Scenario: a member entry is a (role, relative_file, line) tuple
  Given  `a.py` at the code root carrying `# implements: REQ-T-001` on line 1
  When   `scan_members(root, None)` runs
  Then   `members["REQ-T-001"] == [("implements", "a.py", 1)]`

## Members in code (auto)




--------------------


---
id: REQ-SCAN-220
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# A role is one of implements, generated-from, validated-against

> A role is one of `implements`, `generated-from`, `validated-against` and `tested-by`.

Scenario: all four roles are recognized and an unknown role string is not
  Given  one file carrying the four real role tags plus a `refines:` tag, all for one id
  When   `scan_members` runs
  Then   the recorded roles are exactly `implements`, `generated-from`, `validated-against`,
         `tested-by` — `refines` produces no member

## Members in code (auto)




--------------------


---
id: REQ-SCAN-221
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# A tag ID matches A-ZA-Z0-9(-A-Z0-9+)+

> A tag ID matches `[A-Z][A-Z0-9]*(-[A-Z0-9]+)+`.

Scenario: TAG_RE only matches an uppercase, hyphenated id shape
  Given  the strings `"implements: FOO-BAR-001"` and `"implements: foobar"`
  When   `TAG_RE.findall` runs on each
  Then   the first yields `[("implements", "FOO-BAR-001")]` and the second yields `[]`

## Members in code (auto)




--------------------


---
id: REQ-SCAN-222
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# A left-boundary guard prevents a substring match such

> A left-boundary guard prevents a substring match such as `reimplements:` or
> `x-implements:` being read as a real tag.

Scenario: reimplements: and x-implements: are not read as real tags
  Given  the lines `"# reimplements: FOO-BAR-001"` and `"auto-implements: AB-CD-001"`
  When   `TAG_RE.findall` runs on each
  Then   both return `[]`

## Members in code (auto)




--------------------


---
id: REQ-SCAN-223
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# The same (role, ID) appearing twice on one

> The same `(role, ID)` appearing twice on one line is recorded once.

Scenario: a duplicated tag on one line is recorded only once
  Given  one line carrying `implements: FOO-BAR-001` twice
  When   `scan_members` runs
  Then   `len(members["FOO-BAR-001"]) == 1`

## Members in code (auto)




--------------------


---
id: REQ-SCAN-224
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# File paths are reported repo-root-relative, with POSIX separators

> File paths are reported repo-root-relative, with POSIX separators.

Scenario: a nested file's member path uses forward slashes, root-relative
  Given  a tag inside `sub/dir/m.py`, discovered via `scan_members(root, None)`
  When   the recorded member is read
  Then   its path field equals `"sub/dir/m.py"` (POSIX separators, even on Windows)

## Members in code (auto)




--------------------


---
id: REQ-SCAN-225
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# A single tag may bind several requirements through

> A single tag may bind several requirements through a comma-separated id list, written
> `role: <ID>, <ID>, ...`.

Scenario: a comma-separated tag registers members under every listed id
  Given  `<!-- generated-from: REQ-MA-001, REQ-MB-002 -->` in `docs/arch.html`
  When   `scan_members` runs
  Then   both `"REQ-MA-001"` and `"REQ-MB-002"` are keys in the result

## Members in code (auto)




--------------------


---
id: REQ-SCAN-226
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# Each id in that list is recorded as

> Each id in that list is recorded as a member of the same `(role, file, line)`.

Scenario: every id in a multi-id tag carries the identical (role, file, line) triple
  Given  `<!-- generated-from: REQ-MA-001, REQ-MB-002 -->` in `docs/arch.html`
  When   `scan_members` runs
  Then   `members["REQ-MA-001"] == members["REQ-MB-002"] == [("generated-from",
         "docs/arch.html", 1)]`, so the doc drifts when either requirement's contract changes

## Members in code (auto)




--------------------


---
id: REQ-SCAN-228
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# .git, node_modules, __pycache__ and the SSOT requirements/ directory

> `.git`, `node_modules`, `__pycache__` and the SSOT `requirements/` directory are
> skipped.

Scenario: a tag inside the real SSOT requirements/ dir is not scanned
  Given  `ignored.py` inside the SSOT `requirements/` dir, tagged `SSOT-IGN-001`
  When   `scan_members(root, requirements_dir)` runs
  Then   `"SSOT-IGN-001"` is absent from the result

## Members in code (auto)




--------------------


---
id: REQ-SCAN-229
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# The SSOT directory is matched by realpath, so

> The SSOT directory is matched by realpath, so a source package merely named
> `requirements/` is still scanned.

Scenario: a source package named requirements/ that is not the SSOT dir is still scanned
  Given  a tagged file under `pkg/requirements/impl.py`, distinct from the real SSOT dir
  When   `scan_members(root, ssot_dir)` runs
  Then   `"pkg/requirements/impl.py"` appears among the recorded member paths

## Members in code (auto)




--------------------


---
id: REQ-SCAN-230
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# Paths matching .reqmapignore are excluded

> Paths matching `.reqmapignore` are excluded.

Scenario: a file listed in .reqmapignore is excluded from the scan
  Given  `.reqmapignore` naming `scripts/reqmap.py`, which itself carries a tag
  When   `scan_members` runs
  Then   the tagged id from that file is absent, while an untouched file's id is present

## Members in code (auto)




--------------------


---
id: REQ-SCAN-231
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# An unreadable file is skipped without aborting the

> An unreadable file is skipped without aborting the scan.

Scenario: an unreadable file yields None instead of raising
  Given  a path under a directory that does not exist
  When   `_scan_file_tags(path)` runs
  Then   it returns `None` rather than raising an exception

## Members in code (auto)




--------------------


---
id: REQ-SCAN-232
status: baseline
form: atomic
level: code
layer: feature
owner: Alex
satisfies: [ARCH-SCAN-002]
superseded_by:
---

# Scan_all returns the members, the per-criterion coverage and

> `scan_all` returns the members, the per-criterion coverage and the verification levels
> from a single walk, and each result equals what the three separate scanners return.

Scenario: scan_all's triple equals the three scanners run separately
  Given  a mixed tree with `.py`, `.ts` and `.md` files carrying tags, `verifies:` and
         `tested-by:` comments
  When   `scan_all(root, reqs_dir)` runs
  Then   it equals `(scan_members(...), scan_ac_verifies(...), scan_test_levels(...))`

## Members in code (auto)
