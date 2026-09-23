// implements: ARCH-VIEWER-007
/* Render-time smoke test: server-render every view against the engine-adapted
 * dataset and assert real content appears. Catches render-throws and bad data
 * assumptions the build cannot. Bundled + run by run-ssr-smoke.mjs.
 *
 * The checks live in ./smoke/, one file per area, and run in the order imported
 * here: several of them swap the adopted dataset and put it back, so the order
 * is part of the test. */
import { finish } from "./smoke/harness.jsx";
import "./smoke/views.jsx";
import "./smoke/explorer.jsx";
import "./smoke/rail.jsx";
import "./smoke/plan.jsx";
import "./smoke/history.jsx";

finish();
