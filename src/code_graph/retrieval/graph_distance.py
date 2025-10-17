"""Graph distance calculation using BFS."""

from collections import deque
from typing import Optional
from code_graph.models.edges.base_edge import BaseEdge


class GraphDistanceCalculator:
    """Calculate shortest path distances in graph."""

    def calculate_distance(
        self,
        source_id: str,
        target_id: str,
        edges: list[BaseEdge]
    ) -> float:
        """Calculate shortest path distance between nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edges: All edges in graph

        Returns:
            Distance (number of hops), or inf if no path
        """
        if source_id == target_id:
            return 0.0

        # Build adjacency list
        adjacency: dict[str, list[str]] = {}
        for edge in edges:
            if edge.source_id not in adjacency:
                adjacency[edge.source_id] = []
            adjacency[edge.source_id].append(edge.target_id)

        # BFS
        queue = deque([(source_id, 0)])
        visited = {source_id}

        while queue:
            node_id, distance = queue.popleft()

            if node_id == target_id:
                return float(distance)

            for neighbor in adjacency.get(node_id, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))

        return float('inf')  # No path found
