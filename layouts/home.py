"""
=========================================================
HOME
=========================================================
"""

from dash import html

from layouts.header import crear_header


layout = html.Div(

    style={

        "backgroundColor": "#F5F7FA",

        "minHeight": "100vh"

    },

    children=[

        crear_header(),

        html.Div(

            style={

                "padding": "35px"

            },

            children=[

                html.H2(

                    "Bienvenido",

                    style={

                        "color": "#0B2D5B",

                        "fontWeight": "bold"

                    }

                ),

                html.P(

                    "Sistema Gerencial Liderza",

                    style={

                        "fontSize": "20px"

                    }

                )

            ]

        )

    ]

)