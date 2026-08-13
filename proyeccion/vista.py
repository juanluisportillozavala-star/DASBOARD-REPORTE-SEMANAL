"""
=========================================================
proyeccion/vista.py  —  MÓDULO PROYECCIÓN (visualización)
=========================================================
Muestra el cumplimiento de la proyección de un año/mes:
  Producto | Proyección | Facturado | Diferencia | % Avance
           | Utilidad | Util Unit
La fila VARIOS agrupa lo vendido fuera de la lista, y abajo
una tabla con el detalle de esos productos varios.

Lee la proyección de db y las ventas de la caché del servidor.
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag

import db

AZUL = "#173C73"
DORADO = "#D4AF37"

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
                style={"display": "flex", "gap": "20px", "marginBottom": "24px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            html.Div(id="proy-ver-tabla"),

            html.Br(),
            html.H4("Detalle de productos VARIOS",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.P("Productos vendidos que no están en la lista de proyección.",
                   style={"color": "#6C757D", "fontSize": "13px"}),
            html.Div(id="proy-ver-varios"),
            html.Br(),
        ]
    )


def _col_defs():
    return [
        {"field": "producto", "headerName": "Producto", "minWidth": 260,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-proy",
         "cellStyle": {"function":
             "params.data.producto === 'VARIOS' ? {fontStyle:'italic', color:'#6C757D'} : {}"}},
        {"field": "proyeccion", "headerName": "Proyección", "type": "numericColumn",
         "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": False,
         "filter": False, "headerClass": "hdr-proy"},
        {"field": "facturado", "headerName": "Facturado", "type": "numericColumn",
         "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": False,
         "filter": False, "headerClass": "hdr-proy"},
        {"field": "diferencia", "headerName": "Diferencia", "type": "numericColumn",
         "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": False,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"function":
             "params.value < 0 ? {color:'#C0392B'} : {color:'#198754'}"}},
        {"field": "avance", "headerName": "% Avance", "type": "numericColumn",
         "valueFormatter": FMT_PCT, "minWidth": 110, "sortable": False,
         "filter": False, "headerClass": "hdr-proy",
         "cellStyle": {"function":
             "params.value == null ? {} : (params.value >= 100 ? {color:'#198754',fontWeight:'700'} : {color:'#173C73'})"}},
        {"field": "utilidad", "headerName": "Utilidad", "type": "numericColumn",
         "valueFormatter": FMT_MONEDA, "minWidth": 140, "sortable": False,
         "filter": False, "headerClass": "hdr-proy"},
        {"field": "util_unit", "headerName": "Util Unit", "type": "numericColumn",
         "valueFormatter": FMT_MONEDA, "minWidth": 120, "sortable": False,
         "filter": False, "headerClass": "hdr-proy"},
    ]


def _grid(filas, fila_total):
    return dag.AgGrid(
        rowData=filas,
        columnDefs=_col_defs(),
        dashGridOptions={"animateRows": False, "rowHeight": 34,
                         "headerHeight": 40, "domLayout": "autoHeight",
                         "pinnedBottomRowData": [fila_total],
                         "suppressCellFocus": True},
        getRowStyle={"function":
            "params.node.rowPinned ? "
            "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : {}"},
        defaultColDef={"resizable": True, "sortable": False, "filter": False,
                       "flex": 1, "minWidth": 110},
        className="ag-theme-alpine",
        style={"width": "100%", "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


def _grid_varios(detalle):
    if not detalle:
        return html.Div("No hay productos varios en este periodo.",
                        style={"color": "#6C757D"})
    return dag.AgGrid(
        rowData=detalle,
        columnDefs=[
            {"field": "producto", "headerName": "Producto", "minWidth": 260,
             "flex": 2, "sortable": False, "filter": False, "headerClass": "hdr-proy"},
            {"field": "facturado", "headerName": "Facturado", "type": "numericColumn",
             "valueFormatter": FMT_NUM, "minWidth": 120, "sortable": False,
             "filter": False, "headerClass": "hdr-proy"},
            {"field": "utilidad", "headerName": "Utilidad", "type": "numericColumn",
             "valueFormatter": FMT_MONEDA, "minWidth": 140, "sortable": False,
             "filter": False, "headerClass": "hdr-proy"},
            {"field": "util_unit", "headerName": "Util Unit", "type": "numericColumn",
             "valueFormatter": FMT_MONEDA, "minWidth": 120, "sortable": False,
             "filter": False, "headerClass": "hdr-proy"},
        ],
        dashGridOptions={"animateRows": False, "rowHeight": 32,
                         "headerHeight": 38, "domLayout": "autoHeight",
                         "suppressCellFocus": True},
        defaultColDef={"resizable": True, "sortable": False, "filter": False,
                       "flex": 1, "minWidth": 110},
        className="ag-theme-alpine",
        style={"width": "100%", "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


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

    # construir la tabla de cumplimiento + detalle de varios
    @app.callback(
        Output("proy-ver-tabla", "children"),
        Output("proy-ver-varios", "children"),
        Input("proy-ver-anio", "value"),
        Input("proy-ver-mes", "value"),
    )
    def construir(anio, mes):
        if not anio or not mes:
            return (html.Div("Selecciona año y mes.", style={"color": "#6C757D"}),
                    "")
        proyeccion = db.leer_proyeccion(anio, mes)
        if not proyeccion:
            return (html.Div("No hay proyección guardada para este periodo.",
                             style={"color": "#6C757D"}), "")
        df_ventas = db.obtener_df("ventas")
        filas, total, varios = construir_tabla_proyeccion(
            proyeccion, df_ventas, anio, mes)
        return _grid(filas, total), _grid_varios(varios)