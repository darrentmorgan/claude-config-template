"""Query engine: Natural language → context pack."""

from code_graph.retrieval.embeddings import EmbeddingGenerator
from code_graph.retrieval.hybrid_scorer import HybridScorer
from code_graph.retrieval.graph_distance import GraphDistanceCalculator
from code_graph.retrieval.context_pack import ContextPackBuilder
from code_graph.models.context_pack import ContextPack


class QueryEngine:
    """Main query interface for code graph."""

    def __init__(self, graph):
        """Initialize query engine.

        Args:
            graph: GraphStore instance
        """
        self.graph = graph
        self.embeddings = EmbeddingGenerator()
        self.scorer = HybridScorer()
        self.distance_calc = GraphDistanceCalculator()
        self.pack_builder = ContextPackBuilder(graph)

    def query(self, query_text: str, top_n: int = 10) -> ContextPack:
        """Query code graph with natural language.

        Args:
            query_text: Natural language query
            top_n: Number of top results

        Returns:
            ContextPack with ranked results
        """
        # Generate query embedding
        query_emb = self.embeddings.encode(query_text)

        # Score all files (simplified for MVP)
        # TODO: Implement actual scoring logic

        # Build context pack
        return self.pack_builder.build(query_text, top_n)
