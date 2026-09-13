// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-945
import { useEffect, useMemo, useRef, useState } from "react";
import { REQUIREMENTS, REQ_BY_ID } from "../lib/data.js";
import { SpecDoc, ENFORCED } from "./SpecView.jsx";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";
import {
  LEVELS, LEVEL_LABEL, LEVEL_SHORT, levelOf, buildHierarchy, ancestorsOf,
  defaultExpanded, allExpanded, keepSetFor, flattenTree, hasOpenQuestions,
} from "../lib/tree.js";
import { ExplorerFilters } from "./explorer/ExplorerFilters.jsx";

function isOrphan(r) {
  return !!ENFORCED[r.status] && r.layer !== "need" && r.layer !== "aggregate"
    && !(r.members || []).some((m) => m.role === "implements");
}

function statusDot(s) {
  return s === "confirmed" ? "var(--status-confirmed)"
    : s === "in-progress" ? "var(--status-drift)"
    : s === "deprecated" ? "var(--fg-faint)"
    : "var(--status-draft)";
}

function Row({ row, selected, onSelect, onToggle }) {
  const r = row.r;
  const lvl = levelOf(r);
  const cls = ["ex-row", selected ? "sel" : "", row.context ? "ctx" : ""].join(" ").trim();
  const n = row.childCount;
  const chip = row.codeChildren === n
    ? `${n} ${n === 1 ? "clause" : "clauses"}`
    : `${n} ${n === 1 ? "child" : "children"}`;
  return (
    <div className={cls} data-req-row={r.id} style={{ paddingLeft: 6 + row.depth * 16 }}
      onClick={() => onSelect(r.id)}>
      {row.hasChildren
        ? <button type="button" className={"ex-caret" + (row.expanded ? " open" : "")}
            aria-label={row.expanded ? "collapse" : "expand"}
            onClick={(e) => { e.stopPropagation(); onToggle(r.id); }}>
            <Icon name="chevron-right" size={13} />
          </button>
        : <span className="ex-caret empty" />}
      <span className={"ex-lvl lvl-" + lvl} title={LEVEL_LABEL[lvl]}>{LEVEL_SHORT[lvl]}</span>
      <span className="ex-id">{r.id}</span>
      <span className="ex-title">{r.title}</span>
      <span className="ex-glyphs">
        {hasOpenQuestions(r) && <span className="ex-q" title="has an open verify-intent question">?</span>}
        {row.hasChildren && !row.expanded && <span className="ex-count">{chip}</span>}
        <span className="ex-dot" title={r.status} style={{ background: statusDot(r.status) }} />
      </span>
    </div>
  );
}

function LinkGroup({ label, ids, count, onNav, emptyLabel }) {
  return (
    <div className="ex-link-group">
      <div className="ex-link-label">{label}{count != null && <span className="ex-link-n">{count}</span>}</div>
      {ids.length
        ? <div className="ex-link-ids">{ids.map((id) => (
          <button type="button" key={id} className="dep-link" onClick={() => onNav(id)}>{id}</button>
        ))}</div>
        : <div className="ex-link-empty">{emptyLabel}</div>}
    </div>
  );
}

function ExplorerLinks({ sel, h, setSelId, t }) {
  if (!sel) return null;
  const kids = h.childrenOf[sel.id] || [];
  const parents = h.parentOf[sel.id] ? [h.parentOf[sel.id]] : (sel.satisfies || []);
  return (
    <div className="sec ex-links">
      <div className="eyebrow">{t("Links — traceability")}</div>
      <LinkGroup label={t("satisfies (up)")} ids={parents} onNav={setSelId} emptyLabel={t("— top of the trace")} />
      <LinkGroup label={t("satisfied by (down)")} ids={kids} count={kids.length} onNav={setSelId} emptyLabel={t("— nothing decomposes this")} />
      <LinkGroup label={t("depends on (out)")} ids={sel.deps || []} onNav={setSelId} emptyLabel={t("— no outgoing dependency")} />
      <LinkGroup label={t("used by (in)")} ids={sel.usedBy || []} onNav={setSelId} emptyLabel={t("— nothing depends on this")} />
    </div>
  );
}

export function ExplorerView({ selId, setSelId, focus = null, clearFocus }) {
  const { t } = useI18n();
  const h = useMemo(() => buildHierarchy(REQUIREMENTS), [REQUIREMENTS]);
  const [expanded, setExpanded] = useState(() => defaultExpanded(h));
  const [levelFilter, setLevelFilter] = useState({});
  const [statusFilter, setStatusFilter] = useState(() => (focus && focus !== "orphan") ? { [focus]: true } : {});
  const [onlyQuestions, setOnlyQuestions] = useState(false);
  const [onlyOrphans, setOnlyOrphans] = useState(focus === "orphan");
  const listRef = useRef(null);

  useEffect(() => { setExpanded(defaultExpanded(h)); }, [h]);
  useEffect(() => {
    if (focus === "orphan") { setOnlyOrphans(true); setStatusFilter({}); }
    else if (focus) { setOnlyOrphans(false); setStatusFilter({ [focus]: true }); }
    else { setOnlyOrphans(false); setStatusFilter({}); }
  }, [focus]);

  const anyLevel = Object.keys(levelFilter).some((k) => levelFilter[k]);
  const anyStatus = Object.keys(statusFilter).some((k) => statusFilter[k]);
  const filtering = anyLevel || anyStatus || onlyQuestions || onlyOrphans;

  const matched = useMemo(() => {
    if (!filtering) return null;
    return REQUIREMENTS.filter((r) =>
      (!anyLevel || levelFilter[levelOf(r)]) &&
      (!anyStatus || statusFilter[r.status]) &&
      (!onlyQuestions || hasOpenQuestions(r)) &&
      (!onlyOrphans || isOrphan(r))
    ).map((r) => r.id);
  }, [filtering, anyLevel, anyStatus, onlyQuestions, onlyOrphans, levelFilter, statusFilter]);

  const keep = useMemo(() => (matched ? keepSetFor(h, matched) : null), [h, matched]);
  const rows = useMemo(() => flattenTree(h, { expanded, keep }), [h, expanded, keep]);
  const sel = selId && REQ_BY_ID[selId] ? REQ_BY_ID[selId] : (REQUIREMENTS[0] || null);
  const selKey = sel ? sel.id : null;

  useEffect(() => {
    if (!selKey || !h.byId[selKey]) return;
    const chain = ancestorsOf(h, selKey);
    if (!chain.length) return;
    setExpanded((prev) => {
      if (chain.every((a) => prev[a])) return prev;
      const next = Object.assign(Object.create(null), prev);
      chain.forEach((a) => { next[a] = true; });
      return next;
    });
  }, [selKey, h]);

  useEffect(() => {
    if (!selKey || !listRef.current) return;
    const el = listRef.current.querySelector('[data-req-row="' + selKey.replace(/"/g, '\\"') + '"]');
    if (el && el.scrollIntoView) el.scrollIntoView({ block: "nearest" });
  }, [selKey, rows]);

  const flip = (setter) => (key) => setter((prev) => {
    const next = Object.assign({}, prev);
    if (next[key]) delete next[key]; else next[key] = true;
    return next;
  });

  const crumbs = sel ? ancestorsOf(h, sel.id) : [];
  const breadcrumb = sel && crumbs.length > 0 && (
    <div className="ex-crumbs">
      {crumbs.map((id) => (
        <span key={id}>
          <button type="button" className="ex-crumb" onClick={() => setSelId(id)}>
            {(h.byId[id] && h.byId[id].title) || id}
          </button>
          <span className="ex-crumb-sep">/</span>
        </span>
      ))}
      <span className="ex-crumb cur">{sel.id}</span>
    </div>
  );

  return (
    <div className="main explorer">
      <div className="ex-pane">
        <ExplorerFilters
          levelFilter={levelFilter} flipLevel={flip(setLevelFilter)}
          statusFilter={statusFilter} flipStatus={flip(setStatusFilter)}
          onlyOrphans={onlyOrphans} setOnlyOrphans={setOnlyOrphans}
          onlyQuestions={onlyQuestions} setOnlyQuestions={setOnlyQuestions}
          clearFocus={clearFocus} rowsLength={rows.length} total={REQUIREMENTS.length}
          flat={h.flat} onExpandAll={() => setExpanded(allExpanded(h))}
          onCollapseAll={() => setExpanded(Object.create(null))}
        />
        <div className="ex-rows" ref={listRef}>
          {rows.map((row) => (
            <Row key={row.id} row={row} selected={selKey === row.id} onSelect={setSelId}
              onToggle={(id) => setExpanded((prev) => {
                const next = Object.assign(Object.create(null), prev);
                if (next[id]) delete next[id]; else next[id] = true;
                return next;
              })} />
          ))}
          {rows.length === 0 && <div className="ex-none">{t("No requirement matches these filters.")}</div>}
        </div>
      </div>
      <div className="ex-detail">
        {sel
          ? <SpecDoc r={sel} onNav={setSelId} head={breadcrumb}
              after={<ExplorerLinks sel={sel} h={h} setSelId={setSelId} t={t} />} />
          : <div className="ex-none">{t("No requirement selected.")}</div>}
      </div>
    </div>
  );
}
