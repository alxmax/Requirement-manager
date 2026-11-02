// implements: ARCH-BUGS-078
// implements: REQ-BUGS-1121
// implements: REQ-BUGS-1122
// implements: REQ-BUGS-1123
import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { BUGS, REPO, REQUIREMENTS } from "../../lib/data.js";
import { Icon } from "../../lib/icons.jsx";
import { useI18n } from "../../lib/i18n.jsx";
import {
  bugCommand, canWrite, moduleFile, saveBug,
} from "../../lib/bugFile.js";
import { ChipRow } from "./ProblemsPanels.jsx";

const PRIOS = ["P0", "P1", "P2", "P3", "P4"];
const PRIO_NAME = { P0: "critical", P1: "high", P2: "medium", P3: "low",
  P4: "minor" };
const SEV = { P0: "ERROR", P1: "ERROR", P2: "WARN", P3: "REVIEW", P4: "REVIEW" };
const COUNT = {
  marginLeft: 6, opacity: .7, fontFamily: "var(--font-mono)", fontSize: 11,
};
const today = () => new Date().toISOString().slice(0, 10);
const shortDate = (d) => (d || "").split("-").reverse().join(".");

/** What the form offers as a module: every module with a bug, and every
 * capability the map names, so a repository with no bugs still has a list. */
export function moduleChoices(bugs, requirements) {
  const capabilities = requirements
    .filter((r) => r.level === "architecture" && r.status !== "deprecated")
    .map((r) => r.title);
  return [...new Set([...bugs.map((b) => b.module), ...capabilities])].sort();
}

export function BugForm({ modules, add, close, error }) {
  const { t } = useI18n();
  const [f, setF] = useState({ title: "", module: "", prio: "P2",
    date: today(), where: "", why: "" });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const ready = f.title.trim() && moduleFile(f.module);
  return (
    <form className="bug-form" onSubmit={(e) => {
      e.preventDefault();
      if (ready) add({ ...f, title: f.title.trim(), module: f.module.trim() });
    }}>
      <label className="bug-wide">{t("What is broken")}
        <input value={f.title} onChange={set("title")} autoFocus />
      </label>
      <label>{t("Module")}
        <input list="bug-modules" value={f.module} onChange={set("module")} />
        <datalist id="bug-modules">
          {modules.map((m) => <option key={m} value={m} />)}
        </datalist>
      </label>
      <label>{t("Priority")}
        <select value={f.prio} onChange={set("prio")}>
          {PRIOS.map((p) => (
            <option key={p} value={p}>{p} · {t(PRIO_NAME[p])}</option>
          ))}
        </select>
      </label>
      <label>{t("Date")}
        <input type="date" value={f.date} onChange={set("date")} />
      </label>
      <label>{t("Where (file:line)")}
        <input value={f.where} onChange={set("where")} />
      </label>
      <label className="bug-wide">{t("Why it matters")}
        <textarea rows={2} value={f.why} onChange={set("why")} />
      </label>
      {error && <div className="bug-wide bug-error">{t(error)}</div>}
      <div className="q-panel-actions">
        <button className="btn btn-secondary" type="submit" disabled={!ready}>
          {t("Save bug")}
        </button>
        <button className="btn btn-ghost" type="button" onClick={close}>
          {t("Cancel")}
        </button>
      </div>
    </form>
  );
}

const inOrder = (rows) => [...rows].sort((a, b) => a.prio.localeCompare(b.prio));
const located = (b) => b.file + (b.line ? `:${b.line}` : "");
const prioMix = (rows) => PRIOS.filter((p) => rows.some((b) => b.prio === p))
  .map((p) => [p, rows.filter((b) => b.prio === p).length]);

function BugFields({ b }) {
  const { t } = useI18n();
  return (
    <>
      {b.why && <p><b>{t("Why it matters")}:</b> {b.why}</p>}
      {b.where && <p><b>{t("Where")}:</b> <code>{b.where}</code></p>}
      {b.source && <p><b>{t("Source")}:</b> {b.source}</p>}
      {b.file && <p><b>{t("File")}:</b> <code>{located(b)}</code></p>}
    </>
  );
}

/** The list as it goes on paper: every group open, every field out. Mounted
 * under <body> only while printing, and the print stylesheet hides the rest. */
export function BugReport({ groups, keys, scope }) {
  const { t } = useI18n();
  const total = keys.reduce((n, k) => n + groups[k].length, 0);
  const head = [t("{n} bugs", { n: total }), today(), scope];
  return (
    <div className="bug-report">
      <h1>{REPO ? `${REPO}: ` : ""}{t("Known bugs")}</h1>
      <p>{head.filter(Boolean).join(" · ")}</p>
      {keys.map((k) => (
        <section key={k}>
          <h2>{k}</h2>
          <p>{prioMix(groups[k]).map(([p, n]) => `${p} ${n}`).join(" · ")}</p>
          {inOrder(groups[k]).map((b) => (
            <div className="bug-report-row" key={b.id}>
              <div>
                <b>{b.prio}{b.estimated ? "*" : ""} {b.ref}</b>
                {b.date ? ` · ${shortDate(b.date)}` : ""} · {b.title}
              </div>
              <BugFields b={b} />
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}

function BugRow({ b, open, toggle }) {
  const { t } = useI18n();
  return (
    <div className={"prob-row bug-row" + (open ? " picked" : "")}
      onClick={toggle}>
      <div className="bug-left">
        <span className={"prob-sev sev-" + SEV[b.prio]}>
          {b.prio}{b.estimated ? "*" : ""}
        </span>
        {b.date && <span className="bug-date">{shortDate(b.date)}</span>}
      </div>
      <div className="prob-body">
        <div className="prob-head">
          <span className="prob-id">{b.ref}</span>
          {b.added && <span className="bug-own">{t("added, run sync")}</span>}
        </div>
        <div className={"bug-title" + (open ? "" : " clamped")}>{b.title}</div>
        {open && (
          <div className="bug-more" onClick={(e) => e.stopPropagation()}>
            <BugFields b={b} />
          </div>
        )}
      </div>
    </div>
  );
}

function BugGroup({ label, rows, defaultOpen, pick, setPick }) {
  return (
    <details className="bug-group" open={defaultOpen}>
      <summary>
        <b>{label}</b><span style={COUNT}>{rows.length}</span>
        <span className="bug-mix">
          {prioMix(rows).map(([p, n]) => <span key={p}>{p} {n}</span>)}
        </span>
      </summary>
      {inOrder(rows).map((b) => (
        <BugRow key={b.id} b={b} open={pick === b.id}
          toggle={() => setPick(pick === b.id ? null : b.id)} />
      ))}
    </details>
  );
}

/** Known bugs by module, the only grouping. `added` holds what this page
 * wrote, which the map cannot carry until the next `sync`. */
export function BugsPanel({ added, setAdded }) {
  const { t } = useI18n();
  const [prio, setPrio] = useState(null);
  const [query, setQuery] = useState("");
  const [adding, setAdding] = useState(false);
  const [pick, setPick] = useState(null);
  const [error, setError] = useState(null);
  const [command, setCommand] = useState(null);
  const [printing, setPrinting] = useState(false);
  useEffect(() => {
    if (!printing) return undefined;
    const done = () => setPrinting(false);
    window.addEventListener("afterprint", done);
    window.print();
    return () => window.removeEventListener("afterprint", done);
  }, [printing]);
  const all = useMemo(() => [...added, ...BUGS], [added]);
  const modules = useMemo(
    () => moduleChoices(all, REQUIREMENTS), [all]);
  const add = async (bug) => {
    setError(null);
    if (!canWrite()) {
      setCommand(bugCommand(bug));
      setAdding(false);
      return;
    }
    try {
      const { ref, file } = await saveBug(bug);
      setAdded([{ ...bug, id: `new:${file}:${ref}`, ref, file, added: true },
        ...added]);
      setAdding(false);
    } catch (e) {
      if (e.name !== "AbortError") setError(e.message);
    }
  };
  const q = query.trim().toLowerCase();
  const hay = (b) => `${b.ref} ${b.title} ${b.where || ""}`.toLowerCase();
  const found = all.filter((b) => !q || hay(b).includes(q));
  const counts = {};
  found.forEach((b) => { counts[b.prio] = (counts[b.prio] || 0) + 1; });
  const shown = found.filter((b) => !prio || b.prio === prio);
  const groups = {};
  shown.forEach((b) => { (groups[b.module] = groups[b.module] || []).push(b); });
  const keys = Object.keys(groups).sort(
    (a, b) => a.localeCompare(b, undefined, { numeric: true }));
  return (
    <>
      <div className="bug-bar">
        <input className="bug-search" placeholder={t("Search bugs")}
          value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className="btn btn-secondary"
          onClick={() => setAdding(!adding)}>
          <Icon name="plus" size={13} /> {t("Add bug")}
        </button>
        <button className="btn btn-ghost" disabled={keys.length === 0}
          onClick={() => setPrinting(true)}>
          {t("Export PDF")}
        </button>
      </div>
      {adding && <BugForm modules={modules} add={add} error={error}
        close={() => setAdding(false)} />}
      {command && (
        <div className="bug-form">
          <div className="bug-wide">
            {t("This browser cannot write to the repository. Run this "
              + "command, then `sync`:")}
          </div>
          <code className="bug-wide bug-command">{command}</code>
        </div>
      )}
      <ChipRow counts={counts} total={found.length} value={prio}
        setValue={setPrio} label={(k) => k} />
      {keys.map((k) => (
        <BugGroup key={k} label={k} rows={groups[k]}
          defaultOpen={keys.length === 1 || Boolean(q) || Boolean(prio)}
          pick={pick} setPick={setPick} />
      ))}
      {keys.length === 0 && (
        <div className="prob-empty">
          <b>{t(all.length ? "No bugs found." : "No known bugs yet.")}</b>
        </div>
      )}
      {printing && createPortal(
        <BugReport groups={groups} keys={keys}
          scope={[prio, query.trim()].filter(Boolean).join(" · ")} />,
        document.body)}
    </>
  );
}
