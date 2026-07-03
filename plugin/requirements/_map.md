---
generated: 2026-07-03 14:33
nodes: 38
edges: 54
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
    REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
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
    REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
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
  REQ_COVERAGE_029 --> REQ_NEXT_013
  REQ_EXCALIDRAW_031 --> REQ_EXCALIDRAW_030
  REQ_EXCALIDRAW_032 --> REQ_EXCALIDRAW_030
  REQ_INIT_012 --> REQ_EXTRACT_008
  REQ_INIT_012 --> REQ_MAP_007
  REQ_LINTCHECKS_025 --> REQ_LINT_014
  REQ_NEXT_013 --> REQ_MAP_007
  REQ_PAGES_021 --> REQ_MAP_007
  REQ_PROMOTE_TODO_001 --> REQ_NEW_004
  REQ_PROSE_024 --> REQ_EXTRACT_008
  REQ_SITE_026 --> REQ_MAP_007
  REQ_SITE_026 --> REQ_VIEWER_007
  REQ_SITE_026 --> REQ_PAGES_021
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
  f_scripts_reqmap_py_1148_1192["scripts/reqmap.py:1148-1192"]
  CORE_DRIFT_003 -->|implements| f_scripts_reqmap_py_1148_1192
  f_scripts_test_reqmap_py_152_4253["scripts/test_reqmap.py:152-4253"]
  CORE_DRIFT_003 -->|tested-by| f_scripts_test_reqmap_py_152_4253
  CORE_PARSE_001["Requirement reading<br><small>CORE-PARSE-001</small>"]
  f_scripts_reqmap_py_628_699["scripts/reqmap.py:628-699"]
  CORE_PARSE_001 -->|implements| f_scripts_reqmap_py_628_699
  f_scripts_test_reqmap_py_49_4206["scripts/test_reqmap.py:49-4206"]
  CORE_PARSE_001 -->|tested-by| f_scripts_test_reqmap_py_49_4206
  CORE_SCAN_002["Member discovery<br><small>CORE-SCAN-002</small>"]
  f_scripts_reqmap_py_722_917["scripts/reqmap.py:722-917"]
  CORE_SCAN_002 -->|implements| f_scripts_reqmap_py_722_917
  f_scripts_test_reqmap_py_271["scripts/test_reqmap.py:271"]
  CORE_SCAN_002 -->|tested-by| f_scripts_test_reqmap_py_271
  NEED_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>NEED-SSOT-001</small>"]
  style NEED_SSOT_001 fill:#fee,stroke:#c66
  REQ_ACVERIFY_019["Per-criterion test coverage<br><small>REQ-ACVERIFY-019</small>"]
  f_scripts_reqmap_py_1054_1521["scripts/reqmap.py:1054-1521"]
  REQ_ACVERIFY_019 -->|implements| f_scripts_reqmap_py_1054_1521
  f_scripts_test_reqmap_py_2855_4237["scripts/test_reqmap.py:2855-4237"]
  REQ_ACVERIFY_019 -->|tested-by| f_scripts_test_reqmap_py_2855_4237
  REQ_CANDIDATES_009["Capability candidates (extraction plan)<br><small>REQ-CANDIDATES-009</small>"]
  f_scripts_reqmap_py_2087_2235["scripts/reqmap.py:2087-2235"]
  REQ_CANDIDATES_009 -->|implements| f_scripts_reqmap_py_2087_2235
  f_scripts_test_reqmap_py_941_2290["scripts/test_reqmap.py:941-2290"]
  REQ_CANDIDATES_009 -->|tested-by| f_scripts_test_reqmap_py_941_2290
  REQ_CHECK_006["The gate<br><small>REQ-CHECK-006</small>"]
  f_scripts_reqmap_py_1135_1639["scripts/reqmap.py:1135-1639"]
  REQ_CHECK_006 -->|implements| f_scripts_reqmap_py_1135_1639
  f_scripts_test_reqmap_py_142_4415["scripts/test_reqmap.py:142-4415"]
  REQ_CHECK_006 -->|tested-by| f_scripts_test_reqmap_py_142_4415
  REQ_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>REQ-CMDREGISTRY-033</small>"]
  f_scripts_reqmap_py_120_1661["scripts/reqmap.py:120-1661"]
  REQ_CMDREGISTRY_033 -->|implements| f_scripts_reqmap_py_120_1661
  f_scripts_test_reqmap_py_4135["scripts/test_reqmap.py:4135"]
  REQ_CMDREGISTRY_033 -->|tested-by| f_scripts_test_reqmap_py_4135
  REQ_COVERAGE_029["Untagged-code coverage signal<br><small>REQ-COVERAGE-029</small>"]
  f_scripts_reqmap_py_3307["scripts/reqmap.py:3307"]
  REQ_COVERAGE_029 -->|implements| f_scripts_reqmap_py_3307
  f_scripts_test_reqmap_py_2647["scripts/test_reqmap.py:2647"]
  REQ_COVERAGE_029 -->|tested-by| f_scripts_test_reqmap_py_2647
  REQ_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>REQ-DOCBUNDLE-026</small>"]
  f_scripts_reqmap_py_967["scripts/reqmap.py:967"]
  REQ_DOCBUNDLE_026 -->|implements| f_scripts_reqmap_py_967
  f_scripts_test_reqmap_py_382["scripts/test_reqmap.py:382"]
  REQ_DOCBUNDLE_026 -->|tested-by| f_scripts_test_reqmap_py_382
  REQ_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>REQ-DRIFTIMPACT-035</small>"]
  f_scripts_reqmap_py_1559["scripts/reqmap.py:1559"]
  REQ_DRIFTIMPACT_035 -->|implements| f_scripts_reqmap_py_1559
  f_scripts_test_reqmap_py_597["scripts/test_reqmap.py:597"]
  REQ_DRIFTIMPACT_035 -->|tested-by| f_scripts_test_reqmap_py_597
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
  f_scripts_reqmap_py_1924_2070["scripts/reqmap.py:1924-2070"]
  REQ_EXTRACT_008 -->|implements| f_scripts_reqmap_py_1924_2070
  f_scripts_test_reqmap_py_821_836["scripts/test_reqmap.py:821-836"]
  REQ_EXTRACT_008 -->|tested-by| f_scripts_test_reqmap_py_821_836
  REQ_FINDINGS_010["Open-findings report<br><small>REQ-FINDINGS-010</small>"]
  f_scripts_reqmap_py_2356_2443["scripts/reqmap.py:2356-2443"]
  REQ_FINDINGS_010 -->|implements| f_scripts_reqmap_py_2356_2443
  f_scripts_test_reqmap_py_1014_1556["scripts/test_reqmap.py:1014-1556"]
  REQ_FINDINGS_010 -->|tested-by| f_scripts_test_reqmap_py_1014_1556
  REQ_HEALTH_017["Corpus health snapshot<br><small>REQ-HEALTH-017</small>"]
  f_scripts_reqmap_py_3245["scripts/reqmap.py:3245"]
  REQ_HEALTH_017 -->|implements| f_scripts_reqmap_py_3245
  f_scripts_test_reqmap_py_2604_2705["scripts/test_reqmap.py:2604-2705"]
  REQ_HEALTH_017 -->|tested-by| f_scripts_test_reqmap_py_2604_2705
  REQ_INIT_012["First-use bootstrap<br><small>REQ-INIT-012</small>"]
  f_scripts_reqmap_py_3417_3446["scripts/reqmap.py:3417-3446"]
  REQ_INIT_012 -->|implements| f_scripts_reqmap_py_3417_3446
  f_scripts_test_reqmap_py_2050_4367["scripts/test_reqmap.py:2050-4367"]
  REQ_INIT_012 -->|tested-by| f_scripts_test_reqmap_py_2050_4367
  REQ_LINT_014["Requirement readability linter<br><small>REQ-LINT-014</small>"]
  f_scripts_reqmap_py_2759_2939["scripts/reqmap.py:2759-2939"]
  REQ_LINT_014 -->|implements| f_scripts_reqmap_py_2759_2939
  f_scripts_test_reqmap_py_2318["scripts/test_reqmap.py:2318"]
  REQ_LINT_014 -->|tested-by| f_scripts_test_reqmap_py_2318
  REQ_LINTCHECKS_025["Readability & scope checks<br><small>REQ-LINTCHECKS-025</small>"]
  f_scripts_reqmap_py_2788_2826["scripts/reqmap.py:2788-2826"]
  REQ_LINTCHECKS_025 -->|implements| f_scripts_reqmap_py_2788_2826
  f_scripts_test_reqmap_py_2302_2318["scripts/test_reqmap.py:2302-2318"]
  REQ_LINTCHECKS_025 -->|tested-by| f_scripts_test_reqmap_py_2302_2318
  REQ_MAP_007["Requirement map (Mermaid MD + JSON)<br><small>REQ-MAP-007</small>"]
  f_scripts_reqmap_py_2483_4477["scripts/reqmap.py:2483-4477"]
  REQ_MAP_007 -->|implements| f_scripts_reqmap_py_2483_4477
  f_scripts_test_reqmap_py_678_4367["scripts/test_reqmap.py:678-4367"]
  REQ_MAP_007 -->|tested-by| f_scripts_test_reqmap_py_678_4367
  REQ_MEMBERDRIFT_027["Reverse-direction member drift<br><small>REQ-MEMBERDRIFT-027</small>"]
  f_scripts_reqmap_py_1208_1295["scripts/reqmap.py:1208-1295"]
  REQ_MEMBERDRIFT_027 -->|implements| f_scripts_reqmap_py_1208_1295
  f_scripts_test_reqmap_py_437["scripts/test_reqmap.py:437"]
  REQ_MEMBERDRIFT_027 -->|tested-by| f_scripts_test_reqmap_py_437
  REQ_NEW_004["Scaffold a requirement<br><small>REQ-NEW-004</small>"]
  f_scripts_reqmap_py_1755["scripts/reqmap.py:1755"]
  REQ_NEW_004 -->|implements| f_scripts_reqmap_py_1755
  f_scripts_test_reqmap_py_883["scripts/test_reqmap.py:883"]
  REQ_NEW_004 -->|tested-by| f_scripts_test_reqmap_py_883
  REQ_NEXT_013["What-should-I-do-next report<br><small>REQ-NEXT-013</small>"]
  f_scripts_reqmap_py_998_2635["scripts/reqmap.py:998-2635"]
  REQ_NEXT_013 -->|implements| f_scripts_reqmap_py_998_2635
  f_scripts_test_reqmap_py_1924_4317["scripts/test_reqmap.py:1924-4317"]
  REQ_NEXT_013 -->|tested-by| f_scripts_test_reqmap_py_1924_4317
  REQ_ORPHANCODE_034["Orphan-code warning<br><small>REQ-ORPHANCODE-034</small>"]
  f_scripts_reqmap_py_1025_1601["scripts/reqmap.py:1025-1601"]
  REQ_ORPHANCODE_034 -->|implements| f_scripts_reqmap_py_1025_1601
  f_scripts_test_reqmap_py_537["scripts/test_reqmap.py:537"]
  REQ_ORPHANCODE_034 -->|tested-by| f_scripts_test_reqmap_py_537
  REQ_PAGES_021["Publish & gate the GitHub Pages map copy<br><small>REQ-PAGES-021</small>"]
  f_scripts_reqmap_py_2594_4493["scripts/reqmap.py:2594-4493"]
  REQ_PAGES_021 -->|implements| f_scripts_reqmap_py_2594_4493
  f_scripts_test_reqmap_py_1203_1761["scripts/test_reqmap.py:1203-1761"]
  REQ_PAGES_021 -->|tested-by| f_scripts_test_reqmap_py_1203_1761
  REQ_PROMOTE_011["confirm<br><small>REQ-PROMOTE-011</small>"]
  f_scripts_reqmap_py_1864_1890["scripts/reqmap.py:1864-1890"]
  REQ_PROMOTE_011 -->|implements| f_scripts_reqmap_py_1864_1890
  f_scripts_test_reqmap_py_1864_4317["scripts/test_reqmap.py:1864-4317"]
  REQ_PROMOTE_011 -->|tested-by| f_scripts_test_reqmap_py_1864_4317
  REQ_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>REQ-PROMOTE-TODO-001</small>"]
  f_scripts_reqmap_py_1776_1832["scripts/reqmap.py:1776-1832"]
  REQ_PROMOTE_TODO_001 -->|implements| f_scripts_reqmap_py_1776_1832
  f_scripts_test_reqmap_py_3048_4317["scripts/test_reqmap.py:3048-4317"]
  REQ_PROMOTE_TODO_001 -->|tested-by| f_scripts_test_reqmap_py_3048_4317
  REQ_PROSE_024["Prose capability classification & drafting<br><small>REQ-PROSE-024</small>"]
  f_scripts_reqmap_py_1932_1985["scripts/reqmap.py:1932-1985"]
  REQ_PROSE_024 -->|implements| f_scripts_reqmap_py_1932_1985
  f_scripts_test_reqmap_py_635_821["scripts/test_reqmap.py:635-821"]
  REQ_PROSE_024 -->|tested-by| f_scripts_test_reqmap_py_635_821
  REQ_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>REQ-REVIEW-022</small>"]
  f_scripts_reqmap_py_4644["scripts/reqmap.py:4644"]
  REQ_REVIEW_022 -->|implements| f_scripts_reqmap_py_4644
  f_scripts_test_reqmap_py_3115["scripts/test_reqmap.py:3115"]
  REQ_REVIEW_022 -->|tested-by| f_scripts_test_reqmap_py_3115
  f_skills_requirement_quality_review_SKILL_md_6["skills/requirement-quality-review/SKILL.md:6"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_md_6
  f_skills_requirement_quality_review_SKILL_universal_md_9["skills/requirement-quality-review/SKILL.universal.md:9"]
  REQ_REVIEW_022 -->|implements| f_skills_requirement_quality_review_SKILL_universal_md_9
  REQ_SCAN_005["List members per capability<br><small>REQ-SCAN-005</small>"]
  f_scripts_reqmap_py_1332["scripts/reqmap.py:1332"]
  REQ_SCAN_005 -->|implements| f_scripts_reqmap_py_1332
  f_scripts_test_reqmap_py_927["scripts/test_reqmap.py:927"]
  REQ_SCAN_005 -->|tested-by| f_scripts_test_reqmap_py_927
  REQ_SCANCACHE_023["Opt-in scan cache<br><small>REQ-SCANCACHE-023</small>"]
  f_scripts_reqmap_py_894_908["scripts/reqmap.py:894-908"]
  REQ_SCANCACHE_023 -->|implements| f_scripts_reqmap_py_894_908
  f_scripts_test_reqmap_py_3176["scripts/test_reqmap.py:3176"]
  REQ_SCANCACHE_023 -->|tested-by| f_scripts_test_reqmap_py_3176
  REQ_SHOW_015["Single-requirement dossier<br><small>REQ-SHOW-015</small>"]
  f_scripts_reqmap_py_2981["scripts/reqmap.py:2981"]
  REQ_SHOW_015 -->|implements| f_scripts_reqmap_py_2981
  f_scripts_test_reqmap_py_2478["scripts/test_reqmap.py:2478"]
  REQ_SHOW_015 -->|tested-by| f_scripts_test_reqmap_py_2478
  REQ_SIMILAR_016["Duplicate-capability detector<br><small>REQ-SIMILAR-016</small>"]
  f_scripts_reqmap_py_3063_3124["scripts/reqmap.py:3063-3124"]
  REQ_SIMILAR_016 -->|implements| f_scripts_reqmap_py_3063_3124
  f_scripts_test_reqmap_py_2542["scripts/test_reqmap.py:2542"]
  REQ_SIMILAR_016 -->|tested-by| f_scripts_test_reqmap_py_2542
  REQ_SITE_026["Generate & maintain a project presentation page<br><small>REQ-SITE-026</small>"]
  f_scripts_reqmap_py_3472_4854["scripts/reqmap.py:3472-4854"]
  REQ_SITE_026 -->|implements| f_scripts_reqmap_py_3472_4854
  f_scripts_test_reqmap_py_3817["scripts/test_reqmap.py:3817"]
  REQ_SITE_026 -->|tested-by| f_scripts_test_reqmap_py_3817
  REQ_TESTLINK_018["Test-link integrity check<br><small>REQ-TESTLINK-018</small>"]
  f_scripts_reqmap_py_1404_1513["scripts/reqmap.py:1404-1513"]
  REQ_TESTLINK_018 -->|implements| f_scripts_reqmap_py_1404_1513
  f_scripts_test_reqmap_py_2779["scripts/test_reqmap.py:2779"]
  REQ_TESTLINK_018 -->|tested-by| f_scripts_test_reqmap_py_2779
  REQ_TRACE_020["Upstream traceability<br><small>REQ-TRACE-020</small>"]
  f_scripts_reqmap_py_1485_3016["scripts/reqmap.py:1485-3016"]
  REQ_TRACE_020 -->|implements| f_scripts_reqmap_py_1485_3016
  f_scripts_test_reqmap_py_2925["scripts/test_reqmap.py:2925"]
  REQ_TRACE_020 -->|tested-by| f_scripts_test_reqmap_py_2925
  REQ_VIEWER_007["Self-contained HTML map viewer<br><small>REQ-VIEWER-007</small>"]
  f_scripts_reqmap_py_4606_4628["scripts/reqmap.py:4606-4628"]
  REQ_VIEWER_007 -->|implements| f_scripts_reqmap_py_4606_4628
  f_scripts_test_reqmap_py_1176["scripts/test_reqmap.py:1176"]
  REQ_VIEWER_007 -->|tested-by| f_scripts_test_reqmap_py_1176
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_CORE["CORE<br><small>3 caps</small>"]
  a_REQ["REQ<br><small>34 caps</small>"]
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
