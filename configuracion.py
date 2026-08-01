"""
=========================================================
configuracion.py  —  Página de Configuración (solo admin)
=========================================================
Contiene el PANEL DE USUARIOS DE CONSULTA: listar, crear,
cambiar contraseña y eliminar usuarios de rol 'consulta'.
Los admin NO se pueden modificar desde aquí (protegidos en db.py).

Seguridad: el enlace solo aparece para admin y cada operación
valida el rol en el servidor (store-sesion) antes de ejecutarse.
"""

from dash import Input, Output, State, html, dcc, no_update, ctx, ALL
import dash_ag_grid as dag

import db

AZUL = "#173C73"
DORADO = "#D4AF37"


def _tarjeta(titulo, hijos):
    return html.Div(
        [html.H4(titulo, style={"color": AZUL, "fontWeight": "700",
                                "marginBottom": "16px"})] + hijos,
        style={"backgroundColor": "white", "padding": "24px",
               "borderRadius": "14px", "borderTop": f"4px solid {DORADO}",
               "boxShadow": "0 4px 16px rgba(23,60,115,0.08)",
               "marginBottom": "22px", "maxWidth": "640px"},
    )


def _input(id_, placeholder, tipo="text"):
    return dcc.Input(
        id=id_, type=tipo, placeholder=placeholder,
        style={"width": "100%", "padding": "10px 12px", "marginBottom": "12px",
               "borderRadius": "8px", "border": "1px solid #CBD5E1",
               "boxSizing": "border-box", "fontSize": "15px"},
    )


def _input_password(id_, placeholder, id_ojo):
    """Campo de contraseña con ícono de ojo para mostrar/ocultar."""
    return html.Div(
        [
            dcc.Input(
                id=id_, type="password", placeholder=placeholder,
                style={"width": "100%", "padding": "10px 42px 10px 12px",
                       "borderRadius": "8px", "border": "1px solid #CBD5E1",
                       "boxSizing": "border-box", "fontSize": "15px"},
            ),
            html.I(
                id=id_ojo, className="fas fa-eye", n_clicks=0,
                title="Mostrar/ocultar contraseña",
                style={"position": "absolute", "right": "14px", "top": "20px",
                       "transform": "translateY(-50%)", "cursor": "pointer",
                       "color": "#6C757D"},
            ),
        ],
        style={"position": "relative", "width": "100%", "marginBottom": "12px"},
    )


def _boton(texto, id_, color=AZUL):
    return html.Button(
        texto, id=id_, n_clicks=0,
        style={"backgroundColor": color, "color": "white", "border": "none",
               "padding": "10px 18px", "borderRadius": "8px",
               "fontWeight": "600", "cursor": "pointer"},
    )


def crear_layout_configuracion():
    return html.Div(
        [
            html.H1("Configuración", className="titulo"),
            html.P("Administración de usuarios de consulta.",
                   className="subtitulo"),
            html.Br(),

            # aviso si no es admin
            html.Div(id="config-aviso"),

            # ---- Lista de usuarios de consulta ----
            _tarjeta("Usuarios de consulta", [
                html.Div(id="config-lista-usuarios"),
                html.Br(),
                _boton("Actualizar lista", "config-btn-refrescar"),
            ]),

            # ---- Crear usuario ----
            _tarjeta("Crear usuario de consulta", [
                _input("config-nuevo-usuario", "Nombre de usuario"),
                _input_password("config-nuevo-password", "Contraseña", "config-ojo-nuevo"),
                _boton("Crear usuario", "config-btn-crear"),
                html.Div(id="config-msg-crear",
                         style={"marginTop": "12px", "minHeight": "22px"}),
            ]),

            # ---- Cambiar contraseña ----
            _tarjeta("Cambiar contraseña", [
                dcc.Dropdown(id="config-sel-usuario",
                             placeholder="Selecciona un usuario de consulta",
                             style={"marginBottom": "12px"}),
                _input_password("config-cambio-password", "Nueva contraseña", "config-ojo-cambio"),
                _boton("Cambiar contraseña", "config-btn-cambiar"),
                html.Div(id="config-msg-cambiar",
                         style={"marginTop": "12px", "minHeight": "22px"}),
            ]),

            # ---- Eliminar usuario ----
            _tarjeta("Eliminar usuario de consulta", [
                dcc.Dropdown(id="config-sel-eliminar",
                             placeholder="Selecciona un usuario de consulta",
                             style={"marginBottom": "12px"}),
                _boton("Eliminar usuario", "config-btn-eliminar", color="#C0392B"),
                html.Div(id="config-msg-eliminar",
                         style={"marginTop": "12px", "minHeight": "22px"}),
            ]),

            # store para forzar refresco de la lista tras cambios
            dcc.Store(id="config-refresco", data=0),
        ]
    )


def _es_admin(sesion):
    return bool(sesion) and sesion.get("rol") == "admin"


def _tabla_usuarios(usuarios):
    if not usuarios:
        return html.Div("No hay usuarios de consulta.",
                        style={"color": "#6C757D"})
    filas = [{"usuario": u["usuario"],
              "creado": str(u["creado"])[:10] if u["creado"] else ""}
             for u in usuarios]
    return dag.AgGrid(
        rowData=filas,
        columnDefs=[
            {"field": "usuario", "headerName": "Usuario", "flex": 2},
            {"field": "creado", "headerName": "Creado", "flex": 1},
        ],
        dashGridOptions={"domLayout": "autoHeight", "rowHeight": 34,
                         "headerHeight": 38, "suppressCellFocus": True},
        defaultColDef={"sortable": False, "filter": False, "resizable": True},
        className="ag-theme-alpine",
        style={"width": "100%",
               "--ag-header-background-color": AZUL,
               "--ag-header-foreground-color": "#FFFFFF"},
    )


def registrar_callbacks_configuracion(app):

    # Mostrar/ocultar contraseña (clientside, instantáneo) en los
    # dos campos de contraseña del panel.
    _js_ojo = """
        function(n, tipoActual) {
            if (!n) { return window.dash_clientside.no_update; }
            return tipoActual === "password" ? "text" : "password";
        }
    """
    app.clientside_callback(
        _js_ojo,
        Output("config-nuevo-password", "type"),
        Input("config-ojo-nuevo", "n_clicks"),
        State("config-nuevo-password", "type"),
        prevent_initial_call=True,
    )
    app.clientside_callback(
        _js_ojo,
        Output("config-cambio-password", "type"),
        Input("config-ojo-cambio", "n_clicks"),
        State("config-cambio-password", "type"),
        prevent_initial_call=True,
    )

    # Refrescar lista + opciones de dropdowns (al entrar, al refrescar,
    # y tras crear/cambiar/eliminar via config-refresco)
    @app.callback(
        Output("config-lista-usuarios", "children"),
        Output("config-sel-usuario", "options"),
        Output("config-sel-eliminar", "options"),
        Output("config-aviso", "children"),
        Input("config-refresco", "data"),
        Input("config-btn-refrescar", "n_clicks"),
        State("store-sesion", "data"),
    )
    def refrescar(_r, _n, sesion):
        if not _es_admin(sesion):
            aviso = html.Div("Solo un administrador puede administrar usuarios.",
                             style={"color": "#C0392B", "fontWeight": "600"})
            return no_update, [], [], aviso
        usuarios = db.listar_usuarios_consulta()
        opciones = [{"label": u["usuario"], "value": u["usuario"]} for u in usuarios]
        return _tabla_usuarios(usuarios), opciones, opciones, ""

    # Crear usuario
    @app.callback(
        Output("config-msg-crear", "children"),
        Output("config-refresco", "data", allow_duplicate=True),
        Input("config-btn-crear", "n_clicks"),
        State("config-nuevo-usuario", "value"),
        State("config-nuevo-password", "value"),
        State("store-sesion", "data"),
        State("config-refresco", "data"),
        prevent_initial_call=True,
    )
    def crear(n, usuario, password, sesion, refresco):
        if not _es_admin(sesion):
            return html.Span("No autorizado.", style={"color": "#C0392B"}), no_update
        try:
            db.crear_usuario_consulta(usuario, password)
            return (html.Span(f"Usuario '{usuario.strip()}' creado.",
                              style={"color": "#198754", "fontWeight": "600"}),
                    (refresco or 0) + 1)
        except Exception as e:
            return html.Span(str(e), style={"color": "#C0392B"}), no_update

    # Cambiar contraseña
    @app.callback(
        Output("config-msg-cambiar", "children"),
        Output("config-refresco", "data", allow_duplicate=True),
        Input("config-btn-cambiar", "n_clicks"),
        State("config-sel-usuario", "value"),
        State("config-cambio-password", "value"),
        State("store-sesion", "data"),
        State("config-refresco", "data"),
        prevent_initial_call=True,
    )
    def cambiar(n, usuario, password, sesion, refresco):
        if not _es_admin(sesion):
            return html.Span("No autorizado.", style={"color": "#C0392B"}), no_update
        if not usuario:
            return html.Span("Selecciona un usuario.", style={"color": "#C0392B"}), no_update
        try:
            db.cambiar_password_consulta(usuario, password)
            return (html.Span(f"Contraseña de '{usuario}' actualizada.",
                              style={"color": "#198754", "fontWeight": "600"}),
                    (refresco or 0) + 1)
        except Exception as e:
            return html.Span(str(e), style={"color": "#C0392B"}), no_update

    # Eliminar usuario
    @app.callback(
        Output("config-msg-eliminar", "children"),
        Output("config-refresco", "data", allow_duplicate=True),
        Input("config-btn-eliminar", "n_clicks"),
        State("config-sel-eliminar", "value"),
        State("store-sesion", "data"),
        State("config-refresco", "data"),
        prevent_initial_call=True,
    )
    def eliminar(n, usuario, sesion, refresco):
        if not _es_admin(sesion):
            return html.Span("No autorizado.", style={"color": "#C0392B"}), no_update
        if not usuario:
            return html.Span("Selecciona un usuario.", style={"color": "#C0392B"}), no_update
        try:
            db.eliminar_usuario_consulta(usuario)
            return (html.Span(f"Usuario '{usuario}' eliminado.",
                              style={"color": "#198754", "fontWeight": "600"}),
                    (refresco or 0) + 1)
        except Exception as e:
            return html.Span(str(e), style={"color": "#C0392B"}), no_update