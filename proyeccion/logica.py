"""
=========================================================
proyeccion/logica.py
=========================================================
Cruza la PROYECCIÓN guardada (año/mes) con lo FACTURADO en
Ventas, para armar la tabla de cumplimiento.

Ahora la proyección es POR VENDEDOR:
  • Vista "Acumulado": proyección = suma de los 3 vendedores;
    ventas = TODAS (sin filtrar por vendedor).
  • Vista de un vendedor: su proyección; ventas SOLO de ese
    vendedor (se filtra por la columna Vendedor de Ventas).

Del módulo Ventas se toma, por producto (Producto 2) y para el
año/mes elegido: cantidad facturada (suma) y utilidad (suma).

Los productos vendidos que NO están en la lista de proyección
se agrupan en VARIOS (y se listan aparte en el detalle).
"""

import pandas as pd

from core import columnas as C

MES_COL = "Mes"
ANIO_COL = "Año"


def _ventas_del_periodo(df_ventas, anio, mes, vendedor=None):
    """Filtra ventas por año+mes (y por vendedor si se indica) y
    agrega por producto: cantidad facturada y utilidad."""
    if df_ventas is None or len(df_ventas) == 0:
        return {}

    d = df_ventas
    if ANIO_COL in d.columns and anio is not None:
        d = d[d[ANIO_COL] == int(anio)]
    if MES_COL in d.columns and mes is not None:
        d = d[d[MES_COL] == int(mes)]

    # filtro por vendedor (solo para las pestañas de un vendedor)
    if vendedor and C.RAW_VENDEDOR in d.columns:
        d = d[d[C.RAW_VENDEDOR].astype(str).str.strip() == str(vendedor).strip()]

    if len(d) == 0:
        return {}

    col_prod = C.PRODUCTO_2
    col_cant = C.RAW_CANTIDAD
    col_ut = C.UT_BRUTA

    g = d.groupby(col_prod).agg(
        cantidad=(col_cant, "sum"),
        utilidad=(col_ut, "sum"),
    )
    return {
        str(prod): {"cantidad": float(r["cantidad"]),
                    "utilidad": float(r["utilidad"])}
        for prod, r in g.iterrows()
    }


def construir_tabla_proyeccion(proyeccion, df_ventas, anio, mes, vendedor=None):
    """
    proyeccion: dict {producto: cantidad_proyectada} (de db).
    vendedor:   None -> Acumulado (ventas totales);
                nombre -> ventas SOLO de ese vendedor.
    Devuelve (filas_tabla, fila_total, detalle_varios).
    """
    ventas = _ventas_del_periodo(df_ventas, anio, mes, vendedor)

    meta_varios = 0.0
    proy_productos = {}
    for k, v in proyeccion.items():
        if str(k).strip().upper() == "VARIOS":
            meta_varios = float(v or 0)
        else:
            proy_productos[k] = v

    productos_proy = set(proy_productos.keys())

    filas = []
    tot_proy = tot_fact = tot_util = 0.0

    for prod in proy_productos:
        proy_cant = float(proy_productos.get(prod) or 0)
        v = ventas.get(prod, {})
        fact = float(v.get("cantidad", 0))
        util = float(v.get("utilidad", 0))
        filas.append(_fila(prod, proy_cant, fact, util))
        tot_proy += proy_cant
        tot_fact += fact
        tot_util += util

    varios_cant = varios_util = 0.0
    detalle_varios = []
    for prod, v in ventas.items():
        if prod not in productos_proy:
            varios_cant += v["cantidad"]
            varios_util += v["utilidad"]
            detalle_varios.append({
                "producto": prod,
                "facturado": round(v["cantidad"], 2),
                "utilidad": round(v["utilidad"], 2),
                "util_unit": round(v["utilidad"] / v["cantidad"], 2) if v["cantidad"] else 0,
            })

    if varios_cant or varios_util or meta_varios:
        filas.append(_fila("VARIOS", meta_varios, varios_cant, varios_util))
        tot_proy += meta_varios
        tot_fact += varios_cant
        tot_util += varios_util

    detalle_varios.sort(key=lambda x: x["utilidad"], reverse=True)

    fila_total = _fila("TOTAL", tot_proy, tot_fact, tot_util)

    return filas, fila_total, detalle_varios


def _fila(producto, proy, fact, util):
    diferencia = fact - proy
    avance = (fact / proy * 100) if proy else None
    util_unit = (util / fact) if fact else 0.0
    return {
        "producto": producto,
        "proyeccion": round(proy, 2),
        "facturado": round(fact, 2),
        "diferencia": round(diferencia, 2),
        "avance": round(avance, 1) if avance is not None else None,
        "utilidad": round(util, 2),
        "util_unit": round(util_unit, 2),
    }