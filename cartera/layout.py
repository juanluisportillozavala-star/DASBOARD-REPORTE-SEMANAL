"""
=========================================================
MÓDULO CARTERA
=========================================================
Solo VISUALIZACIÓN. La carga (con fecha de corte) se hace en
/cargar (solo admin). Los datos se leen de la caché del
servidor (módulo "cartera").

Estructura: stores + título + calendario Mes/Semana + tabla
de aging expandible (Vendedor -> Cliente).
"""

from dash import html, dcc

from cartera.controles import crear_controles_cartera
from cartera.tabla_cartera import crear_layout_tabla_cartera


def crear_layout_cartera():
    return html.Div(
        children=[
            dcc.Store(id="store-bd-cartera"),
            dcc.Store(id="store-mes-cartera", data=[]),
            dcc.Store(id="store-semana-cartera", data=[]),

            html.H1("Cartera", className="titulo"),
            html.P("Antigüedad de cartera por vendedor.", className="subtitulo"),
            html.Br(),

            crear_controles_cartera(),
            html.Br(),
            crear_layout_tabla_cartera(),
            html.Br(),
        ]
    )