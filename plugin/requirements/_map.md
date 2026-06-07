---
generated: 2026-06-07 19:33
nodes: 17
edges: 23
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
    REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
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
  f_scripts_test_reqmap_py_47_898["scripts/test_reqmap.py:47-898"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_898
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_142_179["scripts/reqmap.py:142-179"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_142_179
  f_scripts_test_reqmap_py_186["scripts/test_reqmap.py:186"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_186
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_667_814["scripts/reqmap.py:667-814"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_667_814
  f_scripts_test_reqmap_py_527_1006["scripts/test_reqmap.py:527-1006"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_527_1006
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_245_294["scripts/reqmap.py:245-294"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_245_294
  f_scripts_test_reqmap_py_93_1056["scripts/test_reqmap.py:93-1056"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_1056
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_504_650["scripts/reqmap.py:504-650"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_504_650
  f_scripts_test_reqmap_py_234_435["scripts/test_reqmap.py:234-435"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_234_435
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_920_1007["scripts/reqmap.py:920-1007"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_920_1007
  f_scripts_test_reqmap_py_600_989["scripts/test_reqmap.py:600-989"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_600_989
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1517["scripts/reqmap.py:1517"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1517
  f_scripts_test_reqmap_py_1698["scripts/test_reqmap.py:1698"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1698
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1629_1658["scripts/reqmap.py:1629-1658"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1629_1658
  f_scripts_test_reqmap_py_1369["scripts/test_reqmap.py:1369"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1369
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1261_1331["scripts/reqmap.py:1261-1331"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1261_1331
  f_scripts_test_reqmap_py_1555["scripts/test_reqmap.py:1555"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1555
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1042_2187["scripts/reqmap.py:1042-2187"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1042_2187
  f_scripts_test_reqmap_py_277_1147["scripts/test_reqmap.py:277-1147"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_277_1147
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_434["scripts/reqmap.py:434"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_434
  f_scripts_test_reqmap_py_469["scripts/test_reqmap.py:469"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_469
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1164_1174["scripts/reqmap.py:1164-1174"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1164_1174
  f_scripts_test_reqmap_py_1252_1362["scripts/test_reqmap.py:1252-1362"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1252_1362
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_455_470["scripts/reqmap.py:455-470"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_455_470
  f_scripts_test_reqmap_py_1192["scripts/test_reqmap.py:1192"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1192
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_258["scripts/reqmap.py:258"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_258
  f_scripts_test_reqmap_py_513["scripts/test_reqmap.py:513"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_513
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1361["scripts/reqmap.py:1361"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1361
  f_scripts_test_reqmap_py_1616["scripts/test_reqmap.py:1616"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1616
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1433_1480["scripts/reqmap.py:1433-1480"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1433_1480
  f_scripts_test_reqmap_py_1660["scripts/test_reqmap.py:1660"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1660
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>14 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```
