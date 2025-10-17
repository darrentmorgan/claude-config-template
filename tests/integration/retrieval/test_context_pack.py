"""Integration test for context pack generation."""

import pytest
from code_graph.retrieval.context_pack import ContextPackBuilder


class TestContextPack:
    """Test context pack assembly."""

    def test_build_context_pack(self, indexed_repo):
        """Test building context pack with rationales."""
        builder = ContextPackBuilder(graph=indexed_repo)

        pack = builder.build(
            query="Fix authentication bug",
            top_n=5
        )

        # Should contain files
        assert len(pack.files) <= 5

        # Should have required fields
        assert pack.total_confidence >= 0.0
        assert pack.total_confidence <= 1.0
        assert pack.max_hops >= 1
        assert pack.retrieval_timestamp is not None

        # Each file should have metadata
        for file_ref in pack.files:
            assert file_ref.file_path
            assert file_ref.rationale
            assert file_ref.relevance_score >= 0.0
            assert file_ref.relevance_score <= 1.0
