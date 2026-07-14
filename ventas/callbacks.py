"""
=========================================================
CALLBACKS DEL MÓDULO VENTAS
=========================================================
"""

from dash import Input, Output


def registrar_callbacks_ventas(app):


    # ==========================================
    # Nombre Catálogo
    # ==========================================

    @app.callback(

        Output(
            "nombre-catalogo",
            "children"
        ),

        Input(
            "upload-catalogo",
            "filename"
        )

    )

    def mostrar_catalogo(nombre):

        if nombre is None:

            return "Ningún archivo seleccionado."

        return f"✅ {nombre}"


    # ==========================================
    # Nombre BD Ventas
    # ==========================================

    @app.callback(

        Output(
            "nombre-ventas",
            "children"
        ),

        Input(
            "upload-ventas",
            "filename"
        )

    )

    def mostrar_bd(nombre):

        if nombre is None:

            return "Ningún archivo seleccionado."

        return f"✅ {nombre}"