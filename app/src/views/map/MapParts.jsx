// implements: ARCH-VIEWER-007
import { Pill, Btn, statusKind, mdInline, reqLinkProps } from "../../lib/ui.jsx";
import { Icon, LocateGlyph } from "../../lib/icons.jsx";
import { useI18n } from "../../lib/i18n.jsx";
import { colorFor, buildEdgePath, NODE_W, NODE_CY } from "../../lib/layout.js";

/** One requirement on a map. `marks` is how it is shown: `selected`, `highlighted`,
 *  `edgeEnd` (an end of the selected edge), `riskClass` and `codeCount`. */
export function MapNodeBox({ r, pos, marks, onClick }) {
  const p = pos[r.id];
  if (!p) return null;
  const { selected, highlighted, edgeEnd, riskClass, codeCount } = marks;
  const cls = ["node",
    r.layer === "bus" ? "bus" : "",
    r.level === "system" ? "sys" : "",
    selected ? "sel" : "",
    highlighted ? "hl" : "",
    riskClass || ""].join(" ");
  const style = { left: p[0], top: p[1], width: NODE_W };
  if (edgeEnd && !selected) style.boxShadow = "0 0 0 3px var(--accent), var(--shadow-2)";
  return (
    <div className={cls} style={style} onClick={() => onClick(r.id)}>
      <span className="nt">{r.title}</span>
      <span className="ni">{r.id}{codeCount > 0 ? ` · ${codeCount} code` : ""}</span>
    </div>
  );
}

function fallbackPath(A, B) {
  const sx = A[0] + NODE_W, sy = A[1] + NODE_CY, tx = B[0], ty = B[1] + NODE_CY;
  const mx = (sx + tx) / 2;
  return `M${sx},${sy} C${mx},${sy} ${mx},${ty} ${tx},${ty}`;
}

export function MapEdges({ meta, selKey, onSelect, markerId = "arrow" }) {
  const edges = meta.edges || [];
  return (
    <svg className="svg-edges">
      <defs>
        <marker id={markerId} markerWidth="11" markerHeight="11" refX="8" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="context-stroke" />
        </marker>
      </defs>
      {edges.map(([a, b], i) => {
        const A = meta.pos[a], B = meta.pos[b];
        if (!A || !B) return null;
        const d = buildEdgePath(meta, a, b) || fallbackPath(A, B);
        const key = a + "|" + b, on = selKey === key, dim = selKey && !on;
        return (
          <g key={i}>
            <path d={d} fill="none" stroke="transparent" strokeWidth="16"
              style={{ pointerEvents: "stroke", cursor: "pointer" }}
              onClick={(e) => { e.stopPropagation(); onSelect(on ? null : [a, b]); }} />
            <path d={d} fill="none" stroke={colorFor(a).line} strokeWidth={on ? 3.4 : 1.8}
              markerEnd={`url(#${markerId})`} opacity={dim ? 0.1 : 0.9}
              style={{ pointerEvents: "none" }} />
          </g>
        );
      })}
    </svg>
  );
}

/** A pannable, zoomable canvas. `size` is `{ width, height, minHeight }`; `pan` carries the
 *  canvas ref and the drag-to-pan handlers from `useDragPan`. */
export function MapCanvas({ size, zoom, pan, onClear, children }) {
  const { width, height, minHeight } = size;
  return (
    <div className="canvas pan" ref={pan.canvasRef} onMouseDown={pan.onMouseDown}
         onClickCapture={pan.onClickCapture}>
      <div className="canvas-inner" style={{ width, height, minHeight, zoom: zoom / 100 }}
           onClick={onClear}>
        {children}
      </div>
    </div>
  );
}

const MUTED = { color: "var(--fg-muted)" };

function PanelMembers({ r }) {
  if (r.members.length) {
    return r.members.map((m, i) => (
      <div className="member" key={i}><span className="role">{m.role}:</span> {m.loc}</div>
    ));
  }
  return r.layer === "need"
    ? <div className="member" style={MUTED}>(satisfied-by other requirements — no direct code)</div>
    : <div className="member" style={{ color: "var(--status-error)" }}>(no members found)</div>;
}

function Kv({ k, v }) {
  return <div className="kv"><span className="k">{k}</span><span className="v">{v}</span></div>;
}

function PanelRisks({ r, t }) {
  if (!r.risks || !r.risks.length) return null;
  return (
    <>
      <div className="lbl risk">{t("Risk — recommended action")}</div>
      {r.risks.map((rk, i) => (
        <div className="members" key={i} style={{ marginTop: 4 }}>
          <b style={{ color: "var(--fg)" }}>{rk.signal}</b> — <span style={MUTED}>{rk.advice}</span>
        </div>
      ))}
    </>
  );
}

function PanelCases({ r, onOpenSpec }) {
  if (r.gwt) {
    return <div className="gwt-mini members" style={{ whiteSpace: "pre-wrap" }}>{r.gwt}</div>;
  }
  return (
    <ul {...reqLinkProps(onOpenSpec)}>{(r.acc || []).map((a, i) => (
      <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(a) }} />))}</ul>
  );
}

export function MapDetailPanel({ r, onClose, onLocate, onOpenSpec }) {
  const { t } = useI18n();
  if (!r) return null;
  return (
    <aside className="panel">
      <div className="panel-head">
        <span className="pid">{r.id}</span>
        <Pill kind={statusKind(r.status)}>{r.status}</Pill>
        <Pill kind={r.layer}>{r.layer}</Pill>
        <button className="locate-btn" title={t("center & highlight in the map")}
                onClick={onLocate}><LocateGlyph /></button>
        <button className="btn-icon bare x" title={t("close")} onClick={onClose}>
          <Icon name="x" size={16} />
        </button>
      </div>
      <h2>{r.title}</h2>
      {r.intent && <>
        <div className="lbl">{t("Why — Intent")}</div>
        <p className="why">{r.intent}</p>
      </>}
      <div className="lbl">{t("Description")}</div>
      <ul {...reqLinkProps(onOpenSpec)}>{r.contract.map((c, i) => (
        <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(c) }} />))}</ul>
      <div className="lbl">{t("Cases")}</div>
      <PanelCases r={r} onOpenSpec={onOpenSpec} />
      <div className="lbl">{t("Where — Members in code")}</div>
      <div className="members"><PanelMembers r={r} /></div>
      <Kv k={t("Depends on")} v={r.deps.join(" · ") || "— (bus)"} />
      <Kv k={t("Used by")} v={r.usedBy.join(" · ") || "—"} />
      <PanelRisks r={r} t={t} />
      <div style={{ marginTop: 18 }}>
        <Btn variant="secondary" icon="file-text" onClick={() => onOpenSpec(r.id)}>
          {t("Open full spec")}
        </Btn>
      </div>
    </aside>
  );
}

const CODE = { font: "var(--text-code)", color: "var(--fg-muted)" };
const ORPHAN = { ...CODE, color: "var(--status-error)" };

function RowMembers({ r }) {
  if (r.members.length) {
    return r.members.map((m, i) => (
      <div key={i} style={CODE}>
        <span style={{ color: m.role === "implements" ? "var(--accent)" : "var(--fg-muted)" }}>
          {m.role}:
        </span> {m.loc}
      </div>
    ));
  }
  return r.layer === "need"
    ? <div style={CODE}>(satisfied-by — no direct code, gate-exempt)</div>
    : <div style={ORPHAN}>(no members — orphan, gate ERROR)</div>;
}

export function ReqCodeView({ selId, setSelId, rows }) {
  const rowStyle = (r) => ({
    display: "grid", gridTemplateColumns: "240px 1fr", gap: 18, padding: "11px 12px",
    borderBottom: "1px solid var(--border-soft)", cursor: "pointer",
    background: selId === r.id ? "var(--surface)" : "transparent",
  });
  const members = { display: "flex", flexDirection: "column", gap: 2, justifyContent: "center" };
  return (
    <div style={{ padding: "18px 22px", overflow: "auto" }}>
      {rows.map((r) => (
        <div key={r.id} onClick={() => setSelId(r.id)} style={rowStyle(r)}>
          <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            <span style={{ font: "var(--text-id)" }}>{r.id}</span>
            <span style={{ font: "var(--text-small)", color: "var(--fg-muted)" }}>{r.title}</span>
          </div>
          <div style={members}><RowMembers r={r} /></div>
        </div>
      ))}
    </div>
  );
}
