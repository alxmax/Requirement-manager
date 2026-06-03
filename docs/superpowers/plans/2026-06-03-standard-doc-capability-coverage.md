# Standard doc & prose capability coverage — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `reqmap` discover `.md`/`.html` capabilities and sync-check docs by default in every action, classifying each prose file into ignore / sync-only / capability-source buckets, without auto-canonizing unreviewed prose.

**Architecture:** Member scanning (`scan_members`) and the tag regex (`TAG_RE`) already cover `.md`/`.html` (incl. tags inside `<!-- -->` comments), and the drift gate already flags stale members — so bucket-2 sync-checking needs **no new engine code**. The only new engine logic is in the auto-draft path (`cmd_extract`): a `classify_prose()` bucketer plus a `_prose_facts()` scaffolder that drafts a `draft`-status stub from a prose file's title + `##` headings. `draft` is excluded from `ENFORCED`, so a post-upgrade draft flood cannot break any consumer's gate. The skill (`SKILL.md`) gains an advisory semantic doc-sync step (orchestrator-run, not engine).

**Tech Stack:** Python 3 stdlib only (`re`, `os`, `fnmatch`, `ast`), `unittest`. No external deps. Engine: `plugin/scripts/reqmap.py`. Tests: `plugin/scripts/test_reqmap.py`. Skill: `plugin/skills/requirement-manager/SKILL.md`.

**Pre-verified (consilium rider, confirmed by reading the code):**
- Rider #1 — `TAG_RE` (reqmap.py:23) is comment-agnostic and `.html` ∈ `CODE_EXTS` (reqmap.py:25); `scan_members` already finds tagged `.html`/`.md` as members. Task 4 adds a guard test, no production change.
- Rider #3 — `ENFORCED = {"in-progress","implemented","confirmed"}` (reqmap.py:29) excludes `draft`. Task 4 adds a guard test.
- Rider #2 — the prose scaffolder is the one genuinely new piece (Tasks 1–3).

**Run tests with:** `cd plugin/scripts && python -X utf8 test_reqmap.py` (the test file does `import reqmap as R`).

---

### Task 1: Classification constants + `classify_prose()`

**Files:**
- Modify: `plugin/scripts/reqmap.py` (add constants after `CODE_EXTS`, ~line 27; add function before `cmd_extract`, ~line 493)
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing test**

Add this class after the `Scanning`/ignore tests (after line 179):

```python
class ProseClassification(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def test_meta_files_are_ignored(self):
        for rel in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", "CONTRIBUTING.md",
                    "SKILL.md", "TODO.md", "LICENSE", "LICENSE.md",
                    "_map.md", "_findings.md", "_map.html"):
            self.assertEqual(R.classify_prose(rel), "ignore", rel)

    def test_readme_and_docs_and_html_are_sync_only(self):
        for rel in ("README", "README.md", "docs/senate.md",
                    "docs/sub/guide.md", "docs/architecture.html", "x.html"):
            self.assertEqual(R.classify_prose(rel), "sync_only", rel)

    def test_prompts_and_specs_are_capability(self):
        for rel in ("prompts/senators/aurelius.md", "specs/foo.md",
                    "modes/bar.md", "notes.md"):
            self.assertEqual(R.classify_prose(rel), "capability", rel)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugin/scripts && python -X utf8 -m unittest test_reqmap.ProseClassification -v`
Expected: FAIL with `AttributeError: module 'reqmap' has no attribute 'classify_prose'`

- [ ] **Step 3: Add the constants**

After `CODE_EXTS = (...)` block (reqmap.py line 26), add:

```python
# ---- prose auto-draft classification (cmd_extract) ----
# These buckets govern AUTO behavior (drafting) ONLY. scan_members still honors an
# explicit tag on ANY file, regardless of bucket — buckets never suppress a real tag.
PROSE_EXTS = (".md", ".html")
# Bucket 1 — meta/boilerplate: never auto-drafted, never sync-checked. Basename match.
META_IGNORE_NAMES = {"CLAUDE.md", "AGENTS.md", "GEMINI.md", "CONTRIBUTING.md",
                     "SKILL.md", "TODO.md"}
```

- [ ] **Step 4: Add the function**

Immediately before `def cmd_extract` (reqmap.py line 494), add:

```python
def classify_prose(rel):  # implements: REQ-EXTRACT-008
    """Bucket a POSIX-relative .md/.html path for the auto-draft path. Returns
    'ignore' (meta/boilerplate, invisible), 'sync_only' (README/docs/*.html — never
    drafted, but a drift- and semantic-checked member when explicitly tagged), or
    'capability' (prompt/spec prose — auto-drafted as a `draft` stub). Governs AUTO
    behavior only: scan_members still honors an explicit tag on any file."""
    base = os.path.basename(rel)
    # Bucket 1 — meta/boilerplate.
    if base in META_IGNORE_NAMES:
        return "ignore"
    if base == "LICENSE" or base.startswith("LICENSE."):
        return "ignore"
    if base.startswith("_"):                      # generated _map.*, _findings.md
        return "ignore"
    # Bucket 2 — sync-only.
    if base == "README" or base.startswith("README."):
        return "sync_only"
    if rel == "docs" or rel.startswith("docs/"):
        return "sync_only"
    if rel.endswith(".html"):                      # all HTML is an overview/derived doc
        return "sync_only"
    # Bucket 3 — capability source (prompts/specs/modes and other prose .md).
    return "capability"
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd plugin/scripts && python -X utf8 -m unittest test_reqmap.ProseClassification -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(reqmap): classify_prose bucketer for md/html auto-draft"
```

---

### Task 2: `_prose_facts()` title + heading extractor

**Files:**
- Modify: `plugin/scripts/reqmap.py` (add function before `cmd_extract`, after `classify_prose`)
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing test**

Add to the `ProseClassification` class (or a new class below it):

```python
class ProseFacts(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def test_markdown_frontmatter_title_and_headings(self):
        src = ("---\ntitle: Senator Aurelius\n---\n\n"
               "## Role\nrisk lens\n## Specialty\nreversibility\n### sub\n")
        title, heads = R._prose_facts(src)
        self.assertEqual(title, "Senator Aurelius")
        self.assertEqual(heads, ["Role", "Specialty"])  # H2 only, not H3

    def test_markdown_h1_title_when_no_frontmatter(self):
        title, heads = R._prose_facts("# My Cap\n\n## A\n## B\n")
        self.assertEqual(title, "My Cap")
        self.assertEqual(heads, ["A", "B"])

    def test_html_title_and_h2(self):
        src = "<title>Project Map</title><h2>Section One</h2><h2>Two</h2>"
        title, heads = R._prose_facts(src)
        self.assertEqual(title, "Project Map")
        self.assertEqual(heads, ["Section One", "Two"])

    def test_no_title_returns_none(self):
        title, heads = R._prose_facts("just text, no headings\n")
        self.assertIsNone(title)
        self.assertEqual(heads, [])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugin/scripts && python -X utf8 -m unittest test_reqmap.ProseFacts -v`
Expected: FAIL with `AttributeError: module 'reqmap' has no attribute '_prose_facts'`

- [ ] **Step 3: Add the function**

Immediately before `def cmd_extract` (after `classify_prose`), add:

```python
def _prose_facts(src):  # implements: REQ-EXTRACT-008
    """(title, [headings]) from markdown/HTML prose, for a draft scaffold.
    Title: markdown frontmatter `title:`, else first `# ` H1, else <title>/<h1>.
    Headings: markdown `## ` H2 lines, else <h2>. Returns (None, []) when absent.
    The scaffold lists headings as an authoring hint — never the contract."""
    meta, _body = parse_frontmatter(src)
    title = meta.get("title") or None
    headings = []
    for line in src.splitlines():
        s = line.strip()
        if title is None:
            m = re.match(r"#\s+(.+)", s)                      # markdown H1
            if m:
                title = m.group(1).strip()
                continue
            m = re.search(r"<(?:title|h1)[^>]*>(.*?)</(?:title|h1)>", s, re.I)
            if m:
                title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                continue
        m = re.match(r"##\s+(.+)", s)                         # markdown H2 (not H3)
        if m:
            headings.append(m.group(1).strip())
            continue
        m = re.search(r"<h2[^>]*>(.*?)</h2>", s, re.I)        # html H2
        if m:
            headings.append(re.sub(r"<[^>]+>", "", m.group(1)).strip())
    return title, headings
```

Note: `re.match(r"##\s+", "### x")` does not match (after `##`, `\s+` requires whitespace but finds `#`), so H3+ are correctly excluded. `re.match(r"#\s+", "## x")` likewise does not match H2 as a title.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd plugin/scripts && python -X utf8 -m unittest test_reqmap.ProseFacts -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(reqmap): _prose_facts title+heading extractor for prose drafts"
```

---

### Task 3: Extend `cmd_extract` to auto-draft bucket-3 prose

**Files:**
- Modify: `plugin/scripts/reqmap.py` (`cmd_extract`, lines 494-543)
- Test: `plugin/scripts/test_reqmap.py`

- [ ] **Step 1: Write the failing test**

Add this class below `ProseFacts`:

```python
class ProseExtract(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def _extract(self, d):
        reqs = R.load_requirements(os.path.join(d, "requirements"))
        members = R.scan_members(d, os.path.join(d, "requirements"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            R.cmd_extract(reqs, members, d, os.path.join(d, "requirements"))
        return os.path.join(d, "requirements")

    def test_capability_prose_is_drafted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "prompts", "aurelius.md"),
                   "---\ntitle: Aurelius\n---\n## Role\nx\n")
            rdir = self._extract(d)
            drafts = [f for f in os.listdir(rdir) if f.endswith(".md")]
            self.assertTrue(any("PROMPTS-AURELIUS" in f for f in drafts), drafts)

    def test_sync_only_and_meta_prose_not_drafted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "README.md"), "# Project\n## Overview\n")
            _write(os.path.join(d, "docs", "guide.md"), "# Guide\n## How\n")
            _write(os.path.join(d, "report.html"), "<title>R</title><h2>S</h2>")
            _write(os.path.join(d, "CLAUDE.md"), "# Claude\n## Rules\n")
            rdir = self._extract(d)
            drafts = [f for f in os.listdir(rdir) if f.endswith(".md")]
            for bad in ("README", "GUIDE", "REPORT", "CLAUDE"):
                self.assertFalse(any(bad in f for f in drafts), (bad, drafts))

    def test_explicitly_tagged_prose_not_redrafted(self):
        with tempfile.TemporaryDirectory() as d:
            # a sync-only README that the human linked to a requirement stays a member
            _write(os.path.join(d, "README.md"),
                   "# P\n<!-- generated-from: SENATE-SYNTH-001 -->\n")
            members = R.scan_members(d, None)
            self.assertIn("SENATE-SYNTH-001", members)   # rider #1 guard
            # and is never drafted (bucket 2)
            rdir = self._extract(d)
            drafts = [f for f in os.listdir(rdir) if f.endswith(".md")]
            self.assertFalse(any("README" in f for f in drafts), drafts)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd plugin/scripts && python -X utf8 -m unittest test_reqmap.ProseExtract -v`
Expected: FAIL — `test_capability_prose_is_drafted` fails (no prose draft written; current `cmd_extract` only drafts `.py/.js/.ts/.cpp/.c`).

- [ ] **Step 3: Implement the prose branch in `cmd_extract`**

In `cmd_extract`, replace the body of the `for fn in sorted(files):` loop. The current code (lines 504-541) starts:

```python
            if not fn.endswith((".py", ".js", ".ts", ".cpp", ".c")):
                continue
```

Change that guard so non-code prose falls through to a new branch instead of being skipped. Replace lines 504-505 with:

```python
            is_code = fn.endswith((".py", ".js", ".ts", ".cpp", ".c"))
            is_prose = fn.endswith(PROSE_EXTS)
            if not (is_code or is_prose):
                continue
```

Then, after the `rel = ...` / ignore / `if rel in tagged: continue` lines (currently 506-510), insert the prose classification gate immediately before `cap = base = _draft_id(rel)`:

```python
            if is_prose and classify_prose(rel) != "capability":
                continue                           # bucket 1/2 -> never auto-drafted
```

Finally, the file-writing block (lines 519-539) currently always writes the code stub. Wrap it so prose writes a prose stub. Replace lines 519-539 (from `with open(...) as f: src = f.read()` through the code-stub `f.write(...)`) with:

```python
            with open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore") as f:
                src = f.read()
            if is_prose:
                title, headings = _prose_facts(src)
                review = "REVIEW"   # intent is unrecoverable from prose — always author
                hint = "\n".join("  - {}".format(h) for h in headings) \
                    or "  - (no section headings detected)"
                with open(dest, "w", encoding="utf-8") as f:
                    f.write("---\nid: {cap}\nstatus: draft\nlayer: feature\n"
                            "owner: auto\ndepends_on: []\n"
                            "risk: 2  # REVIEW — prose capability, author the contract "
                            "before promoting\n---\n\n"
                            "# {title}\n\n"
                            "> DRAFT extracted from {rel} (prose capability). The source "
                            "prose is NOT the contract — author the normative behavior "
                            "below, then tag the source `# generated-from: {cap}` "
                            "(HTML: `<!-- generated-from: {cap} -->`) and promote.\n\n"
                            "## WHAT — Contract (normative)\n"
                            "- TODO: the capability this prose defines (author from "
                            "intent, do not copy the prose).\n\n"
                            "## WHAT — Verify intent (open questions for the human)\n"
                            "- TODO: which source sections are normative vs illustrative?\n\n"
                            "Source sections detected (authoring hint, not the contract):\n"
                            "{hint}\n\n"
                            "## HOW — Acceptance (= tests)\n"
                            "- TODO: Given/When/Then checks for the contract above.\n\n"
                            "## WHERE — Current implementation\n- {rel}\n".format(
                                cap=cap, title=(title or os.path.splitext(fn)[0]),
                                rel=rel, hint=hint))
            else:
                risk = _risk(src)
                review = "REVIEW" if risk >= 2 else "auto-baseline"
                with open(dest, "w", encoding="utf-8") as f:
                    # new emission schema (Contract / Verify-intent / Acceptance / Current-impl),
                    # matching cmd_new so a promoted draft needs no reshaping
                    f.write(f"---\nid: {cap}\nstatus: draft\nlayer: feature\n"
                            f"owner: auto\ndepends_on: []\n"
                            f"risk: {risk}  # {review} — author triage hint, not read by the engine\n---\n\n"
                            f"# {os.path.splitext(fn)[0]}\n\n"
                            f"> DRAFT extracted from {rel}. Describes observed behavior, "
                            f"not validated intent.\n\n"
                            f"## WHAT — Contract (normative)\n"
                            f"- TODO: the observed behavior (characterization — correctness UNVERIFIED).\n\n"
                            f"## WHAT — Verify intent (open questions for the human)\n"
                            f"- TODO: anything that looks like an accident (swallowed error, magic "
                            f"constant, dead branch) — intended, or a bug to fix?\n\n"
                            f"## HOW — Acceptance (= tests)\n"
                            f"- characterization: current behavior captured, correctness UNVERIFIED\n\n"
                            f"## WHERE — Current implementation\n- {rel}\n")
```

(The `else:` block is the original code stub, unchanged except for indentation — the `review`/`risk` computation moves inside it so the prose branch can set its own `review`.)

- [ ] **Step 4: Run the new tests to verify they pass**

Run: `cd plugin/scripts && python -X utf8 -m unittest test_reqmap.ProseExtract -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Run the FULL suite to confirm no regression**

Run: `cd plugin/scripts && python -X utf8 test_reqmap.py`
Expected: `OK` (all pre-existing tests + the new ones).

- [ ] **Step 6: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/scripts/test_reqmap.py
git commit -m "feat(reqmap): cmd_extract auto-drafts bucket-3 prose capabilities"
```

---

### Task 4: Guard tests for consilium rider #1 (HTML-comment tags) and #3 (draft non-enforced)

**Files:**
- Test only: `plugin/scripts/test_reqmap.py` (no production change — these lock in the two pre-verified assumptions)

- [ ] **Step 1: Write the guard tests**

Add this class below `ProseExtract`:

```python
class RiderGuards(unittest.TestCase):  # tested-by: REQ-EXTRACT-008
    def test_tag_inside_html_comment_is_a_member(self):  # rider #1
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "docs", "arch.html"),
                   "<!-- generated-from: SENATE-SYNTH-001 -->\n<h1>x</h1>\n")
            members = R.scan_members(d, None)
            self.assertIn("SENATE-SYNTH-001", members)
            roles = [r for (r, _f, _l) in members["SENATE-SYNTH-001"]]
            self.assertIn("generated-from", roles)

    def test_draft_status_is_not_enforced(self):  # rider #3
        self.assertNotIn("draft", R.ENFORCED)
        self.assertEqual(R.ENFORCED, {"in-progress", "implemented", "confirmed"})
```

- [ ] **Step 2: Run to verify they pass immediately (assumptions already hold)**

Run: `cd plugin/scripts && python -X utf8 -m unittest test_reqmap.RiderGuards -v`
Expected: PASS (2 tests) — confirms the two pre-verified assumptions and pins them against future regression.

- [ ] **Step 3: Commit**

```bash
git add plugin/scripts/test_reqmap.py
git commit -m "test(reqmap): guard html-comment tags + draft non-enforcement"
```

---

### Task 5: Update the `REQ-EXTRACT-008` requirement (same-commit authoring rule)

**Files:**
- Modify: `plugin/requirements/REQ-EXTRACT-008.md`

- [ ] **Step 1: Read the current requirement**

Run: `cat plugin/requirements/REQ-EXTRACT-008.md`
Note its existing Contract + Acceptance sections so the edit extends, not rewrites, them.

- [ ] **Step 2: Add the prose-extraction contract clauses**

In the `## WHAT — Contract` section, append these normative lines (keep existing ones):

```markdown
- `extract` shall also draft `draft`-status requirements from untagged **prose**
  capability files (`.md`/`.html`), classified by `classify_prose(rel)` into three
  buckets: `ignore` (meta/boilerplate — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
  `CONTRIBUTING.md`, `SKILL.md`, `TODO.md`, `LICENSE*`, `_`-prefixed), `sync_only`
  (`README*`, `docs/**`, every `*.html` — never drafted), and `capability`
  (everything else — drafted). Buckets govern auto-drafting only; an explicit tag
  on any file is always honored by `scan_members`.
- A prose draft shall be scaffolded from `_prose_facts(src)` (title + `##`
  headings); the headings are an authoring hint and the source prose is never the
  contract (so the prose may later drift freely from the authored requirement).
```

In the `## HOW — Acceptance` section, append:

```markdown
- Given a `prompts/foo.md` with no tag, When `extract` runs, Then a `DRAFT-...`
  requirement is written with `status: draft`.
- Given a `README.md`, `docs/guide.md`, `report.html`, or `CLAUDE.md`, When
  `extract` runs, Then no draft is written for it.
- Given any file tagged `generated-from: <ID>` inside an HTML comment, When
  `scan_members` runs, Then that file is a member of `<ID>`.
```

- [ ] **Step 3: Commit**

```bash
git add plugin/requirements/REQ-EXTRACT-008.md
git commit -m "docs(req): REQ-EXTRACT-008 covers prose bucket classification"
```

---

### Task 6: SKILL.md — document standard md/html coverage + advisory doc-sync

**Files:**
- Modify: `plugin/skills/requirement-manager/SKILL.md`

- [ ] **Step 1: Update the Commands description for `extract`**

Find the `extract` bullet under `## Commands` and replace it with:

```markdown
- `python scripts/reqmap.py extract`           — draft one requirement per untagged file. Covers **code** and **prose** (`.md`/`.html`) by default. Prose is bucketed by `classify_prose`: meta/boilerplate (`CLAUDE.md`, `SKILL.md`, `TODO.md`, `LICENSE*`, `_`-prefixed) is ignored; `README*`, `docs/**` and every `*.html` are **sync-only** (never drafted — tag them `generated-from: <ID>` to drift- and semantic-check them); everything else (prompts/specs) is drafted as `draft`. An explicit tag on any file is always honored.
```

- [ ] **Step 2: Add the three-bucket rule under Authoring rules**

After authoring rule 6 (the "Authoring is bidirectional" item), add a new subsection:

```markdown
### Prose & doc capabilities (the three buckets)

`extract`/`init` scan `.md`/`.html` by default and classify each:

1. **Ignore** — meta/boilerplate (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
   `CONTRIBUTING.md`, `SKILL.md`, `TODO.md`, `LICENSE*`, `_`-prefixed generated
   files) + anything in `.reqmapignore`. Invisible to reqmap.
2. **Sync-only** — `README*`, everything under `docs/**`, and every `*.html`.
   Never turned into a requirement. Tag it `# generated-from: <ID>` (HTML:
   `<!-- generated-from: <ID> -->`) to make it a member: the drift gate then flags
   it stale when its requirement changes, and the advisory doc-sync step verifies
   its claims still match the code.
3. **Capability source** — prompt/spec prose (`prompts/**`, `specs/**`, …).
   Auto-drafted as a `draft` stub from its title + `##` headings; review, edit and
   `promote`. `draft` is never enforced, so unreviewed prose is never canonized.
```

- [ ] **Step 3: Add the advisory doc-sync step to the menu actions**

In the menu `| Action | ... |` table, in the **regenerate map** row's command list, append after `map`:

```markdown
 → advisory doc-sync (read each sync-only doc tagged `generated-from`, compare its claims to the tagged requirement + implementing code, report mismatches)
```

And add a short paragraph under the table:

```markdown
**Advisory doc-sync (orchestrator step, not the engine).** After `map`, for each
sync-only doc (bucket 2) tagged `generated-from: <ID>`, the assistant reads the doc,
its requirement(s), and the implementing code, then reports concrete mismatches
(e.g. "HTML says quorum 6/9; code says 7/9"). This is judgment, not a gate — it
surfaces findings; it never blocks a commit. The engine's deterministic drift flag
(stale-on-change) is the hard half; this is the semantic half.
```

- [ ] **Step 4: Commit**

```bash
git add plugin/skills/requirement-manager/SKILL.md
git commit -m "docs(skill): standard prose coverage + advisory doc-sync step"
```

---

### Task 7: Version bump + CHANGELOG

**Files:**
- Modify: `plugin/scripts/reqmap.py` (`MAP_ENGINE_VERSION`, line 60)
- Modify: `plugin/.claude-plugin/plugin.json` (`version`)
- Modify: `.claude-plugin/marketplace.json` (the plugin's `version` entry, if present)
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump the engine version**

In `plugin/scripts/reqmap.py` line 60, change:

```python
MAP_ENGINE_VERSION = "2026-06-03.2"
```
to:
```python
MAP_ENGINE_VERSION = "2026-06-03.3"
```

- [ ] **Step 2: Bump the plugin manifest(s)**

In `plugin/.claude-plugin/plugin.json`, change `"version": "1.7.0"` → `"version": "1.8.0"`.
Run `cat .claude-plugin/marketplace.json` — if it pins the plugin version, bump it to `1.8.0` there too.

- [ ] **Step 3: Add a CHANGELOG entry**

Prepend under the top heading of `CHANGELOG.md`:

```markdown
## 1.8.0 — 2026-06-03

### Added
- `extract`/`init` now discover **prose** capabilities (`.md`/`.html`) by default,
  classified into three buckets via `classify_prose`: ignore (meta/boilerplate),
  sync-only (`README*`, `docs/**`, `*.html`), capability-source (prompts/specs).
- Capability-source prose is auto-drafted as a `draft` stub from its title + `##`
  headings (`_prose_facts`).
- Advisory doc-sync step in the skill: sync-only docs tagged `generated-from` are
  checked (deterministically via drift, semantically via an orchestrator step).

### Behavior change
- On first post-upgrade `init`/`extract`, repos with prompt/spec markdown will see
  new `draft` requirements. Drafts are **not** enforced by the gate (`draft` ∉
  `ENFORCED`), so this cannot break an existing `check`. Review, edit, `promote`
  the real ones; delete the rest. README/docs/HTML are never auto-drafted.
```

- [ ] **Step 4: Commit**

```bash
git add plugin/scripts/reqmap.py plugin/.claude-plugin/plugin.json .claude-plugin/marketplace.json CHANGELOG.md
git commit -m "chore(release): reqmap engine 2026-06-03.3, plugin 1.8.0"
```

---

### Task 8: Regenerate the plugin's own map, full suite, and sync to consumers

**Files:**
- Modify (generated): `plugin/requirements/_map.html`, `plugin/requirements/_map.md`, `plugin/requirements/_reqlock.json`
- Modify (synced): plugin cache `reqmap.py`, Senate `scripts/reqmap.py`

- [ ] **Step 1: Run the full test suite**

Run: `cd plugin/scripts && python -X utf8 test_reqmap.py`
Expected: `OK`.

- [ ] **Step 2: Regenerate the plugin's dogfooded map + lock**

The plugin repo dogfoods reqmap, with `requirements/` under `plugin/`. From `plugin/`:

Run:
```bash
cd plugin && python -X utf8 scripts/reqmap.py scan && \
python -X utf8 scripts/reqmap.py check --update-lock && \
python -X utf8 scripts/reqmap.py map
```
Expected: `0 errors`. (If the plugin's own `prompts/`/`docs/` now draft new prose requirements, that is expected — review them; they are this change dogfooding itself.)

- [ ] **Step 3: Run the gate freshness check**

Run: `cd plugin && python -X utf8 scripts/reqmap.py map --check`
Expected: exit 0 (committed map is fresh).

- [ ] **Step 4: Commit the regenerated artifacts**

```bash
git add plugin/requirements/_map.html plugin/requirements/_map.md plugin/requirements/_reqlock.json plugin/requirements/
git commit -m "chore(reqmap): regenerate dogfooded map for 1.8.0"
```

- [ ] **Step 5: Sync the engine to the cache + Senate consumer**

From the plugin repo root, propagate the new engine. (`sync_reqmap.sh` is the author tool; on Windows run the copies directly.)

```bash
cp plugin/scripts/reqmap.py "C:/Users/ALEX/.claude/plugins/cache/requirement-manager/requirement-manager/1.7.0/scripts/reqmap.py"
cp plugin/scripts/reqmap.py "C:/Users/ALEX/Desktop/Doc/Senate/scripts/reqmap.py"
```

Then verify the Senate consumer still gates clean on the new engine:
```bash
cd "C:/Users/ALEX/Desktop/Doc/Senate" && python -X utf8 scripts/reqmap.py check
```
Expected: `0 errors` (the 11 existing confirmed requirements are unaffected; prose drafts are new and non-enforced).

- [ ] **Step 6: Push the branch**

```bash
cd "C:/Users/ALEX/.claude/plugins/marketplaces/requirement-manager" && git push -u origin feat/standard-doc-capability-coverage
```

---

## Follow-up (separate change, NOT this plan)

Once 1.8.0 is synced, in the **Senate** repo run the new flow to actually cover the 9 senator prompts: `reqmap.py extract` drafts them → author each Contract + Given/When/Then acceptance → tag each prompt `# generated-from: <ID>` → `promote` → tag `README.md`/`docs/*.html` `generated-from` for sync-checking → regenerate map. That is requirement-authoring work in the consumer repo, tracked on its own branch.

## Self-Review

- **Spec coverage:** Goal 1 (standard discovery) → Tasks 1,3,6. Goal 2 (init non-empty on prose) → Task 3 (cmd_init calls cmd_extract; covered by `test_capability_prose_is_drafted`). Goal 3 (doc sync staged) → engine half pre-verified + Task 4 guard; skill half → Task 6. Goal 4 (meta never a requirement; README sync-only) → Tasks 1,3. Non-goals respected (no README auto-draft; only .md/.html; semantic check advisory). Rollout → Tasks 7,8. Requirement-update authoring rule → Task 5.
- **Placeholder scan:** all code steps carry full code; the only `TODO:` strings are intentional content *inside generated draft stubs* (matching the existing extract schema), not plan placeholders.
- **Type consistency:** `classify_prose(rel)` returns `"ignore"|"sync_only"|"capability"` — used identically in Task 3's gate. `_prose_facts(src)` returns `(title, headings)` — destructured the same way in Tasks 2 and 3. `PROSE_EXTS`/`META_IGNORE_NAMES` defined in Task 1, used in Tasks 1 and 3.
