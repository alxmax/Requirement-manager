/* RoadmapView — Gantt-style chart: semver milestones on X, swim lanes on Y.
   Requirements with `milestone:` field + TODO.md items via TODOS. */
import { useState, useRef } from "react";
import { REQUIREMENTS, TODOS } from "../lib/data.js";

function semverCmp(a, b) {
  const num = v => v.replace(/^v/i, "").split(".").map(n => parseInt(n, 10) || 0);
  const pa = num(a), pb = num(b);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const d = (pa[i] || 0) - (pb[i] || 0);
    if (d !== 0) return d;
  }
  return 0;
}

function barVariant(status) {
  if (status === "confirmed")   return "done";
  if (status === "in-progress") return "progress";
  if (status === "draft")       return "draft";
  return "planned";
}

const LANES      = ["bus", "feature", "ops"];
const LANE_LABEL = { bus: "Bus", feature: "Feature", ops: "Ops" };

const ARROW = "polygon(0 0, calc(100% - 7px) 0, 100% 50%, calc(100% - 7px) 100%, 0 100%)";

const VARIANT = {
  done:     { background: "var(--cov-tested-bg)",  color: "var(--cov-tested)",   dot: "var(--cov-tested)",   clipPath: ARROW, paddingRight: 20 },
  progress: { background: "var(--indigo-tint)",    color: "var(--indigo-500)",   dot: "var(--indigo-400)",   clipPath: ARROW, paddingRight: 20 },
  draft:    { background: "var(--amber-tint)",     color: "var(--amber-700)",    dot: "var(--amber-600)",    border: "1.5px dashed var(--amber-400)" },
  planned:  { background: "var(--surface-hov)",    color: "var(--fg-muted)",     dot: "var(--fg-faint)",     clipPath: ARROW, paddingRight: 20 },
  todo:     { background: "var(--amber-tint)",     color: "var(--amber-700)",    dot: "var(--amber-600)",    border: "1.5px dashed var(--amber-400)" },
};

function Bar({ variant, id, label, onClick }) {
  const v = VARIANT[variant] || VARIANT.planned;
  return (
    <span
      title={label}
      onClick={onClick}
      style={{
        display: "inline-flex", alignItems: "center", gap: 5,
        height: 24, borderRadius: 5, padding: `0 ${v.paddingRight || 12}px 0 9px`,
        fontSize: 11, fontWeight: 500, whiteSpace: "nowrap",
        cursor: onClick ? "pointer" : "default",
        clipPath: v.clipPath,
        background: v.background, color: v.color,
        border: v.border,
      }}
    >
      <span style={{ width: 5, height: 5, borderRadius: "50%", flexShrink: 0, background: v.dot }} />
      {id && <span style={{ fontSize: 9, opacity: 0.5, fontWeight: 600, letterSpacing: "0.3px" }}>{id}</span>}
      {label}
    </span>
  );
}

export function RoadmapView({ openSpec }) {
  const [showUnscheduled, setShowUnscheduled] = useState(false);
  const ref = useRef(null);
  const drag = useRef(null);
  function onMouseDown(e) {
    if (e.button !== 0) return;
    const el = ref.current; if (!el) return;
    const d = { x: e.clientX, y: e.clientY, sl: el.scrollLeft, st: el.scrollTop, moved: false };
    drag.current = d;
    const move = (ev) => {
      const dx = ev.clientX - d.x, dy = ev.clientY - d.y;
      if (!d.moved && Math.abs(dx) + Math.abs(dy) > 4) { d.moved = true; el.classList.add("grabbing"); }
      if (d.moved) { el.scrollLeft = d.sl - dx; el.scrollTop = d.st - dy; }
    };
    const up = () => {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", up);
      el.classList.remove("grabbing");
      setTimeout(() => { drag.current = null; }, 0);
    };
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", up);
  }
  function onClickCapture(e) {
    if (drag.current && drag.current.moved) { e.stopPropagation(); e.preventDefault(); }
  }

  const msSet = new Set();
  REQUIREMENTS.forEach(r => { if (r.milestone && r.status !== "deprecated") msSet.add(r.milestone); });
  TODOS.forEach(t => { if (!t.done && t.milestone) msSet.add(t.milestone); });
  const milestones = Array.from(msSet).sort(semverCmp);

  const current =
    milestones.find(ms => REQUIREMENTS.some(r => r.milestone === ms && r.status === "in-progress")) ||
    [...milestones].reverse().find(ms => REQUIREMENTS.some(r => r.milestone === ms && r.status === "confirmed"));

  const unscheduled = REQUIREMENTS.filter(r => !r.milestone && r.status !== "deprecated");

  if (!milestones.length && !unscheduled.length) {
    return (
      <div className="main" style={{ padding: 40, color: "var(--fg-faint)", fontSize: 13 }}>
        No milestones yet. Add <code>milestone: v1.x</code> to requirement frontmatter
        or create a <code>TODO.md</code> with <code>## v1.x</code> sections.
      </div>
    );
  }

  const rows = LANES.flatMap(lane => {
    const reqs  = REQUIREMENTS.filter(r => r.layer === lane && r.milestone && r.status !== "deprecated");
    const todos = TODOS.filter(t => t.lane === lane && !t.done);
    const byMs  = Object.fromEntries(milestones.map(ms => [ms, []]));
    reqs.forEach(r  => { if (byMs[r.milestone])  byMs[r.milestone].push({ type: "req",  r  }); });
    todos.forEach(t => { if (byMs[t.milestone])  byMs[t.milestone].push({ type: "todo", t  }); });
    const maxRows = Math.max(1, ...Object.values(byMs).map(a => a.length));
    return Array.from({ length: maxRows }, (_, i) => ({ lane, rowIdx: i, maxRows, byMs }));
  });

  const thBase = {
    background: "var(--bg-raised)", color: "var(--fg-muted)", fontSize: 11, fontWeight: 600,
    letterSpacing: "0.4px", padding: "10px 14px", textAlign: "center",
    borderBottom: "1px solid var(--border)", borderRight: "1px solid var(--border)", whiteSpace: "nowrap",
  };

  return (
    <div ref={ref} onMouseDown={onMouseDown} onClickCapture={onClickCapture}
         className="main pan" style={{ overflow: "auto", padding: "24px 20px" }}>
      <table style={{ borderCollapse: "separate", borderSpacing: 0, width: "max-content", minWidth: 560 }}>
        <thead>
          <tr>
            <th style={{ ...thBase, background: "transparent", border: "none", width: 60 }} />
            {milestones.map(ms => (
              <th key={ms} style={{ ...thBase, ...(ms === current ? { background: "var(--surface-hov)", color: "var(--fg)", fontWeight: 700 } : {}) }}>
                {ms}
                {ms === current && (
                  <span style={{ display: "inline-block", width: 6, height: 6, background: "var(--accent-2)",
                    borderRadius: "50%", marginLeft: 5, verticalAlign: "middle", position: "relative", top: -1 }} />
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map(({ lane, rowIdx, maxRows, byMs }) => (
            <tr key={`${lane}-${rowIdx}`}>
              {rowIdx === 0 && (
                <td rowSpan={maxRows} style={{
                  fontSize: 10, fontWeight: 700, letterSpacing: "0.8px", textTransform: "uppercase",
                  color: "var(--fg-faint)", padding: "0 14px", textAlign: "right", verticalAlign: "middle",
                  borderRight: "1px solid var(--border)", whiteSpace: "nowrap", background: "var(--bg-raised)", minWidth: 60,
                }}>
                  {LANE_LABEL[lane]}
                </td>
              )}
              {milestones.map(ms => {
                const item = byMs[ms][rowIdx];
                return (
                  <td key={ms} style={{
                    padding: "6px 10px", borderBottom: "1px solid var(--border-soft)", borderRight: "1px solid var(--border-soft)",
                    background: "var(--surface)", verticalAlign: "middle",
                  }}>
                    {item?.type === "req" && (
                      <Bar variant={barVariant(item.r.status)} id={item.r.id} label={item.r.title}
                           onClick={() => openSpec(item.r.id)} />
                    )}
                    {item?.type === "todo" && (
                      <Bar variant="todo" label={item.t.name} onClick={() => {}} />
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      {unscheduled.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <button
            onClick={() => setShowUnscheduled(s => !s)}
            style={{ background: "none", border: "none", cursor: "pointer", padding: "4px 0",
                     color: "var(--fg-faint)", fontSize: 12, fontFamily: "inherit" }}
          >
            {showUnscheduled ? "▾" : "▸"} Unscheduled ({unscheduled.length})
          </button>
          {showUnscheduled && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8, padding: "0 4px" }}>
              {unscheduled.map(r => (
                <Bar key={r.id} variant={barVariant(r.status)} id={r.id} label={r.title}
                     onClick={() => openSpec(r.id)} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
