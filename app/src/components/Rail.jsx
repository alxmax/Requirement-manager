// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-945
import {
  REQUIREMENTS, TODOS, ROADMAP, REPO, COMMANDS as CLI, HEALTH, DESIGN,
} from "../lib/data.js";
import { Icon } from "../lib/icons.jsx";
import { useI18n } from "../lib/i18n.jsx";
import { ENFORCED } from "../views/SpecDoc.jsx";

const NAV = [
  { key: "explorer", label: "Explorer", icon: "list-checks" },
  { key: "problems", label: "Problems", icon: "triangle-alert" },
  { key: "map", label: "Map", icon: "network" },
  { key: "roadmap", label: "Roadmap", icon: "list-checks" },
  { key: "commands", label: "Commands", icon: "terminal" },
];

function Gauge({ pct, tone, size = 28 }) {
  const r = (size - 4) / 2, c = 2 * Math.PI * r, mid = size / 2;
  const on = c * Math.max(0, Math.min(100, pct)) / 100;
  return (
    <svg className="gauge" width={size} height={size} viewBox={`0 0 ${size} ${size}`}
         aria-hidden="true">
      <circle cx={mid} cy={mid} r={r} fill="none" stroke="var(--line-2)" strokeWidth="3" />
      <circle cx={mid} cy={mid} r={r} fill="none" stroke={tone} strokeWidth="3"
        strokeLinecap="round" strokeDasharray={`${on} ${c}`}
        transform={`rotate(-90 ${mid} ${mid})`} />
    </svg>
  );
}

const BADGE = { borderRadius: "var(--radius-pill)", padding: "1px 8px", fontWeight: 600 };
const ERROR_BADGE = {
  ...BADGE, color: "var(--status-error)", background: "var(--status-error-bg)",
};
const ASKED_BADGE = {
  ...BADGE, color: "var(--status-drift)", background: "var(--status-drift-bg)",
};

function RailNav({ view, setView, problems }) {
  const { t } = useI18n();
  const errCount = problems.filter((p) => p.sev === "ERROR").length;
  const questionCount = problems.filter((p) => p.sev === "QUESTION").length;
  /* Open work on the Roadmap tab, whichever plan the repo keeps: `TODO.md` items and
   * `ROADMAP.md` horizons. Counting only TODOS made the badge read 0 the day this repo
   * retired its own TODO.md — with ten open horizon items one click away, which reads
   * as "nothing here" and is why the tab looked missing.  implements: REQ-VIEWER-999 */
  const todoCount = TODOS.filter((item) => !item.done).length
    + ROADMAP.filter((item) => !item.done
        && (item.horizon === "now" || item.horizon === "next" || item.horizon === "later")).length;
  const badge = (key) => (key !== "problems" ? undefined
    : errCount > 0 ? ERROR_BADGE : questionCount > 0 ? ASKED_BADGE : undefined);
  const counts = {
    explorer: REQUIREMENTS.length,
    map: REQUIREMENTS.filter((r) => r.level !== "code").length,
    problems: problems.length,
    spec: REQUIREMENTS.length,
    roadmap: todoCount,
    commands: CLI.length || null,
  };
  return (
    <>
      <div className="rail-section" style={{ paddingTop: 2 }}>{t("Workspace")}</div>
      {NAV.map((n) => (
        <div key={n.key} className={"nav-item" + (view === n.key ? " active" : "")}
             onClick={() => setView(n.key)}>
          <Icon name={n.icon} size={17} className="ico" />
          {t(n.label)}
          <span className="count" style={badge(n.key)}>{counts[n.key]}</span>
        </div>
      ))}
    </>
  );
}

function gaugeTone(score) {
  if (score >= 90) return "var(--cov-tested)";
  if (score >= 60) return "var(--cov-partial)";
  return "var(--cov-untested)";
}

function RailGauges({ setView }) {
  const { t } = useI18n();
  if (!HEALTH && !DESIGN) return null;
  return (
    <div className="rail-gauges">
      <div className="rail-section" style={{ paddingTop: 0, paddingLeft: 0 }}>{t("Signals")}</div>
      {HEALTH && (
        <button type="button" className="gauge-row"
          title={t(
            "Requirements green on every axis — confirmed, implemented, tested, "
            + "no open question, no drift",
          )}
          onClick={() => setView("problems")}>
          <Gauge pct={HEALTH.score} tone={gaugeTone(HEALTH.score)} />
          <span className="gauge-txt">
            <span className="gauge-name">{t("Health")}<b>{HEALTH.score}</b></span>
            <span className="gauge-sub">
              {t("{a}/{b} green", { a: HEALTH.healthy, b: HEALTH.scored ?? HEALTH.total })}
              {HEALTH.exempt ? " · " + t("{n} exempt", { n: HEALTH.exempt }) : ""}
            </span>
          </span>
        </button>
      )}
      {DESIGN && (
        <div className="gauge-row static"
          title={t(
            "Source files with no OOP or house-standard candidate — advisory, "
            + "never part of the gate",
          )}>
          <Gauge pct={DESIGN.score} tone="var(--fg-muted)" />
          <span className="gauge-txt">
            <span className="gauge-name">{t("Design OOP")}<b>{DESIGN.score}</b></span>
            <span className="gauge-sub">
              {t("{a}/{b} files clean", { a: DESIGN.clean_files, b: DESIGN.files })}
            </span>
          </span>
        </div>
      )}
    </div>
  );
}

const isOrphan = (r) => ENFORCED[r.status] && r.layer !== "need" && r.layer !== "aggregate"
  && !r.members.some((m) => m.role === "implements");
const ORPHAN_TITLE = "enforced requirements with no implements: member — "
  + "the gate's error condition";
const MUTED_MONO = { fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--fg-faint)" };

function RailStats({ focus, setFocus }) {
  const { t } = useI18n();
  const by = (pred) => REQUIREMENTS.filter(pred).length;
  const stats = [
    { key: "confirmed", n: by((r) => r.status === "confirmed"), color: "var(--status-confirmed)" },
    { key: "in-progress", n: by((r) => r.status === "in-progress"), color: "var(--status-drift)" },
    { key: "draft", n: by((r) => r.status === "draft"), color: "var(--status-draft)" },
    { key: "orphan", n: by(isOrphan), color: "var(--status-error)" },
    { key: "deprecated", n: by((r) => r.status === "deprecated"), color: "var(--cov-exempt)" },
  ];
  const bound = REQUIREMENTS.reduce((a, r) => a + r.members.length, 0);
  return (
    <div className="rail-stat">
      <div className="rail-section" style={{ paddingTop: 0, paddingLeft: 0 }}>{t("Registry")}</div>
      {stats.map((s) => (
        <button type="button" key={s.key} className={"stat-row" + (focus === s.key ? " on" : "")}
          aria-pressed={focus === s.key}
          title={s.key === "orphan" ? ORPHAN_TITLE : "show only " + s.key + " requirements"}
          onClick={() => setFocus(focus === s.key ? null : s.key)}>
          <span className="sw" style={{ background: s.color }} />
          {s.key}<span className="n">{s.n}</span>
        </button>
      ))}
      <div className="stat-row"
           style={{ marginTop: 6, borderTop: "1px solid var(--border-soft)", paddingTop: 8 }}>
        <Icon name="git-branch" size={14} className="ico" style={{ color: "var(--fg-faint)" }} />
        <span style={MUTED_MONO}>{t("{n} members bound", { n: bound })}</span>
      </div>
    </div>
  );
}

const FOOTER = {
  marginTop: 8, paddingTop: 8, borderTop: "1px solid var(--border-soft)", textAlign: "center",
};
const FOOTER_LINK = {
  fontSize: 10, color: "var(--fg-faint)", textDecoration: "none", fontFamily: "var(--font-mono)",
  opacity: 0.7,
};

export function Rail({ view, setView, focus, setFocus, problems }) {
  return (
    <nav className="rail">
      <RailNav view={view} setView={setView} problems={problems} />
      <RailGauges setView={setView} />
      <RailStats focus={focus} setFocus={setFocus} />
      <div style={FOOTER}>
        <a href="https://github.com/alxmax/Requirement-manager" target="_blank" rel="noreferrer"
          style={FOOTER_LINK}>
          by requirement-manager
        </a>
      </div>
    </nav>
  );
}
