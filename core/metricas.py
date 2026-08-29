"""
=========================================================
core/metricas.py
=========================================================
FUENTE ÚNICA de las reglas "margen" y "utilidad unitaria".

Antes esta fórmula estaba implementada CUATRO veces
(analisis.preparar_tabla, analisis._agregar_metricas_df,
analisis._calcular_metricas, kpis.calcular_kpis). Aquí
vive una sola vez, en dos sabores: escalar y vectorizado.

Definición (idéntica a la que el código ya usaba):
  margen %          = utilidad / venta * 100   (0 si venta == 0)
  utilidad unitaria = utilidad / cantidad      (0 si cantidad == 0)

IMPORTANTE (pandas 3.x): la versión vectorizada usa el
mismo patrón .loc[mascara] que el código original ya
usaba y que ya funcionaba en tu entorno.
"""

# =========================================================
# ESCALAR
# =========================================================

def margen(utilidad, venta):
    """Margen bruto en % (0.0 si venta == 0)."""
    if venta == 0:
        return 0.0
    return (utilidad / venta) * 100


def utilidad_unitaria(utilidad, cantidad):
    """Utilidad por unidad (0.0 si cantidad == 0)."""
    if cantidad == 0:
        return 0.0
    return utilidad / cantidad

# =========================================================
# VECTORIZADO (sobre un DataFrame ya agregado)
# =========================================================

def agregar_metricas_df(
    df,
    col_cantidad="Cantidad",
    col_venta="Venta",
    col_utilidad="Utilidad Bruta",
    col_margen="Margen %",
    col_ut_unitaria="Utilidad Unitaria",
):
    """
    Agrega/actualiza Margen % y Utilidad Unitaria sobre un
    DataFrame que ya trae Cantidad, Venta y Utilidad Bruta
    agregadas. Devuelve una copia; no muta la entrada.
    """
    df = df.copy()

    df[col_margen] = 0.0
    mascara = df[col_venta] != 0
    df.loc[mascara, col_margen] = (
        df.loc[mascara, col_utilidad]
        / df.loc[mascara, col_venta]
        * 100
    )

    df[col_ut_unitaria] = 0.0
    mascara = df[col_cantidad] != 0
    df.loc[mascara, col_ut_unitaria] = (
        df.loc[mascara, col_utilidad]
        / df.loc[mascara, col_cantidad]
    )

    return df