"""
=========================================================
KPIs
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_kpis():

    return dbc.Row(

        [

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        [

                            html.H6("VENTAS"),

                            html.H3("$0")

                        ]

                    )

                )

            ),

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        [

                            html.H6("CLIENTES"),

                            html.H3("0")

                        ]

                    )

                )

            ),

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        [

                            html.H6("PRODUCTOS"),

                            html.H3("0")

                        ]

                    )

                )

            ),

            dbc.Col(

                dbc.Card(

                    dbc.CardBody(

                        [

                            html.H6("UTILIDAD"),

                            html.H3("$0")

                        ]

                    )

                )

            )

        ],

        className="mb-4"

    )