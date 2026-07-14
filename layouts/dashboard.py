"""
=========================================================
dashboard.py
=========================================================
Pantalla principal del Sistema Gerencial Liderza.
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_dashboard():

    return html.Div(

        className="contenido",

        children=[

            html.H2(
                "Dashboard",
                className="titulo"
            ),

            html.P(
                "Bienvenido al Sistema Gerencial Liderza",
                className="subtitulo"
            ),

            html.Br(),

            dbc.Row(

                [

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Ventas"),

                                    html.H2("$0.00")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Ingresos"),

                                    html.H2("$0.00")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Inventario"),

                                    html.H2("$0.00")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Cartera"),

                                    html.H2("$0.00")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    )

                ]

            ),

            html.Br(),

            dbc.Card(

                dbc.CardBody(

                    [

                        html.H4("Resumen"),

                        html.Hr(),

                        html.P(

                            """
                            Desde este sistema podrás administrar:

                            • Ventas

                            • Ingresos

                            • Inventario

                            • Cartera

                            • Saldo Proveedor

                            • Reportes

                            """

                        )

                    ]

                )

            )

        ]

    )