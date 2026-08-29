"""
=========================================================
MÓDULO CARTERA
=========================================================
Solo VISUALIZACIÓN. La carga se hace en /cargar (solo admin).
Los datos se leen de la caché del servidor (módulo "cartera").
"""

from dash import html, dcc

from cartera.controles import crear_controles_cartera
from cartera.tabla_cartera import crear_layout_tabla_cartera
from componentes.boton_descarga import boton_descargar_reporte


def crear_layout_cartera():

    return html.Div(
        children=[

            # ==========================================
            # STORES (propios de cartera)
            # ==========================================
            dcc.Store(id="store-bd-cartera"),
            dcc.Store(id="store-mes-cartera", data=[]),
            dcc.Store(id="store-semana-cartera", data=[]),

            # ==========================================
            # TÍTULO + botón de descarga
            # ==========================================
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("Cartera", className="titulo"),
                            html.P("Antigüedad de cartera por vendedor.",
                                   className="subtitulo"),
                        ]
                    ),
                    boton_descargar_reporte("cartera"),
                ],
                style={"display": "flex", "justifyContent": "space-between",
                       "alignItems": "flex-start", "flexWrap": "wrap", "gap": "12px"},
            ),

            html.Br(),

            # ==========================================
            # CALENDARIO Mes / Semana (+ Año)
            # ==========================================
            crear_controles_cartera(),

            html.Br(),

            # ==========================================
            # TABLA DINÁMICA (aging)
            # ==========================================
            crear_layout_tabla_cartera(),

            html.Br(),
        ]
    )