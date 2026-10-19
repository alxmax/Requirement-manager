// tested-by: REQ-AUDITRUN-1108
/* Render smoke test, part: the Audit view and its rail entry. Adopts an audit
 * block, checks the view, then adopts one without it so the parts after this
 * see the real export again. */
import { renderToString } from "react-dom/server";

import { adoptMapExport } from "../../src/lib/data.js";
import { Rail } from "../../src/components/Rail.jsx";
import { AuditView, rateText } from "../../src/views/AuditView.jsx";
import { noop, test } from "./harness.jsx";

const rate = (k, n, lo, hi, judged) => ({ k, n, lo, hi, judged });
const AUDIT_FIXTURE = {
  plan: { date: "2026-10-19", seed: 7, ranked: 2, random: 2, key: "k",
    bands: {}, min_positives: 5 },
  reviewed: { total: 3, ranked: 2, random: 1 },
  counters: { B: 7, F_copilot: 13, G: 0, A: 0, F_tool: 0, M: 0, U: 0,
    undecided: 1 },
  rates: { precision: rate(7, 20, 0.181, 0.567, true),
    miss_rate: rate(0, 1, 0, 0.793, false), agreement: rate(0, 0, null, null,
      false) },
  band: "change the method",
  problems: [],
  requirements: [
    { id: "AUD-DONE-001", set: "ranked", state: "decided", runs: 2,
      findings: [{ clause: 1, labels: ["bug"], counter: "B" }] },
    { id: "AUD-TWICE-002", set: "ranked", state: "reviewed twice", runs: 2,
      findings: [{ clause: 2, labels: ["ok"], counter: null }] },
    { id: "AUD-ONCE-003", set: "random", state: "reviewed once", runs: 1,
      findings: [{ clause: null, labels: ["ok"], counter: null }] },
    { id: "AUD-NONE-004", set: "random", state: "not reviewed", runs: 0,
      findings: [] },
  ],
};
const rail = () => renderToString(
  <Rail view="explorer" setView={noop} focus={null} setFocus={noop}
    problems={[]} openProblems={noop} />);

adoptMapExport({ audit: null });
const railWithout = rail();
adoptMapExport({ audit: AUDIT_FIXTURE });
const railWith = rail();
const page = renderToString(<AuditView openSpec={noop} />);
const auditChecks = [
  // verifies: REQ-AUDITRUN-1108#CASE-2
  ["audit: no audit block, no Audit entry in the rail",
    !railWithout.includes("</svg>Audit<") && railWith.includes("</svg>Audit<")],
  // verifies: REQ-AUDITRUN-1108#CASE-3
  ["audit: each planned id shows its state",
    ["decided", "reviewed twice", "reviewed once", "not reviewed"].every(
      (s) => page.includes(">" + s + "<"))
      && ["AUD-DONE-001", "AUD-NONE-004"].every((id) => page.includes(id))],
  // verifies: REQ-AUDITRUN-1108#CASE-3
  ["audit: every rate is shown as k/n with its interval",
    page.includes(">7/20<") && page.includes("95% 0.18–0.57")
      && rateText(rate(0, 0, null, null, false)).main === "0/0"
      && page.includes("change the method")],
];
for (const [label, ok] of auditChecks) test(label, ok);
adoptMapExport({ audit: null });
