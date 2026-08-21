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
        # identidad de vendedor por usuario (para la captura de
        # proyecciones). Un usuario puede tener asignado el nombre
        # EXACTO del vendedor como aparece en Ventas.
        cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS vendedor TEXT;")
    # tablas del módulo Proyección
    inicializar_esquema_proyeccion()
    # comentarios de proyección (por vendedor/mes/producto)
    inicializar_esquema_comentarios_proyeccion()
    # tabla del histórico mensual de inventario
    inicializar_esquema_inventario_historico()


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
        cur.execute("SELECT password_hash, rol, vendedor FROM usuarios "
                    "WHERE usuario=%s;", (usuario,))
        fila = cur.fetchone()
    if not fila:
        return None
    if bcrypt.checkpw(password.encode(), fila[0].encode()):
        # la sesión lleva el vendedor asignado (o None) para saber
        # qué proyección puede editar este usuario.
        return {"usuario": usuario, "rol": fila[1], "vendedor": fila[2]}
    return None


# =========================================================
# ADMINISTRACIÓN DE USUARIOS DE CONSULTA
# =========================================================
# Estas funciones SOLO operan sobre usuarios de rol 'consulta'.
# Los admin quedan protegidos: no se pueden cambiar ni eliminar
# desde aquí (la validación es en el servidor, no solo en la UI).

def listar_usuarios_consulta():
    """Lista los usuarios de rol 'consulta' (para el panel admin).
    NO incluye admins."""
    with _conn() as c, c.cursor() as cur:
        cur.execute(
            "SELECT usuario, creado, vendedor FROM usuarios WHERE rol='consulta' "
            "ORDER BY usuario;"
        )
        filas = cur.fetchall()
    return [{"usuario": f[0], "creado": f[1], "vendedor": f[2]} for f in filas]


def _rol_de(usuario):
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT rol FROM usuarios WHERE usuario=%s;", (usuario,))
        fila = cur.fetchone()
    return fila[0] if fila else None


def crear_usuario_consulta(usuario, password, vendedor=None):
    """Crea un usuario de consulta. Falla si el nombre ya existe
    (con cualquier rol) para no pisar un admin por accidente.
    vendedor: (opcional) nombre EXACTO del vendedor como aparece
    en Ventas; si se asigna, ese usuario podrá editar la
    proyección de ese vendedor."""
    usuario = (usuario or "").strip()
    password = (password or "").strip()
    vendedor = (vendedor or "").strip() or None
    if not usuario or not password:
        raise ValueError("Usuario y contraseña son obligatorios.")
    if _rol_de(usuario) is not None:
        raise ValueError(f"El usuario '{usuario}' ya existe.")
    h = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with _conn() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO usuarios (usuario, password_hash, rol, vendedor) "
            "VALUES (%s, %s, 'consulta', %s);",
            (usuario, h, vendedor),
        )


def cambiar_password_consulta(usuario, nueva):
    """Cambia la contraseña SOLO si el usuario es de consulta."""
    usuario = (usuario or "").strip()
    nueva = (nueva or "").strip()
    if not nueva:
        raise ValueError("La nueva contraseña no puede estar vacía.")
    if _rol_de(usuario) != "consulta":
        raise ValueError("Solo se pueden cambiar contraseñas de usuarios de consulta.")
    h = bcrypt.hashpw(nueva.encode(), bcrypt.gensalt()).decode()
    with _conn() as c, c.cursor() as cur:
        cur.execute("UPDATE usuarios SET password_hash=%s WHERE usuario=%s AND rol='consulta';",
                    (h, usuario))


def eliminar_usuario_consulta(usuario):
    """Elimina SOLO si el usuario es de consulta."""
    usuario = (usuario or "").strip()
    if _rol_de(usuario) != "consulta":
        raise ValueError("Solo se pueden eliminar usuarios de consulta.")
    with _conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM usuarios WHERE usuario=%s AND rol='consulta';",
                    (usuario,))

# =========================================================
# ===============  MÓDULO PROYECCIÓN  =====================
# =========================================================
# La proyección se guarda por AÑO/MES/PRODUCTO. La LISTA de
# productos es POR MES: los productos de un mes son los que
# tienen fila en la proyección de ese mes. Un mes que aún no
# se ha tocado arranca con la lista PREDETERMINADA (semilla).
#
#   proyecciones : (anio INT, mes INT, producto TEXT,
#                   cantidad NUMERIC)  PK (anio, mes, producto)


# Lista PREDETERMINADA de productos principales (semilla).
# Se usa para PRECARGAR un mes que aún no tiene nada guardado.
_PRODUCTOS_SEMILLA = [
    "HIPOCLORITO DE CALCIO GRANULAR HTH",
    "PERCARBONATO DE SODIO PROVOX",
    "ESTIREN ACRILICA",
    "ACIDO FOSFORICO CLARIFICADO 85%",
    "ALCOHOL POLIVINILICO PVOH 08850",
    "PROTEINA VEGETAL PVH 11307",
    "LESS 70%",
    "NONIL FENOL 10 MOLES",
    "BIOXIDO DE TITANIO",
    "TWEEN 20",
    "XILOL",
    "ALCOHOL TRIDECILICO 8 MOLES",
    "ACIDO ACETICO GLACIAL ALIMENTICIO",
    "POTASA CAUSTICA EN ESCAMA",
    "CARBONATO DE POTASIO LIGERO ROT",
    "EDTA",
]


def productos_semilla():
    """Devuelve la lista predeterminada (para precargar un mes
    nuevo). Copia, para no exponer la lista interna."""
    return list(_PRODUCTOS_SEMILLA)


# Los 3 vendedores. El nombre debe ser EXACTO como aparece en la
# columna Vendedor de Ventas (para que el cruce por vendedor cuadre).
# Si algún nombre difiere en Ventas, corregirlo AQUÍ (un solo lugar).
VENDEDORES = ["ILSE GARCÍA", "FREDY SALAS", "MATEO LÓPEZ"]


def inicializar_esquema_proyeccion():
    """Crea la tabla de proyecciones (por vendedor) si no existe.
    MIGRACIÓN: si existe la versión vieja SIN columna 'vendedor',
    se limpia (drop) y se recrea con el nuevo esquema, ya que la
    proyección ahora se guarda por vendedor. Idempotente: una vez
    migrada, no se vuelve a borrar."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables "
                    "WHERE table_name='proyecciones';")
        existe = cur.fetchone() is not None
        if existe:
            cur.execute("SELECT 1 FROM information_schema.columns "
                        "WHERE table_name='proyecciones' "
                        "AND column_name='vendedor';")
            tiene_vendedor = cur.fetchone() is not None
            if not tiene_vendedor:
                # versión vieja (sin vendedor): limpiar y recrear
                cur.execute("DROP TABLE proyecciones;")
                existe = False
        if not existe:
            cur.execute("""
                CREATE TABLE proyecciones (
                    anio     INTEGER NOT NULL,
                    mes      INTEGER NOT NULL,
                    vendedor TEXT NOT NULL,
                    producto TEXT NOT NULL,
                    cantidad NUMERIC DEFAULT 0,
                    PRIMARY KEY (anio, mes, vendedor, producto)
                );
            """)


# -------- PROYECCIÓN / LISTA POR MES --------

def leer_proyeccion(anio, mes, vendedor):
    """Devuelve dict {producto: cantidad} de un año/mes para UN
    vendedor. Vacío si ese vendedor no tiene nada en ese mes."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT producto, cantidad FROM proyecciones "
                    "WHERE anio=%s AND mes=%s AND vendedor=%s "
                    "ORDER BY producto;",
                    (int(anio), int(mes), vendedor))
        filas = cur.fetchall()
    return {f[0]: float(f[1]) for f in filas}


def leer_proyeccion_acumulada(anio, mes):
    """Suma la proyección de TODOS los vendedores por producto
    (para la vista Acumulado). Devuelve {producto: cantidad_total}."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT producto, SUM(cantidad) FROM proyecciones "
                    "WHERE anio=%s AND mes=%s GROUP BY producto "
                    "ORDER BY producto;",
                    (int(anio), int(mes)))
        filas = cur.fetchall()
    return {f[0]: float(f[1]) for f in filas}


def listar_productos_mes(anio, mes, vendedor):
    """Lista de productos de un mes para un vendedor. Si ese
    vendedor no tiene nada en el mes, devuelve la lista
    PREDETERMINADA (semilla) para arrancar."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT producto FROM proyecciones "
                    "WHERE anio=%s AND mes=%s AND vendedor=%s "
                    "ORDER BY producto;",
                    (int(anio), int(mes), vendedor))
        filas = cur.fetchall()
    if filas:
        return [f[0] for f in filas]
    return productos_semilla()


def guardar_proyeccion(anio, mes, vendedor, proyeccion_por_producto):
    """Guarda (reemplaza) la proyección de un mes para UN vendedor.
    Deja ese (mes, vendedor) EXACTAMENTE con los productos
    recibidos: inserta/actualiza los que vienen y BORRA los que ya
    no estén. No toca a otros vendedores ni otros meses."""
    anio = int(anio); mes = int(mes)
    vendedor = (vendedor or "").strip()
    if not vendedor:
        raise ValueError("Falta el vendedor.")
    limpio = {}
    for producto, cantidad in proyeccion_por_producto.items():
        producto = (producto or "").strip()
        if not producto:
            continue
        try:
            cant = float(cantidad) if cantidad not in (None, "") else 0.0
        except (ValueError, TypeError):
            cant = 0.0
        limpio[producto] = cant

    with _conn() as c, c.cursor() as cur:
        # borrar de ese (mes, vendedor) los productos que ya no están
        if limpio:
            cur.execute(
                "DELETE FROM proyecciones WHERE anio=%s AND mes=%s "
                "AND vendedor=%s AND producto NOT IN %s;",
                (anio, mes, vendedor, tuple(limpio.keys())),
            )
        else:
            cur.execute("DELETE FROM proyecciones "
                        "WHERE anio=%s AND mes=%s AND vendedor=%s;",
                        (anio, mes, vendedor))
        # upsert de los que vienen
        for producto, cant in limpio.items():
            cur.execute("""
                INSERT INTO proyecciones (anio, mes, vendedor, producto, cantidad)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (anio, mes, vendedor, producto)
                DO UPDATE SET cantidad = EXCLUDED.cantidad;
            """, (anio, mes, vendedor, producto, cant))


def anios_con_proyeccion():
    """Años que ya tienen alguna proyección guardada (de cualquier
    vendedor)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT DISTINCT anio FROM proyecciones ORDER BY anio DESC;")
        filas = cur.fetchall()
    return [int(f[0]) for f in filas]


def meses_con_proyeccion(anio):
    """Meses con proyección para un año dado (de cualquier vendedor)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT DISTINCT mes FROM proyecciones "
                    "WHERE anio=%s ORDER BY mes;", (int(anio),))
        filas = cur.fetchall()
    return [int(f[0]) for f in filas]


# =========================================================
# ==========  HISTÓRICO MENSUAL DE INVENTARIO  ============
# =========================================================
# Foto mensual del inventario YA PROCESADO (mismas columnas que
# el inventario actual), guardada como JSONB con llave (anio, mes).
# Es INDEPENDIENTE del inventario semanal (tabla datasets); sirve
# de referencia para ver cómo va cambiando el inventario mes a mes.
#
#   inventario_historico : (anio INT, mes INT, datos JSONB,
#       fecha_corte TEXT, actualizado TIMESTAMP, subido_por TEXT)
#       PK (anio, mes)
#
# Reutiliza _normalizar_para_json (Timestamp->texto, NaN->None).


def inicializar_esquema_inventario_historico():
    """Crea la tabla del histórico de inventario si no existe.
    Se llama desde inicializar_esquema()."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventario_historico (
                anio        INTEGER NOT NULL,
                mes         INTEGER NOT NULL,
                datos       JSONB NOT NULL,
                fecha_corte TEXT,
                actualizado TIMESTAMP DEFAULT now(),
                subido_por  TEXT,
                PRIMARY KEY (anio, mes)
            );
        """)


def guardar_inventario_historico(anio, mes, df, admin=None, fecha_corte=None):
    """Guarda (reemplaza) la foto de inventario de un año/mes.
    df: DataFrame ya procesado (mismas columnas que el inventario
    actual). Si ya existía ese año/mes, se SOBRESCRIBE."""
    registros = _normalizar_para_json(df).to_dict("records")
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO inventario_historico
                (anio, mes, datos, fecha_corte, subido_por, actualizado)
            VALUES (%s, %s, %s, %s, %s, now())
            ON CONFLICT (anio, mes)
            DO UPDATE SET datos=EXCLUDED.datos,
                          fecha_corte=EXCLUDED.fecha_corte,
                          subido_por=EXCLUDED.subido_por,
                          actualizado=now();
        """, (int(anio), int(mes), Json(registros), fecha_corte, admin))


def leer_inventario_historico(anio, mes):
    """DataFrame de la foto guardada de ese año/mes, o None si no
    existe. (Sin caché: el histórico se consulta bajo demanda.)"""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT datos FROM inventario_historico "
                    "WHERE anio=%s AND mes=%s;", (int(anio), int(mes)))
        fila = cur.fetchone()
    return pd.DataFrame(fila[0]) if fila else None


def info_inventario_historico(anio, mes):
    """Metadatos de una foto: fecha de corte, cuándo se guardó y
    quién. None si no existe ese año/mes."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT fecha_corte, actualizado, subido_por "
                    "FROM inventario_historico WHERE anio=%s AND mes=%s;",
                    (int(anio), int(mes)))
        fila = cur.fetchone()
    if not fila:
        return None
    return {"fecha_corte": fila[0], "actualizado": fila[1],
            "subido_por": fila[2]}


def anios_con_historico_inv():
    """Años que ya tienen alguna foto de inventario guardada."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT DISTINCT anio FROM inventario_historico "
                    "ORDER BY anio DESC;")
        filas = cur.fetchall()
    return [int(f[0]) for f in filas]


def meses_con_historico_inv(anio):
    """Meses con foto de inventario para un año dado (ascendente)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT DISTINCT mes FROM inventario_historico "
                    "WHERE anio=%s ORDER BY mes;", (int(anio),))
        filas = cur.fetchall()
    return [int(f[0]) for f in filas]


# =========================================================
# ==========  COMENTARIOS DE PROYECCIÓN  ==================
# =========================================================
# Comentarios de texto libre por (año, mes, vendedor, producto),
# editables SOLO por el propio vendedor desde la vista de
# Proyección. Independientes de la cantidad proyectada; se
# guardan aparte para no tocar la tabla 'proyecciones'.
#
#   comentarios_proyeccion : (anio INT, mes INT, vendedor TEXT,
#       producto TEXT, comentario TEXT)  PK (anio,mes,vendedor,producto)


def inicializar_esquema_comentarios_proyeccion():
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comentarios_proyeccion (
                anio       INTEGER NOT NULL,
                mes        INTEGER NOT NULL,
                vendedor   TEXT NOT NULL,
                producto   TEXT NOT NULL,
                comentario TEXT DEFAULT '',
                PRIMARY KEY (anio, mes, vendedor, producto)
            );
        """)


def leer_comentarios(anio, mes, vendedor):
    """Dict {producto: comentario} de un (año, mes, vendedor)."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT producto, comentario FROM comentarios_proyeccion "
                    "WHERE anio=%s AND mes=%s AND vendedor=%s;",
                    (int(anio), int(mes), vendedor))
        filas = cur.fetchall()
    return {f[0]: (f[1] or "") for f in filas}


def guardar_comentarios(anio, mes, vendedor, comentarios_por_producto):
    """Guarda (upsert) los comentarios de un (año, mes, vendedor).
    comentarios_por_producto: dict {producto: texto}. Los textos
    vacíos también se guardan (permite borrar un comentario)."""
    anio = int(anio); mes = int(mes)
    vendedor = (vendedor or "").strip()
    if not vendedor:
        raise ValueError("Falta el vendedor.")
    with _conn() as c, c.cursor() as cur:
        for producto, texto in comentarios_por_producto.items():
            producto = (producto or "").strip()
            if not producto:
                continue
            texto = "" if texto is None else str(texto)
            cur.execute("""
                INSERT INTO comentarios_proyeccion
                    (anio, mes, vendedor, producto, comentario)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (anio, mes, vendedor, producto)
                DO UPDATE SET comentario = EXCLUDED.comentario;
            """, (anio, mes, vendedor, producto, texto))