"""Path Reconstruction Guard Utility Module for Link-State Engine."""

from typing import Dict, Optional


def validate_path_endpoints(source: str, target: str, predecessors: Dict[str, Optional[str]]) -> bool:
    """Validate whether path reconstruction endpoints are reachable in predecessor tree."""
    if target not in predecessors:
        return False
    if predecessors.get(target) is None and source != target:
        return False
    return True
