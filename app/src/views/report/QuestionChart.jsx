// implements: REQ-VIEWER-1155
/* Open questions by priority, each bar split by where they sit: on a
 * confirmed requirement (its contract is enforced while the question is open)
 * or on a draft. The map carries no date for a question, so this is a
 * picture of now, not a trend. */
import { useI18n } from "../../lib/i18n.jsx";

const ROW = 26;
const LABEL = 78;
const PARTS = [
  { key: "confirmed", name: "On confirmed requirements", color: "var(--status-confirmed)" },
  { key: "other", name: "On drafts", color: "var(--status-draft)" },
];
const PRIO_NAME = { high: "High", medium: "Medium", low: "Low" };

/** `split` from `computeReport()`: [{prio, confirmed, other}]. */
export function QuestionChart({ split, width = 560, filter = null }) {
  const { t } = useI18n();
  // all zero still draws the bars and the filter, so a filter can be undone
  const max = Math.max(1, ...split.map((s) => s.confirmed + s.other));
  const plotW = width - LABEL - 40;
  const w = (n) => (plotW * n) / max;
  return (
    <figure className="rep-chart">
      <figcaption><b>{t("Open questions by priority")}</b></figcaption>
      {filter}
      <div className="bug-chart-legend">
        {PARTS.map((p) => (
          <span key={p.key}><i style={{ background: p.color }} />{t(p.name)}</span>
        ))}
      </div>
      <svg width={width} height={ROW * split.length + 4} role="img"
        aria-label={t("Open questions by priority, on confirmed requirements and on drafts")}>
        {split.map((s, i) => {
          const y = i * ROW + 4;
          const n = s.confirmed + s.other;
          return (
            <g key={s.prio}>
              <text className="rep-chart-label" x={LABEL - 8} y={y + 14} textAnchor="end">
                {t(PRIO_NAME[s.prio])}</text>
              <rect x={LABEL} y={y} width={w(s.confirmed)} height={ROW - 8}
                fill={PARTS[0].color}>
                <title>{`${t(PARTS[0].name)}: ${s.confirmed}`}</title></rect>
              <rect x={LABEL + w(s.confirmed)} y={y} width={w(s.other)} height={ROW - 8}
                fill={PARTS[1].color}>
                <title>{`${t(PARTS[1].name)}: ${s.other}`}</title></rect>
              <text className="rep-chart-label" x={LABEL + w(n) + 6} y={y + 14}>
                {t("{n} ({c} on confirmed)", { n, c: s.confirmed })}</text>
            </g>
          );
        })}
      </svg>
    </figure>
  );
}
