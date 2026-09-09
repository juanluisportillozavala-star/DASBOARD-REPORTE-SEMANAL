"""
=========================================================
bsc/captura.py  —  CAPTURA de OBJETIVOS del BSC (admin)
=========================================================
Una sola tabla: OBJETIVOS del año.
  Indicador | Obj. anual | Ene..Dic
  - Se teclea la meta de cada mes (doble clic para editar).
  - El "Obj. anual" se calcula solo (flujo=suma, saldo=último).
  - Los padres (Venta, Utilidad…) se calculan por suma de hijos.
  - Fórmulas: Ciclo efectivo, Ut. Operativa, Capital de trabajo.

Barra "Rellenar" para poner el mismo valor en varios meses.
Guarda con un botón. Solo edita admin (candado en servidor).
Se recalcula al Guardar.

NOTA: la captura semanal de valores REALES se retiró. Los
indicadores reales se alimentan del auto (Ventas, Cartera, …) o
quedan pendientes de conectar.
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag

from bsc import catalogo, datos

AZUL = "#173C73"
DORADO = "#D4AF37"

MESES_COL = [(1, "Ene"), (2, "Feb"), (3, "Mar"), (4, "Abr"),
             (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Ago"),
             (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dic")]

_FMT_VALOR = {"function": (
    "params.value == null || params.value === '' ? '' : "
    "(params.data.unidad === 'Días' "
    "  ? Math.round(params.value).toLocaleString('en-US') + ' d' "
    "  : Math.round(params.value).toLocaleString('en-US'))"
)}

_PARSER_NUM = {"function": (
    "(function(){"
    " var t = params.newValue;"
    " if (t == null || String(t).trim() === '') return null;"
    " var n = Number(String(t).replace(/[,$\\s]/g, ''));"
    " return isNaN(n) ? null : n;"
    "})()"
)}

_CELL_INDICADOR = {"function": (
    "params.data.es_titulo ? "
    "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : "
    "(params.data.nivel === 2 ? "
    "  {color:'#7A8698', paddingLeft:'48px'} : "
    " (params.data.nivel === 1 ? "
    "  {color:'#5A6472', paddingLeft:'26px'} : "
    "  {fontWeight:'700', color:'#173C73'}))"
)}
_EDITABLE = {"function": "!params.data.es_titulo"}
_CELL_EDIT = {"function": (
    "params.data.es_titulo ? "
    "{backgroundColor:'#EFF2F7', fontWeight:'700', color:'#173C73'} : "
    "{backgroundColor:'#FFFDF5'}"
)}
_CELL_ANUAL_CALC = {"function":
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
            html.P("Define las metas del año. Teclea la meta de cada mes "
                   "(doble clic en la celda); los totales se calculan solos. "
                   "Pica «Guardar».",
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
                    html.Button("Guardar", id="bsc-cap-guardar", n_clicks=0,
                                className="btn btn-primary",
                                style={"height": "40px", "padding": "0 26px"}),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "16px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            html.Div(id="bsc-cap-msg",
                     style={"marginBottom": "12px", "fontWeight": "600"}),

            html.H4("Objetivos del año (metas por mes)",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "8px"}),
            html.P("Teclea la meta de cada mes; el «Obj. anual» se calcula solo.",
                   style={"color": "#6C757D", "fontSize": "13px",
                          "marginBottom": "8px"}),

            # ---- barra de RELLENADO (misma meta en varios meses) ----
            html.Div(
                [
                    html.Span("Rellenar:", style={"fontWeight": "700",
                                                  "color": AZUL,
                                                  "marginRight": "8px"}),
                    dcc.Dropdown(id="bsc-cap-ofill-ind", options=[],
                                 placeholder="Indicador (o todos)",
                                 style={"width": "230px"}),
                    dcc.Dropdown(id="bsc-cap-ofill-mes", options=[],
                                 placeholder="Mes (o todos)",
                                 style={"width": "150px"}),
                    dcc.Input(id="bsc-cap-ofill-valor", type="number",
                              placeholder="Valor",
                              style={"width": "130px", "height": "36px",
                                     "borderRadius": "6px",
                                     "border": "1px solid #CBD5E1",
                                     "padding": "0 10px"}),
                    html.Button("Rellenar", id="bsc-cap-ofill-btn", n_clicks=0,
                                className="btn btn-primary",
                                style={"height": "38px", "padding": "0 20px"}),
                    html.Span(id="bsc-cap-ofill-msg",
                              style={"marginLeft": "10px", "fontWeight": "600"}),
                ],
                style={"display": "flex", "alignItems": "center", "gap": "8px",
                       "flexWrap": "wrap", "marginBottom": "10px",
                       "padding": "10px", "background": "#F8FAFD",
                       "borderRadius": "8px"},
            ),

            # ---- Pegar desde Excel ----
            html.Button("📋 Pegar desde Excel", id="bsc-cap-pegar-btn",
                        n_clicks=0, className="btn",
                        style={"marginBottom": "8px", "height": "38px",
                               "border": "1.5px solid #173C73",
                               "color": "#173C73", "background": "#FFFFFF",
                               "borderRadius": "8px", "fontWeight": "600",
                               "cursor": "pointer", "padding": "0 16px"}),
            html.Div(
                id="bsc-cap-pegar-zona",
                style={"display": "none", "marginBottom": "12px"},
                children=[
                    html.P("Copia de Excel el bloque de metas mensuales (una fila "
                           "por indicador, columnas = Ene…Dic) y pégalo aquí "
                           "(Ctrl+V). Elige desde qué indicador empezar y «Aplicar».",
                           style={"color": "#6C757D", "fontSize": "13px",
                                  "marginBottom": "6px"}),
                    html.Div(
                        [
                            html.Span("Empezar a pegar desde:",
                                      style={"fontWeight": "600", "color": AZUL,
                                             "marginRight": "8px"}),
                            dcc.Dropdown(id="bsc-cap-pegar-desde", options=[],
                                         placeholder="Indicador inicial",
                                         style={"width": "280px"}),
                        ],
                        style={"display": "flex", "alignItems": "center",
                               "marginBottom": "8px"},
                    ),
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

            html.Div(id="bsc-cap-obj-cont"),
        ]
    )


# =========================================================
# TABLA DE OBJETIVOS
# =========================================================

def _obj_column_defs():
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 240,
         "pinned": "left", "editable": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_INDICADOR},
        {"field": "anual", "headerName": "Obj. anual", "editable": False,
         "type": "numericColumn", "valueFormatter": _FMT_VALOR,
         "minWidth": 130, "pinned": "left", "headerClass": "hdr-bsc",
         "cellStyle": _CELL_ANUAL_CALC},
    ]
    for m, nombre in MESES_COL:
        cols.append({
            "field": f"m_{m}", "headerName": nombre, "editable": _EDITABLE,
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

    # construir la tabla de objetivos al cambiar el año
    @app.callback(
        Output("bsc-cap-obj-cont", "children"),
        Input("bsc-cap-anio", "value"),
    )
    def _obj(anio):
        if not anio:
            return html.Div("Selecciona un año.", style={"color": "#6C757D"})
        return _grid_objetivos(anio)

    # GUARDAR: recalcula objetivos (anual + padres + fórmulas) y persiste
    @app.callback(
        Output("bsc-cap-msg", "children"),
        Input("bsc-cap-guardar", "n_clicks"),
        State("bsc-cap-obj-grid", "rowData"),
        State("bsc-cap-anio", "value"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def _guardar(n, obj_rows, anio, sesion):
        if not n or not anio:
            return no_update
        if not (sesion and sesion.get("rol") == "admin"):
            return html.Span("Solo un administrador puede guardar.",
                             style={"color": "#C0392B"})

        from bsc.logica import formular_objetivos
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
        try:
            datos.guardar_objetivos_anio(anio, valores_obj, reemplazar_anio=True)
        except Exception as e:
            return html.Span(f"Error al guardar: {e}",
                             style={"color": "#C0392B"})
        return html.Span(f"✓ Objetivos {anio} guardados.",
                         style={"color": "#1E8449"})

    # opciones del rellenado y del "pegar desde"
    @app.callback(
        Output("bsc-cap-ofill-ind", "options"),
        Output("bsc-cap-ofill-mes", "options"),
        Output("bsc-cap-pegar-desde", "options"),
        Input("bsc-cap-anio", "value"),
    )
    def _ofill_opciones(anio):
        inds = [{"label": "— Todos los indicadores —", "value": "__todos__"}]
        pegar = []
        for ind in catalogo.capturables():
            sangria = "    " if ind["nivel"] >= 1 else ""
            inds.append({"label": sangria + ind["nombre"], "value": ind["id"]})
            pegar.append({"label": sangria + ind["nombre"], "value": ind["id"]})
        meses = [{"label": "— Todos los meses —", "value": "__todos__"}]
        meses += [{"label": n, "value": m} for m, n in MESES_COL]
        return inds, meses, pegar

    # aplicar rellenado a la tabla de objetivos
    @app.callback(
        Output("bsc-cap-obj-grid", "rowData", allow_duplicate=True),
        Output("bsc-cap-ofill-msg", "children"),
        Input("bsc-cap-ofill-btn", "n_clicks"),
        State("bsc-cap-ofill-ind", "value"),
        State("bsc-cap-ofill-mes", "value"),
        State("bsc-cap-ofill-valor", "value"),
        State("bsc-cap-obj-grid", "rowData"),
        prevent_initial_call=True,
    )
    def _aplicar_ofill(n, ind_sel, mes_sel, valor, rowdata):
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
        nums = ([int(mes_sel)] if mes_sel not in (None, "__todos__")
                else [m for m, _ in MESES_COL])
        tocadas = 0
        for fila in rowdata:
            if fila.get("es_titulo"):
                continue
            if ind_sel not in (None, "__todos__") and fila.get("id") != ind_sel:
                continue
            for m in nums:
                fila[f"m_{m}"] = v
                tocadas += 1
        if tocadas == 0:
            return no_update, html.Span("Nada que rellenar (revisa la selección).",
                                        style={"color": "#B7791F"})
        return rowdata, html.Span(
            f"✓ {tocadas} celda(s) rellenadas. Revisa y «Guardar».",
            style={"color": "#1E8449"})

    # mostrar/ocultar zona de pegado
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

    # aplicar el bloque pegado de Excel a la tabla de objetivos.
    # Cada fila del bloque -> una fila capturable (en orden). Las
    # columnas del bloque -> Ene..Dic (m_1..m_12).
    @app.callback(
        Output("bsc-cap-obj-grid", "rowData", allow_duplicate=True),
        Output("bsc-cap-pegar-msg", "children"),
        Input("bsc-cap-pegar-aplicar", "n_clicks"),
        State("bsc-cap-pegar-texto", "value"),
        State("bsc-cap-pegar-desde", "value"),
        State("bsc-cap-obj-grid", "rowData"),
        prevent_initial_call=True,
    )
    def _aplicar_pegado(n, texto, desde_id, rowdata):
        if not n or not texto or not rowdata:
            return no_update, ""
        lineas = [ln for ln in texto.replace("\r", "").split("\n")
                  if ln.strip() != ""]
        if not lineas:
            return no_update, html.Span("No se detectó contenido.",
                                        style={"color": "#C0392B"})
        # filas capturables (en orden visual, saltando títulos)
        idx_capturables = [i for i, f in enumerate(rowdata)
                           if not f.get("es_titulo")]
        if not idx_capturables:
            return no_update, html.Span("No hay filas donde pegar.",
                                        style={"color": "#C0392B"})

        # ¿desde qué indicador empezar? buscar su posición en la lista
        inicio = 0
        if desde_id:
            for pos, i in enumerate(idx_capturables):
                if rowdata[i].get("id") == desde_id:
                    inicio = pos
                    break

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
            destino = inicio + li
            if destino >= len(idx_capturables):
                break
            celdas = linea.split("\t")
            fila = rowdata[idx_capturables[destino]]
            for ci, (m, _) in enumerate(MESES_COL):
                if ci < len(celdas):
                    val = _num(celdas[ci])
                    if val is not None:
                        fila[f"m_{m}"] = val
            aplicadas += 1

        return rowdata, html.Span(
            f"✓ {aplicadas} fila(s) aplicadas. Revisa y «Guardar».",
            style={"color": "#1E8449"})