"""
============================================================
SISTEMA GERENCIAL LIDERZA
============================================================
Aplicación principal
"""

from dash import Dash
import dash_bootstrap_components as dbc

from ventas.layout import crear_layout
from ventas.callbacks import registrar_callbacks

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "/assets/estilos.css"
    ],
    suppress_callback_exceptions=True,
    title="Sistema Gerencial Liderza"
)

server = app.server

app.layout = crear_layout()

registrar_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)