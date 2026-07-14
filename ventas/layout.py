"""
=========================================================
MÓDULO VENTAS
=========================================================
Layout del módulo de Ventas
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def crear_layout_ventas():

    return dbc.Container(

        fluid=True,

        children=[

            # ======================================================
            # TITULO
            # ======================================================

            dbc.Row(

                dbc.Col(

                    [

                        html.H2(

                            "📈 Ventas",

                            className="titulo"

                        ),

                        html.P(

                            "Análisis comercial y seguimiento de ventas.",

                            className="subtitulo"

                        )

                    ]

                )

            ),

            html.Br(),

            # ======================================================
            # CARGA DE ARCHIVOS
            # ======================================================

            dbc.Row(

                [

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H5("Catálogo"),

                                    html.Br(),

                                    dcc.Upload(

                                        id="upload-catalogo",

                                        children=html.Div(

                                            [

                                                "📂 Arrastra o selecciona el archivo"

                                            ]

                                        ),

                                        className="upload-box",

                                        multiple=False

                                    )

                                ]

                            )

                        ),

                        md=6

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H5("Base de Datos"),

                                    html.Br(),

                                    dcc.Upload(

                                        id="upload-bd",

                                        children=html.Div(

                                            [

                                                "📂 Arrastra o selecciona el archivo"

                                            ]

                                        ),

                                        className="upload-box",

                                        multiple=False

                                    )

                                ]

                            )

                        ),

                        md=6

                    )

                ]

            ),

            html.Br(),

            # ======================================================
            # KPI
            # ======================================================

            dbc.Row(

                [

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Ventas"),

                                    html.H2("$0")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Utilidad"),

                                    html.H2("$0")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Margen"),

                                    html.H2("0%")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    ),

                    dbc.Col(

                        dbc.Card(

                            dbc.CardBody(

                                [

                                    html.H6("Clientes"),

                                    html.H2("0")

                                ]

                            ),

                            className="kpi"

                        ),

                        md=3

                    )

                ]

            ),

            html.Br(),

            # ======================================================
            # GRAFICA
            # ======================================================

            dbc.Card(

                dbc.CardBody(

                    [

                        html.H4("Gráfica de Ventas"),

                        html.Hr(),

                        dcc.Graph(

                            id="grafica-ventas"

                        )

                    ]

                )

            ),

            html.Br(),

            # ======================================================
            # TABLA
            # ======================================================

            dbc.Card(

                dbc.CardBody(

                    [

                        html.H4("Detalle de Ventas"),

                        html.Hr(),

                        html.Div(

                            id="tabla-ventas"

                        )

                    ]

                )

            )

        ]

    )