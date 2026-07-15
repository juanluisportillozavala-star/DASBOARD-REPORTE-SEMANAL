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

                # =====================================================
                # MESES
                # =====================================================

                html.Div(

                    [

                        # ---------------------------------------------
                        # Encabezado
                        # ---------------------------------------------

                        html.Div(

                            [

                                html.H3(

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

                        # ---------------------------------------------
                        # Botones de meses
                        # ---------------------------------------------

                        html.Div(

                            [

                                dbc.Button(

                                    str(i),

                                    id={

                                        "type": "btn-mes",

                                        "index": i

                                    },

                                    color="light",

                                    outline=True,

                                    n_clicks=0,

                                    className="cuadro-mes"

                                )

                                for i in range(1, 13)

                            ],

                            id="selector-meses",

                            className="grid-meses"

                        )

                    ],

                    className="bloque-filtro"

                ),

                html.Hr(

                    className="my-4"

                ),

                # =====================================================
                # SEMANAS
                # =====================================================

                html.Div(

                    [

                        html.Div(

                            [

                                html.H3(

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

                            id="selector-semanas",

                            className="grid-semanas"

                        )

                    ],

                    className="bloque-filtro"

                )

            ]

        ),

        className="card-premium"

    )