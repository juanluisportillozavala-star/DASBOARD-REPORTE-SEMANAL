"""
=========================================================
TABLAS
=========================================================
"""

from dash import dash_table


def crear_tabla():

    return dash_table.DataTable(

        id="tabla-ventas",

        page_size=15,

        style_table={

            "overflowX":"auto"

        },

        style_header={

            "backgroundColor":"#0B2D5B",

            "color":"white",

            "fontWeight":"bold"

        },

        style_cell={

            "textAlign":"center",

            "padding":"8px"

        }

    )