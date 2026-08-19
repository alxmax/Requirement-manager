"""Compare app/src/lib/data.js's BAKED requirement fixture against the live
registry — a warn-only drift check wired into `gate` (implements: CORE-SCAN-002).
Stdlib only. Heuristic by design: compares requirement IDs present and a
normalized form of each one's `contract` list text, not a byte-exact diff.
"""
import re


_STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _normalize(strings):
    return sorted(" ".join(s.split()) for s in strings)


def _parse_baked(text):
    """{id: [contract strings]} extracted from data.js's BAKED array."""
    out = {}
    for m in re.finditer(r'id:"([A-Z][A-Z0-9-]+)"[^}]*?contract:\[(.*?)\]', text, re.S):
        rid, block = m.group(1), m.group(2)
        out[rid] = [s.replace('\\"', '"') for s in _STRING_RE.findall(block)]
    return out


def check_viewer_data_sync(data_js_path, map_nodes):  # implements: CORE-SCAN-002
    """Return a sorted list of requirement IDs where app/src/lib/data.js's BAKED
    fixture disagrees with map_nodes ([{"id":..., "contract":[...]}, ...]) — a
    missing id or differently-normalized contract text both count as drift.
    Returns None (not []) when data_js_path doesn't exist — fail-open, matching
    load_ignore()'s convention for an optional file."""
    try:
        with open(data_js_path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    baked = _parse_baked(text)
    live = {n["id"]: n.get("contract", []) for n in map_nodes}
    drift = []
    for rid, contract in baked.items():
        if rid not in live or _normalize(contract) != _normalize(live[rid]):
            drift.append(rid)
    return sorted(drift)
