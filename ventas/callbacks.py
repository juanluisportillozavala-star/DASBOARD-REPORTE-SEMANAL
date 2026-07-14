"""
=========================================================
CALLBACKS DEL MÓDULO VENTAS
=========================================================
"""

from dash import Input, Output, State
from dash import dash_table
from dash import html

from ventas.procesamiento import leer_archivos


def registrar_callbacks_ventas(app):

    # ===================================================
    # Nombre Catálogo
    # ===================================================

    @app.callback(

        Output("nombre-catalogo", "children"),

        Input("upload-catalogo", "filename")

    )
    def mostrar_catalogo(nombre):

        if nombre is None:

            return "Ningún archivo seleccionado."

        return f"✅ {nombre}"


    # ===================================================
    # Nombre BD
    # ===================================================

    @app.callback(

        Output("nombre-ventas", "children"),

        Input("upload-ventas", "filename")

    )
    def mostrar_bd(nombre):

        if nombre is None:

            return "Ningún archivo seleccionado."

        return f"✅ {nombre}"


    # ===================================================
    # Procesar
    # ===================================================

    @app.callback(

        Output("vista-previa", "children"),

        Input("btn-procesar", "n_clicks"),

        State("upload-catalogo", "contents"),

        State("upload-ventas", "contents"),

        prevent_initial_call=True

    )

    def procesar(n, catalogo, ventas):

        if catalogo is None or ventas is None:

            return html.Div(

                "Debe cargar ambos archivos.",

                style={

                    "color":"red",

                    "fontWeight":"bold"

                }

            )

        df_catalogo, df_ventas = leer_archivos(

            catalogo,

            ventas

        )

        return html.Div(

            [

                html.H4("Vista previa BD Ventas"),

                dash_table.DataTable(

                    data=df_ventas.head(10).to_dict("records"),

                    columns=[

                        {

                            "name":i,

                            "id":i

                        }

                        for i in df_ventas.columns

                    ],

                    page_size=10,

                    style_table={

                        "overflowX":"auto"

                    }

                )

            ]

        )