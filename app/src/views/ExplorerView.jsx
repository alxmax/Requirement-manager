// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-945
/* ExplorerView — the module explorer (the DOORS shape).
 *
 * A persistent outline of the whole registry on the left, one row per
 * requirement in hierarchy order; the selected requirement's document on the
 * right, with traceability shown as links IN and OUT rather than as a graph.
 *
 * The corpus this was built for is 685 requirements on three levels, 618 of
 * them `level: code`. Two consequences shape everything here:
 *   - code children start COLLAPSED behind a per-parent count chip, so the
 *     default paint is 67 rows (root + 8 systems + 58 architectures) — the
 *     substance, not the noise;
 *   - `area` is not a grouping any more (640 of 685 are area REQ), so the
 *     outline groups by TRACE (`satisfies`), which is the real structure.
 * No virtualisation: fully expanded is 685 plain rows, measured cheap. */
import { useEffect, useMemo, useRef, useState } from "react";
import { REQUIREMENTS, REQ_BY_ID } from "../lib/data.js";
import { SpecDoc, ENFORCED } from "./SpecView.jsx";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";
import {
  LEVELS, LEVEL_LABEL, LEVEL_SHORT, levelOf, buildHierarchy, ancestorsOf,
  defaultExpanded, allExpanded, keepSetFor, flattenTree, hasOpenQuestions,
} from "../lib/tree.js";

const STATUSES = ["confirmed", "in-progress", "draft", "deprecated"];

/* The gate's own error condition, not a status: an ENFORCED requirement with no
 * `implements:` member. Kept identical to the rail's tally so the count you click
 * and the rows you get are the same set. */
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

function Chip({ on, onClick, children, title }) {
  return (
    <button type="button" className={"ex-chip" + (on ? " on" : "")} onClick={onClick} title={title}>
      {children}
    </button>
  );
}

/* One outline row. `context` marks an ancestor kept only to place a match. */
function Row({ row, selected, onSelect, onToggle }) {
  const r = row.r;
  const lvl = levelOf(r);
  const cls = ["ex-row", selected ? "sel" : "", row.context ? "ctx" : ""].join(" ").trim();
  // "1 clauses" is the kind of detail that makes a tool look unfinished.
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

/* Traceability, as four labelled groups. Up (satisfies), down (satisfied by),
 * out (depends_on), in (used by) — the whole trace neighbourhood of one item on
 * one screen, which is the thing a graph view never gives you at 685 nodes. */
function LinkGroup({ label, ids, count, onNav, emptyLabel }) {
  return (
    <div className="ex-link-group">
      <div className="ex-link-label">{label}{count != null && <span className="ex-link-n">{count}</span>}</div>
      {ids.length
        ? <div className="ex-link-ids">
            {ids.map((id) => (
              <button type="button" key={id} className="dep-link" onClick={() => onNav(id)}>{id}</button>
            ))}
          </div>
        : <div className="ex-link-empty">{emptyLabel}</div>}
    </div>
  );
}

export function ExplorerView({ selId, setSelId, focus = null, clearFocus }) {
  const { t } = useI18n();
  const h = useMemo(() => buildHierarchy(REQUIREMENTS), [REQUIREMENTS]);
  const [expanded, setExpanded] = useState(() => defaultExpanded(h));
  const [levelFilter, setLevelFilter] = useState({});   // {} = no level filter
  // Seeded from `focus` rather than applied by the effect below alone: effects do
  // not run during server rendering, so an effect-only wiring would leave the very
  // first paint (and the SSR smoke) showing an unfiltered outline.
  const [statusFilter, setStatusFilter] = useState(
    () => (focus && focus !== "orphan") ? { [focus]: true } : {});
  const [onlyQuestions, setOnlyQuestions] = useState(false);
  const [onlyOrphans, setOnlyOrphans] = useState(focus === "orphan");
  const listRef = useRef(null);

  // Re-seed the expansion when the registry itself is replaced (loadData()
  // swaps the baked fallback for the engine export after first paint).
  useEffect(() => { setExpanded(defaultExpanded(h)); }, [h]);

  // A registry row clicked in the rail sets the filters it names; the chips stay
  // the visible, clearable truth, so the two controls never disagree.
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
  }, [REQUIREMENTS, filtering, anyLevel, anyStatus, onlyQuestions, onlyOrphans, levelFilter, statusFilter]);

  const keep = useMemo(() => (matched ? keepSetFor(h, matched) : null), [h, matched]);
  const rows = useMemo(() => flattenTree(h, { expanded, keep }), [h, expanded, keep]);

  const sel = selId && REQ_BY_ID[selId] ? REQ_BY_ID[selId] : (REQUIREMENTS[0] || null);
  const selKey = sel ? sel.id : null;

  // A selection made anywhere else (search, a link, the #/req/<ID> hash) must
  // open its ancestor chain and scroll the row into view — otherwise the deep
  // link lands on a document whose row is three collapsed levels away.
  useEffect(() => {
    if (!selKey || !h.byId[selKey]) return;
    const chain = ancestorsOf(h, selKey);
    if (chain.length) {
      setExpanded((prev) => {
        if (chain.every((a) => prev[a])) return prev;
        const next = Object.assign(Object.create(null), prev);
        chain.forEach((a) => { next[a] = true; });
        return next;
      });
    }
  }, [selKey, h]);

  useEffect(() => {
    if (!selKey || !listRef.current) return;
    const el = listRef.current.querySelector('[data-req-row="' + selKey.replace(/"/g, '\\"') + '"]');
    if (el && el.scrollIntoView) el.scrollIntoView({ block: "nearest" });
  }, [selKey, rows]);

  const toggle = (id) => setExpanded((prev) => {
    const next = Object.assign(Object.create(null), prev);
    if (next[id]) delete next[id]; else next[id] = true;
    return next;
  });
  const flip = (setter) => (key) => setter((prev) => {
    const next = Object.assign({}, prev);
    if (next[key]) delete next[key]; else next[key] = true;
    return next;
  });
  const flipLevel = flip(setLevelFilter);
  const flipStatus = flip(setStatusFilter);

  const kids = sel ? (h.childrenOf[sel.id] || []) : [];
  const parents = sel ? (h.parentOf[sel.id] ? [h.parentOf[sel.id]] : (sel.satisfies || [])) : [];
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

  const links = sel && (
    <div className="sec ex-links">
      <div className="eyebrow">{t("Links — traceability")}</div>
      <LinkGroup label={t("satisfies (up)")} ids={parents} onNav={setSelId}
        emptyLabel={t("— top of the trace")} />
      <LinkGroup label={t("satisfied by (down)")} ids={kids} count={kids.length} onNav={setSelId}
        emptyLabel={t("— nothing decomposes this")} />
      <LinkGroup label={t("depends on (out)")} ids={sel.deps || []} onNav={setSelId}
        emptyLabel={t("— no outgoing dependency")} />
      <LinkGroup label={t("used by (in)")} ids={sel.usedBy || []} onNav={setSelId}
        emptyLabel={t("— nothing depends on this")} />
    </div>
  );

  return (
    <div className="main explorer">
      <div className="ex-pane">
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
            <Chip on={onlyOrphans}
              title="enforced requirements with no implements: member"
              onClick={() => { if (clearFocus) clearFocus(); setOnlyOrphans((v) => !v); }}>orphan</Chip>
          </div>
          <div className="ex-filter-row">
            <Chip on={onlyQuestions} onClick={() => setOnlyQuestions((v) => !v)}
              title="only requirements with an unanswered verify-intent bullet">
              {t("has open question")}
            </Chip>
            <span className="ex-spacer" />
            <button type="button" className="ex-mini" onClick={() => setExpanded(allExpanded(h))}>{t("expand all")}</button>
            <button type="button" className="ex-mini" onClick={() => setExpanded(Object.create(null))}>{t("collapse all")}</button>
          </div>
          <div className="ex-tally">
            {t("{shown} of {total} shown", { shown: rows.length, total: REQUIREMENTS.length })}
            {h.flat && <span className="ex-flatnote">{t("· no hierarchy in this map — flat list")}</span>}
          </div>
        </div>
        <div className="ex-rows" ref={listRef}>
          {rows.map((row) => (
            <Row key={row.id} row={row} selected={selKey === row.id}
              onSelect={setSelId} onToggle={toggle} />
          ))}
          {rows.length === 0 && <div className="ex-none">{t("No requirement matches these filters.")}</div>}
        </div>
      </div>
      <div className="ex-detail">
        {sel
          ? <SpecDoc r={sel} onNav={setSelId} head={breadcrumb} after={links} />
          : <div className="ex-none">{t("No requirement selected.")}</div>}
      </div>
    </div>
  );
}
