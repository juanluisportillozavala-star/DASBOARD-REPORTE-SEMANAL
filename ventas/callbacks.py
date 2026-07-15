"""
=========================================================
CALLBACKS DEL MÓDULO VENTAS
=========================================================
"""

from dash import Input, Output, State, html, ALL, ctx, no_update
import pandas as pd

from ventas.filtros import obtener_semanas

from ventas.procesamiento import leer_archivos
from ventas.kpis import calcular_kpis
from ventas.cards import crear_cards


def registrar_callbacks_ventas(app):

    # =====================================================
    # NOMBRE DEL CATÁLOGO
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

            html.I(

                className="fas fa-circle-check me-2",

                style={"color": "#198754"}

            ),

            nombre

        ]

    # =====================================================
    # NOMBRE BD VENTAS
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

            html.I(

                className="fas fa-circle-check me-2",

                style={"color": "#198754"}

            ),

            nombre

        ]

    # =====================================================
    # PROCESAR INFORMACIÓN
    # =====================================================

    @app.callback(

        Output("estado-proceso", "children"),

        Output("store-bd-ventas", "data"),

        Output("store-kpis", "data"),

        Input("btn-procesar", "n_clicks"),

        State("upload-catalogo", "contents"),

        State("upload-ventas", "contents"),

        prevent_initial_call=True

    )

    def procesar_archivos(n_clicks, catalogo, ventas):

        # ==============================================
        # VALIDACIONES
        # ==============================================

        if catalogo is None:

            return (

                html.Div(

                    "❌ Debe seleccionar el archivo Catálogo.",

                    style={

                        "color": "red",

                        "fontWeight": "bold"

                    }

                ),

                None,

                None

            )

        if ventas is None:

            return (

                html.Div(

                    "❌ Debe seleccionar la BD Ventas.",

                    style={

                        "color": "red",

                        "fontWeight": "bold"

                    }

                ),

                None,

                None

            )

        # ==============================================
        # PROCESAMIENTO
        # ==============================================

        try:

            df_catalogo, df_ventas = leer_archivos(

                catalogo,

                ventas

            )

            # ==========================================
            # KPIs
            # ==========================================

            kpis = calcular_kpis(df_ventas)

            # ==========================================
            # ESTADO
            # ==========================================

            estado = html.Div(

                [

                    html.H4(

                        [

                            html.I(

                                className="fas fa-circle-check me-2"

                            ),

                            "Proceso completado correctamente"

                        ],

                        style={

                            "color": "#198754"

                        }

                    ),

                    html.Hr(),

                    html.P(

                        f"📄 Registros procesados: {len(df_ventas):,}"

                    ),

                    html.P(

                        f"📦 Productos del catálogo: {len(df_catalogo):,}"

                    ),

                    html.Br(),

                    html.B(

                        "La información quedó lista para generar el Dashboard.",

                        style={

                            "color": "#0D6EFD"

                        }

                    )

                ]

            )

            return (

                estado,

                df_ventas.to_dict("records"),

                kpis

            )

        except Exception as e:

            return (

                html.Div(

                    [

                        html.H4(

                            "Error durante el procesamiento",

                            style={

                                "color": "red"

                            }

                        ),

                        html.Hr(),

                        html.Pre(

                            str(e)

                        )

                    ]

                ),

                None,

                None

            )

    # =====================================================
    # ACTUALIZAR TARJETAS KPI
    # =====================================================

    @app.callback(

        Output(

            "contenedor-kpis",

            "children"

        ),

        Input(

            "store-kpis",

            "data"

        )

    )

    def actualizar_cards(kpis):

        if kpis is None:

            return ""

        return crear_cards(kpis)
# =====================================================
# SELECCIÓN DE MESES
# =====================================================

    @app.callback(

        Output("store-mes", "data"),

        Output("store-semana","data"),
        
        Output("selector-semanas","children"),

        Output(
            {
                "type": "btn-mes",
                "index": ALL
            },
            "className"
        ),

        Input(
            {
                "type": "btn-mes",
                "index": ALL
            },
            "n_clicks"
        ),

        State("store-mes", "data"),

        State("store-bd-ventas", "data"),

        prevent_initial_call=True

    )

    def seleccionar_meses(_, meses_activos, data):

        if data is None:

            return [], [], ["cuadro-mes"] * 12

        if meses_activos is None:

            meses_activos = []

        trigger = ctx.triggered_id

        if trigger is None:

            return meses_activos, [], ["cuadro-mes"] * 12

        mes = trigger["index"]

        # ----------------------------------------
        # Activa / Desactiva
        # ----------------------------------------

        if mes in meses_activos:

            meses_activos.remove(mes)

        else:

            meses_activos.append(mes)

        meses_activos.sort()

        # ----------------------------------------
        # Obtener semanas
        # ----------------------------------------

        df = pd.DataFrame(data)

        semanas = obtener_semanas(

            df,

            meses_activos

        )

        import dash_bootstrap_components as dbc

        botones = [

            dbc.Button(

                str(s),

                id={

                    "type": "btn-semana",

                    "index": int(s)

                },

                className="cuadro-semana activo",

                color="light",

                outline=True,

                n_clicks=0

            )

            for s in semanas

        ]

        clases = []

        for i in range(1, 13):

            if i in meses_activos:

                clases.append(

                    "cuadro-mes activo"

                )

            else:

                clases.append(

                    "cuadro-mes"

                )

        return (

            meses_activos,
            
            semanas,

            botones,

            clases

        )
# =====================================================
# SELECCIÓN DE SEMANAS
# =====================================================

    @app.callback(

        Output("store-semana", "data"),

        Output(

            {

                "type": "btn-semana",

                "index": ALL

            },

            "className"

        ),

        Input(

            {

                "type": "btn-semana",

                "index": ALL

            },

            "n_clicks"

        ),

        State(

            "store-semana",

            "data"

        ),

        prevent_initial_call=True

    )

    def seleccionar_semana(_, semanas_seleccionadas):

        if ctx.triggered_id is None:

            return (

                [],

                []

            )

        semana = ctx.triggered_id["index"]

        if semanas_seleccionadas is None:

            semanas_seleccionadas = []

        # ==========================================
        # Agregar o quitar semana
        # ==========================================

        if semana in semanas_seleccionadas:

            semanas_seleccionadas.remove(semana)

        else:

            semanas_seleccionadas.append(semana)

        semanas_seleccionadas = sorted(semanas_seleccionadas)

        # ==========================================
        # Pintar botones
        # ==========================================

        clases = []

        botones = ctx.inputs_list[0]

        for boton in botones:

            indice = boton["id"]["index"]

            if indice in semanas_seleccionadas:

                clases.append(

                    "cuadro-semana activo"

                )

            else:

                clases.append(

                    "cuadro-semana"

                )

        return (

            semanas_seleccionadas,

            clases

        )