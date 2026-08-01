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

            ),

            # -------------------------
            # USUARIO + CERRAR SESIÓN (derecha)
            # -------------------------

            html.Div(

                className="header-usuario",

                children=[

                    html.Span(
                        id="header-nombre-usuario",
                        className="header-nombre",
                    ),

                    html.Button(

                        [
                            html.I(className="fas fa-right-from-bracket",
                                   style={"marginRight": "8px"}),
                            "Cerrar sesión",
                        ],

                        id="btn-cerrar-sesion",

                        n_clicks=0,

                        className="btn-cerrar-sesion",

                        style={
                            "backgroundColor": "rgba(255,255,255,0.12)",
                            "color": "#FFFFFF",
                            "border": "1px solid rgba(255,255,255,0.35)",
                            "padding": "8px 16px",
                            "borderRadius": "8px",
                            "fontWeight": "600",
                            "fontSize": "14px",
                            "cursor": "pointer",
                        },
                    ),

                ],

                style={
                    "marginLeft": "auto",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "16px",
                    "paddingRight": "24px",
                },

            ),

        ]

    )