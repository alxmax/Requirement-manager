---
generated: 2026-06-21 19:44
nodes: 36
edges: 50
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
    REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
    REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
    REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
    REQ_EXCALIDRAW_030["Excalidraw scene builder — core API<br><small>REQ-EXCALIDRAW-030</small>"]
    REQ_EXCALIDRAW_031["Excalidraw quality gates<br><small>REQ-EXCALIDRAW-031</small>"]
    REQ_EXCALIDRAW_032["Excalidraw builder CLI verbs<br><small>REQ-EXCALIDRAW-032</small>"]
    REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
    REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
    REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
    REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
    REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
    REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
    REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
    REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
    REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
    REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
    REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
    REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
    REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
    REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
    REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
    REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
    REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
    REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
    REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
    REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
    REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
    REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
    REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  end
  subgraph sg_misc["misc"]
    NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  end
  REQ_ACVERIFY_019 --> REQ_CHECK_006
  REQ_COVERAGE_029 --> REQ_NEXT_013
  REQ_DOCBUNDLE_026 --> REQ_CHECK_006
  REQ_EXCALIDRAW_031 --> REQ_EXCALIDRAW_030
  REQ_EXCALIDRAW_032 --> REQ_EXCALIDRAW_030
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_CHECK_006
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_MEMBERDRIFT_027 --> REQ_CHECK_006
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_PROSE_024 --> REQ_EXTRACT_008
  REQ_SITE_026 --> REQ_MAP_007
  REQ_SITE_026 --> REQ_VIEWER_007
  REQ_SITE_026 --> REQ_PAGES_021
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
  f_scripts_reqmap_py_1073_1107["scripts/reqmap.py:1073-1107"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1073_1107
  f_scripts_test_reqmap_py_151_189["scripts/test_reqmap.py:151-189"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_151_189
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_628_687["scripts/reqmap.py:628-687"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_628_687
  f_scripts_test_reqmap_py_48_1201["scripts/test_reqmap.py:48-1201"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_48_1201
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_703_898["scripts/reqmap.py:703-898"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_703_898
  f_scripts_test_reqmap_py_266["scripts/test_reqmap.py:266"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_266
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1000_1376["scripts/reqmap.py:1000-1376"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1000_1376
  f_scripts_test_reqmap_py_2599["scripts/test_reqmap.py:2599"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2599
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_1904_2052["scripts/reqmap.py:1904-2052"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_1904_2052
  f_scripts_test_reqmap_py_812_2120["scripts/test_reqmap.py:812-2120"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_812_2120
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1060_1467["scripts/reqmap.py:1060-1467"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1060_1467
  f_scripts_test_reqmap_py_141_3743["scripts/test_reqmap.py:141-3743"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_141_3743
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_120_1489["scripts/reqmap.py:120-1489"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_120_1489
  f_scripts_test_reqmap_py_3803["scripts/test_reqmap.py:3803"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_3803
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3087["scripts/reqmap.py:3087"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3087
  f_scripts_test_reqmap_py_2476["scripts/test_reqmap.py:2476"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2476
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_948["scripts/reqmap.py:948"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_948
  f_scripts_test_reqmap_py_377["scripts/test_reqmap.py:377"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_377
  REQ_EXCALIDRAW_030["Excalidraw scene builder — core API<br><small>REQ-EXCALIDRAW-030</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2["skills/excalidraw-diagram/scripts/excalidraw_builder.py:2"]
  REQ_EXCALIDRAW_030 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_2
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_2["skills/excalidraw-diagram/scripts/test_excalidraw.py:2"]
  REQ_EXCALIDRAW_030 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_2
  REQ_EXCALIDRAW_031["Excalidraw quality gates<br><small>REQ-EXCALIDRAW-031</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3["skills/excalidraw-diagram/scripts/excalidraw_builder.py:3"]
  REQ_EXCALIDRAW_031 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_3
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_3["skills/excalidraw-diagram/scripts/test_excalidraw.py:3"]
  REQ_EXCALIDRAW_031 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_3
  REQ_EXCALIDRAW_032["Excalidraw builder CLI verbs<br><small>REQ-EXCALIDRAW-032</small>"]
  f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4["skills/excalidraw-diagram/scripts/excalidraw_builder.py:4"]
  REQ_EXCALIDRAW_032 -->|implements| f_skills_excalidraw_diagram_scripts_excalidraw_builder_py_4
  f_skills_excalidraw_diagram_scripts_test_excalidraw_py_4["skills/excalidraw-diagram/scripts/test_excalidraw.py:4"]
  REQ_EXCALIDRAW_032 -->|tested-by| f_skills_excalidraw_diagram_scripts_test_excalidraw_py_4
  REQ_EXTRACT_008["Legacy extraction<br><small>REQ-EXTRACT-008</small>"]
  f_scripts_reqmap_py_1741_1887["scripts/reqmap.py:1741-1887"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1741_1887
  f_scripts_test_reqmap_py_705_720["scripts/test_reqmap.py:705-720"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_705_720
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2173_2260["scripts/reqmap.py:2173-2260"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2173_2260
  f_scripts_test_reqmap_py_885_1386["scripts/test_reqmap.py:885-1386"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_885_1386
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3036["scripts/reqmap.py:3036"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3036
  f_scripts_test_reqmap_py_2434["scripts/test_reqmap.py:2434"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2434
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3187_3216["scripts/reqmap.py:3187-3216"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3187_3216
  f_scripts_test_reqmap_py_1880_2013["scripts/test_reqmap.py:1880-2013"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1880_2013
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2575_2755["scripts/reqmap.py:2575-2755"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2575_2755
  f_scripts_test_reqmap_py_2148["scripts/test_reqmap.py:2148"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2148
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2604_2642["scripts/reqmap.py:2604-2642"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2604_2642
  f_scripts_test_reqmap_py_2132_2148["scripts/test_reqmap.py:2132-2148"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2132_2148
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2300_4213["scripts/reqmap.py:2300-4213"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2300_4213
  f_scripts_test_reqmap_py_562_1590["scripts/test_reqmap.py:562-1590"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_562_1590
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1123_1176["scripts/reqmap.py:1123-1176"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1123_1176
  f_scripts_test_reqmap_py_432["scripts/test_reqmap.py:432"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_432
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1583["scripts/reqmap.py:1583"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1583
  f_scripts_test_reqmap_py_754["scripts/test_reqmap.py:754"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_754
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_979_2451["scripts/reqmap.py:979-2451"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_979_2451
  f_scripts_test_reqmap_py_1754_1873["scripts/test_reqmap.py:1754-1873"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1754_1873
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2411_4229["scripts/reqmap.py:2411-4229"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2411_4229
  f_scripts_test_reqmap_py_1062_1591["scripts/test_reqmap.py:1062-1591"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1062_1591
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1692_1707["scripts/reqmap.py:1692-1707"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1692_1707
  f_scripts_test_reqmap_py_1694["scripts/test_reqmap.py:1694"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1694
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1604_1660["scripts/reqmap.py:1604-1660"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1604_1660
  f_scripts_test_reqmap_py_2792["scripts/test_reqmap.py:2792"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2792
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1749_1802["scripts/reqmap.py:1749-1802"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1749_1802
  f_scripts_test_reqmap_py_519_705["scripts/test_reqmap.py:519-705"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_519_705
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4380["scripts/reqmap.py:4380"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4380
  f_scripts_test_reqmap_py_2859["scripts/test_reqmap.py:2859"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2859
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1213["scripts/reqmap.py:1213"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1213
  f_scripts_test_reqmap_py_798["scripts/test_reqmap.py:798"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_798
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_875_889["scripts/reqmap.py:875-889"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_875_889
  f_scripts_test_reqmap_py_2911["scripts/test_reqmap.py:2911"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2911
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2797["scripts/reqmap.py:2797"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2797
  f_scripts_test_reqmap_py_2308["scripts/test_reqmap.py:2308"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2308
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_2879_2940["scripts/reqmap.py:2879-2940"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_2879_2940
  f_scripts_test_reqmap_py_2372["scripts/test_reqmap.py:2372"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2372
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3242_4587["scripts/reqmap.py:3242-4587"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3242_4587
  f_scripts_test_reqmap_py_3485["scripts/test_reqmap.py:3485"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3485
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1263_1368["scripts/reqmap.py:1263-1368"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1263_1368
  f_scripts_test_reqmap_py_2535["scripts/test_reqmap.py:2535"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2535
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1340_2832["scripts/reqmap.py:1340-2832"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1340_2832
  f_scripts_test_reqmap_py_2669["scripts/test_reqmap.py:2669"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2669
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4342_4364["scripts/reqmap.py:4342-4364"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4342_4364
  f_scripts_test_reqmap_py_1035["scripts/test_reqmap.py:1035"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1035
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>32 caps</small>"]
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
