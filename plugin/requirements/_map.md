---
generated: 2026-06-09 14:15
nodes: 22
edges: 29
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
    REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
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
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
    REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  end
  subgraph sg_misc["misc"]
    NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  end
  REQ_ACVERIFY_019 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_TESTLINK_018 --> REQ_CHECK_006
  REQ_TRACE_020 --> REQ_CHECK_006
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_275_309["scripts/reqmap.py:275-309"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_275_309
  f_scripts_test_reqmap_py_103_119["scripts/test_reqmap.py:103-119"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_119
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_83_138["scripts/reqmap.py:83-138"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_83_138
  f_scripts_test_reqmap_py_47_906["scripts/test_reqmap.py:47-906"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_906
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_154_191["scripts/reqmap.py:154-191"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_154_191
  f_scripts_test_reqmap_py_194["scripts/test_reqmap.py:194"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_194
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_218_449["scripts/reqmap.py:218-449"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_218_449
  f_scripts_test_reqmap_py_2058["scripts/test_reqmap.py:2058"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2058
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_822_969["scripts/reqmap.py:822-969"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_822_969
  f_scripts_test_reqmap_py_535_1031["scripts/test_reqmap.py:535-1031"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_535_1031
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_316_399["scripts/reqmap.py:316-399"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_316_399
  f_scripts_test_reqmap_py_93_1081["scripts/test_reqmap.py:93-1081"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_1081
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_659_805["scripts/reqmap.py:659-805"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_659_805
  f_scripts_test_reqmap_py_242_443["scripts/test_reqmap.py:242-443"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_242_443
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1075_1162["scripts/reqmap.py:1075-1162"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1075_1162
  f_scripts_test_reqmap_py_608_1014["scripts/test_reqmap.py:608-1014"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_608_1014
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1791["scripts/reqmap.py:1791"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1791
  f_scripts_test_reqmap_py_1940["scripts/test_reqmap.py:1940"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_1940
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_1903_1932["scripts/reqmap.py:1903-1932"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_1903_1932
  f_scripts_test_reqmap_py_1494["scripts/test_reqmap.py:1494"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1494
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1450_1580["scripts/reqmap.py:1450-1580"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1450_1580
  f_scripts_test_reqmap_py_1680["scripts/test_reqmap.py:1680"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1680
  REQ_MAP_007["Requirement map (Mermaid MD + JSON + self-contained viewer)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1197_2514["scripts/reqmap.py:1197-2514"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1197_2514
  f_scripts_test_reqmap_py_285_1204["scripts/test_reqmap.py:285-1204"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_285_1204
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_589["scripts/reqmap.py:589"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_589
  f_scripts_test_reqmap_py_477["scripts/test_reqmap.py:477"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_477
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1330_1343["scripts/reqmap.py:1330-1343"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1330_1343
  f_scripts_test_reqmap_py_1368_1487["scripts/test_reqmap.py:1368-1487"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1368_1487
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1303_2477["scripts/reqmap.py:1303-2477"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1303_2477
  f_scripts_test_reqmap_py_785_1205["scripts/test_reqmap.py:785-1205"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_785_1205
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_610_625["scripts/reqmap.py:610-625"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_610_625
  f_scripts_test_reqmap_py_1308["scripts/test_reqmap.py:1308"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1308
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_329["scripts/reqmap.py:329"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_329
  f_scripts_test_reqmap_py_521["scripts/test_reqmap.py:521"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_521
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1611["scripts/reqmap.py:1611"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1611
  f_scripts_test_reqmap_py_1814["scripts/test_reqmap.py:1814"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1814
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1693_1754["scripts/reqmap.py:1693-1754"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1693_1754
  f_scripts_test_reqmap_py_1878["scripts/test_reqmap.py:1878"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1878
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_379_441["scripts/reqmap.py:379-441"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_379_441
  f_scripts_test_reqmap_py_1994["scripts/test_reqmap.py:1994"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_1994
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_425_1646["scripts/reqmap.py:425-1646"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_425_1646
  f_scripts_test_reqmap_py_2128["scripts/test_reqmap.py:2128"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2128
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>18 caps</small>"]
  a_misc["misc<br><small>1 caps</small>"]
  a_REQ --> a_CORE
  style a_CORE stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```
