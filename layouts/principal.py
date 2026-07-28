"""
LAYOUT PRINCIPAL  (con compuerta de login — versión robusta)

Clave de esta versión: los componentes del LOGIN y el
contenedor de la APP están SIEMPRE en el layout desde el
inicio (no se generan dinámicamente). Se muestran u ocultan
con 'display'. Así el botón de login siempre existe y su
callback queda bien conectado en el navegador (evita el
problema de componentes dinámicos con suppress_callback_
exceptions que hacía que el botón "no hiciera nada").
"""

from dash import html, dcc, Input, Output

from layouts.header import crear_header
from layouts.sidebar import crear_sidebar
from login import crear_layout_login, registrar_callbacks_login


def crear_principal():
    return html.Div(
        children=[
            dcc.Store(id="store-sesion", data=None),

            # ---- LOGIN: siempre presente, visible al inicio ----
            html.Div(
                id="vista-login",
                children=crear_layout_login(),
                style={"display": "block"},
            ),

            # ---- APP: siempre presente, oculta al inicio ----
            html.Div(
                id="vista-app",
                style={"display": "none"},
                children=[
                    dcc.Location(id="url", refresh=False),
                    crear_header(),
                    html.Div(className="linea-dorada"),
                    # el sidebar se rellena por callback según el rol
                    html.Div(id="contenedor-sidebar"),
                    html.Div(
                        className="body",
                        children=[
                            html.Div(id="contenido-principal",
                                     className="contenido")
                        ],
                    ),
                ],
            ),
        ]
    )


def registrar_callbacks_principal(app):
    registrar_callbacks_login(app)

    # Alterna visibilidad login/app y rellena el sidebar con el rol
    @app.callback(
        Output("vista-login", "style"),
        Output("vista-app", "style"),
        Output("contenedor-sidebar", "children"),
        Input("store-sesion", "data"),
    )
    def alternar_vista(sesion):
        if not sesion:
            return {"display": "block"}, {"display": "none"}, None
        return (
            {"display": "none"},
            {"display": "block"},
            crear_sidebar(sesion.get("rol")),
        )