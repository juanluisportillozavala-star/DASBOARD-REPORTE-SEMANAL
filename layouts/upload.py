"""
=========================================================
UPLOAD
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_upload():

    return dbc.Card(

        dbc.CardBody(

            [

                html.H4(
                    "Carga de Información",
                    className="mb-4"
                ),

                dbc.Row(

                    [

                        dbc.Col(

                            dbc.Card(

                                dbc.CardBody(

                                    [

                                        html.H2("📚"),

                                        html.H5("Catálogo"),

                                        html.P("Seleccionar archivo Excel")

                                    ],

                                    className="text-center"

                                ),

                                className="upload-card"

                            ),

                            md=6

                        ),

                        dbc.Col(

                            dbc.Card(

                                dbc.CardBody(

                                    [

                                        html.H2("📊"),

                                        html.H5("Base de Datos"),

                                        html.P("Seleccionar archivo Excel")

                                    ],

                                    className="text-center"

                                ),

                                className="upload-card"

                            ),

                            md=6

                        )

                    ]

                )

            ]

        ),

        className="shadow-sm"
    )