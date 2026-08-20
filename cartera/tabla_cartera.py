"""
=========================================================
cartera/tabla_cartera.py
=========================================================
Tabla jerárquica de Cartera (Vendedor -> Cliente, expandible)
con los 7 rangos de aging + Total. Diseño premium (encabezado
azul, marcador dorado por nivel, franja de periodo, fila TOTAL
CARTERA).

Réplica de la tabla dinámica "Cartera" del Excel:
  • SOLO términos = Crédito.
  • Columnas de aging FIJAS.
  • Filtros: Año (maestro) + calendario Mes/Semana.

Lee de la caché del servidor (db.obtener_df).
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag
import pandas as pd

import db
from cartera.arbol_cartera import (
    construir_arbol_cartera, total_general_cartera, filas_visibles_cartera,
    RANGOS, CAMPOS,
)

MODULO = "cartera"
COL_MES = "MES"
COL_SEMANA = "SEMANA"
COL_ANIO = "AÑO"
COL_TERMINOS = "TERMINOS DE PAGO"

AZUL = "#173C73"
DORADO = "#D4AF37"

ALTO_FILA = 34
ALTO_ENCABEZADO = 38
ALTO_MAXIMO = 600

FMT_MONEDA = {"function": "params.value == null ? '' : '$' + d3.format(',.2f')(params.value)"}


def _column_defs():
    defs = [
        {"field": "concepto", "headerName": "Vendedor / Cliente",
         "minWidth": 280, "pinned": "left", "filter": False, "sortable": False,
         "headerClass": "hdr-cartera",
         "cellStyle": {"function": "params.data.tieneHijos ? {cursor:'pointer'} : {}"}},
    ]
    for campo, etiqueta in RANGOS:
        defs.append({
            "field": campo,
            "headerName": etiqueta,
            "type": "numericColumn",
            "valueFormatter": FMT_MONEDA,
            "minWidth": 130,
            "filter": False, "sortable": False,
            "headerClass": "hdr-cartera",
        })
    defs.append({
        "field": "total", "headerName": "Total Cartera",
        "type": "numericColumn", "valueFormatter": FMT_MONEDA,
        "minWidth": 150, "pinned": "right",
        "filter": False, "sortable": False,
        "headerClass": "hdr-cartera",
    })
    return defs


def _estilo_filas():
    return {
        "function": (
            "params.data.nivel === 0 ? "
            "{fontWeight:'bold', backgroundColor:'#173C73', color:'#FFFFFF'} : "
            "params.data.nivel === 1 ? "
            "{fontWeight:'bold', backgroundColor:'#FFFFFF', color:'#173C73', "
            "borderLeft:'5px solid #D4AF37'} : "
            "{backgroundColor:'#FBF3DC', color:'#173C73'}"
        )
    }


def _estilo_grid(alto):
    return {
        "width": "100%", "height": alto,
        "--ag-font-size": "15px",
        "--ag-header-background-color": AZUL,
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-row-hover-color": "#E5DECB",
        "--ag-icon-color": "#FFFFFF",
    }


def _altura_dinamica(n):
    alto = ALTO_ENCABEZADO + (n * ALTO_FILA) + ALTO_FILA + 16
    return f"{min(alto, ALTO_MAXIMO)}px"


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


def crear_layout_tabla_cartera():
    return html.Div(
        [
            html.Div(
                dcc.Markdown(
                    """<style>
                    .hdr-cartera, .hdr-cartera .ag-header-cell-text { color:#FFFFFF !important; }
                    </style>""",
                    dangerously_allow_html=True,
                ),
                style={"display": "none"},
            ),
            dcc.Store(id="store-cart-arbol", data=None),
            dcc.Store(id="store-cart-exp", data=[]),
            html.Div(id="tabla-cartera-cont"),
        ]
    )


def _filtrar(df, anio, meses, semanas):
    if df is None:
        return df
    # SOLO Crédito (como la tabla dinámica)
    if COL_TERMINOS in df.columns:
        df = df[df[COL_TERMINOS] == "Crédito"]
    if anio:
        df = df[df[COL_ANIO] == int(anio)]
    if meses:
        df = df[df[COL_MES].isin(meses)]
    if semanas:
        df = df[df[COL_SEMANA].isin(semanas)]
    return df


def registrar_callbacks_tabla_cartera(app):

    @app.callback(
        Output("tabla-cartera-cont", "children"),
        Output("store-cart-arbol", "data"),
        Input("store-bd-cartera", "data"),
        Input("dropdown-anio-cartera", "value"),
        Input("store-mes-cartera", "data"),
        Input("store-semana-cartera", "data"),
        State("store-cart-exp", "data"),
    )
    def construir(marca, anio, meses, semanas, ids_exp):
        df = db.obtener_df(MODULO)
        if df is None:
            return html.Div("Aún no hay datos de Cartera cargados.",
                            style={"color": "#6C757D"}), None
        try:
            df_f = _filtrar(df, anio, meses, semanas)
            if df_f is None or len(df_f) == 0:
                return html.Div("No hay datos para el filtro seleccionado.",
                                style={"color": "#6C757D"}), None

            arbol = construir_arbol_cartera(df_f)
            total = total_general_cartera(df_f)
            visibles = filas_visibles_cartera(arbol, ids_exp or [])

            semanas_txt = ", ".join(str(s) for s in sorted(semanas)) if semanas else "Todas"
            anio_txt = str(anio) if anio else "—"

            grid = dag.AgGrid(
                id="tabla-cartera-grid",
                rowData=visibles.to_dict("records"),
                columnDefs=_column_defs(),
                getRowId={"function": "params.data.id"},
                getRowStyle=_estilo_filas(),
                defaultColDef={"flex": 1, "minWidth": 120, "sortable": False,
                               "filter": False, "resizable": True},
                dashGridOptions={"animateRows": False, "rowHeight": ALTO_FILA,
                                 "headerHeight": ALTO_ENCABEZADO,
                                 "pinnedBottomRowData": [total],
                                 "suppressCellFocus": True},
                className="ag-theme-alpine",
                style=_estilo_grid(_altura_dinamica(len(visibles))),
            )
            contenido = html.Div([
                crear_encabezado_periodo(anio_txt, semanas_txt),
                grid,
            ])
            return contenido, arbol.to_dict("records")
        except Exception as e:
            return html.Div([html.H3("ERROR"), html.Pre(str(e))],
                            style={"color": "red"}), None

    @app.callback(
        Output("store-cart-exp", "data"),
        Input("tabla-cartera-grid", "cellClicked"),
        State("store-cart-exp", "data"),
        prevent_initial_call=True,
    )
    def alternar(celda, ids_exp):
        if celda is None:
            return no_update
        fid = celda.get("rowId")
        if fid is None or "||" in fid or fid == "total":
            return no_update
        ids = set(ids_exp or [])
        if fid in ids:
            ids.discard(fid)
        else:
            ids.add(fid)
        return sorted(ids)

    @app.callback(
        Output("tabla-cartera-grid", "rowData"),
        Output("tabla-cartera-grid", "style"),
        Input("store-cart-exp", "data"),
        State("store-cart-arbol", "data"),
        prevent_initial_call=True,
    )
    def refrescar(ids_exp, arbol_data):
        if arbol_data is None:
            return no_update, no_update
        arbol = pd.DataFrame(arbol_data)
        visibles = filas_visibles_cartera(arbol, ids_exp or [])
        return (visibles.to_dict("records"),
                _estilo_grid(_altura_dinamica(len(visibles))))