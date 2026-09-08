---
generated: 2026-09-08
engine: 2026-09-08
nodes: 248
edges: 110
design OOP: 73/100 (56/77 source files without a design candidate)
---

# Requirement Map

## Specification Hierarchy

_The spec hierarchy: system needs -> architecture requirements (`satisfies:`), each box showing how many code-level requirements sit under it. The code level itself is counted, not drawn._

```mermaid
graph TD
  ARCH_ACVERIFY_019[ARCH-ACVERIFY-019<br/>3 code]
  ARCH_ATOMICITY_049[ARCH-ATOMICITY-049<br/>2 code]
  ARCH_AUDIT_065[ARCH-AUDIT-065<br/>5 code]
  ARCH_CANDIDATES_009[ARCH-CANDIDATES-009<br/>2 code]
  ARCH_CHECK_006[ARCH-CHECK-006<br/>6 code]
  ARCH_CLARIFY_062[ARCH-CLARIFY-062<br/>3 code]
  ARCH_CMDREGISTRY_033[ARCH-CMDREGISTRY-033<br/>2 code]
  ARCH_CONFIG_060[ARCH-CONFIG-060<br/>1 code]
  ARCH_CONTEXT_048[ARCH-CONTEXT-048<br/>1 code]
  ARCH_COVERAGE_029[ARCH-COVERAGE-029<br/>1 code]
  ARCH_DECOMPOSE_050[ARCH-DECOMPOSE-050<br/>4 code]
  ARCH_DESIGN_061[ARCH-DESIGN-061<br/>11 code]
  ARCH_DOCBUNDLE_026[ARCH-DOCBUNDLE-026<br/>1 code]
  ARCH_DRIFT_003[ARCH-DRIFT-003<br/>3 code]
  ARCH_DRIFTIMPACT_035[ARCH-DRIFTIMPACT-035<br/>1 code]
  ARCH_EXTRACT_008[ARCH-EXTRACT-008<br/>4 code]
  ARCH_FANOUT_052[ARCH-FANOUT-052<br/>1 code]
  ARCH_FINDINGS_010[ARCH-FINDINGS-010<br/>4 code]
  ARCH_GITRUN_067[ARCH-GITRUN-067<br/>1 code]
  ARCH_HEALTH_017[ARCH-HEALTH-017<br/>5 code]
  ARCH_IMPLEMENT_063[ARCH-IMPLEMENT-063<br/>2 code]
  ARCH_INIT_012[ARCH-INIT-012<br/>2 code]
  ARCH_LEVEL_051[ARCH-LEVEL-051<br/>1 code]
  ARCH_LEVELRETROFIT_066[ARCH-LEVELRETROFIT-066<br/>3 code]
  ARCH_LINT_014[ARCH-LINT-014<br/>2 code]
  ARCH_LINTCHECKS_025[ARCH-LINTCHECKS-025<br/>5 code]
  ARCH_MAP_007[ARCH-MAP-007<br/>4 code]
  ARCH_MAPDIAGRAMS_055[ARCH-MAPDIAGRAMS-055<br/>5 code]
  ARCH_MEMBERDRIFT_027[ARCH-MEMBERDRIFT-027<br/>3 code]
  ARCH_NEW_004[ARCH-NEW-004<br/>2 code]
  ARCH_NEXT_013[ARCH-NEXT-013<br/>5 code]
  ARCH_ORPHANCODE_034[ARCH-ORPHANCODE-034<br/>1 code]
  ARCH_PARSE_001[ARCH-PARSE-001<br/>5 code]
  ARCH_PIPE_046[ARCH-PIPE-046<br/>1 code]
  ARCH_PROMOTE_011[ARCH-PROMOTE-011<br/>2 code]
  ARCH_PROMOTE_TODO_001[ARCH-PROMOTE-TODO-001<br/>3 code]
  ARCH_PROSE_024[ARCH-PROSE-024<br/>2 code]
  ARCH_PYFLOOR_040[ARCH-PYFLOOR-040<br/>1 code]
  ARCH_REGISTRYLAG_035[ARCH-REGISTRYLAG-035<br/>2 code]
  ARCH_REPRO_041[ARCH-REPRO-041<br/>1 code]
  ARCH_RETIRE_064[ARCH-RETIRE-064<br/>4 code]
  ARCH_REVIEW_022[ARCH-REVIEW-022<br/>1 code]
  ARCH_ROADMAP_038[ARCH-ROADMAP-038<br/>2 code]
  ARCH_RULES_059[ARCH-RULES-059<br/>3 code]
  ARCH_SCAN_002[ARCH-SCAN-002<br/>3 code]
  ARCH_SCANCACHE_023[ARCH-SCANCACHE-023<br/>1 code]
  ARCH_SEARCH_036[ARCH-SEARCH-036<br/>5 code]
  ARCH_SECTIONS_068[ARCH-SECTIONS-068<br/>2 code]
  ARCH_SELFGATE_039[ARCH-SELFGATE-039<br/>2 code]
  ARCH_SHOW_015[ARCH-SHOW-015<br/>3 code]
  ARCH_SIMILAR_016[ARCH-SIMILAR-016<br/>5 code]
  ARCH_SITE_026[ARCH-SITE-026<br/>1 code]
  ARCH_STALEENGINE_043[ARCH-STALEENGINE-043<br/>2 code]
  ARCH_SUGGESTVERIFIES_047[ARCH-SUGGESTVERIFIES-047<br/>3 code]
  ARCH_TESTLINK_018[ARCH-TESTLINK-018<br/>4 code]
  ARCH_TRACE_020[ARCH-TRACE-020<br/>2 code]
  ARCH_TRACKED_042[ARCH-TRACKED-042<br/>1 code]
  ARCH_TRANSLATE_044[ARCH-TRANSLATE-044<br/>4 code]
  ARCH_UNSCANNEDTAG_045[ARCH-UNSCANNEDTAG-045<br/>1 code]
  ARCH_VIEWER_007[ARCH-VIEWER-007<br/>12 code]
  ARCH_VLEVEL_037[ARCH-VLEVEL-037<br/>4 code]
  SYS_AUTHOR_101[[SYS-AUTHOR-101]]
  SYS_GATE_102[[SYS-GATE-102]]
  SYS_QUALITY_104[[SYS-QUALITY-104]]
  SYS_READ_103[[SYS-READ-103]]
  SYS_REPORT_105[[SYS-REPORT-105]]
  SYS_SHIP_108[[SYS-SHIP-108]]
  SYS_SSOT_001[[SYS-SSOT-001]]
  SYS_VISUAL_106[[SYS-VISUAL-106]]
  SYS_VMODEL_107[[SYS-VMODEL-107]]
  SYS_GATE_102 --> ARCH_ACVERIFY_019
  SYS_AUTHOR_101 --> ARCH_ATOMICITY_049
  SYS_REPORT_105 --> ARCH_AUDIT_065
  SYS_READ_103 --> ARCH_CANDIDATES_009
  SYS_GATE_102 --> ARCH_CHECK_006
  SYS_AUTHOR_101 --> ARCH_CLARIFY_062
  SYS_SHIP_108 --> ARCH_CMDREGISTRY_033
  SYS_AUTHOR_101 --> ARCH_CONFIG_060
  SYS_AUTHOR_101 --> ARCH_CONTEXT_048
  SYS_REPORT_105 --> ARCH_COVERAGE_029
  SYS_AUTHOR_101 --> ARCH_DECOMPOSE_050
  SYS_READ_103 --> ARCH_DESIGN_061
  SYS_GATE_102 --> ARCH_DOCBUNDLE_026
  SYS_GATE_102 --> ARCH_DRIFT_003
  SYS_GATE_102 --> ARCH_DRIFTIMPACT_035
  SYS_READ_103 --> ARCH_EXTRACT_008
  SYS_VMODEL_107 --> ARCH_FANOUT_052
  SYS_REPORT_105 --> ARCH_FINDINGS_010
  SYS_GATE_102 --> ARCH_GITRUN_067
  SYS_REPORT_105 --> ARCH_HEALTH_017
  SYS_GATE_102 --> ARCH_IMPLEMENT_063
  SYS_SHIP_108 --> ARCH_INIT_012
  SYS_VMODEL_107 --> ARCH_LEVEL_051
  SYS_VMODEL_107 --> ARCH_LEVELRETROFIT_066
  SYS_QUALITY_104 --> ARCH_LINT_014
  SYS_QUALITY_104 --> ARCH_LINTCHECKS_025
  SYS_VISUAL_106 --> ARCH_MAP_007
  SYS_VISUAL_106 --> ARCH_MAPDIAGRAMS_055
  SYS_GATE_102 --> ARCH_MEMBERDRIFT_027
  SYS_AUTHOR_101 --> ARCH_NEW_004
  SYS_REPORT_105 --> ARCH_NEXT_013
  SYS_GATE_102 --> ARCH_ORPHANCODE_034
  SYS_READ_103 --> ARCH_PARSE_001
  SYS_QUALITY_104 --> ARCH_PIPE_046
  SYS_AUTHOR_101 --> ARCH_PROMOTE_011
  SYS_AUTHOR_101 --> ARCH_PROMOTE_TODO_001
  SYS_READ_103 --> ARCH_PROSE_024
  SYS_SHIP_108 --> ARCH_PYFLOOR_040
  SYS_REPORT_105 --> ARCH_REGISTRYLAG_035
  SYS_SHIP_108 --> ARCH_REPRO_041
  SYS_GATE_102 --> ARCH_RETIRE_064
  SYS_QUALITY_104 --> ARCH_REVIEW_022
  SYS_REPORT_105 --> ARCH_ROADMAP_038
  SYS_GATE_102 --> ARCH_RULES_059
  SYS_READ_103 --> ARCH_SCAN_002
  SYS_READ_103 --> ARCH_SCANCACHE_023
  SYS_REPORT_105 --> ARCH_SEARCH_036
  SYS_SSOT_001 --> ARCH_SECTIONS_068
  SYS_SHIP_108 --> ARCH_SELFGATE_039
  SYS_REPORT_105 --> ARCH_SHOW_015
  SYS_QUALITY_104 --> ARCH_SIMILAR_016
  SYS_VISUAL_106 --> ARCH_SITE_026
  SYS_SHIP_108 --> ARCH_STALEENGINE_043
  SYS_QUALITY_104 --> ARCH_SUGGESTVERIFIES_047
  SYS_GATE_102 --> ARCH_TESTLINK_018
  SYS_VMODEL_107 --> ARCH_TRACE_020
  SYS_GATE_102 --> ARCH_TRACKED_042
  SYS_SHIP_108 --> ARCH_TRANSLATE_044
  SYS_GATE_102 --> ARCH_UNSCANNEDTAG_045
  SYS_VISUAL_106 --> ARCH_VIEWER_007
  SYS_VMODEL_107 --> ARCH_VLEVEL_037
  SYS_SSOT_001 --> SYS_AUTHOR_101
  SYS_SSOT_001 --> SYS_GATE_102
  SYS_SSOT_001 --> SYS_QUALITY_104
  SYS_SSOT_001 --> SYS_READ_103
  SYS_SSOT_001 --> SYS_REPORT_105
  SYS_SSOT_001 --> SYS_SHIP_108
  SYS_SSOT_001 --> SYS_VISUAL_106
  SYS_SSOT_001 --> SYS_VMODEL_107
  style SYS_AUTHOR_101 stroke-width:3px
  style SYS_GATE_102 stroke-width:3px
  style SYS_QUALITY_104 stroke-width:3px
  style SYS_READ_103 stroke-width:3px
  style SYS_REPORT_105 stroke-width:3px
  style SYS_SHIP_108 stroke-width:3px
  style SYS_SSOT_001 stroke-width:3px
  style SYS_VISUAL_106 stroke-width:3px
  style SYS_VMODEL_107 stroke-width:3px
```

## System Map

_Capabilities grouped by area; thick border = bus; arrows = `depends_on`. Edges into the bus/hubs are hidden (the Dependency Map shows area-level coupling)._

```mermaid
graph LR
  subgraph sg_ARCH["ARCH"]
    ARCH_ACVERIFY_019["Per-criterion test coverage<br><small>ARCH-ACVERIFY-019</small>"]
    ARCH_ATOMICITY_049["Statement atomicity<br><small>ARCH-ATOMICITY-049</small>"]
    ARCH_AUDIT_065["One report of everything the engine can discover<br><small>ARCH-AUDIT-065</small>"]
    ARCH_CANDIDATES_009["Capability candidates (extraction plan)<br><small>ARCH-CANDIDATES-009</small>"]
    ARCH_CHECK_006["The gate<br><small>ARCH-CHECK-006</small>"]
    ARCH_CLARIFY_062["Questions a requirement has not answered<br><small>ARCH-CLARIFY-062</small>"]
    ARCH_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>ARCH-CMDREGISTRY-033</small>"]
    ARCH_CONFIG_060["Per-repo configuration file<br><small>ARCH-CONFIG-060</small>"]
    ARCH_CONTEXT_048["Consolidated Context section<br><small>ARCH-CONTEXT-048</small>"]
    ARCH_COVERAGE_029["Untagged-code coverage signal<br><small>ARCH-COVERAGE-029</small>"]
    ARCH_DECOMPOSE_050["Clause decomposition scaffold<br><small>ARCH-DECOMPOSE-050</small>"]
    ARCH_DESIGN_061["Advisory design review<br><small>ARCH-DESIGN-061</small>"]
    ARCH_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>ARCH-DOCBUNDLE-026</small>"]
    ARCH_DRIFT_003["Contract hashing & lock<br><small>ARCH-DRIFT-003</small>"]
    ARCH_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>ARCH-DRIFTIMPACT-035</small>"]
    ARCH_EXTRACT_008["Legacy extraction<br><small>ARCH-EXTRACT-008</small>"]
    ARCH_FANOUT_052["Hierarchy breadth<br><small>ARCH-FANOUT-052</small>"]
    ARCH_FINDINGS_010["Open-findings report<br><small>ARCH-FINDINGS-010</small>"]
    ARCH_GITRUN_067["Talking to git<br><small>ARCH-GITRUN-067</small>"]
    ARCH_HEALTH_017["Corpus health snapshot<br><small>ARCH-HEALTH-017</small>"]
    ARCH_IMPLEMENT_063["The brief for implementing a requirement<br><small>ARCH-IMPLEMENT-063</small>"]
    ARCH_INIT_012["First-use bootstrap<br><small>ARCH-INIT-012</small>"]
    ARCH_LEVEL_051["Specification level<br><small>ARCH-LEVEL-051</small>"]
    ARCH_LEVELRETROFIT_066["Giving an existing corpus the three rungs<br><small>ARCH-LEVELRETROFIT-066</small>"]
    ARCH_LINT_014["Requirement readability linter<br><small>ARCH-LINT-014</small>"]
    ARCH_LINTCHECKS_025["Readability & scope checks<br><small>ARCH-LINTCHECKS-025</small>"]
    ARCH_MAP_007["Requirement graph (_map.json)<br><small>ARCH-MAP-007</small>"]
    ARCH_MAPDIAGRAMS_055["Mermaid diagrams (_map.md)<br><small>ARCH-MAPDIAGRAMS-055</small>"]
    ARCH_MEMBERDRIFT_027["Reverse-direction member drift<br><small>ARCH-MEMBERDRIFT-027</small>"]
    ARCH_NEW_004["Scaffold a requirement<br><small>ARCH-NEW-004</small>"]
    ARCH_NEXT_013["What-should-I-do-next report<br><small>ARCH-NEXT-013</small>"]
    ARCH_ORPHANCODE_034["Orphan-code warning<br><small>ARCH-ORPHANCODE-034</small>"]
    ARCH_PARSE_001["Requirement reading<br><small>ARCH-PARSE-001</small>"]
    ARCH_PIPE_046["A closed output pipe ends a command quietly<br><small>ARCH-PIPE-046</small>"]
    ARCH_PROMOTE_011["Confirmation is a human's answer, and an edit takes it back<br><small>ARCH-PROMOTE-011</small>"]
    ARCH_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>ARCH-PROMOTE-TODO-001</small>"]
    ARCH_PROSE_024["Prose capability classification & drafting<br><small>ARCH-PROSE-024</small>"]
    ARCH_PYFLOOR_040["Declared Python support floor<br><small>ARCH-PYFLOOR-040</small>"]
    ARCH_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>ARCH-REGISTRYLAG-035</small>"]
    ARCH_REPRO_041["Committed build artifacts stay re-derivable<br><small>ARCH-REPRO-041</small>"]
    ARCH_RETIRE_064["Taking a requirement out of service<br><small>ARCH-RETIRE-064</small>"]
    ARCH_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>ARCH-REVIEW-022</small>"]
    ARCH_ROADMAP_038["Roadmap coherence signals<br><small>ARCH-ROADMAP-038</small>"]
    ARCH_RULES_059["The gate rule registry<br><small>ARCH-RULES-059</small>"]
    ARCH_SCAN_002["Member discovery<br><small>ARCH-SCAN-002</small>"]
    ARCH_SCANCACHE_023["Opt-in scan cache<br><small>ARCH-SCANCACHE-023</small>"]
    ARCH_SEARCH_036["Free-text requirement search<br><small>ARCH-SEARCH-036</small>"]
    ARCH_SECTIONS_068["Reading a requirement's sections<br><small>ARCH-SECTIONS-068</small>"]
    ARCH_SELFGATE_039["This repo's own gate wiring<br><small>ARCH-SELFGATE-039</small>"]
    ARCH_SHOW_015["Single-requirement dossier<br><small>ARCH-SHOW-015</small>"]
    ARCH_SIMILAR_016["Duplicate-capability detector<br><small>ARCH-SIMILAR-016</small>"]
    ARCH_SITE_026["Generate & maintain a project presentation page<br><small>ARCH-SITE-026</small>"]
    ARCH_STALEENGINE_043["Stale vendored engine, reported in CI<br><small>ARCH-STALEENGINE-043</small>"]
    ARCH_SUGGESTVERIFIES_047["Suggest per-criterion 'verifies:' tags<br><small>ARCH-SUGGESTVERIFIES-047</small>"]
    ARCH_TESTLINK_018["Test-link integrity check<br><small>ARCH-TESTLINK-018</small>"]
    ARCH_TRACE_020["Upstream traceability<br><small>ARCH-TRACE-020</small>"]
    ARCH_TRACKED_042["Untracked members reported<br><small>ARCH-TRACKED-042</small>"]
    ARCH_TRANSLATE_044["Reading a cached requirement translation into the map<br><small>ARCH-TRANSLATE-044</small>"]
    ARCH_UNSCANNEDTAG_045["Tags in unscanned file types reported<br><small>ARCH-UNSCANNEDTAG-045</small>"]
    ARCH_VIEWER_007["Self-contained HTML map viewer<br><small>ARCH-VIEWER-007</small>"]
    ARCH_VLEVEL_037["Verification levels<br><small>ARCH-VLEVEL-037</small>"]
  end
  subgraph sg_REQ["REQ"]
    REQ_ACVERIFY_821["Mapping verifies tags to labelled criteria<br><small>REQ-ACVERIFY-821</small>"]
    REQ_ACVERIFY_822["When per-criterion coverage stays silent<br><small>REQ-ACVERIFY-822</small>"]
    REQ_ACVERIFY_823["Emitting clauses, covered and gap on the map<br><small>REQ-ACVERIFY-823</small>"]
    REQ_ATOMICITY_824["One obligation per clause, with an advisory length backstop<br><small>REQ-ATOMICITY-824</small>"]
    REQ_ATOMICITY_825["statement-size measures length, not atomicity<br><small>REQ-ATOMICITY-825</small>"]
    REQ_AUDIT_970["Every discovery pass, one report, one exit code<br><small>REQ-AUDIT-970</small>"]
    REQ_AUDIT_971["An exemption nobody justified is itself a finding<br><small>REQ-AUDIT-971</small>"]
    REQ_AUDIT_972["Whether the corpus has a shape at all<br><small>REQ-AUDIT-972</small>"]
    REQ_AUDIT_973["Sync says what it found<br><small>REQ-AUDIT-973</small>"]
    REQ_RELEVEL_997["The tail names a move that was only half made<br><small>REQ-RELEVEL-997</small>"]
    REQ_CANDIDATES_826["The plan's JSON shape and read-only scanning<br><small>REQ-CANDIDATES-826</small>"]
    REQ_CANDIDATES_827["Fields a candidate carries<br><small>REQ-CANDIDATES-827</small>"]
    REQ_CHECK_828["Gate errors that block a commit<br><small>REQ-CHECK-828</small>"]
    REQ_CHECK_829["Contract drift and missing-coverage warnings<br><small>REQ-CHECK-829</small>"]
    REQ_CHECK_830["Milestone shape and lock-file warnings<br><small>REQ-CHECK-830</small>"]
    REQ_CHECK_831["Corpus-health warnings: needs, levels, cycles<br><small>REQ-CHECK-831</small>"]
    REQ_CHECK_832["What the gate prints beyond pass or fail<br><small>REQ-CHECK-832</small>"]
    REQ_CHECK_833["Advancing the lock file<br><small>REQ-CHECK-833</small>"]
    REQ_CLARIFY_956["Detecting what a requirement leaves open<br><small>REQ-CLARIFY-956</small>"]
    REQ_CLARIFY_957["Reporting the open questions<br><small>REQ-CLARIFY-957</small>"]
    REQ_CLARIFY_975["An answer can raise a question the old text never had<br><small>REQ-CLARIFY-975</small>"]
    REQ_CMDREGISTRY_834["One COMMANDS dict drives argparse, schema and docs<br><small>REQ-CMDREGISTRY-834</small>"]
    REQ_CMDREGISTRY_963["The command registry as data on the map<br><small>REQ-CMDREGISTRY-963</small>"]
    REQ_CONFIG_949["Reading and applying '_config.json'<br><small>REQ-CONFIG-949</small>"]
    REQ_CONTEXT_835["One Context section replaces three near-synonymous headings<br><small>REQ-CONTEXT-835</small>"]
    REQ_COVERAGE_836["Counting untagged code as a read-only signal<br><small>REQ-COVERAGE-836</small>"]
    REQ_DECOMPOSE_837["--decompose is opt-in; the default lint run never writes<br><small>REQ-DECOMPOSE-837</small>"]
    REQ_DECOMPOSE_838["A created draft's shape: status, parent link, seeded clause, id<br><small>REQ-DECOMPOSE-838</small>"]
    REQ_DECOMPOSE_839["The parent never changes, and the command knows its own limits<br><small>REQ-DECOMPOSE-839</small>"]
    REQ_DECOMPOSE_994["Splitting a requirement along its own contract groups<br><small>REQ-DECOMPOSE-994</small>"]
    REQ_DESIGN_950["Encapsulation and abstraction candidates<br><small>REQ-DESIGN-950</small>"]
    REQ_DESIGN_951["Inheritance and polymorphism candidates<br><small>REQ-DESIGN-951</small>"]
    REQ_DESIGN_952["The 'design' report<br><small>REQ-DESIGN-952</small>"]
    REQ_DESIGN_953["Code-writing standards<br><small>REQ-DESIGN-953</small>"]
    REQ_DESIGN_954["Design health in the map<br><small>REQ-DESIGN-954</small>"]
    REQ_DESIGN_955["Brace-language heuristics<br><small>REQ-DESIGN-955</small>"]
    REQ_DESIGN_976["Design candidates in the map<br><small>REQ-DESIGN-976</small>"]
    REQ_DESIGN_978["Class metrics, the C&K half that applies<br><small>REQ-DESIGN-978</small>"]
    REQ_DESIGN_979["What the review could not measure<br><small>REQ-DESIGN-979</small>"]
    REQ_DESIGN_980["The metrics that did not survive calibration<br><small>REQ-DESIGN-980</small>"]
    REQ_DESIGN_991["Advisory data cannot inherit a verdict<br><small>REQ-DESIGN-991</small>"]
    REQ_DOCBUNDLE_840["Flagging a large, unlinked docs/ HTML bundle<br><small>REQ-DOCBUNDLE-840</small>"]
    REQ_DRIFT_841["Hashing only the normative sections<br><small>REQ-DRIFT-841</small>"]
    REQ_DRIFT_842["Reading and writing the drift baseline<br><small>REQ-DRIFT-842</small>"]
    REQ_DRIFT_988["The waiver leaves a trace<br><small>REQ-DRIFT-988</small>"]
    REQ_DRIFTIMPACT_843["Name a drifted requirement's direct dependents<br><small>REQ-DRIFTIMPACT-843</small>"]
    REQ_EXTRACT_849["Which files draft walks<br><small>REQ-EXTRACT-849</small>"]
    REQ_EXTRACT_850["Writing one draft proposal per file<br><small>REQ-EXTRACT-850</small>"]
    REQ_EXTRACT_851["Scoring risk and capturing an authoring hint<br><small>REQ-EXTRACT-851</small>"]
    REQ_EXTRACT_981["The three rungs extraction drafts<br><small>REQ-EXTRACT-981</small>"]
    REQ_FANOUT_852["Counting children and reporting an out-of-band parent<br><small>REQ-FANOUT-852</small>"]
    REQ_FINDINGS_853["Collecting open verify-intent bullets<br><small>REQ-FINDINGS-853</small>"]
    REQ_FINDINGS_854["The raw findings report<br><small>REQ-FINDINGS-854</small>"]
    REQ_FINDINGS_855["The triaged findings report<br><small>REQ-FINDINGS-855</small>"]
    REQ_FINDINGS_856["Findings integration with map and gate<br><small>REQ-FINDINGS-856</small>"]
    REQ_GITRUN_993["One runner for every git question<br><small>REQ-GITRUN-993</small>"]
    REQ_HEALTH_857["health is a read-only snapshot of the whole corpus<br><small>REQ-HEALTH-857</small>"]
    REQ_HEALTH_858["The headline score: green means every axis passes at once<br><small>REQ-HEALTH-858</small>"]
    REQ_HEALTH_859["Component counts, --json parity, and an always-zero exit<br><small>REQ-HEALTH-859</small>"]
    REQ_HEALTH_968["The health record travels with the map<br><small>REQ-HEALTH-968</small>"]
    REQ_REVIEWEDSCORE_109["Reviewed-only health score<br><small>REQ-REVIEWEDSCORE-109</small>"]
    REQ_IMPLEMENT_958["What the implementation brief states<br><small>REQ-IMPLEMENT-958</small>"]
    REQ_IMPLEMENT_959["Pointing at where this kind of code lives<br><small>REQ-IMPLEMENT-959</small>"]
    REQ_INIT_860["Scaffolding the requirements folder and a starter .reqmapignore<br><small>REQ-INIT-860</small>"]
    REQ_INIT_861["Running draft, lock, and map in a fixed order<br><small>REQ-INIT-861</small>"]
    REQ_LEVEL_862["The level field, validated independently of layer<br><small>REQ-LEVEL-862</small>"]
    REQ_LEVELRETROFIT_985["Which rung, and on what evidence<br><small>REQ-LEVELRETROFIT-985</small>"]
    REQ_LEVELRETROFIT_986["Writing a rung into a file somebody else wrote<br><small>REQ-LEVELRETROFIT-986</small>"]
    REQ_LEVELRETROFIT_987["Read-only by default, and honest about what it will not do<br><small>REQ-LEVELRETROFIT-987</small>"]
    REQ_LINT_863["What lint checks and skips<br><small>REQ-LINT-863</small>"]
    REQ_LINT_864["Where the prose checks read from, and what fails a strict run<br><small>REQ-LINT-864</small>"]
    REQ_LINTCHECKS_865["Readability checks: length, stacking, anonymous subjects<br><small>REQ-LINTCHECKS-865</small>"]
    REQ_LINTCHECKS_866["Scope checks: acceptance count, over-scoping, file spread<br><small>REQ-LINTCHECKS-866</small>"]
    REQ_LINTCHECKS_867["Atomic-form parity and layer-mismatch checks<br><small>REQ-LINTCHECKS-867</small>"]
    REQ_LINTCHECKS_868["The vague-term check<br><small>REQ-LINTCHECKS-868</small>"]
    REQ_LINTCHECKS_869["The redundant-modal check<br><small>REQ-LINTCHECKS-869</small>"]
    REQ_MAP_870["Generating _map.json's node graph<br><small>REQ-MAP-870</small>"]
    REQ_MAP_871["Repo, engine version, todos, and freshness checking<br><small>REQ-MAP-871</small>"]
    REQ_MAP_872["Reading contract clauses across wrapped lines<br><small>REQ-MAP-872</small>"]
    REQ_MAP_873["Deduping intent against the contract<br><small>REQ-MAP-873</small>"]
    REQ_MAPDIAGRAMS_874["_map.md: five legended, always-regenerated Mermaid blocks<br><small>REQ-MAPDIAGRAMS-874</small>"]
    REQ_MAPDIAGRAMS_875["Specification Hierarchy: satisfies edges only, code counted not drawn<br><small>REQ-MAPDIAGRAMS-875</small>"]
    REQ_MAPDIAGRAMS_876["System Map: per-area subgraphs, bus edges hidden<br><small>REQ-MAPDIAGRAMS-876</small>"]
    REQ_MAPDIAGRAMS_877["Dependency Map is area-level; Req→Code colors and collapses lines<br><small>REQ-MAPDIAGRAMS-877</small>"]
    REQ_MAPDIAGRAMS_878["Risk diagram: only flagged requirements, each with advice<br><small>REQ-MAPDIAGRAMS-878</small>"]
    REQ_MEMBERDRIFT_879["The member-hash sidecar<br><small>REQ-MEMBERDRIFT-879</small>"]
    REQ_MEMBERDRIFT_880["Warning when code moves ahead of its spec<br><small>REQ-MEMBERDRIFT-880</small>"]
    REQ_MEMBERDRIFT_982["The member hash keys on the tagged definition<br><small>REQ-MEMBERDRIFT-982</small>"]
    REQ_NEW_881["Stamping a fresh requirement file from a template<br><small>REQ-NEW-881</small>"]
    REQ_NEW_882["Refusing to clobber, and a scaffold that lints clean<br><small>REQ-NEW-882</small>"]
    REQ_NEXT_883["next reads the same risk signals the Risk tab reads<br><small>REQ-NEXT-883</small>"]
    REQ_NEXT_884["Four action buckets, two advisory ones, and untagged files<br><small>REQ-NEXT-884</small>"]
    REQ_NEXT_885["Priority, then risk score, then id decide bucket order<br><small>REQ-NEXT-885</small>"]
    REQ_NEXT_886["Each bucket truncates to a top few, --all shows everything<br><small>REQ-NEXT-886</small>"]
    REQ_NEXT_887["An empty registry and a clean one get different messages<br><small>REQ-NEXT-887</small>"]
    REQ_ORPHANCODE_888["Warning on a sizeable file with no requirement link<br><small>REQ-ORPHANCODE-888</small>"]
    REQ_PARSE_890["load_requirements returns one meta/body/path record per file<br><small>REQ-PARSE-890</small>"]
    REQ_PARSE_891["The hand-rolled frontmatter grammar: scalars and lists only<br><small>REQ-PARSE-891</small>"]
    REQ_PARSE_892["Missing frontmatter, underscore files, and a BOM never crash the reader<br><small>REQ-PARSE-892</small>"]
    REQ_ATOMICFORM_053["The atomic requirement form<br><small>REQ-ATOMICFORM-053</small>"]
    REQ_MODULEFILE_056["Several requirements in one file<br><small>REQ-MODULEFILE-056</small>"]
    REQ_PIPE_893["A closed reader ends the command with exit 0<br><small>REQ-PIPE-893</small>"]
    REQ_PROMOTE_894["A surgical edit to the status line<br><small>REQ-PROMOTE-894</small>"]
    REQ_PROMOTE_974["An edited contract loses its confirmation<br><small>REQ-PROMOTE-974</small>"]
    REQ_PROMOTE_TODO_897["Scaffolding a draft from a matched TODO item<br><small>REQ-PROMOTE-TODO-897</small>"]
    REQ_PROMOTE_TODO_898["Refusing an unresolvable promotion<br><small>REQ-PROMOTE-TODO-898</small>"]
    REQ_PROMOTE_TODO_899["TODO.md stays untouched unless --mark-done asks otherwise<br><small>REQ-PROMOTE-TODO-899</small>"]
    REQ_PROSE_900["Sorting prose files into three drafting buckets<br><small>REQ-PROSE-900</small>"]
    REQ_PROSE_901["Scaffolding a draft from a prose file's own headings<br><small>REQ-PROSE-901</small>"]
    REQ_PYFLOOR_902["Refusing an interpreter below the declared floor<br><small>REQ-PYFLOOR-902</small>"]
    REQ_REGISTRYLAG_903["Counting commits since the registry last moved<br><small>REQ-REGISTRYLAG-903</small>"]
    REQ_REGISTRYLAG_904["Reporting lag without ever gating on it<br><small>REQ-REGISTRYLAG-904</small>"]
    REQ_REPRO_905["Rebuilding and diffing each committed artifact in CI<br><small>REQ-REPRO-905</small>"]
    REQ_RETIRE_960["The blast radius of a retirement<br><small>REQ-RETIRE-960</small>"]
    REQ_RETIRE_961["Deprecating, refusing, and never writing by accident<br><small>REQ-RETIRE-961</small>"]
    REQ_RETIRE_962["Deleting a requirement without deleting meaning<br><small>REQ-RETIRE-962</small>"]
    REQ_RETIRE_963["Retiring a class in one operation<br><small>REQ-RETIRE-963</small>"]
    REQ_REVIEW_906["A deterministic plan for an out-of-band AI review<br><small>REQ-REVIEW-906</small>"]
    REQ_ROADMAP_907["A behind roadmap and an unversioned heading, both read-only<br><small>REQ-ROADMAP-907</small>"]
    REQ_ROADMAP_983["The roadmap can also be ahead of the requirements<br><small>REQ-ROADMAP-983</small>"]
    REQ_RULES_947["One registry of gate rules<br><small>REQ-RULES-947</small>"]
    REQ_RULES_948["Codes on every finding, and per-requirement exemption<br><small>REQ-RULES-948</small>"]
    REQ_RULES_989["Drift severity is a repo's own call<br><small>REQ-RULES-989</small>"]
    REQ_SCAN_908["scan_members walks the tree and collects role: ID tags<br><small>REQ-SCAN-908</small>"]
    REQ_SCAN_909["One tag can bind several requirements, and directories are pruned<br><small>REQ-SCAN-909</small>"]
    REQ_SCAN_992["Which lines a tag may live on<br><small>REQ-SCAN-992</small>"]
    REQ_SCANCACHE_911["Caching scan results without changing them<br><small>REQ-SCANCACHE-911</small>"]
    REQ_SEARCH_912["Ranking a query against the corpus<br><small>REQ-SEARCH-912</small>"]
    REQ_SEARCH_913["Printing ranked matches with their score<br><small>REQ-SEARCH-913</small>"]
    REQ_SEARCH_914["The relevance floor and the empty-query message<br><small>REQ-SEARCH-914</small>"]
    REQ_SEARCH_915["Search always exits zero on a well-formed query<br><small>REQ-SEARCH-915</small>"]
    REQ_SEARCH_965["Finding a requirement by its id, and by its literal text<br><small>REQ-SEARCH-965</small>"]
    REQ_SECTIONS_994["One section reader for every consumer<br><small>REQ-SECTIONS-994</small>"]
    REQ_DESCRIPTION_057["One Description section, and Cases instead of Acceptance<br><small>REQ-DESCRIPTION-057</small>"]
    REQ_SELFGATE_916["Five files wire the gate into CI, hooks, and a consumer's Action<br><small>REQ-SELFGATE-916</small>"]
    REQ_SELFGATE_990["The repo's own documentation is checked, not trusted<br><small>REQ-SELFGATE-990</small>"]
    REQ_SHOW_917["A one-screen header, intent and contract<br><small>REQ-SHOW-917</small>"]
    REQ_SHOW_918["Dependencies both ways, and the code members<br><small>REQ-SHOW-918</small>"]
    REQ_SHOW_919["Open questions, risk signals, and a caller-visible exit code<br><small>REQ-SHOW-919</small>"]
    REQ_SIMILAR_920["Reporting overlapping requirement pairs<br><small>REQ-SIMILAR-920</small>"]
    REQ_SIMILAR_921["Building the comparison bag of words<br><small>REQ-SIMILAR-921</small>"]
    REQ_SIMILAR_922["Weighting terms and scoring a pair<br><small>REQ-SIMILAR-922</small>"]
    REQ_SIMILAR_923["The relevance threshold and report format<br><small>REQ-SIMILAR-923</small>"]
    REQ_REDUNDANCY_058["Requirements that say the same thing<br><small>REQ-REDUNDANCY-058</small>"]
    REQ_SITE_924["Inject engine-owned regions into a presentation page<br><small>REQ-SITE-924</small>"]
    REQ_STALEENGINE_925["The gate action reports a stale vendored engine<br><small>REQ-STALEENGINE-925</small>"]
    REQ_STALEENGINE_926["The staleness probe fails open, never the gate itself<br><small>REQ-STALEENGINE-926</small>"]
    REQ_SUGGESTVERIFIES_927["Proposing a tag from a matching test name<br><small>REQ-SUGGESTVERIFIES-927</small>"]
    REQ_SUGGESTVERIFIES_928["Refusing a match that could be wrong<br><small>REQ-SUGGESTVERIFIES-928</small>"]
    REQ_SUGGESTVERIFIES_929["A dry run by default, --apply to write<br><small>REQ-SUGGESTVERIFIES-929</small>"]
    REQ_TESTLINK_930["Checking every tested-by link, at every status<br><small>REQ-TESTLINK-930</small>"]
    REQ_TESTLINK_931["Recognizing a test function by shape, not by parsing<br><small>REQ-TESTLINK-931</small>"]
    REQ_TESTLINK_932["Recognizing Rust, shell, and stdlib-style test entry points<br><small>REQ-TESTLINK-932</small>"]
    REQ_TESTLINK_933["Reporting a broken link as a warning, never an error<br><small>REQ-TESTLINK-933</small>"]
    REQ_TRACE_934["Declaring and checking a satisfies: link<br><small>REQ-TRACE-934</small>"]
    REQ_TRACE_935["How need and aggregate layers are exempt from code checks<br><small>REQ-TRACE-935</small>"]
    REQ_TRACKED_936["Warning when a member is not tracked by git<br><small>REQ-TRACKED-936</small>"]
    REQ_TRANSLATE_937["The cache key, and the promise that nothing shells out<br><small>REQ-TRANSLATE-937</small>"]
    REQ_TRANSLATE_938["Reading the cache: fresh only, and failing open<br><small>REQ-TRANSLATE-938</small>"]
    REQ_TRANSLATE_967["A translation may not carry a field the requirement does not<br><small>REQ-TRANSLATE-967</small>"]
    REQ_TRANSLATE_996["Declaring the requirements language<br><small>REQ-TRANSLATE-996</small>"]
    REQ_UNSCANNEDTAG_939["Warning about a tag the scan never reads<br><small>REQ-UNSCANNEDTAG-939</small>"]
    REQ_VIEWER_940["Writing _map.html from the vendored template<br><small>REQ-VIEWER-940</small>"]
    REQ_VIEWER_941["Escaping the inlined graph for embedded ‹script›<br><small>REQ-VIEWER-941</small>"]
    REQ_VIEWER_942["Ranking nodes and rendering acceptance criteria as authored<br><small>REQ-VIEWER-942</small>"]
    REQ_VIEWER_943["UI chrome language, requirement content untranslated<br><small>REQ-VIEWER-943</small>"]
    REQ_VIEWER_944["Cross-references and header fields in a rendered spec<br><small>REQ-VIEWER-944</small>"]
    REQ_VIEWER_945["Scoping the outline from the registry tally<br><small>REQ-VIEWER-945</small>"]
    REQ_VIEWER_964["The command reference, in the reader's language<br><small>REQ-VIEWER-964</small>"]
    REQ_VIEWER_966["One inbox, with the origin of a signal as a tab<br><small>REQ-VIEWER-966</small>"]
    REQ_VIEWER_969["Two engine-emitted readings in the rail<br><small>REQ-VIEWER-969</small>"]
    REQ_VIEWER_977["The advisory design tab<br><small>REQ-VIEWER-977</small>"]
    REQ_VIEWER_984["Reading a roadmap wider than the screen<br><small>REQ-VIEWER-984</small>"]
    REQ_VIEWER_995["The roadmap has one lane, and it is named for what the chips are<br><small>REQ-VIEWER-995</small>"]
    REQ_VLEVEL_944["A tested-by tag may carry a level suffix<br><small>REQ-VLEVEL-944</small>"]
    REQ_VLEVEL_945["scan_test_levels collects real levels, not documented examples<br><small>REQ-VLEVEL-945</small>"]
    REQ_VLEVEL_946["The gate reads levels: unvalidated needs, system-only bus code<br><small>REQ-VLEVEL-946</small>"]
    REQ_VRUNGS_054["Level-to-verification correspondence<br><small>REQ-VRUNGS-054</small>"]
  end
  subgraph sg_SYS["SYS"]
    SYS_AUTHOR_101["Authoring and evolving a requirement<br><small>SYS-AUTHOR-101</small>"]
    SYS_GATE_102["Keeping code and specification in step<br><small>SYS-GATE-102</small>"]
    SYS_QUALITY_104["Keeping requirements readable<br><small>SYS-QUALITY-104</small>"]
    SYS_READ_103["Reading a repository<br><small>SYS-READ-103</small>"]
    SYS_REPORT_105["Answering what is here and what to do next<br><small>SYS-REPORT-105</small>"]
    SYS_SHIP_108["Adopting and shipping the engine<br><small>SYS-SHIP-108</small>"]
    SYS_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>SYS-SSOT-001</small>"]
    SYS_VISUAL_106["Seeing the system at a glance<br><small>SYS-VISUAL-106</small>"]
    SYS_VMODEL_107["Placing a requirement in the V<br><small>SYS-VMODEL-107</small>"]
  end
  ARCH_ATOMICITY_049 --> ARCH_LINT_014
  ARCH_AUDIT_065 --> ARCH_NEXT_013
  ARCH_AUDIT_065 --> ARCH_SIMILAR_016
  ARCH_AUDIT_065 --> ARCH_COVERAGE_029
  ARCH_AUDIT_065 --> ARCH_DESIGN_061
  ARCH_CONTEXT_048 --> ARCH_MAP_007
  ARCH_COVERAGE_029 --> ARCH_NEXT_013
  ARCH_DECOMPOSE_050 --> ARCH_ATOMICITY_049
  ARCH_DECOMPOSE_050 --> ARCH_LINT_014
  ARCH_DECOMPOSE_050 --> ARCH_NEW_004
  ARCH_DESIGN_061 --> ARCH_CMDREGISTRY_033
  ARCH_FANOUT_052 --> ARCH_LINT_014
  ARCH_FANOUT_052 --> ARCH_LEVEL_051
  ARCH_IMPLEMENT_063 --> ARCH_SIMILAR_016
  ARCH_IMPLEMENT_063 --> ARCH_CLARIFY_062
  ARCH_INIT_012 --> ARCH_EXTRACT_008
  ARCH_INIT_012 --> ARCH_MAP_007
  ARCH_LEVELRETROFIT_066 --> ARCH_LEVEL_051
  ARCH_LINTCHECKS_025 --> ARCH_LINT_014
  ARCH_MAPDIAGRAMS_055 --> ARCH_MAP_007
  ARCH_NEXT_013 --> ARCH_MAP_007
  ARCH_PIPE_046 --> ARCH_CMDREGISTRY_033
  ARCH_PROMOTE_TODO_001 --> ARCH_NEW_004
  ARCH_PROSE_024 --> ARCH_EXTRACT_008
  ARCH_REGISTRYLAG_035 --> ARCH_HEALTH_017
  ARCH_REPRO_041 --> ARCH_SELFGATE_039
  ARCH_ROADMAP_038 --> ARCH_HEALTH_017
  ARCH_SEARCH_036 --> ARCH_SIMILAR_016
  REQ_REDUNDANCY_058 --> ARCH_NEXT_013
  ARCH_SITE_026 --> ARCH_MAP_007
  ARCH_SITE_026 --> ARCH_VIEWER_007
  ARCH_STALEENGINE_043 --> ARCH_SELFGATE_039
  ARCH_SUGGESTVERIFIES_047 --> ARCH_ACVERIFY_019
  ARCH_TRANSLATE_044 --> ARCH_MAP_007
  ARCH_TRANSLATE_044 --> ARCH_VIEWER_007
  ARCH_VIEWER_007 --> ARCH_MAP_007
  REQ_VRUNGS_054 --> ARCH_LEVEL_051
  style ARCH_CONFIG_060 stroke-width:3px
  style REQ_CONFIG_949 stroke-width:3px
  style ARCH_DRIFT_003 stroke-width:3px
  style REQ_DRIFT_841 stroke-width:3px
  style REQ_DRIFT_842 stroke-width:3px
  style ARCH_GITRUN_067 stroke-width:3px
  style REQ_GITRUN_993 stroke-width:3px
  style ARCH_PARSE_001 stroke-width:3px
  style REQ_PARSE_890 stroke-width:3px
  style REQ_PARSE_891 stroke-width:3px
  style REQ_PARSE_892 stroke-width:3px
  style REQ_MODULEFILE_056 stroke-width:3px
  style ARCH_RULES_059 stroke-width:3px
  style REQ_RULES_947 stroke-width:3px
  style REQ_RULES_948 stroke-width:3px
  style ARCH_SCAN_002 stroke-width:3px
  style REQ_SCAN_908 stroke-width:3px
  style REQ_SCAN_909 stroke-width:3px
  style REQ_SCAN_992 stroke-width:3px
  style ARCH_SECTIONS_068 stroke-width:3px
  style REQ_SECTIONS_994 stroke-width:3px
  style REQ_DESCRIPTION_057 stroke-width:3px
```

## Requirement-to-Code

_Each system/architecture requirement → its code; arrow label = role (`implements` / `tested-by`). Red = confirmed but no code linked (a gap); grey = baseline/draft, not linked yet (expected). Code-level requirements are omitted here (see the viewer)._

```mermaid
graph LR
  ARCH_ACVERIFY_019["Per-criterion test coverage<br><small>ARCH-ACVERIFY-019</small>"]
  f_plugin_scripts_test_reqmap_gate_py_689_787["plugin/scripts/test_reqmap_gate.py:689-787"]
  ARCH_ACVERIFY_019 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_689_787
  f_plugin_scripts_test_reqmap_scan_py_544_890["plugin/scripts/test_reqmap_scan.py:544-890"]
  ARCH_ACVERIFY_019 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_544_890
  f_plugin_scripts_reqmap_engine_acceptance_py_17_90["plugin/scripts/reqmap_engine/acceptance.py:17-90"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_acceptance_py_17_90
  f_plugin_scripts_reqmap_engine_mapdata_py_18["plugin/scripts/reqmap_engine/mapdata.py:18"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_18
  f_plugin_scripts_reqmap_engine_rules_py_182["plugin/scripts/reqmap_engine/rules.py:182"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_182
  f_plugin_scripts_reqmap_engine_scan_py_134_241["plugin/scripts/reqmap_engine/scan.py:134-241"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_134_241
  ARCH_ATOMICITY_049["Statement atomicity<br><small>ARCH-ATOMICITY-049</small>"]
  f_plugin_scripts_test_reqmap_author_py_1470_1934["plugin/scripts/test_reqmap_author.py:1470-1934"]
  ARCH_ATOMICITY_049 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1470_1934
  f_plugin_scripts_reqmap_engine_lintrules_py_108_118["plugin/scripts/reqmap_engine/lintrules.py:108-118"]
  ARCH_ATOMICITY_049 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_108_118
  ARCH_AUDIT_065["One report of everything the engine can discover<br><small>ARCH-AUDIT-065</small>"]
  f_plugin_scripts_test_reqmap_report_py_2734_4744["plugin/scripts/test_reqmap_report.py:2734-4744"]
  ARCH_AUDIT_065 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2734_4744
  f_plugin_scripts_reqmap_engine_audit_py_23_338["plugin/scripts/reqmap_engine/audit.py:23-338"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_audit_py_23_338
  f_plugin_scripts_reqmap_engine_relevel_py_19_206["plugin/scripts/reqmap_engine/relevel.py:19-206"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_relevel_py_19_206
  f_plugin_scripts_reqmap_engine_rules_py_286["plugin/scripts/reqmap_engine/rules.py:286"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_286
  f_plugin_scripts_reqmap_engine_similar_py_35_63["plugin/scripts/reqmap_engine/similar.py:35-63"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_similar_py_35_63
  ARCH_CANDIDATES_009["Capability candidates (extraction plan)<br><small>ARCH-CANDIDATES-009</small>"]
  f_plugin_scripts_test_reqmap_author_py_166_2134["plugin/scripts/test_reqmap_author.py:166-2134"]
  ARCH_CANDIDATES_009 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_166_2134
  f_plugin_scripts_test_reqmap_scan_py_466_507["plugin/scripts/test_reqmap_scan.py:466-507"]
  ARCH_CANDIDATES_009 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_466_507
  f_plugin_scripts_reqmap_engine_candidates_py_22_275["plugin/scripts/reqmap_engine/candidates.py:22-275"]
  ARCH_CANDIDATES_009 -->|implements| f_plugin_scripts_reqmap_engine_candidates_py_22_275
  f_plugin_scripts_reqmap_engine_tags_py_288["plugin/scripts/reqmap_engine/tags.py:288"]
  ARCH_CANDIDATES_009 -->|implements| f_plugin_scripts_reqmap_engine_tags_py_288
  ARCH_CHECK_006["The gate<br><small>ARCH-CHECK-006</small>"]
  f_plugin_hooks_pre_commit_2["plugin/hooks/pre-commit:2"]
  ARCH_CHECK_006 -->|implements| f_plugin_hooks_pre_commit_2
  f_plugin_scripts_test_reqmap_gate_py_42_2837["plugin/scripts/test_reqmap_gate.py:42-2837"]
  ARCH_CHECK_006 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_42_2837
  f_plugin_scripts_test_reqmap_report_py_568["plugin/scripts/test_reqmap_report.py:568"]
  ARCH_CHECK_006 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_568
  f_plugin_scripts_reqmap_engine___init___py_11["plugin/scripts/reqmap_engine/__init__.py:11"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine___init___py_11
  f_plugin_scripts_reqmap_engine_gate_py_56_178["plugin/scripts/reqmap_engine/gate.py:56-178"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_gate_py_56_178
  f_plugin_scripts_reqmap_engine_locks_py_174_343["plugin/scripts/reqmap_engine/locks.py:174-343"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_locks_py_174_343
  f_plugin_scripts_reqmap_engine_mapjson_py_9["plugin/scripts/reqmap_engine/mapjson.py:9"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_mapjson_py_9
  f_plugin_scripts_reqmap_engine_model_py_189["plugin/scripts/reqmap_engine/model.py:189"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_model_py_189
  f_plugin_scripts_reqmap_engine_rules_py_399["plugin/scripts/reqmap_engine/rules.py:399"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_399
  f_plugin_scripts_reqmap_engine_sections_py_96_231["plugin/scripts/reqmap_engine/sections.py:96-231"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_sections_py_96_231
  ARCH_CLARIFY_062["Questions a requirement has not answered<br><small>ARCH-CLARIFY-062</small>"]
  f_plugin_scripts_test_reqmap_author_py_2224_2917["plugin/scripts/test_reqmap_author.py:2224-2917"]
  ARCH_CLARIFY_062 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_2224_2917
  f_plugin_scripts_reqmap_engine_clarify_py_109_244["plugin/scripts/reqmap_engine/clarify.py:109-244"]
  ARCH_CLARIFY_062 -->|implements| f_plugin_scripts_reqmap_engine_clarify_py_109_244
  ARCH_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>ARCH-CMDREGISTRY-033</small>"]
  f_plugin_scripts_reqmap_py_112_226["plugin/scripts/reqmap.py:112-226"]
  ARCH_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_py_112_226
  f_plugin_scripts_test_reqmap_report_py_1889_4526["plugin/scripts/test_reqmap_report.py:1889-4526"]
  ARCH_CMDREGISTRY_033 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1889_4526
  f_plugin_scripts_reqmap_engine_commands_py_14["plugin/scripts/reqmap_engine/commands.py:14"]
  ARCH_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_engine_commands_py_14
  f_plugin_scripts_reqmap_engine_registry_py_12_42["plugin/scripts/reqmap_engine/registry.py:12-42"]
  ARCH_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_engine_registry_py_12_42
  ARCH_CONFIG_060["Per-repo configuration file<br><small>ARCH-CONFIG-060</small>"]
  f_plugin_scripts_reqmap_py_389["plugin/scripts/reqmap.py:389"]
  ARCH_CONFIG_060 -->|implements| f_plugin_scripts_reqmap_py_389
  f_plugin_scripts_test_reqmap_report_py_2606["plugin/scripts/test_reqmap_report.py:2606"]
  ARCH_CONFIG_060 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2606
  f_plugin_scripts_reqmap_engine_config_py_188_198["plugin/scripts/reqmap_engine/config.py:188-198"]
  ARCH_CONFIG_060 -->|implements| f_plugin_scripts_reqmap_engine_config_py_188_198
  ARCH_CONTEXT_048["Consolidated Context section<br><small>ARCH-CONTEXT-048</small>"]
  f_plugin_scripts_test_reqmap_report_py_378_3653["plugin/scripts/test_reqmap_report.py:378-3653"]
  ARCH_CONTEXT_048 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_378_3653
  f_plugin_scripts_reqmap_engine_text_py_178["plugin/scripts/reqmap_engine/text.py:178"]
  ARCH_CONTEXT_048 -->|implements| f_plugin_scripts_reqmap_engine_text_py_178
  ARCH_COVERAGE_029["Untagged-code coverage signal<br><small>ARCH-COVERAGE-029</small>"]
  f_plugin_scripts_test_reqmap_report_py_1363["plugin/scripts/test_reqmap_report.py:1363"]
  ARCH_COVERAGE_029 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1363
  f_plugin_scripts_reqmap_engine_health_py_231["plugin/scripts/reqmap_engine/health.py:231"]
  ARCH_COVERAGE_029 -->|implements| f_plugin_scripts_reqmap_engine_health_py_231
  f_plugin_scripts_reqmap_engine_orphans_py_134["plugin/scripts/reqmap_engine/orphans.py:134"]
  ARCH_COVERAGE_029 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_134
  ARCH_DECOMPOSE_050["Clause decomposition scaffold<br><small>ARCH-DECOMPOSE-050</small>"]
  f_plugin_scripts_test_reqmap_author_py_1548_3038["plugin/scripts/test_reqmap_author.py:1548-3038"]
  ARCH_DECOMPOSE_050 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1548_3038
  f_plugin_scripts_test_reqmap_report_py_4640["plugin/scripts/test_reqmap_report.py:4640"]
  ARCH_DECOMPOSE_050 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4640
  f_plugin_scripts_reqmap_engine_decompose_py_53_107["plugin/scripts/reqmap_engine/decompose.py:53-107"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_decompose_py_53_107
  f_plugin_scripts_reqmap_engine_groups_py_61_400["plugin/scripts/reqmap_engine/groups.py:61-400"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_groups_py_61_400
  f_plugin_scripts_reqmap_engine_lint_py_72_89["plugin/scripts/reqmap_engine/lint.py:72-89"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_72_89
  f_plugin_scripts_reqmap_engine_lintrules_py_17["plugin/scripts/reqmap_engine/lintrules.py:17"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_17
  ARCH_DESIGN_061["Advisory design review<br><small>ARCH-DESIGN-061</small>"]
  f_plugin_scripts_test_reqmap_report_py_2989_4640["plugin/scripts/test_reqmap_report.py:2989-4640"]
  ARCH_DESIGN_061 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2989_4640
  f_plugin_scripts_reqmap_engine_design_py_72["plugin/scripts/reqmap_engine/design.py:72"]
  ARCH_DESIGN_061 -->|implements| f_plugin_scripts_reqmap_engine_design_py_72
  f_plugin_scripts_reqmap_engine_design_python_py_128["plugin/scripts/reqmap_engine/design_python.py:128"]
  ARCH_DESIGN_061 -->|implements| f_plugin_scripts_reqmap_engine_design_python_py_128
  f_plugin_scripts_reqmap_engine_design_report_py_15_87["plugin/scripts/reqmap_engine/design_report.py:15-87"]
  ARCH_DESIGN_061 -->|implements| f_plugin_scripts_reqmap_engine_design_report_py_15_87
  ARCH_DOCBUNDLE_026["Untagged doc-bundle warning<br><small>ARCH-DOCBUNDLE-026</small>"]
  f_plugin_scripts_test_reqmap_gate_py_239["plugin/scripts/test_reqmap_gate.py:239"]
  ARCH_DOCBUNDLE_026 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_239
  f_plugin_scripts_reqmap_engine_orphans_py_100["plugin/scripts/reqmap_engine/orphans.py:100"]
  ARCH_DOCBUNDLE_026 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_100
  f_plugin_scripts_reqmap_engine_rules_py_347["plugin/scripts/reqmap_engine/rules.py:347"]
  ARCH_DOCBUNDLE_026 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_347
  ARCH_DRIFT_003["Contract hashing & lock<br><small>ARCH-DRIFT-003</small>"]
  f_plugin_scripts_test_reqmap_gate_py_52_2693["plugin/scripts/test_reqmap_gate.py:52-2693"]
  ARCH_DRIFT_003 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_52_2693
  f_plugin_scripts_test_reqmap_scan_py_1401["plugin/scripts/test_reqmap_scan.py:1401"]
  ARCH_DRIFT_003 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_1401
  f_plugin_scripts_reqmap_engine_locks_py_11_120["plugin/scripts/reqmap_engine/locks.py:11-120"]
  ARCH_DRIFT_003 -->|implements| f_plugin_scripts_reqmap_engine_locks_py_11_120
  f_plugin_scripts_reqmap_engine_rules_py_316["plugin/scripts/reqmap_engine/rules.py:316"]
  ARCH_DRIFT_003 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_316
  f_plugin_scripts_reqmap_engine_sections_py_179["plugin/scripts/reqmap_engine/sections.py:179"]
  ARCH_DRIFT_003 -->|implements| f_plugin_scripts_reqmap_engine_sections_py_179
  ARCH_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>ARCH-DRIFTIMPACT-035</small>"]
  f_plugin_scripts_test_reqmap_gate_py_454["plugin/scripts/test_reqmap_gate.py:454"]
  ARCH_DRIFTIMPACT_035 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_454
  f_plugin_scripts_test_reqmap_report_py_4111["plugin/scripts/test_reqmap_report.py:4111"]
  ARCH_DRIFTIMPACT_035 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4111
  f_plugin_scripts_reqmap_engine_rules_py_316["plugin/scripts/reqmap_engine/rules.py:316"]
  ARCH_DRIFTIMPACT_035 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_316
  ARCH_EXTRACT_008["Legacy extraction<br><small>ARCH-EXTRACT-008</small>"]
  f_plugin_scripts_test_reqmap_author_py_30_1986["plugin/scripts/test_reqmap_author.py:30-1986"]
  ARCH_EXTRACT_008 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_30_1986
  f_plugin_scripts_test_reqmap_scan_py_451["plugin/scripts/test_reqmap_scan.py:451"]
  ARCH_EXTRACT_008 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_451
  f_plugin_scripts_reqmap_engine_draft_py_10_288["plugin/scripts/reqmap_engine/draft.py:10-288"]
  ARCH_EXTRACT_008 -->|implements| f_plugin_scripts_reqmap_engine_draft_py_10_288
  ARCH_FANOUT_052["Hierarchy breadth<br><small>ARCH-FANOUT-052</small>"]
  f_plugin_scripts_test_reqmap_author_py_1748_1947["plugin/scripts/test_reqmap_author.py:1748-1947"]
  ARCH_FANOUT_052 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1748_1947
  f_plugin_scripts_reqmap_engine_lint_py_14_54["plugin/scripts/reqmap_engine/lint.py:14-54"]
  ARCH_FANOUT_052 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_14_54
  ARCH_FINDINGS_010["Open-findings report<br><small>ARCH-FINDINGS-010</small>"]
  f_plugin_scripts_test_reqmap_report_py_153_3704["plugin/scripts/test_reqmap_report.py:153-3704"]
  ARCH_FINDINGS_010 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_153_3704
  f_plugin_scripts_reqmap_engine_findings_py_13_128["plugin/scripts/reqmap_engine/findings.py:13-128"]
  ARCH_FINDINGS_010 -->|implements| f_plugin_scripts_reqmap_engine_findings_py_13_128
  f_plugin_scripts_reqmap_engine_mapcmd_py_43_154["plugin/scripts/reqmap_engine/mapcmd.py:43-154"]
  ARCH_FINDINGS_010 -->|implements| f_plugin_scripts_reqmap_engine_mapcmd_py_43_154
  f_plugin_scripts_reqmap_engine_text_py_158["plugin/scripts/reqmap_engine/text.py:158"]
  ARCH_FINDINGS_010 -->|implements| f_plugin_scripts_reqmap_engine_text_py_158
  ARCH_GITRUN_067["Talking to git<br><small>ARCH-GITRUN-067</small>"]
  f_plugin_scripts_test_reqmap_scan_py_1482["plugin/scripts/test_reqmap_scan.py:1482"]
  ARCH_GITRUN_067 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_1482
  f_plugin_scripts_reqmap_engine_git_py_6_43["plugin/scripts/reqmap_engine/git.py:6-43"]
  ARCH_GITRUN_067 -->|implements| f_plugin_scripts_reqmap_engine_git_py_6_43
  ARCH_HEALTH_017["Corpus health snapshot<br><small>ARCH-HEALTH-017</small>"]
  f_plugin_scripts_test_reqmap_report_py_1235_4640["plugin/scripts/test_reqmap_report.py:1235-4640"]
  ARCH_HEALTH_017 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1235_4640
  f_plugin_scripts_reqmap_engine_health_py_16_331["plugin/scripts/reqmap_engine/health.py:16-331"]
  ARCH_HEALTH_017 -->|implements| f_plugin_scripts_reqmap_engine_health_py_16_331
  ARCH_IMPLEMENT_063["The brief for implementing a requirement<br><small>ARCH-IMPLEMENT-063</small>"]
  f_plugin_scripts_test_reqmap_author_py_2354["plugin/scripts/test_reqmap_author.py:2354"]
  ARCH_IMPLEMENT_063 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_2354
  f_plugin_scripts_reqmap_engine_implement_py_15_120["plugin/scripts/reqmap_engine/implement.py:15-120"]
  ARCH_IMPLEMENT_063 -->|implements| f_plugin_scripts_reqmap_engine_implement_py_15_120
  ARCH_INIT_012["First-use bootstrap<br><small>ARCH-INIT-012</small>"]
  f_plugin_scripts_test_reqmap_author_py_432_589["plugin/scripts/test_reqmap_author.py:432-589"]
  ARCH_INIT_012 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_432_589
  f_plugin_scripts_test_reqmap_report_py_2084_4640["plugin/scripts/test_reqmap_report.py:2084-4640"]
  ARCH_INIT_012 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2084_4640
  f_plugin_scripts_reqmap_engine_init_py_93_132["plugin/scripts/reqmap_engine/init.py:93-132"]
  ARCH_INIT_012 -->|implements| f_plugin_scripts_reqmap_engine_init_py_93_132
  ARCH_LEVEL_051["Specification level<br><small>ARCH-LEVEL-051</small>"]
  f_plugin_scripts_test_reqmap_gate_py_2233_2599["plugin/scripts/test_reqmap_gate.py:2233-2599"]
  ARCH_LEVEL_051 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2233_2599
  f_plugin_scripts_reqmap_engine_mapdata_py_61["plugin/scripts/reqmap_engine/mapdata.py:61"]
  ARCH_LEVEL_051 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_61
  f_plugin_scripts_reqmap_engine_model_py_23["plugin/scripts/reqmap_engine/model.py:23"]
  ARCH_LEVEL_051 -->|implements| f_plugin_scripts_reqmap_engine_model_py_23
  f_plugin_scripts_reqmap_engine_rules_py_35["plugin/scripts/reqmap_engine/rules.py:35"]
  ARCH_LEVEL_051 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_35
  ARCH_LEVELRETROFIT_066["Giving an existing corpus the three rungs<br><small>ARCH-LEVELRETROFIT-066</small>"]
  f_plugin_scripts_test_reqmap_author_py_1058["plugin/scripts/test_reqmap_author.py:1058"]
  ARCH_LEVELRETROFIT_066 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1058
  f_plugin_scripts_reqmap_engine_levels_py_9_126["plugin/scripts/reqmap_engine/levels.py:9-126"]
  ARCH_LEVELRETROFIT_066 -->|implements| f_plugin_scripts_reqmap_engine_levels_py_9_126
  ARCH_LINT_014["Requirement readability linter<br><small>ARCH-LINT-014</small>"]
  f_plugin_scripts_test_reqmap_author_py_690["plugin/scripts/test_reqmap_author.py:690"]
  ARCH_LINT_014 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_690
  f_plugin_scripts_reqmap_engine_lint_py_13_89["plugin/scripts/reqmap_engine/lint.py:13-89"]
  ARCH_LINT_014 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_13_89
  f_plugin_scripts_reqmap_engine_lintrules_py_78_102["plugin/scripts/reqmap_engine/lintrules.py:78-102"]
  ARCH_LINT_014 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_78_102
  ARCH_LINTCHECKS_025["Readability & scope checks<br><small>ARCH-LINTCHECKS-025</small>"]
  f_plugin_scripts_test_reqmap_author_py_690_1203["plugin/scripts/test_reqmap_author.py:690-1203"]
  ARCH_LINTCHECKS_025 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_690_1203
  f_plugin_scripts_test_reqmap_scan_py_528["plugin/scripts/test_reqmap_scan.py:528"]
  ARCH_LINTCHECKS_025 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_528
  f_plugin_scripts_reqmap_engine_lint_py_13_53["plugin/scripts/reqmap_engine/lint.py:13-53"]
  ARCH_LINTCHECKS_025 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_13_53
  f_plugin_scripts_reqmap_engine_lintrules_py_96_404["plugin/scripts/reqmap_engine/lintrules.py:96-404"]
  ARCH_LINTCHECKS_025 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_96_404
  ARCH_MAP_007["Requirement graph (_map.json)<br><small>ARCH-MAP-007</small>"]
  f_plugin_scripts_test_reqmap_gate_py_936_2193["plugin/scripts/test_reqmap_gate.py:936-2193"]
  ARCH_MAP_007 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_936_2193
  f_plugin_scripts_test_reqmap_report_py_258_4640["plugin/scripts/test_reqmap_report.py:258-4640"]
  ARCH_MAP_007 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_258_4640
  f_plugin_scripts_test_reqmap_scan_py_544["plugin/scripts/test_reqmap_scan.py:544"]
  ARCH_MAP_007 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_544
  f_plugin_scripts_reqmap_engine_acceptance_py_66["plugin/scripts/reqmap_engine/acceptance.py:66"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_acceptance_py_66
  f_plugin_scripts_reqmap_engine_git_py_48["plugin/scripts/reqmap_engine/git.py:48"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_git_py_48
  f_plugin_scripts_reqmap_engine_mapcmd_py_22_182["plugin/scripts/reqmap_engine/mapcmd.py:22-182"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapcmd_py_22_182
  f_plugin_scripts_reqmap_engine_mapdata_py_38["plugin/scripts/reqmap_engine/mapdata.py:38"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_38
  f_plugin_scripts_reqmap_engine_mapjson_py_57_97["plugin/scripts/reqmap_engine/mapjson.py:57-97"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapjson_py_57_97
  f_plugin_scripts_reqmap_engine_mapmd_py_42["plugin/scripts/reqmap_engine/mapmd.py:42"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapmd_py_42
  f_plugin_scripts_reqmap_engine_model_py_232["plugin/scripts/reqmap_engine/model.py:232"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_model_py_232
  f_plugin_scripts_reqmap_engine_rules_py_408["plugin/scripts/reqmap_engine/rules.py:408"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_408
  f_plugin_scripts_reqmap_engine_text_py_28_109["plugin/scripts/reqmap_engine/text.py:28-109"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_text_py_28_109
  ARCH_MAPDIAGRAMS_055["Mermaid diagrams (_map.md)<br><small>ARCH-MAPDIAGRAMS-055</small>"]
  f_plugin_scripts_test_reqmap_report_py_31_4135["plugin/scripts/test_reqmap_report.py:31-4135"]
  ARCH_MAPDIAGRAMS_055 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_31_4135
  f_plugin_scripts_reqmap_engine_mapmd_py_49_358["plugin/scripts/reqmap_engine/mapmd.py:49-358"]
  ARCH_MAPDIAGRAMS_055 -->|implements| f_plugin_scripts_reqmap_engine_mapmd_py_49_358
  ARCH_MEMBERDRIFT_027["Reverse-direction member drift<br><small>ARCH-MEMBERDRIFT-027</small>"]
  f_plugin_scripts_test_reqmap_gate_py_294["plugin/scripts/test_reqmap_gate.py:294"]
  ARCH_MEMBERDRIFT_027 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_294
  f_plugin_scripts_reqmap_engine_locks_py_53_290["plugin/scripts/reqmap_engine/locks.py:53-290"]
  ARCH_MEMBERDRIFT_027 -->|implements| f_plugin_scripts_reqmap_engine_locks_py_53_290
  f_plugin_scripts_reqmap_engine_rules_py_330["plugin/scripts/reqmap_engine/rules.py:330"]
  ARCH_MEMBERDRIFT_027 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_330
  ARCH_NEW_004["Scaffold a requirement<br><small>ARCH-NEW-004</small>"]
  f_plugin_scripts_test_reqmap_author_py_99_2955["plugin/scripts/test_reqmap_author.py:99-2955"]
  ARCH_NEW_004 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_99_2955
  f_plugin_scripts_reqmap_engine_author_py_93_133["plugin/scripts/reqmap_engine/author.py:93-133"]
  ARCH_NEW_004 -->|implements| f_plugin_scripts_reqmap_engine_author_py_93_133
  ARCH_NEXT_013["What-should-I-do-next report<br><small>ARCH-NEXT-013</small>"]
  f_plugin_scripts_test_reqmap_author_py_1634["plugin/scripts/test_reqmap_author.py:1634"]
  ARCH_NEXT_013 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1634
  f_plugin_scripts_test_reqmap_report_py_835_3426["plugin/scripts/test_reqmap_report.py:835-3426"]
  ARCH_NEXT_013 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_835_3426
  f_plugin_scripts_reqmap_engine_lintrules_py_17["plugin/scripts/reqmap_engine/lintrules.py:17"]
  ARCH_NEXT_013 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_17
  f_plugin_scripts_reqmap_engine_orphans_py_134["plugin/scripts/reqmap_engine/orphans.py:134"]
  ARCH_NEXT_013 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_134
  f_plugin_scripts_reqmap_engine_risk_py_12_192["plugin/scripts/reqmap_engine/risk.py:12-192"]
  ARCH_NEXT_013 -->|implements| f_plugin_scripts_reqmap_engine_risk_py_12_192
  ARCH_ORPHANCODE_034["Orphan-code warning<br><small>ARCH-ORPHANCODE-034</small>"]
  f_plugin_scripts_test_reqmap_gate_py_394_2647["plugin/scripts/test_reqmap_gate.py:394-2647"]
  ARCH_ORPHANCODE_034 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_394_2647
  f_plugin_scripts_reqmap_engine_orphans_py_159["plugin/scripts/reqmap_engine/orphans.py:159"]
  ARCH_ORPHANCODE_034 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_159
  f_plugin_scripts_reqmap_engine_rules_py_379["plugin/scripts/reqmap_engine/rules.py:379"]
  ARCH_ORPHANCODE_034 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_379
  ARCH_PARSE_001["Requirement reading<br><small>ARCH-PARSE-001</small>"]
  f_plugin_scripts_test_reqmap_report_py_4640["plugin/scripts/test_reqmap_report.py:4640"]
  ARCH_PARSE_001 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4640
  f_plugin_scripts_test_reqmap_scan_py_31_859["plugin/scripts/test_reqmap_scan.py:31-859"]
  ARCH_PARSE_001 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_31_859
  f_plugin_scripts_reqmap_engine_model_py_60_162["plugin/scripts/reqmap_engine/model.py:60-162"]
  ARCH_PARSE_001 -->|implements| f_plugin_scripts_reqmap_engine_model_py_60_162
  f_plugin_scripts_reqmap_engine_parse_py_7_97["plugin/scripts/reqmap_engine/parse.py:7-97"]
  ARCH_PARSE_001 -->|implements| f_plugin_scripts_reqmap_engine_parse_py_7_97
  ARCH_PIPE_046["A closed output pipe ends a command quietly<br><small>ARCH-PIPE-046</small>"]
  f_plugin_scripts_reqmap_py_442_460["plugin/scripts/reqmap.py:442-460"]
  ARCH_PIPE_046 -->|implements| f_plugin_scripts_reqmap_py_442_460
  f_plugin_scripts_test_reqmap_gate_py_2212["plugin/scripts/test_reqmap_gate.py:2212"]
  ARCH_PIPE_046 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2212
  ARCH_PROMOTE_011["Confirmation is a human's answer, and an edit takes it back<br><small>ARCH-PROMOTE-011</small>"]
  f_plugin_scripts_test_reqmap_author_py_377_2771["plugin/scripts/test_reqmap_author.py:377-2771"]
  ARCH_PROMOTE_011 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_377_2771
  f_plugin_scripts_test_reqmap_gate_py_825["plugin/scripts/test_reqmap_gate.py:825"]
  ARCH_PROMOTE_011 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_825
  f_plugin_scripts_test_reqmap_report_py_1586_2030["plugin/scripts/test_reqmap_report.py:1586-2030"]
  ARCH_PROMOTE_011 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1586_2030
  f_plugin_scripts_reqmap_engine_author_py_263_289["plugin/scripts/reqmap_engine/author.py:263-289"]
  ARCH_PROMOTE_011 -->|implements| f_plugin_scripts_reqmap_engine_author_py_263_289
  ARCH_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>ARCH-PROMOTE-TODO-001</small>"]
  f_plugin_scripts_test_reqmap_author_py_1235_2083["plugin/scripts/test_reqmap_author.py:1235-2083"]
  ARCH_PROMOTE_TODO_001 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1235_2083
  f_plugin_scripts_test_reqmap_report_py_2030["plugin/scripts/test_reqmap_report.py:2030"]
  ARCH_PROMOTE_TODO_001 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2030
  f_plugin_scripts_reqmap_engine_author_py_160_229["plugin/scripts/reqmap_engine/author.py:160-229"]
  ARCH_PROMOTE_TODO_001 -->|implements| f_plugin_scripts_reqmap_engine_author_py_160_229
  ARCH_PROSE_024["Prose capability classification & drafting<br><small>ARCH-PROSE-024</small>"]
  f_plugin_scripts_test_reqmap_scan_py_357_1263["plugin/scripts/test_reqmap_scan.py:357-1263"]
  ARCH_PROSE_024 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_357_1263
  f_plugin_scripts_reqmap_engine_draft_py_18_222["plugin/scripts/reqmap_engine/draft.py:18-222"]
  ARCH_PROSE_024 -->|implements| f_plugin_scripts_reqmap_engine_draft_py_18_222
  f_plugin_scripts_reqmap_engine_tags_py_260["plugin/scripts/reqmap_engine/tags.py:260"]
  ARCH_PROSE_024 -->|implements| f_plugin_scripts_reqmap_engine_tags_py_260
  ARCH_PYFLOOR_040["Declared Python support floor<br><small>ARCH-PYFLOOR-040</small>"]
  f__github_workflows_ci_yml_3[".github/workflows/ci.yml:3"]
  ARCH_PYFLOOR_040 -->|implements| f__github_workflows_ci_yml_3
  f_plugin_scripts_reqmap_py_93["plugin/scripts/reqmap.py:93"]
  ARCH_PYFLOOR_040 -->|implements| f_plugin_scripts_reqmap_py_93
  f_plugin_scripts_test_reqmap_gate_py_1918_2613["plugin/scripts/test_reqmap_gate.py:1918-2613"]
  ARCH_PYFLOOR_040 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_1918_2613
  ARCH_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>ARCH-REGISTRYLAG-035</small>"]
  f_plugin_scripts_test_reqmap_report_py_1387["plugin/scripts/test_reqmap_report.py:1387"]
  ARCH_REGISTRYLAG_035 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1387
  f_plugin_scripts_reqmap_engine_health_py_90_238["plugin/scripts/reqmap_engine/health.py:90-238"]
  ARCH_REGISTRYLAG_035 -->|implements| f_plugin_scripts_reqmap_engine_health_py_90_238
  ARCH_REPRO_041["Committed build artifacts stay re-derivable<br><small>ARCH-REPRO-041</small>"]
  f__github_workflows_ci_yml_4[".github/workflows/ci.yml:4"]
  ARCH_REPRO_041 -->|implements| f__github_workflows_ci_yml_4
  ARCH_RETIRE_064["Taking a requirement out of service<br><small>ARCH-RETIRE-064</small>"]
  f_plugin_scripts_test_reqmap_author_py_1822_2983["plugin/scripts/test_reqmap_author.py:1822-2983"]
  ARCH_RETIRE_064 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1822_2983
  f_plugin_scripts_test_reqmap_report_py_4640["plugin/scripts/test_reqmap_report.py:4640"]
  ARCH_RETIRE_064 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4640
  f_plugin_scripts_reqmap_engine_retire_py_15_243["plugin/scripts/reqmap_engine/retire.py:15-243"]
  ARCH_RETIRE_064 -->|implements| f_plugin_scripts_reqmap_engine_retire_py_15_243
  ARCH_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>ARCH-REVIEW-022</small>"]
  f_plugin_scripts_test_reqmap_author_py_1321["plugin/scripts/test_reqmap_author.py:1321"]
  ARCH_REVIEW_022 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1321
  f_plugin_scripts_reqmap_engine_review_py_10["plugin/scripts/reqmap_engine/review.py:10"]
  ARCH_REVIEW_022 -->|implements| f_plugin_scripts_reqmap_engine_review_py_10
  f_plugin_skills_requirement_quality_review_SKILL_md_6["plugin/skills/requirement-quality-review/SKILL.md:6"]
  ARCH_REVIEW_022 -->|implements| f_plugin_skills_requirement_quality_review_SKILL_md_6
  f_plugin_skills_requirement_quality_review_SKILL_universal_md_9["plugin/skills/requirement-quality-review/SKILL.universal.md:9"]
  ARCH_REVIEW_022 -->|implements| f_plugin_skills_requirement_quality_review_SKILL_universal_md_9
  ARCH_ROADMAP_038["Roadmap coherence signals<br><small>ARCH-ROADMAP-038</small>"]
  f_plugin_scripts_test_reqmap_report_py_2148_4094["plugin/scripts/test_reqmap_report.py:2148-4094"]
  ARCH_ROADMAP_038 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2148_4094
  f_plugin_scripts_reqmap_engine_health_py_244["plugin/scripts/reqmap_engine/health.py:244"]
  ARCH_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_engine_health_py_244
  f_plugin_scripts_reqmap_engine_mapdata_py_116_164["plugin/scripts/reqmap_engine/mapdata.py:116-164"]
  ARCH_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_116_164
  ARCH_RULES_059["The gate rule registry<br><small>ARCH-RULES-059</small>"]
  f_plugin_scripts_test_reqmap_gate_py_2324_2774["plugin/scripts/test_reqmap_gate.py:2324-2774"]
  ARCH_RULES_059 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2324_2774
  f_plugin_scripts_reqmap_engine_gate_py_22_178["plugin/scripts/reqmap_engine/gate.py:22-178"]
  ARCH_RULES_059 -->|implements| f_plugin_scripts_reqmap_engine_gate_py_22_178
  f_plugin_scripts_reqmap_engine_model_py_111_141["plugin/scripts/reqmap_engine/model.py:111-141"]
  ARCH_RULES_059 -->|implements| f_plugin_scripts_reqmap_engine_model_py_111_141
  f_plugin_scripts_reqmap_engine_workspace_py_83_138["plugin/scripts/reqmap_engine/workspace.py:83-138"]
  ARCH_RULES_059 -->|implements| f_plugin_scripts_reqmap_engine_workspace_py_83_138
  ARCH_SCAN_002["Member discovery<br><small>ARCH-SCAN-002</small>"]
  f_plugin_scripts_test_reqmap_scan_py_112_1420["plugin/scripts/test_reqmap_scan.py:112-1420"]
  ARCH_SCAN_002 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_112_1420
  f_plugin_scripts_reqmap_engine_scan_py_16_222["plugin/scripts/reqmap_engine/scan.py:16-222"]
  ARCH_SCAN_002 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_16_222
  f_plugin_scripts_reqmap_engine_tags_py_74_228["plugin/scripts/reqmap_engine/tags.py:74-228"]
  ARCH_SCAN_002 -->|implements| f_plugin_scripts_reqmap_engine_tags_py_74_228
  ARCH_SCANCACHE_023["Opt-in scan cache<br><small>ARCH-SCANCACHE-023</small>"]
  f_plugin_scripts_test_reqmap_scan_py_585["plugin/scripts/test_reqmap_scan.py:585"]
  ARCH_SCANCACHE_023 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_585
  f_plugin_scripts_reqmap_engine_scan_py_73_153["plugin/scripts/reqmap_engine/scan.py:73-153"]
  ARCH_SCANCACHE_023 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_73_153
  ARCH_SEARCH_036["Free-text requirement search<br><small>ARCH-SEARCH-036</small>"]
  f_app_scripts_ssr_smoke_jsx_2["app/scripts/ssr-smoke.jsx:2"]
  ARCH_SEARCH_036 -->|tested-by| f_app_scripts_ssr_smoke_jsx_2
  f_app_src_lib_search_js_1["app/src/lib/search.js:1"]
  ARCH_SEARCH_036 -->|implements| f_app_src_lib_search_js_1
  f_plugin_scripts_test_reqmap_report_py_1155_4561["plugin/scripts/test_reqmap_report.py:1155-4561"]
  ARCH_SEARCH_036 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1155_4561
  f_plugin_scripts_reqmap_engine_similar_py_295_344["plugin/scripts/reqmap_engine/similar.py:295-344"]
  ARCH_SEARCH_036 -->|implements| f_plugin_scripts_reqmap_engine_similar_py_295_344
  ARCH_SECTIONS_068["Reading a requirement's sections<br><small>ARCH-SECTIONS-068</small>"]
  f_plugin_scripts_test_reqmap_scan_py_1547["plugin/scripts/test_reqmap_scan.py:1547"]
  ARCH_SECTIONS_068 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_1547
  f_plugin_scripts_reqmap_engine_sections_py_43_69["plugin/scripts/reqmap_engine/sections.py:43-69"]
  ARCH_SECTIONS_068 -->|implements| f_plugin_scripts_reqmap_engine_sections_py_43_69
  ARCH_SELFGATE_039["This repo's own gate wiring<br><small>ARCH-SELFGATE-039</small>"]
  f_sync_reqmap_sh_2["sync_reqmap.sh:2"]
  ARCH_SELFGATE_039 -->|implements| f_sync_reqmap_sh_2
  f__githooks_pre_commit_2[".githooks/pre-commit:2"]
  ARCH_SELFGATE_039 -->|implements| f__githooks_pre_commit_2
  f__githooks_pre_push_2[".githooks/pre-push:2"]
  ARCH_SELFGATE_039 -->|implements| f__githooks_pre_push_2
  f__github_workflows_ci_yml_2[".github/workflows/ci.yml:2"]
  ARCH_SELFGATE_039 -->|implements| f__github_workflows_ci_yml_2
  f_check_action_yml_2["check/action.yml:2"]
  ARCH_SELFGATE_039 -->|implements| f_check_action_yml_2
  f_plugin_scripts_test_reqmap_report_py_4343["plugin/scripts/test_reqmap_report.py:4343"]
  ARCH_SELFGATE_039 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4343
  f_scripts_changelog_notes_py_2["scripts/changelog_notes.py:2"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_changelog_notes_py_2
  f_scripts_check_engine_bump_py_2["scripts/check_engine_bump.py:2"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_check_engine_bump_py_2
  f_scripts_check_retired_verbs_py_2["scripts/check_retired_verbs.py:2"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_check_retired_verbs_py_2
  f_scripts_check_versions_py_2["scripts/check_versions.py:2"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_check_versions_py_2
  f_scripts_test_changelog_notes_py_2["scripts/test_changelog_notes.py:2"]
  ARCH_SELFGATE_039 -->|tested-by| f_scripts_test_changelog_notes_py_2
  f_scripts_test_check_engine_bump_py_56["scripts/test_check_engine_bump.py:56"]
  ARCH_SELFGATE_039 -->|tested-by| f_scripts_test_check_engine_bump_py_56
  f_scripts_test_check_versions_py_94_101["scripts/test_check_versions.py:94-101"]
  ARCH_SELFGATE_039 -->|tested-by| f_scripts_test_check_versions_py_94_101
  ARCH_SHOW_015["Single-requirement dossier<br><small>ARCH-SHOW-015</small>"]
  f_plugin_scripts_test_reqmap_report_py_992_3572["plugin/scripts/test_reqmap_report.py:992-3572"]
  ARCH_SHOW_015 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_992_3572
  f_plugin_scripts_reqmap_engine_show_py_10["plugin/scripts/reqmap_engine/show.py:10"]
  ARCH_SHOW_015 -->|implements| f_plugin_scripts_reqmap_engine_show_py_10
  ARCH_SIMILAR_016["Duplicate-capability detector<br><small>ARCH-SIMILAR-016</small>"]
  f_plugin_scripts_test_reqmap_report_py_1074_3976["plugin/scripts/test_reqmap_report.py:1074-3976"]
  ARCH_SIMILAR_016 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1074_3976
  f_plugin_scripts_reqmap_engine_similar_py_18_219["plugin/scripts/reqmap_engine/similar.py:18-219"]
  ARCH_SIMILAR_016 -->|implements| f_plugin_scripts_reqmap_engine_similar_py_18_219
  ARCH_SITE_026["Generate & maintain a project presentation page<br><small>ARCH-SITE-026</small>"]
  f_plugin_scripts_test_reqmap_report_py_1625["plugin/scripts/test_reqmap_report.py:1625"]
  ARCH_SITE_026 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1625
  f_plugin_scripts_reqmap_engine_git_py_72_92["plugin/scripts/reqmap_engine/git.py:72-92"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_git_py_72_92
  f_plugin_scripts_reqmap_engine_init_py_160["plugin/scripts/reqmap_engine/init.py:160"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_init_py_160
  f_plugin_scripts_reqmap_engine_mapcmd_py_126_167["plugin/scripts/reqmap_engine/mapcmd.py:126-167"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_mapcmd_py_126_167
  f_plugin_scripts_reqmap_engine_site_py_9_447["plugin/scripts/reqmap_engine/site.py:9-447"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_site_py_9_447
  ARCH_STALEENGINE_043["Stale vendored engine, reported in CI<br><small>ARCH-STALEENGINE-043</small>"]
  f_check_action_yml_3["check/action.yml:3"]
  ARCH_STALEENGINE_043 -->|implements| f_check_action_yml_3
  f_check_engine_staleness_py_2["check/engine_staleness.py:2"]
  ARCH_STALEENGINE_043 -->|implements| f_check_engine_staleness_py_2
  f_scripts_test_engine_staleness_py_49_154["scripts/test_engine_staleness.py:49-154"]
  ARCH_STALEENGINE_043 -->|tested-by| f_scripts_test_engine_staleness_py_49_154
  ARCH_SUGGESTVERIFIES_047["Suggest per-criterion 'verifies:' tags<br><small>ARCH-SUGGESTVERIFIES-047</small>"]
  f_plugin_scripts_test_reqmap_gate_py_979_2530["plugin/scripts/test_reqmap_gate.py:979-2530"]
  ARCH_SUGGESTVERIFIES_047 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_979_2530
  f_plugin_scripts_test_reqmap_report_py_4640["plugin/scripts/test_reqmap_report.py:4640"]
  ARCH_SUGGESTVERIFIES_047 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4640
  f_plugin_scripts_reqmap_engine_verifies_py_20_171["plugin/scripts/reqmap_engine/verifies.py:20-171"]
  ARCH_SUGGESTVERIFIES_047 -->|implements| f_plugin_scripts_reqmap_engine_verifies_py_20_171
  ARCH_TESTLINK_018["Test-link integrity check<br><small>ARCH-TESTLINK-018</small>"]
  f_plugin_scripts_test_reqmap_gate_py_625_2578["plugin/scripts/test_reqmap_gate.py:625-2578"]
  ARCH_TESTLINK_018 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_625_2578
  f_plugin_scripts_reqmap_engine_rules_py_166["plugin/scripts/reqmap_engine/rules.py:166"]
  ARCH_TESTLINK_018 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_166
  f_plugin_scripts_reqmap_engine_workspace_py_52_74["plugin/scripts/reqmap_engine/workspace.py:52-74"]
  ARCH_TESTLINK_018 -->|implements| f_plugin_scripts_reqmap_engine_workspace_py_52_74
  ARCH_TRACE_020["Upstream traceability<br><small>ARCH-TRACE-020</small>"]
  f_plugin_scripts_test_reqmap_gate_py_825_1229["plugin/scripts/test_reqmap_gate.py:825-1229"]
  ARCH_TRACE_020 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_825_1229
  f_plugin_scripts_reqmap_engine_axis_py_13_55["plugin/scripts/reqmap_engine/axis.py:13-55"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_axis_py_13_55
  f_plugin_scripts_reqmap_engine_mapdata_py_50_109["plugin/scripts/reqmap_engine/mapdata.py:50-109"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_50_109
  f_plugin_scripts_reqmap_engine_model_py_178["plugin/scripts/reqmap_engine/model.py:178"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_model_py_178
  f_plugin_scripts_reqmap_engine_rules_py_55_211["plugin/scripts/reqmap_engine/rules.py:55-211"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_55_211
  f_plugin_scripts_reqmap_engine_show_py_48["plugin/scripts/reqmap_engine/show.py:48"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_show_py_48
  ARCH_TRACKED_042["Untracked members reported<br><small>ARCH-TRACKED-042</small>"]
  f_plugin_scripts_test_reqmap_scan_py_803["plugin/scripts/test_reqmap_scan.py:803"]
  ARCH_TRACKED_042 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_803
  f_plugin_scripts_reqmap_engine_orphans_py_13["plugin/scripts/reqmap_engine/orphans.py:13"]
  ARCH_TRACKED_042 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_13
  f_plugin_scripts_reqmap_engine_rules_py_355["plugin/scripts/reqmap_engine/rules.py:355"]
  ARCH_TRACKED_042 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_355
  ARCH_TRANSLATE_044["Reading a cached requirement translation into the map<br><small>ARCH-TRANSLATE-044</small>"]
  f_app_src_lib_i18n_jsx_2["app/src/lib/i18n.jsx:2"]
  ARCH_TRANSLATE_044 -->|implements| f_app_src_lib_i18n_jsx_2
  f_app_src_views_SpecView_jsx_2["app/src/views/SpecView.jsx:2"]
  ARCH_TRANSLATE_044 -->|implements| f_app_src_views_SpecView_jsx_2
  f_plugin_scripts_test_reqmap_author_py_969_3216["plugin/scripts/test_reqmap_author.py:969-3216"]
  ARCH_TRANSLATE_044 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_969_3216
  f_plugin_scripts_reqmap_engine_i18n_py_11_158["plugin/scripts/reqmap_engine/i18n.py:11-158"]
  ARCH_TRANSLATE_044 -->|implements| f_plugin_scripts_reqmap_engine_i18n_py_11_158
  f_plugin_scripts_reqmap_engine_rules_py_253["plugin/scripts/reqmap_engine/rules.py:253"]
  ARCH_TRANSLATE_044 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_253
  ARCH_UNSCANNEDTAG_045["Tags in unscanned file types reported<br><small>ARCH-UNSCANNEDTAG-045</small>"]
  f_plugin_scripts_test_reqmap_scan_py_945["plugin/scripts/test_reqmap_scan.py:945"]
  ARCH_UNSCANNEDTAG_045 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_945
  f_plugin_scripts_reqmap_engine_orphans_py_52["plugin/scripts/reqmap_engine/orphans.py:52"]
  ARCH_UNSCANNEDTAG_045 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_52
  f_plugin_scripts_reqmap_engine_rules_py_367["plugin/scripts/reqmap_engine/rules.py:367"]
  ARCH_UNSCANNEDTAG_045 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_367
  ARCH_VIEWER_007["Self-contained HTML map viewer<br><small>ARCH-VIEWER-007</small>"]
  f_app_vite_viewer_config_js_1["app/vite.viewer.config.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_vite_viewer_config_js_1
  f_app_scripts_run_ssr_smoke_mjs_1["app/scripts/run-ssr-smoke.mjs:1"]
  ARCH_VIEWER_007 -->|implements| f_app_scripts_run_ssr_smoke_mjs_1
  f_app_scripts_ssr_smoke_jsx_1["app/scripts/ssr-smoke.jsx:1"]
  ARCH_VIEWER_007 -->|tested-by| f_app_scripts_ssr_smoke_jsx_1
  f_app_scripts_sync_data_mjs_1["app/scripts/sync-data.mjs:1"]
  ARCH_VIEWER_007 -->|implements| f_app_scripts_sync_data_mjs_1
  f_app_src_App_jsx_1["app/src/App.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_App_jsx_1
  f_app_src_main_jsx_1["app/src/main.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_main_jsx_1
  f_app_src_lib_data_js_1["app/src/lib/data.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_data_js_1
  f_app_src_lib_i18n_jsx_1["app/src/lib/i18n.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_i18n_jsx_1
  f_app_src_lib_icons_jsx_1["app/src/lib/icons.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_icons_jsx_1
  f_app_src_lib_layout_js_1["app/src/lib/layout.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_layout_js_1
  f_app_src_lib_loadData_js_1["app/src/lib/loadData.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_loadData_js_1
  f_app_src_lib_tree_js_1["app/src/lib/tree.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_tree_js_1
  f_app_src_lib_ui_jsx_1["app/src/lib/ui.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_ui_jsx_1
  f_app_src_lib_useDragPan_js_1["app/src/lib/useDragPan.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_useDragPan_js_1
  f_app_src_styles_app_css_1["app/src/styles/app.css:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_styles_app_css_1
  f_app_src_styles_colors_and_type_css_1["app/src/styles/colors_and_type.css:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_styles_colors_and_type_css_1
  f_app_src_views_CommandsView_jsx_1["app/src/views/CommandsView.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_CommandsView_jsx_1
  f_app_src_views_ExplorerView_jsx_1["app/src/views/ExplorerView.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_ExplorerView_jsx_1
  f_app_src_views_MapView_jsx_1["app/src/views/MapView.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_MapView_jsx_1
  f_app_src_views_ProblemsView_jsx_1["app/src/views/ProblemsView.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_ProblemsView_jsx_1
  f_app_src_views_RoadmapView_jsx_1["app/src/views/RoadmapView.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_RoadmapView_jsx_1
  f_app_src_views_SpecView_jsx_1["app/src/views/SpecView.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_SpecView_jsx_1
  f_plugin_scripts_test_reqmap_report_py_351_3917["plugin/scripts/test_reqmap_report.py:351-3917"]
  ARCH_VIEWER_007 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_351_3917
  f_plugin_scripts_reqmap_engine_rules_py_236["plugin/scripts/reqmap_engine/rules.py:236"]
  ARCH_VIEWER_007 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_236
  f_plugin_scripts_reqmap_engine_viewer_py_71_134["plugin/scripts/reqmap_engine/viewer.py:71-134"]
  ARCH_VIEWER_007 -->|implements| f_plugin_scripts_reqmap_engine_viewer_py_71_134
  ARCH_VLEVEL_037["Verification levels<br><small>ARCH-VLEVEL-037</small>"]
  f_plugin_scripts_test_reqmap_gate_py_171_227["plugin/scripts/test_reqmap_gate.py:171-227"]
  ARCH_VLEVEL_037 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_171_227
  f_plugin_scripts_test_reqmap_report_py_1055_1064["plugin/scripts/test_reqmap_report.py:1055-1064"]
  ARCH_VLEVEL_037 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1055_1064
  f_plugin_scripts_test_reqmap_scan_py_250_312["plugin/scripts/test_reqmap_scan.py:250-312"]
  ARCH_VLEVEL_037 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_250_312
  f_plugin_scripts_reqmap_engine_rules_py_122_135["plugin/scripts/reqmap_engine/rules.py:122-135"]
  ARCH_VLEVEL_037 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_122_135
  f_plugin_scripts_reqmap_engine_scan_py_254["plugin/scripts/reqmap_engine/scan.py:254"]
  ARCH_VLEVEL_037 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_254
  f_plugin_scripts_reqmap_engine_show_py_10["plugin/scripts/reqmap_engine/show.py:10"]
  ARCH_VLEVEL_037 -->|implements| f_plugin_scripts_reqmap_engine_show_py_10
  f_scripts_test_cross_tool_py_84["scripts/test_cross_tool.py:84"]
  ARCH_VLEVEL_037 -->|tested-by| f_scripts_test_cross_tool_py_84
  SYS_AUTHOR_101["Authoring and evolving a requirement<br><small>SYS-AUTHOR-101</small>"]
  style SYS_AUTHOR_101 fill:#fee,stroke:#c66
  SYS_GATE_102["Keeping code and specification in step<br><small>SYS-GATE-102</small>"]
  style SYS_GATE_102 fill:#fee,stroke:#c66
  SYS_QUALITY_104["Keeping requirements readable<br><small>SYS-QUALITY-104</small>"]
  style SYS_QUALITY_104 fill:#fee,stroke:#c66
  SYS_READ_103["Reading a repository<br><small>SYS-READ-103</small>"]
  style SYS_READ_103 fill:#fee,stroke:#c66
  SYS_REPORT_105["Answering what is here and what to do next<br><small>SYS-REPORT-105</small>"]
  style SYS_REPORT_105 fill:#fee,stroke:#c66
  SYS_SHIP_108["Adopting and shipping the engine<br><small>SYS-SHIP-108</small>"]
  style SYS_SHIP_108 fill:#fee,stroke:#c66
  SYS_SSOT_001["Stakeholder need — specs and code stay in sync<br><small>SYS-SSOT-001</small>"]
  style SYS_SSOT_001 fill:#fee,stroke:#c66
  SYS_VISUAL_106["Seeing the system at a glance<br><small>SYS-VISUAL-106</small>"]
  style SYS_VISUAL_106 fill:#fee,stroke:#c66
  SYS_VMODEL_107["Placing a requirement in the V<br><small>SYS-VMODEL-107</small>"]
  style SYS_VMODEL_107 fill:#fee,stroke:#c66
```

## Dependency Map

_Area-level coupling: one box per area (N caps), arrow A->B = some capability in A depends on one in B. The System Map has the per-capability detail._

```mermaid
graph LR
  a_ARCH["ARCH<br><small>61 caps</small>"]
  a_REQ["REQ<br><small>178 caps</small>"]
  a_SYS["SYS<br><small>9 caps</small>"]
  a_ARCH --> a_REQ
  a_REQ --> a_ARCH
  style a_ARCH stroke-width:3px
  style a_REQ stroke-width:3px
```

## Risk & Unknowns

_Requirements needing attention: red = unimplemented (confirmed, no code); orange = unreviewed (promote after review); yellow = untested (implemented but no tested-by — set `test_exempt` to silence), or unverified-intent (open verify-intent question)._

```mermaid
graph LR
  ok["No risk signals detected"]
```
