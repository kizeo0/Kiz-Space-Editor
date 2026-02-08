import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from datetime import datetime
import shutil

class FileExpanderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kiz Space Editor - Expansor Hex")
        self.root.geometry("900x730")
        
        # Configurar para cerrar correctamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Variables
        self.file_paths = []
        self.processing = False
        self.output_folder = tk.StringVar()
        self.output_folder.set(os.path.expanduser("~\\Desktop"))  # Por defecto en Escritorio
        
        # Establecer colores de fondo
        self.root.configure(bg='#0a0a0a')
        
        # Cargar icono si existe
        self.load_icon()
        
        # Estilos
        self.setup_styles()
        
        # Interfaz
        self.setup_ui()
    
    def load_icon(self):
        """Intenta cargar el icono de la aplicación."""
        icon_paths = [
            'icon.ico',
            'icon.png',
            os.path.join(os.path.dirname(__file__), 'icon.ico'),
            os.path.join(os.path.dirname(__file__), 'icon.png')
        ]
        
        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    if icon_path.endswith('.ico'):
                        self.root.iconbitmap(icon_path)
                    break
            except:
                continue
    
    def setup_styles(self):
        """Configura los estilos de la aplicación."""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Colores
        self.colors = {
            'bg': '#0a0a0a',
            'fg': '#ffffff',
            'accent': '#1e3a8a',  # Azul marino
            'accent_light': '#3b82f6',
            'secondary': '#1f2937',
            'success': '#10b981',
            'error': '#ef4444',
            'warning': '#f59e0b'
        }
        
        # Configurar estilos básicos
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        
        # Configurar botones
        style.configure('Custom.TButton', 
                       background=self.colors['accent'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       relief='raised',
                       padding=6)
        style.map('Custom.TButton',
                 background=[('active', self.colors['accent_light']),
                            ('disabled', '#4b5563')])
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para scroll
        self.canvas = tk.Canvas(main_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="🚀 KIZ SPACE EDITOR",
                              font=('Segoe UI', 18, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['accent_light'])
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Expansor Hexadecimal de Archivos",
                                 font=('Segoe UI', 12),
                                 bg=self.colors['bg'],
                                 fg=self.colors['fg'])
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Área de archivos
        self.setup_file_area(self.scrollable_frame)
        
        # Controles de tamaño
        self.setup_size_controls(self.scrollable_frame)
        
        # Controles de salida
        self.setup_output_controls(self.scrollable_frame)
        
        # Botones de acción
        self.setup_action_buttons(self.scrollable_frame)
        
        # Área de logs
        self.setup_log_area(self.scrollable_frame)
        
        # Status bar
        self.setup_status_bar()
        
        # Configurar eventos del mouse para el scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Maneja el scroll del mouse."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_file_area(self, parent):
        """Configura el área para seleccionar archivos."""
        file_frame = tk.Frame(parent, bg=self.colors['secondary'], relief='solid', bd=2)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Botón para agregar archivos
        btn_frame = tk.Frame(file_frame, bg=self.colors['secondary'])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        add_files_btn = tk.Button(btn_frame,
                                 text="📁 Agregar Archivos",
                                 command=self.browse_files,
                                 bg=self.colors['accent'],
                                 fg=self.colors['fg'],
                                 font=('Segoe UI', 10),
                                 relief='raised',
                                 padx=15,
                                 pady=5,
                                 cursor="hand2")
        add_files_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        add_folder_btn = tk.Button(btn_frame,
                                  text="📂 Agregar Carpeta",
                                  command=self.browse_folder,
                                  bg=self.colors['accent'],
                                  fg=self.colors['fg'],
                                  font=('Segoe UI', 10),
                                  relief='raised',
                                  padx=15,
                                  pady=5,
                                  cursor="hand2")
        add_folder_btn.pack(side=tk.LEFT)
        
        # Lista de archivos
        list_frame = tk.Frame(file_frame, bg=self.colors['secondary'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.file_listbox = tk.Listbox(list_frame,
                                      bg=self.colors['secondary'],
                                      fg=self.colors['fg'],
                                      selectbackground=self.colors['accent'],
                                      selectforeground=self.colors['fg'],
                                      font=('Consolas', 9),
                                      relief='flat',
                                      height=6)
        
        scrollbar = ttk.Scrollbar(list_frame)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Info label debajo de la lista
        self.file_info_label = tk.Label(file_frame,
                                       bg=self.colors['secondary'],
                                       fg=self.colors['accent_light'],
                                       font=('Segoe UI', 9))
        self.file_info_label.pack(pady=(0, 10))
    
    def setup_size_controls(self, parent):
        """Configura los controles de tamaño."""
        size_frame = tk.Frame(parent, bg=self.colors['bg'])
        size_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title_label = tk.Label(size_frame,
                              text="🔧 CONFIGURACIÓN DE EXPANSIÓN",
                              font=('Segoe UI', 11, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['fg'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para controles
        controls_frame = tk.Frame(size_frame, bg=self.colors['bg'])
        controls_frame.pack(fill=tk.X)
        
        # Tamaño
        tk.Label(controls_frame, text="Tamaño a agregar:", 
                bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, padx=(0, 10), sticky='w')
        
        self.size_entry = ttk.Entry(controls_frame, width=15, font=('Segoe UI', 11))
        self.size_entry.grid(row=0, column=1, padx=(0, 10))
        self.size_entry.insert(0, "100")
        
        # Unidad
        self.unit_var = tk.StringVar(value="KB")
        unit_combo = ttk.Combobox(controls_frame, 
                                 textvariable=self.unit_var,
                                 values=["Bytes", "KB", "MB"],
                                 state="readonly",
                                 width=8)
        unit_combo.grid(row=0, column=2, padx=(0, 20))
        
        # Modo de expansión
        tk.Label(controls_frame, text="Modo:", 
                bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=3, padx=(0, 10), sticky='w')
        
        self.mode_var = tk.StringVar(value="Agregar")
        mode_combo = ttk.Combobox(controls_frame,
                                 textvariable=self.mode_var,
                                 values=["Agregar", "Establecer tamaño"],
                                 state="readonly",
                                 width=15)
        mode_combo.grid(row=0, column=4)
        
        # Info label
        self.size_info_label = tk.Label(size_frame,
                                       text="",
                                       bg=self.colors['bg'],
                                       fg=self.colors['accent_light'],
                                       font=('Segoe UI', 9))
        self.size_info_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Bind para actualizar información
        self.size_entry.bind('<KeyRelease>', self.update_size_info)
        unit_combo.bind('<<ComboboxSelected>>', self.update_size_info)
        mode_combo.bind('<<ComboboxSelected>>', self.update_size_info)
    
    def setup_output_controls(self, parent):
        """Configura los controles de salida."""
        output_frame = tk.Frame(parent, bg=self.colors['bg'])
        output_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title_label = tk.Label(output_frame,
                              text="📁 DESTINO DE SALIDA",
                              font=('Segoe UI', 11, 'bold'),
                              bg=self.colors['bg'],
                              fg=self.colors['fg'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para controles
        controls_frame = tk.Frame(output_frame, bg=self.colors['bg'])
        controls_frame.pack(fill=tk.X)
        
        # Checkbox para usar ubicación personalizada
        self.custom_output_var = tk.BooleanVar(value=False)
        custom_output_cb = tk.Checkbutton(controls_frame,
                                         text="Guardar en ubicación personalizada",
                                         variable=self.custom_output_var,
                                         bg=self.colors['bg'],
                                         fg=self.colors['fg'],
                                         selectcolor=self.colors['bg'],
                                         activebackground=self.colors['bg'],
                                         activeforeground=self.colors['fg'],
                                         command=self.toggle_output_folder)
        custom_output_cb.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 10))
        
        # Carpeta de salida
        tk.Label(controls_frame, text="Carpeta de salida:", 
                bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, padx=(0, 10), sticky='w')
        
        self.output_entry = ttk.Entry(controls_frame, 
                                     textvariable=self.output_folder,
                                     width=40,
                                     font=('Segoe UI', 10),
                                     state='disabled')
        self.output_entry.grid(row=1, column=1, padx=(0, 10))
        
        self.browse_output_btn = tk.Button(controls_frame,
                                          text="📂 Examinar",
                                          command=self.browse_output_folder,
                                          bg=self.colors['accent'],
                                          fg=self.colors['fg'],
                                          font=('Segoe UI', 9),
                                          relief='raised',
                                          padx=10,
                                          pady=3,
                                          cursor="hand2",
                                          state='disabled')
        self.browse_output_btn.grid(row=1, column=2)
        
        # Checkbox para prefijo
        self.use_prefix_var = tk.BooleanVar(value=True)
        prefix_cb = tk.Checkbutton(controls_frame,
                                  text='Agregar prefijo "Nuevo_" a los nombres',
                                  variable=self.use_prefix_var,
                                  bg=self.colors['bg'],
                                  fg=self.colors['fg'],
                                  selectcolor=self.colors['bg'],
                                  activebackground=self.colors['bg'],
                                  activeforeground=self.colors['fg'])
        prefix_cb.grid(row=2, column=0, columnspan=3, sticky='w', pady=(10, 0))
        
        # Info label
        self.output_info_label = tk.Label(output_frame,
                                         text="Por defecto, los archivos se guardan en la misma ubicación original",
                                         bg=self.colors['bg'],
                                         fg=self.colors['accent_light'],
                                         font=('Segoe UI', 9))
        self.output_info_label.pack(anchor=tk.W, pady=(10, 0))
    
    def setup_action_buttons(self, parent):
        """Configura los botones de acción."""
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botón limpiar
        clear_btn = tk.Button(button_frame,
                             text="🗑️ Limpiar lista",
                             command=self.clear_files,
                             bg=self.colors['accent'],
                             fg=self.colors['fg'],
                             font=('Segoe UI', 10),
                             relief='raised',
                             padx=15,
                             pady=5,
                             cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón procesar
        self.process_btn = tk.Button(button_frame,
                                    text="⚡ PROCESAR ARCHIVOS",
                                    command=self.process_files,
                                    bg=self.colors['accent'],
                                    fg=self.colors['fg'],
                                    font=('Segoe UI', 10, 'bold'),
                                    relief='raised',
                                    padx=20,
                                    pady=5,
                                    cursor="hand2")
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón salir
        exit_btn = tk.Button(button_frame,
                            text="❌ Salir",
                            command=self.on_closing,
                            bg='#dc2626',
                            fg=self.colors['fg'],
                            font=('Segoe UI', 10),
                            relief='raised',
                            padx=15,
                            pady=5,
                            cursor="hand2")
        exit_btn.pack(side=tk.LEFT)
    
    def setup_log_area(self, parent):
        """Configura el área de logs."""
        log_frame = tk.Frame(parent, bg=self.colors['bg'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(log_frame,
                text="📝 REGISTRO DE ACTIVIDAD",
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['bg'],
                fg=self.colors['fg']).pack(anchor=tk.W, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 bg=self.colors['secondary'],
                                                 fg=self.colors['fg'],
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD,
                                                 height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Configurar tags para colores
        self.log_text.tag_config('success', foreground=self.colors['success'])
        self.log_text.tag_config('error', foreground=self.colors['error'])
        self.log_text.tag_config('warning', foreground=self.colors['warning'])
        self.log_text.tag_config('info', foreground=self.colors['accent_light'])
        self.log_text.tag_config('header', font=('Consolas', 10, 'bold'))
    
    def setup_status_bar(self):
        """Configura la barra de estado."""
        self.status_var = tk.StringVar(value="📊 Listo. Agrega archivos para comenzar")
        
        status_bar = tk.Frame(self.root, bg=self.colors['secondary'], relief='sunken', bd=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = tk.Label(status_bar,
                               textvariable=self.status_var,
                               bg=self.colors['secondary'],
                               fg=self.colors['fg'],
                               anchor=tk.W,
                               padx=10)
        status_label.pack(fill=tk.X, ipady=5)
    
    def toggle_output_folder(self):
        """Habilita o deshabilita los controles de carpeta de salida."""
        if self.custom_output_var.get():
            self.output_entry.config(state='normal')
            self.browse_output_btn.config(state='normal')
            self.output_info_label.config(text="Los archivos se guardarán en la carpeta seleccionada")
        else:
            self.output_entry.config(state='disabled')
            self.browse_output_btn.config(state='disabled')
            self.output_info_label.config(text="Por defecto, los archivos se guardan en la misma ubicación original")
    
    def browse_files(self):
        """Abre el diálogo para seleccionar archivos."""
        if self.processing:
            messagebox.showwarning("Procesando", "Espera a que termine el procesamiento actual")
            return
        
        files = filedialog.askopenfilenames(title="Seleccionar archivos")
        if files:
            self.add_files(files)
    
    def browse_folder(self):
        """Abre el diálogo para seleccionar una carpeta."""
        if self.processing:
            messagebox.showwarning("Procesando", "Espera a que termine el procesamiento actual")
            return
        
        folder = filedialog.askdirectory(title="Seleccionar carpeta")
        if folder:
            self.add_folder(folder)
    
    def browse_output_folder(self):
        """Abre el diálogo para seleccionar carpeta de salida."""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder.set(folder)
    
    def add_files(self, files):
        """Agrega archivos a la lista."""
        added_count = 0
        for file_path in files:
            if os.path.isfile(file_path) and file_path not in self.file_paths:
                self.file_paths.append(file_path)
                added_count += 1
        
        if added_count > 0:
            self.update_file_list()
            self.update_size_info()
            self.log_message(f"✓ Se agregaron {added_count} archivos", 'success')
        else:
            self.log_message("⚠️ No se agregaron archivos nuevos", 'warning')
    
    def add_folder(self, folder):
        """Agrega todos los archivos de una carpeta."""
        if not os.path.isdir(folder):
            self.log_message(f"✗ La carpeta no existe: {folder}", 'error')
            return
        
        added_count = 0
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
                    added_count += 1
        
        if added_count > 0:
            self.update_file_list()
            self.update_size_info()
            self.log_message(f"✓ Se agregaron {added_count} archivos desde la carpeta", 'success')
        else:
            self.log_message(f"⚠️ No se encontraron archivos en: {folder}", 'warning')
    
    def update_file_list(self):
        """Actualiza la lista de archivos en la interfaz."""
        self.file_listbox.delete(0, tk.END)
        
        for i, path in enumerate(self.file_paths[:50]):  # Mostrar máximo 50
            filename = os.path.basename(path)
            try:
                size = os.path.getsize(path)
                display_text = f"{i+1:3d}. {filename} ({self.format_size(size)})"
            except:
                display_text = f"{i+1:3d}. {filename} (Error al obtener tamaño)"
            self.file_listbox.insert(tk.END, display_text)
        
        total_count = len(self.file_paths)
        if total_count > 50:
            self.file_listbox.insert(tk.END, f"... y {total_count - 50} archivos más")
        
        # Actualizar info label
        try:
            total_size = sum(os.path.getsize(p) for p in self.file_paths if os.path.exists(p))
            self.file_info_label.config(
                text=f"📁 Total: {total_count} archivos | 📊 Tamaño total: {self.format_size(total_size)}"
            )
        except:
            self.file_info_label.config(text=f"📁 Total: {total_count} archivos")
        
        self.status_var.set(f"📊 {total_count} archivos listos para procesar")
    
    def clear_files(self):
        """Limpia la lista de archivos."""
        if self.processing:
            messagebox.showwarning("Procesando", "Espera a que termine el procesamiento actual")
            return
        
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)
        self.file_info_label.config(text="")
        self.status_var.set("📊 Listo. Agrega archivos para comenzar")
        self.log_message("🗑️ Lista de archivos limpiada", 'info')
    
    def update_size_info(self, event=None):
        """Actualiza la información del tamaño."""
        if not self.file_paths:
            self.size_info_label.config(text="")
            return
        
        try:
            size_value = float(self.size_entry.get())
            unit = self.unit_var.get()
            mode = self.mode_var.get()
            
            # Convertir a bytes
            if unit == "KB":
                add_bytes = int(size_value * 1024)
            elif unit == "MB":
                add_bytes = int(size_value * 1024 * 1024)
            else:
                add_bytes = int(size_value)
            
            if mode == "Agregar":
                total_added = add_bytes * len(self.file_paths)
                info_text = f"📈 Se agregarán {self.format_size(add_bytes)} a cada archivo "
                info_text += f"(Total: {self.format_size(total_added)})"
            else:
                # Calcular cuánto se agregaría a cada archivo
                try:
                    current_total = sum(os.path.getsize(p) for p in self.file_paths)
                    avg_current = current_total / len(self.file_paths) if self.file_paths else 0
                    info_text = f"📏 Tamaño actual promedio: {self.format_size(avg_current)} "
                    info_text += f"| Nuevo tamaño: {self.format_size(add_bytes)}"
                except:
                    info_text = "⚠️ Error al calcular tamaños"
            
            self.size_info_label.config(text=info_text)
            
        except ValueError:
            self.size_info_label.config(text="⚠️ Tamaño inválido")
        except Exception as e:
            self.size_info_label.config(text=f"⚠️ Error: {str(e)}")
    
    def format_size(self, size_bytes):
        """Formatea bytes a unidades legibles."""
        try:
            size_bytes = float(size_bytes)
            if size_bytes >= 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            elif size_bytes >= 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
            elif size_bytes >= 1024:
                return f"{size_bytes / 1024:.2f} KB"
            else:
                return f"{size_bytes:.0f} bytes"
        except:
            return "0 bytes"
    
    def log_message(self, message, tag=''):
        """Agrega un mensaje al log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry, tag)
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()
    
    def process_files(self):
        """Procesa los archivos seleccionados."""
        if self.processing:
            messagebox.showwarning("Procesando", "Ya hay un procesamiento en curso")
            return
        
        if not self.file_paths:
            messagebox.showwarning("Sin archivos", "No hay archivos para procesar")
            return
        
        try:
            # Obtener configuración
            size_value = float(self.size_entry.get())
            unit = self.unit_var.get()
            mode = self.mode_var.get()
            
            # Convertir a bytes
            if unit == "KB":
                add_bytes = int(size_value * 1024)
            elif unit == "MB":
                add_bytes = int(size_value * 1024 * 1024)
            else:
                add_bytes = int(size_value)
            
            if add_bytes <= 0:
                messagebox.showerror("Error", "El tamaño debe ser mayor que 0")
                return
            
            # Verificar carpeta de salida si está habilitada
            if self.custom_output_var.get():
                output_folder = self.output_folder.get()
                if not output_folder or not os.path.isdir(output_folder):
                    messagebox.showerror("Error", "Por favor selecciona una carpeta de salida válida")
                    return
            
            # Confirmación
            confirm_msg = f"¿Procesar {len(self.file_paths)} archivos?\n"
            confirm_msg += f"Se agregarán {self.format_size(add_bytes)} a cada archivo.\n\n"
            
            if self.custom_output_var.get():
                confirm_msg += f"📁 Carpeta de salida: {self.output_folder.get()}\n"
                if self.use_prefix_var.get():
                    confirm_msg += '📝 Los archivos tendrán el prefijo "Nuevo_"\n'
            else:
                confirm_msg += "📁 Los archivos se guardarán en su ubicación original\n"
                if self.use_prefix_var.get():
                    confirm_msg += '📝 Los archivos tendrán el prefijo "Nuevo_"\n'
            
            if not messagebox.askyesno("Confirmar", confirm_msg):
                return
            
            # Iniciar procesamiento en hilo separado
            self.processing = True
            self.process_btn.config(state='disabled', text="⏳ PROCESANDO...")
            self.status_var.set("⏳ Procesando archivos...")
            
            thread = threading.Thread(target=self.process_files_thread, 
                                     args=(add_bytes, mode),
                                     daemon=True)
            thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Tamaño inválido: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def process_files_thread(self, add_bytes, mode):
        """Hilo para procesar archivos."""
        success_count = 0
        error_count = 0
        
        use_custom_output = self.custom_output_var.get()
        output_folder = self.output_folder.get() if use_custom_output else None
        use_prefix = self.use_prefix_var.get()
        
        self.log_message(f"🚀 Iniciando procesamiento de {len(self.file_paths)} archivos", 'header')
        self.log_message(f"Modo: {mode} | Bytes por archivo: {add_bytes:,}", 'info')
        if use_custom_output:
            self.log_message(f"📁 Carpeta de salida: {output_folder}", 'info')
            if use_prefix:
                self.log_message('📝 Los archivos tendrán el prefijo "Nuevo_"', 'info')
        
        for i, file_path in enumerate(self.file_paths, 1):
            try:
                # Actualizar estado
                filename = os.path.basename(file_path)
                display_name = filename[:30] + "..." if len(filename) > 30 else filename
                self.root.after(0, self.status_var.set, 
                              f"⏳ Procesando {i}/{len(self.file_paths)}: {display_name}")
                
                # Determinar ruta de salida
                if use_custom_output:
                    output_filename = f"Nuevo_{filename}" if use_prefix else filename
                    output_path = os.path.join(output_folder, output_filename)
                    success = self.process_file_with_output(file_path, output_path, add_bytes, mode)
                else:
                    if use_prefix:
                        # Misma carpeta, pero con prefijo
                        dir_name = os.path.dirname(file_path)
                        output_filename = f"Nuevo_{filename}"
                        output_path = os.path.join(dir_name, output_filename)
                        success = self.process_file_with_output(file_path, output_path, add_bytes, mode)
                    else:
                        # Modificar archivo original
                        success = self.process_file_original(file_path, add_bytes, mode)
                
                if success:
                    success_count += 1
                    output_name = os.path.basename(output_path) if use_custom_output or use_prefix else filename
                    self.root.after(0, self.log_message, f"✓ {output_name} - Completado", 'success')
                else:
                    error_count += 1
                    self.root.after(0, self.log_message, f"✗ {filename} - Error", 'error')
                
                # Actualizar progreso cada 10 archivos
                if i % 10 == 0 or i == len(self.file_paths):
                    percent = (i / len(self.file_paths)) * 100
                    self.root.after(0, self.status_var.set, 
                                  f"⏳ Progreso: {i}/{len(self.file_paths)} ({percent:.1f}%)")
                
            except Exception as e:
                error_count += 1
                self.root.after(0, self.log_message, f"✗ {os.path.basename(file_path)} - Error: {str(e)[:50]}", 'error')
        
        # Finalizar
        self.root.after(0, self.process_complete, success_count, error_count)
    
    def process_file_with_output(self, input_path, output_path, add_bytes, mode):
        """Procesa un archivo guardando en una nueva ubicación."""
        try:
            # Copiar archivo original
            shutil.copy2(input_path, output_path)
            
            # Expandir archivo copiado
            if mode == "Agregar":
                with open(output_path, 'ab') as file:
                    file.write(b'\x00' * add_bytes)
            else:  # Establecer tamaño
                current_size = os.path.getsize(output_path)
                if add_bytes > current_size:
                    with open(output_path, 'ab') as file:
                        file.write(b'\x00' * (add_bytes - current_size))
            
            return True
        except Exception as e:
            self.log_message(f"  Error procesando {os.path.basename(input_path)}: {str(e)[:50]}", 'error')
            return False
    
    def process_file_original(self, file_path, add_bytes, mode):
        """Procesa un archivo modificando el original."""
        try:
            if mode == "Agregar":
                with open(file_path, 'ab') as file:
                    file.write(b'\x00' * add_bytes)
            else:  # Establecer tamaño
                current_size = os.path.getsize(file_path)
                if add_bytes > current_size:
                    with open(file_path, 'ab') as file:
                        file.write(b'\x00' * (add_bytes - current_size))
            
            return True
        except Exception as e:
            self.log_message(f"  Error procesando {os.path.basename(file_path)}: {str(e)[:50]}", 'error')
            return False
    
    def process_complete(self, success_count, error_count):
        """Finaliza el procesamiento."""
        self.processing = False
        self.process_btn.config(state='normal', text="⚡ PROCESAR ARCHIVOS")
        
        # Resumen
        self.log_message("=" * 50, 'header')
        self.log_message("📊 RESUMEN DEL PROCESAMIENTO", 'header')
        self.log_message(f"✓ Archivos exitosos: {success_count}", 'success')
        
        if error_count > 0:
            self.log_message(f"✗ Archivos con error: {error_count}", 'error')
        else:
            self.log_message(f"✗ Archivos con error: {error_count}", 'info')
        
        if success_count > 0:
            total_added = self.calculate_total_added()
            self.log_message(f"📈 Total expandido: {self.format_size(total_added)}", 'info')
            
            # Mostrar ubicación de los archivos
            if self.custom_output_var.get():
                self.log_message(f"📁 Archivos guardados en: {self.output_folder.get()}", 'info')
        
        self.status_var.set(f"✅ Procesamiento completado - {success_count} exitosos, {error_count} errores")
        
        # Mostrar mensaje final
        if error_count == 0:
            self.root.after(100, messagebox.showinfo, "Completado", 
                          f"✅ Todos los {success_count} archivos fueron procesados exitosamente.")
        else:
            self.root.after(100, messagebox.showwarning, "Completado con errores",
                          f"Procesamiento completado.\n"
                          f"✓ Exitosos: {success_count}\n"
                          f"✗ Errores: {error_count}")
    
    def calculate_total_added(self):
        """Calcula el total de bytes agregados."""
        try:
            size_value = float(self.size_entry.get())
            unit = self.unit_var.get()
            
            if unit == "KB":
                add_bytes = int(size_value * 1024)
            elif unit == "MB":
                add_bytes = int(size_value * 1024 * 1024)
            else:
                add_bytes = int(size_value)
            
            return add_bytes * len(self.file_paths)
        except:
            return 0
    
    def on_closing(self):
        """Maneja el cierre de la ventana."""
        if self.processing:
            if not messagebox.askyesno("Procesando", 
                                      "Hay un procesamiento en curso.\n¿Realmente quieres salir?"):
                return
        
        self.root.quit()
        self.root.destroy()

def main():
    """Función principal."""
    try:
        root = tk.Tk()
        
        # Configurar DPI awareness (solo Windows)
        if sys.platform == "win32":
            try:
                from ctypes import windll, oledll
                # Intentar diferentes métodos para DPI awareness
                try:
                    windll.shcore.SetProcessDpiAwareness(1)
                except:
                    try:
                        windll.user32.SetProcessDPIAware()
                    except:
                        pass
            except:
                pass
        
        # Configurar aplicación
        app = FileExpanderApp(root)
        
        # Centrar ventana
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        # Mostrar error en ventana emergente
        try:
            error_msg = f"Error al iniciar la aplicación:\n\n{str(e)}\n\n"
            error_msg += "Posibles soluciones:\n"
            error_msg += "1. Asegúrate de tener Python 3.x instalado\n"
            error_msg += "2. Ejecuta como administrador si es necesario\n"
            error_msg += "3. Verifica que no haya conflictos con otros programas"
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error de Inicio", error_msg)
            root.destroy()
        except:
            print(f"Error al iniciar la aplicación: {e}")
            input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
