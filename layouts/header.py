"""
=========================================================
HEADER
=========================================================
Encabezado principal del Sistema Gerencial Liderza
"""

from dash import html
from config import *


def crear_header():

    return html.Header(

        className="header",

        children=[

            # ============================================
            # LOGO
            # ============================================

            html.Div(

                className="header-logo",

                children=[

                    html.Img(

                        src=f"data:image/png;base64,{LOGO_BASE64}",

                        className="logo-img"

                    ),

                    html.Div(

                        [

                            html.H3(

                                NOMBRE_SISTEMA,

                                className="logo-titulo"

                            ),

                            html.Small(

                                "Dashboard Corporativo",

                                className="logo-subtitulo"

                            )

                        ]

                    )

                ]

            ),

            # ============================================
            # USUARIO
            # ============================================

            html.Div(

                className="header-user",

                children=[

                    html.Div(

                        [

                            html.Div(

                                "Juan Portillo",

                                className="usuario"

                            ),

                            html.Small(

                                "Administrador",

                                className="puesto"

                            )

                        ]

                    ),

                    html.Div(

                        "JP",

                        className="avatar"

                    )

                ]

            )

        ]

    )