"""
=========================================================
SISTEMA GERENCIAL LIDERZA
=========================================================
Archivo principal
"""

from dash import Dash
import dash_bootstrap_components as dbc

from layouts.home import layout
from callbacks.callbacks import register_callbacks

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP
    ],
    suppress_callback_exceptions=True,
    title="Sistema Gerencial Liderza"
)

server = app.server

app.layout = layout

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)