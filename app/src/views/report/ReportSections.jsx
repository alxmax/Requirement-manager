// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1139
// implements: REQ-VIEWER-1153
// implements: REQ-VIEWER-1145
/* The Report's tables: the numbers, the problem types, the top questions,
 * the recommendations and the deliverables. Every section takes one `ctx`
 * ({ c, t, openSpec, full }): the report, the translator, what opens a
 * requirement, and whether every list prints out in full. */

import { ReportCharts } from "./ReportCharts.jsx";

export const NOT_MEASURED = "not measured";
const MONO = { fontFamily: "var(--font-mono)", fontSize: 12 };
const PRIO_CLASS = { high: "structure", medium: "count", low: "wording" };
export const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
const share = (a, b) => `${pct(a, b)}% (${a}/${b})`;
const rateSub = (r) => (r && r.n ? `${r.k}/${r.n} (${pct(r.k, r.n)}%)` : null);

/** The requirements whose cases a test that cannot fail closes. */
const vacuousIds = (list) => [...new Set(list.flatMap((v) =>
  v.cases.map((x) => x.split("#")[0])))].sort();

/** A count's requirements behind a chip that opens them; on paper, open. */
export function Ids({ rows, label, ctx }) {
  if (!rows || !rows.length) return null;
  const { t, openSpec, full } = ctx;
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
      <summary>{label ? `${rows.length} ${t(label)}`
        : t("{n} requirements", { n: rows.length })}</summary>
      {list}
    </details>
  );
}

/** `chip(rows, label)` for one section. */
export const chipper = (ctx) => (rows, label) => (
  <Ids key={label} rows={rows} label={label} ctx={ctx} />);

/** Every requirement with an open question, once. */
export const questionIds = (qi) => [...new Set([...qi.high, ...qi.medium, ...qi.low])].sort();

/** Indicator | value, a chip row under a value whose requirements open. */
export function Numbers({ ctx }) {
  const { c, t } = ctx;
  const tr = c.trace, cov = c.coverage, q = c.questions, qi = c.questionIds;
  const chip = chipper(ctx);
  const allQ = questionIds(qi);
  const prios = Object.entries(c.bugs.byPrio).map(([p, n]) => `${p} ${n}`)
    .join(" · ");
  const rows = [
    ...(c.audit ? [
      ["Read by the audit", share(c.audit.reviewed, c.audit.planned)],
      ["Agreement between runs", rateSub(c.audit.rates.agreement)],
      ["Audit precision", rateSub(c.audit.rates.precision)],
      ["Audit findings", String(c.findings.reduce((n, f) => n + f.n, 0)),
        c.findings.map((f) => chip(f.ids, f.kind))],
    ] : []),
    ["Open bugs", `${c.bugs.open.length}${prios ? ` (${prios})` : ""}`],
    ["Fixed bugs", String(c.bugs.fixed)],
    ["Questions", t("{n} on {m} requirements ({h} High, {md} Medium, {l} Low)",
      { n: q.high + q.medium + q.low, m: allQ.length, h: q.high,
        md: q.medium, l: q.low }),
    [chip(allQ, "all"), chip(qi.high, "High"), chip(qi.medium, "Medium"),
      chip(qi.low, "Low")]],
    ["Confirmed, no implements", String(tr.noImplConfirmed.length),
      [chip(tr.noImplConfirmed, "requirements")]],
    ["Draft, no implements", String(tr.noImplDraft.length),
      [chip(tr.noImplDraft, "requirements")]],
    ["Code, no tested-by", String(tr.noTest.length), c.tiers
      ? [chip(tr.noTest, "all"), chip(c.tiers.A, "tier A"),
        chip(c.tiers.B, "tier B"), chip(c.tiers.C, "tier C")]
      : [chip(tr.noTest, "requirements")]],
    ["Cases with no verifies", String(tr.unprovenCases),
      [chip(tr.unproven, "requirements")]],
    ["Tests that cannot fail", c.vacuous && String(c.vacuous.length),
      c.vacuous && [chip(vacuousIds(c.vacuous), "requirements")]],
    ["Dangling tags", c.dangling == null ? null : String(c.dangling.length)],
    ["Drift", c.drift == null ? null : String(c.drift.length)],
    ...(cov ? [
      ["Code files with a tag", share(cov.tagged_files, cov.code_files)],
      ["Production files watched for drift",
        share(cov.drift_files, cov.production_files)],
    ] : []),
    ...(c.health ? [["Health score", t("{s} ({a} of {b} requirements green)",
      { s: c.health.score, a: c.health.healthy, b: c.health.scored })]] : []),
  ];
  return (
    <>
    <table className="rep-table rep-kv">
      <tbody>
        {rows.map(([label, value, chips]) => (
          <tr key={label}>
            <td>{t(label)}</td>
            <td>
              {value == null ? t(NOT_MEASURED) : value}
              {chips && chips.some(Boolean)
                && <div className="rep-chips">{chips}</div>}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
    <ReportCharts c={c} />
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
    ["Tests that cannot fail", c.vacuous && c.vacuous.map((v) =>
      `${v.file}:${v.line} ${v.test} (${v.kind}) -> ${v.cases.join(", ")}`),
    null],
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

export function Types({ ctx }) {
  const { c, t, full } = ctx;
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
              {ids && <Ids rows={ids} ctx={ctx} />}
              {!ids && list && (full ? list : list.slice(0, 20)).map((l, i) => (
                <div key={i} style={MONO}>{l}</div>))}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function Top({ ctx }) {
  const { c, t, openSpec } = ctx;
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

export function Recs({ ctx }) {
  const { c, t } = ctx;
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

export function Deliverables({ ctx }) {
  const { c, t } = ctx;
  return (
    <>
      <p>{t("Paths are relative to the requirements folder; keep them in "
        + "the repository, not in a temporary folder.")}</p>
      <table className="rep-table">
        <tbody>
          {c.deliverables.map((d) => (
            <tr key={d.path}>
              <td style={MONO}>{d.path}</td>
              <td colSpan={2}>{t(d.what)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
