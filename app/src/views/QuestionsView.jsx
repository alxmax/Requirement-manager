// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1101
import { useState } from "react";
import { REQUIREMENTS } from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";
import { Pill, statusKind } from "../lib/ui.jsx";
import { openQuestions, isObserved, clarifyQuestions } from "../lib/tree.js";
import { ChipRow, ProblemRow } from "./problems/ProblemsPanels.jsx";

/* Where a question came from. The order is the tab order. */
export const ORIGINS = ["code", "person", "clarify"];

const ANSWER_FIX = "Answer it: fold the answer into the Description and "
  + "delete the bullet, or keep it under the question as "
  + "`*Answer (YYYY-MM-DD):* …`.";

/** Verify-intent rows, one per requirement, holding only the bullets of one
 * origin: observed in code, or asked by a person. */
function verifyRows(origin) {
  const out = [];
  REQUIREMENTS.forEach((r) => {
    const qs = openQuestions(r)
      .filter((q) => isObserved(q) === (origin === "code"));
    if (!qs.length) return;
    out.push({ id: r.id, title: r.title, sev: "QUESTION", status: r.status,
      questions: qs, fix: ANSWER_FIX });
  });
  return out;
}

/** Every open question, by origin. `clarify` rows carry the records the
 * map holds; blocking ones first inside each requirement. */
export function computeQuestions() {
  const clarify = [];
  REQUIREMENTS.forEach((r) => {
    const qs = clarifyQuestions(r);
    if (!qs.length) return;
    clarify.push({ id: r.id, title: r.title, status: r.status,
      questions: [...qs].sort((a, b) => (a.severity === "blocking" ? 0 : 1)
        - (b.severity === "blocking" ? 0 : 1)) });
  });
  return { code: verifyRows("code"), person: verifyRows("person"), clarify };
}

/** What a human still has to answer: every Verify-intent question, and the
 * `clarify` questions that block implementing the text as written. The
 * advisory ones are on the page, not in this number. */
export function questionCount(qs = computeQuestions()) {
  const n = (rows) => rows.reduce((a, r) => a + r.questions.length, 0);
  return n(qs.code) + n(qs.person) + qs.clarify.reduce((a, r) => a
    + r.questions.filter((q) => q.severity === "blocking").length, 0);
}

const MUTED = { color: "var(--fg-muted)", font: "var(--text-small)" };

function ClarifyRow({ row, rule, openSpec }) {
  const qs = row.questions.filter((q) => !rule || q.rule === rule);
  if (!qs.length) return null;
  return (
    <div className="prob-row question-row" onClick={() => openSpec(row.id)}>
      <span className="prob-sev sev-QUESTION">clarify</span>
      <div className="prob-body">
        <div className="prob-head">
          <span className="prob-id">{row.id}</span>
          <span className="prob-title">{row.title}</span>
          <Pill kind={statusKind(row.status)}>{row.status}</Pill>
        </div>
        <ul className="finding-qs">
          {qs.map((q, j) => (
            <li key={j}>
              <span className={"prob-sev sev-"
                + (q.severity === "blocking" ? "WARN" : "REVIEW")}
                style={{ marginRight: 6 }}>{q.severity}</span>
              <code>{q.rule}</code> · {q.where}
              {q.quote && <div style={MUTED}>“{q.quote}”</div>}
              <div>{q.question}</div>
              <div className="prob-fix">
                <Icon name="arrow-right" size={13} /> {q.suggest}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

const NOTE = {
  code: "Written from the code: a line the scan found that only the author "
    + "can call intended or a bug.",
  person: "Written down by a person in the requirement's Verify intent "
    + "section.",
  clarify: "Asked by `clarify` of the requirement's own text. Blocking means "
    + "it cannot be implemented as written; advisory is a suggestion.",
};

export function QuestionsView({ openSpec, initialOrigin = null }) {
  const { t } = useI18n();
  const qs = computeQuestions();
  const sizes = {
    code: qs.code.length, person: qs.person.length,
    clarify: qs.clarify.reduce((a, r) => a + r.questions.length, 0),
  };
  const [origin, setOrigin] = useState(initialOrigin
    || ORIGINS.find((o) => sizes[o] > 0) || "code");
  const [rule, setRule] = useState(null);
  const rules = {};
  qs.clarify.forEach((r) => r.questions.forEach((q) => {
    rules[q.rule] = (rules[q.rule] || 0) + 1;
  }));
  const label = { code: "Observed in code", person: "Asked by a person",
    clarify: "Asked by clarify" };
  return (
    <div className="main">
      <div className="tabbar">
        {ORIGINS.map((o) => (
          <button key={o} className={"tab" + (origin === o ? " on" : "")}
            onClick={() => setOrigin(o)}>
            {t(label[o])}
            <span style={{ marginLeft: 6, opacity: .7,
              fontFamily: "var(--font-mono)", fontSize: 11 }}>{sizes[o]}</span>
          </button>
        ))}
      </div>
      <div className="problems">
        <div className="prob-chip" style={{ cursor: "default" }}>
          {t(NOTE[origin])}
        </div>
        {origin === "clarify" && sizes.clarify > 0 && (
          <ChipRow counts={rules} total={sizes.clarify} value={rule}
            setValue={setRule} label={(k) => k} />
        )}
        {origin === "clarify"
          ? qs.clarify.map((r) => (
            <ClarifyRow key={r.id} row={r} rule={rule} openSpec={openSpec} />
          ))
          : qs[origin].map((p) => (
            <ProblemRow key={p.id} p={p} openSpec={openSpec} t={t} />
          ))}
        {sizes[origin] === 0 && (
          <div className="prob-empty">
            <Icon name="shield-check" size={26}
              style={{ color: "var(--cov-tested)" }} />
            <div><b>{t("No open questions here.")}</b></div>
          </div>
        )}
      </div>
    </div>
  );
}
