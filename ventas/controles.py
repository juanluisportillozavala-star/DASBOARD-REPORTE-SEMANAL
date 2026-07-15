"""
=========================================================
CONTROLES DEL DASHBOARD
=========================================================
"""

from dash import html


def crear_controles():

    return html.Div(

        [

            # ==========================================
            # MESES
            # ==========================================

            html.H5(

                "Mes",

                className="mb-3"

            ),

            html.Div(

                [

                    html.Div(

                        str(i),

                        id={

                            "type":"btn-mes",

                            "index":i

                        },

                        n_clicks=0,

                        className="cuadro-mes"

                    )

                    for i in range(1,13)

                ],

                className="selector-meses"

            ),
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