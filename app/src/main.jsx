// implements: ARCH-VIEWER-007
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { NoMap } from "./components/NoMap.jsx";
import { I18nProvider } from "./lib/i18n.jsx";
import { loadData } from "./lib/loadData.js";
import "./styles/app.css";

// Try the engine's _map.json export before first paint; with none, say so
// rather than render an empty registry.
loadData().then((res) => res, () => ({ source: "none" })).then((res) => {
  createRoot(document.getElementById("root")).render(
    <StrictMode>
      <I18nProvider>
        {res.source === "none" ? <NoMap /> : <App />}
      </I18nProvider>
    </StrictMode>
  );
});
