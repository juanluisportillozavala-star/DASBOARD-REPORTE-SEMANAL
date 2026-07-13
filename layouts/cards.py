"""
=========================================================
CARDS
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def tarjeta(titulo, valor):

    return dbc.Card(

        dbc.CardBody(

            [

                html.H5(

                    titulo,

                    className="card-title"

                ),

                html.H2(

                    valor,

                    style={

                        "color":"#0B2D5B",

                        "fontWeight":"bold"

                    }

                )

            ]

        ),

        className="card"

    )