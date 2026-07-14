"""
=========================================================
router.py
=========================================================
Controlador de páginas.
"""

from dash import html

from layouts.dashboard import crear_dashboard


def obtener_layout(pagina):

    pagina = (pagina or "").lower()

    paginas = {

        "dashboard": crear_dashboard

    }

    if pagina in paginas:

        return paginas[pagina]()

    return html.Div(

        [

            html.H2(

                pagina.title(),

                className="titulo"

            ),

            html.P(

                "Este módulo estará disponible próximamente."

            )

        ],

        className="contenido"

    )