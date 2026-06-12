---
generated: 2026-06-12 17:34
nodes: 28
edges: 37
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
    REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
    REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
    REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
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
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_PROSE_024 --> REQ_EXTRACT_008
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
  f_scripts_reqmap_py_354_388["scripts/reqmap.py:354-388"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_354_388
  f_scripts_test_reqmap_py_150_188["scripts/test_reqmap.py:150-188"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_150_188
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_84_141["scripts/reqmap.py:84-141"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_84_141
  f_scripts_test_reqmap_py_47_1037["scripts/test_reqmap.py:47-1037"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_47_1037
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_157_236["scripts/reqmap.py:157-236"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_157_236
  f_scripts_test_reqmap_py_265["scripts/test_reqmap.py:265"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_265
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_283_536["scripts/reqmap.py:283-536"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_283_536
  f_scripts_test_reqmap_py_2237["scripts/test_reqmap.py:2237"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2237
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_990_1137["scripts/reqmap.py:990-1137"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_990_1137
  f_scripts_test_reqmap_py_648_1162["scripts/test_reqmap.py:648-1162"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_648_1162
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_341_480["scripts/reqmap.py:341-480"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_341_480
  f_scripts_test_reqmap_py_140_2404["scripts/test_reqmap.py:140-2404"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_140_2404
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_827_973["scripts/reqmap.py:827-973"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_827_973
  f_scripts_test_reqmap_py_541_556["scripts/test_reqmap.py:541-556"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_541_556
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_1243_1330["scripts/reqmap.py:1243-1330"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_1243_1330
  f_scripts_test_reqmap_py_721_1145["scripts/test_reqmap.py:721-1145"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_721_1145
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_2000["scripts/reqmap.py:2000"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_2000
  f_scripts_test_reqmap_py_2097["scripts/test_reqmap.py:2097"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2097
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_2121_2150["scripts/reqmap.py:2121-2150"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_2121_2150
  f_scripts_test_reqmap_py_1625["scripts/test_reqmap.py:1625"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1625
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_1623_1789["scripts/reqmap.py:1623-1789"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_1623_1789
  f_scripts_test_reqmap_py_1811["scripts/test_reqmap.py:1811"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_1811
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_1652_1681["scripts/reqmap.py:1652-1681"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_1652_1681
  f_scripts_test_reqmap_py_1811["scripts/test_reqmap.py:1811"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_1811
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_1365_2679["scripts/reqmap.py:1365-2679"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_1365_2679
  f_scripts_test_reqmap_py_398_1335["scripts/test_reqmap.py:398-1335"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_398_1335
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_681["scripts/reqmap.py:681"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_681
  f_scripts_test_reqmap_py_590["scripts/test_reqmap.py:590"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_590
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_1498_1511["scripts/reqmap.py:1498-1511"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_1498_1511
  f_scripts_test_reqmap_py_1499_1618["scripts/test_reqmap.py:1499-1618"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1499_1618
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_1471_2695["scripts/reqmap.py:1471-2695"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_1471_2695
  f_scripts_test_reqmap_py_898_1336["scripts/test_reqmap.py:898-1336"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_898_1336
  REQ_PROMOTE_011["promote<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_778_793["scripts/reqmap.py:778-793"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_778_793
  f_scripts_test_reqmap_py_1439["scripts/test_reqmap.py:1439"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1439
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_702_748["scripts/reqmap.py:702-748"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_702_748
  f_scripts_test_reqmap_py_2430["scripts/test_reqmap.py:2430"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2430
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_835_888["scripts/reqmap.py:835-888"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_835_888
  f_scripts_test_reqmap_py_355_541["scripts/test_reqmap.py:355-541"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_355_541
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_2748["scripts/reqmap.py:2748"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_2748
  f_scripts_test_reqmap_py_2472["scripts/test_reqmap.py:2472"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2472
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_410["scripts/reqmap.py:410"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_410
  f_scripts_test_reqmap_py_634["scripts/test_reqmap.py:634"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_634
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_213_227["scripts/reqmap.py:213-227"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_213_227
  f_scripts_test_reqmap_py_2524["scripts/test_reqmap.py:2524"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2524
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_1820["scripts/reqmap.py:1820"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_1820
  f_scripts_test_reqmap_py_1971["scripts/test_reqmap.py:1971"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_1971
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_1902_1963["scripts/reqmap.py:1902-1963"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_1902_1963
  f_scripts_test_reqmap_py_2035["scripts/test_reqmap.py:2035"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2035
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_460_528["scripts/reqmap.py:460-528"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_460_528
  f_scripts_test_reqmap_py_2173["scripts/test_reqmap.py:2173"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2173
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_512_1855["scripts/reqmap.py:512-1855"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_512_1855
  f_scripts_test_reqmap_py_2307["scripts/test_reqmap.py:2307"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2307
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_2719_2732["scripts/reqmap.py:2719-2732"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_2719_2732
  f_scripts_test_reqmap_py_871["scripts/test_reqmap.py:871"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_871
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>24 caps</small>"]
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
