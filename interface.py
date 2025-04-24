import tkinter as tk
from tkinter import filedialog, messagebox
from graph import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Visualization Tool")
        self.current_graph = None

        # Create frames
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Control buttons
        tk.Button(self.control_frame, text="Show Example Graph 1",
                  command=self.show_example1).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Show Example Graph 2",
                  command=self.show_example2).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Load Graph from File",
                  command=self.load_graph).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Save Graph to File",
                  command=self.save_graph).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Add Node",
                  command=self.add_node_dialog).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Add Segment",
                  command=self.add_segment_dialog).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Remove Node",
                  command=self.remove_node_dialog).pack(fill=tk.X, pady=2)
        tk.Button(self.control_frame, text="Clear Graph",
                  command=self.clear_graph).pack(fill=tk.X, pady=2)

        # Node selection
        self.node_var = tk.StringVar()
        self.node_label = tk.Label(self.control_frame, text="Select Node:")
        self.node_label.pack(pady=(10, 2))
        self.node_menu = tk.OptionMenu(self.control_frame, self.node_var, "")
        self.node_menu.pack(fill=tk.X)
        tk.Button(self.control_frame, text="Show Node Neighbors",
                  command=self.show_node_neighbors).pack(fill=tk.X, pady=2)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        # Initialize with example graph
        self.show_example1()

    def plot_graph(self, g=None):
        if g is None:
            g = self.current_graph

        if g is None:
            return

        self.ax.clear()

        # Update node selection menu
        self.node_var.set("")
        self.node_menu['menu'].delete(0, 'end')
        for node in g.nodes:
            self.node_menu['menu'].add_command(label=node.name,
                                               command=tk._setit(self.node_var, node.name))

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

        self.ax.grid(True)
        self.ax.set_title("Graph Visualization")
        self.canvas.draw()

    def show_example1(self):
        self.current_graph = CreateGraph_1()
        self.plot_graph()

    def show_example2(self):
        self.current_graph = CreateGraph_2()
        self.plot_graph()

    def load_graph(self):
        filename = filedialog.askopenfilename(title="Select Graph File",
                                              filetypes=[("Text files", "*.txt")])
        if filename:
            self.current_graph = LoadGraphFromFile(filename)
            if self.current_graph:
                self.plot_graph()
            else:
                messagebox.showerror("Error", "Failed to load graph from file")

    def save_graph(self):
        if self.current_graph is None:
            messagebox.showwarning("Warning", "No graph to save")
            return

        filename = filedialog.asksaveasfilename(title="Save Graph As",
                                                defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filename:
            if SaveGraphToFile(self.current_graph, filename):
                messagebox.showinfo("Success", "Graph saved successfully")
            else:
                messagebox.showerror("Error", "Failed to save graph")

    def add_node_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Node")

        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="X coordinate:").grid(row=1, column=0, padx=5, pady=5)
        x_entry = tk.Entry(dialog)
        x_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Y coordinate:").grid(row=2, column=0, padx=5, pady=5)
        y_entry = tk.Entry(dialog)
        y_entry.grid(row=2, column=1, padx=5, pady=5)

        def add_node():
            try:
                name = name_entry.get()
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

    def add_segment_dialog(self):
        if self.current_graph is None or not self.current_graph.nodes:
            messagebox.showwarning("Warning", "No nodes in the graph")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Segment")

        tk.Label(dialog, text="Segment name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Origin node:").grid(row=1, column=0, padx=5, pady=5)
        origin_var = tk.StringVar()
        origin_menu = tk.OptionMenu(dialog, origin_var, *[n.name for n in self.current_graph.nodes])
        origin_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Destination node:").grid(row=2, column=0, padx=5, pady=5)
        dest_var = tk.StringVar()
        dest_menu = tk.OptionMenu(dialog, dest_var, *[n.name for n in self.current_graph.nodes])
        dest_menu.grid(row=2, column=1, padx=5, pady=5)

        def add_segment():
            name = name_entry.get()
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
                messagebox.showerror("Error", "Failed to add segment (nodes not found)")

        tk.Button(dialog, text="Add", command=add_segment).grid(row=3, column=0, columnspan=2, pady=5)

    def remove_node_dialog(self):
        if self.current_graph is None or not self.current_graph.nodes:
            messagebox.showwarning("Warning", "No nodes in the graph")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Remove Node")

        tk.Label(dialog, text="Select node to remove:").pack(padx=5, pady=5)

        node_var = tk.StringVar()
        node_menu = tk.OptionMenu(dialog, node_var, *[n.name for n in self.current_graph.nodes])
        node_menu.pack(padx=5, pady=5)

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

        tk.Button(dialog, text="Remove", command=remove_node).pack(pady=5)

    def clear_graph(self):
        self.current_graph = Graph()
        self.plot_graph()

    def show_node_neighbors(self):
        if self.current_graph is None:
            messagebox.showwarning("Warning", "No graph loaded")
            return

        node_name = self.node_var.get()
        if not node_name:
            messagebox.showwarning("Warning", "Please select a node")
            return

        self.ax.clear()

        origin = None
        for node in self.current_graph.nodes:
            if node.name == node_name:
                origin = node
                break

        if origin is None:
            messagebox.showerror("Error", "Node not found")
            return

        neighbor_names = [n.name for n in origin.neighbors]

        # Draw all segments first (gray)
        for seg in self.current_graph.segments:
            self.ax.plot([seg.origin.x, seg.destination.x],
                         [seg.origin.y, seg.destination.y],
                         'k-', alpha=0.2)

        # Draw all nodes
        for node in self.current_graph.nodes:
            if node.name == node_name:
                color = 'blue'
                size = 12
            elif node.name in neighbor_names:
                color = 'green'
                size = 10
            else:
                color = 'gray'
                size = 8

            self.ax.plot(node.x, node.y, 'o', markersize=size, color=color)
            self.ax.text(node.x, node.y + 0.5, node.name,
                         ha='center', va='center', fontsize=10)

        # Highlight segments from origin to neighbors (red)
        for seg in self.current_graph.segments:
            if seg.origin.name == node_name:
                self.ax.plot([seg.origin.x, seg.destination.x],
                             [seg.origin.y, seg.destination.y],
                             'r-', alpha=0.7)

                # Add arrow
                self.ax.annotate('', xy=(seg.destination.x, seg.destination.y),
                                 xytext=(seg.origin.x, seg.origin.y),
                                 arrowprops=dict(arrowstyle='->', color='red'))

                # Add cost label
                mid_x = (seg.origin.x + seg.destination.x) / 2
                mid_y = (seg.origin.y + seg.destination.y) / 2
                self.ax.text(mid_x, mid_y, f"{seg.cost:.1f}",
                             bbox=dict(facecolor='white', alpha=0.7))

        self.ax.grid(True)
        self.ax.set_title(f"Node {node_name} and its neighbors")
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
