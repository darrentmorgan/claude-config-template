# Tasks: Intelligent Code Graph and Context Retrieval System

**Input**: Design documents from `/specs/002-repository-code-graph/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: ✅ TDD REQUIRED - Tests MUST be written FIRST per Constitution (Principle III)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions
- **Single project structure**: `src/code_graph/`, `tests/` at repository root
- Per plan.md: Python 3.11+ project with modular organization

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] **T001** Create project structure per plan.md (src/code_graph/, tests/, docs/)
- [ ] **T002** Initialize Python project with poetry (pyproject.toml, dependencies from research.md)
- [ ] **T003** [P] Configure linting (ruff/flake8) and formatting (black) tools
- [ ] **T004** [P] Configure type checking with mypy
- [ ] **T005** [P] Setup pre-commit hooks for quality gates
- [ ] **T006** [P] Create CI/CD pipeline configuration (.github/workflows/ or equivalent)
- [ ] **T007** [P] Initialize git repository and .gitignore for Python

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Memgraph Setup
- [ ] **T008** Write installation documentation for Memgraph (Docker + native) in docs/setup.md
- [ ] **T009** Create Memgraph connection module in src/code_graph/storage/connection.py
- [ ] **T010** Implement WAL configuration in src/code_graph/storage/wal_config.py

### Graph Schema (from data-model.md)
- [ ] **T011** Define graph schema (nodes, edges, indexes) in src/code_graph/storage/schema.py
- [ ] **T012** Implement schema migration framework in src/code_graph/storage/migrations.py
- [ ] **T013** [P] Create Pydantic models for FileNode in src/code_graph/models/nodes/file_node.py
- [ ] **T014** [P] Create Pydantic models for ModuleNode in src/code_graph/models/nodes/module_node.py
- [ ] **T015** [P] Create Pydantic models for ClassNode in src/code_graph/models/nodes/class_node.py
- [ ] **T016** [P] Create Pydantic models for FunctionNode in src/code_graph/models/nodes/function_node.py
- [ ] **T017** [P] Create Pydantic models for TestNode in src/code_graph/models/nodes/test_node.py
- [ ] **T018** [P] Create Pydantic models for edge types (Contains, Imports, Calls, etc.) in src/code_graph/models/edges/
- [ ] **T019** [P] Create Pydantic model for ContextPack in src/code_graph/models/context_pack.py
- [ ] **T020** [P] Create Pydantic model for IndexSnapshot in src/code_graph/models/snapshot.py
- [ ] **T021** [P] Create Pydantic model for WALEntry in src/code_graph/models/wal_entry.py

### Base Parser Infrastructure
- [ ] **T022** Create base parser interface in src/code_graph/indexer/parsers/base.py
- [ ] **T023** Implement tree-sitter initialization and grammar loading in src/code_graph/indexer/tree_sitter_setup.py
- [ ] **T024** Create error-tolerant parsing utilities in src/code_graph/indexer/error_tolerant.py

### Configuration & Utilities
- [ ] **T025** Implement configuration management (.code-graph/config.yaml) in src/code_graph/config/loader.py
- [ ] **T026** [P] Create logging infrastructure with correlation IDs in src/code_graph/utils/logging.py
- [ ] **T027** [P] Create confidence scoring utilities in src/code_graph/utils/confidence.py
- [ ] **T028** [P] Create validation utilities in src/code_graph/utils/validation.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Find Relevant Code for Tasks Automatically (Priority: P1) 🎯 MVP

**Goal**: Automatically identify and retrieve all relevant code files and their dependencies when describing a task, so agents have the right context without manual file specification

**Independent Test**: Submit various natural-language tasks ("Add authentication", "Fix the payment bug") and verify retrieved files include all relevant code, tests, and interfaces without manual specification

### Tests for User Story 1 (TDD Required)

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] **T029** [P] [US1] Unit test for Python parser in tests/unit/parsers/test_python_parser.py
- [ ] **T030** [P] [US1] Unit test for TypeScript parser in tests/unit/parsers/test_typescript_parser.py
- [ ] **T031** [P] [US1] Unit test for graph builder in tests/unit/test_graph_builder.py
- [ ] **T032** [P] [US1] Unit test for relationship extractor in tests/unit/test_relationship_extractor.py
- [ ] **T033** [P] [US1] Unit test for hybrid scorer in tests/unit/scoring/test_hybrid_scorer.py
- [ ] **T034** [P] [US1] Unit test for semantic embeddings in tests/unit/scoring/test_embeddings.py
- [ ] **T035** [P] [US1] Unit test for graph distance calculation in tests/unit/scoring/test_graph_distance.py
- [ ] **T036** [P] [US1] Integration test for full indexing workflow in tests/integration/indexing/test_full_index.py
- [ ] **T037** [P] [US1] Integration test for query workflow ("add email validation to user registration") in tests/integration/retrieval/test_query_email_validation.py
- [ ] **T038** [P] [US1] Integration test for query workflow ("fix the checkout timeout issue") in tests/integration/retrieval/test_query_checkout_timeout.py
- [ ] **T039** [P] [US1] Integration test for context pack generation in tests/integration/retrieval/test_context_pack.py

### T039.5 [GATE] Verify parser tests RED phase
**CONSTITUTION CHECKPOINT**: Verify TDD RED phase before proceeding

Run all parser tests and confirm they FAIL:
```bash
pytest tests/unit/parsers/ tests/unit/test_graph_builder.py tests/unit/test_relationship_extractor.py tests/unit/scoring/ tests/integration/ -v
```

**Acceptance**:
- All tests in T029-T039 execute and FAIL
- Failure messages indicate missing implementations
- Document failure output in commit message or PR description

**Dependencies**: T029-T039
**Unlocks**: T040-T062

---

### Implementation for User Story 1

#### Language-Specific Parsers
- [X] **T040** [P] [US1] Implement Python parser (tree-sitter-python) in src/code_graph/indexer/parsers/python_parser.py
- [X] **T041** [P] [US1] Implement TypeScript parser (tree-sitter-typescript) in src/code_graph/indexer/parsers/typescript_parser.py
- [X] **T042** [P] [US1] Implement Go parser (tree-sitter-go) in src/code_graph/indexer/parsers/go_parser.py
- [ ] **T043** [P] [US1] Implement Java parser (tree-sitter-java) in src/code_graph/indexer/parsers/java.py

#### Graph Building
- [ ] **T044** [US1] Implement graph builder (AST → graph nodes) in src/code_graph/indexer/graph_builder.py (depends on T040-T043)
- [ ] **T045** [US1] Implement relationship extractor (imports, calls, inheritance) in src/code_graph/indexer/relationship_extractor.py (depends on T044)

#### Storage Operations
- [ ] **T046** [US1] Implement graph CRUD operations in src/code_graph/storage/graph_store.py (depends on T011-T021)
- [ ] **T047** [US1] Implement WAL write operations in src/code_graph/storage/wal.py (depends on T010)
- [ ] **T048** [US1] Implement snapshot creation in src/code_graph/storage/snapshot.py (depends on T046)

#### Semantic Embeddings
- [ ] **T049** [P] [US1] Implement Nomic Embed Code integration in src/code_graph/retrieval/embeddings.py
- [ ] **T050** [US1] Implement embedding cache (LRU) in src/code_graph/retrieval/embedding_cache.py (depends on T049)

#### Hybrid Scoring
- [ ] **T051** [P] [US1] Implement graph distance calculation (BFS, shortest path) in src/code_graph/retrieval/graph_distance.py
- [ ] **T052** [P] [US1] Implement execution signals parser (logs, traces) in src/code_graph/retrieval/execution_signals.py
- [ ] **T053** [US1] Implement hybrid scorer (0.4·semantic + 0.4·graph + 0.2·execution) in src/code_graph/retrieval/hybrid_scorer.py (depends on T049, T051, T052)

#### Context Assembly
- [ ] **T054** [US1] Implement context pack builder (files + rationales + scores) in src/code_graph/retrieval/context_pack.py (depends on T053)

#### Full Indexing Workflow
- [ ] **T055** [US1] Implement main indexer orchestrator in src/code_graph/indexer/main.py (depends on T044, T045, T046, T047)

#### Query Interface
- [ ] **T056** [US1] Implement query engine (natural language → context pack) in src/code_graph/retrieval/query_engine.py (depends on T054)

#### Agent Integration (FR-013 Core Requirement)

- [ ] **T056.5** [US1] Write agent integration test
**BLOCKING DEPENDENCY**: MUST write test BEFORE T056.7 implementation (TDD RED FIRST)

Create automated test verifying context pack delivery to agent delegation system:
- `tests/integration/test_agent_integration.py`
  - Test context pack JSON serialization
  - Test automatic invocation on agent query
  - Test context pack contains top-N code snippets
  - Test hybrid score ordering
  - Test graceful fallback when graph unavailable

**Acceptance**:
- Test written and FAILS (RED phase verified)
- Covers FR-013 automated delivery requirement
- No implementation code written yet

**Dependencies**: T052 (hybrid ranking), T056 (query interface)
**Unlocks**: T056.7 (implementation)

---

- [ ] **T056.7** [US1] Implement agent context provider integration in src/code_graph/integration/agent_context.py (depends on T056.5)

#### CLI Commands
- [ ] **T057** [US1] Implement CLI "index" command in src/code_graph/cli/commands/index_cmd.py (depends on T055)
- [ ] **T058** [US1] Implement CLI "query" command in src/code_graph/cli/commands/query_cmd.py (depends on T056)
- [ ] **T059** [US1] Implement CLI "status" command in src/code_graph/cli/commands/status_cmd.py (depends on T046)

#### Error Handling & Logging
- [ ] **T060** [US1] Add comprehensive error handling to indexer pipeline
- [ ] **T061** [US1] Add structured logging with correlation IDs to retrieval pipeline
- [ ] **T062** [US1] Implement progress reporting for indexing operations

**Checkpoint**: At this point, User Story 1 should be fully functional - can index repositories and query for relevant code with hybrid scoring

---

## Phase 4: User Story 2 - Work with Imperfect Codebases (Priority: P1)

**Goal**: Handle syntax errors, incomplete code, and broken dependencies gracefully so assistance works even when codebase isn't perfect

**Independent Test**: Intentionally introduce syntax errors, remove imports, break references, then verify system still indexes most of codebase and retrieves relevant context with confidence indicators

### Tests for User Story 2 (TDD Required)

- [ ] **T063** [P] [US2] Unit test for error recovery in tree-sitter parsing in tests/unit/parsers/test_error_recovery.py
- [ ] **T064** [P] [US2] Unit test for partial structure extraction in tests/unit/test_partial_parsing.py
- [ ] **T065** [P] [US2] Unit test for confidence scoring rules in tests/unit/test_confidence_scoring.py
- [ ] **T066** [P] [US2] Integration test for indexing repo with 20% parse errors in tests/integration/indexing/test_error_tolerance.py
- [ ] **T067** [P] [US2] Integration test for unresolved import handling in tests/integration/indexing/test_unresolved_imports.py
- [ ] **T068** [P] [US2] Integration test for query with broken code in tests/integration/retrieval/test_query_broken_code.py

### T068.5 [GATE] Verify error tolerance tests RED phase
**CONSTITUTION CHECKPOINT**: Verify TDD RED phase before proceeding

Run error tolerance tests and confirm they FAIL:
```bash
pytest tests/unit/parsers/test_error_recovery.py tests/unit/test_partial_parsing.py tests/unit/test_confidence_scoring.py tests/integration/indexing/test_error_tolerance.py tests/integration/indexing/test_unresolved_imports.py tests/integration/retrieval/test_query_broken_code.py -v
```

**Acceptance**:
- All tests in T063-T068 execute and FAIL
- Failures show missing error recovery implementations

**Dependencies**: T063-T068
**Unlocks**: T069-T078

---

### Implementation for User Story 2

#### Error-Tolerant Parsing Extensions
- [ ] **T069** [P] [US2] Implement error node detection in tree-sitter AST in src/code_graph/indexer/error_tolerant.py
- [ ] **T070** [US2] Implement partial symbol extraction from broken files in src/code_graph/indexer/partial_extractor.py (depends on T069)
- [ ] **T071** [US2] Implement confidence score calculation based on parse status in src/code_graph/utils/confidence.py (extends T027)

#### Unresolved Relationship Handling
- [ ] **T072** [US2] Implement unresolved import tracking in src/code_graph/indexer/unresolved_tracker.py
- [ ] **T073** [US2] Mark uncertain relationships with low confidence in graph builder (extends T044)
- [ ] **T074** [US2] Implement warnings for confidence ≤ 0.70 in src/code_graph/utils/warnings.py

#### Query Adjustments
- [ ] **T075** [US2] Adjust hybrid scorer to handle low-confidence edges in src/code_graph/retrieval/hybrid_scorer.py (extends T053)
- [ ] **T076** [US2] Add confidence indicators to context pack results (extends T054)

#### Error Reporting
- [ ] **T077** [P] [US2] Implement parse error collection and reporting in src/code_graph/indexer/error_reporter.py
- [ ] **T078** [P] [US2] Add coverage metrics (percentage successfully indexed) to status command (extends T059)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - can index imperfect codebases and retrieve context with confidence warnings

---

## Phase 5: User Story 3 - Maintain Up-to-Date Index Efficiently (Priority: P1)

**Goal**: Automatically update index when files are modified, so context retrieval always reflects current codebase state without manual re-indexing

**Independent Test**: Make changes to various files, observe only modified files are re-indexed (not entire repository), and verify subsequent searches immediately reflect changes

### Tests for User Story 3 (TDD Required)

- [ ] **T079** [P] [US3] Unit test for file watcher in tests/unit/test_file_watcher.py
- [ ] **T080** [P] [US3] Unit test for diff analyzer in tests/unit/test_diff_analyzer.py
- [ ] **T081** [P] [US3] Unit test for graph updater (targeted updates) in tests/unit/test_graph_updater.py
- [ ] **T082** [P] [US3] Integration test for single file update (<2s) in tests/integration/incremental/test_single_file_update.py
- [ ] **T083** [P] [US3] Integration test for multi-file update in tests/integration/incremental/test_multi_file_update.py
- [ ] **T084** [P] [US3] Integration test for new import detection in tests/integration/incremental/test_new_imports.py
- [ ] **T085** [P] [US3] Integration test for function signature change in tests/integration/incremental/test_signature_change.py

### T085.5 [GATE] Verify incremental update tests RED phase
**CONSTITUTION CHECKPOINT**: Verify TDD RED phase before proceeding

Run incremental update tests and confirm they FAIL:
```bash
pytest tests/unit/test_file_watcher.py tests/unit/test_diff_analyzer.py tests/unit/test_graph_updater.py tests/integration/incremental/ -v
```

**Acceptance**:
- All tests in T079-T085 execute and FAIL
- Failures indicate unimplemented incremental update logic

**Dependencies**: T079-T085
**Unlocks**: T086-T096

---

### Implementation for User Story 3

#### File Watching
- [ ] **T086** [US3] Implement file system watcher (watchdog) in src/code_graph/incremental/file_watcher.py
- [ ] **T087** [US3] Implement debounce logic for rapid changes in src/code_graph/incremental/debouncer.py (depends on T086)

#### Diff Analysis
- [ ] **T088** [US3] Implement AST diff analyzer (compare old/new tree-sitter trees) in src/code_graph/incremental/diff_analyzer.py
- [ ] **T089** [US3] Identify changed symbols (functions, classes added/removed/modified) in src/code_graph/incremental/symbol_diff.py (depends on T088)

#### Targeted Graph Updates
- [ ] **T090** [US3] Implement targeted node updates (update only changed nodes) in src/code_graph/incremental/graph_updater.py
- [ ] **T091** [US3] Implement affected edge re-extraction (re-analyze only edges touching changed nodes) in src/code_graph/incremental/edge_updater.py (depends on T090)
- [ ] **T092** [US3] Invalidate cached embeddings for changed code in src/code_graph/retrieval/embedding_cache.py (extends T050)

#### WAL for Incremental Updates
- [ ] **T093** [US3] Log incremental changes to WAL (CREATE_NODE, UPDATE_NODE, DELETE_NODE) in src/code_graph/storage/wal.py (extends T047)

#### CLI Watch Command
- [ ] **T094** [US3] Implement CLI "watch" command in src/code_graph/cli/commands/watch_cmd.py (depends on T086, T090, T091)

#### Performance Optimization
- [ ] **T095** [US3] Add performance logging for update latency (target: <2s)
- [ ] **T096** [US3] Implement async processing for non-blocking updates

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - full indexing, error tolerance, and incremental updates

---

## Phase 6: User Story 4 - Understand Code Relationships and Impact (Priority: P2)

**Goal**: Visualize which code depends on target files and which files they depend on, to understand blast radius of proposed changes

**Independent Test**: Select any file or function, request its relationship map, verify visualization shows both upstream dependencies (what it uses) and downstream dependents (what uses it) with relationship types labeled

### Tests for User Story 4 (TDD Required)

- [ ] **T097** [P] [US4] Unit test for neighbor expansion (N-hop traversal) in tests/unit/test_neighbor_expansion.py
- [ ] **T098** [P] [US4] Unit test for impact map generation in tests/unit/test_impact_map.py
- [ ] **T099** [P] [US4] Integration test for relationship visualization in tests/integration/graph/test_relationship_viz.py
- [ ] **T100** [P] [US4] Integration test for impact analysis (utility function) in tests/integration/graph/test_impact_utility_function.py
- [ ] **T101** [P] [US4] Integration test for impact analysis (data model) in tests/integration/graph/test_impact_data_model.py

### Implementation for User Story 4

#### Graph Traversal
- [ ] **T102** [P] [US4] Implement neighbor expansion (BFS within N hops) in src/code_graph/retrieval/neighbor_expansion.py
- [ ] **T103** [US4] Implement edge type filtering for traversal in src/code_graph/retrieval/edge_filter.py (depends on T102)

#### Impact Analysis
- [ ] **T104** [US4] Implement upstream dependency finder (what this uses) in src/code_graph/retrieval/upstream_finder.py
- [ ] **T105** [US4] Implement downstream dependent finder (what uses this) in src/code_graph/retrieval/downstream_finder.py
- [ ] **T106** [US4] Calculate blast radius (total affected nodes) in src/code_graph/retrieval/blast_radius.py (depends on T104, T105)

#### Visualization Data
- [ ] **T107** [US4] Generate impact map data structure (upstream, downstream, depth) in src/code_graph/retrieval/impact_map.py (depends on T104, T105, T106)
- [ ] **T108** [US4] Format relationship paths for display (tree, list, json formats) in src/code_graph/cli/formatters/relationship_formatter.py

#### CLI Commands
- [ ] **T109** [US4] Implement CLI "neighbors" command in src/code_graph/cli/commands/neighbors_cmd.py (depends on T102, T103)
- [ ] **T110** [US4] Implement CLI "impact" command in src/code_graph/cli/commands/impact_cmd.py (depends on T107, T108)

#### API Endpoints
- [ ] **T111** [P] [US4] Implement GET /graph/neighbors API endpoint (from contracts/indexer-api.yaml)
- [ ] **T112** [P] [US4] Implement GET /graph/impact API endpoint (from contracts/indexer-api.yaml)

**Checkpoint**: At this point, User Stories 1-4 should all work - can explore relationships and analyze change impact

---

## Phase 7: User Story 5 - Validate Changes with Targeted Testing (Priority: P2)

**Goal**: Identify which tests are relevant to changes and run those first before full suite, for fast feedback

**Independent Test**: Modify a specific function, observe which tests system selects (should include direct tests, integration tests touching that code path, tests for dependent code), verify tests actually exercise changed code

### Tests for User Story 5 (TDD Required)

- [ ] **T113** [P] [US5] Unit test for test-to-code mapping in tests/unit/test_test_mapping.py
- [ ] **T114** [P] [US5] Unit test for test selection algorithm in tests/unit/test_test_selection.py
- [ ] **T115** [P] [US5] Integration test for targeted test identification in tests/integration/testing/test_targeted_tests.py
- [ ] **T116** [P] [US5] Integration test for test coverage calculation in tests/integration/testing/test_coverage_calc.py

### Implementation for User Story 5

#### Test Relationship Tracking
- [ ] **T117** [US5] Implement test-to-code mapping during indexing (TESTS edges) in src/code_graph/indexer/test_mapper.py
- [ ] **T118** [US5] Track test coverage relationships (which tests cover which code) in src/code_graph/indexer/coverage_tracker.py (depends on T117)

#### Test Selection
- [ ] **T119** [US5] Implement direct test finder (unit tests for changed code) in src/code_graph/retrieval/test_selector.py
- [ ] **T120** [US5] Implement indirect test finder (integration tests via call graph) in src/code_graph/retrieval/indirect_test_finder.py (depends on T119)
- [ ] **T121** [US5] Calculate coverage percentage for selected tests in src/code_graph/retrieval/coverage_calculator.py (depends on T119, T120)

#### CLI Commands
- [ ] **T122** [US5] Implement CLI "tests" command in src/code_graph/cli/commands/tests_cmd.py (depends on T119, T120, T121)
- [ ] **T123** [US5] Add --format commands option for pytest/jest command generation

#### API Endpoints
- [ ] **T124** [US5] Implement GET /tests/related API endpoint (from contracts/indexer-api.yaml)

**Checkpoint**: All user stories should now be independently functional - full feature set complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation
- [ ] **T125** [P] Write comprehensive API documentation (docstrings) for all public interfaces
- [ ] **T126** [P] Create usage examples for each CLI command in docs/examples/
- [ ] **T127** [P] Write architecture decision records (ADRs) in docs/decisions/
- [ ] **T128** Validate quickstart.md against actual implementation

### Performance Optimization
- [ ] **T129** Benchmark full indexing performance (target: <10min for 10K files)
- [ ] **T130** Benchmark incremental update performance (target: <2s per file)
- [ ] **T131** Benchmark query performance (target: <3s)
- [ ] **T132** Optimize embedding computation (batch processing, GPU acceleration if available)
- [ ] **T133** Profile memory usage for 100K file repositories

### Security & Error Handling
- [ ] **T134** Implement input validation for all CLI arguments
- [ ] **T135** Add security checks for file path traversal attacks
- [ ] **T136** Implement rate limiting for API endpoints (if exposed as service)
- [ ] **T137** Ensure no sensitive data in logs or error messages

### Configuration & Deployment
- [ ] **T138** [P] Create Docker Compose setup (Memgraph + indexer) in docker/docker-compose.yml
- [ ] **T139** [P] Write deployment documentation in docs/deployment.md
- [ ] **T140** [P] Create example configuration files for common setups in examples/configs/

### Integration with Claude Code

- [ ] **T141** [P] Create example agent configuration in examples/agents/backend-architect.json (depends on T056.7)
- [ ] **T142** [P] Create documentation for agent delegation integration in docs/agent-integration.md (depends on T056.7)

### Additional Unit Tests (Property-Based)
- [ ] **T144** [P] Property-based tests for graph invariants (no cycles in CONTAINS, INHERITS) in tests/unit/properties/test_graph_invariants.py
- [ ] **T145** [P] Property-based tests for confidence score rules in tests/unit/properties/test_confidence_properties.py
- [ ] **T146** [P] Property-based tests for hybrid scoring formula in tests/unit/properties/test_hybrid_scoring_properties.py

### Code Quality
- [ ] **T147** Run full linting and fix all issues
- [ ] **T148** Achieve ≥60% test coverage (Constitution requirement)
- [ ] **T149** Remove dead code and unused imports
- [ ] **T150** Refactor for consistency and maintainability

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - **US1, US2, US3 (P1 stories)**: Can proceed in parallel after Foundation (if staffed)
  - **US4, US5 (P2 stories)**: Can proceed in parallel after Foundation (if staffed)
  - Recommended sequential order for single developer: US1 → US2 → US3 → US4 → US5
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - **No dependencies on other stories** - MVP core
- **User Story 2 (P1)**: Can start after Foundational - **Extends US1** (error handling) - Still independently testable
- **User Story 3 (P1)**: Can start after Foundational - **Extends US1** (incremental updates) - Still independently testable
- **User Story 4 (P2)**: Can start after Foundational - **Uses US1 graph traversal** - Still independently testable
- **User Story 5 (P2)**: Can start after Foundational - **Uses US1 relationships** - Still independently testable

### Within Each User Story

**TDD Order (Constitution Principle III)**:
1. **Write tests FIRST** (all tests marked [P] can be written in parallel)
2. **Verify tests FAIL** (red phase)
3. **Implement models** (all models marked [P] can be implemented in parallel)
4. **Implement services** (depend on models)
5. **Implement endpoints/CLI** (depend on services)
6. **Verify tests PASS** (green phase)
7. **Refactor** (if needed)

### Parallel Opportunities

#### Setup Phase (Phase 1)
- T003, T004, T005, T006, T007 can all run in parallel

#### Foundational Phase (Phase 2)
- **Data Models**: T013-T021 (all node/edge Pydantic models) can run in parallel
- **Utilities**: T026, T027, T028 can run in parallel

#### User Story 1 (Phase 3)
- **Tests**: T029-T039 (all tests) can run in parallel
- **Parsers**: T040-T043 (language parsers) can run in parallel
- **Embeddings**: T049 can run parallel with parsers
- **Scoring components**: T051, T052 can run in parallel (independent algorithms)

#### User Story 2 (Phase 4)
- **Tests**: T063-T068 can run in parallel
- **Components**: T069, T077, T078 can run in parallel

#### User Story 3 (Phase 5)
- **Tests**: T079-T085 can run in parallel

#### User Story 4 (Phase 6)
- **Tests**: T097-T101 can run in parallel
- **API Endpoints**: T111, T112 can run in parallel

#### User Story 5 (Phase 7)
- **Tests**: T113-T116 can run in parallel

#### Polish Phase (Phase 8)
- **Documentation**: T125, T126, T127 can run in parallel
- **Deployment**: T138, T139, T140 can run in parallel
- **Property tests**: T144, T145, T146 can run in parallel

---

## Parallel Example: User Story 1 (MVP)

```bash
# Phase 1: Write all tests in parallel (TDD Red Phase)
Task T029: "Unit test for Python parser in tests/unit/parsers/test_python_parser.py"
Task T030: "Unit test for TypeScript parser in tests/unit/parsers/test_typescript_parser.py"
Task T031: "Unit test for graph builder in tests/unit/test_graph_builder.py"
Task T032: "Unit test for relationship extractor in tests/unit/test_relationship_extractor.py"
Task T033: "Unit test for hybrid scorer in tests/unit/scoring/test_hybrid_scorer.py"
# ... (all T029-T039 in parallel)

# Phase 2: Verify tests FAIL, then implement parsers in parallel
Task T040: "Implement Python parser in src/code_graph/indexer/parsers/python.py"
Task T041: "Implement TypeScript parser in src/code_graph/indexer/parsers/typescript.py"
Task T042: "Implement Go parser in src/code_graph/indexer/parsers/go.py"
Task T043: "Implement Java parser in src/code_graph/indexer/parsers/java.py"

# Phase 3: Implement scoring components in parallel
Task T049: "Implement Nomic Embed Code integration in src/code_graph/retrieval/embeddings.py"
Task T051: "Implement graph distance calculation in src/code_graph/retrieval/graph_distance.py"
Task T052: "Implement execution signals parser in src/code_graph/retrieval/execution_signals.py"

# Phase 4: Sequential integration (dependencies)
Task T044: "Implement graph builder" (depends on T040-T043)
Task T045: "Implement relationship extractor" (depends on T044)
Task T046: "Implement graph CRUD operations" (depends on foundation)
Task T053: "Implement hybrid scorer" (depends on T049, T051, T052)
Task T054: "Implement context pack builder" (depends on T053)
# ... continue with integration tasks
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Fastest Path to Value)

**Timeline**: ~2-3 weeks for single developer

1. ✅ Complete **Phase 1: Setup** (T001-T007) - 1 day
2. ✅ Complete **Phase 2: Foundational** (T008-T028) - 3-4 days
   - **CRITICAL**: Must complete before US1
   - Memgraph setup, graph schema, base models, parser infrastructure
3. ✅ Complete **Phase 3: User Story 1** (T029-T062) - 7-10 days
   - TDD: Write tests first (T029-T039), verify failures
   - Implement parsers, graph building, embeddings, hybrid scoring
   - Build indexing and query workflows
   - Implement basic CLI (index, query, status commands)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Can index a repository?
   - Can query for relevant code?
   - Do results include rationales and confidence scores?
5. **Deploy/demo MVP** - Basic but functional code graph system

**MVP Deliverables**:
- Index repositories with multiple languages (Python, TypeScript, Go, Java)
- Query for relevant code using natural language
- Get context packs with hybrid scoring and rationales
- Basic CLI (index, query, status)
- Functional but without error tolerance, incremental updates, or advanced features

### Incremental Delivery (Add Features Incrementally)

**Timeline**: ~6-8 weeks for single developer (full feature set)

1. ✅ Complete Setup + Foundational → Foundation ready (1 week)
2. ✅ Add **User Story 1** (indexing + query) → Test independently → Deploy/Demo (2 weeks) - **MVP!**
3. ✅ Add **User Story 2** (error tolerance) → Test independently → Deploy/Demo (1 week)
   - Now handles imperfect codebases with confidence scoring
4. ✅ Add **User Story 3** (incremental updates) → Test independently → Deploy/Demo (1 week)
   - Now watches files and updates graph automatically
5. ✅ Add **User Story 4** (relationship visualization) → Test independently → Deploy/Demo (1 week)
   - Now shows impact maps and neighbor relationships
6. ✅ Add **User Story 5** (targeted testing) → Test independently → Deploy/Demo (1 week)
   - Now identifies relevant tests for changes
7. ✅ Add **Polish** → Final testing → Production deploy (1 week)

**Each increment**:
- Adds measurable value
- Is independently testable
- Doesn't break previous features
- Can be deployed/demoed

### Parallel Team Strategy (If Multiple Developers Available)

**Timeline**: ~3-4 weeks with 3 developers (full feature set)

**Week 1**:
- **All developers**: Complete Setup + Foundational together
- **Checkpoint**: Foundation validated, ready for parallel work

**Week 2-3**:
- **Developer A**: User Story 1 (indexing + query - MVP core)
- **Developer B**: User Story 2 (error tolerance) + User Story 3 (incremental)
- **Developer C**: User Story 4 (relationships) + User Story 5 (testing)

**Week 4**:
- **All developers**: Integration testing, polish, documentation
- **Checkpoint**: Full feature set complete

**Benefits**:
- 50% faster time to full feature set
- Stories complete independently and integrate cleanly
- Can still demo MVP (US1) after 2 weeks

---

## Notes

### TDD Discipline (Constitution Principle III - NON-NEGOTIABLE)

**Red-Green-Refactor Cycle**:
1. **Red**: Write failing test FIRST
   - Test describes desired behavior
   - Test MUST fail initially (proves it tests the right thing)
   - Run test, verify failure

2. **Green**: Implement minimal code to pass test
   - Write just enough code to make test pass
   - Don't over-engineer
   - Run test, verify success

3. **Refactor**: Clean up code while keeping tests green
   - Improve design, remove duplication
   - Tests provide safety net
   - Re-run tests to ensure they still pass

**Test Coverage Target**: ≥60% for changed code areas (Constitution requirement)

### Task Execution Rules

- **[P] tasks** = different files, no dependencies → can run in parallel
- **[Story] label** maps task to specific user story for traceability (US1, US2, US3, US4, US5)
- Each user story should be **independently completable and testable**
- **Always write tests FIRST** (verify failures before implementation)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

### File Path Conventions

All paths relative to repository root:
- **Source**: `src/code_graph/` (Python package naming: underscores, per PEP 8)
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- **Docs**: `docs/`
- **Examples**: `examples/`
- **Config**: `.code-graph/config.yaml`

### Performance Validation

After completing each phase, validate against spec targets:
- **Full indexing**: <10 minutes for 10K files (validate after T055, T062)
- **Incremental updates**: <2 seconds per file (validate after T094, T096)
- **Query responses**: <3 seconds (validate after T056, T058)
- **Coverage**: ≥60% test coverage (validate after T148)

### Constitution Compliance Checkpoints

- **After Phase 2**: Verify foundation supports delegation (agents can use graph for context)
- **After each User Story**: Verify TDD followed (tests written first, coverage ≥60%)
- **After Phase 8**: Verify all quality gates pass (linting, type checking, tests, coverage)

---

## Summary

**Total Tasks**: 150 tasks
**Task Breakdown by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 21 tasks - **BLOCKS ALL USER STORIES**
- Phase 3 (US1 - P1): 34 tasks - **MVP CORE**
- Phase 4 (US2 - P1): 16 tasks
- Phase 5 (US3 - P1): 18 tasks
- Phase 6 (US4 - P2): 16 tasks
- Phase 7 (US5 - P2): 12 tasks
- Phase 8 (Polish): 26 tasks

**MVP Scope** (Fastest path to value):
- Phase 1 + Phase 2 + Phase 3 (User Story 1 only)
- **62 tasks total** for MVP
- Delivers: Core indexing and query functionality with hybrid scoring

**P1 Features** (High priority - all three should be complete for production):
- User Stories 1, 2, 3
- **96 tasks total** for all P1 features
- Delivers: Indexing, error tolerance, incremental updates

**Full Feature Set**:
- All 5 user stories + polish
- **150 tasks total**
- Delivers: Complete code graph system with all capabilities

**Parallel Opportunities**: 45+ tasks marked [P] for parallel execution across different files

**Independent Test Criteria**: Each user story (US1-US5) has clear acceptance tests and can be validated independently

**Recommended Start**: Begin with MVP (US1 only) → validate → incrementally add US2, US3, US4, US5

---

**Next Step**: Begin with Phase 1 (Setup) tasks T001-T007
