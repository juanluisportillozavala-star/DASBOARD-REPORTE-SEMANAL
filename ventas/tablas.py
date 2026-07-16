"""
=========================================================
TABLAS DEL DASHBOARD DE VENTAS
=========================================================
"""

from dash import html
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc


# =========================================================
# TABLA REUTILIZABLE
# =========================================================

def crear_tabla(
    titulo,
    dataframe,
    columnas,
    alto="430px"
):

    return dbc.Card(

        [

            dbc.CardHeader(

                html.H5(

                    titulo,

                    className="mb-0",

                    style={

                        "fontWeight": "bold",

                        "color": "white"

                    }

                ),

                style={

                    "backgroundColor": "#173C73"

                }

            ),

            dbc.CardBody(

                [

                    DataTable(

                        id=f"tabla-{titulo.lower().replace(' ','-')}",

                        columns=[{"name": c, "id": c} for c in columnas],

                        data=dataframe.to_dict("records"),

                        page_action="native",

                        page_size=10,

                        sort_action="native",

                        filter_action="native",

                        fixed_rows={"headers": True},

                        style_table={

                            "maxHeight": alto,

                            "overflowY": "auto",

                            "overflowX": "auto"

                        },

                        style_header={

                            "backgroundColor": "#173C73",

                            "color": "white",

                            "fontWeight": "bold",

                            "fontSize": "14px",

                            "textAlign": "center",

                            "border": "none"

                        },

                        style_cell={

                            "textAlign": "center",

                            "padding": "8px",

                            "fontFamily": "Segoe UI",

                            "fontSize": "13px",

                            "border": "1px solid #E6E9EF",

                            "whiteSpace": "normal",

                            "height": "auto",

                        },

                        style_cell_conditional=[
                            {
                                "if": {"column_id": columnas[0]},
                                "textAlign": "left",
                                "fontWeight": "600"
                            }
                        ] if columnas else [],

                        style_data={"backgroundColor": "white", "color": "#2E3A46"},

                        style_data_conditional=[
                            {"if": {"row_index": "odd"}, "backgroundColor": "#F8FAFC"},
                            {"if": {"state": "selected"}, "backgroundColor": "#DCEBFF", "border": "1px solid #173C73"}
                        ],

                        export_format="csv",

                        export_headers="display",

                        fill_width=True

                    )

                ]

            )

        ],

        className="card-premium"

    )


# =========================================================
# DOS TABLAS POR FILA
# =========================================================

def crear_fila_tablas(

    izquierda,

    derecha

):

    return dbc.Row(

        [

            dbc.Col(

                izquierda,

                md=6

            ),

            dbc.Col(

                derecha,

                md=6

            )

        ],

        className="g-4"

    )


# =========================================================
# CUATRO TABLAS
# =========================================================

def crear_dashboard_tablas(

    tabla1,

    tabla2,

    tabla3,

    tabla4

):

    return html.Div(

        [

            crear_fila_tablas(

                tabla1,

                tabla2

            ),

            html.Br(),

            crear_fila_tablas(

                tabla3,

                tabla4

            )

        ]

    )