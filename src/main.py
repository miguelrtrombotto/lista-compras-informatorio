#  feature/estructura-inicial
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import subprocess
import sys
import importlib.util


class App:
    
    def __init__(self, root: tk.Tk):
        
        self.root = root
        self.root.title("Lista de compras")
        self.root.geometry("700x520")

        self.items = []

        self._build_ui()
        self._bind_shortcuts()
        self.render()
        self.update_status()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        # ---------------------
        # Sección: Formulario (input + botón Agregar)
        # ---------------------
        form = ttk.Frame(main)
        form.pack(fill="x")

        ttk.Label(form, text="Ítem:").grid(row=0, column=0, padx=(0, 6))
        self.var_item = tk.StringVar()

        entry = ttk.Entry(form, textvariable=self.var_item)
        entry.grid(row=0, column=1, sticky="ew")
        form.columnconfigure(1, weight=1)

        ttk.Button(form, text="Agregar", command=self.add_item).grid(row=0, column=2, padx=(8, 0))

        entry.bind("<Return>", lambda e: self.add_item())

        # ---------------------
        # Sección: Barra de acciones
        # ---------------------
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(6, 0))

        ttk.Button(actions, text="Eliminar seleccionado(s)", command=self.delete_selected).pack(side="left")

        ttk.Button(actions, text="Limpiar lista", command=self.clear_list).pack(side="left", padx=6)

        # Botones para guardar y abrir
        ttk.Button(actions, text="Guardar (Ctrl+S)", command=self.guardar_lista).pack(side="left", padx=6)

        ttk.Button(actions, text="Abrir (Ctrl+O)", command=self.abrir_lista).pack(side="left", padx=6)

        # ---------------------
        # Sección: Tabla (Treeview) con scroll
        # ---------------------
        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True, pady=8)
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("item", "hecho"),
            show="headings",
            height=14
        )
        self.tree.heading("item", text="Ítem")
        self.tree.heading("hecho", text="Hecho")
        self.tree.column("item", width=520, anchor="w")
        self.tree.column("hecho", width=80, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)

        # ---------------------
        # Sección: Barra de estado (contador)
        # ---------------------
        self.status = tk.StringVar(value="0 ítems · 0 hechos")
        ttk.Label(self.root, textvariable=self.status, anchor="w").pack(fill="x", padx=12, pady=(0, 8))
        
        # ---------------------
        # Sección: Barra de progreso (porcentaje completado)
        # ---------------------
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=12, pady=(0, 4))


    def _bind_shortcuts(self):
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<Control-s>", lambda e: self.guardar_lista())
        self.root.bind("<Control-o>", lambda e: self.abrir_lista())
        self.tree.bind("<Double-1>", self.toggle_done)


    def add_item(self):
        text = (self.var_item.get() or "").strip()

        if not text:
            messagebox.showinfo("Info", "Escribe un ítem.")
            return

        if any(i["text"].lower() == text.lower() for i in self.items):
            continuar = messagebox.askyesno("Duplicado", f"El item \"{text}\" ya esta en la lista.\nDesea agregarlo igualmente?")
            if not continuar:
                self.var_item.set("")
                return
        
        self.items.append({"text": text, "done": False})

        self.var_item.set("")

        self.render()

        self.update_status()
    
    def toggle_done(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        index = self.tree.index(item_id)

        self.items[index]["done"] = not self.items[index]["done"]

        self.render()
        self.update_status()

    def delete_selected(self):
        sel = self.tree.selection()

        if not sel:
            messagebox.showinfo("Info", "Selecciona filas para eliminar.")
            return

        indices = [self.tree.index(i) for i in sel]

        for idx in sorted(indices, reverse=True):
            self.items.pop(idx)

        self.render()
        self.update_status()

    def clear_list(self):
        if not self.items:
            return

        if messagebox.askyesno("Limpiar", "¿Seguro que quieres limpiar toda la lista?"):
            self.items.clear()
            self.render()
            self.update_status()

    def guardar_lista(self):
        """
        Guarda la lista actual en un archivo JSON
        """
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if archivo:
            try:
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.items, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Éxito", f"Lista guardada en:\n{archivo}")
                print(f"Lista guardada en: {archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
                print(f"Error al guardar: {e}")


    def abrir_lista(self):
        """
        Abre una lista desde un archivo JSON
        """
        archivo = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    items_cargados = json.load(f)
                
                # Validar que sea una lista válida
                if not isinstance(items_cargados, list):
                    raise ValueError("El archivo no contiene una lista válida")
                
                # Limpiar la lista actual
                self.items.clear()
                
                # Agregar los ítems del archivo
                for item in items_cargados:
                    if isinstance(item, dict) and "text" in item and "done" in item:
                        self.items.append(item)
                
                self.render()
                self.update_status()
                messagebox.showinfo("Éxito", f"Lista abierta desde:\n{archivo}")
                print(f"Lista abierta desde: {archivo}")
            
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir:\n{e}")
                print(f"Error al abrir archivo: {e}")

    def render(self):
        self.tree.delete(*self.tree.get_children())

        for it in self.items:
            self.tree.insert("", "end", values=(it["text"], "✔" if it["done"] else ""))

    def update_status(self):
        total = len(self.items)
        done = sum(1 for i in self.items if i["done"])
        percent = (done / total * 100) if total else 0 
        self.status.set(f"{total} ítems · {done} hechos · {percent:.0f}% completado")
        
        self.progress["value"] = percent
        

def main():
    
    def instalar_si_falta(paquete):
        
        if importlib.util.find_spec(paquete) is None:
            elec = input("Desea instalar el tema Breeze-dark de la biblioteca ttkthemes? S/N: ").strip().lower()
            if elec == "s":
                print(f"Instalando {paquete}... Esto puede tardar unos minutos")
                subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
                return True
        else:
            print(f"{paquete} ya está instalado.")
            return False
            
    usar_ttkthemes = instalar_si_falta("ttkthemes")
    
    import os
    if usar_ttkthemes:
        try:
            from ttkthemes import ThemedTk
            root = ThemedTk()
            theme = True
        except Exception:
            root = tk.Tk()
            theme = False            
    else:
        
        root = tk.Tk()
        theme = False
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    theme_tcl = os.path.join(base_dir, "breeze-dark", "breeze-dark.tcl")    
    
    try:
        root.tk.call("source", theme_tcl)
        if hasattr(root, "set_theme"):
            root.set_theme("breeze-dark")
    except Exception as err:
        print(f"Advertencia: no se pudo cargar el tema: {err}")
        
    App(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()