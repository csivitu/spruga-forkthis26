# Review 1 Presentation - Network Shortest Path Simulator (SPRUGA)

---

## 📌 Slide 1: Title & Project Overview

**Project Title**: Network Shortest Path Routing Protocol Simulator  
**Domain**: Computer Networks & Distributed Systems  
**Tech Stack**: Python 3.13, Streamlit, NetworkX / Matplotlib, Pytest  

> **Elevator Pitch**: A dynamic, interactive simulation platform built from scratch in Python to visualize, compare, and analyze Link-State (Dijkstra / OSPF) and Distance-Vector (Bellman-Ford / RIP) network routing protocols under static and dynamic network failure conditions.

---

## ❓ Slide 2: Problem Statement

### The Problem in Computer Networking Education & System Design:
1. **Black-Box Nature of Production Routers**: Real network routers (Cisco, Juniper) run routing protocols invisibly in hardware. Students and engineers struggle to observe step-by-step route calculations and message exchanges.
2. **Dynamic Convergence Complexity**: When a physical fiber link severs or router cost changes, understanding how routers restabilize, re-route packets, and avoid routing loops (Count-to-Infinity) is difficult without live visual stepping.
3. **Heavy Reliance on Black-Box Libraries**: Existing academic demos rely on pre-built graph libraries (`networkx.dijkstra_path`), obscuring the underlying data structures (Min-Heaps, Distance Vector exchange matrices, Split Horizon).

---

## 💡 Slide 3: Solution & Core Utility

### What This Project Solves & Why It Is Useful:
- **Transparent Pure-Python Engines**: Implements Dijkstra and Bellman-Ford algorithms 100% from scratch using custom data structures (Min-Heap, Adjacency Lists, Distance Matrices).
- **Interactive Visual Stepper**: Provides line-by-line step-by-step execution playback showing algorithm decisions at each exact micro-step.
- **Dynamic Failure & Convergence Simulator**: Allows users to sever links (`LINK_DOWN`), restore links (`LINK_UP`), or change link costs dynamically and inspect re-convergence iterations in real time.
- **Explicit Forwarding Tables**: Generates standard router forwarding tables displaying `[Destination | Next Hop | Cost | Path]`.

---

## 🏗️ Slide 4: System Architecture & Modules

```
                                  +---------------------------------------+
                                  |         Streamlit Visual UI           |
                                  |  - Visual Canvas & Stepper Controls   |
                                  |  - Live Routing & Vector Tables       |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       Dynamic Event Simulator         |
                                  |  - Link Cuts, Restores, Cost Changes  |
                                  |  - Tracks Re-Convergence Iterations   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
+-----------------------------------------------------+-----------------------------------------------------+
|                                            Algorithm Engines                                              |
|  1. DijkstraEngine (Link-State / OSPF)                              2. BellmanFordEngine (Distance-Vector / RIP) |
|     - Custom Min-Heap Priority Queue                                   - Distance-Vector Matrices D_u(v)      |
|     - Step-by-step trace snapshot array                                - Split Horizon & Poison Reverse       |
+-----------------------------------------------------+-----------------------------------------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |           Graph Data Model            |
                                  |  - Pure Python Adjacency List Graph   |
                                  |  - Active/Inactive Node & Link Flags  |
                                  +---------------------------------------+
```

---

## 📊 Slide 5: Algorithm Comparison Highlighted in Simulator

| Parameter | Link-State (Dijkstra / OSPF) | Distance-Vector (Bellman-Ford / RIP) |
| :--- | :--- | :--- |
| **Network Knowledge** | Full topology map known globally by all routers | Routing by rumor (shares vectors with direct neighbors only) |
| **Data Structure** | Custom Min-Heap Priority Queue ($O(E \log V)$) | Synchronous Iterative Round Matrices ($O(V \cdot E)$) |
| **Loop Prevention** | Naturally loop-free via shortest path tree | Supported via Split Horizon & Poison Reverse flags |
| **Convergence Speed** | Fast re-convergence upon topology change | Iterative convergence across rounds |

---

## 🚀 Slide 6: Current Project Status & Live Demo

### Completed Work (Review 1 Deliverables):
- ✅ Core Graph Data Structure ([src/graph.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/graph.py))
- ✅ Dijkstra Engine from scratch ([src/dijkstra.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/dijkstra.py))
- ✅ Bellman-Ford Engine from scratch ([src/bellman_ford.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/bellman_ford.py))
- ✅ Dynamic Network Event Simulator ([src/network_simulator/simulator.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/network_simulator/simulator.py))
- ✅ Interactive Streamlit GUI Web Dashboard ([app.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/app.py))
- ✅ Terminal CLI Demo Runner ([main.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/main.py))
- ✅ 100% Automated Unit Test Suite (`pytest` - 7/7 passing)

---

## 🔮 Slide 7: Future Scope & Roadmap (Review 2 & Final Review)

1. **Packet-Level Flow Animation**: Animate individual data packets traversing nodes in real-time along calculated shortest paths.
2. **Network Traffic & Latency Metrics**: Introduce link bandwidth, congestion modeling, and packet queueing delays.
3. **Exportable Network Logs**: Export routing convergence traces and PCAP/JSON event history.
