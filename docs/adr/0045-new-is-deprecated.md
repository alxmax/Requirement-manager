# ADR-0045 — `new` is deprecated; a requirement is written, not scaffolded

- **Status:** Accepted.
- **Decided:** 2026-09-17, at the maintainer's direction: "`reqmap.py new AREA-NAME-NNN` — remove
  this command, I have never used it. If I ever want one, I will say directly: create a
  requirement that does x, y, z."
- **Evidence:** the maintainer's own usage (never), and the way requirements in this repo are
  actually authored: written into a module file by hand or by an assistant, then `sync`. Not
  measured further; no further review was asked for.

## Context

`new` stamps a blank requirement out of the built-in template; `new --from-todo` pre-fills one
from a `TODO.md` item (ARCH-NEW-004, ARCH-PROMOTE-TODO-001). This repo keeps its requirements as
module files (`ARCH-*.md` holding their `REQ-*` children, since `REQ-MODULEFILE-056`), which
`new` cannot write into, and it no longer has a `TODO.md`. The verb still costs a registry entry,
a parser branch, an MCP writing tool, three skill passages and about twenty tests.

## Decision

1. **`new` and `new --from-todo` are deprecated in v7.22.1 and removed in v8.0.0.** Through v7.x
   both still work and print exactly one line on stderr naming v8.0.0 and the replacement
   (REQ-NEW-1032). That is ADR-0037 decision 3's alias rule, the same window ADR-0044 gave
   `gate`'s moved flags, so both land in the same major.
2. **The replacement is not a command.** A requirement is written as a file, by hand or by an
   assistant asked for one. The built-in template stays documented as the shape to follow.
3. **Only the entry points go.** `author.py` also holds `_write_frontmatter_status`,
   `_set_frontmatter_status` and the TODO parsers that `gate`, `retire`, `mapcmd` and `mapdata`
   import; v8.0.0 removes `cmd_new`, `cmd_promote_todo` and what only they use, retires
   ARCH-NEW-004 and ARCH-PROMOTE-TODO-001 with `sync --retire --apply`, drops the `reqmap_new`
   MCP tool, and adds `new` to the retired-name guard.

## Consequences

- `init` and `gate --risk` stop pointing a new user at `new`; they name the file to write.
- Six verbs will remain after v8.0.0: `init`, `gate`, `ask`, `sync`, `clarify`, `mcp`.

## Revisit when

- A consumer repo is found scaffolding requirements with `new` before v8.0.0 is cut.
