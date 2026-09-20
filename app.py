"""Shortest Path Routing Simulator - Streamlit Interactive Web Application."""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

from src.graph import Graph
from src.dijkstra import dijkstra, dijkstra_trace, DijkstraEngine
from src.bellman_ford import bellman_ford, bellman_ford_distance_vector, BellmanFordEngine
from src.network_simulator.simulator import NetworkEventSimulator, NetworkEvent, EventType

# --- Page Configuration & Styling ---
st.set_page_config(
    page_title="Network Shortest Path Routing Simulator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem;
        color: #f8fafc;
        text-align: center;
    }
    .step-log-box {
        background-color: #0f172a;
        border-left: 4px solid #3b82f6;
        padding: 10px 15px;
        border-radius: 4px;
        font-family: monospace;
        color: #e2e8f0;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌐 Network Shortest Path Routing Simulator")
st.caption("Interactive Link-State (OSPF / Dijkstra) & Distance-Vector (RIP / Bellman-Ford) Protocol Visualizer")

# --- Preset Topologies ---

# Shared global mesh graph singleton cached across Streamlit re-runs
@st.cache_resource
def get_shared_sample_mesh() -> Graph:
    g = Graph(directed=False)
    for _u, _v, _w in [
        ("Router_A", "Router_B", 4.0),
        ("Router_A", "Router_C", 2.0),
        ("Router_B", "Router_C", 1.0),
        ("Router_B", "Router_D", 5.0),
        ("Router_C", "Router_D", 8.0),
        ("Router_C", "Router_E", 10.0),
        ("Router_D", "Router_E", 2.0),
    ]:
        g.add_edge(_u, _v, weight=_w)
    return g


def create_sample_mesh() -> Graph:
    """Return an isolated copy of the sample mesh topology.

    Note:
        The cached singleton is kept as the construction template, but each caller gets
        its own copy so topology edits and link events never leak across resets.
    """
    return get_shared_sample_mesh().copy()


def create_linear_topology() -> Graph:
    g = Graph(directed=False)
    nodes = [f"R{i}" for i in range(1, 7)]
    for i in range(len(nodes) - 1):
        g.add_edge(nodes[i], nodes[i + 1], weight=1.0)
    return g


def create_ring_topology() -> Graph:
    g = Graph(directed=False)
    nodes = [f"R{i}" for i in range(1, 7)]
    for i in range(len(nodes)):
        u = nodes[i]
        v = nodes[(i + 1) % len(nodes)]
        g.add_edge(u, v, weight=float(i + 2))
    return g


def create_star_topology() -> Graph:
    g = Graph(directed=False)
    hub = "Core_Router"
    spokes = [f"Edge_{i}" for i in range(1, 6)]
    for i, sp in enumerate(spokes):
        g.add_edge(hub, sp, weight=float((i % 3) + 1))
    return g


def create_nsfnet_topology() -> Graph:
    g = Graph(directed=False)
    links = [
        ("WA", "CA1", 3.0), ("WA", "IL", 7.0), ("CA1", "CA2", 2.0), ("CA1", "UT", 4.0),
        ("CA2", "TX", 6.0), ("UT", "CO", 3.0), ("CO", "IL", 4.0), ("CO", "TX", 5.0),
        ("IL", "PA", 5.0), ("TX", "GA", 4.0), ("PA", "NY", 2.0), ("PA", "GA", 6.0),
        ("GA", "FL", 3.0), ("NY", "FL", 8.0)
    ]
    for u, v, w in links:
        g.add_edge(u, v, weight=w)
    return g


# --- Session State Initialization ---
if "graph" not in st.session_state:
    st.session_state.graph = create_sample_mesh()
if "event_history" not in st.session_state:
    st.session_state.event_history = []
if "active_topology" not in st.session_state:
    st.session_state.active_topology = "Mesh Network (Default)"

# --- Sidebar Controls ---
st.sidebar.header("🛠️ Network Settings")

graph_direction_str = st.sidebar.radio(
    "Graph Type",
    ["Undirected Graph", "Directed Graph"],
    index=1 if st.session_state.graph.directed else 0
)

is_directed = (graph_direction_str == "Directed Graph")
if is_directed != st.session_state.graph.directed:
    st.session_state.graph.directed = is_directed
    st.rerun()

topology_choice = st.sidebar.selectbox(
    "Select Topology Preset",
    ["Mesh Network (Default)", "Linear Chain (6 Routers)", "Ring Network (6 Routers)", "Star / Hub-and-Spoke", "NSFNET Backbone (14 Nodes)", "Reset Graph"],
)

if st.sidebar.button("Load Selected Topology"):
    st.session_state.active_topology = topology_choice
    if topology_choice in ["Mesh Network (Default)", "Reset Graph"]:
        st.session_state.graph = create_sample_mesh()
    elif topology_choice == "Linear Chain (6 Routers)":
        st.session_state.graph = create_linear_topology()
    elif topology_choice == "Ring Network (6 Routers)":
        st.session_state.graph = create_ring_topology()
    elif topology_choice == "Star / Hub-and-Spoke":
        st.session_state.graph = create_star_topology()
    elif topology_choice == "NSFNET Backbone (14 Nodes)":
        st.session_state.graph = create_nsfnet_topology()
    st.session_state.graph.directed = is_directed
    st.session_state.event_history = []
    st.rerun()

with st.sidebar.expander("➕ Add Custom Link", expanded=False):
    c_u = st.text_input("Source Node", value="Router_A", key="custom_u")
    c_v = st.text_input("Target Node", value="Router_B", key="custom_v")
    c_w = st.number_input("Link Weight (Cost)", min_value=0.1, value=5.0, step=0.5, key="custom_w")
    if st.button("Add Custom Link"):
        st.session_state.graph.add_edge(c_u, c_v, weight=c_w)
        st.success(f"Added link {c_u} -> {c_v} (weight={c_w})")
        st.rerun()

with st.sidebar.expander("⚡ Add Composite Metric Link", expanded=False):
    comp_u = st.text_input("Source Router", value="Router_A", key="comp_u")
    comp_v = st.text_input("Target Router", value="Router_B", key="comp_v")
    comp_delay = st.number_input("Delay (sec)", min_value=0.0, value=0.1, step=0.05, format="%.3f", key="comp_delay")
    comp_bw = st.number_input("Bandwidth (Gbps)", min_value=0.1, value=5.0, step=0.5, key="comp_bw")
    if st.button("Add Composite Link"):
        st.session_state.graph.add_composite_edge(comp_u, comp_v, comp_delay, comp_bw)
        st.success(f"Added composite link {comp_u} <-> {comp_v}")
        st.rerun()

with st.sidebar.expander("🔗 Path Reconstruction Test", expanded=False):
    if st.button("Test Circular Predecessor Reconstruction"):
        from src.dijkstra import reconstruct_path
        circ_map = {"Target": "Node_A", "Node_A": "Node_B", "Node_B": "Node_A"}
        try:
            res = reconstruct_path("Source", "Target", circ_map)
            st.info(f"Reconstruction output: {res}")
        except Exception as err:
            st.error(f"Reconstruction failed: {err}")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Algorithm Configuration")

algorithm_type = st.sidebar.radio(
    "Routing Algorithm Engine",
    ["Dijkstra (Link-State / OSPF)", "Bellman-Ford (Distance-Vector / RIP)"]
)

split_horizon = False
poison_reverse = False
if "Bellman-Ford" in algorithm_type:
    st.sidebar.subheader("Distance-Vector Convergence Options")
    split_horizon = st.sidebar.checkbox("Enable Split Horizon", value=True)
    poison_reverse = st.sidebar.checkbox("Enable Poison Reverse", value=False)

active_nodes = st.session_state.graph.get_nodes()
if not active_nodes:
    st.warning("Network graph is currently empty.")
    st.stop()

col_src, col_dst = st.sidebar.columns(2)
source_node = col_src.selectbox("Source Router", active_nodes, index=0)
target_node = col_dst.selectbox("Destination Router", active_nodes, index=len(active_nodes) - 1)

# --- Dynamic Network Events ---
st.sidebar.markdown("---")
st.sidebar.header("⚡ Dynamic Network Events")

event_type_str = st.sidebar.selectbox(
    "Event Action",
    ["Cut Link (LINK_DOWN)", "Restore Link (LINK_UP)", "Change Link Cost"]
)

edges_list = [f"{u} <-> {v}" for u, v, w, act in st.session_state.graph.get_edges(active_only=False)]
if edges_list:
    selected_edge_str = st.sidebar.selectbox("Select Target Link", edges_list)
    u_sel, v_sel = selected_edge_str.split(" <-> ")
    new_cost_input = 1.0
    if event_type_str == "Change Link Cost":
        new_cost_input = st.sidebar.number_input("New Link Cost", min_value=0.1, max_value=100.0, value=5.0, step=0.5)

    if st.sidebar.button("Apply Link Event"):
        sim = NetworkEventSimulator(st.session_state.graph)
        if event_type_str == "Cut Link (LINK_DOWN)":
            ev = NetworkEvent(EventType.LINK_DOWN, u_sel, v_sel, description=f"Disabled link {u_sel} <-> {v_sel}")
        elif event_type_str == "Restore Link (LINK_UP)":
            ev = NetworkEvent(EventType.LINK_UP, u_sel, v_sel, description=f"Restored link {u_sel} <-> {v_sel}")
        else:
            ev = NetworkEvent(EventType.COST_CHANGE, u_sel, v_sel, new_cost=new_cost_input, description=f"Updated link cost {u_sel} <-> {v_sel} to {new_cost_input}")

        res = sim.trigger_event(ev, split_horizon=split_horizon, poison_reverse=poison_reverse)
        st.sidebar.success(res.log_summary)
        st.rerun()

# --- Main Application Layout ---

col_main_left, col_main_right = st.columns([1.3, 1.0])

nx_graph = nx.DiGraph() if st.session_state.graph.directed else nx.Graph()
for u, v, w, active in st.session_state.graph.get_edges(active_only=False):
    nx_graph.add_edge(u, v, weight=w, active=active)
for n in st.session_state.graph.get_nodes():
    if n not in nx_graph:
        nx_graph.add_node(n)

active_topo = st.session_state.get("active_topology", "Mesh Network (Default)")
if "Ring" in active_topo:
    pos = nx.circular_layout(nx_graph)
elif "Star" in active_topo:
    pos = nx.shell_layout(nx_graph)
else:
    pos = nx.spring_layout(nx_graph, seed=42)

# Run Selected Algorithm Engine
if "Dijkstra" in algorithm_type:
    routing_table_data = dijkstra(st.session_state.graph, source_node)
    distances, predecessors, dij_steps = dijkstra_trace(st.session_state.graph, source_node)
    total_steps = len(dij_steps)
    bf_steps = []
else:
    routing_table_data = bellman_ford(st.session_state.graph, source_node, split_horizon, poison_reverse)
    D_mat, NH_mat, bf_steps, has_neg_cycle = bellman_ford_distance_vector(st.session_state.graph, split_horizon, poison_reverse)
    total_steps = len(bf_steps)
    dij_steps = []

# Find target path & cost
target_row = next((r for r in routing_table_data if r["Destination"] == target_node), None)
shortest_path = target_row["Path"] if target_row else []
path_cost = target_row["Cost"] if target_row else float("inf")
shortest_path_edges = set(zip(shortest_path[:-1], shortest_path[1:])) if len(shortest_path) > 1 else set()

with col_main_left:
    st.subheader("🕸️ Network Graph Topology Visualizer")

    step_index = 0
    if total_steps > 1:
        step_index = st.slider("Algorithm Step-by-Step Stepper", 0, total_steps - 1, total_steps - 1)

    current_active_edge = None
    visited_nodes_step = set()
    current_node_step = None
    step_description = ""

    if "Dijkstra" in algorithm_type and dij_steps:
        cur_step = dij_steps[step_index]
        current_active_edge = cur_step.active_edge
        visited_nodes_step = cur_step.visited
        current_node_step = cur_step.current_node
        step_description = cur_step.description
    elif "Bellman-Ford" in algorithm_type and bf_steps:
        cur_step_bf = bf_steps[step_index]
        step_description = cur_step_bf.description

    if step_description:
        st.markdown(f'<div class="step-log-box">▶ <strong>Step {step_index} / {total_steps - 1}:</strong> {step_description}</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(9, 6.5))
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    node_colors = []
    for node in nx_graph.nodes():
        if node == source_node:
            node_colors.append('#22c55e')
        elif node == target_node:
            node_colors.append('#f43f5e')
        elif node == current_node_step:
            node_colors.append('#eab308')
        elif node in visited_nodes_step:
            node_colors.append('#8b5cf6')
        else:
            node_colors.append('#38bdf8')

    nx.draw_networkx_nodes(nx_graph, pos, ax=ax, node_color=node_colors, node_size=1300)
    nx.draw_networkx_labels(nx_graph, pos, ax=ax, font_color='white', font_weight='bold', font_size=10)

    active_edges = []
    failed_edges = []
    path_highlight_edges = []

    for u, v, w, is_act in st.session_state.graph.get_edges(active_only=False):
        edge_pair = (u, v)
        rev_pair = (v, u)
        if not is_act:
            failed_edges.append((u, v))
        elif edge_pair in shortest_path_edges or (not st.session_state.graph.directed and rev_pair in shortest_path_edges):
            path_highlight_edges.append((u, v))
        else:
            active_edges.append((u, v))

    nx.draw_networkx_edges(nx_graph, pos, edgelist=active_edges, ax=ax, edge_color='#64748b', width=2, arrows=st.session_state.graph.directed)
    nx.draw_networkx_edges(nx_graph, pos, edgelist=path_highlight_edges, ax=ax, edge_color='#f59e0b', width=4.5, arrows=st.session_state.graph.directed)
    nx.draw_networkx_edges(nx_graph, pos, edgelist=failed_edges, ax=ax, edge_color='#ef4444', width=2, style='dashed', arrows=st.session_state.graph.directed)

    if current_active_edge:
        u_act, v_act = current_active_edge
        nx.draw_networkx_edges(nx_graph, pos, edgelist=[(u_act, v_act)], ax=ax, edge_color='#38bdf8', width=5, arrows=st.session_state.graph.directed)

    edge_labels = {}
    for u, v, w, is_act in st.session_state.graph.get_edges(active_only=False):
        edge_labels[(u, v)] = f"{w}" if is_act else "X"

    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=edge_labels, ax=ax, font_color='#cbd5e1', font_size=9, bbox=dict(facecolor='#1e293b', edgecolor='none', alpha=0.8))

    ax.axis('off')
    st.pyplot(fig)

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        cost_display = "∞" if path_cost == float("inf") else f"{path_cost}"
        st.markdown(f'<div class="metric-card"><h4>Path Cost</h4><h3 style="color:#f59e0b;">{cost_display}</h3></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><h4>Hops Count</h4><h3 style="color:#3b82f6;">{max(0, len(shortest_path) - 1)}</h3></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown(f'<div class="metric-card"><h4>Total Steps</h4><h3 style="color:#10b981;">{total_steps}</h3></div>', unsafe_allow_html=True)


with col_main_right:
    st.subheader("📋 Explicit Routing Table")
    st.markdown(f"Routing Table for Source Router: **`{source_node}`**")

    # Format Routing Table with explicit [Destination | Next Hop | Cost | Path]
    formatted_rt = []
    for row in routing_table_data:
        cost_val = "∞" if row["Cost"] == float("inf") else f"{row['Cost']}"
        next_hop_val = row["Next Hop"] if row["Next Hop"] else "None"
        path_val = " -> ".join(row["Path"]) if row["Path"] else "None"
        formatted_rt.append({
            "Destination": row["Destination"],
            "Next Hop": next_hop_val,
            "Cost": cost_val,
            "Path": path_val
        })

    st.dataframe(formatted_rt, width="stretch" if hasattr(st, "dataframe") else None)

    with st.expander("ℹ️ Routing Table Schema Details"):
        st.markdown(
            """
            - **Destination**: Target router node.
            - **Next Hop**: Immediate adjacent router to forward packets to.
            - **Cost**: Total accumulated link path cost to destination.
            - **Path**: Full sequence of router nodes from source to destination.
            """
        )

st.markdown("---")
st.markdown("🔴 **Red Line**: Severed Link | 🟢 **Green Node**: Source Router | 🌹 **Rose Node**: Target Router | 🟡 **Gold Path**: Shortest Path")
