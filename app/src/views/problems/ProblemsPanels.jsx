// implements: ARCH-VIEWER-007
import { Icon } from "../../lib/icons.jsx";
import { Pill, statusKind } from "../../lib/ui.jsx";
import { useI18n } from "../../lib/i18n.jsx";

const COUNT = { marginLeft: 6, opacity: .7, fontFamily: "var(--font-mono)", fontSize: 11 };

export function ProblemTabBar({ filter, setFilter, counts, gateMsg }) {
  const { t } = useI18n();
  const Tab = ({ k, label, n }) => (
    <button className={"tab" + (filter === k ? " on" : "")} onClick={() => setFilter(k)}>
      {label}{n != null && <span style={COUNT}>{n}</span>}
    </button>
  );
  return (
    <div className="tabbar">
      <Tab k="ALL" label={t("All")} n={counts.all} />
      <Tab k="ERROR" label={t("Errors")} n={counts.ERROR || 0} />
      <Tab k="WARN" label={t("Warnings")} n={counts.WARN || 0} />
      <Tab k="QUESTION" label={t("Questions")} n={counts.QUESTION || 0} />
      <Tab k="REVIEW" label={t("Review")} n={counts.REVIEW || 0} />
      <div className="tab-legend">{gateMsg}</div>
    </div>
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

const EMPTY_NOTE = {
  marginTop: 6, color: "var(--fg-muted)", font: "var(--text-small)", maxWidth: 460,
};

export function ProblemsEmpty({ filter, t }) {
  return (
    <div className="prob-empty">
      <Icon name="shield-check" size={26} style={{ color: "var(--cov-tested)" }} />
      <div>
        <b>{filter === "ALL" ? t("Nothing to fix.") : t("Nothing in this tab.")}</b>
        <div style={EMPTY_NOTE}>
          {filter === "ALL"
            ? t("The gate reports no errors, warnings or review items for this registry.")
            : t("Other tabs may still have open items.")}
        </div>
      </div>
    </div>
  );
}
