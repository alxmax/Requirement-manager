---
generated: 2026-06-28 20:54
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
  f_scripts_reqmap_py_1113_1157["scripts/reqmap.py:1113-1157"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1113_1157
  f_scripts_test_reqmap_py_152_4065["scripts/test_reqmap.py:152-4065"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_152_4065
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_628_699["scripts/reqmap.py:628-699"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_628_699
  f_scripts_test_reqmap_py_49_4018["scripts/test_reqmap.py:49-4018"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_49_4018
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_722_917["scripts/reqmap.py:722-917"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_722_917
  f_scripts_test_reqmap_py_271["scripts/test_reqmap.py:271"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_271
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1019_1483["scripts/reqmap.py:1019-1483"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1019_1483
  f_scripts_test_reqmap_py_2667_4049["scripts/test_reqmap.py:2667-4049"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2667_4049
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2029_2177["scripts/reqmap.py:2029-2177"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2029_2177
  f_scripts_test_reqmap_py_840_2176["scripts/test_reqmap.py:840-2176"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_840_2176
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1100_1581["scripts/reqmap.py:1100-1581"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1100_1581
  f_scripts_test_reqmap_py_142_4227["scripts/test_reqmap.py:142-4227"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_142_4227
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_120_1603["scripts/reqmap.py:120-1603"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_120_1603
  f_scripts_test_reqmap_py_3947["scripts/test_reqmap.py:3947"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_3947
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3213["scripts/reqmap.py:3213"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3213
  f_scripts_test_reqmap_py_2532["scripts/test_reqmap.py:2532"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2532
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_967["scripts/reqmap.py:967"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_967
  f_scripts_test_reqmap_py_382["scripts/test_reqmap.py:382"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_382
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
  f_scripts_reqmap_py_1866_2012["scripts/reqmap.py:1866-2012"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1866_2012
  f_scripts_test_reqmap_py_720_735["scripts/test_reqmap.py:720-735"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_720_735
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2298_2385["scripts/reqmap.py:2298-2385"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2298_2385
  f_scripts_test_reqmap_py_913_1442["scripts/test_reqmap.py:913-1442"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_913_1442
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3162["scripts/reqmap.py:3162"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3162
  f_scripts_test_reqmap_py_2490["scripts/test_reqmap.py:2490"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2490
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3316_3345["scripts/reqmap.py:3316-3345"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3316_3345
  f_scripts_test_reqmap_py_1936_4179["scripts/test_reqmap.py:1936-4179"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_1936_4179
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2701_2881["scripts/reqmap.py:2701-2881"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2701_2881
  f_scripts_test_reqmap_py_2204["scripts/test_reqmap.py:2204"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2204
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2730_2768["scripts/reqmap.py:2730-2768"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2730_2768
  f_scripts_test_reqmap_py_2188_2204["scripts/test_reqmap.py:2188-2204"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2188_2204
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2425_4376["scripts/reqmap.py:2425-4376"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2425_4376
  f_scripts_test_reqmap_py_577_4179["scripts/test_reqmap.py:577-4179"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_577_4179
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1173_1260["scripts/reqmap.py:1173-1260"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1173_1260
  f_scripts_test_reqmap_py_437["scripts/test_reqmap.py:437"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_437
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1697["scripts/reqmap.py:1697"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1697
  f_scripts_test_reqmap_py_782["scripts/test_reqmap.py:782"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_782
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_998_2577["scripts/reqmap.py:998-2577"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_998_2577
  f_scripts_test_reqmap_py_1810_4129["scripts/test_reqmap.py:1810-4129"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1810_4129
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2536_4392["scripts/reqmap.py:2536-4392"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2536_4392
  f_scripts_test_reqmap_py_1102_1647["scripts/test_reqmap.py:1102-1647"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1102_1647
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1806_1832["scripts/reqmap.py:1806-1832"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1806_1832
  f_scripts_test_reqmap_py_1750_4129["scripts/test_reqmap.py:1750-4129"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1750_4129
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1718_1774["scripts/reqmap.py:1718-1774"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1718_1774
  f_scripts_test_reqmap_py_2860_4129["scripts/test_reqmap.py:2860-4129"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_2860_4129
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1874_1927["scripts/reqmap.py:1874-1927"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1874_1927
  f_scripts_test_reqmap_py_534_720["scripts/test_reqmap.py:534-720"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_534_720
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4543["scripts/reqmap.py:4543"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4543
  f_scripts_test_reqmap_py_2927["scripts/test_reqmap.py:2927"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_2927
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1297["scripts/reqmap.py:1297"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1297
  f_scripts_test_reqmap_py_826["scripts/test_reqmap.py:826"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_826
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_894_908["scripts/reqmap.py:894-908"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_894_908
  f_scripts_test_reqmap_py_2988["scripts/test_reqmap.py:2988"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_2988
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2923["scripts/reqmap.py:2923"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2923
  f_scripts_test_reqmap_py_2364["scripts/test_reqmap.py:2364"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2364
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3005_3066["scripts/reqmap.py:3005-3066"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3005_3066
  f_scripts_test_reqmap_py_2428["scripts/test_reqmap.py:2428"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2428
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3371_4753["scripts/reqmap.py:3371-4753"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3371_4753
  f_scripts_test_reqmap_py_3629["scripts/test_reqmap.py:3629"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3629
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1366_1475["scripts/reqmap.py:1366-1475"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1366_1475
  f_scripts_test_reqmap_py_2591["scripts/test_reqmap.py:2591"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2591
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1447_2958["scripts/reqmap.py:1447-2958"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1447_2958
  f_scripts_test_reqmap_py_2737["scripts/test_reqmap.py:2737"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2737
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4505_4527["scripts/reqmap.py:4505-4527"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4505_4527
  f_scripts_test_reqmap_py_1075["scripts/test_reqmap.py:1075"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1075
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
