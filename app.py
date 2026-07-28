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

from layouts.principal import crear_principal

# =========================
# Callbacks
# =========================

from callbacks.router_callbacks import registrar_router_callbacks
from ventas.callbacks import registrar_callbacks_ventas
from ventas.tablas_ventas import registrar_callbacks_tablas_ventas
from ventas.graficos import registrar_callbacks_graficos
from layouts.principal import registrar_callbacks_principal
registrar_callbacks_principal(app)

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

registrar_router_callbacks(app)

registrar_callbacks_ventas(app)
registrar_callbacks_tablas_ventas(app)
registrar_callbacks_graficos(app)

# =========================
# Ejecutar
# =========================

if __name__ == "__main__":

    app.run(debug=True)