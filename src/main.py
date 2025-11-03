# <<<<<<< feature/estructura-inicial
#  feature/estructura-inicial
import tkinter as tk  # Importa el módulo base de Tkinter y lo alias como tk
from tkinter import ttk, messagebox  # Importa widgets tematizados (ttk) y diálogos (messagebox)


class App:
    def __init__(self, root: tk.Tk):
        # Ventana raíz de la aplicación (objeto principal de Tkinter)
        self.root = root
        # Establece el título que verás en la barra superior de la ventana
        self.root.title("Lista de compras")
        # Fija el tamaño inicial de la ventana en píxeles: 700 (ancho) x 520 (alto)
        self.root.geometry("700x520")

        # Modelo de datos en memoria:
        # Lista de diccionarios con el formato: [{"text": str, "done": bool}]
        # - "text": el contenido del ítem
        # - "done": si el ítem está marcado como hecho (True/False)
        self.items = []

        # Construcción de la interfaz gráfica (widgets y layout)
        self._build_ui()
        # Registro de atajos de teclado (bindings)
        self._bind_shortcuts()
        # Primer render de la tabla a partir del modelo self.items
        self.render()
        # Actualiza el texto de la barra de estado (totales)
        self.update_status()

    def _build_ui(self):
        # Contenedor principal con padding interno para que no pegue a los bordes
        main = ttk.Frame(self.root, padding=12)
        # Empaqueta el contenedor para que llene todo el espacio y pueda expandirse
        main.pack(fill="both", expand=True)

        # ---------------------
        # Sección: Formulario (input + botón Agregar)
        # ---------------------
        form = ttk.Frame(main)  # Frame que agrupa el label, entry y botón
        form.pack(fill="x")     # Ocupar todo el ancho disponible

        ttk.Label(form, text="Ítem:").grid(row=0, column=0, padx=(0, 6))  # Etiqueta a la izquierda con padding
        self.var_item = tk.StringVar()  # Variable reactiva para vincular con el Entry

        # Campo de texto donde el usuario escribe el ítem
        entry = ttk.Entry(form, textvariable=self.var_item)
        # Ubicación en la grilla (fila 0, columna 1) y que se estire horizontalmente
        entry.grid(row=0, column=1, sticky="ew")
        # Hace que la columna 1 del formulario crezca cuando la ventana se expanda
        form.columnconfigure(1, weight=1)

        # Botón "Agregar" que invoca add_item al hacer clic
        ttk.Button(form, text="Agregar", command=self.add_item).grid(row=0, column=2, padx=(8, 0))

        # Atajo: presionar Enter en el Entry llama a add_item
        entry.bind("<Return>", lambda e: self.add_item())

        # ---------------------
        # Sección: Barra de acciones
        # ---------------------
        actions = ttk.Frame(main)  # Contenedor para los botones de acciones globales
        actions.pack(fill="x", pady=(6, 0))

        # Botón para eliminar las filas seleccionadas en la tabla (Treeview)
        ttk.Button(actions, text="Eliminar seleccionado(s)", command=self.delete_selected).pack(side="left")

        # Botón para limpiar toda la lista (con confirmación)
        ttk.Button(actions, text="Limpiar lista", command=self.clear_list).pack(side="left", padx=6)

        # ---------------------
        # Sección: Tabla (Treeview) con scroll
        # ---------------------
        table_frame = ttk.Frame(main)  # Contenedor para la tabla y la barra de scroll
        table_frame.pack(fill="both", expand=True, pady=8)

        # Crea el Treeview como una tabla con dos columnas lógicas: "item" y "hecho"
        self.tree = ttk.Treeview(
            table_frame,
            columns=("item", "hecho"),  # Identificadores internos de columnas
            show="headings",            # Muestra sólo encabezados (sin columna de árbol)
            height=14                   # Alto visible en cantidad de filas (aprox.)
        )
        # Encabezados visibles
        self.tree.heading("item", text="Ítem")
        self.tree.heading("hecho", text="Hecho")
        # Configuración de columnas: ancho y alineación
        self.tree.column("item", width=520, anchor="w")
        self.tree.column("hecho", width=80, anchor="center")
        # Empaquetar la tabla para que llene y se expanda dentro del frame
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar vertical y conexión con el desplazamiento de la tabla
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)  # Vincula la tabla para actualizar la posición del scroll

        # ---------------------
        # Sección: Barra de estado (contador)
        # ---------------------
        # Variable de texto para el estado (ej.: "3 ítems · 1 hechos")
        self.status = tk.StringVar(value="0 ítems · 0 hechos")
        # Etiqueta inferior que muestra el estado, alineada a la izquierda
        ttk.Label(self.root, textvariable=self.status, anchor="w").pack(fill="x", padx=12, pady=(0, 8))

    def _bind_shortcuts(self):
        # Atajo de teclado a nivel de ventana:
        # - Tecla Supr (Delete) ejecuta delete_selected para borrar filas seleccionadas
        self.root.bind("<Delete>", lambda e: self.delete_selected())

    def add_item(self):
        # Obtiene el texto del Entry desde la variable y elimina espacios al inicio/fin
        text = (self.var_item.get() or "").strip()

        # Validación: si está vacío, muestra un mensaje y no agrega nada
        if not text:
            messagebox.showinfo("Info", "Escribe un ítem.")
            return  # Sale del método sin cambios

        # Agrega un nuevo diccionario al modelo con el texto y el estado "no hecho"
        self.items.append({"text": text, "done": False})

        # Limpia el Entry para permitir ingresar un nuevo valor fácilmente
        self.var_item.set("")

        # Redibuja la tabla para reflejar el nuevo ítem y actualiza el contador
        self.render()
        self.update_status()

    def delete_selected(self):
        # Obtiene los identificadores (IDs) de las filas seleccionadas en el Treeview
        sel = self.tree.selection()

        # Si no hay nada seleccionado, informa al usuario y sale
        if not sel:
            messagebox.showinfo("Info", "Selecciona filas para eliminar.")
            return

        # Convierte cada selección en su índice/posición dentro del Treeview
        indices = [self.tree.index(i) for i in sel]

        # Elimina del modelo desde el índice más grande al más chico
        # (evita desfasajes por corrimiento de posiciones al borrar)
        for idx in sorted(indices, reverse=True):
            self.items.pop(idx)

        # Refresca la tabla y el estado después de eliminar
        self.render()
        self.update_status()

        # (Opcional) ejemplo de cómo mover la selección al final si quedó algo
        # if self.tree.get_children():
        #     last = self.tree.get_children()[-1]
        #     self.tree.selection_set(last)

    def clear_list(self):
        # Si la lista ya está vacía, no hace nada
        if not self.items:
            return

        # Pide confirmación al usuario antes de borrar todo el contenido
        if messagebox.askyesno("Limpiar", "¿Seguro que quieres limpiar toda la lista?"):
            # Vacía la lista de ítems del modelo
            self.items.clear()
            # Redibuja la tabla ahora vacía y actualiza el contador
            self.render()
            self.update_status()

    def render(self):
        # Elimina todas las filas actuales del Treeview antes de volver a insertar
        self.tree.delete(*self.tree.get_children())

        # Inserta cada ítem del modelo como una fila en la tabla
        # - Columna 1: texto del ítem
        # - Columna 2: "✔" si el ítem está hecho; vacío si no lo está
        for it in self.items:
            self.tree.insert("", "end", values=(it["text"], "✔" if it["done"] else ""))

    def update_status(self):
        # Calcula cuántos ítems hay en total
        total = len(self.items)
        # Cuenta cuántos ítems están marcados como hechos
        done = sum(1 for i in self.items if i["done"])
        # Actualiza el StringVar para que la etiqueta inferior muestre el resumen
        self.status.set(f"{total} ítems · {done} hechos")


def main():
    # Punto de entrada de la aplicación:
    # 1) Crea la ventana principal de Tkinter
    root = tk.Tk()
    # 2) Construye la UI y lógica de la app sobre esa ventana
    App(root)
    # 3) Inicia el bucle principal de eventos (la app queda a la espera de interacción)
    root.mainloop()


if __name__ == "__main__":
    # Si este archivo se ejecuta directamente (no importado como módulo), lanza main()
    main()
# =======
# "Prueba de git"
#  main
# =======
# >>>>>>> main
