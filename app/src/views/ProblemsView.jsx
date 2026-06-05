/* ProblemsView — a linter-style inbox of everything the gate + risk pass flags. */
import { useState } from "react";
import { REQUIREMENTS, coverageOf } from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";

/* derive a flat problem list from the registry (exported so App can count it) */
export function computeProblems() {
  const SEV = {
    unimplemented: { sev:"ERROR",  msg:"No implementing member — orphan. The gate blocks the build.", fix:"Add an `implements:` tag, or author the requirement." },
    drift:         { sev:"WARN",   msg:"Contract drift — lock hash no longer matches the code.", fix:"Re-check the named members, then run `req check --update-lock`." },
    untested:      { sev:"WARN",   msg:"Confirmed, but no `tested-by:` member is linked.", fix:"Add a test tag, or set `test_exempt:` to silence." },
    unreviewed:    { sev:"REVIEW", msg:"Drafted from code by extract — intent not yet validated.", fix:"Review, then `req promote <ID>`." },
  };
  const out = [];
  REQUIREMENTS.forEach(r => (r.risks||[]).forEach(rk => {
    const m = SEV[rk.signal]; if (!m) return;
    out.push({ id:r.id, title:r.title, signal:rk.signal, sev:m.sev, msg:m.msg, fix:m.fix,
      loc: (r.members[0] && r.members[0].loc) || (r.impl && r.impl[0]) || "" });
  }));
  // coverage-derived signals (computed from the clause↔acceptance mapping)
  REQUIREMENTS.forEach(r => {
    const cov = coverageOf(r);
    const flagged = (r.risks||[]).length > 0;
    if (cov === "partial") {
      out.push({ id:r.id, title:r.title, signal:"partial", sev:"WARN",
        msg:`Partial coverage — ${r.covered}/${r.clauses} clauses. ${r.gap||""}`.trim(),
        fix:"Add an acceptance test for the uncovered clause.",
        loc:(r.members.find(m=>m.role==="tested-by")||{}).loc || "" });
    } else if (cov === "untested" && r.status !== "draft" && !flagged) {
      out.push({ id:r.id, title:r.title, signal:"untested", sev:"WARN",
        msg:"Untested — no live acceptance test, or a `tested-by` range that no longer resolves (stale ref).",
        fix:"Add a test, repair the stale `tested-by` ref, or set `test_exempt:`.",
        loc:(r.members.find(m=>m.role==="tested-by")||{}).loc || "" });
    }
  });
  const order = { ERROR:0, WARN:1, REVIEW:2 };
  return out.sort((a,b)=> order[a.sev]-order[b.sev] || a.id.localeCompare(b.id));
}

export function ProblemsView({ openSpec }) {
  const [filter, setFilter] = useState("ALL");
  const all = computeProblems();
  const counts = all.reduce((a,p)=>{ a[p.sev]=(a[p.sev]||0)+1; return a; }, {});
  const shown = filter==="ALL" ? all : all.filter(p=>p.sev===filter);

  const Tab = ({k,label,n}) => (
    <button className={"tab"+(filter===k?" on":"")} onClick={()=>setFilter(k)}>
      {label}{n!=null && <span style={{marginLeft:6,opacity:.7,fontFamily:"var(--font-mono)",fontSize:11}}>{n}</span>}
    </button>
  );

  return (
    <div className="main">
      <div className="tabbar">
        <Tab k="ALL" label="All" n={all.length} />
        <Tab k="ERROR" label="Errors" n={counts.ERROR||0} />
        <Tab k="WARN" label="Warnings" n={counts.WARN||0} />
        <Tab k="REVIEW" label="Review" n={counts.REVIEW||0} />
        <div className="tab-legend">
          {(counts.ERROR||0) > 0
            ? <><Icon name="triangle-alert" size={14} style={{color:"var(--status-error)"}} /> gate blocks the build — {counts.ERROR} error</>
            : <><Icon name="shield-check" size={14} style={{color:"var(--status-confirmed)"}} /> gate passes</>}
        </div>
      </div>

      <div className="problems">
        {shown.map((p,i)=>(
          <div className="prob-row" key={i} onClick={()=>p.id!=="—" && openSpec(p.id)}>
            <span className={"prob-sev sev-"+p.sev}>{p.sev}</span>
            <div className="prob-body">
              <div className="prob-head">
                <span className="prob-id">{p.id}</span>
                <span className="prob-title">{p.title}</span>
              </div>
              <div className="prob-msg">{p.msg}</div>
              <div className="prob-fix"><Icon name="arrow-right" size={13} /> {p.fix}</div>
            </div>
            {p.loc && <span className="prob-loc">{p.loc}</span>}
          </div>
        ))}
        {shown.length===0 && (
          <div className="prob-empty">
            <Icon name="shield-check" size={22} style={{color:"var(--status-confirmed)"}} />
            <div>Nothing here — no <b>{filter.toLowerCase()}</b> signals open.</div>
          </div>
        )}
      </div>
    </div>
  );
}
