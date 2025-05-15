from node import Node, AddNeighbor, Distance
from segment import Segment
import matplotlib.pyplot as plt
from path import Path
import math
import os



class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []

    def __repr__(self):
        return f"Graph with {len(self.nodes)} nodes and {len(self.segments)} segments"

    def get_neighbors(self, node):
        """Obtiene todos los vecinos de un nodo"""
        neighbors = []
        for seg in self.segments:
            if seg.origin == node:
                neighbors.append(seg.destination)
            elif seg.destination == node:
                neighbors.append(seg.origin)
        return neighbors

    def get_segment_cost(self, node1, node2):
        """Obtiene el costo del segmento entre dos nodos"""
        for seg in self.segments:
            if (seg.origin == node1 and seg.destination == node2) or \
                    (seg.origin == node2 and seg.destination == node1):
                return seg.cost
        return None


def AddNode(g, n):
    """Add a node to the graph if it doesn't already exist"""
    if any(node.name == n.name for node in g.nodes):
        return False
    g.nodes.append(n)
    return True


def AddSegment(g, name, origin_name, destination_name):
    """
    Añade un segmento al grafo

    Args:
        g (Graph): Grafo al que añadir el segmento
        name (str): Nombre del segmento
        origin_name (str): Nombre del nodo origen
        destination_name (str): Nombre del nodo destino

    Returns:
        bool: True si se añadió correctamente, False si no
    """
    origin = next((n for n in g.nodes if n.name == origin_name), None)
    destination = next((n for n in g.nodes if n.name == destination_name), None)

    if not origin or not destination:
        return False

    # Verificar si el segmento ya existe
    if any(seg.origin == origin and seg.destination == destination for seg in g.segments):
        return False

    # Calcular costo (distancia euclidiana)
    cost = ((destination.x - origin.x) ** 2 + (destination.y - origin.y) ** 2) ** 0.5

    # Crear el segmento
    new_segment = Segment(name, origin, destination, cost)
    g.segments.append(new_segment)

    # Añadir como vecinos
    AddNeighbor(origin, destination)

    return True


def GetClosest(g, x, y):
    """Find the node closest to the given coordinates"""
    if not g.nodes:
        return None

    return min(g.nodes, key=lambda node: (node.x - x) ** 2 + (node.y - y) ** 2)


def Plot(g, highlight_path=None):
    """Plot the entire graph, optionally highlighting a specific path"""
    plt.figure(figsize=(10, 8))
    ax = plt.gca()

    # Draw all segments first
    for seg in g.segments:
        color = 'black'
        alpha = 0.5
        linewidth = 1

        # Check if this segment is part of the highlighted path
        if highlight_path and seg in highlight_path.segments:
            color = 'red'
            alpha = 0.9
            linewidth = 2

        plt.plot([seg.origin.x, seg.destination.x],
                 [seg.origin.y, seg.destination.y],
                 color=color, alpha=alpha, linewidth=linewidth)

        # Add cost label
        mid_x = (seg.origin.x + seg.destination.x) / 2
        mid_y = (seg.origin.y + seg.destination.y) / 2
        ax.text(mid_x, mid_y, f"{seg.cost:.1f}",
                bbox=dict(facecolor='white', alpha=0.7), ha='center', va='center')

    # Draw all nodes
    for node in g.nodes:
        color = 'blue'
        size = 8
        alpha = 1

        # Highlight nodes in the path if specified
        if highlight_path and node in highlight_path.nodes:
            color = 'red'
            size = 10

        plt.plot(node.x, node.y, 'o', markersize=size, color=color, alpha=alpha)
        ax.text(node.x, node.y + 0.5, node.name,
                ha='center', va='center', fontsize=10)

    plt.grid(True)
    title = "Graph Visualization"
    if highlight_path:
        title += f" - Path cost: {highlight_path.cost:.2f}"
    plt.title(title)
    plt.tight_layout()
    plt.show()


def PlotNode(g, nameOrigin):
    """Plot a specific node and its neighbors"""
    origin = next((node for node in g.nodes if node.name == nameOrigin), None)
    if origin is None:
        return False

    plt.figure(figsize=(10, 8))
    ax = plt.gca()

    # Get neighbor names for quick lookup
    neighbor_names = {n.name for n in origin.neighbors}

    # Draw all segments first (gray)
    for seg in g.segments:
        color = 'gray' if seg.origin != origin else 'red'
        alpha = 0.2 if seg.origin != origin else 0.7
        plt.plot([seg.origin.x, seg.destination.x],
                 [seg.origin.y, seg.destination.y],
                 color=color, alpha=alpha)

    # Draw all nodes with appropriate colors
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
        ax.text(node.x, node.y + 0.5, node.name,
                ha='center', va='center', fontsize=10)

    # Highlight segments from origin to neighbors with cost labels
    for seg in g.segments:
        if seg.origin.name == nameOrigin:
            mid_x = (seg.origin.x + seg.destination.x) / 2
            mid_y = (seg.origin.y + seg.destination.y) / 2
            ax.text(mid_x, mid_y, f"{seg.cost:.1f}",
                    bbox=dict(facecolor='white', alpha=0.7), ha='center', va='center')

    plt.grid(True)
    plt.title(f"Node {nameOrigin} and its neighbors")
    plt.tight_layout()
    plt.show()
    return True


def LoadGraphFromFile(filename):
    """Load graph from a text file with [NODES] and [SEGMENTS] sections"""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return None

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
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        name = parts[0]
                        try:
                            x = float(parts[1])
                            y = float(parts[2])
                            AddNode(g, Node(name, x, y))
                        except ValueError:
                            print(f"Warning: Invalid coordinates for node {name}")

                elif mode == "SEGMENTS":
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        seg_name = parts[0]
                        origin = parts[1]
                        dest = parts[2]
                        if not AddSegment(g, seg_name, origin, dest):
                            print(f"Warning: Could not add segment {seg_name} from {origin} to {dest}")

        return g
    except Exception as e:
        print(f"Error loading graph: {e}")
        return None


def SaveGraphToFile(g, filename):
    """Save graph to a text file in the same format"""
    try:
        with open(filename, 'w') as f:
            f.write("# Graph file\n")
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
    """Remove a node and all connected segments"""
    node_to_remove = next((node for node in g.nodes if node.name == node_name), None)
    if node_to_remove is None:
        return False

    # Remove segments connected to this node
    g.segments = [seg for seg in g.segments
                  if seg.origin.name != node_name and seg.destination.name != node_name]

    # Remove from neighbors lists of other nodes
    for node in g.nodes:
        if node_to_remove in node.neighbors:
            node.neighbors.remove(node_to_remove)

    # Remove the node
    g.nodes.remove(node_to_remove)
    return True


def RemoveSegment(g, origin_name, destination_name):
    """Remove a specific segment between two nodes"""
    origin = next((node for node in g.nodes if node.name == origin_name), None)
    destination = next((node for node in g.nodes if node.name == destination_name), None)

    if origin is None or destination is None:
        return False

    # Remove the segment if it exists
    segments_to_remove = [seg for seg in g.segments
                          if seg.origin == origin and seg.destination == destination]

    if not segments_to_remove:
        return False

    for seg in segments_to_remove:
        g.segments.remove(seg)

    # Update neighbors if no other segments exist between these nodes
    if not any(seg.origin == origin and seg.destination == destination for seg in g.segments):
        if destination in origin.neighbors:
            origin.neighbors.remove(destination)

    return True


def CreateGraph_1():
    """Create the first example graph"""
    G = Graph()
    nodes = [
        Node("A", 1, 20), Node("B", 8, 17), Node("C", 15, 20),
        Node("D", 18, 15), Node("E", 2, 4), Node("F", 6, 5),
        Node("G", 12, 12), Node("H", 10, 3), Node("I", 19, 1),
        Node("J", 13, 5), Node("K", 3, 15), Node("L", 4, 10)
    ]

    for node in nodes:
        AddNode(G, node)

    segments = [
        ("AB", "A", "B"), ("AE", "A", "E"), ("AK", "A", "K"),
        ("BA", "B", "A"), ("BC", "B", "C"), ("BF", "B", "F"),
        ("BK", "B", "K"), ("BG", "B", "G"), ("CD", "C", "D"),
        ("CG", "C", "G"), ("DG", "D", "G"), ("DH", "D", "H"),
        ("DI", "D", "I"), ("EF", "E", "F"), ("FL", "F", "L"),
        ("GB", "G", "B"), ("GF", "G", "F"), ("GH", "G", "H"),
        ("ID", "I", "D"), ("IJ", "I", "J"), ("JI", "J", "I"),
        ("KA", "K", "A"), ("KL", "K", "L"), ("LK", "L", "K"),
        ("LF", "L", "F")
    ]

    for name, origin, dest in segments:
        AddSegment(G, name, origin, dest)

    return G


def CreateGraph_2():
    """Create a second example graph (simple triangle)"""
    G = Graph()
    nodes = [Node("X", 5, 5), Node("Y", 10, 5), Node("Z", 7.5, 10)]

    for node in nodes:
        AddNode(G, node)

    segments = [
        ("XY", "X", "Y"), ("YZ", "Y", "Z"), ("ZX", "Z", "X"),
        ("YX", "Y", "X"), ("ZY", "Z", "Y"), ("XZ", "X", "Z")
    ]

    for name, origin, dest in segments:
        AddSegment(G, name, origin, dest)

    return G


def GetReachableNodes(graph, start_node_name):
    """
    Encuentra todos los nodos alcanzables desde un nodo inicial usando BFS

    Args:
        graph (Graph): Grafo a analizar
        start_node_name (str): Nombre del nodo inicial

    Returns:
        list: Lista de nodos alcanzables (objetos Node)
    """
    # Encontrar el nodo inicial
    start_node = None
    for node in graph.nodes:
        if node.name == start_node_name:
            start_node = node
            break

    if not start_node:
        return []

    visited = set()
    queue = [start_node]  # Usamos una lista como cola
    reachable = []

    while queue:
        current = queue.pop(0)  # Sacamos el primer elemento

        if current in visited:
            continue

        visited.add(current)
        reachable.append(current)

        # Añadir vecinos no visitados
        for neighbor in current.neighbors:
            if neighbor not in visited and neighbor not in queue:
                queue.append(neighbor)

    return reachable


def PlotReachableNodes(g, start_node_name):
    """Plot the graph highlighting reachable nodes from start_node"""
    reachable = GetReachableNodes(g, start_node_name)
    if not reachable:
        return False

    plt.figure(figsize=(10, 8))
    ax = plt.gca()

    # Draw all nodes
    for node in g.nodes:
        if node.name == start_node_name:
            color, size, alpha = 'blue', 12, 1.0
        elif node in reachable:
            color, size, alpha = 'green', 10, 1.0
        else:
            color, size, alpha = 'gray', 8, 0.5

        plt.plot(node.x, node.y, 'o', markersize=size, color=color, alpha=alpha)
        ax.text(node.x, node.y + 0.5, node.name,
                ha='center', va='center', fontsize=10, alpha=alpha)

    # Draw all segments
    for seg in g.segments:
        if seg.origin in reachable and seg.destination in reachable:
            color, alpha = 'green', 0.7
        else:
            color, alpha = 'gray', 0.2

        plt.plot([seg.origin.x, seg.destination.x],
                 [seg.origin.y, seg.destination.y],
                 color=color, alpha=alpha)

    plt.grid(True)
    plt.title(f"Reachable nodes from {start_node_name} (Total: {len(reachable)})")
    plt.tight_layout()
    plt.show()
    return True


def FindShortestPath(graph, start_node_name, end_node_name):
    """
    Encuentra el camino más corto entre dos nodos usando Dijkstra

    Args:
        graph (Graph): Grafo a analizar
        start_node_name (str): Nombre del nodo inicial
        end_node_name (str): Nombre del nodo destino

    Returns:
        dict: {'path': lista de nombres de nodos, 'cost': costo total}
              o None si no hay camino
    """
    # Encontrar nodos de inicio y fin
    start_node = end_node = None
    for node in graph.nodes:
        if node.name == start_node_name:
            start_node = node
        if node.name == end_node_name:
            end_node = node

    if not start_node or not end_node:
        return None

    # Estructuras para el algoritmo
    distances = {node: float('inf') for node in graph.nodes}
    previous = {node: None for node in graph.nodes}
    distances[start_node] = 0
    unvisited = set(graph.nodes)

    while unvisited:
        # Encontrar el nodo no visitado con la distancia mínima
        current = None
        min_dist = float('inf')
        for node in unvisited:
            if distances[node] < min_dist:
                min_dist = distances[node]
                current = node

        if current is None or current == end_node:
            break

        unvisited.remove(current)

        # Actualizar distancias a los vecinos
        for neighbor in current.neighbors:
            # Encontrar el segmento entre current y neighbor
            segment = None
            for seg in graph.segments:
                if (seg.origin == current and seg.destination == neighbor) or \
                        (seg.origin == neighbor and seg.destination == current):
                    segment = seg
                    break

            if segment:
                alt = distances[current] + segment.cost
                if alt < distances[neighbor]:
                    distances[neighbor] = alt
                    previous[neighbor] = current

    # Reconstruir el camino si existe
    if previous[end_node] is None and start_node != end_node:
        return None

    path = []
    current = end_node
    while current is not None:
        path.insert(0, current)
        current = previous[current]

    return {
        'path': [node.name for node in path],
        'cost': distances[end_node]
    }


def PlotShortestPath(g, origin_name, destination_name):
    """Find and plot the shortest path between two nodes"""
    path = FindShortestPath(g, origin_name, destination_name)
    if not path:
        print(f"No path found from {origin_name} to {destination_name}")
        return False

    plt.figure(figsize=(10, 8))
    ax = plt.gca()

    # Draw all nodes
    for node in g.nodes:
        if node.name == origin_name:
            color, size = 'blue', 12
        elif node.name == destination_name:
            color, size = 'purple', 12
        elif node in path.nodes:
            color, size = 'red', 10
        else:
            color, size = 'gray', 8

        plt.plot(node.x, node.y, 'o', markersize=size, color=color)
        ax.text(node.x, node.y + 0.5, node.name,
                ha='center', va='center', fontsize=10)

    # Draw all segments
    for seg in g.segments:
        if seg in path.segments:
            color, alpha, width = 'red', 0.9, 2
        else:
            color, alpha, width = 'gray', 0.2, 1

        plt.plot([seg.origin.x, seg.destination.x],
                 [seg.origin.y, seg.destination.y],
                 color=color, alpha=alpha, linewidth=width)

    plt.grid(True)
    plt.title(f"Shortest path from {origin_name} to {destination_name}\nTotal cost: {path.cost:.2f}")
    plt.tight_layout()
    plt.show()
    return True
