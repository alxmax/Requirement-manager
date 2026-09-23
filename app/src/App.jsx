// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-1082
import { useState, useEffect, useMemo, Component } from "react";
import { REQUIREMENTS } from "./lib/data.js";
import { MapView } from "./views/MapView.jsx";
import { ProblemsView, computeProblems } from "./views/ProblemsView.jsx";
import { RoadmapView } from "./views/RoadmapView.jsx";
import { ExplorerView } from "./views/ExplorerView.jsx";
import { CommandsView } from "./views/CommandsView.jsx";
import { TopBar } from "./components/TopBar.jsx";
import { Rail } from "./components/Rail.jsx";

const HASH_RE = /^#\/req\/([A-Za-z0-9][A-Za-z0-9_-]*)$/;
function readHashId() {
  try {
    const m = HASH_RE.exec(window.location.hash || "");
    return m ? m[1] : null;
  } catch { return null; }
}

class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) {
      return (
        <div className="view" style={{ padding: 24 }}>
          <h2>Something went wrong rendering this view.</h2>
          <pre style={{
            whiteSpace: "pre-wrap", color: "var(--fg-faint)", fontSize: 12,
          }}>
            {String(this.state.error)}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

/** A registry tally row's click: scope the outline to that slice and show
 * the outline, whatever surface was open. The row itself toggles the key
 * (the same row again passes null), so this only routes it.
 * implements: REQ-VIEWER-1082 */
export const openScope = (setFocus, setView) => (key) => {
  setFocus(key);
  setView("explorer");
};

/** A rail reading's click: open Problems on the tab listing the rows
 * behind that number.
 * implements: REQ-VIEWER-1084 */
export const openTab = (setTab, setView) => (tab) => {
  setTab(tab);
  setView("problems");
};

export default function App() {
  const [view, setView] = useState("explorer");
  const [selId, setSelId] = useState(() => readHashId() || "ARCH-CHECK-006");
  const [highlightId, setHighlightId] = useState(null);
  const [query, setQuery] = useState("");
  const [theme, setTheme] = useState("light");
  const [focus, setFocus] = useState(null);
  const [probTab, setProbTab] = useState(null);
  const problems = useMemo(() => computeProblems(), [REQUIREMENTS]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    const apply = () => {
      const id = readHashId();
      if (id) { setSelId(id); setView("explorer"); }
    };
    apply();
    try {
      window.addEventListener("hashchange", apply);
    } catch { return undefined; }
    return () => {
      try {
        window.removeEventListener("hashchange", apply);
      } catch { /* SSR */ }
    };
  }, []);

  useEffect(() => {
    if (!selId) return;
    try {
      const next = "#/req/" + selId;
      const { hash, pathname, search } = window.location;
      if (hash !== next) {
        window.history.replaceState(null, "", pathname + search + next);
      }
    } catch { /* file:// or SSR */ }
  }, [selId]);

  function openSpec(id) { setSelId(id); setView("explorer"); }
  function searchPick(id) { setSelId(id); setView("explorer"); setQuery(""); }

  return (
    <div className="app">
      <TopBar query={query} setQuery={setQuery} theme={theme}
              setTheme={setTheme} onSearchPick={searchPick} />
      <div className="body">
        <Rail view={view} focus={focus} problems={problems}
          setView={(v) => { setProbTab(null); setView(v); }}
          setFocus={openScope(setFocus, setView)}
          openProblems={openTab(setProbTab, setView)} />
        <ErrorBoundary key={view + (probTab || "")}>
          {view === "explorer" && (
            <ExplorerView selId={selId} setSelId={setSelId} focus={focus}
                          clearFocus={() => setFocus(null)} />
          )}
          {view === "map" && (
            <MapView selId={selId} setSelId={setSelId} openSpec={openSpec}
                     highlightId={highlightId}
                     setHighlightId={setHighlightId} />
          )}
          {view === "problems" && (
            <ProblemsView openSpec={openSpec} problems={problems}
                          initialFilter={probTab || "ALL"} />
          )}
          {view === "roadmap" && <RoadmapView openSpec={openSpec} />}
          {view === "commands" && <CommandsView />}
        </ErrorBoundary>
      </div>
    </div>
  );
}
