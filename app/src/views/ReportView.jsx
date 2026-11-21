// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1139
// implements: REQ-VIEWER-1145
/* One page of what is open: a summary, how it was checked, the numbers, the
 * problem types, the ten most important questions and what to do next. It
 * prints as a PDF through the browser's dialog, every list out in full, and
 * downloads as Markdown, so the deliverable outlives the browser tab. */
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { REPO } from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";
import { computeReport } from "../lib/report.js";
import { reportMarkdown } from "../lib/reportMarkdown.js";

const NOT_MEASURED = "not measured";
const MONO = { fontFamily: "var(--font-mono)", fontSize: 12 };
const PRIO_CLASS = { high: "structure", medium: "count", low: "wording" };
const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);

/** A count's requirements behind a chip that opens them; on paper, open. */
function Ids({ rows, openSpec, full, t }) {
  if (!rows || !rows.length) return null;
  const list = (
    <div className="rep-ids">
      {rows.map((r) => {
        const id = typeof r === "string" ? r : r.id;
        const extra = r.gap ? ` (${r.gap})` : r.tests && r.tests.length
          ? ` → ${r.tests.join(", ")}` : "";
        return (
          <button key={id} type="button" className="dep-link"
            onClick={() => openSpec && openSpec(id)}>{id}{extra}</button>
        );
      })}
    </div>
  );
  if (full) return list;
  return (
    <details className="rep-chip">
      <summary>{t("{n} requirements", { n: rows.length })}</summary>
      {list}
    </details>
  );
}

function Num({ label, value, sub, t }) {
  return (
    <div className="rep-num">
      <b>{value == null ? t(NOT_MEASURED) : value}</b>
      <span>{t(label)}</span>
      {sub && <span style={MONO}>{sub}</span>}
    </div>
  );
}

/** The largest open count, named, for the summary's last sentence. */
function largest(c, t) {
  const items = [
    [c.bugs.open.length, t("open bugs")],
    [c.questions.high, t("High questions")],
    [c.trace.noImplConfirmed.length + c.trace.noImplDraft.length,
      t("requirements with no code")],
    [c.trace.noTest.length, t("requirements with no test")],
    [c.trace.unprovenCases, t("unproven cases")],
    ...c.findings.map((f) => [f.n, t("audit findings") + ": " + f.kind]),
  ].sort((a, b) => b[0] - a[0]);
  return items[0][0] ? `${items[0][1]} (${items[0][0]})` : null;
}

function Summary({ c, t }) {
  const parts = [];
  if (c.health) {
    parts.push(t("Health {s}/100: {a} of {b} requirements green.",
      { s: c.health.score, a: c.health.healthy, b: c.health.scored }));
  }
  parts.push(t("{a} of {b} live requirements are confirmed.",
    { a: c.confirmed, b: c.total }));
  if (c.audit) {
    parts.push(t("An audit read {a} of the {b} planned requirements.",
      { a: c.audit.reviewed, b: c.audit.planned }));
  }
  parts.push(t("Open: bugs {bugs}, High questions {high}, missing trace "
    + "tags {tags}.", {
    bugs: c.bugs.open.length, high: c.questions.high,
    tags: c.trace.noImplConfirmed.length + c.trace.noImplDraft.length
      + c.trace.noTest.length + c.trace.unprovenCases,
  }));
  const big = largest(c, t);
  parts.push(big ? t("The largest open item: {x}.", { x: big })
    : t("Nothing is open."));
  return <p className="rep-summary">{parts.join(" ")}</p>;
}

function Method({ c, t }) {
  const m = c.method;
  return (
    <>
      <p>
        {t("Map written {at}, engine {e}.", {
          at: m.at || t(NOT_MEASURED), e: m.engine || t(NOT_MEASURED),
        })}{m.branch ? " " + t("Branch {b}.", { b: m.branch }) : ""}{" "}
        {t("{r} requirements and {f} tagged files read.",
          { r: m.requirements, f: m.files })}
      </p>
      <ul>
        <li>{t("Gate link sync: every tag names a requirement (RM001).")}</li>
        <li>{t("Drift lock: a confirmed contract changed since the lock.")}</li>
        <li>{t("Test links: `implements:`, `tested-by:` and `# verifies:` tags.")}</li>
        <li>{t("`clarify`: questions read from each requirement's own text.")}</li>
        <li>{t("Bug files: the open and fixed bugs the repository keeps.")}</li>
        {c.audit && (
          <li>{t("Audit session: {a} of {b} planned requirements read "
            + "(ranked by risk, plus a random sample), band {band}.",
          { a: c.audit.reviewed, b: c.audit.planned, band: c.audit.band })}</li>
        )}
      </ul>
    </>
  );
}

function rateSub(r) {
  return r && r.n ? `${r.k}/${r.n}` : null;
}

function Numbers({ c, t }) {
  const tr = c.trace, cov = c.coverage;
  return (
    <>
      {c.audit && (
        <div className="rep-nums">
          <Num t={t} label="read by the audit"
            value={`${pct(c.audit.reviewed, c.audit.planned)}%`}
            sub={`${c.audit.reviewed}/${c.audit.planned}`} />
          <Num t={t} label="audit findings"
            value={c.findings.reduce((n, f) => n + f.n, 0)} />
          <Num t={t} label="agreement between runs"
            value={rateSub(c.audit.rates.agreement)} />
          <Num t={t} label="audit precision"
            value={rateSub(c.audit.rates.precision)} />
        </div>
      )}
      <div className="rep-nums">
        <Num t={t} label="open bugs" value={c.bugs.open.length} />
        <Num t={t} label="fixed bugs" value={c.bugs.fixed} />
        <Num t={t} label="High questions" value={c.questions.high} />
        <Num t={t} label="Medium questions" value={c.questions.medium} />
        <Num t={t} label="Low questions" value={c.questions.low} />
      </div>
      {Object.keys(c.bugs.byPrio).length > 0 && (
        <p style={MONO}>{Object.entries(c.bugs.byPrio)
          .map(([p, n]) => `${p} ${n}`).join(" · ")}</p>
      )}
      <div className="rep-nums">
        <Num t={t} label="confirmed, no implements"
          value={tr.noImplConfirmed.length} />
        <Num t={t} label="draft, no implements" value={tr.noImplDraft.length} />
        <Num t={t} label="code, no tested-by" value={tr.noTest.length} />
        <Num t={t} label="cases with no verifies" value={tr.unprovenCases} />
        <Num t={t} label="dangling tags"
          value={c.dangling == null ? null : c.dangling.length} />
        <Num t={t} label="drift" value={c.drift == null ? null : c.drift.length} />
      </div>
      <div className="rep-nums">
        <Num t={t} label="code files with a tag"
          value={cov ? `${pct(cov.tagged_files, cov.code_files)}%` : null}
          sub={cov ? `${cov.tagged_files}/${cov.code_files}` : null} />
        <Num t={t} label="production files watched for drift"
          value={cov ? `${pct(cov.drift_files, cov.production_files)}%` : null}
          sub={cov ? `${cov.drift_files}/${cov.production_files}` : null} />
      </div>
    </>
  );
}

/** [label, list, ids, n] per problem kind with something in it. */
export function problemRows(c, t = (s) => s) {
  const tr = c.trace, h = c.hygiene, tiers = c.tiers;
  return [
    ["Dangling tags (RM001)", c.dangling, null],
    ["Confirmed, no implements", tr.noImplConfirmed, tr.noImplConfirmed],
    ["Drift", c.drift, c.drift],
    ["Requirements with a High question", c.highReqs, c.highReqs],
    ...c.findings.map((f) => [t("Audit finding") + ": " + f.kind, f.ids,
      f.ids, f.n]),
    ["Code, no tested-by", tr.noTest, tr.noTest],
    ...(tiers ? [
      ["tested-by suggestion, tier A (a test already names it)", tiers.A,
        tiers.A],
      ["tested-by suggestion, tier B (a test is paired by name)", tiers.B,
        tiers.B],
      ["tested-by suggestion, tier C (no test found)", tiers.C, tiers.C],
    ] : []),
    ["Cases with no verifies", tr.unproven, tr.unproven, tr.unprovenCases],
    ["Draft, no implements", tr.noImplDraft, tr.noImplDraft],
    ...(h ? [
      ["Same text under two ids", h.duplicates.map((p) => p.join(" = ")),
        null],
      ["Confirmed with a title and no clause", h.title_only_confirmed,
        h.title_only_confirmed],
    ] : []),
    ...c.designRules.map((r) => [t("Design rule") + ": " + r.id
      + (r.why ? " (" + r.why + ")" : ""),
    r.hits.map((x) => `${x.file}:${x.line}`), null, r.count]),
    ...c.rules.map((r) => [r.rule, r.ids, r.ids, r.n]),
  ].filter(([, list, , n]) => list == null || (n ?? list.length) > 0);
}

function Types({ c, t, openSpec, full }) {
  const rows = problemRows(c, t);
  if (!rows.length) return <p>{t("Nothing is open.")}</p>;
  return (
    <table className="rep-table">
      <tbody>
        {rows.map(([label, list, ids, n]) => (
          <tr key={label}>
            <td><b>{t(label)}</b></td>
            <td style={MONO}>
              {list == null ? t(NOT_MEASURED) : (n ?? list.length)}
            </td>
            <td>
              {ids && <Ids rows={ids} openSpec={openSpec} full={full} t={t} />}
              {!ids && list && (full ? list : list.slice(0, 20)).map((l, i) => (
                <div key={i} style={MONO}>{l}</div>))}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Top({ c, t, openSpec }) {
  if (!c.top.length) return <p>{t("No open questions here.")}</p>;
  return (
    <ol className="rep-top">
      {c.top.map((q, i) => (
        <li key={i}>
          <span className={"prob-sev basis-" + PRIO_CLASS[q.prio]}>
            {t(q.prio)}
          </span>{" "}
          <button type="button" className="dep-link"
            onClick={() => openSpec && openSpec(q.id)}>{q.id}</button>
          {" · "}<code>{q.kind}</code>
          <div>{q.text}</div>
        </li>
      ))}
    </ol>
  );
}

function Recs({ c, t }) {
  if (!c.recommendations.length) {
    return <p>{t("Nothing is open: no recommendation.")}</p>;
  }
  return (
    <ol className="rep-recs">
      {c.recommendations.map((r, i) => (
        <li key={i}><b>{r.n}</b> {t(r.text)}</li>
      ))}
    </ol>
  );
}

/** The six sections, the same on screen and on paper. */
export function ReportBody({ c, openSpec, full = false }) {
  const { t } = useI18n();
  const sec = (title, body) => (
    <section className="rep-sec"><h2>{t(title)}</h2>{body}</section>);
  return (
    <>
      {sec("Summary", <Summary c={c} t={t} />)}
      {sec("How it was checked", <Method c={c} t={t} />)}
      {sec("Results in numbers", <Numbers c={c} t={t} />)}
      {sec("Problem types", <Types c={c} t={t} openSpec={openSpec} full={full} />)}
      {sec("Top 10 questions", <Top c={c} t={t} openSpec={openSpec} />)}
      {sec("Recommendations", <Recs c={c} t={t} />)}
    </>
  );
}

function download(name, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/markdown" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function ReportView({ openSpec }) {
  const { t } = useI18n();
  const c = computeReport();
  const [printing, setPrinting] = useState(false);
  useEffect(() => {
    if (!printing) return undefined;
    const done = () => setPrinting(false);
    window.addEventListener("afterprint", done);
    window.print();
    return () => window.removeEventListener("afterprint", done);
  }, [printing]);
  return (
    <div className="main">
      <div className="tabbar">
        <span className="tab on">{t("Report")}</span>
        <div className="tab-legend">
          <button type="button" className="btn btn-ghost rep-md"
            onClick={() => download("report.md",
              reportMarkdown(c, REPO, problemRows(c)))}>
            {t("Export Markdown")}
          </button>{" "}
          <button type="button" className="btn btn-secondary"
            onClick={() => setPrinting(true)}>
            <Icon name="file-text" size={14} /> {t("Export PDF")}
          </button>
        </div>
      </div>
      <div className="problems rep-page">
        <ReportBody c={c} openSpec={openSpec} />
      </div>
      {printing && createPortal(
        <div className="bug-report rep-print">
          <h1>{REPO ? `${REPO}: ` : ""}{t("Report")}</h1>
          <ReportBody c={c} full />
        </div>, document.body)}
    </div>
  );
}
