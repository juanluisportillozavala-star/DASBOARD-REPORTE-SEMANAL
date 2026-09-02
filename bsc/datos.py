"""
=========================================================
bsc/datos.py  —  Capa de datos del módulo BSC
=========================================================
Dos tablas nuevas en Supabase (mismo patrón que db.py):

  bsc_objetivos : (anio, mes, indicador, objetivo)
      PK (anio, mes, indicador)
      La meta de cada indicador para ese mes.

  bsc_captura   : (anio, mes, semana, indicador, valor)
      PK (anio, mes, semana, indicador)
      El valor REAL tecleado por semana. El acumulado del mes
      lo calcula bsc/logica.py (suma o último, según el tipo).

Reutiliza la conexión de db.py (_conn) para no duplicar la
lógica de conexión a Supabase.
"""

from db import _conn


# =========================================================
# ESQUEMA
# =========================================================

def inicializar_esquema_bsc():
    """Crea las tablas del BSC si no existen. Idempotente."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bsc_objetivos (
                anio      INTEGER NOT NULL,
                mes       INTEGER NOT NULL,
                indicador TEXT    NOT NULL,
                objetivo  NUMERIC DEFAULT 0,
                PRIMARY KEY (anio, mes, indicador)
            );
            CREATE TABLE IF NOT EXISTS bsc_captura (
                anio      INTEGER NOT NULL,
                mes       INTEGER NOT NULL,
                semana    INTEGER NOT NULL,
                indicador TEXT    NOT NULL,
                valor     NUMERIC DEFAULT 0,
                PRIMARY KEY (anio, mes, semana, indicador)
            );
        """)


# =========================================================
# OBJETIVOS
# =========================================================

def leer_objetivos(anio, mes):
    """Devuelve {id_indicador: objetivo(float)} de ese año/mes."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT indicador, objetivo FROM bsc_objetivos "
                    "WHERE anio=%s AND mes=%s;", (int(anio), int(mes)))
        filas = cur.fetchall()
    return {f[0]: float(f[1]) for f in filas if f[1] is not None}


def guardar_objetivos(anio, mes, objetivos_por_indicador):
    """Upsert de los objetivos de un mes.
    objetivos_por_indicador: {id_indicador: valor}. Los vacíos
    (None o "") se ignoran (no se guardan como 0)."""
    anio = int(anio); mes = int(mes)
    with _conn() as c, c.cursor() as cur:
        for iid, val in objetivos_por_indicador.items():
            iid = (iid or "").strip()
            if not iid:
                continue
            try:
                v = float(val) if val not in (None, "") else None
            except (ValueError, TypeError):
                v = None
            if v is None:
                continue
            cur.execute("""
                INSERT INTO bsc_objetivos (anio, mes, indicador, objetivo)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (anio, mes, indicador)
                DO UPDATE SET objetivo = EXCLUDED.objetivo;
            """, (anio, mes, iid, v))


# =========================================================
# CAPTURA (valores reales por semana)
# =========================================================

def leer_captura(anio, mes):
    """Devuelve {id_indicador: {num_semana: valor(float)}} del mes."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT indicador, semana, valor FROM bsc_captura "
                    "WHERE anio=%s AND mes=%s;", (int(anio), int(mes)))
        filas = cur.fetchall()
    out = {}
    for iid, sem, val in filas:
        if val is None:
            continue
        out.setdefault(iid, {})[int(sem)] = float(val)
    return out


def guardar_captura(anio, mes, valores):
    """Upsert de la captura de un mes.
    valores: lista de tuplas (indicador, semana, valor). Un valor
    None o "" BORRA esa celda (para poder dejarla en blanco)."""
    anio = int(anio); mes = int(mes)
    with _conn() as c, c.cursor() as cur:
        for iid, sem, val in valores:
            iid = (iid or "").strip()
            if not iid:
                continue
            sem = int(sem)
            try:
                v = float(val) if val not in (None, "") else None
            except (ValueError, TypeError):
                v = None
            if v is None:
                cur.execute("DELETE FROM bsc_captura WHERE anio=%s AND mes=%s "
                            "AND semana=%s AND indicador=%s;",
                            (anio, mes, sem, iid))
            else:
                cur.execute("""
                    INSERT INTO bsc_captura (anio, mes, semana, indicador, valor)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (anio, mes, semana, indicador)
                    DO UPDATE SET valor = EXCLUDED.valor;
                """, (anio, mes, sem, iid, v))


# =========================================================
# AÑOS / MESES DISPONIBLES
# =========================================================

def anios_con_bsc():
    """Años que ya tienen objetivos o captura (para el selector)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT anio FROM (
                SELECT anio FROM bsc_objetivos
                UNION SELECT anio FROM bsc_captura
            ) t ORDER BY anio DESC;
        """)
        filas = cur.fetchall()
    return [int(f[0]) for f in filas]


def meses_con_bsc(anio):
    """Meses con datos para un año dado (ascendente)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT mes FROM (
                SELECT mes FROM bsc_objetivos WHERE anio=%s
                UNION SELECT mes FROM bsc_captura WHERE anio=%s
            ) t ORDER BY mes;
        """, (int(anio), int(anio)))
        filas = cur.fetchall()
    return [int(f[0]) for f in filas]


# =========================================================
# NIVEL ANUAL  (objetivos de los 12 meses + captura del año)
# =========================================================
# El objetivo ANUAL se guarda en la misma tabla bsc_objetivos
# usando mes = 0 (los meses reales son 1..12).

def leer_objetivos_anio(anio):
    """Devuelve {mes: {indicador: objetivo}} para mes 0..12.
    mes 0 = objetivo anual."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT mes, indicador, objetivo FROM bsc_objetivos "
                    "WHERE anio=%s;", (int(anio),))
        filas = cur.fetchall()
    out = {}
    for mes, iid, val in filas:
        if val is None:
            continue
        out.setdefault(int(mes), {})[iid] = float(val)
    return out


def guardar_objetivos_anio(anio, valores, reemplazar_anio=False):
    """Upsert de objetivos anuales y mensuales de un año.
    valores: lista de tuplas (mes, indicador, valor). mes 0 = anual.
    Un valor None o "" BORRA esa celda.
    reemplazar_anio=True: primero BORRA todos los objetivos del año
    (para dejar exactamente lo recibido; útil cuando se recalcula
    todo desde la pantalla de captura)."""
    anio = int(anio)
    with _conn() as c, c.cursor() as cur:
        if reemplazar_anio:
            cur.execute("DELETE FROM bsc_objetivos WHERE anio=%s;", (anio,))
        for mes, iid, val in valores:
            iid = (iid or "").strip()
            if not iid:
                continue
            mes = int(mes)
            try:
                v = float(val) if val not in (None, "") else None
            except (ValueError, TypeError):
                v = None
            if v is None:
                cur.execute("DELETE FROM bsc_objetivos WHERE anio=%s AND mes=%s "
                            "AND indicador=%s;", (anio, mes, iid))
            else:
                cur.execute("""
                    INSERT INTO bsc_objetivos (anio, mes, indicador, objetivo)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (anio, mes, indicador)
                    DO UPDATE SET objetivo = EXCLUDED.objetivo;
                """, (anio, mes, iid, v))


def leer_captura_anio(anio):
    """Devuelve {mes: {indicador: {semana: valor}}} de todo el año."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT mes, indicador, semana, valor FROM bsc_captura "
                    "WHERE anio=%s;", (int(anio),))
        filas = cur.fetchall()
    out = {}
    for mes, iid, sem, val in filas:
        if val is None:
            continue
        out.setdefault(int(mes), {}).setdefault(iid, {})[int(sem)] = float(val)
    return out