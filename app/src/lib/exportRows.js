// implements: REQ-VIEWER-1152
/* The rows a spreadsheet export holds, as plain text. Bugs: priority,
 * requirement, description. Questions: priority, requirement, question, and
 * the answer options when the question offers any. Highest priority first. */

/** Markdown and wiki links reduced to the words a cell shows. */
export function plain(s) {
  return String(s ?? "")
    .replace(/\[\[([^\]]+)\]\]/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/[*_`]+/g, "")
    .replace(/\s+\n/g, "\n")
    .trim();
}

const PRIO_RANK = { P0: 0, P1: 1, P2: 2, P3: 3, P4: 4,
  high: 0, medium: 1, low: 2 };
const byPrio = (a, b) => (PRIO_RANK[a[0]] ?? 9) - (PRIO_RANK[b[0]] ?? 9)
  || String(a[1]).localeCompare(String(b[1]), undefined, { numeric: true });

/** One row per bug: `[prio, requirement, description]`. The description is
 * the title, then the why on its own line when the bug has one. */
export function bugRows(bugs) {
  return (bugs || []).map((b) => [
    `${b.prio || ""}${b.estimated ? "*" : ""}`,
    plain(b.source || ""),
    [plain(b.title), plain(b.why)].filter(Boolean).join("\n"),
  ]).sort(byPrio);
}

/** The options a question offers, written after `Options:`, `Choices:` or
 * `Answer options:`, or as `(a) … (b) …`. Empty when it offers none. */
export function answerOptions(text) {
  const s = plain(text);
  const tail = s.match(/\b(?:answer options|options|choices)\s*:\s*(.+)$/is);
  if (tail) return tail[1].trim();
  const lettered = s.match(/\(a\).+?\(b\).+$/is);
  return lettered ? lettered[0].trim() : "";
}

/** One row per open question: `[priority, requirement, question, options]`.
 * `qs` is the Questions page's `{ code, person, clarify }`, `keep` the
 * filter its tab applies to `clarify` questions, `verify` the origins the
 * tab shows. A person's question is High and an observed one Medium, as on
 * the page; a `clarify` question carries its own priority and its
 * suggestion is the answer it asks for. */
export function questionRows(qs, { keep = () => true, verify = ["person", "code"],
  priorityOf } = {}) {
  const rows = [];
  verify.forEach((origin) => (qs[origin] || []).forEach((r) =>
    r.questions.forEach((q) => rows.push([
      origin === "person" ? "high" : "medium", r.id, plain(q), answerOptions(q),
    ]))));
  (qs.clarify || []).forEach((r) => r.questions.filter(keep).forEach((q) =>
    rows.push([
      priorityOf ? priorityOf(q) : "low", r.id,
      [plain(q.question), q.quote ? `“${plain(q.quote)}”` : ""]
        .filter(Boolean).join("\n"),
      plain(q.suggest),
    ])));
  return rows.sort(byPrio);
}
