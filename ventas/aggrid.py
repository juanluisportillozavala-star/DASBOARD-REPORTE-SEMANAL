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
vía cellRenderer); el callback que ya tienes escucha
"cellClicked", decidir si esa fila se expande o se contrae,
y vuelve a llamar crear_aggrid() con las filas visibles
actualizadas.

IMPORTANTE: no hay filtro ni ordenamiento nativo de columnas.
El ordenamiento nativo de AG Grid se quitó a propósito porque
reordena TODAS las filas visibles juntas (vendedor, cliente y
producto mezclados por valor), rompiendo la jerarquía. El
orden ahora se controla desde Python con el selector "Ordenar
por" (ver crear_encabezado_periodo), que reordena cada nivel
por separado (vendedores entre sí, clientes dentro de cada
vendedor, productos dentro de cada cliente) y mantiene la
jerarquía intacta.
"""

import dash_ag_grid as dag
from dash import html, dcc


# =========================================================
# OPCIONES DEL SELECTOR "ORDENAR POR"
# =========================================================

OPCIONES_ORDEN = [

    {"label": "Venta", "value": "Venta"},

    {"label": "Utilidad Bruta", "value": "Utilidad Bruta"},

    {"label": "Cantidad", "value": "Cantidad"},

    {"label": "Margen %", "value": "Margen %"},

    {"label": "Utilidad Unitaria", "value": "Utilidad Unitaria"}

]


def crear_selector_orden():

    """
    Selector "Ordenar por" FIJO (no se regenera nunca, vive
    una sola vez en el layout). Reemplaza el sort nativo de
    columna de AG Grid, que mezclaba vendedor/cliente/producto
    y rompía la jerarquía. Reordena los 3 niveles del árbol
    por la misma métrica, manteniendo la jerarquía intacta.
    """

    return html.Div(

        [

            html.Span(

                "Ordenar por:  ",

                style={

                    "color": "#173C73",

                    "fontWeight": "bold",

                    "marginRight": "8px"

                }

            ),

            dcc.Dropdown(

                id="selector-orden-arbol",

                options=OPCIONES_ORDEN,

                value="Venta",

                clearable=False,

                searchable=False,

                style={

                    "width": "220px"

                }

            )

        ],

        style={

            "display": "flex",

            "alignItems": "center",

            "marginBottom": "12px"

        }

    )


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

            "minWidth": 300,

            "pinned": "left",

            "filter": False,

            "sortable": False,

            "cellRenderer": {

                "function": "'\u00a0'.repeat(params.data.nivel * 6) + (params.data.tieneHijos ? (params.data.expandido ? '▼ ' : '▶ ') : (params.data.nivel > 0 ? '\u00a0\u00a0\u00a0' : '')) + params.value"

            },

            "cellStyle": {

                "function": "params.data.tieneHijos ? {cursor: 'pointer'} : {}"

            }

        },

        # ---------------------------------------------
        # CANTIDAD
        # ---------------------------------------------

        {

            "field": "Cantidad",

            "headerName": "Cantidad",

            "type": "numericColumn",

            "filter": False,

            "sortable": False,

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

            "filter": False,

            "sortable": False,

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

            "filter": False,

            "sortable": False,

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

            "filter": False,

            "sortable": False,

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

            "filter": False,

            "sortable": False,

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

            "{fontWeight: 'bold', backgroundColor: '#173C73', color: '#FFFFFF'} : "

            "params.data.nivel === 1 ? "

            "{fontWeight: 'bold', backgroundColor: '#FFFFFF', color: '#173C73', "

            "borderLeft: '5px solid #D4AF37'} : "

            "params.data.nivel === 2 ? "

            "{fontWeight: '600', backgroundColor: '#FBF3DC', color: '#173C73'} : "

            "(params.node.rowIndex % 2 === 0 ? "

            "{backgroundColor: '#FFFFFF', color: '#3A3F44'} : "

            "{backgroundColor: '#FAFAF5', color: '#3A3F44'})"

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

        arbol = arbol_ventas(df_filtrado, columna_orden=orden)
        total = total_general_arbol(df_filtrado)

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
        #
        # Sin filter ni sortable (ver nota al inicio del
        # archivo): se quitó el ícono de filtro por pedido, y
        # el sort nativo se reemplazó por el selector Python.
        # -----------------------------------------------------

        defaultColDef={

            "flex": 1,

            "minWidth": 130,

            "sortable": False,

            "filter": False,

            "resizable": True,

            "floatingFilter": False,

            "editable": False

        },

        # -----------------------------------------------------
        # OPCIONES DEL GRID (solo Community). El total fijo
        # (pinnedBottomRowData) va aquí adentro, no como kwarg
        # de nivel superior.
        #
        # domLayout="autoHeight": el grid crece según su propio
        # contenido en vez de vivir en un contenedor de altura
        # fija. Así el TOTAL GENERAL queda pegado justo debajo
        # de la última fila, no "flotando" al fondo de un hueco
        # cuando hay pocas filas visibles.
        # -----------------------------------------------------

        dashGridOptions={

            "pagination": True,

            "paginationPageSize": 100,

            "animateRows": True,

            "rowHeight": 34,

            "headerHeight": 38,

            "domLayout": "autoHeight",

            "pinnedBottomRowData": pinned

        },

        className="ag-theme-alpine",

        # -----------------------------------------------------
        # PALETA AZUL / BLANCO / DORADO
        #
        # ag-theme-alpine se personaliza con variables CSS
        # propias de AG Grid (no requieren tocar ningún .css
        # aparte): encabezado azul marino, bordes y hover en
        # tono dorado tenue, cuerpo blanco.
        # -----------------------------------------------------

        style={

            "width": "100%",

            "height": "auto",

            "--ag-font-size": "18px",

            "--ag-header-background-color": "#173C73",

            "--ag-header-foreground-color": "#090000",

            "--ag-background-color": "#FFFFFF",

            "--ag-foreground-color": "#FDFEFF",

            "--ag-border-color": "#E7DBB0",

            "--ag-header-column-separator-color": "#2C5090",

            "--ag-row-hover-color": "#E5DECB",

            "--ag-range-selection-border-color": "#D4AF37",

            "--ag-icon-color": "#050400"

        }

    )


# =========================================================
# ENCABEZADO "FECHA DE CORTE"
#
# Franja azul/dorado/blanco arriba del grid: fecha de corte
# y semanas activas, estilo el recuadro "Fecha corte /
# Semana" del Excel de referencia.
#
# El selector "Ordenar por" NO vive aquí: vive FIJO en el
# layout (no se regenera cada vez que se reconstruye la
# tabla), por la misma razón por la que los botones de mes/
# semana son fijos y no se regeneran en un callback: si un
# dcc.Dropdown se recrea con un "value" ya puesto, Dash lo
# puede interpretar como un cambio real y disparar el
# callback de nuevo innecesariamente (mismo riesgo que el
# reset de n_clicks que ya resolvimos antes).
# =========================================================

def crear_encabezado_periodo(fecha_corte, semanas_texto):

    return html.Div(

        [

            html.Span(

                "Fecha de corte:  ",

                style={

                    "color": "#D4AF37",

                    "fontWeight": "bold",

                    "marginLeft": "24px"

                }

            ),

            html.Span(

                fecha_corte,

                style={

                    "color": "#FFFFFF",

                    "fontWeight": "bold",

                    "marginRight": "32px"

                }

            ),

            html.Span(

                "Semana(s):  ",

                style={

                    "color": "#D4AF37",

                    "fontWeight": "bold"

                }

            ),

            html.Span(

                semanas_texto,

                style={

                    "color": "#FFFFFF",

                    "fontWeight": "bold"

                }

            )

        ],

        style={

            "backgroundColor": "#173C73",

            "padding": "12px 16px",

            "borderRadius": "10px 10px 0 0",

            "display": "flex",

            "justifyContent": "flex-end",

            "flexWrap": "wrap",

            "fontSize": "15px"

        }

    )