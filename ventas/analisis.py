"""
=========================================================
ANÁLISIS DEL DASHBOARD DE VENTAS
=========================================================

Todas las funciones de este módulo reciben un DataFrame
ya filtrado por Mes y Semana.

Regresan DataFrames listos para mostrarse en las tablas.
"""

import pandas as pd


# =========================================================
# COLUMNAS DEL REPORTE
# =========================================================
#
# NOTA (fix): "Usuario/Vendedor" no existe en ningún punto
# de procesamiento.py — la columna real del vendedor, tal
# como la deja procesar_bd_ventas(), es la cruda de Odoo:
# "Líneas de la orden de venta/Vendedor". Si se dejaba
# "Usuario/Vendedor", top_vendedores() tronaba con KeyError.

COL_VENDEDOR = "Líneas de la orden de venta/Vendedor"

COL_CLIENTE = "Asiento contable/Nombre del partner para mostrar en la factura."

COL_PRODUCTO = "Producto 2"

COL_CANTIDAD = "Líneas de la orden de venta/Cantidad facturada"

COL_VENTA = "Crédito"

COL_UTILIDAD = "Ut Bruta MN"


# =========================================================
# FORMATO GENERAL DE TABLAS
# =========================================================

def preparar_tabla(df):

    df = df.copy()

    df["Margen %"] = 0

    mascara = df["Venta"] != 0

    df.loc[mascara, "Margen %"] = (

        df.loc[mascara, "Utilidad Bruta"]

        /

        df.loc[mascara, "Venta"]

        * 100

    )

    df["Utilidad Unitaria"] = 0

    mascara = df["Cantidad"] != 0

    df.loc[mascara, "Utilidad Unitaria"] = (

        df.loc[mascara, "Utilidad Bruta"]

        /

        df.loc[mascara, "Cantidad"]

    )

    df = df.round(

        {

            "Cantidad":2,

            "Venta":2,

            "Utilidad Bruta":2,

            "Utilidad Unitaria":2,

            "Margen %":2

        }

    )

    return df


# =========================================================
# TOP VENDEDORES
# =========================================================

def top_vendedores(df):

    tabla = (

        df

        .groupby(

            COL_VENDEDOR,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Vendedor",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# TOP CLIENTES
# =========================================================

def top_clientes(df):

    tabla = (

        df

        .groupby(

            COL_CLIENTE,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Cliente",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# TOP PRODUCTOS
# =========================================================

def top_productos(df):

    tabla = (

        df

        .groupby(

            COL_PRODUCTO,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Producto",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# TOP FAMILIAS
# (Preparado para cuando exista la columna)
# =========================================================

def top_familias(df):

    columna = "Familia"

    if columna not in df.columns:

        return pd.DataFrame(

            columns=[

                "Familia",

                "Cantidad",

                "Venta",

                "Utilidad Bruta",

                "Utilidad Unitaria",

                "Margen %"

            ]

        )

    tabla = (

        df

        .groupby(

            columna,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Familia",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# DASHBOARD COMPLETO (tarjetas planas)
# =========================================================

def obtener_tablas_dashboard(df):

    return {

        "vendedores":top_vendedores(df),

        "productos":top_productos(df),

        "clientes":top_clientes(df),

        "familias":top_familias(df)

    }


# =========================================================
# ÁRBOL DE VENTAS: Vendedor > Cliente > Producto
#
# Para la tabla dinámica estilo Excel en AG Grid COMMUNITY
# (aggrid.py). Como rowGroup/treeData son funciones
# Enterprise, la jerarquía se arma manualmente aquí: cada
# fila del DataFrame de salida ES una fila del grid (de
# Vendedor, de Cliente o de Producto), ya con su subtotal
# calculado, su nivel, y su relación padre-hijo por id.
#
# Se asume que "df" ya llega con las columnas limpias:
# Vendedor, Cliente, Producto, Cantidad, Venta, Utilidad Bruta
# =========================================================

COLUMNAS_ARBOL = [

    "id",
    "parentId",
    "nivel",
    "concepto",
    "Cantidad",
    "Venta",
    "Utilidad Bruta",
    "Margen %",
    "Utilidad Unitaria",
    "tieneHijos",
    "expandido"

]


def _calcular_metricas(cantidad, venta, utilidad):

    """
    Margen % y Utilidad Unitaria NO se pueden sumar entre
    niveles (no son aditivos): se recalculan en cada nivel
    a partir de sus propios totales agregados.
    """

    margen = 0.0

    if venta != 0:

        margen = (utilidad / venta) * 100

    utilidad_unitaria = 0.0

    if cantidad != 0:

        utilidad_unitaria = utilidad / cantidad

    return margen, utilidad_unitaria


def arbol_ventas(df):

    """
    Recibe el DataFrame CRUDO de ventas (el mismo que usan
    top_vendedores/top_clientes/top_productos, con las
    columnas de Odoo: COL_VENDEDOR, COL_CLIENTE, COL_PRODUCTO,
    COL_CANTIDAD, COL_VENTA, COL_UTILIDAD). NO hace falta
    renombrarlo antes de llamar esta función; el renombrado
    a Vendedor/Cliente/Producto/Cantidad/Venta/Utilidad Bruta
    se hace aquí adentro.

    Regresa un DataFrame PLANO, ordenado en profundidad
    (Vendedor -> sus Clientes -> los Productos de cada
    Cliente), listo para pintarse tal cual en un AG Grid
    Community. Cada fila trae:

        id            str   identificador único de la fila
        parentId      str   id de la fila padre ("" en Vendedor)
        nivel         int   1=Vendedor, 2=Cliente, 3=Producto
        concepto      str   texto a mostrar, ya indentado
        Cantidad      float subtotal del nivel
        Venta         float subtotal del nivel
        Utilidad Bruta float subtotal del nivel
        Margen %      float recalculado en este nivel
        Utilidad Unitaria float recalculado en este nivel
        tieneHijos    bool  si se puede expandir
        expandido     bool  estado inicial (siempre False)

    Esta función SOLO arma la estructura completa; expandir/
    contraer (qué filas se muestran) lo resuelve el callback
    que ya tienes. Si te sirve, más abajo hay dos funciones
    de apoyo opcionales: total_general_arbol() y
    filas_visibles().
    """

    if df is None or len(df) == 0:

        return pd.DataFrame(columns=COLUMNAS_ARBOL)

    df = df.copy()

    # -----------------------------------------------
    # Renombrar de columnas crudas (Odoo) a nombres
    # amigables. Mismas constantes que usa el resto
    # del archivo (top_vendedores, top_clientes, etc.)
    # -----------------------------------------------

    mapa_columnas = {

        COL_VENDEDOR: "Vendedor",

        COL_CLIENTE: "Cliente",

        COL_PRODUCTO: "Producto",

        COL_CANTIDAD: "Cantidad",

        COL_VENTA: "Venta",

        COL_UTILIDAD: "Utilidad Bruta"

    }

    faltantes = [

        columna for columna in mapa_columnas

        if columna not in df.columns

    ]

    if faltantes:

        raise KeyError(

            "arbol_ventas: al DataFrame le faltan estas columnas: "

            + ", ".join(faltantes)

        )

    df = df.rename(columns=mapa_columnas)

    df = df[

        [

            "Vendedor",

            "Cliente",

            "Producto",

            "Cantidad",

            "Venta",

            "Utilidad Bruta"

        ]

    ]

    df["Vendedor"] = df["Vendedor"].fillna("Sin vendedor")

    df["Cliente"] = df["Cliente"].fillna("Sin cliente")

    df["Producto"] = df["Producto"].fillna("Sin producto")

    # -----------------------------------------------
    # Subtotales por nivel (de más fino a más grueso)
    # -----------------------------------------------

    productos = (

        df

        .groupby(

            ["Vendedor", "Cliente", "Producto"],

            as_index=False

        )

        .agg(

            {

                "Cantidad": "sum",

                "Venta": "sum",

                "Utilidad Bruta": "sum"

            }

        )

    )

    columnas_numericas = ["Cantidad", "Venta", "Utilidad Bruta"]

    productos[columnas_numericas] = productos[columnas_numericas].astype(float)

    clientes = (

        productos

        .groupby(

            ["Vendedor", "Cliente"],

            as_index=False

        )

        .agg(

            {

                "Cantidad": "sum",

                "Venta": "sum",

                "Utilidad Bruta": "sum"

            }

        )

    )

    vendedores = (

        clientes

        .groupby(

            "Vendedor",

            as_index=False

        )

        .agg(

            {

                "Cantidad": "sum",

                "Venta": "sum",

                "Utilidad Bruta": "sum"

            }

        )

        .sort_values(

            "Venta",

            ascending=False

        )

    )

    # -----------------------------------------------
    # Armar filas planas, en profundidad
    # -----------------------------------------------

    filas = []

    for _, fila_v in vendedores.iterrows():

        vendedor = fila_v["Vendedor"]

        id_vendedor = f"v::{vendedor}"

        margen_v, ut_unit_v = _calcular_metricas(

            fila_v["Cantidad"],

            fila_v["Venta"],

            fila_v["Utilidad Bruta"]

        )

        filas.append(

            {

                "id": id_vendedor,

                "parentId": "",

                "nivel": 1,

                "concepto": str(vendedor),

                "Cantidad": fila_v["Cantidad"],

                "Venta": fila_v["Venta"],

                "Utilidad Bruta": fila_v["Utilidad Bruta"],

                "Margen %": margen_v,

                "Utilidad Unitaria": ut_unit_v,

                "tieneHijos": True,

                "expandido": False

            }

        )

        clientes_del_vendedor = (

            clientes[clientes["Vendedor"] == vendedor]

            .sort_values(

                "Venta",

                ascending=False

            )

        )

        for _, fila_c in clientes_del_vendedor.iterrows():

            cliente = fila_c["Cliente"]

            id_cliente = f"{id_vendedor}||c::{cliente}"

            margen_c, ut_unit_c = _calcular_metricas(

                fila_c["Cantidad"],

                fila_c["Venta"],

                fila_c["Utilidad Bruta"]

            )

            filas.append(

                {

                    "id": id_cliente,

                    "parentId": id_vendedor,

                    "nivel": 2,

                    "concepto": "    " + str(cliente),

                    "Cantidad": fila_c["Cantidad"],

                    "Venta": fila_c["Venta"],

                    "Utilidad Bruta": fila_c["Utilidad Bruta"],

                    "Margen %": margen_c,

                    "Utilidad Unitaria": ut_unit_c,

                    "tieneHijos": True,

                    "expandido": False

                }

            )

            productos_del_cliente = (

                productos[

                    (productos["Vendedor"] == vendedor)

                    &

                    (productos["Cliente"] == cliente)

                ]

                .sort_values(

                    "Venta",

                    ascending=False

                )

            )

            for _, fila_p in productos_del_cliente.iterrows():

                producto = fila_p["Producto"]

                id_producto = f"{id_cliente}||p::{producto}"

                margen_p, ut_unit_p = _calcular_metricas(

                    fila_p["Cantidad"],

                    fila_p["Venta"],

                    fila_p["Utilidad Bruta"]

                )

                filas.append(

                    {

                        "id": id_producto,

                        "parentId": id_cliente,

                        "nivel": 3,

                        "concepto": "        " + str(producto),

                        "Cantidad": fila_p["Cantidad"],

                        "Venta": fila_p["Venta"],

                        "Utilidad Bruta": fila_p["Utilidad Bruta"],

                        "Margen %": margen_p,

                        "Utilidad Unitaria": ut_unit_p,

                        "tieneHijos": False,

                        "expandido": False

                    }

                )

    return pd.DataFrame(filas, columns=COLUMNAS_ARBOL)


# =========================================================
# TOTAL GENERAL (opcional)
#
# Para usarse como pinnedBottomRowData en AG Grid: los
# renglones "fijos" (pinned) SÍ son una función de AG Grid
# Community, no requieren Enterprise.
# =========================================================

def total_general_arbol(df):

    """
    Recibe el mismo DataFrame CRUDO que arbol_ventas() (con
    las columnas COL_VENTA / COL_UTILIDAD / COL_CANTIDAD de
    Odoo), no uno ya renombrado.
    """

    if df is None or len(df) == 0:

        cantidad = venta = utilidad = 0.0

    else:

        cantidad = float(df[COL_CANTIDAD].sum())

        venta = float(df[COL_VENTA].sum())

        utilidad = float(df[COL_UTILIDAD].sum())

    margen, ut_unit = _calcular_metricas(cantidad, venta, utilidad)

    return {

        "id": "total",

        "parentId": "",

        "nivel": 0,

        "concepto": "TOTAL GENERAL",

        "Cantidad": cantidad,

        "Venta": venta,

        "Utilidad Bruta": utilidad,

        "Margen %": margen,

        "Utilidad Unitaria": ut_unit,

        "tieneHijos": False,

        "expandido": False

    }


# =========================================================
# FILAS VISIBLES SEGÚN EXPANSIÓN (opcional)
#
# Ayudante por si tu callback de expandir/contraer quiere
# resolverlo así: recibe el árbol completo de arbol_ventas()
# y el conjunto de ids actualmente expandidos, y regresa
# solo las filas que deben pintarse en el grid. Si tu
# callback ya lo resuelve distinto, esta función se ignora
# sin problema: arbol_ventas() no depende de ella.
# =========================================================

def filas_visibles(df_arbol, ids_expandidos):

    if df_arbol is None or len(df_arbol) == 0:

        return df_arbol

    ids_expandidos = set(ids_expandidos or [])

    padres = dict(

        zip(

            df_arbol["id"],

            df_arbol["parentId"]

        )

    )

    def es_visible(fila_id, nivel):

        if nivel == 1:

            return True

        padre = padres.get(fila_id, "")

        if padre == "" or padre not in ids_expandidos:

            return False

        return es_visible(padre, nivel - 1)

    mascara = df_arbol.apply(

        lambda fila: es_visible(

            fila["id"],

            fila["nivel"]

        ),

        axis=1

    )

    return df_arbol[mascara].reset_index(drop=True)