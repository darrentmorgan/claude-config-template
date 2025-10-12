# Data Model: Intelligent Code Graph and Context Retrieval System

**Feature Branch**: `002-repository-code-graph`
**Date**: 2025-10-12
**Status**: Design Phase

## Overview

This document defines the data model for the code graph system, including nodes (code elements), edges (relationships), and supporting entities for retrieval and persistence.

---

## Graph Schema

### Node Types

#### 1. FileNode
Represents a source code file in the repository.

**Properties**:
```python
class FileNode:
    id: str  # UUID or hash-based ID
    path: str  # Relative path from repository root
    language: str  # "python" | "typescript" | "go" | "java"
    content_hash: str  # SHA-256 of file contents
    size_bytes: int
    parse_status: ParseStatus  # "success" | "partial" | "failed"
    error_count: int  # Number of parse errors
    last_indexed: datetime
    embedding: Optional[List[float]]  # Cached semantic embedding (768-dim)
```

**Validations**:
- `path` must be unique within repository
- `content_hash` must be SHA-256 (64 hex chars)
- `language` must be supported language
- `parse_status == "success"` implies `error_count == 0`

**Example**:
```python
FileNode(
    id="f1a2b3c4",
    path="src/auth/login.py",
    language="python",
    content_hash="a7b8c9...",
    size_bytes=4523,
    parse_status="success",
    error_count=0,
    last_indexed="2025-10-12T10:30:00Z",
    embedding=[0.12, -0.34, ...] # 768 floats
)
```

---

#### 2. ModuleNode
Represents a module or namespace within a file.

**Properties**:
```python
class ModuleNode:
    id: str
    name: str  # Module/package name
    qualified_name: str  # Full dotted name (e.g., "auth.services")
    line_start: int
    line_end: int
    docstring: Optional[str]
    is_exported: bool  # Whether module is publicly exported
```

**Validations**:
- `qualified_name` should match language conventions
- `line_start` ≤ `line_end`
- Must have CONTAINS edge from parent FileNode

**Example**:
```python
ModuleNode(
    id="m9x8y7",
    name="services",
    qualified_name="auth.services",
    line_start=1,
    line_end=150,
    docstring="Authentication service layer",
    is_exported=True
)
```

---

#### 3. ClassNode
Represents a class or interface definition.

**Properties**:
```python
class ClassNode:
    id: str
    name: str
    qualified_name: str  # e.g., "auth.models.User"
    line_start: int
    line_end: int
    docstring: Optional[str]
    is_abstract: bool
    is_exported: bool
    decorators: List[str]  # e.g., ["@dataclass", "@frozen"]
    type_params: List[str]  # Generic type parameters
```

**Validations**:
- Must have CONTAINS edge from parent ModuleNode or FileNode
- If `is_abstract == True`, should have INHERITS edges to concrete implementations
- `line_start` ≤ `line_end`

**Example**:
```python
ClassNode(
    id="c4d5e6",
    name="User",
    qualified_name="auth.models.User",
    line_start=10,
    line_end=45,
    docstring="User account model",
    is_abstract=False,
    is_exported=True,
    decorators=["@dataclass"],
    type_params=[]
)
```

---

#### 4. FunctionNode
Represents a function, method, or procedure.

**Properties**:
```python
class FunctionNode:
    id: str
    name: str
    qualified_name: str  # e.g., "auth.services.authenticate"
    line_start: int
    line_end: int
    docstring: Optional[str]
    signature: str  # Full function signature
    return_type: Optional[str]
    parameters: List[Parameter]
    is_async: bool
    is_exported: bool
    decorators: List[str]
    cyclomatic_complexity: Optional[int]
```

**Nested Type**:
```python
class Parameter:
    name: str
    type_hint: Optional[str]
    default_value: Optional[str]
    is_optional: bool
```

**Validations**:
- Must have CONTAINS edge from parent ClassNode, ModuleNode, or FileNode
- `parameters` should match parsed function signature
- `line_start` ≤ `line_end`

**Example**:
```python
FunctionNode(
    id="f7g8h9",
    name="authenticate",
    qualified_name="auth.services.authenticate",
    line_start=50,
    line_end=75,
    docstring="Authenticates user credentials",
    signature="def authenticate(username: str, password: str) -> Optional[User]",
    return_type="Optional[User]",
    parameters=[
        Parameter(name="username", type_hint="str", default_value=None, is_optional=False),
        Parameter(name="password", type_hint="str", default_value=None, is_optional=False)
    ],
    is_async=False,
    is_exported=True,
    decorators=[],
    cyclomatic_complexity=5
)
```

---

#### 5. TestNode
Represents a test function or test case.

**Properties**:
```python
class TestNode:
    id: str
    name: str
    qualified_name: str
    line_start: int
    line_end: int
    test_type: str  # "unit" | "integration" | "e2e"
    test_framework: str  # "pytest" | "jest" | "go test"
    fixtures: List[str]  # Test fixtures/dependencies
    tags: List[str]  # e.g., ["slow", "database"]
```

**Validations**:
- Must have CONTAINS edge from parent FileNode
- Should have TESTS edges to code under test
- `test_type` must be one of defined types

**Example**:
```python
TestNode(
    id="t1i2j3",
    name="test_authenticate_valid_user",
    qualified_name="tests.test_auth.test_authenticate_valid_user",
    line_start=10,
    line_end=25,
    test_type="unit",
    test_framework="pytest",
    fixtures=["user_fixture", "db_session"],
    tags=["database"]
)
```

---

### Edge Types

#### 1. CONTAINS
**Description**: Represents containment relationship (file contains module, module contains class, class contains function).

**Properties**:
```python
class ContainsEdge:
    type: str = "CONTAINS"
    confidence: float  # 0.0-1.0
    metadata: Dict[str, Any]
```

**Examples**:
- `FileNode -[CONTAINS]-> ModuleNode`
- `ModuleNode -[CONTAINS]-> ClassNode`
- `ClassNode -[CONTAINS]-> FunctionNode`
- `FileNode -[CONTAINS]-> TestNode`

**Validations**:
- `confidence == 1.0` for successfully parsed code
- `confidence < 1.0` for partial parses

---

#### 2. IMPORTS
**Description**: Represents import/include/require relationships between files or modules.

**Properties**:
```python
class ImportsEdge:
    type: str = "IMPORTS"
    confidence: float
    import_type: str  # "absolute" | "relative" | "dynamic"
    imported_names: List[str]  # Specific symbols imported (e.g., ["User", "authenticate"])
    is_resolved: bool  # Whether target file was found
    metadata: Dict[str, Any]
```

**Examples**:
- `FileNode -[IMPORTS]-> FileNode` (file-level import)
- `ModuleNode -[IMPORTS]-> ModuleNode` (module-level import)

**Validations**:
- `is_resolved == False` implies `confidence ≤ 0.7`
- Must reference valid source and target nodes

---

#### 3. CALLS
**Description**: Represents function call relationships.

**Properties**:
```python
class CallsEdge:
    type: str = "CALLS"
    confidence: float
    call_type: str  # "direct" | "indirect" | "dynamic"
    call_sites: List[CallSite]  # Locations where call occurs
    is_recursive: bool
    metadata: Dict[str, Any]
```

**Nested Type**:
```python
class CallSite:
    line_number: int
    column: int
    context: str  # Surrounding code snippet
```

**Examples**:
- `FunctionNode -[CALLS]-> FunctionNode`

**Validations**:
- `call_type == "dynamic"` implies lower confidence
- `is_recursive == True` when source and target are same function

---

#### 4. INHERITS
**Description**: Represents class inheritance or interface implementation.

**Properties**:
```python
class InheritsEdge:
    type: str = "INHERITS"
    confidence: float
    inheritance_type: str  # "extends" | "implements" | "mixin"
    is_direct: bool  # Direct parent vs transitive ancestor
    metadata: Dict[str, Any]
```

**Examples**:
- `ClassNode -[INHERITS]-> ClassNode`

**Validations**:
- `is_direct == True` for immediate parent
- No circular inheritance (graph must be acyclic for INHERITS edges)

---

#### 5. READS_WRITES
**Description**: Represents data access relationships (reads/writes to variables, fields, databases).

**Properties**:
```python
class ReadsWritesEdge:
    type: str = "READS_WRITES"
    confidence: float
    access_type: str  # "reads" | "writes" | "both"
    access_points: List[AccessPoint]
    metadata: Dict[str, Any]
```

**Nested Type**:
```python
class AccessPoint:
    line_number: int
    operation: str  # "read" | "write" | "update"
    context: str
```

**Examples**:
- `FunctionNode -[READS_WRITES]-> ClassNode` (function accesses class fields)

**Validations**:
- `access_type` must match operations in `access_points`

---

#### 6. TESTS
**Description**: Represents test coverage relationship.

**Properties**:
```python
class TestsEdge:
    type: str = "TESTS"
    confidence: float
    coverage_type: str  # "unit" | "integration" | "e2e"
    coverage_percentage: Optional[float]  # If known
    metadata: Dict[str, Any]
```

**Examples**:
- `TestNode -[TESTS]-> FunctionNode`
- `TestNode -[TESTS]-> ClassNode`
- `TestNode -[TESTS]-> ModuleNode`

**Validations**:
- `coverage_percentage` should be 0.0-100.0 if present

---

## Supporting Entities

### ContextPack
Represents a retrieval result for a query.

**Properties**:
```python
class ContextPack:
    query: str  # Original natural language query
    files: List[FileReference]
    total_confidence: float  # Weighted average
    retrieval_timestamp: datetime
    max_hops: int  # How many relationship hops were explored
```

**Nested Type**:
```python
class FileReference:
    file_node: FileNode
    relevance_score: float  # Hybrid score (0.0-1.0)
    rationale: str  # Why this file was selected
    related_nodes: List[NodeReference]  # Classes/functions of interest
```

```python
class NodeReference:
    node: Union[ClassNode, FunctionNode, ModuleNode]
    score: float
    score_breakdown: ScoreBreakdown
```

```python
class ScoreBreakdown:
    semantic_score: float  # From embedding similarity
    graph_score: float  # From graph distance
    execution_score: float  # From logs/traces
    hybrid_score: float  # 0.4*semantic + 0.4*graph + 0.2*execution
```

**Example**:
```python
ContextPack(
    query="add email validation to user registration",
    files=[
        FileReference(
            file_node=FileNode(path="src/auth/register.py", ...),
            relevance_score=0.92,
            rationale="Contains register_user() function",
            related_nodes=[
                NodeReference(
                    node=FunctionNode(name="register_user", ...),
                    score=0.92,
                    score_breakdown=ScoreBreakdown(
                        semantic_score=0.85,
                        graph_score=0.95,
                        execution_score=0.0,
                        hybrid_score=0.92
                    )
                )
            ]
        ),
        FileReference(
            file_node=FileNode(path="src/utils/validation.py", ...),
            relevance_score=0.88,
            rationale="Contains email validation utilities",
            related_nodes=[...]
        )
    ],
    total_confidence=0.90,
    retrieval_timestamp="2025-10-12T11:00:00Z",
    max_hops=2
)
```

---

### IndexSnapshot
Represents a point-in-time capture of the graph state.

**Properties**:
```python
class IndexSnapshot:
    id: str  # UUID
    timestamp: datetime
    repository_path: str
    commit_hash: Optional[str]  # Git commit if available
    node_count: int
    edge_count: int
    storage_size_bytes: int
    coverage_percentage: float  # % of files successfully indexed
    errors: List[IndexError]
```

**Nested Type**:
```python
class IndexError:
    file_path: str
    error_type: str  # "parse_error" | "encoding_error" | "io_error"
    message: str
    line_number: Optional[int]
```

---

### WALEntry
Represents a single Write-Ahead Log entry.

**Properties**:
```python
class WALEntry:
    sequence_number: int  # Monotonically increasing
    timestamp: datetime
    operation: str  # "CREATE_NODE" | "UPDATE_NODE" | "DELETE_NODE" | "CREATE_EDGE" | "DELETE_EDGE"
    entity_type: str  # "FileNode" | "ClassNode" | "FunctionNode" | "IMPORTS" | etc.
    entity_id: str
    old_state: Optional[Dict[str, Any]]  # For updates and deletes
    new_state: Optional[Dict[str, Any]]  # For creates and updates
    checksum: str  # CRC32 or SHA-256 of entry
```

**Example**:
```python
WALEntry(
    sequence_number=1523,
    timestamp="2025-10-12T11:05:32Z",
    operation="UPDATE_NODE",
    entity_type="FunctionNode",
    entity_id="f7g8h9",
    old_state={"signature": "def authenticate(username, password)", ...},
    new_state={"signature": "def authenticate(username: str, password: str) -> Optional[User]", ...},
    checksum="a7f3c9b2"
)
```

---

## Confidence Scoring Rules

Confidence scores (0.0-1.0) indicate relationship certainty:

| Score Range | Meaning | Example |
|-------------|---------|---------|
| 1.0 | Certain | Successfully parsed import statement |
| 0.9-0.99 | Very High | Direct function call in clean code |
| 0.8-0.89 | High | Inferred relationship from type hints |
| 0.7-0.79 | Medium | Dynamic import that resolved |
| 0.5-0.69 | Low | Partial parse recovered structure |
| 0.0-0.49 | Very Low | Speculative edge in broken code |

**Warning Threshold**: Display warnings to users when confidence ≤ 0.70 (medium threshold).

---

## State Transitions

### FileNode Parse Status
```
[new file detected]
    ↓
INDEXING → success → "success" (error_count=0, confidence=1.0)
         → partial → "partial" (error_count>0, confidence<1.0)
         → failure → "failed" (error_count>>0, confidence=0.0)

[file modified]
    ↓
RE-INDEXING → (same transitions as above)
```

### Edge Confidence Updates
```
[initial parse] → confidence = 1.0 (if code valid)
                → confidence = 0.5 (if code has errors)

[target becomes available] → confidence increases (e.g., 0.5 → 0.9)

[target deleted] → confidence = 0.0, edge marked for pruning
```

---

## Validation Rules

### Cross-Entity Consistency
1. **CONTAINS edges must form a tree**: No cycles, single parent for each contained node
2. **INHERITS edges must be acyclic**: No circular inheritance chains
3. **Node line ranges must nest properly**: Child nodes' line ranges must be within parent's range
4. **Confidence consistency**: If a node has `parse_status="success"`, all outgoing CONTAINS edges should have `confidence=1.0`

### Integrity Constraints
1. All edges must reference existing nodes (foreign key constraint)
2. `qualified_name` must be unique within repository for ClassNode and FunctionNode
3. `path` must be unique for FileNode
4. WAL `sequence_number` must be strictly increasing

---

## Query Patterns

Common graph queries the system must optimize for:

1. **Find all files importing module X**:
   ```cypher
   MATCH (file:FileNode)-[:IMPORTS]->(target:ModuleNode {name: 'X'})
   RETURN file
   ```

2. **Find all functions called by function F**:
   ```cypher
   MATCH (f:FunctionNode {qualified_name: 'F'})-[:CALLS]->(called:FunctionNode)
   RETURN called
   ```

3. **Find all tests covering class C**:
   ```cypher
   MATCH (test:TestNode)-[:TESTS]->(class:ClassNode {name: 'C'})
   RETURN test
   ```

4. **Find neighbors within N hops**:
   ```cypher
   MATCH path = (start:Node {id: $id})-[*1..N]-(neighbor)
   RETURN DISTINCT neighbor, length(path) AS distance
   ORDER BY distance
   ```

5. **Find impact of changing function F** (downstream dependents):
   ```cypher
   MATCH path = (f:FunctionNode {qualified_name: 'F'})<-[:CALLS*1..3]-(dependent)
   RETURN DISTINCT dependent, length(path) AS depth
   ```

---

## Persistence Strategy

### Memgraph Schema Definition
```cypher
// Create indexes for fast lookups
CREATE INDEX ON :FileNode(path);
CREATE INDEX ON :ClassNode(qualified_name);
CREATE INDEX ON :FunctionNode(qualified_name);
CREATE INDEX ON :TestNode(qualified_name);

// Create constraints
CREATE CONSTRAINT ON (f:FileNode) ASSERT f.path IS UNIQUE;
CREATE CONSTRAINT ON (c:ClassNode) ASSERT c.qualified_name IS UNIQUE;
CREATE CONSTRAINT ON (fn:FunctionNode) ASSERT fn.qualified_name IS UNIQUE;
```

### WAL Configuration
```python
# Memgraph WAL settings
memgraph.execute("""
    SET DATABASE SETTING 'durability.snapshot_interval' TO '300s';  -- Snapshot every 5 minutes
    SET DATABASE SETTING 'durability.wal_file_size' TO '20MB';      -- 20MB WAL files
    SET DATABASE SETTING 'durability.wal_enabled' TO 'true';        -- Enable WAL
""")
```

---

## Next Steps

1. Implement Pydantic models for all entities with validation
2. Create Memgraph schema and indexes
3. Write unit tests for data model constraints
4. Implement serialization/deserialization for graph persistence
5. Design API contracts using these entities

---

**Status**: Data model complete. Ready for contract generation (Phase 1 continued).
