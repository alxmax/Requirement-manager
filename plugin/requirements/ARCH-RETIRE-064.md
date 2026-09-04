---
id: ARCH-RETIRE-064
status: confirmed
level: architecture
layer: feature
owner: Alex
priority: should-have
milestone: v4.0
depends_on: [ARCH-PARSE-001, ARCH-SCAN-002, ARCH-DRIFT-003, ARCH-MODULEFILE-056]
satisfies: [SYS-GATE-102]
---

# Taking a requirement out of service

## Description
> Deleting a requirement is the operation nobody documents and everybody does badly: the file
> goes, the tags stay, and the next gate reports dangling tags in code whose purpose is now
> unrecorded. `retire` inverts that order — it states the blast radius first, refuses while
> anything still depends on the requirement, and only then removes what it can remove
> deterministically. Deprecating is the default because it is reversible.

Every bullet below is binding.
- `retire` reports everything that points at the requirement before anything is changed: dependents, children, members, prose references, and the files where it is the only tagged requirement. [[REQ-RETIRE-960]]
- `retire` deprecates by default, refuses while dependents or children exist unless forced, and never writes without `--apply`. [[REQ-RETIRE-961]]
- `retire --delete` removes the requirement block, its lock entries and its membership tags — never a function body. [[REQ-RETIRE-962]]

## Cases
CASE-1 — the plan comes before the change
  Given  a requirement with members
  When   `retire` runs without `--apply`
  Then   the blast radius is printed and no file changes

CASE-2 — a dependent stops the operation
  Given  a requirement another one depends on
  When   `retire --apply` runs without `--force`
  Then   it refuses, names the dependent, and exits 1

CASE-3 — deprecating keeps the code working
  Given  a confirmed requirement with an implementing member and no dependents
  When   `retire --apply` runs
  Then   its status becomes deprecated and its tags are untouched


---
id: REQ-RETIRE-960
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RETIRE-064]
---

# The blast radius of a retirement

## Description
> What makes a deletion safe is knowing, before it happens, what was pointing at the thing.
> The engine can compute every one of those pointers exactly, and separating exclusive files
> from shared ones is what turns "delete the code too" from a guess into a list.

Every bullet below is binding.
- The plan names the requirements that declare `depends_on` on this id, and those that declare
  `satisfies` it.
- The plan lists every member of the requirement with its role and location.
- The plan separates files where this was the only tagged requirement from files shared with
  other requirements.
- The plan names the requirements whose prose carries a `[[<id>]]` reference to it.
- The plan names the dependencies this requirement was the last consumer of, since
  `depends_on` runs consumer to foundation and nothing else reports a capability that
  has just lost its only caller.
- Computing the plan changes nothing.

## Cases
CASE-1 — dependents and children are named
  Given  requirement B depending on A and requirement C satisfying A
  When   the plan for A is computed
  Then   it names B as a dependent and C as a child

CASE-2 — exclusive and shared files are separated
  Given  A tagged in one file alone and in one file it shares with B
  When   the plan for A is computed
  Then   the first file is listed as exclusive and the second as shared

CASE-3 — a prose cross-reference is found
  Given  requirement D whose Description carries `[[A]]`
  When   the plan for A is computed
  Then   D is named as a referencing requirement

CASE-4 — a dependency left with no consumer is named
  Given  A depends on E, and no other requirement depends on E
  When   the plan for A is computed
  Then   E is named as left with no consumer

---
id: REQ-RETIRE-961
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RETIRE-064]
---

# Deprecating, refusing, and never writing by accident

## Description
> The safe default matters more here than anywhere else in the engine: this is the one
> command whose mistake is measured in lost work. So it reports by default, refuses while
> anything still points at the requirement, and prefers the reversible half of the operation.

Every bullet below is binding.
- Without `--apply` nothing is written, and the output says so.
- With dependents or children present, `retire` refuses and exits 1 unless `--force` is given.
- `--apply` without `--delete` sets the requirement's status to deprecated and leaves its code
  and tags untouched.
- `--apply` refuses on a working tree with uncommitted changes unless `--force`, so the
  retirement is one reviewable diff.
- An unknown id exits 1.

## Cases
CASE-1 — the default run writes nothing
  Given  any requirement
  When   `retire <ID>` runs
  Then   the requirement file is byte-identical afterwards

CASE-2 — force overrides the dependent refusal
  Given  a requirement with one dependent
  When   `retire --apply --force` runs
  Then   the retirement proceeds

CASE-3 — deprecation is a status change and nothing else
  Given  a confirmed requirement with members and no dependents
  When   `retire --apply --force` runs
  Then   its frontmatter reads `status: deprecated` and its member tags are unchanged

---
id: REQ-RETIRE-962
status: confirmed
level: code
layer: feature
owner: Alex
satisfies: [ARCH-RETIRE-064]
---

# Deleting a requirement without deleting meaning

## Description
> A deletion that leaves tags behind produces dangling-tag errors; one that rips out code
> destroys work. The engine takes exactly the half it can do without understanding the code:
> the requirement, its baseline, and the tag tokens. The other half is a list, handed over.

Every bullet below is binding.
- `--delete` removes the requirement's block from its file, and removes the file itself when it
  held only that requirement.
- `--delete` removes the requirement's entry from the contract lock and from the member sidecar.
- `--delete` strips `implements:`, `tested-by:` and `verifies:` tokens for that id from the
  files that carry them; a comment line that held only that tag is removed, a line carrying
  other tags keeps them.
- No function body, class or file of source code is removed on the strength of a tag.
- The files where the tag was exclusive are reported as code nothing points at any more.

## Cases
CASE-1 — a module file keeps its other requirements
  Given  a file holding requirements A and B
  When   A is deleted
  Then   the file still holds B, byte-identical, and A is gone

CASE-2 — a tag line goes, a shared line survives
  Given  one line carrying only `# implements: A` and one carrying `# implements: A  # implements: B`
  When   A is deleted
  Then   the first line is removed and the second keeps `# implements: B`

CASE-3 — the lock forgets the requirement
  Given  a lock holding an entry for A
  When   A is deleted
  Then   the lock no longer carries that entry

CASE-4 — code is never removed on the strength of a tag
  Given  a file whose only tag was A's, carrying a function body
  When   A is deleted
  Then   the function body is still there and the file is named as now-unreferenced
