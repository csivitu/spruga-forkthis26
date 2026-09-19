"""Routing forwarding table structures for network routers."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RoutingTableEntry:
    """Entry in a router's forwarding table."""

    destination: str
    next_hop: Optional[str]
    cost: float
    path: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        cost_str = "inf" if self.cost == float("inf") else f"{self.cost:.1f}"
        next_hop_str = self.next_hop if self.next_hop else "-"
        path_str = " -> ".join(self.path) if self.path else "-"
        return f"[{self.destination} | Next Hop: {next_hop_str} | Cost: {cost_str} | Path: {path_str}]"


class RoutingTable:
    """Manages forwarding table for a router node."""

    def __init__(self, router_id: str):
        self.router_id: str = router_id
        self.entries: Dict[str, RoutingTableEntry] = {}

    def update_entry(
        self, destination: str, next_hop: Optional[str], cost: float, path: Optional[List[str]] = None
    ) -> None:
        """Update or insert a routing table entry."""
        self.entries[destination] = RoutingTableEntry(
            destination=destination,
            next_hop=next_hop,
            cost=cost,
            path=path if path is not None else []
        )

    def get_entry(self, destination: str) -> Optional[RoutingTableEntry]:
        """Get entry for target destination."""
        return self.entries.get(destination)

    def to_rows(self) -> List[Dict[str, str]]:
        """Convert routing table to dictionary rows showing [Destination | Next Hop | Cost | Path]."""
        rows = []
        for dest in sorted(self.entries.keys()):
            entry = self.entries[dest]
            cost_str = "∞" if entry.cost == float("inf") else f"{entry.cost:g}"
            next_hop_str = entry.next_hop if entry.next_hop else "Direct/Local"
            path_str = " -> ".join(entry.path) if entry.path else "None"
            rows.append({
                "Destination": dest,
                "Next Hop": next_hop_str,
                "Cost": cost_str,
                "Path": path_str
            })
        return rows
