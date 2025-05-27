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


def FindAlternativePath(graph, start_name, end_name, avoid_nodes):
    """Encuentra un camino alternativo evitando nodos específicos (usa Dijkstra modificado)."""
    start_node = next((node for node in graph.nodes if node.name == start_name), None)
    end_node = next((node for node in graph.nodes if node.name == end_name), None)

    if not start_node or not end_node:
        return None

    # Inicialización
    distances = {node.name: float('inf') for node in graph.nodes}
    distances[start_name] = 0
    previous = {node.name: None for node in graph.nodes}
    unvisited = set(node.name for node in graph.nodes if node.name not in avoid_nodes)  # Ignorar nodos a evitar

    while unvisited:
        current_name = min(unvisited, key=lambda name: distances[name])
        unvisited.remove(current_name)

        if current_name == end_name:
            path = Path()
            path.nodes = []
            path.cost = distances[end_name]

            current = end_name
            while current:
                node = next((n for n in graph.nodes if n.name == current), None)
                path.nodes.insert(0, node)
                current = previous[current]

            return path

        current_node = next((node for node in graph.nodes if node.name == current_name), None)
        for neighbor in current_node.neighbors:
            if neighbor.name in avoid_nodes:  # Saltar nodos prohibidos
                continue

            segment = next((seg for seg in graph.segments
                            if (seg.origin == current_node and seg.destination == neighbor) or
                            (seg.origin == neighbor and seg.destination == current_node)), None)
            if segment:
                distance = distances[current_name] + segment.cost
                if distance < distances[neighbor.name]:
                    distances[neighbor.name] = distance
                    previous[neighbor.name] = current_name

    return None  # No hay camino válido


def FindShortestPath(graph, start_node_name, end_node_name):
    """
    Implementación del algoritmo A* para encontrar el camino más corto entre dos nodos
    Args:
        graph: Objeto Graph que contiene nodos y segmentos
        start_node_name: Nombre del nodo de inicio
        end_node_name: Nombre del nodo destino
    Returns:
        Objeto Path con los nodos del camino y el costo total, o None si no hay camino
    """
    # 1. Obtener los nodos de inicio y fin
    start_node = next((n for n in graph.nodes if n.name == start_node_name), None)
    end_node = next((n for n in graph.nodes if n.name == end_node_name), None)

    if not start_node or not end_node:
        return None  # No existe alguno de los nodos

    # 2. Función heurística (distancia euclidiana entre nodos)
    def heuristic(node):
        return ((node.x - end_node.x) ** 2 + (node.y - end_node.y) ** 2) ** 0.5

    # 3. Inicializar estructuras de datos
    open_set = {start_node}  # Nodos por explorar
    came_from = {}  # Diccionario para reconstruir el camino

    # g_score[n] = costo real desde el inicio hasta n
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start_node] = 0

    # f_score[n] = g_score[n] + heurística estimada al destino
    f_score = {node: float('inf') for node in graph.nodes}
    f_score[start_node] = heuristic(start_node)

    # 4. Bucle principal del algoritmo A*
    while open_set:
        # Seleccionar nodo con menor f_score
        current = min(open_set, key=lambda node: f_score[node])

        # Si llegamos al destino, reconstruir el camino
        if current == end_node:
            path_nodes = []
            while current in came_from:
                path_nodes.insert(0, current)
                current = came_from[current]
            path_nodes.insert(0, start_node)

            # Crear objeto Path con el camino encontrado
            path = Path()
            path.nodes = path_nodes
            path.cost = g_score[end_node]
            return path

        open_set.remove(current)

        # Explorar vecinos
        for neighbor in current.neighbors:
            # Calcular nuevo g_score tentativo
            segment_cost = graph.get_segment_cost(current, neighbor)
            if segment_cost is None:
                continue  # No hay segmento entre estos nodos

            tentative_g = g_score[current] + segment_cost

            # Si encontramos un mejor camino al vecino
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                if neighbor not in open_set:
                    open_set.add(neighbor)

    # Si llegamos aquí, no hay camino
    return None

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
