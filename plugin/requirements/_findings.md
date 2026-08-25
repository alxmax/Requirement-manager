# Open findings

> 2 open verify-intent item(s) across 1 requirement(s), aggregated from each requirement's `## WHAT — Verify intent` section by `reqmap.py findings`.
>
> These are open questions raised while reconstructing intent from code - NOT confirmed bugs. Resolve each by fixing the code or promoting the behavior into a Contract line. Run the AI triage pass (see SKILL.md) and drop a `_findings_triage.json` beside this file for a verified, prioritized view.

---

## REQ-TRANSLATE-044 - Opt-in requirement-content translation  (2)

- The stopword lists in `_RO_STOPWORDS`/`_EN_STOPWORDS` are small and generic (chosen for a majority-vote signal across a whole corpus, not sentence-level precision). Good enough as shipped, or should they grow before this is used on a much larger or more code-heavy corpus?
- `translate` currently supports exactly `ro`/`en`. Worth generalizing the language set now, or wait for a second real consumer language to shape the API?

