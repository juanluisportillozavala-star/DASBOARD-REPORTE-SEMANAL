"""
=========================================================
CALLBACKS DEL MÓDULO SALDO PROVEEDOR
=========================================================
Selección de SEMANA ÚNICA (una a la vez). Al entrar o cambiar
de año, arranca en la semana MÁS RECIENTE. El MES solo se
resalta; no filtra. El filtrado real es Año + Semana.
"""

from dash import Input, Output, State, ALL, ctx, no_update

import db

MODULO = "saldo_proveedor"
COL_ANIO = "AÑO"
COL_MES = "MES"
COL_SEMANA = "SEMANA"


def _df():
    return db.obtener_df(MODULO)


def _df_anio(anio):
    df = _df()
    if df is None:
        return None
    if anio:
        df = df[df[COL_ANIO] == int(anio)]
    return df


def _semana_reciente(df):
    if df is None or len(df) == 0:
        return None
    ss = df[COL_SEMANA].dropna()
    return int(ss.max()) if len(ss) else None


def _meses_de_semana(df, semana):
    if df is None or semana is None:
        return []
    sub = df[df[COL_SEMANA] == semana]
    return sorted(sub[COL_MES].dropna().astype(int).unique().tolist())


def registrar_callbacks_sp_calendario(app):

    @app.callback(
        Output("store-bd-sp", "data"),
        Output("dropdown-anio-sp", "options"),
        Output("dropdown-anio-sp", "value"),
        Input("store-bd-sp", "data"),
        State("dropdown-anio-sp", "value"),
    )
    def cargar_desde_bd_sp(marca, anio_actual):
        try:
            df = _df()
        except Exception as e:
            print(f">>> [DB] No se pudo leer saldo_proveedor: {e}", flush=True)
            return no_update, no_update, no_update
        if df is None or len(df) == 0:
            return no_update, no_update, no_update

        version = db.version_actual(MODULO)
        anios = sorted([int(a) for a in df[COL_ANIO].dropna().unique().tolist()],
                       reverse=True)
        opciones = [{"label": str(a), "value": a} for a in anios]
        anio_sel = anio_actual if anio_actual in anios else (anios[0] if anios else None)

        if marca and isinstance(marca, dict) and marca.get("version") == version:
            return no_update, opciones, anio_sel
        return {"cargado": True, "version": version}, opciones, anio_sel

    # al cambiar de año (o al cargar) -> semana MÁS RECIENTE
    @app.callback(
        Output("store-semana-sp", "data", allow_duplicate=True),
        Output("store-mes-sp", "data", allow_duplicate=True),
        Input("dropdown-anio-sp", "value"),
        prevent_initial_call=True,
    )
    def al_cambiar_anio(anio):
        df = _df_anio(anio)
        sem = _semana_reciente(df)
        if sem is None:
            return [], []
        return [sem], _meses_de_semana(df, sem)

    # clic en una semana -> selección ÚNICA (reemplaza)
    @app.callback(
        Output("store-semana-sp", "data"),
        Output("store-mes-sp", "data"),
        Input({"type": "btn-semana-sp", "index": ALL}, "n_clicks"),
        State("dropdown-anio-sp", "value"),
        prevent_initial_call=True,
    )
    def seleccionar_semana(_, anio):
        trig = ctx.triggered_id
        if not isinstance(trig, dict):
            return no_update, no_update
        disparo = ctx.triggered[0].get("value") if ctx.triggered else None
        if not disparo:
            return no_update, no_update

        semana = int(trig["index"])
        df = _df_anio(anio)
        if df is not None:
            con_datos = set(df[COL_SEMANA].dropna().astype(int).unique().tolist())
            if semana not in con_datos:
                return no_update, no_update
        return [semana], _meses_de_semana(df, semana)

    # pintar SEMANAS (única activa; deshabilita las sin datos)
    @app.callback(
        Output({"type": "btn-semana-sp", "index": ALL}, "className"),
        Output({"type": "btn-semana-sp", "index": ALL}, "disabled"),
        Input("store-semana-sp", "data"),
        Input("dropdown-anio-sp", "value"),
        Input("store-bd-sp", "data"),
    )
    def pintar_semanas(sel, anio, marca):
        sel = set(sel or [])
        df = _df_anio(anio)
        con = set() if df is None else set(df[COL_SEMANA].dropna().astype(int).unique().tolist())
        clases, deshab = [], []
        for s in range(1, 54):
            clases.append("cuadro-semana activo" if s in sel else "cuadro-semana")
            deshab.append(s not in con)
        return clases, deshab

    # pintar MESES (solo resalta el mes de la semana; no filtra)
    @app.callback(
        Output({"type": "btn-mes-sp", "index": ALL}, "className"),
        Output({"type": "btn-mes-sp", "index": ALL}, "disabled"),
        Input("store-mes-sp", "data"),
        Input("dropdown-anio-sp", "value"),
        Input("store-bd-sp", "data"),
    )
    def pintar_meses(mes_sel, anio, marca):
        mes_sel = set(mes_sel or [])
        df = _df_anio(anio)
        con = set() if df is None else set(df[COL_MES].dropna().astype(int).unique().tolist())
        clases, deshab = [], []
        for i in range(1, 13):
            clases.append("cuadro-mes activo" if i in mes_sel else "cuadro-mes")
            deshab.append(i not in con)
        return clases, deshab