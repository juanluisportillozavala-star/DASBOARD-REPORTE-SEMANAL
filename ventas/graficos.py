"""
=========================================================
ventas/graficos.py
=========================================================
GRÁFICOS DE ANÁLISIS de Ventas (Plotly).
Respeta el filtro AÑO + Mes/Semana activo.
"""

from dash import Input, Output, html, dcc, no_update
import db
import pandas as pd
import plotly.graph_objects as go

from core import columnas as C
from core.metricas import margen as _margen
from ventas.filtros import filtrar_dataframe


# =========================================================
# PALETA CORPORATIVA
# =========================================================

AZUL = "#173C73"
AZUL_CLARO = "#3D6BB3"
DORADO = "#D4AF37"
BLANCO = "#FFFFFF"
GRIS = "#6C757D"
GRIS_CLARO = "#EEF2F7"


def _layout_base(titulo, alto=380):
    return dict(
        title=dict(text=titulo, font=dict(color=AZUL, size=18)),
        plot_bgcolor=BLANCO,
        paper_bgcolor=BLANCO,
        font=dict(color=AZUL, family="Segoe UI, Arial, sans-serif"),
        height=alto,
        autosize=False,
        transition=dict(duration=0),
        margin=dict(l=10, r=20, t=50, b=30),
        xaxis=dict(gridcolor=GRIS_CLARO, zeroline=False),
        yaxis=dict(gridcolor=GRIS_CLARO, zeroline=False, automargin=True),
    )


# =========================================================
# AGREGACIÓN (puras)
# =========================================================

def top_n_por(df, columna_dim, columna_metrica, n=10):
    if df is None or len(df) == 0 or columna_dim not in df.columns:
        return pd.DataFrame(columns=[columna_dim, columna_metrica])
    g = (df.groupby(columna_dim)[columna_metrica].sum()
         .sort_values(ascending=False).head(n).reset_index())
    return g


# =========================================================
# FIGURAS (dibujo)
# =========================================================

def fig_top_barras(df, columna_dim, columna_metrica, titulo, moneda=True):
    if df is None or len(df) == 0:
        fig = go.Figure()
        fig.update_layout(**_layout_base(titulo))
        fig.add_annotation(text="Sin datos para el periodo",
                           showarrow=False, font=dict(color=GRIS, size=14))
        return fig

    dim = [str(x)[:32] for x in df[columna_dim].tolist()][::-1]
    val = [float(v) for v in df[columna_metrica].tolist()][::-1]
    fmt = (lambda v: f"${v:,.0f}") if moneda else (lambda v: f"{v:,.0f}")

    fig = go.Figure(go.Bar(
        x=val, y=dim, orientation="h",
        marker_color=AZUL,
        text=[fmt(v) for v in val],
        textposition="outside",
        textfont=dict(color=AZUL, size=12),
        cliponaxis=False,
        hoverinfo="skip",
    ))
    fig.update_layout(**_layout_base(titulo))
    fig.update_layout(margin=dict(l=10, r=90, t=50, b=30))
    return fig


def fig_venta_vs_margen(df, columna_dim, n=10):
    if df is None or len(df) == 0 or columna_dim not in df.columns:
        fig = go.Figure(); fig.update_layout(**_layout_base("Venta vs Margen %"))
        fig.add_annotation(text="Sin datos para el periodo",
                           showarrow=False, font=dict(color=GRIS, size=14))
        return fig

    g = (df.groupby(columna_dim)
         .agg(Venta=(C.RAW_CREDITO, "sum"),
              Utilidad=(C.UT_BRUTA, "sum"))
         .sort_values("Venta", ascending=False).head(n).reset_index())
    g["Margen"] = [(_margen(u, v)) for u, v in zip(g["Utilidad"], g["Venta"])]

    x = [str(v)[:28] for v in g[columna_dim].tolist()]
    ventas = [float(v) for v in g["Venta"].tolist()]
    margenes = [float(m) for m in g["Margen"].tolist()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x, y=ventas, name="Venta MN",
        marker_color=AZUL, yaxis="y",
        hovertemplate="<b>%{x}</b><br>Venta: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=margenes, name="Margen %",
        mode="lines+markers", line=dict(color=DORADO, width=3),
        marker=dict(color=DORADO, size=8), yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Margen: %{y:.1f}%<extra></extra>",
    ))
    base = _layout_base("")
    base["yaxis"] = dict(title="Venta MN", gridcolor=GRIS_CLARO, zeroline=False)
    base["yaxis2"] = dict(title="Margen %", overlaying="y", side="right",
                          showgrid=False, zeroline=False, ticksuffix="%")
    base["xaxis"] = dict(tickangle=-40, gridcolor=GRIS_CLARO)
    base["legend"] = dict(orientation="h", yanchor="bottom", y=1.02,
                          xanchor="center", x=0.5)
    base["title"] = None
    base["height"] = 470
    base["margin"] = dict(l=10, r=20, t=50, b=90)
    base["hovermode"] = "x unified"
    fig.update_layout(**base)
    return fig


def fig_utilidad_unit_vs_margen(df, columna_dim, n=10):
    """Combo: barras de Utilidad UNITARIA (azul) + línea de Margen %
    (dorado) sobre eje secundario. Top N productos por UTILIDAD BRUTA
    total. La barra muestra la utilidad por unidad; la línea, el margen.
    Sirve para ver, entre los productos que más utilidad dejan, cuánto
    ganas por unidad y con qué margen."""
    if df is None or len(df) == 0 or columna_dim not in df.columns:
        fig = go.Figure(); fig.update_layout(**_layout_base("Utilidad unitaria vs Margen %"))
        fig.add_annotation(text="Sin datos para el periodo",
                           showarrow=False, font=dict(color=GRIS, size=14))
        return fig

    cant = C.RAW_CANTIDAD
    g = (df.groupby(columna_dim)
         .agg(Venta=(C.RAW_CREDITO, "sum"),
              Utilidad=(C.UT_BRUTA, "sum"),
              Cantidad=(cant, "sum"))
         .sort_values("Utilidad", ascending=False).head(n).reset_index())

    # utilidad unitaria = utilidad bruta / cantidad (evita división por 0)
    g["UtUnit"] = [
        (u / c) if c not in (0, None) and not pd.isna(c) else 0.0
        for u, c in zip(g["Utilidad"], g["Cantidad"])
    ]
    g["Margen"] = [(_margen(u, v)) for u, v in zip(g["Utilidad"], g["Venta"])]

    x = [str(v)[:28] for v in g[columna_dim].tolist()]
    ut_unit = [float(v) for v in g["UtUnit"].tolist()]
    margenes = [float(m) for m in g["Margen"].tolist()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x, y=ut_unit, name="Utilidad unitaria",
        marker_color=AZUL, yaxis="y",
        hovertemplate="<b>%{x}</b><br>Ut. unitaria: $%{y:,.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=margenes, name="Margen %",
        mode="lines+markers", line=dict(color=DORADO, width=3),
        marker=dict(color=DORADO, size=8), yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Margen: %{y:.1f}%<extra></extra>",
    ))
    base = _layout_base("")
    base["yaxis"] = dict(title="Utilidad unitaria MN", gridcolor=GRIS_CLARO, zeroline=False)
    base["yaxis2"] = dict(title="Margen %", overlaying="y", side="right",
                          showgrid=False, zeroline=False, ticksuffix="%")
    base["xaxis"] = dict(tickangle=-40, gridcolor=GRIS_CLARO)
    base["legend"] = dict(orientation="h", yanchor="bottom", y=1.02,
                          xanchor="center", x=0.5)
    base["title"] = None
    base["height"] = 470
    base["margin"] = dict(l=10, r=20, t=50, b=90)
    base["hovermode"] = "x unified"
    fig.update_layout(**base)
    return fig


def fig_participacion(df, columna_dim, titulo, n=6):
    if df is None or len(df) == 0 or columna_dim not in df.columns:
        fig = go.Figure(); fig.update_layout(**_layout_base(""))
        fig.add_annotation(text="Sin datos para el periodo",
                           showarrow=False, font=dict(color=GRIS, size=14))
        return fig

    serie = df.groupby(columna_dim)[C.UT_BRUTA].sum().sort_values(ascending=False)
    total = float(serie.sum())
    top = serie.head(n)
    otros = float(serie.iloc[n:].sum())

    etiquetas = [str(x)[:26] for x in top.index.tolist()]
    valores = [float(v) for v in top.tolist()]
    if otros > 0:
        etiquetas.append("Otros")
        valores.append(otros)

    colores = ["#0B2D5B", "#173C73", "#2C5090", "#3D6BB3", "#5A85C7",
               "#D4AF37", "#8FA9CC"]
    colores = colores[:len(valores)]
    if otros > 0:
        colores[-1] = GRIS

    fig = go.Figure(go.Pie(
        labels=etiquetas, values=valores, hole=0.55,
        marker=dict(colors=colores, line=dict(color=BLANCO, width=2)),
        textinfo="percent", textposition="inside",
        textfont=dict(color=BLANCO, size=12),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        sort=False,
    ))
    base = _layout_base("")
    base["height"] = 400
    base["margin"] = dict(l=10, r=10, t=20, b=40)
    base["legend"] = dict(orientation="h", yanchor="top", y=0,
                          xanchor="center", x=0.5, font=dict(size=11))
    fig.update_layout(**base)
    fig.add_annotation(text=f"<b>Total</b><br>${total:,.0f}",
                       showarrow=False, font=dict(color=AZUL, size=13),
                       x=0.5, y=0.5, xanchor="center", yanchor="middle")
    return fig


# =========================================================
# LAYOUT + CALLBACKS del bloque de gráficos
# =========================================================

def crear_layout_graficos():
    return html.Div(
        [
            html.H3("Análisis gráfico",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginTop": "10px", "marginBottom": "28px"}),
            html.Div(
                [
                    html.Div(dcc.Graph(id="grafico-top-productos",
                                       responsive=True,
                                       config={"displayModeBar": False},
                                       style={"height": "400px", "width": "100%"}),
                             style={"flex": "1 1 45%", "minWidth": "0",
                                    "boxSizing": "border-box"}),
                    html.Div(dcc.Graph(id="grafico-top-clientes",
                                       responsive=True,
                                       config={"displayModeBar": False},
                                       style={"height": "400px", "width": "100%"}),
                             style={"flex": "1 1 45%", "minWidth": "0",
                                    "boxSizing": "border-box"}),
                ],
                style={"display": "flex", "flexWrap": "wrap", "gap": "24px",
                       "marginBottom": "10px", "width": "100%",
                       "boxSizing": "border-box"},
            ),
            html.Div(
                [
                    html.H4("Venta vs Margen % (Top 10 Productos)",
                            style={"color": AZUL, "fontWeight": "700",
                                   "marginBottom": "4px"}),
                    dcc.Graph(id="grafico-venta-margen",
                              responsive=True,
                              config={"displayModeBar": False},
                              style={"height": "500px", "width": "100%"}),
                ],
                style={"marginTop": "30px", "width": "100%",
                       "boxSizing": "border-box"},
            ),
            # ==============================================
            # NUEVA GRÁFICA: Utilidad unitaria vs Margen %
            # (Top 10 productos por Utilidad Bruta)
            # ==============================================
            html.Div(
                [
                    html.H4("Utilidad unitaria vs Margen % (Top 10 Productos por Utilidad Bruta)",
                            style={"color": AZUL, "fontWeight": "700",
                                   "marginBottom": "4px"}),
                    dcc.Graph(id="grafico-utunit-margen",
                              responsive=True,
                              config={"displayModeBar": False},
                              style={"height": "500px", "width": "100%"}),
                ],
                style={"marginTop": "30px", "width": "100%",
                       "boxSizing": "border-box"},
            ),
            html.H4("Participación / Concentración (por Utilidad Bruta)",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginTop": "34px", "marginBottom": "4px"}),
            html.Div(
                [
                    html.Div(
                        [
                            html.H5("Por Producto",
                                    style={"color": AZUL, "textAlign": "center",
                                           "marginBottom": "0"}),
                            dcc.Graph(id="grafico-part-productos",
                                      responsive=True,
                                      config={"displayModeBar": False},
                                      style={"height": "400px", "width": "100%"}),
                        ],
                        style={"flex": "1 1 45%", "minWidth": "0",
                               "boxSizing": "border-box"}),
                    html.Div(
                        [
                            html.H5("Por Cliente",
                                    style={"color": AZUL, "textAlign": "center",
                                           "marginBottom": "0"}),
                            dcc.Graph(id="grafico-part-clientes",
                                      responsive=True,
                                      config={"displayModeBar": False},
                                      style={"height": "400px", "width": "100%"}),
                        ],
                        style={"flex": "1 1 45%", "minWidth": "0",
                               "boxSizing": "border-box"}),
                ],
                style={"display": "flex", "flexWrap": "wrap", "gap": "24px",
                       "width": "100%", "boxSizing": "border-box"},
            ),
        ],
        style={"padding": "10px 4px"},
    )


def registrar_callbacks_graficos(app):

    @app.callback(
        Output("grafico-top-productos", "figure"),
        Output("grafico-top-clientes", "figure"),
        Output("grafico-venta-margen", "figure"),
        Output("grafico-utunit-margen", "figure"),
        Output("grafico-part-productos", "figure"),
        Output("grafico-part-clientes", "figure"),
        Input("store-bd-ventas", "data"),
        Input("store-anio", "data"),
        Input("store-mes", "data"),
        Input("store-semana", "data"),
        Input("acc-graficos", "active_item"),
    )
    def actualizar_graficos(marca, anio, meses, semanas, item_activo):
        if not item_activo:
            return (no_update, no_update, no_update, no_update, no_update, no_update)

        df = db.obtener_df("ventas")
        if df is None:
            vacio = go.Figure()
            vacio.update_layout(**_layout_base("Sin datos"))
            return vacio, vacio, vacio, vacio, vacio, vacio

        df_f = filtrar_dataframe(df, meses=meses, semanas=semanas, anio=anio)

        col_prod = C.PRODUCTO_2 if C.PRODUCTO_2 in df_f.columns else None
        if col_prod:
            tp = top_n_por(df_f, col_prod, C.UT_BRUTA, n=10)
            fig_prod = fig_top_barras(tp, col_prod, C.UT_BRUTA,
                                      "Top 10 Productos por Utilidad Bruta")
        else:
            fig_prod = go.Figure(); fig_prod.update_layout(**_layout_base("Top 10 Productos"))

        col_cli = C.RAW_CLIENTE if C.RAW_CLIENTE in df_f.columns else None
        if col_cli:
            tc = top_n_por(df_f, col_cli, C.UT_BRUTA, n=10)
            fig_cli = fig_top_barras(tc, col_cli, C.UT_BRUTA,
                                     "Top 10 Clientes por Utilidad Bruta")
        else:
            fig_cli = go.Figure(); fig_cli.update_layout(**_layout_base("Top 10 Clientes"))

        if col_prod:
            fig_vm = fig_venta_vs_margen(df_f, col_prod, n=10)
            fig_uu = fig_utilidad_unit_vs_margen(df_f, col_prod, n=10)
        else:
            fig_vm = go.Figure(); fig_vm.update_layout(**_layout_base("Venta vs Margen %"))
            fig_uu = go.Figure(); fig_uu.update_layout(**_layout_base("Utilidad unitaria vs Margen %"))

        if col_prod:
            fig_pp = fig_participacion(df_f, col_prod, "Por Producto", n=6)
        else:
            fig_pp = go.Figure(); fig_pp.update_layout(**_layout_base(""))
        if col_cli:
            fig_pc = fig_participacion(df_f, col_cli, "Por Cliente", n=6)
        else:
            fig_pc = go.Figure(); fig_pc.update_layout(**_layout_base(""))

        return fig_prod, fig_cli, fig_vm, fig_uu, fig_pp, fig_pc