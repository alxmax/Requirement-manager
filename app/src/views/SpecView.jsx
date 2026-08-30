/* SpecView — a rendered requirement document (frontmatter → WHY → WHAT → HOW → WHERE). */
import { Fragment } from "react";
import { REQUIREMENTS, REQ_BY_ID, coverageDetail, exemptReason } from "../lib/data.js";
import { Pill, statusKind } from "../lib/ui.jsx";
import { useI18n, translatedText } from "../lib/i18n.jsx";

// A cached translation is opt-in and unreviewed — this badge is the one thing
// standing between "machine text" and "looks like the author wrote it".
// Never render translated content without it (see i18n.jsx's module comment).
function TranslatedBadge() {
  return (
    <span className="i18n-badge" title="Machine-translated by `reqmap.py translate`; not reviewed by the author — the source .md is the artifact of record.">
      machine-translated, unreviewed
    </span>
  );
}

// HTML-escape before the backtick→<code> transform: the output feeds
// dangerouslySetInnerHTML with untrusted requirement text from _map.json.
function mdInlineSpec(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/`([^`]+)`/g,'<code>$1</code>'); }

// The coverage strip shows a fraction ONLY when the engine measured one (the
// requirement labels its criteria and at least one carries a `# verifies:` tag).
// No measurement, no number: the badge alone. A count nobody computed reads as
// authoritative and sends its owner hunting for tests that already exist.
// The `created`/`updated` dates that used to sit here were derived from the
// LENGTH OF THE ID and printed beside the `git log` command that would have
// produced them — removed outright rather than faked more convincingly.
function CovStrip({ r }) {
  const { state, measured, clauses, covered, gap } = coverageDetail(r);
  const segs = [];
  if (measured) for (let i=0;i<clauses;i++) segs.push(i < covered ? "on" : (state==="partial" ? "gap" : "off"));
  let label;
  if (state === "exempt") label = exemptReason(r);
  else if (measured) label = covered+" / "+clauses+" criteria verified";
  else if (state === "tested") label = "acceptance test linked · no per-criterion tags";
  else label = "no acceptance test linked";
  return (
    <div className="cov-strip">
      <div className="cov-row">
        <span className={"cov-badge cov-"+state}><span className="cd" />{state}</span>
        <span className="cov-count">{label}</span>
        {measured && <div className="cov-bar">{segs.map((s,i)=><span key={i} className={"cseg "+s} />)}</div>}
      </div>
      {gap && state==="partial" && <div className="cov-gap">gap · {gap}</div>}
    </div>
  );
}

const PRIORITY_COLOR = {
  "must-have":    { bg: "#F38BA8", color: "#5c0011" },
  "should-have":  { bg: "#F9E2AF", color: "#5c3d00" },
  "could-have":   { bg: "#A6E3A1", color: "#1a4d17" },
  "wont-have":    { bg: "#BAC2DE", color: "#3b3f5c" },
};

function PriorityBadge({ priority }) {
  const c = PRIORITY_COLOR[priority];
  if (!c) return null;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      font: "var(--text-caption)", fontWeight: 600,
      padding: "4px 10px", borderRadius: "var(--radius-pill)",
      background: c.bg, color: c.color,
      border: "1px solid transparent", whiteSpace: "nowrap",
    }}>{priority}</span>
  );
}

function SpecDoc({ r, onNav }) {
  const { t, locale } = useI18n();
  if (!r) return null;
  const title = translatedText(r, locale, "title", r.title);
  const intent = translatedText(r, locale, "intent", r.intent);
  const contract = translatedText(r, locale, "contract");
  const acceptance = translatedText(r, locale, "acceptance");
  return (
    <div className="spec">
      <div className="spec-sheet">
      <div className="spec-fm">
        <span className="fk">id:</span><span>{r.id}</span>
        <span className="fk">status:</span><span>{r.status}</span>
        <span className="fk">layer:</span><span>{r.layer}</span>
        <span className="fk">owner:</span><span>Alex</span>
        <span className="fk">depends_on:</span><span>[{r.deps.length ? r.deps.map((d,i)=>(
          <Fragment key={d}>{i>0 ? ", " : ""}<button className="dep-link" onClick={()=>onNav && onNav(d)}>{d}</button></Fragment>
        )) : ""}]</span>
      </div>

      <div className="head-row">
        <Pill kind={statusKind(r.status)}>{r.status}</Pill>
        <Pill kind={r.layer}>{r.layer}</Pill>
        {r.priority && <PriorityBadge priority={r.priority} />}
      </div>
      <h1>{title.text}{title.isTranslated && <TranslatedBadge />}</h1>
      <div className="sec why-sec">
        <div className="eyebrow">{t("Why — Intent")} <span>{r.layer === "bus" ? "foundation" : "feature"}{intent.isTranslated && <TranslatedBadge />}</span></div>
        <p className="blockquote">{intent.text}</p>
      </div>
      <CovStrip r={r} />

      <div className="sec">
        <div className="eyebrow">{t("What — Contract")} <span className="rule" /> {t("normative")}{contract.isTranslated && <TranslatedBadge />}</div>
        {contract.isTranslated
          ? <div className="gwt">{contract.text.split("\n").map((ln,i)=><div key={i} dangerouslySetInnerHTML={{__html: mdInlineSpec(ln)}} />)}</div>
          : <ul>{r.contract.map((c,i)=><li key={i} dangerouslySetInnerHTML={{__html: mdInlineSpec(c)}} />)}</ul>}
      </div>

      <div className="sec">
        <div className="eyebrow">{t("How — Acceptance")} <span className="rule" /> {t("= tests")}{acceptance.isTranslated && <TranslatedBadge />}</div>
        {acceptance.isTranslated
          ? <div className="gwt">{acceptance.text.split("\n").map((ln,i)=><div key={i}>{ln}</div>)}</div>
          : (r.gwt
            ? <div className="gwt">{r.gwt.split("\n").map((ln,i)=>(
                <div key={i}>{ln}</div>))}</div>
            : <ul>{(r.acc||[]).map((a,i)=><li key={i} dangerouslySetInnerHTML={{__html: mdInlineSpec(a)}} />)}</ul>)}
      </div>

      <div className="sec">
        <div className="eyebrow">{t("Where — Members in code")}</div>
        <div className="members-box">
          {r.members.length
            ? r.members.map((m,i)=><div className="member" key={i}><span className="role">{m.role}:</span> {m.loc}</div>)
            : (r.layer === "need" || r.layer === "aggregate")
              ? <div className="member" style={{color:"var(--fg-muted)"}}>{t("(satisfied-by other requirements — no direct code)")}</div>
              : <div className="member" style={{color:"var(--status-error)"}}>{t("(no members found — orphan)")}</div>}
        </div>
      </div>

      {r.risks && r.risks.length>0 && (
        <div className="sec">
          <div className="eyebrow warn">{t("Risk — recommended action")}</div>
          {r.risks.map((rk,i)=>(
            <div className="member" key={i} style={{font:"var(--text-body)",color:"var(--fg-secondary)"}}>
              <b style={{color:"var(--fg)"}}>{rk.signal}</b> — {rk.advice}</div>
          ))}
        </div>
      )}
      </div>
    </div>
  );
}

export function SpecView({ selId, setSelId }) {
  const cur = selId && REQ_BY_ID[selId] ? selId : "CORE-PARSE-001";
  const r = REQ_BY_ID[cur] || REQUIREMENTS[0];
  const core = REQUIREMENTS.filter(x=>x.area==="CORE");
  const req = REQUIREMENTS.filter(x=>x.area!=="CORE");
  const statusColor = (s) => s==="in-progress" ? "var(--status-drift)"
    : s==="draft" ? "var(--status-draft)"
    : s==="deprecated" ? "var(--fg-faint)"
    : s==="confirmed" ? "transparent" : "var(--status-draft)";
  const statusTint = (s) => s==="in-progress" ? "var(--status-drift-bg)"
    : s==="draft" ? "var(--status-draft-bg)"
    : "transparent";
  const Item = ({x}) => {
    const on = cur===x.id;
    const sc = statusColor(x.status);
    return (
    <button onClick={()=>setSelId(x.id)} title={x.status} style={{
      display:"flex",gap:9,alignItems:"flex-start",textAlign:"left",
      padding:"7px 10px 7px 9px",border:"none",
      borderLeft:`3px solid ${on ? "var(--accent)" : (sc==="transparent" ? "transparent" : sc)}`,
      borderRadius:"0 var(--radius-1) var(--radius-1) 0",cursor:"pointer",width:"100%",marginBottom:"3px",
      background: on ? "var(--accent-soft)" : statusTint(x.status),
      color: on ? "var(--accent)" : "var(--fg-secondary)" }}>
      <span style={{width:7,height:7,borderRadius:"999px",background:sc,flex:"none",marginTop:5}} />
      <span style={{display:"flex",flexDirection:"column",gap:2,minWidth:0}}>
        <span style={{font:"var(--text-id)",color:"inherit"}}>{x.id}</span>
        <span style={{font:"var(--text-small)",color: on ? "var(--accent)" : "var(--fg-muted)",fontSize:12}}>{x.title}</span>
      </span>
    </button>
    );
  };
  return (
    <div className="main" style={{display:"grid",gridTemplateColumns:"220px 1fr",minHeight:0}}>
      <div style={{borderRight:"1px solid var(--border)",background:"var(--bg-raised)",overflow:"auto",padding:"14px 10px"}}>
        <div className="rail-section" style={{paddingTop:0}}>CORE · bus</div>
        {core.map(x=><Item key={x.id} x={x} />)}
        <div className="rail-section">REQ · features</div>
        {req.map(x=><Item key={x.id} x={x} />)}
      </div>
      <div style={{overflow:"auto"}}><SpecDoc r={r} onNav={setSelId} /></div>
    </div>
  );
}
