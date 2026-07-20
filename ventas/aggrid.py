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
from dash import html

from ventas.analisis import comparador_jerarquico


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
        #
        # sortable: True + comparator = comparador
        # jerárquico. NO es el sort plano de AG Grid: el
        # comparator compara la "ruta" [rango_vendedor,
        # rango_cliente, rango_producto] en vez del valor
        # crudo, así que un clic en el encabezado ordena
        # de mayor a menor SIN mezclar niveles.
        # ---------------------------------------------

        {

            "field": "Cantidad",

            "headerName": "Cantidad",

            "type": "numericColumn",

            "filter": False,

            "sortable": True,

            "comparator": {

                "function": comparador_jerarquico("_ruta_Cantidad")

            },

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

            "sortable": True,

            "comparator": {

                "function": comparador_jerarquico("_ruta_Utilidad Unitaria")

            },

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

            "sortable": True,

            "comparator": {

                "function": comparador_jerarquico("_ruta_Venta")

            },

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

            "sortable": True,

            "comparator": {

                "function": comparador_jerarquico("_ruta_Utilidad Bruta")

            },

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

            "sortable": True,

            "comparator": {

                "function": comparador_jerarquico("_ruta_Margen %")

            },

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

    # -----------------------------------------------------
    # ALTURA DINÁMICA CON TOPE (reemplaza domLayout=autoHeight)
    #
    # Antes usaba domLayout="autoHeight": el grid crecía según
    # su contenido, SIN scroll interno propio. Eso resolvía el
    # hueco entre la última fila y el TOTAL GENERAL cuando hay
    # pocas filas, pero tenía un costo: sin scroll interno, el
    # encabezado (Vendedor/Cliente/Producto, Cantidad, etc.) se
    # iba de la pantalla al hacer scroll de la página, en vez
    # de quedarse fijo arriba de la tabla.
    #
    # Ahora: la altura crece con el contenido (pocas filas =
    # grid chico, total pegado abajo) PERO con un tope máximo.
    # Al llegar al tope, el grid usa SU PROPIO scroll interno
    # (comportamiento normal de AG Grid), y ahí el encabezado
    # SÍ se queda fijo mientras se hace scroll de las filas,
    # y el TOTAL GENERAL (pinned) siempre queda visible al
    # fondo sin necesidad de bajar hasta él.
    # -----------------------------------------------------

    ALTO_FILA = 34

    ALTO_ENCABEZADO = 38

    ALTO_MAXIMO = 640

    alto_contenido = (

        ALTO_ENCABEZADO

        + (len(df) * ALTO_FILA)

        + (ALTO_FILA if pinned else 0)

        + 4

    )

    alto_grid = min(alto_contenido, ALTO_MAXIMO)

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
        # Sin domLayout="autoHeight" y sin paginación: con
        # altura acotada (ver alto_grid arriba), AG Grid usa su
        # scroll interno normal, que trae encabezado fijo de
        # fábrica — no hace falta configurar nada extra para
        # eso.
        # -----------------------------------------------------

        dashGridOptions={

            "animateRows": True,

            "rowHeight": ALTO_FILA,

            "headerHeight": ALTO_ENCABEZADO,

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

            "height": f"{alto_grid}px",

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
# Ya no hay selector "Ordenar por": el orden ahora se hace
# con clic nativo en el encabezado de cada columna numérica
# (ver "comparator" en _columnas / comparador_jerarquico en
# analisis.py), que preserva la jerarquía sin necesitar
# ningún componente adicional.
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