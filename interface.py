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
