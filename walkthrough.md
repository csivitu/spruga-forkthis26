# Walkthrough - Network Shortest Path Simulator Modules

Implemented `src/graph.py`, `src/dijkstra.py`, and `src/bellman_ford.py` with explicit routing table outputs showing: `[Destination | Next Hop | Cost | Path]`.

## 📁 Created Modules

### 1. `src/graph.py`
- [src/graph.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/graph.py)
- Custom pure-Python `Graph` adjacency list model.
- Supports directed/undirected edges, link costs, node/edge active flags (`is_edge_active`, `is_node_active`), link cut/restore actions, and neighbor queries.

### 2. `src/dijkstra.py`
- [src/dijkstra.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/dijkstra.py)
- Dijkstra's Link-State algorithm implemented from scratch using a custom binary min-heap priority queue (`MinHeap`).
- `dijkstra(graph, source)` returns explicit routing tables:
  ```json
  [
    {
      "Destination": "Router_D",
      "Next Hop": "Router_C",
      "Cost": 8.0,
      "Path": ["Router_A", "Router_C", "Router_B", "Router_D"]
    }
  ]
  ```

### 3. `src/bellman_ford.py`
- [src/bellman_ford.py](file:///c:/Users/aravi/Downloads/VIT_STUDIES/Comp_Netw/PROJECT_SPRUGA/SPRUGA-/src/bellman_ford.py)
- Bellman-Ford Distance-Vector protocol implemented from scratch.
- Supports round-by-round Distance Vector exchange, Split Horizon, Poison Reverse, and negative weight cycle detection.
- `bellman_ford(graph, source)` returns explicit routing tables:
  ```json
  [
    {
      "Destination": "Router_D",
      "Next Hop": "Router_C",
      "Cost": 8.0,
      "Path": ["Router_A", "Router_C", "Router_B", "Router_D"]
    }
  ]
  ```

---

## 🧪 Verification Results

Ran automated unit test suite:
```powershell
.\venv\Scripts\pytest
```

Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\aravi\Downloads\VIT_STUDIES\Comp_Netw\PROJECT_SPRUGA\SPRUGA-
plugins: anyio-4.14.2
collected 7 items

tests\test_algorithms.py ...                                             [ 42%]
tests\test_graph.py ..                                                   [ 71%]
tests\test_simulator.py ..                                               [100%]

============================== 7 passed in 0.09s ==============================
```
