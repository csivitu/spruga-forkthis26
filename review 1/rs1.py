import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Set, Any
from enum import Enum
from dataclasses import dataclass

# ==========================================
# 1. CORE GRAPH ENGINE
# ==========================================

class Graph:
    def __init__(self, directed: bool = False):
        self.directed = directed
        self._adj: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._nodes: Dict[str, bool] = {}

    def add_node(self, u: str) -> None:
        if u not in self._adj:
            self._adj[u] = {}
            self._nodes[u] = True

    def add_edge(self, u: str, v: str, weight: float = 1.0, active: bool = True) -> None:
        self.add_node(u)
        self.add_node(v)
        self._adj[u][v] = {"weight": float(weight), "active": active}
        if not self.directed:
            self._adj[v][u] = {"weight": float(weight), "active": active}

    def set_edge_active(self, u: str, v: str, active: bool) -> None:
        if u in self._adj and v in self._adj[u]:
            self._adj[u][v]["active"] = active
        if not self.directed and v in self._adj and u in self._adj[v]:
            self._adj[v][u]["active"] = active

    def set_edge_weight(self, u: str, v: str, weight: float) -> None:
        if u in self._adj and v in self._adj[u]:
            self._adj[u][v]["weight"] = float(weight)
        if not self.directed and v in self._adj and u in self._adj[v]:
            self._adj[v][u]["weight"] = float(weight)

    def set_node_active(self, u: str, active: bool) -> None:
        if u in self._nodes:
            self._nodes[u] = active

    def get_nodes(self, active_only: bool = True) -> List[str]:
        if active_only:
            return sorted([n for n, act in self._nodes.items() if act])
        return sorted(list(self._nodes.keys()))

    def get_neighbors(self, u: str, active_only: bool = True) -> List[Tuple[str, float]]:
        if u not in self._adj or (active_only and not self._nodes.get(u, False)):
            return []
        neighbors = []
        for v, data in self._adj[u].items():
            if active_only:
                if self._nodes.get(v, False) and data.get("active", True):
                    neighbors.append((v, data["weight"]))
            else:
                neighbors.append((v, data["weight"]))
        return neighbors

    def get_edges(self, active_only: bool = False) -> List[Tuple[str, str, float, bool]]:
        edges = []
        seen = set()
        for u in self._adj:
            for v, data in self._adj[u].items():
                edge_id = (min(u, v), max(u, v)) if not self.directed else (u, v)
                if edge_id not in seen:
                    seen.add(edge_id)
                    act = self._nodes.get(u, True) and self._nodes.get(v, True) and data.get("active", True)
                    if not active_only or act:
                        edges.append((u, v, data["weight"], act))
        return edges


# ==========================================
# 2. DIJKSTRA ENGINE & CUSTOM MIN-HEAP
# ==========================================

class MinHeap:
    def __init__(self):
        self.heap: List[Tuple[float, str]] = []
        self.pos: Dict[str, int] = {}

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def push(self, cost: float, item: str) -> None:
        if item in self.pos:
            self.decrease_key(item, cost)
            return
        idx = len(self.heap)
        self.heap.append((cost, item))
        self.pos[item] = idx
        self._sift_up(idx)

    def pop(self) -> Tuple[float, str]:
        if self.is_empty():
            raise IndexError("pop from empty heap")
        root_cost, root_item = self.heap[0]
        last_cost, last_item = self.heap.pop()
        del self.pos[root_item]
        if not self.is_empty():
            self.heap[0] = (last_cost, last_item)
            self.pos[last_item] = 0
            self._sift_down(0)
        return root_cost, root_item

    def decrease_key(self, item: str, new_cost: float) -> None:
        idx = self.pos.get(item)
        if idx is None:
            return
        if new_cost < self.heap[idx][0]:
            self.heap[idx] = (new_cost, item)
            self._sift_up(idx)

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
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
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
        self.pos[self.heap[i][1]] = j
        self.pos[self.heap[j][1]] = i
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]


@dataclass
class DijkstraStep:
    step_num: int
    current_node: Optional[str]
    active_edge: Optional[Tuple[str, str]]
    visited: Set[str]
    distances: Dict[str, float]
    predecessors: Dict[str, Optional[str]]
    description: str


def dijkstra_trace(graph: Graph, source: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]], List[DijkstraStep]]:
    nodes = graph.get_nodes(active_only=True)
    distances = {node: float("inf") for node in nodes}
    predecessors = {node: None for node in nodes}
    steps: List[DijkstraStep] = []

    if source not in distances:
        return distances, predecessors, steps

    distances[source] = 0.0
    visited = set()
    pq = MinHeap()
    pq.push(0.0, source)

    steps.append(DijkstraStep(
        step_num=0,
        current_node=source,
        active_edge=None,
        visited=set(visited),
        distances=dict(distances),
        predecessors=dict(predecessors),
        description=f"Initialized source {source} with distance 0.0"
    ))

    step_counter = 1
    while not pq.is_empty():
        curr_dist, u = pq.pop()
        if u in visited:
            continue
        visited.add(u)

        steps.append(DijkstraStep(
            step_num=step_counter,
            current_node=u,
            active_edge=None,
            visited=set(visited),
            distances=dict(distances),
            predecessors=dict(predecessors),
            description=f"Popped router {u} with minimum cost {curr_dist:.1f}"
        ))
        step_counter += 1

        for v, weight in graph.get_neighbors(u, active_only=True):
            if v not in visited:
                new_cost = curr_dist + weight
                if new_cost < distances[v]:
                    distances[v] = new_cost
                    predecessors[v] = u
                    pq.push(new_cost, v)
                    steps.append(DijkstraStep(
                        step_num=step_counter,
                        current_node=u,
                        active_edge=(u, v),
                        visited=set(visited),
                        distances=dict(distances),
                        predecessors=dict(predecessors),
                        description=f"Relaxed edge ({u} -> {v}): updated cost to {new_cost:.1f}"
                    ))
                    step_counter += 1

    return distances, predecessors, steps


def reconstruct_path(predecessors: Dict[str, Optional[str]], source: str, target: str) -> List[str]:
    if source == target:
        return [source]
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        if curr == source:
            break
        curr = predecessors.get(curr)
    if not path or path[-1] != source:
        return []
    path.reverse()
    return path


def dijkstra(graph: Graph, source: str) -> List[Dict[str, Any]]:
    distances, predecessors, _ = dijkstra_trace(graph, source)
    nodes = graph.get_nodes(active_only=True)
    table = []
    for dst in nodes:
        cost = distances.get(dst, float("inf"))
        path = reconstruct_path(predecessors, source, dst) if cost < float("inf") else []
        next_hop = "Local" if dst == source else (path[1] if len(path) > 1 else None)
        table.append({
            "Destination": dst,
            "Next Hop": next_hop,
            "Cost": cost,
            "Path": path
        })
    return table


# ==========================================
# 3. BELLMAN-FORD & DISTANCE-VECTOR ENGINE
# ==========================================

@dataclass
class DistanceVectorStep:
    round_num: int
    router: str
    description: str
    distance_table: Dict[str, Dict[str, float]]


def bellman_ford_distance_vector(graph: Graph, split_horizon: bool = False, poison_reverse: bool = False) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, Optional[str]]], List[DistanceVectorStep], bool]:
    nodes = graph.get_nodes(active_only=True)
    D = {u: {v: (0.0 if u == v else float("inf")) for v in nodes} for u in nodes}
    NH = {u: {v: (u if u == v else None) for v in nodes} for u in nodes}
    steps: List[DistanceVectorStep] = []

    steps.append(DistanceVectorStep(
        round_num=0,
        router="ALL",
        description="Initial local distance tables constructed.",
        distance_table={u: dict(D[u]) for u in nodes}
    ))

    max_rounds = max(1, len(nodes) - 1)
    has_neg_cycle = False

    for r in range(1, max_rounds + 1):
        updated = False
        for u in nodes:
            for v, w in graph.get_neighbors(u, active_only=True):
                for dest in nodes:
                    if dest == u:
                        continue
                    advertised_cost = D[v].get(dest, float("inf"))
                    if NH[v].get(dest) == u:
                        if poison_reverse:
                            advertised_cost = float("inf")
                        elif split_horizon:
                            continue

                    if advertised_cost < float("inf") and (w + advertised_cost < D[u][dest]):
                        D[u][dest] = w + advertised_cost
                        NH[u][dest] = v
                        updated = True
                        steps.append(DistanceVectorStep(
                            round_num=r,
                            router=u,
                            description=f"Round {r}: {u} updated route to {dest} via {v} (Cost: {D[u][dest]:.1f})",
                            distance_table={node: dict(D[node]) for node in nodes}
                        ))
        if not updated:
            break

    return D, NH, steps, has_neg_cycle


def bellman_ford(graph: Graph, source: str, split_horizon: bool = False, poison_reverse: bool = False) -> List[Dict[str, Any]]:
    D, NH, _, _ = bellman_ford_distance_vector(graph, split_horizon, poison_reverse)
    nodes = graph.get_nodes(active_only=True)
    table = []
    for dst in nodes:
        cost = D[source].get(dst, float("inf"))
        next_hop = "Local" if dst == source else NH[source].get(dst)
        path = []
        if cost < float("inf"):
            curr = source
            visited_p = set()
            while curr and curr not in visited_p:
                path.append(curr)
                visited_p.add(curr)
                if curr == dst:
                    break
                curr = NH[curr].get(dst)
            if not path or path[-1] != dst:
                path = []
        table.append({
            "Destination": dst,
            "Next Hop": next_hop,
            "Cost": cost,
            "Path": path
        })
    return table


# ==========================================
# 4. SIMULATOR & EVENT HANDLING
# ==========================================

class EventType(Enum):
    LINK_DOWN = "LINK_DOWN"
    LINK_UP = "LINK_UP"
    COST_CHANGE = "COST_CHANGE"


@dataclass
class NetworkEvent:
    event_type: EventType
    u: str
    v: str
    new_cost: Optional[float] = None
    description: str = ""


@dataclass
class SimulationResult:
    log_summary: str


class NetworkEventSimulator:
    def __init__(self, graph: Graph):
        self.graph = graph

    def trigger_event(self, event: NetworkEvent, split_horizon: bool = False, poison_reverse: bool = False) -> SimulationResult:
        if event.event_type == EventType.LINK_DOWN:
            self.graph.set_edge_active(event.u, event.v, False)
            msg = f"Severed link between {event.u} and {event.v}"
        elif event.event_type == EventType.LINK_UP:
            self.graph.set_edge_active(event.u, event.v, True)
            msg = f"Restored link between {event.u} and {event.v}"
        elif event.event_type == EventType.COST_CHANGE:
            if event.new_cost is not None:
                self.graph.set_edge_weight(event.u, event.v, event.new_cost)
            msg = f"Updated link weight {event.u} <-> {event.v} to {event.new_cost}"
        return SimulationResult(log_summary=msg)


# ==========================================
# 5. STREAMLIT APPLICATION & UI
# ==========================================

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

# Preset Topologies
def create_sample_mesh() -> Graph:
    g = Graph(directed=False)
    edges = [
        ("Router_A", "Router_B", 4.0),
        ("Router_A", "Router_C", 2.0),
        ("Router_B", "Router_C", 1.0),
        ("Router_B", "Router_D", 5.0),
        ("Router_C", "Router_D", 8.0),
        ("Router_C", "Router_E", 10.0),
        ("Router_D", "Router_E", 2.0),
    ]
    for u, v, w in edges:
        g.add_edge(u, v, weight=w)
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


# Session State Initialization
if "graph" not in st.session_state:
    st.session_state.graph = create_sample_mesh()

# Sidebar Controls
st.sidebar.header("🛠️ Network Settings")

topology_choice = st.sidebar.selectbox(
    "Select Topology Preset",
    ["Mesh Network (Default)", "Ring Network (6 Routers)", "Star / Hub-and-Spoke", "NSFNET Backbone (14 Nodes)", "Reset Graph"],
)

if st.sidebar.button("Load Selected Topology"):
    if topology_choice in ["Mesh Network (Default)", "Reset Graph"]:
        st.session_state.graph = create_sample_mesh()
    elif topology_choice == "Ring Network (6 Routers)":
        st.session_state.graph = create_ring_topology()
    elif topology_choice == "Star / Hub-and-Spoke":
        st.session_state.graph = create_star_topology()
    elif topology_choice == "NSFNET Backbone (14 Nodes)":
        st.session_state.graph = create_nsfnet_topology()
    st.rerun()

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

# Dynamic Network Events
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
            ev = NetworkEvent(EventType.LINK_DOWN, u_sel, v_sel)
        elif event_type_str == "Restore Link (LINK_UP)":
            ev = NetworkEvent(EventType.LINK_UP, u_sel, v_sel)
        else:
            ev = NetworkEvent(EventType.COST_CHANGE, u_sel, v_sel, new_cost=new_cost_input)

        res = sim.trigger_event(ev, split_horizon=split_horizon, poison_reverse=poison_reverse)
        st.sidebar.success(res.log_summary)
        st.rerun()

# Layout Setup
col_main_left, col_main_right = st.columns([1.3, 1.0])

nx_graph = nx.Graph()
for u, v, w, active in st.session_state.graph.get_edges(active_only=False):
    nx_graph.add_edge(u, v, weight=w, active=active)
for n in st.session_state.graph.get_nodes():
    if n not in nx_graph:
        nx_graph.add_node(n)

pos = nx.spring_layout(nx_graph, seed=42)

# Algorithm Execution
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

# Target Path Resolution
target_row = next((r for r in routing_table_data if r["Destination"] == target_node), None)
shortest_path = target_row["Path"] if target_row else []
path_cost = target_row["Cost"] if target_row else float("inf")

shortest_path_edges = set()
if len(shortest_path) > 1:
    for i in range(len(shortest_path) - 1):
        shortest_path_edges.add(tuple(sorted((shortest_path[i], shortest_path[i+1]))))

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
        norm_edge = tuple(sorted((u, v)))
        if not is_act:
            failed_edges.append((u, v))
        elif norm_edge in shortest_path_edges:
            path_highlight_edges.append((u, v))
        else:
            active_edges.append((u, v))

    nx.draw_networkx_edges(nx_graph, pos, edgelist=active_edges, ax=ax, edge_color='#64748b', width=2)
    nx.draw_networkx_edges(nx_graph, pos, edgelist=path_highlight_edges, ax=ax, edge_color='#f59e0b', width=4.5)
    nx.draw_networkx_edges(nx_graph, pos, edgelist=failed_edges, ax=ax, edge_color='#ef4444', width=2, style='dashed')

    if current_active_edge:
        u_act, v_act = current_active_edge
        nx.draw_networkx_edges(nx_graph, pos, edgelist=[(u_act, v_act)], ax=ax, edge_color='#38bdf8', width=5)

    edge_labels = {}
    for u, v, w, is_act in st.session_state.graph.get_edges(active_only=False):
        edge_labels[(u, v)] = f"{w:g}" if is_act else "X"

    nx.draw_networkx_edge_labels(
        nx_graph,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_color='#cbd5e1',
        font_size=9,
        bbox=dict(facecolor='#1e293b', edgecolor='none', alpha=0.8)
    )

    ax.axis('off')
    st.pyplot(fig)
    plt.close(fig)

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        cost_display = "∞" if path_cost == float("inf") else f"{path_cost:.1f}"
        st.markdown(f'<div class="metric-card"><h4>Path Cost</h4><h3 style="color:#f59e0b;">{cost_display}</h3></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><h4>Hops Count</h4><h3 style="color:#3b82f6;">{max(0, len(shortest_path) - 1)}</h3></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown(f'<div class="metric-card"><h4>Total Steps</h4><h3 style="color:#10b981;">{total_steps}</h3></div>', unsafe_allow_html=True)

with col_main_right:
    st.subheader("📋 Explicit Routing Table")
    st.markdown(f"Routing Table for Source Router: **`{source_node}`**")

    formatted_rt = []
    for row in routing_table_data:
        cost_val = "∞" if row["Cost"] == float("inf") else f"{row['Cost']:g}"
        next_hop_val = row["Next Hop"] if row["Next Hop"] else "None"
        path_val = " -> ".join(row["Path"]) if row["Path"] else "None"
        formatted_rt.append({
            "Destination": row["Destination"],
            "Next Hop": next_hop_val,
            "Cost": cost_val,
            "Path": path_val
        })

    st.dataframe(formatted_rt, width="stretch")

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
