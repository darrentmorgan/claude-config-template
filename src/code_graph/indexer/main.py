"""Main indexer orchestrator."""

from dataclasses import dataclass
from pathlib import Path
from code_graph.indexer.graph_builder import GraphBuilder
from code_graph.storage.graph_store import GraphStore


@dataclass
class IndexResult:
    """Result of repository indexing."""
    success: bool
    files_indexed: int
    functions_found: int
    errors: list[str]


class Indexer:
    """Main indexer for repositories."""

    def __init__(self):
        """Initialize indexer."""
        self.builder = GraphBuilder()
        self.store = GraphStore()

    def index_repository(self, repo_path: str) -> IndexResult:
        """Index a repository.

        Args:
            repo_path: Path to repository root

        Returns:
            IndexResult with statistics
        """
        repo_root = Path(repo_path)
        files_indexed = 0
        functions_found = 0
        errors = []

        # Find Python files
        for py_file in repo_root.rglob("*.py"):
            try:
                result = self.builder.build_from_file(str(py_file), "python")
                self.store.add_file(result.file_node)
                functions_found += len(result.functions)
                files_indexed += 1
            except Exception as e:
                errors.append(f"{py_file}: {e}")

        return IndexResult(
            success=True,
            files_indexed=files_indexed,
            functions_found=functions_found,
            errors=errors
        )
