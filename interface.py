import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graph import *
from path import *
from airspace import *
from kml_generator import KMLGenerator
import os
import webbrowser
import time
from datetime import datetime
from datetime import datetime
from PIL import Image, ImageTk
















class GraphApp:
 def __init__(self, root):
     self.root = root
     self.root.title("Airspace Route Explorer - Final Version")
     self.current_graph = None
     self.current_airspace = None
     self.dark_mode = False
     self.selected_nodes = []
     self.current_segments_to_draw = None
     self.current_path = None
     self.current_reachable = None
     self.node_neighbors = None
     self.new_node_mode = False
     self.new_segment_mode = False
     self.delete_mode = False
     self.avoid_nodes = set()  # Para funcionalidad de evitar nodos




     # Configuración de la ventana principal
     self.root.minsize(1100, 800)
     self.root.geometry("1100x800")




     # Estilo general
     self.setup_styles()


     # Crear frames
     self.sidebar_frame = tk.Frame(root, bg='#f0f0f0')
     self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)




     self.control_canvas = tk.Canvas(self.sidebar_frame, width=250, bg='#f0f0f0', highlightthickness=0)
     self.control_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)




     self.scrollbar = ttk.Scrollbar(self.sidebar_frame, orient="vertical", command=self.control_canvas.yview)
     self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)




     self.control_canvas.configure(yscrollcommand=self.scrollbar.set)




     self.control_frame = tk.Frame(self.control_canvas, bg='#f0f0f0')
     self.control_canvas.create_window((0, 0), window=self.control_frame, anchor="nw")




     self.canvas_frame = tk.Frame(root, bg='white')
     self.canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)




     # Configurar matplotlib en Tkinter
     self.fig, self.ax = plt.subplots(figsize=(9, 7), facecolor='white')
     self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
     self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)




     # Conectar eventos del gráfico
     self.canvas.mpl_connect('button_press_event', self.on_graph_click)
     self.zoom_factor = 1.2
     self.canvas.mpl_connect("scroll_event", self.on_scroll)  # <-- Para zoom con rueda




     # Configurar controles
     self.setup_controls()
     self.setup_extra_menu()




     # Scroll en panel de controles
     def on_frame_configure(event):
         self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))




     self.control_frame.bind("<Configure>", on_frame_configure)




     def _on_mousewheel(event):
         self.control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")




     self.control_canvas.bind_all("<MouseWheel>", _on_mousewheel)




     # Cargar ejemplo inicial
     self.show_example1()


 def setup_styles(self):
     """Configura los estilos visuales de la interfaz"""
     style = ttk.Style()
     style.theme_use('clam')


     # Configurar colores base según el modo
     bg_color = '#f0f0f0'
     fg_color = '#000000'
     widget_bg = '#ffffff'


     style.configure('TFrame', background=bg_color)
     style.configure('TLabel', background=bg_color, font=('Helvetica', 9), foreground=fg_color)
     style.configure('TButton', font=('Helvetica', 9), padding=5, background=widget_bg, foreground=fg_color)
     style.configure('TLabelFrame', font=('Helvetica', 10, 'bold'), background=bg_color, foreground=fg_color)
     style.configure('TCombobox', font=('Helvetica', 9), fieldbackground=widget_bg, foreground=fg_color)
     style.configure('TRadiobutton', font=('Helvetica', 9), background=bg_color, foreground=fg_color)
     style.configure('TEntry', font=('Helvetica', 9), fieldbackground=widget_bg, foreground=fg_color)


     # Colores personalizados para hover y estados
     style.map('TButton',
               background=[('active', '#e0e0e0'),
                           ('!disabled', widget_bg)],
               foreground=[('!disabled', fg_color)])


     style.map('TCombobox',
               fieldbackground=[('!disabled', widget_bg)],
               background=[('!disabled', widget_bg)])








 def setup_controls(self):
     """Configura todos los elementos de la interfaz"""
     # Panel de selección de airspace
     airspace_frame = ttk.LabelFrame(self.control_frame, text="Airspace Selection", padding=10)
     airspace_frame.pack(fill=tk.X, pady=5)








     self.airspace_var = tk.StringVar()
     self.airspace_menu = ttk.Combobox(airspace_frame, textvariable=self.airspace_var,
                                       values=["Catalunya", "España", "Europa"], state="readonly")
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












     # --- NUEVO BOTÓN PARA MOSTRAR TODOS LOS SEGMENTOS ---
     def show_all_segments():
         self.current_segments_to_draw = None
         if self.current_airspace:
             self.plot_airspace()
         else:
             self.plot_graph()
         self.update_status("Showing all segments.")




     ttk.Button(analysis_frame, text="Show All Segments", command=show_all_segments).pack(fill=tk.X, pady=2)




     # Botones de acción
     ttk.Button(analysis_frame, text="Find Reachable Nodes",
                command=self.find_reachable_interactive).pack(fill=tk.X, pady=2)
     ttk.Button(analysis_frame, text="Find Shortest Path",
                command=self.find_shortest_path_interactive).pack(fill=tk.X, pady=2)
     ttk.Button(analysis_frame, text="Show Node Neighbors",
                command=self.show_node_neighbors).pack(fill=tk.X, pady=2)
     ttk.Button(analysis_frame, text="Clear Analysis",
                command=self.clear_analysis).pack(fill=tk.X, pady=2)






     # Panel de exportación KML
     kml_frame = ttk.LabelFrame(self.control_frame, text="Google Earth Export", padding=10)
     kml_frame.pack(fill=tk.X, pady=5)








     ttk.Button(kml_frame, text="Export Current to KML",
                command=self.export_current_to_kml).pack(fill=tk.X, pady=2)
     ttk.Button(kml_frame, text="Export Path to KML",
                command=self.export_path_to_kml).pack(fill=tk.X, pady=2)
     ttk.Button(kml_frame, text="Open in Google Earth",
                command=self.open_in_google_earth).pack(fill=tk.X, pady=2)








     # Panel de funcionalidades avanzadas
     advanced_frame = ttk.LabelFrame(self.control_frame, text="Advanced Features", padding=10)
     advanced_frame.pack(fill=tk.X, pady=5)




     # Panel de información
     info_frame = ttk.LabelFrame(self.control_frame, text="Information", padding=10)
     info_frame.pack(fill=tk.X, pady=5, expand=True)








     self.info_text = tk.Text(info_frame, height=10, width=30, wrap=tk.WORD, font=('Helvetica', 9))
     self.info_text.pack(fill=tk.BOTH, expand=True)








     # Barra de estado
     self.status_var = tk.StringVar(value="Ready")
     status_bar = tk.Label(self.control_frame, textvariable=self.status_var,
                           relief=tk.SUNKEN, anchor=tk.W, bg='#f0f0f0', fg='#333333')
     status_bar.pack(side=tk.BOTTOM, fill=tk.X)








 # =============================================
 # Métodos principales de interacción
 # =============================================
 def on_scroll(self, event):
     """Realiza zoom sobre el gráfico usando la rueda del ratón"""
     ax = self.ax
     xdata = event.xdata
     ydata = event.ydata
     if xdata is None or ydata is None:
         return  # Fuera del área del gráfico




     cur_xlim = ax.get_xlim()
     cur_ylim = ax.get_ylim()




     if event.button == 'up':
         scale_factor = 1 / self.zoom_factor
     elif event.button == 'down':
         scale_factor = self.zoom_factor
     else:
         scale_factor = 1




     new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
     new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor




     relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
     rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])




     ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
     ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
     self.canvas.draw_idle()




 def on_graph_click(self, event):
     """Maneja los clics en el gráfico"""
     if not event.inaxes:
         return








     if self.current_airspace:
         self.handle_airspace_click(event)
     else:
         self.handle_graph_click(event)




 def handle_airspace_click(self, event):
     """Maneja clics en modo airspace"""
     if not self.current_airspace or not self.current_airspace.nav_points:
         self.update_info("Error: No navigation points loaded in airspace.")
         return


     clicked_node = self.find_closest_navpoint(event.xdata, event.ydata)


     if self.new_node_mode:
         self.add_new_navpoint(event.xdata, event.ydata)
         return


     if self.new_segment_mode and clicked_node:
         self.add_new_airspace_segment(clicked_node)
         return


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




 def handle_graph_click(self, event):
     """Maneja clics en modo grafo normal"""
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




 # =============================================
 # Métodos de gestión de grafos
 # =============================================
 def setup_extra_menu(self):
     # Crea un marco con el título "Extra" en el panel lateral de controles
     extra_frame = ttk.LabelFrame(self.control_frame, text="Extra")
     extra_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

     # Botón para mostrar solo aeropuertos
     show_airports_btn = ttk.Button(extra_frame, text="Mostrar solo aeropuertos", command=self.show_only_airports)
     show_airports_btn.pack(fill=tk.X, pady=(0, 5))

     # Botón para mostrar la foto de grupo
     show_photo_btn = ttk.Button(extra_frame, text="Mostrar foto de grupo", command=self.show_group_photo)
     show_photo_btn.pack(fill=tk.X, pady=(0, 5))

     # Nuevo botón de funcionalidades extra
     extra_features_btn = ttk.Button(extra_frame, text="Funcionalidades extra", command=self.show_extra_features)
     extra_features_btn.pack(fill=tk.X)

 def show_extra_features(self):
     """Muestra un mensaje con las funcionalidades extra disponibles"""
     message = "No te vayas sin comprobar nuestras funcionalidades extra:\n\n"
     message += "- Haz zoom en el mapa con la rueda del ratón\n"
     message += "- Prueba de mostrar solo aeropuertos\n"
     message += "- Vuelve a mostrar todos los segmentos dentro del mapa\n\n"
     message += "¡Explora todas las posibilidades!"

     messagebox.showinfo("Funcionalidades Extra", message)

 def show_only_airports(self):
     """Muestra solo los aeropuertos en el espacio aéreo"""
     if not self.current_airspace:
         return




     self.ax.clear()




     # Dibujar solo aeropuertos
     for airport in self.current_airspace.nav_airports:
         first_sid = airport.get_first_sid_point(self.current_airspace.nav_points)
         if first_sid:
             # Dibujar aeropuerto
             self.ax.plot(first_sid.longitude, first_sid.latitude, 's',
                          markersize=12, color='purple')
             self.ax.text(first_sid.longitude, first_sid.latitude + 0.04,
                          airport.name, fontsize=10, ha='center',
                          bbox=dict(facecolor='white', alpha=0.8))




     # Ajustar límites del gráfico
     if self.current_airspace.nav_airports:
         lons = [p.get_first_sid_point(self.current_airspace.nav_points).longitude
                 for p in self.current_airspace.nav_airports
                 if p.get_first_sid_point(self.current_airspace.nav_points)]
         lats = [p.get_first_sid_point(self.current_airspace.nav_points).latitude
                 for p in self.current_airspace.nav_airports
                 if p.get_first_sid_point(self.current_airspace.nav_points)]




         if lons and lats:
             self.ax.set_xlim(min(lons) - 1, max(lons) + 1)
             self.ax.set_ylim(min(lats) - 1, max(lats) + 1)




     self.ax.set_title(f"{self.airspace_var.get()} - Airports Only", pad=20)
     self.ax.set_xlabel("Longitude")
     self.ax.set_ylabel("Latitude")
     self.ax.grid(True, linestyle=':', alpha=0.3)
     self.canvas.draw()

 def show_group_photo(self):
     """Muestra la imagen foto_grupo.png en una ventana nueva"""
     top = tk.Toplevel(self.root)
     top.title("Foto de grupo")
     try:
         img = Image.open(r"C:\Users\ferra\OneDrive\Imágenes\foto_grupo.jpg")


         img.thumbnail((600, 450))
         tkimg = ImageTk.PhotoImage(img)
         label = tk.Label(top, image=tkimg)
         label.image = tkimg  # Guarda referencia para que no se borre la imagen
         label.pack()
     except Exception as e:
         tk.Label(top, text=f"No se pudo cargar la imagen: {e}").pack()

 def add_new_node(self, x, y):
     """Añade un nuevo nodo al grafo"""
     if self.current_airspace:
         messagebox.showwarning("Warning", "Cannot add nodes in Airspace mode")
         self.new_node_mode = False
         return








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
     """Añade un nuevo segmento al grafo"""
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
             self.update_status(f"Added segment: {origin.name} - {dest.name}")
         else:
             messagebox.showwarning("Warning", "Segment already exists or nodes not found")








         # Resetear selección y modo
         self.selected_nodes = []
         self.new_segment_mode = False
         self.mode_var.set("select")  # Volver al modo selección

 def delete_node(self, node):
     """Elimina un nodo del grafo"""
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








     # Actualizar lista de nodos a evitar
     if node.name in self.avoid_nodes:
         self.avoid_nodes.remove(node.name)
         self.update_avoid_listbox()








     self.plot_graph()
     self.update_status(f"Deleted node: {node.name}")
     self.delete_mode = False

 def add_new_navpoint(self, lon, lat):
     """Añade un nuevo punto de navegación al airspace"""
     if not self.current_airspace:
         return


     # Generar un ID único para el nuevo punto
     new_id = max([p.number for p in self.current_airspace.nav_points], default=0) + 1


     dialog = tk.Toplevel(self.root)
     dialog.title("Add New NavPoint")


     tk.Label(dialog, text="NavPoint Name:").pack()
     name_var = tk.StringVar()
     tk.Entry(dialog, textvariable=name_var).pack()


     def confirm():
         name = name_var.get().strip()
         if not name:
             messagebox.showwarning("Warning", "Name cannot be empty")
             return


         # Crear nuevo NavPoint
         new_point = NavPoint(new_id, name, lat, lon)
         self.current_airspace.nav_points.append(new_point)
         self.plot_airspace()
         dialog.destroy()


     tk.Button(dialog, text="Add", command=confirm).pack()
     tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

 def add_new_airspace_segment(self, node):
     """Añade un nuevo segmento en airspace"""
     if not self.current_airspace:
         return


     self.selected_nodes.append(node)
     if len(self.selected_nodes) > 2:
         self.selected_nodes.pop(0)


     if len(self.selected_nodes) == 2:
         origin = self.selected_nodes[0]
         dest = self.selected_nodes[1]


         # Calcular distancia (podría ser más preciso usando fórmulas de distancia geodésica)
         distance = ((dest.longitude - origin.longitude) ** 2 +
                     (dest.latitude - origin.latitude) ** 2) ** 0.5 * 111  # Aproximación km


         # Crear nuevo segmento
         new_segment = NavSegment(origin.number, dest.number, distance)
         self.current_airspace.nav_segments.append(new_segment)


         self.plot_airspace()
         self.update_status(f"Added segment: {origin.name} - {dest.name}")


         # Resetear selección
         self.selected_nodes = []
         self.new_segment_mode = False

 def load_graph(self):
     file_path = filedialog.askopenfilename(
         title="Load Graph",
         filetypes=[("Graph and text files", "*.graph *.txt"), ("All files", "*.*")]
     )


     if not file_path:
         return


     try:
         with open(file_path, 'r') as f:
             self.current_graph = Graph()
             for line_num, line in enumerate(f, 1):
                 line = line.strip()
                 if not line or line.startswith("#"):
                     continue


                 parts = line.split()
                 if len(parts) < 2:
                     raise ValueError(f"Línea {line_num}: Formato incorrecto")


                 if parts[0] == "Node":
                     if len(parts) != 4:
                         raise ValueError(f"Línea {line_num}: Formato de nodo incorrecto")
                     try:
                         name = parts[1]
                         x = float(parts[2])
                         y = float(parts[3])
                         node = Node(name, x, y)
                         AddNode(self.current_graph, node)
                     except ValueError:
                         raise ValueError(f"Línea {line_num}: Coordenadas inválidas")










                 elif parts[0] == "Segment":


                     if len(parts) != 4:
                         raise ValueError(f"Línea {line_num}: Formato de segmento incorrecto")


                     try:


                         origin_name = parts[1]


                         dest_name = parts[2]


                         # El nombre puede ser algo como "A_B"


                         name = f"{origin_name}_{dest_name}"


                         # Aquí sí añades el segmento al grafo


                         if not AddSegment(self.current_graph, name, origin_name, dest_name):
                             raise ValueError(f"No se pudo añadir el segmento entre {origin_name} y {dest_name}")


                     except ValueError as ve:


                         raise ValueError(f"Línea {line_num}: Coste inválido o nodos incorrectos\n{ve}")


         self.current_airspace = None
         self.clear_analysis()
         self.plot_graph()
         self.update_status(f"Graph loaded from {file_path}")


     except Exception as e:
         messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")
         self.update_status(f"Error loading graph: {str(e)}")

 def save_graph(self):
     """Guarda el grafo actual en un archivo"""
     if not self.current_graph or len(self.current_graph.nodes) == 0:
         messagebox.showwarning("Warning", "No graph to save")
         return








     file_path = filedialog.asksaveasfilename(
         title="Save Graph",
         defaultextension=".graph",
         filetypes=[("Graph files", "*.graph"), ("All files", "*.*")]
     )








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

 def clear_graph(self):
     """Limpia el grafo actual"""
     self.current_graph = Graph()
     self.current_airspace = None
     self.clear_analysis()
     self.plot_graph()
     self.update_status("Graph cleared")

 # =============================================
 # Métodos de análisis de grafos
 # =============================================

 def find_reachable_from(self, start_name):
     """Encuentra nodos alcanzables desde un nodo dado y resalta solo los segmentos conectados"""
     self.current_segments_to_draw = []




     if self.current_airspace:
         start_point = next((p for p in self.current_airspace.nav_points
                             if p.number == start_name), None)
         if not start_point:
             self.update_info(f"NavPoint {start_name} not found")
             return




         reachable = []
         visited = set()
         queue = [start_point.number]
         segments_to_draw = []




         while queue:
             current_num = queue.pop(0)
             if current_num in visited:
                 continue
             visited.add(current_num)




             current_point = next((p for p in self.current_airspace.nav_points
                                   if p.number == current_num), None)
             if current_point:
                 reachable.append(current_point)
                 for seg in self.current_airspace.nav_segments:
                     if seg.origin_number == current_num and seg.destination_number not in visited:
                         queue.append(seg.destination_number)
                         segments_to_draw.append(seg)




         self.current_reachable = reachable
         self.current_segments_to_draw = segments_to_draw
         self.plot_airspace()
         self.update_info(f"Nodes reachable from {start_point.name}:\n" +
                          "\n".join([f"- {p.name}" for p in reachable]))
     else:
         reachable_nodes = GetReachableNodes(self.current_graph, start_name)
         if not reachable_nodes:
             self.update_info(f"Node {start_name} not found")
             return




         reachable_set = set(n.name for n in reachable_nodes)
         segments_to_draw = []
         for seg in self.current_graph.segments:
             if seg.origin.name in reachable_set and seg.destination.name in reachable_set:
                 segments_to_draw.append(seg)
         self.current_reachable = reachable_nodes
         self.current_segments_to_draw = segments_to_draw
         self.plot_graph()
         self.update_info(f"Nodes reachable from {start_name}:\n" +
                          "\n".join([f"- {node.name}" for node in reachable_nodes]))

 def find_reachable_in_airspace(self, start_name):
     """Encuentra nodos alcanzables en espacio aéreo"""
     start_point = next((p for p in self.current_airspace.nav_points
                         if p.number == start_name), None)
     if not start_point:
         self.update_info(f"NavPoint {start_name} not found")
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
     self.update_info(f"Nodes reachable from {start_point.name}:\n" +
                      "\n".join([f"- {p.name}" for p in reachable]))

 def find_reachable_in_graph(self, start_name):
     """Encuentra nodos alcanzables en grafo normal"""
     reachable_nodes = GetReachableNodes(self.current_graph, start_name)
     if not reachable_nodes:
         self.update_info(f"Node {start_name} not found")
         return








     self.current_reachable = reachable_nodes
     self.plot_graph()
     self.update_info(f"Nodes reachable from {start_name}:\n" +
                      "\n".join([f"- {node.name}" for node in reachable_nodes]))
     
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

 def find_shortest_path_in_graph(self, start_name, end_name):
     path = FindShortestPath(self.current_graph, start_name, end_name)

 def heuristic(self, point1, point2):
     """Distancia euclidiana entre dos puntos para A*"""
     return ((point1.longitude - point2.longitude) ** 2 +
             (point1.latitude - point2.latitude) ** 2) ** 0.5

 def show_node_neighbors(self):
     """Muestra los vecinos de un nodo seleccionado y resalta solo los segmentos conectados"""
     if not self.selected_nodes:
         messagebox.showwarning("Warning", "Please select a node first")
         return




     self.current_segments_to_draw = []




     if self.current_airspace:
         node = self.selected_nodes[0]
         neighbors = []
         segments_to_draw = []
         for seg in self.current_airspace.nav_segments:
             if seg.origin_number == node.number:
                 dest = next((p for p in self.current_airspace.nav_points
                              if p.number == seg.destination_number), None)
                 if dest:
                     neighbors.append(f"{dest.name} (distance: {seg.distance:.1f} km)")
                     segments_to_draw.append(seg)
             elif seg.destination_number == node.number:
                 orig = next((p for p in self.current_airspace.nav_points
                              if p.number == seg.origin_number), None)
                 if orig:
                     neighbors.append(f"{orig.name} (distance: {seg.distance:.1f} km)")
                     segments_to_draw.append(seg)
         self.node_neighbors = neighbors
         self.current_segments_to_draw = segments_to_draw
         self.plot_airspace()
         self.update_info(f"Neighbors of {node.name}:\n" + "\n".join(neighbors))
     else:
         node = self.selected_nodes[0]
         neighbors = []
         segments_to_draw = []
         for seg in self.current_graph.segments:
             if seg.origin == node:
                 neighbors.append(f"{seg.destination.name} (cost: {seg.cost:.1f})")
                 segments_to_draw.append(seg)
             elif seg.destination == node:
                 neighbors.append(f"{seg.origin.name} (cost: {seg.cost:.1f})")
                 segments_to_draw.append(seg)


         self.node_neighbors = neighbors
         self.current_segments_to_draw = segments_to_draw
         self.nodes_to_highlight = [seg.destination if seg.origin == node else seg.origin
                                    for seg in segments_to_draw]
         self.plot_graph()
         self.update_info(f"Neighbors of {node.name}:\n" + "\n".join(neighbors))

 def clear_analysis(self):
     """Limpia los resultados del análisis"""
     self.current_path = None
     self.current_reachable = None
     self.node_neighbors = None
     self.selected_nodes = []








     if self.current_airspace:
         self.plot_airspace()
     else:
         self.plot_graph()








     self.update_info("Analysis cleared")

 # =============================================
 # Métodos de visualización
 # =============================================

 def plot_graph(self):
     if not self.current_graph:
         return




     self.ax.clear()




     # Solo los segmentos seleccionados
     segments_to_draw = self.current_segments_to_draw if self.current_segments_to_draw is not None else self.current_graph.segments
     for seg in segments_to_draw:




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








         # Dibujar flecha de dirección
         if seg_color == 'gray':
             self.ax.annotate('', xy=(seg.destination.x, seg.destination.y),
                              xytext=(seg.origin.x, seg.origin.y),
                              arrowprops=dict(arrowstyle='->', color=seg_color, alpha=seg_alpha))








         # Etiqueta de costo
         mid_x = (seg.origin.x + seg.destination.x) / 2
         mid_y = (seg.origin.y + seg.destination.y) / 2
         self.ax.text(mid_x, mid_y, f"{seg.cost:.1f}", fontsize=7, ha='center', va='center',
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
         elif self.current_reachable and any(n.name == node.name for n in self.current_reachable):
             color = 'green'
             size = 7








         # Resaltar si es parte del camino
         elif self.current_path and any(n.name == node.name for n in self.current_path.nodes):
             color = 'purple'
             size = 8








         # Resaltar si es vecino directo seleccionado
         elif hasattr(self, 'nodes_to_highlight') and node in self.nodes_to_highlight:
             color = 'orange'
             size = 7








         # Resaltar si está en la lista de evitados
         elif node.name in self.avoid_nodes:
             color = 'black'
             size = 6








         self.ax.plot(node.x, node.y, 'o', markersize=size, color=color)
         self.ax.text(node.x, node.y + 0.5, node.name,
                      fontsize=8, ha='center', va='bottom')








     # Configuración del gráfico
     self.ax.set_title("Graph Visualization", pad=20)
     self.ax.grid(True, alpha=0.2)
     self.canvas.draw()

 def plot_airspace(self):
     """Dibuja el espacio aéreo actual mostrando aeropuertos correctamente y permitiendo mostrar solo aeropuertos si está activado el filtro."""
     if not self.current_airspace:
         return




     self.ax.clear()




     # 1. Dibujar segmentos
     segments_to_draw = self.current_segments_to_draw if self.current_segments_to_draw is not None else self.current_airspace.nav_segments
     for segment in segments_to_draw:
         origin = next((p for p in self.current_airspace.nav_points if p.number == segment.origin_number), None)
         dest = next((p for p in self.current_airspace.nav_points if p.number == segment.destination_number), None)
         if origin and dest:
             is_path_segment = False
             if self.current_path and hasattr(self.current_path, 'points'):
                 path_points = self.current_path.points
                 for i in range(len(path_points) - 1):
                     if (segment.origin_number == path_points[i].number and segment.destination_number == path_points[
                         i + 1].number):
                         is_path_segment = True
                         break
             if is_path_segment:
                 self.ax.plot([origin.longitude, dest.longitude],
                              [origin.latitude, dest.latitude],
                              color='red', linewidth=3, alpha=0.8)
             else:
                 self.ax.plot([origin.longitude, dest.longitude],
                              [origin.latitude, dest.latitude],
                              color='gray', linewidth=1.8, alpha=0.7)




     # 2. Dibujar puntos de navegación
     only_airports = getattr(self, "only_airports_visible", False)
     airport_sid_numbers = set()
     if only_airports:
         # Obtener los números de primer SID de todos los aeropuertos
         for airport in self.current_airspace.nav_airports:
             if hasattr(airport, "sids") and airport.sids:
                 airport_sid_numbers.add(airport.sids[0])




     for point in self.current_airspace.nav_points:
         # Si está activado el filtro, solo mostrar los puntos que son primer SID de un aeropuerto
         if only_airports and point.number not in airport_sid_numbers:
             continue




         if self.current_path and any(p.number == point.number for p in getattr(self.current_path, 'points', [])):
             color = 'red'
             size = 10
         elif any(p.number == point.number for p in self.selected_nodes):
             color = 'blue'
             size = 12
         elif point.number in self.avoid_nodes:
             color = 'black'
             size = 6
         elif self.current_reachable and any(p.number == point.number for p in self.current_reachable):
             color = 'green'
             size = 8
         else:
             color = 'gray'
             size = 6




         self.ax.plot(point.longitude, point.latitude, 'o',
                      markersize=size, color=color)
         self.ax.text(point.longitude, point.latitude + 0.02, point.name,
                      fontsize=8, ha='center')




     # 3. Dibujar aeropuertos usando su primer SID
     for airport in self.current_airspace.nav_airports:
         # Usar método get_first_sid_point si existe, si no, usa el primer SID manualmente
         if hasattr(airport, "get_first_sid_point"):
             first_sid = airport.get_first_sid_point(self.current_airspace.nav_points)
         elif hasattr(airport, "sids") and airport.sids:
             first_sid = next((p for p in self.current_airspace.nav_points if p.number == airport.sids[0]), None)
         else:
             first_sid = None




         if first_sid:
             self.ax.plot(first_sid.longitude, first_sid.latitude, 's',
                          markersize=10, color='purple')
             self.ax.text(first_sid.longitude, first_sid.latitude + 0.03,
                          airport.name, fontsize=9, ha='center',
                          bbox=dict(facecolor='white', alpha=0.7))




     # 4. Configuración final del gráfico
     if self.current_airspace.nav_points:
         lons = [p.longitude for p in self.current_airspace.nav_points]
         lats = [p.latitude for p in self.current_airspace.nav_points]
         self.ax.set_xlim(min(lons) - 0.5, max(lons) + 0.5)
         self.ax.set_ylim(min(lats) - 0.5, max(lats) + 0.5)




     self.ax.set_title(f"{self.airspace_var.get()} Airspace", pad=20)
     self.ax.set_xlabel("Longitude")
     self.ax.set_ylabel("Latitude")
     self.ax.grid(True, linestyle=':', alpha=0.3)
     self.canvas.draw()




     # Resetea la bandera para que solo afecte a una llamada
     self.only_airports_visible = False

 # =============================================
 # Métodos de espacio aéreo
 # =============================================

 def load_airspace(self, event=None):
     """Carga los datos del espacio aéreo seleccionado"""
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
         self.current_graph = None
         self.clear_analysis()
         self.plot_airspace()
         self.update_status(f"{selected} airspace loaded successfully")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to load airspace: {str(e)}")
         self.update_status("Error loading airspace")

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

 def select_navpoint(self, navpoint):
     """Maneja la selección de un punto de navegación"""
     self.selected_nodes.append(navpoint)
     if len(self.selected_nodes) > 2:
         self.selected_nodes.pop(0)








     self.plot_airspace()
     info_text = f"Selected: {navpoint.name} ({navpoint.number})\n"
     info_text += f"Coordinates: {navpoint.latitude:.6f}, {navpoint.longitude:.6f}"
     self.update_info(info_text)

 # =============================================
 # Métodos de exportación KML
 # =============================================

 def export_current_to_kml(self):
     """Exporta el grafo o espacio aéreo actual a KML"""
     if not (self.current_graph or self.current_airspace):
         messagebox.showwarning("Warning", "No graph or airspace to export")
         return








     file_path = filedialog.asksaveasfilename(
         title="Save KML File",
         defaultextension=".kml",
         filetypes=[("KML files", "*.kml"), ("All files", "*.*")]
     )








     if not file_path:
         return








     try:
         kml_gen = KMLGenerator()








         if self.current_airspace:
             kml_gen.generate_airspace_kml(self.current_airspace, file_path)
         else:
             kml_gen.generate_graph_kml(self.current_graph, file_path)








         self.update_status(f"KML file saved to {file_path}")
         self.last_kml_file = file_path
     except Exception as e:
         messagebox.showerror("Error", f"Failed to export KML: {str(e)}")
         self.update_status("Error exporting KML")

 def export_path_to_kml(self):
     """Exporta el camino actual a KML"""
     if not self.current_path:
         messagebox.showwarning("Warning", "No path to export")
         return








     file_path = filedialog.asksaveasfilename(
         title="Save Path KML",
         defaultextension=".kml",
         filetypes=[("KML files", "*.kml"), ("All files", "*.*")]
     )








     if not file_path:
         return








     try:
         kml_gen = KMLGenerator()








         if hasattr(self.current_path, 'points'):  # Para airspace
             points = self.current_path.points
             coords = [(p.longitude, p.latitude) for p in points]
             point_data = [{'name': p.name, 'lon': p.longitude, 'lat': p.latitude} for p in points]
         else:  # Para grafo normal
             points = self.current_path.nodes
             coords = [(n.x, n.y) for n in points]
             point_data = [{'name': n.name, 'lon': n.x, 'lat': n.y} for n in points]








         kml_gen.add_path("Shortest Path", point_data,
                          f"Path generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
         kml_gen.save_to_file(file_path)








         self.update_status(f"Path exported to {file_path}")
         self.last_kml_file = file_path
     except Exception as e:
         messagebox.showerror("Error", f"Failed to export path: {str(e)}")
         self.update_status("Error exporting path")

 def open_in_google_earth(self):
     """Abre el último archivo KML generado en Google Earth"""
     if not hasattr(self, 'last_kml_file') or not os.path.exists(self.last_kml_file):
         messagebox.showwarning("Warning", "No KML file has been generated yet")
         return








     try:
         webbrowser.open(self.last_kml_file)
         self.update_status(f"Opening {self.last_kml_file} in Google Earth")
     except Exception as e:
         messagebox.showerror("Error", f"Failed to open Google Earth: {str(e)}")
         self.update_status("Error opening Google Earth")

 # =============================================
 # Funcionalidades avanzadas
 # =============================================

 def add_to_avoid_list(self):
     """Añade nodos seleccionados a la lista de evitados"""
     if not self.selected_nodes:
         messagebox.showwarning("Warning", "Please select a node first")
         return








     node = self.selected_nodes[0]
     node_id = node.number if self.current_airspace else node.name








     if node_id in self.avoid_nodes:
         messagebox.showinfo("Info", "Node is already in avoid list")
         return








     self.avoid_nodes.add(node_id)
     self.update_avoid_listbox()








     if self.current_airspace:
         self.plot_airspace()
     else:
         self.plot_graph()








     self.update_status(f"Added {node_id} to avoid list")

 def remove_from_avoid_list(self):
     """Elimina nodos de la lista de evitados"""
     selection = self.avoid_listbox.curselection()
     if not selection:
         messagebox.showwarning("Warning", "Please select a node from the list")
         return








     node_id = self.avoid_listbox.get(selection[0])
     self.avoid_nodes.remove(node_id)
     self.update_avoid_listbox()








     if self.current_airspace:
         self.plot_airspace()
     else:
         self.plot_graph()








     self.update_status(f"Removed {node_id} from avoid list")

 def update_avoid_listbox(self):
     """Actualiza la lista de nodos a evitar"""
     self.avoid_listbox.delete(0, tk.END)
     for node_id in sorted(self.avoid_nodes):
         self.avoid_listbox.insert(tk.END, node_id)

 def find_alternative_path(self):
     """Encuentra un camino alternativo evitando nodos seleccionados"""
     if len(self.selected_nodes) < 2:
         messagebox.showwarning("Warning", "Please select start and end nodes first")
         return








     if self.current_airspace:
         start_id = self.selected_nodes[0].number
         end_id = self.selected_nodes[1].number








         # Implementar búsqueda de camino alternativo para airspace
         # (similar a A* pero evitando los nodos en avoid_nodes)
         pass
     else:
         start_name = self.selected_nodes[0].name
         end_name = self.selected_nodes[1].name








         # Implementar búsqueda de camino alternativo para grafo normal
         path = FindAlternativePath(self.current_graph, start_name, end_name, self.avoid_nodes)








         if path:
             self.current_path = path
             self.plot_graph()
             path_names = [node.name for node in path.nodes]
             self.update_info(f"Alternative path (avoiding {len(self.avoid_nodes)} nodes):\n" +
                              f"{' -> '.join(path_names)}\nTotal cost: {path.cost:.2f}")
         else:
             self.update_info(f"No alternative path exists between {start_name} and {end_name} " +
                              f"while avoiding {len(self.avoid_nodes)} nodes")

 def optimize_route(self):
     """Optimiza la ruta considerando múltiples factores"""
     if len(self.selected_nodes) < 2:
         messagebox.showwarning("Warning", "Please select start and end nodes first")
         return








     # Implementar lógica de optimización según criterios específicos
     # (por ejemplo, menor número de segmentos, menor costo total, etc.)
     pass

 # =============================================
 # Métodos auxiliares
 # =============================================

 def show_example1(self):
     """Carga el primer grafo de ejemplo"""
     self.update_status("Loading example graph 1...")
     self.current_graph = CreateGraph_1()
     self.current_airspace = None
     self.clear_analysis()
     self.plot_graph()

 def show_example2(self):
     """Carga el segundo grafo de ejemplo"""
     self.update_status("Loading example graph 2...")
     self.current_graph = CreateGraph_2()
     self.current_airspace = None
     self.clear_analysis()
     self.plot_graph()

 def select_node(self, node):
     """Maneja la selección de un nodo en grafo normal"""
     self.selected_nodes.append(node)
     if len(self.selected_nodes) > 2:
         self.selected_nodes.pop(0)








     self.plot_graph()
     self.update_info(f"Selected: {node.name}")

 def toggle_add_node_mode(self):
     """Activa/desactiva el modo de añadir nodo"""
     self.new_node_mode = not self.new_node_mode
     self.new_segment_mode = False
     self.delete_mode = False


     if self.new_node_mode:
         self.update_status("Add Node Mode: Click on the canvas to add a new node")
     else:
         self.update_status("Ready")


     self.mode_var.set("select")

 def toggle_add_segment_mode(self):
     """Activa/desactiva el modo de añadir segmento"""
     self.new_segment_mode = not self.new_segment_mode
     self.new_node_mode = False
     self.delete_mode = False


     if self.new_segment_mode:
         self.update_status("Add Segment Mode: Select two nodes to connect")
     else:
         self.update_status("Ready")


     self.mode_var.set("select")

 def toggle_delete_mode(self):
     """Activa/desactiva el modo de eliminar"""
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

 def update_info(self, message):
     """Actualiza el panel de información"""
     self.info_text.delete(1.0, tk.END)
     self.info_text.insert(tk.END, message)

 def update_status(self, message):
     """Actualiza la barra de estado"""
     self.status_var.set(message)
     self.root.update_idletasks()

 def find_reachable_interactive(self):
     """Maneja la búsqueda de nodos alcanzables desde la interfaz"""
     if not self.selected_nodes:
         messagebox.showwarning("Warning", "Please select a starting point first")
         return








     if self.current_airspace:
         self.find_reachable_from(self.selected_nodes[0].number)
     else:
         self.find_reachable_from(self.selected_nodes[0].name)

 def find_shortest_path_interactive(self):
     """Maneja la búsqueda de camino más corto desde la interfaz"""
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

if __name__ == "__main__":
 root = tk.Tk()
 app = GraphApp(root)
 root.mainloop()



