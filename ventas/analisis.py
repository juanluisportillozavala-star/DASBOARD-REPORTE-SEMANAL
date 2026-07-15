"""
=========================================================
ANÁLISIS DEL MÓDULO DE VENTAS
=========================================================
"""

import pandas as pd


# ==========================================================
# NOMBRES DE COLUMNAS
# ==========================================================

COL_CLIENTE = "Asiento contable/Nombre del partner para mostrar en la factura."
COL_VENTA = "Crédito"
COL_UTILIDAD = "Ut Bruta MN"
COL_PRODUCTO = "Producto 2"
COL_MES = "Mes"
COL_SEMANA = "Semana"


# ==========================================================
# KPI PRINCIPALES
# ==========================================================

def obtener_kpis(df):

    venta_total = df[COL_VENTA].sum()

    utilidad = df[COL_UTILIDAD].sum()

    margen = 0

    if venta_total != 0:

        margen = utilidad / venta_total * 100

    clientes = df[COL_CLIENTE].nunique()

    productos = df[COL_PRODUCTO].nunique()

    facturas = len(df)

    return {

        "venta_total": venta_total,

        "utilidad": utilidad,

        "margen": margen,

        "clientes": clientes,

        "productos": productos,

        "facturas": facturas

    }


# ==========================================================
# VENTA POR CLIENTE
# ==========================================================

def ventas_por_cliente(df):

    return (

        df

        .groupby(COL_CLIENTE, as_index=False)

        .agg(

            {

                COL_VENTA: "sum",

                COL_UTILIDAD: "sum"

            }

        )

        .sort_values(

            COL_VENTA,

            ascending=False

        )

    )


# ==========================================================
# VENTA POR PRODUCTO
# ==========================================================

def ventas_por_producto(df):

    return (

        df

        .groupby(COL_PRODUCTO, as_index=False)

        .agg(

            {

                COL_VENTA: "sum",

                COL_UTILIDAD: "sum"

            }

        )

        .sort_values(

            COL_VENTA,

            ascending=False

        )

    )


# ==========================================================
# VENTA POR MES
# ==========================================================

def ventas_por_mes(df):

    return (

        df

        .groupby(COL_MES, as_index=False)

        .agg(

            {

                COL_VENTA: "sum"

            }

        )

    )


# ==========================================================
# VENTA POR SEMANA
# ==========================================================

def ventas_por_semana(df):

    return (

        df

        .groupby(COL_SEMANA, as_index=False)

        .agg(

            {

                COL_VENTA: "sum"

            }

        )

    )


# ==========================================================
# TOP CLIENTES
# ==========================================================

def top_clientes(df):

    return ventas_por_cliente(df).head(10)


# ==========================================================
# TOP PRODUCTOS
# ==========================================================

def top_productos(df):

    return ventas_por_producto(df).head(10)