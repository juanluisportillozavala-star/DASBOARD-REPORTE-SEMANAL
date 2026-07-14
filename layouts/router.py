"""
=========================================================
ROUTER DEL SISTEMA
=========================================================
"""

from dash import html

from layouts.dashboard import crear_dashboard
from ventas.layout import crear_layout_ventas


def pagina_temporal(nombre):

    return html.Div(

        className="card-premium",

        children=[

            html.H1(
                nombre,
                className="titulo"
            ),

            html.P(
                "Módulo en construcción.",
                className="subtitulo"
            )

        ]

    )


def crear_router(pathname):

    if pathname in [None, "/", "/dashboard"]:

        return crear_dashboard()

    elif pathname == "/ventas":

        return crear_layout_ventas()

    elif pathname == "/ingresos":

        return pagina_temporal("Ingresos")

    elif pathname == "/cartera":

        return pagina_temporal("Cartera")

    elif pathname == "/inventario":

        return pagina_temporal("Inventario")

    elif pathname == "/saldo-proveedor":

        return pagina_temporal("Saldo Proveedor")

    elif pathname == "/reportes":

        return pagina_temporal("Reportes")

    elif pathname == "/configuracion":

        return pagina_temporal("Configuración")

    return pagina_temporal("Página no encontrada")