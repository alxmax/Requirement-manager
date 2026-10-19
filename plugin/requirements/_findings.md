# Open findings

> 1 open verify-intent item(s) across 1 requirement(s), aggregated from each requirement's `## WHAT — Verify intent` section by `reqmap.py sync`.
>
> These are open questions raised while reconstructing intent from code - NOT confirmed bugs. Resolve each by fixing the code or promoting the behavior into a Contract line. Run the AI triage pass (see SKILL.md) and drop a `_findings_triage.json` beside this file for a verified, prioritized view.

---

## REQ-DESIGN-952 - The `design` report  (1)

- **Should a Python file that does not parse count as clean in the design score?**
  - a) No: it leaves the score, and the report names it. *(recommended)*
  - b) No: it counts as one file with a candidate.
  - c) Yes: it stays clean, as today.
  - d) Yes, but the line and file-length standards still run on it.
  - *Default:* stays c). A file the review cannot read raises the score.
  - *Context:* The score is the share of files with no candidate, and an unreadable file has none.
  - *Recommendation source:* the draft scan's rule, where a partial scan never reads as clean.
  - *For the developer:* `design_report.py:26` returns `[]` before `writing_standards`; [[REQ-EXTRACT-1099]]; `python scripts/reqmap.py ask --design`.

