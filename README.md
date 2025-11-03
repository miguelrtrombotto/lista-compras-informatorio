# lista-compras-informatorio
Lista de Compra Avanzada con Tkinter para Informatorio



División del trabajo para 3 personas
Un único punto de entrada: src/main.py.
Se trabaja por Issues → ramas feature → PR → merge a main.

Persona A — UI base y operaciones de ítems
Issue 1: Ventana base (Tk root, tamaño, frame principal, rótulo inicial)
Issue 2: Agregar ítems (Entry + botón + Enter) + Treeview (“Ítem”, “Hecho”)
Issue 3: Eliminar seleccionados y Limpiar lista (botones + tecla Delete)
Persona B — Interacciones y estado avanzado
Issue 5: Marcar como hecho con doble clic (toggle_done)
Issue 6: Barra de estado robusta (“N ítems · M hechos”)
Issue 7: Validaciones y atajos extra (duplicados, feedback consistente)
Persona C — Persistencia, documentación y release
Issue 4: Guardar/Abrir JSON + atajos Ctrl+S / Ctrl+O
Issue 8: README (requisitos, cómo ejecutar, atajos, contribución)
Issue 9: Release v0.1.0 (tag y notas)
Orden recomendado de integración: A → B → C.
Si B o C necesitan empezar antes, pueden basar sus ramas en la última rama de A y luego rebasear contra main cuando A haga merge.