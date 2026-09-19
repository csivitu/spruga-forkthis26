"""Unit tests for NetworkEventSimulator."""

import pytest
from src.network_simulator.graph import NetworkGraph
from src.network_simulator.simulator import NetworkEventSimulator, NetworkEvent, EventType


def test_link_down_event():
    g = NetworkGraph(directed=False)
    g.add_edge("A", "B", weight=2.0)
    g.add_edge("B", "C", weight=3.0)
    g.add_edge("A", "C", weight=10.0)

    sim = NetworkEventSimulator(g)
    
    # Sever B-C link
    event = NetworkEvent(
        event_type=EventType.LINK_DOWN, u="B", v="C", description="Cut link B-C"
    )
    result = sim.trigger_event(event)

    assert not g.is_edge_active("B", "C")
    # Path from A to C must now re-route directly via A -> C with cost 10.0
    d_table = result.dijkstra_routing_tables["A"]
    assert d_table.get_entry("C").cost == 10.0
    assert d_table.get_entry("C").next_hop == "C"


def test_cost_change_event():
    g = NetworkGraph(directed=False)
    g.add_edge("A", "B", weight=10.0)
    g.add_edge("B", "C", weight=10.0)
    g.add_edge("A", "C", weight=100.0)

    sim = NetworkEventSimulator(g)
    
    # Lower A-C link cost to 1.0
    event = NetworkEvent(
        event_type=EventType.COST_CHANGE, u="A", v="C", new_cost=1.0, description="Upgrade link A-C"
    )
    result = sim.trigger_event(event)

    assert g.get_edge_weight("A", "C") == 1.0
    d_table = result.dijkstra_routing_tables["A"]
    assert d_table.get_entry("C").cost == 1.0


def test_topology_reset_state_isolation():
    from app import create_sample_mesh
    g1 = create_sample_mesh()
    g1.set_edge_active("Router_A", "Router_B", False)

    # Reload preset topology (Reset Topology action)
    g2 = create_sample_mesh()
    assert g2.is_edge_active("Router_A", "Router_B")

