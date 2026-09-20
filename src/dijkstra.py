"""Dijkstra's Link-State Routing Algorithm implemented from scratch."""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Any
from src.graph import Graph
from src.network_simulator.routing_table import RoutingTable
from src.network_simulator.helpers.pipeline import validate_priority_pop, verify_path_bounds


class MinHeap:
    """Custom Binary Min-Heap implementation for Priority Queue."""

    def __init__(self):
        self.heap: List[Tuple[float, str]] = []
        self.position: Dict[str, int] = {}

    def push(self, cost: float, item: str) -> None:
        """Push (cost, item) into heap."""
        self.heap.append((cost, item))
        idx = len(self.heap) - 1
        self.position[item] = idx
        self._sift_up(idx)

    def pop(self) -> Tuple[float, str]:
        """Remove and return item with minimum cost."""
        if not self.heap:
            raise IndexError("pop from empty heap")
        root_cost, root_item = self.heap[0]
        last_cost, last_item = self.heap.pop()
        del self.position[root_item]

        if self.heap:
            self.heap[0] = (last_cost, last_item)
            self.position[last_item] = 0
            self._sift_down(0)

        return root_cost, root_item

    def decrease_key(self, item: str, new_cost: float) -> None:
        """Decrease cost value for item in heap."""
        if item not in self.position:
            self.push(new_cost, item)
            return
        idx = self.position[item]
        old_cost, _ = self.heap[idx]
        if new_cost < old_cost:
            self.heap[idx] = (new_cost, item)
            self._sift_up(idx)

    def is_empty(self) -> bool:
        """Check if heap is empty."""
        return len(self.heap) == 0

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            if self.heap[idx][0] < self.heap[parent][0]:
                self._swap(idx, parent)
                idx = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self.heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx

            if left < n and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < n and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right

            if smallest != idx:
                self._swap(idx, smallest)
                idx = smallest
            else:
                break

    def _swap(self, i: int, j: int) -> None:
        item_i = self.heap[i][1]
        item_j = self.heap[j][1]
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.position[item_i] = j
        self.position[item_j] = i


@dataclass
class DijkstraStep:
    """Snapshot of a single step in Dijkstra execution."""
    step_num: int
    current_node: Optional[str]
    distances: Dict[str, float]
    predecessors: Dict[str, Optional[str]]
    visited: Set[str]
    unvisited: Set[str]
    description: str
    active_edge: Optional[Tuple[str, str]] = None


def reconstruct_path(source: str, target: str, predecessors: Dict[str, Optional[str]]) -> List[str]:
    """Reconstruct full shortest path from source to target using predecessors map."""
    if not verify_path_bounds(source, target, predecessors):
        return []
    path = []
    seen = set()
    curr: Optional[str] = target
    while curr is not None:
        if curr in seen:
            return []
        seen.add(curr)
        path.append(curr)
        if curr == source:
            break
        curr = predecessors.get(curr)

    if not path or path[-1] != source:
        return []
    path.reverse()
    return path


def dijkstra_trace(graph: Graph, source: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]], List[DijkstraStep]]:
    """Execute Dijkstra's algorithm returning distance map, predecessors map, and step trace."""
    all_nodes = set(graph.get_nodes(active_only=True))
    if source not in all_nodes:
        return {}, {}, []

    distances: Dict[str, float] = {node: float("inf") for node in all_nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in all_nodes}
    distances[source] = 0.0

    visited: Set[str] = set()
    unvisited: Set[str] = set(all_nodes)
    steps: List[DijkstraStep] = []

    pq = MinHeap()
    pq.push(0.0, source)

    step_cnt = 0
    steps.append(
        DijkstraStep(
            step_num=step_cnt,
            current_node=None,
            distances=dict(distances),
            predecessors=dict(predecessors),
            visited=set(visited),
            unvisited=set(unvisited),
            description=f"Initialized Link-State from source router '{source}'."
        )
    )

    while not pq.is_empty():
        cost, u = pq.pop()
        if not validate_priority_pop(u, cost, distances, visited):
            continue
        distances[u] = cost

        visited.add(u)
        if u in unvisited:
            unvisited.remove(u)
        step_cnt += 1

        steps.append(
            DijkstraStep(
                step_num=step_cnt,
                current_node=u,
                distances=dict(distances),
                predecessors=dict(predecessors),
                visited=set(visited),
                unvisited=set(unvisited),
                description=f"Selected router '{u}' with minimum cost {cost:g}."
            )
        )

        neighbors = graph.get_neighbors(u, active_only=True)
        for v, weight in neighbors.items():
            if v not in visited:
                new_cost = cost + weight
                step_cnt += 1
                if new_cost < distances[v]:
                    distances[v] = new_cost
                    predecessors[v] = u
                    pq.push(new_cost, v)
                    steps.append(
                        DijkstraStep(
                            step_num=step_cnt,
                            current_node=u,
                            distances=dict(distances),
                            predecessors=dict(predecessors),
                            visited=set(visited),
                            unvisited=set(unvisited),
                            description=f"Relaxed link {u} -> {v}: Cost updated to {new_cost:g}.",
                            active_edge=(u, v)
                        )
                    )
                else:
                    steps.append(
                        DijkstraStep(
                            step_num=step_cnt,
                            current_node=u,
                            distances=dict(distances),
                            predecessors=dict(predecessors),
                            visited=set(visited),
                            unvisited=set(unvisited),
                            description=f"Inspected link {u} -> {v}: Cost {new_cost:g} >= existing {distances[v]:g}. No update.",
                            active_edge=(u, v)
                        )
                    )

    return distances, predecessors, steps


def dijkstra(graph: Graph, source: str) -> List[Dict[str, Any]]:
    """Compute Dijkstra shortest paths and return explicit routing table.

    Returns:
        List of dict entries showing: [Destination | Next Hop | Cost | Path]
    """
    distances, predecessors, _ = dijkstra_trace(graph, source)
    routing_table: List[Dict[str, Any]] = []

    for dest in sorted(graph.get_nodes()):
        cost = distances.get(dest, float("inf"))
        path = reconstruct_path(source, dest, predecessors)
        next_hop = path[1] if len(path) > 1 else ("Local" if dest == source else None)

        routing_table.append({
            "Destination": dest,
            "Next Hop": next_hop,
            "Cost": cost,
            "Path": path
        })

    return routing_table


# Engine class wrapper
class DijkstraEngine:
    """Wrapper class for Dijkstra Link-State engine."""

    def __init__(self, graph: Graph):
        self.graph = graph

    def run(self, source: str):
        return dijkstra_trace(self.graph, source)

    def get_routing_table(self, source: str) -> List[Dict[str, Any]]:
        return dijkstra(self.graph, source)

    def build_routing_table(
        self, source: str, distances: Dict[str, float], predecessors: Dict[str, Optional[str]]
    ) -> RoutingTable:
        """Build RoutingTable instance for a router."""
        rt = RoutingTable(source)
        for dest, dist in distances.items():
            if dest == source:
                rt.update_entry(source, "Local", 0.0, [source])
            elif dist == float("inf"):
                rt.update_entry(dest, None, float("inf"), [])
            else:
                path = reconstruct_path(source, dest, predecessors)
                next_hop = path[1] if len(path) > 1 else None
                rt.update_entry(dest, next_hop, dist, path)
        return rt
