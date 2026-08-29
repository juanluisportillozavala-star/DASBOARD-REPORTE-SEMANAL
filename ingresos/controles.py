"""
=========================================================
CONTROLES DEL MÓDULO INGRESOS
=========================================================
Segmentador de AÑO (filtro maestro, como Ventas) + calendario
Mes/Semana. IDs con sufijo "-ingresos" para no chocar con Ventas.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def crear_controles_ingresos():

    return dbc.Card(

        dbc.CardBody(

            [

                # =====================================================
                # SEGMENTADOR DE AÑO (filtro maestro)
                # =====================================================
                dbc.Row(
                    dbc.Col(
                        [
                            html.Div(
                                [html.H4("Año", className="titulo-filtro")],
                                className="encabezado-filtro",
                            ),
                            dcc.Dropdown(
                                id="dropdown-anio-ingresos",
                                options=[],      # las llena el callback
                                value=None,      # el callback pone el más reciente
                                clearable=False,
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

                        # =====================================================
                        # MESES
                        # =====================================================

                        dbc.Col(

                            [

                                html.Div(

                                    [

                                        html.H4(

                                            "Mes",

                                            className="titulo-filtro"

                                        ),

                                        html.Div(

                                            [

                                                html.I(

                                                    className="fas fa-check-double filtro-icono",

                                                    id="seleccionar-todos-meses-ingresos",

                                                    title="Seleccionar todos"

                                                ),

                                                html.I(

                                                    className="fas fa-filter-circle-xmark filtro-icono",

                                                    id="limpiar-meses-ingresos",

                                                    title="Limpiar selección"

                                                )

                                            ],

                                            className="acciones-filtro"

                                        )

                                    ],

                                    className="encabezado-filtro"

                                ),

                                html.Div(

                                    [

                                        dbc.Button(

                                            str(i),

                                            id={

                                                "type": "btn-mes-ingresos",

                                                "index": i

                                            },

                                            n_clicks=0,

                                            color="light",

                                            outline=True,

                                            className="cuadro-mes"

                                        )

                                        for i in range(1, 13)

                                    ],

                                    id="selector-meses-ingresos",

                                    className="grid-meses"

                                )

                            ],

                            md=3

                        ),

                        # =====================================================
                        # SEMANAS
                        # =====================================================

                        dbc.Col(

                            [

                                html.Div(

                                    [

                                        html.H4(

                                            "Semana",

                                            className="titulo-filtro"

                                        ),

                                        html.Div(

                                            [

                                                html.I(

                                                    className="fas fa-check-double filtro-icono",

                                                    id="seleccionar-todas-semanas-ingresos",

                                                    title="Seleccionar todas"

                                                ),

                                                html.I(

                                                    className="fas fa-filter-circle-xmark filtro-icono",

                                                    id="limpiar-semanas-ingresos",

                                                    title="Limpiar selección"

                                                )

                                            ],

                                            className="acciones-filtro"

                                        )

                                    ],

                                    className="encabezado-filtro"

                                ),

                                html.Div(

                                    [

                                        dbc.Button(

                                            str(i),

                                            id={

                                                "type": "btn-semana-ingresos",

                                                "index": i

                                            },

                                            n_clicks=0,

                                            color="light",

                                            outline=True,

                                            className="cuadro-semana",

                                        )

                                        for i in range(1, 54)

                                    ],

                                    id="selector-semanas-ingresos",

                                    className="grid-semanas"

                                )

                            ],

                            md=9

                        )

                    ],

                    className="g-4"

                )

            ]

        ),

        className="card-premium"

    )