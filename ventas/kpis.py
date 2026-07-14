"""
=========================================================
KPIs DEL DASHBOARD DE VENTAS
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def tarjeta(titulo, valor, icono, color):

    return dbc.Card(

        dbc.CardBody(

            [

                html.Div(

                    [

                        html.Div(

                            [

                                html.I(

                                    className=f"{icono} fa-2x",

                                    style={

                                        "color": color

                                    }

                                )

                            ],

                            style={

                                "width":"60px",

                                "textAlign":"center"

                            }

                        ),

                        html.Div(

                            [

                                html.Div(

                                    titulo,

                                    style={

                                        "fontSize":"15px",

                                        "color":"gray"

                                    }

                                ),

                                html.H3(

                                    valor,

                                    style={

                                        "margin":"0px",

                                        "fontWeight":"bold",

                                        "color":"#173C73"

                                    }

                                )

                            ],

                            style={

                                "marginLeft":"15px"

                            }

                        )

                    ],

                    style={

                        "display":"flex",

                        "alignItems":"center"

                    }

                )

            ]

        ),

        className="card-premium"

    )


def crear_kpis(kpis):

    return dbc.Row(

        [

            dbc.Col(

                tarjeta(

                    "Venta Total",

                    f"${kpis['venta_total']:,.2f}",

                    "fas fa-dollar-sign",

                    "#28a745"

                ),

                lg=4,

                xl=2

            ),

            dbc.Col(

                tarjeta(

                    "Utilidad",

                    f"${kpis['utilidad']:,.2f}",

                    "fas fa-chart-line",

                    "#0d6efd"

                ),

                lg=4,

                xl=2

            ),

            dbc.Col(

                tarjeta(

                    "Margen",

                    f"{kpis['margen']:.2f}%",

                    "fas fa-percent",

                    "#ffc107"

                ),

                lg=4,

                xl=2

            ),

            dbc.Col(

                tarjeta(

                    "Clientes",

                    f"{kpis['clientes']:,}",

                    "fas fa-users",

                    "#6f42c1"

                ),

                lg=4,

                xl=2

            ),

            dbc.Col(

                tarjeta(

                    "Productos",

                    f"{kpis['productos']:,}",

                    "fas fa-box",

                    "#fd7e14"

                ),

                lg=4,

                xl=2

            ),

            dbc.Col(

                tarjeta(

                    "Facturas",

                    f"{kpis['facturas']:,}",

                    "fas fa-file-invoice",

                    "#20c997"

                ),

                lg=4,

                xl=2

            )

        ],

        className="g-3"

    )