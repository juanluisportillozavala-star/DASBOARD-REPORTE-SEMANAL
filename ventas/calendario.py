"""
=========================================================
CALENDARIO COMERCIAL
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


DIAS = [

    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado"

]


def celda(dia, venta=""):

    return dbc.Col(

        html.Div(

            [

                html.Div(

                    str(dia),

                    className="numero-dia"

                ),

                html.Div(

                    venta,

                    className="venta-dia"

                )

            ],

            className="celda-calendario"

        )

    )


def crear_semana(numero, dias):

    return html.Div(

        [

            html.Div(

                f"SEM {numero}",

                className="titulo-semana"

            ),

            dbc.Row(

                [

                    celda(dia)

                    for dia in dias

                ],

                className="g-2"

            ),

            html.Br()

        ]

    )


def crear_calendario():

    return html.Div(

        [

            html.H4(

                "JULIO 2026",

                style={

                    "textAlign": "center",

                    "fontWeight": "bold",

                    "color": "#173C73",

                    "marginBottom": "25px"

                }

            ),

            dbc.Row(

                [

                    dbc.Col(

                        html.Div(

                            dia,

                            className="encabezado-dia"

                        )

                    )

                    for dia in DIAS

                ],

                className="mb-3"

            ),

            crear_semana(

                27,

                [30,1,2,3,4,5]

            ),

            crear_semana(

                28,

                [7,8,9,10,11,12]

            ),

            crear_semana(

                29,

                [14,15,16,17,18,19]

            ),

            crear_semana(

                30,

                [21,22,23,24,25,26]

            ),

            crear_semana(

                31,

                [28,29,30,31,"",""]

            )

        ]

    )