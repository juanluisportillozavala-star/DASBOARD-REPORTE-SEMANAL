"""
=========================================================
CONTROLES DEL MÓDULO CARTERA
=========================================================
Segmentador de AÑO (filtro maestro, como Ventas/Ingresos) +
calendario Mes/Semana. IDs con sufijo "-cartera".
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
                        # ===== MESES =====
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H4("Mes", className="titulo-filtro"),
                                        html.Div(
                                            [
                                                html.I(
                                                    className="fas fa-check-double filtro-icono",
                                                    id="seleccionar-todos-meses-cartera",
                                                    title="Seleccionar todos",
                                                ),
                                                html.I(
                                                    className="fas fa-filter-circle-xmark filtro-icono",
                                                    id="limpiar-meses-cartera",
                                                    title="Limpiar selección",
                                                ),
                                            ],
                                            className="acciones-filtro",
                                        ),
                                    ],
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
                            ],
                            md=3,
                        ),
                        # ===== SEMANAS =====
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H4("Semana", className="titulo-filtro"),
                                        html.Div(
                                            [
                                                html.I(
                                                    className="fas fa-check-double filtro-icono",
                                                    id="seleccionar-todas-semanas-cartera",
                                                    title="Seleccionar todas",
                                                ),
                                                html.I(
                                                    className="fas fa-filter-circle-xmark filtro-icono",
                                                    id="limpiar-semanas-cartera",
                                                    title="Limpiar selección",
                                                ),
                                            ],
                                            className="acciones-filtro",
                                        ),
                                    ],
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