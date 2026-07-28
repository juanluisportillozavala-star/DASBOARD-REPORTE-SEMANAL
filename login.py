"""
=========================================================
login.py  —  Pantalla de acceso (Pieza 5, Opción A visual)
=========================================================
Compuerta de acceso al dashboard con diseño Liderza
(azul #173C73, dorado #D4AF37, blanco). Pide usuario y
contraseña, verifica contra la tabla `usuarios` de Supabase
(db.verificar_login) y guarda la sesión en un dcc.Store.

Uso desde el layout principal:
  - Incluir dcc.Store(id="store-sesion") a nivel raíz.
  - Mostrar crear_layout_login() si no hay sesión, o el
    dashboard si la hay (lo controla un callback en la app).
  - Llamar registrar_callbacks_login(app) una vez.
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_bootstrap_components as dbc

import db

# Paleta corporativa
AZUL = "#173C73"
DORADO = "#D4AF37"
BLANCO = "#FFFFFF"

# Nombre del archivo del logo en assets/. Ajustar si difiere.
LOGO = "/assets/logo.png"


def crear_layout_login():
    """Tarjeta de login centrada, con logo y colores Liderza."""
    return html.Div(
        html.Div(
            [
                html.Img(
                    src=LOGO,
                    style={"height": "70px", "marginBottom": "8px"},
                ),
                html.H3(
                    "Sistema Gerencial Liderza",
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "4px", "textAlign": "center"},
                ),
                html.P(
                    "Acceso al reporte",
                    style={"color": "#6C757D", "marginBottom": "24px",
                           "textAlign": "center"},
                ),
                dbc.Input(
                    id="login-usuario",
                    placeholder="Usuario",
                    type="text",
                    style={"marginBottom": "12px"},
                ),
                dbc.Input(
                    id="login-password",
                    placeholder="Contraseña",
                    type="password",
                    style={"marginBottom": "20px"},
                ),
                dbc.Button(
                    "Ingresar",
                    id="login-btn",
                    n_clicks=0,
                    style={"width": "100%", "backgroundColor": AZUL,
                           "border": "none", "fontWeight": "600"},
                ),
                html.Div(
                    id="login-mensaje",
                    style={"color": "#DC3545", "marginTop": "14px",
                           "textAlign": "center", "minHeight": "22px"},
                ),
            ],
            style={
                "backgroundColor": BLANCO,
                "padding": "40px 36px",
                "borderRadius": "16px",
                "boxShadow": "0 10px 40px rgba(23,60,115,0.18)",
                "borderTop": f"5px solid {DORADO}",
                "width": "360px",
                "maxWidth": "90vw",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
            },
        ),
        style={
            "minHeight": "100vh",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "background": f"linear-gradient(135deg, {AZUL} 0%, #0B2D5B 100%)",
        },
    )


def registrar_callbacks_login(app):

    @app.callback(
        Output("store-sesion", "data"),
        Output("login-mensaje", "children"),
        Input("login-btn", "n_clicks"),
        State("login-usuario", "value"),
        State("login-password", "value"),
        prevent_initial_call=True,
    )
    def hacer_login(n, usuario, password):
        if not usuario or not password:
            return no_update, "Escribe usuario y contraseña."
        try:
            resultado = db.verificar_login(usuario, password)
        except Exception as e:
            print(f">>> [LOGIN] error: {e}", flush=True)
            return no_update, "Error de conexión. Intenta de nuevo."
        if resultado is None:
            return no_update, "Usuario o contraseña incorrectos."
        # sesión válida: guarda usuario y rol
        return resultado, ""