"""
=========================================================
ventas/graficos.py
=========================================================
GRÁFICOS DE ANÁLISIS de Ventas (Plotly).

Separa, como el resto del proyecto:
  • agregación (funciones puras que devuelven DataFrames)
  • dibujo (funciones que devuelven figuras Plotly con la
    paleta corporativa)
  • layout + callbacks (el bloque que se enchufa en la página)

Reutiliza core.columnas para los nombres y ventas.filtros
para respetar el filtro Mes/Semana activo.

Paleta corporativa (acorde a las tablas):
  AZUL   #173C73   DORADO #D4AF37   BLANCO #FFFFFF
  + grises de apoyo y un azul claro para segundas series.
"""

from dash import Input, Output, html, dcc
import pandas as pd
import plotly.graph_objects as go

from core import columnas as C
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

# Layout base compartido por todas las figuras, para que se
# vean homogéneas y con la marca.
def _layout_base(titulo, alto=380):
    return dict(
        title=dict(text=titulo, font=dict(color=AZUL, size=18)),
        plot_bgcolor=BLANCO,
        paper_bgcolor=BLANCO,
        font=dict(color=AZUL, family="Segoe UI, Arial, sans-serif"),
        height=alto,
        autosize=False,          # evita el bucle de recálculo de tamaño
        transition=dict(duration=0),  # sin animación (era el "se expande sin parar")
        margin=dict(l=10, r=20, t=50, b=30),
        xaxis=dict(gridcolor=GRIS_CLARO, zeroline=False),
        yaxis=dict(gridcolor=GRIS_CLARO, zeroline=False, automargin=True),
    )


# =========================================================
# AGREGACIÓN (puras)
# =========================================================

def top_n_por(df, columna_dim, columna_metrica, n=10):
    """Top N de una dimensión (Producto 2 / cliente / vendedor)
    por una métrica, de mayor a menor."""
    if df is None or len(df) == 0 or columna_dim not in df.columns:
        return pd.DataFrame(columns=[columna_dim, columna_metrica])
    g = (df.groupby(columna_dim)[columna_metrica].sum()
         .sort_values(ascending=False).head(n).reset_index())
    return g


# =========================================================
# FIGURAS (dibujo)
# =========================================================

def fig_top_barras(df, columna_dim, columna_metrica, titulo, moneda=True):
    """Barras horizontales de un Top N. Barras azules, etiqueta
    de valor dorada, orden de mayor (arriba) a menor (abajo)."""
    if df is None or len(df) == 0:
        fig = go.Figure()
        fig.update_layout(**_layout_base(titulo))
        fig.add_annotation(text="Sin datos para el periodo",
                           showarrow=False, font=dict(color=GRIS, size=14))
        return fig

    # invertir para que el mayor quede ARRIBA en barras horizontales.
    # IMPORTANTE: usar LISTAS planas, no Series de pandas — una Series
    # invertida con [::-1] conserva su índice invertido y Plotly puede
    # desalinear x/y al reordenar por índice (bug de la "barra única").
    dim = [str(x)[:32] for x in df[columna_dim].tolist()][::-1]
    val = [float(v) for v in df[columna_metrica].tolist()][::-1]
    fmt = (lambda v: f"${v:,.0f}") if moneda else (lambda v: f"{v:,.0f}")

    fig = go.Figure(go.Bar(
        x=val, y=dim, orientation="h",
        marker_color=AZUL,
        text=[fmt(v) for v in val],
        textposition="outside",          # SIEMPRE afuera: visible en barras chicas
        textfont=dict(color=AZUL, size=12),
        cliponaxis=False,                # que el texto no se recorte en el borde
        hoverinfo="skip",                # sin tooltip al pasar el mouse
    ))
    fig.update_layout(**_layout_base(titulo))
    # margen derecho amplio para que quepan las etiquetas de valor afuera
    fig.update_layout(margin=dict(l=10, r=90, t=50, b=30))
    return fig


def fig_venta_vs_margen(df, columna_dim, n=10):
    """Combo: barras de Venta (azul) + línea de Margen % (dorado)
    sobre eje secundario. Top N por Venta. Sirve para ver qué
    entradas venden mucho pero con margen bajo (o al revés)."""
    from core.metricas import margen as _margen

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
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=margenes, name="Margen %",
        mode="lines+markers", line=dict(color=DORADO, width=3),
        marker=dict(color=DORADO, size=8), yaxis="y2",
        hoverinfo="skip",
    ))
    base = _layout_base("Venta vs Margen % (Top 10 Productos)")
    base["yaxis"] = dict(title="Venta MN", gridcolor=GRIS_CLARO, zeroline=False)
    base["yaxis2"] = dict(title="Margen %", overlaying="y", side="right",
                          showgrid=False, zeroline=False, ticksuffix="%")
    base["xaxis"] = dict(tickangle=-40, gridcolor=GRIS_CLARO)
    base["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, x=0)
    base["height"] = 440
    fig.update_layout(**base)
    return fig


# =========================================================
# LAYOUT + CALLBACKS del bloque de gráficos
# =========================================================

def crear_layout_graficos():
    """Bloque de gráficos de análisis (respeta filtro Mes/Semana)."""
    return html.Div(
        [
            html.H3("Análisis gráfico",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginTop": "20px", "marginBottom": "16px"}),
            html.Div(
                [
                    html.Div(dcc.Graph(id="grafico-top-productos",
                                       responsive=False,
                                       config={"displayModeBar": False},
                                       style={"height": "400px"}),
                             style={"flex": "1", "minWidth": "420px"}),
                    html.Div(dcc.Graph(id="grafico-top-clientes",
                                       responsive=False,
                                       config={"displayModeBar": False},
                                       style={"height": "400px"}),
                             style={"flex": "1", "minWidth": "420px"}),
                ],
                style={"display": "flex", "flexWrap": "wrap", "gap": "20px"},
            ),
            html.Div(
                dcc.Graph(id="grafico-venta-margen",
                          responsive=False,
                          config={"displayModeBar": False},
                          style={"height": "460px"}),
                style={"marginTop": "20px"},
            ),
        ]
    )


def registrar_callbacks_graficos(app):

    @app.callback(
        Output("grafico-top-productos", "figure"),
        Output("grafico-top-clientes", "figure"),
        Output("grafico-venta-margen", "figure"),
        Input("store-bd-ventas", "data"),
        Input("store-mes", "data"),
        Input("store-semana", "data"),
    )
    def actualizar_graficos(data, meses, semanas):
        if data is None:
            vacio = go.Figure()
            vacio.update_layout(**_layout_base("Sin datos"))
            return vacio, vacio, vacio

        df = pd.DataFrame(data)
        df_f = filtrar_dataframe(df, meses=meses, semanas=semanas)

        # Top 10 productos por Ut Bruta (columna real: Producto 2)
        col_prod = C.PRODUCTO_2 if C.PRODUCTO_2 in df_f.columns else None
        if col_prod:
            tp = top_n_por(df_f, col_prod, C.UT_BRUTA, n=10)
            fig_prod = fig_top_barras(tp, col_prod, C.UT_BRUTA,
                                      "Top 10 Productos por Utilidad Bruta")
        else:
            fig_prod = go.Figure(); fig_prod.update_layout(**_layout_base("Top 10 Productos"))

        # Top 10 clientes por Ut Bruta
        col_cli = C.RAW_CLIENTE if C.RAW_CLIENTE in df_f.columns else None
        if col_cli:
            tc = top_n_por(df_f, col_cli, C.UT_BRUTA, n=10)
            fig_cli = fig_top_barras(tc, col_cli, C.UT_BRUTA,
                                     "Top 10 Clientes por Utilidad Bruta")
        else:
            fig_cli = go.Figure(); fig_cli.update_layout(**_layout_base("Top 10 Clientes"))

        # Venta vs Margen % por producto
        if col_prod:
            fig_vm = fig_venta_vs_margen(df_f, col_prod, n=10)
        else:
            fig_vm = go.Figure(); fig_vm.update_layout(**_layout_base("Venta vs Margen %"))

        return fig_prod, fig_cli, fig_vm