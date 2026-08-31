"""
=========================================================
bsc/logica.py  —  Motor de cálculo del BSC
=========================================================
Arma las filas de la tabla del BSC para un año/mes. Es PURO:
no toca la base de datos; recibe los objetivos y la captura ya
leídos (vista.py los trae de bsc/datos.py y los pasa aquí).
Así se puede probar sin conexión.

REGLAS (deducidas de las fórmulas del Excel):
- tipo "flujo": acumulado del mes = SUMA de las semanas.
- tipo "saldo": acumulado = ÚLTIMA semana con dato (el saldo
  más reciente, no la suma).
- Padre con suma_hijos: acumulado = suma del acumulado de sus
  hijos.
- % cumplimiento = acumulado / objetivo.
- deber_ser = % esperado a esta altura del mes (de semanas.py).
- Semáforo:
    sentido "mayor": verde si % >= deber_ser; amarillo si está
      hasta 10 pts abajo; rojo más abajo.
    sentido "menor": se compara el nivel real contra el objetivo
      (para días/vencido): verde si real <= objetivo; amarillo
      si <= objetivo*1.10; rojo si lo rebasa.
"""

from bsc import catalogo
from bsc import semanas as S

MARGEN = 0.10   # 10 % de tolerancia para el amarillo


def _acumular(tipo, valores):
    """valores: lista (una por semana, en orden) con floats o None.
    flujo -> suma de los no vacíos.  saldo -> último no vacío."""
    limpios = [(i, v) for i, v in enumerate(valores) if v is not None]
    if not limpios:
        return None
    if tipo == "flujo":
        return float(sum(v for _, v in limpios))
    # saldo: el de mayor índice (semana más reciente con dato)
    return float(limpios[-1][1])


def _color(sentido, acum, obj, ds):
    """Devuelve 'verde' | 'amarillo' | 'rojo' | 'gris'."""
    if obj in (None, 0) or acum is None:
        return "gris"
    if sentido == "mayor":
        pct = acum / obj
        if pct >= ds - 1e-9:
            return "verde"
        if pct >= ds - MARGEN:
            return "amarillo"
        return "rojo"
    else:  # menor es mejor: comparar nivel real vs objetivo
        if acum <= obj:
            return "verde"
        if acum <= obj * (1 + MARGEN):
            return "amarillo"
        return "rojo"


def construir_bsc(anio, mes, objetivos, captura, hasta=None):
    """Devuelve (filas, semanas, deber_ser).
      objetivos: {id_indicador: objetivo(float)}
      captura:   {id_indicador: {num_semana: valor(float)}}
    Cada fila es un dict listo para la tabla (incluye sem_1..sem_N,
    acumulado, objetivo, pct, color, y metadatos)."""
    sems = S.semanas_del_mes(anio, mes)
    ds = S.deber_ser(anio, mes, hasta)
    inds = catalogo.indicadores()

    # 1) acumulado de cada indicador capturable (y de todos, para hijos)
    acum = {}
    for ind in inds:
        iid = ind["id"]
        if ind["suma_hijos"]:
            continue  # los padres se calculan después
        semvals = captura.get(iid, {})
        vals = [semvals.get(s["num"]) for s in sems]
        acum[iid] = _acumular(ind["tipo"], vals)

    # 2) padres = suma del acumulado de sus hijos
    for ind in inds:
        if ind["suma_hijos"]:
            hijos = catalogo.hijos_de(ind["id"])
            vals = [acum.get(h["id"]) for h in hijos]
            vals = [v for v in vals if v is not None]
            acum[ind["id"]] = float(sum(vals)) if vals else None

    # 3) armar filas
    filas = []
    for ind in inds:
        iid = ind["id"]
        a = acum.get(iid)
        obj = objetivos.get(iid)
        semvals = captura.get(iid, {})
        pct = (a / obj) if (obj not in (None, 0) and a is not None) else None
        fila = {
            "id": iid,
            "grupo": ind["grupo"],
            "indicador": ("    " + ind["nombre"]) if ind["nivel"] else ind["nombre"],
            "unidad": ind["unidad"],
            "tipo": ind["tipo"],
            "nivel": ind["nivel"],
            "objetivo": obj,
            "acumulado": a,
            "pct": pct,
            "deber_ser": ds,
            "color": _color(ind["sentido"], a, obj, ds),
            "capturable": ind["capturable"],
        }
        # valores por semana (para las columnas dinámicas)
        for s in sems:
            fila[f"sem_{s['num']}"] = semvals.get(s["num"])
        filas.append(fila)

    return filas, sems, ds