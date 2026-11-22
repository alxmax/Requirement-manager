/* Render smoke test, part: an opened month or version on the plan's Gantt:
 * what shipped, both commit dates, the whole changelog entry, the planned work
 * and the open TODO.md items. Split from plan.jsx, which runs just before. */
import { renderToString } from "react-dom/server";
import { HISTORY } from "../../src/lib/data.js";
import {
  PlanGantt, ReleaseNote, ShippedNote, VersionNote,
} from "../../src/views/roadmap/PlanGantt.jsx";
import { EntryBody } from "../../src/views/roadmap/EntryBody.jsx";
import { noop, test } from "./harness.jsx";
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

// tested-by: REQ-VERSIONTODOS-1097 @unit
// verifies: REQ-VERSIONTODOS-1097#CASE-1
test("gantt: an opened version lists its open TODO.md items, detail folded",
  (() => {
    const version = { ms: "v9.8.0", due: "2026-09-25", label: "L" };
    const todos = [
      { name: "open one", milestone: "v9.8.0", done: false,
        detail: "why it hurts\n  src/a.py:3" },
      { name: "open plain", milestone: "v9.8.0", done: false },
      { name: "closed one", milestone: "v9.8.0", done: true },
      { name: "elsewhere", milestone: "v9.9.0", done: false },
    ];
    const html = renderToString(<VersionNote version={version} bars={[]}
      todos={todos} t={(x) => x} onClose={noop} onPickBar={noop} />);
    return html.includes("open one") && html.includes("<details")
      && html.includes("why it hurts") && html.includes("open plain")
      && !html.includes("closed one") && !html.includes("elsewhere")
      && !html.includes("Nothing planned");
  })());
// verifies: REQ-VERSIONTODOS-1097#CASE-2
test("gantt: a version with no bars and no open items says nothing is planned",
  (() => {
    const html = renderToString(<VersionNote
      version={{ ms: "v9.8.0", due: "2026-09-25" }} bars={[]}
      todos={[{ name: "gone", milestone: "v9.8.0", done: true }]}
      t={(x) => x} onClose={noop} onPickBar={noop} />);
    return html.includes("Nothing planned") && !html.includes("gone");
  })());
// verifies: REQ-VERSIONTODOS-1097#CASE-3
test("gantt: an open item with no detail is a plain row, nothing to expand",
  (() => {
    const html = renderToString(<VersionNote
      version={{ ms: "v9.8.0", due: "2026-09-25" }} bars={[]}
      todos={[{ name: "plain item", milestone: "v9.8.0", done: false }]}
      t={(x) => x} onClose={noop} onPickBar={noop} />);
    return html.includes("plain item") && !html.includes("<details");
  })());
// ---- ISO week header ------------------------------------------------------
// The week row is labelled with the week OF THE YEAR, not a count from
// the chart's left edge: the same calendar week has to read the same in
// two charts and in a conversation about it. 2026-09-13 is a Sunday, so
// it closes W37 alone and the next band is a full W38.
