from node import Distance


class Path:
    def __init__(self, start_node=None):
        self.nodes = []
        self.cost = 0.0
        if start_node:
            self.nodes.append(start_node)

    def __repr__(self):
        return f"Path(cost={self.cost:.2f}, nodes={[n.name for n in self.nodes]})"

    def add_node(self, node, cost):
        self.nodes.append(node)
        self.cost += cost

    def contains_node(self, node):
        return node in self.nodes

    def cost_to_node(self, node):
        if not self.contains_node(node):
            return -1
        # In a simple path, the cost is cumulative
        # For more complex paths, we'd need to track segment costs
        return self.cost  # Simplified version

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
