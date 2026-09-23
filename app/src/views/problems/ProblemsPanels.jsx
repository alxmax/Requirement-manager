// implements: ARCH-VIEWER-007
import { useState } from "react";
import { Icon } from "../../lib/icons.jsx";
import { REQ_BY_ID } from "../../lib/data.js";
import { Pill, statusKind } from "../../lib/ui.jsx";
import { useI18n } from "../../lib/i18n.jsx";

const COUNT = {
  marginLeft: 6, opacity: .7, fontFamily: "var(--font-mono)", fontSize: 11,
};

export function ProblemTabBar({
  filter, setFilter, counts, designCount, healthCount, gateMsg,
}) {
  const { t } = useI18n();
  const Tab = ({ k, label, n }) => (
    <button className={"tab" + (filter === k ? " on" : "")}
      onClick={() => setFilter(k)}>
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
      {healthCount != null && (
        <Tab k="HEALTH" label={t("Health")} n={healthCount} />
      )}
      {designCount > 0 && (
        <Tab k="DESIGN" label={t("Design")} n={designCount} />
      )}
      <div className="tab-legend">{gateMsg}</div>
    </div>
  );
}

function DesignRow({ f }) {
  return (
    <div className="prob-row">
      <span className="prob-sev sev-REVIEW">{f.kind}</span>
      <div className="prob-body">
        <div className="prob-head">
          <span className="prob-id">{f.name}</span>
        </div>
        <div className="prob-msg">{f.detail}</div>
      </div>
      <span className="prob-loc">{f.file}:{f.line}</span>
    </div>
  );
}

/** One OOP pillar: its findings, then the advice for each kind of
 *  finding in it. */
function PillarGroup({ pillar, rows, advice }) {
  const kinds = [...new Set(rows.map((f) => f.kind))]
    .sort().filter((k) => advice[k]);
  return (
    <div>
      <div className="prob-head"
        style={{ margin: "14px 0 6px", textTransform: "capitalize" }}>
        <b>{pillar}</b>
        <span style={COUNT}>{rows.length}</span>
      </div>
      {rows.map((f, i) => <DesignRow key={i} f={f} />)}
      {kinds.map((k) => (
        <div className="prob-fix" key={k} style={{ margin: "4px 0 0 4px" }}>
          <Icon name="arrow-right" size={13} /> {advice[k]}
        </div>
      ))}
    </div>
  );
}

/** A row of filter chips: `All` plus one per key, each with its count.
 * implements: REQ-VIEWER-1084 */
function ChipRow({ counts, total, value, setValue, label }) {
  const { t } = useI18n();
  const keys = [null, ...Object.keys(counts).sort()];
  return (
    <div style={CHIPS}>
      {keys.map((k) => (
        <button type="button" key={k || "all"}
          className={"ex-chip" + (value === k ? " on" : "")}
          aria-pressed={value === k}
          onClick={() => setValue(k)}>
          {k ? label(k) : t("All")}
          <span style={COUNT}>{k ? counts[k] : total}</span>
        </button>
      ))}
    </div>
  );
}

const CHIPS = {
  display: "flex", flexWrap: "wrap", gap: 6, margin: "8px 0 4px",
};

export function DesignProblemsPanel({
  byPillar, advice, initialPillar = null,
}) {
  // implements: REQ-VIEWER-1084
  const { t } = useI18n();
  const [pillar, setPillar] = useState(initialPillar);
  const counts = Object.fromEntries(
    Object.entries(byPillar).map(([k, v]) => [k, v.length]));
  const total = Object.values(counts).reduce((a, n) => a + n, 0);
  const shown = Object.keys(byPillar).sort()
    .filter((k) => !pillar || k === pillar);
  const note = "Advisory only — a candidate is a shape worth a look, never a "
    + "defect, and this never enters the gate.";
  return (
    <>
      <div className="prob-chip" style={{ cursor: "default" }}>{t(note)}</div>
      <ChipRow counts={counts} total={total} value={pillar}
        setValue={setPillar} label={(k) => k} />
      {shown.map((k) => (
        <PillarGroup key={k} pillar={k}
          rows={byPillar[k]} advice={advice} />
      ))}
    </>
  );
}

const AXIS_FIX = {
  "not confirmed": "Read it, then set `status: confirmed` in its "
    + "frontmatter.",
  "not implemented": "Add an `implements:` tag to the code that does "
    + "it.",
  "not tested": "Tag the test that checks it `# tested-by: <id>`.",
  "open question": "Answer it, then fold the answer into the "
    + "Description.",
  drift: "Re-check its members; `sync --accept-drift` once the code "
    + "still holds.",
};

/** A row whose only failing axis is confirmation — the Review tab already
 * lists it, so the Health tab leaves it out. */
export function onlyUnconfirmed(u) {
  return u.why.length === 1 && u.why[0] === "not confirmed";
}

/** One requirement that is not green, as a problem row. */
function healthProblem(u) {
  return {
    id: u.id, title: (REQ_BY_ID[u.id] || {}).title || "",
    status: u.status,
    sev: u.why.includes("not implemented") ? "ERROR" : "WARN",
    msg: u.why.join(" · "),
    fix: u.why.map((w) => AXIS_FIX[w] || "").join(" "),
  };
}

/** The rows behind the Health reading: every scored requirement that is
 * not green, filterable by the axis it fails, then every waiver.
 * implements: REQ-VIEWER-1084 */
export function HealthPanel({ health, openSpec, initialAxis = null }) {
  const { t } = useI18n();
  const [axis, setAxis] = useState(initialAxis);
  const all = health.unhealthy || [];
  const rows = all.filter((u) => !onlyUnconfirmed(u));
  const inReview = all.length - rows.length;
  const exempt = health.exempt_ids || [];
  const counts = {};
  rows.forEach((u) => u.why.forEach((w) => {
    counts[w] = (counts[w] || 0) + 1;
  }));
  const shown = axis ? rows.filter((u) => u.why.includes(axis)) : rows;
  const note = "Requirements not green on every axis — confirmed, "
    + "implemented, tested, no open question, no drift.";
  return (
    <>
      <div className="prob-chip" style={{ cursor: "default" }}>
        {t(note)}
        {inReview > 0 && <>{" "}{t("{n} only await confirmation — see "
          + "Review.", { n: inReview })}</>}
      </div>
      <ChipRow counts={counts} total={rows.length} value={axis}
        setValue={setAxis} label={(k) => t(k)} />
      {shown.map((u) => (
        <ProblemRow key={u.id} p={healthProblem(u)} openSpec={openSpec}
          t={t} />
      ))}
      {exempt.length > 0 && (
        <div className="prob-head" style={{ margin: "14px 0 6px" }}>
          <b>{t("Exempt")}</b><span style={COUNT}>{exempt.length}</span>
        </div>
      )}
      {exempt.map((e) => (
        <ProblemRow key={"x" + e.id} openSpec={openSpec} t={t} p={{
          id: e.id, title: (REQ_BY_ID[e.id] || {}).title || "",
          sev: "REVIEW", msg: e.keys.join(", "),
          fix: "A waiver: remove it once the finding it silences is "
            + "fixed." }} />
      ))}
      {shown.length === 0 && exempt.length === 0
        && <ProblemsEmpty filter="HEALTH" t={t} />}
    </>
  );
}

export function ProblemRow({ p, openSpec, t }) {
  return (
    <div className={"prob-row" + (p.sev === "QUESTION" ? " question-row" : "")}
      onClick={() => !p.noSpec && p.id !== "—" && openSpec(p.id)}>
      <span className={"prob-sev sev-" + p.sev}>
        {p.sev === "QUESTION" ? t("ASKED") : p.sev}
      </span>
      <div className="prob-body">
        <div className="prob-head">
          <span className="prob-id">{p.id}</span>
          <span className="prob-title">{p.title}</span>
          {p.status && <Pill kind={statusKind(p.status)}>{p.status}</Pill>}
        </div>
        {p.questions
          ? (
            <ul className="finding-qs">
              {p.questions.map((q, j) => <li key={j}>{q}</li>)}
            </ul>
          )
          : <div className="prob-msg">{p.msg}</div>}
        <div className="prob-fix">
          <Icon name="arrow-right" size={13} /> {p.fix}
        </div>
      </div>
      {p.loc && <span className="prob-loc">{p.loc}</span>}
    </div>
  );
}

const EMPTY_NOTE = {
  marginTop: 6, color: "var(--fg-muted)",
  font: "var(--text-small)", maxWidth: 460,
};

export function ProblemsEmpty({ filter, t }) {
  return (
    <div className="prob-empty">
      <Icon name="shield-check" size={26}
        style={{ color: "var(--cov-tested)" }} />
      <div>
        <b>
          {filter === "ALL" ? t("Nothing to fix.") : t("Nothing in this tab.")}
        </b>
        <div style={EMPTY_NOTE}>
          {filter === "ALL"
            ? t(
              "The gate reports no errors, warnings or review items for "
              + "this registry.",
            )
            : t("Other tabs may still have open items.")}
        </div>
      </div>
    </div>
  );
}
