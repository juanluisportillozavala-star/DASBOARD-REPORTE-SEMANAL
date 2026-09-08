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

# Al editar, quitar comas/espacios y convertir a número (para que
# las celdas con formato de miles se puedan editar sin romperse).
_PARSER_NUM = {"function": (
    "params.newValue == null || params.newValue === '' ? null : "
    "Number(String(params.newValue).replace(/[,\\s]/g,''))"
)}

# --- estilos de celda ---
_CELL_INDICADOR = {"function": (
    "params.data.es_titulo ? "
    "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : "
    "(params.data.nivel === 2 ? "
    "  {color:'#7A8698', paddingLeft:'48px'} : "
    " (params.data.nivel === 1 ? "
    "  {color:'#5A6472', paddingLeft:'26px'} : "
    "  {fontWeight:'700', color:'#173C73'}))"
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
                    html.Button("📋 Pegar desde Excel", id="bsc-cap-pegar-btn",
                                n_clicks=0, className="btn",
                                style={"marginLeft": "16px", "height": "38px",
                                       "border": "1.5px solid #173C73",
                                       "color": "#173C73", "background": "#FFFFFF",
                                       "borderRadius": "8px", "fontWeight": "600",
                                       "cursor": "pointer", "padding": "0 16px"}),
                ],
                style={"display": "flex", "alignItems": "center",
                       "marginBottom": "10px", "flexWrap": "wrap"},
            ),
            # zona de pegado (oculta hasta picar el botón)
            html.Div(
                id="bsc-cap-pegar-zona",
                style={"display": "none", "marginBottom": "12px"},
                children=[
                    html.P("Copia el bloque de celdas desde Excel y pégalo aquí "
                           "(Ctrl+V). Debe tener las mismas columnas que la tabla "
                           "de abajo (Obj y Real por semana). Luego pica «Aplicar».",
                           style={"color": "#6C757D", "fontSize": "13px",
                                  "marginBottom": "6px"}),
                    dcc.Textarea(
                        id="bsc-cap-pegar-texto",
                        placeholder="Pega aquí (Ctrl+V)…",
                        style={"width": "100%", "height": "120px",
                               "fontFamily": "monospace", "fontSize": "13px",
                               "border": "1px solid #CBD5E1",
                               "borderRadius": "8px", "padding": "8px"}),
                    html.Button("Aplicar", id="bsc-cap-pegar-aplicar", n_clicks=0,
                                className="btn btn-primary",
                                style={"marginTop": "8px", "height": "38px",
                                       "padding": "0 22px"}),
                    html.Span(id="bsc-cap-pegar-msg",
                              style={"marginLeft": "12px", "fontWeight": "600"}),
                ],
            ),
            # ---- barra de RELLENADO rápido (mismo valor en varias celdas) ----
            html.Div(
                [
                    html.Span("Rellenar:", style={"fontWeight": "700",
                                                  "color": AZUL,
                                                  "marginRight": "8px"}),
                    dcc.Dropdown(id="bsc-cap-fill-ind", options=[],
                                 placeholder="Indicador (o todos)",
                                 style={"width": "230px"}),
                    dcc.Dropdown(id="bsc-cap-fill-sem", options=[],
                                 placeholder="Semana (o todas)",
                                 style={"width": "150px"}),
                    dcc.Dropdown(id="bsc-cap-fill-tipo",
                                 options=[{"label": "Obj", "value": "obj"},
                                          {"label": "Real", "value": "real"},
                                          {"label": "Ambos", "value": "ambos"}],
                                 value="real", clearable=False,
                                 style={"width": "110px"}),
                    dcc.Input(id="bsc-cap-fill-valor", type="number",
                              placeholder="Valor",
                              style={"width": "130px", "height": "36px",
                                     "borderRadius": "6px",
                                     "border": "1px solid #CBD5E1",
                                     "padding": "0 10px"}),
                    html.Button("Rellenar", id="bsc-cap-fill-btn", n_clicks=0,
                                className="btn btn-primary",
                                style={"height": "38px", "padding": "0 20px"}),
                    html.Span(id="bsc-cap-fill-msg",
                              style={"marginLeft": "10px", "fontWeight": "600"}),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "8px",
                       "flexWrap": "wrap", "marginBottom": "10px",
                       "padding": "10px", "background": "#F8FAFD",
                       "borderRadius": "8px"},
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
            "type": "numericColumn", "valueFormatter": _FMT_VALOR,
            "valueParser": _PARSER_NUM,
            "minWidth": 85, "headerClass": "hdr-bsc",
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
                         "headerHeight": 38, "singleClickEdit": True,
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
                 "valueFormatter": _FMT_VALOR, "valueParser": _PARSER_NUM,
                 "minWidth": 80, "headerClass": "hdr-bsc",
                 "cellStyle": _CELL_EDIT},
                {"field": f"sem_{s['num']}", "headerName": "Real",
                 "editable": _EDITABLE, "type": "numericColumn",
                 "valueFormatter": _FMT_VALOR, "valueParser": _PARSER_NUM,
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
                         "headerHeight": 38, "singleClickEdit": True,
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

    # ---- mostrar/ocultar la zona de pegado ----
    @app.callback(
        Output("bsc-cap-pegar-zona", "style"),
        Input("bsc-cap-pegar-btn", "n_clicks"),
        State("bsc-cap-pegar-zona", "style"),
        prevent_initial_call=True,
    )
    def _toggle_pegar(n, style):
        style = dict(style or {})
        visible = style.get("display") != "none"
        style["display"] = "none" if visible else "block"
        style["marginBottom"] = "12px"
        return style

    # ---- aplicar el bloque pegado desde Excel al grid semanal ----
    # El texto de Excel trae TABS entre columnas y saltos de línea
    # entre filas. Cada fila corresponde, EN ORDEN, a las filas
    # capturables visibles del grid (mismas que se ven en pantalla).
    @app.callback(
        Output("bsc-cap-sem-grid", "rowData", allow_duplicate=True),
        Output("bsc-cap-pegar-msg", "children"),
        Input("bsc-cap-pegar-aplicar", "n_clicks"),
        State("bsc-cap-pegar-texto", "value"),
        State("bsc-cap-sem-grid", "rowData"),
        State("bsc-cap-anio", "value"),
        State("bsc-cap-mes", "value"),
        prevent_initial_call=True,
    )
    def _aplicar_pegado(n, texto, rowdata, anio, mes):
        if not n or not texto or not rowdata:
            return no_update, ""
        sems = S.semanas_del_mes(anio, mes)
        # columnas editables por fila, EN ORDEN: obj y real por semana
        campos = []
        for s in sems:
            campos.append(f"obj_{s['num']}")
            campos.append(f"sem_{s['num']}")

        # parsear el texto pegado
        lineas = [ln for ln in texto.replace("\r", "").split("\n") if ln.strip() != ""]
        if not lineas:
            return no_update, html.Span("No se detectó contenido.",
                                        style={"color": "#C0392B"})

        # filas capturables del grid, en el mismo orden visual
        idx_capturables = [i for i, f in enumerate(rowdata)
                           if not f.get("es_titulo")]

        def _num(x):
            x = (x or "").strip().replace(",", "").replace("$", "")
            if x == "":
                return None
            try:
                return float(x)
            except ValueError:
                return None

        aplicadas = 0
        for li, linea in enumerate(lineas):
            if li >= len(idx_capturables):
                break
            celdas = linea.split("\t")
            fila = rowdata[idx_capturables[li]]
            for ci, campo in enumerate(campos):
                if ci < len(celdas):
                    fila[campo] = _num(celdas[ci])
            aplicadas += 1

        return rowdata, html.Span(
            f"✓ {aplicadas} fila(s) aplicadas. Revisa y pica «Guardar todo».",
            style={"color": "#1E8449"})

    # ---- llenar opciones de indicador y semana para el rellenado ----
    @app.callback(
        Output("bsc-cap-fill-ind", "options"),
        Output("bsc-cap-fill-sem", "options"),
        Input("bsc-cap-anio", "value"),
        Input("bsc-cap-mes", "value"),
    )
    def _fill_opciones(anio, mes):
        # indicadores capturables (los que se teclean)
        inds = [{"label": "— Todos los indicadores —", "value": "__todos__"}]
        for ind in catalogo.capturables():
            sangria = "    " if ind["nivel"] >= 1 else ""
            inds.append({"label": sangria + ind["nombre"], "value": ind["id"]})
        # semanas del mes
        sems = [{"label": "— Todas las semanas —", "value": "__todas__"}]
        if anio and mes:
            for s in S.semanas_del_mes(anio, mes):
                sems.append({"label": f"Sem {s['label']}", "value": s["num"]})
        return inds, sems

    # ---- aplicar el rellenado al grid semanal ----
    @app.callback(
        Output("bsc-cap-sem-grid", "rowData", allow_duplicate=True),
        Output("bsc-cap-fill-msg", "children"),
        Input("bsc-cap-fill-btn", "n_clicks"),
        State("bsc-cap-fill-ind", "value"),
        State("bsc-cap-fill-sem", "value"),
        State("bsc-cap-fill-tipo", "value"),
        State("bsc-cap-fill-valor", "value"),
        State("bsc-cap-sem-grid", "rowData"),
        State("bsc-cap-anio", "value"),
        State("bsc-cap-mes", "value"),
        prevent_initial_call=True,
    )
    def _aplicar_relleno(n, ind_sel, sem_sel, tipo, valor, rowdata, anio, mes):
        if not n or not rowdata:
            return no_update, ""
        if valor is None or valor == "":
            return no_update, html.Span("Escribe un valor.",
                                        style={"color": "#C0392B"})
        try:
            v = float(valor)
        except (ValueError, TypeError):
            return no_update, html.Span("Valor inválido.",
                                        style={"color": "#C0392B"})

        sems = S.semanas_del_mes(anio, mes)
        # qué semanas: una o todas
        nums = ([int(sem_sel)] if sem_sel not in (None, "__todas__")
                else [s["num"] for s in sems])
        # qué campos según tipo (obj / real / ambos)
        def _campos(num):
            if tipo == "obj":
                return [f"obj_{num}"]
            if tipo == "real":
                return [f"sem_{num}"]
            return [f"obj_{num}", f"sem_{num}"]

        tocadas = 0
        for fila in rowdata:
            if fila.get("es_titulo"):
                continue
            if ind_sel not in (None, "__todos__") and fila.get("id") != ind_sel:
                continue
            for num in nums:
                for campo in _campos(num):
                    fila[campo] = v
                    tocadas += 1

        if tocadas == 0:
            return no_update, html.Span("Nada que rellenar (revisa la selección).",
                                        style={"color": "#B7791F"})
        return rowdata, html.Span(
            f"✓ {tocadas} celda(s) rellenadas. Revisa y «Guardar todo».",
            style={"color": "#1E8449"})