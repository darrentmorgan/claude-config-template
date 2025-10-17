# Code Graph Indexer - Deployment Guide

**Version**: 0.1.0 (MVP)
**Status**: Production-Ready for Basic Use
**Date**: 2025-10-16

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Usage Examples](#usage-examples)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Upgrading](#upgrading)
8. [Uninstallation](#uninstallation)

---

## Prerequisites

### System Requirements

- **OS**: macOS 10.15+, Linux (Ubuntu 20.04+), Windows 10+ (WSL2 recommended)
- **Python**: 3.11 or higher
- **Memory**: 8GB RAM minimum (16GB recommended for large repositories)
- **Disk**: 100MB for application + 1-5% of repository size for index

### Required Software

- Python 3.11+ with pip
- Poetry 1.5+ (recommended) or pip
- Git (for version control)

### Optional Dependencies

- Docker (for containerized deployment)
- Memgraph (for production persistence - currently not required for MVP)

---

## Installation Methods

### Method 1: Poetry (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/your-org/claude-config-template.git
cd claude-config-template

# Install dependencies
poetry install

# Verify installation
poetry run code-graph --version
```

### Method 2: Pip (System-wide Installation)

```bash
# Install from source
pip install git+https://github.com/your-org/claude-config-template.git

# Or install from local checkout
git clone https://github.com/your-org/claude-config-template.git
cd claude-config-template
pip install -e .

# Verify installation
code-graph --version
```

### Method 3: Docker (Containerized)

**Note**: Docker support is planned but not yet implemented in MVP.

---

## Configuration

### Default Configuration

The MVP runs with sensible defaults and requires no configuration for basic use.

**Default behavior**:
- In-memory graph storage
- Python file indexing only
- No persistence between CLI invocations
- Basic keyword-based scoring

### Future Configuration (Post-MVP)

Configuration file location: `.code-graph/config.yaml`

```yaml
# Future configuration structure
indexer:
  languages: [python, typescript, go, java]
  exclude_patterns:
    - "**/*.test.py"
    - "**/node_modules/**"
    - "**/.venv/**"

storage:
  type: memgraph  # or: in-memory
  connection: "bolt://localhost:7687"

retrieval:
  max_results: 12
  max_hops: 2
  hybrid_weights:
    semantic: 0.4
    graph: 0.4
    execution: 0.2
```

---

## Verification

### Quick Health Check

```bash
# Via Poetry
poetry run code-graph --help

# Via pip
code-graph --help

# Expected output:
# Usage: code-graph [OPTIONS] COMMAND [ARGS]...
#   Code Graph Indexer - Intelligent context retrieval...
```

### Full Verification Test

```bash
# Create test repository
mkdir -p /tmp/test-repo/src
cat > /tmp/test-repo/src/example.py << 'EOF'
def hello(name: str) -> str:
    """Greet a user."""
    return f"Hello, {name}!"
EOF

# Index test repository
poetry run code-graph index /tmp/test-repo

# Expected output:
# 🔍 Indexing repository: /tmp/test-repo
# 📊 Indexing in progress...
# ✅ Indexing completed successfully!
# 📈 Statistics:
#   Files indexed: 1
#   Functions found: 1
```

### Run Test Suite

```bash
# Run all tests
poetry run pytest tests/ -v

# Run core MVP tests only
poetry run pytest tests/integration/ tests/unit/parsers/ tests/unit/test_graph_builder.py tests/unit/scoring/ -v

# Expected: 77 passed, 4 skipped
```

---

## Usage Examples

### Basic Workflow (Programmatic API)

```python
from code_graph.indexer.main import Indexer
from code_graph.retrieval.query_engine import QueryEngine

# 1. Index repository
indexer = Indexer()
result = indexer.index_repository("/path/to/your/repo")
print(f"Indexed {result.files_indexed} files, {result.functions_found} functions")

# 2. Query for relevant code
engine = QueryEngine(graph=indexer.store)
results = engine.query("add user authentication", top_n=5)

# 3. Process results
for file_ref in results.files:
    print(f"{file_ref.file_path}: {file_ref.relevance_score:.2f}")
    print(f"  Rationale: {file_ref.rationale}")
```

### CLI Usage

```bash
# Index a repository
poetry run code-graph index /path/to/repo

# Query for code (note: requires programmatic API for persistence)
# CLI commands create separate in-memory graphs per invocation
```

### Integration with Claude Code

**Note**: Agent integration is implemented but requires manual setup.

1. Create agent configuration:

```json
{
  "name": "backend-architect",
  "capabilities": ["api-design", "database", "code-graph"],
  "tools": ["code-graph-query"]
}
```

2. Use in delegation workflow:

```python
# In agent delegation system
from code_graph.integration.agent_context import provide_context

context = provide_context(
    query="implement user registration endpoint",
    agent="backend-architect"
)
# Context pack includes relevant files automatically
```

---

## Monitoring & Troubleshooting

### Common Issues

#### Issue: "ModuleNotFoundError: No module named 'tree_sitter'"

**Solution**: Ensure dependencies are installed
```bash
poetry install
# or
pip install tree-sitter tree-sitter-language-pack
```

#### Issue: "No index found" when running CLI query command

**Cause**: MVP doesn't persist index between CLI invocations

**Solution**: Use programmatic API (see examples above) or wait for post-MVP Memgraph integration

#### Issue: Slow indexing for large repositories

**Temporary workaround**: Index smaller directories incrementally
```bash
poetry run code-graph index /path/to/repo/src/module1
```

**Future**: Post-MVP will add parallel processing and optimization

### Logging

**Current**: Basic console output only

**Future**: Structured logging with correlation IDs
```bash
# Future logging configuration
export CODE_GRAPH_LOG_LEVEL=DEBUG
export CODE_GRAPH_LOG_FILE=/var/log/code-graph.log
```

### Performance Monitoring

```bash
# Benchmark indexing performance
poetry run pytest tests/unit/scoring/test_hybrid_scorer.py -v --benchmark-only

# Check test coverage
poetry run pytest --cov=src/code_graph --cov-report=html
open htmlcov/index.html
```

---

## Upgrading

### From Source

```bash
cd claude-config-template
git pull origin main
poetry install
poetry run pytest tests/integration/ -v  # Verify upgrade
```

### From Pip

```bash
pip install --upgrade code-graph-indexer
```

### Breaking Changes

**Current version (0.1.0)**: No breaking changes - initial MVP release

**Future versions**: See CHANGELOG.md for migration guides

---

## Uninstallation

### Poetry Installation

```bash
# Remove from project
poetry remove code-graph-indexer

# Or remove entire environment
rm -rf $(poetry env info --path)
```

### Pip Installation

```bash
pip uninstall code-graph-indexer
```

### Clean Data

```bash
# Remove any cached data (future - currently no persistence)
rm -rf ~/.code-graph/
```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] Run full test suite (`poetry run pytest tests/`)
- [ ] Verify Python 3.11+ installed
- [ ] Review `docs/MVP_QUICKSTART.md` for current limitations
- [ ] Test on sample repository representative of production use

### Deployment

- [ ] Install via preferred method (Poetry or pip)
- [ ] Verify installation (`code-graph --version`)
- [ ] Run health check test
- [ ] Document any environment-specific configuration

### Post-Deployment

- [ ] Monitor initial indexing performance
- [ ] Collect user feedback on retrieval accuracy
- [ ] Plan post-MVP features based on usage patterns

### Known Limitations (MVP)

1. **No persistence**: Index recreated per CLI invocation (use programmatic API)
2. **Python only**: Only parses Python files (parsers for TS/Go/Java exist but not integrated)
3. **Basic scoring**: Simple keyword matching (full hybrid scoring in progress)
4. **No incremental updates**: Must re-index entire repository on changes
5. **In-memory only**: Graph doesn't persist between sessions

See `docs/MVP_STATUS.md` for full feature roadmap.

---

## Support & Resources

- **Documentation**: `docs/MVP_QUICKSTART.md`
- **Issues**: GitHub Issues
- **Architecture**: `specs/002-repository-code-graph/`
- **API Reference**: Coming in post-MVP

---

## Security Considerations

### Current Security Posture (MVP)

- ✅ No network dependencies (offline operation)
- ✅ No external API calls
- ✅ Local file system access only
- ⚠️ No input validation on file paths (trusted environment assumed)
- ⚠️ No authentication/authorization (local CLI tool)

### Future Security Enhancements

- Input validation and sanitization
- Rate limiting for API endpoints (if exposed as service)
- Audit logging for sensitive operations
- Encryption at rest for index storage

---

## License & Credits

**License**: (Your license here)
**Version**: 0.1.0 (MVP)
**Built with**: Python 3.11+, tree-sitter, Click, Pydantic
**Maintained by**: (Your team)

---

**Last Updated**: 2025-10-16
**Document Version**: 1.0
