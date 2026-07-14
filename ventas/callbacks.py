"""
=========================================================
CALLBACKS DEL MÓDULO VENTAS
=========================================================
"""

from dash import Input, Output, State, html
from ventas.procesamiento import leer_archivos


def registrar_callbacks_ventas(app):

    # ======================================================
    # Mostrar nombre del Catálogo
    # ======================================================

    @app.callback(

        Output("nombre-catalogo", "children"),

        Input("upload-catalogo", "filename")

    )
    def mostrar_catalogo(nombre):

        if nombre is None:

            return [

                html.I(className="fas fa-file-excel me-2"),

                " Ningún archivo seleccionado."

            ]

        return [

            html.I(className="fas fa-circle-check me-2"),

            nombre

        ]


    # ======================================================
    # Mostrar nombre BD Ventas
    # ======================================================

    @app.callback(

        Output("nombre-ventas", "children"),

        Input("upload-ventas", "filename")

    )
    def mostrar_bd(nombre):

        if nombre is None:

            return [

                html.I(className="fas fa-file-excel me-2"),

                " Ningún archivo seleccionado."

            ]

        return [

            html.I(className="fas fa-circle-check me-2"),

            nombre

        ]


    # ======================================================
    # Procesar información
    # ======================================================

    @app.callback(

        Output("estado-proceso", "children"),

        Input("btn-procesar", "n_clicks"),

        State("upload-catalogo", "contents"),

        State("upload-ventas", "contents"),

        prevent_initial_call=True

    )

    def procesar_archivos(click, catalogo, ventas):

        if catalogo is None:

            return html.Div(

                "❌ Debe seleccionar el archivo Catálogo.",

                style={

                    "color": "red",

                    "fontWeight": "bold"

                }

            )

        if ventas is None:

            return html.Div(

                "❌ Debe seleccionar el archivo BD Ventas.",

                style={

                    "color": "red",

                    "fontWeight": "bold"

                }

            )

        try:

            df_catalogo, df_ventas = leer_archivos(

                catalogo,

                ventas

            )

            return html.Div(

                [

                    html.P("✅ Catálogo leído correctamente"),

                    html.P("✅ BD Ventas leída correctamente"),

                    html.P(

                        f"📄 Registros encontrados: {len(df_ventas):,}"

                    ),

                    html.P(

                        f"📦 Productos del catálogo: {len(df_catalogo):,}"

                    ),

                    html.Br(),

                    html.B(

                        "Proceso terminado correctamente.",

                        style={

                            "color": "#198754"

                        }

                    )

                ]

            )

        except Exception as e:

            return html.Div(

                [

                    html.P(

                        "❌ Error al procesar los archivos.",

                        style={

                            "color": "red",

                            "fontWeight": "bold"

                        }

                    ),

                    html.P(str(e))

                ]

            )