"""
=========================================================
principal.py
=========================================================
Layout principal del Sistema Gerencial Liderza.
"""

from dash import html, dcc

from layouts.header import crear_header
from layouts.sidebar import crear_sidebar
from layouts.router import obtener_layout


def crear_principal():

    return html.Div(

        [

            # ==========================================
            # URL (necesaria para la navegación)
            # ==========================================

            dcc.Location(

                id="url",

                refresh=False

            ),

            # ==========================================
            # HEADER
            # ==========================================

            crear_header(),

            # ==========================================
            # CUERPO
            # ==========================================

            html.Div(

                className="body",

                children=[

                    # ----------------------------
                    # SIDEBAR
                    # ----------------------------

                    crear_sidebar(),

                    # ----------------------------
                    # CONTENIDO
                    # ----------------------------

                    html.Div(

                        id="contenido-principal",

                        className="contenido",

                        children=[

                            obtener_layout(

                                "dashboard"

                            )

                        ]

                    )

                ]

            )

        ]

    )