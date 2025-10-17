"""Integration test for email validation query scenario."""

import pytest
from code_graph.retrieval.query_engine import QueryEngine


class TestEmailValidationQuery:
    """Test querying for email validation code."""

    def test_email_validation_query(self, indexed_repo):
        """Test: 'Add email validation to user registration'."""
        engine = QueryEngine(graph=indexed_repo)

        results = engine.query("Add email validation to user registration")

        # Should return relevant files
        assert len(results.files) > 0

        # Should include rationales
        assert all(r.rationale for r in results.files)

        # Should have relevance scores (using new field name)
        assert all(0.0 <= r.relevance_score <= 1.0 for r in results.files)

        # Should have required ContextPack fields
        assert results.total_confidence >= 0.0
        assert results.max_hops >= 1
