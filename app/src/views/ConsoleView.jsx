/* ConsoleView — the CLI surface. Command chips swap the rendered output. */
import { useState } from "react";

const CMDS = [
  { key:"next",  cmd:"req next" },
  { key:"check", cmd:"req check" },
  { key:"init",  cmd:"req init" },
  { key:"map",   cmd:"req map" },
];

const S = (cls, t) => <span className={cls}>{t}</span>;

function ConsoleOutput({ which }) {
  if (which === "next") return (
    <>
      <div>{S("prompt","$ ")}req next</div>
      <div>{S("bold","15 requirement(s)")} · 13 confirmed · 13 tested · {S("amb","1 draft(s)")}</div>
      <div>{" "}</div>
      <div>{S("red","Orphans")}</div>
      <div>{"  "}REQ-SYNC-014{"      "}{S("dim","add an implements: tag, or author the requirement")}</div>
      <div>{"               "}{S("dim","requirements/REQ-SYNC-014.md")}</div>
      <div>{" "}</div>
      <div>{S("amb","Drafts to review")}</div>
      <div>{"  "}DRAFT-cache-utils{" "}{S("amb","[REVIEW]")}{"  "}{S("dim","review intent, then promote")}</div>
      <div>{"               "}{S("dim","requirements/DRAFT-cache-utils.md")}</div>
      <div>{" "}</div>
      <div>{S("grn","✓")} everything else is in sync. {S("dim","· 2 blast-radius cautions hidden (run --all)")}</div>
      <div>{S("prompt","$ ")}{S("cursor","█")}</div>
    </>
  );
  if (which === "check") return (
    <>
      <div>{S("prompt","$ ")}req check</div>
      <div>{S("red","ERROR")}{"  "}REQ-SYNC-014 {"→"} no implementing member {S("dim","(orphan)  src/sync.py:88")}</div>
      <div>{S("amb","WARN")}{"   "}CORE-DRIFT-003 drift {"—"} re-check members {S("dim","scripts/reqmap.py:209-240")}</div>
      <div>{S("amb","WARN")}{"   "}3 open finding(s) {"—"} {S("dim","see requirements/_findings.md")}</div>
      <div>{S("dim","──────────────────────────────")}</div>
      <div>15 requirements · 41 members · {S("red","1 error")} · {S("amb","2 warnings")}</div>
      <div>{S("dim","exit 1 — the gate blocks the build")}</div>
      <div>{S("prompt","$ ")}{S("cursor","█")}</div>
    </>
  );
  if (which === "init") return (
    <>
      <div>{S("prompt","$ ")}req init</div>
      <div>{S("grn","✓")} created requirements/ and .reqmapignore</div>
      <div>{S("grn","✓")} drafted {S("bold","2")} requirement(s) from untagged code</div>
      <div>{S("grn","✓")} wrote drift lock {S("dim","(requirements/_reqlock.json)")}</div>
      <div>{S("grn","✓")} wrote requirements/_map.md + _map.json</div>
      <div>{" "}</div>
      <div>Next: run {S("acc","req next")} to see your worklist.</div>
      <div>{S("prompt","$ ")}{S("cursor","█")}</div>
    </>
  );
  return (
    <>
      <div>{S("prompt","$ ")}req map</div>
      <div>{S("grn","✓")} wrote requirements/_map.md{"   "}{S("dim","(4 mermaid blocks)")}</div>
      <div>{S("grn","✓")} wrote requirements/_map.json{"  "}{S("dim","(13 nodes · 16 edges)")}</div>
      <div>{" "}</div>
      <div>{S("dim","open the app to browse the map")}</div>
      <div>{S("prompt","$ ")}{S("cursor","█")}</div>
    </>
  );
}

export function ConsoleView() {
  const [which, setWhich] = useState("next");
  return (
    <div className="main">
      <div className="console">
        <div style={{display:"flex",alignItems:"baseline",gap:12,flexWrap:"wrap"}}>
          <h2 style={{font:"var(--text-h2)",margin:0,color:"var(--fg)"}}>Console</h2>
          <span style={{font:"var(--text-small)",color:"var(--fg-muted)"}}>the CLI surface — read-only commands are advice; <code style={{fontFamily:"var(--font-mono)",fontSize:12}}>check</code> is the gate.</span>
        </div>
        <div className="cmd-chips">
          {CMDS.map(c=>(
            <button key={c.key} className={"cmd-chip"+(which===c.key?" on":"")} onClick={()=>setWhich(c.key)}>{c.cmd}</button>
          ))}
        </div>
        <div className="term"><ConsoleOutput which={which} /></div>
      </div>
    </div>
  );
}
