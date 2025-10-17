"""Unit tests for relationship extractor.

Tests extraction of imports, calls, inheritance edges.
"""

import pytest
from code_graph.indexer.relationship_extractor import RelationshipExtractor
from code_graph.models.edges.base_edge import EdgeType


class TestRelationshipExtractor:
    """Test relationship extraction."""

    @pytest.fixture
    def extractor(self):
        """Create relationship extractor."""
        return RelationshipExtractor()

    def test_extract_import_relationships(self, extractor, tmp_path):
        """Test extracting import edges."""
        test_file = tmp_path / "imports.py"
        test_file.write_text("""
import os
from pathlib import Path
from typing import List, Dict
""")

        edges = extractor.extract_from_file(str(test_file), language="python")

        # Should create IMPORTS edges
        import_edges = [e for e in edges if e.type == EdgeType.IMPORTS]
        assert len(import_edges) >= 3

        # Check specific imports
        modules = [e.metadata.get("target_module") for e in import_edges]
        assert "os" in modules
        assert "pathlib" in modules
        assert "typing" in modules

    def test_extract_function_calls(self, extractor, tmp_path):
        """Test extracting function call edges."""
        test_file = tmp_path / "calls.py"
        test_file.write_text("""
def helper():
    return "data"

def main():
    result = helper()
    print(result)
""")

        edges = extractor.extract_from_file(str(test_file), language="python")

        # Should create CALLS edges
        call_edges = [e for e in edges if e.type == EdgeType.CALLS]
        assert len(call_edges) >= 1

    def test_extract_inheritance(self, extractor, tmp_path):
        """Test extracting inheritance edges."""
        test_file = tmp_path / "inherit.py"
        test_file.write_text("""
class Base:
    pass

class Derived(Base):
    pass
""")

        edges = extractor.extract_from_file(str(test_file), language="python")

        # Should create INHERITS edge
        inherit_edges = [e for e in edges if e.type == EdgeType.INHERITS]
        assert len(inherit_edges) >= 1
