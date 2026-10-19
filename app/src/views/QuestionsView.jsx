// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1101
// implements: REQ-VIEWER-1114
import { useState } from "react";
import { REQUIREMENTS } from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";
import {
  Pill, statusKind, mdInline, mdQuestion, reqLinkProps,
} from "../lib/ui.jsx";
import { openQuestions, isObserved, clarifyQuestions } from "../lib/tree.js";
import { ChipRow, ProblemRow } from "./problems/ProblemsPanels.jsx";

const ANSWER_FIX = "Answer it: fold the answer into the Description and "
  + "delete the bullet, or keep it under the question as "
  + "`*Answer (YYYY-MM-DD):* …`.";

/** Verify-intent rows, one per requirement, holding only the bullets of one
 * origin: observed in code, or asked by a person. */
function verifyRows(origin) {
  const out = [];
  REQUIREMENTS.forEach((r) => {
    if (r.status === "deprecated") return;   // retired: nothing to answer
    const qs = openQuestions(r)
      .filter((q) => isObserved(q) === (origin === "code"));
    if (!qs.length) return;
    out.push({ id: r.id, title: r.title, sev: "QUESTION", status: r.status,
      questions: qs, fix: ANSWER_FIX });
  });
  return out;
}

/* What a `clarify` question rests on, strongest first: a section that is
 * absent, two numbers that disagree, a word on a list (ADR-0070). The last
 * one is shown as Optional. */
const BASIS_ORDER = { structure: 0, count: 1, wording: 2 };
const BASIS_LABEL = { structure: "must fix", count: "to check",
  wording: "optional" };
export const basisOf = (q) => (BASIS_ORDER[q.basis] !== undefined ? q.basis
  : q.severity === "blocking" ? "structure" : "wording");

/** Every open question, by origin. `clarify` rows carry the records the
 * map holds, strongest basis first inside each requirement. */
export function computeQuestions() {
  const clarify = [];
  REQUIREMENTS.forEach((r) => {
    const qs = r.status === "deprecated" ? [] : clarifyQuestions(r);
    if (!qs.length) return;
    clarify.push({ id: r.id, title: r.title, status: r.status,
      questions: [...qs].sort((a, b) => BASIS_ORDER[basisOf(a)]
        - BASIS_ORDER[basisOf(b)]) });
  });
  return { code: verifyRows("code"), person: verifyRows("person"), clarify };
}

/** The count of the All tab, which is also the rail's: every Verify-intent
 * question, and every `clarify` question that is not Optional. */
export function questionCount(qs = computeQuestions()) {
  const n = (rows) => rows.reduce((a, r) => a + r.questions.length, 0);
  return n(qs.code) + n(qs.person) + qs.clarify.reduce((a, r) => a
    + r.questions.filter((q) => basisOf(q) !== "wording").length, 0);
}

/* A count rule's tab name; a rule the viewer has not met keeps its own. */
const RULE_TAB = { "clause-without-case": "Clause without case",
  "over-scoped": "Over-scoped" };
const ruleTitle = (rule) => RULE_TAB[rule] || rule;

/** The tabs, in order, each with what it keeps and its count. Must fix
 * appears only when a section is missing; every rule resting on a count
 * gets a tab of its own; Optional holds every word-list question. */
export function questionTabs(qs = computeQuestions()) {
  const all = qs.clarify.flatMap((r) => r.questions);
  const n = (keep) => all.filter(keep).length;
  const countRules = [...new Set(all.filter((q) => basisOf(q) === "count")
    .map((q) => q.rule))].sort();
  const tabs = [
    { key: "all", label: "All", n: questionCount(qs), verify: ["person", "code"],
      keep: (q) => basisOf(q) !== "wording" },
    { key: "structure", label: "Must fix",
      keep: (q) => basisOf(q) === "structure" },
    { key: "person", label: "Asked by a person", verify: ["person"],
      keep: () => false },
    { key: "code", label: "Observed in code", verify: ["code"],
      keep: () => false },
    ...countRules.map((rule) => ({ key: rule, label: ruleTitle(rule),
      keep: (q) => q.rule === rule })),
    { key: "optional", label: "Optional", rules: true,
      keep: (q) => basisOf(q) === "wording" },
  ];
  tabs.forEach((tab) => {
    if (tab.n === undefined) {
      tab.n = n(tab.keep) + (tab.verify || []).reduce(
        (a, o) => a + qs[o].reduce((b, r) => b + r.questions.length, 0), 0);
    }
  });
  return tabs.filter((tab) => tab.key !== "structure" || tab.n > 0);
}

const MUTED = { color: "var(--fg-muted)", font: "var(--text-small)" };
const BADGE = { marginRight: 6, padding: "1px 6px" };
const COUNT = {
  marginLeft: 6, opacity: .7, fontFamily: "var(--font-mono)", fontSize: 11,
};

function ClarifyList({ qs }) {
  return (
    <ul className="finding-qs">
      {qs.map((q, j) => (
        <li key={j}>
          <span className={"prob-sev basis-" + basisOf(q)}
            style={BADGE}>{BASIS_LABEL[basisOf(q)]}</span>
          <code>{q.rule}</code> · {q.where}
          {q.quote && <div style={MUTED}>“{q.quote}”</div>}
          <div>{q.question}</div>
          <div className="prob-fix">
            <Icon name="arrow-right" size={13} /> {q.suggest}
          </div>
        </li>
      ))}
    </ul>
  );
}

export function ClarifyRow({ row, keep, pick, picked }) {
  const qs = row.questions.filter(keep);
  if (!qs.length) return null;
  return (
    <div className={"prob-row question-row" + (picked ? " picked" : "")}
      onClick={() => pick(row.id)}>
      <span className="prob-sev sev-QUESTION">clarify</span>
      <div className="prob-body">
        <div className="prob-head">
          <span className="prob-id">{row.id}</span>
          <span className="prob-title">{row.title}</span>
          <Pill kind={statusKind(row.status)}>{row.status}</Pill>
        </div>
        <ClarifyList qs={qs} />
      </div>
    </div>
  );
}

/** The chosen requirement's questions on this tab, beside the text they are
 * about: its Description clauses and its Cases. Opening the requirement is
 * a button, never the click that chose it. */
export function QuestionPanel({ id, tab, keep, qs, openSpec, close, t }) {
  const r = REQUIREMENTS.find((x) => x.id === id);
  if (!r) return null;
  const asked = (tab.verify || []).flatMap((o) =>
    (qs[o].find((row) => row.id === id) || { questions: [] }).questions);
  const row = qs.clarify.find((x) => x.id === id);
  const clarify = row ? row.questions.filter(keep) : [];
  const md = (fmt) => (c, i) => (
    <li key={i} dangerouslySetInnerHTML={{ __html: fmt(c) }} />);
  return (
    <aside className="q-panel">
      <div className="prob-head">
        <span className="prob-id">{r.id}</span>
        <Pill kind={statusKind(r.status)}>{r.status}</Pill>
      </div>
      <h3>{r.title}</h3>
      {/* first, so a long requirement never pushes them out of sight */}
      <div className="q-panel-actions">
        <button className="btn btn-secondary" onClick={() => openSpec(r.id)}>
          {t("Open requirement")} <Icon name="arrow-right" size={13} />
        </button>
        <button className="btn btn-ghost" onClick={close}>{t("Close")}</button>
      </div>
      {asked.length > 0 && (
        <ul className="finding-qs q-asked" {...reqLinkProps(openSpec)}>
          {asked.map(md(mdQuestion))}
        </ul>
      )}
      {clarify.length > 0 && <ClarifyList qs={clarify} />}
      <div className="eyebrow">{t("Description")}</div>
      <ul {...reqLinkProps(openSpec)}>{(r.contract || []).map(md(mdInline))}</ul>
      <div className="eyebrow">{t("Cases")}</div>
      {r.gwt
        ? <div className="gwt">
            {r.gwt.split("\n").map((ln, i) => <div key={i}>{ln}</div>)}
          </div>
        : <ul {...reqLinkProps(openSpec)}>{(r.acc || []).map(md(mdInline))}</ul>}
    </aside>
  );
}

const OPTIONAL_NOTE = "A word on a list matched. Often not a real gap; read "
  + "it when you have time.";

export function QuestionsView({ openSpec, initialTab = "all",
  initialPick = null }) {
  const { t } = useI18n();
  const qs = computeQuestions();
  const tabs = questionTabs(qs);
  const [key, setKey] = useState(
    tabs.some((tab) => tab.key === initialTab) ? initialTab : "all");
  const [rule, setRule] = useState(null);
  const [pick, setPick] = useState(initialPick);
  const tab = tabs.find((x) => x.key === key);
  const missing = (tabs.find((x) => x.key === "structure") || {}).n || 0;
  const keep = (q) => tab.keep(q) && (!rule || q.rule === rule);
  const rules = {};
  if (tab.rules) {
    qs.clarify.forEach((r) => r.questions.filter(tab.keep).forEach((q) => {
      rules[q.rule] = (rules[q.rule] || 0) + 1;
    }));
  }
  return (
    <div className="main">
      <div className="tabbar">
        {tabs.map((x) => (
          <button key={x.key} className={"tab" + (key === x.key ? " on" : "")}
            onClick={() => { setKey(x.key); setRule(null); }}>
            {t(x.label)}<span style={COUNT}>{x.n}</span>
          </button>
        ))}
        <div className="tab-legend">
          {missing > 0
            ? <>
                <Icon name="triangle-alert" size={14}
                  style={{ color: "var(--status-error)" }} />
                {" "}{t("{n} must fix — a section is missing", { n: missing })}
              </>
            : <>
                <Icon name="shield-check" size={14}
                  style={{ color: "var(--status-confirmed)" }} />
                {" "}{t("nothing missing")}
              </>}
        </div>
      </div>
      <div className={pick ? "q-split" : undefined}>
      <div className="problems">
        {tab.rules && tab.n > 0 && (
          <>
            <div className="prob-chip" style={{ cursor: "default" }}>
              {t(OPTIONAL_NOTE)}
            </div>
            <ChipRow counts={rules} total={tab.n} value={rule}
              setValue={setRule} label={(k) => k} />
          </>
        )}
        {(tab.verify || []).flatMap((o) => qs[o].map((p) => (
          <ProblemRow key={o + p.id} p={p} openSpec={openSpec} t={t}
            onPick={setPick} picked={pick === p.id} />
        )))}
        {qs.clarify.map((r) => (
          <ClarifyRow key={r.id} row={r} keep={keep} pick={setPick}
            picked={pick === r.id} />
        ))}
        {tab.n === 0 && (
          <div className="prob-empty">
            <Icon name="shield-check" size={26}
              style={{ color: "var(--cov-tested)" }} />
            <div><b>{t("No open questions here.")}</b></div>
          </div>
        )}
      </div>
      {pick && (
        <QuestionPanel id={pick} tab={tab} keep={keep} qs={qs}
          openSpec={openSpec} close={() => setPick(null)} t={t} />
      )}
      </div>
    </div>
  );
}
