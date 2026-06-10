---
generated: 2026-06-10 22:37
nodes: 26
edges: 33
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
    REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
    REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
    REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
    REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
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
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_TESTLINK_018 --> REQ_CHECK_006
  REQ_TRACE_020 --> REQ_CHECK_006
  REQ_VIEWER_007 --> REQ_MAP_007
  style CORE_DRIFT_003 stroke-width:3px
  style CORE_PARSE_001 stroke-width:3px
  style CORE_SCAN_002 stroke-width:3px
```

## Requirement-to-Code

_Each requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected)._

```mermaid
graph LR
  CORE_DRIFT_003["Contract hashing & lock<br><small>CORE-DRIFT-003</small>"]
  f_scripts_reqmap_py_352_386["scripts/reqmap.py:352-386"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_352_386
  f_scripts_test_reqmap_py_103_136["scripts/test_reqmap.py:103-136"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_103_136
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_84_139["scripts/reqmap.py:84-139"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_84_139
  f_scripts_test_reqmap_py_47_947["scripts/test_reqmap.py:47-947"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_947
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_155_234["scripts/reqmap.py:155-234"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_155_234
  f_scripts_test_reqmap_py_213["scripts/test_reqmap.py:213"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_213
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_281_534["scripts/reqmap.py:281-534"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_281_534
  f_scripts_test_reqmap_py_2147["scripts/test_reqmap.py:2147"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2147
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_988_1135["scripts/reqmap.py:988-1135"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_988_1135
  f_scripts_test_reqmap_py_576_1072["scripts/test_reqmap.py:576-1072"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_576_1072
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_339_478["scripts/reqmap.py:339-478"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_339_478
  f_scripts_test_reqmap_py_93_2314["scripts/test_reqmap.py:93-2314"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_93_2314
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_825_971["scripts/reqmap.py:825-971"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_825_971
  f_scripts_test_reqmap_py_283_484["scripts/test_reqmap.py:283-484"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_283_484
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1241_1328["scripts/reqmap.py:1241-1328"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1241_1328
  f_scripts_test_reqmap_py_649_1055["scripts/test_reqmap.py:649-1055"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_649_1055
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_1998["scripts/reqmap.py:1998"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_1998
  f_scripts_test_reqmap_py_2007["scripts/test_reqmap.py:2007"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2007
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2119_2148["scripts/reqmap.py:2119-2148"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2119_2148
  f_scripts_test_reqmap_py_1535["scripts/test_reqmap.py:1535"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1535
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1621_1787["scripts/reqmap.py:1621-1787"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1621_1787
  f_scripts_test_reqmap_py_1721["scripts/test_reqmap.py:1721"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1721
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1363_2677["scripts/reqmap.py:1363-2677"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1363_2677
  f_scripts_test_reqmap_py_326_1245["scripts/test_reqmap.py:326-1245"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_326_1245
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_679["scripts/reqmap.py:679"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_679
  f_scripts_test_reqmap_py_518["scripts/test_reqmap.py:518"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_518
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1496_1509["scripts/reqmap.py:1496-1509"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1496_1509
  f_scripts_test_reqmap_py_1409_1528["scripts/test_reqmap.py:1409-1528"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1409_1528
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1469_2693["scripts/reqmap.py:1469-2693"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1469_2693
  f_scripts_test_reqmap_py_826_1246["scripts/test_reqmap.py:826-1246"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_826_1246
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_776_791["scripts/reqmap.py:776-791"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_776_791
  f_scripts_test_reqmap_py_1349["scripts/test_reqmap.py:1349"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1349
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_700_746["scripts/reqmap.py:700-746"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_700_746
  f_scripts_test_reqmap_py_2340["scripts/test_reqmap.py:2340"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2340
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_2746["scripts/reqmap.py:2746"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_2746
  f_scripts_test_reqmap_py_2382["scripts/test_reqmap.py:2382"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2382
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_408["scripts/reqmap.py:408"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_408
  f_scripts_test_reqmap_py_562["scripts/test_reqmap.py:562"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_562
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_211_225["scripts/reqmap.py:211-225"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_211_225
  f_scripts_test_reqmap_py_2434["scripts/test_reqmap.py:2434"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2434
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1818["scripts/reqmap.py:1818"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1818
  f_scripts_test_reqmap_py_1881["scripts/test_reqmap.py:1881"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1881
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1900_1961["scripts/reqmap.py:1900-1961"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1900_1961
  f_scripts_test_reqmap_py_1945["scripts/test_reqmap.py:1945"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_1945
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_458_526["scripts/reqmap.py:458-526"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_458_526
  f_scripts_test_reqmap_py_2083["scripts/test_reqmap.py:2083"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2083
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_510_1853["scripts/reqmap.py:510-1853"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_510_1853
  f_scripts_test_reqmap_py_2217["scripts/test_reqmap.py:2217"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2217
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_2717_2730["scripts/reqmap.py:2717-2730"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_2717_2730
  f_scripts_test_reqmap_py_799["scripts/test_reqmap.py:799"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_799
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>22 caps</small>"]
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
