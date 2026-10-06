// implements: ARCH-VIEWER-007
import { useI18n } from "../lib/i18n.jsx";

/* What the viewer shows when no map reached it: the bare template opened
 * directly, or `npm run dev` before `npm run sync`. It says so and names the
 * command that writes one, instead of showing requirements that do not exist
 * (ADR-0065). */
export function NoMap() {
  const { t } = useI18n();
  return (
    <main style={{
      minHeight: "100vh", display: "grid", placeItems: "center", padding: 24,
      background: "var(--bg)", color: "var(--fg)", fontFamily: "var(--font-sans)",
    }}>
      <div style={{ maxWidth: 520 }}>
        <h1 style={{ font: "var(--text-h1)", marginBottom: 12 }}>
          {t("No requirement map to show")}
        </h1>
        <p style={{ color: "var(--fg-secondary)", marginBottom: 16 }}>
          {t("This viewer opened without a map. Run this in your repository, then open requirements/_map.html:")}
        </p>
        <code style={{
          display: "block", font: "var(--text-code)", padding: "12px 14px",
          background: "var(--surface)", border: "1px solid var(--border)",
          borderRadius: 8,
        }}>python scripts/reqmap.py sync</code>
      </div>
    </main>
  );
}
