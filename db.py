"""
=========================================================
db.py  —  Capa de acceso a datos (PostgreSQL / Supabase)
=========================================================
Guarda las BD de cada módulo (JSON) y los usuarios (login).
Incluye una CACHÉ EN MEMORIA del servidor para que los datos
no viajen del navegador en cada callback (optimización de
velocidad del filtro).

CONEXIÓN: la URL viene de DATABASE_URL (Render/Supabase).
Usar el pooler de Supabase (puerto 6543).

NORMALIZACIÓN: Timestamp -> texto ISO, NaN -> None (JSON no
admite NaN ni Timestamp).
"""

import os
import time
import pandas as pd
import psycopg2
import bcrypt
from psycopg2.extras import Json


def _conn():
    url = os.environ.get("DATABASE_URL") or os.environ.get("LIDERZA_DB_URL")
    if not url:
        raise RuntimeError("Falta DATABASE_URL en el entorno")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)


def inicializar_esquema():
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                modulo       TEXT PRIMARY KEY,
                datos        JSONB NOT NULL,
                actualizado  TIMESTAMP DEFAULT now(),
                subido_por   TEXT
            );
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario       TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                rol           TEXT NOT NULL DEFAULT 'consulta',
                creado        TIMESTAMP DEFAULT now()
            );
        """)


# =========================================================
# DATASETS
# =========================================================

def _normalizar_para_json(df):
    df = df.copy()
    for col in df.columns:
        if str(df[col].dtype).startswith("datetime"):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
    return df.astype(object).where(pd.notna(df), None)


def guardar_dataset(modulo, df, admin):
    """Reemplazo total. Además invalida la caché de ese módulo
    y sube su versión (para que los navegadores detecten el
    cambio y recarguen)."""
    registros = _normalizar_para_json(df).to_dict("records")
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO datasets (modulo, datos, subido_por, actualizado)
            VALUES (%s, %s, %s, now())
            ON CONFLICT (modulo)
            DO UPDATE SET datos=EXCLUDED.datos,
                          subido_por=EXCLUDED.subido_por,
                          actualizado=now();
        """, (modulo, Json(registros), admin))
    invalidar_cache(modulo)


def leer_dataset(modulo):
    """Lee la BD del módulo desde PostgreSQL (sin caché)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT datos FROM datasets WHERE modulo=%s;", (modulo,))
        fila = cur.fetchone()
    return pd.DataFrame(fila[0]) if fila else None


def info_dataset(modulo):
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT actualizado, subido_por FROM datasets WHERE modulo=%s;",
                    (modulo,))
        fila = cur.fetchone()
    return {"actualizado": fila[0], "subido_por": fila[1]} if fila else None


# =========================================================
# CACHÉ EN MEMORIA DEL SERVIDOR
# =========================================================
# _CACHE: modulo -> DataFrame ya cargado.
# _VERSION: modulo -> número que cambia cuando se suben datos
#           nuevos. El navegador guarda su versión en el store;
#           si difiere de la del servidor, recarga.

_CACHE = {}
_VERSION = {}


def obtener_df(modulo):
    """Devuelve el DataFrame del módulo desde la CACHÉ del
    servidor. Si no está en caché, lo lee de PostgreSQL una vez
    y lo guarda. Evita que los datos viajen del navegador."""
    if modulo not in _CACHE:
        df = leer_dataset(modulo)
        if df is not None:
            _CACHE[modulo] = df
            _VERSION.setdefault(modulo, _nueva_version())
    return _CACHE.get(modulo)


def version_actual(modulo):
    """Versión vigente de los datos del módulo. Si no hay nada
    cargado aún, intenta cargar para fijar versión."""
    if modulo not in _VERSION:
        obtener_df(modulo)
    return _VERSION.get(modulo, 0)


def invalidar_cache(modulo):
    """Borra la caché del módulo y sube su versión. Se llama
    al guardar datos nuevos, para que la próxima lectura traiga
    lo nuevo y los navegadores detecten el cambio."""
    _CACHE.pop(modulo, None)
    _VERSION[modulo] = _nueva_version()


def _nueva_version():
    # entero creciente basado en el tiempo (único por cambio)
    return int(time.time() * 1000)


# =========================================================
# USUARIOS / LOGIN
# =========================================================

def crear_usuario(usuario, password, rol="consulta"):
    h = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO usuarios (usuario, password_hash, rol)
            VALUES (%s, %s, %s)
            ON CONFLICT (usuario)
            DO UPDATE SET password_hash=EXCLUDED.password_hash, rol=EXCLUDED.rol;
        """, (usuario, h, rol))


def verificar_login(usuario, password):
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT password_hash, rol FROM usuarios WHERE usuario=%s;",
                    (usuario,))
        fila = cur.fetchone()
    if not fila:
        return None
    if bcrypt.checkpw(password.encode(), fila[0].encode()):
        return {"usuario": usuario, "rol": fila[1]}
    return None