from node import Node
from path import Path, AddNodeToPath, ContainsNode, CostToNode, PlotPath
from graph import Graph, AddNode, AddSegment

def test_path_functions():
    print("Testing Path functions...")
    
    # Create some nodes
    n1 = Node("A", 0, 0)
    n2 = Node("B", 3, 4)
    n3 = Node("C", 6, 0)
    
    # Test basic Path functionality
    p = Path(n1)
    print(p)  # Should show path with just A
    
    # Test AddNodeToPath
    p2 = AddNodeToPath(p, n2, 5.0)
    print(p2)  # Should show path A->B with cost 5.0
    
    # Test ContainsNode
    print("Contains B:", ContainsNode(p2, n2))  # True
    print("Contains C:", ContainsNode(p2, n3))  # False
    
    # Test CostToNode
    print("Cost to B:", CostToNode(p2, n2))  # 5.0
    print("Cost to C:", CostToNode(p2, n3))  # -1
    
    # Test PlotPath with a simple graph
    g = Graph()
    AddNode(g, n1)
    AddNode(g, n2)
    AddNode(g, n3)
    AddSegment(g, "AB", "A", "B")
    AddSegment(g, "BC", "B", "C")
    
    p3 = Path(n1)
    p3 = AddNodeToPath(p3, n2, 5.0)
    p3 = AddNodeToPath(p3, n3, 5.0)
    
    print("Showing path plot...")
    PlotPath(g, p3)

if __name__ == "__main__":
    test_path_functions()
