"""
=========================================================
CONTROLES DEL DASHBOARD
=========================================================
"""

from dash import html


def crear_controles():

    return html.Div(

        [

            # =====================================================
            # MESES
            # =====================================================

            html.Div(

                [

                    html.H5(

                        "Mes",

                        style={

                            "marginBottom": "12px",

                            "color": "#173C73",

                            "fontWeight": "600"

                        }

                    ),

                    html.Div(

                        [

                            html.Div(

                                str(i),

                                id={

                                    "type": "btn-mes",

                                    "index": i

                                },

                                className="cuadro-mes"

                            )

                            for i in range(1, 13)

                        ],

                        className="selector-meses"

                    )

                ]

            ),

            html.Br(),

            # =====================================================
            # SEMANAS
            # =====================================================

            html.Div(

                [

                    html.H5(

                        "Semana",

                        style={

                            "marginBottom": "12px",

                            "color": "#173C73",

                            "fontWeight": "600"

                        }

                    ),

                    html.Div(

                        id="selector-semanas",

                        className="selector-semanas"

                    )

                ]

            )

        ],

        className="card-premium"

    )