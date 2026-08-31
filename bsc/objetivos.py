"""
=========================================================
bsc/objetivos.py  —  CAPTURA de OBJETIVOS anuales (/bsc-objetivos)
=========================================================
Pantalla de admin para planear el año: una tabla editable con
una fila por indicador y columnas [Objetivo anual | Ene..Dic].
Los objetivos mensuales alimentan la vista mensual (BSC); el
objetivo anual (mes=0) alimenta la vista Acumulado.

Los padres (Venta, Utilidad…) van como filas-título; sus
objetivos se calculan sumando a los hijos, no se teclean aquí.
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag

from bsc import catalogo, datos

AZUL = "#173C73"

MESES_COL = [(1, "Ene"), (2, "Feb"), (3, "Mar"), (4, "Abr"),
             (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Ago"),
             (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dic")]

_CELL_INDICADOR = {"function": (
    "params.data.es_titulo ? "
    "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : "
    "(params.data.nivel === 1 ? "
    "  {color:'#5A6472', paddingLeft:'26px'} : "
    "  {fontWeight:'700', color:'#173C73'})"
)}
_EDITABLE = {"function": "!params.data.es_titulo"}
_CELL_EDIT = {"function": (
    "params.data.es_titulo ? {backgroundColor:'#F4F1E4'} : {}"
)}
_CELL_ANUAL = {"function": (
    "params.data.es_titulo ? {backgroundColor:'#F4F1E4'} : "
    "{backgroundColor:'#FFFDF5', fontWeight:'600'}"
)}


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


def crear_layout_objetivos_bsc():
    anios_g = datos.anios_con_bsc()
    anios = sorted(set(list(range(2025, 2036)) + anios_g), reverse=True)
    anio_val = anios_g[0] if anios_g else 2026
    return html.Div(
        [
            html.H1("Objetivos BSC", className="titulo"),
            html.P("Planea el año: teclea el objetivo anual y su "
                   "desglose por mes. Escribe en las celdas y pica «Guardar».",
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
                                id="bsc-obj-anio",
                                options=[{"label": str(a), "value": a}
                                         for a in anios],
                                value=anio_val, clearable=False,
                                style={"width": "140px"}),
                        ],
                    ),
                    html.Button("Guardar", id="bsc-obj-guardar", n_clicks=0,
                                className="btn btn-primary",
                                style={"height": "40px", "padding": "0 26px"}),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),
            html.Div(id="bsc-obj-msg",
                     style={"marginBottom": "12px", "fontWeight": "600"}),
            html.Div(id="bsc-obj-tabla-cont"),
        ]
    )


def _column_defs():
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 240,
         "pinned": "left", "editable": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_INDICADOR},
        {"field": "anual", "headerName": "Objetivo anual", "editable": _EDITABLE,
         "type": "numericColumn", "minWidth": 140, "pinned": "left",
         "headerClass": "hdr-bsc", "cellStyle": _CELL_ANUAL},
    ]
    for m, nombre in MESES_COL:
        cols.append({
            "field": f"m_{m}", "headerName": nombre, "editable": _EDITABLE,
            "type": "numericColumn", "minWidth": 90, "headerClass": "hdr-bsc",
            "cellStyle": _CELL_EDIT})
    return cols


def _filas(anio):
    porm = datos.leer_objetivos_anio(anio)   # {mes: {ind: val}}, mes 0 = anual
    filas = []
    for ind in catalogo.indicadores():
        iid = ind["id"]
        es_titulo = not ind["capturable"]
        fila = {"id": iid, "indicador": ind["nombre"],
                "es_titulo": es_titulo, "nivel": ind["nivel"],
                "anual": None if es_titulo else porm.get(0, {}).get(iid)}
        for m, _ in MESES_COL:
            fila[f"m_{m}"] = None if es_titulo else porm.get(m, {}).get(iid)
        filas.append(fila)
    return filas


def registrar_callbacks_bsc_objetivos(app):

    @app.callback(
        Output("bsc-obj-tabla-cont", "children"),
        Input("bsc-obj-anio", "value"),
    )
    def _construir(anio):
        if not anio:
            return html.Div("Selecciona un año.", style={"color": "#6C757D"})
        grid = dag.AgGrid(
            id="bsc-obj-grid",
            rowData=_filas(anio),
            columnDefs=_column_defs(),
            defaultColDef={"resizable": True, "sortable": False,
                           "filter": False, "flex": 1, "minWidth": 85},
            dashGridOptions={"animateRows": False, "rowHeight": 30,
                             "headerHeight": 40, "singleClickEdit": True,
                             "stopEditingWhenCellsLoseFocus": True},
            className="ag-theme-alpine",
            style=_estilo_grid("640px"),
        )
        return grid

    @app.callback(
        Output("bsc-obj-msg", "children"),
        Input("bsc-obj-guardar", "n_clicks"),
        State("bsc-obj-grid", "rowData"),
        State("bsc-obj-anio", "value"),
        prevent_initial_call=True,
    )
    def _guardar(n, rowdata, anio):
        if not n or not rowdata or not anio:
            return no_update
        valores = []   # (mes, indicador, valor)
        for fila in rowdata:
            iid = fila.get("id")
            if not iid or fila.get("es_titulo"):
                continue
            valores.append((0, iid, fila.get("anual")))       # anual
            for m, _ in MESES_COL:
                valores.append((m, iid, fila.get(f"m_{m}")))   # cada mes
        try:
            datos.guardar_objetivos_anio(anio, valores)
        except Exception as e:
            return html.Span(f"Error al guardar: {e}",
                             style={"color": "#C0392B"})
        return html.Span(f"✓ Objetivos {anio} guardados.",
                         style={"color": "#1E8449"})