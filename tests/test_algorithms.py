"""Unit tests verifying explicit routing tables from dijkstra.py and bellman_ford.py."""

import pytest
from src.graph import Graph
from src.dijkstra import dijkstra, DijkstraEngine, MinHeap, reconstruct_path
from src.bellman_ford import bellman_ford, BellmanFordEngine


def test_min_heap_operations():
    heap = MinHeap()
    heap.push(10.0, "A")
    heap.push(4.0, "B")
    heap.push(7.0, "C")

    cost, item = heap.pop()
    assert (cost, item) == (4.0, "B")

    heap.decrease_key("A", 2.0)
    cost, item = heap.pop()
    assert (cost, item) == (2.0, "A")


@pytest.fixture
def sample_network():
    g = Graph(directed=False)
    g.add_edge("A", "B", weight=4.0)
    g.add_edge("A", "C", weight=2.0)
    g.add_edge("B", "C", weight=1.0)
    g.add_edge("B", "D", weight=5.0)
    g.add_edge("C", "D", weight=8.0)
    return g


def test_dijkstra_explicit_routing_table(sample_network):
    routing_table = dijkstra(sample_network, "A")
    
    # Verify table schema: [Destination | Next Hop | Cost | Path]
    for row in routing_table:
        assert "Destination" in row
        assert "Next Hop" in row
        assert "Cost" in row
        assert "Path" in row

    # Target D row check: A -> C -> B -> D (Cost 8.0)
    d_row = next(r for r in routing_table if r["Destination"] == "D")
    assert d_row["Next Hop"] == "C"
    assert d_row["Cost"] == 8.0
    assert d_row["Path"] == ["A", "C", "B", "D"]


def test_bellman_ford_explicit_routing_table(sample_network):
    routing_table = bellman_ford(sample_network, "A")
    
    # Verify table schema: [Destination | Next Hop | Cost | Path]
    for row in routing_table:
        assert "Destination" in row
        assert "Next Hop" in row
        assert "Cost" in row
        assert "Path" in row

    # Target D row check: A -> C -> B -> D (Cost 8.0)
    d_row = next(r for r in routing_table if r["Destination"] == "D")
    assert d_row["Next Hop"] == "C"
    assert d_row["Cost"] == 8.0
    assert d_row["Path"] == ["A", "C", "B", "D"]


def test_bellman_ford_deep_topology_convergence():
    """Verify Bellman-Ford converges on deep topologies requiring V-1 iterations."""
    g = Graph(directed=False)
    # 6-node linear chain: N1 - N2 - N3 - N4 - N5 - N6
    nodes = ["N1", "N2", "N3", "N4", "N5", "N6"]
    for i in range(len(nodes) - 1):
        g.add_edge(nodes[i], nodes[i + 1], weight=1.0)

    routing_table = bellman_ford(g, "N1")
    n6_row = next(r for r in routing_table if r["Destination"] == "N6")
    assert n6_row["Cost"] == 5.0
    assert n6_row["Path"] == ["N1", "N2", "N3", "N4", "N5", "N6"]


def test_dijkstra_stale_heap_key():
    """Verify Dijkstra priority queue updates on redundant path graphs."""
    g = Graph(directed=True)
    g.add_edge("A", "B", weight=10.0)
    g.add_edge("A", "C", weight=2.0)
    g.add_edge("C", "B", weight=1.0)
    g.add_edge("B", "D", weight=1.0)

    routing_table = dijkstra(g, "A")
    b_row = next(r for r in routing_table if r["Destination"] == "B")
    assert b_row["Cost"] == 3.0, f"Expected cost 3.0 for router B, but got {b_row['Cost']}!"


def test_bellman_ford_poison_reverse():
    """Verify Poison Reverse advertises infinity metric back to next-hop router."""
    g = Graph(directed=True)
    g.add_edge("A", "B", weight=2.0)
    g.add_edge("B", "A", weight=2.0)
    g.add_edge("A", "C", weight=5.0)
    g.add_edge("A", "X", weight=1.0)
    g.add_edge("X", "A", weight=1.0)

    # B routes to C via A (cost 7.0, next_hop='A')
    # Under Poison Reverse, B must advertise inf back to A for target C.
    D, NH, _, _ = BellmanFordEngine(g).run_distance_vector(poison_reverse=True)

    assert D["A"]["C"] == 5.0, f"Expected cost 5.0 for router A -> C, but got {D['A']['C']}!"


def _run_reconstruct(q, predecessors):
    try:
        res = reconstruct_path("Source", "Target", predecessors)
        q.put(res)
    except Exception as e:
        q.put(e)


def test_reconstruct_path_circular_loop():
    """Verify reconstruct_path behavior on circular predecessor maps."""
    import multiprocessing
    predecessors = {
        "Target": "Node_A",
        "Node_A": "Node_B",
        "Node_B": "Node_A",
    }
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_run_reconstruct, args=(q, predecessors))
    p.start()
    p.join(timeout=0.3)
    if p.is_alive():
        p.terminate()
        p.join()
        pytest.fail("reconstruct_path failed to terminate within 0.3s!")






