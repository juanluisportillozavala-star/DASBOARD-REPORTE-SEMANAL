"""
=========================================================
KPIs DEL DASHBOARD DE VENTAS
=========================================================
"""


# =========================================================
# FORMATO MONEDA
# =========================================================

def formato_moneda(valor):

    return f"${valor:,.2f}"


# =========================================================
# FORMATO PORCENTAJE
# =========================================================

def formato_porcentaje(valor):

    return f"{valor:.2f}%"


# =========================================================
# KPIs PRINCIPALES
# =========================================================

def calcular_kpis(df):

    if df is None or df.empty:

        return {

            "venta_total": "$0.00",

            "utilidad_bruta": "$0.00",

            "margen": "0.00%"

        }

    venta_total = df["Crédito"].sum()

    utilidad_bruta = df["Ut Bruta MN"].sum()

    margen = 0

    if venta_total != 0:

        margen = utilidad_bruta / venta_total * 100

    return {

        "venta_total": formato_moneda(venta_total),

        "utilidad_bruta": formato_moneda(utilidad_bruta),

        "margen": formato_porcentaje(margen)

    }