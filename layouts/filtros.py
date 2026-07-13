"""
=========================================================
FILTROS
=========================================================
"""

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def crear_filtros():

    return dbc.Card(

        dbc.CardBody(

            [

                dbc.Row(

                    [

                        dbc.Col(

                            [

                                html.Label("Año"),

                                dcc.Dropdown(

                                    id="filtro-año",

                                    placeholder="Seleccionar"

                                )

                            ]

                        ),

                        dbc.Col(

                            [

                                html.Label("Mes"),

                                dcc.Dropdown(

                                    id="filtro-mes",

                                    placeholder="Seleccionar"

                                )

                            ]

                        ),

                        dbc.Col(

                            [

                                html.Label("Semana"),

                                dcc.Dropdown(

                                    id="filtro-semana",

                                    placeholder="Seleccionar"

                                )

                            ]

                        )

                    ]

                )

            ]

        )

    )