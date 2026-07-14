"""
=========================================================
ANÁLISIS DEL MÓDULO DE VENTAS
=========================================================
Todas las métricas y KPIs del Dashboard.
"""

import pandas as pd


# =========================================================
# KPI PRINCIPALES
# =========================================================

def obtener_kpis(df):

    venta_total = df["Crédito"].sum()

    utilidad = df["Ut Bruta MN"].sum()

    margen = 0

    if venta_total != 0:

        margen = utilidad / venta_total * 100

    clientes = df["Asociado"].nunique()

    productos = df["Producto 2"].nunique()

    facturas = len(df)

    return {

        "venta_total": venta_total,

        "utilidad": utilidad,

        "margen": margen,

        "clientes": clientes,

        "productos": productos,

        "facturas": facturas

    }


# =========================================================
# VENTA POR CLIENTE
# =========================================================

def ventas_por_cliente(df):

    return (

        df

        .groupby("Asociado", as_index=False)

        .agg(

            {

                "Crédito":"sum",

                "Ut Bruta MN":"sum"

            }

        )

        .sort_values(

            "Crédito",

            ascending=False

        )

    )


# =========================================================
# VENTA POR PRODUCTO
# =========================================================

def ventas_por_producto(df):

    return (

        df

        .groupby("Producto 2", as_index=False)

        .agg(

            {

                "Crédito":"sum",

                "Ut Bruta MN":"sum"

            }

        )

        .sort_values(

            "Crédito",

            ascending=False

        )

    )


# =========================================================
# VENTAS POR MES
# =========================================================

def ventas_por_mes(df):

    return (

        df

        .groupby("Mes", as_index=False)

        .agg(

            {

                "Crédito":"sum"

            }

        )

    )


# =========================================================
# VENTAS POR SEMANA
# =========================================================

def ventas_por_semana(df):

    return (

        df

        .groupby("Semana", as_index=False)

        .agg(

            {

                "Crédito":"sum"

            }

        )

    )


# =========================================================
# TOP 10 CLIENTES
# =========================================================

def top_clientes(df):

    return ventas_por_cliente(df).head(10)


# =========================================================
# TOP 10 PRODUCTOS
# =========================================================

def top_productos(df):

    return ventas_por_producto(df).head(10)