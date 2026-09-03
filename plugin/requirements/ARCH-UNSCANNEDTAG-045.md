---
id: ARCH-UNSCANNEDTAG-045
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v2.9
depends_on: [ARCH-SCAN-002, ARCH-CHECK-006]
satisfies: [SYS-GATE-102]
---

# Tags in unscanned file types reported

## Description
> A membership tag only counts when the scan reads the file it sits in. The scan reads a
> fixed list of extensions and basenames, so a tag in any other kind of file is silently
> invisible: the author believes the requirement has a member, the map says it has none,
> and nothing points at the gap. The first consumer run found two such files on the first
> try — a `Caddyfile` and a Prisma schema, both tagged, neither ever read.

Every bullet below is binding.
- `tagged_unscanned_files` lists the tracked, non-scannable files under the scan root that contain a membership tag, and the gate warns (never errors) when any exist. [[REQ-UNSCANNEDTAG-939]]

## Cases
CASE-1
  Given  a tracked file of a type the scan never reads, carrying `# implements: <ID>`
  When   `gate` runs inside a git work tree
  Then   it warns, naming that file and the count, and exits 0

CASE-2
  Given  a tracked non-scannable file with no tag, a binary file, and a `_`-prefixed file
         whose text mentions a tag
  When   `tagged_unscanned_files` runs
  Then   none of them is listed

CASE-3
  Given  a scan root that is not a git work tree
  When   `tagged_unscanned_files` runs
  Then   it returns None and `gate` prints no such warning

## Context
**Terms**
- *scannable*: a file whose extension or basename the scan reads (`CODE_EXTS`, `BASENAME_CODE_FILES`); *tracked*: git has the file in its index.

**Notes**
- Tracked, not "every file on disk": the walk that discovers members is bounded by the
  extension list on purpose (a 135 MB checkout with 40k `node_modules` files must stay
  fast). One `git ls-files` call bounds this check the same way `ARCH-TRACKED-042` is
  bounded, and the two share the fail-open convention.
- The size cap and the UTF-8 requirement are what keep a stray lockfile or an image from
  costing anything: a tag can only live in text a human wrote.
- The remedy is deliberately "ask for the type": a consumer's vendored engine is replaced
  on update, so a local edit to `CODE_EXTS` would not survive. The evidence run that
  produced this requirement also added `.prisma`, `.graphql`, `.proto`, `Caddyfile`,
  `Jenkinsfile`, `Procfile` and `Vagrantfile` to the scan.

**Example**
A consumer tags `apps/api/prisma/schema.prisma` and `Caddyfile`. Before this check the map
listed neither as a member and the gate was green; now the gate prints one WARN naming
both, and the next engine release scans both types.

**Current implementation**
- `tagged_unscanned_files()` in `reqmap.py`, wired into `cmd_check` beside
  `untracked_members()`.

**Links**
- Sibling: [[ARCH-TRACKED-042]] (the same `git ls-files` boundary, other direction).


--------------------


---
id: REQ-UNSCANNEDTAG-939
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-UNSCANNEDTAG-045]
---

# Warning about a tag the scan never reads

## Description
> The scan only reads a fixed list of extensions and basenames, so a membership tag in any
> other file type — a Caddyfile, a Prisma schema — is silently invisible: the author believes
> the requirement has a member, the map says it has none, and nothing points at the gap. This
> check names exactly those files so the mismatch is not discovered by accident.

Every bullet below is binding.
- `tagged_unscanned_files` lists the tracked, non-scannable files under the scan root that
  contain a membership tag.
- `gate` reports those unscanned-type files in one warning, naming up to five paths and the total count.
- The warning states that those files are not members, and names the remedy: move the tag
  into a scannable file, or ask for the file type to be added to the scan.
- The check skips paths matching `.reqmapignore`, files under the SSOT directory, files
  whose basename starts with `_`, `.git` or `.reqmap` (their comments quote tags as
  examples), and files larger than one megabyte. Any other dotfile, such as `.env`, is
  checked like any file.
- A file that is not valid UTF-8 text is skipped. Binary files never produce a warning.
- The check reports nothing and the gate stays silent when the scan root is not a git work
  tree, or git is unavailable.
- The warning never changes the exit code.

## Cases
CASE-1 — a tagged Caddyfile is listed as unscannable
  Given  a tracked `Caddyfile` containing `# implements: ARCH-EXAMPLE-001`
  When   `tagged_unscanned_files` runs
  Then   that file appears in its returned list

CASE-2 — the gate warning names up to five files and the total count
  Given  seven tracked non-scannable files each carrying a tag
  When   `gate` runs
  Then   it prints one warning naming five of them and stating the total of seven, and the
         exit code is unchanged

CASE-3 — the warning states the remedy, not just the file names
  Given  one tracked non-scannable file carrying a tag
  When   `gate` runs
  Then   the warning states the file counts as no member and names both remedies: move the tag, or ask for the type

CASE-4 — ignored, SSOT, underscore-prefixed and oversized files are skipped
  Given  a file matched by `.reqmapignore`, a file under `requirements/`, a `_scratch.txt` file, and a 2 MB file, each carrying a tag
  When   `tagged_unscanned_files` runs
  Then   none of the four appears in its returned list

CASE-5 — a non-UTF-8 file is skipped without warning
  Given  a tracked non-scannable binary file whose bytes are not valid UTF-8, containing a tag-like string
  When   `tagged_unscanned_files` runs
  Then   that file is absent from the returned list

CASE-6 — outside a git work tree, the check stays silent
  Given  a scan root that is not a git repository
  When   `gate` runs
  Then   it prints no unscanned-tag warning at all

