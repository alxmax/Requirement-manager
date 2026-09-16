---
generated: 2026-09-16
engine: 2026-09-16.9
nodes: 281
edges: 120
design pass-rate: 96% (102/106 source files without a design candidate)
---

# Requirement Map

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
    ARCH_DOCCLAIMS_071["Corpus counts a document states about itself<br><small>ARCH-DOCCLAIMS-071</small>"]
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
    ARCH_PLANDRIFT_069["Plan items whose code has moved on without them<br><small>ARCH-PLANDRIFT-069</small>"]
    ARCH_PROMOTE_011["Confirmation is a human's answer, and an edit takes it back<br><small>ARCH-PROMOTE-011</small>"]
    ARCH_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>ARCH-PROMOTE-TODO-001</small>"]
    ARCH_PROSE_024["Prose capability classification & drafting<br><small>ARCH-PROSE-024</small>"]
    ARCH_PYFLOOR_040["Declared Python support floor<br><small>ARCH-PYFLOOR-040</small>"]
    ARCH_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>ARCH-REGISTRYLAG-035</small>"]
    ARCH_RELEASE_072["Releasing from the plan<br><small>ARCH-RELEASE-072</small>"]
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
    ARCH_UNREADABLE_070["Source files the scan cannot decode<br><small>ARCH-UNREADABLE-070</small>"]
    ARCH_UNSCANNEDTAG_045["Tags in unscanned file types reported<br><small>ARCH-UNSCANNEDTAG-045</small>"]
    ARCH_VIEWER_007["Self-contained HTML map viewer<br><small>ARCH-VIEWER-007</small>"]
    ARCH_VLEVEL_037["Verification levels<br><small>ARCH-VLEVEL-037</small>"]
  end
  subgraph sg_REQ["REQ"]
    REQ_ACVERIFY_821["Mapping verifies tags to labelled criteria<br><small>REQ-ACVERIFY-821</small>"]
    REQ_ACVERIFY_822["When per-criterion coverage stays silent<br><small>REQ-ACVERIFY-822</small>"]
    REQ_ACVERIFY_823["Emitting clauses, covered and gap on the map<br><small>REQ-ACVERIFY-823</small>"]
    REQ_DANGLINGVERIFY_1009["A verifies tag that points at nothing<br><small>REQ-DANGLINGVERIFY-1009</small>"]
    REQ_ATOMICITY_824["One obligation per clause, with an advisory length backstop<br><small>REQ-ATOMICITY-824</small>"]
    REQ_ATOMICITY_825["statement-size measures length, not atomicity<br><small>REQ-ATOMICITY-825</small>"]
    REQ_AUDIT_970["Every discovery pass, one report, one exit code<br><small>REQ-AUDIT-970</small>"]
    REQ_AUDIT_971["An exemption nobody justified is itself a finding<br><small>REQ-AUDIT-971</small>"]
    REQ_AUDIT_972["Whether the corpus has a shape at all<br><small>REQ-AUDIT-972</small>"]
    REQ_AUDIT_973["Sync says what it found<br><small>REQ-AUDIT-973</small>"]
    REQ_RELEVEL_997["The tail names a move that was only half made<br><small>REQ-RELEVEL-997</small>"]
    REQ_CANDIDATES_826["The plan's JSON shape and read-only scanning<br><small>REQ-CANDIDATES-826</small>"]
    REQ_CANDIDATES_827["Fields a candidate carries<br><small>REQ-CANDIDATES-827</small>"]
    REQ_PLANTAGGED_1005["One definition of 'this file is already accounted for'<br><small>REQ-PLANTAGGED-1005</small>"]
    REQ_PLANLEVEL_1006["The plan carries the pyramid it would write<br><small>REQ-PLANLEVEL-1006</small>"]
    REQ_PLANDRAFTID_1010["The plan states the id the writer will mint<br><small>REQ-PLANDRAFTID-1010</small>"]
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
    REQ_UNTAGGEDSET_1007["Two untagged reports, one list<br><small>REQ-UNTAGGEDSET-1007</small>"]
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
    REQ_DOCCLAIMS_1012["Re-measuring a marked claim<br><small>REQ-DOCCLAIMS-1012</small>"]
    REQ_DRIFT_841["Hashing only the normative sections<br><small>REQ-DRIFT-841</small>"]
    REQ_DRIFT_842["Reading and writing the drift baseline<br><small>REQ-DRIFT-842</small>"]
    REQ_DRIFT_988["The waiver leaves a trace<br><small>REQ-DRIFT-988</small>"]
    REQ_DRIFTIMPACT_843["Name a drifted requirement's direct dependents<br><small>REQ-DRIFTIMPACT-843</small>"]
    REQ_EXTRACT_849["Which files draft walks<br><small>REQ-EXTRACT-849</small>"]
    REQ_EXTRACT_850["Writing one draft proposal per file<br><small>REQ-EXTRACT-850</small>"]
    REQ_EXTRACT_851["Scoring risk and capturing an authoring hint<br><small>REQ-EXTRACT-851</small>"]
    REQ_EXTRACT_981["The three rungs extraction drafts<br><small>REQ-EXTRACT-981</small>"]
    REQ_INITTAG_1008["The draft and its source are linked in the same run<br><small>REQ-INITTAG-1008</small>"]
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
    REQ_PLANCADENCE_1000["A release cadence, computed once and only drawn by the chart<br><small>REQ-PLANCADENCE-1000</small>"]
    REQ_HISTORY_1003["What already shipped, read from the CHANGELOG and grouped by month<br><small>REQ-HISTORY-1003</small>"]
    REQ_MAPDIAGRAMS_874["_map.md: four legended, always-regenerated Mermaid blocks<br><small>REQ-MAPDIAGRAMS-874</small>"]
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
    REQ_PLANDRIFT_1002["Reading an item's citations, and the six ways that goes wrong<br><small>REQ-PLANDRIFT-1002</small>"]
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
    REQ_VERSIONFILES_1014["The version a repository declares is read where it lives<br><small>REQ-VERSIONFILES-1014</small>"]
    REQ_CHANGELOGFORMS_1015["A CHANGELOG is read in the form its ecosystem writes<br><small>REQ-CHANGELOGFORMS-1015</small>"]
    REQ_VERSIONALIGN_1016["Where the version sources disagree is reported<br><small>REQ-VERSIONALIGN-1016</small>"]
    REQ_NEXTVERSION_1017["The next release's number comes from the plan<br><small>REQ-NEXTVERSION-1017</small>"]
    REQ_RELEASECMD_1018["'sync --release' cuts the next planned version<br><small>REQ-RELEASECMD-1018</small>"]
    REQ_RELEASEWORKFLOW_1019["A GitHub repository gets the workflow that tags a release once<br><small>REQ-RELEASEWORKFLOW-1019</small>"]
    REQ_PLANADVANCE_1020["Releasing a version advances the plan<br><small>REQ-PLANADVANCE-1020</small>"]
    REQ_PLANDATES_1022["'sync' suggests a bar's date when the work moved<br><small>REQ-PLANDATES-1022</small>"]
    REQ_RELEASEROADMAP_1023["A release names the ROADMAP items it carries out<br><small>REQ-RELEASEROADMAP-1023</small>"]
    REQ_REPRO_905["Rebuilding and diffing each committed artifact in CI<br><small>REQ-REPRO-905</small>"]
    REQ_RETIRE_960["The blast radius of a retirement<br><small>REQ-RETIRE-960</small>"]
    REQ_RETIRE_961["Deprecating, refusing, and never writing by accident<br><small>REQ-RETIRE-961</small>"]
    REQ_RETIRE_962["Deleting a requirement without deleting meaning<br><small>REQ-RETIRE-962</small>"]
    REQ_RETIRE_963["Retiring a class in one operation<br><small>REQ-RETIRE-963</small>"]
    REQ_REVIEW_906["A deterministic plan for an out-of-band AI review<br><small>REQ-REVIEW-906</small>"]
    REQ_ROADMAP_907["A behind roadmap and an unversioned heading, both read-only<br><small>REQ-ROADMAP-907</small>"]
    REQ_ROADMAP_983["The roadmap can also be ahead of the requirements<br><small>REQ-ROADMAP-983</small>"]
    REQ_ROADMAP_998["ROADMAP.md: the horizon plan, and the two claims in it that can be checked<br><small>REQ-ROADMAP-998</small>"]
    REQ_PLANHORIZON_1010["A repo with no plan still gets a calendar to plan on<br><small>REQ-PLANHORIZON-1010</small>"]
    REQ_PLANBRANCH_1011["The shipped band is named by the branch it shipped on<br><small>REQ-PLANBRANCH-1011</small>"]
    REQ_PLANSTALE_1013["A plan that schedules a version already declared is reported<br><small>REQ-PLANSTALE-1013</small>"]
    REQ_UNPLANNED_1024["A Now or Next item with no bar is counted<br><small>REQ-UNPLANNED-1024</small>"]
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
    REQ_SELFGATE_1011["A live instruction never names a CLI name the engine dropped<br><small>REQ-SELFGATE-1011</small>"]
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
    REQ_UNREADABLE_1004["Decoding a source file, or refusing it out loud<br><small>REQ-UNREADABLE-1004</small>"]
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
    REQ_VIEWER_999["A plan bar opens the note its author wrote in ROADMAP.md<br><small>REQ-VIEWER-999</small>"]
    REQ_PLANSTACK_1012["Bars are stacked by what is drawn, not by what is scheduled<br><small>REQ-PLANSTACK-1012</small>"]
    REQ_PLANDAYS_1021["Each day on the Plan is labelled<br><small>REQ-PLANDAYS-1021</small>"]
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
  ARCH_LEVELRETROFIT_066 --> ARCH_LEVEL_051
  ARCH_LINTCHECKS_025 --> ARCH_LINT_014
  ARCH_PIPE_046 --> ARCH_CMDREGISTRY_033
  ARCH_PLANDRIFT_069 --> ARCH_ROADMAP_038
  ARCH_PROMOTE_TODO_001 --> ARCH_NEW_004
  ARCH_PROSE_024 --> ARCH_EXTRACT_008
  ARCH_REGISTRYLAG_035 --> ARCH_HEALTH_017
  ARCH_RELEASE_072 --> ARCH_ROADMAP_038
  ARCH_RELEASE_072 --> ARCH_INIT_012
  ARCH_REPRO_041 --> ARCH_SELFGATE_039
  ARCH_ROADMAP_038 --> ARCH_HEALTH_017
  ARCH_SEARCH_036 --> ARCH_SIMILAR_016
  REQ_REDUNDANCY_058 --> ARCH_NEXT_013
  ARCH_SITE_026 --> ARCH_VIEWER_007
  ARCH_STALEENGINE_043 --> ARCH_SELFGATE_039
  ARCH_SUGGESTVERIFIES_047 --> ARCH_ACVERIFY_019
  ARCH_TRANSLATE_044 --> ARCH_VIEWER_007
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
  f_plugin_scripts_test_reqmap_scan_py_545_891["plugin/scripts/test_reqmap_scan.py:545-891"]
  ARCH_ACVERIFY_019 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_545_891
  f_plugin_scripts_reqmap_engine_acceptance_py_17_90["plugin/scripts/reqmap_engine/acceptance.py:17-90"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_acceptance_py_17_90
  f_plugin_scripts_reqmap_engine_mapdata_py_18["plugin/scripts/reqmap_engine/mapdata.py:18"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_18
  f_plugin_scripts_reqmap_engine_rules_py_183_200["plugin/scripts/reqmap_engine/rules.py:183-200"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_183_200
  f_plugin_scripts_reqmap_engine_scan_py_188_291["plugin/scripts/reqmap_engine/scan.py:188-291"]
  ARCH_ACVERIFY_019 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_188_291
  ARCH_ATOMICITY_049["Statement atomicity<br><small>ARCH-ATOMICITY-049</small>"]
  f_plugin_scripts_test_reqmap_author_py_1574_2038["plugin/scripts/test_reqmap_author.py:1574-2038"]
  ARCH_ATOMICITY_049 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1574_2038
  f_plugin_scripts_reqmap_engine_lintrules_py_118_128["plugin/scripts/reqmap_engine/lintrules.py:118-128"]
  ARCH_ATOMICITY_049 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_118_128
  ARCH_AUDIT_065["One report of everything the engine can discover<br><small>ARCH-AUDIT-065</small>"]
  f_plugin_scripts_test_reqmap_report_py_3215_5293["plugin/scripts/test_reqmap_report.py:3215-5293"]
  ARCH_AUDIT_065 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_3215_5293
  f_plugin_scripts_reqmap_engine_audit_py_30_423["plugin/scripts/reqmap_engine/audit.py:30-423"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_audit_py_30_423
  f_plugin_scripts_reqmap_engine_relevel_py_19_212["plugin/scripts/reqmap_engine/relevel.py:19-212"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_relevel_py_19_212
  f_plugin_scripts_reqmap_engine_rules_py_320["plugin/scripts/reqmap_engine/rules.py:320"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_320
  f_plugin_scripts_reqmap_engine_similar_py_35_63["plugin/scripts/reqmap_engine/similar.py:35-63"]
  ARCH_AUDIT_065 -->|implements| f_plugin_scripts_reqmap_engine_similar_py_35_63
  ARCH_CANDIDATES_009["Capability candidates (extraction plan)<br><small>ARCH-CANDIDATES-009</small>"]
  f_plugin_scripts_test_reqmap_author_py_166_2238["plugin/scripts/test_reqmap_author.py:166-2238"]
  ARCH_CANDIDATES_009 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_166_2238
  f_plugin_scripts_test_reqmap_scan_py_467_508["plugin/scripts/test_reqmap_scan.py:467-508"]
  ARCH_CANDIDATES_009 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_467_508
  f_plugin_scripts_reqmap_engine_candidates_py_22_306["plugin/scripts/reqmap_engine/candidates.py:22-306"]
  ARCH_CANDIDATES_009 -->|implements| f_plugin_scripts_reqmap_engine_candidates_py_22_306
  f_plugin_scripts_reqmap_engine_tags_py_292_301["plugin/scripts/reqmap_engine/tags.py:292-301"]
  ARCH_CANDIDATES_009 -->|implements| f_plugin_scripts_reqmap_engine_tags_py_292_301
  ARCH_CHECK_006["The gate<br><small>ARCH-CHECK-006</small>"]
  f_plugin_hooks_pre_commit_2["plugin/hooks/pre-commit:2"]
  ARCH_CHECK_006 -->|implements| f_plugin_hooks_pre_commit_2
  f_plugin_scripts_test_reqmap_gate_py_42_2850["plugin/scripts/test_reqmap_gate.py:42-2850"]
  ARCH_CHECK_006 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_42_2850
  f_plugin_scripts_test_reqmap_report_py_647["plugin/scripts/test_reqmap_report.py:647"]
  ARCH_CHECK_006 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_647
  f_plugin_scripts_reqmap_engine___init___py_12["plugin/scripts/reqmap_engine/__init__.py:12"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine___init___py_12
  f_plugin_scripts_reqmap_engine_gate_py_57_179["plugin/scripts/reqmap_engine/gate.py:57-179"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_gate_py_57_179
  f_plugin_scripts_reqmap_engine_locks_py_174_343["plugin/scripts/reqmap_engine/locks.py:174-343"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_locks_py_174_343
  f_plugin_scripts_reqmap_engine_mapjson_py_9["plugin/scripts/reqmap_engine/mapjson.py:9"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_mapjson_py_9
  f_plugin_scripts_reqmap_engine_model_py_189["plugin/scripts/reqmap_engine/model.py:189"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_model_py_189
  f_plugin_scripts_reqmap_engine_rules_py_443["plugin/scripts/reqmap_engine/rules.py:443"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_443
  f_plugin_scripts_reqmap_engine_sections_py_96_231["plugin/scripts/reqmap_engine/sections.py:96-231"]
  ARCH_CHECK_006 -->|implements| f_plugin_scripts_reqmap_engine_sections_py_96_231
  ARCH_CLARIFY_062["Questions a requirement has not answered<br><small>ARCH-CLARIFY-062</small>"]
  f_plugin_scripts_test_reqmap_author_py_2328_2927["plugin/scripts/test_reqmap_author.py:2328-2927"]
  ARCH_CLARIFY_062 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_2328_2927
  f_plugin_scripts_reqmap_engine_clarify_py_109_244["plugin/scripts/reqmap_engine/clarify.py:109-244"]
  ARCH_CLARIFY_062 -->|implements| f_plugin_scripts_reqmap_engine_clarify_py_109_244
  ARCH_CMDREGISTRY_033["CLI command registry + generated integration artifacts<br><small>ARCH-CMDREGISTRY-033</small>"]
  f_plugin_scripts_reqmap_py_114["plugin/scripts/reqmap.py:114"]
  ARCH_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_py_114
  f_plugin_scripts_test_reqmap_report_py_1972_5081["plugin/scripts/test_reqmap_report.py:1972-5081"]
  ARCH_CMDREGISTRY_033 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1972_5081
  f_plugin_scripts_reqmap_engine_cliflags_py_15_76["plugin/scripts/reqmap_engine/cliflags.py:15-76"]
  ARCH_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_engine_cliflags_py_15_76
  f_plugin_scripts_reqmap_engine_commands_py_14["plugin/scripts/reqmap_engine/commands.py:14"]
  ARCH_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_engine_commands_py_14
  f_plugin_scripts_reqmap_engine_registry_py_12_42["plugin/scripts/reqmap_engine/registry.py:12-42"]
  ARCH_CMDREGISTRY_033 -->|implements| f_plugin_scripts_reqmap_engine_registry_py_12_42
  ARCH_CONFIG_060["Per-repo configuration file<br><small>ARCH-CONFIG-060</small>"]
  f_plugin_scripts_reqmap_py_289["plugin/scripts/reqmap.py:289"]
  ARCH_CONFIG_060 -->|implements| f_plugin_scripts_reqmap_py_289
  f_plugin_scripts_test_reqmap_report_py_3087["plugin/scripts/test_reqmap_report.py:3087"]
  ARCH_CONFIG_060 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_3087
  f_plugin_scripts_reqmap_engine_config_py_203_213["plugin/scripts/reqmap_engine/config.py:203-213"]
  ARCH_CONFIG_060 -->|implements| f_plugin_scripts_reqmap_engine_config_py_203_213
  ARCH_CONTEXT_048["Consolidated Context section<br><small>ARCH-CONTEXT-048</small>"]
  f_plugin_scripts_test_reqmap_report_py_457_4134["plugin/scripts/test_reqmap_report.py:457-4134"]
  ARCH_CONTEXT_048 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_457_4134
  f_plugin_scripts_reqmap_engine_text_py_178["plugin/scripts/reqmap_engine/text.py:178"]
  ARCH_CONTEXT_048 -->|implements| f_plugin_scripts_reqmap_engine_text_py_178
  ARCH_COVERAGE_029["Untagged-code coverage signal<br><small>ARCH-COVERAGE-029</small>"]
  f_plugin_scripts_test_reqmap_report_py_1446["plugin/scripts/test_reqmap_report.py:1446"]
  ARCH_COVERAGE_029 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1446
  f_plugin_scripts_reqmap_engine_health_py_243["plugin/scripts/reqmap_engine/health.py:243"]
  ARCH_COVERAGE_029 -->|implements| f_plugin_scripts_reqmap_engine_health_py_243
  f_plugin_scripts_reqmap_engine_orphans_py_134_150["plugin/scripts/reqmap_engine/orphans.py:134-150"]
  ARCH_COVERAGE_029 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_134_150
  ARCH_DECOMPOSE_050["Clause decomposition scaffold<br><small>ARCH-DECOMPOSE-050</small>"]
  f_plugin_scripts_test_reqmap_author_py_1652_3048["plugin/scripts/test_reqmap_author.py:1652-3048"]
  ARCH_DECOMPOSE_050 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1652_3048
  f_plugin_scripts_test_reqmap_report_py_5195["plugin/scripts/test_reqmap_report.py:5195"]
  ARCH_DECOMPOSE_050 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_5195
  f_plugin_scripts_reqmap_engine_decompose_py_53_107["plugin/scripts/reqmap_engine/decompose.py:53-107"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_decompose_py_53_107
  f_plugin_scripts_reqmap_engine_groups_py_61_400["plugin/scripts/reqmap_engine/groups.py:61-400"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_groups_py_61_400
  f_plugin_scripts_reqmap_engine_lint_py_72_89["plugin/scripts/reqmap_engine/lint.py:72-89"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_72_89
  f_plugin_scripts_reqmap_engine_lintrules_py_17["plugin/scripts/reqmap_engine/lintrules.py:17"]
  ARCH_DECOMPOSE_050 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_17
  ARCH_DESIGN_061["Advisory design review<br><small>ARCH-DESIGN-061</small>"]
  f_plugin_scripts_test_reqmap_report_py_3470_5195["plugin/scripts/test_reqmap_report.py:3470-5195"]
  ARCH_DESIGN_061 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_3470_5195
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
  f_plugin_scripts_reqmap_engine_rules_py_381["plugin/scripts/reqmap_engine/rules.py:381"]
  ARCH_DOCBUNDLE_026 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_381
  ARCH_DOCCLAIMS_071["Corpus counts a document states about itself<br><small>ARCH-DOCCLAIMS-071</small>"]
  f_plugin_scripts_test_reqmap_gate_py_2765["plugin/scripts/test_reqmap_gate.py:2765"]
  ARCH_DOCCLAIMS_071 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2765
  f_plugin_scripts_reqmap_engine_docclaims_py_68["plugin/scripts/reqmap_engine/docclaims.py:68"]
  ARCH_DOCCLAIMS_071 -->|implements| f_plugin_scripts_reqmap_engine_docclaims_py_68
  ARCH_DRIFT_003["Contract hashing & lock<br><small>ARCH-DRIFT-003</small>"]
  f_plugin_scripts_test_reqmap_gate_py_52_2520["plugin/scripts/test_reqmap_gate.py:52-2520"]
  ARCH_DRIFT_003 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_52_2520
  f_plugin_scripts_test_reqmap_scan_py_1402["plugin/scripts/test_reqmap_scan.py:1402"]
  ARCH_DRIFT_003 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_1402
  f_plugin_scripts_reqmap_engine_locks_py_11_120["plugin/scripts/reqmap_engine/locks.py:11-120"]
  ARCH_DRIFT_003 -->|implements| f_plugin_scripts_reqmap_engine_locks_py_11_120
  f_plugin_scripts_reqmap_engine_rules_py_350["plugin/scripts/reqmap_engine/rules.py:350"]
  ARCH_DRIFT_003 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_350
  f_plugin_scripts_reqmap_engine_sections_py_179["plugin/scripts/reqmap_engine/sections.py:179"]
  ARCH_DRIFT_003 -->|implements| f_plugin_scripts_reqmap_engine_sections_py_179
  ARCH_DRIFTIMPACT_035["Drift blast-radius: name dependents<br><small>ARCH-DRIFTIMPACT-035</small>"]
  f_plugin_scripts_test_reqmap_gate_py_454["plugin/scripts/test_reqmap_gate.py:454"]
  ARCH_DRIFTIMPACT_035 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_454
  f_plugin_scripts_test_reqmap_report_py_4592["plugin/scripts/test_reqmap_report.py:4592"]
  ARCH_DRIFTIMPACT_035 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4592
  f_plugin_scripts_reqmap_engine_rules_py_350["plugin/scripts/reqmap_engine/rules.py:350"]
  ARCH_DRIFTIMPACT_035 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_350
  ARCH_EXTRACT_008["Legacy extraction<br><small>ARCH-EXTRACT-008</small>"]
  f_plugin_scripts_test_reqmap_author_py_30_2090["plugin/scripts/test_reqmap_author.py:30-2090"]
  ARCH_EXTRACT_008 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_30_2090
  f_plugin_scripts_test_reqmap_scan_py_452["plugin/scripts/test_reqmap_scan.py:452"]
  ARCH_EXTRACT_008 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_452
  f_plugin_scripts_reqmap_engine_candidates_py_362_405["plugin/scripts/reqmap_engine/candidates.py:362-405"]
  ARCH_EXTRACT_008 -->|implements| f_plugin_scripts_reqmap_engine_candidates_py_362_405
  f_plugin_scripts_reqmap_engine_draft_py_49_318["plugin/scripts/reqmap_engine/draft.py:49-318"]
  ARCH_EXTRACT_008 -->|implements| f_plugin_scripts_reqmap_engine_draft_py_49_318
  f_plugin_scripts_reqmap_engine_tags_py_342_356["plugin/scripts/reqmap_engine/tags.py:342-356"]
  ARCH_EXTRACT_008 -->|implements| f_plugin_scripts_reqmap_engine_tags_py_342_356
  ARCH_FANOUT_052["Hierarchy breadth<br><small>ARCH-FANOUT-052</small>"]
  f_plugin_scripts_test_reqmap_author_py_1852_2051["plugin/scripts/test_reqmap_author.py:1852-2051"]
  ARCH_FANOUT_052 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1852_2051
  f_plugin_scripts_reqmap_engine_lint_py_14_54["plugin/scripts/reqmap_engine/lint.py:14-54"]
  ARCH_FANOUT_052 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_14_54
  ARCH_FINDINGS_010["Open-findings report<br><small>ARCH-FINDINGS-010</small>"]
  f_plugin_scripts_test_reqmap_report_py_153_4185["plugin/scripts/test_reqmap_report.py:153-4185"]
  ARCH_FINDINGS_010 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_153_4185
  f_plugin_scripts_reqmap_engine_findings_py_13_128["plugin/scripts/reqmap_engine/findings.py:13-128"]
  ARCH_FINDINGS_010 -->|implements| f_plugin_scripts_reqmap_engine_findings_py_13_128
  f_plugin_scripts_reqmap_engine_mapcmd_py_45_202["plugin/scripts/reqmap_engine/mapcmd.py:45-202"]
  ARCH_FINDINGS_010 -->|implements| f_plugin_scripts_reqmap_engine_mapcmd_py_45_202
  f_plugin_scripts_reqmap_engine_text_py_158["plugin/scripts/reqmap_engine/text.py:158"]
  ARCH_FINDINGS_010 -->|implements| f_plugin_scripts_reqmap_engine_text_py_158
  ARCH_GITRUN_067["Talking to git<br><small>ARCH-GITRUN-067</small>"]
  f_plugin_scripts_test_reqmap_scan_py_1483["plugin/scripts/test_reqmap_scan.py:1483"]
  ARCH_GITRUN_067 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_1483
  f_plugin_scripts_reqmap_engine_git_py_6_112["plugin/scripts/reqmap_engine/git.py:6-112"]
  ARCH_GITRUN_067 -->|implements| f_plugin_scripts_reqmap_engine_git_py_6_112
  ARCH_HEALTH_017["Corpus health snapshot<br><small>ARCH-HEALTH-017</small>"]
  f_plugin_scripts_test_reqmap_report_py_1318_5195["plugin/scripts/test_reqmap_report.py:1318-5195"]
  ARCH_HEALTH_017 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1318_5195
  f_plugin_scripts_reqmap_engine_health_py_17_349["plugin/scripts/reqmap_engine/health.py:17-349"]
  ARCH_HEALTH_017 -->|implements| f_plugin_scripts_reqmap_engine_health_py_17_349
  ARCH_IMPLEMENT_063["The brief for implementing a requirement<br><small>ARCH-IMPLEMENT-063</small>"]
  style ARCH_IMPLEMENT_063 fill:#eee,stroke:#bbb,color:#888
  ARCH_INIT_012["First-use bootstrap<br><small>ARCH-INIT-012</small>"]
  f_plugin_scripts_test_reqmap_author_py_432_633["plugin/scripts/test_reqmap_author.py:432-633"]
  ARCH_INIT_012 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_432_633
  f_plugin_scripts_test_reqmap_report_py_2167_5195["plugin/scripts/test_reqmap_report.py:2167-5195"]
  ARCH_INIT_012 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2167_5195
  f_plugin_scripts_reqmap_engine_init_py_132_241["plugin/scripts/reqmap_engine/init.py:132-241"]
  ARCH_INIT_012 -->|implements| f_plugin_scripts_reqmap_engine_init_py_132_241
  ARCH_LEVEL_051["Specification level<br><small>ARCH-LEVEL-051</small>"]
  f_plugin_scripts_test_reqmap_gate_py_2090_2426["plugin/scripts/test_reqmap_gate.py:2090-2426"]
  ARCH_LEVEL_051 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2090_2426
  f_plugin_scripts_reqmap_engine_mapdata_py_61["plugin/scripts/reqmap_engine/mapdata.py:61"]
  ARCH_LEVEL_051 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_61
  f_plugin_scripts_reqmap_engine_model_py_23["plugin/scripts/reqmap_engine/model.py:23"]
  ARCH_LEVEL_051 -->|implements| f_plugin_scripts_reqmap_engine_model_py_23
  f_plugin_scripts_reqmap_engine_rules_py_36["plugin/scripts/reqmap_engine/rules.py:36"]
  ARCH_LEVEL_051 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_36
  ARCH_LEVELRETROFIT_066["Giving an existing corpus the three rungs<br><small>ARCH-LEVELRETROFIT-066</small>"]
  f_plugin_scripts_test_reqmap_author_py_1102["plugin/scripts/test_reqmap_author.py:1102"]
  ARCH_LEVELRETROFIT_066 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1102
  f_plugin_scripts_reqmap_engine_levels_py_11_103["plugin/scripts/reqmap_engine/levels.py:11-103"]
  ARCH_LEVELRETROFIT_066 -->|implements| f_plugin_scripts_reqmap_engine_levels_py_11_103
  f_plugin_scripts_reqmap_engine_pyramid_py_45_69["plugin/scripts/reqmap_engine/pyramid.py:45-69"]
  ARCH_LEVELRETROFIT_066 -->|implements| f_plugin_scripts_reqmap_engine_pyramid_py_45_69
  ARCH_LINT_014["Requirement readability linter<br><small>ARCH-LINT-014</small>"]
  f_plugin_scripts_test_reqmap_author_py_734["plugin/scripts/test_reqmap_author.py:734"]
  ARCH_LINT_014 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_734
  f_plugin_scripts_test_reqmap_gate_py_2883["plugin/scripts/test_reqmap_gate.py:2883"]
  ARCH_LINT_014 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2883
  f_plugin_scripts_reqmap_engine_lint_py_13_89["plugin/scripts/reqmap_engine/lint.py:13-89"]
  ARCH_LINT_014 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_13_89
  f_plugin_scripts_reqmap_engine_lintrules_py_88_112["plugin/scripts/reqmap_engine/lintrules.py:88-112"]
  ARCH_LINT_014 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_88_112
  ARCH_LINTCHECKS_025["Readability & scope checks<br><small>ARCH-LINTCHECKS-025</small>"]
  f_plugin_scripts_test_reqmap_author_py_734_1307["plugin/scripts/test_reqmap_author.py:734-1307"]
  ARCH_LINTCHECKS_025 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_734_1307
  f_plugin_scripts_test_reqmap_scan_py_529["plugin/scripts/test_reqmap_scan.py:529"]
  ARCH_LINTCHECKS_025 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_529
  f_plugin_scripts_reqmap_engine_lint_py_13_53["plugin/scripts/reqmap_engine/lint.py:13-53"]
  ARCH_LINTCHECKS_025 -->|implements| f_plugin_scripts_reqmap_engine_lint_py_13_53
  f_plugin_scripts_reqmap_engine_lintrules_py_106_414["plugin/scripts/reqmap_engine/lintrules.py:106-414"]
  ARCH_LINTCHECKS_025 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_106_414
  ARCH_MAP_007["Requirement graph (_map.json)<br><small>ARCH-MAP-007</small>"]
  f_plugin_scripts_test_reqmap_gate_py_936_2050["plugin/scripts/test_reqmap_gate.py:936-2050"]
  ARCH_MAP_007 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_936_2050
  f_plugin_scripts_test_reqmap_report_py_281_5195["plugin/scripts/test_reqmap_report.py:281-5195"]
  ARCH_MAP_007 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_281_5195
  f_plugin_scripts_test_reqmap_scan_py_545["plugin/scripts/test_reqmap_scan.py:545"]
  ARCH_MAP_007 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_545
  f_plugin_scripts_reqmap_engine_acceptance_py_66["plugin/scripts/reqmap_engine/acceptance.py:66"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_acceptance_py_66
  f_plugin_scripts_reqmap_engine_git_py_48["plugin/scripts/reqmap_engine/git.py:48"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_git_py_48
  f_plugin_scripts_reqmap_engine_mapcmd_py_24_230["plugin/scripts/reqmap_engine/mapcmd.py:24-230"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapcmd_py_24_230
  f_plugin_scripts_reqmap_engine_mapdata_py_38["plugin/scripts/reqmap_engine/mapdata.py:38"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_38
  f_plugin_scripts_reqmap_engine_mapjson_py_57_109["plugin/scripts/reqmap_engine/mapjson.py:57-109"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapjson_py_57_109
  f_plugin_scripts_reqmap_engine_mapmd_py_42["plugin/scripts/reqmap_engine/mapmd.py:42"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_mapmd_py_42
  f_plugin_scripts_reqmap_engine_model_py_232["plugin/scripts/reqmap_engine/model.py:232"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_model_py_232
  f_plugin_scripts_reqmap_engine_rules_py_460["plugin/scripts/reqmap_engine/rules.py:460"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_460
  f_plugin_scripts_reqmap_engine_targets_py_1["plugin/scripts/reqmap_engine/targets.py:1"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_targets_py_1
  f_plugin_scripts_reqmap_engine_text_py_28_109["plugin/scripts/reqmap_engine/text.py:28-109"]
  ARCH_MAP_007 -->|implements| f_plugin_scripts_reqmap_engine_text_py_28_109
  ARCH_MAPDIAGRAMS_055["Mermaid diagrams (_map.md)<br><small>ARCH-MAPDIAGRAMS-055</small>"]
  f_plugin_scripts_test_reqmap_report_py_31_4616["plugin/scripts/test_reqmap_report.py:31-4616"]
  ARCH_MAPDIAGRAMS_055 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_31_4616
  f_plugin_scripts_reqmap_engine_mapmd_py_49_310["plugin/scripts/reqmap_engine/mapmd.py:49-310"]
  ARCH_MAPDIAGRAMS_055 -->|implements| f_plugin_scripts_reqmap_engine_mapmd_py_49_310
  ARCH_MEMBERDRIFT_027["Reverse-direction member drift<br><small>ARCH-MEMBERDRIFT-027</small>"]
  f_plugin_scripts_test_reqmap_gate_py_294["plugin/scripts/test_reqmap_gate.py:294"]
  ARCH_MEMBERDRIFT_027 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_294
  f_plugin_scripts_reqmap_engine_locks_py_53_290["plugin/scripts/reqmap_engine/locks.py:53-290"]
  ARCH_MEMBERDRIFT_027 -->|implements| f_plugin_scripts_reqmap_engine_locks_py_53_290
  f_plugin_scripts_reqmap_engine_rules_py_364["plugin/scripts/reqmap_engine/rules.py:364"]
  ARCH_MEMBERDRIFT_027 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_364
  ARCH_NEW_004["Scaffold a requirement<br><small>ARCH-NEW-004</small>"]
  f_plugin_scripts_test_reqmap_author_py_99_2965["plugin/scripts/test_reqmap_author.py:99-2965"]
  ARCH_NEW_004 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_99_2965
  f_plugin_scripts_reqmap_engine_author_py_93_133["plugin/scripts/reqmap_engine/author.py:93-133"]
  ARCH_NEW_004 -->|implements| f_plugin_scripts_reqmap_engine_author_py_93_133
  ARCH_NEXT_013["What-should-I-do-next report<br><small>ARCH-NEXT-013</small>"]
  f_plugin_scripts_test_reqmap_author_py_1738["plugin/scripts/test_reqmap_author.py:1738"]
  ARCH_NEXT_013 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1738
  f_plugin_scripts_test_reqmap_report_py_918_3907["plugin/scripts/test_reqmap_report.py:918-3907"]
  ARCH_NEXT_013 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_918_3907
  f_plugin_scripts_reqmap_engine_lintrules_py_17["plugin/scripts/reqmap_engine/lintrules.py:17"]
  ARCH_NEXT_013 -->|implements| f_plugin_scripts_reqmap_engine_lintrules_py_17
  f_plugin_scripts_reqmap_engine_orphans_py_150["plugin/scripts/reqmap_engine/orphans.py:150"]
  ARCH_NEXT_013 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_150
  f_plugin_scripts_reqmap_engine_risk_py_12_192["plugin/scripts/reqmap_engine/risk.py:12-192"]
  ARCH_NEXT_013 -->|implements| f_plugin_scripts_reqmap_engine_risk_py_12_192
  ARCH_ORPHANCODE_034["Orphan-code warning<br><small>ARCH-ORPHANCODE-034</small>"]
  f_plugin_scripts_test_reqmap_gate_py_394_2474["plugin/scripts/test_reqmap_gate.py:394-2474"]
  ARCH_ORPHANCODE_034 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_394_2474
  f_plugin_scripts_reqmap_engine_orphans_py_172["plugin/scripts/reqmap_engine/orphans.py:172"]
  ARCH_ORPHANCODE_034 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_172
  f_plugin_scripts_reqmap_engine_rules_py_423["plugin/scripts/reqmap_engine/rules.py:423"]
  ARCH_ORPHANCODE_034 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_423
  ARCH_PARSE_001["Requirement reading<br><small>ARCH-PARSE-001</small>"]
  f_plugin_scripts_test_reqmap_report_py_5195["plugin/scripts/test_reqmap_report.py:5195"]
  ARCH_PARSE_001 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_5195
  f_plugin_scripts_test_reqmap_scan_py_32_860["plugin/scripts/test_reqmap_scan.py:32-860"]
  ARCH_PARSE_001 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_32_860
  f_plugin_scripts_reqmap_engine_model_py_60_162["plugin/scripts/reqmap_engine/model.py:60-162"]
  ARCH_PARSE_001 -->|implements| f_plugin_scripts_reqmap_engine_model_py_60_162
  f_plugin_scripts_reqmap_engine_parse_py_7_97["plugin/scripts/reqmap_engine/parse.py:7-97"]
  ARCH_PARSE_001 -->|implements| f_plugin_scripts_reqmap_engine_parse_py_7_97
  ARCH_PIPE_046["A closed output pipe ends a command quietly<br><small>ARCH-PIPE-046</small>"]
  f_plugin_scripts_reqmap_py_342_360["plugin/scripts/reqmap.py:342-360"]
  ARCH_PIPE_046 -->|implements| f_plugin_scripts_reqmap_py_342_360
  f_plugin_scripts_test_reqmap_gate_py_2069["plugin/scripts/test_reqmap_gate.py:2069"]
  ARCH_PIPE_046 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2069
  ARCH_PLANDRIFT_069["Plan items whose code has moved on without them<br><small>ARCH-PLANDRIFT-069</small>"]
  f_plugin_scripts_test_reqmap_report_py_2822["plugin/scripts/test_reqmap_report.py:2822"]
  ARCH_PLANDRIFT_069 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2822
  f_plugin_scripts_reqmap_engine_plandrift_py_190_229["plugin/scripts/reqmap_engine/plandrift.py:190-229"]
  ARCH_PLANDRIFT_069 -->|implements| f_plugin_scripts_reqmap_engine_plandrift_py_190_229
  ARCH_PROMOTE_011["Confirmation is a human's answer, and an edit takes it back<br><small>ARCH-PROMOTE-011</small>"]
  f_plugin_scripts_test_reqmap_author_py_377_2781["plugin/scripts/test_reqmap_author.py:377-2781"]
  ARCH_PROMOTE_011 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_377_2781
  f_plugin_scripts_test_reqmap_gate_py_825["plugin/scripts/test_reqmap_gate.py:825"]
  ARCH_PROMOTE_011 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_825
  f_plugin_scripts_test_reqmap_report_py_1669_2113["plugin/scripts/test_reqmap_report.py:1669-2113"]
  ARCH_PROMOTE_011 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1669_2113
  f_plugin_scripts_reqmap_engine_author_py_263_289["plugin/scripts/reqmap_engine/author.py:263-289"]
  ARCH_PROMOTE_011 -->|implements| f_plugin_scripts_reqmap_engine_author_py_263_289
  ARCH_PROMOTE_TODO_001["Promote a TODO item into a requirement draft<br><small>ARCH-PROMOTE-TODO-001</small>"]
  f_plugin_scripts_test_reqmap_author_py_1339_2187["plugin/scripts/test_reqmap_author.py:1339-2187"]
  ARCH_PROMOTE_TODO_001 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1339_2187
  f_plugin_scripts_test_reqmap_report_py_2113["plugin/scripts/test_reqmap_report.py:2113"]
  ARCH_PROMOTE_TODO_001 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2113
  f_plugin_scripts_reqmap_engine_author_py_160_229["plugin/scripts/reqmap_engine/author.py:160-229"]
  ARCH_PROMOTE_TODO_001 -->|implements| f_plugin_scripts_reqmap_engine_author_py_160_229
  ARCH_PROSE_024["Prose capability classification & drafting<br><small>ARCH-PROSE-024</small>"]
  f_plugin_scripts_test_reqmap_scan_py_358_1264["plugin/scripts/test_reqmap_scan.py:358-1264"]
  ARCH_PROSE_024 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_358_1264
  f_plugin_scripts_reqmap_engine_draft_py_13_240["plugin/scripts/reqmap_engine/draft.py:13-240"]
  ARCH_PROSE_024 -->|implements| f_plugin_scripts_reqmap_engine_draft_py_13_240
  f_plugin_scripts_reqmap_engine_tags_py_264["plugin/scripts/reqmap_engine/tags.py:264"]
  ARCH_PROSE_024 -->|implements| f_plugin_scripts_reqmap_engine_tags_py_264
  ARCH_PYFLOOR_040["Declared Python support floor<br><small>ARCH-PYFLOOR-040</small>"]
  f__github_workflows_ci_yml_3[".github/workflows/ci.yml:3"]
  ARCH_PYFLOOR_040 -->|implements| f__github_workflows_ci_yml_3
  f_plugin_scripts_reqmap_py_96["plugin/scripts/reqmap.py:96"]
  ARCH_PYFLOOR_040 -->|implements| f_plugin_scripts_reqmap_py_96
  f_plugin_scripts_test_reqmap_gate_py_1775_2440["plugin/scripts/test_reqmap_gate.py:1775-2440"]
  ARCH_PYFLOOR_040 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_1775_2440
  ARCH_REGISTRYLAG_035["Registry-lag signal — commits since the requirements dir was last touched<br><small>ARCH-REGISTRYLAG-035</small>"]
  f_plugin_scripts_test_reqmap_report_py_1470["plugin/scripts/test_reqmap_report.py:1470"]
  ARCH_REGISTRYLAG_035 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1470
  f_plugin_scripts_reqmap_engine_health_py_102_250["plugin/scripts/reqmap_engine/health.py:102-250"]
  ARCH_REGISTRYLAG_035 -->|implements| f_plugin_scripts_reqmap_engine_health_py_102_250
  ARCH_RELEASE_072["Releasing from the plan<br><small>ARCH-RELEASE-072</small>"]
  f_plugin_scripts_test_reqmap_author_py_3823["plugin/scripts/test_reqmap_author.py:3823"]
  ARCH_RELEASE_072 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_3823
  f_plugin_scripts_reqmap_engine_plandrift_py_251_301["plugin/scripts/reqmap_engine/plandrift.py:251-301"]
  ARCH_RELEASE_072 -->|implements| f_plugin_scripts_reqmap_engine_plandrift_py_251_301
  f_plugin_scripts_reqmap_engine_release_py_1_290["plugin/scripts/reqmap_engine/release.py:1-290"]
  ARCH_RELEASE_072 -->|implements| f_plugin_scripts_reqmap_engine_release_py_1_290
  f_plugin_scripts_reqmap_engine_versions_py_1_201["plugin/scripts/reqmap_engine/versions.py:1-201"]
  ARCH_RELEASE_072 -->|implements| f_plugin_scripts_reqmap_engine_versions_py_1_201
  ARCH_REPRO_041["Committed build artifacts stay re-derivable<br><small>ARCH-REPRO-041</small>"]
  f__github_workflows_ci_yml_4[".github/workflows/ci.yml:4"]
  ARCH_REPRO_041 -->|implements| f__github_workflows_ci_yml_4
  ARCH_RETIRE_064["Taking a requirement out of service<br><small>ARCH-RETIRE-064</small>"]
  f_plugin_scripts_test_reqmap_author_py_1926_2993["plugin/scripts/test_reqmap_author.py:1926-2993"]
  ARCH_RETIRE_064 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1926_2993
  f_plugin_scripts_test_reqmap_report_py_5195["plugin/scripts/test_reqmap_report.py:5195"]
  ARCH_RETIRE_064 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_5195
  f_plugin_scripts_reqmap_engine_retire_py_15_243["plugin/scripts/reqmap_engine/retire.py:15-243"]
  ARCH_RETIRE_064 -->|implements| f_plugin_scripts_reqmap_engine_retire_py_15_243
  ARCH_REVIEW_022["AI requirement-quality review (deterministic plan + advisory pass)<br><small>ARCH-REVIEW-022</small>"]
  f_plugin_scripts_test_reqmap_author_py_1425["plugin/scripts/test_reqmap_author.py:1425"]
  ARCH_REVIEW_022 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1425
  f_plugin_scripts_reqmap_engine_review_py_10["plugin/scripts/reqmap_engine/review.py:10"]
  ARCH_REVIEW_022 -->|implements| f_plugin_scripts_reqmap_engine_review_py_10
  f_plugin_skills_requirement_quality_review_SKILL_md_6["plugin/skills/requirement-quality-review/SKILL.md:6"]
  ARCH_REVIEW_022 -->|implements| f_plugin_skills_requirement_quality_review_SKILL_md_6
  f_plugin_skills_requirement_quality_review_SKILL_universal_md_9["plugin/skills/requirement-quality-review/SKILL.universal.md:9"]
  ARCH_REVIEW_022 -->|implements| f_plugin_skills_requirement_quality_review_SKILL_universal_md_9
  ARCH_ROADMAP_038["Roadmap coherence signals<br><small>ARCH-ROADMAP-038</small>"]
  f_docs_plan_source_audit_html_6["docs/plan-source-audit.html:6"]
  ARCH_ROADMAP_038 -->|generated-from| f_docs_plan_source_audit_html_6
  f_plugin_scripts_test_reqmap_report_py_2231_4575["plugin/scripts/test_reqmap_report.py:2231-4575"]
  ARCH_ROADMAP_038 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_2231_4575
  f_plugin_scripts_reqmap_engine_health_py_256["plugin/scripts/reqmap_engine/health.py:256"]
  ARCH_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_engine_health_py_256
  f_plugin_scripts_reqmap_engine_mapdata_py_116_282["plugin/scripts/reqmap_engine/mapdata.py:116-282"]
  ARCH_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_116_282
  f_plugin_scripts_reqmap_engine_plandrift_py_319["plugin/scripts/reqmap_engine/plandrift.py:319"]
  ARCH_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_engine_plandrift_py_319
  f_plugin_scripts_reqmap_engine_targets_py_157["plugin/scripts/reqmap_engine/targets.py:157"]
  ARCH_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_engine_targets_py_157
  f_plugin_scripts_reqmap_engine_versions_py_144_173["plugin/scripts/reqmap_engine/versions.py:144-173"]
  ARCH_ROADMAP_038 -->|implements| f_plugin_scripts_reqmap_engine_versions_py_144_173
  ARCH_RULES_059["The gate rule registry<br><small>ARCH-RULES-059</small>"]
  f_plugin_scripts_test_reqmap_gate_py_2181_2601["plugin/scripts/test_reqmap_gate.py:2181-2601"]
  ARCH_RULES_059 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_2181_2601
  f_plugin_scripts_reqmap_engine_gate_py_23_179["plugin/scripts/reqmap_engine/gate.py:23-179"]
  ARCH_RULES_059 -->|implements| f_plugin_scripts_reqmap_engine_gate_py_23_179
  f_plugin_scripts_reqmap_engine_model_py_111_141["plugin/scripts/reqmap_engine/model.py:111-141"]
  ARCH_RULES_059 -->|implements| f_plugin_scripts_reqmap_engine_model_py_111_141
  f_plugin_scripts_reqmap_engine_workspace_py_83_138["plugin/scripts/reqmap_engine/workspace.py:83-138"]
  ARCH_RULES_059 -->|implements| f_plugin_scripts_reqmap_engine_workspace_py_83_138
  ARCH_SCAN_002["Member discovery<br><small>ARCH-SCAN-002</small>"]
  f_plugin_scripts_test_reqmap_scan_py_113_1421["plugin/scripts/test_reqmap_scan.py:113-1421"]
  ARCH_SCAN_002 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_113_1421
  f_plugin_scripts_reqmap_engine_scan_py_16_274["plugin/scripts/reqmap_engine/scan.py:16-274"]
  ARCH_SCAN_002 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_16_274
  f_plugin_scripts_reqmap_engine_tags_py_78_232["plugin/scripts/reqmap_engine/tags.py:78-232"]
  ARCH_SCAN_002 -->|implements| f_plugin_scripts_reqmap_engine_tags_py_78_232
  ARCH_SCANCACHE_023["Opt-in scan cache<br><small>ARCH-SCANCACHE-023</small>"]
  f_plugin_scripts_test_reqmap_scan_py_586["plugin/scripts/test_reqmap_scan.py:586"]
  ARCH_SCANCACHE_023 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_586
  f_plugin_scripts_reqmap_engine_scan_py_73_207["plugin/scripts/reqmap_engine/scan.py:73-207"]
  ARCH_SCANCACHE_023 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_73_207
  ARCH_SEARCH_036["Free-text requirement search<br><small>ARCH-SEARCH-036</small>"]
  f_app_scripts_smoke_views_jsx_4["app/scripts/smoke/views.jsx:4"]
  ARCH_SEARCH_036 -->|tested-by| f_app_scripts_smoke_views_jsx_4
  f_app_src_lib_search_js_1["app/src/lib/search.js:1"]
  ARCH_SEARCH_036 -->|implements| f_app_src_lib_search_js_1
  f_plugin_scripts_test_reqmap_report_py_1238_5116["plugin/scripts/test_reqmap_report.py:1238-5116"]
  ARCH_SEARCH_036 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1238_5116
  f_plugin_scripts_reqmap_engine_similar_py_295_344["plugin/scripts/reqmap_engine/similar.py:295-344"]
  ARCH_SEARCH_036 -->|implements| f_plugin_scripts_reqmap_engine_similar_py_295_344
  ARCH_SECTIONS_068["Reading a requirement's sections<br><small>ARCH-SECTIONS-068</small>"]
  f_plugin_scripts_test_reqmap_scan_py_1548["plugin/scripts/test_reqmap_scan.py:1548"]
  ARCH_SECTIONS_068 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_1548
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
  f_plugin_scripts_test_reqmap_report_py_4824["plugin/scripts/test_reqmap_report.py:4824"]
  ARCH_SELFGATE_039 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_4824
  f_scripts_changelog_notes_py_2["scripts/changelog_notes.py:2"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_changelog_notes_py_2
  f_scripts_check_engine_bump_py_2["scripts/check_engine_bump.py:2"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_check_engine_bump_py_2
  f_scripts_check_retired_verbs_py_2_200["scripts/check_retired_verbs.py:2-200"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_check_retired_verbs_py_2_200
  f_scripts_check_versions_py_2["scripts/check_versions.py:2"]
  ARCH_SELFGATE_039 -->|implements| f_scripts_check_versions_py_2
  f_scripts_test_changelog_notes_py_2["scripts/test_changelog_notes.py:2"]
  ARCH_SELFGATE_039 -->|tested-by| f_scripts_test_changelog_notes_py_2
  f_scripts_test_check_engine_bump_py_56["scripts/test_check_engine_bump.py:56"]
  ARCH_SELFGATE_039 -->|tested-by| f_scripts_test_check_engine_bump_py_56
  f_scripts_test_check_retired_verbs_py_12["scripts/test_check_retired_verbs.py:12"]
  ARCH_SELFGATE_039 -->|tested-by| f_scripts_test_check_retired_verbs_py_12
  f_scripts_test_check_versions_py_94_101["scripts/test_check_versions.py:94-101"]
  ARCH_SELFGATE_039 -->|tested-by| f_scripts_test_check_versions_py_94_101
  ARCH_SHOW_015["Single-requirement dossier<br><small>ARCH-SHOW-015</small>"]
  f_plugin_scripts_test_reqmap_report_py_1075_4053["plugin/scripts/test_reqmap_report.py:1075-4053"]
  ARCH_SHOW_015 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1075_4053
  f_plugin_scripts_reqmap_engine_show_py_10["plugin/scripts/reqmap_engine/show.py:10"]
  ARCH_SHOW_015 -->|implements| f_plugin_scripts_reqmap_engine_show_py_10
  ARCH_SIMILAR_016["Duplicate-capability detector<br><small>ARCH-SIMILAR-016</small>"]
  f_plugin_scripts_test_reqmap_report_py_1157_4457["plugin/scripts/test_reqmap_report.py:1157-4457"]
  ARCH_SIMILAR_016 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1157_4457
  f_plugin_scripts_reqmap_engine_similar_py_18_219["plugin/scripts/reqmap_engine/similar.py:18-219"]
  ARCH_SIMILAR_016 -->|implements| f_plugin_scripts_reqmap_engine_similar_py_18_219
  ARCH_SITE_026["Generate & maintain a project presentation page<br><small>ARCH-SITE-026</small>"]
  f_plugin_scripts_test_reqmap_report_py_1708["plugin/scripts/test_reqmap_report.py:1708"]
  ARCH_SITE_026 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1708
  f_plugin_scripts_reqmap_engine_git_py_72_92["plugin/scripts/reqmap_engine/git.py:72-92"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_git_py_72_92
  f_plugin_scripts_reqmap_engine_init_py_270["plugin/scripts/reqmap_engine/init.py:270"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_init_py_270
  f_plugin_scripts_reqmap_engine_mapcmd_py_148_215["plugin/scripts/reqmap_engine/mapcmd.py:148-215"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_mapcmd_py_148_215
  f_plugin_scripts_reqmap_engine_site_py_10_147["plugin/scripts/reqmap_engine/site.py:10-147"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_site_py_10_147
  f_plugin_scripts_reqmap_engine_site_template_py_9_316["plugin/scripts/reqmap_engine/site_template.py:9-316"]
  ARCH_SITE_026 -->|implements| f_plugin_scripts_reqmap_engine_site_template_py_9_316
  ARCH_STALEENGINE_043["Stale vendored engine, reported in CI<br><small>ARCH-STALEENGINE-043</small>"]
  f_check_action_yml_3["check/action.yml:3"]
  ARCH_STALEENGINE_043 -->|implements| f_check_action_yml_3
  f_check_engine_staleness_py_2["check/engine_staleness.py:2"]
  ARCH_STALEENGINE_043 -->|implements| f_check_engine_staleness_py_2
  f_scripts_test_engine_staleness_py_49_154["scripts/test_engine_staleness.py:49-154"]
  ARCH_STALEENGINE_043 -->|tested-by| f_scripts_test_engine_staleness_py_49_154
  ARCH_SUGGESTVERIFIES_047["Suggest per-criterion 'verifies:' tags<br><small>ARCH-SUGGESTVERIFIES-047</small>"]
  style ARCH_SUGGESTVERIFIES_047 fill:#eee,stroke:#bbb,color:#888
  ARCH_TESTLINK_018["Test-link integrity check<br><small>ARCH-TESTLINK-018</small>"]
  f_plugin_scripts_test_reqmap_gate_py_625_2405["plugin/scripts/test_reqmap_gate.py:625-2405"]
  ARCH_TESTLINK_018 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_625_2405
  f_plugin_scripts_reqmap_engine_rules_py_167["plugin/scripts/reqmap_engine/rules.py:167"]
  ARCH_TESTLINK_018 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_167
  f_plugin_scripts_reqmap_engine_workspace_py_52_74["plugin/scripts/reqmap_engine/workspace.py:52-74"]
  ARCH_TESTLINK_018 -->|implements| f_plugin_scripts_reqmap_engine_workspace_py_52_74
  ARCH_TRACE_020["Upstream traceability<br><small>ARCH-TRACE-020</small>"]
  f_plugin_scripts_test_reqmap_gate_py_825_1086["plugin/scripts/test_reqmap_gate.py:825-1086"]
  ARCH_TRACE_020 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_825_1086
  f_plugin_scripts_reqmap_engine_axis_py_13_55["plugin/scripts/reqmap_engine/axis.py:13-55"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_axis_py_13_55
  f_plugin_scripts_reqmap_engine_mapdata_py_50_109["plugin/scripts/reqmap_engine/mapdata.py:50-109"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_mapdata_py_50_109
  f_plugin_scripts_reqmap_engine_model_py_178["plugin/scripts/reqmap_engine/model.py:178"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_model_py_178
  f_plugin_scripts_reqmap_engine_rules_py_56_245["plugin/scripts/reqmap_engine/rules.py:56-245"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_56_245
  f_plugin_scripts_reqmap_engine_show_py_48["plugin/scripts/reqmap_engine/show.py:48"]
  ARCH_TRACE_020 -->|implements| f_plugin_scripts_reqmap_engine_show_py_48
  ARCH_TRACKED_042["Untracked members reported<br><small>ARCH-TRACKED-042</small>"]
  f_plugin_scripts_test_reqmap_scan_py_804["plugin/scripts/test_reqmap_scan.py:804"]
  ARCH_TRACKED_042 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_804
  f_plugin_scripts_reqmap_engine_orphans_py_13["plugin/scripts/reqmap_engine/orphans.py:13"]
  ARCH_TRACKED_042 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_13
  f_plugin_scripts_reqmap_engine_rules_py_389["plugin/scripts/reqmap_engine/rules.py:389"]
  ARCH_TRACKED_042 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_389
  ARCH_TRANSLATE_044["Reading a cached requirement translation into the map<br><small>ARCH-TRANSLATE-044</small>"]
  f_app_src_lib_i18n_jsx_2["app/src/lib/i18n.jsx:2"]
  ARCH_TRANSLATE_044 -->|implements| f_app_src_lib_i18n_jsx_2
  f_app_src_views_SpecDoc_jsx_6["app/src/views/SpecDoc.jsx:6"]
  ARCH_TRANSLATE_044 -->|implements| f_app_src_views_SpecDoc_jsx_6
  f_plugin_scripts_test_reqmap_author_py_1013_3226["plugin/scripts/test_reqmap_author.py:1013-3226"]
  ARCH_TRANSLATE_044 -->|tested-by| f_plugin_scripts_test_reqmap_author_py_1013_3226
  f_plugin_scripts_reqmap_engine_i18n_py_11_158["plugin/scripts/reqmap_engine/i18n.py:11-158"]
  ARCH_TRANSLATE_044 -->|implements| f_plugin_scripts_reqmap_engine_i18n_py_11_158
  f_plugin_scripts_reqmap_engine_rules_py_287["plugin/scripts/reqmap_engine/rules.py:287"]
  ARCH_TRANSLATE_044 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_287
  ARCH_UNREADABLE_070["Source files the scan cannot decode<br><small>ARCH-UNREADABLE-070</small>"]
  f_plugin_scripts_test_reqmap_scan_py_1631_1710["plugin/scripts/test_reqmap_scan.py:1631-1710"]
  ARCH_UNREADABLE_070 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_1631_1710
  f_plugin_scripts_reqmap_engine_orphans_py_193["plugin/scripts/reqmap_engine/orphans.py:193"]
  ARCH_UNREADABLE_070 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_193
  f_plugin_scripts_reqmap_engine_rules_py_413["plugin/scripts/reqmap_engine/rules.py:413"]
  ARCH_UNREADABLE_070 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_413
  f_plugin_scripts_reqmap_engine_scan_py_144_170["plugin/scripts/reqmap_engine/scan.py:144-170"]
  ARCH_UNREADABLE_070 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_144_170
  ARCH_UNSCANNEDTAG_045["Tags in unscanned file types reported<br><small>ARCH-UNSCANNEDTAG-045</small>"]
  f_plugin_scripts_test_reqmap_scan_py_946["plugin/scripts/test_reqmap_scan.py:946"]
  ARCH_UNSCANNEDTAG_045 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_946
  f_plugin_scripts_reqmap_engine_orphans_py_52["plugin/scripts/reqmap_engine/orphans.py:52"]
  ARCH_UNSCANNEDTAG_045 -->|implements| f_plugin_scripts_reqmap_engine_orphans_py_52
  f_plugin_scripts_reqmap_engine_rules_py_401["plugin/scripts/reqmap_engine/rules.py:401"]
  ARCH_UNSCANNEDTAG_045 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_401
  ARCH_VIEWER_007["Self-contained HTML map viewer<br><small>ARCH-VIEWER-007</small>"]
  f_app_vite_viewer_config_js_1["app/vite.viewer.config.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_vite_viewer_config_js_1
  f_app_scripts_run_ssr_smoke_mjs_1["app/scripts/run-ssr-smoke.mjs:1"]
  ARCH_VIEWER_007 -->|implements| f_app_scripts_run_ssr_smoke_mjs_1
  f_app_scripts_ssr_smoke_jsx_1["app/scripts/ssr-smoke.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_scripts_ssr_smoke_jsx_1
  f_app_scripts_sync_data_mjs_1["app/scripts/sync-data.mjs:1"]
  ARCH_VIEWER_007 -->|implements| f_app_scripts_sync_data_mjs_1
  f_app_scripts_smoke_harness_jsx_1["app/scripts/smoke/harness.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_scripts_smoke_harness_jsx_1
  f_app_scripts_smoke_views_jsx_2["app/scripts/smoke/views.jsx:2"]
  ARCH_VIEWER_007 -->|tested-by| f_app_scripts_smoke_views_jsx_2
  f_app_src_App_jsx_1["app/src/App.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_App_jsx_1
  f_app_src_main_jsx_1["app/src/main.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_main_jsx_1
  f_app_src_components_Rail_jsx_1["app/src/components/Rail.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_components_Rail_jsx_1
  f_app_src_components_TopBar_jsx_1["app/src/components/TopBar.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_components_TopBar_jsx_1
  f_app_src_lib_canvasZoom_jsx_1["app/src/lib/canvasZoom.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_canvasZoom_jsx_1
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
  f_app_src_lib_planBars_js_1["app/src/lib/planBars.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_planBars_js_1
  f_app_src_lib_timeline_js_1["app/src/lib/timeline.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_lib_timeline_js_1
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
  f_app_src_views_SpecDoc_jsx_1["app/src/views/SpecDoc.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_SpecDoc_jsx_1
  f_app_src_views_commands_CommandGroup_jsx_1["app/src/views/commands/CommandGroup.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_commands_CommandGroup_jsx_1
  f_app_src_views_explorer_ExplorerFilters_jsx_1["app/src/views/explorer/ExplorerFilters.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_explorer_ExplorerFilters_jsx_1
  f_app_src_views_map_MapParts_jsx_1["app/src/views/map/MapParts.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_map_MapParts_jsx_1
  f_app_src_views_problems_ProblemsPanels_jsx_1["app/src/views/problems/ProblemsPanels.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_problems_ProblemsPanels_jsx_1
  f_app_src_views_roadmap_GanttLanes_jsx_1["app/src/views/roadmap/GanttLanes.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_roadmap_GanttLanes_jsx_1
  f_app_src_views_roadmap_GanttRuler_jsx_1["app/src/views/roadmap/GanttRuler.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_roadmap_GanttRuler_jsx_1
  f_app_src_views_roadmap_PlanGantt_jsx_1["app/src/views/roadmap/PlanGantt.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_roadmap_PlanGantt_jsx_1
  f_app_src_views_roadmap_PlanNotes_jsx_1["app/src/views/roadmap/PlanNotes.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_roadmap_PlanNotes_jsx_1
  f_app_src_views_roadmap_VersionsTable_jsx_1["app/src/views/roadmap/VersionsTable.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_roadmap_VersionsTable_jsx_1
  f_app_src_views_roadmap_ganttLayout_js_1["app/src/views/roadmap/ganttLayout.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_roadmap_ganttLayout_js_1
  f_app_src_views_roadmap_versionsData_js_1["app/src/views/roadmap/versionsData.js:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_roadmap_versionsData_js_1
  f_app_src_views_spec_SpecParts_jsx_1["app/src/views/spec/SpecParts.jsx:1"]
  ARCH_VIEWER_007 -->|implements| f_app_src_views_spec_SpecParts_jsx_1
  f_plugin_scripts_test_reqmap_report_py_430_4398["plugin/scripts/test_reqmap_report.py:430-4398"]
  ARCH_VIEWER_007 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_430_4398
  f_plugin_scripts_reqmap_engine_rules_py_270["plugin/scripts/reqmap_engine/rules.py:270"]
  ARCH_VIEWER_007 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_270
  f_plugin_scripts_reqmap_engine_viewer_py_33_89["plugin/scripts/reqmap_engine/viewer.py:33-89"]
  ARCH_VIEWER_007 -->|implements| f_plugin_scripts_reqmap_engine_viewer_py_33_89
  ARCH_VLEVEL_037["Verification levels<br><small>ARCH-VLEVEL-037</small>"]
  f_plugin_scripts_test_reqmap_gate_py_171_227["plugin/scripts/test_reqmap_gate.py:171-227"]
  ARCH_VLEVEL_037 -->|tested-by| f_plugin_scripts_test_reqmap_gate_py_171_227
  f_plugin_scripts_test_reqmap_report_py_1138_1147["plugin/scripts/test_reqmap_report.py:1138-1147"]
  ARCH_VLEVEL_037 -->|tested-by| f_plugin_scripts_test_reqmap_report_py_1138_1147
  f_plugin_scripts_test_reqmap_scan_py_251_313["plugin/scripts/test_reqmap_scan.py:251-313"]
  ARCH_VLEVEL_037 -->|tested-by| f_plugin_scripts_test_reqmap_scan_py_251_313
  f_plugin_scripts_reqmap_engine_rules_py_123_136["plugin/scripts/reqmap_engine/rules.py:123-136"]
  ARCH_VLEVEL_037 -->|implements| f_plugin_scripts_reqmap_engine_rules_py_123_136
  f_plugin_scripts_reqmap_engine_scan_py_304["plugin/scripts/reqmap_engine/scan.py:304"]
  ARCH_VLEVEL_037 -->|implements| f_plugin_scripts_reqmap_engine_scan_py_304
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
  a_ARCH["ARCH<br><small>65 caps</small>"]
  a_REQ["REQ<br><small>207 caps</small>"]
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
