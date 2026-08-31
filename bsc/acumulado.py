"""
=========================================================
bsc/acumulado.py  —  VISTA ACUMULADO ANUAL (/bsc-acumulado)
=========================================================
Consolida el año completo (como la hoja "2026 Acumulado"):
objetivo anual, acumulado del año, % avance, deber ser, y una
columna por mes (Ene..Dic). Solo lectura.

Total del año: flujo = suma de los 12 meses; saldo = último mes
con dato (lo calcula bsc/logica.construir_acumulado).
"""

from dash import Input, Output, html, dcc
import dash_ag_grid as dag

from bsc import logica, datos

AZUL = "#173C73"

MESES_COL = [(1, "Ene"), (2, "Feb"), (3, "Mar"), (4, "Abr"),
             (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Ago"),
             (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dic")]

_FMT_VALOR = {"function": (
    "params.value == null ? '' : "
    "(params.data.unidad === '$' ? '$' + d3.format(',.0f')(params.value) : "
    " params.data.unidad === 'Días' ? d3.format(',.0f')(params.value) + ' d' : "
    " d3.format(',.0f')(params.value)))"
)}
_FMT_PCT = {"function":
    "params.value == null ? '' : d3.format(',.1f')(params.value*100) + '%'"}

_CELL_SEMAFORO = {"function": (
    "({'verde':{color:'#2ecc71',fontSize:'18px',textAlign:'center'},"
    "  'amarillo':{color:'#f1c40f',fontSize:'18px',textAlign:'center'},"
    "  'rojo':{color:'#e74c3c',fontSize:'18px',textAlign:'center'},"
    "  'gris':{color:'#cfd6df',fontSize:'18px',textAlign:'center'}}"
    ")[params.data.color] || {textAlign:'center'}"
)}
_CELL_INDICADOR = {"function":
    "params.data.nivel === 1 ? "
    "{color:'#5A6472', paddingLeft:'26px'} : "
    "{fontWeight:'700', color:'#173C73'}"}


def _estilo_grid(alto):
    return {
        "width": "100%", "height": alto,
        "--ag-font-size": "13px",
        "--ag-header-background-color": AZUL,
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-row-hover-color": "#E5DECB",
        "--ag-icon-color": "#FFFFFF",
    }


def crear_panel_acumulado_bsc():
    anios = datos.anios_con_bsc()
    anio_val = anios[0] if anios else None
    return html.Div(
        [
            html.P("Consolidado del año: objetivo, acumulado, % y avance "
                   "mes a mes.", className="subtitulo"),
            html.Div(
                [
                    html.Label("Año", style={"fontWeight": "600", "color": AZUL,
                                             "display": "block",
                                             "marginBottom": "4px"}),
                    dcc.Dropdown(
                        id="bsc-acum-anio",
                        options=[{"label": str(a), "value": a} for a in anios],
                        value=anio_val, clearable=False,
                        style={"width": "160px"}),
                ],
                style={"marginBottom": "18px"},
            ),
            html.Div(id="bsc-acum-info",
                     style={"marginBottom": "14px", "fontSize": "13px",
                            "color": "#6C757D", "fontStyle": "italic"}),
            html.Div(id="bsc-acum-tabla-cont"),
        ]
    )


def _column_defs():
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 240,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-bsc", "cellStyle": _CELL_INDICADOR},
        {"field": "objetivo", "headerName": "Objetivo", "type": "numericColumn",
         "valueFormatter": _FMT_VALOR, "minWidth": 120, "pinned": "left",
         "sortable": False, "filter": False, "headerClass": "hdr-bsc"},
        {"field": "acumulado", "headerName": "Acumulado", "type": "numericColumn",
         "valueFormatter": _FMT_VALOR, "minWidth": 130, "pinned": "left",
         "sortable": False, "filter": False, "headerClass": "hdr-bsc",
         "cellStyle": {"fontWeight": "700", "color": AZUL}},
        {"field": "pct", "headerName": "% avance", "type": "numericColumn",
         "valueFormatter": _FMT_PCT, "minWidth": 95, "pinned": "left",
         "sortable": False, "filter": False, "headerClass": "hdr-bsc"},
        {"field": "semaforo", "headerName": "", "minWidth": 50, "maxWidth": 60,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-bsc", "cellStyle": _CELL_SEMAFORO},
    ]
    for m, nombre in MESES_COL:
        cols.append({
            "field": f"mes_{m}", "headerName": nombre, "type": "numericColumn",
            "valueFormatter": _FMT_VALOR, "minWidth": 90, "sortable": False,
            "filter": False, "headerClass": "hdr-bsc",
            "cellStyle": {"color": "#5A6472"}})
    return cols


def registrar_callbacks_bsc_acumulado(app):

    @app.callback(
        Output("bsc-acum-tabla-cont", "children"),
        Output("bsc-acum-info", "children"),
        Input("bsc-acum-anio", "value"),
    )
    def _tabla(anio):
        if not anio:
            return html.Div("Selecciona un año.",
                            style={"color": "#6C757D"}), ""
        porm = datos.leer_objetivos_anio(anio)
        obj_anual = porm.get(0, {})
        cap = datos.leer_captura_anio(anio)
        filas, ds = logica.construir_acumulado(anio, obj_anual, cap)
        for f in filas:
            f["semaforo"] = "●"
        grid = dag.AgGrid(
            id="bsc-acum-grid",
            rowData=filas,
            columnDefs=_column_defs(),
            defaultColDef={"resizable": True, "sortable": False,
                           "filter": False, "flex": 1, "minWidth": 85},
            dashGridOptions={"animateRows": False, "rowHeight": 30,
                             "headerHeight": 40, "suppressCellFocus": True},
            className="ag-theme-alpine",
            style=_estilo_grid("660px"),
        )
        return grid, f"Año {anio} · avance esperado a hoy: {ds*100:.0f}%"