# Quickstart Guide: Code Graph Indexer

**Feature**: Intelligent Code Graph and Context Retrieval System
**Audience**: Developers integrating the code graph system
**Estimated Time**: 15 minutes

## Overview

This guide walks you through setting up and using the code graph indexer for intelligent context retrieval in multi-agent workflows.

---

## Prerequisites

- **Python**: 3.11 or higher
- **Memory**: 8GB RAM minimum (32GB recommended for large repos)
- **Disk**: 500MB for dependencies + 1-5% of repository size for index
- **Memgraph**: Docker or native installation

---

## Installation

### Step 1: Install Memgraph

**Option A: Docker (Recommended)**
```bash
# Pull and run Memgraph
docker run -d --name memgraph \
  -p 7687:7687 \
  -p 3000:3000 \
  -v memgraph_data:/var/lib/memgraph \
  memgraph/memgraph-platform:latest

# Verify it's running
docker logs memgraph
```

**Option B: Native Installation**
```bash
# macOS (via Homebrew)
brew install memgraph

# Linux (via apt)
curl https://download.memgraph.com/memgraph/v2.11.0/ubuntu-22.04/memgraph_2.11.0-1_amd64.deb -o memgraph.deb
sudo dpkg -i memgraph.deb

# Start service
sudo systemctl start memgraph
```

### Step 2: Install Code Graph Indexer

```bash
# Install via pip (when published)
pip install code-graph-indexer

# OR install from source
git clone https://github.com/your-org/code-graph-indexer.git
cd code-graph-indexer
poetry install
```

### Step 3: Verify Installation

```bash
code-graph --version
# Output: code-graph version 1.0.0

code-graph status
# Should show Memgraph connection status
```

---

## Quick Start (5 Minutes)

### 1. Index Your First Repository

```bash
# Navigate to your project
cd /path/to/your-project

# Initialize configuration (optional - uses defaults if skipped)
code-graph config init

# Index the repository
code-graph index

# Output:
# 🔍 Indexing repository: /path/to/your-project
# ⏱️  Indexing... [====================] 100%
# ✅ Indexing complete (1,234 files, 12,456 nodes, 45,789 edges)
```

**What just happened?**
- Scanned all supported files (Python, TypeScript, Go, Java)
- Parsed code structure (functions, classes, imports)
- Built relationship graph (calls, inheritance, data access)
- Computed semantic embeddings for code
- Persisted everything to Memgraph with WAL

### 2. Query for Relevant Code

```bash
# Ask a natural language question
code-graph query "add email validation to user registration"

# Output shows relevant files with rationales:
# 📄 Results (4 files, confidence: 0.92)
# 1. src/auth/register.py (score: 0.95) ⭐⭐⭐⭐⭐
#    └─ Contains register_user() function
# 2. src/utils/validation.py (score: 0.88) ⭐⭐⭐⭐
#    └─ Contains email validation utilities
# ...
```

### 3. Enable Automatic Updates

```bash
# Watch for file changes (runs in background)
code-graph watch &

# Now edit a file - the index updates automatically
# Edit src/auth/login.py...

# Output:
# [11:05:23] ✏️  Modified: src/auth/login.py
# [11:05:24] 🔄 Updating graph... (324ms)
# [11:05:24] ✅ Update complete
```

---

## Common Workflows

### Workflow 1: Find Code for a New Feature

**Scenario**: You need to add a new feature and want to know which files to modify.

```bash
# Query for relevant code
code-graph query "add two-factor authentication" --format json > context.json

# Use the results in your workflow
cat context.json | jq -r '.files[].path'
# Output:
# src/auth/login.py
# src/models/user.py
# src/utils/otp.py
```

**Integration with Claude Code**:
```bash
# In your agent workflow
CONTEXT=$(code-graph query "$TASK_DESCRIPTION" --format files-only)
echo "Relevant files: $CONTEXT"
# Agent can now read these specific files
```

### Workflow 2: Understand Change Impact

**Scenario**: You're refactoring a function and want to know what it affects.

```bash
# Find the function's node ID
code-graph query "authenticate function in auth service" --format json | \
  jq -r '.files[0].relatedNodes[0].nodeId'
# Output: func_abc123

# Analyze impact
code-graph impact func_abc123

# Output shows:
# ⬆️  Upstream Dependencies (what this uses)
# ⬇️  Downstream Dependents (what uses this)
# 💥 Blast Radius: 12 affected functions
```

### Workflow 3: Run Targeted Tests

**Scenario**: You changed some code and want to run only relevant tests.

```bash
# Get node IDs for changed files
CHANGED_FILES=$(git diff --name-only HEAD~1)
NODE_IDS=$(echo "$CHANGED_FILES" | xargs -I {} code-graph query "file {}" --format json | jq -r '.files[0].relatedNodes[].nodeId')

# Find related tests
code-graph tests $NODE_IDS --format commands > run_tests.sh

# Run the tests
bash run_tests.sh
```

### Workflow 4: Explore Codebase Relationships

**Scenario**: You're new to a codebase and want to understand how modules connect.

```bash
# Start with a key module
code-graph neighbors module_auth --hops 2 --format tree

# Output shows:
# 🌳 Neighbors of: auth (2 hops)
# ├─ IMPORTS → models
# ├─ IMPORTS → utils
# └─ IMPORTED_BY ← api
#    └─ api IMPORTED_BY ← main
```

---

## Configuration

### Basic Configuration

Create `.code-graph/config.yaml` in your repository:

```yaml
# Which languages to index
languages:
  - python
  - typescript

# Exclude patterns
exclude:
  - "**/node_modules/**"
  - "**/__pycache__/**"
  - "**/dist/**"

# Enable semantic embeddings (slower but better retrieval)
indexing:
  enable_embeddings: true
  parallel_workers: 8
```

### Advanced Configuration

```yaml
# Customize hybrid scoring weights
query:
  hybrid_weights:
    semantic: 0.5  # More weight on semantic similarity
    graph: 0.3     # Less weight on graph distance
    execution: 0.2 # Same weight on execution signals

# Adjust confidence threshold
indexing:
  error_tolerance: 0.80  # Higher threshold = stricter parsing

# Memgraph connection
memgraph:
  host: "localhost"
  port: 7687
```

---

## Integration with Claude Code

### Automatic Context Provision

The indexer integrates with Claude Code's delegation system to automatically provide context to agents:

**File**: `.claude/agents/configs/backend-architect.json`
```json
{
  "name": "backend-architect",
  "capabilities": ["api-design", "database", "backend"],
  "context_provider": {
    "type": "code-graph",
    "auto_query": true,
    "max_files": 8
  }
}
```

When an agent receives a task, the indexer automatically:
1. Queries the graph with the task description
2. Retrieves relevant files
3. Provides them as context to the agent

### Manual Queries

Agents can also query explicitly:

**Example Agent Workflow**:
```python
# In agent implementation
from code_graph import Indexer

indexer = Indexer(repo_path="/path/to/repo")
context = indexer.query("implement user authentication")

for file_ref in context.files:
    content = read_file(file_ref.path)
    # Agent processes file with rationale
    print(f"File: {file_ref.path}")
    print(f"Why: {file_ref.rationale}")
```

---

## Performance Optimization

### For Large Repositories (>50K Files)

```yaml
# config.yaml
indexing:
  parallel_workers: 16  # More workers
  enable_embeddings: false  # Skip embeddings initially
  incremental_only: true  # Only update changed files

memgraph:
  memory_limit: "64GB"  # Increase Memgraph memory
```

### Embedding Strategies

```yaml
# Lazy embedding computation (compute on query, not index time)
embeddings:
  lazy_compute: true
  cache_size: 10000  # LRU cache for computed embeddings

# Or disable for faster indexing
indexing:
  enable_embeddings: false
```

### Incremental Updates

```bash
# Instead of full re-index
code-graph index --force

# Use watch mode for continuous updates
code-graph watch
```

---

## Troubleshooting

### Issue: "Memgraph connection failed"

```bash
# Check if Memgraph is running
docker ps | grep memgraph

# Check connection
telnet localhost 7687

# Restart Memgraph
docker restart memgraph
```

### Issue: "Parsing errors for many files"

```bash
# Check detailed status
code-graph status --detailed

# See specific errors
code-graph index --verbose 2>&1 | grep ERROR

# Adjust error tolerance
code-graph config set indexing.error_tolerance 0.5
```

### Issue: "Slow query performance"

```bash
# Check index freshness
code-graph status

# Rebuild if stale
code-graph index --force

# Reduce result count
code-graph query "..." --max-results 6
```

### Issue: "Out of memory during indexing"

```yaml
# config.yaml - reduce parallel workers
indexing:
  parallel_workers: 4  # Reduce from default
  enable_embeddings: false  # Skip embeddings

# OR increase Memgraph memory
memgraph:
  memory_limit: "64GB"
```

---

## Testing Your Setup

Run the built-in test suite to verify everything works:

```bash
# Test basic indexing
code-graph index tests/fixtures/sample-repo

# Test query
code-graph query "find user authentication" --repo tests/fixtures/sample-repo

# Test incremental update
echo "# test change" >> tests/fixtures/sample-repo/src/main.py
code-graph index tests/fixtures/sample-repo

# Verify changes were detected
code-graph status --repo tests/fixtures/sample-repo
```

---

## Next Steps

1. **Explore the API**: Check `contracts/indexer-api.yaml` for programmatic access
2. **Customize Agents**: Update `.claude/agents/configs/` to use code graph context
3. **Monitor Performance**: Use `code-graph status` to track index health
4. **Create Snapshots**: Use `code-graph snapshot create` before major changes

---

## Additional Resources

- **Full CLI Reference**: `contracts/cli-interface.md`
- **Data Model**: `data-model.md`
- **Research Documentation**: `research.md`
- **API Specification**: `contracts/indexer-api.yaml`

---

## Getting Help

```bash
# Command-specific help
code-graph index --help
code-graph query --help

# General help
code-graph --help

# Check status
code-graph status --detailed
```

---

**Status**: Quickstart guide complete. Users can now set up and use the code graph system in ~15 minutes.
