# Network Shortest Path Simulator - Project Flowcharts

This document contains 3 comprehensive flowcharts visualizing:
1. **Project Development & Architecture Procedure**
2. **Dijkstra's Link-State Algorithm Execution Flow**
3. **Bellman-Ford-Moore (BFM) Distance-Vector Algorithm Execution Flow**

---

## 1. Project Development Procedure Flowchart

Visualization of how the project components were designed, integrated, and verified from scratch.

```mermaid
flowchart TD
    A["Project Initiation"] --> B["1. Core Data Model (src/graph.py)"]
    B --> C["Adjacency List Graph & Link Active Flags"]
    C --> D["2. Algorithm Engines from Scratch"]
    D --> E["src/dijkstra.py (Custom MinHeap)"]
    D --> F["src/bellman_ford.py (Distance Vectors)"]
    E --> G["3. Routing Table Formatter"]
    F --> G
    G --> H["Schema: [Destination | Next Hop | Cost | Path]"]
    H --> I["4. Dynamic Event Simulator (simulator.py)"]
    I --> J["5. Interfaces & Verification"]
    J --> K["Streamlit Web App (app.py)"]
    J --> L["CLI Demo Runner (main.py)"]
    J --> M["Pytest Suite (7/7 Passing)"]
```

---

## 2. Dijkstra's Algorithm (Link-State / OSPF) Execution Flowchart

Visualization of how the Dijkstra engine calculates shortest paths using a custom Binary Min-Heap Priority Queue and builds explicit routing tables.

```mermaid
flowchart TD
    Start["Start Dijkstra Engine"] --> Init["Initialize: dist[source]=0, dist[others]=inf, visited={}"]
    Init --> PQ["Push (cost=0, source) into Custom MinHeap"]
    PQ --> CheckPQ{"Is MinHeap Empty?"}
    CheckPQ -- Yes --> BuildTable["Build Forwarding Table: [Destination | Next Hop | Cost | Path]"]
    CheckPQ -- No --> PopMin["Pop router 'u' with min distance from MinHeap"]
    PopMin --> VisitedCheck{"Is 'u' already visited?"}
    VisitedCheck -- Yes --> CheckPQ
    VisitedCheck -- No --> MarkVisited["Mark 'u' as visited & Record Trace Step"]
    MarkVisited --> GetNeighbors["Fetch active neighbors 'v' of 'u'"]
    GetNeighbors --> LoopNeighbors{"For each unvisited neighbor 'v'"}
    LoopNeighbors -- End of Neighbors --> CheckPQ
    LoopNeighbors -- Process 'v' --> RelaxCost{"New Cost (dist[u] + weight) < dist[v]?"}
    RelaxCost -- Yes --> UpdateDist["Update dist[v] = new_cost, pred[v] = u"]
    UpdateDist --> DecreaseKey["Decrease Key in MinHeap for 'v'"]
    DecreaseKey --> RecordStep["Record Trace Step Snapshot"]
    RecordStep --> LoopNeighbors
    RelaxCost -- No --> SkipStep["Record No-Update Trace Step"]
    SkipStep --> LoopNeighbors
    BuildTable --> End["Return Explicit Routing Table"]
```

---

## 3. Bellman-Ford-Moore (BFM) Distance-Vector Execution Flowchart

Visualization of how the Bellman-Ford engine computes distance vectors round-by-round across routers, supporting Split Horizon and Poison Reverse.

```mermaid
flowchart TD
    Start["Start BFM Engine"] --> InitDV["Initialize Matrices: D[u][u]=0, D[u][v]=link cost, NH[u][v]=v"]
    InitDV --> InitRound["Set round iteration = 1, max_rounds = |V|"]
    InitRound --> RoundLoop{"Round <= max_rounds?"}
    RoundLoop -- No / Converged --> OutputTable["Build Forwarding Tables: [Destination | Next Hop | Cost | Path]"]
    RoundLoop -- Yes --> CopyMatrix["Copy Distance Matrix D to D_new for Synchronous Update"]
    CopyMatrix --> NodeLoop{"For each Router 'u'"}
    NodeLoop -- Done all Routers --> CheckConvergence{"Did any router update its Distance Vector in this round?"}
    CheckConvergence -- No (Converged) --> OutputTable
    CheckConvergence -- Yes & round == max_rounds --> NegCycle["Detect Negative Weight Cycle Error!"]
    CheckConvergence -- Yes & round < max_rounds --> NextRound["Increment round iteration"]
    NextRound --> RoundLoop
    NodeLoop -- Process 'u' --> NeighborLoop{"For each Neighbor 'w' of 'u'"}
    NeighborLoop -- Done all Neighbors --> NodeLoop
    NeighborLoop -- Process 'w' --> CheckSplitHorizon{"Is Split Horizon / Poison Reverse active for 'w'?"}
    CheckSplitHorizon -- Yes & NH[w][v]==u --> ApplyRule["Set advertised D[w][v] = inf (or Skip)"]
    ApplyRule --> EvaluateCost{"cost_via_w = cost(u,w) + D[w][v] < D_new[u][v]?"}
    CheckSplitHorizon -- No --> EvaluateCost
    EvaluateCost -- Yes --> UpdateDV["Update D_new[u][v] = cost_via_w, NH_new[u][v] = w"]
    UpdateDV --> MarkUpdated["Set updated_flag = True"]
    MarkUpdated --> NeighborLoop
    EvaluateCost -- No --> NeighborLoop
    OutputTable --> EndBFM["Return Explicit Routing Tables"]
```
