/* MapView — the flagship interactive graph explorer (4 tabs + detail panel).
 * Layout is computed from the live registry (see ../lib/layout.js) — no
 * hand-tuned coordinates — so it renders any repo's requirements, not a fixture. */
import { useState, useMemo, useRef } from "react";
import { REQUIREMENTS, REQ_BY_ID } from "../lib/data.js";
import { Pill, Btn, statusKind } from "../lib/ui.jsx";
import { Icon, LocateGlyph } from "../lib/icons.jsx";
import { computeLayout, colorFor, buildEdgePath, NODE_W, NODE_CY } from "../lib/layout.js";

function NodeBox({ r, pos, selected, highlighted, edgeEnd, riskClass, onClick }) {
  const p = pos[r.id]; if (!p) return null;
  const cls = ["node",
    r.layer === "bus" ? "bus" : "",
    selected ? "sel" : "",
    highlighted ? "hl" : "",
    riskClass || ""].join(" ");
  const style = { left: p[0], top: p[1], width: NODE_W };
  // ring the two endpoints of a selected edge so x→y is unambiguous
  if (edgeEnd && !selected) style.boxShadow = "0 0 0 3px var(--accent), var(--shadow-2)";
  return (
    <div className={cls} style={style} onClick={() => onClick(r.id)}>
      <span className="nt">{r.title}</span>
      <span className="ni">{r.id}</span>
    </div>
  );
}

/* Card-avoiding orthogonal edges (see buildEdgePath): verticals run in the column
 * gutters and intermediate columns are crossed only through card gaps, so a line
 * never runs through a card it doesn't connect to. Each edge is its source
 * requirement's colour and is clickable — click to isolate it + ring its endpoints. */
function fallbackPath(A, B) {
  const sx = A[0] + NODE_W, sy = A[1] + NODE_CY, tx = B[0], ty = B[1] + NODE_CY, mx = (sx + tx) / 2;
  return `M${sx},${sy} C${mx},${sy} ${mx},${ty} ${tx},${ty}`;
}
function Edges({ meta, selKey, onSelect }) {
  const edges = meta.edges || [];
  return (
    <svg className="svg-edges">
      <defs>
        {/* context-stroke → the arrowhead inherits each path's own stroke colour */}
        <marker id="arrow" markerWidth="11" markerHeight="11" refX="8" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="context-stroke" />
        </marker>
      </defs>
      {edges.map(([a, b], i) => {
        const A = meta.pos[a], B = meta.pos[b]; if (!A || !B) return null;
        const d = buildEdgePath(meta, a, b) || fallbackPath(A, B);
        const key = a + "|" + b, on = selKey === key, dim = selKey && !on;
        return (
          <g key={i}>
            {/* wide invisible hit-area so thin lines are easy to click */}
            <path d={d} fill="none" stroke="transparent" strokeWidth="16"
              style={{ pointerEvents: "stroke", cursor: "pointer" }}
              onClick={(e) => { e.stopPropagation(); onSelect(on ? null : [a, b]); }} />
            <path d={d} fill="none" stroke={colorFor(a).line} strokeWidth={on ? 3.4 : 1.8}
              markerEnd="url(#arrow)" opacity={dim ? 0.1 : 0.9} style={{ pointerEvents: "none" }} />
          </g>
        );
      })}
    </svg>
  );
}

/* Scrollable canvas you can also grab-to-pan: drag anywhere to scroll; a real
 * click (no drag) still falls through to node/edge selection. A drag past a small
 * threshold is swallowed in the capture phase so it never triggers a selection. */
function Canvas({ width, height, minHeight, onClear, children }) {
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
  return (
    <div className="canvas pan" ref={ref} onMouseDown={onMouseDown} onClickCapture={onClickCapture}>
      <div className="canvas-inner" style={{ width, height, minHeight }} onClick={onClear}>
        {children}
      </div>
    </div>
  );
}

/* tiny inline-markdown: HTML-escape first, then `code` → <code>. Escaping is
 * mandatory: the output feeds dangerouslySetInnerHTML and the text is untrusted
 * requirement markdown carried verbatim from _map.json. */
function mdInline(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function DetailPanel({ r, onClose, onLocate, onOpenSpec }) {
  if (!r) return null;
  return (
    <aside className="panel">
      <div className="panel-head">
        <span className="pid">{r.id}</span>
        <Pill kind={statusKind(r.status)}>{r.status}</Pill>
        <Pill kind={r.layer}>{r.layer}</Pill>
        <button className="locate-btn" title="center & highlight in the map" onClick={onLocate}><LocateGlyph /></button>
        <button className="btn-icon bare x" title="close" onClick={onClose}><Icon name="x" size={16} /></button>
      </div>
      <h2>{r.title}</h2>
      <div className="lbl">Why — Intent</div>
      <p className="why">{r.intent}</p>

      <div className="lbl">What — Contract</div>
      <ul>{r.contract.map((c, i) => <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(c) }} />)}</ul>

      <div className="lbl">How — Acceptance</div>
      {r.gwt
        ? <div className="gwt-mini members" style={{ whiteSpace: "pre-wrap" }}>{r.gwt}</div>
        : <ul>{(r.acc || []).map((a, i) => <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(a) }} />)}</ul>}

      <div className="lbl">Where — Members in code</div>
      <div className="members">
        {r.members.length
          ? r.members.map((m, i) => <div className="member" key={i}><span className="role">{m.role}:</span> {m.loc}</div>)
          : r.layer === "need"
            ? <div className="member" style={{ color: "var(--fg-muted)" }}>(satisfied-by other requirements — no direct code)</div>
            : <div className="member" style={{ color: "var(--status-error)" }}>(no members found)</div>}
      </div>

      <div className="kv"><span className="k">Depends on</span><span className="v">{r.deps.join(" · ") || "— (bus)"}</span></div>
      <div className="kv"><span className="k">Used by</span><span className="v">{r.usedBy.join(" · ") || "—"}</span></div>

      {r.risks && r.risks.length > 0 && (<>
        <div className="lbl risk">Risk — recommended action</div>
        {r.risks.map((rk, i) => <div className="members" key={i} style={{ marginTop: 4 }}>
          <b style={{ color: "var(--fg)" }}>{rk.signal}</b> — <span style={{ color: "var(--fg-muted)" }}>{rk.advice}</span></div>)}
      </>)}

      <div style={{ marginTop: 18 }}>
        <Btn variant="secondary" icon="file-text" onClick={() => onOpenSpec(r.id)}>Open full spec</Btn>
      </div>
    </aside>
  );
}

const MAP_TABS = [
  { key: "system", label: "System Map" },
  { key: "reqcode", label: "Req→Code" },
  { key: "deps", label: "Dependencies" },
  { key: "risk", label: "Risk" },
];

export function MapView({ selId, setSelId, openSpec, highlightId, setHighlightId }) {
  const [tab, setTab] = useState("system");
  const [selEdge, setSelEdge] = useState(null); // [a,b] of the clicked edge, or null
  const sel = selId ? REQ_BY_ID[selId] : null;
  const selKey = selEdge ? selEdge[0] + "|" + selEdge[1] : null;
  const edgeEnds = selEdge ? new Set(selEdge) : null;

  // computed layouts (recomputed only when the registry reference changes)
  const sys = useMemo(() => computeLayout(REQUIREMENTS), [REQUIREMENTS]);

  const flagged = useMemo(() => REQUIREMENTS.filter(r => (r.risks || []).length > 0), [REQUIREMENTS]);
  const riskLayout = useMemo(() => computeLayout(flagged, { colW: 300, rowH: 150 }), [flagged]);

  const depsGraph = useMemo(() => {
    const idArea = {}, byArea = {};
    REQUIREMENTS.forEach(r => { const a = r.area || "?"; idArea[r.id] = a; (byArea[a] = byArea[a] || []).push(r.id); });
    const ae = new Set();
    REQUIREMENTS.forEach(r => (r.deps || []).forEach(d => {
      const x = idArea[r.id], y = idArea[d]; if (x && y && x !== y && idArea[d]) ae.add(x + "" + y);
    }));
    const pseudo = Object.keys(byArea).map(a => ({
      id: a, deps: [...ae].filter(e => e.startsWith(a + "")).map(e => e.split("")[1]),
    }));
    return { layout: computeLayout(pseudo, { colW: 320, rowH: 150 }), count: byArea };
  }, [REQUIREMENTS]);

  const legend = {
    system: <><span className="pdot" style={{ width: 9, height: 9, borderRadius: 0, border: "3px solid var(--ink-0)", display: "inline-block" }} /> bus · arrows = depends_on · edge colour = source</>,
    reqcode: <>requirement → its code · <span style={{ color: "var(--accent)" }}>implements</span> / tested-by</>,
    deps: <>area-level coupling · arrow A→B = A depends on B</>,
    risk: <>only requirements with ≥1 open risk signal</>,
  }[tab];

  function locate() {
    if (!selId) return;
    setHighlightId(selId);
    setTimeout(() => {
      const el = document.querySelector(".node.hl");
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
    }, 60);
    setTimeout(() => setHighlightId(null), 2200);
  }

  return (
    <div className="main">
      <div className="tabbar">
        {MAP_TABS.map(t => (
          <button key={t.key} className={"tab" + (tab === t.key ? " on" : "")} onClick={() => { setTab(t.key); setSelEdge(null); }}>{t.label}</button>
        ))}
        <div className="tab-legend">{legend}</div>
      </div>

      <div className={"map-wrap" + (sel ? " with-panel" : "")}>
        {tab === "system" && (
          <Canvas width={sys.width} height={sys.height} onClear={() => setSelEdge(null)}>
            <div className="subgraph-label" style={{ left: 50, top: 12 }}>consumers → depends on → foundation · drag to pan · click a line to trace it</div>
            <Edges meta={sys} selKey={selKey} onSelect={setSelEdge} />
            {REQUIREMENTS.filter(r => sys.pos[r.id]).map(r => (
              <NodeBox key={r.id} r={r} pos={sys.pos} selected={selId === r.id}
                highlighted={highlightId === r.id} edgeEnd={edgeEnds && edgeEnds.has(r.id)} onClick={setSelId} />
            ))}
          </Canvas>
        )}

        {tab === "reqcode" && <ReqCodeView selId={selId} setSelId={setSelId} />}

        {tab === "deps" && (
          <Canvas width={depsGraph.layout.width} height={depsGraph.layout.height} onClear={() => setSelEdge(null)}>
            <Edges meta={depsGraph.layout} selKey={selKey} onSelect={setSelEdge} />
            {Object.keys(depsGraph.count).map(area => {
              const p = depsGraph.layout.pos[area]; if (!p) return null;
              return (
                <div key={area} className="node" style={{ left: p[0], top: p[1], width: NODE_W }}>
                  <span className="nt">{area}</span>
                  <span className="ni">{depsGraph.count[area].length} caps</span>
                </div>
              );
            })}
          </Canvas>
        )}

        {tab === "risk" && (
          <Canvas width={riskLayout.width} height={riskLayout.height} minHeight={520} onClear={() => setSelEdge(null)}>
            {flagged.length === 0 && <div className="subgraph-label" style={{ left: 50, top: 30 }}>no open risk signals 🎉</div>}
            <Edges meta={riskLayout} selKey={selKey} onSelect={setSelEdge} />
            {flagged.filter(r => riskLayout.pos[r.id]).map(r => {
              const sig = r.risks[0]?.signal;
              const rc = sig === "unimplemented" ? "risk-error"
                : (sig === "drift" || sig === "blast-radius" || sig === "unreviewed") ? "risk-blast" : "";
              return <NodeBox key={r.id} r={r} pos={riskLayout.pos} selected={selId === r.id}
                highlighted={highlightId === r.id} edgeEnd={edgeEnds && edgeEnds.has(r.id)} riskClass={rc} onClick={setSelId} />;
            })}
          </Canvas>
        )}

        {sel && <DetailPanel r={sel} onClose={() => setSelId(null)} onLocate={locate} onOpenSpec={openSpec} />}
      </div>
    </div>
  );
}

function ReqCodeView({ selId, setSelId }) {
  return (
    <div style={{ padding: "18px 22px", overflow: "auto" }}>
      {REQUIREMENTS.map(r => (
        <div key={r.id} onClick={() => setSelId(r.id)} style={{
          display: "grid", gridTemplateColumns: "240px 1fr", gap: 18, padding: "11px 12px",
          borderBottom: "1px solid var(--border-soft)", cursor: "pointer",
          background: selId === r.id ? "var(--surface)" : "transparent",
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <span style={{ font: "var(--text-id)" }}>{r.id}</span>
            <span style={{ font: "var(--text-small)", color: "var(--fg-muted)" }}>{r.title}</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 2, justifyContent: "center" }}>
            {r.members.length ? r.members.map((m, i) => (
              <div key={i} style={{ font: "var(--text-code)", color: "var(--fg-muted)" }}>
                <span style={{ color: m.role === "implements" ? "var(--accent)" : "var(--fg-muted)" }}>{m.role}:</span> {m.loc}
              </div>
            )) : r.layer === "need"
              ? <div style={{ font: "var(--text-code)", color: "var(--fg-muted)" }}>(satisfied-by — no direct code, gate-exempt)</div>
              : <div style={{ font: "var(--text-code)", color: "var(--status-error)" }}>(no members — orphan, gate ERROR)</div>}
          </div>
        </div>
      ))}
    </div>
  );
}
