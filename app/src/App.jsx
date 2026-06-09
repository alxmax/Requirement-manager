/* App — shell: top bar, rail nav, search, theme toggle, view switching. */
import { useState, useEffect } from "react";
import { REQUIREMENTS, TODOS, REPO } from "./lib/data.js";
import { Icon, Logomark } from "./lib/icons.jsx";
import { Btn } from "./lib/ui.jsx";
import { MapView } from "./views/MapView.jsx";
import { ProblemsView, computeProblems } from "./views/ProblemsView.jsx";
import { SpecView } from "./views/SpecView.jsx";
import { RoadmapView } from "./views/RoadmapView.jsx";

const NAV = [
  { key:"map",     label:"Map",      icon:"network" },
  { key:"problems",label:"Problems", icon:"triangle-alert" },
  { key:"spec",    label:"Spec",     icon:"file-text" },
  { key:"roadmap", label:"Roadmap",  icon:"list-checks" },
];

function TopBar({ query, setQuery, theme, setTheme, onSearchPick }) {
  const q = query.trim().toLowerCase();
  const hits = q ? REQUIREMENTS.filter(r =>
    (r.id+" "+r.title+" "+r.intent+" "+r.contract.join(" ")).toLowerCase().includes(q)
  ).slice(0,8) : [];
  return (
    <header className="topbar">
      <div className="brand">
        <Logomark size={26} />
        <span className="wm">Requirement<b> Manager</b></span>
      </div>
      <span className="repo"><span className="dot" />{REPO || "local repo"}</span>
      <div className="spacer" />
      <div className="search">
        <span className="ico"><Icon name="search" size={15} /></span>
        <input className="search-inp" placeholder="Search id, title, contract…"
          value={query} onChange={e=>setQuery(e.target.value)} />
        {q && (
          <div className="search-res">
            {hits.length ? hits.map(h=>(
              <div className="search-hit" key={h.id} onMouseDown={()=>onSearchPick(h.id)}>
                <span className="hid">{h.id}</span>
                <span className="htitle">{h.title}</span>
              </div>
            )) : <div className="search-empty">no match</div>}
          </div>
        )}
      </div>
      <button className="btn-icon bare" title="toggle theme" onClick={()=>setTheme(theme==="light"?"dark":"light")}>
        <Icon name={theme==="light"?"moon":"sun"} size={17} />
      </button>
    </header>
  );
}

function Rail({ view, setView }) {
  const problems = computeProblems();
  const errCount = problems.filter(p=>p.sev==="ERROR").length;
  const todoCount = TODOS.filter(t => !t.done).length;
  const counts = { map:REQUIREMENTS.length, problems:problems.length, spec:REQUIREMENTS.length, roadmap:todoCount };

  // registry stats derived from whatever data is loaded
  const by = (pred) => REQUIREMENTS.filter(pred).length;
  const confirmed = by(r=>r.status==="confirmed");
  const inProgress = by(r=>r.status==="in-progress");
  const draft = by(r=>r.status==="draft");
  const orphan = by(r=>r.status!=="deprecated" && r.layer!=="need" && !r.members.some(m=>m.role==="implements"));
  const deprecated = by(r=>r.status==="deprecated");
  const bound = REQUIREMENTS.reduce((a,r)=>a+r.members.length,0);

  return (
    <nav className="rail">
      <div className="rail-section" style={{paddingTop:2}}>Workspace</div>
      {NAV.map(n=>(
        <div key={n.key} className={"nav-item"+(view===n.key?" active":"")} onClick={()=>setView(n.key)}>
          <Icon name={n.icon} size={17} className="ico" />
          {n.label}
          {n.key==="problems" && errCount>0
            ? <span className="count" style={{color:"#fff",background:"var(--coral-600)",borderRadius:"var(--radius-pill)",padding:"1px 7px"}}>{counts[n.key]}</span>
            : <span className="count">{counts[n.key]}</span>}
        </div>
      ))}
      <div className="rail-stat">
        <div className="rail-section" style={{paddingTop:0,paddingLeft:0}}>Registry</div>
        <div className="stat-row"><span className="sw" style={{background:"var(--status-confirmed)"}} />confirmed<span className="n">{confirmed}</span></div>
        <div className="stat-row"><span className="sw" style={{background:"var(--status-drift)"}} />in-progress<span className="n">{inProgress}</span></div>
        <div className="stat-row"><span className="sw" style={{background:"var(--status-draft)"}} />draft<span className="n">{draft}</span></div>
        <div className="stat-row"><span className="sw" style={{background:"var(--status-error)"}} />orphan<span className="n">{orphan}</span></div>
        <div className="stat-row"><span className="sw" style={{background:"var(--cov-exempt)"}} />deprecated<span className="n">{deprecated}</span></div>
        <div className="stat-row" style={{marginTop:6,borderTop:"1px solid var(--border-soft)",paddingTop:8}}>
          <Icon name="git-branch" size={14} className="ico" style={{color:"var(--fg-faint)"}} />
          <span style={{fontFamily:"var(--font-mono)",fontSize:11,color:"var(--fg-faint)"}}>{bound} members bound</span>
        </div>
      </div>
      <div style={{marginTop:8,paddingTop:8,borderTop:"1px solid var(--border-soft)",textAlign:"center"}}>
        <a
          href="https://github.com/alxmax/Requirement-manager"
          target="_blank"
          rel="noreferrer"
          style={{fontSize:10,color:"var(--fg-faint)",textDecoration:"none",
                  fontFamily:"var(--font-mono)",opacity:0.7}}
        >
          by requirement-manager
        </a>
      </div>
    </nav>
  );
}

export default function App() {
  const [view, setView] = useState("map");
  const [selId, setSelId] = useState("REQ-CHECK-006");
  const [highlightId, setHighlightId] = useState(null);
  const [query, setQuery] = useState("");
  const [theme, setTheme] = useState("light");

  useEffect(()=>{ document.documentElement.setAttribute("data-theme", theme); }, [theme]);

  function openSpec(id){ setSelId(id); setView("spec"); }
  function searchPick(id){ setSelId(id); setView("spec"); setQuery(""); }

  return (
    <div className="app">
      <TopBar query={query} setQuery={setQuery} theme={theme} setTheme={setTheme}
        onSearchPick={searchPick} />
      <div className="body">
        <Rail view={view} setView={setView} />
        {view==="map" && <MapView selId={selId} setSelId={setSelId} openSpec={openSpec}
          highlightId={highlightId} setHighlightId={setHighlightId} />}
        {view==="problems" && <ProblemsView openSpec={openSpec} />}
        {view==="spec" && <SpecView selId={selId} setSelId={setSelId} />}
        {view==="roadmap" && <RoadmapView openSpec={openSpec} />}
      </div>
    </div>
  );
}
