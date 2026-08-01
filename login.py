"""
=========================================================
login.py  —  Pantalla de acceso (Pieza 5, Opción A visual)
=========================================================
Diseño Liderza (azul #173C73, dorado #D4AF37, blanco).
Usa componentes NATIVOS de Dash (html.Button, dcc.Input) en
vez de dash-bootstrap-components, para garantizar que el
clic del botón siempre engancha su callback.

El campo de contraseña tiene un ícono de OJO para mostrar/
ocultar la contraseña. El alternado se hace con un
clientside_callback (JavaScript en el navegador): es
instantáneo y no toca el servidor. No interfiere con el
n_submit (Enter) del login.
"""

from dash import Input, Output, State, html, dcc, no_update

import db

AZUL = "#173C73"
DORADO = "#D4AF37"
BLANCO = "#FFFFFF"
LOGO = "/assets/logo.png"

# estilo compartido de los inputs
_ESTILO_INPUT = {
    "width": "100%", "padding": "10px 12px", "borderRadius": "8px",
    "border": "1px solid #CBD5E1", "boxSizing": "border-box",
    "fontSize": "15px",
}


def _campo_password():
    """Input de contraseña con ícono de ojo para mostrar/ocultar."""
    estilo_pass = dict(_ESTILO_INPUT)
    estilo_pass["paddingRight"] = "42px"  # espacio para el ojo
    return html.Div(
        [
            dcc.Input(
                id="login-password",
                placeholder="Contraseña",
                type="password",
                n_submit=0,
                style=estilo_pass,
            ),
            html.I(
                id="login-ojo",
                className="fas fa-eye",
                n_clicks=0,
                title="Mostrar/ocultar contraseña",
                style={
                    "position": "absolute", "right": "14px", "top": "50%",
                    "transform": "translateY(-50%)", "cursor": "pointer",
                    "color": "#6C757D",
                },
            ),
        ],
        style={"position": "relative", "width": "100%", "marginBottom": "20px"},
    )


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
                dcc.Input(
                    id="login-usuario",
                    placeholder="Usuario",
                    type="text",
                    n_submit=0,
                    style=dict(_ESTILO_INPUT, marginBottom="12px"),
                ),
                _campo_password(),
                html.Button(
                    "Ingresar",
                    id="login-btn",
                    n_clicks=0,
                    style={"width": "100%", "backgroundColor": AZUL,
                           "color": BLANCO, "border": "none",
                           "padding": "12px", "borderRadius": "8px",
                           "fontWeight": "600", "fontSize": "15px",
                           "cursor": "pointer"},
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

    # Mostrar/ocultar contraseña (clientside: instantáneo, sin servidor)
    app.clientside_callback(
        """
        function(n, tipoActual) {
            if (!n) { return window.dash_clientside.no_update; }
            return tipoActual === "password" ? "text" : "password";
        }
        """,
        Output("login-password", "type"),
        Input("login-ojo", "n_clicks"),
        State("login-password", "type"),
        prevent_initial_call=True,
    )

    # Se dispara con el clic del botón O con Enter en cualquier campo
    @app.callback(
        Output("store-sesion", "data"),
        Output("login-mensaje", "children"),
        Input("login-btn", "n_clicks"),
        Input("login-usuario", "n_submit"),
        Input("login-password", "n_submit"),
        State("login-usuario", "value"),
        State("login-password", "value"),
        prevent_initial_call=True,
    )
    def hacer_login(n_clicks, s1, s2, usuario, password):
        # limpiar espacios accidentales
        usuario = (usuario or "").strip()
        password = (password or "").strip()

        if not usuario or not password:
            return no_update, "Escribe usuario y contraseña."
        try:
            resultado = db.verificar_login(usuario, password)
        except Exception as e:
            print(f">>> [LOGIN] error: {e}", flush=True)
            return no_update, "Error de conexión. Intenta de nuevo."
        if resultado is None:
            return no_update, "Usuario o contraseña incorrectos."
        return resultado, ""