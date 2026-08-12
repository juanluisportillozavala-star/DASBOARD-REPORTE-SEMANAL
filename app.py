"""
=========================================================
SISTEMA GERENCIAL LIDERZA
=========================================================
Aplicación principal
"""

from dash import Dash
import dash_bootstrap_components as dbc

# =========================
# Layouts
# =========================

from layouts.principal import crear_principal, registrar_callbacks_principal

# =========================
# Callbacks
# =========================

from callbacks.router_callbacks import registrar_router_callbacks
from ventas.callbacks import registrar_callbacks_ventas
from ventas.tablas_ventas import registrar_callbacks_tablas_ventas
from ventas.graficos import registrar_callbacks_graficos
from carga import registrar_callbacks_carga

# Ingresos
from ingresos.callbacks import registrar_callbacks_ingresos
from ingresos.tabla_ingresos import registrar_callbacks_tabla_ingresos

# Inventario
from inventario.callbacks import registrar_callbacks_inventario_carga
from inventario.tabla_inventario import registrar_callbacks_inventario

# Configuración (admin de usuarios)
from configuracion import registrar_callbacks_configuracion

# Cartera
from cartera.callbacks import registrar_callbacks_cartera
from cartera.tabla_cartera import registrar_callbacks_tabla_cartera

# =========================
# Crear aplicación
# =========================

app = Dash(

    __name__,

    external_stylesheets=[

        dbc.themes.BOOTSTRAP,

        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css",

        "/assets/estilos.css"

    ],

    suppress_callback_exceptions=True,

    title="Sistema Gerencial Liderza"

)

server = app.server

# ==========================================================
# ENDPOINT /ping  —  mantiene DESPIERTA la base de datos
# ==========================================================
# Un servicio externo (cron-job.org) visita esta ruta cada
# pocos días. La consulta mínima "SELECT 1" toca Supabase y
# evita que el plan gratuito pause el proyecto por inactividad.
# No afecta el resto de la app.
import db as _db_ping

@server.route("/ping")
def ping():
    try:
        with _db_ping._conn() as c, c.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return "ok", 200
    except Exception as e:
        return f"error: {e}", 500

# =========================
# Layout principal
# =========================

app.layout = crear_principal()

# ==========================================================
# INICIALIZACIÓN DE BASE DE DATOS (Supabase / PostgreSQL)
# ==========================================================
import db

try:
    db.inicializar_esquema()
    print(">>> [DB] Conexión a Supabase OK. Tablas listas.", flush=True)
except Exception as e:
    print(f">>> [DB] ERROR conectando a Supabase: {e}", flush=True)

# =========================
# Registrar callbacks
# =========================

registrar_callbacks_principal(app)

registrar_router_callbacks(app)

# Ventas
registrar_callbacks_ventas(app)
registrar_callbacks_tablas_ventas(app)
registrar_callbacks_graficos(app)

# Carga central
registrar_callbacks_carga(app)

# Ingresos
registrar_callbacks_ingresos(app)
registrar_callbacks_tabla_ingresos(app)

# Inventario
registrar_callbacks_inventario_carga(app)
registrar_callbacks_inventario(app)

# Configuración
registrar_callbacks_configuracion(app)

# Cartera
registrar_callbacks_cartera(app)
registrar_callbacks_tabla_cartera(app)

# =========================
# Ejecutar
# =========================

if __name__ == "__main__":

    app.run(debug=True)