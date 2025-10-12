# Setup Guide

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** (the project requires Python 3.11 or higher)
- **Poetry** (for dependency management)
- **Docker** (for running Memgraph - required for full implementation)

### Installing Python 3.11+

macOS (with Homebrew):
```bash
brew install python@3.11
# or
brew install python@3.13
```

Verify installation:
```bash
python3.11 --version
# or
which python3.11 python3.12 python3.13
```

### Installing Poetry

Using pipx (recommended):
```bash
# Install pipx if needed
brew install pipx

# Install Poetry
pipx install poetry
```

Verify installation:
```bash
poetry --version
```

## Initial Setup

### 1. Install Dependencies

From the project root directory:

```bash
# Install all dependencies
poetry install

# Install the package in editable mode
poetry run pip install -e .
```

**Note**: The directory structure changed from `src/code-graph` to `src/code_graph` (hyphen to underscore) to follow Python package naming conventions.

### 2. Verify Installation

Run the unit tests to ensure everything is working:

```bash
# Run all unit tests
poetry run pytest tests/unit/ -v --no-cov

# Run specific test file
poetry run pytest tests/unit/test_hybrid_scorer.py -v --no-cov
```

Expected output: **11 passed tests** ✅

### 3. Test CLI Commands

Verify the CLI is accessible:

```bash
# Show help
poetry run code-graph --help

# Check status (prototype mode)
poetry run code-graph status

# View command options
poetry run code-graph index --help
poetry run code-graph query --help
```

## Setting Up Memgraph (For Full Implementation)

Memgraph is required for the full implementation but not for the prototype.

### Using Docker

```bash
# Start Memgraph container
docker run -d --name memgraph \
  -p 7687:7687 \
  -v memgraph_data:/var/lib/memgraph \
  memgraph/memgraph-platform:latest

# Verify it's running
docker ps | grep memgraph

# View logs
docker logs memgraph

# Stop Memgraph
docker stop memgraph

# Restart Memgraph
docker restart memgraph
```

### Configuration

Create `.code-graph/config.yaml` in your repository:

```yaml
memgraph:
  host: "127.0.0.1"
  port: 7687
  username: ""
  password: ""
```

See `examples/configs/default-config.yaml` for the full configuration template.

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'code_graph'`

**Solution**: Install the package in editable mode:
```bash
poetry run pip install -e .
```

### Issue: `Could not parse version constraint: <empty>`

**Solution**: Regenerate the lock file:
```bash
rm poetry.lock
poetry lock
poetry install
```

### Issue: Poetry not found

**Solution**: Ensure Poetry is in your PATH or use pipx:
```bash
pipx install poetry
```

### Issue: Python version mismatch

**Solution**: Ensure Python 3.11+ is being used:
```bash
# Check current version
python3 --version

# Use specific version
poetry env use python3.11
```

### Issue: Import errors or path issues

**Solution**: Ensure you're running commands through Poetry:
```bash
# ✅ Correct
poetry run code-graph status
poetry run pytest

# ❌ Incorrect
code-graph status  # Won't find the virtual environment
pytest             # May use wrong Python/packages
```

## Development Workflow

### Running Tests

```bash
# All tests
poetry run pytest

# Unit tests only
poetry run pytest tests/unit/

# Integration tests (requires Memgraph)
poetry run pytest tests/integration/

# With coverage
poetry run pytest --cov

# Watch mode
poetry run pytest-watch
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

### Running the CLI

```bash
# Show version
poetry run code-graph --version

# Verbose mode
poetry run code-graph -v status

# Quiet mode (errors only)
poetry run code-graph -q index
```

## Project Structure

```
.
├── pyproject.toml              # Poetry configuration and dependencies
├── poetry.lock                 # Locked dependency versions
├── src/
│   └── code_graph/             # Main package (note: underscore not hyphen)
│       ├── __init__.py
│       ├── cli/                # Command-line interface
│       ├── models/             # Pydantic data models
│       ├── indexer/            # Code parsing and analysis
│       ├── storage/            # Memgraph integration
│       ├── retrieval/          # Query and scoring
│       └── ...
├── tests/
│   ├── unit/                   # Unit tests (no external dependencies)
│   └── integration/            # Integration tests (require Memgraph)
├── docs/
│   ├── DEVELOPMENT.md          # Development guide
│   └── SETUP.md               # This file
└── examples/
    └── configs/                # Configuration examples
```

## Next Steps

1. **Review Implementation Plan**: See `docs/DEVELOPMENT.md` for the full development guide
2. **Review Tasks**: See `specs/002-repository-code-graph/tasks.md` for the 150 task breakdown
3. **Start Development**: Follow TDD approach outlined in `docs/DEVELOPMENT.md`
4. **MVP Focus**: Tasks T029-T062 (Phase 3 - User Story 1)

## Useful Commands

```bash
# Enter Poetry shell
poetry shell

# Update dependencies
poetry update

# Add new dependency
poetry add <package>

# Add dev dependency
poetry add --group dev <package>

# Show dependency tree
poetry show --tree

# Export requirements.txt
poetry export -f requirements.txt --output requirements.txt

# Clean Poetry cache
poetry cache clear pypi --all
```

## Reference

- **Poetry Documentation**: https://python-poetry.org/docs/
- **Tree-sitter Documentation**: https://tree-sitter.github.io/tree-sitter/
- **Memgraph Documentation**: https://memgraph.com/docs
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Click Documentation**: https://click.palletsprojects.com/

## Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review `docs/DEVELOPMENT.md` for common tasks
3. Check the Poetry documentation for dependency issues
4. Review test output for specific errors
5. Ensure all prerequisites are installed correctly
