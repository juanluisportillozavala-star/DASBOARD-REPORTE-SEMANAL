"""
=========================================================
CALLBACKS DEL MÓDULO CARTERA
=========================================================
Calendario Mes/Semana propio (IDs con sufijo -cartera) + AÑO
como filtro maestro (dropdown, arranca en el más reciente).
Mes/semana operan dentro del año elegido.

Los datos se leen de la CACHÉ del servidor (db.obtener_df) del
módulo "cartera". Columnas AÑO / MES / SEMANA las genera
cartera/procesamiento.py desde la columna Fecha.
"""

from dash import Input, Output, State, ALL, ctx, no_update

import db

MODULO = "cartera"
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


def _semanas_de_meses(df, meses):
    if df is None or not meses:
        return []
    sub = df[df[COL_MES].isin(meses)]
    return sub[COL_SEMANA].dropna().astype(int).unique().tolist()


def registrar_callbacks_cartera(app):

    # cargar señal + llenar dropdown de AÑOS
    @app.callback(
        Output("store-bd-cartera", "data"),
        Output("dropdown-anio-cartera", "options"),
        Output("dropdown-anio-cartera", "value"),
        Input("store-bd-cartera", "data"),
        State("dropdown-anio-cartera", "value"),
    )
    def cargar_desde_bd_cartera(marca, anio_actual):
        try:
            df = _df()
        except Exception as e:
            print(f">>> [DB] No se pudo leer cartera: {e}", flush=True)
            return no_update, no_update, no_update
        if df is None or len(df) == 0:
            return no_update, no_update, no_update

        version = db.version_actual(MODULO)
        anios = sorted(
            [int(a) for a in df[COL_ANIO].dropna().unique().tolist()],
            reverse=True,
        )
        opciones = [{"label": str(a), "value": a} for a in anios]
        anio_sel = anio_actual if anio_actual in anios else (anios[0] if anios else None)

        if marca and isinstance(marca, dict) and marca.get("version") == version:
            return no_update, opciones, anio_sel
        return {"cargado": True, "version": version}, opciones, anio_sel

    # cambio de año -> reiniciar mes/semana
    @app.callback(
        Output("store-mes-cartera", "data", allow_duplicate=True),
        Output("store-semana-cartera", "data", allow_duplicate=True),
        Input("dropdown-anio-cartera", "value"),
        prevent_initial_call=True,
    )
    def reiniciar_al_cambiar_anio(anio):
        return [], []

    # selección de meses
    @app.callback(
        Output("store-mes-cartera", "data"),
        Output("store-semana-cartera", "data"),
        Input({"type": "btn-mes-cartera", "index": ALL}, "n_clicks"),
        Input("seleccionar-todos-meses-cartera", "n_clicks"),
        Input("limpiar-meses-cartera", "n_clicks"),
        State("store-mes-cartera", "data"),
        State("store-semana-cartera", "data"),
        State("dropdown-anio-cartera", "value"),
        prevent_initial_call=True,
    )
    def seleccionar_meses(_, todo, limpiar, meses_activos, semanas_activas, anio):
        if ctx.triggered_id is None:
            return no_update, no_update
        if meses_activos is None:
            meses_activos = []
        if semanas_activas is None:
            semanas_activas = []

        trigger = ctx.triggered_id
        df = _df_anio(anio)

        if trigger == "seleccionar-todos-meses-cartera":
            if df is None:
                return no_update, no_update
            meses = sorted(df[COL_MES].dropna().astype(int).unique().tolist())
            semanas = sorted(_semanas_de_meses(df, meses))
            return meses, semanas

        if trigger == "limpiar-meses-cartera":
            return [], []

        mes = int(trigger["index"])
        if df is None:
            if mes in meses_activos:
                meses_activos.remove(mes)
            else:
                meses_activos.append(mes)
            return sorted(meses_activos), no_update

        semanas_del_mes = set(_semanas_de_meses(df, [mes]))
        if mes in meses_activos:
            meses_activos.remove(mes)
            semanas_activas = [s for s in semanas_activas if s not in semanas_del_mes]
        else:
            meses_activos.append(mes)
            semanas_activas = sorted(set(semanas_activas) | semanas_del_mes)

        return sorted(meses_activos), semanas_activas

    # pintar meses
    @app.callback(
        Output({"type": "btn-mes-cartera", "index": ALL}, "className"),
        Output({"type": "btn-mes-cartera", "index": ALL}, "disabled"),
        Input("store-mes-cartera", "data"),
        Input("dropdown-anio-cartera", "value"),
        Input("store-bd-cartera", "data"),
    )
    def pintar_meses(meses_activos, anio, marca):
        if meses_activos is None:
            meses_activos = []
        df = _df_anio(anio)
        con_datos = set() if df is None else set(df[COL_MES].dropna().astype(int).unique().tolist())
        clases, deshab = [], []
        for i in range(1, 13):
            clases.append("cuadro-mes activo" if i in meses_activos else "cuadro-mes")
            deshab.append(i not in con_datos)
        return clases, deshab

    # selección de semanas
    @app.callback(
        Output("store-semana-cartera", "data", allow_duplicate=True),
        Output("store-mes-cartera", "data", allow_duplicate=True),
        Input({"type": "btn-semana-cartera", "index": ALL}, "n_clicks"),
        Input("seleccionar-todas-semanas-cartera", "n_clicks"),
        Input("limpiar-semanas-cartera", "n_clicks"),
        State("store-semana-cartera", "data"),
        State("store-mes-cartera", "data"),
        State("dropdown-anio-cartera", "value"),
        prevent_initial_call=True,
    )
    def seleccionar_semanas(_, todo, limpiar, semanas_activas, meses_activos, anio):
        if ctx.triggered_id is None:
            return no_update, no_update
        if semanas_activas is None:
            semanas_activas = []
        if meses_activos is None:
            meses_activos = []

        trigger = ctx.triggered_id
        df = _df_anio(anio)

        if trigger == "seleccionar-todas-semanas-cartera":
            if df is None:
                return no_update, no_update
            semanas = sorted(df[COL_SEMANA].dropna().astype(int).unique().tolist())
            meses = sorted(df[COL_MES].dropna().astype(int).unique().tolist())
            return semanas, meses

        if trigger == "limpiar-semanas-cartera":
            return [], []

        semana = int(trigger["index"])
        mes_result = no_update

        if semana in semanas_activas:
            # QUITAR (cualquiera, incluida la primera)
            semanas_activas.remove(semana)
            if df is not None:
                fila = df[df[COL_SEMANA] == semana]
                if not fila.empty:
                    mes_de = int(fila[COL_MES].dropna().astype(int).iloc[0])
                    semanas_de_ese_mes = set(_semanas_de_meses(df, [mes_de]))
                    quedan = [s for s in semanas_activas if s in semanas_de_ese_mes]
                    if not quedan and mes_de in meses_activos:
                        mes_result = sorted([m for m in meses_activos if m != mes_de])
        else:
            # AGREGAR (enciende su mes si no estaba)
            semanas_activas.append(semana)
            if df is not None:
                fila = df[df[COL_SEMANA] == semana]
                if not fila.empty:
                    mes_de = int(fila[COL_MES].dropna().astype(int).iloc[0])
                    if mes_de not in meses_activos:
                        mes_result = sorted(meses_activos + [mes_de])

        return sorted(semanas_activas), mes_result

    # pintar semanas
    @app.callback(
        Output({"type": "btn-semana-cartera", "index": ALL}, "className"),
        Output({"type": "btn-semana-cartera", "index": ALL}, "disabled"),
        Input("store-semana-cartera", "data"),
        Input("dropdown-anio-cartera", "value"),
        Input("store-bd-cartera", "data"),
    )
    def pintar_semanas(semanas_activas, anio, marca):
        if semanas_activas is None:
            semanas_activas = []
        df = _df_anio(anio)
        con_datos = set() if df is None else set(df[COL_SEMANA].dropna().astype(int).unique().tolist())
        clases, deshab = [], []
        for s in range(1, 54):
            clases.append("cuadro-semana activo" if s in semanas_activas else "cuadro-semana")
            deshab.append(s not in con_datos)
        return clases, deshab