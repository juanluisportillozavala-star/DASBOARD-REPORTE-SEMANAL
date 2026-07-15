"""
=========================================================
MÓDULO VENTAS
=========================================================
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

from ventas.controles import crear_controles


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
            # ESTADO
            # ==========================================

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

            )

        ]

    )