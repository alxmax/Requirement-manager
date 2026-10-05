/* Render smoke test, part: release cadence, stacking, selection, weeks. */
import { renderToString } from "react-dom/server";

import App from "../../src/App.jsx";
import { rankRequirements, searchRequirements } from "../../src/lib/search.js";
import {
  adoptMapExport, REQUIREMENTS, ROADMAP, HISTORY, TARGETS,
} from "../../src/lib/data.js";
import { adaptNode, loadData } from "../../src/lib/loadData.js";
import {
  ProblemsView, computeProblems, computeQuestions,
} from "../../src/views/ProblemsView.jsx";
import { RoadmapView } from "../../src/views/RoadmapView.jsx";
import {
  PlanGantt, noteText, matchItem, ReleaseNote, ShippedNote, VersionNote,
} from "../../src/views/roadmap/PlanGantt.jsx";
import { EntryBody } from "../../src/views/roadmap/EntryBody.jsx";
import { stackBars, buildDayBands } from "../../src/lib/timeline.js";
import {
  PX, PLAN_CHAR, besideLabelWidth, extent, footprint,
} from "../../src/views/roadmap/ganttLayout.js";
import { dayStyle } from "../../src/views/roadmap/GanttRuler.jsx";
import { SpecDoc } from "../../src/views/SpecDoc.jsx";
import { REQ_BY_ID } from "../../src/lib/data.js";
import { ExplorerView } from "../../src/views/ExplorerView.jsx";
import { CommandsView } from "../../src/views/CommandsView.jsx";

import { I18nProvider, translate } from "../../src/lib/i18n.jsx";
import { computeLayout } from "../../src/lib/layout.js";
import {
  buildHierarchy, defaultExpanded, allExpanded, flattenTree, ancestorsOf,
  keepSetFor, openQuestions, levelOf,
} from "../../src/lib/tree.js";
import { json, noop, specOf, test, fail } from "./harness.jsx";

// ---- release cadence (REQ-PLANCADENCE-1000) --------------------------------
// The chart PLACES engine-computed dates and derives none. Asserted by
// handing it a date the weekday arithmetic would never produce: if a
// rule appears for it, the viewer is reading the list; if the viewer
// recomputed, it would not be there.
// verifies: REQ-PLANCADENCE-1000#CASE-1
test("cadence: a release past the last bar still gets a column",
  (() => {
    // `until` running past everything scheduled is the whole point of a
    // cadence: the months after the last bar are exactly where the next
    // releases land. Before the range counted release dates, those were
    // emitted and then dropped by the in-range filter — the engine said
    // a release lands and the chart showed nothing.
    const far = renderToString(<PlanGantt planning={{
      lanes: ["Feature"],
      bars: [
        { title: "b", lane: "Feature", start: "2026-09-21", end: "2026-09-27" },
      ],
      cadence: {
        every: "month", on: "last", lane: "Release", until: "2026-12-31",
      },
      releases: ["2026-09-30", "2026-12-31"],
    }} history={[]} locale="en" t={(x) => x} zoom={100} />);
    return far.includes("2026-12-31") || far.toLowerCase().includes("dec");
  })());

// verifies: REQ-PLANHORIZON-1010#CASE-3
test("cadence: a plan with only a cadence still draws its calendar",
  (() => {
    // The seeded shape: no bars, no milestone dues, no history. It used
    // to render the "add milestones or bars" dead end — the empty case
    // being the one with nothing to look at, which is backwards for a
    // repo that has planned nothing yet.
    const bare = renderToString(<PlanGantt planning={{
      lanes: ["Feature", "Bug", "Release"],
      cadence: { every: "month", on: "last", lane: "Release" },
      milestones: {}, bars: [],
      releases: ["2026-09-30", "2026-10-31", "2026-11-30", "2026-12-31"],
    }} history={[]} locale="en" t={(x) => x} zoom={100} />);
    return !bare.includes("Add milestones with due dates")
      && bare.includes("Feature") && bare.includes("Release");
  })());

// verifies: REQ-PLANBRANCH-1011#CASE-4
test("roadmap: the shipped band is named by the branch",
  (() => {
    const hist = [{ month: "2026-06", count: 2, first: "2026-06-01",
                    last: "2026-06-30",
                    versions: ["v1.0.0"], landmark: "v1.0.0",
                    headline: "first" }];
    const named = renderToString(
      <PlanGantt planning={{ lanes: ["Feature"], bars: [] }}
        history={hist} branch="feat/plan-bar-note" locale="en"
        t={(x) => x} zoom={100} />);
    const bare = renderToString(
      <PlanGantt planning={{ lanes: ["Feature"], bars: [] }}
        history={hist} locale="en" t={(x) => x} zoom={100} />);
    // a branch shows its own name; no branch keeps the former label
    // rather than a blank
    return named.includes("feat/plan-bar-note") && !named.includes(">Shipped<")
      && bare.includes("Shipped");
  })());

// ---- overlapping short bars ------------------------------------------------
// tested-by: REQ-PLANSTACK-1012 @unit
// Two ONE-DAY bars on consecutive days. Widening the day took week-long
// bars out of the floor entirely, so the case that remains is the short
// one: a single day draws PX - 6 and is floored to 30, while the next day
// starts PX along — 22px at today's scale, so dates say no overlap and
// pixels say 8px of it. The two helper checks below pin stackBars at
// the older 11px scale, where the same pair overlaps by 19px.
const stackPlan = {
  lanes: ["Feature"],
  bars: [
    { title: "primul lucru cu titlu lung", lane: "Feature",
      start: "2026-09-21", end: "2026-09-21" },
    { title: "al doilea lucru", lane: "Feature", start: "2026-09-22",
      end: "2026-09-22" },
  ],
};
// verifies: REQ-PLANSTACK-1012#CASE-1
test("gantt: two one-day bars on consecutive days take separate rows",
  (() => {
    const a = { startIdx: 0, endIdx: 0 }, b = { startIdx: 1, endIdx: 1 };
    const extent = (x) => ({
      left: x.startIdx * 11 + 3,
      width: Math.max((x.endIdx - x.startIdx + 1) * 11 - 6, 30),
    });
    // dates say "no overlap"; pixels say otherwise, and pixels are what
    // is painted
    const rows = stackBars([a, b], extent);
    const rowsByDate = stackBars([{ ...a }, { ...b }]);
    return rows === 2 && rowsByDate === 1;
  })());

// verifies: REQ-PLANSTACK-1012#CASE-2
test("gantt: bars that really are apart still share one row",
  (() => {
    // a full week each, a week apart: 71px of bar, 77px between starts,
    // no clash at all — which is what widening the day bought, and the
    // stacker must not invent a row for it
    const a = { startIdx: 0, endIdx: 6 }, b = { startIdx: 7, endIdx: 13 };
    const extent = (x) => ({
      left: x.startIdx * 11 + 3,
      width: Math.max((x.endIdx - x.startIdx + 1) * 11 - 6, 30),
    });
    return stackBars([a, b], extent) === 1;
  })());

// verifies: REQ-PLANSTACK-1012#CASE-1
test("gantt: the chart itself stacks them, not just the helper",
  (() => {
    // The two checks above exercise stackBars directly, so they stay
    // green even if PlanGantt forgets to hand it `extent` — which is the
    // whole fix. This asserts the WIRING: render the clashing pair and
    // read the two bars' `top` out of the markup.
    const html = renderToString(<PlanGantt planning={stackPlan} history={[]}
      locale="en" t={(x) => x} zoom={100} />);
    // React SSR writes inline styles as `top:10px`, no space, so the
    // probe is a plain substring: with both bars on row 0 the markup
    // carries `top:10px` twice and `top:36px` (PAD + ROW_H) not at all.
    // PAD 10 + ROW_H 58
    const secondRow = (html.match(/top:68px/g) || []).length;
    if (!secondRow) {
      console.log("   (bars share a row — stacking not wired)");
    }
    return secondRow >= 1;
  })());

// verifies: REQ-PLANSTACK-1012#CASE-6
test("gantt: a title too long for its bar runs beside it, and is packed",
  (() => {
    // four releases on four consecutive days, one bar each: every bar
    // keeps its date width, every title is whole, and no two footprints
    // on one row meet
    const days = [0, 1, 2, 3].map((i) => {
      const bar = { startIdx: i, endIdx: i, title: `v1.0.${i} · Export` };
      return { ...bar, labelW: besideLabelWidth(bar) };
    });
    stackBars(days, footprint);
    const whole = days.every((b) => extent(b).width === Math.max(PX - 6, 30)
      && b.labelW >= Math.ceil(b.title.length * PLAN_CHAR));
    const clear = days.every((a) => days.every((b) => a === b
      || a.subRow !== b.subRow
      || footprint(a).left + footprint(a).width <= footprint(b).left
      || footprint(b).left + footprint(b).width <= footprint(a).left));
    // a two-week bar wraps its long title inside itself, as it always has
    const long = { startIdx: 0, endIdx: 13, title: "x ".repeat(60).trim() };
    const html = renderToString(<PlanGantt planning={stackPlan} history={[]}
      locale="en" t={(x) => x} zoom={100} />);
    return whole && clear && besideLabelWidth(long) === 0
      && html.includes("data-beside");
  })());

// verifies: REQ-PLANSTACK-1012#CASE-3
test("gantt: the guides mark the work, not today or the milestones",
  (() => {
    const html = renderToString(<PlanGantt planning={{
      ...stackPlan,
      milestones: { "v9.9": { due: "2026-09-30" } },
    }} history={[]} locale="en" t={(x) => x} zoom={100} />);
    // the milestone keeps its header pill; what goes is the full-height
    // dashed rule
    return html.includes("v9.9") && !html.includes("dashed var(--indigo-400)");
  })());

// verifies: REQ-PLANSTACK-1012#CASE-3
test("gantt: a guide runs from its day on the ruler down to its bar, "
  + "and stops there",
  (() => {
    // Drawn the full height of the chart, a guide crossed every lane
    // below its bar. It now starts at the ruler's bottom edge (HEAD_H =
    // 22 + 26 + 16 + 16) and ends at the bar's top: PAD 10 into the
    // first lane, so a guide in the second lane (Fix) would be longer.
    const html = renderToString(
      <PlanGantt planning={{ ...stackPlan, lanes: ["Feature", "Fix"] }}
        history={[]} locale="en" t={(x) => x} zoom={100} />);
    const guides = html.match(/data-guide="(start|end)" style="[^"]*"/g) || [];
    return guides.length === 4
      && guides.every(
        (g) => g.includes("top:80px") && /height:(10|68)px/.test(g));
  })());

// verifies: REQ-PLANSTACK-1012#CASE-3
test("gantt: a version's guide runs from its due day to its pill",
  (() => {
    const html = renderToString(<PlanGantt planning={{
      lanes: ["Feature", "Release"], bars: [],
      cadence: { every: "week", on: "friday", lane: "Release" },
      releases: ["2026-09-25"],
      milestones: { "v9.8.0": { due: "2026-09-25" } } }}
      history={[]} locale="en" t={(x) => x} zoom={100} />);
    const g = (html.match(/data-guide="version" style="[^"]*"/g)
      || [])[0] || "";
    // Feature lane 78px, then half the Release lane (39) minus half the
    // pill (11)
    return g.includes("top:80px") && g.includes("height:106px");
  })());

// verifies: REQ-PLANSTACK-1012#CASE-5
test("gantt: the guides are dotted and drawn under the bars",
  (() => {
    // Drawn last with a z-index, a solid guide crossed every title it
    // passed through. Positioned siblings with no z-index paint in DOM
    // order, so a guide written before the first bar paints under it.
    const html = renderToString(<PlanGantt planning={stackPlan}
      history={[]} locale="en" t={(x) => x} zoom={100} />);
    const guides = html.match(/data-guide="[a-z]+" style="[^"]*"/g) || [];
    const firstBar = html.indexOf("primul lucru");
    // A translucent bar let the guides and month rules under it show
    // through its title.
    const bars = html.match(/<div title="[^"]*" style="[^"]*"/g) || [];
    return guides.length === 4
      && guides.every((g) => g.includes("dotted") && !g.includes("z-index"))
      && html.lastIndexOf("data-guide=") < firstBar
      && bars.length === 2
      && bars.every((b) => /background:[^;]*var\(--surface\)(;|")/.test(b));
  })());

// ---- milestones due close together (REQ-VIEWER-1087) ------------------------
// tested-by: REQ-VIEWER-1087 @unit
const closeMilestones = {
  "v1.10.0": { due: "2026-09-22" }, "v1.11.0": { due: "2026-09-24" },
  "v1.12.0": { due: "2026-09-25" }, "v1.15.0": { due: "2026-10-02" },
};

// verifies: REQ-VIEWER-1087#CASE-1
test("gantt: release-lane pills due close together take separate rows",
  (() => {
    const html = renderToString(<PlanGantt planning={{
      lanes: ["Feature", "Release"], bars: [],
      cadence: { every: "week", on: "friday", lane: "Release" },
      releases: ["2026-09-25"], milestones: closeMilestones }}
      history={[]} locale="en" t={(x) => x} zoom={100} />);
    const tops = Object.keys(closeMilestones).map((ms) => {
      const m = html.match(new RegExp(
        `data-version="${ms.replace(/\./g, "\\.")}"[^>]*top:(-?[\\d.]+)px`));
      return m ? m[1] : null;
    });
    // every pill drawn, and the three due within one pill's width sit on
    // three different rows
    return tops.every((x) => x !== null)
      && new Set(tops.slice(0, 3)).size === 3;
  })());

// verifies: REQ-VIEWER-1087#CASE-2
test("gantt: ruler pills due close together become one pill naming each",
  (() => {
    const html = renderToString(<PlanGantt planning={{
      lanes: ["Feature"], bars: [], milestones: closeMilestones }}
      history={[]} locale="en" t={(x) => x} zoom={100} />);
    return html.includes('data-flag="v1.10.0 · v1.11.0 · v1.12.0"')
      && html.includes('data-flag="v1.15.0"');
  })());

// verifies: REQ-VIEWER-1087#CASE-3
test("gantt: one milestone keeps its pill where it always was", (() => {
  const html = renderToString(<PlanGantt planning={{
    lanes: ["Feature", "Release"], bars: [],
    cadence: { every: "week", on: "friday", lane: "Release" },
    releases: ["2026-09-25"], milestones: { "v9.8.0": { due: "2026-09-25" } } }}
    history={[]} locale="en" t={(x) => x} zoom={100} />);
  // a Release lane of 78px: 39 - 11
  return /data-version="v9\.8\.0"[^>]*top:28px/.test(html);
})());

test("gantt: the lane column sticks while the chart scrolls sideways",
  // verifies: REQ-PLANSTACK-1012#CASE-4
  (() => {
    // A scroll cannot be rendered on the server, so this asserts the two
    // conditions it depends on: the lane column is sticky at the left
    // edge, and the bordered box that holds it declares no overflow —
    // an ancestor that does becomes the scrollport, and a scrollport
    // that never scrolls never lets its sticky child stick.
    const html = renderToString(<PlanGantt planning={stackPlan} history={[]}
      locale="en" t={(x) => x} zoom={100} />);
    const box = (html.match(
      /<div style="display:flex;border:1px solid[^"]*"/) || [""])[0];
    return html.includes("position:sticky;left:0") && box !== ""
      && !box.includes("overflow");
  })());

export const cadencePlan = {
  lanes: ["Engine"],
  bars: [
    { title: "a bar", lane: "Engine", start: "2026-09-13", end: "2026-09-30" },
  ],
  cadence: { every: "week", on: "friday", lane: "Release" },
  releases: ["2026-09-18", "2026-09-25"],
};
const withCadence = renderToString(
  <PlanGantt planning={cadencePlan} locale="en" t={(s) => s} zoom={100}
             openSpec={noop} />);
const noCadence = renderToString(
  <PlanGantt
    planning={{ ...cadencePlan, cadence: undefined, releases: undefined }}
    locale="en" t={(s) => s} zoom={100} openSpec={noop} />);
const cadenceChecks = [
  // verifies: REQ-PLANCADENCE-1000#CASE-1
  ["cadence: a rule is drawn for every emitted release date",
    (withCadence.match(/release · 2026-09-/g) || []).length === 2],
  // verifies: REQ-PLANCADENCE-1000#CASE-1
  ["cadence: a release is a tick on the ruler, not a line through the lanes",
    // A weekly cadence drew one full-height rule per Friday across
    // every lane, ruling through the bars it was meant to date. The
    // ruler tick carries the same date.
    !withCadence.includes(
      "color-mix(in oklch, var(--fg-faint) 45%, transparent)")],
  // verifies: REQ-PLANCADENCE-1000#CASE-1
  ["cadence: a version is drawn in the release lane, and a date with no "
    + "version draws nothing there",
    (() => {
      const html = renderToString(<PlanGantt planning={{
        ...cadencePlan, lanes: ["Engine", "Release"],
        milestones: { "v9.8.0": { due: "2026-09-25" } } }}
        locale="en" t={(s) => s} zoom={100} openSpec={noop} />);
      return html.includes('data-version="v9.8.0"')
        && !html.includes("rotate(45deg)");
    })()],
  // verifies: REQ-PLANCADENCE-1000#CASE-2
  ["cadence: no releases means no rules",
    !noCadence.includes("release · ")],
  // verifies: REQ-PLANCADENCE-1000#CASE-1
  ["cadence: the chart places the emitted dates and computes none",
    // 2026-09-20 is a Sunday, so a viewer doing its own Friday
    // arithmetic could not produce it. It renders because it was in
    // the list.
    renderToString(
      <PlanGantt planning={{ ...cadencePlan, releases: ["2026-09-20"] }}
                 locale="en" t={(s) => s} zoom={100} openSpec={noop} />)
      .includes("release · 2026-09-20")],
];
for (const [label, ok] of cadenceChecks) test(label, ok);

// tested-by: REQ-PLANDAYS-1021 @unit
// verifies: REQ-PLANDAYS-1021#CASE-1
test("gantt: each day under the weeks is labelled day/month",
  (() => {
    // Monday 14 September
    const bands = buildDayBands(new Date(2026, 8, 14, 12), 7);
    const html = renderToString(
      <PlanGantt planning={cadencePlan} locale="en" t={(s) => s}
                 zoom={100} openSpec={noop} />);
    return bands.map((b) => b.label).join(" ")
      === "14/9 15/9 16/9 17/9 18/9 19/9 20/9"
      && bands[5].weekend && bands[6].weekend && !bands[4].weekend
      && html.includes('data-day="15/9"') && html.includes('data-day="16/9"');
  })());

// verifies: REQ-PLANDAYS-1021#CASE-2
test("gantt: today stands out and a weekend recedes",
  (() => {
    const today = dayStyle({ start: 4, weekend: false }, 4);
    const friday = dayStyle({ start: 11, weekend: false }, 4);
    const saturday = dayStyle({ start: 5, weekend: true }, 4);
    return today.color === "var(--accent-2)" && friday.color !== today.color
      && saturday.color !== friday.color && saturday.color.includes("55%")
      && saturday.background !== "none";
  })());

// verifies: REQ-PLANDAYS-1021#CASE-3
test("gantt: the day row spans the chart",
  (() => {
    const html = renderToString(
      <PlanGantt planning={cadencePlan} locale="en" t={(s) => s}
                 zoom={100} openSpec={noop} />);
    const cells = (html.match(/data-day="/g) || []).length;
    return cells >= 14
      && cells === new Set(html.match(/data-day="[^"]+"/g)).size;
  })());

// ---- selecting a shipped month or a version opens what is in it -----------
// tested-by: REQ-HISTORY-1081
// verifies: REQ-HISTORY-1081#CASE-4
test("gantt: a shipped month and a version are selectable",
  (() => {
    const hist = [{ month: "2026-08", count: 2, first: "2026-08-03",
                    last: "2026-08-20",
                    versions: ["v2.28.0", "v2.29.0"], landmark: "v2.29.0",
                    headline: "x",
                    entries: [
                      { version: "v2.29.0", date: "2026-08-20",
                        headline: "Ten findings fixed",
                        first_commit: "2026-08-15",
                        last_commit: "2026-08-20" },
                      { version: "v2.28.0", date: "2026-08-03",
                        headline: "The viewer splits",
                        first_commit: "2026-08-01",
                        last_commit: "2026-08-03" },
                    ] }];
    const html = renderToString(<PlanGantt planning={{
      lanes: ["Feature", "Release"],
      cadence: { every: "week", on: "friday", lane: "Release" },
      releases: ["2026-09-25"],
      milestones: { "v9.8.0": { due: "2026-09-25" } }, bars: [] }}
      history={hist} locale="en" t={(x) => x} zoom={100} />);
    return /data-release="v2.29.0" role="button" tabindex="0"/.test(html)
      && /data-release="v2.28.0"/.test(html)
      && /data-version="v9.8.0" role="button" tabindex="0"/.test(html);
  })());

// verifies: REQ-HISTORY-1081#CASE-4
test("gantt: an opened release shows what it did and both commit dates",
  (() => {
    const html = renderToString(
      <ReleaseNote t={(x) => x} onClose={noop} release={{
        version: "v2.29.0", headline: "Ten findings fixed",
        start: "2026-08-15", end: "2026-08-20",
        body: "**Ten findings fixed.**\n\nThe gate names the six." }} />);
    return html.includes("Ten findings fixed")
      && html.includes("first commit 2026-08-15")
      && html.includes("last commit 2026-08-20")
      && html.includes("data-entry-body")
      && html.includes("The gate names the six");
  })());

// A month lists its releases in a short contents list, then every release
// unfolded under it; an entry renders as
// subtitles, nested lists and paragraphs, with no Markdown syntax left and
// no second copy of the headline the row already shows.
const SECTIONED = "**Sections land.**\n\nIntro with `a flag`.\n\n### Parser\n\n"
  + "- **Lead.** first\n  - nested\n- second\n\n### Docs\n\n- one more";
const FLAT = "**Flat entry.** Its own words.\n\n- a bullet\n  wrapped on";
// verifies: REQ-HISTORY-1081#CASE-4
test("gantt: a month shows contents, then every release's whole entry",
  (() => {
    const note = renderToString(
      <ShippedNote t={(x) => x} onClose={noop} month={{
        month: "2026-05", count: 2, first: "2026-05-02", last: "2026-05-14",
        entries: [
          { version: "v3.2.0", date: "2026-05-14", headline: "Sections land",
            body: SECTIONED },
          { version: "v3.1.0", date: "2026-05-02", headline: "No body" },
        ] }} />);
    const one = renderToString(
      <EntryBody body={SECTIONED} headline="Sections land" />);
    const two = renderToString(
      <EntryBody body={FLAT} headline="Flat entry" />);
    const clipped = renderToString(
      <EntryBody body={"**" + "alpha ".repeat(12) + "end.**\n\nAfter."}
                 headline={"alpha ".repeat(8).trim() + "…"} />);
    const clean = (h) => !h.includes("**") && !h.includes("`");
    return (note.match(/data-entry-body/g) || []).length === 1
      && (note.match(/data-release=/g) || []).length === 2
      && note.indexOf("data-contents") > -1
      && note.indexOf("data-contents") < note.indexOf("data-entry-body")
      && !note.includes("aria-expanded") && clean(one) && clean(two)
      && /max-height:\s*65vh/.test(note) && /overflow-y:\s*auto/.test(note)
      && /<h4[^>]*>Parser<\/h4>/.test(one) && one.includes("<h4")
      && /<strong>Lead\.<\/strong> first<ul[^>]*><li>nested<\/li>/.test(one)
      && /<code[^>]*>a flag<\/code>/.test(one)
      && !one.includes("Sections land") && one.includes("Intro with")
      && !two.includes("<h4") && !two.includes("Flat entry")
      && two.includes("Its own words.") && two.includes("a bullet wrapped on")
      && !clipped.includes("end.") && clipped.includes("After.");
  })());

// verifies: REQ-PLANCADENCE-1000#CASE-1
test("gantt: an opened version lists the work planned on it",
  (() => {
    const bars = [
      { key: "a", title: "on it", milestone: "v9.8.0", start: "2026-09-21",
        end: "2026-09-25" },
      { key: "b", title: "elsewhere", milestone: "v9.9.0",
        start: "2026-09-28", end: "2026-10-02" },
    ];
    const version = { ms: "v9.8.0", due: "2026-09-25", label: "L" };
    const html = renderToString(<VersionNote version={version}
      bars={bars} t={(x) => x} onClose={noop} onPickBar={noop} />);
    return html.includes("on it") && !html.includes("elsewhere")
      && html.includes("2026-09-25");
  })());
// ---- ISO week header ------------------------------------------------------
// The week row is labelled with the week OF THE YEAR, not a count from
// the chart's left edge: the same calendar week has to read the same in
// two charts and in a conversation about it. 2026-09-13 is a Sunday, so
// it closes W37 alone and the next band is a full W38.
const weekChecks = [
  ["gantt: the header carries ISO week-of-year labels, not a count from "
    + "the left edge",
    withCadence.includes(">W37<") && withCadence.includes(">W38<")],
  ["gantt: a range starting mid-week keeps the real week number, not W1",
    !withCadence.includes(">W1<")],
];
for (const [label, ok] of weekChecks) test(label, ok);
