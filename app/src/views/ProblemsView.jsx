// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-966
// implements: REQ-VIEWER-977
/* ProblemsView — every open signal about the corpus, in one inbox.
 *
 * Two kinds of row live here, and the difference is who said there was a problem:
 *   - the engine's own risk signals, derived from the corpus state on every load
 *     (an orphan, an untested requirement, partial per-criterion coverage, a draft
 *     nobody has reviewed);
 *   - an author's open `## Verify intent` question — a human writing down what they
 *     did not resolve.
 *
 * A third origin joined them: the advisory code review (`gate --design`), whose rows
 * are about a FILE rather than a requirement and which never gates anything. It gets its
 * own tab and is deliberately absent from "All" — the inbox counts what is open about the
 * corpus, and 123 advisory candidates dropped in there would bury the six that are.
 *
 * They were two screens until v4.0.0, because Problems was then ~618 rows of draft
 * review noise and a real question dropped in there was invisible. Two things ended
 * that: the corpus folded to 224 requirements with no drafts at all, and the draft
 * rows gained the collapse below, which treats the noise where it is rather than by
 * evacuating everything else. What survives the merge is the distinction itself —
 * origin is a first-class tab here, never a severity, so "what did a human flag?"
 * stays one click away instead of being ranked among computed findings.
 * See docs/adr/0028. */
import { useState } from "react";
import { REQUIREMENTS, coverageOf, DESIGN } from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { Pill, statusKind } from "../lib/ui.jsx";
import { useI18n } from "../lib/i18n.jsx";
import { openQuestions } from "../lib/tree.js";

/* derive a flat problem list from the registry (exported so App can count it) */
export function computeProblems() {
  const SEV = {
    unimplemented:      { sev:"ERROR",  msg:"No implementing member — orphan. The gate blocks the build.", fix:"Add an `implements:` tag, or author the requirement." },
    untested:           { sev:"WARN",   msg:"Confirmed, but no `tested-by:` member is linked.", fix:"Add a test tag, or set `test_exempt:` to silence." },
    "unverified-intent":{ sev:"WARN",   msg:"Has open `## Verify intent` question(s).", fix:"Run `reqmap.py findings`, resolve each one, then fold the answer into the Description or delete the bullet." },
    unreviewed:         { sev:"REVIEW", msg:"Drafted from code by extract — intent not yet validated.", fix:"Review, then `req promote <ID>`." },
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
        msg:`Partial coverage — ${r.covered}/${r.clauses} criteria verified. ${r.gap||""}`.trim(),
        fix:"Tag a test `# verifies: <id>#CASE-N` for the uncovered criterion, or write one.",
        loc:(r.members.find(m=>m.role==="tested-by")||{}).loc || "" });
    } else if (cov === "untested" && r.status !== "draft" && !flagged) {
      out.push({ id:r.id, title:r.title, signal:"untested", sev:"WARN",
        msg:"Untested — no live acceptance test, or a `tested-by` range that no longer resolves (stale ref).",
        fix:"Add a test, repair the stale `tested-by` ref, or set `test_exempt:`.",
        loc:(r.members.find(m=>m.role==="tested-by")||{}).loc || "" });
    }
  });
  // an author's own open questions — the one kind of row nobody derived
  REQUIREMENTS.forEach(r => {
    const qs = openQuestions(r);
    if (!qs.length) return;
    out.push({ id:r.id, title:r.title, signal:"question", sev:"QUESTION",
      status:r.status, questions:qs,
      msg:`${qs.length} open verify-intent question(s).`,
      fix:"Answer it, fold the answer into the Description, then delete the bullet.",
      loc:"" });
  });
  // A question outranks an unreviewed draft: somebody wrote it down on purpose.
  const order = { ERROR:0, WARN:1, QUESTION:2, REVIEW:3 };
  return out.sort((a,b)=> order[a.sev]-order[b.sev] || a.id.localeCompare(b.id));
}

/** Only the rows a human wrote — App's badge counts these separately. */
export function computeQuestions() {
  return computeProblems().filter(p => p.sev === "QUESTION");
}

/* The `unreviewed` signal on a `draft` is not a defect report — it is the
 * normal state of a requirement drafted from code and not yet promoted. With a
 * decomposed corpus that is ~618 identical rows, and every real ERROR and WARN
 * is buried under them. They are counted, named and one click away; they are
 * not the default reading. */
const isDraftReview = (p) => p.sev === "REVIEW" && p.signal === "unreviewed";

export function ProblemsView({ openSpec }) {
  const { t } = useI18n();
  const [filter, setFilter] = useState("ALL");
  const [showDrafts, setShowDrafts] = useState(false);
  const all = computeProblems();
  const counts = all.reduce((a,p)=>{ a[p.sev]=(a[p.sev]||0)+1; return a; }, {});
  // Advisory code-review candidates, grouped the way the CLI prints them. Absent on a
  // map written before the engine carried them, which is why this is a guarded read.
  const design = (DESIGN && Array.isArray(DESIGN.findings)) ? DESIGN.findings : [];
  const advice = (DESIGN && DESIGN.advice) || {};
  const byPillar = design.reduce((a,f)=>{ (a[f.pillar] = a[f.pillar] || []).push(f); return a; }, {});
  const draftReviews = all.filter(isDraftReview).length;
  const byTab = filter==="ALL" ? all : all.filter(p=>p.sev===filter);
  const shown = showDrafts ? byTab : byTab.filter(p => !isDraftReview(p));
  const hidden = byTab.length - shown.length;

  const Tab = ({k,label,n}) => (
    <button className={"tab"+(filter===k?" on":"")} onClick={()=>setFilter(k)}>
      {label}{n!=null && <span style={{marginLeft:6,opacity:.7,fontFamily:"var(--font-mono)",fontSize:11}}>{n}</span>}
    </button>
  );

  return (
    <div className="main">
      <div className="tabbar">
        <Tab k="ALL" label={t("All")} n={all.length} />
        <Tab k="ERROR" label={t("Errors")} n={counts.ERROR||0} />
        <Tab k="WARN" label={t("Warnings")} n={counts.WARN||0} />
        <Tab k="QUESTION" label={t("Questions")} n={counts.QUESTION||0} />
        <Tab k="REVIEW" label={t("Review")} n={counts.REVIEW||0} />
        {design.length > 0 && <Tab k="DESIGN" label={t("Design")} n={design.length} />}
        <div className="tab-legend">
          {(counts.ERROR||0) > 0
            ? <><Icon name="triangle-alert" size={14} style={{color:"var(--status-error)"}} /> {t("gate blocks the build — {n} error", { n: counts.ERROR })}</>
            : <><Icon name="shield-check" size={14} style={{color:"var(--status-confirmed)"}} /> {t("gate passes")}</>}
        </div>
      </div>

      <div className="problems">
        {filter === "DESIGN" && (
          <>
            <div className="prob-chip" style={{cursor:"default"}}>
              {t("Advisory only — a candidate is a shape worth a look, never a defect, and this never enters the gate.")}
            </div>
            {Object.keys(byPillar).sort().map(pillar => {
              const rows = byPillar[pillar];
              const kinds = [...new Set(rows.map(f=>f.kind))].sort();
              return (
                <div key={pillar}>
                  <div className="prob-head" style={{margin:"14px 0 6px",textTransform:"capitalize"}}>
                    <b>{pillar}</b>
                    <span style={{marginLeft:6,opacity:.7,fontFamily:"var(--font-mono)",fontSize:11}}>{rows.length}</span>
                  </div>
                  {rows.map((f,i)=>(
                    <div className="prob-row" key={i}>
                      <span className="prob-sev sev-REVIEW">{f.kind}</span>
                      <div className="prob-body">
                        <div className="prob-head"><span className="prob-id">{f.name}</span></div>
                        <div className="prob-msg">{f.detail}</div>
                      </div>
                      <span className="prob-loc">{f.file}:{f.line}</span>
                    </div>
                  ))}
                  {kinds.filter(k=>advice[k]).map(k=>(
                    <div className="prob-fix" key={k} style={{margin:"4px 0 0 4px"}}>
                      <Icon name="arrow-right" size={13} /> {advice[k]}
                    </div>
                  ))}
                </div>
              );
            })}
          </>
        )}
        {filter !== "DESIGN" && (hidden > 0 || (showDrafts && draftReviews > 0)) && (
          <button type="button" className="prob-chip" onClick={()=>setShowDrafts(s=>!s)}>
            {showDrafts
              ? t("hide {n} draft review rows", { n: draftReviews })
              : t("{n} draft review rows hidden — show", { n: hidden })}
          </button>
        )}
        {filter !== "DESIGN" && shown.map((p,i)=>(
          <div className={"prob-row"+(p.sev==="QUESTION"?" question-row":"")} key={i}
            onClick={()=>p.id!=="—" && openSpec(p.id)}>
            <span className={"prob-sev sev-"+p.sev}>{p.sev==="QUESTION" ? t("ASKED") : p.sev}</span>
            <div className="prob-body">
              <div className="prob-head">
                <span className="prob-id">{p.id}</span>
                <span className="prob-title">{p.title}</span>
                {p.status && <Pill kind={statusKind(p.status)}>{p.status}</Pill>}
              </div>
              {p.questions
                ? <ul className="finding-qs">{p.questions.map((q,j)=><li key={j}>{q}</li>)}</ul>
                : <div className="prob-msg">{p.msg}</div>}
              <div className="prob-fix"><Icon name="arrow-right" size={13} /> {p.fix}</div>
            </div>
            {p.loc && <span className="prob-loc">{p.loc}</span>}
          </div>
        ))}
        {filter !== "DESIGN" && shown.length===0 && (
          <div className="prob-empty">
            <Icon name="shield-check" size={26} style={{color:"var(--cov-tested)"}} />
            {/* `filter` is "ALL" on the default tab, which read as
                "no all signals open." Say what is actually true instead. */}
            <div>
              <b>{filter==="ALL" ? t("Nothing to fix.") : t("Nothing in this tab.")}</b>
              <div style={{marginTop:6,color:"var(--fg-muted)",font:"var(--text-small)",maxWidth:460}}>
                {filter==="ALL"
                  ? t("The gate reports no errors, warnings or review items for this registry.")
                  : t("Other tabs may still have open items.")}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
