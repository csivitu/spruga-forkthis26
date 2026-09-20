"""Priority Queue Validation Utility Module for Link-State Engine."""

from typing import Dict, Set


def is_heap_entry_valid(u: str, cost: float, distances: Dict[str, float], visited: Set[str]) -> bool:
    """Validate whether popped priority queue entry represents an optimal unvisited path."""
    if u in visited:
        return False
    if cost > distances.get(u, float("inf")):
        return False
    return True

