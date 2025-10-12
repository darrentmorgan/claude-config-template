"""Hybrid scoring engine combining semantic, graph, and execution signals."""

from typing import Optional

from code_graph.models.context_pack import ScoreBreakdown


class HybridScorer:
    """Combines multiple scoring signals using weighted formula.

    Formula: 0.4·semantic_similarity + 0.4·graph_proximity + 0.2·execution_signals

    This balanced weighting equally prioritizes semantic meaning and structural
    relationships, with a moderate boost from runtime data.
    """

    def __init__(
        self,
        semantic_weight: float = 0.4,
        graph_weight: float = 0.4,
        execution_weight: float = 0.2,
    ):
        """Initialize hybrid scorer with custom weights.

        Args:
            semantic_weight: Weight for embedding similarity (default: 0.4)
            graph_weight: Weight for graph distance (default: 0.4)
            execution_weight: Weight for execution signals (default: 0.2)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        total = semantic_weight + graph_weight + execution_weight
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        self.semantic_weight = semantic_weight
        self.graph_weight = graph_weight
        self.execution_weight = execution_weight

    def score(
        self,
        semantic_score: float,
        graph_score: float,
        execution_score: float,
    ) -> ScoreBreakdown:
        """Calculate hybrid score from individual components.

        Args:
            semantic_score: Embedding similarity (0.0-1.0)
            graph_score: Graph proximity (0.0-1.0)
            execution_score: Execution signal relevance (0.0-1.0)

        Returns:
            ScoreBreakdown with all components and hybrid result
        """
        hybrid = (
            self.semantic_weight * semantic_score
            + self.graph_weight * graph_score
            + self.execution_weight * execution_score
        )

        return ScoreBreakdown(
            semantic_score=semantic_score,
            graph_score=graph_score,
            execution_score=execution_score,
            hybrid_score=hybrid,
        )

    def score_query(
        self,
        query_embedding: list[float],
        candidate_embedding: list[float],
        graph_distance: int,
        has_execution_signals: bool,
    ) -> ScoreBreakdown:
        """Score a candidate node for a query.

        Args:
            query_embedding: Query embedding vector
            candidate_embedding: Candidate node embedding vector
            graph_distance: Number of hops from query-related nodes
            has_execution_signals: Whether candidate appears in logs/traces

        Returns:
            ScoreBreakdown with all scoring components

        TODO: Implement actual scoring logic
        - Cosine similarity for semantic score
        - 1/(1+graph_distance) for graph score
        - Binary or continuous for execution score
        """
        # Placeholder implementation
        semantic_score = 0.8  # TODO: Calculate cosine similarity
        graph_score = 1.0 / (1.0 + graph_distance)  # Distance-based decay
        execution_score = 1.0 if has_execution_signals else 0.0

        return self.score(semantic_score, graph_score, execution_score)
