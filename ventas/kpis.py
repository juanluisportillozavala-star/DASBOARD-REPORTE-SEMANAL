"""
=========================================================
KPIs DEL DASHBOARD DE VENTAS
=========================================================
Calcula los 4 KPIs principales y su avance vs los OBJETIVOS
anuales. Devuelve tanto el valor formateado (para mostrar)
como el valor crudo y el % de avance (para la barra de
progreso).
"""

from core import columnas as C

# =========================================================
# OBJETIVOS ANUALES (etapa 1: fijos en código)
# A futuro se cargarán por año desde una pantalla de carga.
# =========================================================

OBJETIVOS = {
    "venta": 53_025_000,      # Venta MN anual
    "utilidad": 10_610_000,   # Utilidad bruta anual
    "margen": 20.0,           # Margen % (mantener o aumentar)
    "peso_kilo": 10.0,        # Utilidad por kilo (mantener o aumentar $)
}


# =========================================================
# FORMATOS
# =========================================================

def formato_moneda(valor):
    return f"${valor:,.2f}"


def formato_porcentaje(valor):
    return f"{valor:.2f}%"


def _avance(valor, objetivo):
    """% de avance vs objetivo (0-100, tope 100 para la barra)."""
    if not objetivo:
        return 0.0
    pct = valor / objetivo * 100
    if pct < 0:
        pct = 0.0
    return pct


# =========================================================
# KPIs PRINCIPALES
# =========================================================

def calcular_kpis(df):

    if df is None or df.empty:
        return {
            "venta_total": "$0.00",
            "utilidad_bruta": "$0.00",
            "margen": "0.00%",
            "peso_kilo": "$0.00",
            # avances
            "venta_pct": 0.0,
            "utilidad_pct": 0.0,
            "margen_pct": 0.0,
            "peso_kilo_pct": 0.0,
            # objetivos (texto)
            "venta_obj": formato_moneda(OBJETIVOS["venta"]),
            "utilidad_obj": formato_moneda(OBJETIVOS["utilidad"]),
            "margen_obj": formato_porcentaje(OBJETIVOS["margen"]),
            "peso_kilo_obj": formato_moneda(OBJETIVOS["peso_kilo"]),
        }

    venta_total = df[C.RAW_CREDITO].sum()
    utilidad_bruta = df[C.UT_BRUTA].sum()

    margen = (utilidad_bruta / venta_total * 100) if venta_total else 0

    # pesos por kilo = utilidad unitaria = Ut Bruta / cantidad (kilos)
    cantidad = df[C.RAW_CANTIDAD].sum() if C.RAW_CANTIDAD in df.columns else 0
    peso_kilo = (utilidad_bruta / cantidad) if cantidad else 0

    return {
        # valores formateados
        "venta_total": formato_moneda(venta_total),
        "utilidad_bruta": formato_moneda(utilidad_bruta),
        "margen": formato_porcentaje(margen),
        "peso_kilo": formato_moneda(peso_kilo),
        # % de avance vs objetivo (para la barra)
        "venta_pct": _avance(venta_total, OBJETIVOS["venta"]),
        "utilidad_pct": _avance(utilidad_bruta, OBJETIVOS["utilidad"]),
        "margen_pct": _avance(margen, OBJETIVOS["margen"]),
        "peso_kilo_pct": _avance(peso_kilo, OBJETIVOS["peso_kilo"]),
        # objetivos como texto (para mostrar "meta: X")
        "venta_obj": formato_moneda(OBJETIVOS["venta"]),
        "utilidad_obj": formato_moneda(OBJETIVOS["utilidad"]),
        "margen_obj": formato_porcentaje(OBJETIVOS["margen"]),
        "peso_kilo_obj": formato_moneda(OBJETIVOS["peso_kilo"]),
    }