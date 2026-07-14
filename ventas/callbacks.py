"""
============================================================
CALLBACKS
============================================================
"""

from dash import Input, Output


def registrar_callbacks(app):

    @app.callback(

        Output("mensaje", "children"),

        Input("upload-catalogo", "filename"),

        Input("upload-bd", "filename")

    )

    def mostrar_archivos(catalogo, bd):

        if catalogo is None and bd is None:

            return "Esperando archivos..."

        texto = ""

        if catalogo:

            texto += f"✅ Catálogo: {catalogo}"

        if bd:

            texto += f" | ✅ BD: {bd}"

        return texto