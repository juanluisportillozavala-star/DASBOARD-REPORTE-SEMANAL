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
                            html.Img(src="/assets/logo.png", className="logo-img")
                        ],
                    ),

                    html.Div(
                        children=[
                            html.H1("Sistema Gerencial Liderza",
                                    className="logo-titulo"),
                            html.P("Dashboard Corporativo",
                                   className="logo-subtitulo"),
                        ]
                    ),

                ],

            ),

            # -------------------------
            # USUARIO + CERRAR SESIÓN (derecha)
            # -------------------------

            html.Div(

                className="header-usuario",

                children=[

                    # bloque del usuario: ícono en círculo dorado + nombre
                    html.Div(
                        className="usuario-chip",
                        children=[
                            html.Div(
                                html.I(className="fas fa-user"),
                                className="usuario-avatar",
                            ),
                            html.Span(id="header-nombre-usuario",
                                      className="usuario-nombre"),
                        ],
                    ),

                    # botón cerrar sesión (borde dorado, se rellena en hover)
                    html.Button(
                        [
                            html.I(className="fas fa-right-from-bracket",
                                   style={"marginRight": "8px"}),
                            "Cerrar sesión",
                        ],
                        id="btn-cerrar-sesion",
                        n_clicks=0,
                        className="btn-cerrar-sesion",
                    ),

                ],

            ),

        ]

    )