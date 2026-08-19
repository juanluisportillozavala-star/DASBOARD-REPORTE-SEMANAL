"""
=========================================================
captura_proyeccion.py  —  MÓDULO "Captura de proyecciones"
=========================================================
Página propia (ruta /captura-proyeccion) donde los VENDEDORES
capturan su proyección mensual. Reemplaza a la vieja captura que
vivía dentro de "Carga de datos" (solo admin).

Reglas:
  • Pestaña por vendedor (ILSE / FREDY / MATEO).
  • Un vendedor VE las 3 pestañas pero solo EDITA la suya.
  • El admin edita las 3.
  • La edición se valida en el SERVIDOR (no solo ocultando botones).

Igual que antes: la edición es en un STORE temporal; nada se
guarda hasta pulsar «Guardar proyección». VARIOS es una fila fija
al final con meta editable. Un mes nuevo arranca con la semilla.
"""

from datetime import date

from dash import Input, Output, State, html, dcc, no_update, ALL, ctx
import dash_bootstrap_components as dbc

import db
from db import VENDEDORES

AZUL = "#173C73"
DORADO = "#D4AF37"

VARIOS = "VARIOS"
ANIOS = list(range(2025, 2036))
MESES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]


def _puede_editar(sesion, vendedor):
    """True si esta sesión puede editar la proyección de 'vendedor'.
    Admin edita cualquiera; un vendedor solo la suya."""
    if not sesion:
        return False
    if sesion.get("rol") == "admin":
        return True
    return (sesion.get("vendedor") or "") == vendedor


def _fila_producto(nombre, valor, editable, fija=False):
    """Fila: nombre + input cantidad + botón quitar.
    - fija=True (VARIOS): sin botón quitar, nombre en cursiva/gris.
    - editable=False: input deshabilitado y sin botón quitar."""
    elementos = [
        html.Span(nombre,
                  style={"flex": "1",
                         "color": "#6C757D" if fija else AZUL,
                         "fontWeight": "500",
                         "fontStyle": "italic" if fija else "normal"}),
        dcc.Input(
            id={"type": "cap-cant", "producto": nombre},
            type="number", min=0, step="any",
            value=valor if valor not in (None, 0) else None,
            placeholder="0", disabled=not editable,
            style={"width": "140px", "padding": "6px 8px",
                   "borderRadius": "6px", "border": "1px solid #CBD5E1",
                   "backgroundColor": "#FFFFFF" if editable else "#F1F3F5"},
        ),
    ]
    if editable and not fija:
        elementos.append(
            html.Button(
                html.I(className="fas fa-trash"),
                id={"type": "cap-quitar", "producto": nombre},
                n_clicks=0, title="Quitar de este mes",
                style={"backgroundColor": "transparent", "border": "none",
                       "color": "#C0392B", "cursor": "pointer",
                       "marginLeft": "10px"},
            )
        )
    else:
        elementos.append(html.Span(style={"width": "34px",
                                          "marginLeft": "10px"}))
    return html.Div(
        elementos,
        style={"display": "flex", "alignItems": "center",
               "justifyContent": "space-between", "padding": "6px 0",
               "borderBottom": "1px solid #EEF2F7",
               "backgroundColor": "#FAFAF5" if fija else "transparent"},
    )


def _render_tabla(lista, editable):
    normales = [x for x in (lista or []) if x["producto"].strip().upper() != VARIOS]
    varios = next((x for x in (lista or [])
                   if x["producto"].strip().upper() == VARIOS), None)
    varios_val = varios.get("cantidad") if varios else None

    filas = [_fila_producto(x["producto"], x.get("cantidad"), editable)
             for x in normales]
    filas.append(_fila_producto(VARIOS, varios_val, editable, fija=True))
    return html.Div(filas)


def crear_layout_captura_proyeccion():
    anio_actual = date.today().year if date.today().year in ANIOS else ANIOS[0]

    return html.Div(
        [
            dcc.Store(id="cap-lista-edit", data=[]),
            dcc.Store(id="cap-ctx", data=None),

            html.H1("Captura de proyecciones", className="titulo"),
            html.P("Captura la proyección mensual de cantidad por producto de "
                   "cada vendedor. Cada quien edita la suya; el administrador "
                   "puede editar las tres.", className="subtitulo"),
            html.Br(),

            # año + mes
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="cap-anio",
                                options=[{"label": str(a), "value": a} for a in ANIOS],
                                value=anio_actual, clearable=False,
                                style={"width": "140px"}),
                        ],
                    ),
                    html.Div(
                        [
                            html.Label("Mes", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="cap-mes",
                                options=[{"label": n, "value": m} for m, n in MESES],
                                value=date.today().month, clearable=False,
                                style={"width": "180px"}),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            # pestañas por vendedor
            dcc.Tabs(
                id="cap-vendedor", value=VENDEDORES[0],
                children=[dcc.Tab(label=v, value=v) for v in VENDEDORES],
                style={"marginBottom": "16px"},
            ),

            # aviso de permiso (solo lectura / editable)
            html.Div(id="cap-permiso",
                     style={"marginBottom": "12px", "minHeight": "20px",
                            "fontWeight": "600"}),

            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Cantidad proyectada por producto",
                                style={"color": AZUL, "fontWeight": "700",
                                       "marginBottom": "16px"}),
                        html.Div(id="cap-tabla"),
                        html.Br(),
                        html.Button(
                            [html.I(className="fas fa-floppy-disk me-2"),
                             "Guardar proyección"],
                            id="cap-btn-guardar", n_clicks=0,
                            style={"backgroundColor": AZUL, "color": "white",
                                   "border": "none", "padding": "12px 22px",
                                   "borderRadius": "8px", "fontWeight": "600",
                                   "cursor": "pointer"},
                        ),
                        html.Div(id="cap-msg-guardar",
                                 style={"marginTop": "12px", "minHeight": "22px"}),
                    ]
                ),
                className="card-premium",
                style={"marginBottom": "24px", "maxWidth": "620px"},
            ),

            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Agregar producto a este mes",
                                style={"color": AZUL, "fontWeight": "700",
                                       "marginBottom": "14px"}),
                        html.Div(
                            [
                                dcc.Input(
                                    id="cap-nuevo-producto", type="text",
                                    placeholder="Nombre exacto del producto",
                                    style={"width": "320px", "padding": "8px 10px",
                                           "borderRadius": "6px",
                                           "border": "1px solid #CBD5E1",
                                           "marginRight": "10px"}),
                                html.Button(
                                    [html.I(className="fas fa-plus me-2"), "Agregar"],
                                    id="cap-btn-agregar", n_clicks=0,
                                    style={"backgroundColor": DORADO, "color": AZUL,
                                           "border": "none", "padding": "8px 16px",
                                           "borderRadius": "6px",
                                           "fontWeight": "600", "cursor": "pointer"}),
                            ],
                            style={"marginBottom": "8px"},
                        ),
                        html.P("Se agrega solo en pantalla; recuerda pulsar "
                               "«Guardar proyección». Escribe el nombre EXACTO "
                               "como aparece en Ventas (Producto).",
                               style={"fontSize": "12px", "color": "#6C757D"}),
                        html.Div(id="cap-msg-lista", style={"minHeight": "20px"}),
                    ]
                ),
                className="card-premium",
                style={"maxWidth": "620px"},
            ),
        ]
    )


def _leer_cantidades_actuales(valores, ids):
    actuales = {}
    for val, cid in zip(valores, ids):
        actuales[cid["producto"]] = val if val is not None else 0
    return actuales


def registrar_callbacks_captura_proyeccion(app):

    # 1) cargar la lista del (año, mes, vendedor) al store
    @app.callback(
        Output("cap-lista-edit", "data"),
        Output("cap-ctx", "data"),
        Input("cap-anio", "value"),
        Input("cap-mes", "value"),
        Input("cap-vendedor", "value"),
    )
    def cargar(anio, mes, vendedor):
        if not anio or not mes or not vendedor:
            return [], None
        guardado = db.leer_proyeccion(anio, mes, vendedor)
        if guardado:
            productos = db.listar_productos_mes(anio, mes, vendedor)
            lista = [{"producto": p, "cantidad": guardado.get(p, 0)}
                     for p in productos if p.strip().upper() != VARIOS]
            if VARIOS in guardado:
                lista.append({"producto": VARIOS,
                              "cantidad": guardado.get(VARIOS, 0)})
        else:
            lista = [{"producto": p, "cantidad": 0}
                     for p in db.productos_semilla()
                     if p.strip().upper() != VARIOS]
        return lista, {"anio": anio, "mes": mes, "vendedor": vendedor}

    # 2) render de la tabla + permisos (habilita/deshabilita edición)
    @app.callback(
        Output("cap-tabla", "children"),
        Output("cap-permiso", "children"),
        Output("cap-permiso", "style"),
        Output("cap-btn-guardar", "disabled"),
        Output("cap-btn-agregar", "disabled"),
        Output("cap-nuevo-producto", "disabled"),
        Input("cap-lista-edit", "data"),
        State("cap-vendedor", "value"),
        State("store-sesion", "data"),
    )
    def render_tabla(lista, vendedor, sesion):
        editable = _puede_editar(sesion, vendedor)
        tabla = _render_tabla(lista or [], editable)

        base_style = {"marginBottom": "12px", "minHeight": "20px",
                      "fontWeight": "600"}
        if editable:
            aviso = f"Editando la proyección de {vendedor}."
            aviso_style = dict(base_style, color="#198754")
        else:
            aviso = (f"Solo lectura. Esta proyección es de {vendedor}; "
                     f"solo {vendedor} o un administrador pueden editarla.")
            aviso_style = dict(base_style, color="#B7791F")

        return (tabla, aviso, aviso_style,
                not editable, not editable, not editable)

    # 3) agregar producto -> SOLO al store (con permiso)
    @app.callback(
        Output("cap-lista-edit", "data", allow_duplicate=True),
        Output("cap-msg-lista", "children"),
        Output("cap-nuevo-producto", "value"),
        Input("cap-btn-agregar", "n_clicks"),
        State("cap-nuevo-producto", "value"),
        State("cap-lista-edit", "data"),
        State("cap-vendedor", "value"),
        State("store-sesion", "data"),
        State({"type": "cap-cant", "producto": ALL}, "value"),
        State({"type": "cap-cant", "producto": ALL}, "id"),
        prevent_initial_call=True,
    )
    def agregar(n, nombre, lista, vendedor, sesion, valores, ids):
        if not _puede_editar(sesion, vendedor):
            return no_update, html.Span("No tienes permiso para editar esta "
                                        "proyección.", style={"color": "#C0392B"}), no_update
        nombre = (nombre or "").strip()
        if not nombre:
            return no_update, html.Span("Escribe un nombre.",
                                        style={"color": "#C0392B"}), no_update
        lista = lista or []
        actuales = _leer_cantidades_actuales(valores, ids)
        for x in lista:
            if x["producto"] in actuales:
                x["cantidad"] = actuales[x["producto"]]
        existentes = {x["producto"].strip().upper() for x in lista}
        if nombre.upper() == VARIOS:
            return no_update, html.Span("«VARIOS» ya está fijo al final.",
                                        style={"color": "#C0392B"}), ""
        if nombre.upper() in existentes:
            return no_update, html.Span(f"'{nombre}' ya está en la lista.",
                                        style={"color": "#C0392B"}), ""
        lista.append({"producto": nombre, "cantidad": 0})
        return lista, html.Span(f"'{nombre}' agregado (recuerda guardar).",
                                style={"color": "#198754"}), ""

    # 4) quitar producto -> SOLO del store (con permiso)
    @app.callback(
        Output("cap-lista-edit", "data", allow_duplicate=True),
        Input({"type": "cap-quitar", "producto": ALL}, "n_clicks"),
        State("cap-lista-edit", "data"),
        State("cap-vendedor", "value"),
        State("store-sesion", "data"),
        State({"type": "cap-cant", "producto": ALL}, "value"),
        State({"type": "cap-cant", "producto": ALL}, "id"),
        prevent_initial_call=True,
    )
    def quitar(clicks, lista, vendedor, sesion, valores, ids):
        if not ctx.triggered_id or not any(clicks):
            return no_update
        if not _puede_editar(sesion, vendedor):
            return no_update
        objetivo = ctx.triggered_id["producto"]
        lista = lista or []
        actuales = _leer_cantidades_actuales(valores, ids)
        nueva = []
        for x in lista:
            if x["producto"] == objetivo:
                continue
            if x["producto"] in actuales:
                x["cantidad"] = actuales[x["producto"]]
            nueva.append(x)
        return nueva

    # 5) GUARDAR -> escribe en la base (permiso validado en servidor)
    @app.callback(
        Output("cap-msg-guardar", "children"),
        Input("cap-btn-guardar", "n_clicks"),
        State("cap-anio", "value"),
        State("cap-mes", "value"),
        State("cap-vendedor", "value"),
        State("cap-lista-edit", "data"),
        State({"type": "cap-cant", "producto": ALL}, "value"),
        State({"type": "cap-cant", "producto": ALL}, "id"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def guardar(n, anio, mes, vendedor, lista, valores, ids, sesion):
        if not _puede_editar(sesion, vendedor):
            return html.Span(f"No tienes permiso para editar la proyección "
                             f"de {vendedor}.", style={"color": "#C0392B"})
        if not anio or not mes:
            return html.Span("Selecciona año y mes.", style={"color": "#C0392B"})
        actuales = _leer_cantidades_actuales(valores, ids)
        proy = {}
        for x in (lista or []):
            p = x["producto"]
            if p.strip().upper() == VARIOS:
                continue
            proy[p] = actuales.get(p, x.get("cantidad", 0))
        varios_meta = actuales.get(VARIOS, 0) or 0
        if varios_meta and float(varios_meta) > 0:
            proy[VARIOS] = varios_meta
        try:
            db.guardar_proyeccion(anio, mes, vendedor, proy)
            return html.Span(f"Proyección de {vendedor} guardada para "
                             f"{int(mes):02d}/{anio}: {len(proy)} línea(s).",
                             style={"color": "#198754", "fontWeight": "600"})
        except Exception as e:
            return html.Span(f"Error: {e}", style={"color": "#C0392B"})