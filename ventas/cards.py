"""
=========================================================
TARJETAS KPI
=========================================================
Cada tarjeta: ícono, título, valor, y barra de progreso hacia
el objetivo anual con su % y meta.

RESPONSIVO:
  - Celular (xs)          -> 1 tarjeta por fila
  - Laptop / monitor (md) -> 2 tarjetas por fila  (layout que se ve bien)
  - Monitor ANCHO (xxl)   -> 4 tarjetas por fila  (solo >=1400px, donde caben)

El valor (monto) NUNCA se recorta: usa fuente flexible y, si hiciera
falta, baja de renglón; jamás se corta con "...".
"""

from dash import html
import dash_bootstrap_components as dbc

AZUL = "#173C73"
DORADO = "#D4AF37"
VERDE = "#28A745"


def _barra_progreso(pct, objetivo_texto):
    pct_barra = min(pct, 100)
    color = VERDE if pct >= 100 else DORADO
    pct_txt = f"{pct:.0f}%"
    return html.Div(
        [
            html.Div(
                html.Div(
                    style={"width": f"{pct_barra}%", "height": "8px",
                           "backgroundColor": color, "borderRadius": "6px",
                           "transition": "width 0.4s ease"},
                ),
                style={"width": "100%", "height": "8px",
                       "backgroundColor": "#E9ECEF", "borderRadius": "6px",
                       "overflow": "hidden", "marginTop": "10px"},
            ),
            html.Div(
                [
                    html.Span(pct_txt, style={"fontWeight": "700",
                                              "color": color, "fontSize": "13px"}),
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
                # ícono
                html.Div(
                    html.I(className=icono,
                           style={"fontSize": "30px", "color": color}),
                    style={"width": "48px", "minWidth": "48px",
                           "display": "flex", "alignItems": "center",
                           "justifyContent": "center"},
                ),
                # texto (título + valor)
                html.Div(
                    [
                        html.Div(titulo,
                                 style={"fontSize": "14px", "color": "#6C757D",
                                        "fontWeight": "600",
                                        "lineHeight": "1.2",
                                        # el título parte SOLO entre palabras,
                                        # nunca a media palabra ("Ven ta")
                                        "wordBreak": "normal",
                                        "overflowWrap": "normal"}),
                        html.Div(
                            valor,
                            style={
                                # tamaño FLEXIBLE: se adapta al ancho de la
                                # tarjeta (entre 20px y 26px).
                                "fontSize": "clamp(20px, 1.8vw, 26px)",
                                "fontWeight": "bold", "color": AZUL,
                                "marginTop": "4px",
                                "lineHeight": "1.15",
                                # SIN nowrap/ellipsis: el monto se ve completo.
                                # Si algún día no cupiera, baja de renglón; nunca
                                # se recorta con "...".
                                "wordBreak": "normal",
                                "overflowWrap": "normal",
                            },
                            title=valor,   # tooltip con el valor completo
                        ),
                    ],
                    style={"flex": "1", "minWidth": "0"},  # minWidth 0 = permite achicar
                ),
            ],
            style={"display": "flex", "alignItems": "center", "gap": "10px"},
        ),
    ]
    if pct is not None and objetivo_texto is not None:
        cuerpo.append(_barra_progreso(pct, objetivo_texto))

    return dbc.Card(
        dbc.CardBody(cuerpo),
        className="card-premium",
        style={"borderLeft": f"6px solid {color}", "height": "100%"},
    )


def crear_cards(kpis):
    defs = [
        ("fas fa-dollar-sign", "Venta Total", kpis["venta_total"], "#28A745",
         kpis.get("venta_pct"), kpis.get("venta_obj")),
        ("fas fa-chart-line", "Utilidad Bruta", kpis["utilidad_bruta"], "#0D6EFD",
         kpis.get("utilidad_pct"), kpis.get("utilidad_obj")),
        ("fas fa-percent", "Margen Bruto", kpis["margen"], "#F39C12",
         kpis.get("margen_pct"), kpis.get("margen_obj")),
        ("fas fa-weight-hanging", "Pesos por Kilo", kpis["peso_kilo"], "#8E44AD",
         kpis.get("peso_kilo_pct"), kpis.get("peso_kilo_obj")),
    ]
    columnas = [
        dbc.Col(
            crear_card(ic, tit, val, col, pct=p, objetivo_texto=obj),
            xs=12, md=6, xxl=3,         # celular 1, laptop 2, monitor ancho 4
            className="mb-3",           # separación vertical al apilarse
        )
        for (ic, tit, val, col, p, obj) in defs
    ]
    return dbc.Row(columnas, className="g-3")