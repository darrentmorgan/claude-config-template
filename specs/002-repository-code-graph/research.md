# Research: Intelligent Code Graph and Context Retrieval System

**Feature Branch**: `002-repository-code-graph`
**Research Date**: 2025-10-12
**Status**: Complete

## Overview

This document consolidates research findings for all technical decisions required to implement the code graph indexing and retrieval system.

---

## 1. Code Parsing Technology

### Decision: Tree-sitter

### Rationale
Tree-sitter provides the best combination of features for error-tolerant, multi-language code parsing:

1. **Error Recovery**: Generates working syntax trees even with partial/erroneous code. Can insert missing tokens and reduce errors without complete parsing failure.

2. **Multi-Language Support**: Native support for Python, JavaScript/TypeScript, Go, and Java through existing grammars. Handles mixed-language files.

3. **Performance**: Incremental parsing with O(1) update complexity. Low memory footprint suitable for large codebases. Multi-threaded support via cheap syntax tree copying.

4. **Ecosystem**: Mature bindings for Python and Node.js. Large collection of maintained language grammars.

### Alternatives Considered
- **srcML**: Limited language support, XML-based output, slower parsing
- **ANTLR**: Good for parsing but less error-tolerant
- **Semantic** (GitHub): Uses tree-sitter internally but adds complexity
- **Babelfish**: Promising but less mature ecosystem
- **CodeQL**: More suited for security analysis than general parsing

### Implementation Approach
```python
# Use tree-sitter core with language-specific grammars
from tree_sitter import Language, Parser

# Load language grammars
PY_LANGUAGE = Language('build/languages.so', 'python')
TS_LANGUAGE = Language('build/languages.so', 'typescript')

# Parse with error recovery
parser = Parser()
parser.set_language(PY_LANGUAGE)
tree = parser.parse(bytes(source_code, "utf8"))

# Even with syntax errors, tree structure is available
if tree.root_node.has_error:
    # Mark relationships as low confidence
    confidence = 0.5
```

### Integration Strategy
1. Create base parser interface for all languages
2. Implement language-specific parsers wrapping tree-sitter grammars
3. Extract AST nodes and convert to graph nodes
4. Handle error nodes by marking relationships with confidence scores
5. Support incremental re-parsing for changed files

---

## 2. Graph Storage

### Decision: Memgraph

### Rationale
Memgraph offers the optimal balance for a code relationship graph:

1. **Performance**: Sub-millisecond query responses. 32,000+ queries per second throughput. 120x faster than Neo4j in benchmarks.

2. **Persistence**: Built-in Write-Ahead Logging (WAL) with configurable durability levels:
   - Synchronous WAL: fsync before every commit (maximum durability)
   - Asynchronous WAL: periodic fsync (performance optimization)
   - Snapshot mechanism for point-in-time recovery

3. **Scalability**: Proven performance for 10K-100K node graphs. In-memory architecture optimized for graph traversals (BFS, DFS, shortest path).

4. **Query Language**: Cypher query language (standard graph query syntax). Supports recursive queries and pattern matching.

### Alternatives Considered
- **Neo4j**: Mature but 120x slower. Better for very large graphs exceeding RAM.
- **FalkorDB**: Redis-based, fast, but less mature than Memgraph.
- **SQLite with graph extensions**: Limited graph query capabilities, slower traversals.
- **NetworkX (in-memory)**: Requires custom persistence layer, no built-in WAL.

### WAL Implementation Strategy
```python
# Memgraph configuration for WAL
from gqlalchemy import Memgraph

memgraph = Memgraph(host="127.0.0.1", port=7687)

# Configure WAL settings
memgraph.execute("""
    SET DATABASE SETTING 'durability.snapshot_interval' TO '300s'
    SET DATABASE SETTING 'durability.wal_file_size' TO '20MB'
""")

# Transactions automatically use WAL
with memgraph.session() as session:
    session.run("""
        CREATE (f:File {path: $path, hash: $hash})
    """, path=file_path, hash=content_hash)
    # Changes logged to WAL before commit
```

### Storage Requirements
- Memory: Recommend 32GB+ RAM for 100K node graphs
- Disk: WAL logs + periodic snapshots
- Expected overhead: <5% of repository size

### Integration Approach
1. Define graph schema (Node types: File, Module, Class, Function, Test; Edge types: Contains, Imports, Calls, Inherits, ReadsWrites, Tests)
2. Implement graph CRUD operations with WAL support
3. Create snapshot mechanism for reproducible builds
4. Optimize queries for common patterns (neighbor expansion, impact analysis)

---

## 3. Semantic Embeddings

### Decision: Nomic Embed Code

### Rationale
Nomic Embed Code provides state-of-the-art code embeddings with offline capability:

1. **Performance**: Outperforms commercial models (OpenAI, Voyage) on CodeSearchNet benchmark. 7B parameter model provides high semantic understanding.

2. **Offline Capability**: Fully open-source (Apache-2.0 license). Runs completely offline without API calls. Can be deployed on developer machines.

3. **Code-Specific Training**: Trained on diverse code corpus. Supports multiple programming languages. Understands code structure, docstrings, and natural language queries.

4. **Integration**: Works with sentence-transformers library (Python). Supports batch processing for efficiency.

### Alternatives Considered
- **OpenAI Embeddings**: High quality but requires API calls (not offline)
- **CodeBERT/GraphCodeBERT**: Good but outperformed by Nomic
- **SFR-Embedding-Code**: Strong performer but more complex
- **Universal Sentence Encoder**: General-purpose, less code-specific

### Implementation Strategy
```python
from sentence_transformers import SentenceTransformer
import torch

# Load model (one-time, cache locally)
model = SentenceTransformer('nomic-ai/nomic-embed-code')

# Compute embeddings for code
def compute_code_embedding(code_snippet: str) -> torch.Tensor:
    return model.encode(code_snippet, convert_to_tensor=True)

# Compute similarity
def cosine_similarity(emb1, emb2):
    return torch.nn.functional.cosine_similarity(emb1, emb2, dim=0)
```

### Caching Strategy
1. **Function-Level Cache**: LRU cache with 10,000 entries. Key by hash of code snippet. Expire after 24 hours.

2. **File-Level Cache**: Persistent disk cache for frequently accessed embeddings. Store in SQLite or similar. Update incrementally when files change.

3. **Batch Processing**: Compute embeddings for multiple functions in parallel. Amortize model loading cost.

### Performance Optimization
- Use GPU acceleration if available (CUDA)
- Lazy loading: compute embeddings on-demand, not during indexing
- Cache embeddings in graph database as node properties

---

## 4. Programming Language & Framework

### Decision: Python 3.11+

### Rationale
Python provides the most complete ecosystem for this project:

1. **Ecosystem Fit**:
   - Native tree-sitter bindings (`tree-sitter-python`)
   - Memgraph driver (`gqlalchemy` or `pymgclient`)
   - Sentence-transformers for Nomic Embed Code
   - Mature async support (`asyncio`)
   - File watching (`watchdog`)

2. **Performance**: Python 3.11+ has significant performance improvements. Type hints enable static analysis. Can use `numba` or `Cython` for compute-intensive operations.

3. **Developer Experience**: Strong typing with type hints. Excellent testing ecosystem (`pytest`). Rich scientific computing libraries.

### Alternatives Considered
- **TypeScript/Node.js**: Good async support but weaker embedding integration (would need ONNX runtime). Less mature graph libraries.
- **Rust**: Maximum performance but steeper learning curve. Harder to integrate with ML models.
- **Hybrid Python/TypeScript**: Adds complexity without clear benefits given Python's capabilities.

### Key Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
tree-sitter = "^0.20"
tree-sitter-python = "^0.20"
tree-sitter-javascript = "^0.20"
gqlalchemy = "^1.4"  # Memgraph driver
sentence-transformers = "^2.2"
torch = "^2.0"  # For embeddings
watchdog = "^3.0"  # File watching
asyncio = "*"  # Async operations
pydantic = "^2.0"  # Data validation
click = "^8.1"  # CLI framework
```

### Testing Framework
- **pytest** with **pytest-asyncio** for async tests
- **pytest-cov** for coverage reporting (target: ≥60%)
- **hypothesis** for property-based testing (graph invariants)
- **pytest-benchmark** for performance regression tests

### Deployment Strategy
```bash
# Package management with poetry
poetry build

# Install as CLI tool
pip install code-graph-indexer

# Usage
code-graph index /path/to/repo
code-graph query "add authentication"
code-graph watch /path/to/repo  # Incremental updates
```

### Performance Considerations
- Use `asyncio` for non-blocking I/O during indexing
- Use `multiprocessing` for parallel file parsing
- Consider `numba` JIT compilation for graph algorithms
- Profile with `cProfile` and optimize hot paths

---

## 5. File Watching & Incremental Updates

### Decision: watchdog + asyncio

### Rationale
Watchdog provides cross-platform file system monitoring with asyncio integration:

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

class CodeChangeHandler(FileSystemEventHandler):
    async def on_modified(self, event):
        if event.is_directory:
            return

        # Trigger incremental update
        await update_graph_for_file(event.src_path)

# Integrate with asyncio
observer = Observer()
observer.schedule(handler, path, recursive=True)
observer.start()
```

### Integration Strategy
1. Monitor file save events in repository
2. Parse only changed files with tree-sitter
3. Identify affected graph nodes and edges
4. Update graph database (Memgraph) with WAL logging
5. Invalidate cached embeddings for changed code
6. Target: <2 second update latency

---

## Summary of Technical Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.11+ | Complete ecosystem, strong typing, async support |
| **Parser** | Tree-sitter | Error-tolerant, multi-language, incremental parsing |
| **Graph Storage** | Memgraph | Fast queries, built-in WAL, Cypher support |
| **Embeddings** | Nomic Embed Code | Offline, state-of-the-art, code-specific |
| **File Watching** | watchdog | Cross-platform, asyncio integration |
| **Testing** | pytest + pytest-asyncio | Mature, async support, rich plugins |
| **CLI** | click or typer | Simple, type-safe, auto-documentation |
| **Packaging** | poetry | Modern dependency management, reproducible builds |

---

## Next Steps

1. **Prototype Phase**:
   - Implement basic tree-sitter parser for Python
   - Set up Memgraph instance and test queries
   - Compute sample embeddings with Nomic Embed Code
   - Benchmark performance on small repository

2. **Integration Phase**:
   - Build graph from parsed AST
   - Implement hybrid scoring formula
   - Add file watching for incremental updates
   - Integrate with Claude Code agent delegation

3. **Validation Phase**:
   - Test on repositories with syntax errors
   - Measure indexing performance (10K file target)
   - Validate retrieval accuracy (90% success rate)
   - Stress test incremental updates

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Memgraph memory requirements | High | Start with smaller repos, implement graph sharding if needed |
| Embedding computation slow | Medium | Cache aggressively, compute lazily, use GPU if available |
| Tree-sitter grammar limitations | Low | Extend grammars or use fallback parsers for edge cases |
| Cross-platform compatibility | Medium | Test on macOS, Linux, Windows. Use CI/CD for validation |

---

## Confidence Assessment

- **Parser Choice (Tree-sitter)**: 90% confident - proven technology, widely used
- **Graph Storage (Memgraph)**: 85% confident - excellent performance, WAL support. Fallback: NetworkX + custom persistence
- **Embeddings (Nomic Embed Code)**: 80% confident - state-of-the-art but relatively new. Fallback: CodeBERT
- **Language (Python)**: 95% confident - best ecosystem fit for all components

---

**Research Complete**: All technical decisions documented with rationale, alternatives, and implementation strategies. Ready to proceed to Phase 1 (Design & Contracts).
