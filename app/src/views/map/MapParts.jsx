// implements: ARCH-VIEWER-007
import { Pill, Btn, statusKind, mdInline, reqLinkProps } from "../../lib/ui.jsx";
import { Icon, LocateGlyph } from "../../lib/icons.jsx";
import { useI18n } from "../../lib/i18n.jsx";
import { colorFor, buildEdgePath, NODE_W, NODE_CY } from "../../lib/layout.js";

export function MapNodeBox({ r, pos, selected, highlighted, edgeEnd, riskClass, codeCount, onClick }) {
  const p = pos[r.id];
  if (!p) return null;
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
              markerEnd={`url(#${markerId})`} opacity={dim ? 0.1 : 0.9} style={{ pointerEvents: "none" }} />
          </g>
        );
      })}
    </svg>
  );
}

export function MapCanvas({ width, height, minHeight, zoom, canvasRef, onClear, onMouseDown, onClickCapture, children }) {
  return (
    <div className="canvas pan" ref={canvasRef} onMouseDown={onMouseDown} onClickCapture={onClickCapture}>
      <div className="canvas-inner" style={{ width, height, minHeight, zoom: zoom / 100 }} onClick={onClear}>
        {children}
      </div>
    </div>
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
        <button className="locate-btn" title={t("center & highlight in the map")} onClick={onLocate}><LocateGlyph /></button>
        <button className="btn-icon bare x" title={t("close")} onClick={onClose}><Icon name="x" size={16} /></button>
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
      {r.gwt
        ? <div className="gwt-mini members" style={{ whiteSpace: "pre-wrap" }}>{r.gwt}</div>
        : <ul {...reqLinkProps(onOpenSpec)}>{(r.acc || []).map((a, i) => (
          <li key={i} dangerouslySetInnerHTML={{ __html: mdInline(a) }} />))}</ul>}
      <div className="lbl">{t("Where — Members in code")}</div>
      <div className="members">
        {r.members.length
          ? r.members.map((m, i) => <div className="member" key={i}><span className="role">{m.role}:</span> {m.loc}</div>)
          : r.layer === "need"
            ? <div className="member" style={{ color: "var(--fg-muted)" }}>(satisfied-by other requirements — no direct code)</div>
            : <div className="member" style={{ color: "var(--status-error)" }}>(no members found)</div>}
      </div>
      <div className="kv"><span className="k">{t("Depends on")}</span><span className="v">{r.deps.join(" · ") || "— (bus)"}</span></div>
      <div className="kv"><span className="k">{t("Used by")}</span><span className="v">{r.usedBy.join(" · ") || "—"}</span></div>
      {r.risks && r.risks.length > 0 && (<>
        <div className="lbl risk">{t("Risk — recommended action")}</div>
        {r.risks.map((rk, i) => <div className="members" key={i} style={{ marginTop: 4 }}>
          <b style={{ color: "var(--fg)" }}>{rk.signal}</b> — <span style={{ color: "var(--fg-muted)" }}>{rk.advice}</span></div>)}
      </>)}
      <div style={{ marginTop: 18 }}>
        <Btn variant="secondary" icon="file-text" onClick={() => onOpenSpec(r.id)}>{t("Open full spec")}</Btn>
      </div>
    </aside>
  );
}

export function ReqCodeView({ selId, setSelId, rows }) {
  return (
    <div style={{ padding: "18px 22px", overflow: "auto" }}>
      {rows.map((r) => (
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
