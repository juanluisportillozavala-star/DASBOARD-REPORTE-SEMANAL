"""
=========================================================
bsc/fuentes.py  —  PUENTE del BSC hacia los módulos reales
=========================================================
Cuando un indicador del catálogo tiene fuente "auto:XXXX", el
BSC NO usa la captura manual: pide aquí el número real del mes.

Cada función devuelve el ACUMULADO del mes de ese indicador
(las semanas del BSC quedan solo informativas, según lo
acordado). Si no hay datos, devuelve None.

MÓDULOS CONECTADOS:
  • ventas  -> Venta y Utilidad bruta, por vendedor y total.

Se calcula con las MISMAS columnas que el módulo Ventas
(core.columnas / core.arbol.total_general): Venta = "Crédito",
Utilidad = "Ut Bruta MN", filtrando por Año / Mes / Vendedor.
"""

import db

# nombres crudos, igual que el módulo Ventas
_COL_ANIO = "Año"
_COL_MES = "Mes"
_COL_VENDEDOR = "Líneas de la orden de venta/Vendedor"
_COL_VENTA = "Crédito"
_COL_UTILIDAD = "Ut Bruta MN"

# Mapeo nombre BSC -> nombre EXACTO del vendedor en la BD de ventas.
# (En el catálogo del BSC son "Ilse García"; en ventas están en
# mayúsculas. Si en tu BD aparecen distinto, ajústalo AQUÍ.)
_VENDEDOR_BSC_A_VENTAS = {
    "Ilse García": "ILSE GARCÍA",
    "Fredy Salas": "FREDY SALAS",
    "Mateo López": "MATEO LÓPEZ",
}


def _df_ventas_mes(anio, mes):
    """DataFrame de ventas del año/mes (de la caché del servidor)."""
    df = db.obtener_df("ventas")
    if df is None or len(df) == 0:
        return None
    if _COL_ANIO not in df.columns or _COL_MES not in df.columns:
        return None
    m = (df[_COL_ANIO] == int(anio)) & (df[_COL_MES] == int(mes))
    sub = df[m]
    return sub if len(sub) else None


def _suma_columna(anio, mes, vendedor_bsc, columna):
    """Suma 'columna' para el año/mes; si vendedor_bsc no es None,
    filtra por ese vendedor. Devuelve float o None."""
    sub = _df_ventas_mes(anio, mes)
    if sub is None or columna not in sub.columns:
        return None
    if vendedor_bsc is not None:
        nombre = _VENDEDOR_BSC_A_VENTAS.get(vendedor_bsc, vendedor_bsc)
        if _COL_VENDEDOR not in sub.columns:
            return None
        sub = sub[sub[_COL_VENDEDOR].astype(str).str.strip() == nombre]
        if len(sub) == 0:
            return None
    try:
        return float(sub[columna].sum())
    except Exception:
        return None


# =========================================================
# API pública: valor_auto(fuente, indicador, anio, mes)
# =========================================================
# 'indicador' es el dict del catálogo (para saber vendedor, etc.).

def valor_auto(fuente, indicador, anio, mes):
    """Devuelve el acumulado real del mes para un indicador auto,
    o None si no se puede calcular. 'fuente' es el string del
    catálogo, p.ej. 'auto:ventas'."""
    if not fuente or not fuente.startswith("auto:"):
        return None
    origen = fuente.split(":", 1)[1]

    if origen == "ventas":
        return _valor_ventas(indicador, anio, mes)

    # otros módulos se irán agregando aquí (cartera, ingresos, …)
    return None


def _valor_ventas(indicador, anio, mes):
    """Venta o Utilidad de un vendedor (o total) para el mes."""
    iid = indicador["id"]
    # ¿es venta o utilidad? por el prefijo del id
    if iid.startswith("venta"):
        columna = _COL_VENTA
    elif iid.startswith("utilidad") or iid.startswith("ub"):
        columna = _COL_UTILIDAD
    else:
        return None

    # ¿qué vendedor? el nombre del indicador es el del vendedor
    # (los hijos), o None si fuese un total.
    vendedor = indicador.get("nombre") if indicador.get("nivel") == 1 else None
    return _suma_columna(anio, mes, vendedor, columna)