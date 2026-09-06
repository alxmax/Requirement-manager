---
id: ARCH-SCAN-002
status: confirmed
level: architecture
layer: bus
owner: Alex
milestone: v1.00
satisfies: [SYS-READ-103]
---

# Member discovery

## Description
> Developers mark a piece of code as belonging to a capability by writing a short note in a
> comment, like "implements: LOGIN-001." This reads through all the project's source files
> and collects every one of those notes, so the tool always knows which code answers to
> which requirement. Without it, the link between a written requirement and the real code
> behind it would have to be tracked by hand, and would quickly fall out of date.

Every bullet below is binding.
- `scan_members` walks a code root and, in every source file with a known extension, finds inline `role: <ID>` tags and returns `cap_id -> [(role, relative_file, line), ...]`. [[REQ-SCAN-908]]
- A single tag may bind several requirements through a comma-separated id list, written `role: <ID>, <ID>, ...`, and `scan_all` runs member, per-criterion and test-level scanning in one walk. [[REQ-SCAN-909]]
- Every scanner reads the same masked view of a file, so a tag written inside a code fence or a string literal is an example to all of them and a member to none. [[REQ-SCAN-992]]

## Cases
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

## Context
**Terms**
- a tag             an inline comment of the form `role: <ID>` marking a piece of
- code as belonging to a capability.
- a role            what that code does for the capability.
- a member          one recorded `(role, file, line)` place in the code.
- the SSOT dir      the `requirements/` directory itself.
- a left-boundary   a check that the word before `implements:` really ends there,
- guard             so `reimplements:` is not read as a tag.

**Notes**
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

**Example**
<!-- Plain-language story; the Contract + Acceptance above are the precise version. -->
- Ana adds a comment `# implements: ARCH-SCAN-002` at the top of a new file and saves it.
  The scan walks the project, skipping folders like `node_modules`, and reports that file —
  with its exact path and line number — as a member of ARCH-SCAN-002. A stray comment
  reading `reimplements:` nearby is correctly ignored and never mistaken for a real tag.

**Current implementation**
- `scan_members`, `_prune_dirs`, `load_ignore`, `TAG_RE`, `TAG_LIST_RE`, `_findall_tags` in `reqmap.py`.


--------------------


---
id: REQ-SCAN-908
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-SCAN-002]
---

# scan_members walks the tree and collects role: ID tags

## Description
> `scan_members` is how the engine learns which code answers to which requirement, without
> anyone hand-maintaining a list. It walks every source file with a known extension, finds
> comments like `# implements: LOGIN-001`, and returns them keyed by requirement id — a
> left-boundary guard keeps a stray `reimplements:` from being read as a real tag.

Every bullet below is binding.
- `scan_members` walks a code root and, in every source file with a known extension,
  finds the inline tags.
- `scan_members` returns `cap_id -> [(role, relative_file, line), ...]`.
- A role is one of `implements`, `generated-from`, `validated-against` and `tested-by`.
- A tag ID matches `[A-Z][A-Z0-9]*(-[A-Z0-9]+)+`.
- A left-boundary guard prevents a substring match such as `reimplements:` or
  `x-implements:` being read as a real tag.
- The same `(role, ID)` appearing twice on one line is recorded once.
- File paths are reported repo-root-relative, with POSIX separators.

## Cases
CASE-1 — an implements: tag in a scanned file is picked up by the walk
  Given  `a.py` at the code root carrying `# implements: REQ-T-001`
  When   `scan_members(root, None)` runs
  Then   `"REQ-T-001"` is a key in the returned dict

CASE-2 — a member entry is a (role, relative_file, line) tuple
  Given  `a.py` at the code root carrying `# implements: REQ-T-001` on line 1
  When   `scan_members(root, None)` runs
  Then   `members["REQ-T-001"] == [("implements", "a.py", 1)]`

CASE-3 — all four roles are recognized and an unknown role string is not
  Given  one file carrying the four real role tags plus a `refines:` tag, all for one id
  When   `scan_members` runs
  Then   the recorded roles are exactly `implements`, `generated-from`, `validated-against`,
         `tested-by` — `refines` produces no member

CASE-4 — TAG_RE only matches an uppercase, hyphenated id shape
  Given  the strings `"implements: FOO-BAR-001"` and `"implements: foobar"`
  When   `TAG_RE.findall` runs on each
  Then   the first yields `[("implements", "FOO-BAR-001")]` and the second yields `[]`

CASE-5 — reimplements: and x-implements: are not read as real tags
  Given  the lines `"# reimplements: FOO-BAR-001"` and `"auto-implements: AB-CD-001"`
  When   `TAG_RE.findall` runs on each
  Then   both return `[]`

CASE-6 — a duplicated tag on one line is recorded only once
  Given  one line carrying `implements: FOO-BAR-001` twice
  When   `scan_members` runs
  Then   `len(members["FOO-BAR-001"]) == 1`

CASE-7 — a nested file's member path uses forward slashes, root-relative
  Given  a tag inside `sub/dir/m.py`, discovered via `scan_members(root, None)`
  When   the recorded member is read
  Then   its path field equals `"sub/dir/m.py"` (POSIX separators, even on Windows)


--------------------


---
id: REQ-SCAN-909
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-SCAN-002]
---

# One tag can bind several requirements, and directories are pruned

## Description
> A comma-separated tag (`generated-from: A, B, C`) lets one file — a whole-system doc, a
> shared fixture — answer to several requirements at once, each getting the same recorded
> location. The walk also has to know what NOT to scan: `.git`, `node_modules`, the SSOT
> `requirements/` dir itself, and anything `.reqmapignore` excludes, or every scan would
> waste time on generated noise and false members inside its own output.

Every bullet below is binding.
- A single tag may bind several requirements through a comma-separated id list,
  written `role: <ID>, <ID>, ...`.
- Each id in that list is recorded as a member of the same `(role, file, line)`.
- A whole-system doc generated from many requirements (`generated-from: A, B, C`) is
  therefore a member of each, and drifts when ANY of them changes.
- `.git`, `node_modules`, `__pycache__` and the SSOT `requirements/` directory are
  skipped.
- The SSOT directory is matched by realpath, so a source package merely named
  `requirements/` is still scanned.
- Paths matching `.reqmapignore` are excluded.
- An unreadable file is skipped without aborting the scan.
- `scan_all` returns the members, the per-criterion coverage and the verification levels
  from a single walk, and each result equals what the three separate scanners return.

## Cases
CASE-1 — a comma-separated tag registers members under every listed id
  Given  `<!-- generated-from: REQ-MA-001, REQ-MB-002 -->` in `docs/arch.html`
  When   `scan_members` runs
  Then   both `"REQ-MA-001"` and `"REQ-MB-002"` are keys in the result

CASE-2 — every id in a multi-id tag carries the identical (role, file, line) triple
  Given  `<!-- generated-from: REQ-MA-001, REQ-MB-002 -->` in `docs/arch.html`
  When   `scan_members` runs
  Then   `members["REQ-MA-001"] == members["REQ-MB-002"] == [("generated-from",
         "docs/arch.html", 1)]`, so the doc drifts when either requirement's contract changes

CASE-3 — a tag inside the real SSOT requirements/ dir is not scanned
  Given  `ignored.py` inside the SSOT `requirements/` dir, tagged `SSOT-IGN-001`
  When   `scan_members(root, requirements_dir)` runs
  Then   `"SSOT-IGN-001"` is absent from the result

CASE-4 — a source package named requirements/ that is not the SSOT dir is still scanned
  Given  a tagged file under `pkg/requirements/impl.py`, distinct from the real SSOT dir
  When   `scan_members(root, ssot_dir)` runs
  Then   `"pkg/requirements/impl.py"` appears among the recorded member paths

CASE-5 — a file listed in .reqmapignore is excluded from the scan
  Given  `.reqmapignore` naming `scripts/reqmap.py`, which itself carries a tag
  When   `scan_members` runs
  Then   the tagged id from that file is absent, while an untouched file's id is present

CASE-6 — an unreadable file yields None instead of raising
  Given  a path under a directory that does not exist
  When   `_scan_file_tags(path)` runs
  Then   it returns `None` rather than raising an exception

CASE-7 — scan_all's triple equals the three scanners run separately
  Given  a mixed tree with `.py`, `.ts` and `.md` files carrying tags, `verifies:` and
         `tested-by:` comments
  When   `scan_all(root, reqs_dir)` runs
  Then   it equals `(scan_members(...), scan_ac_verifies(...), scan_test_levels(...))`


--------------------


---
id: REQ-SCAN-992
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-SCAN-002]
---

# Which lines a tag may live on

## Description
> Documentation shows people how to tag their code, and a test file shows what a tag looks
> like — so the text `# implements: LOGIN-001` appears in places that are demonstrating a
> tag, not writing one. The scanners mask those places out. The rule has to be one rule:
> when each scanner carried its own copy, only the member scan knew what a Markdown fence
> was, and a `# verifies: <ID>#CASE-1` written inside a ```-fenced example counted as real
> per-criterion coverage — silencing the very warning that says the case is untested.

Every bullet below is binding.
- `_visible_lines` is the single masking pass. Member discovery, per-criterion `verifies:`
  coverage and levelled `tested-by:` coverage all read a file through it, so no scanner can
  admit a position another one excludes.
- In a `.md` or `.html` file, a line inside a fenced code block (``` or ~~~, CommonMark
  length-matched, the closer bare) carries no tag of any kind.
- In a `.md` file, a line indented by four spaces or a tab is an indented code block and
  carries no tag. The check runs before fence detection, so an indented fence marker cannot
  open a fence that swallows the rest of the file.
- In a `.py` file, string-literal content — including a docstring spanning many lines — is
  blanked before the search, and comment text is not.
- Stripping inline backtick spans is the caller's decision, not the masking pass's: member
  discovery strips them in prose, the levelled `tested-by:` scan strips them everywhere, and
  the `verifies:` scan does not.

## Cases
CASE-1 — a verifies tag inside a Markdown fence is not coverage
  Given  a `.md` file whose ```-fenced example contains `# verifies: REQ-FAKE-999#CASE-1`
  When   the per-criterion coverage scan runs
  Then   `REQ-FAKE-999` is absent from the coverage map

CASE-2 — a tag outside the fence in the same file is still real
  Given  the same file also carrying `<!-- verifies: REQ-REAL-001#CASE-2 -->` outside any fence
  When   the per-criterion coverage scan runs
  Then   `REQ-REAL-001` maps `CASE-2` to that file and line

CASE-3 — a tag in a Python docstring is masked, one in a comment is not
  Given  a `.py` file with `# verifies: REQ-DOC-1#CASE-1` inside a triple-quoted string and
         `# verifies: REQ-CODE-1#CASE-1` on a comment line
  When   the per-criterion coverage scan runs
  Then   only `REQ-CODE-1` is recorded

CASE-4 — an indented fence marker does not open a fence
  Given  a `.md` file whose four-space-indented line begins with ``` and whose later lines
         carry a real `<!-- implements: <ID> -->` tag
  When   member discovery runs
  Then   the later tag is still recorded

CASE-5 — the three scanners agree on every position
  Given  a tree mixing fenced examples, docstring examples and real tags
  When   `scan_all` and the three standalone scanners run over it
  Then   they return the same members, the same `verifies:` coverage and the same levels
