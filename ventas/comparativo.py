"""
=========================================================
ventas/comparativo.py
=========================================================
COMPARATIVO de dos periodos (independiente del filtro de
arriba). Compara los 4 KPIs (Venta, Utilidad, Margen,
Pesos/kilo) entre un Periodo A y un Periodo B.

Modos:
  • Mes vs Mes : cada periodo = año + mes (pueden ser de
    años distintos, ej. mayo 2025 vs mayo 2026).
  • Año vs Año : cada periodo = un año completo.

Salida: tabla con Métrica | Periodo A | Periodo B | Variación.
Lee los datos de la caché del servidor (db.obtener_df).
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_bootstrap_components as dbc
import pandas as pd

import db
from core import columnas as C
from ventas.filtros import obtener_anios

MODULO = "ventas"

AZUL = "#173C73"
DORADO = "#D4AF37"
VERDE = "#28A745"
ROJO = "#C0392B"

MESES_NOMBRE = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre",
    11: "Noviembre", 12: "Diciembre",
}


# =========================================================
# CÁLCULO de las 4 métricas para un subconjunto
# =========================================================

def _metricas(df):
    if df is None or len(df) == 0:
        return {"venta": 0.0, "utilidad": 0.0, "margen": 0.0, "peso_kilo": 0.0}
    venta = float(df[C.RAW_CREDITO].sum())
    utilidad = float(df[C.UT_BRUTA].sum())
    margen = (utilidad / venta * 100) if venta else 0.0
    cantidad = float(df[C.RAW_CANTIDAD].sum()) if C.RAW_CANTIDAD in df.columns else 0.0
    peso_kilo = (utilidad / cantidad) if cantidad else 0.0
    return {"venta": venta, "utilidad": utilidad,
            "margen": margen, "peso_kilo": peso_kilo}


def _filtrar_periodo(df, anio, mes=None):
    if df is None:
        return df
    d = df
    if "Año" in d.columns and anio is not None:
        d = d[d["Año"] == int(anio)]
    if mes is not None and "Mes" in d.columns:
        d = d[d["Mes"] == int(mes)]
    return d


# =========================================================
# LAYOUT
# =========================================================

def _dropdown(id_, placeholder, ancho="150px"):
    return dcc.Dropdown(id=id_, options=[], value=None, clearable=False,
                        placeholder=placeholder,
                        style={"width": ancho, "display": "inline-block"})


def crear_layout_comparativo():
    return html.Div(
        [
            dcc.Store(id="cmp-anios", data=None),

            html.Div(
                [
                    html.Span("Comparar por: ",
                              style={"fontWeight": "600", "color": AZUL,
                                     "marginRight": "10px"}),
                    dcc.RadioItems(
                        id="cmp-modo",
                        options=[
                            {"label": " Mes vs Mes", "value": "mes"},
                            {"label": " Año vs Año", "value": "anio"},
                        ],
                        value="mes",
                        inline=True,
                        inputStyle={"marginRight": "6px", "marginLeft": "14px"},
                    ),
                ],
                style={"marginBottom": "18px"},
            ),

            # ---- Selectores de los dos periodos ----
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H5("Periodo A",
                                        style={"color": AZUL, "fontWeight": "700"}),
                                html.Div(
                                    [
                                        _dropdown("cmp-a-anio", "Año", "110px"),
                                        html.Span(" ", style={"margin": "0 6px"}),
                                        html.Div(_dropdown("cmp-a-mes", "Mes", "150px"),
                                                 id="cmp-a-mes-cont",
                                                 style={"display": "inline-block"}),
                                    ],
                                ),
                            ],
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.H5("Periodo B",
                                        style={"color": DORADO, "fontWeight": "700"}),
                                html.Div(
                                    [
                                        _dropdown("cmp-b-anio", "Año", "110px"),
                                        html.Span(" ", style={"margin": "0 6px"}),
                                        html.Div(_dropdown("cmp-b-mes", "Mes", "150px"),
                                                 id="cmp-b-mes-cont",
                                                 style={"display": "inline-block"}),
                                    ],
                                ),
                            ],
                        ),
                        md=6,
                    ),
                ],
                className="g-3",
                style={"marginBottom": "20px"},
            ),

            html.Div(id="cmp-tabla"),
        ],
        style={"padding": "6px 4px"},
    )


# =========================================================
# TABLA COMPARATIVA
# =========================================================

def _fmt_moneda(v):
    return f"${v:,.2f}"


def _fmt_pct(v):
    return f"{v:.2f}%"


def _variacion(a, b, es_pct=False):
    """Δ (b - a) y % de variación relativa. Devuelve (texto, color)."""
    delta = b - a
    if es_pct:
        # para margen: la variación es en puntos porcentuales
        signo = "+" if delta >= 0 else ""
        color = VERDE if delta >= 0 else ROJO
        return f"{signo}{delta:.2f} pts", color
    # variación relativa %
    if a == 0:
        texto = "—" if b == 0 else "n/d"
        return texto, "#6C757D"
    var = (b - a) / abs(a) * 100
    signo = "+" if var >= 0 else ""
    color = VERDE if var >= 0 else ROJO
    return f"{signo}{var:.1f}%", color


def _construir_tabla(mA, mB, etiqueta_a, etiqueta_b):
    filas_def = [
        ("Venta", "venta", False, _fmt_moneda),
        ("Utilidad Bruta", "utilidad", False, _fmt_moneda),
        ("Margen %", "margen", True, _fmt_pct),
        ("Pesos por Kilo", "peso_kilo", False, _fmt_moneda),
    ]

    encabezado = html.Thead(
        html.Tr([
            html.Th("Métrica", style={"textAlign": "left"}),
            html.Th(etiqueta_a, style={"textAlign": "right", "color": AZUL}),
            html.Th(etiqueta_b, style={"textAlign": "right", "color": DORADO}),
            html.Th("Variación", style={"textAlign": "right"}),
        ]),
    )

    filas = []
    for nombre, clave, es_pct, fmt in filas_def:
        va, vb = mA[clave], mB[clave]
        var_txt, var_color = _variacion(va, vb, es_pct)
        filas.append(html.Tr([
            html.Td(nombre, style={"fontWeight": "600", "color": AZUL}),
            html.Td(fmt(va), style={"textAlign": "right"}),
            html.Td(fmt(vb), style={"textAlign": "right"}),
            html.Td(var_txt, style={"textAlign": "right", "fontWeight": "700",
                                     "color": var_color}),
        ]))

    return dbc.Table(
        [encabezado, html.Tbody(filas)],
        bordered=False, hover=True, striped=True,
        style={"marginTop": "6px"},
    )


# =========================================================
# CALLBACKS
# =========================================================

def registrar_callbacks_comparativo(app):

    # llenar años disponibles en los 4 dropdowns
    @app.callback(
        Output("cmp-a-anio", "options"),
        Output("cmp-b-anio", "options"),
        Output("cmp-a-anio", "value"),
        Output("cmp-b-anio", "value"),
        Input("store-bd-ventas", "data"),
        State("cmp-a-anio", "value"),
        State("cmp-b-anio", "value"),
    )
    def llenar_anios(marca, a_val, b_val):
        df = db.obtener_df(MODULO)
        if df is None:
            return [], [], None, None
        anios = obtener_anios(df)
        ops = [{"label": str(a), "value": int(a)} for a in anios]
        # A = más reciente, B = anterior si existe
        a_sel = a_val if a_val in anios else (anios[0] if anios else None)
        if b_val in anios:
            b_sel = b_val
        else:
            b_sel = anios[1] if len(anios) > 1 else (anios[0] if anios else None)
        return ops, ops, a_sel, b_sel

    # mostrar/ocultar los dropdowns de mes según el modo
    @app.callback(
        Output("cmp-a-mes-cont", "style"),
        Output("cmp-b-mes-cont", "style"),
        Input("cmp-modo", "value"),
    )
    def alternar_mes(modo):
        visible = {"display": "inline-block"}
        oculto = {"display": "none"}
        if modo == "mes":
            return visible, visible
        return oculto, oculto

    # llenar meses disponibles de cada año elegido
    @app.callback(
        Output("cmp-a-mes", "options"),
        Output("cmp-a-mes", "value"),
        Input("cmp-a-anio", "value"),
        State("cmp-a-mes", "value"),
    )
    def meses_a(anio, mes_val):
        return _opciones_meses(anio, mes_val)

    @app.callback(
        Output("cmp-b-mes", "options"),
        Output("cmp-b-mes", "value"),
        Input("cmp-b-anio", "value"),
        State("cmp-b-mes", "value"),
    )
    def meses_b(anio, mes_val):
        return _opciones_meses(anio, mes_val)

    # construir la tabla comparativa
    @app.callback(
        Output("cmp-tabla", "children"),
        Input("cmp-modo", "value"),
        Input("cmp-a-anio", "value"),
        Input("cmp-b-anio", "value"),
        Input("cmp-a-mes", "value"),
        Input("cmp-b-mes", "value"),
        Input("store-bd-ventas", "data"),
    )
    def actualizar(modo, a_anio, b_anio, a_mes, b_mes, marca):
        df = db.obtener_df(MODULO)
        if df is None:
            return html.Div("Aún no hay datos cargados.",
                            style={"color": "#6C757D"})

        if modo == "mes":
            dA = _filtrar_periodo(df, a_anio, a_mes)
            dB = _filtrar_periodo(df, b_anio, b_mes)
            et_a = f"{MESES_NOMBRE.get(a_mes, '—')} {a_anio}" if a_mes else f"{a_anio}"
            et_b = f"{MESES_NOMBRE.get(b_mes, '—')} {b_anio}" if b_mes else f"{b_anio}"
        else:
            dA = _filtrar_periodo(df, a_anio, None)
            dB = _filtrar_periodo(df, b_anio, None)
            et_a = f"Año {a_anio}"
            et_b = f"Año {b_anio}"

        mA = _metricas(dA)
        mB = _metricas(dB)
        return _construir_tabla(mA, mB, et_a, et_b)


def _opciones_meses(anio, mes_val):
    df = db.obtener_df(MODULO)
    if df is None or anio is None or "Mes" not in df.columns:
        return [], None
    d = df[df["Año"] == int(anio)] if "Año" in df.columns else df
    meses = sorted(d["Mes"].dropna().astype(int).unique().tolist())
    ops = [{"label": MESES_NOMBRE.get(m, str(m)), "value": int(m)} for m in meses]
    if mes_val in meses:
        sel = mes_val
    else:
        sel = meses[0] if meses else None
    return ops, sel