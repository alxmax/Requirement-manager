// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-945
/* App — shell: top bar, rail nav, search, theme toggle, view switching. */
import { useState, useEffect, Component } from "react";
import { REQUIREMENTS, TODOS, REPO, COMMANDS as CLI } from "./lib/data.js";
import { searchRequirements } from "./lib/search.js";
import { Icon, Logomark } from "./lib/icons.jsx";
import { Btn } from "./lib/ui.jsx";
import { useI18n, LOCALES } from "./lib/i18n.jsx";
import { MapView } from "./views/MapView.jsx";
import { ProblemsView, computeProblems, computeQuestions } from "./views/ProblemsView.jsx";
import { SpecView, ENFORCED } from "./views/SpecView.jsx";
import { RoadmapView } from "./views/RoadmapView.jsx";
import { ExplorerView } from "./views/ExplorerView.jsx";
import { CommandsView } from "./views/CommandsView.jsx";

/* `label` is the English source string, also the i18n dictionary key — see lib/i18n.jsx.
 * Explorer leads: at 685 requirements on three levels the outline is the only
 * surface that shows the whole registry. Map is kept but demoted — a 685-node
 * canvas is a picture of a haystack — and is scoped to the non-code levels. */
const NAV = [
  { key:"explorer",label:"Explorer", icon:"list-checks" },
  { key:"problems",label:"Problems", icon:"triangle-alert" },
  { key:"map",     label:"Map",      icon:"network" },
  { key:"spec",    label:"Spec",     icon:"file-text" },
  { key:"roadmap", label:"Roadmap",  icon:"list-checks" },
  { key:"commands",label:"Commands", icon:"terminal" },
];

/* Deep link: `#/req/<ID>` opens that requirement in the Explorer. Parsed and
 * written defensively — the viewer also runs from file:// and under SSR. */
const HASH_RE = /^#\/req\/([A-Za-z0-9][A-Za-z0-9_-]*)$/;
function readHashId() {
  try {
    const m = HASH_RE.exec(window.location.hash || "");
    return m ? m[1] : null;
  } catch { return null; }
}

function TopBar({ query, setQuery, theme, setTheme, onSearchPick }) {
  const { t, locale, setLocale } = useI18n();
  // The result list is tied to focus, not just to a non-empty query: left open
  // on blur it sat over the document until the field was cleared by hand.
  const [open, setOpen] = useState(false);
  const q = query.trim();
  // The same three layers as the engine `search` command (ARCH-SEARCH-036): the id
  // the query names, then a requirement whose text contains it verbatim — in any
  // language the map carries — then the shared TF-IDF ranking for everything else.
  const hits = q ? searchRequirements(REQUIREMENTS, q, { top: 8 }) : [];
  return (
    <header className="topbar">
      <div className="brand">
        <Logomark size={26} />
        <span className="wm">Requirement<b> Manager</b></span>
      </div>
      <span className="repo"><span className="dot" />{REPO || t("local repo")}</span>
      <div className="spacer" />
      <div className="search">
        <span className="ico"><Icon name="search" size={15} /></span>
        <input className="search-inp" placeholder={t("Search id, title, contract…")}
          value={query} onChange={e=>setQuery(e.target.value)}
          onFocus={()=>setOpen(true)}
          /* mousedown on a hit fires before blur, so picking still works */
          onBlur={()=>setOpen(false)}
          onKeyDown={e=>{ if (e.key === "Escape") { setQuery(""); e.currentTarget.blur(); } }} />
        {q && open && (
          <div className="search-res">
            {hits.length ? hits.map(h=>(
              <div className="search-hit" key={h.req.id} onMouseDown={()=>onSearchPick(h.req.id)}>
                <span className="hid">{h.req.id}</span>
                <span className="htitle">{h.req.title}</span>
                <span className="hscore">
                  {h.kind === "score" ? h.score.toFixed(2) : h.kind}
                </span>
              </div>
            )) : <div className="search-empty">{t("no strong match")}</div>}
          </div>
        )}
      </div>
      <button className="btn-icon bare" title={t("switch language")} aria-label={t("switch language")}
        onClick={()=>setLocale(LOCALES[(LOCALES.findIndex(l=>l.code===locale)+1) % LOCALES.length].code)}
        style={{fontFamily:"var(--font-mono)",fontSize:11,fontWeight:600,letterSpacing:".04em",width:34}}>
        {(LOCALES.find(l=>l.code===locale) || LOCALES[0]).label}
      </button>
      <button className="btn-icon bare" title={t("toggle theme")} onClick={()=>setTheme(theme==="light"?"dark":"light")}>
        <Icon name={theme==="light"?"moon":"sun"} size={17} />
      </button>
    </header>
  );
}

function Rail({ view, setView, focus, setFocus }) {
  const { t } = useI18n();
  const problems = computeProblems();
  const errCount = problems.filter(p=>p.sev==="ERROR").length;
  const todoCount = TODOS.filter(t => !t.done).length;
  // An author's open questions live in Problems since v4.0.0 (ADR-0028) but keep
  // their own badge: a computed warning and a human writing down what they do not
  // know are different news. `0` is not news at all, so the badge hides at zero.
  const questionCount = computeQuestions().length;
  const counts = {
    explorer: REQUIREMENTS.length,
    map: REQUIREMENTS.filter(r=>r.level!=="code").length,
    problems: problems.length,
    spec: REQUIREMENTS.length,
    roadmap: todoCount,
    commands: CLI.length || null,
  };

  // registry stats derived from whatever data is loaded
  const by = (pred) => REQUIREMENTS.filter(pred).length;
  const confirmed = by(r=>r.status==="confirmed");
  const inProgress = by(r=>r.status==="in-progress");
  const draft = by(r=>r.status==="draft");
  // Orphan = the gate's ERROR condition, so it must use the gate's scope: an
  // ENFORCED requirement with no `implements:` member. Counting drafts here
  // reported 618 orphans against a gate that reports 0 errors.
  const orphan = by(r=>ENFORCED[r.status] && r.layer!=="need" && r.layer!=="aggregate" && !r.members.some(m=>m.role==="implements"));
  const deprecated = by(r=>r.status==="deprecated");
  const bound = REQUIREMENTS.reduce((a,r)=>a+r.members.length,0);

  return (
    <nav className="rail">
      <div className="rail-section" style={{paddingTop:2}}>{t("Workspace")}</div>
      {NAV.map(n=>(
        <div key={n.key} className={"nav-item"+(view===n.key?" active":"")} onClick={()=>setView(n.key)}>
          <Icon name={n.icon} size={17} className="ico" />
          {t(n.label)}
          {/* A solid white-on-red badge fell to ~2.8:1 once the dark theme
              brightened the reds; the tinted pair is readable in both. */}
          {n.key==="problems" && errCount>0
            ? <span className="count" style={{color:"var(--status-error)",background:"var(--status-error-bg)",borderRadius:"var(--radius-pill)",padding:"1px 8px",fontWeight:600}}>{counts[n.key]}</span>
            : n.key==="problems" && questionCount > 0
              ? <span className="count" style={{color:"var(--status-drift)",background:"var(--status-drift-bg)",borderRadius:"var(--radius-pill)",padding:"1px 8px",fontWeight:600}}>{counts[n.key]}</span>
              : <span className="count">{counts[n.key]}</span>}
        </div>
      ))}
      {/* The registry tally was five numbers you could read but not act on.
          Each row is now the filter it describes: it opens the Explorer scoped to
          that slice, and clicking the active row again clears the scope. */}
      <div className="rail-stat">
        <div className="rail-section" style={{paddingTop:0,paddingLeft:0}}>{t("Registry")}</div>
        {[
          { key:"confirmed",   n:confirmed,  color:"var(--status-confirmed)" },
          { key:"in-progress", n:inProgress, color:"var(--status-drift)" },
          { key:"draft",       n:draft,      color:"var(--status-draft)" },
          { key:"orphan",      n:orphan,     color:"var(--status-error)" },
          { key:"deprecated",  n:deprecated, color:"var(--cov-exempt)" },
        ].map(s=>(
          <button type="button" key={s.key} className={"stat-row"+(focus===s.key?" on":"")}
            aria-pressed={focus===s.key}
            title={s.key==="orphan"
              ? "enforced requirements with no implements: member \u2014 the gate's error condition"
              : "show only "+s.key+" requirements"}
            onClick={()=>setFocus(focus===s.key ? null : s.key)}>
            <span className="sw" style={{background:s.color}} />{s.key}<span className="n">{s.n}</span>
          </button>
        ))}
        <div className="stat-row" style={{marginTop:6,borderTop:"1px solid var(--border-soft)",paddingTop:8}}>
          <Icon name="git-branch" size={14} className="ico" style={{color:"var(--fg-faint)"}} />
          <span style={{fontFamily:"var(--font-mono)",fontSize:11,color:"var(--fg-faint)"}}>{t("{n} members bound", { n: bound })}</span>
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

/* Keeps a render throw in one view from blanking the whole self-contained
 * viewer; keyed by `view` so switching tabs resets it. */
class ErrorBoundary extends Component {
  constructor(props){ super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error){ return { error }; }
  render(){
    if (this.state.error) {
      return (
        <div className="view" style={{padding:24}}>
          <h2>Something went wrong rendering this view.</h2>
          <pre style={{whiteSpace:"pre-wrap",color:"var(--fg-faint)",fontSize:12}}>{String(this.state.error)}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [view, setView] = useState("explorer");
  const [selId, setSelId] = useState(() => readHashId() || "ARCH-CHECK-006");
  const [highlightId, setHighlightId] = useState(null);
  const [query, setQuery] = useState("");
  const [theme, setTheme] = useState("light");
  // Which registry slice the Explorer is scoped to, driven from the rail tally.
  const [focus, setFocus] = useState(null);

  useEffect(()=>{ document.documentElement.setAttribute("data-theme", theme); }, [theme]);

  // `#/req/<ID>` is the shareable address of one requirement. Following it (on
  // load or on a later hashchange) opens the Explorer, which then expands the
  // ancestor chain and scrolls the row into view.
  useEffect(()=>{
    const apply = () => { const id = readHashId(); if (id) { setSelId(id); setView("explorer"); } };
    apply();
    try { window.addEventListener("hashchange", apply); } catch { return undefined; }
    return () => { try { window.removeEventListener("hashchange", apply); } catch { /* SSR */ } };
  }, []);

  // Keep the address bar in step with the selection, without a history entry
  // per click — the back button should leave the viewer, not replay a tree walk.
  useEffect(()=>{
    if (!selId) return;
    try {
      const next = "#/req/" + selId;
      if (window.location.hash !== next)
        window.history.replaceState(null, "", window.location.pathname + window.location.search + next);
    } catch { /* file:// or SSR — the deep link is a convenience, never required */ }
  }, [selId]);

  function openSpec(id){ setSelId(id); setView("explorer"); }
  function searchPick(id){ setSelId(id); setView("explorer"); setQuery(""); }

  return (
    <div className="app">
      <TopBar query={query} setQuery={setQuery} theme={theme} setTheme={setTheme}
        onSearchPick={searchPick} />
      <div className="body">
        <Rail view={view} setView={setView} focus={focus}
          setFocus={(k)=>{ setFocus(k); setView("explorer"); }} />
        <ErrorBoundary key={view}>
          {view==="explorer" && <ExplorerView selId={selId} setSelId={setSelId}
            focus={focus} clearFocus={()=>setFocus(null)} />}
          {view==="map" && <MapView selId={selId} setSelId={setSelId} openSpec={openSpec}
            highlightId={highlightId} setHighlightId={setHighlightId} />}
          {view==="problems" && <ProblemsView openSpec={openSpec} />}
          {view==="spec" && <SpecView selId={selId} setSelId={setSelId} />}
          {view==="roadmap" && <RoadmapView openSpec={openSpec} />}
          {view==="commands" && <CommandsView />}
        </ErrorBoundary>
      </div>
    </div>
  );
}
