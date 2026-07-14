"""
LAYOUT PRINCIPAL
"""

from dash import html

from layouts.header import crear_header
from layouts.sidebar import crear_sidebar
from layouts.router import crear_router


def crear_principal():

    return html.Div(

        children=[

            # ==========================
            # HEADER
            # ==========================

            crear_header(),

            # ==========================
            # LINEA DORADA
            # ==========================

            html.Div(
                className="linea-dorada"
            ),

            # ==========================
            # SIDEBAR
            # ==========================

            crear_sidebar(),

            # ==========================
            # CONTENIDO
            # ==========================

            html.Div(

                className="body",

                children=[

                    html.Div(

                        className="contenido",

                        children=[

                            crear_router()

                        ]

                    )

                ]

            )

        ]

    )