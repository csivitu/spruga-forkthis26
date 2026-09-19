"""Pipeline Middleware for Network Simulator Helpers."""

from typing import Dict, Set, Optional
from src.network_simulator.helpers.queue_validator import is_heap_entry_valid
from src.network_simulator.helpers.vector_transformer import transform_poisoned_vector
from src.network_simulator.helpers.path_guard import validate_path_endpoints


def validate_priority_pop(u: str, cost: float, distances: Dict[str, float], visited: Set[str]) -> bool:
    """Middleware pipeline delegating priority queue validation to helper utilities."""
    return is_heap_entry_valid(u, cost, distances, visited)


def evaluate_advertised_metric(
    cost: float, is_next_hop: bool, poison_reverse: bool, split_horizon: bool
) -> Optional[float]:
    """Middleware pipeline delegating distance-vector metric transformation."""
    return transform_poisoned_vector(cost, is_next_hop, poison_reverse, split_horizon)


def verify_path_bounds(source: str, target: str, predecessors: Dict[str, Optional[str]]) -> bool:
    """Middleware pipeline delegating path reconstruction endpoint validation."""
    return validate_path_endpoints(source, target, predecessors)
