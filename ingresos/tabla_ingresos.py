"""
=========================================================
ingresos/tabla_ingresos.py
=========================================================
Tabla jerárquica de Ingresos (Vendedor -> Cliente, expandible)
con columnas cruzadas Contado/Crédito x Vencido/Vigente + Total.
Diseño premium igual al de Ventas (encabezado azul, marcador
dorado por nivel, franja de fecha de corte, fila TOTAL GENERAL).

ESTATUS es dinámico según el mes de corte del calendario
(ver ingresos/arbol_ingresos.py).

Lee los datos de la caché del servidor (db.obtener_df).
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag
import pandas as pd

import db
from ingresos.arbol_ingresos import (
    construir_arbol_ingresos, total_general_ingresos, filas_visibles_ingresos,
    TERMINOS, ESTATUS, CAMPOS_CRUCE, _campo,
)

MODULO = "ingresos"
COL_MES = "MES"
COL_SEMANA = "SEMANA"
COL_MES_VENC = "MES_VENCIMIENTO"

AZUL = "#173C73"
DORADO = "#D4AF37"

ALTO_FILA = 34
ALTO_ENCABEZADO = 38

FMT_MONEDA = {"function": "params.value == null ? '' : '$' + d3.format(',.2f')(params.value)"}


# =========================================================
# COLUMNAS con encabezados agrupados (Contado/Crédito > Venc/Vig)
# =========================================================

def _column_defs():
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
    for t in TERMINOS:
        hijos = []
        for e in ESTATUS:
            hijos.append({
                "field": _campo(t, e),
                "headerName": e,
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
    """Mismo esquema por nivel que Ventas:
    nivel 0 = TOTAL (azul), nivel 1 = vendedor (dorado),
    nivel 2 = cliente (crema)."""
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


def crear_encabezado_periodo(fecha_corte, semanas_texto):
    return html.Div(
        [
            html.Span("Fecha de corte:  ",
                      style={"color": DORADO, "fontWeight": "bold", "marginLeft": "24px"}),
            html.Span(fecha_corte,
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
            # CSS que fuerza el texto BLANCO en los encabezados
            # (normal y de grupo Contado/Crédito), por si las
            # variables de AG Grid no bastan en esta versión.
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
            # stores del árbol de ingresos (expansión + cache del árbol)
            dcc.Store(id="store-ing-arbol", data=None),
            dcc.Store(id="store-ing-total", data=None),
            dcc.Store(id="store-ing-exp", data=[]),
            html.Div(id="tabla-ingresos-cont"),
        ]
    )


def _filtrar(df, meses, semanas):
    if df is None:
        return df
    if meses:
        df = df[df[COL_MES].isin(meses)]
    if semanas:
        df = df[df[COL_SEMANA].isin(semanas)]
    return df


def _fecha_corte_texto(meses):
    if meses:
        import calendar
        m = max(meses)
        nombres = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return f"Corte a {nombres[m]}"
    return "Todos los meses"


def registrar_callbacks_tabla_ingresos(app):

    # Construir árbol cuando cambian datos/filtro
    @app.callback(
        Output("tabla-ingresos-cont", "children"),
        Output("store-ing-arbol", "data"),
        Output("store-ing-total", "data"),
        Input("store-bd-ingresos", "data"),
        Input("store-mes-ingresos", "data"),
        Input("store-semana-ingresos", "data"),
        State("store-ing-exp", "data"),
    )
    def construir(marca, meses, semanas, ids_exp):
        df = db.obtener_df(MODULO)
        if df is None:
            return html.Div("Aún no hay datos de Ingresos cargados.",
                            style={"color": "#6C757D"}), None, None
        try:
            df_f = _filtrar(df, meses, semanas)
            if df_f is None or len(df_f) == 0:
                return html.Div("No hay datos para el filtro seleccionado.",
                                style={"color": "#6C757D"}), None, None

            arbol = construir_arbol_ingresos(df_f, meses)
            total = total_general_ingresos(df_f, meses)

            semanas_txt = ", ".join(str(s) for s in sorted(semanas)) if semanas else "Todas"
            visibles = filas_visibles_ingresos(arbol, ids_exp or [])

            grid = dag.AgGrid(
                id="tabla-ingresos-grid",
                rowData=visibles.to_dict("records"),
                columnDefs=_column_defs(),
                getRowId={"function": "params.data.id"},
                getRowStyle=_estilo_filas(),
                defaultColDef={"flex": 1, "minWidth": 130, "sortable": False,
                               "filter": False, "resizable": True},
                dashGridOptions=_opciones_grid([total]),
                className="ag-theme-alpine",
                style=_estilo_grid("600px"),
            )
            contenido = html.Div([
                crear_encabezado_periodo(_fecha_corte_texto(meses), semanas_txt),
                grid,
            ])
            return contenido, arbol.to_dict("records"), total
        except Exception as e:
            return html.Div([html.H3("ERROR"), html.Pre(str(e))],
                            style={"color": "red"}), None, None

    # Expandir/contraer al hacer clic en un vendedor
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
        # solo nivel 1 (vendedores) se expande: su id NO tiene "||"
        if "||" in fid or fid == "total":
            return no_update
        ids = set(ids_exp or [])
        if fid in ids:
            ids.discard(fid)
        else:
            ids.add(fid)
        return sorted(ids)

    # Refresco ligero al expandir/contraer (redibuja filas visibles)
    @app.callback(
        Output("tabla-ingresos-grid", "rowData"),
        Input("store-ing-exp", "data"),
        State("store-ing-arbol", "data"),
        prevent_initial_call=True,
    )
    def refrescar(ids_exp, arbol_data):
        if arbol_data is None:
            return no_update
        arbol = pd.DataFrame(arbol_data)
        visibles = filas_visibles_ingresos(arbol, ids_exp or [])
        return visibles.to_dict("records")