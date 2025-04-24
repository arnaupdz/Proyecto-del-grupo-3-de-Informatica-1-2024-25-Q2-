from graph import *
from path import Path

def test_reachability():
    G = CreateGraph_1()
    print("\nTesting reachability from node D:")
    reachable = GetReachableNodes(G, "D")
    print("Reachable nodes:", [n.name for n in reachable])
    
    print("Plotting reachable nodes...")
    PlotReachableNodes(G, "D")

def test_shortest_path():
    G = CreateGraph_1()
    print("\nTesting shortest path from B to F:")
    path = FindShortestPath(G, "B", "F")
    if path:
        print("Shortest path found:", [n.name for n in path.nodes])
        print("Total cost:", path.cost)
        PlotPath(G, path)
    else:
        print("No path found")

if __name__ == "__main__":
    print("Testing graph functions...")
    G = CreateGraph_1()
    Plot(G)
    
    test_reachability()
    test_shortest_path()
    
    # Also test with the simple graph
    G2 = CreateGraph_2()
    Plot(G2)
    
    print("\nTesting shortest path in simple graph (X to Z):")
    path = FindShortestPath(G2, "X", "Z")
    if path:
        print("Shortest path found:", [n.name for n in path.nodes])
        print("Total cost:", path.cost)
        PlotPath(G2, path)
