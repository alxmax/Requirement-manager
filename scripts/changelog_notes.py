#!/usr/bin/env python3
"""Print the CHANGELOG.md section for one plugin version — the release notes.

Usage: python scripts/changelog_notes.py 2.13.0   (reads ./CHANGELOG.md)

The release-automation CI job (`.github/workflows/ci.yml`, job `release`) feeds
this to `gh release create --notes-file`, so a tagged release carries exactly the
CHANGELOG prose for its version — one source of truth for the notes, no drift.
Exit 1 when there is no matching `## plugin` heading for the version (the same
heading the version-bump gate requires), so a bump without notes never releases.
"""
import sys


def extract(text, version):
    """Return the CHANGELOG body for `version`: the `## plugin` heading carrying
    `vX.Y.Z` through to (but not including) the next `## plugin` heading, stripped.
    None if the version has no section."""
    marker = "`v{}`".format(version)
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("## plugin") and marker in ln:
            start = i
            break
    if start is None:
        return None
    out = [lines[start]]
    for ln in lines[start + 1:]:
        if ln.startswith("## plugin"):
            break
        out.append(ln)
    return "\n".join(out).strip()


def main(argv):
    """Print the CHANGELOG section for the version named in `argv`, and return an
    exit code — non-zero when there is no such section."""
    # CHANGELOG prose carries non-ASCII (em-dashes, the `→` in the version note).
    # Force UTF-8 so a legacy Windows codepage doesn't crash on print — same guard
    # reqmap.py's main() uses. Best-effort: reconfigure() is 3.7+ and may be absent.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass
    if len(argv) != 2:
        print("usage: changelog_notes.py <version>", file=sys.stderr)
        return 2
    with open("CHANGELOG.md", encoding="utf-8") as f:
        section = extract(f.read(), argv[1])
    if section is None:
        print("no CHANGELOG.md section for v{}".format(argv[1]), file=sys.stderr)
        return 1
    print(section)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
