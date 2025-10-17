"""Context pack builder: Assemble retrieval results with rationales."""

from dataclasses import dataclass
from datetime import datetime
from code_graph.models.context_pack import ContextPack, FileReference


@dataclass
class ScoredFile:
    """File with calculated scores."""
    path: str
    score: float
    rationale: str


class ContextPackBuilder:
    """Builds context packs from query results."""

    def __init__(self, graph):
        """Initialize context pack builder.

        Args:
            graph: GraphStore instance
        """
        self.graph = graph

    def build(self, query: str, top_n: int = 10, max_hops: int = 2) -> ContextPack:
        """Build context pack for query.

        Args:
            query: Natural language query
            top_n: Number of top results to include
            max_hops: Maximum relationship hops explored (default: 2)

        Returns:
            ContextPack with ranked files and rationales
        """
        # For MVP, get all files from graph and create basic rationales
        scored_files: list[ScoredFile] = []

        for file_id, file_node in self.graph.files.items():
            # Simple placeholder scoring based on file path matching query terms
            query_lower = query.lower()
            path_lower = file_node.path.lower()

            # Basic keyword matching for relevance
            score = 0.5  # Default score
            if any(term in path_lower for term in ['auth', 'user', 'login', 'register'] if term in query_lower):
                score = 0.8
            elif any(term in path_lower for term in ['valid', 'email'] if term in query_lower):
                score = 0.9

            scored_files.append(ScoredFile(
                path=file_node.path,
                score=score,
                rationale=f"File matches query terms: {file_node.path}"
            ))

        # Take top N
        top_files = sorted(scored_files, key=lambda f: f.score, reverse=True)[:top_n]

        # Build context pack
        file_refs = [
            FileReference(
                file_path=f.path,
                relevance_score=f.score,
                rationale=f.rationale,
                related_nodes=[]  # MVP: empty for now
            )
            for f in top_files
        ]

        # Calculate total confidence as average of file scores
        total_confidence = sum(f.score for f in top_files) / len(top_files) if top_files else 0.0

        return ContextPack(
            query=query,
            files=file_refs,
            total_confidence=total_confidence,
            retrieval_timestamp=datetime.now(),
            max_hops=max_hops
        )
