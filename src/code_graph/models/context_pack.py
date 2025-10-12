"""ContextPack model representing a retrieval result for a query."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    """Breakdown of hybrid scoring components."""

    semantic_score: float = Field(..., ge=0.0, le=1.0, description="Embedding similarity")
    graph_score: float = Field(..., ge=0.0, le=1.0, description="Graph proximity")
    execution_score: float = Field(..., ge=0.0, le=1.0, description="Execution signals")
    hybrid_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.4*semantic + 0.4*graph + 0.2*execution",
    )

    @staticmethod
    def calculate_hybrid(semantic: float, graph: float, execution: float) -> float:
        """Calculate hybrid score using weighted formula."""
        return 0.4 * semantic + 0.4 * graph + 0.2 * execution


class NodeReference(BaseModel):
    """Reference to a code element within a file."""

    node_id: str
    node_type: str  # FileNode, ModuleNode, ClassNode, FunctionNode, TestNode
    name: str
    qualified_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    score_breakdown: ScoreBreakdown


class FileReference(BaseModel):
    """Reference to a file in the retrieval result."""

    file_path: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., description="Why this file was selected")
    related_nodes: list[NodeReference] = Field(default_factory=list)


class ContextPack(BaseModel):
    """Represents a retrieval result for a query.

    Attributes:
        query: Original natural language query
        files: List of relevant files with rationales
        total_confidence: Weighted average confidence
        retrieval_timestamp: When the query was executed
        max_hops: How many relationship hops were explored
    """

    query: str
    files: list[FileReference]
    total_confidence: float = Field(..., ge=0.0, le=1.0)
    retrieval_timestamp: datetime
    max_hops: int = Field(..., ge=1)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "query": "add email validation to user registration",
                "files": [
                    {
                        "file_path": "src/auth/register.py",
                        "relevance_score": 0.92,
                        "rationale": "Contains register_user() function",
                        "related_nodes": [
                            {
                                "node_id": "fn_abc123",
                                "node_type": "FunctionNode",
                                "name": "register_user",
                                "qualified_name": "auth.register.register_user",
                                "score": 0.92,
                                "score_breakdown": {
                                    "semantic_score": 0.85,
                                    "graph_score": 0.95,
                                    "execution_score": 0.0,
                                    "hybrid_score": 0.72,
                                },
                            }
                        ],
                    }
                ],
                "total_confidence": 0.90,
                "retrieval_timestamp": "2025-10-12T11:00:00Z",
                "max_hops": 2,
            }
        }
