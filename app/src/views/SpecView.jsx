// implements: ARCH-VIEWER-007
// implements: ARCH-TRANSLATE-044
// implements: REQ-VIEWER-944
/* SpecView — a rendered requirement document (frontmatter → WHY → WHAT → HOW → WHERE). */
import { Fragment } from "react";
import { REQUIREMENTS, REQ_BY_ID, coverageDetail, exemptReason } from "../lib/data.js";
import { Pill, statusKind, mdInline, reqLinkProps } from "../lib/ui.jsx";
import { openQuestions } from "../lib/tree.js";
import { useI18n, translatedText } from "../lib/i18n.jsx";

// A cached translation is opt-in and unreviewed — this badge is the one thing
// standing between "machine text" and "looks like the author wrote it".
// Never render translated content without it (see i18n.jsx's module comment).
function TranslatedBadge() {  // implements: REQ-TRANSLATE-938
  return (
    <span className="i18n-badge" title="Machine-translated by `reqmap.py translate`; not reviewed by the author — the source .md is the artifact of record.">
      machine-translated, unreviewed
    </span>
  );
}

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

/* The statuses at which the gate enforces the implements-tag rule. Anything
 * else (draft, deprecated) is tracked, not enforced — see the gate's link-sync
 * check. Kept here rather than inlined so the two readers of it agree. */
export const ENFORCED = { confirmed: true, "in-progress": true, implemented: true };

const PRIORITY_COLOR = {
  "must-have":    { bg: "var(--status-error-bg)",  color: "var(--status-error)" },
  "should-have":  { bg: "var(--status-drift-bg)",  color: "var(--status-drift)" },
  "could-have":   { bg: "var(--cov-tested-bg)",    color: "var(--cov-tested)" },
  "wont-have":    { bg: "var(--status-draft-bg)",  color: "var(--fg-muted)" },
};

function PriorityBadge({ priority }) {
  const c = PRIORITY_COLOR[priority];
  if (!c) return null;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      font: "var(--text-caption)", fontSize: 12, fontWeight: 600,
      padding: "3px 10px", borderRadius: "var(--radius-pill)",
      background: c.bg, color: c.color, whiteSpace: "nowrap",
    }}>{priority}</span>
  );
}

/* A cached translation arrives as one string that preserves the authored line
 * structure: a `>` intent quote, then `- ` clauses. Rendering it in the monospace
 * acceptance block made a paragraph of Romanian prose look like a code listing, with
 * every `>` marker still on screen. This walks the lines back into the same shapes the
 * untranslated document uses. Acceptance keeps the block form — there it IS a listing. */
function TranslatedProse({ text, onNav, skipQuote = false }) {  // implements: REQ-TRANSLATE-938
  const lines = String(text || "").split("\n");
  const blocks = [];
  lines.forEach((raw) => {
    const line = raw.trim();
    if (!line) return;
    if (line.startsWith(">")) {
      const body = line.replace(/^>\s?/, "");
      const last = blocks[blocks.length - 1];
      if (last && last.kind === "quote") last.lines.push(body);
      else blocks.push({ kind: "quote", lines: [body] });
      return;
    }
    if (line.startsWith("- ")) {
      const body = line.slice(2);
      const last = blocks[blocks.length - 1];
      if (last && last.kind === "list") last.lines.push(body);
      else blocks.push({ kind: "list", lines: [body] });
      return;
    }
    const last = blocks[blocks.length - 1];
    // a hanging-indent continuation belongs to the bullet above it
    if (last && (last.kind === "list" || last.kind === "quote") && /^\s/.test(raw)) {
      last.lines[last.lines.length - 1] += " " + line;
      return;
    }
    blocks.push({ kind: "para", lines: [line] });
  });
  return (
    <>
      {blocks.map((b, i) => {
        if (b.kind === "quote")
          return skipQuote ? null : <p className="blockquote" key={i}>{b.lines.join(" ")}</p>;
        if (b.kind === "list")
          return (
            <ul key={i} {...reqLinkProps(onNav)}>
              {b.lines.map((l, j) => <li key={j} dangerouslySetInnerHTML={{ __html: mdInline(l) }} />)}
            </ul>
          );
        return <p className="spec-para" key={i} dangerouslySetInnerHTML={{ __html: mdInline(b.lines[0]) }} />;
      })}
    </>
  );
}

/* The requirement document itself. `head` and `after` are optional slots the
 * module explorer fills with its breadcrumb and its traceability Links block —
 * they render INSIDE the sheet so the whole thing reads as one document, and
 * both default to nothing so SpecView is unchanged. */
export function SpecDoc({ r, onNav, head = null, after = null }) {
  const { t, locale } = useI18n();
  if (!r) return null;
  const questions = openQuestions(r);
  const title = translatedText(r, locale, "title", r.title);
  const intent = translatedText(r, locale, "intent", r.intent);
  const contract = translatedText(r, locale, "contract");
  const acceptance = translatedText(r, locale, "acceptance");
  return (
    <div className="spec">
      <div className="spec-sheet">
      {head}
      <div className="head-row">
        <Pill kind={statusKind(r.status)}>{r.status}</Pill>
        <Pill kind={r.layer}>{r.layer}</Pill>
        {r.priority && <PriorityBadge priority={r.priority} />}
      </div>
      <h1>{title.text}{title.isTranslated && <TranslatedBadge />}</h1>
      {/* The frontmatter used to be reprinted here as a raw YAML block, `owner:`
          included — a field the engine never exports, so every repo but this one
          read someone else's name. What a reader needs beside the title is the id
          and where it points; the rest is already in the pills above. */}
      <div className="spec-meta">
        <span className="mk-val">{r.id}</span>
        <span className="mk-sep">|</span>
        <span className="mk-key">{t("level")}</span>
        <span className="mk-val">{r.level || "architecture"}</span>
        {r.milestone && <>
          <span className="mk-sep">|</span>
          <span className="mk-key">{t("milestone")}</span>
          <span className="mk-val">{r.milestone}</span>
        </>}
        {r.deps.length > 0 && <span className="mk-deps">
          <span className="mk-key">{t("depends on")}</span>
          <span className="mk-val">{r.deps.map((d,i)=>(
            <Fragment key={d}>{i>0 ? ", " : ""}<button className="dep-link" onClick={()=>onNav && onNav(d)}>{d}</button></Fragment>
          ))}</span>
        </span>}
      </div>
      <CovStrip r={r} />

      {/* Obligation first, reason under it: a requirement is read to find out what it
          binds, and the rationale is what supports that answer rather than what
          precedes it. The authored .md keeps the quote at the top of its Description
          section — this is the reading order, not the file's. */}
      <div className="sec">
        <div className="eyebrow">{t("Description")} <span className="rule" />{contract.isTranslated && <TranslatedBadge />}</div>
        {contract.isTranslated
          ? <TranslatedProse text={contract.text} onNav={onNav} skipQuote />
          : <ul {...reqLinkProps(onNav)}>{r.contract.map((c,i)=><li key={i} dangerouslySetInnerHTML={{__html: mdInline(c)}} />)}</ul>}
      </div>

      {/* An atomic requirement's `>` quote IS its obligation, so the engine emits no
          separate intent for one (_distinct_intent). Drawing the block anyway left an
          empty blockquote under a "Why — Intent" heading on 91% of nodes. */}
      {/* `r.intent` is the engine's verdict on whether the quote says anything the
          clauses do not; a cached translation must not put back a section it hid. */}
      {intent.text && r.intent && (
        <div className="sec why-sec">
          <div className="eyebrow">{t("Why — Intent")} <span>{r.layer === "bus" ? "foundation" : "feature"}{intent.isTranslated && <TranslatedBadge />}</span></div>
          <p className="blockquote">{intent.text}</p>
        </div>
      )}

      <div className="sec">
        <div className="eyebrow">{t("Cases")} <span className="rule" /> {t("= tests")}{acceptance.isTranslated && <TranslatedBadge />}</div>
        {acceptance.isTranslated
          ? <div className="gwt">{acceptance.text.split("\n").map((ln,i)=><div key={i}>{ln}</div>)}</div>
          : (r.gwt  // implements: REQ-VIEWER-942
            ? <div className="gwt">{r.gwt.split("\n").map((ln,i)=>(
                <div key={i}>{ln}</div>))}</div>
            : <ul {...reqLinkProps(onNav)}>{(r.acc||[]).map((a,i)=><li key={i} dangerouslySetInnerHTML={{__html: mdInline(a)}} />)}</ul>)}
      </div>

      <div className="sec">
        <div className="eyebrow">{t("Where — Members in code")}</div>
        <div className="members-box">
          {r.members.length
            ? r.members.map((m,i)=><div className="member" key={i}><span className="role">{m.role}:</span> {m.loc}</div>)
            : (r.layer === "need" || r.layer === "aggregate")
              ? <div className="member" style={{color:"var(--fg-muted)"}}>{t("(satisfied-by other requirements — no direct code)")}</div>
              /* "orphan" is the GATE's word for an ENFORCED requirement with no
                 implementing tag — an exit-1 error. A `draft` with no members is
                 not that; it is a requirement not yet wired, which is the normal
                 state of all 618 decomposed code-level clauses. Printing the red
                 error on them made the default view claim 618 build failures
                 that the gate does not report. */
              : ENFORCED[r.status]
                ? <div className="member" style={{color:"var(--status-error)"}}>{t("(no members found — orphan)")}</div>
                : <div className="member" style={{color:"var(--fg-muted)"}}>{t("(not linked to code yet — not enforced at this status)")}</div>}
        </div>
      </div>

      {/* Open questions — the author's own `## WHAT — Verify intent` bullets,
          minus the "None — …" placeholder the engine also filters out. A
          requirement with nothing but placeholders renders NO section here,
          which is why the Findings rail badge can honestly read zero. */}
      {questions.length > 0 && (
        <div className="sec">
          <div className="eyebrow warn">{t("Open questions — verify intent")}</div>
          <ul {...reqLinkProps(onNav)}>{questions.map((q,i)=><li key={i} dangerouslySetInnerHTML={{__html: mdInline(q)}} />)}</ul>
        </div>
      )}

      {r.risks && r.risks.length>0 && (
        <div className="sec">
          <div className="eyebrow warn">{t("Risk — recommended action")}</div>
          {r.risks.map((rk,i)=>(
            <div className="member" key={i} style={{font:"var(--text-body)",color:"var(--fg-secondary)"}}>
              <b style={{color:"var(--fg)"}}>{rk.signal}</b> — {rk.advice}</div>
          ))}
        </div>
      )}
      {after}
      </div>
    </div>
  );
}

export function SpecView({ selId, setSelId }) {
  const cur = selId && REQ_BY_ID[selId] ? selId : "ARCH-PARSE-001";
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
        {/* `area: CORE` is empty in a corpus that names its areas after commands —
            an empty heading is furniture, so the group only draws when it holds rows. */}
        {core.length > 0 && <>
          <div className="rail-section" style={{paddingTop:0}}>CORE · bus</div>
          {core.map(x=><Item key={x.id} x={x} />)}
        </>}
        {req.map(x=><Item key={x.id} x={x} />)}
      </div>
      <div style={{overflow:"auto"}}><SpecDoc r={r} onNav={setSelId} /></div>
    </div>
  );
}
