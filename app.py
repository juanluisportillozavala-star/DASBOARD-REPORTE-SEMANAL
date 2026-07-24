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
from ventas.tabla_producto_cliente import registrar_callbacks_tabla_pc

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

# =========================
# Registrar callbacks
# =========================

registrar_router_callbacks(app)

registrar_callbacks_ventas(app)
registrar_callbacks_tabla_pc(app)

# =========================
# Ejecutar
# =========================

if __name__ == "__main__":

    app.run(debug=True)