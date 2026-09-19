"""Dynamic Network Event Simulator.

Simulates real-time network events (link cuts, link recovery, link cost updates,
router failure, router restoration) and tracks convergence step counts and routing table updates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict, Optional, Any
from src.network_simulator.graph import NetworkGraph
from src.network_simulator.algorithms import DijkstraEngine, BellmanFordEngine
from src.network_simulator.routing_table import RoutingTable


class EventType(Enum):
    LINK_DOWN = "LINK_DOWN"
    LINK_UP = "LINK_UP"
    COST_CHANGE = "COST_CHANGE"
    NODE_DOWN = "NODE_DOWN"
    NODE_UP = "NODE_UP"


@dataclass
class NetworkEvent:
    """Dataclass representing a network dynamic event."""
    event_type: EventType
    u: str
    v: Optional[str] = None
    new_cost: Optional[float] = None
    description: str = ""

    def __repr__(self) -> str:
        return f"Event[{self.event_type.value}: {self.description}]"


@dataclass
class EventSimulationResult:
    """Result summary of dynamic event execution on network routing."""
    event: NetworkEvent
    dijkstra_steps: int
    bellman_ford_iterations: int
    bf_converged: bool
    dijkstra_routing_tables: Dict[str, RoutingTable]
    bellman_ford_routing_tables: Dict[str, RoutingTable]
    log_summary: str


class NetworkEventSimulator:
    """Manages dynamic network events and tracks re-convergence metrics."""

    def __init__(self, graph: NetworkGraph):
        self.graph = graph
        self.event_history: List[NetworkEvent] = []

    def trigger_event(
        self, event: NetworkEvent, split_horizon: bool = False, poison_reverse: bool = False
    ) -> EventSimulationResult:
        """Apply event to graph topology and measure re-convergence stats across both algorithms."""
        self._apply_event_to_graph(event)
        self.event_history.append(event)

        # 1. Run Dijkstra Link-State re-convergence from all active nodes
        dijkstra_eng = DijkstraEngine(self.graph)
        active_nodes = self.graph.get_nodes(active_only=True)
        total_dijkstra_steps = 0
        dijkstra_tables: Dict[str, RoutingTable] = {}

        for n in active_nodes:
            dist, pred, steps = dijkstra_eng.run(n)
            total_dijkstra_steps += len(steps)
            dijkstra_tables[n] = dijkstra_eng.build_routing_table(n, dist, pred)

        # 2. Run Bellman-Ford Distance Vector re-convergence across network
        bf_eng = BellmanFordEngine(self.graph)
        D, NH, bf_steps, has_neg_cycle = bf_eng.run_distance_vector(
            split_horizon=split_horizon, poison_reverse=poison_reverse
        )
        bf_tables = bf_eng.build_all_routing_tables(D, NH)

        num_bf_iterations = len(bf_steps)

        log_summary = (
            f"Applied '{event.event_type.value}': {event.description}. "
            f"Re-converged in {total_dijkstra_steps} Dijkstra steps and {num_bf_iterations} Distance Vector rounds."
        )

        return EventSimulationResult(
            event=event,
            dijkstra_steps=total_dijkstra_steps,
            bellman_ford_iterations=num_bf_iterations,
            bf_converged=not has_neg_cycle,
            dijkstra_routing_tables=dijkstra_tables,
            bellman_ford_routing_tables=bf_tables,
            log_summary=log_summary,
        )

    def _apply_event_to_graph(self, event: NetworkEvent) -> None:
        """Apply topology modifications to self.graph."""
        if event.event_type == EventType.LINK_DOWN and event.v:
            self.graph.set_edge_active(event.u, event.v, False)
        elif event.event_type == EventType.LINK_UP and event.v:
            self.graph.set_edge_active(event.u, event.v, True)
        elif event.event_type == EventType.COST_CHANGE and event.v and event.new_cost is not None:
            self.graph.set_edge_weight(event.u, event.v, event.new_cost)
        elif event.event_type == EventType.NODE_DOWN:
            self.graph.set_node_active(event.u, False)
        elif event.event_type == EventType.NODE_UP:
            self.graph.set_node_active(event.u, True)
