"""
=========================================================
proyeccion/vista.py  —  MÓDULO PROYECCIÓN (visualización)
=========================================================
Muestra el cumplimiento de la proyección de un año/mes con
pestañas:
  • Acumulado         -> los 3 vendedores sumados vs ventas totales
  • ILSE / FREDY / MATEO -> cada vendedor vs SUS ventas

Cada tabla: Producto | Proyección | Facturado | Diferencia |
% Avance | Utilidad | Util Unit. La fila VARIOS agrupa lo
vendido fuera de la lista, con su detalle abajo.

Lee la proyección de db y las ventas de la caché del servidor.
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag

import db
from db import VENDEDORES

AZUL = "#173C73"
DORADO = "#D4AF37"

ACUMULADO = "ACUMULADO"

# "vendedor" reservado para guardar los comentarios propios del
# Acumulado en la misma tabla comentarios_proyeccion sin chocar
# con ningún vendedor real.
CLAVE_ACUMULADO = "__ACUMULADO__"

MESES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]
MESES_NOMBRE = {m: n for m, n in MESES}

FMT_NUM = {"function": "params.value == null ? '' : d3.format(',.0f')(params.value)"}
FMT_MONEDA = {"function": "params.value == null ? '' : '$' + d3.format(',.2f')(params.value)"}
FMT_PCT = {"function": "params.value == null ? '—' : d3.format(',.1f')(params.value) + '%'"}


def crear_layout_proyeccion():
    return html.Div(
        [
            html.Div(
                dcc.Markdown(
                    """<style>
                    .hdr-proy, .hdr-proy .ag-header-cell-text { color:#FFFFFF !important; }
                    </style>""",
                    dangerously_allow_html=True,
                ),
                style={"display": "none"},
            ),

            html.H1("Proyección", className="titulo"),
            html.P("Cumplimiento de la proyección mensual vs lo facturado.",
                   className="subtitulo"),
            html.Br(),

            # selectores año + mes
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(id="proy-ver-anio", options=[], value=None,
                                         clearable=False, style={"width": "140px"}),
                        ],
                    ),
                    html.Div(
                        [
                            html.Label("Mes", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(id="proy-ver-mes", options=[], value=None,
                                         clearable=False, style={"width": "180px"}),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            # pestañas: Acumulado + un vendedor cada una
            dcc.Tabs(
                id="proy-ver-tab", value=ACUMULADO,
                children=[dcc.Tab(label="Acumulado", value=ACUMULADO)]
                         + [dcc.Tab(label=v, value=v) for v in VENDEDORES],
                style={"marginBottom": "16px"},
            ),

            html.Div(id="proy-ver-tabla"),

            html.Br(),
            html.H4("Detalle de productos VARIOS",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.P("Productos vendidos que no están en la lista de proyección.",
                   style={"color": "#6C757D", "fontSize": "13px"}),
            html.Div(id="proy-ver-varios"),

            # ===== SECCIÓN DE COMENTARIOS (solo pestañas de vendedor) =====
            html.Div(id="proy-coment-seccion"),

            html.Br(),
        ]
    )


def _col_defs():
    return [
        {"field": "producto", "headerName": "Producto", "minWidth": 260,
         "pinned": "left", "sortable": True, "filter": False,
         "headerClass": "hdr-proy hdr-proy-izq",
         "cellStyle": {"function":
             "params.data.producto === 'VARIOS' ? {fontStyle:'italic', color:'#6C757D', textAlign:'left'} : {textAlign:'left'}"}},
        {"field": "proyeccion", "headerName": "Proyección", "type": "numericColumn",
         "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": True,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"textAlign": "center"}},
        {"field": "facturado", "headerName": "Facturado", "type": "numericColumn",
         "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": True,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"textAlign": "center"}},
        {"field": "diferencia", "headerName": "Diferencia", "type": "numericColumn",
         "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": True,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"function":
             "params.value < 0 ? {color:'#C0392B', textAlign:'center'} : {color:'#198754', textAlign:'center'}"}},
        {"field": "avance", "headerName": "% Avance", "type": "numericColumn",
         "valueFormatter": FMT_PCT, "minWidth": 110, "sortable": True,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"function":
             "params.value == null ? {textAlign:'center'} : (params.value >= 100 ? {color:'#198754',fontWeight:'700',textAlign:'center'} : {color:'#173C73',textAlign:'center'})"}},
        {"field": "utilidad", "headerName": "Utilidad", "type": "numericColumn",
         "valueFormatter": FMT_MONEDA, "minWidth": 140, "sortable": True,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"textAlign": "center"}},
        {"field": "util_unit", "headerName": "Util Unit", "type": "numericColumn",
         "valueFormatter": FMT_MONEDA, "minWidth": 120, "sortable": True,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"textAlign": "center"}},
    ]


def _grid(filas, fila_total):
    normales = [f for f in filas if f.get("producto") != "VARIOS"]
    fila_varios = next((f for f in filas if f.get("producto") == "VARIOS"), None)

    pinned = []
    if fila_varios is not None:
        pinned.append(fila_varios)
    pinned.append(fila_total)

    return dag.AgGrid(
        rowData=normales,
        columnDefs=_col_defs(),
        dashGridOptions={"animateRows": False, "rowHeight": 34,
                         "headerHeight": 40, "domLayout": "autoHeight",
                         "pinnedBottomRowData": pinned,
                         "suppressCellFocus": True},
        getRowStyle={"function":
            "params.node.rowPinned ? ("
            "params.data.producto === 'VARIOS' ? "
            "{fontStyle:'italic', color:'#6C757D', backgroundColor:'#FAFAF5'} : "
            "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'}"
            ") : {}"},
        defaultColDef={"resizable": True, "sortable": True, "filter": False,
                       "flex": 1, "minWidth": 110},
        className="ag-theme-alpine",
        style={"width": "100%", "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


def _grid_varios(detalle):
    if not detalle:
        return html.Div("No hay productos varios en este periodo.",
                        style={"color": "#6C757D"})

    tot_fact = sum(float(d.get("facturado", 0)) for d in detalle)
    tot_util = sum(float(d.get("utilidad", 0)) for d in detalle)
    tot_uu = (tot_util / tot_fact) if tot_fact else 0
    fila_total = {"producto": "TOTAL", "facturado": round(tot_fact, 2),
                  "utilidad": round(tot_util, 2), "util_unit": round(tot_uu, 2)}

    centrar = {"textAlign": "center"}
    izq = {"textAlign": "left"}

    return dag.AgGrid(
        rowData=detalle,
        columnDefs=[
            {"field": "producto", "headerName": "Producto", "minWidth": 260,
             "flex": 2, "sortable": True, "filter": False,
             "headerClass": "hdr-proy hdr-proy-izq", "cellStyle": izq},
            {"field": "facturado", "headerName": "Facturado", "type": "numericColumn",
             "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": True,
             "filter": False, "headerClass": "hdr-proy", "cellStyle": centrar},
            {"field": "utilidad", "headerName": "Utilidad", "type": "numericColumn",
             "valueFormatter": FMT_MONEDA, "minWidth": 140, "sortable": True,
             "filter": False, "headerClass": "hdr-proy", "cellStyle": centrar},
            {"field": "util_unit", "headerName": "Util Unit", "type": "numericColumn",
             "valueFormatter": FMT_MONEDA, "minWidth": 120, "sortable": True,
             "filter": False, "headerClass": "hdr-proy", "cellStyle": centrar},
        ],
        dashGridOptions={"animateRows": False, "rowHeight": 32,
                         "headerHeight": 38, "domLayout": "autoHeight",
                         "pinnedBottomRowData": [fila_total],
                         "suppressCellFocus": True},
        getRowStyle={"function":
            "params.node.rowPinned ? "
            "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : {}"},
        defaultColDef={"resizable": True, "sortable": True, "filter": False,
                       "flex": 1, "minWidth": 110},
        className="ag-theme-alpine",
        style={"width": "100%", "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


# =========================================================
# TABLA DE COMENTARIOS (solo pestañas de vendedor)
# =========================================================

def _puede_editar_coment(sesion, clave):
    """Reglas de edición de comentarios:
      • Acumulado (clave == CLAVE_ACUMULADO): SOLO admin.
      • Pestaña de vendedor (clave == nombre del vendedor): SOLO
        ese vendedor (ni admin ni otros)."""
    if not sesion:
        return False
    if clave == CLAVE_ACUMULADO:
        return sesion.get("rol") == "admin"
    return (sesion.get("vendedor") or "") == clave


def _filas_comentarios(filas, guardados):
    """Arma las filas de la tabla de comentarios a partir de las
    filas de cumplimiento (producto/proyección/facturado) + los
    comentarios guardados. Incluye VARIOS. Excluye la fila TOTAL
    (se pone como fila fijada abajo)."""
    out = []
    tot_proy = tot_fact = 0.0
    for f in filas:
        prod = f.get("producto")
        if prod in (None, "TOTAL"):
            continue
        proy = f.get("proyeccion") or 0
        fact = f.get("facturado") or 0
        tot_proy += float(proy)
        tot_fact += float(fact)
        out.append({
            "producto": prod,
            "proyeccion": proy,
            "facturado": fact,
            "comentario": guardados.get(prod, ""),
        })
    total = {"producto": "TOTAL",
             "proyeccion": round(tot_proy, 2),
             "facturado": round(tot_fact, 2),
             "comentario": ""}
    return out, total


def _grid_comentarios(filas_coment, fila_total, editable):
    return dag.AgGrid(
        id="proy-coment-grid",
        rowData=filas_coment,
        columnDefs=[
            {"field": "producto", "headerName": "Producto", "minWidth": 240,
             "pinned": "left", "sortable": False, "filter": False, "editable": False,
             "headerClass": "hdr-proy hdr-proy-izq",
             "cellStyle": {"function":
                 "params.data.producto === 'VARIOS' ? {fontStyle:'italic', color:'#6C757D'} : {}"}},
            {"field": "proyeccion", "headerName": "Proyectado", "type": "numericColumn",
             "valueFormatter": FMT_NUM, "minWidth": 120, "editable": False,
             "sortable": False, "filter": False, "headerClass": "hdr-proy",
             "cellStyle": {"textAlign": "center"}},
            {"field": "facturado", "headerName": "Facturado", "type": "numericColumn",
             "valueFormatter": FMT_NUM, "minWidth": 120, "editable": False,
             "sortable": False, "filter": False, "headerClass": "hdr-proy",
             "cellStyle": {"textAlign": "center"}},
            {"field": "comentario", "headerName": "Comentarios", "minWidth": 380,
             "flex": 2, "editable": editable, "sortable": False, "filter": False,
             "headerClass": "hdr-proy hdr-proy-izq",
             "wrapText": True, "autoHeight": True,
             "cellEditor": {"function": "ComentarioEditor"},
             "cellEditorPopup": True,
             "cellEditorParams": {"rows": 8, "width": 460, "height": 200},
             "cellStyle": {"whiteSpace": "pre-wrap", "lineHeight": "1.4",
                           "backgroundColor": "#FFFDF5" if editable else "#FFFFFF"}},
        ],
        dashGridOptions={"animateRows": False, "headerHeight": 40,
                         "domLayout": "autoHeight",
                         "pinnedBottomRowData": [fila_total],
                         "singleClickEdit": True,
                         "stopEditingWhenCellsLoseFocus": True,
                         "suppressCellFocus": False},
        getRowStyle={"function":
            "params.node.rowPinned ? "
            "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : {}"},
        defaultColDef={"resizable": True, "sortable": False, "filter": False},
        className="ag-theme-alpine",
        style={"width": "100%", "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


def _seccion_comentarios(filas, guardados, editable, etiqueta):
    filas_coment, total = _filas_comentarios(filas, guardados)
    encabezado = [
        html.Br(),
        html.H4("Comentarios por producto",
                style={"color": AZUL, "fontWeight": "700", "marginBottom": "6px"}),
    ]
    if editable:
        encabezado.append(
            html.P("Escribe en la columna Comentarios (doble clic para abrir el "
                   "editor) y pulsa «Guardar comentarios».",
                   style={"color": "#6C757D", "fontSize": "13px"}))
    else:
        encabezado.append(
            html.P(f"{etiqueta} (solo lectura).",
                   style={"color": "#6C757D", "fontSize": "13px"}))

    hijos = encabezado + [
        _grid_comentarios(filas_coment, total, editable),
    ]
    if editable:
        hijos += [
            html.Button(
                [html.I(className="fas fa-floppy-disk me-2"), "Guardar comentarios"],
                id="proy-coment-guardar", n_clicks=0,
                style={"backgroundColor": AZUL, "color": "white", "border": "none",
                       "padding": "12px 22px", "borderRadius": "8px",
                       "fontWeight": "600", "cursor": "pointer", "marginTop": "12px"}),
            html.Div(id="proy-coment-msg",
                     style={"marginTop": "10px", "minHeight": "22px"}),
        ]
    else:
        # el botón/mensaje deben existir siempre (para el callback), aunque ocultos
        hijos += [
            html.Div(
                [html.Button("", id="proy-coment-guardar", n_clicks=0),
                 html.Div(id="proy-coment-msg")],
                style={"display": "none"}),
        ]
    return html.Div(hijos)


def registrar_callbacks_proyeccion(app):

    from proyeccion.logica import construir_tabla_proyeccion

    # llenar años/meses que tienen proyección guardada
    @app.callback(
        Output("proy-ver-anio", "options"),
        Output("proy-ver-anio", "value"),
        Input("url", "pathname"),
        State("proy-ver-anio", "value"),
    )
    def llenar_anios(pathname, actual):
        if pathname != "/proyeccion":
            return no_update, no_update
        anios = db.anios_con_proyeccion()
        if not anios:
            return [], None
        ops = [{"label": str(a), "value": a} for a in anios]
        val = actual if actual in anios else anios[0]
        return ops, val

    @app.callback(
        Output("proy-ver-mes", "options"),
        Output("proy-ver-mes", "value"),
        Input("proy-ver-anio", "value"),
        State("proy-ver-mes", "value"),
    )
    def llenar_meses(anio, actual):
        if not anio:
            return [], None
        meses = db.meses_con_proyeccion(anio)
        if not meses:
            return [], None
        ops = [{"label": MESES_NOMBRE.get(m, str(m)), "value": m} for m in meses]
        val = actual if actual in meses else meses[0]
        return ops, val

    # construir la tabla de cumplimiento + detalle de varios +
    # sección de comentarios, según la pestaña activa.
    @app.callback(
        Output("proy-ver-tabla", "children"),
        Output("proy-ver-varios", "children"),
        Output("proy-coment-seccion", "children"),
        Input("proy-ver-anio", "value"),
        Input("proy-ver-mes", "value"),
        Input("proy-ver-tab", "value"),
        State("store-sesion", "data"),
    )
    def construir(anio, mes, tab, sesion):
        if not anio or not mes:
            return (html.Div("Selecciona año y mes.", style={"color": "#6C757D"}),
                    "", "")

        if tab == ACUMULADO:
            proyeccion = db.leer_proyeccion_acumulada(anio, mes)
            vendedor = None
        else:
            proyeccion = db.leer_proyeccion(anio, mes, tab)
            vendedor = tab

        if not proyeccion:
            quien = "este periodo" if tab == ACUMULADO else f"{tab} en este periodo"
            return (html.Div(f"No hay proyección guardada para {quien}.",
                             style={"color": "#6C757D"}), "", "")

        df_ventas = db.obtener_df("ventas")
        filas, total, varios = construir_tabla_proyeccion(
            proyeccion, df_ventas, anio, mes, vendedor)

        # sección de comentarios:
        #   • Acumulado -> comentarios propios (clave __ACUMULADO__), edita admin
        #   • Vendedor  -> sus comentarios, edita solo ese vendedor
        if tab == ACUMULADO:
            clave = CLAVE_ACUMULADO
            etiqueta = "Comentarios del acumulado"
        else:
            clave = tab
            etiqueta = f"Comentarios de {tab}"
        guardados = db.leer_comentarios(anio, mes, clave)
        editable = _puede_editar_coment(sesion, clave)
        seccion = _seccion_comentarios(filas, guardados, editable, etiqueta)

        return _grid(filas, total), _grid_varios(varios), seccion

    # guardar comentarios (permiso validado en servidor según pestaña)
    @app.callback(
        Output("proy-coment-msg", "children"),
        Input("proy-coment-guardar", "n_clicks"),
        State("proy-ver-anio", "value"),
        State("proy-ver-mes", "value"),
        State("proy-ver-tab", "value"),
        State("proy-coment-grid", "rowData"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def guardar_comentarios(n, anio, mes, tab, rows, sesion):
        if not n:
            return no_update
        if not anio or not mes:
            return no_update
        # clave de guardado según la pestaña
        clave = CLAVE_ACUMULADO if tab == ACUMULADO else tab
        if not _puede_editar_coment(sesion, clave):
            if tab == ACUMULADO:
                msg = "Solo un administrador puede guardar los comentarios del acumulado."
            else:
                msg = "Solo el propio vendedor puede guardar sus comentarios."
            return html.Span(msg, style={"color": "#C0392B"})
        comentarios = {}
        for r in (rows or []):
            prod = r.get("producto")
            if prod in (None, "TOTAL"):
                continue
            comentarios[prod] = r.get("comentario") or ""
        try:
            db.guardar_comentarios(anio, mes, clave, comentarios)
            return html.Span("Comentarios guardados.",
                             style={"color": "#198754", "fontWeight": "600"})
        except Exception as e:
            return html.Span(f"Error: {e}", style={"color": "#C0392B"})