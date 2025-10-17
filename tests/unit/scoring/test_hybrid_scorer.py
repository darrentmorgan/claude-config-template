"""Unit tests for hybrid scorer.

Tests 0.4·semantic + 0.4·graph + 0.2·execution scoring formula.
"""

import pytest
from code_graph.retrieval.hybrid_scorer import HybridScorer


class TestHybridScorer:
    """Test hybrid scoring."""

    @pytest.fixture
    def scorer(self):
        """Create hybrid scorer with default weights."""
        return HybridScorer(
            embedding_weight=0.4,
            graph_weight=0.4,
            signal_weight=0.2
        )

    def test_score_with_all_components(self, scorer):
        """Test scoring with semantic, graph, and signal components."""
        score = scorer.calculate_score(
            embedding_similarity=0.8,
            graph_distance=2,  # 1/(1+2) = 0.333
            execution_signal_score=0.9
        )

        # 0.4*0.8 + 0.4*0.333 + 0.2*0.9 = 0.32 + 0.133 + 0.18 = 0.633
        assert 0.6 < score < 0.7

    def test_score_without_signals(self, scorer):
        """Test scoring when execution signals unavailable."""
        score = scorer.calculate_score(
            embedding_similarity=0.8,
            graph_distance=2,
            execution_signal_score=None  # No signals available
        )

        # Should fallback to 0.5·embedding + 0.5·graph
        # 0.5*0.8 + 0.5*0.333 = 0.4 + 0.167 = 0.567
        assert 0.5 < score < 0.6

    def test_score_normalization(self, scorer):
        """Test scores are normalized to [0, 1]."""
        score = scorer.calculate_score(
            embedding_similarity=1.0,
            graph_distance=0,  # 1/(1+0) = 1.0
            execution_signal_score=1.0
        )

        # Should be capped at 1.0
        assert score <= 1.0
        assert score >= 0.0
