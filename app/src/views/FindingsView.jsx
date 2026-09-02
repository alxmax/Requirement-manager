// implements: ARCH-VIEWER-007
/* FindingsView — the open verify-intent questions, and nothing else.
 *
 * Deliberately NOT folded into Problems. Problems is currently ~618 rows of
 * `draft`/`unreviewed` review noise; a real finding dropped in there is
 * invisible. This surface answers one question — "what did an author write down
 * as unresolved?" — and its rail badge is hidden at zero rather than rendered
 * as a proud `0`, because zero is the honest state of the corpus today (every
 * `verify` bullet in the export is the "None — …" placeholder the engine
 * filters out; see openQuestions in lib/tree.js). */
import { REQUIREMENTS } from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { Pill, statusKind } from "../lib/ui.jsx";
import { useI18n } from "../lib/i18n.jsx";
import { openQuestions } from "../lib/tree.js";

/** [{ r, questions }] for every requirement carrying a REAL open question. */
export function computeFindings(list = REQUIREMENTS) {
  const out = [];
  list.forEach((r) => {
    const q = openQuestions(r);
    if (q.length) out.push({ r, questions: q });
  });
  return out.sort((a, b) => a.r.id.localeCompare(b.r.id));
}

export function FindingsView({ openSpec }) {
  const { t } = useI18n();
  const found = computeFindings();
  const total = found.reduce((a, f) => a + f.questions.length, 0);

  if (!found.length) {
    return (
      <div className="main">
        <div className="tabbar">
          <span className="tab on">{t("Findings")}</span>
          <div className="tab-legend">{t("open `## WHAT — Verify intent` questions")}</div>
        </div>
        <div className="prob-empty">
          <Icon name="shield-check" size={22} style={{ color: "var(--status-confirmed)" }} />
          <div>
            <b>{t("No open questions.")}</b>
            <div style={{ marginTop: 6, color: "var(--fg-faint)", font: "var(--text-small)", maxWidth: 460 }}>
              {t("Every requirement's Verify-intent section is either empty or still carries the authored placeholder, which the engine does not count as a finding either.")}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main">
      <div className="tabbar">
        <span className="tab on">{t("Findings")}</span>
        <div className="tab-legend">
          {t("{n} open question(s) across {m} requirement(s)", { n: total, m: found.length })}
        </div>
      </div>
      <div className="problems">
        {found.map((f) => (
          <div className="prob-row finding-row" key={f.r.id} onClick={() => openSpec(f.r.id)}>
            <div className="prob-body">
              <div className="prob-head">
                <span className="prob-id">{f.r.id}</span>
                <span className="prob-title">{f.r.title}</span>
                <Pill kind={statusKind(f.r.status)}>{f.r.status}</Pill>
              </div>
              <ul className="finding-qs">
                {f.questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
              <div className="prob-fix">
                <Icon name="arrow-right" size={13} />
                {t("Answer it, fold the answer into the Description, then delete the bullet.")}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
