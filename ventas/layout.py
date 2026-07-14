"""
============================================================
LAYOUT DEL MÓDULO DE VENTAS
============================================================
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def crear_layout():

    return dbc.Container(

        [

            html.Br(),

            html.H2(
                "SISTEMA GERENCIAL LIDERZA",
                className="titulo-principal"
            ),

            html.H5(
                "Dashboard Comercial",
                className="subtitulo"
            ),

            html.Hr(),

            dbc.Row(

                [

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H5("Catálogo"),

                                    dcc.Upload(

                                        id="upload-catalogo",

                                        children=dbc.Button(

                                            "Seleccionar Catálogo",

                                            color="primary",

                                            className="w-100"

                                        ),

                                        multiple=False

                                    )

                                ]

                            )

                        ),

                        md=6

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H5("Base de Datos"),

                                    dcc.Upload(

                                        id="upload-bd",

                                        children=dbc.Button(

                                            "Seleccionar BD Ventas",

                                            color="success",

                                            className="w-100"

                                        ),

                                        multiple=False

                                    )

                                ]

                            )

                        ),

                        md=6

                    )

                ]

            ),

            html.Br(),

            dbc.Alert(

                "Esperando archivos...",

                id="mensaje",

                color="secondary"

            ),

            html.Br(),

            dbc.Row(

                [

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H4("$0"),

                                    html.P("Venta Total")

                                ]

                            )

                        )

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H4("$0"),

                                    html.P("Utilidad")

                                ]

                            )

                        )

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H4("0"),

                                    html.P("Clientes")

                                ]

                            )

                        )

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H4("0"),

                                    html.P("Productos")

                                ]

                            )

                        )

                    )

                ]

            ),

            html.Br(),

            dbc.Card(

                dbc.CardBody(

                    [

                        html.H4("Gráficas"),

                        html.P(

                            "Aquí aparecerán las gráficas del Dashboard."

                        )

                    ]

                )

            ),

            html.Br(),

            dbc.Card(

                dbc.CardBody(

                    [

                        html.H4("Tabla de Ventas"),

                        html.P(

                            "Aquí aparecerá la tabla dinámica."

                        )

                    ]

                )

            ),

            html.Br()

        ],

        fluid=True

    )