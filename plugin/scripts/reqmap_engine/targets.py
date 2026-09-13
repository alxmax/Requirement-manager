# implements: ARCH-MAP-007
"""Optional planning sidecar — score targets, milestone due dates, planned items.

Reads `requirements/_planning.json` first, then legacy `_targets.json`."""
import datetime
import json
import os
import re

PLANNING_FILES = ("_planning.json", "_targets.json")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_milestone_entry(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        return {"due": raw} if _DATE_RE.match(raw.strip()) else None
    if not isinstance(raw, dict):
        return None
    out = {}
    due = raw.get("due")
    if isinstance(due, str) and _DATE_RE.match(due.strip()):
        out["due"] = due.strip()
    label = raw.get("label") or raw.get("note")
    if isinstance(label, str) and label.strip():
        out["label"] = label.strip()
    items = raw.get("items")
    if isinstance(items, list):
        clean = [s.strip() for s in items if isinstance(s, str) and s.strip()]
        if clean:
            out["items"] = clean
    return out or None


def _parse_bar(raw):
    if not isinstance(raw, dict):
        return None
    title = raw.get("title") or raw.get("name")
    start = raw.get("start")
    end = raw.get("end") or raw.get("due")
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(start, str) or not _DATE_RE.match(start.strip()):
        return None
    if not isinstance(end, str) or not _DATE_RE.match(end.strip()):
        end = start
    out = {"title": title.strip(), "start": start.strip(), "end": end.strip()}
    lane = raw.get("lane")
    if isinstance(lane, str) and lane.strip():
        out["lane"] = lane.strip()
    ms = raw.get("milestone")
    if isinstance(ms, str) and ms.strip():
        out["milestone"] = ms.strip()
    rid = raw.get("req") or raw.get("reqId") or raw.get("id")
    if isinstance(rid, str) and rid.strip() and rid.strip() != out["title"]:
        out["req"] = rid.strip()
    prog = raw.get("progress")
    if isinstance(prog, (int, float)) and 0 <= prog <= 100:
        out["progress"] = int(round(prog))
    return out


# ---------- release cadence ----------
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
CADENCE_DEFAULTS = {"every": "week", "on": "friday", "lane": "Release"}
# A plan can span years; one marker per week over a decade is 520 vertical lines and an
# unreadable chart. The cap is a rendering limit, not a planning opinion — it truncates
# the tail and the count says so, rather than silently thinning the series.
CADENCE_MAX = 120


def _parse_cadence(raw):
    """Normalise the optional `cadence` block, or None when absent/unusable.

    Only `every: week` exists today. The field is still READ and validated so a plan
    written against a later engine degrades to no cadence instead of a wrong one — the
    configurator this is a placeholder for will add periods, not replace the key."""
    if raw is True:
        raw = {}
    if not isinstance(raw, dict):
        return None
    out = dict(CADENCE_DEFAULTS)
    every = raw.get("every")
    if isinstance(every, str) and every.strip().lower() not in ("week", "weekly"):
        return None
    on = raw.get("on")
    if isinstance(on, str) and on.strip().lower() in WEEKDAYS:
        out["on"] = on.strip().lower()
    lane = raw.get("lane")
    if isinstance(lane, str) and lane.strip():
        out["lane"] = lane.strip()
    for key in ("from", "until"):
        val = raw.get(key)
        if isinstance(val, str) and _DATE_RE.match(val.strip()):
            out[key] = val.strip()
    return out


def _plan_span(out):
    """(first, last) ISO dates the plan already covers, from its bars and milestone
    dues. Returns (None, None) when it covers nothing — a cadence needs something to
    run alongside, and inventing a span from today would put markers on an empty chart."""
    dates = []
    for bar in out.get("bars", []):
        dates.append(bar["start"])
        dates.append(bar["end"])
    for entry in out.get("milestones", {}).values():
        if entry.get("due"):
            dates.append(entry["due"])
    if not dates:
        return None, None
    return min(dates), max(dates)


def _release_dates(cadence, first, last):
    """Every `cadence["on"]` weekday from `first` through `last`, inclusive, as ISO
    strings. Computed HERE and emitted, not recomputed in the viewer: a second
    definition in JavaScript is how the CLI and the chart come to disagree about when
    a release lands."""
    start = cadence.get("from") or first
    end = cadence.get("until") or last
    if not start or not end or start > end:
        return []
    try:
        day = datetime.date(*(int(p) for p in start.split("-")))
        stop = datetime.date(*(int(p) for p in end.split("-")))
    except (TypeError, ValueError):
        return []
    target = WEEKDAYS.index(cadence["on"])
    day += datetime.timedelta(days=(target - day.weekday()) % 7)
    dates = []
    while day <= stop and len(dates) < CADENCE_MAX:
        dates.append(day.isoformat())
        day += datetime.timedelta(days=7)
    return dates


def _read_planning_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def load_targets(reqs_dir):
    """Parsed planning sidecar, or {} when absent or invalid (fail-open)."""
    raw = None
    for name in PLANNING_FILES:
        path = os.path.join(reqs_dir or ".", name)
        if os.path.isfile(path):
            raw = _read_planning_file(path)
            if raw is not None:
                break
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        return {}

    out = {}
    scores = raw.get("scores")
    if isinstance(scores, dict):
        clean = {}
        for key in ("health", "design"):
            val = scores.get(key)
            if isinstance(val, (int, float)) and 0 <= val <= 100:
                clean[key] = int(round(val))
        if clean:
            out["scores"] = clean

    milestones = raw.get("milestones")
    if isinstance(milestones, dict):
        clean_ms = {}
        for ms, entry in milestones.items():
            if not isinstance(ms, str) or not ms.strip():
                continue
            parsed = _parse_milestone_entry(entry)
            if parsed:
                clean_ms[ms.strip()] = parsed
        if clean_ms:
            out["milestones"] = clean_ms

    lanes = raw.get("lanes")
    if isinstance(lanes, list):
        clean_lanes = [s.strip() for s in lanes if isinstance(s, str) and s.strip()]
        if clean_lanes:
            out["lanes"] = clean_lanes

    bars = raw.get("bars")
    if isinstance(bars, list):
        clean_bars = []
        for entry in bars:
            parsed = _parse_bar(entry)
            if parsed:
                clean_bars.append(parsed)
        if clean_bars:
            out["bars"] = clean_bars

    # Last, because it needs the span the bars and milestones above define.
    # implements: REQ-PLANCADENCE-1000
    cadence = _parse_cadence(raw.get("cadence"))
    if cadence:
        first, last = _plan_span(out)
        dates = _release_dates(cadence, first, last)
        if dates:
            out["cadence"] = cadence
            out["releases"] = dates
    return out
