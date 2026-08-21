import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { I18nProvider } from "./lib/i18n.jsx";
import { loadData } from "./lib/loadData.js";
import "./styles/app.css";

// Try the engine's _map.json export before first paint; the loader falls back
// to the baked dataset on any miss, so render is never blocked.
loadData().finally(() => {
  createRoot(document.getElementById("root")).render(
    <StrictMode>
      <I18nProvider>
        <App />
      </I18nProvider>
    </StrictMode>
  );
});
