import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import importlib.util
import json
from pathlib import Path
from tkinter import filedialog
import os


class App:
    """Clase principal de la aplicación de Lista de Compras"""
    
    def __init__(self, root: tk.Tk):
        """
        Inicializa la aplicación
        
        Args:
            root (tk.Tk): Ventana principal de Tkinter
        """
        self.root = root
        self.root.title("Lista de compras")
        self.root.geometry("700x520")

        # Lista para almacenar los ítems (cada uno con texto y estado de "hecho")
        self.items = []
        # Almacena la ruta del archivo abierto actualmente
        self.current_file = None

        # Construir interfaz gráfica
        self._build_ui()
        # Vincular atajos de teclado
        self._bind_shortcuts()
        # Renderizar tabla inicial
        self.render()
        # Actualizar barra de estado
        self.update_status()

    def _build_ui(self):
        """Construye la interfaz gráfica de la aplicación"""
        
        # Marco principal con padding
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        # ===== SECCIÓN: Formulario de entrada =====
        form = ttk.Frame(main)
        form.pack(fill="x")

        # Etiqueta para el campo de entrada
        ttk.Label(form, text="Ítem:").grid(row=0, column=0, padx=(0, 6))
        # Variable para almacenar el texto ingresado
        self.var_item = tk.StringVar()

        # Campo de entrada para escribir ítems
        entry = ttk.Entry(form, textvariable=self.var_item)
        entry.grid(row=0, column=1, sticky="ew")
        # Hace que el campo de entrada sea flexible (expande con la ventana)
        form.columnconfigure(1, weight=1)

        # Botón para agregar ítem manualmente
        ttk.Button(form, text="Agregar", command=self.add_item).grid(row=0, column=2, padx=(8, 0))

        # Permite agregar ítem presionando Enter
        entry.bind("<Return>", lambda e: self.add_item())

        # ===== SECCIÓN: Barra de acciones =====
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(6, 0))

        # Botón para eliminar ítems seleccionados
        ttk.Button(actions, text="Eliminar seleccionado(s)", command=self.delete_selected).pack(side="left")
        # Botón para limpiar toda la lista
        ttk.Button(actions, text="Limpiar lista", command=self.clear_list).pack(side="left", padx=6)

        # Botón para guardar la lista en JSON (Ctrl+S)
        ttk.Button(actions, text="Guardar (Ctrl+S)", command=self.guardar_lista).pack(side="left", padx=6)
        # Botón para abrir una lista guardada (Ctrl+O)
        ttk.Button(actions, text="Abrir (Ctrl+O)", command=self.abrir_lista).pack(side="left", padx=6)

        # ===== SECCIÓN: Tabla (Treeview) con scroll =====
        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True, pady=8)
        
        # Treeview para mostrar los ítems en tabla
        self.tree = ttk.Treeview(
            table_frame,
            columns=("item", "hecho"),
            show="headings",
            height=14
        )
        # Definir encabezados de las columnas
        self.tree.heading("item", text="Ítem")
        self.tree.heading("hecho", text="Hecho")
        # Configurar ancho y alineación de columnas
        self.tree.column("item", width=520, anchor="w")
        self.tree.column("hecho", width=80, anchor="center")
        # Empacar Treeview en la ventana
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar vertical para la tabla
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        # Conectar scrollbar con Treeview
        self.tree.configure(yscrollcommand=scroll.set)

        # ===== SECCIÓN: Barra de estado =====
        self.status = tk.StringVar(value="0 ítems · 0 hechos")
        # Etiqueta que muestra cantidad de ítems y progreso
        ttk.Label(self.root, textvariable=self.status, anchor="w").pack(fill="x", padx=12, pady=(0, 8))
        
        # ===== SECCIÓN: Barra de progreso =====
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        # Barra visual que muestra porcentaje de ítems completados
        self.progress.pack(fill="x", padx=12, pady=(0, 4))


    def _bind_shortcuts(self):
        """Vincula atajos de teclado a sus respectivas funciones"""
        
        # Atajo: Delete para eliminar ítems seleccionados
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        # Atajo: Doble clic para marcar/desmarcar como hecho
        self.tree.bind("<Double-1>", self.toggle_done)
        
        # Atajo: Ctrl+S para guardar lista
        self.root.bind("<Control-s>", lambda e: self.guardar_lista())
        # Atajo: Ctrl+O para abrir lista
        self.root.bind("<Control-o>", lambda e: self.abrir_lista())


    def add_item(self):
        """Agrega un nuevo ítem a la lista con validaciones"""
        
        # Obtener texto del campo de entrada y eliminar espacios
        text = (self.var_item.get() or "").strip()

        # Validar que no esté vacío
        if not text:
            messagebox.showinfo("Info", "Escribe un ítem.")
            return

        # Validar que no sea un duplicado (case-insensitive)
        if any(i["text"].lower() == text.lower() for i in self.items):
            # Preguntar al usuario si desea agregar duplicado
            continuar = messagebox.askyesno("Duplicado", f"El item \"{text}\" ya esta en la lista.\nDesea agregarlo igualmente?")
            if not continuar:
                # Limpiar campo si el usuario rechaza
                self.var_item.set("")
                return
        
        # Agregar el ítem a la lista con estado "no hecho"
        self.items.append({"text": text, "done": False})

        # Limpiar campo de entrada
        self.var_item.set("")

        # Actualizar tabla visual
        self.render()

        # Actualizar barra de estado y progreso
        self.update_status()
    
    def toggle_done(self, event):
        """
        Marca o desmarca un ítem como "hecho" al hacer doble clic
        
        Args:
            event: Evento del mouse (contiene posición)
        """
        
        # Obtener la fila donde se hizo clic
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        # Obtener índice del ítem en la lista
        index = self.tree.index(item_id)

        # Cambiar estado "hecho" del ítem (True <-> False)
        self.items[index]["done"] = not self.items[index]["done"]

        # Actualizar tabla visual
        self.render()
        # Actualizar barra de estado y progreso
        self.update_status()

    def delete_selected(self):
        """Elimina los ítems seleccionados de la tabla"""
        
        # Obtener filas seleccionadas
        sel = self.tree.selection()

        # Validar que hay al menos una fila seleccionada
        if not sel:
            messagebox.showinfo("Info", "Selecciona filas para eliminar.")
            return

        # Obtener índices de las filas seleccionadas
        indices = [self.tree.index(i) for i in sel]

        # Eliminar ítems en orden inverso para evitar cambios de índice
        for idx in sorted(indices, reverse=True):
            self.items.pop(idx)

        # Actualizar tabla visual
        self.render()
        # Actualizar barra de estado y progreso
        self.update_status()

    def clear_list(self):
        """Limpia toda la lista después de una confirmación"""
        
        # Validar que hay ítems
        if not self.items:
            return

        # Pedir confirmación al usuario
        if messagebox.askyesno("Limpiar", "¿Seguro que quieres limpiar toda la lista?"):
            # Vaciar lista de ítems
            self.items.clear()
            # Actualizar tabla visual
            self.render()
            # Actualizar barra de estado y progreso
            self.update_status()

    def guardar_lista(self):
        """Guarda la lista actual en un archivo JSON"""
        
        # Validar que hay ítems para guardar
        if not self.items:
            messagebox.showwarning("Advertencia", "No hay ítems para guardar.")
            return

        # Abrir diálogo para seleccionar ubicación y nombre del archivo
        file = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="data"
        )

        # Si el usuario seleccionó un archivo
        if file:
            try:
                # Guardar ítems en archivo JSON con indentación
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(self.items, f, ensure_ascii=False, indent=2)
                # Recordar archivo actual
                self.current_file = file
                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Lista guardada en:\n{file}")
            except Exception as e:
                # Mostrar mensaje de error si falla
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")

    def abrir_lista(self):
        """Abre una lista guardada desde un archivo JSON"""
        
        # Abrir diálogo para seleccionar archivo JSON
        file = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="data"
        )

        # Si el usuario seleccionó un archivo
        if file:
            try:
                # Leer contenido del archivo JSON
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Validar que el formato es correcto (lista de dicts con "text" y "done")
                if isinstance(data, list) and all(isinstance(i, dict) and "text" in i and "done" in i for i in data):
                    # Reemplazar lista actual con la cargada
                    self.items = data
                    # Recordar archivo actual
                    self.current_file = file
                    # Actualizar tabla visual
                    self.render()
                    # Actualizar barra de estado y progreso
                    self.update_status()
                    # Mostrar mensaje de éxito
                    messagebox.showinfo("Éxito", f"Lista cargada desde:\n{file}")
                else:
                    # Mostrar error si formato es incorrecto
                    messagebox.showerror("Error", "El archivo no tiene el formato correcto.")
            except Exception as e:
                # Mostrar error si no se puede leer el archivo
                messagebox.showerror("Error", f"No se pudo abrir:\n{str(e)}")

    def render(self):
        """Actualiza la tabla visual con los ítems actuales"""
        
        # Limpiar todas las filas existentes de la tabla
        self.tree.delete(*self.tree.get_children())

        # Agregar cada ítem a la tabla
        for it in self.items:
            # Mostrar "✔" si está hecho, vacío si no
            self.tree.insert("", "end", values=(it["text"], "✔" if it["done"] else ""))

    def update_status(self):
        """Actualiza la barra de estado y barra de progreso"""
        
        # Calcular total de ítems
        total = len(self.items)
        # Calcular cuántos ítems están marcados como "hecho"
        done = sum(1 for i in self.items if i["done"])
        # Calcular porcentaje (evitar división por cero)
        percent = (done / total * 100) if total else 0 
        # Actualizar texto de la barra de estado
        self.status.set(f"{total} ítems · {done} hechos · {percent:.0f}% completado")
        
        # Actualizar valor de la barra de progreso visual
        self.progress["value"] = percent
        

def main():
    """Función principal que configura la aplicación e inicia el bucle principal"""
    
    def instalar_si_falta(paquete):
        """
        Verifica si un paquete está instalado y lo instala si es necesario
        
        Args:
            paquete (str): Nombre del paquete a verificar e instalar
            
        Returns:
            bool: True si se instaló, False si ya estaba instalado
        """
        
        # Verificar si el paquete ya está instalado
        if importlib.util.find_spec(paquete) is None:
            # Pedir al usuario si desea instalar el tema ttkthemes
            elec = input("Desea instalar el tema Breeze-dark de la biblioteca ttkthemes? S/N: ").strip().lower()
            if elec == "s":
                print(f"Instalando {paquete}... Esto puede tardar unos minutos")
                # Instalar el paquete usando pip
                subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
                return True
            else:
                return False
        else:
            print(f"{paquete} ya está instalado.")
            return True
    
    # Verificar e instalar ttkthemes si es necesario        
    ttkthemes_disponible = instalar_si_falta("ttkthemes")
    
    # ⭐ CREAR VENTANA CON TEMA ⭐
    try:
        from ttkthemes import ThemedTk
        # Crear ventana SIN tema primero
        root = ThemedTk()
        print("✅ ThemedTk creado")
    except Exception as err:
        print(f"❌ Error al crear ThemedTk: {err}")
        # Si falla, usar ventana normal
        root = tk.Tk()
        print("⚠️ Usando tk.Tk normal (sin tema)")
    
    # Obtener ruta base del proyecto (carpeta padre del archivo actual)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Ruta al archivo TCL del tema Breeze Dark
    theme_tcl = os.path.join(base_dir, "breeze-dark", "breeze-dark.tcl")    
    
    # ⭐ CARGAR TEMA OSCURO ⭐
    try:
        # Verificar que el archivo existe
        if os.path.exists(theme_tcl):
            print(f"✅ Cargando tema desde: {theme_tcl}")
            root.tk.call("source", theme_tcl)
            # Aplicar tema DESPUÉS de cargar el archivo TCL
            if hasattr(root, 'set_theme'):
                root.set_theme("breeze-dark")
                print("✅ Tema Breeze Dark aplicado correctamente")
            else:
                print("⚠️ No se pudo aplicar set_theme")
        else:
            print(f"❌ Archivo de tema no encontrado en: {theme_tcl}")
    except Exception as err:
        # Mostrar error detallado
        print(f"❌ Error al cargar el tema: {err}")
        print(f"   Tipo de error: {type(err).__name__}")
    
    # Crear instancia de la aplicación
    App(root)
    
    # Iniciar bucle principal de eventos
    root.mainloop()

if __name__ == "__main__":
    main()