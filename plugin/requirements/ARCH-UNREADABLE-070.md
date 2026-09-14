---
id: ARCH-UNREADABLE-070
status: confirmed
level: architecture
layer: feature
owner: Alex
milestone: v7.10
lint_exempt: [file-spread]
depends_on: [ARCH-SCAN-002, ARCH-CHECK-006]
satisfies: [SYS-GATE-102]
---

# Source files the scan cannot decode

## Description
> A file the scan opens but cannot decode is worse than one it never opens: it looks read.
> With `errors="ignore"` a UTF-16 source decodes to its text interleaved with dropped NULs,
> so every tag in it silently stops being a member and its line count doubles — the file
> reports "untagged" forever and no message ever says why. MetaEditor saves `.mq4` as
> UTF-16 LE by default, so this is a consumer's first file, not a corner case. It bit the
> same repo twice: once through a tag that "disappeared", once through a 4089-line count
> for a 2041-line file.

Every bullet below is binding.
- One decoder reads every source file the engine opens, decoding a UTF-16 BOM instead of mangling it, and refusing a file whose bytes carry NULs with nothing to key the encoding on rather than half-reading it. [[REQ-UNREADABLE-1004]]
- `undecodable_source_files` lists the scannable files that stay unreadable, and the gate warns (never errors) when any exist. [[REQ-UNREADABLE-1004]]

## Cases
CASE-1
  Given  a scannable file saved as UTF-16 with a byte-order mark, carrying `# implements: <ID>`
  When   `scan_members` runs
  Then   that file is a member of `<ID>`, and its reported line count is its real one

CASE-2
  Given  a scannable file whose bytes are UTF-16 with no byte-order mark
  When   `gate` runs
  Then   it warns naming that file and the reason, exits 0, and no tag is read out of it

CASE-3
  Given  a UTF-8 source file, with or without a BOM
  When   the scan reads it
  Then   its lines, tag line numbers and line count are exactly what they were before this
         requirement existed

## Context
**Terms**
- *undecodable*: the scan opened the file and could not turn its bytes into text it is willing to read — a UTF-16 file with no BOM, or a BOM it cannot decode.

**Notes**
- The pair with [[ARCH-UNSCANNEDTAG-045]] is deliberate: that rule reports a tag in a file
  type the walk never opens, this one a file the walk DOES open and cannot decode. Both
  fail identically from the outside — the tag is silently not a member — and neither is
  visible without being named.
- Line splitting is `io.StringIO(text, newline=None).readlines()`, not `str.splitlines()`.
  The latter also breaks on form feed and U+0085, which would shift every line number after
  one such byte; a tag's recorded line number means universal-newline `readlines()` and must
  keep meaning it.
- A BOM-less UTF-16 file yields empty text rather than a guess. Decoding it by sniffing
  would be a second, weaker heuristic that can mis-read a genuinely binary file as source;
  naming it and moving on is the honest outcome, and the remedy (re-save as UTF-8) is one
  the author can act on.
- The BOM-less test is NUL **density**, not the presence of a NUL. "Any NUL" was tried
  first and this repo falsified it on the first run: `app/src/lib/search.js` is valid UTF-8
  carrying two deliberate NUL sentinels in a string literal, and refusing it dropped four
  real member tags — this requirement's own failure mode, inverted. Mostly-ASCII UTF-16 is
  about half NULs; a sentinel is a few bytes in thousands. The threshold errs toward
  reading: a missed BOM-less UTF-16 file is the status quo, a wrongly refused UTF-8 file is
  a new regression.
- Warn, never error: an undecodable file is a fact about someone's editor, not a broken
  contract, and the gate's errors are reserved for link integrity.

**Example**
A consumer's `mt4/indicator.mq4` is UTF-16 LE from MetaEditor. Before this requirement its
`# implements:` tag was invisible, `gate --risk` listed it as untagged forever, and
`init --plan` reported it at 4089 lines instead of 2041. Now the tag is read, the count is
right, and a BOM-less sibling is named by one WARN instead of failing silently.

**Current implementation**
- `read_source_text()` / `read_source_lines()` in `reqmap_engine/scan.py`, used by
  `scan_all`, `_walk_code_lines`, `candidates._file_facts` and `orphans.orphan_code_files`.
- `undecodable_source_files()` in `reqmap_engine/orphans.py`, wired into the gate as RM033.

- `lint_exempt: file-spread` - the spread IS the capability. One decoder exists so that
  the four places which open a source file stop each deciding for themselves; a version
  touching one file would be the bug this requirement removes.

**Links**
- Sibling: [[ARCH-UNSCANNEDTAG-045]] (the other half of "the tag was never read").


--------------------


---
id: REQ-UNREADABLE-1004
status: confirmed
level: code
layer: feature
owner: Alex
milestone: v7.10
lint_exempt: [file-spread]
satisfies: [ARCH-UNREADABLE-070]
---

# Decoding a source file, or refusing it out loud

## Description
> Four call sites each opened source files with `errors="ignore"` and drifted into the same
> blind spot: a UTF-16 file decoded to interleaved rubbish that still looked like text, so
> its tags vanished and its line count doubled. One decoder, used by all four, either reads
> the file properly or says it could not.

Every bullet below is binding.
- `read_source_text` returns the file's text and no problem when the bytes decode as UTF-8,
  with or without a BOM.
- When the first two bytes are a UTF-16 byte-order mark, it decodes the file as UTF-16 and
  returns the resulting text with no problem, so tags inside it are read normally.
- When the bytes carry no UTF-16 BOM and NULs are at least a tenth of the decoded text, it
  returns empty text and a short reason, so no caller reads a partial tag or counts a
  doubled line. Below that density the text is returned unchanged: a UTF-8 source holding a
  NUL sentinel keeps every tag it has.
- A file that cannot be opened at all yields `(None, None)` — skipped, never fatal.
- `read_source_lines` splits that text exactly as universal-newline `readlines()` splits it,
  so no recorded tag line number moves.
- `undecodable_source_files` returns the sorted `(path, reason)` pairs for every scannable
  file under the scan root that yields a problem.
- `gate` reports each such file in one warning naming the path and the reason, states that
  any tag in it is invisible and it counts as untagged, names the remedy (re-save as UTF-8,
  or ignore it), and never changes the exit code.

## Cases
CASE-1 — a UTF-16 file with a BOM becomes a real member
  Given  a scannable file written as UTF-16 LE with a BOM, whose first line is `# implements: ARCH-EXAMPLE-001`
  When   `scan_members` runs over its directory
  Then   the file is listed as a member of `ARCH-EXAMPLE-001`

CASE-2 — its line count is its real one, not double
  Given  that same 41-line UTF-16 file
  When   `_file_facts` reads it
  Then   the reported `loc` is 41

CASE-3 — a BOM-less UTF-16 file is named, not half-read
  Given  a scannable file written as UTF-16 LE with no BOM, containing a membership tag
  When   `undecodable_source_files` runs
  Then   the file is returned with a reason mentioning UTF-8, and `scan_members` finds no
         tag in it

CASE-4 — the gate warns and stays green
  Given  a repository containing one BOM-less UTF-16 source file
  When   `gate` runs
  Then   it prints one RM033 warning naming that file, and the exit code is 0

CASE-5 — UTF-8 files are untouched
  Given  a UTF-8 source file containing a form feed and a tag after it
  When   `read_source_lines` reads it
  Then   the lines are identical to `readlines()` on the same file, so the tag's line number
         is unchanged

CASE-6 — a UTF-8 file with a NUL sentinel keeps its tags
  Given  a valid UTF-8 source file of several thousand bytes containing two real NUL bytes
         inside a string literal, and four membership tags
  When   `scan_members` runs
  Then   the file is a member for all four tags, and `undecodable_source_files` does not
         list it

## Context
**Notes**
- `str.splitlines()` was rejected for the split: it breaks on form feed, U+0085 and the
  Unicode separators, which moves every line number after one such byte. The test compares
  against `readlines()` directly rather than asserting a count.
- `lint_exempt: file-spread` - one decoder read from four modules IS the requirement.
  A version confined to one file would be the per-call-site drift it removes.
- The NUL test is a density ratio, not `"\x00" in text`. A UTF-8 source may legitimately
  hold a real NUL byte — a sentinel key in a string literal — and this repo has one; the
  presence test dropped its four member tags. Density separates the two cases by three
  orders of magnitude.
