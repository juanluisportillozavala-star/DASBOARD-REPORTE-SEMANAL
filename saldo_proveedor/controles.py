"""
=========================================================
CONTROLES DEL MÓDULO SALDO PROVEEDOR
=========================================================
Segmentador de AÑO + calendario. La SEMANA es de selección
ÚNICA (una a la vez): cada semana es un corte de aging. El MES
solo se resalta (no filtra). IDs con sufijo "-sp".
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def crear_controles_sp():

    return dbc.Card(
        dbc.CardBody(
            [
                # ===== AÑO (filtro maestro) =====
                dbc.Row(
                    dbc.Col(
                        [
                            html.Div(
                                [html.H4("Año", className="titulo-filtro")],
                                className="encabezado-filtro",
                            ),
                            dcc.Dropdown(
                                id="dropdown-anio-sp",
                                options=[], value=None, clearable=False,
                                placeholder="Selecciona un año",
                                style={"maxWidth": "220px"},
                            ),
                        ],
                        md=12,
                    ),
                    className="mb-3",
                ),

                dbc.Row(
                    [
                        # ===== MES (solo informativo: resalta) =====
                        dbc.Col(
                            [
                                html.Div(
                                    [html.H4("Mes", className="titulo-filtro")],
                                    className="encabezado-filtro",
                                ),
                                html.Div(
                                    [
                                        dbc.Button(
                                            str(i),
                                            id={"type": "btn-mes-sp", "index": i},
                                            n_clicks=0, color="light", outline=True,
                                            className="cuadro-mes",
                                        )
                                        for i in range(1, 13)
                                    ],
                                    id="selector-meses-sp",
                                    className="grid-meses",
                                ),
                                html.Small(
                                    "El mes se resalta según la semana elegida.",
                                    style={"color": "#98A6B8"},
                                ),
                            ],
                            md=3,
                        ),
                        # ===== SEMANA (selección ÚNICA) =====
                        dbc.Col(
                            [
                                html.Div(
                                    [html.H4("Semana", className="titulo-filtro")],
                                    className="encabezado-filtro",
                                ),
                                html.Div(
                                    [
                                        dbc.Button(
                                            str(i),
                                            id={"type": "btn-semana-sp", "index": i},
                                            n_clicks=0, color="light", outline=True,
                                            className="cuadro-semana",
                                        )
                                        for i in range(1, 54)
                                    ],
                                    id="selector-semanas-sp",
                                    className="grid-semanas",
                                ),
                                html.Small(
                                    "Selecciona una semana (una a la vez).",
                                    style={"color": "#98A6B8"},
                                ),
                            ],
                            md=9,
                        ),
                    ],
                    className="g-4",
                ),
            ]
        ),
        className="card-premium",
    )