"""
=========================================================
proyeccion_captura.py  —  CAPTURA DE PROYECCIONES (admin)
=========================================================
Sección dentro de Carga de datos donde el admin:
  • Elige AÑO + MES.
  • Ve la lista de productos (la maestra editable) con un
    campo de CANTIDAD para capturar la proyección de ese mes.
  • Guarda (se conserva para siempre en Supabase).
  • Agrega o quita productos de la lista maestra.

Los datos se guardan con db.guardar_proyeccion (upsert por
año/mes/producto: conserva el histórico de otros meses).
"""

from datetime import date

from dash import Input, Output, State, html, dcc, no_update, ALL, ctx
import dash_bootstrap_components as dbc

import db

AZUL = "#173C73"
DORADO = "#D4AF37"

MESES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]


def _input_num(producto, valor=None):
    return dcc.Input(
        id={"type": "proy-cant", "producto": producto},
        type="number", min=0, step="any",
        value=valor if valor not in (None, 0) else None,
        placeholder="0",
        style={"width": "140px", "padding": "6px 8px",
               "borderRadius": "6px", "border": "1px solid #CBD5E1"},
    )


def crear_seccion_proyeccion():
    """Sección grande de captura de proyecciones (para Carga)."""
    anio_actual = date.today().year
    anios = list(range(anio_actual - 1, anio_actual + 2))  # año-1 .. año+1

    return html.Div(
        [
            dcc.Store(id="proy-refresco", data=0),

            html.Hr(style={"margin": "40px 0 24px"}),
            html.H2("Proyección de ventas",
                    style={"color": AZUL, "fontWeight": "700"}),
            html.P("Captura la proyección mensual de cantidad por producto. "
                   "Se guarda de forma permanente para tener referencia "
                   "histórica.",
                   style={"color": "#6C757D", "marginBottom": "20px"}),

            # selectores año + mes
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="proy-anio",
                                options=[{"label": str(a), "value": a} for a in anios],
                                value=anio_actual, clearable=False,
                                style={"width": "140px"},
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.Label("Mes", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="proy-mes",
                                options=[{"label": n, "value": m} for m, n in MESES],
                                value=date.today().month, clearable=False,
                                style={"width": "180px"},
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "24px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            # tabla de captura (lista de productos + cantidad)
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Cantidad proyectada por producto",
                                style={"color": AZUL, "fontWeight": "700",
                                       "marginBottom": "16px"}),
                        html.Div(id="proy-tabla-captura"),
                        html.Br(),
                        html.Button(
                            [html.I(className="fas fa-floppy-disk me-2"),
                             "Guardar proyección"],
                            id="proy-btn-guardar", n_clicks=0,
                            style={"backgroundColor": AZUL, "color": "white",
                                   "border": "none", "padding": "12px 22px",
                                   "borderRadius": "8px", "fontWeight": "600",
                                   "cursor": "pointer"},
                        ),
                        html.Div(id="proy-msg-guardar",
                                 style={"marginTop": "12px", "minHeight": "22px"}),
                    ]
                ),
                className="card-premium",
                style={"marginBottom": "24px", "maxWidth": "560px"},
            ),

            # gestión de la lista maestra
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Gestionar lista de productos",
                                style={"color": AZUL, "fontWeight": "700",
                                       "marginBottom": "14px"}),
                        html.Div(
                            [
                                dcc.Input(
                                    id="proy-nuevo-producto",
                                    type="text",
                                    placeholder="Nombre exacto del producto",
                                    style={"width": "320px", "padding": "8px 10px",
                                           "borderRadius": "6px",
                                           "border": "1px solid #CBD5E1",
                                           "marginRight": "10px"},
                                ),
                                html.Button(
                                    [html.I(className="fas fa-plus me-2"), "Agregar"],
                                    id="proy-btn-agregar", n_clicks=0,
                                    style={"backgroundColor": DORADO,
                                           "color": AZUL, "border": "none",
                                           "padding": "8px 16px",
                                           "borderRadius": "6px",
                                           "fontWeight": "600", "cursor": "pointer"},
                                ),
                            ],
                            style={"marginBottom": "8px"},
                        ),
                        html.P("Escribe el nombre EXACTO como aparece en Ventas "
                               "(Producto), para que el facturado cruce bien.",
                               style={"fontSize": "12px", "color": "#6C757D"}),
                        html.Div(id="proy-msg-lista",
                                 style={"minHeight": "20px", "marginBottom": "8px"}),
                        html.Div(id="proy-lista-productos"),
                    ]
                ),
                className="card-premium",
                style={"maxWidth": "560px"},
            ),
        ]
    )


def registrar_callbacks_proyeccion_captura(app):

    # ---- construir la tabla de captura al cambiar año/mes o refrescar ----
    @app.callback(
        Output("proy-tabla-captura", "children"),
        Input("proy-anio", "value"),
        Input("proy-mes", "value"),
        Input("proy-refresco", "data"),
    )
    def construir_tabla(anio, mes, _r):
        productos = db.listar_productos_proyeccion(solo_activos=True)
        if not productos:
            return html.Div("No hay productos en la lista. Agrega abajo.",
                            style={"color": "#6C757D"})
        guardado = db.leer_proyeccion(anio, mes) if (anio and mes) else {}

        filas = []
        for p in productos:
            nombre = p["producto"]
            filas.append(
                html.Div(
                    [
                        html.Span(nombre, style={"flex": "1", "color": AZUL,
                                                 "fontWeight": "500"}),
                        _input_num(nombre, guardado.get(nombre)),
                    ],
                    style={"display": "flex", "alignItems": "center",
                           "justifyContent": "space-between",
                           "padding": "6px 0",
                           "borderBottom": "1px solid #EEF2F7"},
                )
            )
        return html.Div(filas)

    # ---- guardar proyección ----
    @app.callback(
        Output("proy-msg-guardar", "children"),
        Input("proy-btn-guardar", "n_clicks"),
        State("proy-anio", "value"),
        State("proy-mes", "value"),
        State({"type": "proy-cant", "producto": ALL}, "value"),
        State({"type": "proy-cant", "producto": ALL}, "id"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def guardar(n, anio, mes, valores, ids, sesion):
        if not sesion or sesion.get("rol") != "admin":
            return html.Span("Solo un administrador puede guardar.",
                             style={"color": "#C0392B"})
        if not anio or not mes:
            return html.Span("Selecciona año y mes.",
                             style={"color": "#C0392B"})
        proy = {}
        for val, cid in zip(valores, ids):
            proy[cid["producto"]] = val if val is not None else 0
        try:
            db.guardar_proyeccion(anio, mes, proy)
            return html.Span(f"Proyección guardada para {mes:02d}/{anio}.",
                             style={"color": "#198754", "fontWeight": "600"})
        except Exception as e:
            return html.Span(f"Error: {e}", style={"color": "#C0392B"})

    # ---- lista de productos (con botón quitar) ----
    @app.callback(
        Output("proy-lista-productos", "children"),
        Input("proy-refresco", "data"),
    )
    def mostrar_lista(_r):
        productos = db.listar_productos_proyeccion(solo_activos=True)
        if not productos:
            return html.Div("Lista vacía.", style={"color": "#6C757D"})
        filas = []
        for p in productos:
            nombre = p["producto"]
            filas.append(
                html.Div(
                    [
                        html.Span(nombre, style={"flex": "1", "color": AZUL}),
                        html.Button(
                            html.I(className="fas fa-trash"),
                            id={"type": "proy-quitar", "producto": nombre},
                            n_clicks=0,
                            title="Quitar de la lista",
                            style={"backgroundColor": "transparent",
                                   "border": "none", "color": "#C0392B",
                                   "cursor": "pointer"},
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center",
                           "justifyContent": "space-between",
                           "padding": "5px 0",
                           "borderBottom": "1px solid #EEF2F7"},
                )
            )
        return html.Div(filas)

    # ---- agregar producto ----
    @app.callback(
        Output("proy-msg-lista", "children"),
        Output("proy-refresco", "data", allow_duplicate=True),
        Output("proy-nuevo-producto", "value"),
        Input("proy-btn-agregar", "n_clicks"),
        State("proy-nuevo-producto", "value"),
        State("proy-refresco", "data"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def agregar(n, nombre, refresco, sesion):
        if not sesion or sesion.get("rol") != "admin":
            return html.Span("No autorizado.", style={"color": "#C0392B"}), no_update, no_update
        try:
            db.agregar_producto_proyeccion(nombre)
            return (html.Span(f"'{nombre.strip()}' agregado.",
                              style={"color": "#198754"}),
                    (refresco or 0) + 1, "")
        except Exception as e:
            return html.Span(f"Error: {e}", style={"color": "#C0392B"}), no_update, no_update

    # ---- quitar producto ----
    @app.callback(
        Output("proy-refresco", "data", allow_duplicate=True),
        Input({"type": "proy-quitar", "producto": ALL}, "n_clicks"),
        State("proy-refresco", "data"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def quitar(clicks, refresco, sesion):
        if not sesion or sesion.get("rol") != "admin":
            return no_update
        if not ctx.triggered_id or not any(clicks):
            return no_update
        producto = ctx.triggered_id["producto"]
        try:
            db.quitar_producto_proyeccion(producto)
        except Exception:
            return no_update
        return (refresco or 0) + 1