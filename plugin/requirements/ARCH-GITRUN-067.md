---
id: ARCH-GITRUN-067
status: confirmed
level: architecture
layer: bus
owner: Alex
satisfies: [SYS-GATE-102]
---

# Talking to git

## Description
> Six different checks ask git a question — is this file tracked, what changed since a
> ref, where is the work-tree root, what is the remote, is the tree dirty — and every
> answer is advisory. None of them may raise, and none of them may turn "git could not
> tell me" into "the answer is no". When each call site decided that for itself they
> disagreed about the details that decide whether a check fails open, and the
> disagreement was invisible until it ran on a machine with a different console codec.

Every bullet below is binding.
- One runner issues every git command in the engine, with one decoding rule and one
  fail-open contract, and a `None` return is the only way a caller learns git could not
  answer. [[REQ-GITRUN-993]]

## Cases
CASE-1 — a question git cannot answer returns None, never an exception
  Given  a directory that is not a git work tree
  When   any git-backed check runs against it
  Then   it returns its fail-open value and nothing propagates out

CASE-2 — the work-tree root has one answer
  Given  a repository entered from a sub-directory
  When   two different features resolve the root
  Then   both resolve it through the same call and agree

CASE-3 — no feature reaches git on its own
  Given  the engine source
  When   it is searched for a process start
  Then   the runner is the only place one happens


--------------------


---
id: REQ-GITRUN-993
status: confirmed
level: code
layer: bus
owner: Alex
satisfies: [ARCH-GITRUN-067]
---

# One runner for every git question

## Description
> `_git` exists because eleven call sites had each written the same six lines and got
> them subtly different. The difference that mattered was the decoding: with `text=True`
> and no `encoding=`, Python decodes git's output with the LOCALE codec, so on a Windows
> console a non-ASCII path or remote URL either mojibakes or raises inside a bare
> `except` — and the caller reads the empty result as "nothing found". A check failing
> open, silently, on one platform. Three sites carried `encoding="utf-8"` because
> somebody had been bitten by exactly that; eight did not.

Every bullet below is binding.
- `_git` runs one git command and returns its stdout, or `None` when git is absent, the
  directory is not a work tree, the command exits non-zero, or the call times out.
- `_git` decodes with UTF-8, and strictly: output git cannot hand over as UTF-8 surfaces
  as `None`, never as replacement characters that silently fail to match a real path.
- `_git_root` returns the work tree containing a directory, or that directory itself when
  git cannot say, so every feature that needs the repository root resolves it identically.
- `_git_remote_url` returns `remote.origin.url` or the empty string, and is the only
  place that asks.
- No other code in the engine starts a git process.

## Cases
CASE-1 — a non-zero exit reads as no answer
  Given  a git command that fails
  When   `_git` runs it
  Then   it returns `None` rather than an empty string, so a caller can tell "git said
         nothing" from "git could not be asked"

CASE-2 — a missing git is not an exception
  Given  an environment where the git executable cannot be started
  When   `_git` runs
  Then   it returns `None`

CASE-3 — the root falls back to the directory it was given
  Given  a directory outside any work tree
  When   `_git_root` runs on it
  Then   it returns that directory unchanged

CASE-4 — the engine starts no git process anywhere else
  Given  the engine source
  When   it is searched for `subprocess.run` and `subprocess.check_output`
  Then   the only occurrence is inside `_git`
