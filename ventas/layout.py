"""
=========================================================
MÓDULO VENTAS
=========================================================
Solo VISUALIZACIÓN. La carga de archivos se hace en la
pantalla de Carga de datos (carga.py, solo admin). Aquí los
datos se leen de Supabase (callback cargar_desde_bd).
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from ventas.controles import crear_controles
from ventas.tablas_ventas import crear_layout_tablas_ventas
from ventas.graficos import crear_layout_graficos


def crear_layout_ventas():

    return html.Div(

        children=[

            # ==========================================
            # STORES  (se mantienen: reciben los datos que
            # cargar_desde_bd lee de Supabase)
            # ==========================================

            dcc.Store(id="store-bd-ventas"),

            dcc.Store(id="store-kpis"),

            dcc.Store(id="store-anio", data=None),

            dcc.Store(id="store-mes", data=[]),

            dcc.Store(id="store-semana", data=[]),

            dcc.Store(id="store-arbol-expandido", data=[]),

            dcc.Store(id="store-arbol-completo", data=None),

            dcc.Store(id="store-arbol-total", data=None),

            # ==========================================
            # TITULO
            # ==========================================

            html.H1(

                "Ventas",

                className="titulo"

            ),

            html.P(

                "Reporte semanal de ventas.",

                className="subtitulo"

            ),

            html.Br(),

            # ==========================================
            # KPIs
            # ==========================================

            html.Div(

                id="contenedor-kpis"

            ),

            html.Br(),

            # ==========================================
            # CONTROLES  (año + calendario mes / semana)
            # ==========================================

            crear_controles(),

            html.Br(),

            # ==========================================
            # TABLAS DINÁMICAS (fábrica)
            # ==========================================

            html.Br(),

            crear_layout_tablas_ventas(),

            html.Br(),

            # ==========================================
            # GRAFICAS (dentro del accordion)
            # ==========================================

            dbc.Accordion(

                [

                    dbc.AccordionItem(

                        [

                            crear_layout_graficos()

                        ],

                        title="Ver análisis gráfico"

                    )

                ],

                id="acc-graficos",

                start_collapsed=True

            ),

            html.Br()

        ]

    )