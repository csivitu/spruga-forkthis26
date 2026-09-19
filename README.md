# SPRUGA — Shortest Path Routing Using Graph Algorithms

A from-scratch simulation of computer-network routing, built for the **Computer Networks** course project. SPRUGA models routers and links as a weighted graph and implements both major routing-protocol families — **Dijkstra (link-state)** and **Bellman-Ford (distance-vector)** — complete with a custom binary min-heap, dynamic failure/recovery simulation, and an interactive Streamlit dashboard.

## Team

| Name | Reg. No. |
|---|---|
| Arihanth Kumar R | 25BCE2485 |
| Arya Aravindan | 25BCE0136 |
| Keerthan Hosamane | 25BCE2522 |

B.Tech CSE Core, School of Computer Science and Engineering, VIT Vellore

## Overview

Modern networks are large, dynamic, and interconnected — links fail, costs change, and traffic shifts constantly, so routing decisions can't be static or hand-computed. Routers need a fast, provably-correct way to compute the lowest-cost path to every other router, and to recompute it the instant the topology changes.

SPRUGA builds and visualizes exactly that decision engine.

### Objectives

1. **Model networks as graphs** — represent routers and links as a weighted adjacency-list graph that can activate/deactivate nodes and edges on demand.
2. **Implement both routing families** — build Dijkstra (link-state) and Bellman-Ford (distance-vector) from scratch, including a custom binary min-heap.
3. **Simulate real network events** — support link failure, link recovery, cost changes, and node failure, then measure re-convergence.
4. **Visualize the decision process** — provide a step-by-step CLI trace and an interactive Streamlit dashboard for teaching and demonstration.

## How Routing Works

Each router forwards packets using a locally-stored routing table, where every entry maps a **Destination** to a **Next Hop**, a **Cost**, and (for analysis) the full **Path**. Two broad strategies build these tables automatically:

| | Link-State (e.g. OSPF) | Distance-Vector (e.g. RIP) |
|---|---|---|
| **Strategy** | Greedy, priority-queue driven | Iterative edge relaxation |
| **Mechanism** | Every router floods full topology info; each router independently runs Dijkstra | Each router shares only its own distance table with direct neighbors; paths emerge via Bellman-Ford relaxation |
| **Time complexity** | O((V + E) log V) | O(V · E) |
| **Negative weights** | Not supported | Supported |
| **Negative cycle detection** | No | Yes, via an extra relaxation pass |
| **Information shared** | Full topology (flooded) | Only neighbor distance vectors |
| **Convergence speed** | Fast | Slower, round-based |
| **Loop risk** | Low (global view) | Higher — needs split horizon / poison reverse |
| **Real protocol analog** | OSPF | RIP |
| **Implementation** | `src/dijkstra.py` | `src/bellman_ford.py` |

### Dijkstra's Algorithm

A greedy algorithm that always expands the unvisited router with the smallest known cost first, using a custom binary min-heap (`src/dijkstra.py`) to select the next router in O(log V). Whenever a shorter path to a neighbor is found, its cost and predecessor are updated (edge relaxation). Requires non-negative link weights, which link costs (latency, hop count) always are — so Dijkstra is guaranteed to terminate correctly with optimal, single-source shortest paths.

**Complexity:** `O((V + E) log V)`

### Bellman-Ford Algorithm

Every router relaxes all of its edges once per round, for up to `|V| − 1` rounds. `bellman_ford_distance_vector()` simulates every router computing its table from neighbor gossip, and correctness holds even with negative link costs (unlike Dijkstra). One extra relaxation pass flags a `negative_cycle` if any distance still improves.

**Complexity:** `O(V · E)`

Bellman-Ford is slower to converge than link-state and vulnerable to routing loops, addressed via:

- **Split Horizon** — a router never advertises a route back to the neighbor it learned that route from, breaking the simplest two-router routing loop. Toggle via `bellman_ford_distance_vector(split_horizon=True)`.
- **Poison Reverse** — extends split horizon by advertising the route back with a cost of infinity instead of hiding it, making the loop-breaking signal explicit. Enabled independently via `poison_reverse=True`.

## Networks as Weighted Graphs

- **Nodes (vertices):** represent routers or network devices
- **Edges:** represent physical or logical communication links
- **Edge weights:** represent link cost — latency, hop count, or bandwidth
- **Active flags:** let nodes and edges be switched on/off to model failures

Implemented as a custom weighted adjacency-list class — `src/graph.py` — supporting both directed and undirected topologies.

### Custom Min-Heap

`MinHeap` stores `(cost, router)` pairs in a plain Python list with no external heap library:

| Operation | Behavior | Complexity |
|---|---|---|
| `push(cost, item)` | append + sift up | O(log V) |
| `pop()` | remove min, sift down | O(log V) |
| `decrease_key(item, cost)` | reduce cost + sift up | — |
| `is_empty()` | termination check | O(1) |

A position map gives O(1) lookup of any router's index, enabling a true `decrease_key()` operation. `dijkstra_trace()` records a `DijkstraStep` after every pop and every relaxation, powering both the CLI printout and the Streamlit step slider. `reconstruct_path()` walks the predecessor map backwards from destination to source to build the final route.

## Dynamic Network Event Simulation

Real networks change constantly. SPRUGA models this through a `NetworkEventSimulator` (`src/network_simulator/`) that mutates the live graph:

- **LINK_DOWN** — severs a link (shown as a dashed red line)
- **LINK_UP** — restores a previously failed link
- **COST_CHANGE** — updates a link's weight in place
- **NODE_DOWN / NODE_UP** — disables or re-enables an entire router

Each `trigger_event()` call re-runs both Dijkstra and Bellman-Ford and reports step/iteration counts for the new convergence, letting the dashboard directly compare how quickly each protocol family recovers from the same failure.

## System Architecture

| Component | Location | Description |
|---|---|---|
| Core Graph Engine | `src/graph.py` | Weighted adjacency list — nodes, edges, active/inactive state |
| Routing Algorithms | `src/dijkstra.py`, `src/bellman_ford.py` | MinHeap-based Dijkstra and iterative Bellman-Ford, both with full step tracing |
| Network Simulator | `src/network_simulator/` | Event engine, routing-table objects, and algorithm wrappers for dynamic scenarios |
| Interfaces | `main.py` (CLI), `app.py` (Streamlit) | CLI demo runner and interactive web dashboard consume the same core engine |

## Technology Stack

- **Python 3** — core language for the graph engine, algorithms, and simulator
- **NetworkX** — graph object model and layout for the visual dashboard
- **Matplotlib** — renders the live network topology diagram inside Streamlit
- **Streamlit** — interactive web dashboard: topology presets, step slider, live events
- **Pytest** — automated unit tests covering graph, algorithms, and simulator logic

```
requirements.txt pins: networkx>=3.0, matplotlib>=3.7.0, streamlit>=1.25.0, pytest>=7.0.0
```

## Repository Structure

```
SPRUGA/
├── src/                # Core graph engine, algorithms, and simulator
├── tests/              # Pytest suite — test_graph.py, test_algorithms.py, test_simulator.py
├── app.py              # Streamlit interactive dashboard
├── main.py             # CLI demo runner
├── requirements.txt    # networkx, matplotlib, streamlit, pytest
└── .gitignore
```

## Getting Started

```bash
git clone https://github.com/FridgeMan98/SPRUGA-.git
cd SPRUGA-
pip install -r requirements.txt

# Run the CLI demo
python main.py

# Launch the interactive dashboard
streamlit run app.py

# Run the test suite
pytest tests/
```

## CLI Demo Output

Example routing table computed from `Router_A` on the sample topology:

```
DIJKSTRA – LINK-STATE ROUTING TABLE
Destination   Next Hop    Cost    Path
Router_A      Local       0       Router_A
Router_B      Router_C    3       A → C → B
Router_C      Router_C    2       A → C
Router_D      Router_C    8       A → C → B → D
Router_E      Router_C    10      A → C → B → D → E
```

**Metrics:** Path Cost (A→E) = 10 · Hops = 4 · Total Steps = 12

Bellman-Ford (distance-vector) is printed immediately below with the same schema, confirming both engines agree on the optimal path.

## Interactive Streamlit Dashboard

- **Topology presets** — Mesh, Ring (6 routers), Star / Hub-and-Spoke, and the 14-node NSFNET backbone
- **Algorithm switch** — toggle between Dijkstra and Bellman-Ford, with split horizon / poison reverse controls
- **Step-by-step stepper** — slider replays every relaxation step with a live description and highlighted edge
- **Live routing table** — Destination · Next Hop · Cost · Path, recomputed instantly after any event

Legend: 🔴 Severed Link · 🟢 Source Router · 🚩 Target Router · 🟡 Amber = Shortest Path

## Testing & Validation

| Test file | Coverage |
|---|---|
| `test_graph.py` | Node/edge insertion, weight updates, active/inactive toggling, neighbor queries |
| `test_algorithms.py` | Dijkstra and Bellman-Ford checked against hand-computed shortest paths on known topologies |
| `test_simulator.py` | Confirms link/node events correctly mutate the graph and trigger re-convergence |

```bash
pytest tests/
```

All unit tests pass, giving confidence that routing decisions match theoretical shortest-path results.

## Real-World Applications

- **Enterprise & ISP networks** — OSPF (link-state) runs Dijkstra internally to route traffic across large autonomous systems.
- **Small / legacy networks** — RIP (distance-vector) still powers simple LANs where topology rarely changes.
- **GPS & maps navigation** — shortest-path search over road graphs uses the same relaxation principles as Dijkstra.
- **Logistics & supply chains** — delivery routing and network-flow optimization build directly on these shortest-path foundations.

## Challenges Faced

- Implementing `decrease_key()` correctly in a from-scratch binary heap without an external library.
- Preventing routing loops in the distance-vector engine without over-suppressing valid updates.
- Designing a step trace granular enough to animate in the UI without overwhelming the viewer.
- Keeping the CLI and Streamlit interfaces perfectly in sync with one shared core engine.

## Future Enhancements

- Add hierarchical OSPF areas and route summarization for larger topologies.
- Support weighted, multi-metric costs (latency + bandwidth + reliability).
- Integrate with real router APIs or Mininet for live network testing.
- Explore ML-based traffic prediction to pre-emptively re-route around congestion.

## Conclusion

SPRUGA implements both major routing-protocol families — Dijkstra (link-state) and Bellman-Ford (distance-vector) — entirely from scratch, down to a custom binary min-heap. A dynamic event simulator and an interactive Streamlit dashboard turn abstract graph theory into a hands-on, visual teaching tool. Unit-tested and validated against known shortest-path results, the project brings core computer-networking routing protocols to life through hands-on algorithmic simulation.
