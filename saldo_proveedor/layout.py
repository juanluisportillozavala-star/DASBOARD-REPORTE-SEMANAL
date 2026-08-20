"""
=========================================================
MÓDULO SALDO PROVEEDOR
=========================================================
Solo VISUALIZACIÓN. La carga se hace en /cargar (solo admin).
Los datos se leen de la caché del servidor (módulo
"saldo_proveedor").

Estructura (patrón Ingresos/Cartera):
  - Stores (marca ligera + filtro mes/semana)
  - Título
  - Año + calendario Mes/Semana
  - Matriz por proveedor (aging + total)
"""

from dash import html, dcc

from saldo_proveedor.controles import crear_controles_sp
from saldo_proveedor.tabla_sp import crear_layout_tabla_sp


def crear_layout_saldo_proveedor():
    return html.Div(
        children=[
            dcc.Store(id="store-bd-sp"),
            dcc.Store(id="store-mes-sp", data=[]),
            dcc.Store(id="store-semana-sp", data=[]),

            html.H1("Saldo Proveedor", className="titulo"),
            html.P("Cuentas por pagar por proveedor (aging).",
                   className="subtitulo"),
            html.Br(),

            crear_controles_sp(),
            html.Br(),
            crear_layout_tabla_sp(),
            html.Br(),
        ]
    )