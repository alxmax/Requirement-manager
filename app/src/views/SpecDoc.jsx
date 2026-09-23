// implements: ARCH-VIEWER-007
/* SpecDoc — one requirement, rendered in full. Was `SpecView.jsx`, whose
   own tab was a 220px flat nav beside this component; the Explorer
   shows the SAME component beside a hierarchy tree with filters, a
   breadcrumb and the link panel, so the tab was the poorer half of a
   duplicate. The document stayed; the tab went. */
// implements: REQ-TRANSLATE-1080
// implements: REQ-VIEWER-944
import { Pill, statusKind, mdInline, reqLinkProps } from "../lib/ui.jsx";
import { openQuestions } from "../lib/tree.js";
import { useI18n, translatedText } from "../lib/i18n.jsx";
import { TranslatedProse, CovStrip, SpecMeta } from "./spec/SpecParts.jsx";

function TranslatedBadge() {
  return (
    <span className="i18n-badge"
      title={"Machine-translated, not reviewed by the author — the "
        + "source .md is the artifact of record."}>
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

const PRIORITY_BADGE = {
  display: "inline-flex", alignItems: "center", font: "var(--text-caption)",
  fontSize: 12,
  fontWeight: 600, padding: "3px 10px", borderRadius: "var(--radius-pill)",
  whiteSpace: "nowrap",
};

function PriorityBadge({ priority }) {
  const c = PRIORITY_COLOR[priority];
  if (!c) return null;
  return (
    <span style={{ ...PRIORITY_BADGE, background: c.bg, color: c.color }}>
      {priority}
    </span>
  );
}

export const ENFORCED = {
  confirmed: true, "in-progress": true, implemented: true,
};

/** A list of Markdown-inline bullets whose requirement ids are links. */
function MdList({ items, onNav }) {
  return (
    <ul {...reqLinkProps(onNav)}>
      {items.map((c, i) => (
        <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(c) }} />
      ))}
    </ul>
  );
}

const Lines = ({ text }) => (
  <div className="gwt">
    {text.split("\n").map((ln, i) => <div key={i}>{ln}</div>)}
  </div>
);

function CasesBody({ r, acceptance, onNav }) {
  if (acceptance.isTranslated) return <Lines text={acceptance.text} />;
  if (r.gwt) return <Lines text={r.gwt} />;
  return <MdList items={r.acc || []} onNav={onNav} />;
}

const MUTED = { color: "var(--fg-muted)" };

/** Where the requirement lives in code, or why it has no code. */
function MembersBody({ r, t }) {
  if (r.members.length) {
    return r.members.map((m, i) => (
      <div className="member" key={i}>
        <span className="role">{m.role}:</span> {m.loc}
      </div>
    ));
  }
  if (r.layer === "need" || r.layer === "aggregate") {
    const why = t("(satisfied-by other requirements — no direct code)");
    return <div className="member" style={MUTED}>{why}</div>;
  }
  if (ENFORCED[r.status]) {
    const why = t("(no members found — orphan)");
    return (
      <div className="member" style={{ color: "var(--status-error)" }}>
        {why}
      </div>
    );
  }
  const why = t("(not linked to code yet — not enforced at this status)");
  return <div className="member" style={MUTED}>{why}</div>;
}

function RisksSection({ r, t }) {
  if (!r.risks || !r.risks.length) return null;
  const row = { font: "var(--text-body)", color: "var(--fg-secondary)" };
  return (
    <div className="sec">
      <div className="eyebrow warn">{t("Risk — recommended action")}</div>
      {r.risks.map((rk, i) => (
        <div className="member" key={i} style={row}>
          <b style={{ color: "var(--fg)" }}>{rk.signal}</b> — {rk.advice}</div>
      ))}
    </div>
  );
}

function Eyebrow({ label, extra, translated }) {
  return (
    <div className="eyebrow">
      {label} {extra}{translated && <TranslatedBadge />}
    </div>
  );
}

export function SpecDoc({ r, onNav, head = null, after = null }) {
  const { t, locale } = useI18n();
  if (!r) return null;
  const questions = openQuestions(r);
  const title = translatedText(r, locale, "title", r.title);
  const intent = translatedText(r, locale, "intent", r.intent);
  const contract = translatedText(r, locale, "contract");
  const acceptance = translatedText(r, locale, "acceptance");
  const intentHtml = { __html: mdInline(intent.text) };
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
          <Eyebrow label={t("Description")} extra={<span className="rule" />}
                   translated={contract.isTranslated} />
          {contract.isTranslated
            ? <TranslatedProse text={contract.text} onNav={onNav} skipQuote />
            : <MdList items={r.contract} onNav={onNav} />}
        </div>
        {intent.text && r.intent && (
          <div className="sec why-sec">
            <div className="eyebrow">
              {t("Why — Intent")}{" "}
              <span>
                {r.layer === "bus" ? "foundation" : "feature"}
                {intent.isTranslated && <TranslatedBadge />}
              </span>
            </div>
            <p className="blockquote" {...reqLinkProps(onNav)}
               dangerouslySetInnerHTML={intentHtml} />
          </div>
        )}
        <div className="sec">
          <Eyebrow label={t("Cases")}
                   extra={<><span className="rule" /> {t("= tests")}</>}
                   translated={acceptance.isTranslated} />
          <CasesBody r={r} acceptance={acceptance} onNav={onNav} />
        </div>
        <div className="sec">
          <div className="eyebrow">{t("Where — Members in code")}</div>
          <div className="members-box"><MembersBody r={r} t={t} /></div>
        </div>
        {questions.length > 0 && (
          <div className="sec">
            <div className="eyebrow warn">
              {t("Open questions — verify intent")}
            </div>
            <MdList items={questions} onNav={onNav} />
          </div>
        )}
        <RisksSection r={r} t={t} />
        {after}
      </div>
    </div>
  );
}
