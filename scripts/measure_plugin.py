#!/usr/bin/env python3
"""Print comparable UTF-8 artifact sizes without rewriting any file."""
# implements: ARCH-SELFGATE-039
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugin" / "scripts"))
from reqmap_engine.viewer import _inject_viewer


def measure():
    # implements: ARCH-SELFGATE-039
    reqs = ROOT / "plugin" / "requirements"
    scripts = ROOT / "plugin" / "scripts"
    skill = ROOT / "plugin" / "skills" / "requirement-manager"
    data = json.loads((reqs / "_map.json").read_text(encoding="utf-8"))
    template = (scripts / "_map_viewer.html").read_text(encoding="utf-8")
    return {
        "map_md_bytes": (reqs / "_map.md").stat().st_size,
        "map_json_bytes": (reqs / "_map.json").stat().st_size,
        "offline_html_bytes": len(
            _inject_viewer(template, data).encode("utf-8")),
        "skill_entry_bytes": sum((skill / n).stat().st_size for n in
                                 ("SKILL.md", "SKILL.universal.md")),
        "skill_bundle_bytes": sum(p.stat().st_size for p in skill.rglob("*.md")),
        "requirement_count": len(data["nodes"]),
    }


if __name__ == "__main__":
    print(json.dumps(measure(), indent=2))
