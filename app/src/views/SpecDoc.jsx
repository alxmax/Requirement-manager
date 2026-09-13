// implements: ARCH-VIEWER-007
/* SpecDoc — one requirement, rendered in full. Was `SpecView.jsx`, whose own tab
   was a 220px flat nav beside this component; the Explorer shows the SAME component
   beside a hierarchy tree with filters, a breadcrumb and the link panel, so the tab
   was the poorer half of a duplicate. The document stayed; the tab went. */
// implements: ARCH-TRANSLATE-044
// implements: REQ-VIEWER-944
import { Pill, statusKind, mdInline, reqLinkProps } from "../lib/ui.jsx";
import { openQuestions } from "../lib/tree.js";
import { useI18n, translatedText } from "../lib/i18n.jsx";
import { TranslatedProse, CovStrip, SpecMeta } from "./spec/SpecParts.jsx";

function TranslatedBadge() {
  return (
    <span className="i18n-badge"
      title="Machine-translated by `reqmap.py translate`; not reviewed by the author — the source .md is the artifact of record.">
      machine-translated, unreviewed
    </span>
  );
}

const PRIORITY_COLOR = {
  "must-have": { bg: "var(--status-error-bg)", color: "var(--status-error)" },
  "should-have": { bg: "var(--status-drift-bg)", color: "var(--status-drift)" },
  "could-have": { bg: "var(--cov-tested-bg)", color: "var(--cov-tested)" },
  "wont-have": { bg: "var(--status-draft-bg)", color: "var(--fg-muted)" },
};

function PriorityBadge({ priority }) {
  const c = PRIORITY_COLOR[priority];
  if (!c) return null;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", font: "var(--text-caption)", fontSize: 12, fontWeight: 600,
      padding: "3px 10px", borderRadius: "var(--radius-pill)", background: c.bg, color: c.color, whiteSpace: "nowrap",
    }}>{priority}</span>
  );
}

export const ENFORCED = { confirmed: true, "in-progress": true, implemented: true };

export function SpecDoc({ r, onNav, head = null, after = null }) {
  const { t, locale } = useI18n();
  if (!r) return null;
  const questions = openQuestions(r);
  const title = translatedText(r, locale, "title", r.title);
  const intent = translatedText(r, locale, "intent", r.intent);
  const contract = translatedText(r, locale, "contract");
  const acceptance = translatedText(r, locale, "acceptance");
  return (
    <div className="spec">
      <div className="spec-sheet">
        {head}
        <div className="head-row">
          <Pill kind={statusKind(r.status)}>{r.status}</Pill>
          <Pill kind={r.layer}>{r.layer}</Pill>
          {r.priority && <PriorityBadge priority={r.priority} />}
        </div>
        <h1>{title.text}{title.isTranslated && <TranslatedBadge />}</h1>
        <SpecMeta r={r} t={t} onNav={onNav} />
        <CovStrip r={r} />
        <div className="sec">
          <div className="eyebrow">{t("Description")} <span className="rule" />{contract.isTranslated && <TranslatedBadge />}</div>
          {contract.isTranslated
            ? <TranslatedProse text={contract.text} onNav={onNav} skipQuote />
            : <ul {...reqLinkProps(onNav)}>{r.contract.map((c, i) => <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(c) }} />)}</ul>}
        </div>
        {intent.text && r.intent && (
          <div className="sec why-sec">
            <div className="eyebrow">{t("Why — Intent")} <span>{r.layer === "bus" ? "foundation" : "feature"}{intent.isTranslated && <TranslatedBadge />}</span></div>
            <p className="blockquote" {...reqLinkProps(onNav)} dangerouslySetInnerHTML={{ __html: mdInline(intent.text) }} />
          </div>
        )}
        <div className="sec">
          <div className="eyebrow">{t("Cases")} <span className="rule" /> {t("= tests")}{acceptance.isTranslated && <TranslatedBadge />}</div>
          {acceptance.isTranslated
            ? <div className="gwt">{acceptance.text.split("\n").map((ln, i) => <div key={i}>{ln}</div>)}</div>
            : (r.gwt
              ? <div className="gwt">{r.gwt.split("\n").map((ln, i) => <div key={i}>{ln}</div>)}</div>
              : <ul {...reqLinkProps(onNav)}>{(r.acc || []).map((a, i) => <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(a) }} />)}</ul>)}
        </div>
        <div className="sec">
          <div className="eyebrow">{t("Where — Members in code")}</div>
          <div className="members-box">
            {r.members.length
              ? r.members.map((m, i) => <div className="member" key={i}><span className="role">{m.role}:</span> {m.loc}</div>)
              : (r.layer === "need" || r.layer === "aggregate")
                ? <div className="member" style={{ color: "var(--fg-muted)" }}>{t("(satisfied-by other requirements — no direct code)")}</div>
                : ENFORCED[r.status]
                  ? <div className="member" style={{ color: "var(--status-error)" }}>{t("(no members found — orphan)")}</div>
                  : <div className="member" style={{ color: "var(--fg-muted)" }}>{t("(not linked to code yet — not enforced at this status)")}</div>}
          </div>
        </div>
        {questions.length > 0 && (
          <div className="sec">
            <div className="eyebrow warn">{t("Open questions — verify intent")}</div>
            <ul {...reqLinkProps(onNav)}>{questions.map((q, i) => <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(q) }} />)}</ul>
          </div>
        )}
        {r.risks && r.risks.length > 0 && (
          <div className="sec">
            <div className="eyebrow warn">{t("Risk — recommended action")}</div>
            {r.risks.map((rk, i) => (
              <div className="member" key={i} style={{ font: "var(--text-body)", color: "var(--fg-secondary)" }}>
                <b style={{ color: "var(--fg)" }}>{rk.signal}</b> — {rk.advice}</div>
            ))}
          </div>
        )}
        {after}
      </div>
    </div>
  );
}
