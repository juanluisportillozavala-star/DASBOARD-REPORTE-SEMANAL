"""
=========================================================
MÓDULO VENTAS
=========================================================
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from ventas.controles import crear_controles
from ventas.tablas_ventas import crear_layout_tablas_ventas


def crear_layout_ventas():

    return html.Div(

        children=[

            # ==========================================
            # STORES
            # ==========================================

            dcc.Store(

                id="store-bd-ventas"

            ),

            dcc.Store(

                id="store-kpis"

            ),

            dcc.Store(

                id="store-mes",
                data=[]

            ),

            dcc.Store(

                id="store-semana",
                data=[]

            ),

            dcc.Store(

                id="store-arbol-expandido",
                data=[]

            ),

            dcc.Store(

                id="store-arbol-completo",
                data=None

            ),

            dcc.Store(

                id="store-arbol-total",
                data=None

            ),

            # ==========================================
            # TITULO
            # ==========================================

            html.H1(

                "Ventas",

                className="titulo"

            ),

            html.P(

                "Carga y procesamiento del reporte semanal de ventas.",

                className="subtitulo"

            ),

            html.Br(),

            # ==========================================
            # ARCHIVOS
            # ==========================================

            dbc.Row(

                [

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H4(

                                        "📁 Catálogo",

                                        className="mb-3"

                                    ),

                                    dcc.Upload(

                                        id="upload-catalogo",

                                        multiple=False,

                                        children=dbc.Button(

                                            [

                                                html.I(

                                                    className="fas fa-folder-open me-2"

                                                ),

                                                "Seleccionar Catálogo"

                                            ],

                                            color="primary",

                                            className="w-100"

                                        )

                                    ),

                                    html.Br(),

                                    html.Div(

                                        id="nombre-catalogo",

                                        className="archivo-seleccionado"

                                    )

                                ]

                            ),

                            className="card-premium"

                        ),

                        md=6

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H4(

                                        "📊 BD Ventas",

                                        className="mb-3"

                                    ),

                                    dcc.Upload(

                                        id="upload-ventas",

                                        multiple=False,

                                        children=dbc.Button(

                                            [

                                                html.I(

                                                    className="fas fa-folder-open me-2"

                                                ),

                                                "Seleccionar BD Ventas"

                                            ],

                                            color="primary",

                                            className="w-100"

                                        )

                                    ),

                                    html.Br(),

                                    html.Div(

                                        id="nombre-ventas",

                                        className="archivo-seleccionado"

                                    )

                                ]

                            ),

                            className="card-premium"

                        ),

                        md=6

                    )

                ]

            ),

            html.Br(),

            dbc.Button(

                [

                    html.I(

                        className="fas fa-gears me-2"

                    ),

                    "Procesar Información"

                ],

                id="btn-procesar",

                color="primary",

                size="lg",

                className="px-5"

            ),

            html.Br(),

            html.Br(),

            # ==========================================
            # KPIs
            # ==========================================

            html.Div(

                id="contenedor-kpis"

            ),

            html.Br(),

            # ==========================================
            # CONTROLES
            # ==========================================

            crear_controles(),

            html.Br(),


            # ==========================================
            # TABLAS
            # ==========================================

            html.Div(

                id="contenedor-tablas"

            ),

            # ==========================================
            # TABLA Producto / Cliente (nueva)
            # ==========================================

            html.Br(),

            crear_layout_tablas_ventas(),

            # Debug: muestra resumen corto del store de ventas
            html.Div(
                id="debug-store-bd-ventas",
                style={"whiteSpace": "pre-wrap", "fontSize": "14px", "color": "#173C73"}
            ),

            html.Br(),

            # ==========================================
            # GRAFICAS
            # ==========================================

            dbc.Accordion(

                [

                    dbc.AccordionItem(

                        [

                            html.Div(

                                id="contenedor-graficas"

                            )

                        ],

                        title="Ver análisis gráfico"

                    )

                ],

                start_collapsed=True

            ),

            html.Br(),

            # ==========================================
            # ESTADO (oculto)
            #
            # La tarjeta ya no se muestra en pantalla, pero el
            # div "estado-proceso" SIGUE existiendo: el callback
            # procesar_archivos escribe aquí, así que si algo
            # falla el mensaje se genera (aunque no se vea). Esto
            # evita un fallo silencioso y deja el callback intacto
            # (no hay que quitarle el Output "estado-proceso").
            # Para reactivarlo en el futuro: quitar el display none.
            # ==========================================

            html.Div(

                dbc.Card(

                    dbc.CardBody(

                        [

                            html.H4(

                                [

                                    html.I(

                                        className="fas fa-circle-info me-2"

                                    ),

                                    "Estado del procesamiento"

                                ]

                            ),

                            html.Hr(),

                            html.Div(

                                id="estado-proceso"

                            )

                        ]

                    ),

                    className="card-premium"

                ),

                style={"display": "none"}

            )

        ]

    )