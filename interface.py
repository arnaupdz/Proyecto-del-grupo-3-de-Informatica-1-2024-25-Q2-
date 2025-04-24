import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from graph import Graph, BuildGraphFromFile, Plot, PlotNode, AddNode, AddSegment, GetClosest
from node import Node
from segment import Segment
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os


class GraphEditor:
    def __init__(self, master):
        self.master = master
        master.title("Graph Editor")
        self.current_graph = Graph()
        self.selected_node = None
        self.drawing_mode = None
        self.setup_ui()
        self.canvas.mpl_connect('button_press_event', self.on_click)

    def setup_ui(self):
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        graph_frame = tk.LabelFrame(control_frame, text="Graph Operations")
        graph_frame.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(graph_frame, text="Show Example Graph", command=self.show_example_graph).pack(side=tk.LEFT, padx=2)
        tk.Button(graph_frame, text="Show Custom Graph", command=self.show_custom_graph).pack(side=tk.LEFT, padx=2)
        tk.Button(graph_frame, text="Load Graph", command=self.load_graph).pack(side=tk.LEFT, padx=2)
        tk.Button(graph_frame, text="Save Graph", command=self.save_graph).pack(side=tk.LEFT, padx=2)
        tk.Button(graph_frame, text="New Graph", command=self.new_graph).pack(side=tk.LEFT, padx=2)

        node_frame = tk.LabelFrame(control_frame, text="Node Operations")
        node_frame.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(node_frame, text="Add Node", command=self.start_add_node).pack(side=tk.LEFT, padx=2)
        tk.Button(node_frame, text="Delete Node", command=self.delete_node).pack(side=tk.LEFT, padx=2)
        tk.Button(node_frame, text="Add Segment", command=self.start_add_segment).pack(side=tk.LEFT, padx=2)
        tk.Button(node_frame, text="Show Neighbors", command=self.show_neighbors).pack(side=tk.LEFT, padx=2)

        self.status_label = tk.Label(control_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.node_var = tk.StringVar()
        self.node_dropdown = tk.OptionMenu(control_frame, self.node_var, "")
        self.node_dropdown.pack(side=tk.LEFT, padx=5)
        self.node_var.set("Select node")

        self.update_plot()

    def update_plot(self):
        self.figure.clf()
        ax = self.figure.add_subplot(111)

        for seg in self.current_graph.segments:
            x1, y1 = seg.origin.x, seg.origin.y
            x2, y2 = seg.destination.x, seg.destination.y
            ax.plot([x1, x2], [y1, y2], 'k-')
            dx = x2 - x1
            dy = y2 - y1
            ax.arrow(x1, y1, dx * 0.9, dy * 0.9, head_width=0.3, head_length=0.5, fc='k', ec='k')
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            ax.text(mid_x, mid_y, f"{seg.cost:.1f}", color='red')

        for node in self.current_graph.nodes:
            color = 'blue' if node == self.selected_node else 'gray'
            ax.plot(node.x, node.y, 'o', markersize=10, color=color)
            ax.text(node.x, node.y, f" {node.name}", fontsize=12)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)
        self.canvas.draw()
        self.update_node_dropdown()

    def update_node_dropdown(self):
        menu = self.node_dropdown["menu"]
        menu.delete(0, "end")
        for node in self.current_graph.nodes:
            menu.add_command(label=node.name, command=lambda n=node.name: self.select_node_by_name(n))
        if not self.current_graph.nodes:
            self.node_var.set("No nodes")

    def select_node_by_name(self, name):
        for node in self.current_graph.nodes:
            if node.name == name:
                self.selected_node = node
                self.node_var.set(name)
                self.update_plot()
                break

    def on_click(self, event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata

        if self.drawing_mode == "add_node":
            name = simpledialog.askstring("Add Node", "Enter node name:")
            if name:
                AddNode(self.current_graph, Node(name, x, y))
                self.update_plot()
                self.drawing_mode = None
                self.status_label.config(text="Ready")

        elif self.drawing_mode == "add_segment":
            closest = GetClosest(self.current_graph, x, y)
            if closest:
                if not self.selected_node:
                    self.selected_node = closest
                    self.status_label.config(text=f"Selected {closest.name}, click destination node")
                else:
                    cost = simpledialog.askfloat("Add Segment", "Enter segment cost:", minvalue=0)
                    if cost is not None:
                        seg_name = f"{self.selected_node.name}{closest.name}"
                        if AddSegment(self.current_graph, seg_name, self.selected_node.name, closest.name):
                            for seg in self.current_graph.segments:
                                if seg.name == seg_name:
                                    seg.cost = cost
                                    break
                        self.selected_node = None
                        self.drawing_mode = None
                        self.update_plot()
                        self.status_label.config(text="Ready")

    def start_add_node(self):
        self.drawing_mode = "add_node"
        self.status_label.config(text="Click on graph to add node")

    def start_add_segment(self):
        self.drawing_mode = "add_segment"
        self.selected_node = None
        self.status_label.config(text="Click origin node first")

    def delete_node(self):
        if not self.selected_node:
            messagebox.showwarning("No Selection", "Please select a node first")
            return
        self.current_graph.segments = [seg for seg in self.current_graph.segments if
                                       seg.origin != self.selected_node and seg.destination != self.selected_node]
        self.current_graph.nodes.remove(self.selected_node)
        self.selected_node = None
        self.update_plot()

    def show_neighbors(self):
        if not self.selected_node:
            messagebox.showwarning("No Selection", "Please select a node first")
            return
        self.figure.clf()
        PlotNode(self.current_graph, self.selected_node.name)
        self.canvas.draw()

    def show_example_graph(self):
        self.current_graph = self.create_example_graph()
        self.selected_node = None
        self.update_plot()

    def create_example_graph(self):
        g = Graph()
        nodes = [("A", 1, 20), ("B", 8, 17), ("C", 15, 20), ("D", 18, 15), ("E", 2, 4), ("F", 6, 5),
                 ("G", 12, 12), ("H", 10, 3), ("I", 19, 1), ("J", 13, 5), ("K", 3, 15), ("L", 4, 10)]
        for name, x, y in nodes:
            AddNode(g, Node(name, x, y))

        segments = [("AB", "A", "B", 5.0), ("AE", "A", "E", 3.5), ("AK", "A", "K", 4.2),
                    ("BA", "B", "A", 5.0), ("BC", "B", "C", 6.1), ("BF", "B", "F", 2.8),
                    ("BK", "B", "K", 3.0), ("BG", "B", "G", 4.5), ("CD", "C", "D", 3.7),
                    ("CG", "C", "G", 5.2), ("DG", "D", "G", 4.8), ("DH", "D", "H", 6.3),
                    ("DI", "D", "I", 7.1), ("EF", "E", "F", 2.5), ("FL", "F", "L", 3.2),
                    ("GB", "G", "B", 4.5), ("GF", "G", "F", 3.8), ("GH", "G", "H", 4.0),
                    ("ID", "I", "D", 7.1), ("IJ", "I", "J", 5.5), ("JI", "J", "I", 5.5),
                    ("KA", "K", "A", 4.2), ("KL", "K", "L", 2.7), ("LK", "L", "K", 2.7),
                    ("LF", "L", "F", 3.0)]
        for name, orig, dest, cost in segments:
            if AddSegment(g, name, orig, dest):
                for seg in g.segments:
                    if seg.name == name:
                        seg.cost = cost
                        break
        return g

    def show_custom_graph(self):
        self.current_graph = self.create_custom_graph()
        self.selected_node = None
        self.update_plot()

    def create_custom_graph(self):
        g = Graph()
        nodes = [("X", 0, 0), ("Y", 2, 2), ("Z", 4, 0), ("W", 2, -2), ("V", -2, 0), ("U", 0, 4)]
        for name, x, y in nodes:
            AddNode(g, Node(name, x, y))

        segments = [("XY", "X", "Y", 3.0), ("YZ", "Y", "Z", 3.0), ("ZW", "Z", "W", 3.0),
                    ("WX", "W", "X", 3.0), ("XV", "X", "V", 2.5), ("YU", "Y", "U", 2.5),
                    ("VX", "V", "X", 2.5), ("UY", "U", "Y", 2.5), ("XZ", "X", "Z", 4.2),
                    ("YW", "Y", "W", 4.2)]
        for name, orig, dest, cost in segments:
            if AddSegment(g, name, orig, dest):
                for seg in g.segments:
                    if seg.name == name:
                        seg.cost = cost
                        break
        return g

    def load_graph(self):
        filename = filedialog.askopenfilename(title="Select Graph File",
                                              filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if filename:
            g = BuildGraphFromFile(filename)
            if g:
                self.current_graph = g
                self.selected_node = None
                self.update_plot()

    def save_graph(self):
        if not self.current_graph.nodes:
            messagebox.showwarning("Empty Graph", "There's nothing to save")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Graph As",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")))

        if filename:
            with open(filename, 'w') as f:
                for node in self.current_graph.nodes:
                    f.write(f"{node.name} {node.x} {node.y}\n")

                f.write("---\n")

                for seg in self.current_graph.segments:
                    f.write(f"{seg.name} {seg.origin.name} {seg.destination.name} {seg.cost:.1f}\n")

    def new_graph(self):
        self.current_graph = Graph()
        self.selected_node = None
        self.update_plot()


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()
