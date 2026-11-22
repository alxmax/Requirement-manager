// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1145
/* The Report page as Markdown, for a deliverable kept beside the map instead
 * of in a temporary folder: the same numbers, every list in full. English,
 * like the engine's own reports. */

const pct = (a, b) => (b ? Math.round((100 * a) / b) : 0);
const val = (v) => (v == null ? "not measured" : String(v));

export function reportMarkdown(c, repo, rows) {
  const L = [];
  const tr = c.trace;
  L.push(`# ${repo ? repo + ": " : ""}Report`, "");
  L.push("## Summary", "");
  if (c.health) {
    L.push(`- Health ${c.health.score}/100: ${c.health.healthy} of `
      + `${c.health.scored} requirements green.`);
  }
  L.push(`- ${c.confirmed} of ${c.total} live requirements are confirmed.`);
  if (c.audit) {
    L.push(`- An audit read ${c.audit.reviewed} of the ${c.audit.planned} `
      + "planned requirements.");
  }
  L.push("", "## How it was checked", "");
  const m = c.method;
  const stamp = [m.at && `Map written ${m.at}.`, m.engine && `Engine ${m.engine}.`,
    m.branch && `Branch ${m.branch}.`].filter(Boolean).join(" ");
  L.push(`- ${stamp ? stamp + " " : ""}${m.requirements} requirements and `
    + `${m.files} tagged files read.`);
  if (c.audit) {
    L.push(`- Audit session: ${c.audit.reviewed}/${c.audit.planned} read, `
      + `band ${c.audit.band}.`);
  }
  L.push("", "## Results in numbers", "", "| Indicator | Value |", "|---|---|");
  const row = (k, v) => L.push(`| ${k} | ${val(v)} |`);
  row("Open bugs", c.bugs.open.length);
  row("Bugs by priority", Object.entries(c.bugs.byPrio)
    .map(([p, n]) => `${p} ${n}`).join(", ") || "0");
  row("Fixed bugs", c.bugs.fixed);
  row("Questions (High / Medium / Low)",
    `${c.questions.high} / ${c.questions.medium} / ${c.questions.low}`);
  row("Confirmed, no implements", tr.noImplConfirmed.length);
  row("Draft, no implements", tr.noImplDraft.length);
  row("Code, no tested-by", tr.noTest.length);
  row("Cases with no verifies", tr.unprovenCases);
  row("Tests that cannot fail", c.vacuous == null ? null : c.vacuous.length);
  row("Dangling tags", c.dangling == null ? null : c.dangling.length);
  row("Drift", c.drift == null ? null : c.drift.length);
  if (c.coverage) {
    const v = c.coverage;
    row("Code files with a tag", `${v.tagged_files}/${v.code_files} `
      + `(${pct(v.tagged_files, v.code_files)}%)`);
    row("Production files watched for drift", `${v.drift_files}/`
      + `${v.production_files} (${pct(v.drift_files, v.production_files)}%)`);
  }
  L.push("", "## Problem types", "");
  rows.forEach(([label, list, ids, n]) => {
    const items = (list || []).map((x) => (typeof x === "string" ? x
      : x.id + (x.gap ? ` (${x.gap})` : "")
        + (x.tests && x.tests.length ? ` -> ${x.tests.join(", ")}` : "")));
    L.push(`- **${label}**: ${list == null ? "not measured"
      : (n ?? list.length)}${items.length ? " - " + items.join(", ") : ""}`);
  });
  L.push("", "## Top 10 questions", "");
  c.top.forEach((q, i) => L.push(`${i + 1}. [${q.prio}] ${q.id} (${q.kind}): `
    + q.text));
  L.push("", "## Recommendations", "");
  if (!c.recommendations.length) L.push("Nothing is open.");
  c.recommendations.forEach((r, i) => L.push(`${i + 1}. ${r.n} ${r.text}`));
  L.push("", "## Deliverables", "");
  c.deliverables.forEach((d) => L.push(`- \`${d.path}\`: ${d.what}`));
  return L.join("\n") + "\n";
}
