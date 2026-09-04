// implements: ARCH-VIEWER-007
// implements: REQ-VIEWER-964
/* CommandsView — what each CLI verb does, in the reader's language.
 *
 * The list is not written here: it arrives on `_map.json` as `commands`, generated
 * from the engine's own COMMANDS registry (ARCH-CMDREGISTRY-033). A verb that exists
 * is documented and one that was removed disappears from this page on the next `sync`,
 * which is the only way a command reference stays true.
 *
 * The English summary is the registry's own text. The Romanian one is UI chrome — the
 * tool's description of itself, not a requirement under review — so translating it
 * stays on the safe side of the i18n boundary (see lib/i18n.jsx). Flags are never
 * translated: `--accept-drift` is a literal you type. */
import { COMMANDS } from "../lib/data.js";
import { useI18n, commandSummary } from "../lib/i18n.jsx";

const GROUPS = [
  { key: "author", label: "Author", hint: "writing and evolving a requirement" },
  { key: "build", label: "Build", hint: "turning it into code, and proving it" },
  { key: "read", label: "Read", hint: "asking the corpus questions" },
];

export function CommandsView() {
  const { t, locale } = useI18n();
  const list = Array.isArray(COMMANDS) ? COMMANDS : [];

  if (!list.length) {
    return (
      <div className="main">
        <div className="prob-empty">
          <b>{t("No command list in this map.")}</b>
          <div style={{ marginTop: 6, color: "var(--fg-muted)", font: "var(--text-small)", maxWidth: 460 }}>
            {t("Regenerate it with a current engine — `reqmap.py sync` writes the command reference into _map.json.")}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="main">
      <div className="cmds">
        <p className="cmds-lede">
          {t("Every verb the engine exposes, generated from its own command registry.")}
        </p>
        {GROUPS.map((g) => {
          const rows = list.filter((c) => c.group === g.key);
          if (!rows.length) return null;
          return (
            <section className="cmd-group" key={g.key}>
              <h2 className="cmd-group-h">
                {t(g.label)} <span className="cmd-group-hint">{t(g.hint)}</span>
              </h2>
              {rows.map((c) => (
                <article className="cmd" key={c.name}>
                  <div className="cmd-head">
                    <code className="cmd-name">
                      {"reqmap.py " + c.name + (c.arg ? " " + c.arg : "")}
                    </code>
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
              ))}
            </section>
          );
        })}
      </div>
    </div>
  );
}
