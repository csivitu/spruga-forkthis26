"""Unit tests for Graph class in src/graph.py."""

import pytest
from src.graph import Graph


def test_add_nodes_and_edges():
    g = Graph(directed=False)
    g.add_edge("A", "B", weight=5.0)

    assert "A" in g.get_nodes()
    assert "B" in g.get_nodes()
    assert g.get_neighbors("A")["B"] == 5.0
    assert g.get_neighbors("B")["A"] == 5.0


def test_link_disable_and_enable():
    g = Graph(directed=False)
    g.add_edge("A", "B", weight=3.0)

    assert g.is_edge_active("A", "B")
    g.set_edge_active("A", "B", False)
    assert not g.is_edge_active("A", "B")
    assert "B" not in g.get_neighbors("A", active_only=True)

    g.set_edge_active("A", "B", True)
    assert g.get_neighbors("A", active_only=True)["B"] == 3.0


def test_floating_point_metric_precision():
    """Verify link metric calculation precision under floating point arithmetic."""
    from src.graph import compute_composite_metric
    metric = compute_composite_metric(0.1, 5.0)
    assert metric == 0.3, f"Expected metric 0.3, but got {metric}!"

