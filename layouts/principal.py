"""
LAYOUT PRINCIPAL  (con compuerta de login)
"""

from dash import html, dcc, Input, Output

from layouts.header import crear_header
from layouts.sidebar import crear_sidebar
from login import crear_layout_login, registrar_callbacks_login


def crear_app_interna(rol=None):
    """La app real (lo que antes devolvía crear_principal). Se
    muestra SOLO con sesión iniciada. Recibe el rol para que el
    sidebar oculte o muestre opciones de admin."""
    return html.Div(
        children=[
            dcc.Location(id="url", refresh=False),
            crear_header(),
            html.Div(className="linea-dorada"),
            crear_sidebar(rol),
            html.Div(
                className="body",
                children=[
                    html.Div(id="contenido-principal", className="contenido")
                ],
            ),
        ]
    )


def crear_principal():
    """Raíz: stores de sesión + contenedor que alterna login/app."""
    return html.Div(
        children=[
            dcc.Store(id="store-sesion", data=None),
            html.Div(id="raiz-vista"),
        ]
    )


def registrar_callbacks_principal(app):
    """Registra el login y la compuerta login/app."""
    registrar_callbacks_login(app)

    @app.callback(
        Output("raiz-vista", "children"),
        Input("store-sesion", "data"),
    )
    def mostrar_vista(sesion):
        if not sesion:
            return crear_layout_login()
        return crear_app_interna(sesion.get("rol"))