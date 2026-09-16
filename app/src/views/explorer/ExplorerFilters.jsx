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

/** The filter chips above the tree. `filters` is the state `useExplorerFilters` returns;
 *  `tree` carries the tally and the expand/collapse actions. */
export function ExplorerFilters({ filters, tree }) {
  const { t } = useI18n();
  const f = filters;
  const unfocus = (then) => () => { if (f.clearFocus) f.clearFocus(); then(); };
  return (
    <div className="ex-filters">
      <div className="ex-filter-row">
        <span className="ex-flabel">{t("Level")}</span>
        {LEVELS.map((l) => (
          <Chip key={l} on={!!f.level[l]} onClick={() => f.flipLevel(l)}>{LEVEL_LABEL[l]}</Chip>
        ))}
      </div>
      <div className="ex-filter-row">
        <span className="ex-flabel">{t("Status")}</span>
        {STATUSES.map((s) => (
          <Chip key={s} on={!!f.status[s]} onClick={unfocus(() => f.flipStatus(s))}>{s}</Chip>
        ))}
        <Chip on={f.onlyOrphans} title="enforced requirements with no implements: member"
          onClick={unfocus(() => f.setOnlyOrphans((v) => !v))}>orphan</Chip>
      </div>
      <div className="ex-filter-row">
        <Chip on={f.onlyQuestions} onClick={() => f.setOnlyQuestions((v) => !v)}
          title="only requirements with an unanswered verify-intent bullet">
          {t("has open question")}
        </Chip>
        <span className="ex-spacer" />
        <button type="button" className="ex-mini" onClick={tree.onExpandAll}>
          {t("expand all")}
        </button>
        <button type="button" className="ex-mini" onClick={tree.onCollapseAll}>
          {t("collapse all")}
        </button>
      </div>
      <div className="ex-tally">
        {t("{shown} of {total} shown", { shown: tree.shown, total: tree.total })}
        {tree.flat && (
          <span className="ex-flatnote">{t("· no hierarchy in this map — flat list")}</span>
        )}
      </div>
    </div>
  );
}
