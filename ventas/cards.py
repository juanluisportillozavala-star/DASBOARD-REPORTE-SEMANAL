"""
=========================================================
TARJETAS KPI
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_card(icono, titulo, valor, color):

    return dbc.Card(

        dbc.CardBody(

            [

                html.Div(

                    [

                        html.Div(

                            html.I(

                                className=icono,

                                style={

                                    "fontSize": "34px",

                                    "color": color

                                }

                            ),

                            style={

                                "width": "60px",

                                "display": "flex",

                                "alignItems": "center",

                                "justifyContent": "center"

                            }

                        ),

                        html.Div(

                            [

                                html.Div(

                                    titulo,

                                    style={

                                        "fontSize": "15px",

                                        "color": "#6C757D",

                                        "fontWeight": "600"

                                    }

                                ),

                                html.Div(

                                    valor,

                                    style={

                                        "fontSize": "32px",

                                        "fontWeight": "bold",

                                        "color": "#173C73",

                                        "marginTop": "5px"

                                    }

                                )

                            ],

                            style={

                                "flex": "1"

                            }

                        )

                    ],

                    style={

                        "display": "flex",

                        "alignItems": "center"

                    }

                )

            ]

        ),

        className="card-premium",

        style={

            "borderLeft": f"6px solid {color}"

        }

    )


def crear_cards(kpis):

    return dbc.Row(

        [

            dbc.Col(

                crear_card(

                    "fas fa-dollar-sign",

                    "Venta Total",

                    kpis["venta_total"],

                    "#28A745"

                ),

                md=4

            ),

            dbc.Col(

                crear_card(

                    "fas fa-chart-line",

                    "Utilidad Bruta",

                    kpis["utilidad_bruta"],

                    "#0D6EFD"

                ),

                md=4

            ),

            dbc.Col(

                crear_card(

                    "fas fa-percent",

                    "Margen Bruto",

                    kpis["margen"],

                    "#F39C12"

                ),

                md=4

            )

        ],

        className="g-4"

    )