"""Unit tests for graph builder.

Tests conversion from tree-sitter AST to graph nodes.
"""

import pytest
from pathlib import Path
from code_graph.indexer.graph_builder import GraphBuilder
from code_graph.models.nodes.file_node import FileNode, ParseStatus


class TestGraphBuilder:
    """Test graph builder functionality."""

    @pytest.fixture
    def builder(self):
        """Create graph builder instance."""
        return GraphBuilder()

    def test_build_from_python_file(self, builder, tmp_path):
        """Test building graph from Python file."""
        test_file = tmp_path / "example.py"
        test_file.write_text("""
def greet(name: str) -> str:
    return f"Hello, {name}"

class User:
    def __init__(self, name):
        self.name = name
""")

        result = builder.build_from_file(str(test_file), language="python")

        # Should create FileNode
        assert result.file_node is not None
        assert result.file_node.language == "python"
        assert result.file_node.parse_status == ParseStatus.SUCCESS

        # Should extract functions
        assert len(result.functions) >= 1
        greet_func = next(f for f in result.functions if f.name == "greet")
        assert greet_func.return_type == "str"
        assert len(greet_func.parameters) == 1

        # Should extract classes
        assert len(result.classes) >= 1
        user_class = next(c for c in result.classes if c.name == "User")
        assert user_class.name == "User"

    def test_build_with_syntax_error(self, builder, tmp_path):
        """Test building graph from file with syntax errors."""
        test_file = tmp_path / "broken.py"
        test_file.write_text("""
def valid_func():
    return "works"

def broken_func(
    # Missing closing paren
""")

        result = builder.build_from_file(str(test_file), language="python")

        # Should still create FileNode with PARTIAL status
        assert result.file_node is not None
        assert result.file_node.parse_status == ParseStatus.PARTIAL
        assert result.file_node.error_count > 0

        # Should still extract valid function
        assert len(result.functions) >= 1

    def test_build_from_nonexistent_file(self, builder):
        """Test building graph from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            builder.build_from_file("/nonexistent/path.py", language="python")
