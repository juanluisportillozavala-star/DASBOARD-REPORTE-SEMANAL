"""
=========================================================
inventario/tabla_inventario.py
=========================================================
Tabla PLANA de productos de inventario con diseño premium
(encabezado azul, filas con marcador dorado). Incluye KPIs,
filtro por ubicación y gráficos (pastel categoría + barras
ubicación). Lee de la caché del servidor (db.obtener_df).
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd

import db
from inventario.procesamiento import (
    COL_PRODUCTO, COL_UBICACION, COL_UNIDAD, COL_CANTIDAD,
    COL_VALOR, CAT_1, CAT_2, CAT_3,
)

MODULO = "inventario"
AZUL = "#173C73"
DORADO = "#D4AF37"

COLOR_CAT = {CAT_1: "#2ecc71", CAT_2: "#f1c40f", CAT_3: "#e74c3c"}
# tonos suaves para pintar celdas de cada rango (verde/amarillo/rojo)
COLOR_CAT_SUAVE = {CAT_1: "#D5F5E3", CAT_2: "#FCF3CF", CAT_3: "#FADBD8"}
RANGOS = [CAT_1, CAT_2, CAT_3]

FMT_MONEDA = {"function": "params.value == null ? '' : '$' + d3.format(',.2f')(params.value)"}
FMT_NUM = {"function": "params.value == null ? '' : d3.format(',.0f')(params.value)"}
FMT_PCT = {"function": "params.value == null ? '' : d3.format(',.1f')(params.value) + '%'"}


def _estilo_grid_simple(alto):
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


# =========================================================
# TABLA 1: Resumen por Rango
# =========================================================

def _tabla_resumen_rango(df):
    valor_total = df[COL_VALOR].sum()
    filas = []
    for r in RANGOS:
        sub = df[df["CATEGORIA"] == r]
        val = sub[COL_VALOR].sum()
        filas.append({
            "rango": r,
            "n_productos": len(sub),
            "cantidad": float(sub[COL_CANTIDAD].sum()),
            "valor": float(val),
            "pct": (val / valor_total * 100) if valor_total else 0,
        })
    fila_total = {
        "rango": "Total", "n_productos": len(df),
        "cantidad": float(df[COL_CANTIDAD].sum()),
        "valor": float(valor_total), "pct": 100.0,
    }

    col_defs = [
        {"field": "rango", "headerName": "Rango", "minWidth": 140,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-inv",
         "cellStyle": {"fontWeight": "700"}},
        {"field": "n_productos", "headerName": "N° de productos",
         "type": "numericColumn", "valueFormatter": FMT_NUM, "minWidth": 130,
         "sortable": False, "filter": False, "headerClass": "hdr-inv"},
        {"field": "cantidad", "headerName": "Cantidad en inventario",
         "type": "numericColumn", "valueFormatter": FMT_NUM, "minWidth": 160,
         "sortable": False, "filter": False, "headerClass": "hdr-inv"},
        {"field": "valor", "headerName": "Valor", "type": "numericColumn",
         "valueFormatter": FMT_MONEDA, "minWidth": 150,
         "sortable": False, "filter": False, "headerClass": "hdr-inv"},
        {"field": "pct", "headerName": "% del valor", "type": "numericColumn",
         "valueFormatter": FMT_PCT, "minWidth": 110,
         "sortable": False, "filter": False, "headerClass": "hdr-inv"},
    ]

    return dag.AgGrid(
        rowData=filas,
        columnDefs=col_defs,
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
        style=_estilo_grid_simple("auto"),
    )


# =========================================================
# TABLA 2: Resumen Ubicación x Rango
# =========================================================

def _tabla_resumen_ubicacion(df):
    valor_total = df[COL_VALOR].sum()

    filas = []
    for u in sorted(df[COL_UBICACION].dropna().unique().tolist()):
        subu = df[df[COL_UBICACION] == u]
        fila = {"ubicacion": u}
        tot_u = 0.0
        for r in RANGOS:
            s = subu[subu["CATEGORIA"] == r]
            val = float(s[COL_VALOR].sum())
            fila[f"cant_{r}"] = float(s[COL_CANTIDAD].sum())
            fila[f"val_{r}"] = val
            tot_u += val
        fila["valor_total"] = tot_u
        fila["pct"] = (tot_u / valor_total * 100) if valor_total else 0
        filas.append(fila)

    # fila total
    ftot = {"ubicacion": "Total"}
    for r in RANGOS:
        s = df[df["CATEGORIA"] == r]
        ftot[f"cant_{r}"] = float(s[COL_CANTIDAD].sum())
        ftot[f"val_{r}"] = float(s[COL_VALOR].sum())
    ftot["valor_total"] = float(valor_total)
    ftot["pct"] = 100.0

    # columnas con grupos por rango (color en el encabezado de grupo)
    col_defs = [
        {"field": "ubicacion", "headerName": "Ubicación", "minWidth": 170,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-inv",
         "cellStyle": {"fontWeight": "600", "color": AZUL}},
    ]
    for r in RANGOS:
        col_defs.append({
            "headerName": r,
            "headerClass": "hdr-inv",
            "children": [
                {"field": f"cant_{r}", "headerName": "Cantidad",
                 "type": "numericColumn", "valueFormatter": FMT_NUM,
                 "minWidth": 110, "sortable": False, "filter": False,
                 "headerClass": "hdr-inv"},
                {"field": f"val_{r}", "headerName": "Valor",
                 "type": "numericColumn", "valueFormatter": FMT_MONEDA,
                 "minWidth": 130, "sortable": False, "filter": False,
                 "headerClass": "hdr-inv"},
            ],
        })
    col_defs.append({"field": "valor_total", "headerName": "Valor total",
                     "type": "numericColumn", "valueFormatter": FMT_MONEDA,
                     "minWidth": 140, "pinned": "right", "sortable": False,
                     "filter": False, "headerClass": "hdr-inv",
                     "cellStyle": {"fontWeight": "700", "color": AZUL}})
    col_defs.append({"field": "pct", "headerName": "% del total",
                     "type": "numericColumn", "valueFormatter": FMT_PCT,
                     "minWidth": 110, "pinned": "right", "sortable": False,
                     "filter": False, "headerClass": "hdr-inv"})

    return dag.AgGrid(
        rowData=filas,
        columnDefs=col_defs,
        dashGridOptions={"animateRows": False, "rowHeight": 34,
                         "headerHeight": 38, "groupHeaderHeight": 38,
                         "domLayout": "autoHeight",
                         "pinnedBottomRowData": [ftot],
                         "suppressCellFocus": True},
        getRowStyle={"function":
            "params.node.rowPinned ? "
            "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : {}"},
        defaultColDef={"resizable": True, "sortable": False, "filter": False,
                       "flex": 1, "minWidth": 110},
        className="ag-theme-alpine",
        style=_estilo_grid_simple("auto"),
    )


def _column_defs():
    return [
        {"field": COL_UBICACION, "headerName": "Ubicación", "minWidth": 160,
         "pinned": "left", "filter": False, "sortable": True,
         "headerClass": "hdr-inv"},
        {"field": COL_PRODUCTO, "headerName": "Producto", "minWidth": 320,
         "filter": False, "sortable": True, "headerClass": "hdr-inv"},
        {"field": COL_UNIDAD, "headerName": "Unidad", "minWidth": 90,
         "filter": False, "sortable": False, "headerClass": "hdr-inv"},
        {"field": COL_CANTIDAD, "headerName": "Cantidad", "type": "numericColumn",
         "valueFormatter": FMT_NUM, "minWidth": 110, "filter": False,
         "sortable": True, "headerClass": "hdr-inv"},
        {"field": "DIAS EN ALMACEN", "headerName": "Días en almacén",
         "type": "numericColumn", "valueFormatter": FMT_NUM, "minWidth": 130,
         "filter": False, "sortable": True, "headerClass": "hdr-inv"},
        {"field": "CATEGORIA", "headerName": "Categoría", "minWidth": 120,
         "filter": False, "sortable": True, "headerClass": "hdr-inv",
         "cellStyle": {"function":
             "params.value === '61+ días' ? {color:'#e74c3c',fontWeight:'700'} : "
             "params.value === '31-60 días' ? {color:'#b8860b',fontWeight:'700'} : "
             "{color:'#2ecc71',fontWeight:'700'}"}},
        {"field": COL_VALOR, "headerName": "Valor", "type": "numericColumn",
         "valueFormatter": FMT_MONEDA, "minWidth": 140, "pinned": "right",
         "filter": False, "sortable": True, "headerClass": "hdr-inv"},
    ]


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


def _kpi_card(titulo, valor, color=AZUL):
    return html.Div(
        [
            html.Div(titulo, style={"fontSize": "13px", "color": "#6C757D",
                                    "marginBottom": "6px"}),
            html.Div(valor, style={"fontSize": "24px", "fontWeight": "700",
                                   "color": color}),
        ],
        style={"backgroundColor": "#FFFFFF", "padding": "18px 22px",
               "borderRadius": "12px", "borderTop": f"4px solid {DORADO}",
               "boxShadow": "0 4px 16px rgba(23,60,115,0.08)", "flex": "1",
               "minWidth": "180px"},
    )


def crear_layout_tabla_inventario():
    return html.Div(
        [
            html.Div(
                dcc.Markdown(
                    """<style>
                    .hdr-inv, .hdr-inv .ag-header-cell-text { color:#FFFFFF !important; }
                    .hdr-inv-verde, .hdr-inv-verde .ag-header-cell-text,
                    .hdr-inv-verde .ag-header-group-text,
                    .hdr-inv-amarillo, .hdr-inv-amarillo .ag-header-cell-text,
                    .hdr-inv-amarillo .ag-header-group-text,
                    .hdr-inv-rojo, .hdr-inv-rojo .ag-header-cell-text,
                    .hdr-inv-rojo .ag-header-group-text { color:#FFFFFF !important; }
                    </style>""",
                    dangerously_allow_html=True,
                ),
                style={"display": "none"},
            ),
            # KPIs
            html.Div(id="inv-kpis",
                     style={"display": "flex", "gap": "16px", "flexWrap": "wrap",
                            "marginBottom": "20px"}),

            # ===== TABLAS RESUMEN (NO responden al filtro) =====
            html.H4("Resumen por rango de antigüedad",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.Div(id="inv-tabla-rango", style={"marginBottom": "24px"}),

            html.H4("Resumen por ubicación y rango",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.Div(id="inv-tabla-ubicacion", style={"marginBottom": "24px"}),

            # Filtro por ubicación (solo afecta al detalle y gráficos)
            html.Div(
                [
                    html.Label("Filtrar por ubicación:",
                               style={"fontWeight": "600", "color": AZUL,
                                      "marginRight": "10px"}),
                    dcc.Dropdown(id="inv-filtro-ubicacion", multi=True,
                                 placeholder="Todas las ubicaciones",
                                 style={"minWidth": "320px"}),
                ],
                style={"display": "flex", "alignItems": "center",
                       "marginBottom": "18px"},
            ),
            # Tabla de detalle
            html.H4("Detalle de productos",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.Div(id="inv-tabla-cont"),

            html.Br(),

            # Gráficos AL FINAL. Altura fija (400px) para evitar el
            # bucle de auto-redimensionamiento de Plotly dentro de flex.
            html.H4("Análisis gráfico",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginTop": "20px", "marginBottom": "10px"}),
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="inv-grafico-pastel",
                                  style={"height": "400px", "width": "100%"},
                                  config={"responsive": True,
                                          "displayModeBar": False}),
                        style={"flex": "1 1 45%", "minWidth": "320px"},
                    ),
                    html.Div(
                        dcc.Graph(id="inv-grafico-barras",
                                  style={"height": "400px", "width": "100%"},
                                  config={"responsive": True,
                                          "displayModeBar": False}),
                        style={"flex": "1 1 45%", "minWidth": "320px"},
                    ),
                ],
                style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
            ),
        ]
    )


def _df_filtrado(ubicaciones):
    df = db.obtener_df(MODULO)
    if df is None:
        return None
    if ubicaciones:
        df = df[df[COL_UBICACION].isin(ubicaciones)]
    return df


def registrar_callbacks_inventario(app):

    # Tablas RESUMEN: solo dependen de la carga (NO del filtro).
    # Siempre muestran TODO el inventario.
    @app.callback(
        Output("inv-tabla-rango", "children"),
        Output("inv-tabla-ubicacion", "children"),
        Input("store-bd-inventario", "data"),
    )
    def actualizar_resumenes(marca):
        df = db.obtener_df(MODULO)
        if df is None or len(df) == 0:
            vacio = html.Div("Sin datos.", style={"color": "#6C757D"})
            return vacio, vacio
        return _tabla_resumen_rango(df), _tabla_resumen_ubicacion(df)

    # opciones del filtro de ubicación (al cargar datos)
    @app.callback(
        Output("inv-filtro-ubicacion", "options"),
        Input("store-bd-inventario", "data"),
    )
    def opciones_ubicacion(marca):
        df = db.obtener_df(MODULO)
        if df is None:
            return []
        ubis = sorted(df[COL_UBICACION].dropna().unique().tolist())
        return [{"label": u, "value": u} for u in ubis]

    # KPIs + gráficos + tabla (reaccionan al filtro y a la carga)
    @app.callback(
        Output("inv-kpis", "children"),
        Output("inv-grafico-pastel", "figure"),
        Output("inv-grafico-barras", "figure"),
        Output("inv-tabla-cont", "children"),
        Input("store-bd-inventario", "data"),
        Input("inv-filtro-ubicacion", "value"),
    )
    def actualizar(marca, ubicaciones):
        df = _df_filtrado(ubicaciones)
        if df is None or len(df) == 0:
            vacio = px.pie(names=[], values=[])
            return ([html.Div("Sin datos de inventario.",
                              style={"color": "#6C757D"})],
                    vacio, vacio, html.Div())

        # KPIs
        valor_total = df[COL_VALOR].sum()
        total_prod = len(df)
        # Antigüedad PONDERADA por cantidad en inventario (kg/L):
        # promedio de "DIAS EN ALMACEN" pesado por la cantidad de cada
        # producto -> "en promedio, cada kg/L lleva X días parado".
        # Solo cuentan productos con días válidos (notna).
        _peso = df[COL_CANTIDAD].where(df["DIAS EN ALMACEN"].notna())
        antig = ((df["DIAS EN ALMACEN"] * _peso).sum() / _peso.sum()
                 if _peso.sum() else float("nan"))
        kpis = [
            _kpi_card("Valor total", f"${valor_total:,.2f}"),
            _kpi_card("Total productos", f"{total_prod:,}"),
            _kpi_card("Antigüedad promedio (por kg/L)",
                      f"{antig:.0f} días" if pd.notna(antig) else "—"),
        ]

        # Pastel: valor por categoría
        cat = df.groupby("CATEGORIA", observed=False)[COL_VALOR].sum().reset_index()
        cat = cat[cat[COL_VALOR] > 0]
        fig_pie = px.pie(cat, values=COL_VALOR, names="CATEGORIA",
                         title="Distribución de valor por categoría",
                         color="CATEGORIA", color_discrete_map=COLOR_CAT)
        fig_pie.update_layout(height=380,
                              paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(t=50, b=20, l=20, r=20))

        # Barras: valor por ubicación (valor fijo encima, sin hover)
        ubi = df.groupby(COL_UBICACION)[COL_VALOR].sum().reset_index()
        ubi["etiqueta"] = ubi[COL_VALOR].apply(lambda v: f"${v:,.0f}")
        fig_bar = px.bar(ubi, x=COL_UBICACION, y=COL_VALOR,
                         title="Valor por ubicación",
                         text="etiqueta",
                         color_discrete_sequence=[AZUL])
        fig_bar.update_traces(
            textposition="outside",
            textfont=dict(color=AZUL, size=12),
            hoverinfo="skip", hovertemplate=None,
        )
        fig_bar.update_layout(height=380,
                              paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(t=50, b=20, l=20, r=20),
                              yaxis=dict(range=[0, ubi[COL_VALOR].max() * 1.15]))

        # Tabla
        grid = dag.AgGrid(
            id="inv-grid",
            rowData=df.to_dict("records"),
            columnDefs=_column_defs(),
            defaultColDef={"resizable": True, "sortable": True,
                           "filter": False, "flex": 1, "minWidth": 110},
            dashGridOptions={"animateRows": False, "rowHeight": 32,
                             "headerHeight": 38},
            className="ag-theme-alpine",
            style=_estilo_grid("600px"),
        )
        return kpis, fig_pie, fig_bar, grid