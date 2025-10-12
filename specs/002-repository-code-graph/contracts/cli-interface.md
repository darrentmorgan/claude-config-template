# CLI Interface Contract

**Feature**: Intelligent Code Graph and Context Retrieval System
**Version**: 1.0.0
**Date**: 2025-10-12

## Overview

Command-line interface for the code graph indexer. Provides commands for indexing, querying, watching for changes, and managing graph state.

---

## Installation

```bash
# Install via pip
pip install code-graph-indexer

# Install from source
poetry install
poetry run code-graph --version
```

---

## Global Options

Available for all commands:

```bash
--repo PATH        Repository path (default: current directory)
--config PATH      Config file path (default: .code-graph/config.yaml)
--verbose, -v      Verbose output
--quiet, -q        Suppress non-error output
--help, -h         Show help message
```

---

## Commands

### 1. `index` - Index a repository

**Usage**:
```bash
code-graph index [OPTIONS] [PATH]
```

**Description**:
Performs full indexing of a repository, parsing all supported files and building the code graph.

**Options**:
- `--languages LANGS` - Comma-separated list of languages (default: all supported)
- `--exclude PATTERN` - Glob pattern to exclude (can be repeated)
- `--no-embeddings` - Skip computing semantic embeddings
- `--parallel JOBS` - Number of parallel workers (default: CPU count)
- `--force` - Force re-index even if up-to-date

**Examples**:
```bash
# Index current directory
code-graph index

# Index specific path with options
code-graph index /path/to/repo --languages python,typescript --exclude "tests/**"

# Force full re-index
code-graph index --force
```

**Output**:
```
🔍 Indexing repository: /path/to/repo
📊 Found 1,234 files (python: 456, typescript: 778)
⏱️  Indexing... [====================] 100% (2m 34s)

✅ Indexing complete
   Nodes created: 12,456
   Edges created: 45,789
   Parse errors: 12 (0.97% success rate)
   Coverage: 99.03%

💾 Index persisted to: /path/to/repo/.code-graph/
```

**Exit Codes**:
- 0: Success
- 1: Indexing failed
- 2: Invalid options

---

### 2. `query` - Query for relevant code

**Usage**:
```bash
code-graph query [OPTIONS] QUERY
```

**Description**:
Retrieves relevant code files and functions for a natural language task description.

**Options**:
- `--max-results N` - Maximum number of files to return (default: 12)
- `--hops N` - Maximum relationship hops to explore (default: 2)
- `--format FORMAT` - Output format: json | text | files-only (default: text)
- `--execution-log PATH` - Include execution signals from log file

**Examples**:
```bash
# Basic query
code-graph query "add email validation to user registration"

# With execution context
code-graph query "fix the authentication timeout" --execution-log error.log

# JSON output for programmatic use
code-graph query "refactor the payment module" --format json
```

**Output (text format)**:
```
🔍 Query: "add email validation to user registration"
⏱️  Searching... (1.2s)

📄 Results (4 files, confidence: 0.92)

1. src/auth/register.py (score: 0.95) ⭐⭐⭐⭐⭐
   └─ Contains register_user() function
   └─ Calls create_user() in models.py

2. src/utils/validation.py (score: 0.88) ⭐⭐⭐⭐
   └─ Contains email validation utilities
   └─ Imported by register.py

3. src/models/user.py (score: 0.82) ⭐⭐⭐⭐
   └─ Defines User model with email field

4. tests/test_auth.py (score: 0.76) ⭐⭐⭐
   └─ Tests for registration flow

💡 Tip: Use --hops 3 to explore more distant relationships
```

**Output (JSON format)**:
```json
{
  "query": "add email validation to user registration",
  "files": [
    {
      "path": "src/auth/register.py",
      "relevanceScore": 0.95,
      "rationale": "Contains register_user() function",
      "relatedNodes": [...]
    }
  ],
  "totalConfidence": 0.92,
  "retrievalTimestamp": "2025-10-12T11:00:00Z"
}
```

**Exit Codes**:
- 0: Success (results found)
- 1: Query failed
- 2: No results found

---

### 3. `watch` - Watch for file changes

**Usage**:
```bash
code-graph watch [OPTIONS] [PATH]
```

**Description**:
Monitors repository for file changes and incrementally updates the graph.

**Options**:
- `--debounce MS` - Debounce delay in milliseconds (default: 500)
- `--exclude PATTERN` - Glob pattern to exclude from watching

**Examples**:
```bash
# Watch current directory
code-graph watch

# Watch with custom debounce
code-graph watch --debounce 1000
```

**Output**:
```
👀 Watching: /path/to/repo
📁 Monitoring 1,234 files...

[11:05:23] ✏️  Modified: src/auth/login.py
[11:05:24] 🔄 Updating graph... (324ms)
[11:05:24] ✅ Update complete (3 nodes, 7 edges modified)

[11:06:15] ✏️  Modified: src/models/user.py
[11:06:16] 🔄 Updating graph... (412ms)
[11:06:16] ✅ Update complete (5 nodes, 12 edges modified)

^C
👋 Stopping watcher...
```

**Exit Codes**:
- 0: Normal exit (Ctrl+C)
- 1: Watch failed
- 130: Interrupted by signal

---

### 4. `neighbors` - Explore graph neighbors

**Usage**:
```bash
code-graph neighbors [OPTIONS] NODE_ID
```

**Description**:
Shows all nodes related to a target node within N hops.

**Options**:
- `--hops N` - Maximum hops to explore (default: 2)
- `--edge-types TYPES` - Filter by edge types (comma-separated)
- `--format FORMAT` - Output format: tree | list | json (default: tree)

**Examples**:
```bash
# Explore neighbors (tree view)
code-graph neighbors func_authenticate

# Filter by relationship type
code-graph neighbors func_authenticate --edge-types CALLS,IMPORTS

# Extended exploration
code-graph neighbors class_User --hops 3
```

**Output (tree format)**:
```
🌳 Neighbors of: auth.services.authenticate (2 hops)

├─ 1 hop
│  ├─ CALLS → auth.models.get_user_by_username (confidence: 1.0)
│  ├─ CALLS → auth.utils.verify_password (confidence: 1.0)
│  └─ IMPORTED_BY ← auth.api.login_endpoint (confidence: 1.0)
│
└─ 2 hops
   ├─ auth.models.get_user_by_username
   │  └─ READS_WRITES → models.User.username (confidence: 0.95)
   │
   └─ auth.api.login_endpoint
       └─ CALLED_BY ← tests.test_api.test_login (confidence: 1.0)

📊 Total neighbors: 8 nodes across 2 hops
```

---

### 5. `impact` - Analyze change impact

**Usage**:
```bash
code-graph impact [OPTIONS] NODE_ID
```

**Description**:
Shows upstream dependencies and downstream dependents for a node.

**Options**:
- `--depth N` - Maximum dependency depth (default: 3)
- `--format FORMAT` - Output format: tree | table | json (default: tree)

**Examples**:
```bash
# Analyze impact of changing a function
code-graph impact func_authenticate

# Deeper analysis
code-graph impact class_User --depth 5
```

**Output**:
```
🎯 Impact Analysis: auth.services.authenticate

⬆️  Upstream Dependencies (what this uses)
├─ auth.models.get_user_by_username
├─ auth.utils.verify_password
└─ auth.utils.create_session

⬇️  Downstream Dependents (what uses this)
├─ auth.api.login_endpoint
│  └─ tests.test_api.test_login
│  └─ tests.test_api.test_login_invalid
├─ auth.api.refresh_token
└─ cli.commands.login_command

💥 Blast Radius: 12 affected functions, 3 test files

⚠️  High-impact change: 15 downstream dependencies
```

---

### 6. `tests` - Find related tests

**Usage**:
```bash
code-graph tests [OPTIONS] [NODE_IDS...]
```

**Description**:
Identifies tests that cover specified code elements.

**Options**:
- `--type TYPE` - Filter by test type: unit | integration | e2e | all (default: all)
- `--format FORMAT` - Output format: list | json | commands (default: list)

**Examples**:
```bash
# Find tests for a function
code-graph tests func_authenticate

# Find tests for multiple nodes
code-graph tests func_authenticate class_User

# Generate pytest command
code-graph tests func_authenticate --format commands
```

**Output (list format)**:
```
🧪 Related Tests (3 direct, 5 indirect)

Direct Coverage:
├─ tests/test_auth.py::test_authenticate_valid_user (unit)
├─ tests/test_auth.py::test_authenticate_invalid_password (unit)
└─ tests/test_auth.py::test_authenticate_nonexistent_user (unit)

Indirect Coverage:
├─ tests/test_api.py::test_login_endpoint (integration)
├─ tests/test_api.py::test_login_with_expired_token (integration)
├─ tests/test_workflows.py::test_user_registration_flow (e2e)
└─ ... (2 more)

📊 Estimated coverage: 85% of code paths
⏱️  Estimated run time: ~12 seconds
```

**Output (commands format)**:
```bash
# Run direct tests only
pytest tests/test_auth.py::test_authenticate_valid_user tests/test_auth.py::test_authenticate_invalid_password tests/test_auth.py::test_authenticate_nonexistent_user

# Run all related tests
pytest tests/test_auth.py tests/test_api.py::test_login_endpoint tests/test_workflows.py::test_user_registration_flow
```

---

### 7. `snapshot` - Manage snapshots

**Usage**:
```bash
code-graph snapshot [create|list|show|restore|delete] [OPTIONS]
```

**Description**:
Create and manage point-in-time snapshots of the graph state.

**Subcommands**:

#### `create` - Create a snapshot
```bash
code-graph snapshot create [--label LABEL]
```

#### `list` - List all snapshots
```bash
code-graph snapshot list
```

#### `show` - Show snapshot details
```bash
code-graph snapshot show SNAPSHOT_ID
```

#### `restore` - Restore from snapshot
```bash
code-graph snapshot restore SNAPSHOT_ID
```

#### `delete` - Delete a snapshot
```bash
code-graph snapshot delete SNAPSHOT_ID
```

**Examples**:
```bash
# Create snapshot
code-graph snapshot create --label "before-refactor"

# List snapshots
code-graph snapshot list

# Restore previous state
code-graph snapshot restore abc123de
```

**Output (list)**:
```
📸 Snapshots (5 total)

1. abc123de - 2025-10-12 10:30:00 (label: before-refactor)
   Nodes: 12,456 | Edges: 45,789 | Size: 45.2 MB

2. def456gh - 2025-10-11 15:20:00
   Nodes: 12,234 | Edges: 45,123 | Size: 44.8 MB

...
```

---

### 8. `status` - Show index status

**Usage**:
```bash
code-graph status [OPTIONS]
```

**Description**:
Shows current index statistics and health information.

**Options**:
- `--detailed` - Show detailed statistics

**Examples**:
```bash
code-graph status
code-graph status --detailed
```

**Output**:
```
📊 Code Graph Status

Repository: /path/to/repo
Last indexed: 2025-10-12 10:30:00 (2 hours ago)
Index size: 45.2 MB

Graph Statistics:
├─ Files: 1,234
├─ Modules: 234
├─ Classes: 567
├─ Functions: 3,456
├─ Tests: 789
└─ Total Nodes: 6,280

Relationships:
├─ CONTAINS: 5,234
├─ IMPORTS: 2,345
├─ CALLS: 12,456
├─ INHERITS: 234
├─ READS_WRITES: 3,456
├─ TESTS: 789
└─ Total Edges: 24,514

Coverage: 99.03% (12 files with parse errors)
Memgraph: ✅ Connected
WAL: ✅ Enabled (last sync: 2s ago)
```

---

### 9. `config` - Manage configuration

**Usage**:
```bash
code-graph config [get|set|list|init] [OPTIONS]
```

**Description**:
Get, set, or initialize configuration settings.

**Subcommands**:

#### `init` - Initialize config file
```bash
code-graph config init [--global]
```

#### `list` - List all settings
```bash
code-graph config list
```

#### `get` - Get a setting
```bash
code-graph config get KEY
```

#### `set` - Set a setting
```bash
code-graph config set KEY VALUE
```

**Examples**:
```bash
# Initialize config
code-graph config init

# Set language preferences
code-graph config set languages python,typescript,go

# Get embedding model
code-graph config get embeddings.model
```

---

## Configuration File

Default location: `.code-graph/config.yaml`

```yaml
# Language settings
languages:
  - python
  - typescript
  - javascript
  - go
  - java

# Exclude patterns
exclude:
  - "**/node_modules/**"
  - "**/__pycache__/**"
  - "**/dist/**"
  - "**/build/**"
  - "**/*.min.js"

# Indexing settings
indexing:
  parallel_workers: 8
  enable_embeddings: true
  error_tolerance: 0.70  # Confidence threshold for warnings

# Embeddings
embeddings:
  model: "nomic-ai/nomic-embed-code"
  cache_size: 10000
  lazy_compute: true

# Memgraph connection
memgraph:
  host: "127.0.0.1"
  port: 7687
  username: ""
  password: ""

# WAL settings
wal:
  enabled: true
  snapshot_interval: "5m"
  wal_file_size: "20MB"

# Query settings
query:
  default_max_results: 12
  default_max_hops: 2
  hybrid_weights:
    semantic: 0.4
    graph: 0.4
    execution: 0.2

# Watch settings
watch:
  debounce_ms: 500
  recursive: true
```

---

## Environment Variables

Override config settings with environment variables:

```bash
export CODE_GRAPH_REPO=/path/to/repo
export CODE_GRAPH_MEMGRAPH_HOST=localhost
export CODE_GRAPH_MEMGRAPH_PORT=7687
export CODE_GRAPH_LOG_LEVEL=DEBUG
```

---

## Exit Codes

Standard exit codes across all commands:

- **0**: Success
- **1**: General error (command failed)
- **2**: Invalid arguments or configuration
- **130**: Interrupted by signal (Ctrl+C)

---

## Integration with Claude Code

The indexer integrates with Claude Code's agent delegation system:

```bash
# Query from agent context
code-graph query "$TASK_DESCRIPTION" --format json > context.json

# Find tests for changed files
code-graph tests $(git diff --name-only | xargs code-graph resolve-nodes)

# Watch during development
code-graph watch &
CODE_GRAPH_PID=$!
# ... development work ...
kill $CODE_GRAPH_PID
```

---

## Performance Targets

Per specification requirements:

- **Full indexing**: <10 minutes for 10K files
- **Incremental updates**: <2 seconds per file
- **Query responses**: <3 seconds
- **Memory usage**: ~32GB recommended for 100K file repos

---

**Status**: CLI interface contract complete. Covers all functional requirements from spec.md.
