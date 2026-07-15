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

                # ======================================================
                # MES
                # ======================================================

                dbc.Row(

                    [

                        dbc.Col(

                            html.H3(

                                "Mes",

                                style={

                                    "color": "#173C73",

                                    "fontWeight": "600",

                                    "marginBottom": "0"

                                }

                            ),

                            width="auto"

                        ),

                        dbc.Col(

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

                                style={

                                    "display": "flex",

                                    "justifyContent": "flex-end",

                                    "gap": "15px"

                                }

                            )

                        )

                    ],

                    align="center",

                    className="mb-3"

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

                    className="contenedor-meses"

                ),

                html.Br(),

                html.Br(),

                # ======================================================
                # SEMANA
                # ======================================================

                dbc.Row(

                    [

                        dbc.Col(

                            html.H3(

                                "Semana",

                                style={

                                    "color": "#173C73",

                                    "fontWeight": "600",

                                    "marginBottom": "0"

                                }

                            ),

                            width="auto"

                        ),

                        dbc.Col(

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

                                style={

                                    "display": "flex",

                                    "justifyContent": "flex-end",

                                    "gap": "15px"

                                }

                            )

                        )

                    ],

                    align="center",

                    className="mb-3"

                ),

                html.Div(

                    id="selector-semanas",

                    className="contenedor-semanas"

                )

            ]

        ),

        className="card-premium"

    )