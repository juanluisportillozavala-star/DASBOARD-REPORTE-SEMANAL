"""
=========================================================
CONTROLES DEL MÓDULO SALDO PROVEEDOR
=========================================================
Segmentador de AÑO (filtro maestro) + calendario Mes/Semana.
IDs con sufijo "-sp".
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
                                                    id="seleccionar-todos-meses-sp",
                                                    title="Seleccionar todos",
                                                ),
                                                html.I(
                                                    className="fas fa-filter-circle-xmark filtro-icono",
                                                    id="limpiar-meses-sp",
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
                                            id={"type": "btn-mes-sp", "index": i},
                                            n_clicks=0, color="light", outline=True,
                                            className="cuadro-mes",
                                        )
                                        for i in range(1, 13)
                                    ],
                                    id="selector-meses-sp",
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
                                                    id="seleccionar-todas-semanas-sp",
                                                    title="Seleccionar todas",
                                                ),
                                                html.I(
                                                    className="fas fa-filter-circle-xmark filtro-icono",
                                                    id="limpiar-semanas-sp",
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
                                            id={"type": "btn-semana-sp", "index": i},
                                            n_clicks=0, color="light", outline=True,
                                            className="cuadro-semana",
                                        )
                                        for i in range(1, 54)
                                    ],
                                    id="selector-semanas-sp",
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