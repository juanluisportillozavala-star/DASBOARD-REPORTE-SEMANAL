"""
=========================================================
CONTROLES DEL DASHBOARD DE VENTAS
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_controles():

    meses = [

        html.Div(

            str(i),

            id=f"mes-{i}",

            className="cuadro-mes"

        )

        for i in range(1,13)

    ]

    return dbc.Card(

        dbc.CardBody(

            [

                html.H5(

                    "Filtros",

                    style={

                        "color":"#173C73",

                        "fontWeight":"bold"

                    }

                ),

                html.Hr(),

                dbc.Row(

                    [

                        dbc.Col(

                            [

                                html.Label(

                                    "Mes",

                                    className="fw-bold mb-2"

                                ),

                                html.Div(

                                    meses[:6],

                                    className="selector-meses"

                                ),

                                html.Br(),

                                html.Div(

                                    meses[6:],

                                    className="selector-meses"

                                )

                            ],

                            md=5

                        ),

                        dbc.Col(

                            [

                                html.Label(

                                    "Semana",

                                    className="fw-bold mb-2"

                                ),

                                html.Div(

                                    id="selector-semanas",

                                    className="selector-semanas"

                                )

                            ],

                            md=7

                        )

                    ]

                )

            ]

        ),

        className="card-premium"

    )