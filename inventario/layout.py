"""
=========================================================
MÓDULO INVENTARIO
=========================================================
Solo VISUALIZACIÓN. La carga se hace en /cargar (solo admin).
Los datos se leen de la caché del servidor (módulo "inventario").

Dos pestañas:
  • Inventario actual  -> la vista de siempre (caché semanal).
  • Histórico mensual  -> fotos guardadas por año/mes.

Ambos paneles quedan SIEMPRE montados en el DOM; la pestaña solo
muestra/oculta (evita que los callbacks queden sin destino y que
la vista salga en blanco al regresar de pestaña).
"""

from dash import html, dcc

from inventario.tabla_inventario import crear_layout_tabla_inventario
from inventario.historico import crear_layout_historico

AZUL = "#173C73"
DORADO = "#D4AF37"

_TAB_STYLE = {"padding": "12px 20px", "fontWeight": "600",
              "color": AZUL, "border": "none",
              "borderBottom": "3px solid transparent",
              "backgroundColor": "transparent"}
_TAB_SEL = {"padding": "12px 20px", "fontWeight": "700",
            "color": AZUL, "border": "none",
            "borderBottom": f"3px solid {DORADO}",
            "backgroundColor": "transparent"}


def crear_layout_inventario():
    return html.Div(
        children=[
            # store marca ligera (mismo patrón de caché que los demás)
            dcc.Store(id="store-bd-inventario"),

            html.H1("Inventario", className="titulo"),
            html.P("Dashboard de inventarios — lento movimiento.",
                   className="subtitulo"),

            # barra de pestañas (solo controla qué panel se ve)
            dcc.Tabs(
                id="inv-tabs", value="actual",
                children=[
                    dcc.Tab(label="Inventario actual", value="actual",
                            style=_TAB_STYLE, selected_style=_TAB_SEL),
                    dcc.Tab(label="Histórico mensual", value="historico",
                            style=_TAB_STYLE, selected_style=_TAB_SEL),
                ],
                style={"marginBottom": "20px"},
            ),

            # PANEL 1: inventario actual (siempre montado)
            html.Div(
                id="inv-panel-actual",
                children=[crear_layout_tabla_inventario()],
                style={"display": "block"},
            ),

            # PANEL 2: histórico (siempre montado, oculto al inicio)
            html.Div(
                id="inv-panel-historico",
                children=[crear_layout_historico()],
                style={"display": "none"},
            ),

            html.Br(),
        ]
    )