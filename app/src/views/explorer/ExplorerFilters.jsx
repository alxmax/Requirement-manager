// implements: ARCH-VIEWER-007
import { useI18n } from "../../lib/i18n.jsx";
import { LEVELS, LEVEL_LABEL } from "../../lib/tree.js";

const STATUSES = ["confirmed", "in-progress", "draft", "deprecated"];

function Chip({ on, onClick, children, title }) {
  return (
    <button type="button" className={"ex-chip" + (on ? " on" : "")} onClick={onClick} title={title}>
      {children}
    </button>
  );
}

export function ExplorerFilters({
  levelFilter, flipLevel, statusFilter, flipStatus, onlyOrphans, setOnlyOrphans,
  onlyQuestions, setOnlyQuestions, clearFocus, rowsLength, total, flat, onExpandAll, onCollapseAll,
}) {
  const { t } = useI18n();
  return (
    <div className="ex-filters">
      <div className="ex-filter-row">
        <span className="ex-flabel">{t("Level")}</span>
        {LEVELS.map((l) => (
          <Chip key={l} on={!!levelFilter[l]} onClick={() => flipLevel(l)}>{LEVEL_LABEL[l]}</Chip>
        ))}
      </div>
      <div className="ex-filter-row">
        <span className="ex-flabel">{t("Status")}</span>
        {STATUSES.map((s) => (
          <Chip key={s} on={!!statusFilter[s]}
            onClick={() => { if (clearFocus) clearFocus(); flipStatus(s); }}>{s}</Chip>
        ))}
        <Chip on={onlyOrphans} title="enforced requirements with no implements: member"
          onClick={() => { if (clearFocus) clearFocus(); setOnlyOrphans((v) => !v); }}>orphan</Chip>
      </div>
      <div className="ex-filter-row">
        <Chip on={onlyQuestions} onClick={() => setOnlyQuestions((v) => !v)}
          title="only requirements with an unanswered verify-intent bullet">
          {t("has open question")}
        </Chip>
        <span className="ex-spacer" />
        <button type="button" className="ex-mini" onClick={onExpandAll}>{t("expand all")}</button>
        <button type="button" className="ex-mini" onClick={onCollapseAll}>{t("collapse all")}</button>
      </div>
      <div className="ex-tally">
        {t("{shown} of {total} shown", { shown: rowsLength, total })}
        {flat && <span className="ex-flatnote">{t("· no hierarchy in this map — flat list")}</span>}
      </div>
    </div>
  );
}
