"""
=========================================================
ingresos/tabla_ingresos.py
=========================================================
Matriz de Ingresos: Vendedor -> Cliente (expandible) con
columnas cruzadas (Términos de pago × Estatus) + Total general,
igual que la tabla dinámica del Excel.

Las columnas son DINÁMICAS: solo se muestran las combinaciones
(Contado/Crédito × Vigente/Vencido) que existan en los datos
filtrados, en orden Contado→Crédito, Vigente→Vencido.

Filtros: AÑO (maestro) + calendario Mes/Semana.
Lee de la caché del servidor (db.obtener_df).
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag
import pandas as pd

import db
from ingresos.arbol_ingresos import (
    construir_arbol_ingresos, total_general_ingresos, filas_visibles_ingresos,
    combos_presentes, _campo,
)

MODULO = "ingresos"
COL_MES = "MES"
COL_SEMANA = "SEMANA"
COL_ANIO = "AÑO"

AZUL = "#173C73"
DORADO = "#D4AF37"

ALTO_FILA = 34
ALTO_ENCABEZADO = 38
ALTO_MAXIMO_ING = 600

FMT_MONEDA = {"function": "params.value == null ? '' : '$' + d3.format(',.2f')(params.value)"}


def _column_defs(combos):
    """Columnas según los combos presentes (agrupadas por Términos)."""
    defs = [
        {
            "field": "concepto",
            "headerName": "Vendedor / Cliente",
            "minWidth": 300,
            "pinned": "left",
            "filter": False, "sortable": False,
            "headerClass": "hdr-ingresos",
            "cellStyle": {"function": "params.data.tieneHijos ? {cursor: 'pointer'} : {}"},
        },
    ]
    # agrupar los combos presentes por término, respetando el orden
    terminos_orden = []
    for t, e in combos:
        if t not in terminos_orden:
            terminos_orden.append(t)

    for t in terminos_orden:
        hijos = []
        for (tt, ee) in combos:
            if tt != t:
                continue
            hijos.append({
                "field": _campo(tt, ee),
                "headerName": ee,
                "type": "numericColumn",
                "filter": False, "sortable": False,
                "valueFormatter": FMT_MONEDA,
                "minWidth": 130,
                "headerClass": "hdr-ingresos",
            })
        defs.append({"headerName": t, "children": hijos,
                     "headerClass": "hdr-ingresos-grupo"})

    defs.append({
        "field": "total",
        "headerName": "Total general",
        "type": "numericColumn",
        "filter": False, "sortable": False,
        "valueFormatter": FMT_MONEDA,
        "minWidth": 150, "pinned": "right",
        "headerClass": "hdr-ingresos",
    })
    return defs


def _estilo_filas():
    return {
        "function": (
            "params.data.nivel === 0 ? "
            "{fontWeight: 'bold', backgroundColor: '#173C73', color: '#FFFFFF'} : "
            "params.data.nivel === 1 ? "
            "{fontWeight: 'bold', backgroundColor: '#FFFFFF', color: '#173C73', "
            "borderLeft: '5px solid #D4AF37'} : "
            "{backgroundColor: '#FBF3DC', color: '#173C73'}"
        )
    }


def _estilo_grid(alto):
    return {
        "width": "100%",
        "height": alto,
        "--ag-font-size": "16px",
        "--ag-header-background-color": "#173C73",
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-header-cell-hover-background-color": "#173C73",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-header-column-separator-color": "#2C5090",
        "--ag-row-hover-color": "#E5DECB",
        "--ag-icon-color": "#FFFFFF",
        "--ag-secondary-foreground-color": "#FFFFFF",
    }


def _opciones_grid(pinned):
    return {
        "animateRows": False,
        "rowHeight": ALTO_FILA,
        "headerHeight": ALTO_ENCABEZADO,
        "groupHeaderHeight": ALTO_ENCABEZADO,
        "pinnedBottomRowData": pinned,
        "suppressCellFocus": True,
    }


def _altura_dinamica(n_filas):
    alto = (ALTO_ENCABEZADO * 2) + (n_filas * ALTO_FILA) + ALTO_FILA + 16
    return f"{min(alto, ALTO_MAXIMO_ING)}px"


def crear_encabezado_periodo(anio_txt, semanas_texto):
    return html.Div(
        [
            html.Span("Año:  ",
                      style={"color": DORADO, "fontWeight": "bold", "marginLeft": "24px"}),
            html.Span(anio_txt,
                      style={"color": "#FFFFFF", "fontWeight": "bold", "marginRight": "32px"}),
            html.Span("Semana(s):  ", style={"color": DORADO, "fontWeight": "bold"}),
            html.Span(semanas_texto, style={"color": "#FFFFFF", "fontWeight": "bold"}),
        ],
        style={"backgroundColor": AZUL, "padding": "12px 16px",
               "borderRadius": "10px 10px 0 0", "display": "flex",
               "justifyContent": "flex-end", "flexWrap": "wrap", "fontSize": "15px"},
    )


def crear_layout_tabla_ingresos():
    return html.Div(
        [
            html.Div(
                dcc.Markdown(
                    """<style>
                    .hdr-ingresos, .hdr-ingresos .ag-header-cell-text,
                    .hdr-ingresos-grupo, .hdr-ingresos-grupo .ag-header-group-text {
                        color: #FFFFFF !important;
                    }
                    </style>""",
                    dangerously_allow_html=True,
                ),
                style={"display": "none"},
            ),
            dcc.Store(id="store-ing-arbol", data=None),
            dcc.Store(id="store-ing-total", data=None),
            dcc.Store(id="store-ing-combos", data=None),
            dcc.Store(id="store-ing-exp", data=[]),
            html.Div(id="tabla-ingresos-cont"),
        ]
    )


def _filtrar(df, anio, meses, semanas):
    if df is None:
        return df
    if anio:
        df = df[df[COL_ANIO] == int(anio)]
    if meses:
        df = df[df[COL_MES].isin(meses)]
    if semanas:
        df = df[df[COL_SEMANA].isin(semanas)]
    return df


def registrar_callbacks_tabla_ingresos(app):

    @app.callback(
        Output("tabla-ingresos-cont", "children"),
        Output("store-ing-arbol", "data"),
        Output("store-ing-total", "data"),
        Output("store-ing-combos", "data"),
        Input("store-bd-ingresos", "data"),
        Input("dropdown-anio-ingresos", "value"),
        Input("store-mes-ingresos", "data"),
        Input("store-semana-ingresos", "data"),
        State("store-ing-exp", "data"),
    )
    def construir(marca, anio, meses, semanas, ids_exp):
        df = db.obtener_df(MODULO)
        if df is None:
            return (html.Div("Aún no hay datos de Ingresos cargados.",
                             style={"color": "#6C757D"}), None, None, None)
        try:
            df_f = _filtrar(df, anio, meses, semanas)
            if df_f is None or len(df_f) == 0:
                return (html.Div("No hay datos para el filtro seleccionado.",
                                 style={"color": "#6C757D"}), None, None, None)

            combos = combos_presentes(df_f)
            arbol = construir_arbol_ingresos(df_f, meses)
            total = total_general_ingresos(df_f, meses)

            semanas_txt = ", ".join(str(s) for s in sorted(semanas)) if semanas else "Todas"
            anio_txt = str(anio) if anio else "—"
            visibles = filas_visibles_ingresos(arbol, ids_exp or [])

            grid = dag.AgGrid(
                id="tabla-ingresos-grid",
                rowData=visibles.to_dict("records"),
                columnDefs=_column_defs(combos),
                getRowId={"function": "params.data.id"},
                getRowStyle=_estilo_filas(),
                defaultColDef={"flex": 1, "minWidth": 130, "sortable": False,
                               "filter": False, "resizable": True},
                dashGridOptions=_opciones_grid([total]),
                className="ag-theme-alpine",
                style=_estilo_grid(_altura_dinamica(len(visibles))),
            )
            contenido = html.Div([
                crear_encabezado_periodo(anio_txt, semanas_txt),
                grid,
            ])
            return (contenido, arbol.to_dict("records"), total,
                    [list(c) for c in combos])
        except Exception as e:
            return (html.Div([html.H3("ERROR"), html.Pre(str(e))],
                             style={"color": "red"}), None, None, None)

    @app.callback(
        Output("store-ing-exp", "data"),
        Input("tabla-ingresos-grid", "cellClicked"),
        State("store-ing-exp", "data"),
        prevent_initial_call=True,
    )
    def alternar(celda, ids_exp):
        if celda is None:
            return no_update
        fid = celda.get("rowId")
        if fid is None:
            return no_update
        if "||" in fid or fid == "total":
            return no_update
        ids = set(ids_exp or [])
        if fid in ids:
            ids.discard(fid)
        else:
            ids.add(fid)
        return sorted(ids)

    @app.callback(
        Output("tabla-ingresos-grid", "rowData"),
        Output("tabla-ingresos-grid", "style"),
        Input("store-ing-exp", "data"),
        State("store-ing-arbol", "data"),
        prevent_initial_call=True,
    )
    def refrescar(ids_exp, arbol_data):
        if arbol_data is None:
            return no_update, no_update
        arbol = pd.DataFrame(arbol_data)
        visibles = filas_visibles_ingresos(arbol, ids_exp or [])
        return (visibles.to_dict("records"),
                _estilo_grid(_altura_dinamica(len(visibles))))