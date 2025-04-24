from node import Node, AddNeighbor, Distance
from segment import Segment
import matplotlib.pyplot as plt
import math


class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []

    def __repr__(self):
        return f"Graph with {len(self.nodes)} nodes and {len(self.segments)} segments"


def AddNode(g, n):
    for node in g.nodes:
        if node.name == n.name:
            return False
    g.nodes.append(n)
    return True


def AddSegment(g, name, nameOrigin, nameDestination):
    origin = None
    destination = None

    for node in g.nodes:
        if node.name == nameOrigin:
            origin = node
        if node.name == nameDestination:
            destination = node

    if origin is None or destination is None:
        return False

    segment = Segment(name, origin, destination)
    g.segments.append(segment)
    AddNeighbor(origin, destination)
    return True


def GetClosest(g, x, y):
    if not g.nodes:
        return None

    closest = g.nodes[0]
    min_dist = math.sqrt((closest.x - x) ** 2 + (closest.y - y) ** 2)

    for node in g.nodes[1:]:
        dist = math.sqrt((node.x - x) ** 2 + (node.y - y) ** 2)
        if dist < min_dist:
            min_dist = dist
            closest = node

    return closest


def Plot(g):
    plt.figure(figsize=(10, 8))

    # Draw segments
    for seg in g.segments:
        plt.plot([seg.origin.x, seg.destination.x],
                 [seg.origin.y, seg.destination.y],
                 'k-', alpha=0.5)

        # Add arrow
        plt.annotate('', xy=(seg.destination.x, seg.destination.y),
                     xytext=(seg.origin.x, seg.origin.y),
                     arrowprops=dict(arrowstyle='->', color='black'))

        # Add cost label
        mid_x = (seg.origin.x + seg.destination.x) / 2
        mid_y = (seg.origin.y + seg.destination.y) / 2
        plt.text(mid_x, mid_y, f"{seg.cost:.1f}",
                 bbox=dict(facecolor='white', alpha=0.7))

    # Draw nodes
    for node in g.nodes:
        plt.plot(node.x, node.y, 'o', markersize=10, color='blue')
        plt.text(node.x, node.y + 0.5, node.name,
                 ha='center', va='center', fontsize=10)

    plt.grid(True)
    plt.title("Graph Visualization")
    plt.show()


def PlotNode(g, nameOrigin):
    origin = None
    for node in g.nodes:
        if node.name == nameOrigin:
            origin = node
            break

    if origin is None:
        return False

    plt.figure(figsize=(10, 8))

    # Draw all segments first (gray)
    for seg in g.segments:
        plt.plot([seg.origin.x, seg.destination.x],
                 [seg.origin.y, seg.destination.y],
                 'k-', alpha=0.2)

    # Highlight origin node and its neighbors
    neighbor_names = [n.name for n in origin.neighbors]

    # Draw all nodes
    for node in g.nodes:
        if node.name == nameOrigin:
            color = 'blue'
            size = 12
        elif node.name in neighbor_names:
            color = 'green'
            size = 10
        else:
            color = 'gray'
            size = 8

        plt.plot(node.x, node.y, 'o', markersize=size, color=color)
        plt.text(node.x, node.y + 0.5, node.name,
                 ha='center', va='center', fontsize=10)

    # Highlight segments from origin to neighbors (red)
    for seg in g.segments:
        if seg.origin.name == nameOrigin:
            plt.plot([seg.origin.x, seg.destination.x],
                     [seg.origin.y, seg.destination.y],
                     'r-', alpha=0.7)

            # Add arrow
            plt.annotate('', xy=(seg.destination.x, seg.destination.y),
                         xytext=(seg.origin.x, seg.origin.y),
                         arrowprops=dict(arrowstyle='->', color='red'))

            # Add cost label
            mid_x = (seg.origin.x + seg.destination.x) / 2
            mid_y = (seg.origin.y + seg.destination.y) / 2
            plt.text(mid_x, mid_y, f"{seg.cost:.1f}",
                     bbox=dict(facecolor='white', alpha=0.7))

    plt.grid(True)
    plt.title(f"Node {nameOrigin} and its neighbors")
    plt.show()
    return True


def LoadGraphFromFile(filename):
    g = Graph()
    try:
        with open(filename, 'r') as f:
            mode = None
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line == "[NODES]":
                    mode = "NODES"
                    continue
                elif line == "[SEGMENTS]":
                    mode = "SEGMENTS"
                    continue

                if mode == "NODES":
                    parts = line.split(',')
                    if len(parts) >= 3:
                        name = parts[0].strip()
                        x = float(parts[1].strip())
                        y = float(parts[2].strip())
                        AddNode(g, Node(name, x, y))

                elif mode == "SEGMENTS":
                    parts = line.split(',')
                    if len(parts) >= 3:
                        seg_name = parts[0].strip()
                        origin = parts[1].strip()
                        dest = parts[2].strip()
                        AddSegment(g, seg_name, origin, dest)

        return g
    except Exception as e:
        print(f"Error loading graph: {e}")
        return None


def SaveGraphToFile(g, filename):
    try:
        with open(filename, 'w') as f:
            f.write("# Graph file format\n")
            f.write("[NODES]\n")
            for node in g.nodes:
                f.write(f"{node.name}, {node.x}, {node.y}\n")

            f.write("\n[SEGMENTS]\n")
            for seg in g.segments:
                f.write(f"{seg.name}, {seg.origin.name}, {seg.destination.name}\n")

        return True
    except Exception as e:
        print(f"Error saving graph: {e}")
        return False


def RemoveNode(g, node_name):
    node_to_remove = None
    for node in g.nodes:
        if node.name == node_name:
            node_to_remove = node
            break

    if node_to_remove is None:
        return False

    # Remove segments connected to this node
    segments_to_remove = []
    for seg in g.segments:
        if seg.origin.name == node_name or seg.destination.name == node_name:
            segments_to_remove.append(seg)

    for seg in segments_to_remove:
        g.segments.remove(seg)

    # Remove from neighbors lists of other nodes
    for node in g.nodes:
        if node_to_remove in node.neighbors:
            node.neighbors.remove(node_to_remove)

    # Remove the node
    g.nodes.remove(node_to_remove)
    return True


def CreateGraph_1():
    G = Graph()
    AddNode(G, Node("A", 1, 20))
    AddNode(G, Node("B", 8, 17))
    AddNode(G, Node("C", 15, 20))
    AddNode(G, Node("D", 18, 15))
    AddNode(G, Node("E", 2, 4))
    AddNode(G, Node("F", 6, 5))
    AddNode(G, Node("G", 12, 12))
    AddNode(G, Node("H", 10, 3))
    AddNode(G, Node("I", 19, 1))
    AddNode(G, Node("J", 13, 5))
    AddNode(G, Node("K", 3, 15))
    AddNode(G, Node("L", 4, 10))

    AddSegment(G, "AB", "A", "B")
    AddSegment(G, "AE", "A", "E")
    AddSegment(G, "AK", "A", "K")
    AddSegment(G, "BA", "B", "A")
    AddSegment(G, "BC", "B", "C")
    AddSegment(G, "BF", "B", "F")
    AddSegment(G, "BK", "B", "K")
    AddSegment(G, "BG", "B", "G")
    AddSegment(G, "CD", "C", "D")
    AddSegment(G, "CG", "C", "G")
    AddSegment(G, "DG", "D", "G")
    AddSegment(G, "DH", "D", "H")
    AddSegment(G, "DI", "D", "I")
    AddSegment(G, "EF", "E", "F")
    AddSegment(G, "FL", "F", "L")
    AddSegment(G, "GB", "G", "B")
    AddSegment(G, "GF", "G", "F")
    AddSegment(G, "GH", "G", "H")
    AddSegment(G, "ID", "I", "D")
    AddSegment(G, "IJ", "I", "J")
    AddSegment(G, "JI", "J", "I")
    AddSegment(G, "KA", "K", "A")
    AddSegment(G, "KL", "K", "L")
    AddSegment(G, "LK", "L", "K")
    AddSegment(G, "LF", "L", "F")
    return G


def CreateGraph_2():
    G = Graph()
    AddNode(G, Node("X", 5, 5))
    AddNode(G, Node("Y", 10, 5))
    AddNode(G, Node("Z", 7.5, 10))

    AddSegment(G, "XY", "X", "Y")
    AddSegment(G, "YZ", "Y", "Z")
    AddSegment(G, "ZX", "Z", "X")
    AddSegment(G, "YX", "Y", "X")
    AddSegment(G, "ZY", "Z", "Y")
    AddSegment(G, "XZ", "X", "Z")
    return G
