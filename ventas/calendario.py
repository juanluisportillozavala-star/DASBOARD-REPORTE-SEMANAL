"""
=========================================================
CALENDARIO COMERCIAL
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_selector_semanas(semanas):

    return html.Div(

        [

            html.Div(

                str(semana),

                id=f"semana-{semana}",

                className="cuadro-semana"

            )

            for semana in semanas

        ],

        className="selector-semanas"

    )


def crear_calendario_vacio():

    dias = [

        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado"

    ]

    return dbc.Card(

        dbc.CardBody(

            [

                html.H4(

                    "Calendario Comercial",

                    style={

                        "color":"#173C73",

                        "fontWeight":"bold"

                    }

                ),

                html.Hr(),

                dbc.Row(

                    [

                        dbc.Col(

                            html.Div(

                                dia,

                                style={

                                    "textAlign":"center",

                                    "fontWeight":"bold",

                                    "color":"#173C73",

                                    "fontSize":"17px"

                                }

                            )

                        )

                        for dia in dias

                    ]

                ),

                html.Br(),

                html.Div(

                    id="calendario-comercial"

                )

            ]

        ),

        className="card-premium"

    )