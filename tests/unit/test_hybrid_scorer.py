"""Unit tests for HybridScorer.

Following TDD principles:
1. Write tests FIRST
2. Verify tests FAIL
3. Implement code to pass tests
4. Refactor
"""

import pytest

from code_graph.retrieval.hybrid_scorer import HybridScorer
from code_graph.models.context_pack import ScoreBreakdown


class TestHybridScorer:
    """Test suite for HybridScorer class."""

    def test_default_weights(self):
        """Test scorer initializes with default weights (0.4, 0.4, 0.2)."""
        scorer = HybridScorer()

        assert scorer.semantic_weight == 0.4
        assert scorer.graph_weight == 0.4
        assert scorer.execution_weight == 0.2

    def test_custom_weights(self):
        """Test scorer accepts custom weights."""
        scorer = HybridScorer(
            semantic_weight=0.5,
            graph_weight=0.3,
            execution_weight=0.2,
        )

        assert scorer.semantic_weight == 0.5
        assert scorer.graph_weight == 0.3
        assert scorer.execution_weight == 0.2

    def test_weights_must_sum_to_one(self):
        """Test that weights must sum to 1.0."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            HybridScorer(
                semantic_weight=0.5,
                graph_weight=0.5,
                execution_weight=0.5,
            )

    def test_score_calculation(self):
        """Test hybrid score calculation with formula."""
        scorer = HybridScorer()

        result = scorer.score(
            semantic_score=0.8,
            graph_score=0.9,
            execution_score=0.5,
        )

        # Expected: 0.4 * 0.8 + 0.4 * 0.9 + 0.2 * 0.5 = 0.78
        assert isinstance(result, ScoreBreakdown)
        assert result.semantic_score == 0.8
        assert result.graph_score == 0.9
        assert result.execution_score == 0.5
        assert pytest.approx(result.hybrid_score, 0.001) == 0.78

    def test_score_boundary_conditions(self):
        """Test scoring with boundary values."""
        scorer = HybridScorer()

        # All zeros
        result = scorer.score(0.0, 0.0, 0.0)
        assert result.hybrid_score == 0.0

        # All ones
        result = scorer.score(1.0, 1.0, 1.0)
        assert result.hybrid_score == 1.0

    def test_graph_distance_decay(self):
        """Test that graph score decreases with distance."""
        scorer = HybridScorer()

        # Distance 0 (same node)
        score_0 = 1.0 / (1.0 + 0)
        assert score_0 == 1.0

        # Distance 1 (one hop away)
        score_1 = 1.0 / (1.0 + 1)
        assert score_1 == 0.5

        # Distance 2 (two hops away)
        score_2 = 1.0 / (1.0 + 2)
        assert pytest.approx(score_2, 0.001) == 0.333


@pytest.mark.parametrize(
    "semantic,graph,execution,expected",
    [
        (1.0, 1.0, 1.0, 1.0),  # Perfect match
        (0.0, 0.0, 0.0, 0.0),  # No match
        (1.0, 0.0, 0.0, 0.4),  # Pure semantic
        (0.0, 1.0, 0.0, 0.4),  # Pure graph
        (0.0, 0.0, 1.0, 0.2),  # Pure execution
    ],
)
def test_scoring_scenarios(semantic, graph, execution, expected):
    """Test various scoring scenarios."""
    scorer = HybridScorer()
    result = scorer.score(semantic, graph, execution)
    assert pytest.approx(result.hybrid_score, 0.001) == expected
