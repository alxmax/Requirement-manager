// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-966
// implements: REQ-VIEWER-977
// implements: REQ-VIEWER-1084
import { useState } from "react";
import {
  REQUIREMENTS, coverageOf, DESIGN, HEALTH,
} from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";
import { openQuestions } from "../lib/tree.js";
import {
  ProblemTabBar, DesignProblemsPanel, HealthPanel, ProblemRow,
  ProblemsEmpty,
} from "./problems/ProblemsPanels.jsx";

const SEV = {
  unimplemented: {
    sev: "ERROR",
    msg: "No implementing member — orphan. The gate blocks the build.",
    fix: "Add an `implements:` tag, or author the requirement.",
  },
  untested: {
    sev: "WARN", msg: "Confirmed, but no `tested-by:` member is linked.",
    fix: "Add a test tag, or set `test_exempt:` to silence.",
  },
  "unverified-intent": {
    sev: "WARN", msg: "Has open `## Verify intent` question(s).",
    fix: "Answer each one (`sync` lists them in _findings.md), then fold "
      + "the answer into the Description or delete the bullet.",
  },
  unreviewed: {
    sev: "REVIEW",
    msg: "Drafted from code by extract — intent not yet validated.",
    fix: "Review it, then set `status: confirmed` in its frontmatter.",
  },
};

export function computeProblems() {
  const out = [];
  REQUIREMENTS.forEach((r) => (r.risks || []).forEach((rk) => {
    const m = SEV[rk.signal]; if (!m) return;
    out.push({
      id: r.id, title: r.title, signal: rk.signal, sev: m.sev, msg: m.msg,
      fix: m.fix,
      loc: (r.members[0] && r.members[0].loc) || (r.impl && r.impl[0]) || "",
    });
  }));
  REQUIREMENTS.forEach((r) => {
    const cov = coverageOf(r);
    const flagged = (r.risks || []).length > 0;
    if (cov === "partial") {
      out.push({ id: r.id, title: r.title, signal: "partial", sev: "WARN",
        msg: (`Partial coverage — ${r.covered}/${r.clauses} criteria `
          + `verified. ${r.gap || ""}`).trim(),
        fix: "Tag a test `# verifies: <id>#CASE-N` for the uncovered "
          + "criterion, or write one.",
        loc: (r.members.find((m) => m.role === "tested-by") || {}).loc
          || "" });
    } else if (cov === "untested" && r.status !== "draft" && !flagged) {
      out.push({ id: r.id, title: r.title, signal: "untested", sev: "WARN",
        msg: "Untested — no live acceptance test, or a `tested-by` range "
          + "that no longer resolves (stale ref).",
        fix: "Add a test, repair the stale `tested-by` ref, or set "
          + "`test_exempt:`.",
        loc: (r.members.find((m) => m.role === "tested-by") || {}).loc
          || "" });
    }
  });
  REQUIREMENTS.forEach((r) => {
    const qs = openQuestions(r);
    if (!qs.length) return;
    out.push({ id: r.id, title: r.title, signal: "question", sev: "QUESTION",
      status: r.status, questions: qs,
      msg: `${qs.length} open verify-intent question(s).`,
      fix: "Answer it, fold the answer into the Description, then delete "
        + "the bullet.", loc: "" });
  });
  const design = (DESIGN && Array.isArray(DESIGN.findings))
    ? DESIGN.findings : [];
  const advice = (DESIGN && DESIGN.advice) || {};
  design.forEach((f) => {
    out.push({
      id: f.file,
      title: (f.name && f.name !== f.file) ? `${f.kind} · ${f.name}` : f.kind,
      signal: "design", sev: "DESIGN", noSpec: true, msg: f.detail,
      fix: advice[f.kind]
        || "Advisory: a shape worth a look, never a defect; `ask "
          + "--design` names it.",
      loc: `${f.file}:${f.line}` });
  });
  const order = { ERROR: 0, WARN: 1, QUESTION: 2, REVIEW: 3, DESIGN: 4 };
  return out.sort(
    (a, b) => order[a.sev] - order[b.sev] || a.id.localeCompare(b.id));
}

export function computeQuestions() {
  return computeProblems().filter((p) => p.sev === "QUESTION");
}

const isDraftReview = (p) => p.sev === "REVIEW" && p.signal === "unreviewed";

/* Tabs that render a panel of their own instead of the problem list. */
const PANELS = new Set(["DESIGN", "HEALTH"]);

export function ProblemsView({
  openSpec, problems, initialFilter = "ALL",
}) {
  const { t } = useI18n();
  const [filter, setFilter] = useState(initialFilter);
  const [showDrafts, setShowDrafts] = useState(false);
  const all = (problems || computeProblems()).filter((p) => p.sev !== "DESIGN");
  const counts = all.reduce((a, p) => {
    a[p.sev] = (a[p.sev] || 0) + 1;
    return a;
  }, { all: all.length });
  const design = (DESIGN && Array.isArray(DESIGN.findings))
    ? DESIGN.findings : [];
  const advice = (DESIGN && DESIGN.advice) || {};
  const byPillar = design.reduce((a, f) => {
    (a[f.pillar] = a[f.pillar] || []).push(f);
    return a;
  }, {});
  const health = (HEALTH && Array.isArray(HEALTH.unhealthy))
    ? HEALTH : null;
  const draftReviews = all.filter(isDraftReview).length;
  const byTab = filter === "ALL" ? all : all.filter((p) => p.sev === filter);
  const shown = showDrafts ? byTab : byTab.filter((p) => !isDraftReview(p));
  const hidden = byTab.length - shown.length;
  const gateMsg = (counts.ERROR || 0) > 0
    ? <>
        <Icon name="triangle-alert" size={14}
              style={{ color: "var(--status-error)" }} />
        {" "}{t("gate blocks the build — {n} error", { n: counts.ERROR })}
      </>
    : <>
        <Icon name="shield-check" size={14}
              style={{ color: "var(--status-confirmed)" }} />
        {" "}{t("gate passes")}
      </>;
  const draftsLabel = showDrafts
    ? t("hide {n} draft review rows", { n: draftReviews })
    : t("{n} draft review rows hidden — show", { n: hidden });

  return (
    <div className="main">
      <ProblemTabBar filter={filter} setFilter={setFilter} counts={counts}
                     designCount={design.length}
                     healthCount={health ? health.unhealthy.length
                       + (health.exempt_ids || []).length : null}
                     gateMsg={gateMsg} />
      <div className="problems">
        {filter === "DESIGN"
          && <DesignProblemsPanel byPillar={byPillar} advice={advice} />}
        {filter === "HEALTH" && health
          && <HealthPanel health={health} openSpec={openSpec} />}
        {!PANELS.has(filter)
          && (hidden > 0 || (showDrafts && draftReviews > 0)) && (
          <button type="button" className="prob-chip"
                  onClick={() => setShowDrafts((s) => !s)}>
            {draftsLabel}
          </button>
        )}
        {!PANELS.has(filter) && shown.map((p, i) => (
          <ProblemRow key={i} p={p} openSpec={openSpec} t={t} />
        ))}
        {!PANELS.has(filter) && shown.length === 0
          && <ProblemsEmpty filter={filter} t={t} />}
      </div>
    </div>
  );
}
