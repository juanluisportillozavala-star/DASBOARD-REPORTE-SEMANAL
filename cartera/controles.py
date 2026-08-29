"""
=========================================================
CONTROLES DEL MÓDULO CARTERA
=========================================================
Segmentador de AÑO + calendario. Aquí la SEMANA es de
selección ÚNICA (una a la vez): cada semana es un corte de
aging distinto. El MES solo se resalta (no filtra), por eso su
fila no tiene iconos de acción. IDs con sufijo "-cartera".
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def crear_controles_cartera():

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
                                id="dropdown-anio-cartera",
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
                                            id={"type": "btn-mes-cartera", "index": i},
                                            n_clicks=0, color="light", outline=True,
                                            className="cuadro-mes",
                                        )
                                        for i in range(1, 13)
                                    ],
                                    id="selector-meses-cartera",
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
                                            id={"type": "btn-semana-cartera", "index": i},
                                            n_clicks=0, color="light", outline=True,
                                            className="cuadro-semana",
                                        )
                                        for i in range(1, 54)
                                    ],
                                    id="selector-semanas-cartera",
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