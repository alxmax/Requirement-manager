/* MapView — the flagship interactive graph explorer (4 tabs + detail panel). */
import { useState } from "react";
import { REQUIREMENTS, REQ_BY_ID, coverageOf } from "../lib/data.js";
import { Pill, Btn, statusKind } from "../lib/ui.jsx";
import { Icon, LocateGlyph } from "../lib/icons.jsx";

/* hand-tuned layouts per tab — {id:[x,y]} top-left coords on the canvas */
const NW = 152, NH = 50;
const SYS_POS = {
  "CORE-PARSE-001":[60,60], "CORE-SCAN-002":[60,184], "CORE-DRIFT-003":[60,308],
  "REQ-CHECK-006":[316,40], "REQ-EXTRACT-008":[316,150], "REQ-MAP-007":[316,260],
  "REQ-CANDIDATES-009":[316,370], "REQ-FINDINGS-010":[316,480],
  "REQ-NEW-004":[560,40], "REQ-PROMOTE-011":[560,150], "REQ-SCAN-005":[560,260],
  "REQ-INIT-012":[560,370], "REQ-NEXT-013":[560,480],
  "DRAFT-cache-utils":[812,150], "REQ-SYNC-014":[812,40],
};
const RISK_POS = {
  "CORE-PARSE-001":[80,70],"CORE-SCAN-002":[80,210],"CORE-DRIFT-003":[80,350],
  "REQ-SYNC-014":[440,110],"DRAFT-cache-utils":[440,290],
};

function center(pos, id){ const p = pos[id]; return p ? [p[0]+NW/2, p[1]+NH/2] : [0,0]; }

function NodeBox({ r, pos, selected, highlighted, riskClass, onClick }) {
  const p = pos[r.id]; if (!p) return null;
  const cov = coverageOf(r);
  const covCls = !riskClass && (cov==="partial" ? "cov-partial" : cov==="untested" ? "cov-untested" : "");
  const cls = ["node",
    r.layer === "bus" ? "bus" : "",
    covCls || "",
    selected ? "sel" : "",
    highlighted ? "hl" : "",
    riskClass || ""].join(" ");
  return (
    <div className={cls} style={{ left:p[0], top:p[1], width:NW }} onClick={()=>onClick(r.id)}>
      <span className="nt">{r.title}</span>
      <span className="ni">{r.id}</span>
    </div>
  );
}

function Edges({ pos, edges }) {
  return (
    <svg className="svg-edges">
      <defs>
        <marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="var(--ink-2)" />
        </marker>
      </defs>
      {edges.map(([a,b],i)=>{
        const [x1,y1]=center(pos,a), [x2,y2]=center(pos,b);
        if(!x1||!x2) return null;
        const mx=(x1+x2)/2;
        return <path key={i} d={`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2-8},${y2}`}
          fill="none" stroke="var(--ink-2)" strokeWidth="1.6" markerEnd="url(#arrow)" opacity="0.7" />;
      })}
    </svg>
  );
}

/* tiny inline-markdown: `code` → <code> */
function mdInline(s){
  return String(s).replace(/`([^`]+)`/g, '<code>$1</code>');
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
      <ul>{r.contract.map((c,i)=><li key={i} dangerouslySetInnerHTML={{__html: mdInline(c)}} />)}</ul>

      <div className="lbl">How — Acceptance</div>
      {r.gwt
        ? <div className="gwt-mini members" style={{whiteSpace:"pre-wrap"}}>{r.gwt}</div>
        : <ul>{(r.acc||[]).map((a,i)=><li key={i} dangerouslySetInnerHTML={{__html: mdInline(a)}} />)}</ul>}

      <div className="lbl">Where — Members in code</div>
      <div className="members">
        {r.members.length
          ? r.members.map((m,i)=><div className="member" key={i}><span className="role">{m.role}:</span> {m.loc}</div>)
          : <div className="member" style={{color:"var(--status-error)"}}>(no members found)</div>}
      </div>

      <div className="kv"><span className="k">Depends on</span><span className="v">{r.deps.join(" · ") || "— (bus)"}</span></div>
      <div className="kv"><span className="k">Used by</span><span className="v">{r.usedBy.join(" · ") || "—"}</span></div>

      {r.risks && r.risks.length>0 && (<>
        <div className="lbl risk">Risk — recommended action</div>
        {r.risks.map((rk,i)=><div className="members" key={i} style={{marginTop:4}}>
          <b style={{color:"var(--fg)"}}>{rk.signal}</b> — <span style={{color:"var(--fg-muted)"}}>{rk.advice}</span></div>)}
      </>)}

      <div style={{marginTop:18}}>
        <Btn variant="secondary" icon="file-text" onClick={()=>onOpenSpec(r.id)}>Open full spec</Btn>
      </div>
    </aside>
  );
}

const MAP_TABS = [
  { key:"system", label:"System Map" },
  { key:"reqcode", label:"Req→Code" },
  { key:"deps", label:"Dependencies" },
  { key:"risk", label:"Risk" },
];

export function MapView({ selId, setSelId, openSpec, highlightId, setHighlightId }) {
  const [tab, setTab] = useState("system");
  const sel = selId ? REQ_BY_ID[selId] : null;

  // every real depends_on edge between two positioned System-Map nodes
  const sysEdges = REQUIREMENTS
    .flatMap(r => (r.deps || []).map(d => [r.id, d]))
    .filter(([a, b]) => SYS_POS[a] && SYS_POS[b]);

  const legend = {
    system: <><span className="pdot" style={{width:9,height:9,borderRadius:0,border:"3px solid var(--ink-0)",display:"inline-block"}} /> bus · arrows = depends_on</>,
    reqcode: <>requirement → its code · <span style={{color:"var(--accent)"}}>implements</span> / tested-by</>,
    deps: <>area-level coupling · arrow A→B = A depends on B</>,
    risk: <>only requirements with ≥1 open risk signal</>,
  }[tab];

  function locate(){ if(selId){ setHighlightId(selId); setTimeout(()=>setHighlightId(null), 2200);} }

  return (
    <div className="main">
      <div className="tabbar">
        {MAP_TABS.map(t=>(
          <button key={t.key} className={"tab" + (tab===t.key?" on":"")} onClick={()=>setTab(t.key)}>{t.label}</button>
        ))}
        <div className="tab-legend">{legend}</div>
      </div>

      <div className={"map-wrap" + (sel ? " with-panel" : "")}>
        {tab==="system" && (
          <div className="canvas">
            <div className="canvas-inner" style={{width:1000, height:600}}>
            <div className="subgraph-label" style={{left:60,top:30}}>CORE · bus</div>
            <div className="subgraph-label" style={{left:316,top:12}}>REQ · features</div>
            <Edges pos={SYS_POS} edges={sysEdges} />
            {REQUIREMENTS.filter(r=>SYS_POS[r.id]).map(r=>(
              <NodeBox key={r.id} r={r} pos={SYS_POS} selected={selId===r.id}
                highlighted={highlightId===r.id} onClick={setSelId} />
            ))}
            </div>
          </div>
        )}

        {tab==="reqcode" && <ReqCodeView selId={selId} setSelId={setSelId} />}

        {tab==="deps" && (
          <div className="canvas">
            <div className="canvas-inner" style={{height:480, width:760}}>
            <Edges pos={{CORE:[120,210],REQ:[520,210]}} edges={[["REQ","CORE"]]} />
            <div className="node bus" style={{left:120,top:210,width:NW}}><span className="nt">CORE</span><span className="ni">3 caps</span></div>
            <div className="node" style={{left:520,top:210,width:NW}}><span className="nt">REQ</span><span className="ni">12 caps</span></div>
            </div>
          </div>
        )}

        {tab==="risk" && (
          <div className="canvas">
            <div className="canvas-inner" style={{minHeight:520, width:760}}>
            {REQUIREMENTS.filter(r=>RISK_POS[r.id]).map(r=>{
              const sig = r.risks[0]?.signal;
              const rc = sig==="unimplemented" ? "risk-error" : (sig==="drift"||sig==="blast-radius"||sig==="unreviewed") ? "risk-blast" : "";
              return <NodeBox key={r.id} r={r} pos={RISK_POS} selected={selId===r.id}
                highlighted={highlightId===r.id} riskClass={rc} onClick={setSelId} />;
            })}
            <div className="subgraph-label" style={{left:80,top:470,maxWidth:560,textTransform:"none",letterSpacing:0,color:"var(--fg-muted)",font:"var(--text-small)"}}>
              2 blast-radius · 1 drift · 1 unreviewed draft · 1 orphan (ERROR)
            </div>
            </div>
          </div>
        )}

        {sel && <DetailPanel r={sel} onClose={()=>setSelId(null)} onLocate={locate} onOpenSpec={openSpec} />}
      </div>
    </div>
  );
}

function ReqCodeView({ selId, setSelId }) {
  return (
    <div style={{padding:"18px 22px", overflow:"auto"}}>
      {REQUIREMENTS.filter(r=>!r.id.startsWith("DRAFT")).map(r=>(
        <div key={r.id} onClick={()=>setSelId(r.id)} style={{
          display:"grid", gridTemplateColumns:"240px 1fr", gap:18, padding:"11px 12px",
          borderBottom:"1px solid var(--border-soft)", cursor:"pointer",
          background: selId===r.id ? "var(--surface)" : "transparent" }}>
          <div style={{display:"flex",flexDirection:"column",gap:3}}>
            <span style={{font:"var(--text-id)"}}>{r.id}</span>
            <span style={{font:"var(--text-small)",color:"var(--fg-muted)"}}>{r.title}</span>
          </div>
          <div style={{display:"flex",flexDirection:"column",gap:2,justifyContent:"center"}}>
            {r.members.length ? r.members.map((m,i)=>(
              <div key={i} style={{font:"var(--text-code)",color:"var(--fg-muted)"}}>
                <span style={{color:m.role==="implements"?"var(--accent)":"var(--fg-muted)"}}>{m.role}:</span> {m.loc}
              </div>
            )) : <div style={{font:"var(--text-code)",color:"var(--status-error)"}}>(no members — orphan, gate ERROR)</div>}
          </div>
        </div>
      ))}
    </div>
  );
}
