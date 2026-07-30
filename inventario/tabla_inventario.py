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

FMT_MONEDA = {"function": "params.value == null ? '' : '$' + d3.format(',.2f')(params.value)"}
FMT_NUM = {"function": "params.value == null ? '' : d3.format(',.0f')(params.value)"}


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
                    </style>""",
                    dangerously_allow_html=True,
                ),
                style={"display": "none"},
            ),
            # KPIs
            html.Div(id="inv-kpis",
                     style={"display": "flex", "gap": "16px", "flexWrap": "wrap",
                            "marginBottom": "20px"}),
            # Filtro por ubicación
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
            # Tabla
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
                                  style={"height": "400px"},
                                  config={"responsive": False}),
                        style={"flex": "1", "minWidth": "320px",
                               "maxWidth": "600px"},
                    ),
                    html.Div(
                        dcc.Graph(id="inv-grafico-barras",
                                  style={"height": "400px"},
                                  config={"responsive": False}),
                        style={"flex": "1", "minWidth": "320px",
                               "maxWidth": "600px"},
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
        antig = df["DIAS EN ALMACEN"].mean()
        kpis = [
            _kpi_card("Valor total", f"${valor_total:,.2f}"),
            _kpi_card("Total productos", f"{total_prod:,}"),
            _kpi_card("Antigüedad promedio", f"{antig:.0f} días"),
        ]

        # Pastel: valor por categoría
        cat = df.groupby("CATEGORIA", observed=False)[COL_VALOR].sum().reset_index()
        cat = cat[cat[COL_VALOR] > 0]
        fig_pie = px.pie(cat, values=COL_VALOR, names="CATEGORIA",
                         title="Distribución de valor por categoría",
                         color="CATEGORIA", color_discrete_map=COLOR_CAT)
        fig_pie.update_layout(height=380, autosize=False,
                              margin=dict(t=50, b=20, l=20, r=20))

        # Barras: valor por ubicación
        ubi = df.groupby(COL_UBICACION)[COL_VALOR].sum().reset_index()
        fig_bar = px.bar(ubi, x=COL_UBICACION, y=COL_VALOR,
                         title="Valor por ubicación",
                         color_discrete_sequence=[AZUL])
        fig_bar.update_layout(height=380, autosize=False,
                              margin=dict(t=50, b=20, l=20, r=20))

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