"""
=========================================================
MÓDULO VENTAS
=========================================================
Layout principal del módulo de Ventas
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def crear_layout_ventas():

    return html.Div(

        children=[

            # =====================================
            # TÍTULOS
            # =====================================

            html.H1(
                "Ventas",
                className="titulo"
            ),

            html.P(
                "Carga y procesamiento del reporte de ventas.",
                className="subtitulo"
            ),

            html.Br(),

            # =====================================
            # TARJETAS
            # =====================================

            dbc.Row(

                [

                    # =====================================
                    # CATÁLOGO
                    # =====================================

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

                                        children=[

                                            html.I(
                                                className="fas fa-file-excel me-2"
                                            ),

                                            " Ningún archivo seleccionado."

                                        ],

                                        className="archivo-seleccionado"

                                    )

                                ]

                            ),

                            className="card-premium"

                        ),

                        md=6

                    ),

                    # =====================================
                    # BD VENTAS
                    # =====================================

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

                                        children=[

                                            html.I(
                                                className="fas fa-file-excel me-2"
                                            ),

                                            " Ningún archivo seleccionado."

                                        ],

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

            html.Hr(),

            html.Div(

                id="vista-previa"

            )

        ]

    )