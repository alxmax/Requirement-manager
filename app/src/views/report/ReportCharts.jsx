// implements: REQ-VIEWER-1155
/* The Report's two charts, each with its own filter: the bug trend by
 * priority (P0…P4, only those the register holds) and the open questions by
 * priority (High, Medium, Low). A filter narrows what is drawn and what the
 * PDF prints; the table above keeps every number. */
import { useState } from "react";
import { useI18n } from "../../lib/i18n.jsx";
import { weekly } from "../../lib/bugStats.js";
import { BugChart } from "../problems/BugChart.jsx";
import { QuestionChart } from "./QuestionChart.jsx";

const BUG_PRIOS = ["P0", "P1", "P2", "P3", "P4"];
const Q_PRIOS = [["high", "High"], ["medium", "Medium"], ["low", "Low"]];
const shortDate = (d) => (d || "").split("-").reverse().join(".");

/** `on` with `key` flipped; never empty, since an empty chart answers nothing. */
export function toggled(on, key) {
  const next = on.includes(key) ? on.filter((k) => k !== key) : [...on, key];
  return next.length ? next : on;
}

/** The weeks of the bugs whose priority is in `prios`. */
export function bugWeeksOf(open, fixed, prios) {
  const keep = (b) => prios.includes(b.prio);
  return weekly(open.filter(keep), fixed.filter(keep));
}

function Filter({ label, options, on, setOn }) {
  const { t } = useI18n();
  return (
    <div className="rep-filter" role="group" aria-label={label}>
      {options.map(([key, name]) => (
        <button key={key} type="button" aria-pressed={on.includes(key)}
          onClick={() => setOn(toggled(on, key))}>{t(name)}</button>
      ))}
    </div>
  );
}

export function ReportCharts({ c }) {
  const { t } = useI18n();
  const present = BUG_PRIOS.filter((p) => [...c.bugs.open, ...c.bugs.fixedRows]
    .some((b) => b.prio === p));
  const [bugPrios, setBugPrios] = useState(present);
  const [qPrios, setQPrios] = useState(Q_PRIOS.map(([k]) => k));
  const weeks = bugWeeksOf(c.bugs.open, c.bugs.fixedRows, bugPrios);
  const split = c.questionSplit.filter((s) => qPrios.includes(s.prio));
  const anyQ = c.questionSplit.some((s) => s.confirmed + s.other);
  return (
    <div className="rep-charts">
      {present.length > 0 && c.bugs.fixedRows.length > 0 && (
        <BugChart weeks={weeks} dateOf={shortDate} chosen={null} filter={
          <Filter label={t("Bug priorities")} on={bugPrios} setOn={setBugPrios}
            options={present.map((p) => [p, p])} />} />
      )}
      {anyQ && (
        <QuestionChart split={split} filter={
          <Filter label={t("Question priorities")} on={qPrios} setOn={setQPrios}
            options={Q_PRIOS} />} />
      )}
    </div>
  );
}
