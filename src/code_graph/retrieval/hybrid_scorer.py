"""Hybrid scorer: 0.4·semantic + 0.4·graph + 0.2·execution."""

from typing import Optional


class HybridScorer:
    """Combines semantic, graph, and execution signal scores."""

    def __init__(
        self,
        embedding_weight: float = 0.4,
        graph_weight: float = 0.4,
        signal_weight: float = 0.2
    ):
        """Initialize hybrid scorer.

        Args:
            embedding_weight: Weight for semantic similarity (default 0.4)
            graph_weight: Weight for graph proximity (default 0.4)
            signal_weight: Weight for execution signals (default 0.2)
        """
        self.embedding_weight = embedding_weight
        self.graph_weight = graph_weight
        self.signal_weight = signal_weight

    def calculate_score(
        self,
        embedding_similarity: float,
        graph_distance: float,
        execution_signal_score: Optional[float] = None
    ) -> float:
        """Calculate hybrid score.

        Args:
            embedding_similarity: Semantic similarity [0, 1]
            graph_distance: Graph distance (number of hops)
            execution_signal_score: Execution signal score [0, 1] or None

        Returns:
            Hybrid score [0, 1]
        """
        # Convert graph distance to proximity score: 1/(1+distance)
        graph_proximity = 1.0 / (1.0 + graph_distance)

        # If execution signals unavailable, fallback to 0.5·embedding + 0.5·graph
        if execution_signal_score is None:
            score = 0.5 * embedding_similarity + 0.5 * graph_proximity
        else:
            score = (
                self.embedding_weight * embedding_similarity +
                self.graph_weight * graph_proximity +
                self.signal_weight * execution_signal_score
            )

        return max(0.0, min(1.0, score))
