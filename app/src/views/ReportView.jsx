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
import { PrintDoc, usePrinting, downloadBlob } from "../lib/exportDoc.jsx";
import {
  Deliverables, Numbers, Recs, Top, Types, chipper, pct, problemRows, questionIds,
} from "./report/ReportSections.jsx";

export { problemRows };

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

function Summary({ ctx }) {
  const { c, t } = ctx;
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
  return (
    <>
      <p className="rep-summary">{parts.join(" ")}</p>
      <KeyNumbers c={c} t={t} />
      <Conclusions ctx={ctx} />
    </>
  );
}

/** The few numbers a reader takes away, as tiles: the audit's reach, then
 * whatever is open. */
function KeyNumbers({ c, t }) {
  const q = c.questions, tr = c.trace;
  const tiles = [
    c.audit && [`${pct(c.audit.reviewed, c.audit.planned)}%`,
      t("of planned requirements read by the audit ({a} of {b})",
        { a: c.audit.reviewed, b: c.audit.planned })],
    c.coverage && [`${pct(c.coverage.tagged_files, c.coverage.code_files)}%`,
      t("code files with a tag")],
    [c.bugs.open.length, t("open bugs")],
    [q.high + q.medium + q.low, t("questions for requirement owners")],
    ...c.findings.slice(0, 2).map((f) => [f.n,
      t("audit findings") + ": " + f.kind]),
    [tr.noTest.length, t("requirements with code, no tested-by")],
  ].filter(Boolean);
  return (
    <div className="rep-nums rep-key">
      {tiles.map(([v, l]) => (
        <div key={l} className="rep-num"><b>{v}</b><span>{l}</span></div>))}
    </div>
  );
}

/** One bullet per open finding, its count in bold, and a chip per list
 * behind it. */
function Conclusions({ ctx }) {
  const { c, t } = ctx;
  const q = c.questions, qi = c.questionIds, tr = c.trace, tiers = c.tiers;
  const chip = chipper(ctx);
  const allQ = questionIds(qi);
  const items = [
    c.audit && [t("{a} of {b} planned requirements read ({p}%)", {
      a: c.audit.reviewed, b: c.audit.planned,
      p: pct(c.audit.reviewed, c.audit.planned) }),
    t("band {band}.", { band: c.audit.band }), []],
    c.bugs.open.length > 0 && [t("{n} open bugs.", { n: c.bugs.open.length }),
      Object.entries(c.bugs.byPrio).map(([p, n]) => `${p} ${n}`).join(", "),
      []],
    allQ.length > 0 && [t("{n} questions for requirement owners",
      { n: q.high + q.medium + q.low }),
    t("on {m} requirements: {h} High, {md} Medium, {l} Low.",
      { m: allQ.length, h: q.high, md: q.medium, l: q.low }),
    [chip(allQ, "all requirements"), chip(qi.high, "High"),
      chip(qi.medium, "Medium"), chip(qi.low, "Low")]],
    ...c.findings.map((f) => [t("{n} audit findings: {k}",
      { n: f.n, k: f.kind }), t("on {m} requirements.", { m: f.ids.length }),
    [chip(f.ids, "requirements")]]),
    tr.noTest.length > 0 && [t("{n} requirements have code but no tested-by",
      { n: tr.noTest.length }),
    tiers ? t("mostly tagging gaps when tier A dominates.") : "",
    [chip(tr.noTest, "all"), ...(tiers ? [chip(tiers.A, "tier A"),
      chip(tiers.B, "tier B"), chip(tiers.C, "tier C")] : [])]],
    tr.noImplConfirmed.length > 0 && [t("{n} confirmed requirements have no "
      + "code", { n: tr.noImplConfirmed.length }), "",
    [chip(tr.noImplConfirmed, "requirements")]],
  ].filter(Boolean);
  if (!items.length) return null;
  return (
    <>
      <p className="rep-lead">{t("Main conclusions:")}</p>
      <ul className="rep-concl">
        {items.map(([head, rest, chips]) => (
          <li key={head}><b>{head}</b>{rest ? " " + rest : ""}
            {chips.length > 0 && <div className="rep-chips">{chips}</div>}
          </li>
        ))}
      </ul>
    </>
  );
}

/** The build stamp as the map carries it: a part the map lacks is left
 * out, as the rail's footer does (the date and branch ride only in
 * `_map.html`, never in the committed `_map.json`). */
function stampText(m, t) {
  return [
    m.at && t("Map written {at}.", { at: m.at }),
    m.engine && t("Engine {e}.", { e: m.engine }),
    m.branch && t("Branch {b}.", { b: m.branch }),
  ].filter(Boolean).join(" ");
}

function Method({ c, t }) {
  const m = c.method;
  const stamp = stampText(m, t);
  return (
    <>
      <p>
        {stamp ? stamp + " " : ""}
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

/** The sections in order: the body and the table of contents read this. */
export const SECTIONS = ["Summary", "How it was checked", "Results in numbers",
  "Problem types", "Top 10 questions", "Recommendations", "Deliverables"];
const secId = (i) => `rep-sec-${i + 1}`;

/** The seven sections, the same on screen and on paper. */
export function ReportBody({ c, openSpec, full = false }) {
  const { t } = useI18n();
  const ctx = { c, t, openSpec, full };
  const bodies = [
    <Summary ctx={ctx} />, <Method c={c} t={t} />, <Numbers ctx={ctx} />,
    <Types ctx={ctx} />, <Top ctx={ctx} />, <Recs ctx={ctx} />,
    <Deliverables ctx={ctx} />,
  ];
  return (
    <>
      {SECTIONS.map((title, i) => (
        <section key={title} className="rep-sec" id={full ? undefined : secId(i)}>
          <h2 data-n={`${i + 1}.`}>{t(title)}</h2>{bodies[i]}
        </section>
      ))}
    </>
  );
}

/** Table of contents: one link per section, the one in view marked. */
function Toc({ t }) {
  const [on, setOn] = useState(0);
  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return undefined;
    const els = SECTIONS.map((_, i) => document.getElementById(secId(i)))
      .filter(Boolean);
    const io = new IntersectionObserver((entries) => {
      const seen = entries.filter((e) => e.isIntersecting)
        .map((e) => els.indexOf(e.target));
      if (seen.length) setOn(Math.min(...seen));
    }, { rootMargin: "0px 0px -70% 0px" });
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
  const go = (i) => {
    setOn(i);
    const el = document.getElementById(secId(i));
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  return (
    <nav className="rep-toc">
      <div className="rep-toc-h">{t("Contents")}</div>
      {SECTIONS.map((s, i) => (
        <button key={s} type="button" className={"rep-toc-i" + (on === i ? " on" : "")}
          onClick={() => go(i)}>{i + 1}. {t(s)}</button>
      ))}
    </nav>
  );
}

const download = (name, text) => downloadBlob(name, text, "text/markdown");

export function ReportView({ openSpec }) {
  const { t } = useI18n();
  const c = computeReport();
  const [printing, setPrinting] = usePrinting();
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
      <div className="rep-layout">
        <Toc t={t} />
        <div className="problems rep-page">
          <header className="rep-head">
            <h1>{REPO ? `${REPO}: ` : ""}{t("Report")}</h1>
            <div className="rep-meta">
              {[["Date", c.method.at], ["Branch", c.method.branch],
                ["Engine", c.method.engine], ["Audit", c.audit && c.audit.band]]
                .filter(([, v]) => v).map(([k, v], i) => (
                  <span key={k}>{i ? " | " : ""}<b>{t(k)}:</b> {v}</span>))}
            </div>
          </header>
          <ReportBody c={c} openSpec={openSpec} />
        </div>
      </div>
      {printing && (
        <PrintDoc title={`${REPO ? `${REPO}: ` : ""}${t("Report")}`}
          meta={[c.method.branch, c.method.engine, c.audit && c.audit.band]}>
          <div className="rep-page problems"><ReportBody c={c} full /></div>
        </PrintDoc>
      )}
    </div>
  );
}
