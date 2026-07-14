"""
ROUTER CALLBACKS
"""

from dash import Input, Output

from layouts.dashboard import crear_dashboard
from layouts.router import crear_router


def registrar_router_callbacks(app):

    @app.callback(

        Output("contenido-principal", "children"),

        Input("url", "pathname")

    )

    def cambiar_pagina(pathname):

        if pathname in [None, "/", "/dashboard"]:

            return crear_dashboard()

        return crear_router(pathname)