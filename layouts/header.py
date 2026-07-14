"""
HEADER
Sistema Gerencial Liderza
"""

from dash import html


def crear_header():

    return html.Div(

        className="header",

        children=[

            # -------------------------
            # LOGO
            # -------------------------

            html.Div(

                className="header-logo",

                children=[

                    html.Div(

                        className="logo-box",

                        children=[

                            html.Img(
                                src="/assets/logo.png",
                                className="logo-img"
                            )

                        ]

                    ),

                    html.Div(

                        children=[

                            html.H1(
                                "Sistema Gerencial Liderza",
                                className="logo-titulo"
                            ),

                            html.P(
                                "Dashboard Corporativo",
                                className="logo-subtitulo"
                            )

                        ]

                    )

                ]

            )

        ]

    )