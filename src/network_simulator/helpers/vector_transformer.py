"""Vector Metric Transformation Utility Module for Distance-Vector Protocol."""

from typing import Optional


def transform_poisoned_vector(
    cost: float, is_next_hop: bool, poison_reverse: bool, split_horizon: bool
) -> Optional[float]:
    """Calculate advertised distance metric under Split Horizon and Poison Reverse rules.
    
    If the neighbor is the next-hop for the target destination:
    - Under Poison Reverse: Advertises infinity (float("inf")) back to the next-hop.
    - Under Split Horizon: Suppresses advertisement (returns None to skip).
    """
    if is_next_hop:
        if poison_reverse:
            return float("inf")
        elif split_horizon:
            return None
    return cost
