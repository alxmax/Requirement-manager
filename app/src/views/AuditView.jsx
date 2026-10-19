// implements: ARCH-VIEWER-007
// implements: REQ-AUDITRUN-1108
/* The audit session (ADR-0076): the plan with its seed, each planned
 * requirement's runs and decision, the counters, and every rate as k/n with
 * its Wilson 95% interval. Everything shown is what `sync` copied from
 * requirements/_audit.json; the view computes nothing the engine did not. */
import { AUDIT } from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";

const STATE_TONE = {
  "not reviewed": "var(--fg-faint)",
  "reviewed once": "var(--cov-partial)",
  "reviewed twice": "var(--cov-partial)",
  decided: "var(--cov-tested)",
};
const BAND_TONE = {
  continue: "var(--cov-tested)",
  "change the method": "var(--cov-partial)",
  stop: "var(--status-error)",
};
const RATES = [
  ["precision", "Copilot precision", "B / (B + F_copilot)"],
  ["miss_rate", "Miss rate", "random set: requirements with M / reviewed"],
  ["agreement", "Agreement", "findings whose two runs agree"],
];
const COUNTER_ORDER = ["B", "F_copilot", "G", "A", "F_tool", "M", "U", "ok",
  "undecided"];

const CARD = {
  border: "1px solid var(--border-soft)", borderRadius: 8, padding: "10px 14px",
  minWidth: 180, flex: "1 1 0",
};
const MONO = { fontFamily: "var(--font-mono)", fontSize: 12 };
const ROW = { display: "flex", gap: 12, flexWrap: "wrap", margin: "10px 0" };

/** "k/n" and "95% lo–hi", or the reason there is nothing to judge.
 * implements: REQ-AUDITRUN-1108 */
export function rateText(r) {
  if (!r || !r.n) return { main: "0/0", sub: "nothing to count yet" };
  const pct = (x) => x.toFixed(2);
  return { main: `${r.k}/${r.n}`,
    sub: `95% ${pct(r.lo)}–${pct(r.hi)}` + (r.judged ? "" : " · not judged") };
}

function RateCard({ rate, label, how, t }) {
  const txt = rateText(rate);
  return (
    <div style={CARD}>
      <div style={{ color: "var(--fg-muted)", fontSize: 12 }}>{t(label)}</div>
      <div style={{ fontSize: 22, fontWeight: 600 }}>{txt.main}</div>
      <div style={MONO}>{txt.sub}</div>
      <div style={{ color: "var(--fg-faint)", fontSize: 11 }}>{how}</div>
    </div>
  );
}

function FindingCell({ findings }) {
  if (!findings.length) return <span style={{ color: "var(--fg-faint)" }}>—</span>;
  return (
    <ul className="finding-qs" style={{ margin: 0 }}>
      {findings.map((f, i) => (
        <li key={i} style={MONO}>
          {f.clause === null ? "whole" : "clause " + f.clause}
          {" · "}{f.labels.join(" / ")}
          {" → "}<b>{f.counter || "undecided"}</b>
        </li>
      ))}
    </ul>
  );
}

export function AuditView({ openSpec }) {
  const { t } = useI18n();
  if (!AUDIT) {
    return (
      <div className="main"><div className="prob-empty">
        <div><b>{t("No audit session in this map.")}</b></div>
      </div></div>
    );
  }
  const { plan, reviewed, counters, rates, band, problems } = AUDIT;
  return (
    <div className="main">
      <div className="tabbar">
        <span className="tab on">{t("Audit session")}</span>
        <div className="tab-legend" style={MONO}>
          {t("plan {d} · seed {s} · {r} ranked + {n} random",
            { d: plan.date, s: plan.seed, r: plan.ranked, n: plan.random })}
        </div>
      </div>
      <div className="problems">
        <div style={ROW}>
          <div style={CARD}>
            <div style={{ color: "var(--fg-muted)", fontSize: 12 }}>{t("Band")}</div>
            <div className="audit-band"
              style={{ fontSize: 18, fontWeight: 600,
                color: BAND_TONE[band] || "var(--fg-muted)" }}>{band}</div>
            <div style={MONO}>
              {t("reviewed {a} of {b}", { a: reviewed.total,
                b: plan.ranked + plan.random })}
            </div>
          </div>
          {RATES.map(([key, label, how]) => (
            <RateCard key={key} rate={rates[key]} label={label} how={how} t={t} />
          ))}
        </div>
        <div style={{ ...ROW, ...MONO }} className="audit-counters">
          {COUNTER_ORDER.map((c) => (
            <span key={c}>{c} <b>{counters[c] ?? 0}</b></span>
          ))}
        </div>
        {problems.length > 0 && (
          <div className="prob-chip" style={{ cursor: "default" }}>
            <Icon name="triangle-alert" size={14}
              style={{ color: "var(--status-error)" }} />
            {" "}{t("{n} entries in _audit.json are not counted",
              { n: problems.length })}
          </div>
        )}
        <table className="audit-table" style={{ width: "100%", fontSize: 13 }}>
          <thead><tr>
            <th align="left">{t("Requirement")}</th><th align="left">{t("Set")}</th>
            <th align="left">{t("State")}</th><th align="left">{t("Runs")}</th>
            <th align="left">{t("Findings")}</th>
          </tr></thead>
          <tbody>
            {AUDIT.requirements.map((row) => (
              <tr key={row.id} className="audit-row">
                <td><a className="prob-id" style={{ cursor: "pointer" }}
                  onClick={() => openSpec(row.id)}>{row.id}</a></td>
                <td>{row.set}</td>
                <td className={"audit-state"}
                  style={{ color: STATE_TONE[row.state] }}>{row.state}</td>
                <td style={MONO}>{row.runs}</td>
                <td><FindingCell findings={row.findings} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
