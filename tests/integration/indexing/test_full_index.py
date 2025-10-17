"""Integration test for full indexing workflow."""

import pytest
from pathlib import Path
from code_graph.indexer.main import Indexer


class TestFullIndexing:
    """Test end-to-end indexing."""

    def test_index_small_repository(self, tmp_path):
        """Test indexing a small test repository."""
        # Create test repository
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("""
def main():
    print("Hello, world!")
""")
        (tmp_path / "src" / "utils.py").write_text("""
def helper():
    return 42
""")

        # Index repository
        indexer = Indexer()
        result = indexer.index_repository(str(tmp_path))

        # Verify results
        assert result.success is True
        assert result.files_indexed >= 2
        assert result.functions_found >= 2
