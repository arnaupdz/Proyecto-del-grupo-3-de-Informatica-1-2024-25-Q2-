from node import Distance


class Path:
    def __init__(self):
        self.points = []  # Para airspace (lista de NavPoint)
        self.nodes = []  # Para grafos normales (lista de Node)
        self.cost = 0

    def __repr__(self):
        node_names = [n.name for n in self.nodes]
        return f"Path(cost={self.cost:.2f}, nodes={' -> '.join(node_names)})"

    def add_node(self, node, cost):
        self.nodes.append(node)
        self.cost += cost

    def contains_node(self, node):
        return node in self.nodes

    def copy(self):
        new_path = Path()
        new_path.nodes = self.nodes.copy()
        new_path.cost = self.cost
        return new_path


def AddNodeToPath(path, node, cost):
    new_path = path.copy()
    new_path.add_node(node, cost)
    return new_path


def ContainsNode(path, node):
    return path.contains_node(node)


def CostToNode(path, node):
    return path.cost_to_node(node)


def GetReachableNodes(graph, start_node_name):
    """
    Encuentra todos los nodos alcanzables desde un nodo inicial (BFS)

    Args:
        graph (Graph): Grafo a analizar
        start_node_name (str): Nombre del nodo inicial

    Returns:
        list: Lista de nodos alcanzables
    """
    # Encontrar el nodo inicial
    start_node = next((n for n in graph.nodes if n.name == start_node_name), None)
    if not start_node:
        return []

    visited = set()
    queue = [start_node]
    reachable = []

    while queue:
        current = queue.pop(0)

        if current in visited:
            continue

        visited.add(current)
        reachable.append(current)

        # Obtener vecinos usando el método del grafo
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited and neighbor not in queue:
                queue.append(neighbor)

    return reachable


def FindShortestPath(graph, start_node_name, end_node_name, debug=False):
    class Path:
        def __init__(self, nodes, cost):
            self.nodes = nodes
            self.cost = cost

    print(f"\nBuscando camino de {start_node_name} a {end_node_name}") if debug else None

    start_node = next((n for n in graph.nodes if n.name == start_node_name), None)
    end_node = next((n for n in graph.nodes if n.name == end_node_name), None)

    if not start_node:
        print(f"Nodo inicial {start_node_name} no encontrado") if debug else None
        return None
    if not end_node:
        print(f"Nodo final {end_node_name} no encontrado") if debug else None
        return None

    distances = {node: float('inf') for node in graph.nodes}
    previous = {node: None for node in graph.nodes}
    distances[start_node] = 0
    unvisited = set(graph.nodes)

    while unvisited:
        current = min(unvisited, key=lambda node: distances[node])
        print(f"\nNodo actual: {current.name} (distancia: {distances[current]})") if debug else None

        if distances[current] == float('inf'):
            print("Todos los nodos restantes son inalcanzables") if debug else None
            break

        if current == end_node:
            print("¡Destino alcanzado!") if debug else None
            break

        unvisited.remove(current)

        for segment in graph.segments:
            neighbor = None
            if segment.origin == current:
                neighbor = segment.destination
            elif segment.destination == current:
                neighbor = segment.origin

            if neighbor and neighbor in unvisited:
                new_dist = distances[current] + segment.cost
                print(f"Vecino: {neighbor.name}, costo: {segment.cost}, nueva distancia: {new_dist}") if debug else None

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    print(f"Actualizada distancia a {neighbor.name} = {new_dist}") if debug else None

    if previous[end_node] is None and start_node != end_node:
        print("No hay camino al nodo destino") if debug else None
        return None

    path_nodes = []
    current = end_node
    while current is not None:
        path_nodes.insert(0, current)
        current = previous[current]

    print(f"Camino encontrado: {[n.name for n in path_nodes]}") if debug else None
    print(f"Costo total: {distances[end_node]}") if debug else None

    return Path(path_nodes, distances[end_node])

def PlotPath(graph, path):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 8))

    # Draw all nodes and segments first (light colors)
    for seg in graph.segments:
        plt.plot([seg.origin.x, seg.destination.x],
                 [seg.origin.y, seg.destination.y],
                 'k-', alpha=0.1)

    for node in graph.nodes:
        plt.plot(node.x, node.y, 'o', markersize=8, color='gray')
        plt.text(node.x, node.y + 0.5, node.name,
                 ha='center', va='center', fontsize=8, color='gray')

    # Highlight the path
    if len(path.nodes) > 1:
        for i in range(len(path.nodes) - 1):
            start = path.nodes[i]
            end = path.nodes[i + 1]

            # Find the segment between these nodes
            seg = None
            for s in graph.segments:
                if s.origin == start and s.destination == end:
                    seg = s
                    break

            if seg:
                plt.plot([start.x, end.x], [start.y, end.y],
                         'r-', linewidth=2, alpha=0.7)

                # Add arrow
                plt.annotate('', xy=(end.x, end.y),
                             xytext=(start.x, start.y),
                             arrowprops=dict(arrowstyle='->', color='red', linewidth=2))

                # Add cost label
                mid_x = (start.x + end.x) / 2
                mid_y = (start.y + end.y) / 2
                plt.text(mid_x, mid_y, f"{seg.cost:.1f}",
                         bbox=dict(facecolor='white', alpha=0.9))

    # Highlight path nodes
    for node in path.nodes:
        plt.plot(node.x, node.y, 'o', markersize=10, color='blue')
        plt.text(node.x, node.y + 0.5, node.name,
                 ha='center', va='center', fontsize=10, color='blue')

    plt.grid(True)
    plt.title(f"Path Visualization (Total cost: {path.cost:.2f})")
    plt.show()
