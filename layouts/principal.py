"""
LAYOUT PRINCIPAL
"""

from dash import html, dcc

from layouts.header import crear_header
from layouts.sidebar import crear_sidebar


def crear_principal():

    return html.Div(

        children=[

            # ====================================
            # Detecta la URL
            # ====================================

            dcc.Location(
                id="url",
                refresh=False
            ),

            # ====================================
            # HEADER
            # ====================================

            crear_header(),

            # ====================================
            # LINEA DORADA
            # ====================================

            html.Div(
                className="linea-dorada"
            ),

            # ====================================
            # SIDEBAR
            # ====================================

            crear_sidebar(),

            # ====================================
            # CONTENIDO
            # ====================================

            html.Div(

                className="body",

                children=[

                    html.Div(

                        id="contenido-principal",

                        className="contenido"

                    )

                ]

            )

        ]

    )