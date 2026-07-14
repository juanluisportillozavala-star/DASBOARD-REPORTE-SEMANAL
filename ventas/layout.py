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

            # =====================================
            # TARJETAS DE CARGA
            # =====================================

            dbc.Row(

                [

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H4(
                                        "Catálogo",
                                        className="mb-3"
                                    ),

                                    dcc.Upload(

                                        id="upload-catalogo",

                                        children=html.Div(

                                            [

                                                "Arrastra el archivo aquí o ",

                                                html.A("Selecciona un archivo")

                                            ]

                                        ),

                                        className="upload-box",

                                        multiple=False

                                    ),

                                    html.Br(),

                                    html.Div(

                                        id="nombre-catalogo",

                                        children="Ningún archivo seleccionado.",

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
                                        "BD Ventas",
                                        className="mb-3"
                                    ),

                                    dcc.Upload(

                                        id="upload-ventas",

                                        children=html.Div(

                                            [

                                                "Arrastra el archivo aquí o ",

                                                html.A("Selecciona un archivo")

                                            ]

                                        ),

                                        className="upload-box",

                                        multiple=False

                                    ),

                                    html.Br(),

                                    html.Div(

                                        id="nombre-ventas",

                                        children="Ningún archivo seleccionado.",

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

                "Procesar",

                id="btn-procesar",

                color="primary",

                size="lg"

            ),

            html.Hr(),

            html.H3(

                "Vista previa",

                style={

                    "color":"#173C73"

                }

            ),

            html.Div(

                id="vista-previa"

            )

        ]

    )