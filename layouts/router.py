"""
=========================================================
ROUTER DEL SISTEMA
=========================================================
"""

from dash import html

from layouts.dashboard import crear_dashboard
from ventas.layout import crear_layout_ventas
from carga import crear_layout_carga
from ingresos.layout import crear_layout_ingresos
from inventario.layout import crear_layout_inventario
from configuracion import crear_layout_configuracion
from cartera.layout import crear_layout_cartera
from proyeccion.vista import crear_layout_proyeccion
from captura_proyeccion import crear_layout_captura_proyeccion
from saldo_proveedor.layout import crear_layout_saldo_proveedor
from bsc.vista import crear_layout_bsc


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

    elif pathname == "/proyeccion":

        return crear_layout_proyeccion()

    elif pathname == "/captura-proyeccion":

        return crear_layout_captura_proyeccion()

    elif pathname == "/cargar":

        return crear_layout_carga()

    elif pathname == "/ingresos":

        return crear_layout_ingresos()

    elif pathname == "/cartera":

        return crear_layout_cartera()

    elif pathname == "/inventario":

        return crear_layout_inventario()

    elif pathname == "/saldo-proveedor":

        return crear_layout_saldo_proveedor()

    elif pathname == "/bsc":

        return crear_layout_bsc()

    elif pathname == "/reportes":

        return pagina_temporal("Reportes")

    elif pathname == "/configuracion":

        return crear_layout_configuracion()

    return pagina_temporal("Página no encontrada")