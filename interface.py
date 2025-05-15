import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graph import *
from path import *
from airspace import *


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Airspace Route Explorer - Version 3")
        self.current_graph = None
        self.current_airspace = None
        self.selected_nodes = []
        self.current_path = None
        self.current_reachable = None
        self.node_neighbors = None
        self.new_node_mode = False
        self.new_segment_mode = False
        self.delete_mode = False

        # Configuración de la ventana principal
        self.root.minsize(1000, 750)

        # Crear frames
        self.control_frame = tk.Frame(root, width=300, padx=10, pady=10, bg='#f0f0f0')
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas_frame = tk.Frame(root, bg='white')
        self.canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Configurar matplotlib en Tkinter
        self.fig, self.ax = plt.subplots(figsize=(9, 7), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        # Conectar eventos del gráfico
        self.canvas.mpl_connect('button_press_event', self.on_graph_click)

        # Configurar controles
        self.setup_controls()

        # Cargar ejemplo inicial
        self.show_example1()

    def heuristic(self, point1, point2):
        """Distancia euclidiana entre dos puntos para A*"""
        return ((point1.longitude - point2.longitude) ** 2 +
                (point1.latitude - point2.latitude) ** 2) ** 0.5

    def setup_controls(self):
        # Estilo
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TButton', padding=5)

        # Panel de selección de airspace
        airspace_frame = ttk.LabelFrame(self.control_frame, text="Airspace Selection", padding=10)
        airspace_frame.pack(fill=tk.X, pady=5)

        self.airspace_var = tk.StringVar()
        self.airspace_menu = ttk.Combobox(airspace_frame, textvariable=self.airspace_var,
                                          values=["Catalunya", "España", "Europa"], state='readonly')
        self.airspace_menu.pack(fill=tk.X, pady=5)
        self.airspace_menu.bind("<<ComboboxSelected>>", self.load_airspace)

        # Panel de operaciones básicas
        basic_frame = ttk.LabelFrame(self.control_frame, text="Basic Operations", padding=10)
        basic_frame.pack(fill=tk.X, pady=5)

        ttk.Button(basic_frame, text="Example Graph 1", command=self.show_example1).pack(fill=tk.X, pady=2)
        ttk.Button(basic_frame, text="Example Graph 2", command=self.show_example2).pack(fill=tk.X, pady=2)
        ttk.Button(basic_frame, text="Clear", command=self.clear_graph).pack(fill=tk.X, pady=2)

        # Panel de gestión de grafos
        manage_frame = ttk.LabelFrame(self.control_frame, text="Graph Management", padding=10)
        manage_frame.pack(fill=tk.X, pady=5)

        ttk.Button(manage_frame, text="Load Graph", command=self.load_graph).pack(fill=tk.X, pady=2)
        ttk.Button(manage_frame, text="Save Graph", command=self.save_graph).pack(fill=tk.X, pady=2)
        ttk.Button(manage_frame, text="Add Node", command=self.toggle_add_node_mode).pack(fill=tk.X, pady=2)
        ttk.Button(manage_frame, text="Add Segment", command=self.toggle_add_segment_mode).pack(fill=tk.X, pady=2)
        ttk.Button(manage_frame, text="Delete Node", command=self.toggle_delete_mode).pack(fill=tk.X, pady=2)

        # Panel de análisis
        analysis_frame = ttk.LabelFrame(self.control_frame, text="Analysis Tools", padding=10)
        analysis_frame.pack(fill=tk.X, pady=5)

        # Modo de selección
        self.mode_var = tk.StringVar(value="select")
        ttk.Radiobutton(analysis_frame, text="Select Mode", variable=self.mode_var, value="select").pack(anchor=tk.W)
        ttk.Radiobutton(analysis_frame, text="Reachability Mode", variable=self.mode_var, value="reach").pack(
            anchor=tk.W)
        ttk.Radiobutton(analysis_frame, text="Shortest Path Mode", variable=self.mode_var, value="path").pack(
            anchor=tk.W)

        # Botones de acción
        ttk.Button(analysis_frame, text="Find Reachable Nodes", command=self.find_reachable_interactive).pack(fill=tk.X,
                                                                                                              pady=5)
        ttk.Button(analysis_frame, text="Find Shortest Path", command=self.find_shortest_path_interactive).pack(
            fill=tk.X, pady=5)
        ttk.Button(analysis_frame, text="Show Node Neighbors", command=self.show_node_neighbors).pack(fill=tk.X, pady=5)
        ttk.Button(analysis_frame, text="Clear Analysis", command=self.clear_analysis).pack(fill=tk.X, pady=5)

        # Panel de información
        info_frame = ttk.LabelFrame(self.control_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.X, pady=5)

        self.info_text = tk.Text(info_frame, height=10, width=30, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Barra de estado
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.control_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_add_node_mode(self):
        self.new_node_mode = not self.new_node_mode
        self.new_segment_mode = False
        self.delete_mode = False
        if self.new_node_mode:
            self.update_status("Add Node Mode: Click on the canvas to add a new node")
        else:
            self.update_status("Ready")
        self.mode_var.set("select")

    def toggle_add_segment_mode(self):
        if self.current_airspace:
            messagebox.showinfo("Information", "Cannot add segments in Airspace mode")
            return

        self.new_segment_mode = not self.new_segment_mode
        self.new_node_mode = False
        self.delete_mode = False
        if self.new_segment_mode:
            self.update_status("Add Segment Mode: Select two nodes to connect")
        else:
            self.update_status("Ready")
        self.mode_var.set("select")

    def toggle_delete_mode(self):
        if self.current_airspace:
            messagebox.showinfo("Information", "Cannot delete nodes in Airspace mode")
            return

        self.delete_mode = not self.delete_mode
        self.new_node_mode = False
        self.new_segment_mode = False
        if self.delete_mode:
            self.update_status("Delete Mode: Click on a node to delete it")
        else:
            self.update_status("Ready")
        self.mode_var.set("select")

    def on_graph_click(self, event):
        if not event.inaxes:
            return

        if self.current_airspace:
            # Modo airspace
            clicked_node = self.find_closest_navpoint(event.xdata, event.ydata)
            if not clicked_node:
                return

            if self.delete_mode:
                return  # No permitir eliminar en airspace

            mode = self.mode_var.get()
            if mode == "select":
                self.select_navpoint(clicked_node)
            elif mode == "reach":
                self.find_reachable_from(clicked_node.number)
            elif mode == "path":
                if len(self.selected_nodes) < 2:
                    self.select_navpoint(clicked_node)
                    if len(self.selected_nodes) == 2:
                        self.find_shortest_path_between(
                            self.selected_nodes[0].number,
                            self.selected_nodes[1].number
                        )
        else:
            # Modo grafo normal
            if self.new_node_mode:
                self.add_new_node(event.xdata, event.ydata)
                return

            clicked_node = GetClosest(self.current_graph, event.xdata, event.ydata)
            if not clicked_node:
                return

            if self.delete_mode:
                self.delete_node(clicked_node)
                return

            if self.new_segment_mode:
                self.add_new_segment(clicked_node)
                return

            mode = self.mode_var.get()
            if mode == "select":
                self.select_node(clicked_node)
            elif mode == "reach":
                self.find_reachable_from(clicked_node.name)
            elif mode == "path":
                if len(self.selected_nodes) < 2:
                    self.select_node(clicked_node)
                    if len(self.selected_nodes) == 2:
                        self.find_shortest_path_between(
                            self.selected_nodes[0].name,
                            self.selected_nodes[1].name
                        )

    def add_new_node(self, x, y):
        if self.current_airspace:
            messagebox.showwarning("Warning", "Cannot add nodes in Airspace mode")
            self.new_node_mode = False
            return

        # Crear diálogo para nombre del nodo
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Node")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Node Name:").pack(pady=5)
        name_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=name_var)
        entry.pack(pady=5)

        def confirm():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Node name cannot be empty")
                return

            if self.current_graph is None:
                self.current_graph = Graph()

            # Verificar si el nodo ya existe
            if any(node.name == name for node in self.current_graph.nodes):
                messagebox.showwarning("Warning", f"Node '{name}' already exists")
                return

            # Añadir nuevo nodo
            new_node = Node(name, x, y)
            AddNode(self.current_graph, new_node)
            self.plot_graph()
            self.update_status(f"Added new node: {name}")
            dialog.destroy()
            self.new_node_mode = False

        ttk.Button(dialog, text="Add", command=confirm).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=10, pady=10)
        entry.focus_set()

    def add_new_segment(self, node):
        if self.current_airspace:
            messagebox.showwarning("Warning", "Cannot add segments in Airspace mode")
            self.new_segment_mode = False
            return

        self.selected_nodes.append(node)
        if len(self.selected_nodes) > 2:
            self.selected_nodes.pop(0)

        # Resaltar nodos seleccionados
        self.plot_graph()

        if len(self.selected_nodes) == 2:
            origin = self.selected_nodes[0]
            dest = self.selected_nodes[1]

            # Generar nombre automático para el segmento
            segment_name = f"{origin.name}-{dest.name}"

            # Usar la función AddSegment del grafo
            success = AddSegment(self.current_graph, segment_name, origin.name, dest.name)

            if success:
                self.plot_graph()
                self.update_status(f"Added segment: {origin.name} → {dest.name}")
            else:
                messagebox.showwarning("Warning",
                                       "Segment already exists or nodes not found")

            # Resetear selección y modo
            self.selected_nodes = []
            self.new_segment_mode = False
            self.mode_var.set("select")  # Volver al modo selección

    def delete_node(self, node):
        if self.current_airspace:
            messagebox.showwarning("Warning", "Cannot delete nodes in Airspace mode")
            self.delete_mode = False
            return

        # Confirmar eliminación
        if not messagebox.askyesno("Confirm", f"Delete node '{node.name}' and all connected segments?"):
            return

        # Eliminar el nodo y sus segmentos asociados
        self.current_graph.nodes = [n for n in self.current_graph.nodes if n != node]
        self.current_graph.segments = [seg for seg in self.current_graph.segments
                                       if seg.origin != node and seg.destination != node]

        # Limpiar selecciones si el nodo estaba seleccionado
        self.selected_nodes = [n for n in self.selected_nodes if n != node]

        self.plot_graph()
        self.update_status(f"Deleted node: {node.name}")
        self.delete_mode = False

    def find_closest_navpoint(self, lon, lat):
        """Encuentra el punto de navegación más cercano a las coordenadas dadas"""
        if not self.current_airspace:
            return None

        closest = None
        min_dist = float('inf')

        for point in self.current_airspace.nav_points:
            dist = (point.longitude - lon) ** 2 + (point.latitude - lat) ** 2
            if dist < min_dist:
                min_dist = dist
                closest = point

        # Solo devolver si está suficientemente cerca (umbral de 0.01 grados)
        return closest if min_dist < 0.01 else None

    def select_navpoint(self, navpoint):  # Corregido de naypoint a navpoint
        """Maneja la selección de un punto de navegación en el modo airspace"""
        self.selected_nodes.append(navpoint)
        if len(self.selected_nodes) > 2:
            self.selected_nodes.pop(0)

        self.plot_airspace()
        info_text = f"Selected: {navpoint.name} ({navpoint.number})\n"
        info_text += f"Coordinates: {navpoint.latitude:.6f}, {navpoint.longitude:.6f}"
        self.update_info(info_text)

    def select_node(self, node):
        self.selected_nodes.append(node)
        if len(self.selected_nodes) > 2:
            self.selected_nodes.pop(0)

        self.plot_graph()
        self.update_info(f"Selected: {node.name}")

    def find_reachable_from(self, start_name):
        """Maneja la búsqueda de nodos alcanzables desde la interfaz"""
        if self.current_airspace:
            start_point = next((p for p in self.current_airspace.nav_points
                                if p.number == start_name), None)
            if not start_point:
                self.update_info(f"No se encontró el punto {start_name}")
                return

            # Usar BFS para encontrar nodos alcanzables
            reachable = []
            visited = set()
            queue = [start_point.number]

            while queue:
                current_num = queue.pop(0)
                if current_num in visited:
                    continue

                visited.add(current_num)
                current_point = next((p for p in self.current_airspace.nav_points
                                      if p.number == current_num), None)
                if current_point:
                    reachable.append(current_point)

                    # Añadir vecinos no visitados
                    for seg in self.current_airspace.nav_segments:
                        if seg.origin_number == current_num:
                            if seg.destination_number not in visited:
                                queue.append(seg.destination_number)

            self.current_reachable = reachable
            self.plot_airspace()
            self.update_info(f"Nodos alcanzables desde {start_point.name}:\n" +
                             "\n".join([f"- {p.name}" for p in reachable]))
        else:
            reachable_nodes = GetReachableNodes(self.current_graph, start_name)
            if not reachable_nodes:
                self.update_info(f"No se encontró el nodo {start_name}")
                return

            self.current_reachable = reachable_nodes
            self.plot_graph()
            self.update_info(f"Nodos alcanzables desde {start_name}:\n" +
                             "\n".join([f"- {node.name}" for node in reachable_nodes]))

    def show_node_neighbors(self):
        if not self.selected_nodes:
            messagebox.showwarning("Warning", "Please select a node first")
            return

        if self.current_airspace:
            node = self.selected_nodes[0]
            neighbors = []
            for seg in self.current_airspace.nav_segments:
                if seg.origin_number == node.number:
                    dest = next((p for p in self.current_airspace.nav_points
                                 if p.number == seg.destination_number), None)
                    if dest:
                        neighbors.append(f"{dest.name} (distance: {seg.distance:.1f} km)")
            self.node_neighbors = neighbors
            self.plot_airspace()
            self.update_info(f"Neighbors of {node.name}:\n" + "\n".join(neighbors))
        else:
            node = self.selected_nodes[0]
            neighbors = []
            for seg in self.current_graph.segments:
                if seg.origin == node:
                    neighbors.append(f"{seg.destination.name} (cost: {seg.cost:.1f})")
                elif seg.destination == node:
                    neighbors.append(f"{seg.origin.name} (cost: {seg.cost:.1f})")
            self.node_neighbors = neighbors
            self.plot_graph()
            self.update_info(f"Neighbors of {node.name}:\n" + "\n".join(neighbors))

    def find_shortest_path_between(self, start_name, end_name):
        """Encuentra y dibuja el camino más corto entre dos puntos"""
        if self.current_airspace:
            # 1. Obtener los puntos de inicio y fin
            start_point = next((p for p in self.current_airspace.nav_points
                                if p.number == start_name), None)
            end_point = next((p for p in self.current_airspace.nav_points
                              if p.number == end_name), None)

            if not start_point or not end_point:
                self.update_info("Error: Puntos no encontrados")
                return

            # 2. Implementación del algoritmo A*
            open_set = {start_point.number}
            came_from = {}
            g_score = {p.number: float('inf') for p in self.current_airspace.nav_points}
            g_score[start_point.number] = 0
            f_score = {p.number: float('inf') for p in self.current_airspace.nav_points}
            f_score[start_point.number] = self.heuristic(start_point, end_point)

            while open_set:
                current_num = min(open_set, key=lambda x: f_score[x])
                if current_num == end_point.number:
                    # Reconstruir el camino
                    path_points = []
                    current = end_point.number
                    while current in came_from:
                        path_points.append(next(p for p in self.current_airspace.nav_points
                                                if p.number == current))
                        current = came_from[current]
                    path_points.append(start_point)
                    path_points.reverse()

                    # Crear objeto Path
                    path = Path()
                    path.points = path_points
                    path.cost = g_score[end_point.number]

                    self.current_path = path
                    self.plot_airspace()
                    self.update_info(f"Camino más corto:\n{' -> '.join([p.name for p in path_points])}\n"
                                     f"Distancia total: {path.cost:.2f} km")
                    return

                open_set.remove(current_num)

                # Explorar vecinos
                for seg in self.current_airspace.nav_segments:
                    if seg.origin_number == current_num:
                        neighbor_num = seg.destination_number
                        tentative_g = g_score[current_num] + seg.distance

                        if tentative_g < g_score.get(neighbor_num, float('inf')):
                            came_from[neighbor_num] = current_num
                            g_score[neighbor_num] = tentative_g
                            neighbor_point = next((p for p in self.current_airspace.nav_points
                                                   if p.number == neighbor_num), None)
                            if neighbor_point:
                                f_score[neighbor_num] = tentative_g + self.heuristic(neighbor_point, end_point)
                                if neighbor_num not in open_set:
                                    open_set.add(neighbor_num)

            self.update_info("No hay camino entre los puntos seleccionados")
        else:
            path = FindShortestPath(self.current_graph, start_name, end_name)
            if path:
                self.current_path = path
                self.plot_graph()
                path_names = [node.name for node in path.nodes]
                self.update_info(f"Camino más corto:\n{' -> '.join(path_names)}\nCosto total: {path.cost:.2f}")
            else:
                self.update_info(f"No existe camino entre {start_name} y {end_name}")

    def find_reachable_interactive(self):
        if not self.selected_nodes:
            messagebox.showwarning("Warning", "Please select a starting point first")
            return

        if self.current_airspace:
            self.find_reachable_from(self.selected_nodes[0].number)
        else:
            self.find_reachable_from(self.selected_nodes[0].name)

    def find_shortest_path_interactive(self):
        if len(self.selected_nodes) < 2:
            messagebox.showwarning("Warning", "Please select two points first")
            return

        if self.current_airspace:
            self.find_shortest_path_between(
                self.selected_nodes[0].number,
                self.selected_nodes[1].number
            )
        else:
            self.find_shortest_path_between(
                self.selected_nodes[0].name,
                self.selected_nodes[1].name
            )

    def clear_analysis(self):
        self.current_path = None
        self.current_reachable = None
        self.node_neighbors = None
        self.selected_nodes = []

        if self.current_airspace:
            self.plot_airspace()
        else:
            self.plot_graph()

        self.update_info("Analysis cleared")

    def update_info(self, message):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, message)

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def load_airspace(self, event=None):
        selected = self.airspace_var.get()
        if not selected:
            return

        self.update_status(f"Loading {selected} airspace...")

        try:
            if selected == "Catalunya":
                nav_file = "Cat_nav.txt"
                seg_file = "Cat_seg.txt"
                airport_file = "Cat_ger.txt"
            elif selected == "España":
                nav_file = "Spa_nav.txt"
                seg_file = "Spa_seg.txt"
                airport_file = "Spa_ger.txt"
            else:  # Europa
                nav_file = "Eur_nav.txt"
                seg_file = "Eur_seg.txt"
                airport_file = "Eur_ger.txt"

            self.current_airspace = LoadAirspace(nav_file, seg_file, airport_file)

            # Llamada al diagnóstico (solo para desarrollo)
            self.check_airspace_data(self.current_airspace)

            self.current_graph = None
            self.clear_analysis()
            self.plot_airspace()
            self.update_status(f"{selected} airspace loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load airspace: {str(e)}")
            self.update_status("Error loading airspace")
            # También muestra el error en consola para diagnóstico
            print(f"Error loading airspace: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_graph(self):
        file_path = filedialog.askopenfilename(title="Load Graph",
                                               filetypes=[("Graph files", "*.graph"),
                                                          ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                self.current_graph = Graph()
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()
                    if parts[0] == "Node":
                        name = parts[1]
                        x = float(parts[2])
                        y = float(parts[3])
                        node = Node(name, x, y)
                        AddNode(self.current_graph, node)
                    elif parts[0] == "Segment":
                        origin_name = parts[1]
                        dest_name = parts[2]
                        cost = float(parts[3])
                        origin = next((n for n in self.current_graph.nodes if n.name == origin_name), None)
                        dest = next((n for n in self.current_graph.nodes if n.name == dest_name), None)
                        if origin and dest:
                            segment = Segment(f"{origin_name}-{dest_name}", origin, dest, cost)
                            self.current_graph.segments.append(segment)
                            AddNeighbor(origin, dest)
                            AddNeighbor(dest, origin)

            self.current_airspace = None
            self.clear_analysis()
            self.plot_graph()
            self.update_status(f"Graph loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load graph: {str(e)}")
            self.update_status("Error loading graph")

    def save_graph(self):
        if not self.current_graph or len(self.current_graph.nodes) == 0:
            messagebox.showwarning("Warning", "No graph to save")
            return

        file_path = filedialog.asksaveasfilename(title="Save Graph",
                                                 defaultextension=".graph",
                                                 filetypes=[("Graph files", "*.graph"),
                                                            ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'w') as f:
                f.write("# Graph data\n")
                for node in self.current_graph.nodes:
                    f.write(f"Node {node.name} {node.x} {node.y}\n")
                for seg in self.current_graph.segments:
                    f.write(f"Segment {seg.origin.name} {seg.destination.name} {seg.cost}\n")

            self.update_status(f"Graph saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save graph: {str(e)}")
            self.update_status("Error saving graph")

    def plot_airspace(self):
        if not self.current_airspace:
            return

        self.ax.clear()

        # 1. Dibujar todos los segmentos (en gris)
        for segment in self.current_airspace.nav_segments:
            origin = next((p for p in self.current_airspace.nav_points
                           if p.number == segment.origin_number), None)
            dest = next((p for p in self.current_airspace.nav_points
                         if p.number == segment.destination_number), None)

            if origin and dest:
                # Resaltar segmentos del camino
                is_path_segment = False
                if self.current_path and hasattr(self.current_path, 'points'):
                    path_points = self.current_path.points
                    for i in range(len(path_points) - 1):
                        if (segment.origin_number == path_points[i].number and
                                segment.destination_number == path_points[i + 1].number):
                            is_path_segment = True
                            break

                if is_path_segment:
                    self.ax.plot([origin.longitude, dest.longitude],
                                 [origin.latitude, dest.latitude],
                                 color='red', linewidth=3, alpha=0.8)
                else:
                    self.ax.plot([origin.longitude, dest.longitude],
                                 [origin.latitude, dest.latitude],
                                 color='gray', linewidth=1, alpha=0.3)

        # 2. Dibujar puntos
        for point in self.current_airspace.nav_points:
            # Determinar color
            if self.current_path and any(p.number == point.number
                                         for p in self.current_path.points):
                color = 'red'  # Puntos del camino
                size = 10
            elif any(p.number == point.number for p in self.selected_nodes):
                color = 'blue'  # Puntos seleccionados
                size = 12
            else:
                color = 'green'  # Puntos normales
                size = 6

            self.ax.plot(point.longitude, point.latitude, 'o',
                         markersize=size, color=color)
            self.ax.text(point.longitude, point.latitude + 0.02, point.name,
                         fontsize=8, ha='center')

        # Configuración final del gráfico
        if self.current_airspace.nav_points:
            lons = [p.longitude for p in self.current_airspace.nav_points]
            lats = [p.latitude for p in self.current_airspace.nav_points]
            self.ax.set_xlim(min(lons) - 0.5, max(lons) + 0.5)
            self.ax.set_ylim(min(lats) - 0.5, max(lats) + 0.5)

        self.ax.set_title("Catalunya Airspace", pad=20)
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.ax.grid(True, linestyle=':', alpha=0.3)
        self.canvas.draw()


    def show_example1(self):
        self.update_status("Loading example graph 1...")
        self.current_graph = CreateGraph_1()
        self.current_airspace = None
        self.clear_analysis()
        self.plot_graph()

    def show_example2(self):
        self.update_status("Loading example graph 2...")
        self.current_graph = CreateGraph_2()
        self.current_airspace = None
        self.clear_analysis()
        self.plot_graph()

    def plot_graph(self):
        if not self.current_graph:
            return

        self.ax.clear()

        # Dibujar todos los segmentos (en gris por defecto)
        for seg in self.current_graph.segments:
            seg_color = 'gray'
            seg_alpha = 0.3
            seg_linewidth = 1.5

            # Resaltar segmentos del camino más corto
            if self.current_path:
                path_nodes = self.current_path.nodes if hasattr(self.current_path, 'nodes') else []
                for i in range(len(path_nodes) - 1):
                    if (seg.origin == path_nodes[i] and seg.destination == path_nodes[i + 1]) or \
                            (seg.origin == path_nodes[i + 1] and seg.destination == path_nodes[i]):
                        seg_color = 'red'
                        seg_alpha = 0.8
                        seg_linewidth = 2.5
                        break

            self.ax.plot([seg.origin.x, seg.destination.x],
                         [seg.origin.y, seg.destination.y],
                         color=seg_color, alpha=seg_alpha, linewidth=seg_linewidth)

            # Dibujar flecha de dirección (solo para segmentos no resaltados)
            if seg_color == 'gray':
                self.ax.annotate('', xy=(seg.destination.x, seg.destination.y),
                                 xytext=(seg.origin.x, seg.origin.y),
                                 arrowprops=dict(arrowstyle='->', color=seg_color, alpha=seg_alpha))

            # Etiqueta de costo
            mid_x = (seg.origin.x + seg.destination.x) / 2
            mid_y = (seg.origin.y + seg.destination.y) / 2
            self.ax.text(mid_x, mid_y, f"{seg.cost:.1f}",
                         fontsize=7, ha='center', va='center',
                         bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))

        # Dibujar nodos
        for node in self.current_graph.nodes:
            # Color por defecto
            color = 'blue'
            size = 6

            # Resaltar si está seleccionado
            if any(n.name == node.name for n in self.selected_nodes):
                color = 'red'
                size = 8
            # Resaltar si es alcanzable
            elif self.current_reachable and any(n.name == node.name
                                                for n in self.current_reachable):
                color = 'green'
                size = 7
            # Resaltar si es parte del camino
            elif self.current_path and any(n.name == node.name
                                           for n in self.current_path.nodes):
                color = 'purple'
                size = 8
            # Resaltar si es vecino (cuando se muestran vecinos)
            elif self.node_neighbors is not None and any(
                    node.name == n.split(' ')[0] for n in self.node_neighbors
            ):
                color = 'orange'
                size = 7

            self.ax.plot(node.x, node.y, 'o', markersize=size, color=color)
            self.ax.text(node.x, node.y + 0.5, node.name,
                         fontsize=8, ha='center', va='bottom')

        # Configuración del gráfico
        self.ax.set_title("Graph Visualization", pad=20)
        self.ax.grid(True, alpha=0.2)
        self.canvas.draw()

    def clear_graph(self):
        self.current_graph = Graph()
        self.current_airspace = None
        self.clear_analysis()
        self.plot_graph()
        self.update_status("Graph cleared")

    def check_airspace_data(self, airspace):
        """Función para verificar la carga correcta de datos"""
        print(f"\nDiagnóstico del espacio aéreo:")
        print(f"- Puntos de navegación cargados: {len(airspace.nav_points)}")
        print(f"- Segmentos cargados: {len(airspace.nav_segments)}")
        print(f"- Aeropuertos cargados: {len(airspace.nav_airports)}")

        # Mostrar primeros 3 elementos de cada tipo
        print("\nPrimeros 3 puntos de navegación:")
        for p in airspace.nav_points[:3]:
            print(f"{p.number} {p.name} ({p.latitude}, {p.longitude})")

        print("\nPrimeros 3 segmentos:")
        for s in airspace.nav_segments[:3]:
            print(f"{s.origin_number} -> {s.destination_number} ({s.distance} km)")

        print("\nAeropuertos:")
        for a in airspace.nav_airports:
            print(f"{a.name} - SIDs: {len(a.sids)}, STARs: {len(a.stars)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
