"""
=========================================================
CONTROLES DEL MÓDULO CARTERA
=========================================================
Calendario Mes/Semana propio de Cartera. Mismos estilos que
Ventas/Ingresos, con IDs con sufijo "-cartera" para no chocar
con los callbacks de los otros módulos.

Nota: en Cartera, Mes y Semana provienen de la FECHA de
referencia (la que se captura al cargar), igual para todas las
filas; por eso normalmente habrá un solo mes/semana activo.
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_controles_cartera():

    return dbc.Card(
        dbc.CardBody(
            [
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
                                            style={"gridRow": (i - 1) // 13 + 1,
                                                   "gridColumn": (i - 1) % 13 + 1},
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
                )
            ]
        ),
        className="card-premium",
    )