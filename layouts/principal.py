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

from dash import html, dcc, Input, Output, State, no_update

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

    # Alterna visibilidad login/app, rellena el sidebar con el rol
    # y muestra el nombre del usuario en el header.
    # Al iniciar sesión, además fuerza la URL a /dashboard para que
    # SIEMPRE se entre al Dashboard (no al último módulo que se vio).
    @app.callback(
        Output("vista-login", "style"),
        Output("vista-app", "style"),
        Output("contenedor-sidebar", "children"),
        Output("header-nombre-usuario", "children"),
        Output("url", "pathname"),
        Input("store-sesion", "data"),
    )
    def alternar_vista(sesion):
        if not sesion:
            return {"display": "block"}, {"display": "none"}, None, "", no_update
        nombre = sesion.get("usuario", "")
        saludo = f"Hola, {nombre}" if nombre else ""
        return (
            {"display": "none"},
            {"display": "block"},
            crear_sidebar(sesion.get("rol")),
            saludo,
            "/dashboard",
        )

    # Cerrar sesión: limpia store-sesion -> la compuerta vuelve al login.
    # También VACÍA los campos de usuario/contraseña y el mensaje, para
    # que no queden los datos del usuario anterior visibles.
    @app.callback(
        Output("store-sesion", "data", allow_duplicate=True),
        Output("login-usuario", "value"),
        Output("login-password", "value"),
        Output("login-mensaje", "children", allow_duplicate=True),
        Input("btn-cerrar-sesion", "n_clicks"),
        prevent_initial_call=True,
    )
    def cerrar_sesion(n):
        if not n:
            return no_update, no_update, no_update, no_update
        return None, "", "", ""