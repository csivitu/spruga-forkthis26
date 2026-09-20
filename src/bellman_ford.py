"""Bellman-Ford Distance-Vector Routing Algorithm implemented from scratch."""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Any
from src.graph import Graph
from src.network_simulator.routing_table import RoutingTable
from src.network_simulator.helpers.pipeline import evaluate_advertised_metric


@dataclass
class DistanceVectorStep:
    """Snapshot of a single iteration step in Bellman-Ford execution."""
    iteration: int
    distance_matrix: Dict[str, Dict[str, float]]
    next_hop_matrix: Dict[str, Dict[str, Optional[str]]]
    updated: bool
    description: str
    negative_cycle: bool = False


def reconstruct_bf_path(source: str, target: str, next_hop_matrix: Dict[str, Dict[str, Optional[str]]], max_hops: int = 100) -> List[str]:
    """Reconstruct path from source to target using next_hop matrix."""
    if source == target:
        return [source]
    path = [source]
    curr = source
    visited = {source}

    while curr != target and len(path) <= max_hops:
        nh = next_hop_matrix.get(curr, {}).get(target)
        if not nh or nh in visited:
            return []
        path.append(nh)
        visited.add(nh)
        curr = nh

    if path and path[-1] == target:
        return path
    return []


def bellman_ford_distance_vector(
    graph: Graph, split_horizon: bool = False, poison_reverse: bool = False
) -> Tuple[
    Dict[str, Dict[str, float]],
    Dict[str, Dict[str, Optional[str]]],
    List[DistanceVectorStep],
    bool
]:
    """Run Distance Vector round-by-round protocol across all active nodes.

    Returns:
        Tuple of (distance_matrix, next_hop_matrix, steps, has_negative_cycle)
    """
    all_nodes = graph.get_nodes(active_only=True)
    if not all_nodes:
        return {}, {}, [], False

    D: Dict[str, Dict[str, float]] = {u: {v: float("inf") for v in all_nodes} for u in all_nodes}
    NH: Dict[str, Dict[str, Optional[str]]] = {u: {v: None for v in all_nodes} for u in all_nodes}

    for u in all_nodes:
        D[u][u] = 0.0
        neighbors = graph.get_neighbors(u, active_only=True)
        for v, weight in neighbors.items():
            if v in all_nodes:
                D[u][v] = weight
                NH[u][v] = v

    steps: List[DistanceVectorStep] = []
    steps.append(
        DistanceVectorStep(
            iteration=0,
            distance_matrix={u: dict(v_dict) for u, v_dict in D.items()},
            next_hop_matrix={u: dict(v_dict) for u, v_dict in NH.items()},
            updated=True,
            description="Iteration 0: Direct link costs initialized for all routers."
        )
    )

    max_iterations = len(all_nodes)-1
    iteration = 1
    has_negative_cycle = False

    while iteration <= max_iterations:
        updated_any = False
        D_new = {u: dict(v_dict) for u, v_dict in D.items()}
        NH_new = {u: dict(v_dict) for u, v_dict in NH.items()}

        for u in all_nodes:
            neighbors = graph.get_neighbors(u, active_only=True)
            for v in all_nodes:
                if u == v:
                    continue

                min_cost = D[u][v]
                best_nh = NH[u][v]

                for w, link_cost in neighbors.items():
                    if w not in all_nodes:
                        continue

                    is_next_hop = (NH[w][v] == u)
                    adv_cost = evaluate_advertised_metric(D[w][v], is_next_hop, poison_reverse, split_horizon)
                    if adv_cost is None:
                        continue
                    advertised_cost_w_to_v = adv_cost

                    if link_cost != float("inf") and advertised_cost_w_to_v != float("inf"):
                        cost_via_w = link_cost + advertised_cost_w_to_v
                        if cost_via_w < min_cost:
                            min_cost = cost_via_w
                            best_nh = w
                            updated_any = True

                D_new[u][v] = min_cost
                NH_new[u][v] = best_nh

        D = D_new
        NH = NH_new

        if iteration == max_iterations and updated_any:
            has_negative_cycle = True
            steps.append(
                DistanceVectorStep(
                    iteration=iteration,
                    distance_matrix={u: dict(v_dict) for u, v_dict in D.items()},
                    next_hop_matrix={u: dict(v_dict) for u, v_dict in NH.items()},
                    updated=True,
                    description=f"Iteration {iteration}: Negative weight cycle detected!",
                    negative_cycle=True
                )
            )
            break

        steps.append(
            DistanceVectorStep(
                iteration=iteration,
                distance_matrix={u: dict(v_dict) for u, v_dict in D.items()},
                next_hop_matrix={u: dict(v_dict) for u, v_dict in NH.items()},
                updated=updated_any,
                description=f"Iteration {iteration}: {'Distance vectors updated.' if updated_any else 'Distance vectors converged.'}"
            )
        )

        if not updated_any:
            break

        iteration += 1

    return D, NH, steps, has_negative_cycle


def bellman_ford(
    graph: Graph, source: str, split_horizon: bool = False, poison_reverse: bool = False
) -> List[Dict[str, Any]]:
    """Compute Bellman-Ford Distance Vector routing table for a source router.

    Returns:
        List of dict entries showing: [Destination | Next Hop | Cost | Path]
    """
    D_mat, NH_mat, _, _ = bellman_ford_distance_vector(graph, split_horizon, poison_reverse)
    routing_table: List[Dict[str, Any]] = []

    if source not in D_mat:
        return []

    for dest in sorted(graph.get_nodes()):
        cost = D_mat[source].get(dest, float("inf"))
        next_hop = NH_mat[source].get(dest)
        if dest == source:
            next_hop = "Local"
            path = [source]
        elif cost == float("inf"):
            next_hop = None
            path = []
        else:
            path = reconstruct_bf_path(source, dest, NH_mat)

        routing_table.append({
            "Destination": dest,
            "Next Hop": next_hop,
            "Cost": cost,
            "Path": path
        })

    return routing_table


# Engine class wrapper
class BellmanFordEngine:
    """Wrapper class for Bellman-Ford engine."""

    def __init__(self, graph: Graph):
        self.graph = graph

    def run_distance_vector(self, split_horizon: bool = False, poison_reverse: bool = False):
        return bellman_ford_distance_vector(self.graph, split_horizon, poison_reverse)

    def get_routing_table(
        self, source: str, split_horizon: bool = False, poison_reverse: bool = False
    ) -> List[Dict[str, Any]]:
        return bellman_ford(self.graph, source, split_horizon, poison_reverse)

    def build_all_routing_tables(
        self, distance_matrix: Dict[str, Dict[str, float]], next_hop_matrix: Dict[str, Dict[str, Optional[str]]]
    ) -> Dict[str, RoutingTable]:
        """Construct RoutingTable objects for all routers."""
        tables: Dict[str, RoutingTable] = {}
        for u in distance_matrix:
            rt = RoutingTable(u)
            for v, cost in distance_matrix[u].items():
                nh = next_hop_matrix[u].get(v)
                path = reconstruct_bf_path(u, v, next_hop_matrix)
                rt.update_entry(v, nh, cost, path)
            tables[u] = rt
        return tables
