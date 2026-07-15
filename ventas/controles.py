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

                        # ==========================================
                        # MESES
                        # ==========================================

                        dbc.Col(

                            [

                                html.H5(

                                    "Mes",

                                    className="mb-3"

                                ),

                                dbc.ButtonGroup(

                                    [

                                        dbc.Button(

                                            str(i),

                                            id={
                                                "type": "btn-mes",
                                                "index": i
                                            },

                                            color="light",

                                            outline=True,

                                            className="btn-mes"

                                        )

                                        for i in range(1,7)

                                    ],

                                    className="mb-2"

                                ),

                                html.Br(),

                                dbc.ButtonGroup(

                                    [

                                        dbc.Button(

                                            str(i),

                                            id=f"btn-mes-{i}",

                                            color="light",

                                            outline=True,

                                            className="btn-mes"

                                        )

                                        for i in range(7,13)

                                    ]

                                )

                            ],

                            md=5

                        ),

                        # ==========================================
                        # SEMANAS
                        # ==========================================

                        dbc.Col(

                            [

                                html.H5(

                                    "Semana",

                                    className="mb-3"

                                ),

                                html.Div(

                                    id="selector-semanas"

                                )

                            ],

                            md=7

                        )

                    ]

                )

            ]

        ),

        className="card-premium"

    )