"""Unit tests for graph distance calculation.

Tests BFS shortest path calculations.
"""

import pytest
from code_graph.retrieval.graph_distance import GraphDistanceCalculator
from code_graph.models.edges.base_edge import BaseEdge, EdgeType


class TestGraphDistance:
    """Test graph distance calculations."""

    @pytest.fixture
    def calculator(self):
        """Create distance calculator."""
        return GraphDistanceCalculator()

    def test_direct_connection(self, calculator):
        """Test distance between directly connected nodes."""
        # A -> B
        edges = [
            BaseEdge(
                id="e1",
                type=EdgeType.CALLS,
                source_id="node_a",
                target_id="node_b",
                confidence=1.0
            )
        ]

        distance = calculator.calculate_distance(
            source_id="node_a",
            target_id="node_b",
            edges=edges
        )

        assert distance == 1

    def test_two_hop_distance(self, calculator):
        """Test distance across 2 hops."""
        # A -> B -> C
        edges = [
            BaseEdge(id="e1", type=EdgeType.CALLS, source_id="node_a", target_id="node_b", confidence=1.0),
            BaseEdge(id="e2", type=EdgeType.CALLS, source_id="node_b", target_id="node_c", confidence=1.0),
        ]

        distance = calculator.calculate_distance(
            source_id="node_a",
            target_id="node_c",
            edges=edges
        )

        assert distance == 2

    def test_no_path(self, calculator):
        """Test distance when no path exists."""
        edges = [
            BaseEdge(id="e1", type=EdgeType.CALLS, source_id="node_a", target_id="node_b", confidence=1.0),
        ]

        distance = calculator.calculate_distance(
            source_id="node_a",
            target_id="node_z",  # Not connected
            edges=edges
        )

        assert distance == float('inf')  # No path
