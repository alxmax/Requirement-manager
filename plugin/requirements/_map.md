---
generated: 2026-06-05 17:33
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
  f_scripts_test_reqmap_py_47_837["scripts/test_reqmap.py:47-837"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_837
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_142_179["scripts/reqmap.py:142-179"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_142_179
  f_scripts_test_reqmap_py_146["scripts/test_reqmap.py:146"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_146
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_656_803["scripts/reqmap.py:656-803"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_656_803
  f_scripts_test_reqmap_py_487_945["scripts/test_reqmap.py:487-945"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_487_945
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_245_294["scripts/reqmap.py:245-294"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_245_294
  f_scripts_test_reqmap_py_93_995["scripts/test_reqmap.py:93-995"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_995
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_493_639["scripts/reqmap.py:493-639"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_493_639
  f_scripts_test_reqmap_py_194_395["scripts/test_reqmap.py:194-395"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_194_395
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_909_996["scripts/reqmap.py:909-996"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_909_996
  f_scripts_test_reqmap_py_560_928["scripts/test_reqmap.py:560-928"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_560_928
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1235_1264["scripts/reqmap.py:1235-1264"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1235_1264
  f_scripts_test_reqmap_py_1282["scripts/test_reqmap.py:1282"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1282
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1031_1768["scripts/reqmap.py:1031-1768"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1031_1768
  f_scripts_test_reqmap_py_237_1086["scripts/test_reqmap.py:237-1086"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_237_1086
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_423["scripts/reqmap.py:423"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_423
  f_scripts_test_reqmap_py_429["scripts/test_reqmap.py:429"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_429
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1109_1119["scripts/reqmap.py:1109-1119"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1109_1119
  f_scripts_test_reqmap_py_1191["scripts/test_reqmap.py:1191"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1191
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_444_459["scripts/reqmap.py:444-459"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_444_459
  f_scripts_test_reqmap_py_1131["scripts/test_reqmap.py:1131"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1131
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_258["scripts/reqmap.py:258"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_258
  f_scripts_test_reqmap_py_473["scripts/test_reqmap.py:473"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_473
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
