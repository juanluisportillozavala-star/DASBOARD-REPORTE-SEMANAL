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
    # (múltiple + "seleccionar todo" + "limpiar")
    #
    # Los iconos "seleccionar-todos-meses" y "limpiar-meses"
    # viven en ventas/controles.py (html.I con id propio).
    #
    # Cuando el usuario toca directamente los controles de
    # mes (clic individual, seleccionar todo o limpiar), se
    # auto-seleccionan también las semanas de esos meses. Esa
    # auto-selección vive AQUÍ (no en un callback separado
    # escuchando "store-mes") para que NO se dispare cuando
    # el mes se activa solo como efecto secundario de elegir
    # una semana suelta (ver "seleccionar_semanas" más abajo).
    # =====================================================

    @app.callback(

        Output("store-mes", "data"),

        Output("store-semana", "data"),

        Input(
            {
                "type": "btn-mes",
                "index": ALL
            },
            "n_clicks"
        ),

        Input("seleccionar-todos-meses", "n_clicks"),

        Input("limpiar-meses", "n_clicks"),

        State("store-mes", "data"),

        State("store-bd-ventas", "data"),

        prevent_initial_call=True

    )

    def seleccionar_meses(_, todo_clicks, limpiar_clicks, meses_activos, data):

        if ctx.triggered_id is None:

            return no_update, no_update

        if meses_activos is None:

            meses_activos = []

        trigger = ctx.triggered_id

        # -----------------------------------------
        # Seleccionar todos los meses CON DATOS
        # -----------------------------------------

        if trigger == "seleccionar-todos-meses":

            if not data:

                return no_update, no_update

            df = pd.DataFrame(data)

            meses_con_datos = sorted(

                df["Mes"]

                .dropna()

                .astype(int)

                .unique()

                .tolist()

            )

            semanas_auto = sorted(

                obtener_semanas(

                    df,

                    meses_con_datos

                )

            )

            return meses_con_datos, semanas_auto

        # -----------------------------
        # Limpiar meses (limpia también semanas)
        # -----------------------------

        if trigger == "limpiar-meses":

            return [], []

        # -----------------------------
        # Activa / Desactiva un mes
        # -----------------------------

        mes = int(trigger["index"])

        if mes in meses_activos:

            meses_activos.remove(mes)

        else:

            meses_activos.append(mes)

        meses_activos = sorted(meses_activos)

        if data is None:

            semanas_auto = []

        else:

            df = pd.DataFrame(data)

            semanas_auto = sorted(

                obtener_semanas(

                    df,

                    meses_activos

                )

            )

        return meses_activos, semanas_auto

    # =====================================================
    # PINTAR MESES
    #
    # Solo pinta className activo/inactivo según store-mes.
    # Ya no toca "store-semana": esa auto-selección ahora
    # vive dentro de "seleccionar_meses", para que no se
    # dispare cuando el mes se activa como efecto secundario
    # de elegir una semana suelta.
    #
    # Las 52 celdas de semana son FIJAS y viven en el layout
    # (ventas/controles.py), igual que los 12 meses. Por qué:
    # si se regeneraran cada vez que cambia el mes, Dash
    # resetea el n_clicks de cada botón a 0, y ese reseteo se
    # interpreta como un clic real, desmarcando semanas solas.
    # =====================================================

    @app.callback(

        Output(
            {
                "type": "btn-mes",
                "index": ALL
            },
            "className"
        ),

        Input("store-mes", "data")

    )

    def pintar_meses(meses_activos):

        if meses_activos is None:

            meses_activos = []

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

        return clases

    # =====================================================
    # SELECCIÓN DE SEMANAS
    # (múltiple + "seleccionar todo" + "limpiar" +
    # la primera semana nunca se desmarca)
    #
    # Los iconos "seleccionar-todas-semanas" y "limpiar-semanas"
    # viven en ventas/controles.py (html.I con id propio).
    #
    # "Seleccionar todas las semanas" toma TODAS las semanas
    # con datos en el archivo completo (sin importar el mes
    # activo) y además marca los meses correspondientes a
    # esas semanas, para que meses y semanas queden coherentes
    # en pantalla.
    #
    # Este callback escribe sobre "store-semana" y "store-mes",
    # los mismos Outputs que usan otros callbacks. Por eso usa
    # allow_duplicate=True (soportado por Dash >= 2.9), sin
    # modificar la arquitectura del resto del proyecto.
    # =====================================================

    @app.callback(

        Output("store-semana", "data", allow_duplicate=True),

        Output("store-mes", "data", allow_duplicate=True),

        Input(
            {
                "type": "btn-semana",
                "index": ALL
            },
            "n_clicks"
        ),

        Input("seleccionar-todas-semanas", "n_clicks"),

        Input("limpiar-semanas", "n_clicks"),

        State("store-semana", "data"),

        State("store-mes", "data"),

        State("store-bd-ventas", "data"),

        prevent_initial_call=True

    )

    def seleccionar_semanas(_, todo_clicks, limpiar_clicks, semanas_activas, meses_activos, data):

        if ctx.triggered_id is None:

            return no_update, no_update

        if semanas_activas is None:

            semanas_activas = []

        if meses_activos is None:

            meses_activos = []

        trigger = ctx.triggered_id

        # -----------------------------------------------
        # Seleccionar TODAS las semanas con datos (sin
        # importar el mes activo) y marcar los meses a
        # los que pertenecen esas semanas.
        # -----------------------------------------------

        if trigger == "seleccionar-todas-semanas":

            if not data:

                return no_update, no_update

            df = pd.DataFrame(data)

            semanas_todas = sorted(

                df["Semana"]

                .dropna()

                .astype(int)

                .unique()

                .tolist()

            )

            meses_de_esas_semanas = sorted(

                df["Mes"]

                .dropna()

                .astype(int)

                .unique()

                .tolist()

            )

            return semanas_todas, meses_de_esas_semanas

        # -----------------------------------------------
        # "Semanas visibles" (relevantes a los meses elegidos)
        # solo se pueden calcular si ya hay datos procesados.
        # Sin datos, no hay semana "protegida" pero el toggle
        # individual y "limpiar" igual funcionan (semanas
        # siempre clickeables).
        # -----------------------------------------------

        if data is None:

            semanas_visibles = []

        else:

            df = pd.DataFrame(data)

            semanas_visibles = sorted(

                obtener_semanas(

                    df,

                    meses_activos

                )

            )

        primera_semana = semanas_visibles[0] if semanas_visibles else None

        # -----------------------------------
        # Limpiar semanas: quita TODO, sin
        # excepciones (igual que limpiar meses)
        # -----------------------------------

        if trigger == "limpiar-semanas":

            return [], no_update

        # -----------------------------------
        # Activar / desactivar una semana
        # -----------------------------------

        semana = int(trigger["index"])

        mes_resultado = no_update

        if semana in semanas_activas:

            # La primera semana no se puede desmarcar
            # con un clic individual (sí se puede con
            # "limpiar", arriba)

            if semana == primera_semana:

                return no_update, no_update

            semanas_activas.remove(semana)

        else:

            semanas_activas.append(semana)

            # -----------------------------------------------
            # Auto-seleccionar el mes correspondiente a esta
            # semana, si aún no está activo.
            # -----------------------------------------------

            if data is not None:

                fila_semana = df[df["Semana"] == semana]

                if not fila_semana.empty:

                    mes_de_la_semana = int(

                        fila_semana["Mes"]

                        .dropna()

                        .astype(int)

                        .iloc[0]

                    )

                    if mes_de_la_semana not in meses_activos:

                        mes_resultado = sorted(

                            meses_activos + [mes_de_la_semana]

                        )

        semanas_activas = sorted(semanas_activas)

        return semanas_activas, mes_resultado

    # =====================================================
    # PINTAR SEMANAS
    #
    # El grid de semanas ahora es fijo (1-52), así que solo
    # se necesita "store-semana" para saber cuáles pintar
    # como activas; ya no depende de los datos ni del mes.
    # =====================================================

    @app.callback(

        Output(

            {

                "type": "btn-semana",

                "index": ALL

            },

            "className"

        ),

        Input("store-semana", "data")

    )

    def pintar_semanas(semanas_activas):

        if semanas_activas is None:

            semanas_activas = []

        clases = []

        for semana in range(1, 53):

            if semana in semanas_activas:

                clases.append(

                    "cuadro-semana activo"

                )

            else:

                clases.append(

                    "cuadro-semana"

                )

        return clases