# Development Guide: Code Graph Indexer

## Overview

This document provides guidance for developers working on the code graph indexer implementation.

## Project Status

**Current State**: Prototype/Proof-of-Concept

The project structure and interfaces are complete. Key areas requiring implementation:

### Phase 1: Setup ✅ COMPLETE
- [x] Project structure created
- [x] Poetry configuration with dependencies
- [x] Linting and formatting tools configured
- [x] Pre-commit hooks set up

### Phase 2: Foundational ⚠️ PARTIAL
- [x] Pydantic models defined (FileNode, FunctionNode, Edges, ContextPack)
- [x] Base parser interface created
- [x] Hybrid scorer skeleton with tests
- [ ] Memgraph connection implementation
- [ ] WAL implementation
- [ ] Tree-sitter grammar loading

### Phase 3: User Story 1 (MVP) 🚧 TODO
- [ ] Language-specific parsers (Python, TypeScript, Go, Java)
- [ ] Graph builder implementation
- [ ] Relationship extractor
- [ ] Embedding integration (Nomic Embed Code)
- [ ] Full indexing workflow
- [ ] Query engine
- [ ] CLI commands (full implementation)

### Phase 4-8: Additional Features 📋 PLANNED
- [ ] Error-tolerant parsing (US2)
- [ ] Incremental updates (US3)
- [ ] Relationship visualization (US4)
- [ ] Targeted test selection (US5)
- [ ] Polish and optimization

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry
- Docker (for Memgraph)

### Initial Setup

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Start Memgraph
docker run -d --name memgraph \
  -p 7687:7687 \
  -v memgraph_data:/var/lib/memgraph \
  memgraph/memgraph-platform:latest
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/unit/test_hybrid_scorer.py

# Run integration tests (requires Memgraph)
poetry run pytest tests/integration/
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Lint
poetry run ruff src/ tests/

# Type check
poetry run mypy src/

# Run all pre-commit hooks
poetry run pre-commit run --all-files
```

## Architecture

### Module Organization

```
src/code-graph/
├── indexer/          # Code parsing and graph building
│   ├── parsers/      # Language-specific parsers
│   ├── graph_builder.py
│   └── relationship_extractor.py
├── storage/          # Memgraph and persistence
│   ├── graph_store.py
│   ├── wal.py
│   └── snapshot.py
├── retrieval/        # Query and scoring
│   ├── embeddings.py
│   ├── hybrid_scorer.py
│   └── context_pack.py
├── models/           # Pydantic data models
│   ├── nodes/
│   └── edges/
└── cli/              # Command-line interface
    └── commands/
```

### Key Design Decisions

See `specs/002-repository-code-graph/research.md` for detailed rationale:

- **Tree-sitter**: Error-tolerant parsing with incremental updates
- **Memgraph**: In-memory graph database for fast queries
- **Nomic Embed Code**: Offline code embeddings
- **Hybrid Scoring**: 0.4·semantic + 0.4·graph + 0.2·execution

## Implementation Priorities

### MVP (User Story 1 - 62 tasks)

Focus on core indexing and query functionality:

1. **Memgraph Integration** (T008-T010)
   - Connection management
   - WAL configuration
   - Schema setup

2. **Data Models** (T013-T021)
   - ✅ Already created (Pydantic models)

3. **Parser Implementation** (T040-T043)
   - Start with Python parser (most common)
   - Add TypeScript/JavaScript
   - Add Go and Java

4. **Graph Building** (T044-T046)
   - Convert AST to graph nodes
   - Extract relationships
   - Store in Memgraph

5. **Embeddings** (T049-T050)
   - Integrate Nomic Embed Code
   - Implement caching

6. **Hybrid Scoring** (T051-T054)
   - ✅ Basic structure complete
   - Implement cosine similarity
   - Graph distance calculation
   - Context pack assembly

7. **CLI Implementation** (T057-T059)
   - ✅ Basic structure complete
   - Wire up to actual implementations

### TDD Approach

**CRITICAL**: Follow Test-Driven Development (Constitution Principle III)

For each feature:

1. **RED**: Write failing test first
   ```bash
   # Create test file
   touch tests/unit/test_new_feature.py

   # Write test
   def test_feature():
       # Test the desired behavior
       assert feature() == expected

   # Run test - should FAIL
   poetry run pytest tests/unit/test_new_feature.py
   ```

2. **GREEN**: Implement minimal code to pass
   ```python
   # Implement feature
   def feature():
       return expected

   # Run test - should PASS
   poetry run pytest tests/unit/test_new_feature.py
   ```

3. **REFACTOR**: Clean up while keeping tests green

## Common Tasks

### Adding a New Parser

1. Create parser class in `src/code-graph/indexer/parsers/`
2. Inherit from `BaseParser`
3. Implement abstract methods:
   - `parse_file()`
   - `extract_imports()`
   - `extract_functions()`
   - `extract_classes()`
4. Write tests in `tests/unit/parsers/`
5. Register parser in parser factory

### Adding a New CLI Command

1. Create command file in `src/code-graph/cli/commands/`
2. Define command with `@click.command()`
3. Add options and arguments
4. Register in `src/code-graph/cli/main.py`
5. Test manually: `poetry run code-graph <command>`

### Adding a New Data Model

1. Create Pydantic model in `src/code-graph/models/`
2. Add validation rules with `@field_validator`
3. Include example in `Config.json_schema_extra`
4. Write tests for validation logic
5. Update related models if needed

## Troubleshooting

### Import Errors

If you see import errors like:
```
ModuleNotFoundError: No module named 'code_graph'
```

Ensure you're using Poetry:
```bash
poetry install
poetry run pytest
```

### Memgraph Connection Issues

```bash
# Check if Memgraph is running
docker ps | grep memgraph

# View logs
docker logs memgraph

# Restart
docker restart memgraph
```

### Type Checking Errors

```bash
# Run mypy to see type errors
poetry run mypy src/

# Add type hints to fix
def function(arg: str) -> int:
    return len(arg)
```

## Next Steps

1. Review `specs/002-repository-code-graph/tasks.md` for complete task list
2. Start with MVP tasks (T001-T062)
3. Follow TDD approach for all implementations
4. Commit frequently with clear messages
5. Run tests and linters before committing

## Resources

- **Specification**: `specs/002-repository-code-graph/spec.md`
- **Plan**: `specs/002-repository-code-graph/plan.md`
- **Data Model**: `specs/002-repository-code-graph/data-model.md`
- **API Contracts**: `specs/002-repository-code-graph/contracts/`
- **Tasks**: `specs/002-repository-code-graph/tasks.md`

## Questions?

See:
- Tree-sitter docs: https://tree-sitter.github.io/tree-sitter/
- Memgraph docs: https://memgraph.com/docs
- Pydantic docs: https://docs.pydantic.dev/
- Click docs: https://click.palletsprojects.com/
