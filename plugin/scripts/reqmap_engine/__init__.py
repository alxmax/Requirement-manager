"""reqmap engine package. Holds the engine version and the on-disk anchor; imports nothing from the
package so any module may import it first.
"""
import os


# Bumped on any change to this engine. `check` warns a seeded repo when its
# vendored copy is older than the installed plugin's. ISO date with an optional
# `.N` same-day revision suffix (YYYY-MM-DD[.N]): lexicographic order ==
# chronological order, so a plain string compare is enough.
MAP_ENGINE_VERSION = "2026-09-08"  # implements: ARCH-CHECK-006 -- relevel.py tagged; site.py prints only flags the parser accepts

# The directory that holds reqmap.py and this package — the anchor every
# on-disk neighbour (the viewer template, the plugin manifest) is found from.
ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
