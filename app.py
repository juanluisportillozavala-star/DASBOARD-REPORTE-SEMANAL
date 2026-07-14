"""
=========================================================
Sistema Gerencial Liderza
=========================================================
Aplicación principal
"""

from dash import Dash
import dash_bootstrap_components as dbc

from layouts.principal import crear_principal
from callbacks.router_callbacks import registrar_router_callbacks

app = Dash(

    __name__,

    external_stylesheets=[

        dbc.themes.BOOTSTRAP,

        dbc.icons.BOOTSTRAP,

        "/assets/estilos.css"

    ],

    suppress_callback_exceptions=True,

    title="Sistema Gerencial Liderza"

)

server = app.server

app.layout = crear_principal()

# ============================================
# CALLBACKS
# ============================================

registrar_router_callbacks(app)

if __name__ == "__main__":

    app.run(debug=True)