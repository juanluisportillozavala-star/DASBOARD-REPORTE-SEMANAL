"""
=========================================================
proyeccion/logica.py
=========================================================
Cruza la PROYECCIÓN guardada (año/mes) con lo FACTURADO en
Ventas, para armar la tabla de cumplimiento.

Del módulo Ventas se toma, por producto (Producto 2) y para
el año/mes elegido:
  • cantidad facturada (suma)
  • utilidad bruta (suma)

Los productos vendidos que NO están en la lista de proyección
se agrupan en VARIOS (y se listan aparte en el detalle).
"""

import pandas as pd

from core import columnas as C

MES_COL = "Mes"
ANIO_COL = "Año"


def _ventas_del_periodo(df_ventas, anio, mes):
    """Filtra ventas por año+mes y agrega por producto:
    cantidad facturada y utilidad."""
    if df_ventas is None or len(df_ventas) == 0:
        return {}

    d = df_ventas
    if ANIO_COL in d.columns and anio is not None:
        d = d[d[ANIO_COL] == int(anio)]
    if MES_COL in d.columns and mes is not None:
        d = d[d[MES_COL] == int(mes)]

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


def construir_tabla_proyeccion(proyeccion, df_ventas, anio, mes):
    """
    proyeccion: dict {producto: cantidad_proyectada} (de db).
    Devuelve (filas_tabla, fila_total, detalle_varios).

    filas_tabla: lista de dicts con las columnas de la tabla.
    detalle_varios: lista de productos vendidos fuera de la lista.
    """
    ventas = _ventas_del_periodo(df_ventas, anio, mes)

    # separar la meta de VARIOS (si el usuario la capturó) del resto.
    # VARIOS no es un producto que se cruce con ventas: es el grupo de
    # todo lo vendido fuera de la lista.
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

    # 1) productos de la proyección (sin VARIOS)
    for prod in proy_productos:
        proy_cant = float(proy_productos.get(prod) or 0)
        v = ventas.get(prod, {})
        fact = float(v.get("cantidad", 0))
        util = float(v.get("utilidad", 0))
        filas.append(_fila(prod, proy_cant, fact, util))
        tot_proy += proy_cant
        tot_fact += fact
        tot_util += util

    # 2) VARIOS: productos vendidos que NO están en la proyección
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

    # la fila VARIOS aparece si hay ventas fuera de lista O si el usuario
    # le puso una meta. Usa esa meta como proyección -> calcula % avance.
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
    avance = (fact / proy * 100) if proy else None   # None = no aplica (varios)
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