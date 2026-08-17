"""
=========================================================
inventario/historico.py  —  PESTAÑA "HISTÓRICO" del módulo
Inventario
=========================================================
Muestra una foto mensual GUARDADA (una a la vez): eliges año y
mes y se ve el inventario tal como quedó, con las MISMAS tablas,
KPIs y gráficos del inventario actual.

Lee de db.leer_inventario_historico(anio, mes) (tabla
inventario_historico), NO de la caché del inventario semanal.

Reutiliza los constructores visuales de tabla_inventario.py para
verse idéntico, sin duplicar ni tocar ese archivo.
"""

import dash_ag_grid as dag
import plotly.express as px
import pandas as pd
from dash import Input, Output, html, dcc

import db
from inventario.procesamiento import (
    COL_PRODUCTO, COL_UBICACION, COL_CANTIDAD, COL_VALOR,
)
from inventario.tabla_inventario import (
    _tabla_resumen_rango, _tabla_resumen_ubicacion,
    _column_defs, _estilo_grid, _kpi_card,
    COLOR_CAT, AZUL, DORADO,
)

MESES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]
_MES_NOMBRE = dict(MESES)


def crear_layout_historico():
    """Layout de la pestaña Histórico. Los años se llenan al
    construir la página (refleja lo guardado al abrir el módulo)."""
    anios = db.anios_con_historico_inv()
    anio_val = anios[0] if anios else None

    return html.Div(
        [
            html.P("Consulta una foto mensual del inventario ya guardada. "
                   "Elige el año y el mes; se muestra tal como se cargó "
                   "en «Carga de datos».",
                   style={"color": "#6C757D", "marginBottom": "16px"}),

            # selectores año / mes
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="invh-anio",
                                options=[{"label": str(a), "value": a}
                                         for a in anios],
                                value=anio_val, clearable=False,
                                placeholder="Año",
                                style={"width": "140px"},
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.Label("Mes", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="invh-mes", options=[], value=None,
                                clearable=False, placeholder="Mes",
                                style={"width": "180px"},
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            html.Div(id="invh-info",
                     style={"marginBottom": "16px", "fontSize": "13px",
                            "color": "#6C757D"}),

            # KPIs
            html.Div(id="invh-kpis",
                     style={"display": "flex", "gap": "16px",
                            "flexWrap": "wrap", "marginBottom": "20px"}),

            # Tablas resumen
            html.H4("Resumen por rango de antigüedad",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.Div(id="invh-tabla-rango", style={"marginBottom": "24px"}),

            html.H4("Resumen por ubicación y rango",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.Div(id="invh-tabla-ubicacion", style={"marginBottom": "24px"}),

            # Detalle
            html.H4("Detalle de productos",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "10px"}),
            html.Div(id="invh-tabla-detalle"),

            html.Br(),

            # Gráficos
            html.H4("Análisis gráfico",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginTop": "20px", "marginBottom": "10px"}),
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="invh-graf-pastel",
                                  style={"height": "400px", "width": "100%"},
                                  config={"responsive": True,
                                          "displayModeBar": False}),
                        style={"flex": "1 1 45%", "minWidth": "320px"},
                    ),
                    html.Div(
                        dcc.Graph(id="invh-graf-barras",
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


def registrar_callbacks_historico_inv(app):

    # --- alternar pestañas: paneles SIEMPRE montados, solo se
    #     muestran/ocultan (así ningún callback queda huérfano) ---
    @app.callback(
        Output("inv-panel-actual", "style"),
        Output("inv-panel-historico", "style"),
        Input("inv-tabs", "value"),
    )
    def _alternar(tab):
        oculto = {"display": "none"}
        visible = {"display": "block"}
        if tab == "historico":
            return oculto, visible
        return visible, oculto

    # --- meses disponibles al cambiar el año ---
    @app.callback(
        Output("invh-mes", "options"),
        Output("invh-mes", "value"),
        Input("invh-anio", "value"),
    )
    def _meses(anio):
        if not anio:
            return [], None
        meses = db.meses_con_historico_inv(anio)
        opciones = [{"label": _MES_NOMBRE.get(m, str(m)), "value": m}
                    for m in meses]
        valor = meses[-1] if meses else None   # el mes más reciente
        return opciones, valor

    # --- render de la foto seleccionada ---
    @app.callback(
        Output("invh-info", "children"),
        Output("invh-kpis", "children"),
        Output("invh-tabla-rango", "children"),
        Output("invh-tabla-ubicacion", "children"),
        Output("invh-tabla-detalle", "children"),
        Output("invh-graf-pastel", "figure"),
        Output("invh-graf-barras", "figure"),
        Input("invh-anio", "value"),
        Input("invh-mes", "value"),
    )
    def _render(anio, mes):
        fig_vacia = px.pie(names=[], values=[])
        vacio = html.Div()

        if not anio or not mes:
            aviso = html.Div("Selecciona un año y un mes guardado.",
                             style={"color": "#6C757D"})
            return aviso, [], vacio, vacio, vacio, fig_vacia, fig_vacia

        df = db.leer_inventario_historico(anio, mes)
        if df is None or len(df) == 0:
            aviso = html.Div(
                f"No hay inventario guardado para "
                f"{int(mes):02d}/{anio}.",
                style={"color": "#C0392B"})
            return aviso, [], vacio, vacio, vacio, fig_vacia, fig_vacia

        # los datos vienen de JSON: reasegurar tipos numéricos
        for col in [COL_CANTIDAD, COL_VALOR, "DIAS EN ALMACEN"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # línea de info (fecha de corte / cuándo se guardó)
        info = db.info_inventario_historico(anio, mes)
        etiqueta = f"Foto de {_MES_NOMBRE.get(int(mes), mes)} {anio}"
        if info:
            if info.get("fecha_corte"):
                etiqueta += f" · fecha de corte: {info['fecha_corte']}"
            if info.get("actualizado"):
                etiqueta += f" · guardado: {info['actualizado']}"
        info_div = html.Div(etiqueta, style={"fontStyle": "italic"})

        # KPIs (mismos que el inventario actual)
        valor_total = df[COL_VALOR].sum()
        total_prod = len(df)
        antig = df["DIAS EN ALMACEN"].mean()
        kpis = [
            _kpi_card("Valor total", f"${valor_total:,.2f}"),
            _kpi_card("Total productos", f"{total_prod:,}"),
            _kpi_card("Antigüedad promedio",
                      f"{antig:.0f} días" if pd.notna(antig) else "—"),
        ]

        # tablas resumen (reutilizadas de tabla_inventario)
        t_rango = _tabla_resumen_rango(df)
        t_ubic = _tabla_resumen_ubicacion(df)

        # detalle
        grid = dag.AgGrid(
            id="invh-grid",
            rowData=df.to_dict("records"),
            columnDefs=_column_defs(),
            defaultColDef={"resizable": True, "sortable": True,
                           "filter": False, "flex": 1, "minWidth": 110},
            dashGridOptions={"animateRows": False, "rowHeight": 32,
                             "headerHeight": 38},
            className="ag-theme-alpine",
            style=_estilo_grid("600px"),
        )

        # pastel: valor por categoría
        cat = df.groupby("CATEGORIA", observed=False)[COL_VALOR].sum().reset_index()
        cat = cat[cat[COL_VALOR] > 0]
        fig_pie = px.pie(cat, values=COL_VALOR, names="CATEGORIA",
                         title="Distribución de valor por categoría",
                         color="CATEGORIA", color_discrete_map=COLOR_CAT)
        fig_pie.update_layout(height=380,
                              paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(t=50, b=20, l=20, r=20))

        # barras: valor por ubicación
        ubi = df.groupby(COL_UBICACION)[COL_VALOR].sum().reset_index()
        ubi["etiqueta"] = ubi[COL_VALOR].apply(lambda v: f"${v:,.0f}")
        fig_bar = px.bar(ubi, x=COL_UBICACION, y=COL_VALOR,
                         title="Valor por ubicación",
                         text="etiqueta",
                         color_discrete_sequence=[AZUL])
        fig_bar.update_traces(textposition="outside",
                              textfont=dict(color=AZUL, size=12),
                              hoverinfo="skip", hovertemplate=None)
        tope = ubi[COL_VALOR].max() if len(ubi) else 0
        fig_bar.update_layout(height=380,
                              paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(t=50, b=20, l=20, r=20),
                              yaxis=dict(range=[0, (tope or 1) * 1.15]))

        return info_div, kpis, t_rango, t_ubic, grid, fig_pie, fig_bar