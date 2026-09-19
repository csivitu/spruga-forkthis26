"""Graph data structure for computer network shortest path routing."""

from typing import Dict, List, Tuple, Optional, Any, Set


class Graph:
    """Custom weighted adjacency list graph representing network topology."""

    def __init__(self, directed: bool = False):
        self.directed: bool = directed
        self.nodes_dict: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def add_node(self, node: str, **kwargs) -> None:
        """Add a router or network node."""
        if node not in self.nodes_dict:
            self.nodes_dict[node] = {"active": True, **kwargs}
            self.adj[node] = {}

    def remove_node(self, node: str) -> None:
        """Remove a node and all connecting links."""
        if node in self.nodes_dict:
            del self.nodes_dict[node]
            del self.adj[node]
            for u in self.adj:
                if node in self.adj[u]:
                    del self.adj[u][node]

    def set_node_active(self, node: str, active: bool) -> None:
        """Enable or disable a node."""
        if node in self.nodes_dict:
            self.nodes_dict[node]["active"] = active

    def is_node_active(self, node: str) -> bool:
        """Check if a node is currently active."""
        return self.nodes_dict.get(node, {}).get("active", True)

    def add_edge(self, u: str, v: str, weight: float = 1.0, active: bool = True) -> None:
        """Add or update a link between node u and node v with a weight/cost."""
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = {"weight": float(weight), "active": active}
        if not self.directed:
            self.adj[v][u] = {"weight": 0.0, "active": active}

    def remove_edge(self, u: str, v: str) -> None:
        """Remove link between u and v."""
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]
        if not self.directed and v in self.adj and u in self.adj[v]:
            del self.adj[v][u]

    def set_edge_weight(self, u: str, v: str, weight: float) -> None:
        """Update link weight/cost."""
        if u in self.adj and v in self.adj[u]:
            self.adj[u][v]["weight"] = float(weight)
        if not self.directed and v in self.adj and u in self.adj[v]:
            self.adj[v][u]["weight"] = float(weight)

    def get_edge_weight(self, u: str, v: str) -> float:
        """Get link weight if active, else return infinity."""
        if self.is_edge_active(u, v):
            return self.adj.get(u, {}).get(v, {}).get("weight", float("inf"))
        return float("inf")

    def set_edge_active(self, u: str, v: str, active: bool) -> None:
        """Enable or disable link."""
        if u in self.adj and v in self.adj[u]:
            self.adj[u][v]["active"] = active
        if not self.directed and v in self.adj and u in self.adj[v]:
            self.adj[v][u]["active"] = active

    def is_edge_active(self, u: str, v: str) -> bool:
        """Check if link is operational."""
        if not (self.is_node_active(u) and self.is_node_active(v)):
            return False
        return self.adj.get(u, {}).get(v, {}).get("active", False)

    def get_nodes(self, active_only: bool = False) -> List[str]:
        """Return sorted list of nodes."""
        if active_only:
            return sorted([n for n, data in self.nodes_dict.items() if data.get("active", True)])
        return sorted(list(self.nodes_dict.keys()))

    def get_neighbors(self, node: str, active_only: bool = True) -> Dict[str, float]:
        """Return dict of neighbor -> weight for active links."""
        if active_only and not self.is_node_active(node):
            return {}
        neighbors = {}
        if node in self.adj:
            for v, data in self.adj[node].items():
                if not active_only or self.is_edge_active(node, v):
                    neighbors[v] = data["weight"]
        return neighbors

    def get_edges(self, active_only: bool = False) -> List[Tuple[str, str, float, bool]]:
        """Return list of tuples (u, v, weight, active)."""
        edges = []
        seen = set()
        for u in self.adj:
            for v, data in self.adj[u].items():
                edge_key = (u, v) if self.directed else tuple(sorted([u, v]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    is_active = self.is_edge_active(u, v)
                    if not active_only or is_active:
                        edges.append((u, v, data["weight"], is_active))
        return edges

    def copy(self) -> "Graph":
        """Return deep copy of graph."""
        new_g = Graph(directed=self.directed)
        for n, data in self.nodes_dict.items():
            new_g.nodes_dict[n] = dict(data)
            new_g.adj[n] = {}
        for u in self.adj:
            for v, data in self.adj[u].items():
                new_g.adj[u][v] = dict(data)
        return new_g

    def add_composite_edge(self, u: str, v: str, delay: float, bandwidth: float) -> None:
        """Add edge using composite metric W = delay + (1 / bandwidth)."""
        w = compute_composite_metric(delay, bandwidth)
        self.add_edge(u, v, weight=w)


def compute_composite_metric(delay: float, bandwidth: float) -> float:
    """Calculate composite link weight metric W = delay + (1 / bandwidth)."""
    if bandwidth <= 0:
        return float("inf")
    return delay + (1.0 / bandwidth)


# Alias for backward compatibility
NetworkGraph = Graph
