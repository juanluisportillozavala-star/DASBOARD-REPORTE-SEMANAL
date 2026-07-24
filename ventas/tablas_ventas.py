"""
=========================================================
ventas/tablas_ventas.py
=========================================================
CATÁLOGO de las tablas jerárquicas de Ventas.

Aquí se declara CADA tabla en pocas líneas, usando la
fábrica (ventas/tabla_arbol.py). Añadir una tabla nueva =
añadir una entrada a TABLAS. Nada más.

  clave:   identificador corto y único (sin espacios)
  niveles: dimensiones de la jerarquía, de fuera hacia dentro
  titulo:  encabezado visible (opcional; por defecto los
           niveles unidos por ' / ')
"""

from dash import html

from ventas.tabla_arbol import crear_layout_tabla, registrar_callbacks_tablas


# -------------------------------------------------------
# Definición de las tablas. Por ahora, solo Producto/Cliente
# (validamos la fábrica conectada). Para agregar las otras,
# se descomenta / añade su línea aquí — nada más.
# -------------------------------------------------------

TABLAS = [
    {"clave": "prod_cli", "niveles": ["Producto", "Cliente"]},
    # {"clave": "cli_prod", "niveles": ["Cliente", "Producto"]},
    # {"clave": "vend_prod", "niveles": ["Vendedor", "Producto"]},
]


def crear_layout_tablas_ventas():
    """Apila los layouts de todas las tablas del catálogo."""
    bloques = []
    for t in TABLAS:
        bloques.append(crear_layout_tabla(
            t["clave"], t["niveles"], t.get("titulo"),
        ))
        bloques.append(html.Br())
    return html.Div(bloques)


def registrar_callbacks_tablas_ventas(app):
    """Registra los callbacks de la fábrica (una sola vez sirve
    a todas las tablas del catálogo, vía pattern-matching)."""
    registrar_callbacks_tablas(app)