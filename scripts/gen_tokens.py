#!/usr/bin/env python3
# implements: ARCH-SELFGATE-039
"""Colour tokens -> the two surfaces that render them (dev/CI tooling — NOT part
of the seeded engine).

`design/tokens.json` is the source. Two files declare the same colours and used
to do so independently:

  app/src/styles/colors_and_type.css           the Vite viewer, three themes
  plugin/scripts/reqmap_engine/site_template.py  the project site `sync` emits

They had drifted to different accents — ink blue in one, terracotta in the other
— with no shared name between them, so nothing could notice. This script writes
both from the one source, between `##TOKENS:KEY##` markers, in the same spirit as
the engine's own `<!--##REQMAP:KEY##-->` regions: everything outside a marker is
authored prose and is preserved byte for byte.

  python scripts/gen_tokens.py            rewrite the regions
  python scripts/gen_tokens.py --check    fail if a region is out of date (CI)

The engine stays hermetic: nothing here runs at engine time, and site_template.py
remains a plain string literal with no imports added.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "design", "tokens.json")
CSS = os.path.join(ROOT, "app", "src", "styles", "colors_and_type.css")
SITE = os.path.join(ROOT, "plugin", "scripts", "reqmap_engine", "site_template.py")

ALIAS = re.compile(r"^\{([A-Za-z0-9-]+)\}$")


# --------------------------------------------------------------------- source
def load():
    with open(SOURCE, encoding="utf-8") as fh:
        doc = json.load(fh)
    toks = doc["tokens"]
    for name, tok in toks.items():
        if "light" not in tok["value"]:
            raise SystemExit("tokens.json: %s has no light value" % name)
        for theme, raw in tok["value"].items():
            m = ALIAS.match(raw)
            if m and m.group(1) not in toks:
                raise SystemExit(
                    "tokens.json: %s[%s] aliases {%s}, which is not a token"
                    % (name, theme, m.group(1)))
            if m and m.group(1) == name:
                raise SystemExit("tokens.json: %s aliases itself" % name)
    return doc


def resolve(toks, name, theme, seen=()):
    """The literal a theme ends up with, following aliases and the light fallback."""
    if name in seen:
        raise SystemExit("tokens.json: alias cycle through %s" % name)
    raw = toks[name]["value"].get(theme) or toks[name]["value"]["light"]
    m = ALIAS.match(raw)
    return resolve(toks, m.group(1), theme, seen + (name,)) if m else raw


# ----------------------------------------------------------------- emitters
def css_value(raw):
    """{other} is how tokens.json spells an alias; CSS spells it var(--other)."""
    m = ALIAS.match(raw)
    return "var(--%s)" % m.group(1) if m else raw


def _decl(name, value, note, width):
    line = "  --%s:%s%s;" % (name, " " * max(1, width - len(name)), value)
    if isinstance(note, str):
        return [line + "  /* %s */" % note]
    if note:
        out = ["  /* %s" % note[0]]
        out += ["     %s" % n for n in note[1:-1]]
        out += ["     %s */" % note[-1]] if len(note) > 1 else []
        return out + [line]
    return [line]


def css_block(toks, theme, notes):
    width = max(len(n) for n in toks) + 2
    out, first = [], True
    for name, tok in toks.items():
        if theme != "light" and theme not in tok["value"]:
            continue
        if notes and "section" in tok:
            out += ([""] if not first else []) + [
                "  /* ---- %s %s */" % (tok["section"], "-" * max(3, 64 - len(tok["section"])))]
        out += _decl(name, css_value(tok["value"].get(theme, tok["value"]["light"])),
                     tok.get("note") if notes else None, width)
        first = False
    return out


def css_regions(doc):
    toks = doc["tokens"]
    hc = ["[data-theme=\"hc\"] {"] + css_block(toks, "hc", False) + ["}"]
    media = (["@media (prefers-contrast: more) {",
              "  :root:not([data-theme=\"dark\"]):not([data-theme=\"hc\"]) {"]
             + ["  " + l if l else l for l in css_block(toks, "hc", False)]
             + ["  }", "}"])
    return {
        "LIGHT": css_block(toks, "light", True),
        "DARK": css_block(toks, "dark", False),
        "HC": hc + [""] + media,
    }


def site_region(doc):
    """The engine site's own six colour properties, resolved to literals."""
    toks, mapping = doc["tokens"], doc["site"]["map"]
    def line(theme, indent):
        parts = []
        for prop, ref in mapping.items():
            m = ALIAS.match(ref)
            val = resolve(toks, m.group(1), theme) if m else ref
            parts.append("--%s:%s;" % (prop, val))
        wrapped, cur = [], indent
        for p in parts:
            if len(cur) + len(p) + 1 > 76 and cur.strip():
                wrapped.append(cur.rstrip()); cur = indent
            cur += p + " "
        wrapped.append(cur.rstrip())
        return wrapped
    return (["  :root{"] + line("light", "    ") + ["    --radius:12px; --maxw:980px;", "  }",
             "  @media (prefers-color-scheme: dark){:root{"]
            + line("dark", "    ") + ["  }}"])


# ------------------------------------------------------------------- regions
def splice(text, key, body, nl):
    open_m, close_m = "/*##TOKENS:%s##*/" % key, "/*##/TOKENS:%s##*/" % key
    i, j = text.find(open_m), text.find(close_m)
    if i < 0 or j < 0:
        raise SystemExit("marker ##TOKENS:%s## missing" % key)
    if j < i:
        raise SystemExit("markers for %s are in the wrong order" % key)
    # keep whatever indentation the closing marker was written with
    line_start = text.rfind(nl, 0, j)
    indent = text[line_start + len(nl):j] if line_start >= 0 else text[:j]
    if indent.strip():
        indent = ""
    return text[:i + len(open_m)] + nl + nl.join(body) + nl + indent + text[j:]


def apply_to(path, regions, check):
    with open(path, encoding="utf-8", newline="") as fh:
        before = fh.read()
    nl = "\r\n" if "\r\n" in before else "\n"
    after = before
    for key, body in regions.items():
        after = splice(after, key, body, nl)
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if after == before:
        print("  ok        %s" % rel)
        return True
    if check:
        print("  STALE     %s" % rel)
        return False
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(after)
    print("  written   %s" % rel)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if a generated region is out of date; write nothing")
    args = ap.parse_args()

    doc = load()
    print("design/tokens.json: %d colour tokens, %d themes"
          % (len(doc["tokens"]), len(doc["themes"])))
    ok = apply_to(CSS, css_regions(doc), args.check)
    ok &= apply_to(SITE, {"SITE": site_region(doc)}, args.check)

    if not ok:
        print("\nA generated region does not match design/tokens.json.\n"
              "Edit design/tokens.json, then run: python scripts/gen_tokens.py",
              file=sys.stderr)
        return 1
    print("tokens are in sync." if args.check else "regions rewritten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
