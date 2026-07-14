"""
=========================================================
CALLBACKS DEL MÓDULO VENTAS
=========================================================
"""

from dash import Input, Output, State, html

from ventas.procesamiento import leer_archivos


def registrar_callbacks_ventas(app):

    # =====================================================
    # Mostrar nombre Catálogo
    # =====================================================

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


    # =====================================================
    # Mostrar nombre BD Ventas
    # =====================================================

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


    # =====================================================
    # PROCESAR INFORMACIÓN
    # =====================================================

    @app.callback(

        Output("estado-proceso", "children"),

        Input("btn-procesar", "n_clicks"),

        State("upload-catalogo", "contents"),

        State("upload-ventas", "contents"),

        prevent_initial_call=True

    )

    def procesar(click, catalogo, ventas):

        if catalogo is None:

            return html.Div(

                "Debe seleccionar el archivo Catálogo.",

                style={

                    "color":"red",

                    "fontWeight":"bold"

                }

            )

        if ventas is None:

            return html.Div(

                "Debe seleccionar el archivo BD Ventas.",

                style={

                    "color":"red",

                    "fontWeight":"bold"

                }

            )

        try:

            df_catalogo, df_ventas = leer_archivos(

                catalogo,

                ventas

            )

            productos_catalogo = len(df_catalogo)

            registros = len(df_ventas)

            productos_encontrados = df_ventas["Producto 2"].notna().sum()

            productos_faltantes = df_ventas["Producto 2"].isna().sum()

            monedas_usd = 0

            if "Líneas de la orden de venta/Divisa" in df_ventas.columns:

                monedas_usd = (

                    df_ventas["Líneas de la orden de venta/Divisa"]

                    .astype(str)

                    .str.upper()

                    .eq("USD")

                    .sum()

                )

            return html.Div(

                [

                    html.H5("Proceso terminado correctamente"),

                    html.Hr(),

                    html.P(f"📄 Registros procesados: {registros:,}"),

                    html.P(f"📦 Productos en catálogo: {productos_catalogo:,}"),

                    html.P(f"✅ Productos encontrados: {productos_encontrados:,}"),

                    html.P(f"⚠ Productos sin encontrar: {productos_faltantes:,}"),

                    html.P(f"💲 Registros en USD: {monedas_usd:,}"),

                    html.Br(),

                    html.Div(

                        "La base quedó lista para generar KPIs, gráficas y calendario.",

                        style={

                            "color":"green",

                            "fontWeight":"bold"

                        }

                    )

                ]

            )

        except Exception as e:

            return html.Div(

                [

                    html.H5(

                        "Error durante el procesamiento",

                        style={

                            "color":"red"

                        }

                    ),

                    html.Hr(),

                    html.Pre(str(e))

                ]

            )