"""
=========================================================
MÓDULO INVENTARIO
=========================================================
Solo VISUALIZACIÓN. La carga se hace en /cargar (solo admin).
Los datos se leen de la caché del servidor (módulo "inventario").

Contiene: KPIs, filtro por ubicación, gráficos (pastel + barras)
y tabla plana de productos con diseño premium.
"""

from dash import html, dcc

from inventario.tabla_inventario import crear_layout_tabla_inventario


def crear_layout_inventario():
    return html.Div(
        children=[
            # store marca ligera (mismo patrón de caché que los demás)
            dcc.Store(id="store-bd-inventario"),

            html.H1("Inventario", className="titulo"),
            html.P("Dashboard de inventarios — lento movimiento.",
                   className="subtitulo"),
            html.Br(),

            crear_layout_tabla_inventario(),

            html.Br(),
        ]
    )