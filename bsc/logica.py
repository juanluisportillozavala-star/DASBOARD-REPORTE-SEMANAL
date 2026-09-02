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
            "indicador": ind["nombre"],
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


# =========================================================
# CONSOLIDADO ANUAL  (vista "Acumulado")
# =========================================================

def construir_acumulado(anio, obj_anual, cap_por_mes, hasta=None):
    """Arma las filas del acumulado anual.
      obj_anual:   {indicador: objetivo_anual}
      cap_por_mes: {mes: {indicador: {semana: valor}}}
    Reglas:
      - acumulado mensual de cada indicador = mismo criterio del mes
        (flujo=suma de semanas, saldo=última semana).
      - total del año: flujo = suma de los 12 meses;
                       saldo = último mes con dato.
    Devuelve (filas, deber_ser_anual). Cada fila trae mes_1..mes_12,
    objetivo, acumulado (total del año), pct, color."""
    inds = catalogo.indicadores()
    ds = S.deber_ser_anio(anio, hasta)

    # 1) acumulado mensual de cada indicador (reusa construir_bsc)
    mensual = {}   # {id: {mes: acum}}
    for mes in range(1, 13):
        cap = cap_por_mes.get(mes, {})
        filas_mes, _, _ = construir_bsc(anio, mes, {}, cap)
        for f in filas_mes:
            mensual.setdefault(f["id"], {})[mes] = f["acumulado"]

    # 2) objetivo anual de los padres = suma de objetivos de sus hijos
    obj = dict(obj_anual)
    for ind in inds:
        if ind["suma_hijos"]:
            hijos = catalogo.hijos_de(ind["id"])
            vals = [obj_anual.get(h["id"]) for h in hijos]
            vals = [v for v in vals if v is not None]
            if vals:
                obj[ind["id"]] = float(sum(vals))

    # 3) armar filas
    filas = []
    for ind in inds:
        iid = ind["id"]
        meses = mensual.get(iid, {})
        if ind["tipo"] == "flujo":
            vals = [v for v in meses.values() if v is not None]
            total = float(sum(vals)) if vals else None
        else:  # saldo: último mes con dato
            total = None
            for m in range(1, 13):
                if meses.get(m) is not None:
                    total = meses[m]
        o = obj.get(iid)
        pct = (total / o) if (o not in (None, 0) and total is not None) else None
        fila = {
            "id": iid,
            "indicador": ind["nombre"],
            "nivel": ind["nivel"],
            "unidad": ind["unidad"],
            "objetivo": o,
            "acumulado": total,
            "pct": pct,
            "deber_ser": ds,
            "color": _color(ind["sentido"], total, o, ds),
        }
        for m in range(1, 13):
            fila[f"mes_{m}"] = meses.get(m)
        filas.append(fila)

    return filas, ds


# =========================================================
# OBJETIVOS FORMULADOS (para la pantalla de Objetivos)
# =========================================================

def formular_objetivos(objetivos_por_mes):
    """Completa los objetivos con las celdas CALCULADAS (no tecleadas):
      • Objetivo anual (mes 0):
          - flujo -> suma de los 12 meses del indicador
          - saldo -> el último mes con dato (meta fija del año)
      • Padres (suma_hijos): cada mes y el anual = suma de sus hijos.

    Entrada y salida: dict {mes: {id_indicador: valor}}, mes 0..12.
    Solo RELLENA lo calculado; respeta lo que ya venga tecleado en
    los hijos y principales. Devuelve un dict nuevo (no muta)."""
    inds = catalogo.indicadores()

    # copia editable
    out = {m: dict(objetivos_por_mes.get(m, {})) for m in range(0, 13)}

    # 1) padres: cada mes (1..12) = suma de hijos capturados ese mes
    for ind in inds:
        if not ind["suma_hijos"]:
            continue
        hijos = catalogo.hijos_de(ind["id"])
        for m in range(1, 13):
            vals = [out.get(m, {}).get(h["id"]) for h in hijos]
            vals = [v for v in vals if v is not None]
            if vals:
                out.setdefault(m, {})[ind["id"]] = float(sum(vals))

    # 2) objetivo anual (mes 0) de CADA indicador según su tipo
    for ind in inds:
        iid = ind["id"]
        meses = {m: out.get(m, {}).get(iid) for m in range(1, 13)}
        con_dato = [(m, v) for m, v in meses.items() if v is not None]
        if not con_dato:
            continue
        if ind["tipo"] == "flujo":
            anual = float(sum(v for _, v in con_dato))
        else:  # saldo: meta fija -> el último mes con dato
            anual = float(con_dato[-1][1])
        out.setdefault(0, {})[iid] = anual

    return out