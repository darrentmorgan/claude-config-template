"""Relationship extractor: Extract edges between nodes."""

from pathlib import Path
from code_graph.models.edges.base_edge import BaseEdge, EdgeType
from code_graph.indexer.parsers.python_parser import PythonParser


class RelationshipExtractor:
    """Extracts relationships (edges) from source files."""

    def __init__(self):
        """Initialize relationship extractor."""
        self.parsers = {
            "python": PythonParser(),
        }

    def extract_from_file(self, file_path: str, language: str) -> list[BaseEdge]:
        """Extract relationship edges from a file.

        Args:
            file_path: Path to source file
            language: Programming language

        Returns:
            List of edges (IMPORTS, CALLS, INHERITS)
        """
        parser = self.parsers.get(language.lower())
        if not parser:
            return []

        result = parser.parse_file(file_path)
        return result.edges
