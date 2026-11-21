// implements: ARCH-VIEWER-007
// tested-by: REQ-VIEWER-1139
/* The Report page: one place for the counts of bugs, questions and missing
 * tags, the ten most important questions and what to do next. Each check
 * adopts its own fixture and the real export is put back at the end. */
import { renderToString } from "react-dom/server";
import { adoptMapExport } from "../../src/lib/data.js";
import { adaptNode } from "../../src/lib/loadData.js";
import { computeReport } from "../../src/lib/report.js";
import { ReportView } from "../../src/views/ReportView.jsx";
import { Rail } from "../../src/components/Rail.jsx";
import { test, json, noop } from "./harness.jsx";

const node = (id, extra = {}) => adaptNode({ id, title: id, area: "R",
  layer: "feature", status: "confirmed", intent: "", contract: ["c"], acc: [],
  members: [], deps: [], used_by: [], ...extra });
const IMPL = { role: "implements", loc: "a.py:1" };
const TEST = { role: "tested-by", loc: "test_a.py:1" };
const CQ = (rule, basis) => ({ rule, basis, severity: "advisory",
  where: "clause 1", question: `the ${rule} question`, suggest: "s" });

// verifies: REQ-VIEWER-1139#CASE-1
const rail = renderToString(<Rail view="report" setView={noop} focus={null}
  setFocus={noop} problems={[]} openProblems={noop} />);
const at = (label) => rail.indexOf(`</svg>${label}<`);
test("report: the page sits last in the rail, after Questions",
  at("Report") > at("Questions") && at("Questions") > 0);

// verifies: REQ-VIEWER-1139#CASE-2
adoptMapExport({ nodes: [
  node("R-CONF-001"),
  node("R-DRAFT-002", { status: "draft" }),
  node("R-NOTEST-003", { members: [IMPL] }),
  node("R-AGG-004", { layer: "aggregate" }),
  node("R-CASES-005", { members: [IMPL, TEST], clauses: 3, covered: 1 }),
] });
const tr = computeReport().trace;
test("report: missing tags are counted over the requirements that need them",
  tr.noImplConfirmed.map((r) => r.id).join() === "R-CONF-001"
    && tr.noImplDraft.map((r) => r.id).join() === "R-DRAFT-002"
    && tr.noTest.map((r) => r.id).join() === "R-NOTEST-003"
    && tr.unprovenCases === 2
    && ![...tr.noImplConfirmed, ...tr.noImplDraft, ...tr.noTest]
      .some((r) => r.id === "R-AGG-004"));

// verifies: REQ-VIEWER-1139#CASE-3
adoptMapExport({
  nodes: [node("R-Q-001", { members: [IMPL, TEST], clarify: [
    CQ("no-cases", "structure"), CQ("clause-without-case", "count"),
    CQ("vague-term", "wording")] })],
  bugs: [{ id: "b1", ref: "B-1", prio: "P1", module: "m", title: "one" },
    { id: "b2", ref: "B-2", prio: "P2", module: "m", title: "two" }],
  bugs_fixed: [{ id: "b3", ref: "B-3", title: "three", version: "v1" }],
});
const c3 = computeReport();
const page = renderToString(<ReportView openSpec={noop} />);
test("report: bugs and questions are counted as their pages count them",
  c3.bugs.open.length === 2 && c3.bugs.byPrio.P1 === 1
    && c3.bugs.byPrio.P2 === 1 && c3.bugs.fixed === 1
    && c3.questions.high === 1 && c3.questions.medium === 1
    && c3.questions.low === 1
    && page.includes("P1 1 · P2 1"));
test("report: the six sections come in order",
  ["Summary", "How it was checked", "Results in numbers", "Problem types",
    "Top 10 questions", "Recommendations"].map((h) => page.indexOf(`>${h}<`))
    .every((i, k, a) => i > 0 && (k === 0 || i > a[k - 1])));

// verifies: REQ-VIEWER-1139#CASE-4
test("report: what the map does not carry is not shown as zero",
  c3.dangling === null && c3.drift === null
    && page.includes("not measured"));

// verifies: REQ-VIEWER-1139#CASE-5
adoptMapExport({ nodes: [
  node("R-DRAFT-HIGH", { status: "draft", verify: ["Why?"] }),
  node("R-HUB-HIGH", { verify: ["Who?"], used_by: ["R-L-1", "R-L-2"] }),
  node("R-LEAF-HIGH", { verify: ["When?"] }),
  ...Array.from({ length: 9 }, (_, i) => node(`R-L-${i + 1}`, {
    clarify: [CQ("vague-term", "wording")] })),
] });
const top = computeReport().top;
test("report: the top questions come in priority order and stop at ten",
  top.length === 10
    && top.slice(0, 3).map((q) => q.id).join()
      === "R-HUB-HIGH,R-LEAF-HIGH,R-DRAFT-HIGH"
    && top.slice(3).every((q) => q.prio === "low"));

// verifies: REQ-VIEWER-1139#CASE-6
adoptMapExport({ nodes: [
  node("R-NOCODE-001"), node("R-NOTEST-002", { members: [IMPL] })] });
const rec = computeReport().recommendations;
adoptMapExport({ nodes: [node("R-OK-001", { members: [IMPL, TEST] })] });
const none = renderToString(<ReportView openSpec={noop} />);
test("report: a recommendation per problem, most severe first",
  rec.length === 2 && rec[0].n === 1 && /no code/.test(rec[0].text)
    && /no test/.test(rec[1].text)
    && none.includes("Nothing is open: no recommendation."));

adoptMapExport({ nodes: json.nodes.map(adaptNode) });
