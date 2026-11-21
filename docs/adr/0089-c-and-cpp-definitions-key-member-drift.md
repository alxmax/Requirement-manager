# ADR-0089 — C and C++ definitions key member drift

- **Status:** Accepted. Extends [ADR-0085](0085-drift-holds-on-an-existing-corpus.md), whose
  revisit condition this meets.
- **Decided:** 2026-11-21
- **Evidence:** a read-only audit of an existing C/C++ repository with its requirements and
  tags in place. Member drift keyed every C/C++ member by file, and a file tagged by several
  requirements was dropped, so on that code reverse drift reported almost nothing.

## Context

ADR-0085 kept the whole-file hash for brace languages because their spans were read only by
heuristics, and a wrong span is a wrong drift signal. Its revisit condition was a brace-language
repository asking for member drift on a shared file. An audit asked exactly that: in C and C++
one source file usually implements several requirements, so per file nothing is attributable.

## Decision

- **A top-level C/C++ definition is a span**, read by a narrow reader (`bracedefs.py`) that
  gives up on any doubt. Comments, string and character literals and preprocessor lines are
  blanked first. `namespace` and `extern "C"` blocks are read through. A
  `class`/`struct`/`union`/`enum` body is one definition, as a Python class is. A block whose
  header holds a parameter list and no top-level `=` is a function. Any other block is skipped
  whole. A constructor's brace initializer (`b_{2}`) belongs to its header.
- **The key is the definition's name, qualified as written** (`Foo::Foo`,
  `Widget2<T>::get`). An overloaded name carries its parameter list (`add(int a, int b)`), so
  overloads never share a key.
- **The tag rules are Python's**: a tag inside a definition, or in the unbroken comment block
  right above it, keys it; a blank line ends the block; the hash covers the definition only.
- **Braces that do not balance return no span**, and every member of that file keeps the
  whole-file key, as before.
- **The reader is loaded only for a C/C++ member** (`.c .h .cc .cpp .cxx .hh .hpp .hxx
  .inl`): a repository with none never imports it. The span helpers move from `locks.py` to
  `memberspans.py` so `locks.py` stays under 500 lines.

## Consequences

- A C/C++ member in a file several requirements tag now has member drift, per definition.
- On the first `sync` after an upgrade a C/C++ key moves from the file to the definition. A
  key with no recorded hash is skipped, so the upgrade reports no drift; that `sync` baselines it.
- What the reader does not see stays whole-file: a definition produced by a macro, K&R
  definitions, Objective-C. These are misses, not false drift.
- `CORE_LOGICAL_BUDGET` rises from 6,828 to 6,840: `memberspans.py` is core (its imports and
  docstring) and `locks.py` gains the dispatch. The reader itself is lazy. The physical total
  is 20,353, under its 21,000 ceiling.
- JS, TS, Java and the other brace languages keep the whole-file hash.

## Revisit when

- A false drift is traced to a wrong C/C++ span: then the case becomes a test and the reader
  narrows, or that construct falls back to the file.
- A repository in another brace language asks for the same: then its own reader, with its own
  tests, not a widening of this one.
