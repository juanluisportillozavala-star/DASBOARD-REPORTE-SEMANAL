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
        # MIGRACIÓN: columna para el OBJETIVO de cada semana (además
        # del valor real). Idempotente: si ya existe, no hace nada.
        cur.execute("ALTER TABLE bsc_captura "
                    "ADD COLUMN IF NOT EXISTS objetivo_semanal NUMERIC;")


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
    """Devuelve {id_indicador: {num_semana: valor_real}} del mes.
    (Compatibilidad: solo el real, como antes. Para el objetivo
    semanal usar leer_captura_completa.)"""
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


def leer_captura_completa(anio, mes):
    """Devuelve {id_indicador: {num_semana: {"real":x, "obj":y}}}
    con el valor real Y el objetivo semanal de cada semana."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT indicador, semana, valor, objetivo_semanal "
                    "FROM bsc_captura WHERE anio=%s AND mes=%s;",
                    (int(anio), int(mes)))
        filas = cur.fetchall()
    out = {}
    for iid, sem, val, obj in filas:
        d = out.setdefault(iid, {}).setdefault(int(sem), {})
        d["real"] = float(val) if val is not None else None
        d["obj"] = float(obj) if obj is not None else None
    return out


def guardar_captura(anio, mes, valores):
    """Upsert de la captura de un mes.
    valores: lista de tuplas (indicador, semana, real, obj_semanal).
    (También acepta la forma vieja (indicador, semana, real) por
    compatibilidad.) Si real y obj quedan ambos vacíos, BORRA la
    celda; si al menos uno tiene dato, se guarda."""
    anio = int(anio); mes = int(mes)

    def _num(x):
        try:
            return float(x) if x not in (None, "") else None
        except (ValueError, TypeError):
            return None

    with _conn() as c, c.cursor() as cur:
        for t in valores:
            if len(t) == 4:
                iid, sem, real, obj = t
            else:  # forma vieja (iid, sem, real)
                iid, sem, real = t
                obj = None
            iid = (iid or "").strip()
            if not iid:
                continue
            sem = int(sem)
            r = _num(real)
            o = _num(obj)
            if r is None and o is None:
                cur.execute("DELETE FROM bsc_captura WHERE anio=%s AND mes=%s "
                            "AND semana=%s AND indicador=%s;",
                            (anio, mes, sem, iid))
            else:
                cur.execute("""
                    INSERT INTO bsc_captura
                        (anio, mes, semana, indicador, valor, objetivo_semanal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (anio, mes, semana, indicador)
                    DO UPDATE SET valor = EXCLUDED.valor,
                                  objetivo_semanal = EXCLUDED.objetivo_semanal;
                """, (anio, mes, sem, iid, r, o))


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