"""
=========================================================
FOOTER
=========================================================
"""

from dash import html


def crear_footer():

    return html.Div(

        [

            html.Hr(),

            html.Center(

                "Sistema Gerencial Liderza | Versión 1.0"

            )

        ],

        style={

            "padding":"20px",

            "color":"gray"

        }

    )