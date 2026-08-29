"""
=========================================================
MÓDULO INGRESOS
=========================================================
Solo VISUALIZACIÓN. La carga se hace en /cargar (solo admin).
Los datos se leen de la caché del servidor (módulo "ingresos").
"""

from dash import html, dcc

from ingresos.controles import crear_controles_ingresos
from ingresos.tabla_ingresos import crear_layout_tabla_ingresos
from componentes.boton_descarga import boton_descargar_reporte


def crear_layout_ingresos():

    return html.Div(
        children=[

            # ==========================================
            # STORES (propios de ingresos)
            # ==========================================
            dcc.Store(id="store-bd-ingresos"),
            dcc.Store(id="store-mes-ingresos", data=[]),
            dcc.Store(id="store-semana-ingresos", data=[]),

            # ==========================================
            # TÍTULO + botón de descarga
            # ==========================================
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("Ingresos", className="titulo"),
                            html.P("Reporte de ingresos por vendedor.",
                                   className="subtitulo"),
                        ]
                    ),
                    boton_descargar_reporte("ingresos"),
                ],
                style={"display": "flex", "justifyContent": "space-between",
                       "alignItems": "flex-start", "flexWrap": "wrap", "gap": "12px"},
            ),

            html.Br(),

            # ==========================================
            # CALENDARIO Mes / Semana (+ Año)
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