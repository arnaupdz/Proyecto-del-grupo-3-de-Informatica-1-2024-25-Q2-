import matplotlib.pyplot as plt
from node import Node, Distance, AddNeighbor
from segment import Segment


class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []


def AddNode(g, n):
    for node in g.nodes:
        if node.name == n.name:
            return False
    g.nodes.append(n)
    return True


def AddSegment(g, name, nameOrigin, nameDestination):
    origin = None
    destination = None

    i = 0
    while i < len(g.nodes) and (origin is None or destination is None):
        if g.nodes[i].name == nameOrigin:
            origin = g.nodes[i]
        elif g.nodes[i].name == nameDestination:
            destination = g.nodes[i]
        i += 1

    if origin is None or destination is None:
        return False

    g.segments.append(Segment(name, origin, destination))
    AddNeighbor(origin, destination)
    return True


def GetClosest(g, x, y):
    closest = g.nodes[0]
    min_distance = Distance(closest, Node("", x, y))

    for node in g.nodes[1:]:
        d = Distance(node, Node("", x, y))
        if d < min_distance:
            closest = node
            min_distance = d

    return closest


def Plot(g):
    plt.figure(figsize=(10, 8))

    for segment in g.segments:
        x1, y1 = segment.origin.x, segment.origin.y
        x2, y2 = segment.destination.x, segment.destination.y
        dx, dy = x2 - x1, y2 - y1

        length = (dx ** 2 + dy ** 2) ** 0.5
        if length > 0:
            dx_norm, dy_norm = dx / length, dy / length
            end_x = x2 - dx_norm * 0.2
            end_y = y2 - dy_norm * 0.2
            plt.arrow(x1, y1, end_x - x1, end_y - y1,
                      head_width=0.2, head_length=0.3,
                      fc='black', ec='black', length_includes_head=True)

        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        plt.text(mid_x, mid_y, f"{segment.cost:.1f}", fontsize=9, color="red")

    for node in g.nodes:
        plt.scatter(node.x, node.y, c="gray", s=100, zorder=3)
        plt.text(node.x, node.y, f" {node.name}", fontsize=12, zorder=4)

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Graph Representation with Arrows")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def PlotNode(g, nameOrigin):
    origin = None
    i = 0

    while i < len(g.nodes):
        if g.nodes[i].name == nameOrigin:
            origin = g.nodes[i]
            break
        i += 1

    if origin is None:
        return False

    plt.figure(figsize=(10, 8))

    for segment in g.segments:
        x1, y1 = segment.origin.x, segment.origin.y
        x2, y2 = segment.destination.x, segment.destination.y
        dx, dy = x2 - x1, y2 - y1

        length = (dx ** 2 + dy ** 2) ** 0.5
        if length > 0:
            dx_norm, dy_norm = dx / length, dy / length
            end_x = x2 - dx_norm * 0.2
            end_y = y2 - dy_norm * 0.2

            color = 'red' if segment.origin == origin else 'black'
            plt.arrow(x1, y1, end_x - x1, end_y - y1,
                      head_width=0.3, head_length=0.4,
                      fc=color, ec=color, length_includes_head=True)

    for node in g.nodes:
        color = "blue" if node == origin else ("green" if node in origin.neighbors else "gray")
        plt.scatter(node.x, node.y, c=color, s=100, zorder=3)
        plt.text(node.x, node.y, f" {node.name}", fontsize=12, zorder=4)

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title(f"Node {nameOrigin} and its Neighbors")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return True


def BuildGraphFromFile(filename="test_graph_data.txt"):
    g = Graph()

    file = open(filename, 'r')
    lines = file.readlines()
    file.close()

    nodes_section = True

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line == '---':
            nodes_section = False
            continue

        if nodes_section:
            parts = line.split()
            if len(parts) == 3:
                name = parts[0]
                x = float(parts[1])
                y = float(parts[2])
                AddNode(g, Node(name, x, y))

        else:
            parts = line.split()
            if len(parts) == 4:
                name = parts[0]
                origin = parts[1]
                destination = parts[2]
                cost = float(parts[3])
                if AddSegment(g, name, origin, destination):
                    for seg in g.segments:
                        if seg.name == name:
                            seg.cost = cost

    return g
