"""Graph builder: Convert tree-sitter AST to graph nodes."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from code_graph.indexer.parsers.python_parser import PythonParser
from code_graph.indexer.parsers.typescript_parser import TypeScriptParser
from code_graph.indexer.parsers.go_parser import GoParser
from code_graph.models.nodes.file_node import FileNode, ParseStatus
from code_graph.models.nodes.function_node import FunctionNode
from code_graph.models.nodes.class_node import ClassNode


@dataclass
class BuildResult:
    """Result of graph building."""
    file_node: FileNode
    functions: list[FunctionNode]
    classes: list[ClassNode]
    success: bool


class GraphBuilder:
    """Builds graph nodes from source files."""

    def __init__(self):
        """Initialize graph builder with language parsers."""
        self.parsers = {
            "python": PythonParser(),
            "typescript": TypeScriptParser(),
            "javascript": TypeScriptParser(),  # TypeScript parser handles JS
            "go": GoParser(),
        }

    def build_from_file(self, file_path: str, language: str) -> BuildResult:
        """Build graph nodes from a source file.

        Args:
            file_path: Path to source file
            language: Programming language

        Returns:
            BuildResult with nodes extracted

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If language not supported
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        parser = self.parsers.get(language.lower())
        if not parser:
            raise ValueError(f"Unsupported language: {language}")

        # Parse file
        result = parser.parse_file(file_path)

        return BuildResult(
            file_node=result.file_node,
            functions=result.functions,
            classes=result.classes,
            success=result.success
        )
