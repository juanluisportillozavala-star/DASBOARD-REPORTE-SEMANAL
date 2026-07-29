"""
=========================================================
ingresos/tabla_ingresos.py
=========================================================
Tabla dinámica (pivote) de Ingresos:
  Filas    : Vendedor
  Columnas : Contado/Crédito (nivel 1) x Vencido/Vigente (nivel 2)
  Valores  : suma de "Importe sin impuestos firmado"
  Totales  : por fila (Total general) y fila de totales al pie.

Look: AG Grid con encabezados agrupados (columnGroup), mismo
estilo que las tablas de Ventas. Celdas sin datos: en blanco.
Lee los datos de la CACHÉ del servidor (db.obtener_df).
"""

from dash import Input, Output, html, dcc, no_update
import dash_ag_grid as dag
import pandas as pd

import db

MODULO = "ingresos"
COL_IMPORTE = "Importe sin impuestos firmado"
COL_VENDEDOR = "Vendedor"
COL_TERMINOS = "TERMINOS DE PAGO"   # Contado / Crédito
COL_ESTATUS = "ESTATUS"             # Vencido / Vigente
COL_MES = "MES"
COL_SEMANA = "SEMANA"

AZUL = "#173C73"

# Orden fijo de las columnas cruzadas (como el Excel)
TERMINOS = ["Contado", "Crédito"]
ESTATUS = ["Vencido", "Vigente"]

FMT_MONEDA = {"function": "params.value == null ? '' : d3.format(',.2f')(params.value)"}


def _pivote(df):
    """Devuelve (filas, totales_fila) del pivote Vendedor x
    (Terminos, Estatus). Cada fila es un dict listo para AG Grid."""
    filas = []
    vendedores = sorted(df[COL_VENDEDOR].dropna().unique().tolist())

    # acumulador de totales por columna
    tot_col = {(t, e): 0.0 for t in TERMINOS for e in ESTATUS}
    tot_general = 0.0

    for v in vendedores:
        sub = df[df[COL_VENDEDOR] == v]
        fila = {"vendedor": v}
        total_fila = 0.0
        for t in TERMINOS:
            for e in ESTATUS:
                key = f"{t}|{e}"
                monto = sub[(sub[COL_TERMINOS] == t) & (sub[COL_ESTATUS] == e)][COL_IMPORTE].sum()
                if monto and not pd.isna(monto) and monto != 0:
                    fila[key] = float(monto)
                    total_fila += float(monto)
                    tot_col[(t, e)] += float(monto)
                else:
                    fila[key] = None   # en blanco
        fila["total"] = total_fila if total_fila else None
        tot_general += total_fila
        filas.append(fila)

    # fila de totales al pie (pinned)
    fila_total = {"vendedor": "Total general"}
    for t in TERMINOS:
        for e in ESTATUS:
            val = tot_col[(t, e)]
            fila_total[f"{t}|{e}"] = val if val else None
    fila_total["total"] = tot_general if tot_general else None

    return filas, fila_total


def _column_defs():
    """Definición de columnas con encabezados AGRUPADOS:
    Contado -> [Vencido, Vigente], Crédito -> [Vencido, Vigente]."""
    defs = [
        {"headerName": "Vendedor", "field": "vendedor",
         "pinned": "left", "width": 220,
         "cellStyle": {"fontWeight": "600", "color": AZUL}},
    ]
    for t in TERMINOS:
        hijos = []
        for e in ESTATUS:
            hijos.append({
                "headerName": e,
                "field": f"{t}|{e}",
                "type": "numericColumn",
                "valueFormatter": FMT_MONEDA,
                "width": 130,
            })
        defs.append({"headerName": t, "children": hijos})
    defs.append({
        "headerName": "Total general", "field": "total",
        "type": "numericColumn", "valueFormatter": FMT_MONEDA,
        "width": 150, "pinned": "right",
        "cellStyle": {"fontWeight": "700", "color": AZUL},
    })
    return defs


def crear_layout_tabla_ingresos():
    return html.Div(
        [
            html.H4("Ingresos por Vendedor — Contado/Crédito × Vencido/Vigente",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginTop": "10px", "marginBottom": "12px"}),
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


def registrar_callbacks_tabla_ingresos(app):

    @app.callback(
        Output("tabla-ingresos-cont", "children"),
        Input("store-bd-ingresos", "data"),
        Input("store-mes-ingresos", "data"),
        Input("store-semana-ingresos", "data"),
    )
    def construir(marca, meses, semanas):
        df = db.obtener_df(MODULO)
        if df is None:
            return html.Div("Aún no hay datos de Ingresos cargados.",
                            style={"color": "#6C757D"})
        try:
            df_f = _filtrar(df, meses, semanas)
            if df_f is None or len(df_f) == 0:
                return html.Div("No hay datos para el filtro seleccionado.",
                                style={"color": "#6C757D"})

            filas, fila_total = _pivote(df_f)

            grid = dag.AgGrid(
                id="tabla-ingresos-grid",
                columnDefs=_column_defs(),
                rowData=filas,
                dashGridOptions={
                    "pinnedBottomRowData": [fila_total],
                    "domLayout": "autoHeight",
                    "suppressCellFocus": True,
                },
                defaultColDef={"resizable": True, "sortable": False,
                               "suppressMovable": True},
                style={"width": "100%"},
                className="ag-theme-alpine",
            )
            return grid
        except Exception as e:
            return html.Div([html.H3("ERROR"), html.Pre(str(e))],
                            style={"color": "red"})