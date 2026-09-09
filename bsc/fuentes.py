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
_COL_FECHA = "Asiento contable/Fecha de factura"

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

    if origen == "cartera":
        return _valor_cartera(indicador, anio, mes)

    if origen == "saldo_proveedor":
        return _valor_saldo_prov(indicador, anio, mes)

    # otros módulos se irán agregando aquí (ingresos, inventario, …)
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


# =========================================================
# DESGLOSE POR SEMANA (para la vista mensual)
# =========================================================
import pandas as pd
from bsc import semanas as _S


def _suma_por_semana(anio, mes, vendedor_bsc, columna):
    """Devuelve {num_semana: suma} repartiendo 'columna' según la
    FECHA de factura de cada fila, usando las semanas del BSC
    (lunes-domingo recortadas al mes). None-safe."""
    sub = _df_ventas_mes(anio, mes)
    if sub is None or columna not in sub.columns or _COL_FECHA not in sub.columns:
        return {}
    if vendedor_bsc is not None:
        nombre = _VENDEDOR_BSC_A_VENTAS.get(vendedor_bsc, vendedor_bsc)
        if _COL_VENDEDOR not in sub.columns:
            return {}
        sub = sub[sub[_COL_VENDEDOR].astype(str).str.strip() == nombre]
        if len(sub) == 0:
            return {}

    sub = sub.copy()
    sub["_f"] = pd.to_datetime(sub[_COL_FECHA], errors="coerce")
    sems = _S.semanas_del_mes(anio, mes)

    out = {}
    for s in sems:
        ini = pd.Timestamp(s["ini"])
        fin = pd.Timestamp(s["fin"]) + pd.Timedelta(days=1)  # exclusivo
        m = (sub["_f"] >= ini) & (sub["_f"] < fin)
        val = sub.loc[m, columna].sum()
        out[s["num"]] = float(val) if val else 0.0
    return out


def semanas_auto(fuente, indicador, anio, mes):
    """Desglose por semana de un indicador AUTO, o {} si no aplica.
    Devuelve {num_semana: valor}."""
    if not fuente or not fuente.startswith("auto:"):
        return {}
    if fuente.split(":", 1)[1] != "ventas":
        return {}
    iid = indicador["id"]
    if iid.startswith("venta"):
        columna = _COL_VENTA
    elif iid.startswith("utilidad") or iid.startswith("ub"):
        columna = _COL_UTILIDAD
    else:
        return {}
    vendedor = indicador.get("nombre") if indicador.get("nivel") == 1 else None
    return _suma_por_semana(anio, mes, vendedor, columna)


# =========================================================
# MÓDULO CARTERA  (saldo -> última semana con datos del mes)
# =========================================================
# Rangos de aging (columnas de la BD de cartera):
#   Al corriente = "Por vencer" + "Vigente"
#   Vencido      = >90 + 61-90 + 31-60 + 0-30
# El dato del MES = la ÚLTIMA SEMANA con datos de ese mes (saldo
# más reciente), sumando solo Crédito (como la tabla dinámica).

_CART_COL_ANIO = "AÑO"
_CART_COL_MES = "MES"
_CART_COL_SEMANA = "SEMANA"
_CART_COL_TERMINOS = "TERMINOS DE PAGO"

_CART_CORRIENTE = ["Por vencer", "Vigente"]
_CART_VENCIDO = ["Vencido >90 días", "Vencido 61-90 días",
                 "Vencido 31-60 días", "Vencido 0-30 días"]


def _df_cartera_ultima_semana_mes(anio, mes):
    """DataFrame de la ÚLTIMA semana con datos del año/mes en
    cartera (solo Crédito). None si no hay."""
    df = db.obtener_df("cartera")
    if df is None or len(df) == 0:
        return None
    if _CART_COL_TERMINOS in df.columns:
        df = df[df[_CART_COL_TERMINOS] == "Crédito"]
    if _CART_COL_ANIO in df.columns:
        df = df[df[_CART_COL_ANIO] == int(anio)]
    if _CART_COL_MES in df.columns:
        df = df[df[_CART_COL_MES] == int(mes)]
    if len(df) == 0 or _CART_COL_SEMANA not in df.columns:
        return None
    # última semana con datos de ese mes
    import pandas as pd
    sem = pd.to_numeric(df[_CART_COL_SEMANA], errors="coerce").dropna()
    if len(sem) == 0:
        return None
    ult = int(sem.max())
    return df[pd.to_numeric(df[_CART_COL_SEMANA], errors="coerce") == ult]


def _valor_cartera(indicador, anio, mes):
    """Al corriente / Vencido de cartera para el mes (saldo de la
    última semana). Días cartera NO se calcula aquí (queda manual)."""
    iid = indicador["id"]
    if iid == "cartera_corr":
        cols = _CART_CORRIENTE
    elif iid == "cartera_venc":
        cols = _CART_VENCIDO
    else:
        return None  # dias_cartera u otro -> manual
    sub = _df_cartera_ultima_semana_mes(anio, mes)
    if sub is None or len(sub) == 0:
        return None
    total = 0.0
    for c in cols:
        if c in sub.columns:
            total += float(sub[c].sum())
    return total


# =========================================================
# MÓDULO SALDO PROVEEDOR  (saldo -> última semana del mes)
# =========================================================
# Aging (columnas de la BD de saldo_proveedor):
#   Al corriente = "Vigente"
#   Vencido      = ">60 días" + "31-60 días" + "0-30 días"
# El dato del MES = la ÚLTIMA SEMANA con datos de ese mes.
# NOTA: "Días proveedor" NO se calcula aquí (necesita compras
# acumuladas, dato que no está en este módulo) -> queda manual.

_SP_COL_ANIO = "AÑO"
_SP_COL_MES = "MES"
_SP_COL_SEMANA = "SEMANA"

_SP_CORRIENTE = ["Vigente"]
_SP_VENCIDO = ["Vencido >60 días", "Vencido 31-60 días", "Vencido 0-30 días"]


def _df_sp_ultima_semana_mes(anio, mes):
    """DataFrame de la última semana con datos del año/mes en
    saldo_proveedor. None si no hay."""
    df = db.obtener_df("saldo_proveedor")
    if df is None or len(df) == 0:
        return None
    import pandas as pd
    if _SP_COL_ANIO in df.columns:
        df = df[pd.to_numeric(df[_SP_COL_ANIO], errors="coerce") == int(anio)]
    if _SP_COL_MES in df.columns:
        df = df[pd.to_numeric(df[_SP_COL_MES], errors="coerce") == int(mes)]
    if len(df) == 0 or _SP_COL_SEMANA not in df.columns:
        return None
    sem = pd.to_numeric(df[_SP_COL_SEMANA], errors="coerce").dropna()
    if len(sem) == 0:
        return None
    ult = int(sem.max())
    return df[pd.to_numeric(df[_SP_COL_SEMANA], errors="coerce") == ult]


def _valor_saldo_prov(indicador, anio, mes):
    """Al corriente / Vencido de saldo proveedor (saldo de la última
    semana del mes). Días proveedor NO se calcula aquí (manual)."""
    iid = indicador["id"]
    if iid == "prov_corr":
        cols = _SP_CORRIENTE
    elif iid == "prov_venc":
        cols = _SP_VENCIDO
    else:
        return None  # dias_proveedor u otro -> manual
    sub = _df_sp_ultima_semana_mes(anio, mes)
    if sub is None or len(sub) == 0:
        return None
    total = 0.0
    for c in cols:
        if c in sub.columns:
            total += float(sub[c].sum())
    return total