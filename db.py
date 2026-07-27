"""
=========================================================
db.py  —  Capa de acceso a datos (PostgreSQL)
=========================================================
Pieza 1 del plan de arquitectura: estado compartido en base
de datos. Guarda las BD de cada módulo (como JSON) y los
usuarios para el login.

CONEXIÓN:
  En Render, la URL viene de la variable de entorno
  DATABASE_URL (la crea Render al añadir el PostgreSQL).
  En local, se puede usar una cadena de prueba.

  Nunca se escribe la URL en el código. Se lee del entorno:
      import os; CONN = os.environ["DATABASE_URL"]

DECISIONES aplicadas:
  • Reemplazo total semanal: guardar_dataset hace UPSERT
    (una sola foto por módulo; subir de nuevo la sustituye).
  • Dos roles: 'admin' (actualiza+consulta) y 'consulta'.
  • Contraseñas cifradas con bcrypt (jamás en texto plano).

NORMALIZACIÓN (aprendido probando con datos reales):
  Antes de guardar en JSON hay que arreglar dos cosas o
  PostgreSQL rechaza el dato:
    - Timestamp de pandas  -> texto ISO 'YYYY-MM-DD'
    - NaN / NaT            -> None  (JSON usa null, no NaN)
  Lo hace _normalizar_para_json().
"""

import os
import pandas as pd
import psycopg2
import bcrypt
from psycopg2.extras import Json


def _conn():
    """Devuelve una conexión nueva. Lee DATABASE_URL del entorno
    (Render la provee). Para local, define esa variable o pasa
    una cadena de prueba vía LIDERZA_DB_URL."""
    url = os.environ.get("DATABASE_URL") or os.environ.get("LIDERZA_DB_URL")
    if not url:
        raise RuntimeError("Falta DATABASE_URL en el entorno")
    # Render entrega URLs 'postgres://'; psycopg2 quiere 'postgresql://'
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)


def inicializar_esquema():
    """Crea las tablas si no existen. Llamar una vez al arrancar."""
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
# DATASETS (las BD de cada módulo)
# =========================================================

def _normalizar_para_json(df):
    """Prepara la BD para JSON: fechas -> texto ISO y NaN -> None."""
    df = df.copy()
    for col in df.columns:
        if str(df[col].dtype).startswith("datetime"):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
    return df.astype(object).where(pd.notna(df), None)


def guardar_dataset(modulo, df, admin):
    """Reemplazo total: sustituye la BD del módulo por la nueva."""
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


def leer_dataset(modulo):
    """Devuelve la BD del módulo como DataFrame, o None si no hay."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT datos FROM datasets WHERE modulo=%s;", (modulo,))
        fila = cur.fetchone()
    return pd.DataFrame(fila[0]) if fila else None


def info_dataset(modulo):
    """Metadatos: cuándo y quién actualizó (para mostrar en la UI)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT actualizado, subido_por FROM datasets WHERE modulo=%s;",
                    (modulo,))
        fila = cur.fetchone()
    return {"actualizado": fila[0], "subido_por": fila[1]} if fila else None


# =========================================================
# USUARIOS / LOGIN
# =========================================================

def crear_usuario(usuario, password, rol="consulta"):
    """Crea (o actualiza) un usuario con contraseña cifrada."""
    h = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO usuarios (usuario, password_hash, rol)
            VALUES (%s, %s, %s)
            ON CONFLICT (usuario)
            DO UPDATE SET password_hash=EXCLUDED.password_hash, rol=EXCLUDED.rol;
        """, (usuario, h, rol))


def verificar_login(usuario, password):
    """Devuelve {'usuario','rol'} si las credenciales son válidas, None si no."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT password_hash, rol FROM usuarios WHERE usuario=%s;",
                    (usuario,))
        fila = cur.fetchone()
    if not fila:
        return None
    if bcrypt.checkpw(password.encode(), fila[0].encode()):
        return {"usuario": usuario, "rol": fila[1]}
    return None