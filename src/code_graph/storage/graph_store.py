"""Graph storage: In-memory storage for MVP.

NOTE: This is a simplified in-memory implementation for MVP.
Production should use Memgraph (T008-T010).
"""

from typing import Optional
from code_graph.models.nodes.file_node import FileNode
from code_graph.models.nodes.function_node import FunctionNode
from code_graph.models.edges.base_edge import BaseEdge


class GraphStore:
    """In-memory graph storage."""

    def __init__(self):
        """Initialize empty graph."""
        self.files: dict[str, FileNode] = {}
        self.functions: dict[str, FunctionNode] = {}
        self.edges: list[BaseEdge] = []

    def add_file(self, file_node: FileNode) -> None:
        """Add file node to graph."""
        self.files[file_node.id] = file_node

    def add_function(self, function_node: FunctionNode) -> None:
        """Add function node to graph."""
        self.functions[function_node.id] = function_node

    def add_edge(self, edge: BaseEdge) -> None:
        """Add edge to graph."""
        self.edges.append(edge)

    def get_file(self, file_id: str) -> Optional[FileNode]:
        """Retrieve file node by ID."""
        return self.files.get(file_id)

    def get_all_edges(self) -> list[BaseEdge]:
        """Get all edges in graph."""
        return self.edges

    def clear(self) -> None:
        """Clear all graph data."""
        self.files.clear()
        self.functions.clear()
        self.edges.clear()
