"""
=========================================================
MÓDULO INGRESOS
=========================================================
Solo VISUALIZACIÓN. La carga se hace en /cargar (solo admin).
Los datos se leen de la caché del servidor (módulo "ingresos").

Estructura (patrón similar a Ventas):
  - Stores propios (marca ligera + filtro mes/semana)
  - Título
  - Calendario Mes/Semana (controles propios de ingresos)
  - Tabla dinámica (pivote Vendedor x Contado/Crédito x Vencido/Vigente)
"""

from dash import html, dcc

from ingresos.controles import crear_controles_ingresos
from ingresos.tabla_ingresos import crear_layout_tabla_ingresos


def crear_layout_ingresos():

    return html.Div(
        children=[

            # ==========================================
            # STORES (propios de ingresos)
            # store-bd-ingresos: marca ligera {cargado, version}
            # ==========================================
            dcc.Store(id="store-bd-ingresos"),
            dcc.Store(id="store-mes-ingresos", data=[]),
            dcc.Store(id="store-semana-ingresos", data=[]),

            # ==========================================
            # TÍTULO
            # ==========================================
            html.H1("Ingresos", className="titulo"),

            html.P("Reporte de ingresos por vendedor.",
                   className="subtitulo"),

            html.Br(),

            # ==========================================
            # CALENDARIO Mes / Semana
            # ==========================================
            crear_controles_ingresos(),

            html.Br(),

            # ==========================================
            # TABLA DINÁMICA (pivote)
            # ==========================================
            crear_layout_tabla_ingresos(),

            html.Br(),
        ]
    )