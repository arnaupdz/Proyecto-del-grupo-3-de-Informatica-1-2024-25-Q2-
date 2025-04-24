import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from graph import *
from path import PlotPath
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Visualization Tool")
        self.current_graph = None

        # Configure main window
        self.root.minsize(800, 600)

        # Create frames
        self.control_frame = tk.Frame(root, width=250, padx=5, pady=5)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas_frame = tk.Frame(root, bg='white')
        self.canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Graph control buttons
        control_label = tk.Label(self.control_frame, text="Graph Controls", font=('Arial', 10, 'bold'))
        control_label.pack(pady=5)

        button_frame = tk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=5)

        tk.Button(button_frame, text="Example Graph 1", command=self.show_example1).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Example Graph 2", command=self.show_example2).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Load Graph", command=self.load_graph).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Save Graph", command=self.save_graph).pack(fill=tk.X, pady=2)
        tk.Button(button_frame, text="Clear Graph", command=self.clear_graph).pack(fill=tk.X, pady=2)

        # Node controls
        node_label = tk.Label(self.control_frame, text="Node Operations", font=('Arial', 10, 'bold'))
        node_label.pack(pady=(10, 5))

        node_button_frame = tk.Frame(self.control_frame)
        node_button_frame.pack(fill=tk.X, pady=5)

        tk.Button(node_button_frame, text="Add Node", command=self.add_node_dialog).pack(side=tk.LEFT, expand=True,
                                                                                         padx=2)
        tk.Button(node_button_frame, text="Remove Node", command=self.remove_node_dialog).pack(side=tk.LEFT,
                                                                                               expand=True, padx=2)

        # Segment controls
        segment_label = tk.Label(self.control_frame, text="Segment Operations", font=('Arial', 10, 'bold'))
        segment_label.pack(pady=(10, 5))

        tk.Button(self.control_frame, text="Add Segment", command=self.add_segment_dialog).pack(fill=tk.X, pady=2)

        # Reachability controls
        reach_frame = tk.LabelFrame(self.control_frame, text="Reachability Analysis", padx=5, pady=5)
        reach_frame.pack(fill=tk.X, pady=5)

        self.reach_var = tk.StringVar()
        tk.Label(reach_frame, text="From Node:").pack(anchor='w')
        self.reach_menu = ttk.Combobox(reach_frame, textvariable=self.reach_var, state='readonly')
        self.reach_menu.pack(fill=tk.X, pady=2)

        tk.Button(reach_frame, text="Show Reachable Nodes", command=self.show_reachable).pack(fill=tk.X, pady=2)

        # Shortest Path controls
        path_frame = tk.LabelFrame(self.control_frame, text="Shortest Path", padx=5, pady=5)
        path_frame.pack(fill=tk.X, pady=5)

        tk.Label(path_frame, text="From:").pack(anchor='w')
        self.path_start_var = tk.StringVar()
        self.path_start_menu = ttk.Combobox(path_frame, textvariable=self.path_start_var, state='readonly')
        self.path_start_menu.pack(fill=tk.X, pady=2)

        tk.Label(path_frame, text="To:").pack(anchor='w')
        self.path_end_var = tk.StringVar()
        self.path_end_menu = ttk.Combobox(path_frame, textvariable=self.path_end_var, state='readonly')
        self.path_end_menu.pack(fill=tk.X, pady=2)

        tk.Button(path_frame, text="Find Shortest Path", command=self.find_shortest_path).pack(fill=tk.X, pady=2)

        # Node neighbors button
        tk.Button(self.control_frame, text="Show Node Neighbors", command=self.show_node_neighbors).pack(fill=tk.X,
                                                                                                         pady=10)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.control_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize with example graph
        self.show_example1()

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def update_node_menus(self):
        if self.current_graph is None:
            self.reach_menu['values'] = []
            self.path_start_menu['values'] = []
            self.path_end_menu['values'] = []
            return

        nodes = sorted([node.name for node in self.current_graph.nodes])
        self.reach_menu['values'] = nodes
        self.path_start_menu['values'] = nodes
        self.path_end_menu['values'] = nodes

        if nodes:
            if not self.reach_var.get() in nodes:
                self.reach_var.set(nodes[0])
            if not self.path_start_var.get() in nodes:
                self.path_start_var.set(nodes[0])
            if not self.path_end_var.get() in nodes:
                self.path_end_var.set(nodes[-1] if len(nodes) > 1 else nodes[0])

    def plot_graph(self, g=None):
        if g is None:
            g = self.current_graph

        if g is None:
            return

        self.ax.clear()
        self.update_node_menus()

        # Draw segments
        for seg in g.segments:
            self.ax.plot([seg.origin.x, seg.destination.x],
                         [seg.origin.y, seg.destination.y],
                         'k-', alpha=0.5)

            # Add arrow
            self.ax.annotate('', xy=(seg.destination.x, seg.destination.y),
                             xytext=(seg.origin.x, seg.origin.y),
                             arrowprops=dict(arrowstyle='->', color='black'))

            # Add cost label
            mid_x = (seg.origin.x + seg.destination.x) / 2
            mid_y = (seg.origin.y + seg.destination.y) / 2
            self.ax.text(mid_x, mid_y, f"{seg.cost:.1f}",
                         bbox=dict(facecolor='white', alpha=0.7))

        # Draw nodes
        for node in g.nodes:
            self.ax.plot(node.x, node.y, 'o', markersize=10, color='blue')
            self.ax.text(node.x, node.y + 0.5, node.name,
                         ha='center', va='center', fontsize=10)

        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("Graph Visualization", pad=20)
        self.canvas.draw()
        self.update_status(f"Graph displayed: {len(g.nodes)} nodes, {len(g.segments)} segments")

    def show_example1(self):
        self.update_status("Loading example graph 1...")
        self.current_graph = CreateGraph_1()
        self.plot_graph()

    def show_example2(self):
        self.update_status("Loading example graph 2...")
        self.current_graph = CreateGraph_2()
        self.plot_graph()

    def load_graph(self):
        filename = filedialog.askopenfilename(title="Select Graph File",
                                              filetypes=[("Text files", "*.txt")])
        if filename:
            self.update_status(f"Loading graph from {filename}...")
            self.current_graph = LoadGraphFromFile(filename)
            if self.current_graph:
                self.plot_graph()
                self.update_status(f"Graph loaded from {filename}")
            else:
                self.update_status("Error loading graph")
                messagebox.showerror("Error", "Failed to load graph from file")

    def save_graph(self):
        if self.current_graph is None:
            messagebox.showwarning("Warning", "No graph to save")
            return

        filename = filedialog.asksaveasfilename(title="Save Graph As",
                                                defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filename:
            self.update_status(f"Saving graph to {filename}...")
            if SaveGraphToFile(self.current_graph, filename):
                self.update_status(f"Graph saved to {filename}")
                messagebox.showinfo("Success", "Graph saved successfully")
            else:
                self.update_status("Error saving graph")
                messagebox.showerror("Error", "Failed to save graph")

    def add_node_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Node")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="X coordinate:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        x_entry = tk.Entry(dialog)
        x_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Y coordinate:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        y_entry = tk.Entry(dialog)
        y_entry.grid(row=2, column=1, padx=5, pady=5)

        def add_node():
            try:
                name = name_entry.get().strip()
                x = float(x_entry.get())
                y = float(y_entry.get())

                if not name:
                    messagebox.showerror("Error", "Name cannot be empty")
                    return

                if self.current_graph is None:
                    self.current_graph = Graph()

                if AddNode(self.current_graph, Node(name, x, y)):
                    self.plot_graph()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Node with this name already exists")
            except ValueError:
                messagebox.showerror("Error", "Invalid coordinates")

        tk.Button(dialog, text="Add", command=add_node).grid(row=3, column=0, columnspan=2, pady=5)
        name_entry.focus_set()

    def add_segment_dialog(self):
        if self.current_graph is None or not self.current_graph.nodes:
            messagebox.showwarning("Warning", "No nodes in the graph")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Segment")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Segment name:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Origin node:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        origin_var = tk.StringVar()
        origin_menu = ttk.Combobox(dialog, textvariable=origin_var,
                                   values=[n.name for n in self.current_graph.nodes], state='readonly')
        origin_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Destination node:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        dest_var = tk.StringVar()
        dest_menu = ttk.Combobox(dialog, textvariable=dest_var,
                                 values=[n.name for n in self.current_graph.nodes], state='readonly')
        dest_menu.grid(row=2, column=1, padx=5, pady=5)

        def add_segment():
            name = name_entry.get().strip()
            origin = origin_var.get()
            dest = dest_var.get()

            if not name or not origin or not dest:
                messagebox.showerror("Error", "All fields are required")
                return

            if origin == dest:
                messagebox.showerror("Error", "Origin and destination cannot be the same")
                return

            if AddSegment(self.current_graph, name, origin, dest):
                self.plot_graph()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add segment (nodes not found or segment exists)")

        tk.Button(dialog, text="Add", command=add_segment).grid(row=3, column=0, columnspan=2, pady=5)
        name_entry.focus_set()

    def remove_node_dialog(self):
        if self.current_graph is None or not self.current_graph.nodes:
            messagebox.showwarning("Warning", "No nodes in the graph")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Remove Node")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Select node to remove:").pack(padx=10, pady=5)

        node_var = tk.StringVar()
        node_menu = ttk.Combobox(dialog, textvariable=node_var,
                                 values=[n.name for n in self.current_graph.nodes], state='readonly')
        node_menu.pack(padx=10, pady=5)

        def remove_node():
            node_name = node_var.get()
            if not node_name:
                messagebox.showerror("Error", "Please select a node")
                return

            if RemoveNode(self.current_graph, node_name):
                self.plot_graph()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Node not found")

        tk.Button(dialog, text="Remove", command=remove_node).pack(pady=10)
        node_menu.focus_set()

    def clear_graph(self):
        self.current_graph = Graph()
        self.plot_graph()
        self.update_status("Graph cleared")

    def show_reachable(self):
        if self.current_graph is None:
            messagebox.showwarning("Warning", "No graph loaded")
            return

        node_name = self.reach_var.get()
        if not node_name:
            messagebox.showwarning("Warning", "Please select a node")
            return

        self.update_status(f"Finding nodes reachable from {node_name}...")
        reachable = GetReachableNodes(self.current_graph, node_name)

        if reachable:
            PlotReachableNodes(self.current_graph, node_name)
            self.update_status(f"Found {len(reachable)} reachable nodes from {node_name}")
        else:
            messagebox.showinfo("Reachability", f"No reachable nodes from {node_name} (only itself)")

    def find_shortest_path(self):
        if self.current_graph is None:
            messagebox.showwarning("Warning", "No graph loaded")
            return

        start_name = self.path_start_var.get()
        end_name = self.path_end_var.get()

        if not start_name or not end_name:
            messagebox.showwarning("Warning", "Please select both nodes")
            return

        if start_name == end_name:
            messagebox.showwarning("Warning", "Start and end nodes must be different")
            return

        self.update_status(f"Finding shortest path from {start_name} to {end_name}...")
        path = FindShortestPath(self.current_graph, start_name, end_name)

        if path:
            PlotPath(self.current_graph, path)
            messagebox.showinfo("Shortest Path",
                                f"Found path with cost {path.cost:.2f}:\n" +
                                " -> ".join([n.name for n in path.nodes]))
            self.update_status(f"Found path from {start_name} to {end_name} (cost: {path.cost:.2f})")
        else:
            messagebox.showinfo("Shortest Path",
                                f"No path found from {start_name} to {end_name}")
            self.update_status(f"No path exists from {start_name} to {end_name}")

    def show_node_neighbors(self):
        if self.current_graph is None:
            messagebox.showwarning("Warning", "No graph loaded")
            return

        node_name = self.reach_var.get()
        if not node_name:
            messagebox.showwarning("Warning", "Please select a node")
            return

        self.update_status(f"Showing neighbors of {node_name}...")
        if not PlotNode(self.current_graph, node_name):
            messagebox.showerror("Error", "Node not found")
            self.update_status("Error: Node not found")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
