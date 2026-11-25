// tested-by: REQ-VIEWER-1151
// tested-by: REQ-VIEWER-1152
/* Render smoke test, part: the PDF and spreadsheet exports. Adopts what each
 * page needs, checks the buttons, the printed sheet and the workbook bytes,
 * then adopts the real export again with no audit and no bugs. */
import { renderToString } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { adoptMapExport, REQUIREMENTS } from "../../src/lib/data.js";
import { I18nProvider } from "../../src/lib/i18n.jsx";
import { PrintSheet, paperTheme } from "../../src/lib/exportDoc.jsx";
import { bugRows, questionRows, answerOptions } from "../../src/lib/exportRows.js";
import { crc32, colName, xlsxBytes } from "../../src/lib/xlsx.js";
import { AuditView } from "../../src/views/AuditView.jsx";
import { ExplorerView } from "../../src/views/ExplorerView.jsx";
import { ProblemsView } from "../../src/views/ProblemsView.jsx";
import { QuestionsView, priorityOf } from "../../src/views/QuestionsView.jsx";
import { BugReport, BugsPanel, bugSheet } from "../../src/views/problems/BugsPanel.jsx";
import { json, noop, test } from "./harness.jsx";

const en = (el) => renderToString(<I18nProvider initialLocale="en">{el}</I18nProvider>);
const AUDIT = {
  plan: { date: "2026-11-22", seed: 7, ranked: 1, random: 0, key: "k", bands: {},
    min_positives: 5 },
  reviewed: { total: 1, ranked: 1, random: 0 },
  counters: { B: 1 }, band: "not judged yet", problems: [],
  rates: { precision: { k: 1, n: 1, lo: 0.2, hi: 1, judged: false },
    miss_rate: { k: 0, n: 0, lo: null, hi: null, judged: false },
    agreement: { k: 1, n: 1, lo: 0.2, hi: 1, judged: false } },
  requirements: [{ id: "AUD-ONE-001", set: "ranked", state: "decided", runs: 2,
    findings: [{ clause: 1, labels: ["bug"], counter: "B" }] }],
};
const bug = (ref, prio, extra = {}) => ({ id: `Payments:${ref}`, ref, module: "Payments",
  prio, date: "", title: `Title ${ref}`, estimated: false, where: "", why: "",
  source: "", file: "", ...extra });

adoptMapExport({ health: json.health, design: json.design, audit: AUDIT });
const pdfButton = /<button[^>]*>(?:<svg[\s\S]*?<\/svg>)?\s*(?:<!-- -->)?\s*Export PDF/;
const audit = en(<AuditView openSpec={noop} />);
const health = en(<ProblemsView openSpec={noop} problems={[]} initialFilter="HEALTH" />);
const design = en(<ProblemsView openSpec={noop} problems={[]} initialFilter="DESIGN" />);
const questions = en(<QuestionsView openSpec={noop} />);
const first = REQUIREMENTS[0];
const explorer = en(<ExplorerView selId={first.id} setSelId={noop} clearFocus={noop} />);

adoptMapExport({ repo: "acme/pay", bugs: [bug("B1", "P1")] });
const sheet = en(<PrintSheet title="Open questions" meta={["All", "3 questions"]} />);
const printedBug = en(<BugReport keys={["Payments"]} scope=""
  groups={{ Payments: [bug("B1", "P1")] }} />);
const fullBugs = en(<BugsPanel added={[]} setAdded={noop} />);
adoptMapExport({ repo: json.repo || null, bugs: [] });
const emptyBugs = en(<BugsPanel added={[]} setAdded={noop} />);
adoptMapExport({ audit: null, health: null, design: null });

// a stand-in for <html>: the attribute calls usePrinting makes
const root = { attrs: { "data-theme": "dark" },
  getAttribute(k) { return this.attrs[k] ?? null; },
  setAttribute(k, v) { this.attrs[k] = v; },
  removeAttribute(k) { delete this.attrs[k]; } };
const restore = paperTheme(root);
const during = root.getAttribute("data-theme");
restore();
const after = root.getAttribute("data-theme");

const rows = bugRows([bug("B2", "P2", { why: "Money is lost", source: "PAY-002" }),
  bug("B1", "P1", { source: "PAY-001" })]);
const named = bugSheet([bug("B2", "P2"), bug("B1", "P1"), bug("B3", "P3", { estimated: true })],
  (k) => k).rows.map((r) => r[0]);
const person = { id: "Q-ONE-001", questions: ["Who signs this off?"] };
const code = { id: "Q-TWO-002", questions: ["Observed: retries 3 times"] };
const clarify = { id: "Q-THREE-003", questions: [{ rule: "vague-term", basis: "wording",
  where: "clause 1", quote: "", question: "How fast is fast?",
  suggest: "Replace it with a number and a unit." }] };
const qrows = questionRows({ person: [person], code: [code], clarify: [clarify] },
  { priorityOf });

const bytes = xlsxBytes("Bugs", ["Priority", "Description"],
  [["P1", "A & B"], ["P2", "x < y"]], [10, 40]);
const text = new TextDecoder("latin1").decode(bytes);

const checks = [
  // verifies: REQ-VIEWER-1151#CASE-1
  ["exports: Questions, Audit, Health and Design each have Export PDF; a requirement has one by its badges",
    [audit, health, design, questions].every((h) => pdfButton.test(h))
      && /class="head-row">[\s\S]*?<span class="head-actions"><button[^>]*spec-export/.test(explorer)],
  // verifies: REQ-VIEWER-1151#CASE-2
  ["exports: the printed sheet names the tool, the repository, the title, the date and the facts",
    (() => {
      const s = sheet.replace(/<!-- -->/g, "");
      const at = ["requirement-manager", "acme/pay", "Open questions",
        new Date().getFullYear() + "-", "All", "3 questions"].map((x) => s.indexOf(x));
      return at.every((i, n) => i >= 0 && (n === 0 || i > at[n - 1]))
        && s.includes('class="print-doc');
    })()],
  // verifies: REQ-VIEWER-1151#CASE-3
  ["exports: a printed bug is a card with its priority badge",
    /class="bug-print-row"><span class="prob-sev sev-ERROR">P1/.test(printedBug)],
  // verifies: REQ-VIEWER-1151#CASE-4
  ["exports: a dark screen prints on paper and gets its theme back",
    during === null && after === "dark"],
  // verifies: REQ-VIEWER-1152#CASE-1
  ["exports: bug rows come highest priority first, each priority named, the why under the title",
    rows[0][0] === "P1" && rows[0][1] === "PAY-001" && rows[0][2] === "Title B1"
      && rows[1][2] === "Title B2\nMoney is lost" && rows.every((r) => r.length === 3)
      && named.join(",") === "P1 - High,P2 - Medium,P3* - Low"],
  // verifies: REQ-VIEWER-1152#CASE-2
  ["exports: question rows keep their page's priority; clarify's suggestion is the answer",
    qrows.map((r) => r[0]).join(",") === "high,medium,low"
      && qrows[0][1] === "Q-ONE-001" && qrows[1][1] === "Q-TWO-002"
      && qrows[2][3] === "Replace it with a number and a unit."
      && qrows[0][3] === ""],
  // verifies: REQ-VIEWER-1152#CASE-3
  ["exports: answer options are read only where the question writes them",
    answerOptions("How long? Options: 100 ms / 300 ms") === "100 ms / 300 ms"
      && answerOptions("Which one: (a) lock (b) unlock") === "(a) lock (b) unlock"
      && answerOptions("How long is quickly?") === ""],
  // verifies: REQ-VIEWER-1152#CASE-4
  ["exports: the workbook is a zip of one sheet, header bold and frozen, text escaped",
    bytes[0] === 0x50 && bytes[1] === 0x4B
      && crc32(new TextEncoder().encode("123456789")).toString(16) === "cbf43926"
      && colName(0) === "A" && colName(25) === "Z" && colName(26) === "AA"
      && /<c r="A1" t="inlineStr" s="1">/.test(text)
      && text.includes('state="frozen"') && text.includes('<autoFilter ref="A1:B3"/>')
      && text.includes("A &amp; B") && text.includes("x &lt; y")
      && text.includes("[Content_Types].xml") && text.includes("xl/worksheets/sheet1.xml")],
  // verifies: REQ-VIEWER-1152#CASE-5
  ["exports: Bugs and Questions have Export XLSX, idle when the Bugs tab is empty",
    /<button[^>]*>Export XLSX/.test(fullBugs)
      && !/<button[^>]*disabled=""[^>]*>Export XLSX/.test(fullBugs)
      && /<button[^>]*disabled=""[^>]*>Export XLSX/.test(emptyBugs)
      && /Export XLSX/.test(questions)],
];
for (const [label, ok] of checks) test(label, ok);
{
  // A page break is the printer's, not the server's: this asserts the rule
  // the printer obeys, on the classes the printed rows, cards and lines carry.
  const css = readFileSync(resolve(process.cwd(), "src/styles/print.css"), "utf8")
    .replace(/\/\*[\s\S]*?\*\//g, "");
  const rule = /([^{}]*)\{\s*break-inside:\s*avoid;\s*\}/.exec(css);
  const sel = rule ? rule[1].split(",").map((s) => s.trim()) : [];
  // verifies: REQ-VIEWER-1151#CASE-5
  test("exports: a printed row, card or table line is kept on one sheet",
    /@media print/.test(css)
      && [".print-doc .prob-row", ".print-doc .bug-print-row",
        ".print-doc .audit-card", ".print-doc tr", ".print-doc li"]
        .every((s) => sel.includes(s))
      && printedBug.includes('class="bug-print-row"'));
}
