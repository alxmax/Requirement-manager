// implements: ARCH-VIEWER-007
import { useI18n, commandSummary } from "../../lib/i18n.jsx";

function CommandArticle({ c, locale }) {
  return (
    <article className="cmd">
      <div className="cmd-head">
        <code className="cmd-name">{"reqmap.py " + c.name + (c.arg ? " " + c.arg : "")}</code>
      </div>
      <p className="cmd-sum">{commandSummary(c, locale)}</p>
      {c.flags.length > 0 && (
        <dl className="cmd-flags">
          {c.flags.map((f) => (
            <div className="cmd-flag" key={f.flag}>
              <dt><code>{f.flag}</code></dt>
              <dd>{f.help}</dd>
            </div>
          ))}
        </dl>
      )}
    </article>
  );
}

export function CommandGroup({ group, rows, locale, t }) {
  if (!rows.length) return null;
  return (
    <section className="cmd-group">
      <h2 className="cmd-group-h">
        {t(group.label)} <span className="cmd-group-hint">{t(group.hint)}</span>
      </h2>
      {rows.map((c) => <CommandArticle key={c.name} c={c} locale={locale} />)}
    </section>
  );
}
