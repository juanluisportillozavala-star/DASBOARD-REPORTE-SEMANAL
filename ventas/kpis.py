"""
=========================================================
KPIs DASHBOARD VENTAS
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


# ==========================================================
# TARJETA
# ==========================================================

def crear_tarjeta(titulo, valor, icono, color):

    return dbc.Card(

        dbc.CardBody(

            [

                html.Div(

                    [

                        # Icono
                        html.Div(

                            html.I(

                                className=icono,

                                style={

                                    "fontSize": "32px",

                                    "color": color

                                }

                            ),

                            style={

                                "width": "70px",

                                "display": "flex",

                                "justifyContent": "center",

                                "alignItems": "center"

                            }

                        ),

                        # Texto
                        html.Div(

                            [

                                html.Div(

                                    titulo,

                                    style={

                                        "fontSize": "15px",

                                        "color": "#7A7A7A",

                                        "fontWeight": "600"

                                    }

                                ),

                                html.H2(

                                    valor,

                                    style={

                                        "marginTop": "8px",

                                        "marginBottom": "0px",

                                        "fontWeight": "bold",

                                        "color": "#173C73"

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

            "height": "125px"

        }

    )


# ==========================================================
# CONTENEDOR KPIs
# ==========================================================

def crear_kpis(kpis):

    return dbc.Row(

        [

            dbc.Col(

                crear_tarjeta(

                    "Venta Total",

                    f"${kpis['venta_total']:,.2f}",

                    "fas fa-sack-dollar",

                    "#0B8F44"

                ),

                lg=4

            ),

            dbc.Col(

                crear_tarjeta(

                    "Utilidad Bruta",

                    f"${kpis['utilidad']:,.2f}",

                    "fas fa-chart-line",

                    "#0A66C2"

                ),

                lg=4

            ),

            dbc.Col(

                crear_tarjeta(

                    "Margen Bruto",

                    f"{kpis['margen']:.2f}%",

                    "fas fa-percent",

                    "#D4AF37"

                ),

                lg=4

            )

        ],

        className="g-4"

    )