"""
=========================================================
CONTROLES DEL DASHBOARD
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_controles():

    return dbc.Card(

        dbc.CardBody(

            [

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

                                                    id="seleccionar-todos-meses",

                                                    title="Seleccionar todos"

                                                ),

                                                html.I(

                                                    className="fas fa-filter-circle-xmark filtro-icono",

                                                    id="limpiar-meses",

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

                                                "type": "btn-mes",

                                                "index": i

                                            },

                                            n_clicks=0,

                                            color="light",

                                            outline=True,

                                            className="cuadro-mes"

                                        )

                                        for i in range(1, 13)

                                    ],

                                    id="selector-meses",

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

                                                    id="seleccionar-todas-semanas",

                                                    title="Seleccionar todas"

                                                ),

                                                html.I(

                                                    className="fas fa-filter-circle-xmark filtro-icono",

                                                    id="limpiar-semanas",

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

                                                "type": "btn-semana",

                                                "index": i

                                            },

                                            n_clicks=0,

                                            color="light",

                                            outline=True,

                                            className="cuadro-semana",

                                            style={

                                                "gridRow": (i - 1) // 13 + 1,

                                                "gridColumn": (i - 1) % 13 + 1

                                            }

                                        )

                                        for i in range(1, 54)

                                    ],

                                    id="selector-semanas",

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