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

                # ==========================================
                # MESES
                # ==========================================

                html.H4(

                    "Mes",

                    style={

                        "color": "#173C73",

                        "fontWeight": "600",

                        "marginBottom": "15px"

                    }

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

                    className="selector-meses"

                ),

                html.Br(),

                # ==========================================
                # SEMANAS
                # ==========================================

                html.H4(

                    "Semana",

                    style={

                        "color": "#173C73",

                        "fontWeight": "600",

                        "marginBottom": "15px"

                    }

                ),

                html.Div(

                    id="selector-semanas",

                    className="selector-semanas"

                )

            ]

        ),

        className="card-premium"

    )