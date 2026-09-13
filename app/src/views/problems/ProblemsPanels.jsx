// implements: ARCH-VIEWER-007
import { Icon } from "../../lib/icons.jsx";
import { Pill, statusKind } from "../../lib/ui.jsx";
import { useI18n } from "../../lib/i18n.jsx";

export function ProblemTabBar({ filter, setFilter, counts, designCount, gateMsg }) {
  const { t } = useI18n();
  const Tab = ({ k, label, n }) => (
    <button className={"tab" + (filter === k ? " on" : "")} onClick={() => setFilter(k)}>
      {label}{n != null && <span style={{ marginLeft: 6, opacity: .7, fontFamily: "var(--font-mono)", fontSize: 11 }}>{n}</span>}
    </button>
  );
  return (
    <div className="tabbar">
      <Tab k="ALL" label={t("All")} n={counts.all} />
      <Tab k="ERROR" label={t("Errors")} n={counts.ERROR || 0} />
      <Tab k="WARN" label={t("Warnings")} n={counts.WARN || 0} />
      <Tab k="QUESTION" label={t("Questions")} n={counts.QUESTION || 0} />
      <Tab k="REVIEW" label={t("Review")} n={counts.REVIEW || 0} />
      {designCount > 0 && <Tab k="DESIGN" label={t("Design")} n={designCount} />}
      <div className="tab-legend">{gateMsg}</div>
    </div>
  );
}

export function DesignProblemsPanel({ byPillar, advice }) {
  const { t } = useI18n();
  return (
    <>
      <div className="prob-chip" style={{ cursor: "default" }}>
        {t("Advisory only — a candidate is a shape worth a look, never a defect, and this never enters the gate.")}
      </div>
      {Object.keys(byPillar).sort().map((pillar) => {
        const rows = byPillar[pillar];
        const kinds = [...new Set(rows.map((f) => f.kind))].sort();
        return (
          <div key={pillar}>
            <div className="prob-head" style={{ margin: "14px 0 6px", textTransform: "capitalize" }}>
              <b>{pillar}</b>
              <span style={{ marginLeft: 6, opacity: .7, fontFamily: "var(--font-mono)", fontSize: 11 }}>{rows.length}</span>
            </div>
            {rows.map((f, i) => (
              <div className="prob-row" key={i}>
                <span className="prob-sev sev-REVIEW">{f.kind}</span>
                <div className="prob-body">
                  <div className="prob-head"><span className="prob-id">{f.name}</span></div>
                  <div className="prob-msg">{f.detail}</div>
                </div>
                <span className="prob-loc">{f.file}:{f.line}</span>
              </div>
            ))}
            {kinds.filter((k) => advice[k]).map((k) => (
              <div className="prob-fix" key={k} style={{ margin: "4px 0 0 4px" }}>
                <Icon name="arrow-right" size={13} /> {advice[k]}
              </div>
            ))}
          </div>
        );
      })}
    </>
  );
}

export function ProblemRow({ p, openSpec, t }) {
  return (
    <div className={"prob-row" + (p.sev === "QUESTION" ? " question-row" : "")}
      onClick={() => !p.noSpec && p.id !== "—" && openSpec(p.id)}>
      <span className={"prob-sev sev-" + p.sev}>{p.sev === "QUESTION" ? t("ASKED") : p.sev}</span>
      <div className="prob-body">
        <div className="prob-head">
          <span className="prob-id">{p.id}</span>
          <span className="prob-title">{p.title}</span>
          {p.status && <Pill kind={statusKind(p.status)}>{p.status}</Pill>}
        </div>
        {p.questions
          ? <ul className="finding-qs">{p.questions.map((q, j) => <li key={j}>{q}</li>)}</ul>
          : <div className="prob-msg">{p.msg}</div>}
        <div className="prob-fix"><Icon name="arrow-right" size={13} /> {p.fix}</div>
      </div>
      {p.loc && <span className="prob-loc">{p.loc}</span>}
    </div>
  );
}

export function ProblemsEmpty({ filter, t }) {
  return (
    <div className="prob-empty">
      <Icon name="shield-check" size={26} style={{ color: "var(--cov-tested)" }} />
      <div>
        <b>{filter === "ALL" ? t("Nothing to fix.") : t("Nothing in this tab.")}</b>
        <div style={{ marginTop: 6, color: "var(--fg-muted)", font: "var(--text-small)", maxWidth: 460 }}>
          {filter === "ALL"
            ? t("The gate reports no errors, warnings or review items for this registry.")
            : t("Other tabs may still have open items.")}
        </div>
      </div>
    </div>
  );
}
