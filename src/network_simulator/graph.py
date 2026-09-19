"""Re-export NetworkGraph from src.graph."""

from src.graph import Graph as NetworkGraph, Graph

__all__ = ["NetworkGraph", "Graph"]
