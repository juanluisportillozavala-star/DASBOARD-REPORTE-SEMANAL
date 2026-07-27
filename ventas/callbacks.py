"""
=========================================================
CALLBACKS DEL MÓDULO VENTAS
=========================================================
"""

from dash import Input, Output, State, html, ALL, ctx, no_update
import pandas as pd

from ventas.filtros import obtener_semanas, filtrar_dataframe

from ventas.procesamiento import leer_archivos
from ventas.kpis import calcular_kpis
from ventas.cards import crear_cards

from ventas.analisis import arbol_ventas, total_general_arbol, filas_visibles

from ventas.aggrid import (
    crear_aggrid,
    crear_encabezado_periodo,
    configuracion_tamano,
    estilo_grid,
    opciones_grid
)

# Capa de base de datos (Supabase / PostgreSQL). Se importa aquí
# arriba una sola vez. Si por lo que sea db no estuviera disponible,
# los try/except en cada uso evitan que se rompa la app.
import db


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
            # GUARDAR EN SUPABASE (persistencia compartida)
            #
            # Se guarda la BD en la base para que quede
            # disponible a TODOS los que entren (no solo en
            # esta sesión). Si la base fallara, NO se rompe el
            # procesamiento: la pantalla sigue funcionando con
            # el store local y se deja rastro en los logs.
            # ==========================================

            try:

                db.guardar_dataset("ventas", df_ventas, "admin")

            except Exception as e_db:

                print(

                    f">>> [DB] No se pudo guardar en Supabase: {e_db}",

                    flush=True

                )

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
    # CARGAR DESDE SUPABASE AL ENTRAR
    #
    # Cuando cualquier persona abre la página, si el store de
    # ventas está vacío (no ha procesado nada en su sesión),
    # se llena leyendo la última BD guardada en Supabase. Así,
    # quien entre ve automáticamente el reporte que el admin
    # cargó, sin subir archivos. También recalcula los KPIs.
    #
    # Se dispara con la carga del layout de ventas (Input al
    # propio store, que arranca vacío -> None). allow_duplicate
    # porque store-bd-ventas / store-kpis también los escribe
    # el callback de procesar.
    # =====================================================

    @app.callback(

        Output("store-bd-ventas", "data", allow_duplicate=True),

        Output("store-kpis", "data", allow_duplicate=True),

        Input("store-bd-ventas", "data"),

        prevent_initial_call="initial_duplicate"

    )

    def cargar_desde_bd(store_actual):

        # Si ya hay datos en el store (el admin acaba de procesar,
        # o ya se cargaron antes), no hacemos nada: evita pisar
        # datos frescos y evita un bucle.

        if store_actual:

            return no_update, no_update

        # Store vacío -> intentar leer la última BD de Supabase.

        try:

            df = db.leer_dataset("ventas")

        except Exception as e_db:

            print(

                f">>> [DB] No se pudo leer de Supabase: {e_db}",

                flush=True

            )

            return no_update, no_update

        if df is None or len(df) == 0:

            return no_update, no_update

        kpis = calcular_kpis(df)

        return df.to_dict("records"), kpis

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

        State("store-semana", "data"),

        State("store-bd-ventas", "data"),

        prevent_initial_call=True

    )

    def seleccionar_meses(_, todo_clicks, limpiar_clicks, meses_activos, semanas_activas, data):

        if ctx.triggered_id is None:

            return no_update, no_update

        if meses_activos is None:

            meses_activos = []

        if semanas_activas is None:

            semanas_activas = []

        trigger = ctx.triggered_id

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

        if trigger == "limpiar-meses":

            return [], []

        mes = int(trigger["index"])

        if data is None:

            if mes in meses_activos:

                meses_activos.remove(mes)

            else:

                meses_activos.append(mes)

            return sorted(meses_activos), no_update

        df = pd.DataFrame(data)

        semanas_del_mes = set(

            obtener_semanas(

                df,

                [mes]

            )

        )

        if mes in meses_activos:

            meses_activos.remove(mes)

            semanas_activas = [

                s for s in semanas_activas

                if s not in semanas_del_mes

            ]

        else:

            meses_activos.append(mes)

            semanas_activas = sorted(

                set(semanas_activas) | semanas_del_mes

            )

        meses_activos = sorted(meses_activos)

        return meses_activos, semanas_activas

    # =====================================================
    # PINTAR MESES
    # =====================================================

    @app.callback(

        Output(
            {
                "type": "btn-mes",
                "index": ALL
            },
            "className"
        ),

        Output(
            {
                "type": "btn-mes",
                "index": ALL
            },
            "disabled"
        ),

        Input("store-mes", "data"),

        Input("store-bd-ventas", "data")

    )

    def pintar_meses(meses_activos, data):

        if meses_activos is None:

            meses_activos = []

        if data is None:

            meses_con_datos = set()

        else:

            df = pd.DataFrame(data)

            meses_con_datos = set(

                df["Mes"]

                .dropna()

                .astype(int)

                .unique()

                .tolist()

            )

        clases = []

        deshabilitados = []

        for i in range(1, 13):

            if i in meses_activos:

                clases.append(

                    "cuadro-mes activo"

                )

            else:

                clases.append(

                    "cuadro-mes"

                )

            deshabilitados.append(

                i not in meses_con_datos

            )

        return clases, deshabilitados

    # =====================================================
    # SELECCIÓN DE SEMANAS
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

        if trigger == "limpiar-semanas":

            return [], []

        semana = int(trigger["index"])

        mes_resultado = no_update

        if semana in semanas_activas:

            if semana == primera_semana:

                return no_update, no_update

            semanas_activas.remove(semana)

        else:

            semanas_activas.append(semana)

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
    # =====================================================

    @app.callback(

        Output(

            {

                "type": "btn-semana",

                "index": ALL

            },

            "className"

        ),

        Output(

            {

                "type": "btn-semana",

                "index": ALL

            },

            "disabled"

        ),

        Input("store-semana", "data"),

        Input("store-bd-ventas", "data")

    )

    def pintar_semanas(semanas_activas, data):

        if semanas_activas is None:

            semanas_activas = []

        if data is None:

            semanas_con_datos = set()

        else:

            df = pd.DataFrame(data)

            semanas_con_datos = set(

                df["Semana"]

                .dropna()

                .astype(int)

                .unique()

                .tolist()

            )

        clases = []

        deshabilitados = []

        for semana in range(1, 54):

            if semana in semanas_activas:

                clases.append(

                    "cuadro-semana activo"

                )

            else:

                clases.append(

                    "cuadro-semana"

                )

            deshabilitados.append(

                semana not in semanas_con_datos

            )

        return clases, deshabilitados