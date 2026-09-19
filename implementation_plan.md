# Implementation Plan - Shortest Path Routing Simulator

Design and implement a computer networking **Shortest Path Routing Simulator** from scratch in Python. The simulator models **Link-State Routing (OSPF / Dijkstra)** and **Distance-Vector Routing (RIP / Bellman-Ford)** without relying on third-party pathfinding libraries, featuring dynamic network events (link cuts, cost updates) and an interactive step-by-step visual interface built with Streamlit.

## User Review Required

> [!IMPORTANT]
> **Algorithm Implementations from Scratch**: All routing logic (Dijkstra and Bellman-Ford / Distance Vector exchange) will be implemented using pure Python data structures (Min-Heap, Adjacency Lists, Distance Tables). Third-party libraries like `matplotlib` or `networkx` will be restricted strictly to UI graph rendering layout computations.

> [!NOTE]
> **Distance-Vector Dynamics**: Bellman-Ford will support both single-source calculation and multi-node round-by-round Distance Vector message-passing simulation, with configurable options for **Split Horizon** and **Poison Reverse** to prevent Count-to-Infinity during dynamic link cuts.

---

## Proposed Architecture & Design

```
+-------------------------------------------------------------------------------+
|                             Streamlit UI (app.py)                             |
|  [Topology Visualizer]  [Algorithm Execution Stepper]  [Routing Tables View]   |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                    Dynamic Event Simulator (simulator.py)                      |
|      - Event Queue (Link Cut, Link Restore, Cost Change, Router Failure)      |
|      - Step-by-step timeline execution & convergence metrics tracking         |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                    Algorithm Engines (algorithms/)                            |
|  - DijkstraEngine (Min-Heap, Step Trace, Link-State Database LDB)             |
|  - BellmanFordEngine (Distance Vectors, Iterative Exchanges, Split Horizon)   |
|  - RoutingTable (Per-router Forwarding Table generation)                      |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                    Graph Data Model (graph.py)                                |
|  - Custom Adjacency List Graph (Directed/Undirected, Weighted Edges)          |
|  - Dynamic edge state toggles (active/inactive), cost mutators                |
+-------------------------------------------------------------------------------+
```

---

## Proposed Changes

### Core Network Simulator Package (`src/network_simulator/`)

---

#### [MODIFY] [graph.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/network_simulator/graph.py)
- Replace NetworkX dependency with a pure Python custom `NetworkGraph` class.
- Implement adjacency lists with weighted edges, node metadata, and active/inactive link flags.
- Support link failure (`disable_edge`), recovery (`enable_edge`), weight update (`set_edge_weight`), and adjacency queries.
- Provide export helpers for UI visualization layout.

#### [NEW] [routing_table.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/network_simulator/routing_table.py)
- Define `RoutingTableEntry` dataclass (`destination`, `next_hop`, `cost`).
- Implement `RoutingTable` class mapping each router to its complete forwarding table.
- Support serialization to tabular format for UI rendering.

#### [MODIFY] [algorithms.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/network_simulator/algorithms.py)
- Refactor into modular algorithm engines implemented from scratch:
  1. **`DijkstraEngine` (Link-State / OSPF)**:
     - Pure Python binary min-heap priority queue.
     - Computes shortest paths from source to all nodes.
     - Generates step-by-step snapshot trace array containing visited set, tentative distance array `d[v]`, predecessor tree `p[v]`, current node, and updated edges.
     - Builds full Link-State Routing Table for the source node.
  2. **`BellmanFordEngine` (Distance-Vector / RIP)**:
     - Round-by-round Distance Vector exchange simulation across adjacent nodes.
     - Implements Bellman-Ford equation: $D_u(v) = \min_w \{ c(u,w) + D_w(v) \}$.
     - Detects negative weight cycles.
     - Supports **Split Horizon** and **Poison Reverse** flags for dynamic link cut updates.
     - Generates step-by-step iteration snapshots and full Distance-Vector tables for all routers.

#### [NEW] [simulator.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/network_simulator/simulator.py)
- Implement `NetworkEventSimulator` class.
- Event types: `LINK_DOWN`, `LINK_UP`, `COST_CHANGE`, `NODE_DOWN`, `NODE_UP`.
- Maintained event timeline history with interactive trigger mechanisms.
- Tracks convergence time (number of algorithm iterations or DV message exchange rounds required to stabilize routing tables after an event).

---

### Streamlit Web Application (`app.py`)

#### [MODIFY] [app.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/app.py)
- Build a rich Streamlit visual dashboard:
  - **Sidebar Controls**: Topology selection (Pre-built standard topologies like NSFNET, Ring, Mesh, Star, or custom topology editor), Algorithm mode (Dijkstra Link-State vs. Bellman-Ford Distance Vector), Split Horizon toggles.
  - **Main Network Canvas**: Matplotlib graph rendering with color-coded nodes/links (Active links in green/blue, Failed links in red dashed, Shortest path highlighted in vibrant gold).
  - **Step-by-Step Playback Stepper**: Interactive slider and Next/Previous controls to step through algorithm state progression line-by-line.
  - **Interactive Dynamic Events Panel**: Buttons to sever links or change link costs dynamically and inspect re-convergence.
  - **Live Routing Tables & Distance Vectors**: Clear formatted tables displaying per-router forwarding tables `(Destination, Next Hop, Cost)` and Distance Vector exchange matrices.
  - **Convergence & Performance Panel**: Metrics comparing Dijkstra vs. Bellman-Ford convergence steps and message count.

---

### Test Suite (`tests/`)

#### [NEW] [test_graph.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/tests/test_graph.py)
- Unit tests for custom `NetworkGraph` graph model (add node/edge, disable/enable edge, cost changes, adjacency retrieval).

#### [MODIFY] [test_algorithms.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/tests/test_algorithms.py)
- Unit tests verifying Dijkstra from scratch against known graph shortest paths.
- Unit tests verifying Bellman-Ford from scratch (including disconnected nodes and negative weights detection).
- Step-by-step trace generation verification.

#### [NEW] [test_simulator.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/tests/test_simulator.py)
- Unit tests for dynamic network event simulation (link down/up, cost change, convergence metrics).

---

## Verification Plan

### Automated Tests
Execute the pytest suite using the project virtual environment:
```powershell
.\venv\Scripts\pytest -v
```
Tests will cover:
1. Custom Graph Data Structure operations.
2. Dijkstra path calculation, distance calculation, and step trace validity.
3. Bellman-Ford distance vector convergence and negative cycle detection.
4. Dynamic link failure and routing table updates.

### Manual Verification
1. Launch Streamlit UI:
   ```powershell
   .\venv\Scripts\streamlit run app.py
   ```
2. Interact with step-by-step playback slider for both Dijkstra (Link-State) and Bellman-Ford (Distance-Vector).
3. Trigger a link failure (e.g. sever `Router_A <-> Router_B`) and verify live update of forwarding tables and convergence step count.
