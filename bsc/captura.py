"""
=========================================================
bsc/captura.py  —  CAPTURA UNIFICADA del BSC (admin)
=========================================================
Una sola pantalla con DOS tablas:

  1) OBJETIVOS (arriba): Indicador | Obj. anual | Ene..Dic
     - Se teclea la meta de cada mes.
     - El "Obj. anual" se calcula solo (flujo=suma, saldo=último).
     - Los padres (Venta, Utilidad…) se calculan por suma de hijos.

  2) REALES POR SEMANA (abajo): Indicador | Objetivo | Sem 1..N | Acumulado
     - Se elige un mes y se teclean los valores reales por semana.
     - "Objetivo" es el objetivo de ESE mes (de la tabla de arriba).
     - "Acumulado" se calcula solo (flujo=suma, saldo=última semana).

Guarda todo con un botón. Solo edita admin (candado en servidor).
Se recalcula al Guardar (opción estable).
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag

from bsc import catalogo, datos
from bsc import semanas as S

AZUL = "#173C73"
DORADO = "#D4AF37"

MESES = [(1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
         (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
         (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"),
         (12, "Diciembre")]
_MES_NOMBRE = dict(MESES)
MESES_COL = [(1, "Ene"), (2, "Feb"), (3, "Mar"), (4, "Abr"),
             (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Ago"),
             (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dic")]

_FMT_VALOR = {"function": (
    "params.value == null || params.value === '' ? '' : "
    "(params.data.unidad === 'Días' "
    "  ? Math.round(params.value).toLocaleString('en-US') + ' d' "
    "  : Math.round(params.value).toLocaleString('en-US'))"
)}

# --- estilos de celda ---
_CELL_INDICADOR = {"function": (
    "params.data.es_titulo ? "
    "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : "
    "(params.data.nivel === 1 ? "
    "  {color:'#5A6472', paddingLeft:'26px'} : "
    "  {fontWeight:'700', color:'#173C73'})"
)}
# editable solo si NO es título (los padres se calculan)
_EDITABLE = {"function": "!params.data.es_titulo"}
# celda editable: crema si capturable; gris (calculada) si título
_CELL_EDIT = {"function": (
    "params.data.es_titulo ? "
    "{backgroundColor:'#EFF2F7', fontWeight:'700', color:'#173C73'} : "
    "{backgroundColor:'#FFFDF5'}"
)}
# columnas calculadas (anual / acumulado): siempre gris, azul, negrita
_CELL_CALC = {"function":
    "{backgroundColor:'#EFF2F7', fontWeight:'700', color:'#173C73'}"}


def _estilo_grid(alto):
    return {
        "width": "100%", "height": alto,
        "--ag-font-size": "13px",
        "--ag-header-background-color": AZUL,
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-row-hover-color": "#EEF3FA",
    }


# =========================================================
# LAYOUT
# =========================================================

def crear_panel_captura_bsc():
    anios_guardados = datos.anios_con_bsc()
    anios = sorted(set(list(range(2025, 2036)) + anios_guardados), reverse=True)
    anio_val = anios_guardados[0] if anios_guardados else 2026

    return html.Div(
        [
            html.P("Aquí defines las metas del año (tabla de arriba) y "
                   "capturas los reales por semana de cada mes (tabla de "
                   "abajo). Los totales se calculan solos. Pica «Guardar».",
                   className="subtitulo"),

            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="bsc-cap-anio",
                                options=[{"label": str(a), "value": a}
                                         for a in anios],
                                value=anio_val, clearable=False,
                                style={"width": "140px"}),
                        ],
                    ),
                    html.Button("Guardar todo", id="bsc-cap-guardar", n_clicks=0,
                                className="btn btn-primary",
                                style={"height": "40px", "padding": "0 26px"}),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "16px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            html.Div(id="bsc-cap-msg",
                     style={"marginBottom": "12px", "fontWeight": "600"}),

            # ---- TABLA 1: OBJETIVOS ANUALES ----
            html.H4("Objetivos del año (metas por mes)",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "8px"}),
            html.P("Teclea la meta de cada mes; el «Obj. anual» se calcula "
                   "solo.", style={"color": "#6C757D", "fontSize": "13px",
                                   "marginBottom": "8px"}),
            html.Div(id="bsc-cap-obj-cont"),

            html.Br(),

            # ---- TABLA 2: REALES POR SEMANA ----
            html.H4("Captura semanal (valores reales)",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "8px"}),
            html.Div(
                [
                    html.Label("Mes", style={"fontWeight": "600", "color": AZUL,
                                             "marginRight": "10px"}),
                    dcc.Dropdown(
                        id="bsc-cap-mes",
                        options=[{"label": n, "value": m} for m, n in MESES],
                        value=1, clearable=False,
                        style={"width": "180px", "display": "inline-block"}),
                ],
                style={"display": "flex", "alignItems": "center",
                       "marginBottom": "10px"},
            ),
            html.Div(id="bsc-cap-sem-cont"),
        ]
    )


# =========================================================
# TABLA 1 — OBJETIVOS
# =========================================================

def _obj_column_defs():
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 240,
         "pinned": "left", "editable": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_INDICADOR},
        {"field": "anual", "headerName": "Obj. anual", "editable": False,
         "type": "numericColumn", "valueFormatter": _FMT_VALOR,
         "minWidth": 130, "pinned": "left", "headerClass": "hdr-bsc",
         "cellStyle": _CELL_CALC},
    ]
    for m, nombre in MESES_COL:
        cols.append({
            "field": f"m_{m}", "headerName": nombre, "editable": _EDITABLE,
            "type": "numericColumn", "minWidth": 85, "headerClass": "hdr-bsc",
            "cellStyle": _CELL_EDIT})
    return cols


def _obj_filas(anio):
    from bsc.logica import formular_objetivos
    porm = datos.leer_objetivos_anio(anio)
    porm = formular_objetivos(porm)
    filas = []
    for ind in catalogo.indicadores():
        iid = ind["id"]
        es_titulo = not ind["capturable"]
        fila = {"id": iid, "indicador": ind["nombre"], "unidad": ind["unidad"],
                "es_titulo": es_titulo, "nivel": ind["nivel"],
                "anual": porm.get(0, {}).get(iid)}
        for m, _ in MESES_COL:
            fila[f"m_{m}"] = porm.get(m, {}).get(iid)
        filas.append(fila)
    return filas


def _grid_objetivos(anio):
    return dag.AgGrid(
        id="bsc-cap-obj-grid",
        rowData=_obj_filas(anio),
        columnDefs=_obj_column_defs(),
        defaultColDef={"resizable": True, "sortable": False,
                       "filter": False, "flex": 1, "minWidth": 80},
        dashGridOptions={"animateRows": False, "rowHeight": 30,
                         "headerHeight": 38, "singleClickEdit": False,
                         "domLayout": "autoHeight",
                         "suppressCellFocus": False},
        className="ag-theme-alpine",
        style={"width": "100%", "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


# =========================================================
# TABLA 2 — REALES POR SEMANA
# =========================================================

def _sem_column_defs(sems):
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 240,
         "pinned": "left", "editable": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_INDICADOR},
        {"field": "objetivo", "headerName": "Obj. mensual", "editable": False,
         "type": "numericColumn", "valueFormatter": _FMT_VALOR,
         "minWidth": 120, "pinned": "left", "headerClass": "hdr-bsc",
         "cellStyle": _CELL_CALC},
    ]
    # por cada semana: un grupo con dos columnas (Obj | Real)
    for s in sems:
        cols.append({
            "headerName": s["label"],
            "headerClass": "hdr-bsc",
            "children": [
                {"field": f"obj_{s['num']}", "headerName": "Obj",
                 "editable": _EDITABLE, "type": "numericColumn",
                 "minWidth": 80, "headerClass": "hdr-bsc",
                 "cellStyle": _CELL_EDIT},
                {"field": f"sem_{s['num']}", "headerName": "Real",
                 "editable": _EDITABLE, "type": "numericColumn",
                 "minWidth": 80, "headerClass": "hdr-bsc",
                 "cellStyle": _CELL_EDIT},
            ],
        })
    cols.append(
        {"field": "acumulado", "headerName": "Acum. real", "editable": False,
         "type": "numericColumn", "valueFormatter": _FMT_VALOR,
         "minWidth": 120, "pinned": "right", "headerClass": "hdr-bsc",
         "cellStyle": _CELL_CALC})
    return cols


def _sem_filas(anio, mes):
    from bsc.logica import construir_bsc
    objetivos = datos.leer_objetivos(anio, mes)
    captura = datos.leer_captura(anio, mes)            # solo real (para acum)
    completa = datos.leer_captura_completa(anio, mes)  # real + obj por semana
    sems = S.semanas_del_mes(anio, mes)
    filas_calc, _, _ = construir_bsc(anio, mes, objetivos, captura)
    calc_por_id = {f["id"]: f for f in filas_calc}

    filas = []
    for ind in catalogo.indicadores():
        iid = ind["id"]
        es_titulo = not ind["capturable"]
        c = calc_por_id.get(iid, {})
        fila = {"id": iid, "indicador": ind["nombre"], "unidad": ind["unidad"],
                "es_titulo": es_titulo, "nivel": ind["nivel"],
                "objetivo": objetivos.get(iid), "acumulado": c.get("acumulado")}
        semvals = completa.get(iid, {})
        for s in sems:
            celda = semvals.get(s["num"], {})
            fila[f"sem_{s['num']}"] = None if es_titulo else celda.get("real")
            fila[f"obj_{s['num']}"] = None if es_titulo else celda.get("obj")
        filas.append(fila)
    return filas, sems


def _grid_semanal(anio, mes):
    filas, sems = _sem_filas(anio, mes)
    return dag.AgGrid(
        id="bsc-cap-sem-grid",
        rowData=filas,
        columnDefs=_sem_column_defs(sems),
        defaultColDef={"resizable": True, "sortable": False,
                       "filter": False, "flex": 1, "minWidth": 90},
        dashGridOptions={"animateRows": False, "rowHeight": 30,
                         "headerHeight": 38, "singleClickEdit": False,
                         "domLayout": "autoHeight",
                         "suppressCellFocus": False},
        className="ag-theme-alpine",
        style={"width": "100%", "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


# =========================================================
# CALLBACKS
# =========================================================

def registrar_callbacks_bsc_captura(app):

    # construir tabla de objetivos al cambiar año
    @app.callback(
        Output("bsc-cap-obj-cont", "children"),
        Input("bsc-cap-anio", "value"),
    )
    def _obj(anio):
        if not anio:
            return html.Div("Selecciona un año.", style={"color": "#6C757D"})
        return _grid_objetivos(anio)

    # construir tabla semanal al cambiar año o mes
    @app.callback(
        Output("bsc-cap-sem-cont", "children"),
        Input("bsc-cap-anio", "value"),
        Input("bsc-cap-mes", "value"),
    )
    def _sem(anio, mes):
        if not anio or not mes:
            return html.Div("Selecciona año y mes.", style={"color": "#6C757D"})
        return _grid_semanal(anio, mes)

    # GUARDAR TODO: objetivos (recalculados) + captura semanal del mes
    @app.callback(
        Output("bsc-cap-msg", "children"),
        Input("bsc-cap-guardar", "n_clicks"),
        State("bsc-cap-obj-grid", "rowData"),
        State("bsc-cap-sem-grid", "rowData"),
        State("bsc-cap-anio", "value"),
        State("bsc-cap-mes", "value"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def _guardar(n, obj_rows, sem_rows, anio, mes, sesion):
        if not n or not anio:
            return no_update
        if not (sesion and sesion.get("rol") == "admin"):
            return html.Span("Solo un administrador puede guardar.",
                             style={"color": "#C0392B"})

        from bsc.logica import formular_objetivos

        # 1) OBJETIVOS: recoger lo tecleado (meses de hijos/principales)
        tecleado = {}
        for fila in (obj_rows or []):
            iid = fila.get("id")
            if not iid or fila.get("es_titulo"):
                continue
            for m, _ in MESES_COL:
                v = fila.get(f"m_{m}")
                if v not in (None, ""):
                    tecleado.setdefault(m, {})[iid] = v
        completo = formular_objetivos(tecleado)
        valores_obj = []
        for m in range(0, 13):
            for iid, v in completo.get(m, {}).items():
                valores_obj.append((m, iid, v))

        # 2) CAPTURA SEMANAL del mes (objetivo semanal + real semanal)
        sems = S.semanas_del_mes(anio, mes)
        valores_cap = []
        for fila in (sem_rows or []):
            iid = fila.get("id")
            if not iid or fila.get("es_titulo"):
                continue
            for s in sems:
                real = fila.get(f"sem_{s['num']}")
                obj = fila.get(f"obj_{s['num']}")
                valores_cap.append((iid, s["num"], real, obj))

        try:
            datos.guardar_objetivos_anio(anio, valores_obj, reemplazar_anio=True)
            datos.guardar_captura(anio, mes, valores_cap)
        except Exception as e:
            return html.Span(f"Error al guardar: {e}",
                             style={"color": "#C0392B"})

        return html.Span(
            f"✓ Guardado: objetivos {anio} y captura de "
            f"{_MES_NOMBRE.get(int(mes), mes)}.",
            style={"color": "#1E8449"})