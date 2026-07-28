"""
=========================================================
CALLBACKS DEL MÓDULO VENTAS
=========================================================
VELOCIDAD: los datos NO viajan en store-bd-ventas. Viven en
la caché del servidor (db.obtener_df). El store guarda solo
una marca ligera {"cargado": True, "version": N}. Así el
navegador no reenvía las 589 filas en cada callback.
"""

from dash import Input, Output, State, html, ALL, ctx, no_update
import pandas as pd

from ventas.filtros import obtener_semanas, filtrar_dataframe

from ventas.kpis import calcular_kpis
from ventas.cards import crear_cards

import db

MODULO = "ventas"


def _df():
    """Atajo: DataFrame de ventas desde la caché del servidor."""
    return db.obtener_df(MODULO)


def registrar_callbacks_ventas(app):

    # =====================================================
    # CARGAR DESDE SUPABASE AL ENTRAR
    #
    # Pone en store-bd-ventas solo una MARCA LIGERA (no las
    # filas). Si hay datos en la base, marca {"cargado": True,
    # "version": N}. La versión permite que, si el admin sube
    # datos nuevos, los navegadores abiertos lo detecten (la
    # versión del servidor cambia) y recarguen KPIs/tablas.
    # =====================================================

    @app.callback(
        Output("store-bd-ventas", "data"),
        Output("store-kpis", "data"),
        Input("store-bd-ventas", "data"),
    )
    def cargar_desde_bd(marca):
        try:
            df = _df()
        except Exception as e_db:
            print(f">>> [DB] No se pudo leer de Supabase: {e_db}", flush=True)
            return no_update, no_update

        if df is None or len(df) == 0:
            return no_update, no_update

        version = db.version_actual(MODULO)

        # Si el store ya tiene la versión vigente, no rehacer nada
        if marca and isinstance(marca, dict) and marca.get("version") == version:
            return no_update, no_update

        kpis = calcular_kpis(df)
        return {"cargado": True, "version": version}, kpis

    # =====================================================
    # ACTUALIZAR TARJETAS KPI
    # =====================================================

    @app.callback(
        Output("contenedor-kpis", "children"),
        Input("store-kpis", "data"),
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
        Input({"type": "btn-mes", "index": ALL}, "n_clicks"),
        Input("seleccionar-todos-meses", "n_clicks"),
        Input("limpiar-meses", "n_clicks"),
        State("store-mes", "data"),
        State("store-semana", "data"),
        prevent_initial_call=True,
    )
    def seleccionar_meses(_, todo_clicks, limpiar_clicks, meses_activos, semanas_activas):

        if ctx.triggered_id is None:
            return no_update, no_update

        if meses_activos is None:
            meses_activos = []
        if semanas_activas is None:
            semanas_activas = []

        trigger = ctx.triggered_id
        df = _df()

        if trigger == "seleccionar-todos-meses":
            if df is None:
                return no_update, no_update
            meses_con_datos = sorted(df["Mes"].dropna().astype(int).unique().tolist())
            semanas_auto = sorted(obtener_semanas(df, meses_con_datos))
            return meses_con_datos, semanas_auto

        if trigger == "limpiar-meses":
            return [], []

        mes = int(trigger["index"])

        if df is None:
            if mes in meses_activos:
                meses_activos.remove(mes)
            else:
                meses_activos.append(mes)
            return sorted(meses_activos), no_update

        semanas_del_mes = set(obtener_semanas(df, [mes]))

        if mes in meses_activos:
            meses_activos.remove(mes)
            semanas_activas = [s for s in semanas_activas if s not in semanas_del_mes]
        else:
            meses_activos.append(mes)
            semanas_activas = sorted(set(semanas_activas) | semanas_del_mes)

        return sorted(meses_activos), semanas_activas

    # =====================================================
    # PINTAR MESES
    # =====================================================

    @app.callback(
        Output({"type": "btn-mes", "index": ALL}, "className"),
        Output({"type": "btn-mes", "index": ALL}, "disabled"),
        Input("store-mes", "data"),
        Input("store-bd-ventas", "data"),
    )
    def pintar_meses(meses_activos, marca):
        if meses_activos is None:
            meses_activos = []

        df = _df()
        if df is None:
            meses_con_datos = set()
        else:
            meses_con_datos = set(df["Mes"].dropna().astype(int).unique().tolist())

        clases = []
        deshabilitados = []
        for i in range(1, 13):
            clases.append("cuadro-mes activo" if i in meses_activos else "cuadro-mes")
            deshabilitados.append(i not in meses_con_datos)
        return clases, deshabilitados

    # =====================================================
    # SELECCIÓN DE SEMANAS
    # =====================================================

    @app.callback(
        Output("store-semana", "data", allow_duplicate=True),
        Output("store-mes", "data", allow_duplicate=True),
        Input({"type": "btn-semana", "index": ALL}, "n_clicks"),
        Input("seleccionar-todas-semanas", "n_clicks"),
        Input("limpiar-semanas", "n_clicks"),
        State("store-semana", "data"),
        State("store-mes", "data"),
        prevent_initial_call=True,
    )
    def seleccionar_semanas(_, todo_clicks, limpiar_clicks, semanas_activas, meses_activos):

        if ctx.triggered_id is None:
            return no_update, no_update

        if semanas_activas is None:
            semanas_activas = []
        if meses_activos is None:
            meses_activos = []

        trigger = ctx.triggered_id
        df = _df()

        if trigger == "seleccionar-todas-semanas":
            if df is None:
                return no_update, no_update
            semanas_todas = sorted(df["Semana"].dropna().astype(int).unique().tolist())
            meses_de_esas = sorted(df["Mes"].dropna().astype(int).unique().tolist())
            return semanas_todas, meses_de_esas

        if df is None:
            semanas_visibles = []
        else:
            semanas_visibles = sorted(obtener_semanas(df, meses_activos))

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
            if df is not None:
                fila_semana = df[df["Semana"] == semana]
                if not fila_semana.empty:
                    mes_de_la_semana = int(fila_semana["Mes"].dropna().astype(int).iloc[0])
                    if mes_de_la_semana not in meses_activos:
                        mes_resultado = sorted(meses_activos + [mes_de_la_semana])

        return sorted(semanas_activas), mes_resultado

    # =====================================================
    # PINTAR SEMANAS
    # =====================================================

    @app.callback(
        Output({"type": "btn-semana", "index": ALL}, "className"),
        Output({"type": "btn-semana", "index": ALL}, "disabled"),
        Input("store-semana", "data"),
        Input("store-bd-ventas", "data"),
    )
    def pintar_semanas(semanas_activas, marca):
        if semanas_activas is None:
            semanas_activas = []

        df = _df()
        if df is None:
            semanas_con_datos = set()
        else:
            semanas_con_datos = set(df["Semana"].dropna().astype(int).unique().tolist())

        clases = []
        deshabilitados = []
        for semana in range(1, 54):
            clases.append("cuadro-semana activo" if semana in semanas_activas else "cuadro-semana")
            deshabilitados.append(semana not in semanas_con_datos)
        return clases, deshabilitados