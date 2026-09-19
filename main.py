"""CLI Demo Runner for Network Shortest Path Simulator."""

from src.graph import Graph
from src.dijkstra import dijkstra
from src.bellman_ford import bellman_ford


def run_demo():
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

    print("==========================================================================================")
    print(" DIJKSTRA LINK-STATE ROUTING TABLE (Source: Router_A)")
    print("==========================================================================================")
    print(f"{'Destination':<15} | {'Next Hop':<12} | {'Cost':<8} | {'Path'}")
    print("-" * 90)
    for row in dijkstra(g, "Router_A"):
        next_hop = row['Next Hop'] if row['Next Hop'] else 'None'
        path_str = " -> ".join(row['Path']) if row['Path'] else "None"
        cost_str = "inf" if row['Cost'] == float('inf') else f"{row['Cost']:g}"
        print(f"{row['Destination']:<15} | {next_hop:<12} | {cost_str:<8} | {path_str}")

    print("\n==========================================================================================")
    print(" BELLMAN-FORD DISTANCE-VECTOR ROUTING TABLE (Source: Router_A)")
    print("==========================================================================================")
    print(f"{'Destination':<15} | {'Next Hop':<12} | {'Cost':<8} | {'Path'}")
    print("-" * 90)
    for row in bellman_ford(g, "Router_A"):
        next_hop = row['Next Hop'] if row['Next Hop'] else 'None'
        path_str = " -> ".join(row['Path']) if row['Path'] else "None"
        cost_str = "inf" if row['Cost'] == float('inf') else f"{row['Cost']:g}"
        print(f"{row['Destination']:<15} | {next_hop:<12} | {cost_str:<8} | {path_str}")
    print("==========================================================================================")


if __name__ == "__main__":
    run_demo()
