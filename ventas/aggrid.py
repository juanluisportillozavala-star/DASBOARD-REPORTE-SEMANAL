"""
=========================================================
AG GRID DEL DASHBOARD DE VENTAS
=========================================================

Tabla dinámica estilo Excel (Vendedor > Cliente > Producto)
usando Dash AG Grid COMMUNITY.

No se usa rowGroup, treeData, autoGroupColumnDef, sideBar,
statusBar ni pinnedBottomRowData de nivel superior: todo eso
truena en esta versión del wrapper (35.3.0) porque son
funciones Enterprise o props que no existen como kwarg de
Python en esta versión. Solo se usan los props confirmados
como válidos:

    id, rowData, columnDefs, defaultColDef, dashGridOptions,
    getRowId, getRowStyle, className, style, cellClicked

La jerarquía viene ya armada como filas planas desde
ventas/analisis.py (arbol_ventas). El icono ▶ / ▼ para
expandir/contraer es solo visual (texto dentro de la celda,
vía cellRenderer); el callback que ya tienes es quien debe
escuchar "cellClicked", decidir si esa fila se expande o
se contrae, y volver a llamar crear_aggrid() con las filas
visibles actualizadas (ver ejemplo de uso al final).
"""

import dash_ag_grid as dag


# =========================================================
# DEFINICIÓN DE COLUMNAS
# =========================================================

def _columnas():

    return [

        # ---------------------------------------------
        # CONCEPTO (Vendedor / Cliente / Producto)
        # Indentado + ícono ▶/▼ vía cellRenderer (JS),
        # calculado a partir de "nivel" y "tieneHijos"
        # que ya trae cada fila desde analisis.py.
        # ---------------------------------------------

        {

            "field": "concepto",

            "headerName": "Vendedor / Cliente / Producto",

            "minWidth": 420,

            "filter": "agTextColumnFilter",

            "sortable": True,

            "cellRenderer": {

                "function": "'&nbsp;'.repeat(params.data.nivel * 6) + (params.data.tieneHijos ? (params.data.expandido ? '▼ ' : '▶ ') : (params.data.nivel > 0 ? '&nbsp;&nbsp;&nbsp;' : '')) + params.value"

            }

        },

        # ---------------------------------------------
        # CANTIDAD
        # ---------------------------------------------

        {

            "field": "Cantidad",

            "headerName": "Cantidad",

            "type": "numericColumn",

            "filter": "agNumberColumnFilter",

            "sortable": True,

            "valueFormatter": {

                "function": "d3.format(',.0f')(params.value)"

            }

        },

        # ---------------------------------------------
        # UTILIDAD UNITARIA
        # ---------------------------------------------

        {

            "field": "Utilidad Unitaria",

            "headerName": "Ut. Unit.",

            "type": "numericColumn",

            "filter": "agNumberColumnFilter",

            "sortable": True,

            "valueFormatter": {

                "function": "'$' + d3.format(',.2f')(params.value)"

            }

        },

        # ---------------------------------------------
        # VENTA
        # ---------------------------------------------

        {

            "field": "Venta",

            "headerName": "Venta MN",

            "type": "numericColumn",

            "filter": "agNumberColumnFilter",

            "sortable": True,

            "valueFormatter": {

                "function": "'$' + d3.format(',.2f')(params.value)"

            }

        },

        # ---------------------------------------------
        # UTILIDAD BRUTA
        # ---------------------------------------------

        {

            "field": "Utilidad Bruta",

            "headerName": "Ut Bruta MN",

            "type": "numericColumn",

            "filter": "agNumberColumnFilter",

            "sortable": True,

            "valueFormatter": {

                "function": "'$' + d3.format(',.2f')(params.value)"

            }

        },

        # ---------------------------------------------
        # MARGEN %
        # ---------------------------------------------

        {

            "field": "Margen %",

            "headerName": "Margen%",

            "type": "numericColumn",

            "filter": "agNumberColumnFilter",

            "sortable": True,

            "valueFormatter": {

                "function": "d3.format(',.1f')(params.value) + '%'"

            }

        }

    ]


# =========================================================
# ESTILO POR FILA, SEGÚN NIVEL
# (getRowStyle SÍ es prop válido en esta versión)
# =========================================================

def _estilo_filas():

    return {

        "function": (

            "params.data.nivel === 0 ? "

            "{fontWeight: 'bold', backgroundColor: '#173C73', color: 'white'} : "

            "params.data.nivel === 1 ? "

            "{fontWeight: 'bold', backgroundColor: '#FCE9B5'} : "

            "params.data.nivel === 2 ? "

            "{fontWeight: '600', backgroundColor: '#FBF2D9'} : "

            "{}"

        )

    }


# =========================================================
# AG GRID (100% COMMUNITY)
# =========================================================

def crear_aggrid(df, fila_total=None):

    """
    df: DataFrame con las filas que deben mostrarse AHORA
        (la salida de analisis.arbol_ventas, ya filtrada por
        analisis.filas_visibles según qué esté expandido).

    fila_total: dict opcional (analisis.total_general_arbol)
        para fijarlo al fondo del grid. pinnedBottomRowData
        no es un kwarg de nivel superior en esta versión del
        wrapper, así que va DENTRO de dashGridOptions.

    ---------------------------------------------------------
    Ejemplo de uso en tu callback (que ya existe):

        from ventas.analisis import (
            arbol_ventas, total_general_arbol, filas_visibles
        )
        from ventas.aggrid import crear_aggrid

        arbol = arbol_ventas(df_filtrado)
        total = total_general_arbol(df_filtrado)

        # ids_expandidos: set que vive en un dcc.Store, se
        # actualiza cuando llega un cellClicked sobre la
        # columna "concepto" de una fila con tieneHijos=True

        visibles = filas_visibles(arbol, ids_expandidos)

        return crear_aggrid(visibles, fila_total=total)
    ---------------------------------------------------------
    """

    pinned = [fila_total] if fila_total else None

    return dag.AgGrid(

        id="tabla-ventas",

        rowData=df.to_dict("records"),

        columnDefs=_columnas(),

        # -----------------------------------------------------
        # id único por fila (prop válido, no requiere Enterprise)
        # -----------------------------------------------------

        getRowId={

            "function": "params.data.id"

        },

        # -----------------------------------------------------
        # Color/negrita por nivel (Vendedor, Cliente, Producto)
        # -----------------------------------------------------

        getRowStyle=_estilo_filas(),

        # -----------------------------------------------------
        # CONFIGURACIÓN GENERAL DE COLUMNAS
        # -----------------------------------------------------

        defaultColDef={

            "flex": 1,

            "minWidth": 130,

            "sortable": True,

            "filter": True,

            "resizable": True,

            "floatingFilter": True,

            "editable": False

        },

        # -----------------------------------------------------
        # OPCIONES DEL GRID (solo Community). El total fijo
        # (pinnedBottomRowData) va aquí adentro, no como kwarg
        # de nivel superior.
        # -----------------------------------------------------

        dashGridOptions={

            "pagination": True,

            "paginationPageSize": 25,

            "animateRows": True,

            "rowSelection": {"mode": "singleRow"},

            "pinnedBottomRowData": pinned

        },

        className="ag-theme-alpine",

        style={

            "height": "700px",

            "width": "100%"

        }

    )