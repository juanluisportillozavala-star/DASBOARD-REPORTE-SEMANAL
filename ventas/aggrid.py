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
        #
        # Sin cellRenderer: la indentación y el ícono ▶/▼ ya
        # vienen horneados en el propio texto desde Python
        # (analisis.filas_visibles), no se calculan aquí. Así,
        # cuando cambia "expandido", el VALOR de la celda
        # cambia de verdad, y una actualización ligera de
        # "rowData" (sin reconstruir todo el grid) sí lo
        # redibuja bien.
        # ---------------------------------------------

        {

            "field": "concepto",

            "headerName": "Vendedor / Cliente / Producto",

            "minWidth": 300,

            "pinned": "left",

            "filter": False,

            "sortable": False,

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

    """
    NOTA: antes las filas de producto (nivel 3) alternaban
    color según "params.node.rowIndex % 2" (cebreado tipo
    Excel). Se quitó a propósito: rowIndex es la posición
    VISUAL de la fila, y esa posición se recorre para TODAS
    las filas de abajo cada vez que se expande o contrae
    cualquier cosa arriba — con muchas filas, eso significa
    que potencialmente cientos de filas cambian de color de
    golpe en cada clic, lo cual se ve como parpadeo/"temblor".
    Ahora el color de producto es fijo, no depende de la
    posición, así que un clic ya no le cambia el color a
    filas que ni siquiera se movieron.
    """

    return {

        "function": (

            "params.data.nivel === 0 ? "

            "{fontWeight: 'bold', backgroundColor: '#173C73', color: '#FFFFFF'} : "

            "params.data.nivel === 1 ? "

            "{fontWeight: 'bold', backgroundColor: '#FFFFFF', color: '#173C73', "

            "borderLeft: '5px solid #D4AF37'} : "

            "params.data.nivel === 2 ? "

            "{fontWeight: '600', backgroundColor: '#FBF3DC', color: '#173C73'} : "

            "{backgroundColor: '#FFFFFF', color: '#3A3F44'}"

        )

    }


# =========================================================
# ALTURA DINÁMICA DEL GRID (reemplaza domLayout=autoHeight)
#
# Antes usaba domLayout="autoHeight": el grid crecía según su
# contenido, SIN scroll interno propio. Eso resolvía el hueco
# entre la última fila y el TOTAL GENERAL cuando hay pocas
# filas, pero tenía un costo: sin scroll interno, el
# encabezado se iba de la pantalla al hacer scroll de la
# página, en vez de quedarse fijo arriba de la tabla.
#
# Ahora: la altura crece con el contenido (pocas filas = grid
# chico, total pegado abajo). ALTO_MAXIMO es deliberadamente
# GRANDE (~70 filas): en el uso normal se ve todo de un jalón,
# sin scroll interno — el scroll + encabezado fijo son un
# respaldo solo para el caso extremo de cientos de filas
# visibles a la vez.
#
# Pública (no "_función") porque el callback de expandir en
# callbacks.py también la necesita, para actualizar la altura
# del grid ligeramente (sin reconstruir todo el componente)
# cada vez que cambia cuántas filas están visibles.
# =========================================================

ALTO_FILA = 34

ALTO_ENCABEZADO = 38

ALTO_MAXIMO = 2400

UMBRAL_SCROLL = 40


def calcular_altura_grid(cantidad_filas, hay_total=True):

    """
    NOTA sobre el "+ margen": antes era solo "+ 4", un número
    calculado a ojo. El problema real: cada fila tiene su
    propia línea divisoria (borde de ~1px) y la fila fija
    (TOTAL GENERAL) tiene su propio separador — si el cálculo
    se queda CORTO por aunque sea 1-2px, AG Grid activa su
    scroll interno justo en el límite, y ese scroll aparece y
    desaparece solo en cada recálculo de layout: eso es lo que
    se ve como "temblor", siempre pegado a la esquina inferior
    derecha (donde vive la barra de scroll). Mejor sobrar unos
    pixeles de margen que faltar uno solo.

    Esta función SOLO se usa cuando hay MUCHAS filas (arriba
    de UMBRAL_SCROLL) — con pocas filas se usa domLayout=
    "autoHeight" en vez de esto (ver configuracion_tamano),
    que no necesita adivinar nada porque AG Grid mide su
    propio contenido exacto.
    """

    margen = (cantidad_filas * 1) + 24

    alto_contenido = (

        ALTO_ENCABEZADO

        + (cantidad_filas * ALTO_FILA)

        + (ALTO_FILA if hay_total else 0)

        + margen

    )

    return min(alto_contenido, ALTO_MAXIMO)


def configuracion_tamano(cantidad_filas, hay_total=True):

    """
    Decide CÓMO debe medirse el grid, según cuántas filas hay:

    - Pocas filas (la gran mayoría de los casos): domLayout=
      "autoHeight". AG Grid mide su PROPIO contenido exacto,
      sin que nosotros adivinemos nada en pixeles — cero
      riesgo de quedarnos cortos por 1-2px y disparar el
      scroll fantasma que causaba el "temblor".

    - Muchas filas (arriba de UMBRAL_SCROLL): ya no es
      práctico mostrar todo sin scroll, así que se usa una
      altura acotada con scroll interno propio (con margen de
      sobra, ver calcular_altura_grid) — el encabezado queda
      fijo mientras se hace scroll, como pediste.

    Regresa (dashGridOptions_extra, altura_para_style).
    """

    if cantidad_filas <= UMBRAL_SCROLL:

        return (

            {"domLayout": "autoHeight"},

            "auto"

        )

    alto = calcular_altura_grid(cantidad_filas, hay_total=hay_total)

    return (

        {},

        f"{alto}px"

    )


# =========================================================
# AG GRID (100% COMMUNITY)
# =========================================================

def opciones_grid(pinned, opciones_extra):

    """
    Arma el diccionario COMPLETO de dashGridOptions. Pública
    por la misma razón que estilo_grid(): "dashGridOptions"
    reemplaza todo el diccionario de golpe, así que el
    callback de expandir en callbacks.py también necesita
    esta función para no perder animateRows/rowHeight/etc.
    al actualizarlo ligeramente.
    """

    return {

        "animateRows": False,

        "rowHeight": ALTO_FILA,

        "headerHeight": ALTO_ENCABEZADO,

        "pinnedBottomRowData": pinned,

        **opciones_extra

    }


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

    opciones_extra, alto_estilo = configuracion_tamano(

        len(df),

        hay_total=bool(pinned)

    )

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
        # "domLayout" se agrega condicionalmente (ver
        # configuracion_tamano): con pocas filas se usa
        # "autoHeight" para que AG Grid mida su propio
        # contenido exacto; con muchas, se omite y se usa la
        # altura acotada + scroll interno de estilo_grid.
        # -----------------------------------------------------

        dashGridOptions=opciones_grid(pinned, opciones_extra),

        className="ag-theme-alpine",

        style=estilo_grid(alto_estilo)

    )


# =========================================================
# ESTILO COMPLETO DEL GRID (colores + altura)
#
# Pública porque el callback de expandir en callbacks.py
# también la necesita: al actualizar SOLO "rowData" y
# "style" (sin reconstruir el componente), hay que mandar
# el diccionario de estilo COMPLETO, no nada más la altura
# — "style" reemplaza todo el diccionario de golpe, así que
# si solo se manda {"height": ...} se pierden los colores.
# =========================================================

def estilo_grid(alto):

    """
    alto: string listo para usarse tal cual como CSS height,
    p.ej. "auto" (domLayout=autoHeight) o "640px" (altura
    acotada con scroll). Viene de configuracion_tamano().
    """

    return {

        "width": "100%",

        "height": alto,

        "transition": "height 0.15s ease-out",

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