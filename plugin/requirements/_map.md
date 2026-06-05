---
generated: 2026-06-05 20:00
nodes: 13
edges: 16
---

# Requirement Map

## System Map

_Capabilities grouped by area; thick border = bus; arrows = `depends_on`. Edges into the bus/hubs are hidden (the Dependency Map shows area-level coupling)._

```mermaid
graph LR
  subgraph sg_CORE["CORE"]
    CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
    CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
    CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  end
  subgraph sg_REQ["REQ"]
    REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
    REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
    REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
    REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  end
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_NEXT_013 --> REQ_MAP_007
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_207_238["scripts/reqmap.py:207-238"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_207_238
  f_scripts_test_reqmap_py_103_116["scripts/test_reqmap.py:103-116"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_116
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_71_126["scripts/reqmap.py:71-126"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_71_126
  f_scripts_test_reqmap_py_47_861["scripts/test_reqmap.py:47-861"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_861
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_142_179["scripts/reqmap.py:142-179"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_142_179
  f_scripts_test_reqmap_py_186["scripts/test_reqmap.py:186"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_186
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_667_814["scripts/reqmap.py:667-814"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_667_814
  f_scripts_test_reqmap_py_527_969["scripts/test_reqmap.py:527-969"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_527_969
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_245_294["scripts/reqmap.py:245-294"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_245_294
  f_scripts_test_reqmap_py_93_1019["scripts/test_reqmap.py:93-1019"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_1019
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_504_650["scripts/reqmap.py:504-650"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_504_650
  f_scripts_test_reqmap_py_234_435["scripts/test_reqmap.py:234-435"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_234_435
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_920_1007["scripts/reqmap.py:920-1007"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_920_1007
  f_scripts_test_reqmap_py_600_952["scripts/test_reqmap.py:600-952"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_600_952
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1246_1275["scripts/reqmap.py:1246-1275"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1246_1275
  f_scripts_test_reqmap_py_1306["scripts/test_reqmap.py:1306"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1306
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1042_1772["scripts/reqmap.py:1042-1772"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1042_1772
  f_scripts_test_reqmap_py_277_1110["scripts/test_reqmap.py:277-1110"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_277_1110
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_434["scripts/reqmap.py:434"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_434
  f_scripts_test_reqmap_py_469["scripts/test_reqmap.py:469"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_469
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1120_1130["scripts/reqmap.py:1120-1130"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1120_1130
  f_scripts_test_reqmap_py_1215["scripts/test_reqmap.py:1215"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1215
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_455_470["scripts/reqmap.py:455-470"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_455_470
  f_scripts_test_reqmap_py_1155["scripts/test_reqmap.py:1155"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1155
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_258["scripts/reqmap.py:258"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_258
  f_scripts_test_reqmap_py_513["scripts/test_reqmap.py:513"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_513
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>10 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```
