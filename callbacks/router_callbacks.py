"""
=========================================================
router_callbacks.py
=========================================================
Callbacks de navegación del Sistema Gerencial Liderza.
"""

from dash import Input, Output

from layouts.router import obtener_layout


def registrar_router_callbacks(app):

    # =====================================================
    # CAMBIO DE PÁGINAS
    # =====================================================

    @app.callback(

        Output("contenido-principal", "children"),

        Input("url", "pathname")

    )
    def cambiar_pagina(pathname):

        if pathname is None:

            return obtener_layout("dashboard")

        pagina = pathname.replace("/", "").lower()

        if pagina == "":

            pagina = "dashboard"

        return obtener_layout(pagina)