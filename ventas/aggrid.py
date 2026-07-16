"""
=========================================================
AG GRID DEL DASHBOARD DE VENTAS
=========================================================
"""

import dash_ag_grid as dag


def crear_aggrid(df):

    columnas = []

    for col in df.columns:

        columnas.append(

            {

                "headerName": col,

                "field": col,

                "sortable": True,

                "filter": True,

                "resizable": True,

            }

        )

    return dag.AgGrid(

        id="aggrid-ventas",

        rowData=df.to_dict("records"),

        columnDefs=columnas,

        defaultColDef={

            "flex": 1,

            "minWidth": 120,

            "floatingFilter": True,

        },

        dashGridOptions={

            "pagination": True,

            "paginationPageSize": 20,

            "animateRows": True,

        },

        style={

            "height": "700px",

            "width": "100%"

        }

    )