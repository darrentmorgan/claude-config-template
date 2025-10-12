# Implementation Plan: Intelligent Code Graph and Context Retrieval System

**Branch**: `002-repository-code-graph` | **Date**: 2025-10-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-repository-code-graph/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a repository code graph indexing and retrieval system that automatically identifies relevant code for multi-agent workflows. The system indexes code structure (files, modules, classes, functions, tests) and relationships (imports, calls, inheritance, data access, test coverage), handles syntax errors gracefully with confidence scoring, supports incremental updates via file save hooks, and retrieves context using hybrid scoring (0.4·semantic + 0.4·graph + 0.2·execution signals). Persists state using Write-Ahead Logging (WAL) and integrates with existing agent delegation for automatic and manual context provision.

## Technical Context

**Language/Version**: Python 3.11+ (chosen for complete ecosystem: tree-sitter bindings, Memgraph driver, sentence-transformers, asyncio)
**Primary Dependencies**:
- tree-sitter 0.20+ (error-tolerant parsing)
- Memgraph 2.x (graph storage with WAL)
- sentence-transformers 2.2+ (Nomic Embed Code embeddings)
- watchdog 3.0+ (file watching)
- gqlalchemy 1.4+ (Memgraph Python driver)
- click/typer (CLI framework)

**Storage**: Memgraph (in-memory graph database) + WAL log files + periodic snapshots. Sub-millisecond queries, 32K+ QPS, built-in durability.
**Testing**: pytest + pytest-asyncio (async tests), pytest-cov (≥60% coverage), hypothesis (property-based), pytest-benchmark (performance)
**Target Platform**: Cross-platform CLI tool / Library (macOS, Linux, Windows) - integrates with editors via file save hooks
**Project Type**: Single library/CLI tool with plugin architecture for language parsers
**Performance Goals**:
- Full indexing: <10 minutes for 10K files (tree-sitter incremental parsing)
- Incremental updates: <2 seconds per file save (watchdog + targeted graph updates)
- Search queries: <3 seconds with result ranking (Memgraph in-memory)
- Embedding computation: lazy + cached (compute on-demand, LRU cache)

**Constraints**:
- Must handle syntax errors gracefully (tree-sitter error recovery + confidence scoring)
- Index size: 1-5% of repository size (Memgraph optimized storage)
- Memory: Recommend 32GB+ RAM for 100K node graphs (in-memory graph)
- No network dependencies for core indexing (Nomic Embed Code runs offline)

**Scale/Scope**:
- Initial: 5K-10K file repositories
- Target: Up to 100K files
- Languages: Python, JavaScript/TypeScript, Go, Java (tree-sitter grammars)
- Relationships: 6 types (containment, imports, calls, inheritance, data access, test coverage)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Delegation-First Architecture ✅ PASS

**Status**: Compliant
**Rationale**: This feature provides infrastructure for better delegation. The indexer itself can be implemented by specialized agents:
- Parser implementation → delegated to language-specific agents
- Graph operations → delegated to data-engineer
- Integration with existing delegation system → delegated to backend-architect

**Actions**: None required - follow standard delegation protocol during implementation

### II. Quality Automation ✅ PASS

**Status**: Compliant
**Rationale**: Standard quality gates apply:
- Pre-commit hooks will run linting, type-checking, tests
- Post-write hooks trigger code review
- No special exemptions needed

**Actions**: Ensure test coverage ≥60% for indexer, parser, and retrieval modules

### III. Test-Driven Development ⚠️ REQUIRES ATTENTION

**Status**: Compliant with phased approach
**Rationale**: TDD is critical for this feature due to complex graph algorithms and error-tolerant parsing. Must write tests FIRST for:
- Parser error recovery (syntax errors, broken imports)
- Graph relationship extraction
- Hybrid scoring formula validation
- Incremental update correctness
- WAL durability guarantees

**Actions**:
- Phase 0: Define test scenarios for each functional requirement
- Phase 1: Write failing tests for data model operations
- Phase 2: Implement with red-green-refactor cycle strictly enforced

### IV. Agent Specialization ✅ PASS

**Status**: Compliant
**Rationale**: Feature aligns with agent specialization goals:
- Improves context selection for all specialized agents
- Reduces manual file specification burden
- Integrates with existing `.claude/agents/delegation-map.json` routing

**Actions**: Update agent configurations to use code graph for context retrieval once Phase 3 (agent integration) is complete

### V. Documentation & Observability ✅ PASS

**Status**: Compliant
**Rationale**: Feature inherently supports observability:
- Confidence scores explain relationship certainty
- Rationales explain why files were retrieved
- Progress metrics show indexing coverage
- Structured logging for graph operations

**Actions**:
- Document indexer architecture in ADR
- Create API documentation for query interface
- Add structured logging with correlation IDs
- No silent failures in parser error handling

### Overall Status: ✅ PASS WITH ACTIONS

**Gate Decision**: PROCEED to Phase 0 research
**Required Follow-ups**:
1. Emphasize TDD discipline during implementation (write tests first, verify failures)
2. Document architecture decisions for parser choice, graph storage, WAL implementation
3. Ensure structured logging throughout
4. Plan agent integration strategy (Phase 3)

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/code-graph/
├── indexer/
│   ├── parsers/              # Language-specific parsers (tree-sitter wrappers)
│   │   ├── base.py/ts        # Base parser interface
│   │   ├── python.py/ts      # Python parser
│   │   ├── typescript.py/ts  # TypeScript parser
│   │   └── [go, java, etc.]
│   ├── graph_builder.py/ts   # Constructs graph from parsed code
│   ├── relationship_extractor.py/ts  # Identifies edges between nodes
│   └── error_tolerant.py/ts  # Handles syntax errors, partial parsing
│
├── storage/
│   ├── graph_store.py/ts     # Graph persistence (chosen technology)
│   ├── wal.py/ts             # Write-Ahead Log implementation
│   └── snapshot.py/ts        # Point-in-time snapshots
│
├── retrieval/
│   ├── embeddings.py/ts      # Semantic similarity computation
│   ├── graph_distance.py/ts  # Graph proximity calculation
│   ├── execution_signals.py/ts  # Parse logs, traces for signals
│   ├── hybrid_scorer.py/ts   # Combines α·semantic + β·graph + γ·signals
│   └── context_pack.py/ts    # Assembles retrieval results with rationales
│
├── incremental/
│   ├── file_watcher.py/ts    # Monitors file save events
│   ├── diff_analyzer.py/ts   # Identifies changed symbols
│   └── graph_updater.py/ts   # Updates only affected nodes/edges
│
├── integration/
│   ├── agent_context.py/ts   # Provides context to agent delegation system
│   └── manual_query.py/ts    # CLI/API for manual queries
│
├── models/                   # Data models (Node, Edge, ContextPack, etc.)
└── cli/                      # Command-line interface

tests/
├── unit/
│   ├── parsers/              # Test each parser in isolation
│   ├── graph/                # Test graph operations
│   ├── scoring/              # Test hybrid scoring formula
│   └── wal/                  # Test WAL durability
├── integration/
│   ├── indexing/             # Test full indexing workflows
│   ├── incremental/          # Test incremental updates
│   └── retrieval/            # Test end-to-end retrieval accuracy
└── fixtures/
    └── repos/                # Sample codebases with known structure
```

**Structure Decision**: Single project structure (Option 1) with modular organization by feature area. This is a library/CLI tool, not a web application, so a single `src/code-graph/` directory containing all modules is appropriate. Tests mirror the source structure for easy navigation.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

No constitution violations requiring justification. All complexity is inherent to the feature requirements (graph algorithms, error-tolerant parsing, hybrid scoring, WAL persistence).

---

## Phase 0: Research (Complete ✅)

**Status**: Complete
**Output**: `research.md`

All technical decisions resolved:
- **Parser**: Tree-sitter (error-tolerant, multi-language, incremental)
- **Graph Storage**: Memgraph (fast queries, built-in WAL, Cypher support)
- **Embeddings**: Nomic Embed Code (offline, state-of-the-art, code-specific)
- **Language**: Python 3.11+ (complete ecosystem for all components)
- **File Watching**: watchdog + asyncio (cross-platform, non-blocking)

See `research.md` for detailed rationale and alternatives considered.

---

## Phase 1: Design & Contracts (Complete ✅)

**Status**: Complete
**Outputs**:
- `data-model.md` - Complete graph schema with nodes, edges, and supporting entities
- `contracts/indexer-api.yaml` - OpenAPI specification for all endpoints
- `contracts/cli-interface.md` - Complete CLI command reference
- `quickstart.md` - 15-minute setup guide
- `CLAUDE.md` - Updated agent context with Python + Memgraph

### Data Model Summary
- **5 Node Types**: FileNode, ModuleNode, ClassNode, FunctionNode, TestNode
- **6 Edge Types**: CONTAINS, IMPORTS, CALLS, INHERITS, READS_WRITES, TESTS
- **Supporting Entities**: ContextPack, IndexSnapshot, WALEntry
- **Confidence Scoring**: 0.0-1.0 scale with 0.70 warning threshold

### API Contracts Summary
- **9 REST Endpoints**: index, query, neighbors, impact, tests, snapshot, health
- **CLI Commands**: index, query, watch, neighbors, impact, tests, snapshot, status, config
- **Performance Targets**: <10m indexing, <2s incremental, <3s queries

### Constitution Re-Check ✅

**Post-Design Evaluation**: All principles remain satisfied.

1. **Delegation-First**: Design supports delegation (parser → language agents, graph ops → data-engineer)
2. **Quality Automation**: Standard gates apply, ≥60% test coverage required
3. **TDD**: Design emphasizes test-first approach, property-based testing for graph invariants
4. **Agent Specialization**: Improves context selection for all agents
5. **Documentation & Observability**: Confidence scores, rationales, structured logging throughout

**No new violations introduced during design phase.**

---

## Next Steps (Phase 2: Tasks)

Run `/speckit.tasks` to generate dependency-ordered implementation tasks from this plan.

Expected task categories:
1. **Infrastructure Setup**: Memgraph installation, project scaffolding, CI/CD
2. **Core Indexer**: Tree-sitter integration, error-tolerant parsing, graph building
3. **Storage Layer**: Memgraph schema, WAL implementation, snapshots
4. **Retrieval Engine**: Embeddings, hybrid scoring, context packs
5. **Incremental Updates**: File watching, diff analysis, targeted updates
6. **Integration**: Agent delegation hooks, CLI implementation
7. **Testing**: Unit tests, integration tests, performance benchmarks
8. **Documentation**: API docs, user guides, examples

---

**Phase 1 Complete**: Ready for task generation.
