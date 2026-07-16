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

    df["Margen %"] = 0.0

    mascara = df["Venta"] != 0

    df.loc[mascara, "Margen %"] = (

        df.loc[mascara, "Utilidad Bruta"]

        /

        df.loc[mascara, "Venta"]

        * 100

    )

    df["Utilidad Unitaria"] = 0.0

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
# DASHBOARD COMPLETO
# =========================================================

def obtener_tablas_dashboard(df):

    return {

        "vendedores":top_vendedores(df),

        "productos":top_productos(df),

        "clientes":top_clientes(df),

        "familias":top_familias(df)

    }