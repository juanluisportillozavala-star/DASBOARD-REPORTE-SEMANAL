"""
=========================================================
TARJETAS KPI
=========================================================
Cada tarjeta muestra: ícono, título, valor, y una BARRA DE
PROGRESO hacia el objetivo anual con su porcentaje y la meta.
La barra se pinta verde si se alcanzó el objetivo (>=100%),
dorada si va en progreso.
"""

from dash import html
import dash_bootstrap_components as dbc

AZUL = "#173C73"
DORADO = "#D4AF37"
VERDE = "#28A745"


def _barra_progreso(pct, objetivo_texto):
    """Barra de avance hacia el objetivo + % + meta."""
    pct_barra = min(pct, 100)          # la barra no pasa de 100% visual
    color = VERDE if pct >= 100 else DORADO
    pct_txt = f"{pct:.0f}%"

    return html.Div(
        [
            # barra
            html.Div(
                html.Div(
                    style={
                        "width": f"{pct_barra}%",
                        "height": "8px",
                        "backgroundColor": color,
                        "borderRadius": "6px",
                        "transition": "width 0.4s ease",
                    },
                ),
                style={
                    "width": "100%",
                    "height": "8px",
                    "backgroundColor": "#E9ECEF",
                    "borderRadius": "6px",
                    "overflow": "hidden",
                    "marginTop": "10px",
                },
            ),
            # % y meta
            html.Div(
                [
                    html.Span(pct_txt,
                              style={"fontWeight": "700", "color": color,
                                     "fontSize": "13px"}),
                    html.Span(f" · Meta: {objetivo_texto}",
                              style={"color": "#6C757D", "fontSize": "12px"}),
                ],
                style={"marginTop": "5px"},
            ),
        ]
    )


def crear_card(icono, titulo, valor, color, pct=None, objetivo_texto=None):

    cuerpo = [
        html.Div(
            [
                html.Div(
                    html.I(
                        className=icono,
                        style={"fontSize": "34px", "color": color},
                    ),
                    style={"width": "60px", "display": "flex",
                           "alignItems": "center", "justifyContent": "center"},
                ),
                html.Div(
                    [
                        html.Div(
                            titulo,
                            style={"fontSize": "15px", "color": "#6C757D",
                                   "fontWeight": "600"},
                        ),
                        html.Div(
                            valor,
                            style={"fontSize": "28px", "fontWeight": "bold",
                                   "color": AZUL, "marginTop": "5px"},
                        ),
                    ],
                    style={"flex": "1"},
                ),
            ],
            style={"display": "flex", "alignItems": "center"},
        ),
    ]

    # barra de progreso (si hay objetivo)
    if pct is not None and objetivo_texto is not None:
        cuerpo.append(_barra_progreso(pct, objetivo_texto))

    return dbc.Card(
        dbc.CardBody(cuerpo),
        className="card-premium",
        style={"borderLeft": f"6px solid {color}"},
    )


def crear_cards(kpis):

    return dbc.Row(
        [
            dbc.Col(
                crear_card(
                    "fas fa-dollar-sign", "Venta Total",
                    kpis["venta_total"], "#28A745",
                    pct=kpis.get("venta_pct"),
                    objetivo_texto=kpis.get("venta_obj"),
                ),
                md=3,
            ),
            dbc.Col(
                crear_card(
                    "fas fa-chart-line", "Utilidad Bruta",
                    kpis["utilidad_bruta"], "#0D6EFD",
                    pct=kpis.get("utilidad_pct"),
                    objetivo_texto=kpis.get("utilidad_obj"),
                ),
                md=3,
            ),
            dbc.Col(
                crear_card(
                    "fas fa-percent", "Margen Bruto",
                    kpis["margen"], "#F39C12",
                    pct=kpis.get("margen_pct"),
                    objetivo_texto=kpis.get("margen_obj"),
                ),
                md=3,
            ),
            dbc.Col(
                crear_card(
                    "fas fa-weight-hanging", "Pesos por Kilo",
                    kpis["peso_kilo"], "#8E44AD",
                    pct=kpis.get("peso_kilo_pct"),
                    objetivo_texto=kpis.get("peso_kilo_obj"),
                ),
                md=3,
            ),
        ],
        className="g-4",
    )