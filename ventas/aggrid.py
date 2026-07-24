"""
=========================================================
AG GRID DEL DASHBOARD DE VENTAS
=========================================================

Tabla dinámica estilo Excel usando Dash AG Grid COMMUNITY.

No se usa rowGroup, treeData, autoGroupColumnDef, sideBar,
statusBar ni pinnedBottomRowData de nivel superior: todo eso
truena en esta versión del wrapper (35.3.0) porque son
funciones Enterprise o props que no existen como kwarg de
Python en esta versión. Solo se usan los props confirmados
como válidos:

    id, rowData, columnDefs, defaultColDef, dashGridOptions,
    getRowId, getRowStyle, className, style, cellClicked

La jerarquía viene ya armada como filas planas desde el
motor (core/arbol.py o ventas/analisis.py). El icono ▶ / ▼
para expandir/contraer es solo visual (texto dentro de la
celda); el callback escucha "cellClicked" y vuelve a llamar
crear_aggrid() con las filas visibles actualizadas.

IMPORTANTE: no hay filtro ni ordenamiento nativo de columnas.
El sort nativo se quitó porque reordena TODAS las filas
visibles juntas, rompiendo la jerarquía. El orden se controla
desde Python con el dropdown "Ordenar por" (ver ventas/tabla_arbol.py).
"""

import dash_ag_grid as dag
from dash import html



# =========================================================
# DEFINICIÓN DE COLUMNAS
#
# titulo_concepto: encabezado de la primera columna, parámetro
# para que cada tabla muestre su propio título.
# =========================================================

def _columnas(titulo_concepto="Vendedor / Cliente / Producto"):

    return [

        {

            "field": "concepto",

            "headerName": titulo_concepto,

            "minWidth": 300,

            "pinned": "left",

            "filter": False,

            "sortable": False,

            "cellStyle": {

                "function": "params.data.tieneHijos ? {cursor: 'pointer'} : {}"

            }

        },

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
# =========================================================

def _estilo_filas():

    """
    Color/negrita por nivel. Fijo por nivel (no por rowIndex)
    para evitar el "temblor" al expandir/contraer.
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
# ALTURA DEL GRID (ADAPTATIVA)
#
# - Pocas filas (<= UMBRAL_SCROLL): domLayout="autoHeight". El
#   grid se ajusta EXACTO a su contenido, sin bloque vacío
#   debajo (caso de la tabla con 3 vendedores sin expandir).
# - Muchas filas (> UMBRAL_SCROLL): altura fija por viewport
#   con scroll interno, así el encabezado de columnas queda
#   pegado arriba al desplazarse.
#
# calcular_altura_grid() se conserva SIN uso por si se quiere
# volver a una altura en px calculada.
# =========================================================

ALTO_FILA = 34

ALTO_ENCABEZADO = 38

ALTO_MAXIMO = 500

UMBRAL_SCROLL = 15

# Altura fija SOLO cuando hay muchas filas (> UMBRAL_SCROLL).
# Ajustable: "60vh" más compacto, "80vh" casi pantalla completa.
ALTO_VIEWPORT = "70vh"


def calcular_altura_grid(cantidad_filas, hay_total=True):

    """
    (EN DESUSO — se conserva por si se quiere altura en px.)
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
    Devuelve (dashGridOptions_extra, altura_para_style).

    Usa SIEMPRE altura en píxeles calculada por calcular_altura_grid:
    - Pocas filas -> altura pequeña, ajustada al contenido (sin
      bloque vacío debajo).
    - Muchas filas -> crece hasta ALTO_MAXIMO y ahí se topa,
      activando scroll interno con el encabezado pegado.

    Por qué NO autoHeight: alternar domLayout entre "autoHeight"
    (pocas filas) y normal (muchas) al expandir/contraer NO lo
    aplica bien AG Grid en vivo — el grid se queda en autoHeight
    y crece sin tope, chocando con lo de abajo. Con una altura en
    px que solo cambia de número, no hay esa transición y el tope
    (ALTO_MAXIMO) siempre se respeta.
    """

    alto = calcular_altura_grid(cantidad_filas, hay_total=hay_total)

    return ({}, f"{alto}px")


# =========================================================
# AG GRID (100% COMMUNITY)
# =========================================================

def opciones_grid(pinned, opciones_extra):

    """
    Arma el diccionario COMPLETO de dashGridOptions. Pública
    porque "dashGridOptions" reemplaza todo el diccionario de
    golpe, así que el callback de expandir también la necesita
    para no perder animateRows/rowHeight/etc.
    """

    return {

        "animateRows": False,

        "rowHeight": ALTO_FILA,

        "headerHeight": ALTO_ENCABEZADO,

        "pinnedBottomRowData": pinned,

        **opciones_extra

    }


def crear_aggrid(df, fila_total=None, id_grid="tabla-ventas",
                 titulo_concepto="Vendedor / Cliente / Producto"):

    """
    df: DataFrame con las filas visibles AHORA.
    fila_total: dict opcional para fijar el TOTAL GENERAL al
        fondo (pinnedBottomRowData, dentro de dashGridOptions).
    id_grid: id del componente (una por tabla).
    titulo_concepto: encabezado de la primera columna.
    """

    pinned = [fila_total] if fila_total else None

    opciones_extra, alto_estilo = configuracion_tamano(

        len(df),

        hay_total=bool(pinned)

    )

    return dag.AgGrid(

        id=id_grid,

        rowData=df.to_dict("records"),

        columnDefs=_columnas(titulo_concepto),

        getRowId={

            "function": "params.data.id"

        },

        getRowStyle=_estilo_filas(),

        defaultColDef={

            "flex": 1,

            "minWidth": 130,

            "sortable": False,

            "filter": False,

            "resizable": True,

            "floatingFilter": False,

            "editable": False

        },

        dashGridOptions=opciones_grid(pinned, opciones_extra),

        className="ag-theme-alpine",

        style=estilo_grid(alto_estilo)

    )


# =========================================================
# ESTILO COMPLETO DEL GRID (colores + altura)
# =========================================================

def estilo_grid(alto):

    """
    alto: string CSS height listo, p.ej. "70vh" o "auto".
    Viene de configuracion_tamano().
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