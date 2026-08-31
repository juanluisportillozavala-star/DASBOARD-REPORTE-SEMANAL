"""
=========================================================
bsc/semanas.py  —  Semanas de calendario y días hábiles
=========================================================
SEMANAS: lunes a domingo, RECORTADAS al mes (Opción A). El
primer y último bloque pueden ser parciales; nunca cruzan de
mes, así el acumulado mensual siempre cuadra. Cada mes genera
SOLO sus columnas de semana (4 o 5 según caiga el calendario),
sin que nadie las defina a mano.

DÍAS HÁBILES: lunes a viernes (sin sábados ni domingos). Se
usan para el "deber ser": el % que DEBERÍAS llevar a esta
altura del mes = hábiles transcurridos / hábiles totales.
Esto replica la hoja "%avance" del Excel.
"""

import calendar
from datetime import date, timedelta


def semanas_del_mes(anio, mes):
    """Devuelve la lista de semanas (lunes-domingo) recortadas al
    mes. Cada semana es un dict:
        {"num": 1, "ini": date, "fin": date, "label": "1-4"}
    'num' es el número de semana dentro del mes (1..5) y sirve de
    llave estable para guardar la captura."""
    anio = int(anio)
    mes = int(mes)
    ndias = calendar.monthrange(anio, mes)[1]
    primero = date(anio, mes, 1)
    ultimo = date(anio, mes, ndias)

    semanas = []
    num = 0
    d = primero
    while d <= ultimo:
        # lunes de la semana que contiene a 'd' (weekday: lun=0)
        lunes = d - timedelta(days=d.weekday())
        domingo = lunes + timedelta(days=6)
        ini = max(lunes, primero)   # recortar al inicio del mes
        fin = min(domingo, ultimo)  # recortar al fin del mes
        num += 1
        label = f"{ini.day}" if ini.day == fin.day else f"{ini.day}-{fin.day}"
        semanas.append({"num": num, "ini": ini, "fin": fin, "label": label})
        d = domingo + timedelta(days=1)  # saltar al lunes siguiente
    return semanas


def dias_habiles_mes(anio, mes):
    """Total de días hábiles (lun-vie) que tiene el mes."""
    anio = int(anio)
    mes = int(mes)
    ndias = calendar.monthrange(anio, mes)[1]
    return sum(1 for dia in range(1, ndias + 1)
               if date(anio, mes, dia).weekday() < 5)


def dias_habiles_transcurridos(anio, mes, hasta=None):
    """Días hábiles transcurridos del mes hasta la fecha 'hasta'
    (inclusive). Si 'hasta' es None, usa hoy.
      - Mes futuro  -> 0
      - Mes pasado  -> el mes completo
      - Mes actual  -> hábiles hasta el día de hoy"""
    anio = int(anio)
    mes = int(mes)
    if hasta is None:
        hasta = date.today()
    ndias = calendar.monthrange(anio, mes)[1]

    if (anio, mes) > (hasta.year, hasta.month):
        return 0                       # mes futuro
    if (anio, mes) < (hasta.year, hasta.month):
        fin = ndias                    # mes pasado -> completo
    else:
        fin = min(hasta.day, ndias)    # mes actual -> hasta hoy

    return sum(1 for dia in range(1, fin + 1)
               if date(anio, mes, dia).weekday() < 5)


def deber_ser(anio, mes, hasta=None):
    """% esperado de avance a esta altura del mes (0..1).
    = días hábiles transcurridos / días hábiles totales."""
    tot = dias_habiles_mes(anio, mes)
    if tot == 0:
        return 0.0
    return dias_habiles_transcurridos(anio, mes, hasta) / tot


# =========================================================
# NIVEL ANUAL (para la vista Acumulado)
# =========================================================

def dias_habiles_anio(anio):
    """Total de días hábiles del año (suma de los 12 meses)."""
    return sum(dias_habiles_mes(anio, m) for m in range(1, 13))


def dias_habiles_transcurridos_anio(anio, hasta=None):
    """Días hábiles del año transcurridos hasta 'hasta' (hoy si None)."""
    if hasta is None:
        hasta = date.today()
    if anio > hasta.year:
        return 0
    if anio < hasta.year:
        return dias_habiles_anio(anio)
    # año en curso: meses completos anteriores + lo que va del mes actual
    tot = sum(dias_habiles_mes(anio, m) for m in range(1, hasta.month))
    tot += dias_habiles_transcurridos(anio, hasta.month, hasta)
    return tot


def deber_ser_anio(anio, hasta=None):
    """% esperado de avance del AÑO (0..1)."""
    tot = dias_habiles_anio(anio)
    if tot == 0:
        return 0.0
    return dias_habiles_transcurridos_anio(anio, hasta) / tot