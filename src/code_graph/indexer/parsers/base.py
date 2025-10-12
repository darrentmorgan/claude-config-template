"""Base parser interface for all language-specific parsers."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from code_graph.models.nodes.file_node import FileNode, ParseStatus


class ParserResult(BaseModel):
    """Result of parsing a file."""

    file_node: FileNode
    modules: list[Any]  # ModuleNode instances
    classes: list[Any]  # ClassNode instances
    functions: list[Any]  # FunctionNode instances
    imports: list[Any]  # Import objects or tuples
    errors: list[dict[str, Any]]
    edges: list[Any] = []  # BaseEdge instances
    success: bool = True  # Whether parsing succeeded


class BaseParser(ABC):
    """Base class for language-specific parsers using tree-sitter.

    Each language parser must implement:
    - parse_file(): Parse source code and extract structure
    - extract_imports(): Find import/include statements
    - extract_functions(): Find function/method definitions
    - extract_classes(): Find class/interface definitions
    """

    def __init__(self, language: str):
        """Initialize parser for specific language.

        Args:
            language: Programming language (python, typescript, go, java)
        """
        self.language = language
        self._tree_sitter_language = None  # TODO: Load tree-sitter grammar

    @abstractmethod
    def parse_file(self, file_path: str, content: str) -> ParserResult:
        """Parse a source file and extract structure.

        Args:
            file_path: Relative path from repository root
            content: File contents as string

        Returns:
            ParserResult containing extracted nodes and relationships

        Raises:
            ParseError: If file cannot be parsed
        """
        pass

    @abstractmethod
    def extract_imports(self, tree: Any) -> list[tuple[str, list[str]]]:
        """Extract import statements from AST.

        Args:
            tree: Tree-sitter syntax tree

        Returns:
            List of (target_path, imported_names) tuples
        """
        pass

    @abstractmethod
    def extract_functions(self, tree: Any, parent_path: str) -> list[Any]:
        """Extract function definitions from AST.

        Args:
            tree: Tree-sitter syntax tree
            parent_path: Qualified name of parent (for methods)

        Returns:
            List of FunctionNode instances
        """
        pass

    @abstractmethod
    def extract_classes(self, tree: Any, parent_path: str) -> list[Any]:
        """Extract class definitions from AST.

        Args:
            tree: Tree-sitter syntax tree
            parent_path: Qualified name of parent module

        Returns:
            List of ClassNode instances
        """
        pass

    def handle_parse_errors(self, tree: Any) -> tuple[ParseStatus, int]:
        """Analyze tree for parse errors.

        Args:
            tree: Tree-sitter syntax tree

        Returns:
            Tuple of (parse_status, error_count)
        """
        # TODO: Implement error node detection
        # Check if tree.root_node.has_error
        # Count error nodes in tree
        # Determine if parsing was success/partial/failed
        return ParseStatus.SUCCESS, 0

    def calculate_confidence(self, parse_status: ParseStatus, error_count: int) -> float:
        """Calculate confidence score based on parse status.

        Args:
            parse_status: Result of parsing
            error_count: Number of errors encountered

        Returns:
            Confidence score (0.0-1.0)
        """
        if parse_status == ParseStatus.SUCCESS:
            return 1.0
        elif parse_status == ParseStatus.PARTIAL:
            # Reduce confidence based on error count
            return max(0.5, 1.0 - (error_count * 0.1))
        else:  # FAILED
            return 0.0
